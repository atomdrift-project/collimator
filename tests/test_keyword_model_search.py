"""Research cohorts keep canonical groups and confirmation labels isolated."""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


@pytest.fixture
def module(monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location("keyword_model_search", scripts / "keyword_model_search.py")
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def test_training_cap_preserves_groups_and_ignores_their_labels(module):
    rows = [(i, i % 2, "train", f"{i // 2:064x}", 9) for i in range(40)]
    # Two same-label members in every group.
    rows = [(i, (i // 2) % 2, p, g, s) for i, _, p, g, s in rows]
    accepted = {"min_malware_training_score": 0, "training_score_filter": {"min_score": None}}
    training, dev, excluded = module.select_cohort(rows, accepted, 5)
    flipped = [(i, 1-y, p, g, s) for i, y, p, g, s in rows]
    other, _, _ = module.select_cohort(flipped, accepted, 5)
    assert len(training) == 10
    assert len({r["group_id"] for r in training}) == 5
    assert [r["row_id"] for r in training] == [r["row_id"] for r in other]
    assert not dev and not excluded


def test_selection_excludes_test_and_conflicts_without_filtering_dev(module):
    rows = [(1, 0, "train", "aa", 0), (2, 1, "train", "bb", 1),
            (3, 1, "train", "cc", 4), (4, 0, "dev", "dd", 0),
            (5, 1, "test", "ee", 9), (6, 1, "train", "ff", 9),
            (7, 0, "train", "FF", 9)]
    accepted = {"min_malware_training_score": 4, "feature_env": {"COLLIMATOR_MIN_SAMPLE_SCORE": "3"},
                "training_score_filter": {"min_score": None}}
    train, dev, excluded = module.select_cohort(rows, accepted, 0)
    assert [r["row_id"] for r in train] == [1, 3]
    assert [r["row_id"] for r in dev] == [4]
    assert [r["row_id"] for r in excluded] == [6, 7]
    assert module.is_search("ab") == module.is_search("AB")


def test_frozen_baseline_keeps_already_deployed_keyword_sources(module, tmp_path):
    directory = tmp_path / "filetypes" / "gif"
    directory.mkdir(parents=True)
    (directory / "training_config.json").write_text(json.dumps({"feature_env": {
        "COLLIMATOR_KEYWORD_VOCAB_MAX": "5000", "COLLIMATOR_KEYWORD_MIN_FREQ": "1"}}))
    (directory / "feature_spec.json").write_text(json.dumps({"keyword_vocabs": {"ruleword": ["image"], "descword": []}}))
    _, baseline = module.capture_config(tmp_path, "gif")
    assert baseline == {"ruleword": {"method": "frequency", "cap": 5000, "floor": 1}}


def test_context_subgroups_without_two_classes_are_explicit(module):
    result = module.research.metrics(np.array([], dtype=np.int8), np.array([]))
    assert result["malware"] == result["goodware"] == 0
    assert result["auc"] is None and result["recall_0fp"] is None
    result = module.research.metrics(np.array([1, 1]), np.array([.2, .8]))
    assert result["auc"] is None
    assert result["recall_0fp"] == 1.0


def test_confirmation_requires_gains_in_both_seed_pairs(module):
    from summarize_keyword_model_search import confirmed_candidates

    def result(name, zero, one, pair_zero=None):
        metrics = dict(recall_0fp=zero, recall_1fp=one, ap=.95)
        return dict(name=name, confirmation=metrics,
                    confirmation_seeds_43_44=metrics,
                    confirmation_seeds_45_46=dict(metrics, recall_0fp=zero if pair_zero is None else pair_zero))

    baseline = result("baseline", .5, .6)
    stable = result("stable", .6, .7)
    unstable = result("unstable", .7, .8, pair_zero=.4)
    tradeoff = result("tradeoff", .4, .8)
    report = {"variants": {r["name"]: r for r in (baseline, stable, unstable, tradeoff)}}
    assert [r["name"] for r in confirmed_candidates(report)] == ["stable"]


def test_finalist_freezes_before_test_and_rejects_unstable_one_fp_gain(module, tmp_path):
    from confirm_keyword_model_search import choose
    directory = tmp_path / "main" / "gif"
    (directory / "inputs").mkdir(parents=True)
    (directory / "verified_summary.json").write_text("{}")
    np.savez(directory / "inputs/rows.npz", y_train=[0, 1], y_dev=[0, 1],
             row_ids=[1, 2, 3, 4], search=[True, False])
    def result(name, recall, pair_recall=None):
        m = dict(recall_0fp=.5, recall_1fp=recall, ap=.95)
        return dict(name=name, confirmation=m,
                    confirmation_seeds_43_44=m,
                    confirmation_seeds_45_46=dict(m, recall_1fp=recall if pair_recall is None else pair_recall))
    values = [result("baseline", .5), result("stable", .7), result("unstable", .8, pair_recall=.4)]
    (directory / "confirmation.json").write_text(json.dumps({"variants": {r["name"]: r for r in values}}))
    selected, winner, baseline = choose(tmp_path / "main", tmp_path / "absent-images", "gif")
    assert selected == directory
    assert winner["name"] == "stable"
    assert baseline["name"] == "baseline"
