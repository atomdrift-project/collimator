#!/usr/bin/env python3
"""WHL feature-family ablation on the already viewed research cohorts."""
import json
from pathlib import Path
import numpy as np

import whl_recall_search as capacity
from collimator.bundle import atomic_write_json


class Study(capacity.Study):
    def matrix(self, layout):
        if layout not in self.layouts:
            names = json.loads((self.source / 'base_spec.json').read_text())['feature_names']
            if layout.startswith('traits'):
                keep = [i for i, n in enumerate(names) if n.split(':')[0] in {'present', 'maxcrit'}]
            else:
                keep = [i for i, n in enumerate(names) if n.split(':')[0] not in
                        {'agg', 'ext', 'metrics', 'struct', 'formula', 'score', 'missing'}]
            self.layouts[layout] = self.base[:, keep]
            atomic_write_json(self.output / (layout + '-columns.json'), keep)
        return self.layouts[layout]


def main():
    root = Path('out/experiments/whl-80-20261102/ablation')
    study = Study(Path('out/experiments/weak-specialist-keywords-20261102/whl'), root)
    settings = capacity.plans()
    plans = {f'{layout}-{shape}': dict(settings['base-' + shape], layout=layout)
             for layout in ('base', 'traits', 'no-member-statistics')
             for shape in ('current', 'fine', 'extra')}
    atomic_write_json(root / 'ablation-plan.json', dict(plans=plans,
        limitation='Both development halves and the reserved training groups were viewed previously; exploratory follow-up.'))
    if not (root / 'ablation-locked.json').exists():
        results = [study.run(name, plan, 43) for name, plan in plans.items()]
        baseline = results[0]['search']
        eligible = [r for r in results if r['search']['ap'] >= baseline['ap'] - .01]
        best = max(eligible, key=lambda r: (r['search']['recall_1fp'],r['search']['recall_0fp'],r['search']['ap']))
        atomic_write_json(root / 'ablation-locked.json', dict(names=list(dict.fromkeys(['base-current',best['name']])), results=results))
    locked = json.loads((root / 'ablation-locked.json').read_text())
    results = {}
    for name in locked['names']:
        for seed in (43,44,45,46):
            study.run(name, plans[name], seed)
        p = np.mean([np.load(root/'fits'/name/str(seed)/'predictions.npz')['scores'].astype(np.float64)
                     for seed in (43,44,45,46)],axis=0).astype(np.float32)
        results[name] = {label: capacity.metrics(study.y[mask],p[mask]) for label,mask in
                        [('reserved_training_groups',study.reserved),('dev_confirmation',study.dev_confirm)]}
        atomic_write_json(root/'ablation-confirmation.json',results)
        print('CONFIRM',name,json.dumps(results[name]),flush=True)


if __name__ == '__main__':
    main()
