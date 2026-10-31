#!/usr/bin/env python3
"""Verify the matched keyword source experiment and summarize saved predictions."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from keyword_route_controls import VARIANTS, EXTENDED_VARIANTS


def summarize(root):
    os.environ['COLLIMATOR_SAMPLE_PERCENT'] = '10'
    from collimator.experiment import recall_at_per_100M
    raw = json.loads((root / 'comparison.json').read_text())
    output = dict(sample_percent=raw['sample_percent'], seeds=raw['seeds'], tree_budget=raw['tree_budget'],
                  scope='Matched natural 10% canonical-group sample; two seeds; train/dev only; locked test unused.', routes={})
    rows = []
    common_training = None
    common_vocab_settings = None
    training_revisions = set()
    for route, variants in raw['routes'].items():
        route_out = output['routes'].setdefault(route, {})
        identity = None
        database = None
        predictions_identity = None
        assert list(variants) == raw['variants'], f'incomplete route: {route}'
        baseline = variants['baseline']
        for variant, record in variants.items():
            assert record.get('verified_matched_inputs'), f'unverified or failed {route}/{variant}'
            directory = root / route / variant
            run_path = max((directory / 'runs').glob('*-experiment.json'), key=lambda p: p.stat().st_mtime)
            run = json.loads(run_path.read_text())
            experiment = run['experiment_spec']
            flags = (VARIANTS | EXTENDED_VARIANTS)[variant]
            flags = (*flags, *(0 for _ in range(5-len(flags))))
            keys = ['RULE_KEYWORDS', 'DESCRIPTION_KEYWORDS', 'FULL_RULE_KEYWORDS', 'RULE_DESCRIPTION_KEYWORDS', 'CONTEXT_KEYWORDS']
            for key, enabled in zip(keys, flags, strict=True):
                assert experiment['feature_env']['COLLIMATOR_' + key] == str(enabled)
            spec = json.loads((directory / 'feature_spec.json').read_text())
            sources = ['ruleword', 'descword', 'fullword', 'ruletextword', 'contextword']
            assert set(spec['keyword_vocabs']) == {source for source, enabled in zip(sources, flags, strict=True) if enabled}
            vocab_settings = tuple(experiment['feature_env']['COLLIMATOR_' + key] for key in ['KEYWORD_VOCAB_MAX', 'KEYWORD_MIN_FREQ'])
            if common_vocab_settings is None:
                common_vocab_settings = vocab_settings
                output['keyword_vocab_max'], output['keyword_min_freq'] = map(int, vocab_settings)
            assert vocab_settings == common_vocab_settings
            assert experiment['feature_env']['COLLIMATOR_SAMPLE_PERCENT'] == '10'
            assert experiment['train_samples'] == experiment['max_test_samples'] == experiment['total_limit'] == 0
            assert experiment['train_config']['colsample_bytree'] == 1
            assert experiment['filters']['min_malware_training_score'] == 0
            assert experiment['seed_search_k'] == 2 and run['save_all_seeds']
            training = (experiment['train_config'], experiment['feature_revision'])
            if common_training is None:
                common_training = training
            assert training == common_training, 'training settings or extractor changed during comparison'
            training_revisions.add(experiment['code_revision'])
            inputs = tuple(record[key] for key in ['base_train_sha256', 'base_dev_sha256', 'evaluation_revision', 'train_rows', 'train_malware', 'dev_rows', 'dev_malware'])
            if identity is None:
                identity = inputs
                database = experiment['database_revision']
            assert inputs == identity and experiment['database_revision'] == database
            with np.load(directory / 'dev_predictions.npz') as arrays:
                signature = hashlib.sha256(arrays['row_ids'].tobytes() + arrays['labels'].tobytes()).hexdigest()
                if predictions_identity is None:
                    predictions_identity = signature
                assert signature == predictions_identity, 'dev IDs or labels changed'
                assert [seed['seed'] for seed in record['seeds']] == raw['seeds']
                for member in record['seeds']:
                    scores = np.asarray(arrays[f"seed_{member['seed']}"], dtype=np.float32)
                    metrics = recall_at_per_100M(arrays['labels'], scores)
                    attempt = next(attempt for attempt in run['seed_search_results'] if attempt['seed'] == member['seed'])
                    assert np.isclose(metrics['level_budget_recall'], attempt['level_budget_recall'])
                    for budget in [0, 1]:
                        key = f'recall_at_{budget}fp'
                        assert np.isclose(metrics[key], member[key])
                averaged = np.mean([arrays[f'seed_{seed}'].astype(np.float64) for seed in raw['seeds']], axis=0).astype(np.float32)
                ensemble = recall_at_per_100M(arrays['labels'], averaged)
            arm = dict(train_rows=record['train_rows'], dev_rows=record['dev_rows'], dev_malware=record['dev_malware'],
                       features=record['features'], dev_matrix_nnz=record['dev_matrix_nnz'], spec_bytes=record['spec_bytes'],
                       onnx_bytes=sum(path.stat().st_size for path in (directory / 'models').glob('seed_*.onnx')),
                       training_seconds=record['elapsed_seconds'],
                       matrix_scoring_seconds=[member['scoring_seconds'] for member in record['seeds']],
                       keyword_usage=[member['keyword_usage'] for member in record['seeds']])
            for budget in [0,1]:
                key = f'recall_at_{budget}fp'
                values = [member[key] for member in record['seeds']]
                arm[key] = dict(per_seed=values, mean=float(np.mean(values)),
                                mean_delta_pp=100 * float(np.mean([member[key] - base[key] for member, base in zip(record['seeds'], baseline['seeds'], strict=True)])),
                                ensemble=ensemble[key])
                assert np.isclose(ensemble[key], record['ensemble_metrics'][key])
            route_out[variant] = arm
            rows.append(dict(route=route, variant=variant, dev_malware=arm['dev_malware'],
                mean_recall_0fp_pct=100*arm['recall_at_0fp']['mean'], mean_recall_1fp_pct=100*arm['recall_at_1fp']['mean'],
                delta_1fp_pp=arm['recall_at_1fp']['mean_delta_pp'], ensemble_recall_0fp_pct=100*arm['recall_at_0fp']['ensemble'],
                ensemble_recall_1fp_pct=100*arm['recall_at_1fp']['ensemble'],
                features=arm['features'], dev_nnz=arm['dev_matrix_nnz'], spec_bytes=arm['spec_bytes'], onnx_bytes=arm['onnx_bytes']))
        coverage = root / route / 'context_coverage.json'
        if coverage.exists():
            route_out['context_coverage'] = json.loads(coverage.read_text())
    if len(training_revisions) > 1:
        audit = json.loads((root / 'training_revision_audit.json').read_text())
        assert set(audit['audited_revisions']) == training_revisions, 'unaudited training revision'
        assert audit['source_revisions_reconstructed']
        assert audit['changed_files'] == ['train.py', 'model.py']
        assert [check['seed'] for check in audit['checks']] == raw['seeds']
        assert all(check['bit_identical'] and check['trees'] > 1 for check in audit['checks'])
        # The audited device-probe reorder is equivalent for CPU models only.
        for path in root.glob('*/*/models/seed_*.txt'):
            assert '[device_type: cpu]' in path.read_text(), f'unaudited device: {path}'
        output['training_revision_audit'] = audit
    output['verified_controls'] = True
    (root / 'verified_summary.json').write_text(json.dumps(output, indent=2) + '\n')
    with (root / 'comparison.csv').open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    names = raw['variants']
    lines = ['Mean individual-seed dev recall at one allowed false positive (%). Two seeds; natural 10% sample.', '',
             '| File type | Dev malware | ' + ' | '.join(names) + ' |',
             '|---|---:|' + '---:|' * len(names)]
    for route, values in output['routes'].items():
        lines.append(f"| {route} | {values['baseline']['dev_malware']} | " + ' | '.join(f"{100*values[name]['recall_at_1fp']['mean']:.1f}" for name in names) + ' |')
    lines += ['', 'Two-seed ensemble dev recall at one allowed false positive (%). This scores averaged probabilities, as the saved bundle does.', '',
              '| File type | Dev malware | ' + ' | '.join(names) + ' |',
              '|---|---:|' + '---:|' * len(names)]
    for route, values in output['routes'].items():
        lines.append(f"| {route} | {values['baseline']['dev_malware']} | " + ' | '.join(f"{100*values[name]['recall_at_1fp']['ensemble']:.1f}" for name in names) + ' |')
    lines += ['', 'Hierarchy + descriptions uses separate feature columns; pooled combines only description + full rule ID. Context is a separate arm.',
              'All rows, labels, base feature values, database snapshots within routes, and training settings were verified matched.',
              'This is a dev screen. Java has only 22 malware examples. Context availability varies, and no model was promoted.',
              'Matrix scoring timings exclude text decoding and feature extraction.']
    if len(training_revisions) > 1:
        lines.append('A concurrent training compatibility edit was audited: both revisions produced bit-identical CPU models and predictions. See training_revision_audit.json and training_revision_sources/.')
    (root / 'RESULTS.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    summarize(args.root)
