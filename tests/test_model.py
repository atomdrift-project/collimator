"""Tests for XGBoost model creation and prediction."""

import numpy as np

from collimator.model import create_classifier, predict_proba


def test_create_classifier_defaults() -> None:
    model = create_classifier(n_benign=100, n_malware=50, device="cpu")
    assert model.get_params()["objective"] == "binary:logistic"
    # Default max_depth bumped from 6 → 10 for v16 (deeper trees for the larger
    # feature space). Tests specifying a specific depth should pass it explicitly.
    assert model.get_params()["max_depth"] == 10


def test_create_classifier_custom_params() -> None:
    model = create_classifier(
        n_benign=100, n_malware=50, device="cpu",
        max_depth=4, n_estimators=50, learning_rate=0.1,
    )
    assert model.get_params()["max_depth"] == 4
    assert model.get_params()["n_estimators"] == 50
    assert model.get_params()["learning_rate"] == 0.1


def test_create_classifier_azoth() -> None:
    model = create_classifier(
        n_benign=100,
        n_malware=50,
        learner="azoth",
        max_depth=4,
        n_estimators=50,
        learning_rate=0.1,
    )

    assert model.__class__.__module__.startswith("lightgbm")
    assert model.get_params()["objective"] == "binary"
    assert model.get_params()["n_estimators"] == 50


def test_create_classifier_azoth_leaf_params() -> None:
    model = create_classifier(
        n_benign=100,
        n_malware=50,
        learner="azoth",
        num_leaves=64,
        min_child_samples=100,
    )

    assert model.get_params()["num_leaves"] == 64
    assert model.get_params()["min_child_samples"] == 100


def test_create_classifier_azoth_cuda_device() -> None:
    model = create_classifier(
        n_benign=100,
        n_malware=50,
        learner="azoth",
        device="cuda",
        n_estimators=5,
    )

    assert model.get_params()["device_type"] == "cuda"


def test_predict_proba_shape() -> None:
    model = create_classifier(n_benign=50, n_malware=50, n_estimators=10, device="cpu")
    rng = np.random.default_rng(42)
    X_train = rng.standard_normal((100, 10)).astype(np.float32)
    y_train = np.array([0] * 50 + [1] * 50, dtype=np.float32)
    model.set_params(early_stopping_rounds=None)
    model.fit(X_train, y_train, verbose=False)

    X_test = rng.standard_normal((5, 10)).astype(np.float32)
    probs = predict_proba(model, X_test)
    assert probs.shape == (5,)
    assert all(0.0 <= p <= 1.0 for p in probs)


def test_predict_proba_deterministic() -> None:
    model = create_classifier(n_benign=50, n_malware=50, n_estimators=10, device="cpu")
    rng = np.random.default_rng(42)
    X_train = rng.standard_normal((100, 10)).astype(np.float32)
    y_train = np.array([0] * 50 + [1] * 50, dtype=np.float32)
    model.set_params(early_stopping_rounds=None)
    model.fit(X_train, y_train, verbose=False)

    X_test = rng.standard_normal((3, 10)).astype(np.float32)
    probs1 = predict_proba(model, X_test)
    probs2 = predict_proba(model, X_test)
    np.testing.assert_array_equal(probs1, probs2)
