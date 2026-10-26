#!/usr/bin/env python3
"""Capture bounded counting inputs once; replay exact aggregation without a DB.

Capture uses an existing model's score cohort and vocabulary selection settings. Replay
holds fetch size fixed while varying shard size; each variant runs in a fresh
process so peak RSS and CPU time are comparable. No models are trained.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, replace
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import struct
import subprocess
import sys
import tempfile
import time

from collimator.vocabulary import CountView, VocabularyCounts


class Capture:
    path = "capture"

    def __init__(self):
        self.events = []

    def group_combinations(self, family, tokens, order, *, n=1):
        self.events.append([family, list(tokens), order, None, n])

    def increment_combinations(self, family, tokens, order, document, benign_family="", *, n=1):
        assert not benign_family
        self.events.append([family, list(tokens), order, document, n])

    def view(self, *args, **kwargs):
        return {}


def capture(args):
    import numpy as np
    from collimator import features

    spec = features.FeatureSpec.load(args.model / "feature_spec.json")
    config = replace(features.feature_config_from_env(), trait_path_depth=spec.trait_path_depth,
                     bigram_max=len(spec.bigram_vocab), trigram_max=len(spec.trigram_vocab),
                     include_tiered_crit_bigrams=bool(spec.tiered_bigram_vocab),
                     include_tiered_crit_trigrams=bool(spec.tiered_trigram_vocab),
                     tiered_bigram_min_crit=spec.tiered_min_crit[0],
                     tiered_trigram_min_crit=spec.tiered_min_crit[1],
                     tiered_bigram_branch_min_crit=tuple(
                         f"{branch}={floor}" for branch, floor in spec.tiered_branch_min_crit.items()))
    features.feature_config_from_env = lambda: config
    with np.load(args.model / "threshold_scores.npz") as scores:
        if not len(scores["row_ids"]):
            raise ValueError("score cohort is empty")
        indices = np.linspace(0, len(scores["row_ids"]) - 1,
                              min(args.rows, len(scores["row_ids"])), dtype=int)
        rows = list(zip(map(int, scores["row_ids"][indices]), map(int, scores["labels"][indices])))
    args.input.parent.mkdir(parents=True, exist_ok=True)
    with args.input.open("x") as output:
        for start in range(0, len(rows), args.batch_size):
            batch = rows[start:start + args.batch_size]
            recorder = Capture()
            features._count_labeled_vocab_batch(args.db, batch, recorder)
            output.write(json.dumps({"rows": len(batch), "events": recorder.events}) + "\n")
            output.flush()
            print(f"captured {start + len(batch)}/{len(rows)} rows", flush=True)
    with args.input.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    args.input.with_suffix(".metadata.json").write_text(json.dumps(
        dict(rows=len(rows), batch_size=args.batch_size, input_sha256=digest,
             model=str(args.model.resolve()), config=asdict(config)), indent=2, default=sorted) + "\n")


def replay(args):
    # Workers already import NumPy for feature extraction. Exclude import/BLAS
    # startup from all reducer timings, including the Python baseline.
    import numpy  # noqa: F401

    started, cpu = time.monotonic(), time.process_time()
    count_seconds = merge_seconds = 0.0
    rows = shards = events = 0
    deferred = args.mode in ("global", "parallel", "parallel-batched")
    extra = dict(defer_signatures=True, materialize_workers=2 if args.mode != "global" else 1) if deferred else {}
    if args.mode == "parallel-batched":
        extra["materialize_merge_size"] = 2
    prefill = getattr(args, "prefill", None)
    with tempfile.TemporaryDirectory(prefix="vocab-replay-", dir=args.scratch) as scratch:
        destination = Path(scratch) / "merged.sqlite"
        copy_started = time.monotonic()
        if prefill:
            shutil.copyfile(prefill, destination)
            # Keep fixture-copy writeback outside the aggregation measurement.
            with destination.open("rb") as copied:
                os.fsync(copied.fileno())
        prefill_copy_seconds = time.monotonic() - copy_started
        started, cpu = time.monotonic(), time.process_time()
        with VocabularyCounts(str(Path(scratch) / "merged.sqlite"), durable=True,
                              cache_size_mib=256, stable_token_ids=args.token_ids == "stable",
                              resume=bool(prefill), **extra) as merged:
            worker = None
            ready = []
            with args.input.open() as source:
                for batch_index, line in enumerate(source):
                    batch = json.loads(line)
                    rows += batch["rows"]
                    if worker is None:
                        worker = VocabularyCounts(str(Path(scratch) / f"worker-{shards}.sqlite"),
                                                  bulk_signatures=args.mode in ("bulk", "global", "parallel", "parallel-batched", "sorted"),
                                                  stable_token_ids=args.token_ids == "stable",
                                                  **(dict(defer_signatures=True) if deferred else {}))
                    t = time.monotonic()
                    groups = Counter()
                    for family, tokens, order, document, n in batch["events"]:
                        events += 1
                        if document is None:
                            if args.mode == "batch":
                                groups[family, tuple(tokens), order] += n
                            else:
                                worker.group_combinations(family, tokens, order, n=n)
                        else:
                            worker.increment_combinations(family, tokens, order, document, n=n)
                    for (family, tokens, order), n in groups.items():
                        worker.increment_combinations(family, tokens, order, None, n=n)
                    worker.record_batch(f"count:{batch_index}", None, batch["rows"])
                    count_seconds += time.monotonic() - t
                    if (batch_index + 1) % args.shard_batches == 0:
                        t = time.monotonic()
                        worker.close()
                        count_seconds += time.monotonic() - t
                        t = time.monotonic()
                        if args.mode == "sorted":
                            ready.append(CountView(worker.path, "bigram"))
                            if len(ready) == 8:
                                merge_sorted(merged, ready)
                                ready.clear()
                        else:
                            merged.merge(CountView(worker.path, "bigram"))
                        merge_seconds += time.monotonic() - t
                        worker = None
                        shards += 1
            if worker is not None:
                t = time.monotonic()
                worker.close()
                count_seconds += time.monotonic() - t
                t = time.monotonic()
                if args.mode == "sorted":
                    ready.append(CountView(worker.path, "bigram"))
                else:
                    merged.merge(CountView(worker.path, "bigram"))
                merge_seconds += time.monotonic() - t
                shards += 1
            if ready:
                t = time.monotonic()
                merge_sorted(merged, ready)
                merge_seconds += time.monotonic() - t
            t = time.monotonic()
            if hasattr(merged, "materialize"):
                merged.materialize()
            materialize_seconds = time.monotonic() - t
            elapsed, cpu_seconds = time.monotonic() - started, time.process_time() - cpu
            children = resource.getrusage(resource.RUSAGE_CHILDREN)
            peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            # Canonical names, not local IDs, define equality across variants.
            # SQLite provides an external sort rather than a giant Python dict.
            merged.db.create_function("canonical", 1, lambda key: " + ".join(
                merged.tokens[i] for i in struct.unpack(f">{len(key)//4}I", key)))
            digest = hashlib.sha256()
            keys = 0
            if prefill:
                for family, key, n in merged.db.execute("SELECT family, token, n FROM counts ORDER BY 1,2"):
                    name = family.encode()
                    digest.update(struct.pack(">IIQ",len(name),len(key),n) + name + key)
                    keys += 1
            else:
                for row in merged.db.execute("SELECT family, canonical(token), n FROM counts ORDER BY 1, 2"):
                    digest.update((json.dumps(row) + "\n").encode())
                    keys += 1
            result = dict(mode=args.mode, token_ids=args.token_ids,
                          shard_batches=args.shard_batches, rows=rows, events=events,
                          shards=shards, keys=keys, digest=digest.hexdigest(),
                          elapsed_seconds=elapsed, cpu_seconds=cpu_seconds,
                          cpu_with_children_seconds=cpu_seconds + children.ru_utime + children.ru_stime,
                          child_peak_rss_kib=children.ru_maxrss,
                          count_seconds=count_seconds, merge_seconds=merge_seconds,
                          materialize_seconds=materialize_seconds, prefill=str(prefill or ""),
                          prefill_copy_seconds=prefill_copy_seconds,
                          database_bytes=Path(merged.path).stat().st_size,
                          aggregation_peak_rss_kib=peak_rss,
                          verification_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            print(json.dumps(result), flush=True)


def merge_sorted(merged, views):
    """Benchmark-only bounded SQL sort/reduce alternative; no default change."""
    from collimator.vocabulary import _packed_remapper
    attached = []
    try:
        selections = []
        for i, view in enumerate(views):
            alias = f"input{i}"
            merged.db.execute(f"ATTACH DATABASE ? AS {alias}", (Path(view.path).resolve().as_uri()+"?mode=ro",))
            attached.append(alias)
            mapping = {old: merged._token_id(token) for old, token in merged.db.execute(f"SELECT id, token FROM {alias}.tokens")}
            key = "token"
            if any(old != new for old, new in mapping.items()):
                merged.db.create_function(f"remap{i}",1,_packed_remapper(mapping))
                key = f"remap{i}(token)"
            selections.append(f"SELECT family,{key} AS token,n FROM {alias}.counts")
        merged.db.execute("INSERT INTO counts SELECT family,token,sum(n),NULL,NULL FROM ("+
                          " UNION ALL ".join(selections)+") WHERE true GROUP BY family,token "
                          "ON CONFLICT(family,token) DO UPDATE SET n=n+excluded.n,first_document=NULL,document=NULL")
        for alias in attached:
            merged.db.execute(f"INSERT INTO batches SELECT * FROM {alias}.batches")
        merged.db.commit()
    except BaseException:
        merged.db.rollback()
        raise
    finally:
        for alias in attached:
            merged.db.execute(f"DETACH DATABASE {alias}")
    for view in views:
        Path(view.path).unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["capture", "replay", "compare"])
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--db")
    parser.add_argument("--rows", type=int, default=8192)
    parser.add_argument("--batch-size", type=int, default=170)
    parser.add_argument("--shard-batches", type=int, default=8)
    parser.add_argument("--mode", choices=["batch", "shard", "bulk", "global", "parallel", "parallel-batched", "sorted"], default="bulk")
    parser.add_argument("--prefill", type=Path, help="Existing closed count database for storage-scale stress replay")
    parser.add_argument("--token-ids", choices=["dense", "stable"], default="stable")
    parser.add_argument("--scratch", type=Path, default=Path("/tmp"))
    args = parser.parse_args()
    if args.rows < 1 or args.batch_size < 1 or args.shard_batches < 1:
        parser.error("rows and batch sizes must be positive")
    if args.action == "capture":
        if not args.model or not args.db:
            parser.error("capture requires --model and --db")
        capture(args)
    elif args.action == "replay":
        replay(args)
    else:
        results = []
        for mode, size, ids in [("batch", 8, "dense"), ("shard", 8, "dense"),
                               ("shard", 16, "dense"), ("shard", 32, "dense"),
                               ("bulk", 16, "dense"), ("bulk", 16, "stable"),
                               ("bulk", 32, "stable")]:
            command = [sys.executable, __file__, "replay", "--input", str(args.input),
                       "--scratch", str(args.scratch), "--mode", mode, "--shard-batches", str(size),
                       "--token-ids", ids]
            result = json.loads(subprocess.check_output(command, text=True))
            results.append(result)
            print(json.dumps(result), flush=True)
        if len({result["digest"] for result in results}) != 1:
            raise RuntimeError("exact counts differ between aggregation variants")


if __name__ == "__main__":
    main()
