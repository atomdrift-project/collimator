"""Fast, deterministic subsampled experiments for feature/model iteration."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import time
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

from . import bundle, data, export, features, train
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
#   Keyed by corpus hash + FeatureConfig + COLLIMATOR_* feature env.  Saves
#   X_train, y_train, X_test, y_test, FeatureSpec.  When only model
#   hyperparameters change, the entire data pipeline is skipped.
#
# When n-gram config changes, level 2 misses but level 1 still hits — saving
# the metadata scan while re-running vocab + extraction.


EXPERIMENT_FILEGROUPS: dict[str, tuple[str, ...]] = {
    "scripts": (
        "batch",
        "javascript",
        "lua",
        "perl",
        "php",
        "powershell",
        "python",
        "ruby",
        "shell",
        "typescript",
        "vbscript",
    ),
    "native": ("elf", "macho", "pe"),
    "portable": ("dex", "java_class", "pyc", "wasm"),
    "documents": ("doc", "docx", "html", "ole", "pdf", "ppt", "pptx", "rtf", "xls", "xlsx"),
    "source": (
        "c",
        "cpp",
        "csharp",
        "go",
        "java",
        "kotlin",
        "makefile",
        "rust",
        "scala",
        "swift",
    ),
    "config": ("ini", "json", "package.json", "plist", "toml", "xml", "yaml", "yml"),
    "media": ("bmp", "gif", "jpg", "jpeg", "mp3", "mp4", "png", "svg", "webp"),
}


def _corpus_cache_key(
    seed: int,
    train_samples: int,
    max_test_samples: int,
    min_malware_training_score: int,
    max_id: int,
    route: str,
    route_file_types: tuple[str, ...],
    total_limit: int,
    test_natural_prevalence: bool = False,
    oof_fold_exclude: int | None = None,
) -> str:
    """Deterministic hash for the row-selection parameters.

    ``oof_fold_exclude`` mirrors ``EXP_OOF_FOLD_EXCLUDE``: when set to 0
    or 1, that OOF half is dropped from the corpus snapshot. The two
    fold variants produce DIFFERENT row sets at the same seed, so the
    cache key must distinguish them. Otherwise fold-A and fold-B share
    the same snapshot cache and the second fold gets the first fold's
    rows back.
    """
    blob = json.dumps({
        "seed": seed,
        "train_samples": train_samples,
        "max_test_samples": max_test_samples,
        "min_malware_training_score": min_malware_training_score,
        "max_id": max_id,
        "min_sample_score": data.MIN_SAMPLE_SCORE,
        "route": route,
        "route_file_types": sorted(route_file_types),
        "total_limit": total_limit,
        "test_natural_prevalence": bool(test_natural_prevalence),
        "oof_fold_exclude": oof_fold_exclude,
    }, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def _route_file_types(route: str) -> tuple[str, ...]:
    """Return the file types covered by an experiment route."""
    normalized = str(route or "general").strip().lower()
    if normalized in {"", "general"}:
        return ()
    if normalized.startswith("filetypes/"):
        name = normalized.split("/", 1)[1].strip()
        if not name:
            raise ValueError(f"invalid experiment route: {route!r}")
        return (name,)
    if normalized.startswith("filegroups/"):
        name = normalized.split("/", 1)[1].strip()
        try:
            return EXPERIMENT_FILEGROUPS[name]
        except KeyError as exc:
            known = ", ".join(sorted(EXPERIMENT_FILEGROUPS))
            raise ValueError(f"unknown experiment filegroup {name!r}; known groups: {known}") from exc
    raise ValueError(
        f"invalid experiment route {route!r}; expected general, filetypes/<name>, or filegroups/<name>",
    )


def _matrix_cache_key(
    corpus_hash: str,
    feature_cfg: features.FeatureConfig,
    feature_env: dict[str, str],
) -> str:
    """Deterministic hash for corpus + feature configuration."""
    cfg_dict = _feature_config_dict(feature_cfg)
    blob = json.dumps(
        {
            "corpus": corpus_hash,
            "feature_config": cfg_dict,
            "feature_env": feature_env,
        },
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def _feature_config_dict(feature_cfg: features.FeatureConfig) -> dict[str, object]:
    """Return JSON-friendly feature config for summaries and cache keys."""
    cfg_dict = {f.name: getattr(feature_cfg, f.name) for f in feature_cfg.__dataclass_fields__.values()}
    cfg_dict["enabled_groups"] = sorted(cfg_dict["enabled_groups"])
    return cfg_dict


def _experiment_key(spec: dict[str, object]) -> str:
    blob = json.dumps(spec, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def _collimator_env() -> dict[str, str]:
    prefixes = (
        "COLLIMATOR_",
    )
    return {
        key: value
        for key, value in sorted(os.environ.items())
        if key.startswith(prefixes) and key not in {"COLLIMATOR_EXPERIMENT_TAG"}
    }


def _cached_snapshot_max_id(
    db_path: Path | str,
    cache_dir: Path | None,
    requested_max_id: int,
    *,
    refresh: bool = False,
) -> int:
    """Pin cached experiments to one DB snapshot until explicitly refreshed."""
    if requested_max_id > 0 or cache_dir is None:
        return int(requested_max_id) if requested_max_id > 0 else data.snapshot_max_id(db_path)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / "snapshot_max_id.txt"
    if not refresh and path.exists():
        try:
            value = int(path.read_text().strip())
            if value > 0:
                log.info("using cached experiment snapshot: max_id=%d", value)
                return value
        except ValueError:
            log.warning("ignoring invalid cached experiment snapshot: %s", path)
    value = data.snapshot_max_id(db_path)
    path.write_text(f"{value}\n")
    log.info("pinned experiment snapshot: max_id=%d (%s)", value, path)
    return value


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
    bundle.atomic_write_json(path, obj, indent=None)
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
    sp.save_npz(str(cache_dir / f"matrix_{matrix_hash}_Xtrain.npz"), X_train, compressed=False)
    sp.save_npz(str(cache_dir / f"matrix_{matrix_hash}_Xtest.npz"), X_test, compressed=False)
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
    route_file_types: tuple[str, ...] = (),
    test_natural_prevalence: bool = False,
) -> ExperimentCorpus:
    """Reservoir-sample train rows and optionally cap the external test bucket.

    If train_samples > 0, we reservoir-sample train rows to that target,
    balancing malware/benign 50/50.
    If train_samples == 0, we take ALL non-test rows from the stream (natural distribution).

    If max_test_samples > 0, we reservoir-sample test rows to that target.
    Default behavior balances malware/benign 50/50 (preserves F1/AUC semantics).
    Setting ``test_natural_prevalence=True`` removes the per-class cap so the
    test set carries the route's true class ratio — important for resolving
    recall@k FP/M, since the metric needs as many benigns as the holdout can
    provide (route benign counts dominate the FP/M denominator).
    If max_test_samples == 0, we take ALL test rows from the stream (natural distribution).
    """
    rng = np.random.default_rng(seed)

    train_malware_target = max(train_samples // 2, 1) if train_samples > 1 else train_samples
    train_benign_target = max(train_samples - train_malware_target, 0)

    if test_natural_prevalence:
        # Single pooled cap; class ratio falls out of the natural stream order
        # (which preserves SHA256-bucket determinism).
        test_total_target = max_test_samples
    else:
        test_malware_target = max(max_test_samples // 2, 1) if max_test_samples > 1 else max_test_samples
        test_benign_target = max(max_test_samples - test_malware_target, 0) if max_test_samples > 0 else 0

    train_malware: list[ExperimentSample] = []
    train_benign: list[ExperimentSample] = []
    test_malware: list[ExperimentSample] = []
    test_benign: list[ExperimentSample] = []
    test_pool: list[ExperimentSample] = []  # only used when test_natural_prevalence=True
    test_seen = 0  # only used when test_natural_prevalence=True
    seen = {
        (False, 1): 0,
        (False, 0): 0,
        (True, 1): 0,
        (True, 0): 0,
    }

    # Optional OOF fold exclusion. When EXP_OOF_FOLD_EXCLUDE is set to "0"
    # or "1", drop rows whose canonical-hash-derived oof_fold matches the
    # value. Used for k=2 out-of-fold training: a single training run that
    # excludes one of the two halves of train+dev becomes one of the two
    # fold models; the held-out half then gets OOF predictions from this
    # model for downstream calibration. Test partition is excluded as
    # always; OOF fold logic only affects train+dev rows.
    oof_exclude_str = os.getenv("EXP_OOF_FOLD_EXCLUDE", "").strip()
    oof_exclude: int | None = None
    if oof_exclude_str:
        try:
            value = int(oof_exclude_str)
        except ValueError:
            log.warning("ignoring invalid EXP_OOF_FOLD_EXCLUDE=%r (need 0 or 1)", oof_exclude_str)
        else:
            if value in (0, 1):
                oof_exclude = value
                log.info("OOF k=2: excluding fold %d from training", value)
            else:
                log.warning("ignoring EXP_OOF_FOLD_EXCLUDE=%d (need 0 or 1)", value)

    for row_id, label, partition, group_id, score in data.stream_partitioned_metadata_grouped(
        db_path,
        limit=total_limit,
        max_id=max_id,
        file_types=route_file_types or None,
    ):
        # Locked test partition is reserved for final headline evaluation
        # (azoth-deploy / calibration). Screen experiments operate on
        # train + dev only — dev fills the historical "is_test" eval-slice
        # role for autocollie's selection.
        if partition == "test":
            continue
        if oof_exclude is not None and data.oof_fold_of(group_id) == oof_exclude:
            continue
        is_test = partition == "dev"
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
            if test_natural_prevalence and max_test_samples > 0:
                # Single pooled reservoir across both classes — natural prevalence.
                test_seen = _reservoir_update(test_pool, sample, test_total_target, test_seen, rng)
            elif max_test_samples > 0:
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

    if test_natural_prevalence and max_test_samples > 0:
        # Split the pooled samples back into class buckets so downstream code
        # (which still concatenates benigns then malware) works unchanged.
        for s in test_pool:
            if s.label == 1:
                test_malware.append(s)
            else:
                test_benign.append(s)

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
        f"External test: {len(corpus.test_samples)} "
        f"({test_malware} malware, {len(corpus.test_samples) - test_malware} benign)"
    )


def _print_test_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float,
) -> None:
    y_pred = (y_prob >= threshold).astype(int)
    print(f"\n{'EXTERNAL TEST':=^60}")
    print(f"  Threshold: {threshold:.3f}")
    print(f"  Precision: {precision_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"  Recall:    {recall_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"  F1:        {f1_score(y_true, y_pred, zero_division=0):.4f}")
    if len(np.unique(y_true)) > 1:
        print(f"  ROC AUC:   {roc_auc_score(y_true, y_prob):.4f}")
        print(f"  Avg Prec:  {average_precision_score(y_true, y_prob):.4f}")
        print(f"  Brier:     {brier_score_loss(y_true, y_prob):.4f}")
        rec_fp = _recall_at_fp_per_million(y_true, y_prob)
        print(
            f"  Recall@FP/M: 0={rec_fp['recall_at_fp_per_million_0']:.4f} "
            f"1={rec_fp['recall_at_fp_per_million_1']:.4f} "
            f"3={rec_fp['recall_at_fp_per_million_3']:.4f} "
            f"5={rec_fp['recall_at_fp_per_million_5']:.4f} "
            f"9={rec_fp['recall_at_fp_per_million_9']:.4f} "
            f"(n_benign={rec_fp['n_benign_holdout']}, "
            f"min_resolvable={rec_fp['min_observable_fp_per_million']:.1f}/M)"
        )


# k values reported by `_recall_at_fp_per_million`.  Recall@3 FP/M is the
# operating point the deployed Azoth bundle ships at, so it's the autocollie
# gate's primary axis.  0/1/5/9 frame the curve around it: 0 is the strict
# zero-FP point, 9 the upper edge of the deployed band.
RECALL_AT_FP_PER_MILLION_KS: tuple[float, ...] = (0.0, 1.0, 3.0, 5.0, 9.0)


def _recall_at_fp_per_million(
    y_true: np.ndarray, y_prob: np.ndarray,
) -> dict[str, float | int]:
    """Recall on malware at thresholds where benign FP rate equals k per million.

    For each ``k`` in :data:`RECALL_AT_FP_PER_MILLION_KS` we compute the FP
    budget ``floor(n_benign * k / 1e6)`` and return the recall at the lowest
    threshold whose cumulative benign FPs do not exceed that budget.  When
    ``n_benign`` is small enough that ``k FP/M`` rounds to zero allowed FPs
    (typical for narrow routes), the metric collapses to recall@0 — the
    truthful answer at that holdout size.  Callers can read
    ``n_benign_holdout`` to detect this saturation case.
    """
    n_benign = int(np.sum(y_true == 0))
    n_malware = int(np.sum(y_true == 1))
    # `min_observable_fp_per_million` is 1e6 / n_benign — the smallest non-zero
    # FPR resolvable with this holdout (one false positive over the benign pool).
    # Below this floor, recall@k collapses to recall@0 because there's no integer
    # FP budget to spend.  Reporting the floor lets downstream gates pick the
    # smallest meaningful k for the route instead of optimizing a metric the
    # holdout can't actually distinguish.
    min_observable = (1_000_000.0 / n_benign) if n_benign > 0 else float("inf")
    out: dict[str, float | int] = {
        "n_benign_holdout": n_benign,
        "n_malware_holdout": n_malware,
        "min_observable_fp_per_million": min_observable,
    }
    if n_benign == 0 or n_malware == 0:
        for k in RECALL_AT_FP_PER_MILLION_KS:
            out[f"recall_at_fp_per_million_{int(k)}"] = 0.0
            out[f"threshold_at_fp_per_million_{int(k)}"] = 1.0
        return out

    order = np.argsort(y_prob, kind="stable")[::-1]
    sorted_probs = y_prob[order]
    sorted_y = y_true[order]
    cum_fp = np.cumsum(sorted_y == 0)
    cum_tp = np.cumsum(sorted_y == 1)
    # Collapse to threshold breakpoints so equal-probability rows don't get
    # split between sides of a threshold.
    change_mask = np.concatenate([np.diff(sorted_probs) != 0, [True]])
    cuts = np.where(change_mask)[0]
    thresholds = sorted_probs[cuts]
    fp_at_cut = cum_fp[cuts]
    tp_at_cut = cum_tp[cuts]
    for k in RECALL_AT_FP_PER_MILLION_KS:
        budget = int(np.floor(n_benign * k / 1_000_000.0))
        valid = fp_at_cut <= budget
        suffix = f"fp_per_million_{int(k)}"
        if valid.any():
            idx = int(np.where(valid)[0][-1])
            out[f"recall_at_{suffix}"] = float(tp_at_cut[idx] / n_malware)
            out[f"threshold_at_{suffix}"] = float(thresholds[idx])
        else:
            out[f"recall_at_{suffix}"] = 0.0
            out[f"threshold_at_{suffix}"] = float(np.nextafter(float(sorted_probs[0]), np.inf))
    return out


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
    holdout_fraction: float = 0.0,
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
    scale_pos_weight_mult: float = 1.0,
    boosting_type: str = "gbdt",
    extra_trees: bool = False,
    seed_search_k: int = 1,
    save_all_seeds: bool = False,
    test_natural_prevalence: bool = False,
    total_limit: int = 0,
    max_id: int = 0,
    drop_feature_prefixes: list[str] | None = None,
    monotone_constraints: dict[str, int] | None = None,
    min_malware_training_score: int = 0,
    refresh_cache_snapshot: bool = False,
    experiment_idea: str = "adhoc",
    route: str = "general",
    rerun_existing: bool = False,
) -> dict[str, object]:
    """Run a fast subsampled train cycle evaluated on the full external test bucket."""
    started = time.perf_counter()
    # Pin the dataset to a single max(id) snapshot so concurrent inserts to the
    # hopper DB don't cause drift between this run and any others.
    pinned_max_id = _cached_snapshot_max_id(
        db_path,
        cache_dir,
        int(max_id),
        refresh=refresh_cache_snapshot,
    )
    log.info("dataset snapshot: max_id=%d", pinned_max_id)

    feature_cfg = features.feature_config_from_env()
    feature_env = _collimator_env()
    route_file_types = _route_file_types(route)
    train_config = {
        "n_folds": int(n_folds),
        "holdout_fraction": float(holdout_fraction),
        "device": device,
        "n_estimators": int(n_estimators),
        "max_depth": int(max_depth),
        "learning_rate": float(learning_rate),
        "early_stopping_rounds": int(early_stopping_rounds),
        "min_child_weight": int(min_child_weight),
        "min_child_samples": min_child_samples,
        "num_leaves": num_leaves,
        "colsample_bytree": float(colsample_bytree),
        "subsample": float(subsample),
        "gamma": float(gamma),
        "reg_alpha": float(reg_alpha),
        "reg_lambda": float(reg_lambda),
        "beta": float(beta),
        "threshold_mode": threshold_mode,
        "threshold_fpr_target": threshold_fpr_target,
        "hard_negative_fraction": float(hard_negative_fraction),
        "hard_negative_weight": float(hard_negative_weight),
        "benign_filetype_weights": benign_filetype_weights or {},
        "scale_pos_weight_mult": float(scale_pos_weight_mult),
        "boosting_type": str(boosting_type),
        "extra_trees": bool(extra_trees),
    }
    # EXP_OOF_FOLD_EXCLUDE controls which OOF fold is held out from
    # training (see the row-selection branch below). It MUST participate
    # in the experiment_key — fold-A and fold-B select different rows
    # but share every other parameter, so without this they collide on
    # the same cached run and the second fold reuses the first fold's
    # bundle (the bug that broke azoth-oof-pipeline.sh's stage 2).
    _oof_fold_exclude_str = os.getenv("EXP_OOF_FOLD_EXCLUDE", "").strip()
    _oof_fold_exclude: int | None = None
    if _oof_fold_exclude_str in {"0", "1"}:
        _oof_fold_exclude = int(_oof_fold_exclude_str)
    experiment_spec: dict[str, object] = {
        "route": route,
        "route_file_types": list(route_file_types),
        "snapshot_max_id": int(pinned_max_id),
        "seed": int(seed),
        "seed_search_k": max(int(seed_search_k), 1),
        # save_all_seeds participates in the experiment_key so toggling between
        # picking-best (legacy) and averaged-ensemble (item A) deploy modes
        # produces distinct cached runs — they share training compute but
        # differ in shipped artifact and reported metrics, so reusing one for
        # the other would mask the contract change.
        "save_all_seeds": bool(save_all_seeds) and max(int(seed_search_k), 1) > 1,
        "oof_fold_exclude": _oof_fold_exclude,
        "train_samples": int(train_samples),
        "max_test_samples": int(max_test_samples),
        "test_natural_prevalence": bool(test_natural_prevalence),
        "total_limit": int(total_limit),
        "learner": learner,
        "model_name": model_name,
        "feature_config": _feature_config_dict(feature_cfg),
        "feature_env": feature_env,
        "train_config": train_config,
        "filters": {
            "min_sample_score": data.MIN_SAMPLE_SCORE,
            "min_malware_training_score": int(min_malware_training_score),
            "drop_feature_prefixes": list(drop_feature_prefixes or []),
            "monotone_constraints": monotone_constraints or {},
        },
    }
    exp_key = _experiment_key(experiment_spec)
    keyed_result_path = output_dir / "runs" / f"{exp_key}.json" if output_dir is not None else None
    if keyed_result_path is not None and keyed_result_path.exists() and not rerun_existing:
        with open(keyed_result_path) as f:
            existing = json.load(f)
        payload = existing.get("experiment", existing)
        metrics = payload.get("sampled_test_metrics") or {}
        print(
            f"experiment already exists: {exp_key} "
            f"(route={payload.get('route', route)} idea={payload.get('idea', experiment_idea)})"
        )
        if metrics:
            print(
                "  previous metrics: "
                f"F1={float(metrics.get('f1', 0.0)):.6f} "
                f"P={float(metrics.get('precision', 0.0)):.6f} "
                f"R={float(metrics.get('recall', 0.0)):.6f} "
                f"AUC={float(metrics.get('roc_auc', 0.0)):.6f}"
            )
        print("  set EXP_RERUN=1 or --rerun-existing to force a replicate")
        return payload

    # --- Cache level 2: full matrices (corpus + feature config match) --------
    corpus_hash = (
        _corpus_cache_key(
            seed,
            train_samples,
            max_test_samples,
            min_malware_training_score,
            pinned_max_id,
            route,
            route_file_types,
            total_limit,
            test_natural_prevalence=test_natural_prevalence,
            oof_fold_exclude=_oof_fold_exclude,
        )
        if cache_dir
        else ""
    )
    matrix_hash = _matrix_cache_key(corpus_hash, feature_cfg, feature_env) if cache_dir else ""

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
                route_file_types=route_file_types,
                test_natural_prevalence=test_natural_prevalence,
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

    # Best-of-K seed search: train K models with seeds [seed, seed+1, ..., seed+K-1],
    # ship the one with highest holdout recall@3 FP/M (deployed operating point) with
    # F1 fallback when recall@3 is unresolvable on tiny holdouts.  K=1 (default) is
    # the single-fit current behavior.  Corpus + matrix are reused across attempts
    # — only the model fit varies — so wall clock is K × model_fit, not K × full_pipeline.
    seed_search_k = max(int(seed_search_k), 1)
    seed_search_results: list[dict[str, float | int]] = []
    result = None
    sampled_test_metrics: dict[str, float] = {}
    winning_seed = int(seed)
    winning_idx = 0
    best_score = -math.inf
    # When `save_all_seeds=True` and seed_search_k>1, we deploy the *averaged*
    # ensemble across all K seeds rather than the best single seed. We keep
    # every trained model and its test-time probabilities here so we can both
    # (a) recompute sampled_test_metrics on the averaged scores below, and
    # (b) write each member to the multi-seed bundle layout.
    all_attempt_models: list[Any] = []
    all_attempt_seeds: list[int] = []
    all_attempt_probs: list[np.ndarray] = []

    for k_idx in range(seed_search_k):
        attempt_seed = int(seed) + k_idx
        if seed_search_k > 1:
            log.info("seed-search attempt %d/%d (seed=%d)", k_idx + 1, seed_search_k, attempt_seed)
        attempt_started = time.perf_counter()
        attempt_result = train.train(
            X_train,
            y_train,
            train.TrainConfig(
                learner=learner,
                seed=attempt_seed,
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
                scale_pos_weight_mult=scale_pos_weight_mult,
                boosting_type=boosting_type,
                extra_trees=extra_trees,
                monotone_constraints=tuple(constraints),
                holdout_fraction=holdout_fraction,
            ),
            feature_names=spec.feature_names,
            sample_file_types=train_file_types,
        )

        attempt_metrics: dict[str, float] = {}
        attempt_probs: np.ndarray | None = None
        if X_test.shape[0] > 0:
            attempt_probs = predict_proba(attempt_result.model, X_test)
            if k_idx == 0:
                _print_test_metrics(y_test, attempt_probs, attempt_result.optimal_threshold)
            y_pred = (attempt_probs >= attempt_result.optimal_threshold).astype(int)
            attempt_metrics = {
                "precision": float(precision_score(y_test, y_pred, zero_division=0)),
                "recall": float(recall_score(y_test, y_pred, zero_division=0)),
                "f1": float(f1_score(y_test, y_pred, zero_division=0)),
                "roc_auc": float(roc_auc_score(y_test, attempt_probs)) if len(np.unique(y_test)) > 1 else 0.0,
                "avg_precision": (
                    float(average_precision_score(y_test, attempt_probs)) if len(np.unique(y_test)) > 1 else 0.0
                ),
                "brier": float(brier_score_loss(y_test, attempt_probs)) if len(np.unique(y_test)) > 1 else 0.0,
            }
            attempt_metrics.update(_recall_at_fp_per_million(y_test, attempt_probs))
        elif k_idx == 0:
            print("\nNo external test rows available.")
        all_attempt_models.append(attempt_result.model)
        all_attempt_seeds.append(int(attempt_seed))
        if attempt_probs is not None:
            all_attempt_probs.append(attempt_probs)

        # Winner score: prefer recall@3 FP/M (deployed operating point); fall back
        # to F1 when the holdout is too small to resolve recall@3 (then it equals
        # recall@0 across all attempts and F1 becomes the only signal).
        attempt_score = float(attempt_metrics.get("recall_at_fp_per_million_3",
                              attempt_metrics.get("f1", 0.0)))
        seed_search_results.append({
            "seed": attempt_seed,
            "f1": float(attempt_metrics.get("f1", 0.0)),
            "roc_auc": float(attempt_metrics.get("roc_auc", 0.0)),
            "avg_precision": float(attempt_metrics.get("avg_precision", 0.0)),
            "recall_at_fp_per_million_3": float(attempt_metrics.get("recall_at_fp_per_million_3", 0.0)),
            "wall_s": float(time.perf_counter() - attempt_started),
        })
        if seed_search_k > 1:
            log.info(
                "seed-search attempt %d/%d done: F1=%.4f AUC=%.4f recall@3FPM=%.4f (%.1fs)",
                k_idx + 1, seed_search_k,
                attempt_metrics.get("f1", 0.0), attempt_metrics.get("roc_auc", 0.0),
                attempt_metrics.get("recall_at_fp_per_million_3", 0.0),
                seed_search_results[-1]["wall_s"],
            )

        if attempt_score > best_score:
            best_score = attempt_score
            result = attempt_result
            sampled_test_metrics = attempt_metrics
            winning_seed = attempt_seed
            winning_idx = k_idx

    if seed_search_k > 1:
        log.info(
            "seed-search winner: attempt %d/%d (seed=%d, score=%.4f)",
            winning_idx + 1, seed_search_k, winning_seed, best_score,
        )

    # Multi-seed averaging (item A): when save_all_seeds=True with K>1, the
    # deployed bundle ships every member, and at predict time litmus averages
    # their probabilities. The reported sampled_test_metrics should reflect
    # *that* averaged ensemble — not the best single seed — so the metric
    # autocollie compares against the baseline matches what the runtime
    # actually emits.
    deploy_averaged = bool(save_all_seeds) and len(all_attempt_models) > 1 \
        and len(all_attempt_probs) == len(all_attempt_models)
    averaged_threshold: float | None = None
    if deploy_averaged:
        # Mean of K seed probabilities, in f64 for summation stability then
        # cast back to f32 (matches what litmus emits on the same files).
        ensemble_probs = (
            np.mean([p.astype(np.float64) for p in all_attempt_probs], axis=0)
            .astype(np.float32)
        )
        # Re-pick the threshold on the AVERAGED probabilities. Reusing the
        # winning single-seed threshold is wrong: averaging compresses the
        # variance of the score distribution (~K reduction), so the same
        # numeric cutoff falls at a materially different quantile. The
        # deployed score-to-class mapping must correspond to a threshold
        # the trainer would actually pick on the averaged distribution.
        try:
            averaged_threshold = float(train._select_threshold(
                y_test.astype(int), ensemble_probs,
                mode=threshold_mode, beta=float(beta), max_fpr=threshold_fpr_target,
            ))
        except (ValueError, IndexError) as exc:
            # Degenerate test set (single class, all-zero probs, etc.) —
            # fall back to the winner's threshold and surface the reason
            # rather than silently shipping a 0.5 default.
            averaged_threshold = float(result.optimal_threshold)
            log.warning(
                "averaged-ensemble threshold selection failed (%s); "
                "falling back to winner's threshold %.4f",
                exc, averaged_threshold,
            )
        y_pred = (ensemble_probs >= averaged_threshold).astype(int)
        multi_class = len(np.unique(y_test)) > 1
        sampled_test_metrics = {
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, ensemble_probs)) if multi_class else 0.0,
            "avg_precision": float(average_precision_score(y_test, ensemble_probs)) if multi_class else 0.0,
            "brier": float(brier_score_loss(y_test, ensemble_probs)) if multi_class else 0.0,
            "threshold": averaged_threshold,
            **_recall_at_fp_per_million(y_test, ensemble_probs),
        }
        log.info(
            "seed-search averaged ensemble (K=%d): "
            "F1=%.4f AUC=%.4f recall@3FPM=%.4f threshold=%.4f (re-picked on averaged probs)",
            len(all_attempt_models),
            sampled_test_metrics["f1"],
            sampled_test_metrics["roc_auc"],
            sampled_test_metrics.get("recall_at_fp_per_million_3", 0.0),
            averaged_threshold,
        )

    results = {
        "model_name": model_name,
        "experiment_key": exp_key,
        "idea": experiment_idea,
        "route": route,
        "experiment_spec": experiment_spec,
        "experiment_tag": os.getenv("COLLIMATOR_EXPERIMENT_TAG", ""),
        "learner": learner,
        "device": device or "auto",
        "train_rows": int(X_train.shape[0]),
        "test_rows": int(X_test.shape[0]),
        "n_features": int(spec.total_features),
        "drop_feature_prefixes": list(drop_feature_prefixes or []),
        "feature_config": _feature_config_dict(feature_cfg),
        "feature_env": feature_env,
        "train_config": train_config,
        "train_metrics": result.metrics,
        "sampled_test_metrics": sampled_test_metrics,
        # Row IDs that produced `sampled_test_metrics` above. autocollie
        # uses this to score the *deployed* bundle on the same rows
        # (azoth_score_deployed.py --row-ids-file), so promote decisions
        # compare apples-to-apples instead of comparing the candidate's
        # screen holdout against the deployed model's larger test
        # partition slice.
        "test_sample_row_ids": [int(s.row_id) for s in sorted_test],
        # When deploy_averaged, this is the threshold re-picked on the
        # AVERAGED ensemble's probabilities (matches what the deployment
        # would actually classify at). Otherwise it's the single trained
        # model's optimal threshold.
        "threshold": (
            averaged_threshold if (deploy_averaged and averaged_threshold is not None)
            else float(result.optimal_threshold)
        ),
        "split_summary": result.split_summary,
        "db_path": str(db_path),
        # `seed` is the seed of the SHIPPED model (the seed-search winner). The
        # operator-supplied seed is in experiment_spec.seed.  When seed_search_k=1
        # they're identical.
        "seed": int(winning_seed),
        "seed_search_k": seed_search_k,
        "seed_search_winner_index": winning_idx,
        "seed_search_results": seed_search_results,
        "save_all_seeds": bool(deploy_averaged),
        "n_seed_models_shipped": len(all_attempt_models) if deploy_averaged else 1,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "elapsed_seconds": float(time.perf_counter() - started),
        "snapshot_max_id": int(pinned_max_id),
    }
    if output_dir is not None:
        spec.save(output_dir / "feature_spec.json")
        ext = "txt" if learner == "azoth" else "json"
        model_filename = f"model.{ext}"
        if deploy_averaged:
            # Multi-seed bundle: write every member to a `.tmp` sibling
            # first, then rename atomically. Crash safety: a kill mid-write
            # leaves at most one stray `.tmp` (which `model_files()` skips
            # because it filters by extension). The legacy single-model
            # artifact is unlinked LAST — only after every new seed file
            # is durable on disk — so we never end up with a bundle that
            # has no models at all.
            shared_models_dir = output_dir / "models"
            shared_models_dir.mkdir(parents=True, exist_ok=True)
            # Prune stale seed files from prior runs that used a different K
            # (or different seed list). Otherwise an orphaned seed_<S>.{ext}
            # gets promoted into the deployed bundle and triggers the
            # mismatched-feature-count check at runtime — caught only by
            # litmus 11 hours into a deploy.
            current_seeds = {int(s) for s in all_attempt_seeds}
            for stale in shared_models_dir.glob(f"seed_*.{ext}"):
                try:
                    stale_seed = int(stale.stem.removeprefix("seed_"))
                except ValueError:
                    continue
                if stale_seed not in current_seeds:
                    stale.unlink()
            for s, m in zip(all_attempt_seeds, all_attempt_models, strict=True):
                final_path = shared_models_dir / f"seed_{s}.{ext}"
                tmp_path = shared_models_dir / f".seed_{s}.{ext}.tmp"
                export.save_model(m, tmp_path)
                os.replace(tmp_path, final_path)
            for legacy in (output_dir / "model.txt", output_dir / "model.json"):
                if legacy.is_file():
                    legacy.unlink()
        else:
            export.save_model(result.model, output_dir / model_filename)
            # Symmetric to the multi-seed branch above (which unlinks any
            # leftover `model.txt`): a previous multi-seed run may have
            # left an `output_dir/models/` directory on disk. Without
            # this cleanup, the Makefile's `azoth-general` recipe — which
            # prefers a `models/` directory over a single `model.txt` —
            # would silently promote the stale bundle and throw away
            # this freshly-trained single-seed model.
            stale_models_dir = output_dir / "models"
            if stale_models_dir.is_dir():
                for stale in stale_models_dir.iterdir():
                    if stale.is_file():
                        stale.unlink()
                try:
                    stale_models_dir.rmdir()
                except OSError:
                    # Directory not empty (e.g. nested layout we didn't
                    # write). Leave it alone rather than silently
                    # nuking unrelated files.
                    log.warning(
                        "stale_models_dir %s is non-empty after pruning; leaving in place",
                        stale_models_dir,
                    )
        export.save_run_summary(kind="experiment", payload=results, output_dir=output_dir)
        if keyed_result_path is not None:
            # Atomic write: autocollie reads this as the source of truth for
            # the experiment's metrics and replays its env via
            # azoth_train_best.py.  A truncated keyed JSON would fail JSON
            # parse and silently exclude the run from historical-best
            # selection.
            bundle.atomic_write_json(keyed_result_path, results)
            log.info("saved keyed experiment summary to %s", keyed_result_path)
            # Also save spec + model under per-key paths so downstream consumers
            # (notably autocollie's candidate-bundle staging) can pick them up
            # by experiment_key without racing against the shared
            # `output_dir / feature_spec.json` and `model.txt` files, which get
            # overwritten by the next `make experiment` invocation.  Without
            # this, when full-train hits the AlreadyExists short-circuit and
            # skips re-extraction, staging would copy whatever spec the most
            # recent unrelated experiment happened to leave behind.
            keyed_spec_path = keyed_result_path.with_name(f"{exp_key}_feature_spec.json")
            spec.save(keyed_spec_path)
            if deploy_averaged:
                # Multi-seed keyed layout: <key>_models/seed_<S>.{txt,json}.
                # autocollie's stageCandidateBundle prefers this directory
                # over the legacy single keyed file when present.  Same
                # tmp-rename pattern as the shared write above so a kill
                # mid-loop never leaves a partial seed file in the keyed
                # dir for staging to pick up.
                keyed_models_dir = keyed_result_path.with_name(f"{exp_key}_models")
                keyed_models_dir.mkdir(parents=True, exist_ok=True)
                for s, m in zip(all_attempt_seeds, all_attempt_models, strict=True):
                    final_path = keyed_models_dir / f"seed_{s}.{ext}"
                    tmp_path = keyed_models_dir / f".seed_{s}.{ext}.tmp"
                    export.save_model(m, tmp_path)
                    os.replace(tmp_path, final_path)
                log.info(
                    "saved keyed feature_spec and %d-seed ensemble to %s, %s",
                    len(all_attempt_models), keyed_spec_path, keyed_models_dir,
                )
            else:
                keyed_model_path = keyed_result_path.with_name(f"{exp_key}_{model_filename}")
                export.save_model(result.model, keyed_model_path)
                log.info("saved keyed feature_spec and model to %s, %s",
                         keyed_spec_path, keyed_model_path)
    return results
