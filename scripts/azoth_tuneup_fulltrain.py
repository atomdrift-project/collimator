#!/usr/bin/env python3
"""Refit frozen specialist research choices and emit auditable gate inputs."""
from __future__ import annotations

import argparse
from dataclasses import asdict, fields
import json
import logging
from pathlib import Path
import shutil

import lightgbm as lgb
import numpy as np
import onnxruntime as ort

import azoth_specialist_tuneup as tune
import azoth_portable_stability as study
from azoth_specialist_suite import _seed_health_failure
from collimator import bundle, cache_identity, export, features, train


def refit(root: Path, threads: int):
    research = json.loads((root/'candidate/research.json').read_text())
    selected = research['candidate_config']
    dest = root/'candidate-fulltrain'
    if (dest/'complete.json').exists():
        return
    dest.mkdir(exist_ok=True)
    original = json.loads((root/'original/benchmark.json').read_text())
    if selected['feature_spec'].startswith('features/'):
        matrix_root = root/Path(selected['feature_spec']).parent
        training, dev = tune.load(matrix_root, 'train'), tune.load(matrix_root, 'dev')
    else:
        training, dev = tune.load(root, 'train'), tune.load(root, 'dev')
        if selected['training_pool'] == 'all_labeled':
            training = tune.with_extra(root, training)
    spec = features.FeatureSpec.load(root/selected['feature_spec'])
    shutil.copy2(root/selected['feature_spec'], dest/'feature_spec.json')
    keys = {f.name for f in fields(train.TrainConfig)}
    settings = {**original['train_config'], **selected['training_overrides'],
                'num_threads': threads, 'device': 'cpu', 'n_folds': 0}
    seeds = research['winner']['seeds']
    attempts, predictions, native = [], [], []
    (dest/'models').mkdir(exist_ok=True)
    for seed in seeds:
        config = train.TrainConfig(**{k:v for k,v in settings.items() if k in keys and k != 'seed'}, seed=seed)
        marker = dest/f'seed_{seed}.json'
        txt = dest/'models'/f'seed_{seed}.txt'
        onnx = txt.with_suffix('.onnx')
        if marker.exists():
            attempt = json.loads(marker.read_text())
            if attempt['config'] != asdict(config):
                raise ValueError('Refusing to resume a changed full-training configuration')
        else:
            result = train.train(training[0], training[1], config,
                                 feature_names=spec.feature_names, sample_file_types=training[3])
            reason = _seed_health_failure(result, min_roc_auc=.5)
            if reason:
                raise ValueError(f'Frozen selected seed {seed} failed full-training health gate: {reason}')
            export.save_model(result.model, txt)
            attempt = {'seed': seed, 'accepted': True, 'metrics': result.metrics,
                       'split_summary': result.split_summary, 'config': asdict(config)}
            study.write_json(marker, attempt)
        attempts.append(attempt)
        booster = lgb.Booster(model_file=str(txt))
        native.append(study.predict(booster, dev[0], threads)[2])
        opts = ort.SessionOptions(); opts.intra_op_num_threads = threads; opts.inter_op_num_threads = 1
        session = ort.InferenceSession(str(onnx), opts, providers=['CPUExecutionProvider'])
        name = session.get_inputs()[0].name
        predictions.append(np.concatenate([session.run(['probabilities'], {name:dev[0][i:i+512].toarray().astype(np.float32)})[0][:,1]
                                           for i in range(0, len(dev[1]), 512)]))
    actual, expected = np.mean(predictions, axis=0, dtype=np.float32), np.mean(native, axis=0, dtype=np.float32)
    error = float(np.max(np.abs(actual-expected)))
    if error > 1e-4:
        raise ValueError(f'Full-training ONNX parity failed: {error}')
    np.savez(dest/'dev_predictions.npz', probability=actual, labels=dev[1], ids=dev[4])
    payload = {**original, 'output_dir':str(dest), 'model_path':str(bundle.primary_model_file(dest)),
               'spec_path':str(dest/'feature_spec.json'), 'training_partitions':['train'], 'score_space':'raw',
               'n_seed_models':len(seeds), 'train_rows':len(training[1]),
               'train_malware':int(training[1].sum()), 'train_benign':int((training[1]==0).sum()),
               'n_features':spec.total_features, 'feature_env':selected['feature_env'],
               'feature_spec_policy':'research_selected', 'feature_mask':None,
               'min_malware_training_score':selected['min_malware_training_score'],
               'train_config':attempts[0]['config'], 'train_metrics':attempts[0]['metrics'],
               'benchmark_rows':0, 'benchmark_malware':0, 'benchmark_benign':0,
               'metrics':{'skipped':'benchmark'}, 'levels':[],
               'seed_health':{'target_members':len(seeds),'retry_budget':0,'min_roc_auc':.5,
                              'accepted_seeds':seeds,'attempts':attempts}}
    study.write_json(dest/'benchmark.json', payload)
    cache_identity.write_training_provenance(dest)
    study.write_json(dest/'complete.json', {'research_choice':research['winner'],
        'candidate_config':selected,'max_onnx_difference':error,'dev_metrics':study.metrics(dev[1],actual),
        'deployment_status':'Full training complete; deployment gates pending'})
    logging.info('Full training complete: %s; ONNX max difference %.3g', root.name, error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('out/experiments/specialist-tuneup-20261027'))
    parser.add_argument('--routes', nargs='+', required=True)
    parser.add_argument('--threads', type=int, default=4)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    for route in args.routes:
        refit(args.root/route, args.threads)


if __name__ == '__main__':
    main()
