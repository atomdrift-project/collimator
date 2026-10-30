#!/usr/bin/env python3
"""Ordered specialist research: training, corpus coverage, then richer features.

Select only on selection rows; expose assessment once all trials for a route
finish. Keeps deployed models untouched and writes resumable candidate bundles.
"""
from __future__ import annotations
import argparse
import gc
import inspect
import json
import logging
import os
from pathlib import Path
import shutil
from types import SimpleNamespace

import lightgbm as lgb
import numpy as np
import onnxruntime as ort
from scipy import sparse
from sklearn.metrics import average_precision_score

import azoth_portable_stability as study
from azoth_specialist_suite import _temporary_feature_env
from collimator import data, export, features

LOG = logging.getLogger('specialist_tuneup')
TRAINING = {
    'baseline': {}, 'cap2': {'max_delta_step': 2.},
    'cap5': {'max_delta_step': 5.}, 'cap10': {'max_delta_step': 10.},
    'no_hard_negatives': {'hard_negative_fraction': 0.},
    'gentle_hard_negatives': {'hard_negative_fraction': .05, 'hard_negative_weight': 3.},
    'weight025': {'scale_pos_weight_mult': .25},
    'cap5_weight025_no_hnm': {'max_delta_step': 5., 'scale_pos_weight_mult': .25, 'hard_negative_fraction': 0.},
}
VSIX_TRAINING = {
    'baseline': {}, 'weight025': {'scale_pos_weight_mult': .25},
    'weight050': {'scale_pos_weight_mult': .5}, 'cap5': {'max_delta_step': 5.},
    'finer_leaves': {'min_child_samples': 20, 'num_leaves': 64},
    'regularized': {'num_leaves': 32, 'reg_lambda': 5.},
    'gentle_hard_negatives': {'hard_negative_fraction': .05, 'hard_negative_weight': 3.},
}
FEATURES = {
    'cooccurrence': {'COLLIMATOR_BIGRAM_MIN_FREQ': '5', 'COLLIMATOR_TIERED_CRIT_TRIGRAMS': '1',
                    'COLLIMATOR_TIERED_TRIGRAM_MAX': '5000', 'COLLIMATOR_TIERED_TRIGRAM_MIN_FREQ': '3'},
    'metadata': {'COLLIMATOR_KV_VOCAB': '1', 'COLLIMATOR_KV_VOCAB_MAX': '5000',
                 'COLLIMATOR_KV_MIN_FREQ': '3', 'COLLIMATOR_KV_SHAPE_FEATURES': '1',
                 'COLLIMATOR_TEXT_METRICS_FULL': '1', 'COLLIMATOR_SEVERITY_FRACTION_FEATURES': '1'},
}

STABILITY_TRAINING = {
    **TRAINING,
    'cap2_weight025': {'max_delta_step': 2., 'scale_pos_weight_mult': .25},
    'cap5_weight010': {'max_delta_step': 5., 'scale_pos_weight_mult': .1},
    'cap5_finer_leaves': {'max_delta_step': 5., 'min_child_samples': 20, 'num_leaves': 32},
    'cap5_regularized': {'max_delta_step': 5., 'num_leaves': 32, 'reg_lambda': 5.},
}
WHL_TRAINING = {
    **TRAINING,
    'smaller_trees': {'num_leaves': 32, 'reg_lambda': 5.},
    'finer_leaves': {'min_child_samples': 20, 'num_leaves': 64},
    'full_sampling': {'subsample': 1., 'colsample_bytree': 1.},
    'budget200': {'n_estimators': 200},
}
SMALL_PACKAGE_TRAINING = {
    **STABILITY_TRAINING,
    'cap5_budget100': {'max_delta_step': 5., 'n_estimators': 100},
    'cap5_budget200': {'max_delta_step': 5., 'n_estimators': 200},
    'shallow_regularized': {'max_depth': 6, 'num_leaves': 16, 'reg_lambda': 10.},
}
LOW_FP_TRAINING = {
    'baseline': {},
    'weight025': {'scale_pos_weight_mult': .25},
    'cap5_weight025': {'max_delta_step': 5., 'scale_pos_weight_mult': .25},
    'cap2': {'max_delta_step': 2.},
    'no_hard_negatives': {'hard_negative_fraction': 0.},
    'gentle_hard_negatives': {'hard_negative_fraction': .05, 'hard_negative_weight': 3.},
    'hard_negatives': {'hard_negative_fraction': .2, 'hard_negative_weight': 5.},
    'shallow_regularized': {'num_leaves': 32, 'max_depth': 8, 'reg_lambda': 5.},
    'budget200': {'n_estimators': 200},
}

# Image specialists have very few retained positives. Test leaf support and
# sampling directly instead of spending trials on duplicate HNM settings.
IMAGE_TRAINING = {
    'baseline': {},
    'cap2': {'max_delta_step': 2.},
    'cap5_weight025': {'max_delta_step': 5., 'scale_pos_weight_mult': .25},
    'finer_leaves': {'min_child_samples': 10, 'min_child_weight': 1., 'num_leaves': 16},
    'regularized': {'max_depth': 6, 'num_leaves': 16, 'reg_lambda': 10.},
    'full_sampling': {'subsample': 1., 'colsample_bytree': 1.},
}


def training_grid(route):
    if route in {'gif', 'png'}:
        return IMAGE_TRAINING
    if route in {'npm', 'elf', 'c', 'batch'}:
        return LOW_FP_TRAINING
    if route == 'vsix':
        return VSIX_TRAINING
    if route in {'whl', 'crx'}:
        return WHL_TRAINING
    if route in {'json', 'markdown', 'plist', 'makefile'}:
        return STABILITY_TRAINING
    if route in {'github_actions', 'chrome_manifest', 'xpi', 'nupkg'}:
        return SMALL_PACKAGE_TRAINING
    return TRAINING


def load(root, name):
    x, y, buckets, filetypes = study.load_matrix(root, name)
    ids = np.load(root/name/'ids.npy', mmap_mode='r')
    return x, np.asarray(y), np.asarray(buckets), np.asarray(filetypes), np.asarray(ids)


def partition_evaluation(train_data, dev_data, mode, evaluation_training=None):
    xt, yt, bt, ft, ids = train_data
    xd, yd, bd, fd, dids = dev_data
    if mode == 'dev_halves':
        return (bt >= .12, bt < .12, xd, yd, bd < .5, fd)
    # Small dev cohorts stay wholly held out; tune on a canonical-grouped
    # training holdout. The original model's selection scores are in-sample
    # in this mode and never used to select or admit a candidate.
    # Keep selection identities fixed when the fit pool expands below the
    # malware cutoff. New positives in the reserved bucket stay out of fitting.
    xe, ye, be, fe, _ = evaluation_training if evaluation_training is not None else train_data
    selected = be >= .75
    return ((bt >= .12) & (bt < .75), bt < .12,
            sparse.vstack([xe[selected], xd], format='csr'),
            np.r_[ye[selected], yd], np.r_[np.ones(selected.sum(), dtype=bool), np.zeros(len(yd), dtype=bool)],
            np.r_[fe[selected], fd])


def align_cohort(cohort, reference):
    """Select the reference identities from a different feature layout."""
    order = np.argsort(cohort[4])
    positions = np.searchsorted(cohort[4][order], reference[4])
    if np.any(positions >= len(order)):
        raise ValueError('Evaluation identities missing from feature matrix')
    index = order[positions]
    if not np.array_equal(cohort[4][index], reference[4]) or not np.array_equal(cohort[1][index], reference[1]):
        raise ValueError('Evaluation identities or labels changed')
    return (cohort[0][index], *(a[index] for a in cohort[1:]))


def choose_mode(dev_data):
    _, y, b, _, _ = dev_data
    enough = all(min(int((y[m] == c).sum()) for c in (0, 1)) >= 30 for m in (b < .5, b >= .5))
    return 'dev_halves' if enough else 'train_selection_dev_assessment'


def stage_winner(root, allowed, objective='ap'):
    """Keep resume decisions independent of results from later stages."""
    comparisons=json.loads((root/'selection.json').read_text())['comparisons']
    return max((r for r in comparisons if r['variant'] in allowed),
               key=lambda r: study.rank(r['selection'], objective))


def extra_positives(args, root, benchmark):
    if (root/'extra-ready.json').exists():
        return
    rows, metadata = [], {}
    cutoff = benchmark['min_malware_training_score']
    if cutoff <= 0:
        study.write_json(root/'extra-ready.json', {'rows': 0})
        return
    with data._connect(args.db, repeatable_read=True) as conn:
        with conn.cursor(name='tuneup_extra_malware') as cursor:
            cursor.itersize = 10000
            cursor.execute('SELECT id, sha256, canonical_sha256, file_type FROM samples WHERE '
                           + data.LABELED_WHERE + " AND label='bad' AND COALESCE(score,0)<%s AND id<=%s AND file_type=ANY(%s) ORDER BY id",
                           (cutoff, args.max_id, benchmark['file_types']))
            for rid, sha, canonical, ft in cursor:
                key = canonical or sha
                if data.partition_of(key) != 'train':
                    continue
                rows.append((int(rid), 1)); metadata[int(rid)] = (study.split_bucket(key), ft)
    if rows:
        LOG.info('Extracting %d additional labeled malware training rows below score cutoff %s', len(rows), cutoff)
        identity = {}
        with _temporary_feature_env(benchmark['feature_env']):
            x, y, _, _ = features.extract_partitioned_from_db(args.db, rows, [], features.FeatureSpec.load(root/'original/feature_spec.json'), n_workers=args.workers, identity=identity)
        study.save_matrix(root, 'extra', x, y, identity['train_row_ids'], metadata)
        study.write_json(root/'extra-ready.json', {'rows': len(y), 'requested_rows': len(rows), 'evaluation_revision': identity['evaluation_revision']})
    else:
        study.write_json(root/'extra-ready.json', {'rows': 0})


def with_extra(root, training):
    if not json.loads((root/'extra-ready.json').read_text())['rows']:
        return training
    extra = load(root, 'extra')
    return (sparse.vstack([training[0], extra[0]], format='csr'),
            *(np.r_[training[i], extra[i]] for i in range(1,5)))


def feature_matrices(args, root, family, env, training, dev, mode=None):
    dest = root/'features'/family
    if not (dest/'ready.json').exists():
        dest.mkdir(parents=True, exist_ok=True)
        rows = sorted(zip(map(int, training[4]), map(int, training[1])))
        dev_rows = sorted(zip(map(int, dev[4]), map(int, dev[1])))
        metadata = {int(i): (float(b), str(ft)) for cohort in (training, dev) for i,b,ft in zip(cohort[4],cohort[2],cohort[3])}
        with _temporary_feature_env(env):
            vocab_rows = rows
            if mode is not None:
                fit_mask = training[2] >= .12
                if mode == 'train_selection_dev_assessment':
                    fit_mask &= training[2] < .75
                fit_ids = set(map(int, training[4][fit_mask]))
                vocab_rows = [row for row in rows if row[0] in fit_ids]
            spec = features.build_vocab_from_db(args.db, vocab_rows, n_workers=args.workers, checkpoint_dir=dest/'vocabulary')
            spec.save(dest/'feature_spec.json')
            identity = {}
            xt,yt,xd,yd = features.extract_partitioned_from_db(args.db, rows, dev_rows, spec, n_workers=args.workers, identity=identity)
        # Live report changes are recorded, but missing/reordered identities
        # must never silently change the comparison cohort.
        assert np.array_equal(identity['train_row_ids'], sorted(training[4])), 'training identities changed'
        assert np.array_equal(identity['test_row_ids'], sorted(dev[4])), 'dev identities changed'
        study.save_matrix(dest,'train',xt,yt,identity['train_row_ids'],metadata)
        study.save_matrix(dest,'dev',xd,yd,identity['test_row_ids'],metadata)
        study.write_json(dest/'ready.json', {'features':spec.total_features,'feature_env':env,'evaluation_revision':identity['evaluation_revision']})
    # Match the original row order, including extra positives appended later.
    result=[]
    for name, reference in [('train',training),('dev',dev)]:
        cohort=load(dest,name); order=np.argsort(cohort[4]); pos=np.searchsorted(cohort[4][order],reference[4]); index=order[pos]
        assert np.array_equal(cohort[4][index],reference[4])
        assert np.array_equal(cohort[1][index],reference[1]), 'labels changed during feature extraction'
        result.append((cohort[0][index],*(a[index] for a in cohort[1:])))
    return result


def fit(args, root, name, overrides, training, dev, mode, config, manifest, evaluation_training=None):
    fit_mask, stop_mask, xd, yd, selection, ft = partition_evaluation(training,dev,mode,evaluation_training)
    assert min(np.sum(training[1][fit_mask]==c) for c in (0,1)) >= 2
    # Small stop cohorts use the fixed tree budget; they do not kill the route.
    study.fit_variant(SimpleNamespace(output=root,threads=args.threads), name, overrides,
                      training[0][fit_mask],training[1][fit_mask],training[0][stop_mask],training[1][stop_mask],xd,yd,selection,config)
    for seed in study.SEEDS:
        path=root/'results'/f'{name}_seed{seed}'/'result.json'
        value=json.loads(path.read_text())
        if 'candidate_config' in value and value['candidate_config'] != manifest:
            raise ValueError(f'Resume changed candidate configuration: {path}')
        value['candidate_config']=manifest;study.write_json(path,value)
    return study.summarize(SimpleNamespace(output=root, selection_objective=getattr(args, 'selection_objective', 'ap')),yd,selection,ft)[0]


def validate_candidate(args, root, winner, training, dev, mode, evaluation_training=None):
    _,_,x,y,selection,_=partition_evaluation(training,dev,mode,evaluation_training)
    x=x[~selection];y=y[~selection]
    result=json.loads((root/'results'/f"{winner['variant']}_seed{winner['seeds'][0]}"/'result.json').read_text())
    manifest=result['candidate_config']; candidate=root/'candidate';(candidate/'models').mkdir(parents=True,exist_ok=True)
    shutil.copy2(root/manifest['feature_spec'],candidate/'feature_spec.json')
    native=[];actual=[]
    for seed in winner['seeds']:
        source=root/'results'/f"{winner['variant']}_seed{seed}"
        shutil.copy2(source/'model.txt',candidate/'models'/f'seed_{seed}.txt')
        booster=lgb.Booster(model_file=str(source/'model.txt'))
        assert export.export_lightgbm_onnx(booster,x.shape[1],candidate/'models'/f'seed_{seed}.onnx')
        options=ort.SessionOptions();options.intra_op_num_threads=args.threads;options.inter_op_num_threads=1
        session=ort.InferenceSession(str(candidate/'models'/f'seed_{seed}.onnx'),options,providers=['CPUExecutionProvider']);input_name=session.get_inputs()[0].name
        actual.append(np.concatenate([session.run(['probabilities'],{input_name:x[i:i+512].toarray().astype(np.float32)})[0][:,1] for i in range(0,len(y),512)]))
        native.append(np.load(source/'predictions.npz')['probability'][~selection])
    p=np.mean(actual,axis=0,dtype=np.float32);reference=np.mean(native,axis=0,dtype=np.float32)
    error=float(np.max(np.abs(p-reference)))
    report={'winner':winner,'candidate_config':manifest,'assessment_rows':len(y),'assessment_malware':int(y.sum()),'onnx_ap':float(average_precision_score(y,p)),
            'max_probability_difference':error,'parity_pass':error<=1e-4,'fixed_thresholds':{b:study.operating_point(y,p,v['threshold']) for b,v in winner['selection']['at_fp'].items()},'deployment_status':'research candidate; deployment gates pending'}
    study.write_json(candidate/'research.json',report)
    if error>1e-4:raise RuntimeError(f'ONNX parity failed: {error}')
    return report


def run_route(args, route):
    root=args.output/route;root.mkdir(parents=True,exist_ok=True)
    if (root/'complete.json').exists():return
    grid = training_grid(route)
    objective = getattr(args, 'selection_objective', 'ap')
    os.environ['COLLIMATOR_MATRIX_DISK_DIR']=str(root/'scratch')
    study.prepare(SimpleNamespace(source=args.source/'filetypes'/route,output=root,db=args.db,max_id=args.max_id,workers=args.workers,threads=args.threads,variants=grid))
    training=load(root,'train');dev=load(root,'dev');mode=choose_mode(dev)
    benchmark=json.loads((root/'original/benchmark.json').read_text());config=benchmark['train_config']
    manifest={'feature_spec':'original/feature_spec.json','feature_env':benchmark['feature_env'],'min_malware_training_score':benchmark['min_malware_training_score'],'training_pool':'original','training_overrides':{}}
    _,_,xd,yd,selection,ft=partition_evaluation(training,dev,mode)
    study.write_json(root/'trial-plan.json',{'training':grid,'feature_families':FEATURES,'data_expansion':'try all labeled training malware with the selected training configuration','combined_features':'try union if both feature families improve the selection objective over their input configuration','selection_objective':objective,'selection':'Recall at zero FP, then one FP, then AP' if objective=='low-fp' else 'AP then recall at five selection false positives; seed subsets chosen on selection only','evaluation_mode':mode})
    study.write_json(root/'cohorts.json',{'mode':mode,'selection_rows':int(selection.sum()),'selection_malware':int(yd[selection].sum()),'assessment_rows':int((~selection).sum()),'assessment_malware':int(yd[~selection].sum())})
    if getattr(args, 'allow_new_specialists', False) and not list((root/'original/models').glob('seed_*.txt')):
        LOG.info('%s: new specialist; baseline fit is the control (no saved specialist)', route)
    else:
        study.score_original(SimpleNamespace(output=root,threads=args.threads),xd,yd,selection)
    for name,overrides in grid.items():
        winner=fit(args,root,name,overrides,training,dev,mode,config,{**manifest,'training_overrides':overrides})
    winner=stage_winner(root,set(grid),objective)
    selected=json.loads((root/'results'/f"{winner['variant']}_seed{winner['seeds'][0]}"/'result.json').read_text())['candidate_config']
    settings=selected['training_overrides'];input_score=winner['selection']['ap']
    extra_positives(args,root,benchmark)
    expanded=with_extra(root,training)
    if len(expanded[1])>len(training[1]):
        expanded_manifest={**manifest,'min_malware_training_score':0,'training_pool':'all_labeled','training_overrides':settings}
        winner=fit(args,root,'all_labeled',settings,expanded,dev,mode,config,expanded_manifest,evaluation_training=training)
    winner=stage_winner(root,set(grid)|{'all_labeled'},objective)
    selected=json.loads((root/'results'/f"{winner['variant']}_seed{winner['seeds'][0]}"/'result.json').read_text())['candidate_config']
    selected_training=expanded if selected['training_pool']=='all_labeled' else training
    settings=selected['training_overrides'];input_score=study.rank(winner['selection'],objective);family_gains={}
    for family,changes in FEATURES.items():
        env={**selected['feature_env'],**changes}
        family_train,family_dev=feature_matrices(args,root,family,env,selected_training,dev,mode=mode)
        candidate_manifest={**selected,'feature_spec':f'features/{family}/feature_spec.json','feature_env':env,'training_overrides':settings}
        winner=fit(args,root,family,settings,family_train,family_dev,mode,config,candidate_manifest,evaluation_training=align_cohort(family_train,training))
        selection_report=json.loads((root/'selection.json').read_text())
        family_gains[family]=max(study.rank(r['selection'],objective) for r in selection_report['comparisons'] if r['variant']==family)>input_score
        del family_train,family_dev;gc.collect()
    if all(family_gains.values()):
        env={**selected['feature_env'],**FEATURES['cooccurrence'],**FEATURES['metadata']}
        family_train,family_dev=feature_matrices(args,root,'combined',env,selected_training,dev,mode=mode)
        winner=fit(args,root,'combined',settings,family_train,family_dev,mode,config,{**selected,'feature_spec':'features/combined/feature_spec.json','feature_env':env,'training_overrides':settings},evaluation_training=align_cohort(family_train,training))
        del family_train,family_dev;gc.collect()
    # Only now inspect assessment. All family matrices have identical evaluation identities.
    winner,comparisons,predictions=study.summarize(SimpleNamespace(output=root,selection_objective=objective),yd,selection,ft)
    study.assessment(SimpleNamespace(output=root),yd,selection,ft,winner,comparisons,predictions)
    selected=json.loads((root/'results'/f"{winner['variant']}_seed{winner['seeds'][0]}"/'result.json').read_text())['candidate_config']
    chosen_training=expanded if selected['training_pool']=='all_labeled' else training
    if selected['feature_spec'].startswith('features/'):
        family=selected['feature_spec'].split('/')[1]
        chosen_training,chosen_dev=feature_matrices(args,root,family,selected['feature_env'],chosen_training,dev)
    else:chosen_dev=dev
    validation=validate_candidate(args,root,winner,chosen_training,chosen_dev,mode,evaluation_training=align_cohort(chosen_training,training))
    study.write_json(root/'complete.json',{'route':f'filetypes/{route}','winner':winner,'validation':validation})
    LOG.info('COMPLETE %s: %s',route,validation)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--routes',nargs='+',default=['rust','xml','java','vsix','gem'])
    p.add_argument('--source',type=Path,default=Path('out/models/azoth'))
    p.add_argument('--output',type=Path,default=Path('out/experiments/specialist-tuneup-20261027'))
    p.add_argument('--db',default='postgres://hopper@localhost:5432/hopper')
    p.add_argument('--max-id',type=int,default=6309383805)
    p.add_argument('--workers',type=int,default=4);p.add_argument('--threads',type=int,default=4)
    p.add_argument('--selection-objective', choices=['ap','low-fp'], default='ap')
    p.add_argument('--allow-new-specialists', action='store_true')
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    status=[]
    for route in args.routes:
        LOG.info('START ROUTE %s',route)
        try:run_route(args,route);status.append({'route':route,'status':'complete'})
        except Exception as exc:
            LOG.exception('FAILED %s',route);status.append({'route':route,'status':'failed','error':str(exc)})
        study.write_json(args.output/'status.json',status);gc.collect()
    if any(r['status']=='failed' for r in status):raise SystemExit(1)

if __name__=='__main__':main()
