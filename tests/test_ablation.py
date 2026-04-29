"""Tests for feature-group ablation helpers."""

from __future__ import annotations

import json

import scipy.sparse as sp

from collimator.ablation import _drop_groups, _load_ablation, save_ablation
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


def test_drop_groups_handles_current_dynamic_prefixes() -> None:
    spec = FeatureSpec(
        feature_names=[
            "present:a",
            "crit:h:objectives",
            "atkbi:T1059 + T1105",
            "unsigned_bigram:metadata/unsigned + objectives/evasion",
            "rare:KO",
        ],
        total_features=5,
    )
    X = sp.csr_matrix([[1, 2, 3, 4, 5]], dtype=float)

    X_drop, names = _drop_groups(X, spec, ["crit", "unsigned_bigram", "rare"])

    assert X_drop.shape[1] == 2
    assert names == ["present:a", "atkbi:T1059 + T1105"]


def test_save_and_load_ablation_rows_for_resume(tmp_path) -> None:
    output = tmp_path / "ablation.json"
    rows = [{"ablation": "baseline", "test_metrics": {"test_f1": 0.99}}]

    save_ablation(rows, output)

    assert _load_ablation(output) == rows
    assert json.loads(output.read_text()) == rows
