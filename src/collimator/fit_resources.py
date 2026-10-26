"""Coordinate future fit allocations across processes in a nightly run.

Reservations cover additional anonymous memory, not input matrices already
resident. Unspent reservations also reduce fetch-worker admission. A file lock
makes simultaneous admissions atomic; PID start times reject stale leases.
"""

from contextlib import contextmanager
from functools import wraps
import fcntl
import json
import logging
import os
from pathlib import Path
import time
import uuid

from . import memory

log = logging.getLogger(__name__)


def _process(pid):
    try:
        root = Path('/proc') / str(pid)
        # comm may contain spaces and parentheses.
        fields = (root / 'stat').read_text().rsplit(')', 1)[1].split()
        if fields[0] == 'Z':
            return None
        anon = next(int(line.split()[1]) for line in (root / 'status').read_text().splitlines()
                    if line.startswith('RssAnon:'))
        return fields[19], anon / 2**20
    except (OSError, ValueError, StopIteration, IndexError):
        return None


def _live(entries):
    result = []
    for entry in entries:
        process = _process(entry['pid'])
        if process is not None and process[0] == entry['start']:
            result.append(entry)
    return result


def _unspent(entries):
    total = 0.0
    for entry in entries:
        process = _process(entry['pid'])
        if process is not None and process[0] == entry['start']:
            consumed = max(0, process[1] - entry['base_anon'])
            total += max(0, entry['need'] - consumed)
    return total


@contextmanager
def _locked(directory):
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    with (path / 'fit.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = path / 'fits.json'
        entries = _live(json.loads(state.read_text())) if state.exists() else []
        yield entries
        temporary = path / 'fits.json.tmp'
        temporary.write_text(json.dumps(entries))
        os.replace(temporary, state)


def reserved_headroom_gb():
    directory = os.getenv('COLLIMATOR_FIT_RESOURCE_DIR')
    if not directory:
        return 0.0
    with _locked(directory) as entries:
        return _unspent(entries)


def _available():
    available = memory.available_memory_gb()
    kernel = memory.available_memory_gb(include_arc=False)
    if available is None or kernel is None:
        raise RuntimeError('cannot measure memory for fit admission')
    if kernel < float(os.getenv('COLLIMATOR_MEM_MIN_AVAILABLE_GB', '8')):
        return 0.0
    headroom = max(0, available - float(os.getenv('COLLIMATOR_MEM_RESERVE_GB', '48')))
    limit = memory.cgroup_headroom_gb(reclaim_file=True)
    if limit is not None:
        headroom = min(headroom, limit)
    if ceiling := os.getenv('COLLIMATOR_MEM_CEILING_GB'):
        group = memory.cgroup_path()
        if group is not None:
            stat = dict(line.split() for line in (group / 'memory.stat').read_text().splitlines())
            resident = (int(stat.get('anon', 0)) + int(stat.get('kernel', 0))) / 2**30
            headroom = min(headroom, max(0, float(ceiling) - resident))
    return headroom


def estimate_fit_gb(matrix, config):
    # The original matrix is already accounted for by current memory usage.
    # Budget another split, native learner storage, and temporary work. CV
    # needs an extra subset. Never use row count alone for sparse matrices.
    if hasattr(matrix, 'indptr'):
        size = sum(a.nbytes for a in (matrix.data, matrix.indices, matrix.indptr))
    else:
        size = matrix.nbytes
    multiplier = 3.5 if config is None or config.n_folds >= 2 else 2.5
    # More threads can require more histogram workspace even at the same nnz.
    # Bound an additional 256-bin gradient/hessian workspace per feature/thread.
    threads = max(1, getattr(config, 'num_threads', None) or 8)
    histogram = matrix.shape[1] * 256 * 16 * threads / 2**30
    return 2.0 + multiplier * size / 2**30 + histogram


@contextmanager
def fit_reservation(need):
    directory = os.getenv('COLLIMATOR_FIT_RESOURCE_DIR')
    if not directory:
        yield
        return
    token = uuid.uuid4().hex
    started = time.monotonic()
    timeout = float(os.getenv('COLLIMATOR_FIT_WAIT_SECONDS', '1800'))
    interval = float(os.getenv('COLLIMATOR_FIT_POLL_SECONDS', '10'))
    last_log = -float('inf')
    try:
        while True:
            with _locked(directory) as entries:
                headroom = _available()
                reserved = _unspent(entries)
                admitted = need <= max(0, headroom - reserved)
                if admitted:
                    process = _process(os.getpid())
                    if process is None:
                        raise RuntimeError('cannot identify process for fit reservation')
                    entries.append(dict(token=token, pid=os.getpid(), start=process[0],
                                        base_anon=process[1], need=need))
            if admitted:
                log.info('fit admitted: %.1f GiB additional budget, %.1f GiB headroom, '
                         '%.1f GiB reserved by other fits; waited %.1fs',
                         need, headroom, reserved, time.monotonic() - started)
                break
            elapsed = time.monotonic() - started
            if elapsed >= timeout:
                raise MemoryError(f'fit needs {need:.1f} GiB additional RAM; only '
                                  f'{max(0, headroom - reserved):.1f} GiB available after '
                                  f'{elapsed:.0f}s. Reduce overlapping stages or the matrix footprint.')
            if elapsed - last_log >= 30:
                log.warning('fit waiting BEFORE allocation: needs %.1f GiB additional, '
                            '%.1f GiB headroom, %.1f GiB reserved; %.0fs elapsed',
                            need, headroom, reserved, elapsed)
                last_log = elapsed
            time.sleep(min(max(.1, interval), timeout - elapsed))
        yield
    finally:
        with _locked(directory) as entries:
            entries[:] = [entry for entry in entries if entry['token'] != token]


def budgeted_fit(fn):
    @wraps(fn)
    def wrapped(X, y, config=None, *args, **kwargs):
        with fit_reservation(estimate_fit_gb(X, config)):
            return fn(X, y, config, *args, **kwargs)
    return wrapped
