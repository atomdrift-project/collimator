"""Bounded external reduction of exact weighted n-gram counts.

Each run is sorted and unique. Pairwise merges add equal keys before SQLite
sees them, avoiding repeated B-tree updates as the output grows beyond RAM.
Files are scratch data; only the owner's existing partition receipt commits
completed work to the durable vocabulary database.
"""
from pathlib import Path
import logging
import tempfile
from itertools import repeat

import numpy as np

_READ_KEYS = 65536


def _reduce(records):
    records = records[np.argsort(records['key'], kind='stable')]
    starts = np.r_[0, np.flatnonzero(records['key'][1:] != records['key'][:-1]) + 1]
    output = records[starts].copy()
    output['n'] = np.add.reduceat(records['n'], starts)
    return output


def _merge(left, right, output, dtype):
    """Merge unique runs with bounded reads, including equal boundary keys."""
    with open(left, 'rb') as a_file, open(right, 'rb') as b_file, open(output, 'wb') as dest:
        a = np.fromfile(a_file, dtype=dtype, count=_READ_KEYS)
        b = np.fromfile(b_file, dtype=dtype, count=_READ_KEYS)
        while len(a) and len(b):
            # Consume through the smaller last key. Unread chunks can only
            # contain larger keys, so no duplicate straddles an output write.
            boundary = a['key'][-1] if bytes(a['key'][-1]) <= bytes(b['key'][-1]) else b['key'][-1]
            i = np.searchsorted(a['key'], boundary, side='right')
            j = np.searchsorted(b['key'], boundary, side='right')
            _reduce(np.concatenate((a[:i], b[:j]))).tofile(dest)
            a, b = a[i:], b[j:]
            if not len(a):
                a = np.fromfile(a_file, dtype=dtype, count=_READ_KEYS)
            if not len(b):
                b = np.fromfile(b_file, dtype=dtype, count=_READ_KEYS)
        for current, source in ((a, a_file), (b, b_file)):
            while len(current):
                current.tofile(dest)
                current = np.fromfile(source, dtype=dtype, count=_READ_KEYS)


class SignatureRuns:
    def __init__(self, directory):
        self.directory = tempfile.TemporaryDirectory(prefix='sorted-runs-', dir=directory)
        self.levels = {}
        self.serial = 0
        self.input_keys = 0
        self.output_keys = 0

    def _path(self):
        self.serial += 1
        return Path(self.directory.name) / f'{self.serial}.bin'

    def add(self, family, keys, totals):
        if not len(keys):
            return
        dtype = np.dtype([('key', keys.dtype), ('n', '<i8')])
        records = np.empty(len(keys), dtype=dtype)
        records['key'], records['n'] = keys, totals
        path = self._path()
        records.tofile(path)
        self.input_keys += len(keys)
        levels = self.levels.setdefault((family, keys.dtype.itemsize), [])
        level = 0
        while level < len(levels) and levels[level] is not None:
            other = levels[level]
            merged = self._path()
            _merge(other, path, merged, dtype)
            other.unlink(); path.unlink()
            levels[level] = None
            path = merged
            level += 1
        if level == len(levels):
            levels.append(path)
        else:
            levels[level] = path

    def finish(self, db):
        for (family, size), levels in sorted(self.levels.items()):
            dtype = np.dtype([('key', f'V{size}'), ('n', '<i8')])
            paths = [p for p in levels if p is not None]
            path = paths.pop(0)
            for other in paths:
                merged = self._path()
                _merge(path, other, merged, dtype)
                path.unlink(); other.unlink()
                path = merged
            with path.open('rb') as source:
                while len(records := np.fromfile(source, dtype=dtype, count=_READ_KEYS)):
                    db.executemany(
                        'INSERT INTO counts VALUES (?, ?, ?, NULL, NULL)'
                        ' ON CONFLICT(family, token) DO UPDATE SET n=n+excluded.n,'
                        ' first_document=NULL, document=NULL',
                        zip(repeat(family), records['key'].tolist(), records['n'].tolist()),
                    )
                    db.commit()
                    self.output_keys += len(records)
            path.unlink()
        logging.getLogger(__name__).info('vocab sorted reduction: %d buffered keys -> %d SQLite writes',
                                         self.input_keys, self.output_keys)

    def close(self):
        self.directory.cleanup()
