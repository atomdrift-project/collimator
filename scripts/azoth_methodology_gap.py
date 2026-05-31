"""One-off sanity check: quantify the methodology gap on the existing model.

Compares headline metrics under three views of the same trained model and
score cache:

  full      — all labeled rows (status quo: leaky calibration, leaky test)
  dev       — only the dev partition (~12.5% of corpus)
  test      — only the locked test partition (~12.5% of corpus, never trained on)

For each view we report F1, precision, recall, AUC, PR AUC, Brier, and
recall@FP/100M = {0,50,100,300,500,900} at the model's threshold (0.5 by
default, since this script doesn't rerun threshold search). The
dev-vs-test gap is the generalization-honest signal; the full-vs-test
gap is the leakage signal.

Outputs a markdown table to stdout and a JSON file to ``--output``.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from collimator import data
from collimator.stats import bootstrap_metric

LOG = logging.getLogger(__name__)


def _fetch_canonical_map(db_path: str, row_ids: np.ndarray) -> dict[int, str]:
    """Pull canonical_sha256 for the given row_ids in one batch."""
    ids = [int(x) for x in row_ids]
    if not ids:
        return {}
    chunk = 50_000
    out: dict[int, str] = {}
    for i in range(0, len(ids), chunk):
        batch = ids[i : i + chunk]
        with data._connect(db_path) as conn:  # noqa: SLF001
            if data._is_pg(db_path):  # noqa: SLF001
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, sha256, canonical_sha256 FROM samples WHERE id = ANY(%s)",
                        [batch],
                    )
                    for rid, sha, canonical in cur:
                        out[int(rid)] = (canonical or sha or "")
            else:
                placeholders = ",".join("?" for _ in batch)
                for rid, sha, canonical in conn.execute(
                    f"SELECT id, sha256, canonical_sha256 FROM samples WHERE id IN ({placeholders})",  # noqa: S608
                    batch,
                ):
                    out[int(rid)] = (canonical or sha or "")
    return out


def _recall_at_per_100M(y_true: np.ndarray, y_prob: np.ndarray, target: float) -> float:
    """Recall@target FP/100M on a held-out array. Returns 0 if no benign rows.

    ``target`` is in per-100M units (e.g. 50 == L50 == 0.5 FP/M).
    """
    benign = y_true == 0
    n_benign = int(np.sum(benign))
    if n_benign == 0:
        return 0.0
    fp_budget = max(0, int(np.floor(n_benign * target / 100_000_000.0)))
    benign_probs = np.sort(y_prob[benign])[::-1]
    if fp_budget >= len(benign_probs):
        threshold = 0.0
    elif fp_budget == 0:
        threshold = float(benign_probs[0]) + 1e-9
    else:
        threshold = float(benign_probs[fp_budget - 1])
    flagged = y_prob >= threshold
    tp = int(np.sum(flagged & (y_true == 1)))
    n_malware = int(np.sum(y_true == 1))
    return tp / n_malware if n_malware else 0.0


def _metrics_for_view(y_true: np.ndarray, y_prob: np.ndarray, threshold: float, *, with_ci: bool) -> dict:
    if len(y_true) == 0:
        return {"n_rows": 0}
    y_pred = (y_prob >= threshold).astype(int)
    multi_class = len(np.unique(y_true)) > 1
    out: dict[str, object] = {
        "n_rows": int(len(y_true)),
        "n_malware": int(np.sum(y_true == 1)),
        "n_benign": int(np.sum(y_true == 0)),
        "threshold": threshold,
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)) if multi_class else 0.0,
        "pr_auc": float(average_precision_score(y_true, y_prob)) if multi_class else 0.0,
        "brier": float(brier_score_loss(y_true, y_prob)) if multi_class else 0.0,
    }
    for target in (0.0, 50.0, 100.0, 300.0, 500.0, 900.0):
        out[f"recall_at_{int(target)}_per_100M"] = _recall_at_per_100M(y_true, y_prob, target)
    if with_ci and multi_class:
        for metric_name, metric_fn in (
            ("f1", lambda yt, yp: float(f1_score(yt, (yp >= threshold).astype(int), zero_division=0))),
            ("roc_auc", lambda yt, yp: float(roc_auc_score(yt, yp)) if len(np.unique(yt)) > 1 else 0.0),
            ("recall_at_50_per_100M", lambda yt, yp: _recall_at_per_100M(yt, yp, 50.0)),
        ):
            ci = bootstrap_metric(y_true, y_prob, metric_fn, n_resamples=200, seed=42)
            out[f"{metric_name}_ci"] = {"low": ci["low"], "high": ci["high"]}
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="Hopper DSN")
    parser.add_argument("--scores", type=Path, required=True, help="Path to threshold_scores.npz")
    parser.add_argument("--threshold", type=float, default=0.5, help="Decision threshold to apply (default 0.5)")
    parser.add_argument("--output", type=Path, default=Path("out/methodology_gap.json"))
    parser.add_argument("--no-ci", action="store_true", help="Skip bootstrap CIs (faster)")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level.upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    LOG.info("loading score cache: %s", args.scores)
    arrs = np.load(args.scores, allow_pickle=False)
    row_ids = arrs["row_ids"].astype(np.int64)
    labels = arrs["labels"].astype(np.int64)
    probs = arrs["probs"].astype(np.float32)
    LOG.info("cache: %d rows (%d malware, %d benign)", len(labels), int(np.sum(labels == 1)), int(np.sum(labels == 0)))

    LOG.info("fetching canonical_sha256 for %d rows from hopper", len(row_ids))
    canonical_map = _fetch_canonical_map(args.db, row_ids)
    canonical = np.array(
        [canonical_map.get(int(rid), "") for rid in row_ids],
        dtype=object,
    )
    missing = int(np.sum(canonical == ""))
    if missing:
        LOG.warning("missing canonical_sha256 for %d rows; treating those as 'train'", missing)

    partitions = np.array([data.partition_of(c or "ff") for c in canonical], dtype=object)
    masks = {
        "full": np.ones(len(labels), dtype=bool),
        "train": partitions == "train",
        "dev": partitions == "dev",
        "test": partitions == "test",
    }
    with_ci = not args.no_ci
    results = {}
    for view, mask in masks.items():
        LOG.info("computing metrics for view=%s (n=%d, with_ci=%s)", view, int(np.sum(mask)), with_ci)
        results[view] = _metrics_for_view(labels[mask], probs[mask], args.threshold, with_ci=with_ci)

    print()
    print("# Methodology Gap Comparison")
    print()
    print(f"- Score cache: {args.scores}")
    print(f"- Decision threshold: {args.threshold}")
    print()
    print("| View | Rows | Malware | Benign | F1 | Precision | Recall | ROC AUC | PR AUC | Brier |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for view in ("full", "train", "dev", "test"):
        m = results[view]
        if m.get("n_rows", 0) == 0:
            print(f"| {view} | 0 | 0 | 0 | - | - | - | - | - | - |")
            continue
        print(
            f"| {view} | {m['n_rows']} | {m['n_malware']} | {m['n_benign']} | "
            f"{m['f1']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | "
            f"{m['roc_auc']:.4f} | {m['pr_auc']:.4f} | {m['brier']:.4f} |",
        )
    print()
    print("| View | recall@L0 | recall@L50 | recall@L100 | recall@L300 | recall@L500 | recall@L900 |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for view in ("full", "train", "dev", "test"):
        m = results[view]
        if m.get("n_rows", 0) == 0:
            continue
        print(
            f"| {view} | "
            f"{m['recall_at_0_per_100M']:.4f} | "
            f"{m['recall_at_50_per_100M']:.4f} | "
            f"{m['recall_at_100_per_100M']:.4f} | "
            f"{m['recall_at_300_per_100M']:.4f} | "
            f"{m['recall_at_500_per_100M']:.4f} | "
            f"{m['recall_at_900_per_100M']:.4f} |",
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2))
    LOG.info("wrote results to %s", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
