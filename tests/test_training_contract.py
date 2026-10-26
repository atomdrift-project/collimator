"""Regression tests for evaluation identity and effective training settings."""

import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import azoth_score_deployed as baseline
import azoth_specialist_suite as suite
from collimator import cache_identity, experiment, export, features, model, train
from collimator.autocollie_selection import evaluation_cohort


@pytest.fixture(autouse=True)
def clear_feature_config():
    features.feature_config_from_env.cache_clear()
    yield
    features.feature_config_from_env.cache_clear()


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "samples.db"
    with sqlite3.connect(path) as conn:
        conn.execute("""CREATE TABLE samples (
            id INTEGER PRIMARY KEY, sha256 TEXT, canonical_sha256 TEXT,
            label TEXT, score INTEGER, file_type TEXT, cleave_result TEXT, skip TEXT)""")
        for i, suffix in enumerate(("80", "20", "00"), 1):
            sha = f"{i:062x}" + suffix
            conn.execute("INSERT INTO samples VALUES (?,?,?,?,?,?,?,?)",
                         (i, sha, sha, "bad", 5, "go", "{}", ""))
    return path


@pytest.mark.parametrize("natural", [False, True])
def test_training_knobs_and_seed_cannot_change_evaluation_cohort(monkeypatch, natural):
    rows = []
    for i in range(500):
        rows.extend((i * 4 + j, label, partition, str(i * 4 + j), i % 5)
                    for j, label, partition in ((1, 1, "train"), (2, 0, "train"),
                                                 (3, 1, "dev"), (4, 0, "dev")))
    monkeypatch.setattr(experiment.data, "stream_partitioned_metadata_grouped",
                        lambda *a, **kw: iter(rows))
    def sample(seed, cap, cutoff):
        return experiment.sample_partitioned_reports(
            "unused", train_samples=cap, max_test_samples=100, seed=seed,
            min_malware_training_score=cutoff, test_natural_prevalence=natural,
        )
    a, b, c = sample(42, 100, 0), sample(42, 100, 4), sample(99, 200, 4)
    assert {s.row_id for s in a.test_samples} == {s.row_id for s in b.test_samples} == {s.row_id for s in c.test_samples}
    assert {s.row_id for s in a.train_samples if s.label == 0} == {s.row_id for s in b.train_samples if s.label == 0}


def test_mutations_invalidate_data_but_only_relevant_rows_invalidate_evaluation(db):
    before = cache_identity.database_revision(db)
    ev = cache_identity.evaluation_revision(db, [2], [1])
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE samples SET score=6 WHERE id=1")
    assert cache_identity.database_revision(db) != before
    assert cache_identity.evaluation_revision(db, [2], [1]) == ev
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE samples SET cleave_result='{\"new\":true}' WHERE id=2")
    assert cache_identity.evaluation_revision(db, [2], [1]) != ev
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE samples SET label='good' WHERE id=2")
    with pytest.raises(ValueError, match="labels changed"):
        cache_identity.evaluation_revision(db, [2], [1])
    with pytest.raises(ValueError, match="deleted"):
        cache_identity.evaluation_revision(db, [99])


def test_feature_implementation_invalidates_matrix_cache(monkeypatch):
    cfg = features.feature_config_from_env()
    monkeypatch.setattr(cache_identity, "code_revision", lambda stage: "old")
    before = experiment._matrix_cache_key("corpus", cfg, {})
    monkeypatch.setattr(cache_identity, "code_revision", lambda stage: "new")
    assert experiment._matrix_cache_key("corpus", cfg, {}) != before


def test_bootstrap_comparison_separates_changed_row_versions():
    a = {"test_sample_row_ids": [1, 2], "evaluation_revision": "before"}
    b = {"test_sample_row_ids": [2, 1], "evaluation_revision": "before"}
    assert evaluation_cohort(a) == evaluation_cohort(b)
    b["evaluation_revision"] = "after"
    assert evaluation_cohort(a) != evaluation_cohort(b)


@pytest.mark.parametrize("ensemble", [False, True])
def test_cached_run_restores_only_its_own_complete_bundle(tmp_path, ensemble):
    runs = tmp_path / "runs"
    runs.mkdir()
    (runs / "abc_feature_spec.json").write_text('{"run":"abc"}')
    original = tmp_path / "original"
    original.mkdir()
    if ensemble:
        (original / "models").mkdir()
        for seed in (42, 43):
            (original / "models" / f"seed_{seed}.txt").write_text(str(seed))
        import shutil
        shutil.copytree(original / "models", runs / "abc_models")
    else:
        for ext in ("txt", "onnx"):
            (original / f"model.{ext}").write_text("abc-" + ext)
            (runs / f"abc_model.{ext}").write_text("abc-" + ext)
    proof = cache_identity.write_training_provenance(original)
    # Missing provenance must not restore an unverified model.
    (tmp_path / "model.onnx").write_text("unrelated run")
    assert not experiment._restore_run_artifacts(tmp_path, "abc")
    assert (tmp_path / "model.onnx").read_text() == "unrelated run"
    (runs / "abc_training_provenance.json").write_text(json.dumps(proof))
    assert experiment._restore_run_artifacts(tmp_path, "abc")
    assert cache_identity.model_revision(tmp_path) == proof["model_revision"]
    assert json.loads((tmp_path / "feature_spec.json").read_text()) == {"run": "abc"}
    source = runs / "abc_models" / "seed_42.txt" if ensemble else runs / "abc_model.onnx"
    source.write_text("damaged")
    assert not experiment._restore_run_artifacts(tmp_path, "abc")


@pytest.mark.parametrize("raises", [False, True])
def test_failed_onnx_export_cannot_reuse_previous_model(tmp_path, monkeypatch, raises):
    class Booster:
        def save_model(self, path):
            Path(path).write_text("new model")
        def num_feature(self):
            return 2
    classifier = type("Classifier", (), {"__module__": "lightgbm.sklearn", "booster_": Booster()})()
    def convert(*args):
        if raises:
            raise ValueError("conversion failed")
        return False
    monkeypatch.setattr(export, "export_lightgbm_onnx", convert)
    (tmp_path / "model.onnx").write_text("old model")
    export.save_model(classifier, tmp_path / "model.txt")
    assert (tmp_path / "model.txt").read_text() == "new model"
    assert not (tmp_path / "model.onnx").exists()


def test_concurrent_artifact_restores_keep_model_spec_and_provenance_together(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    runs = tmp_path / "runs"
    runs.mkdir()
    for key in ("first", "second"):
        original = tmp_path / key
        original.mkdir()
        (original / "model.txt").write_text(key)
        proof = cache_identity.write_training_provenance(original)
        (runs / f"{key}_model.txt").write_text(key)
        (runs / f"{key}_feature_spec.json").write_text(json.dumps({"key": key}))
        (runs / f"{key}_training_provenance.json").write_text(json.dumps(proof))
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert all(pool.map(lambda key: experiment._restore_run_artifacts(tmp_path, key),
                            ["first", "second"] * 10))
    key = json.loads((tmp_path / "feature_spec.json").read_text())["key"]
    assert (tmp_path / "model.txt").read_text() == key
    proof = json.loads((tmp_path / "training_provenance.json").read_text())
    assert cache_identity.model_revision(tmp_path) == proof["model_revision"]


def test_specialist_reserves_dev_rows(db, monkeypatch):
    monkeypatch.delenv("EXP_OOF_FOLD_EXCLUDE", raising=False)
    rows = suite._fetch_rows(db, file_types=("go",), max_id=0, min_score=None)
    assert [(r[0], r[2]) for r in rows] == [(1, False), (3, True)]


def test_baseline_requires_matching_model_provenance_for_dev(db, tmp_path, monkeypatch):
    monkeypatch.setattr(cache_identity, "model_revision", lambda root: "model-a")
    baseline._require_held_out(db, tmp_path, [3])  # Legacy model, locked test.
    with pytest.raises(ValueError, match="training may include"):
        baseline._require_held_out(db, tmp_path, [2])
    proof = tmp_path / "training_provenance.json"
    proof.write_text(json.dumps({"training_partitions": ["train"], "model_revision": "model-a"}))
    baseline._require_held_out(db, tmp_path, [2, 3])
    with pytest.raises(ValueError, match="training may include"):
        baseline._require_held_out(db, tmp_path, [1])
    monkeypatch.setattr(cache_identity, "model_revision", lambda root: "model-b")
    with pytest.raises(ValueError, match="training may include"):
        baseline._require_held_out(db, tmp_path, [2])


def test_lightgbm_knobs_reach_fitted_booster():
    rng = np.random.default_rng(7)
    X = rng.normal(size=(300, 2))
    y = (X[:, 0] - X[:, 1] > 0).astype(int)
    clf = model.create_classifier(
        150, 150, learner="azoth", device="cpu", num_threads=1,
        n_estimators=8, subsample=.7, gamma=.3, monotone_constraints=(1, -1),
    )
    clf.fit(X, y)
    params = clf.booster_.params
    assert params["subsample_freq"] == 1
    assert params["subsample"] == .7
    assert params["min_split_gain"] == .3
    assert tuple(params["monotone_constraints"]) == (1, -1)
    grid = np.column_stack([np.linspace(-2, 2, 100), np.zeros(100)])
    assert np.all(np.diff(model.predict_proba(clf, grid)) >= -1e-10)
    with pytest.raises(ValueError, match="GOSS"):
        model.create_classifier(10, 10, learner="azoth", device="cpu", boosting_type="goss", subsample=.8)


def test_saved_threshold_and_holdout_metrics_use_raw_scores():
    rng = np.random.default_rng(4)
    X = rng.normal(size=(600, 4)).astype(np.float32)
    y = (X[:, 0] + rng.normal(size=600) > 0).astype(np.float32)
    cfg = train.TrainConfig(
        learner="azoth", device="cpu", num_threads=1, n_estimators=12,
        n_folds=0, holdout_fraction=.3, early_stopping_rounds=3,
    )
    result = train.train(X, y, cfg)
    _, hold = train_test_split(np.arange(len(y)), test_size=.3, stratify=y, random_state=cfg.seed)
    cal, ev = train_test_split(hold, test_size=.5, stratify=y[hold], random_state=cfg.seed)
    raw = model.predict_proba(result.model, X)
    assert result.isotonic_calibrator is None
    assert result.optimal_threshold == train._select_threshold(
        y[cal], raw[cal], mode=cfg.threshold_mode, beta=cfg.beta, max_fpr=None,
    )
    expected = train._compute_metrics(y[ev], raw[ev], result.optimal_threshold)
    assert result.metrics == expected


@pytest.mark.parametrize("seeds", [1, 2])
def test_experiment_artifacts_cache_and_database_mutation(tmp_path, monkeypatch, seeds):
    """Exercise sampling, features, training, export and cache reuse together."""
    from collimator.demo import create_demo_db
    monkeypatch.setenv("COLLIMATOR_NUM_THREADS", "1")
    monkeypatch.setenv("COLLIMATOR_DISABLE_FEATURE_GROUPS", "clusters")
    db_path = tmp_path / "demo.db"
    create_demo_db(db_path, n_benign=200, n_malware=200, seed=7)
    output = tmp_path / "output"
    options = dict(
        output_dir=output, cache_dir=tmp_path / "cache", n_workers=1,
        learner="azoth", model_name="azoth", device="cpu", n_estimators=5,
        n_folds=0, holdout_fraction=.2, train_samples=200, max_test_samples=40,
        seed_search_k=seeds, save_all_seeds=seeds > 1,
    )
    first = experiment.run_experiment(db_path, **options)
    revision = cache_identity.model_revision(output)
    proof = json.loads((output / "training_provenance.json").read_text())
    assert proof["training_partitions"] == ["train"]
    assert proof["model_revision"] == revision
    cache_identity.require_reserved_dev(output)
    assert first["evaluation_revision"]
    assert first["score_space"] == "raw"
    row_file = tmp_path / "evaluation-ids.txt"
    row_file.write_text("\n".join(map(str, first["test_sample_row_ids"])))
    baseline_output = tmp_path / "baseline.json"
    baseline_args = SimpleNamespace(
        row_ids_file=row_file, db=db_path, cache_root=tmp_path / "baseline-cache",
        route="general", workers=1, output=baseline_output,
    )
    # Compare the deployed artifact on precisely the screened dev rows, then reuse
    # its score cache. Both paths must preserve the cohort and held-out proof.
    for _ in range(2):
        assert baseline._score_subset(baseline_args, output) == 0
        metrics = json.loads(baseline_output.read_text())
        assert metrics["evaluation_revision"] == first["evaluation_revision"]
        assert metrics["held_out"] is True
        assert metrics["n_rows"] == len(first["test_sample_row_ids"])
    # Cache reuse must restore the keyed artifact without fitting another model.
    with monkeypatch.context() as patch:
        def unexpected_fit(*args, **kwargs):
            raise AssertionError("cached experiment tried to retrain")
        patch.setattr(train, "train", unexpected_fit)
        for model_file in (output / "models").glob("*"):
            model_file.unlink()
        (output / "model.onnx").write_bytes(b"another run")
        second = experiment.run_experiment(db_path, **options)
    assert second["experiment_key"] == first["experiment_key"]
    assert cache_identity.model_revision(output) == revision
    # In-place changes below max(id) must not reuse the completed experiment.
    row = first["test_sample_row_ids"][0]
    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE samples SET score=score+1 WHERE id=?", (row,))
    third = experiment.run_experiment(db_path, **options)
    assert third["experiment_key"] != first["experiment_key"]
    assert third["evaluation_revision"] != first["evaluation_revision"]
    assert third["test_sample_row_ids"] == first["test_sample_row_ids"]


@pytest.mark.parametrize("partition", ["train", "evaluation"])
def test_live_label_changes_keep_captured_evaluation(tmp_path, monkeypatch, partition):
    """Relabeling before extraction and updates during fitting cannot abort a run."""
    from collimator.demo import create_demo_db

    monkeypatch.setenv("COLLIMATOR_NUM_THREADS", "1")
    monkeypatch.setenv("COLLIMATOR_DISABLE_FEATURE_GROUPS", "clusters")
    db_path = tmp_path / "demo.db"
    create_demo_db(db_path, n_benign=200, n_malware=200, seed=7)
    selected = []
    selected_test = []
    sample = experiment.sample_partitioned_reports
    revision = cache_identity.evaluation_revision
    extract = features.extract_partitioned_from_db
    extracted = []
    captured = []

    def select_then_relabel(*args, **kwargs):
        corpus = sample(*args, **kwargs)
        selected.extend(sorted((s.row_id, s.label) for s in corpus.train_samples))
        selected_test.extend(sorted((s.row_id, s.label) for s in corpus.test_samples))
        row_id, label = (selected if partition == "train" else selected_test)[0]
        with sqlite3.connect(db_path) as conn:
            conn.execute("UPDATE samples SET label=? WHERE id=?",
                         ("good" if label else "bad", row_id))
        return corpus

    def unexpected_live_scan(*args, **kwargs):
        pytest.fail("experiment reread live evaluation rows")

    def extract_selected(db, train_ids, test_ids, spec, **kwargs):
        assert train_ids == selected
        assert test_ids == selected_test
        matrices = extract(db, train_ids, test_ids, spec, **kwargs)
        np.testing.assert_array_equal(matrices[1], [label for _, label in selected])
        np.testing.assert_array_equal(matrices[3], [label for _, label in selected_test])
        captured.append(kwargs["identity"]["evaluation_revision"])
        # A subsequent update must not relabel or invalidate the extracted matrix.
        with sqlite3.connect(db_path) as conn:
            conn.execute("UPDATE samples SET score=score+1 WHERE id=?", (selected_test[0][0],))
        extracted.append(True)
        return matrices

    monkeypatch.setattr(experiment, "sample_partitioned_reports", select_then_relabel)
    monkeypatch.setattr(cache_identity, "evaluation_revision", unexpected_live_scan)
    monkeypatch.setattr(features, "extract_partitioned_from_db", extract_selected)
    result = experiment.run_experiment(
        db_path, output_dir=tmp_path / "output", cache_dir=tmp_path / "cache",
        n_workers=1, learner="azoth", model_name="azoth", device="cpu",
        n_estimators=5, n_folds=0, holdout_fraction=.2,
        train_samples=200, max_test_samples=40,
    )
    assert extracted == [True]
    assert result["evaluation_revision"] == captured[0]
    assert result["evaluation_revision"] != revision(db_path, result["test_sample_row_ids"])
    assert list((tmp_path / "cache").glob("vocabulary_*/feature_spec.json"))
