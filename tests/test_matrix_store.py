import gc
from pathlib import Path

import numpy as np
import pytest
import scipy.sparse as sp

from collimator import features
from collimator.matrix_store import MatrixWriter


@pytest.mark.parametrize('empty', [False, True])
def test_disk_assembly_matches_ram_and_cleans_up(tmp_path, monkeypatch, empty):
    batches = [] if empty else [
        ([0, 0, 0], [1, 1, 2], [2, 3, 7], [0, 1], [0], [0], [5], [1]),
        ([1], [2], [9], [1, 0], [], [], [], []),
    ]
    monkeypatch.delenv('COLLIMATOR_MATRIX_DISK_DIR', raising=False)
    expected = features._assemble_partitioned_matrices(iter(batches), 3)
    monkeypatch.setenv('COLLIMATOR_MATRIX_DISK_DIR', str(tmp_path))
    actual = features._assemble_partitioned_matrices(iter(batches), 3)
    for i in (0, 2):
        np.testing.assert_array_equal(actual[i].toarray(), expected[i].toarray())
        np.testing.assert_array_equal(actual[i + 1], expected[i + 1])
        assert isinstance(actual[i].indptr, np.memmap)
        assert not actual[i].indptr.flags.writeable
    assert len(list(tmp_path.iterdir())) == 2
    del actual
    gc.collect()
    assert list(tmp_path.iterdir()) == []


def test_disk_assembly_failure_cleans_scratch(tmp_path, monkeypatch):
    monkeypatch.setenv('COLLIMATOR_MATRIX_DISK_DIR', str(tmp_path))
    def batches():
        yield ([0], [0], [1], [1], [], [], [], [])
        raise RuntimeError('fetch failed')
    with pytest.raises(RuntimeError, match='fetch failed'):
        features._assemble_partitioned_matrices(batches(), 3)
    assert list(tmp_path.iterdir()) == []


def test_writer_checks_alignment_and_releases_only_own_directory(tmp_path):
    keep = tmp_path / 'unrelated'
    keep.write_text('keep')
    writer = MatrixWriter(tmp_path, 3)
    try:
        with pytest.raises(ValueError, match='shape'):
            writer.append(sp.csr_matrix((2, 3)), [1])
    finally:
        writer.close()
    assert list(tmp_path.iterdir()) == [keep]
