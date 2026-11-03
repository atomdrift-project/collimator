#!/usr/bin/env python3
"""Score-table-driven mislabeled-sample report, scoped by route kind.

Reads ``score_table.npz`` (per-route scores for the full corpus) and
``route_policies.json`` (per-filetype decisions at each level)
and emits a JSON report compatible with ``scripts/triage_error_samples.py``
and ``scripts/archive_error_samples.py``.

Kinds:
  false-positives — benigns flagged by the scope's decision.
                    Ranked by max-margin desc (most-confidently-flagged first).
  false-negatives — malware missed by the scope's decision.
                    Ranked by max-margin asc (most-deeply-missed first).

Scopes (apply identically to FP and FN). ``--scope`` accepts a
comma-separated list; rows are deduped by row_id across scopes and the
``scopes`` field on each output row lists which scopes flagged it.

  ensemble    — the deployed cumulative policy, including blends and
                the general-threshold fallback when no usable grid exists.
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
from collimator import policy as frozen_policy  # noqa: E402
from collimator.thresholds import DEFAULT_SEVERITY_LEVEL  # noqa: E402


def _load_paths(db_dsn: str, row_ids: list[int]) -> dict[int, tuple[str, str, str, str, str]]:
    """Bulk-fetch (sha256, path, parent, label, skip) by id from hopper.samples.

    ``parent`` is the sha256 of the containing archive for extracted members
    (empty for standalone files). Triage uses it to pull the whole archive by
    sha — reliable even when the archive isn't itself a tracked sample row.

    Deliberately NOT gated on ``LABELED_WHERE``: a row the operator has since
    moved to another pool (good ↔ bad, or out to purgatory/sighted), or that
    hopper has flagged (``skip`` set), still resolves here and carries its
    CURRENT label. The score table's verdict for such a row is stale, so triage
    shouldn't spend a download on it — but it should say WHY, which it can only
    do if the row comes back. Gating here would make an already-relocated
    sample indistinguishable from one deleted outright. The comparison and the
    skipping live in ``triage_error_samples``.
    """
    if not row_ids:
        return {}
    try:
        import psycopg
    except ImportError:
        sys.exit("psycopg is required to resolve row_id → (sha256, path); "
                 "install it or pre-populate")
    out: dict[int, tuple[str, str, str, str, str]] = {}
    with psycopg.connect(db_dsn, connect_timeout=10) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, sha256, path, parent, label, skip FROM samples WHERE id = ANY(%s)",
            (list(row_ids),),
        )
        for rid, sha, path, parent, label, skip in cur.fetchall():
            out[int(rid)] = (sha, path, parent or "", label or "", skip or "")
    return out


def _policy_levels(levels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Preserve explicit levels; old unlabeled grids used positional levels."""
    return [{**item, "level": int(item.get("level", index))}
            for index, item in enumerate(levels)]


def _per_filetype_thresholds(
    policy: dict[str, Any],
    level: int,
    severity: str,
) -> dict[str, dict[str, float]]:
    """Cumulative per-route cuts for component diagnostics, not ensemble decisions.

    For policies whose ``best`` is a ``learned_blend_*`` (no per-route
    thresholds — uses a logit blend with a single threshold), fall back
    to the first ``joint_or_at_fp_*`` candidate that has non-empty
    per-route thresholds. These saved OR surrogates support component-scope
    filtering but can disagree with the deployed blend. Ensemble decisions
    are evaluated separately using the serving policy implementation.
    """
    out: dict[str, dict[str, float]] = {}
    for route_key, entry in policy.get("routes", {}).items():
        if not route_key.startswith("filetypes/"):
            continue
        ft = route_key.split("/", 1)[1]
        cuts: dict[str, float] = {}
        for level_entry in _policy_levels(entry.get("levels") or []):
            if level_entry["level"] > level:
                continue
            sev = level_entry.get(severity) or {}
            best = sev.get("best", sev) or {}
            ts = best.get("thresholds") or {}
            if not ts:
                for cand in sev.get("candidates") or []:
                    if (str(cand.get("policy") or "").startswith("joint_or_at_fp")
                            and cand.get("thresholds")):
                        ts = cand["thresholds"]
                        break
            for route, threshold in ts.items():
                if threshold is not None and 0 <= np.float32(threshold) <= 1:
                    cuts[route] = min(cuts.get(route, float("inf")), float(np.float32(threshold)))
        if cuts:
            out[ft] = cuts
    return out


def _ensemble_margins(
    scores: dict[str, np.ndarray], levels: list[dict[str, Any]],
    level: int, size: int, severity: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return serving margins and the winning rule's display score/cut.

    A blend is reported as an aggregate, rather than attributing its verdict
    to an unrelated component OR surrogate. Classification uses the shared
    float32 policy margin; reconstructed blend probabilities are display only.
    """
    margins = frozen_policy.swept_margin(scores, levels, level, size, severity=severity)
    names = np.full(size, "", dtype=object)
    probabilities = np.full(size, np.nan, dtype=np.float32)
    thresholds = np.full(size, np.nan, dtype=np.float32)
    pending = np.isfinite(margins)
    for item in sorted(levels, key=lambda value: int(value["level"])):
        if int(item["level"]) > level:
            continue
        entry = item.get(severity) or {}
        decision = entry.get("best", entry) or {}
        blend = decision.get("blend")
        if blend:
            distance = frozen_policy.margin(scores, decision, size)
            chosen = pending & np.isfinite(distance) & (distance == margins)
            cut = np.float32(blend["threshold"])
            names[chosen] = "ensemble:blend"
            probabilities[chosen] = np.clip(distance[chosen] + cut, 0, 1)
            thresholds[chosen] = cut
            pending[chosen] = False
        else:
            for route, threshold in (decision.get("thresholds") or {}).items():
                if route not in scores or threshold is None or not 0 <= np.float32(threshold) <= 1:
                    continue
                p = np.asarray(scores[route], dtype=np.float32)
                cut = np.float32(threshold)
                chosen = pending & np.isfinite(p) & ((p - cut) == margins)
                names[chosen] = route
                probabilities[chosen] = p[chosen]
                thresholds[chosen] = cut
                pending[chosen] = False
    if pending.any():
        raise ValueError("Unable to identify a finite ensemble decision")
    return margins, names, probabilities, thresholds


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
    """Return per-route cuts for a component scope, not the ensemble."""
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
        "--config", type=Path,
        help="Bundle config for ensemble fallback; defaults to config.json beside the score table.",
    )
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
            f"Shared pool-adjusted severity level (default {DEFAULT_SEVERITY_LEVEL}). "
            "L0 allows zero observed calibration FPs; positive L allows "
            "1 + (L - 1) * N / 100,000,000 for N benign files, rounded down "
            "for integer counts. Evaluate saved decisions at or below this level."
        ),
    )
    p.add_argument(
        "--severity",
        choices=["hostile"],
        default="hostile",
    )
    p.add_argument("--top-errors", type=int, default=100)
    p.add_argument(
        "--filetypes", default="",
        help="Comma-separated scored filetypes to review; default: all filetypes.",
    )
    p.add_argument(
        "--no-cutoff",
        action="store_true",
        help="Don't gate on the per-filetype operating threshold. Rank EVERY "
             "routable row of the target label by margin and keep the top "
             "(per --per-filetype-top / --top-errors). --level then only sets "
             "the reference the margin is measured against, not membership. "
             "Use for mislabeled-data triage where you want each filetype's "
             "most label-discordant files regardless of any operating point.",
    )
    p.add_argument(
        "--per-filetype-top",
        type=int,
        default=0,
        help="If > 0, take the top N rows PER FILETYPE (ranked within each "
             "filetype by the same margin order) instead of the global "
             "--top-errors. Used by `make triage` to land an even quota per "
             "filetype. --skip is applied to the global ranking before "
             "per-filetype bucketing.",
    )
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
    if args.level < 0:
        p.error("--level must be nonnegative")

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
    no_cutoff = bool(args.no_cutoff)
    target_label = 0 if is_fp else 1

    table = np.load(args.score_table, allow_pickle=False)
    row_ids: np.ndarray = table["row_ids"]
    labels: np.ndarray = table["labels"]
    file_types: np.ndarray = table["file_types"]
    route_names: np.ndarray = table["route_names"]
    selected_filetypes = sorted({ft.strip() for ft in args.filetypes.split(",") if ft.strip()})
    if args.filetypes and not selected_filetypes:
        p.error("--filetypes must name at least one filetype")
    unknown = set(selected_filetypes) - set(map(str, np.unique(file_types)))
    if unknown:
        p.error(f"unknown filetypes in score table: {', '.join(sorted(unknown))}")
    scores: np.ndarray = table["scores"]  # (R, N)
    if selected_filetypes:
        keep = np.isin(file_types, selected_filetypes)
        row_ids, labels, file_types = row_ids[keep], labels[keep], file_types[keep]
        scores = scores[:, keep]

    policy = json.loads(args.route_policies.read_text())
    for route in policy.get("routes", {}).values():
        route["levels"] = _policy_levels(route.get("levels") or [])
    config_path = args.config or args.score_table.parent / "config.json"
    config: dict[str, Any] = {}
    if any(canon == "ensemble" for _, canon, _ in scope_specs):
        if not config_path.is_file():
            raise SystemExit(
                f"ensemble scope requires the bundle config: {config_path}; supply --config"
            )
        config = json.loads(config_path.read_text())
        config["levels"] = _policy_levels(config.get("levels") or [])
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
            ft_mask = target_mask & (file_types == ft)
            ft_row_indices = np.flatnonzero(ft_mask)
            if not ft_row_indices.size:
                continue
            thresholds = {} if canon_scope == "ensemble" else _row_thresholds_for_scope(
                canon_scope, ft_str, per_ft, global_min, explicit_route
            )
            if not thresholds and canon_scope != "ensemble":
                continue
            contributing: list[tuple[int, str, float]] = []
            for route_name, t in thresholds.items():
                ridx = r_idx.get(route_name)
                if ridx is None:
                    continue
                contributing.append((ridx, route_name, t))
            if not contributing and canon_scope != "ensemble":
                continue
            # margin per row: max(score - threshold) across contributing routes.
            # NaN scores (route didn't run / not applicable to this filetype)
            # are excluded — they contribute neither a hit nor a deficit.
            if canon_scope == "ensemble":
                local = {name: scores[index, ft_row_indices] for name, index in r_idx.items()}
                levels = frozen_policy.routing_levels(
                    local, config, policy, ft_str, severity=args.severity,
                )
                margins, headline_names, headline_scores, headline_cuts = _ensemble_margins(
                    local, levels, args.level, len(ft_row_indices), args.severity,
                )
                any_finite = np.isfinite(margins)
            else:
                margins = np.full(ft_row_indices.shape, -np.inf, dtype=np.float32)
                any_finite = np.zeros(ft_row_indices.shape, dtype=bool)
                for ridx, _, t in contributing:
                    row_scores = scores[ridx, ft_row_indices].astype(np.float32)
                    finite = np.isfinite(row_scores)
                    delta = np.where(finite, row_scores - np.float32(t), -np.inf)
                    margins = np.where(finite & (delta > margins), delta, margins)
                    any_finite |= finite
            # no_cutoff: rank EVERY routable row by margin, ignore the
            # threshold-sign gate. The level then only sets the reference
            # the margin is measured against — it no longer decides
            # membership. Used by `make triage` so each filetype yields its
            # top-N most-label-discordant files (most hostile-looking
            # benigns / most benign-looking malware) rather than only those
            # that happen to cross a fixed operating point.
            if no_cutoff:
                hit = any_finite
            elif is_fp:
                hit = margins >= 0
            else:
                hit = any_finite & (margins < 0)
            if not hit.any():
                continue
            for pos in np.flatnonzero(hit):
                row_i = int(ft_row_indices[pos])
                margin = float(margins[pos])
                row_trigs: list[tuple[str, float, float]] = []
                if canon_scope == "ensemble":
                    row_trigs.append((
                        str(headline_names[pos]), float(headline_scores[pos]),
                        float(headline_cuts[pos]),
                    ))
                elif is_fp and not no_cutoff:
                    for ridx, route_name, t in contributing:
                        s = float(np.float32(scores[ridx, row_i]))
                        if np.isfinite(s) and s >= t:
                            row_trigs.append((route_name, s, t))
                else:
                    # FN, or no_cutoff FP: record every contributing route so
                    # the headline reflects the max-score route even when no
                    # route crossed its threshold.
                    for ridx, route_name, t in contributing:
                        s = float(np.float32(scores[ridx, row_i]))
                        if np.isfinite(s):
                            row_trigs.append((route_name, s, t))
                entry = agg.get(row_i)
                if entry is None:
                    agg[row_i] = {
                        "margin": margin,
                        "scopes": {raw_scope},
                        "scope_margins": {raw_scope: margin},
                        "trigs": {(r, s, t) for r, s, t in row_trigs},
                    }
                else:
                    if is_fp:
                        entry["margin"] = max(entry["margin"], margin)
                    else:
                        entry["margin"] = min(entry["margin"], margin)
                    entry["scopes"].add(raw_scope)
                    entry["scope_margins"][raw_scope] = margin
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
    flat = flat[skip:]
    if args.per_filetype_top and args.per_filetype_top > 0:
        per_ft_counts: dict[str, int] = {}
        top = []
        for item in flat:
            ft = str(file_types[item[1]])
            if per_ft_counts.get(ft, 0) >= args.per_filetype_top:
                continue
            per_ft_counts[ft] = per_ft_counts.get(ft, 0) + 1
            top.append(item)
        print(
            f"flagged: {len(flat):,} (deduped across {len(scope_specs)} scope(s)), "
            f"skipping {skip}, taking top {args.per_filetype_top}/filetype "
            f"across {len(per_ft_counts)} filetype(s) = {len(top)} rows",
            file=sys.stderr,
        )
    else:
        top = flat[: args.top_errors]
        print(
            f"flagged: {len(flat) + skip:,} (deduped across {len(scope_specs)} "
            f"scope(s)), skipping {skip}, taking {len(top)}",
            file=sys.stderr,
        )

    selected_row_ids = [int(row_ids[t[1]]) for t in top]
    paths = _load_paths(args.db, selected_row_ids) if args.db else {}
    if args.db and len(paths) < len(selected_row_ids):
        missing = len(selected_row_ids) - len(paths)
        print(
            f"WARN: {missing}/{len(selected_row_ids)} row_ids no longer in the DB "
            "(deleted since the score table was built)",
            file=sys.stderr,
        )

    rows_out: list[dict[str, Any]] = []
    for margin, row_i, entry in top:
        rid = int(row_ids[row_i])
        sha, path, parent, current_label, hopper_skip = paths.get(rid, ("", "", "", "", ""))
        trigs = sorted(entry["trigs"])
        # For FPs the headline route is the one with the largest delta.
        # For FNs the same — most permissive (smallest threshold shortfall).
        headline = max(trigs, key=lambda x: x[1] - x[2]) if trigs else None
        rows_out.append({
            "row_id": rid,
            "sha256": sha,
            "path": path,
            "parent": parent,
            "label": "good" if is_fp else "bad",
            # The pool the row sits in NOW, which may differ from the "label"
            # above (that one is the pool the score table was built against).
            # "" means the row is gone from the DB. Triage skips any row whose
            # current pool has moved rather than downloading a stale verdict.
            "current_label": current_label,
            "hopper_skip": hopper_skip,
            "filetype": str(file_types[row_i]),
            "probability": headline[1] if headline else 0.0,
            "margin": margin,
            "scope": args.scope,
            "scopes_flagged": sorted(entry["scopes"]),
            "scope_margins": entry["scope_margins"],
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
        "config": str(config_path) if config else None,
        "decision_semantics": {
            "ensemble": "cumulative saved policies, including blends and serving fallback",
            "component_scopes": (
                "cumulative per-route OR diagnostics; saved OR surrogates for blends"
            ),
        },
        "kind": args.kind,
        "scope": args.scope,
        "scopes": [raw for raw, _, _ in scope_specs],
        "level": args.level,
        "severity": args.severity,
        "filetypes": selected_filetypes or None,
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
