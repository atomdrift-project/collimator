"""Held-out policy evaluation includes retained OR and blend components."""

import json
import sys

import numpy as np
import pytest

from scripts import azoth_route_policy_eval as evaluate


@pytest.mark.parametrize("blend", [False, True])
def test_cli_evaluates_retained_components_in_saved_policy(tmp_path, monkeypatch, blend):
    route = "filegroups/retained"
    decision = ({"blend": {"routes": [route], "weights": [1.0],
                            "intercept": 0.0, "threshold": 0.5}}
                if blend else {"thresholds": {route: 0.5}})
    policy = tmp_path / "route_policies.json"
    policy.write_text(json.dumps({"routes": {"filetypes/elf": {
        "filetype": "elf", "models": ["general"],
        "levels": [{"level": 0, "hostile": {"best": decision}}],
    }}}))
    scores = tmp_path / "scores.npz"
    np.savez(scores, row_ids=np.arange(3), sha_bucket=np.zeros(3, dtype=np.int8),
             labels=np.array([0, 1, 1]), file_types=np.array(["elf"] * 3),
             file_groups=np.array(["native"] * 3),
             route_names=np.array(["general", route, "filegroups/unrelated"]),
             scores=np.array([[.1, .1, .1], [.1, .9, .9], [.9, .9, .9]], dtype=np.float32))
    output = tmp_path / "eval.json"
    monkeypatch.setattr(sys, "argv", ["evaluate", "--score-table", str(scores),
        "--route-policies", str(policy), "--output-json", str(output),
        "--output-md", str(tmp_path / "eval.md")])

    assert evaluate.main() == 0

    entry = json.loads(output.read_text())["filetypes"]["elf"]
    actual = entry["deployed_or_by_level"]["L0_hostile"]
    assert actual["tp"] == 2
    assert actual["fp"] == 0
    assert route in actual["active_routes"]
    assert "filegroups/unrelated" not in entry["slice_metrics"]["routes"]
