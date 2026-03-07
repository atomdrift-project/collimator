"""SHAP-based model explainability."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import shap
import torch

from .features import FeatureSpec
from .model import MalwareClassifier

log = logging.getLogger(__name__)

# Maximum samples for SHAP.
MAX_BACKGROUND = 50
MAX_EXPLAIN = 50


def compute_shap_importance(
    model: MalwareClassifier,
    X: np.ndarray,
    spec: FeatureSpec,
    output_path: Path | None = None,
) -> dict[str, float]:
    """Compute global SHAP feature importance.

    Returns a dict mapping feature name → mean |SHAP value|, sorted descending.
    """
    model.eval().cpu()

    # Use kmeans to summarize background — much more efficient than raw
    # samples for KernelExplainer, and avoids numerical issues.
    n_bg = min(MAX_BACKGROUND, len(X))
    background = shap.kmeans(X, min(n_bg, 50))

    if len(X) > MAX_EXPLAIN:
        rng = np.random.default_rng(42)
        ex_idx = rng.choice(len(X), MAX_EXPLAIN, replace=False)
        X_explain = X[ex_idx]
    else:
        X_explain = X

    def predict_fn(x: np.ndarray) -> np.ndarray:
        with torch.no_grad():
            t = torch.tensor(x, dtype=torch.float32)
            return torch.sigmoid(model(t)).numpy()

    explainer = shap.KernelExplainer(predict_fn, background)
    # nsamples="auto" lets SHAP pick based on feature count.
    # Suppress verbose SHAP logging.
    shap_logger = logging.getLogger("shap")
    prev_level = shap_logger.level
    shap_logger.setLevel(logging.WARNING)
    try:
        shap_values = explainer.shap_values(X_explain, nsamples="auto")
    finally:
        shap_logger.setLevel(prev_level)

    # shap_values may be a list (one per output) or array.
    if isinstance(shap_values, list):
        shap_values = shap_values[0]
    shap_arr = np.array(shap_values)

    # Squeeze extra dimensions and replace NaN.
    shap_arr = np.nan_to_num(shap_arr.squeeze(), nan=0.0)
    if shap_arr.ndim == 1:
        shap_arr = shap_arr.reshape(1, -1)

    mean_abs = np.abs(shap_arr).mean(axis=0)
    sorted_idx = np.argsort(mean_abs)[::-1].tolist()

    print("\nTop 30 Features by SHAP Importance:")
    print(f"{'Rank':<6} {'Feature':<50} {'Importance':>12}")
    print(f"{'-' * 68}")
    for rank, idx in enumerate(sorted_idx[:30]):
        name = spec.feature_names[idx] if idx < len(spec.feature_names) else f"feature_{idx}"
        print(f"{rank + 1:<6} {name:<50} {mean_abs[idx]:>12.6f}")

    useless = int(np.sum(mean_abs < 0.001))
    if useless > 0:
        print(f"\n{useless} features have SHAP importance < 0.001")

    importance: dict[str, float] = {}
    for idx in sorted_idx:
        name = spec.feature_names[idx] if idx < len(spec.feature_names) else f"feature_{idx}"
        importance[name] = float(mean_abs[idx])

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        top_50 = [
            {"name": spec.feature_names[idx], "importance": float(mean_abs[idx])}
            for idx in sorted_idx[:50]
            if idx < len(spec.feature_names)
        ]
        with open(output_path, "w") as f:
            json.dump({
                "top_features": top_50,
                "useless_feature_count": useless,
                "total_features": len(mean_abs),
            }, f, indent=2)
        log.info("saved SHAP importance to %s", output_path)

    return importance
