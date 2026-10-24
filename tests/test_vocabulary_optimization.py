"""Exact vocabulary counts survive SQL remapping and worker aggregation."""

import json
import random
import sqlite3
import struct
from dataclasses import asdict
from itertools import combinations
from pathlib import Path
from threading import Event

import pytest

from collimator import features
from collimator.vocabulary import CountView, VocabularyCounts, _packed_remapper


def test_auxiliary_vocab_sample_is_order_independent_and_stable_under_growth():
    rows = [(i, i % 2) for i in range(10000)]
    expected = features._stable_vocab_scan_rows(rows, 500, chunk_size=37)
    assert expected == features._stable_vocab_scan_rows(rows[::-1], 500, chunk_size=10001)
    added = [(i, 0) for i in range(10000, 10018)]
    expanded = features._stable_vocab_scan_rows(added + rows, 500, chunk_size=53)
    old_ids = {r[0] for r in expected}
    new_ids = {r[0] for r in expanded}
    # Insertions can displace only one old sample per newly selected ID.
    assert len(old_ids - new_ids) == len(new_ids - old_ids) <= len(added)
    assert len(expanded) == len(new_ids) == 500
    removed = next(r for r in rows if r[0] not in old_ids)
    assert features._stable_vocab_scan_rows([r for r in rows if r != removed], 500) == expected


def test_auxiliary_vocab_sample_retains_labels_and_handles_small_corpora():
    assert features._stable_vocab_scan_rows([]) == []
    rows = [(9, 1), (2, 0), (5, 1)]
    assert set(features._stable_vocab_scan_rows(rows)) == set(rows)
    a = features._stable_vocab_scan_rows(rows, 2)
    b = features._stable_vocab_scan_rows([(rid, 1-label) for rid, label in rows], 2)
    assert [rid for rid, _ in a] == [rid for rid, _ in b]
    assert [label for _, label in b] == [1-label for _, label in a]


def test_packed_remapping_preserves_arbitrary_ids_and_key_orders():
    mapping = {0: 0xFFFFFFFF, 1: 256, 257: 3, 65536: 19, 0xFFFFFFFF: 0}
    remap = _packed_remapper(mapping)
    keys = [parts for order in (1, 2, 3, 4) for parts in combinations(mapping, order)]
    # Include adjacent prefixes as well as transitions between key lengths.
    keys += list(reversed(keys))
    for parts in keys:
        packed = struct.pack(f">{len(parts)}I", *parts)
        expected = struct.pack(f">{len(parts)}I", *(mapping[i] for i in parts))
        assert remap(packed) == expected


def test_ordered_merge_matches_document_sets_and_keeps_all_families(tmp_path):
    rng = random.Random(97)
    tokens = [f"path/{i:03d}/é" for i in range(25)]
    expected = {}
    views = []
    for batch in range(5):
        with VocabularyCounts(str(tmp_path / f"batch {batch}?.sqlite"), buffer_size=7,
                              stable_token_ids=False) as counts:
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
@pytest.mark.parametrize("signature_bytes", [0, 1024, 8 * 1024 * 1024])
def test_grouped_single_file_and_overlapping_archives_count_distinct_samples(
    tmp_path, monkeypatch, buffer_size, signature_bytes,
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
        with VocabularyCounts(str(tmp_path / "grouped.sqlite"), buffer_size=buffer_size,
                              signature_bytes=signature_bytes) as counts:
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
            assert counts.signatures
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
@pytest.mark.parametrize("shard_batches", [8, 16, 32])
def test_parallel_vocab_matches_serial_across_shard_rotation(
    tmp_path, monkeypatch, reverse_results, recover_memory, shard_batches,
):
    monkeypatch.setenv("COLLIMATOR_VOCAB_SHARD_BATCHES", str(shard_batches))
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


def test_shard_rotation_caps_time_and_disk_between_batches(tmp_path, monkeypatch):
    monkeypatch.setenv("COLLIMATOR_VOCAB_SHARD_BATCHES", "16")
    monkeypatch.setattr(features.time, "monotonic", lambda: 120)
    with VocabularyCounts(str(tmp_path / "worker.sqlite")) as counts:
        assert not features._vocab_shard_limit_reached(counts, 15, 61)
        assert features._vocab_shard_limit_reached(counts, 16, 61)
        assert features._vocab_shard_limit_reached(counts, 1, 60)
        monkeypatch.setattr(features.os.path, "getsize", lambda _: 512 * 1024 * 1024)
        assert features._vocab_shard_limit_reached(counts, 1, 119)


def test_repeated_signatures_expand_once_across_batches(tmp_path, monkeypatch):
    from collimator import vocabulary
    expanded = []
    original = vocabulary.combinations

    def combinations_once(tokens, order):
        expanded.append((tuple(tokens), order))
        return original(tokens, order)

    monkeypatch.setattr(vocabulary, "combinations", combinations_once)
    with VocabularyCounts(str(tmp_path / "worker.sqlite")) as counts:
        for _ in range(100):
            counts.group_combinations("trigram", ["a", "b", "c", "d"], 3)
        assert not expanded
        result = dict(counts.view("trigram").items())
        assert len(expanded) == 1
        assert result == {" + ".join(parts): 100 for parts in original("abcd", 3)}


def test_native_reduction_counts_overlaps_across_chunk_boundaries(tmp_path, monkeypatch):
    from collimator import vocabulary
    monkeypatch.setattr(vocabulary, "_SIGNATURE_REDUCE_KEYS", 7)
    paths = [f"path/{i:02d}" for i in range(16)]
    expected = {}
    with VocabularyCounts(str(tmp_path / "worker.sqlite"), buffer_size=1) as counts:
        for family, order in (("bigram", 2), ("trigram", 3), ("quadgram", 4)):
            reference = expected.setdefault(family, {})
            for start, n in ((0, 3), (3, 7), (5, 2)):
                counts.group_combinations(family, paths[start:start + 9], order, n=n)
                for parts in combinations(paths[start:start + 9], order):
                    token = " + ".join(parts)
                    reference[token] = reference.get(token, 0) + n
        for family, reference in expected.items():
            assert dict(counts.view(family).items()) == reference


@pytest.mark.parametrize("legacy", [False, True])
def test_stable_token_collisions_remap_exactly_and_resume_legacy_ids(tmp_path, monkeypatch, legacy):
    from collimator import vocabulary
    # Force all paths to collide, including unsigned wraparound. Different
    # insertion orders produce different local resolutions of the collision.
    monkeypatch.setattr(vocabulary, "_token_hash", lambda _: 0xFFFFFFFF)
    master = tmp_path / "master.sqlite"
    with VocabularyCounts(str(master), durable=True, stable_token_ids=not legacy) as counts:
        counts.increment("bigram", ("a", "b"), n=2)
    for number, paths in enumerate((("z", "b", "a"), ("b", "a", "z"))):
        with VocabularyCounts(str(tmp_path / f"worker-{number}.sqlite")) as worker:
            for path in paths:
                worker._token_id(path)
            worker.group_combinations("bigram", ["a", "b", "z"], 2, n=3)
            view = worker.view("bigram")
        with VocabularyCounts(str(master), durable=True, resume=True) as counts:
            counts.merge(view)
    with VocabularyCounts(str(master), durable=True, resume=True) as counts:
        assert dict(counts.view("bigram").items()) == {"a + b": 8, "a + z": 6, "b + z": 6}
        assert len(set(counts.token_ids.values())) == 3


def test_stable_tokens_avoid_remapping_for_different_insertion_orders(tmp_path, monkeypatch):
    from collimator import vocabulary
    monkeypatch.setattr(vocabulary, "_packed_remapper", lambda _: pytest.fail("unnecessary remapping"))
    with VocabularyCounts(str(tmp_path / "master.sqlite")) as counts:
        counts.increment("bigram", ("a", "b"))
        with VocabularyCounts(str(tmp_path / "worker.sqlite")) as worker:
            worker._token_id("b")
            worker._token_id("a")
            worker.increment("bigram", ("a", "b"))
            view = worker.view("bigram")
        counts.merge(view)
        assert dict(counts.view("bigram").items()) == {"a + b": 2}
