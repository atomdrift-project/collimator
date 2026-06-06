#!/usr/bin/env python3
"""Fail the deploy if collimator, the staged bundle, and litmus disagree on the
default tuning goal (DEFAULT_SEVERITY_LEVEL).

The operating point travels embedded in the model: collimator bakes its
``DEFAULT_SEVERITY_LEVEL`` into each bundle's ``config.json`` as
``default_severity_level``, and litmus / autocollie read it from there at
runtime. This gate, run in azoth-deploy-final, ensures:

  * the staged bundle was calibrated at collimator's CURRENT default (not a
    stale value from an older checkout), and
  * litmus's fallback const still matches collimator (so configless bundles and
    the resolution fallback stay consistent).

Either mismatch fails the deploy before the bundle ships.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from collimator.thresholds import DEFAULT_SEVERITY_LEVEL  # noqa: E402


def _litmus_const(litmus_dir: Path) -> int | None:
    text = (litmus_dir / "src" / "model.rs").read_text()
    m = re.search(r"pub const DEFAULT_SEVERITY_LEVEL:\s*u\d+\s*=\s*(\d+)", text)
    return int(m.group(1)) if m else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--staged", type=Path, required=True, help="staged bundle dir (contains config.json)")
    ap.add_argument("--litmus-dir", type=Path, required=True, help="litmus checkout root")
    args = ap.parse_args()

    col = int(DEFAULT_SEVERITY_LEVEL)
    cfg = json.loads((args.staged / "config.json").read_text()).get("default_severity_level")
    lit = _litmus_const(args.litmus_dir)

    print(f"deploy tuning goal (DEFAULT_SEVERITY_LEVEL): "
          f"collimator={col} bundle={cfg} litmus_fallback={lit}")

    problems: list[str] = []
    if cfg is None:
        problems.append(
            "staged bundle config.json has no default_severity_level — recalibrate "
            "with the current collimator (make azoth-calibrate)"
        )
    elif int(cfg) != col:
        problems.append(
            f"staged bundle default_severity_level={cfg} != collimator {col} "
            "(bundle was calibrated against a different collimator default)"
        )
    if lit is None:
        problems.append(f"could not parse litmus DEFAULT_SEVERITY_LEVEL from {args.litmus_dir}/src/model.rs")
    elif lit != col:
        problems.append(
            f"litmus fallback const={lit} != collimator {col} — update "
            "litmus/src/model.rs `pub const DEFAULT_SEVERITY_LEVEL`"
        )

    if problems:
        print("ERROR: deploy tuning goal disagreement:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print("ok: collimator, staged bundle, and litmus agree on the tuning goal")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
