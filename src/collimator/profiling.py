"""Opt-in per-process/thread cProfile output for pipeline performance runs."""

from contextlib import contextmanager
import cProfile
from functools import wraps
import json
from multiprocessing.util import Finalize
import os
from pathlib import Path
import resource
import sys
import threading
import time

_profiler_lock = threading.Lock()


def event(label, kind, **values):
    """Append one live record per process, without data, SQL, or credentials."""
    directory = os.environ.get("COLLIMATOR_TIMING_DIR")
    if not directory:
        return
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    record = dict(label=label, event=kind, pid=os.getpid(), thread=threading.get_ident(),
                  timestamp=time.time(), monotonic=time.monotonic(), **values)
    payload = (json.dumps(record) + "\n").encode()
    fd = os.open(root / f"{os.getpid()}.jsonl", os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(fd, payload)
    finally:
        os.close(fd)


@contextmanager
def phase(label):
    if not os.environ.get("COLLIMATOR_TIMING_DIR"):
        yield
        return
    started, cpu = time.monotonic(), time.thread_time()
    span = time.time_ns()
    event(label, "start", span=span)
    status = "ok"
    try:
        yield
    except SystemExit as exc:
        status = "ok" if exc.code in (None, 0) else "error"
        raise
    except BaseException:
        status = "error"
        raise
    finally:
        event(label, "end", span=span, status=status,
              wall_seconds=time.monotonic() - started, thread_cpu_seconds=time.thread_time() - cpu,
              peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def timed(label):
    """Instrument an ordinary function (not a generator) only in timing runs."""
    def decorate(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            with phase(label):
                return fn(*args, **kwargs)
        return wrapped
    return decorate


def _save(profiler, label):
    profiler.disable()
    root = Path(os.environ["COLLIMATOR_PROFILE_DIR"])
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{label}-{os.getpid()}-{threading.get_ident()}-{time.time_ns()}.prof"
    profiler.dump_stats(str(path))


@contextmanager
def profile(label):
    with phase(label):
        with _cpu_profile(label):
            yield


@contextmanager
def _cpu_profile(label):
    if not os.environ.get("COLLIMATOR_PROFILE_DIR"):
        yield
        return
    with _profiler_lock:
        # Python 3.14 cProfile uses a process-wide sys.monitoring slot and
        # already observes other threads. Nested/merge scopes must reuse it.
        # Older interpreters expose their thread-local profiler via getprofile.
        monitoring = getattr(sys, "monitoring", None)
        active = sys.getprofile() is not None or (
            monitoring is not None and monitoring.get_tool(monitoring.PROFILER_ID) is not None
        )
        profiler = None if active else cProfile.Profile()
        if profiler is not None:
            profiler.enable()
    try:
        yield
    finally:
        if profiler is not None:
            _save(profiler, label)


def initialize_worker(initializer=None, initargs=()):
    """Spawn-safe initializer; multiprocessing runs Finalize before os._exit."""
    if os.environ.get("COLLIMATOR_PROFILE_DIR"):
        profiler = cProfile.Profile()
        profiler.enable()
        Finalize(None, _save, args=(profiler, "worker"), exitpriority=0)
    if initializer is not None:
        initializer(*initargs)
