"""Current per-model knobs shared by training, research, and deployment."""
from __future__ import annotations
from pathlib import Path
import json
import hashlib
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
    seeds = document.get('ensemble_seeds')
    if seeds is not None:
        validate_ensemble_seeds(seeds)
    return {'route':document['route'],'experiment_key':document.get('experiment_key'),
            **({'ensemble_seeds':seeds} if seeds is not None else {}),
            'idea':'accepted_model_config','timestamp':document.get('updated_at'),
            'train_config':document['train_config'],'feature_env':document['feature_env'],
            'experiment_spec':{'seed':document['train_config'].get('seed',42),
              'filters':{'min_sample_score':int(document['feature_env'].get('COLLIMATOR_MIN_SAMPLE_SCORE','0')),
                         'min_malware_training_score':cutoff},
              'train_config':document['train_config'],'feature_env':document['feature_env']}}


def validate_ensemble_seeds(seeds):
    """Accepted ensemble membership is part of the recipe, not a global default."""
    if (not isinstance(seeds, list) or not seeds
            or any(type(seed) is not int or seed < 0 for seed in seeds)
            or len(set(seeds)) != len(seeds)):
        raise ValueError('ensemble_seeds must be a nonempty list of distinct nonnegative integers')
    return seeds


def parse_ensemble_seeds(raw):
    if not raw.strip():
        return None
    return validate_ensemble_seeds([int(value.strip()) for value in raw.split(',')])


def feature_spec_digest(env):
    path = env.get('COLLIMATOR_FEATURE_SPEC_FILE')
    if not path:
        return ''
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    expected = env.get('COLLIMATOR_FEATURE_SPEC_SHA256')
    if expected and digest != expected:
        raise ValueError(f'Accepted feature specification changed: {path}')
    return digest


def pinned_feature_spec(env):
    if not feature_spec_digest(env):
        return None
    from .features import FeatureSpec
    return FeatureSpec.load(env['COLLIMATOR_FEATURE_SPEC_FILE'])


def load(route, root=DEFAULT_ROOT):
    path=config_path(root,route)
    if not path.is_file():return None
    d=json.loads(path.read_text())
    if d.get('route')!=route:raise ValueError(f'{path}: route mismatch')
    as_run(d)
    if d.get('retired_at'):return None
    # Accepted configurations travel with the repository. Resolve their file
    # pins from its root rather than the caller's working directory.
    for key in ('COLLIMATOR_ALLOWED_FEATURES_FILE', 'COLLIMATOR_FEATURE_SPEC_FILE'):
        value = d['feature_env'].get(key)
        if value and not Path(value).is_absolute():
            d['feature_env'][key] = str(DEFAULT_ROOT.parent / value)
    feature_spec_digest(d['feature_env'])
    return d


def save(root, document):
    as_run(document)
    bundle.atomic_write_json(config_path(root,document['route']),document)
