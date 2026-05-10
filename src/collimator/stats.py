"""Bootstrap CIs and paired-difference tests for honest reporting.

Used by azoth_calibrate_ensemble.py and experiment.py to attach (point,
low, high) tuples to every emitted metric and to compute paired Δ-CIs
when claiming one model beats another.

The convention everywhere: ``metric_fn(y_true, y_score) -> float``.
``y_score`` may be a probability (for AUC/PR-AUC), a thresholded label
(for F1/recall/precision), or any other vector aligned with ``y_true``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

MetricFn = Callable[[np.ndarray, np.ndarray], float]

DEFAULT_N_RESAMPLES = 1000
DEFAULT_CONFIDENCE = 0.95
DEFAULT_SEED = 42


def _stratum_keys(stratify: np.ndarray | None, n: int) -> np.ndarray:
    """Return a stratum-id array of length n. None or empty → single stratum."""
    if stratify is None:
        return np.zeros(n, dtype=np.int64)
    arr = np.asarray(stratify)
    if arr.ndim == 0:
        return np.zeros(n, dtype=np.int64)
    if len(arr) != n:
        raise ValueError(f"stratify length {len(arr)} does not match data length {n}")
    # Map arbitrary values to dense integer ids.
    _, ids = np.unique(arr, return_inverse=True)
    return ids


def _resampled_indices(
    n: int,
    stratum_ids: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """One bootstrap resample: sample n indices with replacement, stratified."""
    if stratum_ids.max(initial=-1) <= 0:
        return rng.integers(0, n, size=n)
    out = np.empty(n, dtype=np.int64)
    cursor = 0
    for stratum in np.unique(stratum_ids):
        mask = np.where(stratum_ids == stratum)[0]
        m = len(mask)
        out[cursor : cursor + m] = rng.choice(mask, size=m, replace=True)
        cursor += m
    return out


def bootstrap_metric(
    y_true: np.ndarray,
    y_score: np.ndarray,
    metric_fn: MetricFn,
    *,
    n_resamples: int = DEFAULT_N_RESAMPLES,
    confidence_level: float = DEFAULT_CONFIDENCE,
    seed: int | None = DEFAULT_SEED,
    stratify: np.ndarray | None = None,
) -> dict[str, Any]:
    """Bootstrap a single metric, returning ``{point, low, high, ...}``.

    Stratify rows by ``(filetype, label)`` or similar to keep the resampled
    class balance representative when reporting aggregate metrics.
    """
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)
    n = len(y_true)
    if n == 0:
        return {
            "point": float("nan"),
            "low": float("nan"),
            "high": float("nan"),
            "n_resamples": 0,
            "n_rows": 0,
            "confidence_level": confidence_level,
        }
    point = float(metric_fn(y_true, y_score))
    rng = np.random.default_rng(seed)
    stratum_ids = _stratum_keys(stratify, n)
    samples = np.empty(n_resamples, dtype=np.float64)
    for i in range(n_resamples):
        idx = _resampled_indices(n, stratum_ids, rng)
        try:
            samples[i] = metric_fn(y_true[idx], y_score[idx])
        except (ValueError, ZeroDivisionError):
            # Degenerate resamples (e.g. one-class) — mark and drop later.
            samples[i] = np.nan
    valid = samples[~np.isnan(samples)]
    if len(valid) == 0:
        low = high = float("nan")
    else:
        alpha = (1.0 - confidence_level) / 2.0
        low = float(np.quantile(valid, alpha))
        high = float(np.quantile(valid, 1.0 - alpha))
    return {
        "point": point,
        "low": low,
        "high": high,
        "n_resamples": int(len(valid)),
        "n_rows": n,
        "confidence_level": confidence_level,
    }


def paired_bootstrap_diff(
    y_true: np.ndarray,
    y_score_a: np.ndarray,
    y_score_b: np.ndarray,
    metric_fn: MetricFn,
    *,
    n_resamples: int = DEFAULT_N_RESAMPLES,
    confidence_level: float = DEFAULT_CONFIDENCE,
    seed: int | None = DEFAULT_SEED,
    stratify: np.ndarray | None = None,
) -> dict[str, Any]:
    """Paired bootstrap of ``metric(A) - metric(B)`` on the same resampled rows.

    Returns the point Δ, its CI, and a two-sided bootstrap p-value (twice the
    smaller tail mass). A 95% CI that excludes 0 corresponds to p < 0.05.
    """
    y_true = np.asarray(y_true)
    y_score_a = np.asarray(y_score_a)
    y_score_b = np.asarray(y_score_b)
    n = len(y_true)
    if n == 0:
        return {
            "diff": float("nan"),
            "low": float("nan"),
            "high": float("nan"),
            "p_two_sided": float("nan"),
            "n_resamples": 0,
            "n_rows": 0,
            "confidence_level": confidence_level,
        }
    point_a = float(metric_fn(y_true, y_score_a))
    point_b = float(metric_fn(y_true, y_score_b))
    diff = point_a - point_b
    rng = np.random.default_rng(seed)
    stratum_ids = _stratum_keys(stratify, n)
    deltas = np.empty(n_resamples, dtype=np.float64)
    for i in range(n_resamples):
        idx = _resampled_indices(n, stratum_ids, rng)
        yt = y_true[idx]
        try:
            deltas[i] = metric_fn(yt, y_score_a[idx]) - metric_fn(yt, y_score_b[idx])
        except (ValueError, ZeroDivisionError):
            deltas[i] = np.nan
    valid = deltas[~np.isnan(deltas)]
    if len(valid) == 0:
        return {
            "diff": diff,
            "low": float("nan"),
            "high": float("nan"),
            "p_two_sided": float("nan"),
            "n_resamples": 0,
            "n_rows": n,
            "confidence_level": confidence_level,
        }
    alpha = (1.0 - confidence_level) / 2.0
    low = float(np.quantile(valid, alpha))
    high = float(np.quantile(valid, 1.0 - alpha))
    # Two-sided bootstrap p-value: twice the smaller tail of (deltas <= 0)
    # vs (deltas >= 0). Capped at 1.0.
    n_valid = len(valid)
    p_le = float(np.sum(valid <= 0.0)) / n_valid
    p_ge = float(np.sum(valid >= 0.0)) / n_valid
    p_two_sided = float(min(1.0, 2.0 * min(p_le, p_ge)))
    return {
        "diff": diff,
        "low": low,
        "high": high,
        "p_two_sided": p_two_sided,
        "n_resamples": n_valid,
        "n_rows": n,
        "confidence_level": confidence_level,
    }


def fdr_adjust(p_values: list[float], *, alpha: float = 0.05) -> tuple[list[float], list[bool]]:
    """Benjamini–Hochberg FDR correction.

    Returns ``(adjusted_p_values, reject)``: adjusted p-values aligned with the
    input order, and a boolean list of which hypotheses survive at level alpha.
    Avoids a statsmodels dependency for one helper.
    """
    if not p_values:
        return [], []
    p = np.asarray(p_values, dtype=np.float64)
    m = len(p)
    order = np.argsort(p)
    ranks = np.empty(m, dtype=np.int64)
    ranks[order] = np.arange(1, m + 1)
    adjusted = np.minimum(1.0, p * m / ranks)
    # Enforce monotonicity over sorted p-values.
    sorted_adj = adjusted[order]
    for i in range(m - 2, -1, -1):
        sorted_adj[i] = min(sorted_adj[i], sorted_adj[i + 1])
    final = np.empty(m, dtype=np.float64)
    final[order] = sorted_adj
    reject = final <= alpha
    return final.tolist(), reject.tolist()
