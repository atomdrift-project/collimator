#!/usr/bin/env python3
"""EXP-8b — EXP-8 with the extreme slope fitted over the deepest decade."""
from __future__ import annotations

from .exp8_fpanchor import FPAnchorCurve


class FPAnchor10Curve(FPAnchorCurve):
    method = "exp8b_fpanchor10"


def fit(logit_benign, route_meta, context=None):  # noqa: ARG001
    return FPAnchor10Curve(route_meta, logit_benign, span=10)
