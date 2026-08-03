#!/usr/bin/env python3
"""EXP-4 ``boosted-tail`` — covariate-conditional GPD (gbex-style).

Direct descendant of gbex (Velthoen-Cai-Engelke-Zhou, *Extremes* 2023):
gradient boosting where the trees predict the GPD parameters themselves.
Every exceedance in the fleet contributes to the loss, and the trees split on
route-level covariates, so the pooling structure is *learned* from what makes
tails similar rather than imposed by the filegroup topology EXP-3 assumes.

Two details matter for this corpus:

* the scale is predicted in normalised form, ``log(sigma / decade_rise)``,
  where ``decade_rise`` is the route's own measured logit rise per decade of
  FP rate. Raw scales are not comparable across routes (they range 1.5 to 16
  logits here), and a tree that splits on an incomparable target learns the
  route's score scale instead of its tail shape;
* the shape is clipped to the fleet's bounds after every boosting step —
  unbounded shape updates are precisely how a boosted EVT model reproduces
  the failure that got the 2026-06-06 GPD attempt deleted.
"""

from __future__ import annotations

import numpy as np

from .base import PooledContext, RouteMeta, RouteTail
from .gpd import XI_MAX, XI_MIN, XI_PRIOR_MEAN, GPDFit, choose_threshold, fit_gpd
from .tailcurve import TailExtendedCurve, observed_decade_rise

# Exceedance rate at which every training route is fitted, so the boosted
# parameters describe the same part of each tail.
TRAIN_ZETA = 0.01
MIN_TRAIN_EXCEEDANCES = 40
# Exceedances kept per route: the loss is a sum over observations, so without
# a cap the three largest routes would carry ~60% of the gradient.
MAX_OBS_PER_ROUTE = 1_000

LOG_SIGMA_MIN, LOG_SIGMA_MAX = -8.0, 8.0

N_ROUNDS = 150
LEARNING_RATE = 0.05
TREE_DEPTH = 3

_MODEL_CACHE: dict[tuple[str, ...], BoostedTailModel | None] = {}

COVARIATES: tuple[str, ...] = (
    "log10_n", "rise1", "rise2", "curvature", "q99_minus_q90",
    "tail_mean", "tail_sd", "tail_skew",
)


def _route_covariates(tail_logits: np.ndarray, n_benign: int) -> np.ndarray:
    """Covariates for one route, computable from a sample of any size."""
    x = np.asarray(tail_logits, dtype=np.float64)
    n = x.size

    def top(k: int) -> float:
        return float(x[n - k]) if k <= n else float(x[0])

    rise1 = top(1) - top(10)
    rise2 = top(10) - top(100) if n >= 100 else rise1
    q90, q99 = float(np.quantile(x, 0.90)), float(np.quantile(x, 0.99))
    upper = x[max(n - MAX_OBS_PER_ROUTE, 0):]
    mean, sd = float(np.mean(upper)), float(np.std(upper) + 1e-9)
    skew = float(np.mean(((upper - mean) / sd) ** 3))
    return np.array([
        np.log10(max(n_benign, 1)), rise1, rise2, rise1 - rise2, q99 - q90,
        mean, sd, skew,
    ])


def _gpd_gradients(y: np.ndarray, xi: np.ndarray, log_sigma: np.ndarray,
                   ) -> tuple[np.ndarray, np.ndarray]:
    """d(NLL)/d(xi) and d(NLL)/d(log sigma) per observation."""
    sigma = np.exp(log_sigma)
    ratio = y / sigma
    xi_safe = np.where(np.abs(xi) < 1e-6, 1e-6, xi)
    z = np.maximum(1.0 + xi_safe * ratio, 1e-9)
    d_xi = -np.log(z) / xi_safe**2 + (1.0 + 1.0 / xi_safe) * ratio / z
    d_ls = 1.0 - (1.0 + xi_safe) * ratio / z
    return d_xi, d_ls


class BoostedTailModel:
    """Boosted (xi, log sigma/decade_rise) predictor over route covariates."""

    def __init__(self, xi0: float, ls0: float, trees: list, routes: tuple[str, ...]):
        self.xi0 = xi0
        self.ls0 = ls0
        self.trees = trees  # list of (tree_xi, tree_ls)
        self.routes = routes

    def predict(self, covariates: np.ndarray) -> tuple[float, float]:
        row = covariates.reshape(1, -1)
        xi, ls = self.xi0, self.ls0
        for tree_xi, tree_ls in self.trees:
            xi += LEARNING_RATE * float(tree_xi.predict(row)[0])
            ls += LEARNING_RATE * float(tree_ls.predict(row)[0])
            xi = float(np.clip(xi, XI_MIN, XI_MAX))
            ls = float(np.clip(ls, LOG_SIGMA_MIN, LOG_SIGMA_MAX))
        return xi, ls


def _training_set(tails: tuple[RouteTail, ...]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(covariates per observation, exceedance, normalising scale)."""
    cov_rows: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    scales: list[np.ndarray] = []
    for tail in tails:
        x = tail.tail_logits
        n_kept = x.size
        if n_kept < MIN_TRAIN_EXCEEDANCES:
            continue
        k = int(round(TRAIN_ZETA * tail.n_benign))
        k = min(max(k, MIN_TRAIN_EXCEEDANCES), n_kept - 1)
        u = float(x[n_kept - k - 1])
        y = x[x > u] - u
        if y.size < MIN_TRAIN_EXCEEDANCES:
            continue
        scale = observed_decade_rise(x)
        if not np.isfinite(scale) or scale <= 1e-6:
            continue  # a route whose tail is one atom teaches nothing here
        if y.size > MAX_OBS_PER_ROUTE:
            step = y.size / MAX_OBS_PER_ROUTE
            y = y[(np.arange(MAX_OBS_PER_ROUTE) * step).astype(int)]
        cov = _route_covariates(x, tail.n_benign)
        cov_rows.append(np.tile(cov, (y.size, 1)))
        ys.append(y)
        scales.append(np.full(y.size, scale))
    if not ys:
        return np.empty((0, len(COVARIATES))), np.empty(0), np.empty(0)
    return np.vstack(cov_rows), np.concatenate(ys), np.concatenate(scales)


def build_model(context: PooledContext) -> BoostedTailModel | None:
    """Boost the conditional GPD over the context routes (cached per context)."""
    key = tuple(sorted(t.route for t in context.tails))
    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key]
    cov, y, scale = _training_set(context.tails)
    if y.size < 500:
        _MODEL_CACHE[key] = None
        return None
    from sklearn.tree import DecisionTreeRegressor  # noqa: PLC0415

    # Work in units of each route's decade rise so the scale target is
    # comparable; convert back at prediction time.
    y_norm = y / scale
    xi = np.full(y.size, XI_PRIOR_MEAN)
    ls = np.full(y.size, float(np.log(np.mean(y_norm))))
    xi0, ls0 = float(xi[0]), float(ls[0])
    trees = []
    for _ in range(N_ROUNDS):
        d_xi, d_ls = _gpd_gradients(y_norm, xi, ls)
        tree_xi = DecisionTreeRegressor(max_depth=TREE_DEPTH, min_samples_leaf=200)
        tree_ls = DecisionTreeRegressor(max_depth=TREE_DEPTH, min_samples_leaf=200)
        tree_xi.fit(cov, -d_xi)
        tree_ls.fit(cov, -d_ls)
        xi = np.clip(xi + LEARNING_RATE * tree_xi.predict(cov), XI_MIN, XI_MAX)
        # Exceedances are in units of the route's decade rise, so log sigma
        # lives near 0; the bound only catches a diverging step, which would
        # otherwise overflow exp() and poison every later round's gradient.
        ls = np.clip(ls + LEARNING_RATE * tree_ls.predict(cov), LOG_SIGMA_MIN, LOG_SIGMA_MAX)
        trees.append((tree_xi, tree_ls))
    model = BoostedTailModel(xi0, ls0, trees, key)
    _MODEL_CACHE[key] = model
    return model


class BoostedTailCurve(TailExtendedCurve):
    method = "exp4_boosted_tail"

    def __init__(self, meta: RouteMeta, benign_logit: np.ndarray, fit: GPDFit,
                 predicted: tuple[float, float] | None):
        super().__init__(meta, benign_logit, fit, method="exp4_boosted_tail")
        self.predicted = predicted

    def row_extras(self, level: float) -> dict[str, object]:
        extras = super().row_extras(level)
        extras["boosted"] = self.predicted is not None
        return extras


def fit(
    logit_benign: np.ndarray,
    route_meta: RouteMeta,
    context: PooledContext | None = None,
) -> BoostedTailCurve:
    benign = np.sort(np.asarray(logit_benign, dtype=np.float64))
    model = build_model(context) if context is not None else None
    base = choose_threshold(benign)
    if model is None:
        return BoostedTailCurve(route_meta, benign, base, None)

    cov = _route_covariates(benign, benign.size)
    xi_hat, ls_hat = model.predict(cov)
    scale = observed_decade_rise(benign)
    sigma_hat = float(np.exp(ls_hat) * max(scale, 1e-6))
    # Keep the exceedance threshold and rate the goodness-of-fit scan picked;
    # only the parameters come from the boosted model. Refit the covariance at
    # those parameters so the credible band still reflects this route's own
    # exceedance count.
    y = benign[benign > base.u] - base.u
    local = fit_gpd(y, u=base.u, zeta=base.zeta, n=benign.size,
                    xi_prior=(xi_hat, 0.05),
                    log_sigma_prior=(float(np.log(max(sigma_hat, 1e-9))), 0.25))
    return BoostedTailCurve(route_meta, benign, local, (xi_hat, sigma_hat))


def prepare(context: PooledContext) -> None:
    """Boost once in the parent, pre-fork (see EXP-5's note)."""
    build_model(context)
