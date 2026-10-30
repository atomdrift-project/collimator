"""Guard paired confirmation diagnostics against mismatched inputs."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import scipy.sparse as sp


def load_script():
    path = Path(__file__).resolve().parents[1] / "scripts" / "confirm_trait_keywords.py"
    spec = importlib.util.spec_from_file_location("confirm_trait_keywords", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pair():
    common = dict(labels=np.array([1, 1, 0, 0]), ids=np.array([10, 20, 30, 40]), revision="reports")
    experiment = dict(database_revision="db", snapshot_max_id=100, feature_revision="code")
    def item(description):
        metrics = {"threshold_at_0fp": 0.7, "threshold_at_1fp": 0.5,
                   "recall_at_0fp": 1.0 if description else 0.5,
                   "recall_at_1fp": 1.0 if description else 0.5}
        return dict(**common,
                    scores=np.array([0.8, 0.9 if description else 0.2, 0.3, 0.6]),
                    spec=dict(feature_names=["base:x", "descword:download"] if description else ["base:x"],
                              keyword_vocabs={"descword": ["download"]} if description else {}),
                    matrix=sp.csr_matrix(np.ones((4, 2 if description else 1))),
                    model=SimpleNamespace(predict=lambda matrix, **kwargs: np.tile([0.1, 0.3, 0.0], (matrix.shape[0], 1))),
                    run=dict(experiment_spec=experiment, experiment_key="description" if description else "base",
                             train_rows=20, sampled_test_metrics=metrics))
    return item(False), item(True)


def test_changed_rows_distinguishes_recovered_lost_and_benign():
    script = load_script()
    base, desc = pair()
    assert script.changed_rows(base, desc, 0) == {
        "recovered_malware": [20], "lost_malware": [],
        "new_false_positives": [], "removed_false_positives": [],
    }
    desc["scores"] = np.array([0.1, 0.9, 0.8, 0.6])
    changes = script.changed_rows(base, desc, 0)
    assert changes["lost_malware"] == [10]
    assert changes["new_false_positives"] == [30]


def test_saved_model_checks_use_threshold_selectors_float32_precision(monkeypatch, tmp_path):
    script = load_script()
    directory, cache = tmp_path / "baseline", tmp_path / "cache"
    directory.mkdir()
    cache.mkdir()
    spec = {"feature_names": ["base:x"]}
    for path in (directory / "feature_spec.json", cache / "matrix_one_spec.json"):
        path.write_text(json.dumps(spec))
    np.savez(cache / "matrix_one.npz", y_test=np.array([1, 0]),
             test_row_ids=np.array([10, 20]), evaluation_revision=np.asarray("reports"))
    sp.save_npz(cache / "matrix_one_Xtest.npz", sp.csr_matrix([[1.0], [0.0]]))
    metrics = {f"{name}_at_{budget}fp": value
               for budget in (0, 1)
               for name, value in (("threshold", 0.9480187892913818), ("recall", 1.0))}
    monkeypatch.setattr(script, "latest_run", lambda _: {"sampled_test_metrics": metrics})
    monkeypatch.setattr(script.lgb, "Booster", lambda **kwargs: SimpleNamespace(
        predict=lambda *args, **kwargs: np.array([0.94801878, 0.2])))
    result = script.load_scores(directory, cache)
    assert result["scores"].dtype == np.float32


def test_summary_verifies_inputs_and_emits_signed_keyword_effects(monkeypatch, tmp_path):
    script = load_script()
    base, desc = pair()
    cache = tmp_path / "seed-43" / "cache"
    cache.mkdir(parents=True)
    (cache / "corpus_one.json").write_text("{}")
    monkeypatch.setattr(script, "load_scores", lambda directory, _: desc if directory.name == "descriptions" else base)
    summary = script.summarize(tmp_path, [43])
    assert summary["mean_deltas"]["recall_at_0fp"] == 0.5
    rows = summary["pairs"][0]["examples"]["rows"]
    recovered = next(row for row in rows if row["row_id"] == 20)
    assert recovered["keyword_effects"] == [dict(feature="descword:download", present=True, log_odds_contribution=0.3)]
    assert json.loads((tmp_path / "confirmation.json").read_text())["fixed_dev_rows_verified"]


@pytest.mark.parametrize("mismatch", ["ids", "labels", "revision", "base_values"])
def test_summary_rejects_unmatched_comparisons(monkeypatch, tmp_path, mismatch):
    script = load_script()
    base, desc = pair()
    if mismatch == "base_values":
        desc["matrix"][0, 0] = 2
    elif mismatch == "revision":
        desc["revision"] = "changed"
    else:
        desc[mismatch] = desc[mismatch][::-1]
    monkeypatch.setattr(script, "load_scores", lambda directory, _: desc if directory.name == "descriptions" else base)
    with pytest.raises(ValueError, match="(dev inputs|base dev feature values) changed|base dev feature values differ"):
        script.summarize(tmp_path, [43])
