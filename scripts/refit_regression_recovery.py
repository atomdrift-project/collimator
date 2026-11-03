#!/usr/bin/env python3
"""Refit frozen, assessment-admitted recovery choices on their full train pool."""
import argparse
from dataclasses import fields
import hashlib
import json
import logging
import os
from pathlib import Path
import shutil
from types import SimpleNamespace

import lightgbm as lgb
import numpy as np

import azoth_portable_stability as study
import azoth_regression_recovery as recovery
from azoth_specialist_suite import _temporary_feature_env
from azoth_tuneup_fulltrain import refit
from tune_regressed_models import freeze, fingerprint
from collimator.train import TrainConfig
from collimator import bundle, cache_identity, model, features, export
from evaluate_recovery_policy_matches import effective_spec


def refit_retention_metrics(labels, selected, refitted, filetypes, targets):
    """Check whether refitting preserved the selected model's dev ranking.

    AP and aggregate gains cannot compensate for losing recall at one FP in
    an affected filetype. This review does not fit a deployment threshold.
    """
    profiles = {
        name: recovery.filetype_profile(labels, scores, filetypes, targets)
        for name, scores in (("selected", selected), ("refitted", refitted))
    }
    declines, unassessed = [], []
    for ft in targets:
        before = profiles['selected']['by_filetype'].get(ft)
        after = profiles['refitted']['by_filetype'].get(ft)
        if (before is None or after is None or not before['malware']
                or before['rows'] == before['malware']):
            unassessed.append(ft)
            continue
        delta = after['at_fp']['1']['tp'] - before['at_fp']['1']['tp']
        if delta < 0:
            declines.append({'filetype': ft, 'tp_delta_at_one_fp': delta})
    return {'status': ('regressed' if declines else
                       'unavailable' if unassessed else 'preserved'),
            'declines': declines, 'unassessed_filetypes': unassessed, 'profiles': profiles,
            'scope': 'Same canonical development inputs; ranking retention only, '
                     'not independent confirmation or deployment calibration.'}


def selected_artifact_for_review(study_root, refit_root, plan, winner):
    """Export a frozen choice when operating-point admission skipped export.

    A research choice can be held on ranking metrics but admitted for a further
    refit by its fixed-threshold assessment. Its exact fitted weights still need
    the same retention review. This creates diagnostic artifacts, not a new fit.
    """
    selected = study_root / 'candidate'
    if bundle.has_model(selected):
        return selected
    layout = winner['layout']
    environment = (plan['benchmark'] if layout == 'current'
                   else plan[layout + '_benchmark'])['feature_env']
    originals = {}
    for seed in winner['seeds']:
        path = (study_root / layout / 'models' / f'seed_{seed}.txt'
                if winner['variant'] == 'saved' else
                study_root / 'fits' / layout / 'results'
                / f"{winner['variant']}_seed{seed}" / 'model.txt')
        if not path.is_file():
            return None
        originals[seed] = path
    if not originals:
        return None
    selected = refit_root / 'selected-for-retention'
    selected.mkdir(parents=True, exist_ok=True)
    identity = {'choice': winner,
                'plan_sha256': fingerprint(study_root / 'plan.json'),
                'source_spec_sha256': fingerprint(study_root / layout / 'feature_spec.json'),
                'source_models': {str(seed): fingerprint(path)
                                  for seed, path in originals.items()}}
    freeze(selected / 'inputs.json', identity)
    with _temporary_feature_env(environment):
        spec = features.FeatureSpec.load(study_root / layout / 'feature_spec.json')
        spec.bind_metric_contract()
    spec_path = selected / 'feature_spec.json'
    if not spec_path.exists():
        spec.save(spec_path)
    else:
        # Do not overwrite a previously materialized feature contract.
        with _temporary_feature_env(environment):
            expected = effective_spec(study_root / layout, environment)
        if effective_spec(selected) != expected:
            raise ValueError('Selected retention feature contract changed')
    (selected / 'models').mkdir(exist_ok=True)
    for seed, path in originals.items():
        onnx = selected / 'models' / f'seed_{seed}.onnx'
        if not onnx.exists() and not export.export_lightgbm_onnx(
                lgb.Booster(model_file=str(path)), spec.total_features, onnx):
            raise ValueError('Cannot export frozen selected weights for retention review')
    return selected


def review_refit_retention(study_root, refit_root, threads):
    """Compare exact selected/refitted ONNX artifacts before test confirmation."""
    if not (study_root / 'frozen-winner.json').is_file():
        return {'status': 'unavailable', 'reason': 'No frozen selected artifact'}
    plan = json.loads((study_root / 'plan.json').read_text())
    winner = json.loads((study_root / 'frozen-winner.json').read_text())['winner']
    selected = selected_artifact_for_review(study_root, refit_root, plan, winner)
    if selected is None:
        return {'status': 'unavailable', 'reason': 'Frozen selected weights are missing'}
    refitted = refit_root / 'candidate-fulltrain'
    layout = winner['layout']
    environment = (plan['benchmark'] if layout == 'current'
                   else plan[layout + '_benchmark'])['feature_env']
    if effective_spec(selected, environment) != effective_spec(refitted):
        raise ValueError('Refit feature semantics differ from the selected model')
    dev_root = study_root / layout / 'dev'
    identity = {
        'selected_model_revision': cache_identity.model_revision(selected),
        'refitted_model_revision': cache_identity.model_revision(refitted),
        'selected_spec_sha256': fingerprint(selected / 'feature_spec.json'),
        'refitted_spec_sha256': fingerprint(refitted / 'feature_spec.json'),
        'selection_sha256': fingerprint(study_root / 'frozen-winner.json'),
        'plan_sha256': fingerprint(study_root / 'plan.json'),
        'dev_files_sha256': {p.name: fingerprint(p) for p in sorted(dev_root.iterdir())
                             if p.is_file()},
    }
    receipt_path = refit_root / 'refit-retention.json'
    if receipt_path.exists():
        prior = json.loads(receipt_path.read_text())
        if prior.get('identity') != identity:
            raise ValueError('Refit retention inputs changed; use a new review directory')
        # Reuse the exact recorded inference, including float32 tie behavior.
        # Recomputing with another ONNX thread count can perturb cutoffs by ULPs.
        return prior
    matrix, labels, _, filetypes = study.load_matrix(study_root / layout, 'dev')
    os.environ['COLLIMATOR_ONNX_THREADS'] = str(threads)
    probabilities = {}
    for name, directory in [('selected', selected), ('refitted', refitted)]:
        ensemble = bundle.Ensemble(model.load_onnx_models(bundle.model_files(directory)))
        probabilities[name] = ensemble.predict_proba(matrix)
    report = refit_retention_metrics(labels, probabilities['selected'],
                                    probabilities['refitted'], filetypes, plan['targets'])
    report.update(identity=identity, prediction_threads=threads)
    freeze(receipt_path, report)
    return report


def operating_refit_basis(source, report_path, level):
    """Allow further research on a frozen winner with fixed-threshold gains.

    This is not installation approval or an independent confirmation. FP changes
    are retained in the receipt; a one-FP ranking loss is not an install budget.
    """
    report = json.loads(report_path.read_text())
    frozen_path = source / 'frozen-winner.json'
    frozen = json.loads(frozen_path.read_text())
    if (report['frozen_winner_sha256'] != hashlib.sha256(frozen_path.read_bytes()).hexdigest()
            or Path(report['study']).resolve() != source.resolve()
            or report['reports']['winner']['key'] != frozen['winner']['key']):
        raise ValueError('Operating assessment does not bind this frozen research winner')
    rows = {}
    for name in ('reference', 'winner'):
        if report['reports'][name]['status'] != 'evaluated':
            raise ValueError('Operating assessment lacks calibration support')
        rows[name] = next(r for r in report['reports'][name]['levels'] if r['level'] == level)
    before, after = rows['reference'], rows['winner']
    for population in ('selection', 'assessment'):
        for count in ('malware', 'benign'):
            if before[population][count] != after[population][count]:
                raise ValueError('Operating assessment populations differ')
        if after[population]['tp'] <= before[population]['tp']:
            raise ValueError('Operating refit requires detection gains in selection and assessment')
    if before['filetypes'].keys() != after['filetypes'].keys():
        raise ValueError('Operating assessment filetype coverage differs')
    for filetype, old in before['filetypes'].items():
        new = after['filetypes'][filetype]
        if old['malware'] != new['malware'] or old['benign'] != new['benign'] or new['tp'] < old['tp']:
            raise ValueError(f'Operating assessment loses coverage or detections: {filetype}')
    return {'report': str(report_path.resolve()),
            'report_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest(),
            'level': level, 'reference': before, 'winner': after,
            'status': 'Further full-training research only; deployment confirmation pending'}


def preserve_saved_subset(source, root, chosen, benchmark, selected, threads):
    """An existing full-training ensemble subset must retain its exact weights."""
    if chosen['layout']!='current':
        raise ValueError('Only the current saved model is eligible for subset reuse')
    dest=root/'candidate-fulltrain'
    if (dest/'complete.json').exists():return
    (dest/'models').mkdir(parents=True,exist_ok=True)
    shutil.copy2(source/'current/feature_spec.json',dest/'feature_spec.json')
    for seed in chosen['seeds']:
        for suffix in ('txt','onnx'):
            name=f'seed_{seed}.{suffix}'
            shutil.copy2(source/'current/models'/name,dest/'models'/name)
    x,y,_,_=study.load_matrix(source/'current','dev')
    native=study.ensemble_probability([study.predict(lgb.Booster(model_file=str(dest/'models'/f'seed_{seed}.txt')),x,threads)[2]
                    for seed in chosen['seeds']])
    os.environ['COLLIMATOR_ONNX_THREADS']=str(threads)
    onnx=study.ensemble_probability([m.predict(x) for m in model.load_onnx_models(sorted((dest/'models').glob('*.onnx')))])
    error=float(np.max(np.abs(native-onnx)))
    if error>1e-4:raise ValueError('Saved-subset ONNX parity failed')
    benchmark={**benchmark,'output_dir':str(dest),'model_path':str(bundle.primary_model_file(dest)),
               'spec_path':str(dest/'feature_spec.json'),'n_seed_models':len(chosen['seeds']),
               'training_partitions':['train'],'score_space':'raw',
               'seed_health':{'accepted_seeds':chosen['seeds']},
               'model_reuse':{'source':str((source/'current').resolve()),'reason':'Exact selected full-training members; no retraining'}}
    study.write_json(dest/'benchmark.json',benchmark)
    cache_identity.write_training_provenance(dest)
    study.write_json(dest/'complete.json',{'research_choice':chosen,'candidate_config':selected,
        'max_onnx_difference':error,'dev_metrics':study.metrics(y,onnx),
        'deployment_status':'Exact saved members retained; confirmation pending',
        'model_reuse':benchmark['model_reuse']})


def prepare(args, route):
    source=args.study/route
    result=json.loads((source/'complete.json').read_text())
    operating_basis = None
    if result['status']!='improved_research_candidate':
        if not getattr(args, 'operating_assessment', None):
            return None
        operating_basis = operating_refit_basis(source,
            args.operating_assessment / route / 'comparison.json', args.operating_level)
    root=args.output/route;root.mkdir(parents=True,exist_ok=True)
    chosen=json.loads((source/'frozen-winner.json').read_text())['winner']
    plan=json.loads((source/'plan.json').read_text())
    variant=chosen['variant'];layout=chosen['layout']
    if variant=='historical_score_floor':
        raise ValueError('A score-floor trial requires an explicit filtered full-training recipe')
    overrides=(plan['previous_benchmark']['train_config'] if variant in ('previous_recipe','previous_recipe_restored_cutoff')
               else {} if variant in ('saved','control_restored_cutoff') else plan['grid'][variant])
    unknown=set(overrides)-{field.name for field in fields(TrainConfig)}
    if unknown:
        raise ValueError(f'Refusing to silently drop research training settings: {sorted(unknown)}')
    env=(plan[f'{layout}_benchmark']['feature_env'] if layout in ('previous','expanded')
         else plan['benchmark']['feature_env'])
    selected={'feature_spec':'original/feature_spec.json','training_pool':'original',
              'training_overrides':overrides,'feature_env':env,
              'min_malware_training_score':chosen.get('min_malware_training_score',plan['benchmark']['min_malware_training_score'])}
    freeze(root/'refit-plan.json',{'study':str(source.resolve()),'choice':chosen,
                                 'configuration':selected,'max_id':plan['max_id'],
                                 **({'operating_refit_basis': operating_basis} if operating_basis else {})})
    original=root/'original'
    if not original.exists():
        if (source/'candidate').exists():
            shutil.copytree(source/'candidate',original)
        else:
            original.mkdir()
            shutil.copy2(source/layout/'feature_spec.json',original/'feature_spec.json')
    benchmark={**plan['benchmark'],'feature_env':env,'seed_health':{'accepted_seeds':chosen['seeds']},
               'min_malware_training_score':selected['min_malware_training_score']}
    freeze(original/'benchmark.json',benchmark)
    (root/'candidate').mkdir(exist_ok=True)
    freeze(root/'candidate/research.json',{'winner':{'variant':variant,'seeds':chosen['seeds']},
                                          'candidate_config':selected})
    if variant=='saved':
        preserve_saved_subset(source,root,chosen,benchmark,selected,args.threads)
        return root,env
    if json.loads((source/'prepared.json').read_text())['train_fraction']==1:
        for name in ('train','dev'):
            if not (root/name).exists():
                if name=='train' and selected['min_malware_training_score']!=plan['benchmark']['min_malware_training_score']:
                    x,y,bucket,filetype=study.load_matrix(source/layout,name)
                    ids=np.load(source/layout/name/'ids.npy')
                    keep=(y==0)|(np.load(source/'train-scores.npy')>=selected['min_malware_training_score'])
                    metadata={int(rid):(float(b),str(ft)) for rid,b,ft in zip(ids[keep],bucket[keep],filetype[keep])}
                    study.save_matrix(root,name,x[keep],y[keep],ids[keep],metadata)
                else:
                    (root/name).symlink_to((source/layout/name).resolve(),target_is_directory=True)
        freeze(root/'prepared.json',{'reused_full_train_matrices':str(source/layout),
                                    'test_usage':'none'})
    else:
        os.environ['COLLIMATOR_MATRIX_DISK_DIR']=str(root/'scratch')
        study.prepare(SimpleNamespace(source=original,output=root,db=args.db,
            max_id=plan['max_id'],workers=args.workers,threads=args.threads))
    return root,env


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--study',type=Path,required=True)
    p.add_argument('--output',type=Path,default=Path('out/experiments/regression-refits-20261031'))
    p.add_argument('--routes',nargs='+',required=True)
    p.add_argument('--db',default='postgres://hopper@localhost:5432/hopper')
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--threads',type=int,default=8)
    p.add_argument('--operating-assessment', type=Path,
                   help='Frozen fixed-threshold diagnostic receipts permitting further research refits')
    p.add_argument('--operating-level', type=int, default=25)
    args=p.parse_args();args.output=args.output.resolve();args.output.mkdir(parents=True,exist_ok=True)
    os.environ['COLLIMATOR_MEM_RESERVE_GB']='2'
    os.environ['COLLIMATOR_FIT_RESOURCE_DIR']=str(args.output/'fit-resources')
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    results=[]
    for route in args.routes:
        try:
            prepared=prepare(args,route)
            if prepared is None:
                results.append({'route':route,'status':'not_admitted'});continue
            root,env=prepared
            with _temporary_feature_env(env):refit(root,args.threads)
            retention = review_refit_retention(args.study / route, root, args.threads)
            status = ('held_back_after_refit' if retention['status'] == 'regressed'
                      else 'refitted')
            if status == 'held_back_after_refit':
                logging.warning('%s: refit lost selected development recall: %s',
                                route, retention['declines'])
            results.append({'route':route,'status':status,
                            'refit_retention':retention['status'],
                            'path':str(root/'candidate-fulltrain')})
        except Exception as exc:
            logging.exception('Refit failed: %s',route)
            results.append({'route':route,'status':'error','error':str(exc)})
        study.write_json(args.output/('status-'+args.study.name+'.json'),results)
    return int(any(r['status']=='error' for r in results))


if __name__=='__main__':raise SystemExit(main())
