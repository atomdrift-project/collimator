"""Export trained XGBoost model to ONNX and native JSON formats."""

from __future__ import annotations

from datetime import datetime
import json
import logging
import platform
from pathlib import Path

import numpy as np
import xgboost as xgb

log = logging.getLogger(__name__)


def load_evaluation(path: Path) -> dict[str, object]:
    """Load evaluation metadata from JSON."""
    with open(path) as f:
        return json.load(f)


def load_threshold(path: Path, default: float = 0.5) -> float:
    """Load the calibrated threshold from an evaluation artifact."""
    try:
        data = load_evaluation(path)
    except (OSError, json.JSONDecodeError):
        return default
    return float(data.get("optimal_threshold", default))


def load_recommended_thresholds(path: Path) -> dict[str, float]:
    """Load suspicious/hostile recommended thresholds from an evaluation artifact.

    Returns the same dict that ``recommended_thresholds`` was saved as. Missing
    or unparseable evaluation files yield an empty dict.
    """
    try:
        data = load_evaluation(path)
    except (OSError, json.JSONDecodeError):
        return {}
    raw = data.get("recommended_thresholds") or {}
    if not isinstance(raw, dict):
        return {}
    return {k: float(v) for k, v in raw.items() if v is not None}


def predict_onnx_proba(session: object, X: np.ndarray) -> np.ndarray:
    """Run ONNX inference and return class-1 probabilities as a 1D array."""
    results = session.run(None, {"features": X})
    n_rows = len(X)

    def _as_probability_vector(value: object) -> np.ndarray | None:
        if isinstance(value, list) and len(value) == n_rows and value:
            first = value[0]
            if isinstance(first, dict):
                return np.array(
                    [row.get(1, row.get("1", 0.0)) for row in value],
                    dtype=np.float32,
                )

        arr = np.asarray(value)
        if arr.ndim == 2 and arr.shape[0] == n_rows and arr.shape[1] >= 2:
            return arr[:, 1].astype(np.float32, copy=False)
        if arr.ndim == 1 and arr.shape[0] == n_rows:
            if np.issubdtype(arr.dtype, np.floating):
                return arr.astype(np.float32, copy=False)
        return None

    output_names = [out.name.lower() for out in session.get_outputs()]
    for name, value in zip(output_names, results):
        if "prob" in name:
            probs = _as_probability_vector(value)
            if probs is not None:
                return probs

    for value in results:
        probs = _as_probability_vector(value)
        if probs is not None and not np.array_equal(probs, probs.astype(np.int32)):
            return probs

    raise ValueError("could not locate probability output in ONNX results")


def export_onnx(
    model: object,
    n_features: int,
    output_path: Path,
) -> None:
    """Export XGBoost model to ONNX with dynamic batch size.

    The exported model outputs probabilities directly (class 1 probability).
    Requires onnxmltools to be installed.
    """
    if model.__class__.__module__.startswith("lightgbm"):
        log.info("skipping ONNX export for LightGBM model")
        return
    try:
        from onnxmltools import convert_xgboost
        from onnxmltools.convert.common.data_types import FloatTensorType
    except ImportError:
        log.warning("onnxmltools not installed, skipping ONNX export")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    initial_type = [("features", FloatTensorType([None, n_features]))]
    onnx_model = convert_xgboost(
        model,
        initial_types=initial_type,
        target_opset=15,
    )

    # Rename outputs for compatibility with existing Rust consumer.
    # XGBoost ONNX produces "label" and "probabilities" outputs.
    # We keep both but log what they are.
    output_names = [o.name for o in onnx_model.graph.output]
    log.info("ONNX output names: %s", output_names)

    import onnx
    onnx.save(onnx_model, str(output_path))
    log.info("exported ONNX model to %s", output_path)


def validate_onnx(
    model: object,
    onnx_path: Path,
    n_features: int,
    X: np.ndarray | None = None,
    n_samples: int = 100,
    tolerance: float = 1e-4,
) -> bool:
    """Verify ONNX model produces same outputs as XGBoost model."""
    if model.__class__.__module__.startswith("lightgbm"):
        log.info("skipping ONNX validation for LightGBM model")
        return True
    try:
        import onnxruntime as ort
    except ImportError:
        log.warning("onnxruntime not installed, skipping ONNX validation")
        return True

    if not onnx_path.exists():
        log.warning("ONNX model not found at %s, skipping validation", onnx_path)
        return True

    if X is not None and len(X) > 0:
        rng = np.random.default_rng(42)
        idx = rng.choice(len(X), min(n_samples, len(X)), replace=False)
        test_input = X[idx].astype(np.float32)
    else:
        test_input = np.random.randn(n_samples, n_features).astype(np.float32)

    # XGBoost predictions.
    from .model import predict_proba
    xgb_output = predict_proba(model, test_input)

    # ONNX predictions.
    session = ort.InferenceSession(str(onnx_path))
    onnx_probs = predict_onnx_proba(session, test_input)

    max_diff = float(np.max(np.abs(xgb_output - onnx_probs)))
    if max_diff > tolerance:
        log.error("ONNX validation failed: max diff %.6f > tolerance %.6f", max_diff, tolerance)
        return False

    log.info("ONNX validation passed: max diff %.8f", max_diff)
    return True


def is_constant_predictor(model: object) -> bool:
    """True when a LightGBM model degenerates to a constant predictor:
    every tree has ≤1 leaf, i.e. the optimizer found no split worth
    making (typically tiny single-class filetype slices like xls/xlsx).

    Such a model carries no feature-space signal — it always emits the
    same score regardless of input. Training refuses to emit a route for
    it (see ``azoth_specialist_suite``) so litmus routes those files to
    the filegroup/general ensemble instead. Accepts either a LightGBM
    Booster or an sklearn ``LGBMClassifier`` wrapper."""
    booster = getattr(model, "booster_", model)
    try:
        leaf_counts = [t["num_leaves"] for t in booster.dump_model().get("tree_info", [])]
    except Exception:
        return False
    return bool(leaf_counts) and max(leaf_counts) <= 1


def route_model_is_degenerate(route_dir: Path) -> bool:
    """True when a deployed route directory ships only constant-predictor
    model(s) and should be kept out of the bundle (so litmus routes those
    files to the filegroup/general ensemble).

    A route carrying an ``.onnx`` artifact is never degenerate: ONNX export
    is skipped for constant predictors (see ``export_lightgbm_onnx``), so its
    presence implies the model learned at least one split. Only ``.txt``-only
    routes are inspected, and only those whose every seed is constant count as
    degenerate. Used by calibration (drops them from ``config.json``) and by
    deploy validation (hard-fails if one slips through)."""
    from collimator import bundle  # noqa: PLC0415 — avoid import cycle at module load

    files = bundle.model_files(route_dir)
    if any(f.suffix == ".onnx" for f in files):
        return False
    txts = [f for f in files if f.suffix == ".txt"]
    if not txts:
        return False
    import lightgbm as lgb  # noqa: PLC0415 — heavy; only needed for .txt-only routes

    try:
        boosters = [lgb.Booster(model_file=str(f)) for f in txts]
    except Exception:
        # Can't parse the model — don't silently drop the route; let real
        # validation (feature-count, schema) surface the problem instead.
        return False
    return all(is_constant_predictor(b) for b in boosters)


def export_lightgbm_onnx(
    booster: object,
    n_features: int,
    output_path: Path,
) -> bool:
    """Export a LightGBM Booster to ONNX. Returns True on success, False
    when onnxmltools is unavailable (warns + skips). Used to emit the
    cross-language inference artifact alongside the native ``.txt``.

    The exported model expects ``(n_samples, n_features)`` float32 input
    and emits ``[label, probabilities]`` outputs, where probabilities
    has shape ``(n, 2)``. Matches what onnxmltools' LightGBM converter
    produces by default with ``zipmap=False``.
    """
    try:
        from onnxmltools import convert_lightgbm  # noqa: PLC0415
        from onnxmltools.convert.common.data_types import FloatTensorType  # noqa: PLC0415
    except ImportError:
        log.warning("onnxmltools not installed; skipping ONNX export for LightGBM")
        return False

    # Defense-in-depth: never emit ONNX for a constant predictor. The
    # converter produces a spec-correct graph that trips an ONNX Runtime
    # bug in TreeEnsembleClassifier (LOGISTIC post-transform skipped for
    # 0-split trees, leaking raw class_weights as probabilities), and the
    # model has no feature-space signal anyway. Training already refuses
    # to emit a route for these (azoth_specialist_suite); this guard
    # covers the direct/migration callers (e.g. convert_bundle_to_onnx).
    if is_constant_predictor(booster):
        log.info(
            "skipping ONNX export for %s: model is a constant predictor "
            "(no split learned — trips the TreeEnsembleClassifier 0-split bug)",
            output_path,
        )
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    onnx_model = convert_lightgbm(
        booster,
        initial_types=[("input", FloatTensorType([None, int(n_features)]))],
        zipmap=False,
        target_opset=15,
    )
    # onnxmltools' LightGBM converter declares the output shapes
    # with a fixed first dim ({1}) even when the INPUT batch was
    # declared dynamic ([None, n_features]). ONNX Runtime then logs
    # a VerifyOutputSizes warning on every inference call where the
    # actual batch != 1 ("Expected shape from model of {1} does not
    # match actual shape of {N} for output label"). The computation
    # is correct; only the declared output shape disagrees. Patch
    # each graph output's first dim to be a symbolic "batch"
    # dimension so the declared shape matches reality and ORT stays
    # quiet.
    for output in onnx_model.graph.output:
        shape = output.type.tensor_type.shape
        if len(shape.dim) > 0:
            shape.dim[0].Clear()
            shape.dim[0].dim_param = "batch"
    # Atomic write: serialize to a sibling .tmp, then rename. A kill
    # mid-write leaves the original alone and the .tmp gets reaped by
    # the next training pass (it doesn't match the *.onnx glob).
    tmp_path = output_path.parent / f".{output_path.name}.tmp"
    tmp_path.write_bytes(onnx_model.SerializeToString())
    import os as _os  # noqa: PLC0415
    _os.replace(tmp_path, output_path)
    log.info("exported LightGBM ONNX to %s", output_path)
    return True


def save_model(model: object, output_path: Path) -> None:
    """Save a model in its native format. For LightGBM, also emit a
    sibling ``.onnx`` so the bundle ships a cross-language inference
    artifact (preferred at load time by ``bundle.model_files``). ONNX
    emission is best-effort: if onnxmltools is unavailable the .txt
    is still written and the bundle stays loadable through the legacy
    LightGBM path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if model.__class__.__module__.startswith("lightgbm"):
        booster = model.booster_
        booster.save_model(str(output_path))
        log.info("saved LightGBM model to %s", output_path)
        # Sibling .onnx with the same stem. Skip when the destination
        # would be the .onnx itself (defensive — save_model shouldn't
        # be called with an .onnx output path, but checked anyway).
        if output_path.suffix == ".txt":
            onnx_path = output_path.with_suffix(".onnx")
            try:
                export_lightgbm_onnx(
                    booster, booster.num_feature(), onnx_path,
                )
            except Exception as e:
                # ONNX export failure shouldn't kill training — the
                # .txt is still the canonical artifact. Log and move on.
                log.warning("LightGBM ONNX export failed for %s: %s", onnx_path, e)
        return
    model.save_model(str(output_path))
    log.info("saved XGBoost model to %s", output_path)


def save_evaluation(
    metrics: dict[str, float],
    calibration: dict[str, object],
    optimal_threshold: float,
    confusion: list[list[int]],
    class_distribution: dict[str, int],
    split_summary: dict[str, int | str],
    fold_metrics: list[dict[str, float]],
    n_features: int,
    model_abi_version: int,
    experiment: dict[str, object],
    output_path: Path,
    recommended_thresholds: dict[str, float | None] | None = None,
    severity_levels: list[dict[str, object]] | None = None,
    severity_level_targets: list[dict[str, object]] | None = None,
    model_name: str | None = None,
) -> None:
    """Save evaluation results as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results = {
        "metrics": metrics,
        "calibration": calibration,
        "optimal_threshold": optimal_threshold,
        "recommended_thresholds": recommended_thresholds,
        "severity_level_targets": severity_level_targets,
        "severity_levels": severity_levels,
        "confusion_matrix": confusion,
        "class_distribution": class_distribution,
        "split_summary": split_summary,
        "fold_metrics": fold_metrics,
        "n_features": n_features,
        "model_abi_version": model_abi_version,
        "model_name": model_name,
        "experiment": experiment,
        "environment": {
            "python": platform.python_version(),
            "xgboost": xgb.__version__,
            "numpy": np.__version__,
        },
    }
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    log.info("saved evaluation to %s", output_path)


def save_run_summary(
    *,
    kind: str,
    payload: dict[str, object],
    output_dir: Path,
) -> Path:
    """Save a timestamped run summary JSON for posterity."""
    runs_dir = output_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    output_path = runs_dir / f"{timestamp}-{kind}.json"
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2)
    log.info("saved %s run summary to %s", kind, output_path)
    return output_path
