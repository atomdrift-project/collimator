"""CLI entry point for collimator training pipeline."""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from . import ablation, benchmark, data, demo, experiment, explain, export, features, inspect, thresholds, train, traits
from .model import detect_device

log = logging.getLogger(__name__)


def _db_dsn(raw: str) -> Path | str:
    """Return *raw* as-is for postgres:// DSNs, or as a Path for SQLite files."""
    if raw.startswith(("postgres://", "postgresql://")):
        return raw
    return Path(raw)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-5s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _git_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def _parse_filetype_weights(entries: list[str] | None) -> dict[str, float]:
    weights: dict[str, float] = {}
    for entry in entries or []:
        if "=" not in entry:
            raise ValueError(f"invalid benign filetype weight '{entry}', expected filetype=weight")
        file_type, raw_weight = entry.split("=", 1)
        file_type = file_type.strip()
        if not file_type:
            raise ValueError(f"invalid benign filetype weight '{entry}', empty file type")
        weight = float(raw_weight)
        weights[file_type] = weight
    return weights


def _print_test_block(
    probs: np.ndarray,
    y: np.ndarray,
    threshold: float,
) -> None:
    """Print test-set metrics at the calibrated holdout threshold."""
    from sklearn.metrics import (
        average_precision_score,
        brier_score_loss,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )
    from .train import _calibration_summary

    n_malware = int(np.sum(y == 1))
    n_benign = int(np.sum(y == 0))
    y_pred = (probs >= threshold).astype(int)
    tp = int(np.sum((y_pred == 1) & (y == 1)))
    fp = int(np.sum((y_pred == 1) & (y == 0)))
    fn = int(np.sum((y_pred == 0) & (y == 1)))
    tn = int(np.sum((y_pred == 0) & (y == 0)))

    print(f"{'─' * 20} Test Set {'─' * 25}")
    print(f"  n={len(y)} ({n_malware} malware, {n_benign} benign)  threshold={threshold:.3f}")
    if len(np.unique(y)) > 1:
        calib = _calibration_summary(y, probs)
        print(
            f"  ROC AUC  {roc_auc_score(y, probs):.4f}   Avg Prec  {average_precision_score(y, probs):.4f}"
            f"   Brier  {brier_score_loss(y, probs):.4f}   ECE  {float(calib['ece']):.4f}"
        )
        print(
            f"  F1  {f1_score(y, y_pred, zero_division=0):.4f}"
            f"   Precision  {precision_score(y, y_pred, zero_division=0):.4f}"
            f"   Recall  {recall_score(y, y_pred, zero_division=0):.4f}"
        )
    if n_malware:
        print(f"  TP {tp:5d} / {n_malware}  ({tp / n_malware:.2%})    FN {fn:5d} / {n_malware}  ({fn / n_malware:.2%})")
    if n_benign:
        print(f"  TN {tn:5d} / {n_benign}  ({tn / n_benign:.2%})    FP {fp:5d} / {n_benign}  ({fp / n_benign:.2%})")
    print(f"{'=' * 54}")


def cmd_train(args: argparse.Namespace) -> None:
    """Train a model and export to ONNX."""
    t0 = time.time()
    db_path = _db_dsn(args.db)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    effective_workers = features.resolve_worker_count(args.workers)
    if args.workers <= 0:
        log.info("auto workers: using %d worker processes", effective_workers)
    else:
        log.info("using %d worker processes", effective_workers)
    log.info("xgboost requested device: auto")
    log.info("xgboost effective device probe: %s", detect_device())

    # Pin the dataset to a single max(id) snapshot so concurrent inserts to the
    # hopper DB don't cause drift mid-run.
    pinned_max_id = data.snapshot_max_id(db_path)
    log.info("dataset snapshot: max_id=%d", pinned_max_id)

    # Partition samples into train/test using canonical_sha256.
    # Exploded archive members are included as regular rows (filtered by skip='').
    train_row_ids, train_ids_labels, test_ids_labels = data.partition_row_ids(
        db_path,
        min_malware_training_score=args.min_malware_score,
        max_id=pinned_max_id,
    )

    log.info("pass 1: building vocabulary from %s", db_path)
    spec = features.build_vocab_from_db(
        db_path,
        train_ids_labels,
        n_workers=args.workers,
    )

    log.info("pass 2: extracting training and test features")
    X, y, X_test, y_test = features.extract_partitioned_from_db(
        db_path,
        train_ids_labels,
        test_ids_labels,
        spec,
        n_workers=args.workers,
    )
    if X.shape[0] < 10:
        print(f"ERROR: only {X.shape[0]} training samples, need at least 10")
        sys.exit(1)

    # Train.
    config = train.TrainConfig(
        seed=args.seed,
        **({"n_estimators": args.n_estimators} if args.n_estimators is not None else {}),
        **({"max_depth": args.max_depth} if args.max_depth is not None else {}),
        **({"learning_rate": args.learning_rate} if args.learning_rate is not None else {}),
        **({"early_stopping_rounds": args.early_stopping_rounds} if args.early_stopping_rounds is not None else {}),
        **({"beta": args.beta} if args.beta is not None else {}),
        threshold_mode=args.threshold_mode,
        threshold_fpr_target=args.threshold_fpr_target,
        hard_negative_fraction=args.hard_negative_fraction,
        hard_negative_weight=args.hard_negative_weight,
    )
    result = train.train(X, y, config, feature_names=spec.feature_names)

    # Attach standardization params to spec before saving.
    spec.feature_means = result.feature_means
    spec.feature_stds = result.feature_stds

    # Export.
    spec.save(out_dir / "feature_spec.json")
    export.export_onnx(result.model, spec.total_features, out_dir / "model.onnx")
    export.save_model(result.model, out_dir / "model.json")

    # Fast in-run estimate from out-of-fold CV predictions. Run
    # `make thresholds-refresh` after training to compute deploy thresholds
    # against the full labeled good corpus, including low-score good rows.
    recommended = thresholds.compute_default_recommendations(result.cv_predictions, result.cv_labels) \
        if len(result.cv_predictions) > 0 else {}
    severity_levels = thresholds.compute_severity_levels(result.cv_predictions, result.cv_labels) \
        if len(result.cv_predictions) > 0 else []

    export.save_evaluation(
        metrics=result.metrics,
        calibration=result.calibration,
        optimal_threshold=result.optimal_threshold,
        confusion=result.confusion,
        class_distribution=result.class_distribution,
        split_summary=result.split_summary,
        fold_metrics=result.fold_metrics,
        n_features=spec.total_features,
        model_abi_version=spec.abi_version,
        recommended_thresholds=recommended if recommended else None,
        severity_levels=severity_levels if severity_levels else None,
        severity_level_targets=thresholds.SEVERITY_LEVEL_TARGETS,
        experiment={
            "model_abi_version": spec.abi_version,
            "seed": config.seed,
            "feature_spec_version": spec.version,
            "workers_requested": args.workers,
            "workers_effective": effective_workers,
            "git_sha": _git_sha(),
            "train_config": {
                "n_folds": config.n_folds,
                "n_estimators": config.n_estimators,
                "max_depth": config.max_depth,
                "learning_rate": config.learning_rate,
                "holdout_fraction": config.holdout_fraction,
                "early_stopping_rounds": config.early_stopping_rounds,
                "min_child_weight": config.min_child_weight,
                "colsample_bytree": config.colsample_bytree,
                "subsample": config.subsample,
                "gamma": config.gamma,
                "reg_alpha": config.reg_alpha,
                "reg_lambda": config.reg_lambda,
                "threshold_mode": config.threshold_mode,
                "threshold_fpr_target": config.threshold_fpr_target,
                "hard_negative_fraction": config.hard_negative_fraction,
                "hard_negative_weight": config.hard_negative_weight,
            },
        },
        output_path=out_dir / "evaluation.json",
    )
    export.save_run_summary(
        kind="train",
        payload={
            "db_path": str(db_path),
            "output_dir": str(out_dir),
            "metrics": result.metrics,
            "calibration": result.calibration,
            "optimal_threshold": result.optimal_threshold,
            "confusion_matrix": result.confusion,
            "class_distribution": result.class_distribution,
            "split_summary": result.split_summary,
            "fold_metrics": result.fold_metrics,
            "n_features": spec.total_features,
            "seed": config.seed,
            "feature_spec_version": spec.version,
            "workers_requested": args.workers,
            "workers_effective": effective_workers,
            "git_sha": _git_sha(),
        },
        output_dir=out_dir,
    )

    # Post-training steps only need small dense subsets — avoid densifying
    # the full sparse matrix to keep memory low.
    rng = np.random.default_rng(42)

    def _dense_subset(n: int) -> np.ndarray:
        idx = rng.choice(X.shape[0], min(n, X.shape[0]), replace=False)
        return X[idx].toarray()

    # Test set metrics at the calibrated threshold — print immediately after
    # the holdout block so both are visible together for experiment comparison.
    test_probs: np.ndarray | None = None
    if X_test.shape[0] > 0:
        from .model import predict_proba
        test_probs_raw = predict_proba(result.model, X_test)
        # Apply the same isotonic calibrator used for the holdout evaluation.
        if result.isotonic_calibrator is not None:
            test_probs = result.isotonic_calibrator.predict(test_probs_raw)
        else:
            test_probs = test_probs_raw
        _print_test_block(test_probs, y_test, result.optimal_threshold)

    # Save CV predictions + test predictions for threshold recomputation
    # without retraining. ~2MB compressed for 180K samples.
    if len(result.cv_predictions) > 0:
        cv_data = {"cv_predictions": result.cv_predictions, "cv_labels": result.cv_labels}
        if test_probs is not None:
            cv_data["test_predictions"] = test_probs
            cv_data["test_labels"] = y_test
        np.savez_compressed(out_dir / "cv_predictions.npz", **cv_data)
        log.info("saved CV predictions to %s", out_dir / "cv_predictions.npz")

    # Validate ONNX (100 samples).
    if not export.validate_onnx(
        result.model, out_dir / "model.onnx", spec.total_features,
        X=_dense_subset(100),
    ):
        print("WARNING: ONNX validation failed")
        sys.exit(1)

    # SHAP analysis (200 samples).
    explain.compute_shap_importance(
        result.model, _dense_subset(200), spec,
        output_path=out_dir / "shap_importance.json",
    )

    # Cross-language test fixtures (50 samples).
    fix_idx = rng.choice(X.shape[0], min(50, X.shape[0]), replace=False)
    fix_idx.sort()
    X_fix = X[fix_idx].toarray()
    generate_fixtures(result.model, spec, X_fix, X_fix, out_dir,
                      optimal_threshold=result.optimal_threshold)

    # Feature-extraction parity fixture: diverse samples covering all
    # file types, score ranges, multi-file archives, and label classes.
    extraction_reports = _gather_diverse_fixture_reports(db_path)
    if extraction_reports:
        generate_extraction_fixture(
            extraction_reports, spec, out_dir,
            n_samples=len(extraction_reports),
            model=result.model, optimal_threshold=result.optimal_threshold,
            recommended_thresholds=recommended,
        )

    # Operating-point table on the test set (skip the large accuracy tables).
    if test_probs is not None:
        thresholds.print_recommendations(
            test_probs, y_test,
            title="TEST SET OPERATING POINTS (held-out)",
            highlight_threshold=result.optimal_threshold,
        )
    else:
        print("\nNo test samples — skipping operating-point table.")

    # Combined CV + test operating points: honest predictions over the full DB
    # for higher-confidence FPR measurement (especially for tight FPR targets).
    if test_probs is not None and len(result.cv_predictions) > 0:
        all_probs = np.concatenate([result.cv_predictions, test_probs])
        all_labels = np.concatenate([result.cv_labels, y_test])
        thresholds.print_recommendations(
            all_probs, all_labels,
            title="FULL DB OPERATING POINTS (CV + held-out)",
            highlight_threshold=result.optimal_threshold,
        )

    elapsed = time.time() - t0
    mins, secs = divmod(int(elapsed), 60)

    print(f"\nOutput files in {out_dir}/:")
    for f in sorted(out_dir.iterdir()):
        if f.is_file():
            print(f"  {f.name}")
    print(f"\nTotal time: {mins}m {secs:02d}s")


def cmd_evaluate(args: argparse.Namespace) -> None:
    """Evaluate an existing model against a database."""
    db_path = _db_dsn(args.db)
    spec_path = Path(args.spec)
    model_path = Path(args.model)

    spec = features.FeatureSpec.load(spec_path)

    try:
        import onnxruntime as ort
    except ImportError:
        print("ERROR: onnxruntime required for evaluation")
        sys.exit(1)

    session = ort.InferenceSession(str(model_path))
    batch_size = 1024
    reports_batch: list[dict[str, object]] = []
    labels_batch: list[int] = []
    pred_batches: list[np.ndarray] = []
    y_batches: list[np.ndarray] = []

    def _score_batch() -> None:
        if not reports_batch:
            return
        X_batch, y_batch = features.extract_all(reports_batch, labels_batch, spec)
        if spec.standardized:
            X_input = features.standardize(X_batch, spec)
        else:
            X_input = X_batch.toarray() if hasattr(X_batch, "toarray") else X_batch
        pred_batches.append(export.predict_onnx_proba(session, X_input))
        y_batches.append(y_batch)
        reports_batch.clear()
        labels_batch.clear()

    for sample in data.stream_samples(db_path):
        reports_batch.append(sample.report)
        labels_batch.append(sample.label)
        if len(reports_batch) >= batch_size:
            _score_batch()
    _score_batch()

    predictions = np.concatenate(pred_batches) if pred_batches else np.array([], dtype=np.float32)
    y = np.concatenate(y_batches) if y_batches else np.array([], dtype=np.float32)
    if len(y) == 0:
        print("No samples found")
        return

    # Use optimal threshold from training if available.
    threshold = 0.5
    if args.eval_json:
        eval_json_path = Path(args.eval_json)
    else:
        eval_json_path = model_path.parent / "evaluation.json"
    if eval_json_path.exists():
        threshold = export.load_threshold(eval_json_path)
        logging.getLogger(__name__).info(
            "using threshold %.3f from %s", threshold, eval_json_path,
        )

    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    y_binary = (predictions > threshold).astype(int)
    print(f"\nEvaluation on {len(y)} samples:")
    print(f"  Accuracy:  {accuracy_score(y, y_binary):.4f}")
    print(f"  Precision: {precision_score(y, y_binary, zero_division=0):.4f}")
    print(f"  Recall:    {recall_score(y, y_binary, zero_division=0):.4f}")
    print(f"  F1:        {f1_score(y, y_binary, zero_division=0):.4f}")
    if len(set(y)) > 1:
        print(f"  ROC AUC:   {roc_auc_score(y, predictions):.4f}")
        from sklearn.metrics import average_precision_score, brier_score_loss
        print(f"  Avg Prec:  {average_precision_score(y, predictions):.4f}")
        print(f"  Brier:     {brier_score_loss(y, predictions):.4f}")


def cmd_explain(args: argparse.Namespace) -> None:
    """Run SHAP analysis on a trained model."""
    from .model import load_model

    db_path = _db_dsn(args.db)
    spec_path = Path(args.spec)
    model_path = Path(args.model)
    out_dir = Path(args.output)

    spec = features.FeatureSpec.load(spec_path)
    rng = np.random.default_rng(42)
    sampled: list[tuple[dict[str, object], int]] = []
    seen = 0
    for report, label in data.stream_reports(db_path):
        seen += 1
        if len(sampled) < explain.MAX_EXPLAIN:
            sampled.append((report, label))
            continue
        j = int(rng.integers(seen))
        if j < explain.MAX_EXPLAIN:
            sampled[j] = (report, label)

    if not sampled:
        print("No samples found")
        return

    reports = [report for report, _label in sampled]
    labels = [label for _report, label in sampled]
    X, _ = features.extract_all(reports, labels, spec)
    if spec.standardized:
        X = features.standardize(X, spec)
    elif hasattr(X, "toarray"):
        X = X.toarray()

    model = load_model(model_path)

    explain.compute_shap_importance(
        model, X, spec,
        output_path=out_dir / "shap_importance.json",
    )


def _add_workers_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--workers",
        type=int,
        default=0,
        help="Feature extraction worker processes (default: auto; use 1 to force single-process)",
    )


def _add_seed_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for splitting, CV, and model training (default: 42)",
    )


def _predict_fixture_batch(
    booster: object,
    X: np.ndarray,
    iteration_range: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Predict probabilities, raw margins, and SHAP values for a feature matrix.

    Returns (probabilities, raw_margins, shap_values, shap_bias).
    """
    import xgboost as xgb

    dmat = xgb.DMatrix(X)
    raw_margins = booster.predict(dmat, output_margin=True, iteration_range=iteration_range)
    # sigmoid(margin) = probability
    probs = 1.0 / (1.0 + np.exp(-raw_margins))
    contribs = booster.predict(dmat, pred_contribs=True, iteration_range=iteration_range)
    shap_values = contribs[:, :-1]
    shap_bias = float(contribs[0, -1])
    return probs, raw_margins, shap_values, shap_bias


def generate_fixtures(
    model: object,
    spec: features.FeatureSpec,
    X_raw: object,
    X_std: object,
    out_dir: Path,
    n_samples: int = 50,
    optimal_threshold: float = 0.5,
) -> None:
    """Generate cross-language test fixtures for xgboost-ars.

    Writes two files into out_dir:
      - cross_language_fixture.json: raw features + expected predictions
        (tests the full Scaler → Model pipeline in Rust)
      - reference.json: standardized features + predictions + SHAP values,
        including NaN-feature and extreme-value edge-case samples
        (tests Model inference and TreeSHAP in Rust)
    """
    import numpy as np

    from .model import predict_proba

    rng = np.random.default_rng(42)
    n = min(n_samples, len(X_raw))
    idx = rng.choice(len(X_raw), n, replace=False)
    idx.sort()

    X_raw_sel = X_raw[idx]
    X_std_sel = X_std[idx]

    probs = predict_proba(model, X_std_sel)

    booster = model.get_booster()

    best_iteration = getattr(model, "best_iteration", None)
    if best_iteration is None:
        best_iteration = len(booster.get_dump()) - 1
    iteration_range = (0, best_iteration + 1)

    _, raw_margins, shap_values, shap_bias = _predict_fixture_batch(
        booster, X_std_sel, iteration_range,
    )

    # --- Edge-case samples for xgboost-ars correctness ---
    n_feat = spec.total_features

    # NaN samples: take real samples and knock out random subsets of features.
    # This exercises default_left routing in tree traversal and SHAP.
    nan_samples = []
    n_nan = min(10, n)
    for i in range(n_nan):
        row = X_std_sel[i].copy()
        # Knock out ~30% of features at deterministic positions.
        nan_mask = rng.random(n_feat) < 0.3
        row[nan_mask] = np.nan
        nan_samples.append(row)
    X_nan = np.array(nan_samples, dtype=np.float32)

    nan_probs, nan_margins, nan_shap, _ = _predict_fixture_batch(
        booster, X_nan, iteration_range,
    )

    # Extreme-value samples: very large/small features to test sigmoid tails
    # and tree traversal with values far outside training distribution.
    X_extreme = np.array([
        np.full(n_feat, 100.0, dtype=np.float32),   # all large positive
        np.full(n_feat, -100.0, dtype=np.float32),   # all large negative
        np.zeros(n_feat, dtype=np.float32),           # all zeros
    ])
    ext_probs, ext_margins, ext_shap, _ = _predict_fixture_batch(
        booster, X_extreme, iteration_range,
    )

    out_dir.mkdir(parents=True, exist_ok=True)

    cross_fixture = {
        "n_features": n_feat,
        "raw_features": X_raw_sel.tolist(),
        "probabilities": probs.tolist(),
    }
    cross_path = out_dir / "cross_language_fixture.json"
    with open(cross_path, "w") as f:
        json.dump(cross_fixture, f)
    print(f"  wrote {cross_path.name} ({n} samples)")

    reference = {
        "n_features": n_feat,
        "best_iteration": best_iteration,
        "optimal_threshold": optimal_threshold,
        "features": X_std_sel.tolist(),
        "probabilities": [float(p) for p in probs],
        "raw_margins": [float(m) for m in raw_margins],
        "shap_values": shap_values.tolist(),
        "shap_bias": shap_bias,
        # NaN edge cases: features with NaN at ~30% of positions.
        # Tests default_left routing in tree traversal and SHAP.
        "nan_features": _nan_safe_tolist(X_nan),
        "nan_probabilities": [float(p) for p in nan_probs],
        "nan_raw_margins": [float(m) for m in nan_margins],
        "nan_shap_values": nan_shap.tolist(),
        # Extreme-value edge cases: [all +100, all -100, all zeros].
        "extreme_features": X_extreme.tolist(),
        "extreme_probabilities": [float(p) for p in ext_probs],
        "extreme_raw_margins": [float(m) for m in ext_margins],
        "extreme_shap_values": ext_shap.tolist(),
    }
    ref_path = out_dir / "reference.json"
    with open(ref_path, "w") as f:
        json.dump(reference, f)
    print(f"  wrote {ref_path.name} ({n}+{n_nan}+{len(X_extreme)} samples, {n_feat} features)")


def _gather_diverse_fixture_reports(
    db_path: Path | str,
    target_per_bucket: int = 2,
) -> list[dict]:
    """Gather a diverse set of reports for the extraction parity fixture.

    Ensures coverage across:
    - File types: PE, ELF, Macho, JavaScript, Python, Go, Rust, Shell, etc.
    - Score ranges: low (3-10), medium (11-50), high (50+)
    - Labels: malware and benign
    - Multi-file samples: archives/packages with inner files
    - Edge cases: unsigned binaries, packed, supply-chain patterns

    Returns ~50-80 reports covering all important code paths.
    """
    import psycopg  # noqa: PLC0415

    reports: list[dict] = []
    seen_ids: set[int] = set()

    dsn = str(db_path)
    if not dsn.startswith(("postgres://", "postgresql://")):
        # SQLite fallback — just stream whatever is available.
        for report, _label in data.stream_reports(db_path):
            reports.append(report)
            if len(reports) >= 30:
                break
        return reports

    conn = psycopg.connect(dsn)

    def _fetch(query: str, params: list | None = None) -> None:
        with conn.cursor() as cur:
            cur.execute(query, params or [])
            for (rid, raw) in cur:
                rid = int(rid)
                if rid in seen_ids:
                    continue
                seen_ids.add(rid)
                report = json.loads(raw) if isinstance(raw, str) else raw
                if isinstance(report, dict):
                    reports.append(report)

    # Cover each major file type × label combo
    file_types = ["pe", "elf", "macho", "javascript", "python", "go",
                  "rust", "shell", "c", "ruby", "perl"]
    for ft in file_types:
        for label in ["bad", "good"]:
            _fetch(
                "SELECT id, cleave_result FROM samples "
                "WHERE file_type = %s AND label = %s AND cleave_result IS NOT NULL "
                "AND score >= 3 AND skip = '' ORDER BY random() LIMIT %s",
                [ft, label, target_per_bucket],
            )

    # Multi-file samples (archives, packages with inner files)
    _fetch(
        "SELECT id, cleave_result FROM samples "
        "WHERE cleave_result IS NOT NULL AND score >= 5 AND skip = '' "
        "AND label = 'bad' AND jsonb_array_length(cleave_result->'fs') > 1 "
        "ORDER BY random() LIMIT %s",
        [target_per_bucket],
    )
    _fetch(
        "SELECT id, cleave_result FROM samples "
        "WHERE cleave_result IS NOT NULL AND score >= 5 AND skip = '' "
        "AND label = 'good' AND jsonb_array_length(cleave_result->'fs') > 1 "
        "ORDER BY random() LIMIT %s",
        [target_per_bucket],
    )

    # High-score malware (likely to exercise many features)
    _fetch(
        "SELECT id, cleave_result FROM samples "
        "WHERE label = 'bad' AND cleave_result IS NOT NULL "
        "AND score >= 50 AND skip = '' ORDER BY random() LIMIT %s",
        [target_per_bucket],
    )

    # Low-score edge cases (the FN population)
    _fetch(
        "SELECT id, cleave_result FROM samples "
        "WHERE label = 'bad' AND cleave_result IS NOT NULL "
        "AND score >= 3 AND score <= 5 AND skip = '' ORDER BY random() LIMIT %s",
        [target_per_bucket],
    )

    conn.close()
    log.info("fixture: gathered %d diverse reports (%d file types, %d with inner files)",
             len(reports), len(file_types), sum(1 for r in reports if any(
                 f.get("dp", 0) > 0 for f in (r.get("fs") or []))))
    return reports


def generate_extraction_fixture(
    reports: list[dict],
    spec: features.FeatureSpec,
    out_dir: Path,
    n_samples: int = 10,
    model: object | None = None,
    optimal_threshold: float = 0.5,
    recommended_thresholds: dict[str, float | None] | None = None,
) -> None:
    """Generate a feature-extraction parity fixture for litmus.

    Writes extraction_fixture.json containing raw cleave reports and their
    expected feature vectors, standardized features, probabilities, and
    classifications. Tests the full pipeline: cleave JSON → extract → standardize
    → predict → classify.

    Classification uses the same three-tier logic as litmus's Thresholds::classify:
      prob >= hostile  → "hostile"
      prob >= suspicious → "suspicious"
      otherwise        → "benign"

    Thresholds are resolved in the same priority order as litmus: recommended
    thresholds from evaluation.json, falling back to optimal_threshold as a
    single hostile threshold.
    """
    from .model import predict_proba

    rng = np.random.default_rng(99)
    n = min(n_samples, len(reports))
    idx = rng.choice(len(reports), n, replace=False)
    idx.sort()

    # Resolve thresholds to match litmus's Model::load priority:
    # recommended_thresholds (suspicious + hostile) > optimal_threshold as hostile-only.
    suspicious_thresh: float | None = None
    hostile_thresh: float = optimal_threshold
    if recommended_thresholds:
        s = recommended_thresholds.get("suspicious")
        h = recommended_thresholds.get("hostile")
        if s is not None and h is not None:
            suspicious_thresh = float(s)
            hostile_thresh = float(h)

    ctx = features._ExtractContext(spec)
    samples = []
    for i in idx:
        report = reports[i]
        vec = np.zeros(spec.total_features, dtype=np.float32)
        # Pull score/formula/elements from the cleave report itself (matching
        # hopper's parseCleaveFile and the live-scan path in features.extract).
        formula, elements, score = features.canonical_fields_from_report(report)
        features._extract_into(
            report, ctx, vec,
            formula=formula, elements=elements, score=score,
        )

        sample: dict = {
            "report": report,
            "expected_features": vec.tolist(),
        }

        # Add standardized features and end-to-end prediction if model available.
        # Use dense arrays throughout to match litmus/xgboost-ars inference
        # (sparse inputs route zeros via default_left, which diverges).
        if model is not None:
            dense_vec = vec.reshape(1, -1)
            if spec.standardized:
                import scipy.sparse as sp
                std_vec = features.standardize(sp.csr_matrix(dense_vec), spec)
                std_dense = std_vec.toarray() if hasattr(std_vec, "toarray") else std_vec
            else:
                std_dense = dense_vec
            prob = float(predict_proba(model, std_dense)[0])

            # Three-tier classification matching litmus Thresholds::classify.
            if prob >= hostile_thresh:
                classification = "hostile"
            elif suspicious_thresh is not None and prob >= suspicious_thresh:
                classification = "suspicious"
            else:
                classification = "benign"

            sample["expected_standardized"] = std_dense.flatten().tolist()
            sample["expected_probability"] = prob
            sample["expected_classification"] = classification
            sample["threshold"] = optimal_threshold

        samples.append(sample)

    fixture = {
        "n_features": spec.total_features,
        "feature_names": spec.feature_names,
        "samples": samples,
    }
    path = out_dir / "extraction_fixture.json"
    with open(path, "w") as f:
        json.dump(fixture, f)
    print(f"  wrote {path.name} ({n} samples, {spec.total_features} features)")


def _nan_safe_tolist(arr: np.ndarray) -> list:
    """Convert array to nested list, encoding NaN as the string "NaN".

    JSON has no NaN literal, so we encode it as a string for the Rust
    deserializer to interpret.
    """
    import math

    def _convert(x: float) -> float | str:
        return "NaN" if math.isnan(x) else float(x)

    return [[_convert(v) for v in row] for row in arr]


def cmd_fixture(args: argparse.Namespace) -> None:
    """Generate cross-language test fixtures for xgboost-ars."""
    from .model import load_model

    db_path = _db_dsn(args.db)
    spec_path = Path(args.spec)
    model_path = Path(args.model)

    spec = features.FeatureSpec.load(spec_path)
    model = load_model(model_path)

    # Reservoir-sample n_samples from the stream to avoid loading all data.
    n = args.n_samples
    rng = np.random.default_rng(42)
    reservoir: list[data.Sample] = []
    for i, sample in enumerate(data.stream_samples(db_path)):
        if i < n:
            reservoir.append(sample)
        else:
            j = int(rng.integers(i + 1))
            if j < n:
                reservoir[j] = sample

    if not reservoir:
        print("No samples found")
        return

    reports = [s.report for s in reservoir]
    labels = [s.label for s in reservoir]
    X, _ = features.extract_all(reports, labels, spec)

    X_fix = X.toarray()
    X_fix_std = features.standardize(X, spec) if spec.standardized else X_fix

    # Load the calibrated threshold from evaluation.json if available.
    eval_path = Path(args.output) / "evaluation.json"
    threshold = 0.5
    if eval_path.exists():
        threshold = export.load_threshold(eval_path)
        log.info("using threshold %.3f from %s", threshold, eval_path)

    generate_fixtures(
        model, spec, X_fix, X_fix_std,
        out_dir=Path(args.output),
        n_samples=n,
        optimal_threshold=threshold,
    )

    # Feature-extraction parity fixture for litmus — diverse samples.
    recommended = None
    if eval_path.exists():
        eval_data = export.load_evaluation(eval_path)
        recommended = eval_data.get("recommended_thresholds")
    extraction_reports = _gather_diverse_fixture_reports(db_path)
    if extraction_reports:
        generate_extraction_fixture(
            extraction_reports, spec, out_dir=Path(args.output),
            n_samples=len(extraction_reports),
            model=model, optimal_threshold=threshold,
            recommended_thresholds=recommended,
        )


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(
        prog="collimator",
        description="ML training pipeline for malware detection",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # train
    p_train = subparsers.add_parser("train", help="Train model and export to ONNX")
    p_train.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    p_train.add_argument("--output", default="out", help="Output directory (default: out)")
    _add_workers_arg(p_train)
    _add_seed_arg(p_train)
    p_train.add_argument("--n-estimators", type=int, default=None, help="Max XGBoost trees (default: TrainConfig default)")
    p_train.add_argument("--max-depth", type=int, default=None, help="Tree depth limit (default: TrainConfig default)")
    p_train.add_argument("--learning-rate", type=float, default=None, help="XGBoost learning rate (default: TrainConfig default)")
    p_train.add_argument("--early-stopping-rounds", type=int, default=None, help="Early stopping patience (default: TrainConfig default)")
    p_train.add_argument("--beta", type=float, default=None, help="F-beta for threshold selection (default: TrainConfig default)")
    p_train.add_argument("--threshold-mode", choices=["fbeta", "max_recall_at_fpr"], default="fbeta", help="Threshold selection strategy")
    p_train.add_argument("--threshold-fpr-target", type=float, default=None, help="Max FPR target when threshold-mode=max_recall_at_fpr")
    p_train.add_argument("--hard-negative-fraction", type=float, default=0.0, help="Fraction of benign train rows to upweight as hard negatives")
    p_train.add_argument("--hard-negative-weight", type=float, default=1.0, help="Sample weight applied to hard benign negatives")
    p_train.add_argument(
        "--min-malware-score", type=int, default=0,
        help="Ignore malware samples with score below this threshold during training",
    )

    # evaluate
    p_eval = subparsers.add_parser("evaluate", help="Evaluate existing model")
    p_eval.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    p_eval.add_argument("--model", required=True, help="Path to ONNX model")
    p_eval.add_argument("--spec", required=True, help="Path to feature_spec.json")
    p_eval.add_argument("--eval-json", default=None, help="Path to evaluation.json for threshold")

    # explain
    p_explain = subparsers.add_parser("explain", help="SHAP feature importance analysis")
    p_explain.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    p_explain.add_argument("--model", required=True, help="Path to XGBoost model (.json)")
    p_explain.add_argument("--spec", required=True, help="Path to feature_spec.json")
    p_explain.add_argument("--output", default="out", help="Output directory")

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect a single sample from the DB")
    p_inspect.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    p_inspect.add_argument("--sample", required=True, help="SHA256 (or prefix) of sample")
    p_inspect.add_argument("--model", default="out/model.json", help="Path to XGBoost model")
    p_inspect.add_argument(
        "--spec", default="out/feature_spec.json", help="Path to feature_spec.json",
    )

    # errors
    p_errors = subparsers.add_parser("errors", help="Show misclassified samples")
    p_errors.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    p_errors.add_argument("--model", default="out/model.json", help="Path to XGBoost model")
    p_errors.add_argument(
        "--spec", default="out/feature_spec.json", help="Path to feature_spec.json",
    )
    p_errors.add_argument("--top", type=int, default=20, help="Number of errors to show")

    # scan
    p_scan = subparsers.add_parser("scan", help="Score a live file using cleave + model")
    p_scan.add_argument("file", help="Path to file to scan")
    p_scan.add_argument("--model", default="out/model.json", help="Path to XGBoost model")
    p_scan.add_argument("--spec", default="out/feature_spec.json", help="Path to feature_spec.json")
    p_scan.add_argument("--cleave", default="cleave", help="Path to cleave binary")
    p_scan.add_argument("--db", default=None, help="Background DB for SHAP context (optional)")

    # rethreshold
    p_rethresh = subparsers.add_parser(
        "rethreshold", help="Recompute suspicious/hostile thresholds from saved CV predictions",
    )
    p_rethresh.add_argument("--output", default="out", help="Directory with cv_predictions.npz")

    # fixture
    p_fixture = subparsers.add_parser(
        "fixture", help="Generate cross-language test fixtures for xgboost-ars",
    )
    p_fixture.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    p_fixture.add_argument("--model", default="out/model.json", help="Path to XGBoost model")
    p_fixture.add_argument(
        "--spec", default="out/feature_spec.json", help="Path to feature_spec.json",
    )
    p_fixture.add_argument("--output", default="out", help="Output directory")
    p_fixture.add_argument(
        "--n-samples", type=int, default=10, help="Number of samples in fixture (default: 10)",
    )

    # traits
    p_traits = subparsers.add_parser("traits", help="Analyze exact finding IDs across the DB")
    p_traits.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    p_traits.add_argument(
        "--crit",
        default="hostile",
        help="Only include findings with this criticality (default: hostile). Use 'any' for all.",
    )
    p_traits.add_argument(
        "--sort",
        choices=["precision", "benign", "malware", "support", "lift"],
        default="precision",
        help="How to rank traits (default: precision; low precision surfaces noisy traits)",
    )
    p_traits.add_argument("--top", type=int, default=50, help="Number of traits to show")
    p_traits.add_argument(
        "--min-samples",
        type=int,
        default=1,
        help="Minimum number of samples containing a trait to include it",
    )
    p_traits.add_argument("--output", default=None, help="Optional JSON output path")

    # thresholds
    p_thresh = subparsers.add_parser(
        "thresholds", help="Show accuracy at various confidence thresholds",
    )
    p_thresh.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    p_thresh.add_argument(
        "--model", default=None,
        help="Path to trained XGBoost model (.json) to reuse instead of retraining",
    )
    p_thresh.add_argument(
        "--spec", default=None,
        help="Path to feature_spec.json to reuse instead of rebuilding vocab",
    )
    _add_workers_arg(p_thresh)

    # tune-thresholds
    p_tune = subparsers.add_parser(
        "tune-thresholds",
        help="Score the full labeled corpus with an existing model and compare threshold policies",
    )
    p_tune.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    p_tune.add_argument("--model", default="out/model.json", help="Path to trained XGBoost model")
    p_tune.add_argument("--spec", default="out/feature_spec.json", help="Path to feature_spec.json")
    p_tune.add_argument("--path-substr", default=None, help="Only include rows whose sample path contains this substring")
    p_tune.add_argument("--min-score", type=int, default=None, help="Optional minimum hopper score to include")
    p_tune.add_argument("--max-score", type=int, default=None, help="Optional maximum hopper score to include")
    p_tune.add_argument("--top-errors", type=int, default=20, help="How many FP/FN paths to show per policy level")
    p_tune.add_argument("--output", default=None, help="Optional JSON output path")
    p_tune.add_argument("--limit", type=int, default=0, help="Optional row cap after filters (0 = no cap)")
    p_tune.add_argument("--scores-cache", default=None, help="Optional .npz cache for full-corpus scores")
    p_tune.add_argument("--refresh-cache", action="store_true", help="Rebuild --scores-cache even if it is current")
    _add_workers_arg(p_tune)

    # false-positives
    p_fp = subparsers.add_parser(
        "false-positives",
        help="Show false positives grouped by severity level",
    )
    p_fp.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    p_fp.add_argument("--model", default="out/model.json", help="Path to trained XGBoost model")
    p_fp.add_argument("--spec", default="out/feature_spec.json", help="Path to feature_spec.json")
    p_fp.add_argument("--top-errors", type=int, default=50, help="How many false positives to show")
    p_fp.add_argument("--output", default=None, help="Optional JSON output path")
    p_fp.add_argument("--scores-cache", default=None, help="Optional .npz cache for full-corpus scores")
    p_fp.add_argument("--refresh-cache", action="store_true", help="Rebuild --scores-cache even if it is current")
    _add_workers_arg(p_fp)

    # false-negatives
    p_fn = subparsers.add_parser(
        "false-negatives",
        help="Show false negatives grouped by severity level",
    )
    p_fn.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    p_fn.add_argument("--model", default="out/model.json", help="Path to trained XGBoost model")
    p_fn.add_argument("--spec", default="out/feature_spec.json", help="Path to feature_spec.json")
    p_fn.add_argument("--top-errors", type=int, default=50, help="How many false negatives to show")
    p_fn.add_argument("--output", default=None, help="Optional JSON output path")
    p_fn.add_argument("--scores-cache", default=None, help="Optional .npz cache for full-corpus scores")
    p_fn.add_argument("--refresh-cache", action="store_true", help="Rebuild --scores-cache even if it is current")
    _add_workers_arg(p_fn)

    # benchmark
    p_bench = subparsers.add_parser("benchmark", help="Benchmark extraction, training, and inference")
    p_bench.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    p_bench.add_argument("--model", default=None, help="Optional trained XGBoost model (.json)")
    p_bench.add_argument("--spec", default=None, help="Optional feature_spec.json")
    p_bench.add_argument("--output", default=None, help="Optional JSON output path")
    _add_workers_arg(p_bench)

    # experiment
    p_exp = subparsers.add_parser(
        "experiment", help="Run a fast subsampled experiment on the full external test bucket",
    )
    p_exp.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    p_exp.add_argument("--output", default="out", help="Directory for experiment summaries (default: out)")
    p_exp.add_argument("--cache-dir", default=None, help="Directory for experiment data caches (corpus + matrices)")
    p_exp.add_argument(
        "--train-samples", type=int, default=10_000,
        help="Approximate sampled training rows (default: 10000)",
    )
    p_exp.add_argument("--n-folds", type=int, default=2, help="CV folds for the experiment")
    p_exp.add_argument("--n-estimators", type=int, default=220, help="Max trees for the experiment")
    p_exp.add_argument("--max-depth", type=int, default=6, help="Tree depth for the experiment")
    p_exp.add_argument(
        "--learning-rate", type=float, default=0.03, help="Learning rate for the experiment",
    )
    p_exp.add_argument(
        "--early-stopping-rounds", type=int, default=25,
        help="Early stopping rounds for the experiment",
    )
    p_exp.add_argument(
        "--max-test-samples", type=int, default=0,
        help="Cap external test set via reservoir sampling (0 = full test bucket, default: 0)",
    )
    p_exp.add_argument("--min-child-weight", type=int, default=5, help="Minimum child weight")
    p_exp.add_argument("--colsample-bytree", type=float, default=0.8, help="Subsample ratio of columns")
    p_exp.add_argument("--subsample", type=float, default=0.8, help="Subsample ratio of training instances")
    p_exp.add_argument("--gamma", type=float, default=0.0, help="Minimum loss reduction to make a further partition")
    p_exp.add_argument("--reg-alpha", type=float, default=0.0, help="L1 regularization term on weights")
    p_exp.add_argument("--reg-lambda", type=float, default=1.0, help="L2 regularization term on weights")
    p_exp.add_argument("--beta", type=float, default=1.0, help="F-beta for threshold selection (default: 1.0)")
    p_exp.add_argument("--threshold-mode", choices=["fbeta", "max_recall_at_fpr"], default="fbeta", help="Threshold selection strategy")
    p_exp.add_argument("--threshold-fpr-target", type=float, default=None, help="Max FPR target when threshold-mode=max_recall_at_fpr")
    p_exp.add_argument("--hard-negative-fraction", type=float, default=0.0, help="Fraction of benign train rows to upweight as hard negatives")
    p_exp.add_argument("--hard-negative-weight", type=float, default=1.0, help="Sample weight applied to hard benign negatives")
    p_exp.add_argument(
        "--benign-filetype-weight",
        action="append",
        default=[],
        help="Upweight benign training rows for a file type, format filetype=weight; repeatable",
    )
    p_exp.add_argument(
        "--total-limit", type=int, default=0,
        help="Cap total records scanned from DB (oldest first, 0 = unlimited)",
    )
    p_exp.add_argument(
        "--monotone-json",
        help="JSON dictionary mapping feature name prefixes to 1 or -1 constraints",
    )
    p_exp.add_argument(
        "--min-malware-score", type=int, default=0,
        help="Ignore malware samples with score below this threshold during training (but keep in test)",
    )
    _add_workers_arg(p_exp)
    _add_seed_arg(p_exp)

    # ablation
    p_ablate = subparsers.add_parser("ablate", help="Run leave-one-group-out feature ablations")
    p_ablate.add_argument("--db", required=True, help="Path to hopper database (SQLite path or postgres:// DSN)")
    p_ablate.add_argument(
        "--groups",
        nargs="*",
        choices=list(features.FEATURE_GROUPS),
        default=None,
        help="Optional subset of feature groups to ablate",
    )
    p_ablate.add_argument("--output", default=None, help="Optional JSON output path")
    p_ablate.add_argument("--n-estimators", type=int, default=None)
    p_ablate.add_argument("--max-depth", type=int, default=None)
    p_ablate.add_argument("--learning-rate", type=float, default=None)
    p_ablate.add_argument("--early-stopping-rounds", type=int, default=None)
    p_ablate.add_argument("--beta", type=float, default=None)
    p_ablate.add_argument("--n-folds", type=int, default=None)
    p_ablate.add_argument(
        "--min-malware-score", type=int, default=0,
        help="Ignore malware samples with score below this threshold during training",
    )
    p_ablate.add_argument(
        "--train-samples", type=int, default=0,
        help="Subsample training data to this size (0 = all, balanced malware/benign)",
    )
    p_ablate.add_argument(
        "--max-test-samples", type=int, default=0,
        help="Cap test data to this size (0 = all)",
    )
    _add_workers_arg(p_ablate)
    _add_seed_arg(p_ablate)

    # demo-db
    p_demo = subparsers.add_parser("demo-db", help="Create a small synthetic hopper database")
    p_demo.add_argument("--output", required=True, help="Path to output SQLite database")
    p_demo.add_argument("--n-benign", type=int, default=64, help="Number of benign samples")
    p_demo.add_argument("--n-malware", type=int, default=64, help="Number of malware samples")
    _add_seed_arg(p_demo)

    args = parser.parse_args()

    if args.command == "train":
        cmd_train(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    elif args.command == "explain":
        cmd_explain(args)
    elif args.command == "inspect":
        inspect.inspect_sample(
            sha256=args.sample,
            db_path=_db_dsn(args.db),
            model_path=Path(args.model),
            spec_path=Path(args.spec),
        )
    elif args.command == "errors":
        inspect.inspect_errors(
            db_path=_db_dsn(args.db),
            model_path=Path(args.model),
            spec_path=Path(args.spec),
            top_n=args.top,
        )
    elif args.command == "scan":
        inspect.scan_file(
            file_path=args.file,
            model_path=Path(args.model),
            spec_path=Path(args.spec),
            cleave_bin=args.cleave,
        )
    elif args.command == "rethreshold":
        cv_path = Path(args.output) / "cv_predictions.npz"
        if not cv_path.exists():
            print(f"error: {cv_path} not found — run make train first")
            sys.exit(1)
        arrays = np.load(str(cv_path))
        cv_preds = arrays["cv_predictions"]
        cv_labels = arrays["cv_labels"]
        all_preds = cv_preds
        all_labels = cv_labels
        if "test_predictions" in arrays:
            all_preds = np.concatenate([cv_preds, arrays["test_predictions"]])
            all_labels = np.concatenate([cv_labels, arrays["test_labels"]])
        print(f"Loaded {len(cv_preds)} CV + {len(all_preds) - len(cv_preds)} test predictions")
        recommended = thresholds.compute_default_recommendations(all_preds, all_labels)
        severity_levels = thresholds.compute_severity_levels(all_preds, all_labels)
        print(f"Recommended thresholds: {recommended}")
        # Update evaluation.json
        eval_path = Path(args.output) / "evaluation.json"
        if eval_path.exists():
            eval_data = json.load(open(eval_path))
            eval_data["recommended_thresholds"] = recommended
            eval_data["severity_level_targets"] = thresholds.SEVERITY_LEVEL_TARGETS
            eval_data["severity_levels"] = severity_levels
            with open(eval_path, "w") as f:
                json.dump(eval_data, f, indent=2)
            print(f"Updated {eval_path}")
        thresholds.print_recommendations(all_preds, all_labels, title="FULL DB")
    elif args.command == "fixture":
        cmd_fixture(args)
    elif args.command == "traits":
        traits.analyze_traits(
            db_path=_db_dsn(args.db),
            crit=None if args.crit == "any" else {"filtered": 0, "component": 1, "baseline": 2, "notable": 3, "suspicious": 4, "hostile": 5}.get(args.crit, 0),
            min_samples=args.min_samples,
            sort_by=args.sort,
            top_n=args.top,
            output_path=Path(args.output) if args.output else None,
        )
    elif args.command == "thresholds":
        thresholds.show_thresholds(
            db_path=_db_dsn(args.db),
            model_path=Path(args.model) if args.model else None,
            spec_path=Path(args.spec) if args.spec else None,
            n_workers=args.workers,
        )
    elif args.command == "tune-thresholds":
        thresholds.tune_thresholds(
            db_path=_db_dsn(args.db),
            model_path=Path(args.model),
            spec_path=Path(args.spec),
            path_substr=args.path_substr,
            min_score=args.min_score,
            max_score=args.max_score,
            top_errors=args.top_errors,
            output_path=Path(args.output) if args.output else None,
            limit=args.limit,
            n_workers=args.workers,
            cache_path=Path(args.scores_cache) if args.scores_cache else None,
            refresh_cache=args.refresh_cache,
        )
    elif args.command == "false-positives":
        thresholds.show_false_positives(
            db_path=_db_dsn(args.db),
            model_path=Path(args.model),
            spec_path=Path(args.spec),
            top_errors=args.top_errors,
            output_path=Path(args.output) if args.output else None,
            n_workers=args.workers,
            cache_path=Path(args.scores_cache) if args.scores_cache else None,
            refresh_cache=args.refresh_cache,
        )
    elif args.command == "false-negatives":
        thresholds.show_false_negatives(
            db_path=_db_dsn(args.db),
            model_path=Path(args.model),
            spec_path=Path(args.spec),
            top_errors=args.top_errors,
            output_path=Path(args.output) if args.output else None,
            n_workers=args.workers,
            cache_path=Path(args.scores_cache) if args.scores_cache else None,
            refresh_cache=args.refresh_cache,
        )
    elif args.command == "benchmark":
        benchmark.run_benchmark(
            db_path=_db_dsn(args.db),
            n_workers=args.workers,
            model_path=Path(args.model) if args.model else None,
            spec_path=Path(args.spec) if args.spec else None,
            output_path=Path(args.output) if args.output else None,
        )
    elif args.command == "experiment":
        experiment.run_experiment(
            db_path=_db_dsn(args.db),
            output_dir=Path(args.output),
            cache_dir=Path(args.cache_dir) if args.cache_dir else None,
            n_workers=args.workers,
            seed=args.seed,
            train_samples=args.train_samples,
            max_test_samples=args.max_test_samples,
            n_folds=args.n_folds,
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            learning_rate=args.learning_rate,
            early_stopping_rounds=args.early_stopping_rounds,
            min_child_weight=args.min_child_weight,
            colsample_bytree=args.colsample_bytree,
            subsample=args.subsample,
            gamma=args.gamma,
            reg_alpha=args.reg_alpha,
            reg_lambda=args.reg_lambda,
            beta=args.beta,
            threshold_mode=args.threshold_mode,
            threshold_fpr_target=args.threshold_fpr_target,
            hard_negative_fraction=args.hard_negative_fraction,
            hard_negative_weight=args.hard_negative_weight,
            benign_filetype_weights=_parse_filetype_weights(args.benign_filetype_weight),
            total_limit=args.total_limit,
            monotone_constraints=json.loads(args.monotone_json) if args.monotone_json else None,
            min_malware_training_score=args.min_malware_score,
        )
    elif args.command == "ablate":
        rows = ablation.run_ablation(
            db_path=_db_dsn(args.db),
            n_workers=args.workers,
            seed=args.seed,
            groups=args.groups,
            min_malware_training_score=args.min_malware_score,
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            learning_rate=args.learning_rate,
            early_stopping_rounds=args.early_stopping_rounds,
            beta=args.beta,
            n_folds=args.n_folds,
            train_samples=args.train_samples,
            max_test_samples=args.max_test_samples,
        )
        ablation.print_ablation(rows)
        if args.output:
            ablation.save_ablation(rows, Path(args.output))
    elif args.command == "demo-db":
        demo.create_demo_db(
            Path(args.output),
            n_benign=args.n_benign,
            n_malware=args.n_malware,
            seed=args.seed,
        )


if __name__ == "__main__":
    main()
