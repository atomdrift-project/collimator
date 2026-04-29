"""Tests for threshold table semantics."""

from __future__ import annotations

import io
import re
from contextlib import redirect_stdout

import numpy as np

from collimator.data import Sample
from collimator.thresholds import (
    compute_default_recommendations,
    compute_severity_levels,
    evaluate_policies,
    fp_budget_tables,
    print_threshold_table,
    _error_rows_for_threshold,
)


def test_print_threshold_table_uses_called_subset_accuracy() -> None:
    probs = np.array([0.95, 0.90, 0.80, 0.30, 0.20, 0.10], dtype=np.float32)
    y = np.array([1, 1, 0, 0, 1, 0], dtype=np.float32)

    buf = io.StringIO()
    with redirect_stdout(buf):
        print_threshold_table(probs, y)
    out = buf.getvalue()

    hostile_line = re.search(r"80\.000%\s+0\.900000\s+5\s+1\s+6", out)
    benign_line = re.search(r"80\.000%\s+0\.900000\s+5\s+1\s+6", out)

    assert hostile_line is not None
    assert benign_line is not None


def test_evaluate_policies_returns_named_candidates() -> None:
    probs = np.array([0.9999, 0.98, 0.75, 0.40, 0.05, 0.01], dtype=np.float32)
    y = np.array([1, 1, 1, 0, 0, 0], dtype=np.float32)

    policies = evaluate_policies(probs, y)

    names = [policy["name"] for policy in policies]
    assert "default_fp_rate" in names
    assert "ultra_low_fpr" in names
    assert "recall_plus_fpr" in names
    assert "precision_floor" in names
    assert all("suspicious" in policy and "hostile" in policy for policy in policies)


def test_default_recommendations_derive_budgets_from_good_count() -> None:
    y = np.array([1] * 20 + [0] * 1_000_001, dtype=np.float32)
    probs = np.concatenate([
        np.linspace(0.99, 0.80, 20, dtype=np.float32),
        np.linspace(0.70, 0.01, 1_000_001, dtype=np.float32),
    ])

    recs = compute_default_recommendations(probs, y)
    budgets = fp_budget_tables(probs, y)
    hostile_row = next(row for row in budgets["hostile"] if row["max_fp_budget"] == 1)
    suspicious_row = next(row for row in budgets["suspicious"] if row["max_fp_budget"] == 10)

    assert recs["hostile"] == hostile_row["threshold"]
    assert recs["suspicious"] == suspicious_row["threshold"]


def test_severity_levels_derive_budgets_from_good_count() -> None:
    y = np.array([1] * 20 + [0] * 1_000_001, dtype=np.float32)
    probs = np.concatenate([
        np.linspace(0.99, 0.80, 20, dtype=np.float32),
        np.linspace(0.70, 0.01, 1_000_001, dtype=np.float32),
    ])

    levels = compute_severity_levels(probs, y)
    by_level = {row["level"]: row for row in levels}

    assert by_level[1]["budgets"]["hostile_fp"] == 0
    assert by_level[1]["budgets"]["suspicious_fp"] == 0
    assert by_level[5]["budgets"]["hostile_fp"] == 1
    assert by_level[5]["budgets"]["suspicious_fp"] == 10
    assert by_level[9]["budgets"]["hostile_fp"] == 5
    assert by_level[9]["budgets"]["suspicious_fp"] == 50
    assert by_level[5]["hostile"]["fp"] <= 1
    assert by_level[5]["suspicious"]["fp"] <= 10
    assert "true_negative_rate" in by_level[5]["hostile"]


def test_error_rows_for_threshold_returns_full_paths_and_confidence() -> None:
    samples = [
        Sample(1, "a" * 64, "/repo/harvest/fp.py", 0, {}, score=1),
        Sample(2, "b" * 64, "/repo/harvest/fn.py", 1, {}, score=9),
        Sample(3, "c" * 64, "/repo/harvest/tp.py", 1, {}, score=50),
    ]
    probs = np.array([0.95, 0.10, 0.99], dtype=np.float32)
    y = np.array([0, 1, 1], dtype=np.float32)

    fp_rows, fn_rows = _error_rows_for_threshold(samples, probs, y, 0.90, top_n=10)

    assert fp_rows[0]["path"] == "/repo/harvest/fp.py"
    assert np.isclose(fp_rows[0]["probability"], 0.95)
    assert fn_rows[0]["path"] == "/repo/harvest/fn.py"
    assert np.isclose(fn_rows[0]["probability"], 0.10)


def test_error_rows_for_threshold_sorts_both_error_types_by_descending_confidence() -> None:
    samples = [
        Sample(1, "a" * 64, "/repo/harvest/fp-low.py", 0, {}, score=1),
        Sample(2, "b" * 64, "/repo/harvest/fp-high.py", 0, {}, score=1),
        Sample(3, "c" * 64, "/repo/harvest/fn-low.py", 1, {}, score=9),
        Sample(4, "d" * 64, "/repo/harvest/fn-high.py", 1, {}, score=9),
    ]
    probs = np.array([0.91, 0.99, 0.10, 0.80], dtype=np.float32)
    y = np.array([0, 0, 1, 1], dtype=np.float32)

    fp_rows, fn_rows = _error_rows_for_threshold(samples, probs, y, 0.90, top_n=10)

    assert [row["path"] for row in fp_rows] == [
        "/repo/harvest/fp-high.py",
        "/repo/harvest/fp-low.py",
    ]
    assert [row["path"] for row in fn_rows] == [
        "/repo/harvest/fn-high.py",
        "/repo/harvest/fn-low.py",
    ]


def test_error_rows_for_threshold_collapses_archive_members_to_outer_paths() -> None:
    samples = [
        Sample(1, "a" * 64, "/repo/pkg.zip!!inner/fp-high.py", 0, {}, score=1),
        Sample(2, "b" * 64, "/repo/pkg.zip!!inner/fp-low.py", 0, {}, score=1),
        Sample(3, "c" * 64, "/repo/other.zip!!inner/fp.py", 0, {}, score=1),
        Sample(4, "d" * 64, "/repo/bad.zip!!inner/fn-high.py", 1, {}, score=9),
        Sample(5, "e" * 64, "/repo/bad.zip!!inner/fn-low.py", 1, {}, score=9),
        Sample(6, "f" * 64, "/repo/missed.zip!!inner/fn.py", 1, {}, score=9),
    ]
    probs = np.array([0.99, 0.98, 0.97, 0.80, 0.10, 0.70], dtype=np.float32)
    y = np.array([0, 0, 0, 1, 1, 1], dtype=np.float32)

    fp_rows, fn_rows = _error_rows_for_threshold(samples, probs, y, 0.90, top_n=2)

    assert [row["path"] for row in fp_rows] == [
        "/repo/pkg.zip",
        "/repo/other.zip",
    ]
    assert np.isclose(fp_rows[0]["probability"], 0.99)
    assert np.isclose(fp_rows[1]["probability"], 0.97)
    assert [row["path"] for row in fn_rows] == [
        "/repo/bad.zip",
        "/repo/missed.zip",
    ]
    assert np.isclose(fn_rows[0]["probability"], 0.80)
    assert np.isclose(fn_rows[1]["probability"], 0.70)
