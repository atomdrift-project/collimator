"""Tests for fast experiment sampling."""

from __future__ import annotations

from collimator.demo import create_demo_db
from collimator.experiment import sample_partitioned_reports


def test_sample_partitioned_reports_is_deterministic(tmp_path) -> None:
    db_path = tmp_path / "demo.db"
    create_demo_db(db_path, n_benign=32, n_malware=32, seed=7)

    a = sample_partitioned_reports(db_path, train_samples=20, seed=11)
    b = sample_partitioned_reports(db_path, train_samples=20, seed=11)

    assert [(s.raw_report, s.label, s.is_test) for s in a.train_samples] == [
        (s.raw_report, s.label, s.is_test) for s in b.train_samples
    ]
    assert [(s.raw_report, s.label, s.is_test) for s in a.test_samples] == [
        (s.raw_report, s.label, s.is_test) for s in b.test_samples
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
