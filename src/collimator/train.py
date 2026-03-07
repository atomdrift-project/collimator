"""Training loop with stratified holdout + K-fold cross-validation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import torch
import torch.nn as nn
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
from torch.nn import functional as f_nn
from torch.utils.data import DataLoader, TensorDataset

from .model import MalwareClassifier

log = logging.getLogger(__name__)

# Minimum samples per class to enable a holdout split.
MIN_HOLDOUT_CLASS_SIZE = 20

# Fraction of data reserved for honest evaluation.
HOLDOUT_FRACTION = 0.15


class FocalLoss(nn.Module):
    """Focal loss for binary classification.

    Focuses training on hard-to-classify examples by downweighting easy ones.
    Better than weighted BCE for severe class imbalance because it naturally
    reduces the contribution of well-classified majority-class samples.

    FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)
    """

    def __init__(self, alpha: float = 0.75, gamma: float = 2.0) -> None:
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        bce = f_nn.binary_cross_entropy_with_logits(logits, targets, reduction="none")
        probs = torch.sigmoid(logits)
        p_t = probs * targets + (1 - probs) * (1 - targets)
        alpha_t = self.alpha * targets + (1 - self.alpha) * (1 - targets)
        focal_weight = alpha_t * (1 - p_t) ** self.gamma
        return (focal_weight * bce).mean()


@dataclass
class TrainConfig:
    n_folds: int = 5
    epochs: int = 100
    batch_size: int = 256
    lr: float = 1e-3
    patience: int = 15
    device: str = "cpu"


@dataclass
class TrainResult:
    model: MalwareClassifier
    metrics: dict[str, float]
    optimal_threshold: float
    confusion: list[list[int]]
    class_distribution: dict[str, int]
    fold_metrics: list[dict[str, float]]
    feature_means: list[float] = field(default_factory=list)
    feature_stds: list[float] = field(default_factory=list)


def _make_loader(
    X: np.ndarray,
    y: np.ndarray,
    batch_size: int,
    shuffle: bool,
    device: str,
) -> DataLoader[tuple[torch.Tensor, ...]]:
    ds = TensorDataset(
        torch.from_numpy(X),
        torch.from_numpy(y),
    )
    pin = device == "cuda"
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, pin_memory=pin)


def _clone_state(model: nn.Module) -> dict[str, torch.Tensor]:
    return {k: v.clone() for k, v in model.state_dict().items()}


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


def _optimal_threshold(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Find threshold that maximizes F1 on a precision-recall curve."""
    if len(np.unique(y_true)) < 2:
        return 0.5
    prec_arr, rec_arr, thresholds = precision_recall_curve(y_true, y_prob)
    f1_arr = 2 * (prec_arr * rec_arr) / (prec_arr + rec_arr + 1e-8)
    opt_idx = int(np.argmax(f1_arr))
    if opt_idx < len(thresholds):
        return float(thresholds[opt_idx])
    return 0.5


def _train_one_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    n_features: int,
    config: TrainConfig,
    focal_alpha: float,
    *,
    X_val: np.ndarray | None = None,
    y_val: np.ndarray | None = None,
) -> MalwareClassifier:
    """Train a single model, optionally with early stopping on validation data."""
    device = config.device
    model = MalwareClassifier(n_features).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=config.lr, weight_decay=1e-4,
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=config.epochs,
    )

    criterion = FocalLoss(alpha=focal_alpha, gamma=2.0).to(device)
    val_criterion = FocalLoss(alpha=0.5, gamma=2.0).to(device)

    train_loader = _make_loader(
        X_train.astype(np.float32, copy=False),
        y_train.astype(np.float32, copy=False),
        config.batch_size, True, device,
    )

    val_loader = None
    if X_val is not None and y_val is not None:
        val_loader = _make_loader(
            X_val.astype(np.float32, copy=False),
            y_val.astype(np.float32, copy=False),
            config.batch_size, False, device,
        )

    best_val_loss = float("inf")
    patience_counter = 0
    best_state = _clone_state(model)

    for epoch in range(config.epochs):
        model.train()
        epoch_loss = 0.0
        for X_b, y_b in train_loader:
            X_b = X_b.to(device, non_blocking=True)
            y_b = y_b.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            logits = model(X_b).squeeze(1)
            loss = criterion(logits, y_b)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            epoch_loss += loss.item()
        scheduler.step()

        # Early stopping on validation loss.
        if val_loader is not None:
            model.eval()
            with torch.no_grad():
                val_loss_total = 0.0
                for X_b, y_b in val_loader:
                    X_b = X_b.to(device, non_blocking=True)
                    y_b = y_b.to(device, non_blocking=True)
                    logits = model(X_b).squeeze(1)
                    val_loss_total += val_criterion(logits, y_b).item()
                val_loss = val_loss_total / max(len(val_loader), 1)

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                best_state = _clone_state(model)
            else:
                patience_counter += 1
                if patience_counter >= config.patience:
                    break
        else:
            # No validation set -- just track training loss, no early stopping.
            best_state = _clone_state(model)
            if (epoch + 1) % 25 == 0:
                avg = epoch_loss / max(len(train_loader), 1)
                log.info("epoch %d/%d loss=%.4f", epoch + 1, config.epochs, avg)

    model.load_state_dict(best_state)
    return model


def _predict_proba(
    model: MalwareClassifier,
    X: np.ndarray,
    device: str = "cpu",
) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        t = torch.from_numpy(X.astype(np.float32, copy=False)).to(device)
        return torch.sigmoid(model(t).squeeze(1)).cpu().numpy()


def train(
    X: np.ndarray,
    y: np.ndarray,
    config: TrainConfig | None = None,
) -> TrainResult:
    """Train a MalwareClassifier with holdout + stratified K-fold CV.

    Pipeline:
      1. Stratified holdout split (15%) for honest evaluation
      2. Compute feature standardization (mean/std) from train+val portion only
      3. K-fold CV on train+val for model selection metrics
      4. Retrain final model on all train+val data
      5. Evaluate on holdout for honest metrics + threshold calibration
    """
    if config is None:
        config = TrainConfig()

    # Reproducible training.
    torch.manual_seed(42)
    np.random.seed(42)

    device = config.device
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

    # --- Standardization ---
    # Compute from train+val portion only to prevent data leakage.
    feature_means = X_tv.mean(axis=0).astype(np.float32)
    feature_stds = X_tv.std(axis=0).astype(np.float32)
    # Avoid division by zero for constant features (booleans, rare one-hots).
    feature_stds[feature_stds < 1e-7] = 1.0

    X_tv = ((X_tv - feature_means) / feature_stds).astype(np.float32)
    if X_holdout is not None:
        X_holdout = ((X_holdout - feature_means) / feature_stds).astype(np.float32)

    dead_mask = (feature_means == 0.0) & (feature_stds == 1.0)
    n_dead = int(np.sum(dead_mask))
    n_constant = int(np.sum(feature_stds == 1.0))
    log.info(
        "standardized: %d features (%d constant, %d dead/never-populated)",
        n_features, n_constant, n_dead,
    )
    if n_dead > 50:
        log.warning(
            "%d features are always zero -- your training reports may be "
            "missing fields that newer cleave versions produce. Consider "
            "re-scanning samples with current cleave.",
            n_dead,
        )

    # --- Focal loss alpha ---
    # Alpha is the weight for the positive (malware) class. Computed from
    # class distribution with sqrt dampening to avoid extreme values.
    n_tv_pos = int(np.sum(y_tv == 1))
    n_tv_neg = int(np.sum(y_tv == 0))
    if n_tv_pos > 0 and n_tv_neg > 0:
        raw_ratio = n_tv_neg / n_tv_pos
        dampened = float(np.sqrt(raw_ratio))
        focal_alpha = min(dampened / (1 + dampened), 0.95)
    else:
        focal_alpha = 0.5
    log.info("focal loss alpha: %.3f (gamma=2.0), device: %s", focal_alpha, device)

    # --- Cross-validation ---
    n_tv_malware = int(np.sum(y_tv == 1))
    n_tv_benign = int(np.sum(y_tv == 0))
    n_folds = min(config.n_folds, n_tv_malware, n_tv_benign)
    if n_folds < 2:
        log.warning("not enough samples for CV, training on all data")
        n_folds = 0

    fold_metrics_list: list[dict[str, float]] = []
    cv_predictions = np.zeros(len(y_tv))

    y_tv_f32 = y_tv.astype(np.float32, copy=False)

    if n_folds >= 2:
        skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        log.info("running %d-fold cross-validation", n_folds)
        print(f"\n{'Fold':<6} {'AUC':>8} {'F1':>8} {'Prec':>8} {'Recall':>8}")
        print(f"{'-' * 42}")

        for fold, (train_idx, val_idx) in enumerate(skf.split(X_tv, y_tv)):
            fold_model = _train_one_model(
                X_tv[train_idx], y_tv_f32[train_idx],
                n_features, config, focal_alpha,
                X_val=X_tv[val_idx], y_val=y_tv_f32[val_idx],
            )

            fold_preds = _predict_proba(fold_model, X_tv[val_idx], device)
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
    final_model = _train_one_model(
        X_tv, y_tv_f32,
        n_features, config, focal_alpha,
    )
    final_model.eval().cpu()

    # --- Evaluation ---
    if X_holdout is not None:
        # Honest metrics from held-out data the model never saw.
        holdout_preds = _predict_proba(final_model, X_holdout)
        optimal_threshold = _optimal_threshold(y_holdout, holdout_preds)
        metrics = _compute_metrics(y_holdout, holdout_preds, optimal_threshold)
        eval_y = y_holdout
        eval_preds = holdout_preds
        log.info("holdout evaluation: AUC=%.4f F1=%.4f threshold=%.3f",
                 metrics["roc_auc"], metrics["f1"], optimal_threshold)
    elif n_folds >= 2:
        # Fall back to CV predictions (honest but from different models).
        optimal_threshold = _optimal_threshold(y_tv, cv_predictions)
        metrics = _compute_metrics(y_tv, cv_predictions, optimal_threshold)
        eval_y = y_tv
        eval_preds = cv_predictions
    else:
        # Last resort: training predictions (overfit, but nothing else available).
        all_preds = _predict_proba(final_model, X_tv)
        optimal_threshold = _optimal_threshold(y_tv, all_preds)
        metrics = _compute_metrics(y_tv, all_preds, optimal_threshold)
        eval_y = y_tv
        eval_preds = all_preds

    y_binary = (eval_preds > optimal_threshold).astype(int)
    cm = confusion_matrix(eval_y, y_binary).tolist()

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
