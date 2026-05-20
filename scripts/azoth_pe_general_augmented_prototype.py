#!/usr/bin/env python3
"""PE-only prototype: train pe-specialist with general's OOF prob as an
extra feature, compare test recall vs general alone.

If `pe-spec-augmented` test recall > general alone by a meaningful margin
(say ≥2pp at the same FP), the score-augmented-specialist approach is
worth rolling out across all specialists. If not, we save a week of
plumbing.

Inputs (all from the existing pipeline run):
  - score_table.npz: per-row labels + filetype + general+spec probs
  - general OOF threshold_scores.npz: honest general probs per row
  - pe specialist OOF route scores
  - pe specialist matrix cache: existing feature matrix

What we train:
  LightGBM on (existing PE features, general_oof_prob) → label
  Single seed, single fold (use the same fold-A/fold-B split for honesty)

What we evaluate:
  Test partition only. Same recall@0FP comparison as the eval report.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp

_SCRIPTS = Path(__file__).resolve().parent
_SRC = _SCRIPTS.parent / "src"
for p in (str(_SRC), str(_SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

from collimator import data, features  # noqa: E402
from collimator.model import predict_proba  # noqa: E402
from collimator.train import TrainConfig, train  # noqa: E402

LOG = logging.getLogger("pe_augmented_prototype")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument(
        "--general-scores",
        type=Path,
        default=Path("out/models/azoth/general/threshold_scores.npz"),
        help="OOF general probs (one prob per row_id).",
    )
    parser.add_argument(
        "--score-table",
        type=Path,
        default=Path("out/models/azoth/score_table.npz"),
        help="Used to find PE rows and their labels + canonical_sha for partition.",
    )
    parser.add_argument(
        "--general-spec",
        type=Path,
        default=Path("out/models/azoth/general/feature_spec.json"),
        help="Feature spec the PE specialist trains against (shared with general).",
    )
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    LOG.info("loading general OOF probs")
    gscores = np.load(args.general_scores, allow_pickle=True)
    g_row_ids = gscores["row_ids"].astype(np.int64)
    g_probs = gscores["probs"].astype(np.float32)
    g_canonicals = gscores["canonical_shas"].astype(str) if "canonical_shas" in gscores.files else None
    g_labels = gscores["labels"].astype(np.int8)
    g_by_row = {int(rid): float(p) for rid, p in zip(g_row_ids, g_probs)}
    LOG.info("general OOF: %d rows", len(g_row_ids))

    LOG.info("loading score_table to scope to PE")
    st = np.load(args.score_table, allow_pickle=True)
    st_row_ids = st["row_ids"].astype(np.int64)
    st_labels = st["labels"].astype(np.int8)
    st_filetypes = np.asarray([str(v) for v in st["file_types"]])
    pe_mask = st_filetypes == "pe"
    pe_indices = np.flatnonzero(pe_mask)
    LOG.info("PE rows in score_table: %d", len(pe_indices))
    pe_row_ids = st_row_ids[pe_indices].tolist()

    # Partition-split. The score_table doesn't carry canonical_sha256
    # directly; derive partition via the general OOF cache.
    LOG.info("partitioning PE rows by canonical_sha256")
    if g_canonicals is None:
        raise SystemExit("general OOF cache lacks canonical_shas — can't partition")
    g_canon_by_row = {int(rid): str(c) for rid, c in zip(g_row_ids, g_canonicals)}
    train_pe_rows = []  # OOF-train: NOT in test partition, with valid general prob
    test_pe_rows = []
    for rid in pe_row_ids:
        canon = g_canon_by_row.get(rid)
        if canon is None:
            continue
        gp = g_by_row.get(rid)
        if gp is None:
            continue
        if data.is_test_sample(canon):
            test_pe_rows.append((rid, gp))
        else:
            train_pe_rows.append((rid, gp))
    LOG.info(
        "PE rows partitioned: %d train (non-test) / %d test",
        len(train_pe_rows), len(test_pe_rows),
    )

    # Pull labels for train + test rows
    LOG.info("fetching labels via stream_labeled_metadata_full")
    max_id = int(gscores.get("corpus_requested_max_id", gscores.get("corpus_max_row_id", 0)) or 0)
    row_id_set = {rid for rid, _ in train_pe_rows + test_pe_rows}
    label_by_row: dict[int, int] = {}
    for row in data.stream_labeled_metadata_full(args.db, max_id=max_id):
        rid = int(row[0])
        if rid in row_id_set:
            label = int(row[4])  # label index in the 6-tuple is 4 → wait let me check
            label_by_row[rid] = label
        if len(label_by_row) == len(row_id_set):
            break
    LOG.info("got labels for %d / %d rows", len(label_by_row), len(row_id_set))

    spec = features.FeatureSpec.load(args.general_spec)

    # Extract train+test PE features
    LOG.info("extracting PE features (train + test) — this is the slow step")
    train_rows_with_labels = [(rid, label_by_row.get(rid, 0)) for rid, _gp in train_pe_rows]
    test_rows_with_labels = [(rid, label_by_row.get(rid, 0)) for rid, _gp in test_pe_rows]
    t0 = time.perf_counter()
    X_train, y_train, X_test, y_test = features.extract_partitioned_from_db(
        args.db, train_rows_with_labels, test_rows_with_labels, spec, n_workers=args.workers,
    )
    LOG.info(
        "extracted in %.1fs: X_train=%s X_test=%s",
        time.perf_counter() - t0, X_train.shape, X_test.shape,
    )

    # ── Comparison 1: general alone on PE test rows ──
    # Already in g_probs (OOF probs from the run). Just slice to PE-test rows.
    LOG.info("Evaluating general alone on PE test rows...")
    g_test_probs = np.array([g_by_row[rid] for rid, _ in test_pe_rows], dtype=np.float32)
    g_test_labels = np.array([label_by_row.get(rid, 0) for rid, _ in test_pe_rows], dtype=np.int8)
    # Sweep thresholds: find threshold where test_fp == 0 and report recall
    benign = g_test_labels == 0
    malware = g_test_labels == 1
    if benign.sum() == 0:
        raise SystemExit("no PE test benigns; can't evaluate FP@0")
    # 0-FP threshold = max(benign prob) + epsilon
    fp0_thresh = float(g_test_probs[benign].max())
    g_recall_fp0 = float(((g_test_probs > fp0_thresh) & malware).sum() / max(malware.sum(), 1))
    print(f"  general alone @ FP=0 on PE test: recall={g_recall_fp0*100:.2f}%  (thresh > {fp0_thresh:.6f})")

    # ── Comparison 2: train pe-specialist (baseline, no augment) ──
    LOG.info("Training baseline pe-specialist (existing features only)...")
    cfg = TrainConfig(
        learner="azoth", seed=args.seed, n_estimators=400, max_depth=12,
        learning_rate=0.05, early_stopping_rounds=50, num_leaves=96,
        min_child_samples=100, beta=1.25, holdout_fraction=0.0,
        num_threads=128,
    )
    baseline_result = train(
        X_train, y_train, cfg,
        feature_names=spec.feature_names, sample_file_types=["pe"] * len(y_train),
    )
    baseline_test_probs = predict_proba(baseline_result.model, X_test)
    if baseline_test_probs.ndim == 2:
        baseline_test_probs = baseline_test_probs[:, 1]
    fp0_b = float(baseline_test_probs[benign].max())
    b_recall_fp0 = float(((baseline_test_probs > fp0_b) & malware).sum() / max(malware.sum(), 1))
    print(f"  baseline pe-spec @ FP=0 on PE test: recall={b_recall_fp0*100:.2f}%")

    # ── Comparison 3: train pe-specialist with general_prob feature ──
    LOG.info("Building augmented matrices (appending general_prob column)...")
    train_gprobs = np.array([gp for _rid, gp in train_pe_rows], dtype=np.float32)
    test_gprobs = np.array([gp for _rid, gp in test_pe_rows], dtype=np.float32)
    X_train_aug = sp.hstack(
        [X_train, sp.csr_matrix(train_gprobs.reshape(-1, 1))], format="csr",
    )
    X_test_aug = sp.hstack(
        [X_test, sp.csr_matrix(test_gprobs.reshape(-1, 1))], format="csr",
    )
    aug_feature_names = list(spec.feature_names) + ["meta:general_prob"]
    LOG.info("augmented X_train shape: %s", X_train_aug.shape)

    LOG.info("Training augmented pe-specialist...")
    aug_result = train(
        X_train_aug, y_train, cfg,
        feature_names=aug_feature_names, sample_file_types=["pe"] * len(y_train),
    )
    aug_test_probs = predict_proba(aug_result.model, X_test_aug)
    if aug_test_probs.ndim == 2:
        aug_test_probs = aug_test_probs[:, 1]
    fp0_a = float(aug_test_probs[benign].max())
    a_recall_fp0 = float(((aug_test_probs > fp0_a) & malware).sum() / max(malware.sum(), 1))
    print(f"  AUGMENTED pe-spec @ FP=0 on PE test: recall={a_recall_fp0*100:.2f}%")

    # Summary
    print()
    print("=== SUMMARY (PE filetype, test partition, FP=0) ===")
    print(f"  general alone:        {g_recall_fp0*100:6.2f}%")
    print(f"  pe-spec (baseline):   {b_recall_fp0*100:6.2f}%   Δ vs general: {(b_recall_fp0-g_recall_fp0)*100:+.2f}pp")
    print(f"  pe-spec (augmented):  {a_recall_fp0*100:6.2f}%   Δ vs general: {(a_recall_fp0-g_recall_fp0)*100:+.2f}pp   Δ vs baseline: {(a_recall_fp0-b_recall_fp0)*100:+.2f}pp")
    print()
    # Also report 3-FP for the more practical operating point
    benign_probs = aug_test_probs[benign]
    benign_probs_sorted = np.sort(benign_probs)[::-1]
    if len(benign_probs_sorted) >= 4:
        fp3_thresh = float(benign_probs_sorted[3])
        a_recall_fp3 = float(((aug_test_probs > fp3_thresh) & malware).sum() / max(malware.sum(), 1))
        b_benign_sorted = np.sort(baseline_test_probs[benign])[::-1]
        b_fp3 = float(b_benign_sorted[3])
        b_recall_fp3 = float(((baseline_test_probs > b_fp3) & malware).sum() / max(malware.sum(), 1))
        g_benign_sorted = np.sort(g_test_probs[benign])[::-1]
        g_fp3 = float(g_benign_sorted[3])
        g_recall_fp3 = float(((g_test_probs > g_fp3) & malware).sum() / max(malware.sum(), 1))
        print(f"=== FP=3 comparison ===")
        print(f"  general:    {g_recall_fp3*100:6.2f}%")
        print(f"  baseline:   {b_recall_fp3*100:6.2f}%")
        print(f"  augmented:  {a_recall_fp3*100:6.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
