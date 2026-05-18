#!/usr/bin/env python3
"""In-process cProfile of one specialist route, single-worker, to find
non-extraction hot spots without needing ptrace permissions.

Runs the same path as azoth_specialist_suite._train_one but inline, so
cProfile sees everything (extraction + LightGBM training).
"""

from __future__ import annotations

import argparse
import cProfile
import io
import pstats
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / "src"
_SCRIPTS = Path(__file__).resolve().parent
for p in (str(_SRC), str(_SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

from collimator import data, features  # noqa: E402
from collimator.train import TrainConfig, train_model  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--filetype", default="pe")
    parser.add_argument("--n-train", type=int, default=50000)
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path("out/models/azoth/general/feature_spec.json"),
    )
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--top", type=int, default=40)
    args = parser.parse_args()

    spec = features.FeatureSpec.load(args.spec)

    # Fetch ~n-train row ids for the filetype.
    with data._connect(args.db) as conn, conn.cursor() as cur:  # noqa: SLF001
        cur.execute(
            "SELECT id, sha256, canonical_sha256, label FROM samples "
            "WHERE file_type = %s AND label IN ('bad','good') AND cleave_result IS NOT NULL "
            "AND skip = '' AND score >= 3 ORDER BY id LIMIT %s",
            (args.filetype, args.n_train),
        )
        rows = []
        for rid, sha, canon, label in cur:
            rows.append((int(rid), 1 if label == "bad" else 0))
    print(f"loaded {len(rows)} {args.filetype} rows", file=sys.stderr)

    pr = cProfile.Profile()
    pr.enable()

    print("[phase] extracting features...", file=sys.stderr)
    x, y, x_test, y_test = features.extract_partitioned_from_db(
        args.db, rows, [], spec, n_workers=args.workers,
    )
    print(f"  -> X shape: {x.shape}, nnz={x.nnz}", file=sys.stderr)

    print("[phase] training LightGBM...", file=sys.stderr)
    cfg = TrainConfig(
        seed=42, n_estimators=400, max_depth=12, learning_rate=0.05,
        early_stopping_rounds=50, num_leaves=96, min_child_samples=100,
    )
    train_model(cfg, x, y, x, y)  # no holdout; same as benchmark-skip

    pr.disable()
    out = io.StringIO()
    pstats.Stats(pr, stream=out).sort_stats("tottime").print_stats(args.top)
    print(out.getvalue())
    print("\n=== restricted to collimator/* ===")
    out2 = io.StringIO()
    pstats.Stats(pr, stream=out2).sort_stats("tottime").print_stats("collimator", args.top)
    print(out2.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
