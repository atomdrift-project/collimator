#!/usr/bin/env python3
"""Route keyword search with a disjoint development confirmation cohort.

Keep 10% of canonical groups for training and development search; reserve the
remaining development groups for confirmation. Locked-test reports are unused.
Base feature settings follow the accepted route model. Its feature allowlist
applies to base features; keyword candidates are explicitly appended separately.
"""
import argparse
from collections import Counter
from contextlib import contextmanager
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import gzip
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import sys
import time

import numpy as np
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from collimator import features, keywords, train
from collimator.bundle import atomic_write_json
from collimator.model import predict_proba
from keyword_route_controls import matrix_digest

SOURCES = tuple(keywords.SOURCES)
ROOT = Path("out/experiments/keyword-macho-search")


def sampled(group_id, percent=10):
    return int(hashlib.md5(group_id.lower().encode()).hexdigest()[:8], 16) < int(2**32 * percent / 100)


def bound_confirmation(rows, max_groups):
    """Cap only confirmation groups by a separate label-blind deterministic hash."""
    if max_groups < 0:
        raise ValueError("confirmation group cap must be nonnegative")
    if not max_groups:
        return rows
    candidates = {row["group_id"].lower() for row in rows if not sampled(row["group_id"])}
    selected = set(sorted(candidates, key=lambda group: (
        hashlib.sha256(("keyword-confirmation:" + group).encode()).hexdigest(), group))[:max_groups])
    return [row for row in rows if sampled(row["group_id"]) or row["group_id"].lower() in selected]


def exclude_label_conflicts(rows):
    """Remove every member of a canonical group with contradictory labels."""
    labels = {}
    for row in rows:
        labels.setdefault(row["group_id"].lower(), set()).add(row["label"])
    conflicts = {group for group, values in labels.items() if len(values) > 1}
    excluded = [row for row in rows if row["group_id"].lower() in conflicts]
    return [row for row in rows if row["group_id"].lower() not in conflicts], excluded


def revisions():
    from collimator import model
    return {name: hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
            for name, module in (("features", features), ("keywords", keywords), ("train", train), ("model", model))}


def set_environment(env):
    for key in list(os.environ):
        if key.startswith("COLLIMATOR_") and "KEYWORD" in key:
            del os.environ[key]
    os.environ.update(env)
    for prefix in keywords.SOURCES.values():
        os.environ[f"COLLIMATOR_{prefix}_KEYWORDS"] = "0"
    os.environ["COLLIMATOR_NUM_THREADS"] = "4"
    features.feature_config_from_env.cache_clear()
    features.allowed_features.cache_clear()


def extract_batch(args):
    from collimator import data
    db, rows, spec_path, directory, index = args
    spec = features.FeatureSpec.load(Path(spec_path))
    fetched = data.fetch_cleave_results(db, [r["row_id"] for r in rows],
                                      evaluation_labels={r["row_id"]: r["label"] for r in rows})
    if set(fetched) != {r["row_id"] for r in rows}:
        raise ValueError("missing selected reports")
    items, tokens, digests = [], [], []
    for row in rows:
        item = fetched[row["row_id"]]
        report = features._coerce_report(item["cleave_result"])
        if report is None:
            raise ValueError("invalid selected report")
        items.append((item, row["label"]))
        tokens.append({s: sorted(words) for s, words in features._report_keywords(features.report_files(report), SOURCES).items()})
        digests.append(item["evaluation_digest"].hex())
    rr, cc, vv, yy = features._extract_batch_worker((0, items, spec))
    assert yy == [r["label"] for r in rows]
    matrix = sp.csr_matrix((np.asarray(vv, dtype=np.float32), (rr, cc)), shape=(len(rows), spec.total_features))
    stem = Path(directory) / f"batch-{index:05d}"
    sp.save_npz(str(stem) + ".npz", matrix)
    with gzip.open(str(stem) + ".json.gz", "wt") as stream:
        json.dump(tokens, stream)
    return str(stem), digests


def token_rows(directory):
    for path in sorted(directory.glob("batch-*.json.gz")):
        with gzip.open(path, "rt") as stream:
            yield from json.load(stream)


def prepare(args, *, row_selector=None, search_selector=sampled, feature_overrides=None,
            accepted_config=None, keyword_min_support=2):
    from collimator import model_config
    accepted = accepted_config if accepted_config is not None else model_config.load(f"filetypes/{args.route}")
    env = dict(accepted["feature_env"], COLLIMATOR_SAMPLE_PERCENT="100")
    env.update(feature_overrides or {})
    set_environment(env)
    from collimator import data
    from collimator.corpus_snapshot import frozen_corpus
    assert not data.SAMPLE_PREDICATE
    args.output.mkdir(parents=True, exist_ok=False)
    cache = args.output / "inputs"
    cache.mkdir()
    atomic_write_json(args.output / "accepted_config.json", accepted)
    started = time.perf_counter()
    rows_train, rows_dev = [], []
    digests, stems = [], []
    with frozen_corpus(args.db) as snapshot:
        metadata = data.stream_partitioned_metadata_grouped(
            args.db, file_types=(args.route,), min_score=None)
        if row_selector is not None:
            rows_train, rows_dev = row_selector(metadata, accepted)
        else:
            for rid, label, partition, group, score in metadata:
                if partition == "test":
                    continue
                row = dict(row_id=rid, label=label, group_id=group, score=score)
                if partition == "train":
                    if sampled(group) and score >= int(env["COLLIMATOR_MIN_SAMPLE_SCORE"]) and (
                            not label or score >= accepted["min_malware_training_score"]):
                        rows_train.append(row)
                elif partition == "dev":
                    rows_dev.append(row)
        if args.exclude_label_conflicts:
            rows_train, excluded_train = exclude_label_conflicts(rows_train)
            rows_dev, excluded_dev = exclude_label_conflicts(rows_dev)
            atomic_write_json(args.output / "excluded_label_conflicts.json",
                              dict(train=excluded_train, dev=excluded_dev))
        rows_dev = bound_confirmation(rows_dev, args.confirmation_groups)
        rows_train.sort(key=lambda row: row["row_id"])
        rows_dev.sort(key=lambda row: row["row_id"])
        assert not {r["group_id"] for r in rows_train} & {r["group_id"] for r in rows_dev}
        search = np.array([search_selector(r["group_id"]) for r in rows_dev])
        assert not {r["group_id"] for r, flag in zip(rows_dev, search) if flag} & {
            r["group_id"] for r, flag in zip(rows_dev, search) if not flag}
        y_train = np.array([r["label"] for r in rows_train], dtype=np.int8)
        y_dev = np.array([r["label"] for r in rows_dev], dtype=np.int8)
        assert set(y_train) == set(y_dev[search]) == set(y_dev[~search]) == {0, 1}
        sizes = dict(train=len(y_train), train_malware=int(y_train.sum()),
                     search=int(search.sum()), search_malware=int(y_dev[search].sum()),
                     confirmation=int((~search).sum()), confirmation_malware=int(y_dev[~search].sum()))
        sizes.update(train_groups=len({r["group_id"] for r in rows_train}),
                     search_groups=len({r["group_id"] for r, flag in zip(rows_dev, search) if flag}),
                     confirmation_groups=len({r["group_id"] for r, flag in zip(rows_dev, search) if not flag}))
        print("COHORT " + json.dumps(sizes), flush=True)
        atomic_write_json(args.output / "cohort.json", dict(train=rows_train, dev=rows_dev, sizes=sizes))
        spec = features.build_vocab_from_db(args.db, [(r["row_id"], r["label"]) for r in rows_train],
                                             n_workers=4, checkpoint_dir=args.output / "base_vocab")
        spec.save(args.output / "base_spec.json")
        rows = rows_train + rows_dev
        tasks = [(args.db, rows[start:start+256], str(args.output / "base_spec.json"), str(cache), i)
                 for i, start in enumerate(range(0, len(rows), 256))]
        with features._feature_worker_pool(4) as pool:
            for stem, hashes in features._bounded_iter(pool, extract_batch, tasks, max_inflight=8):
                stems.append(stem)
                digests.extend(hashes)
                if len(stems) % 20 == 0:
                    print(f"Extracted {len(digests)}/{len(rows)} reports ({time.perf_counter()-started:.0f}s)", flush=True)
    counters = {source: [Counter(), Counter()] for source in SOURCES}
    coverage = {source: dict(train=[0, 0], search=[0, 0], confirmation=[0, 0]) for source in SOURCES}
    labels = np.r_[y_train, y_dev]
    for i, words in enumerate(token_rows(cache)):
        partition = "train" if i < len(y_train) else "search" if search[i-len(y_train)] else "confirmation"
        for source in SOURCES:
            coverage[source][partition][int(labels[i])] += bool(words[source])
            if i < len(y_train):
                counters[source][int(labels[i])].update(words[source])
    base = sp.vstack([sp.load_npz(stem + ".npz") for stem in stems], format="csr")
    sp.save_npz(cache / "base.npz", base)
    np.savez_compressed(cache / "rows.npz", y_train=y_train, y_dev=y_dev, search=search,
                        row_ids=np.array([r["row_id"] for r in rows], dtype=np.int64))
    source_info = {}
    for source in SOURCES:
        good, bad = counters[source]
        eligible = [w for w in good.keys() | bad.keys() if good[w]+bad[w] >= keyword_min_support]
        words = sorted(sorted(eligible, key=lambda w: (-(good[w]+bad[w]), w))[:100000])
        lookup = {w: i for i, w in enumerate(words)}
        indices, indptr = [], [0]
        for tokens in token_rows(cache):
            indices.extend(lookup[w] for w in tokens[source] if w in lookup)
            indptr.append(len(indices))
        matrix = sp.csr_matrix((np.ones(len(indices), dtype=np.float32),
                               np.array(indices, dtype=np.int32), np.array(indptr, dtype=np.int64)),
                              shape=(len(rows), len(words)))
        matrix.sort_indices()
        sp.save_npz(cache / f"{source}.npz", matrix)
        info = dict(words=words, goodware=[good[w] for w in words], malware=[bad[w] for w in words],
                    eligible=len(eligible), candidate_cap=100000, matrix_sha256=matrix_digest(matrix))
        atomic_write_json(cache / f"{source}.json", info)
        source_info[source] = dict(eligible=len(eligible), candidates=len(words))
    manifest = dict(route=f"filetypes/{args.route}", sizes=sizes, sources=source_info, feature_env=env, train_config=accepted["train_config"],
                    coverage=coverage, code_revisions=revisions(), base_sha256=matrix_digest(base),
                    snapshot=snapshot, report_revision_sha256=hashlib.sha256(json.dumps(digests).encode()).hexdigest(),
                    seconds=time.perf_counter()-started, search_sample_percent=10,
                    confirmation_group_cap=args.confirmation_groups,
                    exclude_label_conflicts=args.exclude_label_conflicts,
                    training_min_score=int(env["COLLIMATOR_MIN_SAMPLE_SCORE"]),
                    scope=__doc__)
    atomic_write_json(args.output / "inputs.json", manifest)
    print("PREPARED " + json.dumps(dict(sizes=sizes, sources=source_info)), flush=True)


@contextmanager
def goodware_only_selection(sources):
    """Research-only direction filter; compute it on each fit's labels."""
    original = keywords.select_for_fit

    def select(matrix, labels, names, settings=None):
        labels = np.asarray(labels)
        keep = np.ones(matrix.shape[1], dtype=bool)
        for source in sources:
            columns = np.array([i for i, name in enumerate(names) if name.startswith(source+":")], dtype=int)
            if not len(columns):
                continue
            block = matrix[:, columns] != 0
            rates = [(np.asarray(block[labels == label].sum(axis=0)).ravel()+.5)/(int(np.sum(labels == label))+1)
                     for label in (0, 1)]
            keep[columns[rates[0] <= rates[1]]] = False
        masked = matrix.multiply(keep).tocsr() if sp.issparse(matrix) else matrix * keep
        if sp.issparse(masked):
            masked.eliminate_zeros()
        result, stats = original(masked, labels, names, settings)
        for source in sources:
            if source in stats:
                stats[source]["research_direction"] = "goodware_only"
        return result, stats

    if sources:
        keywords.select_for_fit = select
    try:
        yield
    finally:
        keywords.select_for_fit = original


def metrics(labels, scores):
    from collimator.thresholds import recall_at_fp_budget
    from sklearn.metrics import average_precision_score, roc_auc_score
    n_malware, n_goodware = int(np.sum(labels == 1)), int(np.sum(labels == 0))
    result = dict(malware=n_malware, goodware=n_goodware,
                  ap=float(average_precision_score(labels, scores)) if n_malware else None,
                  auc=float(roc_auc_score(labels, scores)) if n_malware and n_goodware else None)
    for budget in (0, 1):
        recall, threshold, _ = recall_at_fp_budget(labels, scores, budget) if n_malware else (None, None, 0)
        result[f"recall_{budget}fp"] = float(recall) if recall is not None else None
        result[f"threshold_{budget}fp"] = None if threshold is None else float(threshold)
    return result


def fit_member(task):
    """Fit one seed in an isolated process; return only scores and audit metadata."""
    matrix, labels, n, names, config, seed, sources, directory, env = task
    os.environ.update(env)
    features.feature_config_from_env.cache_clear()
    features.allowed_features.cache_clear()
    with goodware_only_selection(sources):
        result = train.train(matrix[:n], labels, train.TrainConfig(**dict(config, seed=seed)),
                             feature_names=names)
    result.model.booster_.save_model(str(directory / f"seed_{seed}.txt"))
    return dict(seed=seed, trees=result.model.booster_.num_trees(),
                keyword_selection=result.keyword_selection,
                probabilities=np.asarray(predict_proba(result.model, matrix[n:]), dtype=np.float32))


class Study:
    def __init__(self, root):
        self.root = root
        self.manifest = json.loads((root / "inputs.json").read_text())
        if self.manifest["code_revisions"] != revisions():
            raise ValueError("training/extraction code changed; use a new study")
        set_environment(self.manifest["feature_env"])
        self.base_spec = features.FeatureSpec.load(root / "base_spec.json")
        self.base = sp.load_npz(root / "inputs/base.npz")
        assert matrix_digest(self.base) == self.manifest["base_sha256"]
        with np.load(root / "inputs/rows.npz") as arrays:
            self.y_train, self.y_dev, self.search = arrays["y_train"], arrays["y_dev"], arrays["search"]
            self.ids = arrays["row_ids"]
        self.n = len(self.y_train)
        self.banks = {}
        self.summary_path = root / "search.json"
        self.summary = json.loads(self.summary_path.read_text()) if self.summary_path.exists() else dict(variants={})

    def bank(self, source):
        if source not in self.banks:
            info = json.loads((self.root / "inputs" / f"{source}.json").read_text())
            matrix = sp.load_npz(self.root / "inputs" / f"{source}.npz")
            assert matrix_digest(matrix) == info["matrix_sha256"]
            self.banks[source] = info, matrix
        return self.banks[source]

    def layout(self, options):
        matrices, vocabs = [self.base], {}
        names = list(self.base_spec.feature_names)
        for source, cfg in sorted(options.items()):
            if source == "context_availability":
                flags = np.array([bool(row["contextword"]) for row in token_rows(self.root / "inputs")], dtype=np.float32)
                matrices.append(sp.csr_matrix(flags[:,None]))
                names.append("research:context_available")
                continue
            info, matrix = self.bank(source)
            support = np.array(info["goodware"]) + np.array(info["malware"])
            if cfg["method"] == "frequency":
                eligible = np.flatnonzero(support >= cfg["floor"])
                columns = sorted(sorted(eligible, key=lambda i: (-support[i], info["words"][i]))[:cfg["cap"]])
            else:
                # Preserve the bounded bank; label-aware filtering happens per fit.
                columns = list(range(len(info["words"])))
            words = [info["words"][i] for i in columns]
            vocabs[source] = words
            names.extend(f"{source}:{word}" for word in words)
            matrices.append(matrix[:, columns])
        spec = (replace(self.base_spec, version=23, abi_version=23, base_feature_abi=self.base_spec.abi_version,
                        keyword_vocabs=vocabs, feature_names=names, total_features=len(names)) if options else self.base_spec)
        return sp.hstack(matrices, format="csr"), spec

    def fit(self, name, options, *, seeds=(43, 44), trees=180, confirmation=False, overrides=None):
        directory = self.root / ("confirmation" if confirmation else "search") / name
        result_path = directory / "result.json"
        if result_path.exists():
            saved = json.loads(result_path.read_text())
            assert saved["options"] == options and saved["seeds"] == list(seeds) and saved["tree_budget"] == trees
            return saved
        directory.mkdir(parents=True, exist_ok=True)
        set_environment(self.manifest["feature_env"])
        for source, cfg in options.items():
            if source == "context_availability":
                continue
            prefix = keywords.SOURCES[source]
            os.environ[f"COLLIMATOR_{prefix}_KEYWORDS"] = "1"
            os.environ[f"COLLIMATOR_{prefix}_KEYWORD_SELECTION"] = "frequency" if cfg["method"] == "frequency" else "balanced_mi"
            os.environ[f"COLLIMATOR_{prefix}_KEYWORD_VOCAB_MAX"] = str(cfg["cap"])
            os.environ[f"COLLIMATOR_{prefix}_KEYWORD_MIN_FREQ"] = str(cfg["floor"])
        features.feature_config_from_env.cache_clear()
        matrix, spec = self.layout(options)
        spec.save(directory / "feature_spec.json")
        config = dict(self.manifest["train_config"])
        config.update(learner="azoth", device="cpu", n_estimators=trees, num_threads=4)
        config.update(overrides or {})
        probabilities, members = {}, []
        started = time.perf_counter()
        print(f"Starting {'confirmation' if confirmation else 'search'}/{name}", flush=True)
        sources = {s for s, cfg in options.items() if cfg["method"] == "goodware_only"}
        env = {key: value for key, value in os.environ.items() if key.startswith("COLLIMATOR_")}
        tasks = [(matrix, self.y_train, self.n, spec.feature_names, config, seed, sources, directory, env)
                 for seed in seeds]
        seed_workers = min(len(seeds), 2 if self.manifest.get("route") == "filetypes/pe" else 1)

        def collect(results):
            for member in results:
                scores = member.pop("probabilities")
                probabilities[f"seed_{member['seed']}"] = scores
                member["search"] = metrics(self.y_dev[self.search], scores[self.search])
                members.append(member)

        if seed_workers == 1:
            collect(map(fit_member, tasks))
        else:
            # Spawn avoids inheriting a live OpenMP thread pool. Separate processes
            # also isolate RNG state and the research-only selector override.
            with ProcessPoolExecutor(max_workers=seed_workers,
                                     mp_context=multiprocessing.get_context("spawn")) as pool:
                collect(pool.map(fit_member, tasks))
        ensemble = np.mean([p.astype(np.float64) for p in probabilities.values()], axis=0).astype(np.float32)
        np.savez_compressed(directory / "predictions.npz", **probabilities, ensemble=ensemble)
        output = dict(name=name, options=options, seeds=list(seeds), members=members, tree_budget=trees,
                      seed_workers=seed_workers,
                      diagnostic="context_availability" in options,
                      train_config=config, source_revisions=revisions(), seconds=time.perf_counter()-started,
                      features=len(spec.feature_names), keyword_candidates={s: len(w) for s,w in spec.keyword_vocabs.items()},
                      search=metrics(self.y_dev[self.search], ensemble[self.search]), matrix_sha256=matrix_digest(matrix))
        if confirmation:
            # Only finalists locked before this stage receive confirmation metrics.
            output["confirmation"] = metrics(self.y_dev[~self.search], ensemble[~self.search])
            for member in members:
                member["confirmation"] = metrics(self.y_dev[~self.search], probabilities[f"seed_{member['seed']}"][~self.search])
            for pair in ((43, 44), (45, 46)):
                scores = np.mean([probabilities[f"seed_{s}"].astype(np.float64) for s in pair], axis=0).astype(np.float32)
                output[f"confirmation_seeds_{pair[0]}_{pair[1]}"] = metrics(self.y_dev[~self.search], scores[~self.search])
        atomic_write_json(result_path, output)
        if not confirmation:
            self.summary["variants"][name] = output
            atomic_write_json(self.summary_path, self.summary)
        print("RESULT " + json.dumps(dict(name=name, search=output["search"], confirmation=output.get("confirmation"))), flush=True)
        return output

    def screen(self):
        if (self.root / "locked_finalists.json").exists():
            raise ValueError("search is locked; do not tune on confirmation results")
        self.fit("baseline", {})
        for source in SOURCES:
            for method in ("frequency", "balanced_mi"):
                self.fit(f"{source}-{method}-1000-5", {source: dict(method=method, cap=1000, floor=5)})

    def refine(self):
        if (self.root / "locked_finalists.json").exists():
            raise ValueError("search is locked; do not tune on confirmation results")
        if len(self.summary["variants"]) < 11:
            raise ValueError("complete the source screen first")
        # Rank sources using search labels only, preferring 1-FP then 0-FP recall.
        def rank(r):
            return (r["search"]["recall_1fp"], r["search"]["recall_0fp"], r["search"]["ap"])
        winners = {}
        for source in SOURCES:
            candidates = [r for r in self.summary["variants"].values() if list(r["options"]) == [source]]
            winners[source] = max(candidates, key=rank)
        strongest = sorted(winners, key=lambda s: rank(winners[s]), reverse=True)[:2]
        atomic_write_json(self.root / "refinement_plan.json", dict(sources=strongest, basis="search only"))
        for source in strongest:
            for method, cap, floor in (("frequency", 5000, 5), ("balanced_mi", 5000, 5),
                                       ("balanced_mi", 10000, 5), ("balanced_mi", 1000, 20),
                                       ("balanced_mi", 1000, 2), ("goodware_only", 1000, 5),
                                       ("goodware_only", 5000, 5)):
                self.fit(f"{source}-{method}-{cap}-{floor}", {source: dict(method=method, cap=cap, floor=floor)})
        best = {}
        for source in strongest:
            candidates = [r for r in self.summary["variants"].values() if list(r["options"]) == [source]]
            best[source] = max(candidates, key=rank)["options"][source]
        self.fit("best-sources-combined", best)
        equal = {source: dict(cfg, cap=500) for source,cfg in best.items()}
        self.fit("best-sources-combined-total1000", equal)
        # Preserve the user's distinction: context is an additional source, never pooled text.
        if "contextword" not in best:
            context = winners["contextword"]["options"]["contextword"]
            self.fit("best-sources-plus-context", dict(best, contextword=context))

    def lock_finalists(self):
        if (self.root / "locked_finalists.json").exists() or (self.root / "confirmation").exists():
            raise ValueError("finalists already locked or confirmation already opened")
        if not (self.root / "refinement_plan.json").exists():
            raise ValueError("finish refinement first")
        baseline = self.summary["variants"]["baseline"]["search"]
        candidates = [r for r in self.summary["variants"].values() if r["name"] != "baseline" and not r.get("diagnostic", False)
                      and r["search"]["ap"] >= baseline["ap"] - .01
                      and r["search"]["auc"] >= baseline["auc"] - .01]
        if not candidates:
            raise ValueError("no keyword configuration passes search ranking guards")
        ranks = [lambda r: (r["search"]["recall_1fp"], r["search"]["recall_0fp"], r["search"]["ap"]),
                 lambda r: (r["search"]["recall_0fp"], r["search"]["recall_1fp"], r["search"]["ap"])]
        names = ["baseline"]
        for key in ranks:
            name = max(candidates, key=key)["name"]
            if name not in names:
                names.append(name)
        # Include the strongest implementable standard selector if a research-only
        # direction filter wins; this provides a deployable comparison.
        standard = [r for r in candidates if all(cfg["method"] != "goodware_only" for cfg in r["options"].values())]
        if standard:
            name = max(standard, key=ranks[0])["name"]
            if name not in names:
                names.append(name)
        # Preserve a frequency-only alternative and a multi-source challenger
        # even when a single supervised source wins the search screen.
        for alternatives in (
                [r for r in candidates if all(cfg["method"] == "frequency" for cfg in r["options"].values())],
                [r for r in candidates if len(r["options"]) > 1]):
            if alternatives:
                name = max(alternatives, key=ranks[0])["name"]
                if name not in names:
                    names.append(name)
        best = max(candidates, key=ranks[0])
        tied = [r for r in candidates if all(r["search"][f"recall_{budget}fp"] ==
                                             best["search"][f"recall_{budget}fp"] for budget in (0,1))]
        smaller = min(tied, key=lambda r: sum(cfg["cap"] for cfg in r["options"].values()))
        if smaller["name"] not in names:
            names.append(smaller["name"])
        # Preserve source ablations so a combined winner can be compared with
        # each constituent on the untouched confirmation cohort.
        for source in best["options"]:
            singles = [r for r in candidates if list(r["options"]) == [source]]
            if singles:
                name = max(singles, key=ranks[0])["name"]
                if name not in names:
                    names.append(name)
        if "context-availability-control" in self.summary["variants"]:
            names.append("context-availability-control")
        locked = dict(names=names, options={name:self.summary["variants"][name]["options"] for name in names},
                      basis="10% development search only; confirmation scores unexamined", trees=400, seeds=[43,44,45,46],
                      search_sha256=hashlib.sha256(self.summary_path.read_bytes()).hexdigest())
        atomic_write_json(self.root / "locked_finalists.json", locked)
        print("LOCKED " + json.dumps(locked), flush=True)

    def budgets(self):
        if (self.root / "locked_finalists.json").exists():
            raise ValueError("search is locked; do not tune on confirmation results")
        plan = json.loads((self.root / "refinement_plan.json").read_text())
        for source in plan["sources"]:
            for cap, floor in ((250,5), (500,5), (1000,2), (1000,20), (10000,5)):
                self.fit(f"{source}-frequency-{cap}-{floor}", {source: dict(method="frequency",cap=cap,floor=floor)})
            if self.manifest["sources"][source]["candidates"] > 10000:
                self.fit(f"{source}-frequency-25000-5", {source: dict(method="frequency",cap=25000,floor=5)})
        if set(plan["sources"]) == {"ruletextword", "contextword"}:
            for pooled, context in ((250,250),(250,750),(750,250),(250,1000),(1000,250)):
                self.fit(f"pooled{pooled}-context{context}", {
                    "ruletextword":dict(method="frequency",cap=pooled,floor=5),
                    "contextword":dict(method="frequency",cap=context,floor=5)})

    def availability(self):
        if (self.root / "locked_finalists.json").exists():
            raise ValueError("search is locked; do not tune on confirmation results")
        self.fit("context-availability-control", {"context_availability":dict(method="frequency", cap=1, floor=1)})

    def confirm(self):
        locked = json.loads((self.root / "locked_finalists.json").read_text())
        if locked["search_sha256"] != hashlib.sha256(self.summary_path.read_bytes()).hexdigest():
            raise ValueError("search changed after finalist lock")
        results = {}
        for name in locked["names"]:
            results[name] = self.fit(name, locked["options"][name], seeds=locked["seeds"],
                                     trees=locked["trees"], confirmation=True)
            atomic_write_json(self.root / "confirmation.json", dict(protocol=locked, variants=results))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "screen", "refine", "budgets", "availability", "lock", "confirm"])
    parser.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    parser.add_argument("--route", choices=("macho", "pe"), default="macho")
    parser.add_argument("--confirmation-groups", type=int, default=0,
                        help="label-blind confirmation group cap during preparation; 0 means all")
    parser.add_argument("--exclude-label-conflicts", action="store_true",
                        help="exclude canonical groups with contradictory labels before sampling confirmation")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is None:
        args.output = Path(f"out/experiments/keyword-{args.route}-search")
    if args.action == "prepare":
        prepare(args)
    else:
        study = Study(args.output)
        if study.manifest.get("route", "filetypes/macho") != f"filetypes/{args.route}":
            raise ValueError("requested route does not match the prepared study")
        {"screen": study.screen, "refine": study.refine, "budgets": study.budgets, "lock": study.lock_finalists,
         "availability": study.availability, "confirm": study.confirm}[args.action]()


if __name__ == "__main__":
    main()
