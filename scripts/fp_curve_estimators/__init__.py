#!/usr/bin/env python3
"""FP-curve estimators (FP_CURVE_PROPOSAL.md).

Each module exposes the proposal's common API::

    fit(logit_benign, route_meta, context) -> CurveModel
    CurveModel.threshold(level)  -> float    # logit space, continuous
    CurveModel.band(level, q)    -> (lo, hi)
    CurveModel.to_grid(levels)   -> list[dict]

Registry lookups are lazy so a run that only needs B0 and EXP-1 does not pay
for the heavier estimators' imports.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from typing import Any

_MODULES: dict[str, str] = {
    "b0": "b0",
    "exp1": "exp1_smooth_interp",
    "exp2": "exp2_logit_gpd",
    "exp3": "exp3_pooled_tail",
    "exp3b": "exp3b_anchored_tail",
    "exp3c": "exp3c_calibrated_tail",
    "exp4": "exp4_boosted_tail",
    "exp5": "exp5_ladder_learned",
    "exp6": "exp6_median_ensemble",
    "exp7": "exp7_loglinear",
    "exp7b": "exp7b_curved",
    "exp8": "exp8_fpanchor",
    "exp8b": "exp8b_fpanchor10",
}

# Estimators that consume cross-route context (leave-route-out applies).
POOLED: frozenset[str] = frozenset({"exp3", "exp3b", "exp3c", "exp4", "exp5", "exp6", "exp7", "exp7b"})


def estimator_names() -> list[str]:
    return list(_MODULES)


def get_fit(name: str) -> Callable[..., Any]:
    if name not in _MODULES:
        raise KeyError(f"unknown estimator {name!r}; known: {sorted(_MODULES)}")
    module = importlib.import_module(f"{__name__}.{_MODULES[name]}")
    return module.fit
