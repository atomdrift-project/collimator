#!/usr/bin/env python3
"""Copy error-report samples into a clean triage directory."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from archive_error_samples import _rows, _sample_path


def _clear_directory(path: Path) -> None:
    resolved = path.resolve(strict=False)
    if not str(resolved).startswith("/tmp/") or resolved == Path("/tmp"):
        raise ValueError(f"refusing to clear non-/tmp triage directory: {path}")
    path.mkdir(parents=True, exist_ok=True)
    for child in path.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def copy_report(
    *,
    report_path: Path,
    output_dir: Path,
    samples_dir: Path,
    kind: str,
    top: int,
) -> dict[str, Any]:
    with open(report_path) as f:
        payload = json.load(f)

    _clear_directory(output_dir)

    seen: set[Path] = set()
    copied: list[str] = []
    missing: list[str] = []

    for row in _rows(payload, kind):
        if len(copied) >= top:
            break
        resolved = _sample_path(samples_dir, row)
        if resolved is None:
            continue
        path, arcname = resolved
        dedupe_key = path.resolve(strict=False)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        if not path.exists():
            missing.append(str(row.get("path") or ""))
            continue

        destination = output_dir / arcname
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            shutil.copytree(path, destination, symlinks=True)
        else:
            shutil.copy2(path, destination)
        copied.append(arcname)

    return {
        "report": str(report_path),
        "output_dir": str(output_dir),
        "samples_dir": str(samples_dir),
        "kind": kind,
        "requested": top,
        "copied": len(copied),
        "missing": missing,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--samples-dir", default="/data/samples", type=Path)
    parser.add_argument(
        "--kind",
        choices=[
            "false-positives",
            "false-negatives",
            "near-false-positives",
            "near-false-negatives",
        ],
        required=True,
    )
    parser.add_argument("--top", type=int, default=100)
    args = parser.parse_args()

    summary = copy_report(
        report_path=args.report,
        output_dir=args.output_dir,
        samples_dir=args.samples_dir,
        kind=args.kind,
        top=args.top,
    )
    print(
        f"Copied {summary['copied']}/{summary['requested']} unique {args.kind} "
        f"samples to {summary['output_dir']}"
    )
    if summary["missing"]:
        print(f"Missing {len(summary['missing'])} paths; first 10:")
        for path in summary["missing"][:10]:
            print(f"  {path}")


if __name__ == "__main__":
    main()
