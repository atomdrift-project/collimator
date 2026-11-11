"""Protect exact operating budgets and the training-only selection boundary."""
from pathlib import Path
from types import SimpleNamespace
import json
import sys

import numpy as np
import pytest
from scipy import sparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import vsix_recall_tuneup as study
from vsix_depth_probe import depth_spec
from collimator.features import FeatureSpec


def test_float32_cut_excludes_tied_benign_and_survives_serialization():
    labels = np.array([0, 0, 1, 1, 1])
    probability = np.array([.8, .8, .9, .8, .7], dtype=np.float32)
    metrics = study.exact_metrics(labels, probability)
    for level in ("L0", "L25"):
        assert metrics[level]["fp"] == 0  # Cannot partially spend a score tie.
        assert metrics[level]["tp"] == 1
        assert np.float32(metrics[level]["threshold"]) > np.float32(.8)


def test_saturated_benign_can_disable_rule_without_rounding_back_to_one():
    metrics = study.exact_metrics(np.array([0, 0, 1]), np.ones(3))
    for level in ("L0", "L25"):
        assert metrics[level]["threshold"] > 1
        assert metrics[level]["tp"] == metrics[level]["fp"] == 0
    with pytest.raises(ValueError, match="benign"):
        study.exact_metrics(np.ones(2), np.array([.1, .2]))


def test_selection_protects_zero_fp_while_maximizing_l25():
    def record(zero, one):
        return {"fold_metrics": [{"L0": {"recall": zero}, "L25": {"recall": one}}] * 3}
    baseline = record(.3, .4)
    loses_zero = record(.29, .9)
    improves = record(.4, .6)
    assert study.choose([baseline, loses_zero, improves]) is improves
    assert study.choose([baseline, loses_zero]) is baseline


def test_outer_validation_never_enters_fit_or_early_stopping(tmp_path, monkeypatch):
    n = 18
    ids, labels = np.arange(n), np.arange(n) % 2
    buckets = np.repeat([.1, .45, .8], 6)
    cohort = (sparse.csr_matrix(ids[:, None]), labels, buckets, np.array(["vsix"] * n), ids)
    monkeypatch.setattr(study.tune, "load", lambda root, name: cohort if name == "train" else pytest.fail("CV accessed dev"))
    monkeypatch.setattr(study.features.FeatureSpec, "load", lambda path: SimpleNamespace(feature_names=["row"]))
    calls = []

    def fit(matrix, y, config, **kwargs):
        fitted_ids = matrix.toarray().ravel().astype(int)
        assert config.holdout_fraction == 0
        calls.append(fitted_ids)
        return SimpleNamespace(model=SimpleNamespace(booster_=set(fitted_ids)))

    def predict(fitted, matrix, threads):
        validation = matrix.toarray().ravel().astype(int)
        assert not set(validation) & fitted
        return None, None, np.linspace(.1, .9, len(validation), dtype=np.float32)

    monkeypatch.setattr(study.train, "train", fit)
    monkeypatch.setattr(study.study, "predict", predict)
    prepared = {"base": {}, "layouts": {"deployed": {}}, "cohort_sha256": "cohort"}
    args = SimpleNamespace(output=tmp_path, threads=1)
    result = study.cv(args, "trial", "deployed", {"holdout_fraction": 0.}, prepared)
    assert len(calls) == 9
    assert sum(m["rows"] for m in result["fold_metrics"]) == n
    # The same contract resumes; a changed partial/full contract is rejected.
    study.cv(args, "trial", "deployed", {"holdout_fraction": 0.}, prepared)
    assert len(calls) == 9
    with pytest.raises(ValueError, match="contract"):
        study.cv(args, "trial", "deployed", {"holdout_fraction": .1}, prepared)


def test_search_settings_replay_in_production_configuration():
    for changes in study.GRID.values():
        cfg = study.settings({}, changes, 44, 2)
        for key, value in changes.items():
            assert getattr(cfg, key) == value
        assert cfg.seed == 44
        assert cfg.learner == "azoth"


def test_complement_spends_one_shared_fp_and_retains_zero_fp_hits():
    labels = np.array([0, 0, 1, 1, 1, 1])
    baseline = np.array([.9, .4, .95, .85, .2, .2], dtype=np.float32)
    candidate = np.array([.4, .9, .2, .2, .95, .85], dtype=np.float32)
    result = study.complement_metrics(labels, baseline, candidate)
    assert result["L0"]["tp"] == 2
    assert result["L0"]["fp"] == 0
    assert result["L25"]["tp"] == 3
    assert result["L25"]["fp"] == 1


def test_paired_group_bootstrap_reports_no_uncertainty_for_identical_decisions():
    labels = np.array([0, 0, 1, 1, 1])
    p = np.array([.9, .2, .95, .95, .5], dtype=np.float32)
    metrics = study.exact_metrics(labels, p)
    result = study.confirmation_details(labels, p, p, np.array([0, 1, 2, 2, 3]), np.arange(5), metrics, metrics)
    assert result["bootstrap_positive_groups"] == 2
    for level in ("L0", "L25"):
        assert result["levels"][level]["paired_delta_ci95"] == [0., 0.]
        assert result["levels"][level]["lost_malware_ids"] == []


def test_depth_probe_preserves_keyword_and_numeric_columns_and_binds_runtime_depth(tmp_path):
    paths = ["objectives", "objectives/supply-chain", "objectives/supply-chain/hidden-payload"]
    names = [p + v for p in ("present:", "maxcrit:") for v in paths] + ["metrics:file_size", "descword:bridge"]
    base = FeatureSpec(presence_vocab=paths, feature_names=names, total_features=len(names),
                       keyword_vocabs={"descword": ["bridge"]}, trait_path_depth=3)
    historical = FeatureSpec(presence_vocab=paths + [paths[-1] + "/runtime", paths[-1] + "/runtime/bridge"])
    shallow = depth_spec(base, historical, 2)
    assert shallow.presence_vocab == paths[:2]
    assert shallow.feature_names[-2:] == names[-2:]
    deep = depth_spec(base, historical, 5)
    path = tmp_path / "feature_spec.json"
    deep.save(path)
    loaded = FeatureSpec.load(path)
    assert loaded.trait_path_depth == 5
    assert loaded.keyword_vocabs == base.keyword_vocabs
    assert "present:objectives/supply-chain/hidden-payload/runtime/bridge" in loaded.feature_names


def test_enriched_context_revision_requires_the_same_frozen_base_inputs(tmp_path):
    for name in ("deployed", "iso", "depth2", "depth4", "depth5", "keywords_rich"):
        directory = tmp_path / "layouts" / name
        directory.mkdir(parents=True)
        value = {"evaluation_revision": "raw"} if name != "keywords_rich" else {
            "evaluation_revision": "enriched", "base_evaluation_revision": "raw"}
        (directory / "ready.json").write_text(json.dumps(value))
    (tmp_path / "original").mkdir()
    (tmp_path / "original/training_config.json").write_text('{"train_config": {}}')
    (tmp_path / "cohort.json").write_text('{}')
    args = SimpleNamespace(output=tmp_path, features_only=False)
    assert study.existing_layouts(args)["layouts"]["keywords_rich"]["evaluation_revision"] == "enriched"
    (tmp_path / "layouts/keywords_rich/ready.json").write_text(json.dumps({
        "evaluation_revision": "enriched", "base_evaluation_revision": "changed"}))
    with pytest.raises(ValueError, match="base report inputs"):
        study.existing_layouts(args)
