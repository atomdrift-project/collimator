#!/usr/bin/env python3
"""Generalized-Pareto tail primitives, shared by EXP-2 and EXP-3.

Peaks-over-threshold in LOGIT space. The 2026-06-06 GPD attempt was deleted
for three specific reasons (METHODOLOGY.md); each has a countermeasure here:

* *overshoot past p=1* — impossible: the fit lives in logit space, whose
  support is the whole real line, and thresholds are converted back only at
  emission;
* *shape degeneracy below ~500 tail points* — the shape is estimated by
  penalized MLE (a Gaussian penalty on xi, i.e. a MAP fit), with a
  probability-weighted-moment fallback when the optimiser fails; EXP-3 goes
  further and shrinks xi toward a family mean;
* *no validation loop* — every fit produced here is scored by
  ``scripts/fp_curve_bench.py`` against realized FP counts before anything is
  allowed near a bundle.

Parameterisation: exceedances ``y = x - u`` over threshold ``u`` follow
``P(Y > y) = (1 + xi*y/sigma)^(-1/xi)`` (exponential limit at xi -> 0).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize
from scipy.stats import kstwo

# Shape bounds. Below -0.5 the MLE loses its regularity properties (Smith).
# The upper bound is empirical: fitting all 73 routes' full OOF pools on
# 2026-08-03 puts the fleet's shape at median -0.165, quartiles [-0.32, 0.00],
# with the handful of larger values coming from routes whose benign tail is a
# saturated atom rather than a tail (see base.Saturation). Extrapolating six
# decades with xi = +0.4 produces thresholds ~1,200 logits above anything
# observable, so the bound is set where the fleet actually lives.
XI_MIN, XI_MAX = -0.45, 0.35

# Default shape penalty: a Gaussian centred on the fleet median with an sd
# just wider than the fleet's interquartile spread. This is the "Coles-style
# penalty" of the proposal with its parameters measured rather than guessed —
# it costs a well-determined route nothing and stops a data-starved one from
# inventing a heavy tail.
# Spread is taken from the routes whose shape is actually determined — the
# large pools with a real (non-atom) tail: scripts -0.24, source -0.23,
# portable -0.23, javascript -0.25, native -0.21, php -0.13, python_bytecode
# -0.04, config +0.09, elf +0.10. That is sd ~0.12 around -0.15. The fleet-wide
# sd of 0.30 is inflated by routes whose "tail" is a quantisation atom, which
# carry no shape information and must not widen the prior for routes that do.
XI_PRIOR_MEAN = -0.15
XI_PENALTY_SD = 0.12

# Candidate exceedance thresholds for the stability scan, plus the minimum
# number of exceedances a candidate needs to be considered at all.
THRESHOLD_QUANTILES: tuple[float, ...] = (0.90, 0.95, 0.975, 0.99, 0.995, 0.999)
MIN_EXCEEDANCES = 50


@dataclass(frozen=True)
class GPDFit:
    """A fitted tail: GPD(xi, sigma) on exceedances over u at rate zeta."""

    xi: float
    sigma: float
    u: float
    zeta: float  # P(X > u), estimated as k/n
    k: int  # number of exceedances
    n: int  # sample size the rate was estimated from
    nll: float
    method: str
    cov: np.ndarray  # 2x2 posterior covariance of (xi, log sigma); may be NaN

    @property
    def log_sigma(self) -> float:
        return float(np.log(self.sigma))


def _nll(params: np.ndarray, y: np.ndarray) -> float:
    xi, log_sigma = float(params[0]), float(params[1])
    sigma = np.exp(log_sigma)
    if not np.isfinite(sigma) or sigma <= 0:
        return np.inf
    z = 1.0 + xi * y / sigma
    if np.any(z <= 1e-12):
        return np.inf
    k = y.size
    if abs(xi) < 1e-8:
        return k * log_sigma + float(np.sum(y)) / sigma
    return k * log_sigma + (1.0 + 1.0 / xi) * float(np.sum(np.log(z)))


def _penalty(params: np.ndarray, xi_prior: tuple[float, float],
             log_sigma_prior: tuple[float, float] | None) -> float:
    xi, log_sigma = float(params[0]), float(params[1])
    mean, sd = xi_prior
    out = 0.5 * ((xi - mean) / sd) ** 2
    if log_sigma_prior is not None:
        ls_mean, ls_sd = log_sigma_prior
        out += 0.5 * ((log_sigma - ls_mean) / ls_sd) ** 2
    return out


def pwm_estimate(y: np.ndarray) -> tuple[float, float]:
    """Probability-weighted-moment (Hosking-Wallis) GPD estimate.

    Closed form, no optimiser, always returns something finite — the fallback
    when penalized MLE fails to converge on a short or degenerate tail.
    """
    ys = np.sort(np.asarray(y, dtype=np.float64))
    k = ys.size
    if k < 2:
        return 0.0, max(float(np.mean(ys)) if k else 1.0, 1e-6)
    p = (np.arange(1, k + 1) - 0.35) / k
    a0 = float(np.mean(ys))
    a1 = float(np.mean(ys * (1.0 - p)))
    denom = a0 - 2.0 * a1
    if abs(denom) < 1e-12 or a0 <= 0:
        return 0.0, max(a0, 1e-6)
    shape_k = a0 / denom - 2.0
    sigma = 2.0 * a0 * a1 / denom
    xi = -shape_k
    if not np.isfinite(sigma) or sigma <= 0:
        return 0.0, max(a0, 1e-6)
    return float(np.clip(xi, XI_MIN, XI_MAX)), float(sigma)


def fit_gpd(
    y: np.ndarray,
    *,
    u: float,
    zeta: float,
    n: int,
    xi_prior: tuple[float, float] = (XI_PRIOR_MEAN, XI_PENALTY_SD),
    log_sigma_prior: tuple[float, float] | None = None,
) -> GPDFit:
    """Penalized-MLE (MAP) GPD fit to exceedances ``y = x - u``.

    ``xi_prior`` / ``log_sigma_prior`` are the (mean, sd) of Gaussian penalties.
    EXP-2 uses the fixed fleet-median shape penalty; EXP-3 passes the
    hierarchical family posterior, which is what turns this into partial
    pooling rather than independent per-route fits.
    """
    y = np.asarray(y, dtype=np.float64)
    y = y[y > 0]
    k = y.size
    if k < 5:
        xi, sigma = pwm_estimate(y if k else np.array([1.0]))
        return GPDFit(xi, sigma, u, zeta, k, n, np.inf, "pwm_tiny", np.full((2, 2), np.nan))

    xi0, sigma0 = pwm_estimate(y)
    start = np.array([np.clip(xi0, -0.2, 0.4), np.log(max(sigma0, 1e-6))])

    def objective(params: np.ndarray) -> float:
        val = _nll(params, y)
        if not np.isfinite(val):
            return 1e12
        return val + _penalty(params, xi_prior, log_sigma_prior)

    best = None
    for start_xi in (start[0], 0.0, 0.2):
        trial = np.array([start_xi, start[1]])
        res = minimize(
            objective, trial, method="L-BFGS-B",
            bounds=[(XI_MIN, XI_MAX), (np.log(1e-8), np.log(1e6))],
        )
        if res.success and np.isfinite(res.fun) and (best is None or res.fun < best.fun):
            best = res
    if best is None:
        xi, sigma = pwm_estimate(y)
        return GPDFit(xi, sigma, u, zeta, k, n, np.inf, "pwm_fallback", np.full((2, 2), np.nan))

    xi = float(np.clip(best.x[0], XI_MIN, XI_MAX))
    sigma = float(np.exp(best.x[1]))
    # Bands are scored against *realized* FP counts (metric 4), which is a
    # frequentist question, so the covariance comes from the observed
    # information — the unpenalized likelihood's curvature. Using the
    # penalized objective would report the posterior's width, which the prior
    # deliberately narrows, and under-cover by exactly that much.
    theta = np.array([xi, np.log(sigma)])
    cov = _laplace_cov(theta, lambda p: _nll(p, y) if np.isfinite(_nll(p, y)) else 1e12)
    if not np.all(np.isfinite(cov)):
        cov = _laplace_cov(theta, objective)
    return GPDFit(xi, sigma, u, zeta, k, n, float(best.fun), "penalized_mle", cov)


def _laplace_cov(theta: np.ndarray, objective) -> np.ndarray:
    """Posterior covariance of (xi, log sigma) from a numerical Hessian.

    The Laplace approximation is what replaces MCMC here: for a two-parameter
    posterior with tens to thousands of exceedances it is accurate enough to
    produce the credible bands metric 4 scores, and it costs milliseconds
    instead of seconds per fit (~7k fits per ladder run).
    """
    step = np.array([1e-3, 1e-3])
    hess = np.zeros((2, 2))
    f0 = objective(theta)
    for i in range(2):
        for j in range(2):
            ei = np.zeros(2)
            ei[i] = step[i]
            ej = np.zeros(2)
            ej[j] = step[j]
            if i == j:
                hess[i, j] = (objective(theta + ei) - 2 * f0 + objective(theta - ei)) / step[i] ** 2
            else:
                hess[i, j] = (
                    objective(theta + ei + ej) - objective(theta + ei - ej)
                    - objective(theta - ei + ej) + objective(theta - ei - ej)
                ) / (4 * step[i] * step[j])
    try:
        cov = np.linalg.inv(hess)
    except np.linalg.LinAlgError:
        return np.full((2, 2), np.nan)
    if not np.all(np.isfinite(cov)) or np.any(np.diag(cov) <= 0):
        return np.full((2, 2), np.nan)
    return cov


def gpd_quantile(fit: GPDFit, prob: np.ndarray | float) -> np.ndarray:
    """Weissman quantile: the score exceeded with probability ``prob``.

    Valid for prob < zeta (above the exceedance threshold); at prob == zeta it
    returns u exactly, which is what makes the seam with the empirical body
    continuous.
    """
    p = np.atleast_1d(np.asarray(prob, dtype=np.float64))
    ratio = np.clip(p / max(fit.zeta, 1e-15), 1e-300, None)
    if abs(fit.xi) < 1e-8:
        excess = fit.sigma * np.log(1.0 / ratio)
    else:
        excess = (fit.sigma / fit.xi) * (ratio ** (-fit.xi) - 1.0)
    return fit.u + excess


def choose_threshold(
    sorted_x: np.ndarray,
    *,
    quantiles: tuple[float, ...] = THRESHOLD_QUANTILES,
    min_exceedances: int = MIN_EXCEEDANCES,
    xi_prior: tuple[float, float] = (XI_PRIOR_MEAN, XI_PENALTY_SD),
) -> GPDFit:
    """Automated threshold selection by standardised goodness of fit.

    Each candidate u is fitted and scored by ``sqrt(k) * D_k``, the
    Kolmogorov-Smirnov distance between the exceedances and their fitted GPD.
    The sqrt(k) factor is what makes candidates with different exceedance
    counts comparable — raw D_k shrinks with k and would always pick the
    highest, most data-starved threshold. Ties are broken toward more
    exceedances (lower variance).

    Returns the winning fit; falls back to the lowest candidate when none has
    enough exceedances (tiny routes, where every choice is data-starved).
    """
    x = np.asarray(sorted_x, dtype=np.float64)
    n = x.size
    best: tuple[float, GPDFit] | None = None
    for q in quantiles:
        k = int(round(n * (1.0 - q)))
        if k < min_exceedances or k >= n:
            continue
        u = float(np.quantile(x, q, method="linear"))
        y = x[x > u] - u
        if y.size < min_exceedances:
            continue
        fit = fit_gpd(y, u=u, zeta=y.size / n, n=n, xi_prior=xi_prior)
        score = _standardised_ks(y, fit)
        if best is None or score < best[0] - 1e-9:
            best = (score, fit)
    if best is None:
        # Data-starved: take the deepest slice that leaves a usable tail.
        k = max(min(int(round(n * 0.10)), n - 1), 5)
        u = float(x[n - k - 1]) if n - k - 1 >= 0 else float(x[0])
        y = x[x > u] - u
        fit = fit_gpd(y, u=u, zeta=max(y.size, 1) / n, n=n, xi_prior=xi_prior)
        return fit
    return best[1]


def _standardised_ks(y: np.ndarray, fit: GPDFit) -> float:
    """sqrt(k) * KS distance of exceedances from the fitted GPD."""
    ys = np.sort(y)
    k = ys.size
    if k == 0 or fit.sigma <= 0:
        return np.inf
    z = 1.0 + fit.xi * ys / fit.sigma
    if np.any(z <= 0):
        return np.inf
    cdf = 1.0 - z ** (-1.0 / fit.xi) if abs(fit.xi) > 1e-8 else 1.0 - np.exp(-ys / fit.sigma)
    emp = np.arange(1, k + 1) / k
    d = float(np.max(np.abs(cdf - emp) + 1.0 / k))
    return np.sqrt(k) * d


def ks_pvalue(y: np.ndarray, fit: GPDFit) -> float:
    """Asymptotic KS p-value for the fitted tail (diagnostics only)."""
    k = np.asarray(y).size
    if k == 0:
        return float("nan")
    stat = _standardised_ks(y, fit) / np.sqrt(k)
    return float(kstwo.sf(stat, k))


def posterior_quantile_band(
    fit: GPDFit,
    prob: np.ndarray,
    q: float = 0.90,
    n_draws: int = 2000,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Credible band on the extrapolated quantile.

    Samples (xi, log sigma) from the Laplace posterior AND the exceedance rate
    zeta from its Beta posterior — at deep levels the rate uncertainty is a
    material share of the total, and a band that ignores it is the kind of
    overconfidence the rollout guardrails are meant to catch.
    """
    rng = rng or np.random.default_rng(0)
    p = np.atleast_1d(np.asarray(prob, dtype=np.float64))
    if not np.all(np.isfinite(fit.cov)):
        point = gpd_quantile(fit, p)
        return point, point
    draws = rng.multivariate_normal([fit.xi, fit.log_sigma], fit.cov, size=n_draws)
    xi = np.clip(draws[:, 0], XI_MIN, XI_MAX)
    sigma = np.exp(np.clip(draws[:, 1], -30, 30))
    zeta = rng.beta(fit.k + 0.5, max(fit.n - fit.k, 1) + 0.5, size=n_draws)
    ratio = np.clip(p[None, :] / zeta[:, None], 1e-300, None)
    xi_c = xi[:, None]
    excess = np.where(
        np.abs(xi_c) < 1e-8,
        sigma[:, None] * np.log(1.0 / ratio),
        (sigma[:, None] / np.where(np.abs(xi_c) < 1e-8, 1.0, xi_c)) * (ratio ** (-xi_c) - 1.0),
    )
    vals = fit.u + excess
    lo = np.quantile(vals, (1.0 - q) / 2.0, axis=0)
    hi = np.quantile(vals, 1.0 - (1.0 - q) / 2.0, axis=0)
    return lo, hi


_PROFILE_XI_GRID = np.linspace(XI_MIN + 0.01, XI_MAX - 0.01, 25)


def _profile_nll(x_p: float, u: float, ratio: float, y: np.ndarray,
                 xi_prior: tuple[float, float]) -> float:
    """min over xi of the penalized NLL with the quantile pinned at ``x_p``.

    Reparameterises (xi, sigma) as (xi, x_p): for each candidate shape the
    scale that puts the level-p quantile exactly at x_p is closed-form, so
    profiling is a vectorised sweep over the shape grid rather than a nested
    optimisation.
    """
    if x_p <= u:
        return np.inf
    xi = _PROFILE_XI_GRID
    denom = ratio ** (-xi) - 1.0
    with np.errstate(divide="ignore", invalid="ignore"):
        sigma = xi * (x_p - u) / denom
    valid = np.isfinite(sigma) & (sigma > 0)
    if not valid.any():
        return np.inf
    xi_v = xi[valid]
    sigma_v = sigma[valid]
    z = 1.0 + (xi_v / sigma_v)[:, None] * y[None, :]
    ok = np.all(z > 1e-12, axis=1)
    if not ok.any():
        return np.inf
    z = z[ok]
    xi_v = xi_v[ok]
    sigma_v = sigma_v[ok]
    nll = y.size * np.log(sigma_v) + (1.0 + 1.0 / xi_v) * np.sum(np.log(z), axis=1)
    nll = nll + 0.5 * ((xi_v - xi_prior[0]) / xi_prior[1]) ** 2
    return float(np.min(nll))


def profile_likelihood_band(
    y: np.ndarray,
    fit: GPDFit,
    prob: float,
    q: float = 0.90,
    xi_prior: tuple[float, float] = (XI_PRIOR_MEAN, XI_PENALTY_SD),
    max_decades: float = 3.0,
) -> tuple[float, float]:
    """Profile-likelihood interval for the extrapolated quantile at ``prob``.

    Bisects each side of the deviance profile until it crosses the chi2(1)
    cutoff. More faithful than a Laplace band on short tails — where the
    quantile's likelihood is strongly asymmetric — which is exactly the case
    EXP-2 has to survive on small routes.
    """
    from scipy.stats import chi2  # noqa: PLC0415

    y = np.asarray(y, dtype=np.float64)
    y = y[y > 0]
    centre = float(gpd_quantile(fit, prob)[0])
    if y.size < 5 or not np.isfinite(fit.nll):
        return centre, centre
    cutoff = chi2.ppf(q, 1) / 2.0
    ratio = prob / max(fit.zeta, 1e-15)
    base = min(_profile_nll(centre, fit.u, ratio, y, xi_prior), fit.nll)
    span = max(abs(centre - fit.u), 1.0) * max_decades

    def cross(direction: float) -> float:
        lo_edge, hi_edge = centre, centre + direction * span
        if _profile_nll(hi_edge, fit.u, ratio, y, xi_prior) - base <= cutoff:
            return hi_edge
        for _ in range(24):
            mid = 0.5 * (lo_edge + hi_edge)
            if _profile_nll(mid, fit.u, ratio, y, xi_prior) - base > cutoff:
                hi_edge = mid
            else:
                lo_edge = mid
        return 0.5 * (lo_edge + hi_edge)

    return cross(-1.0), cross(1.0)
