#!/usr/bin/env python3
"""Measure in-sample bias in the specialist Pareto curves the recall-monotone
floor consults.

The recall-monotone floor in azoth_route_policy_search._mark_dominated_by_specialist
compares each ensemble candidate's (tp, fp) against the specialist's
recall@(same FP) — the "best the specialist could do at that FP cost." That
Pareto curve is computed today from the FULL CORPUS specialist probabilities
in score_table.npz. But specialists were trained on train+dev rows, so their
scores on those rows are IN-SAMPLE — overconfident on training malware,
suspiciously tight on training benigns. The Pareto curve inherits that
optimism and the floor over-rejects ensembles.

Test partition rows are different: they're locked out of training and the
specialists never saw them. Specialist probs on test rows are honest OOS.

This script compares, per filetype:

  * ``full_recall@K``  — Pareto recall@K-FPs computed from ALL rows
    (the curve currently used by the floor; biased optimistic).
  * ``test_recall@K``  — Pareto recall@K-FPs computed from test rows only
    (honest, but bounded by test slice's malware count).

Big positive deltas (full − test) tell us the floor is over-confident in the
specialist by that many recall points at FP=K — exactly the gap that lets
ensembles falsely look "dominated by specialist." Small deltas mean the
in-sample bias is minor and the multi-day retrain is unjustified.

The diagnostic is read-only: it produces a markdown table for inspection
and exits. No calibration is touched.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import data  # noqa: E402


def _pareto_recall_at_fp(
    probs: np.ndarray,
    labels: np.ndarray,
    *,
    fp_targets: tuple[int, ...],
) -> tuple[dict[int, float], int, int]:
    """Best specialist recall achievable using probs alone at each FP count.

    Returns (``{fp: recall_or_nan}``, n_malware, n_benign). NaN probs are
    dropped. Ties at the threshold count benigns BEFORE malware (worst case
    for recall, matches what an attacker can force at a fixed threshold).
    Recall is NaN when the slice has no malware.
    """
    valid = ~np.isnan(probs)
    if not np.any(valid):
        return ({k: math.nan for k in fp_targets}, 0, 0)
    p = probs[valid].astype(np.float64)
    y = labels[valid].astype(np.int8)
    n_mal = int((y == 1).sum())
    n_ben = int((y == 0).sum())
    if n_mal == 0:
        return ({k: math.nan for k in fp_targets}, n_mal, n_ben)
    order = np.lexsort((y, -p))
    y_sorted = y[order]
    fp_cum = np.cumsum(y_sorted == 0)
    tp_cum = np.cumsum(y_sorted == 1)
    out: dict[int, float] = {}
    for k in fp_targets:
        eligible = np.flatnonzero(fp_cum <= k)
        if len(eligible) == 0:
            out[k] = 0.0
        else:
            end = int(eligible[-1])
            out[k] = float(tp_cum[end]) / n_mal
    return (out, n_mal, n_ben)


def _delta_str(full: float, test: float) -> str:
    if math.isnan(full) or math.isnan(test):
        return "—"
    d = (full - test) * 100
    if abs(d) < 0.05:
        return "·"
    sign = "+" if d > 0 else ""
    return f"{sign}{d:.1f}"


def _pct(v: float) -> str:
    if math.isnan(v):
        return "—"
    return f"{100*v:.1f}%"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--score-table",
        type=Path,
        default=Path("out/models/azoth/score_table.npz"),
    )
    parser.add_argument(
        "--general-scores",
        type=Path,
        default=Path("out/models/azoth/general/threshold_scores.npz"),
        help="Needed for canonical_shas → partition filter.",
    )
    parser.add_argument(
        "--fp-targets",
        type=str,
        default="0,1,3,5,10",
        help="Comma-separated FP counts to compare. Default: 0,1,3,5,10.",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("out/models/azoth/specialist_bias_diagnostic.md"),
    )
    args = parser.parse_args()
    fp_targets = tuple(sorted(set(int(x) for x in args.fp_targets.split(","))))

    st = np.load(args.score_table, allow_pickle=False)
    gc = np.load(args.general_scores, allow_pickle=False)
    if "canonical_shas" not in gc.files:
        raise SystemExit(f"{args.general_scores} lacks canonical_shas")
    gen_row_ids = gc["row_ids"].astype(np.int64)
    canon_by_row = dict(zip(gen_row_ids.tolist(), gc["canonical_shas"].tolist()))
    row_ids = st["row_ids"].astype(np.int64)
    canonical_shas = np.asarray(
        [canon_by_row.get(int(r), "") for r in row_ids],
    )
    test_mask = np.asarray(
        [data.partition_of(str(c)) == "test" for c in canonical_shas],
        dtype=bool,
    )
    train_dev_mask = ~test_mask

    labels = st["labels"].astype(np.int8)
    file_types = np.asarray([str(v) for v in st["file_types"]])
    route_names = [str(v) for v in st["route_names"]]
    scores = st["scores"]

    rows: list[dict[str, Any]] = []
    for file_type in sorted(set(file_types)):
        spec_route = f"filetypes/{file_type}"
        if spec_route not in route_names:
            continue
        spec_idx = route_names.index(spec_route)
        ft_mask = file_types == file_type
        if not ft_mask.any():
            continue
        probs = scores[spec_idx]
        full_pareto, n_mal_full, n_ben_full = _pareto_recall_at_fp(
            probs[ft_mask], labels[ft_mask], fp_targets=fp_targets,
        )
        test_slice = ft_mask & test_mask
        test_pareto, n_mal_test, n_ben_test = _pareto_recall_at_fp(
            probs[test_slice], labels[test_slice], fp_targets=fp_targets,
        )
        in_sample_slice = ft_mask & train_dev_mask
        in_sample_pareto, n_mal_is, n_ben_is = _pareto_recall_at_fp(
            probs[in_sample_slice], labels[in_sample_slice],
            fp_targets=fp_targets,
        )
        rows.append({
            "file_type": file_type,
            "n_mal_full": n_mal_full,
            "n_ben_full": n_ben_full,
            "n_mal_test": n_mal_test,
            "n_ben_test": n_ben_test,
            "full": full_pareto,
            "test": test_pareto,
            "in_sample": in_sample_pareto,
        })

    rows.sort(key=lambda r: -r["n_mal_test"])

    # Markdown table.
    lines: list[str] = [
        "# Specialist In-Sample Bias Diagnostic",
        "",
        "Each row: a filetype's specialist-Pareto recall@FP, computed two ways:",
        "",
        "- **full** — over the full corpus slice (train+dev+test). This is",
        "  the curve the recall-monotone floor in `azoth_route_policy_search`",
        "  currently consults. Biased because train+dev rows are in-sample",
        "  for the specialist.",
        "- **test** — over only the test partition slice. Honest, but bounded",
        "  by the test malware count for resolution at small FP counts.",
        "- **Δ** — full − test (percentage points). Positive means full-corpus",
        "  is more optimistic than honest test data. **Large positive Δ at",
        "  the FP counts you care about → the floor is rejecting genuinely-",
        "  useful ensembles based on inflated specialist recall.**",
        "",
        "Filetypes with too little test malware to resolve a clean Pareto",
        "(< 30 test malware) are reported at the bottom for completeness;",
        "their Δ values are noisy and shouldn't drive retrain decisions.",
        "",
    ]
    fp_cols = " | ".join(f"FP={k}" for k in fp_targets)
    delta_cols = " | ".join(f"Δ@{k}" for k in fp_targets)
    header = f"| filetype | mal(test) | ben(test) | mal(full) | {fp_cols} (full) | {fp_cols} (test) | {delta_cols} |"
    lines.append(header)
    lines.append("| --- | ---: | ---: | ---: | " + " | ".join("---:" for _ in fp_targets) + " | "
                 + " | ".join("---:" for _ in fp_targets) + " | "
                 + " | ".join("---:" for _ in fp_targets) + " |")

    resolved_rows = [r for r in rows if r["n_mal_test"] >= 30]
    unresolved_rows = [r for r in rows if r["n_mal_test"] < 30]
    for r in resolved_rows:
        full_cells = " | ".join(_pct(r["full"][k]) for k in fp_targets)
        test_cells = " | ".join(_pct(r["test"][k]) for k in fp_targets)
        delta_cells = " | ".join(
            _delta_str(r["full"][k], r["test"][k]) for k in fp_targets
        )
        lines.append(
            f"| {r['file_type']} | {r['n_mal_test']} | {r['n_ben_test']} | "
            f"{r['n_mal_full']} | {full_cells} | {test_cells} | {delta_cells} |"
        )

    if unresolved_rows:
        lines.append("")
        lines.append("### Filetypes with insufficient test data (Δ unreliable)")
        lines.append("")
        lines.append(header)
        lines.append("| --- | ---: | ---: | ---: | " + " | ".join("---:" for _ in fp_targets) + " | "
                     + " | ".join("---:" for _ in fp_targets) + " | "
                     + " | ".join("---:" for _ in fp_targets) + " |")
        for r in unresolved_rows:
            full_cells = " | ".join(_pct(r["full"][k]) for k in fp_targets)
            test_cells = " | ".join(_pct(r["test"][k]) for k in fp_targets)
            delta_cells = " | ".join(
                _delta_str(r["full"][k], r["test"][k]) for k in fp_targets
            )
            lines.append(
                f"| {r['file_type']} | {r['n_mal_test']} | {r['n_ben_test']} | "
                f"{r['n_mal_full']} | {full_cells} | {test_cells} | {delta_cells} |"
            )

    # Summary statistics: weighted average delta at each FP, using test malware
    # as the weight (so heavy-volume filetypes dominate the headline).
    lines.append("")
    lines.append("## Weighted-average bias (heavy filetypes weighted higher)")
    lines.append("")
    lines.append("Each row's Δ@K weighted by test-malware count, summed and normalized.")
    lines.append("Filetypes with <30 test malware are excluded so the average reflects")
    lines.append("only statistically-resolvable comparisons.")
    lines.append("")
    lines.append(f"| FP | weighted avg full | weighted avg test | weighted avg Δ |")
    lines.append("| ---: | ---: | ---: | ---: |")
    for k in fp_targets:
        total_w = sum(r["n_mal_test"] for r in resolved_rows
                      if not math.isnan(r["full"][k]) and not math.isnan(r["test"][k]))
        if total_w == 0:
            lines.append(f"| {k} | — | — | — |")
            continue
        wf = sum(r["n_mal_test"] * r["full"][k] for r in resolved_rows
                 if not math.isnan(r["full"][k]) and not math.isnan(r["test"][k])) / total_w
        wt = sum(r["n_mal_test"] * r["test"][k] for r in resolved_rows
                 if not math.isnan(r["full"][k]) and not math.isnan(r["test"][k])) / total_w
        lines.append(f"| {k} | {100*wf:.2f}% | {100*wt:.2f}% | {100*(wf-wt):+.2f} |")

    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text("\n".join(lines) + "\n")
    print(f"wrote {args.output_md}")

    # Also dump a short stdout summary so the operator sees the result without
    # opening the file.
    print()
    print("Weighted-average bias by FP count:")
    for k in fp_targets:
        total_w = sum(r["n_mal_test"] for r in resolved_rows
                      if not math.isnan(r["full"][k]) and not math.isnan(r["test"][k]))
        if total_w == 0:
            print(f"  FP={k}: no resolvable comparisons")
            continue
        wf = sum(r["n_mal_test"] * r["full"][k] for r in resolved_rows
                 if not math.isnan(r["full"][k]) and not math.isnan(r["test"][k])) / total_w
        wt = sum(r["n_mal_test"] * r["test"][k] for r in resolved_rows
                 if not math.isnan(r["full"][k]) and not math.isnan(r["test"][k])) / total_w
        print(f"  FP={k}: full-corpus Pareto = {100*wf:.2f}%, test-only Pareto = {100*wt:.2f}%, Δ = {100*(wf-wt):+.2f}pp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
