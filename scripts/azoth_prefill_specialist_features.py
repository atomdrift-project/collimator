#!/usr/bin/env python3
"""Pre-build the per-route feature cache shared by fold-A / fold-B specialist
training, plus retries.

fold-A and fold-B specialists train on overlapping data — ~88% of rows
appear in both (only the held-out half differs). Today each fold's
``_train_one`` does its own ``extract_partitioned_from_db`` call, so the
overlap gets paid for twice (or worse: under PARALLEL_FOLDS=1 the two
extractions compete for DB / worker resources).

This script extracts the train+dev UNION once per route, then derives
each fold's training matrix by masking. Both matrices are saved to the
feature-cache directory under the cache key
``azoth_calibrate_ensemble._save_route_feature_cache`` already uses, so
``_train_one`` (with --feature-cache-dir set) hits the cache and skips
the per-fold extract entirely.

Discovery follows ``azoth_specialist_suite._targets``: same eligibility
gates (min-bad, min-good, score filters), same litmus-extracted-filetype
exclusion. Routes that don't pass the gates get skipped here too.

Read-only on the corpus side: no model fits, no calibrator changes.

Usage:
  python scripts/azoth_prefill_specialist_features.py \\
      --db $DB --general-dir out/models/azoth/general \\
      --feature-cache-dir out/cache/azoth-route-features
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp

_SCRIPTS = Path(__file__).resolve().parent
_SRC = _SCRIPTS.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from collimator import data, features  # noqa: E402
from azoth_calibrate_ensemble import (  # noqa: E402
    _file_sha256,
    _hash_ints,
    _save_route_feature_cache,
)
from azoth_specialist_suite import (  # noqa: E402
    DEPLOYMENT_GROUPS,
    LITMUS_EXTRACTED_FILETYPES,
    _eligible_filetypes,
    _count_rows,
)

LOG = logging.getLogger("azoth_prefill_specialist_features")


def _placeholder(db_path: Path | str) -> str:
    return "%s" if data._is_pg(db_path) else "?"  # noqa: SLF001


def _fetch_union_rows(
    db_path: Path | str,
    file_types: tuple[str, ...],
    max_id: int,
    min_score: int | None,
) -> list[tuple[int, int, str]]:
    """Return train+dev rows for the route's filetypes WITHOUT applying the
    EXP_OOF_FOLD_EXCLUDE filter. Each row is ``(row_id, label, canonical)``.

    Test rows are dropped — they're not training data for either fold, so
    they don't belong in the train-side cache. The benchmark step (when
    not skipped) does its own test-row extraction.
    """
    where = [
        "label IN ('bad', 'good')",
        "cleave_result IS NOT NULL",
        "skip = ''",
    ]
    params: list[Any] = []
    marker = _placeholder(db_path)
    if max_id > 0:
        where.append(f"id <= {marker}")
        params.append(int(max_id))
    if min_score is not None:
        where.append(f"score >= {marker}")
        params.append(int(min_score))
    select = "SELECT id, sha256, label, canonical_sha256 "
    rows: list[tuple[int, int, str]] = []
    with data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if data._is_pg(db_path):  # noqa: SLF001
            where.append("file_type = ANY(%s)")
            params.append(list(file_types))
            query = select + "FROM samples WHERE " + " AND ".join(where) + " ORDER BY id"
            with conn.cursor() as cur:
                cur.execute(query, params)
                for row_id, sha256, label, canonical in cur:
                    split_key = canonical or sha256
                    if data.is_test_sample(split_key):
                        continue
                    rows.append((
                        int(row_id),
                        1 if str(label) == "bad" else 0,
                        str(split_key),
                    ))
        else:
            placeholders = ",".join("?" for _ in file_types)
            where.append(f"file_type IN ({placeholders})")
            params.extend(file_types)
            query = select + "FROM samples WHERE " + " AND ".join(where) + " ORDER BY id"
            for row_id, sha256, label, canonical in conn.execute(query, params):
                split_key = canonical or sha256
                if data.is_test_sample(split_key):
                    continue
                rows.append((
                    int(row_id),
                    1 if str(label) == "bad" else 0,
                    str(split_key),
                ))
    return rows


def _enumerate_routes(
    db_path: Path | str,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    """Walk the same eligibility gates as azoth_specialist_suite._targets,
    so the pre-fill set is exactly the set of routes the training will
    consume. Filegroups first, then per-filetype.
    """
    groups: list[dict[str, Any]] = []
    for name, file_types in DEPLOYMENT_GROUPS.items():
        counts = _count_rows(
            db_path,
            file_types=file_types,
            max_id=args.max_id,
            min_score=data.MIN_SAMPLE_SCORE,
        )
        if counts["bad"] < args.min_bad or counts["good"] < args.min_good:
            continue
        groups.append({
            "name": name,
            "kind": "filegroup",
            "file_types": tuple(sorted(file_types)),
            "min_score": (
                data.MIN_SAMPLE_SCORE if args.filegroup_score_filter else None
            ),
        })
    filetypes = [
        {
            "name": row["name"],
            "kind": "filetype",
            "file_types": tuple(row["file_types"]),
            "min_score": None,
        }
        for row in _eligible_filetypes(
            db_path,
            max_id=args.max_id,
            min_score=None,
            min_bad=args.min_bad,
            min_good=args.min_good,
        )
    ]
    out = groups + filetypes
    if args.only:
        wanted = set(args.only)
        out = [r for r in out if r["name"] in wanted]
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument(
        "--general-dir",
        type=Path,
        default=Path("out/models/azoth/general"),
        help="Source of feature_spec.json — same spec the suite uses for general_shared.",
    )
    parser.add_argument(
        "--feature-cache-dir",
        type=Path,
        default=Path("out/cache/azoth-route-features"),
        help="Where to write per-fold cached matrices.",
    )
    parser.add_argument("--max-id", type=int, default=0)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--min-bad", type=int, default=300)
    parser.add_argument("--min-good", type=int, default=300)
    parser.add_argument("--filegroup-score-filter", action="store_true")
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help="Repeatable; restrict pre-fill to these route names (filetype or filegroup).",
    )
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.max_id <= 0:
        args.max_id = data.snapshot_max_id(args.db)
    LOG.info("snapshot max_id=%d", args.max_id)
    general_spec_path = args.general_dir / "feature_spec.json"
    general_spec = features.FeatureSpec.load(general_spec_path)
    spec_hash = _file_sha256(general_spec_path)
    LOG.info(
        "general spec: %d features, sha256=%s",
        general_spec.total_features, spec_hash[:16],
    )

    routes = _enumerate_routes(args.db, args)
    LOG.info("pre-filling %d routes", len(routes))

    for route in routes:
        name = route["name"]
        kind = route["kind"]
        route_cache_name = (
            f"filegroups/{name}" if kind == "filegroup" else f"filetypes/{name}"
        )
        LOG.info(
            "%s (%s): fetching union rows for %d file_types",
            name, kind, len(route["file_types"]),
        )
        union_rows = _fetch_union_rows(
            args.db, route["file_types"], args.max_id, route["min_score"],
        )
        if not union_rows:
            LOG.warning("%s: no union rows; skipping", name)
            continue
        LOG.info("%s: %d union rows", name, len(union_rows))

        # Extract once for the union. extract_partitioned_from_db sorts by
        # row_id internally, so we sort here to match — the resulting
        # matrix row at index i corresponds to sorted_union_rows[i].
        union_rows_sorted = sorted(union_rows, key=lambda r: r[0])
        union_ids_labels = [(rid, label) for rid, label, _canon in union_rows_sorted]
        LOG.info("%s: extracting union features", name)
        x_union, y_union, _x_test, _y_test = features.extract_partitioned_from_db(
            args.db,
            union_ids_labels,
            [],  # no benchmark/test rows in the union extract
            general_spec,
            n_workers=args.workers,
        )
        LOG.info(
            "%s: extracted %d rows × %d features (nnz=%d)",
            name, x_union.shape[0], x_union.shape[1], x_union.nnz,
        )

        # For each fold, mask the union matrix to rows NOT in the held-out
        # fold (i.e., what _train_one with EXP_OOF_FOLD_EXCLUDE=fold would
        # have extracted). Save each as the cache file that fold's training
        # will look up.
        union_canonicals = [canon for _rid, _label, canon in union_rows_sorted]
        union_row_ids = np.asarray(
            [rid for rid, _label in union_ids_labels], dtype=np.int64,
        )
        for fold in (0, 1):
            keep_mask = np.asarray([
                data.oof_fold_of(c) != fold for c in union_canonicals
            ], dtype=bool)
            fold_row_ids = union_row_ids[keep_mask]
            fold_matrix = x_union[keep_mask]
            fold_rows_hash = _hash_ints(fold_row_ids)
            _save_route_feature_cache(
                args.feature_cache_dir,
                route_name=route_cache_name,
                max_id=args.max_id,
                spec_hash=spec_hash,
                rows_hash=fold_rows_hash,
                matrix=fold_matrix.tocsr(),
            )
            LOG.info(
                "%s: cached fold-%d matrix (%d rows, rows_hash=%s)",
                name, fold, fold_matrix.shape[0], fold_rows_hash[:16],
            )

    print(f"pre-filled {len(routes)} routes into {args.feature_cache_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
