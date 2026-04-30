#!/usr/bin/env python3
"""Create a tar archive from false-positive/false-negative report rows."""

from __future__ import annotations

import argparse
import json
import tarfile
from pathlib import Path
from typing import Any


def _rows(payload: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    if kind == "false-positives":
        rows = payload.get("false_positives", [])
    elif kind == "false-negatives":
        rows = payload.get("uncaught", [])
    elif kind == "near-false-positives":
        rows = payload.get("near_false_positives", [])
    else:
        rows = payload.get("near_false_negatives", [])
    if not isinstance(rows, list):
        raise ValueError(f"invalid {kind} report: expected row list")
    return [row for row in rows if isinstance(row, dict)]


def _outer_path(raw_path: str) -> str:
    """Return the outer sample path for an embedded member path."""
    return raw_path.split("!!", 1)[0].lstrip("/")


def _sample_path(samples_dir: Path, row: dict[str, Any]) -> tuple[Path, str] | None:
    raw = str(row.get("path") or "").strip()
    if not raw:
        return None

    outer = _outer_path(raw)
    path = Path(outer)
    if path.is_absolute():
        try:
            arcname = str(path.relative_to(samples_dir))
        except ValueError:
            arcname = str(path).lstrip("/")
        return path, arcname

    return samples_dir / path, outer


def archive_report(
    *,
    report_path: Path,
    output_path: Path,
    samples_dir: Path,
    kind: str,
    top: int,
) -> dict[str, Any]:
    with open(report_path) as f:
        payload = json.load(f)

    seen: set[Path] = set()
    selected: list[tuple[Path, str]] = []
    missing: list[str] = []

    for row in _rows(payload, kind):
        if len(selected) >= top:
            break
        resolved = _sample_path(samples_dir, row)
        if resolved is None:
            continue
        path, arcname = resolved
        dedupe_key = path.resolve(strict=False)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        if path.exists():
            selected.append((path, arcname))
        else:
            missing.append(str(row.get("path") or ""))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output_path, "w:gz") as tar:
        for path, arcname in selected:
            tar.add(path, arcname=arcname, recursive=True)

    return {
        "report": str(report_path),
        "archive": str(output_path),
        "samples_dir": str(samples_dir),
        "kind": kind,
        "requested": top,
        "archived": len(selected),
        "missing": missing,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
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

    summary = archive_report(
        report_path=args.report,
        output_path=args.output,
        samples_dir=args.samples_dir,
        kind=args.kind,
        top=args.top,
    )
    print(
        f"Archived {summary['archived']}/{summary['requested']} unique {args.kind} "
        f"samples to {summary['archive']}"
    )
    if summary["missing"]:
        print(f"Missing {len(summary['missing'])} paths; first 10:")
        for path in summary["missing"][:10]:
            print(f"  {path}")


if __name__ == "__main__":
    main()
