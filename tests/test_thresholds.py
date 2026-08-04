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
    quantile_severity_threshold,
)


def test_quantile_severity_threshold_curve_properties_on_small_sample() -> None:
    """The shared operating-point estimator must hold these on a TINY sample.

    Levels are resolution-adjusted (LEVELS.md): the requested level is shifted
    by the route's own 1-FP floor, so L1 IS the first false positive on every
    route regardless of corpus size. That makes the contract simple and the
    same everywhere:

      - L0 admits ZERO false positives and is the only extrapolated level;
      - every level >= L1 admits at least 1 FP, sits at or below the max
        observed benign, and is "measured" (interpolation between observed
        order statistics);
      - L0 is strictly stricter than L1, but one step along the same curve
        rather than a jump to "above everything";
      - the level -> threshold map is monotone non-increasing.
    """
    rng = np.random.default_rng(0)
    benign = np.concatenate([
        rng.uniform(0.0, 0.3, 110),
        np.sort(rng.uniform(0.4, 0.95, 10)),
    ]).astype(np.float64)
    mx = float(benign.max())
    # (label, per-100M level) -> target_per_million is level/100.
    levels = [0, 1, 5, 50, 100, 500, 1000, 10000]
    thr = {L: quantile_severity_threshold(benign, L / 100.0)[0] for L in levels}

    # L0: zero FP, the only extrapolated level, strictly stricter than L1.
    assert int(np.sum(benign >= thr[0])) == 0
    assert quantile_severity_threshold(benign, 0.0)[1] == "extrapolated"
    assert thr[0] > thr[1]

    # Every level from L1 up: at least 1 FP, never above the observed data.
    for L in levels[1:]:
        assert thr[L] <= mx
        assert int(np.sum(benign >= thr[L])) >= 1
        assert quantile_severity_threshold(benign, L / 100.0)[1] == "measured"

    # Distinct adjacent levels, even when subtle.
    assert thr[0] != thr[1]
    assert thr[5] != thr[50]
    assert thr[5] > thr[50]  # stricter level -> higher threshold

    # Monotone non-increasing across the whole grid.
    ordered = [thr[L] for L in levels]
    assert all(a >= b for a, b in zip(ordered, ordered[1:]))


def test_l0_admits_zero_fp_on_a_saturated_route() -> None:
    """L0 must admit zero FP even when the model scores benigns at p=1.0.

    Regression, 2026-08-03 -> 2026-08-04. Benign scores are clipped to 1-1e-7
    before the logit, so the L0 line came back at ~0.9999999 — below the p=1.0
    benigns it was supposed to exclude. L0 lost its zero-FP guarantee on every
    saturated route (2,016 benigns fired across nine of them, where the rule it
    replaced had exactly 0). The threshold is now floored at the first float32
    step past the largest observed benign, which on such a route is above 1.0.

    float32 is the operative width: thresholds ship through config.json into
    litmus/ONNX as f32, so a float64 value that merely rounds to the same f32
    as the max benign would stop excluding it once deployed.
    """
    rng = np.random.default_rng(11)
    benign = np.clip(rng.beta(2.0, 5.0, 20_000), 0.0, 1.0)
    benign[:600] = 1.0  # the rust / java_class / text / makefile shape

    thr0, method = quantile_severity_threshold(benign, 0.0)
    assert method == "extrapolated"
    assert thr0 > 1.0, "a saturated route needs an unreachable L0 threshold"
    assert int(np.sum(benign >= thr0)) == 0
    # Survives the width it actually ships at.
    assert int(np.sum(benign.astype(np.float32) >= np.float32(thr0))) == 0

    # L1 still admits the ceiling mass, and L0 is strictly stricter. On a
    # saturated route the 0 -> 600 jump is unavoidable: the route cannot
    # produce a small nonzero FP count, so "some fire" and "none fire" are the
    # only two thresholds it has.
    thr1, _ = quantile_severity_threshold(benign, 0.01)
    assert thr0 > thr1
    assert int(np.sum(benign >= thr1)) == 600


def test_quantile_severity_threshold_returns_none_below_floor() -> None:
    assert quantile_severity_threshold(np.linspace(0, 1, 49), 0.5) == (None, "none")
    # 50 benigns cannot resolve a raw 50/100M rate, but the resolution-adjusted
    # scale puts L50 just past this sample's own 1-FP floor, so it is measured
    # and admits at least one false positive.
    benign = np.linspace(0, 1, 50)
    thr, method = quantile_severity_threshold(benign, 0.5)
    assert method == "measured" and 0.0 <= thr <= 1.0
    assert int(np.sum(benign >= thr)) >= 1


def test_evaluate_policies_returns_named_candidates() -> None:
    probs = np.array([0.9999, 0.98, 0.75, 0.40, 0.05, 0.01], dtype=np.float32)
    y = np.array([1, 1, 1, 0, 0, 0], dtype=np.float32)

    policies = evaluate_policies(probs, y)

    names = [policy["name"] for policy in policies]
    assert "default_fp_rate" in names
    assert "ultra_low_fpr" in names
    assert "recall_plus_fpr" in names
    assert "precision_floor" in names
    # "Suspicious" is a consumer-side derivation now; collimator emits only
    # the single hostile policy level per spec.
    assert all("hostile" in policy and "suspicious" not in policy for policy in policies)


def test_default_recommendations_derive_budgets_from_good_count() -> None:
    y = np.array([1] * 20 + [0] * 1_000_001, dtype=np.float32)
    probs = np.concatenate([
        np.linspace(0.99, 0.80, 20, dtype=np.float32),
        np.linspace(0.70, 0.01, 1_000_001, dtype=np.float32),
    ])

    recs = compute_default_recommendations(probs, y)
    budgets = fp_budget_tables(probs, y)
    # Default severity level is DEFAULT_SEVERITY_LEVEL (per-100M scale). With
    # ~1M benigns the floor budget is clamped to 1 FP by _fp_budget_for_rate
    # regardless of the exact level (the level only affects the *rate*; any
    # rate below 1 FP/M rounds up to a 1-FP budget on this corpus size).
    # "Suspicious" is a consumer-side derivation; only hostile is emitted.
    hostile_row = next(row for row in budgets["hostile"] if row["max_fp_budget"] == 1)

    assert recs["hostile"] == hostile_row["threshold"]
    assert "suspicious" not in recs
    assert "suspicious" not in budgets


def test_severity_levels_derive_budgets_from_good_count() -> None:
    y = np.array([1] * 20 + [0] * 1_000_001, dtype=np.float32)
    probs = np.concatenate([
        np.linspace(0.99, 0.80, 20, dtype=np.float32),
        np.linspace(0.70, 0.01, 1_000_001, dtype=np.float32),
    ])

    levels = compute_severity_levels(probs, y)
    by_level = {row["level"]: row for row in levels}

    # Per-100M scale: level N → N FP per 100M benigns → N/100 FP/M. With ~1M
    # benigns: L100 = 1 FP. Lower levels round to 0 budget (then clamp to 1
    # via _fp_budget_for_rate). The grid caps at L100 to match litmus's CLI.
    assert by_level[0]["budgets"]["hostile_fp"] == 0
    assert by_level[100]["budgets"]["hostile_fp"] == 1
    assert by_level[100]["hostile"]["fp"] <= 1
    assert "true_negative_rate" in by_level[100]["hostile"]
    # "Suspicious" is a consumer-side derivation now; collimator only emits
    # the hostile policy level.
    assert "suspicious_fp" not in by_level[100]["budgets"]
    assert "suspicious" not in by_level[100]


def test_severity_levels_can_use_full_good_file_denominator() -> None:
    y = np.array([1] * 5 + [0] * 10, dtype=np.float32)
    probs = np.concatenate([
        np.linspace(0.99, 0.90, 5, dtype=np.float32),
        np.linspace(0.80, 0.10, 10, dtype=np.float32),
    ])

    levels = compute_severity_levels(probs, y, n_benign_denominator=1_000_000)
    by_level = {row["level"]: row for row in levels}

    # L100 = 1 FP per 100M = 1 FP per 1M benigns at this denominator.
    assert by_level[100]["budgets"]["hostile_fp"] == 1
    assert by_level[100]["hostile"]["n_benign"] == 1_000_000
    # fp_per_100M = (fp / n_benign) * 1e8; with budget 1 in 1M benigns the
    # observed rate is at most 1e-6, so ≤ 100 in per-100M units. Allow a
    # tiny epsilon for float arithmetic.
    assert by_level[100]["hostile"]["fp_per_100M"] <= 100.0 + 1e-6


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
    })

    assert np.isclose(near["hostile"]["threshold"], 0.90)
    assert np.isclose(near["hostile"]["basis_threshold"], 0.95)
    # Suspicious is a consumer derivation now; not present in collimator output.
    assert "suspicious" not in near


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
        },
    ]

    def fake_score(*args, **kwargs):
        return samples, probs, y

    # _score_labeled_corpus lives in the inspect submodule now; patch the
    # canonical location so the show_near_* call sites see the fake.
    from collimator.thresholds import _inspect as _inspect_mod
    monkeypatch.setattr(_inspect_mod, "_score_labeled_corpus", fake_score)
    monkeypatch.setattr(_inspect_mod, "compute_severity_levels", lambda _probs, _y: severity_levels)

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


def test_credible_bound_fp_rate_zero_fps_small_n() -> None:
    """0 FPs out of 100 benigns: empirical FPR is 0, but with so few samples
    we can't claim the true rate is below ~3% at 95% confidence."""
    from collimator.thresholds import credible_bound_fp_rate

    upper = credible_bound_fp_rate(0, 100, side="upper", confidence=0.95)
    assert 0.025 < upper < 0.035, f"unexpected upper bound: {upper}"


def test_credible_bound_fp_rate_zero_fps_large_n_meets_3fpm() -> None:
    """0 FPs out of 1M benigns: 95% upper bound is ~3 FP/M.  This is the N
    threshold beyond which the L3 (3 FP/M) target becomes deploy-confident."""
    from collimator.thresholds import credible_bound_fp_rate

    upper = credible_bound_fp_rate(0, 1_000_000, side="upper", confidence=0.95)
    assert 2.5e-6 < upper < 3.5e-6, f"unexpected upper bound: {upper}"


def test_credible_bound_fp_rate_msi_like_corpus_too_small_for_l3() -> None:
    """msi-style: 18 benigns total.  Even 0 FPs has a 95% upper bound around
    15% — decisively above any L3 (3 FP/M) target.  This test documents the
    fundamental small-corpus limit."""
    from collimator.thresholds import credible_bound_fp_rate

    upper = credible_bound_fp_rate(0, 18, side="upper", confidence=0.95)
    assert upper > 0.10, (
        f"expected upper bound > 10% for n=18 (truly tiny corpus); got {upper}"
    )


def test_credible_bound_fp_rate_monotone_in_fp_count() -> None:
    """For fixed n_benign, more empirical FPs ⇒ higher posterior upper bound."""
    from collimator.thresholds import credible_bound_fp_rate

    n_benign = 1000
    bounds = [
        credible_bound_fp_rate(k, n_benign, side="upper", confidence=0.95)
        for k in (0, 1, 5, 10, 50)
    ]
    for prev, curr in zip(bounds, bounds[1:]):
        assert curr > prev, f"non-monotone: {bounds}"


def test_credible_bound_fp_rate_lower_below_upper() -> None:
    """Lower credible bound must be below upper bound for nontrivial counts."""
    from collimator.thresholds import credible_bound_fp_rate

    lower = credible_bound_fp_rate(5, 1000, side="lower", confidence=0.95)
    upper = credible_bound_fp_rate(5, 1000, side="upper", confidence=0.95)
    assert 0 <= lower < upper, f"expected 0 <= lower < upper, got {lower}, {upper}"


def test_select_threshold_at_credible_bound_strictly_stricter_than_empirical() -> None:
    """The credible-bound threshold should be ≥ the empirical threshold for
    the same target FP/M when N is small — i.e. we deploy a tighter (=larger)
    threshold when sample size is sparse, because we can't confirm the
    empirical FPR is reliable."""
    import numpy as np

    from collimator.thresholds import (
        _select_threshold_at_fp_budget,
        _fp_budget_for_per_million,
        select_threshold_at_credible_bound,
    )

    # Synthetic: 200 benigns; if we set threshold low enough to admit 1 FP,
    # empirical FPR is 0.5%, comfortably above 3 FP/M target — but the
    # smoothed estimator should still detect the budget violation.
    n_benign = 200
    n_malware = 50
    # Threshold→stats arrays in descending threshold order — what
    # _select_threshold_at_fp_budget expects.
    thresholds = np.linspace(0.99, 0.50, 50)
    fp_vals = np.arange(50, dtype=np.int32)  # 0, 1, 2, ... FPs as threshold drops
    tp_vals = np.linspace(0, n_malware, 50).astype(np.int32)
    recall_vals = tp_vals / n_malware
    fpr_vals = fp_vals / n_benign

    target_per_million = 3.0
    max_fp = _fp_budget_for_per_million(n_benign, target_per_million)
    empirical = _select_threshold_at_fp_budget(
        thresholds, tp_vals, fp_vals, recall_vals, fpr_vals,
        n_benign, n_malware, max_fp=max_fp,
    )
    smoothed = select_threshold_at_credible_bound(
        thresholds, tp_vals, fp_vals, recall_vals, fpr_vals,
        n_benign, n_malware, max_fp_per_million=target_per_million,
    )
    assert empirical is not None and smoothed is not None
    # smoothed threshold should be >= empirical (stricter or equal).
    assert smoothed["threshold"] >= empirical["threshold"], (
        f"smoothed threshold {smoothed['threshold']} below empirical "
        f"{empirical['threshold']} — smoothing should never relax the bound"
    )
    # And smoothed must annotate its credible bound for auditability.
    assert "credible_bound_fp_rate" in smoothed
    assert "credible_bound_confidence" in smoothed
