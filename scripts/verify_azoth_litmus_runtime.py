#!/usr/bin/env python3
"""Verify scan can load and score expected Azoth runtime routes."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _clean(text: str) -> str:
    return ANSI_RE.sub("", text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--litmus-dir", type=Path, default=Path("../scan"))
    parser.add_argument("--models-dir", type=Path, required=True)
    parser.add_argument("--sample", type=Path, default=Path("/bin/ls"))
    parser.add_argument("--required-model", action="append", default=[])
    args = parser.parse_args()

    env = os.environ.copy()
    env["SCAN_MODELS_DIR"] = str(args.models_dir)
    # Ask for the JSON envelope and read route scores from `ml.mods[].rte`.
    # scan v2 only prints the terminal `models:` line for process scans, so
    # the structured output is the reliable source for per-route presence.
    cmd = [
        "cargo",
        "run",
        "--release",
        "--",
        "--format",
        "json",
        "scan",
        str(args.sample),
    ]
    proc = subprocess.run(
        cmd,
        cwd=args.litmus_dir,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    stdout = _clean(proc.stdout)
    logs = _clean(proc.stderr)
    # Surface scan's logs (model-load WARNs live here) for CI visibility.
    print(logs, end="" if logs.endswith("\n") else "\n")
    if proc.returncode != 0:
        print(stdout)
        raise SystemExit(proc.returncode)

    try:
        report = json.loads(stdout)
    except json.JSONDecodeError as exc:
        print(stdout)
        print(f"error: could not parse scan JSON output: {exc}")
        return 1

    ml = report.get("ml") or {}
    scored = {m.get("rte") for m in (ml.get("mods") or []) if isinstance(m, dict)}
    skipped = [s for s in (ml.get("skip") or []) if isinstance(s, dict)]

    errors: list[str] = []
    if "dropping specialist" in logs.lower():
        errors.append("scan dropped at least one specialist")
    for model in args.required_model:
        if model not in scored:
            errors.append(
                f"required model score {model!r} missing from scan output "
                f"(scored routes: {sorted(r for r in scored if r)})"
            )
    if skipped:
        # Skipped routes are usually benign (e.g. wrong-format for this sample),
        # so report them for visibility but only fail via the required-model
        # check above.
        names = ", ".join(f"{s.get('rte')}:{s.get('why')}" for s in skipped)
        print(f"note: scan skipped applicable-but-unused routes: {names}")

    # Surface model-config anomalies that scan only logs at WARN. Without
    # this gate they silently degrade the deployed model. Make them
    # deploy-blocking — easy CI signal, no scan change.
    anomaly_patterns = (
        "config.json thresholds are invalid",
        "abi version mismatch",
        "unknown blend transform",
        "blend routes/weights length mismatch",
        "blend threshold outside",
        "ignoring invalid thresholds in ensemble config",
        "no config.json or evaluation.json thresholds found",
    )
    anomaly_hits: list[str] = []
    for line in (logs + "\n" + stdout).splitlines():
        low = line.lower()
        for pat in anomaly_patterns:
            if pat in low:
                anomaly_hits.append(line.strip())
                break
    if anomaly_hits:
        # Cap noise for the error report; show first 20 + total.
        sample = anomaly_hits[:20]
        msg = (
            f"scan emitted {len(anomaly_hits)} model-config anomaly warning(s) "
            f"(showing first {len(sample)}):"
        )
        errors.append(msg)
        for hit in sample:
            errors.append(f"  {hit}")

    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print("scan runtime routes ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
