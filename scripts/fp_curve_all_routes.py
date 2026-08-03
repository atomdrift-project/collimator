#!/usr/bin/env python3
"""All-routes application pass: does a candidate estimator survive the fleet?

The ladder ranks estimators on six deep teacher pools. That is where accuracy
can be *measured*, but it is not where the estimator has to work — production
emits a curve for all 73 routes, most of which are far smaller and stranger
than any teacher. This pass fits the candidates on every route's full OOF pool
and runs the diagnostics battery from the proposal:

* strict monotonicity over the continuous grid (below the score ceiling);
* dial resolution — how many grid levels get distinct thresholds;
* Clopper-Pearson consistency — every sub-floor row must carry the flag and
  the bound, so a model claim can never read as a measurement;
* family-shape outliers — a route whose fitted tail deviates from its
  filegroup by more than 3 prior sds is flagged for eyes-on review;
* saturation — routes whose benign scores touch the float32 probability
  ceiling have an FP floor no estimator can predict its way below;
* fit failures.

A winner that fails more than 5% of routes, or any high-volume route, is not
a winner regardless of its ladder score.

Usage::

    .venv/bin/python scripts/fp_curve_all_routes.py --estimators exp3,exp4,exp5
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fp_curve_bench import _context_for  # noqa: E402
from fp_curve_estimators import POOLED, get_fit  # noqa: E402
from fp_curve_estimators.base import SATURATION_LOGIT  # noqa: E402
from fp_curve_estimators.pools import available_routes, fleet_context, load_pool  # noqa: E402

log = logging.getLogger("fp_curve_all_routes")

GRID: tuple[float, ...] = (
    0, 1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100,
    125, 150, 175, 200, 250, 300, 500, 750, 1000, 1250, 1500, 1750, 2000,
    2250, 2500, 3000, 4000, 5000, 6000, 7500, 10000, 15000, 20000, 25000,
)
DENSE = np.geomspace(0.5, 25_000.0, 400)
# A route carrying this many benigns or more is load-bearing: a diagnostics
# failure there disqualifies a candidate on its own.
HIGH_VOLUME_BENIGN = 500_000
SHRINKAGE_OUTLIER_Z = 3.0


def diagnose(model, route: str, n_benign: int) -> dict:
    """Run the battery on one fitted curve."""
    rows = model.to_grid(GRID)
    dense = model.thresholds(DENSE)
    below_ceiling = dense < SATURATION_LOGIT - 1e-9
    grid_thr = np.array([r["threshold_logit"] for r in rows])
    grid_below = grid_thr[grid_thr < SATURATION_LOGIT - 1e-9]

    mono_viol = int(np.sum(np.diff(dense[below_ceiling]) >= 0.0)) if below_ceiling.sum() > 1 else 0
    distinct = (
        len(np.unique(np.round(grid_below, 12))) / grid_below.size
        if grid_below.size else float("nan")
    )
    # Every row below the fit's own floor must be flagged and must carry the
    # Clopper-Pearson bound; anything else would let a model claim read as a
    # measurement downstream.
    sub_floor = [r for r in rows if r["level"] > 0 and r["level"] < r["fit_floor_per_100M"]]
    cp_ok = all(
        (r["model_extrapolated"] or model.method.startswith("exp1"))
        and r["cp_floor_per_100M"] > 0
        for r in sub_floor
    )
    extras = model.row_extras(1.0)
    return {
        "route": route,
        "n_benign": n_benign,
        "estimator": model.method,
        "mono_violations": mono_viol,
        "distinct_grid": float(distinct),
        "ceiling_fraction": float(np.mean(~below_ceiling)),
        "cp_consistent": bool(cp_ok),
        "floor_per_100M": float(model.fit_floor_level),
        "saturation_floor_per_100M": float(model.saturation.floor_per_100M),
        "saturated": bool(model.saturation.present),
        "xi": float(extras.get("xi", float("nan"))),
        "shrinkage_z": float(extras.get("shrinkage_z", float("nan"))),
        "threshold_l25": float(rows[GRID.index(25)]["threshold"]),
        "threshold_l1": float(rows[GRID.index(1)]["threshold"]),
    }


def verdict(row: dict) -> tuple[bool, str, str]:
    """(pass, failure reasons, review flags) per the proposal's battery.

    A family-shape outlier is not a failure — the proposal asks for it to be
    "flagged for eyes-on review". It is reported separately so a route whose
    tail genuinely differs from its filegroup does not disqualify an estimator
    that is otherwise behaving.
    """
    reasons, flags = [], []
    if row.get("failed"):
        return False, "fit failed", ""
    if row["mono_violations"] > 0:
        reasons.append(f"monotonicity({row['mono_violations']})")
    if np.isfinite(row["distinct_grid"]) and row["distinct_grid"] < 0.95:
        reasons.append(f"dial({row['distinct_grid']:.2f})")
    if not row["cp_consistent"]:
        reasons.append("cp-flag")
    if np.isfinite(row["shrinkage_z"]) and abs(row["shrinkage_z"]) > SHRINKAGE_OUTLIER_Z:
        flags.append(f"family-outlier(z={row['shrinkage_z']:.1f})")
    return (not reasons), ",".join(reasons), ",".join(flags)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--estimators", default="exp3,exp4,exp5")
    ap.add_argument("--out", default="out/experiments/fp_curves/all_routes")
    ap.add_argument("--routes", default="",
                    help="comma-separated subset (default: every OOF route)")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    estimators = [e.strip() for e in args.estimators.split(",") if e.strip()]
    routes = [r.strip() for r in args.routes.split(",") if r.strip()] or available_routes()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    context_all = fleet_context()
    log.info("fleet context: %d routes; applying to %d routes", len(context_all), len(routes))

    results: list[dict] = []
    for route in routes:
        pool = load_pool(route)
        ctx = _context_for(route, context_all, "topology", {route: pool})
        # EXP-5 trains on whole pools; give it the teacher-sized routes that
        # are not the target (and not in its family), same rule as the ladder.
        train_pools = {
            t.route: load_pool(t.route).benign
            for t in ctx.tails
            if t.n_benign >= 200_000
        }
        from fp_curve_estimators.base import PooledContext  # noqa: PLC0415

        ctx = PooledContext(tails=ctx.tails, extras={"full_pools": train_pools})
        for name in estimators:
            started = time.perf_counter()
            try:
                model = get_fit(name)(pool.benign, pool.meta(), ctx if name in POOLED else None)
                row = diagnose(model, route, pool.n_benign)
            except Exception as exc:  # noqa: BLE001 — a failure is a result
                row = {
                    "route": route, "n_benign": pool.n_benign, "estimator": name,
                    "failed": True, "error": f"{type(exc).__name__}: {exc}",
                    "mono_violations": -1, "distinct_grid": float("nan"),
                    "cp_consistent": False, "shrinkage_z": float("nan"),
                }
            row["seconds"] = time.perf_counter() - started
            ok, why, flags = verdict(row)
            row["pass"] = ok
            row["reason"] = why
            row["review_flags"] = flags
            results.append(row)
        log.info("%-32s n=%8d  %s", route, pool.n_benign,
                 "  ".join(f"{r['estimator']}:{r['reason'] or r['review_flags'] or 'ok'}"
                          for r in results[-len(estimators):]))

    fields = sorted({k for r in results for k in r})
    with (out_dir / "per_route.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n# All-routes application pass ({len(routes)} routes)\n")
    print("| estimator | routes | failures | failure rate | high-volume failures "
          "| review flags | saturated routes |")
    print("|---|---|---|---|---|---|---|")
    summary = {}
    for name in estimators:
        sub = [r for r in results if r["estimator"] in (name, f"{name}_pooled_tail") or
               r.get("estimator", "").startswith(name)]
        fails = [r for r in sub if not r["pass"]]
        hv = [r for r in fails if r["n_benign"] >= HIGH_VOLUME_BENIGN]
        sat = [r for r in sub if r.get("saturated")]
        flagged = [r for r in sub if r.get("review_flags")]
        summary[name] = {
            "routes": len(sub), "failures": len(fails),
            "failure_rate": len(fails) / max(len(sub), 1),
            "high_volume_failures": [r["route"] for r in hv],
            "review_flagged": [r["route"] for r in flagged],
            "saturated": [r["route"] for r in sat],
        }
        print(f"| {name} | {len(sub)} | {len(fails)} | {len(fails)/max(len(sub),1):.1%} "
              f"| {len(hv)} | {len(flagged)} | {len(sat)} |")
    print("\n## Routes flagged for eyes-on review (family-shape outliers)\n")
    for name in estimators:
        flagged = [r for r in results
                   if r.get("estimator", "").startswith(name) and r.get("review_flags")]
        if not flagged:
            print(f"- **{name}**: none")
            continue
        print(f"- **{name}**: " + ", ".join(
            f"`{r['route']}` {r['review_flags']}" for r in
            sorted(flagged, key=lambda r: -r["n_benign"])[:12]))
    print("\n## Failures by reason\n")
    for name in estimators:
        fails = [r for r in results if r.get("estimator", "").startswith(name) and not r["pass"]]
        if not fails:
            print(f"- **{name}**: none")
            continue
        print(f"- **{name}**:")
        for r in sorted(fails, key=lambda r: -r["n_benign"])[:12]:
            print(f"  - `{r['route']}` (n={r['n_benign']:,}) — {r['reason']}")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"\nPer-route table: {out_dir / 'per_route.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
