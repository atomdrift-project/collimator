import numpy as np

from collimator.experiment import recall_at_per_100M
from collimator.thresholds import DEFAULT_SEVERITY_LEVEL, recall_at_fp_budget


def test_screen_target_uses_measured_count_budget_with_ties():
    # Two benigns share the highest score: allowing one FP cannot admit either.
    labels = np.array([0] * 100 + [1] * 4)
    scores = np.array([0.9, 0.9] + [0.1] * 98 + [0.95, 0.92, 0.9, 0.8])
    metrics = recall_at_per_100M(labels, scores)
    recall, threshold, fp = recall_at_fp_budget(labels, scores, 1)
    assert metrics["level_budget_contract"] == 1
    assert metrics["level_budget_level"] == DEFAULT_SEVERITY_LEVEL
    assert metrics["level_budget_fp_budget"] == 1
    assert metrics["level_budget_fp"] == fp == 0
    assert metrics["level_budget_recall"] == recall == 0.5
    assert metrics["level_budget_threshold"] == threshold


def test_single_class_cannot_supply_measured_target():
    metrics = recall_at_per_100M(np.ones(10), np.linspace(0.1, 0.9, 10))
    assert "level_budget_recall" not in metrics


def test_frontier_does_not_split_scores_that_tie_in_serving_precision():
    labels = np.array([0, 0, 1, 1])
    scores = np.array([0.9, np.nextafter(0.9, 0), 0.95, 0.92])
    recall, threshold, fp = recall_at_fp_budget(labels, scores, 1)
    assert recall == 1.0
    assert fp == 0
    assert int(np.sum((scores.astype(np.float32) >= threshold) & (labels == 0))) == fp
