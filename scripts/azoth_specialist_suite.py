#!/usr/bin/env python3
"""Train and benchmark azoth filegroup/filetype specialist models."""

from __future__ import annotations

import argparse
import concurrent.futures
import contextlib
import json
import logging
import math
import os
import shutil
from dataclasses import asdict, fields, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from collimator import bundle, data, export, features, model, train

LOG = logging.getLogger("azoth_specialist_suite")

DEPLOYMENT_GROUPS: dict[str, tuple[str, ...]] = {
    "scripts": (
        "batch",
        "javascript",
        "lua",
        "perl",
        "php",
        "powershell",
        "python",
        "ruby",
        "shell",
        "typescript",
        "vbscript",
    ),
    "native": ("elf", "macho", "pe"),
    "portable": (
        "dex",
        "jar",
        "java_class",
        "pyc",
        "wasm",
    ),
    "archive": (
        "7z",
        "apk",
        "cab",
        "deb",
        "egg",
        "gz",
        "msi",
        "rar",
        "rpm",
        "tar",
        "tar.gz",
        "tgz",
        "vsix",
        "war",
        "whl",
        "xpi",
        "xz",
        "zip",
        "zst",
    ),
    "documents": ("doc", "docx", "html", "ole", "pdf", "ppt", "pptx", "rtf", "xls", "xlsx"),
    "source": (
        "c",
        "cpp",
        "csharp",
        "go",
        "java",
        "kotlin",
        "makefile",
        "rust",
        "scala",
        "swift",
    ),
    "config": ("ini", "json", "package.json", "plist", "toml", "xml", "yaml", "yml"),
    "media": ("bmp", "gif", "jpg", "jpeg", "mp3", "mp4", "png", "svg", "webp"),
}


def _label_int(label: str) -> int:
    return 1 if label == "bad" else 0


def _placeholder(db_path: Path | str) -> str:
    return "%s" if data._is_pg(db_path) else "?"  # noqa: SLF001


def _fetch_rows(
    db_path: Path | str,
    *,
    file_types: tuple[str, ...],
    max_id: int,
    min_score: int | None,
) -> list[tuple[int, int, bool, str]]:
    """Return row_id, label, is_test, file_type for labeled samples."""
    where = [
        "label IN ('bad', 'good')",
        "cleave_result IS NOT NULL",
        "skip = ''",
    ]
    params: list[Any] = []
    marker = _placeholder(db_path)
    if max_id > 0:
        where.append(f"id <= {marker}")
        params.append(int(max_id))
    if min_score is not None:
        where.append(f"score >= {marker}")
        params.append(int(min_score))

    select = (
        "SELECT id, sha256, label, canonical_sha256, "
        "COALESCE(NULLIF(file_type, ''), 'unknown')"
    )
    rows: list[tuple[int, int, bool, str]] = []
    with data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if data._is_pg(db_path):  # noqa: SLF001
            where.append("file_type = ANY(%s)")
            params.append(list(file_types))
            query = select + " FROM samples WHERE " + " AND ".join(where) + " ORDER BY id"
            with conn.cursor() as cur:
                cur.execute(query, params)
                for row_id, sha256, label, canonical, file_type in cur:
                    split_key = canonical or sha256
                    rows.append(
                        (
                            int(row_id),
                            _label_int(str(label)),
                            data.is_test_sample(split_key),
                            str(file_type),
                        ),
                    )
        else:
            placeholders = ",".join("?" for _ in file_types)
            where.append(f"file_type IN ({placeholders})")
            params.extend(file_types)
            query = select + " FROM samples WHERE " + " AND ".join(where) + " ORDER BY id"
            for row_id, sha256, label, canonical, file_type in conn.execute(query, params):
                split_key = canonical or sha256
                rows.append(
                    (
                        int(row_id),
                        _label_int(str(label)),
                        data.is_test_sample(split_key),
                        str(file_type),
                    ),
                )
    return rows


def _count_rows(
    db_path: Path | str,
    *,
    file_types: tuple[str, ...],
    max_id: int,
    min_score: int | None,
) -> dict[str, int]:
    marker = _placeholder(db_path)
    where = [
        "label IN ('bad', 'good')",
        "cleave_result IS NOT NULL",
        "skip = ''",
    ]
    params: list[Any] = []
    if max_id > 0:
        where.append(f"id <= {marker}")
        params.append(max_id)
    if min_score is not None:
        where.append(f"score >= {marker}")
        params.append(min_score)
    with data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if data._is_pg(db_path):  # noqa: SLF001
            where.append("file_type = ANY(%s)")
            params.append(list(file_types))
            query = (
                "SELECT"
                " COUNT(*) FILTER (WHERE label = 'bad') AS bad,"
                " COUNT(*) FILTER (WHERE label = 'good') AS good,"
                " COUNT(*) AS total"
                " FROM samples WHERE "
                + " AND ".join(where)
            )
            rows = list(data._execute(conn, query, params))  # noqa: SLF001
        else:
            placeholders = ",".join("?" for _ in file_types)
            where.append(f"file_type IN ({placeholders})")
            params.extend(file_types)
            query = (
                "SELECT"
                " SUM(CASE WHEN label = 'bad' THEN 1 ELSE 0 END) AS bad,"
                " SUM(CASE WHEN label = 'good' THEN 1 ELSE 0 END) AS good,"
                " COUNT(*) AS total"
                " FROM samples WHERE "
                + " AND ".join(where)
            )
            rows = list(conn.execute(query, params))
    bad, good, total = rows[0]
    return {"bad": int(bad or 0), "good": int(good or 0), "total": int(total or 0)}


def _eligible_filetypes(
    db_path: Path | str,
    *,
    max_id: int,
    min_score: int | None,
    min_bad: int,
    min_good: int,
) -> list[dict[str, Any]]:
    marker = _placeholder(db_path)
    where = [
        "label IN ('bad', 'good')",
        "cleave_result IS NOT NULL",
        "skip = ''",
    ]
    params: list[Any] = []
    if min_score is not None:
        where.append(f"score >= {marker}")
        params.append(min_score)
    if max_id > 0:
        where.append(f"id <= {marker}")
        params.append(max_id)
    query = (
        "SELECT COALESCE(NULLIF(file_type, ''), 'unknown') AS file_type,"
        " COUNT(*) FILTER (WHERE label = 'bad') AS bad,"
        " COUNT(*) FILTER (WHERE label = 'good') AS good,"
        " COUNT(*) AS total"
        " FROM samples WHERE "
        + " AND ".join(where)
        + " GROUP BY 1"
        + f" HAVING COUNT(*) FILTER (WHERE label = 'bad') >= {marker}"
        + f" AND COUNT(*) FILTER (WHERE label = 'good') >= {marker}"
        + " ORDER BY total DESC"
    )
    params.extend([min_bad, min_good])
    out: list[dict[str, Any]] = []
    with data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        rows = data._execute(conn, query, params)  # noqa: SLF001
        for file_type, bad, good, total in rows:
            out.append(
                {
                    "name": str(file_type),
                    "file_types": [str(file_type)],
                    "bad": int(bad),
                    "good": int(good),
                    "total": int(total),
                },
            )
    return out


def _ids_labels(
    rows: list[tuple[int, int, bool, str]],
    *,
    test: bool | None = None,
) -> list[tuple[int, int]]:
    return [
        (row_id, label)
        for row_id, label, is_test, _ft in rows
        if test is None or is_test == test
    ]


def _file_types(rows: list[tuple[int, int, bool, str]], *, test: bool | None = None) -> np.ndarray:
    return np.asarray(
        [
            ft
            for _row_id, _label, is_test, ft in rows
            if test is None or is_test == test
        ],
        dtype=object,
    )


def _classification_metrics(y_true: np.ndarray, y_prob: np.ndarray) -> dict[str, float]:
    if len(y_true) == 0:
        return {}
    from sklearn.metrics import precision_recall_curve

    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    f1_values = np.divide(
        2.0 * precision * recall,
        precision + recall,
        out=np.zeros_like(precision),
        where=(precision + recall) > 0,
    )
    best_idx = int(np.argmax(f1_values))
    best_threshold = 1.0 if best_idx >= len(thresholds) else float(thresholds[best_idx])
    y_pred = (y_prob >= best_threshold).astype(int)
    return {
        "roc_auc": (
            float(roc_auc_score(y_true, y_prob))
            if len(np.unique(y_true)) > 1
            else math.nan
        ),
        "avg_precision": (
            float(average_precision_score(y_true, y_prob))
            if len(np.unique(y_true)) > 1
            else math.nan
        ),
        "max_f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "max_f1_threshold": best_threshold,
        "precision_at_max_f1": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall_at_max_f1": float(recall_score(y_true, y_pred, zero_division=0)),
    }


def _fp_budget(n_benign: int, target_per_million: float) -> int:
    if target_per_million <= 0:
        return 0
    return min(n_benign, max(1, int(math.floor(n_benign * target_per_million / 1_000_000))))


def _operating_point(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    target_per_million: float,
) -> dict[str, float | int | None]:
    n_benign = int(np.sum(y_true == 0))
    n_malware = int(np.sum(y_true == 1))
    budget = _fp_budget(n_benign, target_per_million)
    order = np.argsort(-y_prob, kind="mergesort")
    sorted_y = y_true[order]
    sorted_p = y_prob[order]
    tp_cum = np.cumsum(sorted_y == 1)
    fp_cum = np.cumsum(sorted_y == 0)
    best: dict[str, float | int | None] | None = None
    idx = 0
    while idx < len(sorted_p):
        threshold = sorted_p[idx]
        end = idx
        while end + 1 < len(sorted_p) and sorted_p[end + 1] == threshold:
            end += 1
        fp = int(fp_cum[end])
        if fp > budget:
            break
        tp = int(tp_cum[end])
        best = {
            "target_per_million": float(target_per_million),
            "budget": budget,
            "threshold": float(threshold),
            "recall": float(tp / n_malware) if n_malware else math.nan,
            "precision": float(tp / max(tp + fp, 1)),
            "fp": fp,
            "tp": tp,
            "fn": n_malware - tp,
            "tn": n_benign - fp,
            "fp_per_million": float(fp * 1_000_000.0 / n_benign) if n_benign else math.nan,
        }
        idx = end + 1
    if best is not None:
        return best
    return {
        "target_per_million": float(target_per_million),
        "budget": budget,
        "threshold": None,
        "recall": None,
        "precision": None,
        "fp": None,
        "tp": None,
        "fn": None,
        "tn": None,
        "fp_per_million": None,
    }


def _level_table(y_true: np.ndarray, y_prob: np.ndarray) -> list[dict[str, Any]]:
    return [
        {
            "level": level,
            "hostile": _operating_point(y_true, y_prob, float(level)),
            "suspicious": _operating_point(y_true, y_prob, float((level + 1) * 8)),
        }
        for level in range(10)
    ]


def _parse_mask_specs(values: list[str]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"invalid --mask-spec {value!r}; expected name=feature_spec.json")
        name, path = value.split("=", 1)
        out[name] = Path(path)
    return out


def _parse_feature_envs(values: list[str]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for value in values:
        try:
            route, assignment = value.split(":", 1)
            key, raw = assignment.split("=", 1)
        except ValueError as exc:
            raise ValueError(
                f"invalid --feature-env {value!r}; expected name:ENV_VAR=value",
            ) from exc
        route = route.strip()
        key = key.strip()
        if not route or not key:
            raise ValueError(f"invalid --feature-env {value!r}; route and ENV_VAR are required")
        out.setdefault(route, {})[key] = raw
    return out


def _train_config_field_names() -> set[str]:
    return {field.name for field in fields(train.TrainConfig)} - {"learner"}


def _route_key_for_target(target: dict[str, Any]) -> str:
    """Canonical route key as recorded in autocollie run JSONs."""
    name = str(target["name"])
    if target["kind"] == "filegroup":
        return f"filegroups/{name}"
    return f"filetypes/{name}"


def _load_autocollie_best_per_route(
    runs_dir: Path,
    targets: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, str]]]:
    """Scan ``runs_dir/*.json`` for each target's highest-F1 historical run and
    return its train_config + feature_env as per-route override dicts.

    This is how autocollie's discovered wins flow into ``make
    azoth-specialist-suite`` retrains: instead of every retrain reverting to
    the Makefile's hardcoded defaults (which predate autocollie), the suite
    picks each route's deployed-best-quality-of-fit experiment and replays
    its config.

    Selection rule: highest avg_precision (PR AUC) in
    ``sampled_test_metrics``.  When multiple runs tie, the most recent
    timestamp wins (replay-stable across re-runs).  Save-all-seeds (item-A
    averaged) runs are preferred over single-seed when they exist for a
    route, since those are the legitimate multi-seed baselines and produce
    honest comparisons.

    PR AUC is the headline ranking metric for malware classification: it
    summarizes recall vs precision across the operating range and isn't
    swamped by benign mass the way ROC AUC is on this imbalanced corpus.

    Routes with no historical runs in ``runs_dir`` get empty overrides and
    fall through to the suite's CLI defaults — same as before.

    Returns ``(train_overrides_by_route, feature_envs_by_route)``.  Both maps
    are keyed by the canonical route name (e.g. ``filetypes/perl``).
    """
    if not runs_dir.is_dir():
        LOG.info("autocollie-best: %s is not a directory; skipping", runs_dir)
        return {}, {}

    targeted_routes = {_route_key_for_target(t) for t in targets}
    # Track best per route as (f1, save_all_seeds, timestamp, run_dict).
    best: dict[str, tuple[float, bool, str, dict[str, Any]]] = {}
    for path in runs_dir.glob("*.json"):
        # Skip the *_feature_spec.json sidecars and the multi-seed dirs.
        if path.name.endswith("_feature_spec.json"):
            continue
        try:
            with open(path) as f:
                run = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        route = run.get("route")
        if route not in targeted_routes:
            continue
        metrics = run.get("sampled_test_metrics") or {}
        ap = metrics.get("avg_precision")
        if not isinstance(ap, (int, float)):
            continue
        save_all = bool(run.get("save_all_seeds"))
        timestamp = str(run.get("timestamp") or "")
        # Tuple ordering: avg_precision first (max), then save_all_seeds
        # (prefer True), then timestamp (prefer newer).  Python tuple comparison
        # is stable so this gives a total ordering.
        candidate = (float(ap), save_all, timestamp, run)
        prev = best.get(route)
        if prev is None or candidate[:3] > prev[:3]:
            best[route] = candidate

    valid_train_fields = _train_config_field_names()
    train_overrides: dict[str, dict[str, Any]] = {}
    feature_envs: dict[str, dict[str, str]] = {}
    for route, (ap, save_all, _ts, run) in best.items():
        train_cfg = run.get("train_config") or {}
        # Filter to TrainConfig fields the suite knows about; drop unknown
        # keys silently rather than raising — tolerates schema drift.
        cfg_overrides = {
            k: v for k, v in train_cfg.items()
            if k in valid_train_fields and v is not None
        }
        if cfg_overrides:
            train_overrides[route] = cfg_overrides

        env = run.get("feature_env") or {}
        # feature_env in run JSONs is already namespaced (COLLIMATOR_*).
        env_overrides = {str(k): str(v) for k, v in env.items() if str(k).startswith("COLLIMATOR_")}
        if env_overrides:
            feature_envs[route] = env_overrides

        LOG.info(
            "autocollie-best: %s -> key=%s avg_precision=%.4f save_all=%s overrides=%d env=%d",
            route, run.get("experiment_key", "?"), ap, save_all,
            len(cfg_overrides), len(env_overrides),
        )

    return train_overrides, feature_envs


def _merge_route_overrides(
    cli: dict[str, dict[str, Any]],
    auto: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Combine autocollie-best per-route overrides with CLI per-route overrides.

    CLI wins on collisions (operator intent overrides auto-discovery).  Both
    inputs use the canonical route-key form (``filegroups/X`` /
    ``filetypes/Y``); the resulting map gets re-keyed for the suite's
    ``_target_override_keys`` lookup, which checks both the bare-name form
    and the prefixed form.  We emit only the prefixed form here; the bare
    name is left for the operator's manual override (no auto-population).
    """
    merged: dict[str, dict[str, Any]] = {}
    for route, fields_dict in auto.items():
        merged[route] = dict(fields_dict)
    for route, fields_dict in cli.items():
        merged.setdefault(route, {}).update(fields_dict)
    return merged


def _coerce_train_override(field_name: str, raw: str) -> Any:
    if raw.lower() in {"none", "null"}:
        return None
    int_fields = {
        "seed",
        "n_folds",
        "n_estimators",
        "max_depth",
        "early_stopping_rounds",
        "min_child_weight",
        "min_child_samples",
        "num_leaves",
    }
    float_fields = {
        "holdout_fraction",
        "learning_rate",
        "colsample_bytree",
        "subsample",
        "gamma",
        "reg_alpha",
        "reg_lambda",
        "beta",
        "threshold_fpr_target",
        "hard_negative_fraction",
        "hard_negative_weight",
    }
    json_fields = {"monotone_constraints", "benign_filetype_weights"}
    if field_name in int_fields:
        return int(raw)
    if field_name in float_fields:
        return float(raw)
    if field_name in json_fields:
        return json.loads(raw)
    return raw


def _parse_train_overrides(values: list[str]) -> dict[str, dict[str, Any]]:
    valid_fields = _train_config_field_names()
    out: dict[str, dict[str, Any]] = {}
    for value in values:
        try:
            route, assignment = value.split(":", 1)
            key, raw = assignment.split("=", 1)
        except ValueError as exc:
            raise ValueError(
                f"invalid --train-override {value!r}; expected route:train_config_field=value",
            ) from exc
        route = route.strip()
        key = key.strip()
        if not route or not key:
            raise ValueError(f"invalid --train-override {value!r}; route and field are required")
        if key not in valid_fields:
            raise ValueError(
                f"invalid --train-override {value!r}; {key!r} is not a TrainConfig field",
            )
        out.setdefault(route, {})[key] = _coerce_train_override(key, raw)
    return out


def _target_override_keys(target: dict[str, Any]) -> tuple[str, ...]:
    name = str(target["name"])
    if target["kind"] == "filegroup":
        return name, f"filegroups/{name}"
    return name, f"filetypes/{name}"


def _route_train_config(
    base_config: train.TrainConfig,
    target: dict[str, Any],
    train_overrides: dict[str, dict[str, Any]],
) -> train.TrainConfig:
    overrides: dict[str, Any] = {}
    for key in _target_override_keys(target):
        overrides.update(train_overrides.get(key, {}))
    if not overrides:
        return base_config
    LOG.info("%s: using route train overrides %s", target["name"], dict(sorted(overrides.items())))
    return replace(base_config, **overrides)


@contextlib.contextmanager
def _temporary_feature_env(overrides: dict[str, str]):
    if not overrides:
        yield
        return
    previous = {key: os.environ.get(key) for key in overrides}
    try:
        os.environ.update(overrides)
        features.feature_config_from_env.cache_clear()
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        features.feature_config_from_env.cache_clear()


def _allowed_mask_from_spec(
    general_spec: features.FeatureSpec,
    mask_spec_path: Path | None,
) -> tuple[np.ndarray | None, dict[str, Any] | None]:
    if mask_spec_path is None:
        return None, None
    mask_spec = features.FeatureSpec.load(mask_spec_path)
    allowed_names = set(mask_spec.feature_names)
    general_names = general_spec.feature_names
    mask = np.asarray([name in allowed_names for name in general_names], dtype=bool)
    missing = len(allowed_names.difference(general_names))
    metadata = {
        "policy": "general_shared_masked",
        "source_spec": str(mask_spec_path),
        "source_features": int(len(allowed_names)),
        "allowed_features": int(np.sum(mask)),
        "missing_features": int(missing),
    }
    return mask, metadata


def _mask_sparse_columns(x_matrix: sp.spmatrix, allowed_mask: np.ndarray | None) -> sp.csr_matrix:
    if allowed_mask is None:
        return x_matrix.tocsr()
    coo = x_matrix.tocoo(copy=False)
    keep = allowed_mask[coo.col]
    return sp.csr_matrix(
        (coo.data[keep], (coo.row[keep], coo.col[keep])),
        shape=x_matrix.shape,
    )


def _train_one(
    *,
    db_path: Path | str,
    name: str,
    kind: str,
    file_types: tuple[str, ...],
    output_dir: Path,
    general_spec_path: Path,
    general_spec: features.FeatureSpec,
    mask_spec_path: Path | None,
    feature_env: dict[str, str],
    config: train.TrainConfig,
    workers: int,
    max_id: int,
    filegroup_score_filter: bool,
    n_seed_extras: int = 0,
) -> dict[str, Any]:
    train_rows = _fetch_rows(
        db_path,
        file_types=file_types,
        max_id=max_id,
        min_score=data.MIN_SAMPLE_SCORE if kind == "filegroup" and filegroup_score_filter else None,
    )
    benchmark_rows = _fetch_rows(db_path, file_types=file_types, max_id=max_id, min_score=None)
    train_ids_labels = _ids_labels(train_rows, test=False)
    benchmark_ids_labels = _ids_labels(benchmark_rows, test=True)
    if not train_ids_labels or not benchmark_ids_labels:
        raise ValueError(f"{name}: no train or benchmark rows")

    spec = general_spec
    spec_path = general_spec_path
    feature_spec_policy = "general_shared"
    feature_env_metadata: dict[str, Any] | None = None
    with _temporary_feature_env(feature_env):
        if feature_env:
            LOG.info("%s: building route-specific feature spec with %d env overrides", name, len(feature_env))
            spec = features.build_vocab_from_db(db_path, train_ids_labels, n_workers=workers)
            spec_path = output_dir / "feature_spec.json"
            feature_spec_policy = "route_specific"
            feature_env_metadata = dict(sorted(feature_env.items()))
        LOG.info(
            "%s: extracting train and benchmark features with %s spec (%d features)",
            name,
            feature_spec_policy,
            spec.total_features,
        )
        x_train, y_train, x_bench, y_bench = features.extract_partitioned_from_db(
            db_path,
            train_ids_labels,
            benchmark_ids_labels,
            spec,
            n_workers=workers,
        )
    allowed_mask, mask_metadata = _allowed_mask_from_spec(spec, mask_spec_path)
    if mask_metadata is not None:
        LOG.info(
            "%s: applying feature mask from %s (%d/%d general features, %d missing)",
            name,
            mask_spec_path,
            mask_metadata["allowed_features"],
            spec.total_features,
            mask_metadata["missing_features"],
        )
        x_train = _mask_sparse_columns(x_train, allowed_mask)
        x_bench = _mask_sparse_columns(x_bench, allowed_mask)
    sample_file_types = _file_types(train_rows, test=False)
    LOG.info("%s: training (seed=%d)", name, config.seed)
    result = train.train(
        x_train,
        y_train,
        config,
        feature_names=spec.feature_names,
        sample_file_types=sample_file_types,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    if feature_env:
        spec.save(output_dir / "feature_spec.json")
    else:
        shutil.copy2(spec_path, output_dir / "feature_spec.json")

    # Multi-seed (item A): with --n-seed-extras=K, train K additional models
    # against the SAME extracted matrix (cheap — extraction was the slow part)
    # using seeds [base+1, base+K]. All K+1 ship under models/seed_<S>.txt and
    # litmus averages their predictions at inference time. Variance reduction
    # by ~(K+1) without the bias trade-offs of within-model bagging.
    extra_models: list[Any] = []
    if n_seed_extras > 0:
        # Atomic write per seed: train, write to a `.tmp` sibling, then
        # rename in place. A kill mid-loop leaves at most one stray `.tmp`
        # which `bundle.model_files()` skips because it filters by the
        # canonical extension. The legacy single-model artifact is unlinked
        # LAST — only after every new seed file is durable on disk — so
        # an interrupted run never produces a bundle with zero models.
        def _save_seed_atomic(seed: int, model_obj: Any) -> None:
            final_path = bundle.write_seed_model_path(output_dir, seed, "txt")
            tmp_path = final_path.with_name(f".{final_path.name}.tmp")
            export.save_model(model_obj, tmp_path)
            os.replace(tmp_path, final_path)
        _save_seed_atomic(int(config.seed), result.model)
        for offset in range(1, n_seed_extras + 1):
            extra_seed = int(config.seed) + offset
            LOG.info("%s: training seed extra %d/%d (seed=%d)",
                     name, offset, n_seed_extras, extra_seed)
            extra_result = train.train(
                x_train,
                y_train,
                replace(config, seed=extra_seed),
                feature_names=spec.feature_names,
                sample_file_types=sample_file_types,
            )
            _save_seed_atomic(extra_seed, extra_result.model)
            extra_models.append(extra_result.model)
        for legacy in (output_dir / "model.txt", output_dir / "model.json"):
            if legacy.is_file():
                legacy.unlink()
    else:
        export.save_model(result.model, output_dir / "model.txt")

    # Benchmark probabilities use the same averaging the deployed runtime will,
    # so reported metrics match what litmus emits.
    if extra_models:
        probs = model.predict_proba(result.model, x_bench).astype(np.float64)
        for extra in extra_models:
            probs += model.predict_proba(extra, x_bench).astype(np.float64)
        probs = (probs / float(1 + len(extra_models))).astype(np.float32)
    else:
        probs = model.predict_proba(result.model, x_bench)
    # `model_path` reflects the layout actually written: legacy single-model
    # (model.txt) for K=0, primary multi-seed file (models/seed_<base>.txt)
    # for K>=1. Downstream consumers that need every seed should use
    # ``collimator.bundle.model_files``.
    primary_model = bundle.primary_model_file(output_dir)
    payload = {
        "name": name,
        "kind": kind,
        "file_types": list(file_types),
        "output_dir": str(output_dir),
        "model_path": str(primary_model),
        "n_seed_models": 1 + len(extra_models),
        "spec_path": str(output_dir / "feature_spec.json"),
        "train_rows": int(len(y_train)),
        "train_malware": int(np.sum(y_train == 1)),
        "train_benign": int(np.sum(y_train == 0)),
        "benchmark_rows": int(len(y_bench)),
        "benchmark_malware": int(np.sum(y_bench == 1)),
        "benchmark_benign": int(np.sum(y_bench == 0)),
        "n_features": int(spec.total_features),
        "feature_spec_policy": (
            f"{feature_spec_policy}_masked" if mask_metadata is not None else feature_spec_policy
        ),
        "feature_mask": mask_metadata,
        "feature_env": feature_env_metadata,
        "train_metrics": result.metrics,
        "metrics": _classification_metrics(y_bench, probs),
        "levels": _level_table(y_bench, probs),
        "train_config": asdict(config),
        "train_score_filter": (
            {"min_score": data.MIN_SAMPLE_SCORE, "scope": "all labels"}
            if kind == "filegroup" and filegroup_score_filter
            else {"min_score": None, "scope": "full labeled filetype corpus"}
        ),
    }
    with open(output_dir / "benchmark.json", "w") as f:
        json.dump(payload, f, indent=2)
    return payload


def _publish_general(general_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("model.txt", "feature_spec.json", "threshold_tuning.json"):
        src = general_dir / filename
        dst = output_dir / filename
        if src.exists() and src.resolve() != dst.resolve():
            shutil.copy2(src, dst)
    return {
        "name": "general",
        "kind": "general",
        "output_dir": str(output_dir),
        "source_dir": str(general_dir),
    }


def _targets(args: argparse.Namespace) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for name, file_types in DEPLOYMENT_GROUPS.items():
        counts = _count_rows(
            args.db,
            file_types=file_types,
            max_id=args.max_id,
            min_score=data.MIN_SAMPLE_SCORE,
        )
        if counts["bad"] < args.min_bad or counts["good"] < args.min_good:
            LOG.info(
                "%s: skipping filegroup, below gate (%d bad, %d good)",
                name,
                counts["bad"],
                counts["good"],
            )
            continue
        groups.append(
            {
                "name": name,
                "kind": "filegroup",
                "file_types": sorted(file_types),
                **counts,
            },
        )
    filetypes = [
        {
            "name": row["name"],
            "kind": "filetype",
            "file_types": row["file_types"],
            "bad": row["bad"],
            "good": row["good"],
            "total": row["total"],
        }
        for row in _eligible_filetypes(
            args.db,
            max_id=args.max_id,
            min_score=None,
            min_bad=args.min_bad,
            min_good=args.min_good,
        )
    ]
    selected = groups + filetypes
    if args.only:
        requested = set(args.only)
        selected = [target for target in selected if target["name"] in requested]
    return selected


def _pool_init(log_level: str) -> None:
    """Initialize logging in each worker. With fork start-method workers
    inherit handlers; with spawn they don't, so set up explicitly."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _train_target_worker(job: dict[str, Any]) -> dict[str, Any]:
    """ProcessPool entrypoint. Loads general_spec inside the worker so the
    parent doesn't have to pickle it across the boundary, and isolates the
    os.environ mutations performed by ``_temporary_feature_env`` from sibling
    workers."""
    target = job["target"]
    try:
        general_spec = features.FeatureSpec.load(job["general_spec_path"])
        return _train_one(
            db_path=job["db_path"],
            name=str(target["name"]),
            kind=str(target["kind"]),
            file_types=tuple(target["file_types"]),
            output_dir=job["output_dir"],
            general_spec_path=job["general_spec_path"],
            general_spec=general_spec,
            mask_spec_path=job.get("mask_spec_path"),
            feature_env=job.get("feature_env") or {},
            config=job["route_config"],
            workers=job["workers"],
            max_id=job["max_id"],
            filegroup_score_filter=job["filegroup_score_filter"],
            n_seed_extras=job["n_seed_extras"],
        )
    except Exception:
        LOG.exception("%s: failed", target["name"])
        return {"name": target["name"], "kind": target["kind"], "error": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--output-root", type=Path, default=Path("out/models/azoth"))
    parser.add_argument("--summary", type=Path, default=Path("out/models/azoth/specialists.json"))
    parser.add_argument(
        "--general-dir",
        type=Path,
        default=Path("out/models/azoth/general"),
    )
    parser.add_argument("--max-id", type=int, default=0)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-folds", type=int, default=0)
    parser.add_argument("--n-estimators", type=int, default=400)
    parser.add_argument("--max-depth", type=int, default=12)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--early-stopping-rounds", type=int, default=50)
    parser.add_argument("--num-leaves", type=int, default=96)
    parser.add_argument("--min-child-samples", type=int, default=100)
    parser.add_argument("--hard-negative-fraction", type=float, default=0.0)
    parser.add_argument("--hard-negative-weight", type=float, default=1.0)
    parser.add_argument(
        "--train-override",
        action="append",
        default=[],
        help="Per-route TrainConfig override, format route:field=value; repeatable",
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--n-seed-extras",
        type=int,
        default=0,
        help=(
            "Train this many additional seeds per route against the same "
            "extracted matrix. K=0 (default) preserves the legacy single-model "
            "layout (one model.txt per route). K>=1 switches to the multi-seed "
            "layout (models/seed_<S>.txt) so litmus averages predictions across "
            "K+1 trained ensembles, reducing seed-driven variance by ~K+1."
        ),
    )
    parser.add_argument("--min-bad", type=int, default=50)
    parser.add_argument("--min-good", type=int, default=50)
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--mask-spec", action="append", default=[])
    parser.add_argument(
        "--feature-env",
        action="append",
        default=[],
        help="Route-specific feature env override, format name:ENV_VAR=value; repeatable",
    )
    parser.add_argument(
        "--autocollie-best-runs-dir",
        type=Path,
        default=None,
        help=(
            "Optional directory of autocollie experiment run JSONs (typically "
            "out/experiments/azoth/runs). When set, the suite picks each "
            "route's highest-F1 historical run and applies its train_config + "
            "feature_env as automatic per-route overrides. Without this flag, "
            "every retrain reverts to Makefile defaults — autocollie's wins are "
            "lost. Explicit --train-override / --feature-env still take "
            "precedence over auto-discovered values."
        ),
    )
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument(
        "--filegroup-score-filter",
        action="store_true",
        help="Train filegroup specialists on score-filtered rows instead of the full labeled route corpus.",
    )
    parser.add_argument("--no-filegroup-score-filter", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument(
        "--parallelism",
        type=int,
        default=1,
        help=(
            "Train this many specialists concurrently in worker processes. "
            "Default 1 (sequential). Use 2-3 on CPU hosts; mind that each "
            "route already uses --workers for feature extraction and "
            "LightGBM is multi-threaded, so total CPU load = parallelism * "
            "(extract_workers + lgbm_threads). GPU mode should stay at 1."
        ),
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args.max_id = args.max_id or data.snapshot_max_id(args.db)
    LOG.info("snapshot max_id=%d", args.max_id)
    general_spec_path = args.general_dir / "feature_spec.json"
    general_spec = features.FeatureSpec.load(general_spec_path)
    mask_specs = _parse_mask_specs(args.mask_spec)
    feature_envs = _parse_feature_envs(args.feature_env)
    train_overrides = _parse_train_overrides(args.train_override)

    # Resolve targets early so we can scope the autocollie-best scan to
    # routes we'll actually train.
    targets = _targets(args)

    if args.autocollie_best_runs_dir is not None:
        auto_train, auto_env = _load_autocollie_best_per_route(
            args.autocollie_best_runs_dir, targets
        )
        # Operator overrides (CLI --train-override / --feature-env) win on
        # collisions, so the merge order is auto-first then CLI on top.
        train_overrides = _merge_route_overrides(train_overrides, auto_train)
        feature_envs = _merge_route_overrides(feature_envs, auto_env)
        if auto_train or auto_env:
            LOG.info(
                "autocollie-best: applied overrides for %d routes (train) / %d routes (feature_env)",
                len(auto_train), len(auto_env),
            )
        else:
            LOG.info("autocollie-best: no historical runs found in %s for any target route",
                     args.autocollie_best_runs_dir)

    config = train.TrainConfig(
        learner="azoth",
        seed=args.seed,
        device=args.device,
        n_folds=args.n_folds,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        learning_rate=args.learning_rate,
        early_stopping_rounds=args.early_stopping_rounds,
        num_leaves=args.num_leaves,
        min_child_samples=args.min_child_samples,
        hard_negative_fraction=args.hard_negative_fraction,
        hard_negative_weight=args.hard_negative_weight,
        beta=1.25,
    )
    args.output_root.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = [
        _publish_general(args.general_dir, args.output_root / "general"),
    ]
    LOG.info(
        "training %d specialists (parallelism=%d)",
        len(targets), args.parallelism,
    )
    filegroup_score_filter = args.filegroup_score_filter and not args.no_filegroup_score_filter

    # Build per-target placeholder slots so we can keep summary order stable
    # regardless of completion order from the pool.
    pending: list[dict[str, Any]] = []
    slot_index: dict[str, int] = {}
    for target in targets:
        kind_dir = "filegroups" if target["kind"] == "filegroup" else "filetypes"
        output_dir = args.output_root / kind_dir / str(target["name"])
        # Reserve a slot in `results` (one per target, after the general entry).
        slot_index[str(target["name"])] = len(results)
        if args.skip_existing and (output_dir / "benchmark.json").exists():
            LOG.info("%s: using existing benchmark", target["name"])
            with open(output_dir / "benchmark.json") as f:
                results.append(json.load(f))
            continue
        results.append(None)  # placeholder; filled in below
        pending.append(
            {
                "target": target,
                "db_path": args.db,
                "output_dir": output_dir,
                "general_spec_path": general_spec_path,
                "mask_spec_path": mask_specs.get(str(target["name"])),
                "feature_env": feature_envs.get(str(target["name"]), {}),
                "route_config": _route_train_config(config, target, train_overrides),
                "workers": args.workers,
                "max_id": args.max_id,
                "filegroup_score_filter": filegroup_score_filter,
                "n_seed_extras": args.n_seed_extras,
            },
        )

    if args.parallelism > 1 and len(pending) > 1:
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.parallelism,
            initializer=_pool_init,
            initargs=(args.log_level,),
        ) as pool:
            futures = {
                pool.submit(_train_target_worker, job): job["target"]
                for job in pending
            }
            for fut in concurrent.futures.as_completed(futures):
                target = futures[fut]
                try:
                    payload = fut.result()
                except Exception:
                    LOG.exception("%s: worker raised", target["name"])
                    payload = {"name": target["name"], "kind": target["kind"], "error": True}
                results[slot_index[str(target["name"])]] = payload
    else:
        for job in pending:
            results[slot_index[str(job["target"]["name"])]] = _train_target_worker(job)
    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "db": str(args.db),
        "max_id": args.max_id,
        "output_root": str(args.output_root),
        "min_bad": args.min_bad,
        "min_good": args.min_good,
        "results": results,
    }
    if args.only and args.summary.exists():
        with open(args.summary) as f:
            existing = json.load(f)
        merged: dict[tuple[str, str], dict[str, Any]] = {}
        order: list[tuple[str, str]] = []
        for item in existing.get("results", []):
            key = (str(item.get("kind")), str(item.get("name")))
            if key not in merged:
                order.append(key)
            merged[key] = item
        for item in results:
            key = (str(item.get("kind")), str(item.get("name")))
            if key not in merged:
                order.append(key)
            merged[key] = item
        payload["results"] = [merged[key] for key in order]
        payload["partial_update"] = {
            "only": list(args.only),
            "previous_max_id": existing.get("max_id"),
        }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    with open(args.summary, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"wrote {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
