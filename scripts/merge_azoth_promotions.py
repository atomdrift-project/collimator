#!/usr/bin/env python3
"""Merge recovered acceptances, preserving newer current and installed decisions."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
from collimator import bundle,model_config


def merge(history, registry, runs, configs):
    old=json.loads((history/'accepted-baseline-snapshots.json').read_text())
    current=json.loads(registry.read_text()) if registry.exists() else {'schema':'autocollie.promoted_baselines.v1','routes':{}}
    routes={}
    for snapshot in old+[{'document':current}]:
        for route,entry in snapshot['document'].get('routes',{}).items():
            if route not in routes or entry.get('updated_at','')>=routes[route].get('updated_at',''):
                routes[route]=entry
    for research in json.loads((history/'installed-research-snapshots.json').read_text()):
        route=research['route'];b=research['benchmark'];spec={'route':route,'seed':b['train_config'].get('seed',42),
          'train_config':b['train_config'],'feature_env':b['feature_env'],
          'filters':{'min_sample_score':int(b['feature_env'].get('COLLIMATOR_MIN_SAMPLE_SCORE','0')),
                     'min_malware_training_score':b['min_malware_training_score']}}
        key=hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()[:16]
        run={'experiment_key':key,'route':route,'idea':'installed_research','timestamp':research['installed_at'],
             'experiment_spec':spec,'train_config':b['train_config'],'feature_env':b['feature_env'],
             'research_provenance':{'receipt':research['receipt'],'source':research['source'],
               'model_revision':research['model_revision'],'evaluation':'Research metrics are retained in source artifacts, not relabeled as screening metrics.'}}
        bundle.atomic_write_json(runs/f'{key}.json',run)
        if route not in routes or research['installed_at']>=routes[route].get('updated_at',''):
            routes[route]={'route':route,'full_train_key':key,'updated_at':research['installed_at'],
              'source':'verified_research_installation','configuration_only':True,'model_revision':research['model_revision']}
    # General was explicitly excluded from this specialist refresh. Preserve its
    # recovered promotion as history until it is matched to the current bundle.
    if 'general' in routes and 'general' not in current.get('routes',{}):
        routes['general']['retired_at'] = datetime.now(timezone.utc).isoformat()
        routes['general']['retired_reason'] = 'Recovered historical record; current general configuration not verified. General retraining selection preserved.'
    documents=[]
    for route,entry in routes.items():
        if entry.get('retired_at'):continue
        paths=[runs/f'{entry[k]}.json' for k in ['full_train_key','promote_key'] if entry.get(k)]
        path=next((p for p in paths if p.is_file()),None)
        if path is None:raise ValueError(f'Missing accepted run: {route}')
        r=json.loads(path.read_text());spec=r.get('experiment_spec') or {}
        cutoff=(spec.get('filters') or {}).get('min_malware_training_score')
        if cutoff is None:raise ValueError(f'Missing accepted cutoff: {route}')
        d={'schema':model_config.SCHEMA,'route':route,'experiment_key':r['experiment_key'],
          'updated_at':entry['updated_at'],'train_config':r.get('train_config') or spec['train_config'],
          'feature_env':r.get('feature_env') or spec['feature_env'],
          'min_malware_training_score':cutoff,'provenance':{'run':str(path),'acceptance':entry}}
        existing=model_config.load(route,configs)
        # An edited per-model config is already authoritative; merging history
        # never replaces it. Subsequent accepted changes use the shared writer.
        if existing is None:model_config.save(configs,d)
        documents.append(route)
    for route, entry in routes.items():
        entry['configuration_file'] = str(model_config.config_path(configs, route).relative_to(configs.parent))
    merged={'schema':'autocollie.promoted_baselines.v1','routes':routes}
    if registry.exists() and not registry.with_suffix('.pre-merge.json').exists():
        registry.with_suffix('.pre-merge.json').write_bytes(registry.read_bytes())
    bundle.atomic_write_json(registry,merged)
    return {'routes':len(routes),'model_configs':len(documents),'registry':str(registry),'configs':str(configs)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--history',type=Path,default=Path('out/autocollie/history/20261028'))
    p.add_argument('--registry',type=Path,default=Path('out/models/azoth/.autocollie/promoted_baselines.json'))
    p.add_argument('--runs',type=Path,default=Path('out/experiments/azoth/runs'))
    p.add_argument('--configs',type=Path,default=model_config.DEFAULT_ROOT)
    a=p.parse_args();print(json.dumps(merge(a.history,a.registry,a.runs,a.configs),indent=2))
if __name__=='__main__':main()
