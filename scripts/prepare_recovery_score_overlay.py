#!/usr/bin/env python3
"""Stage a research bundle from audited scores without re-extracting every model.

Replacements are frozen before this runs. No candidate selection or installation
occurs here. Every retained row has the same selected label and report version
across all applicable models. Known training IDs are excluded from both dev/test;
previous selection IDs are excluded from test only. Policies must be fitted next.
"""
import argparse
from collections import Counter
import copy
import hashlib
import json
import logging
from pathlib import Path
import shutil

import numpy as np

from collimator import cache_identity, data
from azoth_calibrate_ensemble import _calibrate_one
from evaluate_recovery_policy_matches import load_calibration_audit, require_generation
from tune_regressed_models import fingerprint, freeze


def align_scores(table, metadata, expected, reference_fingerprints=None):
    """Return cohort-aligned scores and a mask requiring complete matching inputs."""
    ids = metadata['row_ids']
    order = np.argsort(ids, kind='stable')
    sorted_ids = ids[order]
    if len(np.unique(ids)) != len(ids) or len(np.unique(table['ids'])) != len(table['ids']):
        raise ValueError('Duplicate cohort or score IDs')
    slots = np.searchsorted(sorted_ids, table['ids'])
    if np.any(slots == len(ids)) or not np.array_equal(sorted_ids[slots], table['ids']):
        raise ValueError('Scores contain IDs outside frozen cohort')
    positions = order[slots]
    valid = table['labels'] == metadata['labels'][positions]
    if reference_fingerprints is not None:
        valid &= table['fingerprints'] == reference_fingerprints[positions]
    probabilities = np.full(len(ids), np.nan, dtype=np.float32)
    probabilities[positions[valid]] = table['probability'][valid]
    fingerprints = np.zeros(len(ids), dtype='V32')
    fingerprints[positions[valid]] = table['fingerprints'][valid]
    keep = ~expected | np.isfinite(probabilities)
    return probabilities, fingerprints, keep


def membership_mask(ids, buckets, training_ids, selection_ids):
    return (~np.isin(ids, training_ids)
            & ~((buckets < data.TEST_BUCKET_MAX) & np.isin(ids, selection_ids)))


def route_key(name, kind):
    if name.startswith(('filegroups/', 'filetypes/')):
        return name
    return 'general' if kind == 'general' else ('filegroups/' if kind == 'filegroup' else 'filetypes/') + name


def additional_score_slots(additional, keys, scores):
    """Preserve a specialist's coverage when retaining it under a new name.

    Only genuinely global alternatives join the global policy search. Scoped
    aliases are available to explicit policies without becoming applicable to
    unrelated filetypes or deleting those rows from the audited cohort.
    """
    slots, global_routes = [], []
    for name, source in additional.items():
        scope = source.get('coverage_from')
        if scope is None:
            expected = np.ones(scores.shape[1], dtype=bool)
            global_routes.append(name)
        elif scope in keys:
            expected = np.isfinite(scores[keys.index(scope)])
        else:
            raise ValueError(f'Unknown additional-model coverage source: {scope}')
        slots.append(np.where(expected, np.float32(0), np.float32(np.nan)))
    return np.asarray(slots, dtype=np.float32), global_routes


def copy_model(source, target):
    cache_identity.require_reserved_dev(source)
    target.mkdir(parents=True)
    for name in ('feature_spec.json', 'benchmark.json', 'training_config.json',
                 'accepted_config.json', 'training_provenance.json'):
        if (source / name).exists():
            shutil.copy2(source / name, target / name)
    (target / 'models').mkdir()
    for path in (source / 'models').iterdir():
        if path.suffix in {'.onnx', '.txt'}:
            shutil.copy2(path, target / 'models' / path.name)
    require_generation(source, target)
    cache_identity.require_reserved_dev(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    plan = json.loads(args.plan.read_text())
    base, output = Path(plan['base_bundle']), Path(plan['output_bundle'])
    if output.exists():
        raise ValueError(f'Refusing to overwrite existing bundle: {output}')
    config = json.loads((base / 'config.json').read_text())
    if config.get('fit_partition') != 'dev' or config.get('score_space') != 'raw':
        raise ValueError('Base calibration must use raw scores and dev fitting')
    source_hash = fingerprint(base / 'score_table.npz')
    if source_hash != config['score_table_hash']:
        raise ValueError('Base table differs from its calibration config')
    if 'general' not in plan['replacements']:
        raise ValueError('An audited general score source is required')
    with np.load(base / 'score_table.npz') as values:
        metadata = {k: values[k] for k in ('row_ids', 'labels', 'file_types', 'file_groups', 'sha_bucket')}
        names, kinds = values['route_names'], values['route_kinds']
        scores = values['scores']
    keys = [route_key(str(n), str(k)) for n, k in zip(names, kinds, strict=True)]
    if keys[0] != 'general' or set(plan['replacements']) - set(keys):
        raise ValueError('Unexpected route layout or unknown replacement')
    additional = plan.get('additional_models', {})
    if (set(additional) & set(keys)
            or any(not key.startswith('filegroups/') for key in additional)):
        raise ValueError('Additional models must be new named filegroup routes')
    if additional:
        slots, global_routes = additional_score_slots(additional, keys, scores)
        keys.extend(additional)
        names = np.r_[names, list(additional)]
        kinds = np.r_[kinds, ['filegroup'] * len(additional)]
        scores = np.concatenate([scores, slots])
        config['models'].extend({'route':key, 'kind':'filegroup'} for key in additional)
        config['global_auxiliary_routes'] = list(dict.fromkeys([
            *config.get('global_auxiliary_routes', []), *global_routes]))
    replacements = {**plan['replacements'], **additional}
    if np.any(metadata['sha_bucket'] >= data.DEV_BUCKET_MAX):
        raise ValueError('Recovery policy table must contain dev/test only')
    environment = json.loads(Path(plan['feature_environment']).read_text())['feature_env']
    keep = np.ones(len(metadata['row_ids']), dtype=bool)
    reference_fingerprints = None
    receipts, sources = [], {}
    for i, key in enumerate(keys):
        replacement = replacements.get(key, {})
        source = Path(replacement.get('model', str(base / key)))
        cache = Path(replacement.get('scores', str(source / 'calibration_scores.npz')))
        values, receipt = load_calibration_audit(cache, source, metadata, environment, test_only=False)
        expected = np.isfinite(scores[i])
        if key == 'general' and not np.all(expected):
            raise ValueError('Base general scores are incomplete')
        probabilities, digests, valid = align_scores(values, metadata, expected, reference_fingerprints)
        if key == 'general':
            reference_fingerprints = digests
        keep &= valid
        # Extra out-of-route rows must not silently widen a model's coverage.
        probabilities[~expected] = np.nan
        scores[i] = probabilities
        receipts.append({'route': key, 'model': str(source), 'scores': str(cache), **receipt,
                         'excluded_missing_or_mismatched_rows': int((~valid).sum()),
                         'model_revision': cache_identity.model_revision(source),
                         'spec_revision': fingerprint(source / 'feature_spec.json')})
        sources[key] = source
        logging.info('Audited %s: %d rows remain jointly valid', key, int(keep.sum()))
    membership_receipts = []
    for field, test_only in [('training_memberships', False), ('selection_memberships', True)]:
        for name in plan.get(field, []):
            path = Path(name)
            before = fingerprint(path)
            ids = np.load(path, mmap_mode='r')
            overlap = ~membership_mask(metadata['row_ids'], metadata['sha_bucket'],
                                       [] if test_only else ids, ids if test_only else [])
            keep &= ~overlap
            if fingerprint(path) != before:
                raise ValueError(f'Membership file changed: {path}')
            membership_receipts.append({'path': name, 'sha256': before,
                                        'test_only': test_only, 'excluded_rows': int(overlap.sum())})
    if not np.any(keep & (metadata['sha_bucket'] >= data.TEST_BUCKET_MAX)):
        raise ValueError('No eligible development rows remain')
    for receipt in receipts:
        source = Path(receipt['model'])
        if (cache_identity.model_revision(source) != receipt['model_revision']
                or fingerprint(source / 'feature_spec.json') != receipt['spec_revision']):
            raise ValueError(f'Source model changed: {source}')
    # Copy only model artifacts, never stale policies or calibration products.
    for key, source in sources.items():
        copy_model(source, output / key)
    freeze(output / 'overlay-plan.json', plan)
    np.save(output / 'excluded-row-ids.npy', metadata['row_ids'][~keep])
    metadata = {k: v[keep] for k, v in metadata.items()}
    table_path = output / 'score_table.npz'
    np.savez_compressed(table_path, **metadata, route_names=names, route_kinds=kinds,
                        scores=scores[:, keep], score_space=np.asarray('raw'))
    np.save(output / 'row-fingerprints.npy', reference_fingerprints[keep])
    fit = metadata['sha_bucket'] >= data.TEST_BUCKET_MAX
    config = copy.deepcopy(config)
    config.update(root=str(output.resolve()), score_table=str(table_path.resolve()),
                  score_table_hash=fingerprint(table_path), rows=int(keep.sum()),
                  malware=int((metadata['labels'] == 1).sum()), benign=int((metadata['labels'] == 0).sum()),
                  fit_rows=int(fit.sum()), fit_malware=int((metadata['labels'][fit] == 1).sum()),
                  fit_benign=int((metadata['labels'][fit] == 0).sum()),
                  observed_filetypes=dict(sorted(Counter(metadata['file_types'].tolist()).items())),
                  model_set_hash=hashlib.sha256(json.dumps(receipts, sort_keys=True).encode()).hexdigest(),
                  search={'method': 'audited_score_overlay_pending_dev_policy_fit'})
    for model, receipt in zip(config['models'], receipts, strict=True):
        if route_key(model['route'], model['kind']) != receipt['route']:
            raise ValueError('Config model order differs from score table')
        model.update(model_revision=receipt['model_revision'], spec_revision=receipt['spec_revision'])
        model['rows'] = int(np.isfinite(scores[keys.index(receipt['route'])][keep]).sum())
    # Fit fallback thresholds on eligible dev rows only. Reusing thresholds
    # from the previous general model would invalidate the combined bundle.
    fit_routes = []
    fit_positions = np.flatnonzero(keep)[fit]
    for i, key in enumerate(keys):
        values = scores[i, fit_positions]
        valid = np.isfinite(values)
        fit_routes.append({'name': key, 'kind': str(kinds[i]),
                           'indices': np.flatnonzero(valid), 'probs': values[valid]})
    for level in config['levels']:
        target = level['hostile']['target_per_million']
        level['hostile'] = _calibrate_one(metadata['labels'][fit], fit_routes,
                                          target_per_million=target)
        logging.info('Fitted dev fallback L%s', level['level'])
    freeze(output / 'config.json', config)
    summary = json.loads((base / 'specialists.json').read_text())
    summary['results'].extend({'name':key.removeprefix('filegroups/'), 'kind':'filegroup'}
                              for key in additional)
    for record in summary['results']:
        key = route_key(record['name'], record.get('kind', 'filetype'))
        if key in sources:
            updated = json.loads((sources[key] / 'benchmark.json').read_text())
            record.update({**updated, 'name': record['name'], 'kind': record.get('kind', 'filetype'),
                           'output_dir': str((output / key).resolve())})
    freeze(output / 'specialists.json', summary)
    freeze(output / 'overlay-receipt.json', {'base_score_table_sha256': source_hash,
        'score_table_sha256': config['score_table_hash'],
        'row_fingerprints_sha256': fingerprint(output / 'row-fingerprints.npy'),
        'feature_revision': cache_identity.code_revision('features'),
        'sources': receipts, 'memberships': membership_receipts, 'retained_rows': int(keep.sum()),
        'excluded_rows': int((~keep).sum()), 'partition_semantics': 'Frozen source canonical partitions',
        'installation': False, 'policies': 'Not fitted; run dev policy search next.'})
    logging.info('Staged %d models and %d audited rows at %s', len(keys), int(keep.sum()), output)


if __name__ == '__main__':
    main()
