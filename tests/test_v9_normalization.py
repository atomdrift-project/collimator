"""Equivalent historical/v9 facts must produce identical model features."""
from copy import deepcopy
from pathlib import Path
import sys

import numpy as np
import pytest

from collimator import features
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from azoth_specialist_suite import _temporary_feature_env


@pytest.mark.parametrize('old,new', features._METRIC_RENAMES.items())
@pytest.mark.parametrize('value', [0, None, False, 5.25, 'signed'])
def test_metric_aliases_are_bidirectional_and_nonmutating(old, new, value):
    old_group, old_key = old.split('.', 1)
    new_group, new_key = new.split('.', 1)
    for source, target in [((old_group, old_key), (new_group, new_key)),
                           ((new_group, new_key), (old_group, old_key))]:
        raw = {source[0]: {source[1]: value}}
        before = deepcopy(raw)
        actual = features._backfill_renamed_metrics(raw)
        assert actual[target[0]][target[1]] == value
        assert raw == before
        assert features._backfill_renamed_metrics(actual) == actual


def test_conflicts_malformed_groups_and_absent_facts_are_preserved():
    raw = {'ast': {'max_array_len': 0, 'max_array_length': 42},
           'binary': None, 'file': {'entropy': 7.5}}
    actual = features._backfill_renamed_metrics(raw)
    assert actual['ast']['max_array_len'] == 0
    assert actual['ast']['max_array_length'] == 42
    assert actual['ast']['array_literal_max_length'] == 42
    assert actual['binary'] is None
    assert 'registry' not in actual
    assert features._backfill_renamed_metrics({}) == {}


def test_v8_v9_vectors_and_discovered_vocabularies_match():
    old = {'v': '8', 'files': [{'id': 0, 'type': 'npm', 'size': 2048,
        'facts': {'metrics': {'ast': {'max_array_len': 12, 'max_numeric_seq': 4},
                             'registry': {'maintainers': 2, 'published_at': 12345},
                             'source': {'extract_panic': False},
                             'archive': {'timing.mtime_dominant_fraction': .8}}},
        'traits': [{'id': 'objectives/execution/shell', 'crit': 4, 'conf': .9}],
        'ctx': [{'ln': 0, 'b': 'old-context-encoding'}]}]}
    new = deepcopy(old)
    new['v'] = '9'
    new['files'][0]['ctx'] = [{'ln': 0, 's': 'new readable context'}]
    new['files'][0]['facts']['metrics'] = {
        'ast': {'max_array_length': 12, 'max_numeric_sequence': 4},
        'registry': {'maintainer_count': 2, 'published_unix': 12345},
        'source': {'extract_panicked': False},
        'archive': {'timing.mtime_dominant_ratio': .8}}
    originals = deepcopy((old, new))
    with _temporary_feature_env({'COLLIMATOR_EXTENDED_METRICS': '1',
        'COLLIMATOR_KV_VOCAB': '1', 'COLLIMATOR_KV_SHAPE_FEATURES': '1',
        'COLLIMATOR_DISABLE_FEATURE_GROUPS': '', 'COLLIMATOR_KV_MIN_FREQ': '1'}):
        specs = []
        for report in (old, new):
            spec = features.build_vocab([deepcopy(report) for _ in range(35)], n_workers=1)
            file = report['files'][0]
            spec.metric_vocab = sorted(f'{g}_{k}' for g, fields in features.file_metrics(file).items()
                                       for k in fields)
            spec.kv_vocab = sorted(features._metric_kv_tokens(file, include_shape=True))
            spec.feature_names = features._build_feature_names(
                spec.presence_vocab, spec.filetype_vocab, spec.element_vocab, spec.bigram_vocab,
                spec.ghost_vocab, spec.skeleton_vocab, spec.rare_element_vocab, spec.trigram_vocab,
                metric_vocab=spec.metric_vocab, kv_vocab=spec.kv_vocab)
            spec.total_features = len(spec.feature_names)
            specs.append(spec)
        assert specs[0].feature_names == specs[1].feature_names
        for spec in specs:
            np.testing.assert_array_equal(features.extract(old, spec), features.extract(new, spec))
            assert any('max_array_len' in name for name in spec.feature_names)
            assert any('registry.maintainers' in name for name in spec.feature_names)
    assert (old, new) == originals
