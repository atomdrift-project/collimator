#!/usr/bin/env python3
"""WHL training-cutoff and regularization follow-up, using dev only.

The previously opened dev cohort is reused for this additional screen. A
single frozen finalist still requires a subsequent locked-test comparison.
"""
import argparse
import hashlib
import json
from pathlib import Path

import keyword_image_transfer as transfer
import keyword_model_search as search
from collimator.bundle import atomic_write_json


def prepare(args):
    accepted, baseline = search.capture_config(args.deployed, "whl")
    original_cutoff = accepted["min_malware_training_score"]
    accepted["min_malware_training_score"] = 0

    def select(metadata, document):
        train, dev, _ = search.select_cohort(metadata, document, 0)
        for row in train:
            row["target"] = not row["label"] or row["score"] >= original_cutoff
        return train, dev

    args.route = "whl"
    args.exclude_label_conflicts = True
    args.confirmation_groups = 0
    search.research.prepare(args, row_selector=select, search_selector=search.is_search,
        accepted_config=accepted, keyword_min_support=1)
    p = args.output / "inputs.json"
    manifest = json.loads(p.read_text())
    manifest.update(scope=__doc__, baseline_options=baseline, search_sample_percent=50,
                    original_malware_cutoff=original_cutoff, transfer_kind="training_cutoff",
                    preparation_runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    atomic_write_json(p, manifest)


class Study(transfer.Study):
    def screen(self):
        if (self.root / "locked_finalists.json").exists():
            raise ValueError("search is locked")
        base = self.manifest["baseline_options"]
        plans = {}
        for complete in (False, True):
            prefix = "all-malware" if complete else "current-cutoff"
            cutoff = 0 if complete else self.manifest["original_malware_cutoff"]
            settings = {"baseline": {},
                "cap5-weight025": dict(max_delta_step=5., scale_pos_weight_mult=.25, hard_negative_fraction=0.),
                "finer-regularized": dict(num_leaves=32, max_depth=8, min_child_samples=10,
                    min_child_weight=1., reg_lambda=5., max_delta_step=2.,
                    scale_pos_weight_mult=.25, hard_negative_fraction=0.)}
            for label, training in settings.items():
                name = "baseline" if not complete and label == "baseline" else prefix+"-"+label
                plans[name] = dict(self.variant(training=training,
                    family="baseline" if name == "baseline" else "structure"),
                    pooled=complete, training_malware_cutoff=cutoff)
            for source in ("descword", "ruletextword", "contextword"):
                plans[prefix+"-"+source] = dict(self.variant(keyword_options=base | search.options(source), source=source),
                    pooled=complete, training_malware_cutoff=cutoff)
        atomic_write_json(self.root / "initial_plan.json", plans)
        for name, variant in plans.items():
            self.fit_variant(name, variant)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=Path("out/experiments/whl-keyword-followup-20261102/whl"))
    p.add_argument("--deployed", type=Path, default=Path("../azoth"))
    p.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
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
