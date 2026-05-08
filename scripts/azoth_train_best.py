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
- Among matching runs we pick the highest ``sampled_test_metrics.f1``;
  ties broken by ``save_all_seeds`` (prefer averaged), then most recent
  ``timestamp`` (replay-stable).

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
    "early_stopping_rounds":  "EXP_EARLY_STOPPING_ROUNDS",
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


def _select_best_run(runs_dir: Path, route: str) -> dict[str, Any] | None:
    """Pick the highest-F1 historical run for ``route``.

    Returns the parsed run dict, or None when no matching run exists. Ties on
    F1 break in favor of save_all_seeds=True then later timestamp — same rule
    azoth_specialist_suite uses for its picker, so the two stay in sync.
    """
    if not runs_dir.is_dir():
        LOG.error("runs dir %s does not exist", runs_dir)
        return None
    best: tuple[float, bool, str, dict[str, Any]] | None = None
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
        f1 = (run.get("sampled_test_metrics") or {}).get("f1")
        if not isinstance(f1, (int, float)):
            continue
        candidate = (
            float(f1),
            bool(run.get("save_all_seeds")),
            str(run.get("timestamp") or ""),
            run,
        )
        if best is None or candidate[:3] > best[:3]:
            best = candidate
    return best[3] if best is not None else None


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
        ("train_samples", "EXP_SAMPLES"),
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


def _idea_for(run: dict[str, Any]) -> str:
    """Replays should be tagged so they're distinguishable from the original run."""
    base = run.get("idea") or "best"
    return f"{base}_replay"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", type=Path, default=Path("out/experiments/azoth/runs"))
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
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    run = _select_best_run(args.runs_dir, args.route)
    if run is None:
        LOG.error("no historical run found for route %r in %s", args.route, args.runs_dir)
        return 1
    LOG.info(
        "best for route %s: key=%s f1=%.4f save_all=%s idea=%s",
        args.route,
        run.get("experiment_key", "?"),
        (run.get("sampled_test_metrics") or {}).get("f1", float("nan")),
        bool(run.get("save_all_seeds")),
        run.get("idea", "?"),
    )

    extra = _parse_extra(args.set)
    extra.setdefault("EXP_ROUTE", args.route)
    extra.setdefault("EXP_IDEA", _idea_for(run))
    # Multi-seed averaging on by default for replays — that's the whole point
    # of running this rather than a single-seed retrain.
    extra.setdefault("EXP_SEED_SEARCH_K", "3")
    extra.setdefault("EXP_SAVE_ALL_SEEDS", "1")
    env = _resolve_env(run, extra)

    if args.print_env:
        for k in sorted(env):
            print(f"{k}={env[k]}")
        return 0

    cmd = ["make", "experiment"] + [f"{k}={v}" for k, v in sorted(env.items())]
    LOG.info("invoking: %s", " ".join(shlex.quote(p) for p in cmd))
    if args.dry_run:
        return 0
    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
