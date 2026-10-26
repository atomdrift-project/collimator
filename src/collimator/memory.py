"""Host RAM available to training, including reclaimable ZFS ARC.

This module uses only the standard library so shell admission can execute it
directly, without importing the training stack.
"""

import sys
import time
from pathlib import Path

# Direct script execution otherwise shadows stdlib inspect with our inspect.py
# when argparse imports dataclasses (Python 3.14).
if __name__ == '__main__' and sys.path and sys.path[0] == str(Path(__file__).resolve().parent):
    sys.path.pop(0)


def cgroup_path() -> Path | None:
    try:
        for line in Path('/proc/self/cgroup').read_text().splitlines():
            if line.startswith('0::'):
                return Path('/sys/fs/cgroup') / line[3:].lstrip('/')
    except OSError:
        pass
    return None


def cgroup_memory(path: Path) -> dict:
    """Read cgroup v2 counters without importing the training stack."""
    def number(name):
        value = (path / name).read_text().strip()
        return None if value == 'max' else int(value)

    events = dict(line.split() for line in (path / 'memory.events').read_text().splitlines())
    pressure = {}
    try:
        for line in (path / 'memory.pressure').read_text().splitlines():
            kind, *fields = line.split()
            pressure[kind] = dict(field.split('=') for field in fields)
    except OSError:
        pass
    return dict(current=number('memory.current'), high=number('memory.high'),
                max=number('memory.max'), events={k: int(v) for k, v in events.items()},
                full_total=int(pressure.get('full', {}).get('total', 0)),
                full_avg10=float(pressure.get('full', {}).get('avg10', 0)))


def cgroup_headroom_gb(*, reclaim_file: bool = False) -> float | None:
    """Respect the tightest current or ancestor cgroup high/max allowance."""
    path = cgroup_path()
    root = Path('/sys/fs/cgroup')
    limits = []
    while path is not None and path != root and root in path.parents:
        try:
            current = int((path / 'memory.current').read_text())
            if reclaim_file:
                stat = dict(line.split() for line in (path / 'memory.stat').read_text().splitlines())
                # Only clean inactive file pages: mapped training inputs may be
                # reclaimed, unlike live anonymous matrices. Dirty pages still
                # require writeback and cannot be promised to a new fit.
                reclaimable = max(0, int(stat.get('inactive_file', 0))
                                  - int(stat.get('file_dirty', 0))
                                  - int(stat.get('file_writeback', 0)))
                current = max(0, current - reclaimable)
            for name in ('memory.high', 'memory.max'):
                value = (path / name).read_text().strip()
                if value != 'max':
                    limits.append(max(0, int(value) - current) / 2**30)
        except (OSError, ValueError):
            pass
        path = path.parent
    return min(limits) if limits else None


def memory_warning(current: dict, previous: dict | None, elapsed: float) -> str | None:
    events = current['events']
    delta = {key: max(0, events.get(key, 0) - (previous or current)['events'].get(key, 0))
             for key in ('high', 'max', 'oom', 'oom_kill')}
    stalled = (100 * max(0, current['full_total'] - previous['full_total']) / (elapsed * 1e6)
               if previous is not None and elapsed > 0 else current['full_avg10'])
    if not any(delta.values()) and stalled < 10:
        return None
    def gib(value):
        return 'unlimited' if value is None else f'{value / 2**30:.1f} GiB'
    kind = 'THROTTLED' if delta['high'] else 'PRESSURE'
    return (f'[memory] {kind}: used={gib(current["current"])} '
            f'high={gib(current["high"])} max={gib(current["max"])}; '
            f'all-task memory stalls={min(100, stalled):.1f}% of interval; '
            f'events high=+{delta["high"]} max=+{delta["max"]} '
            f'oom=+{delta["oom"]} oom_kill=+{delta["oom_kill"]}. '
            'Stage heartbeats do not prove worker progress.')


def watch_memory(path: Path | None, log_file: Path, *, interval: float = 30,
                 warnings_file: Path | None = None):
    previous = None
    was_pressured = False
    last = time.monotonic()
    while True:
        if path is not None and not path.exists():
            return
        if path is not None and (path / 'cgroup.events').exists():
            if 'populated 0' in (path / 'cgroup.events').read_text():
                return
        now = time.monotonic()
        stamp = time.strftime('%Y-%m-%d %H:%M:%S')
        available = available_memory_gb()
        line = f'{stamp} mem_available_gb={available:.1f}' if available is not None else f'{stamp} mem_available_gb=unknown'
        warning = None
        try:
            current = cgroup_memory(path) if path is not None else None
            if current is not None:
                line += f' cgroup_used_gb={current["current"] / 2**30:.1f} memory_full_avg10={current["full_avg10"]:.2f}'
                warning = memory_warning(current, previous, now - last)
                previous = current
        except (OSError, ValueError):
            pass
        with log_file.open('a') as output:
            output.write(line + '\n')
        message = warning or ('[memory] pressure cleared; no new throttling events and memory stalls below 10%.' if was_pressured else None)
        if message:
            if warnings_file is None:
                print(f'{stamp} {message}', file=sys.stderr, flush=True)
            else:
                with warnings_file.open('a') as output:
                    output.write(f'{stamp} {message}\n')
        was_pressured = warning is not None
        last = now
        time.sleep(interval)


def _zfs_reclaimable_bytes() -> int:
    """Match htop's ARC allowance: size above c_min, or zero without ZFS."""
    try:
        counters = {}
        with open("/proc/spl/kstat/zfs/arcstats") as arcstats:
            for line in arcstats:
                fields = line.split()
                if fields and fields[0] in ("size", "c_min"):
                    counters[fields[0]] = int(fields[2])
        size, minimum = counters["size"], counters["c_min"]
        if size < 0 or minimum < 0:
            return 0
        return max(0, size - minimum)
    except (OSError, ValueError, KeyError, IndexError):
        return 0


def available_memory_gb(*, include_arc: bool = True) -> float | None:
    """Available host RAM in GiB, or None when meminfo cannot be read.

    Linux's MemAvailable includes ordinary reclaimable caches, but omits the
    ZFS ARC allowance htop adds. ARC above its minimum can shrink under memory
    pressure; it is headroom, not a promise of immediately free memory. Keep
    caller reserves and concurrency limits on top of this estimate.
    """
    try:
        counters = {}
        with open("/proc/meminfo") as meminfo:
            for line in meminfo:
                name, _, value = line.partition(":")
                if name in ("MemAvailable", "MemTotal"):
                    counters[name] = int(value.split()[0]) * 1024
        available, total = counters["MemAvailable"], counters["MemTotal"]
        if available < 0 or total <= 0:
            return None
    except (OSError, ValueError, KeyError, IndexError):
        return None
    arc = _zfs_reclaimable_bytes() if include_arc else 0
    return min(total, available + arc) / 2**30


if __name__ == "__main__":
    if '--watch' in sys.argv:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--watch', action='store_true')
        parser.add_argument('--cgroup', type=Path)
        parser.add_argument('--log-file', type=Path, required=True)
        parser.add_argument('--warnings-file', type=Path)
        parser.add_argument('--interval', type=float, default=30)
        args = parser.parse_args()
        if args.interval <= 0:
            parser.error('--interval must be positive')
        watch_memory(args.cgroup or cgroup_path(), args.log_file,
                     interval=args.interval, warnings_file=args.warnings_file)
        sys.exit(0)
    available = available_memory_gb()
    if available is None:
        sys.exit("cannot read available host RAM from /proc/meminfo")
    # Round down so shell admission cannot approve a budget it doesn't cover.
    print(int(available))
