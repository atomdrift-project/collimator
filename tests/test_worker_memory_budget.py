"""Worker admission follows changing memory without losing queued work."""

from concurrent.futures import Future, ThreadPoolExecutor
from threading import Event, Timer

import pytest

from collimator import features


@pytest.fixture
def budget_env(monkeypatch):
    monkeypatch.setenv("COLLIMATOR_MEM_AWARE_WORKERS", "1")
    monkeypatch.setenv("COLLIMATOR_MEM_RESERVE_GB", "48")
    monkeypatch.setenv("COLLIMATOR_MEM_PER_WORKER_GB", "2")
    monkeypatch.setenv("COLLIMATOR_MEM_SHARES", "1")


class ManualPool:
    def __init__(self):
        self.submitted = []

    def submit(self, fn, item):
        future = Future()
        self.submitted.append((future, fn, item))
        return future

    def complete_one(self, pending):
        for future, fn, item in self.submitted:
            if future in pending:
                future.set_result(fn(item))
                return {future}, pending - {future}
        raise AssertionError("no pending task")


@pytest.mark.parametrize("recovery", [True, False])
def test_memory_budget_grows_and_drains_without_oversubmitting(monkeypatch, budget_env, recovery):
    clock = 0.0
    headroom = 2.0 if recovery else 8.0
    monkeypatch.setattr(features.time, "monotonic", lambda: clock)
    monkeypatch.setattr(features, "ram_headroom_gb", lambda reserve: headroom)
    pool = ManualPool()
    sizes = []

    def wait(pending, *, timeout, return_when):
        nonlocal clock, headroom
        assert return_when == features.FIRST_COMPLETED
        assert timeout == pytest.approx(30)
        sizes.append(len(pending))
        if len(sizes) == 1:
            # No task completes during this interval. Recheck and grow even
            # while the original batch is blocked, or drain after pressure.
            clock += timeout
            headroom = 8.0 if recovery else 2.0
            return set(), pending
        return pool.complete_one(pending)

    monkeypatch.setattr(features, "wait", wait)
    result = list(features._memory_budgeted_unordered_iter(
        pool, abs, range(-12, 0), n_workers=4,
    ))
    assert sorted(result) == list(range(1, 13))
    assert len(pool.submitted) == 12
    if recovery:
        assert sizes[:2] == [1, 4]
        assert max(sizes) == 4
    else:
        assert sizes[:5] == [4, 4, 3, 2, 1]
        assert all(size == 1 for size in sizes[5:])


@pytest.mark.parametrize("shares,disabled,expected", [(2, False, 2), (1, False, 4), (2, True, 8)])
def test_live_admission_keeps_memory_shares_and_opt_out(
    monkeypatch, budget_env, shares, disabled, expected,
):
    monkeypatch.setenv("COLLIMATOR_MEM_SHARES", str(shares))
    monkeypatch.setenv("COLLIMATOR_MEM_AWARE_WORKERS", "0" if disabled else "1")
    monkeypatch.setattr(features, "ram_headroom_gb", lambda reserve: 8.0)
    pool = ManualPool()
    sizes = []

    def wait(pending, **kwargs):
        sizes.append(len(pending))
        return pool.complete_one(pending)

    monkeypatch.setattr(features, "wait", wait)
    assert sorted(features._memory_budgeted_unordered_iter(
        pool, abs, range(-16, 0), n_workers=8,
    )) == list(range(1, 17))
    assert max(sizes) == expected


def test_recovery_admits_another_task_while_first_is_blocked(monkeypatch, budget_env):
    first_started = Event()
    another_started = Event()
    memory_recovered = Event()
    monkeypatch.setattr(features, "_WORKER_BUDGET_REFRESH_SECONDS", 0.01)
    monkeypatch.setattr(features, "ram_headroom_gb",
                        lambda reserve: 8.0 if memory_recovered.is_set() else 0.0)

    def task(item):
        if item == 0:
            first_started.set()
            assert another_started.wait(timeout=5), "worker budget never recovered"
        else:
            another_started.set()
        return item

    timer = Timer(0.03, memory_recovered.set)
    timer.start()
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(features._memory_budgeted_unordered_iter(
                pool, task, range(12), n_workers=4,
            ))
    finally:
        timer.cancel()
    assert sorted(results) == list(range(12))


def test_serial_recovery_waits_without_dropping_a_batch(monkeypatch, budget_env):
    recovered = False
    monkeypatch.setattr(features, "ram_headroom_gb", lambda _: 8 if recovered else 0)

    def sleep(seconds):
        nonlocal recovered
        assert seconds == 30
        recovered = True

    def work(value):
        assert recovered
        return abs(value)

    monkeypatch.setattr(features.time, "sleep", sleep)
    assert list(features._memory_budgeted_serial_iter(work, range(-3, 0))) == [3, 2, 1]


def test_ordered_extraction_rebudgets_without_reordering(monkeypatch):
    monkeypatch.setattr(features, '_WORKER_BUDGET_REFRESH_SECONDS', .01)
    calls = 0
    budgets = []
    def budget():
        nonlocal calls
        calls += 1
        value = 0 if calls == 1 else (1 if calls == 2 else 3)
        budgets.append(value)
        return value
    def work(item):
        import time
        time.sleep(.03 if item == 0 else .001)
        return item
    with ThreadPoolExecutor(max_workers=3) as pool:
        assert list(features._bounded_iter(pool, work, range(12), max_inflight=budget)) == list(range(12))
    assert 0 in budgets and 1 in budgets and 3 in budgets


def test_ordered_empty_extraction_does_not_wait_at_zero_budget():
    with ThreadPoolExecutor(max_workers=1) as pool:
        assert list(features._bounded_iter(pool, abs, [], max_inflight=lambda: 0)) == []


def test_ordered_stall_reports_blocking_batch_and_completed_followers(monkeypatch, caplog):
    from collimator import memory

    clock = 0.0
    pool = ManualPool()
    calls = 0
    monkeypatch.setattr(features.time, "monotonic", lambda: clock)
    monkeypatch.setattr(memory, "cgroup_path", lambda: None)

    def wait(pending, *, timeout, return_when):
        nonlocal clock, calls
        calls += 1
        if calls == 1:
            pool.submitted[1][0].set_result(1)
            clock += timeout
            return set(), pending
        future = next(iter(pending))
        if not future.done():
            future.set_result(pool.submitted[0 if calls == 2 else 2][2])
        return {future}, set()

    monkeypatch.setattr(features, "wait", wait)
    results = list(features._bounded_ordered_dynamic_iter(
        pool, abs, range(3), lambda: 3, describe=lambda value: f"row_id={value}",
    ))
    assert results == [0, 1, 2]
    assert "row_id=0" in caplog.text
    assert "completed_behind_head=1" in caplog.text
    assert "age=30.0s" in caplog.text
