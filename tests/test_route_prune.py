"""Tests for dropping weak/parity-failed specialist routes from a bundle.

The load-bearing case is the learned *blend* policy: ``routes`` names are paired
positionally with a float ``weights`` vector. The generic member-scrub only
matches string members, so a naive scrub strips a dropped route's name out of
``routes`` while leaving its weight in ``weights`` — producing the
``len(weights) == len(routes) + 1`` corruption that makes litmus reject the
deployed bundle (``blend routes/weights length mismatch``). These tests pin the
lockstep prune that keeps the two arrays aligned through nightly route churn.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))

from collimator.route_prune import _prune_route_policies, _scrub_members  # noqa: E402


def _blend(routes, weights):
    return {
        "routes": list(routes),
        "weights": list(weights),
        "intercept": 0.97,
        "transform": "logit",
        "threshold": 0.48,
    }


def test_scrub_prunes_blend_route_and_weight_in_lockstep():
    blend = _blend(["general", "filetypes/crx"], [0.270, 1.825])
    _scrub_members(blend, frozenset({"filetypes/crx"}))
    assert blend["routes"] == ["general"]
    assert blend["weights"] == [0.270]
    assert len(blend["routes"]) == len(blend["weights"])


def test_scrub_drops_correct_index_not_just_last():
    # Dropping the *first* non-protected route must remove weights[1], not a
    # blanket pop of the tail.
    blend = _blend(["general", "filetypes/a", "filetypes/b"], [0.1, 0.2, 0.3])
    _scrub_members(blend, frozenset({"filetypes/a"}))
    assert blend["routes"] == ["general", "filetypes/b"]
    assert blend["weights"] == [0.1, 0.3]


def test_scrub_leaves_unaffected_blend_untouched():
    blend = _blend(["general", "filetypes/crx"], [0.270, 1.825])
    _scrub_members(blend, frozenset({"filetypes/unrelated"}))
    assert blend == _blend(["general", "filetypes/crx"], [0.270, 1.825])


def test_scrub_skips_malformed_blend_rather_than_worsening_it():
    # An already-mismatched blend isn't realignable by name; leave it as-is for
    # the loader to reject, don't silently drop more.
    blend = _blend(["general"], [0.1, 0.2])
    _scrub_members(blend, frozenset({"filetypes/crx"}))
    assert blend["routes"] == ["general"]
    assert blend["weights"] == [0.1, 0.2]


def test_prune_route_policies_keeps_blend_arrays_aligned():
    # End-to-end through the policy-body scrubber: a dropped specialist appears
    # as a blend member, a threshold-map key, and an allowed_routes entry.
    policy = {
        "routes": {
            "filetypes/crx": {
                "filetype": "crx",
                "levels": [
                    {
                        "level": 3,
                        "hostile": {
                            "best": {
                                "policy": "learned_blend_at_fp_3",
                                "primary": None,
                                "allowed_routes": ["general", "filetypes/crx"],
                                "thresholds": {},
                                "blend": _blend(
                                    ["general", "filetypes/crx"], [0.270, 1.825]
                                ),
                            }
                        },
                    }
                ],
            }
        }
    }
    _prune_route_policies(policy, frozenset({"filetypes/crx"}))
    best = policy["routes"]["filetypes/crx"]["levels"][0]["hostile"]["best"]
    blend = best["blend"]
    assert blend["routes"] == ["general"]
    assert blend["weights"] == [0.270]
    assert best["allowed_routes"] == ["general"]


def test_blend_losing_all_routes_is_removed():
    best = {
        "policy": "learned_blend_at_fp_3",
        "blend": _blend(["filetypes/a", "filetypes/b"], [0.5, 0.5]),
    }
    _scrub_members(best, frozenset({"filetypes/a", "filetypes/b"}))
    assert "blend" not in best
