#!/usr/bin/env python3
"""A finite, matched tuning round for regressions in the installed nightly.

Use train for fitting and early stopping, canonical-grouped halves of dev for
selection and assessment, and never load the production test score table.
Keep the installed model unchanged; export research candidates for confirmation.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import gc
import hashlib
import itertools
import json
import logging
import multiprocessing
import os
from pathlib import Path
import shutil
from types import SimpleNamespace

import lightgbm as lgb
import numpy as np

import azoth_portable_stability as study
import azoth_specialist_tuneup as tune
from collimator import export, features, model
from collimator.fit_resources import estimate_fit_gb, fit_reservation

LOG = logging.getLogger('regressed_models')
ROUTES = ['filetypes/apk_android', 'filetypes/rust', 'filetypes/kotlin',
          'filetypes/go', 'filetypes/html', 'filegroups/portable']
VARIANTS = {
    'control': {},
    'cap5': {'max_delta_step': 5.0},
    'neutral_cap5': {'boost_from_average': False, 'max_delta_step': 5.0},
    'weight025_no_hnm': {'scale_pos_weight_mult': .25, 'hard_negative_fraction': 0.0,
                         'max_delta_step': 5.0},
    'weight010_no_hnm': {'scale_pos_weight_mult': .10, 'hard_negative_fraction': 0.0,
                         'max_delta_step': 2.0},
    'finer_regularized': {'min_child_samples': 20, 'min_child_weight': 1.0,
                          'num_leaves': 32, 'max_depth': 8, 'reg_lambda': 5.0,
                          'scale_pos_weight_mult': .25, 'hard_negative_fraction': 0.0,
                          'max_delta_step': 2.0},
}
PYTHON_BYTECODE = {'pyc', 'python-bytecode', 'python_bytecode'}


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(path, value):
    if path.exists():
        if json.loads(path.read_text()) != value:
            raise ValueError(f'Resume configuration changed: {path}; use a new output directory')
    else:
        study.write_json(path, value)


def profile(labels, probability, filetypes, route):
    result = study.metrics(labels, probability)
    result['by_filetype'] = {
        str(ft): study.metrics(labels[filetypes == ft], probability[filetypes == ft])
        for ft in np.unique(filetypes)
    }
    target = np.isin(filetypes, list(PYTHON_BYTECODE)) if route == 'filegroups/portable' else np.ones(len(labels), bool)
    result['target'] = study.metrics(labels[target], probability[target])
    return result


def rank(value):
    target = value['target']
    return (target['at_fp']['1']['recall'], target['at_fp']['0']['recall'],
            target['ap'] if target['ap'] is not None else -1,
            value['ap'] if value['ap'] is not None else -1)


def choose(records, reference):
    # Protect overall ranking while targeting the damaged strict operating tail.
    eligible = [r for r in records if r['selection']['ap'] is not None
                and r['selection']['ap'] >= reference['selection']['ap'] - .02]
    return max(eligible, key=lambda r: rank(r['selection']))


def paired_recall_interval(labels, groups, candidate_hit, baseline_hit, repeats=2000):
    positive = labels == 1
    _, inverse = np.unique(groups[positive], return_inverse=True)
    if not len(inverse):
        return None
    size = np.bincount(inverse)
    gain = np.bincount(inverse, weights=(candidate_hit[positive].astype(float)
                                       - baseline_hit[positive].astype(float)))
    rng = np.random.default_rng(20261031)
    samples = []
    for _ in range(0, repeats, 50):
        draws = rng.integers(0, len(size), size=(min(50, repeats - len(samples)), len(size)))
        samples.extend((gain[draws].sum(axis=1) / size[draws].sum(axis=1)).tolist())
    return {'delta': float(gain.sum() / size.sum()),
            'ci_low': float(np.quantile(samples, .025)),
            'ci_high': float(np.quantile(samples, .975)),
            'positive_groups': len(size), 'replicates': repeats,
            'scope': 'Paired positive-group bootstrap of recall at selection-fixed thresholds; exploratory, no multiplicity correction'}


def export_candidate(root, winner, spec, matrix, reference, threads):
    dest = root / 'candidate'
    (dest / 'models').mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / 'original/feature_spec.json', dest / 'feature_spec.json')
    paths = []
    for seed in winner['seeds']:
        source = (root / 'original/models' / f'seed_{seed}.txt' if winner['variant'] == 'original'
                  else root / 'results' / f"{winner['variant']}_seed{seed}" / 'model.txt')
        txt = dest / 'models' / f'seed_{seed}.txt'
        shutil.copy2(source, txt)
        path = txt.with_suffix('.onnx')
        if not export.export_lightgbm_onnx(lgb.Booster(model_file=str(txt)), spec.total_features, path):
            raise RuntimeError(f'ONNX export failed: {path}')
        paths.append(path)
    os.environ['COLLIMATOR_ONNX_THREADS'] = str(threads)
    members = model.load_onnx_models(paths)
    actual = np.mean([m.predict(matrix) for m in members], axis=0, dtype=np.float32)
    delta = np.abs(actual - reference)
    report = {'max_probability_difference': float(delta.max()),
              'rows_over_1e_4': int((delta > 1e-4).sum()),
              'assessment_rows': len(actual), 'passed': bool(delta.max() <= 1e-4)}
    study.write_json(dest / 'parity.json', report)
    return report


def run_route(args, route):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    root = args.output / route
    root.mkdir(parents=True, exist_ok=True)
    source = args.source / route
    artifact_names = ['benchmark.json', 'feature_spec.json'] + [str(p.relative_to(source)) for p in sorted((source / 'models').glob('seed_*.txt'))]
    plan = {'route': route, 'max_id': args.max_id, 'variants': VARIANTS,
            'seeds': list(study.SEEDS), 'threads': args.threads,
            'source': str(source.resolve()),
            'source_hashes': {name: fingerprint(source / name) for name in artifact_names},
            'objective': 'Target-filetype recall at one FP, then zero FP, then AP; preserve overall selection AP within 2pp. Portable targets Python bytecode.',
            'selection': 'canonical-grouped development selection; separate assessment after the winner is frozen',
            'test_usage': 'none', 'publication': 'research candidates only'}
    freeze(root / 'plan.json', plan)
    if (root / 'complete.json').exists():
        return json.loads((root / 'complete.json').read_text())
    os.environ['COLLIMATOR_MATRIX_DISK_DIR'] = str(root / 'scratch')
    os.environ['COLLIMATOR_MEM_RESERVE_GB'] = '2'
    os.environ['COLLIMATOR_FIT_RESOURCE_DIR'] = str(args.output / 'fit-resources')
    os.environ['COLLIMATOR_MEM_CEILING_GB'] = '80'
    study.prepare(SimpleNamespace(source=source, output=root, db=args.db, max_id=args.max_id,
                                  workers=args.workers, threads=args.threads, variants=VARIANTS))
    training, dev = tune.load(root, 'train'), tune.load(root, 'dev')
    mode = tune.choose_mode(dev)
    fit, stop, xd, yd, selection, filetypes = tune.partition_evaluation(training, dev, mode)
    config = json.loads((root / 'original/benchmark.json').read_text())['train_config']
    spec = features.FeatureSpec.load(root / 'original/feature_spec.json')
    freeze(root / 'cohorts.json', {'mode': mode, 'fit': int(fit.sum()), 'early_stop': int(stop.sum()),
                                  'selection': int(selection.sum()), 'assessment': int((~selection).sum())})
    LOG.info('%s: frozen cohorts %s; %d features', route, mode, spec.total_features)
    study.score_original(SimpleNamespace(output=root, threads=args.threads), xd, yd, selection)
    for name, overrides in VARIANTS.items():
        LOG.info('%s: fitting %s', route, name)
        budget = SimpleNamespace(n_folds=0, num_threads=args.threads)
        with fit_reservation(estimate_fit_gb(training[0], budget)):
            study.fit_variant(SimpleNamespace(output=root, threads=args.threads), name, overrides,
                              training[0][fit], training[1][fit], training[0][stop], training[1][stop],
                              xd, yd, selection, config)
        gc.collect()
    records, predictions = [], {}
    original = study.original_seeds(root)
    memberships = [('original', list(original))]
    memberships += [('original', list(s)) for n in range(1, len(original)) for s in itertools.combinations(original, n)]
    memberships += [(name, list(study.SEEDS)) for name in VARIANTS]
    for name, seeds in memberships:
        key = name + ':' + ','.join(map(str, seeds))
        p = np.mean([np.load(root / 'results' / f'{name}_seed{seed}' / 'predictions.npz')['probability']
                     for seed in seeds], axis=0, dtype=np.float32)
        predictions[key] = p
        records.append({'key': key, 'variant': name, 'seeds': seeds,
                        'selection': profile(yd[selection], p[selection], filetypes[selection], route)})
    current = records[0]
    winner = choose(records, current)
    # No assessment values participate in this choice, including seed admission.
    freeze(root / 'frozen-winner.json', {'winner': winner, 'current': current, 'comparisons': records})
    assessment = ~selection
    target = np.isin(filetypes, list(PYTHON_BYTECODE)) if route == 'filegroups/portable' else np.ones(len(yd), bool)
    reports = {}
    for entry in [current, winner]:
        p = predictions[entry['key']]
        result = profile(yd[assessment], p[assessment], filetypes[assessment], route)
        threshold = entry['selection']['target']['at_fp']['1']['threshold']
        result['selection_fixed_target_threshold'] = study.operating_point(
            yd[assessment & target], p[assessment & target], threshold)
        reports[entry['key']] = result
    before = reports[current['key']]
    after = reports[winner['key']]
    mask = assessment & target
    interval = paired_recall_interval(yd[mask], dev[2][mask] if mode == 'dev_halves' else np.arange(mask.sum()),
        predictions[winner['key']][mask] >= winner['selection']['target']['at_fp']['1']['threshold'],
        predictions[current['key']][mask] >= current['selection']['target']['at_fp']['1']['threshold'])
    parity = export_candidate(root, winner, spec, xd[assessment], predictions[winner['key']][assessment], args.threads)
    result = {'route': route, 'winner': {'variant': winner['variant'], 'seeds': winner['seeds']},
              'current_assessment': before, 'candidate_assessment': after,
              'target_recall_1fp_delta': after['target']['at_fp']['1']['recall'] - before['target']['at_fp']['1']['recall'],
              'selection_fixed_recall_delta_ci': interval, 'onnx_parity': parity,
              'status': 'finite tuning round complete; independent confirmation and production refit pending',
              'installed_model_changed': False}
    study.write_json(root / 'complete.json', result)
    LOG.info('COMPLETE %s: target assessment recall@1FP %.4f -> %.4f; parity=%s', route,
             before['target']['at_fp']['1']['recall'], after['target']['at_fp']['1']['recall'], parity['passed'])
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, default=Path('out/models/azoth'))
    p.add_argument('--output', type=Path, default=Path('out/experiments/regressed-models-20261031'))
    p.add_argument('--routes', nargs='+', default=ROUTES)
    p.add_argument('--db', default='postgres://hopper@localhost:5432/hopper')
    p.add_argument('--max-id', type=int, default=6309383805)
    p.add_argument('--workers', type=int, default=6)
    p.add_argument('--threads', type=int, default=8)
    p.add_argument('--parallelism', type=int, default=2)
    args = p.parse_args()
    args.source, args.output = args.source.resolve(), args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    for route in args.routes:
        if route not in ROUTES:
            p.error(f'Unsupported route: {route}')
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.parallelism,
            mp_context=multiprocessing.get_context('spawn')) as pool:
        pending = {pool.submit(run_route, args, route): route for route in args.routes}
        for future in concurrent.futures.as_completed(pending):
            route = pending[future]
            try:
                result = future.result()
                results.append(result)
                print(json.dumps({'route': route, 'winner': result['winner'],
                                  'assessment_delta': result['target_recall_1fp_delta']}), flush=True)
            except Exception as exc:
                LOG.exception('FAILED %s', route)
                results.append({'route': route, 'error': str(exc)})
            study.write_json(args.output / 'status.json', results)
    return int(any('error' in result for result in results))


if __name__ == '__main__':
    raise SystemExit(main())
