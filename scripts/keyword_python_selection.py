#!/usr/bin/env python3
"""Paired Python keyword-selection screen on saved train/dev cohort IDs.

Re-extract once under a fresh read-only snapshot. Rank on the intersection of
both seeds' actual fitting rows, excluding their internal holdouts and all dev
rows. Keep the historical base feature spec fixed. No production config edits.
"""
import argparse
from collections import Counter
from dataclasses import replace
import gzip
import hashlib
import json
from pathlib import Path
import os
import sys
import time

import numpy as np
import scipy.sparse as sp
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from collimator import data, features, train
from collimator.bundle import atomic_write_json
from collimator.corpus_snapshot import frozen_corpus
from collimator.experiment import recall_at_per_100M
from collimator.model import predict_proba
from keyword_route_controls import matrix_digest

SOURCES = ("ruletextword", "contextword")
SEEDS = (43, 44)


def selection_rows(labels, seeds=SEEDS, holdout_fraction=.12):
    """One shared vocabulary, with neither seed's holdout leaking into it."""
    rows = set(range(len(labels)))
    for seed in seeds:
        fitting, _ = train_test_split(np.arange(len(labels)), test_size=holdout_fraction,
                                     stratify=labels, random_state=seed)
        rows.intersection_update(fitting.tolist())
    return np.array(sorted(rows), dtype=np.int64)


def balanced_information(malware, benign, n_malware, n_benign):
    """Smoothed binary mutual information under equal class priors (nats).

    Uses both presence and absence, is symmetric between classes, and rewards
    prevalence differences rather than infinite lift from tiny denominators.
    """
    pm = (np.asarray(malware, dtype=float) + .5) / (n_malware + 1)
    pb = (np.asarray(benign, dtype=float) + .5) / (n_benign + 1)
    mean = (pm + pb) / 2
    return .5 * (pm * np.log(pm / mean) + (1-pm) * np.log((1-pm)/(1-mean))
                 + pb * np.log(pb / mean) + (1-pb) * np.log((1-pb)/(1-mean)))


def rank_words(words, malware, benign, totals, method, min_freq=5):
    support = malware + benign
    score = support if method == "frequency" else balanced_information(
        malware, benign, totals[1], totals[0])
    if method not in {"frequency", "balanced_mi"}:
        raise ValueError(method)
    eligible = np.flatnonzero(support >= min_freq)
    # Stable lexical ties; preserve lexical column ordering after selection.
    return sorted(eligible, key=lambda i: (-float(score[i]), words[i]))


def extract_batch(args):
    db, rows, spec_path, directory, index = args
    spec = features.FeatureSpec.load(Path(spec_path))
    ids = [row["row_id"] for row in rows]
    fetched = data.fetch_cleave_results(db, ids, evaluation_labels={r["row_id"]: r["label"] for r in rows})
    if set(fetched) != set(ids):
        raise ValueError("missing saved cohort reports")
    items, token_rows, digests = [], [], []
    for row in rows:
        item = fetched[row["row_id"]]
        report = features._coerce_report(item["cleave_result"])
        if report is None:
            raise ValueError(f"invalid report: {row['row_id']}")
        items.append((item, row["label"]))
        token_rows.append({source: sorted(words) for source, words in
                           features._report_keywords(features.report_files(report), SOURCES).items()})
        digests.append(item["evaluation_digest"].hex())
    rr, cc, vv, yy = features._extract_batch_worker((0, items, spec))
    if yy != [r["label"] for r in rows]:
        raise ValueError("extraction changed label order")
    matrix = sp.csr_matrix((np.asarray(vv, dtype=np.float32), (rr, cc)),
                           shape=(len(rows), spec.total_features))
    stem = Path(directory) / f"batch-{index:05d}"
    sp.save_npz(str(stem) + ".npz", matrix)
    with gzip.open(str(stem) + ".json.gz", "wt") as stream:
        json.dump(token_rows, stream)
    return str(stem), digests


def token_batches(stems):
    for stem in stems:
        with gzip.open(stem + ".json.gz", "rt") as stream:
            yield from json.load(stream)


def prepare(args, original, cohort, spec):
    cache = args.output / "inputs"
    cache.mkdir()
    rows = cohort["train"] + cohort["test"]
    ids = [r["row_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate or overlapping train/dev IDs")
    train_groups = {r["group_id"] for r in cohort["train"]}
    if train_groups & {r["group_id"] for r in cohort["test"]}:
        raise ValueError("train/dev canonical-group overlap")
    y_train = np.array([r["label"] for r in cohort["train"]], dtype=np.int8)
    y_dev = np.array([r["label"] for r in cohort["test"]], dtype=np.int8)
    selected = selection_rows(y_train, holdout_fraction=original["train_config"].get("holdout_fraction", .12))
    selection_mask = np.zeros(len(rows), dtype=bool)
    selection_mask[selected] = True
    counters = {source: [Counter(), Counter()] for source in SOURCES}
    tasks = [(args.db, rows[start:start+256], str(args.output / "base_spec.json"), str(cache), i)
             for i, start in enumerate(range(0, len(rows), 256))]
    stems, digests = [], []
    started = time.perf_counter()
    previous = None
    if args.reuse_inputs:
        previous = json.loads((args.reuse_inputs / "inputs.json").read_text())
        if previous["feature_env"] != original["feature_env"]:
            raise ValueError("cached extraction settings differ")
        if previous["source_sha256"]["features"] != hashlib.sha256(Path(features.__file__).read_bytes()).hexdigest():
            raise ValueError("cached extractor revision differs")
        old_cache = args.reuse_inputs / "inputs"
        with np.load(old_cache / "rows.npz") as old:
            old_ids = old["row_ids"]
            old_labels = np.r_[old["train_labels"], old["dev_labels"]]
            old_n = len(old["train_labels"])
        if set(ids[:len(y_train)]) != set(old_ids[:old_n]) or set(ids[len(y_train):]) != set(old_ids[old_n:]):
            raise ValueError("cached train/dev row membership differs")
        lookup = {int(rid): i for i, rid in enumerate(old_ids)}
        permutation = np.array([lookup[rid] for rid in ids])
        np.testing.assert_array_equal(old_labels[permutation], np.r_[y_train, y_dev])
        base = sp.load_npz(old_cache / "base.npz")
        if matrix_digest(base) != previous["base_sha256"]:
            raise ValueError("cached base matrix changed")
        base = base[permutation]
        old_stems = [str(path)[:-len(".json.gz")] for path in sorted(old_cache.glob("batch-*.json.gz"))]
        tokens = list(token_batches(old_stems))
        if len(tokens) != len(ids):
            raise ValueError("cached keyword rows differ")
        for index, start in enumerate(range(0, len(ids), 256)):
            stem = str(cache / f"batch-{index:05d}")
            with gzip.open(stem + ".json.gz", "wt") as stream:
                json.dump([tokens[i] for i in permutation[start:start+256]], stream)
            stems.append(stem)
        del tokens
        snapshot = previous["snapshot"]
        print(f"Reordered {len(ids)} cached reports to standard training order", flush=True)
    else:
        with frozen_corpus(args.db) as snapshot:
            with features._feature_worker_pool(args.workers) as pool:
                for stem, batch_digests in features._bounded_iter(pool, extract_batch, tasks, max_inflight=2*args.workers):
                    stems.append(stem)
                    digests.extend(batch_digests)
                    if len(stems) % 10 == 0:
                        print(f"Extracted {len(digests)}/{len(rows)} reports ({time.perf_counter()-started:.0f}s)", flush=True)
        matrices = [sp.load_npz(stem + ".npz") for stem in stems]
        base = sp.vstack(matrices, format="csr")
        del matrices
    for i, tokens in enumerate(token_batches(stems)):
        if selection_mask[i]:
            for source in SOURCES:
                counters[source][y_train[i]].update(tokens[source])
    sp.save_npz(cache / "base.npz", base)
    np.savez_compressed(cache / "rows.npz", train_labels=y_train, dev_labels=y_dev,
                        row_ids=np.array(ids, dtype=np.int64), selection_rows=selected)
    totals = [int(np.sum(y_train[selected] == label)) for label in (0, 1)]
    sources = {}
    for source in SOURCES:
        good, bad = counters[source]
        words = sorted(word for word in good.keys() | bad.keys() if good[word] + bad[word] >= 5)
        lookup = {word: i for i, word in enumerate(words)}
        indptr, indices = [0], []
        for tokens in token_batches(stems):
            indices.extend(lookup[word] for word in tokens[source] if word in lookup)
            indptr.append(len(indices))
        matrix = sp.csr_matrix((np.ones(len(indices), dtype=np.float32),
                               np.array(indices, dtype=np.int32), np.array(indptr, dtype=np.int64)),
                              shape=(len(rows), len(words)))
        matrix.sort_indices()
        sp.save_npz(cache / f"{source}.npz", matrix)
        info = dict(words=words, goodware=[good[w] for w in words], malware=[bad[w] for w in words],
                    totals=totals, matrix_sha256=matrix_digest(matrix))
        atomic_write_json(cache / f"{source}.json", info)
        sources[source] = dict(eligible_words=len(words), matrix_sha256=info["matrix_sha256"])
    manifest = dict(scope=__doc__, seeds=list(SEEDS), sources=sources, train_rows=len(y_train),
                    dev_rows=len(y_dev), train_malware=int(y_train.sum()), dev_malware=int(y_dev.sum()),
                    selection_rows=len(selected), selection_class_totals=totals,
                    base_sha256=matrix_digest(base), snapshot=snapshot,
                    report_revision_sha256=(previous["report_revision_sha256"] if previous else
                                            hashlib.sha256(json.dumps(digests).encode()).hexdigest()),
                    reused_extraction=str(args.reuse_inputs) if previous else None,
                    row_order="row_id ascending within train/dev, matching experiment.py",
                    cohort_sha256=hashlib.sha256(json.dumps(cohort, sort_keys=True).encode()).hexdigest(),
                    feature_env=original["feature_env"], train_config=original["train_config"],
                    extraction_seconds=time.perf_counter()-started,
                    source_sha256={name: hashlib.sha256(Path(path).read_bytes()).hexdigest()
                                   for name, path in [("features", features.__file__), ("train", train.__file__),
                                                      ("experiment_script", __file__)]})
    atomic_write_json(args.output / "inputs.json", manifest)
    return manifest


def fit_variant(args, name, spec, x_train, x_dev, y_train, y_dev, original, overrides=None):
    directory = args.output / name
    directory.mkdir(exist_ok=True)
    spec.save(directory / "feature_spec.json")
    config = dict(original["train_config"])
    config.update(learner="azoth", device="cpu", num_threads=4)
    config.update(overrides or {})
    probabilities, members = {}, []
    started = time.perf_counter()
    for seed in SEEDS:
        result = train.train(x_train, y_train, train.TrainConfig(**config, seed=seed),
                             feature_names=spec.feature_names)
        result.model.booster_.save_model(str(directory / f"seed_{seed}.txt"))
        scores = np.asarray(predict_proba(result.model, x_dev), dtype=np.float32)
        probabilities[f"seed_{seed}"] = scores
        metrics = recall_at_per_100M(y_dev, scores)
        members.append(dict(seed=seed, trees=result.model.booster_.num_trees(),
                            recall_at_0fp=metrics["recall_at_0fp"], recall_at_1fp=metrics["recall_at_1fp"]))
    mean = np.mean([p.astype(np.float64) for p in probabilities.values()], axis=0).astype(np.float32)
    metrics = recall_at_per_100M(y_dev, mean)
    np.savez_compressed(directory / "dev_predictions.npz", labels=y_dev, ensemble=mean, **probabilities)
    result = dict(name=name, keywords=sum(map(len, spec.keyword_vocabs.values())), seeds=members,
                  recall_at_0fp=metrics["recall_at_0fp"], recall_at_1fp=metrics["recall_at_1fp"],
                  seconds=time.perf_counter()-started, train_config=config,
                  train_sha256=matrix_digest(x_train), dev_sha256=matrix_digest(x_dev))
    atomic_write_json(directory / "result.json", result)
    print("RESULT " + json.dumps(result), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    parser.add_argument("--study", type=Path, default=Path("out/experiments/keyword-hierarchy-context-10pct-v2/python"))
    parser.add_argument("--output", type=Path, default=Path("out/experiments/keyword-python-selection-10pct"))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--reuse-inputs", type=Path, help="Reuse a completed extraction without another database read")
    args = parser.parse_args()
    if args.output.exists() and not args.resume:
        parser.error("output exists; use --resume for completed cached inputs")
    args.output.mkdir(parents=True, exist_ok=True)
    original = json.loads(next((args.study / "baseline/runs").glob("*-experiment.json")).read_text())
    if original["train_config"]["n_folds"] != 0:
        raise ValueError("this screen requires the no-CV training protocol")
    os.environ.update(original["feature_env"])
    features.feature_config_from_env.cache_clear()
    spec = features.FeatureSpec.load(args.study / "baseline/feature_spec.json")
    if spec.keyword_vocabs or spec.standardized:
        raise ValueError("expected raw baseline spec without keywords")
    spec.save(args.output / "base_spec.json")
    cohort = json.loads((args.study / "selected_cohort.json").read_text())
    for partition in ("train", "test"):
        cohort[partition] = sorted(cohort[partition], key=lambda row: row["row_id"])
    if (args.output / "inputs.json").exists():
        manifest = json.loads((args.output / "inputs.json").read_text())
        if manifest["cohort_sha256"] != hashlib.sha256(json.dumps(cohort, sort_keys=True).encode()).hexdigest():
            raise ValueError("cohort changed")
        if manifest["feature_env"] != original["feature_env"] or manifest["train_config"] != original["train_config"]:
            raise ValueError("experiment settings changed")
        for name, path in (("features", features.__file__), ("train", train.__file__)):
            if manifest["source_sha256"][name] != hashlib.sha256(Path(path).read_bytes()).hexdigest():
                raise ValueError(f"{name} source changed; use a fresh experiment")
    else:
        manifest = prepare(args, original, cohort, spec)
    cache = args.output / "inputs"
    base = sp.load_npz(cache / "base.npz")
    if matrix_digest(base) != manifest["base_sha256"]:
        raise ValueError("base cache changed")
    with np.load(cache / "rows.npz") as arrays:
        y_train, y_dev = arrays["train_labels"], arrays["dev_labels"]
    n = len(y_train)
    summary_path = args.output / "comparison.json"
    summary = (json.loads(summary_path.read_text()) if args.resume and summary_path.exists()
               else dict(inputs=manifest, variants={}))

    def run(name, variant_spec, matrix):
        result_path = args.output / name / "result.json"
        if result_path.exists() and args.resume:
            result = json.loads(result_path.read_text())
            if (result["train_sha256"] != matrix_digest(matrix[:n]) or
                    result["dev_sha256"] != matrix_digest(matrix[n:])):
                raise ValueError("saved fit inputs differ")
        else:
            print(f"Starting {name}", flush=True)
            result = fit_variant(args, name, variant_spec, matrix[:n], matrix[n:], y_train, y_dev, original)
        summary["variants"][name] = result
        atomic_write_json(args.output / "comparison.json", summary)

    run("baseline", spec, base)
    for source in SOURCES:
        info = json.loads((cache / f"{source}.json").read_text())
        keywords = sp.load_npz(cache / f"{source}.npz")
        if matrix_digest(keywords) != info["matrix_sha256"]:
            raise ValueError("keyword cache changed")
        for method in ("frequency", "balanced_mi"):
            ranking = rank_words(info["words"], np.array(info["malware"]), np.array(info["goodware"]),
                                 info["totals"], method)
            for cap in (1000, 5000, 10000):
                columns = sorted(ranking[:cap])
                words = [info["words"][i] for i in columns]
                names = spec.feature_names + [f"{source}:{word}" for word in words]
                variant_spec = replace(spec, version=23, abi_version=23, base_feature_abi=spec.abi_version,
                                       keyword_vocabs={source: words}, feature_names=names, total_features=len(names))
                run(f"{source}-{method}-{cap}", variant_spec, sp.hstack([base, keywords[:, columns]], format="csr"))
    print(f"Finished: {args.output / 'comparison.json'}", flush=True)


if __name__ == "__main__":
    main()
