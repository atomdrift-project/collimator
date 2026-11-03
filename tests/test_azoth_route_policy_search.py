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
import itertools
import sys
from pathlib import Path

import numpy as np
import pytest

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


def test_joint_one_fp_search_finds_shared_benign_optimum_in_any_route_order():
    labels = np.array([0, 0] + [1] * 11)
    scores = {name: np.zeros(13, dtype=np.float32) for name in ('a', 'b', 'c')}
    scores['a'][:2] = scores['b'][:2] = [.9, .1]
    scores['c'][:2] = [.1, .9]
    scores['a'][2:6] = .8
    scores['b'][6:10] = .8
    scores['c'][10:] = .8
    for routes in itertools.permutations(scores):
        cuts, hit = _mod._joint_or_search(scores, labels, routes, fp_budget=1)
        assert int(np.sum(hit & (labels == 1))) == 8
        assert int(np.sum(hit & (labels == 0))) == 1
        np.testing.assert_array_equal(
            hit, _mod.policy.margin(scores, {'thresholds': cuts}, len(labels)) >= 0)


@pytest.mark.parametrize('budget', [0, 1])
def test_joint_small_budget_matches_exhaustive_threshold_search(budget):
    rng = np.random.default_rng(9127)
    labels = np.array([0, 0, 1, 1, 1, 1])
    values = np.array([0, .25, .75, 1, np.nan], dtype=np.float32)
    for _ in range(25):
        scores = {name: rng.choice(values, len(labels)) for name in ('a', 'b', 'c')}
        options = [np.r_[np.unique(p[np.isfinite(p)]), _mod._INACTIVE_THRESHOLD]
                   for p in scores.values()]
        optimum = (0, 0)
        for thresholds in itertools.product(*options):
            decision = {'thresholds': dict(zip(scores, thresholds, strict=True))}
            hit = _mod.policy.margin(scores, decision, len(labels)) >= 0
            fp = int(np.sum(hit & (labels == 0)))
            if fp <= budget:
                optimum = max(optimum, (int(np.sum(hit & (labels == 1))), -fp))
        cuts, hit = _mod._joint_or_search(scores, labels, tuple(scores), fp_budget=budget)
        assert (int(np.sum(hit & (labels == 1))), -int(np.sum(hit & (labels == 0)))) == optimum
        np.testing.assert_array_equal(
            hit, _mod.policy.margin(scores, {'thresholds': cuts}, len(labels)) >= 0)


def test_uncalibrated_route_stays_inactive_at_probability_one():
    labels = np.array([0, 1])
    scores = {'filetypes/x': np.array([1., 1.], dtype=np.float32)}
    candidate = _mod._calibrate_policy(
        labels, scores, policy='filetype_only', primary='filetypes/x',
        allowed_routes=('filetypes/x',), target_per_million=1., total_benign=1,
    )
    deployed_hit = _mod.policy.margin(scores, candidate, len(labels)) >= 0
    assert not deployed_hit.any()
    assert candidate['tp'] == candidate['fp'] == 0


def test_joint_policy_can_detect_probability_one_without_treating_it_as_disabled():
    labels = np.array([0, 0, 1, 1])
    scores = {'general': np.array([.2, .3, 1., .1], dtype=np.float32),
              'filetypes/x': np.array([.2, .3, .1, 1.], dtype=np.float32)}
    candidate = _mod._make_joint_or_candidate_at_fp(
        route_probs=scores, labels=labels, routes=tuple(scores), fp_target=0,
        target_per_million=1., total_benign=2,
    )
    assert candidate is not None
    deployed_hit = _mod.policy.margin(scores, candidate, len(labels)) >= 0
    assert deployed_hit.tolist() == [False, False, True, True]
    assert candidate['tp'] == 2 and candidate['fp'] == 0


def test_threshold_budget_cannot_split_equal_probability_rows():
    labels = np.array([1, 0, 0, 1])
    scores = np.array([.9, .8, .8, .7], dtype=np.float32)
    threshold, tp, fp = _mod._specialist_threshold_for_fp(scores, labels, 1)
    hit = scores >= threshold
    assert int((hit & (labels == 0)).sum()) == fp <= 1
    assert int((hit & (labels == 1)).sum()) == tp == 1


def _labels() -> np.ndarray:
    return np.concatenate([np.zeros(_NBEN), np.ones(_NMAL)]).astype(int)


def test_global_auxiliary_can_recover_complementary_detections(monkeypatch):
    labels = np.r_[np.zeros(60), np.ones(60)].astype(np.int8)
    benign = np.linspace(.15, .25, 60)
    # The models use different raw score scales. A shared max-rule cutoff
    # cannot recover both halves; their thresholds must be chosen jointly.
    general = np.r_[benign, np.full(30, .5), np.full(30, .1)].astype(np.float32)
    auxiliary = np.r_[np.linspace(.7, .8, 60), np.full(30, .7), np.full(30, .9)].astype(np.float32)
    name = 'filegroups/general_previous'
    routes = {'general': {'indices': np.arange(120), 'probs': general, 'kind': 'general'},
              name: {'indices': np.arange(120), 'probs': auxiliary, 'kind': 'filegroup'}}
    config = {'levels': [{'level': 25, 'hostile': {'target_per_million': .25}}]}
    state = {'routes': routes, 'labels': labels, 'file_types': np.array(['x']*120),
             'filetype_to_group': {}, 'config': config, 'total_benign': 60}
    monkeypatch.setattr(_mod, '_SHARED', state)
    _, baseline = _mod._process_filetype('x')
    config['global_auxiliary_routes'] = [name]
    _, augmented = _mod._process_filetype('x')
    baseline_hit = _mod.policy.swept_margin({'general': general}, baseline['levels'],25,120) >= 0
    augmented_hit = _mod.policy.swept_margin({'general': general,name:auxiliary}, augmented['levels'],25,120) >= 0
    assert baseline['models'] == ['general']
    assert name in augmented['models']
    assert (baseline_hit & (labels == 1)).sum() == 30
    assert (augmented_hit & (labels == 1)).sum() == 60
    assert (augmented_hit & (labels == 0)).sum() <= (baseline_hit & (labels == 0)).sum()


def test_auxiliary_preserves_existing_policy_choices(monkeypatch):
    import json

    rng = np.random.default_rng(12)
    labels = np.r_[np.zeros(80), np.ones(80)].astype(np.int8)
    names = ['general', 'filegroups/base', 'filetypes/x', 'filegroups/alternative']
    routes = {name: {'indices': np.arange(160),
                     'probs': rng.uniform(.05, .95, 160).astype(np.float32),
                     'kind': 'general' if name == 'general' else 'filegroup' if 'filegroups' in name else 'filetype'}
              for name in names}
    config = {'levels': [{'level': 25, 'hostile': {'target_per_million': .25}}]}
    monkeypatch.setattr(_mod, '_SHARED', {
        'routes': routes, 'labels': labels, 'file_types': np.array(['x'] * 160),
        'filetype_to_group': {'x': 'base'}, 'config': config, 'total_benign': 80})
    _, baseline = _mod._process_filetype('x')
    config['global_auxiliary_routes'] = [names[-1]]
    _, augmented = _mod._process_filetype('x')

    def choices(result):
        return {json.dumps({key: item.get(key) for key in
                           ('policy', 'allowed_routes', 'thresholds', 'blend')}, sort_keys=True)
                for item in result['levels'][0]['hostile']['candidates']}

    assert choices(baseline) <= choices(augmented)
    assert augmented['levels'][0]['hostile']['best']['tp'] >= baseline['levels'][0]['hostile']['best']['tp']

    # A scoped alternative must preserve the global-auxiliary families too,
    # and leave unrelated filetypes' choices unchanged.
    scoped_name = 'filegroups/scoped_previous'
    routes[scoped_name] = {**routes[names[-1]], 'probs': rng.uniform(.05, .95, 160).astype(np.float32)}
    config['filetype_auxiliary_routes'] = {'unrelated': [scoped_name]}
    _, unrelated = _mod._process_filetype('x')
    assert choices(unrelated) == choices(augmented)
    assert scoped_name not in unrelated['models']
    config['filetype_auxiliary_routes']['x'] = [scoped_name]
    _, scoped = _mod._process_filetype('x')
    assert choices(augmented) <= choices(scoped)
    assert scoped_name in scoped['models']
    assert scoped['levels'][0]['hostile']['best']['tp'] >= augmented['levels'][0]['hostile']['best']['tp']


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


def _tail_blend_fixture():
    rng = np.random.default_rng(71)
    labels = np.r_[np.zeros(500), np.ones(150)].astype(np.int8)
    logits = np.column_stack([
        rng.normal(labels * 3 - 2, 1.3), rng.normal(labels * 2 - 1, 1.2),
    ])
    # A rare benign tail makes overall classification loss a different
    # objective from ranking at a very small false-positive allowance.
    logits[:10, 0] = 3
    return {name: (1 / (1 + np.exp(-logits[:, i]))).astype(np.float32)
            for i, name in enumerate(('general', 'filetypes/x'))}, labels


def test_tail_blend_is_additive_scoped_and_respects_swept_budget(monkeypatch):
    import json

    probs, labels = _tail_blend_fixture()
    config = {'levels': [{'level': level, 'hostile': {'target_per_million': level / 100}}
                         for level in (0, 1, 25)]}
    monkeypatch.setattr(_mod, '_SHARED', {
        'routes': {name: {'indices': np.arange(len(labels)), 'probs': p,
                          'kind': 'general' if name == 'general' else 'filetype'}
                   for name, p in probs.items()},
        'labels': labels, 'file_types': np.array(['x'] * len(labels)),
        'filetype_to_group': {}, 'config': config, 'total_benign': 500})
    _, baseline = _mod._process_filetype('x')
    options = {'weight': 50, 'fraction': .02}
    config['tail_weighted_blends'] = {'other': options}
    assert _mod._process_filetype('x')[1] == baseline
    config['tail_weighted_blends'] = {'x': options}
    _, weighted = _mod._process_filetype('x')
    for before, after in zip(baseline['levels'], weighted['levels'], strict=True):
        def choices(row):
            return {json.dumps({key: c.get(key) for key in ('policy', 'thresholds', 'blend')},
                               sort_keys=True) for c in row['hostile']['candidates']}
        assert choices(before) <= choices(after)
        assert any(c['policy'].startswith('tail_weighted_50_')
                   for c in after['hostile']['candidates'])
        hit = _mod.policy.swept_margin(probs, weighted['levels'], after['level'], len(labels)) >= 0
        assert int((hit & (labels == 0)).sum()) <= after['hostile']['budget']
    config['tail_weighted_blends']['x']['fraction'] = float('nan')
    with pytest.raises(ValueError, match='tail_weighted_blends'):
        _mod._process_filetype('x')


def test_tail_blend_preserves_runtime_score_contract_and_identity_weight():
    probs, labels = _tail_blend_fixture()
    routes = tuple(probs)
    control = _mod._fit_learned_blend(probs, labels, routes)
    identity = _mod._fit_tail_weighted_blend(probs, labels, routes, weight=1)
    weighted = _mod._fit_tail_weighted_blend(probs, labels, routes, weight=50)
    assert control is not None and identity is not None and weighted is not None
    np.testing.assert_array_equal(control['blend_score'], identity['blend_score'])
    assert not np.array_equal(control['blend_score'], weighted['blend_score'])
    assert np.all(weighted['weights'] >= -_mod._BLEND_MIN_WEIGHT)
    decision = {'blend': {'routes': weighted['present_routes'], 'weights': weighted['weights'],
                         'intercept': weighted['intercept'], 'threshold': 0., 'transform': 'logit'}}
    np.testing.assert_array_equal(weighted['blend_score'], _mod.policy.margin(probs, decision, len(labels)))
    with pytest.raises(ValueError, match='sample weights'):
        _mod._fit_learned_blend(probs, labels, routes, sample_weight=np.ones(2))
    for weight, fraction in [(0, .02), (float('inf'), .02), (50, 0), (50, 1.1)]:
        with pytest.raises(ValueError, match='tail blend'):
            _mod._fit_tail_weighted_blend(probs, labels, routes, weight=weight, fraction=fraction)


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
