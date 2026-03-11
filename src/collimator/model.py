"""XGBoost model for binary malware classification.

Gradient-boosted trees are the right model for this data:
- Sparse binary features (path×tier combos) → trees split directly on them
- Feature interactions learned natively (one split per feature per tree)
- Handles class imbalance via scale_pos_weight
- No need for feature standardization (kept for pipeline compatibility)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import xgboost as xgb


def create_classifier(
    n_benign: int,
    n_malware: int,
    *,
    n_estimators: int = 1000,
    max_depth: int = 6,
    learning_rate: float = 0.05,
    early_stopping_rounds: int = 30,
) -> xgb.XGBClassifier:
    """Create an XGBoost classifier with defaults tuned for malware detection."""
    return xgb.XGBClassifier(
        objective="binary:logistic",
        eval_metric="aucpr",
        max_depth=max_depth,
        learning_rate=learning_rate,
        n_estimators=n_estimators,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=5,
        scale_pos_weight=n_benign / max(n_malware, 1),
        tree_method="hist",
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
