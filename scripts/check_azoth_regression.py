#!/usr/bin/env python3
"""Block deploys that regress what litmus actually flags at L3 hostile.

Reads:
  --staged   <dir>   the staged-but-not-yet-deployed bundle
  --deployed <dir>   the bundle currently live (defaults to
                     $XDG_DATA_HOME/litmus/models/azoth)

Both must contain ``route_policy_eval_oof.json`` — the deployed
OR-rule / blend's tp/fp/recall per level on the locked test partition,
which is the ground truth of what litmus produces at scan time.

Per filetype where both bundles have ``n_malware >= --min-mal`` AND
``n_benign >= --min-ben`` (default 500/500), we compare deployed L3
hostile recall: new must be ≥ old − ``--recall-tolerance`` (default
0.01 = 1 percentage point).

Any violation is a deploy block. Exit codes:

  0 — no regressions over threshold
  1 — at least one violation
  2 — usage / IO error

Bypass with ``AZOTH_ALLOW_REGRESSION=1`` for intentional trade-offs.
Skip silently (exit 0) when the deployed bundle doesn't have a deployed
eval — first-deploy or pre-eval bundle.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path


def _load(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as e:
        print(f"warning: failed to load {path}: {e}", file=sys.stderr)
        return {}


def _is_finite_number(value) -> bool:
    if value is None:
        return False
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(v)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", type=Path, required=True)
    parser.add_argument(
        "--deployed", type=Path,
        default=Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
        / "litmus" / "models" / "azoth",
    )
    parser.add_argument("--min-mal", type=int, default=500)
    parser.add_argument("--min-ben", type=int, default=500)
    parser.add_argument("--recall-tolerance", type=float, default=0.01)
    parser.add_argument("--level", type=int, default=3)
    parser.add_argument("--severity", default="hostile", choices=["hostile", "suspicious"])
    args = parser.parse_args()

    if os.environ.get("AZOTH_ALLOW_REGRESSION", "").strip().lower() in {"1", "true", "yes"}:
        print("AZOTH_ALLOW_REGRESSION set; skipping regression check")
        return 0

    staged_eval = _load(args.staged / "route_policy_eval_oof.json")
    deployed_eval = _load(args.deployed / "route_policy_eval_oof.json")

    if not staged_eval:
        print(
            f"error: staged bundle has no route_policy_eval_oof.json at {args.staged}",
            file=sys.stderr,
        )
        return 2
    if not deployed_eval:
        print(
            f"no route_policy_eval_oof.json at deployed location ({args.deployed}); "
            "skipping regression check (first deploy or pre-eval bundle)",
        )
        return 0

    staged_ft = (staged_eval.get("filetypes") or {})
    deployed_ft = (deployed_eval.get("filetypes") or {})
    level_key = f"L{args.level}_{args.severity}"

    regressions: list[str] = []
    compared = 0
    skipped_small = 0

    for ft, deployed_entry in deployed_ft.items():
        staged_entry = staged_ft.get(ft)
        if not staged_entry:
            print(f"info: filetype {ft!r} present in deployed but absent in staged")
            continue
        n_mal = staged_entry.get("malware", 0) or 0
        n_ben = staged_entry.get("benign", 0) or 0
        d_mal = deployed_entry.get("malware", 0) or 0
        d_ben = deployed_entry.get("benign", 0) or 0
        if min(n_mal, d_mal) < args.min_mal or min(n_ben, d_ben) < args.min_ben:
            skipped_small += 1
            continue

        staged_l = (staged_entry.get("deployed_or_by_level") or {}).get(level_key) or {}
        deployed_l = (deployed_entry.get("deployed_or_by_level") or {}).get(level_key) or {}
        s_recall = staged_l.get("recall")
        d_recall = deployed_l.get("recall")
        if _is_finite_number(s_recall) and _is_finite_number(d_recall):
            drop = float(d_recall) - float(s_recall)
            if drop > args.recall_tolerance:
                regressions.append(
                    f"{ft}: L{args.level} {args.severity} recall dropped {drop*100:.2f}pp "
                    f"({float(d_recall)*100:.2f}% → {float(s_recall)*100:.2f}%; "
                    f"tolerance {args.recall_tolerance*100:.2f}pp)",
                )

        compared += 1

    if regressions:
        print()
        print(f"error: {len(regressions)} regression(s) over tolerance:")
        for r in regressions:
            print(f"  - {r}")
        print()
        print(
            f"compared {compared} filetypes "
            f"(mal≥{args.min_mal}, ben≥{args.min_ben}); "
            f"{skipped_small} below threshold and skipped.",
        )
        print()
        print(
            "If this regression is intentional, set "
            "AZOTH_ALLOW_REGRESSION=1 and re-run.",
        )
        return 1

    print(
        f"regression check ok: compared {compared} filetype(s) "
        f"(mal≥{args.min_mal}, ben≥{args.min_ben}) at L{args.level} "
        f"{args.severity}; tolerance {args.recall_tolerance*100:.2f}pp.",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
