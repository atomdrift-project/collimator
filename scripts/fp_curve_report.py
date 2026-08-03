#!/usr/bin/env python3
"""Leaderboard for the FP-curve ladder backtest.

Reads the JSONL streams written by ``scripts/fp_curve_bench.py`` and scores
the proposal's seven metrics plus the five decision-rule gates.

Metric 1 (primary) is Poisson deviance between the FP count a predicted
threshold *claims* (level x N_pool / 1e8) and the count it actually produces
on the full teacher pool. Deviance is unbounded when a method predicts L1 and
delivers L5000, which is the correct signal but makes means unreadable, so the
median absolute log10 rate ratio is reported beside it as the human-scale
version of the same error.

Verification strength buckets (expected FP on the full pool at that level):

* ``strong``    >= 5 expected FP — a single draw is informative;
* ``aggregate`` >= 0.5 — only the mean over draws detects calibration bias;
* ``weak``      < 0.5 — reported, never used to rank.

Usage::

    .venv/bin/python scripts/fp_curve_report.py out/experiments/fp_curves/ladder
    .venv/bin/python scripts/fp_curve_report.py --cliff out/experiments/fp_curves/cliff-ladder
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

# Rungs at or below this size are the deployment case (a real small route), so
# the proposal weights them double in the primary ranking.
SMALL_RUNG = 2_500
SMALL_RUNG_WEIGHT = 2.0

STRONG_FP = 5.0
AGGREGATE_FP = 0.5

# The intervals the goal names, plus a measured-region reference band.
NAMED_BANDS: dict[str, tuple[float, float]] = {
    "L0-1": (0.0, 1.0),
    "L21-22": (21.0, 22.0),
    "L250-300": (250.0, 300.0),
    "L1000+": (1000.0, 1e9),
}

COVERAGE_TARGET = 0.85
# EXP-1 is the no-extrapolation control: it is exempt from the dynamic-range
# gates by construction (proposal, "Decision rule" gate 4).
CONTROL_ESTIMATOR = "exp1"


def poisson_deviance(observed: np.ndarray, expected: np.ndarray) -> np.ndarray:
    """2*(y*log(y/mu) - (y-mu)), with the y=0 term taken as its limit."""
    y = np.asarray(observed, dtype=np.float64)
    mu = np.clip(np.asarray(expected, dtype=np.float64), 1e-12, None)
    term = np.where(y > 0, y * np.log(np.divide(y, mu, where=y > 0, out=np.ones_like(y))), 0.0)
    return 2.0 * (term - (y - mu))


def log10_rate_ratio(observed: np.ndarray, expected: np.ndarray) -> np.ndarray:
    """log10(realized FP rate / claimed FP rate), Anscombe-smoothed at zero."""
    y = np.asarray(observed, dtype=np.float64) + 0.5
    mu = np.clip(np.asarray(expected, dtype=np.float64), 1e-12, None) + 0.5
    return np.log10(y / mu)


def load(run_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    points = pd.read_json(run_dir / "points.jsonl", lines=True)
    fits = pd.read_json(run_dir / "fits.jsonl", lines=True)
    manifest = json.loads((run_dir / "manifest.json").read_text())
    points["deviance"] = poisson_deviance(points["fp_realized"], points["fp_expected"])
    points["log_ratio"] = log10_rate_ratio(points["fp_realized"], points["fp_expected"])
    points["strength"] = np.where(
        points["fp_expected"] >= STRONG_FP, "strong",
        np.where(points["fp_expected"] >= AGGREGATE_FP, "aggregate", "weak"),
    )
    points["weight"] = np.where(points["m"] <= SMALL_RUNG, SMALL_RUNG_WEIGHT, 1.0)
    # A fit can only *measure* levels at or above its own 1-FP floor; below
    # that every estimator is making a claim.
    points["above_fit_floor"] = points["level"] >= (1e8 / points["m"])
    # Metric 4 asks whether the realized FP *count* falls inside the band. The
    # band's edges are thresholds, so mapping them to counts gives an interval
    # on the mean — at deep levels where that mean is below 1, a count is a
    # Poisson draw around it and comparing the two directly would fail an
    # estimator for arithmetic it never got wrong. The edges therefore carry
    # the count's own Poisson spread.
    from scipy.stats import poisson  # noqa: PLC0415

    points["covered"] = (
        (points["fp_realized"] <= poisson.ppf(0.95, np.maximum(points["fp_band_lo"], 1e-9)))
        & (points["fp_realized"] >= poisson.ppf(0.05, np.maximum(points["fp_band_hi"], 1e-9)))
    )
    points["band_decades"] = (
        np.log10(points["fp_band_lo"] + 0.5) - np.log10(points["fp_band_hi"] + 0.5)
    )
    points["threshold_error"] = (points["t_hat"] - points["t_star"]).abs()
    points["recall_error"] = (points["recall_hat"] - points["recall_star"]).abs()
    return points, fits, manifest


def _fmt(df: pd.DataFrame, floatfmt: str = "{:.3f}") -> str:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_float_dtype(out[col]):
            out[col] = out[col].map(lambda v: "—" if pd.isna(v) else floatfmt.format(v))
    header = "| " + " | ".join(str(c) for c in [out.index.name or ""] + list(out.columns)) + " |"
    sep = "|" + "|".join(["---"] * (len(out.columns) + 1)) + "|"
    rows = [
        "| " + " | ".join([str(idx)] + [str(v) for v in row]) + " |"
        for idx, row in zip(out.index, out.to_numpy(), strict=True)
    ]
    return "\n".join([header, sep, *rows])


def aggregated_deviance(points: pd.DataFrame, weight_small: bool = True) -> pd.Series:
    """Metric 1: Poisson deviance on FP counts summed over draws.

    Summing before scoring is what makes the deep levels testable at all: one
    draw at L21 expects ~0.6 FP on the deepest teacher pool, so a per-draw
    deviance is mostly noise, while the sum over 50 draws is Poisson with a
    mean 50x larger and detects a systematic rate error cleanly. It is also
    far more robust than averaging per-point deviances, which a single
    blown-up draw can dominate by six orders of magnitude.
    """
    grouped = points.groupby(["estimator", "pool", "m", "level"], observed=True).agg(
        obs=("fp_realized", "sum"), exp=("fp_expected", "sum"),
    ).reset_index()
    grouped["dev"] = poisson_deviance(grouped["obs"], grouped["exp"])
    grouped["weight"] = np.where(
        (grouped["m"] <= SMALL_RUNG) & weight_small, SMALL_RUNG_WEIGHT, 1.0,
    )
    return grouped.groupby("estimator").apply(
        lambda g: float(np.average(g["dev"], weights=g["weight"])), include_groups=False,
    )


def leaderboard(points: pd.DataFrame, fits: pd.DataFrame) -> pd.DataFrame:
    """Primary ranking table: one row per estimator."""
    scored = points[(points["strength"] != "weak") & (points["level"] > 0)]
    agg_dev = aggregated_deviance(scored)
    rows = []
    for est, grp in scored.groupby("estimator"):
        f = fits[fits["estimator"] == est]
        above = grp[grp["above_fit_floor"]]
        below = grp[~grp["above_fit_floor"]]
        w = grp["weight"].to_numpy()
        rows.append({
            "estimator": est,
            "calib_deviance": float(agg_dev.get(est, np.nan)),
            "point_deviance": float(np.average(grp["deviance"], weights=w)),
            "dev_above": float(np.average(above["deviance"], weights=above["weight"]))
            if len(above) else np.nan,
            "abs_log_ratio_med": float(grp["log_ratio"].abs().median()),
            "log_ratio_above": float(above["log_ratio"].abs().median()) if len(above) else np.nan,
            "log_ratio_below": float(below["log_ratio"].abs().median()) if len(below) else np.nan,
            "thr_mae_above": float(above["threshold_error"].mean()) if len(above) else np.nan,
            "recall_mae": float(grp["recall_error"].mean()),
            "coverage": float(grp["covered"].mean()),
            "cov_above": float(above["covered"].mean()) if len(above) else np.nan,
            "cov_below": float(below["covered"].mean()) if len(below) else np.nan,
            "band_decades": float(grp["band_decades"].median()),
            # Poisson deviance is asymmetric: claiming L1 and delivering zero
            # FP costs almost nothing, while claiming L1 and delivering L5000
            # costs thousands. An estimator can therefore win metric 1 by
            # predicting thresholds nothing fires on. These three columns are
            # what expose that — signed bias, dead predictions, and the recall
            # actually retained at the deploy operating point.
            "signed_log_ratio": float(grp["log_ratio"].median()),
            "dead_frac": float((grp["fp_realized"] == 0).mean()),
            "recall_at_L25": float(grp.loc[grp["level"] == 25, "recall_hat"].median())
            if (grp["level"] == 25).any() else np.nan,
            "ceiling_frac": float((grp["t_hat"] >= 15.999).mean()),
            "mono_viol": (
                float(f["monotone_violations_below_ceiling"].mean()) if len(f) else np.nan
            ),
            "distinct_grid": float(f["distinct_below_ceiling"].mean()) if len(f) else np.nan,
            "slope_tv": float(f["slope_total_variation"].median()) if len(f) else np.nan,
            "fit_s": float(f["fit_seconds"].median()) if len(f) else np.nan,
            "failures": int(f["failed"].sum()) if len(f) else 0,
        })
    out = pd.DataFrame(rows).set_index("estimator").sort_values("calib_deviance")
    out.index.name = "estimator"
    return out


def by_rung(points: pd.DataFrame) -> pd.DataFrame:
    scored = points[(points["strength"] != "weak") & (points["level"] > 0)]
    tab = scored.pivot_table(
        index="estimator", columns="m", values="log_ratio",
        aggfunc=lambda s: float(np.abs(s).median()),
    )
    tab.columns = [f"m={c}" for c in tab.columns]
    return tab


def by_band(points: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for est, grp in points[points["level"] > 0].groupby("estimator"):
        row = {"estimator": est}
        for name, (lo, hi) in NAMED_BANDS.items():
            sel = grp[(grp["level"] >= lo) & (grp["level"] <= hi)]
            row[name] = float(sel["log_ratio"].abs().median()) if len(sel) else np.nan
            row[f"{name} n"] = len(sel)
        rows.append(row)
    return pd.DataFrame(rows).set_index("estimator")


def aggregate_bias(points: pd.DataFrame, min_expected: float = 3.0) -> pd.DataFrame:
    """Pooled-over-draws calibration, which is how the deep levels get tested.

    At L21 a single draw expects ~0.6 FP on the deepest teacher pool, so no
    individual verification is possible. Summed over B draws the total is
    Poisson with a mean B times larger, and a systematic rate error (the thing
    that actually matters) shows up unmistakably. Rows whose *summed* expected
    count is still below ``min_expected`` are reported with a blank ratio
    rather than a number nobody should read.
    """
    rows = []
    scored = points[points["level"] > 0].copy()
    scored["band"] = pd.cut(
        scored["level"],
        bins=[0, 1, 5, 22, 50, 100, 300, 1000, 25_000],
        labels=["<=1", "1-5", "5-22", "22-50", "50-100", "100-300", "300-1k", "1k-25k"],
    )
    for (est, m, band), grp in scored.groupby(["estimator", "m", "band"], observed=True):
        obs = float(grp["fp_realized"].sum())
        exp = float(grp["fp_expected"].sum())
        rows.append({
            "estimator": est, "m": m, "band": str(band),
            "rate_ratio": (obs + 0.5) / (exp + 0.5) if exp >= min_expected else np.nan,
        })
    out = pd.DataFrame(rows)
    return out.pivot_table(
        index=["estimator", "m"], columns="band", values="rate_ratio", observed=True,
    )


def stability(points: pd.DataFrame) -> pd.DataFrame:
    """Metric 7: sd of the predicted threshold across draws, *per level*.

    Pooling levels before taking the sd would measure the curve's slope, not
    its stability; the number that matters is "refit on another sample of the
    same size, how much does this level's threshold move?"
    """
    per_level = points.groupby(["estimator", "m", "pool", "level"])["t_hat"].std()
    tab = per_level.groupby(["estimator", "m"]).median().reset_index().pivot_table(
        index="estimator", columns="m", values="t_hat",
    )
    tab.columns = [f"sd m={c}" for c in tab.columns]
    return tab


def l0_check(points: pd.DataFrame) -> pd.DataFrame:
    """L0 claims zero FP; how often does it actually fire on the full pool?"""
    l0 = points[points["level"] == 0]
    if l0.empty:
        return pd.DataFrame()
    tab = l0.groupby("estimator").agg(
        l0_fp_mean=("fp_realized", "mean"),
        l0_fp_max=("fp_realized", "max"),
        l0_zero_fraction=("fp_realized", lambda s: float((s == 0).mean())),
    )
    return tab


def gates(points: pd.DataFrame, fits: pd.DataFrame, board: pd.DataFrame) -> pd.DataFrame:
    """The decision rule's five hard gates, per estimator."""
    baseline = board.loc["b0", "log_ratio_above"] if "b0" in board.index else np.nan
    rows = []
    for est in board.index:
        f = fits[fits["estimator"] == est]
        control = est == CONTROL_ESTIMATOR
        above = board.loc[est, "log_ratio_above"]
        rows.append({
            "estimator": est,
            "1_measured_fidelity": (
                "PASS" if (np.isnan(baseline) or above <= baseline + 0.05) else "FAIL"
            ),
            "2_strict_monotone": (
                "PASS" if f["monotone_violations_below_ceiling"].max() == 0
                else ("EXEMPT(control)" if control else "FAIL")
            ),
            "4_dial_resolution": (
                "PASS" if f["distinct_below_ceiling"].min() >= 0.95
                else ("EXEMPT(control)" if control else "FAIL")
            ),
            "5_ci_coverage": "PASS" if board.loc[est, "coverage"] >= COVERAGE_TARGET else "FAIL",
        })
    out = pd.DataFrame(rows).set_index("estimator")
    out["3_cliff_test"] = "see --cliff run"
    return out


def cliff_report(points: pd.DataFrame) -> pd.DataFrame:
    """Metric 6: is the curve difference across the 25k regime switch bigger
    than sampling noise at the same rung?

    ``cliff_z`` is |mean(t | m=25376) - mean(t | m=24776)| divided by the
    pooled within-rung sd. A regime discontinuity shows up as z >> 1 at
    levels near the switch; pure sampling noise sits around 1.
    """
    rows = []
    for (est, pool), grp in points[points["level"] > 0].groupby(["estimator", "pool"]):
        stats = grp.groupby(["m", "level"])["t_hat"].agg(["mean", "std", "count"])
        sizes = sorted(grp["m"].unique())
        if len(sizes) != 2:
            continue
        lo, hi = sizes
        merged = stats.loc[lo].join(stats.loc[hi], lsuffix="_lo", rsuffix="_hi")
        delta = (merged["mean_hi"] - merged["mean_lo"]).abs()
        noise = np.sqrt(
            (merged["std_lo"] ** 2 / merged["count_lo"]) + (merged["std_hi"] ** 2 / merged["count_hi"])
        )
        z = delta / noise.replace(0.0, np.nan)
        rows.append({
            "estimator": est, "pool": pool,
            "max_delta_logit": float(delta.max()),
            "median_delta_logit": float(delta.median()),
            "max_cliff_z": float(z.max()),
            "median_cliff_z": float(z.median()),
            "level_at_max_z": float(z.idxmax()) if z.notna().any() else np.nan,
        })
    return pd.DataFrame(rows).set_index(["estimator", "pool"])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--cliff", action="store_true")
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    points, fits, manifest = load(args.run_dir)
    print(f"# FP-curve ladder report — {args.run_dir}\n")
    print(
        f"pools={len(manifest['pools'])} estimators={manifest['estimators']} "
        f"rungs={manifest['rungs']} draws={manifest['draws']} "
        f"points={len(points)} fits={len(fits)}\n"
    )

    if args.cliff:
        print("## Metric 6 — cliff test (24,776 vs 25,376 benigns, same pool)\n")
        print(_fmt(cliff_report(points)))
        return 0

    board = leaderboard(points, fits)
    print("## Leaderboard (ranked by weighted Poisson deviance, metric 1)\n")
    print(_fmt(board))
    print("\n## Median |log10 realized/claimed FP rate| by rung\n")
    print(_fmt(by_rung(points)))
    print("\n## By named level band (all strengths; n = scored points)\n")
    print(_fmt(by_band(points)))
    print("\n## Aggregate calibration over all draws (realized/claimed FP rate; 1.0 is perfect)\n")
    print(_fmt(aggregate_bias(points), "{:.2f}"))
    print("\n## Metric 7 — threshold sd across draws (logit)\n")
    print(_fmt(stability(points)))
    print("\n## L0 sanity — L0 claims zero FP\n")
    print(_fmt(l0_check(points)))
    print("\n## Decision-rule gates\n")
    print(_fmt(gates(points, fits, board)))

    if args.json_out:
        args.json_out.write_text(json.dumps({
            "leaderboard": board.reset_index().to_dict(orient="records"),
            "by_band": by_band(points).reset_index().to_dict(orient="records"),
            "gates": gates(points, fits, board).reset_index().to_dict(orient="records"),
        }, indent=2, default=float) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
