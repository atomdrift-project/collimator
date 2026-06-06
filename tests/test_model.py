"""Tests for XGBoost model creation and prediction."""

from unittest import mock

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from collimator import model as model_mod
from collimator.model import _shape_args, create_classifier, pick_device, predict_proba


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
    from collimator.model import detect_lightgbm_cuda

    model = create_classifier(
        n_benign=100,
        n_malware=50,
        learner="azoth",
        device="cuda",
        n_estimators=5,
    )

    params = model.get_params()
    if detect_lightgbm_cuda():
        # CUDA-built LightGBM: the request is honored.
        assert params["device_type"] == "cuda"
    else:
        # CPU-only LightGBM (e.g. XGBoost has CUDA but LightGBM doesn't):
        # must fall back to CPU rather than abort at fit time.
        assert params.get("device_type") in (None, "cpu")


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


@pytest.fixture
def _force_cuda_available(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make pick_device behave as if CUDA hardware is present, so the shape
    heuristic gets exercised regardless of where the tests run."""
    monkeypatch.setattr(model_mod, "detect_device", lambda: "cuda:0")


def test_pick_device_falls_back_to_cpu_without_cuda(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(model_mod, "detect_device", lambda: "cpu")
    assert pick_device(1_000_000, 100, 100_000_000) == "cpu"


def test_pick_device_no_shape_is_cpu(_force_cuda_available: None) -> None:
    assert pick_device() == "cpu"


def test_pick_device_sparse_is_cpu(_force_cuda_available: None) -> None:
    # macho-shaped: 6k rows × 45k features @ 0.4% density.
    assert pick_device(6_374, 45_503, 1_080_000) == "cpu"


def test_pick_device_small_n_is_cpu(_force_cuda_available: None) -> None:
    assert pick_device(1_000, 100, 100_000) == "cpu"


def test_pick_device_wide_features_is_cpu(_force_cuda_available: None) -> None:
    assert pick_device(100_000, 50_000, 5_000_000_000) == "cpu"


def test_pick_device_large_dense_is_cuda(_force_cuda_available: None) -> None:
    # 100k rows, 5k features, 20% density: every gate passes.
    assert pick_device(100_000, 5_000, 100_000_000) == "cuda"


def test_shape_args_sparse() -> None:
    X = csr_matrix(np.array([[0, 1, 0], [1, 0, 0], [0, 0, 1]], dtype=np.float32))
    assert _shape_args(X) == {"n_rows": 3, "n_features": 3, "nnz": 3}


def test_shape_args_dense() -> None:
    X = np.zeros((4, 7), dtype=np.float32)
    assert _shape_args(X) == {"n_rows": 4, "n_features": 7, "nnz": None}


def test_create_classifier_auto_routes_through_pick_device() -> None:
    """device='auto' must invoke pick_device; sparse high-dim shape -> cpu."""
    with mock.patch.object(model_mod, "pick_device", return_value="cpu") as picker:
        model = create_classifier(
            n_benign=100,
            n_malware=50,
            learner="azoth",
            device="auto",
            n_rows=6_374,
            n_features=45_503,
            nnz=1_080_000,
            n_estimators=5,
        )
    picker.assert_called_once_with(6_374, 45_503, 1_080_000)
    # CPU result -> no device_type set on the LightGBM estimator.
    assert "device_type" not in model.get_params() or model.get_params().get("device_type") is None


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
