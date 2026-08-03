#!/usr/bin/env python3
"""Score-pool loading for the FP-curve benchmark.

Honest scores only. Every pool here is single-model out-of-fold
(``oof_route_scores/<kind>/<route>/threshold_scores.npz``), plus the general
model's merged OOF pool once ``azoth-publish-train`` lands it. In-sample
train-partition scores (``score_table.npz``) are optimistically biased and
are never loaded — a tail fitted on them would predict thresholds the
deployed model cannot hold.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, "src")

from collimator.experiment import EXPERIMENT_FILEGROUPS  # noqa: E402
from collimator.features import FORMAT_GROUPS  # noqa: E402

from .base import PooledContext, RouteMeta, RouteTail, to_logit  # noqa: E402

OOF_ROOT = Path("out/models/azoth/oof_route_scores")
# Phase 0's deepest teacher: the merged general-model OOF pool. Produced by
# `make azoth-oof-merge-general` inside the weekly `azoth-publish-train`
# chain; absent until that run finishes, and simply skipped when absent.
GENERAL_SCORES = Path("out/models/azoth/general/threshold_scores.npz")
CACHE_DIR = Path("out/experiments/fp_curves/cache")

# Teacher pools for the scale-ladder backtest, deepest first. These are the
# only pools where the deep quantiles an estimator must reach are actually
# measurable, so they are what "accuracy" is scored against.
TEACHER_POOLS: tuple[str, ...] = (
    "general",  # skipped automatically until Phase 0 lands it
    "filegroups/scripts",
    "filegroups/source",
    "filetypes/java_class",
    "filegroups/portable",
    "filetypes/c",
    "filetypes/javascript",
)

# Deep-dive evaluation targets from the proposal.
TARGET_ROUTES: tuple[str, ...] = ("filetypes/pe", "filetypes/ruby", "filetypes/gem")

# Number of top benign scores kept per route as pooling context. Pooled tail
# estimators fit above a ~90-95% exceedance threshold; 50k tail points cover
# that for every route in the fleet while keeping the whole context under
# ~30MB.
CONTEXT_TAIL_KEEP = 50_000

_FILETYPE_TO_FILEGROUP: dict[str, str] = {}
for _group, _types in EXPERIMENT_FILEGROUPS.items():
    for _ft in _types:
        _FILETYPE_TO_FILEGROUP[_ft] = _group
# Fallback for filetypes with no training filegroup of their own (archives,
# office documents, packaging manifests): the feature-layer format group is
# the next-best statement of "these files are alike".
_FORMAT_GROUP_ALIAS = {
    "script": "scripts", "native_binary": "native", "archive_package": "archive",
    "document": "documents", "source_code": "source", "config_data": "config",
    "media": "media",
}
for _group, _types in FORMAT_GROUPS.items():
    for _ft in _types:
        _FILETYPE_TO_FILEGROUP.setdefault(_ft, _FORMAT_GROUP_ALIAS.get(_group, _group))


def route_filegroup(route: str) -> str:
    """Hierarchy parent for a route: its filegroup, or a sensible fallback.

    ``filegroups/x`` is its own family. A filetype route uses its training
    filegroup when it has one, else its feature-layer format group, else
    ``other``. Route names carry both spellings of the same type in the
    corpus (``python-bytecode`` / ``python_bytecode``), so both normalise to
    the same family.
    """
    kind, _, name = route.partition("/")
    if kind == "filegroups":
        return name
    if route == "general":
        return "general"
    key = name.replace("-", "_")
    return _FILETYPE_TO_FILEGROUP.get(key, _FILETYPE_TO_FILEGROUP.get(name, "other"))


@dataclass(frozen=True)
class Pool:
    """One route's honest scores, in logit space, sorted ascending."""

    route: str
    filegroup: str
    benign: np.ndarray
    malware: np.ndarray

    @property
    def n_benign(self) -> int:
        return int(self.benign.size)

    @property
    def n_malware(self) -> int:
        return int(self.malware.size)

    @property
    def floor_per_100M(self) -> float:
        return 1e8 / max(self.n_benign, 1)

    def meta(self, n_benign: int | None = None) -> RouteMeta:
        return RouteMeta(
            route=self.route,
            filegroup=self.filegroup,
            n_benign=self.n_benign if n_benign is None else int(n_benign),
            n_malware=self.n_malware,
        )

    def tail(self, keep: int = CONTEXT_TAIL_KEEP) -> RouteTail:
        k = min(int(keep), self.n_benign)
        return RouteTail(
            route=self.route,
            filegroup=self.filegroup,
            n_benign=self.n_benign,
            tail_logits=self.benign[self.n_benign - k:],
        )

    def realized_fp(self, threshold_logit: np.ndarray | float) -> np.ndarray:
        """Benign FP count on this (full) pool at each threshold."""
        t = np.atleast_1d(np.asarray(threshold_logit, dtype=np.float64))
        return self.n_benign - np.searchsorted(self.benign, t, side="left")

    def recall(self, threshold_logit: np.ndarray | float) -> np.ndarray:
        """Malware recall on this pool at each threshold."""
        t = np.atleast_1d(np.asarray(threshold_logit, dtype=np.float64))
        above = self.n_malware - np.searchsorted(self.malware, t, side="left")
        return above / max(self.n_malware, 1)


def pool_path(route: str) -> Path:
    return GENERAL_SCORES if route == "general" else OOF_ROOT / route / "threshold_scores.npz"


def available_routes(include_general: bool = True) -> list[str]:
    """Every route with an honest OOF pool on disk."""
    routes = sorted(
        f"{p.parent.parent.name}/{p.parent.name}"
        for p in OOF_ROOT.glob("*/*/threshold_scores.npz")
    )
    if include_general and GENERAL_SCORES.exists():
        routes.insert(0, "general")
    return routes


def load_pool(route: str, cache: bool = True) -> Pool:
    """Load one route's OOF pool as sorted logit arrays.

    Cached as a small npz of just the two sorted arrays: the source files
    carry sha256/row_id columns that cost far more to read than the scores,
    and the benchmark re-reads pools on every run.
    """
    src = pool_path(route)
    if not src.exists():
        raise FileNotFoundError(f"no OOF pool for {route}: {src}")
    cache_file = CACHE_DIR / f"{route.replace('/', '__')}.npz"
    stamp = f"{src.stat().st_mtime_ns}:{src.stat().st_size}"
    if cache and cache_file.exists():
        cached = np.load(cache_file, allow_pickle=False)
        if str(cached["stamp"]) == stamp:
            return Pool(route, route_filegroup(route), cached["benign"], cached["malware"])
    with np.load(src, allow_pickle=False) as data:
        probs = np.asarray(data["probs"], dtype=np.float64)
        labels = np.asarray(data["labels"])
    benign = np.sort(np.asarray(to_logit(probs[labels == 0])))
    malware = np.sort(np.asarray(to_logit(probs[labels == 1])))
    if cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        np.savez(cache_file, benign=benign, malware=malware, stamp=np.array(stamp))
    return Pool(route, route_filegroup(route), benign, malware)


def build_context(pools: dict[str, Pool], keep: int = CONTEXT_TAIL_KEEP) -> PooledContext:
    """Pooling context over already-loaded pools (caller applies the
    leave-route-out rule with ``context.without(route)``)."""
    return PooledContext(tails=tuple(p.tail(keep) for p in pools.values()))


def fleet_context(keep: int = CONTEXT_TAIL_KEEP, cache: bool = True) -> PooledContext:
    """Pooling context over EVERY route with an honest OOF pool.

    The hierarchy is only as good as the number of routes it can estimate
    between-route variance from: six teacher pools give a family prior so wide
    it barely shrinks anything, while the full fleet of 73 is what production
    would actually have. Cached as a single npz of tails (~30MB) so repeated
    benchmark runs do not re-read 25M rows.
    """
    cache_file = CACHE_DIR / f"fleet_tails_{keep}.npz"
    routes = available_routes()
    if cache and cache_file.exists():
        with np.load(cache_file, allow_pickle=False) as data:
            names = [str(x) for x in data["routes"]]
            if names == routes:
                return PooledContext(tails=tuple(
                    RouteTail(
                        route=name,
                        filegroup=route_filegroup(name),
                        n_benign=int(data["n_benign"][i]),
                        tail_logits=data[f"tail_{i}"],
                    )
                    for i, name in enumerate(names)
                ))
    tails = [load_pool(r).tail(keep) for r in routes]
    if cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        np.savez(
            cache_file,
            routes=np.array(routes),
            n_benign=np.array([t.n_benign for t in tails]),
            **{f"tail_{i}": t.tail_logits for i, t in enumerate(tails)},
        )
    return PooledContext(tails=tuple(tails))
