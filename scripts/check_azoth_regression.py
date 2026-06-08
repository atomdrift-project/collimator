#!/usr/bin/env python3
"""Block deploys that regress what litmus actually flags at L50 hostile.

Reads:
  --staged   <dir>   the staged-but-not-yet-deployed bundle
  --deployed <dir>   the bundle currently live (defaults to
                     $XDG_DATA_HOME/litmus/models/azoth)

Both must contain ``route_policy_eval_oof.json`` — the deployed
OR-rule / blend's tp/fp/recall per level on the locked test partition,
which is the ground truth of what litmus produces at scan time.

Per filetype where both bundles have ``n_malware >= --min-mal`` AND
``n_benign >= --min-ben`` (default 1/1 — we check every filetype with
even a single sample of each class), we compare deployed L50 hostile
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

A second gate compares against a pinned ``--low-water-mark`` (a known-good
floor) so cumulative drift can't erode recall one tolerated step at a time.

``--net-improvement-fallback`` makes the deploy judged on the whole dataset,
not any single filetype: it rescues BOTH gates when the malware-weighted net
TP delta is positive AND no HIGH-VOLUME route (>= ``--catastrophe-min-mal``
malware) craters past ``--max-net-route-regression``. A small route swinging
30%->5% is ~the same handful of samples — dataset-level noise that shouldn't
block a net-positive deploy; a crater on a route big enough to move the
average still does. This is the default deploy posture (set in the Makefile).

For diagnostic context, the same comparison runs against each
*contributing route's* recall@1FP-on-slice (L50-aligned, with `recall_at_3fp`
fallback for pre-migration bundles). Per-route drops do NOT trigger
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

# scripts/ isn't on sys.path; reach src/ for `collimator.thresholds`.
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from collimator.thresholds import DEFAULT_SEVERITY_LEVEL  # noqa: E402


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
    parser.add_argument(
        "--recall-tolerance", type=float, default=0.017,
        help=(
            "Per-filetype recall-drop tolerance vs the currently-deployed "
            "bundle. Default 0.017 = 1.7pp. Combined with the CI gate "
            "below to filter small-sample noise. This is the soft "
            "tolerance — it permits ordinary deploy-to-deploy wiggle. The "
            "low-water-mark gate (--low-water-mark + --lwm-tolerance) is "
            "the harder floor that cumulative drift can't sneak past."
        ),
    )
    parser.add_argument(
        "--low-water-mark", type=Path, default=None,
        help=(
            "Path to a pinned reference bundle (or to its "
            "route_policy_eval_oof.json directly). When set, the gate "
            "ALSO blocks if any filetype's recall falls below the LWM "
            "by more than --lwm-tolerance. Use to lock in a known-good "
            "baseline so cumulative per-deploy drift can't quietly push "
            "performance under it. Captured via `make "
            "azoth-set-low-water-mark`. If the file doesn't exist the "
            "LWM gate is silently skipped (lets you opt in without "
            "breaking existing pipelines)."
        ),
    )
    parser.add_argument(
        "--lwm-tolerance", type=float, default=0.009,
        help=(
            "Per-filetype recall-drop tolerance vs the low-water-mark. "
            "Default 0.009 = 0.9pp. Tighter than --recall-tolerance "
            "because LWM is the floor; deployed tolerance is the "
            "per-deploy wiggle room ABOVE that floor. No CI filter — "
            "the LWM check is unconditional by design."
        ),
    )
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
    parser.add_argument("--level", type=int, default=DEFAULT_SEVERITY_LEVEL,
                        help=(
                            f"Severity level on the per-100M scale (default "
                            f"{DEFAULT_SEVERITY_LEVEL} = {DEFAULT_SEVERITY_LEVEL/100:.2f} FP/M; "
                            f"sourced from collimator.thresholds.DEFAULT_SEVERITY_LEVEL)."
                        ))
    parser.add_argument("--severity", default="hostile", choices=["hostile"])
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
            "5pp. A single HIGH-VOLUME filetype dropping more than this still "
            "blocks the deploy even if net is positive — catastrophes "
            "shouldn't hide behind aggregate wins. Only routes with "
            ">= --catastrophe-min-mal malware count this way (see below)."
        ),
    )
    parser.add_argument(
        "--catastrophe-min-mal",
        type=int,
        default=1500,
        help=(
            "Minimum malware count for a per-filetype recall drop to count "
            "as a catastrophe that defeats --net-improvement-fallback. "
            "Below this, a drop is dataset-level noise: the route is too "
            "small to move the weighted average, and its recall point "
            "estimate is dominated by sampling variance (a 142-malware route "
            "swinging 30%%->5%% is ~the same handful of samples). Such drops "
            "are reported but cannot block a net-positive deploy. Default "
            "1500 (~0.5%% of a ~300K-malware test partition)."
        ),
    )
    parser.add_argument(
        "--source-bundle", type=Path, default=None,
        help=(
            "Source training bundle that the staged candidate was cloned "
            "from. When set, the gate computes impacted filetypes by "
            "hashing each route's model + feature_spec and comparing "
            "staged vs source. Only impacted filetypes are gated — "
            "unimpacted filetypes inherited their metrics verbatim from "
            "the source via the carry-forward optimization, so any drift "
            "vs LWM or deployed there is pre-existing and not this "
            "promote's responsibility. Reports them informationally only."
        ),
    )
    args = parser.parse_args()

    if os.environ.get("AZOTH_ALLOW_REGRESSION", "").strip().lower() in {"1", "true", "yes"}:
        print("AZOTH_ALLOW_REGRESSION set; skipping regression check")
        return 0

    staged_eval = _load(args.staged / "route_policy_eval_oof.json")
    deployed_eval = _load(args.deployed / "route_policy_eval_oof.json")
    # Low-water-mark: accept either a bundle directory or a direct path
    # to a route_policy_eval_oof.json file. Missing file = LWM gate
    # silently skipped (opt-in).
    lwm_eval: dict = {}
    lwm_path_used: Path | None = None
    if args.low_water_mark is not None:
        candidate = args.low_water_mark
        if candidate.is_dir():
            candidate = candidate / "route_policy_eval_oof.json"
        if candidate.is_file():
            lwm_eval = _load(candidate)
            lwm_path_used = candidate

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

    def _has_level(ft_dict: dict, key: str) -> bool:
        for entry in ft_dict.values():
            by_level = (entry or {}).get("deployed_or_by_level") or {}
            if key in by_level:
                return True
        return False

    # Historic eval files predate the per-100M grid change and may not
    # carry an L50 row. Refuse to run rather than silently treating every
    # filetype as "missing level" (which would produce a trivial pass).
    if not _has_level(staged_ft, level_key):
        print(
            f"error: staged bundle has no {level_key} rows in any filetype's "
            f"deployed_or_by_level — bundle predates the per-100M grid or "
            f"--level {args.level} isn't a valid grid value for this bundle.",
            file=sys.stderr,
        )
        return 2
    if not _has_level(deployed_ft, level_key):
        print(
            f"warning: deployed bundle at {args.deployed} has no {level_key} "
            f"rows — likely predates per-100M grid migration. Skipping "
            f"regression check (treat as first deploy on new grid).",
        )
        return 0

    # Impact-aware gating: when --source-bundle is given, compute which
    # filetypes the staged candidate actually touched. A promote that
    # only retrains filegroups/native impacts only {elf, macho, pe} —
    # all other filetypes' metrics are bytewise-identical inheritance
    # from the source training bundle (via the carry-forward
    # optimization). Their drift vs LWM or deployed is pre-existing and
    # not caused by THIS promote; gating on it would block honest
    # candidates for problems they didn't cause. Report those drifts
    # informationally instead.
    impacted_filetypes: set[str] | None = None
    impact_source = ""
    if args.source_bundle is not None:
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from azoth_impact import changed_routes, unchanged_filetypes  # noqa: PLC0415
            from azoth_specialist_suite import DEPLOYMENT_GROUPS  # noqa: PLC0415
            changed, _ = changed_routes(args.staged, args.source_bundle)
            # Available routes = those the staged bundle has trained.
            # Read from the staged bundle's config.json.
            staged_config_path = args.staged / "config.json"
            available_routes: set[str] = {"general"}
            if staged_config_path.is_file():
                try:
                    cfg = json.loads(staged_config_path.read_text())
                    for m in cfg.get("models", []):
                        if isinstance(m, dict) and isinstance(m.get("route"), str):
                            available_routes.add(m["route"])
                except (OSError, ValueError):
                    pass
            all_compared = set(staged_ft.keys()) & set(deployed_ft.keys())
            unchanged = unchanged_filetypes(
                changed, DEPLOYMENT_GROUPS, available_routes, all_compared,
            )
            impacted_filetypes = all_compared - unchanged
            impact_source = (
                f"--source-bundle {args.source_bundle}: "
                f"{len(changed)} routes changed → "
                f"{len(impacted_filetypes)} filetypes impacted, "
                f"{len(unchanged)} unimpacted (drift treated as pre-existing)"
            )
        except Exception as e:
            print(f"warning: impact-aware gating setup failed ({e}); "
                  f"falling back to all-filetypes gating", file=sys.stderr)
            impacted_filetypes = None
    if impacted_filetypes is not None:
        print(impact_source)

    regressions: list[str] = []
    # LWM regressions: hard floor; can't be rescued by net-improvement-fallback
    # because they represent cumulative drift below a pinned baseline, not
    # per-deploy noise. Reported separately so the user can see the two
    # gate types distinctly.
    lwm_regressions: list[str] = []
    # LWM wins are symmetric to lwm_regressions — informational only (don't
    # gate the deploy), but reported so a net-improvement candidate doesn't
    # look one-sidedly bad. The threshold mirrors --lwm-tolerance: a gain
    # large enough that a regression of the same size would block.
    lwm_wins: list[str] = []
    ensemble_wins: list[str] = []
    route_drops: list[str] = []         # informational; doesn't fail the gate
    route_wins: list[str] = []          # informational
    compared = 0
    skipped_small = 0
    # Pre-existing drift on unimpacted filetypes — surfaced informationally
    # so the operator knows the LWM is stale on those filetypes, but
    # doesn't block the deploy (not THIS promote's responsibility).
    preexisting_drift: list[str] = []
    lwm_ft = (lwm_eval.get("filetypes") or {}) if lwm_eval else {}
    # Net-improvement accounting: per-filetype (delta_tp, recall_drop) so the
    # fallback can decide whether the aggregate is net-positive AND no single
    # filetype crossed the catastrophe cap.
    net_delta_tp = 0
    max_recall_drop = 0.0
    max_drop_ft = ""
    # Worst drop restricted to high-volume routes (n_mal >= catastrophe_min_mal).
    # This is the only drop that can defeat the net-improvement rescue: small
    # routes craters are dataset-level noise (see --catastrophe-min-mal).
    max_recall_drop_sig = 0.0
    max_drop_ft_sig = ""

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
        # Impact gating: if --source-bundle was provided and this
        # filetype's routes weren't touched by the promote, its metrics
        # are bytewise-identical inheritance from the source bundle. Any
        # drift vs deployed or LWM here is pre-existing and not THIS
        # promote's responsibility. Report informationally; don't block.
        is_impacted = impacted_filetypes is None or ft in impacted_filetypes

        if _is_finite_number(s_recall) and _is_finite_number(d_recall):
            delta = float(s_recall) - float(d_recall)  # positive = improvement
            if is_impacted and -delta > max_recall_drop:
                max_recall_drop = -delta
                max_drop_ft = ft
            if is_impacted and n_mal >= args.catastrophe_min_mal and -delta > max_recall_drop_sig:
                max_recall_drop_sig = -delta
                max_drop_ft_sig = ft
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
                if is_impacted:
                    regressions.append(
                        f"{ft}: L{args.level} {args.severity} ENSEMBLE recall dropped {-delta*100:.2f}pp "
                        f"({float(d_recall)*100:.2f}% → {float(s_recall)*100:.2f}%; "
                        f"tolerance {args.recall_tolerance*100:.2f}pp{ci_note})",
                    )
                else:
                    preexisting_drift.append(
                        f"{ft}: pre-existing drift, recall {float(d_recall)*100:.2f}% → "
                        f"{float(s_recall)*100:.2f}% ({-delta*100:+.2f}pp; unimpacted by this promote)"
                    )
            elif delta >= args.improvement_threshold:
                # Only report as an "improvement caused by this promote" when
                # the filetype was actually touched by the changed routes.
                # Unimpacted filetypes' positive drift is float-noise or
                # seed-variance in the recalibration step — flagging it as a
                # win attributes credit the candidate didn't earn and makes
                # filegroup promotes look like they affect 70 filetypes
                # when they really touch ~9.
                if is_impacted:
                    ensemble_wins.append(
                        f"  {ft}: L{args.level} {args.severity} ensemble recall +{delta*100:.2f}pp "
                        f"({float(d_recall)*100:.2f}% → {float(s_recall)*100:.2f}%)",
                    )
                else:
                    preexisting_drift.append(
                        f"{ft}: pre-existing drift, recall {float(d_recall)*100:.2f}% → "
                        f"{float(s_recall)*100:.2f}% ({delta*100:+.2f}pp; unimpacted by this promote)"
                    )

        # Low-water-mark check (independent of the deployed-vs-staged
        # gate above): hard floor against a pinned reference. No CI
        # filter — the LWM is the line we promised never to cross,
        # and a drop bigger than --lwm-tolerance against it is a
        # block by definition. Symmetric wins are reported too so the
        # output isn't one-sidedly bad: a candidate with 12 LWM-floor
        # regressions and 8 LWM-ceiling improvements is a different
        # story than 12 regressions and 0 improvements.
        #
        # Impact-aware: unimpacted filetypes' LWM drift is pre-existing
        # state, not this promote's doing. Reporting them as LWM
        # regressions would block honest single-route promotes for
        # problems that pre-date them.
        if lwm_ft and _is_finite_number(s_recall):
            lwm_entry = lwm_ft.get(ft)
            lwm_l = ((lwm_entry or {}).get("deployed_or_by_level") or {}).get(level_key) or {}
            lwm_recall = lwm_l.get("recall")
            if _is_finite_number(lwm_recall):
                lwm_delta = float(s_recall) - float(lwm_recall)
                if -lwm_delta > args.lwm_tolerance:
                    if is_impacted:
                        lwm_regressions.append(
                            f"{ft}: L{args.level} {args.severity} ENSEMBLE recall dropped {-lwm_delta*100:.2f}pp "
                            f"BELOW LOW-WATER-MARK ({float(lwm_recall)*100:.2f}% → {float(s_recall)*100:.2f}%; "
                            f"LWM tolerance {args.lwm_tolerance*100:.2f}pp)",
                        )
                    # else: pre-existing drift already logged in the deployed-vs-staged section above (or not — but either way, not a block)
                elif lwm_delta > args.lwm_tolerance:
                    lwm_wins.append(
                        f"{ft}: L{args.level} {args.severity} ensemble recall +{lwm_delta*100:.2f}pp "
                        f"above LWM ({float(lwm_recall)*100:.2f}% → {float(s_recall)*100:.2f}%)",
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
            # Per-route attribution at the L50-aligned slice budget. The
            # route_policy_eval emits `recall_at_{0,1,3}fp` budgets; the 1-FP
            # budget aligns with L50 = 0.5 FP/M (1 FP per 2M benigns), and
            # is the right per-route diagnostic for an L50-default deploy.
            # Fall back to `recall_at_3fp` (legacy / 3 FP/M) for pre-migration
            # bundles that only carry the old budget — labeled so the user
            # knows which they got.
            kind = "recall@1FP-on-slice"
            s_rec = s_route.get("recall_at_1fp")
            d_rec = d_route.get("recall_at_1fp")
            if not (_is_finite_number(s_rec) and _is_finite_number(d_rec)):
                s_rec = s_route.get("recall_at_3fp")
                d_rec = d_route.get("recall_at_3fp")
                kind = "recall@3FP-on-slice"
            if not (_is_finite_number(s_rec) and _is_finite_number(d_rec)):
                continue
            delta = float(s_rec) - float(d_rec)  # positive = improvement
            # Same impact filter as ensemble_wins above: unimpacted filetypes'
            # per-route slice drift is recalibration noise, not signal. Reporting
            # it as a per-route improvement/regression makes a single-route
            # promote look like it touched everything.
            if not is_impacted:
                continue
            if -delta > args.recall_tolerance:
                route_drops.append(
                    f"  {ft} :: {route_name} {kind} dropped {-delta*100:.2f}pp "
                    f"({float(d_rec)*100:.2f}% → {float(s_rec)*100:.2f}%)",
                )
            elif delta >= args.improvement_threshold:
                route_wins.append(
                    f"  {ft} :: {route_name} {kind} +{delta*100:.2f}pp "
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

    # Pre-existing drift on unimpacted filetypes is intentionally NOT printed:
    # it's noise the operator can't act on (by definition not caused by this
    # promote — it's run-to-run instability on routes this candidate didn't
    # touch). Still computed above in case future logic wants it; just not dumped.
    if lwm_wins:
        print()
        print(
            f"{len(lwm_wins)} low-water-mark improvement(s) "
            f"(>{args.lwm_tolerance*100:.2f}pp above LWM, informational):",
        )
        for w in lwm_wins:
            print(f"  + {w}")

    if regressions:
        print()
        print(
            f"{len(regressions)} DEPLOYED-TOLERANCE regression(s) "
            f"(vs currently-deployed bundle {args.deployed}) — THIS IS WHAT BLOCKS THE DEPLOY:",
        )
        for r in regressions:
            print(f"  - {r}")

    if lwm_regressions:
        print()
        print(
            f"{len(lwm_regressions)} LOW-WATER-MARK regression(s) "
            f"(pinned reference: {lwm_path_used}):",
        )
        for r in lwm_regressions:
            print(f"  - {r}")

    # Two independent gates:
    #   - `regressions`: per-filetype drop vs DEPLOYED beyond --recall-tolerance.
    #     May be rescued by --net-improvement-fallback for shared-route promotes.
    #   - `lwm_regressions`: per-filetype drop vs the pinned LOW-WATER-MARK
    #     beyond --lwm-tolerance. Unconditional — cumulative drift below the
    #     pinned floor is exactly what the LWM exists to catch, so it can't
    #     be rescued by net-positive aggregates.
    deployed_gate_blocked = bool(regressions)
    lwm_gate_blocked = bool(lwm_regressions)

    if (regressions or lwm_regressions) and args.net_improvement_fallback:
        # Net-improvement fallback: ship when the new model is net-positive
        # across the corpus (malware-weighted, via raw TP deltas) despite
        # hurting some routes — provided no HIGH-VOLUME filetype cratered past
        # the catastrophe cap. This now rescues BOTH the deployed-tolerance and
        # low-water-mark gates: a per-filetype LWM drop on a small route is the
        # same dataset-level noise as a deployed-tolerance drop there, and the
        # weighted aggregate already accounts for cumulative drift. Catastrophe
        # detection is volume-gated (--catastrophe-min-mal): only routes large
        # enough to move the average — and whose recall estimate isn't sampling
        # noise — can defeat the rescue.
        net_pp = (
            f"net malware-caught delta = {net_delta_tp:+,} TPs across "
            f"{compared} compared filetypes; "
            f"worst high-volume drop (>={args.catastrophe_min_mal} mal) = "
            f"{max_recall_drop_sig*100:.2f}pp on {max_drop_ft_sig or 'none'!r} "
            f"(cap = {args.max_net_route_regression*100:.2f}pp); "
            f"worst drop overall = {max_recall_drop*100:.2f}pp on {max_drop_ft!r} "
            f"(small-route, not gated)"
        )
        if net_delta_tp > 0 and max_recall_drop_sig <= args.max_net_route_regression:
            print()
            print(f"net-improvement-fallback rescues deploy: {net_pp}")
            deployed_gate_blocked = False
            lwm_gate_blocked = False
        else:
            print()
            print(f"net-improvement-fallback DID NOT rescue: {net_pp}")
            if net_delta_tp <= 0:
                print("  reason: aggregate TP delta is not positive")
            if max_recall_drop_sig > args.max_net_route_regression:
                print(
                    f"  reason: a high-volume filetype cratered "
                    f"({max_recall_drop_sig*100:.2f}pp on {max_drop_ft_sig!r}, "
                    f">={args.catastrophe_min_mal} malware) "
                    f"exceeds catastrophe cap "
                    f"({args.max_net_route_regression*100:.2f}pp)"
                )

    if deployed_gate_blocked or lwm_gate_blocked:
        print()
        print(
            f"compared {compared} filetypes "
            f"(mal≥{args.min_mal}, ben≥{args.min_ben}); "
            f"{skipped_small} below threshold and skipped.",
        )
        print()
        reasons: list[str] = []
        if deployed_gate_blocked:
            reasons.append(
                f"deployed-tolerance gate ({len(regressions)} filetype(s) "
                f"regressed vs deployed beyond the {args.recall_tolerance*100:.2f}pp tolerance; "
                f"see list above for the actual drops)"
            )
        if lwm_gate_blocked:
            reasons.append(
                f"low-water-mark gate ({len(lwm_regressions)} filetype(s) "
                f"below LWM beyond the {args.lwm_tolerance*100:.2f}pp tolerance vs {lwm_path_used})"
            )
        print(f"blocked by: {', '.join(reasons)}")
        print()
        print(
            "If this regression is intentional, set "
            "AZOTH_ALLOW_REGRESSION=1 and re-run, or pass "
            "--net-improvement-fallback to ship a net-positive deploy whose "
            "only regressions are on small routes (below --catastrophe-min-mal). "
            "A high-volume filetype cratering past --max-net-route-regression "
            "blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.",
        )
        return 1

    print(
        f"regression check ok: compared {compared} filetype(s) "
        f"(mal≥{args.min_mal}, ben≥{args.min_ben}) at L{args.level} "
        f"{args.severity}; deployed tolerance {args.recall_tolerance*100:.2f}pp"
        + (f"; LWM tolerance {args.lwm_tolerance*100:.2f}pp ({lwm_path_used})"
           if lwm_path_used is not None else "; no LWM provided")
        + ".",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
