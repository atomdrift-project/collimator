#!/usr/bin/env python3
"""Verify a route keyword screen, report confirmation, and audit benign words."""
import argparse
import hashlib
import json
from pathlib import Path

import lightgbm as lgb
import numpy as np
from sklearn.model_selection import train_test_split

from keyword_macho_search import Study, metrics, matrix_digest, keywords, set_environment, goodware_only_selection, token_rows
from collimator.bundle import atomic_write_json


def canonical_metrics(labels, scores, groups):
    """One decision per canonical group, using its most suspicious report."""
    grouped = {}
    for label, score, group in zip(labels, scores, groups, strict=True):
        group = group.lower()
        if group in grouped:
            if grouped[group][0] != label:
                raise ValueError("contradictory labels in canonical evaluation group")
            grouped[group] = (label, max(score, grouped[group][1]))
        else:
            grouped[group] = (label, score)
    return metrics(np.array([r[0] for r in grouped.values()]),
                   np.array([r[1] for r in grouped.values()]))


def verify(root, study_class=Study):
    study = study_class(root)
    confirmation = json.loads((root / "confirmation.json").read_text())
    locked = json.loads((root / "locked_finalists.json").read_text())
    assert list(confirmation["variants"]) == locked["names"]
    assert hashlib.sha256((root / "search.json").read_bytes()).hexdigest() == locked["search_sha256"]
    for name, result in confirmation["variants"].items():
        if "variants" in locked:
            assert result["variant"] == locked["variants"][name]
        else:
            assert result["options"] == locked["options"][name]
        assert result["seeds"] == locked["seeds"] and result["tree_budget"] == locked["trees"]
    flags = np.array([bool(row["contextword"]) for row in token_rows(root / "inputs")])[study.n:]
    cohort = json.loads((root / "cohort.json").read_text())
    np.testing.assert_array_equal(study.ids, [r["row_id"] for r in cohort["train"] + cohort["dev"]])
    np.testing.assert_array_equal(study.y_train, [r["label"] for r in cohort["train"]])
    np.testing.assert_array_equal(study.y_dev, [r["label"] for r in cohort["dev"]])
    groups = np.array([r["group_id"].lower() for r in cohort["dev"]])
    assert not {r["group_id"].lower() for r in cohort["train"]} & set(groups)
    assert not set(groups[study.search]) & set(groups[~study.search])
    verified, prediction_sets = [], {}
    for phase, results in (("search",study.summary["variants"]), ("confirmation",confirmation["variants"])):
        for name, result in results.items():
            directory = root / phase / name
            if "variant" in result:
                study.set_base(result["variant"])
            matrix, spec = study.layout(result["options"])
            assert matrix_digest(matrix) == result["matrix_sha256"]
            saved_spec = json.loads((directory / "feature_spec.json").read_text())
            assert spec.feature_names == saved_spec["feature_names"]
            assert spec.keyword_vocabs == saved_spec["keyword_vocabs"]
            set_environment(study.manifest["feature_env"])
            for source, cfg in result["options"].items():
                if source not in keywords.SOURCES:
                    continue
                prefix = keywords.SOURCES[source]
                import os
                os.environ[f"COLLIMATOR_{prefix}_KEYWORD_SELECTION"] = "frequency" if cfg["method"] == "frequency" else "balanced_mi"
                os.environ[f"COLLIMATOR_{prefix}_KEYWORD_VOCAB_MAX"] = str(cfg["cap"])
                os.environ[f"COLLIMATOR_{prefix}_KEYWORD_MIN_FREQ"] = str(cfg["floor"])
            scores = []
            with np.load(directory / "predictions.npz") as saved:
                for member in result["members"]:
                    seed = member["seed"]
                    model = lgb.Booster(model_file=str(directory / f"seed_{seed}.txt"))
                    prediction = np.asarray(model.predict(matrix[study.n:],num_threads=4),dtype=np.float32)
                    np.testing.assert_array_equal(prediction,saved[f"seed_{seed}"])
                    fitting,_ = train_test_split(np.arange(study.n),test_size=result["train_config"]["holdout_fraction"],
                                                stratify=study.y_train,random_state=seed)
                    sources = {s for s,cfg in result["options"].items() if cfg["method"] == "goodware_only"}
                    with goodware_only_selection(sources):
                        masked,stats = keywords.select_for_fit(matrix[:study.n][fitting],study.y_train[fitting],spec.feature_names)
                    assert stats == member["keyword_selection"]
                    # Trees cannot use keyword columns discarded by their fitting selector.
                    active = np.asarray((masked != 0).sum(axis=0)).ravel() > 0
                    used = model.feature_importance("split") > 0
                    assert not np.any(used & ~active)
                    scores.append(prediction.astype(np.float64))
                mean = np.mean(scores,axis=0).astype(np.float32)
                np.testing.assert_array_equal(mean,saved["ensemble"])
            measured = metrics(study.y_dev[study.search],mean[study.search])
            assert measured == result["search"]
            if phase == "confirmation":
                assert metrics(study.y_dev[~study.search],mean[~study.search]) == result["confirmation"]
                prediction_sets[name] = mean
            verified.append(dict(phase=phase,name=name,models=len(scores),verified=True))
        print(f"Verified {phase}: {len(results)} configurations",flush=True)
    baseline = confirmation["variants"]["baseline"]
    comparisons = []
    for name,result in confirmation["variants"].items():
        metrics_now = result["confirmation"]
        delta = {f"delta_{budget}fp":metrics_now[f"recall_{budget}fp"]-baseline["confirmation"][f"recall_{budget}fp"] for budget in (0,1)}
        detail = dict(name=name,options=result["options"],metrics=metrics_now,**delta,diagnostic=result.get("diagnostic",False))
        detail["seed_pairs"] = {f"{a}-{b}":result[f"confirmation_seeds_{a}_{b}"] for a,b in ((43,44),(45,46))}
        detail["context_present_only"] = metrics(study.y_dev[(~study.search)&flags],prediction_sets[name][(~study.search)&flags])
        detail["context_absent_only"] = metrics(study.y_dev[(~study.search)&~flags],prediction_sets[name][(~study.search)&~flags])
        if study.manifest.get("exclude_label_conflicts", False):
            detail["canonical_confirmation"] = canonical_metrics(
                study.y_dev[~study.search], prediction_sets[name][~study.search], groups[~study.search])
        comparisons.append(detail)
    improvements = [r["name"] for r in comparisons if r["name"] != "baseline" and not r["diagnostic"]
                    and r["delta_0fp"] >= 0 and r["delta_1fp"] >= 0
                    and (r["delta_0fp"] > 0 or r["delta_1fp"] > 0)]
    decision = ("Confirmation candidates preserving both recall budgets and improving at least one: "
                + ", ".join(improvements) if improvements else
                "No keyword finalist improves either confirmation recall budget without reducing the other.")
    best_search = max((r for r in study.summary["variants"].values() if not r.get("diagnostic", False)),
                      key=lambda r: (r["search"]["recall_1fp"], r["search"]["recall_0fp"], r["search"]["ap"]))["name"]
    report = dict(verification=verified,confirmation=comparisons,inputs=study.manifest,
                  decision=decision,best_search=best_search,promoted=False)
    atomic_write_json(root / "verified_summary.json",report)
    route=study.manifest.get("route", "filetypes/macho")
    cap=study.manifest.get("confirmation_group_cap",0)
    scope=study.manifest.get("scope") or "10% training/search; remaining development groups reserved for confirmation."
    if cap:
        scope+=f" Confirmation capped at {cap:,} groups by a separate label-blind hash."
    trees=study.summary['variants']['baseline']['tree_budget']
    lines=[f"# {route} keyword search", "", scope, "",
           f"| Configuration | Search 0 FP / 1 FP ({trees} trees, 2 seeds) | Confirmation 0 FP / 1 FP (400 trees, 4 seeds) | Δ confirmation 0 FP / 1 FP (pp) |",
           "|---|---:|---:|---:|"]
    for row in comparisons:
        name=row["name"]
        search=study.summary["variants"][name]["search"]
        lines.append(f"| {name} | {100*search['recall_0fp']:.2f}% / {100*search['recall_1fp']:.2f}% | {100*row['metrics']['recall_0fp']:.2f}% / {100*row['metrics']['recall_1fp']:.2f}% | {100*row['delta_0fp']:+.2f} / {100*row['delta_1fp']:+.2f} |")
    lines += ["",report["decision"],"", "The availability-only arm is a research diagnostic, not a deployable keyword feature.", ""]
    (root / "RESULTS.md").write_text("\n".join(lines))
    return study,confirmation


def word_audit(study,confirmation,name=None):
    """Training prevalence plus model use and SHAP direction; no causal claims."""
    candidates=[r for r in confirmation["variants"].values()
                if r["options"] and not r.get("diagnostic", False)]
    if name is None:
        name=max(candidates,key=lambda r:(r["search"]["recall_1fp"],r["search"]["recall_0fp"],r["search"]["ap"]))["name"]
    if name not in {r["name"] for r in candidates}:
        raise ValueError("word audit requires a confirmed keyword candidate")
    result=confirmation["variants"][name]
    directory=study.root / "confirmation" / name
    if "variant" in result:
        study.set_base(result["variant"])
    matrix,spec=study.layout(result["options"])
    names=spec.feature_names
    columns={name:i for i,name in enumerate(names)}
    usage=np.zeros(len(names),dtype=int)
    models=[]
    for seed in result["seeds"]:
        model=lgb.Booster(model_file=str(directory/f"seed_{seed}.txt"))
        usage+=model.feature_importance("split")
        models.append(model)
    total_bad=int(study.y_train.sum()); total_good=study.n-total_bad
    rows=[]
    for source in result["options"]:
        info,_=study.bank(source)
        for word,good,bad in zip(info["words"],info["goodware"],info["malware"]):
            feature=source+":"+word
            if feature not in columns:
                continue
            column=columns[feature]
            gp,bp=good/total_good,bad/total_bad
            if gp>=.1 and bp<=.05 and usage[column]>0:
                rows.append(dict(source=source,word=word,goodware=good,goodware_total=total_good,
                                 malware=bad,malware_total=total_bad,goodware_pct=100*gp,malware_pct=100*bp,
                                 learned_splits=int(usage[column]),column=column))
    rows.sort(key=lambda r:-r["learned_splits"])
    # Take deterministic small samples separately for present/absent words.
    for row in rows[:12]:
        column=row["column"]
        present=matrix[:study.n,column].toarray().ravel()!=0
        for state,mask in (("present",present),("absent",~present)):
            indices=np.flatnonzero(mask)
            indices=indices[np.linspace(0,len(indices)-1,min(100,len(indices)),dtype=int)]
            means=[]
            for model in models:
                shap=model.predict(matrix[indices],pred_contrib=True,num_threads=4)
                values=shap[:,column].toarray().ravel() if hasattr(shap,"toarray") else shap[:,column]
                means.append(float(np.mean(values)))
            row[f"mean_shap_{state}"]=float(np.mean(means))
    for row in rows:
        del row["column"]
    atomic_write_json(study.root / "goodware_words.json",dict(model=name,scope="Training-cohort prevalence; SHAP is average raw-margin contribution, not a causal effect.",words=rows))


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root",type=Path)
    parser.add_argument("--audit-model",help="confirmed keyword model to explain; defaults to best search score")
    args=parser.parse_args()
    study,confirmation=verify(args.root)
    word_audit(study,confirmation,args.audit_model)
