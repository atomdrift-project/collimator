#!/usr/bin/env python3
"""Tune npm for recent arrivals without fitting or selecting on locked test."""
from __future__ import annotations

import argparse
import json
import logging
import math
from pathlib import Path

import numpy as np

import azoth_low_fp_tuneup as low
import azoth_specialist_tuneup as tune
import azoth_portable_stability as study
from azoth_package_tuneup import align, freeze_plan, prepare
from azoth_tuneup_fulltrain import refit
from azoth_specialist_suite import _temporary_feature_env
from collimator import bundle, data, features

LOG = logging.getLogger('npm_recent')
SOURCE = Path('out/experiments/deploy-regression-tuneup-20261028/npm')
GRID = {
    'control': ('cooccurrence', {}),
    'original_layout': ('original', {}),
    'original_shallow': ('original', {'max_depth': 8, 'num_leaves': 32, 'reg_lambda': 5.}),
    'cooccurrence_shallow': ('cooccurrence', {'max_depth': 8, 'num_leaves': 32, 'reg_lambda': 5.}),
    'budget200': ('cooccurrence', {'n_estimators': 200}),
    'cap2_weight025': ('cooccurrence', {'max_delta_step': 2., 'scale_pos_weight_mult': .25}),
}


def recent_cutoff(ids, fraction=.01):
    if not 0 < fraction <= 1 or not len(ids):
        raise ValueError('Need a nonempty population and fraction in (0, 1]')
    return int(np.sort(ids)[-math.ceil(len(ids)*fraction)])


def recency_metrics(y, scores, ids, cutoff):
    threshold = study.threshold_at_fp_budget(y, scores, 0)
    recent = ids >= cutoff
    return {'global': study.metrics(y, scores),
            'recent_rows': int(recent.sum()), 'recent_malware': int(y[recent].sum()),
            'recent': study.operating_point(y[recent], scores[recent], threshold),
            'older': study.operating_point(y[~recent], scores[~recent], threshold)}


def rank(row):
    recent = [m['recent']['recall'] for m in row['recency_folds']]
    return float(np.mean(recent)), float(min(recent)), low.cv_rank(row)


def choose(rows):
    baseline = rows[0]
    ap_floor = np.mean([m['ap'] for m in baseline['fold_metrics']]) - .01
    recall_floor = low.cv_rank(baseline)[0] - .02
    eligible = [r for r in rows if np.mean([m['ap'] for m in r['fold_metrics']]) >= ap_floor
                and low.cv_rank(r)[0] >= recall_floor]
    return max(eligible, key=rank)


def audit_live(output, db, workers):
    """Confirm cached findings on current dev arrivals at a frozen threshold."""
    records = json.loads((output/'recent-live-metadata.json').read_text())
    records = [r for r in records if data.partition_of(r['canonical_sha256'] or r['sha256']) == 'dev']
    labels = {r['id']: int(r['label'] == 'bad') for r in records}
    cohort = sorted(labels.items())
    metadata = {r['id']: (study.split_bucket(r['canonical_sha256'] or r['sha256']), 'npm') for r in records}
    root = output/'live-audit'
    root.mkdir(exist_ok=True)
    candidate = SOURCE/'candidate-fulltrain'
    manifest = json.loads((SOURCE/'candidate/research.json').read_text())['candidate_config']
    # Pin requested identities and labels before allowing cached extraction.
    freeze_plan(root, {'cohort': [list(r) for r in cohort], 'candidate': str(candidate),
        'scope': 'Current dev rows in recent ID window; locked test and train excluded. Not necessarily unseen canonical groups.'})
    if not (root/'ready.json').exists():
        identity = {}
        with _temporary_feature_env(manifest['feature_env']):
            _, _, xd, yd = features.extract_partitioned_from_db(db, [], cohort,
                features.FeatureSpec.load(candidate/'feature_spec.json'), n_workers=workers, identity=identity)
        np.testing.assert_array_equal(identity['test_row_ids'], [i for i, _ in cohort])
        study.save_matrix(root, 'dev', xd, yd, identity['test_row_ids'], metadata)
        study.write_json(root/'ready.json', {'evaluation_revision': identity['evaluation_revision']})
    xd, yd, _, _, ids = tune.load(root, 'dev')
    predicted = bundle.Ensemble.load_bundle(candidate).predict_proba(xd)
    threshold = json.loads((candidate/'complete.json').read_text())['dev_metrics']['at_fp']['0']['threshold']
    new = ids > json.loads((SOURCE/'prepared.json').read_text())['max_id']
    report = {'threshold': threshold,
        'scope': 'Current dev rows with ID >= frozen newest-1% cutoff, including later arrivals; not an exact newest-1% slice of the live corpus.',
        'recent_window': {'rows': len(yd), 'malware': int(yd.sum()),
                          'fixed': study.operating_point(yd, predicted, threshold),
                          'ranking': study.metrics(yd, predicted)},
        'new_arrivals': {'rows': int(new.sum()), 'malware': int(yd[new].sum()),
                         'fixed': study.operating_point(yd[new], predicted[new], threshold)},
        'false_positives': [int(i) for i in ids[(yd == 0) & (predicted.astype(np.float64) >= threshold)]],
        'new_misses': [int(i) for i in ids[new & (yd == 1) & (predicted.astype(np.float64) < threshold)]]}
    np.savez(root/'predictions.npz', ids=ids, labels=yd, probability=predicted)
    study.write_json(root/'complete.json', report)
    LOG.info('Current recent npm dev: %s', report)


def main():
    global SOURCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('out/experiments/npm-recency-20261028'))
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--audit-live-only', action='store_true')
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--db', default='postgres://hopper@localhost:5432/hopper')
    args = parser.parse_args()
    SOURCE = args.source
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    if args.audit_live_only:
        audit_live(args.output, args.db, args.workers)
        return
    root = args.output/'npm'
    if (root/'complete.json').exists():
        return
    prepare(root, SOURCE)
    previous = json.loads((SOURCE/'candidate/research.json').read_text())['candidate_config']
    benchmark = json.loads((SOURCE/'original/benchmark.json').read_text())
    original = tune.with_extra(root, tune.load(root, 'train'))
    rich = align(tune.load(root/'features/cooccurrence', 'train'), original)
    cutoff = recent_cutoff(original[4])
    manifests = {}
    for name, (layout, overrides) in GRID.items():
        manifests[name] = {**previous,
            'feature_spec': 'original/feature_spec.json' if layout == 'original' else previous['feature_spec'],
            'feature_env': benchmark['feature_env'] if layout == 'original' else previous['feature_env'],
            'training_overrides': {**previous['training_overrides'], **overrides}}
    freeze_plan(root, {'manifests': manifests, 'seeds': list(study.SEEDS),
        'training_identity': low.identity(original), 'recent_training_cutoff_id': cutoff,
        'recency_definition': 'Highest 1% of frozen training sample IDs: ingestion-order proxy, not package publication time.',
        'selection': 'Mean then worst-fold recent recall at thresholds fitted on all outer-validation rows with zero FP. Guard global mean AP within 1pp and global mean zero-FP recall within 2pp of control. Fixed three-seed ensembles; production fit path.',
        'limitations': 'Existing vocabularies are frozen from training, so CV is conditional on them. Dev was previously examined and is reused confirmation only; locked test is not read.'})
    records = []
    for name, (layout, _) in GRID.items():
        matrix = original if layout == 'original' else rich
        row = low.run_cv(root, name, manifests[name], matrix, benchmark['train_config'], args.threads)
        with np.load(root/f'{name}-oof.npz') as d:
            np.testing.assert_array_equal(d['ids'], matrix[4])
            p = d['probability']
        assignment = np.minimum((matrix[2]*3).astype(int), 2)
        recent_folds = []
        for fold in range(3):
            mask = assignment == fold
            metrics = recency_metrics(matrix[1][mask], p[mask], matrix[4][mask], cutoff)
            if metrics['recent_malware'] < 10:
                raise ValueError('Too few recent malware samples to select reliably')
            recent_folds.append(metrics)
        row['recency_folds'] = recent_folds
        records.append(row)
        study.write_json(root/'selection.json', {'comparisons': records})
        LOG.info('%s recent recall rank=%s', name, rank(row))
    winner = choose(records)
    study.write_json(root/'winner.json', winner)
    (root/'candidate').mkdir(exist_ok=True)
    study.write_json(root/'candidate/research.json', {'winner': winner, 'candidate_config': winner['candidate_config']})
    refit(root, args.threads)
    # Freeze the choice above, then confirm against the existing dev cohort.
    with np.load(root/'candidate-fulltrain/dev_predictions.npz') as d:
        ids, labels, probability = d['ids'], d['labels'], d['probability']
    with np.load(SOURCE/'candidate-fulltrain/dev_predictions.npz') as d:
        np.testing.assert_array_equal(ids, d['ids'])
        np.testing.assert_array_equal(labels, d['labels'])
        old = d['probability']
    dev_cutoff = recent_cutoff(np.r_[original[4], ids])
    before = recency_metrics(labels, old, ids, dev_cutoff)
    after = recency_metrics(labels, probability, ids, dev_cutoff)
    eligible = (rank(winner) > rank(records[0]) and after['recent']['recall'] > before['recent']['recall']
                and after['global']['ap'] >= before['global']['ap']-.01
                and after['global']['at_fp']['0']['recall'] >= before['global']['at_fp']['0']['recall']-.02)
    study.write_json(root/'complete.json', {'winner': winner['variant'], 'previous_dev': before,
        'candidate_dev': after, 'gate_eligible': bool(eligible),
        'dev_status': 'Reused confirmation, not independent test; thresholds fitted on all dev and then applied unchanged to recent/older slices.',
        'deployment_status': 'Research only; deployment gates pending'})
    LOG.info('NPM complete: %s recent dev recall %.4f -> %.4f; gate eligible=%s',
             winner['variant'], before['recent']['recall'], after['recent']['recall'], eligible)


if __name__ == '__main__':
    main()
