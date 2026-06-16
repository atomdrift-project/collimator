"""SHAP-based model explainability."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import shap

from .features import FeatureSpec

log = logging.getLogger(__name__)

# Maximum samples for SHAP analysis.
MAX_EXPLAIN = 200


def feature_names_digest(feature_names: list[str]) -> str:
    """Stable SHA-256 over the ordered feature-name list. Stamped into
    shap_importance.json as provenance: a SHAP file is only valid for the exact
    feature space it was computed against, so a consumer (e.g. ascan) can hash
    the model it loaded and refuse a SHAP file whose digest differs — catching a
    stale SHAP that no longer matches the model. The newline join can't collide
    across lists since feature names never contain newlines."""
    return hashlib.sha256("\n".join(feature_names).encode("utf-8")).hexdigest()


def _tree_shap_values(model: Any, X: np.ndarray) -> np.ndarray:
    """Per-sample SHAP matrix (n_samples x n_features) for a tree model.

    Both LightGBM and XGBoost expose native per-prediction feature
    contributions whose final column is the bias / expected-value term, so we
    slice it off to get pure per-feature SHAP. SHAP's own TreeExplainer is the
    portable fallback when neither native path applies.
    """
    module = type(model).__module__
    # LightGBM (raw Booster or the sklearn wrapper). `pred_contrib=True` is
    # exact and skips the shap library entirely. This path is what the LightGBM
    # migration left unhandled: the old code only knew `xgboost.get_booster()`,
    # which a lightgbm.Booster doesn't have, so SHAP silently stopped working.
    if module.startswith("lightgbm"):
        booster = getattr(model, "booster_", model)
        contribs = np.asarray(booster.predict(X, pred_contrib=True))
        return contribs[:, :-1]
    # XGBoost: native pred_contribs, on the GPU when the model lives there.
    try:
        import xgboost as xgb  # noqa: PLC0415 — optional dep, lazy

        from .model import detect_device  # noqa: PLC0415
        try:
            dmat = xgb.DMatrix(X, device=detect_device())
        except Exception:
            dmat = xgb.DMatrix(X)
        booster = model.get_booster()
        best_iteration = getattr(model, "best_iteration", None)
        iteration_range = (0, best_iteration + 1) if best_iteration is not None else (0, 0)
        contribs = booster.predict(dmat, pred_contribs=True, iteration_range=iteration_range)
        return contribs[:, :-1]  # last column is the bias term
    except Exception as exc:
        log.warning("native pred_contribs failed (%s); falling back to shap library", exc)
        explainer = shap.TreeExplainer(model)
        return np.asarray(explainer.shap_values(X))


def compute_shap_importance(
    model: Any,
    X: np.ndarray,
    spec: FeatureSpec,
    output_path: Path | None = None,
) -> dict[str, float]:
    """Compute global SHAP feature importance using exact tree contributions.

    TreeExplainer / native pred_contrib is exact for tree models (no sampling
    approximation needed) and dramatically faster than KernelExplainer. Works
    for both LightGBM and XGBoost models.
    """
    if len(X) > MAX_EXPLAIN:
        rng = np.random.default_rng(42)
        ex_idx = rng.choice(len(X), MAX_EXPLAIN, replace=False)
        X_explain = X[ex_idx]
    else:
        X_explain = X

    shap_values = _tree_shap_values(model, X_explain)

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
        significant = [
            spec.feature_names[idx]
            for idx in sorted_idx
            if idx < len(spec.feature_names) and mean_abs[idx] >= 0.001
        ]
        with open(output_path, "w") as f:
            json.dump({
                # Provenance: ties this SHAP to the exact feature space it was
                # computed against, so a stale file can be detected on load.
                "feature_names_sha256": feature_names_digest(spec.feature_names),
                "feature_count": len(spec.feature_names),
                "top_features": top_50,
                "significant_features": significant,
                "useless_feature_count": useless,
                "total_features": len(mean_abs),
            }, f, indent=2)
        log.info("saved SHAP importance to %s", output_path)

    return importance
