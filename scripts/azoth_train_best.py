#!/usr/bin/env python3
"""Replay the highest-F1 historical run for a given route, with multi-seed averaging.

Why this exists
---------------
Autocollie discovers per-route training configs and writes them to
``out/experiments/azoth/runs/<key>.json``.  Without a way to consume those
discoveries from the regular Makefile workflow, every batch retrain (``make
azoth-train``, etc.) reverts to the legacy hardcoded defaults — autocollie's
wins go on the floor.

This script picks the best historical run for the requested route (general or
otherwise), extracts its ``train_config`` + ``feature_env``, and re-runs that
experiment via ``make experiment`` with multi-seed averaging on so the
re-trained model is both *current-best-known-config* and *seed-variance-
reduced*.  It is the natural complement to azoth_specialist_suite.py's new
``--autocollie-best-runs-dir`` flag, which does the same thing for the
specialist suite.

Selection
---------
- Runs are filtered to a target route (default ``general``).
- Primary key is ``sampled_test_metrics.recall_at_fp_per_million_3``,
  the recall at the L3 hostile deploy budget. This is the operational
  metric — what fraction of the slice's malware does the model catch
  at the FP/M target we actually deploy at?
- Ties on operating-point recall break on ``avg_precision`` (curve
  summary), then ``save_all_seeds`` (prefer averaged), then most recent
  ``timestamp`` (replay-stable).
- Selection on ``avg_precision`` alone (the prior behavior) misses
  swaps where two candidates have identical PR AUC but several-fold
  different recall at the deploy budget. Picking on operational metric
  closes that gap.

Usage
-----
::

    .venv/bin/python scripts/azoth_train_best.py \\
        --runs-dir out/experiments/azoth/runs \\
        --route general

Pass ``--print-env`` to dump the resolved ``EXP_*`` env vars without
running anything (useful for piping into ``env -i ... make experiment``).
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

LOG = logging.getLogger("azoth_train_best")

# train_config field -> EXP_* env var the Makefile experiment target accepts.
_TRAIN_CONFIG_TO_EXP_ENV: dict[str, str] = {
    "n_estimators":           "EXP_ESTIMATORS",
    "max_depth":              "EXP_MAX_DEPTH",
    "learning_rate":          "EXP_LEARNING_RATE",
    "num_leaves":             "EXP_NUM_LEAVES",
    "min_child_samples":      "EXP_MIN_CHILD_SAMPLES",
    "min_child_weight":       "EXP_MIN_CHILD_WEIGHT",
    "early_stopping_rounds":  "EXP_EARLY_STOPPING",
    "holdout_fraction":       "EXP_HOLDOUT_FRACTION",
    "subsample":              "EXP_SUBSAMPLE",
    "colsample_bytree":       "EXP_COLSAMPLE_BYTREE",
    "reg_alpha":              "EXP_REG_ALPHA",
    "reg_lambda":             "EXP_REG_LAMBDA",
    "gamma":                  "EXP_GAMMA",
    "beta":                   "EXP_BETA",
    "threshold_mode":         "EXP_THRESHOLD_MODE",
    "threshold_fpr_target":   "EXP_THRESHOLD_FPR_TARGET",
    "hard_negative_fraction": "EXP_HARD_NEGATIVE_FRACTION",
    "hard_negative_weight":   "EXP_HARD_NEGATIVE_WEIGHT",
    "scale_pos_weight_mult":  "EXP_SCALE_POS_WEIGHT_MULT",
    "boosting_type":          "EXP_BOOSTING_TYPE",
    "extra_trees":            "EXP_EXTRA_TREES",
    "n_folds":                "EXP_FOLDS",
}


def _format_env_value(value: Any) -> str:
    """Coerce a Python value to the string form `make experiment` env vars expect."""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, float):
        # Strip trailing zeros / superfluous precision; preserves e.g. 0.05 as "0.05".
        text = f"{value:.10g}"
        return text
    return str(value)


def _load_promoted_baseline(
    baselines_path: Path, runs_dir: Path, route: str,
) -> dict[str, Any] | None:
    """Return the run JSON for a route's promoted baseline, or None.

    ``promoted_baselines.json`` records every route that has passed
    autocollie's screen → confirm → promote chain. The recorded entry
    points at an experiment key whose run JSON sits in ``runs_dir``;
    that run is the authoritative best-known config for the route.

    A promoted baseline has been operationally validated via:
      1. Screen's recall@3FPM-aware gate.
      2. Confirm's K-seed PR-AUC stability check.
      3. Promote's regression check against the deployed bundle.

    So preferring this run over a raw screen-run scan eliminates the
    failure mode where the picker grabs a screen-only candidate that
    looked great on the route's tiny training holdout but degrades the
    deployed slice.
    """
    if not baselines_path.is_file():
        return None
    try:
        with open(baselines_path) as f:
            baselines = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    entry = (baselines.get("routes") or {}).get(route)
    if not isinstance(entry, dict):
        return None
    # Prefer full_train_key (the post-promote full-data replay) but
    # fall back to promote_key when full_train wasn't recorded.
    for key_field in ("full_train_key", "promote_key"):
        key = entry.get(key_field)
        if not isinstance(key, str) or not key:
            continue
        run_path = runs_dir / f"{key}.json"
        if not run_path.is_file():
            continue
        try:
            with open(run_path) as f:
                run = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if run.get("route") == route:
            return run
    return None


def _select_best_run(
    runs_dir: Path, route: str,
    baselines_path: Path | None = None,
) -> dict[str, Any] | None:
    """Pick the historical run for ``route`` most likely to improve the
    deployed ensemble.

    Selection precedence:

      A. **Promoted baseline** (when ``baselines_path`` points at a valid
         ``promoted_baselines.json`` with an entry for the route).
         This run has cleared autocollie's full screen → confirm → promote
         chain, including the regression check against the deployed
         bundle. Always preferred when available — it's the only
         operationally-verified source.

      B. **Best raw screen run** (fallback when no promoted entry).
         Sort key, in priority order:
           1. ``recall_at_fp_per_million_3`` — operational metric matching
              the L3 hostile deploy budget.
           2. ``avg_precision`` — curve-summarized PR/recall tradeoff.
           3. ``save_all_seeds`` — prefer multi-seed bundles.
           4. ``timestamp`` — most recent tied run.

         This path is brittle: screen runs haven't been verified at the
         deploy slice, so the picker may grab configs that look great on
         the route's small training holdout but degrade the test slice
         (observed: ``filegroups/native`` AP=0.9999/r@3FPM=88.89% holdout
         → 56% on test PE slice). A warning is logged when this path
         fires so the human knows the route needs a promote cycle.

    Runs without ``avg_precision`` are skipped entirely. Runs without
    ``recall_at_fp_per_million_3`` get sorted with fallback recall 0.0.
    """
    if baselines_path is not None:
        promoted = _load_promoted_baseline(baselines_path, runs_dir, route)
        if promoted is not None:
            LOG.info(
                "using promoted baseline for route %s (key=%s)",
                route, promoted.get("experiment_key", "?"),
            )
            return promoted
        LOG.warning(
            "no promoted_baselines.json entry for route %s; falling back to "
            "raw screen runs in %s — selection may be brittle. Consider "
            "running an autocollie promote cycle on this route.",
            route, runs_dir,
        )
    if not runs_dir.is_dir():
        LOG.error("runs dir %s does not exist", runs_dir)
        return None
    best: tuple[float, float, bool, str, dict[str, Any]] | None = None
    for path in runs_dir.glob("*.json"):
        if path.name.endswith("_feature_spec.json"):
            continue
        try:
            with open(path) as f:
                run = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if run.get("route") != route:
            continue
        metrics = run.get("sampled_test_metrics") or {}
        ap = metrics.get("avg_precision")
        if not isinstance(ap, (int, float)):
            continue
        recall_at_3 = metrics.get("recall_at_fp_per_million_3")
        if isinstance(recall_at_3, (int, float)) and not math.isnan(float(recall_at_3)):
            r3 = float(recall_at_3)
        else:
            r3 = 0.0
        candidate = (
            r3,
            float(ap),
            bool(run.get("save_all_seeds")),
            str(run.get("timestamp") or ""),
            run,
        )
        if best is None or candidate[:4] > best[:4]:
            best = candidate
    return best[4] if best is not None else None


def _resolve_env(run: dict[str, Any], extra: dict[str, str]) -> dict[str, str]:
    """Build the EXP_*/COLLIMATOR_* env layered as: train_config -> feature_env -> extra (caller wins)."""
    env: dict[str, str] = {}
    for field, value in (run.get("train_config") or {}).items():
        if value is None:
            continue
        exp_name = _TRAIN_CONFIG_TO_EXP_ENV.get(field)
        if exp_name is None:
            continue
        env[exp_name] = _format_env_value(value)
    # min_malware_training_score lives outside train_config in older schemas.
    filters = run.get("filters") or {}
    if "min_malware_training_score" in filters and filters["min_malware_training_score"] is not None:
        env["EXP_MIN_MALWARE_SCORE"] = _format_env_value(filters["min_malware_training_score"])
    # Top-level fields the experiment spec carries explicitly.
    if isinstance(run.get("seed"), int):
        env["SEED"] = _format_env_value(run["seed"])
    spec = run.get("experiment_spec") or {}
    for src_key, env_name in (
        ("train_samples", "EXP_TRAIN_SAMPLES"),
        ("max_test_samples", "EXP_MAX_TEST_SAMPLES"),
        ("seed_search_k", "EXP_SEED_SEARCH_K"),
    ):
        if src_key in spec and spec[src_key] is not None:
            env[env_name] = _format_env_value(spec[src_key])
    # Feature env vars (already in COLLIMATOR_* form).
    for key, value in (run.get("feature_env") or {}).items():
        if str(key).startswith("COLLIMATOR_"):
            env[str(key)] = _format_env_value(value)
    # Caller's last-mile overrides win — used by the Makefile to inject DB,
    # WORKERS, and the multi-seed flags that aren't in the historical spec.
    env.update(extra)
    return env


def _parse_extra(values: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"invalid --set {value!r}; expected KEY=value")
        key, _, raw = value.partition("=")
        key = key.strip()
        if not key:
            raise ValueError(f"invalid --set {value!r}; key is empty")
        out[key] = raw
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", type=Path, default=Path("out/experiments/azoth/runs"))
    parser.add_argument(
        "--promoted-baselines",
        type=Path,
        default=Path("out/models/azoth/.autocollie/promoted_baselines.json"),
        help=(
            "Path to autocollie's promoted_baselines.json. When this file "
            "has an entry for the requested route, the picker uses that "
            "promoted run (verified by screen → confirm → promote) "
            "instead of scanning raw screen runs. Set to '' to disable "
            "and force the legacy raw-screen-runs path."
        ),
    )
    parser.add_argument("--route", default="general")
    parser.add_argument(
        "--set",
        action="append",
        default=[],
        help="Extra KEY=value to inject into the make experiment env (repeatable). "
             "Caller's overrides take precedence over the historical run's spec.",
    )
    parser.add_argument(
        "--print-env",
        action="store_true",
        help="Print resolved env vars one per line and exit; do not invoke make.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the make experiment command without executing it.",
    )
    parser.add_argument(
        "--exec",
        nargs=argparse.REMAINDER,
        default=None,
        help="Instead of invoking `make experiment`, run an arbitrary command "
             "with the resolved env vars in its environment. Use to give other "
             "tools (fixture generators, ad-hoc scripts) the same feature/env "
             "settings the deployed model was trained with. Example: "
             "azoth_train_best.py --exec python -m collimator fixture --db $DB",
    )
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    baselines_path = args.promoted_baselines if str(args.promoted_baselines) else None
    run = _select_best_run(args.runs_dir, args.route, baselines_path=baselines_path)
    if run is None:
        LOG.error("no historical run found for route %r in %s", args.route, args.runs_dir)
        return 1
    metrics = run.get("sampled_test_metrics") or {}
    LOG.info(
        "best for route %s: key=%s recall@3FP/M=%.4f avg_precision=%.4f save_all=%s idea=%s",
        args.route,
        run.get("experiment_key", "?"),
        metrics.get("recall_at_fp_per_million_3", float("nan")),
        metrics.get("avg_precision", float("nan")),
        bool(run.get("save_all_seeds")),
        run.get("idea", "?"),
    )

    extra = _parse_extra(args.set)
    extra.setdefault("EXP_ROUTE", args.route)
    # Tag the replay so it's distinguishable in run JSONs from the original.
    extra.setdefault("EXP_IDEA", f"{run.get('idea') or 'best'}_replay")
    # Multi-seed averaging on by default for replays — that's the whole point
    # of running this rather than a single-seed retrain.
    extra.setdefault("EXP_SEED_SEARCH_K", "3")
    extra.setdefault("EXP_SAVE_ALL_SEEDS", "1")
    env = _resolve_env(run, extra)

    if args.print_env:
        for k in sorted(env):
            print(f"{k}={env[k]}")
        return 0

    if args.exec:
        # Pass-through mode: run an arbitrary command with the resolved env
        # *added to the parent environment*. Used by `make fixture` etc. so
        # downstream Python sees COLLIMATOR_* exactly as if the deployed
        # model's training had set them.
        child_env = os.environ.copy()
        child_env.update(env)
        LOG.info("exec: %s", " ".join(shlex.quote(p) for p in args.exec))
        if args.dry_run:
            return 0
        return subprocess.run(args.exec, env=child_env, check=False).returncode

    cmd = ["make", "experiment"] + [f"{k}={v}" for k, v in sorted(env.items())]
    LOG.info("invoking: %s", " ".join(shlex.quote(p) for p in cmd))
    if args.dry_run:
        return 0
    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
