#!/usr/bin/env python3
"""Profile the three phases of feature extraction to identify the bottleneck.

We want to know: of the wall-clock time per row in the extraction
pipeline, what fraction is spent in (a) DB fetch, (b) JSON decode, and
(c) feature extraction? If (a) is small, swapping PG for a sidecar
cache is a poor lever.

Methodology:
  1. Sample N random row ids from a representative filetype.
  2. Run each phase in isolation with realistic batch sizes:
     - DB fetch:      data.fetch_cleave_results(...)
     - JSON decode:   json.loads on each cleave_result
     - Feature extract: features._extract_into per row
  3. Report wall ms total and per-row μs for each phase.
  4. Repeat under multiple parallel-worker counts so contention is
     measured, not just single-stream.

This is intentionally NOT a comprehensive benchmark. The goal is to
pick a side: I/O-bound (cache helps a lot) vs CPU-bound (cache helps
little, focus on parse/extract).
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import random
import sys
import time
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import data, features  # noqa: E402


def _sample_ids(db: str, filetype: str, n: int, seed: int) -> list[int]:
    with data._connect(db) as conn, conn.cursor() as cur:  # noqa: SLF001
        cur.execute(
            "SELECT id FROM samples WHERE file_type = %s AND label IN ('bad','good') "
            "AND cleave_result IS NOT NULL AND skip = '' ORDER BY id",
            (filetype,),
        )
        all_ids = [int(r[0]) for r in cur]
    rng = random.Random(seed)
    rng.shuffle(all_ids)
    return all_ids[:n]


def _phase_fetch(db: str, ids: list[int], batch_size: int) -> tuple[float, dict[int, dict]]:
    """Return (wall_seconds, merged_results)."""
    t0 = time.perf_counter()
    out: dict[int, dict] = {}
    for i in range(0, len(ids), batch_size):
        batch = ids[i : i + batch_size]
        out.update(data.fetch_cleave_results(db, batch))
    return time.perf_counter() - t0, out


def _phase_json(results: dict[int, dict]) -> tuple[float, dict[int, dict]]:
    t0 = time.perf_counter()
    parsed: dict[int, dict] = {}
    for rid, item in results.items():
        raw = item["cleave_result"]
        if isinstance(raw, str):
            try:
                parsed[rid] = json.loads(raw)
            except json.JSONDecodeError:
                continue
        else:
            parsed[rid] = raw
    return time.perf_counter() - t0, parsed


def _phase_extract(
    parsed: dict[int, dict],
    spec_path: Path,
) -> tuple[float, int]:
    spec = features.FeatureSpec.load(spec_path)
    rows = [({"cleave_result": json.dumps(p), "formula": "", "elements": "", "score": 0, "mtime": "", "cluster_id": -1}, 0) for p in parsed.values()]
    t0 = time.perf_counter()
    r, c, v, lbls = features._extract_batch_worker((0, rows, spec))  # noqa: SLF001
    return time.perf_counter() - t0, len(r)


def _worker(args) -> dict:
    """Run all three phases in a child process so we can measure contention."""
    db, ids, batch_size, spec_path = args
    fetch_s, results = _phase_fetch(db, ids, batch_size)
    json_s, parsed = _phase_json(results)
    extract_s, nnz = _phase_extract(parsed, spec_path)
    return {
        "fetch_s": fetch_s,
        "json_s": json_s,
        "extract_s": extract_s,
        "rows": len(parsed),
        "nnz": nnz,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--filetype", default="pe")
    parser.add_argument("--n", type=int, default=2000, help="row count per worker")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=200,
        help="rows per fetch_cleave_results call",
    )
    parser.add_argument(
        "--workers",
        type=int,
        nargs="+",
        default=[1, 4, 16, 32],
        help="parallel worker counts to measure",
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path("out/models/azoth/general/feature_spec.json"),
    )
    parser.add_argument("--seed", type=int, default=20260518)
    args = parser.parse_args()

    if not args.spec.is_file():
        print(f"spec not found: {args.spec}", file=sys.stderr)
        return 2

    print(f"sampling {args.n * max(args.workers)} ids of file_type={args.filetype}")
    ids = _sample_ids(args.db, args.filetype, args.n * max(args.workers), args.seed)
    if len(ids) < args.n:
        print(f"only {len(ids)} ids available for {args.filetype}", file=sys.stderr)
        return 3
    print(f"got {len(ids)} ids")

    for w in args.workers:
        # Each worker gets disjoint slice of ids.
        chunks = [ids[i * args.n : (i + 1) * args.n] for i in range(w)]
        chunks = [c for c in chunks if c]
        worker_args = [(args.db, c, args.batch_size, args.spec) for c in chunks]
        t0 = time.perf_counter()
        with mp.get_context("spawn").Pool(processes=w) as pool:
            results = pool.map(_worker, worker_args)
        wall = time.perf_counter() - t0
        total_rows = sum(r["rows"] for r in results)
        fetch_total = sum(r["fetch_s"] for r in results)
        json_total = sum(r["json_s"] for r in results)
        extract_total = sum(r["extract_s"] for r in results)
        cpu_total = fetch_total + json_total + extract_total
        per_row_fetch_us = 1e6 * fetch_total / total_rows
        per_row_json_us = 1e6 * json_total / total_rows
        per_row_extract_us = 1e6 * extract_total / total_rows
        print(
            f"\n[workers={w}] wall={wall:6.2f}s  rows={total_rows}  rows/sec={total_rows/wall:7.1f}",
        )
        print(
            f"  per-row (μs, summed across workers):"
            f"  fetch={per_row_fetch_us:6.0f}  json={per_row_json_us:6.0f}  extract={per_row_extract_us:6.0f}",
        )
        frac = lambda x: 100 * x / cpu_total if cpu_total else 0
        print(
            f"  share of CPU time:"
            f"  fetch={frac(fetch_total):5.1f}%  json={frac(json_total):5.1f}%  extract={frac(extract_total):5.1f}%",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
