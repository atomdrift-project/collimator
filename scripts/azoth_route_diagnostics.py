#!/usr/bin/env python3
"""Write azoth routed-ensemble marginal-value diagnostics."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from azoth_calibrate_ensemble import _budget, _candidate_thresholds, _hit_mask


def _fmt(value: Any, digits: int = 6) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        if math.isnan(value):
            return "-"
        return f"{value:.{digits}g}"
    return str(value)


def _route_arrays(score_table: np.lib.npyio.NpzFile) -> dict[str, dict[str, Any]]:
    names = [str(name) for name in score_table["route_names"]]
    kinds = [str(kind) for kind in score_table["route_kinds"]]
    scores = score_table["scores"]
    out: dict[str, dict[str, Any]] = {}
    for idx, name in enumerate(names):
        probs = scores[idx]
        present = ~np.isnan(probs)
        out[name] = {
            "kind": kinds[idx],
            "indices": np.flatnonzero(present).astype(np.int64),
            "probs": probs[present].astype(np.float32),
        }
    return out


def _best_after_general(
    *,
    labels: np.ndarray,
    routes: dict[str, dict[str, Any]],
    route_name: str,
    max_fp: int,
    base_hit: np.ndarray,
    base_tp: int,
    base_fp: int,
    candidate_cache: dict[tuple[str, int], list[dict[str, float | int | None]]],
) -> dict[str, Any]:
    n_rows = len(labels)
    benign = labels == 0
    malware = labels == 1
    if route_name == "general":
        general_best = max(
            candidate_cache[("general", max_fp)],
            key=lambda item: int(item["tp"] or 0),
        )
        return {
            "threshold": general_best["threshold"],
            "inc_tp": 0,
            "inc_fp": 0,
            "tp": base_tp,
            "fp": base_fp,
        }

    route = routes[route_name]
    best: dict[str, Any] | None = None
    for candidate in candidate_cache[(route_name, max_fp)]:
        threshold = candidate["threshold"]
        route_hit = _hit_mask(
            n_rows,
            route["indices"],
            route["probs"],
            None if threshold is None else float(threshold),
        )
        proposed = base_hit | route_hit
        fp = int(np.sum(proposed & benign))
        if fp > max_fp:
            continue
        tp = int(np.sum(proposed & malware))
        item = {
            "threshold": threshold,
            "inc_tp": tp - base_tp,
            "inc_fp": fp - base_fp,
            "tp": tp,
            "fp": fp,
        }
        if best is None or (item["inc_tp"], -max(item["inc_fp"], 0)) > (
            best["inc_tp"],
            -max(best["inc_fp"], 0),
        ):
            best = item
    return best or {"threshold": None, "inc_tp": 0, "inc_fp": 0, "tp": base_tp, "fp": base_fp}


def _general_base(
    *,
    labels: np.ndarray,
    routes: dict[str, dict[str, Any]],
    max_fp: int,
    candidate_cache: dict[tuple[str, int], list[dict[str, float | int | None]]],
) -> tuple[np.ndarray, int, int]:
    general = routes["general"]
    general_best = max(
        candidate_cache[("general", max_fp)],
        key=lambda item: int(item["tp"] or 0),
    )
    base_hit = _hit_mask(
        len(labels),
        general["indices"],
        general["probs"],
        None if general_best["threshold"] is None else float(general_best["threshold"]),
    )
    benign = labels == 0
    malware = labels == 1
    return base_hit, int(np.sum(base_hit & malware)), int(np.sum(base_hit & benign))


def _rows(config: dict[str, Any], score_table: np.lib.npyio.NpzFile) -> list[dict[str, Any]]:
    labels = score_table["labels"].astype(np.int8)
    routes = _route_arrays(score_table)
    n_benign = int(np.sum(labels == 0))
    candidate_cache: dict[tuple[str, int], list[dict[str, float | int | None]]] = {}
    out: list[dict[str, Any]] = []
    for level in config["levels"]:
        level_no = int(level["level"])
        for severity in ("hostile",):
            block = level[severity]
            max_fp = int(block.get("budget") or _budget(n_benign, float(block["target_per_million"])))
            for route_name, route in routes.items():
                candidate_cache.setdefault(
                    (route_name, max_fp),
                    _candidate_thresholds(
                        labels,
                        route["indices"],
                        route["probs"],
                        max_fp=max_fp,
                    ),
                )
            base_hit, base_tp, base_fp = _general_base(
                labels=labels,
                routes=routes,
                max_fp=max_fp,
                candidate_cache=candidate_cache,
            )
            thresholds = block.get("thresholds", {})
            diagnostics = block.get("diagnostics", {})
            for route_name, route in routes.items():
                diag = diagnostics.get(route_name, {})
                standalone = diag.get("standalone", {})
                final = diag.get("best_marginal", {})
                after_general = _best_after_general(
                    labels=labels,
                    routes=routes,
                    route_name=route_name,
                    max_fp=max_fp,
                    base_hit=base_hit,
                    base_tp=base_tp,
                    base_fp=base_fp,
                    candidate_cache=candidate_cache,
                )
                selected_threshold = thresholds.get(route_name)
                out.append(
                    {
                        "level": level_no,
                        "severity": severity,
                        "target_per_million": block["target_per_million"],
                        "budget": max_fp,
                        "route": route_name,
                        "kind": route["kind"],
                        "rows": len(route["indices"]),
                        "selected": route_name in thresholds,
                        "selected_threshold": selected_threshold,
                        "standalone_tp": standalone.get("tp", 0),
                        "standalone_fp": standalone.get("fp", 0),
                        "standalone_threshold": standalone.get("threshold"),
                        "after_general_inc_tp": after_general["inc_tp"],
                        "after_general_inc_fp": after_general["inc_fp"],
                        "after_general_tp": after_general["tp"],
                        "after_general_fp": after_general["fp"],
                        "after_general_threshold": after_general["threshold"],
                        "final_inc_tp": final.get("inc_tp", 0),
                        "final_inc_fp": final.get("inc_fp", 0),
                        "final_tp": final.get("tp", block.get("tp")),
                        "final_fp": final.get("fp", block.get("fp")),
                        "final_threshold": final.get("threshold"),
                    },
                )
    return out


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _route_hit(
    n_rows: int,
    route: dict[str, Any],
    threshold: float | None,
) -> np.ndarray:
    return _hit_mask(n_rows, route["indices"], route["probs"], threshold)


def _score_union(
    *,
    n_rows: int,
    routes: dict[str, dict[str, Any]],
    thresholds: dict[str, float],
    route_names: list[str],
) -> tuple[np.ndarray, list[str]]:
    hit = np.zeros(n_rows, dtype=bool)
    used: list[str] = []
    for route_name in route_names:
        threshold = thresholds.get(route_name)
        route = routes.get(route_name)
        if route is None or threshold is None:
            continue
        hit |= _route_hit(n_rows, route, float(threshold))
        used.append(route_name)
    return hit, used


def _metric_row(
    *,
    level: int,
    severity: str,
    scope: str,
    name: str,
    labels: np.ndarray,
    mask: np.ndarray,
    hit: np.ndarray,
    used_routes: list[str],
    target_per_million: float,
) -> dict[str, Any]:
    scoped_labels = labels[mask]
    scoped_hit = hit[mask]
    malware = scoped_labels == 1
    benign = scoped_labels == 0
    tp = int(np.sum(scoped_hit & malware))
    fp = int(np.sum(scoped_hit & benign))
    fn = int(np.sum((~scoped_hit) & malware))
    tn = int(np.sum((~scoped_hit) & benign))
    n_malware = int(np.sum(malware))
    n_benign = int(np.sum(benign))
    precision = tp / max(tp + fp, 1)
    recall = tp / n_malware if n_malware else math.nan
    fpr = fp / n_benign if n_benign else math.nan
    f1 = (2 * precision * recall / max(precision + recall, 1e-12)) if n_malware else math.nan
    accuracy = (tp + tn) / max(tp + fp + tn + fn, 1)
    return {
        "level": level,
        "severity": severity,
        "scope": scope,
        "name": name,
        "target_per_100M": target_per_million * 100.0,
        "rows": int(np.sum(mask)),
        "malware": n_malware,
        "benign": n_benign,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "accuracy": accuracy,
        "fpr": fpr,
        "fp_per_100M": fp * 100_000_000.0 / n_benign if n_benign else math.nan,
        "used_routes": ",".join(used_routes),
    }


def _slice_rows(config: dict[str, Any], score_table: np.lib.npyio.NpzFile) -> list[dict[str, Any]]:
    labels = score_table["labels"].astype(np.int8)
    file_types = np.asarray([str(value) for value in score_table["file_types"]])
    file_groups = np.asarray([str(value) for value in score_table["file_groups"]])
    routes = _route_arrays(score_table)
    n_rows = len(labels)
    out: list[dict[str, Any]] = []
    filetype_to_group = {str(k): str(v) for k, v in config.get("filetype_to_group", {}).items()}
    scopes: list[tuple[str, str, np.ndarray]] = [("all", "all", np.ones(n_rows, dtype=bool))]
    scopes.extend(
        ("filegroup", group, file_groups == group)
        for group in sorted(value for value in set(file_groups) if value)
    )
    scopes.extend(
        ("filetype", file_type, file_types == file_type)
        for file_type in sorted(set(file_types))
    )

    for level in config["levels"]:
        level_no = int(level["level"])
        for severity in ("hostile",):
            block = level[severity]
            thresholds = {str(k): float(v) for k, v in block.get("thresholds", {}).items()}
            for scope, name, mask in scopes:
                if scope == "filetype":
                    group = filetype_to_group.get(name, "")
                    route_names = ["general"]
                    if group:
                        route_names.append(f"filegroups/{group}")
                    route_names.append(f"filetypes/{name}")
                elif scope == "filegroup":
                    route_names = ["general", f"filegroups/{name}"]
                    route_names.extend(
                        f"filetypes/{file_type}"
                        for file_type, group in sorted(filetype_to_group.items())
                        if group == name
                    )
                else:
                    route_names = list(thresholds)
                hit, used = _score_union(
                    n_rows=n_rows,
                    routes=routes,
                    thresholds=thresholds,
                    route_names=route_names,
                )
                out.append(
                    _metric_row(
                        level=level_no,
                        severity=severity,
                        scope=scope,
                        name=name,
                        labels=labels,
                        mask=mask,
                        hit=hit,
                        used_routes=used,
                        target_per_million=float(block["target_per_million"]),
                    ),
                )
    return out


def _write_slice_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _pct(value: Any) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    return f"{float(value) * 100:.2f}%"


def _write_slice_markdown(path: Path, config: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Azoth Slice Metrics",
        "",
        "Effective routed ensemble metrics by corpus slice. A filetype row uses the route litmus would use for that filetype: `az`, calibrated `az/<filegroup>`, and calibrated `az/<filetype>` when available.",
        "",
        f"- Calibration snapshot: `{config.get('calibration_snapshot_id')}`",
        f"- Rows: {config.get('rows')} ({config.get('malware')} malware, {config.get('benign')} benign)",
    ]
    interesting = [("all", "all"), ("filetype", "elf"), ("filetype", "pe"), ("filetype", "python"), ("filetype", "javascript")]
    # Headline levels in the new per-100M grid: L50 (default), L100 (loose end).
    # L300/L500/L1000 from the old grid are no longer computed.
    for level_no, severity in [(50, "hostile"), (100, "hostile")]:
        selected: list[dict[str, Any]] = []
        for scope, name in interesting:
            selected.extend(
                row
                for row in rows
                if row["level"] == level_no
                and row["severity"] == severity
                and row["scope"] == scope
                and row["name"] == name
            )
        top_filetypes = [
            row
            for row in rows
            if row["level"] == level_no
            and row["severity"] == severity
            and row["scope"] == "filetype"
            and row["malware"] >= 50
        ]
        if not selected and not top_filetypes:
            continue
        lines.extend(
            [
                "",
                f"## L{level_no} {severity.title()}",
                "",
                "| Scope | Rows | Malware | Benign | Recall | FPR | FP/100M | Precision | F1 | Accuracy | Routes |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
            ],
        )
        top_filetypes.sort(key=lambda row: (-float(row["recall"]), -int(row["malware"]), row["name"]))
        for row in selected + [row for row in top_filetypes[:10] if row not in selected]:
            label = row["name"] if row["scope"] == "all" else f"{row['scope']}/{row['name']}"
            lines.append(
                "| "
                f"{label} | "
                f"{row['rows']} | "
                f"{row['malware']} | "
                f"{row['benign']} | "
                f"{_pct(row['recall'])} | "
                f"{_pct(row['fpr'])} | "
                f"{_fmt(row['fp_per_100M'], 5)} | "
                f"{_pct(row['precision'])} | "
                f"{_pct(row['f1'])} | "
                f"{_pct(row['accuracy'])} | "
                f"{row['used_routes'] or '-'} |",
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def _write_markdown(path: Path, config: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Azoth Route Diagnostics",
        "",
        "Marginal-value report for the routed ensemble. `after general` measures the best single-route addition to the general model under the level budget. `final marginal` measures whether a route can still add anything after the final selected ensemble.",
        "",
        f"- Calibration snapshot: `{config.get('calibration_snapshot_id')}`",
        f"- Rows: {config.get('rows')} ({config.get('malware')} malware, {config.get('benign')} benign)",
        f"- Search: `{config.get('search', {}).get('method')}`",
        "",
        "## Selected Routes",
        "",
        "| L | Severity | Selected routes |",
        "| ---: | --- | --- |",
    ]
    for level in config["levels"]:
        for severity in ("hostile",):
            thresholds = level[severity].get("thresholds", {})
            selected = ", ".join(thresholds) if thresholds else "-"
            lines.append(f"| {level['level']} | {severity} | {selected} |")

    # Headline levels in the new per-100M grid.
    interesting = [
        (50, "hostile"),
        (100, "hostile"),
    ]
    for level_no, severity in interesting:
        subset = [
            row
            for row in rows
            if row["level"] == level_no and row["severity"] == severity and row["route"] != "general"
        ]
        if not subset:
            continue
        subset.sort(
            key=lambda row: (
                not row["selected"],
                -int(row["after_general_inc_tp"]),
                -int(row["standalone_tp"]),
                row["route"],
            ),
        )
        lines.extend(
            [
                "",
                f"## L{level_no} {severity.title()}",
                "",
                "| Route | Sel | Rows | Alone TP/FP | After general +TP/+FP | Final +TP/+FP | Threshold |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ],
        )
        for row in subset[:25]:
            lines.append(
                "| "
                f"{row['route']} | "
                f"{'Y' if row['selected'] else '-'} | "
                f"{row['rows']} | "
                f"{row['standalone_tp']}/{row['standalone_fp']} | "
                f"{row['after_general_inc_tp']}/{row['after_general_inc_fp']} | "
                f"{row['final_inc_tp']}/{row['final_inc_fp']} | "
                f"{_fmt(row['selected_threshold'] or row['final_threshold'] or row['after_general_threshold'])} |",
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("out/models/azoth/config.json"))
    parser.add_argument("--score-table", type=Path, default=Path("out/models/azoth/score_table.npz"))
    parser.add_argument("--output", type=Path, default=Path("out/models/azoth/route_diagnostics.md"))
    parser.add_argument("--csv", type=Path, default=Path("out/models/azoth/route_diagnostics.csv"))
    parser.add_argument(
        "--slice-output",
        type=Path,
        default=Path("out/models/azoth/slice_metrics.md"),
    )
    parser.add_argument(
        "--slice-csv",
        type=Path,
        default=Path("out/models/azoth/slice_metrics.csv"),
    )
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)
    score_table = np.load(args.score_table)
    rows = _rows(config, score_table)
    if not rows:
        raise SystemExit("no route diagnostics rows generated")
    _write_csv(args.csv, rows)
    _write_markdown(args.output, config, rows)
    slice_rows = _slice_rows(config, score_table)
    _write_slice_csv(args.slice_csv, slice_rows)
    _write_slice_markdown(args.slice_output, config, slice_rows)
    print(f"wrote {args.output}")
    print(f"wrote {args.csv}")
    print(f"wrote {args.slice_output}")
    print(f"wrote {args.slice_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
