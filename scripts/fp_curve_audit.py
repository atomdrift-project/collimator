#!/usr/bin/env python3
"""Audit: which estimator gives a smooth, accurate curve at the strict end?

The leaderboard ranks estimators over the whole dial and over a handful of
teacher pools. This asks the narrower operational question: across every route
model deep enough to be scored, which estimator can be trusted to produce a
curve that is both *smooth* and *rate-accurate* in L0-L100 — the band scan
consumes for the tightest operating points and the band no route can measure
directly.

Four things are scored per (estimator, model), all restricted to L <= 100:

* **rate accuracy** — realized FP summed over every draw and level in the
  band, against the FP those thresholds claimed. Summing is what makes the
  band testable at all: one draw at L25 on a 2M-benign pool expects 0.5 FP.
* **silenced fraction** — predictions sitting at the score ceiling, i.e. the
  route stops firing. Distinct from "zero FP observed", which at these levels
  is usually the correct outcome.
* **smoothness** — total variation of d(logit t)/d(log level) inside the band,
  plus monotonicity violations and the fraction of levels with distinct
  thresholds.
* **served** — a model is *served* by an estimator when the rate is within
  10x, fewer than 20% of its band is silenced, and the curve is strictly
  monotone with a fully resolving dial.

Usage::

    .venv/bin/python scripts/fp_curve_audit.py out/experiments/fp_curves/audit-all
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

LOW_MAX = 100.0
# A summed expected count below this cannot distinguish an estimator from
# noise, so the model is reported as unscorable in the band rather than given
# a number that reads as a measurement.
MIN_EXPECTED_FP = 5.0
RATE_TOLERANCE = 10.0
MAX_SILENCED = 0.20
CEILING_LOGIT = 15.999


def load(run_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read the run, keeping only the band.

    A 21-model run writes ~400MB of points; reading it whole to throw away
    three quarters of it is a needless couple of GB, so the band filter is
    applied per chunk on the way in.
    """
    keep = []
    with pd.read_json(run_dir / "points.jsonl", lines=True, chunksize=200_000) as reader:
        for chunk in reader:
            keep.append(chunk[(chunk["level"] > 0) & (chunk["level"] <= LOW_MAX)])
    points = pd.concat(keep, ignore_index=True) if keep else pd.DataFrame()
    fits = pd.read_json(run_dir / "fits.jsonl", lines=True)
    return points, fits


def per_model(points: pd.DataFrame, fits: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (est, pool), grp in points.groupby(["estimator", "pool"]):
        f = fits[(fits["estimator"] == est) & (fits["pool"] == pool)]
        obs, exp = float(grp["fp_realized"].sum()), float(grp["fp_expected"].sum())
        scorable = exp >= MIN_EXPECTED_FP
        rows.append({
            "estimator": est,
            "model": pool,
            "expected_fp": exp,
            "observed_fp": obs,
            "rate_ratio": (obs + 0.5) / (exp + 0.5) if scorable else np.nan,
            "silenced": float((grp["t_hat"] >= CEILING_LOGIT).mean()),
            "mono_viol": float(f["low_mono_violations"].max()) if len(f) else np.nan,
            "distinct": float(f["low_distinct_fraction"].min()) if len(f) else np.nan,
            "slope_tv": float(f["low_slope_tv"].median()) if len(f) else np.nan,
            "scorable": scorable,
        })
    out = pd.DataFrame(rows)
    ratio_ok = (out["rate_ratio"].between(1.0 / RATE_TOLERANCE, RATE_TOLERANCE)) | ~out["scorable"]
    out["served"] = (
        ratio_ok
        & (out["silenced"] < MAX_SILENCED)
        & (out["mono_viol"] == 0)
        & (out["distinct"] >= 0.95)
    )
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--csv-out", type=Path, default=None)
    args = ap.parse_args(argv)

    import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from fp_curve_report import _fmt  # noqa: PLC0415 — shared table formatter

    points, fits = load(args.run_dir)
    tab = per_model(points, fits)
    models = sorted(tab["model"].unique())
    ests = [e for e in ("b0", "exp1", "exp2", "exp3", "exp4", "exp5")
            if e in set(tab["estimator"])]

    print(f"# Strict-end audit (L0-L{LOW_MAX:.0f}) — {args.run_dir}\n")
    print(f"{len(models)} route models, {len(ests)} estimators, "
          f"{len(points):,} scored points in band\n")

    print("## Models served (rate within 10x, <20% silenced, monotone, fully resolving)\n")
    served = tab.pivot_table(index="estimator", values="served", aggfunc="sum")
    scorable = tab[tab["scorable"]].groupby("estimator").size()
    summary = pd.DataFrame({
        "models_served": served["served"],
        "of_total": len(models),
        "rate_scorable": scorable,
        "median_rate_ratio": tab.groupby("estimator")["rate_ratio"].median(),
        "worst_rate_ratio": tab.groupby("estimator")["rate_ratio"].max(),
        "median_silenced": tab.groupby("estimator")["silenced"].median(),
        "median_slope_tv": tab.groupby("estimator")["slope_tv"].median(),
        "worst_mono_viol": tab.groupby("estimator")["mono_viol"].max(),
        "worst_distinct": tab.groupby("estimator")["distinct"].min(),
    }).reindex(ests)
    print(_fmt(summary, "{:.2f}"))

    print("\n## Rate ratio in band, per model (1.0 perfect; blank = unscorable)\n")
    print(_fmt(tab.pivot_table(index="model", columns="estimator",
                               values="rate_ratio")[ests], "{:.2f}"))
    print("\n## Silenced fraction in band, per model\n")
    print(_fmt(tab.pivot_table(index="model", columns="estimator",
                               values="silenced")[ests], "{:.1%}"))
    print("\n## Smoothness in band — total variation of d(logit t)/d(log level)\n")
    print(_fmt(tab.pivot_table(index="model", columns="estimator",
                               values="slope_tv")[ests], "{:.2f}"))

    print("\n## Per-model verdict\n")
    print("| model | served by | best rate ratio |")
    print("|---|---|---|")
    for model in models:
        sub = tab[tab["model"] == model]
        ok = sorted(sub.loc[sub["served"], "estimator"])
        scored = sub.dropna(subset=["rate_ratio"])
        best = ""
        if len(scored):
            row = scored.iloc[(scored["rate_ratio"] - 1.0).abs().argsort().iloc[0]]
            best = f"{row['estimator']} ({row['rate_ratio']:.2f}x)"
        print(f"| {model} | {', '.join(ok) if ok else '**none**'} | {best} |")

    if args.csv_out:
        tab.to_csv(args.csv_out, index=False)
        print(f"\nPer-model table: {args.csv_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
