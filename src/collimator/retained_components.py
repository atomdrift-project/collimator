"""Carry validated auxiliary artifacts into a fresh calibration run.

This preserves model inputs, not old calibration decisions. The caller must
rescore the copied models, fit on dev, and run the normal reporting/deploy gates.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from . import bundle, cache_identity, data, model_config


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> dict:
    return json.loads(path.read_text())


def _scopes(config: dict) -> tuple[list[str], dict[str, list[str]]]:
    global_routes = config.get("global_auxiliary_routes", [])
    scoped = config.get("filetype_auxiliary_routes", {})
    if not isinstance(global_routes, list) or not isinstance(scoped, dict):
        raise ValueError("invalid retained auxiliary routing")
    for names in [global_routes, *scoped.values()]:
        if not isinstance(names, list) or any(not isinstance(n, str) for n in names):
            raise ValueError("auxiliary routes must be lists of names")
        if len(names) != len(set(names)):
            raise ValueError("duplicate auxiliary route")
        for name in names:
            model_config.config_path(Path("."), name)
            if not name.startswith("filegroups/"):
                raise ValueError("retained auxiliaries must be named filegroups")
    if any(not isinstance(ft, str) or not ft for ft in scoped):
        raise ValueError("invalid auxiliary filetype scope")
    return global_routes, scoped


def _identity(directory: Path) -> dict:
    cache_identity.require_reserved_dev(directory)
    models = bundle.model_files(directory)
    if not models or any(path.suffix != ".onnx" for path in models):
        raise ValueError(f"{directory}: retained models require exported ONNX artifacts")
    benchmark = _read(directory / "benchmark.json")
    env = benchmark.get("feature_env")
    if not isinstance(env, dict) or any(
        not isinstance(k, str) or not isinstance(v, str) for k, v in env.items()
    ):
        raise ValueError(f"{directory}: missing recorded feature environment")
    file_types = benchmark.get("file_types")
    if not isinstance(file_types, list) or any(not isinstance(ft, str) for ft in file_types):
        raise ValueError(f"{directory}: missing recorded source scope")
    return {
        "model_revision": cache_identity.model_revision(directory),
        "spec_revision": _hash(directory / "feature_spec.json"),
        "benchmark_sha256": _hash(directory / "benchmark.json"),
    }


def _copy_artifacts(source: Path, target: Path, expected: dict) -> None:
    if target.exists():
        if _identity(target) != expected:
            raise ValueError(
                f"retained route collision at {target}; use a distinct candidate alias"
            )
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{target.name}-retaining-", dir=target.parent))
    try:
        paths = {
            source / name
            for name in (
                "feature_spec.json",
                "benchmark.json",
                "training_provenance.json",
                "training_config.json",
                "accepted_config.json",
            )
            if (source / name).is_file()
        }
        for model in bundle.model_files(source):
            paths.add(model)
            paths.update(
                model.with_suffix(ext)
                for ext in (".txt", ".json")
                if model.with_suffix(ext).is_file()
            )
        for path in sorted(paths):
            destination = temporary / path.relative_to(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
        if _identity(temporary) != expected:
            raise ValueError(f"retained source changed while copying {source}")
        if target.exists():
            if _identity(target) != expected:
                raise ValueError(f"retained route collision at {target}")
        else:
            temporary.rename(target)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def prepare(
    root: Path,
    summary_path: Path,
    source: Path | None = None,
    *,
    check_only: bool = False,
) -> dict:
    """Preserve local/previous auxiliary models and return their config fields.

    Existing local artifacts win only when their complete identity agrees;
    conflicts fail before mutation. A preflight performs all validation without
    copying files. No score caches, calibrators, thresholds or policies are copied.
    """
    root = root.resolve()
    documents: list[tuple[Path, Path, dict]] = []
    local = root / "config.json"
    if not local.is_file():
        local = root / "retained_components.json"
    if not local.is_file():
        local = root / ".retained_components" / "manifest.json"
    if local.is_file():
        documents.append((root, local, _read(local)))
    if source is not None and source.resolve() != root:
        source = source.resolve()
        path = source / "config.json"
        documents.append((source, path, _read(path)))

    # Keep source order: policy-search tie breaking can depend on input order.
    global_routes: dict[str, None] = {}
    scopes: dict[str, dict[str, None]] = {}
    planned: dict[str, tuple[Path, dict, dict]] = {}
    sources = []
    for directory, path, config in documents:
        global_names, scoped_names = _scopes(config)
        names = set(global_names).union(*(set(v) for v in scoped_names.values()))
        if not names:
            continue
        if config.get("fit_partition") != "dev" or config.get("score_space") != "raw":
            raise ValueError(f"{path}: retained components require a raw-score dev-fit bundle")
        records = {record["route"]: record for record in config["models"]}
        retained_records = {
            record["route"]: record for record in config.get("retained_components", [])
        }
        if not names <= records.keys():
            raise ValueError(f"{path}: auxiliary route is absent from model manifest")
        for name in sorted(names):
            artifact = directory / name
            identity = _identity(artifact)
            if any(
                records[name].get(key) != identity[key]
                for key in ("model_revision", "spec_revision")
            ):
                raise ValueError(f"{artifact}: artifact differs from source manifest")
            benchmark_hash = records[name].get("benchmark_sha256") or retained_records.get(
                name, {}
            ).get("benchmark_sha256")
            if benchmark_hash is not None and benchmark_hash != identity["benchmark_sha256"]:
                raise ValueError(f"{artifact}: benchmark differs from retention manifest")
            benchmark = _read(artifact / "benchmark.json")
            if name in planned and planned[name][1] != identity:
                raise ValueError(
                    f"conflicting retained route {name}; use distinct candidate aliases"
                )
            destination = root / name
            if destination.exists() and _identity(destination) != identity:
                raise ValueError(f"retained route collision at {destination}")
            planned.setdefault(name, (artifact, identity, benchmark))
        global_routes.update(dict.fromkeys(global_names))
        for ft, names_for_type in scoped_names.items():
            scopes.setdefault(ft, {}).update(dict.fromkeys(names_for_type))
        sources.append({"directory": str(directory), "manifest_sha256": _hash(path)})

    if not planned:
        return {}
    # Keep the original scoring domain for full-source L0 anchors. A route
    # used globally must be scored globally even if it trained on a subset.
    summaries = {}
    for name, (_, _, benchmark) in planned.items():
        original_scope = benchmark["file_types"]
        scoring_scope = (
            [] if name in global_routes else list(data.expand_route_filetypes(original_scope))
        )
        routed_types = {ft for ft, names in scopes.items() if name in names}
        if scoring_scope and not routed_types <= {data.route_filetype(ft) for ft in scoring_scope}:
            raise ValueError(f"{name}: routed filetypes exceed its recorded source scope")
        summaries[name] = {
            **benchmark,
            "name": name.removeprefix("filegroups/"),
            "kind": "filegroup",
            "file_types": scoring_scope,
            "output_dir": str(root / name),
            "retained_artifact": True,
        }
    fields = {
        "global_auxiliary_routes": list(global_routes),
        "filetype_auxiliary_routes": {ft: list(names) for ft, names in sorted(scopes.items())},
        "retained_components": [
            {"route": name, **identity} for name, (_, identity, _) in sorted(planned.items())
        ],
    }
    if check_only:
        return fields
    summary = _read(summary_path)
    kept = [
        row
        for row in summary["results"]
        if not (row.get("kind") == "filegroup" and "filegroups/" + str(row.get("name")) in planned)
    ]
    for name, (artifact, identity, _) in sorted(planned.items()):
        _copy_artifacts(artifact, root / name, identity)
    summary["results"] = kept + [summaries[name] for name in sorted(summaries)]
    bundle.atomic_write_json(summary_path, summary)
    bundle.atomic_write_json(
        root / "retained_components.json",
        {
            "schema": "azoth.retained_components.v1",
            "fit_partition": "dev",
            "score_space": "raw",
            **fields,
            "models": [
                {"route": name, "kind": "filegroup", **identity}
                for name, (_, identity, _) in sorted(planned.items())
            ],
            "sources": sources,
            "method": (
                "Exact artifacts retained; fresh scoring/calibration "
                "and normal gates still required."
            ),
        },
    )
    return fields
