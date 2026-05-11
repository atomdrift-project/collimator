"""Combine k=2 fold-trained general models into an OOF score table.

Publication-grade calibration uses out-of-fold predictions covering all of
train+dev so the calibration sample is N_b ≈ 2.4M benigns instead of the
single-pass dev-only ~150k. This pushes the Clopper-Pearson floor on the
deployment FP/M from ~20 down to ~1.25, making strict L levels (L0–L3)
statistically resolvable for the first time.

This script consumes two general-model bundles trained on disjoint halves
of train+dev (per ``data.oof_fold_of``) and produces a combined
``general/threshold_scores.npz`` whose probabilities are honest OOF — every
row's probability comes from a model that didn't see that row during
training. The output drops into ``--output`` so the standard calibrate
script can ingest it via ``--general-scores`` without further changes.

The fold-A model trains on rows where ``oof_fold_of != 0`` (so it predicts
on fold-0 rows OOF). The fold-B model trains on rows where ``oof_fold_of
!= 1``. Test partition rows have ``oof_fold_of == None`` and are never
involved in OOF — they stay locked for headline reporting.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Any

import numpy as np

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import data, features  # noqa: E402
from collimator.model import load_model, predict_proba  # noqa: E402

LOG = logging.getLogger("azoth_oof_score")


def _score_partition(
    db_path: str,
    model_path: Path,
    spec_path: Path,
    *,
    oof_fold: int,
    workers: int,
    max_id: int,
) -> dict[str, Any]:
    """Score the model on rows whose oof_fold_of(canonical) == oof_fold.

    Returns a dict with row_ids, sha256, paths, scores, labels, probs,
    canonical_shas — the same shape ``thresholds_refresh`` writes for the
    threshold-score cache. ``oof_fold`` here is the fold being predicted
    (held out from this model's training).
    """
    LOG.info("scoring %s on OOF fold %d", model_path, oof_fold)
    spec = features.FeatureSpec.load(spec_path)
    model = load_model(model_path)
    rows = list(
        data.stream_labeled_metadata_full(
            db_path,
            max_id=max_id,
        ),
    )
    # Filter to rows in this OOF fold (excluding test).
    kept_rows = []
    for row in rows:
        canonical = row[5]
        if data.oof_fold_of(canonical) == oof_fold:
            kept_rows.append(row)
    LOG.info(
        "fold %d: %d of %d rows match (%.1f%%)",
        oof_fold, len(kept_rows), len(rows), 100.0 * len(kept_rows) / max(len(rows), 1),
    )
    if not kept_rows:
        raise SystemExit(f"no rows in OOF fold {oof_fold}")

    # Extract features + score, in the standard batched-by-worker pattern.
    row_metadata = kept_rows
    pred_batches: list[np.ndarray] = []
    label_batches: list[np.ndarray] = []
    sample_buffer: list[Any] = []
    for batch_meta, X, y, _stats in features.extract_labeled_metadata_from_db_batches_unordered(
        db_path,
        row_metadata,
        spec,
        n_workers=workers,
    ):
        pred_batches.append(predict_proba(model, X))
        label_batches.append(y)
        sample_buffer.extend(batch_meta)
    probs = np.concatenate(pred_batches).astype(np.float32) if pred_batches else np.array([], dtype=np.float32)
    labels = np.concatenate(label_batches).astype(np.int8) if label_batches else np.array([], dtype=np.int8)
    LOG.info("scored %d rows for fold %d", len(probs), oof_fold)
    return {
        "row_ids": np.array([s.row_id for s in sample_buffer], dtype=np.int64),
        "sha256": np.array([s.sha256 for s in sample_buffer]),
        "paths": np.array([s.path for s in sample_buffer]),
        "scores": np.array([s.score for s in sample_buffer], dtype=np.int32),
        "labels": labels,
        "probs": probs,
        "canonical_shas": np.array([s.canonical_sha256 or s.sha256 for s in sample_buffer]),
    }


def _combine(part_a: dict[str, Any], part_b: dict[str, Any]) -> dict[str, Any]:
    """Concatenate the two fold partitions in row_id order."""
    keys = ("row_ids", "sha256", "paths", "scores", "labels", "probs", "canonical_shas")
    combined = {k: np.concatenate([part_a[k], part_b[k]]) for k in keys}
    order = np.argsort(combined["row_ids"], kind="mergesort")
    return {k: combined[k][order] for k in keys}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="Hopper DSN")
    parser.add_argument(
        "--fold-a-bundle",
        type=Path,
        required=True,
        help="Path to the bundle trained with EXP_OOF_FOLD_EXCLUDE=0 "
        "(model didn't see fold-0 rows during training; predicts on them OOF)",
    )
    parser.add_argument(
        "--fold-b-bundle",
        type=Path,
        required=True,
        help="Path to the bundle trained with EXP_OOF_FOLD_EXCLUDE=1 "
        "(predicts on fold-1 rows OOF)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Where to write the combined OOF threshold_scores.npz",
    )
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--max-id", type=int, default=0)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    fold_a_general = args.fold_a_bundle / "general"
    fold_b_general = args.fold_b_bundle / "general"

    def _model_and_spec(general_dir: Path) -> tuple[Path, Path]:
        spec = general_dir / "feature_spec.json"
        # Multi-seed bundles ship models/ instead of model.txt. Pick seed_42 by
        # convention; if absent, fall back to the lowest-numbered seed file
        # (matches the same logic used by the deploy chain's promote step).
        if (general_dir / "model.txt").exists():
            return general_dir / "model.txt", spec
        candidates = sorted((general_dir / "models").glob("seed_*.txt"))
        if not candidates:
            raise SystemExit(f"no general model.txt or models/seed_*.txt under {general_dir}")
        return candidates[0], spec

    fold_a_model, fold_a_spec = _model_and_spec(fold_a_general)
    fold_b_model, fold_b_spec = _model_and_spec(fold_b_general)

    # Score fold A on rows where oof_fold == 0 (held out from A's training).
    part_a = _score_partition(
        args.db, fold_a_model, fold_a_spec,
        oof_fold=0, workers=args.workers, max_id=args.max_id,
    )
    # Score fold B on rows where oof_fold == 1.
    part_b = _score_partition(
        args.db, fold_b_model, fold_b_spec,
        oof_fold=1, workers=args.workers, max_id=args.max_id,
    )
    combined = _combine(part_a, part_b)

    n_total = len(combined["labels"])
    n_mal = int(np.sum(combined["labels"] == 1))
    n_ben = int(np.sum(combined["labels"] == 0))
    max_row_id = int(np.max(combined["row_ids"])) if n_total else 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        args.output,
        row_ids=combined["row_ids"],
        sha256=combined["sha256"],
        paths=combined["paths"],
        scores=combined["scores"],
        labels=combined["labels"],
        probs=combined["probs"],
        canonical_shas=combined["canonical_shas"],
        corpus_samples=np.array(n_total, dtype=np.int64),
        corpus_malware=np.array(n_mal, dtype=np.int64),
        corpus_benign=np.array(n_ben, dtype=np.int64),
        corpus_max_row_id=np.array(max_row_id, dtype=np.int64),
        corpus_requested_max_id=np.array(int(args.max_id), dtype=np.int64),
    )
    LOG.info(
        "wrote OOF threshold_scores to %s: %d rows (%d malware, %d benign)",
        args.output, n_total, n_mal, n_ben,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
