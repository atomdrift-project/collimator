import hashlib
from contextlib import nullcontext
import json
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import compare_regression_policies as comparison


def test_policy_join_requires_content_and_label_identity():
    hashes = np.array([b'a' * 32, b'b' * 32, b'c' * 32, b'd' * 32], dtype='V32')
    tables = {
        'general': {'ids': np.array([1, 2, 3, 4]), 'labels': np.array([0, 1, 1, 0]),
                    'fingerprints': hashes},
        'specialist': {'ids': np.array([2, 3, 4, 5]), 'labels': np.array([1, 0, 0, 1]),
                       'fingerprints': np.array([b'b' * 32, b'c' * 32, b'x' * 32, b'e' * 32], dtype='V32')},
    }
    ids, positions, rejected = comparison.matched_positions(tables)
    assert ids.tolist() == [2]
    assert positions['general'].tolist() == [1]
    assert positions['specialist'].tolist() == [0]
    assert rejected == 2


def test_policy_join_rejects_unsorted_or_duplicate_ids():
    for ids in [[2, 1], [1, 1]]:
        with pytest.raises(ValueError, match='sorted and unique'):
            comparison.matched_positions({'x': {'ids': np.array(ids)}})


def prepare_scores(tmp_path):
    np.savez(tmp_path / 'predictions.npz', ids=[1, 2], labels=[0, 1], current=[.1, .9], candidate=[.2, .8])
    digests = {1: hashlib.sha256(b'report1').digest(), 2: hashlib.sha256(b'report2').digest()}
    expected = hashlib.sha256(b''.join(digests.values())).hexdigest()
    (tmp_path / 'cohort.json').write_text(json.dumps({'paired_input_sha256': expected}))
    return digests


def test_fingerprint_recovery_proves_old_cohort_and_reuses_verified_result(tmp_path, monkeypatch):
    digests = prepare_scores(tmp_path)
    def fetch(db, ids, evaluation_labels):
        assert evaluation_labels == {1: 0, 2: 1}
        return {i: {'evaluation_digest': digests[i]} for i in ids}
    monkeypatch.setattr(comparison.data, 'fetch_cleave_results', fetch)
    hashes = comparison.report_fingerprints(tmp_path, 'unused')
    assert hashes.tobytes() == b''.join(digests.values())
    monkeypatch.setattr(comparison.data, 'fetch_cleave_results', lambda *a, **k: pytest.fail('must reuse'))
    assert comparison.report_fingerprints(tmp_path, 'unused').tobytes() == hashes.tobytes()
    path = tmp_path / 'verified-report-fingerprints.npz'
    path.write_bytes(path.read_bytes() + b'corruption')
    with pytest.raises(ValueError, match='inputs changed'):
        comparison.report_fingerprints(tmp_path, 'unused')


def test_changed_report_cannot_reuse_original_predictions(tmp_path, monkeypatch):
    digests = prepare_scores(tmp_path)
    digests[2] = hashlib.sha256(b'changed').digest()
    monkeypatch.setattr(comparison.data, 'fetch_cleave_results',
                        lambda db, ids, **kwargs: {i: {'evaluation_digest': digests[i]} for i in ids})
    with pytest.raises(ValueError, match='row versions changed'):
        comparison.report_fingerprints(tmp_path, 'unused')
    assert not (tmp_path / 'verified-report-fingerprints.json').exists()


def test_installed_decision_metrics_use_zero_margin_inclusively():
    result = comparison.decision_metrics(np.array([1, 1, 0, 0]), np.array([0., -.01, .2, -np.inf]))
    assert (result['tp'], result['fp'], result['fn'], result['tn']) == (1, 1, 1, 1)


def test_pg_fingerprint_recovery_matches_extraction_without_loading_reports(monkeypatch):
    class Connection:
        def execute(self, query, params):
            assert query.startswith('SELECT id, xmin::text FROM samples')
            assert 'cleave_result IS NOT NULL' in query
            assert params == ([10, 20],)
            return [(10, '120'), (20, '121')]
    monkeypatch.setattr(comparison.data, '_is_pg', lambda db: True)
    monkeypatch.setattr(comparison.data, '_connect', lambda db: nullcontext(Connection()))
    monkeypatch.setattr(comparison.data, 'fetch_cleave_results',
                        lambda *a, **k: pytest.fail('must not load report JSON'))
    result = comparison._refetch_evaluation_fingerprints('postgres://unused', [(10, 1), (20, 0)])
    assert result == {10: comparison.cache_identity.evaluation_row_digest([10, '120', 'bad']),
                      20: comparison.cache_identity.evaluation_row_digest([20, '121', 'good'])}
