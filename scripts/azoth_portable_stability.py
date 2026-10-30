#!/usr/bin/env python3
"""Compare portable seeds on frozen train/dev features; never read test reports.

The dev cohort is split by canonical identity into selection and assessment.
All tuning, thresholds, and seed admission use selection only. Run sequentially
with bounded workers/threads alongside the nightly recovery. Outputs are resumable.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import inspect
import itertools
import json
import logging
import os
from pathlib import Path
import shutil
import time

import lightgbm as lgb
import numpy as np
from scipy import sparse
from sklearn.metrics import average_precision_score, roc_auc_score

from collimator import data, features, model, train
from azoth_specialist_suite import _temporary_feature_env

LOG = logging.getLogger("portable_stability")
SEEDS = (42, 43, 44)
VARIANTS = {
    "baseline": {},
    "neutral_init": {"boost_from_average": False},
    "cap5": {"max_delta_step": 5.0},
    "cap10": {"max_delta_step": 10.0},
    "neutral_cap5": {"boost_from_average": False, "max_delta_step": 5.0},
    "neutral_cap10": {"boost_from_average": False, "max_delta_step": 10.0},
    "weight010": {"scale_pos_weight_mult": 0.1},
    "weight025": {"scale_pos_weight_mult": 0.25},
    "weight050": {"scale_pos_weight_mult": 0.5},
    "no_hard_negatives": {"hard_negative_fraction": 0.0},
}


def write_json(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    tmp.replace(path)


def split_bucket(canonical):
    """Independent of the last-byte production partition; group duplicates."""
    return int.from_bytes(hashlib.sha256(("portable-stability-v1:" + canonical).encode()).digest()[:4], "big") / 2**32


def threshold_at_fp_budget(y, scores, budget):
    """Inclusive score threshold with no partial acceptance of tied scores."""
    benign = np.sort(np.asarray(scores, dtype=np.float64)[y == 0])[::-1]
    if budget < 0:
        raise ValueError("FP budget must be nonnegative")
    if len(benign) <= budget:
        return float(np.min(scores))
    return float(np.nextafter(benign[budget], np.inf))


def operating_point(y, scores, threshold):
    detected = np.asarray(scores, dtype=np.float64) >= threshold
    tp = int(np.sum(detected & (y == 1)))
    fp = int(np.sum(detected & (y == 0)))
    positives = int(np.sum(y == 1))
    return {"threshold": threshold, "tp": tp, "fp": fp,
            "recall": tp / max(positives, 1),
            "precision": tp / max(tp + fp, 1)}


def metrics(y, scores):
    both = len(np.unique(y)) == 2
    return {"rows": len(y), "malware": int(np.sum(y == 1)),
            "ap": float(average_precision_score(y, scores)) if np.any(y) else None,
            "auc": float(roc_auc_score(y, scores)) if both else None,
            "at_fp": {str(b): operating_point(y, scores, threshold_at_fp_budget(y, scores, b))
                      for b in (0, 1, 5, 10)}}


def save_matrix(root, name, matrix, labels, ids, metadata):
    dest = root / name
    dest.mkdir(exist_ok=True)
    for key, value in (("data", matrix.data), ("indices", matrix.indices),
                       ("indptr", matrix.indptr), ("y", labels), ("ids", ids),
                       ("bucket", [metadata[int(i)][0] for i in ids]),
                       ("filetype", [metadata[int(i)][1] for i in ids])):
        np.save(dest / (key + ".npy"), np.asarray(value))
    write_json(dest / "shape.json", list(matrix.shape))


def load_matrix(root, name):
    dest = root / name
    arrays = {k: np.load(dest / (k + ".npy"), mmap_mode="r")
              for k in ("data", "indices", "indptr", "y", "bucket", "filetype")}
    matrix = sparse.csr_matrix((arrays["data"], arrays["indices"], arrays["indptr"]),
                               shape=json.loads((dest / "shape.json").read_text()), copy=False)
    return matrix, arrays["y"], arrays["bucket"], arrays["filetype"]


def prepare(args):
    root = args.output
    root.mkdir(parents=True, exist_ok=True)
    if (root / "prepared.json").exists():
        return
    frozen = root / "original"
    if not frozen.exists():
        shutil.copytree(args.source, frozen)
    benchmark = json.loads((frozen / "benchmark.json").read_text())
    spec = features.FeatureSpec.load(frozen / "feature_spec.json")
    if spec.standardized:
        raise ValueError("This experiment expects unstandardized portable features")
    LOG.info("Fetching all %s train/dev identities through snapshot %d", args.source, args.max_id)
    train_rows, dev_rows, metadata = [], [], {}
    query = ("SELECT id, sha256, label, canonical_sha256, score, file_type FROM samples WHERE "
             + data.LABELED_WHERE + " AND id <= %s AND file_type = ANY(%s) ORDER BY id")
    with data._connect(args.db, repeatable_read=True) as conn:
        with conn.cursor(name="portable_experiment") as cur:
            cur.itersize = 10000
            cur.execute(query, (args.max_id, benchmark["file_types"]))
            for rid, sha, label, canonical, score, filetype in cur:
                key = canonical or sha
                partition = data.partition_of(key)
                if partition == "test":
                    continue
                y = int(label == "bad")
                if partition == "train" and y and int(score or 0) < benchmark["min_malware_training_score"]:
                    continue
                rows = train_rows if partition == "train" else dev_rows
                rows.append((int(rid), y))
                metadata[int(rid)] = (split_bucket(key), filetype)
    LOG.info("Extracting %d train and %d dev rows (all eligible rows, fixed saved vocabulary)", len(train_rows), len(dev_rows))
    identity = {}
    with _temporary_feature_env(benchmark["feature_env"]):
        xt, yt, xd, yd = features.extract_partitioned_from_db(
            args.db, train_rows, dev_rows, spec, n_workers=args.workers, identity=identity)
    save_matrix(root, "train", xt, yt, identity["train_row_ids"], metadata)
    save_matrix(root, "dev", xd, yd, identity["test_row_ids"], metadata)
    manifest = {"max_id": args.max_id, "train_rows": len(yt), "train_malware": int(yt.sum()),
                "dev_rows": len(yd), "dev_malware": int(yd.sum()),
                "requested_train_rows": len(train_rows), "requested_dev_rows": len(dev_rows),
                "evaluation_revision": identity["evaluation_revision"],
                "feature_spec_sha256": hashlib.sha256((frozen / "feature_spec.json").read_bytes()).hexdigest(),
                "lightgbm": lgb.__version__, "threads": args.threads,
                "split": "canonical hash: train bucket >= .12 fit; < .12 early stopping; dev < .5 selection, >= .5 assessment",
                "selection": "maximize selection AP; break ties with recall at 5 FP; choose subsets using selection only",
                "variants": getattr(args, "variants", VARIANTS)}
    write_json(root / "prepared.json", manifest)
    LOG.info("Frozen features complete: %s", manifest)


def predict(booster, matrix, threads):
    raw = np.concatenate([booster.predict(matrix[i:i + 50000], raw_score=True, num_threads=threads)
                          for i in range(0, matrix.shape[0], 50000)])
    # Match LightGBM's sigmoid and collimator's float32 probability conversion.
    with np.errstate(over="ignore"):
        probability64 = 1.0 / (1.0 + np.exp(-raw))
    return raw, probability64, probability64.astype(np.float32)


def precision_diagnostics(y, raw, p64, p32):
    return {"ap_raw_margin": float(average_precision_score(y, raw)),
            "ap_probability64": float(average_precision_score(y, p64)),
            "ap_probability32": float(average_precision_score(y, p32)),
            "raw_min": float(raw.min()), "raw_max": float(raw.max()),
            "saturated_ones64": int(np.sum(p64 == 1)),
            "saturated_ones32": int(np.sum(p32 == 1)),
            "saturated_zeros32": int(np.sum(p32 == 0))}


def original_seeds(root):
    """Read actual saved members, including replacements for quarantined seeds."""
    directory = root / 'original'
    path = directory / 'benchmark.json'
    benchmark = json.loads(path.read_text()) if path.exists() else {}
    seeds = benchmark.get('seed_health', {}).get('accepted_seeds')
    if seeds is None:
        seeds = sorted(int(p.stem.removeprefix('seed_'))
                       for p in (directory / 'models').glob('seed_*.txt'))
    seeds = tuple(int(seed) for seed in seeds)
    if not seeds or len(seeds) != len(set(seeds)):
        raise ValueError(f'Invalid saved ensemble membership: {directory}')
    for seed in seeds:
        model_path = directory / 'models' / f'seed_{seed}.txt'
        if not model_path.exists():
            raise FileNotFoundError(f'Saved ensemble member missing: {model_path}')
    return seeds


def score_original(args, xd, yd, selection):
    for seed in original_seeds(args.output):
        dest = args.output / "results" / f"original_seed{seed}"
        if (dest / "result.json").exists():
            continue
        dest.mkdir(parents=True, exist_ok=True)
        booster = lgb.Booster(model_file=str(args.output / "original" / "models" / f"seed_{seed}.txt"))
        raw, p64, p32 = predict(booster, xd, args.threads)
        np.savez(dest / "predictions.npz", raw=raw, probability=p32)
        result = {"variant": "original", "seed": seed, "trees": booster.num_trees(),
                  "selection": metrics(yd[selection], p32[selection]),
                  "precision": precision_diagnostics(yd[selection], raw[selection], p64[selection], p32[selection])}
        write_json(dest / "result.json", result)
        LOG.info("Original seed %d: %s", seed, result)


def fit_variant(args, name, overrides, xt, yt, xv, yv, xd, yd, selection, config):
    constructor_keys = inspect.signature(model.create_classifier).parameters
    for seed in SEEDS:
        dest = args.output / "results" / f"{name}_seed{seed}"
        if (dest / "result.json").exists():
            continue
        dest.mkdir(parents=True, exist_ok=True)
        settings = {**config, **overrides, "device": "cpu", "random_state": seed, "num_threads": args.threads}
        kwargs = {k: v for k, v in settings.items() if k in constructor_keys}
        kwargs.update(n_benign=int(np.sum(yt == 0)), n_malware=int(yt.sum()))
        histories = []
        started = time.monotonic()

        def fit(weights=None):
            estimator = model.create_classifier(**kwargs)
            estimator.set_params(boost_from_average=overrides.get("boost_from_average", True),
                                 max_delta_step=settings.get("max_delta_step", 0.0),
                                 metric=["average_precision", "binary_logloss"])
            history = {}
            callbacks = [lgb.record_evaluation(history)]
            enough_validation = min(int(np.sum(yv == label)) for label in (0, 1)) >= train.MIN_EARLY_STOPPING_CLASS_SIZE
            if settings["early_stopping_rounds"] and enough_validation:
                callbacks.append(lgb.early_stopping(settings["early_stopping_rounds"], first_metric_only=True, verbose=False))
            elif settings["early_stopping_rounds"]:
                LOG.info("%s seed %d: early stopping disabled for small validation classes; using full tree budget", name, seed)
            eval_args = {"eval_X": xv, "eval_y": yv} if "eval_X" in inspect.signature(estimator.fit).parameters else {"eval_set": [(xv, yv)]}
            estimator.fit(xt, yt, sample_weight=weights, callbacks=callbacks, **eval_args)
            histories.append({"best_iteration": estimator.best_iteration_, "trees": estimator.booster_.num_trees(),
                              "history": history})
            return estimator

        LOG.info("START %s seed %d overrides=%s", name, seed, overrides)
        estimator = fit()
        weights = train._compute_hard_negative_weights(estimator, xt, yt,
                   fraction=settings["hard_negative_fraction"], weight=settings["hard_negative_weight"])
        if weights is not None:
            del estimator
            gc.collect()
            estimator = fit(weights)
        booster = estimator.booster_
        booster.save_model(str(dest / "model.txt"))
        raw, p64, p32 = predict(booster, xd, args.threads)
        np.savez(dest / "predictions.npz", raw=raw, probability=p32)
        vr, v64, v32 = predict(booster, xv, args.threads)
        result = {"variant": name, "seed": seed, "overrides": overrides,
                  "trees": booster.num_trees(), "seconds": time.monotonic() - started,
                  "selection": metrics(yd[selection], p32[selection]),
                  "precision": precision_diagnostics(yd[selection], raw[selection], p64[selection], p32[selection]),
                  "early_stop_precision": precision_diagnostics(yv, vr, v64, v32),
                  "fits": histories}
        write_json(dest / "result.json", result)
        LOG.info("DONE %s seed %d trees=%d AP=%.6f recall@5FP=%.4f seconds=%.1f", name, seed,
                 result["trees"], result["selection"]["ap"], result["selection"]["at_fp"]["5"]["recall"], result["seconds"])
        del estimator, booster, weights
        gc.collect()


def rank(result, objective='ap'):
    if objective == 'low-fp':
        return (result['at_fp']['0']['recall'], result['at_fp']['1']['recall'],
                result['ap'], result['at_fp']['5']['recall'])
    return result["ap"], result["at_fp"]["5"]["recall"]


def summarize(args, yd, selection, filetypes):
    predictions = {}
    individual = []
    for path in sorted((args.output / "results").glob("*/result.json")):
        result = json.loads(path.read_text())
        individual.append({k: v for k, v in result.items() if k != "fits"})
        predictions[(result["variant"], result["seed"])] = np.load(path.parent / "predictions.npz")["probability"]
    selection_results = []
    for name in sorted({name for name, _ in predictions}):
        expected = original_seeds(args.output) if name == 'original' else SEEDS
        seeds = [s for s in expected if (name, s) in predictions]
        if len(seeds) != len(expected):
            continue
        for size in range(1, len(seeds) + 1):
            for subset in itertools.combinations(seeds, size):
                p = np.mean([predictions[(name, s)] for s in subset], axis=0, dtype=np.float32)
                selection_results.append({"variant": name, "seeds": list(subset),
                                          "selection": metrics(yd[selection], p[selection])})
    # Winner and seed admission are frozen before consulting assessment labels.
    objective = getattr(args, 'selection_objective', 'ap')
    winner = max((r for r in selection_results if r["variant"] != "original"), key=lambda r: rank(r["selection"], objective))
    write_json(args.output / "selection.json", {"winner": winner, "comparisons": selection_results, "individual": individual})
    # Hold back assessment until all trials have finished.
    return winner, selection_results, predictions


def assessment(args, yd, selection, filetypes, winner, comparisons, predictions):
    chosen = [winner]
    for name in sorted({r["variant"] for r in comparisons}):
        rows = [r for r in comparisons if r["variant"] == name]
        chosen += [max(rows, key=lambda r: rank(r["selection"])), max(rows, key=lambda r: len(r["seeds"]))]
    reports = []
    seen = set()
    for entry in chosen:
        key = (entry["variant"], tuple(entry["seeds"]))
        if key in seen:
            continue
        seen.add(key)
        p = np.mean([predictions[(entry["variant"], s)] for s in entry["seeds"]], axis=0, dtype=np.float32)
        mask = ~selection
        thresholds = {b: v["threshold"] for b, v in entry["selection"]["at_fp"].items()}
        def report(subset):
            y, scores = yd[subset], p[subset]
            return {"rows": len(y), "malware": int(y.sum()),
                    "ap": float(average_precision_score(y, scores)) if np.any(y) else None,
                    "fixed_thresholds": {b: operating_point(y, scores, t) for b, t in thresholds.items()}}
        reports.append({**entry, "assessment": report(mask),
                        "by_filetype": {str(ft): report(mask & (filetypes == ft)) for ft in np.unique(filetypes)}})
    write_json(args.output / "assessment.json", {"selected_winner": winner, "comparisons": reports})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    parser.add_argument("--max-id", type=int, default=6309383805)
    parser.add_argument("--source", type=Path, default=Path("out/models/azoth/filegroups/portable"))
    parser.add_argument("--output", type=Path, default=Path("out/experiments/portable-stability-20261027"))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    os.environ.setdefault("COLLIMATOR_MATRIX_DISK_DIR", str(args.output / "scratch"))
    prepare(args)
    if args.prepare_only:
        return
    xt, yt, buckets, _ = load_matrix(args.output, "train")
    xd, yd, dev_buckets, filetypes = load_matrix(args.output, "dev")
    fit = buckets >= 0.12
    selection = dev_buckets < 0.5
    xv, yv = xt[~fit], yt[~fit]
    xt, yt = xt[fit], yt[fit]
    for name, labels in (("fit", yt), ("early_stop", yv), ("selection", yd[selection]), ("assessment", yd[~selection])):
        LOG.info("%s: %d rows %d malware", name, len(labels), labels.sum())
        if min(np.sum(labels == 0), np.sum(labels == 1)) < 30:
            raise ValueError(f"Insufficient class support in {name}")
    config = json.loads((args.output / "original" / "benchmark.json").read_text())["train_config"]
    score_original(args, xd, yd, selection)
    for name, overrides in VARIANTS.items():
        fit_variant(args, name, overrides, xt, yt, xv, yv, xd, yd, selection, config)
        summarize(args, yd, selection, filetypes)
    # One adaptive combination chosen exclusively on selection: strongest
    # stabilizer, strongest weight, and hard-negative toggle (3 additional seeds).
    _, comparisons, _ = summarize(args, yd, selection, filetypes)
    def best(names):
        return max((r for r in comparisons if r["variant"] in names and len(r["seeds"]) == 3), key=lambda r: rank(r["selection"]))["variant"]
    stability = best(["baseline", "neutral_init", "cap5", "cap10", "neutral_cap5", "neutral_cap10"])
    weighting = best(["baseline", "weight010", "weight025", "weight050"])
    hard_negative = best(["baseline", "no_hard_negatives"])
    combined = {**VARIANTS[stability], **VARIANTS[weighting], **VARIANTS[hard_negative]}
    write_json(args.output / "combined-plan.json", {"stability": stability, "weighting": weighting, "hard_negative": hard_negative, "overrides": combined})
    fit_variant(args, "combined", combined, xt, yt, xv, yv, xd, yd, selection, config)
    winner, comparisons, predictions = summarize(args, yd, selection, filetypes)
    assessment(args, yd, selection, filetypes, winner, comparisons, predictions)
    write_json(args.output / "complete.json", {"winner": winner})
    LOG.info("COMPLETE selected winner: %s", winner)


if __name__ == "__main__":
    main()
