"""SHAP-based model explainability."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import shap
import xgboost as xgb

from .features import FeatureSpec

log = logging.getLogger(__name__)

# Maximum samples for SHAP analysis.
MAX_EXPLAIN = 200


def compute_shap_importance(
    model: xgb.XGBClassifier,
    X: np.ndarray,
    spec: FeatureSpec,
    output_path: Path | None = None,
) -> dict[str, float]:
    """Compute global SHAP feature importance using TreeExplainer.

    TreeExplainer is exact for tree models (no sampling approximation needed)
    and dramatically faster than KernelExplainer.
    """
    if len(X) > MAX_EXPLAIN:
        rng = np.random.default_rng(42)
        ex_idx = rng.choice(len(X), MAX_EXPLAIN, replace=False)
        X_explain = X[ex_idx]
    else:
        X_explain = X

    # Prefer XGBoost's native pred_contribs, which runs on the GPU when the
    # model is on CUDA and avoids the shap library overhead entirely.
    # Falls back to shap.TreeExplainer (CPU) if anything goes wrong.
    try:
        from .model import detect_device
        device = detect_device()
        try:
            dmat = xgb.DMatrix(X_explain, device=device)
        except Exception:
            dmat = xgb.DMatrix(X_explain)
        contribs = model.get_booster().predict(dmat, pred_contribs=True)
        shap_values = contribs[:, :-1]  # last column is the bias term
    except Exception as exc:
        log.warning("native pred_contribs failed (%s); falling back to shap library", exc)
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_explain)

    shap_arr = np.nan_to_num(np.array(shap_values).squeeze(), nan=0.0)
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
