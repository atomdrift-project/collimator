#!/usr/bin/env python3
"""Backtest a route's operating point out-of-time. Seconds per experiment.

Every operating-point number the pipeline publishes is in-sample: the
threshold is fitted on a benign pool and reported against that same pool. This
runner reports the out-of-time number instead — fit on benign ingested up to a
cutoff, measure on benign ingested after it — and runs a fixed battery of
interventions against that metric so a claimed improvement has to survive the
split that deploy actually faces.

Experiments (``--experiment``, repeatable, default: all):

  baseline        In-sample vs out-of-time for the shipped estimator. The gap.
  pool-hygiene    Drop carved sub-files / named feeds from the FITTING pool
                  only; evaluate on the untouched pool. Tests whether the
                  operating point is being set by label noise.
  estimator       shared (resolution-adjusted) vs true_rate (literal level).
  extrapolation   Fit on a subsample too small to resolve the level, measure
                  realized rate on the full pool. Answers "can we extrapolate
                  L25 for this route" with a number.
  stability       Threshold spread across resamples of the benign pool — how
                  much of the week-to-week FP swing is the estimator chasing
                  the pool's most extreme file.
  walk-forward    Repeat the out-of-time split at several cutoffs.

Usage::

    make azoth-backtest ROUTE=pe
    scripts/azoth_backtest.py --file-type pe --db $DB --level 25 \
        --experiment baseline --experiment pool-hygiene
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import backtest as bt  # noqa: E402

LOG = logging.getLogger("azoth_backtest")

DAY = 86400

# Benign cohorts whose labels are structurally weaker than the rest of the
# pool. `carved` is a property of the row (extracted from a parent, so the
# benign label is inherited, not observed); the feeds are public corpora whose
# benign halves are known-noisy. Named here rather than inline so the same
# definition is testable and so adding one is a one-line change.
SUSPECT_BENIGN_FEEDS = ("pe-machine-learning-dataset", "enron-xls")


def _fmt(value: Any, spec: str = ".2f") -> str:
    if value is None:
        return "—"
    if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
        return "—"
    return format(value, spec) if isinstance(value, (int, float)) else str(value)


def _row(label: str, res: dict[str, Any]) -> str:
    return (
        f"  {label:<32} n_fit={res.get('n_fit_benign', 0):>7}  "
        f"{res.get('method', '—'):<12} "
        f"recall={_fmt((res.get('recall') or float('nan')) * 100):>6}%  "
        f"tp={res.get('tp', 0):>7}  fp={res.get('fp', 0):>5}  "
        f"fp/M={_fmt(res.get('fp_per_million'), '.1f'):>9}"
    )


def _split(slice_, cutoff, exclude_feeds=()):
    """(fit benign up to cutoff, everything after cutoff) — the honest split.

    ``exclude_feeds`` drops rows from BOTH sides, so a bulk archival import can
    be taken out of the picture without changing the split itself.
    """
    known = slice_.ingested_at > 0
    if exclude_feeds:
        known = known & ~np.isin(slice_.feed, list(exclude_feeds))
    return (slice_.benign & known & (slice_.ingested_at <= cutoff),
            known & (slice_.ingested_at > cutoff))


def exp_validate(slice_, cutoff, level, args) -> dict[str, Any]:
    """Does this harness reproduce the thresholds the pipeline shipped?"""
    route = f"filetypes/{args.file_type}"
    policy_file = args.score_table.parent / "route_policies.json"
    print(f"\n== validate — harness L1 joint-OR vs shipped {route} thresholds")
    if not policy_file.is_file():
        print(f"  (skipped: {policy_file} not found)")
        return {}
    res = bt.validate_against_policy_file(slice_, policy_file, route=route, level=1)
    for r in res["rows"]:
        print(f"  {r['route']:<24} shipped={_fmt(r['shipped'], '.6f'):>10} "
              f"harness={_fmt(r['harness'], '.6f'):>10}  "
              f"{'MATCH' if r['match'] else 'DRIFT'}")
    verdict = ("harness agrees with the shipped policy" if res["all_match"]
               else "DRIFT — results below are suspect")
    print(f"  -> {verdict}")
    return res


def exp_baseline(slice_, cutoff, level, args) -> dict[str, Any]:
    """In-sample vs out-of-time, same policy, same level."""
    fit, later = _split(slice_, cutoff, args.exclude_feed)
    known = slice_.ingested_at > 0
    if args.exclude_feed:
        known = known & ~np.isin(slice_.feed, args.exclude_feed)
    earlier = known & (slice_.ingested_at <= cutoff)
    common = dict(level=level, routes=args.route_list, estimator=args.estimator,
                  kind=args.kind)
    out = {
        "in_sample": bt.backtest(slice_, fit_benign=fit, eval_mask=earlier,
                                 allow_overlap=True, **common),
        "out_of_time": bt.backtest(slice_, fit_benign=fit, eval_mask=later, **common),
    }
    print(f"\n== baseline — in-sample vs out-of-time "
          f"(cutoff {np.datetime64(int(cutoff), 's')}, {args.kind}/{args.estimator}, L{level})")
    print(_row("in-sample (what we publish)", out["in_sample"]))
    print(_row("out-of-time (what deploys)", out["out_of_time"]))
    a = out["in_sample"].get("fp_per_million") or 0.0
    b = out["out_of_time"].get("fp_per_million") or 0.0
    ra = (out["in_sample"].get("recall") or 0) * 100
    rb = (out["out_of_time"].get("recall") or 0) * 100
    print(f"  -> FP/M {_fmt(a, '.1f')} in-sample vs {_fmt(b, '.1f')} out-of-time"
          + (f" ({b / a:.1f}x)" if a > 0 else " (in-sample 0 FP: gap unbounded)")
          + f";  recall {ra:.2f}% -> {rb:.2f}% ({rb - ra:+.2f}pp)")
    return out


def exp_pool_hygiene(slice_, cutoff, level, args) -> dict[str, Any]:
    """Drop suspect cohorts from the FITTING pool only; evaluate untouched."""
    fit, later = _split(slice_, cutoff, args.exclude_feed)
    suspect = np.isin(slice_.feed, SUSPECT_BENIGN_FEEDS)
    variants = {
        "all benign (today)": fit,
        "drop carved sub-files": fit & ~slice_.carved,
        "drop suspect feeds": fit & ~suspect,
        "drop both": fit & ~slice_.carved & ~suspect,
    }
    print(f"\n== pool-hygiene — fitting pool filtered, eval pool untouched (L{level})")
    out, policies = {}, {}
    for name, mask in variants.items():
        res = bt.backtest(slice_, fit_benign=mask, eval_mask=later, level=level,
                          routes=args.route_list, estimator=args.estimator, kind=args.kind)
        policies[name] = bt.fit_policy(slice_, mask, level=level, routes=args.route_list,
                                       estimator=args.estimator, kind=args.kind)
        out[name] = res
        print(_row(name, res))
    base_name = "all benign (today)"
    print(f"  paired bootstrap vs '{base_name}' "
          f"({out[base_name]['n_malware']:,} eval malware, {args.resamples} resamples):")
    for name in variants:
        if name == base_name:
            continue
        d = bt.compare_policies(slice_, policies[name], policies[base_name], later,
                                n_resamples=args.resamples, seed=args.seed)
        out[name]["delta_vs_baseline"] = d
        mark = "significant" if d["significant"] else "NOT significant"
        print(f"    {name:<26} Δrecall {d['diff'] * 100:+.2f}pp  "
              f"95% CI [{d['low'] * 100:+.2f}, {d['high'] * 100:+.2f}]  "
              f"p={d['p_two_sided']:.4f}  {mark}")
    return out


def exp_estimator(slice_, cutoff, level, args) -> dict[str, Any]:
    """Resolution-adjusted level vs literal level, same pool, same split."""
    fit, later = _split(slice_, cutoff, args.exclude_feed)
    print(f"\n== estimator — what L{level} is allowed to mean "
          f"(requested rate {level / 100.0:.2f} FP/M)")
    out = {}
    for name in sorted(bt.ESTIMATORS):
        res = bt.backtest(slice_, fit_benign=fit, eval_mask=later, level=level,
                          routes=args.route_list, estimator=name, kind=args.kind)
        out[name] = res
        print(_row(name, res))
    return out


def exp_extrapolation(slice_, cutoff, level, args) -> dict[str, Any]:
    """How wrong is an extrapolated threshold, per decade of reach?"""
    routes = args.route_list or sorted(slice_.scores)
    out = {}
    print("\n== extrapolation — estimator bias vs distance extrapolated")
    for route in routes:
        ben = slice_.scores[route][slice_.benign]
        need = bt.decades_needed(ben.size, level)
        rows = bt.extrapolation_error(ben, trials=args.trials, seed=args.seed)
        out[route] = {"decades_needed_for_level": need, "rows": rows}
        print(f"  {route}  ({ben.size:,} benigns; L{level} needs {need:.2f} decades "
              f"past its 1-FP floor of {1e6 / ben.size:.2f} FP/M)")
        print(f"    {'decades':>8} {'fit n':>7} {'req /M':>8} {'realized /M':>12} "
              f"{'ratio':>7} {'ratio p05..p95':>18}")
        for r in rows:
            print(f"    {r['decades']:>8.2f} {r['n_fit_benign']:>7} "
                  f"{r['requested_per_million']:>8.0f} "
                  f"{r['realized_per_million_median']:>12.1f} {r['ratio_median']:>7.2f} "
                  f"{r['ratio_p05']:>8.2f}..{r['ratio_p95']:<8.2f}")
    print("  -> ratio 1.0 = delivers the rate it claims; >1 = looser than claimed")
    return out


def exp_stability(slice_, cutoff, level, args) -> dict[str, Any]:
    """How far does the realized FP rate move when the benign pool is resampled?

    The operating point is re-derived on every publish (37 azoth deploys in the
    90 days to 2026-09-15). If it is pinned to the pool's most extreme benign,
    each publish inherits whatever anomaly arrived that night.
    """
    rng = np.random.default_rng(args.seed)
    ben_idx = np.flatnonzero(slice_.benign)
    print(f"\n== stability — refit on 80% resamples of the benign pool "
          f"({args.trials} trials, L{level}, {args.kind})")
    out = {}
    for est in sorted(bt.ESTIMATORS):
        rates, recalls = [], []
        for _ in range(args.trials):
            keep = rng.choice(ben_idx, size=int(ben_idx.size * 0.8), replace=False)
            mask = np.zeros(len(slice_), bool)
            mask[keep] = True
            policy = bt.fit_policy(slice_, mask, level=level, routes=args.route_list,
                                   estimator=est, kind=args.kind)
            if not policy.thresholds:
                continue
            res = bt.measure_policy(slice_, policy, np.ones(len(slice_), bool))
            rates.append(res["fp_per_million"])
            recalls.append(res["recall"] * 100)
        if not rates:
            continue
        out[est] = {
            "fp_per_million_p05": float(np.percentile(rates, 5)),
            "fp_per_million_median": float(np.median(rates)),
            "fp_per_million_p95": float(np.percentile(rates, 95)),
            "recall_p05": float(np.percentile(recalls, 5)),
            "recall_median": float(np.median(recalls)),
            "recall_p95": float(np.percentile(recalls, 95)),
        }
        o = out[est]
        print(f"  {est:<11} FP/M p05..p95 = "
              f"{o['fp_per_million_p05']:.2f}..{o['fp_per_million_p95']:.2f}"
              f"  (median {o['fp_per_million_median']:.2f})   "
              f"recall p05..p95 = {o['recall_p05']:.2f}%..{o['recall_p95']:.2f}%")
    return out


def exp_walk_forward(slice_, cutoff, level, args) -> dict[str, Any]:
    """Repeat the out-of-time split at successive cutoffs."""
    known = slice_.ingested_at > 0
    if not known.any():
        return {}
    latest = int(slice_.ingested_at[known].max())
    print(f"\n== walk-forward — out-of-time performance at successive cutoffs (L{level})")
    print(f"  {'cutoff':<10} {'fit n':>8} {'eval mal':>9} {'eval ben':>9} "
          f"{'recall':>8} {'fp':>5} {'fp/M':>9}")
    out = {}
    for days in args.walk_forward_days:
        cut = latest - days * DAY
        fit, later = _split(slice_, cut, args.exclude_feed)
        if int((fit & slice_.benign).sum()) < 50 or not later.any():
            continue
        res = bt.backtest(slice_, fit_benign=fit, eval_mask=later, level=level,
                          routes=args.route_list, estimator=args.estimator, kind=args.kind)
        out[f"{days}d"] = res
        print(f"  -{days:<9d} {res['n_fit_benign']:>8} {res['n_malware']:>9} "
              f"{res['n_benign']:>9} {(res['recall'] or 0) * 100:>7.2f}% "
              f"{res['fp']:>5} {res['fp_per_million']:>9.1f}")
    return out


def exp_benign_tail(slice_, cutoff, level, args) -> dict[str, Any]:
    """Rank the benign files that set the operating point — the triage list."""
    route = args.route_list[0] if args.route_list else f"filetypes/{args.file_type}"
    if route not in slice_.scores:
        route = sorted(slice_.scores)[0]
    rows = bt.benign_tail(slice_, route, top=args.tail_top)
    print(f"\n== benign-tail — the {args.tail_top} benign files that set {route}'s "
          f"zero-FP threshold")
    print(f"  {'rank':>4} {'row_id':>12} {'score':>9} {'cleave':>7} {'carved':>7} "
          f"{'part':>5} {'cum gain':>9}  feed")
    for r in rows[:args.tail_show]:
        print(f"  {r['rank']:>4} {r['row_id']:>12} {r['score']:>9.6f} "
              f"{r['cleave_score']:>7} {str(r['carved']):>7} {r['partition']:>5} "
              f"{r['recall_gain_pp']:>8.2f}pp  {r['feed'] or '(none)'}")
    n_bad = sum(1 for r in rows if r["carved"] or r["feed"] in SUSPECT_BENIGN_FEEDS)
    print(f"  -> {n_bad}/{len(rows)} of the tail is carved or suspect-feed")
    if rows:
        print(f"  -> clearing the top {min(20, len(rows))} would move recall "
              f"{rows[min(19, len(rows) - 1)]['recall_gain_pp']:+.2f}pp")
    return {"route": route, "rows": rows}


EXPERIMENTS = {
    "validate": exp_validate,
    "benign-tail": exp_benign_tail,
    "baseline": exp_baseline,
    "pool-hygiene": exp_pool_hygiene,
    "estimator": exp_estimator,
    "extrapolation": exp_extrapolation,
    "stability": exp_stability,
    "walk-forward": exp_walk_forward,
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file-type", required=True)
    p.add_argument("--db", default=os.environ.get("DB", ""))
    p.add_argument("--score-table", type=Path,
                   default=Path("out/models/azoth/score_table.npz"))
    p.add_argument("--cache-dir", type=Path, default=Path("out/cache/backtest"))
    p.add_argument("--level", type=int, default=25)
    p.add_argument("--estimator", default="shared", choices=sorted(bt.ESTIMATORS))
    p.add_argument("--routes", default="",
                   help="Comma-separated route names to combine (default: all in the slice)")
    p.add_argument("--kind", default="joint_or", choices=("joint_or", "max", "mean"),
                   help="Decision rule. joint_or is what deploy ships.")
    p.add_argument("--holdout-days", type=int, default=30,
                   help="Out-of-time window: rows ingested in the last N days are eval-only")
    p.add_argument("--walk-forward-days", type=int, nargs="+",
                   default=[90, 60, 45, 30, 14])
    p.add_argument("--trials", type=int, default=50)
    p.add_argument("--tail-top", type=int, default=200,
                   help="How many benign tail rows to rank in benign-tail")
    p.add_argument("--tail-show", type=int, default=25,
                   help="How many benign tail rows to print")
    p.add_argument("--resamples", type=int, default=2000,
                   help="Bootstrap resamples for paired comparison CIs")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--experiment", action="append", default=[],
                   choices=sorted(EXPERIMENTS))
    p.add_argument("--output", type=Path, default=None)
    p.add_argument("--exclude-feed", action="append", default=[],
                   help="Drop a feed from the EVALUATION population (repeatable). "
                        "Use it to separate genuine drift from a bulk archival import.")
    p.add_argument("--refresh-cache", action="store_true")
    p.add_argument("--log-level", default="INFO")
    args = p.parse_args()
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")
    if not args.db:
        raise SystemExit("--db required (or set DB env)")

    slice_ = bt.load_route_slice(args.score_table, args.db, args.file_type,
                                 cache_dir=args.cache_dir, refresh=args.refresh_cache)
    args.route_list = [r for r in args.routes.split(",") if r] or None
    known = slice_.ingested_at > 0
    latest = int(slice_.ingested_at[known].max()) if known.any() else 0
    cutoff = latest - args.holdout_days * DAY

    print(f"\nroute slice: {args.file_type}  rows={len(slice_):,}  "
          f"malware={int(slice_.malware.sum()):,}  benign={int(slice_.benign.sum()):,}")
    print(f"routes ({args.kind}): {args.route_list or sorted(slice_.scores)}")
    if args.exclude_feed:
        n_ex = int(np.isin(slice_.feed, args.exclude_feed).sum())
        print(f"excluded feeds: {args.exclude_feed}  ({n_ex:,} rows dropped from both sides)")
    print(f"ingest span: {np.datetime64(int(slice_.ingested_at[known].min()), 's')} .. "
          f"{np.datetime64(latest, 's')}   holdout = last {args.holdout_days}d")

    names = args.experiment or list(EXPERIMENTS)
    results = {"file_type": args.file_type, "level": args.level,
               "estimator": args.estimator, "kind": args.kind,
               "holdout_days": args.holdout_days, "cutoff_epoch": int(cutoff),
               "n_rows": len(slice_), "experiments": {}}
    for name in names:
        results["experiments"][name] = EXPERIMENTS[name](slice_, cutoff, args.level, args)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2, default=float))
        print(f"\nwrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
