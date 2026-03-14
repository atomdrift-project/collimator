"""Extract fixed-size numeric feature vectors from cleave v3 AnalysisReport JSON.

v13: Capability-first feature extraction with criticality as gradient signal.

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
  3. Path Aggregates: breadth, concentration, and ratio signals (12)
  4. Third-Party / Well-Known Summary: aggregated match signals (6)
  5. Key Metrics: curated binary/text/PE metrics (16)
  6. File Type: one-hot (corpus-dependent, ~30-40)
  7. Structural: anomalies + finding count (4)
"""

from __future__ import annotations

import json
import logging
import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from collections.abc import Iterable
from typing import Any

import numpy as np
import scipy.sparse as sp

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

# Minimum number of samples a path must appear in to get a feature.
MIN_PATH_FREQ = 30

# Minimum confidence for a finding to be included in feature extraction.
# Low-confidence findings add noise without meaningful signal.
MIN_CONFIDENCE = 0.65

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

    Version 13: capability-first features. Each path in presence_vocab gets
    two features: a binary presence flag and an ordinal max-criticality value.
    No path×tier binary features — criticality is a gradient, not a threshold.
    """

    # NOTE: bumping this version requires a matching update in ../collimator (Rust).
    version: int = 13
    presence_vocab: list[str] = field(default_factory=list)
    filetype_vocab: list[str] = field(default_factory=list)
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
            "presence_vocab": self.presence_vocab,
            "filetype_vocab": self.filetype_vocab,
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
                "loading feature spec version %d (expected 13); "
                "models trained with older versions are not compatible",
                version,
            )
        return cls(
            version=version,
            presence_vocab=data.get("presence_vocab", []),
            filetype_vocab=data.get("filetype_vocab", []),
            feature_names=data["feature_names"],
            total_features=data["total_features"],
            feature_means=data.get("feature_means"),
            feature_stds=data.get("feature_stds"),
            standardized=data.get("standardized", True),
        )


# ---------------------------------------------------------------------------
# Vocabulary building
# ---------------------------------------------------------------------------

def build_vocab(reports: Iterable[dict[str, Any]]) -> FeatureSpec:
    """Scan all reports to build the feature vocabulary.

    Each path that appears in >= MIN_PATH_FREQ samples gets two features:
      - present:X  (binary) — capability exists at any crit ≥ baseline
      - maxcrit:X  (ordinal 0-5) — cleave's max criticality for this path

    This lets the model learn from capability combinations (presence) while
    optionally using criticality as a gradient signal (maxcrit). No binary
    tier thresholds — the model decides what criticality levels matter.

    Accepts any iterable of report dicts (including generators).
    """
    presence_counts: dict[str, int] = {}  # path -> sample count
    filetypes: set[str] = set()

    for report in reports:
        pf = primary_file(report)

        ftype = pf.get("file_type", "")
        if ftype:
            filetypes.add(ftype)

        sample_paths: dict[str, int] = {}
        for finding in pf.get("findings") or []:
            fid = finding.get("id", "")
            if not fid:
                continue
            if _float(finding.get("conf", 1.0)) < MIN_CONFIDENCE:
                continue
            crit_ord = CRITICALITY_ORDINAL.get(finding.get("crit", "baseline"), 2)
            for path in _finding_paths(fid):
                if crit_ord > sample_paths.get(path, -1):
                    sample_paths[path] = crit_ord

        for path, max_ord in sample_paths.items():
            if max_ord >= 2:
                presence_counts[path] = presence_counts.get(path, 0) + 1

    presence_vocab = sorted(k for k, c in presence_counts.items() if c >= MIN_PATH_FREQ)
    filetype_vocab = sorted(filetypes)

    feature_names: list[str] = []

    # Group 1: Path Presence — binary (capability exists?).
    for path in presence_vocab:
        feature_names.append(f"present:{path}")

    # Group 2: Path Max Criticality — ordinal 0-5 (cleave's severity gradient).
    for path in presence_vocab:
        feature_names.append(f"maxcrit:{path}")

    # Group 3: Path Aggregates (8).
    # Ratio-based: forces the model to learn from relative concentration of
    # suspicious behavior rather than absolute counts. A tool with 23 suspicious
    # findings out of 154 total (15%) looks very different from malware with
    # 10 suspicious out of 15 total (67%).
    feature_names.extend([
        "agg:max_crit",                  # highest crit seen (0-5)
        "agg:category_breadth",          # distinct top-level categories
        "agg:path_breadth_any",          # log1p of all 3-level paths (any crit)
        "agg:total_active_paths",        # log1p of notable+ 3-level paths
        "agg:suspicious_concentration",  # suspicious / all paths
        "agg:hostile_concentration",     # hostile / all paths
        "agg:escalation_rate",           # suspicious+ / notable+ (cleave escalation)
        "agg:notable_only_fraction",     # notable_only / notable+ (how much stays at notable)
    ])

    # Group 4: Third-Party / Well-Known Summary (6).
    feature_names.extend([
        "ext:third_party_max_crit",
        "ext:third_party_count",
        "ext:well_known_max_crit",
        "ext:well_known_hostile_count",
        "ext:well_known_suspicious_count",
        "ext:has_yara_match",
    ])

    # Group 5: Key Metrics (16).
    for group, fname, _ in KEY_METRICS:
        feature_names.append(f"metrics:{group}_{fname}")

    # Group 6: File Type one-hot.
    for ft in filetype_vocab:
        feature_names.append(f"filetype:{ft}")

    # Group 7: Structural (4).
    feature_names.extend([
        "struct:tiny_executable",
        "struct:no_imports",
        "struct:zero_findings",
        "struct:finding_count_log",
    ])

    spec = FeatureSpec(
        presence_vocab=presence_vocab,
        filetype_vocab=filetype_vocab,
        feature_names=feature_names,
        total_features=len(feature_names),
    )
    log.info(
        "vocab: %d paths (>=%d freq), %d filetypes -> %d features "
        "(v13 presence+maxcrit)",
        len(presence_vocab), MIN_PATH_FREQ,
        len(filetype_vocab), spec.total_features,
    )
    return spec


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

class _ExtractContext:
    """Pre-built lookup tables for fast repeated extraction against a spec."""

    __slots__ = ("presence_lookup", "n_paths", "ft_lookup", "n_ft", "total_features")

    def __init__(self, spec: FeatureSpec) -> None:
        self.presence_lookup: dict[str, int] = {
            path: i for i, path in enumerate(spec.presence_vocab)
        }
        self.n_paths = len(spec.presence_vocab)
        self.ft_lookup = {ft: i for i, ft in enumerate(spec.filetype_vocab)}
        self.n_ft = len(spec.filetype_vocab)
        self.total_features = spec.total_features


def _extract_into(report: dict[str, Any], ctx: _ExtractContext, vec: np.ndarray) -> None:
    """Extract features from a report into a pre-allocated vector."""
    pf = primary_file(report)
    findings = pf.get("findings") or []
    offset = 0

    # Compute per-path max crit at all hierarchy levels.
    sample_paths: dict[str, int] = {}  # path -> max_crit_ord
    filtered_finding_count = 0
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
        if _float(finding.get("conf", 1.0)) < MIN_CONFIDENCE:
            continue
        filtered_finding_count += 1
        crit_ord = CRITICALITY_ORDINAL.get(finding.get("crit", "baseline"), 2)

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

        for path in _finding_paths(fid):
            if crit_ord > sample_paths.get(path, -1):
                sample_paths[path] = crit_ord

    # -----------------------------------------------------------------------
    # Group 1: Path Presence — binary (does this capability exist?)
    # -----------------------------------------------------------------------
    presence_offset = offset
    offset += ctx.n_paths

    for path, max_ord in sample_paths.items():
        if max_ord >= 2:  # baseline or above
            feat_idx = ctx.presence_lookup.get(path)
            if feat_idx is not None:
                vec[presence_offset + feat_idx] = 1.0

    # -----------------------------------------------------------------------
    # Group 2: Path Max Criticality — ordinal 0-5 (cleave's severity gradient)
    # -----------------------------------------------------------------------
    maxcrit_offset = offset
    offset += ctx.n_paths

    for path, max_ord in sample_paths.items():
        feat_idx = ctx.presence_lookup.get(path)
        if feat_idx is not None:
            vec[maxcrit_offset + feat_idx] = float(max_ord)

    # -----------------------------------------------------------------------
    # Group 3: Path Aggregates (8 features) — ratio-based, not counts
    # -----------------------------------------------------------------------
    agg_offset = offset
    offset += 8

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

    vec[agg_offset] = max_crit
    vec[agg_offset + 1] = len(categories)
    vec[agg_offset + 2] = math.log1p(path_breadth_any)
    vec[agg_offset + 3] = math.log1p(total_active)
    # Concentration ratios — what fraction of behavior is suspicious?
    vec[agg_offset + 4] = breadth_suspicious / max(path_breadth_any, 1)
    vec[agg_offset + 5] = breadth_hostile / max(path_breadth_any, 1)
    vec[agg_offset + 6] = breadth_suspicious / max(breadth_notable, 1)
    vec[agg_offset + 7] = breadth_notable_only / max(breadth_notable, 1)

    # -----------------------------------------------------------------------
    # Group 4: Third-Party / Well-Known Summary (6 features)
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
    # Group 5: Key Metrics (16 features)
    # -----------------------------------------------------------------------
    metrics = pf.get("metrics") or {}
    for group, fname, use_log in KEY_METRICS:
        val = _float((metrics.get(group) or {}).get(fname))
        if use_log:
            val = math.log1p(abs(val))
        vec[offset] = val
        offset += 1

    # -----------------------------------------------------------------------
    # Group 6: File Type one-hot
    # -----------------------------------------------------------------------
    idx = ctx.ft_lookup.get(pf.get("file_type", ""))
    if idx is not None:
        vec[offset + idx] = 1.0
    offset += ctx.n_ft

    # -----------------------------------------------------------------------
    # Group 7: Structural (4 features)
    # -----------------------------------------------------------------------
    file_size = pf.get("size", 0)
    file_type = pf.get("file_type", "")
    is_binary = file_type in ("pe", "elf", "macho")
    imports = pf.get("imports") or []

    vec[offset] = 1.0 if (is_binary and file_size < 20000) else 0.0
    vec[offset + 1] = 1.0 if len(imports) == 0 else 0.0
    vec[offset + 2] = 1.0 if filtered_finding_count == 0 else 0.0
    vec[offset + 3] = math.log1p(filtered_finding_count)
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
) -> tuple[sp.csr_matrix, np.ndarray]:
    """Extract feature vectors for all samples as a sparse CSR matrix."""
    return extract_stream(zip(reports, labels), spec)


def extract_stream(
    report_labels: Iterable[tuple[dict[str, Any], int]],
    spec: FeatureSpec,
) -> tuple[sp.csr_matrix, np.ndarray]:
    """Extract features by streaming (report, label) pairs.

    Each report is parsed, its features extracted into sparse COO entries,
    and then discarded — only the sparse indices/values and labels are kept.
    """
    ctx = _ExtractContext(spec)
    rows: list[int] = []
    cols: list[int] = []
    vals: list[float] = []
    labels: list[int] = []
    vec = np.zeros(spec.total_features, dtype=np.float32)

    n = 0
    for report, label in report_labels:
        vec[:] = 0.0
        _extract_into(report, ctx, vec)
        nz = np.nonzero(vec)[0]
        rows.extend([n] * len(nz))
        cols.extend(nz.tolist())
        vals.extend(vec[nz].tolist())
        labels.append(label)
        n += 1

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
