"""Tests for ONNX export/inference helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from collimator.export import (
    is_constant_predictor,
    predict_onnx_proba,
    route_model_is_degenerate,
)


class _FakeOutput:
    def __init__(self, name: str) -> None:
        self.name = name


class _FakeSession:
    def __init__(self, outputs: list[str], results: list[object]) -> None:
        self._outputs = [_FakeOutput(name) for name in outputs]
        self._results = results

    def get_outputs(self) -> list[_FakeOutput]:
        return self._outputs

    def run(self, _unused: object, feed: dict[str, np.ndarray]) -> list[object]:
        assert "features" in feed
        return self._results


def test_predict_onnx_proba_prefers_named_probability_output() -> None:
    X = np.zeros((2, 3), dtype=np.float32)
    session = _FakeSession(
        ["label", "probabilities"],
        [
            np.array([0, 1], dtype=np.int64),
            [{0: 0.8, 1: 0.2}, {0: 0.1, 1: 0.9}],
        ],
    )

    probs = predict_onnx_proba(session, X)
    np.testing.assert_allclose(probs, np.array([0.2, 0.9], dtype=np.float32))


def test_predict_onnx_proba_handles_probability_matrix() -> None:
    X = np.zeros((2, 3), dtype=np.float32)
    session = _FakeSession(
        ["output_probability"],
        [np.array([[0.7, 0.3], [0.2, 0.8]], dtype=np.float32)],
    )

    probs = predict_onnx_proba(session, X)
    np.testing.assert_allclose(probs, np.array([0.3, 0.8], dtype=np.float32))


class _FakeBooster:
    def __init__(self, leaf_counts: list[int]) -> None:
        self._leaf_counts = leaf_counts

    def dump_model(self) -> dict[str, object]:
        return {"tree_info": [{"num_leaves": n} for n in self._leaf_counts]}


class _FakeClassifier:
    """sklearn-style wrapper exposing the trained Booster as ``booster_``."""

    def __init__(self, leaf_counts: list[int]) -> None:
        self.booster_ = _FakeBooster(leaf_counts)


def test_is_constant_predictor_true_when_every_tree_has_one_leaf() -> None:
    assert is_constant_predictor(_FakeBooster([1, 1, 1])) is True
    # Also accepts the sklearn wrapper, not just the raw Booster.
    assert is_constant_predictor(_FakeClassifier([1, 1])) is True


def test_is_constant_predictor_false_when_any_tree_splits() -> None:
    assert is_constant_predictor(_FakeBooster([1, 5, 3])) is False


def test_is_constant_predictor_false_on_empty_or_unknown_model() -> None:
    # No trees, or an object that can't be introspected → not constant
    # (safe default: don't suppress a model we can't reason about).
    assert is_constant_predictor(_FakeBooster([])) is False
    assert is_constant_predictor(object()) is False


def _write_lgb_route(route_dir: Path, *, constant: bool) -> None:
    """Train a tiny real LightGBM model into ``route_dir/model.txt``. With
    ``constant=True`` an impossible min-samples-per-leaf forces every tree to a
    single leaf (a genuine constant predictor); otherwise the model splits."""
    import lightgbm as lgb
    import numpy as np

    rng = np.random.default_rng(0)
    x = rng.random((60, 4)).astype(np.float32)
    # Learnable signal so the non-constant model actually splits.
    y = (x[:, 0] > 0.5).astype(np.int32)
    params = {"n_estimators": 3, "num_leaves": 4, "verbose": -1}
    if constant:
        params["min_child_samples"] = 10**6  # no split ever has enough samples
    clf = lgb.LGBMClassifier(**params).fit(x, y)
    route_dir.mkdir(parents=True, exist_ok=True)
    clf.booster_.save_model(str(route_dir / "model.txt"))


def test_route_model_is_degenerate_true_for_constant_txt_route(tmp_path: Path) -> None:
    route = tmp_path / "filetypes" / "xlsx"
    _write_lgb_route(route, constant=True)
    assert route_model_is_degenerate(route) is True


def test_route_model_is_degenerate_false_for_model_that_splits(tmp_path: Path) -> None:
    route = tmp_path / "filetypes" / "elf"
    _write_lgb_route(route, constant=False)
    assert route_model_is_degenerate(route) is False


def test_route_model_is_degenerate_false_when_onnx_present(tmp_path: Path) -> None:
    # An .onnx artifact means ONNX export succeeded, which only happens for
    # models that learned a split — so the route is healthy by construction,
    # without loading anything.
    route = tmp_path / "filetypes" / "pe"
    route.mkdir(parents=True)
    (route / "model.onnx").write_bytes(b"")
    assert route_model_is_degenerate(route) is False


def test_route_model_is_degenerate_false_when_no_model(tmp_path: Path) -> None:
    route = tmp_path / "filetypes" / "empty"
    route.mkdir(parents=True)
    assert route_model_is_degenerate(route) is False
