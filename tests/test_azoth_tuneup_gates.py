"""Staging must never retain old seeds or write back into the source bundle."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from azoth_tuneup_gates import stage
from collimator import cache_identity


def write_model(root, seed, content):
    (root/'models').mkdir(parents=True)
    (root/'models'/f'seed_{seed}.onnx').write_bytes(content)
    (root/'feature_spec.json').write_text('{}')
    cache_identity.write_training_provenance(root)


def test_stage_replaces_old_ensemble_and_rewrites_paths(tmp_path):
    source=tmp_path/'source';root=tmp_path/'research'
    write_model(source/'general',42,b'general')
    write_model(source/'filetypes/rust',42,b'old specialist')
    candidate=root/'rust/candidate-fulltrain'
    write_model(candidate,43,b'new specialist')
    payload={'kind':'filetype','name':'rust','output_dir':str(candidate),
             'spec_path':str(candidate/'feature_spec.json'),
             'model_path':str(candidate/'models/seed_43.onnx')}
    (candidate/'benchmark.json').write_text(json.dumps(payload))
    (source/'specialists.json').write_text(json.dumps({'results':[
        {'kind':'general','name':'general','output_dir':str(source/'general')},
        {'kind':'filetype','name':'rust','output_dir':str(source/'filetypes/rust')}]}))
    dest=stage(root,source,['rust'])
    assert [p.name for p in (dest/'filetypes/rust/models').iterdir()]==['seed_43.onnx']
    assert (source/'filetypes/rust/models/seed_42.onnx').read_bytes()==b'old specialist'
    result=json.loads((dest/'specialists.json').read_text())['results'][-1]
    assert result['output_dir']==str(dest/'filetypes/rust')
    assert result['model_path']==str(dest/'filetypes/rust/models/seed_43.onnx')
    assert stage(root,source,['rust'])==dest
    (candidate/'models/seed_43.onnx').write_bytes(b'replaced')
    cache_identity.write_training_provenance(candidate)
    with pytest.raises(ValueError,match='Staged candidates changed'):
        stage(root,source,['rust'])
