import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from collimator import fit_resources as resources


def test_unspent_reservation_accounts_for_growth_and_stale_pids(monkeypatch):
    processes = {1: ('start', 15), 2: ('reused', 20)}
    monkeypatch.setattr(resources, '_process', processes.get)
    entries = [dict(pid=1, start='start', base_anon=10, need=8),
               dict(pid=2, start='old', base_anon=10, need=100),
               dict(pid=3, start='gone', base_anon=0, need=100)]
    assert resources._unspent(entries) == 3
    assert resources._live(entries) == entries[:1]


def test_fit_reservation_releases_on_exception(tmp_path, monkeypatch):
    monkeypatch.setenv('COLLIMATOR_FIT_RESOURCE_DIR', str(tmp_path))
    monkeypatch.setattr(resources, '_available', lambda: 10)
    with pytest.raises(RuntimeError):
        with resources.fit_reservation(3):
            assert resources.reserved_headroom_gb() > 2.9
            raise RuntimeError('fit failed')
    assert json.loads((tmp_path / 'fits.json').read_text()) == []


def test_idle_fit_cannot_force_allocation_beyond_budget(tmp_path, monkeypatch):
    monkeypatch.setenv('COLLIMATOR_FIT_RESOURCE_DIR', str(tmp_path))
    monkeypatch.setenv('COLLIMATOR_FIT_WAIT_SECONDS', '.001')
    monkeypatch.setattr(resources, '_available', lambda: 1)
    with pytest.raises(MemoryError, match='needs 3.0 GiB'):
        with resources.fit_reservation(3):
            pytest.fail('oversized fit admitted')
    assert json.loads((tmp_path / 'fits.json').read_text()) == []


def test_default_wait_survives_old_deadline_then_admits(tmp_path, monkeypatch):
    monkeypatch.setenv('COLLIMATOR_FIT_RESOURCE_DIR', str(tmp_path))
    monkeypatch.delenv('COLLIMATOR_FIT_WAIT_SECONDS', raising=False)
    clock = [0.0]
    monkeypatch.setattr(resources.time, 'monotonic', lambda: clock[0])
    monkeypatch.setattr(resources.time, 'sleep', lambda _: clock.__setitem__(0, clock[0] + 1900))
    monkeypatch.setattr(resources, '_available', lambda: 1 if clock[0] < 3800 else 10)
    with resources.fit_reservation(3):
        assert clock[0] == 3800
    assert json.loads((tmp_path / 'fits.json').read_text()) == []


def test_admission_timeout_can_be_disabled_while_waiting(tmp_path, monkeypatch):
    monkeypatch.setenv('COLLIMATOR_FIT_RESOURCE_DIR', str(tmp_path))
    monkeypatch.setenv('COLLIMATOR_FIT_WAIT_SECONDS', '1')
    clock = [0.0]
    monkeypatch.setattr(resources.time, 'monotonic', lambda: clock[0])
    def tick(_):
        clock[0] += 10
        monkeypatch.setenv('COLLIMATOR_FIT_WAIT_SECONDS', '0')
    monkeypatch.setattr(resources.time, 'sleep', tick)
    monkeypatch.setattr(resources, '_available', lambda: 1 if clock[0] < 20 else 10)
    with resources.fit_reservation(3):
        assert clock[0] == 20


@pytest.mark.parametrize('value', ['-1', 'nan'])
def test_invalid_wait_policy_is_rejected(monkeypatch, value):
    monkeypatch.setenv('COLLIMATOR_FIT_WAIT_SECONDS', value)
    with pytest.raises(ValueError):
        resources.fit_wait_seconds()


def test_bounded_competitor_reserve_tracks_remaining_growth(tmp_path, monkeypatch):
    monkeypatch.delenv('COLLIMATOR_MEM_RESERVE_GB', raising=False)
    monkeypatch.setenv('COLLIMATOR_FIT_BOUNDED_CGROUPS', str(tmp_path))
    (tmp_path / 'memory.max').write_text(str(32 * 2**30))
    stat = tmp_path / 'memory.stat'
    stat.write_text(f'anon {27 * 2**30}\nshmem 0\nkernel {2**30}\nfile {10 * 2**30}\n')
    assert resources.host_reserve_gb() == 20
    stat.write_text(f'anon {31 * 2**30}\nshmem 0\nkernel {2**30}\n')
    assert resources.host_reserve_gb() == 16
    # Reclaimable page cache is not deducted from the growth allowance.
    stat.write_text(f'anon 0\nshmem 0\nkernel 0\nfile {32 * 2**30}\n')
    assert resources.host_reserve_gb() == 48
    (tmp_path / 'memory.max').write_text('max')
    assert resources.host_reserve_gb() == 48
    monkeypatch.setenv('COLLIMATOR_MEM_RESERVE_GB', '60')
    assert resources.host_reserve_gb() == 60


def test_unknown_competitor_keeps_conservative_reserve(tmp_path, monkeypatch):
    monkeypatch.delenv('COLLIMATOR_MEM_RESERVE_GB', raising=False)
    monkeypatch.setenv('COLLIMATOR_FIT_BOUNDED_CGROUPS', str(tmp_path / 'missing'))
    assert resources.host_reserve_gb() == 48


def test_adaptive_reserve_still_respects_kernel_and_cgroup_limits(tmp_path, monkeypatch):
    monkeypatch.setattr(resources, 'host_reserve_gb', lambda: 20)
    monkeypatch.setattr(resources.memory, 'available_memory_gb', lambda **kw: 153)
    monkeypatch.setattr(resources.memory, 'cgroup_headroom_gb', lambda **kw: 150)
    monkeypatch.setenv('COLLIMATOR_MEM_CEILING_GB', '144')
    monkeypatch.setenv('COLLIMATOR_MEM_MIN_AVAILABLE_GB', '8')
    monkeypatch.setattr(resources.memory, 'cgroup_path', lambda: tmp_path)
    stat = tmp_path / 'memory.stat'
    stat.write_text(f'anon {5 * 2**30}\nkernel {2**30}\n')
    assert resources._available() == 133  # host availability minus reserve
    monkeypatch.setattr(resources.memory, 'cgroup_headroom_gb', lambda **kw: 80)
    assert resources._available() == 80
    stat.write_text(f'anon {100 * 2**30}\nkernel {2**30}\n')
    assert resources._available() == 43  # advisory ceiling remains enforced
    monkeypatch.setattr(resources.memory, 'available_memory_gb',
                        lambda **kw: 7 if kw.get('include_arc') is False else 153)
    assert resources._available() == 0  # ARC is not immediate free RAM


def test_estimate_scales_with_matrix_threads_and_cv():
    import numpy as np
    from types import SimpleNamespace
    X = np.zeros((100, 20), dtype=np.float32)
    small = resources.estimate_fit_gb(X, SimpleNamespace(n_folds=0, num_threads=8))
    assert resources.estimate_fit_gb(X, SimpleNamespace(n_folds=0, num_threads=32)) > small
    assert resources.estimate_fit_gb(X, SimpleNamespace(n_folds=5, num_threads=8)) > small
    assert resources.estimate_fit_gb(np.zeros((200, 20), dtype=np.float32),
                                     SimpleNamespace(n_folds=0, num_threads=8)) > small


def test_parallel_fit_admission_is_atomic_and_recovers_killed_owner(tmp_path):
    script = '''
import sys,time
from pathlib import Path
from collimator import fit_resources as r
r._available=lambda: 3.0
with r.fit_reservation(2):
    Path(sys.argv[1]).write_text('admitted')
    while True: time.sleep(.1)
'''
    env = dict(os.environ, COLLIMATOR_FIT_RESOURCE_DIR=str(tmp_path / 'state'),
               COLLIMATOR_FIT_POLL_SECONDS='.1', COLLIMATOR_FIT_WAIT_SECONDS='10')
    procs = []
    def wait_file(path):
        until = time.monotonic() + 10
        while not path.exists() and time.monotonic() < until:
            time.sleep(.05)
        assert path.exists()
    try:
        first = subprocess.Popen([sys.executable, '-c', script, str(tmp_path / 'one')], env=env)
        procs.append(first)
        wait_file(tmp_path / 'one')
        second = subprocess.Popen([sys.executable, '-c', script, str(tmp_path / 'two')], env=env)
        procs.append(second)
        time.sleep(.5)
        assert not (tmp_path / 'two').exists()
        first.kill(); first.wait(timeout=5)
        wait_file(tmp_path / 'two')
    finally:
        for process in procs:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)


def test_cleanup_returns_unused_native_pages_without_touching_live_buffers():
    # Pin heap segments with live tiny buffers, leaving freed large blocks
    # between them. Unlike an RSS mock this exercises real allocator retention.
    script = '''
import ctypes,json
from collimator import fit_resources as r
libc=ctypes.CDLL(None)
if not hasattr(libc, 'malloc_trim'):
    raise SystemExit(77)
libc.malloc.argtypes=[ctypes.c_size_t]
libc.malloc.restype=ctypes.c_void_p
libc.free.argtypes=[ctypes.c_void_p]
blocks=[]; keep=[]
for i in range(2048):
    block=libc.malloc(65536); live=libc.malloc(32)
    assert block and live
    ctypes.memset(block, 7, 65536); ctypes.memset(live, 19, 32)
    blocks.append(block); keep.append(live)
for block in blocks: libc.free(block)
released=r.release_unused_memory('test')
assert all(ctypes.string_at(p, 32) == bytes([19])*32 for p in keep)
for p in keep: libc.free(p)
print(json.dumps({'released_gib':released}))
'''
    result = subprocess.run([sys.executable, '-c', script], text=True,
                            capture_output=True, timeout=30)
    if result.returncode == 77:
        pytest.skip('glibc malloc_trim unavailable')
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['released_gib'] > .05


def test_fit_cleanup_preserves_returned_arrays_and_releases_reservation(tmp_path, monkeypatch):
    import numpy as np
    from types import SimpleNamespace
    monkeypatch.setenv('COLLIMATOR_FIT_RESOURCE_DIR', str(tmp_path))
    monkeypatch.setattr(resources, '_available', lambda: 100)
    @resources.budgeted_fit
    def fit(X, y, config):
        return X * 2, y.copy()
    X = np.arange(2000, dtype=np.float32).reshape(100, 20)
    y = np.arange(100)
    matrix, labels = fit(X, y, SimpleNamespace(n_folds=0, num_threads=1))
    np.testing.assert_array_equal(matrix, X * 2)
    np.testing.assert_array_equal(labels, y)
    assert json.loads((tmp_path / 'fits.json').read_text()) == []
