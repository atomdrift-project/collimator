"""CLI entry point for collimator training pipeline."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np

from . import data, explain, export, features, inspect, thresholds, train, traits


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-5s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def cmd_train(args: argparse.Namespace) -> None:
    """Train a model and export to ONNX."""
    db_path = Path(args.db)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load samples, excluding the deterministic test set.
    all_samples = data.load_samples(db_path)
    samples, test_samples = data.split_train_test(all_samples)
    if len(samples) < 10:
        print(f"ERROR: only {len(samples)} training samples, need at least 10")
        sys.exit(1)

    # Build vocabulary and extract features.
    reports = [s.report for s in samples]
    labels = [s.label for s in samples]
    spec = features.build_vocab(reports)
    X, y = features.extract_all(reports, labels, spec)

    # Train.
    config = train.TrainConfig()
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
        optimal_threshold=result.optimal_threshold,
        confusion=result.confusion,
        class_distribution=result.class_distribution,
        fold_metrics=result.fold_metrics,
        n_features=spec.total_features,
        output_path=out_dir / "evaluation.json",
    )

    # Post-training steps only need small dense subsets — avoid densifying
    # the full sparse matrix to keep memory low.
    rng = np.random.default_rng(42)

    # Validate ONNX (100 samples).
    onnx_idx = rng.choice(X.shape[0], min(100, X.shape[0]), replace=False)
    if not export.validate_onnx(
        result.model, out_dir / "model.onnx", spec.total_features,
        X=features.standardize(X[onnx_idx], spec),
    ):
        print("WARNING: ONNX validation failed")
        sys.exit(1)

    # SHAP analysis (200 samples).
    shap_idx = rng.choice(X.shape[0], min(200, X.shape[0]), replace=False)
    explain.compute_shap_importance(
        result.model, features.standardize(X[shap_idx], spec), spec,
        output_path=out_dir / "shap_importance.json",
    )

    # Cross-language test fixtures (10 samples).
    fix_idx = rng.choice(X.shape[0], min(10, X.shape[0]), replace=False)
    fix_idx.sort()
    generate_fixtures(
        result.model, spec,
        X[fix_idx].toarray(), features.standardize(X[fix_idx], spec),
        out_dir,
    )

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

    samples = data.load_samples(db_path)
    spec = features.FeatureSpec.load(spec_path)
    reports = [s.report for s in samples]
    labels = [s.label for s in samples]
    X, y = features.extract_all(reports, labels, spec)
    X = features.standardize(X, spec)

    try:
        import onnxruntime as ort
    except ImportError:
        print("ERROR: onnxruntime required for evaluation")
        sys.exit(1)

    session = ort.InferenceSession(str(model_path))
    predictions = session.run(None, {"features": X})[0].squeeze()

    # Use optimal threshold from training if available.
    threshold = 0.5
    if args.eval_json:
        eval_json_path = Path(args.eval_json)
    else:
        eval_json_path = model_path.parent / "evaluation.json"
    if eval_json_path.exists():
        import json as _json
        with open(eval_json_path) as f:
            eval_data = _json.load(f)
        threshold = eval_data.get("optimal_threshold", 0.5)
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


def cmd_explain(args: argparse.Namespace) -> None:
    """Run SHAP analysis on a trained model."""
    from .model import load_model

    db_path = Path(args.db)
    spec_path = Path(args.spec)
    model_path = Path(args.model)
    out_dir = Path(args.output)

    samples = data.load_samples(db_path)
    spec = features.FeatureSpec.load(spec_path)
    reports = [s.report for s in samples]
    labels = [s.label for s in samples]
    X, y = features.extract_all(reports, labels, spec)
    X = features.standardize(X, spec)

    model = load_model(model_path)

    explain.compute_shap_importance(
        model, X, spec,
        output_path=out_dir / "shap_importance.json",
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

    generate_fixtures(
        model, spec,
        X[idx].toarray(), features.standardize(X[idx], spec),
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
        thresholds.show_thresholds(db_path=Path(args.db))


if __name__ == "__main__":
    main()
