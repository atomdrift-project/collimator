#!/usr/bin/env python3
"""Generate Python probability fixtures for Scan tests on trained keyword bundles."""
import argparse
import json
import sys
from pathlib import Path
import lightgbm as lgb
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from collimator.features import FeatureSpec, extract
parser=argparse.ArgumentParser(description='Build real-bundle Python/Scan probability fixtures.')
parser.add_argument('root',type=Path)
parser.add_argument('output',type=Path)
parser.add_argument('--route',default='python')
parser.add_argument('--fixtures',type=Path,default=Path('../scan/src/features/extended_keyword_parity.json'))
args=parser.parse_args()
root=args.root
fixtures=json.loads(args.fixtures.read_text())
output=[]
for variant in ['hierarchy','pooled','context']:
    directory=(root/args.route/variant).resolve()
    spec=FeatureSpec.load(directory/'feature_spec.json')
    models=[lgb.Booster(model_file=str(directory/'models'/f'seed_{seed}.txt')) for seed in [43,44]]
    cases=[]
    for fixture in fixtures:
        vector=extract(fixture['report'],spec).reshape(1,-1)
        probability=np.mean([np.asarray(model.predict(vector,num_threads=4),dtype=np.float32).astype(np.float64) for model in models],axis=0).astype(np.float32)[0]
        cases.append(dict(name=fixture['name'],report=fixture['report'],probability=float(probability)))
    output.append(dict(directory=str(directory),cases=cases))
args.output.write_text(json.dumps(output,indent=2)+'\n')
