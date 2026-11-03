#!/usr/bin/env python3
"""Expanded Mach-O study with fresh canonical-group search/confirmation cohorts.

Use the entire available training partition for allocation. Groups seen in the
previous keyword study remain fitting-only; among previously unused groups,
60% fit, 20% search, 20% confirm by an independent label-blind hash. Original
corpus development and test partitions are excluded. Search choices are locked
before four-seed confirmation; no post-confirmation tuning is permitted.
"""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import keyword_macho_search as research
from collimator.bundle import atomic_write_json

ROOT = Path('out/experiments/macho-expanded-search')
PREVIOUS = Path('out/experiments/keyword-macho-search/cohort.json')


def fraction(group):
    return int(hashlib.sha256(('macho-expanded-v1:' + group.lower()).encode()).hexdigest()[:16],16) / 2**64


def select_rows(metadata, accepted, seen):
    train, evaluation = [], []
    rows = [dict(row_id=rid,label=label,group_id=group.lower(),score=score)
            for rid,label,partition,group,score in metadata if partition == 'train']
    rows, excluded = research.exclude_label_conflicts(rows)
    for row in rows:
        if row['group_id'] in seen or fraction(row['group_id']) >= .4:
            if row['score'] >= int(accepted['feature_env']['COLLIMATOR_MIN_SAMPLE_SCORE']) and (
                    not row['label'] or row['score'] >= accepted['min_malware_training_score']):
                train.append(row)
        else:
            evaluation.append(row)
    return train, evaluation, excluded


def prepare(args):
    previous=json.loads(PREVIOUS.read_text())
    seen={r['group_id'].lower() for rows in (previous['train'],previous['dev']) for r in rows}
    excluded=[]
    def selector(metadata, accepted):
        train, evaluation, removed=select_rows(metadata, accepted, seen)
        excluded.extend(removed)
        assert not seen & {r['group_id'] for r in evaluation}
        return train,evaluation
    args.route='macho'; args.exclude_label_conflicts=True; args.confirmation_groups=0
    research.prepare(args,row_selector=selector,search_selector=lambda group:fraction(group)<.2,
                     feature_overrides={'COLLIMATOR_BIGRAM_MIN_FREQ':'10'})
    path=args.output/'inputs.json'; manifest=json.loads(path.read_text())
    manifest.update(scope=__doc__,search_sample_percent=None,
                    previous_cohort_sha256=hashlib.sha256(PREVIOUS.read_bytes()).hexdigest(),
                    previous_groups_excluded_from_evaluation=len(seen),
                    runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    atomic_write_json(path,manifest)
    atomic_write_json(args.output/'excluded_conflicts.json',excluded)


def keyword(source,method='frequency',cap=1000,floor=5):
    return {source:dict(method=method,cap=cap,floor=floor)}


def variant(*,floor=1000,options=None,training=None):
    return dict(bigram_floor=floor,options=options or {},training=training or {})


class Study(research.Study):
    def __init__(self,root):
        super().__init__(root)
        self.complete_base,self.complete_spec=self.base,self.base_spec
        columns=[i for i,name in enumerate(self.base_spec.feature_names) if name.startswith('bigrams:')]
        counts=np.asarray(self.base[:self.n][self.y_train==1][:,columns].sum(axis=0)).ravel()
        self.support={self.base_spec.feature_names[i].split(':',1)[1]:int(count)
                      for i,count in zip(columns,counts,strict=True)}
        atomic_write_json(root/'ordinary_bigram_support.json',self.support)

    def set_base(self,cfg):
        columns=[i for i,n in enumerate(self.complete_spec.feature_names)
                 if not n.startswith(('bigrams:','unsigned_bigram:')) or
                 self.support.get(n.split(':',1)[1],0)>=cfg['bigram_floor']]
        names=[self.complete_spec.feature_names[i] for i in columns]
        self.base=self.complete_base[:,columns]
        self.base_spec=replace(self.complete_spec,feature_names=names,total_features=len(names),
            bigram_vocab=[w for w in self.complete_spec.bigram_vocab if self.support.get(w,0)>=cfg['bigram_floor']])

    def fit_variant(self,name,cfg,confirmation=False):
        directory=self.root/('confirmation' if confirmation else 'search')/name
        saved=directory/'result.json'
        if saved.exists():
            result=json.loads(saved.read_text())
            if result.get('variant') != cfg:
                raise ValueError('cached variant does not match requested parameters')
            return result
        self.set_base(cfg)
        result=super().fit(name,cfg['options'],trees=400 if confirmation else 220,
                           seeds=(43,44,45,46) if confirmation else (43,44),
                           confirmation=confirmation,overrides=cfg['training'])
        result['variant']=cfg
        result['ordinary_bigrams']=sum(n.startswith('bigrams:') for n in self.base_spec.feature_names)
        atomic_write_json(saved,result)
        if not confirmation:
            self.summary['variants'][name]=result
            atomic_write_json(self.summary_path,self.summary)
        return result

    def screen(self):
        if (self.root/'locked_finalists.json').exists():raise ValueError('search is locked')
        plans={'baseline':variant()}
        for floor in (10,25,50,100):plans[f'bigram-{floor}']=variant(floor=floor)
        for leaves,depth,child,lam in ((31,8,50,5),(15,6,50,10),(31,8,200,10),(63,10,100,5)):
            plans[f'tree-{leaves}-{child}-{lam}']=variant(training=dict(num_leaves=leaves,max_depth=depth,min_child_samples=child,reg_lambda=lam))
        atomic_write_json(self.root/'initial_plan.json',plans)
        for name,cfg in plans.items():self.fit_variant(name,cfg)

    @staticmethod
    def rank(result):
        m=result['search']
        return m['recall_1fp'],m['recall_0fp'],m['ap']

    def refine(self):
        if (self.root/'locked_finalists.json').exists():raise ValueError('search is locked')
        baseline=self.summary['variants']['baseline']
        bigram=max((r for n,r in self.summary['variants'].items() if n=='baseline' or n.startswith('bigram-')),key=self.rank)
        tree=max((r for n,r in self.summary['variants'].items() if n=='baseline' or n.startswith('tree-')),key=self.rank)
        combined=variant(floor=bigram['variant']['bigram_floor'],training=tree['variant']['training'])
        plans={'best-structure':combined}
        # Compare keywords with BOTH the unchanged and best structural baseline.
        choices={
            'descriptions':keyword('descword'), 'pooled':keyword('ruletextword'),
            'context':keyword('contextword'),
            'pooled-context':dict(keyword('ruletextword'),**keyword('contextword')),
            'pe-combination':dict(keyword('descword','balanced_mi',5000),**keyword('ruleword','balanced_mi'),**keyword('contextword')),
            'pooled-mi':keyword('ruletextword','balanced_mi'),
            'context-availability':keyword('context_availability',cap=1,floor=1),
        }
        for base_name,base_cfg in (('original',baseline['variant']),('structure',combined)):
            for label,options in choices.items():plans[f'{base_name}-{label}']=dict(base_cfg,options=options)
        atomic_write_json(self.root/'refinement_plan.json',plans)
        for name,cfg in plans.items():self.fit_variant(name,cfg)

    def lock(self):
        if (self.root/'locked_finalists.json').exists():raise ValueError('already locked')
        results=list(self.summary['variants'].values())
        if len(results)<30:raise ValueError('complete the search and tail plans first')
        base=self.summary['variants']['baseline']['search']
        eligible=[r for r in results if not r.get('diagnostic')
                  and r['search']['ap']>=base['ap']-.005 and r['search']['auc']>=base['auc']-.005]
        one=max(eligible,key=self.rank)
        zero=max(eligible,key=lambda r:(r['search']['recall_0fp'],r['search']['recall_1fp'],r['search']['ap']))
        structural=max((r for r in eligible if not r['options']),key=self.rank)
        names=list(dict.fromkeys(['baseline',one['name'],zero['name'],structural['name']]))
        # A search-selected keyword challenger lets the keyword hypothesis
        # face the fresh cohort even if structure alone leads the search.
        words=max((r for r in eligible if r['options']),key=self.rank,default=None)
        if words and words['name'] not in names:names.append(words['name'])
        locked=dict(names=names,variants={n:self.summary['variants'][n]['variant'] for n in names},
                    search_sha256=hashlib.sha256(self.summary_path.read_bytes()).hexdigest(),
                    runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    basis='Fresh search groups only; confirmation metrics unopened',seeds=[43,44,45,46],trees=400)
        atomic_write_json(self.root/'locked_finalists.json',locked)
        print('LOCKED '+json.dumps(locked),flush=True)

    def tail(self):
        """Probe class/hard-negative weights on paired base and keyword arms."""
        if (self.root/'locked_finalists.json').exists():raise ValueError('search is locked')
        path=self.root/'tail_plan.json'
        if path.exists():
            plans=json.loads(path.read_text())['variants']
        else:
            if len(self.summary['variants'])<24:raise ValueError('complete source refinement first')
            word=max((r for r in self.summary['variants'].values()
                      if r['options'] and not r.get('diagnostic')),key=self.rank)
            plans={}
            for label,base in (('original',self.summary['variants']['baseline']['variant']),('words',word['variant'])):
                for change,knobs in (('weight-half',dict(scale_pos_weight_mult=.5)),
                                     ('weight-quarter',dict(scale_pos_weight_mult=.25)),
                                     ('no-hard-negative',dict(hard_negative_fraction=0.,hard_negative_weight=1.))):
                    plans[f'tail-{label}-{change}']=dict(base,training=dict(base['training'],**knobs))
            atomic_write_json(path,dict(variants=plans,keyword_basis=word['name'],
                rationale='Search-only check of FP-tail sensitivity to class and hard-negative weights.',
                search_sha256=hashlib.sha256(self.summary_path.read_bytes()).hexdigest()))
        for name,cfg in plans.items():self.fit_variant(name,cfg)

    def confirm(self):
        locked=json.loads((self.root/'locked_finalists.json').read_text())
        if locked['search_sha256']!=hashlib.sha256(self.summary_path.read_bytes()).hexdigest():raise ValueError('search changed after lock')
        if locked['runner_sha256']!=hashlib.sha256(Path(__file__).read_bytes()).hexdigest():raise ValueError('runner changed after lock')
        results={}
        for name in locked['names']:
            results[name]=self.fit_variant(name,locked['variants'][name],confirmation=True)
            atomic_write_json(self.root/'confirmation.json',dict(protocol=locked,variants=results))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['prepare','screen','refine','tail','lock','confirm','verify'])
    p.add_argument('--db',default='postgres://hopper@localhost:5432/hopper')
    p.add_argument('--output',type=Path,default=ROOT)
    args=p.parse_args()
    if args.action=='prepare':prepare(args)
    elif args.action=='verify':
        from summarize_macho_keywords import verify, word_audit
        study,confirmation=verify(args.output,study_class=Study)
        word_audit(study,confirmation)
    else:getattr(Study(args.output),args.action)()


if __name__=='__main__':main()
