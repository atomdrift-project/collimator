"""Tests for ONNX export/inference helpers."""

from __future__ import annotations

import numpy as np

from collimator.export import predict_onnx_proba


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
