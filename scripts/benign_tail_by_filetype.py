from __future__ import annotations

import argparse
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

import numpy as np

from collimator import data
from collimator.features import FeatureSpec, extract, primary_file, standardize
from collimator.model import load_model, predict_proba


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize held-out benign score tails by primary file type.",
    )
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--threshold", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=2048)
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument("--limit-benign", type=int, default=0)
    return parser.parse_args()


def summarize_scores(scores: list[float], threshold: float) -> dict[str, float | int | None]:
    arr = np.asarray(scores, dtype=np.float32)
    return {
        "count": int(arr.size),
        "max_score": float(arr.max(initial=0.0)),
        "mean_score": float(arr.mean()) if arr.size else 0.0,
        "p99": float(np.quantile(arr, 0.99)) if arr.size else 0.0,
        "p999": float(np.quantile(arr, 0.999)) if arr.size >= 1000 else None,
        "above_threshold": int(np.sum(arr > threshold)),
    }


def main() -> None:
    args = parse_args()

    spec = FeatureSpec.load(args.spec)
    model = load_model(args.model)

    by_type: dict[str, list[float]] = defaultdict(list)
    benign_count = 0
    batch_reports: list[dict[str, object]] = []
    batch_types: list[str] = []

    def flush() -> None:
        nonlocal benign_count
        if not batch_reports:
            return
        X = np.vstack([extract(report, spec) for report in batch_reports])
        if spec.standardized:
            X = standardize(X, spec)
        probs = predict_proba(model, X)
        for file_type, prob in zip(batch_types, probs, strict=False):
            by_type[file_type].append(float(prob))
        benign_count += len(batch_reports)
        batch_reports.clear()
        batch_types.clear()

    conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    try:
        placeholders = ",".join("?" for _ in data.BENIGN_STATUSES)
        query = (
            "SELECT s.cleave_json "
            "FROM samples s "
            "JOIN collimator_sample_splits ss ON ss.sample_row_id = s.id "
            f"WHERE ss.is_test = 1 AND s.status IN ({placeholders})"
        )
        for (cleave_json,) in conn.execute(query, tuple(sorted(data.BENIGN_STATUSES))):
            if not cleave_json:
                continue
            try:
                report = json.loads(cleave_json)
            except json.JSONDecodeError:
                continue
            file_type = str(primary_file(report).get("file_type") or "unknown")
            batch_reports.append(report)
            batch_types.append(file_type)
            if len(batch_reports) >= args.batch_size:
                flush()
                if benign_count and benign_count % 10000 == 0:
                    print(f"processed_benign={benign_count}", flush=True)
            if args.limit_benign > 0 and benign_count + len(batch_reports) >= args.limit_benign:
                batch_reports[:] = batch_reports[: max(args.limit_benign - benign_count, 0)]
                batch_types[:] = batch_types[: max(args.limit_benign - benign_count, 0)]
                break
    finally:
        conn.close()
    flush()

    summary: list[dict[str, object]] = []
    for file_type, scores in by_type.items():
        row: dict[str, object] = {"file_type": file_type}
        row.update(summarize_scores(scores, args.threshold))
        summary.append(row)

    summary.sort(
        key=lambda row: (row["max_score"], row["p99"], row["count"]),
        reverse=True,
    )
    output = {
        "threshold": args.threshold,
        "benign_test_count": benign_count,
        "file_types": summary,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2))

    print(f"wrote {args.output}")
    print(
        f"benign_test_count={benign_count} "
        f"threshold={args.threshold:.6f} file_types={len(summary)}",
    )
    print("top_by_max_score:")
    for row in summary[: args.top_n]:
        p999 = row["p999"]
        p999_display = "n/a" if p999 is None else f"{float(p999):.6f}"
        print(
            f"{str(row['file_type']):<24} count={int(row['count']):<6d} "
            f"max={float(row['max_score']):.6f} p99={float(row['p99']):.6f} "
            f"p999={p999_display} above={int(row['above_threshold'])}",
        )

    print("top_by_above_threshold:")
    for row in sorted(
        summary,
        key=lambda item: (item["above_threshold"], item["max_score"]),
        reverse=True,
    )[: args.top_n]:
        print(
            f"{str(row['file_type']):<24} count={int(row['count']):<6d} "
            f"above={int(row['above_threshold']):<4d} "
            f"max={float(row['max_score']):.6f} p99={float(row['p99']):.6f}",
        )


if __name__ == "__main__":
    main()
