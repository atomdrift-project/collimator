#!/usr/bin/env python3
"""Capture route scoring inputs once, then compare pools without live DB reads.

Uses existing fold/production bundles and selected OOF rows. It never retrains
or modifies those bundles. Each replay writes to a fresh output directory.
"""
from __future__ import annotations

import argparse
from contextlib import nullcontext
import hashlib
import json
import logging
import os
from pathlib import Path
import resource
import sqlite3
import subprocess
import sys
import time

import numpy as np

from collimator import data, features
import azoth_oof_score_routes as scoring


def model_manifest(roots, routes):
    files = {}
    for root in roots.values():
        for route in routes:
            for path in sorted((root / route).rglob("*")):
                if path.is_file() and path.suffix in (".onnx", ".txt", ".json"):
                    files[str(path.resolve())] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def file_digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def capture(args):
    args.capture.mkdir(parents=True, exist_ok=False)
    routes = {}
    all_ids = set()
    roots = {"0": args.run / "models/azoth.oof-fold-a",
             "1": args.run / "models/azoth.oof-fold-b", "test": args.run / "models/azoth"}
    for path in sorted((roots["test"] / "oof_route_scores").glob("*/*/threshold_scores.npz")):
        route = path.parent.relative_to(roots["test"] / "oof_route_scores").as_posix()
        if args.only and route not in args.only:
            continue
        if any(not (root / route / "feature_spec.json").is_file() for root in roots.values()):
            continue
        with np.load(path) as scores:
            arrays = {key: scores[key] for key in
                      ("row_ids", "sha256", "scores", "labels", "canonical_shas")}
            count = len(arrays["row_ids"])
            selected = np.linspace(0, count - 1, min(count, args.rows_per_route), dtype=int)
            rows = [(int(arrays["row_ids"][i]), str(arrays["sha256"][i]), "",
                     int(arrays["scores"][i]), int(arrays["labels"][i]),
                     str(arrays["canonical_shas"][i])) for i in selected]
        routes[route] = rows
        all_ids.update(row[0] for row in rows)
    if not routes:
        raise ValueError("no scored routes with all three model bundles")
    ids = sorted(all_ids)
    with sqlite3.connect(args.capture / "reports.sqlite") as db:
        db.execute("CREATE TABLE samples (id INTEGER PRIMARY KEY, cleave_result TEXT, "
                   "formula TEXT, elements TEXT, score INTEGER, mtime TEXT)")
        for start in range(0, len(ids), 128):
            requested = ids[start:start + 128]
            reports = data.fetch_cleave_results(args.db, requested)
            missing = set(requested) - set(reports)
            if missing:
                raise ValueError(f"capture lost {len(missing)} selected rows; choose a fresh cohort")
            db.executemany("INSERT INTO samples VALUES (?,?,?,?,?,?)", [
                (rid, json.dumps(item["cleave_result"]) if isinstance(item["cleave_result"], dict)
                 else item["cleave_result"], item.get("formula", ""), item.get("elements", ""),
                 item.get("score", 0), item.get("mtime", "")) for rid, item in reports.items()
            ])
            db.commit()
            if start % 1024 == 0:
                print(f"captured {start + len(requested)}/{len(ids)} unique reports", flush=True)
    (args.capture / "manifest.json").write_text(json.dumps(
        dict(roots={key: str(path.resolve()) for key, path in roots.items()}, routes=routes,
             models=model_manifest(roots, routes), unique_rows=len(ids),
             database_sha256=file_digest(args.capture / "reports.sqlite")), indent=2) + "\n")
    print(f"capture complete: {len(ids)} unique reports, {len(routes)} routes", flush=True)


def replay(args):
    manifest = json.loads((args.capture / "manifest.json").read_text())
    roots = {key: Path(path) for key, path in manifest["roots"].items()}
    if model_manifest(roots, manifest["routes"]) != manifest["models"]:
        raise ValueError("model inputs changed after capture")
    if file_digest(args.capture / "reports.sqlite") != manifest["database_sha256"]:
        raise ValueError("captured reports changed")
    args.output.mkdir(parents=True, exist_ok=False)
    os.environ["COLLIMATOR_TIMING_DIR"] = str(args.output / "timings")
    started = time.monotonic()
    manager = (features.MetadataExtractionPool(args.workers)
               if args.mode == "persistent" else nullcontext(None))
    with manager as pool:
        for route, rows in manifest["routes"].items():
            route_started = time.monotonic()
            folds = scoring._split_by_fold(rows)
            parts = [scoring._score_rows(args.capture / "reports.sqlite", selected,
                                        roots[key] / route, workers=args.workers, worker_pool=pool)
                     for key, selected in zip(("0", "1", "test"), folds) if selected]
            combined = scoring._combine(parts)
            scoring._write_route(args.output / route / "threshold_scores.npz", combined,
                                 max_id_requested=0)
            print(f"{route}: {len(combined['row_ids'])} rows in "
                  f"{time.monotonic() - route_started:.2f}s", flush=True)
    result = dict(mode=args.mode, workers=args.workers, wall_seconds=time.monotonic() - started,
                  routes=len(manifest["routes"]), unique_rows=manifest["unique_rows"],
                  parent_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    (args.output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


def compare(args):
    args.output.mkdir(parents=True, exist_ok=False)
    for mode in ("route", "persistent"):
        subprocess.run([sys.executable, __file__, "replay", "--capture", str(args.capture),
                        "--output", str(args.output / mode), "--mode", mode,
                        "--workers", str(args.workers)], check=True)
    checked = rows = 0
    for path in sorted((args.output / "route").glob("*/*/threshold_scores.npz")):
        other = args.output / "persistent" / path.relative_to(args.output / "route")
        with np.load(path) as a, np.load(other) as b:
            assert set(a.files) == set(b.files), f"schema mismatch: {path}"
            for key in a.files:
                if not np.array_equal(a[key], b[key]):
                    raise ValueError(f"scoring parity failed: {path.parent} / {key}")
            rows += len(a["row_ids"])
        checked += 1
    if not checked:
        raise ValueError("no outputs compared")
    results = {mode: json.loads((args.output / mode / "result.json").read_text())
               for mode in ("route", "persistent")}
    results.update(exact_parity=True, routes_compared=checked, scores_compared=rows)
    (args.output / "comparison.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("capture", "replay", "compare"))
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--db")
    parser.add_argument("--rows-per-route", type=int, default=2048)
    parser.add_argument("--only", action="append")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--mode", choices=("route", "persistent"), default="persistent")
    parser.add_argument("--workers", type=int, default=24)
    args = parser.parse_args()
    if args.workers < 1 or args.rows_per_route < 1:
        parser.error("workers and rows-per-route must be positive")
    if args.action == "capture" and (not args.db or not args.run):
        parser.error("capture requires --db and --run")
    if args.action != "capture" and not args.output:
        parser.error("replay and compare require --output")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    globals()[args.action](args)


if __name__ == "__main__":
    main()
