#!/usr/bin/env python3
"""Build an optional name filter from current training data and feature knobs.

Discover a fresh vocabulary, count its columns in bounded batches, and retain
frequent candidates plus names used by existing tree splits. A deployed bundle
is optional and never limits discovery. Training needs no allowlist by default.
"""
from __future__ import annotations

import argparse
import glob
import json
import logging
import os
from pathlib import Path
import time

import numpy as np


def _used_names(onnx_path: str, spec_names: list[str]) -> set[str]:
    import onnx
    m = onnx.load(onnx_path, load_external_data=False); ids = modes = None
    for n in m.graph.node:
        for a in n.attribute:
            if a.name == "nodes_featureids": ids = list(a.ints)
            if a.name == "nodes_modes":
                modes = [s.decode() if isinstance(s, bytes) else s for s in a.strings]
    if ids is None: return set()
    pairs = zip(ids, modes) if modes else ((i, "X") for i in ids)
    return {spec_names[i] for i, md in pairs if md != "LEAF" and 0 <= i < len(spec_names)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bundle", default=os.path.expanduser("~/azoth"),
                    help="deployed bundle to read importance from (its route models)")
    ap.add_argument("--db", default=os.environ.get("DB", "postgres://hopper@localhost:5432/hopper"))
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--target-size", type=int, default=15000,
                    help="union target; frequency floor fills up to this (LEVEL knob)")
    ap.add_argument("--freq-min", type=int, default=0,
                    help="absolute corpus-frequency floor; overrides --target-size if >0")
    ap.add_argument("--sample-per-type", type=int, default=6000,
                    help="rows/filetype for the frequency recount (0 = importance only)")
    ap.add_argument("--filetypes", default="", help="comma-separated types; default: all labeled types")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--sampling-workers", type=int, default=4)
    ap.add_argument("--max-db-workers", type=int, default=24,
                    help="cap extraction DB connections; independent of host CPU count")
    ap.add_argument("--batch-size", type=int, default=256)
    ap.add_argument("--cache-dir", type=Path, default=Path("out/cache/azoth-allowlist"))
    ap.add_argument("--cache-max-age", type=float, default=3600,
                    help="maximum frequency-cache age in seconds")
    ap.add_argument("--refresh", action="store_true", help="force a new frequency audit")
    ap.add_argument("--output", default="out/models/azoth/allowed_features.json")
    args = ap.parse_args()
    if min(args.sample_per_type, args.target_size, args.freq_min, args.workers, args.cache_max_age) < 0:
        ap.error("sample counts, workers, sizes, and cache age must be nonnegative")
    if min(args.sampling_workers, args.max_db_workers, args.batch_size) < 1:
        ap.error("worker limits and batch size must be positive")
    args.filetypes = list(dict.fromkeys(ft.strip() for ft in args.filetypes.split(",") if ft.strip()))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s: %(message)s")
    started = time.monotonic()

    import sys; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from collimator import features as F
    from collimator.allowlist import frequency_counts
    # Existing tree splits are retained even when the sample misses a rare
    # feature. They are a retention signal, never a vocabulary ceiling.
    importance: set[str] = set()
    n_models = 0
    specs: dict[str, list[str]] = {}
    for onnx_path in sorted(glob.glob(os.path.join(args.bundle, "**/models/*.onnx"), recursive=True)):
        spec_path = os.path.join(os.path.dirname(os.path.dirname(onnx_path)), "feature_spec.json")
        if spec_path not in specs:
            specs[spec_path] = list(F.FeatureSpec.load(spec_path).feature_names)
        names = specs[spec_path]
        importance |= _used_names(onnx_path, names); n_models += 1
    print(f"importance: {len(importance):,} feature names across {n_models} route models", flush=True)

    # 2) frequency floor (recounted live) to prevent ossification
    floor: set[str] = set()
    audit: dict = {}
    full_names: list[str] = []
    if args.sample_per_type > 0:
        full_names, freq, audit = frequency_counts(args)
        if args.freq_min > 0:
            idx = np.where(freq >= args.freq_min)[0]
        else:
            budget = max(0, args.target_size - len(importance))
            # Fill with NEW names, using lexical ties for deterministic output.
            ranked = sorted(range(len(full_names)), key=lambda i: (-int(freq[i]), full_names[i]))
            idx = [i for i in ranked if freq[i] > 0 and full_names[i] not in importance][:budget]
        floor = {full_names[i] for i in idx}
        print(f"frequency floor: {len(floor):,} names "
              f"({'freq>=%d' % args.freq_min if args.freq_min else 'top-up to %d' % args.target_size})")

    allow = sorted(importance | floor)
    if not allow:
        raise RuntimeError("no retained features; refusing to write an empty allowlist")
    NF = len(set(full_names) | importance)
    out = {
        "significant_features": allow,
        "meta": {
            "generated_from_bundle": args.bundle, "full_features": NF,
            "candidate_source": "current training rows and feature knobs",
            "kept": len(allow), "dropped": NF - len(allow),
            "drop_pct": round(100 * (NF - len(allow)) / max(NF, 1), 1),
            "importance": len(importance), "frequency_floor_only": len(floor - importance),
            "route_models": n_models, "target_size": args.target_size, "freq_min": args.freq_min,
            "frequency_audit": audit,
        },
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    output = Path(args.output)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    with temporary.open("w") as f: json.dump(out, f, indent=0)
    temporary.replace(output)
    m = out["meta"]
    print(f"\nallowlist: {m['kept']:,} kept / {m['dropped']:,} dropped of {NF:,} ({m['drop_pct']}%)")
    print(f"  importance {m['importance']:,} + floor-only {m['frequency_floor_only']:,}")
    print(f"wrote {args.output} in {time.monotonic() - started:.1f}s")
    print(f"\nNext cycle:\n  export COLLIMATOR_ALLOWED_FEATURES_FILE={args.output}")
    print("Then gate the retrain on FP/100M: scripts/check_azoth_regression.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
