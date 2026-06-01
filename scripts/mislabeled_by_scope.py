#!/usr/bin/env python3
"""Score-table-driven mislabeled-sample report, scoped by route kind.

Reads ``score_table.npz`` (per-route scores for the full corpus) and
``route_policies.json`` (per-filetype OR-rule thresholds at each level)
and emits a JSON report compatible with ``scripts/triage_error_samples.py``
and ``scripts/archive_error_samples.py``.

Kinds:
  false-positives — benigns flagged (any route in scope ≥ its threshold).
                    Ranked by max-margin desc (most-confidently-flagged first).
  false-negatives — malware missed (no route in scope ≥ its threshold).
                    Ranked by max-margin asc (most-deeply-missed first).

Scopes (apply identically to FP and FN). ``--scope`` accepts a
comma-separated list; rows are deduped by row_id across scopes and the
``scopes`` field on each output row lists which scopes flagged it.

  ensemble    — the deployed OR-rule for each row's filetype (= what
                ``litmus`` would flag in production).
  specialists — restrict the OR to routes whose name starts with
                ``filetypes/``.
  filegroups  — restrict the OR to routes whose name starts with
                ``filegroups/``.
  any         — flag a row if ANY route's score exceeds that route's
                MOST PERMISSIVE per-filetype operating threshold at this
                (level, severity). Surfaces edge cases the ensemble
                correctly suppresses but where a route alone would fire.
  route:<name> — single named route, e.g. ``route:filetypes/jpeg``.
                Uses the threshold from that route's home filetype
                policy (e.g. ``filetypes/jpeg``) at (level, severity).

Common combined-pool invocation:
  --scope ensemble,specialists,filegroups
This unions errors visible to each of the three deploy-relevant scopes
into one deduped triage list — captures (a) what production flags,
(b) what any specialist alone would flag (sometimes broader than
ensemble when the deployed policy is a blend), and (c) what any
filegroup route would flag.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from collimator.thresholds import DEFAULT_SEVERITY_LEVEL  # noqa: E402


def _load_paths(db_dsn: str, row_ids: list[int]) -> dict[int, tuple[str, str]]:
    """Bulk-fetch (sha256, path) by id from hopper.samples."""
    if not row_ids:
        return {}
    try:
        import psycopg
    except ImportError:
        sys.exit("psycopg is required to resolve row_id → (sha256, path); install it or pre-populate")
    out: dict[int, tuple[str, str]] = {}
    with psycopg.connect(db_dsn, connect_timeout=10) as conn, conn.cursor() as cur:
        cur.execute("SELECT id, sha256, path FROM samples WHERE id = ANY(%s)", (list(row_ids),))
        for rid, sha, path in cur.fetchall():
            out[int(rid)] = (sha, path)
    return out


def _per_filetype_thresholds(
    policy: dict[str, Any],
    level: int,
    severity: str,
) -> dict[str, dict[str, float]]:
    """Map filetype → {route: threshold} for (level, severity).

    For policies whose ``best`` is a ``learned_blend_*`` (no per-route
    thresholds — uses a logit blend with a single threshold), fall back
    to the first ``joint_or_at_fp_*`` candidate that has non-empty
    per-route thresholds. This surrogate operates at a roughly equivalent
    FP budget and lets per-route scope filtering still work for those
    filetypes. ``ensemble`` scope retains the blend-aware semantics via
    a separate ``_blends`` mapping if you call ``_per_filetype_blends``.
    """
    out: dict[str, dict[str, float]] = {}
    for route_key, entry in policy.get("routes", {}).items():
        if not route_key.startswith("filetypes/"):
            continue
        ft = route_key.split("/", 1)[1]
        levels = entry.get("levels") or []
        # Find by level value first (new per-100M grid), fall back to
        # positional index for legacy route_policies.json that predate
        # the grid change. If neither works, skip.
        level_entry = next(
            (lev for lev in levels if int(lev.get("level", -1)) == level),
            None,
        )
        if level_entry is None:
            if 0 <= level < len(levels):
                level_entry = levels[level]
            else:
                continue
        sev = (level_entry.get(severity) or {})
        best = sev.get("best") or {}
        ts = best.get("thresholds") or {}
        if not ts:
            for cand in sev.get("candidates") or []:
                pol = str(cand.get("policy") or "")
                if pol.startswith("joint_or_at_fp") and cand.get("thresholds"):
                    ts = cand["thresholds"]
                    break
        if ts:
            out[ft] = {r: float(t) for r, t in ts.items()}
    return out


def _global_min_thresholds(per_ft: dict[str, dict[str, float]]) -> dict[str, float]:
    """For ``any`` scope: minimum threshold per route across all filetype policies."""
    out: dict[str, float] = {}
    for thresholds in per_ft.values():
        for route, t in thresholds.items():
            if route not in out or t < out[route]:
                out[route] = t
    return out


def _route_index(route_names: np.ndarray) -> dict[str, int]:
    return {str(name): idx for idx, name in enumerate(route_names)}


def _row_thresholds_for_scope(
    scope: str,
    filetype: str,
    per_ft: dict[str, dict[str, float]],
    global_min: dict[str, float],
    explicit_route: str | None,
) -> dict[str, float]:
    """Return {route: threshold} for one row under the requested scope."""
    if scope == "any":
        return global_min
    if scope == "route":
        if not explicit_route:
            return {}
        # Use the route's home-filetype policy if it's a filetype route;
        # otherwise (general / filegroups/*) fall back to global-min across
        # filetype policies (since these routes aren't keyed by filetype).
        if explicit_route.startswith("filetypes/"):
            home = explicit_route.split("/", 1)[1]
            t = per_ft.get(home, {}).get(explicit_route)
        else:
            t = global_min.get(explicit_route)
        return {explicit_route: t} if t is not None else {}

    ft_thresholds = per_ft.get(filetype, {})
    if scope == "ensemble":
        return ft_thresholds
    if scope == "specialists":
        return {r: t for r, t in ft_thresholds.items() if r.startswith("filetypes/")}
    if scope == "filegroups":
        return {r: t for r, t in ft_thresholds.items() if r.startswith("filegroups/")}
    raise SystemExit(f"unknown scope: {scope}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--score-table", default="out/models/azoth/score_table.npz", type=Path)
    p.add_argument("--route-policies", default="out/models/azoth/route_policies.json", type=Path)
    p.add_argument(
        "--kind",
        choices=["false-positives", "false-negatives"],
        default="false-positives",
        help="false-positives: benigns flagged. false-negatives: malware missed.",
    )
    p.add_argument(
        "--scope",
        required=True,
        help=(
            "Comma-separated list of scopes. Each one of: ensemble | "
            "specialists | filegroups | any | route:<name>. Rows are "
            "deduped across scopes; ``scopes`` field on each output row "
            "lists which scope(s) flagged it. Single scope (no comma) "
            "preserves legacy behavior."
        ),
    )
    p.add_argument(
        "--level",
        type=int,
        default=DEFAULT_SEVERITY_LEVEL,
        help=(
            f"Severity level on the per-100M scale (default "
            f"{DEFAULT_SEVERITY_LEVEL} = {DEFAULT_SEVERITY_LEVEL/100:.2f} FP/M; "
            f"any integer in 0..=1000 supported by the current grid; sourced "
            f"from collimator.thresholds.DEFAULT_SEVERITY_LEVEL). Note: "
            f"historical route_policies.json files predating the grid change "
            f"may not have an entry at this level; supply --level explicitly "
            f"to match the file's available levels."
        ),
    )
    p.add_argument(
        "--severity",
        choices=["hostile"],
        default="hostile",
    )
    p.add_argument("--top-errors", type=int, default=100)
    p.add_argument(
        "--skip",
        type=int,
        default=0,
        help="Skip the first N ranked rows before taking --top-errors. Use to "
             "page past samples you've already reviewed.",
    )
    p.add_argument("--output", required=True, type=Path)
    p.add_argument(
        "--db",
        default=os.environ.get("DB", ""),
        help="Hopper DSN to resolve row_id → sha256/path (default $DB).",
    )
    args = p.parse_args()

    raw_scopes = [s.strip() for s in str(args.scope).split(",") if s.strip()]
    if not raw_scopes:
        raise SystemExit("--scope must list at least one scope")
    # Parse each scope into (canonical_name, explicit_route_or_None).
    scope_specs: list[tuple[str, str, str | None]] = []  # (raw, canonical, explicit_route)
    for raw in raw_scopes:
        canon = raw
        explicit: str | None = None
        if canon.startswith("route:"):
            explicit = canon.split(":", 1)[1]
            canon = "route"
        if canon not in {"ensemble", "specialists", "filegroups", "any", "route"}:
            raise SystemExit(f"invalid --scope entry: {raw}")
        scope_specs.append((raw, canon, explicit))

    is_fp = args.kind == "false-positives"
    target_label = 0 if is_fp else 1

    table = np.load(args.score_table, allow_pickle=False)
    row_ids: np.ndarray = table["row_ids"]
    labels: np.ndarray = table["labels"]
    file_types: np.ndarray = table["file_types"]
    route_names: np.ndarray = table["route_names"]
    scores: np.ndarray = table["scores"]  # (R, N)

    policy = json.loads(args.route_policies.read_text())
    per_ft = _per_filetype_thresholds(policy, args.level, args.severity)
    global_min = _global_min_thresholds(per_ft)
    r_idx = _route_index(route_names)

    target_mask = labels == target_label
    n_target = int(target_mask.sum())
    print(
        f"{'benigns' if is_fp else 'malware'} in score table: {n_target:,}",
        file=sys.stderr,
    )

    # Per-row aggregated state across scopes:
    #   row_i -> {
    #     "margin": best-margin (max for FP, min for FN),
    #     "scopes": set of scope names that flagged this row,
    #     "trigs": {(route, score, threshold)} — union across scopes,
    #   }
    agg: dict[int, dict[str, Any]] = {}
    unique_fts = np.unique(file_types[target_mask])

    for raw_scope, canon_scope, explicit_route in scope_specs:
        scope_flagged = 0
        for ft in unique_fts:
            ft_str = str(ft)
            thresholds = _row_thresholds_for_scope(
                canon_scope, ft_str, per_ft, global_min, explicit_route
            )
            if not thresholds:
                continue
            contributing: list[tuple[int, str, float]] = []
            for route_name, t in thresholds.items():
                ridx = r_idx.get(route_name)
                if ridx is None:
                    continue
                contributing.append((ridx, route_name, t))
            if not contributing:
                continue
            ft_mask = target_mask & (file_types == ft)
            ft_row_indices = np.flatnonzero(ft_mask)
            if not ft_row_indices.size:
                continue
            # margin per row: max(score - threshold) across contributing routes.
            # NaN scores (route didn't run / not applicable to this filetype)
            # are excluded — they contribute neither a hit nor a deficit.
            margins = np.full(ft_row_indices.shape, -np.inf, dtype=np.float64)
            any_finite = np.zeros(ft_row_indices.shape, dtype=bool)
            for ridx, _, t in contributing:
                row_scores = scores[ridx, ft_row_indices].astype(np.float64)
                finite = np.isfinite(row_scores)
                delta = np.where(finite, row_scores - t, -np.inf)
                margins = np.where(finite & (delta > margins), delta, margins)
                any_finite |= finite
            if is_fp:
                hit = margins >= 0
            else:
                hit = any_finite & (margins < 0)
            if not hit.any():
                continue
            for pos in np.flatnonzero(hit):
                row_i = int(ft_row_indices[pos])
                margin = float(margins[pos])
                row_trigs: list[tuple[str, float, float]] = []
                if is_fp:
                    for ridx, route_name, t in contributing:
                        s = float(scores[ridx, row_i])
                        if s >= t:
                            row_trigs.append((route_name, s, t))
                else:
                    for ridx, route_name, t in contributing:
                        s = float(scores[ridx, row_i])
                        row_trigs.append((route_name, s, t))
                entry = agg.get(row_i)
                if entry is None:
                    agg[row_i] = {
                        "margin": margin,
                        "scopes": {raw_scope},
                        "trigs": {(r, s, t) for r, s, t in row_trigs},
                    }
                else:
                    if is_fp:
                        entry["margin"] = max(entry["margin"], margin)
                    else:
                        entry["margin"] = min(entry["margin"], margin)
                    entry["scopes"].add(raw_scope)
                    entry["trigs"].update((r, s, t) for r, s, t in row_trigs)
                scope_flagged += 1
        print(
            f"  scope={raw_scope}: flagged {scope_flagged:,} row-hits "
            f"(running unique total {len(agg):,})",
            file=sys.stderr,
        )

    # Flatten and sort. FPs: largest margin first. FNs: smallest first.
    flat = [(entry["margin"], row_i, entry) for row_i, entry in agg.items()]
    flat.sort(key=lambda x: -x[0] if is_fp else x[0])
    skip = max(0, int(args.skip))
    top = flat[skip : skip + args.top_errors]
    print(
        f"flagged: {len(flat):,} (deduped across {len(scope_specs)} scope(s)), "
        f"skipping {skip}, taking {len(top)}",
        file=sys.stderr,
    )

    selected_row_ids = [int(row_ids[t[1]]) for t in top]
    paths = _load_paths(args.db, selected_row_ids) if args.db else {}
    if args.db and len(paths) < len(selected_row_ids):
        missing = len(selected_row_ids) - len(paths)
        print(f"WARN: {missing}/{len(selected_row_ids)} row_ids missing in DB", file=sys.stderr)

    rows_out: list[dict[str, Any]] = []
    for margin, row_i, entry in top:
        rid = int(row_ids[row_i])
        sha, path = paths.get(rid, ("", ""))
        trigs = list(entry["trigs"])
        # For FPs the headline route is the one with the largest delta.
        # For FNs the same — most permissive (smallest threshold shortfall).
        headline = max(trigs, key=lambda x: x[1] - x[2]) if trigs else None
        rows_out.append({
            "row_id": rid,
            "sha256": sha,
            "path": path,
            "label": "good" if is_fp else "bad",
            "filetype": str(file_types[row_i]),
            "probability": headline[1] if headline else 0.0,
            "margin": margin,
            "scope": args.scope,
            "scopes_flagged": sorted(entry["scopes"]),
            "level": args.level,
            "severity": args.severity,
            "headline_route": headline[0] if headline else "",
            "routes": [
                {"route": r, "score": s, "threshold": t} for (r, s, t) in trigs
            ],
        })

    # Schema matches what archive_error_samples._rows / triage_error_samples
    # expect for each kind: FP → "false_positives", FN → "uncaught".
    payload = {
        "corpus": "score_table",
        "score_table": str(args.score_table),
        "route_policies": str(args.route_policies),
        "kind": args.kind,
        "scope": args.scope,
        "scopes": [raw for raw, _, _ in scope_specs],
        "level": args.level,
        "severity": args.severity,
        "raw_count": len(flat),
        "skip": skip,
    }
    payload["false_positives" if is_fp else "uncaught"] = rows_out
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2))
    print(
        f"wrote {args.output} ({len(rows_out)} rows, {len(flat):,} total deduped {args.kind})",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
