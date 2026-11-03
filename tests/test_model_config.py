import json
import hashlib
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


def test_relative_allowlist_pin_survives_checkout_relocation(tmp_path, monkeypatch):
    checkout = tmp_path / 'relocated'
    configs = checkout / 'model-configs'
    relative = 'src/collimator/data/allowed.json'
    allowlist = checkout / relative
    allowlist.parent.mkdir(parents=True)
    allowlist.write_text('["present:test"]')
    d = document()
    d['feature_env']['COLLIMATOR_ALLOWED_FEATURES_FILE'] = relative
    model_config.save(configs, d)
    monkeypatch.setattr(model_config, 'DEFAULT_ROOT', configs)
    monkeypatch.chdir(tmp_path)
    loaded = model_config.load(d['route'], configs)
    pin = loaded['feature_env']['COLLIMATOR_ALLOWED_FEATURES_FILE']
    assert Path(pin).read_text() == '["present:test"]'
    assert json.loads(model_config.config_path(configs, d['route']).read_text())['feature_env'][
        'COLLIMATOR_ALLOWED_FEATURES_FILE'] == relative


def test_explicit_absolute_allowlist_pin_is_preserved(tmp_path):
    d = document()
    d['feature_env']['COLLIMATOR_ALLOWED_FEATURES_FILE'] = '/custom/missing.json'
    model_config.save(tmp_path, d)
    assert model_config.load(d['route'], tmp_path)['feature_env'][
        'COLLIMATOR_ALLOWED_FEATURES_FILE'] == '/custom/missing.json'


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


@pytest.mark.parametrize('seeds', [[], [42,42], [True], [-1], '42'])
def test_reject_invalid_ensemble_membership(seeds):
    d=document();d['ensemble_seeds']=seeds
    with pytest.raises(ValueError,match='ensemble_seeds'):
        model_config.as_run(d)


def test_pinned_ensemble_survives_configuration_roundtrip(tmp_path):
    d=document();d['ensemble_seeds']=[42,44]
    model_config.save(tmp_path,d)
    assert model_config.load(d['route'],tmp_path)['ensemble_seeds']==[42,44]
    assert model_config.as_run(d)['ensemble_seeds']==[42,44]


def test_parse_ensemble_preserves_nonconsecutive_seeds():
    assert model_config.parse_ensemble_seeds('42, 44')==[42,44]
    assert model_config.parse_ensemble_seeds('') is None
    with pytest.raises(ValueError):model_config.parse_ensemble_seeds('42,42')


def test_recovered_research_identity_includes_actual_membership(tmp_path):
    history=tmp_path/'history';history.mkdir()
    runs=tmp_path/'runs';configs=tmp_path/'configs';registry=tmp_path/'registry.json'
    (history/'accepted-baseline-snapshots.json').write_text('[]')
    record={'route':'filetypes/batch','installed_at':'2026-10-28','receipt':'receipt',
            'source':'source','model_revision':'revision',
            'benchmark':{'train_config':{},'feature_env':{},'min_malware_training_score':0,
                         'seed_health':{'accepted_seeds':[43]}}}
    path=history/'installed-research-snapshots.json'
    path.write_text(json.dumps([record]));merger.merge(history,registry,runs,configs)
    first=json.loads(registry.read_text())['routes']['filetypes/batch']['full_train_key']
    record['benchmark']['seed_health']['accepted_seeds']=[43,44]
    path.write_text(json.dumps([record]));merger.merge(history,registry,runs,configs)
    keys={p.stem for p in runs.glob('*.json')}
    assert first in keys and len(keys)==2
    assert model_config.load('filetypes/batch',configs)['ensemble_seeds']==[43]


def test_feature_layout_pin_resolves_and_detects_replaced_contents(tmp_path,monkeypatch):
    from collimator.features import FeatureSpec
    configs=tmp_path/'model-configs';configs.mkdir()
    spec=tmp_path/'saved-layout.json'
    FeatureSpec(total_features=1,feature_names=['agg:n_findings']).save(spec)
    d=document();d['feature_env'].update(COLLIMATOR_FEATURE_SPEC_FILE='saved-layout.json',
        COLLIMATOR_FEATURE_SPEC_SHA256=hashlib.sha256(spec.read_bytes()).hexdigest())
    model_config.save(configs,d)
    monkeypatch.setattr(model_config,'DEFAULT_ROOT',configs)
    loaded=model_config.load(d['route'],configs)
    assert model_config.pinned_feature_spec(loaded['feature_env']).feature_names==['agg:n_findings']
    spec.write_text(spec.read_text()+'\n')
    with pytest.raises(ValueError,match='specification changed'):
        model_config.load(d['route'],configs)
