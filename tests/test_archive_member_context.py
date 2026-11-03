"""Member context is an opt-in keyword input with independent cache identity."""
import json
import sqlite3

from collimator import cache_identity, data, features, model_config


def corpus(tmp_path):
    path = tmp_path / 'samples.db'
    with sqlite3.connect(path) as conn:
        conn.execute('CREATE TABLE samples (id INTEGER PRIMARY KEY, sha256 TEXT, label TEXT, '
                     'cleave_result TEXT, formula TEXT, elements TEXT, score INTEGER, mtime TEXT)')
        parent = {'files': [{'id': 0, 'sha': 'root', 'traits': [{'id': 'inherited', 'crit': 4, 'conf': 1}]},
                            {'id': 7, 'sha': 'child', 'depth': 1, 'path': 'wheel!!module.py'},
                            {'id': 8, 'sha': 'missing', 'depth': 1}], 'truncated': True}
        leaf = {'files': [{'id': 0, 'ctx': [{'s': 'import subprocess'}],
                           'traits': [{'id': 'should-not-be-added'}], 'facts': {'changed': True}}]}
        for rid,sha,label,report in [(1,'root','good',parent),(2,'child','bad',leaf)]:
            conn.execute('INSERT INTO samples VALUES (?,?,?,?,?,?,?,?)',
                         (rid,sha,label,json.dumps(report),'','',0,''))
    return path,parent


def test_opt_in_changes_context_only(tmp_path,monkeypatch):
    path,parent=corpus(tmp_path)
    monkeypatch.delenv('COLLIMATOR_ARCHIVE_MEMBER_CONTEXT',raising=False)
    original=data.fetch_cleave_results(path,[1],evaluation_labels={1:0})[1]
    assert json.loads(original['cleave_result'])==parent
    monkeypatch.setenv('COLLIMATOR_ARCHIVE_MEMBER_CONTEXT','1')
    result=data.fetch_cleave_results(path,[1],evaluation_labels={1:0})[1]
    expanded=result['cleave_result']
    expected=json.loads(json.dumps(parent));expected['files'][1]['ctx']=[{'s':'import subprocess'}]
    assert expanded==expected
    assert features._report_keywords(expanded['files'],['contextword'])['contextword']=={'import','subprocess'}
    h=cache_identity.evaluation_hasher(path);h.update(result['evaluation_digest'])
    assert h.hexdigest()==cache_identity.evaluation_revision(path,[1],[0])


def test_child_changes_and_missing_leaf_arrival_invalidate_parent(tmp_path,monkeypatch):
    path,_=corpus(tmp_path);monkeypatch.setenv('COLLIMATOR_ARCHIVE_MEMBER_CONTEXT','1')
    before=cache_identity.evaluation_revision(path,[1],[0])
    with sqlite3.connect(path) as conn:
        parent_before=conn.execute('SELECT * FROM samples WHERE id=1').fetchone()
        conn.execute('UPDATE samples SET cleave_result=? WHERE id=2',
                     (json.dumps({'fs':[{'ctx':[{'s':'new context'}]}]}),))
    after=cache_identity.evaluation_revision(path,[1],[0]);assert before!=after
    with sqlite3.connect(path) as conn:
        conn.execute('INSERT INTO samples VALUES (3,?,?,?,?,?,?,?)',
                     ('missing','bad',json.dumps({'files':[{'ctx':[{'s':'late context'}]}]}),'','',0,''))
        assert conn.execute('SELECT * FROM samples WHERE id=1').fetchone()==parent_before
    assert cache_identity.evaluation_revision(path,[1],[0])!=after


def test_whl_default_exposes_member_context_recipe():
    accepted=model_config.load('filetypes/whl')
    run=model_config.as_run(accepted)
    assert run['feature_env']['COLLIMATOR_ARCHIVE_MEMBER_CONTEXT']=='1'
    assert run['feature_env']['COLLIMATOR_CONTEXT_KEYWORD_VOCAB_MAX']=='5000'
    assert run['feature_env']['COLLIMATOR_CONTEXT_KEYWORD_MIN_FREQ']=='2'
    assert run['ensemble_seeds']==[43,44,45,46]


def test_snapshot_cache_reuses_windows_and_missing_leaves_without_stale_reads(monkeypatch):
    monkeypatch.setenv('COLLIMATOR_ARCHIVE_MEMBER_CONTEXT','1')
    monkeypatch.setenv('COLLIMATOR_PG_SNAPSHOT_DATABASE','postgres://test-context')
    monkeypatch.setenv('COLLIMATOR_PG_SNAPSHOT','first')
    class Connection:
        queries=0
        text='first context'
        def execute(self,query,params):
            self.queries+=1
            assert params==[['child','missing']]
            return [('child',[{'s':self.text}])]
    conn=Connection()
    def read():
        return data.add_member_context(conn,{1:{'cleave_result':{'files':[
            {'sha':'child','depth':1},{'sha':'missing','depth':1}]},'evaluation_digest':b'parent'}})[1]
    a=read();b=read();assert conn.queries==1 and a==b
    conn.text='updated context'
    monkeypatch.setenv('COLLIMATOR_PG_SNAPSHOT','second')
    c=read();assert conn.queries==2 and c['evaluation_digest']!=a['evaluation_digest']
    monkeypatch.delenv('COLLIMATOR_PG_SNAPSHOT')
    read();read();assert conn.queries==4


def test_context_cache_has_byte_and_entry_bounds(monkeypatch):
    monkeypatch.setattr(data,'_MEMBER_CONTEXT_CACHE_LIMIT',600)
    key=('test-bound','snapshot')
    for i in range(10):data._member_context_cache(key,str(i),(b'x'*20,'digest'))
    assert len(data._MEMBER_CONTEXT_CACHE)==2
    assert data._MEMBER_CONTEXT_CACHE_BYTES<=600
    assert data._member_context_cache(key,'0') is None
    assert data._member_context_cache(key,'9') is not None
