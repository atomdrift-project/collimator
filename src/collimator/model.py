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
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import xgboost as xgb

log = logging.getLogger(__name__)

_device_cache: str | None = None


def booster_device(model: xgb.XGBClassifier) -> str:
    """Read the effective device from a fitted booster config."""
    if model.__class__.__module__.startswith("lightgbm"):
        params = getattr(model, "get_params", lambda: {})()
        return str(params.get("device_type") or params.get("device") or "cpu")
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


def pick_device(
    n_rows: int | None = None,
    n_features: int | None = None,
    nnz: int | None = None,
) -> str:
    """Pick CUDA vs CPU based on the training-set shape.

    LightGBM's CUDA path — and to a lesser extent XGBoost's — only accelerates
    dense, large-N data. Sparse high-dim inputs trigger numeric instability on
    GPU (constant-prediction models, SIGFPE inside fit). Bias toward CPU and
    only opt into CUDA when the workload looks GPU-friendly.
    """
    if not detect_device().startswith("cuda"):
        return "cpu"
    if n_rows is None or n_features is None:
        return "cpu"
    cells = n_rows * n_features
    density = (nnz / cells) if nnz is not None and cells else 1.0
    if density < 0.05:
        log.info("device=cpu (sparse: %.3f%% density)", density * 100)
        return "cpu"
    if n_rows < 50_000:
        log.info("device=cpu (small: %d rows)", n_rows)
        return "cpu"
    if n_features > 20_000:
        log.info("device=cpu (wide: %d features)", n_features)
        return "cpu"
    if cells < 10_000_000:
        log.info("device=cpu (light: %d cells)", cells)
        return "cpu"
    log.info(
        "device=cuda (rows=%d feats=%d density=%.3f%%)",
        n_rows, n_features, density * 100,
    )
    return "cuda"


def _shape_args(X: Any) -> dict[str, int | None]:
    """Extract pick_device kwargs from a feature matrix (sparse or dense)."""
    n_rows, n_features = X.shape
    nnz = int(X.nnz) if hasattr(X, "nnz") else None
    return {"n_rows": int(n_rows), "n_features": int(n_features), "nnz": nnz}


def create_classifier(
    n_benign: int,
    n_malware: int,
    *,
    device: str | None = None,
    n_rows: int | None = None,
    n_features: int | None = None,
    nnz: int | None = None,
    random_state: int = 42,
    n_estimators: int = 600,
    max_depth: int = 10,
    learning_rate: float = 0.02,
    early_stopping_rounds: int = 100,
    min_child_weight: int = 5,
    min_child_samples: int | None = None,
    num_leaves: int | None = None,
    colsample_bytree: float = 0.8,
    subsample: float = 0.8,
    gamma: float = 0.0,
    reg_alpha: float = 0.0,
    reg_lambda: float = 1.0,
    monotone_constraints: str | dict[str, int] | None = None,
    learner: str = "litmus-xg",
    scale_pos_weight_mult: float = 1.0,
    boosting_type: str = "gbdt",
    extra_trees: bool = False,
    num_threads: int | None = None,
) -> Any:
    """Create a classifier with defaults tuned for malware detection.

    ``scale_pos_weight_mult`` multiplies the auto-computed n_benign/n_malware
    ratio used for class balancing.  Values <1.0 down-weight positives at
    training time, biasing the score distribution toward fewer false positives
    at low FPR thresholds (the operating point Azoth ships at).  Values >1.0
    over-weight positives — useful only when training data is so imbalanced
    that the auto ratio still under-represents malware.

    ``boosting_type`` (LightGBM only) chooses the boosting algorithm: ``gbdt``
    (default), ``dart`` (drop-out for regularized tail behavior), or ``goss``
    (gradient-based one-side sampling).  Ignored for the XGBoost learner.

    ``extra_trees`` (LightGBM only) enables random splits instead of greedy
    splits.  Adds ensemble noise that often improves generalization at the tail.
    """
    base_spw = n_benign / max(n_malware, 1)
    spw = base_spw * max(scale_pos_weight_mult, 0.0)
    if device == "auto":
        device = pick_device(n_rows, n_features, nnz)
    if learner == "azoth":
        try:
            import lightgbm as lgb  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "azoth requires LightGBM; run `make venv` to install dependencies",
            ) from exc
        device_params: dict[str, object] = {}
        if device and device not in {"cpu", "auto"}:
            if device not in {"cuda", "gpu"}:
                raise ValueError(f"unsupported azoth device: {device}")
            device_params["device_type"] = device
        return lgb.LGBMClassifier(
            objective="binary",
            boosting_type=boosting_type,
            extra_trees=bool(extra_trees),
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            min_child_weight=min_child_weight,
            **({"min_child_samples": min_child_samples} if min_child_samples is not None else {}),
            **({"num_leaves": num_leaves} if num_leaves is not None else {}),
            colsample_bytree=colsample_bytree,
            subsample=subsample,
            reg_alpha=reg_alpha,
            reg_lambda=reg_lambda,
            scale_pos_weight=spw,
            random_state=random_state,
            # n_jobs=-1 means "claim every core" — fine for a solo training,
            # disastrous when AZOTH_SPECIALIST_PARALLELISM > 1 because
            # every concurrent LightGBM tries to grab the full host and the
            # OS spends most of its time context-switching. The specialist
            # suite passes num_threads = nproc/parallelism to keep total
            # worker count near the core count.
            n_jobs=num_threads if num_threads is not None and num_threads > 0 else -1,
            force_col_wise=True,
            verbosity=-1,
            **device_params,
        )
    if learner != "litmus-xg":
        raise ValueError(f"unsupported learner: {learner}")
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
        monotone_constraints=monotone_constraints,
        scale_pos_weight=spw,
        tree_method="hist",
        device=device,
        random_state=random_state,
        early_stopping_rounds=early_stopping_rounds,
    )


class OnnxModel:
    """Thin wrapper around an onnxruntime InferenceSession exposing the
    same .predict_proba surface the rest of the codebase expects from
    a LightGBM Booster.

    Inference accepts dense float32 input shape ``(n_samples, n_features)``.
    Sparse CSR/CSC inputs are dense-batched in chunks so the dense
    materialization doesn't blow up memory on the 60k-feature azoth
    routes (a 100k-row × 60k-feature dense matrix is 24 GB float32 —
    chunking at 1024 rows keeps each batch under 250 MB).
    """

    # ~1024 rows × 60k features × 4 bytes ≈ 245 MB per chunk. Safe on
    # most hosts, fast enough that chunking overhead is negligible.
    _CHUNK_ROWS = 1024

    # Module-path sentinel checked by predict_proba dispatch. Distinct
    # from "lightgbm"/"xgboost" so the route can fork on it cleanly.
    __module__ = "collimator.model.onnx"

    def __init__(self, session: Any, input_name: str) -> None:
        self._session = session
        self._input_name = input_name

    def predict_proba(self, X: Any) -> np.ndarray:
        """Returns shape (n_samples, 2) probabilities for parity with
        the LightGBM sklearn wrapper. The route .predict_proba consumer
        in this codebase indexes column 1; matching that contract here
        keeps the dispatch in predict_proba below simple.
        """
        import scipy.sparse as sp  # noqa: PLC0415 — optional dep

        n_rows = X.shape[0]
        out = np.empty((n_rows, 2), dtype=np.float32)
        for start in range(0, n_rows, self._CHUNK_ROWS):
            end = min(start + self._CHUNK_ROWS, n_rows)
            chunk = X[start:end]
            if sp.issparse(chunk):
                chunk = chunk.toarray()
            chunk = np.ascontiguousarray(chunk, dtype=np.float32)
            outputs = self._session.run(None, {self._input_name: chunk})
            # onnxmltools' lightgbm classifier emits [label, probs (n,2)].
            probs = outputs[1]
            if probs.ndim != 2 or probs.shape[1] != 2:
                raise ValueError(
                    f"unexpected ONNX output shape: {probs.shape}; "
                    f"expected (n, 2) probabilities"
                )
            out[start:end] = probs
        return out

    def predict(self, X: Any) -> np.ndarray:
        """LightGBM-Booster-compatible 1D prob output (positive class)."""
        return self.predict_proba(X)[:, 1]


def load_model(model_path: Path) -> Any:
    """Load a native XGBoost, LightGBM, or ONNX model."""
    path_str = str(model_path)
    if path_str.endswith(".onnx"):
        try:
            import onnxruntime as ort  # noqa: PLC0415 — optional dep
        except ImportError as e:
            raise ImportError(
                "onnxruntime is required to load .onnx model files; "
                "install onnxruntime or remove .onnx artifacts from the bundle"
            ) from e
        session = ort.InferenceSession(
            path_str, providers=["CPUExecutionProvider"],
        )
        # Resolve the input tensor name (model-dependent; onnxmltools
        # uses 'input' by convention but we lookup defensively).
        inputs = session.get_inputs()
        if not inputs:
            raise ValueError(f"ONNX model {model_path} has no inputs")
        return OnnxModel(session, inputs[0].name)
    model = xgb.XGBClassifier()
    try:
        model.load_model(path_str)
        return model
    except Exception as xgb_exc:
        try:
            import lightgbm as lgb  # noqa: PLC0415
            return lgb.Booster(model_file=path_str)
        except Exception:
            raise xgb_exc


def predict_proba(model: Any, X: np.ndarray) -> np.ndarray:
    """Return malware probability for each sample."""
    if isinstance(model, OnnxModel):
        probs = np.asarray(model.predict_proba(X)[:, 1], dtype=np.float32)
        if probs.ndim != 1:
            raise ValueError(f"unexpected ONNX prob shape: {probs.shape}")
        return probs
    if model.__class__.__module__.startswith("lightgbm"):
        if hasattr(model, "predict_proba"):
            best_iteration = getattr(model, "best_iteration_", None)
            kwargs = {"num_iteration": best_iteration} if best_iteration else {}
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="X does not have valid feature names.*")
                probs = model.predict_proba(X, **kwargs)[:, 1]
        else:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="X does not have valid feature names.*")
                probs = model.predict(X)
        probs = np.asarray(probs, dtype=np.float32)
        if probs.ndim != 1:
            raise ValueError(f"unexpected predict_proba output shape: {probs.shape}")
        return probs

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
