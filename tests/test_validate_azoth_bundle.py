"""Tests for the fast-fail structural gates in validate_azoth_bundle.

These run locally before the litmus build + Rust scan, so a corrupt bundle
fails in ~1s instead of minutes into the deploy gate. The load-bearing case is
``_blend_errors``: a learned blend's ``routes`` are paired positionally with a
float ``weights`` vector, and a route-pruner or writer that desyncs them
produces the ``blend routes/weights length mismatch`` the deployed Rust loader
rejects at scan time.
"""

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))
_SCRIPT = _ROOT / "scripts" / "validate_azoth_bundle.py"
_spec = importlib.util.spec_from_file_location("validate_azoth_bundle", _SCRIPT)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
_blend_errors = _mod._blend_errors


def _policy_with_blend(blend):
    return {
        "routes": {
            "filetypes/crx": {
                "levels": [{"level": 3, "hostile": {"best": {"blend": blend}}}]
            }
        }
    }


def _blend(routes, weights):
    return {"routes": list(routes), "weights": list(weights),
            "intercept": 0.97, "transform": "logit", "threshold": 0.48}


def test_aligned_blend_passes():
    policy = _policy_with_blend(_blend(["general", "filetypes/crx"], [0.27, 1.83]))
    assert _blend_errors(policy) == []


def test_misaligned_blend_flagged():
    policy = _policy_with_blend(_blend(["general"], [0.27, 1.83]))
    errors = _blend_errors(policy)
    assert len(errors) == 1
    assert "routes/weights length mismatch" in errors[0]
    assert "1 routes vs 2 weights" in errors[0]


def test_empty_routes_flagged():
    policy = _policy_with_blend(_blend([], []))
    errors = _blend_errors(policy)
    assert len(errors) == 1
    assert "no routes" in errors[0]


def test_blend_in_candidates_list_is_walked():
    # Blends also live under levels[].hostile.candidates[]; the walk must reach
    # list-nested blends, not just the chosen best.
    policy = {
        "routes": {
            "filetypes/crx": {
                "levels": [{
                    "level": 3,
                    "hostile": {"candidates": [
                        {"blend": _blend(["general", "filetypes/crx"], [0.1, 0.2])},
                        {"blend": _blend(["general"], [0.1, 0.2])},
                    ]},
                }]
            }
        }
    }
    errors = _blend_errors(policy)
    assert len(errors) == 1
    assert "candidates[1]/blend" in errors[0]


def test_no_blends_no_errors():
    policy = {"routes": {"filetypes/crx": {"levels": [
        {"level": 3, "hostile": {"best": {"thresholds": {"general": 0.9}}}}
    ]}}}
    assert _blend_errors(policy) == []
