#!/usr/bin/env python3
"""EXP-6 ``median-ensemble`` — pointwise median of the tail estimators.

Insurance against the failure mode that actually hurts: a single estimator
detonating on a single route. EXP-2 and EXP-3 both pin to the score ceiling on
ELF and return zero recall below L100; EXP-4 stays alive there. On other
routes the roles swap. Taking the pointwise median means no one member's
blowup can carry the answer, and a member that goes silent is outvoted rather
than obeyed.

Two properties make this cheap rather than clever:

* the median of monotone-decreasing curves is monotone-decreasing, so
  smoothness and dial resolution survive by construction;
* it needs no new theory, no new fit — it reuses whatever members are
  registered.

What it cannot do is beat its best member on a route where that member is
already fine; the median sits between them by definition. It buys worst-case
behaviour, not average-case accuracy, and the leaderboard should show exactly
that trade.
"""

from __future__ import annotations

import numpy as np

from .base import CurveModel, PooledContext, RouteMeta, detect_saturation, floor_level

MEMBERS: tuple[str, ...] = ("exp2", "exp3b", "exp4")


class MedianEnsembleCurve(CurveModel):
    method = "exp6_median_ensemble"

    def __init__(self, meta: RouteMeta, benign_logit: np.ndarray, members: list[CurveModel]):
        self.benign = np.sort(np.asarray(benign_logit, dtype=np.float64))
        self.members = members
        super().__init__(
            meta=meta,
            max_observed_logit=float(self.benign[-1]),
            fit_floor_level=floor_level(self.benign.size),
            saturation=detect_saturation(self.benign),
        )

    def _thresholds(self, levels: np.ndarray) -> np.ndarray:
        stack = np.stack([m.thresholds(levels) for m in self.members])
        return np.median(stack, axis=0)

    def _band(self, levels: np.ndarray, q: float) -> tuple[np.ndarray, np.ndarray]:
        # The members disagree exactly where the answer is uncertain, so the
        # envelope of their bands is the honest interval — wider than any one
        # member claims, which is the point.
        los, his = [], []
        for m in self.members:
            lo, hi = m._band(levels, q)  # noqa: SLF001 — members are ours
            los.append(lo)
            his.append(hi)
        point = self._thresholds(levels)
        return np.minimum(np.min(los, axis=0), point), np.maximum(np.max(his, axis=0), point)

    def row_extras(self, level: float) -> dict[str, object]:
        vals = [float(m.thresholds(np.array([level]))[0]) for m in self.members]
        return {
            "members": list(MEMBERS),
            "member_spread_logit": float(max(vals) - min(vals)),
        }


def fit(
    logit_benign: np.ndarray,
    route_meta: RouteMeta,
    context: PooledContext | None = None,
) -> MedianEnsembleCurve:
    from . import get_fit  # noqa: PLC0415 — avoids a circular import at module load

    members = [get_fit(name)(logit_benign, route_meta, context) for name in MEMBERS]
    return MedianEnsembleCurve(route_meta, logit_benign, members)


def prepare(context: PooledContext) -> None:
    """Prepare every member's cross-route structure once, pre-fork."""
    import importlib  # noqa: PLC0415

    from . import _MODULES  # noqa: PLC0415

    for name in MEMBERS:
        mod = importlib.import_module(f"{__package__}.{_MODULES[name]}")
        hook = getattr(mod, "prepare", None)
        if hook is not None:
            hook(context)
