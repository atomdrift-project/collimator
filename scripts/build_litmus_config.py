#!/usr/bin/env python3
"""Build litmus config.json from full-corpus threshold tuning output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    with path.open() as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise SystemExit(f"error: {path} is not a JSON object")
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold-tuning", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if not args.threshold_tuning.exists():
        raise SystemExit(
            f"error: {args.threshold_tuning} not found; run `make thresholds-refresh` before `make deploy`"
        )

    tuning = _load_json(args.threshold_tuning)
    corpus = tuning.get("corpus") or {}
    levels = tuning.get("severity_levels") or []
    targets = tuning.get("severity_level_targets") or []
    if not levels:
        raise SystemExit(
            f"error: {args.threshold_tuning} has no severity_levels; run `make thresholds-refresh`"
        )
    if not corpus.get("benign") or not corpus.get("malware"):
        raise SystemExit(
            f"error: {args.threshold_tuning} does not look like a full-corpus threshold report; "
            "run `make thresholds-refresh`"
        )

    level5 = next((row for row in levels if row.get("level") == 5), None)
    if not isinstance(level5, dict):
        raise SystemExit("error: threshold report does not contain severity level 5")

    config: dict[str, Any] = {
        "severity_level_targets": targets,
        "severity_levels": levels,
    }
    for name in ("suspicious", "hostile"):
        metric = level5.get(name)
        if not isinstance(metric, dict) or metric.get("threshold") is None:
            raise SystemExit(f"error: severity level 5 is missing {name} threshold")
        config[name] = float(metric["threshold"])

    if config["suspicious"] >= config["hostile"]:
        raise SystemExit(
            "error: full-corpus level 5 thresholds do not create a suspicious band "
            f"(suspicious={config['suspicious']:.6f}, hostile={config['hostile']:.6f}); "
            "run `make thresholds-refresh` against the full good corpus"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        json.dump(config, f, indent=2)
    print(
        "  config.json: "
        f"suspicious={config['suspicious']:.6f}, "
        f"hostile={config['hostile']:.6f}, "
        f"severity_levels={len(levels)}, "
        f"corpus={corpus.get('samples')} samples"
    )


if __name__ == "__main__":
    main()
