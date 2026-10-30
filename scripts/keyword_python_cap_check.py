#!/usr/bin/env python3
"""Check the binding Python description cap on the same 10% row boundary."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from keyword_route_controls import command, read_variant


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    parser.add_argument("--study", type=Path, default=Path("out/experiments/keyword-controls-10pct-confirm"))
    parser.add_argument("--output", type=Path, default=Path("out/experiments/keyword-python-cap-10pct"))
    args = parser.parse_args()
    os.environ["COLLIMATOR_SAMPLE_PERCENT"] = "10"
    os.environ["EXP_EVAL_SEED"] = "42"
    from collimator import data, features
    from collimator.bundle import atomic_write_json
    from collimator.corpus_snapshot import frozen_corpus
    from collimator.experiment import sample_partitioned_reports
    original = json.loads((args.study / "comparison.json").read_text())
    boundary = original["snapshot_max_id"]
    args.output.mkdir(parents=True, exist_ok=True)
    controls = argparse.Namespace(db=args.db, seed=43, trees=180)
    study = dict(sample_percent=10, snapshot_max_id=boundary, variants={},
                 scope="Separate paired description-cap comparison on a fresh snapshot at the five-route study's row boundary.")
    with frozen_corpus(args.db):
        print("Auditing Python description vocabulary", flush=True)
        cohort = sample_partitioned_reports(args.db, train_samples=0, max_test_samples=0,
            seed=43, total_limit=0, min_malware_training_score=0, max_id=boundary,
            route_file_types=("python",), evaluation_seed=42)
        rows = sorted(row.row_id for row in cohort.train_samples)
        counters = {"descword": Counter()}
        for start in range(0, len(rows), 500):
            for _ in features._count_keyword_reports(data.fetch_cleave_results(args.db, rows[start:start+500]).values(), counters):
                pass
        eligible = sum(n >= 5 for n in counters["descword"].values())
        study["eligible_description_words"] = eligible
        study["distinct_description_words"] = len(counters["descword"])
        study["train_rows"] = len(rows)
        study["dev_rows"] = len(cohort.test_samples)
        caps = []
        effective = set()
        equivalents = {}
        for cap in (10000, 25000, 50000):
            actual = min(eligible, cap)
            if actual not in effective:
                caps.append(cap)
                effective.add(actual)
            equivalents[str(cap)] = caps[-1]
        study["equivalent_caps"] = equivalents
        atomic_write_json(args.output / "comparison.json", study)
        print(f"{eligible} eligible description words; distinct caps {caps}", flush=True)
        identity = None
        for cap in caps:
            name = f"cap-{cap}"
            print(f"Starting {name}", flush=True)
            parameters = command(controls, "python", "descriptions", args.output)
            replacements = {
                "EXP_KEYWORD_VOCAB_MAX": str(cap), "EXP_OUT_DIR": str(args.output / name),
                "EXP_IDEA": f"keyword_python_description_cap_{cap}", "EXP_MAX_ID": str(boundary),
            }
            parameters = [entry for entry in parameters if entry.split("=",1)[0] not in replacements]
            parameters.extend(f"{key}={value}" for key,value in replacements.items())
            start = time.perf_counter()
            with (args.output / f"{name}.log").open("w") as log:
                subprocess.run(parameters, env=os.environ.copy(), stdout=log, stderr=subprocess.STDOUT, check=True)
            result, captured = read_variant(args.output / name, args.output / "cache", 43)
            if identity is None:
                identity = captured
            if captured != identity:
                raise ValueError("base inputs differ between Python cap trials")
            result["wall_seconds"] = time.perf_counter() - start
            result["onnx_bytes"] = sum(path.stat().st_size for path in (args.output / name / "models").glob("*.onnx"))
            result["verified_matched_inputs"] = True
            study["variants"][str(cap)] = result
            atomic_write_json(args.output / "comparison.json", study)
            print(json.dumps(dict(cap=cap, words=result["seeds"][0]["keyword_usage"]["descword"]["selected"],
                recalls=[(s["seed"],s["recall_at_0fp"],s["recall_at_1fp"]) for s in result["seeds"]])), flush=True)


if __name__ == "__main__":
    main()
