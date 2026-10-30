"""Tests for training utilities."""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp
import pytest

from collimator.train import (
    TrainConfig,
    _compute_benign_filetype_weights,
    _compute_metrics,
    _split_calibration_eval,
    train,
    _sparse_feature_moments,
)


def test_retained_tree_count_handles_lightgbm_one_based_best_iteration():
    import lightgbm as lgb
    from collimator.train import _retained_tree_count

    X = np.arange(200, dtype=float).reshape(-1, 1)
    y = (X[:, 0] >= 100).astype(int)
    estimator = lgb.LGBMClassifier(n_estimators=20, n_jobs=1, verbosity=-1, metric="None")
    estimator.fit(X, y, eval_set=[(X.copy(), y.copy())],
                  eval_metric=lambda y, p: ("constant", .5, True),
                  callbacks=[lgb.early_stopping(3, verbose=False)])
    assert estimator.best_iteration_ == 1
    assert _retained_tree_count(estimator) == 1


def test_retained_tree_count_handles_xgboost_best_iteration_zero():
    from types import SimpleNamespace
    from collimator.train import _retained_tree_count

    assert _retained_tree_count(SimpleNamespace(best_iteration=0)) == 1
    assert _retained_tree_count(SimpleNamespace(best_iteration=399)) == 400
    assert _retained_tree_count(SimpleNamespace(
        get_booster=lambda: SimpleNamespace(num_boosted_rounds=lambda: 17))) == 17


@pytest.mark.parametrize('dtype', [np.float32, np.float64, np.int32])
def test_sparse_moments_are_bounded_and_preserve_input(monkeypatch, dtype):
    import collimator.train as module
    monkeypatch.setattr(module, '_STD_VARIANCE_CHUNK', 3)
    dense = np.array([[0, 2, 0, 7], [1, 0, 0, 7], [3, 4, 0, 7],
                      [0, -5, 0, 7], [6, 0, 0, 7]], dtype=dtype)
    X = sp.csr_matrix(dense)
    saved = X.copy()
    def forbidden(*args, **kwargs):
        raise AssertionError('full sparse mean copy')
    monkeypatch.setattr(sp.csr_matrix, 'mean', forbidden)
    means, stds = _sparse_feature_moments(X)
    expected_std = dense.astype(np.float64).std(axis=0)
    expected_std[expected_std < 1e-7] = 1
    np.testing.assert_allclose(means, dense.mean(axis=0), rtol=1e-6, atol=1e-6)
    np.testing.assert_allclose(stds, expected_std, rtol=1e-6)
    np.testing.assert_array_equal(X.data, saved.data)
    np.testing.assert_array_equal(X.indices, saved.indices)


def test_sparse_moments_duplicate_entries_and_large_values(monkeypatch):
    import collimator.train as module
    monkeypatch.setattr(module, '_STD_VARIANCE_CHUNK', 1)
    X = sp.csr_matrix((np.array([1e20, 1e20, 2e20], dtype=np.float32),
                       [0, 0, 1], [0, 2, 3]), shape=(2, 3))
    expected = X.astype(np.float64).toarray()
    means, stds = _sparse_feature_moments(X)
    np.testing.assert_allclose(means, expected.mean(axis=0), rtol=1e-6)
    expected_std = expected.std(axis=0)
    expected_std[expected_std < 1e-7] = 1
    np.testing.assert_allclose(stds, expected_std, rtol=1e-6)
    assert X.nnz == 3


def test_hard_negative_batches_preserve_global_selection_and_ties(monkeypatch):
    import collimator.train as module
    monkeypatch.setattr(module, '_HARD_NEGATIVE_CHUNK', 3)
    X = sp.csr_matrix(np.array([[.2], [.9], [.1], [.9], [.8], [.2], [.9], [.3]]))
    y = np.array([0, 0, 1, 0, 0, 1, 0, 0])
    sizes = []
    def predict(model, block):
        sizes.append(block.shape[0])
        return block.toarray().ravel()
    monkeypatch.setattr(module, 'predict_proba', predict)
    result = module._compute_hard_negative_weights(None, X, y, fraction=.5, weight=5)
    benign = np.flatnonzero(y == 0)
    selected = benign[np.argsort(X.toarray().ravel()[benign])[-3:]]
    expected = np.ones(len(y), dtype=np.float32)
    expected[selected] = 5
    np.testing.assert_array_equal(result, expected)
    assert sizes == [3, 3]


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
