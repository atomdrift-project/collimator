#!/usr/bin/env python3
"""Verify litmus can load and score expected Azoth runtime routes."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _clean(text: str) -> str:
    return ANSI_RE.sub("", text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--litmus-dir", type=Path, default=Path("../litmus"))
    parser.add_argument("--models-dir", type=Path, required=True)
    parser.add_argument("--sample", type=Path, default=Path("/bin/ls"))
    parser.add_argument("--required-model", action="append", default=[])
    args = parser.parse_args()

    env = os.environ.copy()
    env["LITMUS_MODELS_DIR"] = str(args.models_dir)
    cmd = [
        "cargo",
        "run",
        "--release",
        "--",
        "--extra",
        "--show",
        "all",
        "scan",
        str(args.sample),
    ]
    proc = subprocess.run(
        cmd,
        cwd=args.litmus_dir,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output = _clean(proc.stdout)
    print(output, end="" if output.endswith("\n") else "\n")
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)

    errors: list[str] = []
    lowered = output.lower()
    if "dropping specialist" in lowered:
        errors.append("litmus dropped at least one specialist")
    if "skipped:" in lowered or ":unavailable" in lowered:
        errors.append("litmus reported skipped or unavailable calibrated routes")
    for model in args.required_model:
        if f"{model}=" not in output:
            errors.append(f"required model score {model!r} missing from litmus --extra output")

    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print("litmus runtime routes ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
