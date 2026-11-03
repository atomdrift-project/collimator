"""Validate canonical-group isolation in the controlled recovery protocol."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import grouped_training_recovery as recovery
from collimator import train


def test_group_holdout_keeps_mixed_and_unequal_groups_together():
    groups = np.repeat(np.array([f'group-{i}' for i in range(80)]), np.arange(80) % 5 + 2)
    y = (np.arange(len(groups)) % 3 == 0).astype(int)
    a,b = recovery.group_holdout_indices(y,groups,fraction=.2,seed=42)
    assert not np.intersect1d(groups[a],groups[b]).size
    np.testing.assert_array_equal(np.sort(np.r_[a,b]),np.arange(len(y)))
    assert len(np.unique(y[a])) == len(np.unique(y[b])) == 2
    other = recovery.group_holdout_indices(y,groups,fraction=.2,seed=42)
    for x,z in zip((a,b),other,strict=True):
        np.testing.assert_array_equal(x,z)


def test_group_holdout_rejects_class_confined_to_one_group():
    with pytest.raises(ValueError,match='no group-disjoint split'):
        recovery.group_holdout_indices(np.r_[np.zeros(40),np.ones(40)],
            np.array(['benign']*40+['malware']*40),fraction=.5,seed=42)


@pytest.mark.parametrize('groups', [np.array(['a','b','c']), np.array(['a','','c','d']), np.array([1,2,3,4])])
def test_group_holdout_rejects_invalid_identity_arrays(groups):
    with pytest.raises(ValueError):
        recovery.group_holdout_indices(np.array([0,0,1,1]),groups,fraction=.5,seed=42)


def test_real_training_uses_disjoint_fit_stopping_and_evaluation_groups():
    rng = np.random.default_rng(9)
    groups = np.repeat(np.array([f'group-{i}' for i in range(160)]),3)
    y = np.repeat(np.arange(160)%2,3)
    X = rng.normal(size=(len(y),4)).astype(np.float32)
    X[:,0] += y
    original = train.train_test_split
    config = train.TrainConfig(learner='azoth',device='cpu',num_threads=1,n_folds=0,
        n_estimators=8,min_child_samples=2,min_child_weight=1,holdout_fraction=.3)
    result,audit,parts = recovery.train_grouped(X,y,config,groups)
    assert train.train_test_split is original
    assert not audit['shared_small_holdout']
    for a,b in [('fit','calibration'),('fit','evaluation'),('calibration','evaluation')]:
        assert not np.intersect1d(groups[parts[a]],groups[parts[b]]).size
    assert result.split_summary['evaluation_samples'] == len(parts['evaluation'])


def test_patch_restored_when_training_fails(monkeypatch):
    original = train.train_test_split
    def fail(*args,**kwargs):
        raise RuntimeError('fit failed')
    monkeypatch.setattr(train,'train',fail)
    y = np.arange(200)%2
    with pytest.raises(RuntimeError,match='fit failed'):
        recovery.train_grouped(np.zeros((200,2)),y,
            train.TrainConfig(n_folds=0),np.array([str(i) for i in range(200)]))
    assert train.train_test_split is original
