"""Extract fixed-size numeric feature vectors from cleave v3 AnalysisReport JSON.

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
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
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
MODEL_ABI_VERSION = 15

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

FEATURE_GROUPS = ("present", "maxcrit", "agg", "ext", "metrics", "filetype", "struct", "elements", "formula", "score", "bigrams", "ghosts", "skeletons", "rares", "trigrams", "logic_gaps", "signature_synergy", "clusters", "intent_gaps", "neg_space")


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
        include_silent_packer_signal=os.getenv("COLLIMATOR_SILENT_PACKER_SIGNAL") == "1",
        include_mtime_kurtosis=os.getenv("COLLIMATOR_MTIME_KURTOSIS") == "1",
        include_air_gap_signal=os.getenv("COLLIMATOR_AIR_GAP_SIGNAL") == "1",
        include_extreme_features=os.getenv("COLLIMATOR_EXTREME_FEATURES") == "1",
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


def _float(value: Any, default: float = 0.0) -> float:
    """Best-effort float conversion for report fields."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _finding_paths(finding_id: str) -> list[str]:
    """Extract hierarchical path prefixes (1, 2, 3 levels) from a finding ID.

    "objectives/evasion/process/injection::technique-x"
        -> ["objectives", "objectives/evasion", "objectives/evasion/process"]
    "metadata/format::no-functions"
        -> ["metadata", "metadata/format"]
    """
    base = finding_id.split("::")[0] if "::" in finding_id else finding_id
    parts = base.split("/")
    return ["/".join(parts[:d]) for d in range(1, min(len(parts), 3) + 1)]


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

    # NOTE: bumping this version requires a matching update in ../collimator (Rust).
    version: int = 15
    abi_version: int = MODEL_ABI_VERSION
    presence_vocab: list[str] = field(default_factory=list)
    filetype_vocab: list[str] = field(default_factory=list)
    element_vocab: list[str] = field(default_factory=list)
    bigram_vocab: list[str] = field(default_factory=list)
    ghost_vocab: list[str] = field(default_factory=list)
    skeleton_vocab: list[str] = field(default_factory=list)
    rare_element_vocab: list[str] = field(default_factory=list)
    trigram_vocab: list[str] = field(default_factory=list)
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
            "feature_names": self.feature_names,
            "total_features": self.total_features,
        }
        d["standardized"] = self.standardized
        if self.feature_means is not None:
            d["feature_means"] = self.feature_means
        if self.feature_stds is not None:
            d["feature_stds"] = self.feature_stds
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
        if config.include_extreme_features:
            feature_names.append("agg:hostile_depth_weight")

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

    # Group 5: Key Metrics (16).
    if "metrics" in config.enabled_groups:
        for group, fname, _ in KEY_METRICS:
            feature_names.append(f"metrics:{group}_{fname}")

    # Group 6: File Type multi-hot across all files in the report.
    if "filetype" in config.enabled_groups:
        for ftype in filetype_vocab:
            feature_names.append(f"filetype:{ftype}")

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
            # Interaction with filetype
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

    # Group 12: Ghosts (absence of expected benign behavior).
    if "ghosts" in config.enabled_groups:
        for ghost in ghost_vocab:
            feature_names.append(f"ghost:{ghost}")

    # Group 13: Skeletons and interactions.
    if "skeletons" in config.enabled_groups:
        for skel in skeleton_vocab:
            feature_names.append(f"skeleton:{skel}")
            # Cross-product with filetype for Experiment 22.
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
        if config.include_extreme_features:
            feature_names.extend([
                "struct:anachronistic_injection",
                "struct:code_entropy_spike",
            ])

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
    feature_names = _build_feature_names(presence_vocab, filetype_vocab, element_vocab, bigram_vocab, ghost_vocab, skeleton_vocab)

    spec = FeatureSpec(
        presence_vocab=presence_vocab,
        filetype_vocab=filetype_vocab,
        element_vocab=element_vocab,
        bigram_vocab=bigram_vocab,
        ghost_vocab=ghost_vocab,
        skeleton_vocab=skeleton_vocab,
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
        "presence_lookup", "n_paths", "ft_lookup", "n_ft",
        "element_lookup", "element_interaction_lookup", "n_el", "bigram_lookup", "n_bi",
        "ghost_vocab", "ghost_lookup", "n_gh",
        "skeleton_lookup", "skeleton_interaction_lookup", "n_sk",
        "rare_element_lookup", "n_re",
        "trigram_lookup", "n_tri", "blindfold", "total_features",
        "score_interaction_lookup", "synergy_lookup"
    )

    def __init__(self, spec: FeatureSpec) -> None:
        config = feature_config_from_env()
        self.blindfold = config.include_blindfold
        self.total_features = spec.total_features
        
        # Build lookups that map to the actual indices in feature_names.
        name_to_idx = {name: i for i, name in enumerate(spec.feature_names)}
        
        self.presence_lookup: dict[str, int] = {}
        for path in spec.presence_vocab:
            if (idx := name_to_idx.get(f"present:{path}")) is not None:
                self.presence_lookup[path] = idx
        self.n_paths = len(spec.presence_vocab)

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
        for bi in spec.bigram_vocab:
            if (idx := name_to_idx.get(f"bigrams:{bi}")) is not None:
                self.bigram_lookup[bi] = idx
            # Synergy bigrams use the same vocab.
            if (idx := name_to_idx.get(f"unsigned_bigram:{bi}")) is not None:
                # We can't share lookup if they have different prefixes in spec.
                # Signature synergy uses unsigned_bigram: prefix.
                pass 
        
        # Explicit synergy lookup to be safe.
        self.synergy_lookup: dict[str, int] = {}
        for bi in spec.bigram_vocab:
            if (idx := name_to_idx.get(f"unsigned_bigram:{bi}")) is not None:
                self.synergy_lookup[bi] = idx
        self.n_bi = len(spec.bigram_vocab)

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
        metrics = file_entry.get("ms") or {}
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
    config = feature_config_from_env()
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
        conf = _float(finding.get("c", 1.0))
        if conf < MIN_CONFIDENCE:
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

        top = fid.split("/")[0]
        if crit_ord >= 4:
            suspicious_categories.add(top)
        if crit_ord >= 5:
            hostile_categories.add(top)
        if top == "third_party":
            third_party_count += 1
            if crit_ord > third_party_max_crit:
                third_party_max_crit = crit_ord
            has_yara = has_yara or fid.startswith("third_party/yara")
        elif top == "well-known":
            if crit_ord > well_known_max_crit:
                well_known_max_crit = crit_ord
            if crit_ord >= 5:
                well_known_hostile += 1
            elif crit_ord >= 4:
                well_known_suspicious += 1

        for path in _finding_paths(fid):
            if crit_ord > sample_paths.get(path, -1):
                sample_paths[path] = crit_ord
            if config.include_soft_presence:
                path_confidences[path] = max(path_confidences.get(path, 0.0), conf)

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
) -> tuple[float, ...]:
    """Summarize the riskiest files so a few bad files survive package dilution."""
    if k <= 0 or not files:
        return 0.0, 0.0, 0.0, 0.0

    stats = [_file_risk_stats(file_entry) for file_entry in files]
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


def _safe_assign(vec: np.ndarray, offset: int, idx: int, value: float) -> None:
    """Assign value to vec[offset + idx] if it's within bounds."""
    target = offset + idx
    if target < len(vec):
        vec[target] = value


def _apply_presence_features(
    summary: _FindingSummary,
    ctx: _ExtractContext,
    vec: np.ndarray,
    offset: int,
    score: int = 0,
) -> int:
    """Group 1: path presence features."""
    config = feature_config_from_env()
    sample_paths = summary.sample_paths
    score_weight = 1.0
    if score > 0:
        score_weight = float(math.log1p(score))

    for path, max_ord in sample_paths.items():
        if max_ord >= 2:  # baseline or above
            feat_idx = ctx.presence_lookup.get(path)
            if feat_idx is not None:
                weight = score_weight
                if config.include_soft_presence:
                    weight *= summary.path_confidences.get(path, 1.0)
                _safe_assign(vec, offset, feat_idx, weight)
    return offset + ctx.n_paths


def _apply_maxcrit_features(
    summary: _FindingSummary,
    ctx: _ExtractContext,
    vec: np.ndarray,
    offset: int,
    score: int = 0,
) -> int:
    """Group 2: path maximum criticality features."""
    config = feature_config_from_env()
    sample_paths = summary.sample_paths
    score_weight = 1.0
    if score > 0:
        score_weight = float(math.log1p(score))

    for path, max_ord in sample_paths.items():
        feat_idx = ctx.presence_lookup.get(path)
        if feat_idx is not None:
            weight = score_weight
            if config.include_soft_presence:
                weight *= summary.path_confidences.get(path, 1.0)
            _safe_assign(vec, offset, feat_idx, float(max_ord) * weight)
    return offset + ctx.n_paths


def _apply_aggregate_features(
    summary: _FindingSummary,
    files: list[dict[str, Any]],
    vec: np.ndarray,
    offset: int,
    top_k_risk_files: int,
    include_breadth_density: bool,
    include_hostile_escalation: bool,
    include_hostile_weighted_density: bool,
    include_repetition_penalty: bool,
    include_file_severity_distribution: bool,
) -> int:
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

    for path, max_ord in sample_paths.items():
        if max_ord >= 2:
            top = path.split("/")[0]
            categories.add(top)
            if path.count("/") >= 2:
                path_breadth_any += 1

        if path.count("/") < 2:
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

    _safe_assign(vec, offset, 0, max_crit)
    _safe_assign(vec, offset, 1, len(categories))
    _safe_assign(vec, offset, 2, math.log1p(path_breadth_any))
    _safe_assign(vec, offset, 3, math.log1p(total_active))
    # Concentration ratios — what fraction of behavior is suspicious?
    _safe_assign(vec, offset, 4, breadth_suspicious / max(path_breadth_any, 1))
    _safe_assign(vec, offset, 5, breadth_hostile / max(path_breadth_any, 1))
    _safe_assign(vec, offset, 6, breadth_suspicious / max(breadth_notable, 1))
    _safe_assign(vec, offset, 7, breadth_notable_only / max(breadth_notable, 1))
    _safe_assign(vec, offset, 8, math.log1p(summary.notable_finding_count))
    _safe_assign(vec, offset, 9, math.log1p(summary.suspicious_finding_count))
    _safe_assign(vec, offset, 10, math.log1p(summary.hostile_finding_count))
    
    # Pruned raw IDs for density-first metrics.
    total_kb = max(sum(_float(file_entry.get("sz", 0.0)) for file_entry in files) / 1024.0, 0.1)
    _safe_assign(vec, offset, 11, summary.notable_finding_count / total_kb)
    _safe_assign(vec, offset, 12, summary.suspicious_finding_count / total_kb)
    _safe_assign(vec, offset, 13, summary.hostile_finding_count / total_kb)
    _safe_assign(vec, offset, 14, math.log1p(summary.unique_suspicious_ids) / math.log1p(total_kb))
    _safe_assign(vec, offset, 15, math.log1p(summary.unique_hostile_ids) / math.log1p(total_kb))
    total_kb = max(sum(_float(file_entry.get("sz", 0.0)) for file_entry in files) / 1024.0, 1.0)
    topk_features = _topk_file_risk_features(
        files,
        top_k_risk_files,
        include_breadth_density=include_breadth_density,
    )
    topk_susp_ratio, topk_host_ratio, topk_susp_log, topk_host_log = topk_features[:4]
    _safe_assign(vec, offset, 16,  topk_susp_ratio)
    _safe_assign(vec, offset, 17,  topk_host_ratio)
    _safe_assign(vec, offset, 18,  topk_susp_log)
    _safe_assign(vec, offset, 19,  topk_host_log)
    offset += 20
    if include_breadth_density:
        category_denom = max(len(categories), 1)
        _safe_assign(vec, offset, 0, float(summary.suspicious_category_breadth))
        _safe_assign(vec, offset, 1, float(summary.hostile_category_breadth))
        _safe_assign(vec, offset, 2, summary.suspicious_category_breadth / category_denom)
        _safe_assign(vec, offset, 3, summary.hostile_category_breadth / category_denom)
        _safe_assign(vec, offset, 4, summary.suspicious_finding_count / total_kb)
        _safe_assign(vec, offset, 5, summary.hostile_finding_count / total_kb)
        _safe_assign(vec, offset, 6, summary.suspicious_category_breadth / total_kb)
        _safe_assign(vec, offset, 7, summary.hostile_category_breadth / total_kb)
        _safe_assign(vec, offset, 8, topk_features[4])
        _safe_assign(vec, offset, 9, topk_features[5])
        _safe_assign(vec, offset, 10, topk_features[6])
        _safe_assign(vec, offset, 11, topk_features[7])
        offset += 12
    if include_hostile_escalation:
        _safe_assign(vec, offset, 0, breadth_hostile / max(breadth_notable, 1))
        _safe_assign(vec, offset, 1, breadth_hostile / max(breadth_suspicious, 1))
        _safe_assign(vec, offset, 2, summary.suspicious_finding_count / max(summary.notable_finding_count, 1))
        _safe_assign(vec, offset, 3, summary.hostile_finding_count / max(summary.notable_finding_count, 1))
        _safe_assign(vec, offset, 4, summary.hostile_finding_count / max(summary.suspicious_finding_count, 1))
        offset += 5
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
        _safe_assign(vec, offset, 0, summary.hostile_finding_count / total_kb + 0.25 * (summary.suspicious_finding_count / total_kb))
        _safe_assign(vec, offset, 1, sum(s.hostile_density + 0.25 * s.suspicious_density for s in top_hostile_weighted))
        offset += 2
    if include_repetition_penalty:
        _safe_assign(vec, offset, 0, 1.0 - (summary.unique_suspicious_ids / max(summary.suspicious_finding_count, 1)))
        _safe_assign(vec, offset, 1, 1.0 - (summary.unique_hostile_ids / max(summary.hostile_finding_count, 1)))
        _safe_assign(vec, offset, 2, 1.0 - (summary.suspicious_category_breadth / max(summary.suspicious_finding_count, 1)))
        _safe_assign(vec, offset, 3, 1.0 - (summary.hostile_category_breadth / max(summary.hostile_finding_count, 1)))
        offset += 4
    if include_file_severity_distribution:
        n_files = max(len(files), 1)
        hostile_files = sum(s.max_crit >= 5 for s in stats)
        suspicious_files = sum(s.max_crit == 4 for s in stats)
        notable_files = sum(s.max_crit == 3 for s in stats)
        _safe_assign(vec, offset, 0, hostile_files / n_files)
        _safe_assign(vec, offset, 1, suspicious_files / n_files)
        _safe_assign(vec, offset, 2, notable_files / n_files)
        _safe_assign(vec, offset, 3, math.log1p(hostile_files))
        _safe_assign(vec, offset, 4, math.log1p(suspicious_files))
        _safe_assign(vec, offset, 5, math.log1p(notable_files))
        offset += 6
    return offset


def _apply_external_signal_features(
    summary: _FindingSummary,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 4: aggregated third-party and well-known signals."""
    _safe_assign(vec, offset, 0, summary.third_party_max_crit)
    _safe_assign(vec, offset, 1, math.log1p(summary.third_party_count))
    _safe_assign(vec, offset, 2, summary.well_known_max_crit)
    _safe_assign(vec, offset, 3, summary.well_known_hostile)
    _safe_assign(vec, offset, 4, summary.well_known_suspicious)
    _safe_assign(vec, offset, 5, 1.0 if summary.has_yara else 0.0)
    return offset + 6


def _apply_metric_features(
    metrics: dict[str, Any],
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 5: curated numeric metrics."""
    for group, fname, use_log in KEY_METRICS:
        val = _float((metrics.get(group) or {}).get(fname))
        if use_log:
            val = math.log1p(abs(val))
        _safe_assign(vec, offset, 0, val)
        offset += 1
    return offset


def _apply_filetype_features(
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 6: file type multi-hot features across all files."""
    if not ctx.blindfold:
        for file_entry in files:
            idx = ctx.ft_lookup.get(file_entry.get("type", ""))
            if idx is not None:
                _safe_assign(vec, offset, idx, 1.0)
    # ALWAYS advance by n_ft to maintain feature index stability
    # regardless of whether the specific features were written.
    return offset + ctx.n_ft


def _apply_element_features(
    elements: str,
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 8: element multi-hot features and filetype interactions."""
    if elements:
        present_types = {f.get("type", "") for f in files if f.get("type")}
        for el in elements.split(","):
            el = el.strip()
            if (idx := ctx.element_lookup.get(el)) is not None:
                _safe_assign(vec, 0, idx, 1.0)
            for ft in present_types:
                if (idx := ctx.element_interaction_lookup.get((ft, el))) is not None:
                    _safe_assign(vec, 0, idx, 1.0)

    return offset + ctx.n_el * (1 + ctx.n_ft)


def _apply_formula_features(
    formula: str,
    finding_count: int,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 9: formula features."""
    # formula example: "A2B1C5" -> skeleton: "ABC", unique: 3
    skeleton = "".join([c for c in formula if c.isalpha()])
    _safe_assign(vec, offset, 0, float(len(skeleton)))
    _safe_assign(vec, offset, 1, float(len(set(skeleton))))
    if finding_count > 0:
        _safe_assign(vec, offset, 2, float(len(formula)) / finding_count)
    return offset + 3


def _apply_score_features(
    score: int,
    total_size: float,
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 10: hopper score features and filetype interactions."""
    _safe_assign(vec, offset, 0, float(score))
    _safe_assign(vec, offset, 1, float(score) / math.log1p(total_size) if total_size > 0 else 0.0)
    
    # Interaction with filetype.
    for file_entry in files:
        ft = file_entry.get("type", "")
        if (idx := ctx.score_interaction_lookup.get(ft)) is not None:
            _safe_assign(vec, 0, idx, float(score))

    return offset + 2 + ctx.n_ft


def _apply_structural_features(
    files: list[dict[str, Any]],
    filtered_finding_count: int,
    vec: np.ndarray,
    offset: int,
    include_file_risk_coverage: bool,
    mtime_str: str = "",
) -> int:
    """Group 7: structural / container context (7)."""
    binary_like = {"pe", "elf", "macho"}
    any_tiny_binary = False
    import_candidates = 0
    importless_candidates = 0
    max_entropy = 0.0
    suspicious_files = 0
    hostile_files = 0
    hostile_files_with_parent = 0
    inner_file_count = 0

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
        
        fmt = file_entry.get("mt")
        if fmt:
            try:
                mtimes.append(datetime.fromisoformat(str(fmt).replace(" ", "T")).timestamp())
            except (ValueError, TypeError):
                pass

        if file_entry.get("type", "") in binary_like and _float(file_entry.get("sz", 0)) < 20000:
            any_tiny_binary = True
        if "is" in file_entry:
            import_candidates += 1
            if len(file_entry.get("is") or []) == 0:
                importless_candidates += 1

        # Track max entropy across all files in the report.
        metrics = file_entry.get("ms") or {}
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

    _safe_assign(vec, offset, 0, 1.0 if any_tiny_binary else 0.0)
    _safe_assign(vec, offset, 1, 1.0 if (import_candidates > 0 and importless_candidates == import_candidates) else 0.0)
    _safe_assign(vec, offset, 2, 1.0 if filtered_finding_count == 0 else 0.0)
    _safe_assign(vec, offset, 3, math.log1p(filtered_finding_count))
    _safe_assign(vec, offset, 4, math.log1p(len(files)))
    _safe_assign(vec, offset, 5, math.log1p(max(len(files) - 1, 0)))
    _safe_assign(vec, offset, 6, stealth_potential)
    offset += 7
    if include_file_risk_coverage:
        file_count = max(len(files), 1)
        _safe_assign(vec, offset, 0, suspicious_files / file_count)
        _safe_assign(vec, offset, 1, hostile_files / file_count)
        _safe_assign(vec, offset, 2, math.log1p(suspicious_files))
        _safe_assign(vec, offset, 3, math.log1p(hostile_files))
        offset += 4

    # Group 15: Packaged capability (Experiment 25).
    # Unique element variety * max binary entropy.
    unique_elements = float(len(set("".join([c for c in (files[0].get("formula") or "") if c.isalpha()]))))
    _safe_assign(vec, offset, 0, unique_elements * max_entropy)
    offset += 1

    # Group 17: Mtime anomalies (Experiment 30).
    # Inconsistency in timestamps often signals tampering.
    if len(mtimes) > 1:
        m_arr = np.array(mtimes)
        _safe_assign(vec, offset, 0, float(np.max(m_arr) - np.min(m_arr)) / 3600.0)
        _safe_assign(vec, offset, 1, float(np.std(m_arr)) / 3600.0)
    else:
        _safe_assign(vec, offset, 0, 0.0)
        _safe_assign(vec, offset, 1, 0.0)
    offset += 2

    # Group 18: Structural Depth and Entropy Gradients (Exp 36).
    _safe_assign(vec, offset, 0, math.log1p(max_nesting_depth))
    _safe_assign(vec, offset, 1, float(inner_file_count) / max(len(files), 1))
    if len(entropies) > 1:
        e_arr = np.array(entropies)
        _safe_assign(vec, offset, 2, float(np.std(e_arr)))
        _safe_assign(vec, offset, 3, float(np.max(e_arr) - np.mean(e_arr)))
    else:
        _safe_assign(vec, offset, 2, 0.0)
        _safe_assign(vec, offset, 3, 0.0)
    offset += 4
    
    # Exp 43: Silent Packer Signal
    if os.getenv("COLLIMATOR_SILENT_PACKER_SIGNAL") == "1":
        total_size = sum(_float(f.get("sz", 0)) for f in files)
        size_mb = total_size / (1024 * 1024)
        _safe_assign(vec, offset, 0, math.log1p(size_mb) / (filtered_finding_count + 1))
        offset += 1

    # Exp 44: Mtime Kurtosis
    if os.getenv("COLLIMATOR_MTIME_KURTOSIS") == "1":
        if len(mtimes) > 3:
            _safe_assign(vec, offset, 0, float(stats.kurtosis(mtimes)))
        else:
            _safe_assign(vec, offset, 0, 0.0)
        offset += 1

    # Exp 46: Behavioral Air-Gap
    if os.getenv("COLLIMATOR_AIR_GAP_SIGNAL") == "1":
        # If we have hostile files, but NONE of them have parents, it's an air-gap.
        val = 1.0 if (hostile_files > 0 and hostile_files_with_parent == 0) else 0.0
        _safe_assign(vec, offset, 0, val)
        offset += 1

    # Exp 48 & 49: Extreme Features
    if os.getenv("COLLIMATOR_EXTREME_FEATURES") == "1":
        # 48: Anachronistic Injection
        if mtimes and hostile_mtimes:
            median_mtime = float(np.median(mtimes))
            max_delta = max(abs(t - median_mtime) for t in hostile_mtimes)
            _safe_assign(vec, offset, 0, max_delta / 3600.0)
        else:
            _safe_assign(vec, offset, 0, 0.0)
        
        # 49: Code Entropy Spike
        if code_entropies:
            avg_ent = float(np.mean(entropies)) if entropies else 0.0
            max_code_ent = max(code_entropies)
            _safe_assign(vec, offset, 1, max_code_ent - avg_ent)
        else:
            _safe_assign(vec, offset, 1, 0.0)
        offset += 2

    return offset


def _apply_neg_space_features(
    files: list[dict[str, Any]],
    sample_paths: dict[str, int],
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 23: negative space / missing expected behavior."""
    file_types = {f.get("type", "") for f in files}
    local_offset = 0
    for ftype, traits in sorted(EXPECTED_GHOSTS.items()):
        has_type = ftype in file_types
        for trait in traits:
            # If the type is present but the trait is missing, it's a "ghost".
            val = 1.0 if (has_type and (trait not in sample_paths or sample_paths[trait] < 1)) else 0.0
            _safe_assign(vec, offset, local_offset, val)
            local_offset += 1
    return offset + local_offset


def _apply_bigram_features(
    report: dict[str, Any],
    ctx: _ExtractContext,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 11: trait bigram multi-hot features."""
    for file_entry in report_files(report):
        file_traits: set[str] = set()
        for finding in file_entry.get("ts") or []:
            fid = finding.get("i", "")
            if fid and _float(finding.get("c", 1.0)) >= MIN_CONFIDENCE:
                file_traits.add(fid)

        # Using 3-level path base to match vocabulary.
        paths_list = sorted({fid.split("::")[0] for fid in file_traits})
        for i, p1 in enumerate(paths_list):
            for p2 in paths_list[i + 1 :]:
                bigram = f"{p1} + {p2}"
                idx = ctx.bigram_lookup.get(bigram)
                if idx is not None:
                    _safe_assign(vec, offset, idx, 1.0)
    return offset + ctx.n_bi


def _apply_ghost_features(
    sample_paths: dict[str, int],
    ctx: _ExtractContext,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 12: ghost features (absence of expected benign behavior)."""
    for path in ctx.ghost_vocab:
        # 1.0 if the expected benign path is MISSING.
        if path not in sample_paths or sample_paths[path] < 2:
            idx = ctx.ghost_lookup.get(path)
            if idx is not None:
                _safe_assign(vec, offset, idx, 1.0)
    return offset + ctx.n_gh


def _apply_skeleton_features(
    formula: str,
    files: list[dict[str, Any]],
    ctx: _ExtractContext,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 13: skeleton categorical and filetype interactions."""
    skeleton = "".join([c for c in formula if c.isalpha()])
    if not skeleton:
        return offset + ctx.n_sk * (1 + ctx.n_ft)

    sk_idx = ctx.skeleton_lookup.get(skeleton)
    if sk_idx is not None:
        # Base skeleton feature.
        _safe_assign(vec, offset, sk_idx, 1.0)

        # Interaction features with filetype.
        for file_entry in files:
            ft = file_entry.get("type", "")
            ft_idx = ctx.ft_lookup.get(ft)
            if ft_idx is not None:
                inter_idx = offset + ctx.n_sk + (sk_idx * ctx.n_ft) + ft_idx
                _safe_assign(vec, inter_idx, 0, 1.0)

    return offset + ctx.n_sk * (1 + ctx.n_ft)


def _apply_rare_element_features(
    elements: str,
    summary: _FindingSummary,
    ctx: _ExtractContext,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 14: rare element multi-hot features (smoking guns)."""
    config = feature_config_from_env()
    weight = 1.0
    if config.include_soft_presence and summary.finding_confidences:
        weight = float(np.mean(summary.finding_confidences))

    if elements:
        for el in elements.split(","):
            el = el.strip()
            idx = ctx.rare_element_lookup.get(el)
            if idx is not None:
                _safe_assign(vec, offset, idx, weight)
    return offset + ctx.n_re


def _apply_trigram_features(
    report: dict[str, Any],
    ctx: _ExtractContext,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 16: trait trigram multi-hot features."""
    for file_entry in report_files(report):
        file_traits: set[str] = set()
        for finding in file_entry.get("ts") or []:
            fid = finding.get("i", "")
            if fid and _float(finding.get("c", 1.0)) >= MIN_CONFIDENCE:
                file_traits.add(fid)

        # Using 3-level path base to match vocabulary.
        paths_list = sorted({fid.split("::")[0] for fid in file_traits})
        for i, p1 in enumerate(paths_list):
            for j in range(i + 1, len(paths_list)):
                p2 = paths_list[j]
                for p3 in paths_list[j + 1 :]:
                    trigram = f"{p1} + {p2} + {p3}"
                    idx = ctx.trigram_lookup.get(trigram)
                    if idx is not None:
                        _safe_assign(vec, offset, idx, 1.0)
    return offset + ctx.n_tri


def _apply_logic_gap_features(
    files: list[dict[str, Any]],
    summary: _FindingSummary,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 19: logic gap features (imports present without behavior)."""
    # Collect all unique imports across the report.
    all_imports: set[str] = set()
    for file_entry in files:
        imports = file_entry.get("is") or []
        for imp in imports:
            # Cleave imports are often list of dicts with 'n' key
            if isinstance(imp, dict):
                all_imports.add(imp.get("n", ""))
            else:
                all_imports.add(str(imp))

    sample_paths = summary.sample_paths
    for i, (cat, (imports_set, traits_set)) in enumerate(sorted(LOGIC_GAPS.items())):
        has_import = any(imp in all_imports for imp in imports_set)
        has_behavior = any(
            any(path.startswith(t) for t in traits_set)
            for path, max_ord in sample_paths.items()
            if max_ord >= 3  # notable or above
        )
        if has_import and not has_behavior:
            _safe_assign(vec, offset, i, 1.0)

    return offset + len(LOGIC_GAPS)


def _apply_signature_synergy_features(
    report: dict[str, Any],
    summary: _FindingSummary,
    ctx: _ExtractContext,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 20: signature synergy (unsigned + behavioral patterns)."""
    # Check if any file in the report is unsigned.
    is_unsigned = "metadata/unsigned" in summary.sample_paths
    if not is_unsigned:
        return offset + ctx.n_bi

    for file_entry in report_files(report):
        file_traits: set[str] = set()
        for finding in file_entry.get("ts") or []:
            fid = finding.get("i", "")
            if fid and _float(finding.get("c", 1.0)) >= MIN_CONFIDENCE:
                file_traits.add(fid)

        paths_list = sorted({fid.split("::")[0] for fid in file_traits})
        for i, p1 in enumerate(paths_list):
            for p2 in paths_list[i + 1 :]:
                bigram = f"{p1} + {p2}"
                idx = ctx.bigram_lookup.get(bigram)
                if idx is not None:
                    _safe_assign(vec, offset, idx, 1.0)
    return offset + ctx.n_bi


def _apply_intent_gap_features(
    summary: _FindingSummary,
    vec: np.ndarray,
    offset: int,
) -> int:
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

    for i, (cat, traits) in enumerate(sorted(risky_behaviors.items())):
        has_behavior = any(
            any(path.startswith(t) for t in traits)
            for path, max_ord in summary.sample_paths.items()
            if max_ord >= 4  # suspicious or above
        )
        # Gap exists if they have the behavior but NO documentation/help intent.
        if has_behavior and not intent_signal:
            _safe_assign(vec, offset, i, 1.0)

    return offset + 4


def _apply_cluster_features(
    cluster_id: int,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 21: semantic intent cluster features."""
    if 0 <= cluster_id < 50:
        _safe_assign(vec, offset, cluster_id, 1.0)
    return offset + 50


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

    offset = 0
    if "present" in config.enabled_groups:
        _apply_presence_features(
            summary, ctx, vec, offset,
            score=score if config.include_score_weighted_traits else 0,
        )
        offset += ctx.n_paths
    if "maxcrit" in config.enabled_groups:
        _apply_maxcrit_features(
            summary, ctx, vec, offset,
            score=score if config.include_score_weighted_traits else 0,
        )
        offset += ctx.n_paths
    if "agg" in config.enabled_groups:
        # Exp 51: hostile_depth_weight calculation
        hostile_depth_weight = 0.0
        if config.include_extreme_features:
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

        offset = _apply_aggregate_features(
            summary,
            files,
            vec,
            offset,
            config.top_k_risk_files,
            config.include_suspicious_breadth_density,
            config.include_hostile_escalation_features,
            config.include_hostile_weighted_density,
            config.include_repetition_penalty_features,
            config.include_file_severity_distribution,
        )
        if config.include_extreme_features:
            _safe_assign(vec, offset, 0, hostile_depth_weight)
            offset += 1
    if "ext" in config.enabled_groups:
        offset = _apply_external_signal_features(summary, vec, offset)
    if "metrics" in config.enabled_groups:
        offset = _apply_metric_features(metrics, vec, offset)
    if "filetype" in config.enabled_groups:
        offset = _apply_filetype_features(files, ctx, vec, offset)
    if "struct" in config.enabled_groups:
        offset = _apply_structural_features(
            files,
            summary.filtered_finding_count,
            vec,
            offset,
            config.include_struct_file_risk_coverage,
            mtime_str=mtime,
        )
    if "elements" in config.enabled_groups:
        offset = _apply_element_features(elements, files, ctx, vec, offset)
    if "formula" in config.enabled_groups:
        offset = _apply_formula_features(formula, summary.filtered_finding_count, vec, offset)
    if "score" in config.enabled_groups:
        total_size = sum(_float(f.get("sz", 0)) for f in files)
        offset = _apply_score_features(score, total_size, files, ctx, vec, offset)

    if "bigrams" in config.enabled_groups:
        _apply_bigram_features(report, ctx, vec, offset)
        offset += ctx.n_bi

    if "ghosts" in config.enabled_groups:
        _apply_ghost_features(summary.sample_paths, ctx, vec, offset)
        offset += ctx.n_gh

    if "skeletons" in config.enabled_groups:
        _apply_skeleton_features(formula, files, ctx, vec, offset)
        offset += ctx.n_sk * (1 + ctx.n_ft)

    if "rares" in config.enabled_groups:
        _apply_rare_element_features(elements, summary, ctx, vec, offset)
        offset += ctx.n_re

    if "trigrams" in config.enabled_groups:
        _apply_trigram_features(report, ctx, vec, offset)
        offset += ctx.n_tri

    if "logic_gaps" in config.enabled_groups:
        _apply_logic_gap_features(files, summary, vec, offset)
        offset += len(LOGIC_GAPS)

    if "signature_synergy" in config.enabled_groups:
        _apply_signature_synergy_features(report, summary, ctx, vec, offset)
        offset += ctx.n_bi

    if "clusters" in config.enabled_groups:
        offset = _apply_cluster_features(cluster_id, vec, offset)

    if "intent_gaps" in config.enabled_groups:
        _apply_intent_gap_features(summary, vec, offset)
        offset += 4  # fixed categories

    if "neg_space" in config.enabled_groups:
        offset = _apply_neg_space_features(files, summary.sample_paths, vec, offset)


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
            # Using the 3-level base path to capture broader "behavioral phrases".
            paths_list = sorted({fid.split("::")[0] for fid in file_traits})
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
    """Choose a conservative parallelism level for JSON-heavy feature work."""
    cpu_count = os.cpu_count() or 1
    if cpu_count <= 2:
        return 1
    # JSON parsing + SQLite streaming hits diminishing returns quickly on this
    # workload. Cap the auto setting lower to reduce IPC overhead and DB
    # contention on larger hosts.
    return min(max(cpu_count // 4, 2), 8)


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


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract(report: dict[str, Any], spec: FeatureSpec) -> np.ndarray:
    """Extract a feature vector from a single cleave AnalysisReport."""
    vec = np.zeros(spec.total_features, dtype=np.float32)
    _extract_into(report, _ExtractContext(spec), vec)
    return vec


def extract_all(
    reports: list[dict[str, Any]],
    labels: list[int],
    spec: FeatureSpec,
    n_workers: int = 0,
) -> tuple[sp.csr_matrix, np.ndarray]:
    """Extract feature vectors for all samples as a sparse CSR matrix."""
    return extract_stream(zip(reports, labels), spec, n_workers=n_workers)


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
    log.info(
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
) -> tuple[dict[str, int], list[str], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int]]:
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

            paths_list = sorted({fid.split("::")[0] for fid in file_traits})
            for i, p1 in enumerate(paths_list):
                for p2 in paths_list[i + 1 :]:
                    # Hard cap at 100,000 unique bigrams per worker batch.
                    if len(bigram_counts) < 100000:
                        bigram = f"{p1} + {p2}"
                        bigram_counts[bigram] = bigram_counts.get(bigram, 0) + 1
                    
                    for p3 in paths_list[i + 2 :]:
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

    return (
        presence_counts, filetypes, element_counts, bigram_counts,
        benign_presence, malware_presence, skeleton_counts,
        benign_elements, malware_elements, trigram_counts, benign_trigrams
    )


def build_vocab_from_db(
    db_path: Path | str,
    row_ids_labels: list[tuple[int, int]],
    n_workers: int = 0,
) -> FeatureSpec:
    """Scan sampled reports in the DB to build a feature vocabulary."""
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
    bigram_vocab = sorted(k for k, c in bigram_counts.items() if c >= 1000)[:5000]
    skeleton_vocab = sorted(k for k, c in skeleton_counts.items() if c >= 100)

    # Trigrams: highly specific malware-only triplets (top 500 by frequency).
    malware_only_trigrams = sorted(
        [(k, c) for k, c in trigram_counts.items() if benign_trigrams.get(k, 0) == 0 and c >= 5],
        key=lambda x: x[1],
        reverse=True,
    )[:500]
    trigram_vocab = sorted(k for k, c in malware_only_trigrams)

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

    feature_names = _build_feature_names(
        presence_vocab, filetype_vocab, element_vocab, bigram_vocab, ghost_vocab, skeleton_vocab, rare_element_vocab, trigram_vocab
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
    log.info(
        "vocab: %d paths, %d filetypes, %d elements, %d bigrams, %d ghosts -> %d features",
        len(presence_vocab), len(filetype_vocab), len(element_vocab), len(bigram_vocab), len(ghost_vocab), spec.total_features,
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

    train_rows, train_cols, train_vals, train_labels = [], [], [], []
    test_rows, test_cols, test_vals, test_labels = [], [], [], []

    def _consume(batch_iter):
        for (tr, tc, tv, tl, ter, tec, tev, tel) in batch_iter:
            train_rows.extend(tr); train_cols.extend(tc); train_vals.extend(tv); train_labels.extend(tl)
            test_rows.extend(ter); test_cols.extend(tec); test_vals.extend(tev); test_labels.extend(tel)

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

    # Build final matrices.
    n_train = len(train_labels); n_test = len(test_labels)
    X_train = sp.csr_matrix((np.array(train_vals, dtype=np.float32), (np.array(train_rows, dtype=np.int32), np.array(train_cols, dtype=np.int32))), shape=(n_train, spec.total_features))
    y_train = np.array(train_labels, dtype=np.float32)
    X_test = sp.csr_matrix((np.array(test_vals, dtype=np.float32), (np.array(test_rows, dtype=np.int32), np.array(test_cols, dtype=np.int32))), shape=(n_test, spec.total_features))
    y_test = np.array(test_labels, dtype=np.float32)

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
