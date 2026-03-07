"""CLI entry point for collimator training pipeline."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import torch

from . import data, explain, export, features, inspect, train, traits
from .model import MalwareClassifier


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

    # Load samples.
    samples = data.load_samples(db_path)
    if len(samples) < 10:
        print(f"ERROR: only {len(samples)} samples, need at least 10")
        sys.exit(1)

    # Build vocabulary and extract features.
    reports = [s.report for s in samples]
    labels = [s.label for s in samples]
    spec = features.build_vocab(reports)
    X, y = features.extract_all(reports, labels, spec)

    # Detect device. MPS is skipped — it has numerical stability issues
    # with BatchNorm under extreme class imbalance, and our model is small
    # enough that CPU is comparable speed.
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Train.
    config = train.TrainConfig(device=device)
    result = train.train(X, y, config)

    # Attach standardization params to spec before saving.
    spec.feature_means = result.feature_means
    spec.feature_stds = result.feature_stds

    # Export.
    spec.save(out_dir / "feature_spec.json")
    export.export_onnx(result.model, spec.total_features, out_dir / "model.onnx")
    export.save_pytorch(result.model, out_dir / "model.pt")
    export.save_evaluation(
        metrics=result.metrics,
        optimal_threshold=result.optimal_threshold,
        confusion=result.confusion,
        class_distribution=result.class_distribution,
        fold_metrics=result.fold_metrics,
        n_features=spec.total_features,
        output_path=out_dir / "evaluation.json",
    )

    # Standardize feature data for ONNX validation and SHAP.
    X_std = features.standardize(X, spec)

    # Validate ONNX.
    if not export.validate_onnx(
        result.model, out_dir / "model.onnx", spec.total_features, X=X_std,
    ):
        print("WARNING: ONNX validation failed")
        sys.exit(1)

    # SHAP analysis on standardized data.
    explain.compute_shap_importance(
        result.model, X_std, spec,
        output_path=out_dir / "shap_importance.json",
    )

    print(f"\nOutput files in {out_dir}/:")
    for f in sorted(out_dir.iterdir()):
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

    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    y_binary = (predictions > 0.5).astype(int)
    print(f"\nEvaluation on {len(y)} samples:")
    print(f"  Accuracy:  {accuracy_score(y, y_binary):.4f}")
    print(f"  Precision: {precision_score(y, y_binary, zero_division=0):.4f}")
    print(f"  Recall:    {recall_score(y, y_binary, zero_division=0):.4f}")
    print(f"  F1:        {f1_score(y, y_binary, zero_division=0):.4f}")
    if len(set(y)) > 1:
        print(f"  ROC AUC:   {roc_auc_score(y, predictions):.4f}")


def cmd_explain(args: argparse.Namespace) -> None:
    """Run SHAP analysis on a trained model."""
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

    model = MalwareClassifier(spec.total_features)
    model.load_state_dict(torch.load(model_path, weights_only=True))

    explain.compute_shap_importance(
        model, X, spec,
        output_path=out_dir / "shap_importance.json",
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

    # explain
    p_explain = subparsers.add_parser("explain", help="SHAP feature importance analysis")
    p_explain.add_argument("--db", required=True, help="Path to cyclotron SQLite database")
    p_explain.add_argument("--model", required=True, help="Path to PyTorch model (.pt)")
    p_explain.add_argument("--spec", required=True, help="Path to feature_spec.json")
    p_explain.add_argument("--output", default="out", help="Output directory")

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect a single sample from the DB")
    p_inspect.add_argument("--db", required=True, help="Path to cyclotron SQLite database")
    p_inspect.add_argument("--sample", required=True, help="SHA256 (or prefix) of sample")
    p_inspect.add_argument("--model", default="out/model.pt", help="Path to PyTorch model")
    p_inspect.add_argument(
        "--spec", default="out/feature_spec.json", help="Path to feature_spec.json",
    )

    # errors
    p_errors = subparsers.add_parser("errors", help="Show misclassified samples")
    p_errors.add_argument("--db", required=True, help="Path to cyclotron SQLite database")
    p_errors.add_argument("--model", default="out/model.pt", help="Path to PyTorch model")
    p_errors.add_argument(
        "--spec", default="out/feature_spec.json", help="Path to feature_spec.json",
    )
    p_errors.add_argument("--top", type=int, default=20, help="Number of errors to show")

    # scan
    p_scan = subparsers.add_parser("scan", help="Score a live file using cleave + model")
    p_scan.add_argument("file", help="Path to file to scan")
    p_scan.add_argument("--model", default="out/model.pt", help="Path to PyTorch model")
    p_scan.add_argument("--spec", default="out/feature_spec.json", help="Path to feature_spec.json")
    p_scan.add_argument("--cleave", default="cleave", help="Path to cleave binary")
    p_scan.add_argument("--db", default=None, help="Background DB for SHAP context (optional)")

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
    elif args.command == "traits":
        traits.analyze_traits(
            db_path=Path(args.db),
            crit=None if args.crit == "any" else args.crit,
            min_samples=args.min_samples,
            sort_by=args.sort,
            top_n=args.top,
            output_path=Path(args.output) if args.output else None,
        )


if __name__ == "__main__":
    main()
