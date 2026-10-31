"""Per-model keyword controls must not use calibration or CV validation labels."""
import numpy as np
import pytest
import scipy.sparse as sp

from collimator import features, keywords, train


@pytest.fixture(autouse=True)
def clean_settings(monkeypatch):
    import os
    for key in list(os.environ):
        if key.startswith("COLLIMATOR_") and "KEYWORD" in key:
            monkeypatch.delenv(key)
    features.feature_config_from_env.cache_clear()
    yield
    features.feature_config_from_env.cache_clear()


def test_source_overrides_and_invalid_settings(monkeypatch):
    monkeypatch.setenv("COLLIMATOR_KEYWORD_SELECTION", "balanced_mi")
    monkeypatch.setenv("COLLIMATOR_KEYWORD_VOCAB_MAX", "5000")
    monkeypatch.setenv("COLLIMATOR_CONTEXT_KEYWORD_SELECTION", "frequency")
    monkeypatch.setenv("COLLIMATOR_CONTEXT_KEYWORD_VOCAB_MAX", "1000")
    monkeypatch.setenv("COLLIMATOR_CONTEXT_KEYWORD_MIN_FREQ", "20")
    settings = keywords.settings_from_env()
    assert settings["ruletextword"]["selection"] == "balanced_mi"
    assert settings["ruletextword"]["vocab_max"] == 5000
    assert settings["contextword"]["selection"] == "frequency"
    assert settings["contextword"]["vocab_max"] == 1000
    assert settings["contextword"]["min_freq"] == 20
    monkeypatch.setenv("COLLIMATOR_CONTEXT_KEYWORD_SELECTION", "nonsense")
    with pytest.raises(ValueError, match="invalid keyword selection"):
        keywords.settings_from_env()


def test_discovery_is_bounded_and_source_caps_are_independent(monkeypatch):
    from collections import Counter
    monkeypatch.setenv("COLLIMATOR_KEYWORD_SELECTION", "balanced_mi")
    monkeypatch.setenv("COLLIMATOR_KEYWORD_VOCAB_MAX", "1")
    monkeypatch.setenv("COLLIMATOR_KEYWORD_CANDIDATE_MAX", "3")
    monkeypatch.setenv("COLLIMATOR_CONTEXT_KEYWORD_SELECTION", "frequency")
    monkeypatch.setenv("COLLIMATOR_CONTEXT_KEYWORD_VOCAB_MAX", "2")
    counts = Counter(dict(alpha=9, beta=8, gamma=7, delta=6))
    spec = features._add_keyword_vocab(features.FeatureSpec(), dict(ruletextword=counts, contextword=counts))
    assert spec.keyword_vocabs["ruletextword"] == ["alpha", "beta", "gamma"]
    assert spec.keyword_vocabs["contextword"] == ["alpha", "beta"]
    assert spec.abi_version == 23


@pytest.mark.parametrize("sparse", [False, True])
def test_class_selection_is_symmetric_does_not_mutate_and_preserves_layout(monkeypatch, sparse):
    monkeypatch.setenv("COLLIMATOR_KEYWORD_SELECTION", "balanced_mi")
    monkeypatch.setenv("COLLIMATOR_KEYWORD_VOCAB_MAX", "2")
    monkeypatch.setenv("COLLIMATOR_KEYWORD_MIN_FREQ", "2")
    y = np.array([0]*20 + [1]*20)
    matrix = np.column_stack([np.arange(40), np.ones(40), y, 1-y, np.eye(1,40).ravel()]).astype(np.float32)
    names = ["base", "ruleword:common", "ruleword:bad", "ruleword:good", "ruleword:rare"]
    original = matrix.copy()
    if sparse:
        matrix = sp.csr_matrix(matrix)
    masked, stats = keywords.select_for_fit(matrix, y, names)
    reverse, _ = keywords.select_for_fit(matrix, 1-y, names)
    actual = masked.toarray() if sparse else masked
    np.testing.assert_array_equal(actual[:,[0,2,3]], original[:,[0,2,3]])
    assert not actual[:,[1,4]].any()
    np.testing.assert_array_equal(actual, reverse.toarray() if sparse else reverse)
    np.testing.assert_array_equal(matrix.toarray() if sparse else matrix, original)
    assert stats["ruleword"]["selected"] == 2
    assert stats["ruleword"]["eligible"] == 3


def test_every_cv_and_final_selector_sees_only_its_fitting_rows(monkeypatch):
    from sklearn.model_selection import StratifiedKFold, train_test_split
    monkeypatch.setenv("COLLIMATOR_KEYWORD_SELECTION", "balanced_mi")
    monkeypatch.setenv("COLLIMATOR_KEYWORD_VOCAB_MAX", "1")
    rng = np.random.default_rng(4)
    y = rng.integers(0, 2, 400)
    x = sp.csr_matrix(np.column_stack([np.arange(400), y, rng.integers(0, 2, 400)]).astype(np.float32))
    calls = []
    original = keywords.select_for_fit

    def capture(matrix, labels, names, settings=None):
        calls.append(set(matrix[:,0].toarray().ravel().astype(int)))
        return original(matrix, labels, names, settings)

    monkeypatch.setattr(keywords, "select_for_fit", capture)
    result = train.train(x, y, train.TrainConfig(learner="azoth", device="cpu", n_folds=3,
                         n_estimators=5, num_leaves=4, min_child_samples=5, min_child_weight=0,
                         seed=43, holdout_fraction=.2, num_threads=1),
                         feature_names=["base", "ruleword:signal", "ruleword:noise"])
    tv, holdout = train_test_split(np.arange(400), stratify=y, test_size=.2, random_state=43)
    expected = [set(tv[a]) for a, _ in StratifiedKFold(3, shuffle=True, random_state=43).split(tv,y[tv])]
    assert calls == expected + [set(tv)]
    assert all(not rows.intersection(holdout) for rows in calls)
    assert result.keyword_selection["ruleword"]["selected"] == 1
    # A rejected column can contain arbitrary inference values: no tree uses it.
    probe = x.toarray()
    before = result.model.predict_proba(probe)
    probe[:,2] = 1e6
    np.testing.assert_array_equal(result.model.predict_proba(probe), before)


def test_unmasked_runtime_input_matches_onnx_after_supervised_selection(monkeypatch, tmp_path):
    lgb = pytest.importorskip("lightgbm")
    ort = pytest.importorskip("onnxruntime")
    pytest.importorskip("onnxmltools")
    from collimator.export import export_lightgbm_onnx
    monkeypatch.setenv("COLLIMATOR_KEYWORD_SELECTION", "balanced_mi")
    monkeypatch.setenv("COLLIMATOR_KEYWORD_VOCAB_MAX", "1")
    y = np.array([0]*100+[1]*100)
    x = np.column_stack([y, np.arange(200)%2]).astype(np.float32)
    model = lgb.LGBMClassifier(n_estimators=8, num_leaves=4, min_child_samples=5, n_jobs=1, verbosity=-1)
    train._fit_model(model, sp.csr_matrix(x), y, keyword_feature_names=["contextword:signal", "contextword:noise"])
    path = tmp_path / "model.onnx"
    assert export_lightgbm_onnx(model.booster_, 2, path)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    session = ort.InferenceSession(str(path), sess_options=options, providers=["CPUExecutionProvider"])
    result = session.run(None, {session.get_inputs()[0].name: x})[1][:,1]
    np.testing.assert_allclose(result, model.predict_proba(x)[:,1], atol=1e-6)
