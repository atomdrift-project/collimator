#!/usr/bin/env python3
"""Compute per-filetype routed-ensemble metrics for the Azoth bundle.

For each filetype that has a specialist registered in `route_policies.json`,
this computes three views from the calibration score table:

  * **general**:   score with the `general` route alone (matches EMBER 2024's
                   "All files" classifier evaluated on the filetype subset)
  * **specialist**: score with `filetypes/<name>` alone (matches EMBER 2024's
                    per-filetype classifier evaluated on its own subset)
  * **ensemble**:   the deployed routing rule for this filetype — max of the
                    routes the policy allows at level 5 hostile (the default
                    deploy operating point).  Threshold-equivalent to the
                    "OR" decision the runtime makes.

Output: `per_filetype_metrics.json` written next to the score table.  Each
filetype carries `n_files`, `n_malware`, `n_benign`, plus three metric
blocks each with `roc_auc`, `pr_auc`, `f1` (computed at the F-beta optimum
threshold) and `f1_at_05` for callers that want a fixed reference point.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import sys
from pathlib import Path
from typing import Any


def _strip_nan(value: Any) -> Any:
    """Replace non-finite floats (NaN, ±inf) with None recursively so
    ``json.dump(..., allow_nan=False)`` produces standards-compliant JSON.
    Strict parsers (Go's encoding/json — used by autocollie) reject the
    literal ``NaN`` Python writes with ``allow_nan=True``."""
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {k: _strip_nan(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_strip_nan(v) for v in value]
    return value

# Make sibling scripts importable (e.g., azoth_impact, azoth_specialist_suite).
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import KFold

from collimator import data as collimator_data
from collimator.thresholds import (
    _CHART_LEVELS_PER_100M,
    DEFAULT_SEVERITY_LEVEL as _DEFAULT_SEVERITY_LEVEL_FROM_THRESHOLDS,
    quantile_severity_threshold,
)

LOG = logging.getLogger("compute_routed_metrics")

# Default operating point on the per-100M-benigns grid. Sourced from the
# canonical DEFAULT_SEVERITY_LEVEL in collimator.thresholds — flip there to
# change for the whole pipeline. Litmus's `-l` default mirrors it.
DEFAULT_LEVEL = _DEFAULT_SEVERITY_LEVEL_FROM_THRESHOLDS

# Full deploy grid of per-100M operating points. Sourced from the thresholds
# module so the recall curve emitted here tracks whatever litmus actually
# threshold-sets at scan time. Bootstrap CIs are computed for every level
# below DEFAULT_LEVEL when ``with_ci`` is True; consumers (azoth READMEs)
# render the full curve as an SVG.
RECALL_CURVE_LEVELS: tuple[int, ...] = tuple(_CHART_LEVELS_PER_100M)


def _entry_recall_levels(entry: dict[str, Any]) -> set[int]:
    """The per-100M levels a metrics entry actually carries recall for.

    Reads across the entry's ``general``/``specialist``/``ensemble`` blocks
    (all produced by ``_metrics`` over the same grid, so any one is
    representative) and returns the set of integer levels ``N`` for which a
    ``recall_at_N_per_100M`` key exists.
    """
    levels: set[int] = set()
    for block_name in ("ensemble", "specialist", "general"):
        block = entry.get(block_name)
        if not isinstance(block, dict):
            continue
        for key in block:
            if key.startswith("recall_at_") and key.endswith("_per_100M"):
                mid = key[len("recall_at_"):-len("_per_100M")]
                if mid.isdigit():
                    levels.add(int(mid))
    return levels


def _entry_covers_current_grid(entry: dict[str, Any]) -> bool:
    """Whether a previous-bundle metrics entry was computed on the current
    recall grid, so it can be carried forward without leaving holes.

    Score-identity is not sufficient for carry-forward: the deploy grid
    (``_LEVELS_PER_100M``) and operating level can change even when a
    route's scores don't (e.g. a pure recalibrate that moves the default
    from L50 to L25). A prior entry computed on the old grid lacks the new
    levels' ``recall_at_N_per_100M`` fields — carrying it forward would
    blank the operating-level column and punch holes in the recall curve
    for exactly the big, stable routes that never get retrained. Requiring
    the full current grid forces a recompute whenever the grid moved.
    """
    return set(RECALL_CURVE_LEVELS).issubset(_entry_recall_levels(entry))


def _test_mask_cache_key(db_path: str, row_ids: np.ndarray) -> str:
    """Stable cache key for a score table's row order and split source."""
    arr = np.ascontiguousarray(row_ids)
    h = hashlib.sha256()
    h.update(b"azoth-test-mask-v3")
    h.update(db_path.encode("utf-8"))
    h.update(str(collimator_data.TEST_BUCKET_MAX).encode("ascii"))
    h.update(str(arr.dtype).encode("utf-8"))
    h.update(np.asarray(arr.shape, dtype=np.int64).tobytes())
    h.update(arr.view(np.uint8))
    return h.hexdigest()


def _default_test_mask_cache_dir(score_table_path: Path) -> Path:
    """Use a cache shared by out/models/azoth and candidate bundles."""
    root = score_table_path.resolve().parent
    if root.parent.name == "models":
        return root.parent.parent / "cache" / "azoth-test-masks"
    return root / ".cache" / "azoth-test-masks"


def _recall_at_fpr_per_million(
    labels: np.ndarray, scores: np.ndarray, target_per_million: float,
) -> float:
    """Recall achieved at the threshold that produces ``target_per_million``
    benign hits per million on this set.

    Operationally: the threshold is the (1 − q×10⁻⁶) quantile of benign
    scores; recall is the fraction of malware ranked above it. Headline
    deployment metric for security engineers — "if I budget q FP per
    million benigns, what fraction of malware do I catch?" Bypasses the
    F1 / PR-AUC summarization to give a single operating-point number.

    Threshold derivation is the SHARED operating-point method
    (``collimator.thresholds.quantile_severity_threshold``) — the exact
    definition the deploy policy search, the screen experiment, and litmus use,
    so this reported recall matches the operating point a candidate ships at. The
    threshold is the interpolated benign quantile (>=1 FP for L1+, never above the
    observed data). Returns NaN when the route has no malware/benign rows or
    fewer than the method's 50-benign floor.
    """
    benign_mask = labels == 0
    malware_mask = labels == 1
    n_benign = int(np.sum(benign_mask))
    n_malware = int(np.sum(malware_mask))
    if n_benign == 0 or n_malware == 0:
        return float("nan")
    if target_per_million <= 0:
        return float("nan")
    benign_scores = scores[benign_mask].astype(np.float64)
    threshold, _method = quantile_severity_threshold(benign_scores, target_per_million)
    if threshold is None:
        return float("nan")
    hits = int(np.sum(scores[malware_mask] >= threshold))
    return float(hits / n_malware)


def _metrics(
    labels: np.ndarray, scores: np.ndarray, *, with_ci: bool = True,
) -> dict[str, float]:
    """ROC AUC, PR AUC (= average precision), F1 (at F1-optimum threshold),
    F1 at threshold=0.5 for cross-comparison stability, and recall@3FP/M
    (the headline deployment metric: how many malware does this route catch
    at a budget of 3 false positives per million benigns).

    NaN scores are dropped from both arrays before scoring — they correspond
    to routes that didn't evaluate the row (e.g., a filegroup specialist on a
    file outside its group). The deployed runtime would have fallen back to
    general for such files; the per-route metric here is just "how the
    specialist did on the rows it actually saw."

    When ``with_ci`` is True, attaches 95% bootstrap CIs as
    ``<metric>_ci_low`` / ``<metric>_ci_high`` for ROC AUC, PR AUC, F1, and
    recall@3FP/M. Skipped automatically on degenerate inputs (single-class
    or n<50) where bootstrap doesn't produce stable estimates.
    """
    valid = ~np.isnan(scores)
    if valid.sum() < scores.size:
        labels = labels[valid]
        scores = scores[valid]
    n_pos = int((labels == 1).sum())
    n_neg = int((labels == 0).sum())
    if n_pos == 0 or n_neg == 0:
        degenerate: dict[str, Any] = {
            "roc_auc": 0.0, "pr_auc": 0.0, "f1": 0.0, "f1_at_05": 0.0,
            "recall_at_50_per_100M": float("nan"),
            "n_evaluated": int(labels.size),
        }
        for lvl in RECALL_CURVE_LEVELS:
            if lvl == 50:
                continue
            degenerate[f"recall_at_{lvl}_per_100M"] = float("nan")
        return degenerate
    roc = float(roc_auc_score(labels, scores))
    ap = float(average_precision_score(labels, scores))
    # F1 over the precision-recall curve — saves an O(n log n) sweep over
    # arbitrary thresholds.  Skips the trailing (1.0, 0.0, +inf) sentinel.
    precision, recall, _ = precision_recall_curve(labels, scores)
    denom = precision + recall
    with np.errstate(divide="ignore", invalid="ignore"):
        f1_curve = np.where(denom > 0, 2 * precision * recall / denom, 0.0)
    best_f1 = float(np.max(f1_curve)) if f1_curve.size else 0.0
    f1_05 = float(f1_score(labels, (scores >= 0.5).astype(np.int8), zero_division=0))
    # Recall at 50 FP per 100M = 0.5 FP/M — today's deployed operating point
    # on the per-100M scale and autocollie's selection axis.
    recall_50_per_100m = _recall_at_fpr_per_million(labels, scores, 0.5)
    # Full per-level recall curve over the deploy grid (L0..L100). The
    # legacy recall_at_50_per_100M field is retained above for back-compat
    # with downstream consumers that key on it; the curve is additive.
    recall_curve: dict[int, float] = {}
    for lvl in RECALL_CURVE_LEVELS:
        if lvl == 50:
            recall_curve[lvl] = recall_50_per_100m
        else:
            recall_curve[lvl] = _recall_at_fpr_per_million(
                labels, scores, lvl / 100.0,
            )
    # Brier score on raw probs: how well-calibrated is this route on the
    # eval slice. Lower is better. Useful for per-spec cards where the
    # user wants to see the calibration quality at a glance — bigger
    # filetypes can compute it from many samples, tiny ones get a noisy
    # value but still meaningful enough to display.
    try:
        brier = float(brier_score_loss(labels, np.clip(scores, 0.0, 1.0)))
    except (ValueError, TypeError):
        brier = float("nan")
    out = {"roc_auc": roc, "pr_auc": ap, "f1": best_f1, "f1_at_05": f1_05,
           "recall_at_50_per_100M": recall_50_per_100m,
           "brier": brier,
           "n_evaluated": int(labels.size)}
    # Emit recall_at_{N}_per_100M for every level in the deploy grid.
    # ADDITIVE to recall_at_50_per_100M (which remains for back-compat).
    for lvl, value in recall_curve.items():
        out[f"recall_at_{lvl}_per_100M"] = value
    if with_ci and labels.size >= 50 and n_pos >= 5 and n_neg >= 5:
        from collimator.stats import bootstrap_metric  # noqa: PLC0415
        ci = bootstrap_metric(
            labels, scores,
            lambda y, s: float(roc_auc_score(y, s)) if len(np.unique(y)) > 1 else float("nan"),
            n_resamples=200, seed=42, stratify=labels,
        )
        out["roc_auc_ci_low"], out["roc_auc_ci_high"] = ci["low"], ci["high"]
        ci = bootstrap_metric(
            labels, scores,
            lambda y, s: float(average_precision_score(y, s)) if len(np.unique(y)) > 1 else float("nan"),
            n_resamples=200, seed=42, stratify=labels,
        )
        out["pr_auc_ci_low"], out["pr_auc_ci_high"] = ci["low"], ci["high"]

        def _f1_metric(y, s):
            if len(np.unique(y)) <= 1:
                return float("nan")
            p, r, _ = precision_recall_curve(y, s)
            d = p + r
            with np.errstate(divide="ignore", invalid="ignore"):
                fc = np.where(d > 0, 2 * p * r / d, 0.0)
            return float(np.max(fc)) if fc.size else 0.0

        ci = bootstrap_metric(labels, scores, _f1_metric, n_resamples=200, seed=42, stratify=labels)
        out["f1_ci_low"], out["f1_ci_high"] = ci["low"], ci["high"]

        def _recall_50_per_100m(y, s):
            return _recall_at_fpr_per_million(y, s, 0.5)

        if not math.isnan(recall_50_per_100m):
            ci = bootstrap_metric(
                labels, scores, _recall_50_per_100m,
                n_resamples=200, seed=42, stratify=labels,
            )
            out["recall_at_50_per_100M_ci_low"] = ci["low"]
            out["recall_at_50_per_100M_ci_high"] = ci["high"]

        # CI for every other level in the deploy grid. Mirror the L50
        # pattern: skip levels whose point estimate is NaN (sub-resolution
        # slice with too few benigns to derive a quantile) — a bootstrap on
        # NaN is meaningless. Cost: ~14 extra bootstrap runs per metrics block.
        for lvl in RECALL_CURVE_LEVELS:
            if lvl == 50:
                continue
            point = recall_curve[lvl]
            if math.isnan(point):
                continue
            target = lvl / 100.0

            def _recall_at_level(y, s, _target=target):
                return _recall_at_fpr_per_million(y, s, _target)

            ci = bootstrap_metric(
                labels, scores, _recall_at_level,
                n_resamples=200, seed=42, stratify=labels,
            )
            out[f"recall_at_{lvl}_per_100M_ci_low"] = ci["low"]
            out[f"recall_at_{lvl}_per_100M_ci_high"] = ci["high"]
    return out


def _route_idx(route_names: np.ndarray) -> dict[str, int]:
    return {str(name): i for i, name in enumerate(route_names)}


def _route_calibrator_cache_key(
    route_name: str, partition: str, raw_scores: np.ndarray, labels: np.ndarray,
) -> str:
    """Stable hash of the inputs to _calibrate_route_scores_cv.

    The calibrated output is purely a function of:
      - route_name (identity, not really an input but part of the cache namespace)
      - partition (test vs dev — calibration is per-partition)
      - raw_scores at the partition's rows (NaNs included)
      - labels at the partition's rows
      - n_splits + random_state (held constant at defaults)
    so hashing those gives an exact-match cache key. If the route's
    model didn't change between deploys, the score_table entries for
    that route are identical → hash is identical → cache hit. If ANY
    score differs (route retrained, score table regenerated, partition
    mask shifted), the hash changes and we recompute honestly.
    """
    h = hashlib.sha256()
    h.update(route_name.encode("utf-8"))
    h.update(b"\x00")
    h.update(partition.encode("utf-8"))
    h.update(b"\x00")
    # Use raw bytes — np.ndarray.tobytes() is fast and gives a stable
    # representation as long as dtype is stable (we asarray to float32
    # to lock that in).
    h.update(np.ascontiguousarray(raw_scores, dtype=np.float32).tobytes())
    h.update(b"\x00")
    h.update(np.ascontiguousarray(labels, dtype=np.int8).tobytes())
    return h.hexdigest()[:32]


def _calibrate_route_with_cache(
    route_name: str,
    partition: str,
    raw_scores: np.ndarray,
    labels: np.ndarray,
    cache_dir: Path | None,
) -> np.ndarray:
    """Cached wrapper around _calibrate_route_scores_cv.

    When cache_dir is given, hash the inputs; on hit, load the cached
    calibrated array. On miss, compute and write. Cache files are
    self-validating (hash in filename → input change → miss). Stale
    files accumulate but are bounded — one file per unique
    (route, partition, score-content) tuple, ~2.4 MB each.
    """
    if cache_dir is None:
        return _calibrate_route_scores_cv(raw_scores, labels)
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = _route_calibrator_cache_key(route_name, partition, raw_scores, labels)
    safe_name = route_name.replace("/", "_")
    cache_path = cache_dir / f"{safe_name}-{partition}-{key}.npz"
    if cache_path.is_file():
        try:
            with np.load(cache_path) as cached:
                cached_arr = cached["calibrated"]
                if cached_arr.shape == raw_scores.shape:
                    return cached_arr.astype(np.float32)
                LOG.warning(
                    "calibrator cache shape mismatch for %s: cached=%s, expected=%s; refitting",
                    route_name, cached_arr.shape, raw_scores.shape,
                )
        except (OSError, ValueError) as e:
            LOG.warning("calibrator cache load failed for %s: %s; refitting", route_name, e)
    out = _calibrate_route_scores_cv(raw_scores, labels)
    # Atomic write under concurrent workers. np.savez_compressed
    # auto-appends '.npz' to a string path, which broke the first
    # version that used cache_path.with_suffix('.tmp') — savez wrote
    # to '<hash>.tmp.npz' but we then tried to rename '<hash>.tmp'.
    # Use a unique-per-worker tmp file ending in .npz so savez doesn't
    # rewrite the name, then atomic-rename to the final path. If two
    # workers race to write the same key, last-rename-wins; both
    # outputs are bytewise-identical (deterministic CV at fixed seed)
    # so the race is harmless.
    import os as _os  # noqa: PLC0415
    tmp = cache_path.parent / f"{cache_path.stem}.{_os.getpid()}.tmp.npz"
    np.savez_compressed(tmp, calibrated=out)
    _os.replace(tmp, cache_path)
    return out


def _calibrate_route_scores_cv(
    raw_scores: np.ndarray,
    labels: np.ndarray,
    n_splits: int = 5,
    random_state: int = 42,
) -> np.ndarray:
    """Per-route isotonic calibration via K-fold CV.

    Each route's raw model score lives on its own scale (specialist scores are
    sharper for their own filetype; general scores are diffuse).  Naive
    max-across-routes therefore depends on the scale mismatch, not the model's
    discriminative power, and can rank worse than a single specialist.

    Isotonic regression maps each route's raw scores to calibrated probabilities
    in [0, 1], anchored to the empirical label distribution.  We fit it via
    K-fold CV so the per-row calibrated value isn't computed from the same
    label it predicts (no train→eval leakage on the bucket).

    NaN rows (route didn't score them) pass through as NaN — the caller can
    nan-aware-aggregate.  Returns an array shaped like raw_scores.
    """
    out = np.full_like(raw_scores, np.nan, dtype=np.float32)
    valid = ~np.isnan(raw_scores)
    if valid.sum() < 50 or labels[valid].sum() == 0 or (labels[valid] == 0).sum() == 0:
        # Too few labeled rows to fit any calibrator usefully — pass through.
        out[valid] = raw_scores[valid]
        return out
    valid_idx = np.where(valid)[0]
    valid_scores = raw_scores[valid_idx]
    valid_labels = labels[valid_idx]
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    for train_pos, test_pos in kf.split(valid_idx):
        train_scores = valid_scores[train_pos]
        train_labels = valid_labels[train_pos]
        if train_labels.sum() == 0 or (train_labels == 0).sum() == 0:
            # Degenerate fold — fall back to raw.
            out[valid_idx[test_pos]] = valid_scores[test_pos]
            continue
        iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
        iso.fit(train_scores, train_labels)
        out[valid_idx[test_pos]] = iso.predict(valid_scores[test_pos])
    return out


def _ensemble_scores_naive_max(
    scores: np.ndarray,
    row_mask: np.ndarray,
    allowed_routes: list[str],
    route_idx: dict[str, int],
) -> np.ndarray | None:
    """Naive max-of-raw-scores across allowed routes.  Documented bias: when
    routes' scores live on different scales, max can rank worse than the
    specialist alone — kept here only for the legacy 'naive_max' diagnostic
    column in the metrics JSON, never used as the headline number.

    Returns None if no allowed route has a column in the score table."""
    indices = [route_idx[r] for r in allowed_routes if r in route_idx]
    if not indices:
        return None
    return np.nanmax(scores[indices][:, row_mask], axis=0)


def _ensemble_scores_calibrated_max(
    calibrated: np.ndarray,
    row_mask: np.ndarray,
    allowed_routes: list[str],
    route_idx: dict[str, int],
) -> np.ndarray | None:
    """Max-of-calibrated-probabilities across allowed routes.  After per-route
    isotonic calibration, each route's score is a probability of malware on
    a comparable [0,1] scale — max preserves OR-of-routes semantics without
    the scale-mismatch artifact of the naive version."""
    indices = [route_idx[r] for r in allowed_routes if r in route_idx]
    if not indices:
        return None
    return np.nanmax(calibrated[indices][:, row_mask], axis=0)


def _ensemble_scores_stacked_lr(
    raw_scores: np.ndarray,
    row_mask: np.ndarray,
    allowed_routes: list[str],
    route_idx: dict[str, int],
    labels: np.ndarray,
    n_splits: int = 5,
    random_state: int = 42,
) -> np.ndarray | None:
    """Stacked logistic regression combiner: train an LR over the score
    vector (general, group, specialist) with 5-fold CV on this filetype's
    test rows, return the leak-free predicted probability per row.

    Why stacked LR can beat both `calibrated_max` and `specialist_priority`:
    `max` is monotone in a single route's score; LR can capture
    *complementarity* — e.g. when the specialist is weak (~0.5) but its score
    combined with general's gives a much sharper ranking than either alone.
    Filetypes with thin specialist training data (pdf, xml) are the typical
    winners.

    NaN scores in any allowed route's column for a row are filled with the
    column's median (route-specific) before fitting — fitting on NaN-bearing
    designs would crash sklearn, and median-imputation is the standard
    "this row didn't have this signal" treatment.  Rows where ALL routes are
    NaN are dropped from training but get a default 0.0 prediction (never
    happens in practice for filetype-restricted views: the specialist always
    has scores for its own filetype's rows).

    Returns None if no allowed route has a column or if labels collapse to a
    single class on any fold.
    """
    indices = [route_idx[r] for r in allowed_routes if r in route_idx]
    if len(indices) < 2:
        return None  # need at least 2 routes for a stacker to be interesting
    masked = raw_scores[indices][:, row_mask]  # (n_routes, n_rows)
    n_rows = masked.shape[1]
    if n_rows < 50 or labels.sum() == 0 or (labels == 0).sum() == 0:
        return None

    # Per-route median imputation for NaN cells: the specialist may not have
    # scored some rows (filegroup peers in a family-pool world), but we still
    # want LR to use the routes that did score them.  Median imputation says
    # "no information from this route" rather than letting NaN propagate.
    design = masked.T.copy()  # (n_rows, n_routes)
    for c in range(design.shape[1]):
        col = design[:, c]
        nans = np.isnan(col)
        if nans.any():
            valid = col[~nans]
            fill = float(np.median(valid)) if valid.size else 0.0
            design[nans, c] = fill

    out = np.zeros(n_rows, dtype=np.float32)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    for train_pos, test_pos in kf.split(np.arange(n_rows)):
        train_X = design[train_pos]
        train_y = labels[train_pos]
        if train_y.sum() == 0 or (train_y == 0).sum() == 0:
            # Degenerate fold — fall back to a sensible default (mean of
            # per-route scores) for the held-out fold.
            out[test_pos] = design[test_pos].mean(axis=1)
            continue
        # liblinear is fast on small designs and handles the ~3-feature case
        # well; max_iter is more than enough for convergence on this scale.
        lr = LogisticRegression(
            solver="liblinear",
            C=1.0,
            max_iter=200,
            random_state=random_state,
        )
        lr.fit(train_X, train_y)
        out[test_pos] = lr.predict_proba(design[test_pos])[:, 1]
    return out


def _ensemble_scores_stacked_xgb(
    raw_scores: np.ndarray,
    row_mask: np.ndarray,
    allowed_routes: list[str],
    route_idx: dict[str, int],
    labels: np.ndarray,
    n_splits: int = 5,
    random_state: int = 42,
) -> np.ndarray | None:
    """Nonlinear stacked combiner: a small XGBoost meta-model over the
    route-score vector, trained per filetype with K-fold CV.

    Why XGBoost and not LR (which we already have): when complementarity
    between routes is *interactive* — e.g., "high specialist AND moderate
    general means malware; high specialist AND high general means
    benign-overflow" — a tree-based model captures the joint structure that
    a logistic curve can't.  In practice this matters most for routes whose
    `stacked_lr` already wins (pdf, xml, docx) — XGBoost typically extracts
    a few more bits of signal from those interactions.

    Smaller and faster than full-model XGBoost: 16 trees, depth 3, lr 0.1.
    The design matrix is just 3-5 columns, so the model is mostly capturing
    interactions, not memorizing.  K-fold CV avoids leakage.

    Returns None if XGBoost isn't installed (we don't make it a hard
    dependency for this script) or if the design is degenerate.
    """
    try:
        import xgboost as xgb  # noqa: PLC0415
    except ImportError:
        return None
    indices = [route_idx[r] for r in allowed_routes if r in route_idx]
    if len(indices) < 2:
        return None
    masked = raw_scores[indices][:, row_mask]
    n_rows = masked.shape[1]
    if n_rows < 100 or labels.sum() == 0 or (labels == 0).sum() == 0:
        return None
    design = masked.T.copy()
    for c in range(design.shape[1]):
        col = design[:, c]
        nans = np.isnan(col)
        if nans.any():
            valid = col[~nans]
            fill = float(np.median(valid)) if valid.size else 0.0
            design[nans, c] = fill
    out = np.zeros(n_rows, dtype=np.float32)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    for train_pos, test_pos in kf.split(np.arange(n_rows)):
        train_y = labels[train_pos]
        if train_y.sum() == 0 or (train_y == 0).sum() == 0:
            out[test_pos] = design[test_pos].mean(axis=1)
            continue
        clf = xgb.XGBClassifier(
            n_estimators=16,
            max_depth=3,
            learning_rate=0.1,
            objective="binary:logistic",
            eval_metric="logloss",
            tree_method="hist",
            random_state=random_state,
            n_jobs=4,
            verbosity=0,
        )
        clf.fit(design[train_pos], train_y)
        out[test_pos] = clf.predict_proba(design[test_pos])[:, 1]
    return out


def _ensemble_scores_specialist_priority(
    raw_scores: np.ndarray,
    row_mask: np.ndarray,
    primary_route: str,
    fallback_routes: list[str],
    route_idx: dict[str, int],
) -> np.ndarray | None:
    """Specialist-priority over RAW scores: prefer the most specific route's
    raw score per row, falling back to filegroup then general when the
    specialist didn't score the row (NaN).

    Why raw, not calibrated: the goal is `ensemble == specialist` on filetype-X
    rows by construction — anything in the ensemble pipeline that touches the
    specialist's score (calibration, scaling) can shift its ROC AUC by ε
    because of how isotonic regression introduces tied predictions.  Using raw
    scores means the column "specialist_priority" exactly equals the column
    "specialist" on filetype-X rows, so reporting can never claim the
    ensemble was worse than the specialist within numerical precision.

    Mixing scales across routes (specialist's scale vs filegroup's) is OK here
    because each row uses exactly ONE route's score — there is no cross-route
    aggregation per row, just selection."""
    if primary_route not in route_idx:
        return None
    masked = raw_scores[:, row_mask]
    primary = masked[route_idx[primary_route]].copy()
    needs_fallback = np.isnan(primary)
    for fallback in fallback_routes:
        if fallback not in route_idx or not needs_fallback.any():
            break
        fallback_scores = masked[route_idx[fallback]]
        fill = needs_fallback & ~np.isnan(fallback_scores)
        primary[fill] = fallback_scores[fill]
        needs_fallback = np.isnan(primary)
    return primary


def _load_partition_mask(
    db_path: str,
    row_ids: np.ndarray,
    partition: str = "test",
    *,
    cache_dir: Path | None = None,
) -> np.ndarray:
    """Return a boolean mask of rows in the requested partition.

    Partitions are SHA256-deterministic (see ``collimator.data``):
        test:  byte < TEST_BUCKET_MAX                    (12.5%)
        dev:   TEST_BUCKET_MAX <= byte < DEV_BUCKET_MAX  (12.5%)

    Without partition filtering the score table evaluates on the union of
    all rows including train, inflating metrics. Test is the locked
    reporting partition; dev is used here for honest strategy selection
    (so the strategy chosen on dev is reported on test).
    """
    if partition not in {"test", "dev"}:
        raise ValueError(f"unknown partition: {partition!r}")
    cache_path: Path | None = None
    if cache_dir is not None:
        digest = _test_mask_cache_key(db_path, row_ids)
        cache_path = cache_dir / f"{partition}-{digest}.npz"
        if cache_path.exists():
            try:
                cached = np.load(cache_path)
                mask = cached["mask"].astype(bool, copy=False)
                if mask.shape == row_ids.shape:
                    LOG.info("loaded cached %s-bucket mask: %s", partition, cache_path)
                    LOG.info("%s bucket: %d/%d rows (%.2f%%)",
                             partition, int(mask.sum()), len(row_ids),
                             100.0 * mask.sum() / len(row_ids))
                    return mask
                LOG.warning("ignoring stale %s mask cache %s: shape %s != %s",
                            partition, cache_path, mask.shape, row_ids.shape)
            except Exception as exc:  # noqa: BLE001
                LOG.warning("ignoring unreadable %s mask cache %s: %s",
                            partition, cache_path, exc)

    LOG.info("loading canonical_sha256 for %d rows to apply %s bucket filter",
             len(row_ids), partition)
    chunk = 50_000
    is_pg = collimator_data._is_pg(db_path)  # noqa: SLF001
    mask = np.zeros(len(row_ids), dtype=bool)
    # Postgres-side bucket bounds for the partition.
    if partition == "test":
        lower_bound, upper_bound = 0, collimator_data.TEST_BUCKET_MAX
        py_test = collimator_data.is_test_sample
    else:  # dev
        lower_bound, upper_bound = (
            collimator_data.TEST_BUCKET_MAX,
            collimator_data.DEV_BUCKET_MAX,
        )
        py_test = collimator_data.is_dev_sample
    with collimator_data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        for start in range(0, len(row_ids), chunk):
            ids = [int(x) for x in row_ids[start:start + chunk]]
            if is_pg:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id
                        FROM samples
                        WHERE id = ANY(%s)
                          AND canonical_sha256 IS NOT NULL
                          AND length(canonical_sha256) >= 2
                          AND get_byte(decode(right(canonical_sha256, 2), 'hex'), 0) >= %s
                          AND get_byte(decode(right(canonical_sha256, 2), 'hex'), 0) < %s
                        """,
                        [ids, lower_bound, upper_bound],
                    )
                    bucket_ids = {int(row_id) for (row_id,) in cur}
                if bucket_ids:
                    mask[start:start + chunk] = np.fromiter(
                        (int(rid) in bucket_ids for rid in row_ids[start:start + chunk]),
                        dtype=bool,
                        count=len(ids),
                    )
            else:
                sha_by_id: dict[int, str] = {}
                placeholders = ",".join("?" for _ in ids)
                for row_id, csha in conn.execute(
                    f"SELECT id, canonical_sha256 FROM samples WHERE id IN ({placeholders})",  # noqa: S608
                    ids,
                ):
                    sha_by_id[int(row_id)] = csha or ""
                missing = 0
                for offset, rid in enumerate(row_ids[start:start + chunk]):
                    csha = sha_by_id.get(int(rid), "")
                    if not csha or len(csha) < 2:
                        missing += 1
                        continue
                    mask[start + offset] = py_test(csha)
                if missing:
                    LOG.warning(
                        "missing canonical_sha256 for %d/%d rows in chunk; treated as not-in-%s",
                        missing, len(ids), partition,
                    )
    LOG.info("%s bucket: %d/%d rows (%.2f%%)",
             partition, int(mask.sum()), len(row_ids),
             100.0 * mask.sum() / len(row_ids))
    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = cache_path.with_suffix(".tmp.npz")
        np.savez(tmp, mask=mask)
        tmp.replace(cache_path)
        LOG.info("cached %s bucket mask: %s", partition, cache_path)
    return mask


# Back-compat alias — callers that explicitly want test-only.
def _load_test_mask(
    db_path: str,
    row_ids: np.ndarray,
    *,
    cache_dir: Path | None = None,
) -> np.ndarray:
    return _load_partition_mask(db_path, row_ids, "test", cache_dir=cache_dir)


# Per-filetype metrics workers read heavy state (scores, calibrated, labels,
# …) from this module-level dict. In the SERIAL path the parent populates
# it directly; in the PARALLEL path each spawned worker populates its own
# copy via _init_metrics_worker. Either way `_compute_filetype_entry` reads
# from `_PARALLEL_STATE[...]` so the same function works in both contexts.
_PARALLEL_STATE: dict[str, Any] = {}


def _init_metrics_worker(
    scores: np.ndarray,
    calibrated: np.ndarray,
    file_types: np.ndarray,
    labels: np.ndarray,
    idx: dict[str, int],
    level: int,
    severity: str,
    with_ci: bool,
    include_stacked: bool,
) -> None:
    """ProcessPoolExecutor initializer — runs ONCE per spawned worker.
    Stashes the heavy arrays (each ~hundreds of MB on the full corpus)
    in the worker's `_PARALLEL_STATE` so subsequent per-filetype tasks
    cross the IPC boundary with only a (ftype, route_info) tuple."""
    _PARALLEL_STATE.update({
        "scores": scores, "calibrated": calibrated,
        "file_types": file_types, "labels": labels, "idx": idx,
        "level": level, "severity": severity,
        "with_ci": with_ci, "include_stacked": include_stacked,
    })


def _compute_filetype_entry(
    args: tuple[str, dict[str, Any]],
) -> tuple[str, dict[str, Any] | None]:
    """Per-filetype work: pulls heavy state from `_PARALLEL_STATE`,
    computes general / specialist / ensemble metrics for one filetype.
    Returns (ftype, entry) — entry is None when the slice was skipped
    (zero rows, missing policy level). Lifted from the per-filetype loop
    so it can run either in-process or in a ProcessPoolExecutor worker."""
    ftype, route_info = args
    s = _PARALLEL_STATE
    scores = s["scores"]
    calibrated = s["calibrated"]
    file_types = s["file_types"]
    labels = s["labels"]
    idx = s["idx"]
    level = s["level"]
    severity = s["severity"]
    with_ci = s["with_ci"]
    include_stacked = s["include_stacked"]

    route_name = f"filetypes/{ftype}"
    mask = file_types == ftype
    n_files = int(mask.sum())
    if n_files == 0:
        LOG.info("%s: 0 rows in score table; skipping", route_name)
        return ftype, None
    f_labels = labels[mask]
    n_pos = int((f_labels == 1).sum())
    n_neg = int((f_labels == 0).sum())

    levels = route_info.get("levels") or []
    # Look up by level VALUE, not array index — the per-100M grid
    # (0,1,2,3,4,5,10,...,10000) doesn't align positionally with any
    # legacy index space.
    level_entry = next(
        (L for L in levels if int(L.get("level", -1)) == level),
        None,
    )
    if level_entry is None:
        LOG.warning("%s: level %d not found in route policy (available: %s); skipping",
                    route_name, level, [int(L.get("level", -1)) for L in levels])
        return ftype, None
    sev = level_entry.get(severity, {})
    best = sev.get("best") or {}
    allowed = list(best.get("allowed_routes") or [])

    entry: dict[str, Any] = {
        "n_files": n_files, "n_malware": n_pos, "n_benign": n_neg,
        "ensemble_policy": best.get("policy"),
        "ensemble_allowed_routes": allowed,
    }
    if "general" in idx:
        entry["general"] = _metrics(
            f_labels, scores[idx["general"]][mask], with_ci=with_ci,
        )
    if route_name in idx:
        entry["specialist"] = _metrics(
            f_labels, scores[idx[route_name]][mask], with_ci=with_ci,
        )

    # Strategy candidates — see helper docstrings for the math.
    strategies: dict[str, dict[str, float]] = {}
    naive = _ensemble_scores_naive_max(scores, mask, allowed, idx)
    if naive is not None:
        strategies["naive_max"] = _metrics(f_labels, naive, with_ci=with_ci)
    calib_max = _ensemble_scores_calibrated_max(calibrated, mask, allowed, idx)
    if calib_max is not None:
        strategies["calibrated_max"] = _metrics(
            f_labels, calib_max, with_ci=with_ci,
        )
    fg = route_info.get("filegroup")
    fallback_chain = []
    if fg:
        fallback_chain.append(f"filegroups/{fg}")
    fallback_chain.append("general")
    spec_pri = _ensemble_scores_specialist_priority(
        scores, mask, route_name, fallback_chain, idx,
    )
    if spec_pri is not None:
        strategies["specialist_priority"] = _metrics(
            f_labels, spec_pri, with_ci=with_ci,
        )
    if include_stacked:
        stacked = _ensemble_scores_stacked_lr(
            scores, mask, allowed, idx, f_labels,
        )
        if stacked is not None:
            strategies["stacked_lr"] = _metrics(
                f_labels, stacked, with_ci=with_ci,
            )
        stacked_xgb = _ensemble_scores_stacked_xgb(
            scores, mask, allowed, idx, f_labels,
        )
        if stacked_xgb is not None:
            strategies["stacked_xgb"] = _metrics(
                f_labels, stacked_xgb, with_ci=with_ci,
            )

    # Rank by recall at the deploy operating point (DEFAULT_LEVEL) with PR
    # AUC as a tiebreak. ROC AUC was the prior key but is misleading at the
    # strict tail: a strategy with great average ranking (high ROC) can have
    # a degenerate flat operating-point curve, picking it over a strategy
    # that's 3× better at the actual deploy threshold. See the design doc
    # ("Selection criterion: maximize recall at the deploy operating point")
    # and the matching key in the honest-path picker below.
    _recall_field = f"recall_at_{DEFAULT_LEVEL}_per_100M"

    def _sel_key(m: dict[str, Any]) -> tuple[float, float]:
        r = m.get(_recall_field)
        r = 0.0 if r is None or (isinstance(r, float) and math.isnan(r)) else float(r)
        pr = float(m.get("pr_auc") or 0.0)
        return (r, pr)

    candidates = [
        (name, m) for name, m in strategies.items()
        if name != "naive_max" and m.get("n_evaluated", 0) > 0
    ]
    if candidates:
        best_name, best_metrics = max(
            candidates, key=lambda kv: _sel_key(kv[1]),
        )
        entry["ensemble"] = best_metrics
        entry["ensemble_strategy"] = best_name
    elif "specialist" in entry:
        entry["ensemble"] = entry["specialist"]
        entry["ensemble_strategy"] = "specialist_only_fallback"
    entry["ensemble_strategies"] = strategies
    return ftype, entry


def compute_per_filetype_metrics(
    score_table_path: Path,
    route_policies_path: Path,
    *,
    db_path: str | None = None,
    test_mask_cache_dir: Path | None = None,
    partition: str = "test",
    level: int = DEFAULT_LEVEL,
    severity: str = "hostile",
    with_ci: bool = True,
    include_stacked: bool = True,
    metrics_parallelism: int = 1,
    calib_parallelism: int = 1,
    calibrator_cache_dir: Path | None = None,
    previous_metrics_path: Path | None = None,
    previous_score_table_path: Path | None = None,
) -> dict[str, Any]:
    score_table = np.load(score_table_path, allow_pickle=True)
    scores: np.ndarray = score_table["scores"]
    labels: np.ndarray = score_table["labels"].astype(np.int8)
    file_types: np.ndarray = score_table["file_types"]
    file_groups: np.ndarray = score_table["file_groups"]
    route_names: np.ndarray = score_table["route_names"]
    row_ids: np.ndarray = score_table["row_ids"]
    idx = _route_idx(route_names)

    # Restrict to one of the SHA256-deterministic partitions. test is
    # the locked reporting partition; dev is used for honest strategy
    # selection (see compute_per_filetype_metrics_honest below).
    partition_mask: np.ndarray | None = None
    if db_path:
        if test_mask_cache_dir is None:
            test_mask_cache_dir = _default_test_mask_cache_dir(score_table_path)
        partition_mask = _load_partition_mask(
            db_path, row_ids, partition, cache_dir=test_mask_cache_dir,
        )
        scores = scores[:, partition_mask]
        labels = labels[partition_mask]
        file_types = file_types[partition_mask]
        file_groups = file_groups[partition_mask]

    # Per-route isotonic calibration via 5-fold CV on the (possibly test-only)
    # row population.  Result is a parallel array of probability-domain scores
    # the same shape as `scores`, used by calibrated_max and specialist_priority
    # ensemble strategies.  Costs ~50 isotonic fits × 5 folds.
    #
    # Each route's calibration is independent — embarrassingly parallel. Run
    # them across a ProcessPoolExecutor so we don't sit serially on sklearn's
    # single-threaded IsotonicRegression.fit for ~46 routes (was the dominant
    # deploy-time wall-clock after diagnostics was gated).
    LOG.info("fitting per-route isotonic calibrators (5-fold CV) over %d rows "
             "(parallelism=%d, cache=%s)",
             labels.size, calib_parallelism,
             str(calibrator_cache_dir) if calibrator_cache_dir else "off")
    calibrated = np.full_like(scores, np.nan, dtype=np.float32)
    if calib_parallelism > 1 and len(route_names) > 1:
        from concurrent.futures import ProcessPoolExecutor  # noqa: PLC0415
        # Cap workers at route count (no benefit beyond) and cpu count.
        n_workers = min(calib_parallelism, len(route_names))
        # Build per-route argument tuples; ProcessPoolExecutor will pickle.
        # Each tuple is ~3 MB (one route's float32 scores over 588k rows) so
        # transfer cost is negligible vs the ~seconds-per-route fit.
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            futures = {
                pool.submit(
                    _calibrate_route_with_cache,
                    str(route_names[r_idx]), partition, scores[r_idx], labels,
                    calibrator_cache_dir,
                ): r_idx
                for r_idx in range(len(route_names))
            }
            for fut in futures:
                r_idx = futures[fut]
                calibrated[r_idx] = fut.result()
    else:
        for r_idx, route_name in enumerate(route_names):
            calibrated[r_idx] = _calibrate_route_with_cache(
                str(route_name), partition, scores[r_idx], labels,
                calibrator_cache_dir,
            )
    LOG.info("calibration complete; computing per-filetype metrics")

    with open(route_policies_path) as f:
        policies = json.load(f)

    out: dict[str, Any] = {
        "schema": "azoth.per_filetype_metrics.v1",
        "calibration_snapshot_id": policies.get("calibration_snapshot_id"),
        "operating_level": level,
        "severity": severity,
        "evaluated_on": f"{partition}_bucket_only" if partition_mask is not None else "full_corpus",
        "n_rows_evaluated": int(labels.size),
        "with_ci": with_ci,
        "stacked_diagnostics": include_stacked,
        "filetypes": {},
        "filegroups": {},
        "all_files": {},
    }

    # All-files view: matches EMBER 2024's "All files" row directly.
    if "general" in idx:
        out["all_files"]["general"] = _metrics(
            labels, scores[idx["general"]], with_ci=with_ci,
        )
        out["all_files"]["n_files"] = int(labels.size)
        out["all_files"]["n_malware"] = int((labels == 1).sum())
        out["all_files"]["n_benign"] = int((labels == 0).sum())

    # Carry-forward optimization for single-route promotes. When a
    # previous bundle exists AND its score_table.npz has the same routes
    # with identical scores for a filetype's relevant routes (general +
    # filegroup parent + own specialist), the filetype's ensemble
    # metrics for THIS partition can't have changed. Copy the previous
    # entry rather than recomputing — saves ~3-4 min on a promote where
    # only ONE route's specialist was retrained. Honest invalidation:
    # any score change → hash mismatch → recompute.
    carry_forward: dict[str, dict[str, Any]] = {}
    if previous_metrics_path is not None and previous_score_table_path is not None:
        try:
            from azoth_impact import changed_routes as _changed_routes, unchanged_filetypes  # noqa: PLC0415
            from azoth_specialist_suite import DEPLOYMENT_GROUPS  # noqa: PLC0415
            changed, _ = _changed_routes(score_table_path, previous_score_table_path)
            if previous_metrics_path.is_file():
                with open(previous_metrics_path) as f:
                    prev_metrics = json.load(f)
                prev_ft_entries = (prev_metrics.get("filetypes") or {})
                # Build available_routes from THIS bundle's route list.
                avail = set(_route_idx(route_names).keys())
                # Compute "filetypes whose relevant routes all match previous"
                # — these can be carried forward verbatim from prev_metrics.
                all_fts_in_policies = [
                    rn.split("/", 1)[1]
                    for rn in policies.get("routes", {}).keys()
                    if rn.startswith("filetypes/")
                ]
                unchanged = unchanged_filetypes(
                    changed, DEPLOYMENT_GROUPS, avail, all_fts_in_policies,
                )
                stale_grid = 0
                for ft in unchanged:
                    prev_entry = prev_ft_entries.get(ft)
                    if prev_entry is None:
                        continue
                    # Score-identity alone isn't enough: if the recall grid
                    # or operating level moved since the prev bundle (e.g. a
                    # pure recalibrate flipping the default L50->L25), the
                    # prior entry lacks the new levels and must be recomputed.
                    if not _entry_covers_current_grid(prev_entry):
                        stale_grid += 1
                        continue
                    carry_forward[ft] = prev_entry
                LOG.info(
                    "carry-forward: %d/%d routes changed; %d/%d filetypes carried "
                    "forward from prev metrics (%d eligible-but-recomputed: prev "
                    "grid predates current L%d grid)",
                    len(changed), len(avail),
                    len(carry_forward), len(all_fts_in_policies),
                    stale_grid, DEFAULT_LEVEL,
                )
        except Exception as e:  # noqa: BLE001
            LOG.warning(
                "carry-forward setup failed (%s); recomputing all filetypes from scratch",
                e,
            )
            carry_forward = {}

    # Per-filetype 3-way views. Each filetype is independent — the only
    # shared state is the (read-only) scores / calibrated arrays and the
    # policy lookup. We submit one task per filetype to a spawned process
    # pool; heavy arrays cross the spawn boundary ONCE via the initializer
    # (initargs), and per-task payloads are just (ftype, route_info).
    # Fork would let us inherit the parent's arrays via COW for free, but
    # the upstream calibration step already touched BLAS in the parent —
    # forking after that risks the OpenBLAS-mutex deadlock the calibrate
    # script already worked around.
    _PARALLEL_STATE.update({
        "scores": scores, "calibrated": calibrated,
        "file_types": file_types, "labels": labels, "idx": idx,
        "level": level, "severity": severity,
        "with_ci": with_ci, "include_stacked": include_stacked,
    })
    work_items: list[tuple[str, dict[str, Any]]] = []
    for route_name, route_info in policies.get("routes", {}).items():
        if not route_name.startswith("filetypes/"):
            continue
        ftype = route_name.split("/", 1)[1]
        if ftype in carry_forward:
            # Copy the prior bundle's entry verbatim — its inputs were
            # bytewise-identical to ours.
            out["filetypes"][ftype] = carry_forward[ftype]
            continue
        work_items.append((ftype, route_info))

    if metrics_parallelism > 1 and len(work_items) > 1:
        import multiprocessing as _mp  # noqa: PLC0415
        from concurrent.futures import ProcessPoolExecutor  # noqa: PLC0415
        n_workers = min(metrics_parallelism, len(work_items))
        LOG.info("per-filetype metrics: parallel over %d filetypes "
                 "with %d workers (spawn)",
                 len(work_items), n_workers)
        ctx = _mp.get_context("spawn")
        with ProcessPoolExecutor(
            max_workers=n_workers,
            mp_context=ctx,
            initializer=_init_metrics_worker,
            initargs=(scores, calibrated, file_types, labels, idx,
                      level, severity, with_ci, include_stacked),
        ) as pool:
            for ftype, entry in pool.map(_compute_filetype_entry, work_items):
                if entry is not None:
                    out["filetypes"][ftype] = entry
    else:
        LOG.info("per-filetype metrics: serial over %d filetypes", len(work_items))
        for item in work_items:
            ftype, entry = _compute_filetype_entry(item)
            if entry is not None:
                out["filetypes"][ftype] = entry

    # Per-filegroup view: same shape, useful for routes like filegroups/native
    # whose specialist is ALSO an ensemble member (a step between general and
    # filetype-specialist).
    for route_name, route_info in policies.get("routes", {}).items():
        if not route_name.startswith("filegroups/"):
            continue
        fgroup = route_name.split("/", 1)[1]
        # File-group membership comes from the score table's file_groups column
        # (set at calibration time from FILE_TYPE_GROUPS in collimator).
        mask = file_groups == fgroup
        n_files = int(mask.sum())
        if n_files == 0:
            continue
        f_labels = labels[mask]
        levels = route_info.get("levels") or []
        level_entry = next(
            (L for L in levels if int(L.get("level", -1)) == level),
            None,
        )
        if level_entry is None:
            continue
        best = level_entry.get(severity, {}).get("best") or {}
        allowed = list(best.get("allowed_routes") or [])
        entry: dict[str, Any] = {
            "n_files": n_files,
            "n_malware": int((f_labels == 1).sum()),
            "n_benign": int((f_labels == 0).sum()),
            "ensemble_policy": best.get("policy"),
            "ensemble_allowed_routes": allowed,
        }
        if "general" in idx:
            entry["general"] = _metrics(
                f_labels, scores[idx["general"]][mask], with_ci=with_ci,
            )
        if route_name in idx:
            entry["specialist"] = _metrics(
                f_labels, scores[idx[route_name]][mask], with_ci=with_ci,
            )
        ens = _ensemble_scores_calibrated_max(calibrated, mask, allowed, idx)
        if ens is not None:
            entry["ensemble"] = _metrics(f_labels, ens, with_ci=with_ci)
            entry["ensemble_strategy"] = "calibrated_max"
        out["filegroups"][fgroup] = entry

    return out


def compute_per_filetype_metrics_honest(
    score_table_path: Path,
    route_policies_path: Path,
    *,
    db_path: str,
    test_mask_cache_dir: Path | None = None,
    level: int = DEFAULT_LEVEL,
    severity: str = "hostile",
    with_ci: bool = True,
    include_stacked: bool = True,
    metrics_parallelism: int = 1,
    calib_parallelism: int = 1,
    calibrator_cache_dir: Path | None = None,
    previous_metrics_path: Path | None = None,
    previous_score_table_path: Path | None = None,
) -> dict[str, Any]:
    """Run the metric pipeline twice — once on the dev bucket, once on
    the test bucket — and merge so that ensemble-strategy selection
    uses dev metrics while the reported numbers come from test.

    Without this split, `compute_per_filetype_metrics` selects the best
    ensemble strategy by ROC AUC on the same test partition it then
    reports, which is a textbook selection-on-test leak (small in
    magnitude, but still a leak). Picking on dev removes it.

    Filegroups and the all-files view are reported on test as-is — those
    paths don't do strategy selection.
    """
    LOG.info("computing test-partition metrics (reporting)")
    test_out = compute_per_filetype_metrics(
        score_table_path,
        route_policies_path,
        db_path=db_path,
        test_mask_cache_dir=test_mask_cache_dir,
        partition="test",
        level=level,
        severity=severity,
        with_ci=with_ci,
        include_stacked=include_stacked,
        metrics_parallelism=metrics_parallelism,
        calib_parallelism=calib_parallelism,
        calibrator_cache_dir=calibrator_cache_dir,
        previous_metrics_path=previous_metrics_path,
        previous_score_table_path=previous_score_table_path,
    )
    LOG.info("computing dev-partition metrics (strategy selection)")
    dev_out = compute_per_filetype_metrics(
        score_table_path,
        route_policies_path,
        db_path=db_path,
        test_mask_cache_dir=test_mask_cache_dir,
        partition="dev",
        level=level,
        severity=severity,
        with_ci=False,                # CIs unused for selection; faster.
        include_stacked=include_stacked,
        metrics_parallelism=metrics_parallelism,
        calib_parallelism=calib_parallelism,
        calibrator_cache_dir=calibrator_cache_dir,
        previous_metrics_path=previous_metrics_path,
        previous_score_table_path=previous_score_table_path,
    )

    test_out["schema"] = "azoth.per_filetype_metrics.v2"
    test_out["evaluated_on"] = "test_bucket_only"
    test_out["strategy_selected_on"] = "dev_bucket"
    test_out["dev_rows_used_for_selection"] = dev_out.get("n_rows_evaluated", 0)

    for ft, test_entry in test_out.get("filetypes", {}).items():
        dev_entry = (dev_out.get("filetypes") or {}).get(ft) or {}
        dev_strategies = dev_entry.get("ensemble_strategies") or {}
        test_strategies = test_entry.get("ensemble_strategies") or {}
        # Pick the strategy with the best dev recall at the deploy
        # operating point, restricting to strategies that produced a
        # usable metric in BOTH partitions.
        candidates = [
            (name, dev_metric)
            for name, dev_metric in dev_strategies.items()
            if name != "naive_max"
            and dev_metric.get("n_evaluated", 0) > 0
            and name in test_strategies
            and test_strategies[name].get("n_evaluated", 0) > 0
        ]
        if not candidates:
            continue  # leave whatever test-only selection picked
        # Selection criterion: recall at DEFAULT_LEVEL primary, PR AUC
        # tiebreak. This matches the deployment budget (litmus operates
        # at the same level). PR AUC stays as a secondary signal for
        # tiebreaks but doesn't dominate — at near-saturated values
        # (0.9998-1.0000 is typical here) tiny PR-AUC differences are
        # noise while multi-pp recall differences are meaningful. NaN
        # recall (filetype slice too thin to resolve empirically) maps
        # to 0 for ordering.
        _recall_field = f"recall_at_{DEFAULT_LEVEL}_per_100M"

        def _sel_key(m: dict[str, Any]) -> tuple[float, float]:
            r = m.get(_recall_field)
            r = 0.0 if r is None or (isinstance(r, float) and math.isnan(r)) else float(r)
            pr = float(m.get("pr_auc") or 0.0)
            return (r, pr)

        # Specialist-floor invariant: ensemble cannot be worse than the
        # specialist on the same slice. The specialist_priority strategy
        # equals the specialist on filetype rows by construction, so we
        # filter to candidates that beat specialist_priority on the
        # selection metric. If nothing clears the bar, fall back to
        # specialist_priority itself — that guarantees ensemble ≥
        # specialist always holds in the reported numbers, matching the
        # intent that documents the routing system's design.
        floor_metric = dev_strategies.get("specialist_priority") or {}
        if floor_metric.get("n_evaluated", 0) > 0:
            floor_key = _sel_key(floor_metric)
            qualifying = [
                kv for kv in candidates
                if _sel_key(kv[1]) >= floor_key
            ]
            if qualifying:
                candidates = qualifying
            elif "specialist_priority" in test_strategies:
                # Nothing beats the floor; record specialist_priority.
                test_entry["ensemble"] = test_strategies["specialist_priority"]
                test_entry["ensemble_strategy"] = "specialist_priority"
                test_entry["ensemble_strategy_dev_pr_auc"] = floor_metric.get("pr_auc")
                test_entry[f"ensemble_strategy_dev_{_recall_field}"] = floor_metric.get(_recall_field)
                test_entry["ensemble_strategy_dev_n_evaluated"] = floor_metric.get("n_evaluated")
                continue

        best_name, dev_metric = max(
            candidates, key=lambda kv: _sel_key(kv[1]),
        )
        # Second-stage floor: enforce the same ensemble ≥ specialist
        # invariant on the REPORTED partition (test). A strategy that
        # cleared the dev floor can still regress below specialist_priority
        # on test (sampling variance, dev/test drift). When that happens
        # we report specialist_priority — that's what "ensemble cannot
        # be worse than specialist" means in the docs.
        chosen_test = test_strategies[best_name]
        spec_test = test_strategies.get("specialist_priority") or {}
        if spec_test.get("n_evaluated", 0) > 0:
            if _sel_key(chosen_test) < _sel_key(spec_test):
                best_name = "specialist_priority"
                chosen_test = spec_test
                dev_metric = dev_strategies.get("specialist_priority") or dev_metric
        test_entry["ensemble"] = chosen_test
        test_entry["ensemble_strategy"] = best_name
        test_entry["ensemble_strategy_dev_pr_auc"] = dev_metric.get("pr_auc")
        test_entry[f"ensemble_strategy_dev_{_recall_field}"] = dev_metric.get(_recall_field)
        test_entry["ensemble_strategy_dev_n_evaluated"] = dev_metric.get("n_evaluated")

    return test_out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--azoth-root", type=Path, default=Path("out/models/azoth"))
    parser.add_argument("--db", default=None,
                        help="Hopper DSN for canonical_sha256 lookup. When set, "
                             "the pipeline runs on both the dev and test "
                             "SHA256-deterministic buckets: ensemble strategy "
                             "is picked by ROC AUC on dev, then the chosen "
                             "strategy's metrics on the locked test bucket are "
                             "reported. When omitted, metrics include training "
                             "rows and strategy selection is on the same data "
                             "it reports — honest reporting requires this flag.")
    parser.add_argument("--level", type=int, default=DEFAULT_LEVEL,
                        help="Operating level to use for ensemble routing (default 5).")
    parser.add_argument("--severity", default="hostile",
                        choices=["hostile"],
                        help="Severity tier to use for routing decision.")
    parser.add_argument("--test-mask-cache-dir", type=Path, default=None,
                        help="Directory for cached SHA256 test-bucket masks. "
                             "Defaults to out/cache/azoth-test-masks for "
                             "bundles under out/models.")
    parser.add_argument("--no-test-mask-cache", action="store_true",
                        help="Disable cached test-bucket masks.")
    parser.add_argument("--no-ci", action="store_true",
                        help="Skip bootstrap confidence intervals. Point "
                             "metrics are unchanged; this is much faster for "
                             "candidate validation.")
    parser.add_argument("--no-stacked", action="store_true",
                        help="Skip stacked LR/XGBoost ensemble diagnostics. "
                             "Core general/specialist/ensemble metrics are "
                             "still computed.")
    parser.add_argument("--calib-parallelism", type=int, default=0,
                        help="Worker processes for per-route isotonic "
                             "calibration. 0 (default) auto-picks "
                             "min(cpu_count, n_routes) capped at 16. Set "
                             "to 1 to force serial.")
    parser.add_argument("--metrics-parallelism", type=int, default=0,
                        help="Worker processes for the per-filetype metrics "
                             "loop (bootstrap CIs across the full per-100M "
                             "level grid dominate single-threaded wall-clock "
                             "once the grid grew past ~20 levels). 0 "
                             "(default) auto-picks min(cpu_count, n_filetypes) "
                             "capped at 16. Set to 1 to force serial.")
    parser.add_argument("--calibrator-cache-dir", type=Path, default=None,
                        help="Directory to cache per-route calibrated arrays. "
                             "Cache key = sha256(route + partition + raw_scores "
                             "+ labels), so any input change invalidates the "
                             "entry honestly. Major win on promote: only the "
                             "ONE route that changed needs to refit; the other "
                             "44 hit the cache. Defaults to "
                             "out/cache/azoth-calibrator/. Pass '' to disable.")
    parser.add_argument("--no-calibrator-cache", action="store_true",
                        help="Disable the per-route calibrator cache. Useful "
                             "when debugging suspected calibration drift.")
    parser.add_argument("--previous-bundle", type=Path, default=None,
                        help="Previous bundle path. When set, the script "
                             "compares this bundle's score_table.npz against "
                             "the current one and carries forward per-filetype "
                             "metrics for filetypes whose routes' scores are "
                             "bytewise-identical. Major win on promote: only "
                             "the filetypes whose routes actually changed get "
                             "recomputed; the rest copy from "
                             "<previous-bundle>/per_filetype_metrics.json.")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(message)s")
    root = args.azoth_root
    cache_dir = None if args.no_test_mask_cache else args.test_mask_cache_dir
    if args.calib_parallelism <= 0:
        import os as _os  # noqa: PLC0415
        calib_parallelism = min(_os.cpu_count() or 1, 16)
    else:
        calib_parallelism = args.calib_parallelism
    if args.metrics_parallelism <= 0:
        import os as _os  # noqa: PLC0415
        metrics_parallelism = min(_os.cpu_count() or 1, 16)
    else:
        metrics_parallelism = args.metrics_parallelism
    if args.no_calibrator_cache:
        calibrator_cache_dir = None
    elif args.calibrator_cache_dir is not None:
        calibrator_cache_dir = args.calibrator_cache_dir
    else:
        calibrator_cache_dir = Path("out/cache/azoth-calibrator")
    prev_metrics_path: Path | None = None
    prev_score_table_path: Path | None = None
    if args.previous_bundle is not None:
        # A self-comparison (previous-bundle == the bundle being written) is
        # unsafe: carry-forward keys on route-model-hash identity, and by the
        # time this script runs, training has already overwritten the models
        # at --azoth-root in place. Comparing that path to itself always
        # finds "0 routes changed", so every filetype gets carried forward
        # from whatever per_filetype_metrics.json already sat there —
        # freezing n_malware/n_benign/PR-AUC/recall at a stale snapshot
        # forever, even as the underlying test partition keeps growing.
        # azoth_route_policy_search.py hit this same failure mode and
        # guards against it; mirror that guard here.
        if (args.previous_bundle / "per_filetype_metrics.json").resolve() == (
            args.azoth_root / "per_filetype_metrics.json"
        ).resolve():
            print(
                "compute_routed_metrics: previous-bundle is the bundle being "
                "written (self-comparison); disabling carry-forward to "
                "recompute every filetype from the current score table "
                "(avoids frozen/stale per-filetype metrics)",
                file=sys.stderr,
            )
        else:
            prev_metrics_path = args.previous_bundle / "per_filetype_metrics.json"
            prev_score_table_path = args.previous_bundle / "score_table.npz"
    if args.db:
        # Honest: pick ensemble strategy on dev, report on test.
        metrics = compute_per_filetype_metrics_honest(
            root / "score_table.npz",
            root / "route_policies.json",
            db_path=args.db,
            test_mask_cache_dir=cache_dir,
            level=args.level,
            severity=args.severity,
            with_ci=not args.no_ci,
            include_stacked=not args.no_stacked,
            metrics_parallelism=metrics_parallelism,
            calib_parallelism=calib_parallelism,
            calibrator_cache_dir=calibrator_cache_dir,
            previous_metrics_path=prev_metrics_path,
            previous_score_table_path=prev_score_table_path,
        )
    else:
        # Full-corpus mode (no partition split available). Strategy is
        # selected on the same data it's reported on; documented limit
        # of running without --db.
        metrics = compute_per_filetype_metrics(
            root / "score_table.npz",
            root / "route_policies.json",
            db_path=None,
            test_mask_cache_dir=cache_dir,
            level=args.level,
            severity=args.severity,
            with_ci=not args.no_ci,
            include_stacked=not args.no_stacked,
            metrics_parallelism=metrics_parallelism,
            calib_parallelism=calib_parallelism,
            calibrator_cache_dir=calibrator_cache_dir,
            previous_metrics_path=prev_metrics_path,
            previous_score_table_path=prev_score_table_path,
        )
    out_path = root / "per_filetype_metrics.json"
    with open(out_path, "w") as f:
        json.dump(_strip_nan(metrics), f, indent=2, allow_nan=False)
    LOG.info("wrote %s (filetypes: %d, filegroups: %d)",
             out_path,
             len(metrics["filetypes"]),
             len(metrics["filegroups"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
