"""Training metric transforms must survive export and environment changes."""
import json
import math

import numpy as np
import pytest

from collimator import features


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    import os
    for key in os.environ:
        if key.startswith("COLLIMATOR_"):
            monkeypatch.delenv(key)
    features.feature_config_from_env.cache_clear()
    yield
    features.feature_config_from_env.cache_clear()


def metric_spec(names):
    return features.FeatureSpec(feature_names=["metrics:" + n for n in names],
                                metric_vocab=names, total_features=len(names))


REPORT = {"files": [{"id": 0, "type": "pe", "size": 1024,
    "facts": {"metrics": {"text": {"max_inline_whitespace_run": 9},
                           "binary": {"string_count": 12, "function_count": 3},
                           "pe": {"timestamp_year": 2020, "entry_section": "packed"}}}}]}


@pytest.mark.parametrize("curated", [False, True])
def test_metric_transform_is_preserved_across_export_and_knob_changes(tmp_path, monkeypatch, curated):
    monkeypatch.setenv("COLLIMATOR_TEXT_METRICS_FULL", str(int(curated)))
    monkeypatch.setenv("COLLIMATOR_EXTENDED_METRICS", "1")
    features.feature_config_from_env.cache_clear()
    spec = metric_spec(["text_max_inline_whitespace_run", "binary_function_count"])
    before = features.extract(REPORT, spec)
    spec.bind_metric_contract()
    assert spec.metric_transforms["text_max_inline_whitespace_run"] == ("log1p_abs" if curated else "identity")
    path = tmp_path / "spec.json"
    spec.save(path)
    monkeypatch.setenv("COLLIMATOR_TEXT_METRICS_FULL", str(int(not curated)))
    features.feature_config_from_env.cache_clear()
    loaded = features.FeatureSpec.load(path)
    np.testing.assert_array_equal(features.extract(REPORT, loaded), before)
    assert before[0] == np.float32(math.log1p(9) if curated else 9)


def test_derived_metrics_and_reference_year_survive_export(tmp_path, monkeypatch):
    monkeypatch.setenv("COLLIMATOR_METRIC_RATIO_FEATURES", "1")
    monkeypatch.setenv("COLLIMATOR_PE_FORMAT_FLAGS", "1")
    monkeypatch.setenv("COLLIMATOR_PE_TEMPORAL_ANOMALY", "1")
    monkeypatch.setenv("COLLIMATOR_METRIC_CORRELATION_PAIRS", "binary.string_count*binary.function_count")
    features.feature_config_from_env.cache_clear()
    spec = metric_spec(["derived_string_per_function", "pe_year_distance", "pe_entry_section_nontext",
                        "derived_corr_binary_string_count_x_binary_function_count"])
    before = features.extract(REPORT, spec)
    spec.bind_metric_contract()
    path = tmp_path / "spec.json"
    spec.save(path)
    for knob in ("METRIC_RATIO_FEATURES", "PE_FORMAT_FLAGS", "PE_TEMPORAL_ANOMALY", "METRIC_CORRELATION_PAIRS"):
        monkeypatch.delenv("COLLIMATOR_" + knob)
    features.feature_config_from_env.cache_clear()
    loaded = features.FeatureSpec.load(path)
    np.testing.assert_array_equal(features.extract(REPORT, loaded), before)
    loaded.metric_reference_year = 2025
    assert features.extract(REPORT, loaded)[1] == np.float32(math.log1p(5))
    assert before[0] == 4 and before[2] == 1 and before[3] == 36


def test_saving_legacy_spec_does_not_guess_transforms(tmp_path):
    spec = metric_spec(["text_max_inline_whitespace_run"])
    path = tmp_path / "spec.json"
    spec.save(path)
    assert "metric_transforms" not in json.loads(path.read_text())
    assert features.FeatureSpec.load(path).metric_transforms is None


@pytest.mark.parametrize("transform", [None, "log10"])
def test_incomplete_or_unknown_contract_is_rejected(transform):
    spec = metric_spec(["text_max_inline_whitespace_run"])
    spec.metric_transforms = {} if transform is None else {"text_max_inline_whitespace_run": transform}
    with pytest.raises(ValueError, match="metric transform"):
        features.extract(REPORT, spec)
