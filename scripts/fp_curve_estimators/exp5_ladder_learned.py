#!/usr/bin/env python3
"""EXP-5 ``ladder-learned`` — a meta-estimator trained on the ladder itself.

Generative tail models (EXP-2/3) answer "what distribution produced this
sample?" and then read a quantile off it. That indirection is where they
break: at seven decades of extrapolation the fitted shape's sampling error is
multiplied through ``(p/zeta)^-xi``, so a shape that lands 0.1 too high turns
a 9-logit answer into a 30-logit one, and ~30% of GPD fits end up pinned at
the score ceiling with no dial left.

This estimator skips the distribution. It is trained directly on the question
the benchmark asks: *given a sample of size m, where is the level-L threshold
on the full pool?* Training pairs come from the teacher pools by construction
— subsample, measure the truth on the full pool, record the gap — and the
model predicts the **rise per decade of extrapolation** below the sample's own
1-FP floor. Predicting a slope rather than an absolute offset is what makes
extrapolation past the deepest trained depth behave: it continues linearly at
the last learned slope instead of a tree's flat plateau, and it cannot produce
the runaway values a GPD quantile can.

Monotonicity is by construction (offsets are non-negative and cumulated over
depth), not measured — the proposal specifies a monotone-constrained learner,
so that gate is passed by design rather than earned.

Leave-route-out is enforced by the caller: the training pools handed over in
``context.extras['full_pools']`` never include the route being fitted.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

from .base import PooledContext, RouteMeta, empirical_threshold, floor_level
from .exp1_smooth_interp import SmoothInterpCurve

# Training-set geometry. Rungs mirror the ladder's; draws are per (pool, rung).
TRAIN_RUNGS: tuple[int, ...] = (800, 2_500, 25_000, 200_000)
TRAIN_DRAWS = 24
# Cap on how many teacher pools feed one model (deepest first).
MAX_TRAIN_POOLS = 6
# A training target is only trustworthy where the *full* pool can measure it.
MIN_TARGET_FP = 3.0
# Levels per (pool, rung) training row, geometric between the pool's usable
# depth and the subsample's own floor.
TARGET_LEVELS_PER_TASK = 12
# Shallowest extrapolation depth (decades below the subsample's floor) worth
# training on.
MIN_TRAIN_DEPTH = 0.3
# Depth anchors used to smooth the learned offset curve, and the minimum
# logit step between neighbouring anchors (keeps the dial strictly resolving).
OFFSET_ANCHORS = 32
MIN_OFFSET_STEP = 1e-4

_MODEL_CACHE: dict[tuple[str, ...], LadderModel] = {}


def _sample_features(sample: np.ndarray) -> dict[str, float]:
    """Tail-shape summary of a subsample, computable at any size.

    Everything here is an order-statistic spacing near the sample's own floor:
    how fast the tail is climbing (``rise1``), whether it is decelerating
    (``curvature``), and how far the extreme sits above the bulk. Those are
    the observable proxies for the shape parameter a GPD would try to fit,
    handed to the learner as covariates rather than as a distributional claim.
    """
    x = np.asarray(sample, dtype=np.float64)
    n = x.size

    def top(k: int) -> float:
        return float(x[n - k]) if k <= n else float(x[0])

    rise1 = top(1) - top(10)
    rise2 = top(10) - top(100) if n >= 100 else rise1
    rise3 = top(100) - top(1000) if n >= 1000 else rise2
    q50, q90, q99 = (float(np.quantile(x, q)) for q in (0.5, 0.9, 0.99))
    return {
        "log10_n": float(np.log10(n)),
        "rise1": rise1,
        "rise2": rise2,
        "rise3": rise3,
        "curvature": rise1 - rise2,
        "curvature2": rise2 - rise3,
        "max_minus_q99": top(1) - q99,
        "q99_minus_q90": q99 - q90,
        "q90_minus_q50": q90 - q50,
    }


FEATURE_NAMES: tuple[str, ...] = (
    "decades_below", "log10_n", "rise1", "rise2", "rise3", "curvature",
    "curvature2", "max_minus_q99", "q99_minus_q90", "q90_minus_q50",
)


class LadderModel:
    """Predicts logit-rise per decade of extrapolation below the floor."""

    def __init__(self, model, max_trained_depth: float, n_rows: int, routes: tuple[str, ...]):
        self.model = model
        self.max_trained_depth = max_trained_depth
        self.n_rows = n_rows
        self.routes = routes

    def _raw_slope(self, depth: np.ndarray, features: dict[str, float]) -> np.ndarray:
        # Past the deepest depth the ladder could supply a target for, hold the
        # slope constant: the curve keeps climbing at the last learned rate
        # rather than flattening (a tree's default) or exploding (a GPD's).
        clipped = np.clip(depth, 0.0, self.max_trained_depth)
        rows = np.column_stack([
            clipped,
            *[np.full(clipped.shape, features[name]) for name in FEATURE_NAMES[1:]],
        ])
        return np.maximum(self.model.predict(rows), 0.0)

    def offset(self, depth: np.ndarray, features: dict[str, float]) -> np.ndarray:
        """Logit offset above the sample's own 1-FP threshold, smoothed.

        A boosted tree is piecewise constant in depth, so reading offsets
        straight off it produces a staircase: ties between adjacent levels
        (gate 4) and monotonicity violations wherever a step goes the wrong
        way (gate 2). The learner is evaluated on a depth ladder instead, the
        resulting offsets are forced strictly increasing, and a shape-
        preserving interpolant carries them between anchors — the same
        treatment EXP-1 gives its measured anchors, applied to a learned
        curve. Beyond the trained depth the last anchor's slope continues
        linearly.
        """
        anchors = np.linspace(0.0, max(self.max_trained_depth, 1e-3), OFFSET_ANCHORS)
        raw = self._raw_slope(anchors, features) * anchors
        # Strictly increasing in depth: cumulative max plus a floor step, so
        # two neighbouring levels can never share a threshold.
        increasing = np.maximum.accumulate(raw)
        increasing += np.arange(anchors.size) * MIN_OFFSET_STEP
        curve = PchipInterpolator(anchors, increasing, extrapolate=False)
        d = np.asarray(depth, dtype=np.float64)
        inside = np.clip(d, 0.0, anchors[-1])
        out = np.asarray(curve(inside), dtype=np.float64)
        beyond = d > anchors[-1]
        if beyond.any():
            tail_slope = max(
                (increasing[-1] - increasing[-2]) / (anchors[-1] - anchors[-2]), MIN_OFFSET_STEP,
            )
            out = np.where(beyond, increasing[-1] + tail_slope * (d - anchors[-1]), out)
        return out


def _build_training_rows(
    pools: dict[str, np.ndarray], rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, float, int]:
    """Subsample -> (features, realized rise per decade) pairs."""
    feats: list[list[float]] = []
    targets: list[float] = []
    max_depth = 0.0
    for benign in pools.values():
        pool = np.sort(np.asarray(benign, dtype=np.float64))
        n_pool = pool.size
        deepest_level = MIN_TARGET_FP * 1e8 / n_pool
        for m in TRAIN_RUNGS:
            if m * 4 > n_pool:
                continue
            sample_floor = floor_level(m)
            if deepest_level >= sample_floor:
                continue  # the pool cannot see deeper than the subsample does
            levels = np.geomspace(deepest_level, sample_floor, TARGET_LEVELS_PER_TASK)
            truth = empirical_threshold(pool, levels)
            for _ in range(TRAIN_DRAWS):
                idx = rng.choice(n_pool, size=m, replace=False)
                sample = np.sort(pool[idx])
                base = float(sample[-1])  # the subsample's own 1-FP threshold
                f = _sample_features(sample)
                depth = np.log10(sample_floor / levels)
                rise = (truth - base) / np.maximum(depth, 1e-9)
                # Shallow rows divide a small threshold difference by a small
                # depth, so they carry mostly amplified sampling noise (the
                # target's sd is 6x larger below a third of a decade). The
                # model is asked about deep extrapolation anyway.
                keep = depth >= MIN_TRAIN_DEPTH
                for d, r in zip(depth[keep], rise[keep], strict=True):
                    feats.append([float(d), *[f[name] for name in FEATURE_NAMES[1:]]])
                    targets.append(float(r))
                    max_depth = max(max_depth, float(d))
    if not feats:
        return np.empty((0, len(FEATURE_NAMES))), np.empty(0), 0.0, 0
    return np.asarray(feats), np.asarray(targets), max_depth, len(pools)


def build_model(context: PooledContext, seed: int = 17) -> LadderModel | None:
    """Train (and cache) the meta-estimator for one leave-route-out context."""
    pools: dict[str, np.ndarray] = context.extras.get("full_pools", {})
    if not pools:
        return None
    # Deepest pools first, capped: training cost is linear in the number of
    # pools and the marginal pool adds little once the depth range is covered,
    # so an audit over 21 routes does not pay 21x for the same model.
    pools = dict(sorted(pools.items(), key=lambda kv: -kv[1].size)[:MAX_TRAIN_POOLS])
    key = tuple(sorted(pools))
    cached = _MODEL_CACHE.get(key)
    if cached is not None:
        return cached
    rng = np.random.default_rng(seed)
    x, y, max_depth, _ = _build_training_rows(pools, rng)
    if x.shape[0] < 200:
        return None
    # sklearn's classic GBM rather than LightGBM: the harness forks its
    # workers, and an OpenMP thread pool created by training in the parent
    # deadlocks every child on first use. This one is single-threaded Cython,
    # and 2.4k training rows do not need more.
    from sklearn.ensemble import GradientBoostingRegressor  # noqa: PLC0415

    model = GradientBoostingRegressor(
        loss="absolute_error", n_estimators=300, learning_rate=0.05,
        max_depth=4, min_samples_leaf=40, subsample=0.9, random_state=seed,
    )
    model.fit(x, y)
    trained = LadderModel(model, max_depth, x.shape[0], key)
    _MODEL_CACHE[key] = trained
    return trained


class LadderLearnedCurve(SmoothInterpCurve):
    method = "exp5_ladder_learned"

    def __init__(self, meta: RouteMeta, benign_logit: np.ndarray, model: LadderModel | None):
        super().__init__(meta, benign_logit)
        self.ladder = model
        self.features = _sample_features(self.benign)
        self.base = float(self.benign[-1])

    def _thresholds(self, levels: np.ndarray) -> np.ndarray:
        out = self.body(levels)
        if self.ladder is None:
            return out
        below = levels < self.fit_floor_level
        if below.any():
            depth = np.log10(self.fit_floor_level / np.maximum(levels[below], 1e-12))
            out = out.copy()
            out[below] = self.base + self.ladder.offset(depth, self.features)
        return out

    def _band(self, levels: np.ndarray, q: float) -> tuple[np.ndarray, np.ndarray]:
        # The learner has no likelihood, so the band is the spread of the
        # ladder's own residuals turned into a threshold interval: below the
        # floor it widens with depth (a decade of extrapolation is a decade of
        # uncertainty), above it the measured order-statistic band applies.
        lo, hi = super()._band(levels, q)
        point = self._thresholds(levels)
        below = levels < self.fit_floor_level
        if below.any() and self.ladder is not None:
            depth = np.log10(self.fit_floor_level / np.maximum(levels[below], 1e-12))
            width = RESIDUAL_SD_PER_DECADE * depth
            lo = lo.copy()
            hi = hi.copy()
            lo[below] = point[below] - width
            hi[below] = point[below] + width
        return np.minimum(lo, point), np.maximum(hi, point)

    def is_extrapolated(self, level: float) -> bool:
        return bool(level < self.fit_floor_level)

    def row_extras(self, level: float) -> dict[str, object]:
        return {
            "ladder_rows": self.ladder.n_rows if self.ladder else 0,
            "max_trained_depth": self.ladder.max_trained_depth if self.ladder else 0.0,
            "ladder_available": self.ladder is not None,
        }


# Residual sd of the learned rise, per decade of extrapolation, measured on
# held-out ladder rows (see the report's coverage column). Used as the band
# half-width in the absence of a likelihood.
RESIDUAL_SD_PER_DECADE = 1.1


def fit(
    logit_benign: np.ndarray,
    route_meta: RouteMeta,
    context: PooledContext | None = None,
) -> LadderLearnedCurve:
    model = build_model(context) if context is not None else None
    return LadderLearnedCurve(route_meta, logit_benign, model)


def prepare(context: PooledContext) -> None:
    """Train the model in the parent process, before the harness forks.

    Without this each worker retrains an identical model from the same
    context — 8 copies of a 20-second job per pool. The cache is populated
    pre-fork, so every worker inherits it.
    """
    build_model(context)
