"""Triage reports must identify the decisions the serving policy actually makes."""
import json
import sys

import numpy as np
import pytest

from scripts import mislabeled_by_scope as triage


def level(value, decision, candidates=()):
    return {"level": value, "hostile": {"best": decision, "candidates": list(candidates)}}


def run_report(tmp_path, monkeypatch, *, levels, scores, labels, kind="false-positives",
               scope="ensemble", requested=25, no_cutoff=False, fallback=.99, dtype=np.float32,
               filetypes=None, selected_filetypes=None):
    tmp_path.mkdir(parents=True, exist_ok=True)
    names = list(scores)
    np.savez(tmp_path / "score_table.npz", row_ids=np.arange(1, len(labels) + 1),
             labels=np.asarray(labels), file_types=np.array(filetypes or ["example"] * len(labels)),
             route_names=np.array(names),
             scores=np.array([scores[n] for n in names], dtype=dtype))
    (tmp_path / "route_policies.json").write_text(json.dumps({"routes": {
        "filetypes/example": {"levels": levels},
    }}))
    (tmp_path / "config.json").write_text(json.dumps({"levels": [
        {"level": 0, "hostile": {"thresholds": {"general": fallback}}},
    ]}))
    argv = ["mislabeled_by_scope.py", "--score-table", str(tmp_path / "score_table.npz"),
            "--route-policies", str(tmp_path / "route_policies.json"), "--scope", scope,
            "--kind", kind, "--level", str(requested), "--db", "",
            "--output", str(tmp_path / "report.json")]
    if no_cutoff:
        argv.append("--no-cutoff")
    if selected_filetypes is not None:
        argv.extend(["--filetypes", selected_filetypes])
    monkeypatch.setattr(sys, "argv", argv)
    triage.main()
    return json.loads((tmp_path / "report.json").read_text())


@pytest.mark.parametrize("kind,label,scores,key", [
    ("false-positives", 0, [.95, .999], "false_positives"),
    ("false-negatives", 1, [.1, .01], "uncaught"),
])
def test_filetype_filter_preserves_ids_and_excludes_other_types(
    tmp_path, monkeypatch, kind, label, scores, key,
):
    result = run_report(
        tmp_path, monkeypatch, levels=[level(25, {"thresholds": {"general": .8}})],
        scores={"general": scores}, labels=[label, label], kind=kind,
        filetypes=["example", "other"], selected_filetypes="example",
    )
    assert [row["row_id"] for row in result[key]] == [1]
    assert result["filetypes"] == ["example"]


def test_unknown_filetype_filter_fails_instead_of_reviewing_everything(tmp_path, monkeypatch):
    with pytest.raises(SystemExit):
        run_report(tmp_path, monkeypatch, levels=[], scores={"general": [.9]},
                   labels=[0], selected_filetypes="typo")


def blend_level():
    return level(25, {"blend": {
        "routes": ["filetypes/a", "filegroups/b"], "weights": [.5, .5],
        "intercept": 0, "threshold": .8,
    }}, [{"policy": "joint_or_at_fp_1", "thresholds": {"filetypes/a": .8}}])


def test_ensemble_blend_does_not_use_or_surrogate(tmp_path, monkeypatch):
    scores = {"filetypes/a": [.9, .9, .9], "filegroups/b": [.1, .9, np.nan]}
    result = run_report(tmp_path / "ensemble", monkeypatch, levels=[blend_level()],
                        scores=scores, labels=[0, 0, 0])
    rows = result["false_positives"]
    # Equal-weight logits of .9 and .1 yield .5, so only the .9/.9 row fires.
    assert [r["row_id"] for r in rows] == [2]
    assert rows[0]["headline_route"] == "ensemble:blend"
    assert rows[0]["probability"] == pytest.approx(.9)
    assert rows[0]["scope_margins"]["ensemble"] == pytest.approx(.1)
    components = run_report(tmp_path / "components", monkeypatch, levels=[blend_level()],
                            scores=scores, labels=[0, 0, 0], scope="specialists")
    assert {r["row_id"] for r in components["false_positives"]} == {1, 2, 3}


@pytest.mark.parametrize("no_cutoff,expected", [(False, [1]), (True, [1, 2])])
def test_blend_false_negatives_and_missing_input(tmp_path, monkeypatch, no_cutoff, expected):
    result = run_report(tmp_path, monkeypatch, levels=[blend_level()],
                        scores={"filetypes/a": [.9, .9, .9], "filegroups/b": [.1, .9, np.nan]},
                        labels=[1, 1, 1], kind="false-negatives", no_cutoff=no_cutoff)
    assert [r["row_id"] for r in result["uncaught"]] == expected


@pytest.mark.parametrize("scope", ["ensemble", "specialists"])
def test_lower_level_decision_is_retained_between_grid_points(tmp_path, monkeypatch, scope):
    result = run_report(tmp_path, monkeypatch, levels=[
        level(0, {"thresholds": {"filetypes/a": .8}}),
        level(25, {"thresholds": {"filetypes/a": .99, "filetypes/b": .1}}),
    ], scores={"filetypes/a": [.85, .2], "filetypes/b": [.2, .2]}, labels=[0, 0],
        scope=scope, requested=24)
    # L25 must not leak into L24, and L0 remains active at L24.
    assert [r["row_id"] for r in result["false_positives"]] == [1]


def test_ensemble_retains_lower_blend_at_higher_or_level(tmp_path, monkeypatch):
    blend = blend_level()
    blend["level"] = 0
    result = run_report(tmp_path, monkeypatch, levels=[blend,
        level(25, {"thresholds": {"filetypes/a": .99}})],
        scores={"filetypes/a": [.9], "filegroups/b": [.9]}, labels=[0])
    assert [r["row_id"] for r in result["false_positives"]] == [1]
    assert result["false_positives"][0]["headline_route"] == "ensemble:blend"


@pytest.mark.parametrize("scope", ["ensemble", "specialists"])
def test_float32_cut_and_inactive_probability_one_sentinel(tmp_path, monkeypatch, scope):
    result = run_report(tmp_path, monkeypatch, levels=[level(25, {"thresholds": {
        "filetypes/a": .50000001, "filetypes/b": 1.0000002,
    }})], scores={"filetypes/a": [.5, .1], "filetypes/b": [1., 1.]}, labels=[0, 0], scope=scope)
    assert [r["row_id"] for r in result["false_positives"]] == [1]
    assert result["false_positives"][0]["margin"] == 0


def test_missing_usable_grid_uses_bundle_fallback(tmp_path, monkeypatch):
    result = run_report(tmp_path, monkeypatch, levels=[level(25, {"thresholds": {"general": 2}})],
                        scores={"general": [.9, .7]}, labels=[0, 0], fallback=.8)
    assert [r["row_id"] for r in result["false_positives"]] == [1]


def test_component_headline_uses_same_float32_boundary_as_decision(tmp_path, monkeypatch):
    result = run_report(tmp_path, monkeypatch, levels=[level(25, {"thresholds": {
        "filetypes/a": .5,
    }})], scores={"filetypes/a": [.499999999]}, labels=[0], scope="specialists",
        dtype=np.float64)
    row = result["false_positives"][0]
    assert row["margin"] == 0
    assert row["headline_route"] == "filetypes/a"
    assert row["probability"] == .5


def test_ensemble_requires_config_for_serving_fallback(tmp_path, monkeypatch):
    run_report(tmp_path, monkeypatch, levels=[], scores={"general": [.9]}, labels=[0])
    (tmp_path / "config.json").unlink()
    with pytest.raises(SystemExit, match="requires the bundle config"):
        triage.main()


def test_combined_scopes_keep_their_distinct_margins(tmp_path, monkeypatch):
    result = run_report(tmp_path, monkeypatch, levels=[blend_level()],
                        scores={"filetypes/a": [.9], "filegroups/b": [.1]}, labels=[0],
                        scope="ensemble,specialists", no_cutoff=True)
    row = result["false_positives"][0]
    assert row["scope_margins"] == pytest.approx({"ensemble": -.3, "specialists": .1})
    assert row["scopes_flagged"] == ["ensemble", "specialists"]
