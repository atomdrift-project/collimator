"""Out-of-time backtesting for route operating points.

Why this exists
---------------
Every number collimator publishes about an operating point is measured on the
same benign pool the threshold was fitted on. That answers "how many benigns in
my corpus fire?" It does not answer the question deploy actually cares about:
"how many benigns fire NEXT WEEK, on files the calibration pool had never
seen?"

For ``filetypes/pe`` the two answers differ by roughly three orders of
magnitude. The shipped policy realizes 0 FP on its 265,576-benign calibration
pool; the same bundle run against benign PE ingested afterwards realizes
~1,148 FP per million. Nothing in the pipeline measures that gap, so nothing
regresses when it widens.

This module makes the gap measurable and cheap to measure. It reads the
per-row route scores the policy search already writes (``score_table.npz``),
joins the ingest metadata hopper already records (``samples.created_at``,
``feed``, ``parent``), and evaluates an operating point under a strict
separation: the population a threshold is FITTED on and the population it is
MEASURED on are disjoint by construction, and can be disjoint *in time*.

An experiment here is a fit population, an eval population, a level, and an
estimator. No retraining, no feature extraction — a run is a sort and a
searchsorted over arrays that are already on disk, so the loop is seconds.
Model-side iteration lives in ``scripts/pe_iterate.py``; this is the layer
above it.

See ``scripts/azoth_backtest.py`` for the named experiments and LEVELS.md for
what a level means.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from collimator import data as collimator_data
from collimator.thresholds import _fp_anchor_curve, quantile_severity_threshold

LOG = logging.getLogger("collimator.backtest")

# Cache schema for the joined score+metadata slice. Bump on layout changes.
SLICE_CACHE_VERSION = 1

# Key used for the single threshold of a non-joint_or policy.
COMBINED = "__combined__"


@dataclass(frozen=True)
class RouteSlice:
    """Per-row scores plus the ingest metadata needed to split by cohort.

    One row per labeled sample of a single ``file_type``. ``scores`` holds one
    array per route that scored the slice (``general``, ``filegroups/native``,
    ``filetypes/pe``), aligned with every other field by position.
    """

    file_type: str
    row_ids: np.ndarray       # int64, samples.id
    labels: np.ndarray        # int8, 1 = malware, 0 = benign
    scores: dict[str, np.ndarray]   # route name -> float64 probability
    ingested_at: np.ndarray   # int64 epoch seconds; 0 when unknown
    feed: np.ndarray          # unicode
    carved: np.ndarray        # bool: extracted from a parent, label inherited
    cleave_score: np.ndarray  # int32, samples.score
    partition: np.ndarray     # unicode: 'train' | 'dev' | 'test'

    def __len__(self) -> int:
        return int(self.row_ids.size)

    @property
    def malware(self) -> np.ndarray:
        return self.labels == 1

    @property
    def benign(self) -> np.ndarray:
        return self.labels == 0


# --- decision policies -------------------------------------------------------
#
# The shipped policy for a routed filetype is `joint_or`: each route carries
# its OWN threshold and a row fires if any route clears its own. That is not
# the same decision as thresholding a single combined score, and the gap is
# not small — on pe at L25 a single max-threshold catches 4.8% where joint-OR
# catches 26%, because a row the specialist is confident about does not have
# to out-score the general model's tail to fire.
#
# So joint_or is the default here. `max` is kept because
# per_filetype_metrics.json reports a `calibrated_max` ensemble and comparing
# against it is sometimes what you want, but it is not what deploy does.
#
# `validate_against_policy_file` checks this module's L0 joint-OR thresholds
# against the ones azoth_route_policy_search.py actually shipped, so the two
# implementations cannot drift silently.

def combine(
    slice_: RouteSlice, routes: list[str] | None = None, *, strategy: str = "max",
) -> np.ndarray:
    """Single per-row probability from the slice's route scores."""
    names = routes if routes is not None else sorted(slice_.scores)
    missing = [n for n in names if n not in slice_.scores]
    if missing:
        raise KeyError(f"slice has no scores for {missing}; has {sorted(slice_.scores)}")
    stack = np.vstack([slice_.scores[n] for n in names])
    if strategy == "max":
        return np.nanmax(stack, axis=0)
    if strategy == "mean":
        return np.nanmean(stack, axis=0)
    if strategy == "specialist":
        if len(names) != 1:
            raise ValueError("strategy='specialist' takes exactly one route")
        return stack[0]
    raise ValueError(f"unknown combine strategy: {strategy!r}")


@dataclass(frozen=True)
class Policy:
    """A fitted decision rule: one threshold per route, OR-ed together."""

    kind: str                          # 'joint_or' | 'max' | 'specialist'
    routes: tuple[str, ...]
    thresholds: dict[str, float]
    method: dict[str, str]

    def describe(self) -> str:
        return " ".join(f"{k.split('/')[-1]}={v:.6f}" for k, v in sorted(self.thresholds.items()))

    @property
    def extrapolated(self) -> bool:
        """True if any route's threshold is a model claim rather than measured."""
        return any(m == "extrapolated" for m in self.method.values())


def fit_policy(
    slice_: RouteSlice,
    fit_benign: np.ndarray,
    *,
    level: int,
    routes: list[str] | None = None,
    estimator: str = "shared",
    kind: str = "joint_or",
) -> Policy:
    """Derive per-route thresholds from one benign population.

    ``joint_or`` fits each route independently at the level, exactly as the
    shipped ``joint_or_at_fp_*`` policies do. ``max`` fits a single threshold
    to the per-row max. Both use the same estimator, so a comparison between
    them isolates the decision rule.
    """
    names = routes if routes is not None else sorted(slice_.scores)
    fit = fit_benign & slice_.benign
    est = ESTIMATORS[estimator]
    if kind == "joint_or":
        thresholds, methods = {}, {}
        for name in names:
            # A route leaves NaN for rows it did not score (57 of pe's 1.9M for
            # filegroups/native). Sorting those into the benign tail produces a
            # NaN threshold, which then fires on nothing and silently drops the
            # route out of the OR. Drop them from the fit; `NaN >= thr` is
            # already False at apply time, so an unscored row never fires.
            col = slice_.scores[name][fit]
            col = col[~np.isnan(col)]
            thr, method = est(col, level / 100.0)
            if thr is None or not np.isfinite(thr):
                LOG.warning("route %s produced no usable threshold at L%d "
                            "(%d benigns after NaN drop)", name, level, col.size)
                continue
            thresholds[name], methods[name] = float(thr), method
        return Policy("joint_or", tuple(names), thresholds, methods)
    probs = combine(slice_, names, strategy=kind)
    fit_probs = probs[fit]
    fit_probs = fit_probs[~np.isnan(fit_probs)]
    thr, method = est(fit_probs, level / 100.0)
    usable = thr is not None and np.isfinite(thr)
    return Policy(kind, tuple(names),
                  {COMBINED: float(thr)} if usable else {}, {COMBINED: method})


def apply_policy(slice_: RouteSlice, policy: Policy) -> np.ndarray:
    """Boolean 'this row fires', one entry per row of the slice."""
    fired = np.zeros(len(slice_), dtype=bool)
    if not policy.thresholds:
        return fired
    if policy.kind == "joint_or":
        for name, thr in policy.thresholds.items():
            fired |= slice_.scores[name] >= thr
        return fired
    probs = combine(slice_, list(policy.routes), strategy=policy.kind)
    return probs >= policy.thresholds[COMBINED]


# --- operating-point estimators ----------------------------------------------

Estimator = Callable[[np.ndarray, float], "tuple[float | None, str]"]


def estimator_shared(
    benign_probs: np.ndarray, target_per_million: float,
) -> tuple[float | None, str]:
    """The incumbent: ``thresholds.quantile_severity_threshold``.

    Resolution-adjusted (LEVELS.md): the requested level is shifted so L1 lands
    on the route's first observed false positive. On a route with few benigns
    this makes L25 mean "about one FP on the pool", NOT 0.25 FP/M.
    """
    return quantile_severity_threshold(benign_probs, target_per_million)


def estimator_true_rate(
    benign_probs: np.ndarray, target_per_million: float,
) -> tuple[float | None, str]:
    """Same anchor curve, no resolution shift — the level means its literal rate.

    ``estimator_shared`` maps the requested level through
    ``true_rate = requested + floor_level - 1``, so a route whose pool cannot
    resolve the requested rate silently gets a looser one. This estimator drops
    that shift: L25 is 25 FP/100M on every route, and when the pool cannot
    resolve it the threshold is extrapolated down the log-linear line whose
    slope is measured over the deepest decade of anchors (1..10 FP) — the same
    line ``quantile_severity_threshold`` already uses for L0.

    That is a model claim, not a measurement, and it is the claim
    ``backtest_extrapolation`` exists to falsify. It returns method
    ``"extrapolated"`` whenever the pool cannot resolve the requested rate, so
    callers can refuse to ship an unvalidated one.
    """
    if len(benign_probs) < 50:
        return None, "none"
    arr = np.sort(np.asarray(benign_probs, dtype=np.float64))
    if target_per_million >= 1_000_000.0:
        return float(arr[0]), "measured"
    clipped = np.clip(arr, 1e-7, 1 - 1e-7)
    logit = np.log(clipped) - np.log1p(-clipped)
    levels, thresholds, slope = _fp_anchor_curve(logit)
    floor_level = float(levels[0])
    level = max(target_per_million * 100.0, 1e-9)
    if level >= floor_level:
        value = float(np.interp(np.log10(level), np.log10(levels), thresholds))
        return float(min(1.0 / (1.0 + np.exp(-value)), float(arr[-1]))), "measured"
    value = float(thresholds[0] + slope * (np.log10(floor_level) - np.log10(level)))
    return float(1.0 / (1.0 + np.exp(-value))), "extrapolated"


ESTIMATORS: dict[str, Estimator] = {
    "shared": estimator_shared,
    "true_rate": estimator_true_rate,
}


# --- measurement -------------------------------------------------------------

def measure(probs: np.ndarray, labels: np.ndarray, threshold: float) -> dict[str, Any]:
    """Confusion and rates for one threshold. ``>=`` matches deploy."""
    fired = probs >= threshold
    mal, ben = labels == 1, labels == 0
    n_mal, n_ben = int(mal.sum()), int(ben.sum())
    tp, fp = int((fired & mal).sum()), int((fired & ben).sum())
    return {
        "threshold": float(threshold),
        "n_malware": n_mal,
        "n_benign": n_ben,
        "tp": tp,
        "fp": fp,
        "recall": tp / n_mal if n_mal else float("nan"),
        "fp_per_million": fp * 1e6 / n_ben if n_ben else float("nan"),
        "fp_per_100M": fp * 1e8 / n_ben if n_ben else float("nan"),
    }


def measure_policy(slice_: RouteSlice, policy: Policy, eval_mask: np.ndarray) -> dict[str, Any]:
    """Confusion and rates for a fitted policy over an evaluation population."""
    fired = apply_policy(slice_, policy)[eval_mask]
    labels = slice_.labels[eval_mask]
    mal, ben = labels == 1, labels == 0
    n_mal, n_ben = int(mal.sum()), int(ben.sum())
    tp, fp = int((fired & mal).sum()), int((fired & ben).sum())
    return {
        "thresholds": dict(policy.thresholds),
        "method": "extrapolated" if policy.extrapolated else "measured",
        "n_malware": n_mal,
        "n_benign": n_ben,
        "tp": tp,
        "fp": fp,
        "recall": tp / n_mal if n_mal else float("nan"),
        "fp_per_million": fp * 1e6 / n_ben if n_ben else float("nan"),
        "fp_per_100M": fp * 1e8 / n_ben if n_ben else float("nan"),
    }


def backtest(
    slice_: RouteSlice,
    *,
    fit_benign: np.ndarray,
    eval_mask: np.ndarray,
    level: int,
    routes: list[str] | None = None,
    estimator: str = "shared",
    kind: str = "joint_or",
    allow_overlap: bool = False,
) -> dict[str, Any]:
    """Fit an operating point on one benign population, measure it on another.

    ``fit_benign`` selects the benign rows the thresholds are derived from.
    ``eval_mask`` selects the rows they are measured on — malware and benign
    both. The two must be disjoint: overlapping them reproduces the in-sample
    number the pipeline already reports, which is the thing this module exists
    to stop doing by accident. ``allow_overlap`` is for deliberately computing
    that in-sample number as a baseline, and is never the default.
    """
    if not allow_overlap and np.any(fit_benign & eval_mask):
        overlap = int((fit_benign & eval_mask).sum())
        raise ValueError(
            f"fit and eval populations overlap on {overlap} rows — an "
            "operating point measured on its own fitting sample is in-sample; "
            "pass allow_overlap=True if that is deliberately what you want"
        )
    if not (fit_benign & slice_.benign).any():
        raise ValueError("fit_benign selects no benign rows")
    policy = fit_policy(slice_, fit_benign, level=level, routes=routes,
                        estimator=estimator, kind=kind)
    n_fit = int((fit_benign & slice_.benign).sum())
    if not policy.thresholds:
        return {"level": level, "estimator": estimator, "kind": kind,
                "n_fit_benign": n_fit, "thresholds": {}, "method": "none"}
    out = measure_policy(slice_, policy, eval_mask)
    out.update(level=level, estimator=estimator, kind=kind, n_fit_benign=n_fit,
               target_per_million=level / 100.0)
    return out


def benign_tail(
    slice_: RouteSlice,
    route: str,
    *,
    top: int = 200,
) -> list[dict[str, Any]]:
    """The benign files that set the operating point, worst first.

    A zero-FP policy's threshold is the largest benign score, so recall at the
    deploy operating point is decided by a handful of individual files. This
    ranks them and reports, for each, the recall the route would gain if every
    benign at or above it were removed — i.e. the cost of that file being in
    the pool. It is the triage worklist: the rows at the top are where a
    mislabel is worth the most.
    """
    probs = slice_.scores[route]
    ben = slice_.benign & ~np.isnan(probs)
    mal_probs = probs[slice_.malware & ~np.isnan(probs)]
    idx = np.flatnonzero(ben)
    order = idx[np.argsort(-probs[idx])][:top]
    base = float(np.mean(mal_probs >= np.nextafter(probs[order[0]], np.inf)))
    rows = []
    for rank, i in enumerate(order):
        # Threshold if every benign strictly above this one were removed.
        nxt = order[rank + 1] if rank + 1 < len(order) else i
        thr = float(np.nextafter(probs[nxt], np.inf))
        rows.append({
            "rank": rank,
            "row_id": int(slice_.row_ids[i]),
            "score": float(probs[i]),
            "feed": str(slice_.feed[i]),
            "carved": bool(slice_.carved[i]),
            "cleave_score": int(slice_.cleave_score[i]),
            "partition": str(slice_.partition[i]),
            "recall_if_removed_above": float(np.mean(mal_probs >= thr)),
            "recall_gain_pp": float((np.mean(mal_probs >= thr) - base) * 100),
        })
    return rows


def compare_policies(
    slice_: RouteSlice,
    policy_a: Policy,
    policy_b: Policy,
    eval_mask: np.ndarray,
    *,
    n_resamples: int = 2000,
    seed: int = 42,
) -> dict[str, Any]:
    """Paired bootstrap of recall(A) - recall(B) over the same evaluation rows.

    METHODOLOGY.md requires a paired test on every comparison claim. An
    out-of-time eval window is small by construction — the 30-day non-archival
    PE window holds ~2k malware — so a few hundred extra detections can look
    like a result and not be one. Reuses ``stats.paired_bootstrap_diff``; the
    "scores" here are the policies' own fire/no-fire decisions, so the metric
    is evaluated at the operating point rather than over a swept threshold.
    """
    from collimator.stats import paired_bootstrap_diff  # noqa: PLC0415

    fired_a = apply_policy(slice_, policy_a)[eval_mask].astype(np.float64)
    fired_b = apply_policy(slice_, policy_b)[eval_mask].astype(np.float64)
    y_true = (slice_.labels[eval_mask] == 1).astype(np.int8)

    def _recall(yt: np.ndarray, fired: np.ndarray) -> float:
        mal = yt == 1
        return float(fired[mal].mean()) if mal.any() else float("nan")

    out = paired_bootstrap_diff(y_true, fired_a, fired_b, _recall,
                                n_resamples=n_resamples, seed=seed)
    out["significant"] = bool(
        np.isfinite(out["low"]) and np.isfinite(out["high"])
        and (out["low"] > 0 or out["high"] < 0)
    )
    return out


def validate_against_policy_file(
    slice_: RouteSlice,
    policy_json: Path | str,
    *,
    route: str,
    level: int = 1,
    rel_tol: float = 5e-4,
) -> dict[str, Any]:
    """Check this module's thresholds against the ones the pipeline shipped.

    The shipped ``joint_or_at_fp_0`` policy (L1 and up, until the FP budget
    opens) is, by construction, each route's threshold at its first false
    positive on the full benign pool — which is what ``fit_policy`` derives
    here. L0 is deliberately NOT the comparison point: it ships
    ``calibrate_inherited``, a different policy fitted on the wider filegroup
    and general benign populations. If the two disagree, one of the two
    implementations has drifted and every result from this harness is suspect.
    Run it before trusting a number.
    """
    import json  # noqa: PLC0415

    shipped = json.loads(Path(policy_json).read_text())["routes"][route]
    entry = next(e for e in shipped["levels"] if e["level"] == level)
    want = entry["hostile"]["best"].get("thresholds", {})
    policy = fit_policy(slice_, slice_.benign, level=level,
                        routes=sorted(want) or None, kind="joint_or")
    got = policy.thresholds
    rows = []
    for name in sorted(set(want) | set(got)):
        a, b = want.get(name), got.get(name)
        ok = a is not None and b is not None and abs(a - b) <= rel_tol * max(abs(a), 1e-9)
        rows.append({"route": name, "shipped": a, "harness": b, "match": bool(ok)})
    return {"route": route, "level": level, "all_match": all(r["match"] for r in rows),
            "rows": rows}


def plan_extrapolation_grid(
    n_benign: int,
    *,
    decades: tuple[float, ...] = (0.3, 0.6, 0.9, 1.2, 1.5),
    min_expected_fp: float = 10.0,
) -> list[tuple[float, int]]:
    """Largest (rate, fit size) pairs that can test each extrapolation distance.

    Two constraints bound every honest test, in opposite directions:

    * the HELD-OUT remainder must be able to measure the realized rate, so
      ``rate >= min_expected_fp * 1e6 / n_held``;
    * the FIT sample must NOT be able to measure it, so
      ``n_fit < 1e6 / rate`` — otherwise nothing is extrapolated.

    Between them sits one usable rate per distance, and taking the *largest*
    admissible fit sample matters: extrapolating 1.2 decades from 500 benigns
    is a far weaker test than from 20,000, and using the small one would
    understate the estimator and overstate the case against it.
    """
    rate = min_expected_fp * 1e6 / max(int(n_benign * 0.92), 1)
    grid = []
    for d in decades:
        n_fit = int(1e6 / (rate * (10 ** d)))
        if 50 <= n_fit < n_benign * 0.08:
            grid.append((rate, n_fit))
    return grid


def extrapolation_error(
    benign_probs: np.ndarray,
    *,
    rates_per_million: tuple[float, ...] | None = None,
    fit_sizes: tuple[int, ...] | None = None,
    trials: int = 30,
    seed: int = 42,
    estimator: str = "true_rate",
    min_expected_fp: float = 10.0,
) -> list[dict[str, Any]]:
    """Measure how wrong an extrapolated threshold is, as a function of distance.

    The question "can we extrapolate L25 for pe" cannot be answered by asking
    for L25 and checking: 0.25 FP/M over 265,576 benigns expects 0.066 false
    positives, so *any* threshold scores 0 and the check is vacuous.

    What IS measurable is the estimator's bias per decade of extrapolation.
    Fit on a subsample small enough that the requested rate lies below ITS
    1-FP floor — so the estimator must extrapolate — and measure the realized
    rate on the held-out remainder, at rates the remainder can resolve
    (``min_expected_fp`` expected FPs or more). ``decades`` is how far the
    estimator had to reach; ``ratio`` is realized / requested, where 1.0 is a
    perfectly calibrated extrapolation and > 1 means the threshold is looser
    than it claims.

    Read the result as a curve: fit the bias against ``decades``, then look up
    the distance your real level needs (for pe at L25 that is
    ``log10(1e6 / n_benign / 0.25)`` ≈ 1.2 decades).
    """
    rng = np.random.default_rng(seed)
    arr = np.asarray(benign_probs, dtype=np.float64)
    arr = arr[~np.isnan(arr)]
    n = arr.size
    if rates_per_million is None and fit_sizes is None:
        pairs = plan_extrapolation_grid(n, min_expected_fp=min_expected_fp)
    else:
        pairs = [(r, f) for r in (rates_per_million or ()) for f in (fit_sizes or ())]
    rows: list[dict[str, Any]] = []
    for rate, n_fit in pairs:
        if n_fit >= n:
            continue
        fit_floor = 1e6 / n_fit           # the fit sample's own 1-FP rate
        if rate >= fit_floor:
            continue                      # measurable there; nothing to extrapolate
        if (n - n_fit) * rate / 1e6 < min_expected_fp:
            continue                      # the remainder cannot resolve it
        ratios, realized, methods = [], [], []
        for _ in range(trials):
            idx = rng.choice(n, size=n_fit, replace=False)
            held = np.ones(n, dtype=bool)
            held[idx] = False
            thr, method = ESTIMATORS[estimator](arr[idx], rate)
            if thr is None or not np.isfinite(thr):
                continue
            got = float(np.mean(arr[held] >= thr) * 1e6)
            methods.append(method)
            realized.append(got)
            ratios.append(got / rate)
        if not ratios:
            continue
        rows.append({
            "requested_per_million": rate,
            "n_fit_benign": n_fit,
            "decades": float(np.log10(fit_floor / rate)),
            "trials": len(ratios),
            "method": max(set(methods), key=methods.count),
            "realized_per_million_median": float(np.median(realized)),
            "ratio_median": float(np.median(ratios)),
            "ratio_p05": float(np.percentile(ratios, 5)),
            "ratio_p95": float(np.percentile(ratios, 95)),
            "share_zero_fp": float(np.mean(np.asarray(realized) == 0.0)),
        })
    return sorted(rows, key=lambda r: r["decades"])


def decades_needed(n_benign: int, level: int) -> float:
    """How far past its own 1-FP floor a pool must reach to name this level."""
    if n_benign <= 0 or level <= 0:
        return float("inf")
    return float(np.log10((1e6 / n_benign) / (level / 100.0)))


def threshold_stability(
    benign_probs: np.ndarray,
    *,
    level: int,
    trials: int = 50,
    fraction: float = 0.8,
    seed: int = 42,
    estimator: str = "shared",
) -> dict[str, Any]:
    """Spread of the fitted threshold across resamples of the benign pool.

    The deployed operating point is re-derived on every publish (37 azoth
    deploys in the 90 days to 2026-09-15). If the estimator pins the threshold
    to the pool's most extreme order statistic, each publish inherits whatever
    single anomalous benign arrived that night, and the realized FP rate swings
    with it. This quantifies that sensitivity in FP-rate terms: how far the
    realized rate moves when 20% of the pool is resampled.
    """
    rng = np.random.default_rng(seed)
    arr = np.asarray(benign_probs, dtype=np.float64)
    n = arr.size
    k = max(int(n * fraction), 1)
    thresholds, rates = [], []
    for _ in range(trials):
        sub = arr[rng.choice(n, size=k, replace=False)]
        threshold, _ = ESTIMATORS[estimator](sub, level / 100.0)
        if threshold is None:
            continue
        thresholds.append(threshold)
        rates.append(float(np.mean(arr >= threshold) * 1e6))
    if not thresholds:
        return {"level": level, "estimator": estimator, "trials": 0}
    return {
        "level": level,
        "estimator": estimator,
        "trials": len(thresholds),
        "threshold_median": float(np.median(thresholds)),
        "threshold_p05": float(np.percentile(thresholds, 5)),
        "threshold_p95": float(np.percentile(thresholds, 95)),
        "fp_per_million_median": float(np.median(rates)),
        "fp_per_million_p05": float(np.percentile(rates, 5)),
        "fp_per_million_p95": float(np.percentile(rates, 95)),
        "fp_per_million_spread": float(np.percentile(rates, 95) - np.percentile(rates, 5)),
    }


# --- slice loading -----------------------------------------------------------

_META_SQL = """
SELECT id,
       COALESCE(EXTRACT(EPOCH FROM created_at)::bigint, 0),
       feed,
       (parent <> '' OR filename LIKE 'embedded:%%'),
       score,
       canonical_sha256
FROM samples
WHERE file_type = %s AND label IN ('bad', 'good')
"""


def _fetch_metadata(dsn: str, file_type: str) -> dict[int, tuple[int, str, bool, int, str]]:
    """Ingest metadata for every labeled row of a file type, keyed by row id."""
    with collimator_data._connect(dsn) as conn, conn.cursor(name="backtest_meta") as cur:
        cur.itersize = 50_000
        cur.execute(_META_SQL, (file_type,))
        return {
            int(rid): (int(ts), feed or "", bool(carved), int(score or 0), canon or "")
            for rid, ts, feed, carved, score, canon in cur
        }


def load_route_slice(
    score_table: Path | str,
    dsn: str,
    file_type: str,
    *,
    cache_dir: Path | str = "out/cache/backtest",
    refresh: bool = False,
) -> RouteSlice:
    """Join the policy search's score table with hopper ingest metadata.

    The score table is the same artifact ``azoth_route_policy_search.py``
    consumes, so a backtest scores exactly the rows the shipped policy was
    chosen on — no re-extraction, no model load. The DB join is cached; after
    the first call a slice loads in about a second.
    """
    score_table = Path(score_table)
    cache_dir = Path(cache_dir)
    # The score table holds every route for every row (73 x 19.4M float32 =
    # 5.7 GB); npz materializes the whole `scores` array to read one route, so
    # loading it costs minutes. Cache this file type's slice — scores and
    # metadata together — keyed by the table's mtime+size, and later runs skip
    # it entirely. This is what makes an experiment seconds rather than a wait.
    stat = score_table.stat()
    key = f"v{SLICE_CACHE_VERSION}-{file_type}-{int(stat.st_mtime)}-{stat.st_size}"
    cache_path = cache_dir / f"{key}.npz"
    if cache_path.is_file() and not refresh:
        LOG.info("slice cache hit: %s", cache_path)
        cached = np.load(cache_path, allow_pickle=True)
        row_ids, labels = cached["row_ids"], cached["labels"]
        scores = {str(n): cached[f"score::{n}"] for n in cached["score_routes"]}
        return RouteSlice(
            file_type=file_type, row_ids=row_ids, labels=labels, scores=scores,
            ingested_at=cached["ingested_at"], feed=cached["feed"],
            carved=cached["carved"], cleave_score=cached["cleave_score"],
            partition=cached["partition"],
        )
    LOG.info("reading score table %s (first run for this bundle)", score_table)
    table = np.load(score_table, allow_pickle=True)
    sel = table["file_types"] == file_type
    row_ids = table["row_ids"][sel].astype(np.int64)
    labels = table["labels"][sel].astype(np.int8)
    all_scores = table["scores"]
    scores = {}
    for i, name in enumerate(table["route_names"]):
        col = all_scores[i][sel].astype(np.float64)
        if not np.all(np.isnan(col)):
            scores[str(name)] = col
    del all_scores, table
    LOG.info("fetching ingest metadata for %s (%d rows)", file_type, row_ids.size)
    meta = _fetch_metadata(dsn, file_type)
    blank = (0, "", False, 0, "")
    rows = [meta.get(int(r), blank) for r in row_ids]
    ingested_at = np.array([r[0] for r in rows], dtype=np.int64)
    feed = np.array([r[1] for r in rows])
    carved = np.array([r[2] for r in rows], dtype=bool)
    cleave_score = np.array([r[3] for r in rows], dtype=np.int32)
    partition = np.array([
        collimator_data.partition_of(r[4]) if len(r[4]) >= 2 else "train" for r in rows
    ])
    cache_dir.mkdir(parents=True, exist_ok=True)
    np.savez(
        cache_path, row_ids=row_ids, labels=labels,
        score_routes=np.array(sorted(scores)),
        ingested_at=ingested_at, feed=feed, carved=carved,
        cleave_score=cleave_score, partition=partition,
        **{f"score::{k}": v for k, v in scores.items()},
    )
    LOG.info("cached slice → %s", cache_path)
    missing = int((ingested_at == 0).sum())
    if missing:
        LOG.warning("%d/%d rows have no ingest timestamp; excluded from time splits",
                    missing, row_ids.size)
    return RouteSlice(
        file_type=file_type, row_ids=row_ids, labels=labels, scores=scores,
        ingested_at=ingested_at, feed=feed, carved=carved,
        cleave_score=cleave_score, partition=partition,
    )
