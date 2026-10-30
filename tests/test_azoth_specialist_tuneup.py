"""Keep tune-up selection isolated from final assessment and resume order."""
import json
import sys
from pathlib import Path
import numpy as np
import pytest
from scipy import sparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import azoth_specialist_tuneup as study


def cohort(labels,buckets):
    y=np.asarray(labels);b=np.asarray(buckets);ids=np.arange(len(y))
    return sparse.csr_matrix(ids[:,None]),y,b,np.array(['rust']*len(y)),ids


def test_small_dev_is_reserved_for_assessment():
    train=cohort([0,1,0,1],[.05,.2,.8,.9]);dev=cohort([0,1],[.1,.8])
    assert study.choose_mode(dev)=='train_selection_dev_assessment'
    fit,stop,x,y,selection,ft=study.partition_evaluation(train,dev,'train_selection_dev_assessment')
    np.testing.assert_array_equal(fit,[False,True,False,False])
    np.testing.assert_array_equal(stop,[True,False,False,False])
    np.testing.assert_array_equal(selection,[True,True,False,False])
    np.testing.assert_array_equal(y[~selection],dev[1])
    assert not np.any(fit & stop)


def test_large_dev_uses_separate_selection_and_assessment_halves():
    dev=cohort([0,1]*60,[.1]*60+[.8]*60)
    assert study.choose_mode(dev)=='dev_halves'
    train=cohort([0,1],[.05,.7])
    fit,stop,x,y,selection,ft=study.partition_evaluation(train,dev,'dev_halves')
    assert selection.sum()==60
    np.testing.assert_array_equal(y,dev[1])


def test_resume_stage_ignores_future_candidate_results(tmp_path):
    rows=[{'variant':name,'selection':{'ap':ap,'at_fp':{'5':{'recall':.5}}}}
          for name,ap in [('baseline',.7),('cap5',.8),('metadata',.95)]]
    (tmp_path/'selection.json').write_text(json.dumps({'comparisons':rows}))
    assert study.stage_winner(tmp_path,{'baseline','cap5'})['variant']=='cap5'


def test_low_fp_objective_prefers_operating_recall_over_average_precision(tmp_path):
    rows=[]
    for name,ap,recall in [('high_ap',.99,.2),('high_low_fp_recall',.9,.6)]:
        rows.append({'variant':name,'selection':{'ap':ap,'at_fp':{
            str(k):{'recall':recall} for k in (0,1,5)}}})
    (tmp_path/'selection.json').write_text(json.dumps({'comparisons':rows}))
    allowed={r['variant'] for r in rows}
    assert study.stage_winner(tmp_path,allowed)['variant']=='high_ap'
    assert study.stage_winner(tmp_path,allowed,'low-fp')['variant']=='high_low_fp_recall'


def test_expanded_training_keeps_small_route_selection_fixed():
    original=cohort([0,1,0,1],[.05,.2,.8,.9])
    expanded=cohort([0,1,0,1,1,1],[.05,.2,.8,.9,.4,.85])
    dev=cohort([0,1],[.1,.8])
    before=study.partition_evaluation(original,dev,'train_selection_dev_assessment')
    after=study.partition_evaluation(expanded,dev,'train_selection_dev_assessment',original)
    np.testing.assert_array_equal(after[0],[False,True,False,False,True,False])
    np.testing.assert_array_equal(after[2].toarray(),before[2].toarray())
    for old,new in zip(before[3:],after[3:]):
        np.testing.assert_array_equal(old,new)


def test_feature_alignment_preserves_reference_order_and_rejects_missing_rows():
    original=cohort([0,1,0,1],[.05,.2,.8,.9])
    expanded=cohort([0,1,0,1,1],[.05,.2,.8,.9,.4])
    index=np.array([4,2,0,3,1])
    shuffled=(expanded[0][index],*(a[index] for a in expanded[1:]))
    actual=study.align_cohort(shuffled,original)
    np.testing.assert_array_equal(actual[0].toarray(),original[0].toarray())
    np.testing.assert_array_equal(actual[4],original[4])
    with pytest.raises(ValueError,match='identities'):
        study.align_cohort(original,expanded)
