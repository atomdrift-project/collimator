"""Choose a provisional training configuration when no paired baseline exists.

Bootstrap choices are configuration starting points, never promotions. Compare
PR AUC only within one recent evaluation cohort; extreme-tail recall on a
small holdout is unsuitable for choosing the first specialist.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _snapshot(run: dict[str, Any]) -> int:
    value = run.get("snapshot_max_id") or (run.get("experiment_spec") or {}).get("snapshot_max_id")
    return int(value) if isinstance(value, (int, float)) and _finite(value) else 0


def evaluation_cohort(run: dict[str, Any]) -> str:
    """Fingerprint the snapshot and actual evaluation rows, ignoring row order."""
    ids = run.get("test_sample_row_ids")
    if isinstance(ids, list) and ids:
        identity: Any = sorted(ids)
    else:
        # Older run records lack row IDs. Keep distinct sampling profiles
        # separate rather than claiming their AP scores are comparable.
        spec = run.get("experiment_spec") or {}
        metrics = run.get("sampled_test_metrics") or {}
        identity = {
            "seed": run.get("seed", spec.get("seed")),
            "max_test_samples": spec.get("max_test_samples"),
            "test_natural_prevalence": spec.get("test_natural_prevalence"),
            "n_malware": metrics.get("n_malware_holdout"),
            "n_benign": metrics.get("n_benign_holdout"),
            "test_rows": run.get("test_rows"),
            "filters": spec.get("filters"),
        }
    payload = json.dumps(
        [_snapshot(run), run.get("evaluation_revision"), identity],
        sort_keys=True, separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def select_bootstrap_run(runs: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Select healthy, recent screen evidence without requiring a deployed model.

    Callers first prefer a registered promotion or a meaningful paired run.
    For bootstrap, require both classes (at least 30 of each), finite AP,
    a replayable config, and non-inverted ROC AUC when recorded. Restrict to
    the newest snapshot and the newest successful run's evaluation cohort.
    Rank AP first, then ROC AUC and ensemble support; tail recall is unused.
    """
    eligible = []
    for run in runs:
        metrics = run.get("sampled_test_metrics") or {}
        ap = metrics.get("avg_precision")
        if not _finite(ap) or not 0 < ap <= 1:
            continue
        auc = metrics.get("roc_auc")
        if auc is not None and (not _finite(auc) or not 0.5 <= auc <= 1):
            continue
        if not run.get("train_config") or not run.get("feature_env"):
            continue
        counts = [metrics.get("n_malware_holdout"), metrics.get("n_benign_holdout")]
        if any(not _finite(n) or n < 30 for n in counts):
            continue
        if run.get("error") or run.get("status") in {"failed", "crashed"}:
            continue
        eligible.append(run)
    if not eligible:
        return None
    latest = max(eligible, key=lambda r: (
        _snapshot(r), str(r.get("timestamp") or ""), str(r.get("experiment_key") or ""),
    ))
    cohort = evaluation_cohort(latest)
    comparable = [r for r in eligible if evaluation_cohort(r) == cohort]
    return max(comparable, key=lambda r: (
        float(r["sampled_test_metrics"]["avg_precision"]),
        float(r["sampled_test_metrics"].get("roc_auc") or 0),
        bool(r.get("save_all_seeds")),
        str(r.get("timestamp") or ""),
        str(r.get("experiment_key") or ""),
    ))


def replay_malware_score(run: dict[str, Any]) -> int | None:
    """Read the selected training cutoff, including legacy run records."""
    spec = run.get("experiment_spec") or {}
    for filters in (spec.get("filters") or {}, run.get("filters") or {}):
        value = filters.get("min_malware_training_score")
        if value is not None:
            if isinstance(value, bool) or not _finite(value) or value < 0 or int(value) != value:
                raise ValueError(f"invalid historical min_malware_training_score: {value!r}")
            return int(value)
    return None


def replay_feature_env(run: dict[str, Any]) -> dict[str, str]:
    """Replay feature knobs; use the current job's resources and name filter."""
    excluded = {
        "COLLIMATOR_NUM_THREADS", "COLLIMATOR_MEM_SHARES", "COLLIMATOR_EXPERIMENT_TAG",
        "COLLIMATOR_ALLOWED_FEATURES_FILE",
        "COLLIMATOR_TEXT_ENCODING_FEATURES",  # Raw strings were removed from reports.
    }
    return {
        str(k): ("1" if v is True else "0" if v is False else str(v))
        for k, v in (run.get("feature_env") or {}).items()
        if str(k).startswith("COLLIMATOR_") and k not in excluded and k not in {"COLLIMATOR_PG_SNAPSHOT", "COLLIMATOR_PG_SNAPSHOT_DATABASE"} and v is not None
    }


def selection_record(run: dict[str, Any], source: str) -> dict[str, Any]:
    return {
        "source": source,
        "experiment_key": run.get("experiment_key"),
        "idea": run.get("idea"),
        "timestamp": run.get("timestamp"),
        "snapshot_max_id": _snapshot(run),
        "evaluation_cohort": evaluation_cohort(run),
        "sampled_test_metrics": {
            k: v for k, v in (run.get("sampled_test_metrics") or {}).items()
            if k in {"avg_precision", "roc_auc", "n_malware_holdout", "n_benign_holdout"}
        },
        "train_config": run.get("train_config") or {},
        "min_malware_training_score": replay_malware_score(run),
        "feature_env": replay_feature_env(run),
    }


def write_selection_report(path: Path, records: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps({"routes": records}, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)
