#!/usr/bin/env python3
"""Simulate per-filetype 0.5 FP/M policy selection (L50 on the per-100M scale).

For each filetype with adequate data, scans the L50 hostile candidates in
``route_policies.json`` and picks the one that maximizes recall while
honestly hitting ≤ ``--target-fp-per-million`` × ``--max-fpr-multiplier``
on the slice's own benign tail. The multiplier guard catches cases where a
candidate is LABELED at the level's nominal FP budget but the calibration
degenerates and the realized FPR is way over target (e.g. xlsx
``filetype_only_at_fp_*`` ends up firing on 100% of benigns).

Output: per-filetype before/after recall, before/after FPR, the chosen
new policy, and the global rollup (total recall and corpus-wide FPR if
we deployed the new picks).

This is a DIAGNOSTIC — it doesn't modify any files. It tells us what we'd
get if we replaced ``_apply_global_budget_selection`` with a clamped per-
filetype max-recall picker.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from collimator.thresholds import DEFAULT_SEVERITY_LEVEL  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--policies", type=Path,
        default=Path("out/models/azoth/route_policies.json"),
    )
    p.add_argument(
        "--target-fp-per-million", type=float,
        default=DEFAULT_SEVERITY_LEVEL / 100.0,
        help=(
            f"Per-slice FP/M ceiling (default "
            f"{DEFAULT_SEVERITY_LEVEL / 100.0:g} = L{DEFAULT_SEVERITY_LEVEL} "
            f"on the per-100M scale; derived from "
            f"collimator.thresholds.DEFAULT_SEVERITY_LEVEL). Candidates with "
            f"realized FPR above (target × max-fpr-multiplier) are filtered out."
        ),
    )
    p.add_argument(
        "--max-fpr-multiplier", type=float, default=3.0,
        help="How much realized-FPR slack to allow above target. "
             "Default 3.0 — candidates up to 3× the target FP/M are eligible. "
             "Below 1.0 enforces strict ≤target; above 1.0 permits slop from "
             "finite-sample quantile noise.",
    )
    args = p.parse_args()

    doc = json.loads(args.policies.read_text())
    total_corpus_benign = int(doc["benign"])
    total_corpus_malware = int(doc["malware"])

    target = float(args.target_fp_per_million)
    ceiling_fpm = target * args.max_fpr_multiplier

    # Per filetype: pick candidate.
    sum_deployed_tp = 0
    sum_deployed_fp = 0
    sum_picked_tp = 0
    sum_picked_fp = 0
    rows = []
    for route_name, route in doc["routes"].items():
        ft = route.get("filetype") or route_name.split("/")[-1]
        n_ben = int(route.get("benign") or 0)
        n_mal = int(route.get("malware") or 0)
        if n_ben < 1 or n_mal < 1:
            continue
        # Find deploy-default hostile (per-100M scale; derived from
        # DEFAULT_SEVERITY_LEVEL).
        default_level_row = next(
            (lev for lev in route["levels"]
             if int(lev["level"]) == DEFAULT_SEVERITY_LEVEL),
            None,
        )
        if not default_level_row:
            continue
        h = default_level_row.get("hostile") or {}
        deployed = h.get("best") or {}
        deployed_tp = int(deployed.get("tp") or 0)
        deployed_fp = int(deployed.get("fp") or 0)
        deployed_policy = deployed.get("policy") or "?"
        deployed_recall = float(deployed.get("recall") or 0.0)

        # Candidates: keep those where realized FPR ≤ ceiling_fpm.
        # FPR per slice = candidate.fp / route.benign × 1e6.
        # When n_ben is tiny, even 1 FP can blow past the ceiling — that's
        # fine, the candidate gets filtered, and we fall back to fp=0.
        eligible = []
        for cand in (h.get("candidates") or []):
            cand_fp = int(cand.get("fp") or 0)
            cand_recall = float(cand.get("recall") or 0.0)
            realized_fpm = (cand_fp / n_ben) * 1_000_000.0 if n_ben else math.inf
            if realized_fpm <= ceiling_fpm and not math.isnan(cand_recall):
                eligible.append((cand_recall, cand_fp, cand))
        # Always include a fallback fp=0/recall=0 "no policy" so the picker
        # never has to throw up its hands.
        if not eligible:
            eligible.append((0.0, 0, {"policy": "no_policy", "fp": 0, "tp": 0, "recall": 0.0}))
        # Max by (recall, -fp, then policy name).
        eligible.sort(
            key=lambda t: (
                t[0],
                -t[1],
                str(t[2].get("policy") or ""),
            ),
            reverse=True,
        )
        picked = eligible[0][2]
        picked_tp = int(picked.get("tp") or 0)
        picked_fp = int(picked.get("fp") or 0)
        picked_recall = float(picked.get("recall") or 0.0)
        picked_policy = picked.get("policy") or "?"

        sum_deployed_tp += deployed_tp
        sum_deployed_fp += deployed_fp
        sum_picked_tp += picked_tp
        sum_picked_fp += picked_fp

        rows.append({
            "ft": ft,
            "n_mal": n_mal,
            "n_ben": n_ben,
            "deployed_policy": deployed_policy,
            "deployed_recall": deployed_recall,
            "deployed_fp": deployed_fp,
            "picked_policy": picked_policy,
            "picked_recall": picked_recall,
            "picked_fp": picked_fp,
            "tp_gain": picked_tp - deployed_tp,
            "fp_gain": picked_fp - deployed_fp,
        })

    rows.sort(key=lambda r: -r["tp_gain"])

    # Render header.
    print(
        f"{'filetype':<16} {'n_mal':>7} {'n_ben':>7} "
        f"{'deployed':<28} {'dep_r':>6} {'picked':<28} {'pick_r':>6} "
        f"{'Δrecall':>7} {'Δtp':>6} {'Δfp':>5} {'slice_fpm':>9}"
    )
    print("-" * 158)
    for r in rows:
        slice_fpm = (r["picked_fp"] / r["n_ben"]) * 1_000_000.0 if r["n_ben"] else math.inf
        d_recall = r["picked_recall"] - r["deployed_recall"]
        if abs(d_recall) < 0.005 and r["tp_gain"] == 0:
            continue  # quiet — same as deployed
        print(
            f"{r['ft']:<16} {r['n_mal']:>7} {r['n_ben']:>7} "
            f"{r['deployed_policy'][:28]:<28} {r['deployed_recall']*100:6.2f} "
            f"{r['picked_policy'][:28]:<28} {r['picked_recall']*100:6.2f} "
            f"{d_recall*100:+7.2f} {r['tp_gain']:+6} {r['fp_gain']:+5} {slice_fpm:9.1f}"
        )

    # Global rollup.
    print()
    print("=" * 80)
    deployed_corpus_fpm = sum_deployed_fp / total_corpus_benign * 1_000_000.0
    picked_corpus_fpm = sum_picked_fp / total_corpus_benign * 1_000_000.0
    deployed_corpus_recall = sum_deployed_tp / total_corpus_malware
    picked_corpus_recall = sum_picked_tp / total_corpus_malware
    print(f"Corpus-wide rollup (target {target} FP/M with ≤{ceiling_fpm:.1f} FP/M slice ceiling):")
    print(f"  deployed: tp={sum_deployed_tp:>8} fp={sum_deployed_fp:>3}  recall={deployed_corpus_recall*100:.2f}%  FPR={deployed_corpus_fpm:.2f} FP/M")
    print(f"  picked:   tp={sum_picked_tp:>8} fp={sum_picked_fp:>3}  recall={picked_corpus_recall*100:.2f}%  FPR={picked_corpus_fpm:.2f} FP/M")
    print(f"  delta:    tp={sum_picked_tp - sum_deployed_tp:+8} fp={sum_picked_fp - sum_deployed_fp:+3}  recall={(picked_corpus_recall - deployed_corpus_recall)*100:+.2f}pp  FPR={picked_corpus_fpm - deployed_corpus_fpm:+.2f} FP/M")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
