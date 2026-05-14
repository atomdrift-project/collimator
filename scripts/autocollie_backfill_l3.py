#!/usr/bin/env python3
"""Replay autocollie's selected historical baselines to add tail recall metrics.

Older experiment JSONs predate ``recall_at_fp_per_million_*``. Autocollie's
promotion gate can only compare production-tail metrics when both the candidate
and the baseline have those fields, so this script reruns the selected baseline
experiments and copies the refreshed metrics back onto every JSON with the
legacy baseline key. That copy-back matters because key material has drifted
over time, so an equivalent replay may receive a new current-schema key.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

LOG = logging.getLogger("autocollie_backfill_l3")

_TRAIN_CONFIG_TO_MAKE: dict[str, str] = {
    "n_estimators": "EXP_ESTIMATORS",
    "max_depth": "EXP_MAX_DEPTH",
    "learning_rate": "EXP_LEARNING_RATE",
    "early_stopping_rounds": "EXP_EARLY_STOPPING",
    "min_child_weight": "EXP_MIN_CHILD_WEIGHT",
    "min_child_samples": "EXP_MIN_CHILD_SAMPLES",
    "num_leaves": "EXP_NUM_LEAVES",
    "colsample_bytree": "EXP_COLSAMPLE_BYTREE",
    "subsample": "EXP_SUBSAMPLE",
    "gamma": "EXP_GAMMA",
    "reg_alpha": "EXP_REG_ALPHA",
    "reg_lambda": "EXP_REG_LAMBDA",
    "beta": "EXP_BETA",
    "threshold_mode": "EXP_THRESHOLD_MODE",
    "threshold_fpr_target": "EXP_THRESHOLD_FPR_TARGET",
    "hard_negative_fraction": "EXP_HARD_NEGATIVE_FRACTION",
    "hard_negative_weight": "EXP_HARD_NEGATIVE_WEIGHT",
    "scale_pos_weight_mult": "EXP_SCALE_POS_WEIGHT_MULT",
    "boosting_type": "EXP_BOOSTING_TYPE",
    "extra_trees": "EXP_EXTRA_TREES",
    "n_folds": "EXP_FOLDS",
    "holdout_fraction": "EXP_HOLDOUT_FRACTION",
    "device": "DEVICE",
}


def _format(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def _has_l3(run: dict[str, Any]) -> bool:
    metrics = run.get("sampled_test_metrics") or {}
    return (
        "recall_at_fp_per_million_0" in metrics
        and "recall_at_fp_per_million_3" in metrics
    )


def _tail_score(run: dict[str, Any]) -> tuple[bool, float]:
    metrics = run.get("sampled_test_metrics") or {}
    r0 = metrics.get("recall_at_fp_per_million_0")
    r3 = metrics.get("recall_at_fp_per_million_3")
    if isinstance(r0, (int, float)) and isinstance(r3, (int, float)):
        return True, 0.2 * float(r0) + 0.8 * float(r3)
    ap = metrics.get("avg_precision")
    if isinstance(ap, (int, float)):
        return False, float(ap)
    return False, float("-inf")


def _load_runs(runs_dir: Path) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for path in sorted(runs_dir.glob("*.json")):
        if path.name.endswith("_feature_spec.json"):
            continue
        try:
            with open(path) as f:
                run = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(run, dict):
            continue
        run["_path"] = str(path)
        runs.append(run)
    return runs


def _parse_routes(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def _route_allowed(route: str, selectors: list[str]) -> bool:
    if not selectors:
        return True
    for selector in selectors:
        if selector.endswith("/") and route.startswith(selector):
            return True
        if route == selector:
            return True
    return False


def _runs_by_key(runs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_key: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        key = str(run.get("experiment_key") or "")
        if key:
            by_key.setdefault(key, []).append(run)
    return by_key


def _best_copy(runs: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        runs,
        key=lambda r: (
            _tail_score(r)[1],
            str(r.get("timestamp") or ""),
            str(r.get("_path") or ""),
        ),
    )


def _select_baselines(
    runs: list[dict[str, Any]],
    routes: list[str],
    keys: set[str],
    only_missing: bool,
    all_missing: bool,
) -> list[dict[str, Any]]:
    by_key = _runs_by_key(runs)
    if keys:
        missing = sorted(k for k in keys if k not in by_key)
        for key in missing:
            LOG.warning("requested key %s was not found", key)
        candidate_keys = sorted(k for k in keys if k in by_key)
    else:
        best_l3_by_route: dict[str, float] = {}
        for copies in by_key.values():
            representative = _best_copy(copies)
            route = str(representative.get("route") or "")
            if not route or not _route_allowed(route, routes):
                continue
            l3_scores = [_tail_score(copy)[1] for copy in copies if _has_l3(copy)]
            if not l3_scores:
                continue
            score = max(l3_scores)
            best_l3_by_route[route] = max(score, best_l3_by_route.get(route, float("-inf")))

        candidate_keys = []
        for key, copies in by_key.items():
            representative = _best_copy(copies)
            route = str(representative.get("route") or "")
            if route and _route_allowed(route, routes):
                if only_missing and not all_missing and not any(_has_l3(copy) for copy in copies):
                    _, score = _tail_score(representative)
                    best_l3 = best_l3_by_route.get(route)
                    if best_l3 is not None and score < best_l3:
                        continue
                candidate_keys.append(key)
        candidate_keys.sort(key=lambda k: (
            str(_best_copy(by_key[k]).get("route") or ""),
            k,
        ))

    selected: list[dict[str, Any]] = []
    for key in candidate_keys:
        copies = by_key[key]
        if only_missing and any(_has_l3(copy) for copy in copies):
            continue
        selected.append(_best_copy(copies))
    return selected


def _collimator_to_make_map(makefile: Path) -> dict[str, str]:
    text = makefile.read_text()
    mapping: dict[str, str] = {}
    pattern = re.compile(r"^\s*(COLLIMATOR_[A-Z0-9_]+)=\$\(([^)]+)\)", re.MULTILINE)
    for match in pattern.finditer(text):
        mapping[match.group(1)] = match.group(2)
    return mapping


def _run_make_vars(run: dict[str, Any], makefile: Path, db: str, workers: str) -> dict[str, str]:
    spec = run.get("experiment_spec") or {}
    train = run.get("train_config") or {}
    filters = run.get("filters") or {}
    env_map = _collimator_to_make_map(makefile)

    values: dict[str, str] = {
        "DB": db,
        "EXP_RERUN": "1",
        "MODEL": _format(run.get("model_name") or spec.get("model_name") or "azoth"),
        "LEARNER": _format(spec.get("learner") or "azoth"),
        "EXP_ROUTE": _format(run.get("route") or spec.get("route") or "general"),
        "EXP_IDEA": _format(run.get("idea") or "l3_backfill"),
    }
    if workers:
        values["EXP_WORKERS"] = workers
    for src, dst in (
        ("seed", "SEED"),
        ("train_samples", "EXP_TRAIN_SAMPLES"),
        ("max_test_samples", "EXP_MAX_TEST_SAMPLES"),
        ("total_limit", "EXP_TOTAL_LIMIT"),
        ("snapshot_max_id", "EXP_MAX_ID"),
        ("seed_search_k", "EXP_SEED_SEARCH_K"),
        ("save_all_seeds", "EXP_SAVE_ALL_SEEDS"),
        ("test_natural_prevalence", "EXP_TEST_NATURAL_PREVALENCE"),
    ):
        if src in spec:
            values[dst] = _format(spec[src])
    for src, dst in _TRAIN_CONFIG_TO_MAKE.items():
        if src in train:
            values[dst] = _format(train[src])
    if "benign_filetype_weights" in train and isinstance(train["benign_filetype_weights"], dict):
        pairs = [f"{k}={_format(v)}" for k, v in sorted(train["benign_filetype_weights"].items())]
        values["EXP_BENIGN_FILETYPE_WEIGHT"] = ",".join(pairs)
    if "min_malware_training_score" in filters:
        values["EXP_MIN_MALWARE_SCORE"] = _format(filters["min_malware_training_score"])
    drops = filters.get("drop_feature_prefixes")
    if isinstance(drops, list):
        values["DROP_FEATURE_PREFIXES"] = ",".join(str(v) for v in drops)
    monotone = filters.get("monotone_constraints")
    if isinstance(monotone, dict) and monotone:
        values["EXP_MONOTONE_JSON"] = json.dumps(monotone, sort_keys=True, separators=(",", ":"))
    for key, value in (run.get("feature_env") or {}).items():
        make_var = env_map.get(str(key))
        if make_var:
            values[make_var] = _format(value)
    return {k: v for k, v in values.items() if v != ""}


_KEY_RE = re.compile(r"(?:runs/|experiment(?:_key| already exists)?:\s*)([0-9a-f]{16})")


def _run_make_and_capture_key(cmd: list[str]) -> tuple[int, str]:
    found_key = ""
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert proc.stdout is not None
    for line in proc.stdout:
        print(line, end="")
        for match in _KEY_RE.finditer(line):
            found_key = match.group(1)
    return proc.wait(), found_key


def _propagate_refreshed_metrics(runs_dir: Path, source_key: str, target_key: str) -> None:
    keyed_path = runs_dir / f"{source_key}.json"
    if not keyed_path.is_file():
        LOG.warning("expected refreshed keyed JSON %s was not found", keyed_path)
        return
    try:
        with open(keyed_path) as f:
            refreshed = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        LOG.warning("could not read refreshed keyed JSON %s: %s", keyed_path, exc)
        return

    fields = (
        "sampled_test_metrics",
        "seed_search_results",
        "seed_search_winner_index",
        "seed_search_k",
        "save_all_seeds",
    )
    for path in runs_dir.glob("*.json"):
        if path.name.endswith("_feature_spec.json"):
            continue
        try:
            with open(path) as f:
                existing = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if existing.get("experiment_key") != target_key:
            continue
        changed = False
        for field in fields:
            if field in refreshed and existing.get(field) != refreshed[field]:
                existing[field] = refreshed[field]
                changed = True
        if not changed:
            continue
        tmp = path.with_name(f".{path.name}.tmp")
        with open(tmp, "w") as f:
            json.dump(existing, f, indent=2, sort_keys=True)
            f.write("\n")
        tmp.replace(path)
        LOG.info("propagated refreshed L3 metrics to duplicate summary %s", path)


def _propagate_existing_l3(runs_dir: Path, runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Copy L3 metrics from any already-backfilled duplicate to same-key peers."""
    changed = False
    for key, copies in _runs_by_key(runs).items():
        source = next((copy for copy in copies if _has_l3(copy)), None)
        if source is None:
            continue
        source_path = Path(str(source.get("_path") or ""))
        for copy in copies:
            if _has_l3(copy):
                continue
            path = Path(str(copy.get("_path") or ""))
            if not path:
                continue
            refreshed = {k: v for k, v in source.items() if k != "_path"}
            existing = {k: v for k, v in copy.items() if k != "_path"}
            for field in (
                "sampled_test_metrics",
                "seed_search_results",
                "seed_search_winner_index",
                "seed_search_k",
                "save_all_seeds",
            ):
                if field in refreshed:
                    existing[field] = refreshed[field]
            tmp = path.with_name(f".{path.name}.tmp")
            with open(tmp, "w") as f:
                json.dump(existing, f, indent=2, sort_keys=True)
                f.write("\n")
            tmp.replace(path)
            changed = True
            LOG.info("filled duplicate L3 metrics for %s from %s", path, source_path)
    return _load_runs(runs_dir) if changed else runs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", type=Path, default=Path("out/experiments/azoth/runs"))
    parser.add_argument("--makefile", type=Path, default=Path("Makefile"))
    parser.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    parser.add_argument("--workers", default="64")
    parser.add_argument("--routes", default="", help="Comma-separated routes or prefixes, e.g. filetypes/python,filegroups/")
    parser.add_argument("--keys", default="", help="Comma-separated experiment keys to backfill exactly")
    parser.add_argument("--include-existing-l3", action="store_true", help="Rerun selected baselines even if L3 fields already exist")
    parser.add_argument("--all-missing", action="store_true", help="Backfill every missing-L3 key instead of only keys that can affect route baseline selection")
    parser.add_argument("--dry-run", action="store_true", help="Print selected make commands without running them")
    parser.add_argument("--fail-fast", action="store_true", help="Stop at the first failed legacy replay")
    parser.add_argument("--limit", type=int, default=0, help="Maximum selected baselines to replay")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format="%(levelname)s: %(message)s")

    runs = _propagate_existing_l3(args.runs_dir, _load_runs(args.runs_dir))
    selected = _select_baselines(
        runs,
        _parse_routes(args.routes),
        set(_parse_routes(args.keys)),
        only_missing=not args.include_existing_l3,
        all_missing=args.all_missing,
    )
    if args.limit > 0:
        selected = selected[: args.limit]
    if not selected:
        LOG.info("no selected baselines need L3 backfill")
        return 0

    failed: list[tuple[str, int]] = []
    for run in selected:
        key = str(run.get("experiment_key") or "")
        route = str(run.get("route") or "")
        LOG.info("backfilling %s route=%s path=%s", key, route, run.get("_path"))
        make_vars = _run_make_vars(run, args.makefile, args.db, args.workers)
        cmd = ["make", "experiment"] + [f"{k}={v}" for k, v in sorted(make_vars.items())]
        if args.dry_run:
            print(" ".join(cmd))
            continue
        rc, refreshed_key = _run_make_and_capture_key(cmd)
        if rc != 0:
            LOG.error("backfill failed for %s with exit code %d", key, rc)
            failed.append((key, rc))
            if args.fail_fast:
                return rc
            continue
        _propagate_refreshed_metrics(args.runs_dir, refreshed_key or key, key)
    if failed:
        LOG.warning("backfill skipped %d failed legacy baselines: %s",
                    len(failed), ", ".join(f"{key}(exit={rc})" for key, rc in failed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
