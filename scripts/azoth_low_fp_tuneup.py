#!/usr/bin/env python3
"""Plist/WHL follow-up using grouped training CV and the production fit path.

Development is reused confirmation, never a trial-selection input. Existing
feature vocabularies are frozen, so CV estimates are conditional on them.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, fields
import gc
import hashlib
import json
import logging
from pathlib import Path
import numpy as np

import azoth_portable_stability as study
import azoth_specialist_tuneup as tune
from azoth_package_tuneup import align, freeze_plan, prepare
from azoth_plist_tuneup import folds, subset
from azoth_tuneup_fulltrain import refit
from collimator import train

LOG = logging.getLogger('low_fp_tuneup')
SOURCES = {
    'plist': Path('out/experiments/plist-round2-20261027/plist'),
    'whl': Path('out/experiments/remaining-regressions-20261028/whl'),
}
PLIST = {
    'control': {},
    'weight005': {'scale_pos_weight_mult': .05},
    'weight0025': {'scale_pos_weight_mult': .025},
    'cap2_weight005': {'max_delta_step': 2., 'scale_pos_weight_mult': .05},
    'fine_leaves': {'min_child_samples': 10, 'min_child_weight': 1., 'num_leaves': 32},
    'regularized': {'num_leaves': 16, 'max_depth': 6, 'reg_lambda': 10., 'reg_alpha': 1.},
    'selective_hnm': {'hard_negative_fraction': .01, 'hard_negative_weight': 3.},
    'selective_hnm_fine': {'hard_negative_fraction': .01, 'hard_negative_weight': 3.,
                         'min_child_samples': 20, 'num_leaves': 32, 'reg_lambda': 5.},
    'budget200': {'n_estimators': 200},
    'budget50': {'n_estimators': 50},
}
WHL_BASE = {'early_stopping_rounds': 0, 'n_estimators': 200,
            'hard_negative_fraction': 0., 'max_delta_step': 2.,
            'scale_pos_weight_mult': .1}
WHL = {
    'control': {},
    'stable200': WHL_BASE,
    'stable100': {**WHL_BASE, 'n_estimators': 100},
    'stable400': {**WHL_BASE, 'n_estimators': 400},
    'weight005': {**WHL_BASE, 'scale_pos_weight_mult': .05},
    'selective_hnm': {**WHL_BASE, 'hard_negative_fraction': .01, 'hard_negative_weight': 3.},
    'regularized': {**WHL_BASE, 'max_depth': 6, 'num_leaves': 16, 'reg_lambda': 10.},
    'fine_leaves': {**WHL_BASE, 'min_child_samples': 20, 'num_leaves': 32, 'reg_lambda': 5.},
}


def cv_rank(record):
    """Demand repeatable strict-FP performance, not a lucky seed or split."""
    metrics = record['fold_metrics']
    recall = [m['at_fp']['0']['recall'] for m in metrics]
    return (float(np.mean(recall)), float(min(recall)),
            float(np.mean([m['at_fp']['1']['recall'] for m in metrics])),
            float(np.mean([m['ap'] for m in metrics])))


def choose(records):
    control = records[0]
    minimum_ap = np.mean([m['ap'] for m in control['fold_metrics']]) - .02
    eligible = [r for r in records if np.mean([m['ap'] for m in r['fold_metrics']]) >= minimum_ap]
    return max(eligible, key=cv_rank)


def settings(config, overrides, seed, threads):
    supported = {f.name for f in fields(train.TrainConfig)}
    unknown = set(overrides) - supported
    if unknown:
        raise ValueError(f'Unsupported full-refit settings: {unknown}')
    merged = {**config, **overrides, 'device': 'cpu', 'n_folds': 0,
              'num_threads': threads, 'seed': seed}
    return train.TrainConfig(**{k: v for k, v in merged.items() if k in supported})


def identity(cohort):
    digest = hashlib.sha256()
    for a in (cohort[4], cohort[1], cohort[2]):
        digest.update(np.ascontiguousarray(a).tobytes())
    return digest.hexdigest()


def run_cv(root, name, manifest, training, config, threads, fold_layout=None):
    marker = root/f'{name}-cv.json'
    if marker.exists():
        return json.loads(marker.read_text())
    probability = np.empty(len(training[1]), dtype=np.float32)
    metrics, seeds_by_fold = [], []
    for fold, (fitting, validation, _) in enumerate(folds(training, training[4])):
        fitting_data, validation_data = subset(training, fitting), subset(training, validation)
        if fold_layout is not None:
            fitting_data, validation_data = fold_layout(fold, fitting_data, validation_data)
        work = root/'cv'/name/f'fold-{fold}'
        work.mkdir(parents=True, exist_ok=True)
        predictions, seed_records = [], []
        for seed in study.SEEDS:
            cfg = settings(config, manifest['training_overrides'], seed, threads)
            output = work/f'seed-{seed}.npz'
            meta = work/f'seed-{seed}.json'
            contract = {'config': asdict(cfg), 'fitting': identity(fitting_data),
                        'validation': identity(validation_data), 'manifest': manifest}
            if output.exists() and meta.exists():
                record = json.loads(meta.read_text())
                if record['contract'] != contract:
                    raise ValueError('Changed CV fit contract; use a new output directory')
                with np.load(output) as saved:
                    np.testing.assert_array_equal(saved['ids'], validation_data[4])
                    p = saved['probability']
            else:
                LOG.info('%s fold=%d seed=%d: production fit path', name, fold, seed)
                result = train.train(fitting_data[0], fitting_data[1], cfg,
                                     sample_file_types=fitting_data[3])
                booster = result.model.booster_
                booster.save_model(str(work/f'seed-{seed}.txt'))
                p = study.predict(booster, validation_data[0], threads)[2]
                record = {'contract': contract, 'trees': booster.num_trees(),
                          'outer_validation': study.metrics(validation_data[1], p)}
                np.savez(output, probability=p, ids=validation_data[4])
                study.write_json(meta, record)
                del result, booster
            predictions.append(p)
            seed_records.append({'seed': seed, 'trees': record['trees'],
                                 'metrics': record['outer_validation']})
            gc.collect()
        mean = np.mean(predictions, axis=0, dtype=np.float32)
        probability[validation] = mean
        metrics.append(study.metrics(validation_data[1], mean))
        seeds_by_fold.append(seed_records)
        LOG.info('%s fold=%d: recall@0FP=%.4f AP=%.4f', name, fold,
                 metrics[-1]['at_fp']['0']['recall'], metrics[-1]['ap'])
        del fitting_data, validation_data, predictions
        gc.collect()
    record = {'variant': name, 'seeds': list(study.SEEDS), 'candidate_config': manifest,
              'fold_metrics': metrics, 'seeds_by_fold': seeds_by_fold,
              'oof': study.metrics(training[1], probability)}
    record['rank'] = list(cv_rank(record))
    np.savez(root/f'{name}-oof.npz', probability=probability, ids=training[4], labels=training[1])
    study.write_json(marker, record)
    LOG.info('COMPLETE %s: rank=%s', name, record['rank'])
    return record


def run_route(output, route, threads):
    source, root = SOURCES[route], output/route
    if (root/'complete.json').exists():
        return json.loads((root/'complete.json').read_text())
    prepare(root, source)
    prior = json.loads((source/'candidate/research.json').read_text())['candidate_config']
    config = json.loads((root/'original/benchmark.json').read_text())['train_config']
    original = tune.load(root, 'train')
    reference = tune.with_extra(root, original) if prior['training_pool'] == 'all_labeled' else original
    if prior['feature_spec'].startswith('features/'):
        training = align(tune.load(root/Path(prior['feature_spec']).parent, 'train'), reference)
    else:
        training = reference
    numeric = PLIST if route == 'plist' else WHL
    manifests = {name: {**prior, 'training_overrides': {**prior['training_overrides'], **changes}}
                 for name, changes in numeric.items()}
    if route == 'whl':
        for family in ('metadata', 'cooccurrence'):
            ready = json.loads((root/'features'/family/'ready.json').read_text())
            manifests[family] = {**prior, 'feature_spec': f'features/{family}/feature_spec.json',
                                 'feature_env': ready['feature_env'],
                                 'training_overrides': {**prior['training_overrides'], **WHL_BASE}}
    freeze_plan(root, {'route': route, 'manifests': manifests, 'seeds': list(study.SEEDS),
        'cohort_identity': identity(training),
        'spec_hashes': {m['feature_spec']: hashlib.sha256((root/m['feature_spec']).read_bytes()).hexdigest()
                        for m in manifests.values()},
        'selection': 'Three canonical-grouped outer training folds; same production training/holdout/HNM path as final refit; fixed three-seed mean. Rank mean recall@0FP, worst-fold recall@0FP, mean recall@1FP, mean AP. Reject mean AP drops >2pp from control.',
        'caveat': 'Frozen vocabularies were discovered on the training partition; CV is conditional on them. Development is reused confirmation only. Locked test remains reserved for deployment gates.'})
    records = []
    for name, manifest in manifests.items():
        matrix = training
        if manifest['feature_spec'] != prior['feature_spec']:
            matrix = align(tune.load(root/Path(manifest['feature_spec']).parent, 'train'), reference)
        records.append(run_cv(root, name, manifest, matrix, config, threads))
        study.write_json(root/'selection.json', {'comparisons': records})
        gc.collect()
    winner = choose(records)
    study.write_json(root/'winner.json', winner)
    (root/'candidate').mkdir(exist_ok=True)
    study.write_json(root/'candidate/research.json', {'winner': winner, 'candidate_config': winner['candidate_config']})
    # The winner is frozen before any development predictions are loaded.
    refit(root, threads)
    with np.load(root/'candidate-fulltrain/dev_predictions.npz') as d:
        ids, labels, probability = d['ids'], d['labels'], d['probability']
    with np.load(source/'candidate-fulltrain/dev_predictions.npz') as d:
        np.testing.assert_array_equal(ids, d['ids'])
        np.testing.assert_array_equal(labels, d['labels'])
        previous = study.metrics(labels, d['probability'])
    current = study.metrics(labels, probability)
    improved = cv_rank(winner) > cv_rank(records[0])
    confirmed = (current['at_fp']['0']['recall'] >= previous['at_fp']['0']['recall']
                 and current['ap'] >= previous['ap'] - .02)
    report = {'winner': winner['variant'], 'cv_improved': improved,
              'previous_dev': previous, 'candidate_dev': current,
              'gate_eligible': bool(improved and confirmed),
              'status': 'research complete; no deployment',
              'dev_status': 'Reused confirmation; these are descriptive thresholds fitted on dev, not independent test results.'}
    benign = np.flatnonzero(labels == 0)
    top = benign[np.argsort(probability[benign])[-20:][::-1]]
    report['highest_scoring_dev_benign'] = [{'id': int(ids[i]), 'score': float(probability[i])} for i in top]
    study.write_json(root/'complete.json', report)
    LOG.info('%s: CV winner=%s gate eligible=%s dev recall@0FP %.4f -> %.4f',
             route, winner['variant'], report['gate_eligible'],
             previous['at_fp']['0']['recall'], current['at_fp']['0']['recall'])
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('out/experiments/plist-whl-low-fp-20261028'))
    parser.add_argument('--routes', nargs='+', choices=list(SOURCES), default=list(SOURCES))
    parser.add_argument('--threads', type=int, default=4)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    args.output.mkdir(parents=True, exist_ok=True)
    status = []
    for route in args.routes:
        report = run_route(args.output, route, args.threads)
        status.append({'route': route, 'status': 'complete', 'gate_eligible': report['gate_eligible']})
        study.write_json(args.output/'status.json', status)


if __name__ == '__main__':
    main()
