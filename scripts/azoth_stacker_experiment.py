#!/usr/bin/env python3
"""Standalone experiment: does a gradient-trained LR stacker beat the
deployed OR-rule on test partition?

For each filetype, fit logistic regression on logit-transformed route
probabilities using train+dev rows only. Pareto-tune a threshold on the
blended score to spend exactly FP=K on the train+dev slice. Apply that
threshold to test rows; measure recall vs the deployed OR-rule's recall
at the same level (from route_policies.json).

Read-only: produces a markdown table and a JSON file with the per-filetype
deltas. Does not touch route_policies.json, score_table.npz, or any
deployed artifact.

Reads:
- score_table.npz (route probabilities + labels + file_types)
- general/threshold_scores.npz (canonical_shas for partition filter)
- route_policies.json (the deployed policy we compare against)

Key caveats (worth knowing while reading the numbers):

* General probs are honest OOF on train+dev, NaN on test. Group and
  specialist probs are IN-SAMPLE on train+dev (the specialist was trained
  on those rows), and out-of-sample on test (test was held out). So
  fitting LR on train+dev sees train+dev-in-sample probs for the
  specialist — overconfident. The test-side measurement is honest.
* If the stacker overfits to the in-sample specialist confidence, test
  recall will look pessimistic. A stacker that ties the OR-rule on test
  despite that bias would still be a win after honest specialist OOF
  lands.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import data  # noqa: E402

LOGIT_EPS = 1e-6


def _logit(probs: np.ndarray) -> np.ndarray:
    """Logit with clipping; np.nan rows pass through."""
    valid = ~np.isnan(probs)
    out = np.full_like(probs, np.nan, dtype=np.float64)
    p = np.clip(probs[valid].astype(np.float64), LOGIT_EPS, 1.0 - LOGIT_EPS)
    out[valid] = np.log(p / (1.0 - p))
    return out


def _fit_blend(
    route_probs: dict[str, np.ndarray],
    labels: np.ndarray,
    fit_mask: np.ndarray,
) -> tuple[list[str], np.ndarray, float, np.ndarray]:
    """Fit logistic regression on stacked logit-probs.

    ``fit_mask`` is a boolean array over the slice; True rows are used
    for fitting (typically train+dev). Returns
    ``(routes, weights, intercept, blend_score_over_slice)`` — the
    blended sigmoid(intercept + w·logit(probs)) for every row in the
    slice, not just the fit rows. Rows where any route is NaN are
    excluded from fitting and produce NaN blend scores so downstream
    code can drop them via ~np.isnan().
    """
    routes = list(route_probs)
    stacked = np.stack([_logit(route_probs[r]) for r in routes], axis=1)
    valid_row = ~np.any(np.isnan(stacked), axis=1)
    fit_rows = fit_mask & valid_row
    n_mal_fit = int(((labels == 1) & fit_rows).sum())
    n_ben_fit = int(((labels == 0) & fit_rows).sum())
    # LR needs ≥1 of each class. Slices that don't satisfy this fall
    # back to no-op weights so the caller can skip them cleanly.
    if n_mal_fit < 1 or n_ben_fit < 1:
        return (routes, np.zeros(len(routes)), 0.0,
                np.full(len(labels), np.nan, dtype=np.float64))
    x = stacked[fit_rows]
    y = labels[fit_rows].astype(np.int8)
    # class_weight='balanced' counteracts the corpus's ~76% benign skew
    # so the LR's loss surface isn't dominated by easy benigns. C is
    # mild (default 1.0); with only 3 features and at least hundreds of
    # rows we're nowhere near needing aggressive regularization.
    clf = LogisticRegression(
        C=1.0, class_weight="balanced", solver="liblinear", max_iter=200,
    ).fit(x, y)
    weights = clf.coef_[0].astype(np.float64)
    intercept = float(clf.intercept_[0])
    # Score every valid row in the slice, even rows that weren't fit.
    z = stacked @ weights + intercept
    blend = np.full(len(labels), np.nan, dtype=np.float64)
    blend[valid_row] = 1.0 / (1.0 + np.exp(-z[valid_row]))
    return (routes, weights, intercept, blend)


def _recall_at_fp(
    scores: np.ndarray,
    labels: np.ndarray,
    fp_budget: int,
) -> tuple[float, float | None]:
    """Best recall achievable using scores alone at FP≤fp_budget.

    Returns ``(recall, threshold_or_None)``. NaN rows are dropped. Ties
    put benigns BEFORE malware so cumulative FP leads its row's TP —
    the standard worst-case ordering an attacker can force.
    """
    valid = ~np.isnan(scores)
    if not np.any(valid):
        return (math.nan, None)
    p = scores[valid].astype(np.float64)
    y = labels[valid].astype(np.int8)
    n_mal = int((y == 1).sum())
    if n_mal == 0:
        return (math.nan, None)
    order = np.lexsort((y, -p))
    p_sorted = p[order]
    y_sorted = y[order]
    fp_cum = np.cumsum(y_sorted == 0)
    tp_cum = np.cumsum(y_sorted == 1)
    eligible = np.flatnonzero(fp_cum <= fp_budget)
    if len(eligible) == 0:
        return (0.0, None)
    end = int(eligible[-1])
    return (float(tp_cum[end]) / n_mal, float(p_sorted[end]))


def _apply_or_rule(
    route_probs: dict[str, np.ndarray],
    thresholds: dict[str, float],
    mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (hit, valid) under deployed OR-rule with per-route thresholds.

    Each route is OR'd in when its threshold is < 1.0 (the no-fire
    sentinel). ``valid`` is True wherever at least one named route has
    a non-NaN prob; OR-rule on a row with all NaNs would land on no
    contribution and should be treated as ineligible rather than benign.
    """
    n = int(mask.sum())
    hit = np.zeros(n, dtype=bool)
    valid = np.zeros(n, dtype=bool)
    for route_name, threshold in thresholds.items():
        if threshold is None or float(threshold) >= 1.0:
            continue
        probs = route_probs.get(route_name)
        if probs is None:
            continue
        slice_probs = probs[mask]
        slice_valid = ~np.isnan(slice_probs)
        hit |= slice_valid & (slice_probs >= float(threshold))
        valid |= slice_valid
    return hit, valid


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
    )
    parser.add_argument(
        "--route-policies",
        type=Path,
        default=Path("out/models/azoth/route_policies.json"),
    )
    parser.add_argument(
        "--level",
        type=int,
        default=50,
        help="Which level's deployed policy to compare against (default 50, the new per-100M operating point).",
    )
    parser.add_argument(
        "--fp-targets",
        type=str,
        default="0,1,3",
        help=(
            "FP budgets to evaluate the stacker at, in absolute FP counts "
            "on the train+dev slice. Default 0,1,3 — the operating points "
            "the user prioritizes."
        ),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("out/models/azoth/stacker_experiment.md"),
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("out/models/azoth/stacker_experiment.json"),
    )
    parser.add_argument(
        "--min-mal",
        type=int,
        default=30,
        help="Skip slices with fewer than this many train+dev malware.",
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
    route_name_to_idx = {n: i for i, n in enumerate(route_names)}
    scores = st["scores"]

    with open(args.route_policies) as f:
        rp = json.load(f)
    policies_by_filetype: dict[str, dict[str, Any]] = {}
    for route_payload in rp.get("routes", {}).values():
        if route_payload.get("filetype"):
            policies_by_filetype[route_payload["filetype"]] = route_payload

    results: list[dict[str, Any]] = []
    for file_type in sorted(set(file_types)):
        ft_mask = file_types == file_type
        if not ft_mask.any():
            continue
        train_dev_slice = ft_mask & train_dev_mask
        test_slice = ft_mask & test_mask
        n_mal_td = int(((labels == 1) & train_dev_slice).sum())
        n_mal_test = int(((labels == 1) & test_slice).sum())
        if n_mal_td < args.min_mal or n_mal_test < 1:
            continue

        # Discover routes present for this slice.
        present_routes: dict[str, np.ndarray] = {}
        for candidate_route in ("general",
                                f"filegroups/{rp['routes'].get(f'filetypes/{file_type}', {}).get('filegroup', '') or ''}",
                                f"filetypes/{file_type}"):
            if candidate_route in route_name_to_idx:
                idx = route_name_to_idx[candidate_route]
                row = scores[idx]
                if not np.all(np.isnan(row[ft_mask])):
                    present_routes[candidate_route] = row
        if len(present_routes) < 2:
            # Stacking on a single route is degenerate — falls back to that
            # route's threshold, which the OR-rule already finds.
            continue

        # Restrict to slice rows; fit_mask within slice excludes test +
        # rows missing any route's prob (NaN). LR fitting can't use rows
        # with NaN inputs.
        labels_slice = labels[ft_mask]
        train_dev_within_slice = train_dev_mask[ft_mask]
        slice_probs = {r: scores[route_name_to_idx[r]][ft_mask] for r in present_routes}
        valid_within = np.all(
            np.stack([~np.isnan(slice_probs[r]) for r in present_routes], axis=0),
            axis=0,
        )
        fit_mask = train_dev_within_slice & valid_within
        n_fit_mal = int(((labels_slice == 1) & fit_mask).sum())
        n_fit_ben = int(((labels_slice == 0) & fit_mask).sum())
        if n_fit_mal < 5 or n_fit_ben < 5:
            continue

        routes_fit, weights, intercept, blend = _fit_blend(
            slice_probs, labels_slice, fit_mask,
        )
        # blend is defined over the slice rows; test_within_slice picks
        # test rows for honest measurement.
        test_within_slice = ~train_dev_within_slice
        labels_test = labels_slice[test_within_slice]
        blend_test = blend[test_within_slice]
        blend_train_dev = blend[fit_mask]
        labels_train_dev = labels_slice[fit_mask]

        # Pareto-tune the threshold on the train+dev slice at each FP budget.
        # That threshold is what would deploy. Then apply it to test rows
        # to measure honest recall.
        per_fp: dict[int, dict[str, float | int | None]] = {}
        for fp in fp_targets:
            train_recall, threshold = _recall_at_fp(
                blend_train_dev, labels_train_dev, fp,
            )
            if threshold is None:
                per_fp[fp] = {
                    "threshold": None,
                    "train_recall": train_recall,
                    "test_recall": math.nan,
                    "test_fp": 0,
                    "test_tp": 0,
                }
                continue
            valid_test = ~np.isnan(blend_test)
            hit_test = valid_test & (blend_test >= threshold)
            test_tp = int(((labels_test == 1) & hit_test).sum())
            test_fp = int(((labels_test == 0) & hit_test).sum())
            n_mal_test_slice = int((labels_test == 1).sum())
            test_recall = test_tp / n_mal_test_slice if n_mal_test_slice else math.nan
            per_fp[fp] = {
                "threshold": float(threshold),
                "train_recall": train_recall,
                "test_recall": test_recall,
                "test_fp": test_fp,
                "test_tp": test_tp,
            }

        # Compare against the deployed OR-rule for this filetype at the
        # requested level. The deployed FP count on test will not generally
        # equal our fp_targets (the deployed policy was calibrated on the
        # full slice budget). Report it as-is.
        deployed_or_test: dict[str, Any] | None = None
        policy_payload = policies_by_filetype.get(file_type)
        if policy_payload:
            level_entry = next(
                (lvl for lvl in policy_payload["levels"]
                 if int(lvl["level"]) == args.level),
                None,
            )
            if level_entry and level_entry["hostile"]["best"]["thresholds"]:
                thresholds = level_entry["hostile"]["best"]["thresholds"]
                hit_or, valid_or = _apply_or_rule(
                    slice_probs, thresholds, test_within_slice,
                )
                or_tp = int(((labels_test == 1) & hit_or).sum())
                or_fp = int(((labels_test == 0) & hit_or).sum())
                n_mal_test_slice = int((labels_test == 1).sum())
                deployed_or_test = {
                    "policy": level_entry["hostile"]["best"]["policy"],
                    "test_tp": or_tp,
                    "test_fp": or_fp,
                    "test_recall": or_tp / n_mal_test_slice
                                   if n_mal_test_slice else math.nan,
                    "thresholds": thresholds,
                }

        results.append({
            "file_type": file_type,
            "n_mal_train_dev": n_mal_td,
            "n_mal_test": n_mal_test,
            "n_fit_mal": n_fit_mal,
            "n_fit_ben": n_fit_ben,
            "routes": routes_fit,
            "weights": weights.tolist(),
            "intercept": intercept,
            "per_fp": per_fp,
            "deployed_or_test": deployed_or_test,
        })

    results.sort(key=lambda r: -r["n_mal_test"])

    # Markdown report.
    lines: list[str] = [
        f"# Stacker Experiment vs Deployed OR-Rule (L{args.level} hostile)",
        "",
        "Stacker: logistic regression on `[logit(p_general), logit(p_group), logit(p_specialist)]`",
        "fit on train+dev rows where all routes have probs. Pareto-tune threshold to",
        "FP=K on the train+dev slice, then measure recall on test rows at that threshold.",
        "",
        "Deployed OR-rule: thresholds from the current `route_policies.json` for this filetype",
        f"at L{args.level} hostile, applied to the same test rows.",
        "",
        "**Caveat:** specialist probs are in-sample on train+dev (specialists trained on those",
        "rows), so the stacker fit is biased toward over-weighting the specialist. Test-side",
        "numbers are honest.",
        "",
        f"## Per-filetype recall on test (rows sorted by test malware count, ≥{args.min_mal} train+dev malware required)",
        "",
        "Columns: filetype, train+dev/test malware counts, deployed (test_fp/test_recall),",
        "then per-FP stacker numbers.",
        "",
    ]
    cols_per_fp = " | ".join(
        f"stacker test recall @ FP={k} | stacker test FP @ FP={k}"
        for k in fp_targets
    )
    header = (
        f"| filetype | n_mal_td | n_mal_test | deploy policy | deploy FP | deploy recall | {cols_per_fp} |"
    )
    lines.append(header)
    lines.append(
        "| --- | ---: | ---: | --- | ---: | ---: | "
        + " | ".join(["---: | ---:"] * len(fp_targets)) + " |"
    )

    def fmt(v: Any) -> str:
        if v is None:
            return "—"
        try:
            f = float(v)
        except (TypeError, ValueError):
            return str(v)
        if math.isnan(f):
            return "—"
        return f"{100*f:.1f}%"

    for r in results:
        dor = r["deployed_or_test"]
        deploy_policy = dor["policy"] if dor else "—"
        deploy_fp = dor["test_fp"] if dor else "—"
        deploy_recall = fmt(dor["test_recall"]) if dor else "—"
        per_fp_cells = []
        for k in fp_targets:
            cell = r["per_fp"][k]
            per_fp_cells.append(f"{fmt(cell['test_recall'])} | {cell['test_fp']}")
        lines.append(
            f"| {r['file_type']} | {r['n_mal_train_dev']} | {r['n_mal_test']} | "
            f"`{deploy_policy}` | {deploy_fp} | {deploy_recall} | "
            + " | ".join(per_fp_cells) + " |"
        )

    # Weighted-average summary across filetypes, weighted by test malware.
    lines.append("")
    lines.append("## Weighted-average test recall (heavy filetypes weighted higher)")
    lines.append("")
    lines.append(
        f"| FP budget | deployed test recall | stacker test recall | Δ |"
    )
    lines.append("| ---: | ---: | ---: | ---: |")

    summary: dict[int, dict[str, float | int]] = {}
    for k in fp_targets:
        total_mal_test = sum(r["n_mal_test"] for r in results
                             if r["per_fp"][k]["test_recall"] is not None
                             and not (isinstance(r["per_fp"][k]["test_recall"], float)
                                      and math.isnan(r["per_fp"][k]["test_recall"])))
        if total_mal_test == 0:
            lines.append(f"| {k} | — | — | — |")
            continue
        # Deployed recall is fixed (doesn't depend on k) — it's the test recall
        # of the deployed policy regardless of which FP budget the stacker
        # targets. Still weight the same way for apples-to-apples.
        deploy_caught = 0
        for r in results:
            dor = r["deployed_or_test"]
            if dor and dor["test_recall"] is not None and not (
                isinstance(dor["test_recall"], float) and math.isnan(dor["test_recall"])
            ):
                deploy_caught += int(r["n_mal_test"] * dor["test_recall"])
        stacker_caught = sum(
            int(r["n_mal_test"] * r["per_fp"][k]["test_recall"])
            for r in results
            if r["per_fp"][k]["test_recall"] is not None
            and not (isinstance(r["per_fp"][k]["test_recall"], float)
                     and math.isnan(r["per_fp"][k]["test_recall"]))
        )
        deploy_rate = deploy_caught / total_mal_test
        stacker_rate = stacker_caught / total_mal_test
        delta = stacker_rate - deploy_rate
        lines.append(
            f"| {k} | {100*deploy_rate:.2f}% | {100*stacker_rate:.2f}% | {100*delta:+.2f} |"
        )
        summary[k] = {
            "deployed_recall": deploy_rate,
            "stacker_recall": stacker_rate,
            "delta_pp": delta * 100,
            "n_mal_test": total_mal_test,
        }

    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text("\n".join(lines) + "\n")
    args.output_json.write_text(json.dumps({
        "level": args.level,
        "fp_targets": list(fp_targets),
        "filetypes": results,
        "summary": summary,
    }, default=lambda o: float(o) if hasattr(o, "tolist") else None, indent=2) + "\n")

    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    print()
    print("Headline numbers (weighted by test malware count):")
    for k in fp_targets:
        s = summary.get(k)
        if not s:
            print(f"  FP={k}: no resolvable filetypes")
            continue
        print(
            f"  FP={k}: deployed={100*s['deployed_recall']:.2f}%  "
            f"stacker={100*s['stacker_recall']:.2f}%  Δ={s['delta_pp']:+.2f}pp "
            f"(over {s['n_mal_test']:,} test malware)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
