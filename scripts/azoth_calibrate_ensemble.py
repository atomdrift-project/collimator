#!/usr/bin/env python3
"""Calibrate routed azoth ensemble thresholds against the full corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import scipy.sparse as sp

from collimator import data, features, model, thresholds

sys.path.insert(0, str(Path(__file__).resolve().parent))
from azoth_specialist_suite import DEPLOYMENT_GROUPS  # noqa: E402

LOG = logging.getLogger("azoth_calibrate_ensemble")


def _chunks(values: list[int], size: int) -> list[list[int]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_model_set(general_scores: Path, routes: list[dict[str, Any]]) -> str:
    h = hashlib.sha256()
    h.update(str(general_scores).encode())
    h.update(_file_sha256(general_scores).encode())
    for route in sorted(routes, key=lambda item: item["name"]):
        h.update(str(route["name"]).encode())
        output_dir = Path(route.get("output_dir", ""))
        for filename in ("model.txt", "feature_spec.json"):
            path = output_dir / filename
            if path.exists():
                h.update(filename.encode())
                h.update(_file_sha256(path).encode())
    return h.hexdigest()


def _label_int(label: str) -> int:
    return 1 if label == "bad" else 0


def _fetch_file_types(db_path: Path | str, row_ids: np.ndarray) -> dict[int, str]:
    ids = [int(row_id) for row_id in row_ids]
    out: dict[int, str] = {}
    with data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if data._is_pg(db_path):  # noqa: SLF001
            with conn.cursor() as cur:
                for chunk in _chunks(ids, 10_000):
                    cur.execute(
                        "SELECT id, COALESCE(NULLIF(file_type, ''), 'unknown') "
                        "FROM samples WHERE id = ANY(%s)",
                        [chunk],
                    )
                    out.update({int(row_id): str(file_type) for row_id, file_type in cur})
        else:
            for chunk in _chunks(ids, 10_000):
                placeholders = ",".join("?" for _ in chunk)
                query = (
                    "SELECT id, COALESCE(NULLIF(file_type, ''), 'unknown') "
                    f"FROM samples WHERE id IN ({placeholders})"
                )
                out.update(
                    {
                        int(row_id): str(file_type)
                        for row_id, file_type in conn.execute(query, chunk)
                    },
                )
    return out


def _fetch_rows(
    db_path: Path | str,
    *,
    file_types: list[str],
    max_id: int,
) -> list[tuple[int, int]]:
    marker = "%s" if data._is_pg(db_path) else "?"  # noqa: SLF001
    where = [
        "label IN ('bad', 'good')",
        "cleave_result IS NOT NULL",
        "skip = ''",
        f"id <= {marker}",
    ]
    params: list[Any] = [max_id]
    rows: list[tuple[int, int]] = []
    with data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if data._is_pg(db_path):  # noqa: SLF001
            where.append("file_type = ANY(%s)")
            params.append(file_types)
            query = "SELECT id, label FROM samples WHERE " + " AND ".join(where) + " ORDER BY id"
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = [(int(row_id), _label_int(str(label))) for row_id, label in cur]
        else:
            placeholders = ",".join("?" for _ in file_types)
            where.append(f"file_type IN ({placeholders})")
            params.extend(file_types)
            query = "SELECT id, label FROM samples WHERE " + " AND ".join(where) + " ORDER BY id"
            rows = [
                (int(row_id), _label_int(str(label)))
                for row_id, label in conn.execute(query, params)
            ]
    return rows


def _score_route(
    db_path: Path | str,
    route: dict[str, Any],
    *,
    row_index: dict[int, int],
    max_id: int,
    workers: int,
    refresh: bool,
) -> dict[str, Any]:
    output_dir = Path(route["output_dir"])
    cache_path = output_dir / "calibration_scores.npz"
    if cache_path.exists() and not refresh:
        cache = np.load(cache_path)
        return {
            "name": route["route"],
            "kind": route["kind"],
            "file_types": route["file_types"],
            "output_dir": str(output_dir),
            "indices": cache["indices"].astype(np.int64),
            "probs": cache["probs"].astype(np.float32),
        }

    rows_all = _fetch_rows(db_path, file_types=route["file_types"], max_id=max_id)
    rows = [(row_id, label) for row_id, label in rows_all if row_id in row_index]
    skipped = len(rows_all) - len(rows)
    if skipped:
        LOG.warning(
            "%s: skipped %d rows absent from general score cache",
            route["route"],
            skipped,
        )
    spec = features.FeatureSpec.load(output_dir / "feature_spec.json")
    clf = model.load_model(output_dir / "model.txt")
    batches = list(features.extract_labeled_from_db_batches(db_path, rows, spec, n_workers=workers))
    if batches:
        x_matrix = sp.vstack([batch[0] for batch in batches], format="csr")
    else:
        x_matrix = sp.csr_matrix((0, spec.total_features), dtype=np.float32)
    probs = model.predict_proba(clf, x_matrix)
    indices = np.asarray([row_index[row_id] for row_id, _label in rows], dtype=np.int64)
    np.savez_compressed(cache_path, indices=indices, probs=probs.astype(np.float32))
    return {
        "name": route["route"],
        "kind": route["kind"],
        "file_types": route["file_types"],
        "output_dir": str(output_dir),
        "indices": indices,
        "probs": probs.astype(np.float32),
    }


def _budget(n_benign: int, target_per_million: float) -> int:
    if target_per_million <= 0:
        return 0
    return min(n_benign, max(1, int(math.floor(n_benign * target_per_million / 1_000_000))))


def _candidate_thresholds(
    labels: np.ndarray,
    indices: np.ndarray,
    probs: np.ndarray,
    *,
    max_fp: int,
) -> list[dict[str, float | int | None]]:
    candidates: list[dict[str, float | int | None]] = [{"threshold": None, "fp": 0, "tp": 0}]
    if len(indices) == 0:
        return candidates
    y = labels[indices]
    order = np.argsort(-probs, kind="mergesort")
    sorted_p = probs[order]
    sorted_y = y[order]
    tp_cum = np.cumsum(sorted_y == 1)
    fp_cum = np.cumsum(sorted_y == 0)
    best_by_fp: dict[int, dict[str, float | int]] = {}
    pos = 0
    while pos < len(sorted_p):
        threshold = sorted_p[pos]
        end = pos
        while end + 1 < len(sorted_p) and sorted_p[end + 1] == threshold:
            end += 1
        fp = int(fp_cum[end])
        if fp > max_fp:
            break
        tp = int(tp_cum[end])
        old = best_by_fp.get(fp)
        if old is None or int(old["tp"]) <= tp:
            best_by_fp[fp] = {"threshold": float(threshold), "fp": fp, "tp": tp}
        pos = end + 1
    candidates.extend(best_by_fp[fp] for fp in sorted(best_by_fp))
    return candidates


def _hit_mask(
    n_rows: int,
    indices: np.ndarray,
    probs: np.ndarray,
    threshold: float | None,
) -> np.ndarray:
    hit = np.zeros(n_rows, dtype=bool)
    if threshold is None:
        return hit
    hit[indices[probs >= threshold]] = True
    return hit


def _calibrate_one(
    labels: np.ndarray,
    route_scores: list[dict[str, Any]],
    *,
    target_per_million: float,
) -> dict[str, Any]:
    n_rows = len(labels)
    benign = labels == 0
    malware = labels == 1
    n_benign = int(np.sum(benign))
    n_malware = int(np.sum(malware))
    max_fp = _budget(n_benign, target_per_million)
    selected: dict[str, float | None] = {route["name"]: None for route in route_scores}
    candidates = {
        route["name"]: _candidate_thresholds(
            labels,
            route["indices"],
            route["probs"],
            max_fp=max_fp,
        )
        for route in route_scores
    }
    by_name = {route["name"]: route for route in route_scores}
    selected_hits: dict[str, np.ndarray] = {
        route["name"]: np.zeros(n_rows, dtype=bool)
        for route in route_scores
    }

    general_candidates = candidates.get("general", [{"threshold": None, "tp": 0, "fp": 0}])
    general_best = max(general_candidates, key=lambda item: int(item["tp"] or 0))
    if general_best["threshold"] is not None:
        selected["general"] = float(general_best["threshold"])
        general = by_name["general"]
        selected_hits["general"] = _hit_mask(
            n_rows,
            general["indices"],
            general["probs"],
            selected["general"],
        )

    hit_counts = np.zeros(n_rows, dtype=np.uint16)
    for hit in selected_hits.values():
        hit_counts += hit
    current_fp = int(np.sum((hit_counts > 0) & benign))
    current_tp = int(np.sum((hit_counts > 0) & malware))

    while True:
        best: tuple[int, int, str, float | None, np.ndarray, np.ndarray] | None = None
        for name, route_candidates in candidates.items():
            route = by_name[name]
            old_hit = selected_hits[name]
            for candidate in route_candidates:
                threshold = candidate["threshold"]
                new_hit = _hit_mask(
                    n_rows,
                    route["indices"],
                    route["probs"],
                    None if threshold is None else float(threshold),
                )
                proposed_counts = hit_counts - old_hit + new_hit
                proposed_hit = proposed_counts > 0
                fp = int(np.sum(proposed_hit & benign))
                if fp > max_fp:
                    continue
                tp = int(np.sum(proposed_hit & malware))
                inc_fp = fp - current_fp
                inc_tp = tp - current_tp
                if inc_tp <= 0:
                    continue
                key = (
                    inc_tp,
                    -max(inc_fp, 0),
                    name,
                    None if threshold is None else float(threshold),
                    new_hit,
                    proposed_counts,
                )
                if best is None or key[:2] > best[:2]:
                    best = key
        if best is None:
            break
        _inc_tp, _neg_inc_fp, name, threshold, new_hit, proposed_counts = best
        selected[name] = threshold
        selected_hits[name] = new_hit
        hit_counts = proposed_counts
        current_fp = int(np.sum((hit_counts > 0) & benign))
        current_tp = int(np.sum((hit_counts > 0) & malware))

    diagnostics: dict[str, Any] = {}
    for name, route in by_name.items():
        route_candidates = candidates[name]
        standalone = max(
            route_candidates,
            key=lambda item: (int(item["tp"] or 0), -int(item["fp"] or 0)),
        )
        old_hit = selected_hits[name]
        best_marginal: dict[str, Any] | None = None
        for candidate in route_candidates:
            threshold = candidate["threshold"]
            new_hit = _hit_mask(
                n_rows,
                route["indices"],
                route["probs"],
                None if threshold is None else float(threshold),
            )
            proposed_counts = hit_counts - old_hit + new_hit
            proposed_hit = proposed_counts > 0
            fp = int(np.sum(proposed_hit & benign))
            if fp > max_fp:
                continue
            tp = int(np.sum(proposed_hit & malware))
            inc_fp = fp - current_fp
            inc_tp = tp - current_tp
            item = {
                "threshold": None if threshold is None else float(threshold),
                "inc_tp": inc_tp,
                "inc_fp": inc_fp,
                "tp": tp,
                "fp": fp,
            }
            if best_marginal is None or (inc_tp, -max(inc_fp, 0)) > (
                int(best_marginal["inc_tp"]),
                -max(int(best_marginal["inc_fp"]), 0),
            ):
                best_marginal = item
        diagnostics[name] = {
            "kind": route.get("kind"),
            "rows": int(len(route["indices"])),
            "selected": selected[name] is not None,
            "selected_threshold": selected[name],
            "standalone": {
                "threshold": standalone["threshold"],
                "tp": int(standalone["tp"] or 0),
                "fp": int(standalone["fp"] or 0),
            },
            "best_marginal": best_marginal
            or {"threshold": None, "inc_tp": 0, "inc_fp": 0, "tp": current_tp, "fp": current_fp},
        }

    return {
        "target_per_million": float(target_per_million),
        "budget": max_fp,
        "thresholds": {name: thr for name, thr in selected.items() if thr is not None},
        "diagnostics": diagnostics,
        "tp": current_tp,
        "fp": current_fp,
        "tn": n_benign - current_fp,
        "fn": n_malware - current_tp,
        "recall": float(current_tp / n_malware) if n_malware else math.nan,
        "precision": float(current_tp / max(current_tp + current_fp, 1)),
        "fp_per_million": float(current_fp * 1_000_000.0 / n_benign) if n_benign else math.nan,
    }


def _load_routes(summary_path: Path) -> list[dict[str, Any]]:
    with open(summary_path) as f:
        summary = json.load(f)
    routes: list[dict[str, Any]] = []
    for item in summary["results"]:
        if item.get("error") or item.get("kind") not in {"filegroup", "filetype"}:
            continue
        route = (
            f"filegroups/{item['name']}"
            if item["kind"] == "filegroup"
            else f"filetypes/{item['name']}"
        )
        routes.append({**item, "route": route})
    return routes


def _filetype_to_group() -> dict[str, str]:
    out: dict[str, str] = {}
    for group, file_types in DEPLOYMENT_GROUPS.items():
        for file_type in file_types:
            out[file_type] = group
    return out


def _write_score_table(
    path: Path,
    *,
    row_ids: np.ndarray,
    labels: np.ndarray,
    file_types: np.ndarray,
    file_groups: np.ndarray,
    route_scores: list[dict[str, Any]],
) -> str:
    names = np.asarray([route["name"] for route in route_scores])
    kinds = np.asarray([route["kind"] for route in route_scores])
    scores = np.full((len(route_scores), len(row_ids)), np.nan, dtype=np.float32)
    for idx, route in enumerate(route_scores):
        scores[idx, route["indices"]] = route["probs"]
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        row_ids=row_ids,
        labels=labels,
        file_types=file_types,
        file_groups=file_groups,
        route_names=names,
        route_kinds=kinds,
        scores=scores,
    )
    return _file_sha256(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--azoth-root", type=Path, default=Path("out/models/azoth"))
    parser.add_argument("--summary", type=Path, default=Path("out/models/azoth/specialists.json"))
    parser.add_argument("--general-scores", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("out/models/azoth/config.json"))
    parser.add_argument(
        "--score-table",
        type=Path,
        default=Path("out/models/azoth/score_table.npz"),
    )
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    general_cache = np.load(args.general_scores)
    row_ids = general_cache["row_ids"].astype(np.int64)
    labels = general_cache["labels"].astype(np.int8)
    general_probs = general_cache["probs"].astype(np.float32)
    max_id = int(general_cache["corpus_requested_max_id"])
    if max_id <= 0:
        max_id = int(general_cache["corpus_max_row_id"])
    row_index = {int(row_id): idx for idx, row_id in enumerate(row_ids)}

    file_types_by_row = _fetch_file_types(args.db, row_ids)
    filetype_to_group = _filetype_to_group()
    file_types = np.asarray(
        [file_types_by_row.get(int(row_id), "unknown") for row_id in row_ids],
    )
    file_groups = np.asarray([filetype_to_group.get(file_type, "") for file_type in file_types])
    route_scores = [
        {
            "name": "general",
            "kind": "general",
            "file_types": [],
            "output_dir": str(args.azoth_root / "general"),
            "indices": np.arange(len(row_ids), dtype=np.int64),
            "probs": general_probs,
        },
    ]
    for route in _load_routes(args.summary):
        LOG.info("scoring %s", route["route"])
        route_scores.append(
            _score_route(
                args.db,
                route,
                row_index=row_index,
                max_id=max_id,
                workers=args.workers,
                refresh=args.refresh,
            ),
        )

    score_table_hash = _write_score_table(
        args.score_table,
        row_ids=row_ids,
        labels=labels,
        file_types=file_types,
        file_groups=file_groups,
        route_scores=route_scores,
    )
    model_set_hash = _hash_model_set(args.general_scores, route_scores)
    levels: list[dict[str, Any]] = []
    for target in thresholds.SEVERITY_LEVEL_TARGETS:
        level = int(target["level"])
        hostile = _calibrate_one(
            labels,
            route_scores,
            target_per_million=float(target["hostile_per_million"]),
        )
        suspicious = _calibrate_one(
            labels,
            route_scores,
            target_per_million=float(target["suspicious_per_million"]),
        )
        LOG.info(
            "L%d hostile recall=%.2f%% fp=%d; suspicious recall=%.2f%% fp=%d",
            level,
            hostile["recall"] * 100,
            hostile["fp"],
            suspicious["recall"] * 100,
            suspicious["fp"],
        )
        levels.append({"level": level, "hostile": hostile, "suspicious": suspicious})

    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "schema": "azoth.routed_ensemble.v1",
        "max_id": max_id,
        "calibration_snapshot_id": max_id,
        "score_table": str(args.score_table),
        "score_table_hash": score_table_hash,
        "model_set_hash": model_set_hash,
        "search": {
            "method": "coordinate_descent_v1",
            "start": "best_general_only",
            "objective": "maximize_recall_under_routed_fp_budget",
        },
        "rows": int(len(labels)),
        "malware": int(np.sum(labels == 1)),
        "benign": int(np.sum(labels == 0)),
        "root": str(args.azoth_root),
        "filetype_to_group": filetype_to_group,
        "observed_filetypes": {
            file_type: sum(1 for ft in file_types_by_row.values() if ft == file_type)
            for file_type in sorted(set(file_types_by_row.values()))
        },
        "models": [
            {
                "route": route["name"],
                "kind": route["kind"],
                "rows": int(len(route["indices"])),
            }
            for route in route_scores
        ],
        "levels": levels,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
