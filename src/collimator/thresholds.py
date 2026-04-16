"""Show confidence thresholds required for various accuracy levels."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from . import data, features, train
from .model import predict_proba

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
# Used by `compute_precision_recommendations` (the default since v16).
# Intuition: "of all things flagged at this threshold, X% are real malware".
#   suspicious: "unusual, take a look" — 1 wrong flag per 200
#   hostile:    "must look NOW"        — 1 wrong flag per 2000
# These floors are set to be statistically measurable with ~70K benign
# samples. As the benign pool grows, they can be tightened.
PRECISION_RECOMMENDATIONS = [
    ("suspicious", 0.995),
    ("hostile",    0.9995),
]

# Minimum number of flagged samples required before a precision number is
# trustworthy. Avoids picking a threshold based on 1-2 samples.
MIN_FLAGGED_FOR_PRECISION = 50


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
