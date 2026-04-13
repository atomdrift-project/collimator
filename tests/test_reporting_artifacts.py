"""Tests for benchmark and ablation reporting artifacts."""

from __future__ import annotations

import json

from collimator.ablation import save_ablation
from collimator.benchmark import run_benchmark


def test_save_ablation_writes_json(tmp_path) -> None:
    output = tmp_path / "ablation.json"
    rows = [{"ablation": "baseline", "metrics": {"roc_auc": 0.9}, "n_features": 10}]
    save_ablation(rows, output)
    assert json.loads(output.read_text())[0]["ablation"] == "baseline"


def test_benchmark_can_write_json(tmp_path, monkeypatch) -> None:
    output = tmp_path / "benchmark.json"

    class _Spec:
        total_features = 5
        feature_names = [f"f{i}" for i in range(5)]

    def _extract_partitioned(*args, **kwargs):
        import numpy as np
        import scipy.sparse as sp
        X = sp.csr_matrix([[1, 0, 0, 1, 0]], dtype=np.float32)
        y = np.array([1], dtype=np.float32)
        return X, y, X, y

    class _Model:
        pass

    monkeypatch.setattr("collimator.benchmark.features.build_vocab_from_db", lambda *args, **kwargs: _Spec())
    monkeypatch.setattr("collimator.benchmark.features.extract_partitioned_from_db", _extract_partitioned)
    monkeypatch.setattr("collimator.benchmark.train.train", lambda *args, **kwargs: type("R", (), {"model": _Model()})())
    monkeypatch.setattr("collimator.benchmark.predict_proba", lambda model, X: [0.75] * X.shape[0])
    monkeypatch.setattr(
        "collimator.benchmark.data.stream_partitioned_metadata_grouped",
        lambda *args, **kwargs: iter([(1, 1, False, "aa" * 32, 10)]),
    )

    summary = run_benchmark(tmp_path / "dummy.db", output_path=output)
    data = json.loads(output.read_text())
    assert data["n_features"] == 5
    assert summary["n_features"] == 5
