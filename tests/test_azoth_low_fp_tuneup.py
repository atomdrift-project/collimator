"""Research selection must protect the independent outer validation folds."""
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace
import sys

import numpy as np
from scipy import sparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import azoth_low_fp_tuneup as study
from collimator.train import TrainConfig
from azoth_metadata_followup import metadata_env
from azoth_specialist_suite import _temporary_feature_env
from collimator.features import feature_config_from_env


def record(recalls, ap):
    return {'fold_metrics': [{'ap': ap, 'at_fp': {'0': {'recall': r}, '1': {'recall': r}}}
                             for r in recalls]}


def test_selection_rewards_consistent_strict_fp_recall_and_protects_ap():
    control = record([.2, .2, .2], .8)
    lucky = record([.9, 0., 0.], .81)
    stable = record([.3, .3, .3], .8)
    ap_collapse = record([.9, .9, .9], .7)
    assert study.choose([control, lucky, stable, ap_collapse]) is stable


def test_settings_survive_actual_refit_configuration():
    supported = {f.name for f in fields(TrainConfig)}
    for changes in [*study.PLIST.values(), *study.WHL.values()]:
        assert set(changes) <= supported
        cfg = study.settings({'holdout_fraction': .12}, changes, 43, 4)
        assert cfg.holdout_fraction == .12
        assert cfg.seed == 43
        for key, value in changes.items():
            assert getattr(cfg, key) == value


def test_metadata_override_reenables_kv_without_changing_other_group_choices():
    previous = {'COLLIMATOR_DISABLE_FEATURE_GROUPS': 'clusters, kv, symbols',
                'COLLIMATOR_KV_VOCAB': '0'}
    env = metadata_env(previous, rare=True)
    with _temporary_feature_env(env):
        config = feature_config_from_env()
        assert 'kv' in config.enabled_groups
        assert 'clusters' not in config.enabled_groups
        assert 'symbols' not in config.enabled_groups
        assert config.include_kv_vocab
        assert config.kv_min_freq == 1
        assert config.include_kv_value_split
    assert previous['COLLIMATOR_KV_VOCAB'] == '0'


def test_outer_validation_never_enters_production_fit(tmp_path, monkeypatch):
    ids = np.arange(18)
    labels = ids % 2
    buckets = np.repeat([.1, .45, .8], 6)
    cohort = (sparse.csr_matrix(ids[:, None]), labels, buckets, np.array(['whl']*18), ids)
    fits = []

    class Booster:
        def __init__(self, fitting):
            self.fitting = set(fitting)

        def save_model(self, path):
            Path(path).write_text('test')

        def num_trees(self):
            return 2

    def fit(x, y, config, sample_file_types):
        seen = x.toarray().ravel().astype(int)
        np.testing.assert_array_equal(y, labels[seen])
        assert config.holdout_fraction == .12
        assert config.hard_negative_fraction == .01
        fits.append((config.seed, seen))
        return SimpleNamespace(model=SimpleNamespace(booster_=Booster(seen)))

    def predict(booster, x, threads):
        seen = x.toarray().ravel().astype(int)
        assert not booster.fitting & set(seen)
        assert not set(buckets[list(booster.fitting)]) & set(buckets[seen])
        p = np.asarray(labels[seen]*.8 + .1, dtype=np.float32)
        return p, p, p

    monkeypatch.setattr(study.train, 'train', fit)
    monkeypatch.setattr(study.study, 'predict', predict)
    manifest = {'training_overrides': {'hard_negative_fraction': .01}}
    result = study.run_cv(tmp_path, 'trial', manifest, cohort, {'holdout_fraction': .12}, 4)
    assert len(fits) == 9
    assert result['seeds'] == [42, 43, 44]
    assert len(result['fold_metrics']) == 3
    with np.load(tmp_path/'trial-oof.npz') as saved:
        np.testing.assert_array_equal(saved['ids'], ids)
        np.testing.assert_array_equal(saved['labels'], labels)
    assert study.run_cv(tmp_path, 'trial', manifest, cohort, {'holdout_fraction': .12}, 4) == result
    assert len(fits) == 9
