#!/usr/bin/env python3
"""Second-round VSIX/Gem trials on frozen matrices, with no locked-test access."""
from __future__ import annotations

import argparse
import gc
import json
import logging
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

import numpy as np

import azoth_portable_stability as study
import azoth_specialist_tuneup as tune

LOG = logging.getLogger('package_tuneup')
VSIX = {
    'control': {},
    'smaller_leaves': {'min_child_samples': 10, 'min_child_weight': 1, 'num_leaves': 32},
    'smaller_weight025': {'min_child_samples': 10, 'min_child_weight': 1, 'num_leaves': 32, 'scale_pos_weight_mult': .25},
    'smaller_weight010': {'min_child_samples': 10, 'min_child_weight': 1, 'num_leaves': 32, 'scale_pos_weight_mult': .1},
    'shallow_regularized': {'min_child_samples': 20, 'min_child_weight': 1, 'num_leaves': 16, 'reg_lambda': 5., 'scale_pos_weight_mult': .25},
    'full_rows': {'min_child_samples': 10, 'min_child_weight': 1, 'num_leaves': 32, 'scale_pos_weight_mult': .25, 'subsample': 1., 'colsample_bytree': 1.},
    'capped': {'min_child_samples': 10, 'min_child_weight': 1, 'num_leaves': 32, 'scale_pos_weight_mult': .25, 'max_delta_step': 2.},
    'extra_trees': {'min_child_samples': 10, 'min_child_weight': 1, 'num_leaves': 32, 'scale_pos_weight_mult': .25, 'extra_trees': True},
}
GEM = {
    'control': {},
    'no_hnm': {'hard_negative_fraction': 0.},
    'gentle_hnm': {'hard_negative_fraction': .05, 'hard_negative_weight': 3.},
    'cap2': {'max_delta_step': 2.},
    'cap5': {'max_delta_step': 5.},
    'weight010': {'scale_pos_weight_mult': .1},
    'weight050': {'scale_pos_weight_mult': .5},
    'smaller_trees': {'num_leaves': 32, 'min_child_samples': 30, 'reg_lambda': 5.},
}


def freeze_plan(root, plan):
    path = root/'trial-plan.json'
    if path.exists() and json.loads(path.read_text()) != plan:
        raise ValueError('Changed trial plan; use a new output directory')
    study.write_json(path, plan)


def prepare(root, source):
    root.mkdir(parents=True, exist_ok=True)
    # Read-only shared inputs; all fits and candidate artifacts live in root.
    for name in ('original', 'train', 'dev', 'features', 'extra', 'extra-ready.json'):
        target = source/name
        if target.exists() and not (root/name).exists():
            (root/name).symlink_to(target.resolve(), target_is_directory=target.is_dir())


def align(cohort, reference):
    order = np.argsort(cohort[4])
    index = order[np.searchsorted(cohort[4][order], reference[4])]
    if not np.array_equal(cohort[4][index], reference[4]) or not np.array_equal(cohort[1][index], reference[1]):
        raise ValueError('Feature-family cohort mismatch')
    return (cohort[0][index], *(a[index] for a in cohort[1:]))


def ensemble_predictions(root, name):
    return np.mean([np.load(root/'results'/f'{name}_seed{s}'/'predictions.npz')['probability']
                    for s in study.SEEDS], axis=0, dtype=np.float32)


def vsix(root, source, threads):
    previous = json.loads((source/'candidate/research.json').read_text())
    manifest = previous['candidate_config']
    family = source/Path(manifest['feature_spec']).parent
    reference = tune.load(source, 'train')
    training = align(tune.load(family, 'train'), reference)
    x, y, buckets = training[:3]
    fold_ids = np.minimum((buckets*3).astype(int), 2)
    config = json.loads((source/'original/benchmark.json').read_text())['train_config']
    base = {**manifest['training_overrides'], 'early_stopping_rounds': 0}
    freeze_plan(root, {'route': 'vsix', 'grid': VSIX, 'base': base, 'manifest': manifest,
        'seeds': list(study.SEEDS), 'selection': 'mean AP across three canonical-grouped training folds; fixed three-seed ensemble',
        'caveat': 'Frozen vocabulary was discovered on the whole training partition. CV estimates are conditional on that vocabulary. Development is reused confirmation; locked test remains for deployment gates.'})
    comparisons = []
    for name, changes in VSIX.items():
        overrides = {**base, **changes}
        probabilities = np.empty(len(y), dtype=np.float32)
        fold_metrics = []
        for fold in range(3):
            validation = fold_ids == fold
            fitting = ~validation
            if min(np.sum(y[validation] == c) for c in (0, 1)) < 2:
                raise ValueError('Insufficient classes in canonical fold')
            work = root/f'fold-{fold}'
            work.mkdir(exist_ok=True)
            study.fit_variant(SimpleNamespace(output=work, threads=threads), name, overrides,
                x[fitting], y[fitting], x[validation], y[validation], x[validation], y[validation],
                np.ones(validation.sum(), dtype=bool), config)
            probabilities[validation] = ensemble_predictions(work, name)
            fold_metrics.append(study.metrics(y[validation], probabilities[validation]))
        record = {'variant': name, 'seeds': list(study.SEEDS), 'overrides': overrides,
            'mean_fold_ap': float(np.mean([m['ap'] for m in fold_metrics])),
            'fold_metrics': fold_metrics, 'oof': study.metrics(y, probabilities)}
        comparisons.append(record)
        np.save(root/f'{name}-oof.npy', probabilities)
        study.write_json(root/'selection.json', {'comparisons': comparisons})
        LOG.info('VSIX %s: mean fold AP %.4f; pooled AP %.4f', name, record['mean_fold_ap'], record['oof']['ap'])
        gc.collect()
    winner = max(comparisons, key=lambda r: (r['mean_fold_ap'], r['oof']['ap']))
    return {**manifest, 'training_overrides': winner['overrides']}, winner


def gem(root, source, threads):
    config = json.loads((source/'original/benchmark.json').read_text())['train_config']
    original = json.loads((source/'results/all_labeled_seed44/result.json').read_text())['candidate_config']
    training = tune.with_extra(source, tune.load(source, 'train'))
    dev = tune.load(source, 'dev')
    fit_mask, stop_mask, xd, yd, selection, _ = tune.partition_evaluation(training, dev, 'dev_halves')
    freeze_plan(root, {'route': 'gem', 'grid': GEM, 'base': original, 'seeds': list(study.SEEDS),
        'selection': 'fixed three-seed ensemble, dev selection AP then recall at five false positives; no assessment or test access before selection'})
    comparisons = []
    for name, changes in GEM.items():
        overrides = {**original['training_overrides'], **changes}
        study.fit_variant(SimpleNamespace(output=root, threads=threads), name, overrides,
            training[0][fit_mask], training[1][fit_mask], training[0][stop_mask], training[1][stop_mask],
            xd, yd, selection, config)
        p = ensemble_predictions(root, name)
        comparisons.append({'variant': name, 'seeds': list(study.SEEDS), 'overrides': overrides,
                            'selection': study.metrics(yd[selection], p[selection])})
        study.write_json(root/'selection.json', {'comparisons': comparisons})
    winner = max(comparisons, key=lambda r: study.rank(r['selection']))
    # Freeze before exposing the held-out development half.
    study.write_json(root/'winner.json', winner)
    p = ensemble_predictions(root, winner['variant'])
    study.write_json(root/'assessment.json', {'winner': winner,
        'metrics': study.metrics(yd[~selection], p[~selection]),
        'fixed_thresholds': {b: study.operating_point(yd[~selection], p[~selection], v['threshold'])
                             for b,v in winner['selection']['at_fp'].items()}})
    return {**original, 'training_overrides': winner['overrides']}, winner


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('out/experiments/specialist-tuneup-20261027'))
    parser.add_argument('--output', type=Path, default=Path('out/experiments/vsix-gem-round2-20261027'))
    parser.add_argument('--routes', nargs='+', choices=['vsix','gem'], default=['vsix','gem'])
    parser.add_argument('--threads', type=int, default=4)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    for route in args.routes:
        source, root = args.source/route, args.output/route
        if (root/'complete.json').exists():
            continue
        while not (source/'complete.json').exists():
            LOG.info('Waiting for first-round %s to finish', route)
            time.sleep(30)
        prepare(root, source)
        manifest, winner = (vsix if route == 'vsix' else gem)(root, source, args.threads)
        (root/'candidate').mkdir(exist_ok=True)
        study.write_json(root/'candidate/research.json', {'winner': winner, 'candidate_config': manifest})
        subprocess.run([sys.executable, 'scripts/azoth_tuneup_fulltrain.py', '--root', str(args.output),
                        '--routes', route, '--threads', str(args.threads)], check=True)
        study.write_json(root/'complete.json', {'winner':winner, 'candidate_config':manifest,
            'status':'Refit and ONNX parity complete; deployment gates pending'})
        LOG.info('COMPLETE %s', route)


if __name__ == '__main__':
    main()
