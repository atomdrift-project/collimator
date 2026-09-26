"""Tests for deployable Azoth specialist training overrides."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import azoth_specialist_suite as suite  # noqa: E402

from collimator import train  # noqa: E402


class _FakeModel:
    def __init__(self, *, constant: bool = False) -> None:
        self.constant = constant


def _fake_train_result(
    roc_auc: float,
    *,
    avg_precision: float = 0.8,
    f1: float = 0.7,
    constant: bool = False,
):
    return SimpleNamespace(
        model=_FakeModel(constant=constant),
        metrics={
            "roc_auc": roc_auc,
            "avg_precision": avg_precision,
            "f1": f1,
        },
    )


def test_seed_health_rejects_constant_inverted_and_nonfinite_models(monkeypatch) -> None:
    monkeypatch.setattr(
        suite.export,
        "is_constant_predictor",
        lambda model: model.constant,
    )

    assert suite._seed_health_failure(
        _fake_train_result(0.99), min_roc_auc=0.5,
    ) is None
    assert "constant predictor" in suite._seed_health_failure(
        _fake_train_result(0.99, constant=True), min_roc_auc=0.5,
    )
    assert "below seed-health minimum" in suite._seed_health_failure(
        _fake_train_result(0.0058), min_roc_auc=0.5,
    )
    assert "non-finite" in suite._seed_health_failure(
        _fake_train_result(float("nan")), min_roc_auc=0.5,
    )


def test_seed_ensemble_retries_until_requested_healthy_size(monkeypatch) -> None:
    monkeypatch.setattr(
        suite.export,
        "is_constant_predictor",
        lambda model: model.constant,
    )
    auc_by_seed = {42: 0.0058, 43: 0.984, 44: 0.9992, 45: 0.97}

    accepted, attempts = suite._train_healthy_seed_ensemble(
        name="c",
        base_seed=42,
        target_members=3,
        retry_budget=3,
        min_roc_auc=0.5,
        fit_seed=lambda seed: _fake_train_result(auc_by_seed[seed]),
    )

    assert [seed for seed, _result in accepted] == [43, 44, 45]
    assert [attempt["seed"] for attempt in attempts] == [42, 43, 44, 45]
    assert attempts[0]["accepted"] is False
    assert "roc_auc=0.0058" in attempts[0]["reason"]
    assert all(attempt["accepted"] for attempt in attempts[1:])


def test_seed_ensemble_stops_after_retry_budget_is_exhausted(monkeypatch) -> None:
    monkeypatch.setattr(
        suite.export,
        "is_constant_predictor",
        lambda model: model.constant,
    )

    accepted, attempts = suite._train_healthy_seed_ensemble(
        name="broken",
        base_seed=42,
        target_members=3,
        retry_budget=2,
        min_roc_auc=0.5,
        fit_seed=lambda _seed: _fake_train_result(0.1),
    )

    assert accepted == []
    assert len(attempts) == 5
    assert all(attempt["accepted"] is False for attempt in attempts)


def test_parse_train_overrides_coerces_train_config_values() -> None:
    parsed = suite._parse_train_overrides(
        [
            "filetypes/pe:num_leaves=160",
            "filetypes/pe:learning_rate=0.03",
            "filetypes/pe:threshold_fpr_target=0.000003",
            'filetypes/pe:benign_filetype_weights={"pe": 2.5}',
            "filetypes/pe:min_child_samples=null",
        ],
    )

    assert parsed["filetypes/pe"]["num_leaves"] == 160
    assert parsed["filetypes/pe"]["learning_rate"] == 0.03
    assert parsed["filetypes/pe"]["threshold_fpr_target"] == 0.000003
    assert parsed["filetypes/pe"]["benign_filetype_weights"] == {"pe": 2.5}
    assert parsed["filetypes/pe"]["min_child_samples"] is None


def test_parse_train_overrides_rejects_unknown_train_config_field() -> None:
    with pytest.raises(ValueError, match="not a TrainConfig field"):
        suite._parse_train_overrides(["pe:this_is_not_real=1"])


def test_parse_train_overrides_rejects_non_deployable_learner_override() -> None:
    with pytest.raises(ValueError, match="not a TrainConfig field"):
        suite._parse_train_overrides(["pe:learner=litmus-xg"])


def test_route_train_config_accepts_short_and_full_route_keys() -> None:
    base = train.TrainConfig(learner="azoth", n_estimators=400, num_leaves=96)
    target = {"name": "pe", "kind": "filetype"}
    overrides = suite._parse_train_overrides(
        [
            "pe:n_estimators=250",
            "filetypes/pe:num_leaves=160",
        ],
    )

    got = suite._route_train_config(base, target, overrides)

    assert got.n_estimators == 250
    assert got.num_leaves == 160
    assert base.n_estimators == 400
    assert base.num_leaves == 96


def test_route_train_config_accepts_filegroup_route_key() -> None:
    base = train.TrainConfig(learner="azoth", reg_lambda=1.0)
    target = {"name": "scripts", "kind": "filegroup"}
    overrides = suite._parse_train_overrides(["filegroups/scripts:reg_lambda=3.5"])

    got = suite._route_train_config(base, target, overrides)

    assert got.reg_lambda == 3.5
    assert base.reg_lambda == 1.0


def _fake_meminfo(tmp_path: Path, avail_gb: float) -> Path:
    meminfo = tmp_path / "meminfo"
    meminfo.write_text(
        f"MemTotal:       264000000 kB\nMemAvailable:   {int(avail_gb * 1024 * 1024)} kB\n",
    )
    return meminfo


@pytest.fixture
def meminfo_at(tmp_path, monkeypatch):
    """Point the clamp's /proc/meminfo read at a synthetic MemAvailable."""

    real_open = open

    def _install(avail_gb: float) -> None:
        path = _fake_meminfo(tmp_path, avail_gb)

        def fake_open(file, *args, **kwargs):
            if file == "/proc/meminfo":
                return real_open(path, *args, **kwargs)
            return real_open(file, *args, **kwargs)

        monkeypatch.setattr("builtins.open", fake_open)

    return _install


def test_fit_mem_budget_splits_headroom_across_concurrent_suites(
    meminfo_at, monkeypatch,
) -> None:
    meminfo_at(200)
    monkeypatch.delenv("AZOTH_MEM_RESERVE_GB", raising=False)
    monkeypatch.delenv("AZOTH_CONCURRENT_SUITES", raising=False)
    assert suite.fit_mem_budget_gb() == pytest.approx(168)  # 200 - 32 reserved
    # Two suites sharing the box each admit fits against half the headroom.
    monkeypatch.setenv("AZOTH_CONCURRENT_SUITES", "2")
    assert suite.fit_mem_budget_gb() == pytest.approx(84)
    meminfo_at(8)  # less free than the reserve: nothing to spare, never negative
    assert suite.fit_mem_budget_gb() == 0


def test_fit_mem_budget_is_none_when_meminfo_unreadable(monkeypatch) -> None:
    real_open = open

    def fake_open(file, *args, **kwargs):
        if file == "/proc/meminfo":
            raise OSError("no /proc on this platform")
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open)
    assert suite.fit_mem_budget_gb() is None


def test_fit_mem_estimate_uses_last_measurement_with_margin(monkeypatch) -> None:
    monkeypatch.delenv("AZOTH_MEM_PER_FIT_GB", raising=False)
    assert suite.fit_mem_estimate_gb({"pe": 20.0}, "pe") == pytest.approx(24.0)
    # Never measured: assume the heaviest known fit, as the old clamp did.
    assert suite.fit_mem_estimate_gb({"pe": 20.0}, "lua") == 28.0


def test_next_fit_packs_small_fits_but_never_starves_the_head() -> None:
    def fits(*gbs: float) -> list[dict]:
        return [{"mem_gb": gb} for gb in gbs]

    # An idle pool always starts the head, even one over budget.
    assert suite.next_fit(fits(90, 1), 0, 0, 40, 8) == {"mem_gb": 90}
    # Small fits pack in beside a running one while they fit.
    assert suite.next_fit(fits(5, 5), 30, 1, 40, 8) == {"mem_gb": 5}
    # The head doesn't fit: wait, even though a smaller fit behind it would.
    queue = fits(20, 1)
    assert suite.next_fit(queue, 30, 1, 40, 8) is None
    assert queue == fits(20, 1)
    # The concurrency cap holds regardless of memory.
    assert suite.next_fit(fits(1), 1, 8, 40, 8) is None
    # Without a budget (no /proc), only the concurrency cap applies.
    assert suite.next_fit(fits(90), 90, 1, None, 8) == {"mem_gb": 90}
