#!/usr/bin/env python3
"""Freeze one finalist per specialist, then compare with deployed models on test.

The finalist is selected from development metrics only. Test reports never
participate in vocabulary discovery, fitting, finalist selection, or tuning.
"""
import argparse
import hashlib
import json
import logging
from pathlib import Path
import shutil

import numpy as np

import keyword_model_search as search
from collimator import bundle, data, export, cache_identity
from collimator.corpus_snapshot import frozen_corpus
from confirm_regression_recovery import confirm
from tune_regressed_models import freeze


def choose(root, image_root, route):
    locations = [root / route]
    if (image_root / route / "verified_summary.json").exists():
        locations.append(image_root / route)
    candidates = []
    fallback = None
    reference = None
    for directory in locations:
        if not (directory / "verified_summary.json").exists():
            raise ValueError(f"research verification is incomplete: {directory}")
        with np.load(directory / "inputs/rows.npz") as rows:
            identity = (rows["row_ids"][len(rows["y_train"]):], rows["y_dev"], rows["search"])
        if reference is None:
            reference = identity
        else:
            for old, new in zip(reference, identity, strict=True):
                np.testing.assert_array_equal(old, new)
        results = json.loads((directory / "confirmation.json").read_text())["variants"]
        baseline = results["baseline"]
        if fallback is None:
            fallback = (directory, baseline, baseline)
        for result in results.values():
            if result["name"] == "baseline" or result.get("diagnostic"):
                continue
            current, before = result["confirmation"], baseline["confirmation"]
            if current["recall_1fp"] < before["recall_1fp"] or current["ap"] < before["ap"]-.005:
                continue
            if any(result[f"confirmation_seeds_{a}_{b}"]["recall_1fp"] <
                   baseline[f"confirmation_seeds_{a}_{b}"]["recall_1fp"] for a, b in ((43, 44), (45, 46))):
                continue
            candidates.append((directory, result, baseline))
    return max(candidates, key=lambda item: (item[1]["confirmation"]["recall_1fp"],
        item[1]["confirmation"]["recall_0fp"], item[1]["confirmation"]["ap"])) if candidates else fallback


def freeze_candidate(args, route):
    receipt = args.output / "frozen" / f"{route}.json"
    if receipt.exists():
        return json.loads(receipt.read_text())
    directory, result, baseline = choose(args.root, args.image_root, route)
    manifest = json.loads((directory / "inputs.json").read_text())
    original = json.loads((directory / "accepted_config.json").read_text())
    artifacts = args.output / "artifacts" / route
    current, candidate = artifacts / "current", artifacts / "candidate"
    source = args.deployed / "filetypes" / route
    if not current.exists():
        shutil.copytree(source, current)
    # Standardize legacy single-model layouts for the existing paired evaluator.
    if not (current / "models").exists():
        (current / "models").mkdir()
        for index, path in enumerate(bundle.model_files(source)):
            shutil.copy2(path, current / "models" / f"seed_{index}.onnx")
    training = json.loads((source / "training_config.json").read_text())
    aliases = list(data.expand_filetype_aliases((route,)))
    bundle.atomic_write_json(current / "benchmark.json", dict(training, file_types=aliases))
    (candidate / "models").mkdir(parents=True, exist_ok=True)
    model_root = directory / "confirmation" / result["name"]
    shutil.copy2(model_root / "feature_spec.json", candidate / "feature_spec.json")
    spec = search.research.features.FeatureSpec.load(candidate / "feature_spec.json")
    import lightgbm as lgb
    for seed in result["seeds"]:
        native = model_root / f"seed_{seed}.txt"
        shutil.copy2(native, candidate / "models" / native.name)
        booster = lgb.Booster(model_file=str(native))
        if not export.export_lightgbm_onnx(booster, spec.total_features,
                                          candidate / "models" / f"seed_{seed}.onnx"):
            raise ValueError(f"ONNX export failed: {route}, seed {seed}")
    env = dict(manifest["feature_env"])
    for prefix in search.keywords.SOURCES.values():
        env[f"COLLIMATOR_{prefix}_KEYWORDS"] = "0"
    for word_source, settings in result["options"].items():
        prefix = search.keywords.SOURCES[word_source]
        env.update({f"COLLIMATOR_{prefix}_KEYWORDS": "1",
                    f"COLLIMATOR_{prefix}_KEYWORD_SELECTION": settings["method"],
                    f"COLLIMATOR_{prefix}_KEYWORD_VOCAB_MAX": str(settings["cap"]),
                    f"COLLIMATOR_{prefix}_KEYWORD_MIN_FREQ": str(settings["floor"])})
    pooled = result["variant"].get("pooled", False) and manifest.get("transfer_kind", "image") == "image"
    benchmark = dict(name=route, kind="filetype", file_types=aliases,
        train_config=result["train_config"], feature_env=env,
        min_malware_training_score=result["variant"].get("training_malware_cutoff", original["min_malware_training_score"]),
        seed_health={"accepted_seeds": result["seeds"]},
        training_protocol={"ordinary_train_config_replay_equivalent": not pooled,
                           "image_transfer": pooled, "max_train_groups": manifest.get("max_train_groups"),
                           "training_scope": "Only original training-partition groups; canonical test/dev excluded."})
    bundle.atomic_write_json(candidate / "benchmark.json", benchmark)
    cache_identity.write_training_provenance(candidate)
    cohort = json.loads((directory / "cohort.json").read_text())
    membership = artifacts / "known-training-and-dev-ids.npy"
    np.save(membership, np.array([r["row_id"] for part in ("train", "dev") for r in cohort[part]], dtype=np.int64))
    entry = dict(route=route, current=str(current.resolve()), candidate=str(candidate.resolve()),
        evaluation_file_types=aliases, targets=[route], objective="recall",
        exclude_membership_files=[str(membership.resolve())],
        selection=dict(study=str(directory), name=result["name"], options=result["options"],
                       variant=result["variant"], confirmation=result["confirmation"],
                       matched_baseline=baseline["confirmation"],
                       zero_fp_tradeoff=result["confirmation"]["recall_0fp"] < baseline["confirmation"]["recall_0fp"]))
    receipt.parent.mkdir(parents=True, exist_ok=True)
    freeze(receipt, entry)
    print("FROZEN " + route + " " + result["name"], flush=True)
    return entry


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path("out/experiments/weak-specialist-keywords-20261102"))
    p.add_argument("--image-root", type=Path, default=Path("out/experiments/image-keyword-transfer-20261102"))
    p.add_argument("--output", type=Path, default=Path("out/experiments/weak-specialist-test-20261102"))
    p.add_argument("--routes", nargs="+", choices=search.ROUTES, default=list(search.ROUTES))
    p.add_argument("--deployed", type=Path, default=Path("../azoth"))
    p.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--threads", type=int, default=4)
    p.add_argument("--freeze-only", action="store_true")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    entries = [freeze_candidate(args, route) for route in args.routes]
    if args.freeze_only:
        return
    boundary = args.output / "test_boundary.json"
    if not boundary.exists():
        with frozen_corpus(args.db):
            maximum = data.snapshot_max_id(args.db)
        freeze(boundary, dict(max_id=maximum))
    args.max_id = json.loads(boundary.read_text())["max_id"]
    status = args.output / "status.json"
    results = {r["route"]: r for r in json.loads(status.read_text())} if status.exists() else {}
    for entry in entries:
        results[entry["route"]] = confirm(args, entry)
        bundle.atomic_write_json(status, list(results.values()))


if __name__ == "__main__":
    main()
