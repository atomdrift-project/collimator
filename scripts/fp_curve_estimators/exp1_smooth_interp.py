#!/usr/bin/env python3
"""EXP-1 ``smooth-interp`` — smoothed order statistics, no extrapolation.

The honesty control. Harrell-Davis quantile estimates on the logit benign
sample give a smooth measured curve (so L21 and L22 have distinct, defined
answers instead of nearest-anchor behaviour), a shape-preserving monotone
PCHIP interpolant carries it between anchors, and below the sample's own
1-FP floor the curve **clamps** rather than extrapolating.

That clamp is the point: EXP-1 fails "full dynamic range" by design, so any
extrapolating estimator has to beat it on tail calibration *above* the floor
to justify the risk it takes *below* it.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

from .base import (
    CurveModel,
    PooledContext,
    RouteMeta,
    detect_saturation,
    floor_level,
    harrell_davis,
    level_to_prob,
    order_statistic_band,
)

# Anchors run from the sample's 1-FP floor up to a 10% benign FP rate. The
# deploy grid tops out at L25000 (0.025%), so the extra decades above it exist
# only to give the interpolant well-conditioned support at its loose end.
ANCHOR_LEVEL_CAP = 1e7
N_ANCHORS = 64


class SmoothInterpCurve(CurveModel):
    method = "exp1_smooth_interp"

    def __init__(self, meta: RouteMeta, benign_logit: np.ndarray):
        self.benign = np.sort(np.asarray(benign_logit, dtype=np.float64))
        n = self.benign.size
        super().__init__(
            meta=meta,
            max_observed_logit=float(self.benign[-1]),
            fit_floor_level=floor_level(n),
            saturation=detect_saturation(self.benign),
        )
        lo = self.fit_floor_level
        hi = max(ANCHOR_LEVEL_CAP, lo * 10.0)
        self.anchor_levels = np.geomspace(lo, hi, N_ANCHORS)
        q = np.clip(1.0 - level_to_prob(self.anchor_levels), 0.0, 1.0)
        anchors = harrell_davis(self.benign, q)
        # HD is monotone in q by construction; this only removes float noise
        # at neighbouring deep quantiles, where consecutive anchors can differ
        # by less than an ulp. Smoothing the fit is fair — enforcing
        # monotonicity on the *emitted* curve would hide a broken tail model,
        # which is why the harness measures that separately.
        self.anchor_thresholds = np.minimum.accumulate(anchors)
        self._x = np.log(self.anchor_levels)
        self._spline = PchipInterpolator(self._x, self.anchor_thresholds, extrapolate=False)

    def body(self, levels: np.ndarray) -> np.ndarray:
        """The smooth measured curve: HD anchors, PCHIP between, clamped below.

        This is the implementation; :meth:`_thresholds` is the same thing for
        EXP-1 itself. Subclasses that replace the sub-floor region (EXP-5) call
        ``body`` for the measured part, so the two must not be the same method
        or the override recurses.
        """
        x = np.log(np.clip(np.asarray(levels, dtype=np.float64), 1e-12, None))
        clamped = np.clip(x, self._x[0], self._x[-1])
        return np.asarray(self._spline(clamped), dtype=np.float64)

    def _thresholds(self, levels: np.ndarray) -> np.ndarray:
        return self.body(levels)

    def _band(self, levels: np.ndarray, q: float) -> tuple[np.ndarray, np.ndarray]:
        lo, hi = order_statistic_band(self.benign, levels, q)
        point = self._thresholds(levels)
        return np.minimum(lo, point), np.maximum(hi, point)

    def is_extrapolated(self, level: float) -> bool:
        """Never extrapolates: sub-floor rows are the floor value, clamped."""
        return False

    def row_extras(self, level: float) -> dict[str, object]:
        return {"clamped_below_floor": bool(level < self.fit_floor_level)}


def fit(
    logit_benign: np.ndarray,
    route_meta: RouteMeta,
    context: PooledContext | None = None,  # noqa: ARG001 — control: no pooling
) -> SmoothInterpCurve:
    return SmoothInterpCurve(route_meta, logit_benign)
