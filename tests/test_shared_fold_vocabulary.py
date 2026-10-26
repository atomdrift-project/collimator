"""Fold-isolated raw counts are shared without sharing selected vocabularies."""
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

from collimator import features
from collimator.vocabulary import VocabularyCounts


@pytest.fixture
def corpus(tmp_path, monkeypatch):
    for key in ("BIGRAM_MIN_FREQ", "TRIGRAM_MIN_FREQ", "TIERED_BIGRAM_MIN_FREQ", "TIERED_TRIGRAM_MIN_FREQ"):
        monkeypatch.setenv("COLLIMATOR_"+key, "1")
    monkeypatch.setenv("COLLIMATOR_TRIGRAM_MAX", "100")
    monkeypatch.setenv("COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC", "0.3")
    monkeypatch.setattr(features, "_feature_batch_size", lambda _: 4)
    features.feature_config_from_env.cache_clear()
    path = tmp_path/"samples.sqlite"
    rows = [(i, int((i//2)%3 != 0)) for i in range(1, 41)]
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE samples(id INTEGER PRIMARY KEY,cleave_result TEXT,formula TEXT,elements TEXT,score INTEGER,mtime TEXT)")
        for rid, label in rows:
            tokens = [f"fold{rid%2}/path{i}::finding" for i in range(rid%4, rid%4+5)]
            files = [{"type":"elf", "ts":[{"i":t,"l":4,"c":1.0} for t in tokens],
                      "ms":{"binary":{"size":rid}}}]
            if rid%5 == 0:
                files.append({"type":"pdf", "ts":[{"i":t,"l":4,"c":1.0} for t in tokens[:3]]})
            report = json.dumps({"v":"4","fs":files}) if rid != 17 else "null"
            db.execute("INSERT INTO samples VALUES(?,?,?,?,?,?)", (rid,report,"C2H6",f"E{rid%3}",label*5,""))
    yield path, rows
    features.feature_config_from_env.cache_clear()


@pytest.mark.parametrize("order", [("prod",0,1),(1,"prod",0)])
def test_shared_discovery_halves_row_visits_and_preserves_each_spec(corpus, tmp_path, monkeypatch, order):
    path, rows = corpus
    cohorts = {"prod":rows, 0:[r for r in rows if r[0]%2 == 0], 1:[r for r in rows if r[0]%2 == 1]}
    visits = []
    original = features._count_labeled_vocab_batch
    def count(dsn, batch, counts):
        visits.extend(rid for rid, _ in batch)
        return original(dsn, batch, counts)
    monkeypatch.setattr(features, "_count_labeled_vocab_batch", count)
    expected = {k:asdict(features.build_vocab_from_db(path, selected, n_workers=1)) for k,selected in cohorts.items()}
    assert len(visits) == 2*len(rows)
    visits.clear()
    shared = tmp_path/"shared"
    for key in order:
        selected = cohorts[key]
        actual = features.build_vocab_from_db(path, selected, n_workers=1,
            checkpoint_dir=tmp_path/f"consumer-{key}", shared_cache_dir=shared,
            row_folds=(rid%2 for rid, _ in selected))
        assert asdict(actual) == expected[key]
    assert sorted(visits) == [rid for rid, _ in rows]
    assert len(list(shared.glob("*/discovery.sqlite"))) == 2
    # Fold-exclusive paths must never appear in the opposite vocabulary.
    assert not any("fold1/" in name for name in expected[0]["feature_names"])
    assert not any("fold0/" in name for name in expected[1]["feature_names"])


def test_publish_interruption_reuses_completed_work_without_recount(corpus, tmp_path, monkeypatch):
    path, rows = corpus
    replace = features.os.replace
    def fail(source, target):
        if Path(target).name == "discovery.sqlite":
            raise OSError("interrupted publication")
        return replace(source,target)
    monkeypatch.setattr(features.os, "replace", fail)
    with pytest.raises(OSError, match="publication"):
        features._published_fold_counts(path, rows, 1, tmp_path/"shared")
    monkeypatch.setattr(features.os, "replace", replace)
    monkeypatch.setattr(features, "_count_labeled_vocab_batch", lambda *_: pytest.fail("recounted completed fold"))
    published = features._published_fold_counts(path, rows, 1, tmp_path/"shared")
    assert published.is_file()
    with sqlite3.connect(published) as db:
        assert db.execute("SELECT n_rows FROM batches").fetchone()[0] == len(rows)


def test_parallel_shared_raw_counts_and_summaries_equal_independent(corpus, tmp_path):
    path, rows = corpus
    def canonical(counts):
        counts.materialize()
        families = sorted({r[0] for r in counts.iter_counts()})
        return {family:dict(counts.view(family).items()) for family in families}
    with features._vocabulary_counts(tmp_path/"independent") as (counts,scratch):
        expected_summary = features._count_vocab_rows(path, rows, 2, counts, scratch)
        expected_counts = canonical(counts)
    with features._vocabulary_counts(tmp_path/"consumer") as (counts,scratch):
        actual_summary = features._shared_fold_counts(path, rows, (rid%2 for rid,_ in rows),
                                                     2, counts, tmp_path/"shared")
        assert actual_summary == expected_summary
        assert canonical(counts) == expected_counts


def test_consumer_restart_after_commit_does_not_double_counts(corpus, tmp_path, monkeypatch):
    path, rows = corpus
    expected = asdict(features.build_vocab_from_db(path, rows, n_workers=1))
    attach = VocabularyCounts.attach_shared
    stopped = False
    def interrupt(counts, view):
        nonlocal stopped
        attach(counts, view)
        if not stopped:
            stopped = True
            raise RuntimeError("after shared commit")
    monkeypatch.setattr(VocabularyCounts,"attach_shared",interrupt)
    options = dict(n_workers=1, checkpoint_dir=tmp_path/"consumer", shared_cache_dir=tmp_path/"shared")
    with pytest.raises(RuntimeError, match="shared commit"):
        features.build_vocab_from_db(path, rows, row_folds=[rid%2 for rid,_ in rows], **options)
    monkeypatch.setattr(VocabularyCounts,"attach_shared",attach)
    actual = features.build_vocab_from_db(path, rows, row_folds=[rid%2 for rid,_ in rows], **options)
    assert asdict(actual) == expected


def test_changed_selection_labels_or_settings_cannot_hit_shared_counts(corpus, tmp_path, monkeypatch):
    path, rows = corpus
    root = tmp_path/"shared"
    first = features._published_fold_counts(path, rows, 1, root)
    before = hashlib.sha256(first.read_bytes()).hexdigest()
    changed_labels = [(rid,1-label) for rid,label in rows]
    second = features._published_fold_counts(path, changed_labels, 1, root)
    third = features._published_fold_counts(path, rows[:-1], 1, root)
    monkeypatch.setenv("COLLIMATOR_BIGRAM_MIN_FREQ", "2")
    features.feature_config_from_env.cache_clear()
    fourth = features._published_fold_counts(path, rows, 1, root)
    assert len({first,second,third,fourth}) == 4
    assert hashlib.sha256(first.read_bytes()).hexdigest() == before


def test_concurrent_producers_publish_once(corpus, tmp_path):
    path, rows = corpus
    code = '''
import json,sys,time
from pathlib import Path
from collimator import features
db,root,visits,rows=sys.argv[1:]
original=features._count_labeled_vocab_batch
def count(dsn,batch,counts):
    with open(visits,'a') as f:f.write(json.dumps(batch)+'\\n')
    time.sleep(.2)
    return original(dsn,batch,counts)
features._count_labeled_vocab_batch=count
features._published_fold_counts(db,json.loads(rows),1,Path(root))
'''
    command = [sys.executable,"-c",code,str(path),str(tmp_path/"shared"),str(tmp_path/"visits"),json.dumps(rows)]
    children = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(2)]
    try:
        for child in children:
            stdout,stderr=child.communicate(timeout=30)
            assert child.returncode == 0, stderr.decode()
    finally:
        for child in children:
            if child.poll() is None:
                child.kill();child.wait()
    visits = [rid for line in (tmp_path/"visits").read_text().splitlines() for rid,_ in json.loads(line)]
    assert sorted(visits) == [rid for rid,_ in rows]
    assert len(list((tmp_path/"shared").glob("*/discovery.sqlite"))) == 1


@pytest.mark.parametrize("folds", [[0], [2]*40])
def test_invalid_fold_assignments_rejected_before_counting(corpus,tmp_path,folds):
    path,rows=corpus
    with pytest.raises(ValueError):
        features.build_vocab_from_db(path,rows,n_workers=1,shared_cache_dir=tmp_path/"shared",row_folds=folds)
    assert not list((tmp_path/"shared").glob("*/discovery.sqlite"))
