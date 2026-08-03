#!/usr/bin/env python3
"""Common estimator API for the FP-curve experiments (see FP_CURVE_PROPOSAL.md).

Every estimator maps a benign score sample to a continuous level->threshold
curve. ``level`` is the fleet's canonical wire unit: level k == k false
positives per 100M benign files (``collimator.thresholds._LEVELS_PER_100M``),
so the exceedance probability at level k is ``k * 1e-8``.

All fitting happens in LOGIT space. That is not a stylistic choice: the GPD
attempt deleted on 2026-06-06 overshot past p=1 because it modelled bounded
probabilities directly (METHODOLOGY.md). Logit space is unbounded, so
overshoot is impossible by construction, and the tail shapes EVT assumes are
much better behaved there.

Sign conventions used everywhere:

* thresholds are LOGITS (use :func:`from_logit` to emit probabilities);
* the curve is *decreasing* in level (stricter level -> higher threshold);
* level 0 means "zero FP" and is handled by :meth:`CurveModel.threshold`
  via the shared L0 rule, never by an estimator's own extrapolation.
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.special import expit
from scipy.stats import beta as _beta

# Probability clip before the logit transform. float32 model probs never reach
# 1.0 in practice (multi-seed averaging leaves the max benign near 0.999), but
# clip anyway so a future single-seed pool can't produce infinities.
LOGIT_EPS = 1e-7

# The deploy grid's loosest anchor (collimator.thresholds._LEVELS_PER_100M).
MAX_GRID_LEVEL = 25_000.0

# Level at which the model curve is evaluated to answer "L0". L0 nominally
# means p=0 (an infinite threshold); every estimator answers the strictest
# level anyone can name instead, then the shared L0 rule lifts it above the
# max observed benign so L0 keeps its "zero observed FP" meaning.
L0_EVAL_LEVEL = 1e-3

# Confidence used for the Clopper-Pearson floor reported on every emitted row.
CP_FLOOR_CONFIDENCE = 0.95


def to_logit(p: np.ndarray | float) -> np.ndarray | float:
    """Probability -> logit, clipped to keep the transform finite."""
    arr = np.clip(np.asarray(p, dtype=np.float64), LOGIT_EPS, 1.0 - LOGIT_EPS)
    out = np.log(arr) - np.log1p(-arr)
    return float(out) if np.isscalar(p) or out.ndim == 0 else out


def from_logit(z: np.ndarray | float) -> np.ndarray | float:
    """Logit -> probability."""
    out = expit(np.asarray(z, dtype=np.float64))
    return float(out) if np.isscalar(z) or out.ndim == 0 else out


def level_to_prob(level: np.ndarray | float) -> np.ndarray | float:
    """Level k -> benign exceedance probability (k FP per 100M benigns)."""
    return np.asarray(level, dtype=np.float64) * 1e-8


def prob_to_level(prob: np.ndarray | float) -> np.ndarray | float:
    """Benign exceedance probability -> level."""
    return np.asarray(prob, dtype=np.float64) * 1e8


def floor_level(n_benign: int) -> float:
    """Strictest level a pool of ``n_benign`` can measure (its 1-FP point)."""
    return 1e8 / max(int(n_benign), 1)


def cp_floor_per_100M(n_benign: int, confidence: float = CP_FLOOR_CONFIDENCE) -> float:
    """Clopper-Pearson upper bound on the FP rate after observing zero FP.

    This is the honesty annotation carried on every emitted row: with zero
    observed false positives in ``n`` benigns, no measurement can certify a
    rate below this, no matter what a model predicts. Emitting it next to a
    sub-floor threshold is what keeps a model claim from reading as a
    measurement.
    """
    n = max(int(n_benign), 1)
    return float(1e8 * (1.0 - (1.0 - confidence) ** (1.0 / n)))


def draw_seed(*parts: Any) -> int:
    """Deterministic 63-bit seed from arbitrary parts (pool, rung, draw idx)."""
    digest = hashlib.sha256("|".join(str(p) for p in parts).encode()).digest()
    return int.from_bytes(digest[:8], "big") >> 1


@dataclass(frozen=True, slots=True)
class RouteMeta:
    """Identity and size of the route being fitted."""

    route: str  # "filetypes/pe"
    filegroup: str  # "native" | "other" — hierarchy parent for pooled methods
    n_benign: int
    n_malware: int = 0

    @property
    def floor_level(self) -> float:
        return floor_level(self.n_benign)


@dataclass(frozen=True, slots=True)
class RouteTail:
    """One route's benign upper tail, as pooling context for other routes.

    Only the top ``len(tail_logits)`` benign scores are kept: pooled tail
    estimators never look below their exceedance threshold, and keeping full
    pools for 73 routes would cost ~10x the memory for no information.
    ``n_benign`` is retained so the exceedance *rate* at any tail level is
    recoverable (rate = rank / n_benign).
    """

    route: str
    filegroup: str
    n_benign: int
    tail_logits: np.ndarray  # ascending, the top-k benign logits

    @property
    def tail_fraction(self) -> float:
        """P(X > min(tail_logits)) — the rate the kept tail represents."""
        return len(self.tail_logits) / max(self.n_benign, 1)


@dataclass(frozen=True)
class PooledContext:
    """Cross-route context handed to pooling / covariate estimators.

    The leakage rule from the proposal lives here: when a teacher pool is
    being evaluated, its own route must not appear in ``tails``. Build with
    :meth:`without` rather than filtering by hand at each call site.
    """

    tails: tuple[RouteTail, ...] = ()
    extras: dict[str, Any] = field(default_factory=dict)

    def without(self, route: str) -> PooledContext:
        return PooledContext(
            tails=tuple(t for t in self.tails if t.route != route),
            extras=self.extras,
        )

    def by_filegroup(self, filegroup: str) -> tuple[RouteTail, ...]:
        return tuple(t for t in self.tails if t.filegroup == filegroup)

    def __len__(self) -> int:
        return len(self.tails)


EMPTY_CONTEXT = PooledContext()


# Logit of the float32 probability ceiling: float32 cannot represent a
# probability between 1-6e-8 and 1, and the LOGIT_EPS clip maps both onto
# this value. A benign score here is one the model scored 1.0 on.
SATURATION_LOGIT = 16.0


@dataclass(frozen=True, slots=True)
class Saturation:
    """A benign score atom at the top of a route's distribution.

    12 of the fleet's 73 routes have benign files whose float32 probability is
    exactly 1.0 — the model has saturated on them. No threshold can exclude a
    saturated benign without also excluding every saturated *malware* sample,
    so those routes have a hard FP floor that no estimator can predict its way
    below. Curves clamp at the atom and say so, rather than emitting a
    threshold whose claimed FP rate is unreachable in deployment.
    """

    count: int  # benigns tied at the top score
    logit: float  # the atom's score (inf when there is no atom)
    floor_per_100M: float  # the FP rate that atom imposes

    @property
    def present(self) -> bool:
        return self.count >= 1 and np.isfinite(self.logit)


def detect_saturation(sorted_logits: np.ndarray, ceiling: float = SATURATION_LOGIT) -> Saturation:
    """Find benign scores sitting on the model's output ceiling.

    Only *ceiling contact* counts. Score ties elsewhere in the distribution
    are common — ``filetypes/c`` has 14,448 benigns tied at p=0.0026 from
    feature quantisation — and a threshold can always be placed just above
    such an atom, so treating those as saturation would clamp the whole curve
    onto an interior value and produce a ~1% FP rate at every level.
    """
    x = np.asarray(sorted_logits, dtype=np.float64)
    n = x.size
    if n == 0 or float(x[-1]) < ceiling:
        return Saturation(0, np.inf, 0.0)
    count = int(n - np.searchsorted(x, ceiling, side="left"))
    return Saturation(count, float(x[-1]), count / n * 1e8)


class CurveModel(ABC):
    """A fitted level->threshold curve.

    Subclasses implement :meth:`_thresholds` (vectorised, logit space, levels
    strictly positive) and :meth:`_band`. Everything shared — the L0 rule,
    scalar/array handling, grid emission, the extrapolation flag — lives here
    so every estimator emits the same contract to scan.
    """

    method: str = "base"

    def __init__(
        self,
        meta: RouteMeta,
        max_observed_logit: float,
        fit_floor_level: float,
        saturation: Saturation | None = None,
    ):
        self.meta = meta
        # Highest benign score actually seen in the fitted sample. The L0 rule
        # and the "is this row a measurement or a model claim?" flag key off it.
        self.max_observed_logit = float(max_observed_logit)
        # Strictest level this fit can *measure* (its own 1-FP point). Levels
        # below this are extrapolation for every estimator, EXP-1 included
        # (which is why EXP-1 clamps there instead of extrapolating).
        self.fit_floor_level = float(fit_floor_level)
        self.saturation = saturation or Saturation(0, np.inf, 0.0)

    # -- estimator hooks -----------------------------------------------------

    @abstractmethod
    def _thresholds(self, levels: np.ndarray) -> np.ndarray:
        """Logit thresholds at strictly positive levels."""

    @abstractmethod
    def _band(self, levels: np.ndarray, q: float) -> tuple[np.ndarray, np.ndarray]:
        """(lo, hi) logit-threshold band at the given levels."""

    # -- shared surface ------------------------------------------------------

    def thresholds(self, levels: Sequence[float] | np.ndarray) -> np.ndarray:
        """Vectorised threshold lookup, with the shared L0 rule applied."""
        lv = np.asarray(levels, dtype=np.float64)
        positive = np.where(lv > 0.0, lv, L0_EVAL_LEVEL)
        out = np.asarray(self._thresholds(positive), dtype=np.float64)
        zero = lv <= 0.0
        if zero.any():
            # L0 means "no benign fires". A model may legitimately predict a
            # threshold above the observed max (that is the whole point of
            # extrapolation), but it may never predict one below it and still
            # call it zero-FP.
            out = np.where(zero, np.maximum(out, np.nextafter(self.max_observed_logit, np.inf)), out)
        if self.saturation.present:
            # Above the atom the threshold buys no FP reduction it can keep:
            # every saturated benign scores there, and so does saturated
            # malware. Clamping is the honest answer; the row is flagged.
            out = np.minimum(out, self.saturation.logit)
        # Physical bound for every estimator: a threshold is a probability and
        # cannot exceed 1.0. An extrapolation that lands at logit 500 and one
        # that lands at the ceiling mean the same thing operationally —
        # nothing fires — but only one of them is representable.
        return np.minimum(out, SATURATION_LOGIT)

    def threshold(self, level: float) -> float:
        """Threshold (logit) at one level — the proposal's API entry point."""
        return float(self.thresholds(np.array([level], dtype=np.float64))[0])

    def band(self, level: float, q: float = 0.90) -> tuple[float, float]:
        """Central ``q`` band on the threshold at ``level`` (logit space)."""
        lo, hi = self._band(np.array([max(level, L0_EVAL_LEVEL)], dtype=np.float64), q)
        return float(np.asarray(lo)[0]), float(np.asarray(hi)[0])

    def is_extrapolated(self, level: float) -> bool:
        """True when this row is a model claim rather than a measurement."""
        return bool(level < self.fit_floor_level)

    def row_extras(self, level: float) -> dict[str, Any]:  # noqa: ARG002 — hook
        """Per-row diagnostics an estimator wants carried into the table."""
        return {}

    def to_grid(self, levels: Sequence[float], q: float = 0.90) -> list[dict[str, Any]]:
        """Emit the bundle/scan table for ``levels``.

        Every sub-floor row carries ``model_extrapolated`` and
        ``cp_floor_per_100M`` so no consumer can mistake a model claim for a
        measurement (proposal, "Rollout & guardrails").
        """
        lv = np.asarray(levels, dtype=np.float64)
        thr = self.thresholds(lv)
        lo, hi = self._band(np.where(lv > 0.0, lv, L0_EVAL_LEVEL), q)
        cp_floor = cp_floor_per_100M(self.meta.n_benign)
        rows: list[dict[str, Any]] = []
        for i, level in enumerate(lv):
            rows.append({
                **self.row_extras(float(level)),
                "level": float(level),
                "threshold": float(from_logit(thr[i])),
                "threshold_logit": float(thr[i]),
                "band_lo_logit": float(lo[i]),
                "band_hi_logit": float(hi[i]),
                "band_q": float(q),
                "method": self.method,
                "model_extrapolated": self.is_extrapolated(float(level)),
                "cp_floor_per_100M": cp_floor,
                "fit_floor_per_100M": self.fit_floor_level,
                "saturation_floor_per_100M": self.saturation.floor_per_100M,
                "saturation_limited": bool(
                    self.saturation.present and level < self.saturation.floor_per_100M,
                ),
                "n_benign_fit": int(self.meta.n_benign),
            })
        return rows


# ---------------------------------------------------------------------------
# Shared numerics
# ---------------------------------------------------------------------------


def empirical_threshold(sorted_logits: np.ndarray, levels: np.ndarray) -> np.ndarray:
    """Measured truth: the Type-7 benign quantile at each level.

    Same interpolation convention as the incumbent
    (``collimator.thresholds.quantile_severity_threshold``) so threshold-error
    comparisons are apples-to-apples. Levels below the pool's 1-FP floor
    return the max observed score — unmeasurable, and the caller is expected
    to drop those points rather than score against them.
    """
    prob = level_to_prob(np.asarray(levels, dtype=np.float64))
    q = np.clip(1.0 - prob, 0.0, 1.0)
    return np.quantile(sorted_logits, q, method="linear")


def harrell_davis(sorted_x: np.ndarray, q: np.ndarray, mass_eps: float = 1e-12) -> np.ndarray:
    """Harrell-Davis quantile estimates for a sorted sample.

    HD is a beta-kernel weighted average of *all* order statistics, so it is
    smooth in q where the raw order statistics step. That smoothness is what
    EXP-1 needs to answer between-grid queries (L21, L22) without inventing a
    curve shape.

    For deep quantiles the beta kernel is extremely concentrated near the top
    order statistic, so only a window of ranks carries mass; computing the
    full n-length weight vector per quantile would be O(n) per level for no
    gain. The window is chosen from the beta quantile function at
    ``mass_eps`` and always includes the extreme order statistic.
    """
    x = np.asarray(sorted_x, dtype=np.float64)
    n = x.size
    if n == 0:
        raise ValueError("harrell_davis: empty sample")
    if n == 1:
        return np.full(np.shape(q), x[0], dtype=np.float64)
    qs = np.atleast_1d(np.asarray(q, dtype=np.float64))
    out = np.empty(qs.shape, dtype=np.float64)
    for i, qi in enumerate(qs):
        qi = float(np.clip(qi, 1e-12, 1.0 - 1e-12))
        a = (n + 1) * qi
        b = (n + 1) * (1.0 - qi)
        lo_p = _beta.ppf(mass_eps, a, b)
        hi_p = _beta.ppf(1.0 - mass_eps, a, b)
        lo = max(0, int(np.floor(lo_p * n)) - 1)
        hi = min(n, int(np.ceil(hi_p * n)) + 1)
        if hi <= lo:
            out[i] = x[min(max(int(round(qi * n)) - 1, 0), n - 1)]
            continue
        edges = np.arange(lo, hi + 1, dtype=np.float64) / n
        cdf = _beta.cdf(edges, a, b)
        w = np.diff(cdf)
        total = w.sum()
        if not np.isfinite(total) or total <= 0:
            out[i] = x[min(max(int(round(qi * n)) - 1, 0), n - 1)]
            continue
        out[i] = float(np.dot(w, x[lo:hi]) / total)
    return out if np.ndim(q) else out.reshape(())


def order_statistic_band(
    sorted_logits: np.ndarray, levels: np.ndarray, q: float = 0.90,
) -> tuple[np.ndarray, np.ndarray]:
    """Distribution-free band on a benign quantile, from order statistics.

    The number of benigns above a fixed threshold is Binomial(n, p), so the
    binomial quantiles at ``(1±q)/2`` bracket the rank of the true level-p
    quantile. Above the sample's floor this is the exact nonparametric
    interval; below it (expected exceedances < 1) the upper end runs off the
    top of the sample and is returned as ``+inf`` — honest, and deliberately
    vacuous, which is why the harness also reports band width.
    """
    x = np.asarray(sorted_logits, dtype=np.float64)
    n = x.size
    p = level_to_prob(np.asarray(levels, dtype=np.float64))
    alpha = (1.0 - q) / 2.0
    # Exceedance-count bounds -> rank bounds (rank counted from the top).
    from scipy.stats import binom  # noqa: PLC0415 — local, only needed here

    k_lo = binom.ppf(alpha, n, p)
    k_hi = binom.ppf(1.0 - alpha, n, p)
    lo = np.empty(p.shape, dtype=np.float64)
    hi = np.empty(p.shape, dtype=np.float64)
    for i in range(p.size):
        # More exceedances than expected -> the true threshold sits lower.
        idx_lo = n - int(min(max(k_hi[i], 1), n))
        idx_hi = n - int(min(max(k_lo[i], 1), n))
        lo[i] = x[idx_lo]
        hi[i] = np.inf if k_lo[i] < 1 else x[idx_hi]
    return lo, hi


def monotone_violations(model: CurveModel, levels: np.ndarray) -> int:
    """Count strict-monotonicity violations of a fitted curve.

    Deliberately *measured*, not enforced: enforcing monotonicity at emission
    would hide an estimator whose tail model is unstable, and gate 2 of the
    decision rule exists to catch exactly that.
    """
    lv = np.sort(np.asarray(levels, dtype=np.float64))
    thr = model.thresholds(lv)
    return int(np.sum(np.diff(thr) >= 0.0))
