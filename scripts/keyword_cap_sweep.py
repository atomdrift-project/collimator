#!/usr/bin/env python3
"""Audit and screen distinct keyword vocabularies under one corpus snapshot."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from collimator import data, features
from collimator.corpus_snapshot import frozen_corpus
from collimator.experiment import sample_partitioned_reports


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    p.add_argument("--route", default="filetypes/java_class")
    p.add_argument("--output", type=Path, default=Path("out/experiments/keyword-caps-java-class"))
    p.add_argument("--caps", nargs="+", type=int, default=[1000, 3000, 10000, 25000, 50000])
    p.add_argument("--min-freq", type=int, default=5)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--train-rows", type=int, default=20000)
    p.add_argument("--dev-rows", type=int, default=5000)
    p.add_argument("--trees", type=int, default=100)
    args = p.parse_args()
    if not args.route.startswith("filetypes/") or min(args.caps) < 1 or args.min_freq < 1:
        p.error("provide one filetype route and positive caps/frequency")
    args.output.mkdir(parents=True, exist_ok=True)
    with frozen_corpus(args.db):
        boundary = data.snapshot_max_id(args.db)
        print("Selecting the shared cohort", flush=True)
        cohort = sample_partitioned_reports(
            args.db, train_samples=args.train_rows, max_test_samples=args.dev_rows,
            seed=args.seed, total_limit=0, min_malware_training_score=4, max_id=boundary,
            route_file_types=(args.route.split("/", 1)[1],), evaluation_seed=42,
        )
        counters = {source: Counter() for source in ("ruleword", "descword")}
        rows = sorted(cohort.train_samples, key=lambda row: row.row_id)
        started = time.perf_counter()
        for start in range(0, len(rows), 500):
            ids = [row.row_id for row in rows[start:start + 500]]
            for _ in features._count_keyword_reports(data.fetch_cleave_results(args.db, ids).values(), counters):
                pass
        audit = dict(route=args.route, seed=args.seed, snapshot_max_id=boundary,
                     train_rows=len(rows), dev_rows=len(cohort.test_samples),
                     min_frequency=args.min_freq, audit_seconds=time.perf_counter() - started,
                     sources={})
        jobs = [("baseline", 0, 0, 10000)]
        for source, counts in counters.items():
            eligible = sum(n >= args.min_freq for n in counts.values())
            effective = {}
            aliases = {}
            for cap in sorted(set(args.caps)):
                actual = min(cap, eligible)
                if actual not in effective:
                    effective[actual] = cap
                    if actual:
                        jobs.append((f"{source}-{cap}", int(source == "ruleword"), int(source == "descword"), cap))
                aliases[str(cap)] = effective[actual]
            audit["sources"][source] = dict(distinct_words=len(counts), eligible_words=eligible,
                                            caps_equivalent_to=aliases,
                                            document_frequencies=dict(counts.most_common()))
            print(f"{source}: {eligible} eligible words; distinct caps {list(effective.values())}", flush=True)
        jobs.append(("both-10000", 1, 1, 10000))
        (args.output / "audit.json").write_text(json.dumps(audit, indent=2) + "\n")
        results = []
        shared_ids = shared_revision = None
        for name, ids_enabled, desc_enabled, cap in jobs:
            print(f"Starting {name}", flush=True)
            command = ["make", "experiment", f"DB={args.db}", f"EXP_ROUTE={args.route}",
                       f"SEED={args.seed}", f"EXP_TRAIN_SAMPLES={args.train_rows}",
                       f"EXP_MAX_TEST_SAMPLES={args.dev_rows}", f"EXP_ESTIMATORS={args.trees}",
                       "EXP_WORKERS=4", "EXP_LGBM_THREADS=4", "EXP_SEED_SEARCH_K=1",
                       "EXP_ALLOWED_FEATURES_FILE=", "EXP_MIN_MALWARE_SCORE=4",
                       f"EXP_RULE_KEYWORDS={ids_enabled}", f"EXP_DESCRIPTION_KEYWORDS={desc_enabled}",
                       f"EXP_KEYWORD_VOCAB_MAX={cap}", f"EXP_KEYWORD_MIN_FREQ={args.min_freq}",
                       f"EXP_IDEA=keyword_cap_{name}", f"EXP_OUT_DIR={args.output / name}",
                       f"EXP_CACHE_DIR={args.output / 'cache'}"]
            with (args.output / f"{name}.log").open("w") as log:
                subprocess.run(command, env=dict(os.environ, EXP_EVAL_SEED="42"),
                               stdout=log, stderr=subprocess.STDOUT, check=True)
            root = args.output / name
            path = max((root / "runs").glob("*-experiment.json"), key=lambda path: path.stat().st_mtime)
            run = json.loads(path.read_text())
            if shared_ids is None:
                shared_ids = run["test_sample_row_ids"]
                shared_revision = run["experiment_spec"]["database_revision"]
            if run["test_sample_row_ids"] != shared_ids or run["experiment_spec"]["database_revision"] != shared_revision:
                raise ValueError("comparison inputs changed")
            spec = json.loads((root / "feature_spec.json").read_text())
            import lightgbm as lgb
            import numpy as np
            import scipy.sparse as sp
            candidates = [path for path in (args.output / "cache").glob("matrix_*_spec.json")
                          if json.loads(path.read_text()) == spec]
            stem = str(candidates[-1])[:-len("_spec.json")]
            matrix = sp.load_npz(stem + "_Xtest.npz")
            model = lgb.Booster(model_file=str(root / "model.txt"))
            splits = model.feature_importance(importance_type="split")
            keyword_columns = [i for i, feature in enumerate(spec["feature_names"])
                               if feature.startswith(("ruleword:", "descword:"))]
            model.predict(matrix, num_threads=4)
            timings = []
            for _ in range(5):
                start = time.perf_counter()
                model.predict(matrix, num_threads=4)
                timings.append(time.perf_counter() - start)
            metrics = run["sampled_test_metrics"]
            result = dict(name=name, experiment_key=run["experiment_key"],
                          words={k: len(v) for k, v in spec.get("keyword_vocabs", {}).items()},
                          n_features=run["n_features"], elapsed_seconds=run["elapsed_seconds"],
                          recall_at_0fp=metrics["recall_at_0fp"], recall_at_1fp=metrics["recall_at_1fp"],
                          scoring_median_seconds=float(np.median(timings)),
                          matrix_nnz=int(matrix.nnz),
                          n_trees=model.num_trees(),
                          keyword_features_used=sum(int(splits[i] > 0) for i in keyword_columns),
                          keyword_split_count=sum(int(splits[i]) for i in keyword_columns),
                          spec_bytes=(root / "feature_spec.json").stat().st_size,
                          onnx_bytes=(root / "model.onnx").stat().st_size)
            results.append(result)
            print(json.dumps(result), flush=True)
            (args.output / "comparison.json").write_text(json.dumps(dict(audit=audit,
                results=results, shared_snapshot_verified=True, fixed_dev_rows_verified=True), indent=2) + "\n")


if __name__ == "__main__":
    main()
