#!/usr/bin/env python3
"""Atomically publish a completed training run as the canonical bundle.

Usage:
    azoth_publish_run.py <run-dir> --link <canonical-path>

What it does:
  1. Validate that <run-dir> looks like a complete azoth bundle — has
     ``config.json``, ``score_table.npz``, ``specialists.json``,
     ``route_policies.json``, and a usable ``general/`` route. Refuse
     to publish a half-baked bundle.
  2. If <canonical-path> doesn't exist, create a fresh symlink.
  3. If <canonical-path> is a symlink, atomically replace it via
     ``rename(2)`` of a sibling temp symlink — POSIX guarantees the
     swap is atomic so concurrent readers never see a missing target.
  4. If <canonical-path> is a real directory, move it aside to
     ``<canonical-path>-runs/legacy-<timestamp>/`` first, then create
     the symlink. This is the one-time migration off the old layout.

Doesn't touch caches under ``out/cache/`` — those are hash-keyed and
shared across runs. Doesn't touch the litmus deploy target
(``~/.local/share/litmus/models/azoth``) either — that path is
populated by ``make azoth-deploy-final`` via rsync from the staged
bundle and remains independent of this symlink.

Exit codes:
  0 — publish succeeded (or canonical already points to <run-dir>)
  1 — validation or filesystem error
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
from pathlib import Path


REQUIRED_TOP_LEVEL = (
    "config.json",
    "score_table.npz",
    "specialists.json",
    "route_policies.json",
)


def _validate_bundle(run_dir: Path) -> list[str]:
    """Return a list of missing artifacts. Empty list means the bundle
    is publishable. Mirrors the gates in azoth-deploy-final.
    """
    missing: list[str] = []
    for name in REQUIRED_TOP_LEVEL:
        if not (run_dir / name).is_file():
            missing.append(name)
    general = run_dir / "general"
    if not general.is_dir():
        missing.append("general/")
        return missing
    if not (general / "feature_spec.json").is_file():
        missing.append("general/feature_spec.json")
    # A bundled general model is either a single model.txt or a
    # multi-seed models/seed_*.txt layout. Either suffices.
    if not (general / "model.txt").is_file() and not list(
        (general / "models").glob("seed_*.txt"),
    ):
        missing.append("general/model.txt (or general/models/seed_*.txt)")
    return missing


def _archive_existing_dir(canonical: Path) -> Path:
    """Move a real directory aside so a symlink can take its place."""
    runs_root = canonical.parent / f"{canonical.name}-runs"
    runs_root.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    target = runs_root / f"legacy-{stamp}"
    # If the user re-runs this within a second, append a counter so
    # the archive name is unique. Rare but cheap to guard against.
    counter = 1
    while target.exists():
        target = runs_root / f"legacy-{stamp}-{counter}"
        counter += 1
    shutil.move(str(canonical), str(target))
    return target


def _atomic_symlink(target: Path, link: Path) -> None:
    """Atomically point ``link`` at ``target`` using rename(2).

    POSIX rename of a symlink (or to one) is atomic, so concurrent
    readers either see the old target or the new one — never a
    partially-resolved path.
    """
    tmp = link.with_name(link.name + ".publish-tmp")
    if tmp.exists() or tmp.is_symlink():
        tmp.unlink()
    # Use absolute target so the symlink remains valid if the cwd
    # changes; if target is inside link's parent, write a relative
    # link for portability/grep-ability of the directory tree.
    if link.parent.resolve() in target.resolve().parents:
        target_str = os.path.relpath(target.resolve(), link.parent.resolve())
    else:
        target_str = str(target.resolve())
    os.symlink(target_str, tmp)
    os.rename(tmp, link)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument(
        "--link",
        type=Path,
        required=True,
        help="Canonical path that becomes a symlink to run_dir.",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip the bundle-completeness check. Useful for debugging.",
    )
    args = parser.parse_args()
    run_dir: Path = args.run_dir.resolve()
    link: Path = args.link
    link_dir = link.parent

    if not run_dir.is_dir():
        print(f"error: run dir does not exist: {run_dir}", file=sys.stderr)
        return 1
    if not args.skip_validation:
        missing = _validate_bundle(run_dir)
        if missing:
            print(
                f"error: run dir {run_dir} is missing required artifacts:",
                file=sys.stderr,
            )
            for name in missing:
                print(f"  - {name}", file=sys.stderr)
            return 1

    link_dir.mkdir(parents=True, exist_ok=True)
    if link.is_symlink():
        current = os.readlink(link)
        # Compare resolved targets, not raw strings — they may be
        # relative-vs-absolute encodings of the same path.
        current_resolved = (link.parent / current).resolve()
        if current_resolved == run_dir:
            print(f"already published: {link} -> {run_dir}")
            return 0
        _atomic_symlink(run_dir, link)
        print(f"published: {link} -> {run_dir} (was {current})")
        return 0
    if link.is_dir():
        archived = _archive_existing_dir(link)
        print(
            f"migrated existing directory to {archived}",
        )
        _atomic_symlink(run_dir, link)
        print(f"published: {link} -> {run_dir}")
        return 0
    if link.exists():
        print(
            f"error: {link} exists but is neither a symlink nor a directory",
            file=sys.stderr,
        )
        return 1
    _atomic_symlink(run_dir, link)
    print(f"published: {link} -> {run_dir} (fresh symlink)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
