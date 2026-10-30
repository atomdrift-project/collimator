"""Diagnostic flags must distinguish instability from merely short models."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from azoth_stability_audit import flags_for, model_summary


def test_short_healthy_models_are_not_flagged():
    row = {"train_malware": 1000, "holdout_ap": [.99, .98, .99],
           "models": [{"trees": n, "min_leaf": -4, "max_leaf": .5} for n in (3, 5, 4)]}
    assert flags_for(row) == []


def test_model_audit_flags_collapse_and_insufficient_support(tmp_path):
    model = tmp_path / "seed_42.txt"
    model.write_text("Tree=0\nleaf_value=-8 98\nTree=1\nleaf_value=-120 4\n")
    summary = model_summary(model)
    assert summary["trees"] == 2
    assert summary["first_tree_max_leaf"] == 98
    flags = flags_for({"models": [summary], "holdout_ap": [.05], "train_malware": 36})
    assert set(flags) == {"extreme_leaf_outputs", "weak_holdout_ap", "limited_positive_support"}
