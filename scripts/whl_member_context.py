#!/usr/bin/env python3
"""Capture WHL member context in an isolated, read-only research snapshot.

This tests an additional keyword source. It does not change the production
loader or claim inherited trait IDs are absent from compact parent reports.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import scipy.sparse as sp

import keyword_macho_search as research
from collimator import data, features
from collimator.bundle import atomic_write_json
from collimator.corpus_snapshot import frozen_corpus


def batch(task):
    db, rows, source, output, index = task
    manifest = json.loads((source / 'inputs.json').read_text())
    research.set_environment(manifest['feature_env'])
    spec = features.FeatureSpec.load(source / 'base_spec.json')
    fetched = data.fetch_cleave_results(db, [r['row_id'] for r in rows],
        evaluation_labels={r['row_id']:r['label'] for r in rows})
    references, reports = {}, {}
    for row in rows:
        rid = row['row_id']
        report = features._coerce_report(fetched[rid]['cleave_result'])
        reports[rid] = report
        for file in features.report_files(report):
            if file.get('depth',file.get('dp',0)) > 0 and file.get('sha') and not file.get('ctx'):
                references.setdefault(file['sha'],set()).add(rid)
    added = {r['row_id']:set() for r in rows}
    found = Counter()
    leaf_hash = hashlib.sha256()
    with data._connect(db) as conn:
        shas = sorted(references)
        for start in range(0,len(shas),256):
            records = conn.execute("SELECT sha256,COALESCE(cleave_result->'files',cleave_result->'fs')->0->'ctx' "
                                   "FROM samples WHERE sha256=ANY(%s) ORDER BY sha256",[shas[start:start+256]])
            for sha, ctx in records:
                leaf_hash.update(json.dumps([sha,ctx],sort_keys=True).encode())
                tokens = features._report_keywords([{'ctx':ctx or []}],['contextword'])['contextword']
                for rid in references[sha]:
                    added[rid].update(tokens)
                    found[rid] += 1
    records, items = [], []
    for row in rows:
        rid = row['row_id']; report = reports[rid]
        existing = features._report_keywords(features.report_files(report),['contextword'])['contextword']
        records.append(dict(row_id=rid,label=row['label'],group_id=row['group_id'],
            parent=sorted(existing),expanded=sorted(existing | added[rid]),members_found=found[rid],
            omitted_files=report.get('omitted_files',0),parent_revision=fetched[rid]['evaluation_digest'].hex()))
        items.append((fetched[rid],row['label']))
    rr,cc,vv,yy=features._extract_batch_worker((0,items,spec))
    assert yy == [r['label'] for r in rows]
    stem = output/f'batch-{index:05d}'
    sp.save_npz(str(stem)+'.npz',sp.csr_matrix((np.asarray(vv,dtype=np.float32),(rr,cc)),shape=(len(rows),spec.total_features)))
    with gzip.open(str(stem)+'.json.gz','wt') as f:
        json.dump(dict(rows=records,leaf_revision=leaf_hash.hexdigest()),f)
    return dict(rows=len(rows),with_parent_context=sum(bool(r['parent']) for r in records),
                with_expanded_context=sum(bool(r['expanded']) for r in records),
                added_context=sum(set(r['expanded'])!=set(r['parent']) for r in records),leaves=len(references))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=Path('out/experiments/weak-specialist-keywords-20261102/whl'))
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--limit',type=int,default=0)
    p.add_argument('--db',default='postgres://hopper@localhost:5432/hopper')
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    cohort=json.loads((args.source/'cohort.json').read_text()); rows=cohort['train']+cohort['dev']
    if args.limit:
        rows=[rows[i] for i in np.linspace(0,len(rows)-1,min(args.limit,len(rows)),dtype=int)]
    atomic_write_json(args.output/'plan.json',dict(source=str(args.source),rows=rows,scope=__doc__))
    started=time.perf_counter();total=Counter()
    with frozen_corpus(args.db) as snapshot:
        atomic_write_json(args.output/'snapshot.json',dict(snapshot=snapshot))
        tasks=[(args.db,rows[start:start+64],args.source,args.output,i) for i,start in enumerate(range(0,len(rows),64))]
        with features._feature_worker_pool(4) as pool:
            for result in features._bounded_iter(pool,batch,tasks,max_inflight=8):
                total.update(result)
                print(json.dumps(dict(total,seconds=round(time.perf_counter()-started,1))),flush=True)
    atomic_write_json(args.output/'complete.json',dict(total,seconds=time.perf_counter()-started))


if __name__=='__main__':
    main()
