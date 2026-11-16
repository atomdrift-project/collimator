"""Evaluation identities describe the versions actually fetched, not later DB state."""

from contextlib import contextmanager
import hashlib
import sqlite3

import numpy as np
import pytest

from collimator import cache_identity, data, experiment, features
from collimator.demo import compress_report, create_demo_db, set_report


@pytest.fixture
def corpus(tmp_path, monkeypatch):
    monkeypatch.setenv("COLLIMATOR_DISABLE_FEATURE_GROUPS", "clusters")
    features.feature_config_from_env.cache_clear()
    path = tmp_path / "demo.db"
    create_demo_db(path, n_benign=40, n_malware=40, seed=7)
    with sqlite3.connect(path) as conn:
        labels = [(rid, int(label == "bad")) for rid, label in
                  conn.execute("SELECT id,label FROM samples ORDER BY id")]
    spec = features.build_vocab_from_db(path, labels[:40], n_workers=1)
    yield path, labels[:40], labels[40:], spec
    features.feature_config_from_env.cache_clear()


@pytest.mark.parametrize("workers", [1, 2])
def test_captured_revision_matches_live_and_survives_cache_reuse(corpus, tmp_path, monkeypatch, workers):
    path, training, evaluation, spec = corpus
    monkeypatch.setattr(features, "_feature_batch_size", lambda _: 17)
    identity = {}
    matrices = features.extract_partitioned_from_db(
        path, training, evaluation, spec, n_workers=workers, identity=identity,
    )
    expected = cache_identity.evaluation_revision(path, [rid for rid, _ in evaluation])
    assert identity["evaluation_revision"] == expected
    assert identity["train_row_ids"].tolist() == [rid for rid, _ in training]
    assert identity["test_row_ids"].tolist() == [rid for rid, _ in evaluation]
    np.testing.assert_array_equal(matrices[3], [label for _, label in evaluation])

    cache = tmp_path / "cache"
    experiment._save_matrix_cache(
        cache, "captured", spec, *matrices, np.array(["go"] * len(training)),
        test_row_ids=identity["test_row_ids"], evaluation_revision=expected,
    )
    with sqlite3.connect(path) as conn:
        set_report(conn, evaluation[0][0], {"risk": 11})
    assert cache_identity.evaluation_revision(path, [rid for rid, _ in evaluation]) != expected
    cached = experiment._load_matrix_cache(cache, "captured")
    assert cached[-1] == expected
    np.testing.assert_array_equal(cached[-2], identity["test_row_ids"])
    np.testing.assert_array_equal(cached[4], matrices[3])

    # Old caches cannot acquire a new identity by rereading today's database.
    archive = cache / "matrix_captured.npz"
    with np.load(archive, allow_pickle=True) as arrays:
        legacy = {key: arrays[key] for key in arrays.files if key != "evaluation_revision"}
    np.savez(archive, **legacy)
    assert experiment._load_matrix_cache(cache, "captured") is None


def test_deleted_and_invalid_rows_keep_ids_labels_and_features_aligned(corpus, monkeypatch):
    path, training, evaluation, spec = corpus
    monkeypatch.setattr(features, "_feature_batch_size", lambda _: 80)
    with sqlite3.connect(path) as conn:
        conn.execute("DELETE FROM samples WHERE id IN (?,?)", (training[0][0], evaluation[0][0]))
        set_report(conn, evaluation[1][0], [])
    identity = {}
    X_train, y_train, X_test, y_test = features.extract_partitioned_from_db(
        path, training, evaluation, spec, n_workers=1, identity=identity,
    )
    assert identity["train_row_ids"].tolist() == [rid for rid, _ in training[1:]]
    assert identity["test_row_ids"].tolist() == [rid for rid, _ in evaluation[2:]]
    np.testing.assert_array_equal(y_train, [label for _, label in training[1:]])
    np.testing.assert_array_equal(y_test, [label for _, label in evaluation[2:]])
    assert X_train.shape[0] == len(y_train)
    assert X_test.shape[0] == len(y_test)
    assert identity["evaluation_revision"] == cache_identity.evaluation_revision(
        path, identity["test_row_ids"].tolist(), y_test,
    )


def test_postgres_captures_report_and_version_in_one_snapshot(monkeypatch):
    queries = []
    detail = compress_report({"risk": 5})
    digest = hashlib.sha256(detail).digest()

    class Cursor:
        def __init__(self):
            self.rows = []

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def execute(self, query, params):
            queries.append(query)
            assert params == [[1]]
            if "v.detail IS NOT NULL" in query:  # the reports themselves
                self.rows = [(1, b"\x01" * 32, "pe", 10, detail, "123", digest)]

        def __iter__(self):
            return iter(self.rows)

    class Connection:
        def cursor(self):
            return Cursor()

    snapshots = []

    @contextmanager
    def connect(*args, repeatable_read=False, **kwargs):
        snapshots.append(repeatable_read)
        yield Connection()

    monkeypatch.setattr(data, "_connect", connect)
    result = data.fetch_cleave_results("postgres://test", [1], evaluation_labels={1: 0})
    assert snapshots == [True]  # reports, members and versions read in one snapshot
    assert "xmin::text" in queries[0] and "v.digest" in queries[0]
    assert result[1]["evaluation_digest"] == cache_identity.evaluation_row_digest(
        [1, "123", digest.hex(), "good", {k: v for k, v in result[1].items() if k != "evaluation_digest"}])
    assert result[1]["score"] == 5
