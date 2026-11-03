#!/usr/bin/env python3
"""Evaluate frozen recovery policies using previously paired test predictions.

No fitting, candidate selection, or installation. Cross-route scores must share
IDs, labels and verified row-version digests. Missing routes are reported rather
than silently substituting general scores or historical aggregate metrics.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
import logging
from pathlib import Path

import numpy as np

from collimator import cache_identity, data, features, policy
from azoth_specialist_suite import _temporary_feature_env
from compare_regression_policies import decision_metrics, matched_positions, report_fingerprints
from tune_regressed_models import fingerprint, freeze


def effective_spec(root, base_environment=None):
    """Compare legacy specs under their recorded extraction environment."""
    spec = features.FeatureSpec.load(root / 'feature_spec.json')
    if spec.metric_transforms is not None:
        return asdict(spec)
    metadata = root / 'benchmark.json'
    if not metadata.exists() and base_environment is None:
        raise ValueError(f'No verified environment for legacy spec: {root}')
    benchmark = json.loads(metadata.read_text()) if metadata.exists() else {}
    environment = {**(base_environment or {}), **benchmark.get('feature_env', {})}
    with _temporary_feature_env(environment):
        spec.bind_metric_contract()
    return asdict(spec)


def require_generation(source, deployed, base_environment=None):
    if cache_identity.model_revision(source) != cache_identity.model_revision(deployed):
        raise ValueError(f'Prediction/model generation mismatch: {source} -> {deployed}')
    if effective_spec(source) != effective_spec(deployed, base_environment):
        raise ValueError(f'Prediction/feature contract mismatch: {source} -> {deployed}')


def require_prediction_source(root, source, column):
    plan = json.loads((root / 'plan.json').read_text())
    recorded = plan['hashes'][column]
    expected_models = {name for name in recorded if name.endswith('.onnx')}
    actual_models = {str(p.relative_to(source)) for p in (source / 'models').glob('*.onnx')}
    if not expected_models or expected_models != actual_models:
        raise ValueError(f'Prediction ensemble membership changed: {source}')
    for name, expected in recorded.items():
        if fingerprint(source / name) != expected:
            raise ValueError(f'Prediction source changed: {source / name}')


def load_calibration_audit(path, source, metadata, base_environment, *, test_only=True):
    """Reuse only freshly extracted, version-stable, generation-bound scores."""
    with np.load(path) as values:
        required = {'audit_row_ids', 'audit_labels', 'audit_fingerprints', 'audit_stable_rows',
                    'audit_model_revision', 'audit_spec_revision', 'audit_feature_revision',
                    'audit_feature_config', 'indices', 'probs'}
        if not required <= set(values.files):
            raise ValueError(f'Calibration scores lack row-version evidence: {path}')
        if (str(values['audit_model_revision']) != cache_identity.model_revision(source)
                or str(values['audit_spec_revision']) != fingerprint(source / 'feature_spec.json')):
            raise ValueError(f'Calibration prediction generation changed: {source}')
        if str(values['audit_feature_revision']) != cache_identity.code_revision('features'):
            raise ValueError(f'Calibration feature implementation changed: {source}')
        benchmark = json.loads((source / 'benchmark.json').read_text())
        with _temporary_feature_env({**(base_environment or {}), **benchmark['feature_env']}):
            expected = json.dumps(asdict(features.feature_config_from_env()), sort_keys=True, default=sorted)
        if str(values['audit_feature_config']) != expected:
            raise ValueError(f'Calibration feature environment mismatch: {source}')
        ids, labels, positions = values['audit_row_ids'], values['audit_labels'], values['indices']
        if not np.array_equal(ids, metadata['row_ids'][positions]):
            raise ValueError(f'Calibration row positions changed: {path}')
        stable = values['audit_stable_rows'].astype(bool)
        valid = stable & (labels == metadata['labels'][positions]) & np.isfinite(values['probs'])
        if test_only:
            valid &= metadata['sha_bucket'][positions] < data.TEST_BUCKET_MAX
        order = np.argsort(ids[valid], kind='stable')
        table = {'ids': ids[valid][order], 'labels': labels[valid][order],
                 'filetypes': metadata['file_types'][positions][valid][order],
                 'fingerprints': values['audit_fingerprints'][valid][order],
                 'probability': values['probs'][valid][order]}
        return table, {'scored_rows': len(ids), 'stable_rows': int(stable.sum()),
                       'retained_test_rows' if test_only else 'retained_rows': len(table['ids']),
                       'cache_sha256': fingerprint(path)}


def runtime_prediction_path(root, column=None):
    contract = 'runtime_f64_sum_f32_result_v1'
    plan = json.loads((root/'plan.json').read_text())
    if plan.get('prediction_contract') == contract:
        output = root/'predictions.npz'
        if column is not None:
            with np.load(output) as values:
                if column not in values.files:
                    raise ValueError(f'Runtime predictions lack requested column {column!r}: {root}')
        return output
    marker, output = root/'runtime-predictions.json', root/'runtime-predictions.npz'
    if not marker.exists():
        raise ValueError(f'Legacy predictions need runtime-averaging replay: {root}')
    receipt = json.loads(marker.read_text())
    identity = receipt['identity']
    if (identity['prediction_contract'] != contract
            or identity['plan_sha256'] != fingerprint(root/'plan.json')
            or identity['original_predictions_sha256'] != fingerprint(root/'predictions.npz')
            or receipt['output_sha256'] != fingerprint(output)):
        raise ValueError(f'Runtime prediction receipt changed: {root}')
    if column is not None and column not in identity['columns']:
        raise ValueError(f'Runtime replay lacks requested column {column!r}: {root}; '
                         'replay that generation in a separate source directory')
    return output


def load_overlay_audit(root):
    """Read a jointly audited score overlay, keeping test rows only."""
    receipt = json.loads((root / 'overlay-receipt.json').read_text())
    if (receipt['score_table_sha256'] != fingerprint(root / 'score_table.npz')
            or receipt['row_fingerprints_sha256'] != fingerprint(root / 'row-fingerprints.npy')
            or receipt['feature_revision'] != cache_identity.code_revision('features')):
        raise ValueError(f'Overlay score/version evidence changed: {root}')
    with np.load(root / 'score_table.npz') as values:
        mask = values['sha_bucket'] < data.TEST_BUCKET_MAX
        ids = values['row_ids'][mask]
        order = np.argsort(ids, kind='stable')
        indices = np.flatnonzero(mask)[order]
        common = {'ids': values['row_ids'][indices], 'labels': values['labels'][indices],
                  'filetypes': values['file_types'][indices],
                  'fingerprints': np.load(root / 'row-fingerprints.npy', mmap_mode='r')[indices]}
        scores = values['scores'][:, indices]
        names = values['route_names']
    result = {}
    for name, probabilities in zip(names, scores, strict=True):
        valid = np.isfinite(probabilities)
        result[str(name)] = {**{k: v[valid] for k, v in common.items()},
                             'probability': probabilities[valid]}
    return result, receipt


def evaluate_filetype(filetype, tables, configs, policies, levels):
    needed = {name: set(value.get('routes', {}).get('filetypes/' + filetype, {}).get('models', ['general']))
              for name, value in policies.items()}
    selected = {}
    for generation, routes in needed.items():
        for route in routes:
            key = (generation, route)
            if key not in tables:
                return {'filetype': filetype, 'status': 'missing_scores',
                        'missing': [list(k) for g, rs in needed.items() for r in rs
                                    if (k := (g, r)) not in tables]}
            table = tables[key]
            mask = table['filetypes'] == filetype
            selected[key] = {k: v[mask] for k, v in table.items()}
    ids, positions, excluded = matched_positions(selected)
    if not len(ids):
        return {'filetype': filetype, 'status': 'no_identical_rows',
                'excluded_changed_versions_or_labels': excluded}
    reference = next(iter(selected))
    labels = selected[reference]['labels'][positions[reference]]
    results = []
    for level in levels:
        cells = {}
        for generation, routes in needed.items():
            scores = {route: selected[(generation, route)]['probability'][positions[(generation, route)]]
                      for route in routes}
            margins = policy.routed_margin(scores, configs[generation], policies[generation],
                                           filetype, level, len(ids))
            cells[generation] = decision_metrics(labels, margins)
        results.append({'level': level, **cells,
                        'tp_delta': cells['candidate']['tp'] - cells['current']['tp'],
                        'fp_delta': cells['candidate']['fp'] - cells['current']['fp']})
    return {'filetype': filetype, 'status': 'matched', 'rows': len(ids),
            'input_ids_sha256': hashlib.sha256(ids.tobytes()).hexdigest(),
            'excluded_changed_versions_or_labels': excluded,
            'input_rows': {f'{g}:{r}': len(t['ids']) for (g, r), t in selected.items()},
            'levels': results}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--current-bundle', type=Path, required=True)
    p.add_argument('--candidate-bundle', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--current-feature-env', type=Path,
                   help='Verified training metadata for unbound current specs')
    p.add_argument('--db', default='postgres://hopper@localhost:5432/hopper')
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    manifest = json.loads(args.manifest.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    bundles = {'current': args.current_bundle, 'candidate': args.candidate_bundle}
    current_environment = (json.loads(args.current_feature_env.read_text())['feature_env']
                           if args.current_feature_env else None)
    configs = {k: json.loads((v / 'config.json').read_text()) for k, v in bundles.items()}
    policies = {k: json.loads((v / 'route_policies.json').read_text()) for k, v in bundles.items()}
    candidate = policies['candidate']
    if candidate.get('fit_partition') != 'dev' or candidate.get('score_space') != 'raw':
        raise ValueError('Candidate must have raw policies fitted on dev')
    if candidate.get('score_table_hash') != fingerprint(args.candidate_bundle / 'score_table.npz'):
        raise ValueError('Candidate policy does not match its newly calibrated score table')
    for name in configs:
        freeze(args.output / f'{name}-config.json', configs[name])
        freeze(args.output / f'{name}-policies.json', policies[name])
    freeze(args.output / 'manifest.json', manifest)
    tables, loaded, identities = {}, {}, []
    calibration_metadata = {}
    for entry in manifest['scores']:
        source = Path(entry['model'])
        generation, route = entry['generation'], entry['route']
        require_generation(source, bundles[generation] / route,
                           current_environment if generation == 'current' else None)
        if 'overlay_bundle' in entry:
            root = Path(entry['overlay_bundle'])
            if root not in loaded:
                loaded[root] = load_overlay_audit(root)
            overlays, receipt = loaded[root]
            identity = next(item for item in receipt['sources'] if item['route'] == route)
            if (identity['model_revision'] != cache_identity.model_revision(source)
                    or identity['spec_revision'] != fingerprint(source / 'feature_spec.json')):
                raise ValueError(f'Overlay model generation changed: {source}')
            tables[(generation, route)] = overlays[route]
            identities.append({**entry, 'receipt_sha256': fingerprint(root / 'overlay-receipt.json')})
            continue
        if 'calibration_scores' in entry:
            metadata_path = Path(entry.get('calibration_metadata', args.candidate_bundle / 'score_table.npz'))
            if metadata_path not in calibration_metadata:
                with np.load(metadata_path) as values:
                    calibration_metadata[metadata_path] = {k: values[k] for k in ('row_ids', 'labels', 'file_types', 'sha_bucket')}
            path = Path(entry['calibration_scores'])
            if path not in loaded:
                loaded[path] = load_calibration_audit(path, source, calibration_metadata[metadata_path], current_environment)
            tables[(generation, route)], receipt = loaded[path]
            identities.append({**entry, **receipt})
            continue
        root = Path(entry['predictions'])
        require_prediction_source(root, source, entry['column'])
        runtime_path = runtime_prediction_path(root, entry['column'])
        if root not in loaded:
            with np.load(runtime_path) as values:
                loaded[root] = {k: values[k] for k in values.files}
            loaded[root]['fingerprints'] = report_fingerprints(root, args.db)
        values = loaded[root]
        tables[(generation, route)] = {k: values[k] for k in ('ids', 'labels', 'filetypes', 'fingerprints')}
        tables[(generation, route)]['probability'] = values[entry['column']]
        identities.append({**entry, 'plan_sha256': fingerprint(root / 'plan.json'),
                           'predictions_sha256': fingerprint(root / 'predictions.npz'),
                           'runtime_predictions_sha256': fingerprint(runtime_path),
                           'cohort_sha256': fingerprint(root / 'cohort.json')})
    freeze(args.output / 'input-identities.json', identities)
    excluded_ids = np.asarray(manifest.get('excluded_row_ids', []), dtype=np.int64)
    exclusions = {}
    for key, table in list(tables.items()):
        keep = ~np.isin(table['ids'], excluded_ids)
        exclusions[':'.join(key)] = int((~keep).sum())
        tables[key] = {name: values[keep] for name, values in table.items()}
    levels = sorted({int(x['level']) for config in configs.values() for x in config['levels']})
    results = [evaluate_filetype(ft, tables, configs, policies, levels) for ft in manifest['filetypes']]
    freeze(args.output / 'comparison.json', {
        'purpose': 'Frozen policies on identical previously evaluated test inputs; no selection or installation.',
        'caveat': 'Exploratory reused test data. Row-version matches are required; missing and changed rows are reported. This is not whole-corpus coverage.',
        'excluded_known_train_dev_overlap_by_source': exclusions,
        'levels': levels, 'filetypes': results})
    logging.info('Matched %d/%d requested filetypes', sum(r['status'] == 'matched' for r in results), len(results))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
