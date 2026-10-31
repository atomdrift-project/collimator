#!/usr/bin/env python3
"""Audit context encodings in saved train/dev cohorts, without reading locked test."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from collimator import data, features
from collimator.corpus_snapshot import frozen_corpus


def audit(db, directory, wait=False):
    cohort_path = directory / 'selected_cohort.json'
    deadline = time.monotonic() + (1800 if wait else 0)
    while not cohort_path.exists() and not list((directory / 'cache').glob('corpus_*.json')) and time.monotonic() < deadline:
        time.sleep(2)
    if not cohort_path.exists():
        candidates = list((directory / 'cache').glob('corpus_*.json'))
        if len(candidates) != 1:
            raise ValueError(f'expected one cohort in {directory}')
        cohort_path = candidates[0]
    cohort = json.loads(cohort_path.read_text())
    selected = {row['row_id']: (partition, row['label']) for key, partition in [('train','train'), ('test','dev')]
                for row in cohort[key]}
    stats = {f'{partition}_{label}': Counter() for partition in ['train','dev'] for label in [0,1]}
    invalid = []
    ids = sorted(selected)
    for start in range(0, len(ids), 500):
        for row_id, item in data.fetch_cleave_results(db, ids[start:start+500]).items():
            partition, label = selected[row_id]
            counts = stats[f'{partition}_{label}']
            counts['reports'] += 1
            report = features._coerce_report(item['cleave_result'])
            windows = [window for file in features.report_files(report) for window in file.get('ctx', [])] if report else []
            counts['reports_with_context'] += bool(windows)
            counts['windows'] += len(windows)
            kinds = set()
            had_words = False
            for window in windows:
                kind = ('byte_text' if window.get('s') is not None else
                        'plain_text' if window.get('t') is not None else 'z85')
                kinds.add(kind)
                counts[kind + '_windows'] += 1
                try:
                    raw = features._decode_context_window(window)
                    counts['decoded_bytes'] += len(raw)
                    had_words |= bool(features._keyword_words.__wrapped__(raw.decode('utf-8', errors='replace')))
                except (ValueError, AttributeError) as error:
                    invalid.append(dict(row_id=row_id, partition=partition, label=label, error=str(error)))
            counts['reports_with_words'] += had_words
            for kind in kinds:
                counts[kind + '_reports'] += 1
        if start % 25000 == 0:
            print(f'{directory.name}: audited {min(start+500, len(ids))}/{len(ids)}', flush=True)
    fetched = sum(count['reports'] for count in stats.values())
    result = dict(scope='Fresh read-only snapshot restricted to saved train/dev row IDs; diagnostic coverage audit, not a scoring run.',
                  selected_rows=len(selected), fetched_rows=fetched, missing_rows=len(selected)-fetched,
                  groups=stats, invalid_windows=invalid)
    (directory / 'context_coverage.json').write_text(json.dumps(result, indent=2) + '\n')
    print(directory.name, json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directories', nargs='+', type=Path)
    parser.add_argument('--db', default='postgres://hopper@localhost:5432/hopper')
    parser.add_argument('--wait-for-cohort', action='store_true')
    args = parser.parse_args()
    with frozen_corpus(args.db):
        for directory in args.directories:
            audit(args.db, directory, args.wait_for_cohort)
