"""Tests for feature extraction from cleave v3 AnalysisReport JSON."""

import math

from collimator.features import (
    FeatureSpec,
    _should_log_scale,
    _taxonomy_prefixes,
    build_vocab,
    extract,
    extract_all,
    primary_file,
    standardize,
)


def _make_report(
    findings: list[dict] | None = None,
    structure: list[dict] | None = None,
    imports: list[dict] | None = None,
    strings: list[dict] | None = None,
    sections: list[dict] | None = None,
    metrics: dict | None = None,
    file_type: str = "elf",
    risk: str = "baseline",
    size: int = 1024,
    counts: dict | None = None,
    depth: int = 0,
) -> dict:
    """Create a report in the v3 schema."""
    return {
        "version": "3",
        "files": [{
            "id": 0,
            "path": "/tmp/test",
            "depth": depth,
            "file_type": file_type,
            "sha256": "abc123",
            "size": size,
            "risk": risk,
            "counts": counts or {},
            "findings": findings or [],
            "structure": structure or [],
            "strings": strings or [],
            "imports": imports or [],
            "sections": sections or [],
            "metrics": metrics or {},
        }],
        "summary": {
            "files_analyzed": 1,
            "counts": counts or {},
            "max_risk": risk,
            "duration_ms": 10,
            "tools": ["test"],
        },
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def test_taxonomy_prefixes() -> None:
    assert _taxonomy_prefixes("objectives/anti-analysis/timing::ast") == (
        "objectives",
        "objectives/anti-analysis",
        "objectives/anti-analysis/timing",
    )
    assert _taxonomy_prefixes("net/socket") == ("net", "net/socket")
    assert _taxonomy_prefixes("standalone") == ("standalone",)


def test_primary_file_returns_first() -> None:
    report = _make_report()
    pf = primary_file(report)
    assert pf["file_type"] == "elf"
    assert pf["sha256"] == "abc123"


def test_primary_file_empty() -> None:
    assert primary_file({}) == {}
    assert primary_file({"files": []}) == {}
    assert primary_file({"files": [None]}) == {}


def test_should_log_scale() -> None:
    assert _should_log_scale("file_size") is True
    assert _should_log_scale("string_count") is True
    assert _should_log_scale("total_lines") is True
    assert _should_log_scale("total_bytes") is True
    assert _should_log_scale("overall_entropy") is False
    assert _should_log_scale("avg_complexity") is False
    assert _should_log_scale("is_universal") is False
    assert _should_log_scale("has_code_signature") is False
    assert _should_log_scale("code_to_data_ratio") is False
    assert _should_log_scale("import_density") is False


# ---------------------------------------------------------------------------
# Vocabulary building
# ---------------------------------------------------------------------------

def test_build_vocab_empty() -> None:
    spec = build_vocab([_make_report()])
    assert spec.total_features > 0
    assert len(spec.feature_names) == spec.total_features
    assert spec.version == 9


def test_build_vocab_taxonomy() -> None:
    reports = [
        _make_report(findings=[
            {"id": "net/socket", "crit": "suspicious", "conf": 0.9},
            {"id": "crypto/aes", "crit": "baseline", "conf": 0.8},
        ]),
        _make_report(findings=[
            {"id": "net/socket", "crit": "hostile", "conf": 1.0},
            {"id": "crypto/aes", "crit": "notable", "conf": 0.9},
        ]),
    ]
    spec = build_vocab(reports)
    assert "net" in spec.taxonomy_vocab
    assert "net/socket" in spec.taxonomy_vocab
    assert "crypto" in spec.taxonomy_vocab
    assert "crypto/aes" in spec.taxonomy_vocab


def test_build_vocab_evidence_methods() -> None:
    reports = [
        _make_report(findings=[
            {"id": "a", "crit": "baseline", "conf": 0.5, "evidence": [
                {"method": "symbol", "source": "goblin", "value": "foo"},
                {"method": "hex", "source": "yara", "value": "bar"},
            ]},
        ]),
    ]
    spec = build_vocab(reports)
    assert "symbol" in spec.evidence_vocab
    assert "hex" in spec.evidence_vocab


def test_build_vocab_string_types() -> None:
    reports = [
        _make_report(strings=[
            {"value": "hello", "offset": "0x0", "type": "Const"},
            {"value": "aGVsbG8=", "offset": "0x10", "type": "Base64"},
        ]),
    ]
    spec = build_vocab(reports)
    assert "Const" in spec.string_type_vocab
    assert "Base64" in spec.string_type_vocab


def test_build_vocab_metrics() -> None:
    reports = [
        _make_report(metrics={
            "binary": {"overall_entropy": 7.8, "file_size": 4096},
            "text": {"char_entropy": 5.5},
        }),
    ]
    spec = build_vocab(reports)
    assert "binary:file_size" in spec.metric_vocab
    assert "binary:overall_entropy" in spec.metric_vocab
    assert "text:char_entropy" in spec.metric_vocab


def test_build_vocab_metrics_skips_non_numeric() -> None:
    reports = [
        _make_report(metrics={
            "text": {"most_common_char": "e", "char_entropy": 5.5},
        }),
    ]
    spec = build_vocab(reports)
    assert "text:char_entropy" in spec.metric_vocab
    assert "text:most_common_char" not in spec.metric_vocab


def test_build_vocab_no_sparse_vocabs() -> None:
    """Version 9 should not have highcrit, attack, mbc, import, or library vocabs."""
    reports = [
        _make_report(findings=[
            {"id": "a", "crit": "hostile", "conf": 1.0, "attack": "T1055", "mbc": "B0001"},
        ]),
    ]
    spec = build_vocab(reports)
    assert not hasattr(spec, "highcrit_vocab") or not spec.__dict__.get("highcrit_vocab")
    assert not hasattr(spec, "attack_vocab") or not spec.__dict__.get("attack_vocab")
    assert not hasattr(spec, "import_vocab") or not spec.__dict__.get("import_vocab")


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

def test_extract_taxonomy_criticality() -> None:
    report = _make_report(findings=[
        {"id": "net/socket", "crit": "suspicious", "conf": 0.9},
        {"id": "net/socket", "crit": "hostile", "conf": 1.0},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)

    crit_idx = spec.feature_names.index("taxon_crit:net/socket")
    count_idx = spec.feature_names.index("taxon_count:net/socket")
    assert vec[crit_idx] == 5.0  # hostile = 5
    assert math.isclose(vec[count_idx], math.log1p(2), rel_tol=1e-6)

    net_crit_idx = spec.feature_names.index("taxon_crit:net")
    net_count_idx = spec.feature_names.index("taxon_count:net")
    assert vec[net_crit_idx] == 5.0
    assert math.isclose(vec[net_count_idx], math.log1p(2), rel_tol=1e-6)


def test_extract_criticality_histogram() -> None:
    report = _make_report(findings=[
        {"id": "a", "crit": "hostile", "conf": 1.0},
        {"id": "b", "crit": "hostile", "conf": 1.0},
        {"id": "c", "crit": "suspicious", "conf": 0.8},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)

    assert vec[spec.feature_names.index("crit_count:hostile")] == 2.0
    assert vec[spec.feature_names.index("crit_count:suspicious")] == 1.0


def test_extract_criticality_ratios() -> None:
    report = _make_report(findings=[
        {"id": "a", "crit": "hostile", "conf": 1.0},
        {"id": "b", "crit": "suspicious", "conf": 0.8},
        {"id": "c", "crit": "baseline", "conf": 0.5},
        {"id": "d", "crit": "baseline", "conf": 0.5},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)

    idx_h = spec.feature_names.index("crit_ratio:hostile")
    idx_s = spec.feature_names.index("crit_ratio:suspicious")
    idx_a = spec.feature_names.index("crit_ratio:above_notable")
    assert math.isclose(vec[idx_h], 0.25, rel_tol=1e-6)
    assert math.isclose(vec[idx_s], 0.25, rel_tol=1e-6)
    assert math.isclose(vec[idx_a], 0.5, rel_tol=1e-6)


def test_extract_criticality_weighted() -> None:
    report = _make_report(findings=[
        {"id": "a", "crit": "hostile", "conf": 0.9},
        {"id": "b", "crit": "hostile", "conf": 0.7},
        {"id": "c", "crit": "suspicious", "conf": 0.8},
        {"id": "d", "crit": "baseline", "conf": 0.5},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)

    assert math.isclose(vec[spec.feature_names.index("crit_weighted:hostile")], 1.6, rel_tol=1e-6)
    assert math.isclose(
        vec[spec.feature_names.index("crit_weighted:suspicious")], 0.8, rel_tol=1e-6,
    )


def test_extract_confidence_stats() -> None:
    report = _make_report(findings=[
        {"id": "a", "crit": "baseline", "conf": 0.2},
        {"id": "b", "crit": "baseline", "conf": 0.8},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)

    assert math.isclose(vec[spec.feature_names.index("conf:mean")], 0.5, rel_tol=1e-6)
    assert math.isclose(vec[spec.feature_names.index("conf:max")], 0.8, rel_tol=1e-6)
    assert math.isclose(vec[spec.feature_names.index("conf:min")], 0.2, rel_tol=1e-6)
    assert vec[spec.feature_names.index("conf:stddev")] > 0.0


def test_extract_behavior_summary() -> None:
    report = _make_report(findings=[
        {"id": "a", "crit": "hostile", "conf": 1.0, "attack": "T1055"},
        {"id": "b", "crit": "hostile", "conf": 1.0, "attack": "T1055"},
        {"id": "c", "crit": "hostile", "conf": 1.0, "attack": "T1027", "mbc": "B0001"},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)

    assert vec[spec.feature_names.index("behavior:attack_unique")] == 2.0
    assert vec[spec.feature_names.index("behavior:attack_total")] == 3.0
    assert vec[spec.feature_names.index("behavior:mbc_unique")] == 1.0
    assert vec[spec.feature_names.index("behavior:mbc_total")] == 1.0


def test_extract_evidence_methods() -> None:
    report = _make_report(findings=[
        {"id": "a", "crit": "baseline", "conf": 0.5, "evidence": [
            {"method": "symbol", "source": "goblin", "value": "foo"},
            {"method": "symbol", "source": "goblin", "value": "bar"},
            {"method": "hex", "source": "yara", "value": "baz"},
        ]},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)

    assert vec[spec.feature_names.index("evidence:symbol")] == 2.0
    assert vec[spec.feature_names.index("evidence:hex")] == 1.0


def test_extract_string_type_distribution() -> None:
    report = _make_report(strings=[
        {"value": "hello", "offset": "0x0", "type": "Const"},
        {"value": "aGVsbG8=", "offset": "0x10", "type": "Base64"},
        {"value": "/bin/sh", "offset": "0x20", "type": "ShellCmd"},
        {"value": "http://x", "offset": "0x30", "type": "Url"},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)

    assert vec[spec.feature_names.index("string_type:Const")] == 1.0
    assert vec[spec.feature_names.index("string_type:Base64")] == 1.0
    assert vec[spec.feature_names.index("string_type:ShellCmd")] == 1.0
    assert vec[spec.feature_names.index("string_type:Url")] == 1.0

    # 2 suspicious (Base64 + ShellCmd) out of 4 strings
    assert math.isclose(vec[spec.feature_names.index("string_ratio:suspicious")], 0.5, rel_tol=1e-6)
    # 1 encoded (Base64) out of 4
    assert math.isclose(vec[spec.feature_names.index("string_ratio:encoded")], 0.25, rel_tol=1e-6)
    # 1 network (Url) out of 4
    assert math.isclose(vec[spec.feature_names.index("string_ratio:network")], 0.25, rel_tol=1e-6)


def test_extract_section_metrics() -> None:
    report = _make_report(sections=[
        {"name": ".text", "address": 4096, "size": 8192, "entropy": 6.5, "permissions": "r-x"},
        {"name": ".data", "address": 16384, "size": 2048, "entropy": 3.2, "permissions": "rw-"},
        {"name": ".evil", "address": 32768, "size": 512, "entropy": 7.9, "permissions": "rwx"},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)

    assert vec[spec.feature_names.index("sections:count")] == 3.0
    expected_avg = (6.5 + 3.2 + 7.9) / 3
    avg_idx = spec.feature_names.index("sections:avg_entropy")
    max_idx = spec.feature_names.index("sections:max_entropy")
    assert math.isclose(vec[avg_idx], expected_avg, rel_tol=1e-5)
    assert math.isclose(vec[max_idx], 7.9, rel_tol=1e-5)
    assert vec[spec.feature_names.index("sections:wx_count")] == 1.0  # .evil has rwx
    assert math.isclose(
        vec[spec.feature_names.index("sections:max_size_log")],
        math.log1p(8192),
        rel_tol=1e-5,
    )


def test_extract_metrics_passthrough() -> None:
    report = _make_report(metrics={
        "binary": {"overall_entropy": 7.8, "file_size": 4096, "string_count": 32},
        "text": {"char_entropy": 5.5},
    })
    spec = build_vocab([report])
    vec = extract(report, spec)

    assert vec[spec.feature_names.index("metrics:binary_overall_entropy")] == 7.8
    # file_size should be log-scaled
    assert math.isclose(
        vec[spec.feature_names.index("metrics:binary_file_size")],
        math.log1p(4096),
        rel_tol=1e-6,
    )
    # string_count should be log-scaled
    assert math.isclose(
        vec[spec.feature_names.index("metrics:binary_string_count")],
        math.log1p(32),
        rel_tol=1e-6,
    )
    # char_entropy should NOT be log-scaled
    assert vec[spec.feature_names.index("metrics:text_char_entropy")] == 5.5


def test_extract_filetype_onehot() -> None:
    reports = [
        _make_report(file_type="elf"),
        _make_report(file_type="python"),
    ]
    spec = build_vocab(reports)
    vec = extract(reports[0], spec)

    assert vec[spec.feature_names.index("filetype:elf")] == 1.0
    assert vec[spec.feature_names.index("filetype:python")] == 0.0


def test_extract_aggregate_stats() -> None:
    report = _make_report(
        findings=[
            {"id": "a", "crit": "hostile", "conf": 1.0},
            {"id": "b", "crit": "suspicious", "conf": 0.8},
        ],
        strings=[{"value": "x", "offset": "0x0", "type": "Const"}] * 5,
        imports=[{"symbol": "foo", "source": "goblin"}] * 3,
        risk="hostile",
        size=65536,
        depth=2,
        counts={"hostile": 1, "suspicious": 1, "notable": 0},
    )
    spec = build_vocab([report])
    vec = extract(report, spec)

    assert vec[spec.feature_names.index("agg:finding_count")] == 2.0
    assert vec[spec.feature_names.index("agg:risk_ordinal")] == 5.0  # hostile = 5
    assert vec[spec.feature_names.index("agg:string_count")] == 5.0
    assert vec[spec.feature_names.index("agg:import_count")] == 3.0
    assert math.isclose(
        vec[spec.feature_names.index("agg:log_size")],
        math.log1p(65536),
        rel_tol=1e-6,
    )
    assert vec[spec.feature_names.index("agg:depth")] == 2.0
    assert vec[spec.feature_names.index("agg:hostile_count")] == 1.0
    assert vec[spec.feature_names.index("agg:suspicious_count")] == 1.0


def test_extract_finding_behavior() -> None:
    report = _make_report(findings=[
        {"id": "a", "crit": "hostile", "conf": 1.0, "match_count": 3, "evidence": [
            {"method": "symbol", "source": "goblin", "value": "foo"},
            {"method": "hex", "source": "yara", "value": "bar"},
        ]},
        {"id": "b", "crit": "hostile", "conf": 0.8, "match_count": 1, "evidence": [
            {"method": "string", "source": "string_extractor", "value": "baz"},
        ]},
        {"id": "a", "crit": "hostile", "conf": 0.9, "match_count": 2, "evidence": []},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)

    # 2 unique IDs out of 3 findings
    assert math.isclose(vec[spec.feature_names.index("finding:diversity")], 2 / 3, rel_tol=1e-6)
    # avg match_count: (3 + 1 + 2) / 3 = 2.0
    assert math.isclose(vec[spec.feature_names.index("finding:avg_match")], 2.0, rel_tol=1e-6)
    # avg evidence: (2 + 1 + 0) / 3 = 1.0
    assert math.isclose(vec[spec.feature_names.index("finding:avg_evidence")], 1.0, rel_tol=1e-6)
    # total evidence: 3
    assert vec[spec.feature_names.index("finding:evidence_total")] == 3.0


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_extract_all_shape() -> None:
    reports = [_make_report() for _ in range(5)]
    labels = [0, 1, 0, 1, 0]
    spec = build_vocab(reports)
    X, y = extract_all(reports, labels, spec)

    assert X.shape == (5, spec.total_features)
    assert y.shape == (5,)
    assert list(y) == [0.0, 1.0, 0.0, 1.0, 0.0]


def test_extract_vector_length_matches_spec() -> None:
    report = _make_report(
        findings=[{"id": "net/socket", "crit": "hostile", "conf": 1.0}],
        structure=[{"id": "elf/header", "desc": "x", "evidence": []}],
        imports=[{"symbol": "connect", "source": "goblin"}],
    )
    spec = build_vocab([report])
    vec = extract(report, spec)
    assert len(vec) == spec.total_features


def test_unknown_finding_ignored() -> None:
    report = _make_report(findings=[
        {"id": "known", "crit": "baseline", "conf": 0.5},
    ])
    spec = build_vocab([report])

    report_new = _make_report(findings=[
        {"id": "known", "crit": "baseline", "conf": 0.5},
        {"id": "unknown_new", "crit": "hostile", "conf": 1.0},
    ])
    vec = extract(report_new, spec)
    assert vec[spec.feature_names.index("crit_count:hostile")] == 1.0


def test_null_json_fields() -> None:
    """All list fields may be absent or null in sparse reports."""
    report = {
        "version": "3",
        "files": [{
            "id": 0,
            "path": "/tmp/x",
            "depth": 0,
            "file_type": "elf",
            "sha256": "abc",
            "size": 1024,
        }],
        "summary": {"files_analyzed": 1, "duration_ms": 1, "tools": []},
    }
    spec = build_vocab([report])
    vec = extract(report, spec)
    assert len(vec) == spec.total_features
    # File type one-hot should be set.
    assert vec[spec.feature_names.index("filetype:elf")] == 1.0


def test_empty_files_array() -> None:
    report = {"version": "3", "files": []}
    spec = build_vocab([report])
    vec = extract(report, spec)
    assert len(vec) == spec.total_features


def test_no_findings_confidence_stats_zero() -> None:
    report = _make_report()
    spec = build_vocab([report])
    vec = extract(report, spec)
    assert vec[spec.feature_names.index("conf:mean")] == 0.0
    assert vec[spec.feature_names.index("conf:stddev")] == 0.0


def test_single_finding_stddev_zero() -> None:
    report = _make_report(findings=[
        {"id": "a", "crit": "baseline", "conf": 0.7},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)
    assert vec[spec.feature_names.index("conf:stddev")] == 0.0


def test_no_findings_behavior_zero() -> None:
    report = _make_report()
    spec = build_vocab([report])
    vec = extract(report, spec)
    assert vec[spec.feature_names.index("finding:diversity")] == 0.0
    assert vec[spec.feature_names.index("finding:avg_match")] == 0.0
    assert vec[spec.feature_names.index("finding:avg_evidence")] == 0.0
    assert vec[spec.feature_names.index("finding:evidence_total")] == 0.0


# ---------------------------------------------------------------------------
# Spec round-trip
# ---------------------------------------------------------------------------

def test_feature_spec_save_load(tmp_path) -> None:
    report = _make_report(
        findings=[
            {"id": "net/socket", "crit": "hostile", "conf": 1.0, "attack": "T1055",
             "mbc": "B0001", "evidence": [
                 {"method": "symbol", "source": "goblin", "value": "connect"},
             ]},
        ],
        strings=[{"value": "test", "offset": "0x0", "type": "Base64"}],
        metrics={"binary": {"overall_entropy": 7.8}},
    )
    spec = build_vocab([report])
    path = tmp_path / "spec.json"
    spec.save(path)
    loaded = FeatureSpec.load(path)

    assert loaded.total_features == spec.total_features
    assert loaded.taxonomy_vocab == spec.taxonomy_vocab
    assert loaded.evidence_vocab == spec.evidence_vocab
    assert loaded.string_type_vocab == spec.string_type_vocab
    assert loaded.metric_vocab == spec.metric_vocab
    assert loaded.filetype_vocab == spec.filetype_vocab
    assert loaded.feature_names == spec.feature_names
    assert loaded.version == 9


# ---------------------------------------------------------------------------
# Standardization
# ---------------------------------------------------------------------------

def test_standardize_with_params() -> None:
    import numpy as np
    report = _make_report()
    spec = build_vocab([report])
    spec.feature_means = [0.0] * spec.total_features
    spec.feature_stds = [1.0] * spec.total_features
    X = np.ones((2, spec.total_features), dtype=np.float32)
    result = standardize(X, spec)
    # All features are dead (mean=0, std=1), so result should be all zeros.
    assert np.allclose(result, 0.0)


def test_standardize_without_params() -> None:
    import numpy as np
    report = _make_report()
    spec = build_vocab([report])
    X = np.ones((2, spec.total_features), dtype=np.float32)
    result = standardize(X, spec)
    assert np.array_equal(result, X)
