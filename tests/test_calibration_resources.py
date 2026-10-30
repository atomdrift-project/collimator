"""Validation shares metadata and preserves scores while bounding allocations."""
import os
import pickle
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import azoth_calibrate_ensemble as calibrate
from collimator import bundle, features, model
from collimator.matrix_store import MatrixWriter
from tests.test_onnx_projection import tree


def test_shared_index_preserves_arbitrary_order_and_missing_ids(tmp_path):
    ids = np.array([90, 2, 17, 400], dtype=np.int64)
    with calibrate._shared_row_index(ids, tmp_path) as paths:
        index = calibrate._open_row_index(paths)
        assert isinstance(index.ids, np.memmap)
        assert not index.ids.flags.writeable
        assert index.lookup([400, 3, 90, 0, 999, 17, 2]).tolist() == [3, -1, 0, -1, -1, 2, 1]
        assert len(pickle.dumps(paths)) < 1000
    assert not Path(paths[0]).exists()
    with calibrate._shared_row_index(np.array([], dtype=np.int64), tmp_path) as paths:
        assert calibrate._open_row_index(paths).lookup([1]).tolist() == [-1]
    with pytest.raises(ValueError, match='duplicate'):
        with calibrate._shared_row_index(np.array([4, 4]), tmp_path):
            pass


@pytest.mark.parametrize('standardized', [False, True])
def test_disk_matrix_prediction_is_bit_exact(tmp_path, monkeypatch, standardized):
    monkeypatch.setenv('COLLIMATOR_ONNX_THREADS', '2')
    monkeypatch.setattr(model.OnnxModel, '_DENSE_BYTES', 32 * 4 * 13)
    models = tmp_path / 'models'
    models.mkdir()
    for seed, column in [(42, 2), (43, 29), (44, 9)]:
        tree(models / f'seed_{seed}.onnx', column=column)
    ensemble = bundle.Ensemble.load_bundle(tmp_path)
    x = sp.csr_matrix(np.random.default_rng(19).normal(size=(117, 32)).astype(np.float32))
    spec = SimpleNamespace(standardized=standardized, feature_means=[.1] * 32,
                           feature_stds=[1.1] * 32)
    expected = ensemble.predict_proba(features.standardize(x, spec) if standardized else x)
    writer = MatrixWriter(tmp_path, 32)
    try:
        for start in range(0, len(expected), 17):
            block = x[start:start+17]
            writer.append(block, np.zeros(block.shape[0]))
        mapped, _ = writer.finish()
    finally:
        writer.close()
    assert isinstance(mapped.data, np.memmap)
    np.testing.assert_array_equal(calibrate._predict_matrix(ensemble, mapped, spec), expected)


def test_native_thread_limits_restore_environment(monkeypatch):
    monkeypatch.setenv('OPENBLAS_NUM_THREADS', '97')
    monkeypatch.delenv('COLLIMATOR_ONNX_THREADS', raising=False)
    with calibrate._scoring_threads():
        assert os.environ['OPENBLAS_NUM_THREADS'] == '1'
        assert os.environ['COLLIMATOR_ONNX_THREADS'] == '8'
    assert os.environ['OPENBLAS_NUM_THREADS'] == '97'
    assert 'COLLIMATOR_ONNX_THREADS' not in os.environ


def test_spawn_workers_share_index_and_reuse_verified_scores(tmp_path, monkeypatch):
    """Actual spawned processes must find the maps without serializing a dict."""
    # Earlier tests temporarily change feature env vars. Spawn reads the real
    # environment, so build the parent fixture with that same configuration.
    features.feature_config_from_env.cache_clear()
    monkeypatch.setenv('COLLIMATOR_MATRIX_DISK_DIR', str(tmp_path / 'scratch'))
    # Another legacy test loads this script manually under the same name.
    monkeypatch.setitem(sys.modules, 'azoth_calibrate_ensemble', calibrate)
    jobs = []
    for name in ('one', 'two'):
        directory = tmp_path / name
        directory.mkdir()
        (directory / 'model.onnx').write_bytes(b'cached-model')
        (directory / 'feature_spec.json').write_text('{}')
        route = dict(output_dir=str(directory), route=f'filetypes/{name}', name=name,
                     kind='filetype', file_types=[name])
        # Generate a real score-cache identity via the production scorer.
        with monkeypatch.context() as patch:
            patch.setattr(calibrate, '_fetch_rows', lambda *a, **kw: [(90, 1), (2, 0)])
            patch.setattr(features.FeatureSpec, 'load', lambda p: SimpleNamespace(total_features=1, standardized=False))
            patch.setattr(bundle.Ensemble, 'load_bundle', lambda p: SimpleNamespace(predict_proba=lambda x: np.array([.9, .1], dtype=np.float32)))
            patch.setattr(features, 'extract_labeled_from_db_batches', lambda *a, **kw: iter([(sp.csr_matrix([[1.], [0.]]), np.array([1, 0]))]))
            calibrate._score_route('unused', route, row_index={90: 0, 2: 1}, max_id=90,
                workers=1, refresh=False, refresh_routes=set(), feature_cache_dir=None, cache_context='frozen')
        jobs.append(dict(db_path='unused', route=route, max_id=90, workers=1, refresh=False,
                         refresh_routes=set(), feature_cache_dir=None, cache_context='frozen'))
    results = calibrate._run_score_jobs(jobs, np.array([90, 2]), 2, 'INFO')
    for result in results:
        np.testing.assert_array_equal(result['indices'], [0, 1])
        np.testing.assert_array_equal(result['probs'], np.array([.9, .1], dtype=np.float32))
