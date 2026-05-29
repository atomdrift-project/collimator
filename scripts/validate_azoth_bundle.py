#!/usr/bin/env python3
"""Validate internal references in a deployed Azoth bundle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# scripts/ isn't on sys.path by default when invoked as a CLI; add the
# package root so `from collimator.bundle import ...` works without an editable
# install during ad-hoc validation.
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import bundle, export  # noqa: E402  — late import after sys.path patch


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
    return bundle.has_model(route_dir) and (route_dir / "feature_spec.json").is_file()


def _ensemble_feature_count_errors(root: Path, route: str) -> list[str]:
    """Catch the failure mode where a multi-seed bundle has members with
    different feature counts — e.g. a stale `seed_<S>.txt` from a prior run
    that used a different feature spec lingers next to fresh seeds. The
    runtime detects this when loading the model, but only after the entire
    deploy pipeline has run; checking it here saves ~11 hours.
    """
    route_dir = _route_path(root, route)
    files = bundle.model_files(route_dir)
    if len(files) < 2:
        return []
    counts: dict[Path, int] = {}
    for path in files:
        if path.suffix != ".txt":
            continue
        with open(path) as f:
            for line in f:
                if line.startswith("max_feature_idx="):
                    counts[path] = int(line.split("=", 1)[1].strip()) + 1
                    break
                if line.startswith("Tree="):
                    break
    if len(set(counts.values())) <= 1:
        return []
    detail = ", ".join(f"{p.name}={n}" for p, n in sorted(counts.items()))
    return [f"{route}: ensemble members disagree on feature count ({detail})"]


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
        errors.append("general route is missing model file or feature_spec.json")

    configured_routes = {str(item.get("route")) for item in config.get("models", [])}
    configured_routes.discard("None")
    configured_routes.add("general")
    policy_routes = _policy_routes(policy)

    for route in sorted(configured_routes | policy_routes):
        if not _route_exists(root, route):
            errors.append(f"{route}: referenced but missing model file or feature_spec.json")
        else:
            errors.extend(_ensemble_feature_count_errors(root, route))
            # Degenerate routes must never ship: they carry no signal and
            # (being .txt-only constant predictors) can't even export to ONNX.
            # Calibration drops them upstream; this is the hard deploy gate.
            if export.route_model_is_degenerate(_route_path(root, route)):
                errors.append(f"{route}: constant-predictor model must not be deployed")
            # ONNX-only deploy: litmus no longer loads .txt/.json. Any native
            # dump in the staged bundle means a seed has no .onnx sibling.
            native = sorted(
                p.name
                for p in bundle.model_files(_route_path(root, route))
                if p.suffix != ".onnx"
            )
            if native:
                errors.append(f"{route}: non-ONNX model(s) {native} must not be deployed")

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
