"""Regression coverage for bounded vocabulary work and feature worker threads."""

from __future__ import annotations

import json
import os
from itertools import combinations
from pathlib import Path
import random

import numpy as np
import pytest
from threadpoolctl import threadpool_info

from collimator import data, features
from collimator.vocabulary import VocabularyCounts


@pytest.fixture(autouse=True)
def clear_feature_config_cache():
    features.feature_config_from_env.cache_clear()
    yield
    features.feature_config_from_env.cache_clear()


@pytest.mark.parametrize("order", [2, 3])
@pytest.mark.parametrize("buffer_size", [1, 2, 100])
def test_ngram_counts_are_exact_across_flushes(order, buffer_size):
    expected, benign = {}, {}
    with VocabularyCounts(buffer_size=buffer_size) as counts:
        for document, (paths, is_benign) in enumerate([
            (["a", "b", "c", "d"], True),
            (["a", "b", "c"], False),
            (["b", "c", "d", "e"], True),
        ]):
            for parts in combinations(paths, order):
                token = " + ".join(parts)
                expected[token] = expected.get(token, 0) + 1
                if is_benign:
                    benign[token] = benign.get(token, 0) + 1
            # Repeated embedded files must not increase document frequency.
            for _ in range(3):
                features._count_ngrams(paths, order, counts, "ngram", document,
                                       "benign" if is_benign else "")
        assert counts.view("ngram") == expected
        assert counts.view("benign") == benign


def test_counts_merge_and_filter_before_ranking(tmp_path):
    paths = []
    for number in range(2):
        path = tmp_path / f"batch{number}.sqlite"
        with VocabularyCounts(str(path), buffer_size=1) as counts:
            counts.increment("bigram", "common", 100)
            counts.increment("benign", "common", 100)
            counts.increment("bigram", "z-late", 10)
            counts.increment("bigram", "a-late", 10)
            view = counts.view("bigram")
        paths.append(view)
    with VocabularyCounts() as merged:
        for view in reversed(paths):
            merged.merge(view)
            assert not Path(view.path).exists()
        assert merged.view("bigram")["common"] == 200
        assert merged.top("bigram", 1, 1) == ["common"]
        assert merged.top("bigram", 1, 1, benign_family="benign") == ["a-late"]


@pytest.mark.parametrize("buffer_size", [1, 2, 7, 1000])
def test_packed_counts_match_document_sets_under_eviction(buffer_size):
    rng = random.Random(43)
    expected = {}
    with VocabularyCounts(buffer_size=buffer_size) as counts:
        for document in range(20):
            seen = set()
            for _ in range(100):
                parts = tuple(sorted(rng.sample(["a", "b", "c", "d", "e", "f"], 3)))
                name = " + ".join(parts)
                counts.increment("trigram", parts, document=document)
                seen.add(name)
            for name in seen:
                expected[name] = expected.get(name, 0) + 1
        assert counts.view("trigram") == expected
        assert counts.top("trigram", 7, 1) == sorted(
            sorted(expected, key=lambda name: (-expected[name], name))[:7]
        )


def test_packed_merge_remaps_worker_token_ids(tmp_path):
    views = []
    for i, tokens in enumerate([["z", "a", "m"], ["m", "a", "z"]]):
        with VocabularyCounts(str(tmp_path / f"{i}.sqlite"), stable_token_ids=False) as counts:
            for token in tokens:
                counts.increment("tokens", token)
            counts.increment("bigram", ("a", "z"), document=i)
            views.append(counts.view("bigram"))
    with VocabularyCounts() as merged:
        for view in views:
            merged.merge(view)
        assert merged.view("bigram") == {"a + z": 2}
        assert merged.top("tokens", 1, 1) == ["a"]


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
    assert result[3] == {" + ".join(pair): 2 for pair in combinations(tokens, 2)}
    assert result[9] == {" + ".join(triple): 2 for triple in combinations(tokens, 3)}
    assert result[10] == {}  # Benign prevalence is measured after candidate selection.


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
    calls = []
    monkeypatch.setattr(features, "_count_ngrams", lambda paths, order, _counts, family, *rest, **_kw:
                        calls.append((family, order, len(paths))))
    monkeypatch.setattr(VocabularyCounts, "group_combinations",
                        lambda self, family, paths, order, **_kw:
                        calls.append((family, order, len(paths))))
    features._vocab_batch_worker([report])
    features._vocab_labeled_db_batch_worker(("unused", [(1, 1)]))
    pairs = min(n_paths, features.BIGRAM_MAX_PATHS)
    assert calls[:2] == [("bigram", 2, pairs)] * 2
    assert calls[2] == ("trigram", 3, min(n_paths, 128))


def test_archive_vocab_counts_documents_not_members(monkeypatch):
    file = {"type": "vsix", "ts": [
        {"i": f"trait/{i}", "c": 1, "l": 4} for i in range(4)
    ]}
    monkeypatch.setattr(data, "fetch_cleave_results", lambda *_: {
        1: {"cleave_result": {"v": "4", "fs": [file] * 10}},
    })
    result = features._vocab_labeled_db_batch_worker(("unused", [(1, 1)]))
    assert len(result[3]) == 6
    assert len(result[9]) == 4
    assert set(result[3].values()) == {1}
    assert set(result[9].values()) == {1}
    assert result[10] == {}


def _worker_context_id(spec):
    ctx = features._context(spec)
    assert ctx is features._worker_ctx
    return id(ctx)


# threadpoolctl only sees a BLAS it can limit (OpenBLAS, MKL, BLIS). NumPy on
# macOS links Apple Accelerate, which it cannot see, so there is nothing to check.
@pytest.mark.skipif(
    not any(entry["user_api"] == "blas" for entry in threadpool_info()),
    reason="needs a BLAS threadpoolctl can limit (OpenBLAS, MKL or BLIS)",
)
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


def test_extended_metric_frequency_counts_reports(monkeypatch):
    monkeypatch.setenv("COLLIMATOR_EXTENDED_METRICS", "1")
    common = {"type": "vsix", "ms": {"custom": {"common_count": 1}}}
    repeated = {"type": "javascript", "ms": {"custom": {"rare_count": 1}}}
    reports = {
        rid: {"cleave_result": {"v": "4", "fs": [common] + ([repeated] * 100 if rid == 1 else [])}}
        for rid in range(1, 21)
    }
    monkeypatch.setattr(data, "fetch_cleave_results", lambda _db, ids: {rid: reports[rid] for rid in ids})
    spec = features.build_vocab_from_db("unused", [(rid, rid % 2) for rid in reports], n_workers=1)
    assert "custom_common_count" in spec.metric_vocab
    assert "custom_rare_count" not in spec.metric_vocab


def test_extended_metrics_on_reduced_reports_stay_within_the_fact_profile(monkeypatch):
    monkeypatch.setenv("COLLIMATOR_EXTENDED_METRICS", "1")
    profile = json.loads(features.FACT_PROFILE_MANIFEST.read_text())["id"]
    retained, dropped = "pe_image_size", "custom_common_count"
    entry = {"type": "pe", "ms": {"pe": {"image_size": 4096}, "custom": {"common_count": 1}}}
    report = {"v": "9", "fp": profile, "fs": [entry]}
    reports = {rid: {"cleave_result": report} for rid in range(1, 21)}
    monkeypatch.setattr(
        data, "fetch_cleave_results", lambda _db, ids: {rid: reports[rid] for rid in ids}
    )
    spec = features.build_vocab_from_db("unused", [(rid, rid % 2) for rid in reports], n_workers=1)
    assert retained in spec.metric_vocab
    assert dropped not in spec.metric_vocab


def test_benign_trigram_scan_matches_candidates_without_cross_file_mixing(monkeypatch):
    def file(paths):
        return {"type": "javascript", "ts": [{"i": p, "l": 4, "c": 1.0} for p in paths]}
    report = {"v": "4", "fs": [file(["a", "b", "c"])] * 20 + [file(["d", "e"]), file(["f"])]}
    monkeypatch.setattr(data, "fetch_cleave_results", lambda *_: {1: {"cleave_result": report}})
    result = features._vocab_benign_trigram_worker(("unused", [1], ["a + b + c", "d + e + f"], None))
    assert result == {"a + b + c": 1}


def test_trigram_vocab_requires_malware_support_and_checks_benign_fraction(monkeypatch):
    monkeypatch.setenv("COLLIMATOR_TRIGRAM_MIN_FREQ", "2")
    monkeypatch.setenv("COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC", "0")
    def report(groups):
        return {"cleave_result": {"v": "4", "fs": [{"type": "vsix", "ts": [
            {"i": p, "l": 4, "c": 1.0} for p in paths
        ]} for paths in groups]}}
    reports = {
        1: report([["a", "b", "c"], ["d", "e", "f"]]),
        2: report([["a", "b", "c"], ["d", "e", "f"]]),
        3: report([["g", "h", "i"], ["d", "e", "f"]]),
        4: report([["g", "h", "i"]]),
    }
    monkeypatch.setattr(data, "fetch_cleave_results", lambda _db, ids: {rid: reports[rid] for rid in ids})
    spec = features.build_vocab_from_db("unused", [(1, 1), (2, 1), (3, 0), (4, 0)], n_workers=1)
    assert spec.trigram_vocab == ["a + b + c"]


def test_singletons_use_both_classes_and_combinations_use_malware(monkeypatch):
    for name in ("BIGRAM_MIN_FREQ", "TRIGRAM_MIN_FREQ",
                 "TIERED_BIGRAM_MIN_FREQ", "TIERED_TRIGRAM_MIN_FREQ",
                 "TIERED_QUADGRAM_MIN_FREQ"):
        monkeypatch.setenv(f"COLLIMATOR_{name}", "1")
    for name in ("TIERED_CRIT_BIGRAMS", "TIERED_CRIT_TRIGRAMS", "TIERED_CRIT_QUADGRAMS"):
        monkeypatch.setenv(f"COLLIMATOR_{name}", "1")

    def report(prefix):
        return {"cleave_result": {"v": "4", "fs": [{
            "type": "vsix",
            "ts": [{"i": f"{prefix}{i}", "l": 4, "c": 1.0} for i in range(4)],
        }]}}

    # Enough support for singleton admission, entirely disjoint class signals.
    reports = {rid: report("signed" if rid <= 30 else "unsigned") for rid in range(1, 61)}
    labels = [(rid, int(rid > 30)) for rid in reports]
    monkeypatch.setattr(data, "fetch_cleave_results",
                        lambda _db, ids: {rid: reports[rid] for rid in ids})
    spec = features.build_vocab_from_db("unused", labels, n_workers=1)
    assert {"signed0", "unsigned0"} <= set(spec.presence_vocab)
    for vocab in (spec.bigram_vocab, spec.trigram_vocab, spec.tiered_bigram_vocab,
                  spec.tiered_trigram_vocab, spec.tiered_quadgram_vocab):
        assert vocab
        assert all("unsigned" in token and "signed" not in token.replace("unsigned", "")
                   for token in vocab)


def test_auxiliary_singletons_and_combinations_follow_class_policy(monkeypatch):
    for name in ("CRIT_CATEGORY_NGRAMS", "ATTACK_CODE_NGRAMS", "MBC_ID_VOCAB",
                 "SYMBOL_VOCAB", "SYMBOL_BIGRAMS", "SYMBOL_TRIGRAMS"):
        monkeypatch.setenv(f"COLLIMATOR_{name}", "1")
    monkeypatch.setenv("COLLIMATOR_SYMBOL_MIN_FREQ", "1")

    def report(prefix):
        return {"cleave_result": {"v": "4", "fs": [{
            "type": "vsix", "ff": {"fn": [f"{prefix}{i}" for i in range(3)]},
            "ts": [{"i": f"objectives/{prefix}{i}", "l": 4, "c": 1.0,
                    "a": f"T{prefix}{i}", "m": f"B{prefix}{i}"} for i in range(3)],
        }]}}

    reports = {rid: report("clean" if rid <= 30 else "malware") for rid in range(1, 61)}
    labels = [(rid, int(rid > 30)) for rid in reports]
    monkeypatch.setattr(data, "fetch_cleave_results",
                        lambda _db, ids: {rid: reports[rid] for rid in ids})
    spec = features.build_vocab_from_db("unused", labels, n_workers=1)
    for vocab in (spec.crit_unigram_vocab, spec.mbc_id_vocab, spec.symbol_vocab):
        assert any("clean" in token for token in vocab)
        assert any("malware" in token for token in vocab)
    for vocab in (spec.crit_bigram_vocab, spec.crit_trigram_vocab,
                  spec.attack_bigram_vocab, spec.attack_trigram_vocab,
                  spec.mbc_bigram_vocab, spec.mbc_trigram_vocab,
                  spec.symbol_bigram_vocab, spec.symbol_trigram_vocab):
        assert vocab
        assert all("malware" in token and "clean" not in token for token in vocab)
