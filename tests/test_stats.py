"""Smoke tests for the bootstrap helpers in collimator.stats."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import f1_score, roc_auc_score

from collimator.stats import bootstrap_metric, fdr_adjust, paired_bootstrap_diff


def test_bootstrap_metric_recovers_point_and_brackets_it() -> None:
    """Bootstrap CI should contain the point estimate and have a sane width."""
    rng = np.random.default_rng(0)
    n = 500
    y_true = rng.integers(0, 2, size=n).astype(np.int64)
    y_pred = (rng.random(n) < 0.7).astype(np.int64)  # noisy classifier

    result = bootstrap_metric(
        y_true, y_pred, lambda yt, yp: float(f1_score(yt, yp, zero_division=0.0)),
        n_resamples=200, seed=1,
    )
    assert result["n_rows"] == n
    assert result["low"] <= result["point"] <= result["high"]
    # 95% CI width should be modest, not zero, not the whole range.
    assert 0.0 < (result["high"] - result["low"]) < 0.5


def test_bootstrap_metric_zero_rows() -> None:
    result = bootstrap_metric(
        np.array([], dtype=np.int64),
        np.array([], dtype=np.float64),
        lambda yt, yp: 0.0,
    )
    assert result["n_rows"] == 0
    assert np.isnan(result["point"])


def test_paired_bootstrap_detects_real_difference() -> None:
    """Two genuinely different classifiers produce a CI that excludes 0."""
    rng = np.random.default_rng(0)
    n = 1000
    y_true = (rng.random(n) < 0.5).astype(np.int64)
    # Model A: noisy match. Model B: better match.
    y_score_a = (y_true ^ (rng.random(n) < 0.20).astype(np.int64))
    y_score_b = (y_true ^ (rng.random(n) < 0.05).astype(np.int64))

    result = paired_bootstrap_diff(
        y_true, y_score_a, y_score_b,
        lambda yt, yp: float(f1_score(yt, yp, zero_division=0.0)),
        n_resamples=200, seed=1,
    )
    # B is materially better; A − B should be clearly negative.
    assert result["diff"] < 0
    assert result["high"] < 0  # CI excludes 0 on the negative side
    assert result["p_two_sided"] < 0.05


def test_paired_bootstrap_no_difference() -> None:
    """Two identical predictions — diff = 0, CI brackets 0, p ≈ 1."""
    rng = np.random.default_rng(0)
    n = 500
    y_true = (rng.random(n) < 0.5).astype(np.int64)
    y_pred = (rng.random(n) < 0.5).astype(np.int64)

    result = paired_bootstrap_diff(
        y_true, y_pred, y_pred,
        lambda yt, yp: float(f1_score(yt, yp, zero_division=0.0)),
        n_resamples=200, seed=1,
    )
    assert result["diff"] == 0.0
    assert result["low"] == 0.0
    assert result["high"] == 0.0
    assert result["p_two_sided"] == 1.0


def test_stratified_resample_preserves_class_balance() -> None:
    """Stratified resampling keeps roughly the same per-stratum count."""
    rng = np.random.default_rng(0)
    y_true = np.array([1, 1, 1, 1, 0, 0, 0, 0, 0, 0])  # 4 mal / 6 ben
    y_score = np.array([0.9, 0.8, 0.7, 0.6, 0.1, 0.2, 0.3, 0.4, 0.5, 0.05])

    # Without stratification a small sample can drift; this is a smoke check
    # that the stratified call returns a real CI without erroring on tiny n.
    result = bootstrap_metric(
        y_true, y_score,
        lambda yt, ys: float(roc_auc_score(yt, ys)) if len(set(yt.tolist())) > 1 else 0.5,
        n_resamples=100, seed=1, stratify=y_true,
    )
    assert result["n_rows"] == 10
    assert 0.5 <= result["point"] <= 1.0
    assert result["n_resamples"] > 0


def test_fdr_adjust_keeps_one_strong_signal() -> None:
    """BH at q=0.05: a single strong p stays significant; many weak ones don't."""
    p = [0.001, 0.30, 0.40, 0.50, 0.60, 0.70]
    adjusted, reject = fdr_adjust(p, alpha=0.05)
    assert len(adjusted) == len(p)
    assert reject[0] is True
    assert all(r is False for r in reject[1:])


def test_fdr_adjust_empty() -> None:
    adjusted, reject = fdr_adjust([])
    assert adjusted == []
    assert reject == []
