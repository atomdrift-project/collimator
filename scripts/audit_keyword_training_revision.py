#!/usr/bin/env python3
"""Check numerical equivalence of the two training revisions seen in this screen.

Only the documented CPU device-probe reorder and LightGBM validation-argument
migration are accepted. Reconstruct the earlier revision from git and compare
old/new fit implementations on the screen's full cached JavaScript matrices.
"""
import argparse
import ast
import __future__
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys

import lightgbm as lgb
import numpy as np
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from collimator import train

EXPECTED_OLD = 'de571a1c6f429bd1fa19ca1f91170c7f05d2bf37e7fe0e93158109a682b375de'
EXPECTED_NEW = 'defe0572070e8627b85cc97f4937fddf838a0ff4257851a028fa8acc0238ca34'
FILES = ['train.py', 'fit_resources.py', 'model.py', 'onnx_projection.py', 'experiment.py', 'export.py', 'bundle.py', 'cache_identity.py']


def main(root):
    source = Path(train.__file__).parent
    old_sources = {name: subprocess.check_output(['git', 'show', 'HEAD:src/collimator/' + name]) for name in ['train.py', 'model.py']}
    def revision(legacy):
        digest = hashlib.sha256()
        for name in FILES:
            digest.update(name.encode())
            digest.update(old_sources[name] if legacy and name in old_sources else (source / name).read_bytes())
        for path in sorted((source / 'thresholds').glob('*.py')):
            digest.update(path.read_bytes())
        for package in ['numpy', 'scipy', 'scikit-learn', 'lightgbm', 'xgboost']:
            digest.update(f'{package}={importlib.metadata.version(package)}'.encode())
        return digest.hexdigest()
    assert revision(True) == EXPECTED_OLD, 'earlier source revision was not reconstructed exactly'
    assert revision(False) == EXPECTED_NEW, 'unexpected training change; do not waive it'
    snapshot = root / 'training_revision_sources'
    snapshot.mkdir(exist_ok=True)
    for name, original in old_sources.items():
        (snapshot / ('old_' + name)).write_bytes(original)
        (snapshot / ('new_' + name)).write_bytes((source / name).read_bytes())
    module = ast.parse(old_sources['train.py'])
    node = next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == '_fit_model')
    namespace = dict(train.__dict__)
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'original_train.py', 'exec', flags=__future__.annotations.compiler_flag), namespace)
    old_fit = namespace['_fit_model']
    directory = root / 'javascript'
    spec = json.loads((directory / 'baseline/feature_spec.json').read_text())
    paths = [path for path in (directory / 'cache').glob('matrix_*_spec.json') if json.loads(path.read_text()) == spec]
    assert len(paths) == 1, 'need the unique baseline matrix before cache cleanup'
    stem = str(paths[0])[:-len('_spec.json')]
    x_train, x_dev = sp.load_npz(stem + '_Xtrain.npz'), sp.load_npz(stem + '_Xtest.npz')
    with np.load(stem + '.npz', allow_pickle=True) as arrays:
        y_train, y_dev = arrays['y_train'], arrays['y_test']
    weights = np.where(y_train == 1, 1.2, .8).astype(np.float32)
    checks = []
    for seed in [43,44]:
        parameters = dict(n_estimators=180, num_leaves=96, max_depth=12, learning_rate=.05,
                          min_child_samples=100, min_child_weight=5, subsample=.8,
                          colsample_bytree=1, reg_lambda=1, random_state=seed,
                          n_jobs=4, device_type='cpu', verbosity=-1,
                          scale_pos_weight=float(np.sum(y_train == 0) / np.sum(y_train == 1)))
        models = []
        for fit in [old_fit, train._fit_model]:
            model = lgb.LGBMClassifier(**parameters)
            fit(model, x_train, y_train, sample_weight=weights,
                eval_set=[(x_dev,y_dev)], early_stopping_rounds=25)
            models.append(model)
        old_text, new_text = [model.booster_.model_to_string() for model in models]
        assert old_text == new_text, f'models differ for seed {seed}'
        old_scores, new_scores = [model.predict_proba(x_dev)[:,1] for model in models]
        assert np.array_equal(old_scores,new_scores), f'predictions differ for seed {seed}'
        checks.append(dict(seed=seed, trees=models[0].booster_.num_trees(),
                           model_sha256=hashlib.sha256(old_text.encode()).hexdigest(),
                           predictions_sha256=hashlib.sha256(old_scores.tobytes()).hexdigest(), bit_identical=True))
    result = dict(audited_revisions=[EXPECTED_OLD,EXPECTED_NEW], changed_files=['train.py','model.py'],
                  source_revisions_reconstructed=True, lightgbm=lgb.__version__, train_rows=len(y_train), dev_rows=len(y_dev),
                  checks=checks, conclusion='Equivalent CPU fits for the captured validation-argument migration. No extractor or model-parameter change.')
    (root / 'training_revision_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    args=parser.parse_args()
    main(args.root)
