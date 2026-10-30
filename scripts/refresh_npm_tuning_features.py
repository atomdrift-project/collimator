#!/usr/bin/env python3
"""Re-extract frozen npm identities with the current feature normalizer.

Keep the old vocabularies and labels, and record the newly observed report
revision. Never stamp new code identities onto old feature matrices.
"""
import argparse
import gc
import json
import logging
from pathlib import Path
import shutil

import numpy as np

import azoth_portable_stability as study
import azoth_specialist_tuneup as tune
from azoth_package_tuneup import freeze_plan
from azoth_specialist_suite import _temporary_feature_env
from collimator import features, cache_identity, bundle


def refresh(source, dest, db, workers):
    dest.mkdir(parents=True, exist_ok=True)
    revision = cache_identity.code_revision('features')
    freeze_plan(dest, {'source': str(source), 'feature_code_revision': revision,
                      'policy': 'Freeze source row IDs, labels, vocabulary and canonical splits; re-extract current reports.'})
    if (dest/'refresh-complete.json').exists():
        return
    for name in ('original', 'candidate'):
        shutil.copytree(source/name, dest/name, dirs_exist_ok=True)
    original = tune.load(source, 'train')
    extra = tune.load(source, 'extra')
    dev = tune.load(source, 'dev')
    full_ids = np.r_[original[4], extra[4]]
    full_labels = np.r_[original[1], extra[1]]
    train_rows = sorted(zip(map(int, full_ids), map(int, full_labels)))
    dev_rows = sorted(zip(map(int, dev[4]), map(int, dev[1])))
    metadata = {int(i): (float(b), str(ft)) for cohort in (original, extra, dev)
                for i, b, ft in zip(cohort[4], cohort[2], cohort[3])}
    original_ids, extra_ids = set(map(int, original[4])), set(map(int, extra[4]))
    source_counts = {'original_train': len(original[4]), 'extra': len(extra[4]), 'dev': len(dev[4])}
    # Release source matrices before allocating refreshed ones.
    del original, extra, dev
    gc.collect()
    manifests = {
        'original': {'feature_env': json.loads((source/'original/benchmark.json').read_text())['feature_env'],
                     'feature_spec': 'original/feature_spec.json'},
        'cooccurrence': json.loads((source/'candidate/research.json').read_text())['candidate_config'],
    }
    revisions = {}
    for name, manifest in manifests.items():
        target = dest if name == 'original' else dest/'features/cooccurrence'
        marker = target/'normalized-ready.json'
        if marker.exists():
            revisions[name] = json.loads(marker.read_text())
            continue
        target.mkdir(parents=True, exist_ok=True)
        spec_path = source/manifest['feature_spec']
        if name != 'original':
            shutil.copy2(spec_path, target/'feature_spec.json')
        identity = {}
        logging.info('Refreshing %s: %s train and %s dev rows', name, len(train_rows), len(dev_rows))
        with _temporary_feature_env(manifest['feature_env']):
            xt, yt, xd, yd = features.extract_partitioned_from_db(db, train_rows, dev_rows,
                features.FeatureSpec.load(spec_path), n_workers=workers, identity=identity)
        tids, dids = np.asarray(identity['train_row_ids']), np.asarray(identity['test_row_ids'])
        np.testing.assert_array_equal(tids, [r[0] for r in train_rows])
        np.testing.assert_array_equal(yt, [r[1] for r in train_rows])
        np.testing.assert_array_equal(dids, [r[0] for r in dev_rows])
        np.testing.assert_array_equal(yd, [r[1] for r in dev_rows])
        if name == 'original':
            for label, selected in [('train', original_ids), ('extra', extra_ids)]:
                mask = np.isin(tids, list(selected))
                study.save_matrix(target, label, xt[mask], yt[mask], tids[mask], metadata)
        else:
            study.save_matrix(target, 'train', xt, yt, tids, metadata)
        study.save_matrix(target, 'dev', xd, yd, dids, metadata)
        record = {'feature_code_revision': revision, 'evaluation_revision': identity['evaluation_revision'],
                  'feature_env': manifest['feature_env'], 'source_counts': source_counts}
        study.write_json(marker, record)
        revisions[name] = record
        del xt, yt, xd, yd
        gc.collect()
    study.write_json(dest/'extra-ready.json', {'rows': source_counts['extra'],
        'evaluation_revision': revisions['original']['evaluation_revision']})
    prepared = json.loads((source/'prepared.json').read_text())
    prepared.update(feature_code_revision=revision, evaluation_revision=revisions['original']['evaluation_revision'],
                    feature_refresh_source=str(source))
    study.write_json(dest/'prepared.json', prepared)
    # Re-score the previous frozen model on refreshed dev features for a fair
    # comparison. Preserve its original training provenance and native weights.
    candidate = dest/'candidate-fulltrain'
    shutil.copytree(source/'candidate-fulltrain', candidate, dirs_exist_ok=True)
    xd, yd, _, _, dids = tune.load(dest/'features/cooccurrence', 'dev')
    p = bundle.Ensemble.load_bundle(candidate).predict_proba(xd)
    np.savez(candidate/'dev_predictions.npz', ids=dids, labels=yd, probability=p)
    previous = json.loads((candidate/'complete.json').read_text())
    previous['dev_metrics'] = study.metrics(yd, p)
    previous['dev_feature_refresh'] = revisions['cooccurrence']
    study.write_json(candidate/'complete.json', previous)
    study.write_json(dest/'refresh-complete.json', {'layouts': revisions,
        'baseline': 'Original model weights, rescored on refreshed dev; no retraining or test use.'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('out/experiments/deploy-regression-tuneup-20261028/npm'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--db', default='postgres://hopper@localhost:5432/hopper')
    parser.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    refresh(args.source, args.output, args.db, args.workers)
