"""Interrupted counting resumes exactly; candidate storage stays bounded."""

from dataclasses import asdict
from itertools import combinations
import json
import pickle
import sqlite3

import pytest

from collimator import features
from collimator.vocabulary import DiskTrigramCandidates, TrigramSource, VocabularyCounts


@pytest.fixture
def corpus(tmp_path, monkeypatch):
    for key in ("BIGRAM_MIN_FREQ", "TRIGRAM_MIN_FREQ", "TIERED_BIGRAM_MIN_FREQ",
                "TIERED_TRIGRAM_MIN_FREQ"):
        monkeypatch.setenv(f"COLLIMATOR_{key}", "1")
    monkeypatch.setenv("COLLIMATOR_TRIGRAM_MAX", "100")
    monkeypatch.setenv("COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC", "0.3")
    monkeypatch.setattr(features, "_feature_batch_size", lambda _: 3)
    features.feature_config_from_env.cache_clear()
    path = tmp_path / "samples.sqlite"
    labels = [(i, int(i % 3 != 0)) for i in range(1, 25)]
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE samples (id INTEGER PRIMARY KEY, cleave_result TEXT,"
                   " formula TEXT, elements TEXT, score INTEGER, mtime TEXT)")
        for row, label in labels:
            report = {"v": "4", "fs": [{"type": "elf", "ts": [
                {"i": f"trait/{i}::finding", "l": 4, "c": 1.0}
                for i in range(row % 4, row % 4 + 5)
            ]}]}
            db.execute("INSERT INTO samples VALUES (?, ?, '', '', ?, '')",
                       (row, json.dumps(report), label * 5))
    yield path, labels
    features.feature_config_from_env.cache_clear()


@pytest.mark.parametrize("phase", ["bigram", "benign_trigram"])
def test_restart_keeps_committed_counts_exact(corpus, tmp_path, monkeypatch, phase):
    path, labels = corpus
    expected = features.build_vocab_from_db(path, labels, n_workers=1)
    checkpoint = tmp_path / "checkpoint"
    merge = VocabularyCounts.merge
    interrupted = False

    def interrupt(counts, view):
        nonlocal interrupted
        merge(counts, view)
        if view.family == phase and not interrupted:
            interrupted = True
            raise RuntimeError("simulated interruption after commit")

    monkeypatch.setattr(VocabularyCounts, "merge", interrupt)
    with pytest.raises(RuntimeError, match="simulated interruption"):
        features.build_vocab_from_db(path, labels, n_workers=1, checkpoint_dir=checkpoint)
    assert interrupted
    with sqlite3.connect(checkpoint / "counts.sqlite") as db:
        assert db.execute("SELECT count(*) FROM batches").fetchone()[0] > 0
    monkeypatch.setattr(VocabularyCounts, "merge", merge)
    # Worker-count changes would normally change batch boundaries. Recovery
    # preserves the old boundaries and also works with a spawned worker pool.
    monkeypatch.setattr(features, "_feature_batch_size", lambda _: 5)
    resumed = features.build_vocab_from_db(path, labels, n_workers=2, checkpoint_dir=checkpoint)
    assert asdict(resumed) == asdict(expected)
    assert not (checkpoint / "counts.sqlite").exists()
    assert (checkpoint / "identity").is_file()

    # A completed spec bypasses both DB fetching and recounting.
    from collimator import data
    monkeypatch.setattr(data, "fetch_cleave_results", lambda *_: pytest.fail("recounted completed vocabulary"))
    assert asdict(features.build_vocab_from_db(path, labels, n_workers=1,
                                              checkpoint_dir=checkpoint)) == asdict(expected)
    with pytest.raises(ValueError, match="checkpoint inputs changed"):
        features.build_vocab_from_db(path, labels[:-1], n_workers=1, checkpoint_dir=checkpoint)
    relabeled = [(rid, 1 - label) for rid, label in labels]
    assert features.vocabulary_identity(path, relabeled) != features.vocabulary_identity(path, labels)
    with pytest.raises(ValueError, match="checkpoint inputs changed"):
        features.build_vocab_from_db(path, relabeled, n_workers=1, checkpoint_dir=checkpoint)


def test_failed_merge_rolls_back_counts_and_batch_marker(tmp_path):
    source = tmp_path / "source.sqlite"
    master = tmp_path / "master.sqlite"
    with VocabularyCounts(str(source)) as counts:
        counts.increment("trigram", ("a", "b", "c"), n=5)
        counts.record_batch("count:0", None, 5)
    with VocabularyCounts(str(master), durable=True) as counts:
        counts.db.execute("CREATE TRIGGER reject_progress BEFORE INSERT ON batches "
                          "BEGIN SELECT RAISE(ABORT, 'interrupted'); END")
        counts.db.commit()
        from collimator.vocabulary import CountView
        with pytest.raises(sqlite3.IntegrityError, match="interrupted"):
            counts.merge(CountView(str(source), "trigram"))
        assert counts.db.execute("SELECT count(*) FROM counts").fetchone()[0] == 0
        assert counts.db.execute("SELECT count(*) FROM batches").fetchone()[0] == 0
    with VocabularyCounts(str(master), durable=True, resume=True) as counts:
        counts.db.execute("DROP TRIGGER reject_progress")
        counts.db.commit()
        counts.merge(CountView(str(source), "trigram"))
        assert dict(counts.view("trigram").items()) == {"a + b + c": 5}
        assert len(list(counts.completed_batches("count"))) == 1


def test_sigkill_during_merge_retains_only_committed_progress(tmp_path):
    import subprocess
    import sys
    import time

    source, master, marker = (tmp_path / name for name in ("source.sqlite", "master.sqlite", "merging"))
    with VocabularyCounts(str(source)) as counts:
        counts.increment("trigram", ("a", "b", "c"), n=5)
        counts.record_batch("count:1", None, 5)
    with VocabularyCounts(str(master), durable=True) as counts:
        counts.increment("trigram", ("a", "b", "c"), n=2)
        counts.record_batch("count:0", None, 2)
    code = """
import sys, time
from pathlib import Path
from collimator.vocabulary import VocabularyCounts, CountView
master, source, marker = sys.argv[1:]
with VocabularyCounts(master, durable=True, resume=True) as counts:
    def hold():
        Path(marker).touch()
        time.sleep(60)
        return 0
    counts.db.create_function('hold_merge', 0, hold)
    counts.db.execute('CREATE TRIGGER hold_progress BEFORE INSERT ON batches BEGIN SELECT hold_merge(); END')
    counts.db.commit()
    counts.merge(CountView(source, 'trigram'))
"""
    child = subprocess.Popen([sys.executable, "-c", code, str(master), str(source), str(marker)])
    try:
        deadline = time.monotonic() + 10
        while not marker.exists() and child.poll() is None and time.monotonic() < deadline:
            time.sleep(0.01)
        assert marker.exists(), "child never reached its uncommitted merge"
        child.kill()
        child.wait(timeout=5)
    finally:
        if child.poll() is None:
            child.kill()
            child.wait(timeout=5)
    with VocabularyCounts(str(master), durable=True, resume=True) as counts:
        assert dict(counts.view("trigram").items()) == {"a + b + c": 2}
        assert [row[0] for row in counts.completed_batches("count")] == ["count:0"]
        counts.db.execute("DROP TRIGGER hold_progress")
        counts.db.commit()
        from collimator.vocabulary import CountView
        counts.merge(CountView(str(source), "trigram"))
        assert dict(counts.view("trigram").items()) == {"a + b + c": 7}


def test_disk_candidates_match_exactly_with_tiny_cache(tmp_path):
    path = tmp_path / "candidates.sqlite"
    tokens = [f"p/{i:02d}" for i in range(15)]
    with VocabularyCounts(str(path), durable=True) as counts:
        expected = set()
        for i, triple in enumerate(combinations(tokens, 3)):
            support = 1 + i % 3
            counts.increment("trigram", triple, n=support)
            if support >= 2:
                expected.add(triple)
        counts.flush()
        source = TrigramSource(str(path), 2)
        assert len(pickle.dumps(source)) < 1024
        index = DiskTrigramCandidates(source, cache_bytes=256)
        try:
            for present in (tokens, tokens[::2], ["missing", *tokens[1::2]], tokens):
                assert set(index.matches(present)) == {t for t in expected if set(t) <= set(present)}
                assert index.used_bytes <= 256
        finally:
            index.close()


def test_vocabulary_never_materializes_all_candidates(corpus, monkeypatch):
    path, labels = corpus
    monkeypatch.setattr(VocabularyCounts, "at_least", lambda *_: pytest.fail("loaded candidate list"))
    assert features.build_vocab_from_db(path, labels, n_workers=1).total_features > 0
