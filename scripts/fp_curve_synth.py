#!/usr/bin/env python3
"""Synthetic-tail suite: absolute error bars at L0-1.

The ladder backtest can only verify where a teacher pool can measure. Its
deepest honest verification is ~L34 (2.97M benigns), and rung-consistency
catches an estimator that is *unstable* across scales but not one that is
wrong the same way at every scale. L0-1 has no empirical oracle at all —
direct verification would need ~100M benigns under one model.

Here the distribution is known, so the truth at any level is exact. Each
shape is built as a mixture: a body resampled from a real route's benign
scores (so the estimators see a realistic distribution) spliced at the 99th
percentile onto an analytic tail whose survival function is known in closed
form. Every level below 1% is therefore scored against exact truth, with no
sampling noise in the target at all.

Anti-circularity: results are reported PER SHAPE, never averaged. ``gpd_pure``
is deliberately included as the EVT estimators' own assumption class — a
method that only wins there has been exposed, not rewarded.

Usage::

    .venv/bin/python scripts/fp_curve_synth.py --estimators b0,exp1,exp2,exp3,exp4,exp5
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fp_curve_estimators import POOLED, get_fit  # noqa: E402
from fp_curve_estimators.base import (  # noqa: E402
    SATURATION_LOGIT,
    RouteMeta,
    draw_seed,
    level_to_prob,
)
from fp_curve_estimators.pools import fleet_context, load_pool  # noqa: E402

log = logging.getLogger("fp_curve_synth")

SPLICE_QUANTILE = 0.99
LEVELS: tuple[float, ...] = (0.5, 1, 2, 5, 10, 21, 25, 50, 100, 250, 300, 1000, 5000, 25_000)
RUNGS: tuple[int, ...] = (800, 2_500, 25_000, 200_000)


@dataclass
class Shape:
    """A benign score distribution with a known tail.

    ``body`` is resampled with replacement below the splice; above it the tail
    is analytic. ``zeta`` is the mass above the splice, so for any threshold
    at or above ``u`` the survival function — and hence the realized FP rate a
    predicted threshold would produce — is exact.
    """

    name: str
    body: np.ndarray  # real scores below the splice point
    u: float
    zeta: float
    xi: float
    sigma: float
    bump_mass: float = 0.0
    bump_loc: float = 0.0
    bump_scale: float = 1.0
    quantize: float = 0.0  # logit step size; 0 = continuous

    def _tail_sf(self, x: np.ndarray) -> np.ndarray:
        y = np.maximum(np.asarray(x, dtype=np.float64) - self.u, 0.0)
        if abs(self.xi) < 1e-9:
            return np.exp(-y / self.sigma)
        z = 1.0 + self.xi * y / self.sigma
        return np.where(z > 0, np.power(np.maximum(z, 1e-300), -1.0 / self.xi), 0.0)

    def sf(self, x: np.ndarray) -> np.ndarray:
        """Exact P(X >= x): the FP rate a threshold at x would produce.

        Scores are clamped at the float32 probability ceiling, exactly as the
        real routes are (12 of 73 carry a saturated atom), so mass that the
        analytic tail places above the ceiling piles up on it and no threshold
        above the ceiling exists.
        """
        xs = np.atleast_1d(np.asarray(x, dtype=np.float64))
        over = xs > SATURATION_LOGIT
        out = self.zeta * (1.0 - self.bump_mass) * self._tail_sf(xs)
        if self.bump_mass > 0:
            out = out + self.zeta * self.bump_mass * norm.sf(xs, self.bump_loc, self.bump_scale)
        below = xs < self.u
        if below.any():
            # Below the splice the body is empirical; its survival is the
            # resampling distribution's, which is exactly the body ECDF.
            frac = np.searchsorted(self.body, xs[below], side="left") / self.body.size
            out = out.copy()
            out[below] = self.zeta + (1.0 - self.zeta) * (1.0 - frac)
        return np.where(over, 0.0, out)

    def isf(self, prob: np.ndarray) -> np.ndarray:
        """True threshold at each exceedance probability (exact in the tail)."""
        p = np.atleast_1d(np.asarray(prob, dtype=np.float64))
        out = np.empty(p.shape)
        for i, pi in enumerate(p):
            if pi >= self.zeta:
                idx = int(np.clip(
                    round((1.0 - (pi - self.zeta) / (1.0 - self.zeta)) * self.body.size) - 1,
                    0, self.body.size - 1,
                ))
                out[i] = self.body[idx]
                continue
            # Monotone bisection on the exact survival function.
            lo, hi = self.u, self.u + 1.0
            while self.sf(np.array([hi]))[0] > pi and hi < 1e4:
                hi *= 2.0
            for _ in range(200):
                mid = 0.5 * (lo + hi)
                if self.sf(np.array([mid]))[0] > pi:
                    lo = mid
                else:
                    hi = mid
            out[i] = 0.5 * (lo + hi)
        if self.quantize > 0:
            out = np.ceil(out / self.quantize) * self.quantize
        return np.minimum(out, SATURATION_LOGIT)

    def rvs(self, n: int, rng: np.random.Generator) -> np.ndarray:
        in_tail = rng.random(n) < self.zeta
        n_tail = int(in_tail.sum())
        out = np.empty(n)
        out[~in_tail] = rng.choice(self.body, size=n - n_tail, replace=True)
        if n_tail:
            is_bump = rng.random(n_tail) < self.bump_mass
            n_bump = int(is_bump.sum())
            u_draw = rng.random(n_tail - n_bump)
            if abs(self.xi) < 1e-9:
                excess = -self.sigma * np.log(u_draw)
            else:
                excess = (self.sigma / self.xi) * (np.power(u_draw, -self.xi) - 1.0)
            tail_vals = np.empty(n_tail)
            tail_vals[~is_bump] = self.u + excess
            tail_vals[is_bump] = rng.normal(self.bump_loc, self.bump_scale, n_bump)
            out[in_tail] = tail_vals
        if self.quantize > 0:
            out = np.round(out / self.quantize) * self.quantize
        return np.sort(np.minimum(out, SATURATION_LOGIT))


def build_shapes(route: str = "filegroups/scripts") -> list[Shape]:
    """The shape family: spliced-real plus deliberately adversarial variants."""
    pool = load_pool(route)
    x = pool.benign
    u = float(np.quantile(x, SPLICE_QUANTILE))
    body = np.sort(x[x < u])
    zeta = 1.0 - SPLICE_QUANTILE
    # Scale matched to the route's own measured rise over its deepest
    # observable decade: for an exponential tail the quantile gains
    # sigma*ln(10) per decade of exceedance probability, so the splice starts
    # where the real tail is and climbs at the rate it actually climbs.
    sigma = max(float(np.quantile(x, 0.999) - u) / np.log(10.0), 0.5)
    common = {"body": body, "u": u, "zeta": zeta, "sigma": sigma}
    return [
        # Light, real-ish tail: the fleet's own median shape.
        Shape(name="spliced_light", xi=-0.165, **common),
        # The EVT estimators' own assumption class — the anti-circularity control.
        Shape(name="gpd_pure", xi=0.0, **common),
        # Hard upper endpoint: the tail simply stops.
        Shape(name="truncated", xi=-0.45, **common),
        # Heavier than anything the fleet fits: does the prior over-shrink?
        Shape(name="heavy", xi=0.25, **common),
        # PE's dual-use-tool pileup: a bump of benigns near the top.
        Shape(name="mixture_bump", xi=-0.165, bump_mass=0.02,
              bump_loc=u + 4.0 * sigma, bump_scale=0.5, **common),
        # Score quantisation, as seen on filetypes/c and java_class.
        Shape(name="atoms", xi=-0.165, quantize=0.5, **common),
        # Contaminated tail: a small share of the benigns behave like malware.
        Shape(name="contaminated", xi=-0.165, bump_mass=0.005,
              bump_loc=u + 8.0 * sigma, bump_scale=2.0, **common),
    ]


def run(estimators: list[str], draws: int, out_dir: Path, route: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    base_context = fleet_context()
    # EXP-5 trains on whole pools, so it needs them attached the same way the
    # ladder harness attaches them; without this it silently degrades to its
    # EXP-1 body and the suite would score the wrong estimator.
    from fp_curve_estimators.base import PooledContext  # noqa: PLC0415

    train_pools = {
        t.route: load_pool(t.route).benign
        for t in base_context.tails if t.n_benign >= 200_000
    }
    context = PooledContext(tails=base_context.tails, extras={"full_pools": train_pools})
    log.info(
        "context: %d routes, %d training pools (synthetic shapes are not in the fleet)",
        len(context), len(train_pools),
    )
    shapes = build_shapes(route)
    levels = np.asarray(LEVELS, dtype=np.float64)
    probs = level_to_prob(levels)
    rows = []
    for shape in shapes:
        truth = shape.isf(probs)
        log.info(
            "shape %-14s xi=%+.3f  true L1=%.2f  L25=%.2f  L1000=%.2f (logit)",
            shape.name, shape.xi, truth[1], truth[6], truth[11],
        )
        for m in RUNGS:
            for draw in range(draws):
                rng = np.random.default_rng(draw_seed("synth", shape.name, m, draw))
                sample = shape.rvs(m, rng)
                meta = RouteMeta(f"synth/{shape.name}", "other", m, 0)
                for name in estimators:
                    ctx = context if name in POOLED else None
                    started = time.perf_counter()
                    try:
                        model = get_fit(name)(sample, meta, ctx)
                        thr = model.thresholds(levels)
                    except Exception as exc:  # noqa: BLE001
                        log.warning("%s failed on %s m=%d: %s", name, shape.name, m, exc)
                        continue
                    realized = shape.sf(thr) * 1e8  # exact realized level
                    for i, level in enumerate(levels):
                        rows.append({
                            "estimator": name, "shape": shape.name, "m": m, "draw": draw,
                            "level": float(level),
                            "t_hat": float(thr[i]),
                            "t_true": float(truth[i]),
                            "realized_level": float(realized[i]),
                            "fit_seconds": time.perf_counter() - started,
                        })
    path = out_dir / "synth_points.jsonl"
    with path.open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    log.info("wrote %s (%d rows)", path, len(rows))


def report(out_dir: Path) -> None:
    import pandas as pd  # noqa: PLC0415
    from fp_curve_report import _fmt  # noqa: PLC0415 — shared table formatter

    df = pd.read_json(out_dir / "synth_points.jsonl", lines=True)
    df["abs_logit_err"] = (df["t_hat"] - df["t_true"]).abs()
    # Exact rate error: the realized level a predicted threshold produces on
    # the true distribution, against the level it claims.
    # A prediction above the distribution's entire support produces no false
    # positives at any level: operationally the route stops firing. That is a
    # different failure from a mis-rated threshold, so it is counted, not
    # folded into the rate error as some large number.
    df["dead"] = df["realized_level"] <= 0
    df["log_ratio"] = np.log10(
        np.maximum(df["realized_level"], 1e-6) / np.maximum(df["level"], 1e-6),
    )
    print(f"\n# Synthetic-tail suite — {out_dir}\n")
    print("Exact truth; per-shape, never averaged. Values are median "
          "|log10(realized/claimed FP rate)|.\n")
    deep = df[df["level"] <= 1.0]
    for title, sub in (("All levels", df), ("L0-1 only (no empirical oracle exists)", deep)):
        print(f"\n## {title}\n")
        tab = sub.pivot_table(
            index="estimator", columns="shape", values="log_ratio",
            aggfunc=lambda s: float(np.abs(s).median()),
        )
        print(_fmt(tab, '{:.2f}'))
    print("\n## L0-1 threshold error (median |logit t_hat - logit t_true|)\n")
    tab = deep.pivot_table(
        index="estimator", columns="shape", values="abs_logit_err", aggfunc="median",
    )
    print(_fmt(tab, '{:.2f}'))
    print("\n## L0-1 signed bias by rung (negative = too strict)\n")
    tab = deep.pivot_table(index="estimator", columns="m", values="log_ratio", aggfunc="median")
    print(_fmt(tab, '{:.2f}'))
    print("\n## Dead predictions — threshold above the whole support "
          "(route stops firing entirely)\n")
    tab = df.pivot_table(index="estimator", columns="shape", values="dead", aggfunc="mean")
    print(_fmt(tab, '{:.1%}'))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--estimators", default="b0,exp1,exp2,exp3,exp4,exp5")
    ap.add_argument("--draws", type=int, default=20)
    ap.add_argument("--route", default="filegroups/scripts",
                    help="pool supplying the realistic body")
    ap.add_argument("--out", default="out/experiments/fp_curves/synth")
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    out_dir = Path(args.out)
    if not args.report_only:
        run([e.strip() for e in args.estimators.split(",") if e.strip()],
            args.draws, out_dir, args.route)
    report(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
