"""Feature-group ablation utilities."""

from __future__ import annotations

import json
from pathlib import Path

import scipy.sparse as sp

from . import data, features, train


def _drop_groups(
    X: sp.csr_matrix,
    spec: features.FeatureSpec,
    groups: list[str],
) -> tuple[sp.csr_matrix, list[str]]:
    group_indices = features.feature_group_indices(spec)
    drop_cols = {idx for group in groups for idx in group_indices.get(group, [])}
    keep_cols = [i for i in range(X.shape[1]) if i not in drop_cols]
    X_kept = X[:, keep_cols]
    kept_names = [spec.feature_names[i] for i in keep_cols]
    return X_kept, kept_names


def run_ablation(
    db_path: Path,
    *,
    n_workers: int = 1,
    seed: int = 42,
    groups: list[str] | None = None,
) -> list[dict[str, object]]:
    """Train baseline and leave-one-group-out ablations on the same dataset."""
    spec = features.build_vocab(
        (report for report, _label in data.stream_raw_reports(db_path, exclude_test=True)),
        n_workers=n_workers,
    )
    X, y = features.extract_stream(
        data.stream_raw_reports(db_path, exclude_test=True),
        spec,
        n_workers=n_workers,
    )
    group_names = groups if groups is not None else list(features.FEATURE_GROUPS)

    rows: list[dict[str, object]] = []

    baseline = train.train(
        X,
        y,
        train.TrainConfig(seed=seed),
        feature_names=spec.feature_names,
    )
    rows.append(
        {
            "ablation": "baseline",
            "dropped_groups": [],
            "n_features": X.shape[1],
            "metrics": baseline.metrics,
            "split_summary": baseline.split_summary,
        }
    )

    for group in group_names:
        X_drop, feature_names = _drop_groups(X, spec, [group])
        result = train.train(
            X_drop,
            y,
            train.TrainConfig(seed=seed),
            feature_names=feature_names,
        )
        rows.append(
            {
                "ablation": f"drop:{group}",
                "dropped_groups": [group],
                "n_features": X_drop.shape[1],
                "metrics": result.metrics,
                "split_summary": result.split_summary,
            }
        )

    return rows


def print_ablation(rows: list[dict[str, object]]) -> None:
    """Print a compact ablation table."""
    print("\nABLATION")
    print("=" * 72)
    print(f"{'Run':<18} {'Features':>9} {'ROC AUC':>8} {'AvgPrec':>8} {'Brier':>8} {'F1':>8}")
    print("-" * 72)
    for row in rows:
        metrics = row["metrics"]
        assert isinstance(metrics, dict)
        print(
            f"{str(row['ablation']):<18} {int(row['n_features']):>9} "
            f"{float(metrics['roc_auc']):>8.4f} {float(metrics['avg_precision']):>8.4f} "
            f"{float(metrics['brier']):>8.4f} {float(metrics['f1']):>8.4f}"
        )


def save_ablation(rows: list[dict[str, object]], output_path: Path) -> None:
    """Save ablation results as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(rows, f, indent=2)
