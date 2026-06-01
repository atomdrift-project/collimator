#!/usr/bin/env python3
"""Train binary/ELF specialist models and benchmark them on ELF test samples."""

from __future__ import annotations

import argparse
import json
import logging
import math
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from collimator import data, export, features, model, thresholds, train

LOG = logging.getLogger("elf_model_benchmark")
NATIVE_BINARY_TYPES = ("elf", "macho", "pe")


def _label_int(label: str) -> int:
    return 1 if label == "bad" else 0


def _fetch_rows(
    db_path: Path | str,
    *,
    file_types: tuple[str, ...],
    max_id: int,
    min_score: int | None,
) -> list[tuple[int, int, bool, str]]:
    """Return row_id, label, is_test, file_type for labeled samples."""
    where = [
        "label IN ('bad', 'good')",
        "cleave_result IS NOT NULL",
        "skip = ''",
    ]
    params: list[Any] = []
    if max_id > 0:
        where.append("id <= %s" if data._is_pg(db_path) else "id <= ?")  # noqa: SLF001
        params.append(int(max_id))
    if min_score is not None:
        where.append("score >= %s" if data._is_pg(db_path) else "score >= ?")  # noqa: SLF001
        params.append(int(min_score))

    rows: list[tuple[int, int, bool, str]] = []
    with data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if data._is_pg(db_path):  # noqa: SLF001
            where.append("file_type = ANY(%s)")
            params.append(list(file_types))
            select = (
                "SELECT id, sha256, label, canonical_sha256, "
                "COALESCE(NULLIF(file_type, ''), 'unknown')"
            )
            query = (
                select
                + " FROM samples WHERE "
                + " AND ".join(where)
                + " ORDER BY id"
            )
            with conn.cursor() as cur:
                cur.execute(query, params)
                iterable = cur
                for row_id, sha256, label, canonical, file_type in iterable:
                    split_key = canonical or sha256
                    rows.append(
                        (
                            int(row_id),
                            _label_int(str(label)),
                            data.is_test_sample(split_key),
                            str(file_type),
                        ),
                    )
        else:
            placeholders = ",".join("?" for _ in file_types)
            where.append(f"file_type IN ({placeholders})")
            params.extend(file_types)
            select = (
                "SELECT id, sha256, label, canonical_sha256, "
                "COALESCE(NULLIF(file_type, ''), 'unknown')"
            )
            query = (
                select
                + " FROM samples WHERE "
                + " AND ".join(where)
                + " ORDER BY id"
            )
            for row_id, sha256, label, canonical, file_type in conn.execute(query, params):
                split_key = canonical or sha256
                rows.append(
                    (
                        int(row_id),
                        _label_int(str(label)),
                        data.is_test_sample(split_key),
                        str(file_type),
                    ),
                )
    return rows


def _ids_labels(
    rows: list[tuple[int, int, bool, str]],
    *,
    test: bool | None = None,
) -> list[tuple[int, int]]:
    return [
        (row_id, label)
        for row_id, label, is_test, _ft in rows
        if test is None or is_test == test
    ]


def _file_types(rows: list[tuple[int, int, bool, str]], *, test: bool | None = None) -> np.ndarray:
    return np.asarray(
        [
            ft
            for _row_id, _label, is_test, ft in rows
            if test is None or is_test == test
        ],
        dtype=object,
    )


def _matrix_for_rows(
    db_path: Path | str,
    ids_labels: list[tuple[int, int]],
    spec: features.FeatureSpec,
    *,
    workers: int,
) -> tuple[sp.csr_matrix, np.ndarray]:
    batches = list(
        features.extract_labeled_from_db_batches(
            db_path,
            ids_labels,
            spec,
            n_workers=workers,
        ),
    )
    if not batches:
        empty_x = sp.csr_matrix((0, spec.total_features), dtype=np.float32)
        return empty_x, np.asarray([], dtype=np.float32)
    x_matrix = sp.vstack([batch[0] for batch in batches], format="csr")
    y_values = np.concatenate([batch[1] for batch in batches])
    return x_matrix, y_values


def _classification_metrics(y_true: np.ndarray, y_prob: np.ndarray) -> dict[str, float]:
    if len(y_true) == 0:
        return {}
    precision, recall, thresholds = _precision_recall_curve(y_true, y_prob)
    f1_values = np.divide(
        2.0 * precision * recall,
        precision + recall,
        out=np.zeros_like(precision),
        where=(precision + recall) > 0,
    )
    best_idx = int(np.argmax(f1_values))
    best_threshold = 1.0 if best_idx >= len(thresholds) else float(thresholds[best_idx])
    y_pred = (y_prob >= best_threshold).astype(int)
    result = {
        "roc_auc": (
            float(roc_auc_score(y_true, y_prob))
            if len(np.unique(y_true)) > 1
            else math.nan
        ),
        "avg_precision": (
            float(average_precision_score(y_true, y_prob))
            if len(np.unique(y_true)) > 1
            else math.nan
        ),
        "max_f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "max_f1_threshold": best_threshold,
        "precision_at_max_f1": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall_at_max_f1": float(recall_score(y_true, y_pred, zero_division=0)),
    }
    return result


def _precision_recall_curve(
    y_true: np.ndarray,
    y_prob: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    from sklearn.metrics import precision_recall_curve

    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    return precision, recall, thresholds


def _fp_budget(n_benign: int, target_per_million: float) -> int:
    if target_per_million <= 0:
        return 0
    return min(n_benign, max(1, int(math.floor((n_benign * target_per_million) / 1_000_000.0))))


def _operating_point(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    target_per_million: float,
) -> dict[str, float | int | None]:
    benign = y_true == 0
    malware = y_true == 1
    n_benign = int(np.sum(benign))
    n_malware = int(np.sum(malware))
    budget = _fp_budget(n_benign, target_per_million)
    order = np.argsort(-y_prob, kind="mergesort")
    sorted_y = y_true[order]
    sorted_p = y_prob[order]
    tp_cum = np.cumsum(sorted_y == 1)
    fp_cum = np.cumsum(sorted_y == 0)

    best: dict[str, float | int | None] | None = None
    idx = 0
    while idx < len(sorted_p):
        threshold = sorted_p[idx]
        end = idx
        while end + 1 < len(sorted_p) and sorted_p[end + 1] == threshold:
            end += 1
        fp = int(fp_cum[end])
        if fp <= budget:
            tp = int(tp_cum[end])
            best = {
                "threshold": float(threshold),
                "recall": float(tp / n_malware) if n_malware else math.nan,
                "precision": float(tp / max(tp + fp, 1)),
                "fp": fp,
                "tp": tp,
                "fn": n_malware - tp,
                "tn": n_benign - fp,
                "fp_per_100M": float(fp * 100_000_000.0 / n_benign) if n_benign else math.nan,
            }
        else:
            break
        idx = end + 1

    if best is None:
        return {
            "target_per_100M": float(target_per_million) * 100.0,
            "budget": budget,
            "threshold": None,
            "recall": None,
            "precision": None,
            "fp": None,
            "tp": None,
            "fn": None,
            "tn": None,
            "fp_per_100M": None,
        }
    best["target_per_100M"] = float(target_per_million) * 100.0
    best["budget"] = budget
    return best


def _level_table(y_true: np.ndarray, y_prob: np.ndarray) -> list[dict[str, Any]]:
    levels: list[dict[str, Any]] = []
    for target in thresholds.SEVERITY_LEVEL_TARGETS:
        level = int(target["level"])
        hostile = _operating_point(y_true, y_prob, float(target["hostile_per_million"]))
        levels.append({"level": level, "hostile": hostile})
    return levels


def _score_model(
    name: str,
    model_path: Path,
    spec_path: Path,
    db_path: Path | str,
    benchmark_ids_labels: list[tuple[int, int]],
    *,
    workers: int,
) -> dict[str, Any]:
    LOG.info("scoring %s on %d ELF benchmark rows", name, len(benchmark_ids_labels))
    spec = features.FeatureSpec.load(spec_path)
    clf = model.load_model(model_path)
    x_matrix, y = _matrix_for_rows(db_path, benchmark_ids_labels, spec, workers=workers)
    probs = model.predict_proba(clf, x_matrix)
    metrics = _classification_metrics(y, probs)
    return {
        "name": name,
        "model_path": str(model_path),
        "spec_path": str(spec_path),
        "rows": int(len(y)),
        "malware": int(np.sum(y == 1)),
        "benign": int(np.sum(y == 0)),
        "metrics": metrics,
        "levels": _level_table(y, probs),
    }


def _train_specialist(
    name: str,
    db_path: Path | str,
    train_rows: list[tuple[int, int, bool, str]],
    benchmark_ids_labels: list[tuple[int, int]],
    output_dir: Path,
    config: train.TrainConfig,
    *,
    workers: int,
) -> dict[str, Any]:
    train_ids_labels = _ids_labels(train_rows, test=False)
    sample_file_types = _file_types(train_rows, test=False)
    LOG.info("%s: building vocabulary from %d rows", name, len(train_ids_labels))
    spec = features.build_vocab_from_db(db_path, train_ids_labels, n_workers=workers)
    LOG.info("%s: extracting train and ELF benchmark features", name)
    x_train, y_train, x_bench, y_bench = features.extract_partitioned_from_db(
        db_path,
        train_ids_labels,
        benchmark_ids_labels,
        spec,
        n_workers=workers,
    )
    LOG.info("%s: training", name)
    result = train.train(
        x_train,
        y_train,
        config,
        feature_names=spec.feature_names,
        sample_file_types=sample_file_types,
    )
    spec.feature_means = result.feature_means
    spec.feature_stds = result.feature_stds
    output_dir.mkdir(parents=True, exist_ok=True)
    spec.save(output_dir / "feature_spec.json")
    export.save_model(result.model, output_dir / "model.txt")
    probs = model.predict_proba(result.model, x_bench)
    payload = {
        "name": name,
        "output_dir": str(output_dir),
        "model_path": str(output_dir / "model.txt"),
        "spec_path": str(output_dir / "feature_spec.json"),
        "train_rows": int(len(y_train)),
        "train_malware": int(np.sum(y_train == 1)),
        "train_benign": int(np.sum(y_train == 0)),
        "rows": int(len(y_bench)),
        "malware": int(np.sum(y_bench == 1)),
        "benign": int(np.sum(y_bench == 0)),
        "n_features": int(spec.total_features),
        "train_metrics": result.metrics,
        "metrics": _classification_metrics(y_bench, probs),
        "levels": _level_table(y_bench, probs),
        "train_config": asdict(config),
    }
    with open(output_dir / "elf_benchmark.json", "w") as f:
        json.dump(payload, f, indent=2)
    return payload


def _print_summary(results: list[dict[str, Any]]) -> None:
    print("\nELF benchmark")
    print(
        f"{'model':<24} {'AUC':>8} {'AP':>8} {'F1':>8} "
        f"{'L5 H Rec':>9} {'L5 H FP/1M':>11}",
    )
    for res in results:
        metrics = res["metrics"]
        l5 = res["levels"][5]
        h = l5["hostile"]
        print(
            f"{res['name']:<24} "
            f"{metrics.get('roc_auc', math.nan):>8.4f} "
            f"{metrics.get('avg_precision', math.nan):>8.4f} "
            f"{metrics.get('max_f1', math.nan):>8.4f} "
            f"{(h['recall'] if h['recall'] is not None else math.nan):>9.2%} "
            f"{(h['fp_per_100M'] if h['fp_per_100M'] is not None else math.nan):>11.1f}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--output", type=Path, default=Path("out/models/elf_model_benchmark.json"))
    parser.add_argument("--general-model", type=Path, required=True)
    parser.add_argument("--general-spec", type=Path, required=True)
    parser.add_argument(
        "--binary-output",
        type=Path,
        default=Path("out/models/azoth-binary-cpu"),
    )
    parser.add_argument("--elf-output", type=Path, default=Path("out/models/azoth-elf-cpu"))
    parser.add_argument("--max-id", type=int, default=0)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-folds", type=int, default=2)
    parser.add_argument("--n-estimators", type=int, default=400)
    parser.add_argument("--max-depth", type=int, default=12)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--early-stopping-rounds", type=int, default=50)
    parser.add_argument("--num-leaves", type=int, default=96)
    parser.add_argument("--min-child-samples", type=int, default=100)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    max_id = args.max_id or data.snapshot_max_id(args.db)
    LOG.info("snapshot max_id=%d", max_id)

    trainable_binary_rows = _fetch_rows(
        args.db,
        file_types=NATIVE_BINARY_TYPES,
        max_id=max_id,
        min_score=data.MIN_SAMPLE_SCORE,
    )
    trainable_elf_rows = [row for row in trainable_binary_rows if row[3] == "elf"]
    full_elf_rows = _fetch_rows(args.db, file_types=("elf",), max_id=max_id, min_score=None)
    benchmark_ids_labels = _ids_labels(full_elf_rows, test=True)
    if not benchmark_ids_labels:
        raise SystemExit("no ELF benchmark rows found")

    LOG.info(
        "rows: binary trainable=%d, ELF trainable=%d, full ELF benchmark=%d",
        len(trainable_binary_rows),
        len(trainable_elf_rows),
        len(benchmark_ids_labels),
    )
    config = train.TrainConfig(
        learner="azoth",
        seed=args.seed,
        device=args.device,
        n_folds=args.n_folds,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        learning_rate=args.learning_rate,
        early_stopping_rounds=args.early_stopping_rounds,
        num_leaves=args.num_leaves,
        min_child_samples=args.min_child_samples,
        beta=1.25,
    )
    results = [
        _score_model(
            "general",
            args.general_model,
            args.general_spec,
            args.db,
            benchmark_ids_labels,
            workers=args.workers,
        ),
        _train_specialist(
            "binary-filegroup",
            args.db,
            trainable_binary_rows,
            benchmark_ids_labels,
            args.binary_output,
            config,
            workers=args.workers,
        ),
        _train_specialist(
            "elf-specific",
            args.db,
            trainable_elf_rows,
            benchmark_ids_labels,
            args.elf_output,
            config,
            workers=args.workers,
        ),
    ]
    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "db": str(args.db),
        "max_id": max_id,
        "native_binary_types": list(NATIVE_BINARY_TYPES),
        "benchmark": "full labeled ELF test partition, including low-score samples",
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(payload, f, indent=2)
    _print_summary(results)
    LOG.info("wrote %s", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
