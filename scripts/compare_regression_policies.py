#!/usr/bin/env python3
"""Apply saved generation policies to row-version-verified matched test scores.

No thresholds are fitted. Cross-route joins require identical evaluation digests
and labels, in addition to the paired old/new prediction contract of each input.
"""
import argparse
import concurrent.futures
import hashlib
import json
import logging
from pathlib import Path

import numpy as np

from collimator import cache_identity, data, policy
from tune_regressed_models import fingerprint, freeze


def _refetch_evaluation_fingerprints(db, rows):
    """Read only PostgreSQL version metadata; report JSON is unnecessary."""
    labels = dict(rows)
    if data._is_pg(db):
        with data._connect(db) as conn:
            versions = conn.execute(
                'SELECT id, xmin::text FROM samples WHERE id = ANY(%s) '
                'AND cleave_result IS NOT NULL', ([rid for rid, _ in rows],))
            return {int(rid): cache_identity.evaluation_row_digest(
                [int(rid), version, {0: 'good', 1: 'bad'}[labels[int(rid)]]])
                for rid, version in versions}
    reports = data.fetch_cleave_results(db, [rid for rid, _ in rows], evaluation_labels=labels)
    return {rid: report['evaluation_digest'] for rid, report in reports.items()}


def report_fingerprints(root, db):
    """Recover row-version hashes and prove the original evaluation identity.

    PostgreSQL hashes bind ID, xmin and the selected label. Matching versions
    prove the same row; a mismatch cannot distinguish report from other updates.
    """
    expected = json.loads((root / 'cohort.json').read_text())['paired_input_sha256']
    with np.load(root / 'predictions.npz') as values:
        ids, labels = values['ids'], values['labels']
    identity = {'predictions': fingerprint(root / 'predictions.npz'), 'cohort': expected}
    target = root / 'verified-report-fingerprints.npz'
    marker = root / 'verified-report-fingerprints.json'
    if marker.exists():
        saved = json.loads(marker.read_text())
        if saved['identity'] != identity or saved['array_sha256'] != fingerprint(target):
            raise ValueError(f'Fingerprint inputs changed: {root}')
        with np.load(target) as values:
            if not np.array_equal(values['ids'], ids):
                raise ValueError('Fingerprint identities changed')
            return values['fingerprints']
    found = {}
    for path in sorted((root / 'extraction-chunks').glob('*/complete.json')):
        chunk = json.loads(path.read_text())
        hashes = bytes.fromhex(chunk['report_fingerprints'])
        if len(hashes) != 32 * len(chunk['kept']):
            raise ValueError(f'Invalid report digest array: {path}')
        for i, row in enumerate(chunk['kept']):
            found[int(row[0])] = hashes[32 * i:32 * (i + 1)]
    missing = [(int(rid), int(y)) for rid, y in zip(ids, labels, strict=True)
               if int(rid) not in found]
    batch_size = 2000 if data._is_pg(db) else 256
    for start in range(0, len(missing), batch_size):
        rows = missing[start:start + batch_size]
        digests = _refetch_evaluation_fingerprints(db, rows)
        for rid, _ in rows:
            if rid not in digests:
                raise ValueError(f'Original evaluation row disappeared: {rid}')
            found[rid] = digests[rid]
    joined = b''.join(found[int(rid)] for rid in ids)
    if hashlib.sha256(joined).hexdigest() != expected:
        raise ValueError(f'Evaluated row versions changed; rescore before policy comparison: {root}')
    hashes = np.frombuffer(joined, dtype='V32')
    temporary = target.with_suffix('.tmp.npz')
    np.savez(temporary, ids=ids, fingerprints=hashes)
    temporary.replace(target)
    marker.write_text(json.dumps({'identity': identity, 'array_sha256': fingerprint(target),
        'recovered_from_chunks': len(ids) - len(missing),
        'refetched_and_content_verified': len(missing)}, indent=2) + '\n')
    logging.info('%s: verified %d report fingerprints (%d refetched)', root, len(ids), len(missing))
    return hashes


def matched_positions(tables):
    """Return only rows with the same labels and bytes in every route score set."""
    common = None
    for table in tables.values():
        ids = table['ids']
        if len(ids) and np.any(ids[1:] <= ids[:-1]):
            raise ValueError('Paired identities must be sorted and unique')
        common = ids if common is None else np.intersect1d(common, ids, assume_unique=True)
    positions = {name: np.searchsorted(table['ids'], common) for name, table in tables.items()}
    reference = next(iter(tables))
    ref_positions = positions[reference]
    labels = tables[reference]['labels'][ref_positions]
    digests = tables[reference]['fingerprints'][ref_positions]
    valid = np.ones(len(common), dtype=bool)
    for name, table in tables.items():
        pos = positions[name]
        valid &= (table['labels'][pos] == labels) & (table['fingerprints'][pos] == digests)
    return common[valid], {name: pos[valid] for name, pos in positions.items()}, int((~valid).sum())


def decision_metrics(labels, margin):
    positive = labels == 1
    hit = margin >= 0
    tp, fp = int((hit & positive).sum()), int((hit & ~positive).sum())
    malware, benign = int(positive.sum()), int((~positive).sum())
    return {'rows': len(labels), 'malware': malware, 'benign': benign,
            'tp': tp, 'fp': fp, 'fn': malware - tp, 'tn': benign - fp,
            'recall': tp / malware if malware else None,
            'fpr': fp / benign if benign else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--paired', type=Path, required=True)
    parser.add_argument('--general', type=Path, required=True)
    parser.add_argument('--native', type=Path, required=True)
    parser.add_argument('--dmg', type=Path, required=True)
    parser.add_argument('--refreshed-pairs', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--previous-bundle', type=Path, default=Path('/home/t/src/azoth'))
    parser.add_argument('--nightly-bundle', type=Path,
                        default=Path('/home/t/.local/share/atomdrift/scan/models/azoth'))
    parser.add_argument('--db', default='postgres://hopper@localhost:5432/hopper')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--levels', type=int, nargs='+', default=[0, 1, 25, 50, 100, 1000])
    parser.add_argument('--fingerprints-only', action='store_true')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    args.output.mkdir(parents=True, exist_ok=True)
    routes = [r['route'] for r in json.loads((args.paired / 'status.json').read_text())
              if r['route'].startswith('filetypes/')]
    roots = {str(p.parent.relative_to(args.paired / 'paired')): p.parent
             for p in (args.paired / 'paired').rglob('predictions.npz')}
    roots['filetypes/dmg'] = args.dmg / 'paired/filetypes/dmg'
    roots['general'] = args.general / 'paired/general'
    roots['filegroups/native'] = args.native / 'paired/filegroups/native'
    refreshed = {}
    if args.refreshed_pairs:
        refreshed = {str(p.parent.relative_to(args.refreshed_pairs / 'paired')): p.parent
                     for p in (args.refreshed_pairs / 'paired').rglob('predictions.npz')}
        roots.update(refreshed)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = {pool.submit(report_fingerprints, root, args.db): route
                   for route, root in roots.items() if (root / 'predictions.npz').exists()}
        for future in concurrent.futures.as_completed(pending):
            future.result()
    if args.fingerprints_only:
        return 0
    missing = [route for route, root in roots.items() if not (root / 'predictions.npz').exists()]
    if missing:
        raise ValueError(f'Paired predictions still missing: {missing}')
    configs, policies = {}, {}
    for generation, source in [('previous', args.previous_bundle), ('nightly', args.nightly_bundle)]:
        configs[generation] = json.loads((source / 'config.json').read_text())
        policies[generation] = json.loads((source / 'route_policies.json').read_text())
        if policies[generation].get('score_space') != 'raw':
            raise ValueError('Policy comparison requires raw score space')
        freeze(args.output / f'{generation}-config.json', configs[generation])
        freeze(args.output / f'{generation}-policies.json', policies[generation])
    tables = {}
    for route, root in roots.items():
        with np.load(root / 'predictions.npz') as values:
            tables[route] = {k: values[k] for k in ('ids', 'labels', 'current', 'candidate')}
        tables[route]['fingerprints'] = report_fingerprints(root, args.db)
        generation_root = (args.refreshed_pairs if route in refreshed else
                           args.general if route == 'general' else args.native
                           if route == 'filegroups/native' else args.dmg
                           if route == 'filetypes/dmg' else args.paired)
        for generation, source in [('previous', args.previous_bundle), ('nightly', args.nightly_bundle)]:
            saved = generation_root / 'generations' / generation / route
            if (cache_identity.model_revision(saved) != cache_identity.model_revision(source / route)
                    or fingerprint(saved / 'feature_spec.json') != fingerprint(source / route / 'feature_spec.json')):
                raise ValueError(f'Policy/model generation mismatch: {generation}/{route}')
    results = []
    for route in sorted(routes):
        needed = {'general', route}
        for value in policies.values():
            needed.update(value['routes'].get(route, {}).get('models', []))
        if needed - tables.keys():
            raise ValueError(f'Missing policy inputs: {sorted(needed - tables.keys())}')
        selected = {name: tables[name] for name in sorted(needed)}
        ids, positions, mismatched = matched_positions(selected)
        if not len(ids):
            raise ValueError(f'No content-identical cross-route rows: {route}')
        labels = tables[route]['labels'][positions[route]]
        scores = {generation: {name: tables[name][key][positions[name]] for name in needed}
                  for generation, key in [('previous', 'current'), ('nightly', 'candidate')]}
        levels = []
        for level in args.levels:
            cells = {}
            for model_generation in scores:
                for policy_generation in policies:
                    applicable = policies[policy_generation]['routes'][route]['models']
                    policy_scores = {name: scores[model_generation][name] for name in applicable}
                    margins = policy.routed_margin(policy_scores, configs[policy_generation],
                        policies[policy_generation], route.removeprefix('filetypes/'), level, len(ids))
                    cells[f'{model_generation}_models__{policy_generation}_policy'] = decision_metrics(labels, margins)
            old = cells['previous_models__previous_policy']
            new = cells['nightly_models__nightly_policy']
            levels.append({'level': level, 'cells': cells, 'tp_delta': new['tp'] - old['tp'],
                           'fp_delta': new['fp'] - old['fp'],
                           'recall_delta': new['recall'] - old['recall'] if old['recall'] is not None else None})
        results.append({'route': route, 'rows': len(ids), 'source_rows': len(tables[route]['ids']),
                        'excluded_cross_route_content_or_label_changes': mismatched,
                        'input_ids_sha256': hashlib.sha256(ids.tobytes()).hexdigest(), 'levels': levels})
        logging.info('%s: matched policy comparison on %d rows', route, len(ids))
    freeze(args.output / 'comparison.json', {'purpose': 'Saved-policy diagnosis; no fitting or promotion',
        'caveats': ['Only content-identical cross-route rows included; exclusions reported.',
                    'Crossed model/policy cells are diagnostic counterfactuals, not recalibrated candidates.',
                    'Python raw scores; known scanner feature mismatches assessed separately.'],
        'levels': args.levels, 'routes': results})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
