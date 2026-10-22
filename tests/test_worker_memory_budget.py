"""Worker admission follows changing memory without losing queued work."""

from concurrent.futures import Future, ThreadPoolExecutor
from threading import Event

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
    monkeypatch.setattr(features, "_WORKER_BUDGET_REFRESH_SECONDS", 0.01)
    monkeypatch.setattr(features, "ram_headroom_gb",
                        lambda reserve: 8.0 if first_started.is_set() else 0.0)

    def task(item):
        if item == 0:
            first_started.set()
            assert another_started.wait(timeout=5), "worker budget never recovered"
        else:
            another_started.set()
        return item

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(features._memory_budgeted_unordered_iter(
            pool, task, range(12), n_workers=4,
        ))
    assert sorted(results) == list(range(12))
