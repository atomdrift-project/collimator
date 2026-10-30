#!/usr/bin/env python3
"""Recover recent experiment metadata and the complete known acceptance trail.

Archives remain untouched. Historical acceptance is evidence, never an instruction
 to replace the current promoted-baseline registry. --publish-runs exposes recovered
configurations to autocollie's existing run readers without replacing current files.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re

KEY = re.compile(r'^[0-9a-f]{16}$')


def timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        # Legacy naive timestamps have no reliable timezone; use UTC explicitly.
        d = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d.astimezone(timezone.utc)
    except ValueError:
        return None


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    tmp.replace(path)


def refs(value):
    if isinstance(value, dict):
        return set().union(*(refs(v) for v in value.values())) if value else set()
    if isinstance(value, list):
        return set().union(*(refs(v) for v in value)) if value else set()
    return {value} if isinstance(value, str) and KEY.fullmatch(value) else set()



def capture_research_installations(roots, output):
    """Preserve operator-installed research as evidence, without inventing runs."""
    records = []
    for root in map(Path, roots):
        for receipt_path in sorted((root/'deployments').glob('*/specialists-only/installed.json')):
            receipt = json.loads(receipt_path.read_text())
            if receipt.get('status') != 'installed':
                continue
            plan_path = receipt_path.parent/'plan.json'
            if not plan_path.is_file():
                continue
            plan = json.loads(plan_path.read_text())
            installed = set(receipt.get('changed_specialists', []))
            for candidate in plan.get('candidates', []):
                route = 'filetypes/'+candidate['route']
                if route not in installed:
                    continue
                source = Path(candidate['source'])
                if not source.is_absolute():
                    source = root.parent/source
                benchmark = source/'benchmark.json'
                record = {'route': route, 'installed_at': receipt.get('timestamp'),
                          'receipt': str(receipt_path), 'source': str(source),
                          'model_revision': candidate.get('model_revision')}
                if benchmark.is_file():
                    record['benchmark'] = json.loads(benchmark.read_text())
                else:
                    record['missing_benchmark'] = str(benchmark)
                research = source.parent/'candidate/research.json'
                if research.is_file():
                    record['research_choice'] = json.loads(research.read_text()).get('candidate_config')
                records.append(record)
    write_json(Path(output)/'installed-research-snapshots.json', records)
    return records


def recover(roots, output, now, days=30, reports=(), publish_runs=None):
    cutoff = now-timedelta(days=days)
    runs, events, ledgers, replays, invalid, conflicts = {}, {}, [], [], [], []
    source_ranges = []
    pinned = set()
    for root in roots:  # Newer/current sources last, with explicit conflict records.
        root = Path(root)
        dates = []
        event_path = root/'autocollie/events.jsonl'
        if event_path.exists():
            for n, line in enumerate(event_path.open(), 1):
                try:
                    event = json.loads(line)
                    if not isinstance(event, dict):
                        raise ValueError('event is not an object')
                except ValueError:
                    invalid.append({'source': str(event_path), 'line': n, 'raw': line.rstrip('\n')})
                    continue
                t = timestamp(event.get('ts'))
                if t:
                    dates.append(t)
                canonical = json.dumps(event, sort_keys=True, separators=(',', ':'))
                events.setdefault(canonical, {'event': event, 'sources': []})['sources'].append({'path': str(event_path), 'line': n})
        source_ranges.append({'root': str(root), 'event_start': min(dates).isoformat() if dates else None,
                              'event_end': max(dates).isoformat() if dates else None})
        ledger = root/'models/azoth/.autocollie/promoted_baselines.json'
        if ledger.is_file():
            d = json.loads(ledger.read_text())
            ledgers.append({'source': str(ledger), 'document': d})
            # Preserve retired entries too: they explain reversals of decisions.
            pinned.update(refs(d))
        replay = root/'autocollie/replay_history.json'
        if replay.is_file():
            replays.append({'source': str(replay), 'document': json.loads(replay.read_text())})
        for path in sorted((root/'experiments/azoth/runs').glob('*.json')):
            if path.name.endswith('_feature_spec.json'):
                continue
            try:
                run = json.loads(path.read_text())
            except ValueError:
                invalid.append({'source': str(path), 'error': 'invalid JSON; possibly still copying'})
                continue
            if not isinstance(run, dict) or not run.get('route') or not isinstance(run.get('experiment_spec'), dict):
                continue
            key = run.get('experiment_key')
            if not isinstance(key, str) or not KEY.fullmatch(key):
                continue
            prior = runs.get(key)
            if prior and prior['run'] != run:
                conflicts.append({'key': key, 'earlier': prior['source'], 'later': str(path)})
            # Within one source prefer canonical key files over dated aliases.
            if prior and Path(prior['source']).parent == path.parent and Path(prior['source']).stem == key and path.stem != key:
                continue
            runs[key] = {'run': run, 'source': str(path)}
    keep = pinned | {k for k,v in runs.items() if (timestamp(v['run'].get('timestamp')) or datetime.min.replace(tzinfo=timezone.utc)) >= cutoff}
    chosen_events, cycles = set(), set()
    # Include the entire screen/confirm/promote chain of retained configurations.
    # Retention of a late decision also retains its earlier input experiments.
    changed = True
    while changed:
        changed = False
        for identity, record in events.items():
            e = record['event']; t = timestamp(e.get('ts')); cycle = e.get('cycle_id')
            keys = refs(e.get('payload') or {})
            if identity in chosen_events or ((t is not None and t >= cutoff) or keys & keep or (cycle and cycle in cycles)):
                before = len(keep)+len(chosen_events)+len(cycles)
                chosen_events.add(identity); keep.update(keys)
                if cycle:
                    cycles.add(cycle)
                changed |= before != len(keep)+len(chosen_events)+len(cycles)
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output must be empty; use a new snapshot directory')
    (output/'runs').mkdir(parents=True, exist_ok=True)
    selected = sorted((events[k] for k in chosen_events), key=lambda r:r['event'].get('ts',''))
    with (output/'events.jsonl').open('w') as f, (output/'decisions.jsonl').open('w') as decisions:
        for r in selected:
            e = r['event']; line = json.dumps(e, sort_keys=True)+'\n';f.write(line)
            p = e.get('payload') or {}
            if p.get('verdict') or e.get('type') in {'auto-no-winner','spec-rejected','promote-baseline-published','screen-crashed','screen-corpus-empty'}:
                decisions.write(line)
    provenance = {}
    published, publish_conflicts = 0, []
    for key in sorted(keep & runs.keys()):
        record = runs[key];write_json(output/'runs'/f'{key}.json', record['run'])
        provenance[key] = {'source': record['source'], 'retention': 'accepted_or_decision_dependency' if key in pinned or (timestamp(record['run'].get('timestamp')) or datetime.min.replace(tzinfo=timezone.utc)) < cutoff else 'recent',
                           'sha256':hashlib.sha256((output/'runs'/f'{key}.json').read_bytes()).hexdigest()}
        if publish_runs is not None:
            target = Path(publish_runs)/f'{key}.json'
            if target.exists():
                try:
                    if json.loads(target.read_text()) != record['run']:
                        publish_conflicts.append(str(target))
                except ValueError:
                    publish_conflicts.append(str(target))
            else:
                write_json(target, record['run']);published += 1
    retained_reports = []
    for directory in reports:
        for path in sorted(Path(directory).glob('*.md')):
            # Confirm/promote report names include the original experiment key.
            if not any(k in keep for k in re.findall(r'[0-9a-f]{16}', path.name)):
                continue
            dest = output/'reports'/path.name
            dest.parent.mkdir(exist_ok=True)
            if dest.exists() and dest.read_bytes() != path.read_bytes():
                conflicts.append({'report':str(path),'destination':str(dest)})
                continue
            dest.write_bytes(path.read_bytes());retained_reports.append(str(path))
    installed_research = capture_research_installations(roots, output)
    write_json(output/'accepted-baseline-snapshots.json', ledgers)
    write_json(output/'replay-snapshots.json', replays)
    write_json(output/'invalid-records.json', invalid)
    write_json(output/'source-conflicts.json', conflicts)
    write_json(output/'event-provenance.json', selected)
    write_json(output/'run-provenance.json', provenance)
    manifest = {'schema':'autocollie.recovered_history.v1', 'as_of':now.isoformat(),'cutoff':cutoff.isoformat(),'days':days,
                'retention':'recent records plus historical accepted configurations and their decision dependencies',
                'source_ranges':source_ranges,'runs':len(provenance),'events':len(selected),'reports':len(retained_reports),
                'installed_research_configurations':len(installed_research), 'accepted_registry_snapshots':len(ledgers),'missing_referenced_runs':sorted(keep-runs.keys()),
                'invalid_records':len(invalid),'source_conflict_count':len(conflicts),
                'source_conflicts_file':'source-conflicts.json','published_runs':published,
                'publish_conflicts':publish_conflicts,'current_promotions_modified':False,
                'caveat':'Event date gaps do not establish inactivity or completeness; source archives are retained unchanged.'}
    write_json(output/'manifest.json', manifest)
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--roots',nargs='+',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--as-of',default=datetime.now(timezone.utc).isoformat())
    p.add_argument('--days',type=int,default=30)
    p.add_argument('--reports',nargs='*',type=Path,default=[])
    p.add_argument('--publish-runs',type=Path)
    p.add_argument('--publish-events',type=Path,help='Atomically point autocollie history/events.jsonl at this snapshot')
    a=p.parse_args()
    if a.days<1 or timestamp(a.as_of) is None:p.error('days must be positive and as-of must be an ISO timestamp')
    result = recover(a.roots,a.output,timestamp(a.as_of),a.days,a.reports,a.publish_runs)
    if a.publish_events:
        a.publish_events.parent.mkdir(parents=True,exist_ok=True)
        temporary = a.publish_events.with_suffix('.tmp')
        temporary.symlink_to(os.path.relpath(a.output/'events.jsonl',a.publish_events.parent))
        temporary.replace(a.publish_events)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
