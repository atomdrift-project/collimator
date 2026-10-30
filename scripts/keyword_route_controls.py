#!/usr/bin/env python3
"""Paired keyword controls on a canonical-hash sample of several routes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import lightgbm as lgb
import numpy as np
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
VARIANTS = {"baseline": (0, 0), "ids": (1, 0), "descriptions": (0, 1), "both": (1, 1)}


def matrix_digest(matrix):
    """Hash values and positions independently of CSR index width/storage order."""
    matrix = matrix.tocsr(copy=True)
    matrix.sum_duplicates()
    matrix.eliminate_zeros()
    matrix.sort_indices()
    digest = hashlib.sha256(str(matrix.shape).encode())
    for array, dtype in ((matrix.indptr, "<i8"), (matrix.indices, "<i8"), (matrix.data, "<f4")):
        digest.update(np.asarray(array, dtype=dtype).tobytes())
    return digest.hexdigest()


def command(args, route, variant, directory):
    ids, descriptions = VARIANTS[variant]
    return ["make", "experiment", f"DB={args.db}", f"EXP_ROUTE=filetypes/{route}",
            f"SEED={args.seed}", "EXP_TRAIN_SAMPLES=0", "EXP_MAX_TEST_SAMPLES=0",
            "EXP_TOTAL_LIMIT=0", "EXP_FOLDS=0", "EXP_MIN_SAMPLE_SCORE=0",
            "EXP_MIN_MALWARE_SCORE=0", f"EXP_ESTIMATORS={args.trees}",
            "EXP_COLSAMPLE_BYTREE=1", "EXP_WORKERS=4", "EXP_LGBM_THREADS=4",
            "EXP_SEED_SEARCH_K=2", "EXP_SAVE_ALL_SEEDS=1", "EXP_ALLOWED_FEATURES_FILE=",
            f"EXP_RULE_KEYWORDS={ids}", f"EXP_DESCRIPTION_KEYWORDS={descriptions}",
            "EXP_KEYWORD_VOCAB_MAX=10000", "EXP_KEYWORD_MIN_FREQ=5",
            f"EXP_IDEA=keyword_full_columns_{variant}",
            f"EXP_OUT_DIR={directory / variant}", f"EXP_CACHE_DIR={directory / 'cache'}"]


def read_variant(root, cache, seed):
    from collimator.experiment import recall_at_per_100M
    run_path = max((root / "runs").glob("*-experiment.json"), key=lambda p: p.stat().st_mtime)
    run = json.loads(run_path.read_text())
    spec = json.loads((root / "feature_spec.json").read_text())
    matches = [path for path in cache.glob("matrix_*_spec.json") if json.loads(path.read_text()) == spec]
    if len(matches) != 1:
        raise ValueError(f"expected one matching matrix for {root}, got {len(matches)}")
    stem = str(matches[0])[:-len("_spec.json")]
    with np.load(stem + ".npz", allow_pickle=True) as arrays:
        labels = arrays["y_test"]
        train_labels = arrays["y_train"]
        row_ids = arrays["test_row_ids"]
        revision = str(arrays["evaluation_revision"].item())
    matrix = sp.load_npz(stem + "_Xtest.npz")
    names = spec["feature_names"]
    base_columns = [i for i, name in enumerate(names) if not name.startswith(("ruleword:", "descword:"))]
    base_names = [names[i] for i in base_columns]
    train = sp.load_npz(stem + "_Xtrain.npz")
    train_digest = matrix_digest(train[:, base_columns])
    del train
    dev_digest = matrix_digest(matrix[:, base_columns])
    seeds = []
    probabilities = {}
    for member_seed in (seed, seed + 1):
        model_path = root / "models" / f"seed_{member_seed}.txt"
        model = lgb.Booster(model_file=str(model_path))
        scores = np.asarray(model.predict(matrix, num_threads=4), dtype=np.float32)
        probabilities[f"seed_{member_seed}"] = scores
        metrics = recall_at_per_100M(labels, scores)
        splits = model.feature_importance("split")
        gains = model.feature_importance("gain")
        usage = {}
        for source, words in spec.get("keyword_vocabs", {}).items():
            columns = [i for i, name in enumerate(names) if name.startswith(source + ":")]
            used = sorted((i for i in columns if splits[i]), key=lambda i: -gains[i])
            usage[source] = dict(selected=len(words), used=len(used),
                                 split_count=sum(int(splits[i]) for i in columns),
                                 top_words=[dict(word=names[i], gain=float(gains[i])) for i in used[:12]])
        timings = []
        for _ in range(3):
            started = time.perf_counter()
            model.predict(matrix, num_threads=4)
            timings.append(time.perf_counter() - started)
        seeds.append(dict(seed=member_seed, recall_at_0fp=metrics.get("recall_at_0fp"),
                          recall_at_1fp=metrics.get("recall_at_1fp"),
                          level_budget_recall=metrics.get("level_budget_recall"),
                          n_trees=model.num_trees(), keyword_usage=usage,
                          scoring_seconds=float(np.median(timings))))
    mean_scores = np.mean([scores.astype(np.float64) for scores in probabilities.values()], axis=0).astype(np.float32)
    ensemble_metrics = recall_at_per_100M(labels, mean_scores)
    for budget in (0, 1):
        key = f"recall_at_{budget}fp"
        if key in ensemble_metrics and not np.isclose(ensemble_metrics[key], run["sampled_test_metrics"][key]):
            raise ValueError("saved-model ensemble differs from recorded metrics")
    np.savez_compressed(root / "dev_predictions.npz", row_ids=row_ids, labels=labels, **probabilities)
    result = dict(experiment_key=run["experiment_key"], seeds=seeds,
                  train_rows=len(train_labels), train_malware=int(np.sum(train_labels == 1)),
                  train_benign=int(np.sum(train_labels == 0)),
                  dev_rows=len(labels), dev_malware=int(np.sum(labels == 1)), dev_benign=int(np.sum(labels == 0)),
                  features=len(names), dev_matrix_nnz=int(matrix.nnz),
                  spec_bytes=(root / "feature_spec.json").stat().st_size,
                  ensemble_metrics=ensemble_metrics, elapsed_seconds=run["elapsed_seconds"],
                  base_train_sha256=train_digest, base_dev_sha256=dev_digest,
                  evaluation_revision=revision,
                  feature_revision=run["experiment_spec"]["feature_revision"],
                  database_revision=run["experiment_spec"]["database_revision"])
    identity = (base_names, train_digest, dev_digest, revision,
                hashlib.sha256(row_ids.tobytes() + labels.tobytes() + train_labels.tobytes()).hexdigest())
    return result, identity


def paired_changes(directory, baseline, variant_name, result):
    with np.load(directory / "baseline" / "dev_predictions.npz") as old, np.load(directory / variant_name / "dev_predictions.npz") as new:
        for base, current in zip(baseline["seeds"], result["seeds"], strict=True):
            labels = old["labels"]
            from collimator.thresholds import recall_at_fp_budget
            old_scores = np.asarray(old[f"seed_{base['seed']}"], dtype=np.float32)
            new_scores = np.asarray(new[f"seed_{current['seed']}"], dtype=np.float32)
            for budget in (0, 1):
                key = f"recall_at_{budget}fp"
                if current[key] is None or base[key] is None:
                    continue
                current[f"delta_at_{budget}fp"] = current[key] - base[key]
                _, old_threshold, _ = recall_at_fp_budget(labels, old_scores, budget)
                _, new_threshold, _ = recall_at_fp_budget(labels, new_scores, budget)
                old_detection = (np.zeros(len(labels), dtype=bool) if old_threshold is None
                                 else old_scores >= old_threshold)
                new_detection = (np.zeros(len(labels), dtype=bool) if new_threshold is None
                                 else new_scores >= new_threshold)
                current[f"changes_at_{budget}fp"] = dict(
                    recovered=int(np.sum((labels == 1) & ~old_detection & new_detection)),
                    lost=int(np.sum((labels == 1) & old_detection & ~new_detection)))


def audit_missing(args):
    from collimator import data, features
    directory = args.output / args.audit_missing
    cohort = json.loads((directory / "selected_cohort.json").read_text())
    rows = {row["row_id"]: dict(label=row["label"], partition=partition)
            for key, partition in (("train", "train"), ("test", "dev")) for row in cohort[key]}
    ids = sorted(rows)
    missing = []
    for start in range(0, len(ids), 500):
        for row_id, item in data.fetch_cleave_results(args.db, ids[start:start + 500]).items():
            report = features._coerce_report(item["cleave_result"])
            if report is None:
                continue
            rule_ids = set()
            for file in features.report_files(report):
                for finding in features.file_findings(file):
                    fid = features.finding_id(finding)
                    if not fid or features._float(features.finding_conf(finding), features.MISSING_CONF) < features.MIN_CONFIDENCE:
                        continue
                    description = features._alias(finding, "desc", "d", "description")
                    if not isinstance(description, str) or not description.strip():
                        rule_ids.add(fid)
            if rule_ids:
                missing.append(dict(row_id=row_id, **rows[row_id], missing_rule_ids=sorted(rule_ids)))
    result = dict(route=args.audit_missing, selected_rows=len(rows), affected_rows=missing,
                  source="Live report lookup restricted to the saved train/dev selection; no locked test IDs.")
    path = directory / "missing_descriptions.json"
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Saved {path}: {len(missing)} affected rows among {len(rows)} selected", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    parser.add_argument("--routes", nargs="+", default=["java_class", "go", "c", "python", "javascript"])
    parser.add_argument("--output", type=Path, default=Path("out/experiments/keyword-controls-10pct"))
    parser.add_argument("--sample-percent", default="10")
    parser.add_argument("--seed", type=int, default=43)
    parser.add_argument("--trees", type=int, default=180)
    parser.add_argument("--keep-cache", action="store_true")
    parser.add_argument("--audit-missing", help="Audit descriptions only in a completed route's saved train/dev cohort")
    args = parser.parse_args()
    if any(not route.replace("_", "").isalnum() for route in args.routes):
        parser.error("provide bare filetype names")
    os.environ["COLLIMATOR_SAMPLE_PERCENT"] = args.sample_percent
    os.environ["EXP_EVAL_SEED"] = "42"
    from collimator import data
    from collimator.bundle import atomic_write_json
    from collimator.corpus_snapshot import frozen_corpus
    sample_predicate = data.sample_predicate(args.sample_percent)
    if data.SAMPLE_PREDICATE != sample_predicate:
        raise ValueError("sampling must be configured before importing collimator.data")
    if args.audit_missing:
        with frozen_corpus(args.db):
            audit_missing(args)
        return
    args.output.mkdir(parents=True, exist_ok=True)
    summary = dict(sample_percent=args.sample_percent, sample_predicate=sample_predicate,
                   seeds=[args.seed, args.seed + 1], colsample_bytree=1,
                   train_samples=0, max_dev_samples=0, malware_training_floor=0,
                   tree_budget=args.trees, routes={},
                   scope="Natural 10% canonical-group sample; train/dev only. Each seed is reported separately.")
    with frozen_corpus(args.db):
        summary["snapshot_max_id"] = data.snapshot_max_id(args.db)
        for route in args.routes:
            directory = args.output / route
            directory.mkdir(exist_ok=True)
            route_result = summary["routes"].setdefault(route, {})
            identity = None
            for variant in VARIANTS:
                print(f"Starting {route}/{variant}", flush=True)
                started = time.perf_counter()
                log_path = directory / f"{variant}.log"
                with log_path.open("w") as log:
                    process = subprocess.run(command(args, route, variant, directory),
                                             env=os.environ.copy(), stdout=log, stderr=subprocess.STDOUT)
                if process.returncode:
                    route_result[variant] = dict(error=log_path.read_text()[-5000:], returncode=process.returncode)
                    print(f"FAILED {route}/{variant}: see {log_path}", flush=True)
                    atomic_write_json(args.output / "comparison.json", summary)
                    continue
                result, captured = read_variant(directory / variant, directory / "cache", args.seed)
                if identity is None:
                    identity = captured
                if captured != identity:
                    raise ValueError(f"base features, selected rows, or report inputs differ in {route}/{variant}")
                route_result[variant] = result
                if variant != "baseline" and "seeds" in route_result.get("baseline", {}):
                    paired_changes(directory, route_result["baseline"], variant, result)
                result["verified_matched_inputs"] = True
                print(json.dumps(dict(route=route, variant=variant, train=result["train_rows"],
                                      dev=result["dev_rows"], seeds=result["seeds"],
                                      elapsed_seconds=time.perf_counter() - started)), flush=True)
                atomic_write_json(args.output / "comparison.json", summary)
            if not args.keep_cache and (directory / "cache").exists():
                cohorts = list((directory / "cache").glob("corpus_*.json"))
                if len(cohorts) != 1:
                    raise ValueError(f"expected one shared selection in {directory}")
                shutil.copyfile(cohorts[0], directory / "selected_cohort.json")
                # Only this run's regenerable matrices/checkpoints are removed;
                # models, specs, logs, identities and per-row predictions persist.
                shutil.rmtree(directory / "cache")
            atomic_write_json(args.output / "comparison.json", summary)
    print(f"Finished: {args.output / 'comparison.json'}", flush=True)


if __name__ == "__main__":
    main()
