"""Regression coverage for bounded vocabulary work and feature worker threads."""

from __future__ import annotations

import os
from itertools import combinations
from math import comb

import numpy as np
import pytest
from threadpoolctl import threadpool_info

from collimator import data, features


@pytest.fixture(autouse=True)
def clear_feature_config_cache():
    features.feature_config_from_env.cache_clear()
    yield
    features.feature_config_from_env.cache_clear()


@pytest.mark.parametrize("order", [2, 3])
@pytest.mark.parametrize("cap", [0, 2, 5, 100])
def test_capped_ngrams_preserve_counts_and_benign_tallies(order, cap):
    counts, expected = {}, {}
    benign_counts, expected_benign = {}, {}
    for paths, benign in [
        (["a", "b", "c", "d"], True),
        (["a", "b", "c"], False),
        (["b", "c", "d", "e"], True),
    ]:
        # The old implementation continues iterating after its cap, but stops
        # updating both new and existing keys. Preserve that behavior exactly.
        for tokens in combinations(paths, order):
            if len(expected) < cap:
                key = " + ".join(tokens)
                expected[key] = expected.get(key, 0) + 1
                if benign:
                    expected_benign[key] = expected_benign.get(key, 0) + 1
        features._count_capped_ngrams(
            paths, order, counts, cap, benign_counts if benign else None,
        )
        assert counts == expected
        assert benign_counts == expected_benign


def test_capped_ngrams_stop_consuming_combinations(monkeypatch):
    consumed = 0

    def guarded_combinations(paths, order):
        nonlocal consumed
        for tokens in combinations(paths, order):
            consumed += 1
            assert consumed <= 3, "traversal continued after vocabulary saturation"
            yield tokens

    monkeypatch.setattr(features, "combinations", guarded_combinations)
    paths = [f"trait/{i}" for i in range(10000)]
    counts = {}
    features._count_capped_ngrams(paths, 3, counts, 3)
    features._count_capped_ngrams(paths, 3, counts, 3)
    assert consumed == 3
    assert len(counts) == 3


def test_labeled_vocab_preserves_base_paths_and_benign_counts(monkeypatch):
    paths = ["a/b/c/d", "a/b/c/e", "b/c/d/e", "c/d/e/f"]
    report = {"v": "4", "fs": [{
        "type": "elf", "ts": [
            *[{"i": f"{path}::trait", "c": 1, "l": 4} for path in paths],
            {"i": "ignored/baseline", "c": 1, "l": 2},
        ],
    }]}
    monkeypatch.setattr(data, "fetch_cleave_results", lambda _dsn, _ids: {
        rid: {"cleave_result": report} for rid in (1, 2, 3)
    })
    result = features._vocab_labeled_db_batch_worker(("unused", [(1, 0), (2, 1), (3, 1)]))
    tokens = sorted(paths)
    assert result[3] == {" + ".join(pair): 3 for pair in combinations(tokens, 2)}
    assert result[9] == {" + ".join(triple): 3 for triple in combinations(tokens, 3)}
    assert result[10] == {" + ".join(triple): 1 for triple in combinations(tokens, 3)}


@pytest.mark.parametrize("n_paths", [256, 257, 512, 513])
def test_vocab_workers_preserve_per_file_caps(monkeypatch, n_paths):
    report = {"v": "4", "fs": [{
        "type": "elf", "ts": [
            {"i": f"trait/{i:04d}", "c": 1, "l": 4} for i in range(n_paths)
        ],
    }]}
    monkeypatch.setattr(data, "fetch_cleave_results", lambda _dsn, _ids: {
        1: {"cleave_result": report},
    })
    plain = features._vocab_batch_worker([report])
    labeled = features._vocab_labeled_db_batch_worker(("unused", [(1, 0)]))
    pairs = comb(n_paths, 2) if n_paths <= features.BIGRAM_MAX_PATHS else 0
    triples = comb(n_paths, 3) if n_paths <= features.TRIGRAM_MAX_PATHS else 0
    assert len(plain[3]) == min(pairs, 50000)
    assert len(labeled[3]) == min(pairs, 100000)
    assert len(labeled[9]) == min(triples, 50000)
    assert labeled[10] == labeled[9]


def _worker_context_id(spec):
    ctx = features._context(spec)
    assert ctx is features._worker_ctx
    return id(ctx)


@pytest.mark.parametrize("extraction", [False, True])
def test_feature_pool_limits_blas_and_restores_parent_env(monkeypatch, extraction):
    monkeypatch.setenv("OPENBLAS_NUM_THREADS", "8")
    monkeypatch.delenv("OMP_NUM_THREADS", raising=False)
    spec = features.FeatureSpec(feature_names=["present:a"], total_features=1)
    worker_pool = (
        features._extract_pool(1, spec) if extraction else features._feature_worker_pool(1)
    )
    with worker_pool as pool:
        # Force NumPy to load in the spawned worker, then inspect its runtime
        # library settings rather than just checking inherited env strings.
        assert pool.submit(np.dot, [1, 2], [3, 4]).result(timeout=30) == 11
        info = pool.submit(threadpool_info).result(timeout=30)
        blas = [entry for entry in info if entry["user_api"] == "blas"]
        assert blas
        assert all(entry["num_threads"] == 1 for entry in blas)
        assert pool.submit(os.getenv, "OMP_NUM_THREADS").result(timeout=30) == "1"
        if extraction:
            first = pool.submit(_worker_context_id, spec).result(timeout=30)
            assert pool.submit(_worker_context_id, spec).result(timeout=30) == first
    assert os.environ["OPENBLAS_NUM_THREADS"] == "8"
    assert "OMP_NUM_THREADS" not in os.environ
