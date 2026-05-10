#!/usr/bin/env python3
"""Calibrate routed azoth ensemble thresholds against the full corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp

from collimator import bundle, data, features, model, thresholds

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
    tmp_matrix = matrix_path.with_name(matrix_path.name.removesuffix(".npz") + ".tmp.npz")
    tmp_meta = meta_path.with_suffix(meta_path.suffix + ".tmp")
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
                    out.update({int(row_id): str(file_type) for row_id, file_type in cur})
        else:
            for chunk in _chunks(ids, 10_000):
                placeholders = ",".join("?" for _ in chunk)
                query = (
                    "SELECT id, COALESCE(NULLIF(file_type, ''), 'unknown') "
                    f"FROM samples WHERE id IN ({placeholders})"
                )
                out.update(
                    {
                        int(row_id): str(file_type)
                        for row_id, file_type in conn.execute(query, chunk)
                    },
                )
    return out


def _fetch_rows(
    db_path: Path | str,
    *,
    file_types: list[str],
    max_id: int,
) -> list[tuple[int, int]]:
    marker = "%s" if data._is_pg(db_path) else "?"  # noqa: SLF001
    where = [
        "label IN ('bad', 'good')",
        "cleave_result IS NOT NULL",
        "skip = ''",
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
) -> dict[str, Any]:
    started = time.perf_counter()
    output_dir = Path(route["output_dir"])
    cache_path = output_dir / "calibration_scores.npz"
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
    prepared: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if prepared is None:
        n_benign = int(np.sum(labels == 0))
        prepared = _prepare_calibration(
            labels,
            route_scores,
            max_fp=_budget(n_benign, target_per_million),
        )
    n_rows = int(prepared["n_rows"])
    benign = prepared["benign"]
    malware = prepared["malware"]
    n_benign = int(prepared["n_benign"])
    n_malware = int(prepared["n_malware"])
    max_fp = _budget(n_benign, target_per_million)
    empty_bits = prepared["empty_bits"]
    benign_bits = prepared["benign_bits"]
    malware_bits = prepared["malware_bits"]
    selected: dict[str, float | None] = {route["name"]: None for route in route_scores}
    candidates = {
        name: [candidate for candidate in route_candidates if int(candidate["fp"] or 0) <= max_fp]
        for name, route_candidates in prepared["candidates"].items()
    }
    by_name = {route["name"]: route for route in route_scores}
    active: dict[str, dict[str, Any]] = {}

    general_candidates = candidates.get("general", [{"threshold": None, "tp": 0, "fp": 0}])
    general_best = max(general_candidates, key=lambda item: int(item["tp"] or 0))
    if general_best["threshold"] is not None:
        selected["general"] = float(general_best["threshold"])
        active["general"] = general_best

    current_bits = _union_bits(active, empty_bits=empty_bits)
    current_fp = _count_masked_bits(current_bits, benign_bits)
    current_tp = _count_masked_bits(current_bits, malware_bits)

    while True:
        best: tuple[int, int, str, float | None, dict[str, Any], np.ndarray, int, int] | None = None
        for name, route_candidates in candidates.items():
            for candidate in route_candidates:
                threshold = candidate["threshold"]
                proposed_bits = _union_bits(
                    active,
                    empty_bits=empty_bits,
                    replace_name=name,
                    replacement=candidate,
                )
                fp = _count_masked_bits(proposed_bits, benign_bits)
                if fp > max_fp:
                    continue
                tp = _count_masked_bits(proposed_bits, malware_bits)
                inc_fp = fp - current_fp
                inc_tp = tp - current_tp
                if inc_tp <= 0:
                    continue
                key = (
                    inc_tp,
                    -max(inc_fp, 0),
                    name,
                    None if threshold is None else float(threshold),
                    candidate,
                    proposed_bits,
                    tp,
                    fp,
                )
                if best is None or key[:2] > best[:2]:
                    best = key
        if best is None:
            break
        _inc_tp, _neg_inc_fp, name, threshold, candidate, current_bits, current_tp, current_fp = best
        selected[name] = threshold
        if threshold is None:
            active.pop(name, None)
        else:
            active[name] = candidate

    diagnostics: dict[str, Any] = {}
    for name, route in by_name.items():
        route_candidates = candidates[name]
        standalone = max(
            route_candidates,
            key=lambda item: (int(item["tp"] or 0), -int(item["fp"] or 0)),
        )
        best_marginal: dict[str, Any] | None = None
        for candidate in route_candidates:
            threshold = candidate["threshold"]
            proposed_bits = _union_bits(
                active,
                empty_bits=empty_bits,
                replace_name=name,
                replacement=candidate,
            )
            fp = _count_masked_bits(proposed_bits, benign_bits)
            if fp > max_fp:
                continue
            tp = _count_masked_bits(proposed_bits, malware_bits)
            inc_fp = fp - current_fp
            inc_tp = tp - current_tp
            item = {
                "threshold": None if threshold is None else float(threshold),
                "inc_tp": inc_tp,
                "inc_fp": inc_fp,
                "tp": tp,
                "fp": fp,
            }
            if best_marginal is None or (inc_tp, -max(inc_fp, 0)) > (
                int(best_marginal["inc_tp"]),
                -max(int(best_marginal["inc_fp"]), 0),
            ):
                best_marginal = item
        diagnostics[name] = {
            "kind": route.get("kind"),
            "rows": int(len(route["indices"])),
            "selected": selected[name] is not None,
            "selected_threshold": selected[name],
            "standalone": {
                "threshold": standalone["threshold"],
                "tp": int(standalone["tp"] or 0),
                "fp": int(standalone["fp"] or 0),
            },
            "best_marginal": best_marginal
            or {"threshold": None, "inc_tp": 0, "inc_fp": 0, "tp": current_tp, "fp": current_fp},
        }

    return {
        "target_per_million": float(target_per_million),
        "budget": max_fp,
        "thresholds": {name: thr for name, thr in selected.items() if thr is not None},
        "diagnostics": diagnostics,
        "tp": current_tp,
        "fp": current_fp,
        "tn": n_benign - current_fp,
        "fn": n_malware - current_tp,
        "recall": float(current_tp / n_malware) if n_malware else math.nan,
        "precision": float(current_tp / max(current_tp + current_fp, 1)),
        "fp_per_million": float(current_fp * 1_000_000.0 / n_benign) if n_benign else math.nan,
    }


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
        "fp_per_million": float(fp * 1_000_000.0 / n_benign) if n_benign else math.nan,
    }


def _load_routes(summary_path: Path) -> list[dict[str, Any]]:
    with open(summary_path) as f:
        summary = json.load(f)
    root = summary_path.parent
    routes: list[dict[str, Any]] = []
    for item in summary["results"]:
        if item.get("error") or item.get("kind") not in {"filegroup", "filetype"}:
            continue
        route = (
            f"filegroups/{item['name']}"
            if item["kind"] == "filegroup"
            else f"filetypes/{item['name']}"
        )
        route_dir = root / route
        normalized = {**item, "route": route}
        if bundle.has_model(route_dir) and (route_dir / "feature_spec.json").exists():
            normalized["output_dir"] = str(route_dir)
        routes.append(normalized)
    return routes


def _filetype_to_group() -> dict[str, str]:
    out: dict[str, str] = {}
    for group, file_types in DEPLOYMENT_GROUPS.items():
        for file_type in file_types:
            out[file_type] = group
    return out


def _fit_and_persist_isotonic_calibrator(
    route_scores: list[dict[str, Any]],
    labels: np.ndarray,
    azoth_root: Path,
) -> None:
    """For each route, fit isotonic regression on (raw probability, label) and
    write the calibrator's breakpoints to ``<route_slot>/calibrator.json``.

    Litmus loads this file at score time and applies the calibration before
    emitting the file's probability — so the deployed score is on the same
    [0, 1] probability scale the per-route specialist was empirically observed
    to produce on the calibration corpus.

    Why this matters: raw LightGBM/XGBoost output is a logit-derived probability
    that's miscalibrated by training-set prior, sample weights, and class
    imbalance.  Two specialists with the same ROC AUC can have wildly different
    score distributions; one outputs scores tightly clustered near 0.5, the
    other spreads them across [0, 1].  Without per-route calibration, the
    routing layer's "max across routes" picks routes by their score spread,
    not by their actual confidence.

    Output schema (``calibrator.json``)::

        {
          "schema": "azoth.calibrator.isotonic.v1",
          "x": [...],                # ascending, raw probabilities at breakpoints
          "y": [...],                # monotone-non-decreasing calibrated probs
          "out_of_bounds": "clip",   # x < x[0] -> y[0]; x > x[-1] -> y[-1]
          "n_train": int,            # rows used to fit
          "fit_log": str             # human-readable diagnostic
        }

    Litmus interpolates linearly between breakpoints; clip semantics handle
    the tails.

    The calibrator is fit on the *full* calibration corpus we have labels
    for — this maximizes the data the calibrator sees.  Honest holdout
    evaluation lives in ``compute_routed_metrics.py`` (5-fold CV); the
    bundle ships the strongest calibrator we can train.
    """
    from sklearn.isotonic import IsotonicRegression  # noqa: PLC0415

    calibrators_written = 0
    for entry in route_scores:
        name = entry["name"]
        probs = entry["probs"]
        indices = entry["indices"]
        if probs is None or len(probs) == 0:
            continue
        # Pull the labels of just this route's scored rows (entry["indices"]
        # are positions into the global score-table label array).
        route_labels = labels[indices]
        valid = ~np.isnan(probs)
        if int(valid.sum()) < 50:
            LOG.info("calibrator: skipping %s (only %d valid rows)", name, int(valid.sum()))
            continue
        x = probs[valid].astype(np.float64)
        y = route_labels[valid].astype(np.float64)
        if y.sum() == 0 or (y == 0).sum() == 0:
            LOG.info("calibrator: skipping %s (single-class fold)", name)
            continue
        iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
        iso.fit(x, y)
        # IsotonicRegression exposes its piecewise-constant fit as
        # X_thresholds_/y_thresholds_; persist those directly.
        x_thr = iso.X_thresholds_.astype(float).tolist()
        y_thr = iso.y_thresholds_.astype(float).tolist()
        slot_dir = azoth_root / name
        slot_dir.mkdir(parents=True, exist_ok=True)
        cal_path = slot_dir / "calibrator.json"
        cal = {
            "schema": "azoth.calibrator.isotonic.v1",
            "x": x_thr,
            "y": y_thr,
            "out_of_bounds": "clip",
            "n_train": int(valid.sum()),
            "fit_log": (
                f"isotonic regression on {int(valid.sum())} rows "
                f"({int(y.sum())} malware, {int((y == 0).sum())} benign); "
                f"breakpoints: {len(x_thr)}"
            ),
        }
        # Atomic write: litmus reads calibrator.json on every load and a
        # partially-written file would NaN-poison every prediction for the
        # affected route until the next deploy.
        bundle.atomic_write_json(cal_path, cal)
        calibrators_written += 1
    LOG.info("wrote %d per-route isotonic calibrators", calibrators_written)


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
    np.savez_compressed(
        path,
        row_ids=row_ids,
        labels=labels,
        file_types=file_types,
        file_groups=file_groups,
        route_names=names,
        route_kinds=kinds,
        scores=scores,
    )
    return _file_sha256(path)


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

    # Partition filter. Caches built before the dev/test/train methodology
    # (no canonical_shas array) cannot be filtered safely; require legacy mode.
    if args.partition != "all":
        if "canonical_shas" not in general_cache.files:
            raise SystemExit(
                "general_scores cache lacks canonical_shas; rebuild it (e.g. via "
                "make thresholds-refresh) before calibrating with --partition="
                f"{args.partition}",
            )
        canonical_shas = general_cache["canonical_shas"]
        keep = np.array(
            [data.partition_of(str(c)) == args.partition for c in canonical_shas],
            dtype=bool,
        )
        n_keep = int(np.sum(keep))
        if n_keep == 0:
            raise SystemExit(f"no rows in partition '{args.partition}'")
        LOG.info(
            "partition '%s' filter retained %d of %d rows (%.1f%%)",
            args.partition, n_keep, len(row_ids), 100.0 * n_keep / max(len(row_ids), 1),
        )
        row_ids = row_ids[keep]
        labels = labels[keep]
        general_probs = general_probs[keep]
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
    for route in _load_routes(args.summary):
        LOG.info("scoring %s", route["route"])
        route_scores.append(
            _score_route(
                args.db,
                route,
                row_index=row_index,
                max_id=max_id,
                workers=args.workers,
                refresh=args.refresh,
                refresh_routes=set(args.refresh_route),
                feature_cache_dir=feature_cache_dir,
            ),
        )

    # Eval-only short-circuit: load thresholds from a prior dev-fit config,
    # apply them to this partition's rows, and write metrics-only output.
    # The deployed score_table.npz, isotonic calibrators, and config.json
    # all came from the dev run and stay on disk untouched.
    if args.apply_thresholds_from is not None:
        prior = json.loads(Path(args.apply_thresholds_from).read_text())
        prior_levels = prior.get("levels", [])
        if not prior_levels:
            raise SystemExit(
                f"--apply-thresholds-from {args.apply_thresholds_from} has no "
                "levels; was the dev calibration completed?",
            )
        eval_levels: list[dict[str, Any]] = []
        for prior_level in prior_levels:
            level_id = int(prior_level["level"])
            hostile = _evaluate_thresholds_at_level(
                labels, route_scores,
                thresholds_for_level=prior_level["hostile"].get("thresholds", {}),
                target_per_million=float(prior_level["hostile"]["target_per_million"]),
            )
            suspicious = _evaluate_thresholds_at_level(
                labels, route_scores,
                thresholds_for_level=prior_level["suspicious"].get("thresholds", {}),
                target_per_million=float(prior_level["suspicious"]["target_per_million"]),
            )
            LOG.info(
                "L%d on %s: hostile recall=%.2f%% fp=%d (FP/M=%.2f); suspicious recall=%.2f%% fp=%d (FP/M=%.2f)",
                level_id, args.partition,
                hostile["recall"] * 100, hostile["fp"], hostile["fp_per_million"],
                suspicious["recall"] * 100, suspicious["fp"], suspicious["fp_per_million"],
            )
            eval_levels.append({"level": level_id, "hostile": hostile, "suspicious": suspicious})
        metrics_path = args.azoth_root / f"{args.partition}_metrics.json"
        bundle.atomic_write_json(metrics_path, {
            "schema": "azoth.evaluation.v1",
            "timestamp": datetime.now(UTC).isoformat(),
            "applied_from": str(args.apply_thresholds_from),
            "partition": args.partition,
            "rows": int(len(labels)),
            "malware": int(np.sum(labels == 1)),
            "benign": int(np.sum(labels == 0)),
            "levels": eval_levels,
        })
        print(f"wrote {metrics_path}")
        return 0

    score_table_hash = _write_score_table(
        args.score_table,
        row_ids=row_ids,
        labels=labels,
        file_types=file_types,
        file_groups=file_groups,
        route_scores=route_scores,
    )
    # Per-route isotonic calibrators (azoth.calibrator.isotonic.v1).  Litmus
    # loads these next to model.txt at runtime and applies before emitting the
    # per-route probability — closes the gap between reported AUC (post-
    # calibration) and deployed AUC.
    _fit_and_persist_isotonic_calibrator(route_scores, labels, args.azoth_root)
    model_set_hash = _hash_model_set(args.general_scores, route_scores)
    levels: list[dict[str, Any]] = []
    if args.skip_level_calibration:
        n_benign = int(np.sum(labels == 0))
        for target in thresholds.SEVERITY_LEVEL_TARGETS:
            level = int(target["level"])
            hostile_target = float(target["hostile_per_million"])
            suspicious_target = float(target["suspicious_per_million"])
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
                        "fn": int(np.sum(labels == 1)),
                        "recall": 0.0,
                        "precision": 0.0,
                        "fp_per_million": 0.0,
                        "skipped": True,
                    },
                    "suspicious": {
                        "target_per_million": suspicious_target,
                        "budget": _budget(n_benign, suspicious_target),
                        "thresholds": {},
                        "diagnostics": {},
                        "tp": 0,
                        "fp": 0,
                        "tn": n_benign,
                        "fn": int(np.sum(labels == 1)),
                        "recall": 0.0,
                        "precision": 0.0,
                        "fp_per_million": 0.0,
                        "skipped": True,
                    },
                },
            )
        LOG.info("skipped fallback level calibration; wrote score table and policy targets only")
    else:
        max_target_per_million = max(
            max(float(target["hostile_per_million"]), float(target["suspicious_per_million"]))
            for target in thresholds.SEVERITY_LEVEL_TARGETS
        )
        prepared = _prepare_calibration(
            labels,
            route_scores,
            max_fp=_budget(int(np.sum(labels == 0)), max_target_per_million),
        )
        for target in thresholds.SEVERITY_LEVEL_TARGETS:
            level = int(target["level"])
            hostile = _calibrate_one(
                labels,
                route_scores,
                target_per_million=float(target["hostile_per_million"]),
                prepared=prepared,
            )
            suspicious = _calibrate_one(
                labels,
                route_scores,
                target_per_million=float(target["suspicious_per_million"]),
                prepared=prepared,
            )
            LOG.info(
                "L%d hostile recall=%.2f%% fp=%d; suspicious recall=%.2f%% fp=%d",
                level,
                hostile["recall"] * 100,
                hostile["fp"],
                suspicious["recall"] * 100,
                suspicious["fp"],
            )
            levels.append({"level": level, "hostile": hostile, "suspicious": suspicious})

    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "schema": "azoth.routed_ensemble.v1",
        "max_id": max_id,
        "calibration_snapshot_id": max_id,
        "score_table": str(args.score_table),
        "score_table_hash": score_table_hash,
        "model_set_hash": model_set_hash,
        "search": {
            "method": "skipped_score_table_only" if args.skip_level_calibration else "coordinate_descent_v1",
            "start": "best_general_only",
            "objective": "maximize_recall_under_routed_fp_budget",
        },
        "rows": int(len(labels)),
        "malware": int(np.sum(labels == 1)),
        "benign": int(np.sum(labels == 0)),
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
    }
    # Atomic write: config.json is consumed by litmus, validate, deploy, etc.
    bundle.atomic_write_json(args.output, payload)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
