#!/usr/bin/env python3
"""Copy error-report samples into a clean triage directory.

When a sample is missing from the local samples directory, fall back to
hopper's ``GET /api/file/{sha256}`` endpoint so triage tarballs don't
silently lose samples that have been pruned from local disk. Defaults
to ``HOPPER_URL`` from the env, or http://10.9.8.5:8081/.
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


def _fetch_from_hopper(sha256: str, destination: Path, hopper_url: str, timeout: float = 60.0) -> bool:
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


def _outer_sha_lookup(db_dsn: str, outer_path: str) -> str | None:
    """Resolve an outer archive's sha256 by its filesystem path via the hopper DB.

    Triage rows for archive members report the INNER sample's sha256 (per
    cleave's reporting convention). Hopper's /api/file/{sha} for that
    inner sha returns the EXTRACTED inner file bytes, not the outer
    archive. For triage we want the outer archive — that's what cleave
    re-runs against to reproduce the analysis. Look up its sha by path.
    """
    if not db_dsn or not outer_path:
        return None
    try:
        import psycopg  # noqa: PLC0415 — keep psycopg optional for non-hopper users
    except ImportError:
        return None
    try:
        with psycopg.connect(db_dsn, connect_timeout=5) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT sha256 FROM samples WHERE path = %s LIMIT 1",
                (outer_path,),
            )
            row = cur.fetchone()
            return row[0] if row else None
    except (psycopg.Error, OSError):
        return None


def _clear_directory(path: Path) -> None:
    resolved = path.resolve(strict=False)
    temp_root = Path(tempfile.gettempdir()).resolve(strict=False)
    try:
        inside_temp = os.path.commonpath([str(resolved), str(temp_root)]) == str(temp_root)
    except ValueError:
        inside_temp = False
    if not inside_temp or resolved == temp_root:
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
    db_dsn: str | None,
    seen: set[Path],
    copied: list[str],
    fetched: list[str],
    missing: list[str],
) -> int:
    """Copy up to ``top`` obtainable samples into ``base_dir``.

    Keeps scanning past locally-missing rows (falling back to hopper) until
    ``top`` files actually land — so feeding a larger candidate pool than
    ``top`` covers samples pruned from disk and absent from hopper. Mutates
    the shared accumulators. Returns the count copied into ``base_dir``.
    """
    here = 0
    for row in rows:
        if here >= top:
            break
        resolved = _sample_path(samples_dir, row)
        if resolved is None:
            continue
        path, arcname = resolved
        dedupe_key = path.resolve(strict=False)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        destination = base_dir / arcname

        if path.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            if path.is_dir():
                shutil.copytree(path, destination, symlinks=True)
            else:
                shutil.copy2(path, destination)
            copied.append(arcname)
            here += 1
            continue

        # Missing locally — try hopper if configured.
        if not hopper_url:
            missing.append(str(row.get("path") or ""))
            continue

        # The row's sha256 is the inner sample's sha for archive-member
        # rows; arcname is the outer archive path. If they refer to the
        # same file (no `!!` in the row path) we can fetch directly by
        # that sha. Otherwise look up the outer archive's sha by path
        # so the tarball gets the same artifact local-copy would have
        # given us — a complete archive that cleave can re-run against.
        raw_path = str(row.get("path") or "")
        is_archive_member = "!!" in raw_path
        target_sha = row.get("sha256")
        if is_archive_member:
            # Pull the whole outer archive (cleave re-runs against it). Prefer
            # the row's `parent` — the archive's own sha256, carried on every
            # extracted member. Hopper serves it directly, and it's reliable
            # even when the archive isn't a tracked sample row (so its path
            # won't resolve). Fall back to the legacy path lookup for reports
            # that predate the `parent` field.
            target_sha = str(row.get("parent") or "") or _outer_sha_lookup(db_dsn or "", arcname)

        if target_sha and _fetch_from_hopper(target_sha, destination, hopper_url):
            fetched.append(arcname)
            copied.append(arcname)
            here += 1
            continue

        missing.append(str(row.get("path") or ""))
    return here


def copy_report(
    *,
    report_path: Path,
    output_dir: Path,
    samples_dir: Path,
    kind: str,
    top: int,
    hopper_url: str | None = None,
    db_dsn: str | None = None,
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

    rows = _rows(payload, kind)
    if skip > 0:
        rows = rows[skip:]

    per_filetype: dict[str, int] = {}
    if group_by_filetype:
        # ``top`` is a PER-FILETYPE quota; each filetype lands in its own
        # subdir so the sorter can sweep one type at a time.
        groups: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            ft = str(row.get("filetype") or "unknown")
            groups.setdefault(ft, []).append(row)
        for ft, ft_rows in sorted(groups.items()):
            per_filetype[ft] = _copy_rows(
                ft_rows,
                base_dir=output_dir / ft,
                samples_dir=samples_dir,
                top=top,
                hopper_url=hopper_url,
                db_dsn=db_dsn,
                seen=seen,
                copied=copied,
                fetched=fetched,
                missing=missing,
            )
    else:
        _copy_rows(
            rows,
            base_dir=output_dir,
            samples_dir=samples_dir,
            top=top,
            hopper_url=hopper_url,
            db_dsn=db_dsn,
            seen=seen,
            copied=copied,
            fetched=fetched,
            missing=missing,
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
    parser.add_argument(
        "--db",
        default=os.environ.get("DB", ""),
        help=(
            "Hopper PostgreSQL DSN. Used to resolve outer-archive sha256 by "
            "path when an archive-member sample is missing locally. "
            "Defaults to DB env."
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
        db_dsn=args.db or None,
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
