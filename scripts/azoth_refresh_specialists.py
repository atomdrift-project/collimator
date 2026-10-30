#!/usr/bin/env python3
"""Refresh selected specialists on captured dev/test rows; freeze all other routes.

No general scoring, vocabulary discovery, or training occurs here. Existing
baseline predictions remain historical observations of the captured corpus;
new specialist scores are observations of the currently available reports.
Policies use dev only, and locked test is evaluated after policies freeze.
"""
from __future__ import annotations
import argparse
import copy
from dataclasses import asdict
import gc
import hashlib
import json
import logging
from pathlib import Path
import shutil
import time
import numpy as np
import azoth_calibrate_ensemble as calibration
import azoth_route_policy_search as search
from azoth_specialist_suite import _temporary_feature_env
from stage_azoth_runtime_bundle import _copy_route
from collimator import bundle, cache_identity, data, features, policy

LOG = logging.getLogger('refresh_specialists')
ROW_KEYS = {'row_ids', 'labels', 'file_types', 'file_groups', 'sha_bucket'}


def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def write_npz(path, table):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp.npz')
    np.savez_compressed(temporary, **table)
    temporary.replace(path)


def subset(table, mask):
    return {k: (v[:, mask] if k == 'scores' else v[mask] if k in ROW_KEYS else v)
            for k, v in table.items()}


def assert_frozen(baseline, updated, changed):
    """Refuse any change to unrelated policies, models, or fallback thresholds."""
    for name in ('config.json', 'route_policies.json'):
        old = json.loads((baseline/name).read_text())
        new = json.loads((updated/name).read_text())
        if name == 'route_policies.json':
            for route, block in old['routes'].items():
                if route not in changed:
                    assert new['routes'][route] == block, f'unrelated policy changed: {route}'
        else:
            for level, after in zip(old['levels'], new['levels'], strict=True):
                assert level['level'] == after['level']
                for route, value in level['hostile']['thresholds'].items():
                    if route not in changed:
                        assert after['hostile']['thresholds'][route] == value, route
            for model in old['models']:
                if model['route'] not in changed:
                    assert model in new['models'], model['route']
    for path in baseline.rglob('*'):
        if path.is_file() and (path.suffix == '.onnx' or path.name == 'feature_spec.json'):
            if path.parent.name == 'models':
                route = path.parent.parent.relative_to(baseline).as_posix()
            else:
                route = path.parent.relative_to(baseline).as_posix()
            if route not in changed:
                assert digest(path) == digest(updated/path.relative_to(baseline)), path


def score_route(source, ids, labels, output, db, workers):
    metadata = json.loads((source/'benchmark.json').read_text())
    env = metadata.get('feature_env', {})
    with _temporary_feature_env(env):
        identity = {'model': cache_identity.model_revision(source),
                    'spec': digest(source/'feature_spec.json'),
                    'features': cache_identity.code_revision('features'),
                    'settings': json.dumps(asdict(features.feature_config_from_env()), sort_keys=True, default=sorted),
                    'ids': hashlib.sha256(ids.tobytes()).hexdigest(),
                    'labels': hashlib.sha256(labels.tobytes()).hexdigest()}
        marker = output.with_suffix('.json')
        if output.exists() and marker.exists():
            assert json.loads(marker.read_text())['identity'] == identity, f'changed scoring inputs: {source}'
            with np.load(output) as saved:
                np.testing.assert_array_equal(saved['ids'], ids)
                return saved['probs']
        spec = features.FeatureSpec.load(source/'feature_spec.json')
        model = bundle.Ensemble.load_bundle(source)
        result = np.full(len(ids), np.nan, dtype=np.float32)
        positions = {int(rid): i for i, rid in enumerate(ids)}
        rows = [(int(rid), '', '', 0, int(label), '') for rid, label in zip(ids, labels, strict=True)]
        started = last = time.monotonic()
        processed = 0
        for kept, matrix, actual_labels, _ in features.extract_labeled_metadata_from_db_batches_unordered(
            db, rows, spec, n_workers=workers, batch_size=128,
        ):
            indices = np.array([positions[int(r[0])] for r in kept])
            np.testing.assert_array_equal(actual_labels, labels[indices])
            assert np.all(np.isnan(result[indices])), 'duplicate scoring rows'
            if spec.standardized:
                matrix = features.standardize(matrix, spec)
            result[indices] = model.predict_proba(matrix)
            processed += len(indices)
            if time.monotonic() - last >= 30:
                LOG.info('%s: %d/%d rows scored (%.0f rows/sec)', source.parent.name,
                         processed, len(ids), processed/max(time.monotonic()-started, 1))
                last = time.monotonic()
        missing = int(np.isnan(result).sum())
        if missing > max(2, int(len(ids)*.01)):
            raise ValueError(f'{source}: lost {missing}/{len(ids)} reports; refusing incomplete evaluation')
        write_npz(output, {'ids': ids, 'probs': result})
        bundle.atomic_write_json(marker, {'identity': identity, 'rows': len(ids),
            'missing_reports': missing, 'elapsed_seconds': time.monotonic()-started,
            'note': 'Captured scores; completed checkpoints are retained on resume.'})
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--score-table', type=Path, required=True)
    parser.add_argument('--candidates', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--db', default='postgres://hopper@localhost:5432/hopper')
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--approved-label-correction', type=Path)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    args.output.mkdir(parents=True, exist_ok=True)
    config = json.loads((args.baseline/'config.json').read_text())
    policies = json.loads((args.baseline/'route_policies.json').read_text())
    source_hash = digest(args.score_table)
    assert source_hash == config['score_table_hash'] == policies['score_table_hash'], 'baseline score table mismatch'
    candidates = json.loads(args.candidates.read_text())['candidates']
    correction = (json.loads(args.approved_label_correction.read_text())
                  if args.approved_label_correction else None)
    changed = {'filetypes/'+r['route'] for r in candidates}
    plan = {'baseline_config': digest(args.baseline/'config.json'), 'baseline_policies': digest(args.baseline/'route_policies.json'),
            'source_score_table': source_hash, 'candidates': candidates, 'approved_label_correction': correction,
            'scope': 'Only selected specialists; captured dev/test cohort; general and other routes frozen.'}
    plan_path = args.output/'plan.json'
    if plan_path.exists():
        assert json.loads(plan_path.read_text()) == plan, 'changed update plan'
    else:
        bundle.atomic_write_json(plan_path, plan)
    runtime = args.output/'runtime'
    if not runtime.exists():
        shutil.copytree(args.baseline, runtime)
    LOG.info('Loading captured baseline development/test scores (no general scoring)')
    baseline_path = args.output/'baseline-scores.npz'
    if baseline_path.exists():
        with np.load(baseline_path) as saved:
            baseline = dict(saved)
    else:
        with np.load(args.score_table) as saved:
            mask = saved['sha_bucket'] < data.DEV_BUCKET_MAX
            baseline = {k: (saved[k][:, mask] if k == 'scores' else saved[k][mask] if k in ROW_KEYS else saved[k]) for k in saved.files}
        write_npz(baseline_path, baseline)
    if correction:
        assert correction['status'] == 'verified' and correction['label'] in {'good', 'bad'}
        indices = np.flatnonzero(baseline['row_ids'] == correction['id'])
        assert len(indices) == 1, 'approved correction missing from captured cohort'
        index = int(indices[0])
        assert data.TEST_BUCKET_MAX <= baseline['sha_bucket'][index] < data.DEV_BUCKET_MAX
        assert 'filetypes/'+str(baseline['file_types'][index]) in changed
        baseline['labels'][index] = int(correction['label'] == 'bad')
        LOG.info('Applied previously approved dev-label correction for ID %s on both sides', correction['id'])
    names = baseline['route_names'].tolist()
    additions = sorted(changed - set(names))
    updated = {k: v.copy() for k, v in baseline.items() if k != 'scores'}
    updated['route_names'] = np.array(names+additions)
    updated['route_kinds'] = np.array(baseline['route_kinds'].tolist()+['filetype']*len(additions))
    updated['scores'] = np.full((len(names)+len(additions), len(baseline['labels'])), np.nan, dtype=np.float32)
    updated['scores'][:len(names)] = baseline['scores']
    keep = np.ones(len(baseline['labels']), dtype=bool)
    for record in candidates:
        route = record['route']; name = 'filetypes/'+route
        source = Path(record['source'])
        cache_identity.require_reserved_dev(source)
        assert cache_identity.model_revision(source) == record['model_revision'], route
        indices = np.flatnonzero(baseline['file_types'] == route)
        LOG.info('%s: refreshing %d captured dev/test rows', route, len(indices))
        probs = score_route(source, baseline['row_ids'][indices], baseline['labels'][indices],
                            args.output/'scores'/f'{route}.npz', args.db, args.workers)
        keep[indices[np.isnan(probs)]] = False
        updated['scores'][updated['route_names'].tolist().index(name)] = np.nan
        updated['scores'][updated['route_names'].tolist().index(name), indices] = probs
        destination = runtime/name
        if destination.exists(): shutil.rmtree(destination)
        assert _copy_route(source, destination), route
        gc.collect()
    # Missing documents are removed from BOTH sides of the comparison.
    baseline = subset(baseline, keep); updated = subset(updated, keep)
    write_npz(args.output/'baseline-matched-scores.npz', baseline)
    write_npz(args.output/'scores.npz', updated)
    new_hash = digest(args.output/'scores.npz')
    dev = policy.partition_table(updated, 'dev')
    dev_labels = dev['labels']
    route_arrays = search._route_arrays(dev)
    config['root'] = str(runtime.resolve())
    config['score_table'] = str((args.output/'scores.npz').resolve())
    config['score_table_hash'] = new_hash
    config['incremental_update'] = {'routes': sorted(changed), 'baseline_score_table_hash': source_hash,
        'approved_label_correction': correction,
        'rows': len(updated['labels']), 'missing_reports': int((~keep).sum()),
        'general_model_and_calibration': 'preserved', 'training_rows': 'not rescored or used for calibration',
        'corpus': 'captured baseline labels and canonical partitions; updated specialists use available current reports'}
    old_records = {r['route']: r for r in config['models']}
    for record in candidates:
        name = 'filetypes/'+record['route']; directory = runtime/name
        old_records[name] = {'route': name, 'kind': 'filetype',
            'model_revision': cache_identity.model_revision(directory),
            'spec_revision': digest(directory/'feature_spec.json'),
            'rows': int(np.sum(updated['file_types'] == record['route']))}
        scoped = np.flatnonzero(dev['file_types'] == record['route'])
        probability = route_arrays[name]['dense_probs'][scoped]
        for level in config['levels']:
            fit = calibration._calibrate_one(dev_labels[scoped], [{'name': name, 'kind': 'filetype',
                'indices': np.arange(len(scoped)), 'probs': probability}],
                target_per_million=float(level['hostile']['target_per_million']))
            level['hostile']['thresholds'].pop(name, None)
            level['hostile']['thresholds'].update(fit['thresholds'])
            level['hostile']['diagnostics'][name] = fit['diagnostics'][name]
    config['models'] = list(old_records.values())
    config['model_set_hash'] = hashlib.sha256(json.dumps(config['models'], sort_keys=True).encode()).hexdigest()
    policies['score_table_hash'] = new_hash
    search._SHARED.update(routes=route_arrays, labels=dev_labels, file_types=dev['file_types'],
        filetype_to_group=config['filetype_to_group'], config=config, azoth_root=runtime,
        total_benign=int(np.sum(dev_labels == 0)))
    for record in candidates:
        LOG.info('%s: fitting filetype policies on dev only', record['route'])
        key, payload = search._process_filetype(record['route'])
        block = {'routes': {key: payload}}
        assert not search._level_monotonicity_errors(block), key
        errors = search._swept_budget_errors(
            block, config, subset(dev, dev['file_types'] == record['route']))
        if errors:
            raise ValueError('Refusing specialist policies that overspend: ' + '; '.join(errors[:5]))
        block['routes'][key]['budget_semantics'] = 'resolution_adjusted_per_filetype_v1'
        policies['routes'][key] = block['routes'][key]
    bundle.atomic_write_json(runtime/'config.json', search._json_clean(config))
    bundle.atomic_write_json(runtime/'route_policies.json', search._json_clean(policies))
    search._write_markdown(runtime/'route_policies.md', policies)
    assert_frozen(args.baseline, runtime, changed)
    for i, name in enumerate(baseline['route_names']):
        if name not in changed:
            j = updated['route_names'].tolist().index(name)
            np.testing.assert_array_equal(baseline['scores'][i], updated['scores'][j])
    bundle.atomic_write_json(args.output/'prepared.json', {'status': 'specialists scored and policies frozen; deployment gates pending',
        'changed_routes': sorted(changed), 'evaluated_rows': len(updated['labels']),
        'rescored_rows': sum(int(np.sum(updated['file_types'] == r['route'])) for r in candidates),
        'missing_reports': int((~keep).sum()), 'frozen_invariants': 'passed'})
    LOG.info('Scoped update ready for gates: %d specialists; general and unrelated decisions unchanged', len(changed))


if __name__ == '__main__':
    main()
