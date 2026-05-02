"""Fast, deterministic subsampled experiments for feature/model iteration."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import scipy.sparse as sp

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


# ---------------------------------------------------------------------------
# Experiment data cache
# ---------------------------------------------------------------------------
# Two-level cache stored under --cache-dir:
#
# Level 1 — Row selections (corpus_<hash>.json):
#   Keyed by (seed, train_samples, max_test_samples, min_malware_training_score,
#   max_id, MIN_SAMPLE_SCORE).  Saves the sampled row IDs + labels so the
#   expensive full-table metadata scan (≈1m45s for 10K) is done once.
#
# Level 2 — Extracted matrices (matrix_<hash>.npz + spec):
#   Keyed by corpus hash + FeatureConfig (env-driven).  Saves X_train, y_train,
#   X_test, y_test, FeatureSpec.  When only XGBoost hyperparams change, the
#   entire data pipeline is skipped.
#
# When n-gram config changes, level 2 misses but level 1 still hits — saving
# the metadata scan while re-running vocab + extraction.


def _corpus_cache_key(
    seed: int,
    train_samples: int,
    max_test_samples: int,
    min_malware_training_score: int,
    max_id: int,
) -> str:
    """Deterministic hash for the row-selection parameters."""
    blob = json.dumps({
        "seed": seed,
        "train_samples": train_samples,
        "max_test_samples": max_test_samples,
        "min_malware_training_score": min_malware_training_score,
        "max_id": max_id,
        "min_sample_score": data.MIN_SAMPLE_SCORE,
    }, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def _matrix_cache_key(corpus_hash: str, feature_cfg: features.FeatureConfig) -> str:
    """Deterministic hash for corpus + feature configuration."""
    # FeatureConfig is a frozen dataclass so we can iterate its fields.
    cfg_dict = {f.name: getattr(feature_cfg, f.name) for f in feature_cfg.__dataclass_fields__.values()}
    # frozenset isn't JSON-serializable; convert to sorted list.
    cfg_dict["enabled_groups"] = sorted(cfg_dict["enabled_groups"])
    blob = json.dumps({"corpus": corpus_hash, "feature_config": cfg_dict}, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def _save_corpus_cache(
    cache_dir: Path,
    corpus_hash: str,
    corpus: "ExperimentCorpus",
    train_file_types: np.ndarray,
) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"corpus_{corpus_hash}.json"
    sorted_train = sorted(corpus.train_samples, key=lambda s: s.row_id)
    obj = {
        "train": [{"row_id": s.row_id, "label": s.label, "is_test": s.is_test,
                    "group_id": s.group_id, "score": s.score}
                   for s in corpus.train_samples],
        "test": [{"row_id": s.row_id, "label": s.label, "is_test": s.is_test,
                   "group_id": s.group_id, "score": s.score}
                  for s in corpus.test_samples],
        "train_file_types": [
            {"row_id": s.row_id, "file_type": ft}
            for s, ft in zip(sorted_train, train_file_types)
        ],
    }
    with open(path, "w") as f:
        json.dump(obj, f)
    log.info("cached corpus selections: %s", path)


def _load_corpus_cache(
    cache_dir: Path, corpus_hash: str,
) -> "tuple[ExperimentCorpus, np.ndarray] | None":
    path = cache_dir / f"corpus_{corpus_hash}.json"
    if not path.exists():
        return None
    with open(path) as f:
        obj = json.load(f)
    train = [ExperimentSample(**s) for s in obj["train"]]
    test = [ExperimentSample(**s) for s in obj["test"]]
    # Rebuild file_types array in sorted row_id order (matching how it's used).
    ft_entries = obj.get("train_file_types", [])
    if ft_entries:
        ft_by_id = {e["row_id"]: e["file_type"] for e in ft_entries}
        sorted_train = sorted(train, key=lambda s: s.row_id)
        file_types = np.asarray(
            [ft_by_id.get(s.row_id, "unknown") for s in sorted_train], dtype=object,
        )
    else:
        file_types = np.asarray([], dtype=object)
    log.info("loaded cached corpus: %d train, %d test from %s", len(train), len(test), path)
    return ExperimentCorpus(train_samples=train, test_samples=test), file_types


def _save_matrix_cache(
    cache_dir: Path,
    matrix_hash: str,
    spec: features.FeatureSpec,
    X_train: sp.csr_matrix,
    y_train: np.ndarray,
    X_test: sp.csr_matrix,
    y_test: np.ndarray,
    train_file_types: np.ndarray,
) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    npz_path = cache_dir / f"matrix_{matrix_hash}.npz"
    sp.save_npz(str(cache_dir / f"matrix_{matrix_hash}_Xtrain.npz"), X_train)
    sp.save_npz(str(cache_dir / f"matrix_{matrix_hash}_Xtest.npz"), X_test)
    np.savez_compressed(
        str(npz_path),
        y_train=y_train,
        y_test=y_test,
        train_file_types=train_file_types,
    )
    spec.save(cache_dir / f"matrix_{matrix_hash}_spec.json")
    log.info("cached matrices: %s (%d train, %d test, %d features)",
             npz_path, X_train.shape[0], X_test.shape[0], spec.total_features)


def _load_matrix_cache(
    cache_dir: Path,
    matrix_hash: str,
) -> "tuple[features.FeatureSpec, sp.csr_matrix, np.ndarray, sp.csr_matrix, np.ndarray, np.ndarray] | None":
    npz_path = cache_dir / f"matrix_{matrix_hash}.npz"
    spec_path = cache_dir / f"matrix_{matrix_hash}_spec.json"
    xtrain_path = cache_dir / f"matrix_{matrix_hash}_Xtrain.npz"
    xtest_path = cache_dir / f"matrix_{matrix_hash}_Xtest.npz"
    if not all(p.exists() for p in (npz_path, spec_path, xtrain_path, xtest_path)):
        return None
    spec = features.FeatureSpec.load(spec_path)
    X_train = sp.load_npz(str(xtrain_path))
    X_test = sp.load_npz(str(xtest_path))
    arrays = np.load(str(npz_path), allow_pickle=True)
    y_train = arrays["y_train"]
    y_test = arrays["y_test"]
    train_file_types = arrays["train_file_types"]
    log.info("loaded cached matrices: %d train, %d test, %d features",
             X_train.shape[0], X_test.shape[0], spec.total_features)
    return spec, X_train, y_train, X_test, y_test, train_file_types


@dataclass(frozen=True, slots=True)
class ExperimentSample:
    """One sampled report retained for a fast experiment."""

    row_id: int
    label: int
    is_test: bool
    group_id: str
    score: int


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
    total_limit: int = 0,
    min_malware_training_score: int = 0,
    max_id: int = 0,
) -> ExperimentCorpus:
    """Reservoir-sample train rows and optionally cap the external test bucket.

    If train_samples > 0, we reservoir-sample train rows to that target, 
    balancing malware/benign 50/50.
    If train_samples == 0, we take ALL non-test rows from the stream (natural distribution).

    If max_test_samples > 0, we reservoir-sample test rows to that target,
    balancing malware/benign 50/50.
    If max_test_samples == 0, we take ALL test rows from the stream (natural distribution).
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

    for row_id, label, is_test, group_id, score in data.stream_partitioned_metadata_grouped(db_path, limit=total_limit, max_id=max_id):
        sample = ExperimentSample(row_id=row_id, label=label, is_test=is_test, group_id=group_id, score=score)
        key = (is_test, label)
        
        if not is_test:
            # Heuristic pruning: skip malware with very low scores during training.
            if label == 1 and score < min_malware_training_score:
                continue

            if train_samples > 0:
                if label == 1:
                    seen[key] = _reservoir_update(train_malware, sample, train_malware_target, seen[key], rng)
                else:
                    seen[key] = _reservoir_update(train_benign, sample, train_benign_target, seen[key], rng)
            else:
                if label == 1:
                    train_malware.append(sample)
                else:
                    train_benign.append(sample)
                seen[key] += 1
        else:
            if max_test_samples > 0:
                if label == 1:
                    seen[key] = _reservoir_update(test_malware, sample, test_malware_target, seen[key], rng)
                else:
                    seen[key] = _reservoir_update(test_benign, sample, test_benign_target, seen[key], rng)
            else:
                if label == 1:
                    test_malware.append(sample)
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
    """Load primary file types for a set of row IDs.

    Uses the lightweight ``file_type`` column when available (Postgres),
    falling back to parsing cleave_result JSON (SQLite/demo DBs).
    """
    file_types_by_row: dict[int, str] = {}
    chunk_size = 5000
    for start in range(0, len(row_ids), chunk_size):
        chunk = row_ids[start : start + chunk_size]
        try:
            file_types_by_row.update(_fetch_file_types_lightweight(db_path, chunk))
        except Exception:
            # Fallback: parse from cleave_result JSON (slower, for SQLite).
            for row_id, item in data.fetch_cleave_results(db_path, chunk).items():
                file_type = "unknown"
                try:
                    report = json.loads(item["cleave_result"])
                    file_type = str(features.primary_file(report).get("type") or "unknown")
                except (json.JSONDecodeError, KeyError):
                    pass
                file_types_by_row[row_id] = file_type

    return np.asarray([file_types_by_row.get(row_id, "unknown") for row_id in row_ids], dtype=object)


def _fetch_file_types_lightweight(
    db_path: Path | str, ids: list[int],
) -> dict[int, str]:
    """Fetch file_type column directly — no JSON parsing needed."""
    if not ids:
        return {}
    with data._connect(db_path) as conn:
        if data._is_pg(db_path):
            with conn.cursor() as cur:
                cur.execute("SELECT id, file_type FROM samples WHERE id = ANY(%s)", [ids])
                return {int(rid): (ft or "unknown") for rid, ft in cur}
        else:
            placeholders = ",".join("?" for _ in ids)
            return {
                int(rid): (ft or "unknown")
                for rid, ft in conn.execute(
                    f"SELECT id, file_type FROM samples WHERE id IN ({placeholders})", ids  # noqa: S608
                )
            }


def run_experiment(
    db_path: Path | str,
    *,
    output_dir: Path | None = None,
    cache_dir: Path | None = None,
    n_workers: int = 0,
    seed: int = 42,
    train_samples: int = 10_000,
    max_test_samples: int = 0,
    n_folds: int = 2,
    device: str | None = None,
    n_estimators: int = 220,
    max_depth: int = 6,
    learning_rate: float = 0.03,
    early_stopping_rounds: int = 25,
    min_child_weight: int = 5,
    min_child_samples: int | None = None,
    num_leaves: int | None = None,
    colsample_bytree: float = 0.8,
    subsample: float = 0.8,
    gamma: float = 0.0,
    reg_alpha: float = 0.0,
    reg_lambda: float = 1.0,
    beta: float = 1.0,
    learner: str = "litmus-xg",
    model_name: str = "litmus-xg",
    threshold_mode: str = "fbeta",
    threshold_fpr_target: float | None = None,
    hard_negative_fraction: float = 0.0,
    hard_negative_weight: float = 1.0,
    benign_filetype_weights: dict[str, float] | None = None,
    total_limit: int = 0,
    max_id: int = 0,
    drop_feature_prefixes: list[str] | None = None,
    monotone_constraints: dict[str, int] | None = None,
    min_malware_training_score: int = 0,
) -> dict[str, object]:
    """Run a fast subsampled train cycle evaluated on the full external test bucket."""
    # Pin the dataset to a single max(id) snapshot so concurrent inserts to the
    # hopper DB don't cause drift between this run and any others.
    pinned_max_id = int(max_id) if max_id > 0 else data.snapshot_max_id(db_path)
    log.info("dataset snapshot: max_id=%d", pinned_max_id)

    feature_cfg = features.feature_config_from_env()

    # --- Cache level 2: full matrices (corpus + feature config match) --------
    corpus_hash = _corpus_cache_key(
        seed, train_samples, max_test_samples, min_malware_training_score, pinned_max_id,
    ) if cache_dir else ""
    matrix_hash = _matrix_cache_key(corpus_hash, feature_cfg) if cache_dir else ""

    cached_matrices = _load_matrix_cache(cache_dir, matrix_hash) if cache_dir else None
    if cached_matrices is not None:
        spec, X_train, y_train, X_test, y_test, train_file_types = cached_matrices
        print(f"\nEXPERIMENT (cached matrices: {X_train.shape[0]} train, {X_test.shape[0]} test)")
    else:
        # --- Cache level 1: corpus row selections + file types ----------------
        cached_corpus = _load_corpus_cache(cache_dir, corpus_hash) if cache_dir else None
        if cached_corpus is not None:
            corpus, train_file_types = cached_corpus
        else:
            corpus = sample_partitioned_reports(
                db_path,
                train_samples=train_samples,
                max_test_samples=max_test_samples,
                seed=seed,
                total_limit=total_limit,
                min_malware_training_score=min_malware_training_score,
                max_id=pinned_max_id,
            )
            sorted_train = sorted(corpus.train_samples, key=lambda s: s.row_id)
            train_file_types = _load_primary_file_types(db_path, [s.row_id for s in sorted_train])
            if cache_dir:
                _save_corpus_cache(cache_dir, corpus_hash, corpus, train_file_types)
        _print_dataset_summary(corpus)

        if len(corpus.train_samples) < 10:
            raise ValueError(f"only {len(corpus.train_samples)} sampled training rows, need at least 10")

        # Sort corpus to match DB extraction order (by row_id).
        sorted_train = sorted(corpus.train_samples, key=lambda s: s.row_id)
        sorted_test = sorted(corpus.test_samples, key=lambda s: s.row_id)

        log.info("pass 1: building vocabulary (worker-local DB fetching)")
        spec = features.build_vocab_from_db(
            db_path,
            [(s.row_id, s.label) for s in sorted_train],
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

        if cache_dir:
            _save_matrix_cache(cache_dir, matrix_hash, spec, X_train, y_train, X_test, y_test, train_file_types)

    # Experiment 38: Semantic Clustering.
    if "clusters" in features.feature_config_from_env().enabled_groups:
        log.info("clustering benign training samples...")
        from sklearn.cluster import KMeans
        benign_indices = np.where(y_train == 0)[0]
        if len(benign_indices) >= 50:
            kmeans = KMeans(n_clusters=50, random_state=seed, n_init=10).fit(X_train[benign_indices])
            train_clusters = kmeans.predict(X_train)
            train_dists = kmeans.transform(X_train).min(axis=1)
            test_clusters = kmeans.predict(X_test)
            test_dists = kmeans.transform(X_test).min(axis=1)

            # Find the start index of Group 21: Semantic Clusters.
            cluster_start_idx = -1
            for i, name in enumerate(spec.feature_names):
                if name == "cluster:0":
                    cluster_start_idx = i
                    break

            if cluster_start_idx != -1:
                log.info("applying cluster IDs and distances to feature matrices...")
                # Convert to LIL for efficient row-wise modification of specific columns.
                X_train_lil = X_train.tolil()
                for i, (c_id, dist) in enumerate(zip(train_clusters, train_dists)):
                    if 0 <= c_id < 50:
                        X_train_lil[i, cluster_start_idx + c_id] = 1.0
                    X_train_lil[i, cluster_start_idx + 50] = float(dist)
                X_train = X_train_lil.tocsr()

                X_test_lil = X_test.tolil()
                for i, (c_id, dist) in enumerate(zip(test_clusters, test_dists)):
                    if 0 <= c_id < 50:
                        X_test_lil[i, cluster_start_idx + c_id] = 1.0
                    X_test_lil[i, cluster_start_idx + 50] = float(dist)
                X_test = X_test_lil.tocsr()
            else:
                log.warning("clustering enabled but 'cluster:0' feature not found in spec")
    if drop_feature_prefixes:
        X_train, pruned_spec = features.drop_feature_prefixes(X_train, spec, drop_feature_prefixes)
        X_test, _ = features.drop_feature_prefixes(X_test, spec, drop_feature_prefixes)
        spec = pruned_spec
        log.info(
            "dropped feature prefixes for experiment: %s (%d features remain)",
            drop_feature_prefixes, spec.total_features,
        )
    # Build monotonic constraints for all behavior features.
    # We want to force the model to treat 'presence', 'criticality', and 'aggregate counts'
    # of findings as purely additive signals for malware.
    # We use a tuple aligned by index because XGBoost cannot reliably match
    # feature names when training on sparse matrices.
    constraints = [0] * len(spec.feature_names)
    for i, name in enumerate(spec.feature_names):
        if monotone_constraints and name in monotone_constraints:
            constraints[i] = monotone_constraints[name]
            continue

        if name.startswith(("present:", "maxcrit:")):
            constraints[i] = 1
        elif name.startswith("agg:") and ("suspicious" in name or "hostile" in name or "findings_log" in name):
            constraints[i] = 1
        elif name in ("struct:stealth_potential", "struct:silent_packer_signal"):
            constraints[i] = 1
        elif name.startswith("gap:"):
            constraints[i] = 1

    result = train.train(
        X_train,
        y_train,
        train.TrainConfig(
            learner=learner,
            seed=seed,
            device=device,
            n_folds=n_folds,
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            early_stopping_rounds=early_stopping_rounds,
            min_child_weight=min_child_weight,
            min_child_samples=min_child_samples,
            num_leaves=num_leaves,
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
        "model_name": model_name,
        "learner": learner,
        "device": device or "auto",
        "train_rows": int(X_train.shape[0]),
        "test_rows": int(X_test.shape[0]),
        "n_features": int(spec.total_features),
        "drop_feature_prefixes": list(drop_feature_prefixes or []),
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
        model_filename = "model.txt" if learner == "azoth" else "model.json"
        export.save_model(result.model, output_dir / model_filename)
        export.save_run_summary(kind="experiment", payload=results, output_dir=output_dir)
    return results
