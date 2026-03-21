"""Fast, deterministic subsampled experiments for feature/model iteration."""

from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from . import data, export, features, train
from .model import predict_proba


@dataclass(frozen=True, slots=True)
class ExperimentSample:
    """One sampled report retained for a fast experiment."""

    raw_report: str
    label: int
    is_test: bool
    group_id: str


@dataclass(frozen=True, slots=True)
class ExperimentCorpus:
    """Deterministic train/test subsets used for a fast experiment."""

    train_samples: list[ExperimentSample]
    test_samples: list[ExperimentSample]


def _reservoir_update(
    bucket: list[ExperimentSample],
    sample: ExperimentSample,
    limit: int,
    seen: int,
    rng: np.random.Generator,
) -> int:
    """Add one sample to a bounded reservoir."""
    if limit <= 0:
        return seen
    seen += 1
    if len(bucket) < limit:
        bucket.append(sample)
        return seen
    j = int(rng.integers(seen))
    if j < limit:
        bucket[j] = sample
    return seen


def sample_partitioned_reports(
    db_path: Path,
    *,
    train_samples: int,
    seed: int = 42,
) -> ExperimentCorpus:
    """Reservoir-sample train rows and keep the full external test bucket."""
    rng = np.random.default_rng(seed)

    train_malware_target = max(train_samples // 2, 1) if train_samples > 1 else train_samples
    train_benign_target = max(train_samples - train_malware_target, 0)

    train_malware: list[ExperimentSample] = []
    train_benign: list[ExperimentSample] = []
    test_malware: list[ExperimentSample] = []
    test_benign: list[ExperimentSample] = []
    seen = {
        (False, 1): 0,
        (False, 0): 0,
        (True, 1): 0,
        (True, 0): 0,
    }

    for raw_report, label, is_test, group_id in data.stream_partitioned_raw_reports_grouped(db_path):
        sample = ExperimentSample(raw_report=raw_report, label=label, is_test=is_test, group_id=group_id)
        key = (is_test, label)
        if key == (False, 1):
            seen[key] = _reservoir_update(train_malware, sample, train_malware_target, seen[key], rng)
        elif key == (False, 0):
            seen[key] = _reservoir_update(train_benign, sample, train_benign_target, seen[key], rng)
        elif key == (True, 1):
            test_malware.append(sample)
        else:
            test_benign.append(sample)

    return ExperimentCorpus(
        train_samples=train_benign + train_malware,
        test_samples=test_benign + test_malware,
    )


def _print_dataset_summary(corpus: ExperimentCorpus) -> None:
    train_malware = sum(sample.label == 1 for sample in corpus.train_samples)
    test_malware = sum(sample.label == 1 for sample in corpus.test_samples)
    print("\nEXPERIMENT")
    print("=" * 60)
    print(
        f"Sampled train: {len(corpus.train_samples)} "
        f"({train_malware} malware, {len(corpus.train_samples) - train_malware} benign)"
    )
    print(
        f"Full external test: {len(corpus.test_samples)} "
        f"({test_malware} malware, {len(corpus.test_samples) - test_malware} benign)"
    )


def _print_test_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float,
) -> None:
    y_pred = (y_prob >= threshold).astype(int)
    print(f"\n{'FULL EXTERNAL TEST':=^60}")
    print(f"  Threshold: {threshold:.3f}")
    print(f"  Precision: {precision_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"  Recall:    {recall_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"  F1:        {f1_score(y_true, y_pred, zero_division=0):.4f}")
    if len(np.unique(y_true)) > 1:
        print(f"  ROC AUC:   {roc_auc_score(y_true, y_prob):.4f}")
        print(f"  Avg Prec:  {average_precision_score(y_true, y_prob):.4f}")
        print(f"  Brier:     {brier_score_loss(y_true, y_prob):.4f}")


def run_experiment(
    db_path: Path,
    *,
    output_dir: Path | None = None,
    n_workers: int = 0,
    seed: int = 42,
    train_samples: int = 10_000,
    n_folds: int = 2,
    n_estimators: int = 220,
    max_depth: int = 6,
    learning_rate: float = 0.03,
    early_stopping_rounds: int = 25,
) -> dict[str, object]:
    """Run a fast subsampled train cycle evaluated on the full external test bucket."""
    corpus = sample_partitioned_reports(
        db_path,
        train_samples=train_samples,
        seed=seed,
    )
    _print_dataset_summary(corpus)

    if len(corpus.train_samples) < 10:
        raise ValueError(f"only {len(corpus.train_samples)} sampled training rows, need at least 10")

    spec = features.build_vocab(
        (sample.raw_report for sample in corpus.train_samples),
        n_workers=n_workers,
    )

    X_train, y_train = features.extract_stream(
        ((sample.raw_report, sample.label) for sample in corpus.train_samples),
        spec,
        n_workers=n_workers,
    )
    X_test, y_test = features.extract_stream(
        ((sample.raw_report, sample.label) for sample in corpus.test_samples),
        spec,
        n_workers=n_workers,
    )

    result = train.train(
        X_train,
        y_train,
        train.TrainConfig(
            seed=seed,
            n_folds=n_folds,
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            early_stopping_rounds=early_stopping_rounds,
        ),
        feature_names=spec.feature_names,
        groups=np.array([sample.group_id for sample in corpus.train_samples], dtype=object),
    )

    sampled_test_metrics: dict[str, float] = {}
    if X_test.shape[0] > 0:
        probs = predict_proba(result.model, X_test)
        _print_test_metrics(y_test, probs, result.optimal_threshold)
        y_pred = (probs >= result.optimal_threshold).astype(int)
        sampled_test_metrics = {
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, probs)) if len(np.unique(y_test)) > 1 else 0.0,
            "avg_precision": (
                float(average_precision_score(y_test, probs)) if len(np.unique(y_test)) > 1 else 0.0
            ),
            "brier": float(brier_score_loss(y_test, probs)) if len(np.unique(y_test)) > 1 else 0.0,
        }
    else:
        print("\nNo external test rows available.")

    results = {
        "train_rows": int(X_train.shape[0]),
        "test_rows": int(X_test.shape[0]),
        "n_features": int(spec.total_features),
        "train_metrics": result.metrics,
        "sampled_test_metrics": sampled_test_metrics,
        "threshold": float(result.optimal_threshold),
        "split_summary": result.split_summary,
        "db_path": str(db_path),
        "seed": int(seed),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    if output_dir is not None:
        export.save_run_summary(kind="experiment", payload=results, output_dir=output_dir)
    return results
