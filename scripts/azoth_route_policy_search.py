#!/usr/bin/env python3
"""Search route-owned azoth policies from a persisted score table."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import UTC, datetime
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
        "fp_per_million": fp * 1_000_000.0 / n_benign if n_benign else math.nan,
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


def _choose_best(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Pick the per-filetype policy strategy that gives the best
    detection-vs-FP balance at this level's FP/M target.

    Primary key is recall (catch more malware at the fixed FP target —
    the deployment goal). F1 captures the recall/precision balance. -fp
    is the next tiebreaker so we don't prefer a gratuitously aggressive
    policy when a quieter one matches on the headline metrics.

    Below-resolution levels collapse all candidate policies to identical
    metrics (each picks the loosest 0-FP threshold). We then prefer the
    MORE INCLUSIVE policy on the remaining tiebreaker — i.e., a policy
    naming three routes (`specialist_primary_with_escape`) wins over one
    naming a single route (`general_only`) when both tie. That preserves
    the specialist's name in route_policies.json's thresholds map, which
    is what litmus uses to decide whether to load the specialist at all.

    Accuracy is intentionally not used: with the corpus's ~76% benign /
    24% malware split, accuracy is dominated by the benign class and
    tracks recall most of the way at strict FP budgets.
    """
    return max(
        candidates,
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
        for severity in ("hostile", "suspicious"):
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
                            "target_per_million": target,
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
                            "fp_per_million": 0.0,
                            "global_fp_per_million": 0.0,
                        },
                    )
                candidate_lists.append(candidates)
                route_names.append(route_name)

                next_dp: dict[int, tuple[int, list[int]]] = {}
                for used_fp, (used_tp, choices) in dp.items():
                    for idx, candidate in enumerate(candidates):
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
            for severity in ("hostile", "suspicious"):
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
                        "fp_per_million": best["fp_per_million"],
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
    for level_no, severity in [(5, "hostile"), (9, "hostile"), (5, "suspicious"), (9, "suspicious")]:
        rows = []
        for route_name, route in payload["routes"].items():
            level = next(item for item in route["levels"] if item["level"] == level_no)
            rows.append((route_name, route, level[severity]["best"]))
        rows.sort(key=lambda item: (-_sort_float(item[2]["recall"]), -int(item[1]["malware"]), item[0]))
        lines.extend(
            [
                "",
                f"## L{level_no} {severity.title()}",
                "",
                "Rows marked † are below data resolution: the per-filetype "
                "calibration sample is too small to credibly assert FP/M ≤ "
                "target at this level (95% CI). The threshold shown is the "
                "loosest empirical 0-FP threshold; FP/M is what the test "
                "partition actually observed under that threshold. *95% CI "
                "upper* is the Clopper-Pearson upper bound on deployment "
                "FP/M given the observed FP count in this filetype's benigns.",
                "",
                "| Route | Policy | Malware | Benign | Recall | FP | FP/1M | 95% CI upper | Global FP/1M | F1 | Accuracy | Thresholds |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
            ],
        )
        for route_name, route, best in rows[:30]:
            mark = "†" if best.get("below_resolution") else ""
            ben = int(route["benign"])
            cp_upper = (
                _clopper_pearson_fp_per_million_upper(int(best["fp"]), ben, alpha=0.05)
                if ben > 0 and best.get("fp") is not None
                else None
            )
            lines.append(
                "| "
                f"{route_name}{mark} | "
                f"{best['policy']} | "
                f"{route['malware']} | "
                f"{ben} | "
                f"{_pct(best.get('recall'))} | "
                f"{best['fp']} | "
                f"{_fmt_float(best.get('fp_per_million'), 2)} | "
                f"{_fmt_float(cp_upper, 2)} | "
                f"{_fmt_float(best.get('global_fp_per_million'), 3)} | "
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=None)
    parser.add_argument("--config", type=Path, default=Path("out/models/azoth/config.json"))
    parser.add_argument("--score-table", type=Path, default=Path("out/models/azoth/score_table.npz"))
    parser.add_argument("--output", type=Path, default=Path("out/models/azoth/route_policies.json"))
    parser.add_argument("--csv", type=Path, default=Path("out/models/azoth/route_policies.csv"))
    parser.add_argument("--markdown", type=Path, default=Path("out/models/azoth/route_policies.md"))
    parser.add_argument("--override-route", action="append", default=[])
    parser.add_argument("--workers", type=int, default=0)
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

    for file_type in sorted(set(file_types)):
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
        levels: list[dict[str, Any]] = []
        for target in config["levels"]:
            level_no = int(target["level"])
            level_item: dict[str, Any] = {"level": level_no}
            for severity in ("hostile", "suspicious"):
                target_per_million = float(target[severity]["target_per_million"])
                candidates = [_no_hit_candidate(scoped_labels, target_per_million=target_per_million, total_benign=total_benign)]
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
                level_item[severity] = {
                    "target_per_million": target_per_million,
                    "budget": _budget(benign, target_per_million),
                    "best": _choose_best(candidates),
                    "candidates": candidates,
                }
            levels.append(level_item)
        route_payload[f"filetypes/{file_type}"] = {
            "filetype": file_type,
            "filegroup": group,
            "models": list(route_probs),
            "rows": int(len(indices)),
            "malware": malware,
            "benign": benign,
            "levels": levels,
        }

    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "schema": "azoth.route_policy_search.v1",
        "calibration_snapshot_id": config.get("calibration_snapshot_id"),
        "rows": int(len(labels)),
        "malware": int(np.sum(labels == 1)),
        "benign": total_benign,
        "routes": route_payload,
    }
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
