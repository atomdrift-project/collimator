#!/usr/bin/env python3
"""Compare frozen recovery candidates on identical locked-test report bytes.

This is a confirmation report, not an automatic installer or a tuning search.
One candidate per route is frozen before any test report is loaded.
"""
import argparse
import concurrent.futures as futures
import hashlib
import json
import logging
import multiprocessing
import os
from pathlib import Path

import numpy as np
from collimator import bundle, data, model
import azoth_regression_recovery as recovery
import azoth_portable_stability as study
from tune_regressed_models import freeze, fingerprint


def confirm(args, entry):
    route=entry['route'];root=args.output/route;root.mkdir(parents=True,exist_ok=True)
    paths={name:Path(entry[name]) for name in ('current','candidate')}
    benchmarks={name:json.loads((path/'benchmark.json').read_text()) for name,path in paths.items()}
    hashes={name:{str(p.relative_to(path)):fingerprint(p) for p in
                  [path/'feature_spec.json',path/'benchmark.json',*sorted((path/'models').glob('*.onnx'))]}
            for name,path in paths.items()}
    memberships = {path: fingerprint(Path(path)) for path in entry.get('exclude_membership_files', [])}
    freeze(root/'plan.json',{'entry':entry,'hashes':hashes,'max_id':args.max_id,
                            'prediction_contract':'runtime_f64_sum_f32_result_v1',
                            **({'excluded_membership_sha256': memberships} if memberships else {}),
                            'cohort':'all available locked-test rows; identical report bytes for both models',
                            'metric':'test recall at one FP is a ranking diagnostic, not a calibrated deployment threshold'})
    if (root/'complete.json').exists():return json.loads((root/'complete.json').read_text())
    predictions_path=root/'predictions.npz'
    if not predictions_path.exists():
        query=('SELECT id, label, canonical_sha256, sha256, file_type FROM samples WHERE '
               +data.LABELED_WHERE+' AND id <= %s')
        params=[args.max_id]
        if route!='general':
            query+=' AND file_type = ANY(%s)'
            params.append(entry.get('evaluation_file_types',benchmarks['current']['file_types']))
        query+=" AND right(lower(COALESCE(NULLIF(canonical_sha256,''),sha256)),2) < %s ORDER BY id"
        params.append(f'{data.TEST_BUCKET_MAX:02x}')
        cohort_path=root/'extraction-cohort.json'
        if cohort_path.exists():
            rows=json.loads(cohort_path.read_text())['rows']
        else:
            rows=[]
            with data._connect(args.db,repeatable_read=True) as conn:
                with conn.cursor(name='recovery_confirmation') as cur:
                    cur.itersize=10000
                    cur.execute(query,params)
                    for rid,label,canonical,sha,ft in cur:
                        if data.partition_of(canonical or sha)!='test':raise ValueError('Non-test identity')
                        rows.append((int(rid),int(label=='bad'),True,0.,data.route_filetype(ft),0))
            study.write_json(cohort_path,{'rows':rows,'max_id':args.max_id,
                'contract':'Frozen test identities and labels. Resumed batches retain their original paired features and report fingerprints.'})
        os.environ['COLLIMATOR_ONNX_THREADS']=str(args.threads)
        predictors={name:bundle.Ensemble(model.load_onnx_models(sorted((path/'models').glob('*.onnx'))))
                    for name,path in paths.items()}
        results={name:[] for name in paths};kept=[];digest=hashlib.sha256()
        with futures.ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn'),
                initializer=recovery.init_worker,initargs=(args.db,
                    {name:path/'feature_spec.json' for name,path in paths.items()},
                    {name:b['feature_env'] for name,b in benchmarks.items()})) as pool:
            batches=((str(root/'extraction-chunks'),i//256,rows[i:i+256]) for i in range(0,len(rows),256))
            for i,(actual,matrices,identity) in enumerate(pool.map(recovery.checkpointed_batch,batches,buffersize=args.workers*2)):
                if not actual:continue
                kept.extend(actual);digest.update(identity)
                for name,matrix in matrices.items():
                    results[name].append(predictors[name].predict_proba(matrix))
                if i%100==0:logging.info('%s: matched test %d/%d',route,len(kept),len(rows))
        if not kept:raise ValueError('No test rows available')
        np.savez(predictions_path,ids=[r[0] for r in kept],labels=[r[1] for r in kept],
                 filetypes=[r[4] for r in kept],**{name:np.concatenate(parts) for name,parts in results.items()})
        study.write_json(root/'cohort.json',{'requested_rows':len(rows),'kept_rows':len(kept),'paired_input_sha256':digest.hexdigest()})
    with np.load(predictions_path) as values:
        keep = np.ones(len(values['ids']), dtype=bool)
        for path, digest in memberships.items():
            if fingerprint(Path(path)) != digest:
                raise ValueError(f'Exclusion membership changed during confirmation: {path}')
            keep &= ~np.isin(values['ids'], np.load(path, mmap_mode='r'))
        excluded = values['ids'][~keep].tolist()
        profiles={name:recovery.filetype_profile(values['labels'][keep],values[name][keep],values['filetypes'][keep],entry['targets']) for name in paths}
    before,after=profiles['current'],profiles['candidate']
    failures=recovery.assessment_admission(before,after,entry.get('objective','recall'))
    result={'route':route,'profiles':profiles,'target_recall_1fp_delta':after['target_recall_1fp']-before['target_recall_1fp'] if after['target_malware'] else None,
            'target_ap_delta':after['target_ap']-before['target_ap'] if after['target_malware'] else None,
            'status':'held_back' if failures else 'test_confirmed','reasons':failures,
            'installed_model_changed':False,'deployment_policy_evaluation':'pending'}
    if memberships:
        result['partition_audit'] = {'membership_sha256': memberships, 'excluded_row_ids': excluded,
            'reason': 'Known frozen training/development membership excluded despite later partition reassignment.'}
    study.write_json(root/'complete.json',result)
    logging.info('%s: %s recall delta=%s AP delta=%s',route,result['status'],result['target_recall_1fp_delta'],result['target_ap_delta'])
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--output',type=Path,default=Path('out/experiments/regression-confirmation-20261031'))
    p.add_argument('--db',default='postgres://hopper@localhost:5432/hopper')
    p.add_argument('--max-id',type=int,default=6309383805)
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--threads',type=int,default=8)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(name)s: %(message)s')
    entries=json.loads(args.manifest.read_text());freeze(args.output/'candidates.json',entries)
    results=[]
    for entry in entries:
        try:results.append(confirm(args,entry))
        except Exception as exc:
            logging.exception('Confirmation failed: %s',entry['route'])
            results.append({'route':entry['route'],'status':'error','error':str(exc)})
        study.write_json(args.output/'status.json',results)
    return int(any(r['status']=='error' for r in results))


if __name__=='__main__':raise SystemExit(main())
