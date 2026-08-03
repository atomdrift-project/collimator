#!/usr/bin/env python3
"""EXP-3 ``pooled-tail`` — hierarchical GPD with partial pooling.

Three levels in logit space, global -> filegroup -> route, on the GPD shape.
A route with 2,500 benigns cannot estimate its own tail shape (gem gets ~130
exceedances, and the shape's sampling error at that size is larger than the
range of shapes across the whole fleet), but its *family* can. Partial
pooling lets it inherit the family shape and move away from it only as far as
its own data insist — which is what replaces the incumbent's 25k cliff with
continuous shrinkage.

Pooling is on the SHAPE only. The scale is threshold-dependent
(``sigma(u2) = sigma(u1) + xi*(u2-u1)``), so pooling raw scales across routes
whose thresholds sit at different score levels would pool incomparable
numbers; the shape is threshold-invariant in the limit, which is exactly the
parameter small routes cannot estimate and families genuinely share.

Inference: empirical-Bayes hyperparameters (DerSimonian-Laird between-route
variance) plus a MAP route fit and a Laplace posterior, rather than the NUTS
/ SVI in the proposal. The posterior here is two-dimensional and smooth, the
weekly batch fits ~70 routes, and this keeps the repo free of a jax/numpyro
dependency. The API is unchanged, so a sampler can be swapped in behind it if
the Laplace bands ever fail metric 4.
"""

from __future__ import annotations

import numpy as np

from .base import PooledContext, RouteMeta, RouteTail
from .gpd import XI_PENALTY_SD, XI_PRIOR_MEAN, GPDFit, choose_threshold, fit_gpd
from .tailcurve import TailExtendedCurve

# Exceedance rate used to fit every context route, so their shapes are
# comparable. 1% keeps >= 50 exceedances for routes down to ~5,000 benigns
# and stays inside the 50k tail kept per route in the pooling context.
CONTEXT_ZETA = 0.01
CONTEXT_MIN_EXCEEDANCES = 40

# Floor on the family prior's sd. Zero between-route variance would say "this
# family's shape is known exactly", which no family of six routes has earned.
MIN_PRIOR_SD = 0.05
# Prior sd used when there is no usable context at all (degrades to EXP-2).
FALLBACK_PRIOR_SD = XI_PENALTY_SD

_HIERARCHY_CACHE: dict[tuple[str, ...], Hierarchy] = {}


class Hierarchy:
    """Empirical-Bayes global/family shape priors fitted from context routes."""

    def __init__(self, global_mean: float, global_sd: float,
                 family: dict[str, tuple[float, float]], n_routes: int):
        self.global_mean = global_mean
        self.global_sd = global_sd
        self.family = family
        self.n_routes = n_routes

    def prior_for(self, filegroup: str) -> tuple[float, float]:
        """(mean, sd) shape prior for a route in ``filegroup``."""
        if filegroup in self.family:
            mean, sd = self.family[filegroup]
            return mean, max(sd, MIN_PRIOR_SD)
        return self.global_mean, max(self.global_sd, MIN_PRIOR_SD)

    def as_dict(self) -> dict[str, object]:
        return {
            "global_mean": self.global_mean,
            "global_sd": self.global_sd,
            "n_context_routes": self.n_routes,
            "families": {k: list(v) for k, v in self.family.items()},
        }


def _fit_context_route(tail: RouteTail) -> tuple[float, float] | None:
    """Shape estimate and its standard error for one context route."""
    x = tail.tail_logits
    n_kept = x.size
    if n_kept < CONTEXT_MIN_EXCEEDANCES:
        return None
    # Target a CONTEXT_ZETA exceedance rate of the FULL route, falling back to
    # whatever the kept tail can supply for very large routes.
    k = int(round(CONTEXT_ZETA * tail.n_benign))
    k = min(max(k, CONTEXT_MIN_EXCEEDANCES), n_kept - 1)
    u = float(x[n_kept - k - 1])
    y = x[x > u] - u
    if y.size < CONTEXT_MIN_EXCEEDANCES:
        return None
    fit = fit_gpd(y, u=u, zeta=y.size / tail.n_benign, n=tail.n_benign)
    se = float(np.sqrt(fit.cov[0, 0])) if np.all(np.isfinite(fit.cov)) else np.nan
    if not np.isfinite(se) or se <= 0:
        se = 1.0 / np.sqrt(max(y.size, 1))  # crude but never zero
    return float(fit.xi), float(se)


def _dersimonian_laird(values: np.ndarray, ses: np.ndarray) -> tuple[float, float]:
    """Random-effects mean and between-unit sd (method of moments).

    The between-unit variance is the number that matters: it is how much a
    route is allowed to differ from its family, and estimating it from the
    data is what keeps shrinkage honest rather than a tuning knob.
    """
    if values.size == 0:
        return XI_PRIOR_MEAN, FALLBACK_PRIOR_SD
    if values.size == 1:
        return float(values[0]), FALLBACK_PRIOR_SD
    w = 1.0 / np.maximum(ses ** 2, 1e-8)
    mean_fixed = float(np.sum(w * values) / np.sum(w))
    q = float(np.sum(w * (values - mean_fixed) ** 2))
    df = values.size - 1
    c = float(np.sum(w) - np.sum(w ** 2) / np.sum(w))
    tau2 = max(0.0, (q - df) / c) if c > 0 else 0.0
    w_re = 1.0 / (np.maximum(ses ** 2, 1e-8) + tau2)
    mean_re = float(np.sum(w_re * values) / np.sum(w_re))
    return mean_re, float(np.sqrt(tau2))


def build_hierarchy(context: PooledContext) -> Hierarchy:
    """Fit the global and per-family shape priors from the context routes."""
    key = tuple(sorted(t.route for t in context.tails))
    cached = _HIERARCHY_CACHE.get(key)
    if cached is not None:
        return cached

    per_route: list[tuple[str, float, float]] = []
    for tail in context.tails:
        est = _fit_context_route(tail)
        if est is not None:
            per_route.append((tail.filegroup, est[0], est[1]))

    if not per_route:
        hierarchy = Hierarchy(XI_PRIOR_MEAN, FALLBACK_PRIOR_SD, {}, 0)
        _HIERARCHY_CACHE[key] = hierarchy
        return hierarchy

    xis = np.array([r[1] for r in per_route])
    ses = np.array([r[2] for r in per_route])
    global_mean, global_sd = _dersimonian_laird(xis, ses)

    families: dict[str, tuple[float, float]] = {}
    for fg in {r[0] for r in per_route}:
        members = [(r[1], r[2]) for r in per_route if r[0] == fg]
        fam_xi = np.array([m[0] for m in members])
        fam_se = np.array([m[1] for m in members])
        fam_mean, fam_sd = _dersimonian_laird(fam_xi, fam_se)
        # A family of one or two routes has not earned its own mean; shrink it
        # toward the global one by its own precision (the third hierarchy
        # level, done in closed form).
        n_f = len(members)
        prior_var = max(global_sd, MIN_PRIOR_SD) ** 2
        fam_var = max(fam_sd, MIN_PRIOR_SD) ** 2 / n_f
        weight = prior_var / (prior_var + fam_var)
        mean = weight * fam_mean + (1.0 - weight) * global_mean
        sd = np.sqrt(max(fam_sd, MIN_PRIOR_SD) ** 2 + (1.0 - weight) * prior_var)
        families[fg] = (float(mean), float(sd))

    hierarchy = Hierarchy(global_mean, max(global_sd, MIN_PRIOR_SD), families, len(per_route))
    _HIERARCHY_CACHE[key] = hierarchy
    return hierarchy


class PooledTailCurve(TailExtendedCurve):
    method = "exp3_pooled_tail"

    def __init__(self, meta: RouteMeta, benign_logit: np.ndarray, fit: GPDFit,
                 hierarchy: Hierarchy, prior: tuple[float, float]):
        super().__init__(meta, benign_logit, fit, method="exp3_pooled_tail")
        self.hierarchy = hierarchy
        self.prior = prior

    def row_extras(self, level: float) -> dict[str, object]:
        extras = super().row_extras(level)
        extras.update({
            "prior_mean": self.prior[0],
            "prior_sd": self.prior[1],
            "n_context_routes": self.hierarchy.n_routes,
            # How far the fitted shape moved from the family prior, in prior
            # sds: the shrinkage diagnostic the proposal asks for (a route
            # whose tail genuinely differs from its family shows up here).
            "shrinkage_z": (self.fit.xi - self.prior[0]) / max(self.prior[1], 1e-9),
        })
        return extras


def fit(
    logit_benign: np.ndarray,
    route_meta: RouteMeta,
    context: PooledContext | None = None,
) -> PooledTailCurve:
    ctx = context if context is not None else PooledContext()
    hierarchy = build_hierarchy(ctx)
    prior = hierarchy.prior_for(route_meta.filegroup)
    benign = np.sort(np.asarray(logit_benign, dtype=np.float64))
    tail_fit = choose_threshold(benign, xi_prior=prior)
    return PooledTailCurve(route_meta, benign, tail_fit, hierarchy, prior)


def prepare(context: PooledContext) -> None:
    """Fit the hierarchy once in the parent, pre-fork (see EXP-5's note)."""
    build_hierarchy(context)
