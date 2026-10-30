#!/usr/bin/env python3
"""Compare threshold extraction throughput on one fixed canonical-hash sample.

Uses existing models, preserves ONNX batch boundaries, and requires bit-exact
scores and row identities across worker counts. Writes isolated diagnostics.
"""
import argparse
import cProfile
import hashlib
import json
import logging
import os
from pathlib import Path
import resource
import sys
import time


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',default='postgres://hopper@localhost:5432/hopper')
    parser.add_argument('--model',type=Path,default=Path('out/models/azoth/general'))
    parser.add_argument('--percent',default='1')
    parser.add_argument('--workers',type=int,nargs='+',default=[6,12,6])
    parser.add_argument('--batch-size',type=int,default=512)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if min(args.workers)<1 or args.batch_size<1:parser.error('workers and batch size must be positive')
    os.environ['COLLIMATOR_SAMPLE_PERCENT']=args.percent
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
    import numpy as np
    from collimator import bundle,data,features,cache_identity
    from collimator.corpus_snapshot import frozen_corpus
    data.sample_predicate(args.percent)
    args.output.mkdir(parents=True,exist_ok=False)
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    spec=features.FeatureSpec.load(args.model/'feature_spec.json')
    model=bundle.Ensemble.load_bundle(args.model)
    result={'sample_percent':args.percent,'model':str(args.model.resolve()),'model_revision':cache_identity.model_revision(args.model),'spec_sha256':hashlib.sha256((args.model/'feature_spec.json').read_bytes()).hexdigest(),'feature_code_revision':cache_identity.code_revision('features'),'batch_size':args.batch_size,'runs':[]}
    def save():
        tmp=args.output/'results.tmp';tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(args.output/'results.json')
    with frozen_corpus(args.db):
        result['database_revision']=cache_identity.database_revision(args.db)
        started=time.monotonic()
        rows=list(data.stream_labeled_metadata_full(args.db,compact=True,ordered=False))
        result.update(rows=len(rows),metadata_seconds=time.monotonic()-started)
        save()
        baseline=None
        for index,workers in enumerate(args.workers):
            start=time.monotonic();parts=[];totals={k:0.0 for k in ['fetch_sec','extract_sec','matrix_sec','predict_sec']}
            for meta,x,y,stats in features.extract_labeled_metadata_from_db_batches_unordered(args.db,rows,spec,n_workers=workers,batch_size=args.batch_size):
                if spec.standardized:x=features.standardize(x,spec)
                pstart=time.monotonic();p=model.predict_proba(x).astype(np.float32);totals['predict_sec']+=time.monotonic()-pstart
                parts.append((np.asarray([r[0] for r in meta],dtype=np.int64),y,p))
                for key in ['fetch_sec','extract_sec','matrix_sec']:totals[key]+=float(stats.get(key,0))
            elapsed=time.monotonic()-start
            ids=np.concatenate([p[0] for p in parts]);labels=np.concatenate([p[1] for p in parts]);scores=np.concatenate([p[2] for p in parts]);order=np.argsort(ids)
            arrays=(ids[order],labels[order],scores[order])
            if len(ids)!=len(rows) or len(np.unique(ids))!=len(rows):raise ValueError('extracted cohort changed')
            if baseline is None:baseline=arrays
            elif not all(np.array_equal(a,b) for a,b in zip(baseline,arrays,strict=True)):raise ValueError('worker configuration changed rows, labels or model scores')
            row={'workers':workers,'seconds':elapsed,'rows_per_second':len(ids)/elapsed,'stages':totals,'row_ids_sha256':hashlib.sha256(arrays[0].tobytes()).hexdigest(),'labels_sha256':hashlib.sha256(arrays[1].tobytes()).hexdigest(),'score_sha256':hashlib.sha256(arrays[2].tobytes()).hexdigest(),'exact_parity':True,'parent_peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024}
            result['runs'].append(row);save();print(json.dumps(row),flush=True)
        # Locate extraction hot paths separately; instrumentation isn't included
        # in the worker-count timing comparison.
        features._init_extract_worker(spec)
        profiler=cProfile.Profile();profiler.runcall(features._extract_labeled_metadata_db_batch_worker,(args.db,rows[:min(2048,len(rows))],spec));profiler.dump_stats(str(args.output/'extraction.prof'))
        result['status']='complete';save()
    return 0
if __name__=='__main__':raise SystemExit(main())
