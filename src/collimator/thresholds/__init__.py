"""Show confidence thresholds required for various accuracy levels."""

from __future__ import annotations

import logging
import os
import time
from dataclasses import asdict, dataclass
from itertools import islice
from pathlib import Path
from typing import Any

import numpy as np

from collimator import data, features, train
from collimator.model import load_model, predict_proba

log = logging.getLogger(__name__)

# Deployment operating points on the per-100M-benigns scale. The integer
# `level` IS the false-positive budget per 100 million benigns — so L100
# means 100 FP / 100M ≡ 1 FP/M. The internal computation still carries
# `hostile_per_million` as a float because the rest of the threshold math
# is keyed on FP/M; the per-100M level number is the canonical wire unit
# (matches litmus's `-l` knob and the JSON emit field `target_per_100M`).
#
# Grid is dense in the strict region (L0-L10, where finer resolution
# actually pays off once the benign corpus is large enough to resolve
# sub-FP/M budgets) and decade-aligned in the loose region (L10-L100, to
# match litmus's `-0..-9` shorthand 0/10/20/.../90). L0-L10 will collapse
# to recall@0 on small corpora; that's honest, the volume floor catches it
# (see `min_observable_fp_per_million`). Levels >L100 are intentionally
# absent: litmus's CLI caps at 100, so anything above is unreachable.
#
# "Suspicious" is a consumer-side concept (litmus derives a suspicious
# band from the hostile threshold); collimator only computes and ships
# the single hostile threshold per level.
_LEVELS_PER_100M: tuple[int, ...] = (
    0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100,
)
SEVERITY_LEVEL_TARGETS = [
    {
        "level": level,
        "target_per_100M": level,
        "hostile_per_million": level / 100.0,
    }
    for level in _LEVELS_PER_100M
]

# 50 FP/100M = 0.5 FP/M — the stricter default replacing the legacy L300
# (= 3 FP/M) operating point. Litmus's CLI default (`-l 50`) matches; if
# a future train shows recall doesn't hold here, ratchet looser.
DEFAULT_SEVERITY_LEVEL = 50


def _severity_target(level: int) -> dict[str, int | float]:
    for target in SEVERITY_LEVEL_TARGETS:
        if int(target["level"]) == level:
            return target
    raise ValueError(f"unknown severity level: {level}")


DEFAULT_SEVERITY_TARGET = _severity_target(DEFAULT_SEVERITY_LEVEL)

# (label, FP-rate) pair used by ``fp_budget_tables`` and downstream callers
# to derive the default budget at the configured severity level. Only one
# severity now — "suspicious" is a consumer-side derivation, not a thing
# collimator tunes for.
DEFAULT_FP_RATE_RECOMMENDATIONS = [
    ("hostile", DEFAULT_SEVERITY_TARGET["hostile_per_million"] / 1_000_000),
]

# Minimum expected FP count needed before we trust an FPR-based threshold —
# small benign pools produce noisy FPR estimates that pick thresholds the
# data can't actually support.
_MIN_EXPECTED_FP_FOR_FPR = 5


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
    hostile: PolicyLevel


POLICY_SPECS = [
    PolicySpec(
        name="default_fp_rate",
        description=(
            "Default deploy policy: "
            f"<={DEFAULT_SEVERITY_TARGET['hostile_per_million']:.0f}/1M good FP"
        ),
        hostile=PolicyLevel(
            "hostile",
            "max_recall_at_fp_rate",
            DEFAULT_SEVERITY_TARGET["hostile_per_million"] / 1_000_000,
        ),
    ),
    PolicySpec(
        name="ultra_low_fpr",
        description="Max recall at 1 FP/1M",
        hostile=PolicyLevel("hostile", "max_recall_at_fpr", 1.0),
    ),
    PolicySpec(
        name="low_fpr",
        description="Looser low-FPR operating point",
        hostile=PolicyLevel("hostile", "max_recall_at_fpr", 10.0),
    ),
    PolicySpec(
        name="recall_floor",
        description="Highest threshold that still keeps the malware recall floor",
        hostile=PolicyLevel("hostile", "highest_threshold_at_recall", 0.90),
    ),
    PolicySpec(
        name="recall_plus_fpr",
        description="Recall floor with aspirational FPR tightening when measurable",
        hostile=PolicyLevel("hostile", "recall_floor_then_fpr", 0.85),
    ),
    PolicySpec(
        name="precision_floor",
        description="Lowest threshold that satisfies the precision floor with enough support",
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
    canonical_sha256: str = ""  # for partition_of() lookup at consumption time


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


# Beta-Binomial smoothing for FP-rate estimates on small benign pools.
# Default prior is uniform: alpha=beta=1 — i.e. Beta(1+k, 1+N-k) on a count of
# k FPs in N trials.  At small N, the posterior MAP nudges the empirical
# estimate toward 0.5 (regularization strength matters less for our use case;
# the upper-credible-bound is what changes deploy behavior).  Heavier priors
# (alpha+beta > 2) would pull harder; we keep the prior uninformative so the
# correction kicks in only when N truly hurts.
_DEFAULT_BETA_PRIOR_ALPHA = 1.0
_DEFAULT_BETA_PRIOR_BETA = 1.0


def credible_bound_fp_rate(
    n_fp: int,
    n_benign: int,
    *,
    alpha_prior: float = _DEFAULT_BETA_PRIOR_ALPHA,
    beta_prior: float = _DEFAULT_BETA_PRIOR_BETA,
    side: str = "upper",
    confidence: float = 0.95,
) -> float:
    """Beta-Binomial credible bound on the FP rate.

    Given ``n_fp`` empirical false positives observed over ``n_benign`` benign
    files, returns the upper or lower bound of a one-sided credible interval
    on the true FP rate.  At large N the bound converges to the empirical
    estimate; at small N (where the empirical is noisy) the upper bound is
    materially higher than the empirical, which is exactly what we want when
    deploying conservatively against a 0.5 FP/M target (= L50) with sparse
    data.

    The math: posterior is Beta(alpha_prior + n_fp, beta_prior + n_benign - n_fp).
    Upper bound is the (confidence)-quantile; lower bound is (1-confidence).

    Examples:

      credible_bound_fp_rate(0, 100, side="upper", confidence=0.95)
      # ≈ 0.029  — empirical 0.0, but with only 100 benigns we can't claim
      # the FPR is below ~3% with 95% confidence.

      credible_bound_fp_rate(0, 1_000_000, side="upper", confidence=0.95)
      # ≈ 3.0e-6 — at 1M benigns, the upper bound is finally tight enough
      # to deploy at L50 (0.5 FP/M).

    No SciPy: we use ``np.random.default_rng().beta`` only as a fallback
    test path; the analytic Beta inverse-CDF is in ``scipy.stats`` but
    importing it pulls in the world.  Compute the bound by Newton on the
    regularized incomplete beta function via ``np`` (fallback) or via a
    short numerical recipe.  In practice ``scipy.stats.beta.ppf`` is the
    one-line option and we already import scipy elsewhere in the repo.
    """
    if n_benign < 0 or n_fp < 0 or n_fp > n_benign:
        raise ValueError(f"invalid inputs: n_fp={n_fp}, n_benign={n_benign}")
    if n_benign == 0:
        # No data at all — the prior alone is the posterior; return the
        # prior's upper/lower bound.  Conservative caller should treat this
        # as "no information; do not deploy."
        from scipy.stats import beta as _beta  # noqa: PLC0415
        q = confidence if side == "upper" else 1.0 - confidence
        return float(_beta.ppf(q, alpha_prior, beta_prior))
    from scipy.stats import beta as _beta  # noqa: PLC0415
    a = alpha_prior + n_fp
    b = beta_prior + (n_benign - n_fp)
    q = confidence if side == "upper" else 1.0 - confidence
    return float(_beta.ppf(q, a, b))


def select_threshold_at_credible_bound(
    thresholds: np.ndarray,
    tp_vals: np.ndarray,
    fp_vals: np.ndarray,
    recall_vals: np.ndarray,
    fpr_vals: np.ndarray,
    n_benign: int,
    n_malware: int,
    *,
    max_fp_per_million: float,
    confidence: float = 0.95,
    alpha_prior: float = _DEFAULT_BETA_PRIOR_ALPHA,
    beta_prior: float = _DEFAULT_BETA_PRIOR_BETA,
) -> dict[str, float | int] | None:
    """Pick the threshold whose *upper credible bound* on FP rate is at or
    below the target — strictly more conservative than the empirical
    threshold-at-FP-budget when N is small, identical when N is large.

    This is the deploy-time complement to ``_select_threshold_at_fp_budget``:
    use this when you'd rather deploy a tighter threshold than risk that the
    empirical FP rate underestimates the true rate due to sparse benigns.

    Returns the same stats dict shape as the empirical helper, plus
    ``credible_bound_fp_rate`` and ``credible_bound_confidence`` fields so
    callers can audit how much smoothing happened.
    """
    if n_benign <= 0 or len(thresholds) == 0:
        return None
    target_rate = max_fp_per_million / 1_000_000.0
    # Compute upper credible bound of FP rate at every threshold's empirical
    # FP count.  The bound is monotone in n_fp for fixed n_benign (more FPs
    # → higher bound), so the strictest threshold whose bound clears the
    # target is just the largest fp_val that still satisfies the bound.
    valid = np.zeros(len(fp_vals), dtype=bool)
    bounds = np.zeros(len(fp_vals), dtype=np.float64)
    for i, fp in enumerate(fp_vals):
        bound = credible_bound_fp_rate(
            int(fp), n_benign,
            alpha_prior=alpha_prior, beta_prior=beta_prior,
            side="upper", confidence=confidence,
        )
        bounds[i] = bound
        valid[i] = bound <= target_rate
    if not valid.any():
        # Even fp=0 doesn't bound below target — the corpus is too small for
        # this target rate.  Caller should treat as "do not deploy at this L."
        stats = _empty_threshold_stats(thresholds, n_benign, n_malware)
        stats["max_fp_budget"] = 0
        stats["credible_bound_fp_rate"] = float(bounds[0]) if bounds.size else 0.0
        stats["credible_bound_confidence"] = float(confidence)
        return stats
    index = int(np.where(valid)[0][-1])
    stats = _stats_dict_at_index(
        thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, n_malware, index,
    )
    stats["credible_bound_fp_rate"] = float(bounds[index])
    stats["credible_bound_confidence"] = float(confidence)
    stats["max_fp_budget"] = int(fp_vals[index])
    return stats


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
        "fp_per_100M": float(fpr_vals[index] * 100_000_000),
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
        "fp_per_100M": 0.0,
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
        if n_benign < max(int(np.ceil(_MIN_EXPECTED_FP_FOR_FPR * 1_000_000 / max(level.target, 1e-12))), 1):
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
        # Hostile is the only tier collimator tunes for now; the previous
        # 100 FP/M aspirational target only applied to the (removed) suspicious
        # tier, so a single fixed value is enough.
        aspirational_fpm = 10.0
        measurable = n_benign * aspirational_fpm / 1_000_000 >= _MIN_EXPECTED_FP_FOR_FPR
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
        hostile, hostile_warning = _select_policy_level(
            spec.hostile, thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, n_malware,
        )
        results.append({
            "name": spec.name,
            "description": spec.description,
            "hostile": hostile,
            "warnings": [w for w in [hostile_warning] if w],
            "policy": {
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
) -> dict[str, list[dict[str, float | int]]]:
    thresholds, tp_vals, fp_vals, _correct, recall_vals, fpr_vals, _n, n_malware, n_benign = (
        _threshold_stats(probs, y, n_benign_denominator=n_benign_denominator)
    )
    default_budgets = {
        level: _fp_budget_for_rate(n_benign, rate)
        for level, rate in DEFAULT_FP_RATE_RECOMMENDATIONS
    }
    hostile_budgets = hostile_budgets or _nearby_budgets(default_budgets["hostile"])

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
        per_million = float(target["hostile_per_million"])
        budget = _fp_budget_for_per_million(n_benign, per_million)
        selected = _select_threshold_at_fp_budget(
            thresholds, tp_vals, fp_vals, recall_vals, fpr_vals, n_benign, n_malware,
            max_fp=budget,
        )
        if selected is not None:
            # `per_million` is the per-million target rate; per-100M = ×100.
            selected["target_fp_per_100M"] = per_million * 100.0
            selected["target_per_100M"] = level
        levels.append({
            "level": level,
            "targets": {
                "target_per_100M": level,
                "hostile_per_million": per_million,
            },
            "budgets": {"hostile_fp": budget},
            "hostile": selected,
        })
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
    metric = level.get("hostile")
    if isinstance(metric, dict):
        near_metric = dict(metric)
        threshold = float(metric["threshold"])
        near_metric["threshold"] = max(0.0, 1.0 - (2.0 * (1.0 - threshold)))
        near_metric["basis_threshold"] = threshold
        near["hostile"] = near_metric
    else:
        near["hostile"] = None
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


def compute_default_recommendations(
    probs: np.ndarray,
    y: np.ndarray,
    *,
    n_benign_denominator: int | None = None,
) -> dict[str, float | None]:
    """Compute legacy deploy thresholds from the default severity level."""
    levels = compute_severity_levels(probs, y, n_benign_denominator=n_benign_denominator)
    default_level = _severity_level_by_number(levels, DEFAULT_SEVERITY_LEVEL)
    result: dict[str, float | None] = {"hostile": None}
    if default_level is None:
        return result
    row = default_level.get("hostile")
    if row:
        result["hostile"] = float(row["threshold"])
        log.info(
            "hostile level %d: threshold=%.4f TP-rate=%.2f%% FP=%d/%d good files (target %.1f/1M)",
            DEFAULT_SEVERITY_LEVEL,
            float(row["threshold"]),
            float(row["recall"]) * 100,
            int(row["fp"]),
            int(row["n_benign"]),
            float(row["target_fp_per_100M"]),
        )
    return result






# Re-export the DB-driven inspection surface from the sibling module so
# `collimator.thresholds.tune_thresholds(...)` etc. keep working for the
# Make-target callers — the package layout is internal, not API.
from ._inspect import (  # noqa: E402
    _error_rows_for_threshold,
    _score_labeled_corpus,
    _score_samples,
    compute_default_recommendations_for_corpus,
    show_false_negatives,
    show_false_positives,
    show_near_false_negatives,
    show_near_false_positives,
    tune_thresholds,
)
