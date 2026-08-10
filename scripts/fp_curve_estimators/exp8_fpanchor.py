#!/usr/bin/env python3
"""EXP-8 ``fpanchor`` — the curve through measured false-positive counts.

Every other estimator here fits a tail model and reads quantiles off it. This
one asks what is actually known: the k-th largest benign score IS the
threshold that admits exactly k false positives, at level k*1e8/n. Those are
measurements, not estimates, and there are dozens of them per route. So the
curve is the interpolation through them, and the only extrapolation is the
single step below the 1-FP point.

That single step is the whole design question, and it is why the slope is
measured at the *extreme* rather than over the body: EXP-7 and EXP-7b fitted
their slope across 5-5000 FP and came out ~35-94x too strict, because a benign
tail flattens faster than its body implies. The FP1->FP2 gap is already inside
the flattening.

Two variants of that step, since one order-statistic gap is a noisy thing to
lean on:

* ``span=2``  — the literal construction: slope from the 1-FP and 2-FP points;
* ``span=10`` — slope fitted over the deepest decade of anchors (1..10 FP),
  trading a little locality for a lot less variance.

L0 is one further step along the same line, so there is no cliff between L0 and
L1 — just the next point on the curve.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

from .base import (
    CurveModel, PooledContext, RouteMeta, detect_saturation, floor_level,
    order_statistic_band,
)

# Anchors are FP counts: dense at the extreme, geometric out to 5% of the pool.
def _anchor_counts(n: int) -> np.ndarray:
    top = max(int(0.05 * n), 12)
    counts = np.unique(np.concatenate([
        np.arange(1, 11), np.geomspace(10, top, 28).astype(int),
    ]))
    return counts[(counts >= 1) & (counts < n)]


class FPAnchorCurve(CurveModel):
    method = "exp8_fpanchor"

    def __init__(self, meta: RouteMeta, benign_logit: np.ndarray, span: int = 2):
        self.benign = np.sort(np.asarray(benign_logit, dtype=np.float64))
        n = self.benign.size
        super().__init__(meta=meta, max_observed_logit=float(self.benign[-1]),
                         fit_floor_level=floor_level(n),
                         saturation=detect_saturation(self.benign))
        counts = _anchor_counts(n)
        self.anchor_levels = counts / n * 1e8
        self.anchor_thresholds = np.minimum.accumulate(self.benign[n - counts])
        self._x = np.log10(self.anchor_levels)
        self._spline = PchipInterpolator(self._x, self.anchor_thresholds, extrapolate=False)
        # Rise per decade at the extreme, from the deepest `span` anchors.
        k = min(span, counts.size)
        if k >= 2:
            xs = self._x[:k]
            self.slope = float(max(-np.polyfit(xs, self.anchor_thresholds[:k], 1)[0], 1e-3))
        else:
            self.slope = 1.0
        self.span = span

    def _thresholds(self, levels: np.ndarray) -> np.ndarray:
        x = np.log10(np.maximum(levels, 1e-12))
        inside = np.clip(x, self._x[0], self._x[-1])
        out = np.asarray(self._spline(inside), dtype=np.float64)
        below = x < self._x[0]
        if below.any():
            out = np.where(below, self.anchor_thresholds[0] + self.slope * (self._x[0] - x), out)
        return out

    def _band(self, levels: np.ndarray, q: float) -> tuple[np.ndarray, np.ndarray]:
        lo, hi = order_statistic_band(self.benign, levels, q)
        point = self._thresholds(levels)
        below = levels < self.anchor_levels[0]
        if below.any():
            d = np.log10(self.anchor_levels[0] / np.maximum(levels[below], 1e-12))
            w = 0.5 * self.slope * d
            lo = lo.copy(); hi = hi.copy()
            lo[below] = point[below] - w
            hi[below] = point[below] + w
        return np.minimum(lo, point), np.maximum(hi, point)

    def row_extras(self, level: float) -> dict[str, object]:
        return {"slope_at_extreme": self.slope, "anchor_span_fp": self.span,
                "one_fp_level": float(self.anchor_levels[0]),
                "measured": bool(level >= self.anchor_levels[0])}


def fit(logit_benign, route_meta, context=None):  # noqa: ARG001
    return FPAnchorCurve(route_meta, logit_benign, span=2)
