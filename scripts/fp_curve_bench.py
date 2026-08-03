#!/usr/bin/env python3
"""Scale-ladder backtest harness for the FP-curve experiments.

No target route can measure L0-1, L21-22 or L250-300 (PE's honest floor is
~488 FP/100M), so accuracy is scored where deep quantiles ARE measurable:
subsample a deep teacher pool down to rung sizes that mimic real routes, fit
each estimator on the subsample alone, and count the realized false positives
its predicted thresholds produce on the **full** teacher pool.

Outputs two JSONL streams under ``out/experiments/fp_curves/<tag>/``:

* ``points.jsonl`` — one row per (estimator, pool, rung, draw, level):
  predicted threshold, realized FP on the full pool, band, measured truth.
* ``fits.jsonl`` — one row per (estimator, pool, rung, draw): fit cost and
  the curve-shape diagnostics (monotonicity, dial resolution, smoothness).

``scripts/fp_curve_report.py`` turns those into the leaderboard.

Examples::

    .venv/bin/python scripts/fp_curve_bench.py --estimators b0,exp1 --draws 50
    .venv/bin/python scripts/fp_curve_bench.py --cliff --estimators b0,exp1
"""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import multiprocessing as mp
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fp_curve_estimators import _MODULES, POOLED, get_fit  # noqa: E402
from fp_curve_estimators.base import (  # noqa: E402
    SATURATION_LOGIT,
    PooledContext,
    draw_seed,
    empirical_threshold,
    monotone_violations,
)
from fp_curve_estimators.pools import (  # noqa: E402
    TEACHER_POOLS,
    Pool,
    fleet_context,
    load_pool,
    pool_path,
    route_filegroup,
)

log = logging.getLogger("fp_curve_bench")

# Verification levels: every deploy-grid anchor that matters plus the
# between-anchor probes the proposal names (L1.5, L21, L21.5, L22, L275) —
# the whole point is that a curve must answer levels that are not anchors.
VERIFICATION_LEVELS: tuple[float, ...] = (
    0, 0.5, 1, 1.5, 2, 3, 4, 5, 7.5, 10, 15, 20, 21, 21.5, 22, 25, 30, 40, 50,
    60, 75, 80, 90, 100, 125, 150, 175, 200, 250, 275, 300, 400, 500, 750,
    1000, 1500, 2000, 2500, 3000, 5000, 7500, 10000, 15000, 25000,
)

# Rungs: rtf / gem / PE-eval-slice / PE-full scales.
DEFAULT_RUNGS: tuple[int, ...] = (800, 2500, 25_000, 200_000)

# The historical PE min_sample_score straddle of the incumbent's 25k regime
# switch. Two rungs either side of the cliff, same pool, same draws.
CLIFF_RUNGS: tuple[int, ...] = (24_776, 25_376)

# A rung is scored against the full pool, so the pool must be deeper than the
# rung by this factor or the backtest is measuring the estimator against its
# own training data.
MIN_POOL_OVERSAMPLE = 4

# Dense level grid for the monotonicity / smoothness diagnostics.
_DIAG_LEVELS = np.geomspace(0.5, 25_000.0, 400)
# The strict end of the dial, scored separately: it is what scan consumes for
# the tightest operating points and what no route can measure directly.
_LOW_END_LEVELS = np.geomspace(0.5, 100.0, 200)

_WORKER_STATE: dict[str, Any] = {}


def _fit_and_score(args: tuple[str, int, int, list[str]]) -> tuple[list[dict], list[dict]]:
    """One draw: subsample, fit every estimator, score on the full pool."""
    pool_name, m, draw, estimators = args
    pool: Pool = _WORKER_STATE["pool"]
    contexts: dict[str, Any] = _WORKER_STATE["contexts"]
    levels = _WORKER_STATE["levels"]
    band_q = _WORKER_STATE["band_q"]

    rng = np.random.default_rng(draw_seed(pool_name, m, draw))
    idx = rng.choice(pool.n_benign, size=m, replace=False)
    sample = np.sort(pool.benign[idx])
    meta = pool.meta(n_benign=m)

    points: list[dict] = []
    fits: list[dict] = []
    for name in estimators:
        context = contexts[name]
        started = time.perf_counter()
        try:
            model = get_fit(name)(sample, meta, context)
            thr = model.thresholds(levels)
        except Exception as exc:  # noqa: BLE001 — a fit failure is a result, not a crash
            fits.append({
                "estimator": name, "pool": pool_name, "m": m, "draw": draw,
                "fit_seconds": time.perf_counter() - started, "failed": True,
                "error": f"{type(exc).__name__}: {exc}",
            })
            continue
        fit_seconds = time.perf_counter() - started

        fp = pool.realized_fp(thr)
        recall_hat = pool.recall(thr)
        band_lo = np.empty(levels.size)
        band_hi = np.empty(levels.size)
        for i, level in enumerate(levels):
            band_lo[i], band_hi[i] = model.band(float(level), band_q)
        fp_at_lo = pool.realized_fp(band_lo)  # lower threshold -> more FP
        fp_at_hi = pool.realized_fp(band_hi)

        # Measured truth on the full pool, where the full pool can measure it.
        truth_ok = levels >= pool.floor_per_100M
        t_star = np.full(levels.size, np.nan)
        recall_star = np.full(levels.size, np.nan)
        if truth_ok.any():
            t_star[truth_ok] = empirical_threshold(pool.benign, levels[truth_ok])
            recall_star[truth_ok] = pool.recall(t_star[truth_ok])

        for i, level in enumerate(levels):
            points.append({
                "estimator": name, "pool": pool_name, "m": m, "draw": draw,
                "level": float(level),
                "t_hat": float(thr[i]),
                "fp_expected": float(level) * pool.n_benign / 1e8,
                "fp_realized": int(fp[i]),
                "fp_band_lo": int(fp_at_lo[i]),
                "fp_band_hi": int(fp_at_hi[i]),
                "band_lo": float(band_lo[i]),
                "band_hi": float(band_hi[i]) if np.isfinite(band_hi[i]) else None,
                "t_star": None if np.isnan(t_star[i]) else float(t_star[i]),
                "recall_hat": float(recall_hat[i]),
                "recall_star": None if np.isnan(recall_star[i]) else float(recall_star[i]),
                "extrapolated": bool(model.is_extrapolated(float(level))),
            })

        diag = model.thresholds(_DIAG_LEVELS)
        grid = model.thresholds(np.asarray(VERIFICATION_LEVELS, dtype=np.float64))
        # d(logit t)/d(log level): total variation is the smoothness metric —
        # a curve with cliffs or flat-then-step artefacts scores high.
        dx = np.diff(np.log(_DIAG_LEVELS))
        slope = np.diff(diag) / dx
        # Shape gates are scored where the curve still has room to move. Once
        # a threshold reaches the score ceiling every stricter level ties
        # there, which is a fact about the model's output range, not about the
        # estimator — `ceiling_fraction` is where that shows up instead.
        below = diag < SATURATION_LOGIT - 1e-9
        grid_below = grid[grid < SATURATION_LOGIT - 1e-9]
        fits.append({
            "estimator": name, "pool": pool_name, "m": m, "draw": draw,
            "fit_seconds": fit_seconds, "failed": False,
            "monotone_violations": monotone_violations(model, _DIAG_LEVELS),
            "monotone_violations_below_ceiling": int(
                np.sum(np.diff(diag[below]) >= 0.0) if below.sum() > 1 else 0,
            ),
            "distinct_grid_fraction": float(len(np.unique(np.round(grid, 12))) / grid.size),
            "distinct_below_ceiling": float(
                len(np.unique(np.round(grid_below, 12))) / grid_below.size,
            ) if grid_below.size else float("nan"),
            "ceiling_fraction": float(np.mean(~below)),
            "slope_total_variation": float(np.abs(np.diff(slope[below[:-1]])).sum()),
            **_low_end_diagnostics(model),
            "fit_floor_level": float(model.fit_floor_level),
            "max_observed_logit": float(model.max_observed_logit),
        })
    return points, fits


def _low_end_diagnostics(model) -> dict[str, float]:
    """Curve-shape diagnostics restricted to L0.5-L100.

    The strict end is where every route is extrapolating and where a curve
    consumed by scan is most likely to show cliffs or flat runs, so it is
    scored on its own rather than being averaged into a full-grid number that
    the well-measured loose end dominates.
    """
    thr = model.thresholds(_LOW_END_LEVELS)
    below = thr < SATURATION_LOGIT - 1e-9
    out = {
        "low_ceiling_fraction": float(np.mean(~below)),
        "low_mono_violations": 0,
        "low_slope_tv": 0.0,
        "low_distinct_fraction": float("nan"),
    }
    if below.sum() > 2:
        live = thr[below]
        out["low_mono_violations"] = int(np.sum(np.diff(live) >= 0.0))
        out["low_distinct_fraction"] = float(len(np.unique(np.round(live, 12))) / live.size)
        dx = np.diff(np.log(_LOW_END_LEVELS[below]))
        slope = np.diff(live) / dx
        out["low_slope_tv"] = float(np.abs(np.diff(slope)).sum())
    return out


def _context_for(
    route: str, contexts_all: Any, exclusion: str, loaded: dict[str, Pool] | None = None,
) -> Any:
    """Leave-route-out context for ``route``.

    Topology rule: a route never sees itself, its filegroup parent, or its
    filetype children — those pools are literally the same files scored by a
    related model, so borrowing their tail would be self-teaching. ``strict``
    additionally drops the general pool, which overlaps every route.

    Estimators that pool tail *shape* (EXP-3/4) need only the kept tails;
    EXP-5 trains on subsample-to-truth pairs and so needs whole pools, which
    are attached as ``extras['full_pools']`` — filtered by the same rule.
    """
    kind, _, name = route.partition("/")
    family = route_filegroup(route)
    drop: set[str] = {route}
    if kind == "filetypes":
        drop.add(f"filegroups/{family}")
    elif kind == "filegroups":
        drop.update(t.route for t in contexts_all.tails if route_filegroup(t.route) == name)
    if exclusion == "strict":
        drop.add("general")
    ctx = contexts_all
    for r in drop:
        ctx = ctx.without(r)
    full_pools = {
        n: p.benign for n, p in (loaded or {}).items() if n not in drop
    }
    return PooledContext(tails=ctx.tails, extras={"full_pools": full_pools})


def run(
    pool_names: list[str],
    estimators: list[str],
    rungs: list[int],
    draws: int,
    levels: np.ndarray,
    out_dir: Path,
    jobs: int,
    band_q: float,
    exclusion: str,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    points_path = out_dir / "points.jsonl"
    fits_path = out_dir / "fits.jsonl"
    manifest = {
        "pools": pool_names, "estimators": estimators, "rungs": rungs,
        "draws": draws, "levels": [float(x) for x in levels],
        "band_q": band_q, "exclusion": exclusion,
        "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    loaded: dict[str, Pool] = {}
    for name in pool_names:
        loaded[name] = load_pool(name)
        log.info(
            "pool %-22s benign=%9d malware=%9d floor=%8.1f FP/100M",
            name, loaded[name].n_benign, loaded[name].n_malware,
            loaded[name].floor_per_100M,
        )
    contexts_all = fleet_context()
    log.info("pooling context: %d routes (leave-route-out applied per pool)", len(contexts_all))

    n_points = n_fits = 0
    with points_path.open("w") as pf, fits_path.open("w") as ff:
        for pool_name, pool in loaded.items():
            _WORKER_STATE["pool"] = pool
            _WORKER_STATE["levels"] = levels
            _WORKER_STATE["band_q"] = band_q
            ctx = _context_for(pool_name, contexts_all, exclusion, loaded)
            _WORKER_STATE["contexts"] = {
                name: (ctx if name in POOLED else None) for name in estimators
            }
            # Pooled estimators fit their cross-route structure once per
            # context; doing it here (pre-fork) rather than lazily inside each
            # worker means one fit instead of `jobs` identical ones.
            for name in estimators:
                if name not in POOLED:
                    continue
                prepare = getattr(importlib.import_module(
                    f"fp_curve_estimators.{_MODULES[name]}"), "prepare", None)
                if prepare is not None:
                    started_prep = time.time()
                    prepare(ctx)
                    log.info("%s: context prepared in %.1fs", name, time.time() - started_prep)
            # A rung is only a fair test when the pool it is verified against
            # is materially deeper than the rung itself; at m ~ n_pool the
            # "backtest" degenerates into self-verification.
            usable = [m for m in rungs if m * MIN_POOL_OVERSAMPLE <= pool.n_benign]
            tasks = [
                (pool_name, m, draw, estimators)
                for m in usable
                for draw in range(draws)
            ]
            skipped = [m for m in rungs if m not in usable]
            if skipped:
                log.info(
                    "pool %s (n=%d): rungs %s skipped — need %dx headroom to verify",
                    pool_name, pool.n_benign, skipped, MIN_POOL_OVERSAMPLE,
                )
            if not tasks:
                continue
            started = time.time()
            if jobs > 1:
                with ProcessPoolExecutor(
                    max_workers=jobs, mp_context=mp.get_context("fork"),
                ) as pool_exec:
                    results = list(pool_exec.map(_fit_and_score, tasks, chunksize=1))
            else:
                results = [_fit_and_score(t) for t in tasks]
            for points, fits in results:
                for row in points:
                    pf.write(json.dumps(row) + "\n")
                for row in fits:
                    ff.write(json.dumps(row) + "\n")
                n_points += len(points)
                n_fits += len(fits)
            log.info(
                "pool %-22s %4d fits in %6.1fs (%d points)",
                pool_name, len(tasks) * len(estimators), time.time() - started, n_points,
            )

    manifest["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    manifest["n_points"] = n_points
    manifest["n_fits"] = n_fits
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    log.info("wrote %s (%d points, %d fits)", out_dir, n_points, n_fits)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--pools", default="",
                    help="comma-separated routes (default: teacher pools on disk)")
    ap.add_argument("--estimators", default="b0,exp1")
    ap.add_argument("--rungs", default=",".join(str(r) for r in DEFAULT_RUNGS))
    ap.add_argument("--draws", type=int, default=50)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--band-q", type=float, default=0.90)
    ap.add_argument("--exclusion", choices=("topology", "strict"), default="topology")
    ap.add_argument("--cliff", action="store_true",
                    help="cliff test: rungs straddling the 25k regime switch")
    ap.add_argument("--out", default="out/experiments/fp_curves")
    ap.add_argument("--tag", default="ladder")
    args = ap.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    if args.pools:
        pool_names = [p.strip() for p in args.pools.split(",") if p.strip()]
    else:
        pool_names = [p for p in TEACHER_POOLS if pool_path(p).exists()]
        if "general" not in pool_names:
            log.warning(
                "general OOF pool absent (%s) — Phase 0 has not landed; "
                "L21-22 stays aggregate-only", pool_path("general"),
            )
    rungs = CLIFF_RUNGS if args.cliff else tuple(int(r) for r in args.rungs.split(","))
    if args.cliff:
        pool_names = [p for p in pool_names if load_pool(p).n_benign >= 200_000]

    return_code = run(
        pool_names=pool_names,
        estimators=[e.strip() for e in args.estimators.split(",") if e.strip()],
        rungs=list(rungs),
        draws=args.draws,
        levels=np.asarray(VERIFICATION_LEVELS, dtype=np.float64),
        out_dir=Path(args.out) / (f"cliff-{args.tag}" if args.cliff else args.tag),
        jobs=args.jobs,
        band_q=args.band_q,
        exclusion=args.exclusion,
    )
    return 0 if return_code is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
