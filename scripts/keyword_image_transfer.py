#!/usr/bin/env python3
"""Image transfer follow-up on previously opened development cohorts.

Compare target-only fitting with target plus other image formats, using the
same frozen feature layout. This is additional dev screening, not independent
confirmation; freeze a single finalist before a subsequent locked-test check.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import keyword_model_search as search
from collimator import data
from collimator.bundle import atomic_write_json


def prepare(args):
    accepted, baseline = search.capture_config(args.deployed, args.route)

    def select(_unused, document):
        target_ids = {rid for rid, _, partition, _, _ in data.stream_partitioned_metadata_grouped(
            args.db, file_types=(args.route,), min_score=None) if partition != "test"}
        metadata = data.stream_partitioned_metadata_grouped(args.db, file_types=("jpeg", "gif", "png"), min_score=None)
        training, dev, excluded = search.select_cohort(metadata, document, 0)
        target = [r for r in training if r["row_id"] in target_ids]
        auxiliary = [r for r in training if r["row_id"] not in target_ids]
        selected = set(sorted({r["group_id"] for r in auxiliary},
            key=lambda g: (search.group_hash(g, "image-transfer"), g))[:args.auxiliary_groups])
        training = target + [r for r in auxiliary if r["group_id"] in selected]
        for row in training:
            row["target"] = row["row_id"] in target_ids
        return training, [r for r in dev if r["row_id"] in target_ids]

    args.exclude_label_conflicts = True
    args.confirmation_groups = 0
    search.research.prepare(args, row_selector=select, search_selector=search.is_search,
        accepted_config=accepted, keyword_min_support=1)
    p = args.output / "inputs.json"
    manifest = json.loads(p.read_text())
    manifest.update(scope=__doc__, baseline_options=baseline, search_sample_percent=50,
                    auxiliary_group_cap=args.auxiliary_groups,
                    preparation_runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    atomic_write_json(p, manifest)


class Study(search.Study):
    def __init__(self, root):
        super().__init__(root)
        self.full_base, self.full_labels, self.full_n = self.base, self.y_train, self.n
        cohort = json.loads((root / "cohort.json").read_text())
        self.target = np.array([r["target"] for r in cohort["train"]], dtype=bool)
        self.active = np.ones(self.base.shape[0], dtype=bool)

    def set_base(self, variant):
        mask = np.ones(self.full_n, dtype=bool) if variant.get("pooled", True) else self.target
        self.active = np.r_[mask, np.ones(len(self.y_dev), dtype=bool)]
        self.n = int(mask.sum())
        self.y_train = self.full_labels[mask]
        self.base = self.full_base[self.active]

    def bank(self, source):
        info, matrix = super().bank(source)
        return info, matrix[self.active]

    def fit_variant(self, name, variant, confirmation=False):
        self.set_base(variant)
        return super().fit_variant(name, variant, confirmation)

    def screen(self):
        if (self.root / "locked_finalists.json").exists():
            raise ValueError("search is locked")
        base = self.manifest["baseline_options"]
        plans = {"baseline": dict(self.variant(family="baseline"), pooled=False),
                 "image-pooled": dict(self.variant(family="structure"), pooled=True)}
        for pooled in (False, True):
            prefix = "pooled" if pooled else "target"
            plans[prefix+"-small-leaves"] = dict(self.variant(family="structure", training=dict(
                num_leaves=31, max_depth=8, min_child_samples=10, min_child_weight=1.,
                reg_lambda=5., hard_negative_fraction=0., hard_negative_weight=1., max_delta_step=2.)), pooled=pooled)
            for source, method in (("descword", "balanced_mi"), ("ruletextword", "frequency"),
                                   ("contextword", "frequency")):
                plans[prefix+"-"+source] = dict(self.variant(
                    keyword_options=base | search.options(source, method), source=source), pooled=pooled)
        atomic_write_json(self.root / "initial_plan.json", plans)
        for name, variant in plans.items():
            self.fit_variant(name, variant)

    def lock(self):
        super().lock()
        p = self.root / "locked_finalists.json"
        value = json.loads(p.read_text())
        value["basis"] = "Follow-up search on previously opened dev cohorts; locked-test evaluation is required."
        atomic_write_json(p, value)

    def verify(self):
        from summarize_macho_keywords import verify
        verify(self.root, study_class=Study)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--route", choices=["jpeg", "gif"], required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--deployed", type=Path, default=Path("../azoth"))
    p.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    p.add_argument("--auxiliary-groups", type=int, default=30000)
    args = p.parse_args()
    if not (args.output / "inputs.json").exists():
        prepare(args)
    study = Study(args.output)
    if not (args.output / "locked_finalists.json").exists():
        study.screen()
        study.lock()
    study.confirm()
    study.verify()


if __name__ == "__main__":
    main()
