#!/usr/bin/env python3
"""Analyze the corpus-FP budget curve for azoth route policies.

The L9 hostile target is 9 FP/M, which is a deployment SLA the team
doesn't want to relax. But at 9 FP/M the long tail of filetypes (shell,
ole, php, ...) gets shut out by the knapsack: PE alone consumes 6 of 24
FPs at 100k tp/FP, leaving nothing for routes whose marginal value is
1-3k tp/FP.

This script enumerates the corpus-FP knapsack at a range of target FP/M
values and reports:

* total TP catchable (full corpus and projected per-million-rows),
* marginal TP per added FP,
* which filetype gained its first non-no_policy operating point at
  each FP/M boundary.

That tells the team:

1. Where the marginal-TP curve elbows out (the natural break for an
   additional severity tier — e.g., L10 at 18 or 36 FP/M).
2. How many filetypes each FP/M tier would unlock (the "coverage gain"
   that justifies the tier).

We do NOT loosen L9 — we just measure what an L10/L11 tier WOULD buy
if we added one. The numbers come from the existing candidate set
already in route_policies.json, so no recalibration is needed.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _knapsack(
    routes: list[tuple[str, list[dict[str, Any]]]],
    budget: int,
) -> dict[int, tuple[int, list[tuple[str, dict[str, Any]]]]]:
    """Multi-choice knapsack: pick one candidate per route, max TP under
    budget, return the full dp table keyed by total FP.

    Skips ``dominated_by_specialist`` candidates (they're identical to
    the recall-monotone floor in azoth_route_policy_search.py).
    """
    dp: dict[int, tuple[int, list[tuple[str, dict[str, Any]]]]] = {0: (0, [])}
    for route_name, candidates in routes:
        eligible = [c for c in candidates if not c.get("dominated_by_specialist")]
        if not any(int(c.get("fp", 0)) == 0 and int(c.get("tp", 0)) == 0 for c in eligible):
            eligible.append({"policy": "no_policy", "fp": 0, "tp": 0, "thresholds": {}})
        next_dp: dict[int, tuple[int, list[tuple[str, dict[str, Any]]]]] = {}
        for used_fp, (used_tp, choices) in dp.items():
            for candidate in eligible:
                fp = used_fp + int(candidate.get("fp", 0))
                if fp > budget:
                    continue
                tp = used_tp + int(candidate.get("tp", 0))
                current = next_dp.get(fp)
                if current is None or tp > current[0]:
                    next_dp[fp] = (tp, choices + [(route_name, candidate)])
        dp = next_dp or dp
    return dp


def _aggregate_unique_filetypes_active(
    choices: list[tuple[str, dict[str, Any]]],
) -> int:
    return sum(
        1 for _route_name, c in choices
        if c.get("policy") != "no_policy" and int(c.get("tp", 0)) > 0
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--route-policies",
        type=Path,
        default=Path("out/models/azoth/route_policies.json"),
    )
    parser.add_argument(
        "--severity",
        choices=("hostile", "suspicious"),
        default="hostile",
    )
    parser.add_argument(
        "--level",
        type=int,
        default=9,
        help="Calibration level whose candidate set to use (default 9).",
    )
    parser.add_argument(
        "--fpm-targets",
        type=str,
        default="3,5,9,18,36,72,144,288,576",
        help=(
            "Comma-separated FP/M targets to sweep. Default spans L9 "
            "(9 FP/M) up to ~600 FP/M for marginal-curve analysis."
        ),
    )
    args = parser.parse_args()

    with open(args.route_policies) as f:
        rp = json.load(f)
    total_benign = int(rp["benign"])
    total_malware = int(rp["malware"])
    fpm_targets = [float(x) for x in args.fpm_targets.split(",")]

    routes_for_knapsack: list[tuple[str, list[dict[str, Any]]]] = []
    for route_name, route in rp["routes"].items():
        level_entry = next(
            (lvl for lvl in route["levels"] if int(lvl["level"]) == args.level),
            None,
        )
        if level_entry is None:
            continue
        candidates = list(level_entry[args.severity].get("candidates", []))
        if not candidates:
            continue
        routes_for_knapsack.append((route_name, candidates))

    # The candidate set was calibrated for the chosen level (9 by
    # default). FP counts on those candidates aren't tied to any
    # particular FP/M target — they're just operating points the
    # calibrator found. Reusing them across budget sweeps is valid: a
    # bigger budget simply lets the knapsack pick more / higher-FP
    # candidates from the same set.
    print(f"# Corpus benign: {total_benign:,}")
    print(f"# Corpus malware: {total_malware:,}")
    print(f"# Routes considered: {len(routes_for_knapsack)}")
    print(f"# Source: L{args.level} {args.severity} candidate set")
    print()

    rows: list[OrderedDict[str, Any]] = []
    prev_tp = 0
    prev_fp = 0
    seen_routes: set[str] = set()
    for fpm in fpm_targets:
        budget = int(math.floor(total_benign * fpm / 1_000_000.0))
        dp = _knapsack(routes_for_knapsack, budget)
        best_fp, (best_tp, best_choices) = max(
            dp.items(), key=lambda item: (item[1][0], -item[0]),
        )
        active = _aggregate_unique_filetypes_active(best_choices)
        # Marginal: TP gained per FP added at this tier.
        marginal_tp = best_tp - prev_tp
        marginal_fp = best_fp - prev_fp
        marginal_per_fp = marginal_tp / max(marginal_fp, 1)
        # Routes that gained an operating point at this tier.
        newly_active = []
        active_now = set()
        for route_name, c in best_choices:
            if c.get("policy") != "no_policy" and int(c.get("tp", 0)) > 0:
                active_now.add(route_name)
                if route_name not in seen_routes:
                    newly_active.append(route_name.replace("filetypes/", ""))
        seen_routes |= active_now
        rows.append(OrderedDict([
            ("fpm_target", fpm),
            ("budget_fp", budget),
            ("used_fp", best_fp),
            ("total_tp", best_tp),
            ("recall_fraction", best_tp / max(total_malware, 1)),
            ("marginal_tp_per_fp", marginal_per_fp),
            ("active_filetypes", active),
            ("newly_active", newly_active),
        ]))
        prev_tp = best_tp
        prev_fp = best_fp

    # Print table.
    header = (
        f"{'FP/M':>6}  {'budget':>6}  {'used':>5}  {'tp':>9}  "
        f"{'recall':>7}  {'Δtp/FP':>9}  {'#fts':>5}  newly_active"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        nf = (
            ",".join(row["newly_active"][:6])
            + ("..." if len(row["newly_active"]) > 6 else "")
        )
        print(
            f"{row['fpm_target']:>6.1f}  {row['budget_fp']:>6}  "
            f"{row['used_fp']:>5}  {row['total_tp']:>9,}  "
            f"{row['recall_fraction']*100:>6.2f}%  "
            f"{row['marginal_tp_per_fp']:>9,.0f}  "
            f"{row['active_filetypes']:>5}  {nf}"
        )

    # Compact JSON dump alongside the table for downstream parsing.
    out_path = args.route_policies.with_name("budget_sensitivity.json")
    out_path.write_text(json.dumps(rows, indent=2) + "\n")
    print()
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
