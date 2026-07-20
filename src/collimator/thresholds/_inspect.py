"""DB-driven threshold inspection helpers — the show_*/tune_thresholds
surface that backs the Make targets (false-positives, near-false-positives,
false-negatives, near-false-negatives, tune-thresholds).  These functions
operate on labeled corpora pulled from hopper rather than raw probability
arrays, so they live separately from the pure-math helpers in
``__init__.py``.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict
from itertools import islice
from pathlib import Path
from typing import Any

import numpy as np

from collimator import data, features
from collimator.model import load_model, predict_proba

from . import (
    DEFAULT_FP_RATE_RECOMMENDATIONS,
    SEVERITY_LEVEL_TARGETS,
    ScoredSample,
    _fp_budget_for_rate,
    _matches_severity_level,
    _most_open_severity_level,
    _near_severity_level,
    _outermost_error_rows,
    _outermost_sample_path,
    _print_severity_table,
    _row_for_sample,
    compute_default_recommendations,
    compute_severity_levels,
    evaluate_policies,
    fp_budget_tables,
)

log = logging.getLogger(__name__)


def _error_rows_for_threshold(
    samples: list[ScoredSample],
    probs: np.ndarray,
    y: np.ndarray,
    threshold: float,
    *,
    top_n: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    fp_rows: list[dict[str, Any]] = []
    fn_rows: list[dict[str, Any]] = []
    for sample, prob, label in zip(samples, probs, y, strict=False):
        row = {
            "row_id": sample.row_id,
            "sha256": sample.sha256,
            "path": _outermost_sample_path(sample.path),
            "score": sample.score,
            "probability": float(prob),
            "label": "bad" if int(label) == 1 else "good",
        }
        if int(label) == 0 and prob >= threshold:
            fp_rows.append(row)
        elif int(label) == 1 and prob < threshold:
            fn_rows.append(row)
    fp_rows.sort(key=lambda row: float(row["probability"]), reverse=True)
    fn_rows.sort(key=lambda row: float(row["probability"]), reverse=True)
    return (
        _outermost_error_rows(fp_rows, limit=top_n),
        _outermost_error_rows(fn_rows, limit=top_n),
    )


def _score_samples(
    spec: features.FeatureSpec,
    model_path: Path,
    *,
    samples: list[ScoredSample],
    report_labels: list[tuple[dict[str, Any], int]],
    batch_size: int = 2048,
    n_workers: int = 0,
) -> np.ndarray:
    model = load_model(model_path)
    pred_batches: list[np.ndarray] = []
    seen = 0
    for X_batch, y_batch in features.extract_stream_batches(
        report_labels,
        spec,
        n_workers=n_workers,
        batch_size=batch_size,
    ):
        X_input = features.standardize(X_batch, spec) if spec.standardized else X_batch
        preds = predict_proba(model, X_input)
        pred_batches.append(preds)
        seen += len(y_batch)
    if seen != len(samples):
        raise ValueError(f"scored sample count mismatch: expected {len(samples)}, got {seen}")
    return np.concatenate(pred_batches) if pred_batches else np.array([], dtype=np.float32)


def _score_labeled_corpus(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    path_substr: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    limit: int = 0,
    max_id: int = 0,
    n_workers: int = 0,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
    include_samples: bool = True,
) -> tuple[list[ScoredSample], np.ndarray, np.ndarray]:
    """Score the full labeled corpus used for operational threshold tuning."""
    cacheable = (
        cache_path is not None
        and path_substr is None
        and min_score is None
        and max_score is None
        and limit == 0
    )
    if cacheable and not refresh_cache and cache_path.exists():
        newest_input = max(model_path.stat().st_mtime, spec_path.stat().st_mtime)
        if cache_path.stat().st_mtime >= newest_input:
            log.info("loading threshold score cache from %s", cache_path)
            arrays = np.load(cache_path, allow_pickle=False)
            # Caches without canonical_shas predate the dev/test/train
            # methodology and can't support partition-aware filtering;
            # fall through to rebuild.
            if "canonical_shas" not in arrays.files:
                log.info("threshold score cache lacks canonical_shas; rebuilding for partition-aware calibration")
            else:
                labels = arrays["labels"].astype(np.float32)
                row_ids = arrays["row_ids"]
            cache_samples = int(arrays["corpus_samples"][()]) if "corpus_samples" in arrays.files else int(len(labels))
            cache_malware = int(arrays["corpus_malware"][()]) if "corpus_malware" in arrays.files else int(np.sum(labels == 1))
            cache_benign = int(arrays["corpus_benign"][()]) if "corpus_benign" in arrays.files else int(np.sum(labels == 0))
            cache_max_row_id = (
                int(arrays["corpus_max_row_id"][()])
                if "corpus_max_row_id" in arrays.files
                else int(np.max(row_ids)) if len(row_ids) else 0
            )
            cache_requested_max_id = (
                int(arrays["corpus_requested_max_id"][()])
                if "corpus_requested_max_id" in arrays.files
                else cache_max_row_id if max_id > 0 else 0
            )
            if max_id > 0 and cache_requested_max_id != max_id:
                log.info(
                    "threshold score cache was built for max_id=%d, requested max_id=%d; rebuilding",
                    cache_requested_max_id,
                    max_id,
                )
            elif max_id == 0 and cache_requested_max_id > 0:
                log.info(
                    "threshold score cache was built for pinned max_id=%d, requested live corpus; rebuilding",
                    cache_requested_max_id,
                )
            else:
                log.info(
                    "threshold score cache corpus: %d rows (%d malware, %d benign), max_row_id=%d",
                    cache_samples,
                    cache_malware,
                    cache_benign,
                    cache_max_row_id,
                )
                try:
                    current = data.labeled_corpus_metadata_full(db_path, max_id=max_id)
                    if current["samples"] != cache_samples or current["max_row_id"] != cache_max_row_id:
                        log.info(
                            "current DB threshold corpus: %d rows (%+d vs cache), max_row_id=%d (%+d)",
                            current["samples"],
                            current["samples"] - cache_samples,
                            current["max_row_id"],
                            current["max_row_id"] - cache_max_row_id,
                        )
                except Exception as exc:  # pragma: no cover - diagnostic only
                    log.warning("could not compare threshold score cache to current DB corpus: %s", exc)
                samples = []
                if include_samples:
                    samples = [
                        ScoredSample(
                            row_id=int(row_id),
                            sha256=str(sha256),
                            path=str(path),
                            score=int(score),
                            label=int(label),
                            canonical_sha256=str(canonical),
                        )
                        for row_id, sha256, path, score, label, canonical in zip(
                            arrays["row_ids"],
                            arrays["sha256"],
                            arrays["paths"],
                            arrays["scores"],
                            arrays["labels"],
                            arrays["canonical_shas"],
                            strict=True,
                        )
                    ]
                return samples, arrays["probs"], labels

    if cacheable:
        log.info("building threshold score cache at %s", cache_path)
    spec = features.FeatureSpec.load(spec_path)
    model = load_model(model_path)
    size_aware_batches = os.getenv("COLLIMATOR_THRESHOLD_SIZE_AWARE_BATCHES", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if size_aware_batches:
        row_metadata = list(data.stream_labeled_metadata_full_with_size(
            db_path,
            path_substr=path_substr,
            min_score=min_score,
            max_score=max_score,
            limit=limit,
            max_id=max_id,
        ))
    else:
        row_metadata = list(data.stream_labeled_metadata_full(
            db_path,
            path_substr=path_substr,
            min_score=min_score,
            max_score=max_score,
            limit=limit,
            max_id=max_id,
        ))
    if size_aware_batches:
        log.info("threshold scoring uses size-aware batch packing")
    # Tuple shape:
    #   stream_labeled_metadata_full      -> (row_id, sha256, path, score, label, canonical)
    #   ..._with_size                     -> (row_id, sha256, path, score, label, json_bytes, canonical)
    # In both cases, canonical_sha256 is the LAST element.
    samples = [
        ScoredSample(
            row_id=row[0],
            sha256=row[1],
            path=row[2],
            score=row[3],
            label=row[4],
            canonical_sha256=row[-1],
        )
        for row in row_metadata
    ]
    if not samples:
        raise ValueError("no samples matched the requested filters")
    log.info("threshold scoring metadata: %d labeled rows", len(samples))
    scored_samples: list[ScoredSample] = []
    pred_batches: list[np.ndarray] = []
    label_batches: list[np.ndarray] = []
    score_started = time.monotonic()
    last_progress = score_started
    last_rows_logged = 0
    scored_rows = 0
    stage_totals = {
        "fetch_sec": 0.0,
        "extract_sec": 0.0,
        "matrix_sec": 0.0,
        "predict_sec": 0.0,
    }
    slow_batches: list[dict[str, float | int]] = []

    for metadata_batch, X_batch, y_batch, batch_stats in features.extract_labeled_metadata_from_db_batches_unordered(
        db_path,
        row_metadata,
        spec,
        n_workers=n_workers,
    ):
        X_input = features.standardize(X_batch, spec) if spec.standardized else X_batch
        predict_started = time.monotonic()
        pred_batches.append(predict_proba(model, X_input).astype(np.float32))
        predict_sec = time.monotonic() - predict_started
        label_batches.append(y_batch.astype(np.float32))
        scored_samples.extend(
            ScoredSample(
                row_id=int(row[0]),
                sha256=str(row[1]),
                path=str(row[2]),
                score=int(row[3]),
                label=int(row[4]),
            )
            for row in metadata_batch
        )
        batch_stats = dict(batch_stats)
        batch_stats["predict_sec"] = predict_sec
        batch_stats["total_sec"] = (
            float(batch_stats.get("fetch_sec", 0.0))
            + float(batch_stats.get("extract_sec", 0.0))
            + float(batch_stats.get("matrix_sec", 0.0))
            + predict_sec
        )
        for key in stage_totals:
            stage_totals[key] += float(batch_stats.get(key, 0.0))
        slow_batches.append(batch_stats)
        slow_batches.sort(key=lambda row: float(row.get("total_sec", 0.0)), reverse=True)
        del slow_batches[5:]
        scored_rows += len(y_batch)
        now = time.monotonic()
        if scored_rows == len(samples) or scored_rows - last_rows_logged >= 100_000 or now - last_progress >= 60.0:
            elapsed = max(now - score_started, 1e-9)
            log.info(
                "threshold scoring progress: %d/%d rows (%.1f%%, %.0f rows/sec)",
                scored_rows,
                len(samples),
                100.0 * scored_rows / len(samples),
                scored_rows / elapsed,
            )
            last_progress = now
            last_rows_logged = scored_rows

    probs = np.concatenate(pred_batches) if pred_batches else np.array([], dtype=np.float32)
    y = np.concatenate(label_batches) if label_batches else np.array([], dtype=np.float32)
    elapsed = max(time.monotonic() - score_started, 1e-9)
    log.info(
        "threshold scoring complete: %d rows in %.1fs (%.0f rows/sec)",
        len(y),
        elapsed,
        len(y) / elapsed,
    )
    log.info(
        "threshold scoring stage totals: fetch=%.1fs extract=%.1fs matrix=%.1fs predict=%.1fs",
        stage_totals["fetch_sec"],
        stage_totals["extract_sec"],
        stage_totals["matrix_sec"],
        stage_totals["predict_sec"],
    )
    if slow_batches:
        slow_summary = "; ".join(
            (
                f"{int(row.get('rows', 0))} rows id "
                f"{int(row.get('min_row_id', 0))}-{int(row.get('max_row_id', 0))}: "
                f"total={float(row.get('total_sec', 0.0)):.1f}s "
                f"fetch={float(row.get('fetch_sec', 0.0)):.1f}s "
                f"extract={float(row.get('extract_sec', 0.0)):.1f}s "
                f"matrix={float(row.get('matrix_sec', 0.0)):.1f}s "
                f"predict={float(row.get('predict_sec', 0.0)):.1f}s"
            )
            for row in slow_batches
        )
        log.info("slowest threshold scoring batches: %s", slow_summary)
    expected_samples = len(samples)
    if len(probs) != expected_samples:
        raise ValueError(f"scored sample count mismatch: expected {expected_samples}, got {len(probs)}")
    if len(scored_samples) != expected_samples:
        raise ValueError(f"scored metadata count mismatch: expected {expected_samples}, got {len(scored_samples)}")
    samples = scored_samples
    if cacheable:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        corpus_max_row_id = max((sample.row_id for sample in samples), default=0)
        # Use uncompressed NPZ: this cache is meant to save wall-clock time,
        # and deflate compression is slow and effectively single-threaded here.
        #
        # Write to a sibling temp file and os.replace() it into place so a
        # failed write (e.g. ENOSPC mid-save) never leaves a truncated .npz
        # behind. np.load reads the zip's trailing central directory, so a
        # partial file poisons every downstream consumer with a confusing
        # "BadZipFile: File is not a zip file" instead of failing here where
        # the real cause (out of disk) is obvious.
        # Temp name must keep the .npz suffix, else np.savez appends its own
        # (foo.npz.tmp -> foo.npz.tmp.npz) and os.replace would miss it.
        tmp_path = cache_path.with_name(cache_path.stem + ".tmp.npz")
        np.savez(
            tmp_path,
            row_ids=np.array([sample.row_id for sample in samples], dtype=np.int64),
            sha256=np.array([sample.sha256 for sample in samples]),
            paths=np.array([sample.path for sample in samples]),
            scores=np.array([sample.score for sample in samples], dtype=np.int32),
            labels=y.astype(np.int8),
            probs=probs.astype(np.float32),
            canonical_shas=np.array([sample.canonical_sha256 or sample.sha256 for sample in samples]),
            corpus_samples=np.array(len(samples), dtype=np.int64),
            corpus_malware=np.array(int(np.sum(y == 1)), dtype=np.int64),
            corpus_benign=np.array(int(np.sum(y == 0)), dtype=np.int64),
            corpus_max_row_id=np.array(corpus_max_row_id, dtype=np.int64),
            corpus_requested_max_id=np.array(int(max_id), dtype=np.int64),
        )
        os.replace(tmp_path, cache_path)
        log.info(
            "saved threshold score cache to %s (%d rows, max_row_id=%d)",
            cache_path,
            len(samples),
            corpus_max_row_id,
        )
    return samples, probs, y


def compute_default_recommendations_for_corpus(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    n_workers: int = 0,
    max_id: int = 0,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
) -> dict[str, float | None]:
    """Compute deploy thresholds by scoring the full labeled hopper corpus."""
    _samples, probs, y = _score_labeled_corpus(
        db_path,
        model_path=model_path,
        spec_path=spec_path,
        n_workers=n_workers,
        max_id=max_id,
        cache_path=cache_path,
        refresh_cache=refresh_cache,
        include_samples=False,
    )
    return compute_default_recommendations(probs, y)


def tune_thresholds(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    path_substr: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    top_errors: int = 20,
    output_path: Path | None = None,
    limit: int = 0,
    max_id: int = 0,
    n_workers: int = 0,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
) -> dict[str, Any]:
    """Score the full labeled corpus and report threshold policy candidates."""
    samples, probs, y = _score_labeled_corpus(
        db_path,
        model_path=model_path,
        spec_path=spec_path,
        path_substr=path_substr,
        min_score=min_score,
        max_score=max_score,
        limit=limit,
        max_id=max_id,
        n_workers=n_workers,
        cache_path=cache_path,
        refresh_cache=refresh_cache,
        include_samples=top_errors > 0,
    )
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    policies = evaluate_policies(probs, y)
    budgets = fp_budget_tables(probs, y)
    severity_levels = compute_severity_levels(probs, y)
    for policy in policies:
        errors: dict[str, Any] = {}
        if top_errors > 0:
            for level_name in ("hostile",):
                level = policy.get(level_name)
                if not level or level.get("threshold") is None:
                    continue
                fp_rows, fn_rows = _error_rows_for_threshold(
                    samples, probs, y, float(level["threshold"]), top_n=top_errors,
                )
                errors[level_name] = {
                    "false_positives": fp_rows,
                    "false_negatives": fn_rows,
                    "false_positive_count": int(np.sum((y == 0) & (probs >= float(level["threshold"])))),
                    "false_negative_count": int(np.sum((y == 1) & (probs < float(level["threshold"])))),
                }
        policy["errors"] = errors

    payload: dict[str, Any] = {
        "filters": {
            "path_substr": path_substr,
            "min_score": min_score,
            "max_score": max_score,
            "limit": limit,
            "max_id": max_id,
        },
        "corpus": {
            "samples": len(y),
            "malware": malware,
            "benign": benign,
        },
        "default_fp_rate_targets": {
            level: {
                "target_rate": rate,
                "max_fp_budget": _fp_budget_for_rate(benign, rate),
            }
            for level, rate in DEFAULT_FP_RATE_RECOMMENDATIONS
        },
        "severity_level_targets": SEVERITY_LEVEL_TARGETS,
        "severity_levels": severity_levels,
        "fp_budget_tables": budgets,
        "policies": policies,
    }

    print(f"\n{'TUNE THRESHOLDS':=^78}")
    print(f"Corpus: {len(y)} samples ({malware} malware, {benign} benign)")
    if path_substr:
        print(f"Filter: path contains {path_substr!r}")
    if min_score is not None or max_score is not None:
        print(f"Filter: score range [{min_score if min_score is not None else '-inf'}, {max_score if max_score is not None else 'inf'}]")
    print(f"Top errors per level: {top_errors}")
    print()
    _print_severity_table("HOSTILE SEVERITY LEVELS", severity_levels, "hostile")

    print(f"{'Policy':<18} {'Level':<12} {'Threshold':>10} {'TP Rate':>8} {'Prec':>8} {'FP/1M':>10} {'TP':>7} {'FP':>7}")
    print(f"{'-'*78}")
    for policy in policies:
        for level_name in ("hostile",):
            level = policy.get(level_name)
            if not level:
                print(f"{policy['name']:<18} {level_name:<12} {'—':>10} {'—':>8} {'—':>8} {'—':>10} {'—':>7} {'—':>7}")
                continue
            print(
                f"{policy['name']:<18} {level_name:<12} {float(level['threshold']):>10.6f} "
                f"{float(level['recall']):>8.2%} {float(level['precision']):>8.2%} "
                f"{float(level['fp_per_100M']):>10.1f} {int(level['tp']):>7} {int(level['fp']):>7}"
            )
        for warning in policy["warnings"]:
            print(f"  warning: {warning}")
        print()

    target_budgets = {
        level: _fp_budget_for_rate(benign, rate)
        for level, rate in DEFAULT_FP_RATE_RECOMMENDATIONS
    }
    print(f"{'HOSTILE BY GOOD FP BUDGET':=^78}")
    print(f"Target: <=1 FP per 1,000,000 good files; current budget = {target_budgets['hostile']} FP")
    print(f"{'Allowed FP':>10} {'Good %':>10} {'Threshold':>10} {'TP Rate':>8} {'Prec':>8} {'TP':>7} {'FP':>7} {'FN':>7}")
    for row in budgets["hostile"]:
        fn = malware - int(row["tp"])
        marker = " *" if int(row["max_fp_budget"]) == target_budgets["hostile"] else ""
        print(
            f"{int(row['max_fp_budget']):>10} {100.0 * int(row['fp']) / max(benign, 1):>9.4f}% "
            f"{float(row['threshold']):>10.6f} {float(row['recall']):>8.2%} {float(row['precision']):>8.2%} "
            f"{int(row['tp']):>7} {int(row['fp']):>7} {fn:>7}{marker}"
        )
    print()

    for policy in policies:
        print(f"{policy['name']}: {policy['description']}")
        for level_name in ("hostile",):
            level_errors = policy["errors"].get(level_name)
            if not level_errors:
                continue
            print(
                f"  {level_name} false positives: {level_errors['false_positive_count']}  "
                f"false negatives: {level_errors['false_negative_count']}"
            )
            if level_errors["false_positives"]:
                print("  top false positives:")
                for row in level_errors["false_positives"]:
                    print(f"    {row['probability']:.6f}  {row['sha256'][:16]}  {row['path']}")
            if level_errors["false_negatives"]:
                print("  top false negatives:")
                for row in level_errors["false_negatives"]:
                    print(f"    {row['probability']:.6f}  {row['sha256'][:16]}  {row['path']}")
        print()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            import json
            json.dump(payload, f, indent=2)
        print(f"Saved tuning report to {output_path}")

    return payload


def show_false_positives(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    top_errors: int = 100,
    output_path: Path | None = None,
    n_workers: int = 0,
    max_id: int = 0,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
) -> dict[str, Any]:
    """Print false positives grouped by first severity level reached."""
    samples, probs, y = _score_labeled_corpus(
        db_path,
        model_path=model_path,
        spec_path=spec_path,
        n_workers=n_workers,
        max_id=max_id,
        cache_path=cache_path,
        refresh_cache=refresh_cache,
    )
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    severity_levels = compute_severity_levels(probs, y)
    basis_level = _most_open_severity_level(severity_levels)
    raw_rows = [
        _row_for_sample(sample, float(prob), int(label), severity_levels)
        for sample, prob, label in zip(samples, probs, y, strict=False)
        if int(label) == 0 and basis_level is not None
        and _matches_severity_level(float(prob), basis_level, "hostile")
    ]
    rows = list(raw_rows)
    rows.sort(key=lambda row: float(row["probability"]), reverse=True)
    rows = _outermost_error_rows(rows, limit=len(rows))

    payload: dict[str, Any] = {
        "corpus": {
            "samples": len(samples),
            "malware": malware,
            "benign": benign,
        },
        "severity_level_targets": SEVERITY_LEVEL_TARGETS,
        "severity_levels": severity_levels,
        "basis_level": int(basis_level["level"]) if basis_level is not None else None,
        "raw_false_positive_count": len(raw_rows),
        "outer_false_positive_count": len(rows),
        "false_positives": rows[:top_errors],
        "counts": {"hostile": {}},
    }

    grid_levels = [int(t["level"]) for t in SEVERITY_LEVEL_TARGETS if int(t["level"]) > 0]
    for name in ("hostile",):
        for level in grid_levels:
            payload["counts"][name][str(level)] = sum(
                1 for row in rows if row[f"{name}_level"] == level
            )

    print(f"\n{'FALSE POSITIVES BY SEVERITY LEVEL':=^78}")
    print(f"Corpus: {len(samples)} samples ({malware} malware, {benign} good)")
    if basis_level is not None:
        print(
            f"Basis: level {basis_level['level']} "
            f"(raw rows: {len(raw_rows)}, outer files: {len(rows)})"
        )
    print("First level counts:")
    for name in ("hostile",):
        counts = ", ".join(f"L{level}={payload['counts'][name][str(level)]}" for level in grid_levels)
        print(f"  {name}: {counts}")
    if rows:
        print("\n  top false positives:")
        for row in rows[:top_errors]:
            print(
                f"    {row['probability']:.6f}  H={row['hostile_level'] or '-'} "
                f"score={row['score']:<4} "
                f"{row['sha256'][:16]}  {row['path']}"
            )
    else:
        print("\n  false positives: none")

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            import json
            json.dump(payload, f, indent=2)
        print(f"\nSaved false-positive report to {output_path}")

    return payload


def show_near_false_positives(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    top_errors: int = 100,
    output_path: Path | None = None,
    n_workers: int = 0,
    max_id: int = 0,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
) -> dict[str, Any]:
    """Print benign samples that newly match a twice-looser level-9 threshold."""
    samples, probs, y = _score_labeled_corpus(
        db_path,
        model_path=model_path,
        spec_path=spec_path,
        n_workers=n_workers,
        max_id=max_id,
        cache_path=cache_path,
        refresh_cache=refresh_cache,
    )
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    severity_levels = compute_severity_levels(probs, y)
    basis_level = _most_open_severity_level(severity_levels)
    near_level = _near_severity_level(basis_level) if basis_level is not None else None
    raw_rows = [
        _row_for_sample(sample, float(prob), int(label), severity_levels)
        for sample, prob, label in zip(samples, probs, y, strict=False)
        if int(label) == 0
        and basis_level is not None
        and near_level is not None
        and not _matches_severity_level(float(prob), basis_level, "hostile")
        and _matches_severity_level(float(prob), near_level, "hostile")
    ]
    rows = list(raw_rows)
    rows.sort(key=lambda row: float(row["probability"]), reverse=True)
    rows = _outermost_error_rows(rows, limit=len(rows))

    payload: dict[str, Any] = {
        "corpus": {
            "samples": len(samples),
            "malware": malware,
            "benign": benign,
        },
        "severity_level_targets": SEVERITY_LEVEL_TARGETS,
        "severity_levels": severity_levels,
        "basis_level": int(basis_level["level"]) if basis_level is not None else None,
        "near_level": near_level,
        "raw_near_false_positive_count": len(raw_rows),
        "outer_near_false_positive_count": len(rows),
        "near_false_positives": rows[:top_errors],
        "counts": {"hostile": {}},
    }

    grid_levels = [int(t["level"]) for t in SEVERITY_LEVEL_TARGETS if int(t["level"]) > 0]
    for name in ("hostile",):
        for level in grid_levels:
            payload["counts"][name][str(level)] = sum(
                1 for row in rows if row[f"{name}_level"] == level
            )

    print(f"\n{'NEAR FALSE POSITIVES BY SEVERITY LEVEL':=^78}")
    print(f"Corpus: {len(samples)} samples ({malware} malware, {benign} good)")
    if basis_level is not None and near_level is not None:
        print(
            f"Basis: level {basis_level['level']} with twice-looser thresholds "
            f"(raw rows: {len(raw_rows)}, outer files: {len(rows)})"
        )
        for name in ("hostile",):
            metric = near_level.get(name)
            if isinstance(metric, dict):
                print(
                    f"  {name}: {float(metric['basis_threshold']):.6f} -> "
                    f"{float(metric['threshold']):.6f}"
                )
    print("Existing first level counts for near rows:")
    for name in ("hostile",):
        counts = ", ".join(
            f"L{level}={payload['counts'][name][str(level)]}" for level in grid_levels
        )
        print(f"  {name}: {counts}")
    if rows:
        print("\n  top near false positives:")
        for row in rows[:top_errors]:
            print(
                f"    {row['probability']:.6f}  H={row['hostile_level'] or '-'} "
                f"score={row['score']:<4} "
                f"{row['sha256'][:16]}  {row['path']}"
            )
    else:
        print("\n  near false positives: none")

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            import json
            json.dump(payload, f, indent=2)
        print(f"\nSaved near-false-positive report to {output_path}")

    return payload


def show_false_negatives(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    top_errors: int = 100,
    output_path: Path | None = None,
    n_workers: int = 0,
    max_id: int = 0,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
) -> dict[str, Any]:
    """Print bad samples by first severity level reached, including uncaught rows."""
    samples, probs, y = _score_labeled_corpus(
        db_path,
        model_path=model_path,
        spec_path=spec_path,
        n_workers=n_workers,
        max_id=max_id,
        cache_path=cache_path,
        refresh_cache=refresh_cache,
    )
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    severity_levels = compute_severity_levels(probs, y)
    rows = [
        _row_for_sample(sample, float(prob), int(label), severity_levels)
        for sample, prob, label in zip(samples, probs, y, strict=False)
        if int(label) == 1
    ]
    rows.sort(key=lambda row: float(row["probability"]), reverse=True)
    rows = _outermost_error_rows(rows, limit=len(rows))
    uncaught = [
        row for row in rows
        if row["hostile_level"] is None
    ]

    payload: dict[str, Any] = {
        "corpus": {
            "samples": len(samples),
            "malware": malware,
            "benign": benign,
        },
        "severity_level_targets": SEVERITY_LEVEL_TARGETS,
        "severity_levels": severity_levels,
        "uncaught": uncaught[:top_errors],
        "counts": {"hostile": {}, "uncaught": len(uncaught)},
    }

    grid_levels = [int(t["level"]) for t in SEVERITY_LEVEL_TARGETS if int(t["level"]) > 0]
    for name in ("hostile",):
        for level in grid_levels:
            payload["counts"][name][str(level)] = sum(1 for row in rows if row[f"{name}_level"] == level)

    print(f"\n{'FALSE NEGATIVES BY SEVERITY LEVEL':=^78}")
    print(f"Corpus: {len(samples)} samples ({malware} malware, {benign} good)")
    print("First caught level counts:")
    for name in ("hostile",):
        counts = ", ".join(f"L{level}={payload['counts'][name][str(level)]}" for level in grid_levels)
        print(f"  {name}: {counts}")
    print(f"  uncaught by the loosest grid level: {len(uncaught)}")
    if uncaught:
        print("\n  highest-probability uncaught bad samples:")
        for row in uncaught[:top_errors]:
            print(
                f"    {row['probability']:.6f}  H=- S=- score={row['score']:<4} "
                f"{row['sha256'][:16]}  {row['path']}"
            )
    else:
        print("\n  false negatives at level 9: none")

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            import json
            json.dump(payload, f, indent=2)
        print(f"\nSaved false-negative report to {output_path}")

    return payload


def show_near_false_negatives(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    top_errors: int = 100,
    output_path: Path | None = None,
    n_workers: int = 0,
    max_id: int = 0,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
) -> dict[str, Any]:
    """Print malware samples caught by a twice-looser level-9 threshold only."""
    samples, probs, y = _score_labeled_corpus(
        db_path,
        model_path=model_path,
        spec_path=spec_path,
        n_workers=n_workers,
        max_id=max_id,
        cache_path=cache_path,
        refresh_cache=refresh_cache,
    )
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    severity_levels = compute_severity_levels(probs, y)
    basis_level = _most_open_severity_level(severity_levels)
    near_level = _near_severity_level(basis_level) if basis_level is not None else None
    raw_rows = [
        _row_for_sample(sample, float(prob), int(label), severity_levels)
        for sample, prob, label in zip(samples, probs, y, strict=False)
        if int(label) == 1
        and basis_level is not None
        and near_level is not None
        and not _matches_severity_level(float(prob), basis_level, "hostile")
        and _matches_severity_level(float(prob), near_level, "hostile")
    ]
    rows = list(raw_rows)
    rows.sort(key=lambda row: float(row["probability"]), reverse=True)
    rows = _outermost_error_rows(rows, limit=len(rows))

    payload: dict[str, Any] = {
        "corpus": {
            "samples": len(samples),
            "malware": malware,
            "benign": benign,
        },
        "severity_level_targets": SEVERITY_LEVEL_TARGETS,
        "severity_levels": severity_levels,
        "basis_level": int(basis_level["level"]) if basis_level is not None else None,
        "near_level": near_level,
        "raw_near_false_negative_count": len(raw_rows),
        "outer_near_false_negative_count": len(rows),
        "near_false_negatives": rows[:top_errors],
    }

    print(f"\n{'NEAR FALSE NEGATIVES BY SEVERITY LEVEL':=^78}")
    print(f"Corpus: {len(samples)} samples ({malware} malware, {benign} good)")
    if basis_level is not None and near_level is not None:
        print(
            f"Basis: level {basis_level['level']} with twice-looser thresholds "
            f"(raw rows: {len(raw_rows)}, outer files: {len(rows)})"
        )
        for name in ("hostile",):
            metric = near_level.get(name)
            if isinstance(metric, dict):
                print(
                    f"  {name}: {float(metric['basis_threshold']):.6f} -> "
                    f"{float(metric['threshold']):.6f}"
                )
    if rows:
        print("\n  top near false negatives:")
        for row in rows[:top_errors]:
            print(
                f"    {row['probability']:.6f}  H={row['hostile_level'] or '-'} "
                f"score={row['score']:<4} "
                f"{row['sha256'][:16]}  {row['path']}"
            )
    else:
        print("\n  near false negatives: none")

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            import json
            json.dump(payload, f, indent=2)
        print(f"\nSaved near-false-negative report to {output_path}")

    return payload

