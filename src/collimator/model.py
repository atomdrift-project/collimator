"""XGBoost model for binary malware classification.

Gradient-boosted trees are the right model for this data:
- Sparse binary features (path×tier combos) → trees split directly on them
- Feature interactions learned natively (one split per feature per tree)
- Handles class imbalance via scale_pos_weight
- No need for feature standardization (kept for pipeline compatibility)
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import xgboost as xgb

log = logging.getLogger(__name__)

_device_cache: str | None = None


def detect_device() -> str:
    """Return 'cuda' if XGBoost GPU support is available, else 'cpu'."""
    global _device_cache
    if _device_cache is not None:
        return _device_cache
    try:
        dmat = xgb.DMatrix(np.zeros((1, 1), dtype=np.float32))
        xgb.Booster({"device": "cuda"}, [dmat])
        _device_cache = "cuda"
    except xgb.core.XGBoostError:
        _device_cache = "cpu"
    log.info("xgboost device: %s", _device_cache)
    return _device_cache


def create_classifier(
    n_benign: int,
    n_malware: int,
    *,
    device: str | None = None,
    n_estimators: int = 1000,
    max_depth: int = 6,
    learning_rate: float = 0.05,
    early_stopping_rounds: int = 30,
    min_child_weight: int = 5,
    colsample_bytree: float = 0.8,
    subsample: float = 0.8,
    gamma: float = 0.0,
    reg_alpha: float = 0.0,
    reg_lambda: float = 1.0,
) -> xgb.XGBClassifier:
    """Create an XGBoost classifier with defaults tuned for malware detection."""
    if device is None:
        device = detect_device()
    return xgb.XGBClassifier(
        objective="binary:logistic",
        eval_metric="aucpr",
        max_depth=max_depth,
        learning_rate=learning_rate,
        n_estimators=n_estimators,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        min_child_weight=min_child_weight,
        gamma=gamma,
        reg_alpha=reg_alpha,
        reg_lambda=reg_lambda,
        scale_pos_weight=n_benign / max(n_malware, 1),
        tree_method="hist",
        device=device,
        random_state=42,
        early_stopping_rounds=early_stopping_rounds,
    )


def load_model(model_path: Path) -> xgb.XGBClassifier:
    """Load an XGBoost model from native JSON format."""
    model = xgb.XGBClassifier()
    model.load_model(str(model_path))
    return model


def predict_proba(model: xgb.XGBClassifier, X: np.ndarray) -> np.ndarray:
    """Return malware probability for each sample."""
    proba = model.predict_proba(X)
    return proba[:, 1] if proba.ndim > 1 else proba
