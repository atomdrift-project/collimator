"""Coverage comparisons must share complete, group-disjoint validation folds."""
import sys
from pathlib import Path

import numpy as np
from scipy import sparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from azoth_plist_tuneup import folds, GRID, BASE
from collimator.train import TrainConfig
from dataclasses import fields


def test_cutoff_comparison_keeps_lower_score_malware_in_validation():
    # Each group has a benign and a high-score positive, plus a lower-score
    # positive with a distinct identity but the same canonical group bucket.
    buckets=np.repeat([.1,.2,.4,.5,.7,.8],3)
    labels=np.tile([0,1,1],6)
    ids=np.arange(len(labels))
    original=ids[np.tile([True,True,False],6)]
    cohort=(sparse.csr_matrix(ids[:,None]), labels, buckets, np.array(['plist']*len(ids)), ids)
    seen=np.zeros(len(ids),dtype=int)
    for fitting,validation,eligible in folds(cohort,original):
        seen+=validation
        assert not np.any(fitting & validation)
        assert not set(buckets[fitting]) & set(buckets[validation])
        assert np.sum(labels[validation & ~eligible])==2
        assert np.sum(labels[fitting])>np.sum(labels[fitting & eligible])
    np.testing.assert_array_equal(seen,np.ones(len(ids)))


def test_every_selected_setting_survives_full_refit_config():
    supported={f.name for f in fields(TrainConfig)}
    for changes in GRID.values():
        assert set(BASE)|set(changes) <= supported
