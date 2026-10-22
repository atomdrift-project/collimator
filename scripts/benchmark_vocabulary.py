#!/usr/bin/env python3
"""Measure synthetic vocabulary counting with optional before/after comparison.

--baseline-dir expects features_before.py and vocabulary_before.py copied from
the implementation to compare. Timings use in-memory reports, include closing
and flushing the counter, and verify every family against baseline.
These are component benchmarks, not full-corpus runtime predictions.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
import statistics
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from collimator import data, features  # noqa: E402


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def cases():
    def file(paths):
        return {"type": "pe", "ts": [
            {"i": f"capability/{p:03d}/path", "l": 4, "c": 1.0} for p in paths
        ]}

    def corpus(files, label):
        return {rid: {"cleave_result": {"v": "4", "fs": fs}}
                for rid, fs in enumerate(files, 1)}, label

    repeated = [[file(range(64))] for _ in range(32)]
    rng = random.Random(53)
    diverse = [[file(sorted(rng.sample(range(256), 48)))] for _ in range(16)]
    archives = [[file(range(0, 24)), file(range(8, 32)), file(range(0, 24))]
                for _ in range(32)]
    return [
        ("repeated_single_file", *corpus(repeated, 1), 32),
        ("repeated_across_batches", *corpus(repeated, 1), 4),
        ("distinct_single_files", *corpus(diverse, 1), 16),
        ("overlapping_archive_members", *corpus(archives, 1), 4),
        ("benign_singletons", *corpus(repeated * 64, 0), 128),
    ]


def run(module, reports, label, batch_size, scratch):
    labels = [(rid, label) for rid in reports]
    path = scratch / "counts.sqlite"
    views = {}
    started = time.perf_counter()
    with module.VocabularyCounts(str(path)) as counts:
        for offset in range(0, len(labels), batch_size):
            module._count_labeled_vocab_batch(
                "benchmark", labels[offset:offset + batch_size], counts,
            )
        for family in ("bigram", "trigram", "tiered_bigram", "tiered_trigram"):
            views[family] = module.CountView(str(path), family)
    elapsed = time.perf_counter() - started
    # Decoding/reference comparison is deliberately outside the timed region.
    return elapsed, {family: dict(view.items()) for family, view in views.items()}


def prevalence(module):
    candidates = [f"a + b{i:05d} + c" for i in range(5000)]
    report = {"v": "4", "fs": [{"ts": [
        {"i": p, "l": 4, "c": 1.0} for p in ("a", "b00001", "c")
    ]}]}
    ids = list(range(128))
    with patch.object(data, "fetch_cleave_results",
                      lambda _dsn, rows: {rid: {"cleave_result": report} for rid in rows}):
        started = time.perf_counter()
        # Both versions receive candidates directly here, so this isolates
        # matching work rather than the additional gain from worker reuse.
        counts = module._vocab_benign_trigram_worker(("benchmark", ids, candidates, None))
        elapsed = time.perf_counter() - started
    assert counts == {"a + b00001 + c": len(ids)}
    return elapsed


def merging(module):
    tokens = [f"path/{i:03d}" for i in range(64)]
    with tempfile.TemporaryDirectory(prefix="vocab-merge-benchmark-") as root:
        root = Path(root)
        views = []
        for i in range(3):
            with module.VocabularyCounts(str(root / f"worker-{i}.sqlite")) as counts:
                counts.increment_combinations("trigram", tokens, 3, i)
                views.append(counts.view("trigram"))
        with module.VocabularyCounts(str(root / "merged.sqlite")) as counts:
            started = time.perf_counter()
            for view in views:
                counts.merge(view)
            elapsed = time.perf_counter() - started
            reference = dict(counts.view("trigram").items())
        assert len(reference) == 41664
        assert set(reference.values()) == {3}
    return elapsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-dir", type=Path)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be positive")
    modules = {"current": features}
    if args.baseline_dir:
        old_counts = load_module("collimator._benchmark_counts",
                                 args.baseline_dir / "vocabulary_before.py")
        old_features = load_module("collimator._benchmark_features",
                                   args.baseline_dir / "features_before.py")
        old_features.VocabularyCounts = old_counts.VocabularyCounts
        old_features.CountView = old_counts.CountView
        modules = {"baseline": old_features, **modules}

    results = []
    for name, reports, label, batch_size in cases():
        timings = {}
        reference = None
        with patch.object(data, "fetch_cleave_results",
                          lambda _dsn, ids: {rid: reports[rid] for rid in ids}):
            for version, module in modules.items():
                samples = []
                for _ in range(args.repeat):
                    with tempfile.TemporaryDirectory(prefix="vocab-benchmark-") as root:
                        elapsed, counts = run(module, reports, label, batch_size, Path(root))
                    samples.append(elapsed)
                    if reference is None:
                        reference = counts
                    elif counts != reference:
                        raise AssertionError(f"{name}: vocabulary counts changed for {version}")
                timings[version] = statistics.median(samples)
        result = {"case": name, "rows": len(reports), "batch_size": batch_size,
                  "seconds": timings, "exact_counts_match": True}
        if "baseline" in timings:
            result["speedup"] = timings["baseline"] / timings["current"]
        results.append(result)
        print(json.dumps(result), flush=True)
    timings = {version: statistics.median(prevalence(module) for _ in range(args.repeat))
               for version, module in modules.items()}
    result = {"case": "benign_candidate_matching", "rows": 128,
              "candidates": 5000, "seconds": timings, "exact_counts_match": True}
    if "baseline" in timings:
        result["speedup"] = timings["baseline"] / timings["current"]
    results.append(result)
    print(json.dumps(result), flush=True)
    timings = {version: statistics.median(merging(module) for _ in range(args.repeat))
               for version, module in modules.items()}
    result = {"case": "aligned_dictionary_merges", "shards": 3,
              "seconds": timings, "exact_counts_match": True}
    if "baseline" in timings:
        result["speedup"] = timings["baseline"] / timings["current"]
    results.append(result)
    print(json.dumps(result), flush=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
