#!/usr/bin/env python3
"""WHL capacity/keyword screen on cached reports; never opens historical test.

Reserve 20% of original training canonical groups before fitting. Select on
the previously viewed dev search half, then open the reserved groups once.
The base vocabulary is frozen from the earlier corpus, so this is a model
comparison, not a claim of fully independent end-to-end validation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import joblib
import lightgbm as lgb
import numpy as np
import scipy.sparse as sp
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MaxAbsScaler

import keyword_macho_search as research
from collimator.bundle import atomic_write_json
from collimator.thresholds import recall_at_fp_budget


def metrics(y, p):
    result = research.metrics(y, p)
    for fp in (2, 5, 10):
        result[f"recall_{fp}fp"] = float(recall_at_fp_budget(y, p, fp)[0])
    threshold = np.sort(p[y == 1])[::-1][int(np.ceil(.8 * sum(y == 1))) - 1]
    result["fp_for_80pct"] = int(sum(p[y == 0] >= threshold))
    result["threshold_80pct"] = float(threshold)
    return result


def plans():
    settings = {
        "current": {},
        "fine": dict(num_leaves=63, max_depth=10, min_child_samples=10,
                     min_child_weight=1, reg_lambda=5, n_estimators=600),
        "small": dict(num_leaves=15, max_depth=6, min_child_samples=20,
                      min_child_weight=1, reg_lambda=10, n_estimators=800),
        "extra": dict(num_leaves=63, max_depth=10, min_child_samples=10,
                      min_child_weight=1, reg_lambda=5, extra_trees=True, n_estimators=800),
        "low-weight": dict(num_leaves=63, max_depth=10, min_child_samples=10,
                           min_child_weight=1, reg_lambda=5, scale_pos_weight_mult=.025,
                           max_delta_step=0, n_estimators=600),
    }
    result = {f"{layout}-{name}": dict(kind="lightgbm", layout=layout, settings=config)
              for layout in ("base", "text10000", "context20000")
              for name, config in settings.items()}
    for layout in ("base", "text10000", "context20000"):
        for c in (.1, 1, 10):
            result[f"{layout}-linear-{c}"] = dict(kind="linear", layout=layout, C=c)
    return result


class Study:
    def __init__(self, source, output):
        self.source, self.output = source, output
        output.mkdir(parents=True, exist_ok=True)
        self.manifest = json.loads((source / "inputs.json").read_text())
        assert self.manifest["code_revisions"] == research.revisions()
        rows = json.loads((source / "cohort.json").read_text())
        arrays = np.load(source / "inputs/rows.npz")
        self.y = np.r_[arrays["y_train"], arrays["y_dev"]]
        self.n = len(arrays["y_train"])
        self.fit = np.array([int(hashlib.sha256(("whl80-reserve-v1:" + r["group_id"].lower()).encode()).hexdigest(), 16) % 5 != 0
                             for r in rows["train"]] + [False] * len(arrays["y_dev"]))
        self.reserved = np.r_[~self.fit[:self.n], np.zeros(len(arrays["y_dev"]), dtype=bool)]
        self.search = np.r_[np.zeros(self.n, dtype=bool), arrays["search"]]
        self.dev_confirm = np.r_[np.zeros(self.n, dtype=bool), ~arrays["search"]]
        self.base = sp.load_npz(source / "inputs/base.npz")
        self.layouts = {"base": self.base}
        atomic_write_json(output / "protocol.json", dict(description=__doc__,
            fit_ids=arrays["row_ids"][self.fit].tolist(), reserved_ids=arrays["row_ids"][self.reserved].tolist(),
            selection="previously viewed dev search only; rank recall@1FP, recall@0FP, AP",
            plans=plans(), fit_bad=int(self.y[self.fit].sum()), reserved_bad=int(self.y[self.reserved].sum()),
            source=str(source), source_manifest_sha256=hashlib.sha256((source / "inputs.json").read_bytes()).hexdigest()))

    def matrix(self, layout):
        if layout not in self.layouts:
            source, cap = ("ruletextword", 10000) if layout == "text10000" else ("contextword", 20000)
            matrix = sp.load_npz(self.source / "inputs" / f"{source}.npz")
            words = json.loads((self.source / "inputs" / f"{source}.json").read_text())["words"]
            support = np.asarray(matrix[self.fit].sum(axis=0)).ravel()
            eligible = np.flatnonzero(support >= 2)
            columns = sorted(sorted(eligible, key=lambda i: (-support[i], words[i]))[:cap])
            self.layouts[layout] = sp.hstack([self.base, matrix[:, columns]], format="csr")
            atomic_write_json(self.output / f"{layout}-vocabulary.json", dict(source=source, words=[words[i] for i in columns]))
        return self.layouts[layout]

    def run(self, name, plan, seed):
        directory = self.output / "fits" / name / str(seed)
        directory.mkdir(parents=True, exist_ok=True)
        if (directory / "search.json").exists():
            return json.loads((directory / "search.json").read_text())
        x, y = self.matrix(plan["layout"]), self.y[self.fit]
        started = time.perf_counter()
        if plan["kind"] == "linear":
            model = make_pipeline(MaxAbsScaler(), LogisticRegression(C=plan["C"], solver="liblinear",
                                  max_iter=500, random_state=seed, class_weight="balanced"))
        else:
            cfg = dict(self.manifest["train_config"], **plan["settings"])
            model = lgb.LGBMClassifier(objective="binary", verbosity=-1, force_col_wise=True,
                n_jobs=4, random_state=seed, scale_pos_weight=(sum(y == 0) / sum(y == 1)) * cfg["scale_pos_weight_mult"],
                subsample_freq=1, **{k: cfg[k] for k in ("n_estimators", "num_leaves", "max_depth", "min_child_samples",
                    "min_child_weight", "reg_lambda", "reg_alpha", "learning_rate", "subsample", "colsample_bytree",
                    "max_delta_step", "extra_trees", "boosting_type")})
        model.fit(x[self.fit], y)
        p = model.predict_proba(x)[:, 1].astype(np.float32)
        joblib.dump(model, directory / "model.joblib")
        if plan["kind"] == "lightgbm":
            model.booster_.save_model(str(directory / "model.txt"))
        np.savez_compressed(directory / "predictions.npz", scores=p)
        result = dict(name=name, seed=seed, plan=plan, features=x.shape[1],
                      seconds=time.perf_counter()-started, search=metrics(self.y[self.search], p[self.search]))
        atomic_write_json(directory / "search.json", result)
        print(json.dumps(result), flush=True)
        return result

    def screen(self):
        if (self.output / "locked.json").exists():
            raise ValueError("screen already locked")
        results = [self.run(name, plan, 43) for name, plan in plans().items()]
        baseline = next(r for r in results if r["name"] == "base-current")
        eligible = [r for r in results if r["search"]["ap"] >= baseline["search"]["ap"] - .01]
        rank = lambda r: (r["search"]["recall_1fp"], r["search"]["recall_0fp"], r["search"]["ap"])
        names = ["base-current", max(eligible, key=rank)["name"],
                 max((r for r in eligible if r["plan"]["kind"] == "lightgbm"), key=rank)["name"]]
        atomic_write_json(self.output / "locked.json", dict(names=list(dict.fromkeys(names)), plans=plans(),
                          basis="dev search only; reserved scores unopened", results=results))

    def confirm(self):
        locked = json.loads((self.output / "locked.json").read_text())
        results = {}
        for name in locked["names"]:
            for seed in (43, 44, 45, 46):
                self.run(name, locked["plans"][name], seed)
            p = np.mean([np.load(self.output / "fits" / name / str(seed) / "predictions.npz")["scores"].astype(np.float64)
                         for seed in (43, 44, 45, 46)], axis=0).astype(np.float32)
            results[name] = {label: metrics(self.y[mask], p[mask]) for label, mask in (
                ("reserved_training_groups", self.reserved), ("previously_viewed_dev_confirmation", self.dev_confirm))}
            atomic_write_json(self.output / "confirmation.json", dict(protocol=locked, results=results))
            print("CONFIRM " + json.dumps({name: results[name]}), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("screen", "confirm"))
    p.add_argument("--source", type=Path, default=Path("out/experiments/weak-specialist-keywords-20261102/whl"))
    p.add_argument("--output", type=Path, default=Path("out/experiments/whl-80-20261102/capacity"))
    args = p.parse_args()
    study = Study(args.source, args.output)
    getattr(study, args.action)()
