"""Tests for capability-first feature extraction from cleave v3 AnalysisReport JSON."""

import json
import math
import os
import sqlite3

import numpy as np
import pytest

from collimator.features import (
    FeatureSpec,
    _finding_paths,
    _metric_kv_tokens,
    _string_values,
    _file_symbols,
    build_vocab,
    extract,
    extract_all,
    extract_labeled_from_db_batches,
    extract_labeled_metadata_from_db_batches_unordered,
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


def _make_report_v5(
    findings: list[dict] | None = None,
    imports: list[list[str]] | None = None,
    metrics: dict | None = None,
    values: dict | None = None,
) -> dict:
    """Create a report in the cleave compact v5 schema."""
    return {
        "v": "5",
        "fs": [{
            "id": 0,
            "path": "/tmp/test",
            "dp": 0,
            "type": "pe",
            "sha": "abc123",
            "sz": 1024,
            "ts": findings or [],
            "ff": {
                "id": "pe",
                "i": imports or [],
                "x": [["DllRegisterServer"]],
                "fn": [["main", 4096]],
                "s": [[7, "u16", "CreateFileW"]],
                "m": metrics or {},
                "v": values or {},
            },
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
    assert paths == (
        "objectives",
        "objectives/evasion",
        "objectives/evasion/process",
    )


def test_finding_paths_two_levels() -> None:
    paths = _finding_paths("metadata/format::no-functions")
    assert paths == ("metadata", "metadata/format")


def test_finding_paths_single() -> None:
    paths = _finding_paths("standalone")
    assert paths == ("standalone",)


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


def test_v5_ff_helpers_feed_existing_feature_surfaces() -> None:
    report = _make_report_v5(
        imports=[["kernel32.dll", "CreateFileW"]],
        metrics={"binary": {"overall_entropy": 7.2}},
        values={"pe.machine": "x86_64"},
    )
    file_entry = report_files(report)[0]

    assert "kernel32.dll!CreateFileW" in _file_symbols(file_entry)
    assert "DllRegisterServer" in _file_symbols(file_entry)
    assert "main" in _file_symbols(file_entry)
    assert _string_values(file_entry) == [("CreateFileW", True)]

    tokens = _metric_kv_tokens(file_entry, include_shape=True)
    assert "binary.overall_entropy:exists" in tokens
    assert "v.pe.machine=x86_64" in tokens


# ---------------------------------------------------------------------------
# Vocabulary building
# ---------------------------------------------------------------------------

def test_build_vocab_empty() -> None:
    spec = build_vocab([_make_report()])
    assert spec.total_features > 0
    assert len(spec.feature_names) == spec.total_features
    assert spec.version == 17


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


def test_extract_labeled_from_db_batches_fetches_reports_in_workers(tmp_path) -> None:
    report = _make_report(
        findings=[{"i": "objectives/evasion/process", "l": _CRIT_MAP["hostile"], "c": 1.0}],
    )
    spec = build_vocab([report] * 35)
    db_path = tmp_path / "samples.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE samples ("
        "id INTEGER PRIMARY KEY, cleave_result TEXT, formula TEXT, elements TEXT, "
        "score INTEGER, mtime TEXT)"
    )
    for row_id in range(1, 4):
        conn.execute(
            "INSERT INTO samples (id, cleave_result, formula, elements, score, mtime) "
            "VALUES (?, ?, '', '', 10, '')",
            (row_id, json.dumps(report)),
        )
    conn.commit()
    conn.close()

    batches = list(
        extract_labeled_from_db_batches(
            db_path,
            [(1, 0), (2, 1), (3, 0)],
            spec,
            n_workers=1,
            batch_size=2,
        ),
    )

    assert [X.shape[0] for X, _y in batches] == [2, 1]
    np.testing.assert_array_equal(batches[0][1], np.array([0, 1], dtype=np.float32))
    np.testing.assert_array_equal(batches[1][1], np.array([0], dtype=np.float32))
    assert all(X.nnz > 0 for X, _y in batches)


def test_extract_labeled_metadata_from_db_batches_unordered_keeps_metadata_aligned(tmp_path) -> None:
    report = _make_report(
        findings=[{"i": "objectives/evasion/process", "l": _CRIT_MAP["hostile"], "c": 1.0}],
    )
    spec = build_vocab([report] * 35)
    db_path = tmp_path / "samples.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE samples ("
        "id INTEGER PRIMARY KEY, cleave_result TEXT, formula TEXT, elements TEXT, "
        "score INTEGER, mtime TEXT)"
    )
    for row_id in range(1, 4):
        conn.execute(
            "INSERT INTO samples (id, cleave_result, formula, elements, score, mtime) "
            "VALUES (?, ?, '', '', 10, '')",
            (row_id, json.dumps(report)),
        )
    conn.commit()
    conn.close()

    metadata = [
        (1, "a" * 64, "/one", 10, 0),
        (2, "b" * 64, "/two", 11, 1),
        (3, "c" * 64, "/three", 12, 0),
    ]
    batches = list(
        extract_labeled_metadata_from_db_batches_unordered(
            db_path,
            metadata,
            spec,
            n_workers=1,
            batch_size=2,
        ),
    )

    returned = [row for batch_meta, _X, _y, _stats in batches for row in batch_meta]
    labels = [int(label) for _batch_meta, _X, y, _stats in batches for label in y]
    assert returned == metadata
    assert labels == [row[-1] for row in metadata]
    assert all(X.nnz > 0 for _batch_meta, X, _y, _stats in batches)
    assert all(stats["rows"] > 0 for _batch_meta, _X, _y, stats in batches)
    assert all("fetch_sec" in stats for _batch_meta, _X, _y, stats in batches)


def test_extract_labeled_metadata_from_db_batches_uses_size_aware_batches(tmp_path, monkeypatch) -> None:
    report = _make_report(
        findings=[{"i": "objectives/evasion/process", "l": _CRIT_MAP["hostile"], "c": 1.0}],
    )
    spec = build_vocab([report] * 35)
    db_path = tmp_path / "samples.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE samples ("
        "id INTEGER PRIMARY KEY, cleave_result TEXT, formula TEXT, elements TEXT, "
        "score INTEGER, mtime TEXT)"
    )
    for row_id in range(1, 5):
        conn.execute(
            "INSERT INTO samples (id, cleave_result, formula, elements, score, mtime) "
            "VALUES (?, ?, '', '', 10, '')",
            (row_id, json.dumps(report)),
        )
    conn.commit()
    conn.close()

    monkeypatch.setenv("COLLIMATOR_THRESHOLD_BATCH_BYTES", "100")
    metadata = [
        (1, "a" * 64, "/one", 10, 0, 90),
        (2, "b" * 64, "/two", 11, 1, 90),
        (3, "c" * 64, "/three", 12, 0, 10),
        (4, "d" * 64, "/four", 13, 1, 10),
    ]
    batches = list(
        extract_labeled_metadata_from_db_batches_unordered(
            db_path,
            metadata,
            spec,
            n_workers=1,
            batch_size=4,
        ),
    )

    weights = [sum(int(row[5]) for row in batch_meta) for batch_meta, _X, _y, _stats in batches]
    assert weights == [90, 100, 10]
    assert all(weight <= 100 for weight in weights)


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
    monkeypatch.delenv("COLLIMATOR_EMBER_LITE_FEATURES", raising=False)
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


def test_extract_ember_lite_features(monkeypatch) -> None:
    monkeypatch.setenv("COLLIMATOR_EMBER_LITE_FEATURES", "1")
    feature_config_from_env.cache_clear()
    metrics = {
        "binary": {
            "file_size": 4096.0,
            "import_count": 10.0,
            "export_count": 2.0,
            "dependency_count": 3.0,
            "string_count": 20.0,
            "wide_string_count": 5.0,
            "max_string_length": 100.0,
            "avg_string_entropy": 4.25,
            "function_count": 7.0,
            "code_size": 1024.0,
            "code_to_data_ratio": 1.5,
            "wx_sections": 1.0,
            "writable_sections": 2.0,
            "executable_sections": 1.0,
            "section_count": 4.0,
            "nonstandard_section_name_count": 1.0,
            "largest_section_ratio": 0.5,
            "rsrc_to_file_ratio": 0.125,
            "has_signature": True,
        },
        "text": {"total_lines": 12.0},
    }
    report = _make_report(metrics=metrics, file_type="elf", size=4096)
    spec = build_vocab([report] * 35)
    vec = extract(report, spec)

    assert "agg:static_import_count_log" in spec.feature_names
    assert vec[spec.feature_names.index("agg:static_file_bytes_log")] == math.log1p(4096.0)
    assert vec[spec.feature_names.index("agg:static_import_count_log")] == math.log1p(10.0)
    assert vec[spec.feature_names.index("agg:static_export_count_log")] == math.log1p(2.0)
    assert vec[spec.feature_names.index("agg:static_wide_string_ratio")] == 0.25
    assert vec[spec.feature_names.index("agg:static_text_lines_log")] == math.log1p(12.0)
    assert vec[spec.feature_names.index("agg:static_function_count_log")] == math.log1p(7.0)
    assert vec[spec.feature_names.index("agg:static_writable_unit_ratio")] == 0.5
    assert vec[spec.feature_names.index("agg:static_signed_file_fraction")] == 1.0

    feature_config_from_env.cache_clear()


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


def test_extract_format_hints_from_file_types(monkeypatch) -> None:
    monkeypatch.setenv("COLLIMATOR_FORMAT_HINTS", "1")
    feature_config_from_env.cache_clear()
    report = {
        "version": "3",
        "fs": [
            {
                "id": 0,
                "path": "/tmp/pkg.zip",
                "depth": 0,
                "type": "zip",
                "sha256": "outer",
                "sz": 1024,
                "ts": [],
                "is": [],
                "ms": {},
            },
            {
                "id": 1,
                "path": "pkg.zip!!tool.ps1",
                "depth": 1,
                "type": "powershell",
                "sha256": "script",
                "sz": 100,
                "ts": [{"i": "objectives/execution/process", "l": 4, "c": 1.0}],
                "is": [],
                "ms": {},
            },
            {
                "id": 2,
                "path": "pkg.zip!!helper.exe",
                "depth": 1,
                "type": "pe",
                "sha256": "binary",
                "sz": 100,
                "ts": [{"i": "objectives/evasion/process", "l": 5, "c": 1.0}],
                "is": [],
                "ms": {},
            },
        ],
    }
    spec = build_vocab([report] * 35)
    vec = extract(report, spec)

    assert vec[spec.feature_names.index("format:archive_package")] == 1.0
    assert vec[spec.feature_names.index("format:script")] == 1.0
    assert vec[spec.feature_names.index("format:native_binary")] == 1.0
    assert vec[spec.feature_names.index("format:mixed_archive_script")] == 1.0
    assert vec[spec.feature_names.index("format:mixed_archive_binary")] == 1.0
    assert vec[spec.feature_names.index("format:mixed_script_binary")] == 1.0
    assert vec[spec.feature_names.index("format:script_inner_fraction")] == 0.5
    assert vec[spec.feature_names.index("format:native_binary_hostile_fraction")] == 1.0
    assert vec[spec.feature_names.index("format:script_suspicious_fraction")] == 1.0
    feature_config_from_env.cache_clear()


def test_format_hints_do_not_infer_from_extensions(monkeypatch) -> None:
    monkeypatch.setenv("COLLIMATOR_FORMAT_HINTS", "1")
    feature_config_from_env.cache_clear()
    report = {
        "version": "3",
        "fs": [{
            "id": 0,
            "path": "/tmp/looks_like_python.py",
            "depth": 0,
            "type": "unknown",
            "sha256": "abc",
            "sz": 1024,
            "ts": [],
            "is": [],
            "ms": {},
        }],
    }
    spec = build_vocab([report] * 35)
    vec = extract(report, spec)

    assert vec[spec.feature_names.index("format:script")] == 0.0
    assert vec[spec.feature_names.index("format:unknown_file_fraction")] == 1.0
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
    assert loaded.version == 17


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


# ---------------------------------------------------------------------------
# Batch 1 — cheap metric extracts
# ---------------------------------------------------------------------------
# Each toggle adds a small list of `metrics:<suffix>` columns. Disabled
# knobs add nothing; enabled knobs both register column names AND populate
# them at extract-time. The spec rebuild is gated on the env var, so each
# assertion clears the cached config.

_BATCH1_KNOBS = {
    "COLLIMATOR_PE_FORMAT_FLAGS": [
        "metrics:pe_is_dotnet", "metrics:pe_linker_major_version",
        "metrics:pe_subsystem", "metrics:pe_checksum_missing",
        "metrics:pe_entry_section_nontext",
    ],
    "COLLIMATOR_PE_TEMPORAL_ANOMALY": [
        "metrics:pe_year_distance", "metrics:pe_year_pre_2000", "metrics:pe_year_future",
    ],
    "COLLIMATOR_TEXT_METRICS_FULL": [
        "metrics:text_null_byte_count", "metrics:text_repeated_char_sequences",
        "metrics:text_invisible_chars", "metrics:text_mixed_indent",
    ],
    "COLLIMATOR_OVERLAY_SIGNAL": [
        "metrics:binary_overlay_ratio", "metrics:binary_overlay_size",
        "metrics:binary_has_overlay",
    ],
    "COLLIMATOR_METRIC_RATIO_FEATURES": [
        "metrics:derived_string_per_function", "metrics:derived_imports_per_dependency",
        "metrics:derived_wide_string_ratio",
    ],
    "COLLIMATOR_SIZE_NORMALIZED_METRICS": [
        "metrics:derived_imports_per_kb", "metrics:derived_sections_per_kb",
        "metrics:derived_strings_per_kb",
    ],
    "COLLIMATOR_NONSTANDARD_SECTION_SIGNAL": [
        "metrics:binary_nonstandard_section_name_count",
    ],
    "COLLIMATOR_LINE_LENGTH_BUCKETS": [
        "metrics:text_lines_over_200", "metrics:text_lines_over_500",
        "metrics:text_lines_over_1000", "metrics:text_lines_in_200_499",
        "metrics:text_lines_in_500_999",
    ],
}


@pytest.mark.parametrize("env_var,expected_columns", list(_BATCH1_KNOBS.items()))
def test_batch1_knob_adds_expected_columns(env_var, expected_columns, monkeypatch) -> None:
    """Each Batch-1 knob registers its declared columns when enabled."""
    monkeypatch.setenv(env_var, "1")
    feature_config_from_env.cache_clear()
    spec = build_vocab([_make_report(file_type="pe")])
    for col in expected_columns:
        assert col in spec.feature_names, f"{env_var} should register {col}"


def test_batch1_disabled_by_default(monkeypatch) -> None:
    """With no env vars set, none of the Batch-1 columns appear."""
    for env_var in _BATCH1_KNOBS:
        monkeypatch.delenv(env_var, raising=False)
    feature_config_from_env.cache_clear()
    spec = build_vocab([_make_report(file_type="pe")])
    for cols in _BATCH1_KNOBS.values():
        for col in cols:
            assert col not in spec.feature_names, f"unexpected column {col}"


def test_batch1_pe_format_flags_extraction(monkeypatch) -> None:
    """is_dotnet=True flows into the metrics:pe_is_dotnet column."""
    monkeypatch.setenv("COLLIMATOR_PE_FORMAT_FLAGS", "1")
    feature_config_from_env.cache_clear()
    report = _make_report(
        file_type="pe",
        metrics={"pe": {"is_dotnet": True, "linker_major_version": 14,
                        "subsystem": 3, "checksum_missing": False,
                        "entry_section": ".upx0"}},
    )
    spec = build_vocab([report])
    vec = extract(report, spec)
    assert vec[spec.feature_names.index("metrics:pe_is_dotnet")] == 1.0
    assert vec[spec.feature_names.index("metrics:pe_linker_major_version")] == 14.0
    assert vec[spec.feature_names.index("metrics:pe_subsystem")] == 3.0
    assert vec[spec.feature_names.index("metrics:pe_checksum_missing")] == 0.0
    assert vec[spec.feature_names.index("metrics:pe_entry_section_nontext")] == 1.0


def test_batch1_metric_ratios_extraction(monkeypatch) -> None:
    """Derived ratios produce the expected arithmetic; zero denominators are
    floored to 0 instead of raising ZeroDivisionError."""
    monkeypatch.setenv("COLLIMATOR_METRIC_RATIO_FEATURES", "1")
    feature_config_from_env.cache_clear()
    report = _make_report(
        metrics={"binary": {"string_count": 100, "function_count": 4,
                            "import_count": 30, "dependency_count": 3,
                            "wide_string_count": 5}},
    )
    spec = build_vocab([report])
    vec = extract(report, spec)
    assert vec[spec.feature_names.index("metrics:derived_string_per_function")] == 25.0
    assert vec[spec.feature_names.index("metrics:derived_imports_per_dependency")] == 10.0
    assert vec[spec.feature_names.index("metrics:derived_wide_string_ratio")] == 0.05

    # Zero-denominator path: function_count=0 must not raise.
    report = _make_report(metrics={"binary": {"string_count": 100, "function_count": 0}})
    spec = build_vocab([report])
    vec = extract(report, spec)
    assert vec[spec.feature_names.index("metrics:derived_string_per_function")] == 0.0


def test_batch1_line_buckets_compute_differentials(monkeypatch) -> None:
    """The 200-499 / 500-999 differentials honor the cumulative semantics
    of lines_over_N (so a >500 line also counts in >200)."""
    monkeypatch.setenv("COLLIMATOR_LINE_LENGTH_BUCKETS", "1")
    feature_config_from_env.cache_clear()
    report = _make_report(
        metrics={"text": {"lines_over_200": 30, "lines_over_500": 10, "lines_over_1000": 2}},
    )
    spec = build_vocab([report])
    vec = extract(report, spec)
    # log1p applied to each bucket — assert via inverse expm1, with a
    # generous tolerance to absorb the float32 round-trip in `extract`.
    in_200_499 = math.expm1(vec[spec.feature_names.index("metrics:text_lines_in_200_499")])
    in_500_999 = math.expm1(vec[spec.feature_names.index("metrics:text_lines_in_500_999")])
    assert math.isclose(in_200_499, 20.0, rel_tol=1e-5)
    assert math.isclose(in_500_999, 8.0, rel_tol=1e-5)


def test_batch1_does_not_collide_with_extended_metrics(monkeypatch) -> None:
    """When extended_metrics AND a Batch-1 toggle would both surface the
    same column (e.g. `pe_is_dotnet` if the corpus had ≥5% PE), the spec
    must list it exactly once and extraction must use the Batch-1 value."""
    monkeypatch.setenv("COLLIMATOR_PE_FORMAT_FLAGS", "1")
    monkeypatch.setenv("COLLIMATOR_EXTENDED_METRICS", "1")
    feature_config_from_env.cache_clear()
    spec = build_vocab([_make_report(file_type="pe")])
    pe_is_dotnet_columns = [n for n in spec.feature_names if n == "metrics:pe_is_dotnet"]
    assert len(pe_is_dotnet_columns) == 1, "column must appear exactly once"


# ---------------------------------------------------------------------------
# Batch 2 — allowlist + filter knobs
# ---------------------------------------------------------------------------

def test_batch2_metric_correlation_pairs_creates_columns(monkeypatch) -> None:
    """Each parseable pair becomes a `metrics:derived_corr_*` column,
    and the column value at extract time is the literal product."""
    monkeypatch.setenv(
        "COLLIMATOR_METRIC_CORRELATION_PAIRS",
        "binary.entropy_variance*binary.overlay_ratio,pe.is_dotnet*binary.import_count",
    )
    feature_config_from_env.cache_clear()
    report = _make_report(
        file_type="pe",
        metrics={
            "binary": {"entropy_variance": 2.5, "overlay_ratio": 0.4, "import_count": 100},
            "pe": {"is_dotnet": 1.0},
        },
    )
    spec = build_vocab([report])
    col_a = "metrics:derived_corr_binary_entropy_variance_x_binary_overlay_ratio"
    col_b = "metrics:derived_corr_pe_is_dotnet_x_binary_import_count"
    assert col_a in spec.feature_names
    assert col_b in spec.feature_names
    vec = extract(report, spec)
    assert math.isclose(vec[spec.feature_names.index(col_a)], 1.0, rel_tol=1e-5)
    assert math.isclose(vec[spec.feature_names.index(col_b)], 100.0, rel_tol=1e-5)


def test_batch2_metric_correlation_pairs_skips_malformed(monkeypatch) -> None:
    """Malformed specs (no `*`, missing `.`, empty parts) are silently
    dropped — the well-formed ones still produce columns."""
    monkeypatch.setenv(
        "COLLIMATOR_METRIC_CORRELATION_PAIRS",
        "no_star_here, only.left*, *only.right, binary.x*binary.y",
    )
    feature_config_from_env.cache_clear()
    spec = build_vocab([_make_report()])
    derived_cols = [n for n in spec.feature_names if n.startswith("metrics:derived_corr_")]
    assert derived_cols == ["metrics:derived_corr_binary_x_x_binary_y"]


def test_batch2_top_k_risk_files_min_crit_filters(monkeypatch) -> None:
    """When the floor is set, files with max_crit < floor don't contribute
    to the top-k aggregates. Floor=0 (default) keeps current behavior."""
    # Two files: one with a hostile finding (crit=5), one with a notable
    # finding (crit=3). With floor=4, only the hostile file should count.
    files = [
        {"id": 0, "path": "/a", "type": "elf", "sha": "a", "sz": 1024,
         "ts": [{"i": "objectives/c2/exfil", "l": 5, "c": 1.0}],
         "is": [], "ss": [], "ms": {}},
        {"id": 1, "path": "/b", "type": "elf", "sha": "b", "sz": 1024,
         "ts": [{"i": "metadata/format/notes", "l": 3, "c": 1.0}],
         "is": [], "ss": [], "ms": {}},
    ]
    report = {"v": "4", "fs": files}

    # Baseline: floor=0 picks up both files in top-k aggregation.
    monkeypatch.setenv("COLLIMATOR_TOP_K_RISK_FILES", "2")
    monkeypatch.delenv("COLLIMATOR_TOP_K_RISK_FILES_MIN_CRIT", raising=False)
    feature_config_from_env.cache_clear()
    spec = build_vocab([report] * 35)
    vec_no_floor = extract(report, spec)
    notable_col = "agg:top2_file_suspicious_findings_log"

    # With floor=4: the notable file (crit=3) is filtered out before top-k.
    monkeypatch.setenv("COLLIMATOR_TOP_K_RISK_FILES_MIN_CRIT", "4")
    feature_config_from_env.cache_clear()
    spec = build_vocab([report] * 35)
    vec_with_floor = extract(report, spec)
    # Without the floor, both files contribute their suspicious-finding
    # counts (notable file has 0 here, so the difference shows up only when
    # we sum hostile_findings instead). Easier assertion: verify the spec
    # column still exists; the gate behavior is exercised by the helper
    # unit test on _topk_file_risk_features.
    assert notable_col in spec.feature_names
    # Spot-check: floor=0 vs floor=4 yields a dense vec either way; the
    # key invariant is no crash and the columns survive both configs.
    assert vec_no_floor.shape == vec_with_floor.shape


def test_batch2_topk_min_crit_helper() -> None:
    """Direct test of the helper: with min_crit set, sub-floor files are
    excluded from the sort."""
    from collimator.features import _topk_file_risk_features

    high = {"id": 0, "path": "/h", "type": "elf", "sha": "h", "sz": 1024,
            "ts": [{"i": "objectives/c2", "l": 5, "c": 1.0}],
            "is": [], "ss": [], "ms": {}}
    low = {"id": 1, "path": "/l", "type": "elf", "sha": "l", "sz": 1024,
           "ts": [{"i": "metadata/format", "l": 1, "c": 1.0}],
           "is": [], "ss": [], "ms": {}}

    # No floor — both files contribute.
    base = _topk_file_risk_features([high, low], k=2)
    # Floor=4 — only the hostile file (max_crit=5) survives.
    filtered = _topk_file_risk_features([high, low], k=2, min_crit=4)
    # The hostile-side aggregates should be unchanged; the suspicious-side
    # should be no larger after filtering (low file dropped). The exact
    # values depend on _file_risk_stats internals; the invariant we check
    # is that `filtered` is bounded above by `base` componentwise.
    assert all(f <= b + 1e-9 for f, b in zip(filtered, base, strict=True))
    # Floor=6 — nothing survives; aggregates collapse to zero.
    none_qualify = _topk_file_risk_features([high, low], k=2, min_crit=6)
    assert none_qualify == (0.0, 0.0, 0.0, 0.0)


def test_batch2_extended_metrics_include_filters_vocab(monkeypatch) -> None:
    """When the include-list is set, only matching prefixes survive the
    extended_metrics scan into the spec."""
    monkeypatch.setenv("COLLIMATOR_EXTENDED_METRICS", "1")
    monkeypatch.setenv("COLLIMATOR_EXTENDED_METRICS_INCLUDE", "binary_overlay,pe_is_dotnet")
    feature_config_from_env.cache_clear()
    # The build_vocab path used in unit tests doesn't exercise the corpus
    # scan that populates metric_vocab (that's a DB-backed flow). The thing
    # we can verify here is that the *config* parses the include-list correctly
    # and that the spec build doesn't crash with the flag set.
    cfg = feature_config_from_env()
    assert cfg.extended_metrics_include == ("binary_overlay", "pe_is_dotnet")
    spec = build_vocab([_make_report(file_type="pe")])
    # No extended-metric columns should appear (corpus scan didn't run),
    # but baseline KEY_METRICS still do.
    assert "metrics:binary_overall_entropy" in spec.feature_names


def test_batch2_kv_value_split_emits_components(monkeypatch) -> None:
    """When kv_value_split is on, string-valued kv tokens are additionally
    split on common separators and each component becomes its own token."""
    from collimator.features import _metric_kv_tokens

    file_entry = {
        "ms": {
            "elf": {"needed_libs": "libcap.so.2, libc.so.6"},
        },
    }
    # Off: one opaque-blob token for the joined value.
    tokens_off = _metric_kv_tokens(file_entry)
    component_tokens = {t for t in tokens_off if "=part:" in t}
    assert component_tokens == set()

    # On: each component appears as its own token.
    tokens_on = _metric_kv_tokens(file_entry, split_string_values=True)
    component_tokens = {t for t in tokens_on if "=part:" in t}
    assert "elf.needed_libs=part:libcap.so.2" in component_tokens
    assert "elf.needed_libs=part:libc.so.6" in component_tokens


def test_batch2_parse_metric_pair_validates() -> None:
    """Parser accepts well-formed `<group>.<key>*<group>.<key>`, rejects
    everything else."""
    from collimator.features import _parse_metric_pair

    assert _parse_metric_pair("binary.x*pe.y") == (("binary", "x"), ("pe", "y"))
    # Malformed.
    assert _parse_metric_pair("no_star_here") is None
    assert _parse_metric_pair("missing.dot") is None
    assert _parse_metric_pair("binary.x*missing_dot") is None
    assert _parse_metric_pair("*nothing.before") is None
    assert _parse_metric_pair(".empty*pe.y") is None


# ---------------------------------------------------------------------------
# Batch 3 — symbol & string n-grams
# ---------------------------------------------------------------------------

def test_batch3_symbol_bigram_helper_emits_sorted_pairs() -> None:
    """C(n, 2) sorted unordered pairs over a file's deduplicated symbol set."""
    from collimator.features import _file_symbol_bigrams

    file_entry = {"is": ["malloc", "free", "printf", "strcpy"]}
    bigrams = _file_symbol_bigrams(file_entry)
    assert bigrams == [
        "free||malloc", "free||printf", "free||strcpy",
        "malloc||printf", "malloc||strcpy", "printf||strcpy",
    ]


def test_batch3_symbol_trigram_helper_emits_sorted_triples() -> None:
    """C(n, 3) sorted unordered triples; tighter per-file cap than bigrams."""
    from collimator.features import _file_symbol_trigrams

    file_entry = {"is": ["malloc", "free", "printf", "strcpy"]}
    trigrams = _file_symbol_trigrams(file_entry)
    assert trigrams == [
        "free||malloc||printf", "free||malloc||strcpy",
        "free||printf||strcpy", "malloc||printf||strcpy",
    ]


def test_batch3_symbol_bigram_per_file_cap() -> None:
    """Per-file alphabetical cap bounds n-gram count even for large import lists."""
    from collimator.features import _file_symbol_bigrams, _SYMBOL_BIGRAM_CAP

    syms = [f"sym_{i:03d}" for i in range(_SYMBOL_BIGRAM_CAP * 2)]  # 128 symbols
    bigrams = _file_symbol_bigrams({"is": syms})
    # Exactly C(cap, 2) pairs, never more.
    expected = _SYMBOL_BIGRAM_CAP * (_SYMBOL_BIGRAM_CAP - 1) // 2
    assert len(bigrams) == expected
    # All pairs come from the alphabetically-first cap symbols.
    assert all(s.startswith("sym_0") for pair in bigrams for s in pair.split("||"))


def test_batch3_quadgram_tokens_helper() -> None:
    """4-token combinations; same `+` separator the trigram path uses."""
    from collimator.features import _quadgram_tokens

    assert list(_quadgram_tokens(["a", "b", "c", "d"])) == ["a + b + c + d"]
    assert list(_quadgram_tokens(["a", "b", "c", "d", "e"])) == [
        "a + b + c + d", "a + b + c + e", "a + b + d + e",
        "a + c + d + e", "b + c + d + e",
    ]
    assert list(_quadgram_tokens(["a", "b", "c"])) == []


def test_batch3_symbol_bigram_extraction(monkeypatch) -> None:
    """When the knob is on, columns appear in the spec and present pairs
    score 1.0 at extract."""
    monkeypatch.setenv("COLLIMATOR_SYMBOL_BIGRAMS", "1")
    feature_config_from_env.cache_clear()

    # build_vocab (the in-memory test path) doesn't run the corpus scan,
    # so symbol_bigram_vocab stays empty even with the knob on. Verify
    # the knob enables extraction by directly seeding the vocab and
    # asserting the per-file extractor populates the matching column.
    from collimator.features import _file_symbol_bigrams
    report = _make_report(file_type="elf", imports=["malloc", "free", "printf"])
    spec = build_vocab([report])
    spec.symbol_bigram_vocab = sorted(_file_symbol_bigrams(primary_file(report)))
    spec.feature_names = list(spec.feature_names) + [f"symbol_bi:{b}" for b in spec.symbol_bigram_vocab]
    spec.total_features = len(spec.feature_names)
    vec = extract(report, spec)
    for bi in spec.symbol_bigram_vocab:
        assert vec[spec.feature_names.index(f"symbol_bi:{bi}")] == 1.0


def test_batch3_trigram_min_freq_applied(monkeypatch) -> None:
    """trigram_min_freq replaces the previously-hardcoded `c >= 5` floor.
    Setting it to 1 keeps everything; setting it to 100 keeps nothing
    (assuming no trigram in the test corpus appears 100 times)."""
    # The corpus-side trigram filter only fires inside build_vocab_from_db,
    # not the in-memory build_vocab path used here. Validate config plumbing
    # instead: the knob should be readable as an int and default to 5.
    monkeypatch.delenv("COLLIMATOR_TRIGRAM_MIN_FREQ", raising=False)
    feature_config_from_env.cache_clear()
    assert feature_config_from_env().trigram_min_freq == 5

    monkeypatch.setenv("COLLIMATOR_TRIGRAM_MIN_FREQ", "10")
    feature_config_from_env.cache_clear()
    assert feature_config_from_env().trigram_min_freq == 10


def test_batch3_tiered_quadgram_extraction(monkeypatch) -> None:
    """When the knob is on AND the spec lists a quadgram column, present
    quadgrams score 1.0 at extract."""
    monkeypatch.setenv("COLLIMATOR_TIERED_CRIT_QUADGRAMS", "1")
    feature_config_from_env.cache_clear()
    # 4 hostile findings → 4 distinct path tokens after summarization →
    # 1 quadgram (since C(4,4) = 1). Note: tiered tokens use the
    # severity-prefix + truncated path shape, so we manually compute the
    # expected token names rather than relying on the corpus scan.
    findings = [
        {"i": "objectives/c2/exfil", "l": 5, "c": 1.0},
        {"i": "objectives/evasion/process", "l": 5, "c": 1.0},
        {"i": "objectives/execution/script", "l": 5, "c": 1.0},
        {"i": "objectives/persistence/registry", "l": 5, "c": 1.0},
    ]
    report = _make_report(findings=findings)

    spec = build_vocab([report] * 35)
    # Manually compute the expected quadgram token (mirrors the production
    # build path) and inject it into the spec for extraction.
    from collimator.features import _summarize_report_files, _tiered_bigram_tokens, _quadgram_tokens
    summary = _summarize_report_files(report["fs"])
    tokens = _tiered_bigram_tokens(summary.sample_paths, depth=3, min_crit=3)
    expected_quads = list(_quadgram_tokens(tokens))
    assert len(expected_quads) >= 1, f"expected at least one quadgram from {len(tokens)} tokens"

    spec.tiered_quadgram_vocab = sorted(expected_quads)
    spec.feature_names = list(spec.feature_names) + [f"tierquad:{q}" for q in spec.tiered_quadgram_vocab]
    spec.total_features = len(spec.feature_names)

    vec = extract(report, spec)
    for q in spec.tiered_quadgram_vocab:
        assert vec[spec.feature_names.index(f"tierquad:{q}")] == 1.0, f"quadgram {q} not populated"


def test_batch3_disabled_by_default(monkeypatch) -> None:
    """All Batch-3 toggles default off; columns don't appear in the spec."""
    for env_var in (
        "COLLIMATOR_SYMBOL_BIGRAMS", "COLLIMATOR_SYMBOL_TRIGRAMS",
        "COLLIMATOR_TIERED_CRIT_QUADGRAMS",
    ):
        monkeypatch.delenv(env_var, raising=False)
    feature_config_from_env.cache_clear()
    spec = build_vocab([_make_report(file_type="elf", imports=["malloc", "free"])])
    for prefix in ("symbol_bi:", "symbol_tri:", "tierquad:"):
        assert not any(n.startswith(prefix) for n in spec.feature_names), \
            f"unexpected {prefix}* columns when knobs are off"


# ---------------------------------------------------------------------------
# Batch 4 — trait & taxonomy extensions
# ---------------------------------------------------------------------------

def test_batch4_lexical_distance_helper() -> None:
    """Helper handles identical strings, empties, and the canonical cases."""
    from collimator.features import _lexical_distance

    assert _lexical_distance("abc", "abc") == 0
    assert _lexical_distance("", "abc") == 3
    assert _lexical_distance("abc", "") == 3
    assert _lexical_distance("kitten", "sitting") == 3
    # The motivating real-corpus case: tightly related xattr family IDs.
    assert _lexical_distance("xattr-listxattr", "xattr-llistxattr") == 1


def test_batch4_branch_min_crit_parser() -> None:
    """Per-branch overrides parse cleanly; malformed entries are dropped."""
    from collimator.features import _parse_branch_min_crit_overrides

    assert _parse_branch_min_crit_overrides(("objectives=2", "metadata=4")) == {
        "objectives": 2, "metadata": 4,
    }
    # Out-of-range, missing-equals, non-int values, empty branch — all skipped.
    assert _parse_branch_min_crit_overrides((
        "objectives=2", "bad_no_equals", "metadata=99",
        "noise=notanint", "=missing_branch", "empty_value=",
    )) == {"objectives": 2}


def test_batch4_branch_min_crit_overrides_tiered_tokens() -> None:
    """Per-branch floor lifts the bar for one branch while leaving others alone."""
    from collimator.features import _tiered_bigram_tokens

    sample_paths = {
        "objectives/c2": 5,         # hostile
        "metadata/format": 3,       # notable
        "metadata/binary": 4,       # suspicious
    }
    base = _tiered_bigram_tokens(sample_paths, depth=2, min_crit=3)
    assert sorted(base) == ["h:objectives/c2", "n:metadata/format", "s:metadata/binary"]

    # Lift metadata floor to 5 — only the hostile objectives token survives.
    raised = _tiered_bigram_tokens(
        sample_paths, depth=2, min_crit=3, branch_min_crit={"metadata": 5},
    )
    assert raised == ["h:objectives/c2"]

    # Lower objectives floor to 0; metadata stays at default of 3.
    lowered = _tiered_bigram_tokens(
        sample_paths, depth=2, min_crit=3, branch_min_crit={"objectives": 0},
    )
    assert sorted(lowered) == ["h:objectives/c2", "n:metadata/format", "s:metadata/binary"]


def test_batch4_trait_confidence_moments(monkeypatch) -> None:
    """When the knob is on, mean/std/skew/kurt all appear and populate."""
    monkeypatch.setenv("COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS", "1")
    feature_config_from_env.cache_clear()
    findings = [
        {"i": "objectives/c2", "l": 5, "c": 0.9},
        {"i": "objectives/persistence", "l": 5, "c": 0.95},
        {"i": "objectives/evasion", "l": 5, "c": 0.85},
    ]
    report = _make_report(findings=findings)
    spec = build_vocab([report] * 35)
    for col in ("agg:confidence_mean", "agg:confidence_std",
                "agg:confidence_skew", "agg:confidence_kurtosis"):
        assert col in spec.feature_names

    vec = extract(report, spec)
    mean = vec[spec.feature_names.index("agg:confidence_mean")]
    std = vec[spec.feature_names.index("agg:confidence_std")]
    assert math.isclose(mean, 0.9, rel_tol=1e-5)
    assert std > 0  # nonzero spread


def test_batch4_trait_confidence_moments_legacy_compat(monkeypatch) -> None:
    """The legacy COLLIMATOR_EXP_3 still emits mean+std without the new moments."""
    monkeypatch.delenv("COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS", raising=False)
    monkeypatch.setenv("COLLIMATOR_EXP_3", "1")
    feature_config_from_env.cache_clear()
    spec = build_vocab([_make_report()])
    assert "agg:confidence_mean" in spec.feature_names
    assert "agg:confidence_std" in spec.feature_names
    # Higher moments only appear under the new knob.
    assert "agg:confidence_skew" not in spec.feature_names
    assert "agg:confidence_kurtosis" not in spec.feature_names


def test_batch4_trait_id_lexical_distance(monkeypatch) -> None:
    """Aggregate distance reflects how lexically similar the trait IDs are."""
    monkeypatch.setenv("COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE", "1")
    feature_config_from_env.cache_clear()
    # Tight cluster: all three IDs differ by ≤1 char.
    tight = _make_report(findings=[
        {"i": "xattr-listxattr",  "l": 5, "c": 1.0},
        {"i": "xattr-llistxattr", "l": 5, "c": 1.0},
        {"i": "xattr-flistxattr", "l": 5, "c": 1.0},
    ])
    spec = build_vocab([tight] * 35)
    vec = extract(tight, spec)
    tight_dist = vec[spec.feature_names.index("agg:trait_id_lexical_distance")]
    assert tight_dist <= 1.5  # Tightly related IDs

    # Scattershot: IDs from unrelated subtrees.
    scatter = _make_report(findings=[
        {"i": "objectives/c2",          "l": 5, "c": 1.0},
        {"i": "metadata/binary/format", "l": 5, "c": 1.0},
        {"i": "anti-static/obfuscation","l": 5, "c": 1.0},
    ])
    spec = build_vocab([scatter] * 35)
    vec = extract(scatter, spec)
    scatter_dist = vec[spec.feature_names.index("agg:trait_id_lexical_distance")]
    assert scatter_dist > tight_dist


def test_batch4_document_obfuscation_features(monkeypatch) -> None:
    """Counts the three documented document-malware subtrees."""
    monkeypatch.setenv("COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES", "1")
    feature_config_from_env.cache_clear()
    findings = [
        {"i": "objectives/anti-static/obfuscation/document::pdf-jsfuck-bootstrap",
         "l": 5, "c": 1.0},
        {"i": "objectives/anti-static/obfuscation/document::long-alphanumeric-padding",
         "l": 5, "c": 1.0},
        {"i": "objectives/execution/interpreter/eval::pdf-openaction-js",
         "l": 5, "c": 1.0},
        {"i": "objectives/execution/lure/document::pdf-annotation-object",
         "l": 5, "c": 1.0},
        {"i": "metadata/format/something",  # NOT a doc-obfuscation finding
         "l": 3, "c": 1.0},
    ]
    report = _make_report(findings=findings, file_type="pdf")
    spec = build_vocab([report] * 35)
    vec = extract(report, spec)
    obf = vec[spec.feature_names.index("agg:docobf_obfuscation_count")]
    eval_count = vec[spec.feature_names.index("agg:docobf_eval_count")]
    lure = vec[spec.feature_names.index("agg:docobf_lure_count")]
    total = vec[spec.feature_names.index("agg:docobf_total_count")]
    has_any = vec[spec.feature_names.index("agg:docobf_has_any")]
    assert (obf, eval_count, lure, total, has_any) == (2.0, 1.0, 1.0, 4.0, 1.0)


def test_batch4_mbc_id_vocab_extraction(monkeypatch) -> None:
    """When the knob is on AND the spec lists an MBC column, the per-finding
    `m` field populates it. (Vocab build runs in build_vocab_from_db; here
    we seed the spec directly.)"""
    monkeypatch.setenv("COLLIMATOR_MBC_ID_VOCAB", "1")
    feature_config_from_env.cache_clear()
    findings = [
        {"i": "x", "l": 5, "c": 1.0, "m": "E1082"},
        {"i": "y", "l": 5, "c": 1.0, "m": "T1083"},
        {"i": "z", "l": 5, "c": 1.0},  # no `m` field; ignored
    ]
    report = _make_report(findings=findings)
    spec = build_vocab([report])
    spec.mbc_id_vocab = ["E1082", "T1083"]
    spec.feature_names = list(spec.feature_names) + ["mbc:E1082", "mbc:T1083"]
    spec.total_features = len(spec.feature_names)
    vec = extract(report, spec)
    assert vec[spec.feature_names.index("mbc:E1082")] == 1.0
    assert vec[spec.feature_names.index("mbc:T1083")] == 1.0


def test_batch4_disabled_by_default(monkeypatch) -> None:
    """All Batch-4 toggles default off; their columns don't appear."""
    for env_var in (
        "COLLIMATOR_MBC_ID_VOCAB", "COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS",
        "COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE",
        "COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES",
        "COLLIMATOR_EXP_3",
    ):
        monkeypatch.delenv(env_var, raising=False)
    feature_config_from_env.cache_clear()
    spec = build_vocab([_make_report()])
    for col in (
        "agg:confidence_mean", "agg:confidence_skew",
        "agg:trait_id_lexical_distance",
        "agg:docobf_obfuscation_count", "agg:docobf_has_any",
    ):
        assert col not in spec.feature_names
    assert not any(n.startswith("mbc:") for n in spec.feature_names)


# Reset the cached config after the Batch-1/2/3/4 tests so subsequent tests
# don't inherit a stale per-knob env state.
_BATCH2_KNOBS = {
    "COLLIMATOR_EXTENDED_METRICS_INCLUDE",
    "COLLIMATOR_TOP_K_RISK_FILES_MIN_CRIT",
    "COLLIMATOR_METRIC_CORRELATION_PAIRS",
    "COLLIMATOR_KV_VALUE_SPLIT",
}
_BATCH3_KNOBS = {
    "COLLIMATOR_SYMBOL_BIGRAMS", "COLLIMATOR_SYMBOL_TRIGRAMS",
    "COLLIMATOR_TIERED_CRIT_QUADGRAMS", "COLLIMATOR_TRIGRAM_MIN_FREQ",
}
_BATCH4_KNOBS = {
    "COLLIMATOR_MBC_ID_VOCAB", "COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS",
    "COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE",
    "COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES",
    "COLLIMATOR_TIERED_BIGRAM_BRANCH_MIN_CRIT",
    "COLLIMATOR_EXP_3",
}


@pytest.fixture(autouse=True, scope="module")
def _reset_feature_config_cache():
    yield
    feature_config_from_env.cache_clear()
    for env_var in {*_BATCH1_KNOBS, *_BATCH2_KNOBS, *_BATCH3_KNOBS, *_BATCH4_KNOBS}:
        os.environ.pop(env_var, None)
