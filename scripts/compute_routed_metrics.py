#!/usr/bin/env python3
"""Report saved Azoth policies on the locked test partition.

F1 and recall measure the decisions deployed by scan. AP/AUC rank raw route
probabilities or signed ensemble policy margins. This script fits nothing.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import numpy as np

from collimator import bundle, policy
from collimator.thresholds import DEFAULT_SEVERITY_LEVEL

LOG = logging.getLogger("compute_routed_metrics")


def compute_per_filetype_metrics_honest(
    score_table_path: Path,
    route_policies_path: Path,
    *,
    level: int = DEFAULT_SEVERITY_LEVEL,
    severity: str = "hostile",
    with_ci: bool = True,
    **legacy_options,
) -> dict:
    """Apply frozen policies; old fitting/cache options have no effect."""
    if legacy_options.get("partition", "test") != "test":
        raise ValueError("headline reporting requires the locked test partition")
    config = json.loads((route_policies_path.parent / "config.json").read_text())
    policies = json.loads(route_policies_path.read_text())
    with np.load(score_table_path) as table:
        return policy.report(table, config, policies, level=level, severity=severity, with_ci=with_ci)


# Retain the public name, with the same held-out contract as the CLI.
compute_per_filetype_metrics = compute_per_filetype_metrics_honest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--azoth-root", type=Path, default=Path("out/models/azoth"))
    parser.add_argument("--level", type=int, default=DEFAULT_SEVERITY_LEVEL)
    parser.add_argument("--severity", default="hostile", choices=["hostile"])
    parser.add_argument("--no-ci", action="store_true", help="Omit binomial recall intervals")
    parser.add_argument("--log-level", default="INFO")
    # Existing Make/autocollie invocations pass these. Canonical partitions are
    # now embedded in scores; test reporting needs no DB, fitting, or fit caches.
    for flag in ("--db", "--test-mask-cache-dir", "--calibrator-cache-dir", "--previous-bundle"):
        parser.add_argument(flag, help=argparse.SUPPRESS)
    for flag in ("--no-test-mask-cache", "--no-calibrator-cache", "--no-stacked"):
        parser.add_argument(flag, action="store_true", help=argparse.SUPPRESS)
    for flag in ("--calib-parallelism", "--metrics-parallelism"):
        parser.add_argument(flag, type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(message)s")
    root = args.azoth_root
    metrics = compute_per_filetype_metrics_honest(
        root / "score_table.npz", root / "route_policies.json",
        level=args.level, severity=args.severity, with_ci=not args.no_ci,
    )
    output = root / "per_filetype_metrics.json"
    bundle.atomic_write_json(output, metrics)
    LOG.info("wrote %s (%d filetypes)", output, len(metrics["filetypes"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
