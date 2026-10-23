"""Host RAM available to training, including reclaimable ZFS ARC.

This module uses only the standard library so shell admission can execute it
directly, without importing the training stack.
"""

import sys


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
    available = available_memory_gb()
    if available is None:
        sys.exit("cannot read available host RAM from /proc/meminfo")
    # Round down so shell admission cannot approve a budget it doesn't cover.
    print(int(available))
