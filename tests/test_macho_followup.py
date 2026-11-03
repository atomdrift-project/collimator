"""Fresh follow-up cohorts and sampled-vocabulary support projections."""
import sys
import hashlib
import json
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import macho_followup as followup


def test_fresh_holdouts_exclude_previously_seen_groups_and_preserve_low_scores():
    groups=[f'{i:064x}' for i in range(1000)]
    seen=set(groups[:100])
    rows=[(i,i%2,'train',g,4) for i,g in enumerate(groups)]
    # Same canonical group stays together; evaluation has no score floor.
    holdout=next(g for g in groups[100:] if followup.fraction(g)<.4)
    rows.append((1001,groups.index(holdout)%2,'train',holdout.upper(),0))
    rows.extend([(2000,1,'test','test',9),(2001,1,'dev','dev',9)])
    accepted={'feature_env':{'COLLIMATOR_MIN_SAMPLE_SCORE':'3'},'min_malware_training_score':0}
    train,evaluation,excluded=followup.select_rows(rows,accepted,seen)
    fit_groups={r['group_id'] for r in train};eval_groups={r['group_id'] for r in evaluation}
    assert seen<=fit_groups
    assert not fit_groups & eval_groups
    assert {r['row_id'] for r in evaluation}>={1001}
    assert not {2000,2001} & {r['row_id'] for r in train+evaluation}
    assert not excluded
    assert any(followup.fraction(g)<.2 for g in eval_groups)
    assert any(.2<=followup.fraction(g)<.4 for g in eval_groups)


def test_conflicting_canonical_group_is_excluded_before_assignment():
    accepted={'feature_env':{'COLLIMATOR_MIN_SAMPLE_SCORE':'3'},'min_malware_training_score':0}
    train,evaluation,excluded=followup.select_rows([(1,0,'train','aa',4),(2,1,'train','AA',4)],accepted,set())
    assert train==evaluation==[]
    assert len(excluded)==2


def test_followup_cannot_reopen_search_after_finalist_lock(tmp_path):
    study=followup.Study.__new__(followup.Study);study.root=tmp_path
    (tmp_path/'locked_finalists.json').write_text('{}')
    for action in (study.screen,study.refine,study.tail,study.lock):
        with pytest.raises(ValueError,match='locked'):action()


def test_confirmation_rejects_runner_change_before_fitting(tmp_path):
    study=followup.Study.__new__(followup.Study)
    study.root=tmp_path
    study.summary_path=tmp_path/'search.json'
    study.summary_path.write_text('{}')
    (tmp_path/'locked_finalists.json').write_text(json.dumps(dict(
        search_sha256=hashlib.sha256(study.summary_path.read_bytes()).hexdigest(),
        runner_sha256='changed')))
    with pytest.raises(ValueError,match='runner changed after lock'):
        study.confirm()
