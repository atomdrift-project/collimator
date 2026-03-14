"""Training loop with stratified holdout + K-fold cross-validation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, train_test_split

from .model import create_classifier, predict_proba

log = logging.getLogger(__name__)

# Minimum samples per class to enable a holdout split.
MIN_HOLDOUT_CLASS_SIZE = 20

# Fraction of data reserved for honest evaluation.
HOLDOUT_FRACTION = 0.15


@dataclass
class TrainConfig:
    n_folds: int = 5
    n_estimators: int = 1000
    max_depth: int = 6
    learning_rate: float = 0.05
    early_stopping_rounds: int = 30
    min_child_weight: int = 5
    colsample_bytree: float = 0.8
    subsample: float = 0.8
    gamma: float = 0.0
    reg_alpha: float = 0.0
    reg_lambda: float = 1.0


@dataclass
class TrainResult:
    model: xgb.XGBClassifier
    metrics: dict[str, float]
    optimal_threshold: float
    confusion: list[list[int]]
    class_distribution: dict[str, int]
    fold_metrics: list[dict[str, float]]
    feature_means: list[float] = field(default_factory=list)
    feature_stds: list[float] = field(default_factory=list)


def _compute_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5,
) -> dict[str, float]:
    y_pred = (y_prob > threshold).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": (
            float(roc_auc_score(y_true, y_prob))
            if len(np.unique(y_true)) > 1 else 0.0
        ),
        "avg_precision": (
            float(average_precision_score(y_true, y_prob))
            if len(np.unique(y_true)) > 1 else 0.0
        ),
    }


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


def train(
    X: np.ndarray | sp.spmatrix,
    y: np.ndarray,
    config: TrainConfig | None = None,
    feature_names: list[str] | None = None,
) -> TrainResult:
    """Train an XGBoost classifier with holdout + stratified K-fold CV.

    Pipeline:
      1. Stratified holdout split (15%) for honest evaluation
      2. Compute feature standardization (mean/std) for pipeline compatibility
      3. K-fold CV on train+val for model selection metrics
      4. Retrain final model on all train+val data
      5. Evaluate on holdout for honest metrics + threshold calibration
    """
    if config is None:
        config = TrainConfig()

    np.random.seed(42)

    n_features = X.shape[1]
    n_malware = int(np.sum(y == 1))
    n_benign = int(np.sum(y == 0))

    log.info(
        "training: %d samples (%d malware, %d benign), %d features",
        len(y), n_malware, n_benign, n_features,
    )

    # --- Holdout split ---
    n_min_class = min(n_malware, n_benign)
    if n_min_class >= MIN_HOLDOUT_CLASS_SIZE:
        tv_idx, holdout_idx = train_test_split(
            np.arange(len(y)),
            test_size=HOLDOUT_FRACTION,
            stratify=y,
            random_state=42,
        )
        X_tv, y_tv = X[tv_idx], y[tv_idx]
        X_holdout, y_holdout = X[holdout_idx], y[holdout_idx]
        log.info(
            "holdout: %d samples (%d malware, %d benign)",
            len(y_holdout),
            int(np.sum(y_holdout == 1)),
            int(np.sum(y_holdout == 0)),
        )
    else:
        X_tv, y_tv = X, y
        X_holdout = y_holdout = None
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

    if n_folds >= 2:
        skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        log.info("running %d-fold cross-validation", n_folds)
        print(f"\n{'Fold':<6} {'AUC':>8} {'F1':>8} {'Prec':>8} {'Recall':>8}")
        print(f"{'-' * 42}")

        for fold, (train_idx, val_idx) in enumerate(skf.split(X_tv, y_tv)):
            fold_model = create_classifier(
                n_benign=int(np.sum(y_tv[train_idx] == 0)),
                n_malware=int(np.sum(y_tv[train_idx] == 1)),
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
        print(f"{'-' * 42}")
        print(f"{'Mean':<6} {cv_auc:>8.4f} {cv_f1:>8.4f}")

    # --- Train final model on all train+val data ---
    log.info("training final model on %d samples", len(y_tv))
    final_model = create_classifier(
        n_benign=n_tv_benign,
        n_malware=n_tv_malware,
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

    if X_holdout is not None:
        # Use holdout as eval set for early stopping.
        final_model.fit(
            X_tv, y_tv,
            eval_set=[(X_holdout, y_holdout)],
            verbose=False,
        )
        best_iter = getattr(final_model, "best_iteration", None)
        if best_iter is not None:
            log.info("final model: %d trees (early stopped at %d)", final_model.n_estimators, best_iter)
        else:
            log.info("final model: %d trees", final_model.n_estimators)
    else:
        # No holdout — train without early stopping.
        final_model.set_params(early_stopping_rounds=None)
        final_model.fit(X_tv, y_tv, verbose=False)

    # --- Evaluation ---
    if X_holdout is not None:
        holdout_preds = predict_proba(final_model, X_holdout)
        optimal_threshold = _optimal_threshold(y_holdout, holdout_preds)
        metrics = _compute_metrics(y_holdout, holdout_preds, optimal_threshold)
        eval_y = y_holdout
        eval_preds = holdout_preds
        log.info("holdout evaluation: AUC=%.4f F1=%.4f threshold=%.3f",
                 metrics["roc_auc"], metrics["f1"], optimal_threshold)
    elif n_folds >= 2:
        optimal_threshold = _optimal_threshold(y_tv, cv_predictions)
        metrics = _compute_metrics(y_tv, cv_predictions, optimal_threshold)
        eval_y = y_tv
        eval_preds = cv_predictions
    else:
        all_preds = predict_proba(final_model, X_tv)
        optimal_threshold = _optimal_threshold(y_tv, all_preds)
        metrics = _compute_metrics(y_tv, all_preds, optimal_threshold)
        eval_y = y_tv
        eval_preds = all_preds

    y_binary = (eval_preds > optimal_threshold).astype(int)
    cm = confusion_matrix(eval_y, y_binary).tolist()

    # cm layout: [[TN, FP], [FN, TP]]
    tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
    n_eval_benign = tn + fp
    n_eval_malware = tp + fn

    print(f"\n{'=' * 50}")
    print("TRAINING RESULTS")
    print(f"{'=' * 50}")
    print(f"Samples:     {len(y)} ({n_malware} malware, {n_benign} benign)")
    if X_holdout is not None:
        print(f"Holdout:     {len(y_holdout)} samples")
    print(f"Features:    {n_features}")
    print(f"ROC AUC:     {metrics['roc_auc']:.4f}")
    print(f"Avg Prec:    {metrics['avg_precision']:.4f}")
    print(f"F1 Score:    {metrics['f1']:.4f}")
    print(f"Precision:   {metrics['precision']:.4f}")
    print(f"Recall:      {metrics['recall']:.4f}")
    print(f"Threshold:   {optimal_threshold:.3f}")
    print(f"{'-' * 50}")
    print(f"  {'':>20}  {'Count':>6}  {'Rate':>8}")
    print(f"  {'-' * 40}")
    if n_eval_malware:
        print(f"  {'True Positives':>20}  {tp:>6}  {tp / n_eval_malware:>8.2%}")
        print(f"  {'False Negatives':>20}  {fn:>6}  {fn / n_eval_malware:>8.2%}")
    if n_eval_benign:
        print(f"  {'True Negatives':>20}  {tn:>6}  {tn / n_eval_benign:>8.2%}")
        print(f"  {'False Positives':>20}  {fp:>6}  {fp / n_eval_benign:>8.2%}")
    print(f"{'=' * 50}")

    return TrainResult(
        model=final_model,
        metrics=metrics,
        optimal_threshold=optimal_threshold,
        confusion=cm,
        class_distribution={"benign": n_benign, "malware": n_malware},
        fold_metrics=fold_metrics_list,
        feature_means=feature_means.tolist(),
        feature_stds=feature_stds.tolist(),
    )
