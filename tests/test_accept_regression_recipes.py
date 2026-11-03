import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from accept_regression_recipes import accept
from collimator import features, model_config


@pytest.mark.parametrize('protocol', [
    {'kind': 'frozen_research_canonical_holdout_v1',
     'ordinary_train_config_replay_equivalent': False},
    {'kind': 'unverified_custom_holdout'},
])
def test_confirmed_custom_artifact_cannot_overwrite_a_replayable_recipe(tmp_path, protocol):
    confirmation = tmp_path / 'confirmation'
    review = confirmation / 'filetypes/lnk'
    review.mkdir(parents=True)
    candidate = tmp_path / 'candidate'
    candidate.mkdir()
    benchmark = {'training_protocol': protocol}
    (candidate / 'benchmark.json').write_text(json.dumps(benchmark))
    digest = hashlib.sha256((candidate / 'benchmark.json').read_bytes()).hexdigest()
    (review / 'plan.json').write_text(json.dumps({
        'hashes': {'candidate': {'benchmark.json': digest}}}))
    (review / 'complete.json').write_text(json.dumps({'status': 'test_confirmed'}))
    (confirmation / 'candidates.json').write_text(json.dumps([
        {'route': 'filetypes/lnk', 'candidate': str(candidate)}]))
    configs = tmp_path / 'model-configs'
    recipe = configs / 'filetypes/lnk.json'
    recipe.parent.mkdir(parents=True)
    recipe.write_text('existing accepted recipe\n')
    receipt = tmp_path / 'receipt'
    receipt.mkdir()
    previous = [{'route': 'filetypes/lnk', 'status': 'saved', 'experiment_key': 'prior'}]
    (receipt / 'accepted-recipes.json').write_text(json.dumps(previous))
    result = accept(confirmation, configs, receipt)
    assert result[0]['status'] == 'requires_artifact_preservation'
    assert recipe.read_text() == 'existing accepted recipe\n'
    assert not (tmp_path / 'model-vocabularies').exists()
    assert not (receipt / 'previous-configs').exists()
    assert json.loads((receipt / 'accepted-recipes.json').read_text()) == previous
    assert json.loads((receipt / 'recipe-review.json').read_text()) == result


def test_acceptance_requires_confirmation_and_unchanged_artifacts(tmp_path,monkeypatch):
    confirmation=tmp_path/'confirmation';review=confirmation/'filetypes/html'
    review.mkdir(parents=True)
    candidate=tmp_path/'candidate';candidate.mkdir()
    features.FeatureSpec(total_features=1,feature_names=['agg:n_findings']).save(candidate/'feature_spec.json')
    benchmark={'train_config':{'n_estimators':100},'feature_env':{'COLLIMATOR_MIN_SAMPLE_SCORE':'3'},
               'seed_health':{'accepted_seeds':[43]},'min_malware_training_score':0}
    (candidate/'benchmark.json').write_text(json.dumps(benchmark))
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in candidate.iterdir()}
    (review/'plan.json').write_text(json.dumps({'hashes':{'candidate':hashes}}))
    (confirmation/'candidates.json').write_text(json.dumps([{'route':'filetypes/html','candidate':str(candidate)}]))
    result={'status':'held_back'}
    (review/'complete.json').write_text(json.dumps(result))
    configs=tmp_path/'model-configs';receipt=tmp_path/'receipt'
    assert accept(confirmation,configs,receipt)==[]
    assert not (configs/'filetypes/html.json').exists()
    result.update(status='test_confirmed',target_recall_1fp_delta=.1,target_ap_delta=.02,
                  profiles={'candidate':{'target_malware':100}})
    (review/'complete.json').write_text(json.dumps(result))
    assert accept(confirmation,configs,receipt)[0]['status']=='saved'
    monkeypatch.setattr(model_config,'DEFAULT_ROOT',configs)
    saved=model_config.load('filetypes/html',configs)
    assert saved['ensemble_seeds']==[43]
    assert saved['feature_env']['COLLIMATOR_MIN_SAMPLE_SCORE']=='0'
    assert model_config.pinned_feature_spec(saved['feature_env']).total_features==1
    assert accept(confirmation,configs,receipt)[0]['status']=='already_saved'
    (candidate/'feature_spec.json').write_text('{}')
    with pytest.raises(ValueError,match='Candidate changed'):
        accept(confirmation,configs,receipt)
