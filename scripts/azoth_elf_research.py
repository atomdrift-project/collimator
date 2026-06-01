#!/usr/bin/env python3
"""Run unconstrained AZOTH ELF specialist research experiments."""

from __future__ import annotations

import argparse
import itertools
import json
import logging
import math
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import lightgbm as lgb
import numpy as np
import scipy.sparse as sp
import xgboost as xgb
from sklearn.metrics import average_precision_score, f1_score, precision_recall_curve, roc_auc_score
from sklearn.model_selection import train_test_split

from collimator import data, export, features, model, thresholds

sys.path.insert(0, str(Path(__file__).resolve().parent))
from azoth_calibrate_ensemble import _calibrate_one  # noqa: E402
from azoth_specialist_suite import _fetch_rows, _ids_labels  # noqa: E402

LOG = logging.getLogger("azoth_elf_research")

RuleName = Literal["or", "replacement"]


@dataclass(frozen=True)
class Candidate:
    name: str
    learner: Literal["lightgbm", "xgboost"]
    params: dict[str, Any]


FIRST_BATCH: tuple[Candidate, ...] = (
    Candidate(
        "lgbm_leaves96_mcs100",
        "lightgbm",
        {
            "boosting_type": "gbdt",
            "n_estimators": 500,
            "learning_rate": 0.05,
            "max_depth": 12,
            "num_leaves": 96,
            "min_child_samples": 100,
            "colsample_bytree": 0.8,
            "subsample": 0.8,
            "reg_alpha": 0.0,
            "reg_lambda": 1.0,
        },
    ),
    Candidate(
        "lgbm_leaves255_mcs25",
        "lightgbm",
        {
            "boosting_type": "gbdt",
            "n_estimators": 700,
            "learning_rate": 0.03,
            "max_depth": -1,
            "num_leaves": 255,
            "min_child_samples": 25,
            "colsample_bytree": 0.8,
            "subsample": 0.8,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
        },
    ),
    Candidate(
        "lgbm_leaves511_mcs50",
        "lightgbm",
        {
            "boosting_type": "gbdt",
            "n_estimators": 700,
            "learning_rate": 0.03,
            "max_depth": -1,
            "num_leaves": 511,
            "min_child_samples": 50,
            "colsample_bytree": 0.8,
            "subsample": 0.8,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
        },
    ),
    Candidate(
        "lgbm_goss_leaves255_mcs25",
        "lightgbm",
        {
            "boosting_type": "goss",
            "n_estimators": 700,
            "learning_rate": 0.03,
            "max_depth": -1,
            "num_leaves": 255,
            "min_child_samples": 25,
            "colsample_bytree": 0.8,
            "subsample": 1.0,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
        },
    ),
    Candidate(
        "lgbm_dart_leaves255_mcs25",
        "lightgbm",
        {
            "boosting_type": "dart",
            "n_estimators": 500,
            "learning_rate": 0.03,
            "max_depth": -1,
            "num_leaves": 255,
            "min_child_samples": 25,
            "colsample_bytree": 0.8,
            "subsample": 0.8,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
        },
    ),
    Candidate(
        "xgb_depth10_eta03",
        "xgboost",
        {
            "n_estimators": 700,
            "learning_rate": 0.03,
            "max_depth": 10,
            "min_child_weight": 5,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_alpha": 0.0,
            "reg_lambda": 1.0,
        },
    ),
    Candidate(
        "xgb_depth14_eta02",
        "xgboost",
        {
            "n_estimators": 900,
            "learning_rate": 0.02,
            "max_depth": 14,
            "min_child_weight": 20,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_alpha": 0.0,
            "reg_lambda": 2.0,
        },
    ),
)

EXPANDED_BATCH: tuple[Candidate, ...] = (
    Candidate(
        "expanded_xgb_depth10_eta03",
        "xgboost",
        {
            "n_estimators": 900,
            "learning_rate": 0.03,
            "max_depth": 10,
            "min_child_weight": 5,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_alpha": 0.0,
            "reg_lambda": 1.0,
        },
    ),
    Candidate(
        "expanded_lgbm_leaves96_mcs100",
        "lightgbm",
        {
            "boosting_type": "gbdt",
            "n_estimators": 700,
            "learning_rate": 0.05,
            "max_depth": 12,
            "num_leaves": 96,
            "min_child_samples": 100,
            "colsample_bytree": 0.8,
            "subsample": 0.8,
            "reg_alpha": 0.0,
            "reg_lambda": 1.0,
        },
    ),
    Candidate(
        "expanded_lgbm_goss_leaves255_mcs25",
        "lightgbm",
        {
            "boosting_type": "goss",
            "n_estimators": 700,
            "learning_rate": 0.03,
            "max_depth": -1,
            "num_leaves": 255,
            "min_child_samples": 25,
            "colsample_bytree": 0.8,
            "subsample": 1.0,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
        },
    ),
)


def _matrix(
    db_path: Path | str,
    rows: list[tuple[int, int]],
    spec: features.FeatureSpec,
    workers: int,
) -> tuple[sp.csr_matrix, np.ndarray]:
    batches = list(features.extract_labeled_from_db_batches(db_path, rows, spec, n_workers=workers))
    if not batches:
        empty_x = sp.csr_matrix((0, spec.total_features), dtype=np.float32)
        return empty_x, np.asarray([], dtype=np.float32)
    x_matrix = sp.vstack([x for x, _y in batches], format="csr")
    y_values = np.concatenate([y for _x, y in batches])
    return x_matrix, y_values.astype(np.int8, copy=False)


def _coerce_report(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        return json.loads(raw)
    return {}


def _trait_tokens(
    report: dict[str, Any],
    *,
    mode: str,
    min_crit: int,
    path_depth: int,
) -> list[str]:
    tokens: list[str] = []
    include_exact = mode in {"exact", "combo"}
    include_hierarchy = mode in {"hierarchy", "combo"}
    for file_entry in features.report_files(report):
        for finding in file_entry.get("ts") or []:
            fid = finding.get("i", "")
            if not fid:
                continue
            try:
                conf = float(finding.get("c", 1.0))
            except (TypeError, ValueError):
                conf = 1.0
            if conf < features.MIN_CONFIDENCE:
                continue
            crit = int(finding.get("l", 0) or 0)
            if min_crit > 0 and crit < min_crit:
                continue
            if include_exact:
                tokens.append(f"id:{fid}")
            if include_hierarchy:
                base = fid.split("::")[0]
                parts = [part for part in base.split("/") if part]
                max_depth = len(parts) if path_depth <= 0 else min(path_depth, len(parts))
                for depth in range(1, max_depth + 1):
                    tokens.append(f"path:{'/'.join(parts[:depth])}")
    return tokens


def _paths_for_file_entry(
    file_entry: dict[str, Any],
    *,
    min_crit: int,
    path_depth: int,
) -> list[str]:
    paths: set[str] = set()
    for finding in file_entry.get("ts") or []:
        fid = finding.get("i", "")
        if not fid:
            continue
        try:
            conf = float(finding.get("c", 1.0))
        except (TypeError, ValueError):
            conf = 1.0
        if conf < features.MIN_CONFIDENCE:
            continue
        crit = int(finding.get("l", 0) or 0)
        if min_crit > 0 and crit < min_crit:
            continue
        base = fid.split("::")[0]
        parts = [part for part in base.split("/") if part]
        if not parts:
            continue
        if path_depth > 0:
            base = "/".join(parts[:path_depth])
        paths.add(base)
    return sorted(paths)


def _ngram_tokens(
    report: dict[str, Any],
    *,
    min_crit: int,
    path_depth: int,
    order_min: int,
    order_max: int,
    max_paths: int,
    max_ngrams_per_file: int,
) -> list[str]:
    tokens: list[str] = []
    for file_entry in features.report_files(report):
        paths = _paths_for_file_entry(
            file_entry,
            min_crit=min_crit,
            path_depth=path_depth,
        )
        if len(paths) > max_paths:
            paths = paths[:max_paths]
        emitted = 0
        for order in range(order_min, order_max + 1):
            if len(paths) < order:
                continue
            for combo in itertools.combinations(paths, order):
                tokens.append(f"ng{order}:{' + '.join(combo)}")
                emitted += 1
                if emitted >= max_ngrams_per_file:
                    break
            if emitted >= max_ngrams_per_file:
                break
    return tokens


def _string_tokenize(value: str) -> list[str]:
    out: list[str] = []
    current: list[str] = []
    for char in value.lower():
        if char.isalnum() or char in {"_", "-", ".", "/", ":"}:
            current.append(char)
        else:
            if len(current) >= 3:
                out.append("".join(current[:80]))
            current = []
    if len(current) >= 3:
        out.append("".join(current[:80]))
    return out


def _symbol_tokens(report: dict[str, Any]) -> list[str]:
    tokens: list[str] = []
    saw_symbol = False
    for file_entry in features.report_files(report):
        for item in file_entry.get("ss") or []:
            value = ""
            if isinstance(item, list | tuple) and len(item) >= 2:
                value = str(item[1])
            elif isinstance(item, str):
                value = item
            if not value:
                continue
            saw_symbol = True
            for token in _string_tokenize(value):
                tokens.append(f"sym:{token}")
            if 3 <= len(value) <= 80:
                tokens.append(f"symwhole:{value.lower()}")
    if not saw_symbol:
        tokens.append("sym_missing:none")
    return tokens


def _formula_tokens(item: dict[str, Any]) -> list[str]:
    formula = str(item.get("formula") or "")
    if not formula:
        return ["formula_missing:none"]
    skeleton = "".join(char for char in formula if char.isalpha())
    tokens = [f"formula_len:{min(len(formula) // 20, 20)}"]
    for char in set(skeleton):
        tokens.append(f"formula_el:{char}")
    for n in range(2, 6):
        for idx in range(0, max(0, len(skeleton) - n + 1)):
            tokens.append(f"formula_ng{n}:{skeleton[idx:idx+n]}")
    return tokens


def _split_elements(raw: str) -> list[str]:
    normalized = raw.replace(";", ",").replace("|", ",")
    if "," in normalized:
        return [part.strip().lower() for part in normalized.split(",") if part.strip()]
    elements: list[str] = []
    current: list[str] = []
    for char in raw:
        if not char.isalpha():
            if current:
                elements.append("".join(current).lower())
                current = []
            continue
        if char.isupper() and current:
            elements.append("".join(current).lower())
            current = [char]
        else:
            current.append(char)
    if current:
        elements.append("".join(current).lower())
    return elements


def _element_tokens(item: dict[str, Any]) -> list[str]:
    raw_elements = str(item.get("elements") or "")
    formula = str(item.get("formula") or "")
    elements = _split_elements(raw_elements)
    if not elements and formula:
        skeleton = "".join(char for char in formula if char.isalpha())
        elements = _split_elements(skeleton)
    if not elements:
        return ["elements_missing:none"]

    tokens: list[str] = []
    unique_elements = sorted(set(elements))
    tokens.append(f"elements_count:{min(len(elements), 100)}")
    tokens.append(f"elements_unique:{min(len(unique_elements), 100)}")
    for element in unique_elements:
        tokens.append(f"element:{element}")
    for left, right in zip(elements, elements[1:], strict=False):
        tokens.append(f"element_pair:{left}+{right}")
    return tokens


def _metric_values(report: dict[str, Any]) -> dict[str, float]:
    values: dict[str, float] = {}
    for file_entry in features.report_files(report):
        metrics = file_entry.get("ms") or {}
        if not isinstance(metrics, dict):
            continue
        for group, group_values in metrics.items():
            if not isinstance(group_values, dict):
                continue
            for name, raw in group_values.items():
                if isinstance(raw, bool):
                    value = 1.0 if raw else 0.0
                else:
                    try:
                        value = float(raw)
                    except (TypeError, ValueError):
                        continue
                key = f"metric:{group}.{name}"
                if key not in values or abs(value) > abs(values[key]):
                    values[key] = value
    return values


DENSITY_FEATURES: tuple[str, ...] = (
    "density:file_count_log",
    "density:total_kb_log",
    "density:finding_count_log",
    "density:suspicious_count_log",
    "density:hostile_count_log",
    "density:suspicious_per_kb",
    "density:hostile_per_kb",
    "density:top_file_suspicious_per_kb",
    "density:top_file_hostile_per_kb",
    "density:suspicious_file_frac",
    "density:hostile_file_frac",
    "density:suspicious_category_breadth_log",
    "density:hostile_category_breadth_log",
    "density:hostile_share_of_suspicious",
)


def _density_values(report: dict[str, Any]) -> dict[str, float]:
    files = list(features.report_files(report))
    total_size = 0.0
    finding_count = 0
    suspicious_count = 0
    hostile_count = 0
    suspicious_files = 0
    hostile_files = 0
    suspicious_categories: set[str] = set()
    hostile_categories: set[str] = set()
    top_suspicious_density = 0.0
    top_hostile_density = 0.0

    for file_entry in files:
        try:
            file_size = float(file_entry.get("sz") or file_entry.get("size") or 0.0)
        except (TypeError, ValueError):
            file_size = 0.0
        total_size += max(file_size, 0.0)
        file_suspicious = 0
        file_hostile = 0
        for finding in file_entry.get("ts") or []:
            try:
                conf = float(finding.get("c", 1.0))
            except (TypeError, ValueError):
                conf = 1.0
            if conf < features.MIN_CONFIDENCE:
                continue
            finding_count += 1
            try:
                crit = int(finding.get("l", 0) or 0)
            except (TypeError, ValueError):
                crit = 0
            fid = str(finding.get("i") or "")
            category = fid.split("/", 1)[0] if fid else "unknown"
            if crit >= 4:
                suspicious_count += 1
                file_suspicious += 1
                suspicious_categories.add(category)
            if crit >= 5:
                hostile_count += 1
                file_hostile += 1
                hostile_categories.add(category)
        if file_suspicious:
            suspicious_files += 1
        if file_hostile:
            hostile_files += 1
        file_kb = max(file_size / 1024.0, 1.0)
        top_suspicious_density = max(top_suspicious_density, file_suspicious / file_kb)
        top_hostile_density = max(top_hostile_density, file_hostile / file_kb)

    file_count = len(files)
    total_kb = max(total_size / 1024.0, 1.0)
    return {
        "density:file_count_log": math.log1p(file_count),
        "density:total_kb_log": math.log1p(total_kb),
        "density:finding_count_log": math.log1p(finding_count),
        "density:suspicious_count_log": math.log1p(suspicious_count),
        "density:hostile_count_log": math.log1p(hostile_count),
        "density:suspicious_per_kb": suspicious_count / total_kb,
        "density:hostile_per_kb": hostile_count / total_kb,
        "density:top_file_suspicious_per_kb": top_suspicious_density,
        "density:top_file_hostile_per_kb": top_hostile_density,
        "density:suspicious_file_frac": suspicious_files / max(file_count, 1),
        "density:hostile_file_frac": hostile_files / max(file_count, 1),
        "density:suspicious_category_breadth_log": math.log1p(len(suspicious_categories)),
        "density:hostile_category_breadth_log": math.log1p(len(hostile_categories)),
        "density:hostile_share_of_suspicious": hostile_count / max(suspicious_count, 1),
    }


def _fixed_value_matrix(
    db_path: Path | str,
    rows: list[tuple[int, int]],
    names: tuple[str, ...],
    value_fn: Any,
    *,
    batch_size: int = 1000,
) -> sp.csr_matrix:
    row_positions: list[int] = []
    col_positions: list[int] = []
    values: list[float] = []
    ids = [int(row_id) for row_id, _label in rows]
    for start in range(0, len(ids), batch_size):
        chunk = ids[start : start + batch_size]
        fetched = data.fetch_cleave_results(db_path, chunk)
        for offset, row_id in enumerate(chunk):
            item = fetched.get(row_id)
            if not item:
                continue
            report = _coerce_report(item["cleave_result"])
            raw_values = value_fn(report)
            for col, name in enumerate(names):
                value = raw_values.get(name, 0.0)
                if value == 0.0:
                    continue
                row_positions.append(start + offset)
                col_positions.append(col)
                values.append(float(value))
    return sp.csr_matrix(
        (np.asarray(values, dtype=np.float32), (row_positions, col_positions)),
        shape=(len(rows), len(names)),
        dtype=np.float32,
    )


def _build_token_vocab(
    db_path: Path | str,
    rows: list[tuple[int, int]],
    token_fn: Any,
    *,
    top_k: int,
    min_malware_freq: int,
    max_benign_frac: float,
    batch_size: int = 1000,
) -> tuple[dict[str, int], dict[str, float]]:
    malware_docs = 0
    benign_docs = 0
    malware_counts: Counter[str] = Counter()
    benign_counts: Counter[str] = Counter()
    label_by_id = {int(row_id): int(label) for row_id, label in rows}
    ids = [int(row_id) for row_id, _label in rows]
    for start in range(0, len(ids), batch_size):
        chunk = ids[start : start + batch_size]
        fetched = data.fetch_cleave_results(db_path, chunk)
        for row_id in chunk:
            item = fetched.get(row_id)
            if not item:
                continue
            label = label_by_id[row_id]
            if label == 1:
                malware_docs += 1
            else:
                benign_docs += 1
            tokens = set(token_fn(item))
            if label == 1:
                malware_counts.update(tokens)
            else:
                benign_counts.update(tokens)
    scored: list[tuple[float, str]] = []
    for token, malware_count in malware_counts.items():
        if malware_count < min_malware_freq:
            continue
        benign_count = benign_counts.get(token, 0)
        benign_frac = benign_count / max(benign_docs, 1)
        if benign_frac > max_benign_frac:
            continue
        malware_frac = malware_count / max(malware_docs, 1)
        score = malware_frac / max(benign_frac, 1 / max(benign_docs, 1))
        score *= math.log1p(malware_count)
        scored.append((score, token))
    scored.sort(reverse=True)
    selected = [token for _score, token in scored[:top_k]]
    vocab = {token: idx for idx, token in enumerate(selected)}
    total_docs = malware_docs + benign_docs
    idf = {}
    for token in selected:
        doc_count = malware_counts.get(token, 0) + benign_counts.get(token, 0)
        idf[token] = math.log((1 + total_docs) / (1 + doc_count)) + 1.0
    return vocab, idf


def _token_matrix(
    db_path: Path | str,
    rows: list[tuple[int, int]],
    vocab: dict[str, int],
    token_fn: Any,
    *,
    value: str,
    idf: dict[str, float],
    batch_size: int = 1000,
) -> sp.csr_matrix:
    row_positions: list[int] = []
    col_positions: list[int] = []
    values: list[float] = []
    ids = [int(row_id) for row_id, _label in rows]
    for start in range(0, len(ids), batch_size):
        chunk = ids[start : start + batch_size]
        fetched = data.fetch_cleave_results(db_path, chunk)
        for offset, row_id in enumerate(chunk):
            item = fetched.get(row_id)
            if not item:
                continue
            counts = Counter(token for token in token_fn(item) if token in vocab)
            for token, count in counts.items():
                row_positions.append(start + offset)
                col_positions.append(vocab[token])
                if value == "boolean":
                    values.append(1.0)
                elif value == "log":
                    values.append(math.log1p(count))
                elif value == "tfidf":
                    values.append(math.log1p(count) * idf.get(token, 1.0))
                else:
                    raise ValueError(f"unknown token feature value: {value}")
    return sp.csr_matrix(
        (np.asarray(values, dtype=np.float32), (row_positions, col_positions)),
        shape=(len(rows), len(vocab)),
        dtype=np.float32,
    )


def _build_metric_vocab(
    db_path: Path | str,
    rows: list[tuple[int, int]],
    *,
    min_malware_freq: int,
    max_benign_frac: float,
    batch_size: int = 1000,
) -> dict[str, int]:
    malware_docs = 0
    benign_docs = 0
    malware_counts: Counter[str] = Counter()
    benign_counts: Counter[str] = Counter()
    label_by_id = {int(row_id): int(label) for row_id, label in rows}
    ids = [int(row_id) for row_id, _label in rows]
    for start in range(0, len(ids), batch_size):
        chunk = ids[start : start + batch_size]
        fetched = data.fetch_cleave_results(db_path, chunk)
        for row_id in chunk:
            item = fetched.get(row_id)
            if not item:
                continue
            label = label_by_id[row_id]
            if label == 1:
                malware_docs += 1
            else:
                benign_docs += 1
            report = _coerce_report(item["cleave_result"])
            names = set(_metric_values(report))
            if label == 1:
                malware_counts.update(names)
            else:
                benign_counts.update(names)
    selected: list[str] = []
    for name, malware_count in malware_counts.items():
        if malware_count < min_malware_freq:
            continue
        benign_frac = benign_counts.get(name, 0) / max(benign_docs, 1)
        if benign_frac <= max_benign_frac:
            selected.append(name)
    selected.sort()
    names: list[str] = []
    for name in selected:
        names.append(name)
        names.append(f"{name}:present")
        names.append(f"{name}:missing")
    return {name: idx for idx, name in enumerate(names)}


def _metric_matrix(
    db_path: Path | str,
    rows: list[tuple[int, int]],
    vocab: dict[str, int],
    *,
    batch_size: int = 1000,
) -> sp.csr_matrix:
    row_positions: list[int] = []
    col_positions: list[int] = []
    values: list[float] = []
    metric_names = [name for name in vocab if not name.endswith((":present", ":missing"))]
    ids = [int(row_id) for row_id, _label in rows]
    for start in range(0, len(ids), batch_size):
        chunk = ids[start : start + batch_size]
        fetched = data.fetch_cleave_results(db_path, chunk)
        for offset, row_id in enumerate(chunk):
            item = fetched.get(row_id)
            if not item:
                continue
            report = _coerce_report(item["cleave_result"])
            metrics = _metric_values(report)
            for name in metric_names:
                value = metrics.get(name)
                if value is None:
                    idx = vocab.get(f"{name}:missing")
                    if idx is not None:
                        row_positions.append(start + offset)
                        col_positions.append(idx)
                        values.append(1.0)
                    continue
                raw_idx = vocab[name]
                row_positions.append(start + offset)
                col_positions.append(raw_idx)
                values.append(math.copysign(math.log1p(abs(value)), value))
                present_idx = vocab.get(f"{name}:present")
                if present_idx is not None:
                    row_positions.append(start + offset)
                    col_positions.append(present_idx)
                    values.append(1.0)
    return sp.csr_matrix(
        (np.asarray(values, dtype=np.float32), (row_positions, col_positions)),
        shape=(len(rows), len(vocab)),
        dtype=np.float32,
    )


def _build_trait_vocab(
    db_path: Path | str,
    rows: list[tuple[int, int]],
    *,
    mode: str,
    value: str,
    min_crit: int,
    path_depth: int,
    top_k: int,
    min_malware_freq: int,
    max_benign_frac: float,
    batch_size: int = 1000,
) -> tuple[dict[str, int], dict[str, float]]:
    malware_docs = 0
    benign_docs = 0
    malware_counts: Counter[str] = Counter()
    benign_counts: Counter[str] = Counter()
    label_by_id = {int(row_id): int(label) for row_id, label in rows}
    ids = [int(row_id) for row_id, _label in rows]
    for start in range(0, len(ids), batch_size):
        chunk = ids[start : start + batch_size]
        fetched = data.fetch_cleave_results(db_path, chunk)
        for row_id in chunk:
            item = fetched.get(row_id)
            if not item:
                continue
            label = label_by_id[row_id]
            if label == 1:
                malware_docs += 1
            else:
                benign_docs += 1
            report = _coerce_report(item["cleave_result"])
            tokens = set(
                _trait_tokens(
                    report,
                    mode=mode,
                    min_crit=min_crit,
                    path_depth=path_depth,
                ),
            )
            if label == 1:
                malware_counts.update(tokens)
            else:
                benign_counts.update(tokens)
    scored: list[tuple[float, str]] = []
    for token, malware_count in malware_counts.items():
        if malware_count < min_malware_freq:
            continue
        benign_count = benign_counts.get(token, 0)
        benign_frac = benign_count / max(benign_docs, 1)
        if benign_frac > max_benign_frac:
            continue
        malware_frac = malware_count / max(malware_docs, 1)
        score = malware_frac / max(benign_frac, 1 / max(benign_docs, 1))
        score *= math.log1p(malware_count)
        scored.append((score, token))
    scored.sort(reverse=True)
    selected = [token for _score, token in scored[:top_k]]
    vocab = {token: idx for idx, token in enumerate(selected)}
    idf: dict[str, float] = {}
    if value == "tfidf":
        total_docs = malware_docs + benign_docs
        for token in selected:
            doc_count = malware_counts.get(token, 0) + benign_counts.get(token, 0)
            idf[token] = math.log((1 + total_docs) / (1 + doc_count)) + 1.0
    return vocab, idf


def _trait_matrix(
    db_path: Path | str,
    rows: list[tuple[int, int]],
    vocab: dict[str, int],
    *,
    mode: str,
    value: str,
    min_crit: int,
    path_depth: int,
    idf: dict[str, float],
    batch_size: int = 1000,
) -> sp.csr_matrix:
    row_positions: list[int] = []
    col_positions: list[int] = []
    values: list[float] = []
    ids = [int(row_id) for row_id, _label in rows]
    for start in range(0, len(ids), batch_size):
        chunk = ids[start : start + batch_size]
        fetched = data.fetch_cleave_results(db_path, chunk)
        for offset, row_id in enumerate(chunk):
            item = fetched.get(row_id)
            if not item:
                continue
            report = _coerce_report(item["cleave_result"])
            counts = Counter(
                token
                for token in _trait_tokens(
                    report,
                    mode=mode,
                    min_crit=min_crit,
                    path_depth=path_depth,
                )
                if token in vocab
            )
            for token, count in counts.items():
                row_positions.append(start + offset)
                col_positions.append(vocab[token])
                if value == "boolean":
                    values.append(1.0)
                elif value == "log":
                    values.append(math.log1p(count))
                elif value == "tfidf":
                    values.append(math.log1p(count) * idf.get(token, 1.0))
                else:
                    raise ValueError(f"unknown trait feature value: {value}")
    return sp.csr_matrix(
        (np.asarray(values, dtype=np.float32), (row_positions, col_positions)),
        shape=(len(rows), len(vocab)),
        dtype=np.float32,
    )


def _general_baseline(labels: np.ndarray, general_probs: np.ndarray) -> list[dict[str, Any]]:
    route = {
        "name": "general",
        "indices": np.arange(len(labels), dtype=np.int64),
        "probs": general_probs,
    }
    return [
        {
            "level": int(target["level"]),
            "hostile": _calibrate_one(
                labels,
                [route],
                target_per_million=float(target["hostile_per_million"]),
            ),
        }
        for target in thresholds.SEVERITY_LEVEL_TARGETS
    ]


def _routed_levels(
    labels: np.ndarray,
    general_probs: np.ndarray,
    elf_indices: np.ndarray,
    elf_probs: np.ndarray,
    *,
    rule: RuleName,
) -> list[dict[str, Any]]:
    if rule == "or":
        routes = [
            {
                "name": "general",
                "indices": np.arange(len(labels), dtype=np.int64),
                "probs": general_probs,
            },
            {"name": "elf", "indices": elf_indices, "probs": elf_probs},
        ]
    elif rule == "replacement":
        all_indices = np.arange(len(labels), dtype=np.int64)
        non_elf = np.setdiff1d(all_indices, elf_indices, assume_unique=False)
        routes = [
            {"name": "general_non_elf", "indices": non_elf, "probs": general_probs[non_elf]},
            {"name": "elf", "indices": elf_indices, "probs": elf_probs},
        ]
    else:
        raise ValueError(f"unknown rule: {rule}")
    return [
        {
            "level": int(target["level"]),
            "hostile": _calibrate_one(
                labels,
                routes,
                target_per_million=float(target["hostile_per_million"]),
            ),
        }
        for target in thresholds.SEVERITY_LEVEL_TARGETS
    ]


def _level_summary(levels: list[dict[str, Any]]) -> dict[str, Any]:
    # Per-100M scale: L50 = 0.5 FP/M (dense headline operating point),
    # L100 = 1 FP/M (loose-end headline). Suspicious is a consumer-side
    # derivation; collimator emits only hostile.
    summary: dict[str, Any] = {}
    for key, level_no in (("l50_hostile", 50), ("l100_hostile", 100)):
        entry = next((item for item in levels if item["level"] == level_no), None)
        if entry is None:
            continue
        summary[key] = entry["hostile"]
    return summary


def _metric_summary(y_true: np.ndarray, probs: np.ndarray) -> dict[str, float]:
    precision, recall, pr_thresholds = precision_recall_curve(y_true, probs)
    if len(pr_thresholds) == 0:
        max_f1 = 0.0
        best_threshold = 1.0
    else:
        f1_values = (2 * precision[:-1] * recall[:-1]) / np.maximum(
            precision[:-1] + recall[:-1],
            1e-12,
        )
        best_idx = int(np.nanargmax(f1_values))
        max_f1 = float(f1_values[best_idx])
        best_threshold = float(pr_thresholds[best_idx])
    return {
        "auc": float(roc_auc_score(y_true, probs)),
        "average_precision": float(average_precision_score(y_true, probs)),
        "max_f1": max_f1,
        "max_f1_threshold": best_threshold,
        "f1_at_0_5": float(f1_score(y_true, probs >= 0.5)),
    }


def _elf_fp_budget_table(y_true: np.ndarray, probs: np.ndarray) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    benign = int(np.sum(y_true == 0))
    malware = int(np.sum(y_true == 1))
    order = np.argsort(-probs, kind="mergesort")
    sorted_labels = y_true[order]
    sorted_probs = probs[order]
    cum_tp = np.cumsum(sorted_labels == 1)
    cum_fp = np.cumsum(sorted_labels == 0)
    for target in (0, 1, 5, 9, 40, 50):
        budget = (
            0
            if target == 0
            else min(benign, max(1, int(np.floor(benign * target / 1_000_000))))
        )
        ok = np.flatnonzero(cum_fp <= budget)
        if len(ok) == 0:
            threshold = float("inf")
            tp = 0
            fp = 0
        else:
            idx = int(ok[-1])
            threshold = float(sorted_probs[idx])
            tp = int(cum_tp[idx])
            fp = int(cum_fp[idx])
        out.append(
            {
                # `target` is in per-million units (input convention here);
                # emit it as the canonical per-100M output.
                "target_fp_per_100M": float(target) * 100.0,
                "budget": int(budget),
                "threshold": threshold,
                "recall": float(tp / malware) if malware else 0.0,
                "fp": fp,
                "tp": tp,
            },
        )
    return out


def _fit_lightgbm(
    candidate: Candidate,
    x_train: sp.csr_matrix,
    y_train: np.ndarray,
    *,
    seed: int,
) -> Any:
    train_idx, val_idx = train_test_split(
        np.arange(len(y_train)),
        test_size=0.15,
        stratify=y_train,
        random_state=seed,
    )
    n_benign = int(np.sum(y_train[train_idx] == 0))
    n_malware = int(np.sum(y_train[train_idx] == 1))
    clf = lgb.LGBMClassifier(
        objective="binary",
        scale_pos_weight=n_benign / max(n_malware, 1),
        random_state=seed,
        n_jobs=-1,
        force_col_wise=True,
        verbosity=-1,
        **candidate.params,
    )
    callbacks: list[Any] = []
    if candidate.params.get("boosting_type") != "dart":
        callbacks.append(lgb.early_stopping(50, verbose=False))
    clf.fit(
        x_train[train_idx],
        y_train[train_idx],
        eval_set=[(x_train[val_idx], y_train[val_idx])],
        eval_metric="auc",
        callbacks=callbacks,
    )
    return clf


def _fit_xgboost(
    candidate: Candidate,
    x_train: sp.csr_matrix,
    y_train: np.ndarray,
    *,
    seed: int,
    device: str,
) -> Any:
    train_idx, val_idx = train_test_split(
        np.arange(len(y_train)),
        test_size=0.15,
        stratify=y_train,
        random_state=seed,
    )
    n_benign = int(np.sum(y_train[train_idx] == 0))
    n_malware = int(np.sum(y_train[train_idx] == 1))
    clf = xgb.XGBClassifier(
        objective="binary:logistic",
        eval_metric="aucpr",
        tree_method="hist",
        device=device,
        scale_pos_weight=n_benign / max(n_malware, 1),
        random_state=seed,
        early_stopping_rounds=50,
        **candidate.params,
    )
    clf.fit(
        x_train[train_idx],
        y_train[train_idx],
        eval_set=[(x_train[val_idx], y_train[val_idx])],
        verbose=False,
    )
    return clf


def _score(estimator: Any, x_matrix: sp.csr_matrix) -> np.ndarray:
    return model.predict_proba(estimator, x_matrix).astype(np.float32, copy=False)


def _write_feature_spec_copy(spec_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "feature_spec.json"
    target.write_bytes(spec_path.read_bytes())


def _candidate_by_name(name: str) -> Candidate:
    for candidate in (*FIRST_BATCH, *EXPANDED_BATCH):
        if candidate.name == name:
            return candidate
    raise KeyError(name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    parser.add_argument("--target-name", default="elf")
    parser.add_argument(
        "--file-types",
        nargs="+",
        default=["elf"],
        help="File types included in the specialist target population.",
    )
    parser.add_argument(
        "--general-scores",
        type=Path,
        default=Path("out/models/azoth/general/threshold_scores.npz"),
    )
    parser.add_argument(
        "--feature-spec",
        type=Path,
        default=Path("out/models/azoth/general/feature_spec.json"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("out/models/azoth-elf/research"))
    parser.add_argument("--output", type=Path, default=Path("out/models/azoth-elf/research.json"))
    parser.add_argument("--workers", type=int, default=64)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="cuda")
    parser.add_argument(
        "--trait-mode",
        choices=["none", "exact", "hierarchy", "combo"],
        default="none",
    )
    parser.add_argument(
        "--trait-value",
        choices=["boolean", "log", "tfidf"],
        default="log",
    )
    parser.add_argument("--trait-min-crit", type=int, default=0)
    parser.add_argument("--trait-path-depth", type=int, default=0)
    parser.add_argument("--trait-top-k", type=int, default=50_000)
    parser.add_argument("--trait-min-malware-freq", type=int, default=3)
    parser.add_argument("--trait-max-benign-frac", type=float, default=0.01)
    parser.add_argument(
        "--extra-families",
        nargs="*",
        choices=["ngrams", "metrics", "symbols", "formula", "elements", "density"],
        default=[],
    )
    parser.add_argument("--extra-value", choices=["boolean", "log", "tfidf"], default="log")
    parser.add_argument("--extra-top-k", type=int, default=50_000)
    parser.add_argument("--extra-min-malware-freq", type=int, default=3)
    parser.add_argument("--extra-max-benign-frac", type=float, default=0.01)
    parser.add_argument("--ngram-order-min", type=int, default=2)
    parser.add_argument("--ngram-order-max", type=int, default=8)
    parser.add_argument("--ngram-min-crit", type=int, default=4)
    parser.add_argument("--ngram-path-depth", type=int, default=0)
    parser.add_argument("--ngram-max-paths", type=int, default=16)
    parser.add_argument("--ngram-max-per-file", type=int, default=20_000)
    parser.add_argument(
        "--candidates",
        nargs="+",
        default=[candidate.name for candidate in FIRST_BATCH],
        help="Candidate names to run, or 'first-batch'/'expanded-batch'.",
    )
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.candidates == ["first-batch"]:
        candidate_names = [candidate.name for candidate in FIRST_BATCH]
    elif args.candidates == ["expanded-batch"]:
        candidate_names = [candidate.name for candidate in EXPANDED_BATCH]
    else:
        candidate_names = args.candidates
    candidates = [_candidate_by_name(name) for name in candidate_names]

    cache = np.load(args.general_scores)
    row_ids = cache["row_ids"].astype(np.int64)
    labels = cache["labels"].astype(np.int8)
    general_probs = cache["probs"].astype(np.float32)
    max_id = int(cache["corpus_requested_max_id"]) or int(cache["corpus_max_row_id"])
    row_index = {int(row_id): idx for idx, row_id in enumerate(row_ids)}

    target_file_types = tuple(args.file_types)
    target_rows_all = _fetch_rows(
        args.db,
        file_types=target_file_types,
        max_id=max_id,
        min_score=None,
    )
    target_rows = [
        (row_id, label)
        for row_id, label, _is_test, _ft in target_rows_all
        if row_id in row_index
    ]
    target_indices = np.asarray(
        [row_index[row_id] for row_id, _label in target_rows],
        dtype=np.int64,
    )
    train_rows_all = _fetch_rows(
        args.db,
        file_types=target_file_types,
        max_id=max_id,
        min_score=data.MIN_SAMPLE_SCORE,
    )
    train_rows = _ids_labels(train_rows_all, test=False)

    LOG.info(
        "snapshot max_id=%d rows=%d target=%s target_rows=%d train_rows=%d",
        max_id,
        len(labels),
        args.target_name,
        len(target_rows),
        len(train_rows),
    )
    spec = features.FeatureSpec.load(args.feature_spec)
    x_train, y_train = _matrix(args.db, train_rows, spec, args.workers)
    x_target, y_target = _matrix(args.db, target_rows, spec, args.workers)
    trait_feature_count = 0
    trait_vocab_path = ""
    extra_features: list[dict[str, Any]] = []
    if args.trait_mode != "none":
        LOG.info(
            "building trait vocab mode=%s value=%s top_k=%d "
            "min_malware_freq=%d max_benign_frac=%.4f",
            args.trait_mode,
            args.trait_value,
            args.trait_top_k,
            args.trait_min_malware_freq,
            args.trait_max_benign_frac,
        )
        vocab, idf = _build_trait_vocab(
            args.db,
            train_rows,
            mode=args.trait_mode,
            value=args.trait_value,
            min_crit=args.trait_min_crit,
            path_depth=args.trait_path_depth,
            top_k=args.trait_top_k,
            min_malware_freq=args.trait_min_malware_freq,
            max_benign_frac=args.trait_max_benign_frac,
        )
        trait_feature_count = len(vocab)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        trait_vocab_path = str(args.output_dir / "trait_vocab.json")
        with open(trait_vocab_path, "w") as f:
            json.dump(
                {
                    "mode": args.trait_mode,
                    "value": args.trait_value,
                    "min_crit": args.trait_min_crit,
                    "path_depth": args.trait_path_depth,
                    "top_k": args.trait_top_k,
                    "min_malware_freq": args.trait_min_malware_freq,
                    "max_benign_frac": args.trait_max_benign_frac,
                    "tokens": [
                        token
                        for token, _idx in sorted(vocab.items(), key=lambda item: item[1])
                    ],
                    "idf": idf,
                },
                f,
                indent=2,
            )
        LOG.info("built trait vocab with %d features", trait_feature_count)
        trait_train = _trait_matrix(
            args.db,
            train_rows,
            vocab,
            mode=args.trait_mode,
            value=args.trait_value,
            min_crit=args.trait_min_crit,
            path_depth=args.trait_path_depth,
            idf=idf,
        )
        trait_elf = _trait_matrix(
            args.db,
            target_rows,
            vocab,
            mode=args.trait_mode,
            value=args.trait_value,
            min_crit=args.trait_min_crit,
            path_depth=args.trait_path_depth,
            idf=idf,
        )
        x_train = sp.hstack([x_train, trait_train], format="csr")
        x_target = sp.hstack([x_target, trait_elf], format="csr")
        LOG.info("expanded matrix to %d features", x_train.shape[1])

    for family in args.extra_families:
        LOG.info("building extra feature family=%s", family)
        if family == "ngrams":
            def token_fn(item: dict[str, Any]) -> list[str]:
                return _ngram_tokens(
                    _coerce_report(item["cleave_result"]),
                    min_crit=args.ngram_min_crit,
                    path_depth=args.ngram_path_depth,
                    order_min=args.ngram_order_min,
                    order_max=args.ngram_order_max,
                    max_paths=args.ngram_max_paths,
                    max_ngrams_per_file=args.ngram_max_per_file,
                )
        elif family == "symbols":
            def token_fn(item: dict[str, Any]) -> list[str]:
                return _symbol_tokens(_coerce_report(item["cleave_result"]))
        elif family == "formula":
            def token_fn(item: dict[str, Any]) -> list[str]:
                return _formula_tokens(item)
        elif family == "elements":
            def token_fn(item: dict[str, Any]) -> list[str]:
                return _element_tokens(item)
        elif family == "density":
            density_train = _fixed_value_matrix(
                args.db,
                train_rows,
                DENSITY_FEATURES,
                _density_values,
            )
            density_target = _fixed_value_matrix(
                args.db,
                target_rows,
                DENSITY_FEATURES,
                _density_values,
            )
            vocab_path = args.output_dir / f"{family}_vocab.json"
            args.output_dir.mkdir(parents=True, exist_ok=True)
            with open(vocab_path, "w") as f:
                json.dump(
                    {
                        "family": family,
                        "features": list(DENSITY_FEATURES),
                    },
                    f,
                    indent=2,
                )
            x_train = sp.hstack([x_train, density_train], format="csr")
            x_target = sp.hstack([x_target, density_target], format="csr")
            extra_features.append(
                {
                    "family": family,
                    "feature_count": len(DENSITY_FEATURES),
                    "vocab": str(vocab_path),
                },
            )
            LOG.info(
                "added family=%s features=%d matrix_features=%d",
                family,
                len(DENSITY_FEATURES),
                x_train.shape[1],
            )
            continue
        elif family == "metrics":
            metric_vocab = _build_metric_vocab(
                args.db,
                train_rows,
                min_malware_freq=args.extra_min_malware_freq,
                max_benign_frac=args.extra_max_benign_frac,
            )
            extra_train = _metric_matrix(args.db, train_rows, metric_vocab)
            extra_target = _metric_matrix(args.db, target_rows, metric_vocab)
            vocab_path = args.output_dir / f"{family}_vocab.json"
            args.output_dir.mkdir(parents=True, exist_ok=True)
            with open(vocab_path, "w") as f:
                json.dump(
                    {
                        "family": family,
                        "features": [
                            name
                            for name, _idx in sorted(
                                metric_vocab.items(),
                                key=lambda item: item[1],
                            )
                        ],
                    },
                    f,
                    indent=2,
            )
            x_train = sp.hstack([x_train, extra_train], format="csr")
            x_target = sp.hstack([x_target, extra_target], format="csr")
            extra_features.append(
                {
                    "family": family,
                    "feature_count": len(metric_vocab),
                    "vocab": str(vocab_path),
                },
            )
            LOG.info(
                "added family=%s features=%d matrix_features=%d",
                family,
                len(metric_vocab),
                x_train.shape[1],
            )
            continue
        else:
            raise ValueError(family)

        vocab, idf = _build_token_vocab(
            args.db,
            train_rows,
            token_fn,
            top_k=args.extra_top_k,
            min_malware_freq=args.extra_min_malware_freq,
            max_benign_frac=args.extra_max_benign_frac,
        )
        extra_train = _token_matrix(
            args.db,
            train_rows,
            vocab,
            token_fn,
            value=args.extra_value,
            idf=idf,
        )
        extra_elf = _token_matrix(
            args.db,
            target_rows,
            vocab,
            token_fn,
            value=args.extra_value,
            idf=idf,
        )
        vocab_path = args.output_dir / f"{family}_vocab.json"
        args.output_dir.mkdir(parents=True, exist_ok=True)
        with open(vocab_path, "w") as f:
            json.dump(
                {
                    "family": family,
                    "value": args.extra_value,
                    "top_k": args.extra_top_k,
                    "min_malware_freq": args.extra_min_malware_freq,
                    "max_benign_frac": args.extra_max_benign_frac,
                    "ngram_order_min": args.ngram_order_min,
                    "ngram_order_max": args.ngram_order_max,
                    "ngram_min_crit": args.ngram_min_crit,
                    "ngram_path_depth": args.ngram_path_depth,
                    "ngram_max_paths": args.ngram_max_paths,
                    "tokens": [
                        token
                        for token, _idx in sorted(vocab.items(), key=lambda item: item[1])
                    ],
                    "idf": idf,
                },
                f,
                indent=2,
        )
        x_train = sp.hstack([x_train, extra_train], format="csr")
        x_target = sp.hstack([x_target, extra_elf], format="csr")
        extra_features.append(
            {
                "family": family,
                "feature_count": len(vocab),
                "vocab": str(vocab_path),
            },
        )
        LOG.info(
            "added family=%s features=%d matrix_features=%d",
            family,
            len(vocab),
            x_train.shape[1],
        )

    experiments: list[dict[str, Any]] = []
    baseline_levels = _general_baseline(labels, general_probs)
    experiments.append(
        {
            "name": "general_baseline",
            "learner": "existing",
            "rules": {"general": baseline_levels},
            "summary": _level_summary(baseline_levels),
        },
    )

    for candidate in candidates:
        LOG.info("training %s", candidate.name)
        start = time.monotonic()
        if candidate.learner == "lightgbm":
            estimator = _fit_lightgbm(candidate, x_train, y_train, seed=args.seed)
            model_file = "model.txt"
        elif candidate.learner == "xgboost":
            estimator = _fit_xgboost(
                candidate,
                x_train,
                y_train,
                seed=args.seed,
                device=args.device,
            )
            model_file = "model.json"
        else:
            raise ValueError(candidate.learner)
        fit_seconds = time.monotonic() - start

        candidate_dir = args.output_dir / candidate.name
        export.save_model(estimator, candidate_dir / model_file)
        _write_feature_spec_copy(args.feature_spec, candidate_dir)
        model_size = (candidate_dir / model_file).stat().st_size
        target_probs = _score(estimator, x_target)

        rules = {
            "or": _routed_levels(
                labels,
                general_probs,
                target_indices,
                target_probs,
                rule="or",
            ),
            "replacement": _routed_levels(
                labels,
                general_probs,
                target_indices,
                target_probs,
                rule="replacement",
            ),
        }
        exp = {
            "name": candidate.name,
            "learner": candidate.learner,
            "params": candidate.params,
            "model_path": str(candidate_dir / model_file),
            "feature_spec": str(candidate_dir / "feature_spec.json"),
            "feature_count": int(x_train.shape[1]),
            "base_feature_count": int(spec.total_features),
            "trait_feature_count": int(trait_feature_count),
            "extra_features": extra_features,
            "train_rows": int(len(y_train)),
            "train_malware": int(np.sum(y_train == 1)),
            "train_benign": int(np.sum(y_train == 0)),
            "fit_seconds": fit_seconds,
            "model_size_bytes": int(model_size),
            "target_metrics": _metric_summary(y_target, target_probs),
            "target_fp_budgets": _elf_fp_budget_table(y_target, target_probs),
            "elf_metrics": _metric_summary(y_target, target_probs),
            "elf_fp_budgets": _elf_fp_budget_table(y_target, target_probs),
            "rules": rules,
            "summary": {rule: _level_summary(levels) for rule, levels in rules.items()},
        }
        experiments.append(exp)
        h = exp["summary"]["or"]["l5_hostile"]
        LOG.info("%s OR L5 hostile %.2f%% @ %d FP", candidate.name, 100.0 * h["recall"], h["fp"])

    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "max_id": max_id,
        "rows": int(len(labels)),
        "malware": int(np.sum(labels == 1)),
        "benign": int(np.sum(labels == 0)),
        "target_name": args.target_name,
        "file_types": list(target_file_types),
        "target_rows": int(len(target_indices)),
        "target_malware": int(np.sum(y_target == 1)),
        "target_benign": int(np.sum(y_target == 0)),
        "elf_rows": int(len(target_indices)),
        "elf_malware": int(np.sum(y_target == 1)),
        "elf_benign": int(np.sum(y_target == 0)),
        "feature_spec": str(args.feature_spec),
        "feature_count": int(x_train.shape[1]),
        "base_feature_count": int(spec.total_features),
        "trait_feature_count": int(trait_feature_count),
        "extra_feature_count": int(sum(int(item["feature_count"]) for item in extra_features)),
        "extra_features": extra_features,
        "trait_vocab": trait_vocab_path,
        "trait_config": {
            "mode": args.trait_mode,
            "value": args.trait_value,
            "min_crit": args.trait_min_crit,
            "path_depth": args.trait_path_depth,
            "top_k": args.trait_top_k,
            "min_malware_freq": args.trait_min_malware_freq,
            "max_benign_frac": args.trait_max_benign_frac,
        },
        "experiments": experiments,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"wrote {args.output}")
    for exp in experiments:
        if exp["name"] == "general_baseline":
            h = exp["summary"]["l5_hostile"]
            print(f"{exp['name']}: L5 hostile {h['recall']:.2%} @ {h['fp']} FP")
            continue
        for rule, summary in exp["summary"].items():
            h = summary["l5_hostile"]
            print(f"{exp['name']} {rule}: L5 hostile {h['recall']:.2%} @ {h['fp']} FP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
