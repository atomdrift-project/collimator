"""Nightly retention preserves inputs without reusing old calibration decisions."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from collimator import cache_identity, retained_components
from scripts import azoth_calibrate_ensemble as calibrate


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def model(root, route, *, scope=None, content=b"onnx-model"):
    directory = root / route
    (directory / "models").mkdir(parents=True)
    for seed in (42, 44):
        (directory / "models" / f"seed_{seed}.onnx").write_bytes(content + bytes([seed]))
        (directory / "models" / f"seed_{seed}.txt").write_text(f"native-{seed}")
    write(directory / "feature_spec.json", {"feature_names": ["filetype:tar"]})
    write(
        directory / "benchmark.json",
        {
            "training_partitions": ["train"],
            "file_types": scope or [],
            "feature_env": {"COLLIMATOR_TRAIT_PATH_DEPTH": "3"},
            "seed_health": {"accepted_seeds": [42, 44]},
        },
    )
    cache_identity.write_training_provenance(directory)
    return {
        "route": route,
        "kind": "filegroup",
        "model_revision": cache_identity.model_revision(directory),
        "spec_revision": hashlib.sha256((directory / "feature_spec.json").read_bytes()).hexdigest(),
    }


def source_bundle(root, *, global_route=False, scope=None):
    route = "filegroups/archive_recovery"
    record = model(root, route, scope=scope or ["tar", "zip"])
    config = {
        "fit_partition": "dev",
        "score_space": "raw",
        "models": [record],
        "global_auxiliary_routes": [route] if global_route else [],
        "filetype_auxiliary_routes": {} if global_route else {"tar": [route]},
    }
    write(root / "config.json", config)
    return route, config


def destination(root):
    summary = root / "specialists.json"
    write(summary, {"results": [{"name": "tar", "kind": "filetype", "unchanged": True}]})
    return summary


def test_cold_retention_preserves_members_environment_and_full_source_scope(tmp_path):
    source, target = tmp_path / "previous", tmp_path / "next"
    route, config = source_bundle(source)
    for name in [
        "calibration_scores.npz",
        "threshold_scores.npz",
        "calibrator.json",
        "thresholds.json",
    ]:
        (source / route / name).write_text("stale calibration must not travel")
    summary = destination(target)
    fields = retained_components.prepare(target, summary, source)
    assert fields["filetype_auxiliary_routes"] == config["filetype_auxiliary_routes"]
    assert cache_identity.model_revision(target / route) == config["models"][0]["model_revision"]
    assert (target / route / "benchmark.json").read_bytes() == (
        source / route / "benchmark.json"
    ).read_bytes()
    assert sorted(p.name for p in (target / route / "models").glob("*.onnx")) == [
        "seed_42.onnx",
        "seed_44.onnx",
    ]
    for name in [
        "calibration_scores.npz",
        "threshold_scores.npz",
        "calibrator.json",
        "thresholds.json",
    ]:
        assert not (target / route / name).exists()
    rows = json.loads(summary.read_text())["results"]
    assert rows[0]["unchanged"]
    assert rows[1]["name"] == "archive_recovery"
    assert (
        "zip" in rows[1]["file_types"]
    )  # Keep benigns outside the routed TAR subset for L0 anchoring.
    assert "tar.gz" in rows[1]["file_types"]
    assert rows[1]["feature_env"] == {"COLLIMATOR_TRAIT_PATH_DEPTH": "3"}
    assert (source / route / "models/seed_42.onnx").stat().st_ino != (
        target / route / "models/seed_42.onnx"
    ).stat().st_ino
    # Preflight's artifact staging can be resumed without the previous source.
    assert retained_components.prepare(target, summary) == fields
    assert len(json.loads(summary.read_text())["results"]) == 2


def test_preflight_validates_without_creating_target(tmp_path):
    source, target = tmp_path / "previous", tmp_path / "next"
    source_bundle(source)
    fields = retained_components.prepare(
        target, target / "specialists.json", source, check_only=True
    )
    assert len(fields["retained_components"]) == 1
    assert not target.exists()


@pytest.mark.parametrize("damage", ["weights", "spec", "provenance", "manifest"])
def test_invalid_source_is_rejected_before_any_copy(tmp_path, damage):
    source, target = tmp_path / "previous", tmp_path / "next"
    route, config = source_bundle(source)
    if damage == "weights":
        (source / route / "models/seed_42.onnx").write_bytes(b"replaced")
    elif damage == "spec":
        write(source / route / "feature_spec.json", {"different": True})
    elif damage == "provenance":
        write(
            source / route / "training_provenance.json", {"training_partitions": ["train", "dev"]}
        )
    else:
        config["models"][0]["model_revision"] = "stale"
        write(source / "config.json", config)
    with pytest.raises(ValueError):
        retained_components.prepare(target, target / "specialists.json", source)
    assert not target.exists()


def test_conflicting_candidate_is_not_overwritten(tmp_path):
    source, target = tmp_path / "previous", tmp_path / "next"
    route, _ = source_bundle(source)
    model(target, route, content=b"different-candidate")
    summary = destination(target)
    before = (target / route / "models/seed_42.onnx").read_bytes()
    with pytest.raises(ValueError, match="collision"):
        retained_components.prepare(target, summary, source)
    assert (target / route / "models/seed_42.onnx").read_bytes() == before
    assert len(json.loads(summary.read_text())["results"]) == 1


def test_same_weights_different_feature_environment_is_a_conflict(tmp_path):
    source, target = tmp_path / "previous", tmp_path / "next"
    route, _ = source_bundle(source)
    summary = destination(target)
    retained_components.prepare(target, summary, source)
    benchmark = json.loads((source / route / "benchmark.json").read_text())
    benchmark["feature_env"]["COLLIMATOR_TRAIT_PATH_DEPTH"] = "5"
    write(source / route / "benchmark.json", benchmark)
    with pytest.raises(ValueError, match="conflicting retained route"):
        retained_components.prepare(target, summary, source)


def test_global_auxiliary_is_rescored_globally(tmp_path):
    source, target = tmp_path / "previous", tmp_path / "next"
    route, _ = source_bundle(source, global_route=True, scope=["tar"])
    summary = destination(target)
    fields = retained_components.prepare(target, summary, source)
    assert fields["global_auxiliary_routes"] == [route]
    assert json.loads(summary.read_text())["results"][-1]["file_types"] == []


def test_retention_keeps_auxiliary_order_for_policy_tie_breaks(tmp_path):
    source, target = tmp_path / "previous", tmp_path / "next"
    routes = ["filegroups/z_recovery", "filegroups/a_recovery"]
    records = [model(source, name) for name in routes]
    write(source / "config.json", {
        "fit_partition": "dev", "score_space": "raw", "models": records,
        "global_auxiliary_routes": routes, "filetype_auxiliary_routes": {"tar": routes},
    })
    fields = retained_components.prepare(target, destination(target), source)
    assert fields["global_auxiliary_routes"] == routes
    assert fields["filetype_auxiliary_routes"] == {"tar": routes}


def test_existing_local_scope_survives_previous_bundle_without_auxiliaries(tmp_path):
    target, previous = tmp_path / "current", tmp_path / "previous"
    route, _ = source_bundle(target)
    write(previous / "config.json", {"models": []})
    summary = destination(target)
    fields = retained_components.prepare(target, summary, previous)
    assert fields["filetype_auxiliary_routes"] == {"tar": [route]}


def test_invalid_route_scope_does_not_silently_omit_scores(tmp_path):
    source, target = tmp_path / "previous", tmp_path / "next"
    source_bundle(source, scope=["zip"])
    with pytest.raises(ValueError, match="exceed its recorded source scope"):
        retained_components.prepare(target, target / "specialists.json", source)
    assert not target.exists()


@pytest.mark.parametrize(
    "route", ["filegroups/../escape", "filetypes/tar", "filegroups/../../escape"]
)
def test_invalid_auxiliary_route_names_are_rejected(tmp_path, route):
    source, target = tmp_path / "previous", tmp_path / "next"
    write(source / "config.json", {"global_auxiliary_routes": [route]})
    with pytest.raises(ValueError):
        retained_components.prepare(target, target / "specialists.json", source)


def test_calibration_preflight_checks_retained_source_without_database_or_copy(
    tmp_path, monkeypatch
):
    source, target = tmp_path / "previous", tmp_path / "next"
    route, _ = source_bundle(source)
    model(target, "general")
    summary = target / "specialists.json"
    write(summary, {"results": []})
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "calibrate",
            "--db",
            "unused",
            "--azoth-root",
            str(target),
            "--summary",
            str(summary),
            "--general-scores",
            str(target / "missing-scores.npz"),
            "--retain-auxiliaries-from",
            str(source),
            "--check-inputs-only",
        ],
    )
    monkeypatch.setattr(
        calibrate.data, "_connect", lambda *a, **kw: pytest.fail("preflight accessed DB")
    )
    assert calibrate.main() == 0
    assert not (target / route).exists()
    assert json.loads(summary.read_text()) == {"results": []}


def test_ordinary_bundle_without_auxiliaries_needs_no_retention(tmp_path):
    write(tmp_path / "config.json", {"models": []})
    assert retained_components.prepare(tmp_path, tmp_path / "no-summary.json") == {}
    assert not (tmp_path / "retained_components.json").exists()


def test_calibration_rescores_retained_models_and_emits_their_routing(tmp_path, monkeypatch):
    source, target = tmp_path / "previous", tmp_path / "next"
    route, _ = source_bundle(source)
    general = model(target, "general")
    summary = target / "specialists.json"
    write(summary, {"results": []})
    scores = target / "general/threshold_scores.npz"
    np.savez(
        scores,
        row_ids=np.arange(8),
        labels=np.array([0, 1] * 4),
        probs=np.full(8, 0.1, dtype=np.float32),
        canonical_shas=np.array(["20"] * 6 + ["00"] * 2),
        corpus_requested_max_id=7,
        model_revision=general["model_revision"],
        spec_revision=general["spec_revision"],
        score_space="raw",
    )
    called = []

    def score_jobs(jobs, ids, parallelism, log_level):
        assert len(jobs) == 1 and jobs[0]["route"]["route"] == route
        entry = jobs[0]["route"]
        assert "zip" in entry["file_types"] and "tar.gz" in entry["file_types"]
        called.append(route)
        return [
            {
                "name": route,
                "kind": "filegroup",
                "file_types": entry["file_types"],
                "output_dir": entry["output_dir"],
                "indices": np.arange(8),
                "probs": np.array([0.1, 0.9] * 4, dtype=np.float32),
            }
        ]

    monkeypatch.setattr(calibrate.export, "route_model_is_degenerate", lambda _: False)
    monkeypatch.setattr(calibrate, "_fetch_file_types", lambda db, ids: dict.fromkeys(ids, "tar"))
    monkeypatch.setattr(calibrate, "_run_score_jobs", score_jobs)
    monkeypatch.setattr(calibrate.cache_identity, "database_revision", lambda db: "fixture")
    monkeypatch.setattr(
        calibrate.data, "_connect", lambda *a, **kw: pytest.fail("unexpected DB access")
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "calibrate",
            "--db",
            "unused",
            "--azoth-root",
            str(target),
            "--summary",
            str(summary),
            "--general-scores",
            str(scores),
            "--output",
            str(target / "config.json"),
            "--score-table",
            str(target / "score_table.npz"),
            "--retain-auxiliaries-from",
            str(source),
            "--skip-level-calibration",
            "--workers",
            "1",
        ],
    )
    assert calibrate.main() == 0
    config = json.loads((target / "config.json").read_text())
    assert called == [route]
    assert config["filetype_auxiliary_routes"] == {"tar": [route]}
    assert config["fit_rows"] == 6 and config["fit_partition"] == "dev"
    assert {m["route"] for m in config["models"]} == {"general", route}
    with np.load(target / "score_table.npz") as table:
        assert table["scores"].shape == (2, 8)
        np.testing.assert_array_equal(
            table["scores"][1], np.array([0.1, 0.9] * 4, dtype=np.float32)
        )


@pytest.mark.parametrize("has_previous", [False, True])
def test_nightly_calibration_wires_retention_only_when_previous_exists(tmp_path, has_previous):
    previous = tmp_path / "previous"
    if has_previous:
        source_bundle(previous)
    result = subprocess.run(
        [
            "make",
            "-n",
            "-o",
            "venv",
            "-o",
            "check-db",
            "azoth-calibrate",
            f"AZOTH_PREVIOUS_BUNDLE={previous}",
            f"AZOTH_ROOT={tmp_path / 'next'}",
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=True,
        timeout=10,
    )
    # Preflight and dev fitting get the source; test evaluation uses the
    # already-retained local artifacts and frozen dev thresholds.
    assert result.stdout.count("--retain-auxiliaries-from") == (2 if has_previous else 0)
