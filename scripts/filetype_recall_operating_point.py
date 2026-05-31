#!/usr/bin/env python3
"""Compute per-filetype thresholds for requested malware recall targets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from filetype_metric_matrix import _fetch_file_types


def _operating_point(y: np.ndarray, probs: np.ndarray, recall_target: float) -> dict[str, float | int]:
    malware_probs = np.sort(probs[y == 1])[::-1]
    if malware_probs.size == 0:
        raise ValueError("no malware samples for selected file type")
    required_tp = int(np.ceil(recall_target * malware_probs.size))
    required_tp = min(max(required_tp, 1), malware_probs.size)
    threshold = float(malware_probs[required_tp - 1])
    pred = probs >= threshold
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    fp = int(np.sum((y == 0) & pred))
    tp = int(np.sum((y == 1) & pred))
    tn = int(np.sum((y == 0) & ~pred))
    fn = int(np.sum((y == 1) & ~pred))
    return {
        "target_recall": float(recall_target),
        "threshold": threshold,
        "actual_recall": float(tp / malware) if malware else 0.0,
        "precision": float(tp / (tp + fp)) if tp + fp else 1.0,
        "fp": fp,
        "tp": tp,
        "tn": tn,
        "fn": fn,
        "benign": benign,
        "malware": malware,
        "fp_per_100M": float(fp * 100_000_000 / benign) if benign else 0.0,
        "fpr": float(fp / benign) if benign else 0.0,
    }


def _fp_per_million_operating_point(y: np.ndarray, probs: np.ndarray, fp_per_million: float) -> dict[str, float | int]:
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    if benign <= 0:
        raise ValueError("no benign samples for selected file type")
    budget = int(np.floor(benign * fp_per_million / 1_000_000))
    if fp_per_million > 0:
        budget = max(1, budget)
    benign_probs = np.sort(probs[y == 0])[::-1]
    if budget <= 0:
        threshold = float(np.nextafter(float(benign_probs[0]), np.inf)) if benign_probs.size else 1.0
    elif budget >= benign_probs.size:
        threshold = float(benign_probs[-1])
    else:
        threshold = float(benign_probs[budget - 1])
    pred = probs >= threshold
    fp = int(np.sum((y == 0) & pred))
    tp = int(np.sum((y == 1) & pred))
    tn = int(np.sum((y == 0) & ~pred))
    fn = int(np.sum((y == 1) & ~pred))
    return {
        # `fp_per_million` is in per-million units (input convention); emit
        # as the canonical per-100M output.
        "target_fp_per_100M": float(fp_per_million) * 100.0,
        "max_fp_budget": int(budget),
        "threshold": threshold,
        "actual_recall": float(tp / malware) if malware else 0.0,
        "precision": float(tp / (tp + fp)) if tp + fp else 1.0,
        "fp": fp,
        "tp": tp,
        "tn": tn,
        "fn": fn,
        "benign": benign,
        "malware": malware,
        "fp_per_100M": float(fp * 100_000_000 / benign),
        "fpr": float(fp / benign),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--scores-cache", required=True, type=Path)
    parser.add_argument("--file-type", required=True)
    parser.add_argument("--recall", action="append", type=float, default=[])
    parser.add_argument("--fp-per-million", action="append", type=float, default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    arrays = np.load(args.scores_cache, allow_pickle=False)
    row_ids = arrays["row_ids"].astype(np.int64)
    labels = arrays["labels"].astype(np.int8)
    probs = arrays["probs"].astype(np.float32)
    file_types_by_id = _fetch_file_types(args.db, row_ids)
    file_types = np.asarray([file_types_by_id.get(int(row_id), "unknown") for row_id in row_ids], dtype=object)

    mask = file_types == args.file_type
    if not np.any(mask):
        raise ValueError(f"no samples for file_type={args.file_type!r}")
    y = labels[mask]
    p = probs[mask]
    result = {
        "scores_cache": str(args.scores_cache),
        "file_type": args.file_type,
        "samples": int(mask.sum()),
        "malware": int(np.sum(y == 1)),
        "benign": int(np.sum(y == 0)),
        "recall_operating_points": [_operating_point(y, p, recall) for recall in args.recall],
        "fp_per_million_operating_points": [
            _fp_per_million_operating_point(y, p, fp_per_million)
            for fp_per_million in args.fp_per_million
        ],
    }
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2))
        print(f"wrote {args.output}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
