#!/usr/bin/env python3
"""EXP-7 ``loglinear`` — the simplest thing the data supports.

Every table in this benchmark shows the same structure: in logit space, a
benign tail's threshold rises by a roughly constant number of logits per
decade of FP rate. PE gains 8.9 logits per decade near its floor; scripts,
1.8; general, 2.1. That is the whole signal. The GPD, the three-level
hierarchy, the Laplace posterior and the depth-shrunk shape integrated over a
256-point grid all exist to estimate a *curvature correction* on top of that
line — and between them they produced three construction bugs (a non-monotone
blend, a projection that turned decreases into ties, an asymptote that moved
when the shape was shrunk).

So this estimator is the line:

    threshold(L) = t_anchor + slope * log10(anchor_level / L)

with two measurements and one borrowed number:

* ``t_anchor`` — the threshold at the deepest level the sample resolves
  (5 observed FP), read off the same smoothed body EXP-1 uses;
* ``slope`` — least-squares fit of threshold against log10(level) over the
  decades the sample actually measures;
* the family's median slope, which the route's own slope is shrunk toward in
  proportion to how little data it has.

It is monotone because the slope is positive, smooth because it is a straight
line joined to a smooth body, and it cannot detonate because a line cannot.
If it matches the elaborate version on the ladder, the elaborate version has
not earned its complexity.
"""

from __future__ import annotations

import numpy as np

from .base import (
    CurveModel,
    PooledContext,
    RouteMeta,
    detect_saturation,
    floor_level,
    order_statistic_band,
)
from .exp1_smooth_interp import SmoothInterpCurve

# The anchor sits where the sample has this many observed false positives, and
# the slope is fitted over the decades between there and this many.
ANCHOR_FP = 5.0
SLOPE_FIT_FP = 5_000.0
# Shrinkage: a route's own slope carries full weight once it has this many
# false positives to fit it over; below that the family median carries the rest.
SLOPE_CONFIDENCE_FP = 200.0
# Slopes below this are noise (a quantised tail measures zero rise); above it,
# nothing in the fleet climbs faster.
MIN_SLOPE, MAX_SLOPE = 0.05, 12.0
_FAMILY_SLOPES: dict[tuple[str, ...], dict[str, float]] = {}


def _measure_slope(benign: np.ndarray) -> tuple[float, float]:
    """(logits per decade, false positives the fit spanned) for one sample."""
    n = benign.size
    lo_fp, hi_fp = ANCHOR_FP, min(SLOPE_FIT_FP, n / 4.0)
    if hi_fp <= lo_fp * 2:
        return float("nan"), 0.0
    counts = np.unique(np.geomspace(lo_fp, hi_fp, 24).astype(int))
    counts = counts[(counts >= 1) & (counts < n)]
    if counts.size < 3:
        return float("nan"), 0.0
    thresholds = benign[n - counts]
    decades = np.log10(counts / lo_fp)  # 0 at the anchor, growing as it loosens
    # Threshold falls as the level loosens, so the rise per decade is -slope.
    slope = -np.polyfit(decades, thresholds, 1)[0]
    return float(slope), float(hi_fp)


def family_slopes(context: PooledContext) -> dict[str, float]:
    """Median slope per filegroup, measured from the context routes."""
    key = tuple(sorted(t.route for t in context.tails))
    cached = _FAMILY_SLOPES.get(key)
    if cached is not None:
        return cached
    per_family: dict[str, list[float]] = {}
    for tail in context.tails:
        slope, _ = _measure_slope(tail.tail_logits)
        if np.isfinite(slope) and slope > MIN_SLOPE:
            per_family.setdefault(tail.filegroup, []).append(slope)
    out = {k: float(np.median(v)) for k, v in per_family.items()}
    everything = [s for v in per_family.values() for s in v]
    out["__global__"] = float(np.median(everything)) if everything else 2.0
    _FAMILY_SLOPES[key] = out
    return out


class LogLinearCurve(CurveModel):
    method = "exp7_loglinear"

    def __init__(self, meta: RouteMeta, benign_logit: np.ndarray, slope: float,
                 own_slope: float, family_slope: float, weight: float):
        self.benign = np.sort(np.asarray(benign_logit, dtype=np.float64))
        self.body_model = SmoothInterpCurve(meta, self.benign)
        n = self.benign.size
        super().__init__(
            meta=meta,
            max_observed_logit=float(self.benign[-1]),
            fit_floor_level=floor_level(n),
            saturation=detect_saturation(self.benign),
        )
        self.anchor_level = float(ANCHOR_FP * 1e8 / max(n, 1))
        self.t_anchor = float(self.body_model.body(np.array([self.anchor_level]))[0])
        self.slope = float(np.clip(slope, MIN_SLOPE, MAX_SLOPE))
        self.own_slope = own_slope
        self.family_slope = family_slope
        self.weight = weight

    def _thresholds(self, levels: np.ndarray) -> np.ndarray:
        body = self.body_model.body(levels)
        decades = np.log10(self.anchor_level / np.maximum(levels, 1e-12))
        line = self.t_anchor + self.slope * np.maximum(decades, 0.0)
        return np.where(levels < self.anchor_level, line, body)

    def _band(self, levels: np.ndarray, q: float) -> tuple[np.ndarray, np.ndarray]:
        # Below the anchor the uncertainty is the slope's, and it compounds
        # with every decade extrapolated — so the band is the slope's own
        # spread times the distance travelled. Above it, the measured
        # order-statistic interval applies.
        lo, hi = order_statistic_band(self.benign, levels, q)
        below = levels < self.anchor_level
        if below.any():
            decades = np.log10(self.anchor_level / np.maximum(levels[below], 1e-12))
            spread = abs(self.own_slope - self.family_slope) if np.isfinite(self.own_slope) else self.slope
            width = max(spread, 0.25 * self.slope) * decades
            point = self._thresholds(levels)
            lo = lo.copy()
            hi = hi.copy()
            lo[below] = point[below] - width
            hi[below] = point[below] + width
        point = self._thresholds(levels)
        return np.minimum(lo, point), np.maximum(hi, point)

    def row_extras(self, level: float) -> dict[str, object]:
        return {
            "slope_logits_per_decade": self.slope,
            "own_slope": self.own_slope,
            "family_slope": self.family_slope,
            "own_slope_weight": self.weight,
            "anchor_level": self.anchor_level,
        }


def fit(
    logit_benign: np.ndarray,
    route_meta: RouteMeta,
    context: PooledContext | None = None,
) -> LogLinearCurve:
    benign = np.sort(np.asarray(logit_benign, dtype=np.float64))
    own, span = _measure_slope(benign)
    families = family_slopes(context) if context is not None else {"__global__": 2.0}
    family = families.get(route_meta.filegroup, families["__global__"])
    # How much of its own slope a route has earned: all of it once the fit
    # spans SLOPE_CONFIDENCE_FP false positives, none of it at zero.
    weight = float(np.clip(span / SLOPE_CONFIDENCE_FP, 0.0, 1.0))
    if not np.isfinite(own) or own <= MIN_SLOPE:
        weight, own = 0.0, float("nan")
    slope = weight * (own if np.isfinite(own) else family) + (1.0 - weight) * family
    return LogLinearCurve(route_meta, benign, slope, own, family, weight)


def prepare(context: PooledContext) -> None:
    family_slopes(context)
