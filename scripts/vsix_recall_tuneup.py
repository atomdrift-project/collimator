#!/usr/bin/env python3
"""Select VSIX recipes on grouped training CV at L0/L25; confirm once on dev.

No locked-test reports or labels enter fitting, vocabulary discovery, or scoring.
CV is conditional on frozen training vocabularies. Dev is reused confirmation,
not an independent population estimate or a deployment gate.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, fields, replace
import hashlib
import json
import logging
import multiprocessing as mp
from pathlib import Path
import shutil
from types import SimpleNamespace

import numpy as np
import onnxruntime as ort

import azoth_portable_stability as study
import azoth_specialist_tuneup as tune
from azoth_specialist_suite import _temporary_feature_env
from collimator import cache_identity, data, export, features, train
from collimator.corpus_snapshot import frozen_corpus
from collimator.thresholds import resolution_adjusted_fp_budget

LOG = logging.getLogger("vsix_recall")
SEEDS = (42, 43, 44)
ABLATIONS = {
    "no_keywords": ["ruleword", "descword"],
    "descriptions": ["ruleword"],
    "ids": ["descword"],
    "no_kv": ["kv"],
}
GRID = {
    "replay": {},
    "all_rows": {"holdout_fraction": 0., "early_stopping_rounds": 0},
    "budget100": {"n_estimators": 100},
    "budget400": {"n_estimators": 400},
    "cap2": {"max_delta_step": 2.},
    "weight025": {"scale_pos_weight_mult": .25},
    "weight005": {"scale_pos_weight_mult": .05},
    "weight2": {"scale_pos_weight_mult": 2.},
    "fine": {"min_child_samples": 10, "min_child_weight": 1., "num_leaves": 32},
    "fine_weight025": {"min_child_samples": 10, "min_child_weight": 1., "num_leaves": 32, "scale_pos_weight_mult": .25},
    "shallow": {"min_child_samples": 20, "min_child_weight": 1., "num_leaves": 16, "max_depth": 5, "reg_lambda": 5.},
    "shallow_weight025": {"min_child_samples": 20, "min_child_weight": 1., "num_leaves": 16, "max_depth": 5, "reg_lambda": 5., "scale_pos_weight_mult": .25},
    "full_sampling": {"colsample_bytree": 1., "subsample": 1.},
    "extra_trees": {"extra_trees": True, "min_child_samples": 20, "num_leaves": 32},
    "dart": {"boosting_type": "dart", "n_estimators": 250},
    "hard_negatives": {"holdout_fraction": .12, "hard_negative_fraction": .03, "hard_negative_weight": 5.},
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def exact_metrics(y, scores):
    """Use runtime float32 cuts, including an inactive threshold above one."""
    scores = np.asarray(scores, dtype=np.float32)
    benign = np.sort(scores[y == 0])[::-1]
    if not len(benign):
        raise ValueError("Cannot calibrate levels without benign observations")
    result = {"rows": len(y), "malware": int(y.sum()), "benign": len(benign)}
    for level in (0, 25):
        budget = resolution_adjusted_fp_budget(len(benign), level)
        cut = float(np.nextafter(benign[budget], np.float32(np.inf))) if budget < len(benign) else 0.
        result[f"L{level}"] = {"budget": budget, **study.operating_point(y, scores, cut)}
    return result


def rank(record):
    m = record["fold_metrics"]
    # Equal fold weights avoid letting a large group dominate the selection.
    return (float(np.mean([v["L25"]["recall"] for v in m])),
            float(np.mean([v["L0"]["recall"] for v in m])),
            float(min(v["L25"]["recall"] for v in m)))


def choose(records):
    control = records[0]
    floor = np.mean([m["L0"]["recall"] for m in control["fold_metrics"]])
    eligible = [r for r in records if np.mean([m["L0"]["recall"] for m in r["fold_metrics"]]) >= floor]
    return max(eligible, key=rank)


def confirmation_details(y, baseline, candidate, groups, ids, bm, cm):
    """Paired canonical-group bootstrap, conditional on the selected cuts."""
    _, inverse = np.unique(groups[y == 1], return_inverse=True)
    totals = np.bincount(inverse)
    draws = np.random.default_rng(42).integers(0, len(totals), size=(5000, len(totals)))
    denominator = totals[draws].sum(axis=1)
    details = {}
    for level in ("L0", "L25"):
        base = baseline >= bm[level]["threshold"]
        new = candidate >= cm[level]["threshold"]
        a = np.bincount(inverse, weights=base[y == 1])[draws].sum(axis=1) / denominator
        b = np.bincount(inverse, weights=new[y == 1])[draws].sum(axis=1) / denominator
        details[level] = {
            "baseline_recall_ci95": np.quantile(a, [.025, .975]).tolist(),
            "candidate_recall_ci95": np.quantile(b, [.025, .975]).tolist(),
            "paired_delta_ci95": np.quantile(b - a, [.025, .975]).tolist(),
            "recovered_malware_ids": ids[(y == 1) & new & ~base].tolist(),
            "lost_malware_ids": ids[(y == 1) & base & ~new].tolist(),
            "baseline_false_positive_ids": ids[(y == 0) & base].tolist(),
            "candidate_false_positive_ids": ids[(y == 0) & new].tolist(),
        }
    return {"levels": details, "bootstrap_positive_groups": len(totals), "resamples": 5000,
            "scope": "Conditional on selected dev thresholds; does not account for threshold selection, historical dev reuse, or future corpus drift."}


def complement_metrics(y, baseline, candidate):
    """Measure retention as an alternative, with one shared FP allowance."""
    from azoth_route_policy_search import _joint_or_search
    routes = {"baseline": baseline, "candidate": candidate}
    result, cumulative = {}, np.zeros(len(y), dtype=bool)
    for level in (0, 25):
        budget = resolution_adjusted_fp_budget(int((y == 0).sum()), level)
        cuts, hit = _joint_or_search(routes, y, tuple(routes), fp_budget=budget)
        cumulative |= hit
        fp = int(np.sum(cumulative & (y == 0)))
        if fp > budget:
            raise ValueError("Cumulative complement policy overspent its shared FP budget")
        result[f"L{level}"] = {"budget": budget, "thresholds": cuts, "fp": fp,
            "tp": int(np.sum(cumulative & (y == 1))),
            "recall": float(np.sum(cumulative & (y == 1)) / np.sum(y == 1))}
    return result


def settings(base, overrides, seed, threads):
    supported = {f.name for f in fields(train.TrainConfig)}
    return train.TrainConfig(**{k: v for k, v in {
        **base, **overrides, "seed": seed, "num_threads": threads,
        "device": "cpu", "n_folds": 0, "learner": "azoth",
    }.items() if k in supported})


def prepare(args):
    root = args.output
    if (root / "prepared.json").exists():
        return json.loads((root / "prepared.json").read_text())
    if any(root.glob("layouts/*/ready.json")):
        raise ValueError("Incomplete snapshot preparation; use a fresh output directory")
    original = root / "original"
    original.mkdir(exist_ok=True)
    for name in ("training_config.json", "feature_spec.json", "training_provenance.json"):
        shutil.copy2(args.source / name, original / name)
    shutil.copytree(args.source / "models", original / "models")
    cache_identity.require_reserved_dev(original)
    recipe = json.loads((original / "training_config.json").read_text())
    env = {k: v for k, v in recipe["feature_env"].items()
           if not any(s in k for s in ("SHARED_VOCAB", "MEM_", "ENSEMBLE_SEEDS", "FEATURE_SPEC"))}
    env["COLLIMATOR_NUM_THREADS"] = str(args.threads)
    env["COLLIMATOR_ALLOWED_FEATURES_FILE"] = ""
    with frozen_corpus(args.db) as snapshot:
        metadata, selected = {}, {"train": [], "dev": []}
        with data._connect(args.db, repeatable_read=True) as conn:
            # Restrict metadata as well as reports to train/dev at the SQL boundary.
            rows = conn.execute("SELECT id, label, COALESCE(canonical_sha256,sha256), score "
                "FROM samples WHERE " + data.LABELED_WHERE + " AND file_type='vsix' "
                "AND get_byte(decode(right(COALESCE(canonical_sha256,sha256),2),'hex'),0)>=32 ORDER BY id")
            for rid, label, canonical, score in rows:
                partition = data.partition_of(canonical)
                if partition not in selected:
                    raise ValueError("Unexpected partition")
                selected[partition].append((int(rid), int(label == "bad")))
                metadata[int(rid)] = (study.split_bucket(canonical), "vsix")
        study.write_json(root / "cohort.json", {"rows": selected, "metadata": metadata, "snapshot": snapshot})
        layouts = {
            "deployed": (env, original / "feature_spec.json"),
            "iso": (json.loads(Path("out/experiments/azoth/runs/919a3f6748ae3bc2.json").read_text())["feature_env"],
                    Path("out/experiments/azoth/runs/919a3f6748ae3bc2_feature_spec.json")),
            "rich": ({**env, "COLLIMATOR_BIGRAM_MIN_FREQ": "5", "COLLIMATOR_KEYWORD_MIN_FREQ": "3",
                      "COLLIMATOR_FULL_RULE_KEYWORDS": "1", "COLLIMATOR_CONTEXT_KEYWORDS": "1",
                      "COLLIMATOR_ARCHIVE_MEMBER_CONTEXT": "1", "COLLIMATOR_KV_SHAPE_FEATURES": "1",
                      "COLLIMATOR_SEVERITY_FRACTION_FEATURES": "1"}, None),
        }
        manifests = {}
        for name, (layout_env, source_spec) in layouts.items():
            dest = root / "layouts" / name
            dest.mkdir(parents=True)
            LOG.info("Preparing %s: %d train and %d dev rows", name, len(selected["train"]), len(selected["dev"]))
            with _temporary_feature_env(layout_env):
                spec = features.FeatureSpec.load(source_spec) if source_spec else features.build_vocab_from_db(
                    args.db, selected["train"], n_workers=args.workers, checkpoint_dir=dest / "vocab")
                spec.bind_metric_contract()
                spec.save(dest / "feature_spec.json")
                identity = {}
                xt, yt, xd, yd = features.extract_partitioned_from_db(args.db, selected["train"], selected["dev"],
                    spec, n_workers=args.workers, identity=identity)
            for partition, matrix, y, ids in (("train", xt, yt, identity["train_row_ids"]),
                                             ("dev", xd, yd, identity["test_row_ids"])):
                np.testing.assert_array_equal(ids, [r[0] for r in selected[partition]])
                np.testing.assert_array_equal(y, [r[1] for r in selected[partition]])
                study.save_matrix(dest, partition, matrix, y, ids, metadata)
            manifests[name] = {"feature_env": layout_env, "evaluation_revision": identity["evaluation_revision"],
                               "spec_sha256": digest(dest / "feature_spec.json"), "features": spec.total_features}
            if name == "rich":
                manifests[name]["base_evaluation_revision"] = manifests["deployed"]["evaluation_revision"]
            study.write_json(dest / "ready.json", manifests[name])
        # Member-context enrichment intentionally changes the captured-input
        # revision; the common MVCC view still fixes its underlying reports.
        if manifests["deployed"]["evaluation_revision"] != manifests["iso"]["evaluation_revision"]:
            raise ValueError("Feature layouts did not capture identical input reports")
    payload = {"layouts": manifests, "base": recipe["train_config"], "seeds": list(SEEDS),
               "cohort_sha256": digest(root / "cohort.json"), "grid": GRID,
               "selection": "Mean grouped training-fold L25 recall, constrained to retain baseline mean L0 recall; L0 then worst-fold L25 break ties.",
               "limitations": "CV conditional on frozen training vocabularies. Dev reused confirmation. Locked test untouched."}
    study.write_json(root / "prepared.json", payload)
    return payload


def ablations(args, prepared):
    """Prune frozen columns with the extractor's compatible spec operation."""
    reference = args.output / "layouts" / "deployed"
    xt, yt, bt, ft, ids = tune.load(reference, "train")
    xd, yd, bd, fd, dids = tune.load(reference, "dev")
    metadata = {int(i): (float(b), str(f)) for ii, bb, ff in ((ids, bt, ft), (dids, bd, fd))
                for i, b, f in zip(ii, bb, ff)}
    spec = features.FeatureSpec.load(reference / "feature_spec.json")
    for name, dropped in ABLATIONS.items():
        dest = args.output / "layouts" / name
        if not (dest / "ready.json").exists():
            dest.mkdir(parents=True, exist_ok=True)
            train_x, pruned = features.drop_feature_prefixes(xt, spec, dropped)
            dev_x, _ = features.drop_feature_prefixes(xd, spec, dropped)
            pruned.save(dest / "feature_spec.json")
            study.save_matrix(dest, "train", train_x, yt, ids, metadata)
            study.save_matrix(dest, "dev", dev_x, yd, dids, metadata)
            study.write_json(dest / "ready.json", {
                **prepared["layouts"]["deployed"], "features": pruned.total_features,
                "spec_sha256": digest(dest / "feature_spec.json"), "dropped_prefixes": dropped})
        prepared["layouts"][name] = json.loads((dest / "ready.json").read_text())
    if "keywords_rich" in prepared["layouts"]:
        name = "keywords_rich_mi3000"
        dest = args.output / "layouts" / name
        source = args.output / "layouts/keywords_rich"
        dest.mkdir(parents=True, exist_ok=True)
        for item in ("train", "dev", "feature_spec.json"):
            if not (dest / item).exists():
                (dest / item).symlink_to((source / item).resolve())
        manifest = {**prepared["layouts"]["keywords_rich"], "feature_env": {
            **prepared["layouts"]["keywords_rich"]["feature_env"],
            "COLLIMATOR_KEYWORD_SELECTION": "balanced_mi", "COLLIMATOR_KEYWORD_VOCAB_MAX": "3000"}}
        study.write_json(dest / "ready.json", manifest)
        prepared["layouts"][name] = manifest
    for cap in (1000, 3000):
        name = f"mi{cap}"
        dest = args.output / "layouts" / name
        dest.mkdir(parents=True, exist_ok=True)
        for item in ("train", "dev", "feature_spec.json"):
            if not (dest / item).exists():
                (dest / item).symlink_to((reference / item).resolve())
        manifest = {**prepared["layouts"]["deployed"], "feature_env": {
            **prepared["layouts"]["deployed"]["feature_env"],
            "COLLIMATOR_KEYWORD_SELECTION": "balanced_mi", "COLLIMATOR_KEYWORD_VOCAB_MAX": str(cap)},
            "scope": "Fit-only supervised selection within the frozen deployed keyword candidates"}
        study.write_json(dest / "ready.json", manifest)
        prepared["layouts"][name] = manifest
    for name, prefix in (("no_archive_timing", "metrics:archive_timing"),
                         ("no_archive_metrics", "metrics:archive_")):
        dest = args.output / "layouts" / name
        if not (dest / "ready.json").exists():
            dest.mkdir(parents=True, exist_ok=True)
            keep = [i for i, feature in enumerate(spec.feature_names) if not feature.startswith(prefix)]
            pruned = replace(spec, feature_names=[spec.feature_names[i] for i in keep], total_features=len(keep),
                             feature_means=None, feature_stds=None)
            pruned.save(dest / "feature_spec.json")
            study.save_matrix(dest, "train", xt[:, keep].tocsr(), yt, ids, metadata)
            study.save_matrix(dest, "dev", xd[:, keep].tocsr(), yd, dids, metadata)
            study.write_json(dest / "ready.json", {**prepared["layouts"]["deployed"],
                "features": pruned.total_features, "spec_sha256": digest(dest / "feature_spec.json"),
                "dropped_feature_prefix": prefix})
        prepared["layouts"][name] = json.loads((dest / "ready.json").read_text())
    study.write_json(args.output / "prepared.json", prepared)


def existing_layouts(args):
    root = args.output
    required = ["deployed", "iso", "depth2", "depth4", "depth5"]
    if not args.features_only:
        required.append("keywords_rich")
    layouts = {name: json.loads((root / "layouts" / name / "ready.json").read_text()) for name in required}
    revision = layouts["deployed"]["evaluation_revision"]
    if any(layouts[n]["evaluation_revision"] != revision for n in required if n != "keywords_rich"):
        raise ValueError("Existing layouts differ in raw report inputs")
    if "keywords_rich" in layouts and layouts["keywords_rich"]["base_evaluation_revision"] != revision:
        raise ValueError("Enriched keyword layout differs in base report inputs")
    prepared = {"layouts": layouts, "base": json.loads((root / "original/training_config.json").read_text())["train_config"],
        "seeds": list(SEEDS), "grid": GRID, "cohort_sha256": digest(root / "cohort.json"),
        "selection": "Mean grouped training-fold L25 recall, constrained to retain baseline mean L0 recall; L0 then worst-fold L25 break ties.",
        "limitations": "CV conditional on frozen training vocabularies. Dev reused confirmation. Locked test untouched.",
        "preparation": "Frozen base/depth matrices plus parallel keyword discovery; the original context-plus-ngram discovery was stopped for excessive redundant member reads."}
    return prepared


def cv(args, name, layout, changes, prepared):
    root = args.output
    target = root / "cv" / name
    target.mkdir(parents=True, exist_ok=True)
    config = {**prepared["base"], **changes}
    contract = {"layout": prepared["layouts"][layout], "config": config,
                "cohort": prepared["cohort_sha256"], "seeds": list(SEEDS)}
    contract_path = target / "contract.json"
    if contract_path.exists() and json.loads(contract_path.read_text()) != contract:
        raise ValueError("Changed partial CV contract; use a new output directory")
    study.write_json(contract_path, contract)
    marker = target / "result.json"
    if marker.exists():
        result = json.loads(marker.read_text())
        if result["contract"] != contract:
            raise ValueError("Changed CV contract; use a new output directory")
        return result
    xt, y, buckets, ft, ids = tune.load(root / "layouts" / layout, "train")
    spec = features.FeatureSpec.load(root / "layouts" / layout / "feature_spec.json")
    assignment = np.minimum((buckets * 3).astype(int), 2)
    oof, metrics, members = np.empty(len(y), dtype=np.float32), [], []
    for fold in range(3):
        fitting, validation = assignment != fold, assignment == fold
        probabilities = []
        seed_metrics = []
        for seed in SEEDS:
            dest = target / f"fold{fold}-seed{seed}.npz"
            if dest.exists():
                saved = np.load(dest)
                np.testing.assert_array_equal(saved["ids"], ids[validation])
                p = saved["probability"]
            else:
                LOG.info("CV %s fold=%s seed=%s", name, fold, seed)
                cfg = settings(prepared["base"], changes, seed, args.threads)
                with _temporary_feature_env(prepared["layouts"][layout].get("feature_env", {})):
                    fit = train.train(xt[fitting], y[fitting], cfg, feature_names=spec.feature_names, sample_file_types=ft[fitting])
                p = study.predict(fit.model.booster_, xt[validation], args.threads)[2]
                np.savez(dest, probability=p, ids=ids[validation])
            probabilities.append(p)
            seed_metrics.append(exact_metrics(y[validation], p))
        mean = study.ensemble_probability(probabilities)
        oof[validation] = mean
        metrics.append(exact_metrics(y[validation], mean))
        members.append(seed_metrics)
    result = {"name": name, "layout": layout, "changes": changes, "contract": contract,
              "fold_metrics": metrics, "per_seed": members, "oof": exact_metrics(y, oof)}
    result["rank"] = rank(result)
    np.savez(target / "oof.npz", probability=oof, ids=ids, labels=y)
    study.write_json(marker, result)
    LOG.info("Completed %s: mean L25/L0 %.4f/%.4f", name, *result["rank"][:2])
    return result


def confirm(args, winner, prepared):
    root = args.output
    dest = root / "candidate"
    dest.mkdir(exist_ok=True)
    layout = root / "layouts" / winner["layout"]
    xt, yt, _, ft, _ = tune.load(layout, "train")
    xd, yd, groups, _, ids = tune.load(layout, "dev")
    spec = features.FeatureSpec.load(layout / "feature_spec.json")
    spec.save(dest / "feature_spec.json")
    probabilities, seed_records = [], []
    (dest / "models").mkdir(exist_ok=True)
    for seed in SEEDS:
        cfg = settings(prepared["base"], winner["changes"], seed, args.threads)
        path = dest / "models" / f"seed_{seed}.txt"
        LOG.info("Full training: seed=%d", seed)
        with _temporary_feature_env(prepared["layouts"][winner["layout"]].get("feature_env", {})):
            fit = train.train(xt, yt, cfg, feature_names=spec.feature_names, sample_file_types=ft)
        export.save_model(fit.model, path)
        native = study.predict(fit.model.booster_, xd, args.threads)[2]
        opts = ort.SessionOptions()
        opts.intra_op_num_threads, opts.inter_op_num_threads = args.threads, 1
        session = ort.InferenceSession(str(path.with_suffix(".onnx")), opts, providers=["CPUExecutionProvider"])
        actual = np.concatenate([session.run(["probabilities"], {session.get_inputs()[0].name: xd[i:i+128].toarray().astype(np.float32)})[0][:, 1]
                                 for i in range(0, len(yd), 128)])
        error = float(np.max(np.abs(native - actual)))
        if error > 1e-4:
            raise ValueError(f"ONNX parity failure: {error}")
        probabilities.append(actual)
        seed_records.append({"seed": seed, "onnx_max_error": error, "dev": exact_metrics(yd, actual),
                             "config": asdict(cfg), "train_metrics": fit.metrics, "split_summary": fit.split_summary,
                             "keyword_selection": fit.keyword_selection})
        gains, splits = fit.model.booster_.feature_importance("gain"), fit.model.booster_.feature_importance("split")
        study.write_json(dest / f"feature-usage-seed{seed}.json", {
            "used_keyword_columns": sum(int(splits[i] > 0) for i, name in enumerate(spec.feature_names)
                                        if name.startswith(("ruleword:", "descword:", "fullword:", "contextword:"))),
            "top_features": [{"feature": spec.feature_names[i], "gain": float(gains[i]), "splits": int(splits[i])}
                             for i in np.argsort(-gains)[:60] if gains[i] > 0]})
    candidate = study.ensemble_probability(probabilities)
    # Runtime-only installed models provide the actual current baseline.
    base_x = tune.load(root / "layouts" / "deployed", "dev")[0]
    baseline = []
    for path in sorted((root / "original" / "models").glob("*.onnx")):
        opts = ort.SessionOptions()
        opts.intra_op_num_threads, opts.inter_op_num_threads = args.threads, 1
        session = ort.InferenceSession(str(path), opts, providers=["CPUExecutionProvider"])
        baseline.append(np.concatenate([session.run(["probabilities"], {session.get_inputs()[0].name: base_x[i:i+128].toarray().astype(np.float32)})[0][:, 1]
                                        for i in range(0, len(yd), 128)]))
    if not baseline:
        raise ValueError("No deployed baseline ONNX members")
    baseline = study.ensemble_probability(baseline)
    cm, bm = exact_metrics(yd, candidate), exact_metrics(yd, baseline)
    accepted = all(cm[level]["recall"] >= bm[level]["recall"] for level in ("L0", "L25"))
    np.savez(dest / "dev_predictions.npz", probability=candidate, baseline=baseline, labels=yd, ids=ids)
    recipe_env = {k: v for k, v in prepared["layouts"][winner["layout"]]["feature_env"].items()
                  if not any(s in k for s in ("SHARED_VOCAB", "MEM_", "ENSEMBLE_SEEDS", "FEATURE_SPEC"))}
    recipe_env.update({"COLLIMATOR_FEATURE_SPEC_FILE": str((dest / "feature_spec.json").resolve()),
                       "COLLIMATOR_FEATURE_SPEC_SHA256": digest(dest / "feature_spec.json")})
    recipe = {"schema": "azoth.model_config.v1", "route": "filetypes/vsix", "ensemble_seeds": list(SEEDS),
              "train_config": seed_records[0]["config"], "feature_env": recipe_env,
              "min_malware_training_score": 0, "provenance": {"study": str(root), "winner": winner["name"]}}
    study.write_json(dest / "training_config.json", recipe)
    study.write_json(dest / "benchmark.json", {"kind": "filetype", "name": "vsix", "file_types": ["vsix"],
        "output_dir": str(dest), "train_rows": len(yt), "train_malware": int(yt.sum()), "train_benign": int((yt == 0).sum()),
        "n_features": spec.total_features, "n_seed_models": len(SEEDS), "training_partitions": ["train"],
        "score_space": "raw", "feature_spec_policy": "research_selected", "feature_mask": None,
        "min_malware_training_score": 0, "train_config": recipe["train_config"], "feature_env": recipe["feature_env"],
        "train_metrics": seed_records[0]["train_metrics"], "split_summary": seed_records[0]["split_summary"],
        "seed_health": {"target_members": len(SEEDS), "accepted_seeds": list(SEEDS), "attempts": seed_records},
        "levels": [], "metrics": {"skipped": "locked test reserved"}})
    cache_identity.write_training_provenance(dest)
    report = {"winner": winner["name"], "baseline": bm, "candidate": cm, "seeds": seed_records,
              "dev_nonregression": accepted, "status": "Research candidate; routed calibration and deployment gates pending",
              "paired_confirmation": confirmation_details(yd, baseline, candidate, groups, ids, bm, cm),
              "retained_baseline_complement": complement_metrics(yd, baseline, candidate),
              "limitations": prepared["limitations"]}
    study.write_json(root / "confirmation.json", report)
    LOG.info("Confirmation: %s", {k: report[k] for k in ("winner", "baseline", "candidate", "dev_nonregression")})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    parser.add_argument("--source", type=Path, default=Path("../azoth/filetypes/vsix"))
    parser.add_argument("--output", type=Path, default=Path("out/experiments/vsix-recall-20261104"))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--numeric-only", action="store_true", help="Fit numerical trials while additional feature extraction runs")
    parser.add_argument("--use-existing-layouts", action="store_true")
    parser.add_argument("--features-only", action="store_true", help="Screen ready feature layouts without accessing development predictions")
    args = parser.parse_args()
    if min(args.workers, args.threads, args.jobs) < 1:
        parser.error("workers, threads, and jobs must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if args.numeric_only:
        prepared = {"base": json.loads((args.output / "original/training_config.json").read_text())["train_config"],
            "layouts": {"deployed": json.loads((args.output / "layouts/deployed/ready.json").read_text())},
            "cohort_sha256": digest(args.output / "cohort.json"), "selection": "Numerical stage only"}
    elif args.use_existing_layouts:
        prepared = existing_layouts(args)
        ablations(args, prepared)
    else:
        prepared = prepare(args)
        ablations(args, prepared)
        for name in ("depth2", "depth4", "depth5"):
            path = args.output / "layouts" / name / "ready.json"
            if path.exists():
                prepared["layouts"][name] = json.loads(path.read_text())
    plan = {"grid": GRID, "ablations": ABLATIONS, "seeds": list(SEEDS),
            "selection": prepared["selection"], "cohort_sha256": prepared["cohort_sha256"]}
    plan_path = args.output / "search-plan.json"
    if not (args.numeric_only or args.features_only) and plan_path.exists() and json.loads(plan_path.read_text()) != plan:
        raise ValueError("Search plan changed; use a new output directory")
    if not (args.numeric_only or args.features_only):
        study.write_json(plan_path, plan)
    comparisons = []
    with ProcessPoolExecutor(max_workers=args.jobs, mp_context=mp.get_context("spawn")) as pool:
        pending = [pool.submit(cv, args, name, "deployed",
            change if name == "replay" else {"holdout_fraction": 0., "early_stopping_rounds": 0, **change}, prepared)
            for name, change in GRID.items()]
        for future in pending:
            comparisons.append(future.result())
            study.write_json(args.output / ("numeric-selection.json" if args.numeric_only else "selection.json"), {"comparisons": comparisons})
    if args.numeric_only:
        return
    numeric = choose(comparisons)
    feature_trials = ("iso", *(n for n in ("rich", "keywords_rich", "keywords_rich_mi3000") if n in prepared["layouts"]),
                      *ABLATIONS, "mi1000", "mi3000", "no_archive_timing", "no_archive_metrics",
                      *(n for n in ("depth2", "depth4", "depth5") if n in prepared["layouts"]))
    with ProcessPoolExecutor(max_workers=args.jobs, mp_context=mp.get_context("spawn")) as pool:
        pending = [pool.submit(cv, args, layout, layout, numeric["changes"], prepared) for layout in feature_trials]
        for future in pending:
            comparisons.append(future.result())
            study.write_json(args.output / "selection.json", {"comparisons": comparisons})
    # Feature/learner interactions: keep the stronger zero-FP numerical recipe
    # in play, rather than assuming one tree shape wins for every vocabulary.
    ranked_features = sorted((r for r in comparisons if r["layout"] != "deployed" and r["layout"] != "no_kv"), key=rank, reverse=True)
    interaction_layouts = list(dict.fromkeys([
        *(r["layout"] for r in ranked_features[:2]),
        *(n for n in ("depth2", "keywords_rich") if n in prepared["layouts"])]))
    changes = {"holdout_fraction": 0., "early_stopping_rounds": 0, **GRID["budget400"]}
    with ProcessPoolExecutor(max_workers=args.jobs, mp_context=mp.get_context("spawn")) as pool:
        pending = [pool.submit(cv, args, layout + "_budget400", layout, changes, prepared) for layout in interaction_layouts]
        for future in pending:
            comparisons.append(future.result())
            study.write_json(args.output / "selection.json", {"comparisons": comparisons})
    if args.features_only:
        return
    winner = choose(comparisons)
    study.write_json(args.output / "winner.json", winner)
    control_l25 = rank(comparisons[0])[0]
    strict = max((r for r in comparisons if rank(r)[0] >= control_l25),
                 key=lambda r: (rank(r)[1], rank(r)[0], rank(r)[2]))
    study.write_json(args.output / "winner-l0.json", strict)
    confirm(args, winner, prepared)
    if strict["name"] != winner["name"]:
        alternative = args.output / "l0-alternative"
        alternative.mkdir(exist_ok=True)
        for item in ("layouts", "original"):
            if not (alternative / item).exists():
                (alternative / item).symlink_to((args.output / item).resolve(), target_is_directory=True)
        confirm(SimpleNamespace(output=alternative, threads=args.threads, source=args.source), strict, prepared)


if __name__ == "__main__":
    main()
