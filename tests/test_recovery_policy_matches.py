import copy
import json
from dataclasses import asdict
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import evaluate_recovery_policy_matches as audit


def test_policy_audit_excludes_changed_rows_and_other_filetypes():
    base = {'ids': np.array([1, 2, 3, 4]), 'labels': np.array([1, 0, 1, 1]),
            'filetypes': np.array(['json', 'json', 'json', 'yaml']),
            'fingerprints': np.array([b'a'*32, b'b'*32, b'c'*32, b'd'*32], dtype='V32'),
            'probability': np.array([.4, .1, .2, .9], dtype=np.float32)}
    candidate = copy.deepcopy(base)
    candidate['probability'][0] = .8
    candidate['fingerprints'][2] = b'x'*32
    tables = {('current', 'general'): base, ('candidate', 'general'): candidate}
    level = {'level': 25, 'hostile': {'best': {'thresholds': {'general': .5}}}}
    saved = {'routes': {'filetypes/json': {'models': ['general'], 'levels': [level]}}}
    report = audit.evaluate_filetype('json', tables, {'current': {}, 'candidate': {}},
                                    {'current': saved, 'candidate': saved}, [25])
    assert report['rows'] == 2
    assert report['excluded_changed_versions_or_labels'] == 1
    assert report['levels'][0]['tp_delta'] == 1
    assert report['levels'][0]['fp_delta'] == 0
    saved['routes']['filetypes/json']['models'].append('filetypes/json')
    missing = audit.evaluate_filetype('json', tables, {}, {'current': saved, 'candidate': saved}, [25])
    assert missing['status'] == 'missing_scores'


def test_generation_guard_rejects_wrong_weights_and_feature_contract(monkeypatch):
    monkeypatch.setattr(audit.cache_identity, 'model_revision', lambda p: str(p))
    with pytest.raises(ValueError, match='generation mismatch'):
        audit.require_generation(Path('old'), Path('new'))
    monkeypatch.setattr(audit.cache_identity, 'model_revision', lambda p: 'identical')
    monkeypatch.setattr(audit, 'effective_spec', lambda p, *args: str(p))
    with pytest.raises(ValueError, match='feature contract mismatch'):
        audit.require_generation(Path('old'), Path('new'))


def test_prediction_receipt_rejects_changed_or_added_members(tmp_path):
    source = tmp_path / 'source'
    (source / 'models').mkdir(parents=True)
    model = source / 'models/seed_42.onnx'
    model.write_bytes(b'original')
    (tmp_path / 'plan.json').write_text(json.dumps({'hashes': {'candidate': {
        'models/seed_42.onnx': audit.fingerprint(model)}}}))
    audit.require_prediction_source(tmp_path, source, 'candidate')
    model.write_bytes(b'changed')
    with pytest.raises(ValueError, match='source changed'):
        audit.require_prediction_source(tmp_path, source, 'candidate')
    model.write_bytes(b'original')
    (source / 'models/seed_43.onnx').write_bytes(b'extra')
    with pytest.raises(ValueError, match='membership changed'):
        audit.require_prediction_source(tmp_path, source, 'candidate')


def test_calibration_reuse_requires_stable_test_rows_and_exact_identity(tmp_path, monkeypatch):
    (tmp_path/'feature_spec.json').write_text('{}')
    (tmp_path/'benchmark.json').write_text(json.dumps({'feature_env': {}}))
    monkeypatch.setattr(audit.cache_identity, 'model_revision', lambda p: 'weights')
    monkeypatch.setattr(audit.cache_identity, 'code_revision', lambda stage: 'code')
    path = tmp_path/'calibration_scores.npz'
    # Bind this fixture to its declared empty feature environment, independent
    # of cached configuration left by another test's temporary environment.
    with audit._temporary_feature_env({}):
        feature_config = json.dumps(asdict(audit.features.feature_config_from_env()),
                                    sort_keys=True, default=sorted)
    values = dict(audit_row_ids=[4, 1, 2, 3, 5], audit_labels=[1, 0, 1, 0, 0],
                  audit_fingerprints=np.array([b'a'*32]*5, dtype='V32'),
                  audit_stable_rows=[True, True, False, True, True],
                  audit_model_revision='weights', audit_feature_revision='code',
                  audit_spec_revision=audit.fingerprint(tmp_path/'feature_spec.json'),
                  audit_feature_config=feature_config,
                  indices=[0, 1, 2, 3, 4], probs=[.8, .1, .9, .2, .3])
    np.savez(path, **values)
    metadata = {'row_ids': np.array([4, 1, 2, 3, 5]), 'labels': np.array([1, 0, 1, 1, 0]),
                'sha_bucket': np.array([0, 0, 0, 0, 40]), 'file_types': np.array(['json']*5)}
    table, receipt = audit.load_calibration_audit(path, tmp_path, metadata, {})
    assert table['ids'].tolist() == [1, 4]
    assert table['probability'].tolist() == [.1, .8]
    assert receipt['retained_test_rows'] == 2
    both, receipt = audit.load_calibration_audit(path, tmp_path, metadata, {}, test_only=False)
    assert both['ids'].tolist() == [1, 4, 5]
    assert receipt['retained_rows'] == 3
    np.savez(path, **{**values, 'audit_model_revision': 'other'})
    with pytest.raises(ValueError, match='generation changed'):
        audit.load_calibration_audit(path, tmp_path, metadata, {})
    np.savez(path, probs=[.8])
    with pytest.raises(ValueError, match='lack row-version evidence'):
        audit.load_calibration_audit(path, tmp_path, metadata, {})


def test_overlay_audit_keeps_only_test_and_rejects_modified_evidence(tmp_path, monkeypatch):
    monkeypatch.setattr(audit.cache_identity, 'code_revision', lambda _: 'code')
    np.savez(tmp_path/'score_table.npz', row_ids=[3, 2, 1], labels=[1, 0, 1],
             sha_bucket=[0, 40, 0], file_types=['npm', 'npm', 'npm'],
             route_names=['general', 'filetypes/npm'],
             scores=np.array([[.8, .1, .7], [np.nan, .2, .9]], np.float32))
    np.save(tmp_path/'row-fingerprints.npy', np.array([b'a'*32]*3, dtype='V32'))
    receipt = {'score_table_sha256': audit.fingerprint(tmp_path/'score_table.npz'),
               'row_fingerprints_sha256': audit.fingerprint(tmp_path/'row-fingerprints.npy'),
               'feature_revision': 'code'}
    (tmp_path/'overlay-receipt.json').write_text(json.dumps(receipt))
    tables, _ = audit.load_overlay_audit(tmp_path)
    assert tables['general']['ids'].tolist() == [1, 3]
    assert tables['filetypes/npm']['ids'].tolist() == [1]
    (tmp_path/'row-fingerprints.npy').write_bytes(b'changed')
    with pytest.raises(ValueError, match='evidence changed'):
        audit.load_overlay_audit(tmp_path)
