"""Show confidence thresholds required for various accuracy levels."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from . import data, features, train
from .model import predict_proba

log = logging.getLogger(__name__)

ACCURACY_TARGETS = [0.80, 0.90, 0.95, 0.98, 0.99, 0.999, 0.9999, 0.99999]


def show_thresholds(db_path: Path) -> None:
    """Train a model on non-test samples, then show the confidence
    thresholds needed for each accuracy target on the test set."""
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
        data.stream_reports(db_path, exclude_test=False, only_test=True), spec,
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

    print(f"\nTest set: {len(y)} samples ({n_malware} malware, {n_benign} benign)")

    # --- Hostile thresholds (calling something malware) ---
    print(f"\n{'HOSTILE':=^60}")
    print("  Threshold to call a sample malware (score >= threshold)")
    print(f"  {'Accuracy':<12} {'Threshold':>10} {'Correct':>10} {'Wrong':>8} {'Total':>8}")
    print(f"  {'-'*50}")

    candidates = np.sort(np.unique(probs))[::-1]
    for target in ACCURACY_TARGETS:
        best_t = None
        for t in candidates:
            mask = probs >= t
            n = int(mask.sum())
            if n == 0:
                continue
            correct = int(((probs >= t) & (y == 1)).sum())
            acc = correct / n
            if acc >= target:
                best_t = t
                best_n = n
                best_correct = correct
                best_wrong = n - correct
        if best_t is not None:
            pct = f"{target * 100:.3f}%"
            print(f"  {pct:<12} {best_t:>10.6f} {best_correct:>10} {best_wrong:>8} {best_n:>8}")
        else:
            pct = f"{target * 100:.3f}%"
            print(f"  {pct:<12} {'—':>10} (not achievable on test set)")

    # --- Benign thresholds (calling something safe) ---
    print(f"\n{'BENIGN':=^60}")
    print("  Threshold to call a sample benign (score < threshold)")
    print(f"  {'Accuracy':<12} {'Threshold':>10} {'Correct':>10} {'Wrong':>8} {'Total':>8}")
    print(f"  {'-'*50}")

    candidates_asc = np.sort(np.unique(probs))
    for target in ACCURACY_TARGETS:
        best_t = None
        for t in candidates_asc:
            mask = probs < t
            n = int(mask.sum())
            if n == 0:
                continue
            correct = int(((probs < t) & (y == 0)).sum())
            acc = correct / n
            if acc >= target:
                best_t = t
                best_n = n
                best_correct = correct
                best_wrong = n - correct
        # We want the HIGHEST threshold that still meets accuracy.
        if best_t is not None:
            pct = f"{target * 100:.3f}%"
            print(f"  {pct:<12} {best_t:>10.6f} {best_correct:>10} {best_wrong:>8} {best_n:>8}")
        else:
            pct = f"{target * 100:.3f}%"
            print(f"  {pct:<12} {'—':>10} (not achievable on test set)")

    print()
