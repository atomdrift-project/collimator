#!/usr/bin/env python3
"""Copy error-report samples into a clean triage directory.

Samples are fetched from hopper's ``GET /api/file/{sha256}`` endpoint by
sha256. Local-disk lookup was removed: sample paths come from the hopper
DB and may be absolute paths from whatever host ingested them (e.g.
``/Users/t/...``), which don't exist on the triage host. Defaults to
``HOPPER_URL`` from the env, or http://10.9.8.5:8081/.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from archive_error_samples import _rows, _sample_path

DEFAULT_HOPPER_URL = "http://10.9.8.5:8081"


def _fetch_from_hopper(sha256: str, destination: Path, hopper_url: str, timeout: float = 10.0) -> bool:
    """GET /api/file/{sha256} → destination. Returns True on success."""
    if not sha256:
        return False
    url = f"{hopper_url.rstrip('/')}/api/file/{sha256}"
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            if resp.status != 200:
                return False
            tmp = destination.with_suffix(destination.suffix + ".tmp")
            with open(tmp, "wb") as f:
                shutil.copyfileobj(resp, f)
            tmp.rename(destination)
        return True
    except (urllib.error.URLError, OSError, TimeoutError):
        return False



_TEMP_ROOTS = (Path("/var/tmp"), Path(tempfile.gettempdir()))


def _clear_directory(path: Path) -> None:
    resolved = path.resolve(strict=False)
    inside_temp = False
    for root in _TEMP_ROOTS:
        r = root.resolve(strict=False)
        try:
            if os.path.commonpath([str(resolved), str(r)]) == str(r) and resolved != r:
                inside_temp = True
                break
        except ValueError:
            pass
    if not inside_temp:
        raise ValueError(f"refusing to clear non-temp triage directory: {path}")
    path.mkdir(parents=True, exist_ok=True)
    for child in path.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def _copy_rows(
    rows: list[dict[str, Any]],
    *,
    base_dir: Path,
    samples_dir: Path,
    top: int,
    hopper_url: str | None,
    seen: set[Path],
    copied: list[str],
    fetched: list[str],
    missing: list[str],
    extract_members: bool = True,
    hopper_failures: list[int] | None = None,
    hopper_failure_limit: int = 5,
) -> int:
    """Fetch up to ``top`` obtainable samples from hopper into ``base_dir``.

    Keeps scanning past rows hopper can't serve until ``top`` files actually
    land — so feeding a larger candidate pool than ``top`` covers samples
    absent from hopper. Mutates the shared accumulators. Returns the count
    landed in ``base_dir``.

    When ``extract_members`` is False, archive members land under the outer
    archive's name (deduped across members) rather than in a per-member subdir.
    """
    here = 0
    for row in rows:
        if here >= top:
            break
        resolved = _sample_path(samples_dir, row)
        if resolved is None:
            continue
        outer_path, outer_arcname = resolved

        raw_path = str(row.get("path") or "")
        is_archive_member = "!!" in raw_path
        member_name = raw_path.split("!!", 1)[1] if is_archive_member else None

        # For member extraction: dedupe on (outer_path, member_name).
        # When copying whole archives: dedupe on outer_path so multiple members
        # of the same archive only copy it once.
        if is_archive_member and extract_members:
            dedupe_key = outer_path.resolve(strict=False) / (member_name or "")
        else:
            dedupe_key = outer_path.resolve(strict=False)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        if is_archive_member and extract_members:
            # Place the extracted member under <outer_arcname>/<member_name>
            # so the archive it came from is visible in the path.
            destination = base_dir / outer_arcname / member_name
        else:
            destination = base_dir / outer_arcname

        # Fetch from hopper by sha256 — the only source.
        if not hopper_url:
            missing.append(raw_path)
            continue

        # Skip hopper if it has failed too many consecutive times (dead service).
        if hopper_failures is not None and hopper_failures[0] >= hopper_failure_limit:
            if hopper_failures[0] == hopper_failure_limit:
                print(f"  hopper: {hopper_failure_limit} consecutive failures — skipping remaining hopper fetches", flush=True)
                hopper_failures[0] += 1  # only print once
            missing.append(raw_path)
            continue

        # For archive members, hopper serves the inner file's bytes directly
        # by the row's sha256 — no outer-archive lookup needed.
        target_sha = str(row.get("sha256") or "")
        if target_sha and _fetch_from_hopper(target_sha, destination, hopper_url):
            if hopper_failures is not None:
                hopper_failures[0] = 0
            print(f"  hopper: fetched {target_sha[:12]}… → {destination.name}", flush=True)
            fetched.append(str(destination.relative_to(base_dir)))
            copied.append(str(destination.relative_to(base_dir)))
            here += 1
            continue
        if hopper_failures is not None and target_sha:
            hopper_failures[0] += 1

        missing.append(raw_path)
    return here


def copy_report(
    *,
    report_path: Path,
    output_dir: Path,
    samples_dir: Path,
    kind: str,
    top: int,
    hopper_url: str | None = None,
    skip: int = 0,
    group_by_filetype: bool = False,
) -> dict[str, Any]:
    with open(report_path) as f:
        payload = json.load(f)

    _clear_directory(output_dir)

    seen: set[Path] = set()
    copied: list[str] = []
    missing: list[str] = []
    fetched: list[str] = []
    hopper_failures: list[int] = [0]

    rows = _rows(payload, kind)
    if skip > 0:
        rows = rows[skip:]

    extract_members = kind != "false-negatives"

    per_filetype: dict[str, int] = {}
    if group_by_filetype:
        # ``top`` is a PER-FILETYPE quota; each filetype lands in its own
        # subdir so the sorter can sweep one type at a time.
        groups: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            ft = str(row.get("filetype") or "unknown")
            groups.setdefault(ft, []).append(row)
        n_ft = len(groups)
        for i, (ft, ft_rows) in enumerate(sorted(groups.items()), 1):
            n = _copy_rows(
                ft_rows,
                base_dir=output_dir / ft,
                samples_dir=samples_dir,
                top=top,
                hopper_url=hopper_url,
                seen=seen,
                copied=copied,
                fetched=fetched,
                missing=missing,
                extract_members=extract_members,
                hopper_failures=hopper_failures,
            )
            per_filetype[ft] = n
            print(f"  [{i}/{n_ft}] {ft}: {n} copied", flush=True)
    else:
        _copy_rows(
            rows,
            base_dir=output_dir,
            samples_dir=samples_dir,
            top=top,
            hopper_url=hopper_url,
            seen=seen,
            copied=copied,
            fetched=fetched,
            missing=missing,
            extract_members=extract_members,
            hopper_failures=hopper_failures,
        )

    return {
        "report": str(report_path),
        "output_dir": str(output_dir),
        "samples_dir": str(samples_dir),
        "hopper_url": hopper_url or "",
        "kind": kind,
        "requested": top,
        "grouped_by_filetype": group_by_filetype,
        "filetypes": len(per_filetype),
        "per_filetype_copied": per_filetype,
        "copied": len(copied),
        "fetched_from_hopper": len(fetched),
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
    parser.add_argument(
        "--group-by-filetype",
        action="store_true",
        help="Write each sample under <output-dir>/<filetype>/ and treat "
             "--top as a PER-FILETYPE quota (copy until --top land for each "
             "filetype). Pair with a report built via "
             "mislabeled_by_scope.py --per-filetype-top.",
    )
    parser.add_argument(
        "--skip",
        type=int,
        default=0,
        help="Skip the first N rows in the report before taking --top.",
    )
    parser.add_argument(
        "--hopper-url",
        default=os.environ.get("HOPPER_URL", DEFAULT_HOPPER_URL),
        help=(
            "Hopper download API base URL. Set to empty to disable the fallback "
            "fetch; default uses HOPPER_URL env or " + DEFAULT_HOPPER_URL
        ),
    )
    args = parser.parse_args()

    summary = copy_report(
        report_path=args.report,
        output_dir=args.output_dir,
        samples_dir=args.samples_dir,
        kind=args.kind,
        top=args.top,
        hopper_url=args.hopper_url or None,
        skip=args.skip,
        group_by_filetype=args.group_by_filetype,
    )
    if summary["grouped_by_filetype"]:
        print(
            f"Copied {summary['copied']} unique {args.kind} samples across "
            f"{summary['filetypes']} filetype(s) "
            f"(target {summary['requested']}/filetype) to {summary['output_dir']}"
        )
    else:
        print(
            f"Copied {summary['copied']}/{summary['requested']} unique {args.kind} "
            f"samples to {summary['output_dir']}"
        )
    if summary["fetched_from_hopper"]:
        print(f"  ({summary['fetched_from_hopper']} fetched from hopper "
              f"at {summary['hopper_url']})")
    if summary["missing"]:
        print(f"Missing {len(summary['missing'])} paths (not on disk, not in hopper); first 10:")
        for path in summary["missing"][:10]:
            print(f"  {path}")


if __name__ == "__main__":
    main()
