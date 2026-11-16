"""Persistent scoring workers preserve model layouts, row alignment and cleanup."""
import os
from pathlib import Path
import runpy
import sqlite3

import pytest

from collimator import features
from collimator.demo import add_sample, create_schema, write_reports


@pytest.fixture
def reports(tmp_path):
    path = tmp_path / "reports.sqlite"
    rows = []
    stored = []
    for rid in range(1, 17):
        report = {"v": "4", "fs": [{"type": "elf", "ts": [
            {"i": "a" if rid % 2 else "b", "l": 4, "c": 1.0},
        ]}]}
        stored.append({"id": rid, "report": report, "score": 4})
        rows.append((rid, f"{rid:064x}", "", 4, rid % 2, f"{rid:064x}"))
    write_reports(path, stored)
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
    sha = {rid: f"{rid:064x}" for rid in range(1, 6)}
    with sqlite3.connect(path) as db:
        create_schema(db)
        for rid, label, risk, file_type, label_source in [
            (1, "bad", 4, "elf", None),
            (2, "good", 0, "pe", None),
            (3, "bad", 5, "elf", None),
            (4, "good", 0, "elf", "conflict"),
            (5, "good", 0, "elf", None),
        ]:
            add_sample(db, sample_id=rid, sha256=sha[rid], label=label, file_type=file_type,
                       report={"traits": [{"id": "x", "crit": 5}], "risk": risk},
                       label_source=label_source)
    # Exercise the shared sampling predicate as well as the route and pin filters.
    monkeypatch.setattr(data, "LABELED_WHERE", data.LABELED_WHERE + " AND s.id != 3")
    fetch = scorer["_fetch_route_rows"]
    # Route rows read no reports: score is filled in as each report is extracted.
    assert fetch(path, ["elf", "pe"], 4) == [
        (1, sha[1], "", 0, 1, sha[1]), (2, sha[2], "", 0, 0, sha[2]),
    ]
    assert fetch(path, ["elf"], 4) == [(1, sha[1], "", 0, 1, sha[1])]
    assert fetch(path, [], 4) == []
