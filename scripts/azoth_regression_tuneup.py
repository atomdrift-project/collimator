#!/usr/bin/env python3
"""Independent low-FP route experiments, followed by an isolated bundle gate."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import gc
import json
import logging
from pathlib import Path
import shutil
import subprocess
import sys

import azoth_specialist_tuneup as tune
import azoth_portable_stability as study
from azoth_specialist_suite import _temporary_feature_env
from azoth_tuneup_fulltrain import refit
from collimator import data, features, train

LOG = logging.getLogger('regression_tuneup')
ROUTES = ['npm', 'crx', 'whl', 'applescript', 'cargo.toml', 'chm', 'dmg', 'dockerfile', 'markdown', 'elf']


def prepare_route(args, route):
    root = args.output/route
    root.mkdir(parents=True, exist_ok=True)
    original = root/'original'
    if (original/'benchmark.json').exists():
        return
    source = args.source/'filetypes'/route
    previous = Path('out/experiments/next-model-tuneup-20261027')/route
    if route in {'markdown', 'whl'} and (previous/'prepared.json').exists():
        for name in ('original', 'train', 'dev', 'prepared.json', 'extra', 'extra-ready.json'):
            target = previous/name
            if target.exists() and not (root/name).exists():
                (root/name).symlink_to(target.resolve(), target_is_directory=target.is_dir())
        return
    if (source/'benchmark.json').exists() and list((source/'models').glob('seed_*.txt')):
        original.mkdir(exist_ok=True)
        for name in ('models', 'benchmark.json', 'feature_spec.json', 'training_provenance.json'):
            path = source/name
            if path.is_dir():
                shutil.copytree(path, original/name, dirs_exist_ok=True)
            elif path.exists():
                shutil.copy2(path, original/name)
        return
    # A removed/failed specialist has no current model to compare. Build a
    # research-only vocabulary on canonical training rows, retaining all labels.
    rows = []
    counts = {p: {'bad': 0, 'good': 0} for p in ('train', 'dev')}
    with data._connect(args.db, repeatable_read=True) as conn:
        with conn.cursor(name='regression_new_route') as cursor:
            cursor.itersize = 10000
            cursor.execute('SELECT id, sha256, canonical_sha256, label FROM samples WHERE '
                           + data.LABELED_WHERE + ' AND id<=%s AND file_type=%s ORDER BY id',
                           (args.max_id, route))
            for rid, sha, canonical, label in cursor:
                partition = data.partition_of(canonical or sha)
                if partition == 'test':
                    continue
                counts[partition][label] += 1
                if partition == 'train':
                    rows.append((int(rid), int(label == 'bad')))
    study.write_json(root/'support.json', counts)
    if min(counts['train'].values()) < 4:
        raise ValueError(f'Insufficient training classes for a new specialist: {counts}')
    env = {'COLLIMATOR_MIN_SAMPLE_SCORE': '0', **tune.FEATURES['metadata']}
    original.mkdir(exist_ok=True)
    with _temporary_feature_env(env):
        spec = features.build_vocab_from_db(args.db, rows, n_workers=args.workers,
                                           checkpoint_dir=root/'bootstrap-vocabulary')
    spec.save(original/'feature_spec.json')
    config = train.TrainConfig(learner='azoth', device='cpu', n_folds=0, n_estimators=200,
        max_depth=6, num_leaves=16, min_child_samples=10, min_child_weight=1,
        max_delta_step=5., scale_pos_weight_mult=.25, early_stopping_rounds=0,
        hard_negative_fraction=0., num_threads=args.threads)
    study.write_json(original/'benchmark.json', {'kind':'filetype', 'name':route,
        'file_types':[route], 'train_config':asdict(config), 'feature_env':env,
        'min_malware_training_score':0, 'n_features':spec.total_features,
        'training_partitions':['train'], 'research_origin':'new specialist; absent from current bundle',
        'bootstrap_vocabulary':'canonical training rows only; no dev or locked-test rows'})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=Path('out/experiments/deploy-regression-tuneup-20261028'))
    p.add_argument('--source', type=Path, default=Path('out/models/azoth'))
    p.add_argument('--routes', nargs='+', default=ROUTES)
    p.add_argument('--db', default='postgres://hopper@localhost:5432/hopper')
    p.add_argument('--max-id', type=int, default=6309383805)
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--threads', type=int, default=8)
    p.add_argument('--gate', action='store_true')
    args = p.parse_args()
    args.selection_objective = 'low-fp'
    args.allow_new_specialists = True
    args.output.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    study.write_json(args.output/'work-plan.json', {'routes':args.routes,'max_id':args.max_id,
        'selection':'Selection-only recall at zero FP, then one FP, then AP; assessment reserved until choices freeze.',
        'cohort_caveat':'Historical deployed gate reports use a different corpus snapshot; those numbers identify regressions, not a matched-cohort training objective.',
        'publication':'Individual research and full refits, then isolated deployment gates. No automatic publication.'})
    statuses = []
    completed = []
    for route in args.routes:
        LOG.info('START route %s', route)
        try:
            prepare_route(args, route)
            tune.run_route(args, route)
            refit(args.output/route, args.threads)
            completed.append(route)
            statuses.append({'route':route,'status':'refit_complete'})
        except Exception as exc:
            LOG.exception('Route failed: %s', route)
            statuses.append({'route':route,'status':'failed','error':str(exc)})
        study.write_json(args.output/'status.json', statuses)
        gc.collect()
    if args.gate and completed:
        subprocess.run([sys.executable, 'scripts/azoth_tuneup_gates.py', '--root', str(args.output),
                        '--source', str(args.source), '--routes', *completed], check=True)
    if any(r['status']=='failed' for r in statuses):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
