#!/usr/bin/env python3
"""Focused script-family malware detection experiments."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import logging
import math
import random
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import lightgbm as lgb
import numpy as np
import scipy.sparse as sp
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score

from collimator import data
from collimator.features import MIN_CONFIDENCE, _coerce_report, _finding_paths, _float, report_files  # noqa: PLC2701

LOG = logging.getLogger("script_detection_experiments")

SCRIPT_TYPES = (
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
    "vbs",
)

POOLS = {
    "python": ("python",),
    "javascript": ("javascript",),
    "py_js": ("python", "javascript"),
    "scripts": SCRIPT_TYPES,
}

CRIT_PREFIX = {3: "n", 4: "s", 5: "h"}


@dataclass(frozen=True)
class Row:
    row_id: int
    label: int
    file_type: str
    score: float
    is_test: bool


@dataclass(frozen=True)
class FeatureMode:
    name: str
    depth: int
    crit_filter: str
    n: int
    tiered: bool = False
    sequence: bool = False
    density: bool = False
    benign_framework: bool = False


def _placeholder(db_path: str) -> str:
    return "%s" if data._is_pg(db_path) else "?"  # noqa: SLF001


def _passes_filter(crit: int, filt: str) -> bool:
    if filt == "h":
        return crit >= 5
    if filt == "hs":
        return crit >= 4
    if filt == "hsn":
        return crit >= 3
    raise ValueError(f"unknown filter {filt}")


def _truncate(path: str, depth: int) -> str:
    if depth <= 0:
        return path
    return "/".join(path.split("/")[:depth])


def _hash(text: str, bits: int) -> int:
    digest = hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "little") & ((1 << bits) - 1)


def _fetch_rows(db_path: str, file_types: tuple[str, ...], max_id: int) -> list[Row]:
    marker = _placeholder(db_path)
    where = ["label IN ('bad', 'good')", "cleave_result IS NOT NULL", "skip = ''"]
    params: list[Any] = []
    if data._is_pg(db_path):  # noqa: SLF001
        where.append(f"COALESCE(NULLIF(file_type, ''), 'unknown') = ANY({marker})")
        params.append(list(file_types))
    else:
        placeholders = ",".join(marker for _ in file_types)
        where.append(f"COALESCE(NULLIF(file_type, ''), 'unknown') IN ({placeholders})")
        params.extend(file_types)
    if max_id:
        where.append(f"id <= {marker}")
        params.append(max_id)
    query = (
        "SELECT id, sha256, canonical_sha256, label, score, COALESCE(NULLIF(file_type, ''), 'unknown') "
        "FROM samples WHERE "
        + " AND ".join(where)
        + " ORDER BY id"
    )
    rows: list[Row] = []
    with data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        for row_id, sha256, canonical, label, score, file_type in data._execute(conn, query, params):  # noqa: SLF001
            split_key = canonical or sha256
            rows.append(
                Row(
                    row_id=int(row_id),
                    label=1 if str(label) == "bad" else 0,
                    file_type=str(file_type),
                    score=float(score or 0.0),
                    is_test=data.is_test_sample(str(split_key)),
                ),
            )
    return rows


def _cap(rows: list[Row], per_label: int, seed: int) -> list[Row]:
    if per_label <= 0:
        return rows
    rng = random.Random(seed)
    out: list[Row] = []
    for is_test in (False, True):
        for label in (0, 1):
            bucket = [r for r in rows if r.is_test == is_test and r.label == label]
            rng.shuffle(bucket)
            out.extend(bucket[:per_label])
    return sorted(out, key=lambda r: r.row_id)


def _load_reports(db_path: str, rows: list[Row], batch_size: int = 2000) -> dict[int, dict[str, Any]]:
    reports: dict[int, dict[str, Any]] = {}
    ids = [r.row_id for r in rows]
    for start in range(0, len(ids), batch_size):
        fetched = data.fetch_cleave_results(db_path, ids[start : start + batch_size])
        for row_id, item in fetched.items():
            report = _coerce_report(item.get("cleave_result"))
            if report is not None:
                reports[int(row_id)] = report
        LOG.info("fetched reports %d/%d", min(start + batch_size, len(ids)), len(ids))
    return reports


def _finding_tokens(report: dict[str, Any], mode: FeatureMode) -> list[str]:
    tokens: list[str] = []
    for file_entry in report_files(report):
        for finding in file_entry.get("ts") or []:
            fid = finding.get("i", "")
            if not fid or _float(finding.get("c", 1.0)) < MIN_CONFIDENCE:
                continue
            crit = int(finding.get("l", 0) or 0)
            if not _passes_filter(crit, mode.crit_filter):
                continue
            prefix = f"{CRIT_PREFIX.get(crit, 'n')}:" if mode.tiered else ""
            for path in _finding_paths(fid):
                tokens.append(prefix + _truncate(path, mode.depth))
    if mode.sequence:
        return tokens
    return sorted(set(tokens))


def _limited_combos(tokens: list[str], n: int, limit: int, *, sequence: bool) -> Iterable[tuple[str, ...]]:
    if sequence:
        count = 0
        for idx in range(max(0, len(tokens) - n + 1)):
            yield tuple(tokens[idx : idx + n])
            count += 1
            if count >= limit:
                return
        return
    count = 0
    for combo in itertools.combinations(tokens, n):
        yield combo
        count += 1
        if count >= limit:
            return


def _dense_stats(report: dict[str, Any], mode: FeatureMode) -> list[float]:
    counts = {3: 0, 4: 0, 5: 0}
    files = 0
    for file_entry in report_files(report):
        files += 1
        for finding in file_entry.get("ts") or []:
            if _float(finding.get("c", 1.0)) < MIN_CONFIDENCE:
                continue
            crit = int(finding.get("l", 0) or 0)
            if crit >= 5:
                counts[5] += 1
            elif crit == 4:
                counts[4] += 1
            elif crit == 3:
                counts[3] += 1
    total = sum(counts.values())
    return [
        math.log1p(total),
        math.log1p(counts[5]),
        math.log1p(counts[4]),
        math.log1p(counts[3]),
        math.log1p(files),
        math.log1p(total / max(files, 1)),
        float(mode.depth),
    ]


def _benign_framework_tokens(
    train_rows: list[Row],
    reports: dict[int, dict[str, Any]],
    *,
    depth: int,
    max_tokens: int,
) -> set[str]:
    benign: dict[str, int] = {}
    malware: dict[str, int] = {}
    mode = FeatureMode("framework_probe", depth=depth, crit_filter="hsn", n=1)
    for row in train_rows:
        toks = set(_finding_tokens(reports.get(row.row_id, {}), mode))
        target = malware if row.label else benign
        for tok in toks:
            target[tok] = target.get(tok, 0) + 1
    scored = [
        (b - 3 * malware.get(tok, 0), tok)
        for tok, b in benign.items()
        if b >= 20 and b > 4 * malware.get(tok, 0)
    ]
    return {tok for _score, tok in sorted(scored, reverse=True)[:max_tokens]}


def _feature_matrix(
    rows: list[Row],
    reports: dict[int, dict[str, Any]],
    mode: FeatureMode,
    *,
    hash_bits: int,
    max_tokens: int,
    max_combos: int,
    framework_tokens: set[str] | None = None,
) -> tuple[sp.csr_matrix, np.ndarray]:
    dim = 1 << hash_bits
    dense_dim = 12 if (mode.density or mode.benign_framework) else 3
    indptr = [0]
    indices: list[int] = []
    values: list[float] = []
    labels: list[int] = []
    framework_tokens = framework_tokens or set()
    for row in rows:
        report = reports.get(row.row_id, {})
        tokens = _finding_tokens(report, mode)
        if len(tokens) > max_tokens:
            tokens = tokens[:max_tokens]
        feats: dict[int, float] = {}
        if mode.n <= 1:
            combos = ((tok,) for tok in tokens)
        elif len(tokens) >= mode.n:
            combos = _limited_combos(tokens, mode.n, max_combos, sequence=mode.sequence)
        else:
            combos = ()
        for combo in combos:
            feats[_hash("\x1f".join(combo), hash_bits)] = 1.0
        dense_base = dim
        dense = [math.log1p(max(row.score, 0.0)), math.log1p(len(tokens)), 1.0 if not tokens else 0.0]
        if mode.density or mode.benign_framework:
            dense.extend(_dense_stats(report, mode))
        if mode.benign_framework:
            present = len(set(tokens) & framework_tokens)
            dense.extend([math.log1p(present), 1.0 if present else 0.0])
        for offset, value in enumerate(dense[:dense_dim]):
            feats[dense_base + offset] = float(value)
        for idx in sorted(feats):
            indices.append(idx)
            values.append(feats[idx])
        indptr.append(len(indices))
        labels.append(row.label)
    return (
        sp.csr_matrix((values, indices, indptr), shape=(len(rows), dim + dense_dim), dtype=np.float32),
        np.asarray(labels, dtype=np.int8),
    )


def _fit_classifier(x_train: sp.csr_matrix, y_train: np.ndarray, weights: np.ndarray | None, seed: int) -> lgb.LGBMClassifier:
    clf = lgb.LGBMClassifier(
        objective="binary",
        n_estimators=260,
        learning_rate=0.05,
        num_leaves=96,
        max_depth=10,
        min_child_samples=80,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=seed,
        n_jobs=8,
        verbosity=-1,
    )
    clf.fit(x_train, y_train, sample_weight=weights)
    return clf


def _metric_at_fp_count(y: np.ndarray, probs: np.ndarray, fp_count: int) -> dict[str, Any]:
    malware = int(np.sum(y == 1))
    benign = int(np.sum(y == 0))
    order = np.argsort(-probs)
    tp = fp = 0
    best: dict[str, Any] | None = None
    for idx in order:
        if y[idx] == 1:
            tp += 1
        else:
            fp += 1
        if fp <= fp_count:
            best = {"tp": tp, "fp": fp, "recall": tp / malware if malware else math.nan}
        else:
            break
    if best is None:
        best = {"tp": 0, "fp": 0, "recall": 0.0 if malware else math.nan}
    best["fp_per_100M"] = best["fp"] * 100_000_000.0 / benign if benign else math.nan
    return best


def _metrics(y: np.ndarray, probs: np.ndarray) -> dict[str, Any]:
    pred = probs >= 0.5
    out: dict[str, Any] = {
        "auc": float(roc_auc_score(y, probs)) if len(np.unique(y)) == 2 else None,
        "ap": float(average_precision_score(y, probs)) if len(np.unique(y)) == 2 else None,
        "f1": float(f1_score(y, pred, zero_division=0)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "fp_counts": {},
    }
    for count in (0, 1, 3, 5, 10, 25, 50):
        out["fp_counts"][str(count)] = _metric_at_fp_count(y, probs, count)
    return out


def _json_clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_clean(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def _score_table_features(score_table: Path, rows: list[Row]) -> tuple[np.ndarray, np.ndarray]:
    table = np.load(score_table)
    row_ids = table["row_ids"].astype(np.int64)
    route_names = [str(name) for name in table["route_names"]]
    scores = table["scores"].astype(np.float32)
    row_pos = {int(row_id): idx for idx, row_id in enumerate(row_ids)}
    general_idx = route_names.index("general")
    scripts_idx = route_names.index("filegroups/scripts") if "filegroups/scripts" in route_names else None
    x = np.zeros((len(rows), 4), dtype=np.float32)
    y = np.asarray([row.label for row in rows], dtype=np.int8)
    for out_idx, row in enumerate(rows):
        pos = row_pos.get(row.row_id)
        if pos is None:
            continue
        vals = [scores[general_idx, pos]]
        vals.append(scores[scripts_idx, pos] if scripts_idx is not None else np.nan)
        route = f"filetypes/{row.file_type}"
        vals.append(scores[route_names.index(route), pos] if route in route_names else np.nan)
        vals.append(max(v for v in vals if not math.isnan(float(v))) if any(not math.isnan(float(v)) for v in vals) else 0.0)
        x[out_idx, :] = np.nan_to_num(vals, nan=0.0)
    return x, y


def _run_mode(
    name: str,
    mode: FeatureMode,
    train_rows: list[Row],
    test_rows: list[Row],
    reports: dict[int, dict[str, Any]],
    args: argparse.Namespace,
    *,
    weights: np.ndarray | None = None,
) -> tuple[dict[str, Any], np.ndarray, np.ndarray, sp.csr_matrix, sp.csr_matrix]:
    framework = None
    if mode.benign_framework:
        framework = _benign_framework_tokens(train_rows, reports, depth=mode.depth, max_tokens=1000)
    x_train, y_train = _feature_matrix(
        train_rows,
        reports,
        mode,
        hash_bits=args.hash_bits,
        max_tokens=args.max_tokens,
        max_combos=args.max_combos,
        framework_tokens=framework,
    )
    x_test, y_test = _feature_matrix(
        test_rows,
        reports,
        mode,
        hash_bits=args.hash_bits,
        max_tokens=args.max_tokens,
        max_combos=args.max_combos,
        framework_tokens=framework,
    )
    clf = _fit_classifier(x_train, y_train, weights, args.seed)
    probs = clf.predict_proba(x_test)[:, 1]
    result = {
        "name": name,
        "mode": mode.__dict__,
        "train_rows": int(len(y_train)),
        "train_malware": int(np.sum(y_train == 1)),
        "train_benign": int(np.sum(y_train == 0)),
        "test_rows": int(len(y_test)),
        "test_malware": int(np.sum(y_test == 1)),
        "test_benign": int(np.sum(y_test == 0)),
        "metrics": _metrics(y_test, probs),
    }
    return result, probs, y_test, x_train, x_test


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    rows = sorted(
        payload["results"],
        key=lambda r: (
            r["metrics"]["fp_counts"]["1"]["recall"],
            r["metrics"].get("ap") or 0.0,
            r["metrics"].get("f1") or 0.0,
        ),
        reverse=True,
    )
    lines = [
        "# Azoth Script Detection Experiments",
        "",
        f"- Timestamp: `{payload['timestamp']}`",
        f"- Pool: `{payload['pool']}`",
        f"- Train rows: {payload['train_rows']}",
        f"- Test rows: {payload['test_rows']}",
        "",
        "| Rank | Experiment | AUC | AP | F1 | R@0FP | R@1FP | R@3FP | R@5FP | Test bad/good |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(rows, 1):
        m = row["metrics"]
        fp = m["fp_counts"]
        lines.append(
            f"| {idx} | `{row['name']}` | "
            f"{(m.get('auc') or 0.0):.4f} | {(m.get('ap') or 0.0):.4f} | {m['f1']:.4f} | "
            f"{100.0 * fp['0']['recall']:.2f}% | {100.0 * fp['1']['recall']:.2f}% | "
            f"{100.0 * fp['3']['recall']:.2f}% | {100.0 * fp['5']['recall']:.2f}% | "
            f"{row['test_malware']}/{row['test_benign']} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--score-table", type=Path, default=Path("out/models/azoth/score_table.npz"))
    parser.add_argument("--pool", choices=sorted(POOLS), default="scripts")
    parser.add_argument("--output", type=Path, default=Path("out/experiments/script_detection_experiments.json"))
    parser.add_argument("--markdown", type=Path, default=Path("experiments/AZOTH-SCRIPT-DETECTION.md"))
    parser.add_argument("--max-id", type=int, default=0)
    parser.add_argument("--max-per-label", type=int, default=16000)
    parser.add_argument("--hash-bits", type=int, default=19)
    parser.add_argument("--max-tokens", type=int, default=160)
    parser.add_argument("--max-combos", type=int, default=40000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper()), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args.max_id = args.max_id or data.snapshot_max_id(args.db)

    all_rows = _cap(_fetch_rows(args.db, POOLS[args.pool], args.max_id), args.max_per_label, args.seed)
    train_rows = [row for row in all_rows if not row.is_test]
    test_rows = [row for row in all_rows if row.is_test]
    LOG.info(
        "%s: train=%d (%d bad/%d good), test=%d (%d bad/%d good)",
        args.pool,
        len(train_rows),
        sum(r.label == 1 for r in train_rows),
        sum(r.label == 0 for r in train_rows),
        len(test_rows),
        sum(r.label == 1 for r in test_rows),
        sum(r.label == 0 for r in test_rows),
    )
    reports = _load_reports(args.db, all_rows)
    modes = [
        ("01_prod_hsn_d3_bigram_plain", FeatureMode("hsn_d3_bigram_plain", depth=3, crit_filter="hsn", n=2)),
        ("02_tiered_hsn_d2_4gram", FeatureMode("tiered_hsn_d2_4gram", depth=2, crit_filter="hsn", n=4, tiered=True)),
        ("03_script_only_vocab_unigram_bigram", FeatureMode("script_vocab_probe", depth=3, crit_filter="hsn", n=1, density=True)),
        ("04_hard_tail_weighted_hsn", FeatureMode("hard_tail_hsn", depth=3, crit_filter="hsn", n=2, density=True)),
        ("06_py_js_joint_hsn" if args.pool == "py_js" else "06_joint_style_hsn", FeatureMode("joint_hsn", depth=3, crit_filter="hsn", n=2, density=True)),
        ("07_density_plus_hsn", FeatureMode("density_hsn", depth=3, crit_filter="hsn", n=2, density=True)),
        ("08_trait_sequence_sketch", FeatureMode("sequence_hsn", depth=3, crit_filter="hsn", n=3, sequence=True, density=True)),
        ("09_benign_framework_suppression", FeatureMode("benign_framework", depth=3, crit_filter="hsn", n=2, density=True, benign_framework=True)),
    ]

    results: list[dict[str, Any]] = []
    base_result: dict[str, Any] | None = None
    base_probs: np.ndarray | None = None
    base_y: np.ndarray | None = None
    base_x_train: sp.csr_matrix | None = None
    base_x_test: sp.csr_matrix | None = None
    for name, mode in modes:
        weights = None
        if name.startswith("04_"):
            x_score_train, y_score_train = _score_table_features(args.score_table, train_rows)
            current = np.max(x_score_train, axis=1)
            weights = np.ones(len(y_score_train), dtype=np.float32)
            if np.any(y_score_train == 0):
                cut = np.quantile(current[y_score_train == 0], 0.995)
                weights[(y_score_train == 0) & (current >= cut)] = 12.0
            weights[(y_score_train == 1) & (current < 0.99)] = 8.0
        result, probs, y_test, x_train, x_test = _run_mode(name, mode, train_rows, test_rows, reports, args, weights=weights)
        results.append(result)
        LOG.info("%s ap=%.4f f1=%.4f r@1fp=%.2f%%", name, result["metrics"]["ap"] or 0.0, result["metrics"]["f1"], 100.0 * result["metrics"]["fp_counts"]["1"]["recall"])
        if name.startswith("01_"):
            base_result, base_probs, base_y, base_x_train, base_x_test = result, probs, y_test, x_train, x_test

    # 05: residual two-stage model over misses from the baseline hsn bigram model.
    if base_result is not None and base_probs is not None and base_y is not None and base_x_train is not None and base_x_test is not None:
        base_train_clf = _fit_classifier(base_x_train, np.asarray([r.label for r in train_rows], dtype=np.int8), None, args.seed + 101)
        train_base = base_train_clf.predict_proba(base_x_train)[:, 1]
        y_train = np.asarray([r.label for r in train_rows], dtype=np.int8)
        residual_weights = np.ones(len(y_train), dtype=np.float32) * 0.2
        residual_weights[(y_train == 1) & (train_base < 0.95)] = 15.0
        residual_weights[(y_train == 0) & (train_base >= 0.5)] = 10.0
        residual = _fit_classifier(base_x_train, y_train, residual_weights, args.seed + 202)
        residual_probs = residual.predict_proba(base_x_test)[:, 1]
        combined = np.maximum(base_probs, residual_probs)
        results.append(
            {
                "name": "05_two_stage_residual_or",
                "train_rows": len(train_rows),
                "train_malware": int(np.sum(y_train == 1)),
                "train_benign": int(np.sum(y_train == 0)),
                "test_rows": len(test_rows),
                "test_malware": int(np.sum(base_y == 1)),
                "test_benign": int(np.sum(base_y == 0)),
                "metrics": _metrics(base_y, combined),
            },
        )

    # 10: route score blender.
    x_score_train, y_score_train = _score_table_features(args.score_table, train_rows)
    x_score_test, y_score_test = _score_table_features(args.score_table, test_rows)
    blend = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=args.seed)
    blend.fit(x_score_train, y_score_train)
    blend_probs = blend.predict_proba(x_score_test)[:, 1]
    results.append(
        {
            "name": "10_score_blender_general_scripts_filetype",
            "train_rows": len(y_score_train),
            "train_malware": int(np.sum(y_score_train == 1)),
            "train_benign": int(np.sum(y_score_train == 0)),
            "test_rows": len(y_score_test),
            "test_malware": int(np.sum(y_score_test == 1)),
            "test_benign": int(np.sum(y_score_test == 0)),
            "metrics": _metrics(y_score_test, blend_probs),
        },
    )

    payload = _json_clean(
        {
            "timestamp": datetime.now(UTC).isoformat(),
            "db": args.db,
            "max_id": args.max_id,
            "pool": args.pool,
            "file_types": list(POOLS[args.pool]),
            "train_rows": len(train_rows),
            "test_rows": len(test_rows),
            "settings": vars(args),
            "results": results,
        },
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(payload, f, indent=2, allow_nan=False)
    _write_markdown(args.markdown, payload)
    print(f"wrote {args.output}")
    print(f"wrote {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
