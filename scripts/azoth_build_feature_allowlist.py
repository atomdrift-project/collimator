#!/usr/bin/env python3
"""Build a self-calibrating feature allow-list = importance ∪ frequency-floor.

Consumed by training via COLLIMATOR_ALLOWED_FEATURES_FILE (features.py:1432,
reads the ``significant_features`` key). Designed to be regenerated EVERY
deploy cycle so the kept-feature set tracks the data instead of going stale:

  importance      — feature NAMES the currently-deployed ensemble splits on,
                    read from each route's ONNX + sibling feature_spec.json.
                    Self-updates from the last bundle (one-cycle feedback).
  frequency-floor — feature NAMES above a corpus-frequency threshold, recounted
                    from the live DB. Admits features no model has used YET, so
                    the loop can DISCOVER new ones instead of ossifying on the
                    set the last model happened to use.

The union is the point: importance keeps the proven tail features (memory win
without a quality hit), the floor keeps the door open for new ones. The
aggressiveness knob (--target-size / --freq-min) is a memory-vs-tail tradeoff
that should be swept + gated on FP/100M (check_azoth_regression.py), i.e. owned
by autocollie — not pinned here.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from pathlib import Path

import numpy as np


def _used_names(onnx_path: str, spec_names: list[str]) -> set[str]:
    import onnx
    m = onnx.load(onnx_path); ids = modes = None
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
    ap.add_argument("--general-spec", default=None,
                    help="full feature_spec.json (defaults to <bundle>/general/feature_spec.json)")
    ap.add_argument("--db", default=os.environ.get("DB", "postgres://hopper@localhost:5432/hopper"))
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--target-size", type=int, default=15000,
                    help="union target; frequency floor fills up to this (LEVEL knob)")
    ap.add_argument("--freq-min", type=int, default=0,
                    help="absolute corpus-frequency floor; overrides --target-size if >0")
    ap.add_argument("--sample-per-type", type=int, default=6000,
                    help="rows/filetype for the frequency recount (0 = importance only)")
    ap.add_argument("--output", default="out/models/azoth/allowed_features.json")
    args = ap.parse_args()

    import sys; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from collimator import features as F
    gspec_path = args.general_spec or os.path.join(args.bundle, "general/feature_spec.json")
    gspec = F.FeatureSpec.load(gspec_path)
    full_names = list(gspec.feature_names); NF = len(full_names)

    # 1) importance union from the deployed bundle's route models
    importance: set[str] = set()
    n_models = 0
    for onnx_path in glob.glob(os.path.join(args.bundle, "**/models/*.onnx"), recursive=True):
        spec_path = os.path.join(os.path.dirname(os.path.dirname(onnx_path)), "feature_spec.json")
        names = full_names
        if os.path.exists(spec_path):
            try: names = list(F.FeatureSpec.load(spec_path).feature_names)
            except Exception: names = full_names
        importance |= _used_names(onnx_path, names); n_models += 1
    importance &= set(full_names)  # only names that exist in the trainable vocab
    print(f"importance: {len(importance):,} feature names across {n_models} route models")

    # 2) frequency floor (recounted live) to prevent ossification
    floor: set[str] = set()
    if args.sample_per_type > 0:
        import scripts.azoth_specialist_suite as S
        types = ["pe","xml","java_class","png","javascript","c","go","csharp","html",
                 "json","rust","pdf","shell","elf","python","macho","ruby","perl","php","lua"]
        samp = []; rng = np.random.default_rng(1)
        for ft in types:
            rows = S._fetch_rows(args.db, file_types=(ft,), max_id=0, min_score=None)
            tr = S._ids_labels(rows, test=False)
            if tr:
                k = min(args.sample_per_type, len(tr))
                samp += [tr[i] for i in rng.choice(len(tr), k, replace=False)]
        print(f"frequency floor: extracting {len(samp):,} corpus sample rows...")
        Xc, _, _, _ = F.extract_partitioned_from_db(args.db, samp, [], gspec, n_workers=args.workers)
        freq = np.asarray((Xc > 0).sum(axis=0)).ravel()
        if args.freq_min > 0:
            idx = np.where(freq >= args.freq_min)[0]
        else:
            budget = max(0, args.target_size - len(importance))
            ranked = np.argsort(-freq)
            idx = ranked[freq[ranked] > 0][:budget]
        floor = {full_names[i] for i in idx}
        print(f"frequency floor: {len(floor):,} names "
              f"({'freq>=%d' % args.freq_min if args.freq_min else 'top-up to %d' % args.target_size})")

    allow = sorted(importance | floor)
    out = {
        "significant_features": allow,
        "meta": {
            "generated_from_bundle": args.bundle, "full_features": NF,
            "kept": len(allow), "dropped": NF - len(allow),
            "drop_pct": round(100 * (NF - len(allow)) / max(NF, 1), 1),
            "importance": len(importance), "frequency_floor_only": len(floor - importance),
            "route_models": n_models, "target_size": args.target_size, "freq_min": args.freq_min,
        },
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f: json.dump(out, f, indent=0)
    m = out["meta"]
    print(f"\nallowlist: {m['kept']:,} kept / {m['dropped']:,} dropped of {NF:,} ({m['drop_pct']}%)")
    print(f"  importance {m['importance']:,} + floor-only {m['frequency_floor_only']:,}")
    print(f"wrote {args.output}")
    print(f"\nNext cycle:\n  export COLLIMATOR_ALLOWED_FEATURES_FILE={args.output}")
    print("Then gate the retrain on FP/100M: scripts/check_azoth_regression.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
