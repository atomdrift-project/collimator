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
    oof_fold: int | None,
    workers: int,
    max_id: int,
) -> dict[str, Any]:
    """Score the model on rows whose oof_fold_of(canonical) == oof_fold.

    Returns a dict with row_ids, sha256, paths, scores, labels, probs,
    canonical_shas — the same shape ``thresholds_refresh`` writes for the
    threshold-score cache. ``oof_fold`` here is the fold being predicted
    (held out from this model's training).

    ``oof_fold=None`` is the special "test partition" mode: score rows
    where ``oof_fold_of`` returns None (i.e. ``is_test_sample``).
    Used to fold prod-general predictions on test rows into the OOF
    cache so the downstream ``--partition test`` calibrate has data
    to work with. Without this, the OOF cache covers only train+dev
    and the test-partition calibrate dies with "no rows".
    """
    label = "test" if oof_fold is None else f"OOF fold {oof_fold}"
    LOG.info("scoring %s on %s", model_path, label)
    spec = features.FeatureSpec.load(spec_path)
    model = load_model(model_path)
    rows = list(
        data.stream_labeled_metadata_full(
            db_path,
            max_id=max_id,
        ),
    )
    # Filter to rows in this OOF fold (or test partition when fold is None).
    kept_rows = []
    for row in rows:
        canonical = row[5]
        if data.oof_fold_of(canonical) == oof_fold:
            kept_rows.append(row)
    LOG.info(
        "%s: %d of %d rows match (%.1f%%)",
        label, len(kept_rows), len(rows), 100.0 * len(kept_rows) / max(len(rows), 1),
    )
    if not kept_rows:
        raise SystemExit(f"no rows in {label}")

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
    # LabeledMetadata is currently a plain tuple type alias (see
    # src/collimator/features.py:107). The 6-tuple shape from
    # stream_labeled_metadata_full is:
    #   (row_id, sha256, path, score, label, canonical_sha256)
    # The 7-tuple shape from stream_labeled_metadata_full_with_size adds
    # json_bytes at index 5 and moves canonical_sha256 to index 6 (see
    # the comment in extract_labeled_metadata_from_db_batches_unordered).
    # This script feeds the 6-tuple form, so index 5 is canonical_sha256.
    sample_count = len(sample_buffer)
    canonical_idx = 6 if sample_count > 0 and len(sample_buffer[0]) >= 7 else 5
    return {
        "row_ids": np.array([s[0] for s in sample_buffer], dtype=np.int64),
        "sha256": np.array([s[1] for s in sample_buffer]),
        "paths": np.array([s[2] for s in sample_buffer]),
        "scores": np.array([s[3] for s in sample_buffer], dtype=np.int32),
        "labels": labels,
        "probs": probs,
        "canonical_shas": np.array(
            [s[canonical_idx] or s[1] for s in sample_buffer]
        ),
    }


def _combine(*parts: dict[str, Any]) -> dict[str, Any]:
    """Concatenate fold partitions in row_id order. Accepts 2+ parts."""
    keys = ("row_ids", "sha256", "paths", "scores", "labels", "probs", "canonical_shas")
    nonempty = [p for p in parts if len(p["row_ids"]) > 0]
    if not nonempty:
        return {k: np.array([]) for k in keys}
    combined = {k: np.concatenate([p[k] for p in nonempty]) for k in keys}
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
        "--prod-bundle",
        type=Path,
        default=None,
        help=(
            "Optional path to the production bundle. When provided, the "
            "script ALSO scores test-partition rows with the prod general "
            "(test rows have oof_fold_of()==None and are excluded from "
            "both fold-A and fold-B's coverage). Without this, the output "
            "covers only train+dev and the downstream --partition test "
            "calibrate dies with 'no rows in partition'."
        ),
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

    # Sanity: a cache collision in the experiment runner historically copied
    # the production general bundle into BOTH fold-a/ and fold-b/. Both
    # bundles would then produce identical OOF predictions (in-sample on the
    # whole train+dev set), silently corrupting downstream calibration.
    # Hash the primary model bytes and abort if they match — catches the
    # collision before we sink an hour of feature extraction into bad data.
    import hashlib  # noqa: PLC0415
    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    fold_a_hash = _sha256(fold_a_model)
    fold_b_hash = _sha256(fold_b_model)
    if fold_a_hash == fold_b_hash:
        raise SystemExit(
            f"fold-A model {fold_a_model} and fold-B model {fold_b_model} "
            f"are identical (sha256={fold_a_hash[:16]}…). This typically means "
            "the experiment cache collided across folds and both bundles got "
            "the production model. Clear out/cache/experiment/azoth/ and the "
            "fold roots, then re-run the OOF pipeline.",
        )
    LOG.info(
        "fold-A model %s (%s), fold-B model %s (%s) — distinct, proceeding",
        fold_a_model, fold_a_hash[:8], fold_b_model, fold_b_hash[:8],
    )

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
    parts = [part_a, part_b]

    # Test-partition rows: oof_fold_of(canon)==None. Score them with the
    # prod general (which never trained on test either, so the scores are
    # honest). Without this the OOF cache lacks test rows and downstream
    # calibrate --partition test fails with "no rows".
    if args.prod_bundle is not None:
        prod_model, prod_spec = _model_and_spec(args.prod_bundle / "general")
        part_test = _score_partition(
            args.db, prod_model, prod_spec,
            oof_fold=None, workers=args.workers, max_id=args.max_id,
        )
        parts.append(part_test)
    else:
        LOG.warning(
            "no --prod-bundle provided; test-partition rows will NOT be in "
            "the output. Downstream --partition test calibrate will fail.",
        )
    combined = _combine(*parts)

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
