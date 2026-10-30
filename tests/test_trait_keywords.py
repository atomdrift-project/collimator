"""Keyword discovery must use training documents and survive spec round trips."""

import json
from dataclasses import asdict, replace

import numpy as np
import pytest

from collimator import data, features as f


@pytest.fixture(autouse=True)
def config(monkeypatch):
    for key in ("RULE_KEYWORDS", "DESCRIPTION_KEYWORDS", "DISABLE_FEATURE_GROUPS",
                "ALLOWED_FEATURES_FILE"):
        monkeypatch.delenv(f"COLLIMATOR_{key}", raising=False)
    monkeypatch.setenv("COLLIMATOR_KEYWORD_MIN_FREQ", "1")
    f.feature_config_from_env.cache_clear()
    f.allowed_features.cache_clear()
    yield
    f.feature_config_from_env.cache_clear()
    f.allowed_features.cache_clear()


def report(relative="curl_download_post", desc="Download via HTTP POST", conf=1.0):
    return {"files": [{"type": "python", "traits": [
        {"id": f"micro-behaviors/network::{relative}",
         "desc": desc, "conf": conf, "crit": 2},
    ]}]}


def test_sources_are_separate_and_extract_without_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("COLLIMATOR_RULE_KEYWORDS", "1")
    monkeypatch.setenv("COLLIMATOR_DESCRIPTION_KEYWORDS", "1")
    spec = f.build_vocab([report()], n_workers=1)
    assert spec.keyword_vocabs == {
        "ruleword": ["curl", "download", "post"],
        "descword": ["download", "http", "post", "via"],
    }
    assert spec.abi_version == spec.version == 22
    assert spec.base_feature_abi == 20
    path = tmp_path / "spec.json"
    spec.save(path)
    monkeypatch.delenv("COLLIMATOR_RULE_KEYWORDS")
    monkeypatch.delenv("COLLIMATOR_DESCRIPTION_KEYWORDS")
    f.feature_config_from_env.cache_clear()
    loaded = f.FeatureSpec.load(path)
    np.testing.assert_array_equal(f.extract(report(), spec), f.extract(report(), loaded))
    vec = f.extract(report(), loaded)
    for name in ("ruleword:curl", "descword:http"):
        assert vec[loaded.feature_names.index(name)] == 1
    changed = f.extract(report("wget_upload", "Upload via FTP"), loaded)
    assert changed[loaded.feature_names.index("ruleword:curl")] == 0
    assert changed[loaded.feature_names.index("descword:http")] == 0


def test_frequency_is_per_document_not_per_finding_or_archive_member(monkeypatch):
    monkeypatch.setenv("COLLIMATOR_RULE_KEYWORDS", "1")
    monkeypatch.setenv("COLLIMATOR_KEYWORD_MIN_FREQ", "2")
    monkeypatch.setenv("COLLIMATOR_KEYWORD_VOCAB_MAX", "2")
    repeated = report("rare_rare_common")
    repeated["files"] *= 5
    spec = f.build_vocab([repeated, report("zebra_common_alpha"), report("alpha_zebra")], 1)
    # All three have frequency 2. Lexical ties, then cap; repeated rare loses.
    assert spec.keyword_vocabs["ruleword"] == ["alpha", "common"]


@pytest.mark.parametrize("desc", [None, "", "  ", 7])
def test_missing_description_is_an_error_only_for_description_source(monkeypatch, desc):
    monkeypatch.setenv("COLLIMATOR_RULE_KEYWORDS", "1")
    assert f.build_vocab([report(desc=desc)], 1).keyword_vocabs["ruleword"]
    monkeypatch.setenv("COLLIMATOR_DESCRIPTION_KEYWORDS", "1")
    f.feature_config_from_env.cache_clear()
    with pytest.raises(ValueError, match="curl_download_post"):
        f.build_vocab([report(desc=desc)], 1)
    # Below-confidence findings don't contribute either source.
    spec = f.build_vocab([report(desc=desc, conf=0.1)], 1)
    assert spec.keyword_vocabs == {"ruleword": [], "descword": []}


def test_missing_description_also_fails_at_prediction(monkeypatch):
    monkeypatch.setenv("COLLIMATOR_DESCRIPTION_KEYWORDS", "1")
    spec = f.build_vocab([report()], 1)
    with pytest.raises(ValueError, match="missing descriptions"):
        f.extract(report(desc=None), spec)


def test_pruning_description_columns_removes_description_dependency(monkeypatch):
    monkeypatch.setenv("COLLIMATOR_RULE_KEYWORDS", "1")
    monkeypatch.setenv("COLLIMATOR_DESCRIPTION_KEYWORDS", "1")
    spec = f.build_vocab([report()], 1)
    names = [name for name in spec.feature_names if not name.startswith("descword:")]
    pruned = replace(spec, feature_names=names, total_features=len(names))
    vec = f.extract(report(desc=None), pruned)
    assert vec[names.index("ruleword:curl")] == 1


def test_legacy_fields_tokenization_and_leaf_fallback():
    files = [{"ts": [{"i": "taxonomy/path/CURL-download_post2", "d": "HTTP POST",
                       "c": 1.0, "l": 2}]}]
    assert f._report_keywords(files, ("ruleword", "descword")) == {
        "ruleword": {"curl", "download", "post2"}, "descword": {"http", "post"},
    }
    assert f._keyword_words("curl_download-post + 123 x") == {"curl", "download", "post"}


def test_db_discovery_reads_only_supplied_training_ids(monkeypatch):
    monkeypatch.setenv("COLLIMATOR_RULE_KEYWORDS", "1")
    calls = []
    def fetch(_db, ids):
        calls.extend(ids)
        return {rid: {"cleave_result": json.dumps(report("benign" if rid == 1 else "malicious"))}
                for rid in ids}
    monkeypatch.setattr(data, "fetch_cleave_results", fetch)
    monkeypatch.setattr(f, "_build_vocab_from_db", lambda *a, **kw: f.FeatureSpec())
    spec = f.build_vocab_from_db("unused", [(1, 0), (2, 1)], n_workers=1)
    assert calls == [1, 2]
    assert spec.keyword_vocabs["ruleword"] == ["benign", "malicious"]


def test_allowlist_and_group_disable(monkeypatch, tmp_path):
    monkeypatch.setenv("COLLIMATOR_RULE_KEYWORDS", "1")
    path = tmp_path / "allow.json"
    path.write_text(json.dumps(["agg:max_crit", "ruleword:curl"]))
    monkeypatch.setenv("COLLIMATOR_ALLOWED_FEATURES_FILE", str(path))
    spec = f.build_vocab([report()], 1)
    assert spec.keyword_vocabs == {"ruleword": ["curl"]}
    monkeypatch.setenv("COLLIMATOR_DISABLE_FEATURE_GROUPS", "ruleword")
    f.feature_config_from_env.cache_clear()
    disabled = f.build_vocab([report()], 1)
    assert disabled.keyword_vocabs == {}
    assert disabled.abi_version == f.MODEL_ABI_VERSION


def test_config_identity_and_default_cap(monkeypatch):
    before = asdict(f.feature_config_from_env())
    assert before["keyword_vocab_max"] == 10000
    monkeypatch.setenv("COLLIMATOR_RULE_KEYWORDS", "1")
    f.feature_config_from_env.cache_clear()
    assert before != asdict(f.feature_config_from_env())


def test_keywords_read_findings_independent_of_fact_profile():
    profile = f._fact_profile_manifest()["id"]
    f.check_fact_profile(profile, ["ruleword:curl", "descword:download"])
