"""Extract fixed-size numeric feature vectors from cleave v3 AnalysisReport JSON.

v14: Capability-first features plus high-criticality finding-density signals.

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
  3. Path Aggregates: breadth, concentration, and finding-density signals (16)
  4. Third-Party / Well-Known Summary: aggregated match signals (6)
  5. Key Metrics: curated binary/text/PE metrics (16)
  6. File Type: one-hot (corpus-dependent, ~30-40)
  7. Structural: anomalies + finding count (4)
"""

from __future__ import annotations

import json
import logging
import math
import multiprocessing as mp
import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from collections.abc import Iterable
from itertools import islice
from typing import Any, TypeVar

import numpy as np
import scipy.sparse as sp

log = logging.getLogger(__name__)
T = TypeVar("T")

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

FEATURE_GROUPS = ("present", "maxcrit", "agg", "ext", "metrics", "filetype", "struct")


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

    Version 14: capability-first features. Each path in presence_vocab gets
    two features: a binary presence flag and an ordinal max-criticality value.
    No path×tier binary features — criticality is a gradient, not a threshold.
    """

    # NOTE: bumping this version requires a matching update in ../collimator (Rust).
    version: int = 14
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
                "loading feature spec version %d (expected 14); "
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

def build_vocab(reports: Iterable[dict[str, Any] | str], n_workers: int = 0) -> FeatureSpec:
    """Scan all reports to build the feature vocabulary.

    Each path that appears in >= MIN_PATH_FREQ samples gets two features:
      - present:X  (binary) — capability exists at any crit ≥ baseline
      - maxcrit:X  (ordinal 0-5) — cleave's max criticality for this path

    This lets the model learn from capability combinations (presence) while
    optionally using criticality as a gradient signal (maxcrit). No binary
    tier thresholds — the model decides what criticality levels matter.

    Accepts any iterable of report dicts or raw JSON strings.
    """
    nw = resolve_worker_count(n_workers)
    presence_counts: dict[str, int] = {}
    filetypes: set[str] = set()
    batch_size = max(64, 512 // max(nw, 1))

    def _merge_batch(counts: dict[str, int], fts: list[str]) -> None:
        for k, v in counts.items():
            presence_counts[k] = presence_counts.get(k, 0) + v
        filetypes.update(fts)

    if nw > 1:
        with ProcessPoolExecutor(
            max_workers=nw,
            mp_context=mp.get_context("spawn"),
        ) as pool:
            for counts, fts in pool.map(
                _vocab_batch_worker,
                _batched(reports, batch_size),
            ):
                _merge_batch(counts, fts)

    if nw <= 1:
        for counts, fts in map(_vocab_batch_worker, _batched(reports, batch_size)):
            _merge_batch(counts, fts)

    presence_vocab = sorted(k for k, c in presence_counts.items() if c >= MIN_PATH_FREQ)
    filetype_vocab = sorted(filetypes)

    feature_names: list[str] = []

    # Group 1: Path Presence — binary (capability exists?).
    for path in presence_vocab:
        feature_names.append(f"present:{path}")

    # Group 2: Path Max Criticality — ordinal 0-5 (cleave's severity gradient).
    for path in presence_vocab:
        feature_names.append(f"maxcrit:{path}")

    # Group 3: Path Aggregates (16).
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
        "agg:notable_findings_log",      # log1p of notable+ exact findings
        "agg:suspicious_findings_log",   # log1p of suspicious+ exact findings
        "agg:hostile_findings_log",      # log1p of hostile exact findings
        "agg:notable_finding_ratio",     # notable+ / all filtered findings
        "agg:suspicious_finding_ratio",  # suspicious+ / all filtered findings
        "agg:hostile_finding_ratio",     # hostile / all filtered findings
        "agg:unique_suspicious_ids_log", # log1p of unique suspicious+ trait IDs
        "agg:unique_hostile_ids_log",    # log1p of unique hostile trait IDs
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
        "(v14 presence+maxcrit+density)",
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


@dataclass(slots=True)
class _FindingSummary:
    sample_paths: dict[str, int]
    filtered_finding_count: int
    notable_finding_count: int
    suspicious_finding_count: int
    hostile_finding_count: int
    unique_suspicious_ids: int
    unique_hostile_ids: int
    third_party_max_crit: int
    third_party_count: int
    well_known_max_crit: int
    well_known_hostile: int
    well_known_suspicious: int
    has_yara: bool


def _summarize_findings(findings: list[dict[str, Any]]) -> _FindingSummary:
    """Collect reusable per-report finding statistics."""
    sample_paths: dict[str, int] = {}
    filtered_finding_count = 0
    notable_finding_count = 0
    suspicious_finding_count = 0
    hostile_finding_count = 0
    suspicious_ids: set[str] = set()
    hostile_ids: set[str] = set()
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
        if crit_ord >= 3:
            notable_finding_count += 1
        if crit_ord >= 4:
            suspicious_finding_count += 1
            suspicious_ids.add(fid)
        if crit_ord >= 5:
            hostile_finding_count += 1
            hostile_ids.add(fid)

        top = fid.split("/")[0]
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

    return _FindingSummary(
        sample_paths=sample_paths,
        filtered_finding_count=filtered_finding_count,
        notable_finding_count=notable_finding_count,
        suspicious_finding_count=suspicious_finding_count,
        hostile_finding_count=hostile_finding_count,
        unique_suspicious_ids=len(suspicious_ids),
        unique_hostile_ids=len(hostile_ids),
        third_party_max_crit=third_party_max_crit,
        third_party_count=third_party_count,
        well_known_max_crit=well_known_max_crit,
        well_known_hostile=well_known_hostile,
        well_known_suspicious=well_known_suspicious,
        has_yara=has_yara,
    )


def _apply_presence_features(
    sample_paths: dict[str, int],
    ctx: _ExtractContext,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 1: path presence features."""
    for path, max_ord in sample_paths.items():
        if max_ord >= 2:  # baseline or above
            feat_idx = ctx.presence_lookup.get(path)
            if feat_idx is not None:
                vec[offset + feat_idx] = 1.0
    return offset + ctx.n_paths


def _apply_maxcrit_features(
    sample_paths: dict[str, int],
    ctx: _ExtractContext,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 2: path maximum criticality features."""
    for path, max_ord in sample_paths.items():
        feat_idx = ctx.presence_lookup.get(path)
        if feat_idx is not None:
            vec[offset + feat_idx] = float(max_ord)
    return offset + ctx.n_paths


def _apply_aggregate_features(
    summary: _FindingSummary,
    vec: np.ndarray,
    offset: int,
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

    vec[offset] = max_crit
    vec[offset + 1] = len(categories)
    vec[offset + 2] = math.log1p(path_breadth_any)
    vec[offset + 3] = math.log1p(total_active)
    # Concentration ratios — what fraction of behavior is suspicious?
    vec[offset + 4] = breadth_suspicious / max(path_breadth_any, 1)
    vec[offset + 5] = breadth_hostile / max(path_breadth_any, 1)
    vec[offset + 6] = breadth_suspicious / max(breadth_notable, 1)
    vec[offset + 7] = breadth_notable_only / max(breadth_notable, 1)
    vec[offset + 8] = math.log1p(summary.notable_finding_count)
    vec[offset + 9] = math.log1p(summary.suspicious_finding_count)
    vec[offset + 10] = math.log1p(summary.hostile_finding_count)
    vec[offset + 11] = summary.notable_finding_count / max(summary.filtered_finding_count, 1)
    vec[offset + 12] = summary.suspicious_finding_count / max(summary.filtered_finding_count, 1)
    vec[offset + 13] = summary.hostile_finding_count / max(summary.filtered_finding_count, 1)
    vec[offset + 14] = math.log1p(summary.unique_suspicious_ids)
    vec[offset + 15] = math.log1p(summary.unique_hostile_ids)
    return offset + 16


def _apply_external_signal_features(
    summary: _FindingSummary,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 4: aggregated third-party and well-known signals."""
    vec[offset] = summary.third_party_max_crit
    vec[offset + 1] = math.log1p(summary.third_party_count)
    vec[offset + 2] = summary.well_known_max_crit
    vec[offset + 3] = summary.well_known_hostile
    vec[offset + 4] = summary.well_known_suspicious
    vec[offset + 5] = 1.0 if summary.has_yara else 0.0
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
        vec[offset] = val
        offset += 1
    return offset


def _apply_filetype_features(
    pf: dict[str, Any],
    ctx: _ExtractContext,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 6: file type one-hot features."""
    idx = ctx.ft_lookup.get(pf.get("file_type", ""))
    if idx is not None:
        vec[offset + idx] = 1.0
    return offset + ctx.n_ft


def _apply_structural_features(
    pf: dict[str, Any],
    filtered_finding_count: int,
    vec: np.ndarray,
    offset: int,
) -> int:
    """Group 7: structural anomaly features."""
    file_size = pf.get("size", 0)
    file_type = pf.get("file_type", "")
    is_binary = file_type in ("pe", "elf", "macho")
    imports = pf.get("imports") or []

    vec[offset] = 1.0 if (is_binary and file_size < 20000) else 0.0
    vec[offset + 1] = 1.0 if len(imports) == 0 else 0.0
    vec[offset + 2] = 1.0 if filtered_finding_count == 0 else 0.0
    vec[offset + 3] = math.log1p(filtered_finding_count)
    return offset + 4


def _extract_into(report: dict[str, Any], ctx: _ExtractContext, vec: np.ndarray) -> None:
    """Extract features from a report into a pre-allocated vector."""
    pf = primary_file(report)
    summary = _summarize_findings(pf.get("findings") or [])

    offset = 0
    offset = _apply_presence_features(summary.sample_paths, ctx, vec, offset)
    offset = _apply_maxcrit_features(summary.sample_paths, ctx, vec, offset)
    offset = _apply_aggregate_features(summary, vec, offset)
    offset = _apply_external_signal_features(summary, vec, offset)
    offset = _apply_metric_features(pf.get("metrics") or {}, vec, offset)
    offset = _apply_filetype_features(pf, ctx, vec, offset)
    _apply_structural_features(pf, summary.filtered_finding_count, vec, offset)


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
    reports: list[dict[str, Any] | str],
) -> tuple[dict[str, int], list[str]]:
    """Count path occurrences for a batch of reports. CPU-only."""
    presence_counts: dict[str, int] = {}
    filetypes: list[str] = []
    for raw_report in reports:
        report = _coerce_report(raw_report)
        if report is None:
            continue
        pf = primary_file(report)
        ftype = pf.get("file_type", "")
        if ftype:
            filetypes.append(ftype)
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
    return presence_counts, filetypes


def _extract_batch_worker(
    args: tuple[int, list[tuple[dict[str, Any] | str, int]], FeatureSpec],
) -> tuple[list[int], list[int], list[float], list[int]]:
    """Extract features from a batch of (report, label) pairs. CPU-only."""
    offset, batch, spec = args
    ctx = _ExtractContext(spec)
    vec = np.zeros(spec.total_features, dtype=np.float32)
    rows: list[int] = []
    cols: list[int] = []
    vals: list[float] = []
    labels: list[int] = []
    for i, (raw_report, label) in enumerate(batch):
        report = _coerce_report(raw_report)
        if report is None:
            continue
        vec[:] = 0.0
        _extract_into(report, ctx, vec)
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
    return min(max(cpu_count // 2, 2), 16)


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
) -> tuple[sp.csr_matrix, np.ndarray]:
    """Extract feature vectors for all samples as a sparse CSR matrix."""
    return extract_stream(zip(reports, labels), spec)


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
    batch_size = max(64, 512 // max(nw, 1))

    def _consume(batch_iter: Iterable[tuple[list[int], list[int], list[float], list[int]]]) -> None:
        for b_rows, b_cols, b_vals, b_labels in batch_iter:
            rows.extend(b_rows)
            cols.extend(b_cols)
            vals.extend(b_vals)
            labels.extend(b_labels)

    if nw > 1:
        with ProcessPoolExecutor(
            max_workers=nw,
            mp_context=mp.get_context("spawn"),
        ) as pool:
            _consume(
                pool.map(
                    _extract_batch_worker,
                    (
                        (offset, batch, spec)
                        for offset, batch in _enumerate_batches(report_labels, batch_size)
                    ),
                )
            )

    if nw <= 1:
        _consume(
            map(
                _extract_batch_worker,
                (
                    (offset, batch, spec)
                    for offset, batch in _enumerate_batches(report_labels, batch_size)
                ),
            )
        )

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

    for raw_report, label, is_test in batch:
        report = _coerce_report(raw_report)
        if report is None:
            continue
        vec[:] = 0.0
        _extract_into(report, ctx, vec)
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


def extract_partitioned_stream(
    report_labels_split: Iterable[tuple[dict[str, Any] | str, int, bool]],
    spec: FeatureSpec,
    n_workers: int = 0,
) -> tuple[sp.csr_matrix, np.ndarray, sp.csr_matrix, np.ndarray]:
    """Extract train and test matrices from a mixed stream in one pass."""
    nw = resolve_worker_count(n_workers)
    batch_size = max(64, 512 // max(nw, 1))

    train_rows: list[int] = []
    train_cols: list[int] = []
    train_vals: list[float] = []
    train_labels: list[int] = []

    test_rows: list[int] = []
    test_cols: list[int] = []
    test_vals: list[float] = []
    test_labels: list[int] = []

    def _consume(
        batch_iter: Iterable[
            tuple[
                list[int], list[int], list[float], list[int],
                list[int], list[int], list[float], list[int],
            ]
        ],
    ) -> None:
        for (
            b_train_rows, b_train_cols, b_train_vals, b_train_labels,
            b_test_rows, b_test_cols, b_test_vals, b_test_labels,
        ) in batch_iter:
            train_rows.extend(b_train_rows)
            train_cols.extend(b_train_cols)
            train_vals.extend(b_train_vals)
            train_labels.extend(b_train_labels)
            test_rows.extend(b_test_rows)
            test_cols.extend(b_test_cols)
            test_vals.extend(b_test_vals)
            test_labels.extend(b_test_labels)

    batch_args = (
        (train_offset, test_offset, batch, spec)
        for train_offset, test_offset, batch in _enumerate_partitioned_batches(
            report_labels_split,
            batch_size,
        )
    )

    if nw > 1:
        with ProcessPoolExecutor(
            max_workers=nw,
            mp_context=mp.get_context("spawn"),
        ) as pool:
            _consume(pool.map(_extract_partitioned_batch_worker, batch_args))
    else:
        _consume(map(_extract_partitioned_batch_worker, batch_args))

    n_train = len(train_labels)
    n_test = len(test_labels)
    X_train = sp.csr_matrix(
        (
            np.array(train_vals, dtype=np.float32),
            (np.array(train_rows, dtype=np.int32), np.array(train_cols, dtype=np.int32)),
        ),
        shape=(n_train, spec.total_features),
    )
    y_train = np.array(train_labels, dtype=np.float32)

    X_test = sp.csr_matrix(
        (
            np.array(test_vals, dtype=np.float32),
            (np.array(test_rows, dtype=np.int32), np.array(test_cols, dtype=np.int32)),
        ),
        shape=(n_test, spec.total_features),
    )
    y_test = np.array(test_labels, dtype=np.float32)

    log.info(
        "extracted %d train + %d test samples x %d features",
        n_train, n_test, spec.total_features,
    )
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
