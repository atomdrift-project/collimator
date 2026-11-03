"""In-place nightly cleanup must not erase unretrained recovery components."""

import json

import pytest

from collimator import cache_identity, retained_components
from scripts import clean_azoth_bundle as cleaner
from tests.test_retained_components import destination, model, source_bundle, write


def test_in_place_cleanup_preserves_auxiliaries_then_rebuilds_summary(tmp_path):
    route, config = source_bundle(tmp_path)
    model(tmp_path, "general")
    cache = tmp_path / "general/cache/matrix.npz"
    cache.parent.mkdir()
    cache.write_bytes(b"expensive cached input")
    for name in ["calibration_scores.npz", "threshold_scores.npz", "calibrator.json"]:
        (tmp_path / route / name).write_text("obsolete calibration")
    summary = destination(tmp_path)
    result = cleaner.clean(tmp_path)
    assert result["retained_routes"] == [route]
    cache_identity.require_reserved_dev(tmp_path / route)
    assert cache.read_bytes() == b"expensive cached input"
    assert not (tmp_path / "general/models").exists()
    assert not (tmp_path / "general/training_provenance.json").exists()
    assert not (tmp_path / "config.json").exists()
    assert not summary.exists()
    for name in ["calibration_scores.npz", "threshold_scores.npz", "calibrator.json"]:
        assert not (tmp_path / route / name).exists()
    # A resumed general rebuild can clean again without the old config.json.
    assert cleaner.clean(tmp_path)["retained_routes"] == [route]
    write(summary, {"results": []})
    fields = retained_components.prepare(tmp_path, summary)
    assert fields["filetype_auxiliary_routes"] == config["filetype_auxiliary_routes"]
    assert json.loads(summary.read_text())["results"][0]["name"] == "archive_recovery"


def test_cleanup_rejects_damaged_retention_provenance_before_deleting_general(tmp_path):
    route, _ = source_bundle(tmp_path)
    cleaner.clean(tmp_path)
    model(tmp_path, "general")
    path = tmp_path / route / "benchmark.json"
    benchmark = json.loads(path.read_text())
    benchmark["feature_env"]["COLLIMATOR_TRAIT_PATH_DEPTH"] = "5"
    write(path, benchmark)
    with pytest.raises(ValueError, match="benchmark differs"):
        cleaner.clean(tmp_path)
    assert (tmp_path / "general/models/seed_42.onnx").exists()


def test_cleanup_refuses_auxiliary_alias_that_would_be_retrained_in_place(tmp_path):
    general = model(tmp_path, "general")
    group = model(tmp_path, "filegroups/native")
    write(
        tmp_path / "config.json",
        {
            "fit_partition": "dev",
            "score_space": "raw",
            "models": [general, group],
            "global_auxiliary_routes": ["filegroups/native"],
        },
    )
    with pytest.raises(ValueError, match="ordinary training targets"):
        cleaner.clean(tmp_path)
    assert (tmp_path / "config.json").exists()
    assert (tmp_path / "general/models/seed_42.onnx").exists()


def test_first_build_cleanup_does_not_create_missing_directory(tmp_path):
    root = tmp_path / "absent"
    assert cleaner.clean(root) == {"status": "absent", "retained_routes": []}
    assert not root.exists()


def test_explicit_removal_does_not_resurrect_old_retention_manifest(tmp_path):
    route, _ = source_bundle(tmp_path)
    cleaner.clean(tmp_path)
    write(tmp_path / "config.json", {"models": []})
    assert cleaner.clean(tmp_path)["retained_routes"] == []
    assert not (tmp_path / route / "models").exists()
    assert not (tmp_path / ".retained_components/manifest.json").exists()
    assert retained_components.prepare(tmp_path, tmp_path / "missing-summary.json") == {}


def test_cleanup_unlinks_model_directory_symlink_without_deleting_its_target(tmp_path):
    external = tmp_path / "external"
    external.mkdir()
    (external / "model.onnx").write_bytes(b"preserve")
    root = tmp_path / "bundle"
    (root / "general").mkdir(parents=True)
    (root / "general/models").symlink_to(external, target_is_directory=True)
    cleaner.clean(root)
    assert not (root / "general/models").exists()
    assert (external / "model.onnx").read_bytes() == b"preserve"
