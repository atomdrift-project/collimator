#!/usr/bin/env python3
"""Build per-filetype metric tables from a threshold score cache."""

from __future__ import annotations

import argparse
import csv
import json
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score

from collimator import data


def _chunks(values: list[int], size: int) -> list[list[int]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


def _fetch_file_types(db_path: Path | str, row_ids: np.ndarray, chunk_size: int = 10_000) -> dict[int, str]:
    ids = [int(row_id) for row_id in row_ids]
    file_types: dict[int, str] = {}
    attempts = 5
    for attempt in range(1, attempts + 1):
        try:
            with data._connect(db_path) as conn:  # noqa: SLF001
                if data._is_pg(db_path):  # noqa: SLF001
                    with conn.cursor() as cur:
                        for chunk in _chunks(ids, chunk_size):
                            cur.execute(
                                "SELECT id, COALESCE(NULLIF(file_type, ''), 'unknown') "
                                "FROM samples WHERE id = ANY(%s)",
                                [chunk],
                            )
                            file_types.update({int(row_id): str(file_type or "unknown") for row_id, file_type in cur})
                else:
                    for chunk in _chunks(ids, chunk_size):
                        placeholders = ",".join("?" for _ in chunk)
                        query = f"SELECT id, COALESCE(NULLIF(file_type, ''), 'unknown') FROM samples WHERE id IN ({placeholders})"  # noqa: S608
                        file_types.update({int(row_id): str(file_type or "unknown") for row_id, file_type in conn.execute(query, chunk)})
            break
        except Exception:
            if attempt == attempts:
                raise
            time.sleep(float(attempt))
    return file_types


def _thresholds_from_tuning(path: Path | None) -> dict[str, float]:
    if path is None or not path.exists():
        return {}
    payload = json.loads(path.read_text())
    thresholds: dict[str, float] = {}
    for level in payload.get("severity_levels", []):
        level_number = int(level["level"])
        for severity in ("hostile", "suspicious"):
            metric = level.get(severity)
            if isinstance(metric, dict) and metric.get("threshold") is not None:
                thresholds[f"{severity}_l{level_number}"] = float(metric["threshold"])
    return thresholds


def _threshold_metrics(y: np.ndarray, probs: np.ndarray, threshold: float) -> dict[str, float | int]:
    pred = probs >= threshold
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    fp = int(np.sum((y == 0) & pred))
    tp = int(np.sum((y == 1) & pred))
    fn = int(np.sum((y == 1) & ~pred))
    tn = int(np.sum((y == 0) & ~pred))
    return {
        "threshold": float(threshold),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "fp": fp,
        "tp": tp,
        "tn": tn,
        "fn": fn,
        "fp_per_million": float(fp * 1_000_000 / benign) if benign else None,
        "malware_recall": float(tp / malware) if malware else None,
    }


def _base_metrics(y: np.ndarray, probs: np.ndarray) -> dict[str, float | None]:
    if len(np.unique(y)) < 2:
        return {"roc_auc": None, "avg_precision": None}
    return {
        "roc_auc": float(roc_auc_score(y, probs)),
        "avg_precision": float(average_precision_score(y, probs)),
    }


def build_matrix(
    *,
    db_path: Path | str,
    scores_cache: Path,
    thresholds_path: Path | None,
    min_count: int,
) -> dict[str, Any]:
    arrays = np.load(scores_cache, allow_pickle=False)
    row_ids = arrays["row_ids"].astype(np.int64)
    labels = arrays["labels"].astype(np.int8)
    probs = arrays["probs"].astype(np.float32)
    file_types_by_id = _fetch_file_types(db_path, row_ids)
    file_types = np.asarray([file_types_by_id.get(int(row_id), "unknown") for row_id in row_ids], dtype=object)
    thresholds = _thresholds_from_tuning(thresholds_path)

    rows: list[dict[str, Any]] = []
    counts = Counter(str(file_type) for file_type in file_types)
    for file_type, count in sorted(counts.items()):
        if count < min_count:
            continue
        mask = file_types == file_type
        y = labels[mask]
        p = probs[mask]
        benign = int(np.sum(y == 0))
        malware = int(np.sum(y == 1))
        row: dict[str, Any] = {
            "file_type": file_type,
            "samples": int(count),
            "malware": malware,
            "benign": benign,
        }
        row.update(_base_metrics(y, p))
        for name, threshold in thresholds.items():
            metrics = _threshold_metrics(y, p, threshold)
            for metric_name, value in metrics.items():
                row[f"{name}_{metric_name}"] = value
        rows.append(row)

    rows.sort(
        key=lambda row: (
            float(row.get("hostile_l5_fp_per_million") or 0.0),
            int(row.get("benign") or 0),
            int(row.get("samples") or 0),
        ),
        reverse=True,
    )
    return {
        "scores_cache": str(scores_cache),
        "thresholds": thresholds,
        "corpus": {
            "samples": int(len(labels)),
            "malware": int(np.sum(labels == 1)),
            "benign": int(np.sum(labels == 0)),
            "file_types": len(counts),
            "reported_file_types": len(rows),
            "min_count": int(min_count),
        },
        "file_types": rows,
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    parser.add_argument("--scores-cache", required=True, type=Path)
    parser.add_argument("--thresholds", type=Path, default=None)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--csv-output", type=Path, default=None)
    parser.add_argument("--min-count", type=int, default=25)
    parser.add_argument("--top", type=int, default=25)
    args = parser.parse_args()

    payload = build_matrix(
        db_path=args.db,
        scores_cache=args.scores_cache,
        thresholds_path=args.thresholds,
        min_count=args.min_count,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2))
    if args.csv_output is not None:
        _write_csv(args.csv_output, payload["file_types"])

    print(f"wrote {args.output}")
    if args.csv_output is not None:
        print(f"wrote {args.csv_output}")
    print(
        "corpus: "
        f"{payload['corpus']['samples']} samples, "
        f"{payload['corpus']['reported_file_types']} reported file types"
    )
    print("top hostile_l5 fp_per_million:")
    for row in payload["file_types"][: args.top]:
        fp_rate = row.get("hostile_l5_fp_per_million")
        auc = row.get("roc_auc")
        f1 = row.get("hostile_l5_f1")
        print(
            f"  {row['file_type']:<24} n={row['samples']:<7} "
            f"benign={row['benign']:<7} malware={row['malware']:<7} "
            f"auc={'n/a' if auc is None else f'{auc:.4f}'} "
            f"h_l5_f1={'n/a' if f1 is None else f'{f1:.4f}'} "
            f"h_l5_fp1m={'n/a' if fp_rate is None else f'{fp_rate:.1f}'}"
        )


if __name__ == "__main__":
    main()
