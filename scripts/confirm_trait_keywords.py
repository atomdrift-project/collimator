#!/usr/bin/env python3
"""Confirm description keywords with paired models on a shared dev cohort."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import lightgbm as lgb
import numpy as np
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from collimator.corpus_snapshot import frozen_corpus


def latest_run(directory):
    paths = list((directory / "runs").glob("*-experiment.json"))
    if not paths:
        raise ValueError(f"no completed run in {directory}")
    return json.loads(max(paths, key=lambda path: path.stat().st_mtime).read_text())


def load_scores(directory, cache):
    run = latest_run(directory)
    spec = json.loads((directory / "feature_spec.json").read_text())
    candidates = []
    for path in cache.glob("matrix_*_spec.json"):
        if json.loads(path.read_text()) == spec:
            candidates.append(path)
    if len(candidates) != 1:
        raise ValueError(f"expected one matching matrix for {directory}, found {len(candidates)}")
    stem = str(candidates[0])[:-len("_spec.json")]
    with np.load(stem + ".npz", allow_pickle=True) as arrays:
        labels = arrays["y_test"]
        ids = arrays["test_row_ids"]
        revision = str(arrays["evaluation_revision"].item())
    matrix = sp.load_npz(stem + "_Xtest.npz")
    model = lgb.Booster(model_file=str(directory / "model.txt"))
    # The count-budget threshold selector operates on float32 scores. Comparing
    # its saved thresholds against float64 predictions can lose boundary rows.
    scores = np.asarray(model.predict(matrix, num_threads=4), dtype=np.float32)
    for budget in (0, 1):
        metrics = run["sampled_test_metrics"]
        detected = scores >= metrics[f"threshold_at_{budget}fp"]
        recall = float(np.mean(detected[labels == 1]))
        if not np.isclose(recall, metrics[f"recall_at_{budget}fp"]):
            raise ValueError("saved-model scores disagree with recorded recall")
    return dict(run=run, spec=spec, labels=labels, ids=ids, matrix=matrix,
                scores=scores, model=model, revision=revision)


def changed_rows(base, desc, budget):
    old_threshold = base["run"]["sampled_test_metrics"][f"threshold_at_{budget}fp"]
    new_threshold = desc["run"]["sampled_test_metrics"][f"threshold_at_{budget}fp"]
    old = base["scores"] >= old_threshold
    new = desc["scores"] >= new_threshold
    masks = {
        "recovered_malware": (desc["labels"] == 1) & ~old & new,
        "lost_malware": (desc["labels"] == 1) & old & ~new,
        "new_false_positives": (desc["labels"] == 0) & ~old & new,
        "removed_false_positives": (desc["labels"] == 0) & old & ~new,
    }
    return {name: desc["ids"][mask].tolist() for name, mask in masks.items()}


def explain_rows(desc, changes):
    # Explain changed detections and the highest-scoring benigns. Contributions
    # are signed log-odds effects, not causal claims about the individual words.
    groups = {name: ids[:5] for name, ids in changes.items()}
    benign = np.flatnonzero(desc["labels"] == 0)
    groups["highest_scoring_benign"] = desc["ids"][
        benign[np.argsort(desc["scores"][benign])[-5:][::-1]]
    ].tolist()
    selected = sorted({rid for ids in groups.values() for rid in ids})
    positions = {int(rid): idx for idx, rid in enumerate(desc["ids"])}
    indices = [positions[rid] for rid in selected]
    if not indices:
        return dict(groups=groups, rows=[])
    matrix = desc["matrix"][indices]
    contributions = desc["model"].predict(matrix, pred_contrib=True, num_threads=4)
    if sp.issparse(contributions):
        contributions = contributions.toarray()
    names = desc["spec"]["feature_names"]
    keyword_indices = [i for i, name in enumerate(names) if name.startswith("descword:")]
    rows = []
    for local, (rid, idx) in enumerate(zip(selected, indices)):
        present = set(matrix[local].indices)
        strongest = sorted(keyword_indices, key=lambda col: -abs(contributions[local, col]))[:8]
        rows.append(dict(row_id=rid, label=int(desc["labels"][idx]),
                         description_score=float(desc["scores"][idx]),
                         keyword_effects=[dict(feature=names[col], present=col in present,
                                               log_odds_contribution=float(contributions[local, col]))
                                          for col in strongest]))
    return dict(groups=groups, rows=rows)


def summarize(root, seeds):
    summary = dict(pairs=[], shared_snapshot_verified=True, fixed_dev_rows_verified=True)
    reference_ids = reference_labels = reference_revision = None
    snapshot_identity = None
    for seed in seeds:
        directory = root / f"seed-{seed}"
        base = load_scores(directory / "baseline", directory / "cache")
        desc = load_scores(directory / "descriptions", directory / "cache")
        for item in (base, desc):
            identity = tuple(item["run"]["experiment_spec"][name]
                             for name in ("database_revision", "snapshot_max_id", "feature_revision"))
            if snapshot_identity is None:
                snapshot_identity = identity
            if identity != snapshot_identity:
                raise ValueError("snapshot or feature code changed between fits")
            if reference_ids is None:
                reference_ids, reference_labels = item["ids"], item["labels"]
                reference_revision = item["revision"]
            if (not np.array_equal(item["ids"], reference_ids)
                    or not np.array_equal(item["labels"], reference_labels)
                    or item["revision"] != reference_revision):
                raise ValueError("dev inputs changed between fits")
        names = [name for name in desc["spec"]["feature_names"] if not name.startswith("descword:")]
        if names != base["spec"]["feature_names"]:
            raise ValueError("base feature columns differ within a pair")
        if (base["matrix"] != desc["matrix"][:, :len(names)]).nnz:
            raise ValueError("base dev feature values differ within a pair")
        corpora = list((directory / "cache").glob("corpus_*.json"))
        if len(corpora) != 1:
            raise ValueError("expected one shared training selection per seed; use a fresh output root")
        cohort_hash = hashlib.sha256(corpora[0].read_bytes()).hexdigest()
        pair = dict(seed=seed, selected_cohort_sha256=cohort_hash,
                    train_rows=base["run"]["train_rows"], dev_rows=len(base["ids"]),
                    keyword_count=len(desc["spec"]["keyword_vocabs"]["descword"]),
                    baseline_key=base["run"]["experiment_key"],
                    description_key=desc["run"]["experiment_key"])
        for budget in (0, 1):
            key = f"recall_at_{budget}fp"
            pair[key] = {variant: item["run"]["sampled_test_metrics"][key]
                         for variant, item in (("baseline", base), ("descriptions", desc))}
            pair[key]["delta"] = pair[key]["descriptions"] - pair[key]["baseline"]
            pair[f"changes_at_{budget}fp"] = changed_rows(base, desc, budget)
        pair["examples"] = explain_rows(desc, pair["changes_at_0fp"])
        positions = {int(rid): idx for idx, rid in enumerate(base["ids"])}
        for row in pair["examples"]["rows"]:
            idx = positions[row["row_id"]]
            row["baseline_score"] = float(base["scores"][idx])
            for name, item in (("baseline", base), ("description", desc)):
                row[f"{name}_margin_at_0fp"] = float(
                    item["scores"][idx] - item["run"]["sampled_test_metrics"]["threshold_at_0fp"]
                )
        summary["pairs"].append(pair)
    summary["mean_deltas"] = {
        f"recall_at_{budget}fp": float(np.mean([pair[f"recall_at_{budget}fp"]["delta"]
                                               for pair in summary["pairs"]]))
        for budget in (0, 1)
    }
    summary["snapshot_max_id"] = snapshot_identity[1]
    summary["scope"] = "Dev screening only; locked test is untouched. Seeds vary training selection and learner randomness."
    path = root / "confirmation.json"
    path.write_text(json.dumps(summary, indent=2) + "\n")
    for pair in summary["pairs"]:
        print(json.dumps({key: pair[key] for key in ("seed", "recall_at_0fp", "recall_at_1fp")}), flush=True)
    print(f"Saved {path}; mean deltas: {summary['mean_deltas']}", flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    parser.add_argument("--output", type=Path, default=Path("out/experiments/trait-keywords-confirm"))
    parser.add_argument("--seeds", type=int, nargs="+", default=[43, 44, 45])
    parser.add_argument("--train-rows", type=int, default=20000)
    parser.add_argument("--dev-rows", type=int, default=5000)
    parser.add_argument("--trees", type=int, default=100)
    parser.add_argument("--summarize-only", action="store_true")
    args = parser.parse_args()
    if args.summarize_only:
        summarize(args.output, args.seeds)
        return
    args.output.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, EXP_EVAL_SEED="42")
    with frozen_corpus(args.db):
        # frozen_corpus exports the snapshot after env was first copied.
        env.update({name: value for name, value in os.environ.items()
                    if name.startswith("COLLIMATOR_PG_SNAPSHOT")})
        for seed in args.seeds:
            directory = args.output / f"seed-{seed}"
            directory.mkdir(exist_ok=True)
            for variant in ("baseline", "descriptions"):
                print(f"Starting seed {seed}, {variant}", flush=True)
                command = ["make", "experiment", f"DB={args.db}", "EXP_ROUTE=filetypes/python",
                           f"SEED={seed}", f"EXP_TRAIN_SAMPLES={args.train_rows}",
                           f"EXP_MAX_TEST_SAMPLES={args.dev_rows}", f"EXP_ESTIMATORS={args.trees}",
                           "EXP_WORKERS=4", "EXP_LGBM_THREADS=4", "EXP_SEED_SEARCH_K=1",
                           "EXP_ALLOWED_FEATURES_FILE=", "EXP_RULE_KEYWORDS=0",
                           f"EXP_DESCRIPTION_KEYWORDS={int(variant == 'descriptions')}",
                           "EXP_KEYWORD_VOCAB_MAX=10000", "EXP_KEYWORD_MIN_FREQ=5",
                           f"EXP_IDEA=trait_keywords_confirm_{variant}",
                           f"EXP_OUT_DIR={directory / variant}", f"EXP_CACHE_DIR={directory / 'cache'}"]
                with (directory / f"{variant}.log").open("w") as log:
                    subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
                run = latest_run(directory / variant)
                metrics = run["sampled_test_metrics"]
                print(f"Finished seed {seed}, {variant}: recall@0FP={metrics['recall_at_0fp']:.4f}, "
                      f"recall@1FP={metrics['recall_at_1fp']:.4f}", flush=True)
    summarize(args.output, args.seeds)


if __name__ == "__main__":
    main()
