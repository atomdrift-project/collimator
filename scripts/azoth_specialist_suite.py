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
import sys
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

from collimator import bundle, data, export, features, model, thresholds, train

LOG = logging.getLogger("azoth_specialist_suite")


def _feature_cache_helpers() -> tuple[Any, Any, Any, Any]:
    """Lazy-import the cache helpers from ``azoth_calibrate_ensemble``.

    The top-level import would create a cycle:
    ``azoth_calibrate_ensemble`` already imports ``DEPLOYMENT_GROUPS``
    from this module, so importing back would fail mid-load. Deferring
    the import to call time avoids the cycle without duplicating the
    cache format across two files.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from azoth_calibrate_ensemble import (  # noqa: PLC0415
        _file_sha256,
        _hash_ints,
        _load_route_feature_cache,
        _save_route_feature_cache,
    )
    return _file_sha256, _hash_ints, _load_route_feature_cache, _save_route_feature_cache

# Archive-shaped filetypes whose contents litmus extracts AND for which
# cleave emits no container-level kv_tree subtree. Specialists on these
# learn nothing the general/inner-file pipeline can't already see: litmus
# decomposes the container and re-grades each member at depth>0, and
# there is no archive-level metadata (manifest, signatures, headers) in
# cleave_result for a specialist to exploit.
#
# Sources of truth:
#  * cleave's is_archive() at composite_rules/types.rs:417
#  * the extractor match at analyzers/archive/mod.rs:967-1043 (covers
#    single-file decompression and cab on top of is_archive)
#  * the kv-subtree emitters audited against analyzers/archive/{mod.rs,
#    analyzers.rs} and analyzers/{jar_kv,rpm_kv,chm/chm_kv}.rs
#
# DELIBERATELY KEPT as eligible specialists (extracted by litmus *but*
# cleave emits container kv data):
#   - jar / war / ear → jar_kv (jar_kv.rs:275): manifest, signing, POM
#   - rpm → rpm_kv (archive/mod.rs:747): headers, signatures, build meta
#   - chm → chm_kv (archive/mod.rs:753): ITSF + system metadata
#
# DELIBERATELY KEPT (no full extraction):
#   - msi: ole-container; metadata emitted as findings, not kv_tree, but
#     the binary itself is graded in place. Specialist remains useful.
#
# If any addition to cleave's extractor list also adds a kv subtree,
# remove that filetype from this set; if it adds extraction without kv,
# add it here.
# Residual buckets cleave emits when the file's format couldn't be
# identified (`unknown`) or could only be characterized as a generic
# binary blob (`data`). These are catch-all labels with no shared
# underlying structure — a "specialist" trained on them learns whatever
# weak path/size/fragmentary-feature correlation exists in the
# unidentifiable subset, which doesn't generalize. The general model
# handles these rows on its own.
RESIDUAL_FILETYPES: frozenset[str] = frozenset({"unknown", "data"})


# Minimum holdout sizes for an apples-to-apples claim to count as
# trustworthy in the fallback picker. The deployed_on_same_data field
# records counts from the *candidate's* holdout — both candidate and
# deployed score the same rows. But if those rows can't distinguish
# models in the first place (e.g., 93-benign holdouts make 3 FP/M
# unmeasurable since min-observable FP/M = 1e6/93 ≈ 10752), then even
# a paired comparison can't extract signal. Below these floors the
# run is treated as legacy and ineligible; the route falls through to
# suite defaults rather than locking in a noisy "win." This is what
# would have prevented the 2026-05-22 pdf regression: an old screen
# run with r3=1.0 on a tiny holdout was picked over recent runs with
# stronger configs because no apples-to-apples baseline disqualified
# it.
APPLES_MIN_MALWARE_HOLDOUT: int = 500
APPLES_MIN_BENIGN_HOLDOUT: int = 200


def _op_recall(metrics: dict[str, Any] | None) -> float | None:
    """Operating-point recall for the picker.

    Prefers the canonical per-100M field at the deploy-default level
    (derived from ``DEFAULT_SEVERITY_LEVEL`` via
    ``default_recall_per_100M_field()``); falls back to the legacy
    per-million field ``recall_at_fp_per_million_3`` (L3, 3 FP/M) so
    old run JSONs still rank. Returns None when neither is present or
    both are NaN.
    """
    if not metrics:
        return None
    for key in (thresholds.default_recall_per_100M_field(), "recall_at_fp_per_million_3"):
        v = metrics.get(key)
        if isinstance(v, (int, float)) and not math.isnan(float(v)):
            return float(v)
    return None


# Raw single-file compression formats — these have no multi-file
# container structure for a specialist to learn from. Litmus decompresses
# them and re-routes the single inner file; the wrapper itself has no
# signal of its own. Skip specialist training entirely.
#
# Archive/container formats (tar, tar.gz, zip, 7z, deb, apk, etc.) are
# DIFFERENT: even though litmus extracts their contents and re-routes
# the inner files, the container structure (file count, layout,
# member-name patterns, oversized headers, etc.) carries malware
# signal that a specialist can learn. Those are NOT in this set and
# DO get trained.
RAW_COMPRESSED_FILETYPES: frozenset[str] = frozenset({
    "bz2",
    "gz",
    "lzma",
    "xz",
    "zst",
})

# Backwards-compatible alias. Older code (and possibly downstream
# scripts) still imports LITMUS_EXTRACTED_FILETYPES; keep it as the
# raw-compressed set so existing skip semantics for those formats
# stay intact. Archive formats that USED to be in this set (tar,
# tar.gz, zip, 7z, deb, ...) now train specialists.
LITMUS_EXTRACTED_FILETYPES: frozenset[str] = RAW_COMPRESSED_FILETYPES


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
        "java_class",
        "pyc",
        "wasm",
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


def _strip_nan(value: Any) -> Any:
    """Replace non-finite floats (NaN, ±inf) with None recursively.

    JSON written via ``json.dump(..., allow_nan=True)`` emits the literal
    token ``NaN`` (Python convention) which is not valid JSON and breaks
    strict parsers — including Go's ``encoding/json`` used by autocollie's
    ``loadDeployedRouteMetrics``. Pre-sanitizing the payload here lets
    us write with ``allow_nan=False`` and produces standards-compliant
    JSON that every consumer can parse.
    """
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {k: _strip_nan(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_strip_nan(v) for v in value]
    return value


def _label_int(label: str) -> int:
    return 1 if label == "bad" else 0


def _placeholder(db_path: Path | str) -> str:
    return "%s" if data._is_pg(db_path) else "?"  # noqa: SLF001


def _read_oof_exclude() -> int | None:
    """Honor EXP_OOF_FOLD_EXCLUDE the same way experiment.py does.

    Matches the contract at src/collimator/experiment.py:417-429 so a single
    env var drives both general and specialist OOF training: setting it to 0
    or 1 excludes that fold from training, leaving its rows held out for
    out-of-fold scoring downstream. Anything else is ignored with a warning.
    """
    raw = os.getenv("EXP_OOF_FOLD_EXCLUDE", "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        LOG.warning("ignoring invalid EXP_OOF_FOLD_EXCLUDE=%r (need 0 or 1)", raw)
        return None
    if value not in (0, 1):
        LOG.warning("ignoring EXP_OOF_FOLD_EXCLUDE=%d (need 0 or 1)", value)
        return None
    return value


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

    # EXP_OOF_FOLD_EXCLUDE turns a normal specialist training run into one
    # half of a k=2 OOF pair. Skipping rows whose canonical hash hashes to
    # the excluded fold leaves those rows available for honest OOF scoring
    # afterwards. Test partition rows have oof_fold_of() == None and are
    # untouched by this filter (they're already excluded from training via
    # _ids_labels(test=False)).
    oof_exclude = _read_oof_exclude()
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
                    if oof_exclude is not None and data.oof_fold_of(split_key) == oof_exclude:
                        continue
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
                if oof_exclude is not None and data.oof_fold_of(split_key) == oof_exclude:
                    continue
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
    # Group raw rows by normalized file_type so compressed archive variants
    # (tar.gz, tar.bz2, tar.xz, …) merge onto their container (tar) before
    # we apply the bad/good thresholds. This matches the score-table's
    # normalized labels (see data.normalize_archive_filetype) and gives
    # one specialist per container — a tar.gz file at scan time hits the
    # same model the tar.zst file does, since both share the tar route.
    grouped: dict[str, dict[str, Any]] = {}
    with data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        rows = data._execute(conn, query, params)  # noqa: SLF001
        for file_type, bad, good, total in rows:
            normalized = data.normalize_archive_filetype(file_type)
            if not normalized:
                continue
            entry = grouped.setdefault(
                normalized,
                {"variants": set(), "bad": 0, "good": 0, "total": 0},
            )
            entry["variants"].add(str(file_type))
            entry["bad"] += int(bad)
            entry["good"] += int(good)
            entry["total"] += int(total)
    out: list[dict[str, Any]] = []
    for normalized, agg in sorted(grouped.items(), key=lambda kv: -kv[1]["total"]):
        if normalized in RAW_COMPRESSED_FILETYPES:
            # Raw single-file compression: litmus decompresses and
            # re-routes the inner file. The wrapper itself has no
            # multi-file container structure for a specialist to
            # learn from.
            LOG.info(
                "%s: skipping filetype specialist (raw-compressed; %d bad, %d good)",
                normalized, agg["bad"], agg["good"],
            )
            continue
        if normalized in RESIDUAL_FILETYPES:
            # Residual bucket — cleave couldn't identify the format.
            LOG.info(
                "%s: skipping filetype specialist (residual bucket; %d bad, %d good)",
                normalized, agg["bad"], agg["good"],
            )
            continue
        if agg["bad"] < min_bad or agg["good"] < min_good:
            # Subthreshold after merge — defensive: the SQL HAVING already
            # filtered per-raw-variant, but a normalized group could still
            # land here if a rare variant slipped through with a less-strict
            # threshold elsewhere in the query.
            continue
        variants = sorted(agg["variants"])
        if variants != [normalized]:
            LOG.info(
                "%s: merged %d raw variants %s (%d bad, %d good)",
                normalized, len(variants), variants, agg["bad"], agg["good"],
            )
        out.append(
            {
                "name": normalized,
                # Keep all raw variants in `file_types` so the data query
                # (`_fetch_rows(file_types=route["file_types"], ...)`) still
                # sees every compressed sibling — `samples.file_type` is the
                # un-normalized raw value, normalization happens on read.
                "file_types": variants,
                "bad": agg["bad"],
                "good": agg["good"],
                "total": agg["total"],
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
    out = {
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
    # Operating-point recall at every FP/100M level in the canonical grid.
    # Two consumers read these:
    #   1. autocollie's promote gate (operational comparison against the
    #      baseline at DEFAULT_SEVERITY_LEVEL) — without recall_at_<default>,
    #      the gate falls back to the PR-AUC-only legacy path.
    #   2. write_azoth_readmes.py per-filetype recall-curve SVGs — they
    #      iterate the same canonical grid and draw NaN-broken lines where
    #      a level wasn't recorded.
    # Iterating thresholds._LEVELS_PER_100M means grid extensions (e.g.
    # adding L2000–L10000 to the loose tail) automatically pick up here.
    for fp100m in thresholds._LEVELS_PER_100M:
        op = _operating_point(y_true, y_prob, float(fp100m) / 100.0)
        rec = op.get("recall")
        thr = op.get("threshold")
        out[f"recall_at_{fp100m}_per_100M"] = (
            float(rec) if isinstance(rec, (int, float)) else math.nan
        )
        out[f"threshold_at_{fp100m}_per_100M"] = (
            float(thr) if isinstance(thr, (int, float)) else math.nan
        )
    return out


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
            "target_per_100M": float(target_per_million) * 100.0,
            "budget": budget,
            "threshold": float(threshold),
            "recall": float(tp / n_malware) if n_malware else math.nan,
            "precision": float(tp / max(tp + fp, 1)),
            "fp": fp,
            "tp": tp,
            "fn": n_malware - tp,
            "tn": n_benign - fp,
            "fp_per_100M": float(fp * 100_000_000.0 / n_benign) if n_benign else math.nan,
        }
        idx = end + 1
    if best is not None:
        return best
    return {
        "target_per_100M": float(target_per_million) * 100.0,
        "budget": budget,
        "threshold": None,
        "recall": None,
        "precision": None,
        "fp": None,
        "tp": None,
        "fn": None,
        "tn": None,
        "fp_per_100M": None,
    }


def _level_table(y_true: np.ndarray, y_prob: np.ndarray) -> list[dict[str, Any]]:
    return [
        {
            "level": level,
            "hostile": _operating_point(y_true, y_prob, float(level)),
        }
        for level in range(len(thresholds.SEVERITY_LEVEL_TARGETS))
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


def _load_promoted_baseline_run(
    baselines_path: Path, runs_dir: Path, route: str,
) -> dict[str, Any] | None:
    """Return the run JSON for a route's promoted baseline, or None.

    Mirrors azoth_train_best._load_promoted_baseline. promoted baselines
    have passed the full screen → confirm → promote chain (including the
    regression check against the deployed bundle), so they're the only
    operationally-verified historical source. Prefer them over raw
    screen runs whenever an entry exists.
    """
    if not baselines_path.is_file():
        return None
    try:
        with open(baselines_path) as f:
            baselines = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    entry = (baselines.get("routes") or {}).get(route)
    if not isinstance(entry, dict):
        return None
    # Retired entries: mirror of azoth_train_best._load_promoted_baseline.
    # `retired_at` marks an entry as demoted but kept in-file for audit.
    # The picker treats it as if it didn't exist, so the route falls
    # through to the apples-to-apples screen scan or to defaults.
    if entry.get("retired_at"):
        LOG.info(
            "promoted baseline for %s is retired (at=%s, reason=%s); "
            "falling through to fallback picker",
            route, entry.get("retired_at"), entry.get("retired_reason") or "unspecified",
        )
        return None
    for key_field in ("full_train_key", "promote_key"):
        key = entry.get(key_field)
        if not isinstance(key, str) or not key:
            continue
        run_path = runs_dir / f"{key}.json"
        if not run_path.is_file():
            continue
        try:
            with open(run_path) as f:
                run = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if run.get("route") == route:
            return run
    return None


def _load_autocollie_best_per_route(
    runs_dir: Path,
    targets: list[dict[str, Any]],
    baselines_path: Path | None = None,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, str]]]:
    """Scan ``runs_dir/*.json`` for each target's best historical run by
    operational metric and return its train_config + feature_env as
    per-route override dicts.

    This is how autocollie's discovered wins flow into ``make
    azoth-specialist-suite`` retrains: instead of every retrain reverting to
    the Makefile's hardcoded defaults (which predate autocollie), the suite
    picks each route's best-known config from autocollie's history and
    replays it.

    Selection key (priority order):
      1. ``has_apples_to_apples`` — a run with ``deployed_on_same_data``
         (autocollie's post-screen apples-to-apples baseline) always
         outranks a legacy run without one. Legacy runs' r@L50 is on
         a small training holdout the deployed model never sees, so
         even a big "win" there can flip on the test slice.
      2. ``delta_recall_at_L50`` — when apples-to-apples is present:
         candidate's holdout r@L50 minus the deployed model's
         r@L50 on those same rows. The cleanest "this config beats
         deployed on identical data" signal.
      3. ``recall_at_50_per_100M`` — recall at the L50 hostile
         deploy budget (0.5 FP/M). Tiebreaker within apples-to-apples;
         primary key for legacy runs. Falls back to the legacy
         ``recall_at_fp_per_million_3`` field for older run JSONs.
      4. ``avg_precision`` — curve-summarized PR/recall tradeoff.
      5. ``save_all_seeds`` — prefer multi-seed bundles when otherwise tied.
      6. ``timestamp`` — most recent tied run.

    Selecting on ``avg_precision`` alone misses swaps where two
    candidates have ~identical PR AUC but several-fold different
    recall at the deploy budget. Selecting on raw recall@L50 (the
    prior rule) misses the holdout-vs-test-slice gap — the picker
    used to grab ``filegroups/native`` configs with 88.89% holdout
    recall that scored 56% on the test PE slice. Apples-to-apples
    delta closes that gap by comparing the candidate and the
    deployed model on identical rows.

    Routes with no historical runs in ``runs_dir`` get empty overrides
    and fall through to the suite's CLI defaults. Runs missing both
    ``recall_at_50_per_100M`` and ``recall_at_fp_per_million_3`` get
    sorted with a fallback recall of 0.0 — penalized vs runs that
    recorded the operational metric, but not excluded.

    Returns ``(train_overrides_by_route, feature_envs_by_route)``. Both
    maps are keyed by the canonical route name (e.g. ``filetypes/perl``).
    """
    if not runs_dir.is_dir():
        LOG.info("autocollie-best: %s is not a directory; skipping", runs_dir)
        return {}, {}

    targeted_routes = {_route_key_for_target(t) for t in targets}

    # First pass: pull any route that has a promoted baseline. Those are
    # the operationally-verified historical configs; we always prefer
    # them over raw screen runs when present.
    promoted_runs: dict[str, dict[str, Any]] = {}
    if baselines_path is not None and baselines_path.is_file():
        for route in targeted_routes:
            run = _load_promoted_baseline_run(baselines_path, runs_dir, route)
            if run is not None:
                promoted_runs[route] = run

    # Track best per route as
    # (has_apples, delta_r_op, r_op, avg_precision, save_all_seeds, timestamp, run_dict).
    # r_op is recall at the operating point (L50 preferred, L3 fallback).
    # Skip routes that already have a promoted baseline — those win.
    best: dict[str, tuple[bool, float, float, float, bool, str, dict[str, Any]]] = {}
    apples_counts: dict[str, list[int]] = {}  # route -> [apples, legacy]
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
        if route in promoted_runs:
            continue  # promoted baseline wins; don't bother evaluating screens
        metrics = run.get("sampled_test_metrics") or {}
        ap = metrics.get("avg_precision")
        if not isinstance(ap, (int, float)):
            continue
        op_val = _op_recall(metrics)
        r_op = op_val if op_val is not None else 0.0
        # Apples-to-apples gate: a run is only eligible to win the
        # fallback picker if it carries deployed_on_same_data on a
        # statistically meaningful holdout. Without it, screen-time
        # r_op is dominated by threshold noise on tiny slices —
        # picking by raw r_op across legacy runs is how a lucky-perfect
        # r_op=1.0 on a small holdout beat strong recent configs.
        # See APPLES_MIN_*_HOLDOUT for the floor rationale.
        deployed = run.get("deployed_on_same_data") or {}
        deployed_op = _op_recall(deployed)
        n_mal = deployed.get("n_malware", 0) or 0
        n_ben = deployed.get("n_benign", 0) or 0
        has_apples = (
            deployed_op is not None
            and n_mal >= APPLES_MIN_MALWARE_HOLDOUT
            and n_ben >= APPLES_MIN_BENIGN_HOLDOUT
        )
        counts = apples_counts.setdefault(route, [0, 0])
        if not has_apples:
            counts[1] += 1
            continue
        counts[0] += 1
        delta_r_op = r_op - float(deployed_op)
        save_all = bool(run.get("save_all_seeds"))
        timestamp = str(run.get("timestamp") or "")
        candidate = (has_apples, delta_r_op, r_op, float(ap), save_all, timestamp, run)
        prev = best.get(route)
        if prev is None or candidate[:6] > prev[:6]:
            best[route] = candidate
    for route, (n_apples, n_legacy) in apples_counts.items():
        if route in best:
            winner = best[route]
            LOG.info(
                "autocollie-best (fallback) %s: scanned %d apples-to-apples + "
                "%d legacy (skipped) runs; winner delta_r_op=%+.4f r_op=%.4f (L50)",
                route, n_apples, n_legacy,
                winner[1], winner[2],
            )
        elif n_legacy > 0:
            LOG.warning(
                "autocollie-best %s: scanned %d screen run(s), none with "
                "apples-to-apples on holdout >= %d malware / %d benign; "
                "route falls through to suite defaults. Run an autocollie "
                "cycle on this route to generate a trustworthy baseline.",
                route, n_legacy,
                APPLES_MIN_MALWARE_HOLDOUT, APPLES_MIN_BENIGN_HOLDOUT,
            )

    valid_train_fields = _train_config_field_names()
    train_overrides: dict[str, dict[str, Any]] = {}
    feature_envs: dict[str, dict[str, str]] = {}

    def _record(route: str, run: dict[str, Any], source: str) -> None:
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
        env_overrides = {str(k): str(v) for k, v in env.items() if str(k).startswith("COLLIMATOR_")}
        if env_overrides:
            feature_envs[route] = env_overrides

        metrics = run.get("sampled_test_metrics") or {}
        r_op = _op_recall(metrics)
        ap = metrics.get("avg_precision")
        LOG.info(
            "autocollie-best: %s -> key=%s source=%s recall@L50=%s avg_precision=%s save_all=%s overrides=%d env=%d",
            route, run.get("experiment_key", "?"), source,
            "%.4f" % r_op if r_op is not None else "?",
            "%.4f" % ap if isinstance(ap, (int, float)) else "?",
            bool(run.get("save_all_seeds")),
            len(cfg_overrides), len(env_overrides),
        )

    # Promoted baselines win when present — they've been operationally
    # validated by the screen → confirm → promote chain.
    for route, run in promoted_runs.items():
        _record(route, run, source="promoted_baseline")
    # Fallback: best raw screen run by operational metric. Logs the
    # source explicitly so the human sees which routes need a promote
    # cycle to graduate off the brittle path.
    for route, (has_apples, _delta, _r_op, _ap, _save_all, _ts, run) in best.items():
        if route in promoted_runs:
            continue
        source = "screen_runs_apples_to_apples" if has_apples else "screen_runs_legacy"
        _record(route, run, source=source)

    if best and not promoted_runs:
        LOG.warning(
            "no promoted_baselines.json entries for any of %d target routes; "
            "all overrides come from raw screen runs and may not generalize to "
            "the deployed slice. Run autocollie promote cycles on the affected "
            "routes to graduate them to the operationally-verified path.",
            len(best),
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
    skip_benchmark: bool = False,
    feature_cache_dir: Path | None = None,
) -> dict[str, Any]:
    train_rows = _fetch_rows(
        db_path,
        file_types=file_types,
        max_id=max_id,
        min_score=data.MIN_SAMPLE_SCORE if kind == "filegroup" and filegroup_score_filter else None,
    )
    train_ids_labels = _ids_labels(train_rows, test=False)
    if not train_ids_labels:
        raise ValueError(f"{name}: no train rows")
    if skip_benchmark:
        # OOF fold runs deploy nothing — only the OOF prediction npz is
        # consumed downstream. The per-specialist benchmark exists purely
        # for diagnostic metrics in benchmark.json / specialists.json, so
        # skipping it shaves the test-partition extraction + scoring pass
        # without affecting OOF correctness. write_azoth_readmes.py (the
        # one downstream consumer that requires non-empty benchmark.json)
        # only runs against the production bundle, not the fold bundles.
        benchmark_rows = []
        benchmark_ids_labels = []
    else:
        benchmark_rows = _fetch_rows(db_path, file_types=file_types, max_id=max_id, min_score=None)
        benchmark_ids_labels = _ids_labels(benchmark_rows, test=True)
        if not benchmark_ids_labels:
            raise ValueError(f"{name}: no benchmark rows")

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
            # Persist the spec immediately. Downstream feature-cache lookup
            # hashes spec_path (line ~855), which fails with FileNotFoundError
            # when the spec exists only in memory. Native filegroup hit this
            # and skipped training entirely — produced an empty
            # filegroups/native bundle dir and broke deploy verification.
            output_dir.mkdir(parents=True, exist_ok=True)
            spec.save(spec_path)
        LOG.info(
            "%s: extracting train and benchmark features with %s spec (%d features)",
            name,
            feature_spec_policy,
            spec.total_features,
        )
        # Feature-cache lookup for the training matrix. Cache key matches
        # what azoth_calibrate_ensemble._score_route uses so a matrix
        # produced by either side is interchangeable. The cache covers
        # only the TRAINING half — benchmark features are typically empty
        # (skip_benchmark=True is the OOF default) or small relative to
        # train, and live on a separate extract path either way.
        #
        # Cross-fold sharing: when azoth_prefill_specialist_features.py
        # has pre-populated the cache with fold-A and fold-B matrices
        # (each computed from a single shared union extraction), this
        # lookup hits and skips the per-fold ``extract_partitioned_from_db``
        # entirely. On a cache miss we fall back to today's extract path,
        # then save the result so a retry or a parallel fold benefits.
        cached_train_matrix = None
        feature_cache_read_s = 0.0
        cache_key: dict[str, Any] | None = None
        if feature_cache_dir is not None:
            _file_sha256, _hash_ints, _load_cache, _save_cache = _feature_cache_helpers()
            cache_route_name = (
                f"filegroups/{name}" if kind == "filegroup" else f"filetypes/{name}"
            )
            spec_hash = _file_sha256(output_dir / "feature_spec.json") \
                if (output_dir / "feature_spec.json").exists() \
                else _file_sha256(spec_path)
            train_row_ids = np.asarray(
                [rid for rid, _label in train_ids_labels], dtype=np.int64,
            )
            rows_hash = _hash_ints(train_row_ids)
            cache_key = {
                "route_name": cache_route_name,
                "max_id": max_id,
                "spec_hash": spec_hash,
                "rows_hash": rows_hash,
            }
            cached_train_matrix, feature_cache_read_s = _load_cache(
                feature_cache_dir,
                expected_rows=len(train_ids_labels),
                expected_features=spec.total_features,
                **cache_key,
            )
        if cached_train_matrix is not None:
            LOG.info(
                "%s: cache hit (%.1fs); skipping train extraction",
                name, feature_cache_read_s,
            )
            x_train = cached_train_matrix
            # Labels are recoverable from train_ids_labels directly — the
            # extract function sorts by row_id, so reconstruct the same
            # ordering here. (_load_route_feature_cache verified row
            # count + feature count above; the per-row label is in the
            # input list, no second DB hit needed.)
            sorted_train = sorted(train_ids_labels, key=lambda r: r[0])
            y_train = np.asarray(
                [label for _row_id, label in sorted_train], dtype=np.float32,
            )
            # Benchmark still needs extraction (or stays empty under
            # skip_benchmark). Keep the existing call shape but with an
            # empty train side — extract_partitioned_from_db handles the
            # empty-train case correctly.
            if benchmark_ids_labels:
                _x_train_empty, _y_train_empty, x_bench, y_bench = features.extract_partitioned_from_db(
                    db_path,
                    [],
                    benchmark_ids_labels,
                    spec,
                    n_workers=workers,
                )
            else:
                x_bench = sp.csr_matrix((0, spec.total_features), dtype=np.float32)
                y_bench = np.array([], dtype=np.float32)
        else:
            x_train, y_train, x_bench, y_bench = features.extract_partitioned_from_db(
                db_path,
                train_ids_labels,
                benchmark_ids_labels,
                spec,
                n_workers=workers,
            )
            if feature_cache_dir is not None and cache_key is not None and x_train.shape[0] > 0:
                _, _, _, _save_cache = _feature_cache_helpers()
                _save_cache(feature_cache_dir, matrix=x_train, **cache_key)
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

    # Refuse to emit a route for a constant predictor. When the optimizer
    # finds no split worth making (tiny single-class slices), the model
    # always emits the same score regardless of input — it carries no
    # signal. Rather than ship a useless route, omit it: litmus routes
    # those files to the filegroup/general ensemble instead (the loader
    # treats absent specialists as droppable). Marked with `error` so the
    # existing summary-skip path (azoth_calibrate_ensemble._load_routes)
    # drops it from the deployed route list.
    if export.is_constant_predictor(result.model):
        LOG.info(
            "%s: constant predictor (no split learned) — refusing to emit a route; "
            "litmus will route these files to the filegroup/general ensemble",
            name,
        )
        return {
            "name": name,
            "kind": kind,
            "file_types": list(file_types),
            "error": True,
            "skip_reason": "constant_predictor",
        }

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
            # Write .txt then .onnx, each via a `.tmp` sibling renamed into
            # place (model_files() ignores `.tmp`, so an interrupted run never
            # exposes a half-written seed). The .onnx is emitted EXPLICITLY:
            # the `.tmp` suffix would otherwise suppress save_model's automatic
            # sibling export, and the deployed bundle is ONNX-only — every seed
            # needs an .onnx or the route strands on the retired LightGBM loader.
            final_txt = bundle.write_seed_model_path(output_dir, seed, "txt")
            tmp_txt = final_txt.with_name(f".{final_txt.name}.tmp")
            export.save_model(model_obj, tmp_txt)
            os.replace(tmp_txt, final_txt)
            booster = getattr(model_obj, "booster_", model_obj)
            final_onnx = final_txt.with_suffix(".onnx")
            tmp_onnx = final_onnx.with_name(f".{final_onnx.name}.tmp")
            if export.export_lightgbm_onnx(booster, booster.num_feature(), tmp_onnx):
                os.replace(tmp_onnx, final_onnx)
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
    # so reported metrics match what litmus emits. Skipped entirely when
    # --skip-benchmark is set: x_bench is an empty matrix and predict_proba
    # would return an empty array, so we shortcut and leave probs empty.
    if skip_benchmark:
        probs = np.array([], dtype=np.float32)
    elif extra_models:
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
        # When skip_benchmark is set, y_bench/probs are empty and the metric
        # helpers can't compute anything meaningful. Emit a sentinel marker
        # so downstream tools (notably write_azoth_readmes) can either
        # gracefully degrade or refuse to consume a fold bundle.
        "metrics": (
            {"skipped": "benchmark"}
            if skip_benchmark
            else _classification_metrics(y_bench, probs)
        ),
        "levels": [] if skip_benchmark else _level_table(y_bench, probs),
        "train_config": asdict(config),
        "train_score_filter": (
            {"min_score": data.MIN_SAMPLE_SCORE, "scope": "all labels"}
            if kind == "filegroup" and filegroup_score_filter
            else {"min_score": None, "scope": "full labeled filetype corpus"}
        ),
    }
    with open(output_dir / "benchmark.json", "w") as f:
        json.dump(_strip_nan(payload), f, indent=2, allow_nan=False)
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
            skip_benchmark=job.get("skip_benchmark", False),
            feature_cache_dir=job.get("feature_cache_dir"),
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
            "route's best historical run and applies its train_config + "
            "feature_env as automatic per-route overrides. Without this flag, "
            "every retrain reverts to Makefile defaults — autocollie's wins are "
            "lost. Explicit --train-override / --feature-env still take "
            "precedence over auto-discovered values. The picker prefers entries "
            "from --promoted-baselines (operationally-validated) over raw "
            "screen runs when both exist for a route."
        ),
    )
    parser.add_argument(
        "--promoted-baselines",
        type=Path,
        default=None,
        help=(
            "Path to autocollie's promoted_baselines.json. When set together "
            "with --autocollie-best-runs-dir, routes with a promoted entry "
            "pull their config from the verified promote-chain rather than "
            "raw screen runs. Strongly recommended: skipping it makes the "
            "picker brittle for routes where bad screen-only candidates exist."
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
    parser.add_argument(
        "--feature-cache-dir",
        type=Path,
        default=None,
        help=(
            "Directory holding per-route training feature matrices. When "
            "set, _train_one looks up "
            "{cache_dir}/<route_slug>-{max_id}-{spec_hash[:16]}-{rows_hash[:16]}.matrix.npz "
            "before extracting; cache misses save the freshly-extracted "
            "matrix for later runs. Pre-fill via "
            "scripts/azoth_prefill_specialist_features.py to share work "
            "across fold-A / fold-B / retried runs. Format matches "
            "azoth_calibrate_ensemble._score_route's cache so matrices "
            "are interchangeable between training and calibration scoring."
        ),
    )
    parser.add_argument(
        "--skip-benchmark",
        action="store_true",
        help=(
            "Skip the test-partition extract + score that populates "
            "benchmark.json's metrics for each specialist. Used by the "
            "OOF fold targets where the bundles are never deployed and "
            "the only consumer (write_azoth_readmes) doesn't see them. "
            "Output benchmark.json still gets written with a "
            "``metrics: {skipped: \"benchmark\"}`` sentinel so the "
            "specialists.json summary stays well-formed and so "
            "--skip-existing can detect that the route was already "
            "trained without rerunning."
        ),
    )
    parser.add_argument(
        "--lgbm-threads",
        type=int,
        default=None,
        help=(
            "Hard cap on LightGBM threads per training. Without this, "
            "LightGBM grabs every CPU core (n_jobs=-1), so multiple "
            "concurrent specialist trainings (--parallelism > 1) all try "
            "to claim the full host and thrash on context switches. "
            "Default (None): auto-set to max(1, nproc // parallelism) when "
            "--parallelism > 1, otherwise leave LightGBM uncapped."
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
        # Fall back to the conventional path if --promoted-baselines wasn't
        # given but the file exists under the output root. Operators who
        # never pass this flag still get the verified-baseline preference.
        baselines_path = args.promoted_baselines
        if baselines_path is None:
            default_baselines = args.output_root / ".autocollie" / "promoted_baselines.json"
            if default_baselines.is_file():
                baselines_path = default_baselines
        auto_train, auto_env = _load_autocollie_best_per_route(
            args.autocollie_best_runs_dir, targets,
            baselines_path=baselines_path,
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

    # Small-route defaults for COLLIMATOR_MIN_SAMPLE_SCORE.
    #
    # The global default is 3 (data.py:_default_min) — keeps the training
    # pool to rows whose hopper-rule score crossed a meaningful threshold.
    # For abundant routes (PE, ELF, PDF) this is the right filter — there
    # are millions of score≥3 rows, no need to dilute training with
    # low-signal samples.
    #
    # For tiny routes (groovy, makefile, lnk, etc. — where total labeled
    # samples may be in the hundreds), score≥3 strips most of the pool,
    # often leaving a degenerate one-class training set. We saw exactly
    # this in autocollie cycles on pdf: specs proposing min_sample_score=3
    # produced n_ben_holdout=95 → constant-predictor at confirm.
    #
    # When neither an autocollie-best entry nor a CLI override has set
    # COLLIMATOR_MIN_SAMPLE_SCORE for a small route, default it to a
    # value that preserves benign-pool diversity. "Explicit wins": if
    # the operator or a promoted-baseline already chose a value, keep
    # it — the route's verified history said so.
    #
    # Tradeoff: min_sample_score=0 includes rows where cleave found no
    # features. Those rows have near-empty feature vectors and shift
    # the model toward learning label-prior rather than feature
    # distribution. For very small routes this is still better than
    # starving the model entirely.
    small_route_default_applied: list[str] = []
    for target in targets:
        if target.get("kind") not in ("filetype",):
            continue  # filegroups/general always have abundant pools
        route = _route_key_for_target(target)
        existing_env = feature_envs.get(route, {})
        if "COLLIMATOR_MIN_SAMPLE_SCORE" in existing_env:
            continue
        n_mal = int(target.get("bad", 0))
        n_ben = int(target.get("good", 0))
        binding = min(n_mal, n_ben)
        if binding < 2000:
            new_min = "0"
        elif binding < 10000:
            new_min = "1"
        else:
            continue
        feature_envs.setdefault(route, {})["COLLIMATOR_MIN_SAMPLE_SCORE"] = new_min
        small_route_default_applied.append(
            f"{route} (min={n_mal}/{n_ben} bad/good → min_sample_score={new_min})"
        )
    if small_route_default_applied:
        LOG.info(
            "small-route min_sample_score defaults applied to %d route(s) "
            "(no explicit override present): %s",
            len(small_route_default_applied),
            ", ".join(small_route_default_applied),
        )

    # Auto-cap LightGBM threads per training when running multiple
    # specialists concurrently. Without this, every concurrent training
    # asks for all 128 cores via n_jobs=-1 and the host context-switches
    # itself to death (we saw load avg ~240 on a 128-core box with
    # parallelism=2). nproc // parallelism keeps total worker count
    # roughly equal to the core count and yields predictable wall-clock.
    #
    # AZOTH_CONCURRENT_SUITES (set by scripts/azoth_oof_pipeline.sh when
    # PARALLEL_FOLDS=1) tells the suite that another instance is running
    # in parallel and the thread budget should be split across them.
    # Without this knowledge each suite would claim the full host and
    # 2× CPU oversubscription would erase the parallel-folds win.
    lgbm_threads = args.lgbm_threads
    if lgbm_threads is None and args.parallelism > 1:
        nproc = os.cpu_count() or 1
        concurrent_suites = max(1, int(os.environ.get("AZOTH_CONCURRENT_SUITES", "1")))
        lgbm_threads = max(1, nproc // (args.parallelism * concurrent_suites))
        suite_note = f", concurrent_suites={concurrent_suites}" if concurrent_suites > 1 else ""
        LOG.info(
            "auto-capping LightGBM threads per training at %d "
            "(%d cores / parallelism=%d%s). Override with --lgbm-threads N.",
            lgbm_threads, nproc, args.parallelism, suite_note,
        )

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
        num_threads=lgbm_threads,
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
                "skip_benchmark": args.skip_benchmark,
                "feature_cache_dir": args.feature_cache_dir,
            },
        )

    if args.parallelism > 1 and len(pending) > 1:
        # `spawn` start method — see azoth_calibrate_ensemble.py for the
        # rationale. Fork-based workers inherit the parent's OpenMP/BLAS
        # mutex state and silently futex_wait-deadlock when LightGBM warms
        # up its thread pool inside the worker.
        import multiprocessing as _mp  # noqa: PLC0415
        _spawn_ctx = _mp.get_context("spawn")
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.parallelism,
            mp_context=_spawn_ctx,
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
        json.dump(_strip_nan(payload), f, indent=2, allow_nan=False)
    print(f"wrote {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
