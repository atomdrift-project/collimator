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
- Primary key is ``sampled_test_metrics.recall_at_50_per_100M``,
  the recall at the L50 hostile deploy budget (0.5 FP/M). This is
  the operational metric — what fraction of the slice's malware
  does the model catch at the FP/100M target we actually deploy
  at? Older run JSONs that predate the per-100M emitter fall back
  to ``recall_at_fp_per_million_3``.
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

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from collimator.thresholds import default_recall_per_100M_field  # noqa: E402

LOG = logging.getLogger("azoth_train_best")


# Mirror of azoth_specialist_suite.APPLES_MIN_*_HOLDOUT. Kept in sync by
# convention — both pickers MUST use the same floor so a screen run
# eligible for one is eligible for the other. If you change one,
# change the other.
APPLES_MIN_MALWARE_HOLDOUT: int = 500
APPLES_MIN_BENIGN_HOLDOUT: int = 200


def _op_recall(metrics: dict[str, Any] | None) -> float | None:
    """Operating-point recall for the picker.

    Prefers the canonical per-100M field at the deploy-default level
    (derived from ``DEFAULT_SEVERITY_LEVEL`` via
    ``default_recall_per_100M_field()``); falls back to the legacy
    per-million ``recall_at_fp_per_million_3`` (L3, 3 FP/M) for older
    run JSONs. Returns None when neither field is present or both are
    NaN.
    """
    if not metrics:
        return None
    for key in (default_recall_per_100M_field(), "recall_at_fp_per_million_3"):
        v = metrics.get(key)
        if isinstance(v, (int, float)) and not math.isnan(float(v)):
            return float(v)
    return None

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
    # Retired entries: the audit-trail mechanism for demoting a
    # promoted baseline that later regressed (or was promoted under
    # gates we've since recognized as too lenient). The entry stays
    # in the file with a `retired_at` timestamp so a human can see
    # what was demoted and why (`retired_reason` is informational).
    # Picker treats retired entries as if they didn't exist, falling
    # through to the apples-to-apples screen-run scan or to defaults.
    if entry.get("retired_at"):
        LOG.info(
            "promoted baseline for %s is retired (at=%s, reason=%s); "
            "falling through to fallback picker",
            route, entry.get("retired_at"), entry.get("retired_reason") or "unspecified",
        )
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
           1. ``has_apples_to_apples`` — a run with ``deployed_on_same_data``
              (autocollie's post-screen apples-to-apples baseline; see
              ``azoth_score_deployed.py``) always outranks a legacy run
              without one. Even a slim apples-to-apples win is more
              trustworthy than a big raw-holdout win, because the
              former's metric is on the *same rows* the deployed model
              is also scoring.
           2. ``delta_recall_at_L50`` — when apples-to-apples is
              present: candidate's holdout r@L50 minus the deployed
              model's r@L50 on those same rows. Maximizing this
              ranks "biggest beat over deployed on identical data."
           3. ``recall_at_50_per_100M`` — operational metric matching
              the L50 hostile deploy budget (0.5 FP/M). Tiebreaker
              within apples-to-apples; primary key for legacy runs.
              Falls back to legacy ``recall_at_fp_per_million_3`` for
              older run JSONs.
           4. ``avg_precision`` — curve-summarized PR/recall tradeoff.
           5. ``save_all_seeds`` — prefer multi-seed bundles.
           6. ``timestamp`` — most recent tied run.

         The has_apples gate exists because legacy screen runs are
         brittle: their r@L50 is on the route's small training
         holdout, not the deployed test slice, so a high holdout
         number doesn't reliably translate (observed:
         ``filegroups/native`` AP=0.9999/r@L50=88.89% holdout → 56%
         on test PE slice). When apples-to-apples runs exist they're
         always picked over legacy regardless of raw recall. A
         warning logs when this whole fallback fires so the human
         knows the route needs a promote cycle.

    Runs without ``avg_precision`` are skipped entirely. Runs without
    either ``recall_at_50_per_100M`` or the legacy
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
    best: tuple[bool, float, float, float, bool, str, dict[str, Any]] | None = None
    apples_to_apples_count = 0
    legacy_count = 0
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
        op_val = _op_recall(metrics)
        r_op = op_val if op_val is not None else 0.0
        # Apples-to-apples gate: a screen run is only eligible to win
        # the fallback picker if deployed_on_same_data is populated on
        # a statistically meaningful holdout. Below the floor (see
        # APPLES_MIN_*_HOLDOUT in azoth_specialist_suite), L50 is
        # below the slice's noise floor and even a paired comparison
        # carries no signal. The picker used to break ties on raw r_op
        # across all legacy runs, which is how lucky perfect-recall
        # runs on tiny holdouts beat structurally stronger configs.
        #
        # EXEMPTION: routes that autocollie can't score apples-to-apples
        # by design (general — see routeSupportsSameDataScoring in
        # cmd/autocollie/score_deployed.go) will never have
        # deployed_on_same_data populated. They fall back to legacy
        # r_op ranking. The "tiny holdout" failure mode doesn't apply
        # to general because general sees the whole corpus, not a
        # per-filetype slice — its r_op is on a 100k+ benign holdout
        # where the FP/100M threshold is well above the noise floor.
        route_supports_apples = route.startswith("filetypes/") or route.startswith("filegroups/")
        deployed = run.get("deployed_on_same_data") or {}
        deployed_op = _op_recall(deployed)
        n_mal = deployed.get("n_malware", 0) or 0
        n_ben = deployed.get("n_benign", 0) or 0
        has_apples = (
            deployed_op is not None
            and n_mal >= APPLES_MIN_MALWARE_HOLDOUT
            and n_ben >= APPLES_MIN_BENIGN_HOLDOUT
        )
        if route_supports_apples and not has_apples:
            legacy_count += 1
            continue
        delta_r_op = (r_op - float(deployed_op)) if has_apples else 0.0
        if has_apples:
            apples_to_apples_count += 1
        else:
            legacy_count += 1
        candidate = (
            has_apples,
            delta_r_op,
            r_op,
            float(ap),
            bool(run.get("save_all_seeds")),
            str(run.get("timestamp") or ""),
            run,
        )
        if best is None or candidate[:6] > best[:6]:
            best = candidate
    if best is not None:
        LOG.info(
            "fallback picker for route %s scanned %d apples-to-apples + %d "
            "legacy (skipped) runs; winner delta_r_op=%+.4f r_op=%.4f (L50)",
            route, apples_to_apples_count, legacy_count,
            best[1], best[2],
        )
    elif legacy_count > 0 and (route.startswith("filetypes/") or route.startswith("filegroups/")):
        LOG.warning(
            "fallback picker for route %s scanned %d screen run(s), none "
            "with apples-to-apples on holdout >= %d malware / %d benign; "
            "no override applied — caller will use defaults. Run an "
            "autocollie cycle on this route to generate a trustworthy "
            "baseline.",
            route, legacy_count,
            APPLES_MIN_MALWARE_HOLDOUT, APPLES_MIN_BENIGN_HOLDOUT,
        )
    return best[6] if best is not None else None


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
    parser.add_argument(
        "--runs-dir", type=str,
        default="out/experiments/azoth/runs",
        help=(
            "Directory of autocollie run JSONs to pick from. Pass an "
            "empty string to skip the picker entirely and replay only "
            "the --set values (no historical config injected). Use the "
            "empty form when retraining from Makefile defaults without "
            "autocollie tunings."
        ),
    )
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
             "tools (ad-hoc scripts) the same feature/env settings the deployed "
             "model was trained with. Example: "
             "azoth_train_best.py --exec python scripts/gen_route_extraction_fixture.py --db $DB",
    )
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Empty --runs-dir means "skip the picker, just replay the --set values
    # straight through to make experiment." Used by azoth-publish-train
    # when AZOTH_AUTOCOLLIE_RUNS_DIR="" to retrain from Makefile defaults
    # without any autocollie history.
    runs_dir_str = str(args.runs_dir or "").strip()
    skip_picker = not runs_dir_str
    run: dict[str, Any] | None = None
    if not skip_picker:
        baselines_path = args.promoted_baselines if str(args.promoted_baselines) else None
        run = _select_best_run(Path(runs_dir_str), args.route, baselines_path=baselines_path)
        if run is None:
            LOG.error("no historical run found for route %r in %s", args.route, runs_dir_str)
            return 1
        metrics = run.get("sampled_test_metrics") or {}
        r_op = _op_recall(metrics)
        LOG.info(
            "best for route %s: key=%s recall@L50=%s avg_precision=%.4f save_all=%s idea=%s",
            args.route,
            run.get("experiment_key", "?"),
            f"{r_op:.4f}" if r_op is not None else "?",
            metrics.get("avg_precision", float("nan")),
            bool(run.get("save_all_seeds")),
            run.get("idea", "?"),
        )
    else:
        LOG.info(
            "defaults-only mode for route %s (no --runs-dir): replaying --set "
            "values without autocollie history",
            args.route,
        )

    extra = _parse_extra(args.set)
    extra.setdefault("EXP_ROUTE", args.route)
    if run is not None:
        # Tag the replay so it's distinguishable in run JSONs from the original.
        extra.setdefault("EXP_IDEA", f"{run.get('idea') or 'best'}_replay")
        # Multi-seed averaging on by default for replays — that's the whole point
        # of running this rather than a single-seed retrain.
        extra.setdefault("EXP_SEED_SEARCH_K", "3")
        extra.setdefault("EXP_SAVE_ALL_SEEDS", "1")
    else:
        extra.setdefault("EXP_IDEA", f"{args.route}_defaults")
    env = _resolve_env(run, extra) if run is not None else dict(extra)

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
