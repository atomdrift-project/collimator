"""Tests for training utilities."""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp

from collimator.train import TrainConfig, _split_calibration_eval, train


def test_split_calibration_eval_returns_disjoint_stratified_splits() -> None:
    X = np.arange(64, dtype=np.float32).reshape(16, 4)
    y = np.array([0] * 8 + [1] * 8, dtype=np.float32)

    calibration, evaluation = _split_calibration_eval(X, y)

    assert calibration is not None
    X_calib, y_calib = calibration
    X_eval, y_eval = evaluation

    assert len(X_calib) == len(X_eval) == 8
    assert int(np.sum(y_calib == 1)) == 4
    assert int(np.sum(y_eval == 1)) == 4

    calib_rows = {tuple(row) for row in X_calib.tolist()}
    eval_rows = {tuple(row) for row in X_eval.tolist()}
    assert calib_rows.isdisjoint(eval_rows)


def test_split_calibration_eval_falls_back_when_holdout_too_small() -> None:
    X = np.arange(24, dtype=np.float32).reshape(6, 4)
    y = np.array([0, 0, 0, 1, 1, 1], dtype=np.float32)

    calibration, evaluation = _split_calibration_eval(X, y)

    assert calibration is None
    X_eval, y_eval = evaluation
    np.testing.assert_array_equal(X_eval, X)
    np.testing.assert_array_equal(y_eval, y)


def test_train_reports_split_summary_and_brier() -> None:
    rng = np.random.default_rng(42)
    X = sp.csr_matrix(rng.normal(size=(80, 12)).astype(np.float32))
    y = np.array([0] * 40 + [1] * 40, dtype=np.float32)

    result = train(
        X,
        y,
        TrainConfig(n_estimators=5, early_stopping_rounds=2, n_folds=2, device="cpu"),
    )

    assert "brier" in result.metrics
    assert "ece" in result.calibration
    assert isinstance(result.calibration["bins"], list)
    assert result.split_summary["policy"] in {"train/calibration/evaluation", "train/holdout"}
    assert int(result.split_summary["train_samples"]) > 0
    assert int(result.split_summary["evaluation_samples"]) > 0
