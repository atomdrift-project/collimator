"""Tests for training utilities."""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp

from collimator.train import (
    TrainConfig,
    _compute_benign_filetype_weights,
    _compute_metrics,
    _split_calibration_eval,
    train,
)


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


def test_train_supports_azoth() -> None:
    rng = np.random.default_rng(7)
    X = sp.csr_matrix(rng.normal(size=(80, 12)).astype(np.float32))
    y = np.array([0] * 40 + [1] * 40, dtype=np.float32)

    result = train(
        X,
        y,
        TrainConfig(
            learner="azoth",
            n_estimators=8,
            early_stopping_rounds=2,
            n_folds=2,
        ),
    )

    assert result.metrics["brier"] >= 0.0
    assert result.model.__class__.__module__.startswith("lightgbm")
    assert result.cv_predictions.shape == result.cv_labels.shape


# Tests for _grouped_split_indices and groups= were removed — train.py no
# longer supports grouped-holdout / grouped-CV; the canonical_sha256 partitioning
# in data.py handles group leakage at the DB level instead.


def test_compute_metrics_treats_equal_threshold_as_positive() -> None:
    y_true = np.array([1, 0], dtype=np.float32)
    y_prob = np.array([0.5, 0.4], dtype=np.float32)

    metrics = _compute_metrics(y_true, y_prob, threshold=0.5)

    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0


def test_compute_benign_filetype_weights_only_affects_selected_benign_rows() -> None:
    file_types = np.array(["pe", "javascript", "pe", "python"], dtype=object)
    y = np.array([0, 0, 1, 0], dtype=np.float32)

    weights = _compute_benign_filetype_weights(
        file_types,
        y,
        weights_by_filetype={"pe": 2.0, "python": 1.5},
    )

    assert weights is not None
    np.testing.assert_array_equal(weights, np.array([2.0, 1.0, 1.0, 1.5], dtype=np.float32))


def test_train_rejects_filetype_weights_without_sample_file_types() -> None:
    rng = np.random.default_rng(11)
    X = sp.csr_matrix(rng.normal(size=(40, 6)).astype(np.float32))
    y = np.array([0] * 20 + [1] * 20, dtype=np.float32)

    try:
        train(
            X,
            y,
            TrainConfig(
                n_estimators=5,
                early_stopping_rounds=2,
                n_folds=2,
                device="cpu",
                benign_filetype_weights={"pe": 2.0},
            ),
        )
    except ValueError as exc:
        assert "sample_file_types" in str(exc)
    else:
        raise AssertionError("expected ValueError when sample_file_types are missing")
