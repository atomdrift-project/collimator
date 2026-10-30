import json
from pathlib import Path
import shutil
import sys
import numpy as np
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import azoth_refresh_specialists as refresh
import azoth_route_policy_eval as evaluate


def test_partition_uses_captured_buckets_without_general_cache(tmp_path):
    table = {'row_ids': np.arange(6), 'sha_bucket': np.array([0,31,32,63,64,255])}
    assert evaluate._partition_mask(table, 'test', tmp_path/'nonexistent').tolist() == [True,True,False,False,False,False]
    assert evaluate._partition_mask(table, 'dev').tolist() == [False,False,True,True,False,False]
    assert evaluate._partition_mask(table, 'train').tolist() == [False,False,False,False,True,True]
    with pytest.raises(ValueError, match='canonical buckets'):
        evaluate._partition_mask({**table, 'sha_bucket': np.array([256]*6)}, 'test')


def test_legacy_partition_requires_matching_ids(tmp_path):
    cache = tmp_path/'general.npz'
    np.savez(cache, row_ids=np.array([2,1]), canonical_shas=np.array(['0'*62+'20','0'*64]))
    assert evaluate._partition_mask({'row_ids':np.array([1,2])}, 'test', cache).tolist() == [True,False]
    with pytest.raises(KeyError):
        evaluate._partition_mask({'row_ids':np.array([3])}, 'test', cache)


def test_scoped_update_never_scores_general_or_train_and_preserves_other_routes(tmp_path, monkeypatch):
    baseline=tmp_path/'baseline';baseline.mkdir()
    source=tmp_path/'candidate';source.mkdir()
    for directory,content in [(baseline/'general',b'general'),(baseline/'filetypes/foo',b'old'),(baseline/'filetypes/bar',b'bar'),(source,b'new')]:
        directory.mkdir(parents=True,exist_ok=True)
        (directory/'model.onnx').write_bytes(content)
        (directory/'feature_spec.json').write_text('{}')
    table={'row_ids':np.arange(1,7), 'labels':np.array([1,0,1,0,1,0]),
           'sha_bucket':np.array([0,32,0,32,64,64]), 'file_types':np.array(['foo','foo','bar','bar','foo','bar']),
           'file_groups':np.array(['source']*6), 'route_names':np.array(['general','filetypes/foo','filetypes/bar']),
           'route_kinds':np.array(['general','filetype','filetype']), 'score_space':np.array('raw'),
           'scores':np.array([[.1,.2,.3,.4,.5,.6],[.2,.3,np.nan,np.nan,.7,np.nan],[np.nan,np.nan,.8,.9,np.nan,.2]],dtype=np.float32)}
    scores=tmp_path/'scores.npz';np.savez(scores,**table)
    config={'score_table_hash':refresh.digest(scores), 'filetype_to_group':{'foo':'source','bar':'source'},
        'models':[{'route':r} for r in table['route_names']], 'levels':[{'level':25,'hostile':{'target_per_million':.25,
        'thresholds':{'general':.91,'filetypes/foo':.92,'filetypes/bar':.93},'diagnostics':{}}}]}
    policies={'score_table_hash':refresh.digest(scores),'routes':{'filetypes/foo':{'old':True},'filetypes/bar':{'keep':'exact'}}}
    (baseline/'config.json').write_text(json.dumps(config));(baseline/'route_policies.json').write_text(json.dumps(policies))
    candidates=tmp_path/'candidates.json'
    candidates.write_text(json.dumps({'candidates':[{'route':'foo','source':str(source),'model_revision':'new'}]}))
    monkeypatch.setattr(refresh.cache_identity,'require_reserved_dev',lambda _:None)
    monkeypatch.setattr(refresh.cache_identity,'model_revision',lambda p:(p/'model.onnx').read_text())
    calls=[]
    def score(source,ids,labels,*args):
        calls.append(ids.tolist());return np.array([.8,.1],dtype=np.float32)
    monkeypatch.setattr(refresh,'score_route',score)
    monkeypatch.setattr(refresh,'_copy_route',lambda s,d:shutil.copytree(s,d) or True)
    monkeypatch.setattr(refresh.calibration,'_calibrate_one',lambda *a,**kw:{'thresholds':{'filetypes/foo':.75},'diagnostics':{'filetypes/foo':{}}})
    monkeypatch.setattr(refresh.search,'_SHARED',{})
    def process(ft):
        # Policy selection must only see dev, even though test scores exist.
        assert refresh.search._SHARED['labels'].tolist()==[0,0]
        assert ft=='foo'
        return 'filetypes/foo',{'new':True}
    monkeypatch.setattr(refresh.search,'_process_filetype',process)
    monkeypatch.setattr(refresh.search,'_enforce_level_dominance',lambda _:None)
    monkeypatch.setattr(refresh.search,'_level_monotonicity_errors',lambda _:[])
    monkeypatch.setattr(refresh.search,'_write_markdown',lambda *a:None)
    output=tmp_path/'output'
    monkeypatch.setattr(sys,'argv',['refresh','--baseline',str(baseline),'--score-table',str(scores),
                                  '--candidates',str(candidates),'--output',str(output)])
    refresh.main()
    assert calls==[[1,2]]
    new_config=json.loads((output/'runtime/config.json').read_text())
    assert new_config['levels'][0]['hostile']['thresholds']=={'general':.91,'filetypes/foo':.75,'filetypes/bar':.93}
    new_policy=json.loads((output/'runtime/route_policies.json').read_text())
    assert new_policy['routes']['filetypes/bar']==policies['routes']['filetypes/bar']
    with np.load(output/'scores.npz') as result:
        np.testing.assert_array_equal(result['scores'][0],table['scores'][0,:4])
        np.testing.assert_array_equal(result['scores'][2],table['scores'][2,:4])
        assert result['row_ids'].tolist()==[1,2,3,4]
    (output/'runtime/general/model.onnx').write_bytes(b'changed')
    with pytest.raises(AssertionError):
        refresh.assert_frozen(baseline,output/'runtime',{'filetypes/foo'})
