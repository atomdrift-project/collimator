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


def _test_partition_rows(db_path: str, file_types: list[str]) -> list[tuple[int, int]]:
    """Test partition rows for the given filetypes — labeled, non-skip,
    SHA256 bucket < TEST_BUCKET_MAX. Returns [(row_id, label_int), ...]."""
    is_pg = collimator_data._is_pg(db_path)  # noqa: SLF001
    rows: list[tuple[int, int]] = []
    with collimator_data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if is_pg:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, label
                    FROM samples
                    WHERE label IN ('bad', 'good')
                      AND cleave_result IS NOT NULL
                      AND skip = ''
                      AND file_type = ANY(%s)
                      AND canonical_sha256 IS NOT NULL
                      AND length(canonical_sha256) >= 2
                      AND get_byte(decode(right(canonical_sha256, 2), 'hex'), 0) < %s
                    ORDER BY id
                    """,
                    [file_types, collimator_data.TEST_BUCKET_MAX],
                )
                for row_id, label in cur:
                    rows.append((int(row_id), 1 if str(label) == "bad" else 0))
        else:
            placeholders = ",".join("?" for _ in file_types)
            for row_id, label, csha in conn.execute(
                f"SELECT id, label, canonical_sha256 FROM samples "  # noqa: S608
                f"WHERE label IN ('bad','good') AND cleave_result IS NOT NULL "
                f"AND skip = '' AND file_type IN ({placeholders}) "
                f"AND canonical_sha256 IS NOT NULL ORDER BY id",
                file_types,
            ):
                if not csha or len(csha) < 2:
                    continue
                if collimator_data.is_test_sample(csha):
                    rows.append((int(row_id), 1 if str(label) == "bad" else 0))
    return rows


def _populate_cache(
    *,
    route_dir: Path,
    db_path: str,
    file_types: list[str],
    workers: int,
    cache_path: Path,
) -> None:
    """Extract test-partition features for the route, score with the
    deployed model, write predictions to the cache file. One-time cost
    per deployed model identity per route."""
    spec_path = route_dir / "feature_spec.json"
    if not spec_path.is_file():
        raise SystemExit(f"{spec_path} missing; cannot score deployed model")
    spec = features.FeatureSpec.load(spec_path)
    clf = bundle.Ensemble.load_bundle(route_dir)

    LOG.info("populating cache for %s (filetypes=%s)", route_dir, file_types)
    t0 = time.perf_counter()
    rows = _test_partition_rows(db_path, file_types)
    LOG.info("  %d test-partition rows fetched in %.1fs", len(rows), time.perf_counter() - t0)
    if not rows:
        raise SystemExit(f"no test-partition rows for filetypes={file_types}")

    t0 = time.perf_counter()
    batches = list(features.extract_labeled_from_db_batches(
        db_path, rows, spec, n_workers=workers,
    ))
    if batches:
        x_matrix = sp.vstack([batch[0] for batch in batches], format="csr")
    else:
        x_matrix = sp.csr_matrix((0, spec.total_features), dtype=np.float32)
    LOG.info("  feature extract %.1fs (nnz=%d)", time.perf_counter() - t0, x_matrix.nnz)

    t0 = time.perf_counter()
    probs = clf.predict_proba(x_matrix).astype(np.float32)
    LOG.info("  predict %.1fs", time.perf_counter() - t0)

    row_ids = np.asarray([rid for rid, _ in rows], dtype=np.int64)
    labels = np.asarray([lbl for _, lbl in rows], dtype=np.int8)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    # np.savez auto-appends '.npz' to string/path arguments, which mangles
    # our '<x>.npz.tmp' rename pattern. Open a file handle to force the
    # exact filename, then atomic-rename onto the final cache path.
    tmp = cache_path.parent / (cache_path.name + ".tmp")
    with open(tmp, "wb") as f:
        np.savez(f, row_ids=row_ids, labels=labels, probs=probs)
    tmp.rename(cache_path)
    LOG.info("  cached %d predictions → %s", len(row_ids), cache_path)


def _metrics(
    row_ids: np.ndarray,
    labels: np.ndarray,
    probs: np.ndarray,
    *,
    subset_ids: np.ndarray | None,
) -> dict[str, Any]:
    """Compute PR AUC, ROC AUC, F1, and recall at FP/M targets. When
    ``subset_ids`` is given, restrict to rows present in both the cache
    and the subset."""
    if subset_ids is not None and subset_ids.size:
        keep = np.isin(row_ids, subset_ids)
        row_ids = row_ids[keep]
        labels = labels[keep]
        probs = probs[keep]
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
    # recall_at_fp_per_million_X — sweep predictions to find tightest
    # threshold catching <= X benigns-per-million in the slice.
    order = np.argsort(-probs, kind="mergesort")
    sorted_y = labels[order]
    fp_cum = np.cumsum(sorted_y == 0)
    tp_cum = np.cumsum(sorted_y == 1)
    for fpm in (0, 1, 3, 5, 9):
        budget = max(1, int(np.floor(n_ben * fpm / 1_000_000.0))) if fpm > 0 else 0
        best_rec: float | None = None
        for i in range(len(sorted_y)):
            if fp_cum[i] > budget:
                break
            best_rec = float(tp_cum[i] / n_mal)
        out[f"recall_at_fp_per_million_{fpm}"] = best_rec if best_rec is not None else math.nan
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

    model_hash = _deployed_model_hash(route_dir)
    cache_path = args.cache_root / _route_slug(args.route) / f"{model_hash[:16]}.npz"

    if cache_path.is_file():
        LOG.info("cache hit: %s", cache_path)
    else:
        LOG.info("cache miss: %s", cache_path)
        file_types = args.file_type or _file_types_for_route(
            args.route, route_dir, args.deploy_root,
        )
        _populate_cache(
            route_dir=route_dir,
            db_path=args.db,
            file_types=file_types,
            workers=args.workers,
            cache_path=cache_path,
        )

    cached = np.load(cache_path)
    row_ids = cached["row_ids"]
    labels = cached["labels"]
    probs = cached["probs"]

    subset_ids: np.ndarray | None = None
    if args.row_ids_file is not None:
        raw = args.row_ids_file.read_text().split()
        subset_ids = np.asarray([int(x) for x in raw if x.strip()], dtype=np.int64)

    metrics = _metrics(row_ids, labels, probs, subset_ids=subset_ids)
    metrics["model_hash_used"] = model_hash
    metrics["route"] = args.route
    metrics["cache_path"] = str(cache_path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2, default=str))
    LOG.info("wrote %s", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
