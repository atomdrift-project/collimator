import json
import sys
from pathlib import Path
import pytest
from collimator import model_config
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
import merge_azoth_promotions as merger


def document(route='filetypes/batch'):
    return {'schema':model_config.SCHEMA,'route':route,'experiment_key':'a'*16,
            'updated_at':'2026-10-28T00:00:00Z','train_config':{'n_estimators':200,'max_delta_step':2},
            'feature_env':{'COLLIMATOR_MIN_SAMPLE_SCORE':'0'},'min_malware_training_score':0}


def test_editing_one_model_file_changes_the_replay_config(tmp_path):
    d=document();model_config.save(tmp_path,d)
    path=model_config.config_path(tmp_path,d['route'])
    changed=json.loads(path.read_text());changed['train_config']['max_delta_step']=5
    path.write_text(json.dumps(changed))
    replay=model_config.as_run(model_config.load(d['route'],tmp_path))
    assert replay['train_config']['max_delta_step']==5
    assert replay['experiment_spec']['train_config']['max_delta_step']==5
    assert replay['experiment_spec']['filters']['min_malware_training_score']==0
    with pytest.raises(ValueError):model_config.config_path(tmp_path,'filetypes/../escape')
    changed['min_malware_training_score']=True
    path.write_text(json.dumps(changed))
    with pytest.raises(ValueError):model_config.load(d['route'],tmp_path)


def test_merge_preserves_newer_registry_and_hand_edits(tmp_path):
    history=tmp_path/'history';history.mkdir();runs=tmp_path/'runs';runs.mkdir();configs=tmp_path/'configs'
    route='filetypes/batch';oldkey='b'*16;newkey='c'*16
    old={'route':route,'full_train_key':oldkey,'updated_at':'2026-08-01'}
    current={'route':route,'full_train_key':newkey,'updated_at':'2026-10-01'}
    (history/'accepted-baseline-snapshots.json').write_text(json.dumps([{'document':{'routes':{route:old}}}]))
    (history/'installed-research-snapshots.json').write_text('[]')
    registry=tmp_path/'registry.json';registry.write_text(json.dumps({'routes':{route:current}}))
    d=document();d['experiment_key']=newkey
    (runs/f'{newkey}.json').write_text(json.dumps(model_config.as_run(d)))
    merger.merge(history,registry,runs,configs)
    assert json.loads(registry.read_text())['routes'][route]['full_train_key']==newkey
    d=model_config.load(route,configs);d['train_config']['n_estimators']=123;model_config.save(configs,d)
    merger.merge(history,registry,runs,configs)
    assert model_config.load(route,configs)['train_config']['n_estimators']==123
