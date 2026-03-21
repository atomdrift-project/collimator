"""Show confidence thresholds required for various accuracy levels."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from . import data, features, train
from .model import predict_proba

log = logging.getLogger(__name__)

ACCURACY_TARGETS = [0.80, 0.90, 0.95, 0.98, 0.99, 0.993, 0.996, 0.998, 0.999, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995, 0.9996, 0.9997, 0.9998, 0.9999, 0.99999]

# (label, min recall, max FPR): highest threshold satisfying both constraints.
# Highest threshold = most conservative call that still meets both targets.
RECOMMENDATIONS = [
    ("suspicious", 0.999,  0.002),   # catch 99.9% of malware, ≤0.2% FPR
    ("hostile",    0.980,  0.0002),  # catch 98.0% of malware, ≤0.02% FPR
]


def show_thresholds(
    db_path: Path,
    model_path: Path | None = None,
    spec_path: Path | None = None,
    n_workers: int = 0,
) -> None:
    """Train a model on non-test samples, then show the confidence
    thresholds needed for each accuracy target on the test set.

    If model_path and spec_path are provided and exist, skip training
    entirely and only stream the ~5% test-bucket samples.
    """
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

        X_test, y_test = features.extract_stream(
            data.stream_raw_reports(db_path, only_test=True),
            spec,
            n_workers=n_workers,
        )
        if X_test.shape[0] == 0:
            print("No test samples — cannot compute thresholds.")
            return
        probs = predict_proba(model, X_test)
        print_threshold_table(probs, y_test)
        return
    # Pass 1: build vocab from training samples (streaming).
    spec = features.build_vocab(
        (report for report, _label in data.stream_raw_reports(db_path, exclude_test=True)),
        n_workers=n_workers,
    )

    # Pass 2: extract training and held-out test features in one pass.
    X_train, y_train, X_test, y_test = features.extract_partitioned_stream(
        data.stream_partitioned_raw_reports(db_path), spec, n_workers=n_workers,
    )
    train_groups = data.load_train_group_ids(db_path)
    if X_train.shape[0] == 0:
        print("No training samples found.")
        return
    result = train.train(X_train, y_train, feature_names=spec.feature_names, groups=train_groups)
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


def print_recommendations(probs: np.ndarray, y: np.ndarray, title: str = "RECOMMENDED") -> None:
    """Print the recommended threshold table for a set of predictions."""
    thresholds, tp_vals, fp_vals, _correct_vals, recall_vals, fpr_vals, n, n_malware, n_benign = (
        _threshold_stats(probs, y)
    )

    print(f"\n{title:=^60}")
    print(f"  {n} samples ({n_malware} malware, {n_benign} benign)")
    print("  Highest threshold satisfying both recall and FPR targets")
    print("  (most conservative call still meeting both constraints)")
    print(f"  {'Level':<12} {'Threshold':>10} {'Recall':>8} {'FPR':>8} {'TP':>8} {'FP':>8}")
    print(f"  {'-'*52}")

    for level, min_tpr, max_fpr in RECOMMENDATIONS:
        # valid = window where recall≥min AND fpr≤max (contiguous since both are
        # monotone with threshold). First valid entry = highest threshold in window.
        valid = (recall_vals >= min_tpr) & (fpr_vals <= max_fpr)
        if valid.any():
            k = int(np.where(valid)[0][0])
            print(
                f"  {level:<12} {thresholds[k]:>10.6f} {recall_vals[k]:>8.2%} "
                f"{fpr_vals[k]:>8.3%} {tp_vals[k]:>8} {fp_vals[k]:>8}"
            )
        else:
            tpr_str = f"≥{min_tpr*100:.1f}% recall"
            fpr_str = f"≤{max_fpr*100:.3f}% FPR"
            print(f"  {level:<12} {'—':>10} (no threshold achieves {tpr_str} and {fpr_str})")

    # Fixed reference thresholds — straight numpy, no loop overhead.
    print(f"\n  {'— fixed thresholds —':-^52}")
    print(f"  {'Threshold':>22} {'Recall':>8} {'FPR':>8} {'TP':>8} {'FP':>8}")
    for t in [0.5, 0.8, 0.9, 0.98, 0.99, 0.995]:
        tp = int(((probs >= t) & (y == 1)).sum())
        fp = int(((probs >= t) & (y == 0)).sum())
        tpr = tp / max(n_malware, 1)
        fpr = fp / max(n_benign, 1)
        print(f"  {t:>22.3f} {tpr:>8.2%} {fpr:>8.3%} {tp:>8} {fp:>8}")

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
