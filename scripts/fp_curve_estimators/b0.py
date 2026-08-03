#!/usr/bin/env python3
"""B0 — the incumbent estimator, exactly as shipped.

Wraps ``collimator.thresholds.quantile_severity_threshold`` so the baseline in
the leaderboard is the shipped function itself (including the 25k low-volume
cliff and the absolute-FP reinterpretation below it), not a reimplementation
that might drift from it.

The only thing added here is a confidence band: the shipped estimator has
none, and metric 4 needs one. It is the distribution-free order-statistic
interval — the honest band for an empirical quantile — and it is labelled as
harness-supplied, not as something B0 ships.
"""

from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, "src")

from collimator.thresholds import quantile_severity_threshold  # noqa: E402

from .base import (  # noqa: E402
    CurveModel,
    PooledContext,
    RouteMeta,
    detect_saturation,
    floor_level,
    from_logit,
    order_statistic_band,
    to_logit,
)


class B0Curve(CurveModel):
    method = "b0_incumbent"

    def __init__(self, meta: RouteMeta, benign_logit: np.ndarray):
        self.benign = np.sort(np.asarray(benign_logit, dtype=np.float64))
        # The shipped function works in probability space; hand it exactly the
        # probabilities the model produced.
        self.benign_prob = np.asarray(from_logit(self.benign), dtype=np.float64)
        super().__init__(
            meta=meta,
            max_observed_logit=float(self.benign[-1]),
            fit_floor_level=floor_level(self.benign.size),
            saturation=detect_saturation(self.benign),
        )
        self.methods_used: set[str] = set()

    def _thresholds(self, levels: np.ndarray) -> np.ndarray:
        out = np.empty(levels.shape, dtype=np.float64)
        for i, level in enumerate(levels):
            thr, method = quantile_severity_threshold(
                self.benign_prob, target_per_million=float(level) / 100.0,
            )
            self.methods_used.add(method)
            out[i] = self.max_observed_logit if thr is None else float(to_logit(thr))
        return out

    def _band(self, levels: np.ndarray, q: float) -> tuple[np.ndarray, np.ndarray]:
        lo, hi = order_statistic_band(self.benign, levels, q)
        point = self._thresholds(levels)
        return np.minimum(lo, point), np.maximum(hi, point)

    def row_extras(self, level: float) -> dict[str, object]:
        return {"regime": sorted(self.methods_used)}


def fit(
    logit_benign: np.ndarray,
    route_meta: RouteMeta,
    context: PooledContext | None = None,  # noqa: ARG001 — B0 is per-route by construction
) -> B0Curve:
    return B0Curve(route_meta, logit_benign)
