"""Show confidence thresholds required for various accuracy levels."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from itertools import islice
from pathlib import Path
from typing import Any

import numpy as np

from . import data, features, train
from .model import load_model, predict_proba

log = logging.getLogger(__name__)

ACCURACY_TARGETS = [0.80, 0.90, 0.95, 0.98, 0.99, 0.993, 0.996, 0.998, 0.999, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995, 0.9996, 0.9997, 0.9998, 0.9999, 0.99999]

# (label, max FPR): lowest threshold (highest recall) meeting the FPR ceiling.
# Used by `compute_recommendations` (legacy FPR-based mode).
RECOMMENDATIONS = [
    ("suspicious", 0.00002),   # FPR ≤ 20 per million
    ("hostile",    0.000001),  # FPR ≤ 1 per million
]

# Minimum benign samples needed to trust an FPR target (expect ≥5 FP at that rate).
MIN_SAMPLES_FOR_FPR = 5

# (label, min precision): lowest threshold (highest recall) where precision
# (TP / (TP+FP)) on the test set meets or exceeds the floor.
# Used by `compute_precision_recommendations` (legacy, not the default).
PRECISION_RECOMMENDATIONS = [
    ("suspicious", 0.995),
    ("hostile",    0.9995),
]

# Minimum number of flagged samples required before a precision number is
# trustworthy. Avoids picking a threshold based on 1-2 samples.
MIN_FLAGGED_FOR_PRECISION = 50

# Recall-floor + aspirational FPR targets.
# Used by `compute_recall_fpr_recommendations` (the default since v16).
#
# Each entry: (label, min_recall, aspirational_fpr_per_million)
#   - Always guarantees at least min_recall.
#   - If the benign pool is large enough to measure the FPR target,
#     tightens the threshold to meet it (as long as recall stays above floor).
#   - As data grows, thresholds naturally tighten toward the FPR target.
#
# Intuition:
#   suspicious: "unusual, take a look" — catch ≥95% of malware
#   hostile:    "must look NOW"        — catch ≥80%, very few false alarms
RECALL_FPR_RECOMMENDATIONS = [
    ("suspicious", 0.95, 500),   # ≥95% recall, aspirational ≤500 FP/1M
    ("hostile",    0.80, 100),   # ≥80% recall, aspirational ≤100 FP/1M
]

# Minimum expected FP to trust an FPR measurement.
MIN_EXPECTED_FP_FOR_FPR = 5


@dataclass(frozen=True, slots=True)
class PolicyLevel:
    name: str
    mode: str
    target: float
    min_flags: int = 0


@dataclass(frozen=True, slots=True)
class PolicySpec:
    name: str
    description: str
    suspicious: PolicyLevel
    hostile: PolicyLevel


POLICY_SPECS = [
    PolicySpec(
        name="ultra_low_fpr",
        description="Max recall at 10 FP/1M suspicious and 1 FP/1M hostile",
        suspicious=PolicyLevel("suspicious", "max_recall_at_fpr", 10.0),
        hostile=PolicyLevel("hostile", "max_recall_at_fpr", 1.0),
    ),
    PolicySpec(
        name="low_fpr",
        description="Looser low-FPR operating point for broader suspicious coverage",
        suspicious=PolicyLevel("suspicious", "max_recall_at_fpr", 100.0),
        hostile=PolicyLevel("hostile", "max_recall_at_fpr", 10.0),
    ),
    PolicySpec(
        name="recall_floor",
        description="Highest thresholds that still keep malware recall floors",
        suspicious=PolicyLevel("suspicious", "highest_threshold_at_recall", 0.99),
        hostile=PolicyLevel("hostile", "highest_threshold_at_recall", 0.90),
    ),
    PolicySpec(
        name="recall_plus_fpr",
        description="Recall floors with aspirational FPR tightening when measurable",
        suspicious=PolicyLevel("suspicious", "recall_floor_then_fpr", 0.97),
        hostile=PolicyLevel("hostile", "recall_floor_then_fpr", 0.85),
    ),
    PolicySpec(
        name="precision_floor",
        description="Lowest thresholds that satisfy precision floors with enough support",
        suspicious=PolicyLevel("suspicious", "min_precision", 0.99, min_flags=25),
        hostile=PolicyLevel("hostile", "min_precision", 0.999, min_flags=10),
    ),
]


@dataclass(frozen=True, slots=True)
class ScoredSample:
    row_id: int
    sha256: str
    path: str
    score: int
    label: int


def _batched(items, batch_size: int):
    it = iter(items)
    while True:
        batch = list(islice(it, batch_size))
        if not batch:
            return
        yield batch


def _select_threshold_at_fp_budget(
    thresholds: np.ndarray,
    tp_vals: np.ndarray,
    fp_vals: np.ndarray,
    recall_vals: np.ndarray,
    fpr_vals: np.ndarray,
    n_benign: int,
    *,
    max_fp: int,
) -> dict[str, float | int] | None:
    valid = fp_vals <= max_fp
    if not valid.any():
        return None
    index = int(np.where(valid)[0][-1])
    stats = _stats_dict_at_index(
        thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, index,
    )
    stats["max_fp_budget"] = int(max_fp)
    return stats


def _stats_dict_at_index(
    thresholds: np.ndarray,
    tp_vals: np.ndarray,
    fp_vals: np.ndarray,
    recall_vals: np.ndarray,
    fpr_vals: np.ndarray,
    n_benign: int,
    index: int,
) -> dict[str, float | int]:
    tp = int(tp_vals[index])
    fp = int(fp_vals[index])
    flagged = tp + fp
    precision = float(tp / flagged) if flagged > 0 else 1.0
    return {
        "threshold": float(thresholds[index]),
        "tp": tp,
        "fp": fp,
        "flagged": flagged,
        "recall": float(recall_vals[index]),
        "precision": precision,
        "fpr": float(fpr_vals[index]),
        "fp_per_million": float(fpr_vals[index] * 1_000_000),
        "n_benign": int(n_benign),
    }


def _select_policy_level(
    level: PolicyLevel,
    thresholds: np.ndarray,
    tp_vals: np.ndarray,
    fp_vals: np.ndarray,
    recall_vals: np.ndarray,
    fpr_vals: np.ndarray,
    n_benign: int,
) -> tuple[dict[str, float | int] | None, str | None]:
    if len(thresholds) == 0:
        return None, "no predictions"

    flagged = tp_vals + fp_vals
    with np.errstate(divide="ignore", invalid="ignore"):
        precision_vals = np.where(flagged > 0, tp_vals / np.maximum(flagged, 1), 1.0)

    mode = level.mode
    if mode == "max_recall_at_fpr":
        valid = fpr_vals * 1_000_000 <= level.target
        if not valid.any():
            return None, f"no threshold reaches <= {level.target:.0f} FP/1M"
        index = int(np.where(valid)[0][-1])
        if n_benign < max(int(np.ceil(MIN_EXPECTED_FP_FOR_FPR * 1_000_000 / max(level.target, 1e-12))), 1):
            warning = f"underpowered benign pool for {level.target:.0f} FP/1M target"
        else:
            warning = None
        return _stats_dict_at_index(thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, index), warning

    if mode == "highest_threshold_at_recall":
        valid = recall_vals >= level.target
        if not valid.any():
            return None, f"no threshold keeps recall >= {level.target:.2%}"
        index = int(np.where(valid)[0][0])
        return _stats_dict_at_index(thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, index), None

    if mode == "recall_floor_then_fpr":
        valid_recall = recall_vals >= level.target
        if not valid_recall.any():
            return None, f"no threshold keeps recall >= {level.target:.2%}"
        recall_index = int(np.where(valid_recall)[0][0])
        chosen_index = recall_index
        warning = None
        aspirational_fpm = 100.0 if level.name == "suspicious" else 10.0
        measurable = n_benign * aspirational_fpm / 1_000_000 >= MIN_EXPECTED_FP_FOR_FPR
        if measurable:
            valid_fpr = valid_recall & ((fpr_vals * 1_000_000) <= aspirational_fpm)
            if valid_fpr.any():
                chosen_index = int(np.where(valid_fpr)[0][0])
        else:
            warning = f"underpowered benign pool for aspirational {aspirational_fpm:.0f} FP/1M tightening"
        return _stats_dict_at_index(thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, chosen_index), warning

    if mode == "min_precision":
        valid = (precision_vals >= level.target) & (flagged >= level.min_flags)
        if not valid.any():
            return None, f"no threshold reaches precision >= {level.target:.3f} with >= {level.min_flags} flags"
        index = int(np.where(valid)[0][-1])
        return _stats_dict_at_index(thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, index), None

    raise ValueError(f"unsupported policy mode: {mode}")


def evaluate_policies(
    probs: np.ndarray,
    y: np.ndarray,
) -> list[dict[str, Any]]:
    thresholds, tp_vals, fp_vals, _correct, recall_vals, fpr_vals, _n, _nm, n_benign = (
        _threshold_stats(probs, y)
    )
    results: list[dict[str, Any]] = []
    for spec in POLICY_SPECS:
        suspicious, suspicious_warning = _select_policy_level(
            spec.suspicious, thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign,
        )
        hostile, hostile_warning = _select_policy_level(
            spec.hostile, thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign,
        )
        results.append({
            "name": spec.name,
            "description": spec.description,
            "suspicious": suspicious,
            "hostile": hostile,
            "warnings": [w for w in [suspicious_warning, hostile_warning] if w],
            "policy": {
                "suspicious": asdict(spec.suspicious),
                "hostile": asdict(spec.hostile),
            },
        })
    return results


def fp_budget_tables(
    probs: np.ndarray,
    y: np.ndarray,
    *,
    hostile_budgets: list[int] | None = None,
    suspicious_budgets: list[int] | None = None,
) -> dict[str, list[dict[str, float | int]]]:
    thresholds, tp_vals, fp_vals, _correct, recall_vals, fpr_vals, _n, _nm, n_benign = (
        _threshold_stats(probs, y)
    )
    hostile_budgets = hostile_budgets or [0, 1]
    suspicious_budgets = suspicious_budgets or list(range(1, 11))

    def _rows(budgets: list[int]) -> list[dict[str, float | int]]:
        rows: list[dict[str, float | int]] = []
        for budget in budgets:
            row = _select_threshold_at_fp_budget(
                thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign,
                max_fp=budget,
            )
            if row is not None:
                rows.append(row)
        return rows

    return {
        "hostile": _rows(hostile_budgets),
        "suspicious": _rows(suspicious_budgets),
    }


def _error_rows_for_threshold(
    samples: list[ScoredSample],
    probs: np.ndarray,
    y: np.ndarray,
    threshold: float,
    *,
    top_n: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    fp_rows: list[dict[str, Any]] = []
    fn_rows: list[dict[str, Any]] = []
    for sample, prob, label in zip(samples, probs, y, strict=False):
        row = {
            "row_id": sample.row_id,
            "sha256": sample.sha256,
            "path": sample.path,
            "score": sample.score,
            "probability": float(prob),
            "label": "bad" if int(label) == 1 else "good",
        }
        if int(label) == 0 and prob >= threshold:
            fp_rows.append(row)
        elif int(label) == 1 and prob < threshold:
            fn_rows.append(row)
    fp_rows.sort(key=lambda row: float(row["probability"]), reverse=True)
    fn_rows.sort(key=lambda row: float(row["probability"]))
    return fp_rows[:top_n], fn_rows[:top_n]


def _score_samples(
    spec: features.FeatureSpec,
    model_path: Path,
    *,
    samples: list[ScoredSample],
    report_labels: list[tuple[dict[str, Any], int]],
    batch_size: int = 2048,
    n_workers: int = 0,
) -> np.ndarray:
    model = load_model(model_path)
    pred_batches: list[np.ndarray] = []
    seen = 0
    for X_batch, y_batch in features.extract_stream_batches(
        report_labels,
        spec,
        n_workers=n_workers,
        batch_size=batch_size,
    ):
        X_input = features.standardize(X_batch, spec) if spec.standardized else X_batch
        preds = predict_proba(model, X_input)
        pred_batches.append(preds)
        seen += len(y_batch)
    if seen != len(samples):
        raise ValueError(f"scored sample count mismatch: expected {len(samples)}, got {seen}")
    return np.concatenate(pred_batches) if pred_batches else np.array([], dtype=np.float32)


def tune_thresholds(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    path_substr: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    top_errors: int = 20,
    output_path: Path | None = None,
    limit: int = 0,
    n_workers: int = 0,
) -> dict[str, Any]:
    """Score the full labeled corpus and report threshold policy candidates."""
    spec = features.FeatureSpec.load(spec_path)
    sample_stream = data.stream_labeled_samples_full(
        db_path,
        path_substr=path_substr,
        min_score=min_score,
        max_score=max_score,
        limit=limit,
    )

    samples: list[ScoredSample] = []
    report_labels: list[tuple[dict[str, Any], int]] = []
    for batch in _batched(sample_stream, 4096):
        for sample in batch:
            samples.append(ScoredSample(
                row_id=sample.row_id,
                sha256=sample.sha256,
                path=sample.path,
                score=sample.score,
                label=sample.label,
            ))
            report_labels.append((sample.report, sample.label))

    if not report_labels:
        raise ValueError("no samples matched the requested filters")

    probs = _score_samples(
        spec,
        model_path,
        samples=samples,
        report_labels=report_labels,
        n_workers=n_workers,
    )
    y = np.array([sample.label for sample in samples], dtype=np.float32)
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    policies = evaluate_policies(probs, y)
    budgets = fp_budget_tables(probs, y)
    for policy in policies:
        errors: dict[str, Any] = {}
        for level_name in ("suspicious", "hostile"):
            level = policy.get(level_name)
            if not level or level.get("threshold") is None:
                continue
            fp_rows, fn_rows = _error_rows_for_threshold(
                samples, probs, y, float(level["threshold"]), top_n=top_errors,
            )
            errors[level_name] = {
                "false_positives": fp_rows,
                "false_negatives": fn_rows,
                "false_positive_count": int(np.sum((y == 0) & (probs >= float(level["threshold"])))),
                "false_negative_count": int(np.sum((y == 1) & (probs < float(level["threshold"])))),
            }
        policy["errors"] = errors

    payload: dict[str, Any] = {
        "filters": {
            "path_substr": path_substr,
            "min_score": min_score,
            "max_score": max_score,
            "limit": limit,
        },
        "corpus": {
            "samples": len(samples),
            "malware": malware,
            "benign": benign,
        },
        "fp_budget_tables": budgets,
        "policies": policies,
    }

    print(f"\n{'TUNE THRESHOLDS':=^78}")
    print(f"Corpus: {len(samples)} samples ({malware} malware, {benign} benign)")
    if path_substr:
        print(f"Filter: path contains {path_substr!r}")
    if min_score is not None or max_score is not None:
        print(f"Filter: score range [{min_score if min_score is not None else '-inf'}, {max_score if max_score is not None else 'inf'}]")
    print(f"Top errors per level: {top_errors}")
    print()
    print(f"{'Policy':<18} {'Level':<12} {'Threshold':>10} {'Recall':>8} {'Prec':>8} {'FP/1M':>10} {'TP':>7} {'FP':>7}")
    print(f"{'-'*78}")
    for policy in policies:
        for level_name in ("suspicious", "hostile"):
            level = policy.get(level_name)
            if not level:
                print(f"{policy['name']:<18} {level_name:<12} {'—':>10} {'—':>8} {'—':>8} {'—':>10} {'—':>7} {'—':>7}")
                continue
            print(
                f"{policy['name']:<18} {level_name:<12} {float(level['threshold']):>10.6f} "
                f"{float(level['recall']):>8.2%} {float(level['precision']):>8.2%} "
                f"{float(level['fp_per_million']):>10.1f} {int(level['tp']):>7} {int(level['fp']):>7}"
            )
        for warning in policy["warnings"]:
            print(f"  warning: {warning}")
        print()

    print(f"{'HOSTILE BY ALLOWED FP':=^78}")
    print(f"{'Allowed FP':>10} {'Benign %':>10} {'Threshold':>10} {'Recall':>8} {'Prec':>8} {'TP':>7} {'FP':>7} {'FN':>7}")
    for row in budgets["hostile"]:
        fn = malware - int(row["tp"])
        print(
            f"{int(row['max_fp_budget']):>10} {100.0 * int(row['fp']) / max(benign, 1):>9.4f}% "
            f"{float(row['threshold']):>10.6f} {float(row['recall']):>8.2%} {float(row['precision']):>8.2%} "
            f"{int(row['tp']):>7} {int(row['fp']):>7} {fn:>7}"
        )
    print()

    print(f"{'SUSPICIOUS BY ALLOWED FP':=^78}")
    print(f"{'Allowed FP':>10} {'Benign %':>10} {'Threshold':>10} {'Recall':>8} {'Prec':>8} {'TP':>7} {'FP':>7} {'FN':>7}")
    for row in budgets["suspicious"]:
        fn = malware - int(row["tp"])
        print(
            f"{int(row['max_fp_budget']):>10} {100.0 * int(row['fp']) / max(benign, 1):>9.4f}% "
            f"{float(row['threshold']):>10.6f} {float(row['recall']):>8.2%} {float(row['precision']):>8.2%} "
            f"{int(row['tp']):>7} {int(row['fp']):>7} {fn:>7}"
        )
    print()

    for policy in policies:
        print(f"{policy['name']}: {policy['description']}")
        for level_name in ("suspicious", "hostile"):
            level_errors = policy["errors"].get(level_name)
            if not level_errors:
                continue
            print(
                f"  {level_name} false positives: {level_errors['false_positive_count']}  "
                f"false negatives: {level_errors['false_negative_count']}"
            )
            if level_errors["false_positives"]:
                print("  top false positives:")
                for row in level_errors["false_positives"]:
                    print(f"    {row['probability']:.6f}  {row['sha256'][:16]}  {row['path']}")
            if level_errors["false_negatives"]:
                print("  top false negatives:")
                for row in level_errors["false_negatives"]:
                    print(f"    {row['probability']:.6f}  {row['sha256'][:16]}  {row['path']}")
        print()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            import json
            json.dump(payload, f, indent=2)
        print(f"Saved tuning report to {output_path}")

    return payload


def show_thresholds(
    db_path: Path | str,
    model_path: Path | None = None,
    spec_path: Path | None = None,
    n_workers: int = 0,
) -> None:
    """Train a model on non-test samples, then show the confidence
    thresholds needed for each accuracy target on the test set.

    If model_path and spec_path are provided and exist, skip training
    entirely and only extract features for the test-bucket samples.
    """
    # Partition samples into train/test.
    train_row_ids, train_ids_labels, test_ids_labels = data.partition_row_ids(db_path)

    if (
        model_path is not None
        and spec_path is not None
        and model_path.exists()
        and spec_path.exists()
    ):
        log.info("reusing model from %s and spec from %s", model_path, spec_path)
        from .model import load_model

        spec = features.FeatureSpec.load(spec_path)
        model = load_model(model_path)

        _, _, X_test, y_test = features.extract_partitioned_from_db(
            db_path, [], test_ids_labels, spec, n_workers=n_workers,
        )
        if X_test.shape[0] == 0:
            print("No test samples — cannot compute thresholds.")
            return
        probs = predict_proba(model, X_test)
        print_threshold_table(probs, y_test)
        return

    spec = features.build_vocab_from_db(db_path, train_ids_labels, n_workers=n_workers)

    X_train, y_train, X_test, y_test = features.extract_partitioned_from_db(
        db_path, train_ids_labels, test_ids_labels, spec, n_workers=n_workers,
    )
    if X_train.shape[0] == 0:
        print("No training samples found.")
        return
    result = train.train(X_train, y_train, feature_names=spec.feature_names)
    if X_test.shape[0] == 0:
        print("No test samples — cannot compute thresholds.")
        return

    probs = predict_proba(result.model, X_test)
    print_threshold_table(probs, y_test)


def _threshold_stats(
    probs: np.ndarray,
    y: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int, int]:
    """Pre-compute per-threshold stats via a single sorted pass.

    Reduces all threshold searches from O(n_targets × n_unique × n_samples)
    to O(n log n) by computing cumulative TP/FP once and grouping ties.

    Returns arrays in descending threshold order:
      thresholds, tp, fp, correct, recall, fpr, n, n_malware, n_benign
    """
    n = len(probs)
    n_malware = int((y == 1).sum())
    n_benign = int((y == 0).sum())

    if n == 0:
        empty = np.array([], dtype=np.float64)
        return empty, empty, empty, empty, empty, empty, 0, 0, 0

    # Sort samples high-to-low by predicted probability.
    order = np.argsort(probs)[::-1]
    sorted_probs = probs[order]
    sorted_y = y[order]

    # Cumulative TP and FP as we include more samples (high prob first).
    cum_tp = np.concatenate([[0], np.cumsum(sorted_y == 1)])  # (n+1,)
    cum_fp = np.concatenate([[0], np.cumsum(sorted_y == 0)])  # (n+1,)

    # Group boundaries: we can only set a threshold between groups of identical
    # scores — all samples with the same probability must be treated together.
    change_mask = np.concatenate([np.diff(sorted_probs) != 0, [True]])  # (n,)
    cuts = np.where(change_mask)[0] + 1  # 1-indexed cutpoints; last is always n

    thresholds = sorted_probs[cuts - 1]        # prob of last sample in each group
    tp_vals = cum_tp[cuts].astype(np.int64)
    fp_vals = cum_fp[cuts].astype(np.int64)
    correct_vals = tp_vals + (n_benign - fp_vals)
    recall_vals = tp_vals / max(n_malware, 1)
    fpr_vals = fp_vals / max(n_benign, 1)

    return thresholds, tp_vals, fp_vals, correct_vals, recall_vals, fpr_vals, n, n_malware, n_benign


def compute_recommendations(
    probs: np.ndarray,
    y: np.ndarray,
) -> dict[str, float | None]:
    """Compute recommended thresholds for each level in RECOMMENDATIONS.

    Legacy FPR-based mode: for each level, picks the lowest threshold
    (highest recall) that meets the FPR ceiling. Returns a dict mapping
    level name → threshold (or None if no threshold meets the FPR target).
    """
    thresholds, _tp, _fp, _correct, _recall_vals, fpr_vals, _n, _nm, _nb = (
        _threshold_stats(probs, y)
    )
    result: dict[str, float | None] = {}
    for level, max_fpr in RECOMMENDATIONS:
        valid = fpr_vals <= max_fpr
        if valid.any():
            # Thresholds are in descending order; last valid = lowest threshold = highest recall.
            k = int(np.where(valid)[0][-1])
            result[level] = float(thresholds[k])
        else:
            result[level] = None
    return result


def compute_precision_recommendations(
    probs: np.ndarray,
    y: np.ndarray,
) -> dict[str, float | None]:
    """Compute recommended thresholds for each level in PRECISION_RECOMMENDATIONS.

    For each level (suspicious/hostile), picks the lowest threshold
    (highest recall) where the test-set precision is at least the target
    AND at least MIN_FLAGGED_FOR_PRECISION samples are flagged at that
    threshold. Intuition: "if I flag X at this threshold, I'm right ≥99%
    of the time".

    Returns a dict mapping level name → threshold (or None if no threshold
    meets the precision target with enough flagged samples).
    """
    thresholds, tp_vals, fp_vals, _correct, _recall_vals, _fpr_vals, _n, _nm, _nb = (
        _threshold_stats(probs, y)
    )
    flagged = tp_vals + fp_vals
    # Precision = TP / (TP + FP); when no flags, treat as 1.0 (vacuous).
    with np.errstate(divide="ignore", invalid="ignore"):
        precision = np.where(flagged > 0, tp_vals / np.maximum(flagged, 1), 1.0)

    result: dict[str, float | None] = {}
    for level, min_precision in PRECISION_RECOMMENDATIONS:
        valid = (precision >= min_precision) & (flagged >= MIN_FLAGGED_FOR_PRECISION)
        if valid.any():
            # Thresholds descending → last valid = lowest threshold = highest recall.
            k = int(np.where(valid)[0][-1])
            result[level] = float(thresholds[k])
        else:
            result[level] = None
    return result


def compute_recall_fpr_recommendations(
    probs: np.ndarray,
    y: np.ndarray,
) -> dict[str, float | None]:
    """Compute recommended thresholds using recall floors + aspirational FPR.

    For each level:
    1. Find the highest threshold achieving ≥min_recall (guarantees recall).
    2. If we have enough benign data, try to tighten to meet the FPR target
       — but never drop recall below the floor.
    3. Return the tighter of the two (higher threshold = fewer FP).

    This auto-scales: with more benign data the FPR target becomes
    measurable and thresholds tighten. With little data, recall floor
    governs.
    """
    thresholds, tp_vals, fp_vals, _correct, recall_vals, fpr_vals, _n, n_malware, n_benign = (
        _threshold_stats(probs, y)
    )
    fpm = fpr_vals * 1_000_000

    result: dict[str, float | None] = {}
    for level, min_recall, target_fpm in RECALL_FPR_RECOMMENDATIONS:
        # Step 1: recall-floor threshold (always available).
        recall_valid = recall_vals >= min_recall
        if not recall_valid.any():
            log.warning("%s: cannot achieve %.0f%% recall", level, min_recall * 100)
            result[level] = None
            continue
        # Last valid index = lowest threshold meeting recall floor.
        recall_idx = int(np.where(recall_valid)[0][-1])
        recall_threshold = float(thresholds[recall_idx])

        # Step 2: FPR-target threshold (if measurable).
        expected_fp = n_benign * target_fpm / 1_000_000
        fpr_threshold = None
        if expected_fp >= MIN_EXPECTED_FP_FOR_FPR:
            fpr_valid = (fpm <= target_fpm) & (recall_vals >= min_recall)
            if fpr_valid.any():
                fpr_idx = int(np.where(fpr_valid)[0][-1])
                fpr_threshold = float(thresholds[fpr_idx])

        # Pick the tighter threshold (higher = fewer FP).
        if fpr_threshold is not None and fpr_threshold > recall_threshold:
            chosen = fpr_threshold
            source = "FPR"
        else:
            chosen = recall_threshold
            source = "recall"

        result[level] = chosen

        # Log the choice.
        idx = int(np.searchsorted(-thresholds, -chosen))
        idx = min(idx, len(thresholds) - 1)
        log.info(
            "%s: threshold=%.4f (from %s floor) recall=%.2f%% FPR=%d/1M (%d FP)",
            level, chosen, source,
            float(recall_vals[idx] * 100),
            int(fpm[idx]),
            int(fp_vals[idx]),
        )

    return result


def compute_fpr_recommendations(
    probs: np.ndarray,
    y: np.ndarray,
) -> dict[str, float | None]:
    """Compute recommended thresholds based on FPR ceilings.

    For each level (suspicious/hostile), picks the lowest threshold
    (highest recall) where FP-per-million-benign stays at or below
    the target. This directly controls the false alarm rate.

    The FPR targets in FPR_RECOMMENDATIONS scale naturally: as the
    benign pool grows, finer FPR granularity becomes measurable and
    the thresholds tighten automatically.
    """
    thresholds, tp_vals, fp_vals, _correct, _recall_vals, fpr_vals, _n, _nm, n_benign = (
        _threshold_stats(probs, y)
    )
    # Convert FPR to FP-per-million for comparison with targets.
    fpm = fpr_vals * 1_000_000

    result: dict[str, float | None] = {}
    for level, max_fpm in FPR_RECOMMENDATIONS:
        # Check if we have enough benign samples to measure this FPR.
        min_benign = int(MIN_BENIGN_FOR_FPR / (max_fpm / 1_000_000))
        if n_benign < min_benign:
            log.warning(
                "%s: need ≥%d benign to measure ≤%d FP/1M (have %d)",
                level, min_benign, max_fpm, n_benign,
            )
            result[level] = None
            continue

        valid = fpm <= max_fpm
        if valid.any():
            # Thresholds descending → last valid = lowest threshold = highest recall.
            k = int(np.where(valid)[0][-1])
            result[level] = float(thresholds[k])
            log.info(
                "%s: threshold=%.4f recall=%.2f%% FPR=%.4f%% (%d FP/1M)",
                level, thresholds[k],
                float(tp_vals[k] / max(tp_vals[k] + (_n - tp_vals[k] - fp_vals[k] - (n_benign - fp_vals[k])), 1) * 100),
                float(fpr_vals[k] * 100), int(fpm[k]),
            )
        else:
            result[level] = None
    return result


def print_recommendations(
    probs: np.ndarray,
    y: np.ndarray,
    title: str = "RECOMMENDED",
    *,
    highlight_threshold: float | None = None,
) -> None:
    """Print the recommended threshold table for a set of predictions.

    highlight_threshold: if provided, inserts this threshold (e.g. the
    calibrated holdout threshold) into the fixed-thresholds table marked
    with a ← so it's easy to find the operating point from training.
    """
    thresholds, tp_vals, fp_vals, _correct_vals, recall_vals, fpr_vals, n, n_malware, n_benign = (
        _threshold_stats(probs, y)
    )

    print(f"\n{title:=^70}")
    print(f"  {n} samples ({n_malware} malware, {n_benign} benign)")
    print("  Lowest threshold (highest recall) meeting FPR ceiling")
    print(f"  {'Level':<12} {'Threshold':>10} {'Recall':>8} {'FPR':>8} {'FP/1M':>8} {'TP':>8} {'FP':>8}")
    print(f"  {'-'*62}")

    for level, max_fpr in RECOMMENDATIONS:
        # Warn if test set is too small to measure this FPR with confidence.
        min_benign = int(MIN_SAMPLES_FOR_FPR / max_fpr) if max_fpr > 0 else float("inf")
        underpowered = n_benign < min_benign

        valid = fpr_vals <= max_fpr
        if valid.any():
            # Last valid = lowest threshold = highest recall.
            k = int(np.where(valid)[0][-1])
            fp_per_million = fpr_vals[k] * 1_000_000
            warn = ""
            if underpowered:
                warn = f"  ⚠ need ≥{min_benign:,} benign to measure 1/{1/max_fpr:,.0f} FPR"
            print(
                f"  {level:<12} {thresholds[k]:>10.6f} {recall_vals[k]:>8.2%} "
                f"{fpr_vals[k]:>8.4%} {fp_per_million:>8.0f} {tp_vals[k]:>8} {fp_vals[k]:>8}"
            )
            if warn:
                print(warn)
        else:
            fpr_str = f"≤{max_fpr*100:.4f}% FPR"
            print(f"  {level:<12} {'—':>10} (no threshold achieves {fpr_str})")
            if underpowered:
                print(f"  ⚠ need ≥{min_benign:,} benign to measure 1/{1/max_fpr:,.0f} FPR")

    # Fixed reference thresholds — include the calibrated holdout threshold if provided.
    fixed_set: set[float] = {0.1, 0.25, 0.5, 0.6, 0.7, 0.8, 0.9, 0.98, 0.99, 0.995}
    if highlight_threshold is not None:
        fixed_set.add(highlight_threshold)
    fixed = sorted(fixed_set)
    print(f"\n  {'— fixed thresholds —':-^62}")
    print(f"  {'Threshold':>22} {'Recall':>8} {'FPR':>8} {'FP/1M':>8} {'TP':>8} {'FP':>8}")
    for t in fixed:
        tp = int(((probs >= t) & (y == 1)).sum())
        fp = int(((probs >= t) & (y == 0)).sum())
        tpr = tp / max(n_malware, 1)
        fpr = fp / max(n_benign, 1)
        fp_per_million = fpr * 1_000_000
        marker = " ←" if t is highlight_threshold or t == highlight_threshold else ""
        print(f"  {t:>22.3f} {tpr:>8.2%} {fpr:>8.4%} {fp_per_million:>8.0f} {tp:>8} {fp:>8}{marker}")

    # Recall-target table: highest threshold achieving each recall level.
    recall_targets = [0.99, 0.995, 0.999, 0.9999, 0.99999]
    print(f"\n  {'— by recall target —':-^62}")
    print(f"  {'Recall target':>22} {'Threshold':>10} {'Actual':>8} {'FPR':>8} {'FP/1M':>8} {'TP':>8} {'FP':>8}")
    for target in recall_targets:
        valid = recall_vals >= target
        if valid.any():
            k = int(np.where(valid)[0][0])
            label = f"≥{target*100:.3f}%"
            fp_per_million = fpr_vals[k] * 1_000_000
            print(
                f"  {label:>22} {thresholds[k]:>10.6f} {recall_vals[k]:>8.2%} "
                f"{fpr_vals[k]:>8.4%} {fp_per_million:>8.0f} {tp_vals[k]:>8} {fp_vals[k]:>8}"
            )
        else:
            label = f"≥{target*100:.3f}%"
            print(f"  {label:>22} {'—':>10} (not achievable)")

    print()


def print_threshold_table(probs: np.ndarray, y: np.ndarray) -> None:
    """Print the hostile/benign threshold table for a set of predictions."""
    n_benign = int(np.sum(y == 0))
    n_malware = int(np.sum(y == 1))
    n_total = len(y)

    print(f"\nTest set: {len(y)} samples ({n_malware} malware, {n_benign} benign)")

    thresholds, _tp_vals, fp_vals, correct_vals, _recall_vals, _fpr_vals, n, _, _ = (
        _threshold_stats(probs, y)
    )

    # --- Hostile thresholds ---
    # Lowest threshold (most permissive malware call) still meeting overall accuracy.
    # In descending thresholds: last valid entry = lowest threshold.
    print(f"\n{'HOSTILE':=^60}")
    print("  Lowest threshold to call malware while meeting overall accuracy")
    print(f"  {'Accuracy':<12} {'Threshold':>10} {'Correct':>10} {'Wrong':>8} {'Total':>8}")
    print(f"  {'-'*50}")
    for target in ACCURACY_TARGETS:
        valid = correct_vals / max(n_total, 1) >= target
        if valid.any():
            k = int(np.where(valid)[0][-1])
            pct = f"{target * 100:.3f}%"
            print(
                f"  {pct:<12} {thresholds[k]:>10.6f} {correct_vals[k]:>10} "
                f"{n_total - correct_vals[k]:>8} {n_total:>8}"
            )
        else:
            pct = f"{target * 100:.3f}%"
            print(f"  {pct:<12} {'—':>10} (not achievable on test set)")

    # --- Benign thresholds ---
    # Highest threshold (most permissive benign call) still meeting overall accuracy.
    # In descending thresholds: first valid entry = highest threshold.
    print(f"\n{'BENIGN':=^60}")
    print("  Highest threshold to call benign while meeting overall accuracy")
    print(f"  {'Accuracy':<12} {'Threshold':>10} {'Correct':>10} {'Wrong':>8} {'Total':>8}")
    print(f"  {'-'*50}")
    for target in ACCURACY_TARGETS:
        valid = correct_vals / max(n_total, 1) >= target
        if valid.any():
            k = int(np.where(valid)[0][0])
            pct = f"{target * 100:.3f}%"
            print(
                f"  {pct:<12} {thresholds[k]:>10.6f} {correct_vals[k]:>10} "
                f"{n_total - correct_vals[k]:>8} {n_total:>8}"
            )
        else:
            pct = f"{target * 100:.3f}%"
            print(f"  {pct:<12} {'—':>10} (not achievable on test set)")

    print()
    print_recommendations(probs, y, title="RECOMMENDED (test set, held-out)")
