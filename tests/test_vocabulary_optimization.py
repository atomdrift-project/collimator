"""Exact vocabulary counts survive SQL remapping and worker aggregation."""

import json
import random
import sqlite3
from dataclasses import asdict
from itertools import combinations
from pathlib import Path

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


@pytest.mark.parametrize("reverse_results", [False, True])
def test_parallel_vocab_matches_serial_across_shard_rotation(tmp_path, monkeypatch, reverse_results):
    for name in ("BIGRAM_MIN_FREQ", "TRIGRAM_MIN_FREQ", "TIERED_BIGRAM_MIN_FREQ",
                 "TIERED_TRIGRAM_MIN_FREQ"):
        monkeypatch.setenv(f"COLLIMATOR_{name}", "1")
    for name in ("TIERED_CRIT_BIGRAMS", "TIERED_CRIT_TRIGRAMS", "EXTENDED_METRICS"):
        monkeypatch.setenv(f"COLLIMATOR_{name}", "1")
    monkeypatch.setenv("COLLIMATOR_VOCAB_TMPDIR", str(tmp_path / "scratch"))
    monkeypatch.setattr(features, "_feature_batch_size", lambda _nw: 7)
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
        assert asdict(parallel) == asdict(serial)
        # 34 input batches become at most four full shards plus two tails.
        assert 1 < len(merges) <= 6
        assert len(merges) == len(set(merges))
        assert not list((tmp_path / "scratch").iterdir())
    finally:
        features.feature_config_from_env.cache_clear()
