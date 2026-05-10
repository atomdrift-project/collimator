#!/usr/bin/env python3
"""N-gram depth × crit sweep — fast in-memory experimentation.

Optimized for 32-core / 128GB RAM / 96GB GPU machines:
  1. Incremental cache: only fetches new rows from DB.
  2. Split extraction: base features computed once, ngram features per-config.
  3. GPU training: XGBoost on CUDA with full VRAM.
  4. Full parallelism: 32 workers for extraction.

Usage:
    # First run (fetches from DB, saves cache):
    .venv/bin/python scripts/ngram_sweep.py --db postgres://hopper@localhost/hopper

    # Subsequent runs (loads from cache, fetches only new rows):
    .venv/bin/python scripts/ngram_sweep.py --db postgres://hopper@localhost/hopper

    # Custom configs:
    .venv/bin/python scripts/ngram_sweep.py --depths 0,2,3,4 --crits 0,1,2,3,4,5 --train-samples 50000
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import pickle
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from collimator import data, train
from collimator.features import (
    FeatureSpec,
    build_vocab,
    extract_all,
    feature_config_from_env,
)
from collimator.model import predict_proba

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s  %(message)s")

CACHE_DIR = Path("out/cache")
CACHE_FILE = CACHE_DIR / "cleave_cache.pkl"

# Feature groups that depend on ngram_path_depth / ngram_min_crit.
# Everything else is identical across configs and can be extracted once.
NGRAM_GROUPS = {"bigrams", "trigrams", "signature_synergy"}


def fetch_and_cache(db_path: str, max_id: int) -> dict[int, dict]:
    """Fetch all trainable cleave results with incremental caching."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_meta = CACHE_DIR / "cache_meta.json"

    cache: dict[int, dict] = {}
    old_max_id = 0

    # Load existing cache if available.
    if CACHE_FILE.exists() and cache_meta.exists():
        meta = json.loads(cache_meta.read_text())
        old_max_id = meta.get("max_id", 0)
        if old_max_id == max_id:
            log.info("loading cached cleave results (max_id=%d)", max_id)
            t0 = time.time()
            with open(CACHE_FILE, "rb") as f:
                cache = pickle.load(f)
            log.info("loaded %d rows from cache in %.1fs", len(cache), time.time() - t0)
            return cache
        # Incremental: load old cache, then fetch only new rows.
        log.info("loading existing cache (max_id=%d) for incremental update to %d",
                 old_max_id, max_id)
        t0 = time.time()
        with open(CACHE_FILE, "rb") as f:
            cache = pickle.load(f)
        log.info("loaded %d existing rows in %.1fs", len(cache), time.time() - t0)

    # Get all trainable IDs. ngram_sweep is a one-off feature search; it
    # caches scored predictions for every labeled row, so it pulls dev too.
    _, train_ids_labels, dev_ids_labels, test_ids_labels = data.partition_row_ids(
        db_path, min_malware_training_score=0, max_id=max_id,
    )
    all_ids = (
        [rid for rid, _ in train_ids_labels]
        + [rid for rid, _ in dev_ids_labels]
        + [rid for rid, _ in test_ids_labels]
    )

    if old_max_id > 0:
        # Only fetch IDs we don't have yet.
        new_ids = [rid for rid in all_ids if rid not in cache]
        log.info("incremental fetch: %d new rows (of %d total)", len(new_ids), len(all_ids))
        fetch_ids = new_ids
    else:
        fetch_ids = all_ids

    if fetch_ids:
        t0 = time.time()
        batch_size = 2000
        for i in range(0, len(fetch_ids), batch_size):
            batch = fetch_ids[i:i + batch_size]
            cache.update(data.fetch_cleave_results(db_path, batch))
            if (i // batch_size) % 20 == 0:
                log.info("  fetched %d / %d", min(i + batch_size, len(fetch_ids)), len(fetch_ids))
        log.info("fetched %d rows in %.1fs", len(fetch_ids), time.time() - t0)

    # Prune rows no longer in the trainable set (labels may have changed).
    valid_ids = set(all_ids)
    pruned = {k: v for k, v in cache.items() if k in valid_ids}
    if len(pruned) < len(cache):
        log.info("pruned %d stale rows from cache", len(cache) - len(pruned))
    cache = pruned

    # Save updated cache.
    log.info("saving cache to %s", CACHE_FILE)
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f, protocol=pickle.HIGHEST_PROTOCOL)
    cache_meta.write_text(json.dumps({"max_id": max_id, "n_rows": len(cache)}))
    log.info("cache saved (%.1f MB)", CACHE_FILE.stat().st_size / 1e6)
    return cache


def prepare_reports(
    ids_labels: list[tuple[int, int]],
    cache: dict[int, dict],
) -> tuple[list[dict], list[int]]:
    """Convert cached cleave results to (reports, labels) lists for extract_all."""
    reports = []
    labels = []
    for rid, label in ids_labels:
        item = cache.get(rid)
        if item is None:
            continue
        cr = item.get("cleave_result")
        if cr is None:
            continue
        try:
            report = json.loads(cr) if isinstance(cr, str) else cr
        except (json.JSONDecodeError, TypeError):
            continue
        reports.append(report)
        labels.append(label)
    return reports, labels


def _set_ngram_env(depth: int, crit: int) -> None:
    """Set ngram env vars and clear the config cache."""
    os.environ["COLLIMATOR_NGRAM_PATH_DEPTH"] = str(depth)
    os.environ["COLLIMATOR_NGRAM_MIN_CRIT"] = str(crit)
    feature_config_from_env.cache_clear()


def _disable_groups_env(groups: set[str]) -> None:
    """Disable specific feature groups via env var."""
    os.environ["COLLIMATOR_DISABLE_FEATURE_GROUPS"] = ",".join(sorted(groups))
    feature_config_from_env.cache_clear()


def _enable_all_groups_env() -> None:
    """Re-enable all feature groups."""
    os.environ.pop("COLLIMATOR_DISABLE_FEATURE_GROUPS", None)
    feature_config_from_env.cache_clear()


def _enable_only_groups_env(groups: set[str]) -> None:
    """Enable ONLY the specified groups (disable everything else)."""
    from collimator.features import FEATURE_GROUPS
    disable = set(FEATURE_GROUPS) - groups
    _disable_groups_env(disable)


def extract_base_features(
    reports: list[dict],
    labels: list[int],
    n_workers: int,
) -> tuple[sp.csr_matrix, np.ndarray, FeatureSpec]:
    """Extract all features EXCEPT ngram-dependent ones. Done once."""
    _disable_groups_env(NGRAM_GROUPS)
    spec = build_vocab(reports, n_workers=n_workers)
    X, y = extract_all(reports, labels, spec, n_workers=n_workers)
    _enable_all_groups_env()
    return X, y, spec


def extract_ngram_features(
    reports: list[dict],
    labels: list[int],
    depth: int,
    crit: int,
    n_workers: int,
) -> tuple[sp.csr_matrix, np.ndarray, FeatureSpec]:
    """Extract ONLY ngram-dependent features for one config."""
    _set_ngram_env(depth, crit)
    _enable_only_groups_env(NGRAM_GROUPS)
    spec = build_vocab(reports, n_workers=n_workers)
    X, y = extract_all(reports, labels, spec, n_workers=n_workers)
    _enable_all_groups_env()
    feature_config_from_env.cache_clear()
    return X, y, spec


def run_config(
    depth: int,
    crit: int,
    X_base_train: sp.csr_matrix,
    y_base_train: np.ndarray,
    X_base_test: sp.csr_matrix,
    y_base_test: np.ndarray,
    base_feature_names: list[str],
    train_reports: list[dict],
    train_labels: list[int],
    test_reports: list[dict],
    test_labels: list[int],
    seed: int,
    n_workers: int,
) -> dict:
    """Run one experiment: extract ngram features, hstack with base, train, evaluate."""
    label = f"depth={depth} crit={crit}"
    t0 = time.time()

    # Extract only the ngram-dependent features for this config.
    t1 = time.time()
    X_ngram_train, _, ngram_spec = extract_ngram_features(
        train_reports, train_labels, depth, crit, n_workers,
    )
    X_ngram_test, _, _ = extract_ngram_features(
        test_reports, test_labels, depth, crit, n_workers,
    )
    log.info("  [%s] ngram features: %d cols, extracted in %.1fs",
             label, X_ngram_train.shape[1], time.time() - t1)

    # Combine base + ngram features.
    X_train = sp.hstack([X_base_train, X_ngram_train], format="csr")
    X_test = sp.hstack([X_base_test, X_ngram_test], format="csr")
    feature_names = base_feature_names + ngram_spec.feature_names
    n_features = X_train.shape[1]

    log.info("  [%s] combined: %d features (%d base + %d ngram)",
             label, n_features, X_base_train.shape[1], X_ngram_train.shape[1])

    # Train with GPU.
    t2 = time.time()
    cfg = train.TrainConfig(
        seed=seed, n_estimators=1000, max_depth=16,
        learning_rate=0.02, early_stopping_rounds=100, beta=2.0, n_folds=2,
    )
    result = train.train(X_train, y_base_train, cfg, feature_names=feature_names)
    log.info("  [%s] trained (%.1fs)", label, time.time() - t2)

    # Evaluate.
    probs = predict_proba(result.model, X_test)
    threshold = result.optimal_threshold
    y_pred = (probs >= threshold).astype(int)
    y_true = y_base_test.astype(int)
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    fp = int(((y_pred == 1) & (y_true == 0)).sum())
    fn = int(((y_pred == 0) & (y_true == 1)).sum())
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)

    log.info("  [%s] → F1=%.4f Prec=%.4f Rec=%.4f FP=%d FN=%d (total %.1fs)",
             label, f1, precision, recall, fp, fn, time.time() - t0)
    return {
        "depth": depth, "crit": crit, "label": label,
        "n_features": n_features,
        "n_base_features": X_base_train.shape[1],
        "n_ngram_features": X_ngram_train.shape[1],
        "threshold": float(threshold),
        "test_f1": float(f1),
        "test_precision": float(precision),
        "test_recall": float(recall),
        "test_fp": fp, "test_fn": fn, "test_tp": tp,
        "cv_f1": float(result.metrics.get("f1", 0)),
        "train_samples": X_train.shape[0],
        "test_samples": X_test.shape[0],
    }


def main():
    parser = argparse.ArgumentParser(description="N-gram depth × crit sweep")
    parser.add_argument("--db", default="postgres://hopper@localhost/hopper")
    parser.add_argument("--train-samples", type=int, default=50_000)
    parser.add_argument("--depths", default="0,2,3,4", help="Comma-separated depths")
    parser.add_argument("--crits", default="0,1,2,3,4,5", help="Comma-separated min crits")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=0, help="Extraction workers (0=auto)")
    parser.add_argument("--output", default="out/ngram_sweep.json")
    args = parser.parse_args()

    depths = [int(d) for d in args.depths.split(",")]
    crits = [int(c) for c in args.crits.split(",")]
    n_configs = len(depths) * len(crits)
    log.info("sweep: %d depths × %d crits = %d configs", len(depths), len(crits), n_configs)

    # Pin dataset.
    max_id = data.snapshot_max_id(args.db)
    log.info("dataset snapshot: max_id=%d", max_id)

    # Fetch (or incrementally update cache).
    cache = fetch_and_cache(args.db, max_id)

    # Partition. ngram_sweep evaluates against the dev partition (the held-
    # out selection slice); the locked test partition is not touched.
    _, train_ids_labels, dev_ids_labels, _test_ids_labels = data.partition_row_ids(
        args.db, min_malware_training_score=9, max_id=max_id,
    )
    test_ids_labels = dev_ids_labels  # script's "test" pool is dev under new methodology

    # Subsample train for fast iteration.
    rng = np.random.default_rng(args.seed)
    mal = [(r, l) for r, l in train_ids_labels if l == 1]
    ben = [(r, l) for r, l in train_ids_labels if l == 0]
    per_class = args.train_samples // 2
    if len(mal) > per_class:
        mal = [mal[i] for i in rng.choice(len(mal), per_class, replace=False)]
    if len(ben) > per_class:
        ben = [ben[i] for i in rng.choice(len(ben), per_class, replace=False)]
    train_ids_labels = mal + ben

    log.info("preparing reports: %d train, %d test", len(train_ids_labels), len(test_ids_labels))
    train_reports, train_labels = prepare_reports(train_ids_labels, cache)
    test_reports, test_labels = prepare_reports(test_ids_labels, cache)
    log.info("ready: %d train reports, %d test reports", len(train_reports), len(test_reports))

    # Free cache memory — reports are already materialized.
    del cache

    n_workers = args.workers

    # ---------------------------------------------------------------
    # Phase 1: Extract base features ONCE (everything except ngrams).
    # ---------------------------------------------------------------
    log.info("=" * 60)
    log.info("PHASE 1: extracting base features (non-ngram groups)")
    t_base = time.time()
    X_base_train, y_train, base_spec = extract_base_features(
        train_reports, train_labels, n_workers,
    )
    X_base_test, y_test, _ = extract_base_features(
        test_reports, test_labels, n_workers,
    )
    log.info("base features: %d cols, train=%s test=%s (%.1fs)",
             base_spec.total_features, X_base_train.shape, X_base_test.shape,
             time.time() - t_base)

    # ---------------------------------------------------------------
    # Phase 2: Per-config ngram extraction + train + eval.
    # ---------------------------------------------------------------
    log.info("=" * 60)
    log.info("PHASE 2: running %d ngram configs", n_configs)
    results = []
    for depth in depths:
        for crit in crits:
            row = run_config(
                depth, crit,
                X_base_train, y_train,
                X_base_test, y_test,
                base_spec.feature_names,
                train_reports, train_labels,
                test_reports, test_labels,
                args.seed, n_workers,
            )
            results.append(row)

    # Print summary.
    print("\n" + "=" * 120)
    print(f"{'Config':<20} {'nFeat':>7} {'base':>6} {'ngram':>6} {'thresh':>7} "
          f"{'cv_F1':>7} {'tF1':>7} {'tPrec':>7} {'tRec':>7} {'tFP':>5} {'tFN':>5}")
    print("-" * 120)
    for r in sorted(results, key=lambda x: -x["test_f1"]):
        print(f"depth={r['depth']} crit={r['crit']:<10} "
              f"{r['n_features']:>7} {r['n_base_features']:>6} {r['n_ngram_features']:>6} "
              f"{r['threshold']:>7.3f} {r['cv_f1']:>7.4f} "
              f"{r['test_f1']:>7.4f} {r['test_precision']:>7.4f} {r['test_recall']:>7.4f} "
              f"{r['test_fp']:>5} {r['test_fn']:>5}")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()
