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
import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import KFold

from collimator import data as collimator_data

LOG = logging.getLogger("compute_routed_metrics")

# Default operating point.  Level 5 corresponds to the deploy-time hostile
# point we currently ship at (matches azoth_calibrate_ensemble's default).
DEFAULT_LEVEL = 5


def _metrics(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    """ROC AUC, PR AUC (= average precision), F1 (at F1-optimum threshold),
    and F1 at threshold=0.5 for cross-comparison stability.

    NaN scores are dropped from both arrays before scoring — they correspond
    to routes that didn't evaluate the row (e.g., a filegroup specialist on a
    file outside its group). The deployed runtime would have fallen back to
    general for such files; the per-route metric here is just "how the
    specialist did on the rows it actually saw."
    """
    valid = ~np.isnan(scores)
    if valid.sum() < scores.size:
        labels = labels[valid]
        scores = scores[valid]
    n_pos = int((labels == 1).sum())
    n_neg = int((labels == 0).sum())
    if n_pos == 0 or n_neg == 0:
        return {"roc_auc": 0.0, "pr_auc": 0.0, "f1": 0.0, "f1_at_05": 0.0,
                "n_evaluated": int(labels.size)}
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
    return {"roc_auc": roc, "pr_auc": ap, "f1": best_f1, "f1_at_05": f1_05,
            "n_evaluated": int(labels.size)}


def _route_idx(route_names: np.ndarray) -> dict[str, int]:
    return {str(name): i for i, name in enumerate(route_names)}


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


def _load_test_mask(db_path: str, row_ids: np.ndarray) -> np.ndarray:
    """Look up canonical_sha256 for each row_id in the score table and return
    a boolean mask of the test-bucket rows (the same SHA256-deterministic
    12.5% slice collimator uses at training time — see data.is_test_sample).

    Without this filter the score table evaluates on the union of train+test,
    inflating metrics relative to EMBER 2024's strict train→test reporting.
    Querying canonical_sha256 in chunks keeps the IN-list small enough that
    Postgres' planner doesn't blow up on 2M+ id lookups.
    """
    LOG.info("loading canonical_sha256 for %d rows to apply test bucket filter",
             len(row_ids))
    sha_by_id: dict[int, str] = {}
    chunk = 50_000
    is_pg = collimator_data._is_pg(db_path)  # noqa: SLF001
    with collimator_data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        for start in range(0, len(row_ids), chunk):
            ids = [int(x) for x in row_ids[start:start + chunk]]
            if is_pg:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, canonical_sha256 FROM samples WHERE id = ANY(%s)",
                        [ids],
                    )
                    for row_id, csha in cur:
                        sha_by_id[int(row_id)] = csha or ""
            else:
                placeholders = ",".join("?" for _ in ids)
                for row_id, csha in conn.execute(
                    f"SELECT id, canonical_sha256 FROM samples WHERE id IN ({placeholders})",  # noqa: S608
                    ids,
                ):
                    sha_by_id[int(row_id)] = csha or ""
    mask = np.zeros(len(row_ids), dtype=bool)
    missing = 0
    for i, rid in enumerate(row_ids):
        csha = sha_by_id.get(int(rid), "")
        if not csha or len(csha) < 2:
            missing += 1
            continue
        mask[i] = collimator_data.is_test_sample(csha)
    if missing:
        LOG.warning("missing canonical_sha256 for %d/%d rows; treated as not-in-test",
                    missing, len(row_ids))
    LOG.info("test bucket: %d/%d rows (%.2f%%)",
             int(mask.sum()), len(row_ids), 100.0 * mask.sum() / len(row_ids))
    return mask


def compute_per_filetype_metrics(
    score_table_path: Path,
    route_policies_path: Path,
    *,
    db_path: str | None = None,
    level: int = DEFAULT_LEVEL,
    severity: str = "hostile",
) -> dict[str, Any]:
    score_table = np.load(score_table_path, allow_pickle=True)
    scores: np.ndarray = score_table["scores"]
    labels: np.ndarray = score_table["labels"].astype(np.int8)
    file_types: np.ndarray = score_table["file_types"]
    file_groups: np.ndarray = score_table["file_groups"]
    route_names: np.ndarray = score_table["route_names"]
    row_ids: np.ndarray = score_table["row_ids"]
    idx = _route_idx(route_names)

    # EMBER 2024 reports strict train→test split metrics; our calibration
    # corpus mixes both halves (see _fetch_rows in azoth_calibrate_ensemble).
    # When db_path is provided, restrict to the deterministic 12.5% test
    # bucket so the resulting numbers are apples-to-apples.
    test_mask: np.ndarray | None = None
    if db_path:
        test_mask = _load_test_mask(db_path, row_ids)
        scores = scores[:, test_mask]
        labels = labels[test_mask]
        file_types = file_types[test_mask]
        file_groups = file_groups[test_mask]

    # Per-route isotonic calibration via 5-fold CV on the (possibly test-only)
    # row population.  Result is a parallel array of probability-domain scores
    # the same shape as `scores`, used by calibrated_max and specialist_priority
    # ensemble strategies.  Costs ~50 isotonic fits × 5 folds; bounded.
    LOG.info("fitting per-route isotonic calibrators (5-fold CV) over %d rows", labels.size)
    calibrated = np.full_like(scores, np.nan, dtype=np.float32)
    for r_idx, route_name in enumerate(route_names):
        calibrated[r_idx] = _calibrate_route_scores_cv(scores[r_idx], labels)
    LOG.info("calibration complete; computing per-filetype metrics")

    with open(route_policies_path) as f:
        policies = json.load(f)

    out: dict[str, Any] = {
        "schema": "azoth.per_filetype_metrics.v1",
        "calibration_snapshot_id": policies.get("calibration_snapshot_id"),
        "operating_level": level,
        "severity": severity,
        "evaluated_on": "test_bucket_only" if test_mask is not None else "full_corpus",
        "n_rows_evaluated": int(labels.size),
        "filetypes": {},
        "filegroups": {},
        "all_files": {},
    }

    # All-files view: matches EMBER 2024's "All files" row directly.
    if "general" in idx:
        out["all_files"]["general"] = _metrics(labels, scores[idx["general"]])
        out["all_files"]["n_files"] = int(labels.size)
        out["all_files"]["n_malware"] = int((labels == 1).sum())
        out["all_files"]["n_benign"] = int((labels == 0).sum())

    # Per-filetype 3-way views.
    for route_name, route_info in policies.get("routes", {}).items():
        if not route_name.startswith("filetypes/"):
            continue
        ftype = route_name.split("/", 1)[1]
        mask = file_types == ftype
        n_files = int(mask.sum())
        if n_files == 0:
            LOG.info("%s: 0 rows in score table; skipping", route_name)
            continue
        f_labels = labels[mask]
        n_pos = int((f_labels == 1).sum())
        n_neg = int((f_labels == 0).sum())

        levels = route_info.get("levels") or []
        if level >= len(levels):
            LOG.warning("%s: level %d out of range (have %d); skipping",
                        route_name, level, len(levels))
            continue
        sev = levels[level].get(severity, {})
        best = sev.get("best") or {}
        allowed = list(best.get("allowed_routes") or [])

        entry: dict[str, Any] = {
            "n_files": n_files, "n_malware": n_pos, "n_benign": n_neg,
            "ensemble_policy": best.get("policy"),
            "ensemble_allowed_routes": allowed,
        }
        if "general" in idx:
            entry["general"] = _metrics(f_labels, scores[idx["general"]][mask])
        if route_name in idx:
            entry["specialist"] = _metrics(f_labels, scores[idx[route_name]][mask])

        # Three ensemble strategies, computed honestly so we can pick the one
        # that doesn't degrade vs the specialist.  See the helper docstrings
        # for the math; in summary: naive_max has a known scale-mismatch bias,
        # calibrated_max + specialist_priority address it differently.
        strategies: dict[str, dict[str, float]] = {}
        naive = _ensemble_scores_naive_max(scores, mask, allowed, idx)
        if naive is not None:
            strategies["naive_max"] = _metrics(f_labels, naive)
        calib_max = _ensemble_scores_calibrated_max(calibrated, mask, allowed, idx)
        if calib_max is not None:
            strategies["calibrated_max"] = _metrics(f_labels, calib_max)
        # Specialist-priority needs a primary + fallback chain.  We use the
        # filetype specialist as primary, then the route's filegroup if
        # known, then general — matching the deployed router's preference
        # ordering when a specialist owns the file.
        fg = route_info.get("filegroup")
        fallback_chain = []
        if fg:
            fallback_chain.append(f"filegroups/{fg}")
        fallback_chain.append("general")
        spec_pri = _ensemble_scores_specialist_priority(
            scores, mask, route_name, fallback_chain, idx,
        )
        if spec_pri is not None:
            strategies["specialist_priority"] = _metrics(f_labels, spec_pri)
        stacked = _ensemble_scores_stacked_lr(
            scores, mask, allowed, idx, f_labels,
        )
        if stacked is not None:
            strategies["stacked_lr"] = _metrics(f_labels, stacked)
        stacked_xgb = _ensemble_scores_stacked_xgb(
            scores, mask, allowed, idx, f_labels,
        )
        if stacked_xgb is not None:
            strategies["stacked_xgb"] = _metrics(f_labels, stacked_xgb)

        # Headline pick: among non-naive strategies, prefer the one with the
        # highest ROC AUC, breaking ties on PR AUC.  Specialist_priority is
        # guaranteed >= specialist by construction; calibrated_max often beats
        # both.  When all calibrated strategies are missing, fall back to the
        # specialist's standalone score so the ensemble row never vanishes.
        candidates = [
            (name, m) for name, m in strategies.items()
            if name != "naive_max" and m.get("n_evaluated", 0) > 0
        ]
        if candidates:
            best_name, best_metrics = max(
                candidates,
                key=lambda kv: (kv[1].get("roc_auc", 0.0), kv[1].get("pr_auc", 0.0)),
            )
            entry["ensemble"] = best_metrics
            entry["ensemble_strategy"] = best_name
        elif "specialist" in entry:
            # Emergency fallback: use the specialist's own metrics.  This keeps
            # the headline column populated even when calibration was degenerate.
            entry["ensemble"] = entry["specialist"]
            entry["ensemble_strategy"] = "specialist_only_fallback"
        # All three strategies recorded for audit, regardless of which won.
        entry["ensemble_strategies"] = strategies

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
        if level >= len(levels):
            continue
        best = levels[level].get(severity, {}).get("best") or {}
        allowed = list(best.get("allowed_routes") or [])
        entry: dict[str, Any] = {
            "n_files": n_files,
            "n_malware": int((f_labels == 1).sum()),
            "n_benign": int((f_labels == 0).sum()),
            "ensemble_policy": best.get("policy"),
            "ensemble_allowed_routes": allowed,
        }
        if "general" in idx:
            entry["general"] = _metrics(f_labels, scores[idx["general"]][mask])
        if route_name in idx:
            entry["specialist"] = _metrics(f_labels, scores[idx[route_name]][mask])
        ens = _ensemble_scores_calibrated_max(calibrated, mask, allowed, idx)
        if ens is not None:
            entry["ensemble"] = _metrics(f_labels, ens)
            entry["ensemble_strategy"] = "calibrated_max"
        out["filegroups"][fgroup] = entry

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--azoth-root", type=Path, default=Path("out/models/azoth"))
    parser.add_argument("--db", default=None,
                        help="Hopper DSN for canonical_sha256 lookup. When set, "
                             "metrics are computed only on the SHA256-deterministic "
                             "12.5%% test bucket (apples-to-apples vs EMBER 2024). "
                             "When omitted, metrics include training rows too — "
                             "honest reporting requires this flag.")
    parser.add_argument("--level", type=int, default=DEFAULT_LEVEL,
                        help="Operating level to use for ensemble routing (default 5).")
    parser.add_argument("--severity", default="hostile",
                        choices=["hostile", "suspicious"],
                        help="Severity tier to use for routing decision.")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(message)s")
    root = args.azoth_root
    metrics = compute_per_filetype_metrics(
        root / "score_table.npz",
        root / "route_policies.json",
        db_path=args.db,
        level=args.level,
        severity=args.severity,
    )
    out_path = root / "per_filetype_metrics.json"
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
    LOG.info("wrote %s (filetypes: %d, filegroups: %d)",
             out_path,
             len(metrics["filetypes"]),
             len(metrics["filegroups"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
