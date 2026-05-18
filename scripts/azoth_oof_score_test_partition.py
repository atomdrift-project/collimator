#!/usr/bin/env python3
"""Score test-partition rows with the production general model and merge
into an existing OOF threshold_scores.npz.

The OOF merge (azoth_oof_score.py / stage 3) deliberately excludes
test rows — they have ``oof_fold_of() == None`` so they never match
either fold. That's correct for honest dev calibration, but it leaves
the threshold_scores cache without any test rows, which breaks
``azoth_calibrate_ensemble.py --partition test`` (the second calibrate
call that produces honest test-bucket metrics).

This script scores those test rows in-sample with the production
general model — the production model never trained on test either, so
those scores are honest — and appends them to the cache.

One-shot recovery utility, not part of the normal pipeline. The proper
fix is to roll this into stage 3 itself; until then this script bridges
the gap.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np

_SCRIPTS = Path(__file__).resolve().parent
_SRC = _SCRIPTS.parent / "src"
for p in (str(_SRC), str(_SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

from collimator import data, features  # noqa: E402
from collimator.model import load_model, predict_proba  # noqa: E402

LOG = logging.getLogger("azoth_oof_score_test_partition")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument(
        "--prod-bundle",
        type=Path,
        default=Path("out/models/azoth"),
        help="Production bundle root (contains general/{model.txt|models/,feature_spec.json}).",
    )
    parser.add_argument(
        "--threshold-scores",
        type=Path,
        default=Path("out/models/azoth/general/threshold_scores.npz"),
        help="Existing OOF threshold_scores.npz to append test rows into.",
    )
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Locate the prod general model + spec. Multi-seed bundles use
    # models/seed_*.txt; single-seed uses model.txt. Pick the lowest seed
    # for multi-seed (the seed-search "canonical" choice).
    general_dir = args.prod_bundle / "general"
    spec_path = general_dir / "feature_spec.json"
    if not spec_path.is_file():
        raise SystemExit(f"missing feature_spec at {spec_path}")
    if (general_dir / "model.txt").is_file():
        model_path = general_dir / "model.txt"
    else:
        candidates = sorted((general_dir / "models").glob("seed_*.txt"))
        if not candidates:
            raise SystemExit(
                f"no general model under {general_dir} (looked for model.txt and models/seed_*.txt)",
            )
        model_path = candidates[0]
    LOG.info("prod general: model=%s spec=%s", model_path, spec_path)

    existing = dict(np.load(args.threshold_scores, allow_pickle=True))
    existing_row_ids = set(int(r) for r in existing["row_ids"].tolist())
    LOG.info("existing threshold_scores: %d rows", len(existing_row_ids))

    max_id = int(existing.get(
        "corpus_requested_max_id", existing.get("corpus_max_row_id", 0),
    ) or 0)
    if max_id <= 0:
        max_id = data.snapshot_max_id(args.db)
        LOG.warning("existing cache had no max_id; using live snapshot %d", max_id)

    # Stream the corpus and keep only test rows that aren't already in the
    # cache. The OOF merge writes fold-0 + fold-1 = all train+dev rows,
    # so the missing set is exactly the test partition.
    rows = list(data.stream_labeled_metadata_full(args.db, max_id=max_id))
    kept = [
        r for r in rows
        if data.is_test_sample(str(r[5])) and int(r[0]) not in existing_row_ids
    ]
    LOG.info("found %d test rows to score (of %d total in corpus)", len(kept), len(rows))
    if not kept:
        LOG.info("nothing to do; cache already includes all test rows")
        return 0

    spec = features.FeatureSpec.load(spec_path)
    model = load_model(model_path)

    pred_batches: list[np.ndarray] = []
    label_batches: list[np.ndarray] = []
    sample_buffer: list = []
    for batch_meta, X, y, _stats in features.extract_labeled_metadata_from_db_batches_unordered(
        args.db, kept, spec, n_workers=args.workers,
    ):
        pred_batches.append(predict_proba(model, X))
        label_batches.append(y)
        sample_buffer.extend(batch_meta)
    if not pred_batches:
        raise SystemExit("scored zero rows — extraction failed?")
    test_probs = np.concatenate(pred_batches).astype(np.float32)
    test_labels = np.concatenate(label_batches).astype(np.int8)

    # The 6-tuple shape from stream_labeled_metadata_full is
    # (row_id, sha256, path, score, label, canonical_sha256). The
    # extract_labeled_metadata_from_db_batches_unordered path may emit
    # a 7-tuple (with json_bytes spliced in); honor either.
    canonical_idx = 6 if sample_buffer and len(sample_buffer[0]) >= 7 else 5
    test_part = {
        "row_ids": np.array([s[0] for s in sample_buffer], dtype=np.int64),
        "sha256": np.array([s[1] for s in sample_buffer]),
        "paths": np.array([s[2] for s in sample_buffer]),
        "scores": np.array([s[3] for s in sample_buffer], dtype=np.int32),
        "labels": test_labels,
        "probs": test_probs,
        "canonical_shas": np.array([s[canonical_idx] or s[1] for s in sample_buffer]),
    }
    LOG.info("scored %d test rows", len(test_part["probs"]))

    # Concatenate (existing OOF + test rows), keep sorted by row_id.
    keys = ("row_ids", "sha256", "paths", "scores", "labels", "probs", "canonical_shas")
    combined = {k: np.concatenate([existing[k], test_part[k]]) for k in keys}
    order = np.argsort(combined["row_ids"], kind="mergesort")
    combined = {k: combined[k][order] for k in keys}

    # Preserve the corpus-summary scalars that azoth_calibrate_ensemble
    # reads from the cache (corpus_samples, corpus_malware, etc.).
    for k, v in existing.items():
        if k not in combined:
            combined[k] = v

    np.savez_compressed(args.threshold_scores, **combined)
    LOG.info(
        "wrote %s: %d total rows (%d OOF + %d test)",
        args.threshold_scores, len(combined["row_ids"]),
        len(existing_row_ids), len(test_part["probs"]),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
