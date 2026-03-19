"""CLI entry point for collimator training pipeline."""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

import numpy as np

from . import ablation, benchmark, data, demo, experiment, explain, export, features, inspect, thresholds, train, traits

log = logging.getLogger(__name__)


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


def cmd_train(args: argparse.Namespace) -> None:
    """Train a model and export to ONNX."""
    db_path = Path(args.db)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    effective_workers = features.resolve_worker_count(args.workers)
    if args.workers <= 0:
        log.info("auto workers: using %d worker processes", effective_workers)
    else:
        log.info("using %d worker processes", effective_workers)

    # Pass 1: stream reports to build vocabulary (no reports kept in memory).
    log.info("pass 1: building vocabulary from %s", db_path)
    spec = features.build_vocab(
        (report for report, _label in data.stream_raw_reports(db_path, exclude_test=True)),
        n_workers=args.workers,
    )

    # Pass 2: stream the corpus once to extract both training and held-out test features.
    log.info("pass 2: extracting training and test features")
    X, y, X_test, y_test = features.extract_partitioned_stream(
        data.stream_partitioned_raw_reports(db_path), spec, n_workers=args.workers,
    )
    if X.shape[0] < 10:
        print(f"ERROR: only {X.shape[0]} training samples, need at least 10")
        sys.exit(1)

    # Train.
    config = train.TrainConfig(seed=args.seed)
    result = train.train(X, y, config, feature_names=spec.feature_names)

    # Attach standardization params to spec before saving.
    spec.feature_means = result.feature_means
    spec.feature_stds = result.feature_stds

    # Export.
    spec.save(out_dir / "feature_spec.json")
    export.export_onnx(result.model, spec.total_features, out_dir / "model.onnx")
    export.save_model(result.model, out_dir / "model.json")
    export.save_evaluation(
        metrics=result.metrics,
        calibration=result.calibration,
        optimal_threshold=result.optimal_threshold,
        confusion=result.confusion,
        class_distribution=result.class_distribution,
        split_summary=result.split_summary,
        fold_metrics=result.fold_metrics,
        n_features=spec.total_features,
        experiment={
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
            },
        },
        output_path=out_dir / "evaluation.json",
    )

    # Post-training steps only need small dense subsets — avoid densifying
    # the full sparse matrix to keep memory low.
    rng = np.random.default_rng(42)

    def _dense_subset(n: int) -> np.ndarray:
        idx = rng.choice(X.shape[0], min(n, X.shape[0]), replace=False)
        return X[idx].toarray()

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

    # Cross-language test fixtures (10 samples).
    fix_idx = rng.choice(X.shape[0], min(10, X.shape[0]), replace=False)
    fix_idx.sort()
    X_fix = X[fix_idx].toarray()
    generate_fixtures(result.model, spec, X_fix, X_fix, out_dir)

    # Threshold table on the deterministic test set.
    if X_test.shape[0] > 0:
        from .model import predict_proba
        test_probs = predict_proba(result.model, X_test)
        thresholds.print_threshold_table(test_probs, y_test)
    else:
        print("\nNo test samples — skipping threshold table.")

    print(f"\nOutput files in {out_dir}/:")
    for f in sorted(out_dir.iterdir()):
        if f.is_file():
            size = f.stat().st_size
            print(f"  {f.name:<30s} {size:>10,d} bytes")


def cmd_evaluate(args: argparse.Namespace) -> None:
    """Evaluate an existing model against a database."""
    db_path = Path(args.db)
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

    db_path = Path(args.db)
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


def generate_fixtures(
    model: object,
    spec: features.FeatureSpec,
    X_raw: object,
    X_std: object,
    out_dir: Path,
    n_samples: int = 10,
) -> None:
    """Generate cross-language test fixtures for xgboost-native.

    Writes two files into out_dir:
      - cross_language_fixture.json: raw features + expected predictions
        (tests the full Scaler → Model pipeline in Rust)
      - reference.json: standardized features + predictions + SHAP values
        (tests Model inference and TreeSHAP in Rust)
    """
    import numpy as np
    import xgboost as xgb

    from .model import predict_proba

    rng = np.random.default_rng(42)
    n = min(n_samples, len(X_raw))
    idx = rng.choice(len(X_raw), n, replace=False)
    idx.sort()

    X_raw_sel = X_raw[idx]
    X_std_sel = X_std[idx]

    probs = predict_proba(model, X_std_sel)

    booster = model.get_booster()
    dmat = xgb.DMatrix(X_std_sel)
    raw_margins = booster.predict(dmat, output_margin=True)

    shap_contribs = booster.predict(dmat, pred_contribs=True)
    shap_values = shap_contribs[:, :-1]
    shap_bias = float(shap_contribs[0, -1])

    best_iteration = getattr(model, "best_iteration", None)
    if best_iteration is None:
        best_iteration = len(booster.get_dump()) - 1

    out_dir.mkdir(parents=True, exist_ok=True)

    cross_fixture = {
        "n_features": spec.total_features,
        "raw_features": X_raw_sel.tolist(),
        "probabilities": probs.tolist(),
    }
    cross_path = out_dir / "cross_language_fixture.json"
    with open(cross_path, "w") as f:
        json.dump(cross_fixture, f)
    print(f"  wrote {cross_path.name} ({n} samples)")

    reference = {
        "n_features": spec.total_features,
        "best_iteration": best_iteration,
        "features": X_std_sel.tolist(),
        "probabilities": [float(p) for p in probs],
        "raw_margins": [float(m) for m in raw_margins],
        "shap_values": shap_values.tolist(),
        "shap_bias": shap_bias,
    }
    ref_path = out_dir / "reference.json"
    with open(ref_path, "w") as f:
        json.dump(reference, f)
    print(f"  wrote {ref_path.name} ({n} samples, {spec.total_features} features)")


def cmd_fixture(args: argparse.Namespace) -> None:
    """Generate cross-language test fixtures for xgboost-native."""
    from .model import load_model

    db_path = Path(args.db)
    spec_path = Path(args.spec)
    model_path = Path(args.model)

    samples = data.load_samples(db_path)
    spec = features.FeatureSpec.load(spec_path)
    model = load_model(model_path)

    reports = [s.report for s in samples]
    labels = [s.label for s in samples]
    X, _ = features.extract_all(reports, labels, spec)

    # Only densify the small subset needed for fixtures.
    rng = np.random.default_rng(42)
    idx = rng.choice(X.shape[0], min(args.n_samples, X.shape[0]), replace=False)
    idx.sort()

    X_fix = X[idx].toarray()
    X_fix_std = features.standardize(X[idx], spec) if spec.standardized else X_fix

    generate_fixtures(
        model, spec, X_fix, X_fix_std,
        out_dir=Path(args.output),
        n_samples=args.n_samples,
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
    p_train.add_argument("--db", required=True, help="Path to cyclotron SQLite database")
    p_train.add_argument("--output", default="out", help="Output directory (default: out)")
    _add_workers_arg(p_train)
    _add_seed_arg(p_train)

    # evaluate
    p_eval = subparsers.add_parser("evaluate", help="Evaluate existing model")
    p_eval.add_argument("--db", required=True, help="Path to cyclotron SQLite database")
    p_eval.add_argument("--model", required=True, help="Path to ONNX model")
    p_eval.add_argument("--spec", required=True, help="Path to feature_spec.json")
    p_eval.add_argument("--eval-json", default=None, help="Path to evaluation.json for threshold")

    # explain
    p_explain = subparsers.add_parser("explain", help="SHAP feature importance analysis")
    p_explain.add_argument("--db", required=True, help="Path to cyclotron SQLite database")
    p_explain.add_argument("--model", required=True, help="Path to XGBoost model (.json)")
    p_explain.add_argument("--spec", required=True, help="Path to feature_spec.json")
    p_explain.add_argument("--output", default="out", help="Output directory")

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect a single sample from the DB")
    p_inspect.add_argument("--db", required=True, help="Path to cyclotron SQLite database")
    p_inspect.add_argument("--sample", required=True, help="SHA256 (or prefix) of sample")
    p_inspect.add_argument("--model", default="out/model.json", help="Path to XGBoost model")
    p_inspect.add_argument(
        "--spec", default="out/feature_spec.json", help="Path to feature_spec.json",
    )

    # errors
    p_errors = subparsers.add_parser("errors", help="Show misclassified samples")
    p_errors.add_argument("--db", required=True, help="Path to cyclotron SQLite database")
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

    # fixture
    p_fixture = subparsers.add_parser(
        "fixture", help="Generate cross-language test fixtures for xgboost-native",
    )
    p_fixture.add_argument("--db", required=True, help="Path to cyclotron SQLite database")
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
    p_traits.add_argument("--db", required=True, help="Path to cyclotron SQLite database")
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
    p_thresh.add_argument("--db", required=True, help="Path to cyclotron SQLite database")
    p_thresh.add_argument(
        "--model", default=None,
        help="Path to trained XGBoost model (.json) to reuse instead of retraining",
    )
    p_thresh.add_argument(
        "--spec", default=None,
        help="Path to feature_spec.json to reuse instead of rebuilding vocab",
    )
    _add_workers_arg(p_thresh)

    # benchmark
    p_bench = subparsers.add_parser("benchmark", help="Benchmark extraction, training, and inference")
    p_bench.add_argument("--db", required=True, help="Path to cyclotron SQLite database")
    p_bench.add_argument("--model", default=None, help="Optional trained XGBoost model (.json)")
    p_bench.add_argument("--spec", default=None, help="Optional feature_spec.json")
    p_bench.add_argument("--output", default=None, help="Optional JSON output path")
    _add_workers_arg(p_bench)

    # experiment
    p_exp = subparsers.add_parser(
        "experiment", help="Run a fast subsampled experiment on the full external test bucket",
    )
    p_exp.add_argument("--db", required=True, help="Path to cyclotron SQLite database")
    p_exp.add_argument(
        "--train-samples", type=int, default=10_000,
        help="Approximate sampled training rows (default: 10000)",
    )
    p_exp.add_argument("--n-folds", type=int, default=2, help="CV folds for the experiment")
    p_exp.add_argument("--n-estimators", type=int, default=120, help="Max trees for the experiment")
    p_exp.add_argument("--max-depth", type=int, default=5, help="Tree depth for the experiment")
    p_exp.add_argument(
        "--learning-rate", type=float, default=0.05, help="Learning rate for the experiment",
    )
    p_exp.add_argument(
        "--early-stopping-rounds", type=int, default=12,
        help="Early stopping rounds for the experiment",
    )
    _add_workers_arg(p_exp)
    _add_seed_arg(p_exp)

    # ablation
    p_ablate = subparsers.add_parser("ablate", help="Run leave-one-group-out feature ablations")
    p_ablate.add_argument("--db", required=True, help="Path to cyclotron SQLite database")
    p_ablate.add_argument(
        "--groups",
        nargs="*",
        choices=list(features.FEATURE_GROUPS),
        default=None,
        help="Optional subset of feature groups to ablate",
    )
    p_ablate.add_argument("--output", default=None, help="Optional JSON output path")
    _add_workers_arg(p_ablate)
    _add_seed_arg(p_ablate)

    # demo-db
    p_demo = subparsers.add_parser("demo-db", help="Create a small synthetic cyclotron database")
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
            db_path=Path(args.db),
            model_path=Path(args.model),
            spec_path=Path(args.spec),
        )
    elif args.command == "errors":
        inspect.inspect_errors(
            db_path=Path(args.db),
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
    elif args.command == "fixture":
        cmd_fixture(args)
    elif args.command == "traits":
        traits.analyze_traits(
            db_path=Path(args.db),
            crit=None if args.crit == "any" else args.crit,
            min_samples=args.min_samples,
            sort_by=args.sort,
            top_n=args.top,
            output_path=Path(args.output) if args.output else None,
        )
    elif args.command == "thresholds":
        thresholds.show_thresholds(
            db_path=Path(args.db),
            model_path=Path(args.model) if args.model else None,
            spec_path=Path(args.spec) if args.spec else None,
            n_workers=args.workers,
        )
    elif args.command == "benchmark":
        benchmark.run_benchmark(
            db_path=Path(args.db),
            n_workers=args.workers,
            model_path=Path(args.model) if args.model else None,
            spec_path=Path(args.spec) if args.spec else None,
            output_path=Path(args.output) if args.output else None,
        )
    elif args.command == "experiment":
        experiment.run_experiment(
            db_path=Path(args.db),
            n_workers=args.workers,
            seed=args.seed,
            train_samples=args.train_samples,
            n_folds=args.n_folds,
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            learning_rate=args.learning_rate,
            early_stopping_rounds=args.early_stopping_rounds,
        )
    elif args.command == "ablate":
        rows = ablation.run_ablation(
            db_path=Path(args.db),
            n_workers=args.workers,
            seed=args.seed,
            groups=args.groups,
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
