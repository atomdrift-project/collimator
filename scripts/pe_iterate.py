#!/usr/bin/env python3
"""Fast PE-specialist iteration loop over the experiment harness's matrix cache.

Why this exists
---------------
Root-causing PE recall needs many fits against ONE fixed slice. Going through
``make experiment`` each time re-runs vocab + extraction (~35 min) even when
only hyperparameters changed. The harness already caches extracted matrices
(``experiment.py`` level 2, keyed by corpus + feature env), so once that cache
is warm a fit is the only remaining cost.

This script reads those cached matrices directly and sweeps ``TrainConfig``
variants against them, so an iteration is a fit, not a pipeline.

Populate the cache once (see ``--print-seed-cmd``), then iterate here.

Metric
------
Reports recall at ABSOLUTE benign FP counts, not at a per-100M level. PE's
benign eval pool (~25k) can only resolve ~3900 FP/100M, so every level below
L40 collapses onto 1 FP -- and ``quantile_severity_threshold`` switches regimes
at 25,000 benign (below: L25 = 5 FP; at or above: L25 ~= 1 FP), which makes
level-indexed numbers jump ~10 points for reasons unrelated to the model. FP
counts are regime-independent and comparable across runs.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import features, train  # noqa: E402
from collimator.model import predict_proba  # noqa: E402

LOG = logging.getLogger("pe_iterate")

# Benign FP counts to report recall at. 1 is the deploy operating point for a
# ~25k-benign slice; the rest show how fast recall recovers as the tail opens.
FP_POINTS: tuple[int, ...] = (0, 1, 2, 3, 5, 10, 25, 50, 100, 250)


def find_cache(cache_dir: Path, matrix_hash: str | None) -> str:
    """Resolve the matrix hash to load, or list candidates and exit."""
    stems = sorted(
        p.name[len("matrix_"):-len("_Xtrain.npz")]
        for p in cache_dir.glob("matrix_*_Xtrain.npz")
    )
    if not stems:
        raise SystemExit(f"no cached matrices under {cache_dir}; run the seed command first")
    if matrix_hash:
        if matrix_hash not in stems:
            raise SystemExit(f"{matrix_hash} not in cache; have: {stems}")
        return matrix_hash
    if len(stems) == 1:
        return stems[0]
    newest = max(
        stems, key=lambda h: (cache_dir / f"matrix_{h}_Xtrain.npz").stat().st_mtime,
    )
    LOG.info("%d cached matrices; using newest (%s). Pass --matrix-hash to pin.",
             len(stems), newest)
    return newest


def load_cache(cache_dir: Path, matrix_hash: str) -> dict[str, Any]:
    x_train = sp.load_npz(cache_dir / f"matrix_{matrix_hash}_Xtrain.npz")
    x_test = sp.load_npz(cache_dir / f"matrix_{matrix_hash}_Xtest.npz")
    extras = np.load(cache_dir / f"matrix_{matrix_hash}.npz", allow_pickle=True)
    spec = features.FeatureSpec.load(cache_dir / f"matrix_{matrix_hash}_spec.json")
    return {
        "X_train": x_train,
        "y_train": extras["y_train"],
        "X_test": x_test,
        "y_test": extras["y_test"],
        "train_file_types": extras["train_file_types"],
        "spec": spec,
    }


def fp_curve(y_true: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    """Recall on malware at thresholds admitting exactly N benign FPs.

    Threshold for N>0 is the Nth-largest benign score (so exactly N benign
    land at or above it); for N=0 it is just above the max benign score.
    """
    benign = np.sort(scores[y_true == 0])
    malware = scores[y_true == 1]
    n_ben = benign.size
    out: dict[str, Any] = {
        "n_benign": int(n_ben),
        "n_malware": int(malware.size),
        "min_observable_per_100M": (1e8 / n_ben) if n_ben else None,
        "recall_at_fp": {},
    }
    for fp in FP_POINTS:
        if fp > n_ben:
            continue
        thr = float(np.nextafter(benign[-1], np.inf)) if fp == 0 else float(benign[n_ben - fp])
        out["recall_at_fp"][fp] = {
            "recall": float(np.mean(malware >= thr)),
            "threshold": thr,
            "fp_per_100M": fp / n_ben * 1e8,
        }
    return out


def run_variant(
    name: str, cache: dict[str, Any], overrides: dict[str, Any], base: dict[str, Any],
    save_scores_dir: Path | None = None,
) -> dict[str, Any]:
    cfg_kwargs = {**base, **overrides}
    config = train.TrainConfig(**cfg_kwargs)
    started = time.time()
    result = train.train(
        cache["X_train"],
        cache["y_train"],
        config,
        feature_names=list(cache["spec"].feature_names),
        sample_file_types=cache["train_file_types"],
    )
    scores = predict_proba(result.model, cache["X_test"])
    if save_scores_dir is not None:
        save_scores_dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            save_scores_dir / f"{name}.npz",
            scores=scores.astype(np.float32),
            y_test=cache["y_test"].astype(np.int8),
        )
    curve = fp_curve(cache["y_test"], scores)
    return {
        "name": name,
        "overrides": overrides,
        "elapsed_s": round(time.time() - started, 1),
        "roc_auc": float(result.metrics.get("roc_auc", float("nan"))),
        "avg_precision": float(result.metrics.get("avg_precision", float("nan"))),
        **curve,
    }


def report(rows: list[dict[str, Any]]) -> None:
    fps = [fp for fp in FP_POINTS if any(fp in r["recall_at_fp"] for r in rows)]
    head = f"{'variant':<26}{'ROC':>8}{'fit_s':>7}" + "".join(f"{'fp='+str(f):>9}" for f in fps)
    print("\n" + head)
    print("-" * len(head))
    for r in rows:
        line = f"{r['name']:<26}{r['roc_auc']:>8.5f}{r['elapsed_s']:>7.0f}"
        for f in fps:
            entry = r["recall_at_fp"].get(f)
            line += f"{entry['recall']:>9.4f}" if entry else f"{'-':>9}"
        print(line)
    ref = rows[0]
    print(f"\neval slice: {ref['n_benign']} benign / {ref['n_malware']} malware "
          f"(min observable {ref['min_observable_per_100M']:.0f} FP/100M; "
          f"regime = {'STRICT quantile' if ref['n_benign'] >= 25000 else 'LENIENT absolute_fp'})")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache-dir", type=Path, default=Path("out/cache/experiment/azoth"))
    ap.add_argument("--matrix-hash", default=None,
                    help="Which cached matrix to load (default: newest).")
    ap.add_argument("--variants", type=Path, required=True,
                    help="JSON: {'base': {...TrainConfig...}, 'variants': {name: {overrides}}}")
    ap.add_argument("--out", type=Path, default=None, help="Write results JSON here.")
    ap.add_argument("--save-scores-dir", type=Path, default=None,
                    help="Save each variant's eval scores as <name>.npz here "
                         "(for cross-variant ensembling, e.g. seed-mean curves).")
    ap.add_argument("--log-level", default="INFO")
    args = ap.parse_args()
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")

    spec = json.loads(args.variants.read_text())
    base = spec.get("base", {})
    variants = spec["variants"]

    matrix_hash = find_cache(args.cache_dir, args.matrix_hash)
    cache = load_cache(args.cache_dir, matrix_hash)
    LOG.info("matrix %s: %d train x %d features, %d eval",
             matrix_hash, cache["X_train"].shape[0], cache["X_train"].shape[1],
             cache["X_test"].shape[0])

    rows = [run_variant(name, cache, ov, base, save_scores_dir=args.save_scores_dir)
            for name, ov in variants.items()]
    report(rows)
    if args.out:
        args.out.write_text(json.dumps(
            {"matrix_hash": matrix_hash, "base": base, "results": rows}, indent=2))
        LOG.info("wrote %s", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
