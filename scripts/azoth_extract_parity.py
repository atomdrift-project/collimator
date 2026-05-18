#!/usr/bin/env python3
"""Verify the path-filter optimization in _apply_{bi,tri,synergy}gram_features
produces bit-identical feature vectors as the unfiltered version.

Approach: monkey-patch the filter sets to be "all paths" (so behavior
matches pre-optimization), extract once. Then restore the real filter
sets, extract again. Compare matrices.
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path

import numpy as np

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import data, features  # noqa: E402


def _make_batch(db: str, n: int, ftype: str, seed: int) -> list:
    with data._connect(db) as conn, conn.cursor() as cur:  # noqa: SLF001
        cur.execute(
            "SELECT id FROM samples WHERE file_type = %s AND label IN ('bad','good') "
            "AND cleave_result IS NOT NULL AND skip = '' ORDER BY id",
            (ftype,),
        )
        all_ids = [int(r[0]) for r in cur]
    rng = random.Random(seed)
    rng.shuffle(all_ids)
    ids = all_ids[:n]
    results = data.fetch_cleave_results(db, ids)
    return [(item, 0) for item in results.values() if item["cleave_result"]]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--filetype", default="pe")
    parser.add_argument("--n", type=int, default=100)
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path("out/models/azoth/general/feature_spec.json"),
    )
    args = parser.parse_args()

    spec = features.FeatureSpec.load(args.spec)
    batch = _make_batch(args.db, args.n, args.filetype, 20260518)
    print(f"batch size: {len(batch)}")

    # First: with the optimization active (real vocab paths).
    ctx_real = features._ExtractContext(spec)  # noqa: SLF001
    print(
        f"vocab paths: bigram={len(ctx_real.bigram_vocab_paths)} "
        f"trigram={len(ctx_real.trigram_vocab_paths)} "
        f"synergy={len(ctx_real.synergy_vocab_paths)}",
    )

    t0 = time.perf_counter()
    rows_opt, cols_opt, vals_opt, _ = features._extract_batch_worker((0, batch, spec))  # noqa: SLF001
    t_opt = time.perf_counter() - t0
    print(f"optimized:   wall={t_opt:.3f}s  nnz={len(rows_opt)}")

    # Second: monkey-patch the filter sets to a frozenset that contains
    # every path the extractor will ever see — equivalent to "no filter".
    # We use a sentinel set that returns True for any membership check.
    class _Universe(frozenset):
        def __contains__(self, _item):  # type: ignore[override]
            return True

    universe: frozenset[str] = _Universe()
    orig_b = features._ExtractContext.__init__  # noqa: SLF001

    def patched_init(self, spec):
        orig_b(self, spec)
        self.bigram_vocab_paths = universe
        self.trigram_vocab_paths = universe
        self.synergy_vocab_paths = universe
        self.tiered_bigram_vocab_tokens = universe
        self.tiered_trigram_vocab_tokens = universe
        self.tiered_quadgram_vocab_tokens = universe

    features._ExtractContext.__init__ = patched_init  # type: ignore[assignment]
    try:
        t0 = time.perf_counter()
        rows_un, cols_un, vals_un, _ = features._extract_batch_worker((0, batch, spec))  # noqa: SLF001
        t_un = time.perf_counter() - t0
    finally:
        features._ExtractContext.__init__ = orig_b  # type: ignore[assignment]
    print(f"unfiltered:  wall={t_un:.3f}s  nnz={len(rows_un)}")

    # Compare bit-exact.
    if rows_opt == rows_un and cols_opt == cols_un and vals_opt == vals_un:
        print(f"PARITY: bit-exact ({len(rows_opt)} entries match)")
        print(f"SPEEDUP: {t_un / t_opt:.2f}× on extraction")
        return 0
    # Diff details
    a = set(zip(rows_opt, cols_opt, vals_opt, strict=True))
    b = set(zip(rows_un, cols_un, vals_un, strict=True))
    print(f"PARITY: MISMATCH  opt={len(a)} un={len(b)}  shared={len(a & b)}  opt-only={len(a - b)}  un-only={len(b - a)}")
    print("first 5 un-only:", list(b - a)[:5])
    print("first 5 opt-only:", list(a - b)[:5])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
