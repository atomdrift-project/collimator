"""Tests for feature-group ablation helpers."""

from __future__ import annotations

import scipy.sparse as sp

from collimator.ablation import _drop_groups
from collimator.features import FeatureSpec


def test_drop_groups_removes_selected_feature_prefixes() -> None:
    spec = FeatureSpec(
        feature_names=[
            "present:a",
            "maxcrit:a",
            "agg:x",
            "metrics:y",
            "struct:z",
        ],
        total_features=5,
    )
    X = sp.csr_matrix([[1, 2, 3, 4, 5]], dtype=float)

    X_drop, names = _drop_groups(X, spec, ["agg", "struct"])

    assert X_drop.shape[1] == 3
    assert names == ["present:a", "maxcrit:a", "metrics:y"]
