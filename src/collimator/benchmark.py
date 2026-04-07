"""Simple performance benchmarks for the training pipeline."""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from . import data, features, train
from .model import load_model, predict_proba


def _rate(n: int, seconds: float) -> float:
    return n / max(seconds, 1e-9)


def run_benchmark(
    db_path: Path | str,
    *,
    n_workers: int = 1,
    model_path: Path | None = None,
    spec_path: Path | None = None,
    output_path: Path | None = None,
) -> dict[str, float | int]:
    """Benchmark feature extraction, training, and inference throughput."""
    print("\nBENCHMARK")
    print("=" * 60)

    # Partition samples into train/test.
    train_row_ids, train_ids_labels, test_ids_labels = data.partition_row_ids(db_path)

    t0 = time.perf_counter()
    if model_path is not None and spec_path is not None and model_path.exists() and spec_path.exists():
        spec = features.FeatureSpec.load(spec_path)
        model = load_model(model_path)
        vocab_secs = 0.0
        train_secs = 0.0
        train_samples = None

        t_ext = time.perf_counter()
        _, _, X_test, y_test = features.extract_partitioned_from_db(
            db_path, [], test_ids_labels, spec, n_workers=n_workers,
        )
        extract_test_secs = time.perf_counter() - t_ext
        extract_train_secs = 0.0
    else:
        spec = features.build_vocab_from_db(db_path, train_ids_labels, n_workers=n_workers)
        vocab_secs = time.perf_counter() - t0

        t1 = time.perf_counter()
        X_train, y_train, X_test, y_test = features.extract_partitioned_from_db(
            db_path, train_ids_labels, test_ids_labels, spec, n_workers=n_workers,
        )
        extract_train_secs = time.perf_counter() - t1

        t2 = time.perf_counter()
        result = train.train(
            X_train,
            y_train,
            train.TrainConfig(n_estimators=200, early_stopping_rounds=20),
            feature_names=spec.feature_names,
        )
        train_secs = time.perf_counter() - t2
        model = result.model
        train_samples = X_train.shape[0]
        print(f"train extract: {extract_train_secs:8.3f}s  {_rate(X_train.shape[0], extract_train_secs):10.1f} rows/s")
        extract_test_secs = 0.0

    t4 = time.perf_counter()
    probs = predict_proba(model, X_test)
    infer_secs = time.perf_counter() - t4

    print(f"vocab build:    {vocab_secs:8.3f}s")
    if train_samples is not None:
        print(f"model train:    {train_secs:8.3f}s  {_rate(train_samples, train_secs):10.1f} train rows/s")
    print(f"test extract:   {extract_test_secs:8.3f}s  {_rate(X_test.shape[0], extract_test_secs):10.1f} rows/s")
    print(f"inference:      {infer_secs:8.3f}s  {_rate(len(probs), infer_secs):10.1f} rows/s")
    print(f"test samples:   {len(y_test):8d}")
    print(f"features:       {spec.total_features:8d}")
    print(f"mean prob:      {float(np.mean(probs)) if len(probs) else 0.0:8.4f}")
    summary: dict[str, float | int] = {
        "workers": n_workers,
        "vocab_seconds": vocab_secs,
        "train_seconds": train_secs,
        "test_extract_seconds": extract_test_secs,
        "inference_seconds": infer_secs,
        "train_rows": int(train_samples or 0),
        "test_rows": int(len(y_test)),
        "n_features": int(spec.total_features),
        "train_rows_per_second": _rate(int(train_samples or 0), train_secs) if train_samples is not None else 0.0,
        "test_rows_per_second": _rate(X_test.shape[0], extract_test_secs),
        "inference_rows_per_second": _rate(len(probs), infer_secs),
        "mean_probability": float(np.mean(probs)) if len(probs) else 0.0,
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)
    return summary
