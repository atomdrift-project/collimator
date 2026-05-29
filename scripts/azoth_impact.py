#!/usr/bin/env python3
"""Detect which routes / filetypes are impacted by a bundle change.

When a promote modifies one route (say filegroups/native), only a subset
of the deploy validation pipeline actually needs to recompute — the rest
can be carried forward from the previous bundle's outputs. This module
provides the shared "what's impacted" logic used by both:

  * ``azoth_route_policy_search``  — skip policy reselection for filetypes
                                     whose routes didn't change.
  * ``compute_routed_metrics``      — copy unchanged filetype entries from
                                     the previous bundle's metrics JSON.

The impact analysis is exact, not heuristic: it hashes each route's raw
scores in the current vs previous score_table.npz. If a route's scores
are bytewise-identical between bundles, that route is unchanged. A
filetype is unchanged when ALL of its scoring routes (general, its
filegroup parent, its own filetype specialist if any) are unchanged.
Anything else recomputes from scratch.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Iterable

import numpy as np


LOG = logging.getLogger("azoth_impact")


def route_model_hashes(bundle_path: Path) -> dict[str, str]:
    """Return ``{route_name: sha256_of_(model + feature_spec)}`` for every
    route in the bundle.

    Why model files, not score values: a route's score for any given row
    is a pure function of (model, feature_spec, row_features). Two bundles
    with identical models + feature_specs will produce identical scores
    on any common row, regardless of when their score_tables were
    computed or what snapshot they used. Hashing the model file is the
    correct invariant; hashing score_table values fails because the
    table includes rows that may differ between the candidate and the
    deployed bundle (different snapshot_max_id → different row sets →
    different bytes even when the model is identical).

    Hash includes feature_spec.json because changing features changes
    the input vector → different scores → different policy decisions
    even with the same model.

    Returns an empty dict if the bundle doesn't exist (first deploy).
    Routes without a model file (e.g., the bundle is partially staged)
    are silently omitted — caller treats them as "changed" by absence.
    """
    if not bundle_path.is_dir():
        return {}
    out: dict[str, str] = {}
    # Enumerate the routes from the bundle's config.json — that's the
    # authoritative list of what the bundle ships. Falls back to a
    # directory walk if config is missing.
    config_path = bundle_path / "config.json"
    routes: list[str] = ["general"]
    if config_path.is_file():
        try:
            with open(config_path) as f:
                config = __import__("json").load(f)
            for m in config.get("models", []):
                if isinstance(m, dict) and isinstance(m.get("route"), str):
                    r = m["route"]
                    if r not in routes:
                        routes.append(r)
        except (OSError, ValueError):
            pass
    for route in routes:
        if route == "general":
            route_dir = bundle_path / "general"
        else:
            route_dir = bundle_path / route
        if not route_dir.is_dir():
            continue
        # Collect CANONICAL model files only — the ones that determine
        # litmus's runtime behavior. The hash must be agnostic to which
        # additional format-files are present in the bundle layout
        # (e.g. a training bundle ships model.onnx + model.txt; the
        # staged runtime bundle keeps only model.onnx). If we hashed
        # the file SET, those two would look "different" even when the
        # underlying model is byte-identical, and impact detection
        # would think every route changed.
        #
        # Priority: ONNX > TXT > JSON, matching bundle.model_files()
        # and bundle.Ensemble.load_bundle. For multi-seed, hash each
        # seed's preferred-format file. For legacy single-seed, hash
        # the top-priority root-level model file.
        files_to_hash: list[tuple[str, Path]] = []
        spec_path = route_dir / "feature_spec.json"
        if spec_path.is_file():
            files_to_hash.append(("feature_spec.json", spec_path))

        # Multi-seed layout: dedup per-stem across formats.
        models_dir = route_dir / "models"
        if models_dir.is_dir():
            seed_files: dict[str, Path] = {}
            ext_priority = {".onnx": 0, ".txt": 1, ".json": 2}
            for p in sorted(models_dir.iterdir()):
                if not p.is_file() or not p.name.startswith("seed_"):
                    continue
                if p.suffix not in ext_priority:
                    continue
                existing = seed_files.get(p.stem)
                if existing is None or ext_priority[p.suffix] < ext_priority[existing.suffix]:
                    seed_files[p.stem] = p
            for stem in sorted(seed_files.keys()):
                files_to_hash.append((stem, seed_files[stem]))

        # Legacy single-seed: pick first available by priority. Skip if
        # multi-seed already covered (multi-seed wins per
        # bundle.model_files()).
        if not models_dir.is_dir() or not any(p.is_file() and p.name.startswith("seed_") for p in models_dir.iterdir()):
            for name in ("model.onnx", "model.txt", "model.json"):
                p = route_dir / name
                if p.is_file():
                    files_to_hash.append(("model", p))
                    break  # first match wins

        if not files_to_hash:
            continue
        h = hashlib.sha256()
        for label, p in files_to_hash:
            # Tag with a CANONICAL label (not file basename) so the
            # same logical artifact has the same hash regardless of
            # which format-file ships it. "model" is the same whether
            # it's model.onnx or model.txt; "seed_42" is the same
            # whether it's seed_42.onnx or seed_42.txt.
            h.update(label.encode("utf-8"))
            h.update(b"\x00")
            try:
                with open(p, "rb") as f:
                    while True:
                        buf = f.read(1 << 16)
                        if not buf:
                            break
                        h.update(buf)
            except OSError:
                continue
        out[route] = h.hexdigest()
    return out


# Back-compat shim: older callers passed a score_table.npz path.
# The function now lives on route_model_hashes which hashes the
# correct invariant (model + spec, not transient score-table values).
route_score_hashes = route_model_hashes


def changed_routes(
    current_path: Path, previous_path: Path,
) -> tuple[set[str], dict[str, str]]:
    """Return (changed_route_names, current_hashes).

    A route is "changed" when:
      - It exists in the current bundle AND its model+spec hash differs
        from the previous one, OR
      - It exists in the current bundle but NOT in the previous one
        (new route), OR
      - It exists in the previous bundle but NOT in the current one
        (removed route — counts as changed so downstream caches drop it).

    Accepts either bundle directories or per-route hash maps via paths.
    The current_hashes map is returned for logging/inspection.
    """
    # Both paths are bundle directories. (Earlier versions of this
    # function took score_table.npz paths; we now hash models. If
    # someone passes a path ending in .npz we treat it as the bundle
    # directory containing it — backward-compat best effort.)
    def _resolve_bundle_dir(p: Path) -> Path:
        if p.is_dir():
            return p
        # If pointed at score_table.npz, hop up to the parent.
        if p.suffix == ".npz":
            return p.parent
        return p
    current = route_model_hashes(_resolve_bundle_dir(current_path))
    previous = route_model_hashes(_resolve_bundle_dir(previous_path))
    if not previous:
        # Previous bundle absent → everything is "changed" from null.
        return set(current.keys()), current
    changed: set[str] = set()
    for route, h in current.items():
        if previous.get(route) != h:
            changed.add(route)
    for route in previous:
        if route not in current:
            changed.add(route)
    return changed, current


def filetype_to_relevant_routes(
    file_types: Iterable[str],
    deployment_groups: dict[str, tuple[str, ...]],
    available_routes: set[str],
) -> dict[str, set[str]]:
    """Map each filetype to the routes that contribute to its ensemble.

    Currently the deploy ensemble for a filetype X considers up to three
    scoring routes:
      1. ``general``               — always present
      2. ``filegroups/<parent>``   — when X is in a deployment group
      3. ``filetypes/<X>``         — when X has its own specialist
    Routes that aren't in ``available_routes`` are dropped (the
    score_table only has the routes that actually got trained).
    """
    # Invert deployment_groups: filetype → parent filegroup name.
    parent_of: dict[str, str] = {}
    for group, members in deployment_groups.items():
        for member in members:
            parent_of[member] = group
    out: dict[str, set[str]] = {}
    for ft in file_types:
        relevant: set[str] = set()
        if "general" in available_routes:
            relevant.add("general")
        if ft in parent_of:
            fg_route = f"filegroups/{parent_of[ft]}"
            if fg_route in available_routes:
                relevant.add(fg_route)
        ft_route = f"filetypes/{ft}"
        if ft_route in available_routes:
            relevant.add(ft_route)
        out[ft] = relevant
    return out


def unchanged_filetypes(
    changed: set[str],
    deployment_groups: dict[str, tuple[str, ...]],
    available_routes: set[str],
    candidate_filetypes: Iterable[str],
) -> set[str]:
    """Return the subset of ``candidate_filetypes`` whose ensemble would
    produce identical scores given the routes in ``changed``. A filetype
    is unchanged iff none of its relevant routes are in the changed set.
    """
    ft_map = filetype_to_relevant_routes(candidate_filetypes, deployment_groups, available_routes)
    unchanged: set[str] = set()
    for ft, routes in ft_map.items():
        if routes.isdisjoint(changed):
            unchanged.add(ft)
    return unchanged


def log_impact_summary(
    changed: set[str], all_routes: Iterable[str], all_filetypes: Iterable[str],
    unchanged_fts: set[str],
) -> None:
    """Log a one-shot summary of what an impact analysis identified.
    Caller hands us the four-tuple and we emit a single readable line.
    """
    all_routes_list = list(all_routes)
    all_fts_list = list(all_filetypes)
    LOG.info(
        "impact: %d/%d routes changed (%s); %d/%d filetypes affected, "
        "%d unchanged (can carry forward)",
        len(changed), len(all_routes_list),
        ", ".join(sorted(changed)) if changed else "none",
        len(all_fts_list) - len(unchanged_fts), len(all_fts_list),
        len(unchanged_fts),
    )
