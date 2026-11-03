#!/usr/bin/env python3
"""Replay saved paired feature matrices using deployed ensemble arithmetic.

Original predictions and receipts remain intact. No database reads, feature
extraction, training, selection, or installation take place.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import logging
import multiprocessing
import os
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from collimator import bundle, features
from evaluate_recovery_policy_matches import require_prediction_source
from tune_regressed_models import fingerprint, freeze

CONTRACT = 'runtime_f64_sum_f32_result_v1'


def replay(task):
    directory, columns, threads = task
    root = Path(directory)
    os.environ['COLLIMATOR_ONNX_THREADS'] = str(threads)
    plan = json.loads((root/'plan.json').read_text())
    if plan.get('prediction_contract') == CONTRACT:
        return {'root': str(root), 'status': 'already_runtime_contract'}
    sources = {column: Path(plan['entry'][column]) for column in columns}
    for column, source in sources.items():
        require_prediction_source(root, source, column)
    identity = {'plan_sha256': fingerprint(root/'plan.json'),
                'original_predictions_sha256': fingerprint(root/'predictions.npz'),
                'columns': columns, 'prediction_contract': CONTRACT}
    output, marker = root/'runtime-predictions.npz', root/'runtime-predictions.json'
    if marker.exists():
        saved = json.loads(marker.read_text())
        if saved['identity'] != identity or saved['output_sha256'] != fingerprint(output):
            raise ValueError(f'Runtime replay inputs changed: {root}')
        return {'root': str(root), 'status': 'cached', **saved['comparison']}
    with np.load(root/'predictions.npz') as values:
        metadata = {k: values[k] for k in ('ids', 'labels', 'filetypes')}
        original = {column: values[column] for column in columns}
    chunks = sorted((root/'extraction-chunks').glob('*/complete.json'))
    if not chunks:
        raise ValueError(f'No saved matrices for runtime replay: {root}')
    predictors = {key: bundle.Ensemble.load_bundle(path) for key, path in sources.items()}
    specs = {key: features.FeatureSpec.load(path/'feature_spec.json') for key, path in sources.items()}
    predictions = {column: np.empty(len(metadata['ids']), dtype=np.float32) for column in columns}
    offset, digest = 0, hashlib.sha256()
    for i, path in enumerate(chunks):
        chunk = json.loads(path.read_text())
        kept = chunk['kept']
        end = offset + len(kept)
        if (not np.array_equal(metadata['ids'][offset:end], [r[0] for r in kept])
                or not np.array_equal(metadata['labels'][offset:end], [r[1] for r in kept])):
            raise ValueError(f'Replay row ordering or labels changed: {path}')
        digest.update(bytes.fromhex(chunk['report_fingerprints']))
        for column in columns:
            matrix_path = path.parent/(column+'.npz')
            if fingerprint(matrix_path) != chunk['matrices'][column]:
                raise ValueError(f'Replay matrix changed: {matrix_path}')
            matrix = sp.load_npz(matrix_path)
            if specs[column].standardized:
                matrix = features.standardize(matrix, specs[column])
            predictions[column][offset:end] = predictors[column].predict_proba(matrix)
        offset = end
        if i % 500 == 0:
            logging.info('%s: runtime replay %d/%d rows', root, offset, len(metadata['ids']))
    if offset != len(metadata['ids']):
        raise ValueError(f'Incomplete replay matrices: {root}')
    if digest.hexdigest() != json.loads((root/'cohort.json').read_text())['paired_input_sha256']:
        raise ValueError(f'Replay report versions changed: {root}')
    temporary = output.with_suffix('.tmp.npz')
    np.savez(temporary, **metadata, **predictions)
    temporary.replace(output)
    comparison = {column: {'changed_scores': int(np.sum(predictions[column] != original[column])),
                           'max_absolute_difference': float(np.max(np.abs(
                               predictions[column].astype(float)-original[column]), initial=0))}
                  for column in columns}
    freeze(marker, {'identity': identity, 'output_sha256': fingerprint(output), 'comparison': comparison})
    return {'root': str(root), 'status': 'replayed', **comparison}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--parallelism', type=int, default=2)
    p.add_argument('--threads', type=int, default=2)
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    selected = {}
    for entry in json.loads(args.manifest.read_text())['scores']:
        if 'predictions' in entry:
            selected.setdefault(entry['predictions'], set()).add(entry['column'])
    # Work on the largest source first so it overlaps the smaller routes.
    tasks = [(root, sorted(columns), args.threads) for root, columns in selected.items()]
    tasks.sort(key=lambda task: -(Path(task[0])/'predictions.npz').stat().st_size)
    with ProcessPoolExecutor(max_workers=args.parallelism,
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(replay, tasks))
    freeze(args.output, {'prediction_contract': CONTRACT, 'results': results})
    logging.info('Replayed or verified %d paired score sources', len(results))


if __name__ == '__main__':
    main()
