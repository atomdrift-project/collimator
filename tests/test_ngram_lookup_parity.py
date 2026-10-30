"""N-gram lookup retains file boundaries, confidence and legacy ABI behavior."""

import numpy as np
import pytest

from collimator import features as f


@pytest.mark.parametrize("abi", [19, 20])
@pytest.mark.parametrize("weighted", [False, True])
def test_bigram_lookup_preserves_orientation_and_file_boundaries(monkeypatch, abi, weighted):
    monkeypatch.setenv("COLLIMATOR_CONFIDENCE_WEIGHTED_NGRAMS", "1" if weighted else "0")
    f.feature_config_from_env.cache_clear()
    try:
        pairs = ["a + b", "b + a", "a + c", "x + y"]
        names = ["bigrams:" + p for p in pairs]
        spec = f.FeatureSpec(abi_version=abi, bigram_vocab=pairs, feature_names=names)
        ctx = f._ExtractContext(spec)
        report = {"fs": [
            {"ts": [{"i": "a", "l": 5, "c": .9}, {"i": "b", "l": 5, "c": .8}]},
            {"ts": [{"i": "c", "l": 5, "c": .95}]},
        ]}
        summary = f._summarize_report_files(report["fs"])
        vec = np.zeros(len(names), dtype=np.float32)
        f._apply_bigram_features(report, ctx, vec, summary)
        value = np.float32(.85 if weighted else 1.)
        assert np.array_equal(vec, np.asarray([value, value, 0, 0], dtype=np.float32))
    finally:
        f.feature_config_from_env.cache_clear()


@pytest.mark.parametrize("abi", [19, 20])
@pytest.mark.parametrize("order", [2, 3, 4])
def test_tiered_lookup_requires_every_token(abi, order):
    tokens = ["h:a", "h:b", "h:c", "h:d"]
    prefix = {2: "tierbi:", 3: "tiertri:", 4: "tierquad:"}[order]
    matches = " + ".join(tokens[:order])
    misses = " + ".join(tokens[:order - 1] + ["h:missing"])
    spec = f.FeatureSpec(abi_version=abi, feature_names=[prefix + matches, prefix + misses])
    ctx = f._ExtractContext(spec)
    summary = f._summarize_report_files([
        {"ts": [{"i": p, "l": 5, "c": 1.} for p in "abcd"]},
    ])
    vec = np.zeros(2, dtype=np.float32)
    f._apply_tiered_features(summary, ctx, vec, order)
    assert np.array_equal(vec, [1., 0.])
