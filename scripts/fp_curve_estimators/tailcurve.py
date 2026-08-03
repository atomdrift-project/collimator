#!/usr/bin/env python3
"""Curve made of EXP-1's measured body plus a GPD tail above the seam.

EXP-2 and EXP-3 differ only in how the tail is fitted (fixed penalty vs
hierarchical shrinkage); the way a tail is grafted onto the measured body is
identical, so it lives here once.

Continuity at the seam is enforced explicitly: the Weissman quantile returns
exactly ``u`` at the exceedance rate ``zeta``, and the body curve returns its
own (Harrell-Davis smoothed) value there, so the tail branch is shifted by
the difference. Without that, a curve consumed by scan would step at the
seam — exactly the artefact this whole exercise exists to remove.
"""

from __future__ import annotations

import numpy as np

from .base import (
    SATURATION_LOGIT,
    CurveModel,
    RouteMeta,
    detect_saturation,
    floor_level,
    level_to_prob,
    order_statistic_band,
)
from .exp1_smooth_interp import SmoothInterpCurve
from .gpd import GPDFit, gpd_quantile, posterior_quantile_band


def observed_decade_rise(sorted_logits: np.ndarray) -> float:
    """Observed threshold rise per decade of FP rate, near the sample's floor.

    Measured as ``x_(k) - x_(10k)`` for k in 1/10/100 (the k-th largest score):
    how far the threshold has to climb to go from 10k false positives down to
    k. Reported as a diagnostic — routes whose top decade is a single
    quantisation atom score 0 here, which is the signal that their tail shape
    is not estimable from the data at all.
    """
    x = np.asarray(sorted_logits, dtype=np.float64)
    n = x.size
    rises = [
        float(x[n - k] - x[n - 10 * k])
        for k in (1, 10, 100)
        if 10 * k <= n
    ]
    return max([r for r in rises if np.isfinite(r)] or [0.0])


class TailExtendedCurve(CurveModel):
    """Measured body below the seam, extrapolated GPD tail above it."""

    def __init__(
        self,
        meta: RouteMeta,
        benign_logit: np.ndarray,
        fit: GPDFit,
        *,
        method: str,
        band_seed: int = 0,
    ):
        self.benign = np.sort(np.asarray(benign_logit, dtype=np.float64))
        self.body_model = SmoothInterpCurve(meta, self.benign)
        self.fit = fit
        self.method = method
        self._rng = np.random.default_rng(band_seed)
        super().__init__(
            meta=meta,
            max_observed_logit=float(self.benign[-1]),
            fit_floor_level=floor_level(self.benign.size),
            saturation=detect_saturation(self.benign),
        )
        # Levels stricter than this are the GPD's responsibility.
        self.seam_level = float(fit.zeta * 1e8)
        self.seam_shift = float(
            self.body_model.body(np.array([self.seam_level]))[0] - fit.u,
        )
        self.decade_rise = observed_decade_rise(self.benign)
        self.n_capped = 0

    def _thresholds(self, levels: np.ndarray) -> np.ndarray:
        out = self.body_model.body(levels)
        tail = levels < self.seam_level
        if tail.any():
            out = out.copy()
            out[tail] = gpd_quantile(self.fit, level_to_prob(levels[tail])) + self.seam_shift
        # The physical ceiling clamp itself lives in CurveModel.thresholds (it
        # applies to every estimator); this only records how often this fit
        # ran into it, since a curve pinned at the ceiling has no dial left.
        self.n_capped = int(np.sum(out > SATURATION_LOGIT))
        return out

    def _band(self, levels: np.ndarray, q: float) -> tuple[np.ndarray, np.ndarray]:
        lo, hi = order_statistic_band(self.benign, levels, q)
        tail = levels < self.seam_level
        if tail.any():
            t_lo, t_hi = posterior_quantile_band(
                self.fit, level_to_prob(levels[tail]), q=q, rng=self._rng,
            )
            lo = lo.copy()
            hi = hi.copy()
            lo[tail] = t_lo + self.seam_shift
            hi[tail] = t_hi + self.seam_shift
        point = self._thresholds(levels)
        return np.minimum(lo, point), np.maximum(hi, point)

    def row_extras(self, level: float) -> dict[str, object]:
        return {
            "xi": self.fit.xi,
            "sigma": self.fit.sigma,
            "seam_level": self.seam_level,
            "n_exceedances": self.fit.k,
            "gpd_branch": bool(level < self.seam_level),
            "fit_method": self.fit.method,
            "decade_rise": self.decade_rise,
            "at_ceiling": bool(
                self._thresholds(np.array([max(level, 1e-3)]))[0] >= SATURATION_LOGIT - 1e-12,
            ),
        }
