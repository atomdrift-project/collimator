#!/usr/bin/env python3
"""EXP-2 ``logit-gpd`` — per-route peaks-over-threshold, penalized.

Classical EVT with the three fixes the version deleted on 2026-06-06 lacked:

1. the fit is in logit space, so the "bounded-support overshoot past 1.0"
   failure cannot occur;
2. the shape is regularised (Gaussian penalty centred on the fleet's measured
   median shape = MAP) with a PWM fallback, so the "shape degeneracy below
   ~500 tail points" failure is bounded rather than explosive;
3. the exceedance threshold is picked automatically by a standardised
   goodness-of-fit scan instead of a hand-chosen quantile.

Bands are profile-likelihood intervals: on short tails the quantile's
likelihood is markedly asymmetric, and a symmetric Laplace band would claim
precision on the tight side that the data do not support. They are computed
at geometric anchors and interpolated in log-level space — the profile is a
smooth function of level, and computing it at all 40+ verification levels per
fit would cost more than the fit itself for no resolution gain.

No pooling: EXP-2 is the cheap classical reference that tells us how much of
EXP-3's benefit actually comes from borrowing strength across routes.
"""

from __future__ import annotations

import numpy as np

from .base import PooledContext, RouteMeta, level_to_prob
from .gpd import XI_PENALTY_SD, XI_PRIOR_MEAN, GPDFit, choose_threshold, profile_likelihood_band
from .tailcurve import TailExtendedCurve

# Level anchors for the profile-likelihood band, spanning the deploy grid.
BAND_ANCHOR_LEVELS = np.array([0.1, 1.0, 10.0, 100.0, 1000.0, 25_000.0])


class LogitGPDCurve(TailExtendedCurve):
    method = "exp2_logit_gpd"

    def __init__(self, meta: RouteMeta, benign_logit: np.ndarray, fit: GPDFit):
        super().__init__(meta, benign_logit, fit, method="exp2_logit_gpd")
        self.exceedances = self.benign[self.benign > fit.u] - fit.u
        self._band_cache: dict[float, tuple[np.ndarray, np.ndarray]] = {}

    def _anchor_halfwidths(self, q: float) -> tuple[np.ndarray, np.ndarray]:
        """Profile half-widths (logit) at the anchor levels, cached per q."""
        cached = self._band_cache.get(q)
        if cached is not None:
            return cached
        lo = np.empty(BAND_ANCHOR_LEVELS.size)
        hi = np.empty(BAND_ANCHOR_LEVELS.size)
        for i, level in enumerate(BAND_ANCHOR_LEVELS):
            centre = float(self._thresholds(np.array([level]))[0])
            p_lo, p_hi = profile_likelihood_band(
                self.exceedances, self.fit, float(level_to_prob(level)), q=q,
            )
            lo[i] = max(centre - (p_lo + self.seam_shift), 0.0)
            hi[i] = max((p_hi + self.seam_shift) - centre, 0.0)
        self._band_cache[q] = (lo, hi)
        return lo, hi

    def _band(self, levels: np.ndarray, q: float) -> tuple[np.ndarray, np.ndarray]:
        point = self._thresholds(levels)
        tail = levels < self.seam_level
        if not tail.any():
            return super()._band(levels, q)
        lo_w, hi_w = self._anchor_halfwidths(q)
        x = np.log(np.clip(levels, 1e-12, None))
        anchors = np.log(BAND_ANCHOR_LEVELS)
        lo = point - np.interp(x, anchors, lo_w)
        hi = point + np.interp(x, anchors, hi_w)
        body_lo, body_hi = super()._band(levels, q)
        # Above the seam the measured order-statistic band is the honest one.
        lo = np.where(tail, lo, body_lo)
        hi = np.where(tail, hi, body_hi)
        return np.minimum(lo, point), np.maximum(hi, point)


def fit(
    logit_benign: np.ndarray,
    route_meta: RouteMeta,
    context: PooledContext | None = None,  # noqa: ARG001 — per-route by design
) -> LogitGPDCurve:
    benign = np.sort(np.asarray(logit_benign, dtype=np.float64))
    tail_fit = choose_threshold(benign, xi_prior=(XI_PRIOR_MEAN, XI_PENALTY_SD))
    return LogitGPDCurve(route_meta, benign, tail_fit)
