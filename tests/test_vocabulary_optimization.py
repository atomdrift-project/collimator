"""Exact vocabulary counts survive SQL remapping and worker aggregation."""

import json
import random
import sqlite3
from dataclasses import asdict
from itertools import combinations
from pathlib import Path
from threading import Event

import pytest

from collimator import features
from collimator.vocabulary import CountView, VocabularyCounts


def test_ordered_merge_matches_document_sets_and_keeps_all_families(tmp_path):
    rng = random.Random(97)
    tokens = [f"path/{i:03d}/é" for i in range(25)]
    expected = {}
    views = []
    for batch in range(5):
        with VocabularyCounts(str(tmp_path / f"batch {batch}?.sqlite"), buffer_size=7) as counts:
            rng.shuffle(tokens)
            for document in range(batch * 8, (batch + 1) * 8):
                paths = sorted(rng.sample(tokens, 7))
                for family, order in [("bigram", 2), ("trigram", 3), ("tiered_trigram", 3)]:
                    for parts in combinations(paths, order):
                        name = " + ".join(parts)
                        expected.setdefault(family, {}).setdefault(name, set()).add(document)
                    # Repeat files and evict keys: each sample still counts once.
                    for _ in range(2):
                        counts.increment_combinations(family, paths, order, document)
            views.append(counts.view("bigram"))
    with VocabularyCounts(str(tmp_path / "merged.sqlite")) as merged:
        for view in reversed(views):
            merged.merge(view)
            assert not Path(view.path).exists()
        for family, documents in expected.items():
            reference = {name: len(ids) for name, ids in documents.items()}
            assert dict(merged.view(family).items()) == reference
            assert merged.top(family, 10, 2) == sorted(
                sorted((name for name, n in reference.items() if n >= 2),
                       key=lambda name: (-reference[name], name))[:10]
            )


def test_failed_merge_retains_source_and_detaches_it(tmp_path):
    invalid = tmp_path / "invalid.sqlite"
    with sqlite3.connect(invalid) as db:
        db.execute("CREATE TABLE tokens (id INTEGER, token TEXT)")
    valid = tmp_path / "valid.sqlite"
    with VocabularyCounts(str(valid)) as counts:
        counts.increment_combinations("bigram", ["a", "b"], 2, 1)
        view = counts.view("bigram")
    with VocabularyCounts() as merged:
        with pytest.raises(sqlite3.OperationalError, match="no such table"):
            merged.merge(CountView(str(invalid), "bigram"))
        assert invalid.exists()
        missing = tmp_path / "missing.sqlite"
        with pytest.raises(sqlite3.OperationalError):
            merged.merge(CountView(str(missing), "bigram"))
        assert not missing.exists()
        merged.merge(view)
        assert merged.view("bigram") == {"a + b": 1}


@pytest.mark.parametrize("buffer_size", [1, 7, 100_000])
def test_grouped_single_file_and_overlapping_archives_count_distinct_samples(
    tmp_path, monkeypatch, buffer_size,
):
    for family in ("BIGRAMS", "TRIGRAMS"):
        monkeypatch.setenv(f"COLLIMATOR_TIERED_CRIT_{family}", "1")
    features.feature_config_from_env.cache_clear()
    try:
        def file(start, stop):
            return {"type": "elf", "ts": [
                {"i": f"trait/{i:02d}/capability", "l": 4, "c": 1.0}
                for i in range(start, stop)
            ]}

        patterns = [[file(0, 7)], [file(0, 7)] * 3,
                    [file(0, 7), file(3, 10)], [file(2, 9)],
                    [file(0, 1), file(3, 10)], [file(1, 6), file(2, 8)]]
        rng = random.Random(29)
        reports = {rid: {"cleave_result": {"v": "4", "fs": rng.choice(patterns)}}
                   for rid in range(1, 60)}
        labels = [(rid, int(rid % 4 != 0)) for rid in reports]
        monkeypatch.setattr(features, "MIN_PATH_FREQ", 1)
        from collimator import data
        monkeypatch.setattr(data, "fetch_cleave_results",
                            lambda _dsn, ids: {rid: reports[rid] for rid in ids})
        expected = {family: {} for family in
                    ("bigram", "trigram", "tiered_bigram", "tiered_trigram")}
        config = features.feature_config_from_env()
        for rid, label in labels:
            if not label:
                continue
            report = reports[rid]["cleave_result"]
            for family, order, limit in [("bigram", 2, 512), ("trigram", 3, 128)]:
                seen = {" + ".join(parts) for f in report["fs"]
                        for parts in combinations(features._ranked_ngram_paths(f, limit), order)}
                for token in seen:
                    expected[family][token] = expected[family].get(token, 0) + 1
            summary = features._summarize_report_files(report["fs"])
            for family, order, floor in [
                ("tiered_bigram", 2, config.tiered_bigram_min_crit),
                ("tiered_trigram", 3, config.tiered_trigram_min_crit),
            ]:
                tokens = features._ranked_tiered_tokens(
                    summary.sample_paths, summary.path_scores, order=order, min_crit=floor,
                )
                for parts in combinations(tokens, order):
                    token = " + ".join(parts)
                    expected[family][token] = expected[family].get(token, 0) + 1
        with VocabularyCounts(str(tmp_path / "grouped.sqlite"), buffer_size=buffer_size) as counts:
            for start in range(0, len(labels), 7):
                features._count_labeled_vocab_batch("unused", labels[start:start + 7], counts)
            for family, reference in expected.items():
                assert dict(counts.view(family).items()) == reference
    finally:
        features.feature_config_from_env.cache_clear()


def test_active_shards_keep_cache_between_batches(tmp_path, monkeypatch):
    from collimator import data
    report = {"v": "4", "fs": [{"type": "elf", "ts": [
        {"i": p, "l": 4, "c": 1.0} for p in ("a", "b", "c")
    ]}]}
    monkeypatch.setattr(data, "fetch_cleave_results",
                        lambda _dsn, ids: {rid: {"cleave_result": report} for rid in ids})
    with VocabularyCounts(str(tmp_path / "shard.sqlite")) as counts:
        for rid in (1, 2):
            result = features._count_labeled_vocab_batch("unused", [(rid, 1)], counts)
            assert counts.pending
            assert isinstance(result[3], CountView)
    assert dict(result[3].items()) == {"a + b": 2, "a + c": 2, "b + c": 2}


def test_shared_finding_pass_preserves_nan_confidence_filter(monkeypatch):
    from collimator import data
    report = {"v": "4", "fs": [{"type": "elf", "ts": [
        {"i": p, "l": 4, "c": float("nan") if p == "c" else 1.0}
        for p in ("a", "b", "c", "d")
    ]}]}
    monkeypatch.setattr(data, "fetch_cleave_results",
                        lambda _dsn, ids: {rid: {"cleave_result": report} for rid in ids})
    result = features._vocab_labeled_db_batch_worker(("unused", [(1, 1)]))
    assert result[3] == {"a + b": 1, "a + d": 1, "b + d": 1}
    assert result[9] == {"a + b + d": 1}


def test_background_merges_overlap_work_and_finish_before_queries(tmp_path, monkeypatch):
    views = []
    for i in range(3):
        with VocabularyCounts(str(tmp_path / f"worker-{i}.sqlite")) as worker:
            worker.increment("bigram", ("a", "b"), document=i)
            views.append(worker.view("bigram"))
    started, release = Event(), Event()
    with VocabularyCounts(str(tmp_path / "merged.sqlite"), check_same_thread=False) as counts:
        original_merge = counts.merge

        def merge(view):
            started.set()
            assert release.wait(timeout=5)
            original_merge(view)

        monkeypatch.setattr(counts, "merge", merge)
        with features._background_vocab_merges(counts) as submit:
            try:
                submit(views[0])
                assert started.wait(timeout=5)
                # Admission continues while the first merge remains blocked.
                submit(views[1])
                submit(views[2])
                assert all(Path(view.path).exists() for view in views)
            finally:
                release.set()
        assert counts.top("bigram", 1, 1) == ["a + b"]
        assert dict(counts.view("bigram").items()) == {"a + b": 3}
    assert all(not Path(view.path).exists() for view in views)


def test_background_merge_failure_reaches_caller(tmp_path):
    source = tmp_path / "invalid.sqlite"
    with sqlite3.connect(source) as db:
        db.execute("CREATE TABLE tokens (id INTEGER, token TEXT)")
    with VocabularyCounts(check_same_thread=False) as counts:
        with pytest.raises(sqlite3.OperationalError, match="no such table"):
            with features._background_vocab_merges(counts) as submit:
                submit(CountView(str(source), "bigram"))
        assert source.exists()


def test_benign_candidate_index_is_reused_between_batches(monkeypatch):
    from collimator import data
    monkeypatch.setattr(features, "_worker_trigram_candidates", None)
    original_index = features._trigram_candidate_index
    builds = []

    def index(candidates):
        builds.append(None)
        return original_index(candidates)

    monkeypatch.setattr(features, "_trigram_candidate_index", index)
    monkeypatch.setattr(data, "fetch_cleave_results", lambda _dsn, ids: {
        rid: {"cleave_result": {"v": "4", "fs": [{"ts": [
            {"i": p, "l": 4, "c": 1.0} for p in ("a", "b", "c")
        ]}]}} for rid in ids
    })
    features._init_trigram_candidates(["a + b + c"])
    for ids in ([1, 2], [3, 4]):
        assert features._vocab_benign_trigram_worker(("unused", ids, None, None)) == {
            "a + b + c": 2,
        }
    assert len(builds) == 1


@pytest.mark.parametrize("reverse_results", [False, True])
@pytest.mark.parametrize("recover_memory", [False, True])
def test_parallel_vocab_matches_serial_across_shard_rotation(
    tmp_path, monkeypatch, reverse_results, recover_memory,
):
    for name in ("BIGRAM_MIN_FREQ", "TRIGRAM_MIN_FREQ", "TIERED_BIGRAM_MIN_FREQ",
                 "TIERED_TRIGRAM_MIN_FREQ"):
        monkeypatch.setenv(f"COLLIMATOR_{name}", "1")
    for name in ("TIERED_CRIT_BIGRAMS", "TIERED_CRIT_TRIGRAMS", "EXTENDED_METRICS"):
        monkeypatch.setenv(f"COLLIMATOR_{name}", "1")
    monkeypatch.setenv("COLLIMATOR_VOCAB_TMPDIR", str(tmp_path / "scratch"))
    monkeypatch.setattr(features, "_feature_batch_size", lambda _nw: 7)
    monkeypatch.setenv("COLLIMATOR_MEM_AWARE_WORKERS", "1")
    monkeypatch.setenv("COLLIMATOR_MEM_PER_WORKER_GB", "2")
    monkeypatch.setenv("COLLIMATOR_MEM_SHARES", "1")
    budget_reads = []

    def headroom(_reserve):
        budget_reads.append(None)
        return 0.0 if recover_memory and len(budget_reads) == 1 else 4.0

    monkeypatch.setattr(features, "ram_headroom_gb", headroom)
    monkeypatch.setattr(features, "_WORKER_BUDGET_REFRESH_SECONDS", 0.01)
    features.feature_config_from_env.cache_clear()
    try:
        db_path = tmp_path / "reports.sqlite"
        labels = []
        with sqlite3.connect(db_path) as db:
            db.execute("CREATE TABLE samples (id INTEGER PRIMARY KEY, cleave_result TEXT,"
                       " formula TEXT, elements TEXT, score INTEGER, mtime TEXT)")
            for rid in range(1, 234):
                label = int(rid % 3 != 0)
                labels.append((rid, label))
                file = {"type": "elf", "ms": {"text": {"custom_count": rid}}, "ts": [
                    {"i": f"trait/{p}::finding", "l": 3 + p % 3, "c": 1.0}
                    for p in range(rid % 5, rid % 5 + 5)
                ]}
                report = json.dumps({"v": "4", "fs": [file, file]})
                db.execute("INSERT INTO samples VALUES (?, ?, ?, ?, ?, ?)",
                           (rid, report if rid % 17 else None, "C2H6", "C,H", label * 5, ""))
        serial = features.build_vocab_from_db(db_path, labels, n_workers=1)
        merges = []
        original_merge = VocabularyCounts.merge

        def merge(counts, view):
            if view.family == "bigram":
                merges.append(view.path)
            original_merge(counts, view)

        monkeypatch.setattr(VocabularyCounts, "merge", merge)
        if reverse_results:
            original_iter = features._bounded_unordered_iter

            def reversed_iter(*args, **kwargs):
                # A sealed shard is deliberately delivered before earlier
                # batches from the same file. It must be merged exactly once.
                return reversed(list(original_iter(*args, **kwargs)))

            monkeypatch.setattr(features, "_bounded_unordered_iter", reversed_iter)
        parallel = features.build_vocab_from_db(db_path, labels, n_workers=2)
        if recover_memory:
            assert len(budget_reads) > 1
        assert asdict(parallel) == asdict(serial)
        # 34 input batches become at most four full shards plus two tails.
        assert 1 < len(merges) <= 6
        assert len(merges) == len(set(merges))
        assert not list((tmp_path / "scratch").iterdir())
    finally:
        features.feature_config_from_env.cache_clear()
