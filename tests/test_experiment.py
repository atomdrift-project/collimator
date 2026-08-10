"""Tests for fast experiment sampling."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from collimator.demo import create_demo_db
from collimator import features, thresholds as _severity
from collimator.experiment import (
    RECALL_AT_PER_100M_KS,
    _allowlist_content_hash,
    _matrix_cache_key,
    recall_at_per_100M,
    sample_partitioned_reports,
)


def test_allowlist_content_hash_tracks_content(tmp_path) -> None:
    f = tmp_path / "allow.json"
    f.write_text('["a", "b"]')
    env = {"COLLIMATOR_ALLOWED_FEATURES_FILE": str(f)}
    h1 = _allowlist_content_hash(env)
    assert h1  # non-empty
    f.write_text('["a", "b", "c"]')  # same path, new content
    assert _allowlist_content_hash(env) != h1
    assert _allowlist_content_hash({}) == ""  # unset
    assert _allowlist_content_hash({"COLLIMATOR_ALLOWED_FEATURES_FILE": str(tmp_path / "missing.json")}) == ""


def test_matrix_cache_key_invalidates_on_allowlist_content(tmp_path) -> None:
    cfg = features.feature_config_from_env()
    f = tmp_path / "allow.json"
    f.write_text('["a", "b"]')
    env = {"COLLIMATOR_ALLOWED_FEATURES_FILE": str(f)}
    k1 = _matrix_cache_key("corpusABC", cfg, env)
    assert k1 == _matrix_cache_key("corpusABC", cfg, env)  # stable
    f.write_text('["a", "b", "c", "d"]')  # same path, different content
    assert _matrix_cache_key("corpusABC", cfg, env) != k1  # cache busts

    # No allowlist: key must NOT depend on the content-hash path (keeps legacy
    # cache valid) — i.e. stable and unaffected by the new logic.
    empty_env: dict[str, str] = {}
    assert _matrix_cache_key("corpusABC", cfg, empty_env) == _matrix_cache_key("corpusABC", cfg, empty_env)


def test_recall_at_per_100M_perfect_separation() -> None:
    # 4 benigns scored low, 4 malware scored high — perfectly separable.
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    p = np.array([0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9])
    out = recall_at_per_100M(y, p)
    for k in RECALL_AT_PER_100M_KS:
        assert out[f"recall_at_{int(k)}_per_100M"] == 1.0
    assert out["n_benign_holdout"] == 4
    assert out["n_malware_holdout"] == 4
    # 1e8 / 4 benigns = 25_000_000 FP/100M minimum resolvable rate.
    assert out["min_observable_per_100M"] == 25_000_000.0


def test_recall_at_per_100M_min_observable_none_when_no_benigns() -> None:
    y = np.array([1, 1, 1])
    p = np.array([0.7, 0.8, 0.9])
    out = recall_at_per_100M(y, p)
    assert out["n_benign_holdout"] == 0
    # Emit None (=> JSON null) rather than +inf; the literal Infinity token
    # crashes strict downstream parsers. See recall_at_per_100M for context.
    assert out["min_observable_per_100M"] is None


def test_recall_at_per_100M_degenerate_inputs() -> None:
    # No malware: all metrics report 0 cleanly without divide-by-zero.
    y_benign_only = np.array([0, 0, 0, 0])
    p_benign_only = np.array([0.1, 0.2, 0.3, 0.4])
    out = recall_at_per_100M(y_benign_only, p_benign_only)
    assert out["n_malware_holdout"] == 0
    for k in RECALL_AT_PER_100M_KS:
        assert out[f"recall_at_{int(k)}_per_100M"] == 0.0


def test_recall_at_per_100M_widening_budget_is_monotone() -> None:
    # 2M benigns, 100 malware: recall@k must be non-decreasing in k.
    rng = np.random.RandomState(0)
    n_benign = 2_000_000
    ben = rng.uniform(0.0, 0.5, n_benign)
    mal_clean = rng.uniform(0.6, 1.0, 70)
    mal_buried = rng.uniform(0.1, 0.45, 30)
    p = np.concatenate([ben, mal_clean, mal_buried])
    y = np.concatenate([np.zeros(n_benign), np.ones(100)]).astype(int)
    out = recall_at_per_100M(y, p)
    last = -1.0
    for k in RECALL_AT_PER_100M_KS:
        v = out[f"recall_at_{int(k)}_per_100M"]
        assert v >= last - 1e-12, f"recall@{k} regressed vs prior k: {v} < {last}"
        last = v


def test_sample_partitioned_reports_is_deterministic(tmp_path) -> None:
    db_path = tmp_path / "demo.db"
    create_demo_db(db_path, n_benign=32, n_malware=32, seed=7)

    a = sample_partitioned_reports(db_path, train_samples=20, seed=11)
    b = sample_partitioned_reports(db_path, train_samples=20, seed=11)

    assert [(s.row_id, s.label, s.is_test, s.group_id) for s in a.train_samples] == [
        (s.row_id, s.label, s.is_test, s.group_id) for s in b.train_samples
    ]
    assert [(s.row_id, s.label, s.is_test, s.group_id) for s in a.test_samples] == [
        (s.row_id, s.label, s.is_test, s.group_id) for s in b.test_samples
    ]
    assert all(not s.is_test for s in a.train_samples)
    assert all(s.is_test for s in a.test_samples)


def test_sample_partitioned_reports_full_test_keeps_all_test_rows(tmp_path) -> None:
    db_path = tmp_path / "demo.db"
    create_demo_db(db_path, n_benign=32, n_malware=32, seed=7)

    sampled = sample_partitioned_reports(db_path, train_samples=20, seed=11)

    assert all(not s.is_test for s in sampled.train_samples)
    assert all(s.is_test for s in sampled.test_samples)
    assert len(sampled.test_samples) > 1


def test_measured_fp_anchors_are_emitted_and_monotone() -> None:
    # The strict-end anchors a small screen holdout can actually observe.
    rng = np.random.RandomState(3)
    ben = rng.beta(2, 6, 5_000)
    mal = rng.beta(3, 3, 5_000)
    y = np.concatenate([np.zeros(ben.size), np.ones(mal.size)]).astype(int)
    out = recall_at_per_100M(y, np.concatenate([ben, mal]))
    for budget in (0, 1, 3):
        assert f"recall_at_{budget}fp" in out
        assert out[f"fp_at_{budget}fp"] <= budget
    assert out["recall_at_0fp"] <= out["recall_at_1fp"] <= out["recall_at_3fp"]


def test_measured_1fp_anchor_is_at_least_the_shipped_level_recall() -> None:
    # The two conventions are deliberately different and must not be conflated:
    # recall_at_1fp is the dominating point (loosest threshold still admitting
    # one benign), while recall_at_<level>_per_100M uses the conservative
    # ships-at threshold from quantile_severity_threshold. Below the holdout's
    # resolution both realize ~1 FP, and the anchor can only read >= the level.
    # Comparing one against the other across two models is what made a screen
    # baseline look 0.9pp better than like-for-like (2026-08-08).
    rng = np.random.RandomState(5)
    ben = rng.beta(2, 6, 10_000)
    mal = rng.beta(3, 3, 10_000)
    y = np.concatenate([np.zeros(ben.size), np.ones(mal.size)]).astype(int)
    out = recall_at_per_100M(y, np.concatenate([ben, mal]))
    assert out["min_observable_per_100M"] == 10_000.0
    level = _severity.DEFAULT_SEVERITY_LEVEL
    assert out["recall_at_1fp"] >= out[f"recall_at_{level}_per_100M"] - 1e-12


def test_route_policy_eval_shares_the_anchor_implementation() -> None:
    # scripts/azoth_route_policy_eval.py delegates to the same function, so a
    # screen anchor and a deploy-scale slice anchor cannot drift apart.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    import azoth_route_policy_eval as rpe

    rng = np.random.RandomState(11)
    p = np.concatenate([rng.beta(2, 6, 2_000), rng.beta(3, 3, 2_000)])
    y = np.concatenate([np.zeros(2_000), np.ones(2_000)]).astype(int)
    for budget in (0, 1, 3):
        assert rpe._recall_pr_at_fp(p, y, budget) == _severity.recall_at_fp_budget(
            y, p, budget,
        )
