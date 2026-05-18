"""Training loop with holdout + K-fold cross-validation."""

from __future__ import annotations

import logging
import os
import warnings
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import scipy.sparse as sp
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.isotonic import IsotonicRegression
from sklearn.model_selection import StratifiedKFold, train_test_split

from .model import _shape_args, booster_device, create_classifier, predict_proba

log = logging.getLogger(__name__)

# Minimum samples per class to enable a holdout split.
MIN_HOLDOUT_CLASS_SIZE = 20
MIN_CALIBRATION_CLASS_SIZE = 8

# Fraction of non-test training data reserved for calibration/evaluation.
HOLDOUT_FRACTION = 0.10


@dataclass
class TrainConfig:
    learner: str = "litmus-xg"
    seed: int = 42
    device: str | None = None
    holdout_fraction: float = HOLDOUT_FRACTION
    n_folds: int = 5
    n_estimators: int = 600
    max_depth: int = 10
    learning_rate: float = 0.02
    early_stopping_rounds: int = 100
    min_child_weight: int = 5
    min_child_samples: int | None = None
    num_leaves: int | None = None
    colsample_bytree: float = 0.8
    subsample: float = 0.8
    gamma: float = 0.0
    reg_alpha: float = 0.0
    reg_lambda: float = 1.0
    beta: float = 2.0  # F-beta for threshold selection; >1.0 favors recall on malware
    monotone_constraints: str | dict[str, int] | None = None
    threshold_mode: str = "fbeta"  # fbeta | max_recall_at_fpr
    threshold_fpr_target: float | None = None
    hard_negative_fraction: float = 0.0
    hard_negative_weight: float = 1.0
    benign_filetype_weights: dict[str, float] = field(default_factory=dict)
    # Multiplier applied to the auto-computed n_benign/n_malware scale_pos_weight.
    # 1.0 = current behavior (fully balanced).  <1.0 down-weights positives at
    # training time, biasing toward fewer false positives at low FPR — what we
    # want when optimizing recall@k FP/M for the deployed operating point.
    scale_pos_weight_mult: float = 1.0
    # LightGBM-only: gbdt | dart | goss.  Ignored by the XGBoost learner.
    boosting_type: str = "gbdt"
    # LightGBM-only: random splits instead of greedy.  Ignored by XGBoost.
    extra_trees: bool = False
    # Maximum CPU threads to use per training. ``None`` = let LightGBM use
    # every core (n_jobs=-1, the historical behavior). Set this when running
    # multiple trainings concurrently (the specialist suite at
    # AZOTH_SPECIALIST_PARALLELISM > 1) so each LightGBM instance doesn't
    # try to claim all 128 cores and thrash on context switches. The suite
    # auto-computes nproc/parallelism when this is None and parallelism>1.
    #
    # ``COLLIMATOR_NUM_THREADS`` env override applies when this is None — lets
    # the OOF pipeline cap threads for concurrent prod+fold-A+fold-B general
    # training without plumbing a flag through experiment.py's argparse.
    num_threads: int | None = None

    def __post_init__(self) -> None:
        if self.num_threads is None:
            env_val = os.environ.get("COLLIMATOR_NUM_THREADS", "").strip()
            if env_val:
                try:
                    n = int(env_val)
                except ValueError:
                    log.warning(
                        "ignoring invalid COLLIMATOR_NUM_THREADS=%r", env_val,
                    )
                else:
                    if n > 0:
                        self.num_threads = n


@dataclass
class TrainResult:
    model: Any
    metrics: dict[str, float]
    calibration: dict[str, object]
    optimal_threshold: float
    confusion: list[list[int]]
    class_distribution: dict[str, int]
    split_summary: dict[str, int | str]
    fold_metrics: list[dict[str, float]]
    feature_means: list[float] = field(default_factory=list)
    feature_stds: list[float] = field(default_factory=list)
    isotonic_calibrator: IsotonicRegression | None = None
    # Out-of-fold CV predictions and labels for the full training set.
    # These are honest (no data leakage) and can be combined with test-set
    # predictions for FPR measurement over the entire database.
    cv_predictions: np.ndarray = field(default_factory=lambda: np.array([]))
    cv_labels: np.ndarray = field(default_factory=lambda: np.array([]))


def _compute_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5,
) -> dict[str, float]:
    y_pred = (y_prob >= threshold).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "brier": float(brier_score_loss(y_true, y_prob)),
        "roc_auc": (
            float(roc_auc_score(y_true, y_prob))
            if len(np.unique(y_true)) > 1 else 0.0
        ),
        "avg_precision": (
            float(average_precision_score(y_true, y_prob))
            if len(np.unique(y_true)) > 1 else 0.0
        ),
    }


def _calibration_summary(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    *,
    n_bins: int = 10,
) -> dict[str, object]:
    """Summarize calibration with equal-width bins and ECE."""
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_ids = np.clip(np.digitize(y_prob, edges[1:-1], right=False), 0, n_bins - 1)
    rows: list[dict[str, float | int]] = []
    ece = 0.0
    for i in range(n_bins):
        mask = bin_ids == i
        count = int(np.sum(mask))
        if count == 0:
            rows.append(
                {
                    "bin": i,
                    "count": 0,
                    "avg_confidence": 0.0,
                    "empirical_rate": 0.0,
                    "abs_gap": 0.0,
                }
            )
            continue
        avg_conf = float(np.mean(y_prob[mask]))
        emp_rate = float(np.mean(y_true[mask]))
        gap = abs(avg_conf - emp_rate)
        ece += (count / max(len(y_prob), 1)) * gap
        rows.append(
            {
                "bin": i,
                "count": count,
                "avg_confidence": avg_conf,
                "empirical_rate": emp_rate,
                "abs_gap": gap,
            }
        )
    return {"ece": float(ece), "bins": rows}


def _optimal_threshold(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    beta: float = 0.5,
) -> float:
    """Find threshold that maximizes F-beta on a precision-recall curve.

    Default beta=0.5 weights precision 2x more than recall, appropriate for
    a pipeline where false positives (legitimate tools flagged as malware)
    are more disruptive than false negatives (missed malware that cleave
    can catch with criticality heuristics).
    """
    if len(np.unique(y_true)) < 2:
        return 0.5
    prec_arr, rec_arr, thresholds = precision_recall_curve(y_true, y_prob)
    beta_sq = beta ** 2
    fbeta = (1 + beta_sq) * (prec_arr * rec_arr) / (beta_sq * prec_arr + rec_arr + 1e-8)
    opt_idx = int(np.argmax(fbeta))
    if opt_idx < len(thresholds):
        return float(thresholds[opt_idx])
    return 0.5


def _max_recall_threshold_at_fpr(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    *,
    max_fpr: float,
) -> float:
    """Lowest threshold with observed FPR <= max_fpr."""
    if len(np.unique(y_true)) < 2:
        return 0.5
    benign = y_true == 0
    n_benign = int(np.sum(benign))
    if n_benign == 0:
        return 0.5
    order = np.argsort(y_prob)[::-1]
    sorted_probs = y_prob[order]
    sorted_y = y_true[order]
    cum_fp = np.cumsum(sorted_y == 0)
    change_mask = np.concatenate([np.diff(sorted_probs) != 0, [True]])
    cuts = np.where(change_mask)[0]
    thresholds = sorted_probs[cuts]
    fp_vals = cum_fp[cuts]
    valid = (fp_vals / n_benign) <= max_fpr
    if valid.any():
        return float(thresholds[np.where(valid)[0][-1]])
    return float(np.nextafter(np.max(y_prob), np.inf))


def _select_threshold(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    *,
    mode: str,
    beta: float,
    max_fpr: float | None,
) -> float:
    if mode == "max_recall_at_fpr":
        if max_fpr is None:
            raise ValueError("threshold_fpr_target is required for max_recall_at_fpr mode")
        return _max_recall_threshold_at_fpr(y_true, y_prob, max_fpr=max_fpr)
    return _optimal_threshold(y_true, y_prob, beta=beta)


def _compute_hard_negative_weights(
    model: Any,
    X_train: np.ndarray | sp.spmatrix,
    y_train: np.ndarray,
    *,
    fraction: float,
    weight: float,
) -> np.ndarray | None:
    """Upweight top-scoring benign samples inside the current training split."""
    if fraction <= 0.0 or weight <= 1.0:
        return None
    benign_idx = np.where(y_train == 0)[0]
    if len(benign_idx) == 0:
        return None
    n_hard = max(int(np.ceil(len(benign_idx) * fraction)), 1)
    benign_scores = predict_proba(model, X_train[benign_idx])
    top_local = benign_idx[np.argsort(benign_scores)[-n_hard:]]
    sample_weight = np.ones(len(y_train), dtype=np.float32)
    sample_weight[top_local] = float(weight)
    return sample_weight


def _compute_benign_filetype_weights(
    sample_file_types: np.ndarray,
    y_train: np.ndarray,
    *,
    weights_by_filetype: dict[str, float],
) -> np.ndarray | None:
    """Upweight benign samples from selected file types."""
    if not weights_by_filetype:
        return None
    sample_weight = np.ones(len(y_train), dtype=np.float32)
    any_weighted = False
    for file_type, weight in weights_by_filetype.items():
        if weight <= 1.0:
            continue
        mask = (y_train == 0) & (sample_file_types == file_type)
        if np.any(mask):
            sample_weight[mask] = np.float32(weight)
            any_weighted = True
    return sample_weight if any_weighted else None


def _merge_sample_weights(
    base_weight: np.ndarray | None,
    extra_weight: np.ndarray | None,
) -> np.ndarray | None:
    if base_weight is None:
        return extra_weight
    if extra_weight is None:
        return base_weight
    return (base_weight * extra_weight).astype(np.float32, copy=False)


def _fit_model(
    model: Any,
    X: np.ndarray | sp.spmatrix,
    y: np.ndarray,
    *,
    sample_weight: np.ndarray | None = None,
    eval_set: list[tuple[np.ndarray | sp.spmatrix, np.ndarray]] | None = None,
    early_stopping_rounds: int | None = None,
) -> None:
    if model.__class__.__module__.startswith("lightgbm"):
        callbacks = []
        if eval_set and early_stopping_rounds:
            import lightgbm as lgb  # noqa: PLC0415
            callbacks.append(lgb.early_stopping(early_stopping_rounds, verbose=False))
        model.fit(
            X,
            y,
            sample_weight=sample_weight,
            eval_set=eval_set,
            callbacks=callbacks or None,
        )
        return
    model.fit(
        X,
        y,
        sample_weight=sample_weight,
        eval_set=eval_set,
        verbose=False,
    )


def _split_calibration_eval(
    X_holdout: np.ndarray | sp.spmatrix,
    y_holdout: np.ndarray,
    *,
    seed: int = 42,
) -> tuple[
    tuple[np.ndarray | sp.spmatrix, np.ndarray] | None,
    tuple[np.ndarray | sp.spmatrix, np.ndarray],
]:
    """Split holdout into calibration and final evaluation subsets when feasible."""
    n_holdout_malware = int(np.sum(y_holdout == 1))
    n_holdout_benign = int(np.sum(y_holdout == 0))
    if min(n_holdout_malware, n_holdout_benign) < MIN_CALIBRATION_CLASS_SIZE:
        return None, (X_holdout, y_holdout)

    calib_idx, eval_idx = train_test_split(
        np.arange(len(y_holdout)),
        test_size=0.5,
        stratify=y_holdout,
        random_state=seed,
    )
    return (
        (X_holdout[calib_idx], y_holdout[calib_idx]),
        (X_holdout[eval_idx], y_holdout[eval_idx]),
    )


def train(
    X: np.ndarray | sp.spmatrix,
    y: np.ndarray,
    config: TrainConfig | None = None,
    feature_names: list[str] | None = None,
    sample_file_types: np.ndarray | None = None,
) -> TrainResult:
    """Train an XGBoost classifier with holdout + K-fold CV.

    Pipeline:
      1. Holdout split (default 10%) for honest evaluation
      2. Compute feature standardization (mean/std) for pipeline compatibility
      3. K-fold CV on train+val for model selection metrics
      4. Retrain final model on all train+val data
      5. Evaluate on holdout for honest metrics + threshold calibration
    """
    if config is None:
        config = TrainConfig()

    np.random.seed(config.seed)
    if sample_file_types is not None and len(sample_file_types) != len(y):
        raise ValueError(
            f"sample_file_types length {len(sample_file_types)} does not match labels {len(y)}",
        )
    if config.benign_filetype_weights and sample_file_types is None:
        raise ValueError("sample_file_types are required when benign_filetype_weights are configured")

    n_features = X.shape[1]
    n_malware = int(np.sum(y == 1))
    n_benign = int(np.sum(y == 0))

    if sp.issparse(X):
        mem_mb = (X.data.nbytes + X.indices.nbytes + X.indptr.nbytes) / 1024 / 1024
        log.info(
            "training: %d samples (%d malware, %d benign), %d features, "
            "sparse nnz=%d density=%.1f%% mem=%.0fMB",
            len(y), n_malware, n_benign, n_features,
            X.nnz, 100.0 * X.nnz / max(len(y) * n_features, 1), mem_mb,
        )
    else:
        mem_mb = X.nbytes / 1024 / 1024
        log.info(
            "training: %d samples (%d malware, %d benign), %d features, dense mem=%.0fMB",
            len(y), n_malware, n_benign, n_features, mem_mb,
        )

    # --- Holdout split ---
    n_min_class = min(n_malware, n_benign)
    if config.holdout_fraction <= 0.0:
        # No holdout requested — use all data for training; CV drives threshold.
        X_tv, y_tv = X, y
        X_holdout = y_holdout = None
        file_types_tv = np.asarray(sample_file_types, dtype=object) if sample_file_types is not None else None
    elif n_min_class >= MIN_HOLDOUT_CLASS_SIZE:
        tv_idx, holdout_idx = train_test_split(
            np.arange(len(y)),
            test_size=config.holdout_fraction,
            stratify=y,
            random_state=config.seed,
        )
        X_tv, y_tv = X[tv_idx], y[tv_idx]
        X_holdout, y_holdout = X[holdout_idx], y[holdout_idx]
        file_types_tv = np.asarray(sample_file_types, dtype=object)[tv_idx] if sample_file_types is not None else None
        log.info(
            "holdout: %d samples (%d malware, %d benign)",
            len(y_holdout),
            int(np.sum(y_holdout == 1)),
            int(np.sum(y_holdout == 0)),
        )
    else:
        X_tv, y_tv = X, y
        X_holdout = y_holdout = None
        file_types_tv = np.asarray(sample_file_types, dtype=object) if sample_file_types is not None else None
        log.warning(
            "dataset too small for holdout (%d min class), using all data",
            n_min_class,
        )

    # --- Standardization params ---
    # Trees are invariant to monotonic feature transforms, so we train on raw
    # features directly (no dense copy needed). We still compute mean/std and
    # export them so the Rust inference pipeline can apply standardization if
    # the model was trained that way — but for v13+ we skip it.
    if sp.issparse(X_tv):
        feature_means64 = np.asarray(X_tv.mean(axis=0), dtype=np.float64).ravel()
        # Var = E[X^2] - E[X]^2, computed without densifying or mutating X_tv.
        # Some aggregate features can exceed float32's safe square range.
        X_sq = X_tv.copy()
        X_sq.data = X_sq.data.astype(np.float64, copy=False)
        X_sq.data **= 2
        variance = (
            np.asarray(X_sq.mean(axis=0), dtype=np.float64).ravel()
            - feature_means64 ** 2
        )
        feature_means = feature_means64.astype(np.float32)
        feature_stds = np.sqrt(np.maximum(variance, 0)).astype(np.float32)
        del X_sq, feature_means64, variance
    else:
        feature_means = X_tv.mean(axis=0).astype(np.float32)
        feature_stds = X_tv.std(axis=0).astype(np.float32)
    feature_stds[feature_stds < 1e-7] = 1.0

    # --- Cross-validation ---
    n_tv_malware = int(np.sum(y_tv == 1))
    n_tv_benign = int(np.sum(y_tv == 0))
    if config.n_folds < 2:
        log.info("cross-validation disabled")
        n_folds = 0
    else:
        n_folds = min(config.n_folds, n_tv_malware, n_tv_benign)
    if n_folds < 2:
        if config.n_folds >= 2:
            log.warning("not enough samples for CV, training on all data")
        n_folds = 0

    fold_metrics_list: list[dict[str, float]] = []
    cv_predictions = np.zeros(len(y_tv))
    cv_policy = "none"

    if n_folds >= 2:
        skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=config.seed)
        split_iter = skf.split(X_tv, y_tv)
        cv_policy = "stratified"
        log.info("running %d-fold cross-validation", n_folds)
        # Suppress the XGBoost device-mismatch UserWarning for the CV loop.
        # It fires on the first inplace_predict when data is on CPU and model
        # on CUDA — expected behaviour, not actionable.
        warnings.filterwarnings("ignore", category=UserWarning, module="xgboost.*")
        print(f"\n{'Fold':<6} {'AUC':>8} {'F1':>8} {'Prec':>8} {'Recall':>8}")
        print(f"{'-' * 42}")

        for fold, (train_idx, val_idx) in enumerate(split_iter):
            fold_base_weight = _compute_benign_filetype_weights(
                file_types_tv[train_idx],
                y_tv[train_idx],
                weights_by_filetype=config.benign_filetype_weights,
            ) if file_types_tv is not None else None
            fold_model = create_classifier(
                n_benign=int(np.sum(y_tv[train_idx] == 0)),
                n_malware=int(np.sum(y_tv[train_idx] == 1)),
                device=config.device,
                **_shape_args(X_tv[train_idx]),
                random_state=config.seed,
                n_estimators=config.n_estimators,
                max_depth=config.max_depth,
                learning_rate=config.learning_rate,
                early_stopping_rounds=config.early_stopping_rounds,
                min_child_weight=config.min_child_weight,
                min_child_samples=config.min_child_samples,
                num_leaves=config.num_leaves,
                colsample_bytree=config.colsample_bytree,
                subsample=config.subsample,
                gamma=config.gamma,
                reg_alpha=config.reg_alpha,
                reg_lambda=config.reg_lambda,
                learner=config.learner,
                scale_pos_weight_mult=config.scale_pos_weight_mult,
                boosting_type=config.boosting_type,
                extra_trees=config.extra_trees,
                num_threads=config.num_threads,
            )
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module="xgboost")
                if config.hard_negative_fraction > 0.0 and config.hard_negative_weight > 1.0:
                    _fit_model(
                        fold_model,
                        X_tv[train_idx], y_tv[train_idx],
                        sample_weight=fold_base_weight,
                        eval_set=[(X_tv[val_idx], y_tv[val_idx])],
                        early_stopping_rounds=config.early_stopping_rounds,
                    )
                    hard_negative_weight = _compute_hard_negative_weights(
                        fold_model,
                        X_tv[train_idx],
                        y_tv[train_idx],
                        fraction=config.hard_negative_fraction,
                        weight=config.hard_negative_weight,
                    )
                    sample_weight = _merge_sample_weights(fold_base_weight, hard_negative_weight)
                    fold_model = create_classifier(
                        n_benign=int(np.sum(y_tv[train_idx] == 0)),
                        n_malware=int(np.sum(y_tv[train_idx] == 1)),
                        device=config.device,
                        **_shape_args(X_tv[train_idx]),
                        random_state=config.seed,
                        n_estimators=config.n_estimators,
                        max_depth=config.max_depth,
                        learning_rate=config.learning_rate,
                        early_stopping_rounds=config.early_stopping_rounds,
                        min_child_weight=config.min_child_weight,
                        min_child_samples=config.min_child_samples,
                        num_leaves=config.num_leaves,
                        colsample_bytree=config.colsample_bytree,
                        subsample=config.subsample,
                        gamma=config.gamma,
                        reg_alpha=config.reg_alpha,
                        reg_lambda=config.reg_lambda,
                        monotone_constraints=config.monotone_constraints,
                        learner=config.learner,
                        scale_pos_weight_mult=config.scale_pos_weight_mult,
                        boosting_type=config.boosting_type,
                        extra_trees=config.extra_trees,
                        num_threads=config.num_threads,
                    )
                    _fit_model(
                        fold_model,
                        X_tv[train_idx], y_tv[train_idx],
                        sample_weight=sample_weight,
                        eval_set=[(X_tv[val_idx], y_tv[val_idx])],
                        early_stopping_rounds=config.early_stopping_rounds,
                    )
                else:
                    _fit_model(
                        fold_model,
                        X_tv[train_idx], y_tv[train_idx],
                        sample_weight=fold_base_weight,
                        eval_set=[(X_tv[val_idx], y_tv[val_idx])],
                        early_stopping_rounds=config.early_stopping_rounds,
                    )

            fold_preds = predict_proba(fold_model, X_tv[val_idx])
            cv_predictions[val_idx] = fold_preds

            fm = _compute_metrics(y_tv[val_idx], fold_preds)
            fold_metrics_list.append(fm)
            log.info(
                "fold %d/%d: fitted on %s",
                fold + 1,
                n_folds,
                booster_device(fold_model),
            )
            print(
                f"{fold + 1:<6} {fm['roc_auc']:>8.4f} {fm['f1']:>8.4f} "
                f"{fm['precision']:>8.4f} {fm['recall']:>8.4f}"
            )

        cv_auc = np.mean([m["roc_auc"] for m in fold_metrics_list])
        cv_f1 = np.mean([m["f1"] for m in fold_metrics_list])
        cv_prec = np.mean([m["precision"] for m in fold_metrics_list])
        cv_rec = np.mean([m["recall"] for m in fold_metrics_list])
        print(f"{'-' * 42}")
        print(f"{'Mean':<6} {cv_auc:>8.4f} {cv_f1:>8.4f} {cv_prec:>8.4f} {cv_rec:>8.4f}")

    # --- Train final model on all train+val data ---
    log.info("training final model on %d samples", len(y_tv))
    final_model = create_classifier(
        n_benign=n_tv_benign,
        n_malware=n_tv_malware,
        device=config.device,
        **_shape_args(X_tv),
        random_state=config.seed,
        n_estimators=config.n_estimators,
        max_depth=config.max_depth,
        learning_rate=config.learning_rate,
        early_stopping_rounds=config.early_stopping_rounds,
        min_child_weight=config.min_child_weight,
        min_child_samples=config.min_child_samples,
        num_leaves=config.num_leaves,
        colsample_bytree=config.colsample_bytree,
        subsample=config.subsample,
        gamma=config.gamma,
        reg_alpha=config.reg_alpha,
        reg_lambda=config.reg_lambda,
        monotone_constraints=config.monotone_constraints,
        learner=config.learner,
        scale_pos_weight_mult=config.scale_pos_weight_mult,
        boosting_type=config.boosting_type,
        extra_trees=config.extra_trees,
        num_threads=config.num_threads,
        )
    final_base_weight = _compute_benign_filetype_weights(
        file_types_tv,
        y_tv,
        weights_by_filetype=config.benign_filetype_weights,
    ) if file_types_tv is not None else None
    if X_holdout is not None:
        calibration_split, evaluation_split = _split_calibration_eval(
            X_holdout, y_holdout, seed=config.seed,
        )
        if calibration_split is None:
            log.warning(
                "holdout too small to separate calibration from evaluation; "
                "using same split for both"
            )
            X_calib, y_calib = X_holdout, y_holdout
            X_eval, y_eval = X_holdout, y_holdout
        else:
            X_calib, y_calib = calibration_split
            X_eval, y_eval = evaluation_split

        # Use calibration split for early stopping and threshold selection.
        if config.hard_negative_fraction > 0.0 and config.hard_negative_weight > 1.0:
            _fit_model(
                final_model,
                X_tv, y_tv,
                sample_weight=final_base_weight,
                eval_set=[(X_calib, y_calib)],
                early_stopping_rounds=config.early_stopping_rounds,
            )
            hard_negative_weight = _compute_hard_negative_weights(
                final_model,
                X_tv,
                y_tv,
                fraction=config.hard_negative_fraction,
                weight=config.hard_negative_weight,
            )
            sample_weight = _merge_sample_weights(final_base_weight, hard_negative_weight)
            final_model = create_classifier(
                n_benign=n_tv_benign,
                n_malware=n_tv_malware,
                device=config.device,
                **_shape_args(X_tv),
                random_state=config.seed,
                n_estimators=config.n_estimators,
                max_depth=config.max_depth,
                learning_rate=config.learning_rate,
                early_stopping_rounds=config.early_stopping_rounds,
                min_child_weight=config.min_child_weight,
                min_child_samples=config.min_child_samples,
                num_leaves=config.num_leaves,
                colsample_bytree=config.colsample_bytree,
                subsample=config.subsample,
                gamma=config.gamma,
                reg_alpha=config.reg_alpha,
                reg_lambda=config.reg_lambda,
                monotone_constraints=config.monotone_constraints,
                learner=config.learner,
                scale_pos_weight_mult=config.scale_pos_weight_mult,
                boosting_type=config.boosting_type,
                extra_trees=config.extra_trees,
                num_threads=config.num_threads,
            )
            _fit_model(
                final_model,
                X_tv, y_tv,
                sample_weight=sample_weight,
                eval_set=[(X_calib, y_calib)],
                early_stopping_rounds=config.early_stopping_rounds,
            )
        else:
            _fit_model(
                final_model,
                X_tv, y_tv,
                sample_weight=final_base_weight,
                eval_set=[(X_calib, y_calib)],
                early_stopping_rounds=config.early_stopping_rounds,
            )
        best_iter = getattr(final_model, "best_iteration", None)
        if best_iter is None:
            best_iter = getattr(final_model, "best_iteration_", None)
        if best_iter is not None:
            log.info(
                "final model: %d trees (early stopped at %d) on %s",
                final_model.n_estimators,
                best_iter,
                booster_device(final_model),
            )
        else:
            log.info("final model: %d trees on %s", final_model.n_estimators, booster_device(final_model))
        split_summary = {
            "policy": "train/calibration/evaluation" if calibration_split is not None else "train/holdout",
            "holdout_split": "stratified",
            "cv_split": cv_policy if n_folds >= 2 else "none",
            "train_samples": int(len(y_tv)),
            "calibration_samples": int(len(y_calib)),
            "evaluation_samples": int(len(y_eval)),
        }
    else:
        # No holdout — train without early stopping.
        if hasattr(final_model, "set_params"):
            final_model.set_params(early_stopping_rounds=None)
        _fit_model(final_model, X_tv, y_tv, sample_weight=final_base_weight)
        log.info("final model: %d trees on %s", final_model.n_estimators, booster_device(final_model))
        split_summary = {
            "policy": "train_only",
            "holdout_split": "none",
            "cv_split": cv_policy if n_folds >= 2 else "none",
            "train_samples": int(len(y_tv)),
            "calibration_samples": 0,
            "evaluation_samples": int(len(y_tv)),
        }

    # --- Evaluation ---
    iso_calibrator: IsotonicRegression | None = None
    if X_holdout is not None:
        calib_preds = predict_proba(final_model, X_calib)
        iso_calibrator = IsotonicRegression(out_of_bounds="clip")
        iso_calibrator.fit(calib_preds, y_calib)
        calib_preds_cal = iso_calibrator.predict(calib_preds)
        # Detect degenerate calibration (too few unique outputs = overfitting on small split).
        if len(np.unique(calib_preds_cal)) <= 5:
            log.warning(
                "isotonic calibration degenerate (%d unique outputs on %d samples); "
                "falling back to raw scores for threshold",
                len(np.unique(calib_preds_cal)), len(y_calib),
            )
            iso_calibrator = None
            optimal_threshold = _select_threshold(
                y_calib,
                calib_preds,
                mode=config.threshold_mode,
                beta=config.beta,
                max_fpr=config.threshold_fpr_target,
            )
            eval_preds = predict_proba(final_model, X_eval)
        else:
            optimal_threshold = _select_threshold(
                y_calib,
                calib_preds_cal,
                mode=config.threshold_mode,
                beta=config.beta,
                max_fpr=config.threshold_fpr_target,
            )
            eval_preds = iso_calibrator.predict(predict_proba(final_model, X_eval))
        metrics = _compute_metrics(y_eval, eval_preds, optimal_threshold)
        calibration = _calibration_summary(y_eval, eval_preds)
        eval_y = y_eval
        cal_label = "isotonic calibrated" if iso_calibrator is not None else "raw (calibration degenerate)"
        log.info("evaluation: AUC=%.4f F1=%.4f threshold=%.3f (%s)",
                 metrics["roc_auc"], metrics["f1"], optimal_threshold, cal_label)
    elif n_folds >= 2:
        optimal_threshold = _select_threshold(
            y_tv,
            cv_predictions,
            mode=config.threshold_mode,
            beta=config.beta,
            max_fpr=config.threshold_fpr_target,
        )
        metrics = _compute_metrics(y_tv, cv_predictions, optimal_threshold)
        calibration = _calibration_summary(y_tv, cv_predictions)
        eval_y = y_tv
        eval_preds = cv_predictions
    else:
        all_preds = predict_proba(final_model, X_tv)
        optimal_threshold = _select_threshold(
            y_tv,
            all_preds,
            mode=config.threshold_mode,
            beta=config.beta,
            max_fpr=config.threshold_fpr_target,
        )
        metrics = _compute_metrics(y_tv, all_preds, optimal_threshold)
        calibration = _calibration_summary(y_tv, all_preds)
        eval_y = y_tv
        eval_preds = all_preds

    y_binary = (eval_preds >= optimal_threshold).astype(int)
    cm = confusion_matrix(eval_y, y_binary).tolist()

    # cm layout: [[TN, FP], [FN, TP]]
    tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
    n_eval_benign = tn + fp
    n_eval_malware = tp + fn

    best_iteration = getattr(final_model, "best_iteration", None)
    if best_iteration is None:
        best_iteration = getattr(final_model, "best_iteration_", None)
    n_actual_trees = (best_iteration or config.n_estimators - 1) + 1
    imbalance = n_benign / max(n_malware, 1)

    print(f"\n{'=' * 54}")
    print("TRAINING RESULTS")
    print(f"{'=' * 54}")
    print(f"Dataset:  {len(y)} ({n_malware} malware, {n_benign} benign, {imbalance:.1f}:1)")
    print(f"Features: {n_features}")
    print(
        f"Model:    {config.learner}  {n_actual_trees}/{config.n_estimators} trees  "
        f"depth={config.max_depth}  lr={config.learning_rate}  "
        f"leaves={config.num_leaves or 'auto'}  min_child_samples={config.min_child_samples or 'auto'}  "
        f"β={config.beta}  seed={config.seed}"
    )
    holdout_label = "Holdout" if X_holdout is not None else f"CV (out-of-fold, n={len(eval_y)})"
    print(f"{'─' * 20} {holdout_label} {'─' * max(1, 54 - 22 - len(holdout_label))}")
    if X_holdout is not None:
        print(f"  n={len(y_eval)} ({n_eval_malware} malware, {n_eval_benign} benign)  threshold={optimal_threshold:.3f}")
    print(
        f"  ROC AUC  {metrics['roc_auc']:.4f}   Avg Prec  {metrics['avg_precision']:.4f}"
        f"   Brier  {metrics['brier']:.4f}   ECE  {float(calibration['ece']):.4f}"
    )
    print(
        f"  F1  {metrics['f1']:.4f}   Precision  {metrics['precision']:.4f}"
        f"   Recall  {metrics['recall']:.4f}"
    )
    if n_eval_malware:
        print(f"  TP {tp:5d} / {n_eval_malware}  ({tp / n_eval_malware:.2%})    FN {fn:5d} / {n_eval_malware}  ({fn / n_eval_malware:.2%})")
    if n_eval_benign:
        print(f"  TN {tn:5d} / {n_eval_benign}  ({tn / n_eval_benign:.2%})    FP {fp:5d} / {n_eval_benign}  ({fp / n_eval_benign:.2%})")
    print(f"{'=' * 54}")

    return TrainResult(
        model=final_model,
        metrics=metrics,
        calibration=calibration,
        optimal_threshold=optimal_threshold,
        confusion=cm,
        class_distribution={"benign": n_benign, "malware": n_malware},
        split_summary=split_summary,
        fold_metrics=fold_metrics_list,
        feature_means=feature_means.tolist(),
        feature_stds=feature_stds.tolist(),
        isotonic_calibrator=iso_calibrator,
        cv_predictions=cv_predictions,
        cv_labels=y_tv,
    )
