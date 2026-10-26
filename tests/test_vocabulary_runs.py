from collections import Counter
from itertools import combinations
import sqlite3
import struct

import numpy as np
import pytest

from collimator.vocabulary_runs import SignatureRuns, _merge
from collimator import vocabulary_runs
from collimator.vocabulary import VocabularyCounts, _materialize_partition

@pytest.mark.parametrize('width', [4, 8, 12, 16])
def test_streaming_merge_equal_keys_on_read_boundaries(tmp_path, monkeypatch, width):
    monkeypatch.setattr(vocabulary_runs, '_READ_KEYS', 3)
    dtype=np.dtype([('key', f'V{width}'),('n','<i8')])
    a=[0,1,3,5,6,8,100,2**32-1];b=[0,2,3,4,5,7,8,9,100]
    for name,values in [('a',a),('b',b)]:
        rows=np.empty(len(values),dtype=dtype)
        rows['key']=[v.to_bytes(width,'big') for v in values];rows['n']=7 if name=='a' else 11
        rows.tofile(tmp_path/name)
    _merge(tmp_path/'a',tmp_path/'b',tmp_path/'c',dtype)
    actual={int.from_bytes(bytes(r['key']),'big'):int(r['n']) for r in np.fromfile(tmp_path/'c',dtype=dtype)}
    assert actual=={v:(7 if v in a else 0)+(11 if v in b else 0) for v in set(a+b)}

@pytest.mark.parametrize('reducer', ['upsert','sorted'])
def test_partition_reducer_exact_across_chunks_and_families(tmp_path,monkeypatch,reducer):
    monkeypatch.setenv('COLLIMATOR_VOCAB_REDUCER',reducer)
    monkeypatch.setenv('COLLIMATOR_VOCAB_REDUCE_KEYS','7')
    monkeypatch.setattr(vocabulary_runs,'_READ_KEYS',2)
    source=tmp_path/'source.sqlite';output=tmp_path/'output.sqlite';expected=Counter()
    with VocabularyCounts(str(source),defer_signatures=True) as counts:
        for family,k in [('pairs',2),('triples',3),('quads',4)]:
            for i in range(15):
                paths=[f'p{x}' for x in range(i%4,i%4+6)]
                counts.group_combinations(family,paths,k,n=i+1)
                expected.update({(family,' + '.join(parts)):i+1 for parts in combinations(paths,k)})
    _materialize_partition(str(source),str(output),0,1,'done')
    with VocabularyCounts(str(output),resume=True) as counts:
        actual={}
        for family in ('pairs','triples','quads'):
            actual.update({(family,k):v for k,v in counts.view(family).items()})
        assert actual==expected
        assert counts.db.execute('SELECT id,n_rows FROM batches').fetchall()==[('done',0)]


def test_failed_sorted_partition_has_no_receipt_and_source_is_retryable(tmp_path,monkeypatch):
    monkeypatch.setenv('COLLIMATOR_VOCAB_REDUCER','sorted')
    source=tmp_path/'source.sqlite';failed=tmp_path/'failed.sqlite'
    with VocabularyCounts(str(source),defer_signatures=True) as counts:
        counts.group_combinations('trigram',['a','b','c','d'],3,n=2**40)
    original=SignatureRuns.finish
    def fail(self,db):
        original(self,db)
        raise RuntimeError('interrupted before receipt')
    monkeypatch.setattr(SignatureRuns,'finish',fail)
    with pytest.raises(RuntimeError,match='before receipt'):
        _materialize_partition(str(source),str(failed),0,1,'materialize:0')
    with sqlite3.connect(failed) as db:
        assert not db.execute('SELECT id FROM batches').fetchall()
    assert not list(tmp_path.glob('sorted-runs-*'))
    monkeypatch.setattr(SignatureRuns,'finish',original)
    _materialize_partition(str(source),str(tmp_path/'retry.sqlite'),0,1,'materialize:0')
    with VocabularyCounts(str(tmp_path/'retry.sqlite'),resume=True) as counts:
        assert dict(counts.view('trigram').items())=={' + '.join(c):2**40 for c in combinations('abcd',3)}
    with sqlite3.connect(source) as db:
        assert db.execute('SELECT n FROM signatures').fetchall()==[(2**40,)]


@pytest.mark.parametrize('variable,value', [('COLLIMATOR_VOCAB_REDUCE_CACHE_MIB','0'),('COLLIMATOR_VOCAB_REDUCE_KEYS','0'),('COLLIMATOR_VOCAB_REDUCE_KEYS','4194305'),('COLLIMATOR_VOCAB_REDUCER','typo')])
def test_invalid_worker_settings_fail_clearly(tmp_path,monkeypatch,variable,value):
    monkeypatch.setenv(variable,value)
    with VocabularyCounts(str(tmp_path/'source.sqlite')):pass
    with pytest.raises(ValueError,match=variable):
        _materialize_partition(str(tmp_path/'source.sqlite'),str(tmp_path/'output.sqlite'),0,1,'done')


def test_resume_keeps_partition_assignment_across_reducer_changes(tmp_path,monkeypatch):
    from collimator import vocabulary
    monkeypatch.setattr(vocabulary,'_PARALLEL_MATERIALIZE_KEYS',0)
    monkeypatch.setenv('COLLIMATOR_VOCAB_REDUCER','sorted')
    path=tmp_path/'master.sqlite';expected=Counter()
    with VocabularyCounts(str(path),defer_signatures=True,durable=True,materialize_workers=3) as counts:
        for i in range(12):
            paths=[f'p{x}' for x in range(i,i+6)]
            counts.group_combinations('trigram',paths,3,n=i+1)
            expected.update({' + '.join(c):i+1 for c in combinations(paths,3)})
        counts.flush()
        original=counts.merge_many
        def interrupt(views):
            original(views)
            raise RuntimeError('stop after committed partition')
        monkeypatch.setattr(counts,'merge_many',interrupt)
        with pytest.raises(RuntimeError,match='committed partition'):
            counts.materialize()
        assert counts.db.execute("SELECT count(*) FROM batches WHERE id LIKE 'materialize:%'").fetchone()[0]==1
    monkeypatch.setenv('COLLIMATOR_VOCAB_REDUCER','upsert')
    with VocabularyCounts(str(path),resume=True,defer_signatures=True,durable=True,materialize_workers=1) as counts:
        assert dict(counts.view('trigram').items())==expected
        assert counts.state('materialization') is None
        assert counts.db.execute("SELECT count(*) FROM batches WHERE id LIKE 'materialize:%'").fetchone()[0]==3


def test_feature_revision_includes_sorted_reducer(tmp_path,monkeypatch):
    from pathlib import Path
    from collimator import cache_identity
    root=Path(cache_identity.__file__).parent
    for name in ('features.py','matrix_store.py','vocabulary.py','vocabulary_runs.py','allowlist.py','data.py','filegroups.py','cache_identity.py'):
        (tmp_path/name).write_bytes((root/name).read_bytes())
    monkeypatch.setattr(cache_identity,'__file__',str(tmp_path/'cache_identity.py'))
    cache_identity.code_revision.cache_clear()
    try:
        before=cache_identity.code_revision('features')
        with (tmp_path/'vocabulary_runs.py').open('a') as f:f.write('\n# changed reducer\n')
        assert cache_identity.code_revision('features')==before
        cache_identity.code_revision.cache_clear()  # A new process captures new code.
        assert cache_identity.code_revision('features')!=before
    finally:
        cache_identity.code_revision.cache_clear()
