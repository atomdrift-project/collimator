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
