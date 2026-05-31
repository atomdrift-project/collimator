"""Tests for fast experiment sampling."""

from __future__ import annotations

import numpy as np

from collimator.demo import create_demo_db
from collimator.experiment import (
    RECALL_AT_PER_100M_KS,
    _recall_at_per_100M,
    sample_partitioned_reports,
)


def test_recall_at_per_100M_perfect_separation() -> None:
    # 4 benigns scored low, 4 malware scored high — perfectly separable.
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    p = np.array([0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9])
    out = _recall_at_per_100M(y, p)
    for k in RECALL_AT_PER_100M_KS:
        assert out[f"recall_at_{int(k)}_per_100M"] == 1.0
    assert out["n_benign_holdout"] == 4
    assert out["n_malware_holdout"] == 4
    # 1e8 / 4 benigns = 25_000_000 FP/100M minimum resolvable rate.
    assert out["min_observable_per_100M"] == 25_000_000.0


def test_recall_at_per_100M_min_observable_none_when_no_benigns() -> None:
    y = np.array([1, 1, 1])
    p = np.array([0.7, 0.8, 0.9])
    out = _recall_at_per_100M(y, p)
    assert out["n_benign_holdout"] == 0
    # Emit None (=> JSON null) rather than +inf; the literal Infinity token
    # crashes strict downstream parsers. See _recall_at_per_100M for context.
    assert out["min_observable_per_100M"] is None


def test_recall_at_per_100M_degenerate_inputs() -> None:
    # No malware: all metrics report 0 cleanly without divide-by-zero.
    y_benign_only = np.array([0, 0, 0, 0])
    p_benign_only = np.array([0.1, 0.2, 0.3, 0.4])
    out = _recall_at_per_100M(y_benign_only, p_benign_only)
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
    out = _recall_at_per_100M(y, p)
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
