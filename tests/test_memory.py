"""Memory admission includes shrinkable ARC without bypassing run budgets."""

import builtins
import io
import runpy

import pytest

from collimator import features, memory


@pytest.fixture
def memory_files(monkeypatch):
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
