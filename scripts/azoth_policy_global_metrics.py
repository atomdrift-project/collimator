#!/usr/bin/env python3
"""Measure deployed Azoth route policies against the full score table."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


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
    if target_per_million <= 0:
        return 0
    return max(1, int(math.floor(benign * target_per_million / 1_000_000.0)))


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
        "target_per_million": target_per_million,
        "budget": budget,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "fp_per_million": fp * 1_000_000.0 / benign_n if benign_n else math.nan,
        "within_budget": fp <= budget,
    }


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
    hit = np.zeros(len(labels), dtype=bool)
    route_hits: dict[str, int] = {}
    config_thresholds = _config_thresholds(config, level, severity)
    for filetype in sorted(set(str(value) for value in file_types)):
        mask = file_types == filetype
        thresholds = _policy_thresholds(policy, filetype, level, severity)
        if thresholds is None:
            thresholds = config_thresholds
        for route, threshold in thresholds.items():
            if route not in route_names:
                continue
            route_idx = route_names.index(route)
            route_score = scores[route_idx, mask]
            route_hit = ~np.isnan(route_score) & (route_score >= threshold)
            if np.any(route_hit):
                hit[np.flatnonzero(mask)[route_hit]] = True
                route_hits[route] = route_hits.get(route, 0) + int(np.sum(route_hit))
    return hit, route_hits


def _pct(value: float) -> str:
    return "-" if math.isnan(value) else f"{100 * value:.2f}%"


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Azoth Global Policy Metrics",
        "",
        f"- Rows: {payload['rows']} ({payload['malware']} malware, {payload['benign']} benign)",
        f"- Calibration snapshot: `{payload.get('calibration_snapshot_id')}`",
        "",
        "| L | Severity | Target/1M | Budget | Recall | Precision | F1 | FP | FP/1M | Within budget |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in payload["levels"]:
        for severity in ("hostile", "suspicious"):
            m = item[severity]
            lines.append(
                "| "
                f"{item['level']} | {severity} | "
                f"{m['target_per_million']:.1f} | {m['budget']} | "
                f"{_pct(float(m['recall']))} | {_pct(float(m['precision']))} | {_pct(float(m['f1']))} | "
                f"{m['fp']} | {float(m['fp_per_million']):.2f} | "
                f"{'yes' if m['within_budget'] else 'NO'} |"
            )
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
    args = parser.parse_args()

    config = _load_json(args.config)
    policy = _load_json(args.policy)
    score_table = np.load(args.score_table)
    labels = score_table["labels"].astype(np.int8)
    file_types = np.asarray([str(value) for value in score_table["file_types"]])
    route_names = [str(value) for value in score_table["route_names"]]
    scores = score_table["scores"].astype(np.float32)

    levels: list[dict[str, Any]] = []
    failed = False
    for level_item in config.get("levels", []):
        level = int(level_item["level"])
        out: dict[str, Any] = {"level": level}
        for severity in ("hostile", "suspicious"):
            target = float(level_item[severity]["target_per_million"])
            hit, route_hits = _decisions(
                labels=labels,
                file_types=file_types,
                route_names=route_names,
                scores=scores,
                config=config,
                policy=policy,
                level=level,
                severity=severity,
            )
            m = _metrics(labels, hit, target)
            m["route_hits"] = route_hits
            failed = failed or not bool(m["within_budget"])
            out[severity] = m
        levels.append(out)

    payload = {
        "schema": "azoth.global_policy_metrics.v1",
        "calibration_snapshot_id": config.get("calibration_snapshot_id"),
        "rows": int(len(labels)),
        "malware": int(np.sum(labels == 1)),
        "benign": int(np.sum(labels == 0)),
        "levels": levels,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = _json_clean(payload)
    with open(args.output, "w") as f:
        json.dump(payload, f, indent=2, allow_nan=False)
    _write_markdown(args.markdown, payload)
    print(f"wrote {args.output}")
    print(f"wrote {args.markdown}")
    if args.fail_on_budget and failed:
        print("error: one or more levels exceed the configured FP budget")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
