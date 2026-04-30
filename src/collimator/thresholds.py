"""Show confidence thresholds required for various accuracy levels."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from itertools import islice
from pathlib import Path
from typing import Any

import numpy as np

from . import data, features, train
from .model import load_model, predict_proba

log = logging.getLogger(__name__)

ACCURACY_TARGETS = [0.80, 0.90, 0.95, 0.98, 0.99, 0.993, 0.996, 0.998, 0.999, 0.9991, 0.9992, 0.9993, 0.9994, 0.9995, 0.9996, 0.9997, 0.9998, 0.9999, 0.99999]

# (label, max FPR): lowest threshold (highest recall) meeting the FPR ceiling.
# Used by `compute_recommendations` (legacy FPR-based mode).
RECOMMENDATIONS = [
    ("suspicious", 0.00002),   # FPR ≤ 20 per million
    ("hostile",    0.000001),  # FPR ≤ 1 per million
]

# Minimum benign samples needed to trust an FPR target (expect ≥5 FP at that rate).
MIN_SAMPLES_FOR_FPR = 5

# (label, min precision): lowest threshold (highest recall) where precision
# (TP / (TP+FP)) on the test set meets or exceeds the floor.
# Used by `compute_precision_recommendations` (legacy, not the default).
PRECISION_RECOMMENDATIONS = [
    ("suspicious", 0.995),
    ("hostile",    0.9995),
]

# Minimum number of flagged samples required before a precision number is
# trustworthy. Avoids picking a threshold based on 1-2 samples.
MIN_FLAGGED_FOR_PRECISION = 50

# Deployment operating points, expressed as false positives per million good
# files. Level 5 is the legacy default: hostile <=1/1M, suspicious <=10/1M.
SEVERITY_LEVEL_TARGETS = [
    {"level": 1, "hostile_per_million": 0.0, "suspicious_per_million": 0.0},
    {"level": 2, "hostile_per_million": 0.0, "suspicious_per_million": 2.0},
    {"level": 3, "hostile_per_million": 0.0, "suspicious_per_million": 4.0},
    {"level": 4, "hostile_per_million": 0.0, "suspicious_per_million": 8.0},
    {"level": 5, "hostile_per_million": 1.0, "suspicious_per_million": 10.0},
    {"level": 6, "hostile_per_million": 2.0, "suspicious_per_million": 20.0},
    {"level": 7, "hostile_per_million": 3.0, "suspicious_per_million": 30.0},
    {"level": 8, "hostile_per_million": 4.0, "suspicious_per_million": 40.0},
    {"level": 9, "hostile_per_million": 5.0, "suspicious_per_million": 50.0},
]

DEFAULT_SEVERITY_LEVEL = 5

# Legacy aliases retained for existing litmus config consumers.
DEFAULT_FP_RATE_RECOMMENDATIONS = [
    ("suspicious", SEVERITY_LEVEL_TARGETS[DEFAULT_SEVERITY_LEVEL - 1]["suspicious_per_million"] / 1_000_000),
    ("hostile", SEVERITY_LEVEL_TARGETS[DEFAULT_SEVERITY_LEVEL - 1]["hostile_per_million"] / 1_000_000),
]

# Legacy FP-per-million equivalent of the default rates.
FPR_RECOMMENDATIONS = [
    (level, rate * 1_000_000)
    for level, rate in DEFAULT_FP_RATE_RECOMMENDATIONS
]

# Recall-floor + aspirational FPR targets.
# Used by `compute_recall_fpr_recommendations` (legacy).
#
# Each entry: (label, min_recall, aspirational_fpr_per_million)
#   - Always guarantees at least min_recall.
#   - If the benign pool is large enough to measure the FPR target,
#     tightens the threshold to meet it (as long as recall stays above floor).
#   - As data grows, thresholds naturally tighten toward the FPR target.
#
# Intuition:
#   suspicious: "unusual, take a look" — catch ≥95% of malware
#   hostile:    "must look NOW"        — catch ≥80%, very few false alarms
RECALL_FPR_RECOMMENDATIONS = [
    ("suspicious", 0.95, 500),   # ≥95% recall, aspirational ≤500 FP/1M
    ("hostile",    0.80, 100),   # ≥80% recall, aspirational ≤100 FP/1M
]

# Minimum expected FP to trust an FPR measurement.
MIN_EXPECTED_FP_FOR_FPR = 5


@dataclass(frozen=True, slots=True)
class PolicyLevel:
    name: str
    mode: str
    target: float
    min_flags: int = 0


@dataclass(frozen=True, slots=True)
class PolicySpec:
    name: str
    description: str
    suspicious: PolicyLevel
    hostile: PolicyLevel


POLICY_SPECS = [
    PolicySpec(
        name="default_fp_rate",
        description="Default deploy policy: suspicious <=1/100k good FP, hostile <=1/1M good FP",
        suspicious=PolicyLevel("suspicious", "max_recall_at_fp_rate", 1 / 100_000),
        hostile=PolicyLevel("hostile", "max_recall_at_fp_rate", 1 / 1_000_000),
    ),
    PolicySpec(
        name="ultra_low_fpr",
        description="Max recall at 10 FP/1M suspicious and 1 FP/1M hostile",
        suspicious=PolicyLevel("suspicious", "max_recall_at_fpr", 10.0),
        hostile=PolicyLevel("hostile", "max_recall_at_fpr", 1.0),
    ),
    PolicySpec(
        name="low_fpr",
        description="Looser low-FPR operating point for broader suspicious coverage",
        suspicious=PolicyLevel("suspicious", "max_recall_at_fpr", 100.0),
        hostile=PolicyLevel("hostile", "max_recall_at_fpr", 10.0),
    ),
    PolicySpec(
        name="recall_floor",
        description="Highest thresholds that still keep malware recall floors",
        suspicious=PolicyLevel("suspicious", "highest_threshold_at_recall", 0.99),
        hostile=PolicyLevel("hostile", "highest_threshold_at_recall", 0.90),
    ),
    PolicySpec(
        name="recall_plus_fpr",
        description="Recall floors with aspirational FPR tightening when measurable",
        suspicious=PolicyLevel("suspicious", "recall_floor_then_fpr", 0.97),
        hostile=PolicyLevel("hostile", "recall_floor_then_fpr", 0.85),
    ),
    PolicySpec(
        name="precision_floor",
        description="Lowest thresholds that satisfy precision floors with enough support",
        suspicious=PolicyLevel("suspicious", "min_precision", 0.99, min_flags=25),
        hostile=PolicyLevel("hostile", "min_precision", 0.999, min_flags=10),
    ),
]


@dataclass(frozen=True, slots=True)
class ScoredSample:
    row_id: int
    sha256: str
    path: str
    score: int
    label: int


def _batched(items, batch_size: int):
    it = iter(items)
    while True:
        batch = list(islice(it, batch_size))
        if not batch:
            return
        yield batch


def _select_threshold_at_fp_budget(
    thresholds: np.ndarray,
    tp_vals: np.ndarray,
    fp_vals: np.ndarray,
    recall_vals: np.ndarray,
    fpr_vals: np.ndarray,
    n_benign: int,
    n_malware: int,
    *,
    max_fp: int,
) -> dict[str, float | int] | None:
    valid = fp_vals <= max_fp
    if not valid.any():
        if max_fp < 0:
            return None
        stats = _empty_threshold_stats(thresholds, n_benign, n_malware)
    else:
        index = int(np.where(valid)[0][-1])
        stats = _stats_dict_at_index(
            thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, n_malware, index,
        )
    stats["max_fp_budget"] = int(max_fp)
    return stats


def _fp_budget_for_rate(n_benign: int, rate: float) -> int:
    """Allowed benign false positives for a target per-good-file FP rate."""
    if n_benign <= 0:
        return 0
    if rate <= 0:
        return 0
    return max(1, int(np.floor(n_benign * rate)))


def _fp_budget_for_per_million(n_benign: int, per_million: float) -> int:
    """Allowed benign false positives for a target FP-per-million rate."""
    return _fp_budget_for_rate(n_benign, per_million / 1_000_000)


def _nearby_budgets(target: int) -> list[int]:
    """Small readable budget window around the selected operating point."""
    values = {0, 1, target}
    for delta in (-5, -2, -1, 1, 2, 5):
        if target + delta >= 0:
            values.add(target + delta)
    if target >= 10:
        values.update({target - 10, target + 10})
    return sorted(values)


def _stats_dict_at_index(
    thresholds: np.ndarray,
    tp_vals: np.ndarray,
    fp_vals: np.ndarray,
    recall_vals: np.ndarray,
    fpr_vals: np.ndarray,
    n_benign: int,
    n_malware: int,
    index: int,
) -> dict[str, float | int]:
    tp = int(tp_vals[index])
    fp = int(fp_vals[index])
    tn = int(n_benign - fp)
    fn = int(n_malware - tp)
    flagged = tp + fp
    precision = float(tp / flagged) if flagged > 0 else 1.0
    tnr = float(tn / max(n_benign, 1))
    return {
        "threshold": float(thresholds[index]),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "flagged": flagged,
        "recall": float(recall_vals[index]),
        "true_positive_rate": float(recall_vals[index]),
        "true_negative_rate": tnr,
        "precision": precision,
        "fpr": float(fpr_vals[index]),
        "fp_per_million": float(fpr_vals[index] * 1_000_000),
        "n_benign": int(n_benign),
        "n_malware": int(n_malware),
    }


def _empty_threshold_stats(
    thresholds: np.ndarray,
    n_benign: int,
    n_malware: int,
) -> dict[str, float | int]:
    threshold = 1.0
    if len(thresholds) > 0:
        threshold = float(np.nextafter(float(thresholds[0]), np.inf))
    return {
        "threshold": threshold,
        "tp": 0,
        "fp": 0,
        "tn": int(n_benign),
        "fn": int(n_malware),
        "flagged": 0,
        "recall": 0.0,
        "true_positive_rate": 0.0,
        "true_negative_rate": 1.0,
        "precision": 1.0,
        "fpr": 0.0,
        "fp_per_million": 0.0,
        "n_benign": int(n_benign),
        "n_malware": int(n_malware),
    }


def _select_policy_level(
    level: PolicyLevel,
    thresholds: np.ndarray,
    tp_vals: np.ndarray,
    fp_vals: np.ndarray,
    recall_vals: np.ndarray,
    fpr_vals: np.ndarray,
    n_benign: int,
    n_malware: int,
) -> tuple[dict[str, float | int] | None, str | None]:
    if len(thresholds) == 0:
        return None, "no predictions"

    flagged = tp_vals + fp_vals
    with np.errstate(divide="ignore", invalid="ignore"):
        precision_vals = np.where(flagged > 0, tp_vals / np.maximum(flagged, 1), 1.0)

    mode = level.mode
    if mode == "max_recall_at_fpr":
        valid = fpr_vals * 1_000_000 <= level.target
        if not valid.any():
            return None, f"no threshold reaches <= {level.target:.0f} FP/1M"
        index = int(np.where(valid)[0][-1])
        if n_benign < max(int(np.ceil(MIN_EXPECTED_FP_FOR_FPR * 1_000_000 / max(level.target, 1e-12))), 1):
            warning = f"underpowered benign pool for {level.target:.0f} FP/1M target"
        else:
            warning = None
        return _stats_dict_at_index(thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, n_malware, index), warning

    if mode == "max_recall_at_fp_rate":
        budget = _fp_budget_for_rate(n_benign, level.target)
        row = _select_threshold_at_fp_budget(
            thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign,
            n_malware,
            max_fp=budget,
        )
        if row is None:
            return None, f"no threshold reaches <= {budget} FP"
        row["target_fp_rate"] = float(level.target)
        return row, None

    if mode == "highest_threshold_at_recall":
        valid = recall_vals >= level.target
        if not valid.any():
            return None, f"no threshold keeps recall >= {level.target:.2%}"
        index = int(np.where(valid)[0][0])
        return _stats_dict_at_index(thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, n_malware, index), None

    if mode == "recall_floor_then_fpr":
        valid_recall = recall_vals >= level.target
        if not valid_recall.any():
            return None, f"no threshold keeps recall >= {level.target:.2%}"
        recall_index = int(np.where(valid_recall)[0][0])
        chosen_index = recall_index
        warning = None
        aspirational_fpm = 100.0 if level.name == "suspicious" else 10.0
        measurable = n_benign * aspirational_fpm / 1_000_000 >= MIN_EXPECTED_FP_FOR_FPR
        if measurable:
            valid_fpr = valid_recall & ((fpr_vals * 1_000_000) <= aspirational_fpm)
            if valid_fpr.any():
                chosen_index = int(np.where(valid_fpr)[0][0])
        else:
            warning = f"underpowered benign pool for aspirational {aspirational_fpm:.0f} FP/1M tightening"
        return _stats_dict_at_index(thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, n_malware, chosen_index), warning

    if mode == "min_precision":
        valid = (precision_vals >= level.target) & (flagged >= level.min_flags)
        if not valid.any():
            return None, f"no threshold reaches precision >= {level.target:.3f} with >= {level.min_flags} flags"
        index = int(np.where(valid)[0][-1])
        return _stats_dict_at_index(thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, n_malware, index), None

    raise ValueError(f"unsupported policy mode: {mode}")


def evaluate_policies(
    probs: np.ndarray,
    y: np.ndarray,
    *,
    n_benign_denominator: int | None = None,
) -> list[dict[str, Any]]:
    thresholds, tp_vals, fp_vals, _correct, recall_vals, fpr_vals, _n, n_malware, n_benign = (
        _threshold_stats(probs, y, n_benign_denominator=n_benign_denominator)
    )
    results: list[dict[str, Any]] = []
    for spec in POLICY_SPECS:
        suspicious, suspicious_warning = _select_policy_level(
            spec.suspicious, thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, n_malware,
        )
        hostile, hostile_warning = _select_policy_level(
            spec.hostile, thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, n_malware,
        )
        results.append({
            "name": spec.name,
            "description": spec.description,
            "suspicious": suspicious,
            "hostile": hostile,
            "warnings": [w for w in [suspicious_warning, hostile_warning] if w],
            "policy": {
                "suspicious": asdict(spec.suspicious),
                "hostile": asdict(spec.hostile),
            },
        })
    return results


def fp_budget_tables(
    probs: np.ndarray,
    y: np.ndarray,
    *,
    n_benign_denominator: int | None = None,
    hostile_budgets: list[int] | None = None,
    suspicious_budgets: list[int] | None = None,
) -> dict[str, list[dict[str, float | int]]]:
    thresholds, tp_vals, fp_vals, _correct, recall_vals, fpr_vals, _n, n_malware, n_benign = (
        _threshold_stats(probs, y, n_benign_denominator=n_benign_denominator)
    )
    default_budgets = {
        level: _fp_budget_for_rate(n_benign, rate)
        for level, rate in DEFAULT_FP_RATE_RECOMMENDATIONS
    }
    hostile_budgets = hostile_budgets or _nearby_budgets(default_budgets["hostile"])
    suspicious_budgets = suspicious_budgets or _nearby_budgets(default_budgets["suspicious"])

    def _rows(budgets: list[int]) -> list[dict[str, float | int]]:
        rows: list[dict[str, float | int]] = []
        for budget in budgets:
            row = _select_threshold_at_fp_budget(
                thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign,
                n_malware,
                max_fp=budget,
            )
            if row is not None:
                rows.append(row)
        return rows

    return {
        "hostile": _rows(hostile_budgets),
        "suspicious": _rows(suspicious_budgets),
    }


def compute_severity_levels(
    probs: np.ndarray,
    y: np.ndarray,
    *,
    n_benign_denominator: int | None = None,
) -> list[dict[str, Any]]:
    """Compute severity-level thresholds from configured FP-per-million targets."""
    thresholds, tp_vals, fp_vals, _correct, recall_vals, fpr_vals, _n, n_malware, n_benign = (
        _threshold_stats(probs, y, n_benign_denominator=n_benign_denominator)
    )
    levels: list[dict[str, Any]] = []
    for target in SEVERITY_LEVEL_TARGETS:
        level = int(target["level"])
        row: dict[str, Any] = {
            "level": level,
            "targets": {
                "hostile_per_million": float(target["hostile_per_million"]),
                "suspicious_per_million": float(target["suspicious_per_million"]),
            },
            "budgets": {},
        }
        for name in ("hostile", "suspicious"):
            per_million = float(target[f"{name}_per_million"])
            budget = _fp_budget_for_per_million(n_benign, per_million)
            selected = _select_threshold_at_fp_budget(
                thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, n_malware,
                max_fp=budget,
            )
            row["budgets"][f"{name}_fp"] = budget
            if selected is not None:
                selected["target_fp_per_million"] = per_million
            row[name] = selected
        levels.append(row)
    return levels


def _severity_level_by_number(levels: list[dict[str, Any]], level_number: int) -> dict[str, Any] | None:
    for row in levels:
        if int(row.get("level", 0)) == level_number:
            return row
    return None


def _most_open_severity_level(levels: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not levels:
        return None
    return max(levels, key=lambda row: int(row.get("level", 0)))


def _matches_severity_level(probability: float, level: dict[str, Any], name: str) -> bool:
    metric = level.get(name)
    return isinstance(metric, dict) and probability >= float(metric["threshold"])


def _near_severity_level(level: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of a severity level with thresholds twice as far from 1.0."""
    near: dict[str, Any] = {
        "level": level.get("level"),
        "basis_level": level.get("level"),
        "targets": level.get("targets", {}),
        "budgets": level.get("budgets", {}),
    }
    for name in ("hostile", "suspicious"):
        metric = level.get(name)
        if isinstance(metric, dict):
            near_metric = dict(metric)
            threshold = float(metric["threshold"])
            near_metric["threshold"] = max(0.0, 1.0 - (2.0 * (1.0 - threshold)))
            near_metric["basis_threshold"] = threshold
            near[name] = near_metric
        else:
            near[name] = None
    return near


def _first_matching_level(probability: float, levels: list[dict[str, Any]], name: str) -> int | None:
    for row in levels:
        metric = row.get(name)
        if isinstance(metric, dict) and probability >= float(metric["threshold"]):
            return int(row["level"])
    return None


def _row_for_sample(sample: ScoredSample, probability: float, label: int, levels: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "row_id": sample.row_id,
        "sha256": sample.sha256,
        "path": _outermost_sample_path(sample.path),
        "score": sample.score,
        "probability": float(probability),
        "label": "bad" if int(label) == 1 else "good",
        "suspicious_level": _first_matching_level(float(probability), levels, "suspicious"),
        "hostile_level": _first_matching_level(float(probability), levels, "hostile"),
    }


def _outermost_sample_path(path: str) -> str:
    """Return the archive path for an embedded member path."""
    return path.split("!!", 1)[0]


def _outermost_error_rows(rows: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    """Collapse embedded archive member rows to one row per outer sample path."""
    seen: set[str] = set()
    selected: list[dict[str, Any]] = []
    for row in rows:
        outer_path = _outermost_sample_path(str(row.get("path") or ""))
        key = outer_path or str(row.get("path") or "")
        if key in seen:
            continue
        seen.add(key)
        row = dict(row)
        row["path"] = outer_path
        selected.append(row)
        if len(selected) >= limit:
            break
    return selected


def _print_severity_table(title: str, levels: list[dict[str, Any]], name: str) -> None:
    print(f"{title:=^100}")
    print(
        f"{'Lvl':>3} {'Target/1M':>9} {'Budget':>7} {'Threshold':>10} "
        f"{'Recall':>8} {'Prec':>8} {'TNR':>8} {'TP':>8} {'FP':>7} {'TN':>8} {'FN':>8}"
    )
    for row in levels:
        metric = row.get(name)
        target = float(row["targets"][f"{name}_per_million"])
        budget = int(row["budgets"][f"{name}_fp"])
        if not metric:
            print(f"{int(row['level']):>3} {target:>9.1f} {budget:>7} {'—':>10} {'—':>8} {'—':>8} {'—':>8} {'—':>8} {'—':>7} {'—':>8} {'—':>8}")
            continue
        print(
            f"{int(row['level']):>3} {target:>9.1f} {budget:>7} {float(metric['threshold']):>10.6f} "
            f"{float(metric['recall']):>8.2%} {float(metric['precision']):>8.2%} "
            f"{float(metric['true_negative_rate']):>8.2%} {int(metric['tp']):>8} "
            f"{int(metric['fp']):>7} {int(metric['tn']):>8} {int(metric['fn']):>8}"
        )
    print()


def _error_rows_for_threshold(
    samples: list[ScoredSample],
    probs: np.ndarray,
    y: np.ndarray,
    threshold: float,
    *,
    top_n: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    fp_rows: list[dict[str, Any]] = []
    fn_rows: list[dict[str, Any]] = []
    for sample, prob, label in zip(samples, probs, y, strict=False):
        row = {
            "row_id": sample.row_id,
            "sha256": sample.sha256,
            "path": _outermost_sample_path(sample.path),
            "score": sample.score,
            "probability": float(prob),
            "label": "bad" if int(label) == 1 else "good",
        }
        if int(label) == 0 and prob >= threshold:
            fp_rows.append(row)
        elif int(label) == 1 and prob < threshold:
            fn_rows.append(row)
    fp_rows.sort(key=lambda row: float(row["probability"]), reverse=True)
    fn_rows.sort(key=lambda row: float(row["probability"]), reverse=True)
    return (
        _outermost_error_rows(fp_rows, limit=top_n),
        _outermost_error_rows(fn_rows, limit=top_n),
    )


def _score_samples(
    spec: features.FeatureSpec,
    model_path: Path,
    *,
    samples: list[ScoredSample],
    report_labels: list[tuple[dict[str, Any], int]],
    batch_size: int = 2048,
    n_workers: int = 0,
) -> np.ndarray:
    model = load_model(model_path)
    pred_batches: list[np.ndarray] = []
    seen = 0
    for X_batch, y_batch in features.extract_stream_batches(
        report_labels,
        spec,
        n_workers=n_workers,
        batch_size=batch_size,
    ):
        X_input = features.standardize(X_batch, spec) if spec.standardized else X_batch
        preds = predict_proba(model, X_input)
        pred_batches.append(preds)
        seen += len(y_batch)
    if seen != len(samples):
        raise ValueError(f"scored sample count mismatch: expected {len(samples)}, got {seen}")
    return np.concatenate(pred_batches) if pred_batches else np.array([], dtype=np.float32)


def _score_labeled_corpus(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    path_substr: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    limit: int = 0,
    n_workers: int = 0,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
    include_samples: bool = True,
) -> tuple[list[ScoredSample], np.ndarray, np.ndarray]:
    """Score the full labeled corpus used for operational threshold tuning."""
    cacheable = (
        cache_path is not None
        and path_substr is None
        and min_score is None
        and max_score is None
        and limit == 0
    )
    if cacheable and not refresh_cache and cache_path.exists():
        newest_input = max(model_path.stat().st_mtime, spec_path.stat().st_mtime)
        if cache_path.stat().st_mtime >= newest_input:
            log.info("loading threshold score cache from %s", cache_path)
            arrays = np.load(cache_path, allow_pickle=False)
            samples = []
            if include_samples:
                samples = [
                    ScoredSample(
                        row_id=int(row_id),
                        sha256=str(sha256),
                        path=str(path),
                        score=int(score),
                        label=int(label),
                    )
                    for row_id, sha256, path, score, label in zip(
                        arrays["row_ids"],
                        arrays["sha256"],
                        arrays["paths"],
                        arrays["scores"],
                        arrays["labels"],
                        strict=True,
                    )
                ]
            return samples, arrays["probs"], arrays["labels"].astype(np.float32)

    if cacheable:
        log.info("building threshold score cache at %s", cache_path)
    spec = features.FeatureSpec.load(spec_path)
    model = load_model(model_path)
    samples = [
        ScoredSample(row_id=row_id, sha256=sha256, path=path, score=score, label=label)
        for row_id, sha256, path, score, label in data.stream_labeled_metadata_full(
            db_path,
            path_substr=path_substr,
            min_score=min_score,
            max_score=max_score,
            limit=limit,
        )
    ]
    if not samples:
        raise ValueError("no samples matched the requested filters")
    log.info("threshold scoring metadata: %d labeled rows", len(samples))
    row_ids_labels = [(sample.row_id, sample.label) for sample in samples]
    pred_batches: list[np.ndarray] = []
    label_batches: list[np.ndarray] = []

    for X_batch, y_batch in features.extract_labeled_from_db_batches(
        db_path,
        row_ids_labels,
        spec,
        n_workers=n_workers,
    ):
        X_input = features.standardize(X_batch, spec) if spec.standardized else X_batch
        pred_batches.append(predict_proba(model, X_input).astype(np.float32))
        label_batches.append(y_batch.astype(np.float32))

    probs = np.concatenate(pred_batches) if pred_batches else np.array([], dtype=np.float32)
    y = np.concatenate(label_batches) if label_batches else np.array([], dtype=np.float32)
    if len(probs) != len(samples):
        raise ValueError(f"scored sample count mismatch: expected {len(samples)}, got {len(probs)}")
    if cacheable:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        # Use uncompressed NPZ: this cache is meant to save wall-clock time,
        # and deflate compression is slow and effectively single-threaded here.
        np.savez(
            cache_path,
            row_ids=np.array([sample.row_id for sample in samples], dtype=np.int64),
            sha256=np.array([sample.sha256 for sample in samples]),
            paths=np.array([sample.path for sample in samples]),
            scores=np.array([sample.score for sample in samples], dtype=np.int32),
            labels=y.astype(np.int8),
            probs=probs.astype(np.float32),
        )
        log.info("saved threshold score cache to %s", cache_path)
    return samples, probs, y


def compute_default_recommendations_for_corpus(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    n_workers: int = 0,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
) -> dict[str, float | None]:
    """Compute deploy thresholds by scoring the full labeled hopper corpus."""
    _samples, probs, y = _score_labeled_corpus(
        db_path,
        model_path=model_path,
        spec_path=spec_path,
        n_workers=n_workers,
        cache_path=cache_path,
        refresh_cache=refresh_cache,
        include_samples=False,
    )
    return compute_default_recommendations(probs, y)


def tune_thresholds(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    path_substr: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    top_errors: int = 20,
    output_path: Path | None = None,
    limit: int = 0,
    n_workers: int = 0,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
) -> dict[str, Any]:
    """Score the full labeled corpus and report threshold policy candidates."""
    samples, probs, y = _score_labeled_corpus(
        db_path,
        model_path=model_path,
        spec_path=spec_path,
        path_substr=path_substr,
        min_score=min_score,
        max_score=max_score,
        limit=limit,
        n_workers=n_workers,
        cache_path=cache_path,
        refresh_cache=refresh_cache,
        include_samples=top_errors > 0,
    )
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    policies = evaluate_policies(probs, y)
    budgets = fp_budget_tables(probs, y)
    severity_levels = compute_severity_levels(probs, y)
    for policy in policies:
        errors: dict[str, Any] = {}
        if top_errors > 0:
            for level_name in ("suspicious", "hostile"):
                level = policy.get(level_name)
                if not level or level.get("threshold") is None:
                    continue
                fp_rows, fn_rows = _error_rows_for_threshold(
                    samples, probs, y, float(level["threshold"]), top_n=top_errors,
                )
                errors[level_name] = {
                    "false_positives": fp_rows,
                    "false_negatives": fn_rows,
                    "false_positive_count": int(np.sum((y == 0) & (probs >= float(level["threshold"])))),
                    "false_negative_count": int(np.sum((y == 1) & (probs < float(level["threshold"])))),
                }
        policy["errors"] = errors

    payload: dict[str, Any] = {
        "filters": {
            "path_substr": path_substr,
            "min_score": min_score,
            "max_score": max_score,
            "limit": limit,
        },
        "corpus": {
            "samples": len(y),
            "malware": malware,
            "benign": benign,
        },
        "default_fp_rate_targets": {
            level: {
                "target_rate": rate,
                "max_fp_budget": _fp_budget_for_rate(benign, rate),
            }
            for level, rate in DEFAULT_FP_RATE_RECOMMENDATIONS
        },
        "severity_level_targets": SEVERITY_LEVEL_TARGETS,
        "severity_levels": severity_levels,
        "fp_budget_tables": budgets,
        "policies": policies,
    }

    print(f"\n{'TUNE THRESHOLDS':=^78}")
    print(f"Corpus: {len(y)} samples ({malware} malware, {benign} benign)")
    if path_substr:
        print(f"Filter: path contains {path_substr!r}")
    if min_score is not None or max_score is not None:
        print(f"Filter: score range [{min_score if min_score is not None else '-inf'}, {max_score if max_score is not None else 'inf'}]")
    print(f"Top errors per level: {top_errors}")
    print()
    _print_severity_table("HOSTILE SEVERITY LEVELS", severity_levels, "hostile")
    _print_severity_table("SUSPICIOUS SEVERITY LEVELS", severity_levels, "suspicious")

    print(f"{'Policy':<18} {'Level':<12} {'Threshold':>10} {'TP Rate':>8} {'Prec':>8} {'FP/1M':>10} {'TP':>7} {'FP':>7}")
    print(f"{'-'*78}")
    for policy in policies:
        for level_name in ("suspicious", "hostile"):
            level = policy.get(level_name)
            if not level:
                print(f"{policy['name']:<18} {level_name:<12} {'—':>10} {'—':>8} {'—':>8} {'—':>10} {'—':>7} {'—':>7}")
                continue
            print(
                f"{policy['name']:<18} {level_name:<12} {float(level['threshold']):>10.6f} "
                f"{float(level['recall']):>8.2%} {float(level['precision']):>8.2%} "
                f"{float(level['fp_per_million']):>10.1f} {int(level['tp']):>7} {int(level['fp']):>7}"
            )
        for warning in policy["warnings"]:
            print(f"  warning: {warning}")
        print()

    target_budgets = {
        level: _fp_budget_for_rate(benign, rate)
        for level, rate in DEFAULT_FP_RATE_RECOMMENDATIONS
    }
    print(f"{'HOSTILE BY GOOD FP BUDGET':=^78}")
    print(f"Target: <=1 FP per 1,000,000 good files; current budget = {target_budgets['hostile']} FP")
    print(f"{'Allowed FP':>10} {'Good %':>10} {'Threshold':>10} {'TP Rate':>8} {'Prec':>8} {'TP':>7} {'FP':>7} {'FN':>7}")
    for row in budgets["hostile"]:
        fn = malware - int(row["tp"])
        marker = " *" if int(row["max_fp_budget"]) == target_budgets["hostile"] else ""
        print(
            f"{int(row['max_fp_budget']):>10} {100.0 * int(row['fp']) / max(benign, 1):>9.4f}% "
            f"{float(row['threshold']):>10.6f} {float(row['recall']):>8.2%} {float(row['precision']):>8.2%} "
            f"{int(row['tp']):>7} {int(row['fp']):>7} {fn:>7}{marker}"
        )
    print()

    print(f"{'SUSPICIOUS BY GOOD FP BUDGET':=^78}")
    print(f"Target: <=1 FP per 100,000 good files; current budget = {target_budgets['suspicious']} FP")
    print(f"{'Allowed FP':>10} {'Good %':>10} {'Threshold':>10} {'TP Rate':>8} {'Prec':>8} {'TP':>7} {'FP':>7} {'FN':>7}")
    for row in budgets["suspicious"]:
        fn = malware - int(row["tp"])
        marker = " *" if int(row["max_fp_budget"]) == target_budgets["suspicious"] else ""
        print(
            f"{int(row['max_fp_budget']):>10} {100.0 * int(row['fp']) / max(benign, 1):>9.4f}% "
            f"{float(row['threshold']):>10.6f} {float(row['recall']):>8.2%} {float(row['precision']):>8.2%} "
            f"{int(row['tp']):>7} {int(row['fp']):>7} {fn:>7}{marker}"
        )
    print()

    for policy in policies:
        print(f"{policy['name']}: {policy['description']}")
        for level_name in ("suspicious", "hostile"):
            level_errors = policy["errors"].get(level_name)
            if not level_errors:
                continue
            print(
                f"  {level_name} false positives: {level_errors['false_positive_count']}  "
                f"false negatives: {level_errors['false_negative_count']}"
            )
            if level_errors["false_positives"]:
                print("  top false positives:")
                for row in level_errors["false_positives"]:
                    print(f"    {row['probability']:.6f}  {row['sha256'][:16]}  {row['path']}")
            if level_errors["false_negatives"]:
                print("  top false negatives:")
                for row in level_errors["false_negatives"]:
                    print(f"    {row['probability']:.6f}  {row['sha256'][:16]}  {row['path']}")
        print()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            import json
            json.dump(payload, f, indent=2)
        print(f"Saved tuning report to {output_path}")

    return payload


def show_false_positives(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    top_errors: int = 100,
    output_path: Path | None = None,
    n_workers: int = 0,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
) -> dict[str, Any]:
    """Print false positives grouped by first severity level reached."""
    samples, probs, y = _score_labeled_corpus(
        db_path,
        model_path=model_path,
        spec_path=spec_path,
        n_workers=n_workers,
        cache_path=cache_path,
        refresh_cache=refresh_cache,
    )
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    severity_levels = compute_severity_levels(probs, y)
    basis_level = _most_open_severity_level(severity_levels)
    raw_rows = [
        _row_for_sample(sample, float(prob), int(label), severity_levels)
        for sample, prob, label in zip(samples, probs, y, strict=False)
        if int(label) == 0 and basis_level is not None and (
            _matches_severity_level(float(prob), basis_level, "suspicious")
            or _matches_severity_level(float(prob), basis_level, "hostile")
        )
    ]
    rows = list(raw_rows)
    rows.sort(key=lambda row: float(row["probability"]), reverse=True)
    rows = _outermost_error_rows(rows, limit=len(rows))

    payload: dict[str, Any] = {
        "corpus": {
            "samples": len(samples),
            "malware": malware,
            "benign": benign,
        },
        "severity_level_targets": SEVERITY_LEVEL_TARGETS,
        "severity_levels": severity_levels,
        "basis_level": int(basis_level["level"]) if basis_level is not None else None,
        "raw_false_positive_count": len(raw_rows),
        "outer_false_positive_count": len(rows),
        "false_positives": rows[:top_errors],
        "counts": {"suspicious": {}, "hostile": {}},
    }

    for name in ("suspicious", "hostile"):
        for level in range(1, 10):
            payload["counts"][name][str(level)] = sum(
                1 for row in rows if row[f"{name}_level"] == level
            )

    print(f"\n{'FALSE POSITIVES BY SEVERITY LEVEL':=^78}")
    print(f"Corpus: {len(samples)} samples ({malware} malware, {benign} good)")
    if basis_level is not None:
        print(
            f"Basis: level {basis_level['level']} "
            f"(raw rows: {len(raw_rows)}, outer files: {len(rows)})"
        )
    print("First level counts:")
    for name in ("hostile", "suspicious"):
        counts = ", ".join(f"L{level}={payload['counts'][name][str(level)]}" for level in range(1, 10))
        print(f"  {name}: {counts}")
    if rows:
        print("\n  top false positives:")
        for row in rows[:top_errors]:
            print(
                f"    {row['probability']:.6f}  H={row['hostile_level'] or '-'} "
                f"S={row['suspicious_level'] or '-'} score={row['score']:<4} "
                f"{row['sha256'][:16]}  {row['path']}"
            )
    else:
        print("\n  false positives: none")

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            import json
            json.dump(payload, f, indent=2)
        print(f"\nSaved false-positive report to {output_path}")

    return payload


def show_near_false_positives(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    top_errors: int = 100,
    output_path: Path | None = None,
    n_workers: int = 0,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
) -> dict[str, Any]:
    """Print benign samples that newly match a twice-looser level-9 threshold."""
    samples, probs, y = _score_labeled_corpus(
        db_path,
        model_path=model_path,
        spec_path=spec_path,
        n_workers=n_workers,
        cache_path=cache_path,
        refresh_cache=refresh_cache,
    )
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    severity_levels = compute_severity_levels(probs, y)
    basis_level = _most_open_severity_level(severity_levels)
    near_level = _near_severity_level(basis_level) if basis_level is not None else None
    raw_rows = [
        _row_for_sample(sample, float(prob), int(label), severity_levels)
        for sample, prob, label in zip(samples, probs, y, strict=False)
        if int(label) == 0
        and basis_level is not None
        and near_level is not None
        and not (
            _matches_severity_level(float(prob), basis_level, "suspicious")
            or _matches_severity_level(float(prob), basis_level, "hostile")
        )
        and (
            _matches_severity_level(float(prob), near_level, "suspicious")
            or _matches_severity_level(float(prob), near_level, "hostile")
        )
    ]
    rows = list(raw_rows)
    rows.sort(key=lambda row: float(row["probability"]), reverse=True)
    rows = _outermost_error_rows(rows, limit=len(rows))

    payload: dict[str, Any] = {
        "corpus": {
            "samples": len(samples),
            "malware": malware,
            "benign": benign,
        },
        "severity_level_targets": SEVERITY_LEVEL_TARGETS,
        "severity_levels": severity_levels,
        "basis_level": int(basis_level["level"]) if basis_level is not None else None,
        "near_level": near_level,
        "raw_near_false_positive_count": len(raw_rows),
        "outer_near_false_positive_count": len(rows),
        "near_false_positives": rows[:top_errors],
        "counts": {"suspicious": {}, "hostile": {}},
    }

    for name in ("suspicious", "hostile"):
        for level in range(1, 10):
            payload["counts"][name][str(level)] = sum(
                1 for row in rows if row[f"{name}_level"] == level
            )

    print(f"\n{'NEAR FALSE POSITIVES BY SEVERITY LEVEL':=^78}")
    print(f"Corpus: {len(samples)} samples ({malware} malware, {benign} good)")
    if basis_level is not None and near_level is not None:
        print(
            f"Basis: level {basis_level['level']} with twice-looser thresholds "
            f"(raw rows: {len(raw_rows)}, outer files: {len(rows)})"
        )
        for name in ("hostile", "suspicious"):
            metric = near_level.get(name)
            if isinstance(metric, dict):
                print(
                    f"  {name}: {float(metric['basis_threshold']):.6f} -> "
                    f"{float(metric['threshold']):.6f}"
                )
    print("Existing first level counts for near rows:")
    for name in ("hostile", "suspicious"):
        counts = ", ".join(
            f"L{level}={payload['counts'][name][str(level)]}" for level in range(1, 10)
        )
        print(f"  {name}: {counts}")
    if rows:
        print("\n  top near false positives:")
        for row in rows[:top_errors]:
            print(
                f"    {row['probability']:.6f}  H={row['hostile_level'] or '-'} "
                f"S={row['suspicious_level'] or '-'} score={row['score']:<4} "
                f"{row['sha256'][:16]}  {row['path']}"
            )
    else:
        print("\n  near false positives: none")

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            import json
            json.dump(payload, f, indent=2)
        print(f"\nSaved near-false-positive report to {output_path}")

    return payload


def show_false_negatives(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    top_errors: int = 100,
    output_path: Path | None = None,
    n_workers: int = 0,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
) -> dict[str, Any]:
    """Print bad samples by first severity level reached, including uncaught rows."""
    samples, probs, y = _score_labeled_corpus(
        db_path,
        model_path=model_path,
        spec_path=spec_path,
        n_workers=n_workers,
        cache_path=cache_path,
        refresh_cache=refresh_cache,
    )
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    severity_levels = compute_severity_levels(probs, y)
    rows = [
        _row_for_sample(sample, float(prob), int(label), severity_levels)
        for sample, prob, label in zip(samples, probs, y, strict=False)
        if int(label) == 1
    ]
    rows.sort(key=lambda row: float(row["probability"]), reverse=True)
    rows = _outermost_error_rows(rows, limit=len(rows))
    uncaught = [
        row for row in rows
        if row["suspicious_level"] is None and row["hostile_level"] is None
    ]

    payload: dict[str, Any] = {
        "corpus": {
            "samples": len(samples),
            "malware": malware,
            "benign": benign,
        },
        "severity_level_targets": SEVERITY_LEVEL_TARGETS,
        "severity_levels": severity_levels,
        "uncaught": uncaught[:top_errors],
        "counts": {"suspicious": {}, "hostile": {}, "uncaught": len(uncaught)},
    }

    for name in ("suspicious", "hostile"):
        for level in range(1, 10):
            payload["counts"][name][str(level)] = sum(1 for row in rows if row[f"{name}_level"] == level)

    print(f"\n{'FALSE NEGATIVES BY SEVERITY LEVEL':=^78}")
    print(f"Corpus: {len(samples)} samples ({malware} malware, {benign} good)")
    print("First caught level counts:")
    for name in ("hostile", "suspicious"):
        counts = ", ".join(f"L{level}={payload['counts'][name][str(level)]}" for level in range(1, 10))
        print(f"  {name}: {counts}")
    print(f"  uncaught by level 9: {len(uncaught)}")
    if uncaught:
        print("\n  highest-probability uncaught bad samples:")
        for row in uncaught[:top_errors]:
            print(
                f"    {row['probability']:.6f}  H=- S=- score={row['score']:<4} "
                f"{row['sha256'][:16]}  {row['path']}"
            )
    else:
        print("\n  false negatives at level 9: none")

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            import json
            json.dump(payload, f, indent=2)
        print(f"\nSaved false-negative report to {output_path}")

    return payload


def show_near_false_negatives(
    db_path: Path | str,
    *,
    model_path: Path,
    spec_path: Path,
    top_errors: int = 100,
    output_path: Path | None = None,
    n_workers: int = 0,
    cache_path: Path | None = None,
    refresh_cache: bool = False,
) -> dict[str, Any]:
    """Print malware samples caught by a twice-looser level-9 threshold only."""
    samples, probs, y = _score_labeled_corpus(
        db_path,
        model_path=model_path,
        spec_path=spec_path,
        n_workers=n_workers,
        cache_path=cache_path,
        refresh_cache=refresh_cache,
    )
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    severity_levels = compute_severity_levels(probs, y)
    basis_level = _most_open_severity_level(severity_levels)
    near_level = _near_severity_level(basis_level) if basis_level is not None else None
    raw_rows = [
        _row_for_sample(sample, float(prob), int(label), severity_levels)
        for sample, prob, label in zip(samples, probs, y, strict=False)
        if int(label) == 1
        and basis_level is not None
        and near_level is not None
        and not (
            _matches_severity_level(float(prob), basis_level, "suspicious")
            or _matches_severity_level(float(prob), basis_level, "hostile")
        )
        and (
            _matches_severity_level(float(prob), near_level, "suspicious")
            or _matches_severity_level(float(prob), near_level, "hostile")
        )
    ]
    rows = list(raw_rows)
    rows.sort(key=lambda row: float(row["probability"]), reverse=True)
    rows = _outermost_error_rows(rows, limit=len(rows))

    payload: dict[str, Any] = {
        "corpus": {
            "samples": len(samples),
            "malware": malware,
            "benign": benign,
        },
        "severity_level_targets": SEVERITY_LEVEL_TARGETS,
        "severity_levels": severity_levels,
        "basis_level": int(basis_level["level"]) if basis_level is not None else None,
        "near_level": near_level,
        "raw_near_false_negative_count": len(raw_rows),
        "outer_near_false_negative_count": len(rows),
        "near_false_negatives": rows[:top_errors],
    }

    print(f"\n{'NEAR FALSE NEGATIVES BY SEVERITY LEVEL':=^78}")
    print(f"Corpus: {len(samples)} samples ({malware} malware, {benign} good)")
    if basis_level is not None and near_level is not None:
        print(
            f"Basis: level {basis_level['level']} with twice-looser thresholds "
            f"(raw rows: {len(raw_rows)}, outer files: {len(rows)})"
        )
        for name in ("hostile", "suspicious"):
            metric = near_level.get(name)
            if isinstance(metric, dict):
                print(
                    f"  {name}: {float(metric['basis_threshold']):.6f} -> "
                    f"{float(metric['threshold']):.6f}"
                )
    if rows:
        print("\n  top near false negatives:")
        for row in rows[:top_errors]:
            print(
                f"    {row['probability']:.6f}  H={row['hostile_level'] or '-'} "
                f"S={row['suspicious_level'] or '-'} score={row['score']:<4} "
                f"{row['sha256'][:16]}  {row['path']}"
            )
    else:
        print("\n  near false negatives: none")

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            import json
            json.dump(payload, f, indent=2)
        print(f"\nSaved near-false-negative report to {output_path}")

    return payload


def show_thresholds(
    db_path: Path | str,
    model_path: Path | None = None,
    spec_path: Path | None = None,
    n_workers: int = 0,
) -> None:
    """Train a model on non-test samples, then show the confidence
    thresholds needed for each accuracy target on the test set.

    If model_path and spec_path are provided and exist, skip training
    entirely and only extract features for the test-bucket samples.
    """
    # Partition samples into train/test.
    train_row_ids, train_ids_labels, test_ids_labels = data.partition_row_ids(db_path)

    if (
        model_path is not None
        and spec_path is not None
        and model_path.exists()
        and spec_path.exists()
    ):
        log.info("reusing model from %s and spec from %s", model_path, spec_path)
        from .model import load_model

        spec = features.FeatureSpec.load(spec_path)
        model = load_model(model_path)

        _, _, X_test, y_test = features.extract_partitioned_from_db(
            db_path, [], test_ids_labels, spec, n_workers=n_workers,
        )
        if X_test.shape[0] == 0:
            print("No test samples — cannot compute thresholds.")
            return
        probs = predict_proba(model, X_test)
        print_threshold_table(probs, y_test)
        return

    spec = features.build_vocab_from_db(db_path, train_ids_labels, n_workers=n_workers)

    X_train, y_train, X_test, y_test = features.extract_partitioned_from_db(
        db_path, train_ids_labels, test_ids_labels, spec, n_workers=n_workers,
    )
    if X_train.shape[0] == 0:
        print("No training samples found.")
        return
    result = train.train(X_train, y_train, feature_names=spec.feature_names)
    if X_test.shape[0] == 0:
        print("No test samples — cannot compute thresholds.")
        return

    probs = predict_proba(result.model, X_test)
    print_threshold_table(probs, y_test)


def _threshold_stats(
    probs: np.ndarray,
    y: np.ndarray,
    *,
    n_benign_denominator: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, int, int, int]:
    """Pre-compute per-threshold stats via a single sorted pass.

    Reduces all threshold searches from O(n_targets × n_unique × n_samples)
    to O(n log n) by computing cumulative TP/FP once and grouping ties.

    Returns arrays in descending threshold order:
      thresholds, tp, fp, correct, recall, fpr, n, n_malware, n_benign
    """
    n = len(probs)
    n_malware = int((y == 1).sum())
    observed_benign = int((y == 0).sum())
    n_benign = observed_benign
    if n_benign_denominator is not None:
        n_benign = max(observed_benign, int(n_benign_denominator))

    if n == 0:
        empty = np.array([], dtype=np.float64)
        return empty, empty, empty, empty, empty, empty, 0, 0, n_benign

    # Sort samples high-to-low by predicted probability.
    order = np.argsort(probs)[::-1]
    sorted_probs = probs[order]
    sorted_y = y[order]

    # Cumulative TP and FP as we include more samples (high prob first).
    cum_tp = np.concatenate([[0], np.cumsum(sorted_y == 1)])  # (n+1,)
    cum_fp = np.concatenate([[0], np.cumsum(sorted_y == 0)])  # (n+1,)

    # Group boundaries: we can only set a threshold between groups of identical
    # scores — all samples with the same probability must be treated together.
    change_mask = np.concatenate([np.diff(sorted_probs) != 0, [True]])  # (n,)
    cuts = np.where(change_mask)[0] + 1  # 1-indexed cutpoints; last is always n

    thresholds = sorted_probs[cuts - 1]        # prob of last sample in each group
    tp_vals = cum_tp[cuts].astype(np.int64)
    fp_vals = cum_fp[cuts].astype(np.int64)
    correct_vals = tp_vals + (n_benign - fp_vals)
    recall_vals = tp_vals / max(n_malware, 1)
    fpr_vals = fp_vals / max(n_benign, 1)

    return thresholds, tp_vals, fp_vals, correct_vals, recall_vals, fpr_vals, n, n_malware, n_benign


def compute_recommendations(
    probs: np.ndarray,
    y: np.ndarray,
) -> dict[str, float | None]:
    """Compute recommended thresholds for each level in RECOMMENDATIONS.

    Legacy FPR-based mode: for each level, picks the lowest threshold
    (highest recall) that meets the FPR ceiling. Returns a dict mapping
    level name → threshold (or None if no threshold meets the FPR target).
    """
    thresholds, _tp, _fp, _correct, _recall_vals, fpr_vals, _n, _nm, _nb = (
        _threshold_stats(probs, y)
    )
    result: dict[str, float | None] = {}
    for level, max_fpr in RECOMMENDATIONS:
        valid = fpr_vals <= max_fpr
        if valid.any():
            # Thresholds are in descending order; last valid = lowest threshold = highest recall.
            k = int(np.where(valid)[0][-1])
            result[level] = float(thresholds[k])
        else:
            result[level] = None
    return result


def compute_precision_recommendations(
    probs: np.ndarray,
    y: np.ndarray,
) -> dict[str, float | None]:
    """Compute recommended thresholds for each level in PRECISION_RECOMMENDATIONS.

    For each level (suspicious/hostile), picks the lowest threshold
    (highest recall) where the test-set precision is at least the target
    AND at least MIN_FLAGGED_FOR_PRECISION samples are flagged at that
    threshold. Intuition: "if I flag X at this threshold, I'm right ≥99%
    of the time".

    Returns a dict mapping level name → threshold (or None if no threshold
    meets the precision target with enough flagged samples).
    """
    thresholds, tp_vals, fp_vals, _correct, _recall_vals, _fpr_vals, _n, _nm, _nb = (
        _threshold_stats(probs, y)
    )
    flagged = tp_vals + fp_vals
    # Precision = TP / (TP + FP); when no flags, treat as 1.0 (vacuous).
    with np.errstate(divide="ignore", invalid="ignore"):
        precision = np.where(flagged > 0, tp_vals / np.maximum(flagged, 1), 1.0)

    result: dict[str, float | None] = {}
    for level, min_precision in PRECISION_RECOMMENDATIONS:
        valid = (precision >= min_precision) & (flagged >= MIN_FLAGGED_FOR_PRECISION)
        if valid.any():
            # Thresholds descending → last valid = lowest threshold = highest recall.
            k = int(np.where(valid)[0][-1])
            result[level] = float(thresholds[k])
        else:
            result[level] = None
    return result


def compute_recall_fpr_recommendations(
    probs: np.ndarray,
    y: np.ndarray,
) -> dict[str, float | None]:
    """Compute recommended thresholds using recall floors + aspirational FPR.

    For each level:
    1. Find the highest threshold achieving ≥min_recall (guarantees recall).
    2. If we have enough benign data, try to tighten to meet the FPR target
       — but never drop recall below the floor.
    3. Return the tighter of the two (higher threshold = fewer FP).

    This auto-scales: with more benign data the FPR target becomes
    measurable and thresholds tighten. With little data, recall floor
    governs.
    """
    thresholds, tp_vals, fp_vals, _correct, recall_vals, fpr_vals, _n, n_malware, n_benign = (
        _threshold_stats(probs, y)
    )
    fpm = fpr_vals * 1_000_000

    result: dict[str, float | None] = {}
    for level, min_recall, target_fpm in RECALL_FPR_RECOMMENDATIONS:
        # Step 1: recall-floor threshold (always available).
        recall_valid = recall_vals >= min_recall
        if not recall_valid.any():
            log.warning("%s: cannot achieve %.0f%% recall", level, min_recall * 100)
            result[level] = None
            continue
        # Last valid index = lowest threshold meeting recall floor.
        recall_idx = int(np.where(recall_valid)[0][-1])
        recall_threshold = float(thresholds[recall_idx])

        # Step 2: FPR-target threshold (if measurable).
        expected_fp = n_benign * target_fpm / 1_000_000
        fpr_threshold = None
        if expected_fp >= MIN_EXPECTED_FP_FOR_FPR:
            fpr_valid = (fpm <= target_fpm) & (recall_vals >= min_recall)
            if fpr_valid.any():
                fpr_idx = int(np.where(fpr_valid)[0][-1])
                fpr_threshold = float(thresholds[fpr_idx])

        # Pick the tighter threshold (higher = fewer FP).
        if fpr_threshold is not None and fpr_threshold > recall_threshold:
            chosen = fpr_threshold
            source = "FPR"
        else:
            chosen = recall_threshold
            source = "recall"

        result[level] = chosen

        # Log the choice.
        idx = int(np.searchsorted(-thresholds, -chosen))
        idx = min(idx, len(thresholds) - 1)
        log.info(
            "%s: threshold=%.4f (from %s floor) recall=%.2f%% FPR=%d/1M (%d FP)",
            level, chosen, source,
            float(recall_vals[idx] * 100),
            int(fpm[idx]),
            int(fp_vals[idx]),
        )

    return result


def compute_default_recommendations(
    probs: np.ndarray,
    y: np.ndarray,
    *,
    n_benign_denominator: int | None = None,
) -> dict[str, float | None]:
    """Compute legacy deploy thresholds from severity level 5."""
    levels = compute_severity_levels(probs, y, n_benign_denominator=n_benign_denominator)
    default_level = _severity_level_by_number(levels, DEFAULT_SEVERITY_LEVEL)
    result: dict[str, float | None] = {"suspicious": None, "hostile": None}
    if default_level is None:
        return result
    for name in ("suspicious", "hostile"):
        row = default_level.get(name)
        if not row:
            continue
        result[name] = float(row["threshold"])
        log.info(
            "%s level %d: threshold=%.4f TP-rate=%.2f%% FP=%d/%d good files (target %.1f/1M)",
            name,
            DEFAULT_SEVERITY_LEVEL,
            float(row["threshold"]),
            float(row["recall"]) * 100,
            int(row["fp"]),
            int(row["n_benign"]),
            float(row["target_fp_per_million"]),
        )
    return result


def compute_fpr_recommendations(
    probs: np.ndarray,
    y: np.ndarray,
) -> dict[str, float | None]:
    """Compute recommended thresholds based on FPR ceilings.

    For each level (suspicious/hostile), picks the lowest threshold
    (highest recall) where FP-per-million-benign stays at or below
    the target. This directly controls the false alarm rate.

    The FPR targets in FPR_RECOMMENDATIONS scale naturally: as the
    benign pool grows, finer FPR granularity becomes measurable and
    the thresholds tighten automatically.
    """
    thresholds, tp_vals, fp_vals, _correct, _recall_vals, fpr_vals, _n, _nm, n_benign = (
        _threshold_stats(probs, y)
    )
    # Convert FPR to FP-per-million for comparison with targets.
    fpm = fpr_vals * 1_000_000

    result: dict[str, float | None] = {}
    for level, max_fpm in FPR_RECOMMENDATIONS:
        # Check if we have enough benign samples to measure this FPR.
        min_benign = int(MIN_EXPECTED_FP_FOR_FPR / (max_fpm / 1_000_000))
        if n_benign < min_benign:
            log.warning(
                "%s: need ≥%d benign to measure ≤%d FP/1M (have %d)",
                level, min_benign, max_fpm, n_benign,
            )
            result[level] = None
            continue

        valid = fpm <= max_fpm
        if valid.any():
            # Thresholds descending → last valid = lowest threshold = highest recall.
            k = int(np.where(valid)[0][-1])
            result[level] = float(thresholds[k])
            log.info(
                "%s: threshold=%.4f recall=%.2f%% FPR=%.4f%% (%d FP/1M)",
                level, thresholds[k],
                float(tp_vals[k] / max(tp_vals[k] + (_n - tp_vals[k] - fp_vals[k] - (n_benign - fp_vals[k])), 1) * 100),
                float(fpr_vals[k] * 100), int(fpm[k]),
            )
        else:
            result[level] = None
    return result


def print_recommendations(
    probs: np.ndarray,
    y: np.ndarray,
    title: str = "RECOMMENDED",
    *,
    highlight_threshold: float | None = None,
    n_benign_denominator: int | None = None,
) -> None:
    """Print the recommended threshold table for a set of predictions.

    highlight_threshold: if provided, inserts this threshold (e.g. the
    calibrated holdout threshold) into the fixed-thresholds table marked
    with a ← so it's easy to find the operating point from training.
    """
    thresholds, tp_vals, fp_vals, _correct_vals, recall_vals, fpr_vals, n, n_malware, n_benign = (
        _threshold_stats(probs, y, n_benign_denominator=n_benign_denominator)
    )
    observed_benign = int((y == 0).sum())
    observed_severity_levels = compute_severity_levels(probs, y)
    corpus_severity_levels = (
        compute_severity_levels(probs, y, n_benign_denominator=n_benign_denominator)
        if n_benign != observed_benign
        else observed_severity_levels
    )

    print(f"\n{title:=^70}")
    print(f"  {n} scored samples ({n_malware} malware, {observed_benign} benign)")
    if n_benign != observed_benign:
        ignored_benign = n_benign - observed_benign
        print(
            f"  FP/1M denominator: {n_benign} benign files "
            f"(includes {ignored_benign} low-score ignored rows)"
        )
    print("  Severity thresholds: lowest threshold meeting each good-file FP-per-million target")
    print()
    if n_benign != observed_benign:
        print("  Measured on scored rows only:")
        _print_severity_table("HOSTILE SEVERITY LEVELS", observed_severity_levels, "hostile")
        _print_severity_table("SUSPICIOUS SEVERITY LEVELS", observed_severity_levels, "suspicious")
        print("  Measured with full good-file denominator:")
    _print_severity_table("HOSTILE SEVERITY LEVELS", corpus_severity_levels, "hostile")
    _print_severity_table("SUSPICIOUS SEVERITY LEVELS", corpus_severity_levels, "suspicious")

    # Fixed reference thresholds — include the calibrated holdout threshold if provided.
    fixed_set: set[float] = {0.1, 0.25, 0.5, 0.6, 0.7, 0.8, 0.9, 0.98, 0.99, 0.995}
    if highlight_threshold is not None:
        fixed_set.add(highlight_threshold)
    fixed = sorted(fixed_set)
    print(f"\n  {'— fixed thresholds —':-^62}")
    print(f"  {'Threshold':>22} {'Recall':>8} {'FPR':>8} {'FP/1M':>8} {'TP':>8} {'FP':>8}")
    for t in fixed:
        tp = int(((probs >= t) & (y == 1)).sum())
        fp = int(((probs >= t) & (y == 0)).sum())
        tpr = tp / max(n_malware, 1)
        fpr = fp / max(n_benign, 1)
        fp_per_million = fpr * 1_000_000
        marker = " ←" if t is highlight_threshold or t == highlight_threshold else ""
        print(f"  {t:>22.3f} {tpr:>8.2%} {fpr:>8.4%} {fp_per_million:>8.0f} {tp:>8} {fp:>8}{marker}")

    # Recall-target table: highest threshold achieving each recall level.
    recall_targets = [0.99, 0.995, 0.999, 0.9999, 0.99999]
    print(f"\n  {'— by recall target —':-^62}")
    print(f"  {'Recall target':>22} {'Threshold':>10} {'Actual':>8} {'FPR':>8} {'FP/1M':>8} {'TP':>8} {'FP':>8}")
    for target in recall_targets:
        valid = recall_vals >= target
        if valid.any():
            k = int(np.where(valid)[0][0])
            label = f"≥{target*100:.3f}%"
            fp_per_million = fpr_vals[k] * 1_000_000
            print(
                f"  {label:>22} {thresholds[k]:>10.6f} {recall_vals[k]:>8.2%} "
                f"{fpr_vals[k]:>8.4%} {fp_per_million:>8.0f} {tp_vals[k]:>8} {fp_vals[k]:>8}"
            )
        else:
            label = f"≥{target*100:.3f}%"
            print(f"  {label:>22} {'—':>10} (not achievable)")

    print()


def print_threshold_table(probs: np.ndarray, y: np.ndarray) -> None:
    """Print the hostile/benign threshold table for a set of predictions."""
    n_benign = int(np.sum(y == 0))
    n_malware = int(np.sum(y == 1))
    n_total = len(y)

    print(f"\nTest set: {len(y)} samples ({n_malware} malware, {n_benign} benign)")

    thresholds, _tp_vals, fp_vals, correct_vals, _recall_vals, _fpr_vals, n, _, _ = (
        _threshold_stats(probs, y)
    )

    # --- Hostile thresholds ---
    # Lowest threshold (most permissive malware call) still meeting overall accuracy.
    # In descending thresholds: last valid entry = lowest threshold.
    print(f"\n{'HOSTILE':=^60}")
    print("  Lowest threshold to call malware while meeting overall accuracy")
    print(f"  {'Accuracy':<12} {'Threshold':>10} {'Correct':>10} {'Wrong':>8} {'Total':>8}")
    print(f"  {'-'*50}")
    for target in ACCURACY_TARGETS:
        valid = correct_vals / max(n_total, 1) >= target
        if valid.any():
            k = int(np.where(valid)[0][-1])
            pct = f"{target * 100:.3f}%"
            print(
                f"  {pct:<12} {thresholds[k]:>10.6f} {correct_vals[k]:>10} "
                f"{n_total - correct_vals[k]:>8} {n_total:>8}"
            )
        else:
            pct = f"{target * 100:.3f}%"
            print(f"  {pct:<12} {'—':>10} (not achievable on test set)")

    # --- Benign thresholds ---
    # Highest threshold (most permissive benign call) still meeting overall accuracy.
    # In descending thresholds: first valid entry = highest threshold.
    print(f"\n{'BENIGN':=^60}")
    print("  Highest threshold to call benign while meeting overall accuracy")
    print(f"  {'Accuracy':<12} {'Threshold':>10} {'Correct':>10} {'Wrong':>8} {'Total':>8}")
    print(f"  {'-'*50}")
    for target in ACCURACY_TARGETS:
        valid = correct_vals / max(n_total, 1) >= target
        if valid.any():
            k = int(np.where(valid)[0][0])
            pct = f"{target * 100:.3f}%"
            print(
                f"  {pct:<12} {thresholds[k]:>10.6f} {correct_vals[k]:>10} "
                f"{n_total - correct_vals[k]:>8} {n_total:>8}"
            )
        else:
            pct = f"{target * 100:.3f}%"
            print(f"  {pct:<12} {'—':>10} (not achievable on test set)")

    print()
    print_recommendations(probs, y, title="RECOMMENDED (test set, held-out)")
