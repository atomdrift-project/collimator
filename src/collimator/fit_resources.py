"""Coordinate future fit allocations across processes in a nightly run.

Reservations cover additional anonymous memory, not input matrices already
resident. Unspent reservations also reduce fetch-worker admission. A file lock
makes simultaneous admissions atomic; PID start times reject stale leases.
"""

from contextlib import contextmanager
from functools import wraps
import fcntl
import gc
import json
import logging
import math
import os
from pathlib import Path
import time
import uuid

from . import memory

log = logging.getLogger(__name__)


def release_unused_memory(reason='fit boundary'):
    """Return unused allocator pages; never count them as hypothetical credit.

    glibc can retain large freed native workspaces between seeds. Only memory
    actually released contributes to the next admission's measured headroom.
    Live matrices, fitted models and predictions keep their references.
    """
    import ctypes

    before = _process(os.getpid())
    started = time.monotonic()
    gc.collect()
    try:
        trim = ctypes.CDLL(None).malloc_trim
        trim.argtypes = [ctypes.c_size_t]
        trim.restype = ctypes.c_int
        trim(0)
    except (AttributeError, OSError):
        # Other C libraries need not expose glibc's optional allocator API.
        pass
    after = _process(os.getpid())
    released = max(0.0, before[1] - after[1]) if before and after else 0.0
    log.info('memory cleanup (%s): released %.2f GiB anonymous; now %s GiB; %.2fs',
             reason, released, f'{after[1]:.2f}' if after else 'unknown',
             time.monotonic() - started)
    return released


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


def host_reserve_gb():
    """Reserve for other host work plus bounded competitors' remaining growth.

    Coordinated pipelines also recognize the host's bounded build runner, so
    later children of an already-running pipeline pick up the policy. Count
    non-reclaimable usage against the hard limit, not
    their page cache. A 16 GiB floor remains for unrelated host allocations.
    An explicit host reserve always wins. A run can also set host-reserve-gb
    in its resource directory, including for children of an existing pipeline.
    """
    value = os.getenv('COLLIMATOR_MEM_RESERVE_GB')
    if not value and (directory := os.getenv('COLLIMATOR_FIT_RESOURCE_DIR')):
        try:
            value = (Path(directory) / 'host-reserve-gb').read_text().strip()
        except FileNotFoundError:
            pass
    if value is not None and value != '':
        reserve = float(value)
        if not math.isfinite(reserve) or reserve < 0:
            raise ValueError('host memory reserve must be finite and nonnegative')
        return reserve
    default = ('/sys/fs/cgroup/system.slice/actions.runner.werewolf-linux.linux-amd64.service'
               if os.getenv('COLLIMATOR_FIT_RESOURCE_DIR') else '')
    competitors = os.getenv('COLLIMATOR_FIT_BOUNDED_CGROUPS', default)
    if not competitors:
        return 48.0
    growth = 0.0
    try:
        for name in set(competitors.split(os.pathsep)):
            path = Path(name)
            limit = int((path / 'memory.max').read_text())
            stat = dict(line.split() for line in (path / 'memory.stat').read_text().splitlines())
            resident = sum(int(stat[key]) for key in ('anon', 'shmem', 'kernel'))
            growth += max(0, limit - resident) / 2**30
    except (OSError, ValueError, KeyError):
        return 48.0
    return min(48.0, 16.0 + growth)


def fit_wait_seconds():
    """No deadline for contention by default; explicit finite limits are opt-in."""
    value = float(os.getenv('COLLIMATOR_FIT_WAIT_SECONDS', '0'))
    if math.isnan(value) or value < 0:
        raise ValueError('COLLIMATOR_FIT_WAIT_SECONDS must be nonnegative')
    return value if value > 0 else math.inf


def _available():
    available = memory.available_memory_gb()
    kernel = memory.available_memory_gb(include_arc=False)
    if available is None or kernel is None:
        raise RuntimeError('cannot measure memory for fit admission')
    if kernel < float(os.getenv('COLLIMATOR_MEM_MIN_AVAILABLE_GB', '8')):
        return 0.0
    headroom = max(0, available - host_reserve_gb())
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
    release_unused_memory('before fit admission')
    token = uuid.uuid4().hex
    started = time.monotonic()
    interval = float(os.getenv('COLLIMATOR_FIT_POLL_SECONDS', '10'))
    last_log = -float('inf')
    try:
        while True:
            # Re-read policy while waiting so controlled operational updates
            # need not discard already-extracted matrices.
            timeout = fit_wait_seconds()
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
                            '%.1f GiB headroom, %.1f GiB reserved by fits; '
                            'host reserve %.1f GiB; %.0fs elapsed; %s',
                            need, headroom, reserved, host_reserve_gb(), elapsed,
                            'no admission deadline' if math.isinf(timeout) else
                            f'explicit admission deadline {timeout:.0f}s')
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
            try:
                return fn(X, y, config, *args, **kwargs)
            finally:
                if os.getenv('COLLIMATOR_FIT_RESOURCE_DIR'):
                    release_unused_memory('after fit')
    return wrapped
