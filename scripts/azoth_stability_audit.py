#!/usr/bin/env python3
"""Audit saved routes for numerical instability and compare capped dev trials.

Historical external benchmark scores are not used to choose trials or winners.
Freeze each selected route, compare uncapped/2/5/10 with fixed train/dev splits,
and retain the independent assessment half for the final comparison.
"""
from __future__ import annotations

import argparse
import csv
import gc
import json
import logging
import os
from pathlib import Path
from types import SimpleNamespace

import numpy as np

import azoth_portable_stability as experiment

LOG = logging.getLogger("stability_audit")
CAPS = {"baseline": {}, "cap2": {"max_delta_step": 2.0},
        "cap5": {"max_delta_step": 5.0}, "cap10": {"max_delta_step": 10.0}}


def model_summary(path):
    count, low, high = 0, float("inf"), float("-inf")
    first_high = None
    with path.open() as stream:
        for line in stream:
            if line.startswith("Tree="):
                count += 1
            elif line.startswith("leaf_value="):
                values = [float(x) for x in line.split("=", 1)[1].split()]
                low, high = min(low, min(values)), max(high, max(values))
                if count == 1:
                    first_high = max(values)
    return {"seed": int(path.stem.split("_")[-1]), "trees": count,
            "min_leaf": low, "max_leaf": high, "first_tree_max_leaf": first_high}


def flags_for(row):
    flags = []
    seeds = row["models"]
    if any(s["max_leaf"] > 17 or s["min_leaf"] < -104 for s in seeds):
        flags.append("extreme_leaf_outputs")
    if seeds and max(s["trees"] for s in seeds) >= 20 * max(1, min(s["trees"] for s in seeds)):
        flags.append("uneven_tree_counts")
    ap = row["holdout_ap"]
    if ap and max(ap) - min(ap) >= .15:
        flags.append("uneven_holdout_ap")
    if ap and min(ap) < .7:
        flags.append("weak_holdout_ap")
    if row["train_malware"] is not None and row["train_malware"] < 100:
        flags.append("limited_positive_support")
    return flags


def audit(source, output):
    rows = []
    for models in sorted(source.rglob("models")):
        files = sorted(models.glob("seed_*.txt"))
        if not files:
            continue
        root = models.parent
        benchmark = root / "benchmark.json"
        saved = json.loads(benchmark.read_text()) if benchmark.exists() else {}
        attempts = saved.get("seed_health", {}).get("attempts", [])
        row = {"route": str(root.relative_to(source)), "train_rows": saved.get("train_rows"),
               "train_malware": saved.get("train_malware"),
               "holdout_ap": [a["avg_precision"] for a in attempts if a.get("accepted")],
               "models": [model_summary(p) for p in files]}
        row["flags"] = flags_for(row)
        rows.append(row)
    output.mkdir(parents=True, exist_ok=True)
    experiment.write_json(output / "audit.json", {"routes": rows,
        "note": "Risk flags are diagnostic, not proof of dev failure. Holdouts differ between saved seeds; trial comparisons use a common dev cohort."})
    with (output / "audit.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["route", "train_rows", "train_malware", "holdout_ap", "trees", "max_leaf", "flags"])
        for r in rows:
            writer.writerow([r["route"], r["train_rows"], r["train_malware"], r["holdout_ap"],
                             [s["trees"] for s in r["models"]], [s["max_leaf"] for s in r["models"]], r["flags"]])
    return rows


def run_route(args, route):
    root = args.output / route.replace("/", "-")
    if (root / "complete.json").exists():
        return
    case = SimpleNamespace(source=args.source / route, output=root, db=args.db,
                           max_id=args.max_id, workers=args.workers, threads=args.threads, variants=CAPS)
    os.environ["COLLIMATOR_MATRIX_DISK_DIR"] = str(root / "scratch")
    experiment.prepare(case)
    xt, yt, buckets, _ = experiment.load_matrix(root, "train")
    xd, yd, dev_buckets, filetypes = experiment.load_matrix(root, "dev")
    fit, selection = buckets >= .12, dev_buckets < .5
    xv, yv = xt[~fit], yt[~fit]
    xt, yt = xt[fit], yt[fit]
    counts = {name: {"rows": len(y), "malware": int(y.sum()), "benign": int((y == 0).sum())}
              for name, y in (("fit", yt), ("early_stop", yv),
                              ("selection", yd[selection]), ("assessment", yd[~selection]))}
    experiment.write_json(root / "cohorts.json", counts)
    if any(min(c["malware"], c["benign"]) < 30 for c in counts.values()):
        experiment.write_json(root / "insufficient-support.json", counts)
        LOG.warning("%s: too little class support for these comparisons: %s", route, counts)
        return
    experiment.score_original(case, xd, yd, selection)
    config = json.loads((root / "original/benchmark.json").read_text())["train_config"]
    # Freeze the candidate grid before looking at assessment outcomes.
    experiment.write_json(root / "trial-plan.json", CAPS)
    for name, overrides in CAPS.items():
        experiment.fit_variant(case, name, overrides, xt, yt, xv, yv, xd, yd, selection, config)
    winner, comparisons, predictions = experiment.summarize(case, yd, selection, filetypes)
    experiment.assessment(case, yd, selection, filetypes, winner, comparisons, predictions)
    experiment.write_json(root / "complete.json", {"route": route, "winner": winner})
    LOG.info("COMPLETE %s: %s", route, winner)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("out/models/azoth"))
    parser.add_argument("--output", type=Path, default=Path("out/experiments/route-stability-20261027"))
    parser.add_argument("--routes", nargs="*", default=[])
    parser.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    parser.add_argument("--max-id", type=int, default=6309383805)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--threads", type=int, default=8)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    rows = audit(args.source, args.output)
    LOG.info("Audited %d routes; %d have diagnostic flags", len(rows), sum(bool(r["flags"]) for r in rows))
    outcomes = []
    for route in args.routes:
        try:
            run_route(args, route)
            outcomes.append({"route": route, "status": "complete" if (args.output / route.replace("/", "-") / "complete.json").exists() else "insufficient_support"})
        except Exception as exc:
            LOG.exception("Route experiment failed: %s", route)
            outcomes.append({"route": route, "status": "failed", "error": str(exc)})
        experiment.write_json(args.output / "status.json", outcomes)
        gc.collect()
    if any(row["status"] == "failed" for row in outcomes):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
