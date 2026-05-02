"""Tests for threshold table semantics."""

from __future__ import annotations

import io
import re
from contextlib import redirect_stdout

import numpy as np

from collimator import thresholds
from collimator.data import Sample
from collimator.thresholds import (
    ScoredSample,
    _error_rows_for_threshold,
    _near_severity_level,
    compute_default_recommendations,
    compute_severity_levels,
    evaluate_policies,
    fp_budget_tables,
    print_threshold_table,
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


def test_print_recommendations_shows_scored_and_full_denominator_levels() -> None:
    probs = np.array([0.99, 0.95, 0.80, 0.70], dtype=np.float32)
    y = np.array([1, 1, 0, 0], dtype=np.float32)

    buf = io.StringIO()
    with redirect_stdout(buf):
        thresholds.print_recommendations(
            probs,
            y,
            n_benign_denominator=1_000_000,
        )
    out = buf.getvalue()

    assert "Measured on scored rows only" in out
    assert "Measured with full good-file denominator" in out
    assert "FP/1M denominator: 1000000 benign files" in out


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
    hostile_row = next(row for row in budgets["hostile"] if row["max_fp_budget"] == 5)
    suspicious_row = next(row for row in budgets["suspicious"] if row["max_fp_budget"] == 48)

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

    assert by_level[0]["budgets"]["hostile_fp"] == 0
    assert by_level[0]["budgets"]["suspicious_fp"] == 8
    assert by_level[1]["budgets"]["hostile_fp"] == 1
    assert by_level[1]["budgets"]["suspicious_fp"] == 16
    assert by_level[5]["budgets"]["hostile_fp"] == 5
    assert by_level[5]["budgets"]["suspicious_fp"] == 48
    assert by_level[9]["budgets"]["hostile_fp"] == 9
    assert by_level[9]["budgets"]["suspicious_fp"] == 80
    assert by_level[5]["hostile"]["fp"] <= 5
    assert by_level[5]["suspicious"]["fp"] <= 48
    assert "true_negative_rate" in by_level[5]["hostile"]


def test_severity_levels_can_use_full_good_file_denominator() -> None:
    y = np.array([1] * 5 + [0] * 10, dtype=np.float32)
    probs = np.concatenate([
        np.linspace(0.99, 0.90, 5, dtype=np.float32),
        np.linspace(0.80, 0.10, 10, dtype=np.float32),
    ])

    levels = compute_severity_levels(probs, y, n_benign_denominator=1_000_000)
    by_level = {row["level"]: row for row in levels}

    assert by_level[5]["budgets"]["hostile_fp"] == 5
    assert by_level[5]["budgets"]["suspicious_fp"] == 48
    assert by_level[5]["hostile"]["n_benign"] == 1_000_000
    assert by_level[5]["hostile"]["fp_per_million"] <= 5.0


def test_severity_levels_report_empty_threshold_when_budget_is_too_tight() -> None:
    y = np.array([0, 0, 1], dtype=np.float32)
    probs = np.array([0.99, 0.99, 0.98], dtype=np.float32)

    levels = compute_severity_levels(probs, y)
    level_zero = next(row for row in levels if row["level"] == 0)

    assert level_zero["hostile"]["fp"] == 0
    assert level_zero["hostile"]["tp"] == 0
    assert level_zero["hostile"]["threshold"] > 0.99


def test_near_severity_level_doubles_distance_from_full_confidence() -> None:
    near = _near_severity_level({
        "level": 9,
        "hostile": {"threshold": 0.95},
        "suspicious": {"threshold": 0.90},
    })

    assert np.isclose(near["hostile"]["threshold"], 0.90)
    assert np.isclose(near["suspicious"]["threshold"], 0.80)
    assert np.isclose(near["hostile"]["basis_threshold"], 0.95)
    assert np.isclose(near["suspicious"]["basis_threshold"], 0.90)


def test_near_false_reports_only_newly_crossing_rows(monkeypatch) -> None:
    samples = [
        ScoredSample(1, "a" * 64, "/repo/good-near.py", 0, 0),
        ScoredSample(2, "b" * 64, "/repo/good-false.py", 0, 0),
        ScoredSample(3, "c" * 64, "/repo/good-low.py", 0, 0),
        ScoredSample(4, "d" * 64, "/repo/bad-near.py", 9, 1),
        ScoredSample(5, "e" * 64, "/repo/bad-false.py", 9, 1),
        ScoredSample(6, "f" * 64, "/repo/bad-low.py", 9, 1),
    ]
    probs = np.array([0.85, 0.95, 0.75, 0.88, 0.95, 0.70], dtype=np.float32)
    y = np.array([0, 0, 0, 1, 1, 1], dtype=np.float32)
    severity_levels = [
        {
            "level": 9,
            "hostile": {"threshold": 0.90},
            "suspicious": {"threshold": 0.90},
        },
    ]

    def fake_score(*args, **kwargs):
        return samples, probs, y

    monkeypatch.setattr(thresholds, "_score_labeled_corpus", fake_score)
    monkeypatch.setattr(thresholds, "compute_severity_levels", lambda _probs, _y: severity_levels)

    fp_payload = thresholds.show_near_false_positives(
        "db",
        model_path="model",
        spec_path="spec",
        top_errors=10,
    )
    fn_payload = thresholds.show_near_false_negatives(
        "db",
        model_path="model",
        spec_path="spec",
        top_errors=10,
    )

    assert [row["path"] for row in fp_payload["near_false_positives"]] == ["/repo/good-near.py"]
    assert [row["path"] for row in fn_payload["near_false_negatives"]] == ["/repo/bad-near.py"]


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
