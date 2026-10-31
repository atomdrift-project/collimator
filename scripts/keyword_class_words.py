#!/usr/bin/env python3
"""Count malware/goodware document prevalence of trained keyword vocabularies.

Reads only saved training IDs, using their saved labels and one fresh read-only
report snapshot. This is a descriptive training-cohort audit, not a dev/test
score or a reconstruction of reports that have since been reanalyzed.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import json
import math
import multiprocessing
from pathlib import Path
import sys

import lightgbm as lgb

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from collimator import data, features
from collimator.corpus_snapshot import frozen_corpus


def model_words(directory):
    vocabularies = {}
    usage = {}
    for spec_path in directory.glob('*/feature_spec.json'):
        spec = json.loads(spec_path.read_text())
        for source, words in spec.get('keyword_vocabs', {}).items():
            previous = vocabularies.setdefault(source, set(words))
            if previous != set(words):
                raise ValueError(f'inconsistent source vocabulary: {spec_path}/{source}')
        for model_path in (spec_path.parent / 'models').glob('seed_*.txt'):
            model = lgb.Booster(model_file=str(model_path))
            gains = model.feature_importance('gain')
            splits = model.feature_importance('split')
            for name, gain, split_count in zip(spec['feature_names'], gains, splits, strict=True):
                if not split_count:
                    continue
                source, _, word = name.partition(':')
                if source not in vocabularies:
                    continue
                info = usage.setdefault((source, word), dict(splits=0, gain=0., models=0))
                info['splits'] += int(split_count)
                info['gain'] += float(gain)
                info['models'] += 1
    return vocabularies, usage


def count_route(db, root, route):
    directory = root / route
    cohort = json.loads((directory / 'selected_cohort.json').read_text())
    labels = {item['row_id']: item['label'] for item in cohort['train']}
    totals = Counter(labels.values())
    vocabularies, usage = model_words(directory)
    counts = {source: {label: Counter() for label in [0,1]} for source in vocabularies}
    available = {source: Counter() for source in vocabularies}
    ids = sorted(labels)
    fetched = 0
    for start in range(0, len(ids), 500):
        batch = data.fetch_cleave_results(db, ids[start:start+500])
        fetched += len(batch)
        for row_id, item in batch.items():
            label = labels[row_id]
            report = features._coerce_report(item['cleave_result'])
            tokens = features._report_keywords(features.report_files(report), vocabularies) if report else {}
            for source, words in tokens.items():
                available[source][label] += bool(words)
                counts[source][label].update(words & vocabularies[source])
        if start % 25000 == 0:
            print(f'{route}: counted {min(start+500,len(ids))}/{len(ids)} training reports', flush=True)
    if fetched != len(ids):
        raise ValueError(f'{route}: fetched {fetched}/{len(ids)} saved training rows')
    rows = []
    for source, words in vocabularies.items():
        for word in sorted(words):
            malware, benign = counts[source][1][word], counts[source][0][word]
            mp, bp = malware / totals[1], benign / totals[0]
            info = usage.get((source, word), dict(splits=0, gain=0., models=0))
            rows.append(dict(route=route, source=source, word=word,
                malware_reports=malware, malware_total=totals[1], malware_pct=100*mp,
                goodware_reports=benign, goodware_total=totals[0], goodware_pct=100*bp,
                presence_lift=None if not benign else mp/bp,
                smoothed_lift=((malware+.5)/(totals[1]+1))/((benign+.5)/(totals[0]+1)),
                absence_lift=None if benign == totals[0] else (1-mp)/(1-bp),
                source_available_malware=available[source][1], source_available_goodware=available[source][0],
                splits=info['splits'], gain=info['gain'], models_using_word=info['models']))
    positive = sorted((row for row in rows if row['splits'] and row['malware_reports'] >= max(10,math.ceil(.05*totals[1]))
                       and row['goodware_pct'] <= 1 and row['smoothed_lift'] >= 5),
                      key=lambda row: (-row['smoothed_lift'], -row['malware_reports'], row['word']))
    absence = sorted((row for row in rows if row['splits'] and row['goodware_pct'] >= 20
                      and row['malware_pct'] <= 10),
                     key=lambda row: (-row['absence_lift'], -row['goodware_pct'], row['word']))
    return dict(route=route, training_rows=fetched, malware=totals[1], goodware=totals[0],
                rows=rows, positive=positive[:100], absence=absence[:100])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--db', default='postgres://hopper@localhost:5432/hopper')
    parser.add_argument('--routes', nargs='+', default=['java_class','go','c','python','javascript'])
    parser.add_argument('--workers', type=int, default=3)
    args = parser.parse_args()
    output = args.root / 'keyword_class_words'
    output.mkdir(exist_ok=True)
    summary = dict(scope=__doc__, routes={})
    with frozen_corpus(args.db):
        with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
            futures = [pool.submit(count_route,args.db,args.root,route) for route in args.routes]
            for future in as_completed(futures):
                result = future.result()
                rows = result.pop('rows')
                with (output / (result['route']+'.csv')).open('w',newline='') as file:
                    writer = csv.DictWriter(file,fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
                summary['routes'][result['route']] = result
                (output / 'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
                print(f"Finished {result['route']}: {len(result['positive'])} malware-enriched candidates; {len(result['absence'])} goodware-presence candidates",flush=True)
    print(f'Finished: {output}',flush=True)


if __name__ == '__main__':
    main()
