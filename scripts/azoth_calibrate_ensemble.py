#!/usr/bin/env python3
"""Calibrate routed azoth ensemble thresholds against the full corpus."""

from __future__ import annotations

import argparse
import concurrent.futures
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


def _gpd_tail_threshold(
    benign_probs: np.ndarray, target_per_million: float,
) -> tuple[float, dict[str, float]] | None:
    """Generalized Pareto tail extrapolation: estimate the threshold T such
    that ``P(benign_score > T) = target_per_million × 1e-6``.

    Used for observation-only severity-tier derivation. Calibration's
    DEPLOYMENT threshold is decided elsewhere (F-beta on dev); the L0..L9
    tier thresholds reported here are observed quantiles, with this GPD
    extrapolation kicking in when the FP/M target sits below what the
    empirical sample can resolve directly.

    Returns ``(threshold, diagnostics)`` or None if the fit is unreliable
    (insufficient tail data, fit failure, or target loose enough that
    empirical quantiles already work without extrapolation).
    """
    n = len(benign_probs)
    if n < 100:
        # Below 100 benigns there's no usable tail to extrapolate from —
        # any fit would be dominated by sampling noise. Smaller slices
        # should fall back to the empirical floor in callers.
        return None
    sorted_probs = np.sort(benign_probs)
    # Adaptive anchor percentile: fixed 0.99 needs n ≥ 3000 to leave ≥30
    # excesses for a stable fit. For smaller slices, drop the anchor to
    # 0.95 / 0.90 / 0.80 so we still have enough tail mass. The trade-off:
    # lower anchor → more bulk in the fit → less faithful to the true
    # tail shape. The headline-table use case is single-decimal-place
    # recall percentages, so a looser anchor is fine.
    if n >= 3000:
        anchor = 0.99
    elif n >= 1000:
        anchor = 0.95
    elif n >= 300:
        anchor = 0.90
    else:
        anchor = 0.80
    u_idx = int(anchor * n)
    n_tail = n - u_idx
    if n_tail < 20:
        return None
    u = float(sorted_probs[u_idx])
    excesses = sorted_probs[sorted_probs > u] - u
    if len(excesses) < 20:
        return None
    p_above_u = float(len(excesses)) / float(len(sorted_probs))
    p_target = target_per_million / 1_000_000.0
    if p_target <= 0:
        return None
    if p_target >= p_above_u:
        return None
    try:
        import scipy.stats  # noqa: PLC0415
        xi, _, sigma = scipy.stats.genpareto.fit(excesses, floc=0)
    except (ValueError, RuntimeError):
        return None
    if not np.isfinite(xi) or not np.isfinite(sigma) or sigma <= 0:
        return None
    if abs(xi) < 1e-9:
        threshold = u + sigma * np.log(p_above_u / p_target)
    else:
        threshold = u + (sigma / xi) * ((p_target / p_above_u) ** (-xi) - 1.0)
    if not np.isfinite(threshold):
        return None
    # When the GPD fit on a tightly-concentrated benign distribution
    # extrapolates above 1.0, the threshold is unreachable for any
    # calibrated probability score: clipping to 1.0 silently produces a
    # fire-never policy. Returning None instead lets
    # _quantile_severity_threshold fall back to its empirical_floor
    # branch (the max observed benign), which is a real operating point
    # honestly labeled below-resolution rather than a no-op disguised as
    # a threshold. Same for thresholds at or below the GPD anchor u —
    # those indicate a degenerate fit, not a usable answer.
    if threshold >= 1.0 or threshold <= u:
        return None
    return threshold, {
        "u": u,
        "xi": float(xi),
        "sigma": float(sigma),
        "p_above_u": p_above_u,
        "p_target": p_target,
    }


def _quantile_severity_threshold(
    benign_probs: np.ndarray,
    target_per_million: float,
) -> tuple[float | None, str]:
    """Threshold T such that fraction(benign_score > T) ≈ target_per_million × 1e-6.

    Returns ``(threshold, method)`` where method is one of:
      - ``"empirical"``: the (1 − q×10⁻⁶) quantile of benign_probs is well-defined
        (i.e., q*N/1e6 ≥ 1 — at least one benign expected above threshold).
      - ``"extrapolated"``: q is below the empirical floor; threshold derived via
        GPD tail extrapolation.
      - ``"empirical_floor"``: q is below empirical AND GPD fit failed; fall back
        to "above the highest observed benign score."
      - ``"none"``: too few benigns to derive any threshold.

    Threshold is the OBSERVATION at this q rate, not a calibration target.
    L0..L9 tiers in the deployed bundle use this to give litmus a severity
    grading curve derived from data.
    """
    if target_per_million <= 0 or len(benign_probs) < 50:
        return None, "none"
    n = len(benign_probs)
    sorted_probs = np.sort(benign_probs)
    p_target = target_per_million / 1_000_000.0
    n_allowed = int(np.floor(n * p_target))
    if n_allowed >= 1:
        idx = max(0, min(n - n_allowed - 1, n - 1))
        return float(sorted_probs[idx]), "empirical"
    gpd = _gpd_tail_threshold(benign_probs, target_per_million)
    if gpd is not None:
        return gpd[0], "extrapolated"
    return float(sorted_probs[-1]), "empirical_floor"


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


def _enforce_severity_monotonicity(
    level: int,
    hostile: dict[str, Any],
    suspicious: dict[str, Any],
) -> None:
    """Mutate `suspicious['thresholds']` in-place so that, for every route
    present in both severities, suspicious_threshold ≤ hostile_threshold.

    Independent per-severity extrapolation occasionally inverts this on
    noisy slices. Litmus rejects inverted (route, level) pairs entirely
    — silently dropping real recall. We collapse to the stricter
    threshold (i.e. raise suspicious to hostile) when inverted, which
    keeps the route active at the cost of merging the two tiers at that
    operating point for that route.
    """
    h_thresholds = hostile.get("thresholds", {}) or {}
    s_thresholds = suspicious.get("thresholds", {}) or {}
    fixed: list[str] = []
    for route, h_t in h_thresholds.items():
        if h_t is None:
            continue
        s_t = s_thresholds.get(route)
        if s_t is None:
            continue
        if s_t > h_t:
            s_thresholds[route] = h_t
            fixed.append(route)
    if fixed:
        LOG.warning(
            "L%d: %d route(s) had inverted hostile/suspicious thresholds; "
            "clamped suspicious to hostile for: %s",
            level, len(fixed), ", ".join(sorted(fixed)),
        )


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
    extrapolated_routes: list[str] = []

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
        if method == "extrapolated":
            extrapolated_routes.append(name)
        selected[name] = float(threshold)
        hit_local = (probs >= threshold) & valid
        union_hit[indices[hit_local]] = True
        per_route_tp = int(np.sum(hit_local & malware_mask))
        per_route_fp = int(np.sum(hit_local & benign_mask))
        diagnostics[name] = {
            "kind": route.get("kind"),
            "rows": n_route,
            "selected": True,
            "selected_threshold": float(threshold),
            "method": method,
            "standalone": {
                "threshold": float(threshold),
                "tp": per_route_tp,
                "fp": per_route_fp,
            },
        }

    tp = int(np.sum(union_hit & malware))
    fp = int(np.sum(union_hit & benign))
    return {
        "target_per_million": float(target_per_million),
        "below_resolution": bool(below_resolution),
        "cp_floor_per_million": float(cp_floor_per_million),
        "extrapolated_routes": extrapolated_routes,
        "thresholds": selected,
        "diagnostics": diagnostics,
        "tp": tp,
        "fp": fp,
        "tn": n_benign - fp,
        "fn": n_malware - tp,
        "recall": float(tp / n_malware) if n_malware else math.nan,
        "precision": float(tp / max(tp + fp, 1)),
        "fp_per_million": float(fp * 1_000_000.0 / n_benign) if n_benign else math.nan,
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

    # Operational tail anchor: when isotonic's empirical fit doesn't reach
    # high calibrated y at high raw x — because the per-route dev partition
    # had a benign-dominated upper tail — extend the curve linearly toward
    # (1.0, 1.0). Without this, routes whose dev sample lacks confident-
    # malware rows ship calibrators capped well below 1.0 and litmus drops
    # them as "uncalibrated."
    #
    # This is honest: it's an extrapolation, not a measurement, and we
    # mark it in the calibrator's `method` field. The deployed verdict
    # (hostile/suspicious/benign) is driven by the raw-score thresholds
    # found via GPD tail extrapolation in `_calibrate_one`; the calibrator
    # is for human-readable reporting. Anchoring it doesn't add leakage —
    # we use no test rows, and the extension uses no data at all.
    ANCHOR_THRESHOLD_Y = 0.7
    ANCHOR_THRESHOLD_X = 0.999

    calibrators_written = 0
    for entry in route_scores:
        name = entry["name"]
        probs = entry["probs"]
        indices = entry["indices"]
        if probs is None or len(probs) == 0:
            continue
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
        x_thr = iso.X_thresholds_.astype(float)
        y_thr = iso.y_thresholds_.astype(float)
        method = "isotonic"
        emp_x_max = float(x_thr[-1])
        emp_y_max = float(y_thr.max())
        # Anchor when the empirical curve fails to reach (~1, ~1).
        if emp_x_max < ANCHOR_THRESHOLD_X or emp_y_max < ANCHOR_THRESHOLD_Y:
            method = "isotonic+anchor"
            if emp_x_max < ANCHOR_THRESHOLD_X:
                x_thr = np.append(x_thr, 1.0)
                y_thr = np.append(y_thr, 1.0)
            else:
                # x already reaches 1.0; replace the terminal y to 1.0.
                y_thr = y_thr.copy()
                y_thr[-1] = 1.0
        fit_log = (
            f"isotonic on {int(valid.sum())} rows "
            f"({int(y.sum())} malware, {int((y == 0).sum())} benign); "
            f"empirical max x={emp_x_max:.3f} y={emp_y_max:.3f}; "
            f"method={method}, breakpoints={len(x_thr)}"
        )
        if method == "isotonic+anchor":
            LOG.warning("calibrator %s: %s", name, fit_log)
        slot_dir = azoth_root / name
        slot_dir.mkdir(parents=True, exist_ok=True)
        cal_path = slot_dir / "calibrator.json"
        cal = {
            "schema": "azoth.calibrator.isotonic.v1",
            "method": method,
            "x": x_thr.tolist(),
            "y": y_thr.tolist(),
            "out_of_bounds": "clip",
            "n_train": int(valid.sum()),
            "fit_log": fit_log,
        }
        bundle.atomic_write_json(cal_path, cal)
        calibrators_written += 1
    LOG.info("wrote %d per-route calibrators", calibrators_written)


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
    score_jobs = [
        {
            "db_path": args.db,
            "route": route,
            "row_index": row_index,
            "max_id": max_id,
            "workers": args.workers,
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
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.parallelism,
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
            suspicious = _evaluate_thresholds_at_level(
                eval_labels, eval_route_scores,
                thresholds_for_level=prior_level["suspicious"].get("thresholds", {}),
                target_per_million=float(prior_level["suspicious"]["target_per_million"]),
            )
            # Carry through the dev-side resolution flags. These are
            # properties of the threshold-fit data, not of test eval — we
            # propagate them so cards rendered from test_metrics.json can
            # mark "below resolution" rows transparently.
            for sev_dst, sev_src in (
                (hostile, prior_level["hostile"]),
                (suspicious, prior_level["suspicious"]),
            ):
                if "below_resolution" in sev_src:
                    sev_dst["below_resolution"] = bool(sev_src["below_resolution"])
                if "cp_floor_per_million" in sev_src:
                    sev_dst["cp_floor_per_million"] = float(sev_src["cp_floor_per_million"])
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
    # Per-route isotonic calibrators (azoth.calibrator.isotonic.v1).  Litmus
    # loads these next to model.txt at runtime and applies before emitting the
    # per-route probability — closes the gap between reported AUC (post-
    # calibration) and deployed AUC.
    _fit_and_persist_isotonic_calibrator(fit_route_scores, fit_labels, args.azoth_root)
    model_set_hash = _hash_model_set(args.general_scores, route_scores)
    levels: list[dict[str, Any]] = []
    if args.skip_level_calibration:
        n_benign = int(np.sum(fit_labels == 0))
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
                        "fn": int(np.sum(fit_labels == 1)),
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
                        "fn": int(np.sum(fit_labels == 1)),
                        "recall": 0.0,
                        "precision": 0.0,
                        "fp_per_million": 0.0,
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
            suspicious = _calibrate_one(
                fit_labels,
                fit_route_scores,
                target_per_million=float(target["suspicious_per_million"]),
            )
            # Per-route monotonicity guard: hostile must be at least as
            # strict as suspicious (i.e. hostile_threshold ≥ suspicious_threshold).
            # Independent extrapolation per severity occasionally inverts
            # this on noisy slices (e.g. small filetypes where the
            # 3-FP vs 32-FP quantiles wobble). Litmus's classifier
            # `if prob ≥ hostile → Hostile; elif prob ≥ suspicious → Suspicious`
            # would silently swallow such routes — losing real recall.
            # When inverted, raise suspicious to hostile so the two tiers
            # collapse to the stricter operating point for that (route, level).
            _enforce_severity_monotonicity(level, hostile, suspicious)
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
            "method": "skipped_score_table_only" if args.skip_level_calibration else "quantile_severity_v1",
            "objective": "per-route observed (1-q*1e-6) benign-score quantile; GPD tail extrapolation when below empirical floor",
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
    }
    # Atomic write: config.json is consumed by litmus, validate, deploy, etc.
    bundle.atomic_write_json(args.output, payload)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
