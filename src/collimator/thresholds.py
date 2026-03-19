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
            data.stream_reports(db_path, only_test=True), spec,
        )
        if X_test.shape[0] == 0:
            print("No test samples — cannot compute thresholds.")
            return
        probs = predict_proba(model, X_test)
        print_threshold_table(probs, y_test)
        return

    # Pass 1: build vocab from training samples (streaming).
    spec = features.build_vocab(
        report for report, _label in data.stream_reports(db_path, exclude_test=True)
    )

    # Pass 2: extract training features (streaming).
    X_train, y_train = features.extract_stream(
        data.stream_reports(db_path, exclude_test=True), spec,
    )
    if X_train.shape[0] == 0:
        print("No training samples found.")
        return
    result = train.train(X_train, y_train, feature_names=spec.feature_names)

    # Pass 3: extract test features (streaming).
    X_test, y_test = features.extract_stream(
        data.stream_reports(db_path, only_test=True), spec,
    )
    if X_test.shape[0] == 0:
        print("No test samples — cannot compute thresholds.")
        return

    probs = predict_proba(result.model, X_test)
    print_threshold_table(probs, y_test)


def print_threshold_table(probs: np.ndarray, y: np.ndarray) -> None:
    """Print the hostile/benign threshold table for a set of predictions."""
    n_benign = int(np.sum(y == 0))
    n_malware = int(np.sum(y == 1))
    n_total = len(y)

    print(f"\nTest set: {len(y)} samples ({n_malware} malware, {n_benign} benign)")

    # --- Hostile thresholds (calling something malware) ---
    print(f"\n{'HOSTILE':=^60}")
    print("  Lowest threshold to call malware while meeting overall accuracy")
    print(f"  {'Accuracy':<12} {'Threshold':>10} {'Correct':>10} {'Wrong':>8} {'Total':>8}")
    print(f"  {'-'*50}")

    # Scan high→low; keep updating so we end up with the lowest threshold
    # (most permissive hostile call) that still meets overall accuracy.
    candidates = np.sort(np.unique(probs))[::-1]
    for target in ACCURACY_TARGETS:
        best_t = None
        for t in candidates:
            tp = int(((probs >= t) & (y == 1)).sum())
            tn = int(((probs < t) & (y == 0)).sum())
            correct = tp + tn
            if correct / n_total >= target:
                best_t = t
                best_correct = correct
                best_wrong = n_total - correct
        if best_t is not None:
            pct = f"{target * 100:.3f}%"
            print(f"  {pct:<12} {best_t:>10.6f} {best_correct:>10} {best_wrong:>8} {n_total:>8}")
        else:
            pct = f"{target * 100:.3f}%"
            print(f"  {pct:<12} {'—':>10} (not achievable on test set)")

    # --- Benign thresholds (calling something safe) ---
    print(f"\n{'BENIGN':=^60}")
    print("  Highest threshold to call benign while meeting overall accuracy")
    print(f"  {'Accuracy':<12} {'Threshold':>10} {'Correct':>10} {'Wrong':>8} {'Total':>8}")
    print(f"  {'-'*50}")

    # Scan low→high; keep updating so we end up with the highest threshold
    # (most permissive benign call) that still meets overall accuracy.
    candidates_asc = np.sort(np.unique(probs))
    for target in ACCURACY_TARGETS:
        best_t = None
        for t in candidates_asc:
            tn = int(((probs < t) & (y == 0)).sum())
            tp = int(((probs >= t) & (y == 1)).sum())
            correct = tn + tp
            if correct / n_total >= target:
                best_t = t
                best_correct = correct
                best_wrong = n_total - correct
        if best_t is not None:
            pct = f"{target * 100:.3f}%"
            print(f"  {pct:<12} {best_t:>10.6f} {best_correct:>10} {best_wrong:>8} {n_total:>8}")
        else:
            pct = f"{target * 100:.3f}%"
            print(f"  {pct:<12} {'—':>10} (not achievable on test set)")

    print()

    # --- Recommended thresholds: highest T where recall≥min AND FPR≤max ---
    print(f"\n{'RECOMMENDED':=^60}")
    print("  Highest threshold satisfying both recall and FPR targets")
    print("  (most conservative call still meeting both constraints)")
    print(f"  {'Level':<12} {'Threshold':>10} {'Recall':>8} {'FPR':>8} {'TP':>8} {'FP':>8}")
    print(f"  {'-'*52}")

    for level, min_tpr, max_fpr in RECOMMENDATIONS:
        best_t = None
        # Scan low→high; keep updating while both constraints are met.
        for t in np.sort(np.unique(probs)):
            tp = int(((probs >= t) & (y == 1)).sum())
            fp = int(((probs >= t) & (y == 0)).sum())
            tpr = tp / n_malware if n_malware else 0.0
            fpr = fp / n_benign if n_benign else 0.0
            if tpr >= min_tpr and fpr <= max_fpr:
                best_t = t
                best_tp = tp
                best_fp = fp
                best_tpr = tpr
                best_fpr = fpr
        if best_t is not None:
            print(
                f"  {level:<12} {best_t:>10.6f} {best_tpr:>8.2%} {best_fpr:>8.3%} "
                f"{best_tp:>8} {best_fp:>8}"
            )
        else:
            tpr_str = f"≥{min_tpr*100:.1f}% recall"
            fpr_str = f"≤{max_fpr*100:.3f}% FPR"
            print(f"  {level:<12} {'—':>10} (no threshold achieves {tpr_str} and {fpr_str})")

    # --- Fixed threshold reference points ---
    print(f"\n  {'— fixed thresholds —':-^52}")
    print(f"  {'Threshold':>22} {'Recall':>8} {'FPR':>8} {'TP':>8} {'FP':>8}")
    for t in [0.5, 0.8, 0.9, 0.98, 0.99, 0.995]:
        tp = int(((probs >= t) & (y == 1)).sum())
        fp = int(((probs >= t) & (y == 0)).sum())
        tpr = tp / n_malware if n_malware else 0.0
        fpr = fp / n_benign if n_benign else 0.0
        print(f"  {t:>22.3f} {tpr:>8.2%} {fpr:>8.3%} {tp:>8} {fp:>8}")

    print()
