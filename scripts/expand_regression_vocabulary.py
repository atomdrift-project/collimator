#!/usr/bin/env python3
"""Test a train-only route vocabulary against the installed feature layout.

Development data are exploratory and have been used by earlier recovery
studies. No locked-test row is fetched. A selected candidate still requires a
full refit and independent confirmation before promotion.
"""
import argparse
import hashlib
import json
import logging
from pathlib import Path
from types import SimpleNamespace

import azoth_regression_recovery as recovery
import azoth_portable_stability as study
from azoth_specialist_suite import _temporary_feature_env
from collimator import features
from collimator.corpus_snapshot import frozen_corpus
from tune_regressed_models import freeze


GRID = {
    'control': {},
    'cap2': {'max_delta_step': 2.},
    'small_regularized': {'max_delta_step': 2., 'num_leaves':31,
                          'max_depth':8, 'reg_lambda':5., 'min_child_samples':50},
}


def fitting_rows(rows):
    # Use only the fitting portion; exclude early stopping and every dev row.
    dev = [row for row in rows if row[2]]
    dev_halves = all(sum(r[1] == label and (r[3] < .5) == half for r in dev) >= 30
                     for label in (0, 1) for half in (False, True))
    return [(r[0], r[1]) for r in rows if not r[2] and r[3] >= .12
            and (dev_halves or r[3] < .75)]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--route',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source',type=Path,default=Path('out/models/azoth'))
    p.add_argument('--base-feature-env',type=Path,default=Path('out/experiments/azoth/runs/2026-10-31T07-43-33-experiment.json'))
    p.add_argument('--db',default='postgres://hopper@localhost:5432/hopper')
    p.add_argument('--max-id',type=int,default=6309383805)
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--threads',type=int,default=4)
    a=p.parse_args()
    if not a.route.startswith('filetypes/') or len(Path(a.route).parts)!=2:
        p.error('Expected a specialist route such as filetypes/macho')
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(name)s: %(message)s')
    a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
    grid_path=a.output/'grid.json';freeze(grid_path,GRID)
    args=SimpleNamespace(**vars(a), train_cap=10000000, grid_json=grid_path,
        current_layout_only=True, expanded_layout=a.output/'expanded-source',
        reuse=None, reuse_matrices_only=False, previous=None,
        previous_base_feature_env=None, ensemble_subsets=False, metric='recall')
    benchmark=recovery.benchmark_for(args,a.route)
    expanded=args.expanded_layout/a.route
    root=a.output/a.route
    freeze(a.output/'inventory.json',{a.route:[a.route.split('/')[1]]})
    if not (root/'prepared.json').exists():
        if (expanded/'feature_spec.json').exists():
            raise ValueError('Interrupted snapshot preparation; use a fresh output directory')
        expanded.mkdir(parents=True,exist_ok=True)
        env={**benchmark['feature_env'], 'COLLIMATOR_ALLOWED_FEATURES_FILE':'',
             'COLLIMATOR_BIGRAM_MIN_FREQ':'10', 'COLLIMATOR_BIGRAM_MAX':'5000'}
        freeze(expanded/'benchmark.json',{**benchmark,'feature_env':env})
        with frozen_corpus(a.db) as snapshot:
            rows=recovery.metadata(args,a.route,benchmark,1.)
            fit=fitting_rows(rows)
            logging.info('%s: discovering uncensored vocabulary from %d fitting rows',a.route,len(fit))
            with _temporary_feature_env(env):
                spec=features.build_vocab_from_db(a.db,fit,n_workers=a.workers,
                                                 checkpoint_dir=expanded/'vocabulary')
            spec.save(expanded/'feature_spec.json')
            freeze(expanded/'discovery.json',{'snapshot':snapshot,'fitting_rows':len(fit),
                'fitting_ids_sha256':hashlib.sha256(json.dumps(fit).encode()).hexdigest(),
                'features':spec.total_features,'max_id':a.max_id,'test_usage':'none',
                'scope':'Only fitting rows determine vocabulary; development is exploratory.'})
            # Preparation imports this same read-only snapshot in every worker.
            recovery.run_route(args,a.route,[a.route.split('/')[1]])
    else:
        recovery.run_route(args,a.route,[a.route.split('/')[1]])
    return 0


if __name__=='__main__':
    raise SystemExit(main())
