#!/usr/bin/env python3
"""Compare independent/shared vocabulary work on a bounded frozen cohort.

Run each mode in a fresh, resource-limited process with a fresh output directory.
Only vocabulary generation is measured; models are not fitted or published.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
import logging
import os
from pathlib import Path
import resource
import struct
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True, help="Saved experiment with feature_env")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("independent", "shared"), required=True)
    parser.add_argument("--rows", type=int, default=4096)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    if args.rows < 2 or args.workers < 1:
        parser.error("need at least two rows and one worker")
    args.output.mkdir(parents=True, exist_ok=False)
    saved = json.loads(args.run.read_text())
    os.environ.update(saved["feature_env"])
    for key in ("COLLIMATOR_PROFILE_DIR", "COLLIMATOR_SHARED_VOCAB_DIR"):
        os.environ.pop(key, None)
    os.environ["COLLIMATOR_TIMING_DIR"] = str((args.output/"timings").resolve())
    os.environ["COLLIMATOR_NUM_THREADS"] = str(args.workers)
    os.environ["COLLIMATOR_VOCAB_TMPDIR"] = str((args.output/"scratch").resolve())
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    from collimator import data, features
    features.feature_config_from_env.cache_clear()
    selected = json.loads(args.cohort.read_text())["train"]
    labels = [(s["row_id"], s["label"]) for s in selected]
    rows = sorted(features._stable_vocab_scan_rows(labels, args.rows))
    groups = {s["row_id"]:data.oof_fold_of(s["group_id"]) for s in selected}
    assert all(groups[rid] in (0,1) for rid,_ in rows)
    cohorts = {"prod":rows, "fold-a":[r for r in rows if groups[r[0]] == 1],
               "fold-b":[r for r in rows if groups[r[0]] == 0]}
    del selected, labels
    verification_wall = verification_cpu = 0.0
    raw_counts = {}

    def verify(selected_rows, counts):
        nonlocal verification_wall, verification_cpu
        identity = hashlib.sha256(json.dumps(selected_rows).encode()).hexdigest()
        if identity in raw_counts:
            return
        counts.materialize()  # Necessary training work, included in its timing.
        started, cpu = time.monotonic(), time.process_time()
        total = keys = 0
        logical_counts = counts.iter_counts() if hasattr(counts, "iter_counts") else counts.db.execute("SELECT family,token,n FROM counts")
        for family, packed, n in logical_counts:
            names = [counts.tokens[i] for i in struct.unpack(f">{len(packed)//4}I", packed)]
            payload = json.dumps([family,names,n],separators=(",",":")).encode()
            total = (total + int.from_bytes(hashlib.sha256(payload).digest(), "big")) % (1 << 256)
            keys += 1
        raw_counts[identity] = dict(rows=len(selected_rows), keys=keys,
                                   count_multiset_sha256_sum=f"{total:064x}")
        verification_wall += time.monotonic()-started
        verification_cpu += time.process_time()-cpu
        logging.info("verified raw discovery counts: %d rows, %d keys",len(selected_rows),keys)

    original_count = features._count_vocab_rows
    def count(*positional):
        result = original_count(*positional)
        verify(positional[1],positional[3])
        return result
    original_shared = features._shared_fold_counts
    def shared(*positional):
        result = original_shared(*positional)
        verify(positional[1],positional[4])
        return result
    features._count_vocab_rows = count
    features._shared_fold_counts = shared
    specs = {}
    started, cpu = time.monotonic(), time.process_time()
    for name, selected_rows in cohorts.items():
        options = dict(shared_cache_dir=args.output/"shared", row_folds=(groups[rid] for rid,_ in selected_rows)) if args.mode == "shared" else {}
        spec = features.build_vocab_from_db(args.db.resolve(), selected_rows, n_workers=args.workers,
                                            checkpoint_dir=args.output/name, **options)
        serialized = json.dumps(asdict(spec),sort_keys=True)
        specs[name] = dict(rows=len(selected_rows), features=spec.total_features,
                          digest=hashlib.sha256(serialized.encode()).hexdigest())
        (args.output/f"{name}-spec.json").write_text(serialized+"\n")
    elapsed = time.monotonic()-started-verification_wall
    cpu_seconds = time.process_time()-cpu-verification_cpu
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    visits = returned = 0
    for path in (args.output/"timings").glob("*.jsonl"):
        for line in path.read_text().splitlines():
            record = json.loads(line)
            if record["label"] == "vocabulary.discovery" and record["event"] == "rows":
                visits += record["requested"]
                returned += record["returned"]
    result = dict(mode=args.mode, selected_rows=len(rows), workers=args.workers, specs=specs,
                  raw_counts=raw_counts, discovery_row_visits=visits, discovery_rows_returned=returned,
                  elapsed_seconds=elapsed, cpu_seconds_including_children=cpu_seconds+children.ru_utime+children.ru_stime,
                  excluded_verification_seconds=verification_wall,
                  parent_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  child_peak_rss_kib=children.ru_maxrss,
                  limitations="Sequential vocabulary generation only; frozen subset; count verification time excluded; no model fitting or deployment.")
    (args.output/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result),flush=True)


if __name__ == "__main__":
    main()
