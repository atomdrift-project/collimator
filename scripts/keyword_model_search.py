#!/usr/bin/env python3
"""Matched keyword and tree searches for weak deployed specialist routes.

Use training rows to build every vocabulary and fit every model. Split the
ordinary dev partition into disjoint canonical-group search and confirmation
cohorts. Lock finalists before confirmation. Never load locked-test reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np

import keyword_macho_search as research
from collimator import keywords
from collimator.bundle import atomic_write_json

ROUTES = ("shell", "c", "package.json", "jpeg", "gif", "whl", "png", "csharp")
ROOT = Path(__file__).resolve().parents[1]


def group_hash(group, purpose):
    return hashlib.sha256(("weak-specialists-v1:" + purpose + ":" + group.lower()).encode()).hexdigest()


def is_search(group):
    return int(group_hash(group, "dev"), 16) < 2**255


def select_cohort(metadata, accepted, max_train_groups):
    rows = [dict(row_id=rid, label=label, group_id=group.lower(), score=score,
                 partition=partition)
            for rid, label, partition, group, score in metadata if partition != "test"]
    rows, excluded = research.exclude_label_conflicts(rows)
    cutoff = accepted["min_malware_training_score"]
    floor = (accepted.get("training_score_filter") or {}).get("min_score") or 0
    training = [r for r in rows if r["partition"] == "train" and r["score"] >= floor
                and (not r["label"] or r["score"] >= cutoff)]
    groups = {r["group_id"] for r in training}
    if max_train_groups and len(groups) > max_train_groups:
        kept = set(sorted(groups, key=lambda g: (group_hash(g, "train-cap"), g))[:max_train_groups])
        training = [r for r in training if r["group_id"] in kept]
    dev = [r for r in rows if r["partition"] == "dev"]
    return training, dev, excluded


def capture_config(deployed, route):
    path = deployed / "filetypes" / route
    document = json.loads((path / "training_config.json").read_text())
    document["route"] = f"filetypes/{route}"
    for key in ("COLLIMATOR_ALLOWED_FEATURES_FILE", "COLLIMATOR_FEATURE_SPEC_FILE"):
        value = document["feature_env"].get(key)
        if value and not Path(value).is_absolute():
            document["feature_env"][key] = str(ROOT / value)
    spec = json.loads((path / "feature_spec.json").read_text())
    research.set_environment(document["feature_env"])
    settings = keywords.settings_from_env()
    baseline_options = {
        source: dict(method=settings[source]["selection"], cap=settings[source]["vocab_max"],
                     floor=settings[source]["min_freq"])
        for source, words in spec.get("keyword_vocabs", {}).items() if words
    }
    return document, baseline_options


def prepare(args):
    accepted, baseline_options = capture_config(args.deployed, args.route)
    exclusions = []

    def selector(metadata, config):
        train, dev, excluded = select_cohort(metadata, config, args.max_train_groups)
        exclusions.extend(excluded)
        return train, dev

    research.prepare(args, row_selector=selector, search_selector=is_search,
                     accepted_config=accepted, keyword_min_support=1)
    manifest_path = args.output / "inputs.json"
    manifest = json.loads(manifest_path.read_text())
    manifest.update(scope=__doc__, search_sample_percent=50,
                    baseline_options=baseline_options, max_train_groups=args.max_train_groups,
                    training_score_filter=accepted.get("training_score_filter"),
                    preparation_runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    baseline_training_config_sha256=hashlib.sha256(
                        (args.deployed / "filetypes" / args.route / "training_config.json").read_bytes()).hexdigest())
    atomic_write_json(manifest_path, manifest)
    atomic_write_json(args.output / "excluded_label_conflicts.json", exclusions)


def options(source, method="frequency", cap=1000, floor=5):
    return {source: dict(method=method, cap=cap, floor=floor)}


class Study(research.Study):
    @staticmethod
    def rank(result):
        m = result["search"]
        return m["recall_1fp"], m["recall_0fp"], m["ap"]

    def set_base(self, variant):
        """Every variant shares the same frozen base vocabulary and matrices."""

    def variant(self, *, keyword_options=None, training=None, family="keyword", source=None):
        return dict(options=(self.manifest["baseline_options"] if keyword_options is None else keyword_options),
                    training=training or {}, family=family, source=source)

    def fit_variant(self, name, variant, confirmation=False):
        path = self.root / ("confirmation" if confirmation else "search") / name / "result.json"
        if path.exists():
            result = json.loads(path.read_text())
            if result.get("variant") != variant:
                raise ValueError(f"cached variant changed: {name}")
            return result
        result = super().fit(name, variant["options"],
                             seeds=(43, 44, 45, 46) if confirmation else (43, 44),
                             trees=400 if confirmation else 180, confirmation=confirmation,
                             overrides=variant["training"])
        result["variant"] = variant
        atomic_write_json(path, result)
        if not confirmation:
            self.summary["variants"][name] = result
            atomic_write_json(self.summary_path, self.summary)
        return result

    def screen(self):
        if (self.root / "locked_finalists.json").exists():
            raise ValueError("search is locked")
        plans = {"baseline": self.variant(family="baseline")}
        base = self.manifest["baseline_options"]
        if base:
            plans["no-keywords"] = self.variant(keyword_options={}, family="keyword-ablation")
        for source in keywords.SOURCES:
            for method in ("frequency", "balanced_mi"):
                name = f"{source}-{method}-1000"
                plans[name] = self.variant(keyword_options=base | options(source, method), source=source)
        plans["pe-combination"] = self.variant(keyword_options=base
            | options("descword", "balanced_mi", 5000)
            | options("ruleword", "balanced_mi") | options("contextword"))
        for name, settings in {
            "shallow-support25": dict(num_leaves=31, max_depth=8, min_child_samples=25, reg_lambda=5.0),
            "moderate-support50": dict(num_leaves=63, max_depth=10, min_child_samples=50, reg_lambda=5.0),
            "no-hard-negatives": dict(hard_negative_fraction=0.0, hard_negative_weight=1.0),
            "positive-weight1": dict(scale_pos_weight_mult=1.0),
        }.items():
            if any(self.manifest["train_config"].get(k) != v for k, v in settings.items()):
                plans[name] = self.variant(training=settings, family="structure")
        plans["context-availability-control"] = self.variant(
            keyword_options=base | options("context_availability", cap=1, floor=1), family="diagnostic")
        atomic_write_json(self.root / "initial_plan.json", plans)
        for name, variant in plans.items():
            self.fit_variant(name, variant)

    def refine(self):
        if (self.root / "locked_finalists.json").exists():
            raise ValueError("search is locked")
        candidates = [r for r in self.summary["variants"].values() if r["variant"]["source"]]
        winners = {source: max((r for r in candidates if r["variant"]["source"] == source), key=self.rank)
                   for source in keywords.SOURCES}
        strongest = sorted(winners, key=lambda s: self.rank(winners[s]), reverse=True)[:2]
        base = self.manifest["baseline_options"]
        plans = {}
        for source in strongest:
            method = winners[source]["options"][source]["method"]
            for cap, floor in ((5000, 5), (1000, 2)):
                name = f"{source}-{method}-{cap}-support{floor}"
                plans[name] = self.variant(keyword_options=base | options(source, method, cap, floor), source=source)
        for name, variant in plans.items():
            self.fit_variant(name, variant)
        all_results = list(self.summary["variants"].values())
        best = {s: max((r for r in all_results if r["variant"]["source"] == s), key=self.rank)
                for s in strongest}
        combined = dict(base)
        for s, result in best.items():
            combined[s] = result["options"][s]
        plans["best-two-sources"] = self.variant(keyword_options=combined)
        structure = max((r for r in all_results if r["variant"]["family"] in {"baseline", "structure"}), key=self.rank)
        plans["best-sources-and-structure"] = self.variant(
            keyword_options=combined, training=structure["variant"]["training"], family="combined")
        atomic_write_json(self.root / "refinement_plan.json", dict(sources=strongest, plans=plans))
        for name in ("best-two-sources", "best-sources-and-structure"):
            self.fit_variant(name, plans[name])

    def lock(self):
        if (self.root / "locked_finalists.json").exists():
            return
        results = [r for r in self.summary["variants"].values() if not r.get("diagnostic")]
        baseline = self.summary["variants"]["baseline"]["search"]
        eligible = [r for r in results if r["search"]["ap"] >= baseline["ap"] - .01
                    and r["search"]["auc"] >= baseline["auc"] - .01]
        names = ["baseline"]
        categories = [eligible,
                      [r for r in eligible if r["variant"]["family"] == "keyword"],
                      [r for r in eligible if r["variant"]["family"] == "structure"]]
        for candidates in categories:
            if candidates:
                names.append(max(candidates, key=self.rank)["name"])
        names.append(max(eligible, key=lambda r: (r["search"]["recall_0fp"],
                     r["search"]["recall_1fp"], r["search"]["ap"]))["name"])
        names = list(dict.fromkeys(names))
        variants = {name: self.summary["variants"][name]["variant"] for name in names}
        atomic_write_json(self.root / "locked_finalists.json", dict(
            names=names, variants=variants, seeds=[43, 44, 45, 46], trees=400,
            search_sha256=hashlib.sha256(self.summary_path.read_bytes()).hexdigest(),
            basis="Only canonical-group search metrics; confirmation metrics unopened."))
        print("LOCKED " + json.dumps(names), flush=True)

    def confirm(self):
        locked = json.loads((self.root / "locked_finalists.json").read_text())
        assert locked["search_sha256"] == hashlib.sha256(self.summary_path.read_bytes()).hexdigest()
        results = {}
        for name in locked["names"]:
            results[name] = self.fit_variant(name, locked["variants"][name], confirmation=True)
            atomic_write_json(self.root / "confirmation.json", dict(protocol=locked, variants=results))

    def verify(self):
        from summarize_macho_keywords import verify
        verify(self.root, study_class=Study)


def run_one(args):
    if not (args.output / "inputs.json").exists():
        if args.output.exists():
            raise ValueError(f"incomplete extraction at {args.output}; preserve it and choose a fresh output")
        prepare(args)
    study = Study(args.output)
    if not (args.output / "locked_finalists.json").exists():
        study.screen()
        study.refine()
        study.lock()
    study.confirm()
    study.verify()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route", choices=ROUTES)
    parser.add_argument("--routes", nargs="+", choices=ROUTES, default=list(ROUTES))
    parser.add_argument("--output", type=Path, default=Path("out/experiments/weak-specialist-keywords-20261102"))
    parser.add_argument("--deployed", type=Path, default=Path("../azoth"))
    parser.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    parser.add_argument("--max-train-groups", type=int, default=150000)
    parser.add_argument("--route-jobs", type=int, default=2)
    args = parser.parse_args()
    if args.max_train_groups < 0 or args.route_jobs < 1:
        parser.error("invalid training cap or route concurrency")
    args.exclude_label_conflicts = True
    args.confirmation_groups = 0
    if args.route:
        run_one(args)
        return
    args.output.mkdir(parents=True, exist_ok=True)
    atomic_write_json(args.output / "plan.json", dict(routes=args.routes, max_train_groups=args.max_train_groups,
        route_jobs=args.route_jobs, deployed=str(args.deployed.resolve()), protocol=__doc__))

    def launch(route):
        command = [sys.executable, str(Path(__file__).resolve()), "--route", route,
                   "--output", str(args.output / route), "--deployed", str(args.deployed.resolve()),
                   "--db", args.db, "--max-train-groups", str(args.max_train_groups)]
        with (args.output / f"{route}.log").open("a") as log:
            subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        print(f"Completed {route}", flush=True)

    with ThreadPoolExecutor(max_workers=args.route_jobs) as executor:
        results = list(executor.map(launch, args.routes))


if __name__ == "__main__":
    main()
