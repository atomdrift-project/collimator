"""Tests for synthetic demo database generation."""

from __future__ import annotations

from collimator.data import load_samples
from collimator.demo import create_demo_db


def test_create_demo_db_generates_labeled_samples(tmp_path) -> None:
    db_path = tmp_path / "demo.db"
    create_demo_db(db_path, n_benign=4, n_malware=6, seed=7)

    samples = load_samples(db_path)
    assert len(samples) == 10
    assert sum(sample.label == 0 for sample in samples) == 4
    assert sum(sample.label == 1 for sample in samples) == 6
