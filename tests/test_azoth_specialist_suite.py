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
