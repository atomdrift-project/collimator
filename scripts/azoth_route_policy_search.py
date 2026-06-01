#!/usr/bin/env python3
"""Search route-owned azoth policies from a persisted score table."""

from __future__ import annotations

import argparse
import csv
import json
import math
import multiprocessing as mp
import os
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp

from azoth_calibrate_ensemble import (
    _budget,
    _clopper_pearson_fp_per_million_upper,
    _max_dev_fp_for_target,
    _quantile_severity_threshold,
)
from collimator import bundle, features, model


def _json_clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_clean(v) for v in value]
    if isinstance(value, tuple):
        return [_json_clean(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, np.floating):
        f = float(value)
        return None if not math.isfinite(f) else f
    if isinstance(value, np.integer):
        return int(value)
    return value


def _route_arrays(score_table: np.lib.npyio.NpzFile) -> dict[str, dict[str, Any]]:
    names = [str(name) for name in score_table["route_names"]]
    kinds = [str(kind) for kind in score_table["route_kinds"]]
    scores = score_table["scores"]
    out: dict[str, dict[str, Any]] = {}
    for idx, name in enumerate(names):
        dense_probs = scores[idx].astype(np.float32, copy=False)
        probs = dense_probs
        present = ~np.isnan(probs)
        out[name] = {
            "kind": kinds[idx],
            "indices": np.flatnonzero(present).astype(np.int64),
            "probs": probs[present].astype(np.float32),
            "dense_probs": dense_probs,
        }
    return out


def _dense_route_probs(
    routes: dict[str, dict[str, Any]],
    route_name: str,
    global_indices: np.ndarray,
) -> np.ndarray | None:
    route = routes.get(route_name)
    if route is None:
        return None
    dense_probs = route.get("dense_probs")
    if dense_probs is not None:
        out = dense_probs[global_indices].astype(np.float32, copy=False)
        if np.all(np.isnan(out)):
            return None
        return out
    local_by_global = {int(idx): pos for pos, idx in enumerate(route["indices"])}
    out = np.full(len(global_indices), np.nan, dtype=np.float32)
    for pos, global_idx in enumerate(global_indices):
        route_pos = local_by_global.get(int(global_idx))
        if route_pos is not None:
            out[pos] = route["probs"][route_pos]
    if np.all(np.isnan(out)):
        return None
    return out


def _metrics(
    labels: np.ndarray,
    hit: np.ndarray,
    *,
    target_per_million: float,
    total_benign: int,
    thresholds: dict[str, float],
    policy: str,
    primary: str | None,
    allowed_routes: tuple[str, ...],
) -> dict[str, Any]:
    benign = labels == 0
    malware = labels == 1
    tp = int(np.sum(hit & malware))
    fp = int(np.sum(hit & benign))
    tn = int(np.sum((~hit) & benign))
    fn = int(np.sum((~hit) & malware))
    n_malware = int(np.sum(malware))
    n_benign = int(np.sum(benign))
    precision = tp / max(tp + fp, 1)
    recall = tp / n_malware if n_malware else math.nan
    fpr = fp / n_benign if n_benign else math.nan
    f1 = 2 * precision * recall / max(precision + recall, 1e-12) if n_malware else math.nan
    accuracy = (tp + tn) / max(tp + fp + tn + fn, 1)
    return {
        "policy": policy,
        "primary": primary,
        "allowed_routes": list(allowed_routes),
        "target_per_million": float(target_per_million),
        "thresholds": thresholds,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "accuracy": accuracy,
        "fpr": fpr,
        "fp_per_100M": fp * 100_000_000.0 / n_benign if n_benign else math.nan,
        "global_fp_per_million": fp * 1_000_000.0 / total_benign if total_benign else math.nan,
    }


def _calibrate_policy(
    labels: np.ndarray,
    route_probs: dict[str, np.ndarray],
    *,
    policy: str,
    primary: str | None,
    allowed_routes: tuple[str, ...],
    target_per_million: float,
    total_benign: int,
) -> dict[str, Any]:
    present_routes = tuple(
        route for route in allowed_routes if route in route_probs and not np.all(np.isnan(route_probs[route]))
    )
    if not present_routes:
        return _metrics(
            labels,
            np.zeros(len(labels), dtype=bool),
            target_per_million=target_per_million,
            total_benign=total_benign,
            thresholds={},
            policy=policy,
            primary=primary,
            allowed_routes=(),
        )
    if primary not in present_routes:
        primary = present_routes[0] if primary is not None else None

    # Per-route severity-tier thresholds: each participating route's
    # threshold at this filetype's local FP/M target is the (1 − q×10⁻⁶)
    # quantile of that route's benign scores within the filetype slice.
    # Below the empirical floor we extrapolate via GPD on the benign upper
    # tail (see _quantile_severity_threshold). No coordinate-descent
    # search — each route's threshold is independent; the policy
    # comparison happens in _choose_best on the resulting OR-rule metrics.
    n_benign = int(np.sum(labels == 0))
    _, below_resolution = _max_dev_fp_for_target(
        target_per_million, n_benign, alpha=0.05,
    ) if n_benign > 0 else (0, True)

    n_rows = len(labels)
    union_hit = np.zeros(n_rows, dtype=bool)
    selected: dict[str, float | None] = {route_name: None for route_name in present_routes}
    extrapolated: list[str] = []

    for route_name in present_routes:
        probs = route_probs[route_name]
        valid = ~np.isnan(probs)
        route_benign_mask = valid & (labels == 0)
        benign_probs = probs[route_benign_mask].astype(np.float64)
        if len(benign_probs) < 50:
            # Below the resolution floor — leave inactive (sentinel 1.0
            # below). Documented presence preserves litmus's
            # contains_route check.
            continue
        threshold, method = _quantile_severity_threshold(benign_probs, target_per_million)
        if threshold is None:
            continue
        if method == "extrapolated":
            extrapolated.append(route_name)
        selected[route_name] = float(threshold)
        union_hit |= (probs >= threshold) & valid

    # Include EVERY present_route in thresholds_out — with a no-fire
    # sentinel (1.0) for any route whose threshold was None. Litmus's
    # contains_route check (model.rs:824) tests for route presence in
    # route_policies as the signal that the route's specialist should be
    # loaded; sentinel 1.0 means "score ≥ 1.0 fires" which is unreachable
    # for calibrated probabilities, so the route formally exists in the
    # policy but is operationally a no-op until later calibration moves it.
    thresholds_out: dict[str, float] = {}
    for route_name in present_routes:
        sel = selected.get(route_name)
        thresholds_out[route_name] = float(sel) if sel is not None else 1.0

    out = _metrics(
        labels,
        union_hit,
        target_per_million=target_per_million,
        total_benign=total_benign,
        thresholds=thresholds_out,
        policy=policy,
        primary=primary,
        allowed_routes=present_routes,
    )
    out["below_resolution"] = bool(below_resolution)
    out["cp_floor_per_million"] = (
        float(_clopper_pearson_fp_per_million_upper(0, n_benign, alpha=0.05))
        if n_benign > 0
        else None
    )
    if extrapolated:
        out["extrapolated_routes"] = list(extrapolated)
    return out


def _policy_candidates(
    *,
    general: str,
    group: str | None,
    filetype: str | None,
) -> list[tuple[str, str | None, tuple[str, ...]]]:
    routes = tuple(route for route in (general, group, filetype) if route)
    out: list[tuple[str, str | None, tuple[str, ...]]] = [
        ("general_only", general, (general,)),
        ("or_general_primary", general, routes),
    ]
    if group:
        out.append(("group_only", group, (group,)))
        out.append(("group_primary_with_escape", group, routes))
    if filetype:
        out.append(("filetype_only", filetype, (filetype,)))
        out.append(("specialist_primary_with_escape", filetype, routes))
    return out


def _joint_or_search(
    route_probs: dict[str, np.ndarray],
    labels: np.ndarray,
    routes: tuple[str, ...],
    *,
    fp_budget: int,
    max_iters: int = 8,
) -> tuple[dict[str, float], np.ndarray]:
    """Coordinate descent on per-route thresholds for an OR-rule policy
    constrained to ``fp_budget`` total FPs in the slice.

    Each round, hold all-but-one route fixed and solve a 1-D problem:
    given the OR-hit from the other routes, find the loosest threshold
    for this route whose newly-added rows keep total FP ≤ budget. This is
    exactly the per-route Pareto-at-FP problem on rows not already hit by
    others — closed-form, no learning, no gradient framework needed.

    Repeat until thresholds stop moving (typically 2-3 rounds). The result
    OR-rule fires at exactly the union of per-route firings under their
    final thresholds, never overspending the FP budget.

    Why not "gradient descent": the objective (TP@FP≤K) is piecewise-
    constant in each threshold, so gradients are 0 almost everywhere.
    Coordinate descent on the 1-D Pareto frontiers is the right shape.

    Returns ``(thresholds, union_hit)``.
    """
    n = len(labels)
    thresholds: dict[str, float] = {route: 1.0 for route in routes}
    if fp_budget < 0:
        return thresholds, np.zeros(n, dtype=bool)
    # Initial seed: each route's solo-Pareto threshold at the full budget.
    # Coordinate descent then redistributes budget across routes.
    for route in routes:
        probs = route_probs[route]
        threshold, _, _ = _specialist_threshold_for_fp(probs, labels, fp_budget)
        thresholds[route] = float(threshold) if threshold is not None else 1.0

    def _hit_union(except_route: str | None = None) -> np.ndarray:
        out = np.zeros(n, dtype=bool)
        for r, t in thresholds.items():
            if r == except_route or t >= 1.0:
                continue
            probs = route_probs[r]
            valid = ~np.isnan(probs)
            out |= valid & (probs >= t)
        return out

    benign = labels == 0
    for _ in range(max_iters):
        changed = False
        for route in routes:
            other_hit = _hit_union(except_route=route)
            other_fp = int(np.sum(other_hit & benign))
            remaining = fp_budget - other_fp
            if remaining < 0:
                # Other routes already exhaust the budget; turn this one off.
                if thresholds[route] < 1.0:
                    thresholds[route] = 1.0
                    changed = True
                continue
            probs = route_probs[route]
            valid = ~np.isnan(probs)
            mask = valid & ~other_hit
            if not mask.any():
                if thresholds[route] < 1.0:
                    thresholds[route] = 1.0
                    changed = True
                continue
            p = probs[mask].astype(np.float64)
            y = labels[mask].astype(np.int8)
            if int((y == 1).sum()) == 0:
                if thresholds[route] < 1.0:
                    thresholds[route] = 1.0
                    changed = True
                continue
            order = np.lexsort((y, -p))
            p_sorted = p[order]
            y_sorted = y[order]
            fp_cum = np.cumsum(y_sorted == 0)
            eligible = np.flatnonzero(fp_cum <= remaining)
            if len(eligible) == 0:
                new_t = 1.0
            else:
                end = int(eligible[-1])
                new_t = float(p_sorted[end])
            if abs(thresholds[route] - new_t) > 1e-12:
                thresholds[route] = new_t
                changed = True
        if not changed:
            break

    return thresholds, _hit_union()


_LEARNED_BLEND_LOGIT_EPS = 1e-6


@lru_cache(maxsize=None)
def _load_route_calibrator(
    azoth_root: Path, route_name: str,
) -> tuple[np.ndarray, np.ndarray] | None:
    """Load a route's isotonic calibrator breakpoints.

    Returns ``(x, y)`` arrays (raw_prob, calibrated_prob) or None if the
    route isn't calibrated yet — pre-calibrator bundles and routes that
    failed calibration won't have the file. Schema is
    ``azoth.calibrator.isotonic.v1`` (see
    azoth_calibrate_ensemble._fit_and_persist_isotonic_calibrator).

    Cached across calls: the bundle has at most ~50 routes and the file
    is a few KB each. Saves ~3× redundant disk reads when called from
    the per-filetype loop.
    """
    if route_name == "general":
        path = azoth_root / "general" / "calibrator.json"
    elif route_name.startswith("filegroups/"):
        path = azoth_root / route_name / "calibrator.json"
    elif route_name.startswith("filetypes/"):
        path = azoth_root / route_name / "calibrator.json"
    else:
        return None
    if not path.is_file():
        return None
    with open(path) as f:
        cal = json.load(f)
    x = np.asarray(cal["x"], dtype=np.float64)
    y = np.asarray(cal["y"], dtype=np.float64)
    if len(x) < 2 or len(x) != len(y):
        return None
    return (x, y)


def _apply_isotonic(
    probs: np.ndarray, breakpoints: tuple[np.ndarray, np.ndarray],
) -> np.ndarray:
    """Linear-interpolate raw probs through isotonic breakpoints with
    clip-out-of-bounds semantics, matching litmus's deploy behavior
    (litmus/src/model.rs:1437 calls cal.apply, which is clip+lerp).

    NaN inputs pass through as NaN — calibration only applies where the
    route emitted a real score.
    """
    x_breaks, y_breaks = breakpoints
    out = np.full_like(probs, np.nan, dtype=np.float32)
    valid = ~np.isnan(probs)
    if not np.any(valid):
        return out
    # np.interp clamps outside the input domain to the boundary y-values,
    # which is exactly the "clip" out-of-bounds policy the calibrator
    # file declares. Cast through float64 for numerical stability with
    # tight raw-prob distributions, then back to float32 to match the
    # score table's storage type.
    raw = probs[valid].astype(np.float64)
    cal = np.interp(raw, x_breaks, y_breaks)
    out[valid] = cal.astype(np.float32)
    return out


def _build_calibrated_route_probs(
    raw_route_probs: dict[str, np.ndarray],
    azoth_root: Path,
) -> dict[str, np.ndarray]:
    """Apply each route's isotonic calibrator to its raw probabilities,
    so the learned-blend fit operates in the same prob space litmus
    emits at deploy.

    Routes without a calibrator pass through unchanged with a warning —
    the blend will then be slightly inconsistent for that route, but
    that's preferable to dropping the route entirely. (Pre-calibrator
    bundles are vanishingly rare in this pipeline now; the warning
    surfaces them if they appear.)
    """
    out: dict[str, np.ndarray] = {}
    missing: list[str] = []
    for route_name, probs in raw_route_probs.items():
        bps = _load_route_calibrator(azoth_root, route_name)
        if bps is None:
            missing.append(route_name)
            out[route_name] = probs
            continue
        out[route_name] = _apply_isotonic(probs, bps)
    if missing:
        # Logged at info level rather than warning because deploy still
        # works; the blend just won't be deploy-accurate for these routes.
        print(
            f"# learned_blend: {len(missing)} route(s) without isotonic "
            f"calibrators; passing raw probs through: {missing}",
        )
    return out


def _logit_stack(
    route_probs: dict[str, np.ndarray],
    routes: tuple[str, ...],
) -> tuple[np.ndarray, np.ndarray, tuple[str, ...]]:
    """Stack per-route logits for the learned-blend candidate.

    Returns ``(stacked_logits, valid_row_mask, present_routes)``. Routes
    that are entirely NaN over the slice get dropped. ``valid_row_mask``
    is True where every retained route has a non-NaN prob — LR can't
    accept NaN inputs, and a row missing any route's score must use
    fallback semantics at deploy too.
    """
    cols: list[np.ndarray] = []
    present: list[str] = []
    for route in routes:
        probs = route_probs.get(route)
        if probs is None or np.all(np.isnan(probs)):
            continue
        p = np.clip(
            probs.astype(np.float64),
            _LEARNED_BLEND_LOGIT_EPS,
            1.0 - _LEARNED_BLEND_LOGIT_EPS,
        )
        with np.errstate(divide="ignore"):
            cols.append(np.log(p / (1.0 - p)))
        present.append(route)
    if not cols:
        return (
            np.empty((len(next(iter(route_probs.values()))), 0), dtype=np.float64),
            np.zeros(len(next(iter(route_probs.values()))), dtype=bool),
            tuple(),
        )
    stacked = np.stack(cols, axis=1)
    # A row is valid if no retained route has NaN; the logit clip above
    # only handles in-range probs, NaN passes through to the stack.
    valid = ~np.any(np.isnan(stacked), axis=1)
    return stacked, valid, tuple(present)


def _fit_learned_blend(
    route_probs: dict[str, np.ndarray],
    labels: np.ndarray,
    routes: tuple[str, ...],
) -> dict[str, Any] | None:
    """Fit a logistic regression over logit-stacked route probabilities.

    Returns a dict with the fitted blend (``weights``, ``intercept``,
    ``present_routes``) plus the precomputed per-row blend score and
    valid-row mask. The blend score is the same regardless of operating
    point, so this is the work to hoist out of the per-level loop —
    only the per-fp threshold step varies (see
    ``_blend_candidate_from_fit``).

    Returns None when there are fewer than two routes with finite
    probabilities or fewer than 5 rows per class to fit on.

    Why LR-on-logits rather than LR-on-probs: probabilities pile up near
    0 and 1 for confident specialist scores, and a linear-in-prob model
    is forced to throw most of its weight at the [0,1] interior. Working
    in logit space lets the LR linearly combine evidence in log-odds —
    the natural language of stacking probabilistic classifiers.
    """
    if len(routes) < 2:
        return None
    try:
        from sklearn.linear_model import LogisticRegression  # noqa: PLC0415
    except ImportError:
        return None
    stacked, valid_row, present_routes = _logit_stack(route_probs, routes)
    if len(present_routes) < 2:
        return None
    fit_mask = valid_row
    n_mal_fit = int(((labels == 1) & fit_mask).sum())
    n_ben_fit = int(((labels == 0) & fit_mask).sum())
    # LR needs at least one row per class; below this we'd be fitting on
    # near-singleton data and the resulting weights aren't trustworthy.
    if n_mal_fit < 5 or n_ben_fit < 5:
        return None
    x_fit = stacked[fit_mask]
    y_fit = labels[fit_mask].astype(np.int8)
    # class_weight='balanced' counteracts the corpus's benign skew so the
    # loss doesn't get dominated by easy benigns. L2 with C=1 is mild —
    # with only len(present_routes) features we're nowhere near overfit
    # territory at typical slice sizes.
    clf = LogisticRegression(
        C=1.0, class_weight="balanced", solver="liblinear", max_iter=200,
    ).fit(x_fit, y_fit)
    weights = clf.coef_[0].astype(np.float64)
    intercept = float(clf.intercept_[0])
    # Apply the blend to every valid slice row, NaN otherwise.
    z = stacked @ weights + intercept
    blend = np.full(len(labels), np.nan, dtype=np.float64)
    blend[valid_row] = 1.0 / (1.0 + np.exp(-z[valid_row]))
    return {
        "blend_score": blend,
        "valid_row": valid_row,
        "present_routes": present_routes,
        "weights": weights,
        "intercept": intercept,
    }


def _blend_candidate_from_fit(
    fit: dict[str, Any],
    labels: np.ndarray,
    *,
    fp_target: int,
    target_per_million: float,
    total_benign: int,
) -> dict[str, Any] | None:
    """Tune the threshold on a precomputed blend fit at ``fp_target``
    false-positives in the slice and emit a candidate. The blend's
    ``thresholds`` stays empty (OR-rule semantics don't apply); the
    ``blend`` field carries the fit metadata litmus consumes.
    """
    blend = fit["blend_score"]
    valid_row = fit["valid_row"]
    present_routes = fit["present_routes"]
    weights = fit["weights"]
    intercept = fit["intercept"]
    threshold, _, _ = _specialist_threshold_for_fp(
        blend.astype(np.float32),
        labels,
        fp_target,
    )
    if threshold is None:
        return None
    valid = ~np.isnan(blend)
    hit = valid & (blend >= threshold)
    if not np.any(hit):
        return None
    candidate = _metrics(
        labels,
        hit,
        target_per_million=target_per_million,
        total_benign=total_benign,
        thresholds={},
        policy=f"learned_blend_at_fp_{fp_target}",
        primary=None,
        allowed_routes=present_routes,
    )
    candidate["blend"] = {
        "routes": list(present_routes),
        "weights": [float(w) for w in weights],
        "intercept": intercept,
        "transform": "logit",
        "threshold": float(threshold),
    }
    return candidate


def _make_learned_blend_candidate_at_fp(
    *,
    route_probs: dict[str, np.ndarray],
    labels: np.ndarray,
    routes: tuple[str, ...],
    fp_target: int,
    target_per_million: float,
    total_benign: int,
) -> dict[str, Any] | None:
    """Back-compat wrapper: fit + threshold in one call. Prefer
    ``_fit_learned_blend`` + ``_blend_candidate_from_fit`` when the fit
    can be hoisted out of a per-fp loop (which is most of policy_search).
    """
    fit = _fit_learned_blend(route_probs, labels, routes)
    if fit is None:
        return None
    return _blend_candidate_from_fit(
        fit, labels,
        fp_target=fp_target,
        target_per_million=target_per_million,
        total_benign=total_benign,
    )


def _make_joint_or_candidate_at_fp(
    *,
    route_probs: dict[str, np.ndarray],
    labels: np.ndarray,
    routes: tuple[str, ...],
    fp_target: int,
    target_per_million: float,
    total_benign: int,
) -> dict[str, Any] | None:
    """Build an OR-rule candidate whose per-route thresholds are
    jointly tuned to spend at most ``fp_target`` FPs in the slice.

    Returns None when the routes can't be made to fire at all within
    the budget (e.g., budget=0 and every benign sits at the top of every
    route's score distribution).
    """
    if len(routes) < 2:
        return None
    thresholds, hit = _joint_or_search(
        route_probs, labels, routes, fp_budget=fp_target,
    )
    if not np.any(hit):
        return None
    thresholds_out = {r: t for r, t in thresholds.items() if t < 1.0}
    if not thresholds_out:
        return None
    return _metrics(
        labels,
        hit,
        target_per_million=target_per_million,
        total_benign=total_benign,
        thresholds=thresholds_out,
        policy=f"joint_or_at_fp_{fp_target}",
        primary=None,
        allowed_routes=tuple(thresholds_out.keys()),
    )


def _calibrate_max_rule_policy(
    labels: np.ndarray,
    route_probs: dict[str, np.ndarray],
    *,
    allowed_routes: tuple[str, ...],
    target_per_million: float,
    total_benign: int,
) -> dict[str, Any]:
    """Continuous max-rule ensemble: threshold ``max(p_route)`` across the
    given routes, at a uniform value calibrated to the slice FP target.

    Unlike ``or_general_primary`` and friends — which OR per-route binary
    fires with INDEPENDENTLY calibrated thresholds and can spend up to
    N×target FP in the worst case — max-rule with a single uniform
    threshold spends at most the target FP itself. Mathematically:
    ``max(p_route) >= T ⟺ any p_route >= T``, so uniform-T OR-of-routes
    is identical to max-rule.

    Litmus's ``policy_classify`` (model.rs:1499) already evaluates
    ``any(score.prob >= policy.thresholds[route])``, which matches this
    semantics when every route in ``thresholds`` carries the same value.
    No deploy-side change is needed.
    """
    present_routes = tuple(
        route for route in allowed_routes
        if route in route_probs and not np.all(np.isnan(route_probs[route]))
    )
    if len(present_routes) < 2:
        # Degenerate to a single route — already covered by general_only /
        # group_only / filetype_only; don't pollute the candidate set.
        return _no_hit_candidate(
            labels, target_per_million=target_per_million, total_benign=total_benign,
        )

    stack = np.stack([route_probs[route] for route in present_routes], axis=0)
    with np.errstate(invalid="ignore"):
        max_probs = np.nanmax(stack, axis=0).astype(np.float32)
    all_nan = np.all(np.isnan(stack), axis=0)
    max_probs[all_nan] = np.nan

    valid = ~np.isnan(max_probs)
    benign_mask = valid & (labels == 0)
    benign_probs = max_probs[benign_mask].astype(np.float64)
    if len(benign_probs) < 50:
        out = _no_hit_candidate(
            labels, target_per_million=target_per_million, total_benign=total_benign,
        )
        out["policy"] = "max_rule"
        out["allowed_routes"] = list(present_routes)
        return out
    threshold, method = _quantile_severity_threshold(benign_probs, target_per_million)
    if threshold is None:
        out = _no_hit_candidate(
            labels, target_per_million=target_per_million, total_benign=total_benign,
        )
        out["policy"] = "max_rule"
        out["allowed_routes"] = list(present_routes)
        return out
    hit = valid & (max_probs >= threshold)
    thresholds_out = {route: float(threshold) for route in present_routes}
    out = _metrics(
        labels, hit,
        target_per_million=target_per_million,
        total_benign=total_benign,
        thresholds=thresholds_out,
        policy="max_rule",
        primary=None,
        allowed_routes=present_routes,
    )
    n_benign = int(np.sum(labels == 0))
    _, below_resolution = _max_dev_fp_for_target(
        target_per_million, n_benign, alpha=0.05,
    ) if n_benign > 0 else (0, True)
    out["below_resolution"] = bool(below_resolution)
    if method == "extrapolated":
        out["extrapolated_routes"] = ["max_rule"]
    return out


def _specialist_pareto_curve(
    probs: np.ndarray,
    labels: np.ndarray,
) -> dict[int, float]:
    """Max recall achievable using the specialist's probabilities alone,
    at each integer FP count in [0, n_benign].

    Returned as ``{fp_count: best_recall}``. NaN probs are dropped; ties
    favor benigns (worst case for recall — what an attacker can force by
    pushing malware to the same score as a benign neighbour).

    This is the floor the recall-monotone constraint enforces: any
    ensemble candidate whose recall undershoots this curve at its own FP
    count is wasting FP budget compared to tuning the specialist alone
    to the same budget.
    """
    valid = ~np.isnan(probs)
    if not np.any(valid):
        return {}
    p = probs[valid].astype(np.float64)
    y = labels[valid].astype(np.int8)
    n_mal = int((y == 1).sum())
    if n_mal == 0:
        return {}
    # Sort descending; on ties put benigns BEFORE malware so cumulative FP
    # leads its row's TP — matches what _recall_pr_at_fp does in the eval
    # harness and what an adversary can force at a given threshold.
    order = np.lexsort((y, -p))
    y_sorted = y[order]
    fp_cum = np.cumsum(y_sorted == 0)
    tp_cum = np.cumsum(y_sorted == 1)
    max_fp = int(fp_cum[-1]) if len(fp_cum) else 0
    out: dict[int, float] = {}
    # Walk FP counts ascending: for each k, the max-recall row with
    # fp_cum <= k is monotone, so a single pass suffices.
    j = 0
    n = len(y_sorted)
    last_recall = 0.0
    for k in range(max_fp + 1):
        while j < n and fp_cum[j] <= k:
            last_recall = float(tp_cum[j]) / n_mal
            j += 1
        out[k] = last_recall
    return out


def _specialist_threshold_for_fp(
    probs: np.ndarray,
    labels: np.ndarray,
    fp_target: int,
) -> tuple[float | None, int, int]:
    """Find the loosest specialist threshold yielding at most ``fp_target``
    benigns above it, and return (threshold, tp_count, fp_count_actual).

    Returns (None, 0, 0) if no such threshold exists (e.g. fewer than
    ``fp_target`` benigns in the slice). Threshold is set just above the
    (fp_target+1)-th highest benign so the firing rule ``probs >=
    threshold`` produces exactly ``fp_count_actual`` benigns above the
    line.
    """
    valid = ~np.isnan(probs)
    if not np.any(valid):
        return None, 0, 0
    p = probs[valid].astype(np.float64)
    y = labels[valid].astype(np.int8)
    n_mal = int((y == 1).sum())
    if n_mal == 0:
        return None, 0, 0
    order = np.lexsort((y, -p))
    p_sorted = p[order]
    y_sorted = y[order]
    fp_cum = np.cumsum(y_sorted == 0)
    tp_cum = np.cumsum(y_sorted == 1)
    eligible = np.flatnonzero(fp_cum <= fp_target)
    if len(eligible) == 0:
        return None, 0, 0
    end = int(eligible[-1])
    threshold = float(p_sorted[end])
    return threshold, int(tp_cum[end]), int(fp_cum[end])


def _make_specialist_candidate_at_fp(
    *,
    probs: np.ndarray,
    labels: np.ndarray,
    fp_target: int,
    target_per_million: float,
    total_benign: int,
    specialist_route: str,
) -> dict[str, Any] | None:
    """Build a specialist_only-style candidate tuned to a specific FP
    count. Returns None when the slice can't support that FP level.
    """
    threshold, tp, fp = _specialist_threshold_for_fp(probs, labels, fp_target)
    if threshold is None:
        return None
    valid = ~np.isnan(probs)
    hit = np.zeros(len(labels), dtype=bool)
    hit[valid] = probs[valid] >= threshold
    return _metrics(
        labels,
        hit,
        target_per_million=target_per_million,
        total_benign=total_benign,
        thresholds={specialist_route: float(threshold)},
        policy=f"filetype_only_at_fp_{fp_target}",
        primary=specialist_route,
        allowed_routes=(specialist_route,),
    )


def _make_calibrate_inherited_candidate(
    labels: np.ndarray,
    route_probs: dict[str, np.ndarray],
    *,
    thresholds: dict[str, float],
    target_per_million: float,
    total_benign: int,
    suffix: str = "",
) -> dict[str, Any]:
    """Candidate that applies the calibrate stage's per-route thresholds
    AS-IS — i.e. takes the cascading-scope output (filegroup / general
    fallback when per-filetype dev is too small) and runs an OR-rule
    over the routes for which calibrate produced thresholds.

    The standalone _calibrate_policy candidates re-derive thresholds
    INSIDE the filetype slice. For tiny filetypes that derivation
    fails ("too few benigns to derive a quantile") and the slice ends
    up with no thresholds at all. The calibrate stage already handled
    that case by extrapolating from the wider scope; this candidate
    just propagates that decision into the policy search so it has a
    chance to win against ultra-tight joint-OR thresholds.
    """
    present_routes = tuple(
        route for route in thresholds
        if route in route_probs and not np.all(np.isnan(route_probs[route]))
    )
    if not present_routes:
        return _metrics(
            labels, np.zeros(len(labels), dtype=bool),
            target_per_million=target_per_million,
            total_benign=total_benign,
            thresholds={},
            policy=f"calibrate_inherited{suffix}",
            primary=None,
            allowed_routes=(),
        )
    n_rows = len(labels)
    union_hit = np.zeros(n_rows, dtype=bool)
    selected: dict[str, float] = {}
    for route_name in present_routes:
        t = float(thresholds[route_name])
        probs = route_probs[route_name]
        valid = ~np.isnan(probs)
        hit = np.zeros(n_rows, dtype=bool)
        hit[valid] = probs[valid] >= t
        union_hit |= hit
        selected[route_name] = t
    return _metrics(
        labels, union_hit,
        target_per_million=target_per_million,
        total_benign=total_benign,
        thresholds=selected,
        policy=f"calibrate_inherited{suffix}",
        primary=None,
        allowed_routes=tuple(selected),
    )


def _mark_dominated_by_specialist(
    candidates: list[dict[str, Any]],
    route_probs: dict[str, np.ndarray],
    labels: np.ndarray,
    *,
    specialist_route: str,
    target_per_million: float,
    total_benign: int,
    calibrated_route_probs: dict[str, np.ndarray] | None = None,
    pareto: dict[int, float] | None = None,
    blend_fit: dict[str, Any] | None = None,
) -> None:
    """Inject specialist-tuned-to-same-FP candidates and mark any
    ensemble whose recall falls below the specialist's recall at the
    SAME FP count as dominated.

    Filtering alone isn't enough: removing a dominated ensemble without
    surfacing the specialist alternative at that FP count leaves the
    knapsack with strictly worse choices (the specialist's calibrated
    candidate sits at a different FP). So for each unique FP count used
    by an ensemble candidate, we build a ``filetype_only_at_fp_K``
    candidate using the Pareto-optimal specialist threshold for that FP.

    The check uses the full specialist-Pareto curve rather than just the
    specialist's calibrated operating point — an ensemble spending FP=3
    is compared against what the specialist could achieve relaxed to
    FP<=3. This catches ensembles that waste FP budget for no recall
    gain, even when the specialist's default threshold sits elsewhere.

    Mutates ``candidates`` in place: ensembles get
    ``dominated_by_specialist`` (bool) and ``specialist_recall_at_fp``
    (float) for diagnostic display; new ``filetype_only_at_fp_K`` items
    are appended.
    """
    probs = route_probs.get(specialist_route)
    if probs is None:
        for item in candidates:
            item["dominated_by_specialist"] = False
        return
    # Pareto curve depends only on (specialist probs, labels) — same
    # for every (level, severity) within a filetype. Accept a
    # precomputed curve from the caller to avoid 42× redundant compute
    # per filetype; fall back to computing in place when not provided.
    if pareto is None:
        pareto = _specialist_pareto_curve(probs, labels)
    if not pareto:
        for item in candidates:
            item["dominated_by_specialist"] = False
        return
    max_fp = max(pareto)
    extra_fps: set[int] = set()
    for item in candidates:
        policy = item.get("policy")
        if policy in ("filetype_only", "no_policy"):
            item["dominated_by_specialist"] = False
            continue
        item_fp = int(item.get("fp", 0))
        item_recall = float(item.get("recall", 0.0))
        if math.isnan(item_recall):
            item_recall = 0.0
        spec_recall = pareto.get(item_fp, pareto[max_fp]) if item_fp <= max_fp else pareto[max_fp]
        if item_recall + 1e-9 < spec_recall:
            item["dominated_by_specialist"] = True
            item["specialist_recall_at_fp"] = spec_recall
            # Make sure the knapsack sees the specialist-at-same-FP
            # alternative. Without this the dominated ensemble's slot
            # falls through to the specialist's default-FP candidate,
            # which may use far less FP — a recall regression even
            # though the floor was meant to protect against one.
            extra_fps.add(item_fp)
        else:
            item["dominated_by_specialist"] = False
    # The two FP levels we always want operating points at: 0 (absolute
    # zero-FP-on-calibration, the strictest tier) and 3 (the default
    # deployment severity). Without these, levels with target_per_million
    # too strict for a quantile threshold (notably L0 hostile) collapse to
    # fire-never on every route — even when the specialist has a perfectly
    # good threshold at exactly the level's budget. Injecting unconditionally
    # at these FPs guarantees the per-filetype candidate set always carries
    # a real operating point at the user-priority levels.
    extra_fps |= {0, 3}
    # Only treat a filetype_only candidate as "covering" its FP level if it
    # actually fires (tp > 0). Sentinel fire-never candidates — produced
    # when target_per_million is below what the quantile machinery can
    # resolve (L0 hostile sets target=0 and falls into the early-return
    # at _quantile_severity_threshold:560) — claim fp=0 but catch zero
    # malware, so suppressing the fp=0 injection would leave L0 with no
    # operating point. The Pareto-tuned injection below is the actual
    # zero-FP operating point.
    existing_fps = {
        int(c.get("fp", 0))
        for c in candidates
        if c.get("policy") == "filetype_only" and int(c.get("tp", 0)) > 0
    }
    fp_targets = sorted(extra_fps - existing_fps)
    for fp_target in fp_targets:
        extra = _make_specialist_candidate_at_fp(
            probs=probs,
            labels=labels,
            fp_target=fp_target,
            target_per_million=target_per_million,
            total_benign=total_benign,
            specialist_route=specialist_route,
        )
        if extra is not None:
            extra["dominated_by_specialist"] = False
            candidates.append(extra)

    # Joint-OR injection: at each FP level where a dominated ensemble
    # lived, also try a coordinate-descent OR-rule that respects the
    # budget. If the specialist's solo-Pareto still wins, the floor
    # below will dominate this candidate too; if joint-OR catches
    # malware the specialist alone misses (decorrelated routes), it
    # survives and the knapsack has a third option besides
    # specialist-only and the original independent-threshold OR-rule.
    routes_for_joint = tuple(r for r in route_probs.keys() if r != specialist_route)
    # Include the specialist in the OR-rule too — multi-route OR with
    # specialist as one component is what most ensembles look like at
    # deploy.
    routes_for_joint_full = tuple(route_probs.keys())
    if len(routes_for_joint_full) >= 2:
        for fp_target in fp_targets:
            joint = _make_joint_or_candidate_at_fp(
                route_probs=route_probs,
                labels=labels,
                routes=routes_for_joint_full,
                fp_target=fp_target,
                target_per_million=target_per_million,
                total_benign=total_benign,
            )
            if joint is None:
                continue
            # Apply the same recall-monotone floor to joint-OR.
            item_fp = int(joint.get("fp", 0))
            item_recall = float(joint.get("recall", 0.0))
            if math.isnan(item_recall):
                item_recall = 0.0
            spec_recall = pareto.get(item_fp, pareto[max_fp]) if item_fp <= max_fp else pareto[max_fp]
            if item_recall + 1e-9 < spec_recall:
                joint["dominated_by_specialist"] = True
                joint["specialist_recall_at_fp"] = spec_recall
            else:
                joint["dominated_by_specialist"] = False
            candidates.append(joint)

    # Learned-blend (logistic regression on logit-stacked route probs).
    # Same FP injection set as joint-OR; the floor below filters those
    # the specialist alone can match at the same FP. The standalone
    # experiment (scripts/azoth_stacker_experiment.py) showed the
    # in-sample bias on specialist probs DOES NOT meaningfully shift
    # train+dev recall vs test recall — train+dev numbers are within
    # tenths of a percent of test for the blends that ended up
    # competitive. The integration is therefore safe to consume by the
    # global knapsack as-is.
    # Use calibrated probs for blend fitting so the learned weights live
    # in the same prob space litmus emits at deploy (post-isotonic). The
    # OR-rule machinery above continues to operate on raw probs because
    # litmus calibrates per-route THRESHOLDS at load via
    # calibrate_policy_thresholds_with — that translation is monotone
    # for the OR-rule but doesn't decompose for a learned blend.
    # Learned-blend candidates reuse a precomputed fit when the caller
    # supplied one — the LR weights and per-row blend score depend only
    # on (filetype slice, routes), so they're the same for every level
    # and severity. Only the threshold tuning per fp_target needs to
    # vary. The fallback path (no precomputed fit) fits fresh; that's
    # what the back-compat wrapper does too.
    blend_probs = (
        calibrated_route_probs if calibrated_route_probs is not None else route_probs
    )
    if len(routes_for_joint_full) >= 2:
        if blend_fit is None:
            blend_fit = _fit_learned_blend(
                blend_probs, labels, routes_for_joint_full,
            )
        if blend_fit is not None:
            for fp_target in fp_targets:
                blend = _blend_candidate_from_fit(
                    blend_fit, labels,
                    fp_target=fp_target,
                    target_per_million=target_per_million,
                    total_benign=total_benign,
                )
                if blend is None:
                    continue
                item_fp = int(blend.get("fp", 0))
                item_recall = float(blend.get("recall", 0.0))
                if math.isnan(item_recall):
                    item_recall = 0.0
                spec_recall = pareto.get(item_fp, pareto[max_fp]) if item_fp <= max_fp else pareto[max_fp]
                if item_recall + 1e-9 < spec_recall:
                    blend["dominated_by_specialist"] = True
                    blend["specialist_recall_at_fp"] = spec_recall
                else:
                    blend["dominated_by_specialist"] = False
                candidates.append(blend)


# Reject candidates whose realized slice FPR is well above the
# calibration target. "Roughly 3 FP/M per pool" tolerates the noise
# inherent in finite-sample quantile estimation:
#
#   slice with N benigns at target r FP/M -> expected count = rN/1e6
#   95% Poisson CI -> realized count up to ~3× expected for large N
#
# At a 3 FP/M target on a 100K-benign slice that's a realized FPR of
# up to ~30 FP/M. We accept up to 10× target as plausible noise. Beyond
# that the candidate is operating at a *different* target (e.g. the
# `_at_fp_25` policies are blend pareto operating points at ~190 FP/M
# on python's slice, not noisy 3 FP/M realizations) and gets filtered.
#
# Small-benign slices (xlsx with 144 benigns) often produce a
# candidate that fires on every benign in the slice. That's a broken
# calibration, not a deployable operating point, and gets filtered
# whether the multiplier is 10× or 100×.
_CHOOSE_BEST_FPR_OVER_TARGET_MULTIPLIER = 10.0


def _is_over_target(item: dict[str, Any]) -> bool:
    """A candidate's realized slice FPR is too far above its level's
    calibration target to count as "roughly the target rate." Used to
    filter candidates labeled with one target but operating at a
    different one (e.g. ``learned_blend_at_fp_25`` candidates whose
    realized FPR is ~50× target — they're pareto operating points the
    blend explored, not noisy 3 FP/M realizations), and to filter
    broken calibrations on tiny-benign slices (e.g. xlsx candidates
    that fire on every benign in the slice).

    L0 (target=0 FP/M) is special: any non-zero realized FP is
    over-target. Multiplier can't help — 0 × anything = 0. So strict
    fp==0 is the gate at L0.
    """
    realized_fp = int(item.get("fp") or 0)
    target = float(item.get("target_per_million") or 0.0)
    realized_fpm = float(item.get("fp_per_100M") or 0.0)
    if target <= 0:
        # L0 hostile / "true zero FP" levels.  Strict: any benign hit
        # in the slice disqualifies the candidate.
        return realized_fp > 0
    if math.isnan(realized_fpm):
        return False
    return realized_fpm > target * _CHOOSE_BEST_FPR_OVER_TARGET_MULTIPLIER


def _choose_best(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Pick the per-filetype policy strategy that gives the best
    detection-vs-FP balance at this level's per-route 3 FP/M target.

    Selection key (lex, max wins):
      1. recall — catch more malware at the calibration target. The
         deployment goal.
      2. f1 — recall/precision balance.
      3. -fp — when other metrics tie, prefer the quieter policy.
      4. len(allowed_routes) — tiebreaker that keeps inclusive policies
         (naming multiple routes) over single-route ones. Litmus uses
         the route NAMES in route_policies.json to decide whether to
         load each specialist; preserving inclusive names keeps every
         specialist loadable even when below-resolution slices have
         identical metrics across policies.
      5. policy — alphabetic, just for determinism.

    Filters (applied before the max):
      * ``dominated_by_specialist=True`` — spending more FP than the
        specialist alone needs for the same recall.
      * realized FPR > 10× target. See ``_is_over_target``. Filters
        two distinct pathologies in one rule:
        (a) candidates labeled with the level target but actually
            operating at a different one (e.g. ``learned_blend_at_fp_25``
            candidates run at ~190 FP/M on python's slice — not noisy
            3 FP/M but a different operating point the blend search
            explored), and
        (b) broken small-slice calibration where the candidate fires on
            every benign because the (1 - r×10⁻⁶) quantile fell below
            the smallest observed prob (xlsx with 144 benigns is the
            canonical case).

    Accuracy is intentionally not used: with the corpus's ~64% benign /
    36% malware split, accuracy is dominated by the benign class and
    tracks recall most of the way at strict FP budgets.
    """
    eligible = [
        c for c in candidates
        if not c.get("dominated_by_specialist") and not _is_over_target(c)
    ]
    if not eligible:
        # Fall back to the no-policy candidate (fp=0, tp=0) if every
        # candidate failed the filters — better to deploy a
        # known-inert candidate than to deploy a catastrophe.
        no_policy = next(
            (c for c in candidates if c.get("policy") == "no_policy"),
            None,
        )
        if no_policy is not None:
            return no_policy
        # Last resort: original candidates without filter. Should not
        # be reachable for any well-formed candidate list since
        # _candidate_lists always includes a no_policy entry.
        eligible = list(candidates)
    return max(
        eligible,
        key=lambda item: (
            float(item["recall"]) if not math.isnan(float(item["recall"])) else -1.0,
            float(item["f1"]) if not math.isnan(float(item["f1"])) else -1.0,
            -int(item["fp"]),
            len(item.get("allowed_routes") or ()),
            item["policy"],
        ),
    )


def _no_hit_candidate(
    labels: np.ndarray,
    *,
    target_per_million: float,
    total_benign: int,
) -> dict[str, Any]:
    return _metrics(
        labels,
        np.zeros(len(labels), dtype=bool),
        target_per_million=target_per_million,
        total_benign=total_benign,
        thresholds={},
        policy="no_policy",
        primary=None,
        allowed_routes=(),
    )


def _apply_global_budget_selection(payload: dict[str, Any], config: dict[str, Any]) -> None:
    """Replace local winners with a full-corpus budgeted choice.

    Filetypes partition the score table, so false positives and true positives
    add across filetype policies. For each level/severity this is a
    multiple-choice knapsack: choose one candidate per filetype, maximize TP,
    and keep total FP inside the configured global budget.
    """

    total_benign = int(payload["benign"])
    routes = list(payload["routes"].items())
    for config_level in config["levels"]:
        level_no = int(config_level["level"])
        for severity in ("hostile",):
            target = float(config_level[severity]["target_per_million"])
            budget = _budget(total_benign, target)
            dp: dict[int, tuple[int, list[int]]] = {0: (0, [])}
            candidate_lists: list[list[dict[str, Any]]] = []
            route_names: list[str] = []
            for route_name, route in routes:
                level = next(item for item in route["levels"] if int(item["level"]) == level_no)
                candidates = list(level[severity]["candidates"])
                if not any(int(item["fp"]) == 0 and int(item["tp"]) == 0 for item in candidates):
                    candidates.append(
                        {
                            "policy": "no_policy",
                            "primary": None,
                            "allowed_routes": [],
                            "target_per_100M": target * 100.0,
                            "thresholds": {},
                            "tp": 0,
                            "fp": 0,
                            "tn": int(route["benign"]),
                            "fn": int(route["malware"]),
                            "recall": 0.0 if int(route["malware"]) else math.nan,
                            "precision": 0.0,
                            "f1": 0.0 if int(route["malware"]) else math.nan,
                            "accuracy": int(route["benign"]) / max(int(route["rows"]), 1),
                            "fpr": 0.0,
                            "fp_per_100M": 0.0,
                            "global_fp_per_million": 0.0,
                        },
                    )
                candidate_lists.append(candidates)
                route_names.append(route_name)

                next_dp: dict[int, tuple[int, list[int]]] = {}
                for used_fp, (used_tp, choices) in dp.items():
                    for idx, candidate in enumerate(candidates):
                        # Recall-monotone floor: skip ensemble candidates
                        # that lose to the specialist tuned to the same
                        # FP count. Their slot in the knapsack should go
                        # to the specialist's own candidate (or no_policy
                        # if that's not affordable either).
                        if candidate.get("dominated_by_specialist"):
                            continue
                        fp = used_fp + int(candidate["fp"])
                        if fp > budget:
                            continue
                        tp = used_tp + int(candidate["tp"])
                        current = next_dp.get(fp)
                        # Tiebreak on inclusiveness: when two candidate
                        # combinations produce the same (tp, fp) totals, prefer
                        # the one whose latest pick names more routes in its
                        # policy. This matters at below-resolution levels where
                        # many policies tie on metrics — without the tiebreak,
                        # general_only (1 route) silently wins over
                        # specialist_primary_with_escape (3 routes), and
                        # specialist routes never get into route_policies.json's
                        # thresholds maps. Litmus's contains_route check then
                        # rejects those specialists as "uncalibrated."
                        if current is None or tp > current[0]:
                            next_dp[fp] = (tp, choices + [idx])
                        elif tp == current[0]:
                            cur_routes = len(candidates[current[1][-1]].get("allowed_routes") or ()) if current[1] else 0
                            new_routes = len(candidate.get("allowed_routes") or ())
                            if new_routes > cur_routes:
                                next_dp[fp] = (tp, choices + [idx])
                dp = next_dp or {0: (0, choices + [len(candidates) - 1]) for _fp, (_tp, choices) in dp.items()}

            best_fp, (_best_tp, best_choices) = max(
                dp.items(),
                key=lambda item: (item[1][0], -item[0]),
            )
            _ = best_fp
            for route_name, choice_idx in zip(route_names, best_choices, strict=True):
                route = payload["routes"][route_name]
                level = next(item for item in route["levels"] if int(item["level"]) == level_no)
                level[severity]["best"] = candidate_lists[route_names.index(route_name)][choice_idx]


def _csv_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for route_name, route in payload["routes"].items():
        for level in route["levels"]:
            for severity in ("hostile",):
                best = level[severity]["best"]
                rows.append(
                    {
                        "route": route_name,
                        "level": level["level"],
                        "severity": severity,
                        "policy": best["policy"],
                        "primary": best["primary"],
                        "rows": route["rows"],
                        "malware": route["malware"],
                        "benign": route["benign"],
                        "tp": best["tp"],
                        "fp": best["fp"],
                        "recall": best["recall"],
                        "precision": best["precision"],
                        "f1": best["f1"],
                        "accuracy": best["accuracy"],
                        "fp_per_100M": best["fp_per_100M"],
                        "global_fp_per_million": best["global_fp_per_million"],
                        "thresholds": json.dumps(best["thresholds"], sort_keys=True),
                    },
                )
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _pct(value: float | None) -> str:
    if value is None:
        return "-"
    try:
        f = float(value)
    except (TypeError, ValueError):
        return "-"
    if math.isnan(f):
        return "-"
    return f"{100 * f:.2f}%"


def _fmt_float(value: Any, digits: int = 2) -> str:
    if value is None:
        return "—"
    try:
        f = float(value)
    except (TypeError, ValueError):
        return "—"
    if math.isnan(f):
        return "—"
    return f"{f:.{digits}f}"


def _sort_float(value: Any) -> float:
    if value is None:
        return -1.0
    numeric = float(value)
    return -1.0 if math.isnan(numeric) else numeric


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Azoth Route Policy Search",
        "",
        "Best calibrated decision policy per filetype route. `*_with_escape` policies start from the specialist/group model, then allow general/group/type escape thresholds only when they add detections inside the route FP budget.",
        "",
        f"- Calibration snapshot: `{payload.get('calibration_snapshot_id')}`",
        f"- Rows: {payload.get('rows')} ({payload.get('malware')} malware, {payload.get('benign')} benign)",
    ]
    # Headline sections: L50 (new default), L100 (loose end of the new grid).
    # Skip a level cleanly if a route lacks it — happens for routes whose
    # policies are carried forward from a pre-migration bundle that emitted
    # the old (0,1,2,3,5,10,25,50,100,200,300,500,1000,2000) grid.
    for level_no, severity in [(50, "hostile"), (100, "hostile")]:
        rows = []
        for route_name, route in payload["routes"].items():
            level = next(
                (item for item in route["levels"] if item["level"] == level_no),
                None,
            )
            if level is None:
                continue
            rows.append((route_name, route, level[severity]["best"]))
        if not rows:
            continue
        rows.sort(key=lambda item: (-_sort_float(item[2]["recall"]), -int(item[1]["malware"]), item[0]))
        lines.extend(
            [
                "",
                f"## L{level_no} {severity.title()}",
                "",
                "Rows marked † are below data resolution: the per-filetype "
                "calibration sample is too small to credibly assert FP/100M ≤ "
                "target at this level (95% CI). The threshold shown is the "
                "loosest empirical 0-FP threshold; FP/100M is what the test "
                "partition actually observed under that threshold. *95% CI "
                "upper* is the Clopper-Pearson upper bound on deployment "
                "FP/100M given the observed FP count in this filetype's benigns.",
                "",
                "| Route | Policy | Malware | Benign | Recall | FP | FP/100M | 95% CI upper (FP/100M) | Global FP/100M | F1 | Accuracy | Thresholds |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
            ],
        )
        for route_name, route, best in rows[:30]:
            mark = "†" if best.get("below_resolution") else ""
            ben = int(route["benign"])
            cp_upper = (
                _clopper_pearson_fp_per_million_upper(int(best["fp"]), ben, alpha=0.05) * 100.0
                if ben > 0 and best.get("fp") is not None
                else None
            )
            global_fp_per_million = best.get("global_fp_per_million")
            global_fp_per_100M = (
                global_fp_per_million * 100.0 if global_fp_per_million is not None else None
            )
            lines.append(
                "| "
                f"{route_name}{mark} | "
                f"{best['policy']} | "
                f"{route['malware']} | "
                f"{ben} | "
                f"{_pct(best.get('recall'))} | "
                f"{best['fp']} | "
                f"{_fmt_float(best.get('fp_per_100M'), 2)} | "
                f"{_fmt_float(cp_upper, 2)} | "
                f"{_fmt_float(global_fp_per_100M, 3)} | "
                f"{_pct(best.get('f1'))} | "
                f"{_pct(best.get('accuracy'))} | "
                f"`{json.dumps(best['thresholds'], sort_keys=True)}` |",
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def _parse_override(values: list[str]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"invalid --override-route {value!r}; expected route=directory")
        route, raw_path = value.split("=", 1)
        if not route:
            raise ValueError(f"invalid --override-route {value!r}; empty route")
        out[route] = Path(raw_path)
    return out


def _apply_route_overrides(
    *,
    db_path: str | None,
    score_table: np.lib.npyio.NpzFile,
    routes: dict[str, dict[str, Any]],
    overrides: dict[str, Path],
    fallback_spec: Path,
    workers: int,
) -> None:
    if not overrides:
        return
    if not db_path:
        raise SystemExit("--db is required when --override-route is used")
    labels = score_table["labels"].astype(np.int8)
    file_types = np.asarray([str(value) for value in score_table["file_types"]])
    file_groups = np.asarray([str(value) for value in score_table["file_groups"]])
    for route_name, route_dir in overrides.items():
        if route_name.startswith("filetypes/"):
            kind = "filetype"
            route_value = route_name.split("/", 1)[1]
            indices = np.flatnonzero(file_types == route_value).astype(np.int64)
        elif route_name.startswith("filegroups/"):
            kind = "filegroup"
            route_value = route_name.split("/", 1)[1]
            indices = np.flatnonzero(file_groups == route_value).astype(np.int64)
        else:
            raise SystemExit(f"{route_name}: expected filetypes/<name> or filegroups/<name>")
        if len(indices) == 0:
            raise SystemExit(f"{route_name}: no rows in score table")
        row_ids = score_table["row_ids"][indices].astype(np.int64)
        rows = [(int(row_id), int(labels[idx])) for row_id, idx in zip(row_ids, indices, strict=True)]
        spec_path = route_dir / "feature_spec.json"
        if not spec_path.exists():
            spec_path = fallback_spec
        if not bundle.has_model(route_dir):
            raise SystemExit(f"{route_name}: no model file found in {route_dir}")
        spec = features.FeatureSpec.load(spec_path)
        # Multi-seed bundles get averaged inside the Ensemble; legacy bundles
        # are length-1 ensembles whose predict_proba is byte-identical to the
        # pre-item-A path.
        clf = bundle.Ensemble.load_bundle(route_dir)
        batches = list(features.extract_labeled_from_db_batches(db_path, rows, spec, n_workers=workers))
        x_matrix = (
            sp.vstack([batch[0] for batch in batches], format="csr")
            if batches
            else sp.csr_matrix((0, spec.total_features), dtype=np.float32)
        )
        probs = clf.predict_proba(x_matrix).astype(np.float32)
        routes[route_name] = {
            "kind": kind,
            "indices": indices,
            "probs": probs,
            "override_dir": str(route_dir),
            "feature_spec": str(spec_path),
        }


# Per-process state populated by the parent before forking workers.
# Each worker sees an inherited (read-only) view via copy-on-write on
# Linux; spawn-based platforms reimport this module but the data stays
# small (the arrays are loaded once in main() from disk).
_SHARED: dict[str, Any] = {}


def _resolve_parallelism(requested: int, n_filetypes: int) -> int:
    """Pick a worker count. ``requested`` semantics match other scripts:
    ``0`` (the default) means autodetect, positive integers are honored,
    and anything > n_filetypes is capped so we don't fork idle workers.

    Autodetect uses ``os.process_cpu_count()`` when available (cgroup
    aware on Linux 3.13+), falls back to ``os.cpu_count()``. We cap the
    autodetected count at 32 to avoid memory churn on high-core hosts
    where each worker is a forked Python process; explicit values
    above 32 are still honored.
    """
    if requested > 0:
        return min(requested, max(1, n_filetypes))
    auto = getattr(os, "process_cpu_count", os.cpu_count)() or 1
    return min(max(1, auto), n_filetypes, 32)


def _process_filetype(file_type: str) -> tuple[str, dict[str, Any]]:
    """Compute one filetype's policy block.

    Reads shared state from ``_SHARED`` (set up by ``main`` before
    workers fork). Returns the JSON-shaped payload for
    ``routes[filetypes/<name>]`` plus its key, so the caller can stitch
    everything back together. Per-filetype work hoisted out of the
    level loop: specialist Pareto curve and learned-blend LR fit both
    depend only on (file_type, route_probs, labels), so the work is
    done once here instead of 42× inside the level loop.
    """
    routes = _SHARED["routes"]
    labels = _SHARED["labels"]
    file_types = _SHARED["file_types"]
    filetype_to_group = _SHARED["filetype_to_group"]
    config = _SHARED["config"]
    azoth_root = _SHARED["azoth_root"]
    total_benign = _SHARED["total_benign"]

    mask = file_types == file_type
    indices = np.flatnonzero(mask).astype(np.int64)
    scoped_labels = labels[indices]
    malware = int(np.sum(scoped_labels == 1))
    benign = int(np.sum(scoped_labels == 0))
    group = filetype_to_group.get(file_type)
    group_route = f"filegroups/{group}" if group else None
    type_route = f"filetypes/{file_type}"
    route_names = ["general"]
    if group_route and group_route in routes:
        route_names.append(group_route)
    if type_route in routes:
        route_names.append(type_route)
    route_probs = {
        route_name: dense
        for route_name in route_names
        if (dense := _dense_route_probs(routes, route_name, indices)) is not None
    }
    calibrated_route_probs = _build_calibrated_route_probs(
        route_probs, azoth_root,
    ) if route_probs else {}
    specialist_probs = route_probs.get(type_route)
    pareto = (
        _specialist_pareto_curve(specialist_probs, scoped_labels)
        if specialist_probs is not None else None
    )
    routes_for_joint_full = tuple(route_probs.keys())
    blend_fit = None
    if len(routes_for_joint_full) >= 2:
        blend_probs = (
            calibrated_route_probs if calibrated_route_probs else route_probs
        )
        blend_fit = _fit_learned_blend(
            blend_probs, scoped_labels, routes_for_joint_full,
        )
    levels: list[dict[str, Any]] = []
    for target in config["levels"]:
        level_no = int(target["level"])
        level_item: dict[str, Any] = {"level": level_no}
        for severity in ("hostile",):
            target_per_million = float(target[severity]["target_per_million"])
            candidates = [
                _no_hit_candidate(
                    scoped_labels,
                    target_per_million=target_per_million,
                    total_benign=total_benign,
                )
            ]
            if malware:
                candidates.extend(
                    _calibrate_policy(
                        scoped_labels,
                        route_probs,
                        policy=policy,
                        primary=primary,
                        allowed_routes=allowed,
                        target_per_million=target_per_million,
                        total_benign=total_benign,
                    )
                    for policy, primary, allowed in _policy_candidates(
                        general="general",
                        group=group_route if group_route in route_probs else None,
                        filetype=type_route if type_route in route_probs else None,
                    )
                )
                routes_for_max = tuple(
                    route for route in (
                        "general",
                        group_route if group_route in route_probs else None,
                        type_route if type_route in route_probs else None,
                    )
                    if route is not None
                )
                if len(routes_for_max) >= 2:
                    candidates.append(
                        _calibrate_max_rule_policy(
                            scoped_labels,
                            route_probs,
                            allowed_routes=routes_for_max,
                            target_per_million=target_per_million,
                            total_benign=total_benign,
                        ),
                    )
            calibrated_thresholds = target[severity].get("thresholds", {})
            if calibrated_thresholds:
                candidates.append(
                    _make_calibrate_inherited_candidate(
                        scoped_labels, route_probs,
                        thresholds=calibrated_thresholds,
                        target_per_million=target_per_million,
                        total_benign=total_benign,
                    ),
                )
            # (Previously: when hostile had no inherited thresholds, fall back
            # to the suspicious thresholds. With suspicious removed from
            # collimator's output, there's no fallback source — the candidate
            # set just relies on the no-hit + policy + max-rule candidates.)
            _mark_dominated_by_specialist(
                candidates,
                route_probs,
                scoped_labels,
                specialist_route=type_route,
                target_per_million=target_per_million,
                total_benign=total_benign,
                calibrated_route_probs=calibrated_route_probs,
                pareto=pareto,
                blend_fit=blend_fit,
            )
            level_item[severity] = {
                "target_per_million": target_per_million,
                "budget": _budget(benign, target_per_million),
                "best": _choose_best(candidates),
                "candidates": candidates,
            }
        levels.append(level_item)
    return f"filetypes/{file_type}", {
        "filetype": file_type,
        "filegroup": group,
        "models": list(route_probs),
        "rows": int(len(indices)),
        "malware": malware,
        "benign": benign,
        "levels": levels,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=None)
    parser.add_argument("--config", type=Path, default=Path("out/models/azoth/config.json"))
    parser.add_argument("--score-table", type=Path, default=Path("out/models/azoth/score_table.npz"))
    parser.add_argument(
        "--azoth-root",
        type=Path,
        default=Path("out/models/azoth"),
        help=(
            "Root containing per-route calibrator.json files. Used by the "
            "learned_blend candidate to fit on isotonic-calibrated probs "
            "rather than the raw probs in the score table, so the blend "
            "weights match the deploy-time probabilities litmus emits."
        ),
    )
    parser.add_argument("--output", type=Path, default=Path("out/models/azoth/route_policies.json"))
    parser.add_argument("--csv", type=Path, default=Path("out/models/azoth/route_policies.csv"))
    parser.add_argument("--markdown", type=Path, default=Path("out/models/azoth/route_policies.md"))
    parser.add_argument("--override-route", action="append", default=[])
    parser.add_argument(
        "--previous-bundle", type=Path, default=None,
        help=(
            "Previous bundle path. When set, the script compares this "
            "bundle's score_table.npz against the current one and "
            "carries forward route_policies entries for filetypes "
            "whose routes' scores are bytewise-identical. Major win on "
            "promote: only filetypes whose routes actually changed get "
            "re-searched; the rest copy from "
            "<previous-bundle>/route_policies.json."
        ),
    )
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument(
        "--parallelism",
        type=int,
        default=0,
        help=(
            "Worker processes for per-filetype policy search. 0 (default) "
            "autodetects from process_cpu_count() capped at 32 and at "
            "the filetype count. Set to 1 to force serial."
        ),
    )
    parser.add_argument(
        "--global-fp-budget",
        action="store_true",
        default=False,
        help=(
            "Legacy semantic: enforce a single corpus-wide FP budget "
            "(target_per_million × total_corpus_benign) across all "
            "filetypes via knapsack, replacing per-filetype "
            "_choose_best picks. The default (omit this flag) is the "
            "per-route per-filetype 'L3 = roughly 3 FP per 1M scans "
            "of this filetype/group/pool' semantic — each route's "
            "threshold is calibrated to its own pool's 3 FP/M and we "
            "deploy whatever per-filetype combination maximizes recall "
            "at that calibration."
        ),
    )
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)
    score_table = np.load(args.score_table)
    labels = score_table["labels"].astype(np.int8)
    file_types = np.asarray([str(value) for value in score_table["file_types"]])
    filetype_to_group = {str(k): str(v) for k, v in config.get("filetype_to_group", {}).items()}
    routes = _route_arrays(score_table)
    _apply_route_overrides(
        db_path=args.db,
        score_table=score_table,
        routes=routes,
        overrides=_parse_override(args.override_route),
        fallback_spec=Path(config.get("root", "out/models/azoth")) / "general" / "feature_spec.json",
        workers=args.workers,
    )
    total_benign = int(np.sum(labels == 0))
    route_payload: dict[str, Any] = {}

    # Stash per-filetype-shared state where the worker function can see
    # it. With fork-based multiprocessing (Linux default) child workers
    # inherit these arrays read-only via COW; on spawn-based platforms
    # they're rebuilt per worker but the cost is small relative to the
    # policy_search compute itself.
    _SHARED["routes"] = routes
    _SHARED["labels"] = labels
    _SHARED["file_types"] = file_types
    _SHARED["filetype_to_group"] = filetype_to_group
    _SHARED["config"] = config
    _SHARED["azoth_root"] = args.azoth_root
    _SHARED["total_benign"] = total_benign

    unique_filetypes = sorted(set(file_types))

    # Carry-forward optimization for single-route promotes. When
    # --previous-bundle is set, compare the current score_table.npz
    # against the previous one; for filetypes whose relevant routes
    # are bytewise-identical between bundles, the policy choice cannot
    # have changed (it's a deterministic function of the scores).
    # Copy those entries from <previous-bundle>/route_policies.json
    # rather than re-running policy_search on them.
    carry_forward_policies: dict[str, dict[str, Any]] = {}
    if args.previous_bundle is not None:
        try:
            import sys as _sys
            _sys.path.insert(0, str(Path(__file__).parent))
            from azoth_impact import changed_routes, unchanged_filetypes  # noqa: PLC0415
            from azoth_specialist_suite import DEPLOYMENT_GROUPS  # noqa: PLC0415
            prev_score_table = args.previous_bundle / "score_table.npz"
            prev_policies_path = args.previous_bundle / "route_policies.json"
            changed_set, _ = changed_routes(args.score_table, prev_score_table)
            avail_routes = set(routes.keys())
            unchanged = unchanged_filetypes(
                changed_set, DEPLOYMENT_GROUPS, avail_routes, unique_filetypes,
            )
            print(
                f"policy_search carry-forward: {len(changed_set)}/{len(avail_routes)} "
                f"routes changed; {len(unchanged)}/{len(unique_filetypes)} filetypes "
                f"can be carried forward from previous bundle"
            )
            if prev_policies_path.is_file():
                with open(prev_policies_path) as f:
                    prev_payload = json.load(f)
                prev_routes = prev_payload.get("routes", {}) or {}
                for ft in unchanged:
                    route_key = f"filetypes/{ft}"
                    if route_key in prev_routes:
                        carry_forward_policies[route_key] = prev_routes[route_key]
        except Exception as e:  # noqa: BLE001
            print(f"policy_search: carry-forward setup failed ({e}); "
                  f"running full search")
            carry_forward_policies = {}

    # Stash carried-forward results into route_payload directly; only
    # process the remaining filetypes.
    for route_key, entry in carry_forward_policies.items():
        route_payload[route_key] = entry
    skipped = set(rk.split("/", 1)[1] for rk in carry_forward_policies if rk.startswith("filetypes/"))
    to_process = [ft for ft in unique_filetypes if ft not in skipped]

    parallelism = _resolve_parallelism(args.parallelism, len(to_process))
    if not to_process:
        print(f"policy_search: all {len(unique_filetypes)} filetypes carried forward; "
              f"no recomputation needed")
        results = []
    elif parallelism <= 1 or len(to_process) <= 1:
        print(f"policy_search: processing {len(to_process)} filetypes serially "
              f"({len(skipped)} carried forward)")
        results = [_process_filetype(ft) for ft in to_process]
    else:
        print(
            f"policy_search: processing {len(to_process)} filetypes "
            f"across {parallelism} worker processes "
            f"({len(skipped)} carried forward)",
        )
        ctx = mp.get_context("fork")
        with ctx.Pool(parallelism) as pool:
            results = list(pool.imap_unordered(_process_filetype, to_process))
    for route_key, ft_payload in results:
        route_payload[route_key] = ft_payload

    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "schema": "azoth.route_policy_search.v1",
        "calibration_snapshot_id": config.get("calibration_snapshot_id"),
        "rows": int(len(labels)),
        "malware": int(np.sum(labels == 1)),
        "benign": total_benign,
        "routes": route_payload,
    }
    if args.global_fp_budget:
        # Legacy semantic — reinterpret per-level target_per_million as
        # a CORPUS-WIDE rate (target × total_corpus_benign = budget),
        # then knapsack across filetypes to maximize TP within that
        # single global budget. Caps total FPs aggressively (~9 for
        # L3 at 3 FP/M on a 3M-benign corpus) but distorts the
        # per-pool calibration since most filetypes end up forced to
        # at_fp_0 candidates regardless of their slice's own 3 FP/M
        # threshold.
        _apply_global_budget_selection(payload, config)
    payload = _json_clean(payload)
    # route_policies.json is loaded by litmus; a partial write would crash
    # bundle load. Atomic temp+rename guards against process kill.
    bundle.atomic_write_json(args.output, payload)
    csv_rows = _csv_rows(payload)
    _write_csv(args.csv, csv_rows)
    _write_markdown(args.markdown, payload)
    print(f"wrote {args.output}")
    print(f"wrote {args.csv}")
    print(f"wrote {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
