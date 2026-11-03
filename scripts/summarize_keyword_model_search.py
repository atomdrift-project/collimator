#!/usr/bin/env python3
"""Collect independently verified specialist comparisons and export parity cases."""
import argparse
import csv
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from keyword_model_search import ROUTES
from collimator.bundle import atomic_write_json


def confirmed_candidates(confirmation):
    baseline = confirmation["variants"]["baseline"]
    candidates = []
    for name, result in confirmation["variants"].items():
        if name == "baseline" or result.get("diagnostic"):
            continue
        current, old = result["confirmation"], baseline["confirmation"]
        deltas = [current[f"recall_{budget}fp"]-old[f"recall_{budget}fp"] for budget in (0, 1)]
        pairs_pass = all(
            result[f"confirmation_seeds_{a}_{b}"][f"recall_{budget}fp"] >=
            baseline[f"confirmation_seeds_{a}_{b}"][f"recall_{budget}fp"]
            for a, b in ((43, 44), (45, 46)) for budget in (0, 1))
        if min(deltas) >= 0 and max(deltas) > 0 and pairs_pass and current["ap"] >= old["ap"]-.005:
            candidates.append(result)
    return sorted(candidates, key=lambda r: (r["confirmation"]["recall_1fp"],
        r["confirmation"]["recall_0fp"], r["confirmation"]["ap"]), reverse=True)


def summarize(root):
    records = []
    for route in ROUTES:
        directory = root / route
        if not (directory / "verified_summary.json").exists():
            records.append(dict(route=route, status="incomplete"))
            continue
        verified = json.loads((directory / "verified_summary.json").read_text())
        confirmation = json.loads((directory / "confirmation.json").read_text())
        baseline = confirmation["variants"]["baseline"]
        eligible = confirmed_candidates(confirmation)
        chosen = eligible[0] if eligible else baseline
        before, after = baseline["confirmation"], chosen["confirmation"]
        item = dict(route=route, status="confirmed_improvement" if eligible else "no_confirmed_improvement",
                    winner=chosen["name"], sources=chosen["options"], training=chosen["variant"]["training"],
                    baseline=before, candidate=after,
                    delta_0fp_pp=100*(after["recall_0fp"]-before["recall_0fp"]),
                    delta_1fp_pp=100*(after["recall_1fp"]-before["recall_1fp"]),
                    seed_pairs_preserve_both_budgets=bool(eligible),
                    finalists=list(confirmation["variants"]),
                    verified_models=sum(v["models"] for v in verified["verification"]),
                    sizes=verified["inputs"]["sizes"], scope="Reserved development ranking confirmation; locked test unused.")
        records.append(item)
    atomic_write_json(root / "summary.json", dict(routes=records,
        deployment="No production threshold or deployed model is changed by this research study."))
    complete = [r for r in records if r["status"] != "incomplete"]
    with (root / "comparison.csv").open("w", newline="") as stream:
        columns = ["route", "status", "winner", "confirmation_malware", "confirmation_goodware",
                   "baseline_0fp", "candidate_0fp", "delta_0fp_pp", "baseline_1fp", "candidate_1fp", "delta_1fp_pp"]
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for r in complete:
            writer.writerow(dict(route=r["route"], status=r["status"], winner=r["winner"],
                confirmation_malware=r["baseline"]["malware"], confirmation_goodware=r["baseline"]["goodware"],
                baseline_0fp=r["baseline"]["recall_0fp"], candidate_0fp=r["candidate"]["recall_0fp"],
                baseline_1fp=r["baseline"]["recall_1fp"], candidate_1fp=r["candidate"]["recall_1fp"],
                delta_0fp_pp=r["delta_0fp_pp"], delta_1fp_pp=r["delta_1fp_pp"]))
    for r in records:
        print(r["route"], r["status"], r.get("winner"), r.get("delta_0fp_pp"), r.get("delta_1fp_pp"))
    return complete


def fetch_parity_reports(root, output, db):
    from collimator import data, features
    from collimator.corpus_snapshot import frozen_corpus
    selected = {}
    records = summarize(root)
    for record in records:
        if record["status"] != "confirmed_improvement":
            continue
        directory = root / record["route"]
        with np.load(directory / "inputs/rows.npz") as arrays:
            labels, mask = arrays["y_dev"], ~arrays["search"]
            ids = arrays["row_ids"][len(arrays["y_train"]):]
        with np.load(directory / "confirmation" / record["winner"] / "predictions.npz") as arrays:
            scores = arrays["ensemble"]
        for label in (0, 1):
            candidates = np.flatnonzero(mask & (labels == label))
            ranked = candidates[np.argsort(scores[candidates], kind="stable")]
            for index in ranked[np.linspace(0, len(ranked)-1, min(4, len(ranked)), dtype=int)]:
                selected[int(ids[index])] = (record["route"], label)
    if not selected:
        raise ValueError("no confirmed candidate to export")
    output.mkdir(parents=True, exist_ok=True)
    with frozen_corpus(db) as snapshot:
        fetched = data.fetch_cleave_results(db, sorted(selected),
            evaluation_labels={rid: label for rid, (_, label) in selected.items()})
        assert set(fetched) == set(selected)
        cases = [dict(name=f"{selected[rid][0]}-{rid}", row_id=rid, label=selected[rid][1],
                      report=features._coerce_report(fetched[rid]["cleave_result"])) for rid in sorted(selected)]
    atomic_write_json(output / "reports.json", dict(snapshot=snapshot, cases=cases,
        scope="Runtime parity on fresh copies of saved dev reports; no accuracy measurement."))


def export_parity(root, output):
    import keyword_scan_model_fixtures as parity
    records = summarize(root)
    parity.BUNDLES = {r["route"]: root/r["route"]/'confirmation'/r["winner"]
                      for r in records if r["status"] == "confirmed_improvement"}
    parity.build(SimpleNamespace(output=output))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("root", type=Path)
    p.add_argument("--action", choices=["summarize", "fetch", "export"], default="summarize")
    p.add_argument("--output", type=Path)
    p.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    args = p.parse_args()
    output = args.output or args.root / "runtime-parity"
    if args.action == "summarize":
        summarize(args.root)
    elif args.action == "fetch":
        fetch_parity_reports(args.root, output, args.db)
    else:
        export_parity(args.root, output)


if __name__ == "__main__":
    main()
