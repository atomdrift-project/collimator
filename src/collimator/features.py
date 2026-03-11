"""Extract fixed-size numeric feature vectors from cleave v3 AnalysisReport JSON.

v12: Path-centric feature extraction using hierarchical binary features.

Each finding's subdirectory path is extracted at 1, 2, and 3 levels of depth,
then paired with criticality tiers (notable, suspicious, hostile) to create
binary features. For example, a finding at "objectives/evasion/process" with
crit=hostile produces these binary signals:

    path:objectives:hostile                    = 1
    path:objectives:suspicious                 = 1
    path:objectives:notable                    = 1
    path:objectives/evasion:hostile             = 1
    path:objectives/evasion:suspicious          = 1
    path:objectives/evasion:notable             = 1
    path:objectives/evasion/process:hostile      = 1
    path:objectives/evasion/process:suspicious   = 1
    path:objectives/evasion/process:notable      = 1

This lets the model learn patterns like "objectives/anti-static:hostile AND
micro-behaviors/process/injection:suspicious → malware" while ignoring
sub-notable noise that dominates benign software.

Feature groups:
  1. Path × Tier: binary features for hierarchical paths × crit tiers (~500)
  2. Path Aggregates: attack breadth, context breadth, ratios (8)
  3. Third-Party / Well-Known Summary: aggregated match signals (6)
  4. Key Metrics: curated binary/text/PE metrics (16)
  5. File Type: one-hot (corpus-dependent, ~30-40)
  6. Structural: anomalies + finding count (4)
"""

from __future__ import annotations

import json
import logging
import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CRITICALITY_ORDINAL: dict[str, int] = {
    "filtered": 0,
    "component": 1,
    "baseline": 2,
    "notable": 3,
    "suspicious": 4,
    "hostile": 5,
}

RISK_ORDINAL: dict[str, int] = {
    "": 0,
    "filtered": 0,
    "component": 1,
    "baseline": 2,
    "notable": 3,
    "suspicious": 4,
    "hostile": 5,
}

# Criticality tiers used for binary path features (ignore below notable).
TIERS: list[tuple[str, int]] = [
    ("notable", 3),
    ("suspicious", 4),
    ("hostile", 5),
]
TIER_ORDINALS: dict[str, int] = {name: ordinal for name, ordinal in TIERS}

# Minimum number of samples a path×tier combo must appear in to get a feature.
MIN_PATH_FREQ = 30

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

# Top-level categories that count as "attack" paths for aggregate features.
_ATTACK_TOPS = frozenset({"objectives"})
# Top-level categories that count as "context" (benign indicator) paths.
_CONTEXT_TOPS = frozenset({"metadata"})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def primary_file(report: dict[str, Any]) -> dict[str, Any]:
    """Return the primary (first) file entry from a v3 report."""
    files = report.get("files") or []
    if files and isinstance(files[0], dict):
        return files[0]
    return {}


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

    Version 12: path×tier binary features. path_vocab contains strings like
    "objectives/evasion/process:hostile" — each is a binary feature.
    """

    version: int = 12
    path_vocab: list[str] = field(default_factory=list)
    filetype_vocab: list[str] = field(default_factory=list)
    feature_names: list[str] = field(default_factory=list)
    total_features: int = 0
    feature_means: list[float] | None = None
    feature_stds: list[float] | None = None

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        d: dict[str, Any] = {
            "version": self.version,
            "path_vocab": self.path_vocab,
            "filetype_vocab": self.filetype_vocab,
            "feature_names": self.feature_names,
            "total_features": self.total_features,
        }
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
        if version < 12:
            log.warning(
                "loading feature spec version %d (expected 12); "
                "models trained with older versions are not compatible",
                version,
            )
        return cls(
            version=version,
            path_vocab=data.get("path_vocab", []),
            filetype_vocab=data.get("filetype_vocab", []),
            feature_names=data["feature_names"],
            total_features=data["total_features"],
            feature_means=data.get("feature_means"),
            feature_stds=data.get("feature_stds"),
        )


# ---------------------------------------------------------------------------
# Vocabulary building
# ---------------------------------------------------------------------------

def build_vocab(reports: list[dict[str, Any]]) -> FeatureSpec:
    """Scan all reports to build the feature vocabulary.

    Collects hierarchical path × tier combos with frequency >= MIN_PATH_FREQ,
    plus all file types.
    """
    combo_counts: dict[str, int] = {}
    filetypes: set[str] = set()

    for report in reports:
        pf = primary_file(report)

        ftype = pf.get("file_type", "")
        if ftype:
            filetypes.add(ftype)

        # Compute per-path max crit for this sample (at all hierarchy levels).
        sample_paths: dict[str, int] = {}  # path -> max_crit_ord
        for finding in pf.get("findings") or []:
            fid = finding.get("id", "")
            if not fid:
                continue
            crit_ord = CRITICALITY_ORDINAL.get(finding.get("crit", "baseline"), 2)
            for path in _finding_paths(fid):
                if crit_ord > sample_paths.get(path, -1):
                    sample_paths[path] = crit_ord

        # Count which path×tier combos this sample activates.
        for path, max_ord in sample_paths.items():
            for tier_name, tier_ord in TIERS:
                if max_ord >= tier_ord:
                    key = f"{path}:{tier_name}"
                    combo_counts[key] = combo_counts.get(key, 0) + 1

    # Filter by minimum frequency, sort for deterministic ordering.
    path_vocab = sorted(k for k, c in combo_counts.items() if c >= MIN_PATH_FREQ)
    filetype_vocab = sorted(filetypes)

    # Build feature name list.
    feature_names: list[str] = []

    # Group 1: Path × Tier binary features.
    for combo in path_vocab:
        feature_names.append(f"path:{combo}")

    # Group 2: Path Aggregates (8).
    feature_names.extend([
        "agg:attack_breadth_notable",
        "agg:attack_breadth_suspicious",
        "agg:attack_max_crit",
        "agg:micro_breadth_notable",
        "agg:context_breadth",
        "agg:attack_to_context_ratio",
        "agg:total_active_paths",
        "agg:supply_chain_signal",
    ])

    # Group 3: Third-Party / Well-Known Summary (6).
    feature_names.extend([
        "ext:third_party_max_crit",
        "ext:third_party_count",
        "ext:well_known_max_crit",
        "ext:well_known_hostile_count",
        "ext:well_known_suspicious_count",
        "ext:has_yara_match",
    ])

    # Group 4: Key Metrics (16).
    for group, fname, _ in KEY_METRICS:
        feature_names.append(f"metrics:{group}_{fname}")

    # Group 5: File Type one-hot.
    for ft in filetype_vocab:
        feature_names.append(f"filetype:{ft}")

    # Group 6: Structural (4).
    feature_names.extend([
        "struct:tiny_executable",
        "struct:no_imports",
        "struct:zero_findings",
        "struct:finding_count_log",
    ])

    spec = FeatureSpec(
        path_vocab=path_vocab,
        filetype_vocab=filetype_vocab,
        feature_names=feature_names,
        total_features=len(feature_names),
    )
    log.info(
        "vocab: %d path×tier combos (>=%d freq), %d filetypes -> %d features (v12 path×tier)",
        len(path_vocab), MIN_PATH_FREQ, len(filetype_vocab), spec.total_features,
    )
    return spec


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

class _ExtractContext:
    """Pre-built lookup tables for fast repeated extraction against a spec."""

    __slots__ = ("path_tiers", "n_combos", "ft_lookup", "n_ft", "total_features")

    def __init__(self, spec: FeatureSpec) -> None:
        # Map path -> [(feature_index, tier_ord)] for fast lookup during extraction.
        self.path_tiers: dict[str, list[tuple[int, int]]] = defaultdict(list)
        for i, combo in enumerate(spec.path_vocab):
            # combo is "objectives/evasion/process:hostile"
            path, tier_name = combo.rsplit(":", 1)
            tier_ord = TIER_ORDINALS[tier_name]
            self.path_tiers[path].append((i, tier_ord))
        self.n_combos = len(spec.path_vocab)
        self.ft_lookup = {ft: i for i, ft in enumerate(spec.filetype_vocab)}
        self.n_ft = len(spec.filetype_vocab)
        self.total_features = spec.total_features


def _extract_into(report: dict[str, Any], ctx: _ExtractContext, vec: np.ndarray) -> None:
    """Extract features from a report into a pre-allocated vector."""
    pf = primary_file(report)
    findings = pf.get("findings") or []
    offset = 0

    # -----------------------------------------------------------------------
    # Group 1: Path × Tier binary features (n_combos features)
    # -----------------------------------------------------------------------
    path_offset = offset
    offset += ctx.n_combos

    # Compute per-path max crit at all hierarchy levels.
    sample_paths: dict[str, int] = {}  # path -> max_crit_ord
    third_party_max_crit = 0
    third_party_count = 0
    well_known_max_crit = 0
    well_known_hostile = 0
    well_known_suspicious = 0
    has_yara = False

    for finding in findings:
        fid = finding.get("id", "")
        if not fid:
            continue
        crit_ord = CRITICALITY_ORDINAL.get(finding.get("crit", "baseline"), 2)

        # Track third_party / well-known for aggregate features.
        top = fid.split("/")[0]
        if top == "third_party":
            third_party_count += 1
            if crit_ord > third_party_max_crit:
                third_party_max_crit = crit_ord
            has_yara = True
        elif top == "well-known":
            if crit_ord > well_known_max_crit:
                well_known_max_crit = crit_ord
            if crit_ord >= 5:
                well_known_hostile += 1
            elif crit_ord >= 4:
                well_known_suspicious += 1

        # Update max crit for each hierarchical path level.
        for path in _finding_paths(fid):
            if crit_ord > sample_paths.get(path, -1):
                sample_paths[path] = crit_ord

    # Set binary features: 1.0 if sample's max crit for path >= tier threshold.
    for path, max_ord in sample_paths.items():
        for feat_idx, tier_ord in ctx.path_tiers.get(path, []):
            if max_ord >= tier_ord:
                vec[path_offset + feat_idx] = 1.0

    # -----------------------------------------------------------------------
    # Group 2: Path Aggregates (8 features)
    # -----------------------------------------------------------------------
    agg_offset = offset
    offset += 8

    # Compute from raw per-path max crits (3-level paths only for specificity).
    attack_breadth_notable = 0
    attack_breadth_suspicious = 0
    attack_max_crit = 0
    micro_breadth_notable = 0
    context_breadth = 0
    total_active = 0

    for path, max_ord in sample_paths.items():
        # Only count 3-level paths for aggregates to avoid double-counting.
        if path.count("/") < 2:
            continue
        if max_ord < 3:  # below notable — skip
            continue
        total_active += 1
        top = path.split("/")[0]
        if top in _ATTACK_TOPS:
            attack_breadth_notable += 1
            if max_ord >= 4:
                attack_breadth_suspicious += 1
            if max_ord > attack_max_crit:
                attack_max_crit = max_ord
        elif top in _CONTEXT_TOPS:
            context_breadth += 1
        elif top == "micro-behaviors":
            micro_breadth_notable += 1

    vec[agg_offset] = attack_breadth_notable
    vec[agg_offset + 1] = attack_breadth_suspicious
    vec[agg_offset + 2] = attack_max_crit
    vec[agg_offset + 3] = micro_breadth_notable
    vec[agg_offset + 4] = context_breadth
    vec[agg_offset + 5] = (
        attack_breadth_notable / (context_breadth + 1)
    )
    vec[agg_offset + 6] = math.log1p(total_active)
    # Supply chain signal: attack behaviors coexisting with legitimate context.
    vec[agg_offset + 7] = (
        attack_breadth_notable * (context_breadth / max(total_active, 1))
    )

    # -----------------------------------------------------------------------
    # Group 3: Third-Party / Well-Known Summary (6 features)
    # -----------------------------------------------------------------------
    ext_offset = offset
    offset += 6

    vec[ext_offset] = third_party_max_crit
    vec[ext_offset + 1] = math.log1p(third_party_count)
    vec[ext_offset + 2] = well_known_max_crit
    vec[ext_offset + 3] = well_known_hostile
    vec[ext_offset + 4] = well_known_suspicious
    vec[ext_offset + 5] = 1.0 if has_yara else 0.0

    # -----------------------------------------------------------------------
    # Group 4: Key Metrics (16 features)
    # -----------------------------------------------------------------------
    metrics = pf.get("metrics") or {}
    for group, fname, use_log in KEY_METRICS:
        val = _float((metrics.get(group) or {}).get(fname))
        if use_log:
            val = math.log1p(abs(val))
        vec[offset] = val
        offset += 1

    # -----------------------------------------------------------------------
    # Group 5: File Type one-hot
    # -----------------------------------------------------------------------
    idx = ctx.ft_lookup.get(pf.get("file_type", ""))
    if idx is not None:
        vec[offset + idx] = 1.0
    offset += ctx.n_ft

    # -----------------------------------------------------------------------
    # Group 6: Structural (4 features)
    # -----------------------------------------------------------------------
    file_size = pf.get("size", 0)
    file_type = pf.get("file_type", "")
    is_binary = file_type in ("pe", "elf", "macho")
    imports = pf.get("imports") or []

    vec[offset] = 1.0 if (is_binary and file_size < 20000) else 0.0  # tiny_executable
    vec[offset + 1] = 1.0 if len(imports) == 0 else 0.0  # no_imports
    vec[offset + 2] = 1.0 if len(findings) == 0 else 0.0  # zero_findings
    vec[offset + 3] = math.log1p(len(findings))  # finding_count_log
    offset += 4


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
) -> tuple[np.ndarray, np.ndarray]:
    """Extract feature vectors for all samples."""
    n = len(reports)
    X = np.zeros((n, spec.total_features), dtype=np.float32)
    y = np.array(labels, dtype=np.float32)

    ctx = _ExtractContext(spec)
    for i, report in enumerate(reports):
        _extract_into(report, ctx, X[i])

    log.info("extracted %d samples x %d features", n, spec.total_features)
    return X, y


def standardize(X: np.ndarray, spec: FeatureSpec) -> np.ndarray:
    """Apply z-score standardization using training statistics.

    Works on single vectors (1D) and batches (2D) via numpy broadcasting.
    Features that were constant during training (mean=0, std=1) are zeroed
    out to prevent catastrophic misclassification from unseen raw values.
    """
    if spec.feature_means is None or spec.feature_stds is None:
        return X
    means = np.array(spec.feature_means, dtype=np.float32)
    stds = np.array(spec.feature_stds, dtype=np.float32)
    result = (X - means) / stds
    dead = (means == 0.0) & (stds == 1.0)
    result[..., dead] = 0.0
    return result
