"""Recent-slice experiments must retain whole-cohort FP constraints."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from azoth_npm_recent import recent_cutoff, recency_metrics, choose


def test_cutoff_is_based_on_population_not_labels_or_input_order():
    assert recent_cutoff(np.array([9, 1, 2, 7, 3]), .4) == 7
    assert recent_cutoff(np.arange(201), .01) == 198


def test_recent_recall_uses_global_threshold_including_old_false_positives():
    y = np.array([0, 1, 0, 1])
    p = np.array([.95, .99, .1, .9])
    d = recency_metrics(y, p, np.array([1, 2, 100, 101]), 100)
    assert d['recent']['tp'] == 0
    assert d['older']['tp'] == 1
    assert d['recent']['threshold'] == d['older']['threshold']


def test_recent_gain_cannot_hide_large_global_regression():
    def row(recent, global_recall, ap):
        return {'recency_folds': [{'recent': {'recall': recent}}]*3,
                'fold_metrics': [{'ap': ap, 'at_fp': {'0': {'recall': global_recall},
                                                    '1': {'recall': global_recall}}}]*3}
    baseline = row(.4, .7, .97)
    improved = row(.5, .7, .97)
    collapse = row(.9, .6, .97)
    ap_collapse = row(.9, .7, .94)
    assert choose([baseline, improved, collapse, ap_collapse]) is improved
