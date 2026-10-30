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
OLD_PROFILE = "azoth-1fbfcdb8a8ed5902"

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


def test_explicit_profile_check_still_fails_naming_missing_inputs() -> None:
    spec = _spec([*COVERED, UNCOVERED, "kv:pe.dll_name", "agg:static_import_count_log"])
    with pytest.raises(FactProfileError) as err:
        check_fact_profile(OLD_PROFILE, spec.feature_names)
    message = str(err.value)
    assert "3 features" in message
    assert f"{UNCOVERED} (metric not retained)" in message
    assert "kv:pe.dll_name (family 'kv' not in profile)" in message
    assert "agg:static_import_count_log (no fact-dependency audit)" in message


def test_explicit_unknown_profile_check_fails() -> None:
    with pytest.raises(FactProfileError, match="unknown fact profile 'azoth-0000'"):
        check_fact_profile("azoth-0000", COVERED)


@pytest.mark.parametrize("profile", [OLD_PROFILE, "azoth-0000"])
def test_incomplete_profile_keeps_present_metrics_and_defaults_absent_ones(
    extended_metrics, caplog, profile,
) -> None:
    spec = _spec([*COVERED, UNCOVERED])
    report = _report(profile)
    # A contract mismatch alone must not discard facts that are present.
    present = extract(report, spec)
    assert present[-1] == pytest.approx(np.log1p(12))
    del report["files"][0]["facts"]["metrics"]["binary"]["tiny_function_count"]
    absent = extract(report, spec)
    np.testing.assert_array_equal(absent[:-1], present[:-1])
    assert absent[-1] == 0
    assert "keeping the sample" in caplog.text


def test_historical_profile_does_not_gain_newly_retained_inputs() -> None:
    check_fact_profile(OLD_PROFILE, COVERED)
    for name in ("symbol:VirtualAlloc", "metrics:binary_is_pie"):
        check_fact_profile(PROFILE, [name])
        with pytest.raises(FactProfileError, match="omits inputs"):
            check_fact_profile(OLD_PROFILE, [name])


def test_discovered_metrics_and_categorical_inputs_are_retained(monkeypatch) -> None:
    monkeypatch.setenv("COLLIMATOR_EXTENDED_METRICS", "1")
    monkeypatch.setenv("COLLIMATOR_KV_VOCAB", "1")
    feature_config_from_env.cache_clear()
    try:
        report = _report()
        report["files"][0]["facts"]["metrics"]["fixture"] = {
            "new_count": 7, "kind": "native", "enabled": True,
        }
        spec = _spec(["metrics:fixture_new_count", "kv:fixture.kind=native",
                      "kv:fixture.enabled=true"])
        full = extract(report, spec)
        report["fp"] = PROFILE
        np.testing.assert_array_equal(extract(report, spec), full)
        np.testing.assert_allclose(full, [np.log1p(7), 1, 1])
        with pytest.raises(FactProfileError):
            check_fact_profile(OLD_PROFILE, spec.feature_names)
        with pytest.raises(FactProfileError):
            check_fact_profile(PROFILE, ["metrics:derived_unaudited"])
    finally:
        feature_config_from_env.cache_clear()


def test_symbols_survive_new_profile_extraction(monkeypatch) -> None:
    monkeypatch.setenv("COLLIMATOR_SYMBOL_VOCAB", "1")
    feature_config_from_env.cache_clear()
    try:
        report = _report()
        report["files"][0]["facts"].update({
            "imp": [["kernel32.dll", "VirtualAlloc"]],
            "exp": [["exported"]], "funcs": [["function", 12]],
            "tgt": ["object.call"], "mbr": ["object.member"],
        })
        tokens = ["VirtualAlloc", "kernel32.dll!VirtualAlloc", "exported",
                  "function", "object.call", "object.member"]
        spec = _spec([f"symbol:{token}" for token in tokens])
        spec.symbol_vocab = tokens
        full = extract(report, spec)
        report["fp"] = PROFILE
        np.testing.assert_array_equal(extract(report, spec), full)
        np.testing.assert_array_equal(full, np.ones(len(tokens)))
    finally:
        feature_config_from_env.cache_clear()


def test_severity_features_need_no_omitted_facts(monkeypatch) -> None:
    monkeypatch.setenv("COLLIMATOR_SEVERITY_FRACTION_FEATURES", "1")
    feature_config_from_env.cache_clear()
    try:
        spec = _spec(["agg:crit3_finding_fraction", "agg:crit4_finding_fraction",
                      "agg:hostile_finding_fraction", "agg:severe_to_mundane_ratio",
                      "agg:crit4_present"])
        full = extract(_report(), spec)
        for profile in (OLD_PROFILE, PROFILE):
            np.testing.assert_array_equal(extract(_report(profile), spec), full)
        assert full.any()
    finally:
        feature_config_from_env.cache_clear()


@pytest.mark.parametrize("n_workers", [1, 2])
def test_mixed_corpus_with_and_without_profile(extended_metrics, caplog, n_workers) -> None:
    spec = _spec(COVERED)
    X, _ = extract_all([_report(), _report(PROFILE)], [0, 1], spec, n_workers=n_workers)
    assert X.shape == (2, len(COVERED))
    np.testing.assert_array_equal(X[0].toarray(), X[1].toarray())

    uncovered = _spec([*COVERED, UNCOVERED])
    reduced = _report(OLD_PROFILE)
    del reduced["files"][0]["facts"]["metrics"]["binary"]["tiny_function_count"]
    X, labels = extract_all(
        [_report(), reduced, reduced], [0, 1, 0], uncovered, n_workers=n_workers,
    )
    assert X.shape == (3, len(uncovered.feature_names))
    np.testing.assert_array_equal(labels, [0, 1, 0])
    assert X[0, -1] == pytest.approx(np.log1p(12))
    np.testing.assert_array_equal(X[1:, -1].toarray(), [[0], [0]])
    for row in (1, 2):
        np.testing.assert_array_equal(X[row, :-1].toarray(), X[0, :-1].toarray())
    if n_workers == 1:
        assert caplog.text.count("keeping the sample") == 1


def test_pinned_azoth_allowlist_is_covered_by_the_profile() -> None:
    """Every feature the default training allowlist can keep survives reduction."""
    path = FACT_PROFILE_MANIFEST.with_name("azoth_allowed_features_importance10k.json")
    check_fact_profile(PROFILE, json.loads(path.read_text())["significant_features"])


def test_shipped_allowlist_is_covered_by_the_profile() -> None:
    path = FACT_PROFILE_MANIFEST.parent.parent / "allowed_features.json"
    check_fact_profile(PROFILE, json.loads(path.read_text()))


def _raise_profile_error_in_worker():
    check_fact_profile(OLD_PROFILE, [UNCOVERED])


def test_worker_profile_error_survives_parent_with_older_features_module(monkeypatch):
    import concurrent.futures
    import multiprocessing
    from collimator import features

    # Reproduce the old parent's module namespace: the worker starts fresh,
    # but the parent never imported the newly added features exception class.
    monkeypatch.delattr(features, 'FactProfileError')
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=1, mp_context=multiprocessing.get_context('spawn'),
    ) as pool:
        with pytest.raises(FactProfileError, match='metric not retained'):
            pool.submit(_raise_profile_error_in_worker).result(timeout=20)
        # A validation error must not corrupt the transport or break the pool.
        assert pool.submit(abs, -7).result(timeout=20) == 7
