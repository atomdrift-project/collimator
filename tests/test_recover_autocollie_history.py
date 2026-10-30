import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('recovery',Path(__file__).parents[1]/'scripts/recover_autocollie_history.py')
recovery=importlib.util.module_from_spec(spec);spec.loader.exec_module(recovery)


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value))


def run_record(key,date):
    return {'experiment_key':key,'route':'filetypes/batch','timestamp':date,
            'experiment_spec':{'filters':{'min_malware_training_score':0},'train_config':{'n_estimators':200}}}


def test_retains_recent_and_accepted_dependency_chain_without_repromoting(tmp_path):
    source=tmp_path/'source';dest=tmp_path/'history';active=tmp_path/'active'
    accepted='a'*16;original='b'*16;recent='c'*16;expired='d'*16
    for k,date in [(accepted,'2026-07-01'),(original,'2026-06-30'),(recent,'2026-10-20'),(expired,'2026-08-01')]:
        save(source/'experiments/azoth/runs'/f'{k}.json',run_record(k,date))
    save(source/'models/azoth/.autocollie/promoted_baselines.json',{'routes':{'filetypes/batch':{'full_train_key':accepted}}})
    events=[{'ts':'2026-07-01T00:00:00Z','cycle_id':'promote','type':'screen-finished','payload':{'experiment_key':accepted,'original_key':original}},
            {'ts':'2026-07-01T01:00:00Z','cycle_id':'promote','type':'cycle-complete','payload':{'verdict':'pass'}},
            {'ts':'2026-08-01T00:00:00Z','cycle_id':'expired','type':'screen-finished','payload':{'experiment_key':expired}},
            {'ts':'2026-10-20T00:00:00Z','cycle_id':'recent','type':'screen-finished','payload':{'experiment_key':recent}}]
    ep=source/'autocollie/events.jsonl';ep.parent.mkdir(parents=True);ep.write_text(''.join(json.dumps(e)+'\n' for e in events)+'broken\n')
    report=recovery.recover([source],dest,datetime(2026,10,28,tzinfo=timezone.utc),publish_runs=active)
    assert report['runs']==3 and report['events']==3 and report['invalid_records']==1
    assert not (active/f'{expired}.json').exists()
    assert json.loads((active/f'{accepted}.json').read_text())['experiment_spec']['filters']['min_malware_training_score']==0
    assert not (active.parent/'models').exists()
    assert not report['current_promotions_modified']
    assert len((dest/'decisions.jsonl').read_text().splitlines())==1
    assert source.joinpath('autocollie/events.jsonl').read_text().endswith('broken\n')


def test_current_runs_not_overwritten_and_nonempty_snapshot_rejected(tmp_path):
    source=tmp_path/'source';dest=tmp_path/'history';active=tmp_path/'active';key='e'*16
    save(source/'experiments/azoth/runs'/f'{key}.json',run_record(key,'2026-10-20'))
    original={**run_record(key,'2026-10-20'),'extra':'current paired evidence'}
    save(active/f'{key}.json',original)
    report=recovery.recover([source],dest,datetime(2026,10,28,tzinfo=timezone.utc),publish_runs=active)
    assert report['publish_conflicts']==[str(active/f'{key}.json')]
    assert json.loads((active/f'{key}.json').read_text())==original
    with pytest.raises(ValueError,match='empty'):
        recovery.recover([source],dest,datetime(2026,10,28,tzinfo=timezone.utc))


def test_installation_snapshot_excludes_held_back_candidates(tmp_path):
    root=tmp_path/'out';installation=root/'deployments/release/specialists-only'
    save(installation/'installed.json',{'status':'installed','changed_specialists':['filetypes/gem'],'timestamp':'2026-10-28'})
    save(installation/'plan.json',{'candidates':[{'route':'gem','source':'out/experiments/gem/candidate-fulltrain'}, {'route':'plist','source':'out/experiments/plist/candidate-fulltrain'}]})
    save(root/'experiments/gem/candidate-fulltrain/benchmark.json',{'train_config':{'max_delta_step':2},'min_malware_training_score':0})
    records=recovery.capture_research_installations([root],tmp_path/'history')
    assert [r['route'] for r in records]==['filetypes/gem']
    assert records[0]['benchmark']['min_malware_training_score']==0
    assert records[0]['benchmark']['train_config']['max_delta_step']==2
