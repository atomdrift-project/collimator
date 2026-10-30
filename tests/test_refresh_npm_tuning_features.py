"""Refreshing extraction must preserve frozen cohorts and model weights."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
import pytest
from scipy import sparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import refresh_npm_tuning_features as refresh


def test_refresh_extracts_again_and_never_relabels_or_retrains(tmp_path, monkeypatch):
    source, dest = tmp_path/'source', tmp_path/'dest'
    source.mkdir()
    meta = {i: (.1, 'npm') for i in range(1, 8)}
    for name, ids, labels in [('train', [1, 3, 5], [0, 1, 0]),
                              ('extra', [2, 4], [1, 1]), ('dev', [6, 7], [0, 1])]:
        refresh.study.save_matrix(source, name, sparse.csr_matrix((len(ids), 1)),
                                  np.array(labels), np.array(ids), meta)
    for name in ('original', 'candidate', 'candidate-fulltrain/models', 'features/cooccurrence'):
        (source/name).mkdir(parents=True, exist_ok=True)
    (source/'original/benchmark.json').write_text(json.dumps({'feature_env': {}}))
    (source/'original/feature_spec.json').write_text('{}')
    (source/'features/cooccurrence/feature_spec.json').write_text('{}')
    (source/'candidate/research.json').write_text(json.dumps({'candidate_config': {
        'feature_spec': 'features/cooccurrence/feature_spec.json', 'feature_env': {}}}))
    (source/'candidate-fulltrain/complete.json').write_text(json.dumps({'dev_metrics': {}}))
    (source/'candidate-fulltrain/models/seed_42.onnx').write_bytes(b'original weights')
    (source/'prepared.json').write_text(json.dumps({'max_id': 7, 'evaluation_revision': 'old'}))
    calls = []

    def extract(db, train, dev, spec, n_workers, identity):
        calls.append((train, dev))
        assert train == [(1, 0), (2, 1), (3, 1), (4, 1), (5, 0)]
        assert dev == [(6, 0), (7, 1)]
        identity.update(train_row_ids=[i for i, _ in train], test_row_ids=[i for i, _ in dev],
                        evaluation_revision='fresh-report-revision')
        return (sparse.csr_matrix(np.ones((5, 1))), np.array([y for _, y in train]),
                sparse.csr_matrix(np.ones((2, 1))), np.array([y for _, y in dev]))

    monkeypatch.setattr(refresh.features, 'extract_partitioned_from_db', extract)
    monkeypatch.setattr(refresh.features.FeatureSpec, 'load', lambda _: None)
    monkeypatch.setattr(refresh.cache_identity, 'code_revision', lambda _: 'normalized-code')
    monkeypatch.setattr(refresh.bundle.Ensemble, 'load_bundle', lambda _: SimpleNamespace(
        predict_proba=lambda x: np.array([.1, .9], dtype=np.float32)))
    refresh.refresh(source, dest, 'unused', 1)
    assert len(calls) == 2
    for name in ('train', 'extra', 'dev'):
        np.testing.assert_array_equal(np.load(dest/name/'ids.npy'), np.load(source/name/'ids.npy'))
        np.testing.assert_array_equal(np.load(dest/name/'y.npy'), np.load(source/name/'y.npy'))
    assert np.load(dest/'train/data.npy').tolist() == [1., 1., 1.]
    assert (dest/'candidate-fulltrain/models/seed_42.onnx').read_bytes() == b'original weights'
    refresh.refresh(source, dest, 'unused', 1)
    assert len(calls) == 2
    monkeypatch.setattr(refresh.cache_identity, 'code_revision', lambda _: 'changed-again')
    with pytest.raises(ValueError, match='Changed trial plan'):
        refresh.refresh(source, dest, 'unused', 1)
