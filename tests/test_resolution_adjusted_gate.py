"""Level counts, cumulative runtime decisions, and held-out gate semantics."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import azoth_calibrate_ensemble as calibrate
import azoth_policy_global_metrics as gate
import azoth_route_policy_search as search
from collimator import policy, thresholds


@pytest.mark.parametrize("benign,level,expected", [
    (2540, 0, 0), (2540, 1, 1), (2540, 25, 1),
    (1_000_000, 101, 2), (100_000_000, 25, 25), (0, 25, 0),
])
def test_shared_budget_matches_level_contract(benign, level, expected):
    assert thresholds.resolution_adjusted_fp_budget(benign, level) == expected
    assert calibrate._budget(benign, level / 100) == expected
    assert gate._budget(benign, level / 100) == expected
    assert thresholds._fp_budget_for_per_million(benign, level / 100) == expected


def candidate(labels, scores, route, target=.25):
    return search._metrics(
        labels, scores[route] >= .5, target_per_million=target,
        total_benign=int((labels == 0).sum()), thresholds={route: .5},
        policy=route, primary=route, allowed_routes=(route,),
    )


def test_small_route_one_fp_is_eligible_two_is_not():
    labels = np.array([0] * 2540 + [1] * 50)
    scores = {"general": np.zeros(len(labels), dtype=np.float32)}
    scores["general"][0] = 1
    scores["general"][-50:] = 1
    first = candidate(labels, scores, "general")
    assert not search._is_over_target(first)
    scores["general"][1] = 1
    second = candidate(labels, scores, "general")
    assert search._is_over_target(second)
    none = search._no_hit_candidate(labels, target_per_million=.25, total_benign=2540)
    assert search._choose_best([none, first, second]) is first


@pytest.mark.parametrize("same_benign", [False, True])
def test_selection_counts_union_of_benign_files_not_just_candidate_counts(same_benign):
    labels = np.array([0, 0, 1, 1, 1])
    scores = {"general": np.array([.9, .1, .9, .1, .1], dtype=np.float32),
              "filetypes/x": np.array([.9 if same_benign else .1,
                                        .1 if same_benign else .9, .9, .9, .9], dtype=np.float32)}
    levels = []
    for level, route in [(1, "general"), (25, "filetypes/x")]:
        target = level / 100
        levels.append({"level": level, "hostile": {"target_per_million": target,
            "candidates": [search._no_hit_candidate(labels, target_per_million=target, total_benign=2),
                           candidate(labels, scores, route, target)]}})
    config = {"levels": [{"level": x["level"], "hostile": {"thresholds": {}}} for x in levels]}
    search._select_swept_levels(levels, scores, labels, config, total_benign=2)
    best = levels[-1]["hostile"]["best"]
    hit = policy.swept_margin(scores, levels, 25, len(labels)) >= 0
    assert best["fp"] == int(np.sum(hit & (labels == 0))) == 1
    assert best["tp"] == int(np.sum(hit & (labels == 1))) == (3 if same_benign else 1)


def test_gate_checks_routes_individually_and_reports_uncertainty():
    labels = np.array([0] * 100 + [1] * 5 + [0] * 100 + [1] * 5)
    hit = np.zeros(len(labels), dtype=bool)
    hit[:2] = True
    groups = {"filetypes/a": np.arange(105), "filetypes/b": np.arange(105, 210)}
    result = gate._level_metrics(labels, hit, groups, .25)
    assert result["budget"] == result["fp"] == 2  # Total alone would hide route a.
    assert not result["within_budget"]
    assert result["exceeded_routes"] == ["filetypes/a"]
    hit[1] = False
    result = gate._level_metrics(labels, hit, groups, .25)
    assert result["status"] == "within_adjusted_budget"
    assert result["fp_upper_95_per_100M"] > 25  # A pass is not rate certification.
    assert gate._level_metrics(labels, hit, groups, 0)["status"] == "exceeds_adjusted_budget"


def test_no_benign_evidence_is_explicit():
    result = gate._level_metrics(np.ones(3), np.ones(3, dtype=bool),
                                 {"filetypes/x": np.arange(3)}, .25)
    assert result["status"] == "insufficient_benign_data"
    assert result["fp_upper_95_per_100M"] is None
    assert result["budget"] == 0


def test_runtime_fallback_cannot_hide_behind_empty_grid():
    table = {"labels": np.array([0, 0, 1]), "file_types": np.array(["x"] * 3),
             "route_names": np.array(["general"]), "scores": np.array([[.9, .9, .9]])}
    config = {"levels": [{"level": 25, "hostile": {
        "target_per_million": .25, "thresholds": {"general": .5}}}]}
    payload = {"routes": {"filetypes/x": {"levels": [{"level": 25,
        "hostile": {"best": {"thresholds": {}}}}]}}}
    assert "2 FP, allowance 1" in search._swept_budget_errors(payload, config, table)[0]


def test_filetype_search_generates_one_fp_choice_and_exports_a_budgeted_sweep(monkeypatch):
    rng = np.random.default_rng(48)
    labels = np.r_[np.zeros(100), np.ones(60)].astype(np.int8)
    scores = {
        "general": rng.uniform(.05, .8, len(labels)).astype(np.float32),
        "filetypes/x": np.r_[rng.uniform(.05, .5, 100), rng.uniform(.4, .95, 60)].astype(np.float32),
    }
    config = {"levels": [{"level": level, "hostile": {"target_per_million": level / 100,
               "thresholds": {"general": .9, "filetypes/x": .9}}} for level in (0, 1, 25)]}
    monkeypatch.setattr(search, "_SHARED", {
        "routes": {name: {"kind": "general" if name == "general" else "filetype",
                          "dense_probs": p} for name, p in scores.items()},
        "labels": labels, "file_types": np.array(["x"] * len(labels)),
        "filetype_to_group": {}, "config": config, "total_benign": 100,
    })
    route, entry = search._process_filetype("x")
    assert any(c["policy"] == "filetype_only_at_fp_1"
               for c in entry["levels"][-1]["hostile"]["candidates"])
    table = {"labels": labels, "file_types": np.array(["x"] * len(labels)),
             "route_names": np.array(list(scores)), "scores": np.array(list(scores.values()))}
    assert not search._swept_budget_errors({"routes": {route: entry}}, config, table)
    assert entry["levels"][-1]["hostile"]["best"]["decision_rule"] == "saved_policy_sweep"


def test_cli_gates_l25_on_test_only_without_resolution_skip(tmp_path, monkeypatch):
    config = {"levels": [{"level": 25, "hostile": {
        "target_per_million": .25, "thresholds": {"general": .5}}}]}
    policies = {"routes": {"filetypes/x": {"levels": [{"level": 25, "hostile": {
        "best": {"thresholds": {"general": .5}}}}]}}}
    for name, obj in [("config", config), ("policy", policies)]:
        (tmp_path / f"{name}.json").write_text(json.dumps(obj))
    # Test: two FPs in three benigns; dev/train have only benign low scores.
    np.savez(tmp_path / "scores.npz", labels=np.zeros(5, dtype=np.int8),
             file_types=np.array(["x"] * 5), route_names=np.array(["general"]),
             scores=np.array([[.9, .9, .1, .1, .1]], dtype=np.float32),
             sha_bucket=np.array([0, 1, 2, 32, 128]))
    argv = ["gate", "--config", str(tmp_path / "config.json"), "--policy", str(tmp_path / "policy.json"),
            "--score-table", str(tmp_path / "scores.npz"), "--output", str(tmp_path / "report.json"),
            "--markdown", str(tmp_path / "report.md"), "--fail-on-budget"]
    monkeypatch.setattr(sys, "argv", argv)
    assert gate.main() == 1
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["benign"] == 3
    assert report["levels"][0]["hostile"]["budget_gated"]
    assert report["levels"][0]["hostile"]["budget"] == 1
    # One FP shared by L0 and L25 is within the chosen L25 contract. L0's
    # separate zero-FP diagnostic must not silently veto that deployment.
    config["levels"].insert(0, {"level": 0, "hostile": {
        "target_per_million": 0, "thresholds": {"general": .5}}})
    policies["routes"]["filetypes/x"]["levels"].insert(0, {"level": 0, "hostile": {
        "best": {"thresholds": {"general": .5}}}})
    for name, obj in [("config", config), ("policy", policies)]:
        (tmp_path / f"{name}.json").write_text(json.dumps(obj))
    np.savez(tmp_path / "scores.npz", labels=np.zeros(5, dtype=np.int8),
             file_types=np.array(["x"] * 5), route_names=np.array(["general"]),
             scores=np.array([[.9, .1, .1, .1, .1]], dtype=np.float32),
             sha_bucket=np.array([0, 1, 2, 32, 128]))
    assert gate.main() == 0
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["levels"][0]["hostile"]["status"] == "exceeds_adjusted_budget"
    assert not report["levels"][0]["hostile"]["budget_gated"]
    assert report["levels"][1]["hostile"]["status"] == "within_adjusted_budget"
