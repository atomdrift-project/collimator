"""Regression tests for probability prediction with early stopping."""

from __future__ import annotations

import numpy as np

from collimator.model import create_classifier, predict_proba


def test_predict_proba_matches_sklearn_wrapper_with_early_stopping() -> None:
    rng = np.random.default_rng(0)
    X = rng.integers(0, 2, size=(2000, 20), dtype=np.int32).astype(np.float32)
    y = ((X[:, 0] + X[:, 1] * 2 + X[:, 2] * 3) > 2).astype(np.int32)

    model = create_classifier(
        int((y == 0).sum()),
        int((y == 1).sum()),
        device="cpu",
        n_estimators=50,
        early_stopping_rounds=5,
    )
    model.fit(X[:1500], y[:1500], eval_set=[(X[1500:], y[1500:])], verbose=False)

    X_test = X[:64]
    expected = model.predict_proba(X_test)[:, 1]
    actual = predict_proba(model, X_test)
    np.testing.assert_allclose(actual, expected)
