"""Controls must change keyword sources without changing rows or sampling."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import scipy.sparse as sp


def script():
    path = Path(__file__).resolve().parents[1] / "scripts/keyword_route_controls.py"
    spec = importlib.util.spec_from_file_location("keyword_route_controls", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_commands_use_all_sampled_rows_and_two_retained_seeds(tmp_path):
    module = script()
    args = SimpleNamespace(db="unused", seed=43, trees=180)
    for name, flags in module.VARIANTS.items():
        command = module.command(args, "java_class", name, tmp_path)
        assert "EXP_COLSAMPLE_BYTREE=1" in command
        assert "EXP_TRAIN_SAMPLES=0" in command
        assert "EXP_MAX_TEST_SAMPLES=0" in command
        assert "EXP_MIN_MALWARE_SCORE=0" in command
        assert "EXP_SAVE_ALL_SEEDS=1" in command
        assert "EXP_SEED_SEARCH_K=2" in command
        assert f"EXP_RULE_KEYWORDS={flags[0]}" in command
        assert f"EXP_DESCRIPTION_KEYWORDS={flags[1]}" in command


def test_pooling_and_context_are_independent_experiment_arms(tmp_path):
    module = script()
    args = SimpleNamespace(db="unused", seed=43, trees=180)
    pooled = module.command(args, "python", "pooled", tmp_path)
    assert "EXP_RULE_DESCRIPTION_KEYWORDS=1" in pooled
    assert "EXP_CONTEXT_KEYWORDS=0" in pooled
    context = module.command(args, "python", "context", tmp_path)
    assert "EXP_CONTEXT_KEYWORDS=1" in context
    assert "EXP_RULE_DESCRIPTION_KEYWORDS=0" in context
    assert "EXP_FULL_RULE_KEYWORDS=0" in context
    separate = module.command(args, "python", "hierarchy_descriptions", tmp_path)
    assert "EXP_FULL_RULE_KEYWORDS=1" in separate
    assert "EXP_DESCRIPTION_KEYWORDS=1" in separate
    assert "EXP_RULE_DESCRIPTION_KEYWORDS=0" in separate
    assert "EXP_CONTEXT_KEYWORDS=0" in separate
    args.keyword_vocab_max = 25000
    larger = module.command(args, "python", "context", tmp_path)
    assert "EXP_KEYWORD_VOCAB_MAX=25000" in larger


def test_digest_matches_equivalent_sparse_storage_and_detects_changes():
    module = script()
    left = sp.csr_matrix([[0., 1.], [2., 0.]])
    right = left.tocoo().tocsr()
    right.indices = right.indices.astype(np.int64)
    right.indptr = right.indptr.astype(np.int64)
    assert module.matrix_digest(left) == module.matrix_digest(right)
    right.data[0] = 3
    assert module.matrix_digest(left) != module.matrix_digest(right)


def test_seed_deltas_use_individual_saved_probabilities(tmp_path):
    module = script()
    for name, scores in (("baseline", [0.8, 0.2, 0.4, 0.6]), ("ids", [0.8, 0.9, 0.3, 0.6])):
        directory = tmp_path / name
        directory.mkdir()
        np.savez(directory / "dev_predictions.npz", labels=np.array([1, 1, 0, 0]), seed_43=np.array(scores))
    baseline = {"seeds": [dict(seed=43,recall_at_0fp=.5,recall_at_1fp=.5)]}
    result = {"seeds": [dict(seed=43,recall_at_0fp=1.,recall_at_1fp=1.)]}
    module.paired_changes(tmp_path, baseline, "ids", result)
    assert result["seeds"][0]["delta_at_0fp"] == .5
    assert result["seeds"][0]["changes_at_0fp"] == dict(recovered=1,lost=0)


def test_no_usable_threshold_means_no_detections(tmp_path):
    module = script()
    for name, scores in (("baseline", [1., 1.]), ("ids", [.8, .2])):
        directory = tmp_path / name
        directory.mkdir()
        np.savez(directory / "dev_predictions.npz", labels=np.array([1, 0]), seed_43=np.array(scores))
    baseline = {"seeds": [dict(seed=43,recall_at_0fp=0.,recall_at_1fp=1.)]}
    result = {"seeds": [dict(seed=43,recall_at_0fp=1.,recall_at_1fp=1.)]}
    module.paired_changes(tmp_path, baseline, "ids", result)
    assert result["seeds"][0]["changes_at_0fp"] == dict(recovered=1,lost=0)
