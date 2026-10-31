"""Keyword discovery must use training documents and survive spec round trips."""

import json
from dataclasses import asdict, replace

import numpy as np
import pytest

from collimator import data, features as f


@pytest.fixture(autouse=True)
def config(monkeypatch):
    for key in ("RULE_KEYWORDS", "DESCRIPTION_KEYWORDS", "DISABLE_FEATURE_GROUPS",
                "FULL_RULE_KEYWORDS", "RULE_DESCRIPTION_KEYWORDS", "CONTEXT_KEYWORDS",
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
def test_missing_description_preserves_other_keywords(monkeypatch, desc, caplog):
    monkeypatch.setenv("COLLIMATOR_RULE_KEYWORDS", "1")
    monkeypatch.setenv("COLLIMATOR_DESCRIPTION_KEYWORDS", "1")
    mixed = report(desc=desc)
    mixed["files"][0]["traits"].extend(report("valid_trait", "Valid description")["files"][0]["traits"])
    with caplog.at_level("INFO", logger="collimator.features"):
        spec = f.build_vocab([mixed, report(desc=desc)], 1)
    assert spec.keyword_vocabs == {
        "ruleword": ["curl", "download", "post", "trait", "valid"],
        "descword": ["description", "valid"],
    }
    assert "2 findings across 2 reports" in caplog.text
    # Below-confidence findings don't contribute either source.
    spec = f.build_vocab([report(desc=desc, conf=0.1)], 1)
    assert spec.keyword_vocabs == {"ruleword": [], "descword": []}


@pytest.mark.parametrize("desc", [None, "", "  ", 7])
def test_missing_description_is_zero_at_prediction(monkeypatch, tmp_path, desc):
    monkeypatch.setenv("COLLIMATOR_RULE_KEYWORDS", "1")
    monkeypatch.setenv("COLLIMATOR_DESCRIPTION_KEYWORDS", "1")
    spec = f.build_vocab([report()], 1)
    path = tmp_path / "spec.json"
    spec.save(path)
    loaded = f.FeatureSpec.load(path)
    vec = f.extract(report(desc=desc), loaded)
    assert vec[loaded.feature_names.index("ruleword:curl")] == 1
    for i, name in enumerate(loaded.feature_names):
        if name.startswith("descword:"):
            assert vec[i] == 0


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
    f.check_fact_profile(profile, ["ruleword:curl", "descword:download", "fullword:network",
                                 "ruletextword:network", "contextword:curl"])


def encode_z85(raw):
    alphabet = "".join(f._Z85_DIGITS)
    result = ""
    for start in range(0, len(raw), 4):
        chunk = raw[start:start + 4]
        value = int.from_bytes(chunk.ljust(4, b"\0"), "big")
        digits = ""
        for _ in range(5):
            digits = alphabet[value % 85] + digits
            value //= 85
        result += digits[:5 if len(chunk) == 4 else len(chunk) + 1]
    return result


def test_context_decode_matches_cleave_formats_and_partial_tails():
    assert f._decode_context_window({"a": 56, "l": 7, "t": "café\0"}) == "café\0".encode()
    assert f._decode_context_window({"b": "HelloWorld"}) == bytes.fromhex("864fd26fb559f75b")
    for length in range(261):
        raw = bytes((i * 37 ^ 0xa5) % 256 for i in range(length))
        assert f._decode_context_window({"b": encode_z85(raw)}) == raw
        text = "".join(chr(byte or 256) for byte in raw)
        assert f._decode_context_window({"s": text}) == raw


@pytest.mark.parametrize("window", [{}, {"b": "a"}, {"b": "#####"}, {"b": "ab\"cd"},
    {"s": "x", "b": "aa"}, {"s": "x", "t": "x"}, {"t": 2},
    {"s": "\0"}, {"s": "\u0101"}, {"s": 2}])
def test_invalid_context_is_rejected_only_when_used(window):
    with pytest.raises(ValueError):
        f._report_keywords([{"ctx": [window]}], ("contextword",))
    assert f._report_keywords([{"ctx": [window]}], ("fullword",)) == {"fullword": set()}


def test_full_hierarchy_pooling_and_decoded_context_roundtrip(monkeypatch, tmp_path):
    for key in ("FULL_RULE_KEYWORDS", "RULE_DESCRIPTION_KEYWORDS", "CONTEXT_KEYWORDS"):
        monkeypatch.setenv("COLLIMATOR_" + key, "1")
    item = report()
    raw = b"curl FETCH_token 123 x\xff caf\xc3\xa9"
    item["files"][0]["ctx"] = [{"ln": 0, "s": "".join(chr(b or 256) for b in raw),
                                "notes": "neverlearnannotation"}]
    spec = f.build_vocab([item], 1)
    assert spec.abi_version == 23
    assert spec.base_feature_abi == 20
    assert spec.keyword_vocabs == {
        "fullword": ["behaviors", "curl", "download", "micro", "network", "post"],
        "ruletextword": ["behaviors", "curl", "download", "http", "micro", "network", "post", "via"],
        "contextword": ["caf", "curl", "fetch", "token"],
    }
    before = f.extract(item, spec)
    item["files"][0]["ctx"] = [{"ln": 0, "b": encode_z85(raw)}] * 3
    path = tmp_path / "spec.json"
    spec.save(path)
    for key in ("FULL_RULE_KEYWORDS", "RULE_DESCRIPTION_KEYWORDS", "CONTEXT_KEYWORDS"):
        monkeypatch.delenv("COLLIMATOR_" + key)
    f.feature_config_from_env.cache_clear()
    np.testing.assert_array_equal(before, f.extract(item, f.FeatureSpec.load(path)))
    item["files"][0]["ctx"] = [{"a": 0, "l": 1, "t": raw.decode("utf-8", errors="replace")}]
    np.testing.assert_array_equal(before, f.extract(item, f.FeatureSpec.load(path)))
    # Missing descriptions preserve hierarchy words; missing context stays zero.
    vec = f.extract(report(desc=None), spec)
    assert vec[spec.feature_names.index("ruletextword:network")] == 1
    assert vec[spec.feature_names.index("ruletextword:http")] == 0
    assert vec[spec.feature_names.index("contextword:curl")] == 0


@pytest.mark.parametrize("source,flag", [("fullword", "FULL_RULE_KEYWORDS"),
    ("ruletextword", "RULE_DESCRIPTION_KEYWORDS"), ("contextword", "CONTEXT_KEYWORDS")])
def test_extended_discovery_uses_only_train_documents(monkeypatch, source, flag):
    monkeypatch.setenv("COLLIMATOR_" + flag, "1")
    monkeypatch.setenv("COLLIMATOR_KEYWORD_MIN_FREQ", "2")
    calls = []
    def fetch(_db, ids):
        calls.extend(ids)
        return {rid: {"cleave_result": {"files": [{"ctx": [{"s": "common rare" if rid == 1 else "common"}],
            "traits": [{"id": "common::rare" if rid == 1 else "common::common", "conf": 1}]}]}}
                for rid in ids}
    monkeypatch.setattr(data, "fetch_cleave_results", fetch)
    monkeypatch.setattr(f, "_build_vocab_from_db", lambda *a, **kw: f.FeatureSpec())
    spec = f.build_vocab_from_db("unused", [(1, 0), (2, 1)], n_workers=1)
    assert calls == [1, 2]
    assert spec.keyword_vocabs == {source: ["common"]}
