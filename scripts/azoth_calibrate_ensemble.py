#!/usr/bin/env python3
"""Calibrate routed azoth ensemble thresholds against the full corpus."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import logging
import math
import os
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp

from collimator import bundle, data, export, features, thresholds

sys.path.insert(0, str(Path(__file__).resolve().parent))
from azoth_specialist_suite import DEPLOYMENT_GROUPS  # noqa: E402

LOG = logging.getLogger("azoth_calibrate_ensemble")
_POPCOUNT8 = np.asarray([int(i).bit_count() for i in range(256)], dtype=np.uint8)


def _chunks(values: list[int], size: int) -> list[list[int]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _route_artifact_paths(output_dir: Path) -> list[Path]:
    """All artifact files that fingerprint a route's training output.

    For multi-seed bundles this is every ``models/seed_*.{txt,json}`` plus
    ``feature_spec.json``; for legacy single-model bundles it's
    ``model.{txt,json}`` plus ``feature_spec.json``. Returned in deterministic
    order so the hash is stable across runs.
    """
    spec = output_dir / "feature_spec.json"
    paths: list[Path] = []
    try:
        paths.extend(bundle.model_files(output_dir))
    except ValueError:
        # Ambiguous layouts get fingerprinted as legacy so a re-run will
        # propagate the broken state into the cache key and force re-derivation.
        for legacy in (output_dir / "model.txt", output_dir / "model.json"):
            if legacy.is_file():
                paths.append(legacy)
    if spec.is_file():
        paths.append(spec)
    return paths


def _hash_model_set(general_scores: Path, routes: list[dict[str, Any]]) -> str:
    h = hashlib.sha256()
    h.update(str(general_scores).encode())
    h.update(_file_sha256(general_scores).encode())
    for route in sorted(routes, key=lambda item: item["name"]):
        h.update(str(route["name"]).encode())
        output_dir = Path(route.get("output_dir", ""))
        for path in _route_artifact_paths(output_dir):
            h.update(path.name.encode())
            h.update(_file_sha256(path).encode())
    return h.hexdigest()


def _hash_route_artifacts(output_dir: Path) -> str:
    h = hashlib.sha256()
    for path in _route_artifact_paths(output_dir):
        h.update(path.name.encode())
        h.update(_file_sha256(path).encode())
    return h.hexdigest()


def _hash_ints(values: np.ndarray) -> str:
    contiguous = np.ascontiguousarray(values, dtype=np.int64)
    return hashlib.sha256(contiguous.view(np.uint8)).hexdigest()


def _route_cache_slug(route_name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", route_name).strip("_") or "route"


def _route_feature_cache_paths(
    cache_dir: Path,
    *,
    route_name: str,
    max_id: int,
    spec_hash: str,
    rows_hash: str,
) -> tuple[Path, Path]:
    stem = f"{_route_cache_slug(route_name)}-{max_id}-{spec_hash[:16]}-{rows_hash[:16]}"
    return cache_dir / f"{stem}.matrix.npz", cache_dir / f"{stem}.meta.json"


def _load_route_feature_cache(
    cache_dir: Path | None,
    *,
    route_name: str,
    max_id: int,
    spec_hash: str,
    rows_hash: str,
    expected_rows: int,
    expected_features: int,
) -> tuple[sp.csr_matrix | None, float]:
    if cache_dir is None:
        return None, 0.0
    started = time.perf_counter()
    matrix_path, meta_path = _route_feature_cache_paths(
        cache_dir,
        route_name=route_name,
        max_id=max_id,
        spec_hash=spec_hash,
        rows_hash=rows_hash,
    )
    if not matrix_path.exists() or not meta_path.exists():
        return None, 0.0
    try:
        with open(meta_path) as f:
            meta = json.load(f)
        if (
            meta.get("route") != route_name
            or int(meta.get("max_id", -1)) != max_id
            or meta.get("feature_spec_hash") != spec_hash
            or meta.get("rows_hash") != rows_hash
            or int(meta.get("rows", -1)) != expected_rows
            or int(meta.get("features", -1)) != expected_features
        ):
            return None, time.perf_counter() - started
        matrix = sp.load_npz(matrix_path).tocsr()
        if matrix.shape != (expected_rows, expected_features):
            return None, time.perf_counter() - started
        LOG.info(
            "%s: loaded route feature matrix cache %s (%d rows, %d features, nnz=%d)",
            route_name,
            matrix_path,
            matrix.shape[0],
            matrix.shape[1],
            matrix.nnz,
        )
        return matrix, time.perf_counter() - started
    except Exception:
        LOG.warning("%s: failed to load route feature matrix cache", route_name, exc_info=True)
        return None, time.perf_counter() - started


def _save_route_feature_cache(
    cache_dir: Path | None,
    *,
    route_name: str,
    max_id: int,
    spec_hash: str,
    rows_hash: str,
    matrix: sp.csr_matrix,
) -> float:
    if cache_dir is None:
        return 0.0
    started = time.perf_counter()
    cache_dir.mkdir(parents=True, exist_ok=True)
    matrix_path, meta_path = _route_feature_cache_paths(
        cache_dir,
        route_name=route_name,
        max_id=max_id,
        spec_hash=spec_hash,
        rows_hash=rows_hash,
    )
    # Process-unique temp names. The cache dir is shared across concurrent
    # calibrate runs (autocollie-loop runs route experiments in parallel, and
    # every experiment's calibrate scores *all* routes — so the largest route,
    # PE, is written by several processes at once). A deterministic temp name
    # let the first writer's os.replace() consume the shared temp out from under
    # the others, crashing them with FileNotFoundError. The pid suffix keeps each
    # writer's temp private; os.replace stays atomic so the final file is sound.
    pid = os.getpid()
    tmp_matrix = matrix_path.with_name(matrix_path.name.removesuffix(".npz") + f".tmp.{pid}.npz")
    tmp_meta = meta_path.with_suffix(meta_path.suffix + f".tmp.{pid}")
    sp.save_npz(tmp_matrix, matrix, compressed=False)
    meta = {
        "route": route_name,
        "max_id": max_id,
        "feature_spec_hash": spec_hash,
        "rows_hash": rows_hash,
        "rows": int(matrix.shape[0]),
        "features": int(matrix.shape[1]),
        "nnz": int(matrix.nnz),
        "created_at": datetime.now(UTC).isoformat(),
    }
    with open(tmp_meta, "w") as f:
        json.dump(meta, f, indent=2, sort_keys=True)
        f.write("\n")
    tmp_matrix.replace(matrix_path)
    tmp_meta.replace(meta_path)
    LOG.info("%s: saved route feature matrix cache %s", route_name, matrix_path)
    return time.perf_counter() - started


def _route_artifacts_newer_than(path: Path, output_dir: Path) -> bool:
    try:
        cache_mtime = path.stat().st_mtime
    except FileNotFoundError:
        return True
    artifacts = _route_artifact_paths(output_dir)
    if not artifacts:
        # No model on disk at all; treat as fresher to force re-derivation
        # rather than silently trusting a stale cache.
        return True
    for artifact in artifacts:
        try:
            if artifact.stat().st_mtime > cache_mtime:
                return True
        except FileNotFoundError:
            return True
    return False


def _label_int(label: str) -> int:
    return 1 if label == "bad" else 0


def _fetch_file_types(db_path: Path | str, row_ids: np.ndarray) -> dict[int, str]:
    """Return {row_id: canonical_file_type}. Each stored `file_type` is mapped
    to its canonical filefacts label via [data.route_filetype] — compression
    suffixes collapse onto the container (`tar.gz` → `tar`) AND historical
    spellings fold onto the filefacts form (`python-bytecode` →
    `python_bytecode`, `xlsx` → `ooxml`) — before it ever lands in the score
    table. Every downstream consumer (route discovery, specialist training,
    per-filetype metrics, scan route lookup) inherits the canonical form, so
    old and new spellings of one type train a single specialist named the way
    scan receives it from filefacts at runtime."""
    ids = [int(row_id) for row_id in row_ids]
    out: dict[int, str] = {}
    with data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if data._is_pg(db_path):  # noqa: SLF001
            with conn.cursor() as cur:
                for chunk in _chunks(ids, 10_000):
                    cur.execute(
                        "SELECT id, COALESCE(NULLIF(file_type, ''), 'unknown') "
                        "FROM samples WHERE id = ANY(%s)",
                        [chunk],
                    )
                    out.update({
                        int(row_id): data.route_filetype(file_type)
                        for row_id, file_type in cur
                    })
        else:
            for chunk in _chunks(ids, 10_000):
                placeholders = ",".join("?" for _ in chunk)
                query = (
                    "SELECT id, COALESCE(NULLIF(file_type, ''), 'unknown') "
                    f"FROM samples WHERE id IN ({placeholders})"
                )
                out.update({
                    int(row_id): data.route_filetype(file_type)
                    for row_id, file_type in conn.execute(query, chunk)
                })
    return out


def _fetch_rows(
    db_path: Path | str,
    *,
    file_types: list[str],
    max_id: int,
) -> list[tuple[int, int]]:
    marker = "%s" if data._is_pg(db_path) else "?"  # noqa: SLF001
    where = [
        data.LABELED_WHERE,
        f"id <= {marker}",
    ]
    params: list[Any] = [max_id]
    rows: list[tuple[int, int]] = []
    with data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if data._is_pg(db_path):  # noqa: SLF001
            where.append("file_type = ANY(%s)")
            params.append(file_types)
            query = "SELECT id, label FROM samples WHERE " + " AND ".join(where) + " ORDER BY id"
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = [(int(row_id), _label_int(str(label))) for row_id, label in cur]
        else:
            placeholders = ",".join("?" for _ in file_types)
            where.append(f"file_type IN ({placeholders})")
            params.extend(file_types)
            query = "SELECT id, label FROM samples WHERE " + " AND ".join(where) + " ORDER BY id"
            rows = [
                (int(row_id), _label_int(str(label)))
                for row_id, label in conn.execute(query, params)
            ]
    return rows


def _load_oof_route_scores(
    oof_path: Path,
    *,
    row_index: dict[int, int],
    route_label: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Load a per-route OOF threshold_scores.npz produced by
    ``azoth_oof_score_routes.py`` and project it into score-table layout.

    Returns ``(indices, probs)``: ``indices`` are positions in the
    score-table row order; ``probs`` are the matching OOF-predicted
    probabilities. Rows present in the OOF file but missing from the
    score-table row index are dropped with a warning (they fell out of
    the corpus snapshot since OOF was computed).
    """
    cache = np.load(oof_path)
    row_ids = cache["row_ids"].astype(np.int64)
    probs = cache["probs"].astype(np.float32)
    indices: list[int] = []
    kept_probs: list[float] = []
    dropped = 0
    for row_id, prob in zip(row_ids.tolist(), probs.tolist(), strict=True):
        idx = row_index.get(int(row_id))
        if idx is None:
            dropped += 1
            continue
        indices.append(idx)
        kept_probs.append(prob)
    if dropped:
        LOG.warning(
            "%s: dropped %d OOF rows missing from current row index "
            "(corpus snapshot drift?)",
            route_label,
            dropped,
        )
    return (
        np.asarray(indices, dtype=np.int64),
        np.asarray(kept_probs, dtype=np.float32),
    )


def _score_route(
    db_path: Path | str,
    route: dict[str, Any],
    *,
    row_index: dict[int, int],
    max_id: int,
    workers: int,
    refresh: bool,
    refresh_routes: set[str],
    feature_cache_dir: Path | None,
    oof_route_scores_dir: Path | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    output_dir = Path(route["output_dir"])
    cache_path = output_dir / "calibration_scores.npz"

    # OOF override: when a per-route OOF threshold_scores.npz exists under
    # ``oof_route_scores_dir`` (produced by azoth_oof_score_routes.py),
    # short-circuit the in-sample scoring path. The OOF file already has
    # row_ids and probs in honest OOF order — train+dev rows scored by
    # whichever fold model didn't see them, test rows scored by the
    # production bundle (if --prod-root was passed to the merge script).
    # This eliminates the in-sample-specialist bias the calibration has
    # historically carried; downstream (recall-monotone floor, Pareto
    # curves, future stacker) consumes honest probabilities.
    if oof_route_scores_dir is not None:
        oof_path = oof_route_scores_dir / route["route"] / "threshold_scores.npz"
        if oof_path.is_file():
            indices, probs = _load_oof_route_scores(
                oof_path,
                row_index=row_index,
                route_label=route["route"],
            )
            LOG.info(
                "%s: using OOF scores from %s (%d rows in %.2fs)",
                route["route"],
                oof_path,
                len(indices),
                time.perf_counter() - started,
            )
            return {
                "name": route["route"],
                "kind": route["kind"],
                "file_types": route["file_types"],
                "output_dir": str(output_dir),
                "indices": indices,
                "probs": probs,
            }
        LOG.warning(
            "%s: OOF route scores requested but %s is missing; falling back "
            "to in-sample scoring (this measurement carries in-sample bias)",
            route["route"],
            oof_path,
        )
    route_hash = _hash_route_artifacts(output_dir)
    force_refresh = refresh or route["route"] in refresh_routes or route["name"] in refresh_routes
    if cache_path.exists() and not force_refresh:
        cache = np.load(cache_path)
        cached_hash = str(cache["route_hash"]) if "route_hash" in cache.files else ""
        cached_max_id = int(cache["max_id"]) if "max_id" in cache.files else max_id
        if cached_hash and cached_hash != route_hash:
            LOG.info("%s: route artifacts changed; refreshing score cache", route["route"])
        elif not cached_hash and _route_artifacts_newer_than(cache_path, output_dir):
            LOG.info("%s: legacy cache is older than route artifacts; refreshing score cache", route["route"])
        elif cached_max_id != max_id:
            LOG.info(
                "%s: cache snapshot changed (%d != %d); refreshing score cache",
                route["route"],
                cached_max_id,
                max_id,
            )
        else:
            if not cached_hash:
                LOG.warning("%s: using legacy score cache without artifact hash", route["route"])
            else:
                LOG.info("%s: using cached scores", route["route"])
            return {
                "name": route["route"],
                "kind": route["kind"],
                "file_types": route["file_types"],
                "output_dir": str(output_dir),
                "indices": cache["indices"].astype(np.int64),
                "probs": cache["probs"].astype(np.float32),
            }

    t0 = time.perf_counter()
    rows_all = _fetch_rows(db_path, file_types=route["file_types"], max_id=max_id)
    fetch_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    rows = [(row_id, label) for row_id, label in rows_all if row_id in row_index]
    filter_s = time.perf_counter() - t0
    skipped = len(rows_all) - len(rows)
    if skipped:
        LOG.warning(
            "%s: skipped %d rows absent from general score cache",
            route["route"],
            skipped,
        )
    t0 = time.perf_counter()
    spec_path = output_dir / "feature_spec.json"
    spec_hash = _file_sha256(spec_path)
    spec = features.FeatureSpec.load(spec_path)
    # ``Ensemble`` averages across all members of a multi-seed bundle; for the
    # legacy single-model layout it's a length-1 ensemble whose ``predict_proba``
    # is byte-equivalent to the pre-item-A path.
    clf = bundle.Ensemble.load_bundle(output_dir)
    load_s = time.perf_counter() - t0
    row_ids = np.asarray([row_id for row_id, _label in rows], dtype=np.int64)
    rows_hash = _hash_ints(row_ids)
    t0 = time.perf_counter()
    x_matrix, feature_cache_read_s = _load_route_feature_cache(
        feature_cache_dir,
        route_name=route["route"],
        max_id=max_id,
        spec_hash=spec_hash,
        rows_hash=rows_hash,
        expected_rows=len(rows),
        expected_features=spec.total_features,
    )
    feature_cache_write_s = 0.0
    if x_matrix is None:
        batches = list(features.extract_labeled_from_db_batches(db_path, rows, spec, n_workers=workers))
        extract_s = time.perf_counter() - t0
        t0 = time.perf_counter()
        if batches:
            x_matrix = sp.vstack([batch[0] for batch in batches], format="csr")
        else:
            x_matrix = sp.csr_matrix((0, spec.total_features), dtype=np.float32)
        matrix_s = time.perf_counter() - t0
        feature_cache_write_s = _save_route_feature_cache(
            feature_cache_dir,
            route_name=route["route"],
            max_id=max_id,
            spec_hash=spec_hash,
            rows_hash=rows_hash,
            matrix=x_matrix,
        )
    else:
        extract_s = 0.0
        matrix_s = 0.0
    t0 = time.perf_counter()
    probs = clf.predict_proba(x_matrix)
    predict_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    indices = np.asarray([row_index[row_id] for row_id, _label in rows], dtype=np.int64)
    np.savez_compressed(
        cache_path,
        indices=indices,
        probs=probs.astype(np.float32),
        route_hash=np.asarray(route_hash),
        max_id=np.asarray(max_id, dtype=np.int64),
    )
    write_s = time.perf_counter() - t0
    LOG.info(
        "%s: refreshed %d rows in %.1fs "
        "(fetch %.1fs, filter %.1fs, load %.1fs, extract %.1fs, matrix %.1fs, predict %.1fs, write %.1fs; "
        "feature_cache_read %.1fs, feature_cache_write %.1fs; features=%d nnz=%d)",
        route["route"],
        len(rows),
        time.perf_counter() - started,
        fetch_s,
        filter_s,
        load_s,
        extract_s,
        matrix_s,
        predict_s,
        write_s,
        feature_cache_read_s,
        feature_cache_write_s,
        spec.total_features,
        x_matrix.nnz,
    )
    return {
        "name": route["route"],
        "kind": route["kind"],
        "file_types": route["file_types"],
        "output_dir": str(output_dir),
        "indices": indices,
        "probs": probs.astype(np.float32),
    }


def _budget(n_benign: int, target_per_million: float) -> int:
    if target_per_million <= 0:
        return 0
    return min(n_benign, max(1, int(math.floor(n_benign * target_per_million / 1_000_000))))


def _candidate_thresholds(
    labels: np.ndarray,
    indices: np.ndarray,
    probs: np.ndarray,
    *,
    max_fp: int,
    n_rows: int | None = None,
    empty_bits: np.ndarray | None = None,
) -> list[dict[str, float | int | None]]:
    if n_rows is None:
        n_rows = len(labels)
    if empty_bits is None:
        empty_bits = np.packbits(np.zeros(n_rows, dtype=bool))
    candidates: list[dict[str, Any]] = [
        {"threshold": None, "fp": 0, "tp": 0, "hit_bits": empty_bits},
    ]
    if len(indices) == 0:
        return candidates
    y = labels[indices]
    order = np.argsort(-probs, kind="mergesort")
    sorted_p = probs[order]
    sorted_y = y[order]
    tp_cum = np.cumsum(sorted_y == 1)
    fp_cum = np.cumsum(sorted_y == 0)
    best_by_fp: dict[int, dict[str, float | int]] = {}
    hit = np.zeros(n_rows, dtype=bool)
    pos = 0
    while pos < len(sorted_p):
        threshold = sorted_p[pos]
        end = pos
        while end + 1 < len(sorted_p) and sorted_p[end + 1] == threshold:
            end += 1
        hit[indices[order[pos : end + 1]]] = True
        fp = int(fp_cum[end])
        if fp > max_fp:
            break
        tp = int(tp_cum[end])
        old = best_by_fp.get(fp)
        if old is None or int(old["tp"]) <= tp:
            best_by_fp[fp] = {
                "threshold": float(threshold),
                "fp": fp,
                "tp": tp,
                "hit_bits": np.packbits(hit),
            }
        pos = end + 1
    candidates.extend(best_by_fp[fp] for fp in sorted(best_by_fp))
    return candidates


# Canonical operating-point threshold now lives in collimator.thresholds so the
# screen experiment (experiment._recall_at_per_100M) derives recall at the EXACT
# same operating point the deploy/policy-search uses. Re-exported under the old
# private name for azoth_route_policy_search's `from azoth_calibrate_ensemble
# import _quantile_severity_threshold`.
_quantile_severity_threshold = thresholds.quantile_severity_threshold

# --- Route admission --------------------------------------------------------
#
# A route ships only where it is beneficial. Same spirit as the 50-benign
# cutoff below it: don't emit a model we can't justify. This is the ONLY gate
# that sees filegroups — the conversion-time weakness gate
# (`route_prune.weak_filetype_specialists`) walks filetypes exclusively.
#
# The motivating case is a SATURATED route — one that scores benign files at
# the p=1.0 ceiling. Such a route has no dial: no threshold separates its top
# benigns from malware, so it is either off or spending its entire ceiling mass
# at once. On 2026-08-04 nine of them together put a floor of 2,016 false
# positives under the whole fleet, which is why L0 through L70 all realized the
# same FP count — three decades of dial that moved 227 FP on top of an
# immovable 2,016. filetypes/svg was the extreme: 353,179 benign files fired to
# catch 59 malicious ones.
#
# Deliberately NOT a saturation test. Saturation is a symptom; "does this route
# earn its keep" is the question, and some saturated routes are real detectors
# (png caught 494 with 171 FP). Judging them on marginal contribution keeps
# those and drops the rest, and it does so per level — a route too expensive at
# L25 can still be admitted at L5000, where the budget affords it.
#
# The comparison is against what would cover the file anyway. `general` scores
# every row and the filegroups cover most of the rest, so dropping a specialist
# degrades to them rather than to nothing.
_SPECIALIST_MIN_MARGINAL_TP_PER_FP = 1.0


def _is_backstop_route(name: str, kind: str | None) -> bool:
    """True for the one route that must never be gated out.

    `general` scores every row in the corpus, so gating it would leave files
    with nothing scoring them at all — a different and worse failure than an
    unhelpful specialist.

    Filegroups are NOT exempt, though they were until 2026-08-04. The original
    reasoning — "the filegroups are the fallback for their filetypes" — is
    wrong: general is already behind them, so a filegroup is never the last
    line of defence. Exempting them meant nothing checked them at all, because
    the conversion-time weakness gate (`route_prune.weak_filetype_specialists`)
    only walks `per_filetype_metrics["filetypes"]`. filegroups/media, trained
    that day at 0.4627 ROC-AUC and 0.0850 average precision — at or below a
    coin flip, i.e. actively misleading — would have shipped unexamined.
    """
    return name == "general"


def _clopper_pearson_fp_per_million_upper(
    x: int, n: int, *, alpha: float = 0.05,
) -> float:
    """One-sided 1−α Clopper-Pearson upper bound on the per-sample FP rate
    given x observed FPs in n benign samples, expressed as FP per million.

    Used to translate dev-observed FP counts into honest deployment FP/M
    bounds. Reflects the binomial sampling uncertainty in the observed FP
    fraction. The classic "rule of three" emerges as the x=0 case:
    upper bound ≈ 3/n × 10⁶ for large n.

    For x=0 and n=150,000 at α=0.05, this returns ~20 FP/M — the volume
    floor for our dev partition. Below this floor, no threshold can claim
    a deployment FP rate at 95% confidence.
    """
    if n <= 0:
        return float("inf")
    if x < 0 or x > n:
        raise ValueError(f"x={x} not in [0, n={n}]")
    if x == n:
        return 1_000_000.0
    import scipy.stats  # noqa: PLC0415
    upper = float(scipy.stats.beta.isf(alpha, x + 1, n - x))
    return upper * 1_000_000.0


def _max_dev_fp_for_target(
    target_per_million: float, n_benign: int, *, alpha: float = 0.05,
) -> tuple[int, bool]:
    """Largest dev FP count whose CP upper-bound projects to ≤ target FP/M.

    Returns (max_fp, below_resolution). ``below_resolution`` is True iff
    even x=0 dev FPs in n_benign already projects to a CP upper bound
    above the target — i.e., no threshold satisfies the constraint at the
    chosen confidence level. In that case the caller should fall back to
    the loosest empirical threshold producing zero dev FPs and surface
    the actual upper bound instead of pretending to hit the target.

    With n_benign=150k at α=0.05 and α=0.05, the boundary q below which
    everything is below-resolution is approximately 3/150k × 10⁶ = 20 FP/M.
    """
    if n_benign <= 0:
        return 0, True
    # Below-resolution check: x=0 already over budget.
    upper_x0 = _clopper_pearson_fp_per_million_upper(0, n_benign, alpha=alpha)
    if upper_x0 > target_per_million:
        return 0, True
    # Binary search for max x in [0, n_benign] s.t. upper(x) <= target.
    lo, hi = 0, n_benign
    best = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if _clopper_pearson_fp_per_million_upper(mid, n_benign, alpha=alpha) <= target_per_million:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best, False


def _count_masked_bits(bits: np.ndarray, mask_bits: np.ndarray) -> int:
    return int(_POPCOUNT8[np.bitwise_and(bits, mask_bits)].sum(dtype=np.uint64))


def _hit_mask(
    n_rows: int,
    indices: np.ndarray,
    probs: np.ndarray,
    threshold: float | None,
) -> np.ndarray:
    hit = np.zeros(n_rows, dtype=bool)
    if threshold is None:
        return hit
    hit[indices[probs >= threshold]] = True
    return hit


def _union_bits(
    active: dict[str, dict[str, Any]],
    *,
    empty_bits: np.ndarray,
    replace_name: str | None = None,
    replacement: dict[str, Any] | None = None,
) -> np.ndarray:
    out = empty_bits.copy()
    names = set(active)
    if replace_name is not None and replacement is not None and replacement["threshold"] is not None:
        names.add(replace_name)
    for name in names:
        candidate = replacement if name == replace_name and replacement is not None else active.get(name)
        if candidate is None or candidate["threshold"] is None:
            continue
        np.bitwise_or(out, candidate["hit_bits"], out=out)
    return out


def _prepare_calibration(
    labels: np.ndarray,
    route_scores: list[dict[str, Any]],
    *,
    max_fp: int,
) -> dict[str, Any]:
    n_rows = len(labels)
    benign = labels == 0
    malware = labels == 1
    empty_bits = np.packbits(np.zeros(n_rows, dtype=bool))
    candidates = {
        route["name"]: _candidate_thresholds(
            labels,
            route["indices"],
            route["probs"],
            max_fp=max_fp,
            n_rows=n_rows,
            empty_bits=empty_bits,
        )
        for route in route_scores
    }
    return {
        "n_rows": n_rows,
        "benign": benign,
        "malware": malware,
        "n_benign": int(np.sum(benign)),
        "n_malware": int(np.sum(malware)),
        "empty_bits": empty_bits,
        "benign_bits": np.packbits(benign),
        "malware_bits": np.packbits(malware),
        "candidates": candidates,
    }


def _calibrate_one(
    labels: np.ndarray,
    route_scores: list[dict[str, Any]],
    *,
    target_per_million: float,
    prepared: dict[str, Any] | None = None,  # noqa: ARG001 - kept for API stability
) -> dict[str, Any]:
    """Derive per-route severity-tier thresholds at ``target_per_million``.

    For each route, the threshold is the (1 − q×10⁻⁶) quantile of that
    route's calibrated benign dev scores — the *observation* of which score
    cut leaves at most q FP per million benigns below it. When q sits below
    the empirical floor (q × N_benign / 1e6 < 1), the threshold comes from
    a generalized-Pareto tail fit on the upper tail of the benign scores
    instead. Either way the answer is data-derived, not searched: there is
    no coordinate-descent over a TP-vs-FP-budget objective. The deploy
    decision (which threshold to honor at run-time) lives elsewhere — this
    function produces the L0..L9 severity grade litmus uses.

    Returns the same dict shape the legacy FP-budget search emitted so the
    rest of the pipeline (cards, route_policies.json, runtime config) keeps
    its current schema; ``below_resolution`` and ``cp_floor_per_million``
    survive as informational annotations on the chosen threshold rather
    than as gates on candidate selection.
    """
    n_rows = int(len(labels))
    benign = labels == 0
    malware = labels == 1
    n_benign = int(np.sum(benign))
    n_malware = int(np.sum(malware))
    cp_floor_per_million = _clopper_pearson_fp_per_million_upper(0, n_benign, alpha=0.05) \
        if n_benign else math.nan
    _, below_resolution = _max_dev_fp_for_target(target_per_million, n_benign, alpha=0.05) \
        if n_benign else (0, True)

    selected: dict[str, float] = {}
    diagnostics: dict[str, Any] = {}
    union_hit = np.zeros(n_rows, dtype=bool)

    # PASS 1 — every route's candidate threshold and the rows it would fire on.
    # Admission is decided afterwards, because whether a specialist is worth
    # having depends on what the rest of the ensemble already covers.
    candidates: list[dict[str, Any]] = []
    for route in route_scores:
        name = route["name"]
        indices = np.asarray(route["indices"], dtype=np.int64)
        probs = np.asarray(route["probs"], dtype=np.float64)
        n_route = int(len(indices))
        if n_route == 0:
            diagnostics[name] = {
                "kind": route.get("kind"),
                "rows": 0,
                "selected": False,
                "reason": "no rows",
                "selected_threshold": None,
                "standalone": {"threshold": None, "tp": 0, "fp": 0},
            }
            continue
        valid = ~np.isnan(probs)
        route_labels = labels[indices]
        benign_mask = valid & (route_labels == 0)
        malware_mask = valid & (route_labels == 1)
        benign_probs = probs[benign_mask]
        if len(benign_probs) < 50:
            diagnostics[name] = {
                "kind": route.get("kind"),
                "rows": n_route,
                "selected": False,
                "reason": "too few benigns to derive a quantile",
                "selected_threshold": None,
                "standalone": {"threshold": None, "tp": 0, "fp": 0},
            }
            continue
        threshold, method = _quantile_severity_threshold(benign_probs, target_per_million)
        if threshold is None:
            diagnostics[name] = {
                "kind": route.get("kind"),
                "rows": n_route,
                "selected": False,
                "reason": "quantile derivation failed",
                "selected_threshold": None,
                "standalone": {"threshold": None, "tp": 0, "fp": 0},
            }
            continue
        hit_local = (probs >= threshold) & valid
        candidates.append({
            "name": name,
            "kind": route.get("kind"),
            "rows": n_route,
            "threshold": float(threshold),
            "method": method,
            "hit_rows": indices[hit_local],
            "tp": int(np.sum(hit_local & malware_mask)),
            "fp": int(np.sum(hit_local & benign_mask)),
        })

    # PASS 2 — the fallback: what still covers a file if its route is dropped.
    # `general` carries every row, so it alone is the real counterfactual — not
    # an approximation of one. It is also the only route never gated.
    fallback_hit = np.zeros(n_rows, dtype=bool)
    for cand in candidates:
        if _is_backstop_route(cand["name"], cand["kind"]):
            fallback_hit[cand["hit_rows"]] = True

    # PASS 3 — admit. A route earns its place at this level only if it finds
    # malware general misses, at least as often as it raises false alarms
    # general would not have raised. Filegroups face this too; see
    # `_is_backstop_route` for why they are not exempt.
    for cand in candidates:
        name = cand["name"]
        row = {
            "kind": cand["kind"],
            "rows": cand["rows"],
            "method": cand["method"],
            "standalone": {
                "threshold": cand["threshold"],
                "tp": cand["tp"],
                "fp": cand["fp"],
            },
        }
        if _is_backstop_route(name, cand["kind"]):
            marginal_tp = marginal_fp = None
            admit = True
        else:
            fresh = cand["hit_rows"][~fallback_hit[cand["hit_rows"]]]
            fresh_labels = labels[fresh]
            marginal_tp = int(np.sum(fresh_labels == 1))
            marginal_fp = int(np.sum(fresh_labels == 0))
            admit = marginal_tp >= _SPECIALIST_MIN_MARGINAL_TP_PER_FP * marginal_fp
        row["marginal"] = {"tp": marginal_tp, "fp": marginal_fp}
        if not admit:
            row["selected"] = False
            row["selected_threshold"] = None
            row["reason"] = (
                f"not beneficial: {marginal_tp} new TP vs {marginal_fp} new FP "
                f"over the general/filegroup fallback"
            )
            diagnostics[name] = row
            continue
        selected[name] = cand["threshold"]
        union_hit[cand["hit_rows"]] = True
        row["selected"] = True
        row["selected_threshold"] = cand["threshold"]
        diagnostics[name] = row

    tp = int(np.sum(union_hit & malware))
    fp = int(np.sum(union_hit & benign))
    return {
        "target_per_million": float(target_per_million),
        "below_resolution": bool(below_resolution),
        "cp_floor_per_million": float(cp_floor_per_million),
        "thresholds": selected,
        "diagnostics": diagnostics,
        "tp": tp,
        "fp": fp,
        "tn": n_benign - fp,
        "fn": n_malware - tp,
        "recall": float(tp / n_malware) if n_malware else math.nan,
        "precision": float(tp / max(tp + fp, 1)),
        "fp_per_100M": float(fp * 100_000_000.0 / n_benign) if n_benign else math.nan,
    }


def _apply_mask_to_routes(
    route_scores: list[dict[str, Any]],
    mask: np.ndarray,
) -> list[dict[str, Any]]:
    """Rebuild route_scores so each route's indices/probs cover only mask=True
    rows, with indices remapped to positions in the masked label array.

    Used to restrict calibration internals (isotonic fit, threshold search,
    test eval) to a partition while leaving the score_table written over the
    full labeled corpus — downstream tools (route_diagnostics, policy_search,
    global_policy_metrics) need full coverage to compute deployment-time
    FP/M against the real benign denominator.
    """
    if mask.dtype != bool:
        mask = mask.astype(bool)
    cumsum = np.cumsum(mask.astype(np.int64)) - 1
    out: list[dict[str, Any]] = []
    for r in route_scores:
        idx = np.asarray(r["indices"], dtype=np.int64)
        keep = mask[idx]
        new_indices = cumsum[idx[keep]].astype(np.int64)
        new_probs = np.asarray(r["probs"])[keep]
        out.append({**r, "indices": new_indices, "probs": new_probs})
    return out


def _evaluate_thresholds_at_level(
    labels: np.ndarray,
    route_scores: list[dict[str, Any]],
    *,
    thresholds_for_level: dict[str, float],
    target_per_million: float,
) -> dict[str, Any]:
    """Apply already-chosen thresholds to (possibly different) labels+scores.

    Mirrors _calibrate_one's return shape but does no fitting or search.
    Use for "fit on dev, evaluate on test" scoring: thresholds come from a
    prior dev run; labels and probs come from the test partition.

    Routes named in thresholds_for_level but missing from route_scores are
    skipped (they were deployed but their model isn't present in this
    invocation, e.g. a specialist whose feature spec wasn't built).
    """
    n_rows = len(labels)
    benign_bits = np.packbits(labels == 0)
    malware_bits = np.packbits(labels == 1)
    n_benign = int(np.sum(labels == 0))
    n_malware = int(np.sum(labels == 1))
    by_name = {route["name"]: route for route in route_scores}
    selected: dict[str, float | None] = {route["name"]: None for route in route_scores}
    union = np.zeros_like(benign_bits)
    diagnostics: dict[str, Any] = {}
    for name, threshold in thresholds_for_level.items():
        route = by_name.get(name)
        if route is None or threshold is None:
            continue
        selected[name] = float(threshold)
        hit = _hit_mask(n_rows, route["indices"], route["probs"], float(threshold))
        union = np.bitwise_or(union, np.packbits(hit))
        # Per-route standalone counts (no union across routes).
        standalone_tp = _count_masked_bits(np.packbits(hit), malware_bits)
        standalone_fp = _count_masked_bits(np.packbits(hit), benign_bits)
        diagnostics[name] = {
            "kind": route.get("kind"),
            "rows": int(len(route["indices"])),
            "selected": True,
            "selected_threshold": float(threshold),
            "standalone": {
                "threshold": float(threshold),
                "tp": int(standalone_tp),
                "fp": int(standalone_fp),
            },
            "best_marginal": {"threshold": float(threshold), "inc_tp": 0, "inc_fp": 0,
                              "tp": int(standalone_tp), "fp": int(standalone_fp)},
        }
    tp = _count_masked_bits(union, malware_bits)
    fp = _count_masked_bits(union, benign_bits)
    return {
        "target_per_million": float(target_per_million),
        "budget": _budget(n_benign, target_per_million),
        "thresholds": {n: t for n, t in selected.items() if t is not None},
        "diagnostics": diagnostics,
        "tp": tp,
        "fp": fp,
        "tn": n_benign - fp,
        "fn": n_malware - tp,
        "recall": float(tp / n_malware) if n_malware else math.nan,
        "precision": float(tp / max(tp + fp, 1)),
        "fp_per_100M": float(fp * 100_000_000.0 / n_benign) if n_benign else math.nan,
    }


def _load_routes(summary_path: Path) -> list[dict[str, Any]]:
    # Residual buckets cleave can't characterize coherently (see
    # azoth_specialist_suite.RESIDUAL_FILETYPES). Older bundles may
    # still carry trained specialist artifacts on disk for these; skip
    # them here so they don't enter the route list, regardless of what
    # specialists.json says.
    residual_filetypes = {"unknown", "data"}
    with open(summary_path) as f:
        summary = json.load(f)
    root = summary_path.parent
    routes: list[dict[str, Any]] = []
    for item in summary["results"]:
        if item.get("error") or item.get("kind") not in {"filegroup", "filetype"}:
            continue
        if item.get("kind") == "filetype" and item.get("name") in residual_filetypes:
            continue
        route = (
            f"filegroups/{item['name']}"
            if item["kind"] == "filegroup"
            else f"filetypes/{item['name']}"
        )
        route_dir = root / route
        # No model on disk → not a deployable route. This covers routes
        # training deliberately refused to emit (constant predictors) as
        # well as partial/legacy bundles. Dropping it here keeps it out of
        # config.json so litmus routes those files to the filegroup/general
        # ensemble (absent specialists are droppable on the loader side).
        if not (bundle.has_model(route_dir) and (route_dir / "feature_spec.json").exists()):
            LOG.info("skipping route %s: no model on disk", route)
            continue
        # Degenerate (constant-predictor) routes carry no signal. Drop them
        # so they never enter config.json — the stager copies per config, so
        # this keeps them out of the entire deploy; litmus routes those files
        # to the filegroup/general ensemble.
        if export.route_model_is_degenerate(route_dir):
            LOG.info("skipping route %s: constant-predictor model (no split learned)", route)
            continue
        normalized = {**item, "route": route, "output_dir": str(route_dir)}
        routes.append(normalized)
    return routes


def _filetype_to_group() -> dict[str, str]:
    out: dict[str, str] = {}
    for group, file_types in DEPLOYMENT_GROUPS.items():
        for file_type in file_types:
            out[file_type] = group
    return out


def _write_score_table(
    path: Path,
    *,
    row_ids: np.ndarray,
    labels: np.ndarray,
    file_types: np.ndarray,
    file_groups: np.ndarray,
    route_scores: list[dict[str, Any]],
) -> str:
    names = np.asarray([route["name"] for route in route_scores])
    kinds = np.asarray([route["kind"] for route in route_scores])
    scores = np.full((len(route_scores), len(row_ids)), np.nan, dtype=np.float32)
    for idx, route in enumerate(route_scores):
        scores[idx, route["indices"]] = route["probs"]
    path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write via a process-unique temp + os.replace. np.savez_compressed
    # streams a zip straight to the target, so a killed/overlapping writer (the
    # autocollie loop runs calibrate concurrently) would leave a truncated .npz
    # that crashes every downstream reader with EOFError. The pid suffix keeps
    # the temp private; os.replace makes the final file appear all-at-once.
    tmp = path.with_name(path.name.removesuffix(".npz") + f".tmp.{os.getpid()}.npz")
    np.savez_compressed(
        tmp,
        row_ids=row_ids,
        labels=labels,
        file_types=file_types,
        file_groups=file_groups,
        route_names=names,
        route_kinds=kinds,
        scores=scores,
    )
    os.replace(tmp, path)
    return _file_sha256(path)


def _score_pool_init(log_level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _score_route_worker(job: dict[str, Any]) -> dict[str, Any]:
    return _score_route(
        job["db_path"],
        job["route"],
        row_index=job["row_index"],
        max_id=job["max_id"],
        workers=job["workers"],
        refresh=job["refresh"],
        refresh_routes=job["refresh_routes"],
        feature_cache_dir=job["feature_cache_dir"],
        oof_route_scores_dir=job.get("oof_route_scores_dir"),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--azoth-root", type=Path, default=Path("out/models/azoth"))
    parser.add_argument("--summary", type=Path, default=Path("out/models/azoth/specialists.json"))
    parser.add_argument("--general-scores", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("out/models/azoth/config.json"))
    parser.add_argument(
        "--score-table",
        type=Path,
        default=Path("out/models/azoth/score_table.npz"),
    )
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument(
        "--refresh-route",
        action="append",
        default=[],
        help="Force-refresh one route score cache, e.g. filetypes/python or python; repeatable",
    )
    parser.add_argument(
        "--skip-level-calibration",
        action="store_true",
        help="Write score_table/config targets, but skip fallback ensemble threshold search",
    )
    parser.add_argument(
        "--feature-cache-dir",
        type=Path,
        default=Path("out/cache/azoth-route-features"),
        help="Shared cache for extracted route feature matrices; use 'none' to disable",
    )
    parser.add_argument(
        "--oof-route-scores-dir",
        type=Path,
        default=None,
        help=(
            "Directory of per-route OOF scores produced by "
            "azoth_oof_score_routes.py. When set, each route's scoring "
            "step reads "
            "{oof_route_scores_dir}/<route>/threshold_scores.npz instead "
            "of running an in-sample predict_proba pass. Routes missing "
            "an OOF file fall back to in-sample scoring with a warning. "
            "Pair with --general-scores pointing at an OOF general "
            "threshold_scores.npz for fully-honest calibration."
        ),
    )
    parser.add_argument(
        "--partition",
        choices=("dev", "test", "all"),
        default="dev",
        help=(
            "Which partition to fit calibrators and report metrics on. 'dev' "
            "(default) is the held-out selection slice — calibrators and L0..L9 "
            "thresholds are fit honestly here. 'test' applies the existing bundle "
            "to the locked test slice for headline reporting (use with "
            "--apply-thresholds-from to skip fitting). 'all' is the legacy leaky-"
            "corpus behavior, retained for sanity-check comparisons only."
        ),
    )
    parser.add_argument(
        "--apply-thresholds-from",
        type=Path,
        default=None,
        help=(
            "Path to a config.json from a prior calibration run (typically the "
            "dev-fit one). When set, this invocation skips isotonic fitting and "
            "threshold search; it loads the per-level thresholds and applies "
            "them to the rows in --partition, writing a metrics-only artifact at "
            "{azoth_root}/{partition}_metrics.{json,md}. Standard config.json / "
            "score_table / route policies are NOT overwritten — those came from "
            "the dev fit and stay deployed."
        ),
    )
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument(
        "--parallelism",
        type=int,
        default=1,
        help=(
            "Score this many routes concurrently in worker processes. "
            "Default 1 (sequential). Bump to 2-3 to overlap feature "
            "extraction and prediction across routes; mind the same "
            "CPU/DB caveats as azoth_specialist_suite --parallelism."
        ),
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    general_cache = np.load(args.general_scores)
    feature_cache_dir = None if str(args.feature_cache_dir).lower() == "none" else args.feature_cache_dir
    row_ids = general_cache["row_ids"].astype(np.int64)
    labels = general_cache["labels"].astype(np.int8)
    general_probs = general_cache["probs"].astype(np.float32)
    max_id = int(general_cache["corpus_requested_max_id"])
    if max_id <= 0:
        max_id = int(general_cache["corpus_max_row_id"])

    # Partition handling. The score_table is always written over the FULL
    # labeled corpus so downstream tools (route_diagnostics, policy_search,
    # global_policy_metrics) can compute deployment-time FP/M against the
    # real benign denominator. The partition filter is applied DEEP — at the
    # isotonic-fit and threshold-search call sites — by restricting labels
    # and route_scores to mask=True rows. This separates score-table coverage
    # from calibration honesty: routes are scored on every row; calibrators
    # and L0..L9 thresholds only see the dev partition.
    if args.partition != "all":
        if "canonical_shas" not in general_cache.files:
            raise SystemExit(
                "general_scores cache lacks canonical_shas; rebuild it (e.g. via "
                "make thresholds-refresh) before calibrating with --partition="
                f"{args.partition}",
            )
        canonical_shas = general_cache["canonical_shas"]
        partition_mask = np.array(
            [data.partition_of(str(c)) == args.partition for c in canonical_shas],
            dtype=bool,
        )
        n_keep = int(np.sum(partition_mask))
        if n_keep == 0:
            raise SystemExit(f"no rows in partition '{args.partition}'")
        LOG.info(
            "partition '%s': %d of %d rows (%.1f%%) kept for fit/eval; score_table covers all %d",
            args.partition, n_keep, len(row_ids),
            100.0 * n_keep / max(len(row_ids), 1), len(row_ids),
        )
    else:
        partition_mask = np.ones(len(row_ids), dtype=bool)
    row_index = {int(row_id): idx for idx, row_id in enumerate(row_ids)}

    file_types_by_row = _fetch_file_types(args.db, row_ids)
    filetype_to_group = _filetype_to_group()
    file_types = np.asarray(
        [file_types_by_row.get(int(row_id), "unknown") for row_id in row_ids],
    )
    file_groups = np.asarray([filetype_to_group.get(file_type, "") for file_type in file_types])
    route_scores = [
        {
            "name": "general",
            "kind": "general",
            "file_types": [],
            "output_dir": str(args.azoth_root / "general"),
            "indices": np.arange(len(row_ids), dtype=np.int64),
            "probs": general_probs,
        },
    ]
    routes = list(_load_routes(args.summary))
    refresh_routes = set(args.refresh_route)
    # Cap per-route extraction workers. Each of the `parallelism` concurrent
    # route jobs re-extracts its FULL-row matrix, and each worker buffers a
    # batch of cleave reports — so the resident report memory scales with
    # (parallelism * workers). At the default workers=128 * parallelism, this
    # spiked to ~240 GB and OOM-killed the co-tenant litmus scanner. Mirror the
    # specialist suite: divide by parallelism and cap at an absolute ceiling
    # (~28 GB/job operating point). Override via AZOTH_CALIBRATE_EXTRACT_WORKERS_MAX.
    extract_workers = args.workers
    if args.workers and args.workers > 1:
        ceiling = max(1, int(os.environ.get("AZOTH_CALIBRATE_EXTRACT_WORKERS_MAX", "16")))
        per_job = args.workers // max(1, args.parallelism)
        extract_workers = max(1, min(per_job, ceiling))
        if extract_workers != args.workers:
            LOG.info("capping per-route extraction workers at %d (requested %d, parallelism=%d, ceiling=%d)",
                     extract_workers, args.workers, args.parallelism, ceiling)
    score_jobs = [
        {
            "db_path": args.db,
            "route": route,
            "row_index": row_index,
            "max_id": max_id,
            "workers": extract_workers,
            "refresh": args.refresh,
            "refresh_routes": refresh_routes,
            "feature_cache_dir": feature_cache_dir,
            "oof_route_scores_dir": args.oof_route_scores_dir,
        }
        for route in routes
    ]
    if args.parallelism > 1 and len(score_jobs) > 1:
        LOG.info("scoring %d routes (parallelism=%d)", len(score_jobs), args.parallelism)
        route_scores.extend([None] * len(score_jobs))
        # `spawn` start method instead of `fork` so each worker boots a clean
        # interpreter and re-imports numpy/lightgbm/onnxruntime fresh — no
        # inherited OpenMP/BLAS thread-pool state from the parent. Fork
        # inherited the parent's BLAS mutex in a state the child can't safely
        # use, producing silent futex_wait deadlocks in worker subprocesses
        # (observed 2026-06-01 with parallelism=2 on a 64-core box). The
        # ~1s/worker spawn overhead is negligible vs. minutes-per-route
        # scoring work.
        import multiprocessing as _mp  # noqa: PLC0415 — guard against fork side-effects
        _spawn_ctx = _mp.get_context("spawn")
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.parallelism,
            mp_context=_spawn_ctx,
            initializer=_score_pool_init,
            initargs=(args.log_level,),
        ) as pool:
            futures = {
                pool.submit(_score_route_worker, job): idx
                for idx, job in enumerate(score_jobs)
            }
            general_offset = 1  # index 0 is the general entry already appended above
            for fut in concurrent.futures.as_completed(futures):
                idx = futures[fut]
                route_scores[general_offset + idx] = fut.result()
    else:
        for job in score_jobs:
            LOG.info("scoring %s", job["route"]["route"])
            route_scores.append(_score_route_worker(job))

    # Eval-only short-circuit: load thresholds from a prior dev-fit config,
    # apply them to this partition's rows, and write metrics-only output.
    # The deployed score_table.npz, isotonic calibrators, and config.json
    # all came from the dev run and stay on disk untouched. Routes are
    # scored on the full corpus above; the partition_mask restricts which
    # rows count for tp/fp at each level.
    if args.apply_thresholds_from is not None:
        prior = json.loads(Path(args.apply_thresholds_from).read_text())
        prior_levels = prior.get("levels", [])
        if not prior_levels:
            raise SystemExit(
                f"--apply-thresholds-from {args.apply_thresholds_from} has no "
                "levels; was the dev calibration completed?",
            )
        eval_labels = labels[partition_mask]
        eval_route_scores = _apply_mask_to_routes(route_scores, partition_mask)
        eval_levels: list[dict[str, Any]] = []
        for prior_level in prior_levels:
            level_id = int(prior_level["level"])
            hostile = _evaluate_thresholds_at_level(
                eval_labels, eval_route_scores,
                thresholds_for_level=prior_level["hostile"].get("thresholds", {}),
                target_per_million=float(prior_level["hostile"]["target_per_million"]),
            )
            # Carry through the dev-side resolution flags. These are
            # properties of the threshold-fit data, not of test eval — we
            # propagate them so cards rendered from test_metrics.json can
            # mark "below resolution" rows transparently.
            sev_src = prior_level["hostile"]
            if "below_resolution" in sev_src:
                hostile["below_resolution"] = bool(sev_src["below_resolution"])
            if "cp_floor_per_million" in sev_src:
                hostile["cp_floor_per_million"] = float(sev_src["cp_floor_per_million"])
            LOG.info(
                "L%d on %s: hostile recall=%.2f%% fp=%d (FP/100M=%.2f)",
                level_id, args.partition,
                hostile["recall"] * 100, hostile["fp"], hostile["fp_per_100M"],
            )
            eval_levels.append({"level": level_id, "hostile": hostile})
        metrics_path = args.azoth_root / f"{args.partition}_metrics.json"
        bundle.atomic_write_json(metrics_path, {
            "schema": "azoth.evaluation.v1",
            "timestamp": datetime.now(UTC).isoformat(),
            "applied_from": str(args.apply_thresholds_from),
            "partition": args.partition,
            "rows": int(eval_labels.size),
            "malware": int(np.sum(eval_labels == 1)),
            "benign": int(np.sum(eval_labels == 0)),
            "levels": eval_levels,
        })
        print(f"wrote {metrics_path}")
        return 0

    # Score table over the full labeled corpus — downstream tools need full
    # benign coverage to compute deployment-time FP/M.
    score_table_hash = _write_score_table(
        args.score_table,
        row_ids=row_ids,
        labels=labels,
        file_types=file_types,
        file_groups=file_groups,
        route_scores=route_scores,
    )
    # Calibrators and L0..L9 thresholds are fit on the partition subset
    # only — that's where the leakage protection lives. Score table above
    # is unaffected.
    fit_labels = labels[partition_mask]
    fit_route_scores = _apply_mask_to_routes(route_scores, partition_mask)
    # No per-route isotonic calibrator is emitted: it was decision-irrelevant
    # (monotonic; litmus mapped thresholds through it) and saturated the
    # upper score tail, which also collapsed the learned blend's logit inputs.
    # Deploy now runs on raw GBDT probabilities end to end — the level grids and
    # blends are fit on raw scores. See the project_calibrator_decision_irrelevant
    # memory. (litmus treats an absent calibrator.json as raw passthrough.)
    model_set_hash = _hash_model_set(args.general_scores, route_scores)
    levels: list[dict[str, Any]] = []
    if args.skip_level_calibration:
        n_benign = int(np.sum(fit_labels == 0))
        for target in thresholds.SEVERITY_LEVEL_TARGETS:
            level = int(target["level"])
            hostile_target = float(target["hostile_per_million"])
            levels.append(
                {
                    "level": level,
                    "hostile": {
                        "target_per_million": hostile_target,
                        "budget": _budget(n_benign, hostile_target),
                        "thresholds": {},
                        "diagnostics": {},
                        "tp": 0,
                        "fp": 0,
                        "tn": n_benign,
                        "fn": int(np.sum(fit_labels == 1)),
                        "recall": 0.0,
                        "precision": 0.0,
                        "fp_per_100M": 0.0,
                        "skipped": True,
                    },
                },
            )
        LOG.info("skipped fallback level calibration; wrote score table and policy targets only")
    else:
        for target in thresholds.SEVERITY_LEVEL_TARGETS:
            level = int(target["level"])
            hostile = _calibrate_one(
                fit_labels,
                fit_route_scores,
                target_per_million=float(target["hostile_per_million"]),
            )
            LOG.info(
                "L%d hostile recall=%.2f%% fp=%d",
                level,
                hostile["recall"] * 100,
                hostile["fp"],
            )
            levels.append({"level": level, "hostile": hostile})

    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "schema": "azoth.routed_ensemble.v1",
        "max_id": max_id,
        "calibration_snapshot_id": max_id,
        "score_table": str(args.score_table),
        "score_table_hash": score_table_hash,
        "model_set_hash": model_set_hash,
        "search": {
            "method": "skipped_score_table_only" if args.skip_level_calibration else "quantile_severity_v1",
            "objective": "per-route (1-q*1e-6) interpolated benign-score quantile; strict levels cluster at the 1-FP ceiling below resolution (no tail extrapolation)",
        },
        "rows": int(len(labels)),
        "malware": int(np.sum(labels == 1)),
        "benign": int(np.sum(labels == 0)),
        "fit_partition": args.partition,
        "fit_rows": int(len(fit_labels)),
        "fit_malware": int(np.sum(fit_labels == 1)),
        "fit_benign": int(np.sum(fit_labels == 0)),
        "root": str(args.azoth_root),
        "filetype_to_group": filetype_to_group,
        "observed_filetypes": {
            file_type: sum(1 for ft in file_types_by_row.values() if ft == file_type)
            for file_type in sorted(set(file_types_by_row.values()))
        },
        "models": [
            {
                "route": route["name"],
                "kind": route["kind"],
                "rows": int(len(route["indices"])),
            }
            for route in route_scores
        ],
        "levels": levels,
        # The deploy tuning goal prescribed BY THIS MODEL. collimator's single
        # knob (thresholds.DEFAULT_SEVERITY_LEVEL) is baked into the bundle here
        # so litmus and autocollie read the operating point from the model
        # config instead of mirroring a constant. litmus still honors an explicit
        # CLI level; this is only the default when none is requested. Consumers
        # fall back to their own const only for older configs lacking the field.
        "default_severity_level": int(thresholds.DEFAULT_SEVERITY_LEVEL),
    }
    # Atomic write: config.json is consumed by litmus, validate, deploy, etc.
    bundle.atomic_write_json(args.output, payload)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
