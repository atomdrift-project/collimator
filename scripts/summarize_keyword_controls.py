#!/usr/bin/env python3
"""Verify saved five-route controls and emit per-seed and mean comparisons."""
import argparse
import csv
import json
import os
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from keyword_route_controls import VARIANTS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--clean-go", action="store_true")
    args = parser.parse_args()
    os.environ["COLLIMATOR_SAMPLE_PERCENT"] = "10"
    from collimator.experiment import recall_at_per_100M
    raw = json.loads((args.root / "comparison.json").read_text())
    output = dict(sample_percent=10, seeds=raw["seeds"], colsample_bytree=1,
                  tree_budget=raw["tree_budget"], verified_controls=True,
                  scope="Paired dev screens; canonical-group sample, natural class proportions; locked test unused.",
                  routes={})
    seed_rows = []
    mean_rows = []
    ensemble_rows = []
    feature_revision = training_revision = common_training = None
    for route in ("java_class", "go", "c", "python", "javascript"):
        directory = args.root / route
        variants = raw["routes"][route]
        if route == "go" and args.clean_go:
            directory = args.root / "go-clean"
            clean = json.loads((directory / "comparison.json").read_text())
            variants = clean["variants"]
            original = json.loads((args.root / "go/selected_cohort.json").read_text())
            retained = json.loads((directory / "selected_cohort.json").read_text())
            assert {r["row_id"] for r in retained["train"]} == {r["row_id"] for r in original["train"]} - set(clean["manifest"]["excluded_training_rows"])
            assert original["test"] == retained["test"], "Go dev selection changed"
            assert raw["routes"]["go"]["baseline"]["base_dev_sha256"] == variants["baseline"]["base_dev_sha256"]
            output["go_data_quality"] = dict(manifest=clean["manifest"], original_dev_features_verified=True)
        route_output = {}
        base = variants["baseline"]
        reference_inputs = None
        reference_arrays = None
        reference_database = None
        for variant, flags in VARIANTS.items():
            record = variants[variant]
            assert "seeds" in record, f"incomplete {route}/{variant}"
            run_path = max((directory / variant / "runs").glob("*-experiment.json"), key=lambda p: p.stat().st_mtime)
            run = json.loads(run_path.read_text())
            experiment = run["experiment_spec"]
            env = experiment["feature_env"]
            assert env["COLLIMATOR_SAMPLE_PERCENT"] == "10"
            assert env["COLLIMATOR_RULE_KEYWORDS"] == str(flags[0])
            assert env["COLLIMATOR_DESCRIPTION_KEYWORDS"] == str(flags[1])
            assert experiment["train_samples"] == experiment["max_test_samples"] == experiment["total_limit"] == 0
            assert experiment.get("oof_fold_exclude") is None
            assert experiment["train_config"]["colsample_bytree"] == 1
            assert experiment["filters"]["min_malware_training_score"] == 0
            assert experiment["seed_search_k"] == 2 and run["save_all_seeds"]
            if common_training is None:
                common_training = experiment["train_config"]
                feature_revision = experiment["feature_revision"]
                training_revision = experiment["code_revision"]
            assert experiment["train_config"] == common_training
            assert experiment["feature_revision"] == feature_revision
            assert experiment["code_revision"] == training_revision
            inputs = (record["base_train_sha256"], record["base_dev_sha256"], record["evaluation_revision"],
                      record["train_rows"], record["dev_rows"], record["train_malware"], record["dev_malware"])
            if reference_inputs is None:
                reference_inputs = inputs
                reference_database = experiment["database_revision"]
            assert inputs == reference_inputs, f"unmatched inputs: {route}/{variant}"
            assert experiment["database_revision"] == reference_database
            with np.load(directory / variant / "dev_predictions.npz") as arrays:
                ids, labels = arrays["row_ids"], arrays["labels"]
                if reference_arrays is None:
                    reference_arrays = (ids.copy(), labels.copy())
                assert np.array_equal(ids, reference_arrays[0]) and np.array_equal(labels, reference_arrays[1])
                for item in record["seeds"]:
                    metrics = recall_at_per_100M(labels, arrays[f"seed_{item['seed']}"])
                    attempt = next(value for value in run["seed_search_results"] if value["seed"] == item["seed"])
                    assert np.isclose(metrics["level_budget_recall"], attempt["level_budget_recall"])
                    for budget in (0, 1):
                        key = f"recall_at_{budget}fp"
                        assert np.isclose(metrics[key], item[key]), f"metric mismatch: {route}/{variant}"
                averaged = np.mean([arrays[f"seed_{seed}"].astype(np.float64) for seed in raw["seeds"]], axis=0).astype(np.float32)
                ensemble = recall_at_per_100M(labels, averaged)
                for budget in (0, 1):
                    key = f"recall_at_{budget}fp"
                    assert np.isclose(ensemble[key], record["ensemble_metrics"][key])
            source_summary = {}
            for budget in (0, 1):
                key = f"recall_at_{budget}fp"
                values = [item[key] for item in record["seeds"]]
                deltas = [item[key] - other[key] for item, other in zip(record["seeds"], base["seeds"], strict=True)]
                source_summary[key] = dict(mean=float(np.mean(values)), per_seed=values,
                                            mean_delta_pp=float(np.mean(deltas) * 100),
                                            per_seed_delta_pp=[float(delta * 100) for delta in deltas])
            source_summary["keyword_usage"] = [item["keyword_usage"] for item in record["seeds"]]
            source_summary["experiment_key"] = record["experiment_key"]
            source_summary["ensemble"] = {
                f"recall_at_{budget}fp": record["ensemble_metrics"][f"recall_at_{budget}fp"]
                for budget in (0, 1)
            }
            route_output[variant] = source_summary
            for item, other in zip(record["seeds"], base["seeds"], strict=True):
                seed_rows.append(dict(route=route, variant=variant, seed=item["seed"],
                    train_rows=record["train_rows"], dev_malware=record["dev_malware"], dev_benign=record["dev_benign"],
                    recall_at_0fp=item["recall_at_0fp"], recall_at_1fp=item["recall_at_1fp"],
                    delta_0fp_pp=100 * (item["recall_at_0fp"] - other["recall_at_0fp"]),
                    delta_1fp_pp=100 * (item["recall_at_1fp"] - other["recall_at_1fp"]),
                    used_keyword_features=sum(u["used"] for u in item["keyword_usage"].values()),
                    tree_count=item["n_trees"]))
            mean_rows.append(dict(route=route, variant=variant,
                recall_at_0fp=source_summary["recall_at_0fp"]["mean"],
                recall_at_1fp=source_summary["recall_at_1fp"]["mean"],
                delta_0fp_pp=source_summary["recall_at_0fp"]["mean_delta_pp"],
                delta_1fp_pp=source_summary["recall_at_1fp"]["mean_delta_pp"]))
            ensemble_rows.append(dict(route=route, variant=variant,
                **source_summary["ensemble"],
                delta_0fp_pp=100*(source_summary["ensemble"]["recall_at_0fp"]-base["ensemble_metrics"]["recall_at_0fp"]),
                delta_1fp_pp=100*(source_summary["ensemble"]["recall_at_1fp"]-base["ensemble_metrics"]["recall_at_1fp"])))
        output["routes"][route] = dict(train_rows=base["train_rows"], dev_rows=base["dev_rows"],
            dev_malware=base["dev_malware"], dev_benign=base["dev_benign"], variants=route_output)
    output["feature_revision"] = feature_revision
    output["training_revision"] = training_revision
    (args.root / "results_summary.json").write_text(json.dumps(output, indent=2) + "\n")
    for name, rows in (("per_seed.csv", seed_rows), ("means.csv", mean_rows), ("ensembles.csv", ensemble_rows)):
        with (args.root / name).open("w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print("Verified 40 comparable fits across five routes.")
    for route, result in output["routes"].items():
        print(route, {name: round(value["recall_at_1fp"]["mean_delta_pp"], 2)
                      for name, value in result["variants"].items()})


if __name__ == "__main__":
    main()
