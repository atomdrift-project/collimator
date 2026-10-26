"""Extract fixed-size numeric feature vectors from cleave v3 AnalysisReport JSON.

This module is intentionally one file. The ~30 ``_apply_*`` per-family
extractors share a layer of local helpers (``_crit_category_tokens``,
``_tiered_bigram_tokens``, ``_file_risk_stats``,
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

from .profiling import timed

import collections
import fcntl
import hashlib
import json
import logging
import math
import heapq
import multiprocessing as mp
import os
import re
import shutil
import subprocess
import time
import tempfile
from collections import defaultdict
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, ThreadPoolExecutor, wait
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path
from collections.abc import Callable, Iterable, Iterator
from itertools import combinations, islice
from multiprocessing.util import Finalize
from typing import Any, TypeVar
from datetime import datetime

import numpy as np
import scipy.sparse as sp
import scipy.stats as stats

from .memory import available_memory_gb, cgroup_headroom_gb
from .vocabulary import CountView, DiskTrigramCandidates, TrigramSource, VocabularyCounts

log = logging.getLogger(__name__)
_extract_trait_depth: ContextVar[int | None] = ContextVar("extract_trait_depth", default=None)
T = TypeVar("T")
LabeledMetadata = tuple[int, str, str, int, int] | tuple[int, str, str, int, int, int]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# v4: criticality is already an integer ordinal (0-5) in the JSON.
# 0=filtered, 1=component, 2=baseline, 3=notable, 4=suspicious, 5=hostile

# Minimum number of samples a path must appear in to get a feature.
MIN_PATH_FREQ = 5

# Default trait hierarchy levels the path-prefix families see. Scan's
# finding_paths serves exactly this many; see FeatureConfig.trait_path_depth.
DEFAULT_TRAIT_PATH_DEPTH = 3


# Minimum confidence for a finding to be included in feature extraction.
# Low-confidence findings add noise without meaningful signal.
MIN_CONFIDENCE = 0.65

# What a *missing* `conf` on a finding means: no confidence recorded. cleave
# now always writes `conf`, so this only applies to reports from builds that
# omitted it. Reading the absence as 1.0 (the old value here) let a finding
# cleave was unsure about clear MIN_CONFIDENCE and score as definitive, in
# training and inference alike. Zero falls below every gate, which is the
# honest reading of an absent value. Matches cleave's plain serde default.
MISSING_CONF = 0.0

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
# or removed (v20 ranks n-gram tokens before limiting them;
# v19 makes trait_path_depth a per-model runtime contract;
# v18 added the ALWAYS_KEEP_METRICS allowlist, which
# grows the extended-metrics block by `ast_depth_capped`; v17 added cluster:* +
# agg:static_*).
#
# Bump it ALSO when the feature-allowlist prune changes the LAYOUT — not
# just when whole families appear/disappear. litmus places the offset-written
# families (present:/maxcrit:/bigrams:/trigram:/unsigned_bigram:) by their
# position in feature_names, so pruning entries out of an earlier block shifts
# every later family. A 26-slot metrics-block prune shipped under an unchanged
# v17 and ran litmus's unsigned-bigram block off the end of the vector. The
# `feature_layout_hash` written into every spec records the exact layout so
# such a change is detectable even when this number is forgotten.
MODEL_ABI_VERSION = 20

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

# Extended-metric keys that must enter the vocab even though they fall below the
# COLLIMATOR_METRIC_MIN_FREQ_PCT floor. Anti-analysis signals are rare *by
# design* — they fire on a tiny fraction of (almost exclusively malicious)
# samples — so a pure frequency prune would drop exactly the high-signal columns
# we most want. Listing one here reserves its feature slot regardless of how
# often the scan sample happened to see it. Keys are `group_field` (the same
# form the scan produces from the dotted metric path, e.g. `ast.depth_capped` →
# `ast_depth_capped`). Unlike KEY_METRICS these are NOT force-emitted when
# absent from the spec vocab — they are only retained when the extended-metrics
# scan is enabled, and they still honor an explicit extended_metrics_include
# prefix filter so experiment isolation is preserved.
ALWAYS_KEEP_METRICS: frozenset[str] = frozenset({
    # filefacts emits this (=1) when a source file forces the AST walk's
    # MAX_AST_DEPTH bound — a member/concat/subscript chain thousands deep, an
    # anti-static-analysis shape that used to overflow the worker stack.
    "ast_depth_capped",
})


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
    min_crit: int,
    branch_min_crit: dict[str, int] | None = None,
) -> list[str]:
    """Generate severity-prefixed report-level path tokens for tiered bigrams.

    `sample_paths` already holds each finding's prefixes up to
    trait_path_depth, so every qualifying prefix becomes one token.

    When `branch_min_crit` is supplied, the per-branch floor (matched against
    the path's top-level component) overrides the global `min_crit`. Branches
    not in the map fall back to `min_crit`. Lets autocollie set tighter floors
    on noisy branches (e.g. `metadata=4`) and looser on signal-dense ones
    (e.g. `objectives=2`).
    """
    branch_min_crit = branch_min_crit or {}
    tokens: list[str] = []
    for path, max_ord in sample_paths.items():
        floor = branch_min_crit.get(path.split("/", 1)[0], min_crit)
        # Filtered (crit 0) paths never form tokens, even under a 0 floor.
        if max_ord > 0 and max_ord >= floor:
            tokens.append(f"{_CRIT_PREFIX.get(max_ord, 'n')}:{path}")
    return sorted(tokens)


# v20 keeps evidence instead of dropping the whole family on overflow.
# Higher-order families have smaller budgets to bound vocabulary enumeration.
TIERED_TOKEN_LIMITS = {2: 512, 3: 128, 4: 64}


def _finding_score(criticality: int, confidence: float) -> float:
    # Cleave stores confidence as f32. Canonicalize before multiplying so
    # JSON decoding precision cannot change ranking at the token boundary.
    if not math.isfinite(confidence):
        return 0.0
    return criticality * float(np.float32(min(1.0, max(0.0, confidence))))


def _ranked_tiered_tokens(
    sample_paths: dict[str, int],
    path_scores: dict[str, float],
    *,
    order: int,
    min_crit: int,
    branch_min_crit: dict[str, int] | None = None,
) -> list[str]:
    tokens = _tiered_bigram_tokens(
        sample_paths, min_crit=min_crit, branch_min_crit=branch_min_crit,
    )
    limit = TIERED_TOKEN_LIMITS[order]
    if len(tokens) > limit:
        # Every score is max(criticality * confidence) from an actual finding.
        # Lexical ties make the result independent of report/file ordering.
        tokens = heapq.nsmallest(
            limit, tokens, key=lambda token: (-path_scores.get(token[2:], 0.0), token),
        )
    return sorted(tokens)


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
    # Size-invariant severity FRACTIONS (crit-tier count / total findings) +
    # malicious:mundane ratio + crit4-present flag. Unlike the per-KB density
    # features, these don't read sparsity as innocence — a tiny file that is
    # mostly suspicious findings (e.g. an npm dropper: a few crit-4 supply-chain
    # traits and nothing else) scores HIGH. Opt-in (autocollie A/B candidate).
    include_severity_fractions: bool
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
    # How many levels of a trait path (`objectives/evasion/process/...`) the
    # path-prefix families see: presence, ghosts, taxonomy aggregates, and the
    # tiered n-grams. Each finding contributes its 1..depth prefixes.
    trait_path_depth: int
    # Report-level severity-prefixed trait bigrams from notable+ paths.
    # This is intentionally separate from generic per-file bigrams so it can
    # be ablated independently. Default production setting is min_crit=3,
    # matching the scripts-pool sweep winner.
    include_tiered_crit_bigrams: bool
    tiered_bigram_min_crit: int
    tiered_bigram_max: int
    tiered_bigram_min_freq: int
    include_tiered_crit_trigrams: bool
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
    # so the per-token cap is tighter (64) and autocollie should
    # only enable this on routes where the trigram knob already won.
    include_tiered_crit_quadgrams: bool
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
    # Default OFF — opt-in experimental feature group (autocollie A/B candidate).
    include_severity_fractions = os.getenv("COLLIMATOR_SEVERITY_FRACTION_FEATURES", "0").strip().lower() in {
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
        include_severity_fractions=include_severity_fractions,
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
        trait_path_depth=max(
            int(os.getenv("COLLIMATOR_TRAIT_PATH_DEPTH", str(DEFAULT_TRAIT_PATH_DEPTH))), 1,
        ),
        include_tiered_crit_bigrams=os.getenv("COLLIMATOR_TIERED_CRIT_BIGRAMS") in {
            "1", "true", "yes", "on",
        },
        tiered_bigram_min_crit=int(os.getenv("COLLIMATOR_TIERED_BIGRAM_MIN_CRIT", "3")),
        tiered_bigram_max=int(os.getenv("COLLIMATOR_TIERED_BIGRAM_MAX", "5000")),
        tiered_bigram_min_freq=int(os.getenv("COLLIMATOR_TIERED_BIGRAM_MIN_FREQ", "5")),
        include_tiered_crit_trigrams=os.getenv("COLLIMATOR_TIERED_CRIT_TRIGRAMS") in {
            "1", "true", "yes", "on",
        },
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
        bigram_max=int(os.getenv("COLLIMATOR_BIGRAM_MAX", "5000")),
        bigram_min_freq=int(os.getenv("COLLIMATOR_BIGRAM_MIN_FREQ", "5")),
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

def _alias(obj: dict[str, Any], *keys: str) -> Any:
    """First non-None value among key aliases (new key first, old fallbacks).

    Bridges cleave's v7 long keys (`files`, `find`, `conf`, `crit`, …) with the
    legacy short keys (`fs`, `ts`, `c`, `l`, …) so collimator parses old stored
    reports and new cleave output alike. Mirrors prism's parse-old/emit-new
    handling: both schemes are read; only the new scheme is emitted.
    """
    for key in keys:
        value = obj.get(key)
        if value is not None:
            return value
    return None


def report_files(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Return all valid file entries (v7 `files`, else v4 `fs`)."""
    files = _alias(report, "files", "fs") or []
    return [f for f in files if isinstance(f, dict)]


def primary_file(report: dict[str, Any]) -> dict[str, Any]:
    """Return the primary (first) file entry from a report."""
    files = report_files(report)
    return files[0] if files else {}


def file_facts(file_entry: dict[str, Any]) -> dict[str, Any]:
    """Return the dense facts block: cleave v8 `facts`, v7 `fact`, else v5 `ff`, else {}."""
    facts = _alias(file_entry, "facts", "fact", "ff")
    return facts if isinstance(facts, dict) else {}


# cleave metric renames (2026-08-22, Pike-naming pass, and later). Trained
# models and allowed_features.json carry the OLD feature names; reports carry
# the NEW metric names. `file_metrics` back-fills the old key from the new one so
# every existing vocab keeps resolving. Keep every entry: hopper keeps reports
# from every generation, so training always mixes old and new names. Mirrored
# in scan's src/features.rs METRIC_RENAMES; change both together.
_METRIC_RENAMES: dict[str, str] = {  # old flat name -> new flat name
    "archive.total_compressed": "archive.compressed_size",
    "archive.total_uncompressed": "archive.uncompressed_size",
    "ast.array_literal_max_length": "ast.max_array_length",
    "ast.numeric_array_max_length": "ast.max_numeric_array",
    "ast.numeric_sequence_max_length": "ast.max_numeric_sequence",
    "ast.string_concat_chain_max_length": "ast.max_concat_chain",
    "binary.embedded_archive_count": "binary.embedded_archives",
    "binary.embedded_binary_count": "binary.embedded_binaries",
    "binary.embedded_file_count": "binary.embedded_files",
    "binary.overall_entropy": "file.entropy",
    "binary.total_basic_blocks": "binary.basic_block_count",
    "comments.base64_in_comments": "comments.base64",
    "comments.code_in_comments": "comments.code",
    "comments.empty_comments": "comments.empty",
    "comments.high_entropy_comments": "comments.high_entropy",
    "comments.total": "comments.count",
    "elf.gnu_stack_section_absent": "elf.no_gnu_stack",
    "elf.stripped_but_symtab_present": "elf.stripped_with_symtab",
    "file.size_bytes": "file.size",
    "functions.code_in_functions_ratio": "functions.code_ratio",
    "functions.density_per_100_lines": "functions.density",
    "functions.nested_functions": "functions.nested",
    "identifiers.total": "identifiers.count",
    "identifiers.unique_count": "identifiers.unique",
    "imports.aliased_imports": "imports.aliased",
    "imports.dynamic_imports": "imports.dynamic",
    "imports.relative_imports": "imports.relative",
    "imports.unique_modules": "imports.count",
    "imports.wildcard_imports": "imports.wildcard",
    "pe.headers_size_bytes": "pe.headers_size",
    "strings.hex_strings": "strings.hex",
    "strings.shell_command_strings": "strings.shell",
    "strings.sql_strings": "strings.sql",
    "strings.total": "strings.count",
    "strings.total_bytes": "strings.bytes",
    "strings.unicode_heavy_strings": "strings.unicode_heavy",
    "strings.url_encoded_strings": "strings.url_encoded",
    "strings.very_long_strings": "strings.very_long",
    "text.high_byte_ratio": "text.non_ascii_ratio",
    "text.max_inline_whitespace_run": "text.max_whitespace_run",
    "text.most_common_char_codepoint": "text.top_char",
    "text.most_common_char_is_null": "text.top_char_null",
    "text.most_common_ratio": "text.top_char_ratio",
    "text.total_lines": "text.lines",
    # Later renames: filefacts' 2026-10-01 schema cleanup, and metrics cleave
    # computed before filefacts took over parsing.
    "ast.member_depth_max": "ast.max_member_depth",
    "binary.high_entropy_strings": "binary.high_entropy_string_count",
    "binary.normalized_string_count": "text.normalized_string_count",
    "comments.url_in_comments": "comments.url_count",
    "elf.build_id_present": "elf.has_build_id",
    "elf.class_bits": "elf.bits",
    "elf.debuglink_present": "elf.has_debuglink",
    "elf.entry_point": "elf.entry",
    "elf.gnu_hash_present": "elf.has_gnu_hash",
    "elf.hidden_symbols": "elf.hidden_symbol_count",
    "elf.load_segment_max_p_filesz": "elf.load_segment_max_file_size",
    "elf.load_segment_max_p_memsz": "elf.load_segment_max_memory_size",
    "pe.certificate_table_size": "pe.cert_table_size",
    "pe.delay_load_imports": "pe.delay_import_count",
    "pe.manifest_present": "pe.has_manifest",
    "pe.size_of_headers": "pe.headers_size",
    "pe.size_of_image": "pe.image_size",
    "pe.tls_callbacks": "pe.tls_callback_count",
    "pe.version_info_present": "pe.has_version_info",
    "text.max_ws_run": "text.max_whitespace_run",
}


def _backfill_renamed_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    """Alias renamed metrics under their old names (see _METRIC_RENAMES)."""
    for old, new in _METRIC_RENAMES.items():
        old_group, old_field = old.split(".", 1)
        new_group, new_field = new.split(".", 1)
        new_grp = metrics.get(new_group)
        if not isinstance(new_grp, dict) or new_field not in new_grp:
            continue
        old_grp = metrics.setdefault(old_group, {})
        if isinstance(old_grp, dict) and old_field not in old_grp:
            old_grp[old_field] = new_grp[new_field]
    return metrics


def file_metrics(file_entry: dict[str, Any]) -> dict[str, Any]:
    """Return per-file metrics from v8 facts.metrics / v7 fact.met / v5 ff.m / v4 ms."""
    facts = file_facts(file_entry)
    metrics = _alias(facts, "metrics", "met", "m") if facts else None
    if not isinstance(metrics, dict):
        metrics = file_entry.get("ms")
    if not isinstance(metrics, dict):
        return {}
    return _backfill_renamed_metrics(metrics)


def _tuple_string(raw: Any, index: int) -> str:
    if isinstance(raw, (list, tuple)) and len(raw) > index:
        return str(raw[index] or "")
    return ""


def file_imports(file_entry: dict[str, Any]) -> list[Any]:
    """Return import entries from v7 fact.imp / v5 ff.i / v4 is."""
    facts = file_facts(file_entry)
    raw = _alias(facts, "imp", "i") if facts else None
    if raw is None:
        raw = file_entry.get("is")
    return raw if isinstance(raw, list) else []


def file_findings(file_entry: dict[str, Any]) -> list[Any]:
    """Return a file entry's findings (v8 `traits`, v7 `find`, else v4 `ts`)."""
    return _alias(file_entry, "traits", "find", "ts") or []


def file_has_parent(file_entry: dict[str, Any]) -> bool:
    """Whether this file was extracted from another file in the same report.

    Three spellings, because cleave renamed this twice. v8 names the parent
    `pid`, the containing file's id. v4-v6 named it `p`, the containing file's
    *path*. Both v7 and v8 also carry `depth`, and anything below the root is
    by definition contained.

    Reading only `p` — which is what this module did until the rename was
    noticed — silently reports every v8 report as a flat bag of root files.
    """
    if file_entry.get("pid") is not None:
        return True
    if file_entry.get("p"):
        return True
    return _float(_alias(file_entry, "depth", "dp") or 0) > 0


def report_depths(files: list[dict[str, Any]]) -> list[int]:
    """Archive nesting depth for every file, in report order.

    v7 and v8 state it outright, so it is taken as given. Older reports carry
    only `p`, the parent's path, and depth is the length of the chain from a
    file up to a root — walked here rather than accumulated in one pass,
    because a report is not required to list a parent before its children and
    the old one-pass form quietly returned zero when it did not.
    """
    if any(_alias(f, "depth", "dp") is not None for f in files):
        return [int(_float(_alias(f, "depth", "dp") or 0)) for f in files]

    parents = {f.get("path", ""): f.get("p", "") for f in files}
    depths = []
    for entry in files:
        seen: set[str] = set()
        path = entry.get("path", "")
        depth = 0
        while True:
            parent = parents.get(path, "")
            # A path that is its own ancestor would otherwise spin forever.
            if not parent or parent in seen:
                break
            seen.add(path)
            path = parent
            depth += 1
        depths.append(depth)
    return depths


def file_size(file_entry: dict[str, Any]) -> Any:
    """Return a file entry's size (v7 `size`, else v4 `sz`)."""
    return _alias(file_entry, "size", "sz")


def file_formula(file_entry: dict[str, Any]) -> Any:
    """Return a file entry's molecular formula (v7 `mol`, else v4 `f`)."""
    return _alias(file_entry, "mol", "f")


def file_risk(file_entry: dict[str, Any]) -> Any:
    """Return a file entry's risk/score (v7 `risk`, else v4 `x`)."""
    return _alias(file_entry, "risk", "x")


def finding_id(finding: dict[str, Any]) -> Any:
    """Return a finding's id (v7 `id`, else v4 `i`)."""
    return _alias(finding, "id", "i")


def finding_conf(finding: dict[str, Any]) -> Any:
    """Return a finding's confidence (v7 `conf`, else v4 `c`)."""
    return _alias(finding, "conf", "c")


def finding_crit(finding: dict[str, Any]) -> Any:
    """Return a finding's criticality ordinal (v7 `crit`, else v4 `l`)."""
    return _alias(finding, "crit", "l")


def finding_attack(finding: dict[str, Any]) -> Any:
    """Return a finding's ATT&CK code (v7 `atk`, else v4 `a`)."""
    return _alias(finding, "atk", "a")


def finding_mbc(finding: dict[str, Any]) -> Any:
    """Return a finding's MBC code (v7 `mbc`, else v4 `m`)."""
    return _alias(finding, "mbc", "m")


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
    for raw in _alias(facts, "exp", "x") or []:
        name = _tuple_string(raw, 0) if isinstance(raw, (list, tuple)) else raw
        sym = _normalize_vocab_token(name)
        if len(sym) >= 2:
            symbols.add(sym)
    for raw in (facts.get("funcs") or facts.get("fn")) or []:
        name = _tuple_string(raw, 0) if isinstance(raw, (list, tuple)) else raw
        sym = _normalize_vocab_token(name)
        if len(sym) >= 2:
            symbols.add(sym)
    for raw in _alias(facts, "tgt", "ct") or []:
        sym = _normalize_vocab_token(raw)
        if len(sym) >= 2:
            symbols.add(sym)
    for raw in _alias(facts, "mbr", "mc") or []:
        sym = _normalize_vocab_token(raw)
        if len(sym) >= 2:
            symbols.add(sym)
    return symbols


_SYMBOL_BIGRAM_CAP = 64
_SYMBOL_TRIGRAM_CAP = 24


def _file_symbol_bigrams(file_entry: dict[str, Any]) -> list[str]:
    symbols = sorted(_file_symbols(file_entry))[:_SYMBOL_BIGRAM_CAP]
    return ["||".join(pair) for pair in combinations(symbols, 2)]


def _file_symbol_trigrams(file_entry: dict[str, Any]) -> list[str]:
    symbols = sorted(_file_symbols(file_entry))[:_SYMBOL_TRIGRAM_CAP]
    return ["||".join(triple) for triple in combinations(symbols, 3)]


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
    """Categorical metric values, with optional bounded shape/part tokens."""
    tokens: set[str] = set()
    for group, fields in file_metrics(file_entry).items():
        if not isinstance(fields, dict):
            continue
        for key, value in fields.items():
            base = f"{group}.{key}"
            if include_shape:
                tokens.add(f"{base}:exists")
            if isinstance(value, bool):
                val = str(value).lower()
                tokens.add(f"{base}={val}")
                if include_shape:
                    tokens.add(f"{base}:bool={val}")
            elif isinstance(value, str):
                val = _normalize_vocab_token(value, max_len=80)
                if val:
                    tokens.add(f"{base}={val}")
                if include_shape:
                    tokens.add(f"{base}:strlen={_bucket_count(len(value))}")
                    tokens.add(f"{base}:nonempty" if value else f"{base}:empty")
                if split_string_values:
                    for part in _KV_VALUE_SPLIT_SEPARATORS.split(value):
                        part = _normalize_vocab_token(part, max_len=64)
                        if part:
                            tokens.add(f"{base}=part:{part}")
            elif include_shape:
                if value in (None, [], {}, ()):
                    tokens.add(f"{base}:empty")
                if isinstance(value, (int, float)):
                    tokens.add(f"{base}:number={_bucket_number(float(value))}")
                elif isinstance(value, (list, tuple, set, dict)):
                    tokens.add(f"{base}:len={_bucket_count(len(value))}")
    return tokens


def _char_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts: dict[str, int] = {}
    for ch in value:
        counts[ch] = counts.get(ch, 0) + 1
    n = len(value)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


@lru_cache(maxsize=32768)
def _finding_paths(finding_id: str, depth: int) -> tuple[str, ...]:
    """Extract hierarchical path prefixes (1..depth levels) from a finding ID.

    At depth=3:
    "objectives/evasion/process/injection::technique-x"
        -> ("objectives", "objectives/evasion", "objectives/evasion/process")
    "metadata/format::no-functions"
        -> ("metadata", "metadata/format")

    Cached because callers in the hot extraction loop call this 1000+
    times per row with a small universe of distinct finding_ids.
    """
    base = finding_id.split("::")[0] if "::" in finding_id else finding_id
    parts = base.split("/")
    return tuple("/".join(parts[:d]) for d in range(1, min(len(parts), depth) + 1))


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

    # `version` and `abi_version` are one compatibility number — both derive
    # from MODEL_ABI_VERSION so they can never drift (they used to be a literal
    # `17` and the constant, which silently desynced on a bump). Raising
    # MODEL_ABI_VERSION requires a matching bump of EXPECTED_SPEC_VERSION in
    # ../scan (Rust); scan accepts a range (v16..=current) so live deploys
    # keep working through a transition while new bundles serialize at current.
    version: int = MODEL_ABI_VERSION
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
    # Trait hierarchy levels the path-prefix vocabs were built at. Scan v19
    # reads this per model; absent fields in older specs default to depth 3.
    trait_path_depth: int = DEFAULT_TRAIT_PATH_DEPTH
    tiered_min_crit: tuple[int, int, int] = (3, 3, 3)
    tiered_branch_min_crit: dict[str, int] = field(default_factory=dict)

    def _litmus_offset_vocabs(self) -> tuple[list[str], list[str], list[str]]:
        """Return the presence/bigram/trigram vocabs litmus reconstructs the
        offset-written families from, derived directly from ``feature_names``.

        litmus builds present:/maxcrit: from presence_vocab, bigrams:/
        unsigned_bigram: from bigram_vocab, and trigram: from trigram_vocab,
        resolving each member to its real slot by name (no contiguity required —
        see litmus features.rs slot maps). A path that survives the allowlist for
        only ONE side of a pair (e.g. importance keeps maxcrit:X but drops
        present:X) still needs its path in the vocab, or litmus can't produce the
        surviving member at all — it extracts as a silent zero and logs "feature
        spec contains features unknown to this extractor". So each vocab is the
        UNION of the paths its two families use in feature_names, in first-
        appearance order. Deriving from feature_names (rather than the in-memory
        vocab) makes this correct even when re-saving an already-pruned spec.
        collimator's own extractor is name-addressed, so output is unchanged.
        """
        def _family_union(prefixes: tuple[str, ...]) -> list[str]:
            seen: dict[str, None] = {}
            for name in self.feature_names:
                for prefix in prefixes:
                    if name.startswith(prefix):
                        seen.setdefault(name[len(prefix):], None)
                        break
            return list(seen)

        presence = _family_union(("present:", "maxcrit:"))
        bigram = _family_union(("bigrams:", "unsigned_bigram:"))
        trigram = _family_union(("trigram:",))
        return presence, bigram, trigram

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        presence_vocab, bigram_vocab, trigram_vocab = self._litmus_offset_vocabs()
        # Records the exact emitted layout. Any prune/reorder changes it, so an
        # incompatible bundle is detectable even if MODEL_ABI_VERSION is forgotten.
        layout_hash = hashlib.sha256("\n".join(self.feature_names).encode()).hexdigest()
        d: dict[str, Any] = {
            "version": self.version,
            "abi_version": self.abi_version,
            "feature_layout_hash": layout_hash,
            "presence_vocab": presence_vocab,
            "filetype_vocab": self.filetype_vocab,
            "element_vocab": self.element_vocab,
            "bigram_vocab": bigram_vocab,
            "ghost_vocab": self.ghost_vocab,
            "skeleton_vocab": self.skeleton_vocab,
            "rare_element_vocab": self.rare_element_vocab,
            "trigram_vocab": trigram_vocab,
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
            "trait_path_depth": self.trait_path_depth,
            "tiered_min_crit": list(self.tiered_min_crit),
            "tiered_branch_min_crit": self.tiered_branch_min_crit,
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
            trait_path_depth=data.get("trait_path_depth", DEFAULT_TRAIT_PATH_DEPTH),
            tiered_min_crit=tuple(data.get("tiered_min_crit", [3, 3, 3])),
            tiered_branch_min_crit=data.get("tiered_branch_min_crit", {}),
        )


# ---------------------------------------------------------------------------
# Fact profiles
# ---------------------------------------------------------------------------
# cleave stores reports whose `files[].facts` are cut down to a model-input
# profile and stamps the report `"fp": <profile id>`. Every metric outside the
# profile, every symbol row whose name is not a gap token, and every section is
# gone, and a feature reading one would silently extract 0 for these reports
# but the true value for full-facts reports. A report with no `fp` carries
# full facts and needs no check.
#
# The profile is cleave's src/model_facts_manifest.json, vendored here so
# training does not depend on a sibling checkout; a report naming any other
# profile is rejected rather than guessed at. The rules are those of cleave's
# model_facts::supports, so both sides agree on what a profile covers.
FACT_PROFILE_MANIFEST = Path(__file__).parent / "data" / "model_facts_manifest.json"


class FactProfileError(ValueError):
    """A report's fact profile cannot supply every feature in the layout."""


@lru_cache(maxsize=1)
def _fact_profile_manifest() -> dict[str, Any]:
    with open(FACT_PROFILE_MANIFEST) as f:
        manifest: dict[str, Any] = json.load(f)
    return manifest


def check_fact_profile(profile: str, feature_names: Iterable[str]) -> None:
    """Raise FactProfileError unless `profile` covers every feature named.

    A metric must be one the profile retains. Families that only re-key
    vocabulary entries (present:, bigrams:, ...) or read no facts at all
    (filetype:, ghost:, ...) are covered as a whole; any other feature must be
    in the profile's audited fixed-feature list, so a new scalar feature fails
    until its fact dependencies have been audited.
    """
    manifest = _fact_profile_manifest()
    if profile != manifest["id"]:
        raise FactProfileError(
            f"unknown fact profile {profile!r}: collimator knows only "
            f"{manifest['id']!r} ({FACT_PROFILE_MANIFEST}); copy the matching "
            "src/model_facts_manifest.json from cleave"
        )
    families = set(manifest["families"])
    parameterized = set(manifest["parameterized_families"])
    metrics = set(manifest["metrics"])
    fixed = set(manifest["fixed_features"])
    uncovered: list[str] = []
    for name in feature_names:
        family, _, key = name.partition(":")
        if family not in families:
            uncovered.append(f"{name} (family {family!r} not in profile)")
        elif family == "metrics":
            if key not in metrics:
                uncovered.append(f"{name} (metric not retained)")
        elif family not in parameterized and name not in fixed:
            uncovered.append(f"{name} (no fact-dependency audit)")
    if uncovered:
        shown = ", ".join(uncovered[:20])
        more = f", and {len(uncovered) - 20} more" if len(uncovered) > 20 else ""
        raise FactProfileError(
            f"fact profile {profile} omits inputs for {len(uncovered)} features "
            f"in this layout: {shown}{more}. Train on full facts (cleave "
            "--full-facts), drop these features, or extend the profile in cleave"
        )


# ---------------------------------------------------------------------------
# Vocabulary building
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def allowed_features() -> frozenset[str] | None:
    """Read an explicit name filter. Missing or invalid pins are errors."""
    path = os.getenv("COLLIMATOR_ALLOWED_FEATURES_FILE")
    if not path:
        return None
    with open(path) as f:
        content = json.load(f)
    names = content.get("significant_features") if isinstance(content, dict) else content
    if not isinstance(names, list) or not names or any(not isinstance(n, str) or not n for n in names):
        raise ValueError(f"{path}: expected a nonempty feature-name list or significant_features list")
    return frozenset(names)


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
        if config.include_severity_fractions:
            feature_names.extend([
                "agg:crit3_finding_fraction",    # (crit>=3) / total findings — size-invariant
                "agg:crit4_finding_fraction",    # (crit>=4) / total findings
                "agg:hostile_finding_fraction",  # (crit>=5) / total findings
                "agg:severe_to_mundane_ratio",   # (crit>=3) / (crit<3) — malicious:mundane
                "agg:crit4_present",             # 1.0 if any crit>=4 finding, else 0.0
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

    # Metadata vocabularies share the same knobs at discovery and extraction.
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

    # Optional explicit name filter.
    allowed = allowed_features()
    if allowed is not None:
        original_count = len(feature_names)
        feature_names = [name for name in feature_names if _allowed_with_pair(name, allowed)]
        if not feature_names:
            raise ValueError("selected allowlist excludes every discovered feature")
        log.info("pruned feature spec: %d -> %d features", original_count, len(feature_names))
    else:
        log.info("feature vocabulary: %d columns (no fixed name filter)", len(feature_names))

    return feature_names


# Offset-written families come in pairs that litmus reconstructs from a single
# shared vocab — present:/maxcrit: from presence_vocab, bigrams:/unsigned_bigram:
# from bigram_vocab. Both members of a pair MUST keep identical membership or
# litmus extracts the orphaned slots as zeros (and validate warns "unknown
# features"). An importance/frequency allowlist ranks the two members
# independently, so it routinely keeps one and drops the other. Couple them:
# keep a member whenever EITHER it or its partner survives the allowlist.
_OFFSET_FAMILY_PAIRS = (("present:", "maxcrit:"), ("bigrams:", "unsigned_bigram:"))


def _allowed_with_pair(name: str, allowed: "frozenset[str]") -> bool:
    if name in allowed:
        return True
    for a, b in _OFFSET_FAMILY_PAIRS:
        if name.startswith(a):
            return (b + name[len(a):]) in allowed
        if name.startswith(b):
            return (a + name[len(b):]) in allowed
    return False


def build_vocab(reports: Iterable[dict[str, Any] | str], n_workers: int = 0) -> FeatureSpec:
    """Unlabeled helper: count the supplied reports without class selection.

    Training uses build_vocab_from_db to discover singletons from both classes
    and combinations from malware.
    """
    with _vocabulary_counts() as (counts, scratch):
        return _build_vocab(reports, n_workers, counts, scratch)


def _build_vocab(reports, n_workers, counts, scratch) -> FeatureSpec:
    """Scan all reports to build the feature vocabulary."""
    # This standard build_vocab doesn't have labels, so it can't find ghosts.
    # Ghosts require build_vocab_from_db or a labeled stream.
    # For now, we'll return an empty ghost_vocab here.
    nw = resolve_worker_count(n_workers)
    presence_counts: dict[str, int] = {}
    filetypes: set[str] = set()
    element_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    batch_size = _feature_batch_size(nw)
    n_batches = 0
    _PROGRESS_BATCH_INTERVAL = 500

    def _merge_batch(
        path_counts: dict[str, int],
        fts: list[str],
        el_counts: dict[str, int],
        bi_counts: CountView,
        b_pres: dict[str, int],
        m_pres: dict[str, int],
        sk_counts: dict[str, int],
    ) -> None:
        nonlocal n_batches
        for k, v in path_counts.items():
            presence_counts[k] = presence_counts.get(k, 0) + v
        filetypes.update(fts)
        for k, v in el_counts.items():
            element_counts[k] = element_counts.get(k, 0) + v
        counts.merge(bi_counts)
        for k, v in sk_counts.items():
            skeleton_counts[k] = skeleton_counts.get(k, 0) + v
        n_batches += 1

    if nw > 1:
        with _feature_worker_pool(nw) as pool:
            for res in _bounded_iter(
                pool, _vocab_stream_batch_worker, ((batch, scratch) for batch in _batched(reports, batch_size)),
                max_inflight=2 * nw,
            ):
                _merge_batch(*res)
    else:
        for res in map(_vocab_stream_batch_worker, ((batch, scratch) for batch in _batched(reports, batch_size))):
            _merge_batch(*res)

    presence_vocab = sorted(k for k, c in presence_counts.items() if c >= MIN_PATH_FREQ)
    filetype_vocab = sorted(filetypes)
    element_vocab = sorted(k for k, c in element_counts.items() if c >= MIN_PATH_FREQ)
    bigram_vocab = counts.top("bigram", feature_config_from_env().bigram_max, feature_config_from_env().bigram_min_freq)
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
        trait_path_depth=feature_config_from_env().trait_path_depth,
        tiered_min_crit=(feature_config_from_env().tiered_bigram_min_crit, feature_config_from_env().tiered_trigram_min_crit, feature_config_from_env().tiered_quadgram_min_crit),
        tiered_branch_min_crit=_parse_branch_min_crit_overrides(feature_config_from_env().tiered_bigram_branch_min_crit),
    )
    return spec


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

class _ExtractContext:
    """Pre-built lookup tables for fast repeated extraction against a spec."""

    __slots__ = (
        "presence_lookup", "maxcrit_lookup", "ft_lookup", "n_ft",
        "tiered_min_crit", "tiered_branch_min_crit",
        "element_lookup", "element_interaction_lookup", "n_el",
        "bigram_lookup", "n_bi", "tiered_bigram_lookup", "n_tier_bi",
        "tiered_trigram_lookup", "n_tier_tri",
        "ghost_vocab", "ghost_lookup", "n_gh",
        "skeleton_lookup", "skeleton_interaction_lookup", "n_sk",
        "rare_element_lookup", "n_re",
        "trigram_lookup", "n_tri", "blindfold", "total_features",
        "score_interaction_lookup", "synergy_lookup",
        "absolute_lookup",
        "ngram_vocab_paths", "bigram_vocab_paths", "trigram_vocab_paths", "synergy_vocab_paths",
        "tiered_bigram_vocab_tokens", "tiered_trigram_vocab_tokens",
        "tiered_quadgram_vocab_tokens",
        "bigram_lookup_pair", "synergy_lookup_pair", "trigram_lookup_triple", "trigrams_by_first",
        "trait_path_depth", "ranked_ngrams", "tiered_slots", "fact_profiles",
    )

    def __init__(self, spec: FeatureSpec) -> None:
        config = feature_config_from_env()
        self.blindfold = config.include_blindfold
        self.trait_path_depth = max(1, spec.trait_path_depth)
        self.ranked_ngrams = spec.abi_version >= 20
        self.total_features = spec.total_features
        self.tiered_min_crit = spec.tiered_min_crit
        self.tiered_branch_min_crit = spec.tiered_branch_min_crit
        
        # Build lookups that map to the actual indices in feature_names.
        name_to_idx = {name: i for i, name in enumerate(spec.feature_names)}
        self.absolute_lookup = name_to_idx
        # Fact profiles already checked against this layout (see check_fact_profile).
        self.fact_profiles: set[str] = set()

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

        self.tiered_slots = {
            order: [(idx, tuple(name[len(prefix):].split(" + ")))
                    for name, idx in name_to_idx.items() if name.startswith(prefix)]
            for order, prefix in ((2, "tierbi:"), (3, "tiertri:"), (4, "tierquad:"))
        }

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
        # Every path of an emitted n-gram feature: scan's path_to_id, which it
        # builds from the saved bigram/trigram vocabs — and FeatureSpec.save
        # derives those from the emitted names, not the (possibly unpruned)
        # in-memory lists. The per-file caps count against this set.
        self.ngram_vocab_paths: frozenset[str] = (
            self.bigram_vocab_paths | self.synergy_vocab_paths | self.trigram_vocab_paths
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
        # Only test triples whose first token occurs in the current file.
        # Scanning every vocabulary triple per archive member dominated CPU
        # time even when that member contained none of the vocabulary paths.
        self.trigrams_by_first: dict[str, list[tuple[str, str, int]]] = {}
        for (first, second, third), idx in self.trigram_lookup_triple.items():
            self.trigrams_by_first.setdefault(first, []).append((second, third, idx))


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
    path_scores: dict[str, float] = field(default_factory=dict)
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
    # are slow in a tight loop. include_soft_presence and trait_path_depth are
    # also read once (config snapshots, not per-finding switches) so we can
    # branch outside the inner loop.
    config = feature_config_from_env()
    include_soft_presence = config.include_soft_presence
    depth_override = _extract_trait_depth.get()
    path_depth = config.trait_path_depth if depth_override is None else depth_override
    min_conf = MIN_CONFIDENCE
    finding_paths = _finding_paths
    sample_paths: dict[str, int] = {}
    path_confidences: dict[str, float] = {}
    path_scores: dict[str, float] = {}
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
        fid = finding_id(finding) or ""
        if not fid:
            continue
        # _float used to wrap the confidence read but the value is
        # already a float coming from JSON in 99.9% of cases — the
        # try/float() overhead was hot. Fall back only for stragglers.
        conf_raw = finding_conf(finding)
        if conf_raw is None:
            conf_raw = MISSING_CONF
        conf = conf_raw if isinstance(conf_raw, float) else _float(conf_raw)
        if conf < min_conf:
            continue
        finding_confidences.append(conf)
        filtered_finding_count += 1
        crit_ord = finding_crit(finding) or 0
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

        paths = finding_paths(fid, path_depth)
        score = _finding_score(crit_ord, conf)
        for path in paths:
            path_scores[path] = max(path_scores.get(path, 0.0), score)
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
        path_scores=path_scores,
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
    path_scores: dict[str, float] = {}
    finding_confidences: list[float] = []

    for file_entry in files:
        summary = _summarize_findings(file_findings(file_entry))
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
            path_scores[path] = max(path_scores.get(path, 0.0), summary.path_scores.get(path, 0.0))

        finding_confidences.extend(summary.finding_confidences)

        for finding in file_findings(file_entry):
            fid = finding_id(finding) or ""
            if not fid or _float(finding_conf(finding), MISSING_CONF) < MIN_CONFIDENCE:
                continue
            crit_ord = finding_crit(finding) or 0
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
        path_scores=path_scores,
        finding_confidences=finding_confidences,
    )


def _file_risk_stats(file_entry: dict[str, Any]) -> _FileRiskStats:
    """Compute per-file suspiciousness for top-k package aggregation."""
    summary = _summarize_findings(file_findings(file_entry))
    denom = max(summary.filtered_finding_count, 1)
    size_kb = max(_float(file_size(file_entry) or 0.0) / 1024.0, 1.0)
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
    include_severity_fractions: bool = False,
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
    total_kb = max(sum(_float(file_size(file_entry) or 0.0) for file_entry in files) / 1024.0, 0.1)
    _assign(vec, lookup.get("agg:notable_finding_ratio"), summary.notable_finding_count / total_kb)
    _assign(vec, lookup.get("agg:suspicious_finding_ratio"), summary.suspicious_finding_count / total_kb)
    _assign(vec, lookup.get("agg:hostile_finding_ratio"), summary.hostile_finding_count / total_kb)
    _assign(vec, lookup.get("agg:unique_suspicious_ids_log"), math.log1p(summary.unique_suspicious_ids) / math.log1p(total_kb))
    _assign(vec, lookup.get("agg:unique_hostile_ids_log"), math.log1p(summary.unique_hostile_ids) / math.log1p(total_kb))

    if include_severity_fractions:
        # Size-invariant severity fractions: count of crit>=N findings as a
        # share of ALL findings (not per-KB). A minimal dropper — a few crit-4
        # supply-chain traits and almost no other findings — scores HIGH here,
        # where the per-KB density features (which assume malware is "busy")
        # read its sparsity as benign. See the npm-dropper SHAP analysis.
        total_findings = max(summary.filtered_finding_count, 1)
        mundane = max(summary.filtered_finding_count - summary.notable_finding_count, 1)
        _assign(vec, lookup.get("agg:crit3_finding_fraction"), summary.notable_finding_count / total_findings)
        _assign(vec, lookup.get("agg:crit4_finding_fraction"), summary.suspicious_finding_count / total_findings)
        _assign(vec, lookup.get("agg:hostile_finding_fraction"), summary.hostile_finding_count / total_findings)
        _assign(vec, lookup.get("agg:severe_to_mundane_ratio"), summary.notable_finding_count / mundane)
        _assign(vec, lookup.get("agg:crit4_present"), 1.0 if summary.suspicious_finding_count > 0 else 0.0)

    total_kb = max(sum(_float(file_size(file_entry) or 0.0) for file_entry in files) / 1024.0, 1.0)
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

    # Collect import count for import-density and import-finding-ratio features.
    total_imports = 0
    if config.exp_unsigned_import_density or config.exp_import_finding_ratio:
        import re
        api_pattern = re.compile(r'^[A-Z][a-zA-Z0-9_]{3,}[A-Za-z]$')
        for file_entry in files:
            for sym in _file_symbols(file_entry):
                if not api_pattern.match(sym):
                    continue
                total_imports += 1

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
            for finding in file_findings(file_entry):
                crit = finding_crit(finding) or 0
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
            total_size = sum(_float(file_size(f) or 0) for f in files) or 1.0
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
            for finding in file_findings(fe):
                fid = finding_id(finding)
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
            for finding in file_findings(fe):
                fid = finding_id(finding) or ""
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
            for finding in file_findings(file_entry):
                a = finding_attack(finding)
                if a:
                    attack_techniques.add(a)
                m = finding_mbc(finding)
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
        total_file_bytes += _metric_number(metrics, "binary", "file_size") or _float(file_size(file_entry) or 0)
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
        for finding in file_findings(fe):
            mid = finding_mbc(finding)
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
        is_inner = file_has_parent(file_entry)
        if is_inner:
            inner_files += 1
        if groups:
            known_files += 1
        file_summary = _summarize_findings(file_findings(file_entry))
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

    # Nesting depth, from whichever spelling this report uses.
    file_depths = report_depths(files)
    max_nesting_depth = max(file_depths, default=0)

    for file_entry in files:
        if file_has_parent(file_entry):
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

        if file_entry.get("type", "") in binary_like and _float(file_size(file_entry) or 0) < 20000:
            any_tiny_binary = True

        # Track max entropy across all files in the report.
        metrics = file_metrics(file_entry)
        binary_metrics = metrics.get("binary") or {}
        ent = _float(binary_metrics.get("overall_entropy", 0.0))
        if ent > 0:
            entropies.append(ent)
        max_entropy = max(max_entropy, ent)
        file_summary = _summarize_findings(file_findings(file_entry))
        if file_summary.suspicious_finding_count > 0:
            suspicious_files += 1
        if file_summary.hostile_finding_count > 0:
            hostile_files += 1
            if fmt:
                try:
                    hostile_mtimes.append(datetime.fromisoformat(str(fmt).replace(" ", "T")).timestamp())
                except (ValueError, TypeError):
                    pass
            if file_has_parent(file_entry):
                hostile_files_with_parent += 1
        
        if ent > 0 and file_entry.get("type", "") in {"javascript", "python", "pe", "elf", "macho"}:
            code_entropies.append(ent)

    # Stealth potential: high entropy (packed/encrypted) but very few findings.
    stealth_potential = 1.0 if (filtered_finding_count < 5 and max_entropy > 6.5) else 0.0

    _assign(vec, lookup.get("struct:tiny_executable"), 1.0 if any_tiny_binary else 0.0)
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
        total_size = sum(_float(file_size(f) or 0) for f in files)
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


# The n-gram contract with scan, which computes these features at serving time
# (~/scan src/features.rs: unique_3level_paths and
# write_{bigram,trigram}_features_optimized). Change both sides together.
NGRAM_MIN_CRIT = 3  # only notable+ findings form n-grams
BIGRAM_MAX_PATHS = 512  # v20 keeps the strongest paths; older models drop overflow
TRIGRAM_MAX_PATHS = 256  # legacy cap; v20 selects 128 to bound discovery work


def _ngram_paths_for_file(file_entry: dict[str, Any]) -> list[str]:
    """Sorted unique base paths of a file's confident notable+ findings."""
    paths: set[str] = set()
    for finding in file_findings(file_entry):
        fid = finding_id(finding)
        if (
            fid
            and _float(finding_conf(finding), MISSING_CONF) >= MIN_CONFIDENCE
            and (finding_crit(finding) or 0) >= NGRAM_MIN_CRIT
        ):
            paths.add(fid.split("::")[0])
    return sorted(paths)


def _ranked_ngram_paths(file_entry: dict[str, Any], limit: int) -> list[str]:
    """Select before vocabulary filtering, identically in discovery and serving."""
    scores: dict[str, float] = {}
    for finding in file_findings(file_entry):
        fid = finding_id(finding)
        conf = _float(finding_conf(finding), MISSING_CONF)
        crit = finding_crit(finding) or 0
        if fid and conf >= MIN_CONFIDENCE and crit >= NGRAM_MIN_CRIT:
            path = fid.split("::")[0]
            score = _finding_score(crit, conf)
            scores[path] = max(scores.get(path, 0.0), score)
    return _select_ngram_paths(scores, limit)


def _select_ngram_paths(scores: dict[str, float], limit: int) -> list[str]:
    if len(scores) <= limit:
        return sorted(scores)
    return sorted(heapq.nsmallest(limit, scores, key=lambda path: (-scores[path], path)))


def _ngram_files(
    report: dict[str, Any],
    ctx: _ExtractContext,
    max_paths: int,
    family_paths: frozenset[str],
) -> Iterator[list[str]]:
    """Yield selected paths; v19 retains its historical overflow behavior."""
    if not family_paths:
        return
    for file_entry in report_files(report):
        if ctx.ranked_ngrams:
            limit = 128 if max_paths == TRIGRAM_MAX_PATHS else max_paths
            paths = _ranked_ngram_paths(file_entry, limit)
            yield [p for p in paths if p in family_paths]
        else:
            paths = [p for p in _ngram_paths_for_file(file_entry) if p in ctx.ngram_vocab_paths]
            if len(paths) <= max_paths:
                yield [p for p in paths if p in family_paths]


def _apply_bigram_features(
    report: dict[str, Any],
    ctx: _ExtractContext,
    vec: np.ndarray,
    summary: "_FindingSummary | None" = None,
) -> None:
    """Group 11: trait bigram multi-hot features."""
    config = feature_config_from_env()
    use_conf = config.include_confidence_weighted_ngrams and summary is not None
    lookup = ctx.bigram_lookup_pair
    for paths_list in _ngram_files(report, ctx, BIGRAM_MAX_PATHS, ctx.bigram_vocab_paths):
        present = set(paths_list)
        for (p1, p2), idx in lookup.items():
            if p1 in present and p2 in present:
                vec[idx] = ((summary.path_confidences.get(p1, 1.0)
                             + summary.path_confidences.get(p2, 1.0)) / 2.0) if use_conf else 1.0


def _apply_tiered_features(
    summary: "_FindingSummary", ctx: _ExtractContext, vec: np.ndarray, order: int,
) -> None:
    slots = ctx.tiered_slots[order]
    if not slots:
        return
    options = dict(min_crit=ctx.tiered_min_crit[order - 2],
                   branch_min_crit=ctx.tiered_branch_min_crit)
    if ctx.ranked_ngrams:
        tokens = _ranked_tiered_tokens(
            summary.sample_paths, summary.path_scores, order=order, **options,
        )
    else:
        tokens = _tiered_bigram_tokens(summary.sample_paths, **options)
        if len(tokens) > (64 if order == 4 else 512):
            return
    present = set(tokens)
    # Work is bounded by the model vocabulary, not C(n, order).
    for slot, parts in slots:
        if all(part in present for part in parts):
            vec[slot] = 1.0


def _apply_tiered_bigram_features(summary, ctx, vec) -> None:
    _apply_tiered_features(summary, ctx, vec, 2)


def _apply_tiered_trigram_features(summary, ctx, vec) -> None:
    _apply_tiered_features(summary, ctx, vec, 3)


def _apply_tiered_quadgram_features(summary, ctx, vec) -> None:
    _apply_tiered_features(summary, ctx, vec, 4)


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
    lookup = ctx.trigrams_by_first
    for paths_list in _ngram_files(report, ctx, TRIGRAM_MAX_PATHS, ctx.trigram_vocab_paths):
        present = set(paths_list)
        for first in present:
            for second, third, idx in lookup.get(first, ()):
                if second in present and third in present:
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

    lookup = ctx.synergy_lookup_pair
    for paths_list in _ngram_files(report, ctx, BIGRAM_MAX_PATHS, ctx.synergy_vocab_paths):
        present = set(paths_list)
        for (p1, p2), idx in lookup.items():
            if p1 in present and p2 in present:
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
    profile = report.get("fp")
    if profile is not None:
        profile = str(profile)
        if profile not in ctx.fact_profiles:
            check_fact_profile(profile, ctx.absolute_lookup)
            ctx.fact_profiles.add(profile)
    token = _extract_trait_depth.set(ctx.trait_path_depth)
    try:
        _extract_into_at_depth(report, ctx, vec, formula, elements, score, mtime, cluster_id)
    finally:
        _extract_trait_depth.reset(token)


def _extract_into_at_depth(
    report: dict[str, Any],
    ctx: _ExtractContext,
    vec: np.ndarray,
    formula: str,
    elements: str,
    score: int,
    mtime: str,
    cluster_id: int,
) -> None:
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
            for file_entry, depth in zip(files, report_depths(files), strict=True):
                file_summary = _summarize_findings(file_findings(file_entry))
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
            config.include_severity_fractions,
            top_k_risk_files_min_crit=config.top_k_risk_files_min_crit,
        )
        if config.include_hostile_depth_weight:
            _assign(vec, ctx.absolute_lookup.get("agg:hostile_depth_weight"), hostile_depth_weight)

    if "ext" in config.enabled_groups:
        _apply_external_signal_features(summary, ctx, vec)
    if "metrics" in config.enabled_groups:
        _apply_metric_features(metrics, files, ctx, vec)
    # Batch 4: MBC ID unigram vocab. Lives in the `agg` group since attack
    # features (its closest sibling) live there too.
    if "agg" in config.enabled_groups and config.include_mbc_id_vocab:
        _apply_mbc_id_features(files, ctx, vec)
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
        total_size = sum(_float(file_size(f) or 0) for f in files)
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
            for finding in file_findings(file_entry):
                a = finding_attack(finding)
                if a:
                    atk_codes.add(a)
                m = finding_mbc(finding)
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


def _count_ngrams(paths, order, counts, family, document, benign_family="", *, n=1) -> None:
    """Exact document frequencies; input token selection bounds the work."""
    counts.increment_combinations(family, paths, order, document, benign_family, n=n)


@contextmanager
def _vocabulary_counts(checkpoint_dir: Path | None = None):
    if checkpoint_dir is not None:
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        with (checkpoint_dir / "lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            # A killed process cannot run TemporaryDirectory's cleanup.
            # Only this checkpoint's exclusive owner may remove orphan shards.
            for orphan in checkpoint_dir.iterdir():
                if (orphan.name.startswith(("workers-", "materialize-"))
                        and orphan.is_dir() and not orphan.is_symlink()):
                    shutil.rmtree(orphan)
            with tempfile.TemporaryDirectory(prefix="workers-", dir=checkpoint_dir.resolve()) as scratch:
                with VocabularyCounts(str(checkpoint_dir / "counts.sqlite"), durable=True,
                                      resume=True, check_same_thread=False, cache_size_mib=256,
                                      defer_signatures=True, materialize_workers=max(1, int(os.getenv(
                                          "COLLIMATOR_VOCAB_REDUCE_WORKERS", "2"))),
                                      materialize_merge_size=int(os.getenv("COLLIMATOR_VOCAB_MERGE_GROUP", "1"))) as counts:
                    yield counts, scratch
            if (checkpoint_dir / "feature_spec.json").is_file():
                # The spec is sufficient for pass 2 and future retries. Keep
                # its identity receipt, not tens of GB of completed counts.
                for suffix in ("", "-wal", "-shm"):
                    (checkpoint_dir / f"counts.sqlite{suffix}").unlink(missing_ok=True)
        return
    root = Path(os.getenv("COLLIMATOR_VOCAB_TMPDIR", "out/cache/vocabulary"))
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="count-", dir=root.resolve()) as scratch:
        # The merge thread uses this connection exclusively during counting;
        # the parent queries it only after the thread has joined.
        with VocabularyCounts(str(Path(scratch) / "merged.sqlite"), durable=True,
                              check_same_thread=False, cache_size_mib=256, defer_signatures=True,
                              materialize_workers=max(1, int(os.getenv(
                                  "COLLIMATOR_VOCAB_REDUCE_WORKERS", "2"))),
                              materialize_merge_size=int(os.getenv("COLLIMATOR_VOCAB_MERGE_GROUP", "1"))) as counts:
            yield counts, scratch


_VOCAB_MERGE_BACKLOG = 4


@contextmanager
def _background_vocab_merges(counts):
    """Overlap one SQLite writer with counting; bound queued shard files."""
    from .profiling import event
    pending = collections.deque()
    last_wait_log = 0.0
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="vocab-merge") as pool:
        def merge(view):
            from .profiling import profile
            with profile("vocab-merge"):
                counts.merge(view)

        def submit(view):
            nonlocal last_wait_log
            if len(pending) >= _VOCAB_MERGE_BACKLOG:
                started = time.monotonic()
                pending.popleft().result()
                waited = time.monotonic() - started
                event("vocabulary.merge_queue", "wait", wall_seconds=waited, depth=len(pending)+1)
                if waited >= 5 and time.monotonic() - last_wait_log >= 30:
                    log.info("vocab merge queue: waited %.1fs for writer (%d queued shards)",
                             waited, len(pending)+1)
                    last_wait_log = time.monotonic()
            pending.append(pool.submit(merge, view))

        yield submit
        for future in pending:
            future.result()


def _batch_count_path(scratch):
    if scratch is None:
        return ""
    fd, path = tempfile.mkstemp(suffix=".sqlite", dir=scratch)
    os.close(fd)
    return path


def _vocab_stream_batch_worker(args):
    items, scratch = args
    with VocabularyCounts(_batch_count_path(scratch)) as counts:
        return _count_vocab_batch(items, counts)


def _vocab_batch_worker(items):
    return _vocab_stream_batch_worker((items, None))


def _count_vocab_batch(
    items: list[dict[str, Any] | str], counts: VocabularyCounts,
) -> tuple[dict[str, int], list[str], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int]]:
    """Count path, element, bigram, and skeleton occurrences for a batch. CPU-only."""
    config = feature_config_from_env()
    path_depth = config.trait_path_depth
    presence_counts: dict[str, int] = {}
    filetypes: list[str] = []
    element_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}

    for document, item in enumerate(items):
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

        seen_bigrams: set[tuple[str, ...]] = set()
        sample_paths: dict[str, int] = {}
        for file_entry in report_files(report):
            ftype = file_entry.get("type", "")
            if ftype:
                filetypes.append(ftype)

            file_traits: set[str] = set()
            for finding in file_findings(file_entry):
                fid = finding_id(finding) or ""
                if not fid:
                    continue
                if _float(finding_conf(finding), MISSING_CONF) < MIN_CONFIDENCE:
                    continue
                crit_ord = finding_crit(finding) or 0
                file_traits.add(fid)
                for path in _finding_paths(fid, path_depth):
                    if crit_ord > sample_paths.get(path, -1):
                        sample_paths[path] = crit_ord

            # Collect co-occurring path pairs (bigrams) within each file.
            paths_list = _ranked_ngram_paths(file_entry, BIGRAM_MAX_PATHS)
            path_key = tuple(paths_list)
            if config.bigram_max > 0 and path_key not in seen_bigrams:
                seen_bigrams.add(path_key)
                _count_ngrams(paths_list, 2, counts, "bigram", document)

        for path, max_ord in sample_paths.items():
            if max_ord >= 2:
                presence_counts[path] = presence_counts.get(path, 0) + 1
    return presence_counts, filetypes, element_counts, counts.view("bigram"), {}, {}, skeleton_counts


def _vocab_db_batch_worker(
    args: tuple[Path | str, list[int]],
) -> tuple[dict[str, int], list[str], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int]]:
    """Fetch and count paths for a batch of IDs from the DB."""
    from . import data  # noqa: PLC0415 — deferred to avoid circular import in workers

    dsn, ids = args
    results = data.fetch_cleave_results(dsn, ids)
    return _vocab_batch_worker(list(results.values()))


# An extraction pool's workers all see the same spec, so each builds its
# context once, in the pool initializer, instead of per task: construction
# costs ~0.7s (the element x filetype lookups) against ~0.3s of real work
# in a 341-row task.
_worker_ctx: _ExtractContext | None = None
_worker_spec_identity: bytes | None = None


class MetadataExtractionPool:
    """Reuse processes across scoring calls, retaining only one spec per worker.

    Calls are consumed sequentially; each task carries its complete spec identity
    so equal-width, different-layout models can never share the wrong context.
    """

    def __init__(self, n_workers: int = 0):
        self.n_workers = resolve_worker_count(n_workers)
        self.pool = None
        self._manager = None

    def __enter__(self):
        if self.pool is not None:
            raise RuntimeError("metadata extraction pool is already open")
        self._manager = _feature_worker_pool(self.n_workers)
        self.pool = self._manager.__enter__()
        return self

    def __exit__(self, *exc):
        try:
            return self._manager.__exit__(*exc)
        finally:
            self.pool = None


def _extract_persistent_metadata_worker(args):
    global _worker_spec_identity
    identity, task = args
    started = time.monotonic()
    rebuilt = _worker_spec_identity != identity
    if rebuilt:
        _init_extract_worker(task[2])
        _worker_spec_identity = identity
    context_sec = time.monotonic() - started
    result = _extract_labeled_metadata_db_batch_worker(task)
    result[-1].update(context_sec=context_sec, context_rebuilt=int(rebuilt), worker_pid=os.getpid())
    return result


def _init_extract_worker(spec: FeatureSpec) -> None:
    global _worker_ctx
    _worker_ctx = _ExtractContext(spec)


@contextmanager
def _extract_pool(nw: int, spec: FeatureSpec) -> Iterator[ProcessPoolExecutor]:
    with _feature_worker_pool(nw, spec) as pool:
        yield pool


def _context(spec: FeatureSpec) -> _ExtractContext:
    if _worker_ctx is None:
        return _ExtractContext(spec)
    if _worker_ctx.total_features != spec.total_features:
        raise RuntimeError(
            f"extraction worker built for {_worker_ctx.total_features} features "
            f"got a task for {spec.total_features}",
        )
    return _worker_ctx


def _extract_batch_worker(
    args: tuple[int, list[tuple[dict[str, Any] | str, int]], FeatureSpec],
) -> tuple[list[int], list[int], list[float], list[int]]:
    """Extract features from a batch of (item, label) pairs. CPU-only."""
    offset, batch, spec = args
    ctx = _context(spec)
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


@contextmanager
def _feature_worker_pool(
    n_workers: int, spec: FeatureSpec | None = None,
    *, initializer: Callable | None = None, initargs: tuple = (),
) -> Iterator[ProcessPoolExecutor]:
    """Spawn feature workers without a nested numerical thread pool each.

    Set these before spawning, so NumPy/SciPy do not create their default
    machine-sized BLAS pools during import. Parent libraries are already
    loaded; restore its environment before the later model-training stage.
    """
    thread_vars = (
        "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
        "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS",
    )
    previous = {name: os.environ.get(name) for name in thread_vars}
    if os.environ.get("COLLIMATOR_PROFILE_DIR"):
        from .profiling import initialize_worker
        # Compose below, after the extraction initializer has been selected.
    if spec is not None:
        if initializer is not None:
            raise ValueError("spec and a custom worker initializer are mutually exclusive")
        initializer, initargs = _init_extract_worker, (spec,)
    if os.environ.get("COLLIMATOR_PROFILE_DIR"):
        initializer, initargs = initialize_worker, (initializer, initargs)
    try:
        for name in thread_vars:
            os.environ[name] = "1"
        with ProcessPoolExecutor(
            max_workers=n_workers, mp_context=mp.get_context("spawn"),
            initializer=initializer, initargs=initargs,
        ) as pool:
            yield pool
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


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


def ram_headroom_gb(reserve_gb: float) -> float | None:
    """GiB of RAM this process tree may still claim; None if meminfo is unreadable.

    Available host RAM (including reclaimable ZFS ARC) less ``reserve_gb`` for
    everything else on the box. When COLLIMATOR_MEM_CEILING_GB is set (the
    nightly sets it), headroom is also capped at that ceiling less the anonymous
    memory this process's cgroup already holds. Page cache is reclaimable, so
    it doesn't count against the ceiling.
    """
    available = available_memory_gb()
    if available is None:
        return None
    headroom = available - reserve_gb
    # ARC can take time to shrink. Stop launching batches when the kernel's
    # immediately available headroom is nearly gone, even if ARC is large.
    kernel_available = available_memory_gb(include_arc=False)
    minimum = float(os.getenv("COLLIMATOR_MEM_MIN_AVAILABLE_GB", "8"))
    if kernel_available is not None and kernel_available < minimum:
        headroom = 0.0
    if ceiling := os.getenv("COLLIMATOR_MEM_CEILING_GB"):
        try:
            headroom = min(headroom, float(ceiling) - _cgroup_anon_gb())
        except (OSError, ValueError, IndexError) as exc:
            log.warning("ignoring COLLIMATOR_MEM_CEILING_GB=%s: %s", ceiling, exc)
    cgroup_headroom = cgroup_headroom_gb()
    if cgroup_headroom is not None:
        headroom = min(headroom, cgroup_headroom)
    from .fit_resources import reserved_headroom_gb
    headroom -= reserved_headroom_gb()
    return max(0.0, headroom)


def _cgroup_anon_gb() -> float:
    """Anonymous memory held by this process's cgroup (v2), in GB."""
    cgroup = next(
        line.split("::", 1)[1].strip()
        for line in Path("/proc/self/cgroup").read_text().splitlines()
        if line.startswith("0::")
    )
    stat = (Path("/sys/fs/cgroup") / cgroup.lstrip("/") / "memory.stat").read_text()
    anon = next(int(line.split()[1]) for line in stat.splitlines() if line.startswith("anon "))
    return anon / 2**30


def clamp_workers_to_available_ram(n_workers: int, *, log_budget: bool = True,
                                   allow_zero: bool = False) -> int:
    """Best-effort cap on the DB-fetch worker count from currently-available RAM.

    Each concurrent fetch worker opens its own postgres backend and holds a
    fetch/count buffer, so on a co-tenanted host (hopper + scan) launching the
    full worker count when the box is *already* full is what tips it into a
    global OOM. This reads host RAM including reclaimable ZFS ARC at call time
    and clamps the resolved worker count so ``(available RAM - reserve)``
    covers the per-worker headroom. Vocabulary scheduling rechecks this budget
    during the pass; extraction takes a fresh snapshot after vocabulary completes.
    Linux-only; on any other platform or a parse failure it returns the
    request unchanged (never raises). Tune via COLLIMATOR_MEM_RESERVE_GB /
    COLLIMATOR_MEM_PER_WORKER_GB, or disable with COLLIMATOR_MEM_AWARE_WORKERS=0.

    Available RAM is read independently by every process that calls this, so N
    trainings launched concurrently each see the WHOLE box free and each admit
    a full worker count — an N-fold over-commit of the same RAM. An orchestrator
    that fans out (scripts/azoth_oof_pipeline.sh) must therefore export
    COLLIMATOR_MEM_SHARES=N, which divides the headroom into N equal budgets so
    the concurrent caps sum to what a single run would have taken.
    """
    resolved = resolve_worker_count(n_workers)
    if os.getenv("COLLIMATOR_MEM_AWARE_WORKERS", "1") == "0" or (resolved <= 1 and not allow_zero):
        return resolved
    try:
        reserve = float(os.getenv("COLLIMATOR_MEM_RESERVE_GB", "48"))
        per_worker = float(os.getenv("COLLIMATOR_MEM_PER_WORKER_GB", "2"))
        shares = max(1, int(os.getenv("COLLIMATOR_MEM_SHARES", "1")))
    except ValueError:
        return resolved
    headroom = ram_headroom_gb(reserve)
    if headroom is None:
        return resolved  # non-Linux or unparseable /proc/meminfo: leave as requested
    cap = max(0 if allow_zero else 1, int(headroom / shares // max(per_worker, 0.1)))
    share_note = f", shares={shares}" if shares > 1 else ""
    if cap < resolved:
        if log_budget:
            log.warning(
                "mem-aware workers: capping %d -> %d (headroom=%.0f GB after "
                "reserve=%.0f GB, per_worker=%.1f GB%s); tune via "
                "COLLIMATOR_MEM_RESERVE_GB / COLLIMATOR_MEM_PER_WORKER_GB or "
                "disable with COLLIMATOR_MEM_AWARE_WORKERS=0",
                resolved, cap, headroom, reserve, per_worker, share_note,
            )
        return cap
    if log_budget:
        log.info(
            "mem-aware workers: %d workers fit (headroom=%.0f GB after reserve=%.0f GB, "
            "per_worker=%.1f GB%s)",
            resolved, headroom, reserve, per_worker, share_note,
        )
    return resolved


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
    for f in report_files(report):
        if int(f.get("depth") or f.get("dp") or 0) == 0:
            formula = str(file_formula(f) or "")
            # Strip Unicode subscript digits ₀-₉ to match hopper.stripSubscripts.
            elements = "".join(c for c in formula if not ("₀" <= c <= "₉"))
            score = int(file_risk(f) or 0)
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
        with _extract_pool(nw, spec) as pool:
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
        with _extract_pool(nw, spec) as pool:
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


def _bounded_iter(pool: ProcessPoolExecutor, fn, it: Iterable,
                  *, max_inflight: int | Callable[[], int]) -> Iterator:
    """Submit tasks to pool with bounded concurrency, yielding results in order.

    Unlike pool.map(), which eagerly submits all tasks before any results are
    consumed, this keeps at most max_inflight tasks in flight at once. This
    bounds the amount of pickled task data queued in the IPC pipe and the
    number of raw-JSON strings materialised in the main process simultaneously.
    """
    if callable(max_inflight):
        yield from _bounded_ordered_dynamic_iter(pool, fn, it, max_inflight)
        return
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


_WORKER_BUDGET_REFRESH_SECONDS = 30.0


def _bounded_ordered_dynamic_iter(pool, fn, it, budget):
    """Drain under pressure, expand after recovery, and preserve row ordering."""
    pending = collections.deque()
    source = iter(it)
    sentinel = object()
    buffered = sentinel
    exhausted = False
    refresh_at = 0.0
    limit = 0
    while pending or not exhausted:
        now = time.monotonic()
        if now >= refresh_at:
            limit = max(0, int(budget()))
            refresh_at = now + _WORKER_BUDGET_REFRESH_SECONDS
        # Probe exhaustion even at zero budget; an empty iterator must finish.
        if buffered is sentinel and not exhausted:
            buffered = next(source, sentinel)
            exhausted = buffered is sentinel
        while len(pending) < limit and not exhausted:
            pending.append(pool.submit(fn, buffered))
            buffered = next(source, sentinel)
            exhausted = buffered is sentinel
        if pending:
            done, _ = wait([pending[0]], timeout=max(0, refresh_at - time.monotonic()),
                           return_when=FIRST_COMPLETED)
            if done:
                yield pending.popleft().result()
        elif not exhausted:
            time.sleep(max(0, refresh_at - time.monotonic()))


def _extraction_budget(n_workers):
    previous = None
    def budget():
        nonlocal previous
        current = clamp_workers_to_available_ram(n_workers, log_budget=previous is None,
                                                 allow_zero=True)
        if current != previous:
            log.info('extraction worker budget: %s -> %d/%d; preserving row order',
                     previous if previous is not None else 'initial', current, n_workers)
            previous = current
        return current
    return budget


def _bounded_unordered_iter(
    pool: ProcessPoolExecutor, fn, it: Iterable,
    *, max_inflight: int | Callable[[], int],
) -> Iterator:
    """Yield completed tasks, optionally refreshing their admission budget.

    Timed waits allow a growing budget to admit work even while the first
    batch is still running. A shrinking budget drains existing work before
    submitting replacements; running batches are never cancelled.
    """
    pending = set()
    source = iter(it)
    exhausted = False
    refresh_at = 0.0
    limit = max_inflight if isinstance(max_inflight, int) else 1
    sentinel = object()
    buffered = sentinel
    while pending or not exhausted:
        if callable(max_inflight) and time.monotonic() >= refresh_at:
            limit = max(0, max_inflight())
            refresh_at = time.monotonic() + _WORKER_BUDGET_REFRESH_SECONDS
        while not exhausted and len(pending) < limit:
            try:
                item = next(source) if buffered is sentinel else buffered
                buffered = sentinel
                pending.add(pool.submit(fn, item))
            except StopIteration:
                exhausted = True
        if not pending:
            if exhausted:
                return
            # Keep one input buffered to distinguish an empty source from a
            # paused pool; a zero budget must not silently discard queued work.
            if buffered is sentinel:
                try:
                    buffered = next(source)
                except StopIteration:
                    return
            time.sleep(max(0.0, refresh_at - time.monotonic()))
            continue
        timeout = max(0.0, refresh_at - time.monotonic()) if callable(max_inflight) else None
        done, _ = wait(pending, timeout=timeout, return_when=FIRST_COMPLETED)
        if done:
            future = next(iter(done))
            pending.remove(future)
            yield future.result()


def _memory_budgeted_unordered_iter(pool, fn, it, *, n_workers: int) -> Iterator:
    previous = None

    def budget():
        nonlocal previous
        admitted = clamp_workers_to_available_ram(n_workers, log_budget=previous is None,
                                                  allow_zero=True)
        if admitted != previous:
            log.info("vocab worker budget: %s -> %d/%d workers; rechecking every %.0fs",
                     previous if previous is not None else "initial", admitted, n_workers,
                     _WORKER_BUDGET_REFRESH_SECONDS)
            previous = admitted
        return admitted

    # With a pool sized for future growth, queuing 2*budget tasks could spawn
    # 2*budget workers. Admit only one task per budgeted worker.
    yield from _bounded_unordered_iter(pool, fn, it, max_inflight=budget)


def _memory_budgeted_serial_iter(fn, it) -> Iterator:
    """Sequential recovery must respect the same zero-worker admission floor."""
    for item in it:
        waiting = False
        while clamp_workers_to_available_ram(1, log_budget=False, allow_zero=True) == 0:
            if not waiting:
                log.info("vocab worker budget: 0/1 workers; waiting for memory")
                waiting = True
            time.sleep(_WORKER_BUDGET_REFRESH_SECONDS)
        if waiting:
            log.info("vocab worker budget: memory recovered; resuming 1 worker")
        yield fn(item)


def _extract_partitioned_batch_worker(
    args: tuple[int, int, list[tuple[dict[str, Any] | str, int, bool]], FeatureSpec],
) -> tuple[
    list[int], list[int], list[float], list[int],
    list[int], list[int], list[float], list[int],
]:
    """Extract train/test features from a mixed batch into separate sparse rows.

    Emits batch-LOCAL 0-based row indices; the leading offsets in ``args`` are
    accepted for caller compatibility but intentionally unused (see the row
    numbering note below).
    """
    _train_offset, _test_offset, batch, spec = args
    ctx = _context(spec)
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
        # Row indices are batch-LOCAL (0-based). Rows can be skipped mid-batch —
        # a report that fails to coerce (continue above), or an id dropped
        # because it was concurrently deleted before its fetch. Numbering by an
        # absolute (train_offset + position) base computed *before* extraction
        # desyncs from the actual extracted count the moment one row is skipped,
        # and _assemble_partitioned_matrices then rebases by its own running
        # total → the block's max row index exceeds its row count → scipy
        # raises "axis 0 index N exceeds matrix dimension N". Emitting local
        # 0-based indices keeps each block self-consistent; the assembler
        # vstacks blocks in order, so global row identity is preserved by order.
        if is_test:
            row = local_test
            local_test += 1
            test_rows.extend([row] * len(nz))
            test_cols.extend(nz.tolist())
            test_vals.extend(vec[nz].tolist())
            test_labels.append(label)
        else:
            row = local_train
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
    args: tuple[int, int, Path | str, list[tuple[int, int, bool]], FeatureSpec]
    | tuple[int, int, Path | str, list[tuple[int, int, bool]], FeatureSpec, bool],
) -> tuple[
    list[int], list[int], list[float], list[int],
    list[int], list[int], list[float], list[int],
] | tuple[
    tuple[list[int], list[int], list[float], list[int],
          list[int], list[int], list[float], list[int]],
    tuple[list[int], list[int], bytes],
]:
    """Fetch and extract train/test features for a batch of IDs from the DB."""
    from . import data  # noqa: PLC0415 — deferred to avoid circular import in workers

    train_offset, test_offset, dsn, batch_ids, spec, *capture = args
    ids = [rid for rid, _l, _t in batch_ids]
    if capture and capture[0]:
        reports_map = data.fetch_cleave_results(
            dsn, ids, evaluation_labels={rid: label for rid, label, test in batch_ids if test},
        )
        _check_missing_cleave_rows(ids, reports_map)
        kept = []
        for rid, label, test in batch_ids:
            if rid not in reports_map:
                continue
            report = _coerce_report(reports_map[rid]["cleave_result"])
            if report is not None:
                reports_map[rid]["cleave_result"] = report
                kept.append((rid, label, test))
        batch = [(reports_map[rid], label, test) for rid, label, test in kept]
        matrices = _extract_partitioned_batch_worker((train_offset, test_offset, batch, spec))
        return matrices, (
            [rid for rid, _, test in kept if not test],
            [rid for rid, _, test in kept if test],
            b"".join(reports_map[rid]["evaluation_digest"] for rid, _, test in kept if test),
        )
    reports_map = data.fetch_cleave_results(dsn, ids)

    batch = [
        (reports_map[rid], label, is_test)
        for rid, label, is_test in batch_ids
        if rid in reports_map
    ]
    return _extract_partitioned_batch_worker((train_offset, test_offset, batch, spec))


# A row selected into the corpus can vanish before this batch's fetch when
# hopper's cleanup/purge stages DELETE samples concurrently (pg.go
# purgeUnsupported / applyCleanup). Dropping the odd deleted row from a
# multi-hour full-corpus pass is correct — but a large fraction missing means
# something is actually wrong (wrong DB, truncated table), so still fail loudly
# there. Threshold is per-batch (batches are ~128 rows); a couple of concurrent
# deletes is <4%, a wrong DB is ~100%.
_MAX_MISSING_CLEAVE_FRACTION = 0.25


def _check_missing_cleave_rows(ids: list[int], reports_map: dict[int, Any]) -> None:
    """Tolerate a few concurrently-deleted rows; raise on mass loss."""
    missing = set(ids) - set(reports_map)
    if not missing:
        return
    frac = len(missing) / max(len(ids), 1)
    if frac > _MAX_MISSING_CLEAVE_FRACTION:
        raise ValueError(
            f"missing cleave_result rows during extraction: {len(missing)}/{len(ids)} "
            f"({frac:.0%}) exceeds {_MAX_MISSING_CLEAVE_FRACTION:.0%} — likely wrong DB "
            f"or mass deletion"
        )
    log.warning(
        "skipping %d/%d rows that vanished mid-run (concurrent hopper delete)",
        len(missing),
        len(ids),
    )


def _extract_labeled_db_batch_worker(
    args: tuple[int, Path | str, list[tuple[int, int]], FeatureSpec],
) -> tuple[list[int], list[int], list[float], list[int]]:
    """Fetch and extract one labeled batch from the DB."""
    from . import data  # noqa: PLC0415 — deferred to avoid circular import in workers

    offset, dsn, batch_ids, spec = args
    ids = [rid for rid, _label in batch_ids]
    reports_map = data.fetch_cleave_results(dsn, ids)
    _check_missing_cleave_rows(ids, reports_map)
    batch = [(reports_map[rid], label) for rid, label in batch_ids if rid in reports_map]
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
    _check_missing_cleave_rows(ids, reports_map)
    # Keep only rows still present, so the returned metadata stays aligned with
    # the extracted feature rows (the caller cross-checks their lengths).
    kept_meta = [row for row in batch_meta if int(row[0]) in reports_map]
    batch = [
        (reports_map[int(row[0])], int(row[4]))
        for row in kept_meta
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
    return kept_meta, rows, cols, vals, labels, stats


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
        with _extract_pool(nw, spec) as pool:
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
    worker_pool: MetadataExtractionPool | None = None,
) -> Iterator[tuple[list[LabeledMetadata], sp.csr_matrix, np.ndarray, dict[str, float | int]]]:
    """Yield DB-backed feature batches with metadata as workers complete.

    This is intended for full-corpus threshold/FP cache construction, where
    global row order is not meaningful as long as metadata, labels, and
    predictions stay aligned within each yielded batch.
    """
    nw = resolve_worker_count(n_workers)
    if worker_pool is not None:
        if worker_pool.pool is None:
            raise RuntimeError("metadata extraction pool is not open")
        nw = min(nw, worker_pool.n_workers)
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

    if worker_pool is not None:
        import pickle
        identity = hashlib.sha256(pickle.dumps(spec, protocol=5)).digest()
        for result in _bounded_unordered_iter(
            worker_pool.pool, _extract_persistent_metadata_worker,
            ((identity, task) for task in batch_args), max_inflight=2 * nw,
        ):
            yield _to_matrix(result)
        return

    if nw > 1:
        with _extract_pool(nw, spec) as pool:
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


def _vocab_labeled_db_batch_worker(args):
    dsn, ids_labels, *rest = args
    with VocabularyCounts(_batch_count_path(rest[0] if rest else None)) as counts:
        result = _count_labeled_vocab_batch(dsn, ids_labels, counts)
        if len(rest) > 1:
            counts.record_batch(rest[1], result, len(ids_labels))
        return result


# Keep fetched reports bounded to one batch, but combine repeated n-grams
# locally before the parent touches its much larger database. Rotate files
# independently of fetch size, with time/disk bounds for checkpoint latency.
_VOCAB_SHARD_BATCHES = 16
_vocab_shard_counts: VocabularyCounts | None = None
_vocab_shard_batches = 0
_vocab_shard_finalizer: Finalize | None = None
_vocab_shard_started = 0.0


def _vocab_shard_limit_reached(counts, batches, started):
    return (
        batches >= max(1, int(os.getenv("COLLIMATOR_VOCAB_SHARD_BATCHES", str(_VOCAB_SHARD_BATCHES))))
        or time.monotonic() - started >= 60
        or os.path.getsize(counts.path) >= 512 * 1024 * 1024
    )


def _active_vocab_shard(scratch):
    global _vocab_shard_counts, _vocab_shard_batches, _vocab_shard_finalizer, _vocab_shard_started
    if _vocab_shard_counts is None:
        _vocab_shard_counts = VocabularyCounts(_batch_count_path(scratch), defer_signatures=True)
        _vocab_shard_batches = 0
        _vocab_shard_started = time.monotonic()
        _vocab_shard_finalizer = Finalize(
            _vocab_shard_counts, _vocab_shard_counts.close, exitpriority=10,
        )
    return _vocab_shard_counts


def _finish_vocab_shard_batch():
    global _vocab_shard_counts, _vocab_shard_batches, _vocab_shard_finalizer
    _vocab_shard_batches += 1
    sealed = _vocab_shard_limit_reached(_vocab_shard_counts, _vocab_shard_batches, _vocab_shard_started)
    if sealed:
        _vocab_shard_counts.close()
        _vocab_shard_counts = None
        _vocab_shard_finalizer.cancel()
        _vocab_shard_finalizer = None
    return sealed


def _vocab_labeled_db_shard_worker(args):
    dsn, ids_labels, scratch, *batch_id = args
    counts = _active_vocab_shard(scratch)
    result = _count_labeled_vocab_batch(dsn, ids_labels, counts)
    if batch_id:
        counts.record_batch(batch_id[0], result, len(ids_labels))
    return result, _finish_vocab_shard_batch(), len(ids_labels)


def _vocab_benign_trigram_shard_worker(args):
    counts = _active_vocab_shard(args[3])
    result = _vocab_benign_trigram_worker(args, counts=counts)
    return result, _finish_vocab_shard_batch()


@timed('vocabulary.batch')
def _count_labeled_vocab_batch(dsn, ids_labels, counts):
    from . import data
    from .profiling import event

    ids = [rid for rid, _l in ids_labels]
    reports_map = data.fetch_cleave_results(dsn, ids)
    event("vocabulary.discovery", "rows", requested=len(ids), returned=len(reports_map))

    presence_counts: dict[str, int] = {}
    filetypes: set[str] = set()
    element_counts: dict[str, int] = {}
    benign_presence: dict[str, int] = {}
    malware_presence: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    benign_elements: dict[str, int] = {}
    malware_elements: dict[str, int] = {}
    config = feature_config_from_env()

    benign_ids = {rid for rid, label in ids_labels if label == 0}
    path_depth = config.trait_path_depth
    tiered_enabled = (
        config.include_tiered_crit_bigrams and config.tiered_bigram_max > 0
        or config.include_tiered_crit_trigrams and config.tiered_trigram_max > 0
    )
    branch_floors = _parse_branch_min_crit_overrides(config.tiered_bigram_branch_min_crit)
    def group(paths, order, family):
        if len(paths) >= order:
            counts.group_combinations(family, paths, order)

    def count_document(files, order, family, document):
        if len(files) == 1:
            # One selected token set per sample has no cross-file overlaps.
            # Count identical sets once, weighted by their distinct samples.
            group(next(iter(files)), order, family)
        else:
            for paths in files:
                _count_ngrams(paths, order, counts, family, document)

    for rid, item in reports_map.items():
        raw_report = item["cleave_result"]
        elements_str = item.get("elements", "")
        formula = item.get("formula", "")
        report = _coerce_report(raw_report)
        if report is None:
            continue
        malware = rid not in benign_ids
        ngrams_enabled = malware and (config.bigram_max > 0 or config.trigram_max > 0)
        need_scores = ngrams_enabled or malware and tiered_enabled

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

        seen_bigrams: set[tuple[str, ...]] = set()
        seen_trigrams: set[tuple[str, ...]] = set()
        sample_paths: dict[str, int] = {}
        path_scores: dict[str, float] = {}
        for file_entry in report_files(report):
            ftype = file_entry.get("type", "")
            if ftype:
                filetypes.add(ftype)

            file_path_scores: dict[str, float] = {}
            for finding in file_findings(file_entry):
                fid = finding_id(finding) or ""
                conf = _float(finding_conf(finding), MISSING_CONF)
                if not fid or conf < MIN_CONFIDENCE:
                    continue
                crit_ord = finding_crit(finding) or 0
                score = _finding_score(crit_ord, conf) if need_scores else 0.0
                if ngrams_enabled and conf >= MIN_CONFIDENCE and crit_ord >= NGRAM_MIN_CRIT:
                    path = fid.split("::")[0]
                    file_path_scores[path] = max(file_path_scores.get(path, 0.0), score)
                for path in _finding_paths(fid, path_depth):
                    if malware and tiered_enabled:
                        path_scores[path] = max(path_scores.get(path, 0.0), score)
                    if crit_ord > sample_paths.get(path, -1):
                        sample_paths[path] = crit_ord

            # Select the strongest paths before vocabulary filtering, exactly
            # as at serving time. Fixed budgets bound discovery combinations.
            if malware and config.bigram_max > 0:
                paths_list = _select_ngram_paths(file_path_scores, BIGRAM_MAX_PATHS)
                if len(paths_list) >= 2:
                    seen_bigrams.add(tuple(paths_list))
            # This family is malware-enriched: discover candidates from
            # positives, then measure only supported candidates on benigns.
            if malware and config.trigram_max > 0:
                tri_paths = _select_ngram_paths(file_path_scores, 128)
                if len(tri_paths) >= 3:
                    seen_trigrams.add(tuple(tri_paths))

        count_document(seen_bigrams, 2, "bigram", rid)
        count_document(seen_trigrams, 3, "trigram", rid)

        for path, max_ord in sample_paths.items():
            if max_ord >= 2:
                presence_counts[path] = presence_counts.get(path, 0) + 1
                if rid in benign_ids:
                    benign_presence[path] = benign_presence.get(path, 0) + 1
                else:
                    malware_presence[path] = malware_presence.get(path, 0) + 1

        if rid in benign_ids:
            continue

        if config.include_tiered_crit_bigrams and config.tiered_bigram_max > 0:
            tokens = _ranked_tiered_tokens(
                sample_paths, path_scores, order=2,
                min_crit=config.tiered_bigram_min_crit,
                branch_min_crit=branch_floors,
            )
            group(tokens, 2, "tiered_bigram")
        if config.include_tiered_crit_trigrams and config.tiered_trigram_max > 0:
            tokens = _ranked_tiered_tokens(
                sample_paths, path_scores, order=3,
                min_crit=config.tiered_trigram_min_crit,
                branch_min_crit=branch_floors,
            )
            group(tokens, 3, "tiered_trigram")

    def view(family):
        return counts.view(family, flush=not counts.path)

    return (
        presence_counts, sorted(filetypes), element_counts, view("bigram"),
        benign_presence, malware_presence, skeleton_counts,
        benign_elements, malware_elements, view("trigram"), view("benign_trigram"),
        view("tiered_bigram"), view("tiered_trigram"),
    )


def _trigram_candidate_index(candidates):
    by_first: dict[str, dict[str, set[str]]] = {}
    for candidate in candidates:
        a, b, c = candidate.split(" + ")
        by_first.setdefault(a, {}).setdefault(b, set()).add(c)
    return by_first


_worker_trigram_candidates: dict[str, dict[str, set[str]]] | DiskTrigramCandidates | None = None


def _init_trigram_candidates(candidates):
    global _worker_trigram_candidates
    _worker_trigram_candidates = (DiskTrigramCandidates(candidates)
                                  if isinstance(candidates, TrigramSource)
                                  else candidates if isinstance(candidates, dict)
                                  else _trigram_candidate_index(candidates))


@timed("vocabulary.benign_batch")
def _vocab_benign_trigram_worker(args, *, counts=None):
    """Count supported candidates without enumerating every benign triple."""
    from . import data
    from contextlib import nullcontext

    dsn, ids, candidates, scratch, *batch_id = args
    if candidates is None:
        by_first = _worker_trigram_candidates
        if by_first is None:
            raise RuntimeError("trigram candidate index was not initialized")
    else:
        if isinstance(candidates, (dict, DiskTrigramCandidates)):
            by_first = candidates
        else:
            by_first = _trigram_candidate_index(candidates)
    with (nullcontext(counts) if counts is not None
          else VocabularyCounts(_batch_count_path(scratch))) as counts:
        for rid, item in data.fetch_cleave_results(dsn, ids).items():
            report = _coerce_report(item["cleave_result"])
            if report is None:
                continue
            seen_files: set[tuple[str, ...]] = set()
            for file in report_files(report):
                paths = tuple(_ranked_ngram_paths(file, 128))
                if paths in seen_files:
                    continue
                seen_files.add(paths)
                if isinstance(by_first, DiskTrigramCandidates):
                    for triple in by_first.matches(paths):
                        counts.increment("benign_trigram", triple, document=rid)
                    continue
                present = set(paths)
                for a in present.intersection(by_first):
                    seconds = by_first[a]
                    for b in present.intersection(seconds):
                        for c in present.intersection(seconds[b]):
                            counts.increment("benign_trigram", (a, b, c), document=rid)
        if batch_id:
            counts.record_batch(batch_id[0], None, len(ids))
        return counts.view("benign_trigram", flush=not counts.path)


def vocabulary_identity(db_path: Path | str, row_ids_labels: Iterable[tuple[int, int]]) -> str:
    """Identify a selected training cohort without rereading live labels.

    Labels are fixed by selection and shared by vocabulary counting and feature
    extraction. Reports are read batch by batch; committed counts retain what
    their workers observed, even when the live reports subsequently change.
    This is a recovery identity, not an immutable database-content checksum.
    """
    from .cache_identity import code_revision

    identity = hashlib.sha256(f"selected-cohort-v1:{db_path}\n".encode())
    for row_id, label in row_ids_labels:
        identity.update(f"{row_id}:{label}\n".encode())
    config = feature_config_from_env()
    identity.update(json.dumps(
        {name: getattr(config, name) for name in config.__dataclass_fields__},
        sort_keys=True, default=sorted,
    ).encode())
    identity.update(code_revision("features").encode())
    return identity.hexdigest()


@timed('vocabulary.sample')
def _stable_vocab_scan_rows(row_ids_labels, limit=5000, *, chunk_size=262144):
    """Bottom-k row-ID hash sample, stable across ordering and corpus growth.

    Fixed-seed sampling of list positions reshuffles existing selections when
    a few rows arrive or disappear. A bijective uint64 mixer assigns each ID a
    fixed rank instead. Chunking bounds temporary memory for full-corpus runs.
    """
    if limit < 1 or chunk_size < 1:
        raise ValueError("sample limit and chunk size must be positive")
    best_keys = np.empty(0, dtype=np.uint64)
    best_indices = np.empty(0, dtype=np.int64)
    for start in range(0, len(row_ids_labels), chunk_size):
        stop = min(start + chunk_size, len(row_ids_labels))
        keys = np.fromiter((row_ids_labels[i][0] for i in range(start, stop)),
                           dtype=np.uint64, count=stop-start)
        # SplitMix64 finalization: fixed per-ID priorities, no RNG state.
        keys += np.uint64(0x9E3779B97F4A7C15)
        keys = (keys ^ (keys >> 30)) * np.uint64(0xBF58476D1CE4E5B9)
        keys = (keys ^ (keys >> 27)) * np.uint64(0x94D049BB133111EB)
        keys ^= keys >> 31
        indices = np.arange(start, stop, dtype=np.int64)
        keys = np.concatenate((best_keys, keys))
        indices = np.concatenate((best_indices, indices))
        selected = np.argpartition(keys, limit-1)[:limit] if len(keys) > limit else np.arange(len(keys))
        best_keys, best_indices = keys[selected], indices[selected]
    return [row_ids_labels[int(i)] for i in best_indices[np.argsort(best_keys)]]


@timed('vocabulary.total')
def build_vocab_from_db(db_path: Path | str, row_ids_labels: list[tuple[int, int]],
                        n_workers: int = 0, *, checkpoint_dir: Path | None = None,
                        shared_cache_dir: Path | None = None, row_folds: Iterable[int] | None = None) -> FeatureSpec:
    if (shared_cache_dir is None) != (row_folds is None):
        raise ValueError("shared vocabulary requires both cache directory and row folds")
    with _vocabulary_counts(checkpoint_dir) as (counts, scratch):
        if checkpoint_dir is not None:
            expected = vocabulary_identity(db_path, row_ids_labels)
            identity_path = checkpoint_dir / "identity"
            saved_identity = identity_path.read_text().strip() if identity_path.exists() else expected
            if saved_identity != expected or counts.state("identity", expected) != expected:
                raise ValueError("vocabulary checkpoint inputs changed; use a new checkpoint directory")
            counts.set_state("identity", expected)
            temporary_identity = identity_path.with_suffix(".tmp")
            temporary_identity.write_text(expected + "\n")
            os.replace(temporary_identity, identity_path)
        spec_path = checkpoint_dir / "feature_spec.json" if checkpoint_dir else None
        if spec_path is not None and spec_path.exists():
            log.info("resuming completed vocabulary: %s", spec_path)
            return FeatureSpec.load(spec_path)
        spec = _build_vocab_from_db(db_path, row_ids_labels, n_workers, counts, scratch,
                                   shared_cache_dir=shared_cache_dir, row_folds=row_folds)
        if spec_path is not None:
            temporary = spec_path.with_suffix(".tmp")
            spec.save(temporary)
            os.replace(temporary, spec_path)
        return spec


def _count_vocab_rows(db_path, row_ids_labels, n_workers, counts, scratch):
    config = feature_config_from_env()
    nw = resolve_worker_count(n_workers)
    presence_counts: dict[str, int] = {}
    filetypes: set[str] = set()
    element_counts: dict[str, int] = {}
    benign_presence: dict[str, int] = {}
    malware_presence: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    benign_elements: dict[str, int] = {}
    malware_elements: dict[str, int] = {}
    # The same checkpoint may resume with fewer workers. Preserve its batch
    # boundaries so completion IDs still refer to exactly the same input rows.
    batch_size = counts.state("batch_size", _feature_batch_size(nw))
    counts.set_state("batch_size", batch_size)
    pending_shards: dict[str, CountView] = {}
    merged_shards: set[str] = set()
    rows_counted = 0

    benign_total = sum(1 for _rid, label in row_ids_labels if label == 0)
    malware_total = len(row_ids_labels) - benign_total
    if config.bigram_max > 0 and config.bigram_min_freq > malware_total:
        log.warning("bigram_min_freq=%d exceeds %d malware training samples; "
                    "lower the cutoff to discover ordinary bigrams",
                    config.bigram_min_freq, malware_total)
    vocab_started = time.monotonic()
    last_progress = vocab_started
    def _merge_batch(
        path_counts: dict[str, int],
        fts: list[str],
        el_counts: dict[str, int],
        bi_counts: CountView,
        b_pres: dict[str, int],
        m_pres: dict[str, int],
        sk_counts: dict[str, int],
        b_els: dict[str, int],
        m_els: dict[str, int],
        tri_counts: dict[str, int],
        b_tris: dict[str, int],
        tier_bi_counts: CountView,
        tier_tri_counts: dict[str, int],
        *,
        n_rows: int | None = None,
        restoring: bool = False,
    ) -> None:
        nonlocal last_progress, rows_counted
        rows_counted += batch_size if n_rows is None else n_rows
        for k, v in path_counts.items():
            presence_counts[k] = presence_counts.get(k, 0) + v
        filetypes.update(fts)
        for k, v in el_counts.items():
            element_counts[k] = element_counts.get(k, 0) + v
        if restoring:
            pass
        elif nw > 1:
            # Results from one worker can be consumed out of order. A sealed
            # shard already includes its earlier batches, even if their small
            # singleton-count results have not reached the parent yet.
            if bi_counts.path not in merged_shards:
                pending_shards[bi_counts.path] = bi_counts
        else:
            counts.merge(bi_counts)
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
        now = time.monotonic()
        if batches_merged == 0 or now - last_progress >= 30:
            log.info(
                "vocab progress: %d/%d rows, %d batches, %.1fs elapsed",
                min(rows_counted, len(row_ids_labels)),
                len(row_ids_labels), batches_merged + 1, now - vocab_started,
            )
            last_progress = now

    # Counts spill to disk; never discard singletons between batches.
    batches_merged = 0
    completed = set()
    for batch_id, summary, n_rows in counts.completed_batches("count"):
        _merge_batch(*json.loads(summary), n_rows=n_rows, restoring=True)
        completed.add(batch_id)
        batches_merged += 1
    if completed:
        log.info("resuming vocabulary: %d committed batches, %d rows", len(completed), rows_counted)
    batch_args = (
        (db_path, batch, scratch, f"count:{i}")
        for i, batch in enumerate(_batched(row_ids_labels, batch_size))
        if f"count:{i}" not in completed
    )

    if nw > 1:
        with _background_vocab_merges(counts) as merge:
            with _feature_worker_pool(nw) as pool:
                for res, sealed, n_rows in _memory_budgeted_unordered_iter(
                    pool, _vocab_labeled_db_shard_worker, batch_args,
                    n_workers=nw,
                ):
                    _merge_batch(*res, n_rows=n_rows)
                    if sealed:
                        merge(pending_shards.pop(res[3].path))
                        merged_shards.add(res[3].path)
                    batches_merged += 1
        # A worker's last file may contain fewer than the shard limit. Wait for
        # pool shutdown before reading these files so no worker can still write
        # them. Full shards above are closed before their result is returned.
        from .profiling import profile
        merge_started = last_merge_progress = time.monotonic()
        for i, view in enumerate(pending_shards.values(), 1):
            with profile("vocab-merge"):
                counts.merge(view)
            now = time.monotonic()
            if i == 1 or i == len(pending_shards) or now - last_merge_progress >= 30:
                log.info("vocab final merge: %d/%d shards, %.1fs elapsed",
                         i, len(pending_shards), now - merge_started)
                last_merge_progress = now
    else:
        for res in _memory_budgeted_serial_iter(_vocab_labeled_db_batch_worker, batch_args):
            _merge_batch(*res)
            batches_merged += 1

    log.info("vocab counting complete: %d rows, %d batches, %.1fs elapsed",
             len(row_ids_labels), batches_merged, time.monotonic() - vocab_started)

    return (presence_counts, sorted(filetypes), element_counts, None, benign_presence,
            malware_presence, skeleton_counts, benign_elements, malware_elements, None, None, None, None)


def _published_fold_counts(db_path, rows, n_workers, root):
    """Publish one immutable, resumable discovery-count database per cohort.

    The key includes selected labels, configuration and feature code. It is a
    captured training input, not a claim that the live database is immutable.
    No vocabulary threshold or benign-candidate filtering runs in this cache.
    """
    key = vocabulary_identity(db_path, rows)
    directory = Path(root) / key
    directory.mkdir(parents=True, exist_ok=True)
    published = directory / "discovery.sqlite"
    with (directory / "publish.lock").open("w") as lock:
        # Competing production/fold trainers consume the first completed copy.
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            log.info("shared vocabulary: waiting for matching fold (%d rows, %s)", len(rows), key[:12])
            fcntl.flock(lock, fcntl.LOCK_EX)
        if published.is_file():
            log.info("shared vocabulary: reuse %d discovery rows (%s)", len(rows), key[:12])
            return published
        work = directory / "work"
        with _vocabulary_counts(work) as (fold_counts, scratch):
            if not fold_counts.state("shared_export_ready", False):
                log.info("shared vocabulary: count %d discovery rows (%s)", len(rows), key[:12])
                summary = _count_vocab_rows(db_path, rows, n_workers, fold_counts, scratch)
                fold_counts.materialize()
                # Replacing worker receipts and marking readiness is atomic.
                # A restart after this commit must publish, never recount.
                fold_counts.db.execute("DELETE FROM batches")
                fold_counts.record_batch(f"shared:{key}", summary, len(rows))
                fold_counts.set_state("shared_export_ready", True)
        # Closing the last connection checkpoints WAL. Move the closed DB
        # instead of copying potentially gigabytes of expanded counts.
        os.replace(work / "counts.sqlite", published)
        directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        log.info("shared vocabulary: published %d discovery rows (%s)", len(rows), key[:12])
    return published


def _shared_fold_counts(db_path, rows, row_folds, n_workers, counts, root):
    """Build fold-local raw counts once; combine only the requested cohorts."""
    import sqlite3

    folds = {0: [], 1: []}
    for row, fold in zip(rows, row_folds, strict=True):
        if fold not in folds:
            raise ValueError("shared vocabulary requires training folds 0 or 1")
        folds[fold].append(row)
    summary = [{}, set(), {}, None, {}, {}, {}, {}, {}, None, None, None, None]
    for fold, selected in folds.items():
        if not selected:
            continue
        published = _published_fold_counts(db_path, selected, n_workers, root)
        # Published files are never opened for writing or removed by consumers.
        with sqlite3.connect(published.resolve().as_uri() + "?mode=ro", uri=True) as db:
            row = db.execute("SELECT summary,n_rows FROM batches WHERE id LIKE 'shared:%'").fetchone()
            if row is None or row[1] != len(selected):
                raise ValueError("shared vocabulary receipt does not match selected rows")
            values = json.loads(row[0])
        counts.attach_shared(CountView(str(published), "bigram"))
        summary[1].update(values[1])
        for index in (0, 2, 4, 5, 6, 7, 8):
            for key, value in values[index].items():
                summary[index][key] = summary[index].get(key, 0) + value
        log.info("shared vocabulary: fold %d attached read-only (%d rows)", fold, len(selected))
    summary[1] = sorted(summary[1])
    return tuple(summary)


@timed("vocabulary.benign_filter")
def _count_benign_prevalence(db_path, benign_ids, nw, counts, scratch, source, prefix, batch_size):
    """Count one candidate set; batch receipts and counts commit together."""
    done = {row[0] for row in counts.completed_batches(prefix)}
    total = (len(benign_ids) + batch_size - 1) // batch_size
    processed = len(done)
    log.info("trigram prevalence %s: %d benign rows, %d/%d batches resumed",
             prefix, len(benign_ids), processed, total)
    if processed == total:
        return
    started = last_progress = time.monotonic()

    def progress():
        nonlocal processed, last_progress
        processed += 1
        now = time.monotonic()
        if now - last_progress >= 30 or processed == total:
            log.info("trigram prevalence %s: %d/%d batches processed, %.1fs elapsed",
                     prefix, processed, total, now - started)
            last_progress = now

    if nw > 1:
        args = ((db_path, batch, None, scratch, f"{prefix}:{i}")
                for i, batch in enumerate(_batched(benign_ids, batch_size))
                if f"{prefix}:{i}" not in done)
        pending, merged = {}, set()
        with _background_vocab_merges(counts) as merge:
            with _feature_worker_pool(nw, initializer=_init_trigram_candidates, initargs=(source,)) as pool:
                for result, sealed in _memory_budgeted_unordered_iter(
                    pool, _vocab_benign_trigram_shard_worker, args, n_workers=nw,
                ):
                    if result.path not in merged:
                        pending[result.path] = result
                    if sealed:
                        merge(pending.pop(result.path))
                        merged.add(result.path)
                    progress()
            for result in pending.values():
                merge(result)
    else:
        index = DiskTrigramCandidates(source) if isinstance(source, TrigramSource) else source
        try:
            args = ((db_path, batch, index, scratch, f"{prefix}:{i}")
                    for i, batch in enumerate(_batched(benign_ids, batch_size))
                    if f"{prefix}:{i}" not in done)
            for result in _memory_budgeted_serial_iter(_vocab_benign_trigram_worker, args):
                counts.merge(result)
                progress()
        finally:
            if isinstance(index, DiskTrigramCandidates):
                index.close()


@timed("vocabulary.trigram_selection")
def _select_trigram_vocabulary(db_path, benign_ids, nw, counts, scratch, *,
                               limit, minimum, benign_ceiling, batch_size):
    """Filter consecutive exact rank pages until enough candidates survive.

    Every unseen candidate ranks after the current page, including lexical
    frequency ties. Once K survive, none of the unseen candidates can replace
    them. Only tested candidates get benign counts; never run an unrestricted
    top-k against the missing (untested) counts.
    """
    if limit <= 0:
        return []
    mode = "exhaustive" if os.getenv("COLLIMATOR_TRIGRAM_SHORTLIST", "1") == "0" else "shortlist"
    if counts.state("trigram_filter_mode", mode) != mode:
        raise ValueError("trigram filtering mode changed; use a new checkpoint")
    counts.set_state("trigram_filter_mode", mode)
    if mode == "exhaustive":
        if counts.count_at_least("trigram", minimum):
            _count_benign_prevalence(db_path, benign_ids, nw, counts, scratch,
                                    TrigramSource(counts.path, minimum), "benign", batch_size)
        return counts.top("trigram", limit, minimum, benign_family="benign_trigram",
                          benign_ceiling=benign_ceiling)
    page_size = int(os.getenv("COLLIMATOR_TRIGRAM_SHORTLIST_SIZE", "4096"))
    if not 1 <= page_size <= 65536:
        raise ValueError("trigram shortlist size must be between 1 and 65536")
    parameters = [limit, minimum, benign_ceiling, len(benign_ids), batch_size]
    state = counts.state("trigram_selection", dict(parameters=parameters, accepted=[],
                         after=None, round=0, tested=0, complete=False))
    if state["parameters"] != parameters:
        raise ValueError("trigram shortlist inputs changed; use a new checkpoint")
    while not state["complete"]:
        if state.get("fallback"):
            _count_benign_prevalence(db_path, benign_ids, nw, counts, scratch,
                                    TrigramSource(counts.path, minimum), "benign-fallback", batch_size)
            state.update(accepted=counts.top("trigram", limit, minimum,
                         benign_family="benign_trigram", benign_ceiling=benign_ceiling), complete=True)
            counts.set_state("trigram_selection", state)
            break
        if "page" not in state:
            if state["round"] >= 4:
                # Bound rereads when nearly every leading candidate is benign.
                # Clear earlier subset counts atomically with the fallback
                # marker; exhaustive counting must not add to those counts.
                log.info("trigram shortlist: few candidates survived %d rounds; falling back to exhaustive filtering",
                         state["round"])
                try:
                    counts.db.execute("DELETE FROM counts WHERE family='benign_trigram'")
                    counts.db.execute("DELETE FROM batches WHERE id LIKE 'benign-shortlist-%'")
                    state["fallback"] = True
                    counts.set_state("trigram_selection", state)
                except BaseException:
                    counts.db.rollback()
                    raise
                continue
            page = counts.ranked_page("trigram", min(65536, page_size * (2 ** state["round"])), minimum, state["after"])
            state["page"] = [(key.hex(), n) for key,n in page]
            counts.set_state("trigram_selection", state)
        page = [(bytes.fromhex(key), n) for key,n in state["page"]]
        if not page:
            state["complete"] = True
            counts.set_state("trigram_selection", state)
            break
        candidates = {}
        for key, _ in page:
            a, b, c = counts.token_parts(key)
            candidates.setdefault(a, {}).setdefault(b, set()).add(c)
        log.info("trigram shortlist: round %d, %d candidates, %d/%d accepted so far",
                 state["round"] + 1, len(page), len(state["accepted"]), limit)
        _count_benign_prevalence(db_path, benign_ids, nw, counts, scratch, candidates,
                                f"benign-shortlist-{state['round']}", batch_size)
        for key, _ in page:
            row = counts.db.execute("SELECT n FROM counts WHERE family='benign_trigram' AND token=?", (key,)).fetchone()
            if (row[0] if row else 0) <= benign_ceiling:
                state["accepted"].append(" + ".join(counts.token_parts(key)))
                if len(state["accepted"]) == limit:
                    break
        key, n = page[-1]
        state.update(after=[n, " + ".join(counts.token_parts(key)), key.hex()],
                     round=state["round"] + 1, tested=state["tested"] + len(page),
                     complete=len(state["accepted"]) == limit)
        del state["page"]
        counts.set_state("trigram_selection", state)
        from .profiling import event
        event("vocabulary.trigram_shortlist", "round", candidates=len(page),
              tested=state["tested"], accepted=len(state["accepted"]), complete=state["complete"])
    log.info("trigram selection complete: %d shortlist candidates tested, %d selected, %d rounds, exhaustive fallback=%s",
             state["tested"], len(state["accepted"]), state["round"], state.get("fallback", False))
    return sorted(state["accepted"])


def _build_vocab_from_db(db_path, row_ids_labels, n_workers, counts, scratch, *,
                         shared_cache_dir=None, row_folds=None) -> FeatureSpec:
    config = feature_config_from_env()
    nw = resolve_worker_count(n_workers)
    mode = "shared-folds-readonly" if shared_cache_dir is not None else "independent"
    if counts.state("counting_mode", mode) != mode:
        raise ValueError("vocabulary counting mode changed; use a new checkpoint directory")
    counts.set_state("counting_mode", mode)
    if shared_cache_dir is None:
        summary = _count_vocab_rows(db_path, row_ids_labels, n_workers, counts, scratch)
    else:
        summary = _shared_fold_counts(db_path, row_ids_labels, row_folds, n_workers,
                                      counts, shared_cache_dir)
    (presence_counts, filetypes, element_counts, _, benign_presence, malware_presence,
     skeleton_counts, benign_elements, malware_elements, _, _, _, _) = summary
    batch_size = counts.state("batch_size", _feature_batch_size(nw))
    counts.set_state("batch_size", batch_size)
    benign_total = sum(label == 0 for _, label in row_ids_labels)
    malware_total = len(row_ids_labels) - benign_total
    # Keep existing sampled IDs stable when a few training rows change.
    scan_rows = _stable_vocab_scan_rows(row_ids_labels)
    scan_digest = hashlib.sha256(np.asarray([r[0] for r in scan_rows], dtype="<u8").tobytes()).hexdigest()
    log.info("auxiliary vocabulary sample: %d rows, ID digest=%s", len(scan_rows), scan_digest)

    presence_vocab = sorted(k for k, c in presence_counts.items() if c >= MIN_PATH_FREQ)
    filetype_vocab = sorted(filetypes)
    element_vocab = sorted(k for k, c in element_counts.items() if c >= MIN_PATH_FREQ)
    # Bigram/trigram vocab sizes are controlled by FeatureConfig (which reads
    # from env vars) so they're included in the matrix cache key.
    bigram_vocab = counts.top("bigram", config.bigram_max, config.bigram_min_freq)
    skeleton_vocab = sorted(k for k, c in skeleton_counts.items() if c >= 100)

    trigram_benign_ceil = int(config.trigram_max_benign_frac * benign_total) if config.trigram_max_benign_frac > 0 else 0
    trigram_vocab = _select_trigram_vocabulary(
        db_path, [rid for rid, label in row_ids_labels if label == 0], nw, counts, scratch,
        limit=config.trigram_max, minimum=config.trigram_min_freq,
        benign_ceiling=trigram_benign_ceil, batch_size=batch_size,
    )
    tiered_bigram_vocab = counts.top("tiered_bigram", config.tiered_bigram_max, config.tiered_bigram_min_freq)
    tiered_trigram_vocab = counts.top("tiered_trigram", config.tiered_trigram_max, config.tiered_trigram_min_freq)

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
        reduced = False  # whether any scanned report carries cleave's fact profile
        # Scan a random subset for speed (5000 rows is enough to find common keys).
        scan_ids = [rid for rid, _l in scan_rows]
        for start in range(0, len(scan_ids), 500):
            chunk = scan_ids[start:start + 500]
            for _rid, item in _data.fetch_cleave_results(db_path, chunk).items():
                report = _coerce_report(item["cleave_result"])
                if report is None:
                    continue
                reduced = reduced or report.get("fp") is not None
                report_metric_keys: set[str] = set()
                for file_entry in report_files(report):
                    ms = file_metrics(file_entry)
                    for group, fields in ms.items():
                        if not isinstance(fields, dict):
                            continue
                        for k, v in fields.items():
                            if isinstance(v, (int, float)):
                                mk = f"{group}_{k}"
                                report_metric_keys.add(mk)
                for mk in report_metric_keys:
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

        def _passes_prefix(k: str) -> bool:
            return not prefixes or any(k.startswith(p) for p in prefixes)

        # Frequency-selected keys, plus the always-keep allowlist (which bypasses
        # the threshold but still respects base_keys and the prefix filter). The
        # allowlist reserves the slot even when the scan sample never saw the key
        # — exactly the case for a rare anti-analysis signal.
        # On a corpus with reduced reports, offer only metrics the fact profile
        # retains: those reports carry no others, so a column for one would be
        # zero on every reduced row. To offer a new metric there, add it to
        # cleave's profile first.
        retained = frozenset(_fact_profile_manifest()["metrics"]) if reduced else None
        kept = {
            k for k, c in metric_key_counts.items()
            if c >= threshold and k not in base_keys and _passes_prefix(k)
            and (retained is None or k in retained)
        }
        forced = {
            k for k in ALWAYS_KEEP_METRICS
            if k not in base_keys and _passes_prefix(k)
        }
        metric_vocab = sorted(kept | forced)
        forced_present = sorted(forced - kept)
        log.info("extended metrics: %d keys from %d scanned rows%s%s",
                 len(metric_vocab), len(scan_ids),
                 f" (filtered by prefixes: {','.join(prefixes)})" if prefixes else "",
                 f" (always-keep below threshold: {','.join(forced_present)})" if forced_present else "")

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
        scan_ids_labels = scan_rows
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
                    for finding in file_findings(fe):
                        fid = finding_id(finding) or ""
                        if not fid or _float(finding_conf(finding), MISSING_CONF) < MIN_CONFIDENCE:
                            continue
                        for path in _finding_paths(fid, config.trait_path_depth):
                            crit_ord = finding_crit(finding) or 0
                            if crit_ord > sp.get(path, -1):
                                sp[path] = crit_ord
                tokens = _crit_category_tokens(sp)
                is_benign = rid in benign_scan_ids
                for t in tokens:
                    crit_uni_counts[t] = crit_uni_counts.get(t, 0) + 1
                for i, t1 in enumerate(tokens):
                    for t2 in tokens[i + 1:]:
                        bi = f"{t1} + {t2}"
                        if not is_benign:
                            crit_bi_counts[bi] = crit_bi_counts.get(bi, 0) + 1
                        if is_benign:
                            crit_bi_benign[bi] = crit_bi_benign.get(bi, 0) + 1
                    for j in range(i + 1, len(tokens)):
                        t2 = tokens[j]
                        for t3 in tokens[j + 1:]:
                            tri = f"{t1} + {t2} + {t3}"
                            if not is_benign:
                                crit_tri_counts[tri] = crit_tri_counts.get(tri, 0) + 1
                            if is_benign:
                                crit_tri_benign[tri] = crit_tri_benign.get(tri, 0) + 1

        n_scan = len(scan_ids_labels)
        benign_frac = 0.01  # allow ≤1% benign
        n_benign_scan = len(benign_scan_ids)
        benign_ceil = int(benign_frac * n_benign_scan)

        crit_unigram_vocab = sorted(k for k, c in crit_uni_counts.items() if c >= 10)
        crit_bigram_vocab = sorted(
            sorted(
                (k for k, c in crit_bi_counts.items()
                 if c >= 5 and crit_bi_benign.get(k, 0) <= benign_ceil),
                key=lambda k: (-crit_bi_counts[k], k),
            )[:500]
        )
        crit_trigram_vocab = sorted(
            sorted(
                (k for k, c in crit_tri_counts.items()
                 if c >= 3 and crit_tri_benign.get(k, 0) <= benign_ceil),
                key=lambda k: (-crit_tri_counts[k], k),
            )[:500]
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
        scan_ids_labels = scan_rows
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
                    for finding in file_findings(fe):
                        a = finding_attack(finding)
                        if a:
                            attacks.add(a)
                        m = finding_mbc(finding)
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
                        if not is_benign:
                            atk_bi_counts[bi] = atk_bi_counts.get(bi, 0) + 1
                        if is_benign:
                            atk_bi_benign[bi] = atk_bi_benign.get(bi, 0) + 1
                        for a3 in sorted_a[j + 1:]:
                            tri = f"{a1} + {a2} + {a3}"
                            if not is_benign:
                                atk_tri_counts[tri] = atk_tri_counts.get(tri, 0) + 1
                # MBC bigrams/trigrams
                sorted_m = sorted(mbcs)
                for i, m1 in enumerate(sorted_m):
                    for j in range(i + 1, len(sorted_m)):
                        m2 = sorted_m[j]
                        bi = f"{m1} + {m2}"
                        if not is_benign:
                            mbc_bi_counts[bi] = mbc_bi_counts.get(bi, 0) + 1
                        if is_benign:
                            mbc_bi_benign[bi] = mbc_bi_benign.get(bi, 0) + 1
                        for m3 in sorted_m[j + 1:]:
                            tri = f"{m1} + {m2} + {m3}"
                            if not is_benign:
                                mbc_tri_counts[tri] = mbc_tri_counts.get(tri, 0) + 1

        n_benign_scan = len(benign_scan)
        benign_ceil = int(0.01 * n_benign_scan)
        if config.include_attack_code_ngrams:
            attack_bigram_vocab = sorted(
                sorted(
                    (k for k, c in atk_bi_counts.items()
                     if c >= 5 and atk_bi_benign.get(k, 0) <= benign_ceil),
                    key=lambda k: (-atk_bi_counts[k], k),
                )[:500]
            )
            attack_trigram_vocab = sorted(
                k for k, c in sorted(atk_tri_counts.items(), key=lambda x: (-x[1], x[0]))[:500]
                if c >= 3
            )
            mbc_bigram_vocab = sorted(
                sorted(
                    (k for k, c in mbc_bi_counts.items()
                     if c >= 5 and mbc_bi_benign.get(k, 0) <= benign_ceil),
                    key=lambda k: (-mbc_bi_counts[k], k),
                )[:500]
            )
            mbc_trigram_vocab = sorted(
                k for k, c in sorted(mbc_tri_counts.items(), key=lambda x: (-x[1], x[0]))[:500]
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
                k for k, c in sorted(mbc_unigram_counts.items(), key=lambda x: (-x[1], x[0]))[:500]
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
        kv_counts: dict[str, int] = {}
        scan_ids = [rid for rid, _l in scan_rows]
        malware_scan_ids = {rid for rid, label in scan_rows if label == 1}
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
                    if config.include_symbol_bigrams and _rid in malware_scan_ids:
                        report_symbol_bigrams.update(_file_symbol_bigrams(file_entry))
                    if config.include_symbol_trigrams and _rid in malware_scan_ids:
                        report_symbol_trigrams.update(_file_symbol_trigrams(file_entry))
                    if config.include_kv_vocab:
                        report_kvs.update(
                            _metric_kv_tokens(
                                file_entry,
                                include_shape=config.include_kv_shape_features,
                                split_string_values=config.include_kv_value_split,
                            )
                        )
                if (_rid in malware_scan_ids and config.include_tiered_crit_quadgrams
                        and config.tiered_quadgram_max > 0):
                    # Tiered quadgrams: one per report (not per file). Use the
                    # already-summarized sample_paths via _summarize_report_files.
                    quad_summary = _summarize_report_files(report_files(report))
                    tokens = _ranked_tiered_tokens(
                        quad_summary.sample_paths, quad_summary.path_scores, order=4,
                        min_crit=config.tiered_quadgram_min_crit,
                        branch_min_crit=_parse_branch_min_crit_overrides(config.tiered_bigram_branch_min_crit),
                    )
                    _count_ngrams(tokens, 4, counts, "tiered_quadgram", _rid)
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
                k for k, c in sorted(symbol_counts.items(), key=lambda x: (-x[1], x[0]))[:config.symbol_vocab_max]
                if c >= config.symbol_min_freq
            )
            log.info("symbol vocab: %d entries from %d scanned rows", len(symbol_vocab), len(scan_ids))
        if config.include_symbol_bigrams:
            symbol_bigram_vocab = sorted(
                k for k, c in sorted(symbol_bigram_counts.items(), key=lambda x: (-x[1], x[0]))[:config.symbol_bigram_max]
                if c >= config.symbol_min_freq_bigram
            )
            log.info("symbol bigram vocab: %d entries (cap=%d/file) from %d scanned rows",
                     len(symbol_bigram_vocab), _SYMBOL_BIGRAM_CAP, len(scan_ids))
        if config.include_symbol_trigrams:
            symbol_trigram_vocab = sorted(
                k for k, c in sorted(symbol_trigram_counts.items(), key=lambda x: (-x[1], x[0]))[:config.symbol_trigram_max]
                if c >= config.symbol_min_freq_trigram
            )
            log.info("symbol trigram vocab: %d entries (cap=%d/file) from %d scanned rows",
                     len(symbol_trigram_vocab), _SYMBOL_TRIGRAM_CAP, len(scan_ids))
        if config.include_kv_vocab:
            kv_vocab = sorted(
                k for k, c in sorted(kv_counts.items(), key=lambda x: (-x[1], x[0]))[:config.kv_vocab_max]
                if c >= config.kv_min_freq
            )
            log.info("kv vocab: %d entries from %d scanned rows", len(kv_vocab), len(scan_ids))
        if config.include_tiered_crit_quadgrams and config.tiered_quadgram_max > 0:
            tiered_quadgram_vocab = counts.top("tiered_quadgram", config.tiered_quadgram_max, config.tiered_quadgram_min_freq)
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
        trait_path_depth=config.trait_path_depth,
        tiered_min_crit=(config.tiered_bigram_min_crit, config.tiered_trigram_min_crit, config.tiered_quadgram_min_crit),
        tiered_branch_min_crit=_parse_branch_min_crit_overrides(config.tiered_bigram_branch_min_crit),
    )
    log.info(
        "vocab: %d paths, %d filetypes, %d elements, %d bigrams, %d ghosts, %d ext_metrics -> %d features",
        len(presence_vocab), len(filetype_vocab), len(element_vocab), len(bigram_vocab),
        len(ghost_vocab), len(metric_vocab), spec.total_features,
    )
    return spec


def _assemble_partitioned_matrices(
    batch_iter: Iterable[tuple[
        list[int], list[int], list[float], list[int],
        list[int], list[int], list[float], list[int],
    ]],
    total_features: int,
) -> tuple[sp.csr_matrix, np.ndarray, sp.csr_matrix, np.ndarray]:
    """Assemble (X_train, y_train, X_test, y_test) from a stream of worker batches.

    Each batch is the 8-tuple emitted by ``_extract_partitioned_batch_worker``:
    ``(train_rows, train_cols, train_vals, train_labels, test_rows, ...)`` where
    the ``rows`` are batch-LOCAL 0-based indices. Global row identity is carried
    by block order (blocks vstack in the same order labels concatenate), NOT by
    the index values — so a batch that dropped rows (concurrent delete, or a
    report that failed to coerce) still stacks correctly.

    Rather than accumulating raw COO triplets and a final ``np.concatenate``
    (which holds the chunk lists, the concatenated copy, and the built CSR all at
    once — ~32 bytes/nnz), we convert each small batch to a CSR block and
    ``vstack`` at the end. CSR drops the per-nnz row array the COO path carried,
    so peak construction memory is ~16 bytes/nnz — roughly half. ``vstack`` also
    lets scipy size the result's index dtype, promoting to int64 once nnz crosses
    2^31 (general is already at ~1.5B of that 2.15B ceiling).

    Relies on ``batch_iter`` arriving in enumeration order (``_bounded_iter`` is
    ordered) so the running offsets match each batch's global row base.
    """
    empty = sp.csr_matrix((0, total_features), dtype=np.float32)

    def _block(rows: list[int], cols: list[int], vals: list[float], n_rows: int) -> sp.csr_matrix:
        # Rows are already batch-local 0-based (see _extract_partitioned_batch_worker),
        # so a block is self-consistent regardless of how many rows earlier batches
        # dropped. Global row identity comes from vstack order, not the indices.
        local = np.asarray(rows, dtype=np.int64) if rows else np.empty(0, dtype=np.int64)
        return sp.csr_matrix(
            (
                np.asarray(vals, dtype=np.float32),
                (local, np.asarray(cols, dtype=np.int64)),
            ),
            shape=(n_rows, total_features),
        )

    if directory := os.getenv('COLLIMATOR_MATRIX_DISK_DIR'):
        from .matrix_store import MatrixWriter
        train_writer = MatrixWriter(directory, total_features)
        try:
            test_writer = MatrixWriter(directory, total_features)
            try:
                for tr, tc, tv, tl, ter, tec, tev, tel in batch_iter:
                    if len(tl):
                        train_writer.append(_block(tr, tc, tv, len(tl)), tl)
                    if len(tel):
                        test_writer.append(_block(ter, tec, tev, len(tel)), tel)
                X_train, y_train = train_writer.finish()
                X_test, y_test = test_writer.finish()
                return X_train, y_train, X_test, y_test
            finally:
                test_writer.close()
        finally:
            train_writer.close()

    train_blocks: list[sp.csr_matrix] = []
    test_blocks: list[sp.csr_matrix] = []
    train_labels: list[np.ndarray] = []
    test_labels: list[np.ndarray] = []
    for (tr, tc, tv, tl, ter, tec, tev, tel) in batch_iter:
        n_tr = len(tl)
        n_te = len(tel)
        if n_tr:
            train_blocks.append(_block(tr, tc, tv, n_tr))
            train_labels.append(np.asarray(tl, dtype=np.float32))
        if n_te:
            test_blocks.append(_block(ter, tec, tev, n_te))
            test_labels.append(np.asarray(tel, dtype=np.float32))

    X_train = sp.vstack(train_blocks, format="csr") if train_blocks else empty.copy()
    X_test = sp.vstack(test_blocks, format="csr") if test_blocks else empty.copy()
    y_train = np.concatenate(train_labels) if train_labels else np.array([], dtype=np.float32)
    y_test = np.concatenate(test_labels) if test_labels else np.array([], dtype=np.float32)
    return X_train, y_train, X_test, y_test


@timed('features.extract')
def extract_partitioned_from_db(
    db_path: Path | str,
    train_ids_labels: list[tuple[int, int]],
    test_ids_labels: list[tuple[int, int]],
    spec: FeatureSpec,
    n_workers: int = 0,
    *,
    identity: dict[str, Any] | None = None,
) -> tuple[sp.csr_matrix, np.ndarray, sp.csr_matrix, np.ndarray]:
    """Extract features and optionally fill identities of the rows actually read.

    ``identity`` receives aligned train/test row IDs and an evaluation revision
    captured alongside reports, without pre/post scans of the live database.
    """
    nw = resolve_worker_count(n_workers)
    batch_size = _feature_batch_size(nw)

    # Combine all IDs into one mixed stream for partitioned extraction.
    mixed_ids = (
        [(rid, label, False) for rid, label in train_ids_labels] +
        [(rid, label, True) for rid, label in test_ids_labels]
    )
    # Sort to ensure predictable row assignment if needed (not strictly required for sparse).
    mixed_ids.sort(key=lambda x: x[0])

    batch_args = (
        (train_offset, test_offset, db_path, batch, spec, identity is not None)
        for train_offset, test_offset, batch in _enumerate_partitioned_batches(
            mixed_ids,
            batch_size,
        )
    )

    def assemble(results):
        if identity is None:
            return _assemble_partitioned_matrices(results, spec.total_features)
        from array import array
        from .cache_identity import evaluation_hasher

        train_ids, test_ids = array("q"), array("q")
        revision = evaluation_hasher(db_path)

        def capture_batches():
            for matrices, (train_rows, test_rows, digests) in results:
                if len(train_rows) != len(matrices[3]) or len(test_rows) != len(matrices[7]):
                    raise ValueError("extracted rows and captured identities disagree")
                train_ids.extend(train_rows)
                test_ids.extend(test_rows)
                revision.update(digests)
                yield matrices

        matrices = _assemble_partitioned_matrices(capture_batches(), spec.total_features)
        identity.update(
            train_row_ids=np.frombuffer(train_ids, dtype=np.int64),
            test_row_ids=np.frombuffer(test_ids, dtype=np.int64),
            evaluation_revision=revision.hexdigest(),
        )
        return matrices

    if nw > 1:
        with _extract_pool(nw, spec) as pool:
            results = _bounded_iter(pool, _extract_partitioned_db_batch_worker, batch_args,
                                    max_inflight=_extraction_budget(nw))
            return assemble(results)
    return assemble(map(_extract_partitioned_db_batch_worker, batch_args))


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
