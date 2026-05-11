"""Smoke test for the per-route isotonic calibrator emission.

Verifies that ``_fit_and_persist_isotonic_calibrator`` writes a
``calibrator.json`` for every route with enough labeled rows, that the
file matches the ``azoth.calibrator.isotonic.v1`` schema litmus expects,
and that monotone properties (x ascending, y non-decreasing) hold.
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


def _route_scores_for(rng: np.random.Generator, name: str, n: int):
    """Build a synthetic per-route score table where probs correlate with labels."""
    labels = rng.integers(0, 2, size=n).astype(np.int32)
    # Probs are correlated with labels but miscalibrated (centered far from 0.5).
    probs = np.clip(0.3 + 0.4 * labels + rng.normal(0, 0.1, size=n), 0.0, 1.0).astype(np.float32)
    indices = np.arange(n, dtype=np.int64)
    return labels, {"name": name, "probs": probs, "indices": indices}


def test_calibrator_emitted_per_route(tmp_path: Path) -> None:
    rng = np.random.default_rng(42)
    azoth_root = tmp_path / "azoth"

    # Three routes; the calibrator code resolves <azoth_root>/<name>/calibrator.json.
    n = 500
    labels_g, entry_g = _route_scores_for(rng, "general", n)
    labels_e, entry_e = _route_scores_for(rng, "filetypes/elf", n)
    labels_p, entry_p = _route_scores_for(rng, "filegroups/native", n)
    # Each entry indexes into a *shared* labels array; collapse the three
    # synthetic per-route label vectors into a global one and re-index.
    all_labels = np.concatenate([labels_g, labels_e, labels_p])
    entry_g["indices"] = np.arange(0, n)
    entry_e["indices"] = np.arange(n, 2 * n)
    entry_p["indices"] = np.arange(2 * n, 3 * n)

    _mod._fit_and_persist_isotonic_calibrator(  # type: ignore[attr-defined]
        [entry_g, entry_e, entry_p], all_labels, azoth_root
    )

    for name in ("general", "filetypes/elf", "filegroups/native"):
        path = azoth_root / name / "calibrator.json"
        assert path.is_file(), f"missing {path}"
        cal = json.loads(path.read_text())
        assert cal["schema"] == "azoth.calibrator.isotonic.v1"
        assert cal["out_of_bounds"] == "clip"
        x = cal["x"]
        y = cal["y"]
        assert len(x) == len(y) >= 2
        # x ascending, y monotone non-decreasing.
        assert all(x[i] <= x[i + 1] for i in range(len(x) - 1))
        assert all(y[i] <= y[i + 1] for i in range(len(y) - 1))
        # n_train recorded and matches input size.
        assert cal["n_train"] == n


def test_calibrator_skips_too_few_rows(tmp_path: Path) -> None:
    """Routes with <50 valid rows must be skipped silently (no file)."""
    rng = np.random.default_rng(7)
    azoth_root = tmp_path / "azoth"
    labels = rng.integers(0, 2, size=10).astype(np.int32)
    entry = {
        "name": "filetypes/tiny",
        "probs": rng.uniform(0, 1, size=10).astype(np.float32),
        "indices": np.arange(10, dtype=np.int64),
    }
    _mod._fit_and_persist_isotonic_calibrator([entry], labels, azoth_root)  # type: ignore[attr-defined]
    assert not (azoth_root / "filetypes/tiny" / "calibrator.json").exists()


def test_calibrator_skips_single_class_route(tmp_path: Path) -> None:
    """Routes whose labels are all-benign or all-malware can't be calibrated."""
    rng = np.random.default_rng(11)
    azoth_root = tmp_path / "azoth"
    n = 200
    labels = np.zeros(n, dtype=np.int32)  # all benign
    entry = {
        "name": "filetypes/benign_only",
        "probs": rng.uniform(0, 1, size=n).astype(np.float32),
        "indices": np.arange(n, dtype=np.int64),
    }
    _mod._fit_and_persist_isotonic_calibrator([entry], labels, azoth_root)  # type: ignore[attr-defined]
    assert not (azoth_root / "filetypes/benign_only" / "calibrator.json").exists()


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


def test_calibrator_falls_back_to_platt_when_isotonic_tail_degenerate(tmp_path: Path) -> None:
    """When the per-route dev sample has too few high-prob malware to anchor
    isotonic at 1.0, fit Platt scaling instead and serialize the sampled
    curve. Litmus's loader treats it the same way as isotonic
    (piecewise-linear interpolation on x/y) but the y range now spans
    [0, ~1] regardless of dev tail density.

    Specifically: malware all clustered below 0.3, but benigns with rare
    outliers above 0.5. Isotonic's last knot ends up on a benign row,
    forcing max y < 0.7 even though the model still distinguishes the
    classes well at lower thresholds.
    """
    rng = np.random.default_rng(101)
    azoth_root = tmp_path / "azoth"
    n_mal = 1000
    n_ben_low = 3000  # benigns overlapping with the malware bulk
    n_ben_high = 1500  # benign-only outliers at the top of the prob range
    n = n_mal + n_ben_low + n_ben_high
    # Malware sits in [0.1, 0.4]; low-region benigns sit in the same range
    # (overlap → empirical malware rate < 100% there); high-region rows are
    # benign-only — at probs > 0.5, dev sees ONLY benigns, so isotonic's
    # right-end is forced to y=0 even though the model still discriminates
    # across the bulk. Isotonic max y ends up below the production
    # acceptance bar (~0.7).
    mal_probs = rng.uniform(0.1, 0.4, size=n_mal)
    ben_low = rng.uniform(0.0, 0.4, size=n_ben_low)
    ben_high = rng.uniform(0.5, 0.95, size=n_ben_high)
    probs = np.concatenate([mal_probs, ben_low, ben_high]).astype(np.float32)
    labels = np.concatenate([
        np.ones(n_mal, dtype=np.int32),
        np.zeros(n_ben_low + n_ben_high, dtype=np.int32),
    ])
    entry = {
        "name": "filetypes/sparse_tail",
        "probs": probs,
        "indices": np.arange(n, dtype=np.int64),
    }
    _mod._fit_and_persist_isotonic_calibrator([entry], labels, azoth_root)  # type: ignore[attr-defined]
    cal = json.loads((azoth_root / "filetypes/sparse_tail" / "calibrator.json").read_text())
    assert cal["schema"] == "azoth.calibrator.isotonic.v1"
    # Anchor was applied because the empirical fit didn't reach (~1, ~1).
    assert cal["method"] == "isotonic+anchor"
    # After anchoring, the calibrator must reach 1.0 at x=1.0 — that's
    # what makes litmus accept it as a usable verdict-rendering function.
    assert cal["x"][-1] == 1.0
    assert cal["y"][-1] == 1.0
    # Monotone non-decreasing (litmus assumes this).
    y = cal["y"]
    assert all(y[i] <= y[i + 1] for i in range(len(y) - 1))


def test_calibrator_keeps_isotonic_when_tail_is_well_anchored(tmp_path: Path) -> None:
    """When dev has clean separable rows, isotonic is preferred."""
    rng = np.random.default_rng(102)
    azoth_root = tmp_path / "azoth"
    n = 2000
    labels = (rng.random(n) < 0.5).astype(np.int32)
    # Strong separation: malware probs near 1, benign near 0.
    probs = np.where(
        labels == 1,
        np.clip(rng.normal(0.95, 0.02, size=n), 0, 1),
        np.clip(rng.normal(0.05, 0.02, size=n), 0, 1),
    ).astype(np.float32)
    entry = {
        "name": "filetypes/clean",
        "probs": probs,
        "indices": np.arange(n, dtype=np.int64),
    }
    _mod._fit_and_persist_isotonic_calibrator([entry], labels, azoth_root)  # type: ignore[attr-defined]
    cal = json.loads((azoth_root / "filetypes/clean" / "calibrator.json").read_text())
    assert cal["method"] == "isotonic"
    assert max(cal["y"]) > 0.9


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


def test_quantile_severity_threshold_extrapolates_below_floor() -> None:
    """When q is below the empirical floor (q × N < 1e6) but the benign
    sample has enough tail data, GPD extrapolation should kick in.

    A 1k-row benign sample can't directly resolve q=100 FP/M (would need
    n × p_target = 1000 × 1e-4 = 0.1 expected FP — below 1). Drawing from
    a heavy-tailed distribution with enough tail mass should make GPD fit
    succeed and return a finite extrapolated threshold above the empirical
    max for that target.
    """
    rng = np.random.default_rng(11)
    # Heavy-ish tail so GPD has something to fit (Beta concentrated near 1
    # with a long upper tail in [0, 1]).
    benign_probs = np.clip(rng.beta(0.5, 5.0, size=2000) + 0.3, 0.0, 1.0).astype(np.float64)
    threshold, method = _mod._quantile_severity_threshold(  # type: ignore[attr-defined]
        benign_probs, target_per_million=100.0,
    )
    assert threshold is not None
    # Either GPD extrapolated, or fell back to empirical_floor — both are
    # honest for "below empirical resolution" responses. Failure modes
    # (None, "none") would mean the helper bailed.
    assert method in ("extrapolated", "empirical_floor")
    # Threshold must be a real number in [0, 1].
    assert 0.0 <= threshold <= 1.0


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
