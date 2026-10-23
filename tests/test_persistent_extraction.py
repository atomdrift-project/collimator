"""Persistent scoring workers preserve model layouts, row alignment and cleanup."""
import json
import os
from pathlib import Path
import runpy
import sqlite3

import pytest

from collimator import features


@pytest.fixture
def reports(tmp_path):
    path = tmp_path / "reports.sqlite"
    rows = []
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE samples (id INTEGER PRIMARY KEY, cleave_result TEXT, "
                   "formula TEXT, elements TEXT, score INTEGER, mtime TEXT)")
        for rid in range(1, 17):
            report = {"v": "4", "fs": [{"type": "elf", "ts": [
                {"i": "a" if rid % 2 else "b", "l": 4, "c": 1.0},
            ]}]}
            db.execute("INSERT INTO samples VALUES (?,?, '', '', 4, '')", (rid, json.dumps(report)))
            rows.append((rid, f"{rid:064x}", "", 4, rid % 2, f"{rid:064x}"))
    return path, rows


def collect(path, rows, spec, workers, pool=None):
    output = {}
    stats = []
    for meta, matrix, labels, batch_stats in features.extract_labeled_metadata_from_db_batches_unordered(
        path, rows, spec, n_workers=workers, batch_size=3, worker_pool=pool,
    ):
        assert len(meta) == matrix.shape[0] == len(labels)
        for row, vector, label in zip(meta, matrix.toarray(), labels):
            output[row[0]] = (tuple(vector), label)
        stats.append(batch_stats)
    return output, stats


@pytest.mark.parametrize("workers", [1, 2])
def test_reused_workers_switch_equal_width_specs_without_stale_features(reports, workers, monkeypatch):
    path, rows = reports
    monkeypatch.setenv("OPENBLAS_NUM_THREADS", "3")
    a = features.FeatureSpec(presence_vocab=["a"], feature_names=["present:a"], total_features=1)
    b = features.FeatureSpec(presence_vocab=["b"], feature_names=["present:b"], total_features=1)
    expected = {name: collect(path, rows, spec, 1)[0] for name, spec in (("a", a), ("b", b))}
    assert expected["a"] != expected["b"]
    pids = set()
    with features.MetadataExtractionPool(workers) as pool:
        for name, spec in (("a", a), ("a", a), ("b", b), ("a", a)):
            result, stats = collect(path, rows, spec, workers, pool)
            assert result == expected[name]
            pids.update(stat["worker_pid"] for stat in stats)
        assert len(pids) <= workers
    assert pool.pool is None
    assert os.environ["OPENBLAS_NUM_THREADS"] == "3"
    with pytest.raises(RuntimeError, match="not open"):
        collect(path, rows, a, workers, pool)


def test_pool_reuses_context_and_cleans_up_after_fetch_failure(reports):
    path, rows = reports
    spec = features.FeatureSpec(feature_names=["present:a"], total_features=1)
    with pytest.raises(ValueError, match="missing cleave_result"):
        with features.MetadataExtractionPool(1) as pool:
            first, first_stats = collect(path, rows, spec, 1, pool)
            second, second_stats = collect(path, rows, spec, 1, pool)
            assert first == second
            assert sum(stat["context_rebuilt"] for stat in first_stats) == 1
            assert sum(stat["context_rebuilt"] for stat in second_stats) == 0
            collect(path, [(999, "x", "", 0, 0, "x")], spec, 1, pool)
    assert pool.pool is None


def test_route_selection_needs_only_covered_fields_and_preserves_filters(tmp_path, monkeypatch):
    from collimator import data
    scorer = runpy.run_path(str(Path(__file__).parents[1] / "scripts/azoth_oof_score_routes.py"))
    path = tmp_path / "metadata.sqlite"
    with sqlite3.connect(path) as db:
        # Deliberately no path column: it must not be fetched for route scores.
        db.execute("CREATE TABLE samples (id INTEGER, sha256 TEXT, canonical_sha256 TEXT, "
                   "label TEXT, score INTEGER, file_type TEXT, skip TEXT, cleave_result TEXT)")
        db.executemany("INSERT INTO samples VALUES (?,?,?,?,?,?,?,?)", [
            (1, "sha1", "canonical1", "bad", 4, "elf", "", "{}"),
            (2, "sha2", "", "good", 0, "pe", "", "{}"),
            (3, "sha3", "", "bad", 5, "elf", "", "{}"),
            (4, "sha4", "", "good", 0, "elf", "excluded", "{}"),
            (5, "sha5", "", "good", 0, "elf", "", "{}"),
        ])
    # Exercise the shared sampling predicate as well as the route and pin filters.
    monkeypatch.setattr(data, "LABELED_WHERE", "label IN ('bad','good') AND skip='' AND id != 3")
    fetch = scorer["_fetch_route_rows"]
    assert fetch(path, ["elf", "pe"], 4) == [
        (1, "sha1", "", 4, 1, "canonical1"), (2, "sha2", "", 0, 0, "sha2"),
    ]
    assert fetch(path, ["elf"], 4) == [(1, "sha1", "", 4, 1, "canonical1")]
    assert fetch(path, [], 4) == []
