"""Export trained XGBoost model to ONNX and native JSON formats."""

from __future__ import annotations

from datetime import datetime
import json
import logging
import platform
from pathlib import Path

import numpy as np
import xgboost as xgb

log = logging.getLogger(__name__)


def load_evaluation(path: Path) -> dict[str, object]:
    """Load evaluation metadata from JSON."""
    with open(path) as f:
        return json.load(f)


def load_threshold(path: Path, default: float = 0.5) -> float:
    """Load the calibrated threshold from an evaluation artifact."""
    try:
        data = load_evaluation(path)
    except (OSError, json.JSONDecodeError):
        return default
    return float(data.get("optimal_threshold", default))


def predict_onnx_proba(session: object, X: np.ndarray) -> np.ndarray:
    """Run ONNX inference and return class-1 probabilities as a 1D array."""
    results = session.run(None, {"features": X})
    n_rows = len(X)

    def _as_probability_vector(value: object) -> np.ndarray | None:
        if isinstance(value, list) and len(value) == n_rows and value:
            first = value[0]
            if isinstance(first, dict):
                return np.array(
                    [row.get(1, row.get("1", 0.0)) for row in value],
                    dtype=np.float32,
                )

        arr = np.asarray(value)
        if arr.ndim == 2 and arr.shape[0] == n_rows and arr.shape[1] >= 2:
            return arr[:, 1].astype(np.float32, copy=False)
        if arr.ndim == 1 and arr.shape[0] == n_rows:
            if np.issubdtype(arr.dtype, np.floating):
                return arr.astype(np.float32, copy=False)
        return None

    output_names = [out.name.lower() for out in session.get_outputs()]
    for name, value in zip(output_names, results):
        if "prob" in name:
            probs = _as_probability_vector(value)
            if probs is not None:
                return probs

    for value in results:
        probs = _as_probability_vector(value)
        if probs is not None and not np.array_equal(probs, probs.astype(np.int32)):
            return probs

    raise ValueError("could not locate probability output in ONNX results")


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
    onnx_probs = predict_onnx_proba(session, test_input)

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
    calibration: dict[str, object],
    optimal_threshold: float,
    confusion: list[list[int]],
    class_distribution: dict[str, int],
    split_summary: dict[str, int | str],
    fold_metrics: list[dict[str, float]],
    n_features: int,
    experiment: dict[str, object],
    output_path: Path,
) -> None:
    """Save evaluation results as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results = {
        "metrics": metrics,
        "calibration": calibration,
        "optimal_threshold": optimal_threshold,
        "confusion_matrix": confusion,
        "class_distribution": class_distribution,
        "split_summary": split_summary,
        "fold_metrics": fold_metrics,
        "n_features": n_features,
        "experiment": experiment,
        "environment": {
            "python": platform.python_version(),
            "xgboost": xgb.__version__,
            "numpy": np.__version__,
        },
    }
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    log.info("saved evaluation to %s", output_path)


def save_run_summary(
    *,
    kind: str,
    payload: dict[str, object],
    output_dir: Path,
) -> Path:
    """Save a timestamped run summary JSON for posterity."""
    runs_dir = output_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    output_path = runs_dir / f"{timestamp}-{kind}.json"
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2)
    log.info("saved %s run summary to %s", kind, output_path)
    return output_path
