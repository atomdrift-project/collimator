#!/usr/bin/env python3
"""Discover richer keywords in parallel, reusing the frozen non-keyword vocabulary."""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import json
import logging
import multiprocessing as mp
import os
from pathlib import Path

import numpy as np

import vsix_recall_tuneup as run
from azoth_specialist_suite import _temporary_feature_env
from collimator import data, features
from collimator.corpus_snapshot import SNAPSHOT_ENV, DATABASE_ENV


def count_batch(task):
    db, rows, env = task
    counts = {source: Counter() for source in ("ruleword", "descword", "fullword", "contextword")}
    with _temporary_feature_env(env):
        for item in data.fetch_cleave_results(db, [int(i) for i, _ in rows]).values():
            report = features._coerce_report(item["cleave_result"])
            if report:
                for source, words in features._report_keywords(features.report_files(report), counts).items():
                    counts[source].update(words)
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("out/experiments/vsix-recall-20261104"))
    parser.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--snapshot-file", type=Path)
    parser.add_argument("--extract-only", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    root = args.root
    cohort = json.loads((root / "cohort.json").read_text())
    metadata = {int(k): tuple(v) for k, v in cohort["metadata"].items()}
    ready = json.loads((root / "layouts/deployed/ready.json").read_text())
    env = {**ready["feature_env"], "COLLIMATOR_FULL_RULE_KEYWORDS": "1", "COLLIMATOR_CONTEXT_KEYWORDS": "1",
           "COLLIMATOR_ARCHIVE_MEMBER_CONTEXT": "1", "COLLIMATOR_KEYWORD_MIN_FREQ": "3"}
    source_snapshot = (json.loads(args.snapshot_file.read_text())["snapshot"] if args.snapshot_file else cohort["snapshot"])
    os.environ.update({SNAPSHOT_ENV: source_snapshot, DATABASE_ENV: args.db})
    with data._connect(args.db, repeatable_read=True) as owner:
        owner.execute("SET TRANSACTION READ ONLY")
        owner.execute("SET LOCAL idle_in_transaction_session_timeout=0")
        snapshot = owner.execute("SELECT pg_export_snapshot()").fetchone()[0]
        os.environ[SNAPSHOT_ENV] = snapshot
        lease = "keyword-extraction-lease.json" if args.extract_only else "keyword-snapshot-lease.json"
        run.study.write_json(root / lease, {"snapshot": snapshot, "source": source_snapshot})
        dest = root / "layouts/keywords_rich"
        dest.mkdir(parents=True, exist_ok=True)
        checkpoint = dest / "keyword-counts.json"
        if args.extract_only and not checkpoint.exists():
            raise ValueError("Keyword counting must complete before extract-only mode")
        if not checkpoint.exists():
            counts = {s: Counter() for s in ("ruleword", "descword", "fullword", "contextword")}
            rows = cohort["rows"]["train"]
            tasks = [(args.db, rows[i:i+100], env) for i in range(0, len(rows), 100)]
            with ProcessPoolExecutor(max_workers=args.workers, mp_context=mp.get_context("spawn")) as pool:
                for index, batch in enumerate(pool.map(count_batch, tasks)):
                    for source, values in batch.items():
                        counts[source].update(values)
                    logging.info("Keyword batches: %d/%d", index + 1, len(tasks))
            run.study.write_json(checkpoint, {k: dict(v) for k, v in counts.items()})
        counts = {k: Counter(v) for k, v in json.loads(checkpoint.read_text()).items()}
        base = features.FeatureSpec.load(root / "layouts/deployed/feature_spec.json")
        prefixes = tuple(k + ":" for k in base.keyword_vocabs)
        names = [n for n in base.feature_names if not n.startswith(prefixes)]
        base = replace(base, feature_names=names, total_features=len(names), keyword_vocabs={})
        with _temporary_feature_env(env):
            spec = features._add_keyword_vocab(base, counts)
            spec.save(dest / "feature_spec.json")
            identity = {}
            xt, yt, xd, yd = features.extract_partitioned_from_db(args.db, cohort["rows"]["train"],
                cohort["rows"]["dev"], spec, n_workers=args.workers, identity=identity)
        for part, x, y, ids in (("train", xt, yt, identity["train_row_ids"]), ("dev", xd, yd, identity["test_row_ids"])):
            np.testing.assert_array_equal(ids, [r[0] for r in cohort["rows"][part]])
            np.testing.assert_array_equal(y, [r[1] for r in cohort["rows"][part]])
            run.study.save_matrix(dest, part, x, y, ids, metadata)
        run.study.write_json(dest / "ready.json", {"feature_env": env, "features": spec.total_features,
            "spec_sha256": run.digest(dest / "feature_spec.json"), "evaluation_revision": identity["evaluation_revision"],
            "base_evaluation_revision": ready["evaluation_revision"],
            "scope": "Full-path and context keywords; all non-keyword vocabularies held fixed. Context enriches the evaluation revision under the same MVCC view."})


if __name__ == "__main__":
    main()
