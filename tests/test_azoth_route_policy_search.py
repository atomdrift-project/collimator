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


# --- L0 anchor, malware floor, and level-grid monotonicity -------------------
#
# Regression cover for the 2026-08-04 bundle, which shipped filetypes/odf an L0
# general threshold of 8.07e-06 fitted on 370 benign ODFs. It was perfect on
# the slice, fired on essentially every real ODF, and graded three benign
# fixtures hostile at every deploy level.


def _cand(policy, thresholds, *, tpm, tp, fp, recall, f1=None, fp_per_100M=0.0):
    return {
        "policy": policy,
        "primary": None,
        "allowed_routes": list(thresholds),
        "target_per_million": tpm,
        "thresholds": dict(thresholds),
        "tp": tp,
        "fp": fp,
        "recall": recall,
        "f1": recall if f1 is None else f1,
        "fp_per_100M": fp_per_100M,
    }


_ANCHOR = {"general": 0.9995415806770325}


def test_l0_rejects_threshold_looser_than_the_calibrate_anchor():
    """The odf case: slice-perfect, zero slice FP, five orders of magnitude
    below the wider-scope threshold. Recall-first ranking would take it."""
    degenerate = _cand(
        "or_general_primary", {"general": 8.072087394214536e-06},
        tpm=0.0, tp=5, fp=0, recall=1.0,
    )
    inherited = _cand(
        "calibrate_inherited", _ANCHOR, tpm=0.0, tp=0, fp=0, recall=0.0,
    )
    no_policy = _cand("no_policy", {}, tpm=0.0, tp=0, fp=0, recall=0.0)
    best = _mod._choose_best([no_policy, degenerate, inherited], anchor=_ANCHOR)
    assert best["policy"] != "or_general_primary", (
        "a threshold the slice cannot justify must not win at L0"
    )
    assert best["thresholds"].get("general", 0.0) >= _ANCHOR["general"]


def test_l0_keeps_a_threshold_stricter_than_the_anchor():
    """Tightening is always defensible — the slice can prove it needs less
    reach, it just can't prove it needs more."""
    stricter = _cand(
        "or_general_primary", {"general": 0.99999},
        tpm=0.0, tp=7, fp=0, recall=0.7,
    )
    inherited = _cand(
        "calibrate_inherited", _ANCHOR, tpm=0.0, tp=3, fp=0, recall=0.3,
    )
    best = _mod._choose_best([stricter, inherited], anchor=_ANCHOR)
    assert best["policy"] == "or_general_primary"


def test_anchor_rule_does_not_apply_above_l0():
    """Every level from L1 up has a non-zero target, so the rate filter can do
    its job and slice-local thresholds stay free to loosen."""
    looser = _cand(
        "or_general_primary", {"general": 0.5},
        tpm=0.01, tp=9, fp=0, recall=0.9, fp_per_100M=0.0,
    )
    inherited = _cand(
        "calibrate_inherited", _ANCHOR, tpm=0.01, tp=1, fp=0, recall=0.1,
    )
    best = _mod._choose_best([looser, inherited], anchor=_ANCHOR)
    assert best["policy"] == "or_general_primary"


def test_min_slice_malware_floor_matches_the_specialist_floor():
    assert _mod._MIN_SLICE_MALWARE >= _mod._SPECIALIST_MIN_MALWARE


def _payload(levels):
    return {
        "routes": {
            "filetypes/x": {
                "levels": [
                    {"level": lvl, "hostile": {"target_per_million": tpm, "best": best}}
                    for lvl, tpm, best in levels
                ],
            },
        },
    }


def test_looser_level_inherits_a_stricter_policy_that_catches_more():
    """filetypes/pdf shipped L0 catching 26,819 at zero FP and L1 catching
    nothing, because every L1 candidate failed the rate filter."""
    strict = _cand("or_general_primary", {"general": 0.99}, tpm=0.0,
                   tp=26819, fp=0, recall=0.15)
    collapsed = _cand("no_policy", {}, tpm=0.01, tp=0, fp=0, recall=0.0)
    payload = _payload([(0, 0.0, strict), (1, 0.01, collapsed)])
    assert _mod._enforce_level_dominance(payload) == 1
    adopted = payload["routes"]["filetypes/x"]["levels"][1]["hostile"]["best"]
    assert adopted["tp"] == 26819
    assert adopted["thresholds"] == {"general": 0.99}
    assert adopted["inherited_from_level"] == 0
    # The level's own budget is re-stamped; the counts come from the policy.
    assert adopted["target_per_million"] == 0.01
    assert not _mod._level_monotonicity_errors(payload)


def test_a_level_keeps_its_own_policy_when_it_beats_the_stricter_one():
    strict = _cand("or_general_primary", {"general": 0.99}, tpm=0.0,
                   tp=100, fp=0, recall=0.1)
    better = _cand("joint_or", {"general": 0.9}, tpm=0.01,
                   tp=400, fp=2, recall=0.4)
    payload = _payload([(0, 0.0, strict), (1, 0.01, better)])
    assert _mod._enforce_level_dominance(payload) == 0
    assert payload["routes"]["filetypes/x"]["levels"][1]["hostile"]["best"] is better


def test_monotonicity_check_flags_a_strict_level_that_fires_more():
    strict = _cand("or_general_primary", {"general": 0.1}, tpm=0.0,
                   tp=500, fp=0, recall=0.5)
    loose = _cand("no_policy", {}, tpm=0.01, tp=0, fp=0, recall=0.0)
    errors = _mod._level_monotonicity_errors(
        _payload([(0, 0.0, strict), (1, 0.01, loose)]),
    )
    assert len(errors) == 1
    assert "L0 fires on more malware than L1" in errors[0]
