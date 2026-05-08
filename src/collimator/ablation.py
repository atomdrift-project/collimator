"""Feature-group ablation utilities."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from . import data, experiment, features, train
from .model import predict_proba


def _drop_groups(
    X: sp.csr_matrix,
    spec: features.FeatureSpec,
    groups: list[str],
) -> tuple[sp.csr_matrix, list[str]]:
    group_indices = features.feature_group_indices(spec)
    drop_cols = {idx for group in groups for idx in group_indices.get(group, [])}
    keep_cols = [i for i in range(X.shape[1]) if i not in drop_cols]
    X_kept = X[:, keep_cols]
    kept_names = [spec.feature_names[i] for i in keep_cols]
    return X_kept, kept_names


def _test_metrics(
    model: object,
    X_test: sp.csr_matrix,
    y_test: np.ndarray,
    threshold: float,
) -> dict[str, float]:
    """Evaluate a trained model against a held-out test set at a given threshold."""
    if X_test.shape[0] == 0 or len(y_test) == 0:
        return {
            "test_n": 0,
            "test_f1": 0.0,
            "test_precision": 0.0,
            "test_recall": 0.0,
            "test_tp": 0,
            "test_fp": 0,
            "test_fn": 0,
            "test_tn": 0,
        }
    probs = predict_proba(model, X_test)
    y_pred = (probs >= threshold).astype(int)
    y_true = y_test.astype(int)
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    fp = int(((y_pred == 1) & (y_true == 0)).sum())
    fn = int(((y_pred == 0) & (y_true == 1)).sum())
    tn = int(((y_pred == 0) & (y_true == 0)).sum())
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return {
        "test_n": int(len(y_true)),
        "test_f1": float(f1),
        "test_precision": float(precision),
        "test_recall": float(recall),
        "test_tp": tp,
        "test_fp": fp,
        "test_fn": fn,
        "test_tn": tn,
    }


def _load_ablation(output_path: Path | None) -> list[dict[str, object]]:
    """Load previously saved ablation rows for resumable long runs."""
    if output_path is None or not output_path.exists():
        return []
    with open(output_path) as f:
        rows = json.load(f)
    if not isinstance(rows, list):
        raise ValueError(f"invalid ablation output {output_path}: expected JSON list")
    return [row for row in rows if isinstance(row, dict)]


def run_ablation(
    db_path: Path | str,
    *,
    n_workers: int = 1,
    seed: int = 42,
    groups: list[str] | None = None,
    min_malware_training_score: int = 0,
    n_estimators: int | None = None,
    max_depth: int | None = None,
    learning_rate: float | None = None,
    early_stopping_rounds: int | None = None,
    beta: float | None = None,
    device: str | None = None,
    learner: str = "litmus-xg",
    model_name: str = "litmus-xg",
    n_folds: int | None = None,
    train_samples: int = 0,
    max_test_samples: int = 0,
    cache_dir: Path | None = None,
    max_id: int = 0,
    output_path: Path | None = None,
) -> list[dict[str, object]]:
    """Train baseline and leave-one-group-out ablations on the same dataset.

    Evaluates each ablation on both CV and the held-out is_test partition
    so we see how each group affects the user-visible operating point
    (not just in-CV F1). Hyperparameters default to the layered v16
    baseline if not overridden.

    If train_samples > 0, reservoir-samples the training data to that size
    (balanced malware/benign). If max_test_samples > 0, caps test data.
    """
    pinned_max_id = int(max_id) if max_id > 0 else data.snapshot_max_id(db_path)
    feature_cfg = features.feature_config_from_env()
    feature_env = experiment._collimator_env()  # noqa: SLF001
    corpus_hash = (
        experiment._corpus_cache_key(  # noqa: SLF001
            seed,
            train_samples,
            max_test_samples,
            min_malware_training_score,
            pinned_max_id,
            "general",
            (),
            0,
        )
        if cache_dir
        else ""
    )
    matrix_hash = experiment._matrix_cache_key(corpus_hash, feature_cfg, feature_env) if cache_dir else ""  # noqa: SLF001
    cached_matrices = experiment._load_matrix_cache(cache_dir, matrix_hash) if cache_dir else None  # noqa: SLF001
    if cached_matrices is not None:
        spec, X_train, y_train, X_test, y_test, _train_file_types = cached_matrices
        print(f"\nABLATION (cached matrices: {X_train.shape[0]} train, {X_test.shape[0]} test)")
    else:
        cached_corpus = experiment._load_corpus_cache(cache_dir, corpus_hash) if cache_dir else None  # noqa: SLF001
        if cached_corpus is not None:
            corpus, train_file_types = cached_corpus
        else:
            corpus = experiment.sample_partitioned_reports(
                db_path,
                train_samples=train_samples,
                max_test_samples=max_test_samples,
                seed=seed,
                min_malware_training_score=min_malware_training_score,
                max_id=pinned_max_id,
            )
            sorted_train = sorted(corpus.train_samples, key=lambda s: s.row_id)
            train_file_types = experiment._load_primary_file_types(  # noqa: SLF001
                db_path, [s.row_id for s in sorted_train],
            )
            if cache_dir:
                experiment._save_corpus_cache(cache_dir, corpus_hash, corpus, train_file_types)  # noqa: SLF001

        train_ids_labels = [(s.row_id, s.label) for s in sorted(corpus.train_samples, key=lambda s: s.row_id)]
        test_ids_labels = [(s.row_id, s.label) for s in sorted(corpus.test_samples, key=lambda s: s.row_id)]
        spec = features.build_vocab_from_db(db_path, train_ids_labels, n_workers=n_workers)
        X_train, y_train, X_test, y_test = features.extract_partitioned_from_db(
            db_path, train_ids_labels, test_ids_labels, spec, n_workers=n_workers,
        )
        if cache_dir:
            experiment._save_matrix_cache(  # noqa: SLF001
                cache_dir, matrix_hash, spec, X_train, y_train, X_test, y_test, train_file_types,
            )
    group_indices = features.feature_group_indices(spec)
    if groups is not None:
        group_names = [group for group in groups if group_indices.get(group)]
        skipped = [group for group in groups if not group_indices.get(group)]
        if skipped:
            print(f"Skipping empty/unknown groups: {', '.join(skipped)}")
    else:
        group_names = [
            group for group, indices in group_indices.items() if indices
        ]

    # Build a TrainConfig honoring the caller's overrides, defaulting to
    # train.TrainConfig defaults. For comparable numbers across runs, pass
    # explicit overrides matching the deployed model's hyperparameters.
    cfg_kwargs: dict[str, object] = {"seed": seed, "learner": learner}
    if device is not None:
        cfg_kwargs["device"] = device
    if n_estimators is not None:
        cfg_kwargs["n_estimators"] = n_estimators
    if max_depth is not None:
        cfg_kwargs["max_depth"] = max_depth
    if learning_rate is not None:
        cfg_kwargs["learning_rate"] = learning_rate
    if early_stopping_rounds is not None:
        cfg_kwargs["early_stopping_rounds"] = early_stopping_rounds
    if beta is not None:
        cfg_kwargs["beta"] = beta
    if n_folds is not None:
        cfg_kwargs["n_folds"] = n_folds
    base_cfg = train.TrainConfig(**cfg_kwargs)  # type: ignore[arg-type]

    rows = _load_ablation(output_path)
    completed = {
        str(row.get("ablation"))
        for row in rows
        if row.get("ablation") is not None
    }
    if completed:
        print(f"Resuming ablation from {output_path}: {len(completed)} completed rows")

    def _run_one(label: str, dropped: list[str], X: sp.csr_matrix, names: list[str]) -> None:
        if label in completed:
            print(f"Skipping completed ablation: {label}")
            return
        result = train.train(X, y_train, base_cfg, feature_names=names)
        # Drop the same columns from the test matrix.
        if dropped:
            X_test_dropped, _ = _drop_groups(X_test, spec, dropped)
        else:
            X_test_dropped = X_test
        test_metrics = _test_metrics(
            result.model, X_test_dropped, y_test, result.optimal_threshold,
        )
        rows.append({
            "ablation": label,
            "model_name": model_name,
            "learner": learner,
            "device": device or "auto",
            "dropped_groups": dropped,
            "n_features": X.shape[1],
            "optimal_threshold": float(result.optimal_threshold),
            "cv_metrics": result.metrics,
            "test_metrics": test_metrics,
            "split_summary": result.split_summary,
        })
        completed.add(label)
        if output_path is not None:
            save_ablation(rows, output_path)

    _run_one("baseline", [], X_train, spec.feature_names)
    for group in group_names:
        X_drop, feature_names = _drop_groups(X_train, spec, [group])
        _run_one(f"drop:{group}", [group], X_drop, feature_names)

    return rows


def print_ablation(rows: list[dict[str, object]]) -> None:
    """Print a compact ablation table with CV + test metrics + FP/FN counts."""
    print("\nABLATION")
    print("=" * 110)
    print(
        f"{'Run':<22} {'nFeat':>7} {'thresh':>7} "
        f"{'cv_F1':>7} {'cv_AUC':>7} "
        f"{'tF1':>7} {'tPrec':>7} {'tRec':>7} {'tFP':>6} {'tFN':>5}"
    )
    print("-" * 110)
    for row in rows:
        cv = row["cv_metrics"]
        t = row["test_metrics"]
        assert isinstance(cv, dict) and isinstance(t, dict)
        print(
            f"{str(row['ablation']):<22} "
            f"{int(row['n_features']):>7} "
            f"{float(row.get('optimal_threshold', 0.5)):>7.3f} "
            f"{float(cv.get('f1', 0.0)):>7.4f} "
            f"{float(cv.get('roc_auc', 0.0)):>7.4f} "
            f"{float(t.get('test_f1', 0.0)):>7.4f} "
            f"{float(t.get('test_precision', 0.0)):>7.4f} "
            f"{float(t.get('test_recall', 0.0)):>7.4f} "
            f"{int(t.get('test_fp', 0)):>6d} "
            f"{int(t.get('test_fn', 0)):>5d}"
        )


def save_ablation(rows: list[dict[str, object]], output_path: Path) -> None:
    """Save ablation results as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(f"{output_path.suffix}.tmp")
    with open(tmp_path, "w") as f:
        json.dump(rows, f, indent=2)
    tmp_path.replace(output_path)
