#!/usr/bin/env python3
"""Train and benchmark azoth filegroup/filetype specialist models."""

from __future__ import annotations

import argparse
import json
import logging
import math
import shutil
from dataclasses import asdict
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

from collimator import data, export, features, model, train

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
    config: train.TrainConfig,
    workers: int,
    max_id: int,
    filegroup_score_filter: bool,
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

    LOG.info(
        "%s: extracting train and benchmark features with general spec (%d features)",
        name,
        general_spec.total_features,
    )
    x_train, y_train, x_bench, y_bench = features.extract_partitioned_from_db(
        db_path,
        train_ids_labels,
        benchmark_ids_labels,
        general_spec,
        n_workers=workers,
    )
    allowed_mask, mask_metadata = _allowed_mask_from_spec(general_spec, mask_spec_path)
    if mask_metadata is not None:
        LOG.info(
            "%s: applying feature mask from %s (%d/%d general features, %d missing)",
            name,
            mask_spec_path,
            mask_metadata["allowed_features"],
            general_spec.total_features,
            mask_metadata["missing_features"],
        )
        x_train = _mask_sparse_columns(x_train, allowed_mask)
        x_bench = _mask_sparse_columns(x_bench, allowed_mask)
    LOG.info("%s: training", name)
    result = train.train(
        x_train,
        y_train,
        config,
        feature_names=general_spec.feature_names,
        sample_file_types=_file_types(train_rows, test=False),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(general_spec_path, output_dir / "feature_spec.json")
    export.save_model(result.model, output_dir / "model.txt")
    probs = model.predict_proba(result.model, x_bench)
    payload = {
        "name": name,
        "kind": kind,
        "file_types": list(file_types),
        "output_dir": str(output_dir),
        "model_path": str(output_dir / "model.txt"),
        "spec_path": str(output_dir / "feature_spec.json"),
        "train_rows": int(len(y_train)),
        "train_malware": int(np.sum(y_train == 1)),
        "train_benign": int(np.sum(y_train == 0)),
        "benchmark_rows": int(len(y_bench)),
        "benchmark_malware": int(np.sum(y_bench == 1)),
        "benchmark_benign": int(np.sum(y_bench == 0)),
        "n_features": int(general_spec.total_features),
        "feature_spec_policy": (
            "general_shared_masked" if mask_metadata is not None else "general_shared"
        ),
        "feature_mask": mask_metadata,
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
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--min-bad", type=int, default=50)
    parser.add_argument("--min-good", type=int, default=50)
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--mask-spec", action="append", default=[])
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--no-filegroup-score-filter", action="store_true")
    parser.add_argument("--log-level", default="INFO")
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
        beta=1.25,
    )
    args.output_root.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = [
        _publish_general(args.general_dir, args.output_root / "general"),
    ]
    targets = _targets(args)
    LOG.info("training %d specialists", len(targets))
    for target in targets:
        kind_dir = "filegroups" if target["kind"] == "filegroup" else "filetypes"
        output_dir = args.output_root / kind_dir / str(target["name"])
        if args.skip_existing and (output_dir / "benchmark.json").exists():
            LOG.info("%s: using existing benchmark", target["name"])
            with open(output_dir / "benchmark.json") as f:
                results.append(json.load(f))
            continue
        try:
            results.append(
                _train_one(
                    db_path=args.db,
                    name=str(target["name"]),
                    kind=str(target["kind"]),
                    file_types=tuple(target["file_types"]),
                    output_dir=output_dir,
                    general_spec_path=general_spec_path,
                    general_spec=general_spec,
                    mask_spec_path=mask_specs.get(str(target["name"])),
                    config=config,
                    workers=args.workers,
                    max_id=args.max_id,
                    filegroup_score_filter=not args.no_filegroup_score_filter,
                ),
            )
        except Exception:
            LOG.exception("%s: failed", target["name"])
            results.append({"name": target["name"], "kind": target["kind"], "error": True})
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
