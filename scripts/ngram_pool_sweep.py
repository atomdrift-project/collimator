#!/usr/bin/env python3
"""Screen trait n-gram designs on small filetype pools.

This is intentionally not the production feature pipeline. It is a cheap
research harness for answering questions like:

  * should paths be full-depth or collapsed to 1/2/3 levels?
  * should n-grams use hostile only, suspicious+hostile, or notable+?
  * do larger combinations, up to 8-way, carry useful signal?

The features are hashed so we can try many variants without rebuilding a large
vocabulary for each one.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import logging
import math
import random
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import scipy.sparse as sp
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score

from collimator import data
from collimator.features import MIN_CONFIDENCE, _coerce_report, _finding_paths, _float, report_files  # noqa: PLC2701
from collimator.model import create_classifier, predict_proba

LOG = logging.getLogger("ngram_pool_sweep")

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
    "portable": ("dex", "java_class", "pyc", "wasm"),
    "documents": ("doc", "docx", "html", "ole", "pdf", "ppt", "pptx", "rtf", "xls", "xlsx"),
    "source": ("c", "cpp", "csharp", "go", "java", "kotlin", "makefile", "rust", "scala", "swift"),
    "config": ("ini", "json", "package.json", "plist", "toml", "xml", "yaml", "yml"),
    "media": ("bmp", "gif", "jpg", "jpeg", "mp3", "mp4", "png", "svg", "webp"),
}


@dataclass(frozen=True)
class Pool:
    name: str
    filetypes: tuple[str, ...]


@dataclass(frozen=True)
class Variant:
    pool: str
    depth: int
    crit_filter: str
    n: int
    severity_prefix: bool

    @property
    def name(self) -> str:
        depth = "full" if self.depth == 0 else f"d{self.depth}"
        prefix = "tiered" if self.severity_prefix else "plain"
        return f"{self.pool}-{depth}-{self.crit_filter}-{self.n}gram-{prefix}"


def _placeholder(db_path: str) -> str:
    return "%s" if data._is_pg(db_path) else "?"  # noqa: SLF001


def _label_int(label: str) -> int:
    return 1 if label == "bad" else 0


def _fetch_rows(db_path: str, pool: Pool, max_id: int) -> list[dict[str, Any]]:
    marker = _placeholder(db_path)
    where = [
        "label IN ('bad', 'good')",
        "cleave_result IS NOT NULL",
        "skip = ''",
    ]
    params: list[Any] = []
    if data._is_pg(db_path):  # noqa: SLF001
        where.append(f"COALESCE(NULLIF(file_type, ''), 'unknown') = ANY({marker})")
        params.append(list(pool.filetypes))
    else:
        placeholders = ",".join(marker for _ in pool.filetypes)
        where.append(f"COALESCE(NULLIF(file_type, ''), 'unknown') IN ({placeholders})")
        params.extend(pool.filetypes)
    if max_id:
        where.append(f"id <= {marker}")
        params.append(max_id)
    query = (
        "SELECT id, sha256, canonical_sha256, label, score "
        "FROM samples WHERE "
        + " AND ".join(where)
        + " ORDER BY id"
    )
    rows: list[dict[str, Any]] = []
    with data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        for row_id, sha256, canonical, label, score in data._execute(conn, query, params):  # noqa: SLF001
            split_key = canonical or sha256
            rows.append(
                {
                    "id": int(row_id),
                    "label": _label_int(str(label)),
                    "is_test": data.is_test_sample(str(split_key)),
                    "score": float(score or 0.0),
                },
            )
    return rows


def _cap_rows(rows: list[dict[str, Any]], *, per_label: int, seed: int) -> list[dict[str, Any]]:
    if per_label <= 0:
        return rows
    rng = random.Random(seed)
    out: list[dict[str, Any]] = []
    for is_test in (False, True):
        for label in (0, 1):
            bucket = [r for r in rows if r["is_test"] == is_test and r["label"] == label]
            rng.shuffle(bucket)
            out.extend(bucket[:per_label])
    return sorted(out, key=lambda r: r["id"])


def _load_reports(db_path: str, rows: list[dict[str, Any]], batch_size: int = 2000) -> dict[int, dict[str, Any]]:
    reports: dict[int, dict[str, Any]] = {}
    ids = [r["id"] for r in rows]
    for start in range(0, len(ids), batch_size):
        chunk = ids[start : start + batch_size]
        fetched = data.fetch_cleave_results(db_path, chunk)
        for rid, item in fetched.items():
            report = _coerce_report(item.get("cleave_result"))
            if report is not None:
                reports[int(rid)] = report
        LOG.info("fetched reports %d/%d", min(start + batch_size, len(ids)), len(ids))
    return reports


def _passes_filter(crit: int, crit_filter: str) -> bool:
    if crit_filter == "h":
        return crit >= 5
    if crit_filter == "s":
        return crit == 4
    if crit_filter == "n":
        return crit == 3
    if crit_filter == "hs":
        return crit >= 4
    if crit_filter == "hsn":
        return crit >= 3
    raise ValueError(f"unknown criticality filter: {crit_filter}")


def _tier(crit: int) -> str:
    if crit >= 5:
        return "h"
    if crit == 4:
        return "s"
    return "n"


def _truncate_path(path: str, depth: int) -> str:
    if depth <= 0:
        return path
    return "/".join(path.split("/")[:depth])


def _tokens(report: dict[str, Any], *, depth: int, crit_filter: str, severity_prefix: bool) -> list[str]:
    toks: set[str] = set()
    for file_entry in report_files(report):
        for finding in file_entry.get("ts") or []:
            fid = finding.get("i", "")
            if not fid or _float(finding.get("c", 1.0)) < MIN_CONFIDENCE:
                continue
            crit = int(finding.get("l", 0) or 0)
            if not _passes_filter(crit, crit_filter):
                continue
            for path in _finding_paths(fid):
                p = _truncate_path(path, depth)
                toks.add(f"{_tier(crit)}:{p}" if severity_prefix else p)
    return sorted(toks)


def _hash_feature(text: str, hash_bits: int) -> int:
    digest = hashlib.blake2b(text.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "little") & ((1 << hash_bits) - 1)


def _limited_combinations(tokens: list[str], n: int, max_combos: int) -> Iterable[tuple[str, ...]]:
    count = 0
    for combo in itertools.combinations(tokens, n):
        yield combo
        count += 1
        if count >= max_combos:
            return


def _matrix(
    rows: list[dict[str, Any]],
    reports: dict[int, dict[str, Any]],
    variant: Variant,
    *,
    hash_bits: int,
    max_tokens: int,
    max_combos: int,
) -> tuple[sp.csr_matrix, np.ndarray]:
    dim = 1 << hash_bits
    indptr = [0]
    indices: list[int] = []
    values: list[float] = []
    labels: list[int] = []
    for row in rows:
        report = reports.get(row["id"])
        toks = _tokens(
            report or {},
            depth=variant.depth,
            crit_filter=variant.crit_filter,
            severity_prefix=variant.severity_prefix,
        )
        if len(toks) > max_tokens:
            toks = toks[:max_tokens]
        feats: dict[int, float] = {}
        if len(toks) >= variant.n:
            for combo in _limited_combinations(toks, variant.n, max_combos):
                idx = _hash_feature("\x1f".join(combo), hash_bits)
                feats[idx] = 1.0
        # Three stable dense-ish context features appended after the hash space.
        feats[dim] = math.log1p(max(row["score"], 0.0))
        feats[dim + 1] = math.log1p(len(toks))
        feats[dim + 2] = 1.0 if not toks else 0.0
        for idx in sorted(feats):
            indices.append(idx)
            values.append(feats[idx])
        indptr.append(len(indices))
        labels.append(int(row["label"]))
    x = sp.csr_matrix((values, indices, indptr), shape=(len(rows), dim + 3), dtype=np.float32)
    return x, np.asarray(labels, dtype=np.int8)


def _metric_at_fp_budget(y: np.ndarray, probs: np.ndarray, budget_per_million: int) -> dict[str, Any]:
    benign = int(np.sum(y == 0))
    malware = int(np.sum(y == 1))
    allowed_fp = int(math.floor((budget_per_million / 1_000_000.0) * benign))
    order = np.argsort(-probs)
    tp = 0
    fp = 0
    best: dict[str, Any] | None = None
    for idx in order:
        if y[idx] == 1:
            tp += 1
        else:
            fp += 1
        if fp <= allowed_fp:
            best = {
                "threshold": float(probs[idx]),
                "tp": int(tp),
                "fp": int(fp),
                "recall": float(tp / malware) if malware else None,
                "fp_per_million": float(fp / benign * 1_000_000.0) if benign else None,
            }
        elif fp > allowed_fp:
            break
    if best is None:
        return {
            "threshold": None,
            "tp": 0,
            "fp": 0,
            "recall": 0.0 if malware else None,
            "fp_per_million": 0.0 if benign else None,
        }
    return best


def _metrics(y: np.ndarray, probs: np.ndarray) -> dict[str, Any]:
    pred = probs >= 0.5
    out = {
        "auc": float(roc_auc_score(y, probs)) if len(np.unique(y)) == 2 else None,
        "ap": float(average_precision_score(y, probs)) if len(np.unique(y)) == 2 else None,
        "f1": float(f1_score(y, pred, zero_division=0)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "fp_budgets": {},
    }
    for budget in (0, 1, 5, 10, 50, 100, 500, 1000, 5000):
        out["fp_budgets"][str(budget)] = _metric_at_fp_budget(y, probs, budget)
    return out


def _run_variant(
    variant: Variant,
    train_rows: list[dict[str, Any]],
    test_rows: list[dict[str, Any]],
    reports: dict[int, dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    x_train, y_train = _matrix(
        train_rows,
        reports,
        variant,
        hash_bits=args.hash_bits,
        max_tokens=args.max_tokens,
        max_combos=args.max_combos,
    )
    x_test, y_test = _matrix(
        test_rows,
        reports,
        variant,
        hash_bits=args.hash_bits,
        max_tokens=args.max_tokens,
        max_combos=args.max_combos,
    )
    clf = create_classifier(
        int(np.sum(y_train == 0)),
        int(np.sum(y_train == 1)),
        learner="azoth",
        device=args.device,
        random_state=args.seed,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        learning_rate=args.learning_rate,
        min_child_samples=args.min_child_samples,
        num_leaves=args.num_leaves,
    )
    clf.fit(x_train, y_train)
    probs = predict_proba(clf, x_test)
    payload = {
        **asdict(variant),
        "name": variant.name,
        "train_rows": int(len(y_train)),
        "train_malware": int(np.sum(y_train == 1)),
        "train_benign": int(np.sum(y_train == 0)),
        "test_rows": int(len(y_test)),
        "test_malware": int(np.sum(y_test == 1)),
        "test_benign": int(np.sum(y_test == 0)),
        "metrics": _metrics(y_test, probs),
    }
    LOG.info(
        "%s auc=%.4f ap=%.4f f1=%.4f r@5fp/M=%.2f%% r@1000fp/M=%.2f%%",
        variant.name,
        payload["metrics"]["auc"] or 0.0,
        payload["metrics"]["ap"] or 0.0,
        payload["metrics"]["f1"],
        100.0 * (payload["metrics"]["fp_budgets"]["5"]["recall"] or 0.0),
        100.0 * (payload["metrics"]["fp_budgets"]["1000"]["recall"] or 0.0),
    )
    return payload


def _score_only(pool: str, train_rows: list[dict[str, Any]], test_rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    del train_rows, args
    y = np.asarray([r["label"] for r in test_rows], dtype=np.int8)
    score = np.asarray([math.log1p(max(r["score"], 0.0)) for r in test_rows], dtype=np.float32)
    if score.max() > score.min():
        probs = (score - score.min()) / (score.max() - score.min())
    else:
        probs = np.zeros_like(score)
    return {
        "name": f"{pool}-score-only",
        "pool": pool,
        "baseline": "score_only",
        "test_rows": int(len(y)),
        "test_malware": int(np.sum(y == 1)),
        "test_benign": int(np.sum(y == 0)),
        "metrics": _metrics(y, probs),
    }


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    rows = payload["results"]
    lines = [
        "# Azoth N-Gram Pool Sweep",
        "",
        f"- Timestamp: `{payload['timestamp']}`",
        f"- Pools: `{', '.join(payload['pools'])}`",
        f"- Depths: `{payload['depths']}`",
        f"- Criticality filters: `{payload['crit_filters']}`",
        f"- N sizes: `{payload['n_values']}`",
        f"- Severity-prefix modes: `{payload['severity_prefix']}`",
        "",
        "Criticality filters: `h` = hostile, `s` = suspicious exact, `n` = notable exact, `hs` = suspicious+hostile, `hsn` = notable+suspicious+hostile.",
        "",
    ]
    for pool in payload["pools"]:
        subset = [r for r in rows if r.get("pool") == pool]
        subset.sort(
            key=lambda r: (
                r["metrics"].get("ap") or -1.0,
                r["metrics"].get("auc") or -1.0,
                r["metrics"].get("f1") or -1.0,
            ),
            reverse=True,
        )
        lines.extend([
            f"## {pool}",
            "",
            "| Rank | Variant | AUC | AP | F1 | R@0FP/M | R@5FP/M | R@50FP/M | R@1000FP/M | Test bad/good |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for rank, row in enumerate(subset[:20], 1):
            m = row["metrics"]
            r0 = m["fp_budgets"]["0"]["recall"]
            r5 = m["fp_budgets"]["5"]["recall"]
            r50 = m["fp_budgets"]["50"]["recall"]
            r1000 = m["fp_budgets"]["1000"]["recall"]
            lines.append(
                f"| {rank} | `{row['name']}` | "
                f"{(m.get('auc') or 0.0):.4f} | {(m.get('ap') or 0.0):.4f} | {m['f1']:.4f} | "
                f"{100.0 * (r0 or 0.0):.2f}% | {100.0 * (r5 or 0.0):.2f}% | "
                f"{100.0 * (r50 or 0.0):.2f}% | {100.0 * (r1000 or 0.0):.2f}% | "
                f"{row.get('test_malware', 0)}/{row.get('test_benign', 0)} |"
            )
        lines.append("")
    path.write_text("\n".join(lines) + "\n")


def _parse_csv_ints(raw: str) -> list[int]:
    return [int(part) for part in raw.split(",") if part.strip()]


def _parse_csv_strs(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def _parse_pools(raw: str) -> list[Pool]:
    pools: list[Pool] = []
    for part in _parse_csv_strs(raw):
        if "=" in part:
            name, filetypes_raw = part.split("=", 1)
            pools.append(Pool(name.strip(), tuple(_parse_csv_strs(filetypes_raw))))
        elif part in DEPLOYMENT_GROUPS:
            pools.append(Pool(part, DEPLOYMENT_GROUPS[part]))
        else:
            pools.append(Pool(part, (part,)))
    return pools


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument(
        "--pools",
        default="python,javascript",
        help="Comma-separated filetypes, deployment groups, or name=ft1|ft2 style pools.",
    )
    parser.add_argument("--depths", default="1,2,3,0")
    parser.add_argument("--crit-filters", default="h,s,n,hs,hsn")
    parser.add_argument("--n-values", default="2,3,4,5,6,7,8")
    parser.add_argument("--severity-prefix", choices=("plain", "tiered", "both"), default="both")
    parser.add_argument("--output", type=Path, default=Path("out/experiments/ngram_pool_sweep.json"))
    parser.add_argument("--markdown", type=Path, default=Path("experiments/AZOTH-NGRAMS.md"))
    parser.add_argument("--max-id", type=int, default=0)
    parser.add_argument("--max-per-label", type=int, default=8000)
    parser.add_argument("--hash-bits", type=int, default=18)
    parser.add_argument("--max-tokens", type=int, default=96)
    parser.add_argument("--max-combos", type=int, default=20000)
    parser.add_argument("--n-estimators", type=int, default=180)
    parser.add_argument("--max-depth", type=int, default=10)
    parser.add_argument("--learning-rate", type=float, default=0.06)
    parser.add_argument("--num-leaves", type=int, default=64)
    parser.add_argument("--min-child-samples", type=int, default=80)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit-variants", type=int, default=0)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args.max_id = args.max_id or data.snapshot_max_id(args.db)
    pools = _parse_pools(args.pools)
    depths = _parse_csv_ints(args.depths)
    crit_filters = _parse_csv_strs(args.crit_filters)
    n_values = _parse_csv_ints(args.n_values)
    prefix_modes = [False, True] if args.severity_prefix == "both" else [args.severity_prefix == "tiered"]

    results: list[dict[str, Any]] = []
    for pool in pools:
        rows = _fetch_rows(args.db, pool, args.max_id)
        rows = _cap_rows(rows, per_label=args.max_per_label, seed=args.seed)
        train_rows = [r for r in rows if not r["is_test"]]
        test_rows = [r for r in rows if r["is_test"]]
        LOG.info(
            "%s: train=%d (%d bad/%d good), test=%d (%d bad/%d good)",
            pool.name,
            len(train_rows),
            sum(r["label"] == 1 for r in train_rows),
            sum(r["label"] == 0 for r in train_rows),
            len(test_rows),
            sum(r["label"] == 1 for r in test_rows),
            sum(r["label"] == 0 for r in test_rows),
        )
        reports = _load_reports(args.db, rows)
        results.append(_score_only(pool.name, train_rows, test_rows, args))
        variants = [
            Variant(pool.name, depth, crit_filter, n, severity_prefix)
            for depth in depths
            for crit_filter in crit_filters
            for n in n_values
            for severity_prefix in prefix_modes
        ]
        if args.limit_variants:
            variants = variants[: args.limit_variants]
        for variant in variants:
            results.append(_run_variant(variant, train_rows, test_rows, reports, args))

    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "db": args.db,
        "max_id": args.max_id,
        "pools": [pool.name for pool in pools],
        "pool_filetypes": {pool.name: list(pool.filetypes) for pool in pools},
        "depths": depths,
        "crit_filters": crit_filters,
        "n_values": n_values,
        "severity_prefix": args.severity_prefix,
        "settings": {
            "max_per_label": args.max_per_label,
            "hash_bits": args.hash_bits,
            "max_tokens": args.max_tokens,
            "max_combos": args.max_combos,
            "n_estimators": args.n_estimators,
            "max_depth": args.max_depth,
            "learning_rate": args.learning_rate,
            "num_leaves": args.num_leaves,
            "min_child_samples": args.min_child_samples,
        },
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(payload, f, indent=2, allow_nan=False)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    _write_markdown(args.markdown, payload)
    print(f"wrote {args.output}")
    print(f"wrote {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
