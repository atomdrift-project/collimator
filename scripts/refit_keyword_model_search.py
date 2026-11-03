#!/usr/bin/env python3
"""Refit fixed dev-selected recipes on full training data, without new tuning."""
import argparse
from dataclasses import fields
import hashlib
import json
import logging
from pathlib import Path

import numpy as np

import keyword_model_search as search
from confirm_keyword_model_search import choose, freeze_candidate
from confirm_regression_recovery import confirm
from collimator import bundle, cache_identity, data, features, train
from collimator.corpus_snapshot import frozen_corpus
import azoth_specialist_suite as suite
from tune_regressed_models import freeze


def refit(args, route):
    directory, result, _ = choose(args.root, args.image_root, route)
    manifest = json.loads((directory / "inputs.json").read_text())
    original = json.loads((directory / "accepted_config.json").read_text())
    spec_path = (directory / "confirmation" / result["name"] / "feature_spec.json").resolve()
    root = args.output / route
    root.mkdir(parents=True, exist_ok=True)
    env = dict(manifest["feature_env"])
    for prefix in search.keywords.SOURCES.values():
        env[f"COLLIMATOR_{prefix}_KEYWORDS"] = "0"
    for source, settings in result["options"].items():
        prefix = search.keywords.SOURCES[source]
        env.update({f"COLLIMATOR_{prefix}_KEYWORDS": "1",
                    f"COLLIMATOR_{prefix}_KEYWORD_SELECTION": settings["method"],
                    f"COLLIMATOR_{prefix}_KEYWORD_VOCAB_MAX": str(settings["cap"]),
                    f"COLLIMATOR_{prefix}_KEYWORD_MIN_FREQ": str(settings["floor"])})
    env.update(COLLIMATOR_FEATURE_SPEC_FILE=str(spec_path),
               COLLIMATOR_FEATURE_SPEC_SHA256=hashlib.sha256(spec_path.read_bytes()).hexdigest(),
               COLLIMATOR_NUM_THREADS="4", COLLIMATOR_MIN_SAMPLE_SCORE="0")
    plan = dict(route=route, selected_model=result["name"], study=str(directory),
        options=result["options"], train_config=result["train_config"], feature_env=env,
        seeds=result["seeds"], code_revisions=search.research.revisions(),
        reason="Remove the predeclared research training cap. No test-guided hyperparameter or vocabulary changes.")
    freeze(root / "plan.json", plan)
    candidate = root / "candidate"
    complete = root / "complete.json"
    if not complete.exists():
        with frozen_corpus(args.db) as snapshot:
            max_id = data.snapshot_max_id(args.db)
            config = dict(result["train_config"], seed=result["seeds"][0], num_threads=4)
            allowed = {f.name for f in fields(train.TrainConfig)}
            assert set(config) <= allowed
            summary = suite._train_one(db_path=args.db, name=route, kind="filetype",
                file_types=tuple(data.expand_filetype_aliases((route,))), output_dir=candidate,
                general_spec_path=spec_path, general_spec=features.FeatureSpec.load(spec_path),
                mask_spec_path=None, feature_env=env, config=train.TrainConfig(**config),
                workers=args.workers, max_id=max_id, filegroup_score_filter=False,
                min_malware_score=original["min_malware_training_score"],
                n_seed_extras=len(result["seeds"])-1, requested_seeds=result["seeds"], skip_benchmark=True)
            if summary.get("error"):
                raise ValueError(f"full refit failed: {route}: {summary}")
            rows = suite._fetch_rows(args.db, file_types=tuple(summary["file_types"]),
                max_id=max_id, min_score=None, min_malware_score=original["min_malware_training_score"])
            ids = [rid for rid, _ in suite._ids_labels(rows, test=False)]
        assert plan["code_revisions"] == search.research.revisions()
        cohort = json.loads((directory / "cohort.json").read_text())
        ids += [r["row_id"] for r in cohort["dev"]]
        np.save(root / "training-and-dev-ids.npy", np.array(ids, dtype=np.int64))
        bundle.atomic_write_json(complete, dict(status="full_training_refit", snapshot=snapshot,
            max_id=max_id, train_rows=summary["train_rows"], model_revision=cache_identity.model_revision(candidate),
            spec_revision=hashlib.sha256((candidate / "feature_spec.json").read_bytes()).hexdigest()))
    before = json.loads(complete.read_text())
    assert cache_identity.model_revision(candidate) == before["model_revision"]
    assert hashlib.sha256((candidate / "feature_spec.json").read_bytes()).hexdigest() == before["spec_revision"]
    return candidate, before["max_id"]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--routes", nargs="+", choices=search.ROUTES, default=["c", "png"])
    p.add_argument("--root", type=Path, default=Path("out/experiments/weak-specialist-keywords-20261102"))
    p.add_argument("--image-root", type=Path, default=Path("out/experiments/image-keyword-transfer-20261102"))
    p.add_argument("--output", type=Path, default=Path("out/experiments/weak-specialist-full-refit-20261102"))
    p.add_argument("--deployed", type=Path, default=Path("../azoth"))
    p.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--threads", type=int, default=4)
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    test_root = args.output / "test"
    prepared = []
    for route in args.routes:
        candidate, maximum = refit(args, route)
        # The normal freezer records the same dev-selected recipe before test.
        freezer = argparse.Namespace(**dict(vars(args), output=test_root))
        entry = freeze_candidate(freezer, route)
        entry = dict(entry, candidate=str(candidate.resolve()),
                     exclude_membership_files=[str((args.output/route/'training-and-dev-ids.npy').resolve())])
        prepared.append((entry, maximum))
    results = []
    for entry, maximum in prepared:
        run = argparse.Namespace(**dict(vars(args), output=test_root, max_id=maximum))
        results.append(confirm(run, entry))
        bundle.atomic_write_json(args.output / "status.json", results)


if __name__ == "__main__":
    main()
