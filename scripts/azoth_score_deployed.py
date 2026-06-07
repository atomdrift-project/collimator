#!/usr/bin/env python3
"""Score the currently-deployed model for a route, cached by model identity.

Purpose
-------
Apples-to-apples baseline measurement for autocollie. When autocollie runs a
screen experiment, the candidate's metrics are computed on a small sampled
holdout of *today's* corpus. The natural baseline is "what would the
currently-deployed model score on the same rows?" — but recomputing that for
every screen is wasteful when the deployed model hasn't changed.

This script caches the deployed model's *per-row predictions* on the route's
SHA256-deterministic test partition slice, keyed by the deployed model's
sha256. Once the cache is warm, evaluating metrics on any subset of those
rows (e.g. the row IDs a screen actually held out) is a NumPy index +
arithmetic operation — milliseconds.

When a promote/redeploy changes the deployed model.txt, its sha256 changes
and the cache is naturally invalidated. The next score run repopulates.

CLI
---
::

    azoth_score_deployed.py --route filetypes/pe --db <DSN> \\
        --output /tmp/baseline.json [--row-ids-file /tmp/rows.txt]

When ``--row-ids-file`` is given, metrics are computed on the intersection of
the cache and the supplied row IDs. Without it, metrics are computed on the
full test partition slice — useful for periodic deploy-baseline reports.

Cache location: ``out/cache/autocollie-baseline/<route_slug>/<model_hash[:16]>.npz``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp

# Reach src/ for collimator imports the way scripts/ normally does.
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import bundle, data as collimator_data, features  # noqa: E402

LOG = logging.getLogger("azoth_score_deployed")

DEFAULT_DEPLOY_ROOT = (
    Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
    / "litmus" / "models" / "azoth"
)
DEFAULT_CACHE_ROOT = Path("out/cache/autocollie-baseline")

# Bump when the cache layout changes incompatibly. Mismatching caches are
# invalidated on load and rebuilt from scratch.
CACHE_SCHEMA_VERSION = 2  # v2: labels are live-from-DB, not cached. Sidecar carries max_id.


def _resolve_route_dir(deploy_root: Path, route: str) -> Path:
    """``filetypes/pe`` → ``<deploy_root>/filetypes/pe``;
    ``general`` → ``<deploy_root>/general``."""
    if route == "general":
        return deploy_root / "general"
    if route.startswith(("filetypes/", "filegroups/")):
        return deploy_root / route
    raise SystemExit(f"invalid route name: {route!r}")


def _model_files(route_dir: Path) -> list[Path]:
    """Multi-seed bundles expose ``models/seed_*.txt``; legacy single-model
    bundles have ``model.txt`` at the top. Both supported."""
    multi = sorted((route_dir / "models").glob("seed_*.txt")) if (route_dir / "models").is_dir() else []
    if multi:
        return multi
    legacy = route_dir / "model.txt"
    if legacy.is_file():
        return [legacy]
    return []


def _deployed_model_hash(route_dir: Path) -> str:
    """Combined sha256 of the route's model files. A multi-seed bundle's
    hash includes every seed in deterministic sort order, so retraining
    any seed invalidates the cache."""
    paths = _model_files(route_dir)
    if not paths:
        raise SystemExit(f"no model files under {route_dir}")
    h = hashlib.sha256()
    for path in paths:
        h.update(path.name.encode())
        with open(path, "rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                h.update(chunk)
    return h.hexdigest()


def _route_slug(route: str) -> str:
    return route.replace("/", "_")


def _file_types_for_route(route: str, route_dir: Path, deploy_root: Path) -> list[str]:
    """A filetype route covers exactly one filetype. A filegroup route
    covers whatever filetypes are mapped to it in the deployed config. The
    ``general`` route covers every filetype — too broad for this script;
    callers should pass an explicit list via ``--file-type``."""
    if route.startswith("filetypes/"):
        return [route.split("/", 1)[1]]
    if route.startswith("filegroups/"):
        group = route.split("/", 1)[1]
        config_path = deploy_root / "config.json"
        if not config_path.is_file():
            raise SystemExit(
                f"{config_path} missing; cannot resolve filetypes for {route}"
            )
        with open(config_path) as f:
            config = json.load(f)
        mapping = config.get("filetype_to_group") or {}
        return sorted(ft for ft, g in mapping.items() if g == group)
    if route == "general":
        raise SystemExit(
            "general route covers all filetypes; pass --file-type explicitly",
        )
    raise SystemExit(f"unhandled route: {route}")


def _test_partition_row_ids(
    db_path: str,
    file_types: list[str],
    *,
    min_id_exclusive: int = 0,
) -> list[int]:
    """Test partition row IDs for the given filetypes — non-skip,
    SHA256 bucket < TEST_BUCKET_MAX. When ``min_id_exclusive`` > 0,
    only returns rows with ``id > min_id_exclusive`` (used for
    append-mode cache extension).

    Labels are NOT returned here. They're fetched live at metric time
    via ``_fetch_labels`` so the cache survives label corrections /
    reclassifications without producing stale comparisons.
    """
    is_pg = collimator_data._is_pg(db_path)  # noqa: SLF001
    row_ids: list[int] = []
    with collimator_data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if is_pg:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT id
                    FROM samples
                    WHERE {collimator_data.LABELED_WHERE}
                      AND file_type = ANY(%s)
                      AND id > %s
                      AND canonical_sha256 IS NOT NULL
                      AND length(canonical_sha256) >= 2
                      AND get_byte(decode(right(canonical_sha256, 2), 'hex'), 0) < %s
                    ORDER BY id
                    """,
                    [file_types, int(min_id_exclusive), collimator_data.TEST_BUCKET_MAX],
                )
                for (row_id,) in cur:
                    row_ids.append(int(row_id))
        else:
            placeholders = ",".join("?" for _ in file_types)
            for row_id, csha in conn.execute(
                f"SELECT id, canonical_sha256 FROM samples "  # noqa: S608
                f"WHERE {collimator_data.LABELED_WHERE} "
                f"AND file_type IN ({placeholders}) AND id > ? "
                f"AND canonical_sha256 IS NOT NULL ORDER BY id",
                [*file_types, int(min_id_exclusive)],
            ):
                if not csha or len(csha) < 2:
                    continue
                if collimator_data.is_test_sample(csha):
                    row_ids.append(int(row_id))
    return row_ids


def _fetch_labels(db_path: str, row_ids: np.ndarray) -> np.ndarray:
    """Fetch current labels (1=bad, 0=good) for ``row_ids`` from the DB,
    aligned to input order. Rows whose current label is neither 'bad'
    nor 'good' (relabelled to 'unknown', deleted, etc) get -1, and
    callers should drop them before computing metrics.

    Live-fetching labels closes a drift channel the previous cache
    layout left open: a cache populated months ago might hold a
    'bad' label that has since been corrected to 'good' (or vice
    versa), and the deployed-on-same-data metrics would silently
    score against stale truth. The probs themselves are a function
    of model bytes + row features, both stable, so they're safe to
    cache long-term.
    """
    n = int(row_ids.shape[0])
    if n == 0:
        return np.array([], dtype=np.int8)
    is_pg = collimator_data._is_pg(db_path)  # noqa: SLF001
    label_map: dict[int, int] = {}
    ids_int = [int(x) for x in row_ids.tolist()]
    with collimator_data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if is_pg:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, label FROM samples "
                    "WHERE id = ANY(%s) AND label IN ('bad','good')",
                    [ids_int],
                )
                for row_id, label in cur:
                    label_map[int(row_id)] = 1 if str(label) == "bad" else 0
        else:
            chunk = 5000
            for i in range(0, n, chunk):
                batch = ids_int[i : i + chunk]
                placeholders = ",".join("?" for _ in batch)
                for row_id, label in conn.execute(
                    f"SELECT id, label FROM samples "  # noqa: S608
                    f"WHERE id IN ({placeholders}) AND label IN ('bad','good')",
                    batch,
                ):
                    label_map[int(row_id)] = 1 if str(label) == "bad" else 0
    return np.asarray(
        [label_map.get(int(r), -1) for r in row_ids.tolist()],
        dtype=np.int8,
    )


def _db_max_test_partition_id(db_path: str, file_types: list[str]) -> int:
    """Return ``max(id)`` over test-partition rows for ``file_types``,
    or 0 if no rows match. Used to detect DB rollbacks (replica rebuild
    that restored an older snapshot, table truncate-and-restore, etc.):
    if the DB's current max is *less than* the sidecar's
    ``max_id_at_populate``, the cache references rows that no longer
    exist, and append-mode can't fix it — we must invalidate.

    Normally we'd retrain after such a reset (which would change the
    model hash and invalidate the cache anyway), but the check is
    near-free and turns a silent stale-cache failure into an obvious
    log line.
    """
    is_pg = collimator_data._is_pg(db_path)  # noqa: SLF001
    with collimator_data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if is_pg:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT max(id) FROM samples "
                    "WHERE label IN ('bad','good') AND file_type = ANY(%s)",
                    [file_types],
                )
                row = cur.fetchone()
                return int(row[0]) if row and row[0] is not None else 0
        placeholders = ",".join("?" for _ in file_types)
        row = conn.execute(
            f"SELECT max(id) FROM samples WHERE label IN ('bad','good') "  # noqa: S608
            f"AND file_type IN ({placeholders})",
            file_types,
        ).fetchone()
        return int(row[0]) if row and row[0] is not None else 0


def _sidecar_path(cache_path: Path) -> Path:
    return cache_path.with_suffix(".json")


def _load_sidecar(sidecar_path: Path) -> dict | None:
    if not sidecar_path.is_file():
        return None
    try:
        return json.loads(sidecar_path.read_text())
    except (OSError, ValueError):
        return None


def _save_sidecar(sidecar_path: Path, data: dict) -> None:
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = sidecar_path.parent / (sidecar_path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True))
    tmp.rename(sidecar_path)


def _save_cache(cache_path: Path, row_ids: np.ndarray, probs: np.ndarray) -> None:
    """Atomic write of a v2 cache file: (row_ids, probs) only — labels
    are pulled live at metric time. ``np.savez`` auto-appends '.npz'
    to string/path arguments, so write to a file handle to force the
    exact tmp filename, then rename onto the final path.
    """
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = cache_path.parent / (cache_path.name + ".tmp")
    with open(tmp, "wb") as f:
        np.savez(f, row_ids=row_ids, probs=probs)
    tmp.rename(cache_path)


def _strip_nan(value):
    """Recursively replace non-finite floats with None so the output is
    standards-compliant JSON. Mirrors the helper used in other azoth
    scripts (azoth_specialist_suite, compute_routed_metrics) — same
    rationale: Go's strict JSON parser rejects literal NaN/Infinity.
    """
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, dict):
        return {k: _strip_nan(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_strip_nan(v) for v in value]
    return value


def _is_v2_cache(npz: np.lib.npyio.NpzFile) -> bool:
    """v1 caches carry a 'labels' array; v2 does not. Used to detect
    old-schema caches and force a fresh populate."""
    return "labels" not in npz.files


def _extract_and_predict(
    *,
    route_dir: Path,
    db_path: str,
    row_ids: list[int],
    workers: int,
) -> np.ndarray:
    """Feature-extract + predict for a list of row IDs. Labels are
    not relevant here (predictions are label-independent); we pass
    dummy zeros to ``extract_labeled_from_db_batches`` and discard the
    label array."""
    if not row_ids:
        return np.array([], dtype=np.float32)
    spec_path = route_dir / "feature_spec.json"
    if not spec_path.is_file():
        raise SystemExit(f"{spec_path} missing; cannot score deployed model")
    spec = features.FeatureSpec.load(spec_path)
    clf = bundle.Ensemble.load_bundle(route_dir)
    rows_with_dummy_labels = [(rid, 0) for rid in row_ids]
    t0 = time.perf_counter()
    batches = list(features.extract_labeled_from_db_batches(
        db_path, rows_with_dummy_labels, spec, n_workers=workers,
    ))
    if batches:
        x_matrix = sp.vstack([batch[0] for batch in batches], format="csr")
    else:
        x_matrix = sp.csr_matrix((0, spec.total_features), dtype=np.float32)
    LOG.info("  feature extract %.1fs (nnz=%d)", time.perf_counter() - t0, x_matrix.nnz)
    t0 = time.perf_counter()
    probs = clf.predict_proba(x_matrix).astype(np.float32)
    LOG.info("  predict %.1fs", time.perf_counter() - t0)
    return probs


def _populate_cache(
    *,
    route_dir: Path,
    db_path: str,
    file_types: list[str],
    workers: int,
    cache_path: Path,
    model_hash: str,
) -> dict:
    """Full populate: extract+predict every test-partition row for the
    route, write a fresh v2 cache and sidecar. Returns the sidecar
    dict the caller should persist. One-time cost per deployed model
    identity per route; subsequent calls reuse via ``_extend_cache``."""
    LOG.info("populating cache for %s (filetypes=%s)", route_dir, file_types)
    t0 = time.perf_counter()
    row_ids_list = _test_partition_row_ids(db_path, file_types)
    LOG.info("  %d test-partition rows fetched in %.1fs", len(row_ids_list), time.perf_counter() - t0)
    if not row_ids_list:
        raise SystemExit(f"no test-partition rows for filetypes={file_types}")

    probs = _extract_and_predict(
        route_dir=route_dir, db_path=db_path,
        row_ids=row_ids_list, workers=workers,
    )
    row_ids = np.asarray(row_ids_list, dtype=np.int64)
    _save_cache(cache_path, row_ids, probs)
    sidecar = {
        "schema_version": CACHE_SCHEMA_VERSION,
        "model_hash": model_hash,
        "file_types": sorted(file_types),
        "max_id_at_populate": int(row_ids.max()) if len(row_ids) else 0,
        "n_rows": int(len(row_ids)),
        "populated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _save_sidecar(_sidecar_path(cache_path), sidecar)
    LOG.info("  cached %d predictions → %s", len(row_ids), cache_path)
    return sidecar


def _extend_cache(
    *,
    cache_path: Path,
    route_dir: Path,
    db_path: str,
    file_types: list[str],
    workers: int,
    sidecar: dict,
) -> dict:
    """Append-mode update: query the DB for test-partition rows added
    since ``sidecar.max_id_at_populate``, extract+predict only those,
    concatenate onto the existing cache, atomic-rewrite. Returns the
    updated sidecar (caller persists)."""
    max_id = int(sidecar.get("max_id_at_populate", 0))
    t0 = time.perf_counter()
    new_row_ids_list = _test_partition_row_ids(
        db_path, file_types, min_id_exclusive=max_id,
    )
    LOG.info(
        "  cache extend: %d new test-partition rows since id=%d (%.1fs)",
        len(new_row_ids_list), max_id, time.perf_counter() - t0,
    )
    if not new_row_ids_list:
        return sidecar
    new_probs = _extract_and_predict(
        route_dir=route_dir, db_path=db_path,
        row_ids=new_row_ids_list, workers=workers,
    )
    with np.load(cache_path) as cached:
        existing_row_ids = np.asarray(cached["row_ids"], dtype=np.int64)
        existing_probs = np.asarray(cached["probs"], dtype=np.float32)
    new_row_ids = np.asarray(new_row_ids_list, dtype=np.int64)
    # Defensive: drop any new_row_ids already present in the cache.
    # Shouldn't happen given the id > max_id filter, but DB ID reuse or
    # races aren't impossible.
    if existing_row_ids.size:
        mask = ~np.isin(new_row_ids, existing_row_ids)
        if not mask.all():
            LOG.warning(
                "  cache extend: dropped %d row IDs already in cache (DB ID reuse?)",
                int((~mask).sum()),
            )
            new_row_ids = new_row_ids[mask]
            new_probs = new_probs[mask]
    if new_row_ids.size == 0:
        return sidecar
    combined_row_ids = np.concatenate([existing_row_ids, new_row_ids])
    combined_probs = np.concatenate([existing_probs, new_probs])
    _save_cache(cache_path, combined_row_ids, combined_probs)
    sidecar = {**sidecar}
    sidecar["max_id_at_populate"] = int(combined_row_ids.max())
    sidecar["n_rows"] = int(len(combined_row_ids))
    sidecar["last_extended_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _save_sidecar(_sidecar_path(cache_path), sidecar)
    return sidecar


def _metrics(
    row_ids: np.ndarray,
    probs: np.ndarray,
    *,
    db_path: str,
    subset_ids: np.ndarray | None,
) -> dict[str, Any]:
    """Compute PR AUC, ROC AUC, F1, and recall at FP/M targets on the
    rows that survive the (cache ∩ subset) intersection. Labels are
    fetched LIVE from the DB for that intersection so the metric uses
    current truth, not a snapshot from cache-populate time.

    Rows whose current DB label is neither 'bad' nor 'good' (relabelled
    to unknown, deleted, etc) get -1 from ``_fetch_labels`` and are
    dropped here so they don't pollute the metric.
    """
    if subset_ids is not None and subset_ids.size:
        keep = np.isin(row_ids, subset_ids)
        row_ids = row_ids[keep]
        probs = probs[keep]
    labels = _fetch_labels(db_path, row_ids)
    valid = labels >= 0
    if not valid.all():
        n_dropped = int((~valid).sum())
        if n_dropped:
            LOG.info("  dropped %d rows with non-{bad,good} current labels", n_dropped)
        row_ids = row_ids[valid]
        labels = labels[valid]
        probs = probs[valid]
    n = len(labels)
    n_mal = int(np.sum(labels == 1))
    n_ben = int(np.sum(labels == 0))
    out: dict[str, Any] = {
        "n_rows": n,
        "n_malware": n_mal,
        "n_benign": n_ben,
        "model_hash_used": None,  # set by caller
    }
    if n_mal == 0 or n_ben == 0:
        return out
    from sklearn.metrics import (  # noqa: PLC0415
        average_precision_score, roc_auc_score, f1_score,
        precision_recall_curve,
    )
    out["avg_precision"] = float(average_precision_score(labels, probs))
    out["roc_auc"] = float(roc_auc_score(labels, probs))
    # Max-F1 via PR-curve sweep (matches azoth_specialist_suite convention).
    precision, recall, thresholds = precision_recall_curve(labels, probs)
    f1_vals = np.divide(
        2.0 * precision * recall, precision + recall,
        out=np.zeros_like(precision), where=(precision + recall) > 0,
    )
    best = int(np.argmax(f1_vals))
    thr = 1.0 if best >= len(thresholds) else float(thresholds[best])
    out["max_f1"] = float(f1_score(labels, (probs >= thr).astype(int), zero_division=0))
    # recall_at_X_per_100M — sweep predictions to find tightest threshold
    # catching <= X benigns-per-100M in the slice. Per-100M is the deployed
    # scale; 50 maps to the L50 default operating point.
    order = np.argsort(-probs, kind="mergesort")
    sorted_y = labels[order]
    fp_cum = np.cumsum(sorted_y == 0)
    tp_cum = np.cumsum(sorted_y == 1)
    for fp100m in (0, 50, 100, 300, 500, 900):
        budget = max(1, int(np.floor(n_ben * fp100m / 100_000_000.0))) if fp100m > 0 else 0
        best_rec: float | None = None
        for i in range(len(sorted_y)):
            if fp_cum[i] > budget:
                break
            best_rec = float(tp_cum[i] / n_mal)
        out[f"recall_at_{fp100m}_per_100M"] = best_rec if best_rec is not None else math.nan
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--route", required=True, help="general | filetypes/<X> | filegroups/<X>")
    p.add_argument("--db", default=os.environ.get("DB", ""))
    p.add_argument(
        "--deploy-root", type=Path, default=DEFAULT_DEPLOY_ROOT,
        help="Root of the deployed bundle (default: litmus's deploy dir)",
    )
    p.add_argument(
        "--cache-root", type=Path, default=DEFAULT_CACHE_ROOT,
        help="Where to store cached predictions (default: out/cache/autocollie-baseline)",
    )
    p.add_argument(
        "--row-ids-file", type=Path, default=None,
        help="Optional newline-delimited file of row IDs to restrict metrics to. "
             "When omitted, metrics are computed on the full cached test slice.",
    )
    p.add_argument("--file-type", action="append", default=[],
                   help="Override file types (repeatable). Required for --route general.")
    p.add_argument("--workers", type=int, default=0,
                   help="Feature extraction workers (0 = auto).")
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--log-level", default="INFO")
    args = p.parse_args()
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")

    if not args.db:
        raise SystemExit("--db required (or set DB env)")

    route_dir = _resolve_route_dir(args.deploy_root, args.route)
    if not route_dir.is_dir():
        raise SystemExit(f"deployed route dir not found: {route_dir}")

    file_types = args.file_type or _file_types_for_route(
        args.route, route_dir, args.deploy_root,
    )

    # A route with no specialist model — suite-skipped raw-compressed filetypes
    # (zst/gz/xz/tar) or any route that fell below the min-bad/min-good floor —
    # is served by the GENERAL model at inference, so baseline its rows against
    # general rather than dying with "no model files". This gives autocollie a
    # real apples-to-apples baseline (what the deployed ensemble actually scores
    # these rows) instead of an exit-2 that drops it to the weaker legacy
    # promoted_baselines comparison. file_types stays the route's own — we score
    # the route's rows, just through the general model.
    model_dir = route_dir
    if not _model_files(route_dir):
        general_dir = args.deploy_root / "general"
        if not _model_files(general_dir):
            raise SystemExit(
                f"no model files under {route_dir} and no general fallback at {general_dir}"
            )
        LOG.info(
            "route %s has no specialist model; baselining its rows against general",
            args.route,
        )
        model_dir = general_dir

    model_hash = _deployed_model_hash(model_dir)
    cache_path = args.cache_root / _route_slug(args.route) / f"{model_hash[:16]}.npz"
    sidecar_path = _sidecar_path(cache_path)

    # Cache state machine, in order of preference:
    #   1. v2 cache + sidecar present → check sidecar.max_id_at_populate
    #      against the DB. If new rows exist, append-extract them
    #      (cheap, O(delta)); otherwise reuse as-is.
    #   2. v1 cache present (labels stored, no sidecar) → invalidate.
    #      The drift channels v2 closes (label drift, repin staleness)
    #      are exactly why we don't trust v1 long-term.
    #   3. No cache → full populate.
    sidecar = _load_sidecar(sidecar_path) if cache_path.is_file() else None
    needs_full_populate = False
    if cache_path.is_file():
        with np.load(cache_path) as cached_check:
            cache_is_v2 = _is_v2_cache(cached_check)
        schema = (sidecar or {}).get("schema_version")
        if not cache_is_v2 or sidecar is None or schema != CACHE_SCHEMA_VERSION:
            LOG.info(
                "cache at %s is pre-v%d schema (v2=%s, sidecar=%s, schema=%s); "
                "invalidating and repopulating",
                cache_path, CACHE_SCHEMA_VERSION, cache_is_v2,
                "present" if sidecar else "missing", schema,
            )
            cache_path.unlink(missing_ok=True)
            sidecar_path.unlink(missing_ok=True)
            needs_full_populate = True
        else:
            # Rollback guard: if the DB's current max(id) is *below*
            # the sidecar's max_id_at_populate, the DB has gone
            # backward (replica rebuild from an older snapshot, table
            # truncate-and-restore, full DB reset). Append-mode is
            # unsalvageable in that case — extracting id >
            # max_id_at_populate yields nothing, but the cache still
            # references row IDs that may no longer exist or now
            # belong to different content. Invalidate and repopulate.
            db_max = _db_max_test_partition_id(args.db, file_types)
            sidecar_max = int(sidecar.get("max_id_at_populate", 0))
            if db_max < sidecar_max:
                LOG.warning(
                    "DB max(id)=%d < sidecar max_id_at_populate=%d for "
                    "%s: DB appears to have rolled back. Invalidating "
                    "cache and repopulating from scratch.",
                    db_max, sidecar_max, args.route,
                )
                cache_path.unlink(missing_ok=True)
                sidecar_path.unlink(missing_ok=True)
                needs_full_populate = True
    else:
        needs_full_populate = True

    if needs_full_populate:
        LOG.info("cache miss: %s", cache_path)
        sidecar = _populate_cache(
            route_dir=model_dir,
            db_path=args.db,
            file_types=file_types,
            workers=args.workers,
            cache_path=cache_path,
            model_hash=model_hash,
        )
    else:
        LOG.info(
            "cache hit: %s (max_id=%d, n_rows=%d)",
            cache_path,
            int(sidecar.get("max_id_at_populate", 0)),
            int(sidecar.get("n_rows", 0)),
        )
        sidecar = _extend_cache(
            cache_path=cache_path,
            route_dir=model_dir,
            db_path=args.db,
            file_types=file_types,
            workers=args.workers,
            sidecar=sidecar,
        )

    with np.load(cache_path) as cached:
        row_ids = np.asarray(cached["row_ids"], dtype=np.int64)
        probs = np.asarray(cached["probs"], dtype=np.float32)

    subset_ids: np.ndarray | None = None
    if args.row_ids_file is not None:
        raw = args.row_ids_file.read_text().split()
        subset_ids = np.asarray([int(x) for x in raw if x.strip()], dtype=np.int64)

    # Populate-on-miss: when the caller passes a subset of row IDs that
    # don't all overlap with the cache's coverage (which only stores
    # test-partition rows for this route), score the missing rows on
    # demand and merge them into the cache. Without this, autocollie's
    # apples-to-apples scoring silently returned n_rows=0 whenever the
    # candidate's holdout rows (its internal screen-time split) fell
    # outside the deployed model's test-partition population — which
    # is the common case, since the candidate's holdout is drawn from
    # its own training pool, not from the deployed test bucket. The
    # screen gate would then fall back to legacy promoted_baselines
    # comparison without telling anyone the apples-to-apples evidence
    # was missing.
    if subset_ids is not None and subset_ids.size:
        cache_set = set(int(x) for x in row_ids.tolist())
        missing = [int(x) for x in subset_ids.tolist() if int(x) not in cache_set]
        if missing:
            LOG.info(
                "subset has %d row IDs not in cache; scoring on-demand and "
                "extending cache (cache had %d rows)",
                len(missing), int(row_ids.size),
            )
            new_probs = _extract_and_predict(
                route_dir=model_dir, db_path=args.db,
                row_ids=missing, workers=args.workers,
            )
            new_row_ids = np.asarray(missing, dtype=np.int64)
            row_ids = np.concatenate([row_ids, new_row_ids])
            probs = np.concatenate([probs, new_probs])
            _save_cache(cache_path, row_ids, probs)
            sidecar = {**(sidecar or {})}
            sidecar["max_id_at_populate"] = int(row_ids.max())
            sidecar["n_rows"] = int(row_ids.size)
            sidecar["last_extended_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            _save_sidecar(sidecar_path, sidecar)

    metrics = _metrics(row_ids, probs, db_path=args.db, subset_ids=subset_ids)
    metrics["model_hash_used"] = model_hash
    metrics["route"] = args.route
    metrics["cache_path"] = str(cache_path)
    metrics["cache_max_id_at_populate"] = int(sidecar.get("max_id_at_populate", 0))
    metrics["cache_n_rows"] = int(sidecar.get("n_rows", 0))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Strip non-finite floats (NaN, ±inf) before serializing — Python's
    # json.dumps emits them as literal NaN/Infinity tokens which aren't
    # valid JSON and break Go's strict parser on the autocollie side.
    # The script emits math.nan from _metrics() for recall_at_X_per_100M
    # when there are no eligible scores; replace those with None (=> JSON
    # null) so the consumer can detect-and-skip without parse failures.
    # Also pass allow_nan=False so any non-finite we missed crashes here
    # loudly rather than producing invalid JSON.
    args.output.write_text(
        json.dumps(_strip_nan(metrics), indent=2, default=str, allow_nan=False)
    )
    LOG.info("wrote %s", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
