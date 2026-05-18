#!/usr/bin/env python3
"""cProfile drill into _extract_into to find the hot loop.

Loads N rows from PG, runs features._extract_batch_worker under cProfile,
prints the top time-consumers by cumulative and own time.
"""

from __future__ import annotations

import argparse
import cProfile
import io
import json
import pstats
import random
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import data, features  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--filetype", default="pe")
    parser.add_argument("--n", type=int, default=200)
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path("out/models/azoth/general/feature_spec.json"),
    )
    parser.add_argument("--seed", type=int, default=20260518)
    parser.add_argument(
        "--top", type=int, default=30, help="how many lines of pstats output",
    )
    parser.add_argument("--sort", default="tottime", help="cumtime|tottime|calls")
    args = parser.parse_args()

    with data._connect(args.db) as conn, conn.cursor() as cur:  # noqa: SLF001
        cur.execute(
            "SELECT id FROM samples WHERE file_type = %s AND label IN ('bad','good') "
            "AND cleave_result IS NOT NULL AND skip = '' ORDER BY id",
            (args.filetype,),
        )
        all_ids = [int(r[0]) for r in cur]
    rng = random.Random(args.seed)
    rng.shuffle(all_ids)
    ids = all_ids[: args.n]
    print(f"fetched {len(ids)} ids", file=sys.stderr)

    results = data.fetch_cleave_results(args.db, ids)
    spec = features.FeatureSpec.load(args.spec)

    batch = []
    for rid, item in results.items():
        if item["cleave_result"]:
            batch.append((item, 0))
    print(f"profiling extraction over {len(batch)} rows", file=sys.stderr)

    profiler = cProfile.Profile()
    profiler.enable()
    features._extract_batch_worker((0, batch, spec))  # noqa: SLF001
    profiler.disable()

    out = io.StringIO()
    stats = pstats.Stats(profiler, stream=out).sort_stats(args.sort)
    stats.print_stats(args.top)
    print(out.getvalue())

    # Also print restricted to collimator package
    print("\n=== restricted to collimator/* ===")
    out2 = io.StringIO()
    stats2 = pstats.Stats(profiler, stream=out2).sort_stats(args.sort)
    stats2.print_stats("collimator", args.top)
    print(out2.getvalue())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
