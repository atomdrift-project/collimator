"""Export trained PyTorch model to ONNX format for Rust inference."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import onnx
import torch

from .model import MalwareClassifier

log = logging.getLogger(__name__)


class _ModelWithSigmoid(torch.nn.Module):
    """Wraps a logit-output model with sigmoid for ONNX export."""

    def __init__(self, model: MalwareClassifier) -> None:
        super().__init__()
        self.model = model

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.sigmoid(self.model(x))


def export_onnx(
    model: MalwareClassifier,
    n_features: int,
    output_path: Path,
) -> None:
    """Export model to ONNX with dynamic batch size.

    The exported model includes a final sigmoid so ONNX consumers
    (e.g. Rust/ort) receive probabilities directly.
    """
    # Clone to CPU for export — don't mutate the caller's model.
    cpu_model = MalwareClassifier(n_features)
    cpu_model.load_state_dict(model.state_dict())
    cpu_model.eval()
    wrapper = _ModelWithSigmoid(cpu_model)
    wrapper.eval()
    dummy = torch.randn(1, n_features)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        wrapper,
        dummy,
        str(output_path),
        input_names=["features"],
        output_names=["probability"],
        dynamic_axes={
            "features": {0: "batch_size"},
            "probability": {0: "batch_size"},
        },
        opset_version=17,
    )
    log.info("exported ONNX model to %s", output_path)


def validate_onnx(
    model: MalwareClassifier,
    onnx_path: Path,
    n_features: int,
    X: np.ndarray | None = None,
    n_samples: int = 100,
    tolerance: float = 1e-5,
) -> bool:
    """Verify ONNX model produces same outputs as PyTorch model.

    If X is provided, a subsample of real (standardized) feature data is used
    instead of random noise, exercising realistic activation patterns.
    """
    try:
        import onnxruntime as ort
    except ImportError:
        log.warning("onnxruntime not installed, skipping ONNX validation")
        return True

    onnx_model = onnx.load(str(onnx_path))
    onnx.checker.check_model(onnx_model)

    cpu_model = MalwareClassifier(n_features)
    cpu_model.load_state_dict(model.state_dict())
    cpu_model.eval()

    if X is not None and len(X) > 0:
        rng = np.random.default_rng(42)
        idx = rng.choice(len(X), min(n_samples, len(X)), replace=False)
        test_input = X[idx].astype(np.float32)
    else:
        test_input = np.random.randn(n_samples, n_features).astype(np.float32)

    with torch.no_grad():
        pt_output = torch.sigmoid(cpu_model(torch.tensor(test_input))).numpy()

    session = ort.InferenceSession(str(onnx_path))
    onnx_output = session.run(None, {"features": test_input})[0]

    max_diff = float(np.max(np.abs(pt_output - onnx_output)))
    if max_diff > tolerance:
        log.error("ONNX validation failed: max diff %.6f > tolerance %.6f", max_diff, tolerance)
        return False

    log.info("ONNX validation passed: max diff %.8f", max_diff)
    return True


def save_pytorch(model: MalwareClassifier, output_path: Path) -> None:
    """Save PyTorch model state dict (for SHAP / further training)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), output_path)
    log.info("saved PyTorch model to %s", output_path)


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
