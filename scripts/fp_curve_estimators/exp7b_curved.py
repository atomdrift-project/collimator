#!/usr/bin/env python3
"""EXP-7b ``curved`` — a straight line with the fleet's curvature borrowed.

EXP-7 showed that a constant logits-per-decade slope extrapolates ~94x too
strict and silences 72% of the strict band: real benign tails decelerate, and
that curvature carries real signal. EXP-3b captures it by fitting a shape per
route, at the cost of a hierarchy, a posterior and three construction bugs.

This keeps the curvature and drops the fitting. A GPD tail rises by
``s * 10^(xi*d)`` logits per decade at depth d, so its quantile is

    threshold(L) = t_anchor + (s / (xi*ln10)) * (10^(xi*d) - 1)

with ``s`` the route's own measured rise per decade at the anchor, and ``xi``
NOT fitted — it is the fleet's median shape, a single constant for everyone.
Two numbers per route, one of them borrowed, no optimiser, no posterior.
"""

from __future__ import annotations

import numpy as np

from .base import PooledContext, RouteMeta
from .exp7_loglinear import LogLinearCurve, family_slopes, fit as _linear_fit

# The fleet's median shape, measured across all 73 routes' full OOF pools.
# Constant for every route: routes cannot estimate this reliably and the ones
# that try (java_class at +0.40) are exactly the ones that detonate.
FLEET_CURVATURE = -0.165


class CurvedCurve(LogLinearCurve):
    method = "exp7b_curved"

    def _thresholds(self, levels: np.ndarray) -> np.ndarray:
        body = self.body_model.body(levels)
        d = np.maximum(np.log10(self.anchor_level / np.maximum(levels, 1e-12)), 0.0)
        xi = FLEET_CURVATURE
        rise = (self.slope / (xi * np.log(10.0))) * (np.power(10.0, xi * d) - 1.0)
        return np.where(levels < self.anchor_level, self.t_anchor + rise, body)

    def row_extras(self, level: float) -> dict[str, object]:
        extras = super().row_extras(level)
        extras["curvature"] = FLEET_CURVATURE
        return extras


def fit(logit_benign: np.ndarray, route_meta: RouteMeta,
        context: PooledContext | None = None) -> CurvedCurve:
    linear = _linear_fit(logit_benign, route_meta, context)
    return CurvedCurve(route_meta, logit_benign, linear.slope, linear.own_slope,
                       linear.family_slope, linear.weight)


def prepare(context: PooledContext) -> None:
    family_slopes(context)
