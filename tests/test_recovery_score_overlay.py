import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import prepare_recovery_score_overlay as overlay


def test_overlay_matches_by_id_and_report_version_without_changing_coverage():
    metadata = {'row_ids': np.array([30, 10, 20, 40, 50]), 'labels': np.array([1, 0, 1, 0, 1])}
    table = {'ids': np.array([10, 20, 30, 40]), 'labels': np.array([0, 1, 1, 1]),
             'probability': np.array([.1, .9, .8, .3], dtype=np.float32),
             'fingerprints': np.array([b'a'*32, b'x'*32, b'c'*32, b'd'*32], dtype='V32')}
    reference = np.array([b'c'*32, b'a'*32, b'b'*32, b'd'*32, b'e'*32], dtype='V32')
    probs, digests, keep = overlay.align_scores(table, metadata, np.array([1, 1, 1, 1, 0], bool), reference)
    assert keep.tolist() == [True, True, False, False, True]
    np.testing.assert_array_equal(probs[:2], np.array([.8, .1], np.float32))
    assert np.isnan(probs[2:]).all()
    assert digests[0] == reference[0]


def test_overlay_excludes_training_everywhere_but_selection_only_from_test():
    ids = np.array([1, 2, 3, 4, 5, 6])
    buckets = np.array([0, 40, 0, 40, 0, 40])
    keep = overlay.membership_mask(ids, buckets, [1, 2], [3, 4])
    # ID4 is legitimate calibration data, though it was used for selection.
    assert keep.tolist() == [False, False, False, True, True, True]


def test_overlay_rejects_duplicate_and_foreign_score_ids():
    metadata = {'row_ids': np.array([1, 2]), 'labels': np.array([0, 1])}
    for ids, error in [([1, 1], 'Duplicate'), ([1, 3], 'outside')]:
        table = {'ids': np.array(ids), 'labels': np.array([0, 1]),
                 'probability': np.array([.1, .8]), 'fingerprints': np.zeros(2, dtype='V32')}
        with pytest.raises(ValueError, match=error):
            overlay.align_scores(table, metadata, np.ones(2, bool))


def test_route_identity_accepts_summary_names_and_calibration_paths():
    assert overlay.route_key('archive', 'filegroup') == 'filegroups/archive'
    assert overlay.route_key('filetypes/npm', 'filetype') == 'filetypes/npm'
    assert overlay.route_key('general', 'general') == 'general'


def test_scoped_alias_retains_only_original_coverage_and_is_not_global():
    scores = np.array([[.1, .2, .3], [.4, np.nan, .6]], dtype=np.float32)
    slots, global_routes = overlay.additional_score_slots({
        'filegroups/previous_general': {},
        'filegroups/previous_archive': {'coverage_from': 'filegroups/archive'},
    }, ['general', 'filegroups/archive'], scores)
    assert np.isfinite(slots).tolist() == [[True, True, True], [True, False, True]]
    assert global_routes == ['filegroups/previous_general']
    with pytest.raises(ValueError, match='Unknown.*coverage'):
        overlay.additional_score_slots({'filegroups/bad': {'coverage_from': 'missing'}},
                                       ['general', 'filegroups/archive'], scores)
