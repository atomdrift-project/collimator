#!/usr/bin/env python3
"""EXP-3c ``calibrated-tail`` — EXP-3b with its measured bias corrected.

The ladder does not just rank estimators, it *quantifies* how each one is
wrong: EXP-3b's thresholds are systematically too low (too loose) by a
depth-dependent amount, +0.33 decades of FP rate at deployment scale and more
on smaller samples. That is a measurement, and a measurement can be corrected.

The correction is a single positive multiplier on the tail's growth, learned
from subsample-to-truth pairs exactly as EXP-5's offsets are, but applied to a
curve that already has the right shape rather than replacing it:

    t(d) = t_anchor + lambda(features) * integral of the growth rate

Because ``lambda`` is strictly positive it cannot invert the curve — the
result is monotone for the same reason EXP-3b is — and because it multiplies a
finite integral rather than an exponent it cannot run away. That is the whole
point of correcting instead of learning from scratch: EXP-5 hit the benchmark
objective by predicting thresholds nothing fired on, and no positive
multiplier of a bounded rise can do that.

Leave-route-out comes from the caller, via the same ``full_pools`` contract
EXP-5 uses.
"""

from __future__ import annotations

import numpy as np

from .base import PooledContext, RouteMeta, empirical_threshold, floor_level, level_to_prob
from .exp3b_anchored_tail import ANCHOR_FP, AnchoredTailCurve
from .exp3_pooled_tail import build_hierarchy
from .gpd import choose_threshold

TRAIN_RUNGS: tuple[int, ...] = (800, 2_500, 25_000, 200_000)
TRAIN_DRAWS = 16
MAX_TRAIN_POOLS = 5
# The correction is bounded: it may rescale the tail's rise, not replace it.
LAMBDA_MIN, LAMBDA_MAX = 0.25, 4.0
FEATURES: tuple[str, ...] = ("log10_n", "xi", "rise1", "rise2", "curvature", "log10_anchor")

_MODEL_CACHE: dict[tuple[str, ...], object] = {}


def _features(curve: AnchoredTailCurve) -> list[float]:
    x = curve.benign
    n = x.size

    def top(k: int) -> float:
        return float(x[n - k]) if k <= n else float(x[0])

    rise1 = top(1) - top(10)
    rise2 = top(10) - top(100) if n >= 100 else rise1
    return [
        float(np.log10(n)), float(curve.fit.xi), rise1, rise2, rise1 - rise2,
        float(np.log10(max(curve.anchor_level, 1e-9))),
    ]


def _uncorrected(sample: np.ndarray, meta: RouteMeta, prior: tuple[float, float]) -> AnchoredTailCurve:
    return AnchoredTailCurve(
        meta, sample, choose_threshold(sample, xi_prior=prior), None, prior,
    )


def build_model(context: PooledContext, seed: int = 23):
    pools: dict[str, np.ndarray] = context.extras.get("full_pools", {})
    if not pools:
        return None
    pools = dict(sorted(pools.items(), key=lambda kv: -kv[1].size)[:MAX_TRAIN_POOLS])
    key = tuple(sorted(pools))
    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key]

    hierarchy = build_hierarchy(context)
    rng = np.random.default_rng(seed)
    rows: list[list[float]] = []
    targets: list[float] = []
    for benign in pools.values():
        pool = np.sort(np.asarray(benign, dtype=np.float64))
        n_pool = pool.size
        # Deepest level this pool can verify with 5 observed FP.
        truth_level = ANCHOR_FP * 1e8 / n_pool
        for m in TRAIN_RUNGS:
            if m * 4 > n_pool or floor_level(m) <= truth_level:
                continue
            t_true = float(empirical_threshold(pool, np.array([truth_level]))[0])
            for _ in range(TRAIN_DRAWS):
                sample = np.sort(pool[rng.choice(n_pool, size=m, replace=False)])
                meta = RouteMeta("train", "other", m, 0)
                curve = _uncorrected(sample, meta, (-0.15, 0.12))
                t_hat = float(curve._thresholds(np.array([truth_level]))[0])  # noqa: SLF001
                rise_hat = t_hat - curve.t_anchor
                rise_true = t_true - curve.t_anchor
                if rise_hat <= 1e-6 or rise_true <= 0:
                    continue
                rows.append(_features(curve))
                targets.append(float(np.clip(rise_true / rise_hat, LAMBDA_MIN, LAMBDA_MAX)))
    if len(rows) < 100:
        _MODEL_CACHE[key] = None
        return None
    from sklearn.ensemble import GradientBoostingRegressor  # noqa: PLC0415

    model = GradientBoostingRegressor(
        loss="absolute_error", n_estimators=200, learning_rate=0.05,
        max_depth=3, min_samples_leaf=20, subsample=0.9, random_state=seed,
    )
    model.fit(np.asarray(rows), np.asarray(targets))
    _MODEL_CACHE[key] = model
    del hierarchy
    return model


class CalibratedTailCurve(AnchoredTailCurve):
    method = "exp3c_calibrated_tail"

    def __init__(self, *args, correction: float = 1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.correction = float(np.clip(correction, LAMBDA_MIN, LAMBDA_MAX))

    def _tail(self, levels: np.ndarray, xi: float, sigma: float) -> np.ndarray:
        base = super()._tail(levels, xi, sigma)
        return self.t_anchor + self.correction * (base - self.t_anchor)

    def row_extras(self, level: float) -> dict[str, object]:
        extras = super().row_extras(level)
        extras["ladder_correction"] = self.correction
        return extras


def fit(
    logit_benign: np.ndarray,
    route_meta: RouteMeta,
    context: PooledContext | None = None,
) -> CalibratedTailCurve:
    ctx = context if context is not None else PooledContext()
    hierarchy = build_hierarchy(ctx)
    prior = hierarchy.prior_for(route_meta.filegroup)
    benign = np.sort(np.asarray(logit_benign, dtype=np.float64))
    tail_fit = choose_threshold(benign, xi_prior=prior)
    curve = CalibratedTailCurve(route_meta, benign, tail_fit, hierarchy, prior)
    model = build_model(ctx)
    if model is not None:
        curve.correction = float(np.clip(
            model.predict(np.asarray([_features(curve)]))[0], LAMBDA_MIN, LAMBDA_MAX,
        ))
    return curve


def prepare(context: PooledContext) -> None:
    build_hierarchy(context)
    build_model(context)
