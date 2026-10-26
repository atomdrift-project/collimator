"""Reports whose facts cleave reduced to a model-input profile (`fp`)."""

import json

import numpy as np
import pytest

from collimator.features import (
    FACT_PROFILE_MANIFEST,
    FactProfileError,
    FeatureSpec,
    check_fact_profile,
    extract,
    extract_all,
    feature_config_from_env,
)

PROFILE = json.loads(FACT_PROFILE_MANIFEST.read_text())["id"]

# Retained by the profile: a KEY_METRICS column, a trait path, an audited
# aggregate, and a family that reads no facts.
COVERED = [
    "metrics:binary_overall_entropy", "present:objectives/c2", "agg:max_crit", "filetype:elf",
]
# Read from facts the profile drops.
UNCOVERED = "metrics:binary_tiny_function_count"


def _spec(names: list[str]) -> FeatureSpec:
    return FeatureSpec(
        presence_vocab=["objectives/c2"],
        feature_names=names,
        total_features=len(names),
    )


def _report(fp: str | None = None) -> dict:
    report = {
        "v": "9",
        "files": [{
            "id": 0,
            "path": "/tmp/a.elf",
            "type": "elf",
            "size": 2048,
            "depth": 0,
            "traits": [{"id": "objectives/c2/beacon", "crit": 4, "conf": 1.0}],
            "facts": {"metrics": {"binary": {"overall_entropy": 6.5, "tiny_function_count": 12}}},
        }],
    }
    if fp is not None:
        report["fp"] = fp
    return report


@pytest.fixture
def extended_metrics(monkeypatch):
    monkeypatch.setenv("COLLIMATOR_EXTENDED_METRICS", "1")
    feature_config_from_env.cache_clear()
    yield
    feature_config_from_env.cache_clear()


def test_report_without_profile_extracts_every_feature(extended_metrics) -> None:
    spec = _spec([*COVERED, UNCOVERED])
    vec = extract(_report(), spec)
    assert vec[spec.feature_names.index(UNCOVERED)] == pytest.approx(np.log1p(12))


def test_profile_covering_the_layout_extracts_as_full_facts() -> None:
    spec = _spec(COVERED)
    np.testing.assert_array_equal(extract(_report(PROFILE), spec), extract(_report(), spec))


def test_profile_missing_a_feature_input_fails_naming_it() -> None:
    spec = _spec([*COVERED, UNCOVERED, "kv:pe.dll_name", "agg:static_import_count_log"])
    with pytest.raises(FactProfileError) as err:
        extract(_report(PROFILE), spec)
    message = str(err.value)
    assert "3 features" in message
    assert f"{UNCOVERED} (metric not retained)" in message
    assert "kv:pe.dll_name (family 'kv' not in profile)" in message
    assert "agg:static_import_count_log (no fact-dependency audit)" in message


def test_unknown_profile_fails() -> None:
    with pytest.raises(FactProfileError, match="unknown fact profile 'azoth-0000'"):
        extract(_report("azoth-0000"), _spec(COVERED))


def test_mixed_corpus_with_and_without_profile() -> None:
    spec = _spec(COVERED)
    X, _ = extract_all([_report(), _report(PROFILE)], [0, 1], spec, n_workers=1)
    assert X.shape == (2, len(COVERED))
    np.testing.assert_array_equal(X[0].toarray(), X[1].toarray())

    uncovered = _spec([*COVERED, UNCOVERED])
    with pytest.raises(FactProfileError):
        extract_all([_report(), _report(PROFILE)], [0, 1], uncovered, n_workers=1)


def test_pinned_azoth_allowlist_is_covered_by_the_profile() -> None:
    """Every feature the default training allowlist can keep survives reduction."""
    path = FACT_PROFILE_MANIFEST.with_name("azoth_allowed_features_importance10k.json")
    check_fact_profile(PROFILE, json.loads(path.read_text())["significant_features"])


def test_shipped_allowlist_is_covered_by_the_profile() -> None:
    path = FACT_PROFILE_MANIFEST.parent.parent / "allowed_features.json"
    check_fact_profile(PROFILE, json.loads(path.read_text()))
