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
# Optional files (README.md, recall curve) are copied if present. The per-route
# isotonic calibrator is no longer emitted or staged — deploy runs on raw
# probabilities (see project_calibrator_decision_irrelevant); excluding it here
# also strips any stale calibrator.json from older bundles being restaged.
ROUTE_AUX_FILES = ("feature_spec.json", "README.md", "recall_curve.svg")
ROOT_FILES = ("config.json", "route_policies.json")

# Optional root files. Deploy proceeds without them, but downstream
# tools (regression check, dashboards) read them when present.
OPTIONAL_ROOT_FILES = (
    "per_filetype_metrics.json",
    "test_metrics.json",
    "route_policy_eval_oof.json",
    "route_policy_eval_oof.md",
)


def _copy_if_exists(src: Path, dst: Path) -> None:
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _stage_feature_spec(src: Path, dst: Path) -> None:
    """Copy feature_spec.json, re-deriving the offset-written families' vocabs
    (presence/bigram/trigram) as the UNION of each family's paths in
    feature_names.

    The allowlist prune can leave a path in feature_names for only one side of a
    pair (e.g. maxcrit:X kept while present:X is dropped). Without the path in the
    vocab, litmus can't produce the surviving member — it extracts as a silent
    zero and logs "feature spec contains features unknown to this extractor".
    Re-deriving here (not just at FeatureSpec.save time) makes every staged
    bundle self-consistent regardless of how the source spec was produced, so a
    plain `make deploy` of an already-trained bundle ships clean specs too.
    """
    if not src.is_file():
        return

    def _union(names: list[str], prefixes: tuple[str, ...]) -> list[str]:
        seen: dict[str, None] = {}
        for name in names:
            for prefix in prefixes:
                if name.startswith(prefix):
                    seen.setdefault(name[len(prefix):], None)
                    break
        return list(seen)

    with src.open() as f:
        spec = json.load(f)
    names = spec.get("feature_names") or []
    if names:
        spec["presence_vocab"] = _union(names, ("present:", "maxcrit:"))
        spec["bigram_vocab"] = _union(names, ("bigrams:", "unsigned_bigram:"))
        spec["trigram_vocab"] = _union(names, ("trigram:",))
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w") as f:
        json.dump(spec, f, indent=2)


def _copy_route(src: Path, dst: Path) -> bool:
    if not src.is_dir():
        return False
    if not bundle.has_model(src):
        return False
    if not (src / "feature_spec.json").is_file():
        return False
    # The deployed bundle is ONNX-only — litmus no longer loads .txt/.json.
    # model_files() already prefers .onnx per seed, so any non-ONNX artifact
    # here means that seed has no .onnx sibling: refuse to deploy it.
    try:
        model_paths = bundle.model_files(src)
    except ValueError as exc:
        raise SystemExit(f"{src}: {exc}") from exc
    non_onnx = sorted(p.name for p in model_paths if p.suffix != ".onnx")
    if non_onnx:
        raise SystemExit(
            f"{src}: ONNX-only deploy but route ships non-ONNX model(s) {non_onnx}; "
            f"regenerate so every seed has an .onnx sibling (litmus dropped the "
            f"LightGBM/XGBoost loaders)."
        )
    dst.mkdir(parents=True, exist_ok=True)
    # Preserve the source layout (top-level or models/) so litmus loads the
    # same layout it sees during validation.
    for model_path in model_paths:
        _copy_if_exists(model_path, dst / model_path.relative_to(src))
    for name in ROUTE_AUX_FILES:
        if name == "feature_spec.json":
            _stage_feature_spec(src / name, dst / name)
        else:
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

    for name in OPTIONAL_ROOT_FILES:
        _copy_if_exists(src / name, dst / name)

    for path in sorted(src.glob("*.md")):
        _copy_if_exists(path, dst / path.name)
    # Per-level recall curves are sibling SVGs to README.md and are referenced
    # by `<img src="recall_curve.svg">` in the markdown. Codeberg's renderer
    # strips inline `<svg>` so the chart MUST be an external file. Copy all
    # SVGs alongside the markdown — small (~30KB each), and lets the README
    # actually display the curves it references.
    for path in sorted(src.glob("*.svg")):
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
