#!/usr/bin/env python3
"""Matched WHL keyword comparison using captured parent and member context."""
from collections import Counter
import gzip
import json
from pathlib import Path

import numpy as np
import scipy.sparse as sp

import whl_recall_search as capacity
from collimator.bundle import atomic_write_json


class Study(capacity.Study):
    def __init__(self, source, capture, output):
        super().__init__(source,output)
        assert (capture/'complete.json').exists(), 'capture must finish before fitting'
        records=[]
        for p in sorted(capture.glob('batch-*.json.gz')):
            with gzip.open(p,'rt') as f:
                records.extend(json.load(f)['rows'])
        original=np.load(source/'inputs/rows.npz')
        assert [r['row_id'] for r in records] == original['row_ids'].tolist()
        np.testing.assert_array_equal([r['label'] for r in records],self.y)
        self.base=sp.vstack([sp.load_npz(p) for p in sorted(capture.glob('batch-*.npz'))],format='csr')
        self.layouts={'base':self.base}
        for kind in ('parent','expanded'):
            counts=Counter(word for r,fit in zip(records,self.fit) if fit for word in r[kind])
            words=sorted(sorted((w for w,c in counts.items() if c>=2),key=lambda w:(-counts[w],w))[:5000])
            lookup={w:i for i,w in enumerate(words)};rr=[];cc=[]
            for i,r in enumerate(records):
                cols=[lookup[w] for w in r[kind] if w in lookup]
                rr.extend([i]*len(cols));cc.extend(cols)
            matrix=sp.csr_matrix((np.ones(len(rr),dtype=np.float32),(rr,cc)),shape=(len(records),len(words)))
            self.layouts[kind]=sp.hstack([self.base,matrix],format='csr')
            atomic_write_json(output/(kind+'-vocabulary.json'),words)
        flags=np.asarray([bool(r['expanded']) for r in records],dtype=np.float32)
        self.layouts['availability']=sp.hstack([self.base,sp.csr_matrix(flags[:,None])],format='csr')
        atomic_write_json(output/'context-protocol.json',dict(capture=str(capture),
            snapshot=json.loads((capture/'snapshot.json').read_text()),
            note='Exploratory follow-up on previously viewed dev and reserved groups; no historical test rows read. '
                 'Every arm uses the same freshly captured parent feature matrix and labels. '
                 'Keyword vocabulary uses fitting rows only. Availability is a diagnostic control.'))


def main():
    root=Path('out/experiments/whl-80-20261102')
    output=root/'context-search'
    study=Study(Path('out/experiments/weak-specialist-keywords-20261102/whl'),root/'context-full',output)
    settings=capacity.plans()
    plans={f'{layout}-{shape}':dict(settings['base-'+shape],layout=layout)
           for layout in ('base','parent','expanded','availability') for shape in ('current','fine')}
    atomic_write_json(output/'context-plan.json',plans)
    if not (output/'context-locked.json').exists():
        results=[study.run(name,plan,43) for name,plan in plans.items()]
        baseline=results[0]['search']
        eligible=[r for r in results if r['search']['ap']>=baseline['ap']-.01 and r['plan']['layout']!='availability']
        best=max(eligible,key=lambda r:(r['search']['recall_1fp'],r['search']['recall_0fp'],r['search']['ap']))
        names=list(dict.fromkeys(['base-current','parent-current','expanded-current',best['name']]))
        atomic_write_json(output/'context-locked.json',dict(names=names,results=results))
    locked=json.loads((output/'context-locked.json').read_text());results={}
    for name in locked['names']:
        for seed in (43,44,45,46):study.run(name,plans[name],seed)
        p=np.mean([np.load(output/'fits'/name/str(seed)/'predictions.npz')['scores'].astype(np.float64)
                   for seed in (43,44,45,46)],axis=0).astype(np.float32)
        results[name]={label:capacity.metrics(study.y[mask],p[mask]) for label,mask in
                       [('reserved_training_groups',study.reserved),('dev_confirmation',study.dev_confirm)]}
        atomic_write_json(output/'context-confirmation.json',results)
        print('CONFIRM',name,json.dumps(results[name]),flush=True)


if __name__=='__main__':
    main()
