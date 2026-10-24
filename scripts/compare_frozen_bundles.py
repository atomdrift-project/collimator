#!/usr/bin/env python3
"""Compare saved bundles on identical reports/labels without refitting policies.

Capture the source run's test rows plus PE dev rows, snapshot the models and
policies, and fetch reports in one read-only database snapshot. Replay is local.
Labels and canonical partitions are frozen from the source run, not refreshed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
from pathlib import Path
import shutil
import sqlite3
import time

import numpy as np

from collimator import bundle, data, features, policy
import azoth_oof_score_routes as scoring


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def cohort_mask(buckets, filetypes):
    return ((buckets < data.TEST_BUCKET_MAX) |
            ((buckets < data.DEV_BUCKET_MAX) & (filetypes == 'pe')))


def route_mask(route, filetypes, config):
    if route == 'general':
        return np.ones(len(filetypes), dtype=bool)
    kind, name = route.split('/', 1)
    if kind == 'filetypes':
        return filetypes == name
    if kind == 'filegroups':
        mapping = config['filetype_to_group']
        return np.array([mapping.get(str(ft)) == name for ft in filetypes])
    raise ValueError(f'unknown route kind: {route}')


def align_predictions(expected_ids, result):
    order = np.argsort(result['row_ids'])
    if not np.array_equal(result['row_ids'][order], expected_ids):
        raise ValueError('extraction lost, duplicated, or changed cohort row IDs')
    probabilities = result['probs'][order]
    if not np.isfinite(probabilities).all():
        raise ValueError('model returned non-finite probabilities')
    return probabilities


def capture(args):
    out = args.capture
    out.mkdir(parents=True, exist_ok=False)
    table_path = args.source / 'score_table.npz'
    general_path = args.source / 'general/threshold_scores.npz'
    source_hashes = {str(p): digest(p) for p in (table_path, general_path)}
    with np.load(table_path) as table, np.load(general_path) as general:
        buckets, filetypes = table['sha_bucket'], table['file_types']
        mask = cohort_mask(buckets, filetypes)
        ids = table['row_ids'][mask]
        order = np.argsort(ids)
        ids = ids[order]
        if len(np.unique(ids)) != len(ids):
            raise ValueError('duplicate source row IDs')
        g_ids = general['row_ids']
        g_order = np.argsort(g_ids)
        positions = np.searchsorted(g_ids[g_order], ids)
        if np.any(positions >= len(g_ids)) or not np.array_equal(g_ids[g_order][positions], ids):
            raise ValueError('source general cache does not cover score table')
        metadata = dict(row_ids=ids, labels=table['labels'][mask][order],
                        file_types=filetypes[mask][order], sha_bucket=buckets[mask][order])
        metadata['canonical_shas'] = general['canonical_shas'][g_order[positions]]
        if not np.array_equal(general['labels'][g_order[positions]], metadata['labels']):
            raise ValueError('source general cache labels disagree with score table')
        metadata['sha256'] = np.full(len(ids), '', dtype='<U64')
        metadata['scores'] = np.zeros(len(ids), dtype=np.int32)
    if any(digest(Path(p)) != h for p, h in source_hashes.items()):
        raise ValueError('source scores changed during capture')
    names = []
    for assignment in args.bundle:
        name, source = assignment.split('=', 1)
        if not name or not all(c.isalnum() or c in '_-' for c in name) or name in names:
            raise ValueError('bundle names must be unique simple identifiers')
        names.append(name)
        root = Path(source)
        config = json.loads((root / 'config.json').read_text())
        if config.get('score_space') not in (None, 'raw'):
            raise ValueError('comparison requires raw-score bundles')
        paths = [root / 'config.json', root / 'route_policies.json']
        for record in config['models']:
            route = root / record['route']
            if (route / 'calibrator.json').exists():
                raise ValueError('this raw-score replay does not support legacy calibrators')
            if json.loads((route / 'feature_spec.json').read_text()).get('standardized'):
                raise ValueError('this replay requires unstandardized feature specifications')
            files = bundle.model_files(route)
            if not files:
                raise ValueError(f'missing model: {route}')
            paths.extend([route / 'feature_spec.json', *files])
        fingerprints = {str(p): digest(p) for p in paths}
        for p in paths:
            target = out / 'bundles' / name / p.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, target)
            if digest(target) != fingerprints[str(p)]:
                raise ValueError('bundle changed during snapshot')
        if any(digest(p) != fingerprints[str(p)] for p in paths):
            raise ValueError('bundle changed during snapshot')
    # One repeatable-read transaction freezes all reports, not one per batch.
    ids = metadata['row_ids'].tolist()
    changed_labels = []
    with data._connect(args.db, repeatable_read=True) as source, sqlite3.connect(out / 'reports.sqlite') as db:
        if data._is_pg(args.db):
            source.execute('SET TRANSACTION READ ONLY')
        db.execute('CREATE TABLE samples (id INTEGER PRIMARY KEY, cleave_result TEXT, '
                   'formula TEXT, elements TEXT, score INTEGER, mtime TEXT)')
        for start in range(0, len(ids), 128):
            batch = ids[start:start + 128]
            params = [batch] if data._is_pg(args.db) else batch
            where = 'id = ANY(%s)' if data._is_pg(args.db) else 'id IN (' + ','.join('?' for _ in batch) + ')'
            rows = source.execute('SELECT id, cleave_result, formula, elements, score, mtime, label, sha256 '
                                  'FROM samples WHERE ' + where, params).fetchall()
            if {r[0] for r in rows if r[1] is not None} != set(batch):
                raise ValueError('capture lost a selected report; no partial cohort accepted')
            expected = dict(zip(batch, metadata['labels'][start:start+len(batch)], strict=True))
            for rid, report, formula, elements, score, mtime, label, sha in rows:
                index = int(np.searchsorted(metadata['row_ids'], rid))
                metadata['sha256'][index] = str(sha)
                metadata['scores'][index] = int(score or 0)
                if str(label) != {0: 'good', 1: 'bad'}[int(expected[rid])]:
                    changed_labels.append(int(rid))
                db.execute('INSERT INTO samples VALUES (?,?,?,?,?,?)', (
                    rid, json.dumps(report) if isinstance(report, dict) else report,
                    formula, elements, score, str(mtime) if mtime else ''))
            db.commit()
            if start % 1024 == 0:
                print(f'captured {start+len(batch)}/{len(ids)} reports', flush=True)
    np.savez_compressed(out / 'cohort.npz', **metadata)
    hashes = {str(p.relative_to(out)): digest(p) for p in sorted(out.rglob('*')) if p.is_file()}
    (out / 'manifest.json').write_text(json.dumps(dict(
        source=str(args.source.resolve()), source_hashes=source_hashes, bundles=names,
        rows=len(ids), hashes=hashes, live_labels_differ_from_frozen=changed_labels,
        labels_origin='source score table; retained for all bundles',
    ), indent=2) + '\n')
    print(f'capture complete: {len(ids)} rows; {len(changed_labels)} live label changes', flush=True)


def verify_capture(root):
    manifest = json.loads((root / 'manifest.json').read_text())
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p != root / 'manifest.json'}
    if actual != set(manifest['hashes']):
        raise ValueError('captured input file set changed')
    for name, expected in manifest['hashes'].items():
        if digest(root / name) != expected:
            raise ValueError(f'captured input changed: {name}')
    return manifest


def decisions(table, config, policies, level):
    hit = np.zeros(len(table['labels']), dtype=bool)
    for ft in np.unique(table['file_types']):
        mask = table['file_types'] == ft
        scores = {str(route): values[mask] for route, values in zip(table['route_names'], table['scores'], strict=True)}
        hit[mask] = policy.routed_margin(scores, config, policies, str(ft), level, int(mask.sum())) >= 0
    return hit


def counts(labels, hit):
    pos = labels == 1
    tp, fp = int((hit & pos).sum()), int((hit & ~pos).sum())
    return dict(malware=int(pos.sum()), benign=int((~pos).sum()), tp=tp, fp=fp,
                recall=tp / int(pos.sum()) if pos.any() else None)


def replay(args):
    manifest = verify_capture(args.capture)
    if args.name not in manifest['bundles']:
        raise ValueError('unknown captured bundle')
    args.output.mkdir(parents=True, exist_ok=False)
    with np.load(args.capture / 'cohort.npz') as archive:
        cohort = dict(archive)
    root = args.capture / 'bundles' / args.name
    config = json.loads((root / 'config.json').read_text())
    policies = json.loads((root / 'route_policies.json').read_text())
    names = [entry['route'] for entry in config['models']]
    scores = np.full((len(names), len(cohort['row_ids'])), np.nan, dtype=np.float32)
    started = time.monotonic()
    with features.MetadataExtractionPool(args.workers) as pool:
        for index, route in enumerate(names):
            selected = np.flatnonzero(route_mask(route, cohort['file_types'], config))
            if not len(selected):
                continue
            rows = [(int(cohort['row_ids'][i]), str(cohort['sha256'][i]), '', int(cohort['scores'][i]),
                     int(cohort['labels'][i]), str(cohort['canonical_shas'][i])) for i in selected]
            result = scoring._score_rows(args.capture / 'reports.sqlite', rows, root / route,
                                         workers=args.workers, worker_pool=pool)
            scores[index, selected] = align_predictions(cohort['row_ids'][selected], result)
            print(f'{args.name}: {route}: {len(selected)} rows', flush=True)
    table = {k: cohort[k] for k in ('row_ids', 'labels', 'file_types', 'sha_bucket')}
    table.update(route_names=np.array(names), scores=scores)
    hit = decisions(table, config, policies, args.level)
    np.savez_compressed(args.output / 'scores.npz', **table, hit=hit)
    test = table['sha_bucket'] < data.TEST_BUCKET_MAX
    result = dict(bundle=args.name, level=args.level, wall_seconds=time.monotonic()-started,
                  test=counts(table['labels'][test], hit[test]), filetypes={})
    for ft in np.unique(table['file_types'][test]):
        mask = test & (table['file_types'] == ft)
        result['filetypes'][str(ft)] = counts(table['labels'][mask], hit[mask])
    (args.output / 'result.json').write_text(json.dumps(result, indent=2)+'\n')
    verify_capture(args.capture)
    print(json.dumps({k:v for k,v in result.items() if k != 'filetypes'}), flush=True)


def compare(args):
    manifest = verify_capture(args.capture)
    args.output.mkdir(parents=True, exist_ok=False)
    with np.load(args.capture / 'cohort.npz') as archive:
        cohort = dict(archive)
    tables, configs, policies = {}, {}, {}
    report = dict(level=args.level, capture_manifest_sha256=digest(args.capture / 'manifest.json'),
                  bundles={}, paired_changes={}, pe_policy_crosscheck={})
    test = cohort['sha_bucket'] < data.TEST_BUCKET_MAX
    for name in manifest['bundles']:
        with np.load(args.results / name / 'scores.npz') as archive:
            table = dict(archive)
        for key in ('row_ids', 'labels', 'file_types', 'sha_bucket'):
            if not np.array_equal(table[key], cohort[key]):
                raise ValueError(f'{name}: {key} differs from frozen cohort')
        root = args.capture / 'bundles' / name
        config = json.loads((root / 'config.json').read_text())
        saved_policy = json.loads((root / 'route_policies.json').read_text())
        table['hit'] = decisions(table, config, saved_policy, args.level)
        tables[name], configs[name], policies[name] = table, config, saved_policy
        report['bundles'][name] = dict(
            calibration_fit_partition=config.get('fit_partition'),
            test=counts(table['labels'][test], table['hit'][test]), filetypes={})
        for ft in np.unique(cohort['file_types'][test]):
            mask = test & (cohort['file_types'] == ft)
            report['bundles'][name]['filetypes'][str(ft)] = counts(table['labels'][mask], table['hit'][mask])
    names = manifest['bundles']
    for i, left in enumerate(names):
        for right in names[i+1:]:
            a, b = tables[left]['hit'], tables[right]['hit']
            pair = {}
            for label, kind in ((1, 'malware'), (0, 'benign')):
                mask = test & (cohort['labels'] == label)
                pair[kind] = dict(left_only=int((mask & a & ~b).sum()),
                                  right_only=int((mask & b & ~a).sum()),
                                  both=int((mask & a & b).sum()), neither=int((mask & ~a & ~b).sum()))
            report['paired_changes'][f'{left}_vs_{right}'] = pair
    # Diagnostic counterfactuals only: no policy is fitted or selected here.
    for partition, partition_mask in (('test', test), ('dev', ~test)):
        mask = partition_mask & (cohort['file_types'] == 'pe')
        cross = report['pe_policy_crosscheck'][partition] = {}
        for model_name, table in tables.items():
            subset = {k: (v[:, mask] if k == 'scores' else v[mask] if k in
                      ('row_ids','labels','file_types','sha_bucket','hit') else v) for k,v in table.items()}
            cross[model_name] = {policy_name: counts(subset['labels'], decisions(
                subset, configs[policy_name], policies[policy_name], args.level)) for policy_name in names}
    report['limitations'] = [
        'Labels and partitions are frozen from the source run; reports are captured later in one DB snapshot.',
        'Calibration policies are unchanged; bundles calibrated on all partitions have test exposure.',
        'PE policy crosschecks are diagnostic counterfactuals, not selected replacement policies.',
        'This small test cohort cannot certify a 25-per-100M false-positive rate.',
    ]
    (args.output / 'comparison.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({n:d['test'] for n,d in report['bundles'].items()}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('capture', 'replay', 'compare'))
    parser.add_argument('--capture', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--bundle', action='append', default=[])
    parser.add_argument('--db')
    parser.add_argument('--name')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--results', type=Path)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--level', type=int, default=25)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    if args.action == 'capture' and (not args.source or not args.db or not args.bundle):
        parser.error('capture requires source, db, and at least one named bundle')
    if args.action == 'replay' and (not args.name or not args.output):
        parser.error('replay requires name and output')
    if args.action == 'compare' and (not args.results or not args.output):
        parser.error('compare requires results directory and output')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    globals()[args.action](args)


if __name__ == '__main__':
    main()
