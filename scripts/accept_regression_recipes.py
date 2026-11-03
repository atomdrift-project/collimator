#!/usr/bin/env python3
"""Persist test-confirmed recovery recipes without replacing installed models."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from collimator import model_config
from tune_regressed_models import fingerprint


def accept(confirmation, configs, receipt):
    entries=json.loads((confirmation/'candidates.json').read_text())
    results=[]
    for entry in entries:
        route=entry['route'];review=confirmation/route/'complete.json'
        if not review.exists():continue
        result=json.loads(review.read_text())
        if result['status']!='test_confirmed':continue
        candidate=Path(entry['candidate'])
        plan=json.loads((confirmation/route/'plan.json').read_text())
        for relative,digest in plan['hashes']['candidate'].items():
            if fingerprint(candidate/relative)!=digest:raise ValueError(f'Candidate changed: {route}/{relative}')
        benchmark=json.loads((candidate/'benchmark.json').read_text())
        protocol=benchmark.get('training_protocol')
        if protocol is not None and protocol.get('ordinary_train_config_replay_equivalent') is not True:
            # A confirmed artifact is not necessarily a replayable recipe.
            # Dropping its custom holdout/stopping procedure would recreate
            # the refit drift this recovery is intended to repair.
            results.append({'route':route,'status':'requires_artifact_preservation',
                            'candidate':str(candidate),'training_protocol':protocol,
                            'reason':'Ordinary TrainConfig does not reproduce the selected training procedure; retain the exact artifact or implement and verify protocol replay.'})
            continue
        original=model_config.config_path(configs,route)
        backup=receipt/'previous-configs'/f'{route}.json';backup.parent.mkdir(parents=True,exist_ok=True)
        if original.exists() and not backup.exists():backup.write_bytes(original.read_bytes())
        spec=candidate/'feature_spec.json';digest=fingerprint(spec)
        pinned=configs.parent/'model-vocabularies'/route/(digest+'.json');pinned.parent.mkdir(parents=True,exist_ok=True)
        if pinned.exists() and fingerprint(pinned)!=digest:raise ValueError('Pinned vocabulary changed')
        if not pinned.exists():pinned.write_bytes(spec.read_bytes())
        env=dict(benchmark['feature_env'])
        # Recovery fits use every labeled training row subject only to the
        # malware cutoff. A historical MIN_SAMPLE_SCORE pin must not silently
        # filter benign or malware rows when train-best replays this recipe.
        env['COLLIMATOR_MIN_SAMPLE_SCORE']='0'
        env.update(COLLIMATOR_FEATURE_SPEC_FILE=str(pinned.relative_to(configs.parent)),COLLIMATOR_FEATURE_SPEC_SHA256=digest)
        # Normalize the old checkout spelling for a portable repository recipe.
        if env.get('COLLIMATOR_ALLOWED_FEATURES_FILE','').endswith('/src/collimator/data/azoth_allowed_features_importance10k.json'):
            env['COLLIMATOR_ALLOWED_FEATURES_FILE']='src/collimator/data/azoth_allowed_features_importance10k.json'
        recipe={'schema':model_config.SCHEMA,'route':route,
                'train_config':benchmark['train_config'],'feature_env':env,
                'ensemble_seeds':benchmark['seed_health']['accepted_seeds'],
                'min_malware_training_score':benchmark['min_malware_training_score']}
        key=hashlib.sha256(json.dumps(recipe,sort_keys=True).encode()).hexdigest()[:16]
        if original.exists():
            existing=json.loads(original.read_text())
            if existing.get('experiment_key')==key:
                results.append({'route':route,'experiment_key':key,'status':'already_saved'});continue
        recipe.update(experiment_key=key,updated_at=datetime.now(timezone.utc).isoformat(),
            provenance={'kind':'matched_test_confirmed_recovery','candidate':str(candidate),
                        'confirmation':str(review.resolve()),'artifact_hashes':plan['hashes']['candidate'],
                        'recall_1fp_delta':result['target_recall_1fp_delta'],'ap_delta':result['target_ap_delta'],
                        'test_malware':result['profiles']['candidate']['target_malware'],
                        'prediction_contract':plan.get('prediction_contract'),
                        'partition_audit':result.get('partition_audit'),
                        'installed_model_changed':False,
                        'note':'Ranking confirmation; recalibration and routed deployment evaluation remain required.'})
        model_config.save(configs,recipe)
        results.append({'route':route,'experiment_key':key,'status':'saved'})
    receipt.mkdir(parents=True,exist_ok=True)
    receipt_path=receipt/'accepted-recipes.json'
    previous=json.loads(receipt_path.read_text()) if receipt_path.exists() else []
    combined={row['route']:row for row in previous}
    combined.update({row['route']:row for row in results
                     if row['status'] in {'saved','already_saved'}})
    receipt_path.write_text(json.dumps(list(combined.values()),indent=2)+'\n')
    (receipt/'recipe-review.json').write_text(json.dumps(results,indent=2)+'\n')
    return results


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--confirmation',type=Path,required=True)
    p.add_argument('--configs',type=Path,default=model_config.DEFAULT_ROOT)
    p.add_argument('--receipt',type=Path,default=Path('out/experiments/regression-diagnosis-20261031'))
    a=p.parse_args();print(json.dumps(accept(a.confirmation,a.configs,a.receipt),indent=2))
