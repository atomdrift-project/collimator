"""Current per-model knobs shared by training, research, and deployment."""
from __future__ import annotations
from pathlib import Path
import json
from . import bundle

DEFAULT_ROOT = Path(__file__).resolve().parents[2]/'model-configs'
SCHEMA = 'azoth.model_config.v1'


def config_path(root, route):
    parts = route.split('/')
    if route != 'general' and (len(parts)!=2 or parts[0] not in {'filetypes','filegroups'}):
        raise ValueError(f'Invalid model route: {route}')
    if any(p in {'','.','..'} or '\\' in p for p in parts):
        raise ValueError(f'Invalid model route: {route}')
    return Path(root)/f'{route}.json'


def as_run(document):
    if document.get('schema') != SCHEMA or not isinstance(document.get('train_config'),dict) or not isinstance(document.get('feature_env'),dict):
        raise ValueError('Invalid per-model configuration')
    cutoff=document.get('min_malware_training_score')
    if isinstance(cutoff,bool) or not isinstance(cutoff,int) or not 0<=cutoff<=9:
        raise ValueError('Invalid malware cutoff')
    return {'route':document['route'],'experiment_key':document.get('experiment_key'),
            'idea':'accepted_model_config','timestamp':document.get('updated_at'),
            'train_config':document['train_config'],'feature_env':document['feature_env'],
            'experiment_spec':{'seed':document['train_config'].get('seed',42),
              'filters':{'min_sample_score':int(document['feature_env'].get('COLLIMATOR_MIN_SAMPLE_SCORE','0')),
                         'min_malware_training_score':cutoff},
              'train_config':document['train_config'],'feature_env':document['feature_env']}}


def load(route, root=DEFAULT_ROOT):
    path=config_path(root,route)
    if not path.is_file():return None
    d=json.loads(path.read_text())
    if d.get('route')!=route:raise ValueError(f'{path}: route mismatch')
    as_run(d)
    if d.get('retired_at'):return None
    # Accepted configurations travel with the repository. Resolve their file
    # pins from its root rather than the caller's working directory.
    value = d['feature_env'].get('COLLIMATOR_ALLOWED_FEATURES_FILE')
    if value and not Path(value).is_absolute():
        d['feature_env']['COLLIMATOR_ALLOWED_FEATURES_FILE'] = str(
            DEFAULT_ROOT.parent / value)
    return d


def save(root, document):
    as_run(document)
    bundle.atomic_write_json(config_path(root,document['route']),document)
