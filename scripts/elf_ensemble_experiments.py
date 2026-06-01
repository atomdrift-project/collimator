#!/usr/bin/env python3
"""Run focused ELF routed-ensemble experiments."""

from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import lightgbm as lgb
import numpy as np
import scipy.sparse as sp

from collimator import data, export, features, model, thresholds
from collimator.model import predict_proba

sys.path.insert(0, str(Path(__file__).resolve().parent))
from azoth_calibrate_ensemble import _calibrate_one, _candidate_thresholds, _hit_mask  # noqa: E402
from azoth_specialist_suite import _fetch_rows, _ids_labels  # noqa: E402

LOG = logging.getLogger("elf_ensemble_experiments")


def _matrix(
    db_path: Path | str,
    rows: list[tuple[int, int]],
    spec: features.FeatureSpec,
    workers: int,
) -> tuple[sp.csr_matrix, np.ndarray]:
    batches = list(features.extract_labeled_from_db_batches(db_path, rows, spec, n_workers=workers))
    if not batches:
        empty_x = sp.csr_matrix((0, spec.total_features), dtype=np.float32)
        return empty_x, np.asarray([], dtype=np.float32)
    x_matrix = sp.vstack([x for x, _y in batches], format="csr")
    y_values = np.concatenate([y for _x, y in batches])
    return x_matrix, y_values


def _fetch_file_type_ids(db_path: Path | str, row_ids: np.ndarray, file_type: str) -> set[int]:
    ids = [int(row_id) for row_id in row_ids]
    out: set[int] = set()
    with data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if data._is_pg(db_path):  # noqa: SLF001
            with conn.cursor() as cur:
                for start in range(0, len(ids), 10_000):
                    chunk = ids[start : start + 10_000]
                    cur.execute(
                        "SELECT id FROM samples WHERE id = ANY(%s) AND file_type = %s",
                        [chunk, file_type],
                    )
                    out.update(int(row_id) for (row_id,) in cur)
        else:
            for start in range(0, len(ids), 10_000):
                chunk = ids[start : start + 10_000]
                placeholders = ",".join("?" for _ in chunk)
                query = f"SELECT id FROM samples WHERE id IN ({placeholders}) AND file_type = ?"  # noqa: S608
                out.update(int(row_id) for (row_id,) in conn.execute(query, [*chunk, file_type]))
    return out


def _budget(n_benign: int, target_per_million: float) -> int:
    if target_per_million <= 0:
        return 0
    return min(n_benign, max(1, int(math.floor(n_benign * target_per_million / 1_000_000))))


def _general_baseline(labels: np.ndarray, general_probs: np.ndarray) -> list[dict[str, Any]]:
    route = {
        "name": "general",
        "indices": np.arange(len(labels), dtype=np.int64),
        "probs": general_probs,
    }
    return [
        {
            "level": int(target["level"]),
            "hostile": _calibrate_one(
                labels,
                [route],
                target_per_million=float(target["hostile_per_million"]),
            ),
        }
        for target in thresholds.SEVERITY_LEVEL_TARGETS
    ]


def _or_levels(
    labels: np.ndarray,
    general_probs: np.ndarray,
    elf_indices: np.ndarray,
    elf_probs: np.ndarray,
) -> list[dict[str, Any]]:
    routes = [
        {
            "name": "general",
            "indices": np.arange(len(labels), dtype=np.int64),
            "probs": general_probs,
        },
        {"name": "elf", "indices": elf_indices, "probs": elf_probs},
    ]
    return [
        {
            "level": int(target["level"]),
            "hostile": _calibrate_one(
                labels,
                routes,
                target_per_million=float(target["hostile_per_million"]),
            ),
        }
        for target in thresholds.SEVERITY_LEVEL_TARGETS
    ]


def _replacement_levels(
    labels: np.ndarray,
    general_probs: np.ndarray,
    elf_indices: np.ndarray,
    elf_probs: np.ndarray,
) -> list[dict[str, Any]]:
    all_indices = np.arange(len(labels), dtype=np.int64)
    non_elf = np.setdiff1d(all_indices, elf_indices, assume_unique=False)
    routes = [
        {"name": "general_non_elf", "indices": non_elf, "probs": general_probs[non_elf]},
        {"name": "elf", "indices": elf_indices, "probs": elf_probs},
    ]
    return [
        {
            "level": int(target["level"]),
            "hostile": _calibrate_one(
                labels,
                routes,
                target_per_million=float(target["hostile_per_million"]),
            ),
        }
        for target in thresholds.SEVERITY_LEVEL_TARGETS
    ]


def _calibrate_acquittal_one(
    labels: np.ndarray,
    general_probs: np.ndarray,
    elf_indices: np.ndarray,
    elf_probs: np.ndarray,
    target_per_million: float,
) -> dict[str, Any]:
    n = len(labels)
    all_indices = np.arange(n, dtype=np.int64)
    non_elf = np.setdiff1d(all_indices, elf_indices, assume_unique=False)
    thresholds_to_try: list[float | None] = [None]
    float_thresholds: list[float] = []
    # Add low-score acquittal thresholds; these are not necessarily useful as
    # positive cut points, but they test whether ELF can veto general FPs.
    float_thresholds.extend(
        float(q)
        for q in np.quantile(elf_probs, [0.001, 0.005, 0.01, 0.02])
    )
    thresholds_to_try.extend(sorted(set(float_thresholds)))
    best: dict[str, Any] | None = None
    for acquit_threshold in thresholds_to_try:
        if acquit_threshold is None:
            general_indices = all_indices
            general_route_probs = general_probs
        else:
            keep_elf = elf_indices[elf_probs > acquit_threshold]
            general_indices = np.concatenate([non_elf, keep_elf])
            general_route_probs = general_probs[general_indices]
        routes = [
            {"name": "general_acquitted", "indices": general_indices, "probs": general_route_probs},
            {"name": "elf", "indices": elf_indices, "probs": elf_probs},
        ]
        result = _calibrate_one(labels, routes, target_per_million=target_per_million)
        result["acquit_threshold"] = None if acquit_threshold is None else float(acquit_threshold)
        if best is None or (result["tp"], -result["fp"]) > (best["tp"], -best["fp"]):
            best = result
    assert best is not None
    return best


def _acquittal_levels(
    labels: np.ndarray,
    general_probs: np.ndarray,
    elf_indices: np.ndarray,
    elf_probs: np.ndarray,
) -> list[dict[str, Any]]:
    return [
        {
            "level": int(target["level"]),
            "hostile": _calibrate_acquittal_one(
                labels,
                general_probs,
                elf_indices,
                elf_probs,
                float(target["hostile_per_million"]),
            ),
        }
        for target in thresholds.SEVERITY_LEVEL_TARGETS
    ]


def _best_l5_l9(levels: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key, level_no in (("l500_hostile", 50), ("l1000_hostile", 100)):
        entry = next((item for item in levels if item["level"] == level_no), None)
        if entry is None:
            continue
        summary[key] = entry["hostile"]
    return summary


def _metrics_from_hit(
    labels: np.ndarray,
    hit: np.ndarray,
    *,
    total_benign: int,
    target_per_million: float,
    thresholds_used: dict[str, float],
) -> dict[str, Any]:
    malware = labels == 1
    benign = labels == 0
    tp = int(np.sum(hit & malware))
    fp = int(np.sum(hit & benign))
    tn = int(np.sum((~hit) & benign))
    fn = int(np.sum((~hit) & malware))
    n_malware = int(np.sum(malware))
    n_benign = int(np.sum(benign))
    precision = tp / max(tp + fp, 1)
    recall = tp / n_malware if n_malware else math.nan
    fpr = fp / n_benign if n_benign else math.nan
    f1 = 2 * precision * recall / max(precision + recall, 1e-12) if n_malware else math.nan
    accuracy = (tp + tn) / max(tp + fp + tn + fn, 1)
    return {
        "target_per_100M": float(target_per_million) * 100.0,
        "thresholds": thresholds_used,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "accuracy": accuracy,
        "fpr": fpr,
        "fp_per_100M": fp * 100_000_000.0 / n_benign if n_benign else math.nan,
        "global_fp_per_million": fp * 1_000_000.0 / total_benign if total_benign else math.nan,
    }


def _calibrate_policy_one(
    labels: np.ndarray,
    route_probs: dict[str, np.ndarray],
    *,
    target_per_million: float,
    total_benign: int,
    primary: str | None,
    allowed_routes: tuple[str, ...],
) -> dict[str, Any]:
    n_rows = len(labels)
    n_benign = int(np.sum(labels == 0))
    max_fp = _budget(n_benign, target_per_million)
    indices = np.arange(n_rows, dtype=np.int64)
    candidates = {
        name: _candidate_thresholds(labels, indices, route_probs[name], max_fp=max_fp)
        for name in allowed_routes
    }
    selected: dict[str, float | None] = {name: None for name in allowed_routes}
    selected_hits: dict[str, np.ndarray] = {
        name: np.zeros(n_rows, dtype=bool)
        for name in allowed_routes
    }
    if primary is not None:
        primary_best = max(candidates[primary], key=lambda item: int(item["tp"] or 0))
        if primary_best["threshold"] is not None:
            selected[primary] = float(primary_best["threshold"])
            selected_hits[primary] = _hit_mask(
                n_rows,
                indices,
                route_probs[primary],
                selected[primary],
            )
    hit_counts = np.zeros(n_rows, dtype=np.uint16)
    for hit in selected_hits.values():
        hit_counts += hit
    benign = labels == 0
    malware = labels == 1
    current_fp = int(np.sum((hit_counts > 0) & benign))
    current_tp = int(np.sum((hit_counts > 0) & malware))
    while True:
        best: tuple[int, int, str, float | None, np.ndarray, np.ndarray] | None = None
        for name, route_candidates in candidates.items():
            old_hit = selected_hits[name]
            for candidate in route_candidates:
                threshold = candidate["threshold"]
                new_hit = _hit_mask(
                    n_rows,
                    indices,
                    route_probs[name],
                    None if threshold is None else float(threshold),
                )
                proposed_counts = hit_counts - old_hit + new_hit
                proposed_hit = proposed_counts > 0
                fp = int(np.sum(proposed_hit & benign))
                if fp > max_fp:
                    continue
                tp = int(np.sum(proposed_hit & malware))
                inc_tp = tp - current_tp
                inc_fp = fp - current_fp
                if inc_tp <= 0:
                    continue
                key = (inc_tp, -max(inc_fp, 0), name, threshold, new_hit, proposed_counts)
                if best is None or key[:2] > best[:2]:
                    best = key
        if best is None:
            break
        _inc_tp, _neg_inc_fp, name, threshold, new_hit, hit_counts = best
        selected[name] = None if threshold is None else float(threshold)
        selected_hits[name] = new_hit
        current_fp = int(np.sum((hit_counts > 0) & benign))
        current_tp = int(np.sum((hit_counts > 0) & malware))

    hit = hit_counts > 0
    return {
        "budget": max_fp,
        **_metrics_from_hit(
            labels,
            hit,
            total_benign=total_benign,
            target_per_million=target_per_million,
            thresholds_used={k: v for k, v in selected.items() if v is not None},
        ),
    }


def _elf_local_levels(
    labels: np.ndarray,
    general_probs: np.ndarray,
    elf_indices: np.ndarray,
    elf_probs: np.ndarray,
) -> list[dict[str, Any]]:
    elf_labels = labels[elf_indices]
    route_probs = {
        "general": general_probs[elf_indices],
        "elf": elf_probs,
    }
    total_benign = int(np.sum(labels == 0))
    return [
        {
            "level": int(target["level"]),
            "hostile": {
                "general_only": _calibrate_policy_one(
                    elf_labels,
                    route_probs,
                    target_per_million=float(target["hostile_per_million"]),
                    total_benign=total_benign,
                    primary="general",
                    allowed_routes=("general",),
                ),
                "elf_only": _calibrate_policy_one(
                    elf_labels,
                    route_probs,
                    target_per_million=float(target["hostile_per_million"]),
                    total_benign=total_benign,
                    primary="elf",
                    allowed_routes=("elf",),
                ),
                "or_general_primary": _calibrate_policy_one(
                    elf_labels,
                    route_probs,
                    target_per_million=float(target["hostile_per_million"]),
                    total_benign=total_benign,
                    primary="general",
                    allowed_routes=("general", "elf"),
                ),
                "specialist_primary": _calibrate_policy_one(
                    elf_labels,
                    route_probs,
                    target_per_million=float(target["hostile_per_million"]),
                    total_benign=total_benign,
                    primary="elf",
                    allowed_routes=("general", "elf"),
                ),
            },
        }
        for target in thresholds.SEVERITY_LEVEL_TARGETS
    ]


def _elf_local_l5_l9(levels: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key, level_no in (("l500_hostile", 50), ("l1000_hostile", 100)):
        entry = next((item for item in levels if item["level"] == level_no), None)
        if entry is None:
            continue
        summary[key] = entry["hostile"]
    return summary


def _train_lgbm_classifier(
    x_train: sp.csr_matrix,
    y_train: np.ndarray,
    *,
    sample_weight: np.ndarray | None,
    seed: int,
) -> lgb.LGBMClassifier:
    n_benign = int(np.sum(y_train == 0))
    n_malware = int(np.sum(y_train == 1))
    clf = lgb.LGBMClassifier(
        objective="binary",
        n_estimators=400,
        max_depth=12,
        learning_rate=0.05,
        num_leaves=96,
        min_child_samples=100,
        colsample_bytree=0.8,
        subsample=0.8,
        scale_pos_weight=n_benign / max(n_malware, 1),
        random_state=seed,
        n_jobs=-1,
        force_col_wise=True,
        verbosity=-1,
    )
    clf.fit(x_train, y_train, sample_weight=sample_weight)
    return clf


def _train_lgbm_regressor(
    x_train: sp.csr_matrix,
    target: np.ndarray,
    *,
    seed: int,
) -> lgb.LGBMRegressor:
    reg = lgb.LGBMRegressor(
        objective="regression",
        n_estimators=400,
        max_depth=12,
        learning_rate=0.05,
        num_leaves=96,
        min_child_samples=100,
        colsample_bytree=0.8,
        subsample=0.8,
        random_state=seed,
        n_jobs=-1,
        force_col_wise=True,
        verbosity=-1,
    )
    reg.fit(x_train, target)
    return reg


def _train_lgbm_ranker(
    x_train: sp.csr_matrix,
    y_train: np.ndarray,
    *,
    seed: int,
) -> lgb.LGBMRanker:
    groups: list[int] = []
    remaining = len(y_train)
    while remaining > 0:
        n = min(5000, remaining)
        groups.append(n)
        remaining -= n
    ranker = lgb.LGBMRanker(
        objective="lambdarank",
        n_estimators=400,
        max_depth=12,
        learning_rate=0.05,
        num_leaves=96,
        min_child_samples=100,
        colsample_bytree=0.8,
        subsample=0.8,
        random_state=seed,
        n_jobs=-1,
        force_col_wise=True,
        verbosity=-1,
    )
    ranker.fit(x_train, y_train.astype(int), group=groups)
    return ranker


def _save_model(estimator: Any, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    export.save_model(estimator, output_dir / "model.txt")


def _score_estimator(estimator: Any, x_matrix: sp.csr_matrix) -> np.ndarray:
    if hasattr(estimator, "predict_proba"):
        return estimator.predict_proba(x_matrix)[:, 1].astype(np.float32)
    return np.asarray(estimator.predict(x_matrix), dtype=np.float32)


def _model_feature_count(estimator: Any) -> int | None:
    if hasattr(estimator, "num_feature"):
        return int(estimator.num_feature())
    if hasattr(estimator, "n_features_in_"):
        return int(estimator.n_features_in_)
    if hasattr(estimator, "n_features_"):
        return int(estimator.n_features_)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--general-scores", type=Path, required=True)
    parser.add_argument("--general-spec", type=Path, required=True)
    parser.add_argument("--teacher-model", type=Path, required=True)
    parser.add_argument("--teacher-spec", type=Path, required=True)
    parser.add_argument("--file-type", default="elf")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("out/models/azoth/elf_experiments"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("out/models/azoth/elf_experiments.json"),
    )
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    general_spec = features.FeatureSpec.load(args.general_spec)
    teacher_spec = features.FeatureSpec.load(args.teacher_spec)
    teacher = model.load_model(args.teacher_model)
    teacher_features = _model_feature_count(teacher)
    if teacher_features is not None and teacher_features != teacher_spec.total_features:
        raise SystemExit(
            "teacher model/spec feature mismatch: "
            f"{args.teacher_model} expects {teacher_features} features, "
            f"but {args.teacher_spec} describes {teacher_spec.total_features}. "
            "Use a deployable specialist bundle, or persist the research sidecar "
            "feature vocabularies into a replayable feature spec.",
        )

    cache = np.load(args.general_scores)
    row_ids = cache["row_ids"].astype(np.int64)
    labels = cache["labels"].astype(np.int8)
    general_probs = cache["probs"].astype(np.float32)
    max_id = int(cache["corpus_requested_max_id"]) or int(cache["corpus_max_row_id"])
    row_index = {int(row_id): idx for idx, row_id in enumerate(row_ids)}
    route_types = tuple(part.strip() for part in str(args.file_type).split(",") if part.strip())
    route_label = "+".join(route_types)
    elf_rows_all = _fetch_rows(args.db, file_types=route_types, max_id=max_id, min_score=None)
    elf_rows = [
        (row_id, label)
        for row_id, label, _is_test, _ft in elf_rows_all
        if row_id in row_index
    ]
    elf_indices = np.asarray([row_index[row_id] for row_id, _label in elf_rows], dtype=np.int64)
    LOG.info("%s calibration rows: %d", route_label.upper(), len(elf_indices))

    train_rows_all = _fetch_rows(
        args.db,
        file_types=route_types,
        max_id=max_id,
        min_score=data.MIN_SAMPLE_SCORE,
    )
    train_rows = _ids_labels(train_rows_all, test=False)
    LOG.info("%s train rows: %d", route_label.upper(), len(train_rows))

    x_train, y_train = _matrix(args.db, train_rows, general_spec, args.workers)
    x_elf, y_elf = _matrix(args.db, elf_rows, general_spec, args.workers)
    x_train_teacher, _ = _matrix(args.db, train_rows, teacher_spec, args.workers)
    x_elf_teacher, _ = _matrix(args.db, elf_rows, teacher_spec, args.workers)

    teacher_train = predict_proba(teacher, x_train_teacher)
    teacher_elf = predict_proba(teacher, x_elf_teacher)

    experiments: list[dict[str, Any]] = []
    baseline_levels = _general_baseline(labels, general_probs)
    experiments.append(
        {
            "name": "general_baseline",
            "deployable": True,
            "rules": {"general": baseline_levels},
            "summary": _best_l5_l9(baseline_levels),
            "elf_local": _elf_local_l5_l9(
                _elf_local_levels(labels, general_probs, elf_indices, general_probs[elf_indices]),
            ),
        },
    )

    teacher_rules = {
        "or": _or_levels(labels, general_probs, elf_indices, teacher_elf),
        "replacement": _replacement_levels(labels, general_probs, elf_indices, teacher_elf),
        "acquittal": _acquittal_levels(labels, general_probs, elf_indices, teacher_elf),
    }
    experiments.append(
        {
            "name": "custom_teacher_upper_bound",
            "deployable": False,
            "rules": teacher_rules,
            "summary": {rule: _best_l5_l9(levels) for rule, levels in teacher_rules.items()},
            "elf_local": _elf_local_l5_l9(
                _elf_local_levels(labels, general_probs, elf_indices, teacher_elf),
            ),
        },
    )

    # Tail contrast: emphasize ELF malware that general scores below L50
    # hostile (= 0.5 FP/M, today's dense headline) and benign ELF in the
    # high general-score tail.
    general_l50_entry = next(
        (item for item in baseline_levels if item["level"] == 50), None,
    )
    if general_l50_entry is None:
        raise RuntimeError("L50 missing from baseline levels; cannot derive tail-contrast threshold")
    general_l500 = general_l50_entry["hostile"]
    l500_threshold = float(general_l500["thresholds"]["general"])
    train_global_indices = np.asarray(
        [row_index[row_id] for row_id, _label in train_rows if row_id in row_index],
        dtype=np.int64,
    )
    weights = np.ones(len(y_train), dtype=np.float32)
    if len(train_global_indices) == len(y_train):
        train_general_scores = general_probs[train_global_indices]
        hard_pos = (y_train == 1) & (train_general_scores < l500_threshold)
        hard_neg_cut = np.quantile(train_general_scores[y_train == 0], 0.995)
        hard_neg = (y_train == 0) & (train_general_scores >= hard_neg_cut)
        weights[hard_pos] = 8.0
        weights[hard_neg] = 12.0
    tail = _train_lgbm_classifier(x_train, y_train, sample_weight=weights, seed=args.seed)
    _save_model(tail, args.output_dir / "tail_contrast")
    tail_elf = _score_estimator(tail, x_elf)
    tail_rules = {
        "or": _or_levels(labels, general_probs, elf_indices, tail_elf),
        "replacement": _replacement_levels(labels, general_probs, elf_indices, tail_elf),
        "acquittal": _acquittal_levels(labels, general_probs, elf_indices, tail_elf),
    }
    experiments.append(
        {
            "name": "tail_contrast",
            "deployable": True,
            "rules": tail_rules,
            "summary": {rule: _best_l5_l9(levels) for rule, levels in tail_rules.items()},
            "elf_local": _elf_local_l5_l9(
                _elf_local_levels(labels, general_probs, elf_indices, tail_elf),
            ),
        },
    )

    distill_target = np.clip(0.35 * y_train + 0.65 * teacher_train, 0.0, 1.0)
    distill = _train_lgbm_regressor(x_train, distill_target, seed=args.seed)
    _save_model(distill, args.output_dir / "teacher_distill")
    distill_elf = np.clip(_score_estimator(distill, x_elf), 0.0, 1.0)
    distill_rules = {
        "or": _or_levels(labels, general_probs, elf_indices, distill_elf),
        "replacement": _replacement_levels(labels, general_probs, elf_indices, distill_elf),
        "acquittal": _acquittal_levels(labels, general_probs, elf_indices, distill_elf),
    }
    experiments.append(
        {
            "name": "teacher_distill",
            "deployable": True,
            "rules": distill_rules,
            "summary": {rule: _best_l5_l9(levels) for rule, levels in distill_rules.items()},
            "elf_local": _elf_local_l5_l9(
                _elf_local_levels(labels, general_probs, elf_indices, distill_elf),
            ),
        },
    )

    ranker = _train_lgbm_ranker(x_train, y_train, seed=args.seed)
    _save_model(ranker, args.output_dir / "ranker")
    ranker_elf = _score_estimator(ranker, x_elf)
    ranker_rules = {
        "or": _or_levels(labels, general_probs, elf_indices, ranker_elf),
        "replacement": _replacement_levels(labels, general_probs, elf_indices, ranker_elf),
        "acquittal": _acquittal_levels(labels, general_probs, elf_indices, ranker_elf),
    }
    experiments.append(
        {
            "name": "ranker",
            "deployable": True,
            "rules": ranker_rules,
            "summary": {rule: _best_l5_l9(levels) for rule, levels in ranker_rules.items()},
            "elf_local": _elf_local_l5_l9(
                _elf_local_levels(labels, general_probs, elf_indices, ranker_elf),
            ),
        },
    )

    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "max_id": max_id,
        "rows": int(len(labels)),
        "malware": int(np.sum(labels == 1)),
        "benign": int(np.sum(labels == 0)),
        "file_type": route_label,
        "route_rows": int(len(elf_indices)),
        "elf_rows": int(len(elf_indices)),
        "experiments": experiments,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"wrote {args.output}")
    for exp in experiments:
        if exp["name"] == "general_baseline":
            h = exp["summary"]["l500_hostile"]
            print(f"{exp['name']}: L500 hostile {h['recall']:.2%} @ {h['fp']} FP")
            continue
        for rule, summary in exp["summary"].items():
            h = summary["l500_hostile"]
            print(f"{exp['name']} {rule}: L500 hostile {h['recall']:.2%} @ {h['fp']} FP")
        local = exp.get("elf_local", {}).get("l500_hostile", {})
        if local:
            best_policy = max(local.items(), key=lambda item: (item[1]["recall"], -item[1]["fp"]))
            print(
                f"{exp['name']} {route_label}-local {best_policy[0]}: "
                f"L5 hostile {best_policy[1]['recall']:.2%} @ {best_policy[1]['fp']} {route_label} FP "
                f"(F1 {best_policy[1]['f1']:.2%}, acc {best_policy[1]['accuracy']:.2%})",
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
