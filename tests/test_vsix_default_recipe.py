"""The checked-in VSIX recipe reaches nightly and experiment replay unchanged."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from collimator import features, model_config

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import azoth_specialist_suite as suite

ROOT = Path(__file__).resolve().parents[1]


def test_vsix_default_pins_the_measured_layout_and_ensemble_from_any_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    recipe = model_config.load("filetypes/vsix")
    assert recipe["ensemble_seeds"] == [42, 43, 44]
    assert recipe["min_malware_training_score"] == 0
    env = recipe["feature_env"]
    assert "out/" not in env["COLLIMATOR_FEATURE_SPEC_FILE"]
    assert hashlib.sha256(Path(env["COLLIMATOR_FEATURE_SPEC_FILE"]).read_bytes()).hexdigest() == env["COLLIMATOR_FEATURE_SPEC_SHA256"]
    spec = model_config.pinned_feature_spec(env)
    assert spec.total_features == 50111
    assert spec.trait_path_depth == 3
    assert {name: len(words) for name, words in spec.keyword_vocabs.items()} == {
        "ruleword": 10000, "descword": 10000, "fullword": 10000, "contextword": 10000}


def test_python_replay_uses_default_even_without_autocollie_history(tmp_path):
    result = subprocess.run([sys.executable, str(ROOT / "scripts/azoth_train_best.py"),
        "--route", "filetypes/vsix", "--runs-dir", "", "--print-env"],
        cwd=tmp_path, text=True, capture_output=True, check=True)
    env = dict(line.split("=", 1) for line in result.stdout.splitlines())
    for key, value in {"EXP_ESTIMATORS": "400", "EXP_HOLDOUT_FRACTION": "0",
        "EXP_EARLY_STOPPING": "0", "EXP_MIN_MALWARE_SCORE": "0", "EXP_ENSEMBLE_SEEDS": "42,43,44",
        "EXP_FULL_RULE_KEYWORDS": "1", "EXP_CONTEXT_KEYWORDS": "1", "EXP_ARCHIVE_MEMBER_CONTEXT": "1"}.items():
        assert env[key] == value
    assert Path(env["COLLIMATOR_FEATURE_SPEC_FILE"]).is_file()


@pytest.mark.parametrize("explicit_estimators", [None, 123])
def test_nightly_specialist_job_overrides_history_with_the_current_recipe(tmp_path, monkeypatch, explicit_estimators):
    general = tmp_path / "general"
    general.mkdir()
    features.FeatureSpec(total_features=1, feature_names=["agg:n_findings"]).save(general / "feature_spec.json")
    target = {"kind": "filetype", "name": "vsix", "file_types": ["vsix"], "bad": 228, "good": 5804, "total": 6032}
    monkeypatch.setattr(suite, "_targets", lambda args: [target])
    monkeypatch.setattr(suite, "_publish_general", lambda *args: {"kind": "general", "name": "general"})
    monkeypatch.setattr(suite, "_load_autocollie_best_per_route", lambda *args, **kwargs: (
        {"filetypes/vsix": {"n_estimators": 50, "holdout_fraction": .3, "early_stopping_rounds": 25}},
        {"filetypes/vsix": {"COLLIMATOR_CONTEXT_KEYWORDS": "0"}}, {"filetypes/vsix": 4}))
    jobs = []

    def capture(job):
        jobs.append(job)
        return {"kind": "filetype", "name": "vsix", "file_types": ["vsix"]}

    monkeypatch.setattr(suite, "_train_target_worker", capture)
    argv = ["azoth_specialist_suite.py", "--db", "unused", "--max-id", "123",
        "--general-dir", str(general), "--output-root", str(tmp_path / "next"),
        "--summary", str(tmp_path / "specialists.json"), "--parallelism", "1", "--workers", "1",
        "--autocollie-best-runs-dir", str(tmp_path / "history")]
    if explicit_estimators is not None:
        argv += ["--train-override", f"filetypes/vsix:n_estimators={explicit_estimators}"]
    monkeypatch.setattr(sys, "argv", argv)
    assert suite.main() == 0
    assert len(jobs) == 1
    job = jobs[0]
    assert job["route_config"].n_estimators == (400 if explicit_estimators is None else explicit_estimators)
    assert job["route_config"].holdout_fraction == 0
    assert job["route_config"].early_stopping_rounds == 0
    assert job["requested_seeds"] == [42, 43, 44]
    assert job["min_malware_score"] == 0
    assert job["feature_env"]["COLLIMATOR_CONTEXT_KEYWORDS"] == "1"
    assert model_config.pinned_feature_spec(job["feature_env"]).total_features == 50111
