"""Regression recovery must preserve route coverage and assessment isolation."""
import sys
import os
from pathlib import Path

import numpy as np
import pytest
import json
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import azoth_regression_recovery as recovery
import refit_regression_recovery as refits


def test_inventory_includes_constituents_and_routing_only_losses(tmp_path):
    (tmp_path/'filetypes/dockerfile/models').mkdir(parents=True)
    comparison={'models':[{'route':'general','ft':'rust','delta':-.1},
                           {'route':'filetypes/go','ft':'go','delta':-.01},
                           {'route':'filetypes/elf','ft':'elf','delta':.1}],
                'routed':[{'ft':'dockerfile','delta':-1}, {'ft':'wasm','delta':-1}]}
    assert recovery.inventory(comparison,tmp_path)=={
        'general':['rust'],'filetypes/go':['go'],'filetypes/dockerfile':['dockerfile']}


def test_target_objective_uses_each_filetype_threshold():
    y=np.array([0,0,1,1,0,0,1,1])
    ft=np.array(['a']*4+['b']*4)
    p=np.array([.8,.7,.9,.6,.2,.1,.3,.25])
    profile=recovery.filetype_profile(y,p,ft,['a','b'])
    assert profile['target_recall_1fp']==.75


def test_research_ensemble_does_not_create_a_probability_one_tie():
    low = np.nextafter(np.float32(1), np.float32(0))
    members = np.array([[1, 1, .5], [low, 1, .5], [low, 1, .5]], dtype=np.float32)
    labels = np.array([0, 1, 0])
    runtime = recovery.study.ensemble_probability(members)
    # Independent equivalent of Scan's serial f64 sum, cast after division.
    expected = np.array([sum(map(float, column)) / 3 for column in members.T], dtype=np.float32)
    np.testing.assert_array_equal(runtime, expected)
    assert runtime[0] < runtime[1]
    assert recovery.study.metrics(labels, runtime)['at_fp']['0']['tp'] == 1
    old = np.mean(members, axis=0, dtype=np.float32)
    assert old[0] == old[1]
    assert recovery.study.metrics(labels, old)['at_fp']['0']['tp'] == 0


def test_assessment_cannot_hide_one_filetype_loss_in_an_aggregate_gain():
    before={'target_malware':10,'target_recall_1fp':.4,'ap':.95,
            'by_filetype':{'a':{'malware':9,'at_fp':{'1':{'tp':3}}},
                           'b':{'malware':1,'at_fp':{'1':{'tp':1}}}}}
    after={'target_malware':10,'target_recall_1fp':.7,'ap':.96,
           'by_filetype':{'a':{'malware':9,'at_fp':{'1':{'tp':7}}},
                          'b':{'malware':1,'at_fp':{'1':{'tp':0}}}}}
    assert recovery.assessment_admission(before,after)==['b: assessment recall at one FP declined']


def test_refit_retention_rejects_constituent_loss_despite_aggregate_gain():
    labels = np.array([0, 0, 1, 1, 1] * 2)
    filetypes = np.array(['a'] * 5 + ['b'] * 5)
    selected = np.array([.9, .5, .8, .4, .3, .9, .1, .8, .7, .6])
    refitted = np.array([.9, .1, .8, .7, .6, .9, .5, .8, .7, .4])
    result = refits.refit_retention_metrics(
        labels, selected, refitted, filetypes, ['a', 'b'])
    assert result['status'] == 'regressed'
    assert result['declines'] == [{'filetype': 'b', 'tp_delta_at_one_fp': -1}]
    assert (result['profiles']['refitted']['target_recall_1fp']
            > result['profiles']['selected']['target_recall_1fp'])


def test_refit_retention_accepts_equal_scores_without_requiring_another_gain():
    labels = np.array([0, 0, 1, 1])
    probabilities = np.array([.8, .2, .9, .7])
    result = refits.refit_retention_metrics(
        labels, probabilities, probabilities.copy(), np.array(['a'] * 4), ['a'])
    assert result['status'] == 'preserved'
    assert result['declines'] == []


def test_refit_retention_does_not_claim_review_without_selected_artifact(tmp_path):
    result = refits.review_refit_retention(tmp_path / 'study', tmp_path / 'refit', 1)
    assert result['status'] == 'unavailable'


def test_refit_retention_requires_both_classes_in_every_target():
    labels = np.array([0, 0, 1, 1])
    scores = np.array([.1, .2, .8, .9])
    result = refits.refit_retention_metrics(
        labels, scores, scores, np.array(['benign_only'] * 2 + ['malware_only'] * 2),
        ['benign_only', 'malware_only', 'missing'])
    assert result['status'] == 'unavailable'
    assert result['unassessed_filetypes'] == ['benign_only', 'malware_only', 'missing']


def test_retention_materializes_frozen_operating_choice_and_rejects_changed_weights(tmp_path):
    import lightgbm as lgb
    from collimator import features, bundle

    source, output = tmp_path / 'study', tmp_path / 'review'
    (source / 'current').mkdir(parents=True)
    features.FeatureSpec(total_features=1, feature_names=['x']).save(
        source / 'current/feature_spec.json')
    plan = {'benchmark': {'feature_env': {}}}
    (source / 'plan.json').write_text(json.dumps(plan))
    fit = source / 'fits/current/results/control_seed42'
    fit.mkdir(parents=True)
    x = np.arange(8, dtype=np.float32).reshape(-1, 1)
    booster = lgb.train({'objective': 'binary', 'num_leaves': 2,
                         'min_data_in_leaf': 1, 'min_data_in_bin': 1,
                         'num_threads': 1, 'verbosity': -1},
                        lgb.Dataset(x, label=np.array([0] * 4 + [1] * 4)),
                        num_boost_round=3)
    weights = fit / 'model.txt'
    booster.save_model(str(weights))
    winner = {'layout': 'current', 'variant': 'control', 'seeds': [42]}
    artifact = refits.selected_artifact_for_review(source, output, plan, winner)
    assert bundle.has_model(artifact)
    assert not (source / 'candidate').exists()  # No false research admission.
    assert refits.selected_artifact_for_review(source, output, plan, winner) == artifact
    weights.write_text(weights.read_text() + '\n')
    with pytest.raises(ValueError, match='Resume configuration changed'):
        refits.selected_artifact_for_review(source, output, plan, winner)


def test_selection_guard_prefers_smaller_gain_without_constituent_loss():
    def record(name, recall, a, b):
        return {'key':name,'selection':{'target_recall_1fp':recall,'ap':.99,
            'by_filetype':{'a':{'malware':10,'at_fp':{'1':{'tp':a}}},
                           'b':{'malware':10,'at_fp':{'1':{'tp':b}}}}}}
    baseline=record('baseline',.5,5,5)
    bad=record('tradeoff',.8,8,4)
    good=record('balanced',.7,7,5)
    assert recovery.choose([baseline,bad,good],baseline,protect_filetypes=True)==good


def test_sampling_keeps_full_small_routes_and_bounds_large_ones():
    assert recovery.sampling_fraction('filetypes/rust',{'train_rows':200000},300000)==1
    assert recovery.sampling_fraction('general',{'train_rows':15000000},300000)==.02
    with pytest.raises(ValueError, match='positive'):
        recovery.sampling_fraction('general',{'train_rows':15000000},0)


def test_historical_malware_cutoff_preserves_benign_and_filters_stopping():
    labels=np.array([0,1,1,0,1,1])
    scores=np.array([0,2,5,0,3,4])
    fit=np.array([1,1,1,0,0,0],dtype=bool)
    stop=~fit
    a,b=recovery.malware_cutoff_masks(labels,scores,fit,stop,4)
    np.testing.assert_array_equal(a,[1,0,1,0,0,0])
    np.testing.assert_array_equal(b,[0,0,0,1,0,1])


def test_full_refit_filters_the_selected_malware_cutoff(tmp_path):
    from scipy import sparse
    source=tmp_path/'study/filetypes/apk_android';source.mkdir(parents=True)
    chosen={'variant':'previous_recipe_restored_cutoff','layout':'previous','seeds':[42],
            'min_malware_training_score':4}
    baseline={'min_malware_training_score':0,'feature_env':{},'train_config':{}}
    plan={'benchmark':baseline,'previous_benchmark':dict(baseline,min_malware_training_score=4),
          'grid':{},'max_id':100}
    for name,value in [('complete',{'status':'improved_research_candidate'}),
                       ('frozen-winner',{'winner':chosen}),('plan',plan),('prepared',{'train_fraction':1})]:
        (source/(name+'.json')).write_text(json.dumps(value))
    (source/'candidate').mkdir();(source/'candidate/feature_spec.json').write_text('{}')
    (source/'previous').mkdir()
    metadata={i:(.2,'apk_android') for i in range(4)}
    for part in ('train','dev'):
        recovery.study.save_matrix(source/'previous',part,sparse.eye(4,format='csr'),
            np.array([0,1,1,0]),np.arange(4),metadata)
    np.save(source/'train-scores.npy',[0,2,4,0])
    args=SimpleNamespace(study=tmp_path/'study',output=tmp_path/'refits')
    root,_=refits.prepare(args,'filetypes/apk_android')
    np.testing.assert_array_equal(np.load(root/'train/ids.npy'),[0,2,3])
    np.testing.assert_array_equal(np.load(root/'dev/ids.npy'),[0,1,2,3])
    assert json.loads((root/'original/benchmark.json').read_text())['min_malware_training_score']==4


def test_custom_grid_requires_control_and_safe_variant_directories(tmp_path):
    path=tmp_path/'grid.json'
    for grid in ({'cap2':{}}, {'control':{}, '../outside':{}}, {'control':{'max_depth':3}},
                 {'control':{}, 'unknown_knob':{'boost_from_average':False}}):
        path.write_text(json.dumps(grid))
        with pytest.raises(ValueError):
            recovery.search_grid(path)
    grid={'control':{}, 'gentle_hnm':{'hard_negative_fraction':.05}}
    path.write_text(json.dumps(grid))
    assert recovery.search_grid(path)==grid


def test_full_refit_rejects_unreplayable_research_settings(tmp_path):
    source=tmp_path/'study/filetypes/cab';source.mkdir(parents=True)
    (source/'complete.json').write_text(json.dumps({'status':'improved_research_candidate'}))
    (source/'frozen-winner.json').write_text(json.dumps({'winner':{
        'variant':'unsupported','layout':'current','seeds':[42,43,44]}}))
    (source/'plan.json').write_text(json.dumps({'grid':{'unsupported':{'boost_from_average':False}}}))
    args=SimpleNamespace(study=tmp_path/'study',output=tmp_path/'refit')
    with pytest.raises(ValueError,match='silently drop'):
        refits.prepare(args,'filetypes/cab')
    assert not (args.output/'filetypes/cab/candidate-fulltrain').exists()


def test_seed_subset_study_includes_exact_previous_single_seed():
    members=recovery.memberships([42,43,44],True)
    assert len(members)==7
    assert (43,) in members and (42,44) in members and (42,43,44) in members
    assert () not in members


def test_paired_extraction_fetches_once_for_both_layouts(monkeypatch):
    class Spec:
        total_features=1
    recovery._SPECS={'current':Spec(),'previous':Spec()}
    calls=[]
    def fetch(db,ids,**kwargs):
        calls.append(ids)
        return {1:{'cleave_result':{},'evaluation_digest':b'same bytes'}}
    monkeypatch.setattr(recovery.data,'fetch_cleave_results',fetch)
    monkeypatch.setattr(recovery.features,'_coerce_report',lambda x:x)
    monkeypatch.setattr(recovery.features,'_extract_partitioned_batch_worker',
                        lambda args:([0],[0],[7.],[1],[],[],[],[]))
    kept,matrices,digest=recovery.paired_batch([(1,1,True,.3,'rust',4)])
    assert calls==[[1]]
    np.testing.assert_array_equal(matrices['current'].toarray(),matrices['previous'].toarray())
    assert digest==b'same bytes'


def test_paired_layouts_restore_their_own_extraction_environment(monkeypatch):
    class Spec:
        total_features=1
    monkeypatch.setattr(recovery,'_SPECS',{'current':Spec(),'previous':Spec()})
    monkeypatch.setattr(recovery,'_ENVS',{
        'current':{'COLLIMATOR_TEXT_METRICS_FULL':'1'},
        'previous':{'COLLIMATOR_TEXT_METRICS_FULL':'0'}})
    monkeypatch.setattr(recovery.data,'fetch_cleave_results',lambda *a,**kw:{
        1:{'cleave_result':{},'evaluation_digest':b'x'}})
    monkeypatch.setattr(recovery.features,'_coerce_report',lambda x:x)
    def extract(args):
        value=float(os.environ['COLLIMATOR_TEXT_METRICS_FULL'])
        return [0],[0],[value],[1],[],[],[],[]
    monkeypatch.setattr(recovery.features,'_extract_partitioned_batch_worker',extract)
    _,matrices,_=recovery.paired_batch([(1,1,True,.3,'rust',4)])
    assert matrices['current'][0,0]==1
    assert matrices['previous'][0,0]==0


def test_identical_layout_and_environment_extract_once(monkeypatch):
    class Spec:
        total_features=1
    monkeypatch.setattr(recovery,'_SPECS',{'current':Spec(),'candidate':Spec()})
    monkeypatch.setattr(recovery,'_LAYOUT_IDENTITIES',{'current':('same','{}'),'candidate':('same','{}')})
    monkeypatch.setattr(recovery,'_ENVS',{})
    monkeypatch.setattr(recovery.data,'fetch_cleave_results',lambda *a,**kw:{
        1:{'cleave_result':{},'evaluation_digest':b'x'}})
    monkeypatch.setattr(recovery.features,'_coerce_report',lambda x:x)
    calls=[]
    def extract(args):
        calls.append(args)
        return [0],[0],[7.],[1],[],[],[],[]
    monkeypatch.setattr(recovery.features,'_extract_partitioned_batch_worker',extract)
    _,matrices,_=recovery.paired_batch([(1,1,True,.3,'rust',4)])
    assert len(calls)==1
    assert matrices['current'] is matrices['candidate']


def test_extraction_checkpoint_reuses_exact_rows_and_checks_integrity(tmp_path,monkeypatch):
    from scipy import sparse
    monkeypatch.setattr(recovery,'_SPECS',{'current':SimpleNamespace(total_features=2)})
    calls=[]
    def extract(rows):
        calls.append(rows)
        return rows,{'current':sparse.csr_matrix([[1.,2.]])},b'original-report'
    monkeypatch.setattr(recovery,'paired_batch',extract)
    rows=[(1,1,True,.3,'macho',4)]
    first=recovery.checkpointed_batch((str(tmp_path),0,rows))
    second=recovery.checkpointed_batch((str(tmp_path),0,rows))
    assert len(calls)==1
    assert second[2]==first[2]
    np.testing.assert_array_equal(second[1]['current'].toarray(),first[1]['current'].toarray())
    with pytest.raises(ValueError,match='inputs changed'):
        recovery.checkpointed_batch((str(tmp_path),0,[(1,0,True,.3,'macho',4)]))
    (tmp_path/'00000000/current.npz').write_bytes(b'interrupted write')
    with pytest.raises(ValueError,match='matrix changed'):
        recovery.checkpointed_batch((str(tmp_path),0,rows))
