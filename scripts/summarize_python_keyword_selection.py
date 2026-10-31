#!/usr/bin/env python3
"""Verify saved Python selection models/predictions and summarize paired gains."""
import argparse
import json
from pathlib import Path
import sys

import lightgbm as lgb
import numpy as np
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from collimator.bundle import atomic_write_json
from collimator.thresholds import recall_at_fp_budget
from keyword_route_controls import matrix_digest
from keyword_python_selection import rank_words, selection_rows, token_batches


def main(root):
    study = json.loads((root / "comparison.json").read_text())
    base_spec = json.loads((root / "base_spec.json").read_text())
    base = sp.load_npz(root / "inputs/base.npz")
    assert matrix_digest(base) == study["inputs"]["base_sha256"]
    with np.load(root / "inputs/rows.npz") as rows:
        y = rows["dev_labels"]
        y_train = rows["train_labels"]
        n = len(y_train)
        selected = rows["selection_rows"]
        np.testing.assert_array_equal(selected, selection_rows(y_train))
    with np.load(root / "baseline/dev_predictions.npz") as saved:
        baseline = saved["ensemble"]
    sources = {}
    verified = []
    for name, result in study["variants"].items():
        spec = json.loads((root / name / "feature_spec.json").read_text())
        assert spec["feature_names"][:base_spec["total_features"]] == base_spec["feature_names"]
        matrix = base
        for source, words in spec["keyword_vocabs"].items():
            if source not in sources:
                info = json.loads((root / "inputs" / f"{source}.json").read_text())
                keywords = sp.load_npz(root / "inputs" / f"{source}.npz")
                assert matrix_digest(keywords) == info["matrix_sha256"]
                for label, field in ((0, "goodware"), (1, "malware")):
                    counts = np.asarray(keywords[selected[y_train[selected] == label]].sum(axis=0)).ravel()
                    np.testing.assert_array_equal(counts, info[field])
                sources[source] = info, keywords
            info, keywords = sources[source]
            _, method, cap = result.get("selection_parent", name).split("-")
            ranking = rank_words(info["words"], np.array(info["malware"]), np.array(info["goodware"]),
                                 info["totals"], method)
            columns = sorted(ranking[:int(cap)])
            assert words == [info["words"][i] for i in columns]
            assert spec["feature_names"][base_spec["total_features"]:] == [f"{source}:{word}" for word in words]
            matrix = sp.hstack([base, keywords[:, columns]], format="csr")
        assert matrix.shape[1] == spec["total_features"]
        assert matrix_digest(matrix[:n]) == result["train_sha256"]
        assert matrix_digest(matrix[n:]) == result["dev_sha256"]
        scores = []
        with np.load(root / name / "dev_predictions.npz") as saved:
            assert np.array_equal(saved["labels"], y)
            for member in result["seeds"]:
                model = lgb.Booster(model_file=str(root / name / f"seed_{member['seed']}.txt"))
                prediction = np.asarray(model.predict(matrix[n:], num_threads=4), dtype=np.float32)
                np.testing.assert_array_equal(prediction, saved[f"seed_{member['seed']}"])
                scores.append(prediction.astype(np.float64))
            ensemble = np.mean(scores, axis=0).astype(np.float32)
            np.testing.assert_array_equal(ensemble, saved["ensemble"])
        changes = {}
        for budget in (0, 1):
            recall, threshold, _ = recall_at_fp_budget(y, ensemble, budget)
            _, old_threshold, _ = recall_at_fp_budget(y, baseline, budget)
            np.testing.assert_allclose(recall, result[f"recall_at_{budget}fp"])
            detected = ensemble >= threshold if threshold is not None else np.zeros(len(y), dtype=bool)
            old_detected = baseline >= old_threshold if old_threshold is not None else np.zeros(len(y), dtype=bool)
            changes[str(budget)] = dict(recovered=int(np.sum((y == 1) & detected & ~old_detected)),
                                       lost=int(np.sum((y == 1) & ~detected & old_detected)))
        verified.append(dict(**result, changes=changes, verified=True))
        print(f"Verified {name}", flush=True)
    atomic_write_json(root / "verified_summary.json", dict(inputs=study["inputs"], variants=verified))
    present = np.array([bool(row["contextword"]) for row in token_batches(
        [str(p)[:-len(".json.gz")] for p in sorted((root / "inputs").glob("batch-*.json.gz"))])])
    coverage = {}
    for partition, labels, available in (("train", y_train, present[:n]), ("dev", y, present[n:])):
        coverage[partition] = {}
        for label, name in ((0, "goodware"), (1, "malware")):
            total, count = int(np.sum(labels == label)), int(np.sum(available[labels == label]))
            coverage[partition][name] = dict(total=total, context_present=count, percent=100*count/total)
    atomic_write_json(root / "context_coverage.json", coverage)
    baseline_result = study["variants"]["baseline"]
    lines = ["# Python keyword selection screen", "", "Two-seed ensemble recall on the saved 10% dev cohort. "
             "Fresh reports and a fixed historical base vocabulary; compare within this screen.", "",
             "| Variant | Keywords | Recall at 0 FP | Recall at 1 FP | Δ 0 FP (pp) | Δ 1 FP (pp) | Fit seconds |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for result in verified:
        r0, r1 = result["recall_at_0fp"], result["recall_at_1fp"]
        d0, d1 = [100*(result[f"recall_at_{k}fp"]-baseline_result[f"recall_at_{k}fp"]) for k in (0,1)]
        lines.append(f"| {result['name']} | {result['keywords']} | {100*r0:.2f}% | {100*r1:.2f}% | {d0:+.2f} | {d1:+.2f} | {result['seconds']:.1f} |")
    lines += ["", "Selection uses only the intersection of both seeds' fitting rows. "
              "No internal holdout or dev labels enter frequency counts or supervised ranking. "
              "Minimum document support is five; binary features and all other training settings are held fixed "
              "in the selection screen. The follow-up changes only min_child_samples to 300 (leaf300) "
              "or reg_lambda to 5 (lambda5), with matching baseline controls.", "",
              "Balanced MI uses Jeffreys-smoothed class-conditional presence rates and equal class priors; "
              "it rewards association with either class. Each source is evaluated separately.", "",
              "These are exploratory dev results, not an independent confirmation. "
              "Context coverage remains confounded with class; no model is promoted.", "",
              "Every saved model prediction, selected vocabulary, and train/dev matrix hash was verified.", ""]
    (root / "RESULTS.md").write_text("\n".join(lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    main(parser.parse_args().root)
