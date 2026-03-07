"""Extract fixed-size numeric feature vectors from cleave v3 AnalysisReport JSON.

Each sample's cleave_json is parsed into a feature vector suitable for the MLP.
The vocabulary (taxonomy prefixes, evidence methods, etc.) is built from the
training corpus and exported alongside the model so Rust can construct identical
vectors.

All data lives in the report's files[] array. The primary file (files[0]) is
used for feature extraction.

Feature groups:
  1.  Taxonomy: 2 slots per prefix (max crit ordinal + log1p count)
  2.  Criticality histogram: count per level (6)
  3.  Criticality ratios: hostile/suspicious/above-notable fractions (3)
  4.  Criticality weighted: confidence-weighted hostile + suspicious scores (2)
  5.  Confidence stats: mean/max/min/stddev (4)
  6.  Behavior summary: ATT&CK + MBC aggregate counts (4)
  7.  Evidence methods: count per method type
  8.  String type distribution: count per type + suspicious/encoded/network ratios
  9.  Section metrics: count, entropy stats, permissions (5)
  10. Metrics passthrough: all discovered numeric metric fields
  11. File type: one-hot
  12. Aggregate stats: counts, risk, size, depth (9)
  13. Finding behavior: diversity, match counts, evidence density (4)
"""

from __future__ import annotations

import json
import logging
import math
from collections import Counter
from dataclasses import dataclass, field
from functools import cache
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
CRITICALITY_LEVELS = list(CRITICALITY_ORDINAL.keys())

RISK_ORDINAL: dict[str, int] = {
    "": 0,
    "filtered": 0,
    "component": 1,
    "baseline": 2,
    "notable": 3,
    "suspicious": 4,
    "hostile": 5,
}

SUSPICIOUS_STRING_TYPES = frozenset({
    "Base64", "ShellCmd", "CommandInjection", "CryptoWallet",
    "SuspiciousPath", "StackString", "AppleScript",
})
ENCODED_STRING_TYPES = frozenset({
    "Base64", "Base32", "UrlEncoded", "JWT",
})
NETWORK_STRING_TYPES = frozenset({
    "Url", "IP",
})

# Vocabulary limits.
MAX_TAXONOMY_VOCAB = 200
MIN_TAXONOMY_FREQUENCY = 3

# Metric field name keywords that indicate large-scale values benefiting from log1p.
_LOG_KEYWORDS = frozenset({"count", "total", "size", "bytes", "chars", "lines"})


def _should_log_scale(field_name: str) -> bool:
    """Whether a metric field benefits from log1p scaling."""
    if any(kw in field_name for kw in ("ratio", "entropy", "density", "avg", "stddev", "per_")):
        return False
    if field_name.startswith(("is_", "has_")):
        return False
    return any(kw in field_name for kw in _LOG_KEYWORDS)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@cache
def _taxonomy_prefixes(finding_id: str) -> tuple[str, ...]:
    """Extract ancestor prefixes from a finding ID.

    "objectives/anti-analysis/timing::ast" -> (
        "objectives",
        "objectives/anti-analysis",
        "objectives/anti-analysis/timing",
    )

    The :: suffix (rule variant) is stripped before splitting.
    """
    base = finding_id.split("::")[0] if "::" in finding_id else finding_id
    parts = base.split("/")
    return tuple("/".join(parts[:i]) for i in range(1, len(parts) + 1))


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


# ---------------------------------------------------------------------------
# FeatureSpec
# ---------------------------------------------------------------------------

@dataclass
class FeatureSpec:
    """Describes the feature vector layout. Exported for Rust inference parity."""

    version: int = 9
    taxonomy_vocab: list[str] = field(default_factory=list)
    evidence_vocab: list[str] = field(default_factory=list)
    string_type_vocab: list[str] = field(default_factory=list)
    metric_vocab: list[str] = field(default_factory=list)
    filetype_vocab: list[str] = field(default_factory=list)
    feature_names: list[str] = field(default_factory=list)
    total_features: int = 0
    feature_means: list[float] | None = None
    feature_stds: list[float] | None = None

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        d: dict[str, Any] = {
            "version": self.version,
            "taxonomy_vocab": self.taxonomy_vocab,
            "evidence_vocab": self.evidence_vocab,
            "string_type_vocab": self.string_type_vocab,
            "metric_vocab": self.metric_vocab,
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
        version = data.get("version", 9)
        if version < 9:
            log.warning(
                "loading feature spec version %d (expected 9); "
                "models trained with older versions are not compatible",
                version,
            )
        return cls(
            version=version,
            taxonomy_vocab=data.get("taxonomy_vocab", []),
            evidence_vocab=data.get("evidence_vocab", []),
            string_type_vocab=data.get("string_type_vocab", []),
            metric_vocab=data.get("metric_vocab", []),
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
    """Scan all reports to build the feature vocabulary."""
    taxonomy_counts: Counter[str] = Counter()
    evidence_methods: set[str] = set()
    string_types: set[str] = set()
    metric_fields: set[str] = set()
    filetypes: set[str] = set()

    for report in reports:
        pf = primary_file(report)
        findings = pf.get("findings") or []

        # Taxonomy prefixes (deduplicated per report).
        seen_prefixes: set[str] = set()
        for finding in findings:
            fid = finding.get("id", "")
            if fid:
                for prefix in _taxonomy_prefixes(fid):
                    seen_prefixes.add(prefix)
        for prefix in seen_prefixes:
            taxonomy_counts[prefix] += 1

        # Evidence methods.
        for finding in findings:
            for ev in finding.get("evidence") or []:
                method = ev.get("method", "")
                if method:
                    evidence_methods.add(method)

        # String types.
        for s in pf.get("strings") or []:
            stype = s.get("type", "")
            if stype:
                string_types.add(stype)

        # Metric fields (only numeric values).
        for group, fields in (pf.get("metrics") or {}).items():
            if isinstance(fields, dict):
                for fname, val in fields.items():
                    if isinstance(val, (int, float)):
                        metric_fields.add(f"{group}:{fname}")

        # File type.
        ftype = pf.get("file_type", "")
        if ftype:
            filetypes.add(ftype)

    # --- Build vocabularies ---
    min_freq = MIN_TAXONOMY_FREQUENCY if len(reports) >= MIN_TAXONOMY_FREQUENCY else 1
    taxonomy_all = [(p, c) for p, c in taxonomy_counts.most_common() if c >= min_freq]
    taxonomy_vocab = [p for p, _ in taxonomy_all[:MAX_TAXONOMY_VOCAB]]
    evidence_vocab = sorted(evidence_methods)
    string_type_vocab = sorted(string_types)
    metric_vocab = sorted(metric_fields)
    filetype_vocab = sorted(filetypes)

    # --- Build feature name list ---
    feature_names: list[str] = []

    # Group 1: Taxonomy (2 slots per prefix: max crit + log1p count).
    for prefix in taxonomy_vocab:
        feature_names.append(f"taxon_crit:{prefix}")
        feature_names.append(f"taxon_count:{prefix}")

    # Group 2: Criticality histogram (6 levels).
    for level in CRITICALITY_LEVELS:
        feature_names.append(f"crit_count:{level}")

    # Group 3: Criticality ratios (3).
    feature_names.extend([
        "crit_ratio:hostile", "crit_ratio:suspicious", "crit_ratio:above_notable",
    ])

    # Group 4: Criticality weighted (2).
    feature_names.extend(["crit_weighted:hostile", "crit_weighted:suspicious"])

    # Group 5: Confidence stats (4).
    feature_names.extend(["conf:mean", "conf:max", "conf:min", "conf:stddev"])

    # Group 6: Behavior summary (4).
    feature_names.extend([
        "behavior:attack_unique", "behavior:attack_total",
        "behavior:mbc_unique", "behavior:mbc_total",
    ])

    # Group 7: Evidence method counts.
    for method in evidence_vocab:
        feature_names.append(f"evidence:{method}")

    # Group 8: String type distribution + ratios.
    for stype in string_type_vocab:
        feature_names.append(f"string_type:{stype}")
    feature_names.extend([
        "string_ratio:suspicious", "string_ratio:encoded", "string_ratio:network",
    ])

    # Group 9: Section metrics (5).
    feature_names.extend([
        "sections:count", "sections:avg_entropy", "sections:max_entropy",
        "sections:wx_count", "sections:max_size_log",
    ])

    # Group 10: Metrics passthrough.
    for mf in metric_vocab:
        group, fname = mf.split(":", 1)
        feature_names.append(f"metrics:{group}_{fname}")

    # Group 11: File type one-hot.
    for ft in filetype_vocab:
        feature_names.append(f"filetype:{ft}")

    # Group 12: Aggregate stats (9).
    feature_names.extend([
        "agg:finding_count", "agg:risk_ordinal", "agg:string_count",
        "agg:import_count", "agg:log_size", "agg:depth",
        "agg:hostile_count", "agg:suspicious_count", "agg:notable_count",
    ])

    # Group 13: Finding behavior (4).
    feature_names.extend([
        "finding:diversity", "finding:avg_match",
        "finding:avg_evidence", "finding:evidence_total",
    ])

    spec = FeatureSpec(
        taxonomy_vocab=taxonomy_vocab,
        evidence_vocab=evidence_vocab,
        string_type_vocab=string_type_vocab,
        metric_vocab=metric_vocab,
        filetype_vocab=filetype_vocab,
        feature_names=feature_names,
        total_features=len(feature_names),
    )
    log.info(
        "vocab: %d taxonomy, %d evidence, %d string_types, "
        "%d metrics, %d filetypes -> %d features",
        len(taxonomy_vocab), len(evidence_vocab), len(string_type_vocab),
        len(metric_vocab), len(filetype_vocab), spec.total_features,
    )
    return spec


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------

class _ExtractContext:
    """Pre-built lookup tables for fast repeated extraction against a spec."""

    __slots__ = (
        "taxon_lookup", "evidence_lookup", "string_type_lookup", "ft_lookup",
        "n_taxon", "n_evidence", "n_string_type", "n_ft",
        "metric_vocab", "total_features",
    )

    def __init__(self, spec: FeatureSpec) -> None:
        self.taxon_lookup = {p: i for i, p in enumerate(spec.taxonomy_vocab)}
        self.evidence_lookup = {m: i for i, m in enumerate(spec.evidence_vocab)}
        self.string_type_lookup = {t: i for i, t in enumerate(spec.string_type_vocab)}
        self.ft_lookup = {ft: i for i, ft in enumerate(spec.filetype_vocab)}
        self.n_taxon = len(spec.taxonomy_vocab)
        self.n_evidence = len(spec.evidence_vocab)
        self.n_string_type = len(spec.string_type_vocab)
        self.n_ft = len(spec.filetype_vocab)
        self.metric_vocab = spec.metric_vocab
        self.total_features = spec.total_features


def _extract_into(report: dict[str, Any], ctx: _ExtractContext, vec: np.ndarray) -> None:
    """Extract features from a report into a pre-allocated vector."""
    pf = primary_file(report)
    findings = pf.get("findings") or []
    offset = 0

    # --- Group 1: Taxonomy (max crit + log1p count per prefix) ---
    taxon_lookup = ctx.taxon_lookup
    taxon_crit: dict[str, int] = {}
    taxon_count: dict[str, int] = {}
    for finding in findings:
        fid = finding.get("id", "")
        if not fid:
            continue
        crit = CRITICALITY_ORDINAL.get(finding.get("crit", "baseline"), 2)
        for prefix in _taxonomy_prefixes(fid):
            if prefix in taxon_lookup:
                prev = taxon_crit.get(prefix, 0)
                if crit > prev:
                    taxon_crit[prefix] = crit
                taxon_count[prefix] = taxon_count.get(prefix, 0) + 1
    for prefix, slot in taxon_lookup.items():
        base = offset + slot * 2
        c = taxon_crit.get(prefix)
        if c is not None:
            vec[base] = c
            vec[base + 1] = math.log1p(taxon_count[prefix])
    offset += ctx.n_taxon * 2

    # --- Group 2: Criticality histogram ---
    crit_counts: dict[str, int] = {}
    for finding in findings:
        c = finding.get("crit", "baseline")
        crit_counts[c] = crit_counts.get(c, 0) + 1
    for i, level in enumerate(CRITICALITY_LEVELS):
        v = crit_counts.get(level)
        if v is not None:
            vec[offset + i] = v
    offset += len(CRITICALITY_LEVELS)

    # --- Group 3: Criticality ratios ---
    n_findings = len(findings) or 1
    hostile = crit_counts.get("hostile", 0)
    suspicious = crit_counts.get("suspicious", 0)
    vec[offset] = hostile / n_findings
    vec[offset + 1] = suspicious / n_findings
    vec[offset + 2] = (hostile + suspicious) / n_findings
    offset += 3

    # --- Group 4: Criticality weighted (confidence-weighted scores) ---
    hostile_conf_sum = 0.0
    suspicious_conf_sum = 0.0
    for finding in findings:
        c = finding.get("crit", "baseline")
        conf = finding.get("conf", 0.5)
        if c == "hostile":
            hostile_conf_sum += conf
        elif c == "suspicious":
            suspicious_conf_sum += conf
    vec[offset] = hostile_conf_sum
    vec[offset + 1] = suspicious_conf_sum
    offset += 2

    # --- Group 5: Confidence stats ---
    if findings:
        confs = [finding.get("conf", 0.5) for finding in findings]
        mean_conf = sum(confs) / len(confs)
        vec[offset] = mean_conf
        vec[offset + 1] = max(confs)
        vec[offset + 2] = min(confs)
        if len(confs) > 1:
            var = sum((c - mean_conf) ** 2 for c in confs) / len(confs)
            vec[offset + 3] = math.sqrt(var)
    offset += 4

    # --- Group 6: Behavior summary ---
    seen_attacks: set[str] = set()
    total_attack_refs = 0
    seen_mbc: set[str] = set()
    total_mbc_refs = 0
    for finding in findings:
        attack = finding.get("attack")
        if attack:
            total_attack_refs += 1
            seen_attacks.add(attack)
        mbc = finding.get("mbc")
        if mbc:
            total_mbc_refs += 1
            seen_mbc.add(mbc)
    vec[offset] = len(seen_attacks)
    vec[offset + 1] = total_attack_refs
    vec[offset + 2] = len(seen_mbc)
    vec[offset + 3] = total_mbc_refs
    offset += 4

    # --- Group 7: Evidence method counts ---
    evidence_lookup = ctx.evidence_lookup
    total_evidence = 0
    for finding in findings:
        for ev in finding.get("evidence") or []:
            total_evidence += 1
            idx = evidence_lookup.get(ev.get("method", ""))
            if idx is not None:
                vec[offset + idx] += 1.0
    offset += ctx.n_evidence

    # --- Group 8: String type distribution ---
    string_type_lookup = ctx.string_type_lookup
    strings = pf.get("strings") or []
    suspicious_count = 0
    encoded_count = 0
    network_count = 0
    for s in strings:
        stype = s.get("type", "")
        idx = string_type_lookup.get(stype)
        if idx is not None:
            vec[offset + idx] += 1.0
        if stype in SUSPICIOUS_STRING_TYPES:
            suspicious_count += 1
        if stype in ENCODED_STRING_TYPES:
            encoded_count += 1
        if stype in NETWORK_STRING_TYPES:
            network_count += 1
    offset += ctx.n_string_type
    n_strings = len(strings) or 1
    vec[offset] = suspicious_count / n_strings
    vec[offset + 1] = encoded_count / n_strings
    vec[offset + 2] = network_count / n_strings
    offset += 3

    # --- Group 9: Section metrics ---
    sections = pf.get("sections") or []
    vec[offset] = len(sections)
    if sections:
        entropies = [s.get("entropy", 0.0) for s in sections]
        sizes = [s.get("size", 0) for s in sections]
        vec[offset + 1] = sum(entropies) / len(entropies)
        vec[offset + 2] = max(entropies)
        wx = sum(
            1 for s in sections
            if "w" in (s.get("permissions") or "") and "x" in (s.get("permissions") or "")
        )
        vec[offset + 3] = wx
        vec[offset + 4] = math.log1p(max(sizes)) if sizes else 0.0
    offset += 5

    # --- Group 10: Metrics passthrough ---
    metrics = pf.get("metrics") or {}
    for mf in ctx.metric_vocab:
        group, fname = mf.split(":", 1)
        val = _float((metrics.get(group) or {}).get(fname))
        if _should_log_scale(fname):
            val = math.log1p(abs(val))
        vec[offset] = val
        offset += 1

    # --- Group 11: File type one-hot ---
    idx = ctx.ft_lookup.get(pf.get("file_type", ""))
    if idx is not None:
        vec[offset + idx] = 1.0
    offset += ctx.n_ft

    # --- Group 12: Aggregate stats ---
    counts = pf.get("counts") or {}
    imports = pf.get("imports") or []
    vec[offset] = len(findings)
    vec[offset + 1] = RISK_ORDINAL.get(pf.get("risk", ""), 0)
    vec[offset + 2] = len(strings)
    vec[offset + 3] = len(imports)
    vec[offset + 4] = math.log1p(pf.get("size", 0))
    vec[offset + 5] = pf.get("depth", 0)
    vec[offset + 6] = counts.get("hostile", 0)
    vec[offset + 7] = counts.get("suspicious", 0)
    vec[offset + 8] = counts.get("notable", 0)
    offset += 9

    # --- Group 13: Finding behavior ---
    if findings:
        unique_ids = len({f.get("id", "") for f in findings})
        vec[offset] = unique_ids / len(findings)  # diversity

        match_counts = [f.get("match_count", 1) for f in findings]
        vec[offset + 1] = sum(match_counts) / len(match_counts)  # avg match

        evidence_counts = [len(f.get("evidence") or []) for f in findings]
        vec[offset + 2] = sum(evidence_counts) / len(evidence_counts)  # avg evidence
    vec[offset + 3] = total_evidence  # evidence total


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
