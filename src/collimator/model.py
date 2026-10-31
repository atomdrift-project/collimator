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
import os
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import xgboost as xgb

log = logging.getLogger(__name__)

_device_cache: str | None = None
_lgb_cuda_cache: bool | None = None


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


def detect_lightgbm_cuda() -> bool:
    """True only if LightGBM was actually built with CUDA.

    ``detect_device`` probes XGBoost, but the azoth learner is LightGBM — and a
    box can have XGBoost-CUDA while its LightGBM is CPU-only. ``pick_device``
    would then return ``cuda`` and LightGBM aborts with "CUDA Tree Learner was
    not enabled in this build". This is latent until a matrix gets narrow/dense
    enough to clear pick_device's GPU gates (e.g. after feature pruning drops
    n_features below the wide-CPU threshold), so probe LightGBM directly.
    """
    global _lgb_cuda_cache
    if _lgb_cuda_cache is not None:
        return _lgb_cuda_cache
    try:
        import lightgbm as lgb  # noqa: PLC0415
        X = np.zeros((8, 1), dtype=np.float32)
        y = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.float32)
        lgb.train(
            {"objective": "binary", "device_type": "cuda", "verbose": -1,
             "num_iterations": 1, "min_data_in_leaf": 1, "min_data_in_bin": 1},
            lgb.Dataset(X, label=y),
        )
        _lgb_cuda_cache = True
    except Exception:
        _lgb_cuda_cache = False
    log.info("lightgbm cuda available: %s", _lgb_cuda_cache)
    return _lgb_cuda_cache


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
    if n_rows is None or n_features is None:
        return "cpu"
    cells = n_rows * n_features
    density = (nnz / cells) if nnz is not None and cells else 1.0
    # Benchmarked: at ~7% density (250k×12k, the post-pruning azoth shape) the
    # CUDA tree learner is no faster than a 16-thread CPU — GBDT histogram
    # construction is memory-bound/scatter-heavy, not the dense-FLOP work GPUs
    # win at, and the CPU path exploits sparsity. So require genuinely dense
    # (>=15%) before paying for GPU; realistic azoth matrices stay on CPU.
    if density < 0.15:
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
    # CPU-only shapes need no GPU probe (which initializes XGBoost/CUDA even
    # when this fit uses LightGBM). Probe only workloads eligible for CUDA.
    if not detect_device().startswith("cuda"):
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
    monotone_constraints: str | dict[str, int] | tuple[int, ...] | None = None,
    learner: str = "litmus-xg",
    scale_pos_weight_mult: float = 1.0,
    max_delta_step: float = 0.0,
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
        if not np.isfinite(max_delta_step) or max_delta_step < 0:
            raise ValueError("max_delta_step must be finite and nonnegative")
        try:
            import lightgbm as lgb  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "azoth requires LightGBM; run `make venv` to install dependencies",
            ) from exc
        # pick_device()/detect_device() reflect XGBoost's CUDA support; LightGBM
        # may be CPU-only on the same host, so verify before committing to GPU
        # (otherwise LightGBM aborts: "CUDA Tree Learner was not enabled").
        if device in {"cuda", "gpu"} and not detect_lightgbm_cuda():
            log.warning("LightGBM not built with CUDA; using CPU (pick_device chose %s)", device)
            device = "cpu"
        device_params: dict[str, object] = {}
        if boosting_type == "goss" and subsample != 1:
            raise ValueError("GOSS does not support row bagging; set subsample=1")
        if device and device not in {"cpu", "auto"}:
            if device not in {"cuda", "gpu"}:
                raise ValueError(f"unsupported azoth device: {device}")
            device_params["device_type"] = device
        threads = num_threads if num_threads is not None and num_threads > 0 else -1
        # Small CPU fits spend more time synchronizing large OpenMP teams than
        # building trees. A 17.9k-row / 3.25M-nnz DEB fit took 40.6s at 64
        # threads versus 2.8-3.1s at four, with the same 400-tree budget.
        # num_threads is a ceiling; preserve lower explicit limits and avoid
        # applying this small-workload rule to large or unknown shapes.
        entries = nnz if nnz is not None else (
            n_rows * n_features if n_rows is not None and n_features is not None else None
        )
        if (not device_params and n_rows is not None and n_rows <= 50_000
                and entries is not None and entries <= 10_000_000
                and (threads == -1 or threads > 4)):
            log.info("small LightGBM fit: limiting threads from %s to 4 (%d rows, %d entries)",
                     "all" if threads == -1 else threads, n_rows, entries)
            threads = 4
        return lgb.LGBMClassifier(
            objective="binary",
            metric="average_precision",
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
            subsample_freq=1 if subsample < 1 else 0,
            min_split_gain=gamma,
            **({"monotone_constraints": monotone_constraints} if monotone_constraints is not None else {}),
            reg_alpha=reg_alpha,
            reg_lambda=reg_lambda,
            scale_pos_weight=spw,
            max_delta_step=max_delta_step,
            random_state=random_state,
            n_jobs=threads,
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
    Supported tree graphs select only columns used by their splits before
    densifying. Callers continue supplying the original full feature layout.
    Dense batches are bounded by both row count and a 64 MiB byte budget.
    """

    _CHUNK_ROWS = 1024
    _DENSE_BYTES = 64 * 1024 * 1024

    @classmethod
    def dense_chunk_rows(cls, n_features: int) -> int:
        """Bound the dense input even for unusually wide feature layouts."""
        return min(cls._CHUNK_ROWS, max(1, cls._DENSE_BYTES // (max(1, n_features) * 4)))

    # Module-path sentinel checked by predict_proba dispatch. Distinct
    # from "lightgbm"/"xgboost" so the route can fork on it cleanly.
    __module__ = "collimator.model.onnx"

    def __init__(self, session: Any, input_name: str, *,
                 input_columns: np.ndarray | None = None,
                 original_features: int | None = None) -> None:
        self._session = session
        self._input_name = input_name
        self._input_columns = input_columns
        self._original_features = original_features

    def shares_input_layout(self, other: OnnxModel) -> bool:
        return (self._original_features == other._original_features
                and (self._input_columns is other._input_columns
                     or (self._input_columns is not None and other._input_columns is not None
                         and np.array_equal(self._input_columns, other._input_columns))))

    def validate_input(self, X: Any) -> None:
        if self._original_features is not None and X.shape[1] != self._original_features:
            raise ValueError(f'expected {self._original_features} original ONNX features, got {X.shape[1]}')

    def project_input(self, X: Any) -> Any:
        self.validate_input(X)
        return X if self._input_columns is None else X[:, self._input_columns]

    def _predict_dense(self, chunk: np.ndarray) -> np.ndarray:
        """Run one already-projected, bounded dense batch."""
        outputs = self._session.run(None, {self._input_name: chunk})
        probs = outputs[1]
        if probs.ndim != 2 or probs.shape != (len(chunk), 2):
            raise ValueError(f'unexpected ONNX output shape: {probs.shape}; expected (n, 2) probabilities')
        return probs

    def predict_proba(self, X: Any) -> np.ndarray:
        """Returns shape (n_samples, 2) probabilities for parity with
        the LightGBM sklearn wrapper. The route .predict_proba consumer
        in this codebase indexes column 1; matching that contract here
        keeps the dispatch in predict_proba below simple.
        """
        import scipy.sparse as sp  # noqa: PLC0415 — optional dep

        n_rows = X.shape[0]
        self.validate_input(X)
        out = np.empty((n_rows, 2), dtype=np.float32)
        # Preserve pre-projection batch boundaries. ORT can change floating
        # reduction order for short tails when the batch shape changes.
        chunk_rows = self.dense_chunk_rows(X.shape[1])
        for start in range(0, n_rows, chunk_rows):
            end = min(start + chunk_rows, n_rows)
            chunk = self.project_input(X[start:end])
            if sp.issparse(chunk):
                chunk = chunk.toarray()
            chunk = np.ascontiguousarray(chunk, dtype=np.float32)
            out[start:end] = self._predict_dense(chunk)
        return out

    def predict(self, X: Any) -> np.ndarray:
        """LightGBM-Booster-compatible 1D prob output (positive class)."""
        return self.predict_proba(X)[:, 1]


def load_onnx_models(paths: list[Path]) -> list[OnnxModel]:
    """Load ensemble members with a shared projection and dense input buffer."""
    from collimator.onnx_projection import project_tree_inputs

    try:
        import onnxruntime as ort
    except ImportError as e:
        raise ImportError('onnxruntime is required to load .onnx model files') from e
    payloads, columns, width = [str(p) for p in paths], None, None
    if os.getenv('COLLIMATOR_ONNX_PROJECT_INPUT', '1').lower() not in {'0', 'false', 'no', 'off'}:
        payloads, columns, width = project_tree_inputs(paths)
    if columns is not None:
        log.info('ONNX input projection: %d -> %d columns across %d members', width, len(columns), len(paths))
    threads = int(os.getenv('COLLIMATOR_ONNX_THREADS', '8'))
    if threads < 1:
        raise ValueError('COLLIMATOR_ONNX_THREADS must be positive')
    options = ort.SessionOptions()
    options.intra_op_num_threads = threads
    options.inter_op_num_threads = 1
    options.add_session_config_entry('session.intra_op.allow_spinning', '0')
    options.add_session_config_entry('session.inter_op.allow_spinning', '0')
    members = []
    for path, payload in zip(paths, payloads, strict=True):
        session = ort.InferenceSession(payload, options, providers=['CPUExecutionProvider'])
        inputs = session.get_inputs()
        if not inputs:
            raise ValueError(f'ONNX model {path} has no inputs')
        members.append(OnnxModel(session, inputs[0].name, input_columns=columns, original_features=width))
    return members


def load_model(model_path: Path) -> Any:
    """Load a native XGBoost, LightGBM, or ONNX model."""
    path_str = str(model_path)
    if path_str.endswith(".onnx"):
        return load_onnx_models([model_path])[0]
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
