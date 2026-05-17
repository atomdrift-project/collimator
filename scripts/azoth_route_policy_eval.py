#!/usr/bin/env python3
"""Evaluate routed-ensemble policies against single-route baselines.

The user-visible complaint this script measures: at fixed false-positive
budgets (recall@0FP, recall@3FP) and on PR-AUC, our deployed ensemble OR-rule
underperforms the specialist alone. We want a clean side-by-side number on
the locked test partition before changing any calibration.

Per filetype slice, on test-partition rows only, we compute:

* Single-route Pareto: recall@0FP, recall@3FP, PR-AUC for each of
  ``general``, ``filegroups/<group>``, ``filetypes/<type>`` independently.
* Free ensemble baseline (``max_rule``): operate on
  ``max(p_general, p_group, p_specialist)`` as a continuous score. No
  training needed; demonstrates that any sensible continuous combinator
  beats hard-thresholded OR.
* Deployed OR-rule: apply the per-route thresholds from
  ``route_policies.json`` and report the single operating point (FP count
  actually observed, recall achieved). For each level/severity we report
  the delta vs the best single-route Pareto at the OR's observed FP count.

Output is markdown + JSON. The markdown sorts filetypes by malware count,
so the cases worth fixing first surface at the top.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import data  # noqa: E402


def _route_probs_dense(scores: np.ndarray, route_idx: int) -> np.ndarray:
    """Return route's dense prob row (NaN where the route doesn't apply)."""
    return scores[route_idx].astype(np.float32, copy=False)


def _recall_pr_at_fp(
    probs: np.ndarray,
    labels: np.ndarray,
    fp_budget: int,
) -> tuple[float, float | None, int]:
    """Recall at the tightest threshold with FP <= fp_budget.

    Returns (recall, threshold_or_None, fp_count). Threshold is None when
    no row passes (e.g., budget=0 and the top benign outranks every
    malware). Ties in probability are handled by the standard
    sort-by-(-prob, label_desc) convention so a tie containing benigns is
    resolved against the malware (worst case for recall).
    """
    valid = ~np.isnan(probs)
    if not np.any(valid):
        return (math.nan, None, 0)
    p = probs[valid]
    y = labels[valid].astype(np.int8)
    n_mal = int(np.sum(y == 1))
    if n_mal == 0:
        return (math.nan, None, 0)
    # Sort descending; on ties put benigns BEFORE malware so cumulative FP
    # leads its row's TP — this matches what an attacker can force.
    order = np.lexsort((y, -p))
    p_sorted = p[order]
    y_sorted = y[order]
    fp_cum = np.cumsum(y_sorted == 0)
    tp_cum = np.cumsum(y_sorted == 1)
    eligible = np.flatnonzero(fp_cum <= fp_budget)
    if len(eligible) == 0:
        return (0.0, None, 0)
    end = int(eligible[-1])
    threshold = float(p_sorted[end])
    fp = int(fp_cum[end])
    recall = float(tp_cum[end]) / n_mal
    return (recall, threshold, fp)


def _pr_auc(probs: np.ndarray, labels: np.ndarray) -> float:
    """PR-AUC (average precision). Numpy-only to avoid sklearn dep here."""
    valid = ~np.isnan(probs)
    if not np.any(valid):
        return math.nan
    p = probs[valid]
    y = labels[valid].astype(np.int8)
    n_mal = int(np.sum(y == 1))
    if n_mal == 0 or n_mal == len(y):
        return math.nan
    order = np.argsort(-p, kind="mergesort")
    y_sorted = y[order]
    tp_cum = np.cumsum(y_sorted == 1).astype(np.float64)
    fp_cum = np.cumsum(y_sorted == 0).astype(np.float64)
    precision = tp_cum / np.maximum(tp_cum + fp_cum, 1.0)
    recall = tp_cum / n_mal
    # AP = sum_k (R_k - R_{k-1}) * P_k, with R_{-1}=0.
    delta_recall = np.diff(recall, prepend=0.0)
    return float(np.sum(delta_recall * precision))


def _deployed_or_metrics(
    probs_by_route: dict[str, np.ndarray],
    labels: np.ndarray,
    thresholds: dict[str, float],
) -> dict[str, Any]:
    """OR-rule across routes at the deployed per-route thresholds.

    A sentinel threshold of 1.0 (or larger) is unreachable for calibrated
    probabilities and is treated as no-op — consistent with the
    policy_search writer that uses 1.0 to keep a route "present but
    inactive" in route_policies.json.
    """
    n_rows = len(labels)
    hit = np.zeros(n_rows, dtype=bool)
    active_routes: list[str] = []
    for route_name, threshold in thresholds.items():
        if threshold is None or threshold >= 1.0:
            continue
        probs = probs_by_route.get(route_name)
        if probs is None:
            continue
        valid = ~np.isnan(probs)
        hit |= valid & (probs >= float(threshold))
        active_routes.append(route_name)
    malware = labels == 1
    benign = labels == 0
    tp = int(np.sum(hit & malware))
    fp = int(np.sum(hit & benign))
    n_mal = int(np.sum(malware))
    return {
        "tp": tp,
        "fp": fp,
        "recall": (tp / n_mal) if n_mal else math.nan,
        "active_routes": active_routes,
    }


def _slice_metrics(
    probs_by_route: dict[str, np.ndarray],
    labels: np.ndarray,
    *,
    fp_budgets: tuple[int, ...],
) -> dict[str, Any]:
    """Per-route + max-rule baselines on the slice."""
    out: dict[str, Any] = {"routes": {}, "max_rule": {}}
    for route_name, probs in probs_by_route.items():
        route_out: dict[str, Any] = {
            "pr_auc": _pr_auc(probs, labels),
        }
        for budget in fp_budgets:
            recall, threshold, fp = _recall_pr_at_fp(probs, labels, budget)
            route_out[f"recall_at_{budget}fp"] = recall
            route_out[f"threshold_at_{budget}fp"] = threshold
            route_out[f"fp_at_{budget}fp"] = fp
        out["routes"][route_name] = route_out

    # Max-rule combines routes by taking the element-wise max of their
    # probabilities — a free continuous "ensemble" with no training. Rows
    # where a route is NaN fall back to the surviving route(s); if all
    # routes are NaN for a row it stays NaN and the metric ignores it.
    stack = np.stack(list(probs_by_route.values()), axis=0)
    with np.errstate(invalid="ignore"):
        max_probs = np.nanmax(stack, axis=0)
    all_nan = np.all(np.isnan(stack), axis=0)
    max_probs[all_nan] = np.nan
    out["max_rule"]["pr_auc"] = _pr_auc(max_probs, labels)
    for budget in fp_budgets:
        recall, threshold, fp = _recall_pr_at_fp(max_probs, labels, budget)
        out["max_rule"][f"recall_at_{budget}fp"] = recall
        out["max_rule"][f"threshold_at_{budget}fp"] = threshold
        out["max_rule"][f"fp_at_{budget}fp"] = fp
    return out


def _best_route_recall_at_fp(
    slice_metrics: dict[str, Any],
    fp_budget: int,
) -> tuple[str, float]:
    """Among single routes, the route with the highest recall@fp_budget."""
    best_route = ""
    best_recall = -1.0
    for route_name, route_metrics in slice_metrics["routes"].items():
        recall = route_metrics.get(f"recall_at_{fp_budget}fp")
        if recall is None or (isinstance(recall, float) and math.isnan(recall)):
            continue
        if recall > best_recall:
            best_recall = recall
            best_route = route_name
    return best_route, best_recall if best_recall >= 0 else math.nan


def _present_route_probs(
    score_table: np.lib.npyio.NpzFile,
    scores: np.ndarray,
    route_name_to_idx: dict[str, int],
    file_type: str,
    file_group: str,
    slice_mask: np.ndarray,
) -> dict[str, np.ndarray]:
    """Pick the (general, group, specialist) probs that have any data in the slice."""
    out: dict[str, np.ndarray] = {}
    candidates = [("general", "general")]
    if file_group:
        candidates.append((f"filegroups/{file_group}", "group"))
    candidates.append((f"filetypes/{file_type}", "specialist"))
    for route_name, _kind in candidates:
        idx = route_name_to_idx.get(route_name)
        if idx is None:
            continue
        probs = scores[idx, slice_mask].astype(np.float32, copy=False)
        if np.all(np.isnan(probs)):
            continue
        out[route_name] = probs
    return out


def _fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "—"
    try:
        f = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(f):
        return "—"
    return f"{f:.{digits}f}"


def _pct(value: Any) -> str:
    if value is None:
        return "—"
    try:
        f = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(f):
        return "—"
    return f"{100 * f:.2f}%"


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    fp_budgets = payload["fp_budgets"]
    lines: list[str] = [
        "# Azoth Route Policy Eval",
        "",
        f"- Partition: `{payload['partition']}`",
        f"- Score table: `{payload['score_table']}`",
        f"- Route policies: `{payload['route_policies']}`",
        f"- Rows in partition: {payload['rows']} "
        f"({payload['malware']} malware, {payload['benign']} benign)",
        "",
        "## Per-filetype: single-route Pareto vs deployed OR-rule",
        "",
        "Columns: best single route's recall at FP budget, vs deployed "
        "OR-rule's recall at its **own** observed FP count. A negative "
        "delta means the ensemble loses to the best single route AT THE "
        "OR's actual operating point — the headline regression.",
        "",
        "| Filetype | Mal | Ben | Routes | Best route@0FP | OR FP | OR recall | Δ vs best@OR-FP | Best route@3FP | Spec PR-AUC | Max-rule PR-AUC |",
        "| --- | ---: | ---: | --- | --- | ---: | ---: | ---: | --- | ---: | ---: |",
    ]
    rows = []
    for file_type, ft_payload in payload["filetypes"].items():
        n_mal = ft_payload["malware"]
        n_ben = ft_payload["benign"]
        slice_metrics = ft_payload["slice_metrics"]
        # Pick a representative L/severity for the headline row: highest-malware
        # L9 hostile if present, else first available.
        op_summary = ft_payload.get("deployed_or_summary") or {}
        or_fp = op_summary.get("fp")
        or_recall = op_summary.get("recall")
        best_route_0, best_recall_0 = _best_route_recall_at_fp(slice_metrics, 0)
        best_route_3, best_recall_3 = _best_route_recall_at_fp(slice_metrics, 3)
        # Delta vs best-single-route recall at the OR-rule's own FP count.
        # If OR observed FP=k, find best single-route recall@k and compare.
        if or_fp is not None and not math.isnan(float(or_fp)):
            _, best_at_or = _best_route_recall_at_fp(slice_metrics, int(or_fp))
            delta = (or_recall - best_at_or) if (
                or_recall is not None and not math.isnan(or_recall) and not math.isnan(best_at_or)
            ) else math.nan
        else:
            delta = math.nan
        spec_route = f"filetypes/{file_type}"
        spec_metrics = slice_metrics["routes"].get(spec_route, {})
        max_metrics = slice_metrics.get("max_rule", {})
        rows.append((
            n_mal,
            file_type,
            n_ben,
            ",".join(slice_metrics["routes"].keys()),
            f"{best_route_0}: {_pct(best_recall_0)}" if best_route_0 else "—",
            or_fp if or_fp is not None else "—",
            _pct(or_recall),
            _pct(delta),
            f"{best_route_3}: {_pct(best_recall_3)}" if best_route_3 else "—",
            _fmt(spec_metrics.get("pr_auc"), 3),
            _fmt(max_metrics.get("pr_auc"), 3),
        ))
    rows.sort(key=lambda r: (-int(r[0]), r[1]))
    for r in rows:
        lines.append(
            "| " + " | ".join([
                str(r[1]),
                str(r[0]),
                str(r[2]),
                f"`{r[3]}`",
                r[4],
                str(r[5]),
                r[6],
                r[7],
                r[8],
                r[9],
                r[10],
            ]) + " |",
        )

    # Per-level appendix only if anything was deployed.
    levels = sorted({
        (lvl, sev)
        for ft in payload["filetypes"].values()
        for lvl, sev in (ft.get("deployed_or_by_level") or {})
    }, key=lambda pair: (pair[0], pair[1]))
    for lvl, sev in levels:
        lines.extend([
            "",
            f"## Deployed OR-rule at L{lvl} {sev}",
            "",
            "Per filetype, the OR-rule operating point and the gap to the "
            "best single route's recall at the SAME FP count.",
            "",
            "| Filetype | OR routes | OR FP | OR recall | Best single@OR-FP | Δ |",
            "| --- | --- | ---: | ---: | --- | ---: |",
        ])
        op_rows = []
        for file_type, ft_payload in payload["filetypes"].items():
            entry = (ft_payload.get("deployed_or_by_level") or {}).get((lvl, sev))
            if entry is None:
                continue
            slice_metrics = ft_payload["slice_metrics"]
            fp = int(entry["fp"])
            recall = entry["recall"]
            _, best_at_fp = _best_route_recall_at_fp(slice_metrics, fp)
            delta = (recall - best_at_fp) if (
                not math.isnan(recall) and not math.isnan(best_at_fp)
            ) else math.nan
            op_rows.append((
                ft_payload["malware"],
                file_type,
                ",".join(entry["active_routes"]),
                fp,
                recall,
                best_at_fp,
                delta,
            ))
        op_rows.sort(key=lambda r: (r[6] if not math.isnan(r[6]) else 0.0,))
        for r in op_rows:
            lines.append(
                f"| {r[1]} | `{r[2]}` | {r[3]} | {_pct(r[4])} | {_pct(r[5])} | {_pct(r[6])} |",
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--score-table", type=Path, default=Path("out/models/azoth/score_table.npz"))
    parser.add_argument(
        "--general-scores",
        type=Path,
        required=True,
        help="general/threshold_scores.npz, used for canonical_shas → partition filter",
    )
    parser.add_argument(
        "--route-policies",
        type=Path,
        default=Path("out/models/azoth/route_policies.json"),
    )
    parser.add_argument(
        "--partition",
        choices=("test", "dev", "train", "all"),
        default="test",
        help="Eval partition. test = locked headline slice (default).",
    )
    parser.add_argument(
        "--fp-budget",
        type=int,
        action="append",
        default=None,
        help="Repeatable. Default: 0 and 3.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("out/models/azoth/route_policy_eval.json"),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("out/models/azoth/route_policy_eval.md"),
    )
    args = parser.parse_args()
    fp_budgets = tuple(sorted(set(args.fp_budget or [0, 3])))

    score_table = np.load(args.score_table, allow_pickle=False)
    general_cache = np.load(args.general_scores, allow_pickle=False)
    if "canonical_shas" not in general_cache.files:
        raise SystemExit(
            f"{args.general_scores} lacks canonical_shas; rerun thresholds-refresh",
        )
    canonical_shas = general_cache["canonical_shas"]
    general_row_ids = general_cache["row_ids"].astype(np.int64)
    row_ids = score_table["row_ids"].astype(np.int64)
    if not np.array_equal(row_ids, general_row_ids):
        # Score table is the source of truth for ordering; build a permuted view.
        sha_by_row = dict(zip(general_row_ids.tolist(), canonical_shas.tolist(), strict=True))
        canonical_shas = np.asarray(
            [sha_by_row.get(int(r), "") for r in row_ids],
        )

    if args.partition == "all":
        partition_mask = np.ones(len(row_ids), dtype=bool)
    else:
        partition_mask = np.asarray(
            [data.partition_of(str(c)) == args.partition for c in canonical_shas],
            dtype=bool,
        )
    if not np.any(partition_mask):
        raise SystemExit(f"no rows in partition {args.partition!r}")

    labels_all = score_table["labels"].astype(np.int8)
    file_types_all = np.asarray([str(v) for v in score_table["file_types"]])
    file_groups_all = np.asarray([str(v) for v in score_table["file_groups"]])
    route_names = [str(v) for v in score_table["route_names"]]
    route_name_to_idx = {name: idx for idx, name in enumerate(route_names)}
    scores = score_table["scores"]

    with open(args.route_policies) as f:
        route_policies = json.load(f)
    policies_by_filetype: dict[str, dict[str, Any]] = {}
    for route_name, route_payload in route_policies.get("routes", {}).items():
        if route_payload.get("filetype"):
            policies_by_filetype[route_payload["filetype"]] = route_payload

    n_rows = int(np.sum(partition_mask))
    n_mal = int(np.sum(labels_all[partition_mask] == 1))
    n_ben = int(np.sum(labels_all[partition_mask] == 0))

    per_filetype: dict[str, Any] = {}
    for file_type in sorted(set(file_types_all)):
        slice_mask_full = (file_types_all == file_type) & partition_mask
        slice_mask = np.flatnonzero(slice_mask_full)
        if len(slice_mask) == 0:
            continue
        labels_slice = labels_all[slice_mask]
        n_mal_slice = int(np.sum(labels_slice == 1))
        n_ben_slice = int(np.sum(labels_slice == 0))
        if n_mal_slice == 0:
            # Skip slices with no malware in this partition; recall is undefined.
            continue
        file_group = ""
        # Same row's file_group is constant across the slice; pick the first.
        groups_in_slice = set(file_groups_all[slice_mask].tolist()) - {""}
        if groups_in_slice:
            file_group = next(iter(groups_in_slice))

        probs_by_route = _present_route_probs(
            score_table,
            scores,
            route_name_to_idx,
            file_type,
            file_group,
            slice_mask,
        )
        if not probs_by_route:
            continue
        slice_metrics = _slice_metrics(probs_by_route, labels_slice, fp_budgets=fp_budgets)

        # Deployed OR-rule operating points, by (level, severity).
        deployed_or_by_level: dict[tuple[int, str], dict[str, Any]] = {}
        deployed_or_summary: dict[str, Any] | None = None
        policy_payload = policies_by_filetype.get(file_type)
        if policy_payload:
            for level in policy_payload.get("levels", []):
                level_no = int(level["level"])
                for severity in ("hostile", "suspicious"):
                    best = level.get(severity, {}).get("best") or {}
                    thresholds = best.get("thresholds") or {}
                    if not thresholds:
                        continue
                    or_metrics = _deployed_or_metrics(
                        probs_by_route, labels_slice, thresholds,
                    )
                    deployed_or_by_level[(level_no, severity)] = or_metrics
                    # Headline summary: prefer L9 hostile (the deployment
                    # default for high-stakes blocks); fallback to L5 hostile.
                    if (level_no, severity) == (9, "hostile") or (
                        deployed_or_summary is None and (level_no, severity) == (5, "hostile")
                    ):
                        deployed_or_summary = or_metrics

        per_filetype[file_type] = {
            "malware": n_mal_slice,
            "benign": n_ben_slice,
            "file_group": file_group,
            "slice_metrics": slice_metrics,
            "deployed_or_by_level": deployed_or_by_level,
            "deployed_or_summary": deployed_or_summary,
        }

    payload = {
        "schema": "azoth.route_policy_eval.v1",
        "partition": args.partition,
        "score_table": str(args.score_table),
        "route_policies": str(args.route_policies),
        "rows": n_rows,
        "malware": n_mal,
        "benign": n_ben,
        "fp_budgets": list(fp_budgets),
        "filetypes": per_filetype,
    }

    # JSON keys must be strings — flatten (level, severity) tuples.
    def _flatten(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                (f"L{k[0]}_{k[1]}" if isinstance(k, tuple) else str(k)): _flatten(v)
                for k, v in obj.items()
            }
        if isinstance(obj, (list, tuple)):
            return [_flatten(v) for v in obj]
        if isinstance(obj, float) and not math.isfinite(obj):
            return None
        if isinstance(obj, np.floating):
            f = float(obj)
            return None if not math.isfinite(f) else f
        if isinstance(obj, np.integer):
            return int(obj)
        return obj

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(_flatten(payload), indent=2) + "\n")
    _write_markdown(args.output_md, payload)
    print(f"wrote {args.output_json}")
    print(f"wrote {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
