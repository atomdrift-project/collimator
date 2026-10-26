#!/usr/bin/env python3
"""Benchmark exact expansion on a captured, unexpanded vocabulary database.

The source is opened read-only and backed up into a new output directory.
Run under resource limits when training is active. Times exclude copying and
verification. A count digest and ranked vocabularies detect semantic changes.
"""
import argparse
from contextlib import closing
import hashlib
import json
import logging
import os
from pathlib import Path
import resource
import sqlite3
import struct
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--cache-mib', type=int, default=256)
    parser.add_argument('--reduce-keys', type=int, default=1048576)
    parser.add_argument('--reducer', choices=('upsert', 'sorted'), default='sorted')
    args = parser.parse_args()
    if args.workers < 1 or not 1 <= args.cache_mib <= 1024 or not 1 <= args.reduce_keys <= 4194304:
        parser.error('workers must be positive, cache 1..1024 MiB, reduce-keys 1..4194304')
    args.output.mkdir(parents=True, exist_ok=False)
    os.environ.update(COLLIMATOR_VOCAB_REDUCE_CACHE_MIB=str(args.cache_mib),
                      COLLIMATOR_VOCAB_REDUCE_KEYS=str(args.reduce_keys),
                      COLLIMATOR_VOCAB_REDUCER=args.reducer)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    from collimator.vocabulary import VocabularyCounts
    output = args.output / 'counts.sqlite'
    with closing(sqlite3.connect(args.source.resolve().as_uri() + '?mode=ro', uri=True)) as source:
        if not source.execute('SELECT 1 FROM signatures LIMIT 1').fetchone():
            raise ValueError('source must contain unexpanded signatures')
        if source.execute("SELECT 1 FROM state WHERE key='materialization'").fetchone():
            raise ValueError('capture the fixture before expansion starts; partial plans fix partition assignments')
        with closing(sqlite3.connect(output)) as target:
            source.backup(target)
    started, cpu = time.monotonic(), time.process_time()
    with VocabularyCounts(str(output), durable=True, resume=True, defer_signatures=True,
                          materialize_workers=args.workers, cache_size_mib=args.cache_mib) as counts:
        counts._reduce_keys = args.reduce_keys
        counts.materialize()
        children = resource.getrusage(resource.RUSAGE_CHILDREN)
        result = dict(source=str(args.source.resolve()), workers=args.workers,
                      cache_mib=args.cache_mib, reduce_keys=args.reduce_keys, reducer=args.reducer,
                      elapsed_seconds=time.monotonic() - started,
                      cpu_seconds=time.process_time() - cpu + children.ru_utime + children.ru_stime,
                      parent_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      child_peak_rss_kib=children.ru_maxrss)
        digest, keys = hashlib.sha256(), 0
        for family, key, n in counts.db.execute('SELECT family,token,n FROM counts ORDER BY family,token'):
            encoded = family.encode()
            digest.update(struct.pack('>IIQ', len(encoded), len(key), n) + encoded + key)
            keys += 1
        result.update(keys=keys, count_digest=digest.hexdigest())
        result['top'] = {family: counts.top(family, 500, 5)
                         for family in ('bigram', 'trigram', 'tiered_bigram')}
    result['database_bytes'] = output.stat().st_size
    (args.output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'top'}))


if __name__ == '__main__':
    main()
