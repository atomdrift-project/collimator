"""Stream extracted CSR blocks to reclaimable disk-backed arrays."""

from contextlib import ExitStack
import logging
from pathlib import Path
import tempfile
import weakref

import numpy as np
import scipy.sparse as sp

log = logging.getLogger(__name__)


class MatrixWriter:
    """Append complete rows without keeping blocks or a final vstack copy."""

    def __init__(self, directory, columns):
        Path(directory).mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='matrix-', dir=directory)
        self.path = Path(self.temp.name)
        self.columns = columns
        self.rows = self.nnz = 0
        self.files = ExitStack()
        self.outputs = {name: self.files.enter_context((self.path / name).open('wb'))
                        for name in ('data', 'indices', 'indptr', 'labels')}
        np.array([0], dtype=np.int64).tofile(self.outputs['indptr'])
        self.finished = False

    def append(self, block, labels):
        if block.shape != (len(labels), self.columns):
            raise ValueError('matrix block/label shape mismatch')
        block.data.astype(np.float32, copy=False).tofile(self.outputs['data'])
        block.indices.astype(np.int64, copy=False).tofile(self.outputs['indices'])
        (block.indptr[1:].astype(np.int64) + self.nnz).tofile(self.outputs['indptr'])
        np.asarray(labels, dtype=np.float32).tofile(self.outputs['labels'])
        self.rows += block.shape[0]
        self.nnz += block.nnz

    def finish(self):
        self.files.close()
        def mapped(name, dtype, size):
            if size == 0:
                return np.empty(0, dtype=dtype)
            return np.memmap(self.path / name, dtype=dtype, mode='r', shape=(size,))
        matrix = sp.csr_matrix((self.rows, self.columns), dtype=np.float32)
        # Avoid scipy's constructor making an anonymous int32 copy for small
        # matrices. The matching int64 arrays also support >2^31 nonzeros.
        matrix.data = mapped('data', np.float32, self.nnz)
        matrix.indices = mapped('indices', np.int64, self.nnz)
        matrix.indptr = mapped('indptr', np.int64, self.rows + 1)
        labels = mapped('labels', np.float32, self.rows)
        # On Linux unlinked mapped files remain usable by any surviving views.
        # Keep the directory until the matrix is collected, including failures.
        weakref.finalize(matrix, self.temp.cleanup)
        self.finished = True
        log.info('disk-backed matrix ready: %d rows, %d nnz, %.2f GiB; scratch=%s',
                 self.rows, self.nnz, sum(p.stat().st_size for p in self.path.iterdir()) / 2**30,
                 self.path)
        return matrix, labels

    def close(self):
        self.files.close()
        if not self.finished:
            self.temp.cleanup()
