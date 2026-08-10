"""Tests for deployable Azoth specialist training overrides."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import azoth_specialist_suite as suite  # noqa: E402
from collimator import train  # noqa: E402


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


def test_clamp_parallelism_splits_headroom_across_concurrent_suites(
    meminfo_at, monkeypatch,
) -> None:
    # 200 GB available, 32 GB reserved, 28 GB/fit -> 6 fits for a lone suite.
    meminfo_at(200)
    monkeypatch.delenv("AZOTH_CONCURRENT_SUITES", raising=False)
    monkeypatch.delenv("AZOTH_MEM_PER_FIT_GB", raising=False)
    monkeypatch.delenv("AZOTH_MEM_RESERVE_GB", raising=False)
    assert suite.clamp_parallelism_to_ram(16) == 6

    # Two suites sharing the same box must admit half each, so that the fits
    # actually resident across both still sum to ~6 rather than 12.
    monkeypatch.setenv("AZOTH_CONCURRENT_SUITES", "2")
    assert suite.clamp_parallelism_to_ram(16) == 3


def test_clamp_parallelism_never_raises_request_or_drops_below_one(
    meminfo_at, monkeypatch,
) -> None:
    meminfo_at(200)
    monkeypatch.setenv("AZOTH_CONCURRENT_SUITES", "1")
    # A request under the cap is left alone — the clamp only ever reduces.
    assert suite.clamp_parallelism_to_ram(2) == 2
    # parallelism=1 short-circuits before any /proc read.
    assert suite.clamp_parallelism_to_ram(1) == 1
    # A box with less free RAM than the reserve still admits one fit rather
    # than returning 0 and deadlocking the pool.
    meminfo_at(8)
    assert suite.clamp_parallelism_to_ram(16) == 1


def test_clamp_parallelism_returns_request_when_meminfo_unreadable(monkeypatch) -> None:
    real_open = open

    def fake_open(file, *args, **kwargs):
        if file == "/proc/meminfo":
            raise OSError("no /proc on this platform")
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open)
    assert suite.clamp_parallelism_to_ram(8) == 8
