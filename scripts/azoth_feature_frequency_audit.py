#!/usr/bin/env python3
"""Identify min-frequency thresholds that cull the feature long tail with
minimal information loss — the runtime lever we actually want.

LightGBM training cost scales roughly linearly with ``n_features`` for
the histogram construction at every tree node. A 42K-feature matrix at
~0.2-2.6% density spends most of its split evaluation walking columns
that fire on a handful of rows total. Those features can't generalize
(too few examples to fit a real split) and they can't BE generalized to
from (too rare to help at deploy). They're pure overhead.

This script answers: how many features could we drop, and at what
quality risk, by raising the min-frequency threshold the corpus
generator uses (``COLLIMATOR_BIGRAM_MIN_FREQ`` and siblings)?

Inputs:
  --matrix      cached training feature matrix (sparse npz)
  --spec        feature spec with feature_names index
  --labels      sibling .npz with ``y_train`` (typically the matrix's
                base file: matrix_<hash>.npz holds labels, while the
                _Xtrain suffix holds the feature matrix proper)

For each candidate threshold T we report:
  * features retained / dropped
  * proportional training-cost reduction
  * features that would be dropped but ARE plausibly useful — i.e.,
    fire on at least N_MIN_MAL malware. These are the false-positive
    drops; if any threshold drops many of them, that threshold's too
    aggressive.

Plus per-family breakdown so you can see which bigram/trigram families
have the most cullable long tail.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp


def _per_column_nnz_by_label(
    matrix: sp.csc_matrix, labels: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Per-column counts of non-zero entries split by binary label.

    Returns ``(nnz_malware, nnz_benign)`` arrays of length n_features.
    Uses the CSC indptr/indices directly — no per-column slicing, so
    runtime is O(nnz_total).
    """
    n_features = matrix.shape[1]
    nnz_mal = np.zeros(n_features, dtype=np.int64)
    nnz_ben = np.zeros(n_features, dtype=np.int64)
    labels_int = labels.astype(np.int8)
    is_mal = labels_int == 1
    is_ben = labels_int == 0
    indptr = matrix.indptr
    indices = matrix.indices
    data = matrix.data
    nz_mask = data != 0 if data.dtype != bool else data
    for col in range(n_features):
        start, end = int(indptr[col]), int(indptr[col + 1])
        if start == end:
            continue
        col_rows = indices[start:end]
        col_nz = nz_mask[start:end]
        rows = col_rows[col_nz] if col_nz.dtype == bool else col_rows
        nnz_mal[col] = int(is_mal[rows].sum())
        nnz_ben[col] = int(is_ben[rows].sum())
    return nnz_mal, nnz_ben


def _feature_family(name: str) -> str:
    """Coarse-grained bucket for per-family rollups.

    Family = "<prefix>:<path[:2]>". For ``bigrams:metadata/binary/...``
    that's ``bigrams:metadata/binary``. Captures the granularity at
    which COLLIMATOR_BIGRAM_MIN_FREQ would actually cut.
    """
    if ":" not in name:
        return "(unprefixed)"
    prefix, path = name.split(":", 1)
    parts = path.split("/")
    if len(parts) >= 2:
        return f"{prefix}:{'/'.join(parts[:2])}"
    return f"{prefix}:{parts[0] if parts else '?'}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("out/cache/experiment/azoth/matrix_ea302944c7d68f6b_Xtrain.npz"),
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path("out/cache/experiment/azoth/matrix_ea302944c7d68f6b_spec.json"),
    )
    parser.add_argument(
        "--labels",
        type=Path,
        default=Path("out/cache/experiment/azoth/matrix_ea302944c7d68f6b.npz"),
        help=(
            "Companion .npz holding the y_train array. The experiment "
            "cache writes labels to the base file (without the _Xtrain "
            "suffix) and the feature matrix to the _Xtrain suffix."
        ),
    )
    parser.add_argument(
        "--thresholds",
        type=str,
        default="10,25,50,100,200,500,1000,2000,5000",
        help="Comma-separated min-frequency candidates to evaluate.",
    )
    parser.add_argument(
        "--min-malware-protected",
        type=int,
        default=10,
        help=(
            "A feature is considered POTENTIALLY USEFUL if it fires on "
            "at least this many malware rows. Features dropped by a "
            "threshold that have ≥ N_MIN_MAL malware-fires are reported "
            "as 'borderline drops' — if a candidate threshold has many "
            "borderline drops, it's too aggressive."
        ),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("out/models/azoth/feature_frequency_audit.md"),
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("out/models/azoth/feature_frequency_audit.csv"),
    )
    args = parser.parse_args()

    thresholds = sorted(int(x) for x in args.thresholds.split(","))

    print(f"loading matrix {args.matrix}")
    matrix = sp.load_npz(args.matrix)
    if not sp.isspmatrix_csc(matrix):
        matrix = matrix.tocsc()
    print(f"  shape={matrix.shape}, nnz={matrix.nnz:,}, dtype={matrix.dtype}")

    print(f"loading labels from {args.labels}")
    label_blob = np.load(args.labels, allow_pickle=True)
    if "y_train" not in label_blob.files:
        raise SystemExit(
            f"{args.labels} has no y_train key (keys: {label_blob.files})",
        )
    labels = label_blob["y_train"]
    if len(labels) != matrix.shape[0]:
        raise SystemExit(
            f"label length {len(labels)} != matrix rows {matrix.shape[0]}",
        )
    n_mal = int((labels.astype(np.int8) == 1).sum())
    n_ben = int((labels.astype(np.int8) == 0).sum())
    print(f"  malware={n_mal:,} benign={n_ben:,}")

    import json  # noqa: PLC0415
    spec = json.load(open(args.spec))
    feature_names = list(spec["feature_names"])
    if matrix.shape[1] != len(feature_names):
        raise SystemExit("matrix cols / spec feature_names mismatch")

    print("computing per-column nnz split by label...")
    nnz_mal, nnz_ben = _per_column_nnz_by_label(matrix, labels)
    total_nnz = nnz_mal + nnz_ben

    print()
    print("Per-feature frequency distribution:")
    n_features = len(feature_names)
    for bucket_hi in [1, 10, 100, 1000, 10000, 100000, 1_000_000]:
        below = int((total_nnz < bucket_hi).sum())
        print(f"  nnz < {bucket_hi:>10,}: {below:>6,} features ({100*below/n_features:.1f}%)")

    # Per-threshold drop count + borderline analysis.
    print()
    print("Per-threshold drop projections:")
    print(
        f"{'min-freq':>10s}  {'dropped':>10s}  {'retained':>10s}  "
        f"{'%retained':>10s}  {'borderline':>10s}  {'note':<30s}"
    )
    threshold_rows: list[dict[str, Any]] = []
    for t in thresholds:
        keep_mask = total_nnz >= t
        dropped = int((~keep_mask).sum())
        retained = int(keep_mask.sum())
        # Borderline: features that WOULD be dropped at threshold t but
        # have ≥ min_malware_protected malware fires. Likely-real signal
        # the cull would lose.
        borderline = int(((~keep_mask) & (nnz_mal >= args.min_malware_protected)).sum())
        note = ""
        if borderline > 100:
            note = "(>100 borderline; aggressive)"
        elif borderline < 5:
            note = "(safe)"
        print(
            f"{t:>10d}  {dropped:>10,}  {retained:>10,}  "
            f"{100*retained/n_features:>9.1f}%  {borderline:>10,}  {note:<30s}"
        )
        threshold_rows.append({
            "min_freq": t,
            "dropped": dropped,
            "retained": retained,
            "retained_pct": 100 * retained / n_features,
            "borderline_drops": borderline,
            "est_speedup_pct": 100 * (1 - retained / n_features),
        })

    # Per-family rollup at one focal threshold (typically the
    # "interesting middle" — 200-500). We pick the middle threshold of
    # the user's list for the table.
    focal = thresholds[len(thresholds) // 2]
    print()
    print(f"Per-family breakdown at min-freq={focal}:")
    family_stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"total": 0, "dropped": 0, "borderline": 0, "max_mal": 0}
    )
    for idx, name in enumerate(feature_names):
        fam = _feature_family(name)
        family_stats[fam]["total"] += 1
        if int(total_nnz[idx]) < focal:
            family_stats[fam]["dropped"] += 1
            if int(nnz_mal[idx]) >= args.min_malware_protected:
                family_stats[fam]["borderline"] += 1
        if int(nnz_mal[idx]) > family_stats[fam]["max_mal"]:
            family_stats[fam]["max_mal"] = int(nnz_mal[idx])

    fam_rows = []
    for fam, stats in family_stats.items():
        if stats["total"] < 50:
            continue  # tiny families add table noise; focus on the heavy hitters
        fam_rows.append({
            "family": fam,
            "total": stats["total"],
            "dropped_at_focal": stats["dropped"],
            "drop_pct": 100 * stats["dropped"] / max(stats["total"], 1),
            "borderline": stats["borderline"],
            "max_mal_in_family": stats["max_mal"],
        })
    fam_rows.sort(key=lambda r: -r["dropped_at_focal"])
    print(
        f"{'family':<40s} {'total':>6s}  {'dropped':>7s}  {'drop%':>6s}  "
        f"{'borderline':>10s}"
    )
    for r in fam_rows[:30]:
        print(
            f"{r['family']:<40s} {r['total']:>6d}  {r['dropped_at_focal']:>7d}  "
            f"{r['drop_pct']:>5.1f}%  {r['borderline']:>10d}"
        )

    # Markdown report.
    lines = [
        "# Feature-Frequency Audit (runtime savings via min-freq tuning)",
        "",
        f"- Matrix: `{args.matrix}` ({matrix.shape[0]:,} rows × {matrix.shape[1]:,} cols, nnz={matrix.nnz:,})",
        f"- Labels: {n_mal:,} malware, {n_ben:,} benign",
        "",
        "Per-feature nnz = number of rows where the feature fires (non-zero).",
        "LightGBM training cost is roughly linear in retained feature count.",
        "Borderline drop = a feature the threshold would cull but that fires on",
        f"≥ {args.min_malware_protected} malware rows (potentially-real signal at risk).",
        "",
        "## Min-frequency threshold projections",
        "",
        "| min-freq | dropped | retained | %retained | borderline drops | est. cost reduction |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in threshold_rows:
        lines.append(
            f"| {r['min_freq']} | {r['dropped']:,} | {r['retained']:,} | "
            f"{r['retained_pct']:.1f}% | {r['borderline_drops']:,} | "
            f"{r['est_speedup_pct']:.1f}% |"
        )

    lines.extend([
        "",
        f"## Per-family breakdown at min-freq={focal}",
        "",
        "Families with ≥ 50 features sorted by drop count.",
        "Borderline = features in this family that would drop but fire on ≥ 10 malware.",
        "",
        "| Family | Total | Dropped | Drop % | Borderline | Max malware fires |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for r in fam_rows:
        lines.append(
            f"| `{r['family']}` | {r['total']} | {r['dropped_at_focal']} | "
            f"{r['drop_pct']:.1f}% | {r['borderline']} | {r['max_mal_in_family']} |"
        )

    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text("\n".join(lines) + "\n")
    print()
    print(f"wrote {args.output_md}")

    # CSV: per-feature dump for arbitrary downstream filtering.
    with open(args.output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["feature", "family", "nnz_total", "nnz_malware", "nnz_benign"])
        for idx, name in enumerate(feature_names):
            writer.writerow([
                name,
                _feature_family(name),
                int(total_nnz[idx]),
                int(nnz_mal[idx]),
                int(nnz_ben[idx]),
            ])
    print(f"wrote {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
