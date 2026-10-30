"""Regression coverage for production score identity and frozen test decisions."""

import copy
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import azoth_calibrate_ensemble as calibrate
import azoth_oof_score as oof
import azoth_policy_global_metrics as global_metrics
import azoth_route_policy_eval as policy_eval
import azoth_route_policy_search as search
import convert_bundle_to_onnx as convert
import stage_azoth_runtime_bundle as stage
import validate_azoth_bundle as validate
from collimator import bundle, cache_identity, export, features, model, model_bounds, policy, route_prune, train
from collimator.thresholds import _inspect


def score_table():
    return {
        "row_ids": np.arange(6), "labels": np.array([1, 0, 1, 0, 1, 0]),
        "file_types": np.array(["vsix"] * 6), "file_groups": np.array(["archive"] * 6),
        "sha_bucket": np.array([0, 31, 32, 63, 64, 255], dtype=np.uint8),
        "route_names": np.array(["general", "filetypes/vsix"]),
        "route_kinds": np.array(["general", "filetype"]),
        "scores": np.array([[.2, .1, .9, .2, .99, .01], [.51, .1, .9, .3, 1, 0]], dtype=np.float32),
        "score_space": np.asarray("raw"),
    }


def decision(level=25, threshold=.727):
    return {"level": level, "hostile": {"best": {"thresholds": {"filetypes/vsix": threshold}}}}


def config_and_policy():
    config = {"fit_partition": "dev", "score_space": "raw", "levels": [
        {"level": 25, "hostile": {"target_per_million": .25,
                                  "thresholds": {"general": .7, "filetypes/vsix": .727}}},
    ]}
    policies = {"fit_partition": "dev", "score_space": "raw",
                "routes": {"filetypes/vsix": {"levels": [decision()]}}}
    return config, policies


def test_partition_table_keeps_column_order_and_rejects_missing_canonical_partition():
    table = score_table()
    dev = policy.partition_table(table, "dev")
    assert dev["row_ids"].tolist() == [2, 3]
    np.testing.assert_array_equal(dev["scores"], table["scores"][:, [2, 3]])
    assert dev["route_names"].tolist() == table["route_names"].tolist()
    del table["sha_bucket"]
    with pytest.raises(ValueError, match="canonical partitions"):
        policy.partition_table(table, "test")


def test_perfect_ranking_does_not_hide_zero_deployed_recall_or_refit_on_test():
    table = score_table()
    config, policies = config_and_policy()
    before = copy.deepcopy(policies)
    report = policy.report(table, config, policies, level=25)
    entry = report["filetypes"]["vsix"]
    assert report["evaluated_on"] == "test_bucket_only"
    assert entry["n_malware"] == entry["n_benign"] == 1
    assert entry["specialist"]["pr_auc"] == 1
    assert entry["specialist"]["recall_at_25_per_100M"] == 0
    assert entry["ensemble"]["tp"] == 0
    assert entry["ensemble_strategy"] == "deployed_policy"
    assert entry["ensemble_allowed_routes"] == ["filetypes/vsix"]
    # Changing test labels changes measured quality, never selection or thresholds.
    table["labels"][:2] = [0, 1]
    changed = policy.report(table, config, policies, level=25)
    assert changed["filetypes"]["vsix"]["ensemble_strategy"] == "deployed_policy"
    assert changed["filetypes"]["vsix"]["ensemble"]["tp"] == 0
    assert policies == before
    # Training and dev rows never contribute to headline metrics.
    table["labels"][2:] = 0
    assert policy.report(table, config, policies, level=25) == changed


def test_policy_sweep_preserves_stricter_hits_even_with_empty_looser_policy():
    scores = {"filetypes/vsix": np.array([.6, .1, np.nan], dtype=np.float32)}
    levels = [decision(5, .5), {"level": 25, "hostile": {"best": {"thresholds": {}}}}]
    assert (policy.swept_margin(scores, levels, 25, 3) >= 0).tolist() == [True, False, False]
    assert not (policy.swept_margin(scores, levels, 0, 3) >= 0).any()


def test_blend_and_global_gate_use_runtime_decisions_including_missing_inputs():
    scores = {"general": np.array([.9, .1, .9], dtype=np.float32),
              "filetypes/vsix": np.array([.9, .1, np.nan], dtype=np.float32)}
    blend = {"routes": list(scores), "weights": [.5, .5], "intercept": 0., "threshold": .8}
    config, policies = config_and_policy()
    policies["routes"]["filetypes/vsix"]["levels"][0]["hostile"]["best"] = {"blend": blend}
    expected = [True, False, False]
    assert (policy.margin(scores, {"blend": blend}, 3) >= 0).tolist() == expected
    hit, counts = global_metrics._decisions(
        labels=np.array([1, 0, 1]), file_types=np.array(["vsix"] * 3),
        route_names=list(scores), scores=np.array(list(scores.values())),
        config=config, policy=policies, level=25, severity="hostile")
    assert hit.tolist() == expected
    assert counts["filetypes/vsix"] == 1
    del scores["general"]
    assert not (policy.margin(scores, {"blend": blend}, 3) >= 0).any()


def test_first_decision_budget_gate_matches_repeated_runtime_sweeps():
    rng = np.random.default_rng(12)
    file_types = np.array(['vsix'] * 80 + ['fallback'] * 40)
    scores = rng.random((2, len(file_types))).astype(np.float32)
    scores[1, ::9] = np.nan
    config, policies = config_and_policy()
    config['levels'] = [{'level': level, 'hostile': {'thresholds': {'general': threshold}}}
                        for level, threshold in [(0,.95),(25,.8),(50,.5)]]
    policies['routes']['filetypes/vsix']['levels'] = [
        {'level':0,'hostile':{'best':{'thresholds':{'general':.8}}}},
        {'level':25,'hostile':{'best':{'blend':{'routes':['general','filetypes/vsix'],
            'weights':[.5,.5],'intercept':0.,'threshold':.9}}}},
        {'level':50,'hostile':{'best':{'thresholds':{'filetypes/vsix':.4}}}},
    ]
    names = ['general', 'filetypes/vsix']
    first, groups = global_metrics._first_decisions(file_types, names, scores, config, policies)
    for level in [0, 12, 25, 50, 100]:
        expected, counts = global_metrics._decisions(labels=np.zeros(len(file_types)),
            file_types=file_types, route_names=names, scores=scores, config=config,
            policy=policies, level=level, severity='hostile')
        np.testing.assert_array_equal(first <= level, expected)
        assert {name:int(np.sum(first[indices] <= level)) for name,indices in groups.items()} == counts


def test_selected_blend_scores_and_counts_survive_runtime_float_roundtrip():
    rng = np.random.default_rng(17)
    labels = np.tile([0, 1], 100)
    scores = {name: np.clip(.3 + .4 * labels + rng.normal(0, .2, len(labels)), 0, 1).astype(np.float32)
              for name in ("general", "filetypes/vsix")}
    fit = search._fit_learned_blend(scores, labels, tuple(scores))
    assert fit is not None
    candidate = search._blend_candidate_from_fit(
        fit, labels, fp_target=1, target_per_million=10000., total_benign=100)
    assert candidate is not None
    raw = policy.margin(scores, {"blend": dict(candidate["blend"], threshold=0.)}, len(labels))
    np.testing.assert_array_equal(fit["blend_score"], raw)
    hit = policy.margin(scores, candidate, len(labels)) >= 0
    assert candidate["tp"] == int((hit & (labels == 1)).sum())
    assert candidate["fp"] == int((hit & (labels == 0)).sum())


def test_general_fallback_matches_runtime_general_threshold_on_all_available_routes():
    config, _ = config_and_policy()
    scores = {"general": np.array([.1]), "filegroups/archive": np.array([.8])}
    assert policy.routed_margin(scores, config, {}, "zip", 25, 1)[0] >= 0
    empty_policy = {"routes": {"filetypes/zip": {"levels": [
        {"level": 25, "hostile": {"best": {"thresholds": {}}}},
    ]}}}
    assert policy.routed_margin(scores, config, empty_policy, "zip", 25, 1)[0] >= 0


def test_runtime_float32_boundary_and_probability_one():
    # scan accepts a threshold of exactly one, and compares in f32.
    scores = {"general": np.array([1., .5], dtype=np.float32)}
    assert (policy.margin(scores, {"thresholds": {"general": 1.}}, 2) >= 0).tolist() == [True, False]
    assert (policy.margin(scores, {"thresholds": {"general": .5000000001}}, 2) >= 0).all()
    assert not (policy.margin(scores, {"thresholds": {"general": 1.00001}}, 2) >= 0).any()


def test_policy_report_average_precision_is_invariant_to_order_of_tied_scores():
    scores = np.array([.5, .5, .5, .5])
    labels = np.array([1, 1, 0, 0])
    assert policy_eval._pr_auc(scores, labels) == .5
    assert policy_eval._pr_auc(scores, labels[::-1]) == .5


def test_policy_eval_headline_counts_cover_all_filetypes(tmp_path, monkeypatch):
    table = score_table()
    table["labels"] = np.array([1, 1, 0, 1, 0, 0])
    table["file_types"] = np.array(["vsix"] * 3 + ["zip"] * 3)
    table_path = tmp_path / "scores.npz"
    np.savez(table_path, **table)
    general_path = tmp_path / "general.npz"
    np.savez(general_path, row_ids=table["row_ids"], canonical_shas=np.array(["00" * 32] * 6))
    policies = {"routes": {"filetypes/" + ft: {
        "filetype": ft, "levels": [{"level": 25, "hostile": {
            "best": {"thresholds": {"general": .5}},
        }}],
    } for ft in ("vsix", "zip")}}
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policies))
    output = tmp_path / "eval.json"
    monkeypatch.setattr(sys, "argv", [
        "policy-eval", "--score-table", str(table_path), "--general-scores", str(general_path),
        "--route-policies", str(policy_path), "--partition", "all",
        "--output-json", str(output), "--output-md", str(tmp_path / "eval.md"),
    ])
    assert policy_eval.main() == 0
    report = json.loads(output.read_text())
    assert report["malware"] == 3 == sum(x["malware"] for x in report["filetypes"].values())
    assert report["rows"] == report["malware"] + report["benign"] == 6
    assert report["filetypes"]["vsix"]["deployed_or_by_level"]["L25_hostile"]["recall"] == 0
    assert report["filetypes"]["zip"]["deployed_or_by_level"]["L25_hostile"]["recall"] == 0


def test_calibration_groups_cover_canonical_labels_and_aliases():
    from collimator import data
    mapping = calibrate._filetype_to_group()
    assert mapping["ooxml"] == mapping["docx"] == mapping["ole_doc"] == "documents"
    assert mapping["vbs"] == mapping["vbscript"] == "scripts"
    assert mapping["python_bytecode"] == mapping["pyc"] == "portable"
    for group, spellings in calibrate.DEPLOYMENT_GROUPS.items():
        for spelling in spellings:
            assert mapping[data.route_filetype(spelling)] == group


def test_scoring_expands_legacy_specialist_summary_to_runtime_coverage(tmp_path, monkeypatch):
    import azoth_oof_score_routes as oof_routes
    root = tmp_path / 'filetypes/ole_doc'
    root.mkdir(parents=True)
    (root / 'feature_spec.json').write_text('{}')
    summary = tmp_path / 'specialists.json'
    summary.write_text(json.dumps({'results':[{'name':'ole_doc','kind':'filetype','file_types':['ole','xls']}]}))
    monkeypatch.setattr(calibrate.bundle, 'has_model', lambda p: True)
    monkeypatch.setattr(calibrate.export, 'route_model_is_degenerate', lambda p: False)
    expected = set(calibrate._load_routes(summary)[0]['file_types'])
    assert {'ole_doc','ole','doc','xls','ppt','msi'} <= expected
    assert set(oof_routes._load_route_file_types(summary)['filetypes/ole_doc']) == expected


@pytest.mark.parametrize("args", [
    ["--partition", "all"], ["--partition", "test"], ["--oof-route-scores-dir", "/tmp/oof"],
])
def test_calibration_rejects_leaky_or_wrong_model_inputs_before_loading_data(monkeypatch, args):
    monkeypatch.setattr(sys, "argv", ["calibrate", "--db", "unused", "--general-scores", "missing", *args])
    with pytest.raises(SystemExit, match="2"):
        calibrate.main()


@pytest.mark.parametrize("changed", [None, "table", "model", "spec", "general", "routes"])
def test_test_evaluation_uses_verified_captured_scores_without_database(tmp_path, monkeypatch, changed):
    table = score_table()
    np.savez(tmp_path / "scores.npz", **table)
    general_scores = tmp_path / "general.npz"
    general_scores.write_bytes(b"captured general cache")
    records, model_routes = [], []
    for name in table["route_names"]:
        directory = tmp_path / name
        directory.mkdir(parents=True)
        (directory / "model.onnx").write_bytes(name.encode())
        (directory / "feature_spec.json").write_text("{}")
        cache_identity.write_training_provenance(directory)
        records.append({"route": str(name), "model_revision": cache_identity.model_revision(directory),
                        "spec_revision": calibrate._file_sha256(directory / "feature_spec.json")})
        model_routes.append({"name": str(name), "output_dir": str(directory)})
    config, _ = config_and_policy()
    config["levels"][0]["hostile"].update(target_per_million=.25, below_resolution=True)
    config.update(models=records, score_table_hash=calibrate._file_sha256(tmp_path / "scores.npz"),
                  model_set_hash=calibrate._hash_model_set(general_scores, model_routes))
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    before = config_path.read_bytes()
    routes = [{"route": "filetypes/vsix", "output_dir": str(tmp_path / "filetypes/vsix")}]
    monkeypatch.setattr(calibrate, "_load_routes", lambda _: routes)
    def forbidden(*args, **kwargs):
        pytest.fail("captured evaluation must not query the live database or rescore")
    monkeypatch.setattr(calibrate.data, "_connect", forbidden)
    monkeypatch.setattr(calibrate, "_score_route_worker", forbidden)
    monkeypatch.setattr(calibrate, "_calibrate_one", forbidden)
    if changed == "table":
        table["labels"][:2] = [0, 1]
        np.savez(tmp_path / "scores.npz", **table)
    elif changed == "model":
        (tmp_path / "general/model.onnx").write_bytes(b"changed")
    elif changed == "spec":
        (tmp_path / "general/feature_spec.json").write_text('{"changed":true}')
    elif changed == "general":
        general_scores.write_bytes(b"changed")
    elif changed == "routes":
        routes.clear()
    monkeypatch.setattr(sys, "argv", [
        "calibrate", "--db", "unused", "--azoth-root", str(tmp_path),
        "--general-scores", str(general_scores), "--score-table", str(tmp_path / "scores.npz"),
        "--partition", "test", "--apply-thresholds-from", str(config_path),
    ])
    if changed:
        with pytest.raises(ValueError):
            calibrate.main()
        assert not (tmp_path / "test_metrics.json").exists()
    else:
        assert calibrate.main() == 0
        result = json.loads((tmp_path / "test_metrics.json").read_text())
        assert (result["rows"], result["malware"], result["benign"]) == (2, 1, 1)
        assert result["levels"][0]["hostile"]["tp"] == 0
        assert result["levels"][0]["hostile"]["below_resolution"] is True
    assert config_path.read_bytes() == before


def test_policy_search_only_sees_dev_and_never_carries_forward_test_fitted_policies(tmp_path, monkeypatch):
    table = score_table()
    np.savez(tmp_path / "scores.npz", **table)
    config, _ = config_and_policy()
    config["score_table_hash"] = calibrate._file_sha256(tmp_path / "scores.npz")
    (tmp_path / "config.json").write_text(json.dumps(config))
    seen = []
    def process(ft):
        seen.append(search._SHARED["labels"].copy())
        np.testing.assert_array_equal(search._SHARED["routes"]["general"]["dense_probs"], table["scores"][0, 2:4])
        return "filetypes/" + ft, {"filetype": ft, "levels": []}
    monkeypatch.setattr(search, "_process_filetype", process)
    monkeypatch.setattr(search, "_write_markdown", lambda *a: None)
    monkeypatch.setattr(sys, "argv", [
        "search", "--config", str(tmp_path / "config.json"), "--score-table", str(tmp_path / "scores.npz"),
        "--output", str(tmp_path / "policy.json"), "--csv", str(tmp_path / "policy.csv"),
        "--markdown", str(tmp_path / "policy.md"), "--parallelism", "1",
        "--previous-bundle", str(tmp_path),
    ])
    assert search.main() == 0
    assert len(seen) == 1
    assert seen[0].tolist() == [1, 0]
    assert json.loads((tmp_path / "policy.json").read_text())["fit_partition"] == "dev"


@pytest.mark.parametrize("minority", [5, 40])
def test_early_stopping_uses_ap_only_and_requires_validation_support(monkeypatch, minority):
    rng = np.random.default_rng(9)
    X = rng.normal(size=(400, 3))
    y = (X[:, 0] > .5).astype(int)
    clf = model.create_classifier(int((1-y).sum()), int(y.sum()), learner="azoth", device="cpu",
                                  num_threads=1, n_estimators=12, min_child_samples=5)
    validation_y = np.array([1] * minority + [0] * 60)
    validation_X = rng.normal(size=(len(validation_y), 3))
    train._fit_model(clf, X, y, eval_set=[(validation_X, validation_y)], early_stopping_rounds=2)
    assert list(clf.evals_result_["valid_0"]) == ["average_precision"]
    if minority < train.MIN_EARLY_STOPPING_CLASS_SIZE:
        assert clf.booster_.num_trees() == 12
        assert clf.best_iteration_ == 0
    else:
        assert clf.best_iteration_ > 0


def test_general_cache_averages_ensemble_preserves_unordered_canonical_rows_and_invalidates(tmp_path, monkeypatch):
    root = tmp_path / "general"
    root.mkdir()
    (root / "models").mkdir()
    for seed in (42, 43):
        (root / "models" / f"seed_{seed}.onnx").write_bytes(str(seed).encode())
    spec_path = root / "feature_spec.json"
    spec_path.write_text("{}")
    monkeypatch.setattr(features.FeatureSpec, "load", lambda p: SimpleNamespace(standardized=False))
    class Member:
        __module__ = "lightgbm.sklearn"
        def __init__(self, probabilities):
            self.probabilities = np.array(probabilities)
        def predict_proba(self, x):
            return np.column_stack((1 - self.probabilities, self.probabilities))
    ensemble = bundle.Ensemble([Member([.5, .1]), Member([.9, .3])])
    calls = []
    monkeypatch.setattr(bundle.Ensemble, "load_bundle", lambda p: calls.append(p) or ensemble)
    rows = [(1, "own80", "a", 5, 1, "parent20"), (2, "own81", "b", 0, 0, "parent00")]
    monkeypatch.setattr(_inspect.data, "stream_labeled_metadata_full", lambda *a, **k: iter(rows))
    monkeypatch.setattr(features, "extract_labeled_metadata_from_db_batches_unordered",
                        lambda *a, **k: iter([(rows[::-1], sp.csr_matrix((2, 1)), np.array([0, 1]), {})]))
    revision = ["db1"]
    monkeypatch.setattr(cache_identity, "database_revision", lambda db: revision[0])
    cache = tmp_path / "scores.npz"
    options = dict(model_path=root, spec_path=spec_path, cache_path=cache)
    for _ in range(2):
        samples, probs, labels = _inspect._score_labeled_corpus("db", **options)
        assert [s.canonical_sha256 for s in samples] == ["parent00", "parent20"]
        assert labels.tolist() == [0, 1]
        np.testing.assert_allclose(probs, [.7, .2])
    assert calls == [root]
    with np.load(cache) as stored:
        assert str(stored["model_revision"]) == cache_identity.model_revision(root)
        assert stored["canonical_shas"].tolist() == ["parent00", "parent20"]
    revision[0] = "db2"
    _inspect._score_labeled_corpus("db", **options)
    assert len(calls) == 2
    (root / "models" / "seed_43.onnx").write_bytes(b"new seed")
    _inspect._score_labeled_corpus("db", **options)
    assert len(calls) == 3
    compact_cache = tmp_path / "compact.npz"
    for _ in range(2):
        _inspect._score_labeled_corpus(
            "db", model_path=root, spec_path=spec_path, cache_path=compact_cache, include_samples=False)
    assert len(calls) == 4
    with np.load(compact_cache) as compact:
        assert "paths" not in compact.files
        assert "canonical_shas" in compact.files
    # OOF diagnostics must also score every member, including their test part.
    oof_rows = [(*row[:-1], "00") for row in rows]
    monkeypatch.setattr(features, "extract_labeled_metadata_from_db_batches_unordered",
                        lambda db, metadata, *a, **k: iter([
                            (metadata[::-1], sp.csr_matrix((2, 1)), np.array([0, 1]), {}),
                        ]))
    result = oof._score_partition("db", root, spec_path, oof_rows, oof_fold=None, workers=1)
    np.testing.assert_allclose(result["probs"], [.7, .2])
    assert calls[-1] == root


def test_model_bounds_export_staging_and_calibration_identity(tmp_path):
    rng = np.random.default_rng(11)
    X = rng.normal(size=(300, 2))
    y = (X[:, 0] + X[:, 1] > 1).astype(int)
    root = tmp_path / "bundle"
    route = root / "general"
    route.mkdir(parents=True)
    (route / "feature_spec.json").write_text('{"abi_version":19,"trait_path_depth":3}')
    (route / "models").mkdir()
    for seed in (42, 43):
        clf = model.create_classifier(int((1-y).sum()), int(y.sum()), learner="azoth", device="cpu",
                                      num_threads=1, n_estimators=3, min_child_samples=5, random_state=seed)
        clf.fit(X, y)
        export.save_model(clf, route / "models" / f"seed_{seed}.txt")
    cache_identity.write_training_provenance(route)
    bounds = model_bounds.probability_bounds(route)
    assert bounds is not None
    probs = bundle.Ensemble.load_bundle(route).predict_proba(X)
    assert bounds[0] <= probs.min() <= probs.max() <= bounds[1]
    config = {
        "fit_partition": "dev", "score_space": "raw", "score_table_hash": "table",
        "models": [{"route": "general", "model_revision": cache_identity.model_revision(route),
                    "spec_revision": hashlib.sha256((route / "feature_spec.json").read_bytes()).hexdigest()}],
        "levels": [{"level": 25, "hostile": {"thresholds": {"general": bounds[1] / 2}}}],
    }
    policies = {"fit_partition": "dev", "score_space": "raw", "score_table_hash": "table", "routes": {}}
    assert validate._calibration_errors(root, config, policies) == []
    staged = tmp_path / "staged"
    assert stage._copy_route(route, staged / "general")
    assert validate._calibration_errors(staged, config, policies) == []
    config["levels"][0]["hostile"]["thresholds"]["general"] = (bounds[1] + 1) / 2
    assert any("upper bound" in e for e in validate._calibration_errors(root, config, policies))
    (staged / "general" / "feature_spec.json").write_text("{}")
    assert any("feature spec differs" in e for e in validate._calibration_errors(staged, config, policies))
    (staged / "general" / "training_provenance.json").unlink()
    with pytest.raises(ValueError, match="train-only provenance"):
        cache_identity.require_reserved_dev(staged / "general")


def test_converter_cannot_replace_calibrated_models_or_prune_from_test(tmp_path, monkeypatch):
    root = tmp_path / "general"
    root.mkdir()
    (root / "model.txt").write_text("not yet exported")
    (root / "feature_spec.json").write_text("{}")
    (tmp_path / "config.json").write_text("{}")
    (tmp_path / "per_filetype_metrics.json").write_text(json.dumps({
        "filetypes": {"vsix": {"specialist": {"pr_auc": .1}, "general": {"pr_auc": .9}}},
    }))
    monkeypatch.setattr(convert.route_prune, "prune_routes", lambda *a: pytest.fail("test-dependent pruning"))
    monkeypatch.setattr(sys, "argv", ["convert", "--azoth-root", str(tmp_path), "--skip-parity"])
    with pytest.raises(SystemExit, match="before calibration"):
        convert.main()


def test_general_scores_reject_one_seed_and_changed_specs(tmp_path):
    (tmp_path / "models").mkdir()
    first = tmp_path / "models" / "seed_42.onnx"
    first.write_bytes(b"first")
    (tmp_path / "feature_spec.json").write_text("{}")
    record = {"model_revision": cache_identity.model_revision(tmp_path),
              "spec_revision": calibrate._file_sha256(tmp_path / "feature_spec.json"),
              "score_space": "raw"}
    calibrate._validate_general_scores(record, tmp_path)
    (tmp_path / "models" / "seed_43.onnx").write_bytes(b"second")
    with pytest.raises(SystemExit, match="model_revision"):
        calibrate._validate_general_scores(record, tmp_path)
    record["model_revision"] = cache_identity.model_revision(tmp_path)
    (tmp_path / "feature_spec.json").write_text('{"trait_path_depth":4}')
    with pytest.raises(SystemExit, match="spec_revision"):
        calibrate._validate_general_scores(record, tmp_path)
    del record["score_space"]
    record["spec_revision"] = calibrate._file_sha256(tmp_path / "feature_spec.json")
    with pytest.raises(SystemExit, match="score_space"):
        calibrate._validate_general_scores(record, tmp_path)


def test_specialist_cache_invalidates_changed_row_positions(tmp_path, monkeypatch):
    (tmp_path / "model.onnx").write_bytes(b"model")
    (tmp_path / "feature_spec.json").write_text("{}")
    monkeypatch.setattr(cache_identity, "database_revision", lambda p: "revision")
    monkeypatch.setattr(features.FeatureSpec, "load", lambda p: SimpleNamespace(total_features=1, standardized=False))
    monkeypatch.setattr(calibrate, "_fetch_rows", lambda *a, **kw: [(1, 1), (2, 0)])
    calls = []
    monkeypatch.setattr(bundle.Ensemble, "load_bundle", lambda p: calls.append(p) or SimpleNamespace(
        predict_proba=lambda x: np.array([.7, .2], dtype=np.float32)))
    monkeypatch.setattr(features, "extract_labeled_from_db_batches", lambda *a, **kw: iter([
        (sp.csr_matrix([[1], [0]], dtype=np.float32), np.array([1, 0])),
    ]))
    route = {"output_dir": str(tmp_path), "route": "filetypes/vsix", "name": "vsix",
             "kind": "filetype", "file_types": ["vsix"]}
    options = dict(max_id=2, workers=1, refresh=False, refresh_routes=set(), feature_cache_dir=None)
    for _ in range(2):
        result = calibrate._score_route("unused", route, row_index={1: 0, 2: 1}, **options)
        assert result["indices"].tolist() == [0, 1]
    assert len(calls) == 1
    result = calibrate._score_route("unused", route, row_index={1: 1, 2: 0}, **options)
    assert result["indices"].tolist() == [1, 0]
    assert len(calls) == 2


def test_specialist_replays_feature_settings_and_invalidates_cached_values(tmp_path, monkeypatch):
    monkeypatch.setenv("COLLIMATOR_TEXT_METRICS_FULL", "0")
    monkeypatch.setenv("COLLIMATOR_EXTENDED_METRICS", "1")
    features.feature_config_from_env.cache_clear()
    (tmp_path / "model.onnx").write_bytes(b"model")
    spec = features.FeatureSpec(metric_vocab=["text_max_inline_whitespace_run"],
        feature_names=["metrics:text_max_inline_whitespace_run"], total_features=1)
    spec.save(tmp_path / "feature_spec.json")
    benchmark = tmp_path / "benchmark.json"
    monkeypatch.setattr(calibrate, "_fetch_rows", lambda *a, **kw: [(1, 1)])
    monkeypatch.setattr(bundle.Ensemble, "load_bundle", lambda p: SimpleNamespace(
        predict_proba=lambda x: x.toarray()[:, 0] / 10))
    report = {"v": "9", "files": [{"id": 0, "type": "text", "size": 100,
        "facts": {"metrics": {"text": {"max_whitespace_run": 9}}}, "traits": []}]}
    extractions = []

    def extract(*args, **kwargs):
        extractions.append(features.feature_config_from_env().include_text_metrics_full)
        yield sp.csr_matrix(features.extract(report, spec).reshape(1, -1)), np.array([1])

    monkeypatch.setattr(features, "extract_labeled_from_db_batches", extract)
    route = {"output_dir": str(tmp_path), "route": "filetypes/text", "name": "text",
             "kind": "filetype", "file_types": ["text"]}
    options = dict(row_index={1: 0}, max_id=1, workers=1, refresh=False,
                   refresh_routes=set(), feature_cache_dir=tmp_path / "cache",
                   cache_context="same-corpus-and-model")
    for enabled, expected in [("1", np.log1p(9) / 10), ("0", .9)]:
        benchmark.write_text(json.dumps({"feature_env": {"COLLIMATOR_TEXT_METRICS_FULL": enabled}}))
        for _ in range(2):
            result = calibrate._score_route("unused", route, **options)
            np.testing.assert_allclose(result["probs"], [expected])
            assert not features.feature_config_from_env().include_text_metrics_full
    assert extractions == [True, False]


def test_explicit_route_pruning_invalidates_calibration_before_publication(tmp_path):
    config, policies = config_and_policy()
    config["models"] = [{"route": "filetypes/vsix"}, {"route": "general"}]
    (tmp_path / "config.json").write_text(json.dumps(config))
    (tmp_path / "route_policies.json").write_text(json.dumps(policies))
    assert route_prune.prune_routes(tmp_path, {"filetypes/vsix"}) == {"filetypes/vsix"}
    for name in ("config.json", "route_policies.json"):
        changed = json.loads((tmp_path / name).read_text())
        assert changed["requires_recalibration"] is True
        assert changed["fit_partition"] is None
        assert changed["score_table_hash"] is None


def test_export_calibrate_select_and_report_end_to_end(tmp_path, monkeypatch):
    """Run the production entry points on actual exported scores and reserved data."""
    rng = np.random.default_rng(123)
    X = rng.normal(size=(600, 2))
    y = (X[:, 0] + X[:, 1] > .5).astype(int)
    general = tmp_path / "general"
    general.mkdir()
    clf = model.create_classifier(int((1-y).sum()), int(y.sum()), learner="azoth", device="cpu",
                                  num_threads=1, n_estimators=10, min_child_samples=5)
    clf.fit(X, y)
    export.save_model(clf, general / "model.txt")
    (general / "feature_spec.json").write_text('{"abi_version":19,"trait_path_depth":3}')
    cache_identity.write_training_provenance(general)
    holdout = rng.normal(size=(400, 2))
    labels = (holdout[:, 0] + holdout[:, 1] > .5).astype(np.int8)
    scores = bundle.Ensemble.load_bundle(general).predict_proba(holdout)
    canonical = np.array([f"{i:062x}{('20' if i < 200 else '00')}" for i in range(400)])
    arrays = dict(row_ids=np.arange(1, 401), labels=labels, probs=scores, canonical_shas=canonical,
                  corpus_requested_max_id=np.asarray(400), corpus_max_row_id=np.asarray(400),
                  model_revision=np.asarray(cache_identity.model_revision(general)),
                  spec_revision=np.asarray(calibrate._file_sha256(general / "feature_spec.json")),
                  score_space=np.asarray("raw"))
    score_path = general / "threshold_scores.npz"
    np.savez(score_path, **arrays)
    monkeypatch.setattr(calibrate, "_fetch_file_types", lambda db, ids: {int(i): "vsix" for i in ids})
    monkeypatch.setattr(calibrate, "_load_routes", lambda p: [])
    argv = ["calibrate", "--db", "unused", "--azoth-root", str(tmp_path),
            "--general-scores", str(score_path), "--score-table", str(tmp_path / "score_table.npz"),
            "--output", str(tmp_path / "config.json"), "--workers", "1"]
    monkeypatch.setattr(sys, "argv", argv)
    with monkeypatch.context() as patch:
        patch.setattr(sys, "argv", argv + ["--check-inputs-only"])
        patch.setattr(calibrate.np, "load", lambda *a, **k: pytest.fail("preflight read the score cache"))
        assert calibrate.main() == 0
    assert calibrate.main() == 0
    config = json.loads((tmp_path / "config.json").read_text())
    assert config["fit_rows"] == 200
    assert config["fit_partition"] == "dev"
    assert config["fit_malware"] == int(labels[:200].sum())
    # Mutating only test labels cannot move any selected threshold.
    arrays["labels"] = labels.copy()
    arrays["labels"][200:] = 1 - labels[200:]
    np.savez(score_path, **arrays)
    assert calibrate.main() == 0
    changed = json.loads((tmp_path / "config.json").read_text())
    assert config["levels"] == changed["levels"]
    monkeypatch.setattr(sys, "argv", [
        "search", "--config", str(tmp_path / "config.json"), "--azoth-root", str(tmp_path),
        "--score-table", str(tmp_path / "score_table.npz"),
        "--output", str(tmp_path / "route_policies.json"),
        "--csv", str(tmp_path / "policy.csv"), "--markdown", str(tmp_path / "policy.md"),
        "--parallelism", "1",
    ])
    assert search.main() == 0
    selected = json.loads((tmp_path / "route_policies.json").read_text())
    assert selected["rows"] == 200
    with np.load(tmp_path / "score_table.npz") as table:
        report = policy.report(table, changed, selected, level=25)
    assert report["n_rows_evaluated"] == 200
    assert report["filetypes"]["vsix"]["ensemble_strategy"] == "deployed_policy"
    assert validate._calibration_errors(tmp_path, changed, selected) == []
