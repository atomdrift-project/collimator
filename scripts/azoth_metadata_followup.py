#!/usr/bin/env python3
"""Fit metadata vocabularies inside training folds, then confirm frozen winners."""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
from pathlib import Path

import numpy as np

import azoth_low_fp_tuneup as low
import azoth_specialist_tuneup as tune
import azoth_portable_stability as study
from azoth_package_tuneup import align, freeze_plan
from azoth_tuneup_fulltrain import refit

LOG = logging.getLogger('metadata_followup')


def metadata_env(previous, *, rare=False):
    env = {**previous, **tune.FEATURES['metadata']}
    # Discovery stores kv_vocab even when the feature group is disabled.
    # Merely enabling KV_VOCAB therefore does not enable its model columns.
    disabled = {x.strip() for x in env.get('COLLIMATOR_DISABLE_FEATURE_GROUPS', '').split(',') if x.strip()}
    disabled.discard('kv')
    env['COLLIMATOR_DISABLE_FEATURE_GROUPS'] = ','.join(sorted(disabled))
    if rare:
        env.update(COLLIMATOR_KV_MIN_FREQ='1', COLLIMATOR_KV_VALUE_SPLIT='1')
    return env


def route(args, name):
    root, source = args.output/name, low.SOURCES[name]
    if (root/'complete.json').exists():
        return json.loads((root/'complete.json').read_text())
    root.mkdir(parents=True, exist_ok=True)
    # Feature outputs here are writable local directories, not source symlinks.
    for part in ('original', 'train', 'dev', 'extra', 'extra-ready.json'):
        if (source/part).exists() and not (root/part).exists():
            (root/part).symlink_to((source/part).resolve())
    prior = json.loads((source/'candidate/research.json').read_text())['candidate_config']
    config = json.loads((root/'original/benchmark.json').read_text())['train_config']
    original = tune.load(root, 'train')
    training = tune.with_extra(root, original) if prior['training_pool'] == 'all_labeled' else original
    source_family = source/Path(prior['feature_spec']).parent if prior['feature_spec'].startswith('features/') else source
    control = align(tune.load(source_family, 'train'), training)
    # Control's fixed full-training vocabulary is explicitly conditional CV.
    # New layouts discover their vocabularies only on the outer fitting rows.
    manifests = {'control': {**prior, 'feature_spec': 'features/control/feature_spec.json'}}
    (root/'features').mkdir(exist_ok=True)
    control_root = root/'features/control'
    control_root.mkdir(exist_ok=True)
    for part in ('train', 'dev'):
        if not (control_root/part).exists():
            (control_root/part).symlink_to((source_family/part).resolve())
    if not (control_root/'feature_spec.json').exists():
        (control_root/'feature_spec.json').symlink_to((source/prior['feature_spec']).resolve())
    base = prior['training_overrides'] if name == 'plist' else low.WHL_BASE
    for family, rare in [('metadata_enabled', False), ('metadata_rare_tokens', True)]:
        manifests[family] = {**prior, 'feature_spec': f'features/{family}/feature_spec.json',
                             'feature_env': metadata_env(prior['feature_env'], rare=rare),
                             'training_overrides': base}
    freeze_plan(root, {'route': name, 'manifests': manifests, 'cohort_identity': low.identity(training),
        'control_spec_sha256': hashlib.sha256((source/prior['feature_spec']).read_bytes()).hexdigest(),
        'seeds': list(study.SEEDS), 'selection': 'Same low-FP ranking and AP guard as numeric study; three canonical training folds, production fit, fixed three-seed mean.',
        'vocabulary': 'Control uses prior frozen vocabulary. Each new feature vocabulary sees only its outer fitting rows. Dev is loaded after freezing the winner; locked test is not read.'})
    records = [low.run_cv(root, 'control', manifests['control'], control, config, args.threads)]
    for family in ('metadata_enabled', 'metadata_rare_tokens'):
        manifest = manifests[family]

        def layout(fold, fitting, validation):
            work = root/f'fold-{fold}'
            work.mkdir(exist_ok=True)
            result = tune.feature_matrices(args, work, family, manifest['feature_env'], fitting, validation)
            spec = json.loads((work/'features'/family/'feature_spec.json').read_text())
            kv_columns = sum(n.startswith('kv:') for n in spec['feature_names'])
            LOG.info('%s %s fold=%s: %s key/value model columns', name, family, fold, kv_columns)
            if spec.get('kv_vocab') and not kv_columns:
                raise ValueError('KV vocabulary discovered but all KV columns disabled')
            return result

        records.append(low.run_cv(root, family, manifest, training, config, args.threads, fold_layout=layout))
        study.write_json(root/'selection.json', {'comparisons': records})
    winner = low.choose(records)
    study.write_json(root/'winner.json', winner)
    if winner['variant'] != 'control':
        tune.feature_matrices(args, root, winner['variant'], winner['candidate_config']['feature_env'],
                              training, tune.load(root, 'dev'))
    (root/'candidate').mkdir(exist_ok=True)
    study.write_json(root/'candidate/research.json', {'winner': winner, 'candidate_config': winner['candidate_config']})
    refit(root, args.threads)
    with np.load(root/'candidate-fulltrain/dev_predictions.npz') as d:
        ids, labels, probability = d['ids'], d['labels'], d['probability']
    with np.load(source/'candidate-fulltrain/dev_predictions.npz') as d:
        np.testing.assert_array_equal(ids, d['ids'])
        np.testing.assert_array_equal(labels, d['labels'])
        previous = study.metrics(labels, d['probability'])
    current = study.metrics(labels, probability)
    eligible = (low.cv_rank(winner) > low.cv_rank(records[0])
                and current['at_fp']['0']['recall'] >= previous['at_fp']['0']['recall']
                and current['ap'] >= previous['ap'] - .02)
    report = {'winner': winner['variant'], 'previous_dev': previous, 'candidate_dev': current,
              'gate_eligible': bool(eligible), 'status': 'research complete; no deployment',
              'dev_status': 'Reused confirmation only. Operating thresholds fitted on dev, not an independent test.'}
    study.write_json(root/'complete.json', report)
    LOG.info('%s: winner=%s gate eligible=%s', name, winner['variant'], eligible)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('out/experiments/plist-whl-metadata-20261028'))
    parser.add_argument('--routes', nargs='+', choices=list(low.SOURCES), default=list(low.SOURCES))
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--db', default='postgres://hopper@localhost:5432/hopper')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    args.output.mkdir(parents=True, exist_ok=True)
    status = []
    for name in args.routes:
        report = route(args, name)
        status.append({'route': name, 'status': 'complete', 'gate_eligible': report['gate_eligible']})
        study.write_json(args.output/'status.json', status)


if __name__ == '__main__':
    main()
