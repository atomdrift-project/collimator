"""Global signature aggregation is exact and recoverable at both commit boundaries."""
from collections import Counter
from itertools import combinations
import shutil
import sqlite3

import pytest

from collimator import vocabulary
from collimator.vocabulary import CountView, VocabularyCounts


@pytest.mark.parametrize('stable', [False, True])
@pytest.mark.parametrize('collision', [False, True])
def test_repeated_signatures_across_shards_preserve_archive_unions(tmp_path, monkeypatch, stable, collision):
    if collision:
        monkeypatch.setattr(vocabulary, '_token_hash', lambda _: 7)
    expected = Counter()
    with VocabularyCounts(str(tmp_path/'master.sqlite'), defer_signatures=True) as merged:
        for batch in range(4):
            path = tmp_path / f'worker{batch}.sqlite'
            with VocabularyCounts(str(path), defer_signatures=True, stable_token_ids=stable,
                                  signature_bytes=1, buffer_size=2) as worker:
                worker._token_id('a' if batch%2 else 'z')
                worker.group_combinations('trigram', ['a','b','c','d'], 3, n=batch+1)
                expected.update({' + '.join(x):batch+1 for x in combinations('abcd',3)})
                for tokens in ('abc', 'bce', 'abc'):
                    worker.increment_combinations('trigram', tokens, 3, batch)
                expected.update({'a + b + c', 'b + c + e'})
                worker.record_batch(f'count:{batch}', None, batch+2)
            merged.merge(CountView(str(path),'trigram'))
        assert merged.db.execute('SELECT count(*),sum(n) FROM signatures').fetchone() == (1,10)
        assert len(list(merged.completed_batches('count'))) == 4
        assert dict(merged.view('trigram').items()) == expected
        assert merged.db.execute('SELECT count(*) FROM signatures').fetchone()[0] == 0
        merged.materialize()
        assert dict(merged.view('trigram').items()) == expected


def test_materialization_rollback_then_reopen_counts_each_signature_once(tmp_path, monkeypatch):
    path=tmp_path/'master.sqlite'
    with VocabularyCounts(str(path), defer_signatures=True, durable=True) as counts:
        counts.group_combinations('bigram', ['a','b','c'], 2, n=9)
        counts.flush()
        original=counts._reduce_signatures
        def fail(**kwargs):
            original(**kwargs)
            raise RuntimeError('interrupted after increments')
        monkeypatch.setattr(counts,'_reduce_signatures',fail)
        with pytest.raises(RuntimeError,match='interrupted'):
            counts.materialize()
        assert counts.db.execute('SELECT count(*) FROM counts').fetchone()[0] == 0
        assert counts.db.execute('SELECT sum(n) FROM signatures').fetchone()[0] == 9
    with VocabularyCounts(str(path),defer_signatures=True,durable=True,resume=True) as counts:
        assert dict(counts.view('bigram').items()) == {'a + b':9,'a + c':9,'b + c':9}


def test_failed_signature_merge_keeps_counts_and_progress_atomic(tmp_path):
    path=tmp_path/'source.sqlite';master=tmp_path/'master.sqlite'
    with VocabularyCounts(str(path),defer_signatures=True) as worker:
        worker.group_combinations('bigram',['a','b'],2,n=5)
        worker.record_batch('count:1',None,5)
    backup=tmp_path/'retry.sqlite';shutil.copyfile(path,backup)
    with VocabularyCounts(str(master),defer_signatures=True,durable=True) as merged:
        merged.db.execute("CREATE TRIGGER reject BEFORE INSERT ON batches BEGIN SELECT RAISE(ABORT,'interrupted'); END")
        merged.db.commit()
        with pytest.raises(sqlite3.IntegrityError,match='interrupted'):
            merged.merge(CountView(str(path),'bigram'))
        assert merged.db.execute('SELECT count(*) FROM signatures').fetchone()[0] == 0
        assert list(merged.completed_batches('count')) == []
    with VocabularyCounts(str(master),defer_signatures=True,durable=True,resume=True) as merged:
        merged.db.execute('DROP TRIGGER reject');merged.db.commit()
        merged.merge(CountView(str(path),'bigram'))
        merged.merge(CountView(str(backup),'bigram'))
        assert dict(merged.view('bigram').items()) == {'a + b':5}
        assert len(list(merged.completed_batches('count'))) == 1


def test_deferred_view_refuses_partial_counts(tmp_path):
    path=tmp_path/'source.sqlite'
    with VocabularyCounts(str(path),defer_signatures=True) as worker:
        worker.group_combinations('bigram',['a','b'],2,n=5)
    with pytest.raises(ValueError,match='materialized'):
        list(CountView(str(path),'bigram').items())


def test_parallel_expansion_resumes_only_uncommitted_partitions(tmp_path, monkeypatch):
    monkeypatch.setattr(vocabulary,'_PARALLEL_MATERIALIZE_KEYS',0)
    path=tmp_path/'master.sqlite'
    expected=Counter()
    with VocabularyCounts(str(path),defer_signatures=True,durable=True,materialize_workers=3,
                          materialize_merge_size=2) as counts:
        for i in range(12):
            tokens=[f'path/{j:03d}' for j in range(i,i+5)]
            counts.group_combinations('trigram',tokens,3,n=i+1)
            expected.update({' + '.join(c):i+1 for c in combinations(tokens,3)})
        counts.flush()
        original=counts.merge_many
        def stop_after_commit(views):
            original(views)
            raise RuntimeError('stopped after partition commit')
        monkeypatch.setattr(counts,'merge_many',stop_after_commit)
        with pytest.raises(RuntimeError,match='partition commit'):
            counts.materialize()
        assert counts.db.execute("SELECT count(*) FROM batches WHERE id LIKE 'materialize:%'").fetchone()[0] == 2
        assert counts.db.execute('SELECT count(*) FROM signatures').fetchone()[0] == 12
        assert counts.state('materialization')['partitions'] == 3
    # A reduced worker budget must retain the original partition assignment.
    with VocabularyCounts(str(path),defer_signatures=True,durable=True,resume=True,materialize_workers=1) as counts:
        assert dict(counts.view('trigram').items()) == expected
        assert counts.state('materialization') is None
        assert counts.db.execute('SELECT count(*) FROM signatures').fetchone()[0] == 0
        assert counts.db.execute("SELECT count(*) FROM batches WHERE id LIKE 'materialize:%'").fetchone()[0] == 3


def test_in_memory_parallel_request_falls_back_to_serial():
    with VocabularyCounts(defer_signatures=True,materialize_workers=2) as counts:
        counts.group_combinations('bigram',['a','b','c'],2,n=3)
        assert counts.view('bigram') == {'a + b':3,'a + c':3,'b + c':3}


def test_checkpoint_owner_cleans_only_orphan_work_directories(tmp_path):
    from collimator.features import _vocabulary_counts
    checkpoint=tmp_path/'checkpoint';checkpoint.mkdir()
    outside=tmp_path/'outside';outside.mkdir()
    (outside/'keep').write_text('keep')
    (checkpoint/'materialize-link').symlink_to(outside,target_is_directory=True)
    for name in ('workers-dead','materialize-dead','keep'):
        (checkpoint/name).mkdir()
        (checkpoint/name/'data').write_text('data')
    with _vocabulary_counts(checkpoint):
        assert not (checkpoint/'workers-dead').exists()
        assert not (checkpoint/'materialize-dead').exists()
        assert (checkpoint/'keep/data').read_text()=='data'
        assert (outside/'keep').read_text()=='keep'
        assert (checkpoint/'materialize-link').is_symlink()


def test_sigkill_during_expansion_rolls_back_counts_and_source_removal(tmp_path):
    import subprocess
    import sys
    import time
    path=tmp_path/'master.sqlite';marker=tmp_path/'deleting'
    with VocabularyCounts(str(path),defer_signatures=True,durable=True) as counts:
        counts.group_combinations('bigram',['a','b','c'],2,n=9)
    code='''
import sys,time
from pathlib import Path
from collimator.vocabulary import VocabularyCounts
path,marker=sys.argv[1:]
with VocabularyCounts(path,defer_signatures=True,durable=True,resume=True) as counts:
    def hold():
        Path(marker).touch()
        time.sleep(60)
        return 0
    counts.db.create_function('hold',0,hold)
    counts.db.execute("CREATE TRIGGER hold_delete BEFORE DELETE ON signatures BEGIN SELECT hold(); END")
    counts.db.commit()
    counts.materialize()
'''
    child=subprocess.Popen([sys.executable,'-c',code,str(path),str(marker)])
    try:
        deadline=time.monotonic()+15
        while not marker.exists() and child.poll() is None and time.monotonic()<deadline:
            time.sleep(.01)
        assert marker.exists(),'child did not enter uncommitted signature removal'
        child.kill();child.wait(timeout=5)
    finally:
        if child.poll() is None:
            child.kill();child.wait(timeout=5)
    with VocabularyCounts(str(path),defer_signatures=True,durable=True,resume=True) as counts:
        assert counts.db.execute('SELECT count(*) FROM counts').fetchone()[0]==0
        assert counts.db.execute('SELECT sum(n) FROM signatures').fetchone()[0]==9
        counts.db.execute('DROP TRIGGER hold_delete');counts.db.commit()
        assert dict(counts.view('bigram').items())=={'a + b':9,'a + c':9,'b + c':9}
