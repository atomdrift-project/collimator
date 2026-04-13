"""Tests for capability-first feature extraction from cleave v3 AnalysisReport JSON."""

import math

import numpy as np

from collimator.features import (
    FeatureSpec,
    _finding_paths,
    build_vocab,
    extract,
    extract_all,
    feature_config_from_env,
    feature_group_indices,
    primary_file,
    report_files,
    standardize,
)


_CRIT_MAP = {"filtered": 0, "component": 1, "baseline": 2, "notable": 3, "suspicious": 4, "hostile": 5}

def _make_report(
    findings: list[dict] | None = None,
    imports: list[str] | None = None,
    metrics: dict | None = None,
    file_type: str = "elf",
    size: int = 1024,
) -> dict:
    """Create a report in the v4 schema."""
    return {
        "v": "4",
        "fs": [{
            "id": 0,
            "path": "/tmp/test",
            "dp": 0,
            "type": file_type,
            "sha": "abc123",
            "sz": size,
            "ts": findings or [],
            "is": imports or [],
            "ss": [],
            "ms": metrics or {},
        }],
    }


# Many reports needed to exceed MIN_PATH_FREQ (30).
def _reports_with_finding(finding_id: str, crit: str, n: int = 35) -> list[dict]:
    """Create n reports each containing one finding with the given id and crit."""
    return [
        _make_report(findings=[{"i": finding_id, "l": _CRIT_MAP.get(crit, 0), "c": 1.0}])
        for _ in range(n)
    ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def test_finding_paths_deep() -> None:
    paths = _finding_paths("objectives/evasion/process/injection::technique-x")
    assert paths == [
        "objectives",
        "objectives/evasion",
        "objectives/evasion/process",
    ]


def test_finding_paths_two_levels() -> None:
    paths = _finding_paths("metadata/format::no-functions")
    assert paths == ["metadata", "metadata/format"]


def test_finding_paths_single() -> None:
    paths = _finding_paths("standalone")
    assert paths == ["standalone"]


def test_primary_file_returns_first() -> None:
    report = _make_report()
    pf = primary_file(report)
    assert pf["type"] == "elf"
    assert pf["sha"] == "abc123"


def test_primary_file_empty() -> None:
    assert primary_file({}) == {}
    assert primary_file({"fs": []}) == {}
    assert primary_file({"fs": [None]}) == {}


def test_report_files_filters_invalid_entries() -> None:
    report = {"fs": [None, {"type": "zip"}, "bad", {"type": "python"}]}
    files = report_files(report)

    assert [f["type"] for f in files] == ["zip", "python"]


# ---------------------------------------------------------------------------
# Vocabulary building
# ---------------------------------------------------------------------------

def test_build_vocab_empty() -> None:
    spec = build_vocab([_make_report()])
    assert spec.total_features > 0
    assert len(spec.feature_names) == spec.total_features
    assert spec.version == 16


def test_build_vocab_presence() -> None:
    reports = _reports_with_finding("objectives/evasion/process", "hostile", n=35)
    spec = build_vocab(reports)

    # Presence vocab should contain tier-agnostic paths.
    assert "objectives" in spec.presence_vocab
    assert "objectives/evasion" in spec.presence_vocab
    assert "objectives/evasion/process" in spec.presence_vocab

    # Both presence and maxcrit features should exist.
    assert "present:objectives" in spec.feature_names
    assert "maxcrit:objectives" in spec.feature_names
    assert "present:objectives/evasion/process" in spec.feature_names
    assert "maxcrit:objectives/evasion/process" in spec.feature_names


def test_build_vocab_freq_filter() -> None:
    # Below MIN_PATH_FREQ -> excluded.
    reports = _reports_with_finding("objectives/rare", "hostile", n=4)
    spec = build_vocab(reports)
    assert "objectives/rare" not in spec.presence_vocab


def test_build_vocab_filetype() -> None:
    reports = [_make_report(file_type="elf"), _make_report(file_type="pe")]
    spec = build_vocab(reports)
    assert "elf" in spec.filetype_vocab
    assert "pe" in spec.filetype_vocab


def test_build_vocab_feature_groups_present() -> None:
    reports = _reports_with_finding("objectives/evasion", "hostile", n=35)
    spec = build_vocab(reports)

    groups = set()
    for name in spec.feature_names:
        groups.add(name.split(":")[0])
    assert "present" in groups
    assert "maxcrit" in groups
    assert "agg" in groups
    assert "ext" in groups
    assert "metrics" in groups
    assert "filetype" in groups
    assert "struct" in groups


def test_feature_group_indices_covers_all_features() -> None:
    reports = _reports_with_finding("objectives/evasion", "hostile", n=35)
    spec = build_vocab(reports)
    grouped = feature_group_indices(spec)

    seen = sorted(i for idxs in grouped.values() for i in idxs)
    assert seen == list(range(spec.total_features))


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

def test_extract_presence_features() -> None:
    reports = _reports_with_finding("objectives/evasion/process", "hostile", n=35)
    spec = build_vocab(reports)
    vec = extract(reports[0], spec)

    assert vec[spec.feature_names.index("present:objectives")] == 1.0
    assert vec[spec.feature_names.index("present:objectives/evasion")] == 1.0
    assert vec[spec.feature_names.index("present:objectives/evasion/process")] == 1.0


def test_extract_maxcrit_features() -> None:
    reports = _reports_with_finding("objectives/evasion/process", "hostile", n=35)
    spec = build_vocab(reports)
    vec = extract(reports[0], spec)

    # Hostile = ordinal 5.
    assert vec[spec.feature_names.index("maxcrit:objectives")] == 5.0
    assert vec[spec.feature_names.index("maxcrit:objectives/evasion")] == 5.0
    assert vec[spec.feature_names.index("maxcrit:objectives/evasion/process")] == 5.0


def test_extract_maxcrit_notable() -> None:
    """Notable finding should produce maxcrit=3."""
    reports = _reports_with_finding("objectives/evasion", "notable", n=35)
    spec = build_vocab(reports)
    vec = extract(reports[0], spec)

    assert vec[spec.feature_names.index("maxcrit:objectives")] == 3.0
    assert vec[spec.feature_names.index("maxcrit:objectives/evasion")] == 3.0


def test_extract_presence_baseline_only() -> None:
    """A baseline finding should set presence and maxcrit but at baseline level."""
    reports = _reports_with_finding("objectives/evasion", "baseline", n=35)
    spec = build_vocab(reports)
    vec = extract(reports[0], spec)

    assert vec[spec.feature_names.index("present:objectives")] == 1.0
    assert vec[spec.feature_names.index("present:objectives/evasion")] == 1.0
    assert vec[spec.feature_names.index("maxcrit:objectives")] == 2.0  # baseline
    assert vec[spec.feature_names.index("maxcrit:objectives/evasion")] == 2.0


def test_extract_aggregates() -> None:
    reports = _reports_with_finding("objectives/evasion/process", "hostile", n=35)
    spec = build_vocab(reports)
    vec = extract(reports[0], spec)

    # max_crit should be 5 (hostile).
    idx = spec.feature_names.index("agg:max_crit")
    assert vec[idx] == 5.0

    # Concentration: single hostile finding in 1 path = 100%.
    susp_conc = vec[spec.feature_names.index("agg:suspicious_concentration")]
    hostile_conc = vec[spec.feature_names.index("agg:hostile_concentration")]
    assert susp_conc > 0.0
    assert hostile_conc > 0.0


def test_extract_finding_density_features() -> None:
    # NB: _make_report defaults to size=1024 → size_kb = 1.0 → total_kb_p1 = 1.0.
    # agg:*_finding_ratio features are per-KB density (count / total_kb_p1),
    # not per-finding ratio; and agg:unique_*_ids_log is log1p(N)/log1p(total_kb_p1).
    report = _make_report(findings=[
        {"i": "objectives/evasion/process::a", "l": 5, "c":1.0},
        {"i": "objectives/evasion/process::a", "l": 5, "c":1.0},
        {"i": "objectives/evasion/process::b", "l": 4, "c":1.0},
        {"i": "metadata/format::x", "l": 2, "c":1.0},
    ])
    spec = build_vocab([report] * 35)
    vec = extract(report, spec)
    total_kb_p1 = max(1024 / 1024.0, 0.1)  # = 1.0
    log_kb = math.log1p(total_kb_p1)         # = ln(2)

    assert vec[spec.feature_names.index("agg:notable_findings_log")] == math.log1p(3)
    assert vec[spec.feature_names.index("agg:suspicious_findings_log")] == math.log1p(3)
    assert vec[spec.feature_names.index("agg:hostile_findings_log")] == math.log1p(2)
    # Per-KB density: notable(3)/total_kb_p1(1.0) = 3.0, etc.
    assert vec[spec.feature_names.index("agg:notable_finding_ratio")] == 3.0
    assert vec[spec.feature_names.index("agg:suspicious_finding_ratio")] == 3.0
    assert vec[spec.feature_names.index("agg:hostile_finding_ratio")] == 2.0
    # log1p(N) / log1p(total_kb_p1)
    assert math.isclose(
        float(vec[spec.feature_names.index("agg:unique_suspicious_ids_log")]),
        math.log1p(2) / log_kb,
        rel_tol=1e-5,
    )
    assert math.isclose(
        float(vec[spec.feature_names.index("agg:unique_hostile_ids_log")]),
        math.log1p(1) / log_kb,
        rel_tol=1e-5,
    )


def test_extract_third_party_signals() -> None:
    report = _make_report(findings=[
        {"i": "third_party/yara_match", "l": 5, "c":1.0},
        {"i": "third_party/another", "l": 4, "c":1.0},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)

    idx = spec.feature_names.index("ext:third_party_max_crit")
    assert vec[idx] == 5.0

    idx = spec.feature_names.index("ext:third_party_count")
    assert math.isclose(vec[idx], math.log1p(2), rel_tol=1e-6)

    idx = spec.feature_names.index("ext:has_yara_match")
    assert vec[idx] == 1.0


def test_build_vocab_can_disable_feature_groups(monkeypatch) -> None:
    monkeypatch.setenv("COLLIMATOR_DISABLE_FEATURE_GROUPS", "filetype,ext")
    feature_config_from_env.cache_clear()
    try:
        reports = _reports_with_finding("objectives/evasion", "hostile", n=35)
        spec = build_vocab(reports)
    finally:
        feature_config_from_env.cache_clear()

    assert "filetype:elf" not in spec.feature_names
    assert "ext:third_party_max_crit" not in spec.feature_names
    assert "present:objectives" in spec.feature_names


def test_build_vocab_uses_configured_top_k_risk_files(monkeypatch) -> None:
    monkeypatch.setenv("COLLIMATOR_TOP_K_RISK_FILES", "3")
    feature_config_from_env.cache_clear()
    try:
        spec = build_vocab(_reports_with_finding("objectives/evasion", "hostile", n=35))
    finally:
        feature_config_from_env.cache_clear()

    assert "agg:top3_file_suspicious_ratio_sum" in spec.feature_names
    assert "agg:top1_file_suspicious_ratio_sum" not in spec.feature_names


def test_extract_struct_file_risk_coverage(monkeypatch) -> None:
    monkeypatch.setenv("COLLIMATOR_STRUCT_FILE_RISK_COVERAGE", "1")
    feature_config_from_env.cache_clear()
    try:
        report = {
            "fs": [
                {
                    "type":"elf",
                    "sz":1000,
                    "is":[],
                    "ms":{},
                    "ts": [{"i": "objectives/evasion::a", "l": 4, "c":1.0}],
                },
                {
                    "type":"elf",
                    "sz":1000,
                    "is":[],
                    "ms":{},
                    "ts": [{"i": "objectives/evasion::b", "l": 5, "c":1.0}],
                },
            ],
        }
        spec = build_vocab([report] * 35)
        vec = extract(report, spec)
    finally:
        feature_config_from_env.cache_clear()

    assert vec[spec.feature_names.index("struct:suspicious_file_fraction")] == 1.0
    assert vec[spec.feature_names.index("struct:hostile_file_fraction")] == 0.5


def test_extract_suspicious_breadth_density(monkeypatch) -> None:
    monkeypatch.setenv("COLLIMATOR_SUSPICIOUS_BREADTH_DENSITY", "1")
    feature_config_from_env.cache_clear()
    try:
        report = {
            "fs": [
                {
                    "type":"pe",
                    "sz":1024,
                    "is":[],
                    "ms":{},
                    "ts": [
                        {"i": "objectives/evasion::a", "l": 4, "c":1.0},
                        {"i": "metadata/format::b", "l": 5, "c":1.0},
                    ],
                },
                {
                    "type":"javascript",
                    "sz":4096,
                    "is":[],
                    "ms":{},
                    "ts": [
                        {"i": "micro-behaviors/network::c", "l": 4, "c":1.0},
                    ],
                },
            ],
        }
        spec = build_vocab([report] * 35)
        vec = extract(report, spec)
    finally:
        feature_config_from_env.cache_clear()

    assert vec[spec.feature_names.index("agg:suspicious_category_breadth")] == 3.0
    assert vec[spec.feature_names.index("agg:hostile_category_breadth")] == 1.0
    assert vec[spec.feature_names.index("agg:suspicious_category_density")] == 1.0
    assert vec[spec.feature_names.index("agg:hostile_category_density")] == 1 / 3
    assert vec[spec.feature_names.index("agg:suspicious_findings_per_kb")] == 3 / 5
    assert vec[spec.feature_names.index("agg:hostile_findings_per_kb")] == 1 / 5
    assert vec[spec.feature_names.index("agg:suspicious_categories_per_kb")] == 3 / 5
    assert vec[spec.feature_names.index("agg:hostile_categories_per_kb")] == 1 / 5
    assert vec[spec.feature_names.index("agg:top1_file_suspicious_density_sum")] == 2.0
    assert vec[spec.feature_names.index("agg:top1_file_hostile_density_sum")] == 1.0
    assert vec[spec.feature_names.index("agg:top1_file_suspicious_category_breadth_sum")] == 2.0
    assert vec[spec.feature_names.index("agg:top1_file_hostile_category_breadth_sum")] == 1.0


def test_extract_hostile_escalation_features(monkeypatch) -> None:
    monkeypatch.setenv("COLLIMATOR_HOSTILE_ESCALATION_FEATURES", "1")
    feature_config_from_env.cache_clear()
    try:
        report = _make_report(findings=[
            {"i": "objectives/evasion/process::a", "l": 3, "c":1.0},
            {"i": "objectives/evasion/process::b", "l": 4, "c":1.0},
            {"i": "metadata/format::c", "l": 5, "c":1.0},
        ])
        spec = build_vocab([report] * 35)
        vec = extract(report, spec)
    finally:
        feature_config_from_env.cache_clear()

    assert vec[spec.feature_names.index("agg:hostile_escalation_rate")] == 0.0
    assert vec[spec.feature_names.index("agg:hostile_share_of_suspicious")] == 0.0
    assert vec[spec.feature_names.index("agg:suspicious_finding_escalation_rate")] == 2 / 3
    assert vec[spec.feature_names.index("agg:hostile_finding_escalation_rate")] == 1 / 3
    assert vec[spec.feature_names.index("agg:hostile_share_of_suspicious_findings")] == 0.5


def test_extract_density_penalty_and_file_severity_features(monkeypatch) -> None:
    monkeypatch.setenv("COLLIMATOR_HOSTILE_WEIGHTED_DENSITY", "1")
    monkeypatch.setenv("COLLIMATOR_REPETITION_PENALTY_FEATURES", "1")
    monkeypatch.setenv("COLLIMATOR_FILE_SEVERITY_DISTRIBUTION", "1")
    feature_config_from_env.cache_clear()
    try:
        report = {
            "fs": [
                {
                    "type":"pe",
                    "sz":1024,
                    "is":[],
                    "ms":{},
                    "ts": [
                        {"i": "objectives/evasion/process::a", "l": 5, "c":1.0},
                        {"i": "objectives/evasion/process::a", "l": 5, "c":1.0},
                        {"i": "metadata/format::b", "l": 4, "c":1.0},
                    ],
                },
                {
                    "type":"javascript",
                    "sz":4096,
                    "is":[],
                    "ms":{},
                    "ts": [
                        {"i": "metadata/format::c", "l": 4, "c":1.0},
                    ],
                },
                {
                    "type":"zip",
                    "sz":1024,
                    "is":[],
                    "ms":{},
                    "ts": [
                        {"i": "micro-behaviors/fs::d", "l": 3, "c":1.0},
                    ],
                },
            ],
        }
        spec = build_vocab([report] * 35)
        vec = extract(report, spec)
    finally:
        feature_config_from_env.cache_clear()

    assert vec[spec.feature_names.index("agg:hostile_weighted_density")] == 0.5
    assert vec[spec.feature_names.index("agg:top1_file_hostile_weighted_density_sum")] == 2.75
    assert vec[spec.feature_names.index("agg:suspicious_id_repeat_ratio")] == 0.25
    assert vec[spec.feature_names.index("agg:hostile_id_repeat_ratio")] == 0.5
    assert vec[spec.feature_names.index("agg:suspicious_category_repeat_ratio")] == 0.5
    assert vec[spec.feature_names.index("agg:hostile_category_repeat_ratio")] == 0.5
    assert vec[spec.feature_names.index("agg:file_hostile_fraction")] == 1 / 3
    assert vec[spec.feature_names.index("agg:file_suspicious_fraction")] == 1 / 3
    assert vec[spec.feature_names.index("agg:file_notable_fraction")] == 1 / 3


def test_extract_non_yara_third_party_does_not_set_yara_flag() -> None:
    report = _make_report(findings=[
        {"i": "third_party/packer_match", "l": 5, "c":1.0},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)

    idx = spec.feature_names.index("ext:has_yara_match")
    assert vec[idx] == 0.0


def test_extract_well_known_signals() -> None:
    report = _make_report(findings=[
        {"i": "well-known/cobalt", "l": 5, "c":1.0},
        {"i": "well-known/meterpreter", "l": 4, "c":1.0},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)

    idx = spec.feature_names.index("ext:well_known_max_crit")
    assert vec[idx] == 5.0

    idx = spec.feature_names.index("ext:well_known_hostile_count")
    assert vec[idx] == 1.0

    idx = spec.feature_names.index("ext:well_known_suspicious_count")
    assert vec[idx] == 1.0


def test_extract_key_metrics() -> None:
    report = _make_report(metrics={
        "binary": {"overall_entropy": 7.8, "function_count": 42},
        "text": {"char_entropy": 5.5},
    })
    spec = build_vocab([report])
    vec = extract(report, spec)

    idx = spec.feature_names.index("metrics:binary_overall_entropy")
    assert vec[idx] == 7.8

    idx = spec.feature_names.index("metrics:binary_function_count")
    assert math.isclose(vec[idx], math.log1p(42), rel_tol=1e-6)

    idx = spec.feature_names.index("metrics:text_char_entropy")
    assert vec[idx] == 5.5


def test_extract_uses_inner_files_from_archive(monkeypatch) -> None:
    # BLINDFOLD=1 (v16 default) skips filetype one-hot writes; disable for this test.
    monkeypatch.setenv("COLLIMATOR_BLINDFOLD", "0")
    feature_config_from_env.cache_clear()
    report = {
        "version": "3",
        "fs": [
            {
                "id": 0,
                "path": "/tmp/archive.zip",
                "depth": 0,
                "type":"zip",
                "sha256": "outer",
                "sz":4096,
                "ts": [],
                "is":[],
                "strings": [],
                "sections": [],
                "ms":{},
            },
            {
                "id": 1,
                "path": "archive.zip!!hello.py",
                "depth": 1,
                "type":"python",
                "sha256": "inner",
                "sz":512,
                "ts": [
                    {"i": "objectives/evasion/process", "l": 5, "c":1.0},
                ],
                "is":[{"module": "os"}],
                "strings": [],
                "sections": [],
                "ms":{
                    "text": {"char_entropy": 5.5},
                },
            },
        ],
        "summary": {
            "files_analyzed": 2,
            "duration_ms": 10,
            "tools": ["test"],
        },
    }
    spec = build_vocab([report] * 35)
    vec = extract(report, spec)

    assert vec[spec.feature_names.index("present:objectives")] == 1.0
    assert vec[spec.feature_names.index("maxcrit:objectives")] == 5.0
    assert vec[spec.feature_names.index("filetype:zip")] == 1.0
    assert vec[spec.feature_names.index("filetype:python")] == 1.0
    assert vec[spec.feature_names.index("metrics:text_char_entropy")] == 5.5
    assert vec[spec.feature_names.index("struct:finding_count_log")] == math.log1p(1)
    assert vec[spec.feature_names.index("struct:inner_file_count_log")] == math.log1p(1)


def test_extract_topk_file_risk_features() -> None:
    report = {
        "version": "3",
        "fs": [
            {
                "id": 0,
                "path": "/tmp/pkg.zip",
                "depth": 0,
                "type":"zip",
                "sha256": "outer",
                "sz":1024,
                "ts": [],
                "is":[],
                "strings": [],
                "sections": [],
                "ms":{},
            },
            {
                "id": 1,
                "path": "pkg.zip!!benign.py",
                "depth": 1,
                "type":"python",
                "sha256": "b",
                "sz":100,
                "ts": [
                    {"i": "metadata/format::x", "l": 2, "c":1.0},
                ],
                "is":[],
                "strings": [],
                "sections": [],
                "ms":{},
            },
            {
                "id": 2,
                "path": "pkg.zip!!evil.py",
                "depth": 1,
                "type":"python",
                "sha256": "e",
                "sz":100,
                "ts": [
                    {"i": "objectives/evasion/process::a", "l": 5, "c":1.0},
                    {"i": "objectives/evasion/process::b", "l": 4, "c":1.0},
                ],
                "is":[],
                "strings": [],
                "sections": [],
                "ms":{},
            },
        ],
        "summary": {"files_analyzed": 3, "duration_ms": 10, "tools": ["test"]},
    }
    spec = build_vocab([report] * 35)
    vec = extract(report, spec)

    assert vec[spec.feature_names.index("agg:top1_file_suspicious_ratio_sum")] == 1.0
    assert vec[spec.feature_names.index("agg:top1_file_hostile_ratio_sum")] == 0.5
    assert vec[spec.feature_names.index("agg:top1_file_suspicious_findings_log")] == math.log1p(2)
    assert vec[spec.feature_names.index("agg:top1_file_hostile_findings_log")] == math.log1p(1)


def test_extract_filetype_onehot(monkeypatch) -> None:
    # BLINDFOLD=1 is the v16 default, which *skips* the filetype write loop.
    # Disable it here so we can assert on the filetype one-hot directly.
    monkeypatch.setenv("COLLIMATOR_BLINDFOLD", "0")
    feature_config_from_env.cache_clear()
    reports = [_make_report(file_type="elf"), _make_report(file_type="pe")]
    spec = build_vocab(reports)
    vec = extract(reports[0], spec)

    assert vec[spec.feature_names.index("filetype:elf")] == 1.0
    assert vec[spec.feature_names.index("filetype:pe")] == 0.0
    feature_config_from_env.cache_clear()


def test_extract_structural() -> None:
    report = _make_report(file_type="pe", size=5000)
    spec = build_vocab([report])
    vec = extract(report, spec)

    idx = spec.feature_names.index("struct:tiny_executable")
    assert vec[idx] == 1.0

    report_big = _make_report(file_type="pe", size=50000)
    vec_big = extract(report_big, spec)
    assert vec_big[idx] == 0.0


def test_extract_no_imports() -> None:
    report = _make_report(imports=[])
    spec = build_vocab([report])
    vec = extract(report, spec)

    idx = spec.feature_names.index("struct:no_imports")
    assert vec[idx] == 1.0


def test_extract_zero_findings() -> None:
    report = _make_report(findings=[])
    spec = build_vocab([report])
    vec = extract(report, spec)

    idx = spec.feature_names.index("struct:zero_findings")
    assert vec[idx] == 1.0


def test_extract_finding_count_log() -> None:
    report = _make_report(findings=[
        {"i": "a", "l": 2, "c":1.0},
        {"i": "b", "l": 2, "c":1.0},
        {"i": "c", "l": 2, "c":1.0},
    ])
    spec = build_vocab([report])
    vec = extract(report, spec)

    idx = spec.feature_names.index("struct:finding_count_log")
    assert math.isclose(vec[idx], math.log1p(3), rel_tol=1e-6)


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
        findings=[{"i": "net/socket", "l": 5, "c":1.0}],
        imports=[{"symbol": "connect", "source": "goblin"}],
    )
    spec = build_vocab([report])
    vec = extract(report, spec)
    assert len(vec) == spec.total_features


def test_unknown_path_ignored() -> None:
    report = _make_report(findings=[
        {"i": "known/path", "l": 2, "c":0.5},
    ])
    spec = build_vocab([report])

    report_new = _make_report(findings=[
        {"i": "known/path", "l": 2, "c":0.5},
        {"i": "unknown_new/deep/thing", "l": 5, "c":1.0},
    ])
    vec = extract(report_new, spec)
    assert len(vec) == spec.total_features


def test_null_json_fields(monkeypatch) -> None:
    monkeypatch.setenv("COLLIMATOR_BLINDFOLD", "0")
    feature_config_from_env.cache_clear()
    """All list fields may be absent or null in sparse reports."""
    report = {
        "version": "3",
        "fs": [{
            "id": 0,
            "path": "/tmp/x",
            "depth": 0,
            "type":"elf",
            "sha256": "abc",
            "sz":1024,
        }],
        "summary": {"files_analyzed": 1, "duration_ms": 1, "tools": []},
    }
    spec = build_vocab([report])
    vec = extract(report, spec)
    assert len(vec) == spec.total_features
    assert vec[spec.feature_names.index("filetype:elf")] == 1.0


def test_empty_files_array() -> None:
    report = {"version": "3", "fs": []}
    spec = build_vocab([report])
    vec = extract(report, spec)
    assert len(vec) == spec.total_features


def test_no_findings_zero_aggregates() -> None:
    report = _make_report()
    spec = build_vocab([report])
    vec = extract(report, spec)
    assert vec[spec.feature_names.index("agg:max_crit")] == 0.0
    assert vec[spec.feature_names.index("struct:zero_findings")] == 1.0


# ---------------------------------------------------------------------------
# Spec round-trip
# ---------------------------------------------------------------------------

def test_feature_spec_save_load(tmp_path) -> None:
    reports = _reports_with_finding("objectives/evasion", "hostile", n=35)
    spec = build_vocab(reports)
    path = tmp_path / "spec.json"
    spec.save(path)
    loaded = FeatureSpec.load(path)

    assert loaded.total_features == spec.total_features
    assert loaded.presence_vocab == spec.presence_vocab
    assert loaded.filetype_vocab == spec.filetype_vocab
    assert loaded.feature_names == spec.feature_names
    assert loaded.version == 16


def test_feature_spec_save_load_with_standardization(tmp_path) -> None:
    reports = _reports_with_finding("objectives/evasion", "hostile", n=35)
    spec = build_vocab(reports)
    spec.feature_means = [0.0] * spec.total_features
    spec.feature_stds = [1.0] * spec.total_features
    path = tmp_path / "spec.json"
    spec.save(path)
    loaded = FeatureSpec.load(path)

    assert loaded.feature_means == spec.feature_means
    assert loaded.feature_stds == spec.feature_stds


# ---------------------------------------------------------------------------
# Standardization
# ---------------------------------------------------------------------------

def test_standardize_with_params() -> None:
    report = _make_report()
    spec = build_vocab([report])
    spec.feature_means = [0.0] * spec.total_features
    spec.feature_stds = [1.0] * spec.total_features
    X = np.ones((2, spec.total_features), dtype=np.float32)
    result = standardize(X, spec)
    assert np.allclose(result, 0.0)


def test_standardize_without_params() -> None:
    report = _make_report()
    spec = build_vocab([report])
    X = np.ones((2, spec.total_features), dtype=np.float32)
    result = standardize(X, spec)
    assert np.array_equal(result, X)


def test_standardize_basic_arithmetic() -> None:
    report = _make_report()
    spec = build_vocab([report])
    n = spec.total_features
    spec.feature_means = [2.0] * n
    spec.feature_stds = [4.0] * n
    X = np.full((1, n), 10.0, dtype=np.float32)
    result = standardize(X, spec)
    assert np.allclose(result, 2.0)
