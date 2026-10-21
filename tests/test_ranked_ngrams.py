"""The v20 token budget retains evidence and matches vocabulary discovery."""

import numpy as np
import pytest

from collimator import features as f


@pytest.fixture(autouse=True)
def config_cache():
    f.feature_config_from_env.cache_clear()
    yield
    f.feature_config_from_env.cache_clear()


@pytest.mark.parametrize("order,limit", [(2, 512), (3, 128), (4, 64)])
def test_ranked_tiered_tokens_keep_strongest_and_break_ties(order, limit):
    paths = {f"path{i:04}": 3 for i in range(600)}
    paths["strong"] = 5
    scores = dict.fromkeys(paths, 3.0)
    scores["strong"] = 4.5
    expected = sorted(["h:strong"] + [f"n:path{i:04}" for i in range(limit - 1)])
    for ordered in (paths, dict(reversed(list(paths.items())))):
        assert f._ranked_tiered_tokens(ordered, scores, order=order, min_crit=3) == expected


@pytest.mark.parametrize("soft_presence", ["0", "1"])
def test_scores_use_same_finding_not_independent_maxima(monkeypatch, soft_presence):
    monkeypatch.setenv("COLLIMATOR_SOFT_PRESENCE", soft_presence)
    summary = f._summarize_findings([
        {"i": "a/b::high-severity", "l": 5, "c": 0.7},
        {"i": "a/b::high-confidence", "l": 3, "c": 1.0},
        {"i": "a/b::low-confidence", "l": 5, "c": 0.1},
    ])
    assert summary.path_scores == {"a": f._finding_score(5, 0.7), "a/b": f._finding_score(5, 0.7)}
    assert summary.sample_paths == {"a": 5, "a/b": 5}


@pytest.mark.parametrize("order,prefix", [(2, "tierbi"), (3, "tiertri"), (4, "tierquad")])
def test_overflow_keeps_learned_features_and_preserves_legacy(order, prefix):
    paths = {f"path{i:04}": 3 for i in range(600)}
    summary = f._summarize_findings([
        {"i": path, "l": crit, "c": 1.0} for path, crit in paths.items()
    ])
    name = prefix + ":" + " + ".join(f"n:path{i:04}" for i in range(order))
    for abi, expected in [(19, 0.0), (20, 1.0)]:
        spec = f.FeatureSpec(abi_version=abi, feature_names=[name], total_features=1)
        vec = np.zeros(1)
        f._apply_tiered_features(summary, f._ExtractContext(spec), vec, order)
        assert vec.tolist() == [expected]


def test_selection_precedes_vocabulary_filtering():
    report = {"v": "4", "fs": [{"type": "vsix", "ts": [
        *[{"i": f"strong{i:04}", "l": 5, "c": 1.0} for i in range(513)],
        {"i": "weak-a", "l": 3, "c": 1.0},
        {"i": "weak-b", "l": 3, "c": 1.0},
    ]}]}
    names = ["bigrams:strong0000 + strong0001", "bigrams:weak-a + weak-b"]
    spec = f.FeatureSpec(bigram_vocab=[n.split(":", 1)[1] for n in names],
                         feature_names=names, total_features=2)
    assert f.extract(report, spec).tolist() == [1.0, 0.0]


def test_branch_floor_applied_before_budget():
    paths = {"metadata/a": 3, "objectives/b": 2, "other/c": 3}
    assert f._ranked_tiered_tokens(
        paths, dict.fromkeys(paths, 3.0), order=2, min_crit=3,
        branch_min_crit={"metadata": 4, "objectives": 2},
    ) == ["n:objectives/b", "n:other/c"]
