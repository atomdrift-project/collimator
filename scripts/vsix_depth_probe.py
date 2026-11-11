#!/usr/bin/env python3
"""Isolate trait depth while holding keywords, metrics and n-gram vocabularies fixed."""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
import logging
import os
from pathlib import Path

import numpy as np

import vsix_recall_tuneup as run
from azoth_specialist_suite import _temporary_feature_env
from collimator import data, features
from collimator.corpus_snapshot import SNAPSHOT_ENV, DATABASE_ENV

HISTORICAL = {2: "6de1fec97c53dac3", 4: "266de5af2f3cce0a", 5: "65ac73d4ae42c6fa"}


def depth_spec(base, historical, depth):
    paths = sorted({p for p in (*base.presence_vocab, *historical.presence_vocab)
                    if len(p.split("/")) <= depth})
    names = [prefix + path for prefix in ("present:", "maxcrit:") for path in paths]
    names += [name for name in base.feature_names if not name.startswith(("present:", "maxcrit:"))]
    return replace(base, presence_vocab=paths, feature_names=names, total_features=len(names),
                   trait_path_depth=depth, feature_means=None, feature_stds=None)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path("out/experiments/vsix-recall-20261104"))
    p.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    root = args.root
    cohort = json.loads((root / "cohort.json").read_text())
    metadata = {int(k): tuple(v) for k, v in cohort["metadata"].items()}
    base = features.FeatureSpec.load(root / "layouts/deployed/feature_spec.json")
    ready = json.loads((root / "layouts/deployed/ready.json").read_text())
    env = json.loads((root / "original/training_config.json").read_text())["feature_env"]
    os.environ.update({SNAPSHOT_ENV: cohort["snapshot"], DATABASE_ENV: args.db})
    # Import while the original study is alive, then hold our own export lease.
    with data._connect(args.db, repeatable_read=True) as owner:
        owner.execute("SET TRANSACTION READ ONLY")
        owner.execute("SET LOCAL idle_in_transaction_session_timeout=0")
        os.environ[SNAPSHOT_ENV] = owner.execute("SELECT pg_export_snapshot()").fetchone()[0]
        for depth, key in HISTORICAL.items():
            dest = root / "layouts" / f"depth{depth}"
            if (dest / "ready.json").exists():
                continue
            dest.mkdir(parents=True, exist_ok=True)
            historical = features.FeatureSpec.load(Path("out/experiments/azoth/runs") / f"{key}_feature_spec.json")
            spec = depth_spec(base, historical, depth)
            active = {**env, "COLLIMATOR_TRAIT_PATH_DEPTH": str(depth), "COLLIMATOR_SHARED_VOCAB_DIR": ""}
            identity = {}
            with _temporary_feature_env(active):
                spec.save(dest / "feature_spec.json")
                xt, yt, xd, yd = features.extract_partitioned_from_db(args.db, cohort["rows"]["train"],
                    cohort["rows"]["dev"], spec, n_workers=4, identity=identity)
            for part, x, y, ids in (("train", xt, yt, identity["train_row_ids"]), ("dev", xd, yd, identity["test_row_ids"])):
                np.testing.assert_array_equal(ids, [r[0] for r in cohort["rows"][part]])
                np.testing.assert_array_equal(y, [r[1] for r in cohort["rows"][part]])
                run.study.save_matrix(dest, part, x, y, ids, metadata)
            if identity["evaluation_revision"] != ready["evaluation_revision"]:
                raise ValueError("Depth probe input revisions differ from the control")
            run.study.write_json(dest / "ready.json", {"features": spec.total_features, "feature_env": active,
                "spec_sha256": run.digest(dest / "feature_spec.json"), "evaluation_revision": identity["evaluation_revision"],
                "scope": "Isolated trait-depth probe with historical train-only presence vocabulary; all other vocabularies frozen"})
            logging.info("Depth %s ready: %s features", depth, spec.total_features)


if __name__ == "__main__":
    main()
