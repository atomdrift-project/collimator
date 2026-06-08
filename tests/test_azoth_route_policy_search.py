"""Tests for the Step-2 specialist triage gate in azoth_route_policy_search.

`_specialist_earns_keep` decides whether a filetype specialist enters the
ensemble at all. The gate measures the specialist's *marginal ensemble
contribution* — does adding it lift the max-rule recall at a matched FP budget
for some deployed level — rather than its standalone ranking. A specialist that
adds no recall (near-random, or it pins its own benigns at the ceiling so the
operating point can't admit its malware) is dropped; one that genuinely
separates is kept even if its standalone ROC is weak.
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np

# ``scripts/`` isn't an installed package; the module imports sibling scripts
# (azoth_calibrate_ensemble) and the collimator package, so both dirs go on path.
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "src"))
_SCRIPT = _ROOT / "scripts" / "azoth_route_policy_search.py"
_spec = importlib.util.spec_from_file_location("azoth_route_policy_search", _SCRIPT)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Two deployed levels at FP budgets that resolve empirically on the 2000-benign
# slices below (rate_budget = n_ben * tpm / 1e6 >= 1).
_CONFIG = {
    "levels": [
        {"level": 50, "hostile": {"target_per_million": 2000.0}},
        {"level": 100, "hostile": {"target_per_million": 10000.0}},
    ]
}
_NBEN = 2000
_NMAL = 2000


def _labels() -> np.ndarray:
    return np.concatenate([np.zeros(_NBEN), np.ones(_NMAL)]).astype(int)


def _keep(route_probs, type_route="filetypes/x"):
    return _mod._specialist_earns_keep(
        route_probs, type_route, _labels(), config=_CONFIG, total_benign=_NBEN
    )


def test_specialist_that_lifts_recall_is_kept():
    rng = np.random.default_rng(0)
    # General is weak on this slice (poor separation).
    gen = np.concatenate(
        [rng.uniform(0, 0.9, _NBEN), rng.uniform(0.1, 0.9, _NMAL)]
    ).astype(np.float32)
    # Specialist: clean benigns, and it catches ~40% of malware general misses
    # by scoring them near the ceiling.
    spec_mal = rng.uniform(0, 0.3, _NMAL)
    spec_mal[: int(0.4 * _NMAL)] = rng.uniform(0.9, 0.99, int(0.4 * _NMAL))
    spec = np.concatenate([rng.uniform(0, 0.3, _NBEN), spec_mal]).astype(np.float32)
    assert _keep({"general": gen, "filetypes/x": spec}) is True


def test_noise_specialist_is_dropped():
    rng = np.random.default_rng(1)
    gen = np.concatenate(
        [rng.uniform(0, 0.9, _NBEN), rng.uniform(0.1, 0.9, _NMAL)]
    ).astype(np.float32)
    # Pure noise — same distribution for both classes, no separation.
    spec = rng.uniform(0, 1, _NBEN + _NMAL).astype(np.float32)
    assert _keep({"general": gen, "filetypes/x": spec}) is False


def test_ceiling_pinning_specialist_is_dropped():
    rng = np.random.default_rng(2)
    gen = np.concatenate(
        [rng.uniform(0, 0.6, _NBEN), rng.uniform(0.2, 0.9, _NMAL)]
    ).astype(np.float32)
    # Overconfident: scores its malware low, but pins a chunk of its benigns at
    # the ceiling — that raises the matched-FP threshold and admits no malware.
    spec_ben = rng.uniform(0, 0.3, _NBEN)
    spec_ben[:150] = rng.uniform(0.99, 1.0, 150)
    spec = np.concatenate([spec_ben, rng.uniform(0, 0.3, _NMAL)]).astype(np.float32)
    assert _keep({"general": gen, "filetypes/x": spec}) is False


def test_too_few_malware_dropped():
    rng = np.random.default_rng(3)
    n_mal = _mod._SPECIALIST_MIN_MALWARE - 1
    y = np.concatenate([np.zeros(_NBEN), np.ones(n_mal)]).astype(int)
    gen = rng.uniform(0, 0.5, _NBEN + n_mal).astype(np.float32)
    spec = np.concatenate(
        [rng.uniform(0, 0.3, _NBEN), rng.uniform(0.9, 1.0, n_mal)]
    ).astype(np.float32)
    assert (
        _mod._specialist_earns_keep(
            {"general": gen, "filetypes/x": spec}, "filetypes/x", y,
            config=_CONFIG, total_benign=_NBEN,
        )
        is False
    )


def test_missing_specialist_returns_false():
    rng = np.random.default_rng(4)
    gen = rng.uniform(0, 1, _NBEN + _NMAL).astype(np.float32)
    # No filetypes/x entry → nothing to keep.
    assert _keep({"general": gen}) is False


def test_specialist_only_route_is_kept():
    rng = np.random.default_rng(5)
    spec = np.concatenate(
        [rng.uniform(0, 0.3, _NBEN), rng.uniform(0.7, 1.0, _NMAL)]
    ).astype(np.float32)
    # No base routes (general absent) → the specialist is all we have; keep it.
    assert _keep({"filetypes/x": spec}) is True


def _two_strong_one_benign_route():
    """Two routes with real malware signal plus one route that is HIGH on
    benigns and low on malware — the configuration that earns a negative blend
    weight (the pe/`general` pathology)."""
    rng = np.random.default_rng(7)
    n = 4000
    y = (rng.random(n) < 0.5).astype(int)

    def probs(sig):
        return (1.0 / (1.0 + np.exp(-(sig + rng.standard_normal(n) * 0.5)))).astype(
            np.float64
        )

    strong_a = probs(np.where(y == 1, 4.0, -4.0))
    strong_b = probs(np.where(y == 1, 3.0, -3.0))
    benigny = probs(np.where(y == 1, -2.0, 2.0))  # high on benign → wants w<0
    route_probs = {
        "general": benigny,
        "filegroups/native": strong_a,
        "filetypes/pe": strong_b,
    }
    routes = ("general", "filegroups/native", "filetypes/pe")
    return route_probs, y, routes


def test_blend_drops_negative_weight_route():
    # The benign-correlated route would get a negative weight; the non-negativity
    # constraint must drop it and refit on the survivors. A negative weight in an
    # OR-style ensemble vetoes detections (it buried the PE-trojan true positive).
    route_probs, y, routes = _two_strong_one_benign_route()
    fit = _mod._fit_learned_blend(route_probs, y, routes)
    assert fit is not None
    assert "general" not in fit["present_routes"]
    assert set(fit["present_routes"]) == {"filegroups/native", "filetypes/pe"}
    assert all(w >= -_mod._BLEND_MIN_WEIGHT for w in fit["weights"])


def test_blend_keeps_all_positive_weight_routes():
    # When every route carries real malware signal (all positive weights), none
    # are dropped — the constraint only fires on genuine vetoes.
    rng = np.random.default_rng(8)
    n = 4000
    y = (rng.random(n) < 0.5).astype(int)

    def probs(sep):
        return (
            1.0 / (1.0 + np.exp(-(np.where(y == 1, sep, -sep) + rng.standard_normal(n) * 0.5)))
        ).astype(np.float64)

    route_probs = {
        "general": probs(2.0),
        "filegroups/native": probs(3.0),
        "filetypes/pe": probs(2.5),
    }
    routes = ("general", "filegroups/native", "filetypes/pe")
    fit = _mod._fit_learned_blend(route_probs, y, routes)
    assert fit is not None
    assert set(fit["present_routes"]) == set(routes)
    assert all(w >= -_mod._BLEND_MIN_WEIGHT for w in fit["weights"])
