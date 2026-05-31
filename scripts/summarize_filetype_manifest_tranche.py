#!/usr/bin/env python3
"""Summarize the all-filetype manifest tranche against historical runs."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PlannedRun:
    index: int
    route: str
    filetype: str
    idea: str
    template: str
    note: str


def load_manifest(path: Path) -> tuple[list[PlannedRun], set[str]]:
    spec = importlib.util.spec_from_file_location("azoth_manifest", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)

    planned: list[PlannedRun] = []
    failed: set[str] = set()
    idx = 0
    for ft, template in mod.iter_runs():
        idx += 1
        idea = f"{mod.slugify(ft)}_{template.key}"
        route = f"filetypes/{ft}"
        planned.append(
            PlannedRun(
                index=idx,
                route=route,
                filetype=ft,
                idea=idea,
                template=template.key,
                note=template.note,
            )
        )
    return planned, failed


def parse_failures(log_path: Path) -> set[str]:
    failed: set[str] = set()
    if not log_path.exists():
        return failed
    for line in log_path.read_text(errors="replace").splitlines():
        if line.startswith("failed: "):
            failed.add(line.removeprefix("failed: ").strip())
    return failed


def metric(run: dict[str, Any] | None, name: str) -> float | None:
    if not run:
        return None
    for key in ("sampled_test_metrics", "holdout_metrics", "cross_val_metrics"):
        value = (run.get(key) or {}).get(name)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def load_runs(runs_dir: Path) -> dict[str, dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}
    for path in runs_dir.glob("*.json"):
        try:
            run = json.loads(path.read_text())
        except Exception:
            continue
        key = str(run.get("experiment_key") or "")
        if not key:
            continue
        current = by_key.get(key)
        # Prefer the keyed/timestamped copy with the most complete data.
        if current is None or len(run) > len(current):
            run["_path"] = str(path)
            by_key[key] = run
    return by_key


def load_deployed_l50(specialists_path: Path) -> dict[str, dict[str, Any]]:
    if not specialists_path.exists():
        return {}
    doc = json.loads(specialists_path.read_text())
    out: dict[str, dict[str, Any]] = {}
    for item in doc.get("results", []):
        kind = item.get("kind")
        name = item.get("name")
        if kind == "filetype":
            route = f"filetypes/{name}"
        elif kind == "filegroup":
            route = f"filegroups/{name}"
        elif kind == "general":
            route = "general"
        else:
            continue
        hostile_l50 = None
        for level in item.get("levels", []):
            if level.get("level") == 50:  # L50 (per-100M) = 0.5 FP/M = today's default
                hostile_l50 = level.get("hostile") or {}
                break
        out[route] = {
            "benchmark_rows": item.get("benchmark_rows"),
            "benchmark_malware": item.get("benchmark_malware"),
            "benchmark_benign": item.get("benchmark_benign"),
            "l50_recall": hostile_l50.get("recall") if hostile_l50 else None,
            "l50_fp_per_100M": hostile_l50.get("fp_per_100M") if hostile_l50 else None,
            "n_features": item.get("n_features"),
        }
    return out


def fmt(value: float | None, digits: int = 4) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="scripts/azoth_filetype_manifest_tranche.py")
    ap.add_argument("--log", default="out/experiments/azoth/logs/filetype-manifest-tranche-2026-05-07T03-27-36.log")
    ap.add_argument("--runs-dir", default="out/experiments/azoth/runs")
    ap.add_argument("--specialists", default="out/models/azoth/specialists.json")
    ap.add_argument("--markdown", default="experiments/AZOTH-FILETYPE-MANIFEST-TRANCHE.md")
    ap.add_argument("--csv", default="out/experiments/azoth/filetype_manifest_tranche_summary.csv")
    ap.add_argument("--json", default="out/experiments/azoth/filetype_manifest_tranche_summary.json")
    ap.add_argument("--win-margin", type=float, default=0.001)
    args = ap.parse_args()

    planned, _ = load_manifest(Path(args.manifest))
    failed = parse_failures(Path(args.log))
    planned_pairs = {(p.route, p.idea) for p in planned}
    runs = load_runs(Path(args.runs_dir))
    deployed = load_deployed_l50(Path(args.specialists))

    runs_by_pair: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    runs_by_route: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for run in runs.values():
        route = run.get("route")
        idea = run.get("idea")
        if not route or not idea:
            continue
        runs_by_pair[(route, idea)].append(run)
        runs_by_route[route].append(run)

    by_route: dict[str, list[PlannedRun]] = defaultdict(list)
    for p in planned:
        by_route[p.route].append(p)

    rows: list[dict[str, Any]] = []
    winners: list[dict[str, Any]] = []
    missing = 0
    failed_count = 0
    completed_count = 0

    for route in sorted(by_route):
        route_plans = by_route[route]
        route_planned_ideas = {p.idea for p in route_plans}
        hist = [
            r
            for r in runs_by_route.get(route, [])
            if (r.get("route"), r.get("idea")) not in planned_pairs
        ]
        hist_best = max(hist, key=lambda r: metric(r, "f1") or -1.0, default=None)
        hist_f1 = metric(hist_best, "f1")

        completed: list[tuple[PlannedRun, dict[str, Any]]] = []
        for p in route_plans:
            fail_key = f"{p.route}:{p.idea}"
            matches = runs_by_pair.get((p.route, p.idea), [])
            best_match = max(matches, key=lambda r: metric(r, "f1") or -1.0, default=None)
            status = "completed"
            if fail_key in failed:
                status = "failed"
                failed_count += 1
            elif best_match is None:
                status = "missing"
                missing += 1
            else:
                completed_count += 1
                completed.append((p, best_match))

            row = {
                "route": p.route,
                "filetype": p.filetype,
                "idea": p.idea,
                "template": p.template,
                "status": status,
                "key": best_match.get("experiment_key") if best_match else "",
                "f1": metric(best_match, "f1"),
                "precision": metric(best_match, "precision"),
                "recall": metric(best_match, "recall"),
                "roc_auc": metric(best_match, "roc_auc"),
                "avg_precision": metric(best_match, "avg_precision"),
                "brier": metric(best_match, "brier"),
                "elapsed_seconds": best_match.get("elapsed_seconds") if best_match else None,
                "historical_best_key": hist_best.get("experiment_key") if hist_best else "",
                "historical_best_idea": hist_best.get("idea") if hist_best else "",
                "historical_best_f1": hist_f1,
                "delta_vs_historical_f1": (metric(best_match, "f1") - hist_f1) if best_match and hist_f1 is not None and metric(best_match, "f1") is not None else None,
                "note": p.note,
            }
            rows.append(row)

        best_pair = max(completed, key=lambda pr: metric(pr[1], "f1") or -1.0, default=None)
        if best_pair:
            p, run = best_pair
            best_f1 = metric(run, "f1")
            delta = (best_f1 - hist_f1) if best_f1 is not None and hist_f1 is not None else None
            if delta is None:
                verdict = "candidate"
            elif delta >= args.win_margin:
                verdict = "winner"
            elif delta >= -args.win_margin:
                verdict = "near"
            else:
                verdict = "below_history"
            winners.append(
                {
                    "route": route,
                    "filetype": p.filetype,
                    "idea": p.idea,
                    "template": p.template,
                    "key": run.get("experiment_key"),
                    "f1": best_f1,
                    "precision": metric(run, "precision"),
                    "recall": metric(run, "recall"),
                    "roc_auc": metric(run, "roc_auc"),
                    "avg_precision": metric(run, "avg_precision"),
                    "elapsed_seconds": run.get("elapsed_seconds"),
                    "historical_best_key": hist_best.get("experiment_key") if hist_best else "",
                    "historical_best_idea": hist_best.get("idea") if hist_best else "",
                    "historical_best_f1": hist_f1,
                    "delta_vs_historical_f1": delta,
                    "verdict": verdict,
                    **{f"deployed_{k}": v for k, v in deployed.get(route, {}).items()},
                }
            )

    out_csv = Path(args.csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with out_csv.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    out_json = Path(args.json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps({"rows": rows, "winners": winners}, indent=2, sort_keys=True))

    verdict_counts = defaultdict(int)
    for w in winners:
        verdict_counts[w["verdict"]] += 1

    winners_sorted = sorted(
        winners,
        key=lambda w: (
            {"winner": 0, "near": 1, "candidate": 2, "below_history": 3}.get(w["verdict"], 9),
            -(w["delta_vs_historical_f1"] or -999),
            w["route"],
        ),
    )

    md = Path(args.markdown)
    md.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Azoth Filetype Manifest Tranche")
    lines.append("")
    lines.append("Stopped after the local DB replica was truncated. Results below use completed, content-addressed experiment summaries only; failed tail entries are excluded from candidate selection.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Planned entries: {len(planned)}")
    lines.append(f"- Completed/available entries: {completed_count}")
    lines.append(f"- Failed entries: {failed_count}")
    lines.append(f"- Missing entries: {missing}")
    lines.append(f"- Routes with completed candidates: {len(winners)}")
    lines.append(f"- Verdicts: " + ", ".join(f"{k}={verdict_counts[k]}" for k in sorted(verdict_counts)))
    lines.append(f"- CSV: `{out_csv}`")
    lines.append(f"- JSON: `{out_json}`")
    lines.append("")
    recommended = [
        w
        for w in winners_sorted
        if w["verdict"] in {"winner", "near"} and (w["f1"] is not None and w["f1"] >= 0.90)
    ]
    no_history = [w for w in winners_sorted if w["verdict"] == "candidate"]
    weak_no_history = [w for w in no_history if w["f1"] is None or w["f1"] < 0.90]
    strong_no_history = [w for w in no_history if w["f1"] is not None and w["f1"] >= 0.90]

    lines.append("## Recommended Retrain Set")
    lines.append("")
    lines.append("These are the tranche winners/near-winners that beat or matched prior route history and have usable sampled F1. Use these first for the next candidate model-set train.")
    lines.append("")
    lines.append("| route | idea | key | verdict | F1 | delta vs hist | AUC | AP |")
    lines.append("|---|---|---|---|---:|---:|---:|---:|")
    for w in recommended:
        lines.append(
            "| `{route}` | `{idea}` | `{key}` | {verdict} | {f1} | {delta} | {auc} | {ap} |".format(
                route=w["route"],
                idea=w["idea"],
                key=w["key"],
                verdict=w["verdict"],
                f1=fmt(w["f1"]),
                delta=fmt(w["delta_vs_historical_f1"]),
                auc=fmt(w["roc_auc"]),
                ap=fmt(w["avg_precision"]),
            )
        )
    lines.append("")
    lines.append("## Candidate Winners")
    lines.append("")
    lines.append("| verdict | route | best tranche idea | key | F1 | delta vs hist | AUC | AP | deployed L50 recall |")
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|")
    for w in winners_sorted:
        if w["verdict"] not in {"winner", "near", "candidate"}:
            continue
        lines.append(
            "| {verdict} | `{route}` | `{idea}` | `{key}` | {f1} | {delta} | {auc} | {ap} | {l50} |".format(
                verdict=w["verdict"],
                route=w["route"],
                idea=w["idea"],
                key=w["key"],
                f1=fmt(w["f1"]),
                delta=fmt(w["delta_vs_historical_f1"]),
                auc=fmt(w["roc_auc"]),
                ap=fmt(w["avg_precision"]),
                l50=fmt(w.get("deployed_l50_recall")),
            )
        )
    lines.append("")
    lines.append("## No Historical Baseline")
    lines.append("")
    lines.append("These routes had no non-tranche historical comparison in the experiment DB. Strong rows may be worth confirming; weak rows should be treated as diagnostics, not winners.")
    lines.append("")
    lines.append("| bucket | route | best tranche idea | key | F1 | AUC | AP |")
    lines.append("|---|---|---|---|---:|---:|---:|")
    for bucket, items in (("strong", strong_no_history), ("weak", weak_no_history)):
        for w in items:
            lines.append(
                "| {bucket} | `{route}` | `{idea}` | `{key}` | {f1} | {auc} | {ap} |".format(
                    bucket=bucket,
                    route=w["route"],
                    idea=w["idea"],
                    key=w["key"],
                    f1=fmt(w["f1"]),
                    auc=fmt(w["roc_auc"]),
                    ap=fmt(w["avg_precision"]),
                )
            )
    lines.append("")
    lines.append("## Below Historical Best")
    lines.append("")
    lines.append("| route | best tranche idea | F1 | historical best | hist F1 | delta |")
    lines.append("|---|---|---:|---|---:|---:|")
    for w in sorted([x for x in winners if x["verdict"] == "below_history"], key=lambda x: x["delta_vs_historical_f1"] or -999):
        lines.append(
            "| `{route}` | `{idea}` | {f1} | `{hist}` | {hist_f1} | {delta} |".format(
                route=w["route"],
                idea=w["idea"],
                f1=fmt(w["f1"]),
                hist=w["historical_best_idea"] or "-",
                hist_f1=fmt(w["historical_best_f1"]),
                delta=fmt(w["delta_vs_historical_f1"]),
            )
        )
    lines.append("")
    lines.append("## Failed Entries")
    lines.append("")
    for name in sorted(failed):
        lines.append(f"- `{name}`")
    lines.append("")
    lines.append("## Next Use")
    lines.append("")
    lines.append("Use `winner` and `near` rows as the first candidate set for a full model-set retrain. For routes marked `below_history`, keep the historical/default recipe unless a full-corpus route policy result says otherwise.")
    md.write_text("\n".join(lines) + "\n")

    print(f"wrote {md}")
    print(f"wrote {out_csv}")
    print(f"wrote {out_json}")
    print(f"completed={completed_count} failed={failed_count} missing={missing} routes={len(winners)}")
    print("verdicts:", dict(sorted(verdict_counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
