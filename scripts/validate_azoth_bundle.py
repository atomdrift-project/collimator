#!/usr/bin/env python3
"""Validate internal references in a deployed Azoth bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    with open(path) as f:
        data = json.load(
            f,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"non-standard JSON constant {value}"),
            ),
        )
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected JSON object")
    return data


def _route_path(root: Path, route: str) -> Path:
    if route == "general":
        return root / "general"
    return root / route


def _route_exists(root: Path, route: str) -> bool:
    route_dir = _route_path(root, route)
    return (route_dir / "model.txt").is_file() and (route_dir / "feature_spec.json").is_file()


def _policy_routes(policy: dict[str, Any]) -> set[str]:
    routes: set[str] = set()
    for route_name, route in policy.get("routes", {}).items():
        if not str(route_name).startswith("filetypes/"):
            raise SystemExit(f"route_policies.json: unexpected route key {route_name!r}")
        for level in route.get("levels", []):
            for severity in ("hostile", "suspicious"):
                best = level.get(severity, {}).get("best", {})
                thresholds = best.get("thresholds", {})
                if not isinstance(thresholds, dict):
                    raise SystemExit(
                        f"route_policies.json: {route_name} L{level.get('level')} {severity} thresholds must be an object",
                    )
                routes.update(str(name) for name in thresholds)
    return routes


def validate(root: Path) -> list[str]:
    config_path = root / "config.json"
    policy_path = root / "route_policies.json"
    config = _load_json(config_path)
    policy = _load_json(policy_path)
    errors: list[str] = []

    if config.get("schema") != "azoth.routed_ensemble.v1":
        errors.append(f"{config_path}: unsupported schema {config.get('schema')!r}")
    if policy.get("schema") != "azoth.route_policy_search.v1":
        errors.append(f"{policy_path}: unsupported schema {policy.get('schema')!r}")

    if not _route_exists(root, "general"):
        errors.append("general route is missing model.txt or feature_spec.json")

    configured_routes = {str(item.get("route")) for item in config.get("models", [])}
    configured_routes.discard("None")
    configured_routes.add("general")
    policy_routes = _policy_routes(policy)

    for route in sorted(configured_routes | policy_routes):
        if not _route_exists(root, route):
            errors.append(f"{route}: referenced but missing model.txt or feature_spec.json")

    for route_name, route in policy.get("routes", {}).items():
        filetype = str(route.get("filetype", ""))
        expected = f"filetypes/{filetype}"
        if route_name != expected:
            errors.append(f"{route_name}: filetype field {filetype!r} does not match route key")
        group = route.get("filegroup")
        if group is not None:
            mapped = config.get("filetype_to_group", {}).get(filetype)
            if mapped != group:
                errors.append(
                    f"{route_name}: filegroup {group!r} does not match config mapping {mapped!r}",
                )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path("out/models/azoth"))
    args = parser.parse_args()

    errors = validate(args.root)
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    print(f"azoth bundle ok: {args.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
