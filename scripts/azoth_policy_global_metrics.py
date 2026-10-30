#!/usr/bin/env python3
"""Measure deployed Azoth route policies against the full score table."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

# scripts/ isn't on sys.path; reach src/ for `collimator.bundle`.
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import bundle, thresholds  # noqa: E402


def _json_clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_clean(v) for v in value]
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, np.floating):
        f = float(value)
        return None if math.isnan(f) else f
    if isinstance(value, np.integer):
        return int(value)
    return value


def _budget(benign: int, target_per_million: float) -> int:
    return thresholds.resolution_adjusted_fp_budget(benign, target_per_million * 100.0)


def _load_json(path: Path) -> dict[str, Any]:
    with open(path) as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected JSON object")
    return data


def _config_thresholds(config: dict[str, Any], level: int, severity: str) -> dict[str, float]:
    for item in config.get("levels", []):
        if int(item.get("level", -1)) == level:
            return {str(k): float(v) for k, v in item[severity].get("thresholds", {}).items()}
    return {}


def _policy_thresholds(policy: dict[str, Any], filetype: str, level: int, severity: str) -> dict[str, float] | None:
    route = policy.get("routes", {}).get(f"filetypes/{filetype}")
    if not route:
        return None
    for item in route.get("levels", []):
        if int(item.get("level", -1)) == level:
            thresholds = item.get(severity, {}).get("best", {}).get("thresholds", {})
            return {str(k): float(v) for k, v in thresholds.items()}
    return None


def _metrics(labels: np.ndarray, hit: np.ndarray, target_per_million: float) -> dict[str, Any]:
    benign = labels == 0
    malware = labels == 1
    tp = int(np.sum(hit & malware))
    fp = int(np.sum(hit & benign))
    tn = int(np.sum((~hit) & benign))
    fn = int(np.sum((~hit) & malware))
    benign_n = int(np.sum(benign))
    malware_n = int(np.sum(malware))
    budget = _budget(benign_n, target_per_million)
    precision = tp / max(tp + fp, 1)
    recall = tp / malware_n if malware_n else math.nan
    f1 = 2 * precision * recall / max(precision + recall, 1e-12) if malware_n else math.nan
    return {
        "target_per_100M": target_per_million * 100.0,
        "benign": benign_n,
        "malware": malware_n,
        "budget": budget,
        "nominal_rate_budget": int(math.floor(benign_n * target_per_million / 1_000_000)),
        "fp_upper_95_per_100M": _fp_upper_95(fp, benign_n),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "fp_per_100M": fp * 100_000_000.0 / benign_n if benign_n else math.nan,
        "within_budget": fp <= budget,
    }


def _fp_upper_95(fp: int, benign: int) -> float | None:
    """One-sided exact binomial bound, informational rather than an FP allowance."""
    if not benign:
        return None
    if fp == benign:
        return 1e8
    from scipy.stats import beta
    return float(beta.isf(0.05, fp + 1, benign - fp) * 1e8)


def _level_metrics(labels, hit, groups, target_per_million, *, multiplier=1.0):
    """One allowance per final filetype decision pool, never per component model.

    Aggregate FP alone could hide one bad route behind unused allowances on
    other routes. Each route must pass; totals are a summary of those checks.
    The literal population-rate bound remains separate from this empirical gate.
    """
    result = _metrics(labels, hit, target_per_million)
    routes = {}
    for route, indices in groups.items():
        m = _metrics(labels[indices], hit[indices], target_per_million)
        m["scaled_budget"] = int(math.floor(m["budget"] * multiplier))
        m["within_scaled_budget"] = m["fp"] <= m["scaled_budget"]
        m["status"] = ("insufficient_benign_data" if not m["benign"] else
                       "within_adjusted_budget" if m["within_scaled_budget"] else
                       "exceeds_adjusted_budget")
        routes[route] = m
    result.update(
        routes=routes,
        budget=sum(m["budget"] for m in routes.values()),
        scaled_budget=sum(m["scaled_budget"] for m in routes.values()),
        scaled_budget_multiplier=multiplier,
        within_budget=all(m["within_budget"] for m in routes.values()),
        within_scaled_budget=all(m["within_scaled_budget"] for m in routes.values()),
        exceeded_routes=[route for route, m in routes.items() if not m["within_scaled_budget"]],
        route_hits={route: m["tp"] + m["fp"] for route, m in routes.items()},
    )
    result["status"] = ("insufficient_benign_data" if not result["benign"] else
                        "within_adjusted_budget" if result["within_scaled_budget"] else
                        "exceeds_adjusted_budget")
    return result


def _decisions(
    *,
    labels: np.ndarray,
    file_types: np.ndarray,
    route_names: list[str],
    scores: np.ndarray,
    config: dict[str, Any],
    policy: dict[str, Any],
    level: int,
    severity: str,
) -> tuple[np.ndarray, dict[str, int]]:
    from collimator.policy import routed_margin
    hit = np.zeros(len(labels), dtype=bool)
    policy_hits: dict[str, int] = {}
    for filetype in np.unique(file_types):
        mask = file_types == filetype
        subset = {route: scores[index, mask] for index, route in enumerate(route_names)}
        hit[mask] = routed_margin(subset, config, policy, str(filetype), level,
                                  int(mask.sum()), severity=severity) >= 0
        policy_hits[f"filetypes/{filetype}"] = int(hit[mask].sum())
    return hit, policy_hits


def _pct(value: float | None) -> str:
    return "-" if value is None or math.isnan(value) else f"{100 * value:.2f}%"


def _first_decisions(file_types, route_names, scores, config, policy, *, severity="hostile"):
    """Evaluate each policy once instead of replaying stricter levels repeatedly."""
    from collimator.policy import first_firing_level, routing_levels
    first = np.full(len(file_types), np.iinfo(np.int64).max, dtype=np.int64)
    groups = {}
    for filetype in np.unique(file_types):
        indices = np.flatnonzero(file_types == filetype)
        subset = {route: scores[index, indices] for index, route in enumerate(route_names)}
        levels = routing_levels(subset, config, policy, str(filetype), severity=severity)
        first[indices], _ = first_firing_level(subset, levels, len(indices), -1, severity=severity)
        groups[f"filetypes/{filetype}"] = indices
    return first, groups


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Azoth Global Policy Metrics",
        "",
        f"- Rows: {payload['rows']} ({payload['malware']} malware, {payload['benign']} benign)",
        f"- Calibration snapshot: `{payload.get('calibration_snapshot_id')}`",
        "- Budget: one resolution-adjusted allowance per filetype's final swept decision.",
        "- Passing this empirical gate does not certify the nominal population FP rate.",
        "",
        "| L | Severity | Nominal level | Sum of allowances | Recall | Precision | F1 | FP | Observed FP/100M | Status |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in payload["levels"]:
        for severity in ("hostile",):
            m = item[severity]
            lines.append(
                "| "
                f"{item['level']} | {severity} | "
                f"{float(m['target_per_100M']):.1f} | {m['budget']} | "
                f"{_pct(m['recall'])} | {_pct(m['precision'])} | {_pct(m['f1'])} | "
                f"{m['fp']} | {m['fp_per_100M'] if m['fp_per_100M'] is not None else '-'} | "
                f"{m['status']} |"
            )
    deployed = next(item["hostile"] for item in payload["levels"]
                    if int(item["level"]) == payload["operating_level"])
    lines.extend(["", f"At L{payload['operating_level']}, the one-sided 95% upper "
                  f"bound is {deployed['fp_upper_95_per_100M']} FP/100M (informational)."])
    lines.extend(["", "## Routes exceeding their allowance", "",
                  "| L | Route | Benign | FP | Allowance | Effective gate allowance |",
                  "| ---: | --- | ---: | ---: | ---: | ---: |"])
    for item in payload["levels"]:
        for route in item["hostile"]["exceeded_routes"]:
            m = item["hostile"]["routes"][route]
            lines.append(f"| {item['level']} | {route} | {m['benign']} | {m['fp']} | "
                         f"{m['budget']} | {m['scaled_budget']} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("out/models/azoth/config.json"))
    parser.add_argument("--policy", type=Path, default=Path("out/models/azoth/route_policies.json"))
    parser.add_argument("--score-table", type=Path, default=Path("out/models/azoth/score_table.npz"))
    parser.add_argument("--output", type=Path, default=Path("out/models/azoth/global_policy_metrics.json"))
    parser.add_argument("--markdown", type=Path, default=Path("out/models/azoth/global_policy_metrics.md"))
    parser.add_argument("--fail-on-budget", action="store_true")
    parser.add_argument(
        "--budget-gate-level", type=int, default=thresholds.DEFAULT_SEVERITY_LEVEL,
        help="Deployment operating point to gate (default: canonical L25); other levels are reported.",
    )
    parser.add_argument(
        "--max-budget-multiplier",
        type=float,
        default=1.0,
        help=(
            "Explicit waiver: multiply each filetype's resolution-adjusted allowance. "
            "Default 1.0 enforces the documented level contract."
        ),
    )
    parser.add_argument(
        "--budget-gate-max-level",
        type=int,
        default=None,
        help=(
            "Opt in to gating every level <= this, including zero-FP L0, "
            "instead of just --budget-gate-level. Not the default: a zero-FP "
            "L0 test gate would impose a stricter objective than L25."
        ),
    )
    parser.add_argument(
        "--budget-gate-min-fp-resolution",
        type=int,
        default=0,
        help=("Deprecated resolution waiver. Only 0 is supported: small pools already "
              "receive their one-FP allowance and must not silently escape the gate."),
    )
    args = parser.parse_args()
    if not math.isfinite(args.max_budget_multiplier) or args.max_budget_multiplier < 1:
        parser.error("--max-budget-multiplier must be finite and >= 1")
    if args.budget_gate_min_fp_resolution != 0:
        parser.error("resolution skipping is incompatible with the adjusted count gate; use 0")

    config = _load_json(args.config)
    if not any(int(item["level"]) == args.budget_gate_level
               for item in config.get("levels", [])):
        raise ValueError("config is missing the deployment operating level")
    policy = _load_json(args.policy)
    from collimator import policy as frozen_policy
    with np.load(args.score_table) as table:
        score_table = frozen_policy.partition_table(table, "test")
    labels = score_table["labels"].astype(np.int8)
    file_types = np.asarray([str(value) for value in score_table["file_types"]])
    route_names = [str(value) for value in score_table["route_names"]]
    scores = score_table["scores"].astype(np.float32)

    levels: list[dict[str, Any]] = []
    failed = False
    multiplier = max(1.0, float(args.max_budget_multiplier))
    gate_max_level = args.budget_gate_max_level
    first, groups = _first_decisions(file_types, route_names, scores, config, policy)
    for level_item in config.get("levels", []):
        level = int(level_item["level"])
        out: dict[str, Any] = {"level": level}
        for severity in ("hostile",):
            target = float(level_item[severity]["target_per_million"])
            hit = first <= level
            m = _level_metrics(labels, hit, groups, target, multiplier=multiplier)
            m["budget_gated"] = (level <= gate_max_level if gate_max_level is not None
                                 else level == args.budget_gate_level)
            if m["budget_gated"]:
                failed = failed or m["status"] != "within_adjusted_budget"
            out[severity] = m
        levels.append(out)

    payload = {
        "schema": "azoth.global_policy_metrics.v2",
        "budget_semantics": "resolution_adjusted_per_filetype_v1",
        "decision_rule": "saved_policy_sweep",
        "operating_level": args.budget_gate_level,
        "confidence_note": "FP allowances are empirical; confidence bounds assume representative independent benign samples.",
        "calibration_snapshot_id": config.get("calibration_snapshot_id"),
        "rows": int(len(labels)),
        "evaluated_on": "test_bucket_only",
        "malware": int(np.sum(labels == 1)),
        "benign": int(np.sum(labels == 0)),
        "levels": levels,
    }
    payload = _json_clean(payload)
    bundle.atomic_write_json(args.output, payload)
    _write_markdown(args.markdown, payload)
    print(f"wrote {args.output}")
    print(f"wrote {args.markdown}")
    if args.fail_on_budget and failed:
        for item in levels:
            m = item["hostile"]
            if m["budget_gated"] and m["status"] != "within_adjusted_budget":
                print(f"L{item['level']}: {m['status']}; routes: "
                      + ", ".join(m["exceeded_routes"]))
        print("error: resolution-adjusted filetype FP gate failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
