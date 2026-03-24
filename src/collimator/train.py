"""Training loop with holdout + K-fold cross-validation."""

from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass, field

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
from sklearn.model_selection import GroupShuffleSplit, StratifiedGroupKFold, StratifiedKFold, train_test_split

from .model import create_classifier, predict_proba

log = logging.getLogger(__name__)

# Minimum samples per class to enable a holdout split.
MIN_HOLDOUT_CLASS_SIZE = 20
MIN_CALIBRATION_CLASS_SIZE = 8

# Fraction of non-test training data reserved for calibration/evaluation.
HOLDOUT_FRACTION = 0.10


@dataclass
class TrainConfig:
    seed: int = 42
    device: str | None = None
    holdout_fraction: float = HOLDOUT_FRACTION
    n_folds: int = 5
    n_estimators: int = 600
    max_depth: int = 10
    learning_rate: float = 0.02
    early_stopping_rounds: int = 100
    min_child_weight: int = 5
    colsample_bytree: float = 0.8
    subsample: float = 0.8
    gamma: float = 0.0
    reg_alpha: float = 0.0
    reg_lambda: float = 1.0
    beta: float = 1.0  # F-beta for threshold selection; 1.0 = balanced precision and recall
    monotone_constraints: str | dict[str, int] | None = None


@dataclass
class TrainResult:
    model: xgb.XGBClassifier
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


def _split_calibration_eval(
    X_holdout: np.ndarray | sp.spmatrix,
    y_holdout: np.ndarray,
    *,
    groups_holdout: np.ndarray | None = None,
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

    if groups_holdout is not None and len(np.unique(groups_holdout)) >= 2:
        calib_idx, eval_idx = _grouped_split_indices(
            y_holdout,
            groups_holdout,
            test_size=0.5,
            seed=seed,
        )
    else:
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


def _grouped_split_indices(
    y: np.ndarray,
    groups: np.ndarray,
    *,
    test_size: float,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return train/test indices using groups when feasible, else stratified rows."""
    n_splits = max(int(round(1.0 / max(test_size, 1e-6))), 2)
    unique_groups = np.unique(groups)
    if len(unique_groups) >= n_splits:
        try:
            splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
            train_idx, test_idx = next(splitter.split(np.zeros(len(y)), y, groups))
            return np.asarray(train_idx), np.asarray(test_idx)
        except ValueError:
            pass
    if len(unique_groups) >= 2:
        splitter = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
        train_idx, test_idx = next(splitter.split(np.zeros(len(y)), y, groups))
        return np.asarray(train_idx), np.asarray(test_idx)
    train_idx, test_idx = train_test_split(
        np.arange(len(y)),
        test_size=test_size,
        stratify=y,
        random_state=seed,
    )
    return np.asarray(train_idx), np.asarray(test_idx)


def train(
    X: np.ndarray | sp.spmatrix,
    y: np.ndarray,
    config: TrainConfig | None = None,
    feature_names: list[str] | None = None,
    groups: np.ndarray | None = None,
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
    if groups is not None and len(groups) != len(y):
        raise ValueError(f"groups length {len(groups)} does not match labels {len(y)}")

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
        groups_tv = groups
        X_holdout = y_holdout = groups_holdout = None
    elif n_min_class >= MIN_HOLDOUT_CLASS_SIZE:
        if groups is not None:
            tv_idx, holdout_idx = _grouped_split_indices(
                y,
                np.asarray(groups, dtype=object),
                test_size=config.holdout_fraction,
                seed=config.seed,
            )
        else:
            tv_idx, holdout_idx = train_test_split(
                np.arange(len(y)),
                test_size=config.holdout_fraction,
                stratify=y,
                random_state=config.seed,
            )
        X_tv, y_tv = X[tv_idx], y[tv_idx]
        X_holdout, y_holdout = X[holdout_idx], y[holdout_idx]
        groups_tv = np.asarray(groups, dtype=object)[tv_idx] if groups is not None else None
        groups_holdout = np.asarray(groups, dtype=object)[holdout_idx] if groups is not None else None
        log.info(
            "holdout: %d samples (%d malware, %d benign)",
            len(y_holdout),
            int(np.sum(y_holdout == 1)),
            int(np.sum(y_holdout == 0)),
        )
    else:
        X_tv, y_tv = X, y
        X_holdout = y_holdout = None
        groups_tv = np.asarray(groups, dtype=object) if groups is not None else None
        groups_holdout = None
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
        feature_means = np.asarray(X_tv.mean(axis=0), dtype=np.float32).ravel()
        # Var = E[X^2] - E[X]^2, computed without densifying.
        X_tv_sq = X_tv.copy()
        X_tv_sq.data **= 2
        variance = (
            np.asarray(X_tv_sq.mean(axis=0), dtype=np.float32).ravel()
            - feature_means ** 2
        )
        del X_tv_sq
        feature_stds = np.sqrt(np.maximum(variance, 0)).astype(np.float32)
        del variance
    else:
        feature_means = X_tv.mean(axis=0).astype(np.float32)
        feature_stds = X_tv.std(axis=0).astype(np.float32)
    feature_stds[feature_stds < 1e-7] = 1.0

    # --- Cross-validation ---
    n_tv_malware = int(np.sum(y_tv == 1))
    n_tv_benign = int(np.sum(y_tv == 0))
    n_folds = min(config.n_folds, n_tv_malware, n_tv_benign)
    if n_folds < 2:
        log.warning("not enough samples for CV, training on all data")
        n_folds = 0

    fold_metrics_list: list[dict[str, float]] = []
    cv_predictions = np.zeros(len(y_tv))
    cv_policy = "none"

    if n_folds >= 2:
        if groups_tv is not None and len(np.unique(groups_tv)) >= n_folds:
            skf = StratifiedGroupKFold(n_splits=n_folds, shuffle=True, random_state=config.seed)
            split_iter = skf.split(X_tv, y_tv, groups_tv)
            cv_policy = "grouped"
        else:
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
            fold_model = create_classifier(
                n_benign=int(np.sum(y_tv[train_idx] == 0)),
                n_malware=int(np.sum(y_tv[train_idx] == 1)),
                device=config.device,
                random_state=config.seed,
                n_estimators=config.n_estimators,
                max_depth=config.max_depth,
                learning_rate=config.learning_rate,
                early_stopping_rounds=config.early_stopping_rounds,
                min_child_weight=config.min_child_weight,
                colsample_bytree=config.colsample_bytree,
                subsample=config.subsample,
                gamma=config.gamma,
                reg_alpha=config.reg_alpha,
                reg_lambda=config.reg_lambda,
            )
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module="xgboost")
                fold_model.fit(
                    X_tv[train_idx], y_tv[train_idx],
                    eval_set=[(X_tv[val_idx], y_tv[val_idx])],
                    verbose=False,
                )

            fold_preds = predict_proba(fold_model, X_tv[val_idx])
            cv_predictions[val_idx] = fold_preds

            fm = _compute_metrics(y_tv[val_idx], fold_preds)
            fold_metrics_list.append(fm)
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
        random_state=config.seed,
        n_estimators=config.n_estimators,
        max_depth=config.max_depth,
        learning_rate=config.learning_rate,
        early_stopping_rounds=config.early_stopping_rounds,
        min_child_weight=config.min_child_weight,
        colsample_bytree=config.colsample_bytree,
        subsample=config.subsample,
        gamma=config.gamma,
        reg_alpha=config.reg_alpha,
        reg_lambda=config.reg_lambda,
        monotone_constraints=config.monotone_constraints,
        )
    if X_holdout is not None:
        calibration_split, evaluation_split = _split_calibration_eval(
            X_holdout, y_holdout, groups_holdout=groups_holdout, seed=config.seed,
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
        final_model.fit(
            X_tv, y_tv,
            eval_set=[(X_calib, y_calib)],
            verbose=False,
        )
        best_iter = getattr(final_model, "best_iteration", None)
        if best_iter is not None:
            log.info("final model: %d trees (early stopped at %d)", final_model.n_estimators, best_iter)
        else:
            log.info("final model: %d trees", final_model.n_estimators)
        split_summary = {
            "policy": "train/calibration/evaluation" if calibration_split is not None else "train/holdout",
            "holdout_split": "grouped" if groups is not None else "stratified",
            "cv_split": cv_policy if n_folds >= 2 else "none",
            "train_samples": int(len(y_tv)),
            "calibration_samples": int(len(y_calib)),
            "evaluation_samples": int(len(y_eval)),
        }
    else:
        # No holdout — train without early stopping.
        final_model.set_params(early_stopping_rounds=None)
        final_model.fit(X_tv, y_tv, verbose=False)
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
            optimal_threshold = _optimal_threshold(y_calib, calib_preds, beta=config.beta)
            eval_preds = predict_proba(final_model, X_eval)
        else:
            optimal_threshold = _optimal_threshold(y_calib, calib_preds_cal, beta=config.beta)
            eval_preds = iso_calibrator.predict(predict_proba(final_model, X_eval))
        metrics = _compute_metrics(y_eval, eval_preds, optimal_threshold)
        calibration = _calibration_summary(y_eval, eval_preds)
        eval_y = y_eval
        cal_label = "isotonic calibrated" if iso_calibrator is not None else "raw (calibration degenerate)"
        log.info("evaluation: AUC=%.4f F1=%.4f threshold=%.3f (%s)",
                 metrics["roc_auc"], metrics["f1"], optimal_threshold, cal_label)
    elif n_folds >= 2:
        optimal_threshold = _optimal_threshold(y_tv, cv_predictions, beta=config.beta)
        metrics = _compute_metrics(y_tv, cv_predictions, optimal_threshold)
        calibration = _calibration_summary(y_tv, cv_predictions)
        eval_y = y_tv
        eval_preds = cv_predictions
    else:
        all_preds = predict_proba(final_model, X_tv)
        optimal_threshold = _optimal_threshold(y_tv, all_preds)
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

    n_actual_trees = (getattr(final_model, "best_iteration", None) or config.n_estimators - 1) + 1
    imbalance = n_benign / max(n_malware, 1)

    print(f"\n{'=' * 54}")
    print("TRAINING RESULTS")
    print(f"{'=' * 54}")
    print(f"Dataset:  {len(y)} ({n_malware} malware, {n_benign} benign, {imbalance:.1f}:1)")
    print(f"Features: {n_features}")
    print(
        f"Model:    {n_actual_trees}/{config.n_estimators} trees  "
        f"depth={config.max_depth}  lr={config.learning_rate}  "
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
    )
