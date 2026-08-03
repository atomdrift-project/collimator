#!/usr/bin/env python3
"""EXP-3b ``anchored-tail`` — EXP-3 with a shorter, better-behaved extrapolation.

Two changes to EXP-3, both aimed at defects the harness measured rather than
at anything that merely sounded good.

**1. The tail is anchored at the deepest level the sample can resolve, not at
the peaks-over-threshold cut.** EXP-3 hands everything below its POT threshold
to the GPD, and that threshold sits around L100,000-L1,000,000 — so on PE it
extrapolates 3.6 decades to reach L25 even though PE can *measure* down to
L2,438 (5 observed FP). Extrapolation distance is the dominant error term in
every table this benchmark produces, so the tail is re-based onto the deepest
measured point instead: shape still fitted on the broad tail (it needs the
exceedances), but the curve is forced through the measurement and extrapolates
only from there. On PE that is 2.0 decades instead of 3.6; on scripts, 0.8.
It also means the measured region is measured again rather than restated by a
model.

**2. The shape is shrunk toward the family mean as extrapolation deepens.**
The Weissman quantile grows like ``(p/p_a)^-xi``, i.e. exponentially in
xi x decades, so a positive shape detonates within one decade — which is
exactly how ELF (xi = +0.099) ended up pinned at the score ceiling with zero
recall at L25. A local shape estimate describes the tail *near* the data; the
further past it you go, the less it should be trusted and the more the family
prior should carry. The effective shape therefore relaxes from the route's own
estimate toward the hierarchical prior with depth.

Everything else — the hierarchy, the Laplace posterior, the API — is EXP-3's.
"""

from __future__ import annotations

import numpy as np
from scipy.special import expit

from .base import (
    CurveModel,
    PooledContext,
    RouteMeta,
    detect_saturation,
    floor_level,
    level_to_prob,
    order_statistic_band,
)
from .exp1_smooth_interp import SmoothInterpCurve
from .exp3_pooled_tail import Hierarchy, build_hierarchy
from .gpd import XI_MAX, XI_MIN, GPDFit, choose_threshold

# The tail is anchored where the sample has this many observed false
# positives — the same "measurable" bar the rest of the benchmark uses.
ANCHOR_FP = 5.0
# Width of the logistic hand-over between measured body and modelled tail, in
# decades of level. A hard switch would put a kink at the anchor; both
# branches agree there by construction, so a narrow blend is enough.
BLEND_DECADES = 0.15
# Depth (decades below the anchor) at which the effective shape sits halfway
# between the route's own estimate and its family prior.
SHRINK_HALF_LIFE = 1.0
# Depth grid used to integrate the growth rate (0 to the deepest level asked).
RATE_GRID = 256


class AnchoredTailCurve(CurveModel):
    method = "exp3b_anchored_tail"

    def __init__(
        self,
        meta: RouteMeta,
        benign_logit: np.ndarray,
        fit: GPDFit,
        hierarchy: Hierarchy,
        prior: tuple[float, float],
        band_seed: int = 0,
    ):
        self.benign = np.sort(np.asarray(benign_logit, dtype=np.float64))
        self.body_model = SmoothInterpCurve(meta, self.benign)
        self.fit = fit
        self.hierarchy = hierarchy
        self.prior = prior
        self._rng = np.random.default_rng(band_seed)
        n = self.benign.size
        super().__init__(
            meta=meta,
            max_observed_logit=float(self.benign[-1]),
            fit_floor_level=floor_level(n),
            saturation=detect_saturation(self.benign),
        )
        # Anchor: the deepest level this sample resolves, and the measured
        # threshold there (read off the smoothed body, so the hand-over is
        # smooth rather than landing on a single noisy order statistic).
        self.anchor_level = float(ANCHOR_FP * 1e8 / max(n, 1))
        self.anchor_prob = float(level_to_prob(self.anchor_level))
        self.t_anchor = float(self.body_model.body(np.array([self.anchor_level]))[0])
        # Re-base the GPD scale from the fitted threshold u onto the anchor
        # (sigma(u2) = sigma(u1) + xi*(u2-u1) — the standard threshold-stability
        # relation). A non-positive result means the fitted tail claims an
        # endpoint below the anchor, which the data contradicts; fall back to
        # the unrebased scale in that case.
        rebased = fit.sigma + fit.xi * (self.t_anchor - fit.u)
        self.sigma_anchor = float(rebased) if rebased > 1e-6 else float(fit.sigma)

    # -- tail ---------------------------------------------------------------

    def _effective_xi(self, depth: np.ndarray, xi: float) -> np.ndarray:
        """Shape at each extrapolation depth, relaxed toward the family prior."""
        weight = depth / (depth + SHRINK_HALF_LIFE)
        return np.clip((1.0 - weight) * xi + weight * self.prior[0], XI_MIN, XI_MAX)

    def _tail(self, levels: np.ndarray, xi: float, sigma: float) -> np.ndarray:
        """Threshold at each level, built by integrating the local growth rate.

        Shrinking the shape inside the closed-form GPD quantile does not work:
        the quantile's asymptote is a function of xi, so relaxing xi with depth
        moves the endpoint and the curve can come back *down* — which is how
        a degenerate fit (text at m=800 pins xi at +0.35) produced
        non-monotone output. What is actually meant by "trust the local shape
        locally" is a statement about the *rate*, so that is what is shrunk:
        a GPD grows by ``sigma*ln(10)*10^(xi*s)`` per decade at depth s, the
        shape in that rate relaxes toward the family prior, and the threshold
        is the integral of a strictly positive rate. Monotone by construction,
        no projection needed, and it decelerates rather than detonating.
        """
        p = level_to_prob(np.maximum(levels, 1e-12))
        ratio = np.clip(p / max(self.anchor_prob, 1e-300), 1e-300, None)
        depth = np.maximum(-np.log10(ratio), 0.0)
        grid = np.linspace(0.0, max(float(depth.max()), 1e-6), RATE_GRID)
        rate = sigma * np.log(10.0) * np.power(
            10.0, np.clip(self._effective_xi(grid, xi) * grid, -30.0, 30.0),
        )
        cumulative = np.concatenate([
            [0.0], np.cumsum(0.5 * (rate[1:] + rate[:-1]) * np.diff(grid)),
        ])
        return self.t_anchor + np.interp(depth, grid, cumulative)

    def _blend_weight(self, levels: np.ndarray) -> np.ndarray:
        """1 where the sample measures, 0 where the model takes over."""
        x = np.log10(np.maximum(levels, 1e-12))
        return expit((x - np.log10(self.anchor_level)) / BLEND_DECADES)

    def _thresholds(self, levels: np.ndarray) -> np.ndarray:
        body = self.body_model.body(levels)
        tail = self._tail(levels, self.fit.xi, self.sigma_anchor)
        w = self._blend_weight(levels)
        return w * body + (1.0 - w) * tail

    def _band(self, levels: np.ndarray, q: float) -> tuple[np.ndarray, np.ndarray]:
        lo, hi = order_statistic_band(self.benign, levels, q)
        below = levels < self.anchor_level
        if below.any() and np.all(np.isfinite(self.fit.cov)):
            draws = self._rng.multivariate_normal(
                [self.fit.xi, float(np.log(max(self.sigma_anchor, 1e-9)))],
                self.fit.cov, size=512,
            )
            sub = levels[below]
            vals = np.stack([
                self._tail(sub, float(np.clip(d[0], XI_MIN, XI_MAX)),
                           float(np.exp(np.clip(d[1], -30, 30))))
                for d in draws
            ])
            lo = lo.copy()
            hi = hi.copy()
            lo[below] = np.quantile(vals, (1.0 - q) / 2.0, axis=0)
            hi[below] = np.quantile(vals, 1.0 - (1.0 - q) / 2.0, axis=0)
        point = self._thresholds(levels)
        return np.minimum(lo, point), np.maximum(hi, point)

    def row_extras(self, level: float) -> dict[str, object]:
        depth = max(np.log10(self.anchor_level / max(level, 1e-12)), 0.0)
        return {
            "xi": self.fit.xi,
            "xi_effective": float(self._effective_xi(np.array([depth]), self.fit.xi)[0]),
            "anchor_level": self.anchor_level,
            "extrapolation_decades": float(depth),
            "sigma_anchor": self.sigma_anchor,
            "prior_mean": self.prior[0],
            "prior_sd": self.prior[1],
            "shrinkage_z": (self.fit.xi - self.prior[0]) / max(self.prior[1], 1e-9),
            "n_exceedances": self.fit.k,
        }


def fit(
    logit_benign: np.ndarray,
    route_meta: RouteMeta,
    context: PooledContext | None = None,
) -> AnchoredTailCurve:
    ctx = context if context is not None else PooledContext()
    hierarchy = build_hierarchy(ctx)
    prior = hierarchy.prior_for(route_meta.filegroup)
    benign = np.sort(np.asarray(logit_benign, dtype=np.float64))
    tail_fit = choose_threshold(benign, xi_prior=prior)
    return AnchoredTailCurve(route_meta, benign, tail_fit, hierarchy, prior)


def prepare(context: PooledContext) -> None:
    """Fit the hierarchy once in the parent, pre-fork."""
    build_hierarchy(context)
