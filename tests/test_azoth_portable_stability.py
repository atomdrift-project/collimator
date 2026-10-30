"""Guard the experiment's split isolation and low-FP threshold semantics."""
import sys
from pathlib import Path

import numpy as np
from scipy import sparse
from dataclasses import asdict
from types import SimpleNamespace
import json
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import azoth_portable_stability as experiment
from collimator.train import TrainConfig


def test_saved_ensemble_uses_replacement_seeds_and_requires_all_members(tmp_path):
    original = tmp_path/'original'
    (original/'models').mkdir(parents=True)
    (original/'benchmark.json').write_text(json.dumps({'seed_health': {'accepted_seeds': [42,44,45]}}))
    for seed in [42,44,45]:
        (original/'models'/f'seed_{seed}.txt').write_text('model')
    assert experiment.original_seeds(tmp_path) == (42,44,45)
    (original/'models'/'seed_45.txt').unlink()
    with pytest.raises(FileNotFoundError, match='seed_45'):
        experiment.original_seeds(tmp_path)


def test_summary_and_assessment_keep_actual_original_ensemble(tmp_path):
    original = tmp_path/'original'
    (original/'models').mkdir(parents=True)
    # A two-member saved ensemble must also be reported intact.
    for seed in (44,45):
        (original/'models'/f'seed_{seed}.txt').write_text('model')
    y=np.array([0,1,0,1]); selection=np.array([True,True,False,False])
    filetypes=np.array(['markdown']*4)
    for variant,seeds in [('original',(44,45)),('baseline',experiment.SEEDS)]:
        for seed in seeds:
            dest=tmp_path/'results'/f'{variant}_seed{seed}'
            dest.mkdir(parents=True)
            (dest/'result.json').write_text(json.dumps({'variant':variant,'seed':seed}))
            np.savez(dest/'predictions.npz',probability=np.array([.1,.9,.2,.8],dtype=np.float32))
    args=SimpleNamespace(output=tmp_path)
    winner,comparisons,predictions=experiment.summarize(args,y,selection,filetypes)
    assert any(r['variant']=='original' and r['seeds']==[44,45] for r in comparisons)
    experiment.assessment(args,y,selection,filetypes,winner,comparisons,predictions)
    reports=json.loads((tmp_path/'assessment.json').read_text())['comparisons']
    assert any(r['variant']=='original' and r['seeds']==[44,45] for r in reports)


def test_threshold_never_splits_ties_or_rounds_back_to_float32():
    y = np.array([0, 0, 0, 1, 1])
    scores = np.array([1, 1, .5, 1, .75], dtype=np.float32)
    for budget in (0, 1, 2, 3):
        threshold = experiment.threshold_at_fp_budget(y, scores, budget)
        point = experiment.operating_point(y, scores, threshold)
        assert point["fp"] <= budget
    assert experiment.operating_point(y, scores, experiment.threshold_at_fp_budget(y, scores, 1))["tp"] == 0
    assert experiment.operating_point(y, scores, experiment.threshold_at_fp_budget(y, scores, 2))["tp"] == 2


def test_canonical_split_is_stable_and_has_expected_support():
    keys = [f"{i:064x}" for i in range(10000)]
    buckets = np.array([experiment.split_bucket(k) for k in keys])
    assert 0.10 < np.mean(buckets < .12) < 0.14
    assert .48 < np.mean(buckets < .5) < .52
    assert experiment.split_bucket(keys[99]) == buckets[99]


def test_matrix_roundtrip_preserves_row_alignment(tmp_path):
    matrix = sparse.csr_matrix([[0, 1, 0], [3, 0, 4]], dtype=np.float32)
    labels = np.array([0, 1])
    ids = np.array([15, 21])
    metadata = {21: (.7, "dex"), 15: (.2, "wasm")}
    experiment.save_matrix(tmp_path, "train", matrix, labels, ids, metadata)
    restored, y, buckets, filetypes = experiment.load_matrix(tmp_path, "train")
    np.testing.assert_equal(restored.toarray(), matrix.toarray())
    np.testing.assert_equal(y, labels)
    np.testing.assert_equal(buckets, [.2, .7])
    np.testing.assert_equal(filetypes, ["wasm", "dex"])


def test_precision_diagnostic_detects_saturation_ranking_loss():
    y = np.array([0, 1, 0, 1])
    raw = np.array([30., 60., -5., 50.])
    p64 = 1 / (1 + np.exp(-raw))
    report = experiment.precision_diagnostics(y, raw, p64, p64.astype(np.float32))
    assert report["ap_raw_margin"] == 1
    assert report["ap_probability32"] < 1
    assert report["saturated_ones32"] == 3


def test_small_early_stop_cohort_uses_full_budget(tmp_path):
    rng = np.random.default_rng(7)
    x = sparse.csr_matrix(rng.normal(size=(80, 4)).astype(np.float32))
    y = np.tile([0, 1], 40)
    xv = x[:20]; yv = np.r_[np.zeros(18), np.ones(2)]
    config = asdict(TrainConfig(learner='azoth', device='cpu', num_threads=1,
                               n_estimators=12, early_stopping_rounds=1,
                               min_child_weight=.001, min_child_samples=1, num_leaves=4))
    experiment.fit_variant(SimpleNamespace(output=tmp_path, threads=1), 'small_stop', {},
                           x, y, xv, yv, x, y, np.arange(80)<40, config)
    for seed in experiment.SEEDS:
        report = json.loads((tmp_path/'results'/f'small_stop_seed{seed}'/'result.json').read_text())
        history = next(iter(report['fits'][0]['history'].values()))
        assert len(history['average_precision']) == 12
