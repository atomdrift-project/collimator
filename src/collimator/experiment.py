"""Fast, deterministic subsampled experiments for feature/model iteration."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

import numpy as np

log = logging.getLogger(__name__)
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

    row_id: int
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
    db_path: Path | str,
    *,
    train_samples: int,
    max_test_samples: int = 0,
    seed: int = 42,
) -> ExperimentCorpus:
    """Reservoir-sample train rows and optionally cap the external test bucket.

    max_test_samples=0 keeps the full test set (original behaviour).
    Set it to a positive value to reservoir-sample the test set too,
    which substantially reduces peak memory when the test bucket is large.
    """
    rng = np.random.default_rng(seed)

    train_malware_target = max(train_samples // 2, 1) if train_samples > 1 else train_samples
    train_benign_target = max(train_samples - train_malware_target, 0)

    test_malware_target = max(max_test_samples // 2, 1) if max_test_samples > 1 else max_test_samples
    test_benign_target = max(max_test_samples - test_malware_target, 0) if max_test_samples > 0 else 0

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

    for row_id, label, is_test, group_id in data.stream_partitioned_metadata_grouped(db_path):
        sample = ExperimentSample(row_id=row_id, label=label, is_test=is_test, group_id=group_id)
        key = (is_test, label)
        if key == (False, 1):
            seen[key] = _reservoir_update(train_malware, sample, train_malware_target, seen[key], rng)
        elif key == (False, 0):
            seen[key] = _reservoir_update(train_benign, sample, train_benign_target, seen[key], rng)
        elif key == (True, 1):
            if max_test_samples > 0:
                seen[key] = _reservoir_update(test_malware, sample, test_malware_target, seen[key], rng)
            else:
                test_malware.append(sample)
                seen[key] += 1
        else:
            if max_test_samples > 0:
                seen[key] = _reservoir_update(test_benign, sample, test_benign_target, seen[key], rng)
            else:
                test_benign.append(sample)
                seen[key] += 1

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


def _load_primary_file_types(db_path: Path | str, row_ids: list[int]) -> np.ndarray:
    file_types_by_row: dict[int, str] = {}
    chunk_size = 1000
    for start in range(0, len(row_ids), chunk_size):
        chunk = row_ids[start:start + chunk_size]
        for row_id, cleave_result in data.fetch_cleave_results(db_path, chunk).items():
            file_type = "unknown"
            try:
                report = json.loads(cleave_result)
                file_type = str(features.primary_file(report).get("type") or "unknown")
            except json.JSONDecodeError:
                pass
            file_types_by_row[row_id] = file_type

    return np.asarray([file_types_by_row.get(row_id, "unknown") for row_id in row_ids], dtype=object)


def run_experiment(
    db_path: Path | str,
    *,
    output_dir: Path | None = None,
    n_workers: int = 0,
    seed: int = 42,
    train_samples: int = 10_000,
    max_test_samples: int = 0,
    n_folds: int = 2,
    n_estimators: int = 220,
    max_depth: int = 6,
    learning_rate: float = 0.03,
    early_stopping_rounds: int = 25,
    min_child_weight: int = 5,
    colsample_bytree: float = 0.8,
    subsample: float = 0.8,
    gamma: float = 0.0,
    reg_alpha: float = 0.0,
    reg_lambda: float = 1.0,
    beta: float = 1.0,
    threshold_mode: str = "fbeta",
    threshold_fpr_target: float | None = None,
    hard_negative_fraction: float = 0.0,
    hard_negative_weight: float = 1.0,
    benign_filetype_weights: dict[str, float] | None = None,
) -> dict[str, object]:
    """Run a fast subsampled train cycle evaluated on the full external test bucket."""
    corpus = sample_partitioned_reports(
        db_path,
        train_samples=train_samples,
        max_test_samples=max_test_samples,
        seed=seed,
    )
    _print_dataset_summary(corpus)

    if len(corpus.train_samples) < 10:
        raise ValueError(f"only {len(corpus.train_samples)} sampled training rows, need at least 10")

    # Sort corpus to match DB extraction order (by row_id).
    sorted_train = sorted(corpus.train_samples, key=lambda s: s.row_id)
    sorted_test = sorted(corpus.test_samples, key=lambda s: s.row_id)
    train_file_types = _load_primary_file_types(db_path, [s.row_id for s in sorted_train])

    log.info("pass 1: building vocabulary (worker-local DB fetching)")
    spec = features.build_vocab_from_db(
        db_path,
        [s.row_id for s in sorted_train],
        n_workers=n_workers,
    )

    log.info("pass 2: extracting all features (worker-local DB fetching)")
    X_train, y_train, X_test, y_test = features.extract_partitioned_from_db(
        db_path,
        [(s.row_id, s.label) for s in sorted_train],
        [(s.row_id, s.label) for s in sorted_test],
        spec,
        n_workers=n_workers,
    )
    del corpus

    # Build monotonic constraints for all behavior features.
    # We want to force the model to treat 'presence', 'criticality', and 'aggregate counts'
    # of findings as purely additive signals for malware.
    # We use a tuple aligned by index because XGBoost cannot reliably match
    # feature names when training on sparse matrices.
    constraints = [0] * len(spec.feature_names)
    for i, name in enumerate(spec.feature_names):
        if name.startswith(("present:", "maxcrit:")):
            constraints[i] = 1
        elif name.startswith("agg:") and ("suspicious" in name or "hostile" in name or "findings_log" in name):
            constraints[i] = 1
        elif name == "struct:stealth_potential":
            constraints[i] = 1

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
            min_child_weight=min_child_weight,
            colsample_bytree=colsample_bytree,
            subsample=subsample,
            gamma=gamma,
            reg_alpha=reg_alpha,
            reg_lambda=reg_lambda,
            beta=beta,
            threshold_mode=threshold_mode,
            threshold_fpr_target=threshold_fpr_target,
            hard_negative_fraction=hard_negative_fraction,
            hard_negative_weight=hard_negative_weight,
            benign_filetype_weights=benign_filetype_weights or {},
            monotone_constraints=tuple(constraints),
            holdout_fraction=0.0,  # use all samples; CV predictions drive threshold
        ),
        feature_names=spec.feature_names,
        sample_file_types=train_file_types,
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
        spec.save(output_dir / "feature_spec.json")
        export.save_model(result.model, output_dir / "model.json")
        export.save_run_summary(kind="experiment", payload=results, output_dir=output_dir)
    return results
