"""Full-vector parity and report isolation for finding-summary reuse."""

import copy

import numpy as np
import pytest

from collimator import features as f


@pytest.fixture(autouse=True)
def reset_feature_configuration():
    f.feature_config_from_env.cache_clear()
    yield
    f.feature_config_from_env.cache_clear()


def report(modern=False):
    def file_entry(index, findings):
        item = {
            "id": index, "path": f"/file{index}", "type": "elf", "sz": 1000, "dp": index,
            "ms": {"binary": {"overall_entropy": 5.5}},
        }
        item["traits" if modern else "ts"] = findings
        return item

    findings = (
        [{"id": "objectives/evasion/process", "crit": 5, "conf": .9},
         {"id": "objectives/collection/files", "crit": 4, "conf": .7}]
        if modern else
        [{"i": "objectives/evasion/process", "l": 5, "c": .9},
         {"i": "objectives/collection/files", "l": 4, "c": .7}]
    )
    return {
        "v": "9" if modern else "4",
        "fs": [file_entry(0, findings), file_entry(1, copy.deepcopy(findings))],
    }


@pytest.mark.parametrize("modern", [False, True])
@pytest.mark.parametrize("depth", [2, 3, 5])
def test_complete_vectors_identical_with_and_without_reuse(monkeypatch, modern, depth):
    monkeypatch.setenv("COLLIMATOR_TRAIT_PATH_DEPTH", str(depth))
    sample = report(modern)
    spec = f.build_vocab([sample] * 35)
    spec.trait_path_depth = depth
    original = f._summarize_findings
    monkeypatch.setattr(f, "_summarize_findings", f._compute_finding_summary)
    expected = f.extract(sample, spec)
    monkeypatch.setattr(f, "_summarize_findings", original)
    assert np.array_equal(f.extract(sample, spec), expected)
    # A report object may be updated between calls. Never reuse a summary
    # from its preceding extraction.
    key = "traits" if modern else "ts"
    sample["fs"][0][key].clear()
    actual = f.extract(sample, spec)
    monkeypatch.setattr(f, "_summarize_findings", f._compute_finding_summary)
    assert np.array_equal(actual, f.extract(sample, spec))


def test_report_scope_released_on_error(monkeypatch):
    sample = report()
    spec = f.build_vocab([sample] * 35)

    def fail(*args, **kwargs):
        raise ValueError("injected extraction error")

    monkeypatch.setattr(f, "_extract_into_at_depth", fail)
    with pytest.raises(ValueError, match="injected"):
        f.extract(sample, spec)
    assert f._report_feature_cache.get() is None
    assert f._extract_trait_depth.get() is None
