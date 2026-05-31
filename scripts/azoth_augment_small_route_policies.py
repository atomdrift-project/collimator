#!/usr/bin/env python3
"""Augment route policies for small-corpus routes by re-calibrating thresholds
against the route's filegroup pool.

Problem this fixes
------------------
A route with N benigns in the calibration corpus has a smallest observable FP
rate of 1/N.  For routes like ``filetypes/msi`` (~18 benigns), that's
55,555 FP/M — orders of magnitude above any sensible operating point, so the
empirical threshold search returns ``no_policy`` at every level even when the
specialist's discrimination is excellent.

This script does a *post-hoc* threshold re-search for routes whose policy at
a given level is ``no_policy``:

  1. Identify the route's filegroup (e.g. ``msi`` → ``native``).
  2. Pull family-pool benigns from hopper (members of the filegroup;
     test bucket only, capped at ``--max-pool-benigns``).
  3. Load the route's specialist + feature spec, featurize and score the
     family-pool benigns.
  4. Re-run the threshold search using the augmented benign pool plus the
     route's own malware (from the score table).  Optionally apply
     Beta-Binomial credible-bound smoothing (from ``thresholds.py``) so the
     selected threshold respects the residual FP-estimation uncertainty.
  5. Write the new threshold back into ``route_policies.json`` with policy
     name ``family_pool_calibrated`` and a ``family_pool`` annotation
     recording the augmented pool size.

Conceptual validity
-------------------
A specialist that's truly sharp on its own filetype should give *low* scores
to its filegroup peers' benigns (otherwise it's overfitting).  Augmenting the
FP-estimation pool with peer benigns therefore tightens the deploy-side FP
guarantee at the cost of slightly stricter thresholds.  When the specialist
*does* mis-fire on peer benigns, the augmented threshold rises — which is
correct: in production the routing layer occasionally mis-routes, and a
calibration that's blind to that is overconfident.

Risks and limits
----------------
- Featurization of large benign pools is expensive.  The default cap of
  100k benigns is ~10 minutes of inference per route (lots of cleave_result
  parsing).  Increase only when you really need finer FP-rate resolution.
- Family-pool calibration assumes the specialist's score behavior on peer
  filetypes is representative of its production behavior.  If a peer is
  wildly out-of-distribution for the specialist, the threshold may be
  conservative beyond what's needed.  ``--family-only`` keeps the pool to
  the route's filegroup; ``--full-corpus`` allows wider augmentation
  (use sparingly; primarily for routes whose family is also small, e.g.
  ``filetypes/rtf`` where the documents filegroup is itself thin).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp

from collimator import bundle, data, features, model, thresholds

sys.path.insert(0, str(Path(__file__).resolve().parent))
from azoth_specialist_suite import DEPLOYMENT_GROUPS  # noqa: E402

LOG = logging.getLogger("azoth_augment_small_route_policies")

# Routes with own-benign count below this threshold get family-pool
# augmentation by default.  At ≥50k benigns, the empirical threshold search
# can resolve FPRs down to ~20 FP/M with reasonable confidence — augmentation
# adds little value.  Below it, the smaller the route, the more help it
# needs.
DEFAULT_AUGMENT_THRESHOLD = 50_000


def _filegroup_for(filetype: str) -> str | None:
    for group, file_types in DEPLOYMENT_GROUPS.items():
        if filetype in file_types:
            return group
    return None


def _own_benign_count(score_table: dict[str, np.ndarray], route_name: str) -> int:
    """Return how many benigns the route has scores for in the score table."""
    route_names = score_table["route_names"]
    labels = score_table["labels"]
    matches = np.where(route_names == route_name)[0]
    if len(matches) == 0:
        return 0
    r_idx = int(matches[0])
    valid = ~np.isnan(score_table["scores"][r_idx])
    return int(((labels == 0) & valid).sum())


def _own_malware_scores(
    score_table: dict[str, np.ndarray],
    route_name: str,
    file_types: list[str],
) -> np.ndarray:
    """Pull the route's own-malware scores from the existing score table.
    Used as the recall-side reference during augmented threshold search."""
    route_names = score_table["route_names"]
    matches = np.where(route_names == route_name)[0]
    if len(matches) == 0:
        return np.array([], dtype=np.float32)
    r_idx = int(matches[0])
    file_types_arr = score_table["file_types"]
    labels = score_table["labels"]
    mask = (
        np.isin(file_types_arr, file_types)
        & (labels == 1)
        & ~np.isnan(score_table["scores"][r_idx])
    )
    return score_table["scores"][r_idx][mask].astype(np.float32)


def _fetch_family_benigns(
    db_path: str,
    *,
    family_filetypes: list[str],
    max_id: int,
    max_pool_benigns: int,
    rng: np.random.Generator,
) -> list[tuple[int, int]]:
    """Fetch test-bucket benigns of the given filetypes from hopper.  Returns
    (row_id, label=0) tuples capped at ``max_pool_benigns`` via reservoir
    sampling so the augmented pool stays bounded even on big filegroups."""
    # Reuse data.stream_partitioned_metadata_grouped: it streams partitioned
    # rows. We sample dev-partition benigns to augment policy search (test
    # remains locked for headline reporting; dev is the held-out slice the
    # policy is allowed to inspect).
    benigns: list[tuple[int, int]] = []
    seen = 0
    for row_id, label, partition, _group_id, _score in data.stream_partitioned_metadata_grouped(
        db_path,
        max_id=max_id,
        file_types=tuple(family_filetypes),
    ):
        if partition != "dev" or label != 0:
            continue
        seen += 1
        if len(benigns) < max_pool_benigns:
            benigns.append((row_id, label))
        else:
            # Reservoir: keep total roughly uniform across the stream.
            j = int(rng.integers(0, seen))
            if j < max_pool_benigns:
                benigns[j] = (row_id, label)
    LOG.info("family pool: sampled %d benigns from %d test-bucket members of %s",
             len(benigns), seen, family_filetypes[:5])
    return benigns


def _score_pool_with_route(
    db_path: str,
    rows: list[tuple[int, int]],
    *,
    feature_spec_path: Path,
    bundle_dir: Path,
    workers: int,
) -> np.ndarray:
    """Featurize and score a row pool with a route's specialist.  Returns a
    1-D array of probabilities aligned to ``rows``.  Loads the route as an
    Ensemble so multi-seed bundles get averaged at predict time, matching
    what litmus emits for the same files."""
    if not rows:
        return np.array([], dtype=np.float32)
    spec = features.FeatureSpec.load(feature_spec_path)
    clf = bundle.Ensemble.load_bundle(bundle_dir)
    LOG.info("featurizing %d rows through %s (%d features, %d seed%s)…",
             len(rows), feature_spec_path.parent.name, spec.total_features,
             clf.n_members, "s" if clf.n_members != 1 else "")
    batches = list(features.extract_labeled_from_db_batches(
        db_path, rows, spec, n_workers=workers,
    ))
    if not batches:
        return np.array([], dtype=np.float32)
    x = sp.vstack([b[0] for b in batches], format="csr")
    return clf.predict_proba(x).astype(np.float32)


def _augment_route(
    *,
    azoth_root: Path,
    db_path: str,
    score_table: dict[str, np.ndarray],
    policies: dict[str, Any],
    route_name: str,
    route_info: dict[str, Any],
    max_pool_benigns: int,
    use_credible_bound: bool,
    workers: int,
    max_id: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Recalibrate one route's no_policy levels.  Returns a stats dict for
    the audit log."""
    stats: dict[str, Any] = {
        "route": route_name,
        "no_policy_levels_before": [],
        "augmented_levels": [],
        "still_no_policy": [],
        "pool_benigns": 0,
    }
    # 1. Identify no_policy levels.
    levels = route_info.get("levels") or []
    no_policy: list[tuple[int, str]] = []
    for level_obj in levels:
        for severity in ("hostile",):
            best = (level_obj.get(severity) or {}).get("best") or {}
            if best.get("policy") == "no_policy":
                no_policy.append((level_obj["level"], severity))
    if not no_policy:
        return stats
    stats["no_policy_levels_before"] = no_policy

    # 2. Resolve filegroup peer pool.
    filetype = route_info.get("filetype")
    filegroup = route_info.get("filegroup") or (_filegroup_for(filetype) if filetype else None)
    if not filegroup:
        LOG.warning("%s: no filegroup mapping; skipping augmentation", route_name)
        stats["still_no_policy"] = no_policy
        return stats
    family_filetypes = list(DEPLOYMENT_GROUPS.get(filegroup, []))
    if not family_filetypes:
        LOG.warning("%s: family %s has no members; skipping", route_name, filegroup)
        stats["still_no_policy"] = no_policy
        return stats

    # 3. Resolve specialist artifacts.
    slot = azoth_root / route_name
    spec_path = slot / "feature_spec.json"
    if not spec_path.exists() or not bundle.has_model(slot):
        LOG.warning("%s: missing %s or no model file; skipping", route_name, spec_path)
        stats["still_no_policy"] = no_policy
        return stats

    # 4. Sample family-pool benigns and score them.
    pool_rows = _fetch_family_benigns(
        db_path,
        family_filetypes=family_filetypes,
        max_id=max_id,
        max_pool_benigns=max_pool_benigns,
        rng=rng,
    )
    pool_scores = _score_pool_with_route(
        db_path, pool_rows,
        feature_spec_path=spec_path, bundle_dir=slot,
        workers=workers,
    )
    stats["pool_benigns"] = len(pool_rows)
    if len(pool_rows) == 0 or pool_scores.size == 0:
        stats["still_no_policy"] = no_policy
        return stats

    # 5. Pull route's own malware scores from the score table for recall side.
    route_filetypes = route_info.get("models")  # not quite — we want the filetypes the specialist owns
    # The route's *own* filetype is the one matching the route's filetype field.
    own_filetypes = [filetype] if filetype else []
    own_malware_scores = _own_malware_scores(score_table, route_name, own_filetypes)
    if own_malware_scores.size == 0:
        LOG.warning("%s: no own-malware scores in score table; skipping", route_name)
        stats["still_no_policy"] = no_policy
        return stats

    # 6. For each no_policy level, run an augmented threshold search.
    combined_scores = np.concatenate([pool_scores, own_malware_scores])
    combined_labels = np.concatenate([
        np.zeros(len(pool_scores), dtype=np.int8),
        np.ones(len(own_malware_scores), dtype=np.int8),
    ])
    # Build threshold sweep arrays once.
    order = np.argsort(combined_scores)[::-1]
    sorted_scores = combined_scores[order]
    sorted_labels = combined_labels[order]
    cum_tp = np.cumsum(sorted_labels == 1).astype(np.int64)
    cum_fp = np.cumsum(sorted_labels == 0).astype(np.int64)
    n_benign = int((combined_labels == 0).sum())
    n_malware = int((combined_labels == 1).sum())
    # Threshold breakpoints: where the score changes.
    change = np.concatenate([np.diff(sorted_scores) != 0, [True]])
    cuts = np.where(change)[0]
    candidate_thresholds = sorted_scores[cuts].astype(np.float64)
    fp_at_cut = cum_fp[cuts]
    tp_at_cut = cum_tp[cuts]
    recall_at_cut = tp_at_cut / max(n_malware, 1)
    fpr_at_cut = fp_at_cut / max(n_benign, 1)

    for level, severity in no_policy:
        target_per_million = (
            (levels[level].get(severity) or {}).get("target_per_million", 0.0)
        )
        if not target_per_million:
            continue
        if use_credible_bound:
            stat_dict = thresholds.select_threshold_at_credible_bound(
                candidate_thresholds, tp_at_cut, fp_at_cut,
                recall_at_cut, fpr_at_cut,
                n_benign, n_malware,
                max_fp_per_million=target_per_million,
            )
        else:
            max_fp = thresholds._fp_budget_for_per_million(n_benign, target_per_million)  # noqa: SLF001
            stat_dict = thresholds._select_threshold_at_fp_budget(  # noqa: SLF001
                candidate_thresholds, tp_at_cut, fp_at_cut,
                recall_at_cut, fpr_at_cut,
                n_benign, n_malware, max_fp=max_fp,
            )
        if stat_dict is None or stat_dict.get("threshold") is None:
            stats["still_no_policy"].append((level, severity))
            continue
        if stat_dict.get("recall", 0.0) <= 0.0:
            # Found a threshold but it doesn't catch anything — equivalent to
            # no_policy in practice; don't replace.
            stats["still_no_policy"].append((level, severity))
            continue

        new_best: dict[str, Any] = {
            "policy": "family_pool_calibrated",
            "primary": route_name,
            "allowed_routes": [route_name],
            "target_per_million": target_per_million,
            "thresholds": {route_name: float(stat_dict["threshold"])},
            "tp": int(stat_dict.get("tp", 0)),
            "fp": int(stat_dict.get("fp", 0)),
            "tn": int(stat_dict.get("tn", 0)),
            "fn": int(stat_dict.get("fn", 0)),
            "recall": float(stat_dict.get("recall", 0.0)),
            "precision": float(stat_dict.get("precision", 0.0)),
            "f1": float(2 * stat_dict.get("recall", 0) * stat_dict.get("precision", 0) /
                       max(stat_dict.get("recall", 0) + stat_dict.get("precision", 0), 1e-9)),
            "fpr": float(stat_dict.get("fpr", 0.0)),
            "fp_per_100M": float(stat_dict.get("fp_per_100M", 0.0)),
            "augmented_pool_size": int(n_benign),
            "augmented_pool_family": filegroup,
            "augmented_pool_filetypes": family_filetypes,
            "augmented_pool_credible_bound_used": use_credible_bound,
        }
        if "credible_bound_fp_rate" in stat_dict:
            new_best["augmented_pool_credible_bound_fp_rate"] = float(
                stat_dict["credible_bound_fp_rate"]
            )
        levels[level][severity]["best"] = new_best
        stats["augmented_levels"].append((level, severity))
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--azoth-root", type=Path, default=Path("out/models/azoth"))
    parser.add_argument("--db", required=True)
    parser.add_argument("--max-pool-benigns", type=int, default=100_000,
                        help="Cap on family-pool benigns per route (default 100k).")
    parser.add_argument("--augment-threshold-benigns", type=int, default=DEFAULT_AUGMENT_THRESHOLD,
                        help="Routes with own-benign count below this get augmented "
                             f"(default {DEFAULT_AUGMENT_THRESHOLD}).")
    parser.add_argument("--use-credible-bound", action="store_true",
                        help="Apply Beta-Binomial upper-credible-bound smoothing to "
                             "the threshold search (recommended for very small pools).")
    parser.add_argument("--workers", type=int, default=8,
                        help="Workers for feature extraction.")
    parser.add_argument("--only-routes", action="append", default=[],
                        help="Restrict augmentation to these routes (repeatable). "
                             "Useful for smoke-testing or recalibrating one route.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dry-run", action="store_true",
                        help="Identify augmentable routes but don't modify the policy file.")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(levelname)s %(name)s: %(message)s")

    rng = np.random.default_rng(args.seed)
    policy_path = args.azoth_root / "route_policies.json"
    score_table_path = args.azoth_root / "score_table.npz"
    if not policy_path.exists() or not score_table_path.exists():
        LOG.error("missing %s or %s", policy_path, score_table_path)
        return 1

    with open(policy_path) as f:
        policies = json.load(f)
    score_table = dict(np.load(score_table_path, allow_pickle=True))
    max_id = int(policies.get("snapshot_max_id") or score_table.get("max_id", 0) or 0)
    if max_id == 0:
        # Try reading from config.json if not in policies.
        try:
            with open(args.azoth_root / "config.json") as f:
                cfg = json.load(f)
            max_id = int(cfg.get("snapshot_max_id") or 0)
        except FileNotFoundError:
            pass
    if max_id == 0:
        LOG.warning("no snapshot_max_id available; benign sampling will use current DB state")

    # Identify candidates: routes with small own-benign counts AND any no_policy
    # level AND actual specialist artifacts on disk.  Skip large routes
    # (own benigns ≥ threshold) — they don't need help.  Skip empty slots
    # (no trained model) — those are placeholder routes from older calibration
    # and there's nothing to score the augmented pool with.
    candidates: list[tuple[str, dict[str, Any]]] = []
    skipped_no_artifacts = 0
    for route_name, route_info in policies.get("routes", {}).items():
        own_benigns = _own_benign_count(score_table, route_name)
        if own_benigns >= args.augment_threshold_benigns:
            continue
        if own_benigns == 0:
            # Route never produced calibration scores → no own-malware reference
            # for the threshold search.  Augmentation is pointless without it.
            continue
        # Specialist artifacts must exist on disk.
        slot = args.azoth_root / route_name
        if not bundle.has_model(slot) or not (slot / "feature_spec.json").exists():
            skipped_no_artifacts += 1
            continue
        # Has any no_policy level?
        any_no_policy = any(
            (lvl.get("hostile") or {}).get("best", {}).get("policy") == "no_policy"
            for lvl in (route_info.get("levels") or [])
        )
        if any_no_policy:
            candidates.append((route_name, route_info))
    if skipped_no_artifacts:
        LOG.info("skipped %d routes with no model file / feature_spec.json", skipped_no_artifacts)
    if args.only_routes:
        wanted = set(args.only_routes)
        candidates = [c for c in candidates if c[0] in wanted]
        LOG.info("--only-routes filter: kept %d", len(candidates))

    LOG.info("found %d candidate routes for augmentation:", len(candidates))
    for route_name, info in candidates:
        own = _own_benign_count(score_table, route_name)
        LOG.info("  %s (own benigns=%d, filegroup=%s)",
                 route_name, own, info.get("filegroup", "?"))
    if args.dry_run:
        LOG.info("dry run; exiting without modifying policy file")
        return 0
    if not candidates:
        LOG.info("no augmentation needed; exiting cleanly")
        return 0

    # 7. Run augmentation per candidate.
    started = time.perf_counter()
    audit: list[dict[str, Any]] = []
    for route_name, route_info in candidates:
        LOG.info("augmenting %s …", route_name)
        try:
            stats = _augment_route(
                azoth_root=args.azoth_root,
                db_path=args.db,
                score_table=score_table,
                policies=policies,
                route_name=route_name,
                route_info=route_info,
                max_pool_benigns=args.max_pool_benigns,
                use_credible_bound=args.use_credible_bound,
                workers=args.workers,
                max_id=max_id,
                rng=rng,
            )
        except Exception as exc:  # noqa: BLE001
            LOG.exception("%s: augmentation crashed: %s", route_name, exc)
            stats = {"route": route_name, "error": str(exc)}
        audit.append(stats)
        LOG.info("  %s: augmented %d/%d levels (pool=%d benigns)",
                 route_name,
                 len(stats.get("augmented_levels") or []),
                 len(stats.get("no_policy_levels_before") or []),
                 stats.get("pool_benigns", 0))

    # 8. Write back.
    with open(policy_path, "w") as f:
        json.dump(policies, f, indent=2)
    audit_path = args.azoth_root / "small_route_augmentation.json"
    with open(audit_path, "w") as f:
        json.dump({"audit": audit, "duration_s": time.perf_counter() - started}, f, indent=2)
    LOG.info("wrote augmented policies to %s; audit at %s (%.1fs total)",
             policy_path, audit_path, time.perf_counter() - started)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
