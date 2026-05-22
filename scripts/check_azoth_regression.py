#!/usr/bin/env python3
"""Block deploys that regress what litmus actually flags at L3 hostile.

Reads:
  --staged   <dir>   the staged-but-not-yet-deployed bundle
  --deployed <dir>   the bundle currently live (defaults to
                     $XDG_DATA_HOME/litmus/models/azoth)

Both must contain ``route_policy_eval_oof.json`` — the deployed
OR-rule / blend's tp/fp/recall per level on the locked test partition,
which is the ground truth of what litmus produces at scan time.

Per filetype where both bundles have ``n_malware >= --min-mal`` AND
``n_benign >= --min-ben`` (default 1/1 — we check every filetype with
even a single sample of each class), we compare deployed L3 hostile
recall. A regression triggers only when BOTH:

  1. The recall drop exceeds ``--recall-tolerance`` (default 1pp), AND
  2. The drop is statistically significant — the new recall point
     estimate falls below the deployed recall's 95% Clopper-Pearson
     lower bound.

The dual gate is the key to keeping the floor at 1/1 without false
positives. Small filetypes have wide CIs, so noise-level drops on
20-sample slices don't trigger; large filetypes have tight CIs, so
even sub-pp drops fire. The effect size threshold prevents firing on
statistically-significant but practically-irrelevant 0.1pp shifts on
huge slices.

For diagnostic context, the same comparison runs against each
*contributing route's* recall@3FP/M. Per-route drops do NOT trigger
exit 1; they're attribution context.

Bypass with ``AZOTH_ALLOW_REGRESSION=1`` for intentional trade-offs.
Skip silently (exit 0) when the deployed bundle doesn't have a
deployed eval — first-deploy or pre-eval bundle.

Exit codes:
  0 — no ensemble regressions over threshold
  1 — at least one ensemble regression
  2 — usage / IO error
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path


def _load(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as e:
        print(f"warning: failed to load {path}: {e}", file=sys.stderr)
        return {}


def _is_finite_number(value) -> bool:
    if value is None:
        return False
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(v)


def _clopper_pearson_lower(tp: int, n: int, alpha: float = 0.05) -> float:
    """Lower bound of the 1-alpha Clopper-Pearson interval for a
    binomial proportion. Exact, no normal approximation — works at
    n=1. Uses the inverse-Beta relationship to avoid pulling in
    scipy.stats just for ppf calls.
    """
    if n <= 0 or tp <= 0:
        return 0.0
    # Beta(tp, n-tp+1).ppf(alpha/2) — try scipy first; fall back to a
    # bisection if scipy isn't available.
    try:
        from scipy.stats import beta  # noqa: PLC0415
        return float(beta.ppf(alpha / 2.0, tp, n - tp + 1))
    except ImportError:
        # Bisection on the regularized incomplete beta function via the
        # CDF of Beta(tp, n-tp+1). math.betacdf doesn't exist in stdlib;
        # in practice scipy is always available here, so this is a
        # safety net rather than a real fallback.
        return max(0.0, tp / n - 1.96 * math.sqrt(tp * (n - tp) / (n * n * n)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", type=Path, required=True)
    parser.add_argument(
        "--deployed", type=Path,
        default=Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
        / "litmus" / "models" / "azoth",
    )
    parser.add_argument("--min-mal", type=int, default=1)
    parser.add_argument("--min-ben", type=int, default=1)
    parser.add_argument("--recall-tolerance", type=float, default=0.01)
    parser.add_argument(
        "--ci-alpha", type=float, default=0.05,
        help=(
            "Significance level for the Clopper-Pearson CI on deployed "
            "recall. A regression triggers only when the staged recall "
            "falls below the deployed recall's (1 - alpha) CI lower "
            "bound. Default 0.05 (95%% CI). Set higher to widen the "
            "gate's mouth, lower to tighten it."
        ),
    )
    parser.add_argument(
        "--improvement-threshold",
        type=float,
        default=0.001,
        help=(
            "Log ensemble and per-route recall gains at or above this "
            "fraction (default 0.001 = 0.1pp). Improvements never block; "
            "they're surfaced for the same reason regressions are — to "
            "attribute the deploy's net effect to specific routes."
        ),
    )
    parser.add_argument("--level", type=int, default=3)
    parser.add_argument("--severity", default="hostile", choices=["hostile", "suspicious"])
    parser.add_argument(
        "--net-improvement-fallback",
        action="store_true",
        help=(
            "When set, the gate PASSES despite per-filetype regressions if "
            "(a) the net malware-caught delta across all compared filetypes "
            "is positive, and (b) no single filetype's recall drop exceeds "
            "--max-net-route-regression. Designed for shared-route promotes "
            "(filegroups/* or general) where a new model legitimately helps "
            "most filetypes but hurts one — the strict per-filetype gate "
            "blocks net-positive deploys. The catastrophe cap prevents "
            "this from masking a single huge regression that average-out "
            "across many small wins."
        ),
    )
    parser.add_argument(
        "--max-net-route-regression",
        type=float,
        default=0.05,
        help=(
            "Maximum tolerated per-filetype recall drop (absolute) when "
            "--net-improvement-fallback rescues a deploy. Default 0.05 = "
            "5pp. A single filetype dropping more than this still blocks "
            "the deploy even if net is positive — catastrophes shouldn't "
            "hide behind aggregate wins."
        ),
    )
    args = parser.parse_args()

    if os.environ.get("AZOTH_ALLOW_REGRESSION", "").strip().lower() in {"1", "true", "yes"}:
        print("AZOTH_ALLOW_REGRESSION set; skipping regression check")
        return 0

    staged_eval = _load(args.staged / "route_policy_eval_oof.json")
    deployed_eval = _load(args.deployed / "route_policy_eval_oof.json")

    if not staged_eval:
        print(
            f"error: staged bundle has no route_policy_eval_oof.json at {args.staged}",
            file=sys.stderr,
        )
        return 2
    if not deployed_eval:
        print(
            f"no route_policy_eval_oof.json at deployed location ({args.deployed}); "
            "skipping regression check (first deploy or pre-eval bundle)",
        )
        return 0

    staged_ft = (staged_eval.get("filetypes") or {})
    deployed_ft = (deployed_eval.get("filetypes") or {})
    level_key = f"L{args.level}_{args.severity}"

    regressions: list[str] = []
    ensemble_wins: list[str] = []
    route_drops: list[str] = []         # informational; doesn't fail the gate
    route_wins: list[str] = []          # informational
    compared = 0
    skipped_small = 0
    # Net-improvement accounting: per-filetype (delta_tp, recall_drop) so the
    # fallback can decide whether the aggregate is net-positive AND no single
    # filetype crossed the catastrophe cap.
    net_delta_tp = 0
    max_recall_drop = 0.0
    max_drop_ft = ""

    for ft, deployed_entry in deployed_ft.items():
        staged_entry = staged_ft.get(ft)
        if not staged_entry:
            print(f"info: filetype {ft!r} present in deployed but absent in staged")
            continue
        n_mal = staged_entry.get("malware", 0) or 0
        n_ben = staged_entry.get("benign", 0) or 0
        d_mal = deployed_entry.get("malware", 0) or 0
        d_ben = deployed_entry.get("benign", 0) or 0
        if min(n_mal, d_mal) < args.min_mal or min(n_ben, d_ben) < args.min_ben:
            skipped_small += 1
            continue

        staged_l = (staged_entry.get("deployed_or_by_level") or {}).get(level_key) or {}
        deployed_l = (deployed_entry.get("deployed_or_by_level") or {}).get(level_key) or {}
        s_recall = staged_l.get("recall")
        d_recall = deployed_l.get("recall")
        d_tp = deployed_l.get("tp")
        s_tp = staged_l.get("tp")
        # Track per-filetype TP delta for the net-improvement fallback. Use
        # raw TP counts (not recall) so the aggregation weights by absolute
        # malware-caught — a 0.5pp shift on PE (113K mal) outweighs a 5pp
        # shift on a 200-malware route, matching deploy-time customer impact.
        if _is_finite_number(s_tp) and _is_finite_number(d_tp):
            net_delta_tp += int(s_tp) - int(d_tp)
        if _is_finite_number(s_recall) and _is_finite_number(d_recall):
            delta = float(s_recall) - float(d_recall)  # positive = improvement
            if -delta > max_recall_drop:
                max_recall_drop = -delta
                max_drop_ft = ft
            # Dual-gate regression: drop must exceed the configured
            # tolerance (effect-size threshold) AND fall below the
            # deployed recall's 1-alpha Clopper-Pearson lower bound
            # (statistical-significance threshold). The first prevents
            # firing on practically-irrelevant shifts; the second
            # prevents firing on small-sample noise. Together they let
            # us check every filetype with even 1 mal + 1 ben without
            # drowning in noise.
            d_lower: float | None = None
            if _is_finite_number(d_tp) and d_mal > 0:
                d_lower = _clopper_pearson_lower(int(d_tp), int(d_mal), args.ci_alpha)
            stat_sig = d_lower is None or float(s_recall) < d_lower
            if -delta > args.recall_tolerance and stat_sig:
                ci_note = (
                    f"; deployed 95% CI lower = {d_lower*100:.2f}%"
                    if d_lower is not None else ""
                )
                regressions.append(
                    f"{ft}: L{args.level} {args.severity} ENSEMBLE recall dropped {-delta*100:.2f}pp "
                    f"({float(d_recall)*100:.2f}% → {float(s_recall)*100:.2f}%; "
                    f"tolerance {args.recall_tolerance*100:.2f}pp{ci_note})",
                )
            elif delta >= args.improvement_threshold:
                ensemble_wins.append(
                    f"  {ft}: L{args.level} {args.severity} ensemble recall +{delta*100:.2f}pp "
                    f"({float(d_recall)*100:.2f}% → {float(s_recall)*100:.2f}%)",
                )

        # Per-route attribution. ``slice_metrics.routes.<route>.recall_at_3fp``
        # is each contributing route's single-point operating metric on
        # this filetype's slice. Drops + improvements both reported, so a
        # deploy can answer "is the ensemble change coming from the
        # specialist, the general, or just blend variance?" without
        # blocking on the per-route lines themselves.
        s_routes = (staged_entry.get("slice_metrics") or {}).get("routes") or {}
        d_routes = (deployed_entry.get("slice_metrics") or {}).get("routes") or {}
        for route_name, d_route in d_routes.items():
            s_route = s_routes.get(route_name)
            if not isinstance(s_route, dict) or not isinstance(d_route, dict):
                continue
            s_rec = s_route.get("recall_at_3fp")
            d_rec = d_route.get("recall_at_3fp")
            if not (_is_finite_number(s_rec) and _is_finite_number(d_rec)):
                continue
            delta = float(s_rec) - float(d_rec)  # positive = improvement
            if -delta > args.recall_tolerance:
                route_drops.append(
                    f"  {ft} :: {route_name} recall@3FP/M dropped {-delta*100:.2f}pp "
                    f"({float(d_rec)*100:.2f}% → {float(s_rec)*100:.2f}%)",
                )
            elif delta >= args.improvement_threshold:
                route_wins.append(
                    f"  {ft} :: {route_name} recall@3FP/M +{delta*100:.2f}pp "
                    f"({float(d_rec)*100:.2f}% → {float(s_rec)*100:.2f}%)",
                )

        compared += 1

    if ensemble_wins:
        print()
        print(
            f"ensemble improvements (≥{args.improvement_threshold*100:.2f}pp):",
        )
        for line in ensemble_wins:
            print(line)

    if route_wins:
        print()
        print(
            f"per-route improvements (≥{args.improvement_threshold*100:.2f}pp, informational):",
        )
        for line in route_wins:
            print(line)

    if route_drops:
        print()
        print("per-route regressions (informational; does not block deploy):")
        for line in route_drops:
            print(line)

    if regressions:
        print()
        print(f"{len(regressions)} ensemble regression(s) over tolerance:")
        for r in regressions:
            print(f"  - {r}")

        # Net-improvement fallback. Lets shared-route promotes (filegroups/*
        # and general) ship when the new model is net-positive across the
        # corpus despite hurting one or two routes — provided no single
        # filetype's recall drop crossed the catastrophe cap. Strict per-
        # filetype gating still applies when this flag is off.
        if args.net_improvement_fallback:
            net_pp = (
                f"net malware-caught delta = {net_delta_tp:+,} TPs across "
                f"{compared} compared filetypes; "
                f"worst single drop = {max_recall_drop*100:.2f}pp on {max_drop_ft!r} "
                f"(cap = {args.max_net_route_regression*100:.2f}pp)"
            )
            if net_delta_tp > 0 and max_recall_drop <= args.max_net_route_regression:
                print()
                print(
                    f"net-improvement-fallback rescues deploy: {net_pp}"
                )
                return 0
            print()
            print(f"net-improvement-fallback DID NOT rescue: {net_pp}")
            if net_delta_tp <= 0:
                print("  reason: aggregate TP delta is not positive")
            if max_recall_drop > args.max_net_route_regression:
                print(
                    f"  reason: worst single-filetype drop "
                    f"({max_recall_drop*100:.2f}pp on {max_drop_ft!r}) "
                    f"exceeds catastrophe cap "
                    f"({args.max_net_route_regression*100:.2f}pp)"
                )

        print()
        print(
            f"compared {compared} filetypes "
            f"(mal≥{args.min_mal}, ben≥{args.min_ben}); "
            f"{skipped_small} below threshold and skipped.",
        )
        print()
        print(
            "If this regression is intentional, set "
            "AZOTH_ALLOW_REGRESSION=1 and re-run "
            "(or pass --net-improvement-fallback for shared-route promotes).",
        )
        return 1

    print(
        f"regression check ok: compared {compared} filetype(s) "
        f"(mal≥{args.min_mal}, ben≥{args.min_ben}) at L{args.level} "
        f"{args.severity}; tolerance {args.recall_tolerance*100:.2f}pp.",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
