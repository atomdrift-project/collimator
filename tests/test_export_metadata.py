"""Tests for evaluation artifact metadata."""

from __future__ import annotations

import json

from collimator.export import save_evaluation


def test_save_evaluation_includes_split_summary_and_environment(tmp_path) -> None:
    output = tmp_path / "evaluation.json"
    save_evaluation(
        metrics={"roc_auc": 0.9, "avg_precision": 0.8, "brier": 0.1},
        calibration={"ece": 0.02, "bins": []},
        optimal_threshold=0.42,
        confusion=[[5, 1], [2, 7]],
        class_distribution={"benign": 6, "malware": 9},
        split_summary={
            "policy": "train/calibration/evaluation",
            "train_samples": 100,
            "calibration_samples": 10,
            "evaluation_samples": 10,
        },
        fold_metrics=[],
        n_features=123,
        model_abi_version=14,
        experiment={
            "seed": 42,
            "feature_spec_version": 13,
            "model_abi_version": 14,
            "workers": 1,
            "git_sha": None,
        },
        output_path=output,
        model_name="litmus-xg",
    )

    data = json.loads(output.read_text())
    assert data["split_summary"]["policy"] == "train/calibration/evaluation"
    assert data["model_abi_version"] == 14
    assert data["model_name"] == "litmus-xg"
    assert data["experiment"]["seed"] == 42
    assert data["experiment"]["model_abi_version"] == 14
    assert data["calibration"]["ece"] == 0.02
    assert "python" in data["environment"]
    assert "xgboost" in data["environment"]
    assert "numpy" in data["environment"]
