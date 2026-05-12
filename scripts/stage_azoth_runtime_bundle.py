#!/usr/bin/env python3
"""Stage only the azoth files needed by litmus plus markdown documentation."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

# scripts/ isn't on sys.path; reach src/ for `collimator.bundle`.
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import bundle  # noqa: E402


# Per-route files that aren't model artifacts. Model files are picked up
# separately because their location depends on layout (top-level or models/).
# Optional files (calibrator.json, README.md) are copied if present.
ROUTE_AUX_FILES = ("feature_spec.json", "README.md", "calibrator.json")
ROOT_FILES = ("config.json", "route_policies.json")


def _copy_if_exists(src: Path, dst: Path) -> None:
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _copy_route(src: Path, dst: Path) -> bool:
    if not src.is_dir():
        return False
    if not bundle.has_model(src):
        return False
    if not (src / "feature_spec.json").is_file():
        return False
    dst.mkdir(parents=True, exist_ok=True)
    # Copy model artifacts in whichever layout the source uses; the relative
    # path is preserved so litmus loads the same layout it sees during
    # validation.
    try:
        for model_path in bundle.model_files(src):
            rel = model_path.relative_to(src)
            _copy_if_exists(model_path, dst / rel)
    except ValueError as exc:
        raise SystemExit(f"{src}: {exc}") from exc
    for name in ROUTE_AUX_FILES:
        _copy_if_exists(src / name, dst / name)
    return True


def _routes_from_config(config: dict[str, Any]) -> list[str]:
    routes = ["general"]
    for model in config.get("models", []):
        route = model.get("route") if isinstance(model, dict) else None
        if isinstance(route, str) and route not in routes:
            routes.append(route)
    return routes


def stage_runtime_bundle(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)

    config_path = src / "config.json"
    if not config_path.is_file():
        raise SystemExit(f"missing required file: {config_path}")
    with config_path.open() as f:
        config = json.load(f)

    for name in ROOT_FILES:
        required = src / name
        if not required.is_file():
            raise SystemExit(f"missing required file: {required}")
        _copy_if_exists(required, dst / name)

    for path in sorted(src.glob("*.md")):
        _copy_if_exists(path, dst / path.name)
    _copy_if_exists(src / "LICENSE", dst / "LICENSE")

    missing: list[str] = []
    for route in _routes_from_config(config):
        if route == "general":
            route_src = src / "general"
            route_dst = dst / "general"
        else:
            route_src = src / route
            route_dst = dst / route
        if not _copy_route(route_src, route_dst):
            missing.append(route)

    if missing:
        joined = ", ".join(sorted(missing))
        raise SystemExit(f"missing deployable route artifacts: {joined}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=Path)
    parser.add_argument("dst", type=Path)
    args = parser.parse_args()
    stage_runtime_bundle(args.src, args.dst)
    print(f"staged runtime azoth bundle: {args.dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
