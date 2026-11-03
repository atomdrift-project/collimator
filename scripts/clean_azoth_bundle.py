#!/usr/bin/env python3
"""Clear regenerable models while preserving configured recovery auxiliaries."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from collimator import bundle, retained_components

sys.path.insert(0, str(Path(__file__).resolve().parent))
from azoth_specialist_suite import DEPLOYMENT_GROUPS  # noqa: E402

_ROUTE_FILES = (
    "model.txt",
    "model.json",
    "model.onnx",
    "feature_spec.json",
    "calibrator.json",
    "benchmark.json",
    "README.md",
    "threshold_scores.npz",
    "calibration_scores.npz",
    "threshold_tuning.json",
    "training_provenance.json",
    "training_config.json",
    "accepted_config.json",
)


def clean(root: Path) -> dict:
    root = root.resolve()
    if not root.is_dir():
        return {"status": "absent", "retained_routes": []}
    fields = retained_components.prepare(root, root / "specialists.json", check_only=True)
    protected = {item["route"] for item in fields.get("retained_components", [])}
    ordinary = {"filegroups/" + name for name in DEPLOYMENT_GROUPS}
    if protected & ordinary:
        raise ValueError(
            "ordinary training targets cannot also be frozen auxiliaries; use distinct aliases: "
            + ", ".join(sorted(protected & ordinary))
        )
    manifest = root / ".retained_components" / "manifest.json"
    if protected:
        # Nested metadata survives the top-level cleanup. Artifacts remain in
        # their normal route directories, so no duplicate model archive is needed.
        bundle.atomic_write_json(
            manifest,
            {
                "schema": "azoth.retained_components.v1",
                "fit_partition": "dev",
                "score_space": "raw",
                **fields,
                "models": [{**item, "kind": "filegroup"} for item in fields["retained_components"]],
            },
        )
    elif manifest.is_file():
        # An authoritative current config can deliberately remove auxiliaries.
        # Do not resurrect an older manifest after deleting that config.
        manifest.unlink()
    for path in root.iterdir():
        if path.is_file() and path.suffix in {".json", ".md", ".csv", ".npz"}:
            path.unlink()
    routes = [root / "general", *(root / "filegroups").glob("*"), *(root / "filetypes").glob("*")]
    for directory in routes:
        if not directory.is_dir():
            continue
        if directory.relative_to(root).as_posix() in protected:
            for name in (
                "calibrator.json",
                "README.md",
                "threshold_scores.npz",
                "calibration_scores.npz",
                "threshold_tuning.json",
            ):
                (directory / name).unlink(missing_ok=True)
            continue
        for name in _ROUTE_FILES:
            (directory / name).unlink(missing_ok=True)
        models = directory / "models"
        if models.is_symlink():
            models.unlink()
        elif models.is_dir():
            shutil.rmtree(models)
    return {"status": "cleaned", "retained_routes": sorted(protected)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--azoth-root", type=Path, required=True)
    args = parser.parse_args()
    result = clean(args.azoth_root)
    print(
        f"azoth-clean-bundle: {result['status']}; "
        f"retained {len(result['retained_routes'])} auxiliaries"
    )
