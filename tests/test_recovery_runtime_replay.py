import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pytest
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import replay_recovery_runtime_scores as replay
from evaluate_recovery_policy_matches import runtime_prediction_path
from collimator import bundle, features


def test_runtime_replay_uses_exact_saved_rows_and_deployed_averaging(tmp_path, monkeypatch):
    source = tmp_path/'source'
    (source/'models').mkdir(parents=True)
    for seed in [42, 43, 44]:
        (source/'models'/f'seed_{seed}.onnx').write_bytes(str(seed).encode())
    features.FeatureSpec(total_features=1, feature_names=['x']).save(source/'feature_spec.json')
    hashes = {str(p.relative_to(source)): replay.fingerprint(p)
              for p in [source/'feature_spec.json', *sorted((source/'models').glob('*.onnx'))]}
    (tmp_path/'plan.json').write_text(json.dumps({'entry': {'candidate': str(source)},
                                               'hashes': {'candidate': hashes}}))
    member_scores = np.array([.5545847415924072, .8878898024559021, .06381720304489136], dtype=np.float32)
    legacy = np.mean(member_scores, dtype=np.float32)
    runtime = np.float32(np.mean(member_scores, dtype=np.float64))
    assert legacy != runtime  # This fixture catches the original float32 sum.
    np.savez(tmp_path/'predictions.npz', ids=[1, 2], labels=[0, 1], filetypes=['json', 'json'],
             candidate=[legacy, legacy])
    chunk = tmp_path/'extraction-chunks/00000000';chunk.mkdir(parents=True)
    sp.save_npz(chunk/'candidate.npz', sp.csr_matrix([[1.], [2.]], dtype=np.float32))
    fingerprints = b'a'*32 + b'b'*32
    (chunk/'complete.json').write_text(json.dumps({'kept': [[1, 0], [2, 1]],
        'report_fingerprints': fingerprints.hex(),
        'matrices': {'candidate': replay.fingerprint(chunk/'candidate.npz')}}))
    (tmp_path/'cohort.json').write_text(json.dumps({
        'paired_input_sha256': hashlib.sha256(fingerprints).hexdigest()}))
    class Member:
        __module__ = 'lightgbm.fake'
        def __init__(self, value): self.value = value
        def predict(self, matrix): return np.full(matrix.shape[0], self.value, dtype=np.float32)
    monkeypatch.setattr(replay.bundle.Ensemble, 'load_bundle', lambda path:
                        bundle.Ensemble([Member(v) for v in member_scores]))
    with pytest.raises(ValueError, match='need runtime-averaging replay'):
        runtime_prediction_path(tmp_path)
    result = replay.replay((str(tmp_path), ['candidate'], 1))
    assert result['candidate']['changed_scores'] == 2
    with np.load(runtime_prediction_path(tmp_path)) as values:
        assert values['candidate'].tolist() == [runtime, runtime]
        assert values['ids'].tolist() == [1, 2]
    assert replay.replay((str(tmp_path), ['candidate'], 1))['status'] == 'cached'
    assert runtime_prediction_path(tmp_path, 'candidate').is_file()
    with pytest.raises(ValueError, match="lacks requested column 'current'"):
        runtime_prediction_path(tmp_path, 'current')
    with (tmp_path/'runtime-predictions.npz').open('ab') as stream:stream.write(b'corrupt')
    with pytest.raises(ValueError, match='receipt changed'):
        runtime_prediction_path(tmp_path)
