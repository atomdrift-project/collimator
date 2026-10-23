"""The v20 token budget retains evidence and matches vocabulary discovery."""

import numpy as np
import pytest

from collimator import features as f


@pytest.mark.parametrize("abi", [19, 20])
def test_indexed_trigrams_match_exhaustive_membership_across_archive_files(abi):
    rng = np.random.default_rng(42)
    tokens = [f"path{i:04}" for i in range(180)]
    triples = sorted({tuple(sorted(rng.choice(tokens, 3, replace=False))) for _ in range(500)})
    vocab = [" + ".join(parts) for parts in triples]
    spec = f.FeatureSpec(abi_version=abi, trigram_vocab=vocab,
                         feature_names=[f"trigram:{name}" for name in vocab], total_features=len(vocab))
    ctx = f._ExtractContext(spec)
    # Include empty, sparse, dense and overflowing archive members; matching
    # paths in different files must never combine into a trigram.
    report = {"v": "4", "fs": [{"type": "zip", "ts": [
        {"i": str(path), "l": 3, "c": 1.0}
        for path in rng.choice(tokens, count, replace=False)
    ]} for count in (0, 1, 2, 3, 8, 40, 130, 180)]}
    expected = np.zeros(len(vocab))
    for paths in f._ngram_files(report, ctx, f.TRIGRAM_MAX_PATHS, ctx.trigram_vocab_paths):
        present = set(paths)
        for parts, idx in ctx.trigram_lookup_triple.items():
            if all(path in present for path in parts):
                expected[idx] = 1.0
    actual = np.zeros(len(vocab))
    f._apply_trigram_features(report, ctx, actual)
    assert expected.any()
    np.testing.assert_array_equal(actual, expected)


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
