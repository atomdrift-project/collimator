#!/usr/bin/env python3
"""Finish ordered research candidates, then run the normal isolated bundle gates."""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import shutil
import subprocess
import sys
import time

import azoth_portable_stability as study
from collimator import cache_identity

ROUTES = ['rust', 'xml', 'java', 'vsix', 'gem']
LOG = logging.getLogger('tuneup_gates')


def stage(root, source, routes):
    dest = root/'gate-bundle'
    revisions = {}
    for route in routes:
        candidate = root/route/'candidate-fulltrain'
        cache_identity.require_reserved_dev(candidate)
        revisions[route] = json.loads((candidate/'training_provenance.json').read_text())
    if (dest/'tuneup-stage.json').exists():
        recorded = json.loads((dest/'tuneup-stage.json').read_text())
        if recorded['routes'] != routes or recorded['candidate_revisions'] != revisions:
            raise ValueError('Staged candidates changed; use a new experiment output directory')
        return dest
    # Resume a partial copy only inside this experiment-owned directory.
    shutil.copytree(source, dest, dirs_exist_ok=True)
    summary = json.loads((dest/'specialists.json').read_text())
    for route in routes:
        candidate = root/route/'candidate-fulltrain'
        cache_identity.require_reserved_dev(candidate)
        target = dest/'filetypes'/route
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(candidate, target)
        payload = json.loads((target/'benchmark.json').read_text())
        summary['results'] = [r for r in summary['results'] if not (r['kind']=='filetype' and r['name']==route)]
        summary['results'].append(payload)
    summary['output_root'] = str(dest)
    for item in summary['results']:
        directory = dest/('general' if item['kind']=='general' else ('filetypes' if item['kind']=='filetype' else 'filegroups'))
        if item['kind'] != 'general':
            directory /= item['name']
        for field in ('output_dir', 'source_dir'):
            if field in item:
                item[field] = str(directory)
        for field in ('model_path', 'spec_path'):
            if field in item:
                old = Path(item[field])
                item[field] = str(directory/('models' if old.parent.name=='models' else '')/old.name)
        if (directory/'benchmark.json').exists() and not item.get('error'):
            study.write_json(directory/'benchmark.json', item)
    study.write_json(dest/'specialists.json', summary)
    study.write_json(dest/'tuneup-stage.json', {'routes':routes,'source':str(source),
        'candidate_revisions':revisions,
        'general_model_revision':cache_identity.model_revision(dest/'general')})
    return dest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('out/experiments/specialist-tuneup-20261027'))
    parser.add_argument('--source', type=Path, default=Path('out/models/azoth'))
    parser.add_argument('--wait', action='store_true')
    parser.add_argument('--routes', nargs='+', default=ROUTES)
    parser.add_argument('--workers', type=int, default=16)
    parser.add_argument('--parallelism', type=int, default=2)
    parser.add_argument('--threads', type=int, default=4)
    args = parser.parse_args()
    if min(args.workers, args.parallelism, args.threads) < 1:
        parser.error('workers, parallelism, and threads must be positive')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    for route in args.routes:
        while not (args.root/route/'complete.json').exists():
            status_path = args.root/'status.json'
            status = json.loads(status_path.read_text()) if status_path.exists() else []
            if any(row['route']==route and row['status']=='failed' for row in status):
                raise RuntimeError(f'Research failed for {route}; resolve before gating')
            if not args.wait:
                raise RuntimeError(f'Research not complete for {route}')
            time.sleep(30)
        LOG.info('Refitting frozen choice for %s', route)
        subprocess.run([sys.executable, 'scripts/azoth_tuneup_fulltrain.py', '--root',str(args.root), '--routes',route,
                        '--threads',str(args.threads)], check=True)
    dest = stage(args.root, args.source, args.routes)
    command = ['make','azoth-validate',f'AZOTH_ROOT={dest}',
               'THRESHOLD_MAX_ID=6309383805',f'EXP_WORKERS={args.workers}',f'AZOTH_CALIBRATE_PARALLELISM={args.parallelism}',
               'AZOTH_DEPLOY_DIR=/home/t/src/azoth','AZOTH_PREVIOUS_BUNDLE=/home/t/src/azoth']
    study.write_json(args.root/'gate-status.json', {'status':'running','command':command})
    LOG.info('Running deployment gates against isolated bundle: %s', dest)
    result = subprocess.run(command)
    study.write_json(args.root/'gate-status.json', {'status':'passed' if result.returncode==0 else 'failed',
                                                  'returncode':result.returncode,'command':command})
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
