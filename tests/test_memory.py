"""Memory admission includes shrinkable ARC without bypassing run budgets."""

import builtins
import io
import runpy

import pytest

from collimator import features, memory


@pytest.fixture
def memory_files(monkeypatch):
    monkeypatch.setattr(features, "cgroup_headroom_gb", lambda: None)
    files = {
        "/proc/meminfo": f"MemTotal: {251 * 2**20} kB\nMemAvailable: {52 * 2**20} kB\n",
        "/proc/spl/kstat/zfs/arcstats": (
            f"name type data\nsize 4 {135 * 2**30}\nc_min 4 {8 * 2**30}\n"
        ),
    }
    real_open = builtins.open

    def fake_open(file, *args, **kwargs):
        if str(file) in files:
            value = files[str(file)]
            if isinstance(value, Exception):
                raise value
            return io.StringIO(value)
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)
    return files


def test_arc_headroom_reaches_worker_admission_and_respects_ceiling(memory_files, monkeypatch):
    # 52 GiB MemAvailable plus 127 GiB shrinkable ARC clears the 96 GiB gate.
    assert memory.available_memory_gb() == 179
    monkeypatch.delenv("COLLIMATOR_MEM_CEILING_GB", raising=False)
    monkeypatch.setenv("COLLIMATOR_MEM_AWARE_WORKERS", "1")
    monkeypatch.setenv("COLLIMATOR_MEM_RESERVE_GB", "48")
    monkeypatch.setenv("COLLIMATOR_MEM_PER_WORKER_GB", "2")
    monkeypatch.setenv("COLLIMATOR_MEM_SHARES", "2")
    assert features.ram_headroom_gb(48) == 131
    assert features.clamp_workers_to_available_ram(48) == 32

    monkeypatch.setenv("COLLIMATOR_MEM_CEILING_GB", "192")
    monkeypatch.setattr(features, "_cgroup_anon_gb", lambda: 184)
    assert features.ram_headroom_gb(48) == 8
    assert features.clamp_workers_to_available_ram(48) == 2


@pytest.mark.parametrize("arcstats", [
    FileNotFoundError(), PermissionError(), "", "name type data\n",
    "size 4 100\n", "c_min 4 10\n", "size 4 invalid\nc_min 4 10\n",
    "size\nc_min 4 10\n", "size 4 -1\nc_min 4 10\n",
    "size 4 100\nc_min 4 -1\n", "size 4 10\nc_min 4 100\n",
    "size 4 100\nc_min 4 100\n",
])
def test_missing_invalid_or_minimum_arc_uses_kernel_available(memory_files, arcstats):
    memory_files["/proc/spl/kstat/zfs/arcstats"] = arcstats
    assert memory.available_memory_gb() == 52


def test_estimate_cannot_exceed_physical_ram(memory_files):
    memory_files["/proc/spl/kstat/zfs/arcstats"] = f"size 4 {1000 * 2**30}\nc_min 4 0\n"
    assert memory.available_memory_gb() == 251


def test_kernel_floor_pauses_workers_even_when_arc_is_large(memory_files, monkeypatch):
    memory_files["/proc/meminfo"] = (
        f"MemTotal: {251 * 2**20} kB\nMemAvailable: {7 * 2**20} kB\n"
    )
    monkeypatch.setenv("COLLIMATOR_MEM_MIN_AVAILABLE_GB", "8")
    monkeypatch.setenv("COLLIMATOR_MEM_AWARE_WORKERS", "1")
    assert memory.available_memory_gb() == 134
    assert memory.available_memory_gb(include_arc=False) == 7
    assert features.ram_headroom_gb(48) == 0
    assert features.clamp_workers_to_available_ram(24, allow_zero=True) == 0


@pytest.mark.parametrize("meminfo", [
    FileNotFoundError(), PermissionError(), "", "MemTotal: 1024 kB\n",
    "MemAvailable: 1024 kB\n", "MemTotal: 1024 kB\nMemAvailable: invalid kB\n",
    "MemTotal: 1024 kB\nMemAvailable:\n",
    "MemTotal: 1024 kB\nMemAvailable: -1 kB\n",
    "MemTotal: 0 kB\nMemAvailable: 1024 kB\n",
])
def test_invalid_meminfo_cannot_admit_using_arc_alone(memory_files, meminfo):
    memory_files["/proc/meminfo"] = meminfo
    assert memory.available_memory_gb() is None
    assert features.ram_headroom_gb(48) is None
    with pytest.raises(SystemExit, match="cannot read available host RAM"):
        runpy.run_path(memory.__file__, run_name="__main__")


def test_shell_entry_point_rounds_down(memory_files, capsys):
    memory_files["/proc/meminfo"] = (
        f"MemTotal: {251 * 2**20} kB\nMemAvailable: {int(52.9 * 2**20)} kB\n"
    )
    runpy.run_path(memory.__file__, run_name="__main__")
    assert capsys.readouterr().out == "179\n"


def test_cgroup_headroom_includes_parent_and_soft_limit(tmp_path, monkeypatch):
    # Use a temporary tree but retain the real root boundary for traversal.
    from pathlib import Path
    root = tmp_path / "parent"
    child = root / "child"
    child.mkdir(parents=True)
    for path, current, high, maximum in ((root, 140, 144, 160), (child, 20, 80, 100)):
        for name, value in (("current", current), ("high", high), ("max", maximum)):
            (path / f"memory.{name}").write_text(str(value * 2**30))
    monkeypatch.setattr(memory, "cgroup_path", lambda: Path('/sys/fs/cgroup/parent/child'))
    read = Path.read_text
    def fake_read(path, *args, **kwargs):
        prefix = '/sys/fs/cgroup/parent'
        if str(path).startswith(prefix):
            path = root / str(path)[len(prefix):].lstrip('/')
        return read(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'read_text', fake_read)
    assert memory.cgroup_headroom_gb() == 4
    (root / 'memory.high').write_text('max')
    assert memory.cgroup_headroom_gb() == 20
    (root / 'memory.current').write_text(str(161 * 2**30))
    assert memory.cgroup_headroom_gb() == 0


def test_worker_admission_honors_actual_cgroup_without_env_ceiling(memory_files, monkeypatch):
    monkeypatch.delenv('COLLIMATOR_MEM_CEILING_GB', raising=False)
    monkeypatch.setattr(features, 'cgroup_headroom_gb', lambda: 3)
    assert features.ram_headroom_gb(48) == 3


def test_memory_warning_uses_counter_deltas_not_old_events():
    before = dict(current=119 * 2**30, high=112 * 2**30, max=160 * 2**30,
                  events={'high': 1_000_000, 'max': 0, 'oom': 0, 'oom_kill': 0},
                  full_total=1_000_000, full_avg10=0)
    after = dict(before, events=dict(before['events'], high=1_000_050), full_total=22_000_000)
    warning = memory.memory_warning(after, before, 30)
    assert 'THROTTLED' in warning
    assert '70.0%' in warning
    assert 'high=+50' in warning
    assert 'used=119.0 GiB' in warning
    assert memory.memory_warning(after, after, 30) is None
    assert memory.memory_warning(before, None, 30) is None


def test_watch_cli_works_without_importing_training_dependencies(tmp_path):
    import subprocess
    from pathlib import Path
    (tmp_path / 'cgroup.events').write_text('populated 0\nfrozen 0\n')
    result = subprocess.run(
        ['/usr/bin/python3', str(Path(memory.__file__).resolve()), '--watch',
         '--cgroup', str(tmp_path), '--log-file', str(tmp_path / 'log')],
        text=True, capture_output=True, timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_watch_writes_warning_and_recovery_to_main_log(tmp_path, monkeypatch):
    group = tmp_path / 'group'
    group.mkdir()
    for name, value in {'current': 119, 'high': 112, 'max': 160}.items():
        (group / f'memory.{name}').write_text(str(value * 2**30))
    (group / 'memory.events').write_text('high 500\nmax 0\noom 0\noom_kill 0\n')
    (group / 'memory.pressure').write_text('full avg10=70 avg60=70 avg300=70 total=1000000\n')
    (group / 'cgroup.events').write_text('populated 1\n')
    monkeypatch.setattr(memory, 'available_memory_gb', lambda: 48)
    ticks = 0
    def sleep(_):
        nonlocal ticks
        ticks += 1
        if ticks == 2:
            (group / 'cgroup.events').write_text('populated 0\n')
    monkeypatch.setattr(memory.time, 'sleep', sleep)
    memory.watch_memory(group, tmp_path / 'samples', warnings_file=tmp_path / 'main.log')
    messages = (tmp_path / 'main.log').read_text()
    assert '[memory] PRESSURE' in messages
    assert '70.0%' in messages
    assert 'pressure cleared' in messages
    assert len((tmp_path / 'samples').read_text().splitlines()) == 2
