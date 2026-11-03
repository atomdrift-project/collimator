"""Pure OR composition must preserve serving decisions on arbitrary inputs."""
import copy

import numpy as np
import pytest

from collimator import policy


def test_or_union_matches_every_source_rule_with_serving_edge_cases():
    rng = np.random.default_rng(9321)
    probabilities = np.array([0,.1,.5,.9,1,np.nan,np.inf,-np.inf],dtype=np.float32)
    thresholds = [None,-1.,0.,.1,.5,.9,1.,1.+1e-9,1.0001,np.nan,np.inf]
    for _ in range(100):
        scores = {r:rng.choice(probabilities,50) for r in ('a','b','c')}
        rules = [{'thresholds':{r:thresholds[int(rng.integers(len(thresholds)))]
                                for r in ('a','b','missing')}} for _ in range(4)]
        combined = policy.union_threshold_rules(*rules)
        expected = np.logical_or.reduce([policy.margin(scores,r,50)>=0 for r in rules])
        np.testing.assert_array_equal(policy.margin(scores,combined,50)>=0,expected)
        assert combined == policy.union_threshold_rules(*reversed(rules))


def test_l0_union_preserves_every_incumbent_detection_through_the_level_sweep():
    scores={'a':np.array([.1,.2,.9,.1,.3],dtype=np.float32),
            'b':np.array([.2,.1,.1,.9,.4],dtype=np.float32)}
    labels=np.array([0,0,1,1,1])
    original=[{'level':0,'hostile':{'best':{'thresholds':{'a':.8}}}},
              {'level':25,'hostile':{'best':{'blend':{'routes':['a','b'],
                   'weights':[.4,.6],'intercept':0.,'threshold':.3}}}}]
    additional={'thresholds':{'b':.8}}
    updated=copy.deepcopy(original)
    updated[0]['hostile']['best']=policy.union_threshold_rules(original[0]['hostile']['best'],additional)
    for level in (0,1,25,100):
        before=policy.swept_margin(scores,original,level,len(labels))>=0
        after=policy.swept_margin(scores,updated,level,len(labels))>=0
        assert not np.any(before & ~after)
        assert int((after & (labels==0)).sum()) == int((before & (labels==0)).sum())
    l0=policy.swept_margin(scores,updated,0,len(labels))>=0
    assert int((l0 & (labels==1)).sum())==2
    assert updated[1:] == original[1:]


def test_union_rejects_blend_instead_of_discarding_its_decision():
    with pytest.raises(ValueError,match='blend'):
        policy.union_threshold_rules({'thresholds':{'a':.5},'blend':{'routes':['a']}})


def test_union_does_not_mutate_frozen_inputs():
    a={'thresholds':{'a':.5,'b':None}}
    b={'thresholds':{'a':.8,'b':1.0001}}
    saved=copy.deepcopy((a,b))
    assert policy.union_threshold_rules(a,b)=={'thresholds':{'a':.5}}
    assert (a,b)==saved
