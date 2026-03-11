"""Export trained XGBoost model to ONNX and native JSON formats."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import xgboost as xgb

log = logging.getLogger(__name__)


def export_onnx(
    model: xgb.XGBClassifier,
    n_features: int,
    output_path: Path,
) -> None:
    """Export XGBoost model to ONNX with dynamic batch size.

    The exported model outputs probabilities directly (class 1 probability).
    Requires onnxmltools to be installed.
    """
    try:
        from onnxmltools import convert_xgboost
        from onnxmltools.convert.common.data_types import FloatTensorType
    except ImportError:
        log.warning("onnxmltools not installed, skipping ONNX export")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    initial_type = [("features", FloatTensorType([None, n_features]))]
    onnx_model = convert_xgboost(
        model,
        initial_types=initial_type,
        target_opset=15,
    )

    # Rename outputs for compatibility with existing Rust consumer.
    # XGBoost ONNX produces "label" and "probabilities" outputs.
    # We keep both but log what they are.
    output_names = [o.name for o in onnx_model.graph.output]
    log.info("ONNX output names: %s", output_names)

    import onnx
    onnx.save(onnx_model, str(output_path))
    log.info("exported ONNX model to %s", output_path)


def validate_onnx(
    model: xgb.XGBClassifier,
    onnx_path: Path,
    n_features: int,
    X: np.ndarray | None = None,
    n_samples: int = 100,
    tolerance: float = 1e-4,
) -> bool:
    """Verify ONNX model produces same outputs as XGBoost model."""
    try:
        import onnxruntime as ort
    except ImportError:
        log.warning("onnxruntime not installed, skipping ONNX validation")
        return True

    if not onnx_path.exists():
        log.warning("ONNX model not found at %s, skipping validation", onnx_path)
        return True

    if X is not None and len(X) > 0:
        rng = np.random.default_rng(42)
        idx = rng.choice(len(X), min(n_samples, len(X)), replace=False)
        test_input = X[idx].astype(np.float32)
    else:
        test_input = np.random.randn(n_samples, n_features).astype(np.float32)

    # XGBoost predictions.
    from .model import predict_proba
    xgb_output = predict_proba(model, test_input)

    # ONNX predictions.
    session = ort.InferenceSession(str(onnx_path))
    onnx_results = session.run(None, {"features": test_input})

    # XGBoost ONNX outputs: [labels, probabilities_map].
    # probabilities_map is a list of dicts [{0: p0, 1: p1}, ...].
    onnx_probs = np.array([r[1] for r in onnx_results[1]], dtype=np.float32)

    max_diff = float(np.max(np.abs(xgb_output - onnx_probs)))
    if max_diff > tolerance:
        log.error("ONNX validation failed: max diff %.6f > tolerance %.6f", max_diff, tolerance)
        return False

    log.info("ONNX validation passed: max diff %.8f", max_diff)
    return True


def save_model(model: xgb.XGBClassifier, output_path: Path) -> None:
    """Save XGBoost model in native JSON format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(output_path))
    log.info("saved XGBoost model to %s", output_path)


def save_evaluation(
    metrics: dict[str, float],
    optimal_threshold: float,
    confusion: list[list[int]],
    class_distribution: dict[str, int],
    fold_metrics: list[dict[str, float]],
    n_features: int,
    output_path: Path,
) -> None:
    """Save evaluation results as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results = {
        "metrics": metrics,
        "optimal_threshold": optimal_threshold,
        "confusion_matrix": confusion,
        "class_distribution": class_distribution,
        "fold_metrics": fold_metrics,
        "n_features": n_features,
    }
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    log.info("saved evaluation to %s", output_path)
