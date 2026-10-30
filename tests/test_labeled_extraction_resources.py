"""Calibration bounds live reports and IPC while preserving every feature."""
import pickle
from types import SimpleNamespace

import numpy as np
import pytest
import scipy.sparse as sp

from collimator import data, features


def test_compact_worker_preserves_features_labels_and_fetch_bound(monkeypatch):
    report = {"v": 4, "fs": [{"type": "pe", "ts": [
        {"i": "objectives/evasion/process", "l": 5, "c": 0.9},
    ]}]}
    spec = features.build_vocab([report] * 35)
    ids = [(rid, rid % 2) for rid in range(141, 0, -1)]
    item = {"cleave_result": report}
    fetches = []

    def fetch(_db, row_ids):
        fetches.append(row_ids)
        return {rid: item for rid in row_ids}

    monkeypatch.setattr(data, "fetch_cleave_results", fetch)
    expected = features._extract_batch_worker((0, [(item, y) for _, y in ids], spec))
    row, column, values, labels = expected
    expected_matrix = sp.csr_matrix(
        (np.asarray(values, dtype=np.float32), (row, column)),
        shape=(len(ids), spec.total_features),
    )
    matrix, actual_labels = features._extract_labeled_db_csr_worker(("unused", ids, spec))
    assert list(map(len, fetches)) == [64, 64, 13]
    assert [rid for batch in fetches for rid in batch] == [rid for rid, _ in ids]
    np.testing.assert_array_equal(matrix.indptr, expected_matrix.indptr)
    np.testing.assert_array_equal(matrix.indices, expected_matrix.indices)
    np.testing.assert_array_equal(matrix.data, expected_matrix.data)
    np.testing.assert_array_equal(actual_labels, labels)
    assert matrix.dtype == np.float32
    assert matrix.nnz > 0


def test_compact_worker_sends_arrays_and_releases_watchdog_on_failure(monkeypatch):
    timers = []
    monkeypatch.setattr(features.faulthandler, "dump_traceback_later", lambda *a, **kw: timers.append("start"))
    monkeypatch.setattr(features.faulthandler, "cancel_dump_traceback_later", lambda: timers.append("stop"))
    spec = SimpleNamespace(total_features=2000)
    monkeypatch.setattr(features, "_context", lambda _spec: None)

    def worker(args, **kwargs):
        return ([0] * 2000, list(range(2000)), [0.5] * 2000, [1])

    monkeypatch.setattr(features, "_extract_labeled_db_batch_worker", worker)
    result = features._extract_labeled_db_csr_worker(("unused", [(3, 1)], spec))
    assert sp.isspmatrix_csr(result[0])
    assert len(pickle.dumps(result)) < len(pickle.dumps(worker(None))) * 0.7
    assert timers == ["start", "stop"]

    def failing(_args, **kwargs):
        raise ValueError("missing row")

    monkeypatch.setattr(features, "_extract_labeled_db_batch_worker", failing)
    with pytest.raises(ValueError, match="missing row"):
        features._extract_labeled_db_csr_worker(("unused", [(3, 1)], spec))
    assert timers == ["start", "stop", "start", "stop"]
