#!/usr/bin/env python3
"""Plist follow-up: coverage-aware grouped CV, then frozen dev confirmation."""
from __future__ import annotations

import argparse
import gc
import json
import logging
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import numpy as np

import azoth_portable_stability as study
import azoth_specialist_tuneup as tune
from azoth_package_tuneup import freeze_plan, ensemble_predictions

LOG = logging.getLogger('plist_tuneup')
BASE = {'max_delta_step': 5., 'scale_pos_weight_mult': .1,
        'early_stopping_rounds': 0, 'hard_negative_fraction': 0.}
GRID = {
    'cutoff4_control': {},
    'all_labels_control': {},
    'cap2': {'max_delta_step': 2.},
    'weight025': {'scale_pos_weight_mult': .25},
    'cap2_weight025': {'max_delta_step': 2., 'scale_pos_weight_mult': .25},
    'weight1': {'scale_pos_weight_mult': 1.},
    'smaller_leaves': {'min_child_samples': 10, 'min_child_weight': 1., 'num_leaves': 32},
    'shallow_regularized': {'max_depth': 6, 'min_child_samples': 20,
                          'min_child_weight': 1., 'num_leaves': 16, 'reg_lambda': 5.},
    'full_sampling': {'subsample': 1., 'colsample_bytree': 1.},
    'extra_trees': {'extra_trees': True},
    'budget100': {'n_estimators': 100},
    'budget200': {'n_estimators': 200},
}


def subset(cohort, mask):
    return (cohort[0][mask], *(a[mask] for a in cohort[1:]))


def folds(training, original_ids):
    assignments = np.minimum((training[2] * 3).astype(int), 2)
    eligible = np.isin(training[4], original_ids)
    result = []
    for fold in range(3):
        validation = assignments == fold
        fitting = ~validation
        for mask in (validation, fitting, fitting & eligible):
            if min(int(np.sum(training[1][mask] == c)) for c in (0, 1)) < 2:
                raise ValueError('Insufficient class support in a canonical training fold')
        result.append((fitting, validation, eligible))
    return result


def run_cv(args, root, name, overrides, training, original, config, env=None):
    completed = root/f'{name}-cv.json'
    if completed.exists():
        return json.loads(completed.read_text())
    probability = np.empty(len(training[1]), dtype=np.float32)
    fold_metrics = []
    for fold, (fitting, validation, eligible) in enumerate(folds(training, original[4])):
        if name == 'cutoff4_control':
            fitting &= eligible
        work = root/f'fold-{fold}'
        work.mkdir(exist_ok=True)
        train_cohort, val_cohort = subset(training, fitting), subset(training, validation)
        if env is not None:
            train_cohort, val_cohort = tune.feature_matrices(
                args, work, name, env, train_cohort, val_cohort)
        study.fit_variant(SimpleNamespace(output=work, threads=args.threads), name, overrides,
            train_cohort[0], train_cohort[1], val_cohort[0], val_cohort[1],
            val_cohort[0], val_cohort[1], np.ones(len(val_cohort[1]), dtype=bool), config)
        probability[validation] = ensemble_predictions(work, name)
        fold_metrics.append(study.metrics(training[1][validation], probability[validation]))
        gc.collect()
    record = {'variant': name, 'seeds': list(study.SEEDS), 'overrides': overrides,
              'feature_env': env, 'fold_metrics': fold_metrics,
              'mean_fold_ap': float(np.mean([m['ap'] for m in fold_metrics])),
              'oof': study.metrics(training[1], probability)}
    np.save(root/f'{name}-oof.npy', probability)
    study.write_json(completed, record)
    LOG.info('%s: mean fold AP %.4f, pooled AP %.4f', name, record['mean_fold_ap'], record['oof']['ap'])
    return record


def rank(row):
    return row['mean_fold_ap'], row['oof']['ap']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('out/experiments/next-model-tuneup-20261027/plist'))
    parser.add_argument('--output', type=Path, default=Path('out/experiments/plist-round2-20261027'))
    parser.add_argument('--db', default='postgres://hopper@localhost:5432/hopper')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--gate', action='store_true')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    root = args.output/'plist'
    root.mkdir(parents=True, exist_ok=True)
    for name in ('original', 'train', 'dev', 'extra', 'extra-ready.json'):
        if not (root/name).exists():
            (root/name).symlink_to((args.source/name).resolve())
    original = tune.load(root, 'train')
    training = tune.with_extra(root, original)
    benchmark = json.loads((root/'original/benchmark.json').read_text())
    config = benchmark['train_config']
    freeze_plan(root, {'grid': GRID, 'base': BASE, 'seeds': list(study.SEEDS),
        'selection': 'mean AP over three canonical-grouped training folds with all labeled malware in every validation pool; no early stopping or seed selection',
        'training_rows': len(training[1]), 'training_malware': int(training[1].sum()),
        'original_training_malware': int(original[1].sum()),
        'features': ['metadata', 'metadata_cooccurrence'],
        'caveat': 'Original vocabulary was built on the training partition; original-layout CV is conditional on that vocabulary. New feature vocabularies use each fold fitting rows only. Dev is reused confirmation; locked test is reserved for deployment gates.'})
    comparisons = []
    for name, changes in GRID.items():
        comparisons.append(run_cv(args, root, name, {**BASE, **changes}, training, original, config))
        study.write_json(root/'selection.json', {'comparisons': comparisons})
    # Richer features use the strongest all-label configuration chosen in CV.
    numeric = max((r for r in comparisons if r['variant'] != 'cutoff4_control'), key=rank)
    for name, changes in [('metadata', tune.FEATURES['metadata']),
                          ('metadata_cooccurrence', {**tune.FEATURES['metadata'], **tune.FEATURES['cooccurrence']})]:
        env = {**benchmark['feature_env'], **changes}
        comparisons.append(run_cv(args, root, name, numeric['overrides'], training, original, config, env))
        study.write_json(root/'selection.json', {'comparisons': comparisons})
    winner = max(comparisons, key=rank)
    study.write_json(root/'winner.json', winner)
    manifest = {'feature_spec': 'original/feature_spec.json', 'feature_env': benchmark['feature_env'],
        'min_malware_training_score': 4 if winner['variant']=='cutoff4_control' else 0,
        'training_pool': 'original' if winner['variant']=='cutoff4_control' else 'all_labeled',
        'training_overrides': winner['overrides']}
    # Only after freezing the winner load dev for confirmation and full refit.
    dev = tune.load(root, 'dev')
    if winner['feature_env'] is not None:
        family = winner['variant']
        tune.feature_matrices(args, root, family, winner['feature_env'], training, dev)
        manifest.update(feature_spec=f'features/{family}/feature_spec.json', feature_env=winner['feature_env'])
    (root/'candidate').mkdir(exist_ok=True)
    study.write_json(root/'candidate/research.json', {'winner': winner, 'candidate_config': manifest})
    subprocess.run([sys.executable, 'scripts/azoth_tuneup_fulltrain.py', '--root', str(args.output),
                    '--routes', 'plist', '--threads', str(args.threads)], check=True)
    with np.load(root/'candidate-fulltrain/dev_predictions.npz') as d:
        actual = np.asarray(d['probability'])
        np.testing.assert_array_equal(d['ids'], dev[4])
    old = np.mean([np.load(args.source/'results'/f'original_seed{s}'/'predictions.npz')['probability'][-len(dev[1]):]
                   for s in study.original_seeds(root)], axis=0, dtype=np.float32)
    report = {'winner': winner, 'candidate_config': manifest,
              'original_dev': study.metrics(dev[1], old), 'candidate_dev': study.metrics(dev[1], actual),
              'dev_status': 'Reused confirmation, not an independent test; thresholds in these metrics are descriptive dev operating points.',
              'deployment_status': 'Deployment gates pending'}
    study.write_json(root/'complete.json', report)
    LOG.info('Plist frozen candidate dev AP %.4f; original %.4f', report['candidate_dev']['ap'], report['original_dev']['ap'])
    if args.gate:
        subprocess.run([sys.executable, 'scripts/azoth_tuneup_gates.py', '--root', str(args.output),
                        '--routes', 'plist'], check=True)


if __name__ == '__main__':
    main()
