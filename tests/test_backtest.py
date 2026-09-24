"""Tests for the out-of-time operating-point backtest harness."""

from __future__ import annotations

import numpy as np
import pytest

from collimator import backtest as bt


def _slice(n_ben=2000, n_mal=500, seed=0):
    rng = np.random.default_rng(seed)
    labels = np.array([0] * n_ben + [1] * n_mal, dtype=np.int8)
    ben = rng.beta(1, 40, n_ben)
    mal = rng.beta(8, 2, n_mal)
    probs = np.concatenate([ben, mal])
    n = n_ben + n_mal
    return bt.RouteSlice(
        file_type="pe",
        row_ids=np.arange(n, dtype=np.int64),
        labels=labels,
        scores={"general": probs, "filetypes/pe": probs},
        ingested_at=np.arange(n, dtype=np.int64) + 1_700_000_000,
        feed=np.array(["a"] * (n // 2) + ["pe-machine-learning-dataset"] * (n - n // 2)),
        carved=np.zeros(n, dtype=bool),
        cleave_score=np.zeros(n, dtype=np.int32),
        partition=np.array(["train"] * n),
    ), probs


class TestCombine:
    def test_max_of_two_routes(self):
        s, _ = _slice()
        s.scores["filetypes/pe"] = np.zeros(len(s))
        out = bt.combine(s, ["general", "filetypes/pe"], strategy="max")
        assert np.allclose(out, s.scores["general"])

    def test_specialist_requires_single_route(self):
        s, _ = _slice()
        with pytest.raises(ValueError):
            bt.combine(s, ["general", "filetypes/pe"], strategy="specialist")

    def test_unknown_route_raises(self):
        s, _ = _slice()
        with pytest.raises(KeyError):
            bt.combine(s, ["nope"])


class TestMeasure:
    def test_counts_and_rates(self):
        labels = np.array([0, 0, 1, 1], dtype=np.int8)
        probs = np.array([0.1, 0.9, 0.4, 0.95])
        out = bt.measure(probs, labels, 0.9)
        assert out["tp"] == 1 and out["fp"] == 1
        assert out["recall"] == 0.5
        assert out["fp_per_million"] == pytest.approx(5e5)

    def test_threshold_is_inclusive(self):
        """Deploy grades ``score >= threshold`` as firing; so must the harness."""
        labels = np.array([0, 1], dtype=np.int8)
        out = bt.measure(np.array([0.5, 0.5]), labels, 0.5)
        assert out["fp"] == 1 and out["tp"] == 1


class TestBacktestSeparation:
    def test_overlapping_populations_rejected(self):
        """The whole point of the harness: in-sample measurement must be an error."""
        s, _ = _slice()
        both = s.benign.copy()
        with pytest.raises(ValueError, match="overlap"):
            bt.backtest(s, fit_benign=both, eval_mask=both, level=25)

    def test_overlap_allowed_only_when_asked(self):
        s, _ = _slice()
        both = s.benign.copy()
        res = bt.backtest(s, fit_benign=both, eval_mask=both, level=25,
                          allow_overlap=True)
        assert res["n_benign"] > 0

    def test_empty_fit_population_rejected(self):
        s, _ = _slice()
        with pytest.raises(ValueError, match="no benign rows"):
            bt.backtest(s, fit_benign=np.zeros(len(s), bool),
                        eval_mask=np.ones(len(s), bool), level=25)

    def test_disjoint_split_runs(self):
        s, _ = _slice()
        half = len(s) // 2
        fit = s.benign.copy()
        fit[half:] = False
        ev = np.zeros(len(s), bool)
        ev[half:] = True
        res = bt.backtest(s, fit_benign=fit, eval_mask=ev, level=25)
        assert res["thresholds"]
        assert 0.0 <= res["recall"] <= 1.0


class TestPolicy:
    def test_joint_or_fires_if_any_route_clears(self):
        s, _ = _slice()
        s.scores["general"][:] = 0.0
        s.scores["filetypes/pe"][:] = 0.0
        s.scores["filetypes/pe"][5] = 1.0
        pol = bt.Policy("joint_or", ("general", "filetypes/pe"),
                        {"general": 0.5, "filetypes/pe": 0.5}, {})
        fired = bt.apply_policy(s, pol)
        assert fired[5] and fired.sum() == 1

    def test_joint_or_catches_at_least_as_much_as_max(self):
        """OR-ing per-route thresholds is never stricter than one max threshold
        fitted at the same level — this is the 4.8% vs 26% gap on pe."""
        s, _ = _slice(n_ben=4000, n_mal=1000, seed=11)
        rng = np.random.default_rng(12)
        s.scores["filetypes/pe"] = np.clip(s.scores["general"] + rng.normal(0, .2, len(s)), 0, 1)
        fit = s.benign
        j = bt.fit_policy(s, fit, level=1000, kind="joint_or")
        m = bt.fit_policy(s, fit, level=1000, kind="max")
        assert bt.apply_policy(s, j).sum() >= bt.apply_policy(s, m).sum()

    def test_extrapolated_flag_propagates(self):
        s, _ = _slice(n_ben=300, n_mal=100)
        pol = bt.fit_policy(s, s.benign, level=25, estimator="true_rate", kind="joint_or")
        assert pol.extrapolated


class TestEstimators:
    def test_below_min_benign_returns_none(self):
        for name, fn in bt.ESTIMATORS.items():
            thr, method = fn(np.linspace(0, 1, 10), 0.25)
            assert thr is None and method == "none", name

    def test_true_rate_is_at_least_as_strict_as_shared(self):
        """true_rate drops the resolution shift, so it never asks for a LOOSER
        rate than the level literally names."""
        rng = np.random.default_rng(3)
        ben = rng.beta(1, 40, 5000)
        shared, _ = bt.estimator_shared(ben, 0.25)
        true_rate, _ = bt.estimator_true_rate(ben, 0.25)
        assert true_rate >= shared

    def test_true_rate_extrapolates_when_pool_cannot_resolve(self):
        rng = np.random.default_rng(4)
        ben = rng.beta(1, 40, 1000)   # 1-FP floor is 1e5/100M; L25 is far below
        _, method = bt.estimator_true_rate(ben, 0.25)
        assert method == "extrapolated"

    def test_true_rate_measures_when_pool_can_resolve(self):
        rng = np.random.default_rng(5)
        ben = rng.beta(1, 40, 1000)
        _, method = bt.estimator_true_rate(ben, 5000.0)
        assert method == "measured"

    def test_thresholds_are_monotone_in_level(self):
        rng = np.random.default_rng(6)
        ben = rng.beta(1, 40, 20000)
        for name, fn in bt.ESTIMATORS.items():
            ts = [fn(ben, lvl / 100.0)[0] for lvl in (1, 25, 100, 1000, 10000)]
            assert all(a >= b for a, b in zip(ts[:-1], ts[1:], strict=True)), f"{name}: {ts}"


class TestExtrapolationError:
    def test_only_extrapolated_configurations_are_reported(self):
        """A row whose rate the fit sample could measure is not a test of
        extrapolation and must not be included."""
        rng = np.random.default_rng(7)
        ben = rng.beta(1, 40, 50000)
        rows = bt.extrapolation_error(ben, trials=3)
        assert rows, "expected at least one extrapolated configuration"
        for r in rows:
            assert r["method"] == "extrapolated"
            assert r["requested_per_million"] < 1e6 / r["n_fit_benign"]
            assert r["decades"] > 0

    def test_rows_are_ordered_by_distance(self):
        rng = np.random.default_rng(8)
        ben = rng.beta(1, 40, 50000)
        rows = bt.extrapolation_error(ben, trials=3)
        assert [r["decades"] for r in rows] == sorted(r["decades"] for r in rows)

    def test_decades_needed_is_zero_when_pool_resolves_the_level(self):
        assert bt.decades_needed(4_000_000, 25) == pytest.approx(0.0)
        assert bt.decades_needed(265_576, 25) > 1.0


class TestStability:
    def test_spread_is_nonnegative_and_ordered(self):
        rng = np.random.default_rng(9)
        ben = rng.beta(1, 40, 20000)
        r = bt.threshold_stability(ben, level=25, trials=10)
        assert r["threshold_p05"] <= r["threshold_median"] <= r["threshold_p95"]
        assert r["fp_per_million_spread"] >= 0

    def test_deterministic_for_a_seed(self):
        rng = np.random.default_rng(10)
        ben = rng.beta(1, 40, 5000)
        a = bt.threshold_stability(ben, level=25, trials=8, seed=1)
        b = bt.threshold_stability(ben, level=25, trials=8, seed=1)
        assert a == b


class TestMeasurePolicy:
    def test_matches_measure_for_a_single_route(self):
        s, probs = _slice()
        pol = bt.Policy("joint_or", ("general",), {"general": 0.9}, {})
        a = bt.measure_policy(s, pol, np.ones(len(s), bool))
        b = bt.measure(probs, s.labels, 0.9)
        assert (a["tp"], a["fp"], a["recall"]) == (b["tp"], b["fp"], b["recall"])


class TestNaNHandling:
    def test_unscored_rows_do_not_poison_a_threshold(self):
        """A route leaves NaN for rows it did not score. Sorting those into the
        benign tail yields a NaN threshold, which fires on nothing and silently
        drops the route out of the OR — this caught a real bug on
        filegroups/native (57 unscored rows of 1.9M)."""
        s, _ = _slice()
        s.scores["general"][3] = np.nan
        pol = bt.fit_policy(s, s.benign, level=25, routes=["general"], kind="joint_or")
        assert np.isfinite(pol.thresholds["general"])

    def test_unscored_row_never_fires(self):
        s, _ = _slice()
        s.scores["general"][:] = np.nan
        pol = bt.Policy("joint_or", ("general",), {"general": 0.5}, {})
        assert not bt.apply_policy(s, pol).any()

    def test_route_with_no_usable_threshold_is_dropped(self):
        s, _ = _slice()
        s.scores["general"] = np.full(len(s), np.nan)
        pol = bt.fit_policy(s, s.benign, level=25, routes=["general"], kind="joint_or")
        assert "general" not in pol.thresholds


class TestComparePolicies:
    def test_identical_policies_have_zero_delta(self):
        s, _ = _slice()
        pol = bt.Policy("joint_or", ("general",), {"general": 0.5}, {})
        d = bt.compare_policies(s, pol, pol, np.ones(len(s), bool), n_resamples=50)
        assert d["diff"] == 0.0
        assert not d["significant"]

    def test_strictly_better_policy_is_significant(self):
        s, _ = _slice(n_ben=3000, n_mal=3000, seed=2)
        loose = bt.Policy("joint_or", ("general",), {"general": 0.3}, {})
        tight = bt.Policy("joint_or", ("general",), {"general": 0.95}, {})
        d = bt.compare_policies(s, loose, tight, np.ones(len(s), bool), n_resamples=200)
        assert d["diff"] > 0 and d["significant"]


class TestBenignTail:
    def test_ranked_worst_first(self):
        s, _ = _slice()
        rows = bt.benign_tail(s, "general", top=20)
        scores = [r["score"] for r in rows]
        assert scores == sorted(scores, reverse=True)

    def test_gain_is_monotone_nondecreasing(self):
        """Removing more of the tail can only lower the threshold, so recall
        gain never goes backwards down the list."""
        s, _ = _slice()
        gains = [r["recall_gain_pp"] for r in bt.benign_tail(s, "general", top=30)]
        assert all(a <= b + 1e-9 for a, b in zip(gains[:-1], gains[1:], strict=True))

    def test_only_benign_rows_are_listed(self):
        s, _ = _slice()
        ids = {r["row_id"] for r in bt.benign_tail(s, "general", top=50)}
        benign_ids = set(s.row_ids[s.benign].tolist())
        assert ids <= benign_ids
