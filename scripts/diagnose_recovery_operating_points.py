#!/usr/bin/env python3
"""Describe frozen recovery winners at development-fitted standalone thresholds.

This does not select winners, fit models, or approve deployment. Routed ensemble
confirmation remains separate. Existing assessment observations are reused only
for descriptive comparison, not claimed as a new independent confirmation.
"""
import argparse
import gc
import hashlib
import json
import logging
from pathlib import Path

import numpy as np

import azoth_portable_stability as study
import azoth_regression_recovery as recovery
from collimator import policy, thresholds
from tune_regressed_models import freeze


def counts(y, hit):
    return {'malware': int(np.sum(y == 1)), 'benign': int(np.sum(y == 0)),
            'tp': int(np.sum(hit & (y == 1))), 'fp': int(np.sum(hit & (y == 0)))}


def fixed_points(y, p, selection, filetypes, levels):
    """Calibrate only on selection benigns, then evaluate frozen f32 decisions."""
    benign = np.asarray(p[selection & (y == 0)], dtype=np.float64)
    if len(benign) < 50:
        return {'status': 'insufficient calibration benigns', 'benign': len(benign)}
    assessment = ~selection
    result = []
    for level in levels:
        threshold, method = thresholds.quantile_severity_threshold(benign, level / 100.)
        decision = {'thresholds': {'model': threshold}}
        hit = policy.margin({'model': p}, decision, len(y)) >= 0
        result.append({'level': level, 'threshold': threshold, 'method': method,
            'selection': counts(y[selection], hit[selection]),
            'assessment': counts(y[assessment], hit[assessment]),
            'filetypes': {str(ft): counts(y[mask], hit[mask])
                          for ft in np.unique(filetypes[assessment])
                          if (mask := assessment & (filetypes == ft)).any()}})
    return {'status': 'evaluated', 'levels': result}


def metadata(root, partition):
    directory = root / 'current' / partition
    return tuple(np.load(directory / (name + '.npy'), mmap_mode='r')
                 for name in ('y', 'bucket', 'filetype', 'ids'))


def predictions(root, entry, dev_matrix, threads):
    if entry['variant'] == 'saved':
        if entry['layout'] != 'current' or dev_matrix is None:
            raise ValueError('Saved predictor evaluation requires held-out current-layout dev rows')
        members = recovery.saved_predictions(root, 'current', dev_matrix, threads)
    else:
        members = {}
        for seed in entry['seeds']:
            path = root / 'fits' / entry['layout'] / 'results' / f"{entry['variant']}_seed{seed}" / 'predictions.npz'
            with np.load(path) as values:
                members[seed] = values['probability']
    return np.mean([members[s] for s in entry['seeds']], axis=0, dtype=np.float32)


def evaluate(root, output, levels, threads):
    frozen_path = root / 'frozen-winner.json'
    frozen = json.loads(frozen_path.read_text())
    complete = json.loads((root / 'complete.json').read_text())
    mode = frozen['mode']
    dy, db, df, dids = metadata(root, 'dev')
    matrix = None
    if mode == 'dev_halves':
        y, selection, ft, ids = dy, db < .5, df, dids
        reference = frozen['comparisons'][0]
        matrix = study.load_matrix(root / 'current', 'dev')[0]
    else:
        ty, tb, tf, tids = metadata(root, 'train')
        selected = tb >= .75
        y, ft, ids = np.r_[ty[selected], dy], np.r_[tf[selected], df], np.r_[tids[selected], dids]
        selection = np.r_[np.ones(selected.sum(), dtype=bool), np.zeros(len(dy), dtype=bool)]
        reference = next(r for r in frozen['comparisons'] if r['key'] == 'current/control')
    reports = {}
    for name, entry in [('reference', reference), ('winner', frozen['winner'])]:
        if name == 'winner' and entry['key'] == reference['key']:
            reports[name] = reports['reference']
            continue
        p = predictions(root, entry, matrix, threads)
        if len(p) != len(y):
            raise ValueError('Frozen prediction/label shape mismatch')
        actual = study.metrics(y[selection], p[selection])
        expected = entry['selection']
        if (actual['rows'] != expected['rows'] or actual['malware'] != expected['malware']
                or not np.isclose(actual['ap'], expected['ap'], rtol=0, atol=1e-10)):
            raise ValueError(f'Cannot reproduce frozen selection scores: {root}/{entry["key"]}')
        reports[name] = {'key': entry['key'],
            'probability_sha256': hashlib.sha256(p.tobytes()).hexdigest(),
            **fixed_points(y, p, selection, ft, levels)}
    result = {'route': complete['route'], 'study': str(root.resolve()),
              'frozen_winner_sha256': hashlib.sha256(frozen_path.read_bytes()).hexdigest(),
              'ids_sha256': hashlib.sha256(ids.tobytes()).hexdigest(),
              'mode': mode, 'prior_status': complete['status'], 'reports': reports,
              'scope': 'Standalone threshold diagnosis of a previously frozen winner. No ensemble routing, new selection, full refit, or installation approval.'}
    destination = output / complete['route']
    destination.mkdir(parents=True, exist_ok=True)
    freeze(destination / 'comparison.json', result)
    logging.info('%s: %s vs %s', complete['route'], reference['key'], frozen['winner']['key'])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--studies', type=Path, nargs='+', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--levels', nargs='+', type=int, default=[0, 25, 50, 100])
    parser.add_argument('--threads', type=int, default=2)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    roots = [p.parent for study_root in args.studies for p in study_root.rglob('frozen-winner.json')
             if (p.parent / 'complete.json').exists()]
    routes = [json.loads((p / 'complete.json').read_text())['route'] for p in roots]
    if len(routes) != len(set(routes)):
        raise ValueError('Use one completed study per route')
    for root in roots:
        evaluate(root, args.output, args.levels, args.threads)
        gc.collect()


if __name__ == '__main__':
    main()
