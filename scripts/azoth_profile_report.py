#!/usr/bin/env python3
"""Combine cProfile output from a sampled pipeline, including workers/merges."""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import pstats
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("directory", type=Path)
parser.add_argument("--limit", type=int, default=30)
args = parser.parse_args()
timing_root = args.directory / "timings"
if not timing_root.exists():
    timing_root = args.directory.parent / "timings"
totals = defaultdict(lambda: [0, 0., 0.])
active = {}
merge_totals = defaultdict(lambda: [0, 0, 0, 0, 0., 0.])
merge_phase = {}
signature_occurrences = signature_expansions = 0
for path in timing_root.glob("*.jsonl"):
    for line in path.read_text().splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:  # a live writer may still be finishing its last line
            continue
        key = (row["pid"], row["thread"], row.get("span"))
        thread = (row["pid"], row["thread"])
        if row["event"] == "counts" and row["label"] == "vocabulary.merge":
            merge_phase[thread] = row["phase"]
            values = merge_totals[row["phase"]]
            values[0] += 1
            values[1] += row["batches"]
            values[2] += row["source_bytes"]
            values[3] += int(row["remapped"])
        elif row["event"] == "counts" and row["label"] == "vocabulary.signatures":
            signature_occurrences += row["documents"]
            signature_expansions += row["signatures"]
        if row["event"] == "start":
            active[key] = row
        elif row["event"] == "end":
            active.pop(key, None)
            values = totals[row["label"]]
            values[0] += 1
            values[1] += row["wall_seconds"]
            values[2] += row["thread_cpu_seconds"]
            if row["label"] == "vocabulary.merge" and thread in merge_phase:
                values = merge_totals[merge_phase.pop(thread)]
                values[4] += row["wall_seconds"]
                values[5] += row["thread_cpu_seconds"]
if totals or active:
    print("Live timings: nested/concurrent calls overlap; CPU is the calling thread only.")
    print(f"{'Phase':40s} {'Calls':>7s} {'Wall sum(s)':>12s} {'Thread CPU(s)':>14s}")
    for label, (count, wall, cpu) in sorted(totals.items(), key=lambda item: -item[1][1]):
        print(f"{label:40s} {count:7d} {wall:12.1f} {cpu:14.1f}")
    for row in active.values():
        print(f"Unfinished: {row['label']} pid={row['pid']} started {time.time()-row['timestamp']:.0f}s ago "
              "(running or interrupted)")
if merge_totals:
    print("Vocabulary shards (completed merge inputs; sources may contain overlapping keys):")
    print(f"{'Phase':12s} {'Shards':>8s} {'Batches':>8s} {'Source MiB':>12s} "
          f"{'Remapped':>9s} {'Wall sum(s)':>12s} {'Thread CPU(s)':>14s}")
    for label, (shards, batches, size, remapped, wall, cpu) in sorted(merge_totals.items()):
        print(f"{label:12s} {shards:8d} {batches:8d} {size / 2**20:12.1f} "
              f"{remapped:9d} {wall:12.1f} {cpu:14.1f}")
if signature_expansions:
    print(f"Signature reuse: {signature_occurrences:,} token-set occurrences -> "
          f"{signature_expansions:,} expansions "
          f"({signature_occurrences / signature_expansions:.2f}x; excludes multi-file unions)")
paths = sorted(args.directory.rglob("*.prof"))
if not paths:
    if totals or active:
        raise SystemExit(0)
    parser.error("no timing records or completed .prof files found")
stats = pstats.Stats(*(str(path) for path in paths))
print(f"Combined {len(paths)} profiles; concurrent process times are summed, not wall time.")
stats.strip_dirs().sort_stats("cumulative").print_stats(args.limit)
stats.sort_stats("tottime").print_stats(args.limit)
