#!/usr/bin/env python3
"""Diagnose historical regressions with paired saved-generation predictions.

This does not select, train, promote, or install a candidate. Each pair sees
identical test reports and labels in a read-only snapshot. Historical source
models and their metadata are verified before inherited settings are merged.
"""
import argparse
import json
import logging
from pathlib import Path
import shutil
from types import SimpleNamespace

from collimator.bundle import model_files
from collimator.cache_identity import model_revision
from collimator.corpus_snapshot import frozen_corpus
import confirm_regression_recovery as confirmation
import azoth_portable_stability as study
from tune_regressed_models import fingerprint, freeze


def artifact_hashes(directory):
    paths=[directory/'feature_spec.json',*model_files(directory)]
    return {str(p.relative_to(directory)):fingerprint(p) for p in paths}


def general_benchmark(source, run_path):
    run=json.loads(run_path.read_text())
    keyed=run_path.parent/(run['experiment_key']+'.json')
    if json.loads(keyed.read_text())!=run:
        raise ValueError('General timestamped/keyed metadata differ')
    provenance=json.loads((run_path.parent/(run['experiment_key']+'_training_provenance.json')).read_text())
    if model_revision(source)!=provenance['model_revision'] or fingerprint(source/'feature_spec.json')!=provenance['spec_revision']:
        raise ValueError('General run metadata does not match model/spec bytes')
    return {'feature_env':run['feature_env'],'train_config':run['train_config'],
            'train_rows':run['train_rows'],'file_types':[],
            'min_malware_training_score':run['experiment_spec']['filters']['min_malware_training_score'],
            'source_experiment':str(run_path),'artifact_binding':provenance}


def freeze_generation(destination, source, benchmark):
    hashes=artifact_hashes(source)
    destination.mkdir(parents=True,exist_ok=True)
    freeze(destination/'source.json',{'directory':str(source.resolve()),'hashes':hashes})
    for relative,digest in hashes.items():
        target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():shutil.copy2(source/relative,target)
        if fingerprint(target)!=digest:raise ValueError('Frozen generation changed: '+str(target))
    freeze(destination/'benchmark.json',benchmark)


def differences(before,after):
    rows=[]
    for ft,old in before['by_filetype'].items():
        new=after['by_filetype'][ft]
        rows.append({'filetype':ft,'malware':old['malware'],'benign':old['rows']-old['malware'],
            'recall_1fp_before':old['at_fp']['1']['recall'],
            'recall_1fp_after':new['at_fp']['1']['recall'],
            'recall_1fp_delta':new['at_fp']['1']['recall']-old['at_fp']['1']['recall'],
            'ap_before':old['ap'],'ap_after':new['ap'],
            'ap_delta':new['ap']-old['ap'] if old['ap'] is not None else None})
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--routes',nargs='+')
    p.add_argument('--environment-corrections',type=Path,
                   help='Audited per-route/per-generation overrides for incomplete historical metadata')
    p.add_argument('--db',default='postgres://hopper@localhost:5432/hopper')
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--threads',type=int,default=4)
    p.add_argument('--max-id',type=int,default=6309383805)
    a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(name)s: %(message)s')
    base=Path('out/experiments')
    metadata=json.loads((base/'regression-diagnosis-20261031/verified-previous-metadata.json').read_text())
    general_runs={'previous':base/'azoth/runs/2026-10-26T17-19-22-experiment.json',
                  'nightly':base/'azoth/runs/2026-10-31T07-43-33-experiment.json'}
    if a.routes and 'general' in a.routes:metadata['general']=str(general_runs['previous'])
    inventory={}
    for name in ('regression-recovery-20261031','regression-recovery-ap-20261031'):
        inventory.update(json.loads((base/name/'inventory.json').read_text()))
    routes=a.routes or sorted(metadata,key=lambda r:(r.startswith('filegroups/'),r))
    if set(routes)-metadata.keys():p.error('Every route needs artifact-verified historical metadata')
    corrections=json.loads(a.environment_corrections.read_text()) if a.environment_corrections else {}
    plan={'routes':routes,'max_id':a.max_id,
        'purpose':'Historical generation diagnosis only; never a promotion decision',
        'limitation':'Old metadata may record route overrides only; explicit inherited nightly settings are merged.'}
    if corrections:plan['audited_environment_corrections']=corrections
    freeze(a.output/'plan.json',plan)
    inherited={
        'previous':json.loads((base/'azoth/runs/2026-10-26T17-19-22-experiment.json').read_text())['feature_env'],
        'nightly':json.loads((base/'azoth/runs/2026-10-31T07-43-33-experiment.json').read_text())['feature_env']}
    results=[]
    for route in routes:
        try:
            old=Path('/home/t/src/azoth')/route
            old_metadata=Path(metadata[route])
            if route!='general' and artifact_hashes(old)!=artifact_hashes(old_metadata.parent):
                raise ValueError('Historical metadata no longer matches model bytes: '+route)
            sources={'previous':old,'nightly':Path('out/models/azoth')/route}
            paths={}; filetypes=set()
            for name,source in sources.items():
                benchmark=(general_benchmark(source,general_runs[name]) if route=='general' else
                           json.loads((old_metadata if name=='previous' else source/'benchmark.json').read_text()))
                benchmark['feature_env']={**inherited[name],**benchmark['feature_env']}
                correction=corrections.get(route,{}).get(name)
                if correction:
                    if not correction.get('evidence'):
                        raise ValueError('Environment correction requires evidence: '+route)
                    benchmark['feature_env'].update(correction['feature_env'])
                    benchmark['environment_reconstruction']=correction
                filetypes.update(benchmark['file_types'])
                paths[name]=a.output/'generations'/name/route
                freeze_generation(paths[name],source,benchmark)
            entry={'route':route,'targets':inventory[route],
                   'evaluation_file_types':sorted(filetypes),
                   'current':str(paths['previous']),'candidate':str(paths['nightly'])}
            confirm_args=SimpleNamespace(**{**vars(a),'output':a.output/'paired'})
            with frozen_corpus(a.db):
                result=confirmation.confirm(confirm_args,entry)
            rows=differences(result['profiles']['current'],result['profiles']['candidate'])
            targeted=[r for r in rows if r['filetype'] in inventory[route]]
            result={'route':route,'status':'paired_diagnosis_complete','targets':inventory[route],
                'paired_cohort':str(a.output/'paired'/route/'cohort.json'),
                'filetypes':rows,'targeted_recall_declines':[r['filetype'] for r in targeted if r['malware'] and r['recall_1fp_delta']<0],
                'targeted_ap_declines':[r['filetype'] for r in targeted if r['ap_delta'] is not None and r['ap_delta']<-1e-12],
                'installed_model_changed':False}
            directory=a.output/route;directory.mkdir(parents=True,exist_ok=True)
            freeze(directory/'diagnosis.json',result)
            logging.info('%s: matched recall declines=%s; AP declines=%s',route,result['targeted_recall_declines'],result['targeted_ap_declines'])
        except Exception as exc:
            logging.exception('Generation diagnosis failed: %s',route)
            result={'route':route,'status':'error','error':str(exc)}
        results.append(result);study.write_json(a.output/'status.json',results)
    return int(any(r['status']=='error' for r in results))


if __name__=='__main__':raise SystemExit(main())
