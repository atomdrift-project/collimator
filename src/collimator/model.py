"""XGBoost model for binary malware classification.

Gradient-boosted trees are the right model for this data:
- Sparse binary features (path×tier combos) → trees split directly on them
- Feature interactions learned natively (one split per feature per tree)
- Handles class imbalance via scale_pos_weight
- No need for feature standardization (kept for pipeline compatibility)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
import xgboost as xgb

log = logging.getLogger(__name__)

_device_cache: str | None = None


def _booster_device(model: xgb.XGBClassifier) -> str:
    """Read the effective device from a fitted booster config."""
    try:
        cfg = json.loads(model.get_booster().save_config())
        return str(cfg["learner"]["generic_param"].get("device", "cpu"))
    except Exception:
        return "cpu"


def detect_device() -> str:
    """Return the device XGBoost can actually use for training."""
    global _device_cache
    if _device_cache is not None:
        return _device_cache
    try:
        X = np.zeros((8, 1), dtype=np.float32)
        y = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.float32)
        dmat = xgb.DMatrix(X, label=y)
        booster = xgb.train(
            {"tree_method": "hist", "device": "cuda", "objective": "binary:logistic"},
            dmat,
            num_boost_round=1,
        )
        cfg = json.loads(booster.save_config())
        _device_cache = cfg["learner"]["generic_param"].get("device", "cpu")
    except Exception:
        _device_cache = "cpu"
    log.info("xgboost device: %s", _device_cache)
    return _device_cache


def create_classifier(
    n_benign: int,
    n_malware: int,
    *,
    device: str | None = None,
    random_state: int = 42,
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
        random_state=random_state,
        early_stopping_rounds=early_stopping_rounds,
    )


def load_model(model_path: Path) -> xgb.XGBClassifier:
    """Load an XGBoost model from native JSON format."""
    model = xgb.XGBClassifier()
    model.load_model(str(model_path))
    return model


def predict_proba(model: xgb.XGBClassifier, X: np.ndarray) -> np.ndarray:
    """Return malware probability for each sample."""
    # Use inplace_predict with the fitted best_iteration to preserve early
    # stopping semantics without triggering the sklearn wrapper's CPU/GPU
    # fallback warning on CPU-resident inputs.
    booster = model.get_booster()
    best_iteration = getattr(model, "best_iteration", None)
    iteration_range = (0, best_iteration + 1) if best_iteration is not None else (0, 0)
    probs = booster.inplace_predict(
        X,
        iteration_range=iteration_range,
        predict_type="value",
        validate_features=False,
    )
    probs = np.asarray(probs, dtype=np.float32)
    if probs.ndim != 1:
        raise ValueError(f"unexpected predict_proba output shape: {probs.shape}")
    return probs
