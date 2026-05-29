"""Extract fixed-size numeric feature vectors from cleave v3 AnalysisReport JSON.

This module is intentionally one file. The ~30 ``_apply_*`` per-family
extractors share a layer of local helpers (``_crit_category_tokens``,
``_tiered_bigram_tokens``, ``_metric_kv_tokens``, ``_file_risk_stats``,
``_summarize_findings``, etc.) that aren't exposed elsewhere; splitting
them across modules forces those helpers to be either re-implemented or
exposed as cross-module API, neither of which improves clarity. The layout
below is the navigation key — sections are stable enough that line ranges
are accurate at the time of a release commit.

Section map (line ranges approximate):

  ── Configuration & spec ─────────────────────────────────
   ~120    _crit_category_tokens, _tiered_bigram_tokens
   ~219    FeatureConfig dataclass
   ~318    feature_config_from_env (env-driven knob loader)
   ~492    Report normalization helpers (file_symbols, metric_kv, ...)
   ~687    FeatureSpec (vocabulary + feature-name list)
   ~812    allowed_features
   ~829    _build_feature_names (the feature ordering decision)

  ── Vocabulary building ──────────────────────────────────
   ~1262   build_vocab (in-memory reports)
   ~3257   _vocab_*_worker (multiprocess workers)
   ~4098   build_vocab_from_db (DB-driven streaming)

  ── Per-family extractors (the _apply_* layer) ──────────
   ~1487   Summarization helpers (_summarize_findings, _file_risk_stats)
   ~1749   _apply_presence_features through _apply_aggregate_features
   ~2005   _apply_experimental_features
   ~2204   _apply_external_signal_features
   ~2234   _apply_ember_lite_features
   ~2317   _apply_metric_features
   ~2349+  _apply_{symbol,kv,text_encoding,filetype,format_hint,element,
                    formula,score,structural,neg_space,bigram,tiered_bigram,
                    tiered_trigram,ghost,skeleton,rare_element,trigram,
                    logic_gap,signature_synergy,intent_gap,cluster}_features

  ── Top-level extract drivers ────────────────────────────
   ~3053   _extract_into (the master applier — calls every _apply_*)
   ~3257-3955  Worker pool batch wrappers + extract / extract_all /
              extract_stream / extract_partitioned / extract_labeled paths

  ── Output utilities ─────────────────────────────────────
   ~4570   standardize, feature_group_indices, drop_feature_prefixes

The historical commentary below describes the model's first design
intuition — kept because the current feature surface still embodies it.



v15: Capability-first features plus hostile-escalation signals.

The ML pipeline exists because cleave's criticality judgments are imperfect.
The model must learn malicious *capability combinations* independently from
cleave's tier assignments. Cleave is good at identifying what capabilities
exist; it's less reliable at judging how severe they are. So we give the
model two complementary views per finding path:

  Presence (binary): "does this capability exist?" — the primary signal for
  learning malicious combinations. When 91k benign samples also have a path,
  the model automatically learns to discount it. This works even when cleave
  gets criticality wrong.

  Max criticality (ordinal 0-5): "how severe does cleave rate it?" — a
  gradient signal the model can use when helpful, but can't over-rely on
  since it's a single value per path rather than 3 binary thresholds.

Feature groups:
  1. Path Presence: binary features for path existing at any crit ≥ baseline
  2. Path Max Criticality: ordinal (0-5) per path in presence vocab
  3. Path Aggregates: breadth, concentration, and finding-density signals (20)
  4. Third-Party / Well-Known Summary: aggregated match signals (6)
  5. Key Metrics: curated binary/text/PE metrics (16)
  6. File Type: multi-hot across all files in the report
  7. Structural: report/container context (6)
"""

from __future__ import annotations

import collections
import json
import logging
import math
import multiprocessing as mp
import os
import re
import subprocess
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path
from collections.abc import Iterable, Iterator
from itertools import islice
from typing import Any, TypeVar
from datetime import datetime

import numpy as np
import scipy.sparse as sp
import scipy.stats as stats

log = logging.getLogger(__name__)
T = TypeVar("T")
LabeledMetadata = tuple[int, str, str, int, int] | tuple[int, str, str, int, int, int]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# v4: criticality is already an integer ordinal (0-5) in the JSON.
# 0=filtered, 1=component, 2=baseline, 3=notable, 4=suspicious, 5=hostile

# Minimum number of samples a path must appear in to get a feature.
MIN_PATH_FREQ = 5


# Minimum confidence for a finding to be included in feature extraction.
# Low-confidence findings add noise without meaningful signal.
MIN_CONFIDENCE = 0.65

# Number of riskiest files to summarize for package-level top-k signals.
TOP_K_RISK_FILES = 1

# Stable model ABI version shared with litmus.
# Keep this in sync with FeatureSpec.version for a single compatibility number.
#
# Spec version tracks the FEATURE SCHEMA (what features each model
# expects, which COLLIMATOR_* env knobs are honored), not the model
# file format. Adding ONNX as an alternate serialization (.onnx
# alongside .txt; landed with litmus 1.3.0) did NOT change the schema —
# the same FeatureSpec is emitted regardless of which file format the
# model is stored in. Older litmus (1.2.x) reading a v17 bundle that
# now ships .onnx + .txt silently ignores the .onnx and uses the .txt;
# fully forward-compatible. Bump this when feature families are added
# or removed (last bump: v17 added cluster:* + agg:static_*).
MODEL_ABI_VERSION = 17

# Curated code metrics — covers binary, text, string, and PE analysis.
# Each entry is (metric_group, field_name, use_log1p).
KEY_METRICS: list[tuple[str, str, bool]] = [
    # Binary structure
    ("binary", "overall_entropy", False),
    ("binary", "code_entropy", False),
    ("binary", "code_to_data_ratio", False),
    ("binary", "function_count", True),
    ("binary", "complexity_per_kb", False),
    ("binary", "max_complexity", False),
    ("binary", "normalized_string_count", False),
    ("binary", "high_entropy_regions", False),
    # Text analysis
    ("text", "char_entropy", False),
    ("text", "unique_chars", True),
    ("text", "whitespace_ratio", False),
    ("text", "most_common_ratio", False),
    ("text", "total_lines", True),
    # String analysis
    ("strings", "avg_entropy", False),
    # PE-specific
    ("pe", "rsrc_entropy", False),
    ("pe", "rsrc_size", True),
]

# Metric keys where log1p should be applied (counts, sizes, lengths).
_LOG_METRIC_WORDS = frozenset({"count", "size", "total", "bytes", "length"})


# ---------------------------------------------------------------------------
# Batch 1 — cheap metric extracts (gated per-knob, optional)
# ---------------------------------------------------------------------------
# Each Batch-1 knob exposes a list of metric columns in the existing
# `metrics:<suffix>` namespace. Columns are added to the feature spec only
# when the knob is enabled, so disabled knobs cost nothing and don't affect
# cached feature_specs of routes that never turn them on.
#
# A "getter" reads the merged ms.* dict and returns a float. For values that
# don't survive the per-file → per-report max-aggregation (strings like
# entry_section), the getter takes the raw `files` list as a fallback source.
# Boolean cleave fields are converted to 0/1 via _metric_bool. Use_log1p
# follows KEY_METRICS — log1p for counts/sizes, raw for ratios/booleans.

# Each entry: (column_suffix, getter(metrics, files) -> float, use_log1p).
# The full column name is "metrics:" + column_suffix.
_Batch1Entry = tuple[str, "Callable[[dict, list[dict]], float]", bool]


def _pe_entry_section_nontext(_metrics: dict, files: list[dict]) -> float:
    """1.0 if any file's PE entry section isn't .text. Strings don't survive
    metric max-aggregation, so we scan files directly."""
    for f in files:
        es = ((file_metrics(f).get("pe") or {}).get("entry_section"))
        if isinstance(es, str) and es and es != ".text":
            return 1.0
    return 0.0


def _pe_year_distance(metrics: dict, _files: list[dict]) -> float:
    y = _metric_number(metrics, "pe", "timestamp_year")
    if y <= 0:
        return 0.0
    from datetime import datetime  # noqa: PLC0415 — stdlib, local for cold path
    return float(abs(datetime.now().year - y))


def _ratio(num: float, denom: float) -> float:
    return num / denom if denom > 0 else 0.0


# pe_format_flags — 5 PE flag-shape extracts.
_BATCH1_PE_FORMAT_FLAGS: list[_Batch1Entry] = [
    ("pe_is_dotnet",             lambda m, _f: float(_metric_bool(m, "pe", "is_dotnet")),       False),
    ("pe_linker_major_version",  lambda m, _f: _metric_number(m, "pe", "linker_major_version"), False),
    ("pe_subsystem",             lambda m, _f: _metric_number(m, "pe", "subsystem"),            False),
    ("pe_checksum_missing",      lambda m, _f: float(_metric_bool(m, "pe", "checksum_missing")),False),
    ("pe_entry_section_nontext", _pe_entry_section_nontext,                                     False),
]

# pe_temporal_anomaly — distance from current year + 1970/future flags.
_BATCH1_PE_TEMPORAL: list[_Batch1Entry] = [
    ("pe_year_distance", _pe_year_distance,                                                           True),
    ("pe_year_pre_2000", lambda m, _f: 1.0 if 0 < _metric_number(m, "pe", "timestamp_year") < 2000 else 0.0, False),
    ("pe_year_future",   lambda m, _f: 1.0 if _metric_number(m, "pe", "timestamp_year") > 2030 else 0.0,     False),
]

# text_metrics_full — promote ~25 ms.text.* fields. Currently only
# char_entropy/unique_chars/whitespace_ratio/most_common_ratio/total_lines
# are in KEY_METRICS; the rest of the text block sits idle, despite being
# the most-distinguishing signal we found between good/bad PDFs.
_TEXT_FULL_FIELDS: list[tuple[str, bool]] = [
    ("non_ascii_ratio", False), ("non_printable_ratio", False), ("null_byte_count", True),
    ("high_byte_ratio", False), ("avg_line_length", True), ("max_line_length", True),
    ("line_length_stddev", True), ("last_line_length", True), ("empty_line_ratio", False),
    ("tab_count", True), ("space_count", True), ("trailing_whitespace_lines", True),
    ("unusual_whitespace", True), ("max_inline_whitespace_run", True),
    ("unicode_escape_count", True), ("octal_escape_count", True), ("escape_density", False),
    ("invisible_chars", True), ("long_token_count", True),
    ("repeated_char_sequences", True), ("digit_ratio", False),
]
_BATCH1_TEXT_FULL: list[_Batch1Entry] = [
    (f"text_{f}", (lambda m, _f, f=f: _metric_number(m, "text", f)), use_log)
    for f, use_log in _TEXT_FULL_FIELDS
] + [
    ("text_mixed_indent", lambda m, _f: float(_metric_bool(m, "text", "mixed_indent")), False),
]

# overlay_signal_features — promote overlay metrics from the one-shot
# threshold check at line ~2134 to continuous features.
_BATCH1_OVERLAY: list[_Batch1Entry] = [
    ("binary_overlay_ratio",   lambda m, _f: _metric_number(m, "binary", "overlay_ratio"),   False),
    ("binary_overlay_entropy", lambda m, _f: _metric_number(m, "binary", "overlay_entropy"), False),
    ("binary_overlay_size",    lambda m, _f: _metric_number(m, "binary", "overlay_size"),    True),
    ("binary_has_overlay",     lambda m, _f: float(_metric_bool(m, "binary", "has_overlay")), False),
]

# metric_ratio_features — derived cross-metric ratios. Trees can in
# principle learn these, but pre-engineering helps on small corpora where
# the tree can't afford to discover every interaction itself.
_BATCH1_RATIOS: list[_Batch1Entry] = [
    ("derived_string_per_function",
     lambda m, _f: _ratio(_metric_number(m, "binary", "string_count"),
                          _metric_number(m, "binary", "function_count")), False),
    ("derived_imports_per_dependency",
     lambda m, _f: _ratio(_metric_number(m, "binary", "import_count"),
                          _metric_number(m, "binary", "dependency_count")), False),
    ("derived_wide_string_ratio",
     lambda m, _f: _ratio(_metric_number(m, "binary", "wide_string_count"),
                          _metric_number(m, "binary", "string_count")), False),
]

# size_normalized_metrics — raw structural counts divided by file size in
# KB. Distinct from the existing finding-density features (which normalize
# *finding* counts).
_BATCH1_SIZE_NORMALIZED: list[_Batch1Entry] = [
    ("derived_imports_per_kb",
     lambda m, _f: _ratio(_metric_number(m, "binary", "import_count"),
                          _metric_number(m, "binary", "file_size") / 1024.0), False),
    ("derived_sections_per_kb",
     lambda m, _f: _ratio(_metric_number(m, "binary", "section_count"),
                          _metric_number(m, "binary", "file_size") / 1024.0), False),
    ("derived_strings_per_kb",
     lambda m, _f: _ratio(_metric_number(m, "binary", "string_count"),
                          _metric_number(m, "binary", "file_size") / 1024.0), False),
]

# nonstandard_section_signal — promote one binary metric to a feature.
_BATCH1_NONSTANDARD_SECTION: list[_Batch1Entry] = [
    ("binary_nonstandard_section_name_count",
     lambda m, _f: _metric_number(m, "binary", "nonstandard_section_name_count"), True),
]

# line_length_bucket_histogram — explicit bucketed histogram + the per-
# bucket differentials (lines in 200-499 range vs 500-999 range).
_BATCH1_LINE_BUCKETS: list[_Batch1Entry] = [
    ("text_lines_over_200",  lambda m, _f: _metric_number(m, "text", "lines_over_200"),  True),
    ("text_lines_over_500",  lambda m, _f: _metric_number(m, "text", "lines_over_500"),  True),
    ("text_lines_over_1000", lambda m, _f: _metric_number(m, "text", "lines_over_1000"), True),
    ("text_lines_in_200_499",
     lambda m, _f: max(0.0, _metric_number(m, "text", "lines_over_200")
                            - _metric_number(m, "text", "lines_over_500")), True),
    ("text_lines_in_500_999",
     lambda m, _f: max(0.0, _metric_number(m, "text", "lines_over_500")
                            - _metric_number(m, "text", "lines_over_1000")), True),
]


def _batch1_enabled_tables(config: "FeatureConfig") -> list[list[_Batch1Entry]]:
    """Ordered list of Batch-1 tables whose knob is enabled in `config`."""
    out: list[list[_Batch1Entry]] = []
    if config.include_pe_format_flags:            out.append(_BATCH1_PE_FORMAT_FLAGS)
    if config.include_pe_temporal_anomaly:        out.append(_BATCH1_PE_TEMPORAL)
    if config.include_text_metrics_full:          out.append(_BATCH1_TEXT_FULL)
    if config.include_overlay_signal:             out.append(_BATCH1_OVERLAY)
    if config.include_metric_ratio_features:      out.append(_BATCH1_RATIOS)
    if config.include_size_normalized_metrics:    out.append(_BATCH1_SIZE_NORMALIZED)
    if config.include_nonstandard_section_signal: out.append(_BATCH1_NONSTANDARD_SECTION)
    if config.include_line_length_buckets:        out.append(_BATCH1_LINE_BUCKETS)
    return out


def _batch1_column_suffixes(config: "FeatureConfig") -> list[str]:
    """All Batch-1 column suffixes this config enables (no `metrics:` prefix)."""
    return [suffix for table in _batch1_enabled_tables(config) for suffix, _, _ in table]


# ---------------------------------------------------------------------------
# Batch 2 — allowlist + filter knobs
# ---------------------------------------------------------------------------
# `metric_correlation_pairs` accepts a CSV of `<group_a>.<key_a>*<group_b>.<key_b>`
# pair specs and exposes each as a derived `metrics:derived_corr_*` column.
# Trees can in principle learn pairwise interactions, but pre-engineering
# them helps on small corpora where the tree can't afford to discover
# every interaction itself.

def _parse_metric_pair(spec: str) -> tuple[tuple[str, str], tuple[str, str]] | None:
    """Parse a `<group_a>.<key_a>*<group_b>.<key_b>` pair spec.

    Returns ((group_a, key_a), (group_b, key_b)) or None if malformed.
    """
    if "*" not in spec:
        return None
    a, _, b = spec.partition("*")
    a_parts = a.strip().split(".", 1)
    b_parts = b.strip().split(".", 1)
    if len(a_parts) != 2 or len(b_parts) != 2:
        return None
    if not all(p.strip() for p in a_parts + b_parts):
        return None
    return (a_parts[0].strip(), a_parts[1].strip()), (b_parts[0].strip(), b_parts[1].strip())


_MetricPair = tuple[str, str]
_CorrelationColumn = tuple[str, _MetricPair, _MetricPair]


def _metric_correlation_columns(config: "FeatureConfig") -> list[_CorrelationColumn]:
    """For each parseable pair spec, return (column_suffix, a, b)."""
    out: list[_CorrelationColumn] = []
    for raw in config.metric_correlation_pairs:
        parsed = _parse_metric_pair(raw)
        if parsed is None:
            continue
        a, b = parsed
        suffix = f"derived_corr_{a[0]}_{a[1]}_x_{b[0]}_{b[1]}"
        out.append((suffix, a, b))
    return out


_CRIT_PREFIX = {3: "n", 4: "s", 5: "h"}  # notable, suspicious, hostile

# Top-level categories included in crit-category n-grams.
# objectives/* and well-known/* are attack-intent categories.
# Others (micro-behaviors, metadata) can be added but may add noise.
_CRIT_NGRAM_CATEGORIES = frozenset({
    "objectives", "well-known", "supply-chain",
    "anti-analysis", "anti-static", "command-and-control",
    "evasion", "execution", "exfiltration",
})


def _crit_category_tokens(sample_paths: dict[str, int]) -> list[str]:
    """Generate sorted crit:category tokens from sample_paths.

    Uses 2nd-level path (e.g., objectives/anti-analysis → objectives/anti-analysis)
    prefixed with max criticality: h:objectives/evasion, s:objectives/c2.
    Only includes paths under attack-relevant top-level categories.
    """
    path_max_crit: dict[str, int] = {}
    for path, max_ord in sample_paths.items():
        if max_ord < 3:
            continue
        parts = path.split("/")
        top = parts[0]
        if top not in _CRIT_NGRAM_CATEGORIES:
            continue
        # Use 2nd-level for specificity: objectives/anti-analysis, not just objectives
        key = "/".join(parts[:2]) if len(parts) >= 2 else top
        if max_ord > path_max_crit.get(key, 0):
            path_max_crit[key] = max_ord
    return sorted(f"{_CRIT_PREFIX.get(crit, 'n')}:{key}" for key, crit in path_max_crit.items())


def _parse_branch_min_crit_overrides(items: tuple[str, ...]) -> dict[str, int]:
    """Parse `<branch>=<min_crit>` overrides for tiered_bigram min-crit gating.

    Skips malformed entries silently. Branches are matched against a
    finding's top-level path component (e.g. `objectives` matches
    `objectives/evasion/process`).
    """
    out: dict[str, int] = {}
    for raw in items:
        if "=" not in raw:
            continue
        branch, _, value = raw.partition("=")
        branch = branch.strip()
        try:
            crit = int(value.strip())
        except ValueError:
            continue
        if branch and 0 <= crit <= 5:
            out[branch] = crit
    return out


def _tiered_bigram_tokens(
    sample_paths: dict[str, int],
    *,
    depth: int,
    min_crit: int,
    branch_min_crit: dict[str, int] | None = None,
) -> list[str]:
    """Generate severity-prefixed report-level path tokens for tiered bigrams.

    When `branch_min_crit` is supplied, the per-branch floor (matched against
    the path's top-level component) overrides the global `min_crit`. Branches
    not in the map fall back to `min_crit`. Lets autocollie set tighter floors
    on noisy branches (e.g. `metadata=4`) and looser on signal-dense ones
    (e.g. `objectives=2`).
    """
    token_max_crit: dict[str, int] = {}
    branch_min_crit = branch_min_crit or {}
    for path, max_ord in sample_paths.items():
        branch = path.split("/", 1)[0]
        floor = branch_min_crit.get(branch, min_crit)
        if max_ord < floor:
            continue
        key = _truncate_path(path, depth)
        if max_ord > token_max_crit.get(key, 0):
            token_max_crit[key] = max_ord
    return sorted(f"{_CRIT_PREFIX.get(crit, 'n')}:{path}" for path, crit in token_max_crit.items())


def _quadgram_tokens(tokens: list[str]) -> "Iterator[str]":
    """Yield 4-token combinations as `t1 + t2 + t3 + t4` strings.

    Mirrors the tiered_trigram pattern (`t1 + t2 + t3`) one order up.
    Tokens are assumed already sorted; combinations preserve that order.
    """
    n = len(tokens)
    for i in range(n):
        t1 = tokens[i]
        for j in range(i + 1, n):
            t2 = tokens[j]
            for k in range(j + 1, n):
                t3 = tokens[k]
                for m in range(k + 1, n):
                    yield f"{t1} + {t2} + {t3} + {tokens[m]}"

LOGIC_GAPS = {
    # Behavior Category -> (List of imports that imply it, List of trait paths that represent it)
    "network": (
        {"socket", "urllib", "requests", "http", "curl", "wininet", "winhttp"},
        {"micro-behaviors/network", "objectives/command-and-control"},
    ),
    "process": (
        {"subprocess", "os.spawn", "os.system", "CreateProcess", "ShellExecute", "posix_spawn"},
        {"micro-behaviors/process/create", "objectives/execution"},
    ),
    "crypto": (
        {"cryptography", "Crypto", "hashlib", "CryptAcquireContext", "BCryptOpenAlgorithmProvider"},
        {"micro-behaviors/crypto", "metadata/encoded-payload"},
    ),
}

EXPECTED_GHOSTS = {
    "pe": [
        "metadata/binary/layout",
        "metadata/binary/metrics",
        "metadata/binary/resource",
        "metadata/binary/symbols",
        "metadata/binary/linking",
    ],
    "elf": [
        "metadata/binary/layout",
        "metadata/binary/metrics",
        "metadata/binary/symbols",
        "metadata/binary/linking",
    ],
    "javascript": [
        "micro-behaviors/javascript/async",
        "metadata/package/versioning",
    ],
}

FEATURE_GROUPS = ("present", "maxcrit", "agg", "ext", "metrics", "filetype", "format", "struct", "elements", "formula", "score", "bigrams", "tiered_bigrams", "tiered_trigrams", "ghosts", "skeletons", "rares", "trigrams", "logic_gaps", "signature_synergy", "clusters", "intent_gaps", "neg_space", "symbols", "kv", "textenc")

FORMAT_GROUPS: dict[str, frozenset[str]] = {
    "script": frozenset({
        "batch", "javascript", "lua", "perl", "php", "powershell", "python",
        "ruby", "shell", "typescript", "vbscript",
    }),
    "native_binary": frozenset({"elf", "macho", "pe"}),
    "archive_package": frozenset({
        "7z", "apk", "cab", "deb", "egg", "gz", "jar", "msi", "rar", "rpm",
        "tar", "tgz", "vsix", "war", "whl", "xpi", "xz", "zip", "zst",
    }),
    "document": frozenset({"doc", "docx", "html", "pdf", "ppt", "pptx", "rtf", "xls", "xlsx"}),
    "source_code": frozenset({
        "c", "cpp", "csharp", "go", "java", "kotlin", "makefile", "rust",
        "scala", "swift",
    }),
    "config_data": frozenset({"ini", "json", "plist", "toml", "xml", "yaml", "yml"}),
    "media": frozenset({"bmp", "gif", "jpg", "jpeg", "mp3", "mp4", "png", "svg", "webp"}),
}

_FORMAT_GROUP_ORDER = tuple(FORMAT_GROUPS)


@dataclass(frozen=True, slots=True)
class FeatureConfig:
    """Experiment-only feature layout toggles controlled via environment."""

    enabled_groups: frozenset[str]
    top_k_risk_files: int
    include_struct_file_risk_coverage: bool
    include_suspicious_breadth_density: bool
    include_hostile_escalation_features: bool
    include_hostile_weighted_density: bool
    include_repetition_penalty_features: bool
    include_file_severity_distribution: bool
    include_score_weighted_traits: bool
    include_soft_presence: bool
    include_blindfold: bool
    include_silent_packer_signal: bool
    include_mtime_kurtosis: bool
    include_air_gap_signal: bool
    include_extreme_features: bool
    # If False, drops inter:{ft}*{element} and inter:{ft}*{skeleton} cross-products
    # (~163k mostly-useless features in v15). inter:{ft}*score is always kept.
    include_filetype_interactions: bool
    include_format_hints: bool
    # Individual extreme-feature toggles (Exps 48, 49, 51, 54, 55, 56).
    # Each defaults to include_extreme_features for backwards compatibility.
    include_anachronistic_injection: bool
    include_code_entropy_spike: bool
    include_foreign_binary_signal: bool
    include_extension_mismatch_signal: bool
    include_hostile_finding_density: bool
    include_hostile_depth_weight: bool
    # N-gram path depth: 0 = full base path (default), 2/3 = truncate finding
    # IDs to that many directory levels before generating bigrams/trigrams.
    # Coarser paths produce more generalizable n-grams.
    ngram_path_depth: int
    # N-gram minimum criticality: only findings at this level or above
    # participate in bigram/trigram generation. 0 = all (default/current),
    # 1 = component+, 2 = baseline+, 3 = notable+, 4 = suspicious+, 5 = hostile.
    ngram_min_crit: int
    # Taxonomy-exploitation features: kill chain span, cross-domain
    # co-occurrence, depth signal, and objective/micro-behavior ratio.
    include_taxonomy_features: bool
    # Experimental feature batch (2026-04-13): 10 new features, each
    # individually toggleable via COLLIMATOR_EXP_<N>=1 for screening.
    include_extended_metrics: bool   # all numeric ms.* metrics from vocab scan
    include_ember_lite_features: bool # portable EMBER-style aggregates from ms.* metrics
    bigram_max: int                  # max bigram vocab size
    bigram_min_freq: int             # min frequency for bigram inclusion
    trigram_max: int                 # max trigram vocab size
    trigram_max_benign_frac: float   # max benign fraction for trigram inclusion
    include_attack_features: bool    # ATT&CK technique/tactic features from 'a' field
    include_confidence_weighted_ngrams: bool  # weight bigrams/trigrams by confidence
    # Targeted n-gram variants for catching low-density malware patterns.
    include_objective_trigrams: bool  # count-based objective path combos (deprecated)
    include_suspicious_trigrams: bool # count-based suspicious+ combos (deprecated)
    include_attack_ngrams: bool      # count-based ATT&CK code combos (deprecated)
    # Crit-category n-grams: vocab-based bigrams/trigrams from "crit:category"
    # tokens. e.g., "s:anti-analysis + s:command-and-control + n:evasion".
    # Tokens: h:=hostile, s:=suspicious, n:=notable, top-level category.
    # Small stable vocabulary discovered from training data.
    include_crit_category_ngrams: bool
    # Vocab-based ATT&CK technique and MBC behavior n-grams.
    # Builds bigram/trigram vocabs from T-codes and MBC B-codes
    # discovered in training data.
    include_attack_code_ngrams: bool
    # Report-level severity-prefixed trait bigrams from notable+ paths.
    # This is intentionally separate from generic per-file bigrams so it can
    # be ablated independently. Default production setting is depth=3,
    # min_crit=3, matching the scripts-pool sweep winner.
    include_tiered_crit_bigrams: bool
    tiered_bigram_path_depth: int
    tiered_bigram_min_crit: int
    tiered_bigram_max: int
    tiered_bigram_min_freq: int
    include_tiered_crit_trigrams: bool
    tiered_trigram_path_depth: int
    tiered_trigram_min_crit: int
    tiered_trigram_max: int
    tiered_trigram_min_freq: int
    include_symbol_vocab: bool
    symbol_vocab_max: int
    symbol_min_freq: int
    include_kv_vocab: bool
    kv_vocab_max: int
    kv_min_freq: int
    include_kv_shape_features: bool
    include_text_encoding_features: bool
    exp_import_categories: bool      # 1: import functional category count
    exp_suspicious_api_combo: bool   # 2: suspicious API category co-occurrence
    exp_confidence_skew: bool        # 3: finding confidence distribution skew
    exp_finding_depth_var: bool      # 4: taxonomy depth variance
    exp_multifile_crit_spread: bool  # 5: max crit difference across files
    exp_metric_anomaly: bool         # 6: composite metric anomaly score
    exp_unsigned_import_density: bool # 7: unsigned × import density interaction
    exp_entropy_hostile: bool        # 8: entropy × hostile concentration
    exp_hostile_objective_div: bool  # 9: hostile-level objective category diversity
    exp_import_finding_ratio: bool   # 10: import count / finding count ratio
    # Batch 1: cheap metric extracts. Each toggle adds a small list of
    # `metrics:<suffix>` columns; see _BATCH1_* tables above for the exact
    # column names. All default off so disabled knobs cost nothing.
    include_pe_format_flags: bool
    include_pe_temporal_anomaly: bool
    include_text_metrics_full: bool
    include_overlay_signal: bool
    include_metric_ratio_features: bool
    include_size_normalized_metrics: bool
    include_nonstandard_section_signal: bool
    include_line_length_buckets: bool
    # Batch 2: allowlist + filter knobs. Allow autocollie to dial in finer
    # selections of existing infrastructure without all-or-nothing toggles.
    # Non-empty extended_metrics_include restricts the extended_metrics scan
    # to keys matching one of those `<group>_<key>` prefixes.
    extended_metrics_include: tuple[str, ...]
    # Min cleave-crit floor for files eligible for top-k risk aggregation.
    # 0 = no floor (current behavior).
    top_k_risk_files_min_crit: int
    # CSV of `<group_a>.<key_a>*<group_b>.<key_b>` pairs exposed as derived
    # `metrics:derived_corr_*` columns (pre-computed pairwise products).
    metric_correlation_pairs: tuple[str, ...]
    # Additionally split string-valued kv tokens on common separators.
    include_kv_value_split: bool
    # Batch 3 — symbol & string n-grams. Each toggle adds a new vocab built
    # from the corpus scan; columns appear in the spec only when the
    # corresponding bool is on. Defaults preserve current behavior (off).
    include_symbol_bigrams: bool
    symbol_bigram_max: int
    symbol_min_freq_bigram: int
    include_symbol_trigrams: bool
    symbol_trigram_max: int
    symbol_min_freq_trigram: int
    # Symmetry fix: existing path-trigrams hard-code `c >= 5` for vocab
    # inclusion. This knob exposes that floor so autocollie can sweep it
    # the same way it sweeps `bigram_min_freq`.
    trigram_min_freq: int
    # Tiered crit quadgrams — extends the tiered_crit_bigrams /
    # tiered_crit_trigrams ladder one more order. C(n, 4) cost is steep,
    # so the per-token cap stays the same (512) but autocollie should
    # only enable this on routes where the trigram knob already won.
    include_tiered_crit_quadgrams: bool
    tiered_quadgram_path_depth: int
    tiered_quadgram_min_crit: int
    tiered_quadgram_max: int
    tiered_quadgram_min_freq: int
    # Batch 4 — trait & taxonomy extensions.
    include_mbc_id_vocab: bool                      # bag of unique MBC IDs (m-field) as binary features
    include_trait_confidence_moments: bool          # mean/std/skew/kurtosis of finding confidences
    include_trait_id_lexical_distance: bool         # avg Levenshtein distance between sorted trait IDs
    include_document_obfuscation_features: bool     # aggregate counts of doc-obfuscation/eval/lure paths
    # CSV of `<top_level_branch>=<min_crit>` overrides for the tiered_bigram
    # min_crit gate (e.g. `capability=4,metadata=2`). Branches not listed
    # fall back to tiered_bigram_min_crit. Empty = current behavior (uniform).
    tiered_bigram_branch_min_crit: tuple[str, ...]


@lru_cache(maxsize=1)
def feature_config_from_env() -> FeatureConfig:
    """Load experiment feature toggles from environment variables."""
    raw_groups = os.getenv("COLLIMATOR_DISABLE_FEATURE_GROUPS", "").strip()
    disabled = {part.strip() for part in raw_groups.split(",") if part.strip()}
    unknown = disabled - set(FEATURE_GROUPS)
    if unknown:
        log.warning("ignoring unknown feature groups in COLLIMATOR_DISABLE_FEATURE_GROUPS: %s", sorted(unknown))
    enabled_groups = frozenset(group for group in FEATURE_GROUPS if group not in disabled)

    try:
        top_k_risk_files = max(int(os.getenv("COLLIMATOR_TOP_K_RISK_FILES", str(TOP_K_RISK_FILES))), 0)
    except ValueError:
        log.warning("invalid COLLIMATOR_TOP_K_RISK_FILES=%r, falling back to %d", os.getenv("COLLIMATOR_TOP_K_RISK_FILES"), TOP_K_RISK_FILES)
        top_k_risk_files = TOP_K_RISK_FILES

    include_struct_file_risk_coverage = os.getenv("COLLIMATOR_STRUCT_FILE_RISK_COVERAGE", "1").strip().lower() in {
        "1", "true", "yes", "on",
    }
    include_suspicious_breadth_density = os.getenv("COLLIMATOR_SUSPICIOUS_BREADTH_DENSITY", "1").strip().lower() in {
        "1", "true", "yes", "on",
    }
    include_hostile_escalation_features = os.getenv("COLLIMATOR_HOSTILE_ESCALATION_FEATURES", "1").strip().lower() in {
        "1", "true", "yes", "on",
    }
    include_hostile_weighted_density = os.getenv("COLLIMATOR_HOSTILE_WEIGHTED_DENSITY", "1").strip().lower() in {
        "1", "true", "yes", "on",
    }
    include_repetition_penalty_features = os.getenv("COLLIMATOR_REPETITION_PENALTY_FEATURES", "1").strip().lower() in {
        "1", "true", "yes", "on",
    }
    include_file_severity_distribution = os.getenv("COLLIMATOR_FILE_SEVERITY_DISTRIBUTION", "1").strip().lower() in {
        "1", "true", "yes", "on",
    }
    include_score_weighted_traits = os.getenv("COLLIMATOR_SCORE_WEIGHTED_TRAITS", "1").strip().lower() in {
        "1", "true", "yes", "on",
    }
    include_soft_presence = os.getenv("COLLIMATOR_SOFT_PRESENCE", "1").strip().lower() in {
        "1", "true", "yes", "on",
    }
    include_blindfold = os.getenv("COLLIMATOR_BLINDFOLD", "1").strip().lower() in {
        "1", "true", "yes", "on",
    }
    # v16 default: OFF. Drops 163k mostly-useless inter:{ft}*{element/skeleton} features.
    include_filetype_interactions = os.getenv("COLLIMATOR_FILETYPE_INTERACTIONS", "0").strip().lower() in {
        "1", "true", "yes", "on",
    }

    try:
        ngram_path_depth = int(os.getenv("COLLIMATOR_NGRAM_PATH_DEPTH", "0"))
    except ValueError:
        ngram_path_depth = 0
    try:
        ngram_min_crit = int(os.getenv("COLLIMATOR_NGRAM_MIN_CRIT", "0"))
    except ValueError:
        ngram_min_crit = 0

    include_extreme_features = os.getenv("COLLIMATOR_EXTREME_FEATURES") == "1"
    # Per-feature defaults inherit from the master EXTREME_FEATURES toggle.
    # Treat empty string as "not set" so Make can pass `VAR=` for inherit.
    def _extreme_flag(name: str) -> bool:
        raw = (os.getenv(name) or "").strip().lower()
        if not raw:
            return include_extreme_features
        return raw in {"1", "true", "yes", "on"}

    return FeatureConfig(
        enabled_groups=enabled_groups,
        top_k_risk_files=top_k_risk_files,
        include_struct_file_risk_coverage=include_struct_file_risk_coverage,
        include_suspicious_breadth_density=include_suspicious_breadth_density,
        include_hostile_escalation_features=include_hostile_escalation_features,
        include_hostile_weighted_density=include_hostile_weighted_density,
        include_repetition_penalty_features=include_repetition_penalty_features,
        include_file_severity_distribution=include_file_severity_distribution,
        include_score_weighted_traits=include_score_weighted_traits,
        include_soft_presence=include_soft_presence,
        include_blindfold=include_blindfold,
        include_filetype_interactions=include_filetype_interactions,
        include_format_hints=os.getenv("COLLIMATOR_FORMAT_HINTS") in {
            "1", "true", "yes", "on",
        },
        include_silent_packer_signal=os.getenv("COLLIMATOR_SILENT_PACKER_SIGNAL") == "1",
        include_mtime_kurtosis=os.getenv("COLLIMATOR_MTIME_KURTOSIS") == "1",
        include_air_gap_signal=os.getenv("COLLIMATOR_AIR_GAP_SIGNAL") == "1",
        include_extreme_features=include_extreme_features,
        include_anachronistic_injection=_extreme_flag("COLLIMATOR_ANACHRONISTIC_INJECTION"),
        include_code_entropy_spike=_extreme_flag("COLLIMATOR_CODE_ENTROPY_SPIKE"),
        include_foreign_binary_signal=_extreme_flag("COLLIMATOR_FOREIGN_BINARY_SIGNAL"),
        include_extension_mismatch_signal=_extreme_flag("COLLIMATOR_EXTENSION_MISMATCH_SIGNAL"),
        include_hostile_finding_density=_extreme_flag("COLLIMATOR_HOSTILE_FINDING_DENSITY"),
        include_hostile_depth_weight=_extreme_flag("COLLIMATOR_HOSTILE_DEPTH_WEIGHT"),
        ngram_path_depth=ngram_path_depth,
        ngram_min_crit=ngram_min_crit,
        include_taxonomy_features=os.getenv("COLLIMATOR_TAXONOMY_FEATURES") in {
            "1", "true", "yes", "on",
        },
        include_extended_metrics=os.getenv("COLLIMATOR_EXTENDED_METRICS") in {
            "1", "true", "yes", "on",
        },
        include_ember_lite_features=os.getenv("COLLIMATOR_EMBER_LITE_FEATURES") in {
            "1", "true", "yes", "on",
        },
        include_attack_features=os.getenv("COLLIMATOR_ATTACK_FEATURES") in {
            "1", "true", "yes", "on",
        },
        include_confidence_weighted_ngrams=os.getenv("COLLIMATOR_CONFIDENCE_WEIGHTED_NGRAMS") in {
            "1", "true", "yes", "on",
        },
        include_objective_trigrams=os.getenv("COLLIMATOR_OBJECTIVE_TRIGRAMS") in {
            "1", "true", "yes", "on",
        },
        include_suspicious_trigrams=os.getenv("COLLIMATOR_SUSPICIOUS_TRIGRAMS") in {
            "1", "true", "yes", "on",
        },
        include_attack_ngrams=os.getenv("COLLIMATOR_ATTACK_NGRAMS") in {
            "1", "true", "yes", "on",
        },
        include_crit_category_ngrams=os.getenv("COLLIMATOR_CRIT_CATEGORY_NGRAMS") in {
            "1", "true", "yes", "on",
        },
        include_attack_code_ngrams=os.getenv("COLLIMATOR_ATTACK_CODE_NGRAMS") in {
            "1", "true", "yes", "on",
        },
        include_tiered_crit_bigrams=os.getenv("COLLIMATOR_TIERED_CRIT_BIGRAMS") in {
            "1", "true", "yes", "on",
        },
        tiered_bigram_path_depth=int(os.getenv("COLLIMATOR_TIERED_BIGRAM_PATH_DEPTH", "3")),
        tiered_bigram_min_crit=int(os.getenv("COLLIMATOR_TIERED_BIGRAM_MIN_CRIT", "3")),
        tiered_bigram_max=int(os.getenv("COLLIMATOR_TIERED_BIGRAM_MAX", "5000")),
        tiered_bigram_min_freq=int(os.getenv("COLLIMATOR_TIERED_BIGRAM_MIN_FREQ", "5")),
        include_tiered_crit_trigrams=os.getenv("COLLIMATOR_TIERED_CRIT_TRIGRAMS") in {
            "1", "true", "yes", "on",
        },
        tiered_trigram_path_depth=int(os.getenv("COLLIMATOR_TIERED_TRIGRAM_PATH_DEPTH", "3")),
        tiered_trigram_min_crit=int(os.getenv("COLLIMATOR_TIERED_TRIGRAM_MIN_CRIT", "3")),
        tiered_trigram_max=int(os.getenv("COLLIMATOR_TIERED_TRIGRAM_MAX", "5000")),
        tiered_trigram_min_freq=int(os.getenv("COLLIMATOR_TIERED_TRIGRAM_MIN_FREQ", "5")),
        include_symbol_vocab=os.getenv("COLLIMATOR_SYMBOL_VOCAB") in {
            "1", "true", "yes", "on",
        },
        symbol_vocab_max=int(os.getenv("COLLIMATOR_SYMBOL_VOCAB_MAX", "5000")),
        symbol_min_freq=int(os.getenv("COLLIMATOR_SYMBOL_MIN_FREQ", "5")),
        include_kv_vocab=os.getenv("COLLIMATOR_KV_VOCAB") in {
            "1", "true", "yes", "on",
        },
        kv_vocab_max=int(os.getenv("COLLIMATOR_KV_VOCAB_MAX", "5000")),
        kv_min_freq=int(os.getenv("COLLIMATOR_KV_MIN_FREQ", "5")),
        include_kv_shape_features=os.getenv("COLLIMATOR_KV_SHAPE_FEATURES") in {
            "1", "true", "yes", "on",
        },
        include_text_encoding_features=os.getenv("COLLIMATOR_TEXT_ENCODING_FEATURES") in {
            "1", "true", "yes", "on",
        },
        bigram_max=int(os.getenv("COLLIMATOR_BIGRAM_MAX", "5000")),
        bigram_min_freq=int(os.getenv("COLLIMATOR_BIGRAM_MIN_FREQ", "1000")),
        trigram_max=int(os.getenv("COLLIMATOR_TRIGRAM_MAX", "500")),
        trigram_max_benign_frac=float(os.getenv("COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC", "0.01")),
        exp_import_categories=os.getenv("COLLIMATOR_EXP_1") == "1",
        exp_suspicious_api_combo=os.getenv("COLLIMATOR_EXP_2") == "1",
        exp_confidence_skew=os.getenv("COLLIMATOR_EXP_3") == "1",
        exp_finding_depth_var=os.getenv("COLLIMATOR_EXP_4") == "1",
        exp_multifile_crit_spread=os.getenv("COLLIMATOR_EXP_5") == "1",
        exp_metric_anomaly=os.getenv("COLLIMATOR_EXP_6") == "1",
        exp_unsigned_import_density=os.getenv("COLLIMATOR_EXP_7") == "1",
        exp_entropy_hostile=os.getenv("COLLIMATOR_EXP_8") == "1",
        exp_hostile_objective_div=os.getenv("COLLIMATOR_EXP_9") == "1",
        exp_import_finding_ratio=os.getenv("COLLIMATOR_EXP_10") == "1",
        # Batch 1 — cheap metric extracts.
        include_pe_format_flags=os.getenv("COLLIMATOR_PE_FORMAT_FLAGS") in {
            "1", "true", "yes", "on",
        },
        include_pe_temporal_anomaly=os.getenv("COLLIMATOR_PE_TEMPORAL_ANOMALY") in {
            "1", "true", "yes", "on",
        },
        include_text_metrics_full=os.getenv("COLLIMATOR_TEXT_METRICS_FULL") in {
            "1", "true", "yes", "on",
        },
        include_overlay_signal=os.getenv("COLLIMATOR_OVERLAY_SIGNAL") in {
            "1", "true", "yes", "on",
        },
        include_metric_ratio_features=os.getenv("COLLIMATOR_METRIC_RATIO_FEATURES") in {
            "1", "true", "yes", "on",
        },
        include_size_normalized_metrics=os.getenv("COLLIMATOR_SIZE_NORMALIZED_METRICS") in {
            "1", "true", "yes", "on",
        },
        include_nonstandard_section_signal=os.getenv("COLLIMATOR_NONSTANDARD_SECTION_SIGNAL") in {
            "1", "true", "yes", "on",
        },
        include_line_length_buckets=os.getenv("COLLIMATOR_LINE_LENGTH_BUCKETS") in {
            "1", "true", "yes", "on",
        },
        # Batch 2 — allowlist + filter knobs.
        extended_metrics_include=tuple(
            p.strip() for p in os.getenv("COLLIMATOR_EXTENDED_METRICS_INCLUDE", "").split(",")
            if p.strip()
        ),
        top_k_risk_files_min_crit=max(int(os.getenv("COLLIMATOR_TOP_K_RISK_FILES_MIN_CRIT", "0") or "0"), 0),
        metric_correlation_pairs=tuple(
            p.strip() for p in os.getenv("COLLIMATOR_METRIC_CORRELATION_PAIRS", "").split(",")
            if p.strip()
        ),
        include_kv_value_split=os.getenv("COLLIMATOR_KV_VALUE_SPLIT") in {
            "1", "true", "yes", "on",
        },
        # Batch 3 — symbol & string n-grams.
        include_symbol_bigrams=os.getenv("COLLIMATOR_SYMBOL_BIGRAMS") in {
            "1", "true", "yes", "on",
        },
        symbol_bigram_max=int(os.getenv("COLLIMATOR_SYMBOL_BIGRAM_MAX", "5000")),
        symbol_min_freq_bigram=int(os.getenv("COLLIMATOR_SYMBOL_MIN_FREQ_BIGRAM", "10")),
        include_symbol_trigrams=os.getenv("COLLIMATOR_SYMBOL_TRIGRAMS") in {
            "1", "true", "yes", "on",
        },
        symbol_trigram_max=int(os.getenv("COLLIMATOR_SYMBOL_TRIGRAM_MAX", "2000")),
        symbol_min_freq_trigram=int(os.getenv("COLLIMATOR_SYMBOL_MIN_FREQ_TRIGRAM", "10")),
        trigram_min_freq=int(os.getenv("COLLIMATOR_TRIGRAM_MIN_FREQ", "5")),
        include_tiered_crit_quadgrams=os.getenv("COLLIMATOR_TIERED_CRIT_QUADGRAMS") in {
            "1", "true", "yes", "on",
        },
        tiered_quadgram_path_depth=int(os.getenv("COLLIMATOR_TIERED_QUADGRAM_PATH_DEPTH", "3")),
        tiered_quadgram_min_crit=int(os.getenv("COLLIMATOR_TIERED_QUADGRAM_MIN_CRIT", "3")),
        tiered_quadgram_max=int(os.getenv("COLLIMATOR_TIERED_QUADGRAM_MAX", "5000")),
        tiered_quadgram_min_freq=int(os.getenv("COLLIMATOR_TIERED_QUADGRAM_MIN_FREQ", "5")),
        # Batch 4 — trait & taxonomy extensions.
        include_mbc_id_vocab=os.getenv("COLLIMATOR_MBC_ID_VOCAB") in {
            "1", "true", "yes", "on",
        },
        include_trait_confidence_moments=os.getenv("COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS") in {
            "1", "true", "yes", "on",
        },
        include_trait_id_lexical_distance=os.getenv("COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE") in {
            "1", "true", "yes", "on",
        },
        include_document_obfuscation_features=os.getenv("COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES") in {
            "1", "true", "yes", "on",
        },
        tiered_bigram_branch_min_crit=tuple(
            p.strip() for p in os.getenv("COLLIMATOR_TIERED_BIGRAM_BRANCH_MIN_CRIT", "").split(",")
            if p.strip()
        ),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def report_files(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all valid file entries from a v4 report."""
    files = report.get("fs") or []
    return [f for f in files if isinstance(f, dict)]


def primary_file(report: dict[str, Any]) -> dict[str, Any]:
    """Return the primary (first) file entry from a v3 report."""
    files = report_files(report)
    return files[0] if files else {}


def file_facts(file_entry: dict[str, Any]) -> dict[str, Any]:
    """Return a cleave v5 ff block, or an empty mapping for v4 rows."""
    facts = file_entry.get("ff")
    return facts if isinstance(facts, dict) else {}


def file_metrics(file_entry: dict[str, Any]) -> dict[str, Any]:
    """Return per-file metrics from v5 ff.m or v4 ms."""
    facts = file_facts(file_entry)
    metrics = facts.get("m") if facts else None
    if not isinstance(metrics, dict):
        metrics = file_entry.get("ms")
    return metrics if isinstance(metrics, dict) else {}


def file_values(file_entry: dict[str, Any]) -> dict[str, Any]:
    """Return flat structural values from v5 ff.v or v4 k."""
    facts = file_facts(file_entry)
    values = facts.get("v") if facts else None
    if not isinstance(values, dict):
        values = file_entry.get("k")
    return values if isinstance(values, dict) else {}


def _tuple_string(raw: Any, index: int) -> str:
    if isinstance(raw, (list, tuple)) and len(raw) > index:
        return str(raw[index] or "")
    return ""


def file_imports(file_entry: dict[str, Any]) -> list[Any]:
    """Return import entries from v5 ff.i or v4 is."""
    facts = file_facts(file_entry)
    raw = facts.get("i") if facts else None
    if raw is None:
        raw = file_entry.get("is")
    return raw if isinstance(raw, list) else []


def file_strings(file_entry: dict[str, Any]) -> list[Any]:
    """Return string tuples from v5 ff.s or v4 ss."""
    facts = file_facts(file_entry)
    raw = facts.get("s") if facts else None
    if raw is None:
        raw = file_entry.get("ss")
    return raw if isinstance(raw, list) else []


def _float(value: Any, default: float = 0.0) -> float:
    """Best-effort float conversion for report fields."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_vocab_token(value: Any, *, max_len: int = 96) -> str:
    """Normalize report strings for bounded experimental vocabularies."""
    token = str(value or "").strip()
    if not token:
        return ""
    token = " ".join(token.split())
    if len(token) > max_len:
        token = token[:max_len]
    return token


def _file_symbols(file_entry: dict[str, Any]) -> set[str]:
    """Return normalized import/symbol tokens from a cleave file entry.

    Sources unified under one `symbol_vocab`:
      - imports (`ff.i` / v4 `is`) — lib!name and bare name
      - exports (`ff.x`)
      - functions (`ff.fn`)
      - call targets (`ff.ct`) — filefacts `Symbol::Call` dotted paths
      - member chains (`ff.mc`) — filefacts `Symbol::Member` paths

    `ff.ct`/`ff.mc` only appear in cleave's newer (filefacts-backed)
    schema; on older reports `facts.get("ct")` returns None and the
    loop is a no-op. So the read is naturally graceful — no gate.
    """
    symbols: set[str] = set()
    for raw in file_imports(file_entry):
        if isinstance(raw, (list, tuple)):
            lib = _tuple_string(raw, 0)
            name = _tuple_string(raw, 1)
            name_sym = _normalize_vocab_token(name)
            if len(name_sym) >= 2:
                symbols.add(name_sym)
            raw = f"{lib}!{name}" if lib and name else name or lib
        if isinstance(raw, dict):
            raw = raw.get("n") or raw.get("name") or raw.get("symbol")
        sym = _normalize_vocab_token(raw)
        if len(sym) >= 2:
            symbols.add(sym)
    facts = file_facts(file_entry)
    for raw in facts.get("x") or []:
        name = _tuple_string(raw, 0) if isinstance(raw, (list, tuple)) else raw
        sym = _normalize_vocab_token(name)
        if len(sym) >= 2:
            symbols.add(sym)
    for raw in facts.get("fn") or []:
        name = _tuple_string(raw, 0) if isinstance(raw, (list, tuple)) else raw
        sym = _normalize_vocab_token(name)
        if len(sym) >= 2:
            symbols.add(sym)
    for raw in facts.get("ct") or []:
        sym = _normalize_vocab_token(raw)
        if len(sym) >= 2:
            symbols.add(sym)
    for raw in facts.get("mc") or []:
        sym = _normalize_vocab_token(raw)
        if len(sym) >= 2:
            symbols.add(sym)
    return symbols


# Per-file caps for symbol n-gram generation. Real binaries can have 300+
# imports; C(300, 2) = 44k pairs and C(300, 3) = 4.4M triples per file
# would blow corpus-scan memory + time. Sorting alphabetically and taking
# the first N gives deterministic vocab across rebuilds; the corpus-scan
# min_freq filter then drops pairs that don't survive across files.
_SYMBOL_BIGRAM_CAP = 64
_SYMBOL_TRIGRAM_CAP = 24


def _file_symbol_bigrams(file_entry: dict[str, Any]) -> list[str]:
    """Sorted unordered symbol-pair tokens. Capped per file."""
    syms = sorted(_file_symbols(file_entry))[:_SYMBOL_BIGRAM_CAP]
    out: list[str] = []
    for i, a in enumerate(syms):
        for b in syms[i + 1:]:
            out.append(f"{a}||{b}")
    return out


def _file_symbol_trigrams(file_entry: dict[str, Any]) -> list[str]:
    """Sorted unordered symbol-triple tokens. Capped tighter than bigrams
    because C(n, 3) grows much faster."""
    syms = sorted(_file_symbols(file_entry))[:_SYMBOL_TRIGRAM_CAP]
    out: list[str] = []
    for i, a in enumerate(syms):
        for j in range(i + 1, len(syms)):
            b = syms[j]
            for c in syms[j + 1:]:
                out.append(f"{a}||{b}||{c}")
    return out


def _bucket_count(value: int) -> str:
    if value <= 0:
        return "0"
    if value == 1:
        return "1"
    if value <= 3:
        return "2_3"
    if value <= 7:
        return "4_7"
    if value <= 15:
        return "8_15"
    if value <= 31:
        return "16_31"
    if value <= 63:
        return "32_63"
    if value <= 127:
        return "64_127"
    return "128_plus"


def _bucket_number(value: float) -> str:
    if not math.isfinite(value):
        return "nonfinite"
    if value == 0:
        return "zero"
    sign = "neg" if value < 0 else "pos"
    mag = abs(value)
    if mag < 1:
        bucket = "lt1"
    elif mag < 10:
        bucket = "1_9"
    elif mag < 100:
        bucket = "10_99"
    elif mag < 1000:
        bucket = "100_999"
    elif mag < 10000:
        bucket = "1k_9k"
    elif mag < 1000000:
        bucket = "10k_999k"
    else:
        bucket = "1m_plus"
    return f"{sign}_{bucket}"


_KV_VALUE_SPLIT_SEPARATORS = re.compile(r"[\s,;:/\\|]+")


def _metric_kv_tokens(
    file_entry: dict[str, Any],
    *,
    include_shape: bool = False,
    split_string_values: bool = False,
) -> set[str]:
    """Return ms.* key/value and shape tokens for experimental KV vocab.

    `split_string_values` additionally emits per-component tokens for
    string-valued metrics by splitting on common separators — recovers
    the per-element signal in things like `needed_libs="[libcap.so.2,
    libc.so.6]"` that would otherwise be one opaque blob token.
    """
    tokens: set[str] = set()
    metrics = file_metrics(file_entry)
    for group, fields in metrics.items():
        if not isinstance(fields, dict):
            continue
        for key, value in fields.items():
            base = f"{group}.{key}"
            if include_shape:
                tokens.add(f"{base}:exists")
            if isinstance(value, bool):
                val = str(value).lower()
                if include_shape:
                    tokens.add(f"{base}:bool={val}")
            elif isinstance(value, str):
                val = _normalize_vocab_token(value, max_len=80)
                if include_shape:
                    tokens.add(f"{base}:strlen={_bucket_count(len(value))}")
                    tokens.add(f"{base}:nonempty" if value else f"{base}:empty")
                if split_string_values and value:
                    for component in _KV_VALUE_SPLIT_SEPARATORS.split(value):
                        sub = _normalize_vocab_token(component, max_len=64)
                        if sub:
                            tokens.add(f"{base}=part:{sub}")
            else:
                if include_shape:
                    if value in (None, [], {}, ()):
                        tokens.add(f"{base}:empty")
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        tokens.add(f"{base}:number={_bucket_number(float(value))}")
                    elif isinstance(value, (list, tuple, set)):
                        tokens.add(f"{base}:len={_bucket_count(len(value))}")
                        for item in list(value)[:32]:
                            item_token = _normalize_vocab_token(item, max_len=64)
                            if item_token:
                                tokens.add(f"{base}:item={item_token}")
                    elif isinstance(value, dict):
                        tokens.add(f"{base}:len={_bucket_count(len(value))}")
                        for subkey, subvalue in list(value.items())[:32]:
                            sub = _normalize_vocab_token(subkey, max_len=48)
                            if not sub:
                                continue
                            tokens.add(f"{base}.{sub}:exists")
                            if subvalue in (None, "", [], {}, ()):
                                tokens.add(f"{base}.{sub}:empty")
                            elif isinstance(subvalue, str):
                                tokens.add(f"{base}.{sub}:strlen={_bucket_count(len(subvalue))}")
                            elif isinstance(subvalue, (list, tuple, set, dict)):
                                tokens.add(f"{base}.{sub}:len={_bucket_count(len(subvalue))}")
                continue
            if val:
                tokens.add(f"{base}={val}")
            elif include_shape:
                tokens.add(f"{base}:empty")
    for path, value in file_values(file_entry).items():
        base = f"v.{path}"
        if include_shape:
            tokens.add(f"{base}:exists")
        if isinstance(value, bool):
            tokens.add(f"{base}={str(value).lower()}")
        elif isinstance(value, str):
            val = _normalize_vocab_token(value, max_len=80)
            if val:
                tokens.add(f"{base}={val}")
            if include_shape:
                tokens.add(f"{base}:strlen={_bucket_count(len(value))}")
            if split_string_values and value:
                for component in _KV_VALUE_SPLIT_SEPARATORS.split(value):
                    sub = _normalize_vocab_token(component, max_len=64)
                    if sub:
                        tokens.add(f"{base}=part:{sub}")
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            if include_shape:
                tokens.add(f"{base}:number={_bucket_number(float(value))}")
        elif include_shape:
            if value in (None, [], {}, ()):  # type: ignore[comparison-overlap]
                tokens.add(f"{base}:empty")
            elif isinstance(value, (list, tuple, set, dict)):
                tokens.add(f"{base}:len={_bucket_count(len(value))}")
    return tokens


def _string_values(file_entry: dict[str, Any]) -> list[tuple[str, bool]]:
    """Return extracted string values with a best-effort wide-string flag."""
    out: list[tuple[str, bool]] = []
    for item in file_strings(file_entry):
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue
        is_wide = any(str(part).lower() in {"wide", "u16", "utf16le", "utf-16le"} for part in item[1:-1])
        value = str(item[-1] or "")
        if value:
            out.append((value, is_wide))
    return out


def _char_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts: dict[str, int] = {}
    for ch in value:
        counts[ch] = counts.get(ch, 0) + 1
    n = len(value)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def _looks_base64ish(value: str) -> bool:
    if len(value) < 16:
        return False
    chars = sum(ch.isalnum() or ch in "+/=_-" for ch in value)
    return chars / max(len(value), 1) > 0.92 and any(ch in "+/=" for ch in value)


def _looks_hexish(value: str) -> bool:
    compact = value.strip().replace(" ", "")
    if len(compact) < 16:
        return False
    return sum(ch in "0123456789abcdefABCDEF" for ch in compact) / len(compact) > 0.95


@lru_cache(maxsize=32768)
def _finding_paths(finding_id: str) -> tuple[str, ...]:
    """Extract hierarchical path prefixes (1, 2, 3 levels) from a finding ID.

    "objectives/evasion/process/injection::technique-x"
        -> ("objectives", "objectives/evasion", "objectives/evasion/process")
    "metadata/format::no-functions"
        -> ("metadata", "metadata/format")

    Cached because callers in the hot extraction loop call this 1000+
    times per row with a small universe of distinct finding_ids.
    """
    base = finding_id.split("::")[0] if "::" in finding_id else finding_id
    parts = base.split("/")
    return tuple("/".join(parts[:d]) for d in range(1, min(len(parts), 3) + 1))


# ---------------------------------------------------------------------------
# FeatureSpec
# ---------------------------------------------------------------------------

@dataclass
class FeatureSpec:
    """Describes the feature vector layout. Exported for Rust inference parity.

    Version 15: capability-first features with default hostile-escalation
    aggregates. Each path in presence_vocab gets
    two features: a binary presence flag and an ordinal max-criticality value.
    No path×tier binary features — criticality is a gradient, not a threshold.
    """

    # NOTE: bumping this version requires a matching update in ../litmus (Rust).
    # litmus accepts v16..=v17 to allow live deploys to keep working through
    # a version transition; new bundles always serialize at MODEL_ABI_VERSION.
    version: int = 17
    abi_version: int = MODEL_ABI_VERSION
    presence_vocab: list[str] = field(default_factory=list)
    filetype_vocab: list[str] = field(default_factory=list)
    element_vocab: list[str] = field(default_factory=list)
    bigram_vocab: list[str] = field(default_factory=list)
    ghost_vocab: list[str] = field(default_factory=list)
    skeleton_vocab: list[str] = field(default_factory=list)
    rare_element_vocab: list[str] = field(default_factory=list)
    trigram_vocab: list[str] = field(default_factory=list)
    metric_vocab: list[str] = field(default_factory=list)
    crit_unigram_vocab: list[str] = field(default_factory=list)
    crit_bigram_vocab: list[str] = field(default_factory=list)
    crit_trigram_vocab: list[str] = field(default_factory=list)
    attack_bigram_vocab: list[str] = field(default_factory=list)
    attack_trigram_vocab: list[str] = field(default_factory=list)
    mbc_bigram_vocab: list[str] = field(default_factory=list)
    mbc_trigram_vocab: list[str] = field(default_factory=list)
    tiered_bigram_vocab: list[str] = field(default_factory=list)
    tiered_trigram_vocab: list[str] = field(default_factory=list)
    tiered_quadgram_vocab: list[str] = field(default_factory=list)
    symbol_vocab: list[str] = field(default_factory=list)
    symbol_bigram_vocab: list[str] = field(default_factory=list)
    symbol_trigram_vocab: list[str] = field(default_factory=list)
    kv_vocab: list[str] = field(default_factory=list)
    mbc_id_vocab: list[str] = field(default_factory=list)
    feature_names: list[str] = field(default_factory=list)
    total_features: int = 0
    feature_means: list[float] | None = None
    feature_stds: list[float] | None = None
    # Whether the model was trained on standardized features. When False,
    # inference should use raw features directly (no z-score transform).
    standardized: bool = False

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        d: dict[str, Any] = {
            "version": self.version,
            "abi_version": self.abi_version,
            "presence_vocab": self.presence_vocab,
            "filetype_vocab": self.filetype_vocab,
            "element_vocab": self.element_vocab,
            "bigram_vocab": self.bigram_vocab,
            "ghost_vocab": self.ghost_vocab,
            "skeleton_vocab": self.skeleton_vocab,
            "rare_element_vocab": self.rare_element_vocab,
            "trigram_vocab": self.trigram_vocab,
            "metric_vocab": self.metric_vocab,
            "crit_unigram_vocab": self.crit_unigram_vocab,
            "crit_bigram_vocab": self.crit_bigram_vocab,
            "crit_trigram_vocab": self.crit_trigram_vocab,
            "attack_bigram_vocab": self.attack_bigram_vocab,
            "attack_trigram_vocab": self.attack_trigram_vocab,
            "mbc_bigram_vocab": self.mbc_bigram_vocab,
            "mbc_trigram_vocab": self.mbc_trigram_vocab,
            "tiered_bigram_vocab": self.tiered_bigram_vocab,
            "tiered_trigram_vocab": self.tiered_trigram_vocab,
            "tiered_quadgram_vocab": self.tiered_quadgram_vocab,
            "symbol_vocab": self.symbol_vocab,
            "symbol_bigram_vocab": self.symbol_bigram_vocab,
            "symbol_trigram_vocab": self.symbol_trigram_vocab,
            "kv_vocab": self.kv_vocab,
            "mbc_id_vocab": self.mbc_id_vocab,
            "feature_names": self.feature_names,
            "total_features": self.total_features,
        }
        d["standardized"] = self.standardized
        if self.feature_means is not None:
            d["feature_means"] = [0.0 if (math.isinf(v) or math.isnan(v)) else v for v in self.feature_means]
        if self.feature_stds is not None:
            # Replace inf/nan stds with 1.0 (identity transform — feature passes through raw).
            d["feature_stds"] = [1.0 if (math.isinf(v) or math.isnan(v)) else v for v in self.feature_stds]
        with open(path, "w") as f:
            json.dump(d, f, indent=2)
        log.info("saved feature spec: %d features to %s", self.total_features, path)

    @classmethod
    def load(cls, path: Path) -> FeatureSpec:
        with open(path) as f:
            data = json.load(f)
        version = data.get("version", 11)
        if version < 13:
            log.warning(
                "loading feature spec version %d (expected 15); "
                "models trained with older versions are not compatible",
                version,
            )
        return cls(
            version=version,
            abi_version=data.get("abi_version", version),
            presence_vocab=data.get("presence_vocab", []),
            filetype_vocab=data.get("filetype_vocab", []),
            element_vocab=data.get("element_vocab", []),
            bigram_vocab=data.get("bigram_vocab", []),
            ghost_vocab=data.get("ghost_vocab", []),
            skeleton_vocab=data.get("skeleton_vocab", []),
            rare_element_vocab=data.get("rare_element_vocab", []),
            trigram_vocab=data.get("trigram_vocab", []),
            metric_vocab=data.get("metric_vocab", []),
            crit_unigram_vocab=data.get("crit_unigram_vocab", []),
            crit_bigram_vocab=data.get("crit_bigram_vocab", []),
            crit_trigram_vocab=data.get("crit_trigram_vocab", []),
            attack_bigram_vocab=data.get("attack_bigram_vocab", []),
            attack_trigram_vocab=data.get("attack_trigram_vocab", []),
            mbc_bigram_vocab=data.get("mbc_bigram_vocab", []),
            mbc_trigram_vocab=data.get("mbc_trigram_vocab", []),
            tiered_bigram_vocab=data.get("tiered_bigram_vocab", []),
            tiered_trigram_vocab=data.get("tiered_trigram_vocab", []),
            tiered_quadgram_vocab=data.get("tiered_quadgram_vocab", []),
            symbol_vocab=data.get("symbol_vocab", []),
            symbol_bigram_vocab=data.get("symbol_bigram_vocab", []),
            symbol_trigram_vocab=data.get("symbol_trigram_vocab", []),
            kv_vocab=data.get("kv_vocab", []),
            mbc_id_vocab=data.get("mbc_id_vocab", []),
            feature_names=data["feature_names"],
            total_features=data["total_features"],
            feature_means=data.get("feature_means"),
            feature_stds=data.get("feature_stds"),
            standardized=data.get("standardized", True),
        )


# ---------------------------------------------------------------------------
# Vocabulary building
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def allowed_features() -> frozenset[str] | None:
    """Load allowed feature names from a file if COLLIMATOR_ALLOWED_FEATURES_FILE is set."""
    path = os.getenv("COLLIMATOR_ALLOWED_FEATURES_FILE")
    if not path:
        return None
    try:
        import json
        with open(path) as f:
            data = json.load(f)
            if isinstance(data, list):
                return frozenset(data)
            return frozenset(data.get("significant_features", []))
    except Exception as exc:
        log.warning("failed to load allowed features from %s: %s", path, exc)
        return None


def _build_feature_names(
    presence_vocab: list[str],
    filetype_vocab: list[str],
    element_vocab: list[str],
    bigram_vocab: list[str],
    ghost_vocab: list[str],
    skeleton_vocab: list[str],
    rare_element_vocab: list[str],
    trigram_vocab: list[str],
    metric_vocab: list[str] | None = None,
    crit_unigram_vocab: list[str] | None = None,
    crit_bigram_vocab: list[str] | None = None,
    crit_trigram_vocab: list[str] | None = None,
    attack_bigram_vocab: list[str] | None = None,
    attack_trigram_vocab: list[str] | None = None,
    mbc_bigram_vocab: list[str] | None = None,
    mbc_trigram_vocab: list[str] | None = None,
    tiered_bigram_vocab: list[str] | None = None,
    tiered_trigram_vocab: list[str] | None = None,
    tiered_quadgram_vocab: list[str] | None = None,
    symbol_vocab: list[str] | None = None,
    symbol_bigram_vocab: list[str] | None = None,
    symbol_trigram_vocab: list[str] | None = None,
    kv_vocab: list[str] | None = None,
    mbc_id_vocab: list[str] | None = None,
) -> list[str]:
    """Generate the full ordered list of feature names for a given vocabulary."""
    config = feature_config_from_env()
    feature_names: list[str] = []

    # Group 1: Path Presence — binary (capability exists?).
    if "present" in config.enabled_groups:
        for path in presence_vocab:
            feature_names.append(f"present:{path}")

    # Group 2: Path Max Criticality — ordinal 0-5 (cleave's severity gradient).
    if "maxcrit" in config.enabled_groups:
        for path in presence_vocab:
            feature_names.append(f"maxcrit:{path}")

    # Group 3: Path Aggregates (20).
    if "agg" in config.enabled_groups:
        feature_names.extend([
            "agg:max_crit",                  # highest crit seen (0-5)
            "agg:category_breadth",          # distinct top-level categories
            "agg:path_breadth_any",          # log1p of all 3-level paths (any crit)
            "agg:total_active_paths",        # log1p of notable+ 3-level paths
            "agg:suspicious_concentration",  # suspicious / all paths
            "agg:hostile_concentration",     # hostile / all paths
            "agg:escalation_rate",           # suspicious+ / notable+ (cleave escalation)
            "agg:notable_only_fraction",     # notable_only / notable+ (how much stays at notable)
            "agg:notable_findings_log",      # log1p of notable+ exact findings
            "agg:suspicious_findings_log",   # log1p of suspicious+ exact findings
            "agg:hostile_findings_log",      # log1p of hostile exact findings
            "agg:notable_finding_ratio",     # notable+ / all filtered findings
            "agg:suspicious_finding_ratio",  # suspicious+ / all filtered findings
            "agg:hostile_finding_ratio",     # hostile / all filtered findings
            "agg:unique_suspicious_ids_log", # log1p of unique suspicious+ trait IDs
            "agg:unique_hostile_ids_log",    # log1p of unique hostile trait IDs
            f"agg:top{config.top_k_risk_files}_file_suspicious_ratio_sum",
            f"agg:top{config.top_k_risk_files}_file_hostile_ratio_sum",
            f"agg:top{config.top_k_risk_files}_file_suspicious_findings_log",
            f"agg:top{config.top_k_risk_files}_file_hostile_findings_log",
        ])
        if config.include_suspicious_breadth_density:
            feature_names.extend([
                "agg:suspicious_category_breadth",
                "agg:hostile_category_breadth",
                "agg:suspicious_category_density",
                "agg:hostile_category_density",
                "agg:suspicious_findings_per_kb",
                "agg:hostile_findings_per_kb",
                "agg:suspicious_categories_per_kb",
                "agg:hostile_categories_per_kb",
                f"agg:top{config.top_k_risk_files}_file_suspicious_density_sum",
                f"agg:top{config.top_k_risk_files}_file_hostile_density_sum",
                f"agg:top{config.top_k_risk_files}_file_suspicious_category_breadth_sum",
                f"agg:top{config.top_k_risk_files}_file_hostile_category_breadth_sum",
            ])
        if config.include_hostile_escalation_features:
            feature_names.extend([
                "agg:hostile_escalation_rate",
                "agg:hostile_share_of_suspicious",
                "agg:suspicious_finding_escalation_rate",
                "agg:hostile_finding_escalation_rate",
                "agg:hostile_share_of_suspicious_findings",
            ])
        if config.include_hostile_weighted_density:
            feature_names.extend([
                "agg:hostile_weighted_density",
                f"agg:top{config.top_k_risk_files}_file_hostile_weighted_density_sum",
            ])
        if config.include_repetition_penalty_features:
            feature_names.extend([
                "agg:suspicious_id_repeat_ratio",
                "agg:hostile_id_repeat_ratio",
                "agg:suspicious_category_repeat_ratio",
                "agg:hostile_category_repeat_ratio",
            ])
        if config.include_file_severity_distribution:
            feature_names.extend([
                "agg:file_hostile_fraction",
                "agg:file_suspicious_fraction",
                "agg:file_notable_fraction",
                "agg:file_hostile_count_log",
                "agg:file_suspicious_count_log",
                "agg:file_notable_count_log",
            ])
        if config.include_hostile_depth_weight:
            feature_names.append("agg:hostile_depth_weight")
        # 2-level category breadth: distinct 2nd-level paths at each tier.
        # More discriminative than top-1 (e.g., "micro-behaviors/network" ≠
        # "micro-behaviors/anti-analysis"). Also: objectives/* breadth counts
        # distinct objectives sub-paths at any crit (how many distinct attack
        # objectives the sample touches).
        feature_names.extend([
            "agg:suspicious_2level_breadth",
            "agg:hostile_2level_breadth",
            "agg:objectives_breadth",
        ])
        if config.include_taxonomy_features:
            feature_names.extend([
                # Kill chain span: distinct ATT&CK-like phases (objectives/*
                # 2nd-level categories) the sample covers.
                "agg:kill_chain_span",
                # Objective-to-micro-behavior ratio: high = more intent signals
                # relative to implementation noise.
                "agg:objective_micro_ratio",
                # Average taxonomy depth of all findings (deeper = more specific).
                "agg:avg_finding_depth",
                # Cross-domain density: objectives breadth × hostile concentration.
                "agg:objective_hostile_density",
            ])
        # Experimental feature batch (2026-04-13).
        if config.exp_import_categories:
            feature_names.append("agg:import_category_count")
        if config.exp_suspicious_api_combo:
            feature_names.append("agg:suspicious_api_combo")
        if config.exp_confidence_skew or config.include_trait_confidence_moments:
            feature_names.extend(["agg:confidence_mean", "agg:confidence_std"])
        if config.include_trait_confidence_moments:
            # Promote from EXP_3 with 2 additional moments (skew + kurtosis).
            feature_names.extend(["agg:confidence_skew", "agg:confidence_kurtosis"])
        if config.include_trait_id_lexical_distance:
            feature_names.append("agg:trait_id_lexical_distance")
        if config.include_document_obfuscation_features:
            # Aggregate counts of doc-obfuscation / interpreter-eval / lure
            # paths from cleave's document-malware taxonomy. These show up
            # frequently on PDF/RTF/DOCX malware and rarely on benign docs.
            feature_names.extend([
                "agg:docobf_obfuscation_count",
                "agg:docobf_eval_count",
                "agg:docobf_lure_count",
                "agg:docobf_total_count",
                "agg:docobf_has_any",
            ])
        if config.exp_finding_depth_var:
            feature_names.append("agg:finding_depth_var")
        if config.exp_multifile_crit_spread:
            feature_names.append("agg:multifile_crit_spread")
        if config.exp_metric_anomaly:
            feature_names.append("agg:metric_anomaly")
        if config.exp_unsigned_import_density:
            feature_names.append("agg:unsigned_import_density")
        if config.exp_entropy_hostile:
            feature_names.append("agg:entropy_hostile")
        if config.exp_hostile_objective_div:
            feature_names.append("agg:hostile_objective_diversity")
        if config.exp_import_finding_ratio:
            feature_names.append("agg:import_finding_ratio")
        if config.include_attack_features:
            feature_names.extend([
                "agg:attack_technique_count",    # distinct ATT&CK T-codes
                "agg:attack_tactic_count",       # distinct tactic prefixes (T1xxx → tactic)
                "agg:mbc_behavior_count",        # distinct MBC B-codes
                "agg:has_attack_and_objective",   # has T-codes AND objectives/* findings
            ])
        if config.include_ember_lite_features:
            feature_names.extend([
                "agg:static_file_bytes_log",
                "agg:static_import_count_log",
                "agg:static_export_count_log",
                "agg:static_dependency_count_log",
                "agg:static_string_count_log",
                "agg:static_wide_string_ratio",
                "agg:static_max_string_length_log",
                "agg:static_string_entropy_max",
                "agg:static_text_lines_log",
                "agg:static_function_count_log",
                "agg:static_code_bytes_log",
                "agg:static_code_to_data_ratio_max",
                "agg:static_wx_units_log",
                "agg:static_writable_unit_ratio",
                "agg:static_executable_unit_ratio",
                "agg:static_nonstandard_unit_names_log",
                "agg:static_largest_unit_ratio_max",
                "agg:static_resource_ratio_max",
                "agg:static_signed_file_fraction",
            ])
        if config.include_objective_trigrams:
            feature_names.extend([
                "agg:objective_trigram_count",    # distinct 3-way objective path combos
                "agg:objective_bigram_count",     # distinct 2-way objective path combos
            ])
        if config.include_suspicious_trigrams:
            feature_names.extend([
                "agg:suspicious_trigram_count",   # distinct 3-way combos from crit>=4 findings
                "agg:suspicious_bigram_count",    # distinct 2-way combos from crit>=4 findings
            ])
        if config.include_attack_ngrams:
            feature_names.extend([
                "agg:attack_bigram_count",        # distinct ATT&CK T-code pairs
                "agg:attack_trigram_count",        # distinct ATT&CK T-code triples
                "agg:mbc_bigram_count",           # distinct MBC code pairs
            ])
        if config.include_crit_category_ngrams:
            for cu in (crit_unigram_vocab or []):
                feature_names.append(f"crit:{cu}")
            for cb in (crit_bigram_vocab or []):
                feature_names.append(f"critbi:{cb}")
            for ct in (crit_trigram_vocab or []):
                feature_names.append(f"crittri:{ct}")
        if config.include_attack_code_ngrams:
            for ab in (attack_bigram_vocab or []):
                feature_names.append(f"atkbi:{ab}")
            for at in (attack_trigram_vocab or []):
                feature_names.append(f"atktri:{at}")
            for mb in (mbc_bigram_vocab or []):
                feature_names.append(f"mbcbi:{mb}")
            for mt in (mbc_trigram_vocab or []):
                feature_names.append(f"mbctri:{mt}")
        # Batch 4: unigram MBC IDs as binary features (mirrors symbol_vocab
        # shape but pulled from the trait `m` field).
        if config.include_mbc_id_vocab:
            for mid in (mbc_id_vocab or []):
                feature_names.append(f"mbc:{mid}")

    # Group 4: Third-Party / Well-Known Summary (6).
    if "ext" in config.enabled_groups:
        feature_names.extend([
            "ext:third_party_max_crit",
            "ext:third_party_count",
            "ext:well_known_max_crit",
            "ext:well_known_hostile_count",
            "ext:well_known_suspicious_count",
            "ext:has_yara_match",
        ])

    # Group 5: Key Metrics (16 base) + extended metric vocab + Batch-1 toggles.
    if "metrics" in config.enabled_groups:
        for group, fname, _ in KEY_METRICS:
            feature_names.append(f"metrics:{group}_{fname}")
        # Batch 1 columns are appended before extended_metrics so the dedup
        # below can skip any extended-metrics-vocab entries that collide
        # (e.g. the corpus may have surfaced `pe_is_dotnet` already).
        batch1_suffixes = _batch1_column_suffixes(config)
        seen = {f"{g}_{f}" for g, f, _ in KEY_METRICS} | set(batch1_suffixes)
        for suffix in batch1_suffixes:
            feature_names.append(f"metrics:{suffix}")
        for suffix, _a, _b in _metric_correlation_columns(config):
            seen.add(suffix)
            feature_names.append(f"metrics:{suffix}")
        if config.include_extended_metrics:
            for mk in (metric_vocab or ()):
                if mk in seen:
                    continue
                feature_names.append(f"metrics:{mk}")

    # Group 6: File Type multi-hot across all files in the report.
    if "filetype" in config.enabled_groups:
        for ftype in filetype_vocab:
            feature_names.append(f"filetype:{ftype}")

    # Group 6b: Portable format-group hints derived only from cleave file types.
    if "format" in config.enabled_groups and config.include_format_hints:
        for group in _FORMAT_GROUP_ORDER:
            feature_names.extend([
                f"format:{group}",
                f"format:{group}_file_fraction",
                f"format:{group}_inner_fraction",
                f"format:{group}_suspicious_fraction",
                f"format:{group}_hostile_fraction",
            ])
        feature_names.extend([
            "format:group_count_log",
            "format:mixed_script_binary",
            "format:mixed_archive_script",
            "format:mixed_archive_binary",
            "format:unknown_file_fraction",
        ])

    # Group 7: Structural / container context (7).
    if "struct" in config.enabled_groups:
        feature_names.extend([
            "struct:tiny_executable",
            "struct:no_imports",
            "struct:zero_findings",
            "struct:finding_count_log",
            "struct:file_count_log",
            "struct:inner_file_count_log",
            "struct:stealth_potential",
        ])
        if config.include_struct_file_risk_coverage:
            feature_names.extend([
                "struct:suspicious_file_fraction",
                "struct:hostile_file_fraction",
                "struct:suspicious_file_count_log",
                "struct:hostile_file_count_log",
            ])

    # Group 8: Elements multi-hot.
    if "elements" in config.enabled_groups:
        for el in element_vocab:
            feature_names.append(f"elements:{el}")
            # Interaction with filetype (gated; mostly-useless cross-product in v15)
            if config.include_filetype_interactions:
                for ft in filetype_vocab:
                    feature_names.append(f"inter:{ft}*{el}")

    # Group 9: Formula.
    if "formula" in config.enabled_groups:
        feature_names.extend([
            "formula:skeleton_len",
            "formula:unique_elements",
            "formula:complexity_ratio",  # formula_len / finding_count
        ])

    # Group 10: Score.
    if "score" in config.enabled_groups:
        feature_names.extend([
            "score:hopper_score",
            "score:density",  # score / log1p(size)
        ])
        # Interaction with filetype
        for ft in filetype_vocab:
            feature_names.append(f"inter:{ft}*score")

    # Group 11: Bigrams multi-hot.
    if "bigrams" in config.enabled_groups:
        for bigram in bigram_vocab:
            feature_names.append(f"bigrams:{bigram}")

    # Group 11b: Report-level severity-prefixed trait bigrams.
    if "tiered_bigrams" in config.enabled_groups and config.include_tiered_crit_bigrams:
        for bigram in (tiered_bigram_vocab or []):
            feature_names.append(f"tierbi:{bigram}")

    # Group 11c: Report-level severity-prefixed trait trigrams.
    if "tiered_trigrams" in config.enabled_groups and config.include_tiered_crit_trigrams:
        for trigram in (tiered_trigram_vocab or []):
            feature_names.append(f"tiertri:{trigram}")

    # Group 11d (Batch 3): Report-level severity-prefixed trait quadgrams.
    # Reuses the `tiered_trigrams` group toggle so quadgrams ride the same
    # disable_groups switch — they're an extension of the same family.
    if "tiered_trigrams" in config.enabled_groups and config.include_tiered_crit_quadgrams:
        for quadgram in (tiered_quadgram_vocab or []):
            feature_names.append(f"tierquad:{quadgram}")

    # Group 12: Ghosts (absence of expected benign behavior).
    if "ghosts" in config.enabled_groups:
        for ghost in ghost_vocab:
            feature_names.append(f"ghost:{ghost}")

    # Group 13: Skeletons and interactions.
    if "skeletons" in config.enabled_groups:
        for skel in skeleton_vocab:
            feature_names.append(f"skeleton:{skel}")
            # Cross-product with filetype (Exp 22; gated, mostly-useless in v15)
            if config.include_filetype_interactions:
                for ft in filetype_vocab:
                    feature_names.append(f"inter:{ft}*{skel}")

    # Group 14: Rare elements (smoking guns).
    if "rares" in config.enabled_groups:
        for el in rare_element_vocab:
            feature_names.append(f"rare:{el}")

    # Group 15: Structural interactions (Experiment 25).
    if "struct" in config.enabled_groups:
        feature_names.append("struct:packaged_capability")
        # Experiment 30
        feature_names.extend([
            "struct:mtime_range_hours",
            "struct:mtime_std_dev_hours",
            "struct:max_nesting_depth_log",
            "struct:inner_file_ratio",
            "struct:entropy_std_dev",
            "struct:entropy_max_diff",
        ])
        if config.include_silent_packer_signal:
            feature_names.append("struct:silent_packer_signal")
        if config.include_mtime_kurtosis:
            feature_names.append("struct:mtime_kurtosis")
        if config.include_air_gap_signal:
            feature_names.append("struct:air_gap_signal")
        if config.include_anachronistic_injection:
            feature_names.append("struct:anachronistic_injection")
        if config.include_code_entropy_spike:
            feature_names.append("struct:code_entropy_spike")
        if config.include_foreign_binary_signal:
            feature_names.append("struct:foreign_binary_signal")
        if config.include_extension_mismatch_signal:
            feature_names.append("struct:extension_mismatch_signal")
        if config.include_hostile_finding_density:
            feature_names.append("struct:hostile_finding_density")

    # Group 16: Trigrams multi-hot.
    if "trigrams" in config.enabled_groups:
        for trigram in trigram_vocab:
            feature_names.append(f"trigram:{trigram}")

    # Group 19: Logic Gaps (Exp 35).
    if "logic_gaps" in config.enabled_groups:
        for cat in sorted(LOGIC_GAPS.keys()):
            feature_names.append(f"gap:{cat}")

    # Group 20: Signature Synergy (Exp 37).
    if "signature_synergy" in config.enabled_groups:
        for bigram in bigram_vocab:
            feature_names.append(f"unsigned_bigram:{bigram}")

    # Group 21: Semantic Clusters (Exp 38, scaled in Exp 52).
    if "clusters" in config.enabled_groups:
        for i in range(50):  # Increased from 10 to 50 for higher resolution
            feature_names.append(f"cluster:{i}")
        feature_names.append("cluster:dist")

    # Group 22: Package Intent Gaps (Exp 40).
    # Flags risky behavior present without corresponding intent in metadata.
    if "intent_gaps" in config.enabled_groups:
        intent_categories = ["network", "filesystem", "execution", "crypto"]
        for cat in intent_categories:
            feature_names.append(f"intent_gap:{cat}")

    # Group 23: Negative Space (Exp 45).
    if "neg_space" in config.enabled_groups:
        for ftype, traits in sorted(EXPECTED_GHOSTS.items()):
            for trait in traits:
                feature_names.append(f"missing:{ftype}*{trait}")

    # Experimental report metadata vocabularies. These are Python-side probes
    # until litmus gains parity for any winning recipe.
    if "symbols" in config.enabled_groups and config.include_symbol_vocab:
        for sym in symbol_vocab or []:
            feature_names.append(f"symbol:{sym}")

    # Batch 3: symbol n-grams. Same `symbols` group toggle so they ride the
    # disable_groups switch alongside `symbol_vocab`.
    if "symbols" in config.enabled_groups and config.include_symbol_bigrams:
        for bi in symbol_bigram_vocab or []:
            feature_names.append(f"symbol_bi:{bi}")
    if "symbols" in config.enabled_groups and config.include_symbol_trigrams:
        for tri in symbol_trigram_vocab or []:
            feature_names.append(f"symbol_tri:{tri}")

    if "kv" in config.enabled_groups and config.include_kv_vocab:
        for kv in kv_vocab or []:
            feature_names.append(f"kv:{kv}")

    if "textenc" in config.enabled_groups and config.include_text_encoding_features:
        feature_names.extend([
            "textenc:string_count_log",
            "textenc:avg_len_log",
            "textenc:max_len_log",
            "textenc:base64ish_ratio",
            "textenc:hexish_ratio",
            "textenc:urlish_ratio",
            "textenc:pathish_ratio",
            "textenc:unicode_escape_ratio",
            "textenc:wide_ratio",
            "textenc:high_entropy_ratio",
            "textenc:long_token_ratio",
            "textenc:short_junk_ratio",
        ])

    # NEW: Filter based on allowed list if provided.
    allowed = allowed_features()
    if allowed is not None:
        original_count = len(feature_names)
        feature_names = [name for name in feature_names if name in allowed]
        log.info("pruned feature spec: %d -> %d features", original_count, len(feature_names))

    return feature_names


def build_vocab(reports: Iterable[dict[str, Any] | str], n_workers: int = 0) -> FeatureSpec:
    """Scan all reports to build the feature vocabulary."""
    # This standard build_vocab doesn't have labels, so it can't find ghosts.
    # Ghosts require build_vocab_from_db or a labeled stream.
    # For now, we'll return an empty ghost_vocab here.
    nw = resolve_worker_count(n_workers)
    presence_counts: dict[str, int] = {}
    filetypes: set[str] = set()
    element_counts: dict[str, int] = {}
    bigram_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    batch_size = _feature_batch_size(nw)
    n_batches = 0
    _PROGRESS_BATCH_INTERVAL = 500

    def _merge_batch(
        counts: dict[str, int],
        fts: list[str],
        el_counts: dict[str, int],
        bi_counts: dict[str, int],
        b_pres: dict[str, int],
        m_pres: dict[str, int],
        sk_counts: dict[str, int],
    ) -> None:
        nonlocal n_batches
        for k, v in counts.items():
            presence_counts[k] = presence_counts.get(k, 0) + v
        filetypes.update(fts)
        for k, v in el_counts.items():
            element_counts[k] = element_counts.get(k, 0) + v
        for k, v in bi_counts.items():
            bigram_counts[k] = bigram_counts.get(k, 0) + v
        for k, v in sk_counts.items():
            skeleton_counts[k] = skeleton_counts.get(k, 0) + v
        n_batches += 1

    if nw > 1:
        with ProcessPoolExecutor(max_workers=nw, mp_context=mp.get_context("spawn")) as pool:
            for res in _bounded_iter(
                pool, _vocab_batch_worker, _batched(reports, batch_size),
                max_inflight=2 * nw,
            ):
                _merge_batch(*res)
    else:
        for res in map(_vocab_batch_worker, _batched(reports, batch_size)):
            _merge_batch(*res)

    presence_vocab = sorted(k for k, c in presence_counts.items() if c >= MIN_PATH_FREQ)
    filetype_vocab = sorted(filetypes)
    element_vocab = sorted(k for k, c in element_counts.items() if c >= MIN_PATH_FREQ)
    bigram_vocab = sorted(k for k, c in bigram_counts.items() if c >= 1000)[:5000]
    skeleton_vocab = sorted(k for k, c in skeleton_counts.items() if c >= 100)
    ghost_vocab: list[str] = []
    # Legacy build_vocab doesn't track rare_elements or trigrams — those need
    # labeled data and a streaming pass. build_vocab_from_db is the full path.
    rare_element_vocab: list[str] = []
    trigram_vocab: list[str] = []
    feature_names = _build_feature_names(
        presence_vocab,
        filetype_vocab,
        element_vocab,
        bigram_vocab,
        ghost_vocab,
        skeleton_vocab,
        rare_element_vocab,
        trigram_vocab,
    )

    spec = FeatureSpec(
        presence_vocab=presence_vocab,
        filetype_vocab=filetype_vocab,
        element_vocab=element_vocab,
        bigram_vocab=bigram_vocab,
        ghost_vocab=ghost_vocab,
        skeleton_vocab=skeleton_vocab,
        rare_element_vocab=rare_element_vocab,
        trigram_vocab=trigram_vocab,
        feature_names=feature_names,
        total_features=len(feature_names),
    )
    return spec


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

class _ExtractContext:
    """Pre-built lookup tables for fast repeated extraction against a spec."""

    __slots__ = (
        "presence_lookup", "maxcrit_lookup", "ft_lookup", "n_ft",
        "element_lookup", "element_interaction_lookup", "n_el",
        "bigram_lookup", "n_bi", "tiered_bigram_lookup", "n_tier_bi",
        "tiered_trigram_lookup", "n_tier_tri",
        "ghost_vocab", "ghost_lookup", "n_gh",
        "skeleton_lookup", "skeleton_interaction_lookup", "n_sk",
        "rare_element_lookup", "n_re",
        "trigram_lookup", "n_tri", "blindfold", "total_features",
        "score_interaction_lookup", "synergy_lookup",
        "absolute_lookup",
        "bigram_vocab_paths", "trigram_vocab_paths", "synergy_vocab_paths",
        "tiered_bigram_vocab_tokens", "tiered_trigram_vocab_tokens",
        "tiered_quadgram_vocab_tokens",
        "bigram_lookup_pair", "synergy_lookup_pair", "trigram_lookup_triple",
    )

    def __init__(self, spec: FeatureSpec) -> None:
        config = feature_config_from_env()
        self.blindfold = config.include_blindfold
        self.total_features = spec.total_features
        
        # Build lookups that map to the actual indices in feature_names.
        name_to_idx = {name: i for i, name in enumerate(spec.feature_names)}
        self.absolute_lookup = name_to_idx

        self.presence_lookup: dict[str, int] = {}
        self.maxcrit_lookup: dict[str, int] = {}
        for path in spec.presence_vocab:
            if (idx := name_to_idx.get(f"present:{path}")) is not None:
                self.presence_lookup[path] = idx
            if (idx := name_to_idx.get(f"maxcrit:{path}")) is not None:
                self.maxcrit_lookup[path] = idx

        self.ft_lookup: dict[str, int] = {}
        for ft in spec.filetype_vocab:
            if (idx := name_to_idx.get(f"filetype:{ft}")) is not None:
                self.ft_lookup[ft] = idx
        self.n_ft = len(spec.filetype_vocab)

        self.element_lookup: dict[str, int] = {}
        self.element_interaction_lookup: dict[tuple[str, str], int] = {}
        for el in spec.element_vocab:
            if (idx := name_to_idx.get(f"elements:{el}")) is not None:
                self.element_lookup[el] = idx
            for ft in spec.filetype_vocab:
                if (idx := name_to_idx.get(f"inter:{ft}*{el}")) is not None:
                    self.element_interaction_lookup[(ft, el)] = idx
        self.n_el = len(spec.element_vocab)

        self.score_interaction_lookup: dict[str, int] = {}
        for ft in spec.filetype_vocab:
            if (idx := name_to_idx.get(f"inter:{ft}*score")) is not None:
                self.score_interaction_lookup[ft] = idx

        self.bigram_lookup: dict[str, int] = {}
        self.tiered_bigram_lookup: dict[str, int] = {}
        self.synergy_lookup: dict[str, int] = {}
        for bi in spec.bigram_vocab:
            if (idx := name_to_idx.get(f"bigrams:{bi}")) is not None:
                self.bigram_lookup[bi] = idx
            if (idx := name_to_idx.get(f"unsigned_bigram:{bi}")) is not None:
                self.synergy_lookup[bi] = idx
        self.n_bi = len(spec.bigram_vocab)
        for bi in spec.tiered_bigram_vocab:
            if (idx := name_to_idx.get(f"tierbi:{bi}")) is not None:
                self.tiered_bigram_lookup[bi] = idx
        self.n_tier_bi = len(spec.tiered_bigram_vocab)
        self.tiered_trigram_lookup: dict[str, int] = {}
        for tri in spec.tiered_trigram_vocab:
            if (idx := name_to_idx.get(f"tiertri:{tri}")) is not None:
                self.tiered_trigram_lookup[tri] = idx
        self.n_tier_tri = len(spec.tiered_trigram_vocab)
        # Pre-filter sets for tiered n-grams. Same idea as bigram_vocab_paths
        # but the tokens are severity-prefixed (e.g. "L5/objectives/network")
        # rather than raw finding paths.
        self.tiered_bigram_vocab_tokens: frozenset[str] = frozenset(
            t for bi in self.tiered_bigram_lookup for t in bi.split(" + ")
        )
        self.tiered_trigram_vocab_tokens: frozenset[str] = frozenset(
            t for tri in self.tiered_trigram_lookup for t in tri.split(" + ")
        )
        # Tiered quadgrams live in absolute_lookup under "tierquad:" prefix.
        # Extract the tokens that appear in at least one vocab quadgram.
        _quad_tokens: set[str] = set()
        for key in name_to_idx:
            if key.startswith("tierquad:"):
                for t in key[len("tierquad:"):].split(" + "):
                    _quad_tokens.add(t)
        self.tiered_quadgram_vocab_tokens: frozenset[str] = frozenset(_quad_tokens)

        self.ghost_vocab = spec.ghost_vocab
        self.ghost_lookup: dict[str, int] = {}
        for gh in spec.ghost_vocab:
            if (idx := name_to_idx.get(f"ghost:{gh}")) is not None:
                self.ghost_lookup[gh] = idx
        self.n_gh = len(spec.ghost_vocab)

        self.skeleton_lookup: dict[str, int] = {}
        self.skeleton_interaction_lookup: dict[tuple[str, str], int] = {}
        for sk in spec.skeleton_vocab:
            if (idx := name_to_idx.get(f"skeleton:{sk}")) is not None:
                self.skeleton_lookup[sk] = idx
            for ft in spec.filetype_vocab:
                if (idx := name_to_idx.get(f"inter:{ft}*{sk}")) is not None:
                    self.skeleton_interaction_lookup[(ft, sk)] = idx
        self.n_sk = len(spec.skeleton_vocab)

        self.rare_element_lookup: dict[str, int] = {}
        for re in spec.rare_element_vocab:
            if (idx := name_to_idx.get(f"rare:{re}")) is not None:
                self.rare_element_lookup[re] = idx
        self.n_re = len(spec.rare_element_vocab)

        self.trigram_lookup: dict[str, int] = {}
        for tri in spec.trigram_vocab:
            if (idx := name_to_idx.get(f"trigram:{tri}")) is not None:
                self.trigram_lookup[tri] = idx
        self.n_tri = len(spec.trigram_vocab)

        # Pre-filter sets: paths that can possibly participate in a vocab
        # n-gram. _apply_{bigram,trigram,signature_synergy}_features used
        # to enumerate O(N^2)/O(N^3) over all per-file finding paths, then
        # dict-miss the vast majority. The vocab paths are a tiny subset
        # (~50 for trigrams, ~1k for bigrams) of the per-file path
        # universe, so filtering first turns ~390k trigram-string-formats
        # per file into ~10-20.
        self.bigram_vocab_paths: frozenset[str] = frozenset(
            p for bi in self.bigram_lookup for p in bi.split(" + ")
        )
        self.trigram_vocab_paths: frozenset[str] = frozenset(
            p for tri in self.trigram_lookup for p in tri.split(" + ")
        )
        self.synergy_vocab_paths: frozenset[str] = frozenset(
            p for bi in self.synergy_lookup for p in bi.split(" + ")
        )
        # Tuple-keyed mirrors of the string-keyed bigram/trigram/synergy
        # lookups. Building "p1 + p2" / "p1 + p2 + p3" inside the hot
        # extraction loop dominated those functions; a tuple lookup
        # avoids the f-string and string-hashing cost entirely.
        self.bigram_lookup_pair: dict[tuple[str, str], int] = {}
        for bi, idx in self.bigram_lookup.items():
            parts = bi.split(" + ")
            if len(parts) == 2:
                self.bigram_lookup_pair[(parts[0], parts[1])] = idx
        self.synergy_lookup_pair: dict[tuple[str, str], int] = {}
        for bi, idx in self.synergy_lookup.items():
            parts = bi.split(" + ")
            if len(parts) == 2:
                self.synergy_lookup_pair[(parts[0], parts[1])] = idx
        self.trigram_lookup_triple: dict[tuple[str, str, str], int] = {}
        for tri, idx in self.trigram_lookup.items():
            parts = tri.split(" + ")
            if len(parts) == 3:
                self.trigram_lookup_triple[(parts[0], parts[1], parts[2])] = idx


@dataclass(slots=True)
class _FindingSummary:
    sample_paths: dict[str, int]
    filtered_finding_count: int
    notable_finding_count: int
    suspicious_finding_count: int
    hostile_finding_count: int
    unique_notable_ids: int
    unique_suspicious_ids: int
    unique_hostile_ids: int
    suspicious_category_breadth: int
    hostile_category_breadth: int
    third_party_max_crit: int
    third_party_count: int
    well_known_max_crit: int
    well_known_hostile: int
    well_known_suspicious: int
    has_yara: bool
    path_confidences: dict[str, float] = field(default_factory=dict)
    finding_confidences: list[float] = field(default_factory=list)


@dataclass(slots=True)
class _FileRiskStats:
    suspicious_ratio: float
    hostile_ratio: float
    suspicious_findings: int
    hostile_findings: int
    suspicious_density: float
    hostile_density: float
    suspicious_category_breadth: int
    hostile_category_breadth: int
    max_crit: int


def _merge_metric_values(files: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Collapse per-file metrics into report-level maxima.

    Max aggregation preserves single-file detections for embedded files while
    still allowing multi-file reports to contribute their strongest signal.
    """
    merged: dict[str, dict[str, float]] = {}
    for file_entry in files:
        metrics = file_metrics(file_entry)
        for group, fields in metrics.items():
            if not isinstance(fields, dict):
                continue
            group_metrics = merged.setdefault(group, {})
            for fname, raw_value in fields.items():
                val = _float(raw_value)
                if fname not in group_metrics or val > group_metrics[fname]:
                    group_metrics[fname] = val
    return merged


def _summarize_findings(findings: list[dict[str, Any]]) -> _FindingSummary:
    """Collect reusable per-report finding statistics."""
    # Hoist hot lookups into locals: dot-attribute and global-name lookups
    # are slow in a tight loop. include_soft_presence is also read once
    # (it's a config snapshot, not a per-finding switch) so we can branch
    # outside the inner loop.
    include_soft_presence = feature_config_from_env().include_soft_presence
    min_conf = MIN_CONFIDENCE
    finding_paths = _finding_paths
    sample_paths: dict[str, int] = {}
    path_confidences: dict[str, float] = {}
    finding_confidences: list[float] = []
    filtered_finding_count = 0
    notable_finding_count = 0
    suspicious_finding_count = 0
    hostile_finding_count = 0
    notable_ids: set[str] = set()
    suspicious_ids: set[str] = set()
    hostile_ids: set[str] = set()
    suspicious_categories: set[str] = set()
    hostile_categories: set[str] = set()
    third_party_max_crit = 0
    third_party_count = 0
    well_known_max_crit = 0
    well_known_hostile = 0
    well_known_suspicious = 0
    has_yara = False

    for finding in findings:
        fid = finding.get("i", "")
        if not fid:
            continue
        # _float used to wrap finding.get("c", 1.0) but the value is
        # already a float coming from JSON in 99.9% of cases — the
        # try/float() overhead was hot. Fall back only for stragglers.
        conf_raw = finding.get("c", 1.0)
        conf = conf_raw if isinstance(conf_raw, float) else _float(conf_raw)
        if conf < min_conf:
            continue
        finding_confidences.append(conf)
        filtered_finding_count += 1
        crit_ord = finding.get("l", 0)
        if crit_ord >= 3:
            notable_finding_count += 1
            notable_ids.add(fid)
            if crit_ord >= 4:
                suspicious_finding_count += 1
                suspicious_ids.add(fid)
                if crit_ord >= 5:
                    hostile_finding_count += 1
                    hostile_ids.add(fid)

        slash_pos = fid.find("/")
        top = fid[:slash_pos] if slash_pos >= 0 else fid
        if crit_ord >= 4:
            suspicious_categories.add(top)
            if crit_ord >= 5:
                hostile_categories.add(top)
        if top == "third_party":
            third_party_count += 1
            if crit_ord > third_party_max_crit:
                third_party_max_crit = crit_ord
            if not has_yara:
                has_yara = fid.startswith("third_party/yara")
        elif top == "well-known":
            if crit_ord > well_known_max_crit:
                well_known_max_crit = crit_ord
            if crit_ord >= 5:
                well_known_hostile += 1
            elif crit_ord >= 4:
                well_known_suspicious += 1

        paths = finding_paths(fid)
        if include_soft_presence:
            for path in paths:
                if crit_ord > sample_paths.get(path, -1):
                    sample_paths[path] = crit_ord
                if conf > path_confidences.get(path, 0.0):
                    path_confidences[path] = conf
        else:
            for path in paths:
                if crit_ord > sample_paths.get(path, -1):
                    sample_paths[path] = crit_ord

    return _FindingSummary(
        sample_paths=sample_paths,
        filtered_finding_count=filtered_finding_count,
        notable_finding_count=notable_finding_count,
        suspicious_finding_count=suspicious_finding_count,
        hostile_finding_count=hostile_finding_count,
        unique_notable_ids=len(notable_ids),
        unique_suspicious_ids=len(suspicious_ids),
        unique_hostile_ids=len(hostile_ids),
        suspicious_category_breadth=len(suspicious_categories),
        hostile_category_breadth=len(hostile_categories),
        third_party_max_crit=third_party_max_crit,
        third_party_count=third_party_count,
        well_known_max_crit=well_known_max_crit,
        well_known_hostile=well_known_hostile,
        well_known_suspicious=well_known_suspicious,
        has_yara=has_yara,
        path_confidences=path_confidences,
        finding_confidences=finding_confidences,
    )


def _summarize_report_files(files: list[dict[str, Any]]) -> _FindingSummary:
    """Aggregate findings across every file in the report.

    This makes an embedded file contribute the same capability signal it would
    have as a standalone sample, while still letting the report express
    multi-file/package behavior as a whole.
    """
    sample_paths: dict[str, int] = {}
    filtered_finding_count = 0
    notable_finding_count = 0
    suspicious_finding_count = 0
    hostile_finding_count = 0
    unique_notable_ids: set[str] = set()
    unique_suspicious_ids: set[str] = set()
    unique_hostile_ids: set[str] = set()
    suspicious_categories: set[str] = set()
    hostile_categories: set[str] = set()
    third_party_max_crit = 0
    third_party_count = 0
    well_known_max_crit = 0
    well_known_hostile = 0
    well_known_suspicious = 0
    has_yara = False
    path_confidences: dict[str, float] = {}
    finding_confidences: list[float] = []

    for file_entry in files:
        summary = _summarize_findings(file_entry.get("ts") or [])
        filtered_finding_count += summary.filtered_finding_count
        notable_finding_count += summary.notable_finding_count
        suspicious_finding_count += summary.suspicious_finding_count
        hostile_finding_count += summary.hostile_finding_count
        third_party_count += summary.third_party_count
        well_known_hostile += summary.well_known_hostile
        well_known_suspicious += summary.well_known_suspicious
        suspicious_categories.update(
            path.split("/")[0]
            for path, max_ord in summary.sample_paths.items()
            if max_ord >= 4
        )
        hostile_categories.update(
            path.split("/")[0]
            for path, max_ord in summary.sample_paths.items()
            if max_ord >= 5
        )
        third_party_max_crit = max(third_party_max_crit, summary.third_party_max_crit)
        well_known_max_crit = max(well_known_max_crit, summary.well_known_max_crit)
        has_yara = has_yara or summary.has_yara

        for path, max_ord in summary.sample_paths.items():
            if max_ord > sample_paths.get(path, -1):
                sample_paths[path] = max_ord
            path_confidences[path] = max(path_confidences.get(path, 0.0), summary.path_confidences.get(path, 0.0))

        finding_confidences.extend(summary.finding_confidences)

        for finding in file_entry.get("ts") or []:
            fid = finding.get("i", "")
            if not fid or _float(finding.get("c", 1.0)) < MIN_CONFIDENCE:
                continue
            crit_ord = finding.get("l", 0)
            if crit_ord >= 3:
                unique_notable_ids.add(fid)
            if crit_ord >= 4:
                unique_suspicious_ids.add(fid)
            if crit_ord >= 5:
                unique_hostile_ids.add(fid)

    return _FindingSummary(
        sample_paths=sample_paths,
        filtered_finding_count=filtered_finding_count,
        notable_finding_count=notable_finding_count,
        suspicious_finding_count=suspicious_finding_count,
        hostile_finding_count=hostile_finding_count,
        unique_notable_ids=len(unique_notable_ids),
        unique_suspicious_ids=len(unique_suspicious_ids),
        unique_hostile_ids=len(unique_hostile_ids),
        suspicious_category_breadth=len(suspicious_categories),
        hostile_category_breadth=len(hostile_categories),
        third_party_max_crit=third_party_max_crit,
        third_party_count=third_party_count,
        well_known_max_crit=well_known_max_crit,
        well_known_hostile=well_known_hostile,
        well_known_suspicious=well_known_suspicious,
        has_yara=has_yara,
        path_confidences=path_confidences,
        finding_confidences=finding_confidences,
    )


def _file_risk_stats(file_entry: dict[str, Any]) -> _FileRiskStats:
    """Compute per-file suspiciousness for top-k package aggregation."""
    summary = _summarize_findings(file_entry.get("ts") or [])
    denom = max(summary.filtered_finding_count, 1)
    size_kb = max(_float(file_entry.get("sz", 0.0)) / 1024.0, 1.0)
    return _FileRiskStats(
        suspicious_ratio=summary.suspicious_finding_count / denom,
        hostile_ratio=summary.hostile_finding_count / denom,
        suspicious_findings=summary.suspicious_finding_count,
        hostile_findings=summary.hostile_finding_count,
        suspicious_density=summary.suspicious_finding_count / size_kb,
        hostile_density=summary.hostile_finding_count / size_kb,
        suspicious_category_breadth=summary.suspicious_category_breadth,
        hostile_category_breadth=summary.hostile_category_breadth,
        max_crit=max(summary.sample_paths.values(), default=0),
    )




def _topk_file_risk_features(
    files: list[dict[str, Any]],
    k: int,
    *,
    include_breadth_density: bool = False,
    min_crit: int = 0,
) -> tuple[float, ...]:
    """Summarize the riskiest files so a few bad files survive package dilution.

    `min_crit` filters out files whose max_crit is below the floor before
    sorting. This keeps the top-k from surfacing 0.1-crit noise on archives
    that have no real findings.
    """
    if k <= 0 or not files:
        return 0.0, 0.0, 0.0, 0.0

    stats = [_file_risk_stats(file_entry) for file_entry in files]
    if min_crit > 0:
        stats = [s for s in stats if s.max_crit >= min_crit]
        if not stats:
            return 0.0, 0.0, 0.0, 0.0
    top_suspicious = sorted(
        stats,
        key=lambda s: (s.suspicious_ratio, s.suspicious_findings, s.hostile_ratio, s.hostile_findings),
        reverse=True,
    )[:k]
    top_hostile = sorted(
        stats,
        key=lambda s: (s.hostile_ratio, s.hostile_findings, s.suspicious_ratio, s.suspicious_findings),
        reverse=True,
    )[:k]

    base: tuple[float, ...] = (
        sum(s.suspicious_ratio for s in top_suspicious),
        sum(s.hostile_ratio for s in top_hostile),
        math.log1p(sum(s.suspicious_findings for s in top_suspicious)),
        math.log1p(sum(s.hostile_findings for s in top_hostile)),
    )
    if not include_breadth_density:
        return base
    return base + (
        sum(s.suspicious_density for s in top_suspicious),
        sum(s.hostile_density for s in top_hostile),
        float(sum(s.suspicious_category_breadth for s in top_suspicious)),
        float(sum(s.hostile_category_breadth for s in top_hostile)),
    )


def _assign(vec: np.ndarray, idx: int | None, value: float) -> None:
    """Assign value to vec[idx] if idx is not None."""
    if idx is not None:
        vec[idx] = value


def _apply_presence_features(
    summary: _FindingSummary,
    ctx: _ExtractContext,
    vec: np.ndarray,
    score: int = 0,
) -> None:
    """Group 1: path presence features."""
    config = feature_config_from_env()
    sample_paths = summary.sample_paths
    score_weight = 1.0
    if score > 0:
        score_weight = float(math.log1p(score))

    for path, max_ord in sample_paths.items():
        if max_ord >= 2:  # baseline or above
            idx = ctx.presence_lookup.get(path)
            weight = score_weight
            if config.include_soft_presence:
                weight *= summary.path_confidences.get(path, 1.0)
            _assign(vec, idx, weight)


def _apply_maxcrit_features(
    summary: _FindingSummary,
    ctx: _ExtractContext,
    vec: np.ndarray,
    score: int = 0,
) -> None:
    """Group 2: path maximum criticality features."""
    config = feature_config_from_env()
    sample_paths = summary.sample_paths
    score_weight = 1.0
    if score > 0:
        score_weight = float(math.log1p(score))

    for path, max_ord in sample_paths.items():
        idx = ctx.maxcrit_lookup.get(path)
        weight = score_weight
        if config.include_soft_presence:
            weight *= summary.path_confidences.get(path, 1.0)
        _assign(vec, idx, float(max_ord) * weight)


def _apply_aggregate_features(
    summary: _FindingSummary,
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
    top_k_risk_files: int,
    include_breadth_density: bool,
    include_hostile_escalation: bool,
    include_hostile_weighted_density: bool,
    include_repetition_penalty: bool,
    include_file_severity_distribution: bool,
    top_k_risk_files_min_crit: int = 0,
) -> None:
    """Group 3: aggregate path breadth and concentration features."""
    sample_paths = summary.sample_paths
    breadth_notable = 0
    breadth_suspicious = 0
    breadth_hostile = 0
    breadth_notable_only = 0
    max_crit = 0
    total_active = 0
    categories: set[str] = set()
    path_breadth_any = 0
    # 2-level breadth: "micro-behaviors/network" is more specific than "micro-behaviors".
    suspicious_2level: set[str] = set()
    hostile_2level: set[str] = set()
    objectives_2level: set[str] = set()  # any crit under objectives/

    # Taxonomy-exploitation tracking.
    objectives_phases: set[str] = set()  # 2nd-level under objectives/ (kill chain phases)
    micro_behavior_count = 0
    objectives_count = 0
    all_depths: list[int] = []

    for path, max_ord in sample_paths.items():
        parts = path.split("/")
        all_depths.append(len(parts))

        if max_ord >= 2:
            categories.add(parts[0])
            if len(parts) >= 3:
                path_breadth_any += 1

        # Track 2-level paths for the new breadth features.
        if len(parts) >= 2:
            two_level = f"{parts[0]}/{parts[1]}"
            if max_ord >= 4:
                suspicious_2level.add(two_level)
            if max_ord >= 5:
                hostile_2level.add(two_level)
            if parts[0] == "objectives" and max_ord >= 2:
                objectives_2level.add(two_level)
                objectives_phases.add(parts[1])
                objectives_count += 1
            elif parts[0] == "micro-behaviors":
                micro_behavior_count += 1

        if len(parts) < 3:
            continue
        if max_ord < 3:
            continue
        total_active += 1
        breadth_notable += 1
        if max_ord >= 4:
            breadth_suspicious += 1
        if max_ord > max_crit:
            max_crit = max_ord
        if max_ord >= 5:
            breadth_hostile += 1
        elif max_ord == 3:
            breadth_notable_only += 1

    lookup = ctx.absolute_lookup
    _assign(vec, lookup.get("agg:max_crit"), max_crit)
    _assign(vec, lookup.get("agg:category_breadth"), len(categories))
    _assign(vec, lookup.get("agg:path_breadth_any"), math.log1p(path_breadth_any))
    _assign(vec, lookup.get("agg:total_active_paths"), math.log1p(total_active))
    # Concentration ratios — what fraction of behavior is suspicious?
    _assign(vec, lookup.get("agg:suspicious_concentration"), breadth_suspicious / max(path_breadth_any, 1))
    _assign(vec, lookup.get("agg:hostile_concentration"), breadth_hostile / max(path_breadth_any, 1))
    _assign(vec, lookup.get("agg:escalation_rate"), breadth_suspicious / max(breadth_notable, 1))
    _assign(vec, lookup.get("agg:notable_only_fraction"), breadth_notable_only / max(breadth_notable, 1))
    _assign(vec, lookup.get("agg:notable_findings_log"), math.log1p(summary.notable_finding_count))
    _assign(vec, lookup.get("agg:suspicious_findings_log"), math.log1p(summary.suspicious_finding_count))
    _assign(vec, lookup.get("agg:hostile_findings_log"), math.log1p(summary.hostile_finding_count))
    
    # Pruned raw IDs for density-first metrics.
    total_kb = max(sum(_float(file_entry.get("sz", 0.0)) for file_entry in files) / 1024.0, 0.1)
    _assign(vec, lookup.get("agg:notable_finding_ratio"), summary.notable_finding_count / total_kb)
    _assign(vec, lookup.get("agg:suspicious_finding_ratio"), summary.suspicious_finding_count / total_kb)
    _assign(vec, lookup.get("agg:hostile_finding_ratio"), summary.hostile_finding_count / total_kb)
    _assign(vec, lookup.get("agg:unique_suspicious_ids_log"), math.log1p(summary.unique_suspicious_ids) / math.log1p(total_kb))
    _assign(vec, lookup.get("agg:unique_hostile_ids_log"), math.log1p(summary.unique_hostile_ids) / math.log1p(total_kb))
    total_kb = max(sum(_float(file_entry.get("sz", 0.0)) for file_entry in files) / 1024.0, 1.0)
    topk_features = _topk_file_risk_features(
        files,
        top_k_risk_files,
        include_breadth_density=include_breadth_density,
        min_crit=top_k_risk_files_min_crit,
    )
    topk_susp_ratio, topk_host_ratio, topk_susp_log, topk_host_log = topk_features[:4]
    _assign(vec, lookup.get(f"agg:top{top_k_risk_files}_file_suspicious_ratio_sum"), topk_susp_ratio)
    _assign(vec, lookup.get(f"agg:top{top_k_risk_files}_file_hostile_ratio_sum"), topk_host_ratio)
    _assign(vec, lookup.get(f"agg:top{top_k_risk_files}_file_suspicious_findings_log"), topk_susp_log)
    _assign(vec, lookup.get(f"agg:top{top_k_risk_files}_file_hostile_findings_log"), topk_host_log)
    
    if include_breadth_density:
        category_denom = max(len(categories), 1)
        _assign(vec, lookup.get("agg:suspicious_category_breadth"), float(summary.suspicious_category_breadth))
        _assign(vec, lookup.get("agg:hostile_category_breadth"), float(summary.hostile_category_breadth))
        _assign(vec, lookup.get("agg:suspicious_category_density"), summary.suspicious_category_breadth / category_denom)
        _assign(vec, lookup.get("agg:hostile_category_density"), summary.hostile_category_breadth / category_denom)
        _assign(vec, lookup.get("agg:suspicious_findings_per_kb"), summary.suspicious_finding_count / total_kb)
        _assign(vec, lookup.get("agg:hostile_findings_per_kb"), summary.hostile_finding_count / total_kb)
        _assign(vec, lookup.get("agg:suspicious_categories_per_kb"), summary.suspicious_category_breadth / total_kb)
        _assign(vec, lookup.get("agg:hostile_categories_per_kb"), summary.hostile_category_breadth / total_kb)
        _assign(vec, lookup.get(f"agg:top{top_k_risk_files}_file_suspicious_density_sum"), topk_features[4])
        _assign(vec, lookup.get(f"agg:top{top_k_risk_files}_file_hostile_density_sum"), topk_features[5])
        _assign(vec, lookup.get(f"agg:top{top_k_risk_files}_file_suspicious_category_breadth_sum"), topk_features[6])
        _assign(vec, lookup.get(f"agg:top{top_k_risk_files}_file_hostile_category_breadth_sum"), topk_features[7])

    if include_hostile_escalation:
        _assign(vec, lookup.get("agg:hostile_escalation_rate"), breadth_hostile / max(breadth_notable, 1))
        _assign(vec, lookup.get("agg:hostile_share_of_suspicious"), breadth_hostile / max(breadth_suspicious, 1))
        _assign(vec, lookup.get("agg:suspicious_finding_escalation_rate"), summary.suspicious_finding_count / max(summary.notable_finding_count, 1))
        _assign(vec, lookup.get("agg:hostile_finding_escalation_rate"), summary.hostile_finding_count / max(summary.notable_finding_count, 1))
        _assign(vec, lookup.get("agg:hostile_share_of_suspicious_findings"), summary.hostile_finding_count / max(summary.suspicious_finding_count, 1))

    if include_hostile_weighted_density or include_file_severity_distribution:
        stats = [_file_risk_stats(file_entry) for file_entry in files]
    else:
        stats = []

    if include_hostile_weighted_density:
        top_hostile_weighted = sorted(
            stats,
            key=lambda s: (s.hostile_density + 0.25 * s.suspicious_density, s.hostile_density, s.suspicious_density),
            reverse=True,
        )[:top_k_risk_files]
        _assign(vec, lookup.get("agg:hostile_weighted_density"), summary.hostile_finding_count / total_kb + 0.25 * (summary.suspicious_finding_count / total_kb))
        _assign(vec, lookup.get(f"agg:top{top_k_risk_files}_file_hostile_weighted_density_sum"), sum(s.hostile_density + 0.25 * s.suspicious_density for s in top_hostile_weighted))

    if include_repetition_penalty:
        _assign(vec, lookup.get("agg:suspicious_id_repeat_ratio"), 1.0 - (summary.unique_suspicious_ids / max(summary.suspicious_finding_count, 1)))
        _assign(vec, lookup.get("agg:hostile_id_repeat_ratio"), 1.0 - (summary.unique_hostile_ids / max(summary.hostile_finding_count, 1)))
        _assign(vec, lookup.get("agg:suspicious_category_repeat_ratio"), 1.0 - (summary.suspicious_category_breadth / max(summary.suspicious_finding_count, 1)))
        _assign(vec, lookup.get("agg:hostile_category_repeat_ratio"), 1.0 - (summary.hostile_category_breadth / max(summary.hostile_finding_count, 1)))

    if include_file_severity_distribution:
        n_files = max(len(files), 1)
        hostile_files = sum(s.max_crit >= 5 for s in stats)
        suspicious_files = sum(s.max_crit == 4 for s in stats)
        notable_files = sum(s.max_crit == 3 for s in stats)
        _assign(vec, lookup.get("agg:file_hostile_fraction"), hostile_files / n_files)
        _assign(vec, lookup.get("agg:file_suspicious_fraction"), suspicious_files / n_files)
        _assign(vec, lookup.get("agg:file_notable_fraction"), notable_files / n_files)
        _assign(vec, lookup.get("agg:file_hostile_count_log"), math.log1p(hostile_files))
        _assign(vec, lookup.get("agg:file_suspicious_count_log"), math.log1p(suspicious_files))
        _assign(vec, lookup.get("agg:file_notable_count_log"), math.log1p(notable_files))

    # 2-level breadth features: more discriminative than top-1 category breadth.
    _assign(vec, lookup.get("agg:suspicious_2level_breadth"), float(len(suspicious_2level)))
    _assign(vec, lookup.get("agg:hostile_2level_breadth"), float(len(hostile_2level)))
    _assign(vec, lookup.get("agg:objectives_breadth"), float(len(objectives_2level)))

    # Taxonomy-exploitation features.
    _assign(vec, lookup.get("agg:kill_chain_span"), float(len(objectives_phases)))
    _assign(vec, lookup.get("agg:objective_micro_ratio"),
            objectives_count / max(micro_behavior_count, 1))
    avg_depth = sum(all_depths) / max(len(all_depths), 1) if all_depths else 0.0
    _assign(vec, lookup.get("agg:avg_finding_depth"), avg_depth)
    hostile_conc = breadth_hostile / max(total_active, 1) if total_active > 0 else 0.0
    _assign(vec, lookup.get("agg:objective_hostile_density"),
            float(len(objectives_2level)) * hostile_conc)


# ---------------------------------------------------------------------------
# Import functional categories for experiments 1 & 2.
# ---------------------------------------------------------------------------

_SUSPICIOUS_API_CATEGORIES = {
    "process_inject": {"VirtualAllocEx", "WriteProcessMemory", "CreateRemoteThread",
                       "NtUnmapViewOfSection", "QueueUserAPC", "NtWriteVirtualMemory"},
    "network": {"InternetOpenA", "InternetOpenW", "InternetOpenUrlA", "InternetOpenUrlW",
                "URLDownloadToFileA", "URLDownloadToFileW", "HttpSendRequestA",
                "HttpSendRequestW", "WSAStartup", "WinHttpOpen", "HttpOpenRequestA"},
    "crypto": {"CryptEncrypt", "CryptDecrypt", "CryptHashData", "CryptCreateHash",
               "CryptAcquireContextA", "CryptAcquireContextW", "BCryptEncrypt"},
    "anti_debug": {"IsDebuggerPresent", "CheckRemoteDebuggerPresent",
                   "NtQueryInformationProcess", "OutputDebugStringA"},
    "service": {"CreateServiceA", "CreateServiceW", "StartServiceA", "StartServiceW",
                "OpenSCManagerA", "OpenSCManagerW", "ChangeServiceConfigA"},
    "registry": {"RegSetValueExA", "RegSetValueExW", "RegCreateKeyExA",
                 "RegCreateKeyExW", "RegDeleteKeyA", "RegDeleteKeyW",
                 "RegDeleteValueA", "RegDeleteValueW"},
    "privilege": {"AdjustTokenPrivileges", "OpenProcessToken", "LookupPrivilegeValueA",
                  "LookupPrivilegeValueW", "ImpersonateLoggedOnUser"},
    "execution": {"ShellExecuteA", "ShellExecuteW", "ShellExecuteExA", "ShellExecuteExW",
                  "CreateProcessA", "CreateProcessW", "WinExec", "system"},
    "stealth": {"SetWindowsHookExA", "SetWindowsHookExW", "DeleteFileA", "DeleteFileW",
                "MoveFileA", "MoveFileW", "SetFileAttributesA", "SetFileAttributesW"},
    "keylog": {"GetAsyncKeyState", "GetKeyState", "SetWindowsHookExA",
               "GetForegroundWindow", "GetWindowTextA", "GetWindowTextW"},
}

# Flatten for quick lookup: symbol → set of categories it belongs to.
_SYMBOL_TO_CATEGORIES: dict[str, set[str]] = {}
for _cat, _syms in _SUSPICIOUS_API_CATEGORIES.items():
    for _s in _syms:
        _SYMBOL_TO_CATEGORIES.setdefault(_s, set()).add(_cat)

# Categories considered especially suspicious when co-occurring.
_HIGH_RISK_COMBOS = {"process_inject", "network", "crypto", "anti_debug", "privilege", "keylog"}


def _apply_experimental_features(
    report: dict[str, Any],
    summary: _FindingSummary,
    files: list[dict[str, Any]],
    metrics: dict[str, dict[str, float]],
    ctx: _ExtractContext,
    vec: np.ndarray,
    score: int,
) -> None:
    """Compute the 10 experimental features (2026-04-13 batch)."""
    config = feature_config_from_env()
    lookup = ctx.absolute_lookup

    # Collect import data once for import-based features.
    import_categories: set[str] = set()
    total_imports = 0
    if config.exp_import_categories or config.exp_suspicious_api_combo or \
       config.exp_unsigned_import_density or config.exp_import_finding_ratio:
        import re
        api_pattern = re.compile(r'^[A-Z][a-zA-Z0-9_]{3,}[A-Za-z]$')
        for file_entry in files:
            for sym in _file_symbols(file_entry):
                if not api_pattern.match(sym):
                    continue
                total_imports += 1
                cats = _SYMBOL_TO_CATEGORIES.get(sym)
                if cats:
                    import_categories.update(cats)

    # Exp 1: Import functional category count.
    if config.exp_import_categories:
        _assign(vec, lookup.get("agg:import_category_count"), float(len(import_categories)))

    # Exp 2: Suspicious API combo score — count of high-risk categories present.
    if config.exp_suspicious_api_combo:
        high_risk_present = import_categories & _HIGH_RISK_COMBOS
        _assign(vec, lookup.get("agg:suspicious_api_combo"), float(len(high_risk_present)))

    # Exp 3 / Batch 4: Confidence distribution features. The legacy EXP_3
    # path emits mean+std; the Batch-4 promotion adds skew+kurtosis as
    # 3rd/4th moments. Either flag triggers the mean+std columns; only
    # trait_confidence_moments adds the higher moments.
    if config.exp_confidence_skew or config.include_trait_confidence_moments:
        confs = summary.finding_confidences
        if confs:
            n = len(confs)
            mean_c = sum(confs) / n
            var_c = sum((c - mean_c) ** 2 for c in confs) / n
            _assign(vec, lookup.get("agg:confidence_mean"), mean_c)
            _assign(vec, lookup.get("agg:confidence_std"), var_c ** 0.5)
            if config.include_trait_confidence_moments:
                std_c = var_c ** 0.5
                if std_c > 1e-9:
                    skew = sum((c - mean_c) ** 3 for c in confs) / n / (std_c ** 3)
                    kurt = sum((c - mean_c) ** 4 for c in confs) / n / (std_c ** 4) - 3.0
                else:
                    skew, kurt = 0.0, 0.0
                _assign(vec, lookup.get("agg:confidence_skew"), skew)
                _assign(vec, lookup.get("agg:confidence_kurtosis"), kurt)

    # Exp 4: Finding depth variance.
    if config.exp_finding_depth_var:
        depths = [len(p.split("/")) for p in summary.sample_paths]
        if len(depths) >= 2:
            mean_d = sum(depths) / len(depths)
            var_d = sum((d - mean_d) ** 2 for d in depths) / len(depths)
            _assign(vec, lookup.get("agg:finding_depth_var"), var_d ** 0.5)

    # Exp 5: Multi-file crit spread — max crit difference across files.
    if config.exp_multifile_crit_spread:
        file_max_crits: list[int] = []
        for file_entry in files:
            fmax = 0
            for finding in (file_entry.get("ts") or []):
                crit = finding.get("l", 0)
                if crit > fmax:
                    fmax = crit
            file_max_crits.append(fmax)
        if len(file_max_crits) >= 2:
            spread = max(file_max_crits) - min(file_max_crits)
            _assign(vec, lookup.get("agg:multifile_crit_spread"), float(spread))

    # Exp 6: Metric anomaly composite — normalized sum of suspicious metrics.
    if config.exp_metric_anomaly:
        binary = metrics.get("binary", metrics.get("pe", {}))
        anomaly = 0.0
        entropy = _float(binary.get("overall_entropy", 0))
        if entropy > 6.5:
            anomaly += 1.0  # high entropy
        import_density = _float(binary.get("import_density", 0))
        if import_density > 5.0:
            anomaly += 1.0  # high import density
        overlay_ratio = _float(binary.get("overlay_ratio", 0))
        if overlay_ratio > 0.3:
            anomaly += 1.0  # large overlay
        func_count = _float(binary.get("function_count", 0))
        if 0 < func_count < 10:
            anomaly += 1.0  # suspiciously few functions
        complexity = _float(binary.get("complexity_per_kb", 0))
        if complexity > 2.0:
            anomaly += 1.0  # high complexity
        _assign(vec, lookup.get("agg:metric_anomaly"), anomaly)

    # Exp 7: Unsigned × import density interaction.
    if config.exp_unsigned_import_density:
        is_unsigned = "metadata/unsigned" in summary.sample_paths
        if is_unsigned and total_imports > 0:
            total_size = sum(_float(f.get("sz", 0)) for f in files) or 1.0
            density = total_imports / (total_size / 1024.0)
            _assign(vec, lookup.get("agg:unsigned_import_density"), density)

    # Exp 8: Entropy × hostile concentration.
    if config.exp_entropy_hostile:
        binary = metrics.get("binary", metrics.get("pe", {}))
        entropy = _float(binary.get("overall_entropy", 0))
        total_findings = max(summary.filtered_finding_count, 1)
        hostile_conc = summary.hostile_finding_count / total_findings
        _assign(vec, lookup.get("agg:entropy_hostile"), entropy * hostile_conc)

    # Exp 9: Hostile-level objective category diversity.
    if config.exp_hostile_objective_div:
        hostile_obj_cats: set[str] = set()
        for path, max_ord in summary.sample_paths.items():
            if max_ord >= 5 and path.startswith("objectives/"):
                parts = path.split("/")
                if len(parts) >= 2:
                    hostile_obj_cats.add(parts[1])
        _assign(vec, lookup.get("agg:hostile_objective_diversity"), float(len(hostile_obj_cats)))

    # Exp 10: Import-to-finding ratio.
    if config.exp_import_finding_ratio:
        finding_count = max(summary.filtered_finding_count, 1)
        _assign(vec, lookup.get("agg:import_finding_ratio"),
                math.log1p(total_imports) / math.log1p(finding_count))

    # Batch 4: trait_id lexical distance — average per-character edit distance
    # between consecutive sorted trait IDs. Bursts of similar IDs (e.g.
    # `xattr-list-listxattr`, `xattr-list-llistxattr`) shrink the average;
    # scattershot IDs spanning unrelated subtrees grow it.
    if config.include_trait_id_lexical_distance:
        all_ids: set[str] = set()
        for fe in files:
            for finding in fe.get("ts") or []:
                fid = finding.get("i")
                if isinstance(fid, str) and fid:
                    all_ids.add(fid)
        sorted_ids = sorted(all_ids)
        if len(sorted_ids) >= 2:
            total = sum(_lexical_distance(sorted_ids[i], sorted_ids[i + 1])
                        for i in range(len(sorted_ids) - 1))
            avg = total / (len(sorted_ids) - 1)
        else:
            avg = 0.0
        _assign(vec, lookup.get("agg:trait_id_lexical_distance"), avg)

    # Batch 4: document-obfuscation aggregate counts. Cleave's document-malware
    # taxonomy concentrates under three subtree prefixes; counting findings
    # under each gives the model a dedicated "document is doing
    # obfuscation/eval/lure things" signal that doesn't get diluted by the
    # general taxonomy presence vocabulary.
    if config.include_document_obfuscation_features:
        obf_count = eval_count = lure_count = 0
        for fe in files:
            for finding in fe.get("ts") or []:
                fid = finding.get("i", "")
                if not isinstance(fid, str):
                    continue
                if fid.startswith("objectives/anti-static/obfuscation/document"):
                    obf_count += 1
                elif fid.startswith("objectives/execution/interpreter/eval"):
                    eval_count += 1
                elif fid.startswith("objectives/execution/lure/document"):
                    lure_count += 1
        total = obf_count + eval_count + lure_count
        _assign(vec, lookup.get("agg:docobf_obfuscation_count"), float(obf_count))
        _assign(vec, lookup.get("agg:docobf_eval_count"), float(eval_count))
        _assign(vec, lookup.get("agg:docobf_lure_count"), float(lure_count))
        _assign(vec, lookup.get("agg:docobf_total_count"), float(total))
        _assign(vec, lookup.get("agg:docobf_has_any"), 1.0 if total > 0 else 0.0)

    if config.include_ember_lite_features:
        _apply_ember_lite_features(files, ctx, vec)

    # ATT&CK / MBC features from 'a' and 'm' fields in findings.
    if config.include_attack_features:
        attack_techniques: set[str] = set()
        mbc_behaviors: set[str] = set()
        for file_entry in files:
            for finding in file_entry.get("ts") or []:
                a = finding.get("a")
                if a:
                    attack_techniques.add(a)
                m = finding.get("m")
                if m:
                    mbc_behaviors.add(m)
        # ATT&CK tactics: T1xxx.yyy → T1xxx is the technique, first 2 digits = tactic
        # But T-codes don't directly encode tactics — use unique technique count instead.
        _assign(vec, lookup.get("agg:attack_technique_count"), float(len(attack_techniques)))
        # Group by technique prefix (e.g., T10xx = execution, T15xx = defense evasion)
        tactic_prefixes = {t[:4] for t in attack_techniques if t.startswith("T") and len(t) >= 4}
        _assign(vec, lookup.get("agg:attack_tactic_count"), float(len(tactic_prefixes)))
        _assign(vec, lookup.get("agg:mbc_behavior_count"), float(len(mbc_behaviors)))
        has_objectives = any(p.startswith("objectives/") for p in summary.sample_paths)
        _assign(vec, lookup.get("agg:has_attack_and_objective"),
                1.0 if attack_techniques and has_objectives else 0.0)

    # Objective-only trigrams: combinations of objectives/* and well-known/* paths.
    # These capture attack-intent patterns regardless of criticality level.
    if config.include_objective_trigrams:
        obj_paths: set[str] = set()
        for path in summary.sample_paths:
            if path.startswith(("objectives/", "well-known/")):
                obj_paths.add(path)
        obj_sorted = sorted(obj_paths)
        n_obj_bi = 0
        n_obj_tri = 0
        for i in range(len(obj_sorted)):
            for j in range(i + 1, len(obj_sorted)):
                n_obj_bi += 1
                for k in range(j + 1, min(len(obj_sorted), j + 20)):  # cap to avoid O(n^3) explosion
                    n_obj_tri += 1
        _assign(vec, lookup.get("agg:objective_bigram_count"), math.log1p(n_obj_bi))
        _assign(vec, lookup.get("agg:objective_trigram_count"), math.log1p(n_obj_tri))

    # Suspicious+ trigrams: combinations from only suspicious/hostile findings.
    if config.include_suspicious_trigrams:
        sus_paths = sorted({
            path for path, max_ord in summary.sample_paths.items()
            if max_ord >= 4
        })
        n_sus_bi = 0
        n_sus_tri = 0
        for i in range(len(sus_paths)):
            for j in range(i + 1, len(sus_paths)):
                n_sus_bi += 1
                for k in range(j + 1, min(len(sus_paths), j + 20)):
                    n_sus_tri += 1
        _assign(vec, lookup.get("agg:suspicious_bigram_count"), math.log1p(n_sus_bi))
        _assign(vec, lookup.get("agg:suspicious_trigram_count"), math.log1p(n_sus_tri))

    # ATT&CK/MBC n-grams: co-occurring ATT&CK techniques and MBC behaviors.
    if config.include_attack_ngrams and attack_techniques:
        sorted_attacks = sorted(attack_techniques)
        n_atk_bi = 0
        n_atk_tri = 0
        for i in range(len(sorted_attacks)):
            for j in range(i + 1, len(sorted_attacks)):
                n_atk_bi += 1
                for k in range(j + 1, len(sorted_attacks)):
                    n_atk_tri += 1
        _assign(vec, lookup.get("agg:attack_bigram_count"), math.log1p(n_atk_bi))
        _assign(vec, lookup.get("agg:attack_trigram_count"), math.log1p(n_atk_tri))
        sorted_mbc = sorted(mbc_behaviors)
        n_mbc_bi = sum(1 for i in range(len(sorted_mbc)) for j in range(i + 1, len(sorted_mbc)))
        _assign(vec, lookup.get("agg:mbc_bigram_count"), math.log1p(n_mbc_bi))


def _apply_external_signal_features(
    summary: _FindingSummary,
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 4: aggregated third-party and well-known signals."""
    lookup = ctx.absolute_lookup
    _assign(vec, lookup.get("ext:third_party_max_crit"), summary.third_party_max_crit)
    _assign(vec, lookup.get("ext:third_party_count"), math.log1p(summary.third_party_count))
    _assign(vec, lookup.get("ext:well_known_max_crit"), summary.well_known_max_crit)
    _assign(vec, lookup.get("ext:well_known_hostile_count"), summary.well_known_hostile)
    _assign(vec, lookup.get("ext:well_known_suspicious_count"), summary.well_known_suspicious)
    _assign(vec, lookup.get("ext:has_yara_match"), 1.0 if summary.has_yara else 0.0)


def _metric_number(metrics: dict[str, Any], group: str, field: str) -> float:
    return _float((metrics.get(group) or {}).get(field))


def _metric_bool(metrics: dict[str, Any], group: str, field: str) -> bool:
    raw = (metrics.get(group) or {}).get(field)
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, (int, float)):
        return raw != 0
    if isinstance(raw, str):
        return raw.strip().lower() in {"1", "true", "yes", "on"}
    return False


def _apply_ember_lite_features(
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Portable EMBER-style aggregates using cleave metrics already in reports."""
    lookup = ctx.absolute_lookup
    analyzed_files = 0
    total_file_bytes = 0.0
    import_count = 0.0
    export_count = 0.0
    dependency_count = 0.0
    string_count = 0.0
    wide_string_count = 0.0
    max_string_length = 0.0
    max_string_entropy = 0.0
    text_lines = 0.0
    function_count = 0.0
    code_bytes = 0.0
    code_to_data_ratio = 0.0
    wx_units = 0.0
    writable_units = 0.0
    executable_units = 0.0
    structural_units = 0.0
    nonstandard_unit_names = 0.0
    largest_unit_ratio = 0.0
    resource_ratio = 0.0
    signed_files = 0

    for file_entry in files:
        metrics = file_metrics(file_entry)
        if not metrics:
            continue

        analyzed_files += 1
        binary = metrics.get("binary") or {}
        total_file_bytes += _metric_number(metrics, "binary", "file_size") or _float(file_entry.get("sz", 0))
        import_count += _metric_number(metrics, "binary", "import_count")
        export_count += _metric_number(metrics, "binary", "export_count")
        dependency_count += _metric_number(metrics, "binary", "dependency_count")
        strings = _metric_number(metrics, "binary", "string_count")
        string_count += strings
        wide_string_count += _metric_number(metrics, "binary", "wide_string_count")
        max_string_length = max(max_string_length, _metric_number(metrics, "binary", "max_string_length"))
        max_string_entropy = max(max_string_entropy, _metric_number(metrics, "binary", "avg_string_entropy"))
        text_lines += _metric_number(metrics, "text", "total_lines")
        function_count += _metric_number(metrics, "binary", "function_count")
        code_bytes += _metric_number(metrics, "binary", "code_size")
        code_to_data_ratio = max(code_to_data_ratio, _metric_number(metrics, "binary", "code_to_data_ratio"))
        wx_units += _metric_number(metrics, "binary", "wx_sections")
        writable_units += _metric_number(metrics, "binary", "writable_sections")
        executable_units += _metric_number(metrics, "binary", "executable_sections")
        structural_units += _metric_number(metrics, "binary", "section_count")
        nonstandard_unit_names += _metric_number(metrics, "binary", "nonstandard_section_name_count")
        largest_unit_ratio = max(largest_unit_ratio, _metric_number(metrics, "binary", "largest_section_ratio"))
        resource_ratio = max(resource_ratio, _metric_number(metrics, "binary", "rsrc_to_file_ratio"))
        if _metric_bool(metrics, "binary", "has_signature") or bool(binary.get("signature_type")):
            signed_files += 1

    denom_files = max(analyzed_files, 1)
    denom_units = max(structural_units, 1.0)
    denom_strings = max(string_count, 1.0)
    _assign(vec, lookup.get("agg:static_file_bytes_log"), math.log1p(total_file_bytes))
    _assign(vec, lookup.get("agg:static_import_count_log"), math.log1p(import_count))
    _assign(vec, lookup.get("agg:static_export_count_log"), math.log1p(export_count))
    _assign(vec, lookup.get("agg:static_dependency_count_log"), math.log1p(dependency_count))
    _assign(vec, lookup.get("agg:static_string_count_log"), math.log1p(string_count))
    _assign(vec, lookup.get("agg:static_wide_string_ratio"), wide_string_count / denom_strings)
    _assign(vec, lookup.get("agg:static_max_string_length_log"), math.log1p(max_string_length))
    _assign(vec, lookup.get("agg:static_string_entropy_max"), max_string_entropy)
    _assign(vec, lookup.get("agg:static_text_lines_log"), math.log1p(text_lines))
    _assign(vec, lookup.get("agg:static_function_count_log"), math.log1p(function_count))
    _assign(vec, lookup.get("agg:static_code_bytes_log"), math.log1p(code_bytes))
    _assign(vec, lookup.get("agg:static_code_to_data_ratio_max"), code_to_data_ratio)
    _assign(vec, lookup.get("agg:static_wx_units_log"), math.log1p(wx_units))
    _assign(vec, lookup.get("agg:static_writable_unit_ratio"), writable_units / denom_units)
    _assign(vec, lookup.get("agg:static_executable_unit_ratio"), executable_units / denom_units)
    _assign(vec, lookup.get("agg:static_nonstandard_unit_names_log"), math.log1p(nonstandard_unit_names))
    _assign(vec, lookup.get("agg:static_largest_unit_ratio_max"), largest_unit_ratio)
    _assign(vec, lookup.get("agg:static_resource_ratio_max"), resource_ratio)
    _assign(vec, lookup.get("agg:static_signed_file_fraction"), signed_files / denom_files)


def _apply_metric_features(
    metrics: dict[str, Any],
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 5: curated numeric metrics + Batch-1 toggles + extended vocab."""
    lookup = ctx.absolute_lookup
    config = feature_config_from_env()
    for group, fname, use_log in KEY_METRICS:
        val = _float((metrics.get(group) or {}).get(fname))
        if use_log:
            val = math.log1p(abs(val))
        _assign(vec, lookup.get(f"metrics:{group}_{fname}"), val)

    batch1_seen: set[str] = set()
    for table in _batch1_enabled_tables(config):
        for suffix, getter, use_log in table:
            val = getter(metrics, files)
            if use_log:
                val = math.log1p(abs(val))
            _assign(vec, lookup.get(f"metrics:{suffix}"), val)
            batch1_seen.add(suffix)

    for suffix, (group_a, key_a), (group_b, key_b) in _metric_correlation_columns(config):
        product = _metric_number(metrics, group_a, key_a) * _metric_number(metrics, group_b, key_b)
        _assign(vec, lookup.get(f"metrics:{suffix}"), product)
        batch1_seen.add(suffix)

    if config.include_extended_metrics:
        # Extract all numeric metrics in the extended vocabulary.
        # Skip keys already handled by KEY_METRICS or a Batch-1 toggle so
        # we don't overwrite their (possibly log-transformed) values.
        base_keys = {f"{g}_{f}" for g, f, _ in KEY_METRICS} | batch1_seen
        for group, fields in metrics.items():
            if not isinstance(fields, dict):
                continue
            for fname, raw_value in fields.items():
                key = f"{group}_{fname}"
                if key in base_keys:
                    continue
                idx = lookup.get(f"metrics:{key}")
                if idx is not None:
                    val = _float(raw_value)
                    if any(w in fname for w in ("count", "size", "total", "bytes", "length")):
                        val = math.log1p(abs(val))
                    _assign(vec, idx, val)


def _apply_symbol_vocab_features(
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Experimental import/symbol vocabulary features."""
    lookup = ctx.absolute_lookup
    for file_entry in files:
        for sym in _file_symbols(file_entry):
            _assign(vec, lookup.get(f"symbol:{sym}"), 1.0)


def _apply_symbol_bigram_features(
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Batch 3: bigram multi-hot over import/symbol pairs (capped per file)."""
    lookup = ctx.absolute_lookup
    for file_entry in files:
        for bi in _file_symbol_bigrams(file_entry):
            _assign(vec, lookup.get(f"symbol_bi:{bi}"), 1.0)


def _apply_symbol_trigram_features(
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Batch 3: trigram multi-hot over import/symbol triples (capped per file)."""
    lookup = ctx.absolute_lookup
    for file_entry in files:
        for tri in _file_symbol_trigrams(file_entry):
            _assign(vec, lookup.get(f"symbol_tri:{tri}"), 1.0)


def _apply_mbc_id_features(
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Batch 4: bag-of-MBC-IDs binary multi-hot from the trait `m` field.

    Mirrors the symbol_vocab shape but pulls from the Malware Behavior
    Catalog code on each finding (e.g. `E1082`, `T1083`). Distinct from
    attack_features (which exposes only aggregate counts) and from the
    existing mbc_bigram_vocab/mbc_trigram_vocab (which capture co-occurrence).
    """
    lookup = ctx.absolute_lookup
    for fe in files:
        for finding in fe.get("ts") or []:
            mid = finding.get("m")
            if isinstance(mid, str) and mid:
                _assign(vec, lookup.get(f"mbc:{mid}"), 1.0)


def _lexical_distance(a: str, b: str) -> int:
    """Levenshtein distance between two strings. Linear-space DP.

    Used by the trait_id_lexical_distance aggregate feature; tiny enough
    to inline if it ever shows up as a hot path, but kept as a helper for
    test coverage of the edge cases (empty strings, unicode).
    """
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            curr[j] = min(
                prev[j] + 1,
                curr[j - 1] + 1,
                prev[j - 1] + (0 if ca == cb else 1),
            )
        prev = curr
    return prev[-1]


def _apply_kv_vocab_features(
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Experimental categorical ms.* key/value vocabulary features."""
    lookup = ctx.absolute_lookup
    config = feature_config_from_env()
    for file_entry in files:
        for token in _metric_kv_tokens(
            file_entry,
            include_shape=config.include_kv_shape_features,
            split_string_values=config.include_kv_value_split,
        ):
            _assign(vec, lookup.get(f"kv:{token}"), 1.0)


def _apply_text_encoding_features(
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Experimental string/text encoding shape features."""
    lookup = ctx.absolute_lookup
    strings: list[tuple[str, bool]] = []
    for file_entry in files:
        strings.extend(_string_values(file_entry))
    n = len(strings)
    if n == 0:
        return
    lengths = [len(s) for s, _wide in strings]
    base64ish = 0
    hexish = 0
    urlish = 0
    pathish = 0
    unicode_escape = 0
    wide = 0
    high_entropy = 0
    long_token = 0
    short_junk = 0
    for value, is_wide in strings:
        lower = value.lower()
        if _looks_base64ish(value):
            base64ish += 1
        if _looks_hexish(value):
            hexish += 1
        if "http://" in lower or "https://" in lower or "://" in lower or "%2f" in lower:
            urlish += 1
        if "/" in value or "\\" in value or lower.startswith(("c:", "./", "../")):
            pathish += 1
        if "\\x" in value or "\\u" in value or "%u" in lower:
            unicode_escape += 1
        if is_wide:
            wide += 1
        if len(value) >= 24 and _char_entropy(value) >= 4.0:
            high_entropy += 1
        if len(value) >= 80:
            long_token += 1
        if 4 <= len(value) <= 8 and _char_entropy(value) >= 2.4:
            short_junk += 1

    denom = max(n, 1)
    _assign(vec, lookup.get("textenc:string_count_log"), math.log1p(n))
    _assign(vec, lookup.get("textenc:avg_len_log"), math.log1p(sum(lengths) / denom))
    _assign(vec, lookup.get("textenc:max_len_log"), math.log1p(max(lengths)))
    _assign(vec, lookup.get("textenc:base64ish_ratio"), base64ish / denom)
    _assign(vec, lookup.get("textenc:hexish_ratio"), hexish / denom)
    _assign(vec, lookup.get("textenc:urlish_ratio"), urlish / denom)
    _assign(vec, lookup.get("textenc:pathish_ratio"), pathish / denom)
    _assign(vec, lookup.get("textenc:unicode_escape_ratio"), unicode_escape / denom)
    _assign(vec, lookup.get("textenc:wide_ratio"), wide / denom)
    _assign(vec, lookup.get("textenc:high_entropy_ratio"), high_entropy / denom)
    _assign(vec, lookup.get("textenc:long_token_ratio"), long_token / denom)
    _assign(vec, lookup.get("textenc:short_junk_ratio"), short_junk / denom)


def _apply_filetype_features(
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 6: file type multi-hot features across all files."""
    if not ctx.blindfold:
        for file_entry in files:
            idx = ctx.ft_lookup.get(file_entry.get("type", ""))
            _assign(vec, idx, 1.0)


def _format_groups_for_type(file_type: str) -> tuple[str, ...]:
    """Return coarse portable format groups for a cleave-reported file type."""
    normalized = str(file_type or "").strip().lower()
    if not normalized:
        return ()
    return tuple(group for group in _FORMAT_GROUP_ORDER if normalized in FORMAT_GROUPS[group])


def _apply_format_hint_features(
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Format-group hints derived only from cleave file type fields."""
    lookup = ctx.absolute_lookup
    total_files = max(len(files), 1)
    inner_files = 0
    known_files = 0
    group_file_counts = {group: 0 for group in _FORMAT_GROUP_ORDER}
    group_inner_counts = {group: 0 for group in _FORMAT_GROUP_ORDER}
    group_suspicious_counts = {group: 0 for group in _FORMAT_GROUP_ORDER}
    group_hostile_counts = {group: 0 for group in _FORMAT_GROUP_ORDER}
    present_groups: set[str] = set()

    for file_entry in files:
        groups = _format_groups_for_type(str(file_entry.get("type", "")))
        is_inner = bool(file_entry.get("p")) or _float(file_entry.get("depth", file_entry.get("dp", 0))) > 0
        if is_inner:
            inner_files += 1
        if groups:
            known_files += 1
        file_summary = _summarize_findings(file_entry.get("ts") or [])
        for group in groups:
            present_groups.add(group)
            group_file_counts[group] += 1
            if is_inner:
                group_inner_counts[group] += 1
            if file_summary.suspicious_finding_count > 0:
                group_suspicious_counts[group] += 1
            if file_summary.hostile_finding_count > 0:
                group_hostile_counts[group] += 1

    inner_denom = max(inner_files, 1)
    for group in _FORMAT_GROUP_ORDER:
        group_count = group_file_counts[group]
        group_denom = max(group_count, 1)
        _assign(vec, lookup.get(f"format:{group}"), 1.0 if group_count > 0 else 0.0)
        _assign(vec, lookup.get(f"format:{group}_file_fraction"), group_count / total_files)
        _assign(vec, lookup.get(f"format:{group}_inner_fraction"), group_inner_counts[group] / inner_denom)
        _assign(vec, lookup.get(f"format:{group}_suspicious_fraction"), group_suspicious_counts[group] / group_denom)
        _assign(vec, lookup.get(f"format:{group}_hostile_fraction"), group_hostile_counts[group] / group_denom)

    _assign(vec, lookup.get("format:group_count_log"), math.log1p(len(present_groups)))
    _assign(vec, lookup.get("format:mixed_script_binary"), 1.0 if {"script", "native_binary"} <= present_groups else 0.0)
    _assign(vec, lookup.get("format:mixed_archive_script"), 1.0 if {"archive_package", "script"} <= present_groups else 0.0)
    _assign(vec, lookup.get("format:mixed_archive_binary"), 1.0 if {"archive_package", "native_binary"} <= present_groups else 0.0)
    _assign(vec, lookup.get("format:unknown_file_fraction"), (total_files - known_files) / total_files)


def _apply_element_features(
    elements: str,
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 8: element multi-hot features and filetype interactions."""
    if elements:
        present_types = {f.get("type", "") for f in files if f.get("type")}
        for el in elements.split(","):
            el = el.strip()
            _assign(vec, ctx.element_lookup.get(el), 1.0)
            for ft in present_types:
                _assign(vec, ctx.element_interaction_lookup.get((ft, el)), 1.0)


def _apply_formula_features(
    formula: str,
    finding_count: int,
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 9: formula features."""
    lookup = ctx.absolute_lookup
    skeleton = "".join([c for c in formula if c.isalpha()])
    _assign(vec, lookup.get("formula:skeleton_len"), float(len(skeleton)))
    _assign(vec, lookup.get("formula:unique_elements"), float(len(set(skeleton))))
    if finding_count > 0:
        _assign(vec, lookup.get("formula:complexity_ratio"), float(len(formula)) / finding_count)


def _apply_score_features(
    score: int,
    total_size: float,
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 10: hopper score features and filetype interactions."""
    lookup = ctx.absolute_lookup
    _assign(vec, lookup.get("score:hopper_score"), float(score))
    _assign(vec, lookup.get("score:density"), float(score) / math.log1p(total_size) if total_size > 0 else 0.0)
    
    # Interaction with filetype.
    for file_entry in files:
        ft = file_entry.get("type", "")
        _assign(vec, ctx.score_interaction_lookup.get(ft), float(score))


def _apply_structural_features(
    files: list[dict[str, Any]],
    filtered_finding_count: int,
    ctx: _ExtractContext,
    vec: np.ndarray,
    include_file_risk_coverage: bool,
    mtime_str: str = "",
    formula: str = "",
    summary: "_FindingSummary | None" = None,
) -> None:
    """Group 7: structural / container context (7)."""
    lookup = ctx.absolute_lookup
    binary_like = {"pe", "elf", "macho"}
    any_tiny_binary = False
    import_candidates = 0
    importless_candidates = 0
    max_entropy = 0.0
    suspicious_files = 0
    hostile_files = 0
    hostile_files_with_parent = 0
    inner_file_count = 0
    total_loc = 0
    extension_mismatches = 0
    has_source_files = False
    has_foreign_binaries = False
    source_types = {"javascript", "python", "typescript", "ruby", "php"}

    # Track mtimes and entropies across the report.
    mtimes: list[float] = []
    entropies: list[float] = []
    hostile_mtimes: list[float] = []
    code_entropies: list[float] = []
    if mtime_str:
        try:
            dt = datetime.fromisoformat(mtime_str.replace(" ", "T"))
            mtimes.append(dt.timestamp())
        except (ValueError, TypeError):
            pass

    # Nesting depth calculation.
    depths: dict[str, int] = {}
    for file_entry in files:
        fpath = file_entry.get("path", "")
        parent = file_entry.get("p", "")
        if not parent:
            depths[fpath] = 0
        else:
            depths[fpath] = depths.get(parent, 0) + 1
    max_nesting_depth = max(depths.values(), default=0)

    for file_entry in files:
        if file_entry.get("p"):
            inner_file_count += 1
        
        ftype = file_entry.get("type", "")
        if ftype in source_types:
            has_source_files = True
        if ftype in binary_like:
            if has_source_files:
                has_foreign_binaries = True
        
        # Track lines of code for density
        per_file_metrics = file_metrics(file_entry)
        text_metrics = per_file_metrics.get("text") or {}
        total_loc += int(_float(text_metrics.get("total_lines", 0)))

        # Track extension mismatches
        fpath = file_entry.get("path", "")
        if fpath and "." in fpath:
            ext = fpath.split(".")[-1].lower()
            if ftype in binary_like and ext in {"txt", "md", "json", "png", "jpg"}:
                extension_mismatches += 1

        fmt = file_entry.get("mt")
        if fmt:
            try:
                mtimes.append(datetime.fromisoformat(str(fmt).replace(" ", "T")).timestamp())
            except (ValueError, TypeError):
                pass

        if file_entry.get("type", "") in binary_like and _float(file_entry.get("sz", 0)) < 20000:
            any_tiny_binary = True
        imports = file_imports(file_entry)
        if imports or "is" in file_entry or "ff" in file_entry:
            import_candidates += 1
            if len(imports) == 0:
                importless_candidates += 1

        # Track max entropy across all files in the report.
        metrics = file_metrics(file_entry)
        binary_metrics = metrics.get("binary") or {}
        ent = _float(binary_metrics.get("overall_entropy", 0.0))
        if ent > 0:
            entropies.append(ent)
        max_entropy = max(max_entropy, ent)
        file_summary = _summarize_findings(file_entry.get("ts") or [])
        if file_summary.suspicious_finding_count > 0:
            suspicious_files += 1
        if file_summary.hostile_finding_count > 0:
            hostile_files += 1
            if fmt:
                try:
                    hostile_mtimes.append(datetime.fromisoformat(str(fmt).replace(" ", "T")).timestamp())
                except (ValueError, TypeError):
                    pass
            if file_entry.get("p"):
                hostile_files_with_parent += 1
        
        if ent > 0 and file_entry.get("type", "") in {"javascript", "python", "pe", "elf", "macho"}:
            code_entropies.append(ent)

    # Stealth potential: high entropy (packed/encrypted) but very few findings.
    stealth_potential = 1.0 if (filtered_finding_count < 5 and max_entropy > 6.5) else 0.0

    _assign(vec, lookup.get("struct:tiny_executable"), 1.0 if any_tiny_binary else 0.0)
    _assign(vec, lookup.get("struct:no_imports"), 1.0 if (import_candidates > 0 and importless_candidates == import_candidates) else 0.0)
    _assign(vec, lookup.get("struct:zero_findings"), 1.0 if filtered_finding_count == 0 else 0.0)
    _assign(vec, lookup.get("struct:finding_count_log"), math.log1p(filtered_finding_count))
    _assign(vec, lookup.get("struct:file_count_log"), math.log1p(len(files)))
    _assign(vec, lookup.get("struct:inner_file_count_log"), math.log1p(max(len(files) - 1, 0)))
    _assign(vec, lookup.get("struct:stealth_potential"), stealth_potential)
    
    if include_file_risk_coverage:
        file_count = max(len(files), 1)
        _assign(vec, lookup.get("struct:suspicious_file_fraction"), suspicious_files / file_count)
        _assign(vec, lookup.get("struct:hostile_file_fraction"), hostile_files / file_count)
        _assign(vec, lookup.get("struct:suspicious_file_count_log"), math.log1p(suspicious_files))
        _assign(vec, lookup.get("struct:hostile_file_count_log"), math.log1p(hostile_files))

    # Group 15: Packaged capability (Experiment 25).
    # packaged_capability: distinct capability paths × max binary entropy.
    # Content-based interpretation: "how many distinct capability slots does
    # this sample touch, weighted by how packed the binary is". Selected after
    # a 5-way ablation (zero / chars / tokens / paths / findings — see
    # EXPERIMENTS.md 2026-04-10). Mode is overridable via env var for
    # future experiments but defaults to `paths`.
    _pc_mode = os.getenv("COLLIMATOR_PACKAGED_CAPABILITY_MODE", "paths").strip().lower()
    if _pc_mode == "zero" or _pc_mode == "none":
        _pc_value = 0.0
    elif _pc_mode == "chars":
        _pc_value = float(len({c for c in formula if c.isalpha()})) * max_entropy
    elif _pc_mode == "tokens":
        import re as _re
        _pc_value = float(len(set(_re.findall(r"[A-Z][a-z]?", formula)))) * max_entropy
    elif _pc_mode == "findings" and summary is not None:
        _pc_value = float(
            summary.unique_notable_ids
            + summary.unique_suspicious_ids
            + summary.unique_hostile_ids
        ) * max_entropy
    else:  # "paths" (default)
        _pc_value = float(len(summary.sample_paths)) * max_entropy if summary is not None else 0.0
    _assign(vec, lookup.get("struct:packaged_capability"), _pc_value)

    # Group 17: Mtime anomalies (Experiment 30).
    # Inconsistency in timestamps often signals tampering.
    if len(mtimes) > 1:
        m_arr = np.array(mtimes)
        _assign(vec, lookup.get("struct:mtime_range_hours"), float(np.max(m_arr) - np.min(m_arr)) / 3600.0)
        _assign(vec, lookup.get("struct:mtime_std_dev_hours"), float(np.std(m_arr)) / 3600.0)
    else:
        _assign(vec, lookup.get("struct:mtime_range_hours"), 0.0)
        _assign(vec, lookup.get("struct:mtime_std_dev_hours"), 0.0)

    # Group 18: Structural Depth and Entropy Gradients (Exp 36).
    _assign(vec, lookup.get("struct:max_nesting_depth_log"), math.log1p(max_nesting_depth))
    _assign(vec, lookup.get("struct:inner_file_ratio"), float(inner_file_count) / max(len(files), 1))
    if len(entropies) > 1:
        e_arr = np.array(entropies)
        _assign(vec, lookup.get("struct:entropy_std_dev"), float(np.std(e_arr)))
        _assign(vec, lookup.get("struct:entropy_max_diff"), float(np.max(e_arr) - np.mean(e_arr)))
    else:
        _assign(vec, lookup.get("struct:entropy_std_dev"), 0.0)
        _assign(vec, lookup.get("struct:entropy_max_diff"), 0.0)
    
    # Exp 43: Silent Packer Signal
    if os.getenv("COLLIMATOR_SILENT_PACKER_SIGNAL") == "1":
        total_size = sum(_float(f.get("sz", 0)) for f in files)
        size_mb = total_size / (1024 * 1024)
        _assign(vec, lookup.get("struct:silent_packer_signal"), math.log1p(size_mb) / (filtered_finding_count + 1))

    # Exp 44: Mtime Kurtosis
    if os.getenv("COLLIMATOR_MTIME_KURTOSIS") == "1":
        if len(mtimes) > 3:
            _assign(vec, lookup.get("struct:mtime_kurtosis"), float(stats.kurtosis(mtimes)))
        else:
            _assign(vec, lookup.get("struct:mtime_kurtosis"), 0.0)

    # Exp 46: Behavioral Air-Gap
    if os.getenv("COLLIMATOR_AIR_GAP_SIGNAL") == "1":
        # If we have hostile files, but NONE of them have parents, it's an air-gap.
        val = 1.0 if (hostile_files > 0 and hostile_files_with_parent == 0) else 0.0
        _assign(vec, lookup.get("struct:air_gap_signal"), val)

    # Extreme features (Exps 48, 49, 54, 55, 56) — each individually toggleable.
    config = feature_config_from_env()
    if config.include_anachronistic_injection:
        # Exp 48: Anachronistic Injection
        if mtimes and hostile_mtimes:
            median_mtime = float(np.median(mtimes))
            max_delta = max(abs(t - median_mtime) for t in hostile_mtimes)
            _assign(vec, lookup.get("struct:anachronistic_injection"), max_delta / 3600.0)
        else:
            _assign(vec, lookup.get("struct:anachronistic_injection"), 0.0)

    if config.include_code_entropy_spike:
        # Exp 49: Code Entropy Spike
        if code_entropies:
            avg_ent = float(np.mean(entropies)) if entropies else 0.0
            max_code_ent = max(code_entropies)
            _assign(vec, lookup.get("struct:code_entropy_spike"), max_code_ent - avg_ent)
        else:
            _assign(vec, lookup.get("struct:code_entropy_spike"), 0.0)

    if config.include_foreign_binary_signal:
        # Exp 54: Foreign Binary Signal
        _assign(vec, lookup.get("struct:foreign_binary_signal"), 1.0 if has_foreign_binaries else 0.0)

    if config.include_extension_mismatch_signal:
        # Exp 55: Extension Mismatch Signal
        _assign(vec, lookup.get("struct:extension_mismatch_signal"), float(extension_mismatches))

    if config.include_hostile_finding_density:
        # Exp 56: Hostile Density Signal — findings per 1000 lines of code
        if total_loc > 0:
            _assign(vec, lookup.get("struct:hostile_finding_density"), (hostile_files * 1000.0) / total_loc)
        else:
            _assign(vec, lookup.get("struct:hostile_finding_density"), 0.0)


def _apply_neg_space_features(
    files: list[dict[str, Any]],
    sample_paths: dict[str, int],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 23: negative space / missing expected behavior."""
    file_types = {f.get("type", "") for f in files}
    for ftype, traits in sorted(EXPECTED_GHOSTS.items()):
        has_type = ftype in file_types
        for trait in traits:
            # If the type is present but the trait is missing, it's a "ghost".
            val = 1.0 if (has_type and (trait not in sample_paths or sample_paths[trait] < 1)) else 0.0
            _assign(vec, ctx.absolute_lookup.get(f"missing:{ftype}*{trait}"), val)


def _truncate_path(base: str, depth: int) -> str:
    """Truncate a finding path to at most `depth` directory segments.

    If depth <= 0, returns the full base path (no truncation).
    "objectives/supply-chain/hidden-payload/staging" at depth=2 → "objectives/supply-chain"
    """
    if depth <= 0:
        return base
    parts = base.split("/")
    return "/".join(parts[:depth])


def _ngram_paths_for_file(
    file_entry: dict[str, Any],
    depth: int,
    min_crit: int = 0,
) -> list[str]:
    """Collect the unique (optionally truncated) finding paths for one file.

    depth=0 → full base paths; depth=2/3 → truncated to that many segments.
    min_crit=0 → all findings; 3 → notable+; 4 → suspicious+; etc.
    Shared by bigram, trigram, and unsigned-bigram generation.
    """
    file_traits: set[str] = set()
    for finding in file_entry.get("ts") or []:
        fid = finding.get("i", "")
        if not fid:
            continue
        if _float(finding.get("c", 1.0)) < MIN_CONFIDENCE:
            continue
        if min_crit > 0 and finding.get("l", 0) < min_crit:
            continue
        file_traits.add(fid)
    return sorted({_truncate_path(fid.split("::")[0], depth) for fid in file_traits})


def _apply_bigram_features(
    report: dict[str, Any],
    ctx: _ExtractContext,
    vec: np.ndarray,
    summary: "_FindingSummary | None" = None,
) -> None:
    """Group 11: trait bigram multi-hot features."""
    config = feature_config_from_env()
    use_conf = config.include_confidence_weighted_ngrams and summary is not None
    vocab_paths = ctx.bigram_vocab_paths
    lookup = ctx.bigram_lookup_pair
    for file_entry in report_files(report):
        paths_list = _ngram_paths_for_file(file_entry, config.ngram_path_depth, config.ngram_min_crit)
        paths_list = [p for p in paths_list if p in vocab_paths]
        if use_conf:
            path_conf = summary.path_confidences
            for i, p1 in enumerate(paths_list):
                c1 = path_conf.get(p1, 1.0)
                for p2 in paths_list[i + 1 :]:
                    idx = lookup.get((p1, p2))
                    if idx is not None:
                        vec[idx] = (c1 + path_conf.get(p2, 1.0)) / 2.0
        else:
            for i, p1 in enumerate(paths_list):
                for p2 in paths_list[i + 1 :]:
                    idx = lookup.get((p1, p2))
                    if idx is not None:
                        vec[idx] = 1.0


def _apply_tiered_bigram_features(
    summary: "_FindingSummary",
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Report-level severity-prefixed notable+ trait bigrams."""
    config = feature_config_from_env()
    tokens = _tiered_bigram_tokens(
        summary.sample_paths,
        depth=config.tiered_bigram_path_depth,
        min_crit=config.tiered_bigram_min_crit,
        branch_min_crit=_parse_branch_min_crit_overrides(config.tiered_bigram_branch_min_crit),
    )
    if len(tokens) > 512:
        log.warning("too many tiered bigram tokens (%d); skipping sample", len(tokens))
        return
    vocab_tokens = ctx.tiered_bigram_vocab_tokens
    tokens = [t for t in tokens if t in vocab_tokens]
    tiered_lookup = ctx.tiered_bigram_lookup
    for i, t1 in enumerate(tokens):
        for t2 in tokens[i + 1:]:
            _assign(vec, tiered_lookup.get(f"{t1} + {t2}"), 1.0)


def _apply_tiered_trigram_features(
    summary: "_FindingSummary",
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Report-level severity-prefixed notable+ trait trigrams."""
    config = feature_config_from_env()
    tokens = _tiered_bigram_tokens(
        summary.sample_paths,
        depth=config.tiered_trigram_path_depth,
        min_crit=config.tiered_trigram_min_crit,
    )
    if len(tokens) > 512:
        log.warning("too many tiered trigram tokens (%d); skipping sample", len(tokens))
        return
    vocab_tokens = ctx.tiered_trigram_vocab_tokens
    tokens = [t for t in tokens if t in vocab_tokens]
    tiered_lookup = ctx.tiered_trigram_lookup
    for i, t1 in enumerate(tokens):
        for j in range(i + 1, len(tokens)):
            t2 = tokens[j]
            for t3 in tokens[j + 1:]:
                _assign(vec, tiered_lookup.get(f"{t1} + {t2} + {t3}"), 1.0)


def _apply_tiered_quadgram_features(
    summary: "_FindingSummary",
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Batch 3: report-level severity-prefixed quadgrams (one order up from trigrams).

    Tighter token cap than trigrams (64 vs 512) because C(n, 4) grows much
    faster — 64 tokens = 635k quadgrams; 128 = 10.5M.
    """
    config = feature_config_from_env()
    tokens = _tiered_bigram_tokens(
        summary.sample_paths,
        depth=config.tiered_quadgram_path_depth,
        min_crit=config.tiered_quadgram_min_crit,
    )
    if len(tokens) > 64:
        log.warning("too many tiered quadgram tokens (%d); skipping sample", len(tokens))
        return
    vocab_tokens = ctx.tiered_quadgram_vocab_tokens
    tokens = [t for t in tokens if t in vocab_tokens]
    absolute_lookup = ctx.absolute_lookup
    for quad in _quadgram_tokens(tokens):
        _assign(vec, absolute_lookup.get(f"tierquad:{quad}"), 1.0)


def _apply_ghost_features(
    sample_paths: dict[str, int],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 12: ghost features (absence of expected benign behavior)."""
    for path in ctx.ghost_vocab:
        # 1.0 if the expected benign path is MISSING.
        if path not in sample_paths or sample_paths[path] < 2:
            _assign(vec, ctx.ghost_lookup.get(path), 1.0)


def _apply_skeleton_features(
    formula: str,
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 13: skeleton categorical and filetype interactions."""
    skeleton = "".join([c for c in formula if c.isalpha()])
    if not skeleton:
        return

    _assign(vec, ctx.skeleton_lookup.get(skeleton), 1.0)

    # Interaction features with filetype.
    for file_entry in files:
        ft = file_entry.get("type", "")
        _assign(vec, ctx.skeleton_interaction_lookup.get((ft, skeleton)), 1.0)


def _apply_rare_element_features(
    elements: str,
    summary: _FindingSummary,
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 14: rare element multi-hot features (smoking guns)."""
    config = feature_config_from_env()
    weight = 1.0
    if config.include_soft_presence and summary.finding_confidences:
        weight = float(np.mean(summary.finding_confidences))

    if elements:
        for el in elements.split(","):
            el = el.strip()
            _assign(vec, ctx.rare_element_lookup.get(el), weight)


def _apply_trigram_features(
    report: dict[str, Any],
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 16: trait trigram multi-hot features."""
    config = feature_config_from_env()
    vocab_paths = ctx.trigram_vocab_paths
    lookup = ctx.trigram_lookup_triple
    for file_entry in report_files(report):
        paths_list = _ngram_paths_for_file(file_entry, config.ngram_path_depth, config.ngram_min_crit)
        paths_list = [p for p in paths_list if p in vocab_paths]
        for i, p1 in enumerate(paths_list):
            for j in range(i + 1, len(paths_list)):
                p2 = paths_list[j]
                for p3 in paths_list[j + 1 :]:
                    idx = lookup.get((p1, p2, p3))
                    if idx is not None:
                        vec[idx] = 1.0


def _apply_logic_gap_features(
    files: list[dict[str, Any]],
    summary: _FindingSummary,
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 19: logic gap features (imports present without behavior)."""
    # Collect all unique imports across the report.
    all_imports: set[str] = set()
    for file_entry in files:
        all_imports.update(_file_symbols(file_entry))

    sample_paths = summary.sample_paths
    for cat, (imports_set, traits_set) in sorted(LOGIC_GAPS.items()):
        has_import = any(imp in all_imports for imp in imports_set)
        has_behavior = any(
            any(path.startswith(t) for t in traits_set)
            for path, max_ord in sample_paths.items()
            if max_ord >= 3  # notable or above
        )
        if has_import and not has_behavior:
            _assign(vec, ctx.absolute_lookup.get(f"gap:{cat}"), 1.0)


def _apply_signature_synergy_features(
    report: dict[str, Any],
    summary: _FindingSummary,
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 20: signature synergy (unsigned + behavioral patterns)."""
    is_unsigned = "metadata/unsigned" in summary.sample_paths
    if not is_unsigned:
        return

    config = feature_config_from_env()
    vocab_paths = ctx.synergy_vocab_paths
    lookup = ctx.synergy_lookup_pair
    for file_entry in report_files(report):
        paths_list = _ngram_paths_for_file(file_entry, config.ngram_path_depth, config.ngram_min_crit)
        paths_list = [p for p in paths_list if p in vocab_paths]
        for i, p1 in enumerate(paths_list):
            for p2 in paths_list[i + 1 :]:
                idx = lookup.get((p1, p2))
                if idx is not None:
                    vec[idx] = 1.0


def _apply_intent_gap_features(
    summary: _FindingSummary,
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 22: package intent gaps (risky behavior without documentation)."""
    has_doc = "metadata/package/documentation" in summary.sample_paths
    has_help = "metadata/package/help" in summary.sample_paths
    intent_signal = has_doc or has_help

    # Define risky behaviors that should normally be documented.
    risky_behaviors = {
        "network": ["objectives/network", "micro-behaviors/network"],
        "filesystem": ["objectives/persistence", "micro-behaviors/filesystem"],
        "execution": ["objectives/execution", "micro-behaviors/process/create"],
        "crypto": ["objectives/crypto", "micro-behaviors/crypto"],
    }

    for cat, traits in sorted(risky_behaviors.items()):
        has_behavior = any(
            any(path.startswith(t) for t in traits)
            for path, max_ord in summary.sample_paths.items()
            if max_ord >= 4  # suspicious or above
        )
        # Gap exists if they have the behavior but NO documentation/help intent.
        if has_behavior and not intent_signal:
            _assign(vec, ctx.absolute_lookup.get(f"intent_gap:{cat}"), 1.0)


def _apply_cluster_features(
    cluster_id: int,
    ctx: _ExtractContext,
    vec: np.ndarray,
) -> None:
    """Group 21: semantic intent cluster features."""
    if 0 <= cluster_id < 50:
        _assign(vec, ctx.absolute_lookup.get(f"cluster:{cluster_id}"), 1.0)


def _extract_into(
    report: dict[str, Any],
    ctx: _ExtractContext,
    vec: np.ndarray,
    formula: str = "",
    elements: str = "",
    score: int = 0,
    mtime: str = "",
    cluster_id: int = -1,
) -> None:
    """Extract features from a report into a pre-allocated vector."""
    config = feature_config_from_env()
    files = report_files(report)
    if not files:
        files = [{}]
    summary = _summarize_report_files(files)
    metrics = _merge_metric_values(files)

    if "present" in config.enabled_groups:
        _apply_presence_features(
            summary, ctx, vec,
            score=score if config.include_score_weighted_traits else 0,
        )
    if "maxcrit" in config.enabled_groups:
        _apply_maxcrit_features(
            summary, ctx, vec,
            score=score if config.include_score_weighted_traits else 0,
        )
    if "agg" in config.enabled_groups:
        # Exp 51: hostile_depth_weight calculation
        hostile_depth_weight = 0.0
        if config.include_hostile_depth_weight:
            depths: dict[str, int] = {}
            for file_entry in files:
                fpath = file_entry.get("path", "")
                parent = file_entry.get("p", "")
                depths[fpath] = depths.get(parent, 0) + 1 if parent else 0

            for file_entry in files:
                fpath = file_entry.get("path", "")
                depth = depths.get(fpath, 0)
                file_summary = _summarize_findings(file_entry.get("ts") or [])
                hostile_depth_weight += file_summary.hostile_finding_count * depth

        _apply_aggregate_features(
            summary,
            files,
            ctx,
            vec,
            config.top_k_risk_files,
            config.include_suspicious_breadth_density,
            config.include_hostile_escalation_features,
            config.include_hostile_weighted_density,
            config.include_repetition_penalty_features,
            config.include_file_severity_distribution,
            top_k_risk_files_min_crit=config.top_k_risk_files_min_crit,
        )
        if config.include_hostile_depth_weight:
            _assign(vec, ctx.absolute_lookup.get("agg:hostile_depth_weight"), hostile_depth_weight)

    if "ext" in config.enabled_groups:
        _apply_external_signal_features(summary, ctx, vec)
    if "metrics" in config.enabled_groups:
        _apply_metric_features(metrics, files, ctx, vec)
    if "symbols" in config.enabled_groups and config.include_symbol_vocab:
        _apply_symbol_vocab_features(files, ctx, vec)
    if "symbols" in config.enabled_groups and config.include_symbol_bigrams:
        _apply_symbol_bigram_features(files, ctx, vec)
    if "symbols" in config.enabled_groups and config.include_symbol_trigrams:
        _apply_symbol_trigram_features(files, ctx, vec)
    # Batch 4: MBC ID unigram vocab. Lives in the `agg` group since attack
    # features (its closest sibling) live there too.
    if "agg" in config.enabled_groups and config.include_mbc_id_vocab:
        _apply_mbc_id_features(files, ctx, vec)
    if "kv" in config.enabled_groups and config.include_kv_vocab:
        _apply_kv_vocab_features(files, ctx, vec)
    if "textenc" in config.enabled_groups and config.include_text_encoding_features:
        _apply_text_encoding_features(files, ctx, vec)
    if "filetype" in config.enabled_groups:
        _apply_filetype_features(files, ctx, vec)
    if "format" in config.enabled_groups and config.include_format_hints:
        _apply_format_hint_features(files, ctx, vec)
    if "struct" in config.enabled_groups:
        _apply_structural_features(
            files,
            summary.filtered_finding_count,
            ctx,
            vec,
            config.include_struct_file_risk_coverage,
            mtime_str=mtime,
            formula=formula,
            summary=summary,
        )
    if "elements" in config.enabled_groups:
        _apply_element_features(elements, files, ctx, vec)
    if "formula" in config.enabled_groups:
        _apply_formula_features(formula, summary.filtered_finding_count, ctx, vec)
    if "score" in config.enabled_groups:
        total_size = sum(_float(f.get("sz", 0)) for f in files)
        _apply_score_features(score, total_size, files, ctx, vec)

    if "bigrams" in config.enabled_groups:
        _apply_bigram_features(report, ctx, vec, summary=summary)

    if (
        "tiered_bigrams" in config.enabled_groups
        and config.include_tiered_crit_bigrams
    ):
        _apply_tiered_bigram_features(summary, ctx, vec)

    if (
        "tiered_trigrams" in config.enabled_groups
        and config.include_tiered_crit_trigrams
    ):
        _apply_tiered_trigram_features(summary, ctx, vec)

    if (
        "tiered_trigrams" in config.enabled_groups
        and config.include_tiered_crit_quadgrams
    ):
        _apply_tiered_quadgram_features(summary, ctx, vec)

    if "ghosts" in config.enabled_groups:
        _apply_ghost_features(summary.sample_paths, ctx, vec)

    if "skeletons" in config.enabled_groups:
        _apply_skeleton_features(formula, files, ctx, vec)

    if "rares" in config.enabled_groups:
        _apply_rare_element_features(elements, summary, ctx, vec)

    if "trigrams" in config.enabled_groups:
        _apply_trigram_features(report, ctx, vec)

    if "logic_gaps" in config.enabled_groups:
        _apply_logic_gap_features(files, summary, ctx, vec)

    if "signature_synergy" in config.enabled_groups:
        _apply_signature_synergy_features(report, summary, ctx, vec)

    if "clusters" in config.enabled_groups:
        _apply_cluster_features(cluster_id, ctx, vec)

    if "intent_gaps" in config.enabled_groups:
        _apply_intent_gap_features(summary, ctx, vec)

    if "neg_space" in config.enabled_groups:
        _apply_neg_space_features(files, summary.sample_paths, ctx, vec)

    # Experimental feature batch + ATT&CK + targeted n-grams.
    if any((config.include_attack_features,
            config.include_objective_trigrams, config.include_suspicious_trigrams,
            config.include_attack_ngrams,
            config.exp_import_categories, config.exp_suspicious_api_combo,
            config.exp_confidence_skew, config.exp_finding_depth_var,
            config.exp_multifile_crit_spread, config.exp_metric_anomaly,
            config.exp_unsigned_import_density, config.exp_entropy_hostile,
            config.exp_hostile_objective_div, config.exp_import_finding_ratio,
            config.include_ember_lite_features,
            config.include_trait_confidence_moments,
            config.include_trait_id_lexical_distance,
            config.include_document_obfuscation_features)):
        _apply_experimental_features(report, summary, files, metrics, ctx, vec, score)

    # ATT&CK/MBC code n-grams: vocab-based features from T-codes and MBC B-codes.
    if config.include_attack_code_ngrams:
        atk_codes: set[str] = set()
        mbc_codes: set[str] = set()
        for file_entry in files:
            for finding in file_entry.get("ts") or []:
                a = finding.get("a")
                if a:
                    atk_codes.add(a)
                m = finding.get("m")
                if m:
                    mbc_codes.add(m)
        lookup = ctx.absolute_lookup
        sorted_a = sorted(atk_codes)
        for i, a1 in enumerate(sorted_a):
            for j in range(i + 1, len(sorted_a)):
                a2 = sorted_a[j]
                _assign(vec, lookup.get(f"atkbi:{a1} + {a2}"), 1.0)
                for a3 in sorted_a[j + 1:]:
                    _assign(vec, lookup.get(f"atktri:{a1} + {a2} + {a3}"), 1.0)
        sorted_m = sorted(mbc_codes)
        for i, m1 in enumerate(sorted_m):
            for j in range(i + 1, len(sorted_m)):
                m2 = sorted_m[j]
                _assign(vec, lookup.get(f"mbcbi:{m1} + {m2}"), 1.0)
                for m3 in sorted_m[j + 1:]:
                    _assign(vec, lookup.get(f"mbctri:{m1} + {m2} + {m3}"), 1.0)

    # Crit-category n-grams: vocab-based features from crit:category tokens.
    if config.include_crit_category_ngrams:
        tokens = _crit_category_tokens(summary.sample_paths)
        lookup = ctx.absolute_lookup
        for t in tokens:
            _assign(vec, lookup.get(f"crit:{t}"), 1.0)
        for i, t1 in enumerate(tokens):
            for t2 in tokens[i + 1:]:
                _assign(vec, lookup.get(f"critbi:{t1} + {t2}"), 1.0)
            for j in range(i + 1, len(tokens)):
                t2 = tokens[j]
                for t3 in tokens[j + 1:]:
                    _assign(vec, lookup.get(f"crittri:{t1} + {t2} + {t3}"), 1.0)


# ---------------------------------------------------------------------------
# Parallel worker functions (module-level for multiprocessing pickling)
# ---------------------------------------------------------------------------

def _coerce_report(report: dict[str, Any] | str) -> dict[str, Any] | None:
    """Return a parsed report dict from either a dict or raw JSON string."""
    if isinstance(report, str):
        try:
            parsed = json.loads(report)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return report


def _vocab_batch_worker(
    items: list[dict[str, Any] | str],
) -> tuple[dict[str, int], list[str], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int]]:
    """Count path, element, bigram, and skeleton occurrences for a batch. CPU-only."""
    presence_counts: dict[str, int] = {}
    filetypes: list[str] = []
    element_counts: dict[str, int] = {}
    bigram_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}

    for item in items:
        if isinstance(item, dict) and "cleave_result" in item:
            raw_report = item["cleave_result"]
            elements_str = item.get("elements", "")
            formula = item.get("formula", "")
        else:
            raw_report = item
            elements_str = ""
            formula = ""

        if formula:
            skeleton = "".join([c for c in formula if c.isalpha()])
            if skeleton:
                skeleton_counts[skeleton] = skeleton_counts.get(skeleton, 0) + 1

        report = _coerce_report(raw_report)
        if report is None:
            continue

        if elements_str:
            for el in elements_str.split(","):
                el = el.strip()
                if el:
                    element_counts[el] = element_counts.get(el, 0) + 1

        sample_paths: dict[str, int] = {}
        for file_entry in report_files(report):
            ftype = file_entry.get("type", "")
            if ftype:
                filetypes.append(ftype)

            file_traits: set[str] = set()
            for finding in file_entry.get("ts") or []:
                fid = finding.get("i", "")
                if not fid:
                    continue
                if _float(finding.get("c", 1.0)) < MIN_CONFIDENCE:
                    continue
                crit_ord = finding.get("l", 0)
                file_traits.add(fid)
                for path in _finding_paths(fid):
                    if crit_ord > sample_paths.get(path, -1):
                        sample_paths[path] = crit_ord

            # Collect co-occurring path pairs (bigrams) within each file.
            # Uses shared helper that respects NGRAM_PATH_DEPTH and NGRAM_MIN_CRIT.
            config = feature_config_from_env()
            paths_list = _ngram_paths_for_file(file_entry, config.ngram_path_depth, config.ngram_min_crit)
            for i, p1 in enumerate(paths_list):
                for p2 in paths_list[i + 1 :]:
                    # Hard cap at 50,000 unique bigrams per worker batch to prevent
                    # the 1.3M+ feature explosion while still finding frequent ones.
                    if len(bigram_counts) < 50000:
                        bigram = f"{p1} + {p2}"
                        bigram_counts[bigram] = bigram_counts.get(bigram, 0) + 1

        for path, max_ord in sample_paths.items():
            if max_ord >= 2:
                presence_counts[path] = presence_counts.get(path, 0) + 1
    return presence_counts, filetypes, element_counts, bigram_counts, {}, {}, skeleton_counts


def _vocab_db_batch_worker(
    args: tuple[Path | str, list[int]],
) -> tuple[dict[str, int], list[str], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int]]:
    """Fetch and count paths for a batch of IDs from the DB."""
    from . import data  # noqa: PLC0415 — deferred to avoid circular import in workers

    dsn, ids = args
    results = data.fetch_cleave_results(dsn, ids)
    return _vocab_batch_worker(list(results.values()))


def _extract_batch_worker(
    args: tuple[int, list[tuple[dict[str, Any] | str, int]], FeatureSpec],
) -> tuple[list[int], list[int], list[float], list[int]]:
    """Extract features from a batch of (item, label) pairs. CPU-only."""
    offset, batch, spec = args
    ctx = _ExtractContext(spec)
    vec = np.zeros(spec.total_features, dtype=np.float32)
    rows: list[int] = []
    cols: list[int] = []
    vals: list[float] = []
    labels: list[int] = []
    for i, (item, label) in enumerate(batch):
        if isinstance(item, dict) and "cleave_result" in item:
            raw_report = item["cleave_result"]
            formula = item.get("formula", "")
            elements = item.get("elements", "")
            score = item.get("score", 0)
            mtime = item.get("mtime", "")
            cluster_id = item.get("cluster_id", -1)
        else:
            raw_report = item
            formula, elements, score, mtime, cluster_id = "", "", 0, "", -1

        report = _coerce_report(raw_report)
        if report is None:
            continue
        vec[:] = 0.0
        _extract_into(report, ctx, vec, formula=formula, elements=elements, score=score, mtime=mtime, cluster_id=cluster_id)
        nz = np.nonzero(vec)[0]
        rows.extend([offset + i] * len(nz))
        cols.extend(nz.tolist())
        vals.extend(vec[nz].tolist())
        labels.append(label)
    return rows, cols, vals, labels


def _n_workers_default() -> int:
    """Choose the default parallelism level for feature extraction."""
    cpu_count = _physical_cpu_count() or os.cpu_count()
    return max(1, cpu_count or 1)


def _physical_cpu_count() -> int | None:
    try:
        out = subprocess.check_output(
            ["lscpu", "-p=Core,Socket"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    cores = {
        tuple(line.split(",", 1))
        for line in out.splitlines()
        if line and not line.startswith("#") and "," in line
    }
    return len(cores) or None


def _feature_batch_size(n_workers: int) -> int:
    """Pick a batch size that amortises IPC overhead without huge tail latency."""
    # Small batches create tens of thousands of tasks on full-corpus runs, and
    # most of the time is spent serialising JSON between processes. Larger
    # batches materially reduce scheduling and pickling overhead.
    return min(512, max(128, 4096 // max(n_workers, 1)))


def resolve_worker_count(n_workers: int) -> int:
    """Resolve a requested worker count to the effective process count."""
    return n_workers if n_workers > 0 else _n_workers_default()


def _batched(items: Iterable[T], batch_size: int) -> Iterable[list[T]]:
    """Yield lists of up to batch_size items from an iterable."""
    it = iter(items)
    while True:
        batch = list(islice(it, batch_size))
        if not batch:
            return
        yield batch


def _weighted_metadata_batches(
    items: list[LabeledMetadata],
    *,
    max_items: int,
    max_weight: int,
) -> Iterable[list[LabeledMetadata]]:
    """Yield metadata batches capped by row count and estimated JSON bytes."""
    if not items:
        return
    # Same shape detection as in extract_labeled_metadata_from_db_batches_unordered:
    # row[5] is json_bytes (int) on the with_size variant, canonical_sha256
    # (str) on the regular variant. isinstance gates the integer path.
    if max_weight <= 0 or not any(
        len(item) > 5 and isinstance(item[5], int) and item[5] > 0
        for item in items
    ):
        yield from _batched(items, max_items)
        return
    batch: list[LabeledMetadata] = []
    weight = 0
    for item in items:
        item_weight = int(item[5]) if len(item) > 5 and isinstance(item[5], int) else 0
        if batch and (len(batch) >= max_items or weight + item_weight > max_weight):
            yield batch
            batch = []
            weight = 0
        batch.append(item)
        weight += item_weight
    if batch:
        yield batch


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def canonical_fields_from_report(report: dict[str, Any]) -> tuple[str, str, int]:
    """Extract (formula, elements, score) from a cleave report's depth-0 file.

    Mirrors hopper's parseCleaveFile (hopper.go:160). The depth-0 entry in
    ``fs`` is the top-level analyzed file; for archives, deeper entries are
    inner files. ``samples.formula``, ``samples.elements``, and
    ``samples.score`` columns are all populated from this file by hopper.

    Returns ("", "", 0) if no depth-0 file is found.
    """
    files = report.get("fs") or []
    for f in files:
        if not isinstance(f, dict):
            continue
        if int(f.get("dp") or 0) == 0:
            formula = str(f.get("f") or "")
            # Strip Unicode subscript digits ₀-₉ to match hopper.stripSubscripts.
            elements = "".join(c for c in formula if not ("₀" <= c <= "₉"))
            score = int(f.get("x") or 0)
            return formula, elements, score
    return "", "", 0


def extract(report: dict[str, Any], spec: FeatureSpec) -> np.ndarray:
    """Extract a feature vector from a single cleave AnalysisReport.

    Pulls ``formula``, ``elements``, and ``score`` from the depth-0 file in
    the report so that live-scoring (e.g. ``make scan``, litmus) produces the
    same feature values as training (where these come from DB columns
    populated by hopper from the same source).
    """
    vec = np.zeros(spec.total_features, dtype=np.float32)
    formula, elements, score = canonical_fields_from_report(report)
    _extract_into(
        report,
        _ExtractContext(spec),
        vec,
        formula=formula,
        elements=elements,
        score=score,
    )
    return vec


def extract_all(
    reports: list[dict[str, Any]],
    labels: list[int],
    spec: FeatureSpec,
    n_workers: int = 0,
) -> tuple[sp.csr_matrix, np.ndarray]:
    """Extract feature vectors for all samples as a sparse CSR matrix."""
    return extract_stream(zip(reports, labels), spec, n_workers=n_workers)


def extract_stream_batches(
    report_labels: Iterable[tuple[dict[str, Any] | str, int]],
    spec: FeatureSpec,
    *,
    n_workers: int = 0,
    batch_size: int | None = None,
) -> Iterator[tuple[sp.csr_matrix, np.ndarray]]:
    """Yield extracted feature matrices batch-by-batch using one worker pool.

    This is the high-throughput path for large inference jobs: it reuses a
    single ProcessPoolExecutor across the full stream instead of rebuilding the
    pool for each caller-defined scoring batch.
    """
    nw = resolve_worker_count(n_workers)
    eff_batch_size = batch_size if batch_size is not None and batch_size > 0 else _feature_batch_size(nw)
    batch_iter = (
        (0, batch, spec)
        for _offset, batch in _enumerate_batches(report_labels, eff_batch_size)
    )

    def _to_matrix(
        result: tuple[list[int], list[int], list[float], list[int]],
    ) -> tuple[sp.csr_matrix, np.ndarray]:
        rows, cols, vals, labels = result
        n = len(labels)
        y = np.array(labels, dtype=np.float32)
        X = sp.csr_matrix(
            (np.array(vals, dtype=np.float32),
             (np.array(rows, dtype=np.int32), np.array(cols, dtype=np.int32))),
            shape=(n, spec.total_features),
        )
        log.debug(
            "extracted %d samples x %d features (nnz=%d, density=%.1f%%)",
            n, spec.total_features, X.nnz,
            100.0 * X.nnz / max(n * spec.total_features, 1),
        )
        return X, y

    if nw > 1:
        with ProcessPoolExecutor(
            max_workers=nw,
            mp_context=mp.get_context("spawn"),
        ) as pool:
            for result in _bounded_iter(pool, _extract_batch_worker, batch_iter, max_inflight=2 * nw):
                yield _to_matrix(result)
        return

    for args in batch_iter:
        yield _to_matrix(_extract_batch_worker(args))


def extract_stream(
    report_labels: Iterable[tuple[dict[str, Any] | str, int]],
    spec: FeatureSpec,
    n_workers: int = 0,
) -> tuple[sp.csr_matrix, np.ndarray]:
    """Extract features by streaming (report, label) pairs.

    Each report's features are extracted into sparse COO entries.
    When n_workers > 1 (or auto-detected > 1) and the dataset is large
    enough, extraction is parallelised across CPU workers.  Falls back
    to sequential on any failure.
    """
    nw = resolve_worker_count(n_workers)
    rows: list[int] = []
    cols: list[int] = []
    vals: list[float] = []
    labels: list[int] = []
    batch_size = _feature_batch_size(nw)

    def _consume(batch_iter: Iterable[tuple[list[int], list[int], list[float], list[int]]]) -> None:
        for b_rows, b_cols, b_vals, b_labels in batch_iter:
            rows.extend(b_rows)
            cols.extend(b_cols)
            vals.extend(b_vals)
            labels.extend(b_labels)

    batch_args = (
        (offset, batch, spec)
        for offset, batch in _enumerate_batches(report_labels, batch_size)
    )

    if nw > 1:
        with ProcessPoolExecutor(
            max_workers=nw,
            mp_context=mp.get_context("spawn"),
        ) as pool:
            _consume(_bounded_iter(pool, _extract_batch_worker, batch_args, max_inflight=2 * nw))

    if nw <= 1:
        _consume(map(_extract_batch_worker, batch_args))

    n = len(labels)

    y = np.array(labels, dtype=np.float32)
    X = sp.csr_matrix(
        (np.array(vals, dtype=np.float32),
         (np.array(rows, dtype=np.int32), np.array(cols, dtype=np.int32))),
        shape=(n, spec.total_features),
    )
    log.debug(
        "extracted %d samples x %d features (nnz=%d, density=%.1f%%)",
        n, spec.total_features, X.nnz,
        100.0 * X.nnz / max(n * spec.total_features, 1),
    )
    return X, y


def _enumerate_batches(
    items: Iterable[T],
    batch_size: int,
) -> Iterable[tuple[int, list[T]]]:
    """Yield (row_offset, batch) pairs for a stream."""
    offset = 0
    for batch in _batched(items, batch_size):
        yield offset, batch
        offset += len(batch)


def _bounded_iter(pool: ProcessPoolExecutor, fn, it: Iterable, *, max_inflight: int) -> Iterator:
    """Submit tasks to pool with bounded concurrency, yielding results in order.

    Unlike pool.map(), which eagerly submits all tasks before any results are
    consumed, this keeps at most max_inflight tasks in flight at once. This
    bounds the amount of pickled task data queued in the IPC pipe and the
    number of raw-JSON strings materialised in the main process simultaneously.
    """
    pending: collections.deque = collections.deque()
    source = iter(it)
    for item in islice(source, max_inflight):
        pending.append(pool.submit(fn, item))
    while pending:
        yield pending.popleft().result()
        try:
            pending.append(pool.submit(fn, next(source)))
        except StopIteration:
            pass


def _bounded_unordered_iter(pool: ProcessPoolExecutor, fn, it: Iterable, *, max_inflight: int) -> Iterator:
    """Submit tasks with bounded concurrency, yielding results as they complete."""
    pending = set()
    source = iter(it)
    for item in islice(source, max_inflight):
        pending.add(pool.submit(fn, item))
    while pending:
        for future in as_completed(pending):
            pending.remove(future)
            yield future.result()
            try:
                pending.add(pool.submit(fn, next(source)))
            except StopIteration:
                pass
            break


def _extract_partitioned_batch_worker(
    args: tuple[int, int, list[tuple[dict[str, Any] | str, int, bool]], FeatureSpec],
) -> tuple[
    list[int], list[int], list[float], list[int],
    list[int], list[int], list[float], list[int],
]:
    """Extract train/test features from a mixed batch into separate sparse rows."""
    train_offset, test_offset, batch, spec = args
    ctx = _ExtractContext(spec)
    vec = np.zeros(spec.total_features, dtype=np.float32)

    train_rows: list[int] = []
    train_cols: list[int] = []
    train_vals: list[float] = []
    train_labels: list[int] = []

    test_rows: list[int] = []
    test_cols: list[int] = []
    test_vals: list[float] = []
    test_labels: list[int] = []

    local_train = 0
    local_test = 0

    for item, label, is_test in batch:
        if isinstance(item, dict) and "cleave_result" in item:
            raw_report = item["cleave_result"]
            formula = item.get("formula", "")
            elements = item.get("elements", "")
            score = item.get("score", 0)
            mtime = item.get("mtime", "")
            cluster_id = item.get("cluster_id", -1)
        else:
            raw_report = item
            formula, elements, score, mtime, cluster_id = "", "", 0, "", -1

        report = _coerce_report(raw_report)
        if report is None:
            continue
        vec[:] = 0.0
        _extract_into(report, ctx, vec, formula=formula, elements=elements, score=score, mtime=mtime, cluster_id=cluster_id)
        nz = np.nonzero(vec)[0]
        if is_test:
            row = test_offset + local_test
            local_test += 1
            test_rows.extend([row] * len(nz))
            test_cols.extend(nz.tolist())
            test_vals.extend(vec[nz].tolist())
            test_labels.append(label)
        else:
            row = train_offset + local_train
            local_train += 1
            train_rows.extend([row] * len(nz))
            train_cols.extend(nz.tolist())
            train_vals.extend(vec[nz].tolist())
            train_labels.append(label)

    return (
        train_rows, train_cols, train_vals, train_labels,
        test_rows, test_cols, test_vals, test_labels,
    )


def _extract_partitioned_db_batch_worker(
    args: tuple[int, int, Path | str, list[tuple[int, int, bool]], FeatureSpec],
) -> tuple[
    list[int], list[int], list[float], list[int],
    list[int], list[int], list[float], list[int],
]:
    """Fetch and extract train/test features for a batch of IDs from the DB."""
    from . import data  # noqa: PLC0415 — deferred to avoid circular import in workers

    train_offset, test_offset, dsn, batch_ids, spec = args
    ids = [rid for rid, _l, _t in batch_ids]
    reports_map = data.fetch_cleave_results(dsn, ids)

    batch = [
        (reports_map[rid], label, is_test)
        for rid, label, is_test in batch_ids
        if rid in reports_map
    ]
    return _extract_partitioned_batch_worker((train_offset, test_offset, batch, spec))


def _extract_labeled_db_batch_worker(
    args: tuple[int, Path | str, list[tuple[int, int]], FeatureSpec],
) -> tuple[list[int], list[int], list[float], list[int]]:
    """Fetch and extract one labeled batch from the DB."""
    from . import data  # noqa: PLC0415 — deferred to avoid circular import in workers

    offset, dsn, batch_ids, spec = args
    ids = [rid for rid, _label in batch_ids]
    reports_map = data.fetch_cleave_results(dsn, ids)
    missing = set(ids) - set(reports_map)
    if missing:
        raise ValueError(f"missing cleave_result rows during extraction: {len(missing)}")
    batch = [(reports_map[rid], label) for rid, label in batch_ids]
    return _extract_batch_worker((offset, batch, spec))


def _extract_labeled_metadata_db_batch_worker(
    args: tuple[Path | str, list[LabeledMetadata], FeatureSpec],
) -> tuple[
    list[LabeledMetadata],
    list[int],
    list[int],
    list[float],
    list[int],
    dict[str, float | int],
]:
    """Fetch and extract one labeled metadata batch from the DB."""
    from . import data  # noqa: PLC0415 — deferred to avoid circular import in workers

    dsn, batch_meta, spec = args
    ids = [int(row[0]) for row in batch_meta]
    fetch_started = time.monotonic()
    reports_map = data.fetch_cleave_results(dsn, ids)
    fetch_sec = time.monotonic() - fetch_started
    missing = set(ids) - set(reports_map)
    if missing:
        raise ValueError(f"missing cleave_result rows during extraction: {len(missing)}")
    batch = [
        (reports_map[int(row[0])], int(row[4]))
        for row in batch_meta
    ]
    extract_started = time.monotonic()
    rows, cols, vals, labels = _extract_batch_worker((0, batch, spec))
    extract_sec = time.monotonic() - extract_started
    stats: dict[str, float | int] = {
        "rows": len(labels),
        "fetch_sec": fetch_sec,
        "extract_sec": extract_sec,
        "min_row_id": min(ids) if ids else 0,
        "max_row_id": max(ids) if ids else 0,
    }
    return batch_meta, rows, cols, vals, labels, stats


def extract_labeled_from_db_batches(
    db_path: Path | str,
    row_ids_labels: list[tuple[int, int]],
    spec: FeatureSpec,
    *,
    n_workers: int = 0,
    batch_size: int | None = None,
) -> Iterator[tuple[sp.csr_matrix, np.ndarray]]:
    """Yield feature batches for labeled DB row IDs.

    Workers fetch raw JSON directly from the DB, avoiding a single parent
    process parsing and pickling every report before feature extraction.
    """
    nw = resolve_worker_count(n_workers)
    eff_batch_size = batch_size if batch_size is not None and batch_size > 0 else max(
        _feature_batch_size(nw),
        1024,
    )
    log.info(
        "DB-backed feature extraction: %d rows, %d workers, batch_size=%d",
        len(row_ids_labels),
        nw,
        eff_batch_size,
    )
    batch_args = (
        (0, db_path, batch, spec)
        for batch in _batched(row_ids_labels, eff_batch_size)
    )

    def _to_matrix(
        result: tuple[list[int], list[int], list[float], list[int]],
    ) -> tuple[sp.csr_matrix, np.ndarray]:
        rows, cols, vals, labels = result
        n = len(labels)
        y = np.array(labels, dtype=np.float32)
        X = sp.csr_matrix(
            (
                np.array(vals, dtype=np.float32),
                (np.array(rows, dtype=np.int32), np.array(cols, dtype=np.int32)),
            ),
            shape=(n, spec.total_features),
        )
        log.debug(
            "extracted %d samples x %d features (nnz=%d, density=%.1f%%)",
            n,
            spec.total_features,
            X.nnz,
            100.0 * X.nnz / max(n * spec.total_features, 1),
        )
        return X, y

    if nw > 1:
        with ProcessPoolExecutor(
            max_workers=nw,
            mp_context=mp.get_context("spawn"),
        ) as pool:
            for result in _bounded_iter(
                pool,
                _extract_labeled_db_batch_worker,
                batch_args,
                max_inflight=nw,
            ):
                yield _to_matrix(result)
        return

    for args in batch_args:
        yield _to_matrix(_extract_labeled_db_batch_worker(args))


def extract_labeled_metadata_from_db_batches_unordered(
    db_path: Path | str,
    row_metadata: list[LabeledMetadata],
    spec: FeatureSpec,
    *,
    n_workers: int = 0,
    batch_size: int | None = None,
) -> Iterator[tuple[list[LabeledMetadata], sp.csr_matrix, np.ndarray, dict[str, float | int]]]:
    """Yield DB-backed feature batches with metadata as workers complete.

    This is intended for full-corpus threshold/FP cache construction, where
    global row order is not meaningful as long as metadata, labels, and
    predictions stay aligned within each yielded batch.
    """
    nw = resolve_worker_count(n_workers)
    eff_batch_size = batch_size if batch_size is not None and batch_size > 0 else _feature_batch_size(nw)
    max_batch_bytes = int(os.getenv("COLLIMATOR_THRESHOLD_BATCH_BYTES", str(16 * 1024 * 1024)))
    # Size-aware batching is enabled iff a row carries an int json_bytes
    # at index 5. Tuple shapes:
    #   stream_labeled_metadata_full           -> 6-tuple, row[5] is canonical_sha256 (str)
    #   stream_labeled_metadata_full_with_size -> 7-tuple, row[5] is json_bytes (int), row[6] is canonical_sha256
    sized = any(
        len(row) > 5 and isinstance(row[5], int) and row[5] > 0
        for row in row_metadata
    )
    log.info(
        "unordered DB-backed feature extraction: %d rows, %d workers, batch_size=%d%s",
        len(row_metadata),
        nw,
        eff_batch_size,
        f", max_batch_bytes={max_batch_bytes}" if sized else "",
    )
    batch_args = (
        (db_path, batch, spec)
        for batch in _weighted_metadata_batches(
            row_metadata,
            max_items=eff_batch_size,
            max_weight=max_batch_bytes,
        )
    )

    def _to_matrix(
        result: tuple[
            list[LabeledMetadata],
            list[int],
            list[int],
            list[float],
            list[int],
            dict[str, float | int],
        ],
    ) -> tuple[list[LabeledMetadata], sp.csr_matrix, np.ndarray, dict[str, float | int]]:
        metadata, rows, cols, vals, labels, stats = result
        n = len(labels)
        y = np.array(labels, dtype=np.float32)
        matrix_started = time.monotonic()
        X = sp.csr_matrix(
            (
                np.array(vals, dtype=np.float32),
                (np.array(rows, dtype=np.int32), np.array(cols, dtype=np.int32)),
            ),
            shape=(n, spec.total_features),
        )
        stats = dict(stats)
        stats["matrix_sec"] = time.monotonic() - matrix_started
        stats["nnz"] = X.nnz
        log.debug(
            "extracted %d samples x %d features (nnz=%d, density=%.1f%%)",
            n,
            spec.total_features,
            X.nnz,
            100.0 * X.nnz / max(n * spec.total_features, 1),
        )
        return metadata, X, y, stats

    if nw > 1:
        with ProcessPoolExecutor(
            max_workers=nw,
            mp_context=mp.get_context("spawn"),
        ) as pool:
            for result in _bounded_unordered_iter(
                pool,
                _extract_labeled_metadata_db_batch_worker,
                batch_args,
                max_inflight=2 * nw,
            ):
                yield _to_matrix(result)
        return

    for args in batch_args:
        yield _to_matrix(_extract_labeled_metadata_db_batch_worker(args))


def _enumerate_partitioned_batches(
    items: Iterable[tuple[T, int, bool]],
    batch_size: int,
) -> Iterable[tuple[int, int, list[tuple[T, int, bool]]]]:
    """Yield (train_offset, test_offset, batch) for a mixed train/test stream."""
    train_offset = 0
    test_offset = 0
    for batch in _batched(items, batch_size):
        yield train_offset, test_offset, batch
        batch_train = sum(1 for _item, _label, is_test in batch if not is_test)
        train_offset += batch_train
        test_offset += len(batch) - batch_train


def _vocab_labeled_db_batch_worker(
    args: tuple[Path | str, list[tuple[int, int]]],
) -> tuple[dict[str, int], list[str], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int]]:
    """Fetch and count paths for a batch of IDs with labels."""
    from . import data  # noqa: PLC0415

    dsn, ids_labels = args
    ids = [rid for rid, _l in ids_labels]
    reports_map = data.fetch_cleave_results(dsn, ids)

    presence_counts: dict[str, int] = {}
    filetypes: list[str] = []
    element_counts: dict[str, int] = {}
    bigram_counts: dict[str, int] = {}
    benign_presence: dict[str, int] = {}
    malware_presence: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    benign_elements: dict[str, int] = {}
    malware_elements: dict[str, int] = {}
    trigram_counts: dict[str, int] = {}
    benign_trigrams: dict[str, int] = {}
    tiered_bigram_counts: dict[str, int] = {}
    tiered_trigram_counts: dict[str, int] = {}

    benign_ids = {rid for rid, label in ids_labels if label == 0}

    for rid, item in reports_map.items():
        raw_report = item["cleave_result"]
        elements_str = item.get("elements", "")
        formula = item.get("formula", "")
        report = _coerce_report(raw_report)
        if report is None:
            continue

        if formula:
            skeleton = "".join([c for c in formula if c.isalpha()])
            if skeleton:
                skeleton_counts[skeleton] = skeleton_counts.get(skeleton, 0) + 1

        if elements_str:
            for el in elements_str.split(","):
                el = el.strip()
                if el:
                    element_counts[el] = element_counts.get(el, 0) + 1
                    if rid in benign_ids:
                        benign_elements[el] = benign_elements.get(el, 0) + 1
                    else:
                        malware_elements[el] = malware_elements.get(el, 0) + 1

        sample_paths: dict[str, int] = {}
        for file_entry in report_files(report):
            ftype = file_entry.get("type", "")
            if ftype:
                filetypes.append(ftype)

            file_traits: set[str] = set()
            for finding in file_entry.get("ts") or []:
                fid = finding.get("i", "")
                if not fid or _float(finding.get("c", 1.0)) < MIN_CONFIDENCE:
                    continue
                crit_ord = finding.get("l", 0)
                file_traits.add(fid)
                for path in _finding_paths(fid):
                    if crit_ord > sample_paths.get(path, -1):
                        sample_paths[path] = crit_ord

            # Uses shared helper for n-gram paths (respects NGRAM_PATH_DEPTH + NGRAM_MIN_CRIT).
            config = feature_config_from_env()
            paths_list = _ngram_paths_for_file(file_entry, config.ngram_path_depth, config.ngram_min_crit)
            for i, p1 in enumerate(paths_list):
                for p2 in paths_list[i + 1 :]:
                    # Hard cap at 100,000 unique bigrams per worker batch.
                    if len(bigram_counts) < 100000:
                        bigram = f"{p1} + {p2}"
                        bigram_counts[bigram] = bigram_counts.get(bigram, 0) + 1

                for j in range(i + 1, len(paths_list)):
                    p2 = paths_list[j]
                    for p3 in paths_list[j + 1 :]:
                        # Hard cap at 50,000 unique trigrams per worker batch.
                        if len(trigram_counts) < 50000:
                            trigram = f"{p1} + {p2} + {p3}"
                            trigram_counts[trigram] = trigram_counts.get(trigram, 0) + 1
                            if rid in benign_ids:
                                benign_trigrams[trigram] = benign_trigrams.get(trigram, 0) + 1

        for path, max_ord in sample_paths.items():
            if max_ord >= 2:
                presence_counts[path] = presence_counts.get(path, 0) + 1
                if rid in benign_ids:
                    benign_presence[path] = benign_presence.get(path, 0) + 1
                else:
                    malware_presence[path] = malware_presence.get(path, 0) + 1

        config = feature_config_from_env()
        if config.include_tiered_crit_bigrams:
            tokens = _tiered_bigram_tokens(
                sample_paths,
                depth=config.tiered_bigram_path_depth,
                min_crit=config.tiered_bigram_min_crit,
            )
            if len(tokens) <= 512:
                for i, t1 in enumerate(tokens):
                    for t2 in tokens[i + 1:]:
                        if len(tiered_bigram_counts) < 100000:
                            bigram = f"{t1} + {t2}"
                            tiered_bigram_counts[bigram] = tiered_bigram_counts.get(bigram, 0) + 1
        if config.include_tiered_crit_trigrams:
            tokens = _tiered_bigram_tokens(
                sample_paths,
                depth=config.tiered_trigram_path_depth,
                min_crit=config.tiered_trigram_min_crit,
            )
            if len(tokens) <= 512:
                for i, t1 in enumerate(tokens):
                    for j in range(i + 1, len(tokens)):
                        t2 = tokens[j]
                        for t3 in tokens[j + 1:]:
                            if len(tiered_trigram_counts) < 100000:
                                trigram = f"{t1} + {t2} + {t3}"
                                tiered_trigram_counts[trigram] = tiered_trigram_counts.get(trigram, 0) + 1

    return (
        presence_counts, filetypes, element_counts, bigram_counts,
        benign_presence, malware_presence, skeleton_counts,
        benign_elements, malware_elements, trigram_counts, benign_trigrams,
        tiered_bigram_counts, tiered_trigram_counts,
    )


def build_vocab_from_db(
    db_path: Path | str,
    row_ids_labels: list[tuple[int, int]],
    n_workers: int = 0,
) -> FeatureSpec:
    """Scan sampled reports in the DB to build a feature vocabulary."""
    config = feature_config_from_env()
    nw = resolve_worker_count(n_workers)
    presence_counts: dict[str, int] = {}
    filetypes: set[str] = set()
    element_counts: dict[str, int] = {}
    bigram_counts: dict[str, int] = {}
    benign_presence: dict[str, int] = {}
    malware_presence: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    benign_elements: dict[str, int] = {}
    malware_elements: dict[str, int] = {}
    trigram_counts: dict[str, int] = {}
    benign_trigrams: dict[str, int] = {}
    tiered_bigram_counts: dict[str, int] = {}
    tiered_trigram_counts: dict[str, int] = {}
    batch_size = _feature_batch_size(nw)

    benign_total = sum(1 for _rid, label in row_ids_labels if label == 0)
    malware_total = len(row_ids_labels) - benign_total

    def _merge_batch(
        counts: dict[str, int],
        fts: list[str],
        el_counts: dict[str, int],
        bi_counts: dict[str, int],
        b_pres: dict[str, int],
        m_pres: dict[str, int],
        sk_counts: dict[str, int],
        b_els: dict[str, int],
        m_els: dict[str, int],
        tri_counts: dict[str, int],
        b_tris: dict[str, int],
        tier_bi_counts: dict[str, int],
        tier_tri_counts: dict[str, int],
    ) -> None:
        for k, v in counts.items():
            presence_counts[k] = presence_counts.get(k, 0) + v
        filetypes.update(fts)
        for k, v in el_counts.items():
            element_counts[k] = element_counts.get(k, 0) + v
        for k, v in bi_counts.items():
            bigram_counts[k] = bigram_counts.get(k, 0) + v
        for k, v in b_pres.items():
            benign_presence[k] = benign_presence.get(k, 0) + v
        for k, v in m_pres.items():
            malware_presence[k] = malware_presence.get(k, 0) + v
        for k, v in sk_counts.items():
            skeleton_counts[k] = skeleton_counts.get(k, 0) + v
        for k, v in b_els.items():
            benign_elements[k] = benign_elements.get(k, 0) + v
        for k, v in m_els.items():
            malware_elements[k] = malware_elements.get(k, 0) + v
        for k, v in tri_counts.items():
            trigram_counts[k] = trigram_counts.get(k, 0) + v
        for k, v in b_tris.items():
            benign_trigrams[k] = benign_trigrams.get(k, 0) + v
        for k, v in tier_bi_counts.items():
            tiered_bigram_counts[k] = tiered_bigram_counts.get(k, 0) + v
        for k, v in tier_tri_counts.items():
            tiered_trigram_counts[k] = tiered_trigram_counts.get(k, 0) + v

    batch_args = ((db_path, batch) for batch in _batched(row_ids_labels, batch_size))

    if nw > 1:
        with ProcessPoolExecutor(
            max_workers=nw,
            mp_context=mp.get_context("spawn"),
        ) as pool:
            for res in _bounded_iter(
                pool, _vocab_labeled_db_batch_worker, batch_args,
                max_inflight=2 * nw,
            ):
                _merge_batch(*res)
    else:
        for res in map(_vocab_labeled_db_batch_worker, batch_args):
            _merge_batch(*res)

    presence_vocab = sorted(k for k, c in presence_counts.items() if c >= MIN_PATH_FREQ)
    filetype_vocab = sorted(filetypes)
    element_vocab = sorted(k for k, c in element_counts.items() if c >= MIN_PATH_FREQ)
    # Bigram/trigram vocab sizes are controlled by FeatureConfig (which reads
    # from env vars) so they're included in the matrix cache key.
    bigram_vocab = sorted(k for k, c in bigram_counts.items() if c >= config.bigram_min_freq)[:config.bigram_max]
    skeleton_vocab = sorted(k for k, c in skeleton_counts.items() if c >= 100)

    # Trigrams: malware-enriched triplets, top N by frequency. Min-freq cutoff
    # is configurable (Batch 3 symmetry fix); previous hardcoded `>= 5`.
    trigram_benign_ceil = int(config.trigram_max_benign_frac * benign_total) if config.trigram_max_benign_frac > 0 else 0
    malware_only_trigrams = sorted(
        [(k, c) for k, c in trigram_counts.items()
         if benign_trigrams.get(k, 0) <= trigram_benign_ceil and c >= config.trigram_min_freq],
        key=lambda x: x[1],
        reverse=True,
    )[:config.trigram_max]
    trigram_vocab = sorted(k for k, c in malware_only_trigrams)
    tiered_bigram_vocab: list[str] = []
    if config.include_tiered_crit_bigrams:
        tiered_bigram_vocab = sorted(
            k for k, c in sorted(tiered_bigram_counts.items(), key=lambda x: -x[1])[:config.tiered_bigram_max]
            if c >= config.tiered_bigram_min_freq
        )
        log.info("tiered crit bigrams: %d vocab entries", len(tiered_bigram_vocab))
    tiered_trigram_vocab: list[str] = []
    if config.include_tiered_crit_trigrams:
        tiered_trigram_vocab = sorted(
            k for k, c in sorted(tiered_trigram_counts.items(), key=lambda x: -x[1])[:config.tiered_trigram_max]
            if c >= config.tiered_trigram_min_freq
        )
        log.info("tiered crit trigrams: %d vocab entries", len(tiered_trigram_vocab))

    # Rare Elements: highly specific to malware (e.g. 0% benign, >= 5 malware samples).
    rare_element_vocab = sorted([
        el for el, m_count in malware_elements.items()
        if m_count >= 5 and benign_elements.get(el, 0) == 0
    ])

    # Ghosts: common in benign (>=2%) but rare in malware (<0.5%).
    ghost_vocab = sorted([
        path for path, b_count in benign_presence.items()
        if b_count >= 0.02 * benign_total and malware_presence.get(path, 0) < 0.005 * malware_total
    ])

    # Extended metrics vocabulary: scan a sample of reports for all numeric
    # ms.* keys that appear in ≥5% of training data. Quick single-pass scan
    # (reuses the same DB connection pattern as vocab workers).
    metric_vocab: list[str] = []
    if config.include_extended_metrics:
        from . import data as _data  # noqa: PLC0415
        metric_key_counts: dict[str, int] = {}
        # Scan a random subset for speed (5000 rows is enough to find common keys).
        scan_ids = [rid for rid, _l in row_ids_labels[:5000]]
        for start in range(0, len(scan_ids), 500):
            chunk = scan_ids[start:start + 500]
            for _rid, item in _data.fetch_cleave_results(db_path, chunk).items():
                report = _coerce_report(item["cleave_result"])
                if report is None:
                    continue
                for file_entry in report_files(report):
                    ms = file_metrics(file_entry)
                    for group, fields in ms.items():
                        if not isinstance(fields, dict):
                            continue
                        for k, v in fields.items():
                            if isinstance(v, (int, float)):
                                mk = f"{group}_{k}"
                                metric_key_counts[mk] = metric_key_counts.get(mk, 0) + 1
        # Keep keys appearing above a frequency threshold. Exclude keys already in KEY_METRICS.
        # Default 5%; override via COLLIMATOR_METRIC_MIN_FREQ_PCT for experiments.
        # When `extended_metrics_include` is set, restrict to keys matching one of
        # those prefixes (e.g. `pe_timestamp,binary_overlay`) — lets autocollie
        # isolate the effect of newly-added metric families instead of toggling
        # every numeric ms.* field at once.
        base_keys = {f"{g}_{f}" for g, f, _ in KEY_METRICS}
        metric_pct = float(os.getenv("COLLIMATOR_METRIC_MIN_FREQ_PCT", "5")) / 100
        threshold = max(len(scan_ids) * metric_pct, 10)
        prefixes = config.extended_metrics_include
        metric_vocab = sorted(
            k for k, c in metric_key_counts.items()
            if c >= threshold
            and k not in base_keys
            and (not prefixes or any(k.startswith(p) for p in prefixes))
        )
        log.info("extended metrics: %d keys from %d scanned rows%s",
                 len(metric_vocab), len(scan_ids),
                 f" (filtered by prefixes: {','.join(prefixes)})" if prefixes else "")

    # Crit-category n-gram vocabulary: build from the same sample_paths
    # already computed by the vocab workers (stored in presence_counts).
    # Quick scan of training data to find common crit:category tokens.
    crit_unigram_vocab: list[str] = []
    crit_bigram_vocab: list[str] = []
    crit_trigram_vocab: list[str] = []
    if config.include_crit_category_ngrams:
        from . import data as _data  # noqa: PLC0415
        crit_uni_counts: dict[str, int] = {}
        crit_bi_counts: dict[str, int] = {}
        crit_tri_counts: dict[str, int] = {}
        crit_bi_benign: dict[str, int] = {}
        crit_tri_benign: dict[str, int] = {}
        scan_ids_labels = row_ids_labels[:5000]
        benign_scan_ids = {rid for rid, label in scan_ids_labels if label == 0}
        for start in range(0, len(scan_ids_labels), 500):
            chunk_ids = [rid for rid, _l in scan_ids_labels[start:start + 500]]
            for rid, item in _data.fetch_cleave_results(db_path, chunk_ids).items():
                report = _coerce_report(item["cleave_result"])
                if report is None:
                    continue
                # Build sample_paths from all findings
                sp: dict[str, int] = {}
                for fe in report_files(report):
                    for finding in fe.get("ts") or []:
                        fid = finding.get("i", "")
                        if not fid or _float(finding.get("c", 1.0)) < MIN_CONFIDENCE:
                            continue
                        for path in _finding_paths(fid):
                            crit_ord = finding.get("l", 0)
                            if crit_ord > sp.get(path, -1):
                                sp[path] = crit_ord
                tokens = _crit_category_tokens(sp)
                is_benign = rid in benign_scan_ids
                for t in tokens:
                    crit_uni_counts[t] = crit_uni_counts.get(t, 0) + 1
                for i, t1 in enumerate(tokens):
                    for t2 in tokens[i + 1:]:
                        bi = f"{t1} + {t2}"
                        crit_bi_counts[bi] = crit_bi_counts.get(bi, 0) + 1
                        if is_benign:
                            crit_bi_benign[bi] = crit_bi_benign.get(bi, 0) + 1
                    for j in range(i + 1, len(tokens)):
                        t2 = tokens[j]
                        for t3 in tokens[j + 1:]:
                            tri = f"{t1} + {t2} + {t3}"
                            crit_tri_counts[tri] = crit_tri_counts.get(tri, 0) + 1
                            if is_benign:
                                crit_tri_benign[tri] = crit_tri_benign.get(tri, 0) + 1

        n_scan = len(scan_ids_labels)
        benign_frac = 0.01  # allow ≤1% benign
        n_benign_scan = len(benign_scan_ids)
        benign_ceil = int(benign_frac * n_benign_scan)

        crit_unigram_vocab = sorted(k for k, c in crit_uni_counts.items() if c >= 10)
        crit_bigram_vocab = sorted(
            k for k, c in sorted(crit_bi_counts.items(), key=lambda x: -x[1])[:500]
            if c >= 5 and crit_bi_benign.get(k, 0) <= benign_ceil
        )
        crit_trigram_vocab = sorted(
            k for k, c in sorted(crit_tri_counts.items(), key=lambda x: -x[1])[:500]
            if c >= 3 and crit_tri_benign.get(k, 0) <= benign_ceil
        )
        log.info(
            "crit-category n-grams: %d unigrams, %d bigrams, %d trigrams from %d scanned rows",
            len(crit_unigram_vocab), len(crit_bigram_vocab), len(crit_trigram_vocab), n_scan,
        )

    # ATT&CK/MBC code n-gram vocabulary: bigrams/trigrams from T-codes and MBC B-codes.
    # MBC unigram vocab (Batch 4) is built in the same scan when its knob is on.
    attack_bigram_vocab: list[str] = []
    attack_trigram_vocab: list[str] = []
    mbc_bigram_vocab: list[str] = []
    mbc_trigram_vocab: list[str] = []
    mbc_id_vocab: list[str] = []
    needs_attack_scan = config.include_attack_code_ngrams or config.include_mbc_id_vocab
    if needs_attack_scan:
        from . import data as _data  # noqa: PLC0415
        atk_bi_counts: dict[str, int] = {}
        atk_tri_counts: dict[str, int] = {}
        mbc_bi_counts: dict[str, int] = {}
        mbc_tri_counts: dict[str, int] = {}
        mbc_unigram_counts: dict[str, int] = {}
        atk_bi_benign: dict[str, int] = {}
        mbc_bi_benign: dict[str, int] = {}
        scan_ids_labels = row_ids_labels[:5000]
        benign_scan = {rid for rid, label in scan_ids_labels if label == 0}
        for start in range(0, len(scan_ids_labels), 500):
            chunk_ids = [rid for rid, _l in scan_ids_labels[start:start + 500]]
            for rid, item in _data.fetch_cleave_results(db_path, chunk_ids).items():
                report = _coerce_report(item["cleave_result"])
                if report is None:
                    continue
                is_benign = rid in benign_scan
                attacks: set[str] = set()
                mbcs: set[str] = set()
                for fe in report_files(report):
                    for finding in fe.get("ts") or []:
                        a = finding.get("a")
                        if a:
                            attacks.add(a)
                        m = finding.get("m")
                        if m:
                            mbcs.add(m)
                if config.include_mbc_id_vocab:
                    for mid in mbcs:
                        mbc_unigram_counts[mid] = mbc_unigram_counts.get(mid, 0) + 1
                if not config.include_attack_code_ngrams:
                    continue
                # ATT&CK bigrams/trigrams
                sorted_a = sorted(attacks)
                for i, a1 in enumerate(sorted_a):
                    for j in range(i + 1, len(sorted_a)):
                        a2 = sorted_a[j]
                        bi = f"{a1} + {a2}"
                        atk_bi_counts[bi] = atk_bi_counts.get(bi, 0) + 1
                        if is_benign:
                            atk_bi_benign[bi] = atk_bi_benign.get(bi, 0) + 1
                        for a3 in sorted_a[j + 1:]:
                            tri = f"{a1} + {a2} + {a3}"
                            atk_tri_counts[tri] = atk_tri_counts.get(tri, 0) + 1
                # MBC bigrams/trigrams
                sorted_m = sorted(mbcs)
                for i, m1 in enumerate(sorted_m):
                    for j in range(i + 1, len(sorted_m)):
                        m2 = sorted_m[j]
                        bi = f"{m1} + {m2}"
                        mbc_bi_counts[bi] = mbc_bi_counts.get(bi, 0) + 1
                        if is_benign:
                            mbc_bi_benign[bi] = mbc_bi_benign.get(bi, 0) + 1
                        for m3 in sorted_m[j + 1:]:
                            tri = f"{m1} + {m2} + {m3}"
                            mbc_tri_counts[tri] = mbc_tri_counts.get(tri, 0) + 1

        n_benign_scan = len(benign_scan)
        benign_ceil = int(0.01 * n_benign_scan)
        if config.include_attack_code_ngrams:
            attack_bigram_vocab = sorted(
                k for k, c in sorted(atk_bi_counts.items(), key=lambda x: -x[1])[:500]
                if c >= 5 and atk_bi_benign.get(k, 0) <= benign_ceil
            )
            attack_trigram_vocab = sorted(
                k for k, c in sorted(atk_tri_counts.items(), key=lambda x: -x[1])[:500]
                if c >= 3
            )
            mbc_bigram_vocab = sorted(
                k for k, c in sorted(mbc_bi_counts.items(), key=lambda x: -x[1])[:500]
                if c >= 5 and mbc_bi_benign.get(k, 0) <= benign_ceil
            )
            mbc_trigram_vocab = sorted(
                k for k, c in sorted(mbc_tri_counts.items(), key=lambda x: -x[1])[:500]
                if c >= 3
            )
            log.info(
                "ATT&CK/MBC n-grams: %d/%d atk bi/tri, %d/%d mbc bi/tri from %d scanned rows",
                len(attack_bigram_vocab), len(attack_trigram_vocab),
                len(mbc_bigram_vocab), len(mbc_trigram_vocab), len(scan_ids_labels),
            )
        if config.include_mbc_id_vocab:
            # Min freq=5 mirrors the bigram floor; cap at 500 to keep vocab tight.
            mbc_id_vocab = sorted(
                k for k, c in sorted(mbc_unigram_counts.items(), key=lambda x: -x[1])[:500]
                if c >= 5
            )
            log.info("MBC unigram vocab: %d entries from %d scanned rows",
                     len(mbc_id_vocab), len(scan_ids_labels))

    symbol_vocab: list[str] = []
    symbol_bigram_vocab: list[str] = []
    symbol_trigram_vocab: list[str] = []
    tiered_quadgram_vocab: list[str] = []
    kv_vocab: list[str] = []
    needs_symbol_scan = (
        config.include_symbol_vocab
        or config.include_symbol_bigrams
        or config.include_symbol_trigrams
    )
    if needs_symbol_scan or config.include_kv_vocab or config.include_tiered_crit_quadgrams:
        from . import data as _data  # noqa: PLC0415
        symbol_counts: dict[str, int] = {}
        symbol_bigram_counts: dict[str, int] = {}
        symbol_trigram_counts: dict[str, int] = {}
        tiered_quadgram_counts: dict[str, int] = {}
        kv_counts: dict[str, int] = {}
        scan_ids = [rid for rid, _l in row_ids_labels[:5000]]
        for start in range(0, len(scan_ids), 500):
            chunk = scan_ids[start:start + 500]
            for _rid, item in _data.fetch_cleave_results(db_path, chunk).items():
                report = _coerce_report(item["cleave_result"])
                if report is None:
                    continue
                report_symbols: set[str] = set()
                report_symbol_bigrams: set[str] = set()
                report_symbol_trigrams: set[str] = set()
                report_kvs: set[str] = set()
                for file_entry in report_files(report):
                    if config.include_symbol_vocab:
                        report_symbols.update(_file_symbols(file_entry))
                    if config.include_symbol_bigrams:
                        report_symbol_bigrams.update(_file_symbol_bigrams(file_entry))
                    if config.include_symbol_trigrams:
                        report_symbol_trigrams.update(_file_symbol_trigrams(file_entry))
                    if config.include_kv_vocab:
                        report_kvs.update(
                            _metric_kv_tokens(
                                file_entry,
                                include_shape=config.include_kv_shape_features,
                                split_string_values=config.include_kv_value_split,
                            )
                        )
                if config.include_tiered_crit_quadgrams:
                    # Tiered quadgrams: one per report (not per file). Use the
                    # already-summarized sample_paths via _summarize_report_files.
                    quad_summary = _summarize_report_files(report_files(report))
                    tokens = _tiered_bigram_tokens(
                        quad_summary.sample_paths,
                        depth=config.tiered_quadgram_path_depth,
                        min_crit=config.tiered_quadgram_min_crit,
                    )
                    # Tighter cap than tiered_trigram (which uses 512) because
                    # C(n, 4) grows much faster: 64 tokens -> 635k quadgrams.
                    if len(tokens) <= 64:
                        for quad in _quadgram_tokens(tokens):
                            if len(tiered_quadgram_counts) >= 100000:
                                break
                            tiered_quadgram_counts[quad] = tiered_quadgram_counts.get(quad, 0) + 1
                for sym in report_symbols:
                    symbol_counts[sym] = symbol_counts.get(sym, 0) + 1
                for bi in report_symbol_bigrams:
                    symbol_bigram_counts[bi] = symbol_bigram_counts.get(bi, 0) + 1
                for tri in report_symbol_trigrams:
                    symbol_trigram_counts[tri] = symbol_trigram_counts.get(tri, 0) + 1
                for kv in report_kvs:
                    kv_counts[kv] = kv_counts.get(kv, 0) + 1
        if config.include_symbol_vocab:
            symbol_vocab = sorted(
                k for k, c in sorted(symbol_counts.items(), key=lambda x: -x[1])[:config.symbol_vocab_max]
                if c >= config.symbol_min_freq
            )
            log.info("symbol vocab: %d entries from %d scanned rows", len(symbol_vocab), len(scan_ids))
        if config.include_symbol_bigrams:
            symbol_bigram_vocab = sorted(
                k for k, c in sorted(symbol_bigram_counts.items(), key=lambda x: -x[1])[:config.symbol_bigram_max]
                if c >= config.symbol_min_freq_bigram
            )
            log.info("symbol bigram vocab: %d entries (cap=%d/file) from %d scanned rows",
                     len(symbol_bigram_vocab), _SYMBOL_BIGRAM_CAP, len(scan_ids))
        if config.include_symbol_trigrams:
            symbol_trigram_vocab = sorted(
                k for k, c in sorted(symbol_trigram_counts.items(), key=lambda x: -x[1])[:config.symbol_trigram_max]
                if c >= config.symbol_min_freq_trigram
            )
            log.info("symbol trigram vocab: %d entries (cap=%d/file) from %d scanned rows",
                     len(symbol_trigram_vocab), _SYMBOL_TRIGRAM_CAP, len(scan_ids))
        if config.include_kv_vocab:
            kv_vocab = sorted(
                k for k, c in sorted(kv_counts.items(), key=lambda x: -x[1])[:config.kv_vocab_max]
                if c >= config.kv_min_freq
            )
            log.info("kv vocab: %d entries from %d scanned rows", len(kv_vocab), len(scan_ids))
        if config.include_tiered_crit_quadgrams:
            tiered_quadgram_vocab = sorted(
                k for k, c in sorted(tiered_quadgram_counts.items(), key=lambda x: -x[1])[:config.tiered_quadgram_max]
                if c >= config.tiered_quadgram_min_freq
            )
            log.info("tiered crit quadgrams: %d vocab entries from %d scanned rows",
                     len(tiered_quadgram_vocab), len(scan_ids))

    feature_names = _build_feature_names(
        presence_vocab, filetype_vocab, element_vocab, bigram_vocab,
        ghost_vocab, skeleton_vocab, rare_element_vocab, trigram_vocab,
        metric_vocab, crit_unigram_vocab, crit_bigram_vocab, crit_trigram_vocab,
        attack_bigram_vocab, attack_trigram_vocab, mbc_bigram_vocab, mbc_trigram_vocab,
        tiered_bigram_vocab, tiered_trigram_vocab, tiered_quadgram_vocab,
        symbol_vocab, symbol_bigram_vocab, symbol_trigram_vocab, kv_vocab,
        mbc_id_vocab=mbc_id_vocab,
    )

    spec = FeatureSpec(
        presence_vocab=presence_vocab,
        filetype_vocab=filetype_vocab,
        element_vocab=element_vocab,
        bigram_vocab=bigram_vocab,
        ghost_vocab=ghost_vocab,
        skeleton_vocab=skeleton_vocab,
        rare_element_vocab=rare_element_vocab,
        trigram_vocab=trigram_vocab,
        metric_vocab=metric_vocab,
        crit_unigram_vocab=crit_unigram_vocab,
        crit_bigram_vocab=crit_bigram_vocab,
        crit_trigram_vocab=crit_trigram_vocab,
        attack_bigram_vocab=attack_bigram_vocab,
        attack_trigram_vocab=attack_trigram_vocab,
        mbc_bigram_vocab=mbc_bigram_vocab,
        mbc_trigram_vocab=mbc_trigram_vocab,
        tiered_bigram_vocab=tiered_bigram_vocab,
        tiered_trigram_vocab=tiered_trigram_vocab,
        tiered_quadgram_vocab=tiered_quadgram_vocab,
        symbol_vocab=symbol_vocab,
        symbol_bigram_vocab=symbol_bigram_vocab,
        symbol_trigram_vocab=symbol_trigram_vocab,
        kv_vocab=kv_vocab,
        mbc_id_vocab=mbc_id_vocab,
        feature_names=feature_names,
        total_features=len(feature_names),
    )
    log.info(
        "vocab: %d paths, %d filetypes, %d elements, %d bigrams, %d ghosts, %d ext_metrics -> %d features",
        len(presence_vocab), len(filetype_vocab), len(element_vocab), len(bigram_vocab),
        len(ghost_vocab), len(metric_vocab), spec.total_features,
    )
    return spec


def extract_partitioned_from_db(
    db_path: Path | str,
    train_ids_labels: list[tuple[int, int]],
    test_ids_labels: list[tuple[int, int]],
    spec: FeatureSpec,
    n_workers: int = 0,
) -> tuple[sp.csr_matrix, np.ndarray, sp.csr_matrix, np.ndarray]:
    """Extract train/test features using worker-local DB fetching."""
    nw = resolve_worker_count(n_workers)
    batch_size = _feature_batch_size(nw)

    # Combine all IDs into one mixed stream for partitioned extraction.
    mixed_ids = (
        [(rid, label, False) for rid, label in train_ids_labels] +
        [(rid, label, True) for rid, label in test_ids_labels]
    )
    # Sort to ensure predictable row assignment if needed (not strictly required for sparse).
    mixed_ids.sort(key=lambda x: x[0])

    # Accumulate COO components as compact numpy arrays rather than Python
    # lists to avoid ~7x per-element overhead (28-byte Python int vs 4-byte
    # int32). At full dataset scale (~1B non-zeros), this saves ~25 GB.
    train_row_chunks: list[np.ndarray] = []
    train_col_chunks: list[np.ndarray] = []
    train_val_chunks: list[np.ndarray] = []
    train_label_chunks: list[np.ndarray] = []
    test_row_chunks: list[np.ndarray] = []
    test_col_chunks: list[np.ndarray] = []
    test_val_chunks: list[np.ndarray] = []
    test_label_chunks: list[np.ndarray] = []

    def _consume(batch_iter):
        for (tr, tc, tv, tl, ter, tec, tev, tel) in batch_iter:
            if tr:
                train_row_chunks.append(np.array(tr, dtype=np.int32))
                train_col_chunks.append(np.array(tc, dtype=np.int32))
                train_val_chunks.append(np.array(tv, dtype=np.float32))
                train_label_chunks.append(np.array(tl, dtype=np.float32))
            if ter:
                test_row_chunks.append(np.array(ter, dtype=np.int32))
                test_col_chunks.append(np.array(tec, dtype=np.int32))
                test_val_chunks.append(np.array(tev, dtype=np.float32))
                test_label_chunks.append(np.array(tel, dtype=np.float32))

    batch_args = (
        (train_offset, test_offset, db_path, batch, spec)
        for train_offset, test_offset, batch in _enumerate_partitioned_batches(
            mixed_ids,
            batch_size,
        )
    )

    if nw > 1:
        with ProcessPoolExecutor(max_workers=nw, mp_context=mp.get_context("spawn")) as pool:
            _consume(_bounded_iter(pool, _extract_partitioned_db_batch_worker, batch_args, max_inflight=2 * nw))
    else:
        _consume(map(_extract_partitioned_db_batch_worker, batch_args))

    # Build final matrices from concatenated numpy chunks.
    def _concat(chunks: list[np.ndarray], dtype) -> np.ndarray:
        return np.concatenate(chunks).astype(dtype) if chunks else np.array([], dtype=dtype)

    n_train = int(sum(c.shape[0] for c in train_label_chunks)) if train_label_chunks else 0
    n_test = int(sum(c.shape[0] for c in test_label_chunks)) if test_label_chunks else 0
    X_train = sp.csr_matrix(
        (_concat(train_val_chunks, np.float32), (_concat(train_row_chunks, np.int32), _concat(train_col_chunks, np.int32))),
        shape=(n_train, spec.total_features),
    )
    y_train = _concat(train_label_chunks, np.float32)
    X_test = sp.csr_matrix(
        (_concat(test_val_chunks, np.float32), (_concat(test_row_chunks, np.int32), _concat(test_col_chunks, np.int32))),
        shape=(n_test, spec.total_features),
    )
    y_test = _concat(test_label_chunks, np.float32)

    return X_train, y_train, X_test, y_test


def standardize(X: np.ndarray | sp.spmatrix, spec: FeatureSpec) -> np.ndarray:
    """Apply z-score standardization using training statistics.

    Works on single vectors (1D) and batches (2D) via numpy broadcasting.
    Accepts sparse input (densifies it — call on small subsets only).
    Features that were constant during training (mean=0, std=1) are zeroed
    out to prevent catastrophic misclassification from unseen raw values.
    """
    if spec.feature_means is None or spec.feature_stds is None:
        return X.toarray() if sp.issparse(X) else X  # type: ignore[union-attr]
    means = np.array(spec.feature_means, dtype=np.float32)
    stds = np.array(spec.feature_stds, dtype=np.float32)
    dense = X.toarray() if sp.issparse(X) else X  # type: ignore[union-attr]
    result = (dense - means) / stds
    dead = (means == 0.0) & (stds == 1.0)
    result[..., dead] = 0.0
    return result


def feature_group_indices(spec: FeatureSpec) -> dict[str, list[int]]:
    """Return feature indices grouped by their prefix before ':'."""
    groups: dict[str, list[int]] = {group: [] for group in FEATURE_GROUPS}
    for i, name in enumerate(spec.feature_names):
        group = name.split(":", 1)[0]
        groups.setdefault(group, []).append(i)
    return groups


def drop_feature_prefixes(
    X: sp.spmatrix,
    spec: FeatureSpec,
    prefixes: Iterable[str],
) -> tuple[sp.csr_matrix, FeatureSpec]:
    """Return a matrix/spec with feature-name prefixes removed.

    Prefixes are matched against the part of a feature name before ``:``.
    Vocabularies are intentionally retained so extraction with the pruned spec
    remains compatible: dropped feature lookups simply do not resolve to an
    output column.
    """
    drop_prefixes = {prefix.strip().rstrip(":") for prefix in prefixes if prefix.strip()}
    if not drop_prefixes:
        return X.tocsr(), spec
    if X.shape[1] != spec.total_features:
        raise ValueError(f"matrix has {X.shape[1]} columns but spec has {spec.total_features} features")
    keep_indices = [
        idx for idx, name in enumerate(spec.feature_names)
        if name.split(":", 1)[0] not in drop_prefixes
    ]
    if len(keep_indices) == spec.total_features:
        return X.tocsr(), spec
    pruned_spec = replace(
        spec,
        feature_names=[spec.feature_names[idx] for idx in keep_indices],
        total_features=len(keep_indices),
        feature_means=None,
        feature_stds=None,
    )
    return X[:, keep_indices].tocsr(), pruned_spec
