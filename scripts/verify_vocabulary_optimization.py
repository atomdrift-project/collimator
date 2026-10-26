#!/usr/bin/env python3
"""Offline, bounded-resource checks; invoke under the documented systemd limits.

Uses only isolated checkouts and a previously captured counting stream. Never
opens the training replica or the active nightly's files. The large fixture
contains synthetic opaque keys to stress SQLite storage, not model training.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time


def create_mature_fixture(path, gib):
    def setup(db):
        db.execute('PRAGMA journal_mode=OFF')
        db.execute('PRAGMA synchronous=OFF')
        db.execute('PRAGMA cache_size=-65536')
        db.execute('CREATE TABLE tokens(id INTEGER PRIMARY KEY, token TEXT NOT NULL)')
        db.execute('CREATE TABLE counts(family TEXT, token BLOB, n INTEGER NOT NULL, first_document INTEGER, document INTEGER, PRIMARY KEY(family,token)) WITHOUT ROWID')
        db.execute('CREATE TABLE batches(id TEXT PRIMARY KEY, summary TEXT, n_rows INTEGER)')
        db.execute('CREATE TABLE state(key TEXT PRIMARY KEY, value TEXT)')

    def insert(db, start, stop):
        db.execute("WITH RECURSIVE rows(i) AS (VALUES(?) UNION ALL SELECT i+1 FROM rows WHERE i+1<?) "
                   "INSERT INTO counts SELECT 'trigram',packed(i),1,NULL,NULL FROM rows", (start,stop))
        db.commit()

    probe=path.with_suffix('.probe.sqlite')
    with sqlite3.connect(probe) as db:
        setup(db)
        db.create_function('packed',1,lambda i:(i*((1<<96)//100000)).to_bytes(12,'big'))
        insert(db,0,100000)
    bytes_per_key=probe.stat().st_size/100000
    probe.unlink()
    count=math.ceil(gib*2**30/bytes_per_key*1.03)
    step=(1<<96)//count
    started=time.monotonic()
    with sqlite3.connect(path) as db:
        setup(db)
        db.create_function('packed',1,lambda i:(i*step).to_bytes(12,'big'))
        for start in range(0,count,1000000):
            insert(db,start,min(start+1000000,count))
            print(f'fixture: {min(start+1000000,count):,}/{count:,} keys, {path.stat().st_size/2**30:.2f} GiB',flush=True)
    return dict(keys=count,bytes=path.stat().st_size,seconds=time.monotonic()-started,
                description='Synthetic ordered opaque keys; exact packed-count equality, not a training-corpus proxy')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--mature-gib',type=float,default=2)
    args=parser.parse_args()
    group=next(line.split(':',2)[2] for line in Path('/proc/self/cgroup').read_text().splitlines() if line.startswith('0::'))
    cgroup=Path('/sys/fs/cgroup')/group.lstrip('/')
    limits={name:(cgroup/name).read_text().strip() for name in ('cpu.max','memory.max','io.max')}
    quota,period=limits['cpu.max'].split()
    if quota=='max' or int(quota)>2*int(period) or int(limits['memory.max'])>8*2**30:
        raise SystemExit('Verification requires enforced CPU and memory limits')
    device = Path(__file__).stat().st_dev
    block = (Path('/sys/dev/block') / f'{os.major(device)}:{os.minor(device)}').resolve()
    if (block/'partition').exists():
        block = block.parent
    backing = (block/'dev').read_text().strip()
    disk_limit = next((line for line in limits['io.max'].splitlines() if line.split()[0] == backing), '')
    if 'rbps=30000000' not in disk_limit or 'wbps=30000000' not in disk_limit:
        raise SystemExit('Verification requires enforced 30 MB/s disk limits')
    print('Enforced resource limits: '+json.dumps(limits),flush=True)
    area=Path(__file__).resolve().parents[2]
    output=args.output.resolve();output.mkdir(exist_ok=False,parents=True)
    scratch=output/'scratch';scratch.mkdir()
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',
             COLLIMATOR_NUM_THREADS='2',TMPDIR=str(scratch))
    env['PYTHONPATH']=str(area/'candidate/src')
    result={'limits':limits,'input':str(args.input.resolve()),'input_sha256':hashlib.sha256(args.input.read_bytes()).hexdigest(),
            'runs':[],'status':'running'}
    receipt=output/'results.json'
    def save():receipt.write_text(json.dumps(result,indent=2)+'\n')
    save()
    print('Running complete isolated test suite',flush=True)
    with (output/'tests.log').open('w') as log:
        tests=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=area/'candidate',env=env,stdout=log,stderr=subprocess.STDOUT)
    result['test_returncode']=tests.returncode
    save()
    if tests.returncode:
        raise SystemExit('Tests failed; benchmarks not started')
    print('Tests passed',flush=True)
    for scale in ('capture','mature'):
        fixture=None
        if scale=='mature':
            fixture=output/'mature.sqlite'
            result['fixture']=create_mature_fixture(fixture,args.mature_gib)
            save()
        for variant,mode in [('baseline','bulk'),('candidate','global'),('candidate','parallel'),('candidate','sorted')]:
            env['PYTHONPATH']=str(area/variant/'src')
            command=[sys.executable,str(area/'candidate/scripts/replay_vocabulary.py'),'replay',
                     '--input',str(args.input.resolve()),'--scratch',str(scratch),
                     '--mode',mode,'--shard-batches','16','--token-ids','stable']
            if fixture:command.extend(['--prefill',str(fixture)])
            name=f'{scale}-{variant}-{mode}'
            print('Starting '+name,flush=True)
            with (output/f'{name}.log').open('w') as log:
                process=subprocess.run(command,cwd=area/variant,env=env,stdout=log,stderr=subprocess.STDOUT)
            if process.returncode:
                result['status']='failed';result['failed_run']=name;save()
                raise SystemExit(f'{name} failed: {process.returncode}')
            row=json.loads((output/f'{name}.log').read_text().splitlines()[-1])
            row.update(scale=scale,variant=variant)
            result['runs'].append(row);save()
            print(name+': '+json.dumps({k:row[k] for k in ('elapsed_seconds','merge_seconds','materialize_seconds','digest')}),flush=True)
        runs=[row for row in result['runs'] if row['scale']==scale]
        if len({row['digest'] for row in runs})!=1 or len({row['keys'] for row in runs})!=1:
            result['status']='count_mismatch';save()
            raise SystemExit('Exact count comparison failed')
    result['status']='passed';save()
    print('All variants produced identical counts at both scales.',flush=True)


if __name__=='__main__':main()
