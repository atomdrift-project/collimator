"""Guard selection objectives, archive grouping, and immutable tuning plans."""

import json
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import tune_regressed_models as tuning


def record(name, recall, ap=.95):
    return {'variant': name, 'selection': {'ap': ap, 'target': {
        'ap': ap, 'at_fp': {'0': {'recall': recall / 2}, '1': {'recall': recall}}}}}


def test_tail_selection_uses_one_fp_recall_and_preserves_overall_ranking():
    current = record('current', .5)
    candidates = [current, record('high_ap', .4, .99), record('tail_gain', .7, .94),
                  record('ranking_collapse', .9, .8)]
    assert tuning.choose(candidates, current)['variant'] == 'tail_gain'


def test_portable_objective_measures_python_bytecode_separately():
    labels = np.array([0, 0, 1, 1, 0, 1])
    probability = np.array([.8, .7, .9, .6, .1, .95], dtype=np.float32)
    filetypes = np.array(['pyc'] * 4 + ['java_class'] * 2)
    value = tuning.profile(labels, probability, filetypes, 'filegroups/portable')
    assert value['target']['rows'] == 4
    assert value['target']['malware'] == 2
    assert value['rows'] == 6


def test_resume_refuses_a_changed_experiment(tmp_path):
    path = tmp_path / 'plan.json'
    tuning.freeze(path, {'seed': 42})
    tuning.freeze(path, {'seed': 42})
    with pytest.raises(ValueError, match='Resume configuration changed'):
        tuning.freeze(path, {'seed': 43})
    assert json.loads(path.read_text()) == {'seed': 42}


def test_paired_interval_groups_related_positive_rows():
    labels = np.array([1, 1, 1, 1, 0])
    groups = np.array([.1, .1, .2, .2, .3])
    before = np.array([False, False, False, False, False])
    after = np.array([True, True, True, True, False])
    value = tuning.paired_recall_interval(labels, groups, after, before, repeats=100)
    assert value['positive_groups'] == 2
    assert value['delta'] == value['ci_low'] == value['ci_high'] == 1
