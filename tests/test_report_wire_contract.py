"""Reader defaults follow cleave's CompactFile/CompactTrait wire contract."""
import math

import numpy as np
import pytest

from collimator import features


@pytest.mark.parametrize('legacy', [False, True])
def test_missing_confidence_matches_explicit_zero_in_features_and_discovery(legacy):
    id_key,crit_key,conf_key = ('i','l','c') if legacy else ('id','crit','conf')
    findings_key,files_key = ('ts','fs') if legacy else ('traits','files')
    finding = {id_key:'objectives/execution/shell/bash::finding', crit_key:5}
    missing = {'path':'sample','type':'shell',findings_key:[finding]}
    zero = {**missing, findings_key:[{**finding,conf_key:0.0}]}
    certain = {**missing, findings_key:[{**finding,conf_key:1.0}]}
    assert features._ranked_ngram_paths(missing,128) == []
    assert features._ngram_paths_for_file(missing) == []
    assert features._summarize_findings([finding]).hostile_finding_count == 0
    assert features._ranked_ngram_paths(certain,128) == ['objectives/execution/shell/bash']
    report_missing,report_zero = {files_key:[missing]},{files_key:[zero]}
    spec = features.build_vocab([report_missing,report_zero,{files_key:[certain]}])
    np.testing.assert_array_equal(features.extract(report_missing,spec),features.extract(report_zero,spec))


def test_modern_zero_confidence_is_authoritative_over_legacy_alias():
    finding={'id':'objectives/execution/shell/bash::finding','crit':5,'conf':0.0,'c':1.0}
    assert features.finding_conf(finding)==0.0
    assert features._summarize_findings([finding]).hostile_finding_count==0


def test_parent_zero_and_omitted_zero_depth_match_current_wire():
    files=[{'id':0,'path':'archive','type':'zip','traits':[]},
           {'id':1,'pid':0,'path':'archive!!child','type':'shell','depth':1,'traits':[]}]
    assert features.report_depths(files)==[0,1]
    assert not features.file_has_parent(files[0])
    assert features.file_has_parent(files[1])
    report={'v':'8','files':files};spec=features.build_vocab([report]);vec=features.extract(report,spec)
    assert vec[spec.feature_names.index('struct:max_nesting_depth_log')]==pytest.approx(math.log1p(1))
    assert vec[spec.feature_names.index('struct:inner_file_ratio')]==pytest.approx(.5)


def test_parent_link_does_not_invent_depth_for_zero_depth_occurrence():
    # Current CompactFile omits zero, even if an occurrence has a relation to
    # another file. Parent presence and archive nesting are separate inputs.
    files=[{'id':0,'path':'source'}, {'id':1,'path':'fetched','pid':0}]
    assert features.report_depths(files)==[0,0]
    assert features.file_has_parent(files[1])
