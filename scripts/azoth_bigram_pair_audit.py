#!/usr/bin/env python3
"""Audit ``bigrams:X`` vs ``unsigned_bigram:X`` feature pairs for redundancy.

Cleave emits two parallel families for the same trait hierarchies — the
``bigrams:`` and ``unsigned_bigram:`` ones share the same path keys (look
at out/models/azoth/general/feature_spec.json: 3,039 entries in each for
``metadata/binary`` alone). They may encode different signal, or they
may be near-duplicates and we're paying 2× the feature-count cost for
the same information.

This script answers: per pair, are they fire-on-the-same-rows duplicates
or do they carry distinct signal?

Inputs:
  --matrix      path to a cached sparse feature matrix (csr_matrix .npz)
  --spec        path to the feature spec (feature_names list) used to
                build that matrix

The pair-finding logic strips the family prefix and compares paths:
  bigrams:metadata/binary/foo + bar      ┐  paired
  unsigned_bigram:metadata/binary/foo + bar  ┘

For each pair we report:
  * Jaccard similarity over presence (rows where the feature is non-zero)
  * Pearson correlation of the column values
  * Combined activity (rows where either fires)
  * Asymmetry: rows where bigrams fires but unsigned_bigram doesn't, and
    vice versa

Output is a markdown table sorted by Jaccard ascending — the LEAST
redundant pairs come first (most worth keeping) and the most redundant
pairs come last (drop candidates).

Read-only: no model retraining, no feature regeneration. Operates entirely
on cached matrices.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy.sparse as sp


def _pair_features(feature_names: list[str]) -> dict[str, tuple[int, int]]:
    """Find feature indices for ``bigrams:<path>`` / ``unsigned_bigram:<path>``
    pairs sharing the same path.

    Returns ``{path: (bigrams_idx, unsigned_bigram_idx)}``. Single-family
    entries (only one prefix present for a path) are dropped — we can
    only audit pairs, not orphans.
    """
    by_path: dict[str, dict[str, int]] = defaultdict(dict)
    for idx, name in enumerate(feature_names):
        for prefix in ("bigrams:", "unsigned_bigram:"):
            if name.startswith(prefix):
                path = name[len(prefix):]
                by_path[path][prefix] = idx
                break
    pairs: dict[str, tuple[int, int]] = {}
    for path, indices in by_path.items():
        if "bigrams:" in indices and "unsigned_bigram:" in indices:
            pairs[path] = (indices["bigrams:"], indices["unsigned_bigram:"])
    return pairs


def _csc_col_rows(matrix: sp.csc_matrix, col_idx: int) -> np.ndarray:
    """Return the row indices of non-zero entries in column ``col_idx``.

    For a CSC matrix this is an O(nnz_per_column) slice into ``indices``;
    no per-call scan of the whole matrix needed. The data filter (``!= 0``)
    handles the rare case where the matrix carries explicit zeros that
    a stale build process left in place.
    """
    start, end = matrix.indptr[col_idx], matrix.indptr[col_idx + 1]
    data = matrix.data[start:end]
    rows = matrix.indices[start:end]
    if data.dtype != bool:
        return rows[data != 0]
    return rows[data]


def _column_stats(
    matrix: sp.csc_matrix,
    a_idx: int,
    b_idx: int,
) -> dict[str, float | int]:
    """Per-pair similarity stats using the BOOLEAN fire mask.

    Real-valued correlation would be ideal but most cleave bigram features
    are 0/1 indicators with occasional counts; presence-Jaccard captures
    the redundancy question ("do they fire on the same rows?") without
    needing to assume the column dtype.

    Uses sorted-array intersection via ``np.intersect1d`` instead of Python
    sets — the row index arrays are already sorted (CSC invariant) and
    NumPy's set ops are ~10x faster for the column sizes cleave bigrams
    produce.
    """
    a_rows = _csc_col_rows(matrix, a_idx)
    b_rows = _csc_col_rows(matrix, b_idx)
    n_a = int(len(a_rows))
    n_b = int(len(b_rows))
    # assume_unique=True: CSC column indices are already unique+sorted, so
    # NumPy can use the merge-style fast path.
    inter = np.intersect1d(a_rows, b_rows, assume_unique=True)
    n_inter = int(len(inter))
    n_union = n_a + n_b - n_inter
    return {
        "a_count": n_a,
        "b_count": n_b,
        "intersection": n_inter,
        "union": n_union,
        "a_only": n_a - n_inter,
        "b_only": n_b - n_inter,
        "jaccard": n_inter / max(n_union, 1),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("out/cache/experiment/azoth/matrix_ea302944c7d68f6b_Xtrain.npz"),
        help=(
            "Sparse csr_matrix .npz to audit. Use any cached training "
            "matrix — pair stats are invariant to the model that consumed "
            "it, as long as columns align with --spec's feature_names."
        ),
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path("out/cache/experiment/azoth/matrix_ea302944c7d68f6b_spec.json"),
        help="Feature spec whose feature_names index the matrix columns.",
    )
    parser.add_argument(
        "--min-support",
        type=int,
        default=100,
        help=(
            "Skip pairs where the union of presences is below this many "
            "rows — Jaccard is noisy on tiny supports. Default 100."
        ),
    )
    parser.add_argument(
        "--max-pairs",
        type=int,
        default=0,
        help="If >0, audit only this many pairs (for quick iteration).",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("out/models/azoth/bigram_pair_audit.md"),
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("out/models/azoth/bigram_pair_audit.csv"),
    )
    args = parser.parse_args()

    matrix = sp.load_npz(args.matrix)
    # CSC for fast column access — getcol on CSR is O(n_rows) which on a
    # 671k-row matrix multiplied by 10k column accesses becomes minutes
    # per pair. CSC turns the inner loop into a slice into indptr/indices,
    # so the same audit finishes in seconds.
    if not sp.isspmatrix_csc(matrix):
        matrix = matrix.tocsc()
    with open(args.spec) as f:
        spec = json.load(f)
    feature_names = list(spec["feature_names"])
    if matrix.shape[1] != len(feature_names):
        raise SystemExit(
            f"matrix has {matrix.shape[1]} columns, spec has "
            f"{len(feature_names)} feature_names — mismatched pair?",
        )

    pairs = _pair_features(feature_names)
    print(f"# Found {len(pairs)} bigrams/unsigned_bigram pairs in {len(feature_names):,} features")
    print(f"# Matrix: {matrix.shape[0]:,} rows × {matrix.shape[1]:,} cols, nnz={matrix.nnz:,}")
    if args.max_pairs > 0:
        # Stable but deterministic limit so re-runs land on the same subset.
        pairs = dict(list(pairs.items())[: args.max_pairs])
        print(f"# Limited to first {len(pairs)} pairs by --max-pairs")

    results: list[dict[str, float | int | str]] = []
    for path, (a_idx, b_idx) in pairs.items():
        stats = _column_stats(matrix, a_idx, b_idx)
        if stats["union"] < args.min_support:
            continue
        family = path.split(" + ", 1)[0] if " + " in path else path.split("/", 2)[1] if "/" in path else "?"
        results.append({
            "path": path,
            "family": family,
            **stats,
        })

    # Sort: lowest Jaccard first (least redundant — most worth keeping both).
    results.sort(key=lambda r: r["jaccard"])

    print(f"# After --min-support={args.min_support}: {len(results)} pairs audited")
    print()

    # Aggregate by family for the headline.
    per_family: dict[str, list[float]] = defaultdict(list)
    for r in results:
        per_family[str(r["family"])].append(float(r["jaccard"]))
    print(f"## Per-family Jaccard distribution (lower = pair carries distinct signal)")
    print()
    print(f"{'family':<40s} {'n':>5s}  {'p10':>5s}  {'p50':>5s}  {'p90':>5s}  {'mean':>5s}")
    fam_summary = []
    for fam, jaccs in per_family.items():
        arr = np.array(jaccs)
        fam_summary.append({
            "family": fam,
            "n": len(jaccs),
            "p10": float(np.percentile(arr, 10)),
            "p50": float(np.percentile(arr, 50)),
            "p90": float(np.percentile(arr, 90)),
            "mean": float(arr.mean()),
        })
    fam_summary.sort(key=lambda x: -x["n"])
    for row in fam_summary[:30]:
        print(
            f"{row['family']:<40s} {row['n']:>5d}  "
            f"{row['p10']:>5.2f}  {row['p50']:>5.2f}  "
            f"{row['p90']:>5.2f}  {row['mean']:>5.2f}",
        )

    # Markdown report.
    lines: list[str] = [
        "# Bigram Pair Redundancy Audit",
        "",
        f"- Matrix: `{args.matrix}` ({matrix.shape[0]:,} rows × {matrix.shape[1]:,} cols)",
        f"- Spec: `{args.spec}`",
        f"- Pairs found: {len(pairs):,} (of {len(feature_names):,} features)",
        f"- Audited (union ≥ {args.min_support}): {len(results):,}",
        "",
        "Jaccard = |A ∩ B| / |A ∪ B| over rows where each feature is non-zero.",
        "Jaccard near 1.0 ⇒ near-duplicate columns: dropping one is safe.",
        "Jaccard near 0.0 ⇒ disjoint: both columns carry distinct information.",
        "",
        "## Per-family Jaccard summary",
        "",
        "| Family | Pairs | Jaccard p10 | p50 | p90 | mean |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in fam_summary:
        lines.append(
            f"| `{row['family']}` | {row['n']} | {row['p10']:.2f} | "
            f"{row['p50']:.2f} | {row['p90']:.2f} | {row['mean']:.2f} |",
        )

    lines.extend([
        "",
        "## Most redundant pairs (Jaccard ≥ 0.95) — drop candidates",
        "",
        "| Family | Path | Jaccard | A only | B only | Both | Union |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    redundant = [r for r in results if r["jaccard"] >= 0.95]
    for r in redundant[:200]:
        lines.append(
            f"| `{r['family']}` | `{r['path']}` | {r['jaccard']:.3f} | "
            f"{r['a_only']} | {r['b_only']} | {r['intersection']} | {r['union']} |",
        )
    if len(redundant) > 200:
        lines.append(f"\n... and {len(redundant) - 200} more.")

    lines.extend([
        "",
        "## Least redundant pairs (Jaccard ≤ 0.5) — keep both",
        "",
        "| Family | Path | Jaccard | A only | B only | Both | Union |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    distinct = [r for r in results if r["jaccard"] <= 0.5]
    for r in distinct[:200]:
        lines.append(
            f"| `{r['family']}` | `{r['path']}` | {r['jaccard']:.3f} | "
            f"{r['a_only']} | {r['b_only']} | {r['intersection']} | {r['union']} |",
        )
    if len(distinct) > 200:
        lines.append(f"\n... and {len(distinct) - 200} more.")

    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text("\n".join(lines) + "\n")

    # CSV for further analysis.
    import csv  # noqa: PLC0415
    with open(args.output_csv, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["family", "path", "jaccard", "a_count", "b_count",
                        "intersection", "union", "a_only", "b_only"],
        )
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    n_redundant = sum(1 for r in results if r["jaccard"] >= 0.95)
    n_mostly = sum(1 for r in results if r["jaccard"] >= 0.80)
    n_distinct = sum(1 for r in results if r["jaccard"] <= 0.5)
    print()
    print(f"Headline:")
    print(f"  Near-duplicate pairs (Jaccard ≥ 0.95): {n_redundant:,} (dropping one saves {n_redundant} features)")
    print(f"  Mostly redundant (Jaccard ≥ 0.80): {n_mostly:,}")
    print(f"  Distinct signal (Jaccard ≤ 0.5): {n_distinct:,}")
    print()
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
