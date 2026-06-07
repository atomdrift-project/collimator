"""Tests for the azoth ensemble calibration internals: quantile-severity
threshold derivation, Clopper-Pearson FP-per-million bounds, per-route
threshold evaluation, and bundle route loading.

(The per-route isotonic calibrator was removed — it was decision-irrelevant
and saturated the score tail; deploy now runs on raw probabilities. See the
project_calibrator_decision_irrelevant memory.)
"""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

# ``scripts/`` isn't an installed package; load the module directly.
_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "azoth_calibrate_ensemble.py"
_spec = importlib.util.spec_from_file_location("azoth_calibrate_ensemble", _SCRIPT)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
sys.modules["azoth_calibrate_ensemble"] = _mod
_spec.loader.exec_module(_mod)


def test_evaluate_thresholds_at_level_applies_without_search() -> None:
    """_evaluate_thresholds_at_level should apply pre-fit thresholds and
    compute tp/fp without running coordinate descent. Used for fit-on-dev,
    evaluate-on-test scoring."""
    rng = np.random.default_rng(13)
    n = 1000
    labels = rng.integers(0, 2, size=n).astype(np.int8)
    # Two routes both scoring on the same rows; route A is more accurate.
    probs_a = np.clip(0.05 + 0.85 * labels + rng.normal(0, 0.05, size=n), 0.0, 1.0).astype(np.float32)
    probs_b = np.clip(0.10 + 0.50 * labels + rng.normal(0, 0.20, size=n), 0.0, 1.0).astype(np.float32)
    indices = np.arange(n, dtype=np.int64)
    route_scores = [
        {"name": "general", "kind": "general", "indices": indices, "probs": probs_a},
        {"name": "filetypes/x", "kind": "filetype", "indices": indices, "probs": probs_b},
    ]
    # Apply thresholds chosen on a hypothetical dev set: a tight one (fewer FPs)
    # and a loose one. Regardless of FP target, the function should compute
    # the union OR exactly without rebudgeting.
    result = _mod._evaluate_thresholds_at_level(  # type: ignore[attr-defined]
        labels, route_scores,
        thresholds_for_level={"general": 0.7, "filetypes/x": 0.6},
        target_per_million=3.0,
    )
    # Sanity: thresholds were preserved, tp/fp align with applied OR rule.
    assert result["thresholds"] == {"general": 0.7, "filetypes/x": 0.6}
    n_malware = int(np.sum(labels == 1))
    n_benign = int(np.sum(labels == 0))
    union_hit = (probs_a >= 0.7) | (probs_b >= 0.6)
    expected_tp = int(np.sum(union_hit & (labels == 1)))
    expected_fp = int(np.sum(union_hit & (labels == 0)))
    assert result["tp"] == expected_tp
    assert result["fp"] == expected_fp
    assert result["tn"] == n_benign - expected_fp
    assert result["fn"] == n_malware - expected_tp
    # Diagnostics carry the threshold for each named route.
    assert result["diagnostics"]["general"]["selected_threshold"] == 0.7
    assert result["diagnostics"]["filetypes/x"]["selected_threshold"] == 0.6


def test_clopper_pearson_x0_matches_rule_of_three() -> None:
    """The classic 'rule of three' for binomial 95% upper bounds at x=0:
    upper bound ≈ 3/n × 10⁶ FP/M for large n."""
    n = 150_000
    upper = _mod._clopper_pearson_fp_per_million_upper(0, n, alpha=0.05)  # type: ignore[attr-defined]
    # Exact CP at x=0 is 1 - α^(1/n); rule of three is the small-α
    # asymptotic. With n=150k and α=0.05, the exact answer is ~19.97 FP/M.
    assert 19.5 < upper < 20.5


def test_clopper_pearson_grows_with_x() -> None:
    """Adding observed FPs strictly raises the upper bound."""
    n = 150_000
    bounds = [
        _mod._clopper_pearson_fp_per_million_upper(x, n, alpha=0.05)  # type: ignore[attr-defined]
        for x in (0, 1, 2, 5, 10, 20)
    ]
    # Strictly increasing.
    for a, b in zip(bounds, bounds[1:]):
        assert b > a
    # Sanity sketch: x=20 in n=150k → about 200 FP/M (Wilson-style).
    assert 150 < bounds[-1] < 250


def test_clopper_pearson_smaller_n_widens_bound() -> None:
    """Holding x fixed, a smaller n yields a wider upper bound."""
    upper_small = _mod._clopper_pearson_fp_per_million_upper(0, 1_000, alpha=0.05)  # type: ignore[attr-defined]
    upper_large = _mod._clopper_pearson_fp_per_million_upper(0, 1_000_000, alpha=0.05)  # type: ignore[attr-defined]
    assert upper_small > upper_large
    # n=1k has ~3000 FP/M floor; n=1M has ~3 FP/M floor.
    assert 2900 < upper_small < 3100
    assert 2.5 < upper_large < 3.5


def test_max_dev_fp_for_target_below_resolution_at_strict_target() -> None:
    """When even x=0 dev FPs projects above target, mark below_resolution."""
    # n=150k benigns, target q=3 FP/M. Floor ~20 → below resolution.
    max_fp, below = _mod._max_dev_fp_for_target(3.0, 150_000, alpha=0.05)  # type: ignore[attr-defined]
    assert below is True
    assert max_fp == 0


def test_max_dev_fp_for_target_resolves_at_loose_target() -> None:
    """At q safely above the volume floor, the function returns the largest
    integer x whose CP upper still fits under the target."""
    n = 150_000
    # q=100 FP/M is well above the 20 FP/M floor.
    max_fp, below = _mod._max_dev_fp_for_target(100.0, n, alpha=0.05)  # type: ignore[attr-defined]
    assert below is False
    assert max_fp >= 1
    # The chosen max_fp must satisfy the budget.
    assert _mod._clopper_pearson_fp_per_million_upper(max_fp, n, alpha=0.05) <= 100.0  # type: ignore[attr-defined]
    # And max_fp + 1 must violate it (we picked the largest valid x).
    assert _mod._clopper_pearson_fp_per_million_upper(max_fp + 1, n, alpha=0.05) > 100.0  # type: ignore[attr-defined]


def test_max_dev_fp_for_target_resolves_at_large_n() -> None:
    """When the calibration sample is large (e.g., k=2 OOF gives ~2.4M
    benigns), strict targets like q=3 FP/M ARE resolvable."""
    n = 2_400_000
    max_fp, below = _mod._max_dev_fp_for_target(3.0, n, alpha=0.05)  # type: ignore[attr-defined]
    assert below is False
    # CP upper at x=0 with n=2.4M ≈ 1.25 FP/M, well under 3.
    assert max_fp >= 0
    # We expect a few FPs allowed.
    assert max_fp >= 1


def test_quantile_severity_threshold_empirical_when_resolvable() -> None:
    """When q × N / 1e6 ≥ 1, _quantile_severity_threshold returns the
    empirical (1 − q×10⁻⁶) quantile of benign scores.

    Construct 100k benign scores uniform in [0, 1]. At q = 50,000 FP/M
    (5% of benigns), the empirical quantile is around 0.95.
    """
    rng = np.random.default_rng(5)
    benign_probs = rng.uniform(0.0, 1.0, size=100_000).astype(np.float64)
    threshold, method = _mod._quantile_severity_threshold(  # type: ignore[attr-defined]
        benign_probs, target_per_million=50_000.0,
    )
    assert method == "empirical"
    assert threshold is not None
    # Should be very close to the 95th percentile of a uniform[0,1] sample.
    assert 0.93 < threshold < 0.97


def test_quantile_severity_threshold_below_floor_uses_absolute_fp() -> None:
    """A low-volume route that can't resolve the per-100M rate switches to the
    absolute-FP regime — a real threshold <= max benign admitting a bounded FP
    count, never an above-max value that could overshoot on live traffic.

    A 2k-row benign sample can't resolve q=100 FP/M (n × p = 2000 × 1e-4 = 0.2
    expected FP, below 1), and 2k < the 25k low-volume cutoff, so the level is
    read as an absolute FP count capped at 5% of benigns (here 100 FP).
    """
    rng = np.random.default_rng(11)
    benign_probs = np.clip(rng.beta(0.5, 5.0, size=2000) + 0.3, 0.0, 1.0).astype(np.float64)
    threshold, method = _mod._quantile_severity_threshold(  # type: ignore[attr-defined]
        benign_probs, target_per_million=100.0,
    )
    assert threshold is not None
    assert method == "absolute_fp"
    assert 0.0 <= threshold <= float(benign_probs.max())
    fp = int((benign_probs >= threshold).sum())
    assert 1 <= fp <= max(1, round(0.05 * 2000))  # bounded by the 5% cap


def test_quantile_severity_threshold_returns_none_for_too_few_benigns() -> None:
    """Below the 50-row floor, no threshold is derivable."""
    rng = np.random.default_rng(3)
    benign_probs = rng.uniform(0.0, 1.0, size=10).astype(np.float64)
    threshold, method = _mod._quantile_severity_threshold(  # type: ignore[attr-defined]
        benign_probs, target_per_million=1000.0,
    )
    assert threshold is None
    assert method == "none"


def test_calibrate_one_per_route_quantile_no_search() -> None:
    """_calibrate_one derives one threshold per route from benign-score
    quantiles independently — no coordinate-descent search.

    For each route the threshold should be near the (1 - q×10⁻⁶) benign
    quantile of *that* route's benign scores; routes with too few benigns
    are skipped (selected=False). The OR-rule TP/FP totals are computed
    over the union.
    """
    rng = np.random.default_rng(101)
    n = 50_000
    labels = rng.integers(0, 2, size=n).astype(np.int8)
    indices = np.arange(n, dtype=np.int64)

    # Two routes both score on the same rows with different separability.
    probs_a = np.clip(
        0.20 + 0.60 * labels + rng.normal(0, 0.05, size=n), 0.0, 1.0,
    ).astype(np.float32)
    probs_b = np.clip(
        0.30 + 0.30 * labels + rng.normal(0, 0.10, size=n), 0.0, 1.0,
    ).astype(np.float32)
    route_scores = [
        {"name": "general", "kind": "general", "indices": indices, "probs": probs_a},
        {"name": "filetypes/x", "kind": "filetype", "indices": indices, "probs": probs_b},
    ]
    result = _mod._calibrate_one(  # type: ignore[attr-defined]
        labels, route_scores, target_per_million=10_000.0,
    )
    # Every route ended up with a threshold (synthetic separation is strong).
    assert set(result["thresholds"].keys()) == {"general", "filetypes/x"}
    # Each route's threshold matches the (1 − q×10⁻⁶) quantile of its
    # benign scores within a small numerical tolerance.
    p_target = 10_000.0 / 1_000_000.0
    benign_a = probs_a[labels == 0]
    benign_b = probs_b[labels == 0]
    sorted_a = np.sort(benign_a.astype(np.float64))
    sorted_b = np.sort(benign_b.astype(np.float64))
    expected_a = float(sorted_a[int(len(benign_a) * (1 - p_target)) - 1])
    expected_b = float(sorted_b[int(len(benign_b) * (1 - p_target)) - 1])
    assert abs(result["thresholds"]["general"] - expected_a) < 1e-3
    assert abs(result["thresholds"]["filetypes/x"] - expected_b) < 1e-3
    # OR rule: total tp >= each per-route standalone tp.
    standalone_tp = max(
        result["diagnostics"]["general"]["standalone"]["tp"],
        result["diagnostics"]["filetypes/x"]["standalone"]["tp"],
    )
    assert result["tp"] >= standalone_tp
    # Each route's standalone fp count must be at or near the requested rate
    # (with sample-noise slack proportional to the inverse of expected count).
    n_benign_route = int(np.sum(labels == 0))
    expected_fp = n_benign_route * p_target  # roughly 250 per route
    for diag in result["diagnostics"].values():
        assert abs(diag["standalone"]["fp"] - expected_fp) <= max(50.0, 0.3 * expected_fp)


def test_calibrate_one_skips_route_with_too_few_benigns() -> None:
    """A specialist route with <50 benigns gets selected=False with reason."""
    rng = np.random.default_rng(7)
    n_general = 2000
    n_specialist = 30
    n = n_general + n_specialist
    labels = np.concatenate([
        rng.integers(0, 2, size=n_general).astype(np.int8),
        np.ones(n_specialist, dtype=np.int8),  # specialist sees only malware
    ])
    probs_g = np.clip(
        0.3 + 0.4 * labels[:n_general] + rng.normal(0, 0.1, size=n_general),
        0.0, 1.0,
    ).astype(np.float32)
    probs_s = rng.uniform(0.5, 1.0, size=n_specialist).astype(np.float32)
    route_scores = [
        {
            "name": "general",
            "kind": "general",
            "indices": np.arange(0, n_general, dtype=np.int64),
            "probs": probs_g,
        },
        {
            "name": "filetypes/specialist",
            "kind": "filetype",
            "indices": np.arange(n_general, n, dtype=np.int64),
            "probs": probs_s,
        },
    ]
    result = _mod._calibrate_one(  # type: ignore[attr-defined]
        labels, route_scores, target_per_million=10_000.0,
    )
    assert "general" in result["thresholds"]
    assert "filetypes/specialist" not in result["thresholds"]
    assert result["diagnostics"]["filetypes/specialist"]["selected"] is False
    assert "too few benigns" in result["diagnostics"]["filetypes/specialist"]["reason"]


def test_evaluate_thresholds_at_level_skips_missing_route() -> None:
    """A threshold for a route not present in route_scores is silently ignored
    (the bundle's specialist may be missing in this calibration run)."""
    rng = np.random.default_rng(17)
    n = 200
    labels = rng.integers(0, 2, size=n).astype(np.int8)
    probs = np.clip(0.5 + 0.4 * labels + rng.normal(0, 0.1, size=n), 0.0, 1.0).astype(np.float32)
    indices = np.arange(n, dtype=np.int64)
    route_scores = [{"name": "general", "kind": "general", "indices": indices, "probs": probs}]
    # filetypes/missing isn't in route_scores; should not crash.
    result = _mod._evaluate_thresholds_at_level(  # type: ignore[attr-defined]
        labels, route_scores,
        thresholds_for_level={"general": 0.5, "filetypes/missing": 0.3},
        target_per_million=3.0,
    )
    assert "general" in result["thresholds"]
    assert "filetypes/missing" not in result["thresholds"]


def test_load_routes_drops_routes_without_a_model(tmp_path: Path) -> None:
    """A route training refused to emit (constant predictor -> no model on
    disk) is dropped from the route list, so it never reaches config.json and
    litmus routes those files to the filegroup/general ensemble. A route with
    a model + feature_spec is kept."""
    root = tmp_path
    # Present route: has a model file and a feature_spec.
    kept = root / "filetypes" / "elf"
    kept.mkdir(parents=True)
    (kept / "model.txt").write_text("tree\n")
    (kept / "feature_spec.json").write_text("{}")
    # Refused route: recorded in the summary but no model on disk.
    (root / "filetypes" / "xls").mkdir(parents=True)

    summary = {
        "results": [
            {"name": "general", "kind": "general"},
            {"name": "elf", "kind": "filetype"},
            {"name": "xls", "kind": "filetype", "error": True,
             "skip_reason": "constant_predictor"},
        ]
    }
    summary_path = root / "specialists.json"
    summary_path.write_text(json.dumps(summary))

    routes = _mod._load_routes(summary_path)  # type: ignore[attr-defined]
    names = {r["route"] for r in routes}
    assert names == {"filetypes/elf"}
    assert routes[0]["output_dir"] == str(kept)
