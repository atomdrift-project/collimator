import sys
from pathlib import Path
import numpy as np
import json
import hashlib
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from diagnose_recovery_operating_points import fixed_points
from refit_regression_recovery import operating_refit_basis


def test_assessment_labels_and_scores_do_not_fit_threshold():
    y = np.r_[np.zeros(100), np.ones(10), [0, 1]]
    p = np.r_[np.linspace(.01, .2, 100), np.full(10, .9), [.99, .99]].astype(np.float32)
    selection = np.arange(len(y)) < 110
    ft = np.full(len(y), 'x')
    before = fixed_points(y, p, selection, ft, [25])['levels'][0]
    y[-2:] = [1, 0]
    p[-2:] = [.01, .01]
    after = fixed_points(y, p, selection, ft, [25])['levels'][0]
    assert before['threshold'] == after['threshold']
    assert before['selection'] == after['selection']
    assert before['assessment']['tp'] == before['assessment']['fp'] == 1
    assert after['assessment']['tp'] == after['assessment']['fp'] == 0


def test_small_calibration_is_reported_without_inventing_threshold():
    result = fixed_points(np.array([0, 1]), np.array([.1, 1.]),
                          np.array([True, False]), np.array(['x', 'x']), [25])
    assert result['status'] == 'insufficient calibration benigns'


def operating_receipt(tmp_path):
    frozen = tmp_path / 'frozen-winner.json'
    frozen.write_text(json.dumps({'winner': {'key': 'current/frozen'}}))
    def entry(tp, fp, filetypes):
        return {'key': 'current/frozen', 'status': 'evaluated', 'levels': [{
            'level': 25, 'selection': {'tp': tp, 'fp': fp, 'malware': 10, 'benign': 100},
            'assessment': {'tp': tp, 'fp': fp, 'malware': 10, 'benign': 100},
            'filetypes': filetypes}]}
    old = {'x': {'tp': 4, 'fp': 0, 'malware': 9, 'benign': 90},
           'y': {'tp': 1, 'fp': 0, 'malware': 1, 'benign': 10}}
    new = {'x': {'tp': 6, 'fp': 2, 'malware': 9, 'benign': 90}, 'y': old['y'].copy()}
    report = {'study': str(tmp_path),
        'frozen_winner_sha256': hashlib.sha256(frozen.read_bytes()).hexdigest(),
        'reports': {'reference': entry(5, 0, old), 'winner': entry(7, 2, new)}}
    path = tmp_path / 'comparison.json'
    path.write_text(json.dumps(report))
    return path, report


def test_operating_refit_records_fp_tradeoff_without_install_budget(tmp_path):
    path, _ = operating_receipt(tmp_path)
    receipt = operating_refit_basis(tmp_path, path, 25)
    assert receipt['winner']['assessment']['fp'] == 2
    assert 'confirmation pending' in receipt['status']


def test_operating_refit_rejects_constituent_loss_and_stale_choice(tmp_path):
    path, report = operating_receipt(tmp_path)
    report['reports']['winner']['levels'][0]['filetypes']['y']['tp'] = 0
    path.write_text(json.dumps(report))
    with pytest.raises(ValueError, match='loses coverage or detections: y'):
        operating_refit_basis(tmp_path, path, 25)
    (tmp_path / 'frozen-winner.json').write_text('{}')
    with pytest.raises(ValueError, match='does not bind'):
        operating_refit_basis(tmp_path, path, 25)
