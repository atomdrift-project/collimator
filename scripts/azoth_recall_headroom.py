#!/usr/bin/env python3
"""Per-filetype recall headroom diagnostic — where's the upside?

For each filetype in the deployed bundle's ``route_policy_eval_oof.json``,
emits a one-line digest covering:

  - The CURRENT deploy point (L3 hostile OR-rule recall).
  - The BEST AVAILABLE route at the same FP budget (what we'd get if we
    just picked the single strongest specialist for this slice).
  - The PR-AUC ceiling for that best route (a separability proxy — if it's
    near 1.0 the model can rank perfectly; recall@3FP shortfalls are
    score-distribution-tail problems, not learning capacity).
  - Absolute miss count = (1 - recall@L3) * n_malware — how many malware
    samples we're leaving on the table at the current operating point.
  - A diagnosis tag:
      * "or_loses"      — current OR is below the best single route at
                          its own FP budget; combiner is the bottleneck.
      * "saturated_pr"  — best route PR-AUC > 0.99 AND recall@3FP < 0.9.
                          Ranking is fine; the score tail is crowded
                          (benigns and malware mix at very high probs).
                          Knob-tuning won't help; need new features or
                          hard-negative mining.
      * "low_pr"        — best route PR-AUC < 0.99. Learning capacity
                          short; autocollie can probably help.
      * "limited_data"  — n_malware < 1000 OR n_benign < 500. Anything
                          we learn here will overfit or hit GPD-
                          extrapolation resolution limits; need more
                          samples before tuning. (The n_benign floor
                          matters because the "best@3FP" number on a
                          small-benign slice is really "best at 1 FP
                          out of n_benign" — wildly above 3 FP/M when
                          n_benign is small. xlsx with 12 benigns is
                          the canonical case.)

Sorted by absolute miss count (highest first) — the table reads as a
priority list.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def _safe(x: Any) -> float:
    try:
        f = float(x)
        return f if math.isfinite(f) else math.nan
    except (TypeError, ValueError):
        return math.nan


def _best_single_route_at_fp(slice_routes: dict, fp_target: int) -> tuple[str, float, float]:
    """Pick the single route with the highest recall@<fp_target>fp.
    Returns (route_name, recall, pr_auc). NaN values lose to numeric."""
    best_name = "?"
    best_recall = math.nan
    best_pr = math.nan
    for name, m in slice_routes.items():
        if not isinstance(m, dict):
            continue
        r = _safe(m.get(f"recall_at_{fp_target}fp"))
        if math.isnan(r):
            continue
        if math.isnan(best_recall) or r > best_recall:
            best_recall = r
            best_name = name
            best_pr = _safe(m.get("pr_auc"))
    return best_name, best_recall, best_pr


def _diagnose(
    *,
    n_mal: int,
    n_ben: int,
    or_recall_l3: float,
    best_recall_3: float,
    best_pr: float,
) -> str:
    # n_benign < 500 means recall@3FP is on a slice where the per-slice
    # 3 FP/M budget rounds to max(1, 0) = 1 FP, which is >> 3 FP/M in
    # rate. The "headroom" is then a measurement artifact of the small
    # benign tail, not a real operating point we could deploy at.
    if n_mal < 1000 or n_ben < 500:
        return "limited_data"
    # The OR rule combines multiple routes — if it's losing to the single
    # best route at the same FP budget, the combiner is the issue.
    if not math.isnan(or_recall_l3) and not math.isnan(best_recall_3):
        if best_recall_3 - or_recall_l3 > 0.02:
            return "or_loses"
    if math.isnan(best_pr):
        return "no_pr_auc"
    if best_pr > 0.99 and not math.isnan(best_recall_3) and best_recall_3 < 0.9:
        return "saturated_pr"
    if best_pr < 0.99:
        return "low_pr"
    return "near_ceiling"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--eval", type=Path,
        default=Path("out/models/azoth/route_policy_eval_oof.json"),
        help="Path to route_policy_eval_oof.json",
    )
    p.add_argument(
        "--output-md", type=Path, default=None,
        help="Optional path to write a markdown report (default: stdout only)",
    )
    p.add_argument(
        "--top", type=int, default=0,
        help="Show only the top N filetypes by miss count (0 = all)",
    )
    args = p.parse_args()

    payload = json.loads(args.eval.read_text())
    fts = payload.get("filetypes") or {}

    rows: list[dict[str, Any]] = []
    for ft, e in fts.items():
        n_mal = int(e.get("malware") or 0)
        n_ben = int(e.get("benign") or 0)
        if n_mal < 1 or n_ben < 1:
            continue
        slice_routes = ((e.get("slice_metrics") or {}).get("routes") or {})

        # Current deploy operating point: L3 hostile OR-rule.
        l3 = (e.get("deployed_or_by_level") or {}).get("L3_hostile") or {}
        or_recall_l3 = _safe(l3.get("recall"))
        active_routes = l3.get("active_routes") or []

        # Best single route at the deploy FP budget (3 FP/M).
        best_name_3, best_recall_3, best_pr = _best_single_route_at_fp(slice_routes, 3)
        _, best_recall_0, _ = _best_single_route_at_fp(slice_routes, 0)

        # Headroom proxies.
        miss = math.nan if math.isnan(or_recall_l3) else (1.0 - or_recall_l3) * n_mal
        single_vs_or = math.nan if (math.isnan(best_recall_3) or math.isnan(or_recall_l3)) else best_recall_3 - or_recall_l3
        diag = _diagnose(
            n_mal=n_mal,
            n_ben=n_ben,
            or_recall_l3=or_recall_l3,
            best_recall_3=best_recall_3,
            best_pr=best_pr,
        )
        rows.append({
            "filetype": ft,
            "filegroup": e.get("file_group") or "?",
            "n_mal": n_mal,
            "n_ben": n_ben,
            "or_recall_l3": or_recall_l3,
            "best_recall_3": best_recall_3,
            "best_recall_0": best_recall_0,
            "best_route_3": best_name_3,
            "best_pr": best_pr,
            "miss": miss,
            "single_vs_or": single_vs_or,
            "diag": diag,
            "active_routes": active_routes,
        })

    # Sort by absolute miss count (NaN sinks to bottom).
    rows.sort(key=lambda r: (-r["miss"] if not math.isnan(r["miss"]) else -math.inf), reverse=False)
    rows = [r for r in rows if not math.isnan(r["miss"])] + [r for r in rows if math.isnan(r["miss"])]
    rows.sort(key=lambda r: (-r["miss"] if not math.isnan(r["miss"]) else math.inf))
    if args.top > 0:
        rows = rows[: args.top]

    # Header.
    hdr = (
        f"{'filetype':<16} {'group':<12} {'n_mal':>8} "
        f"{'recall@L3':>10} {'best@3FP':>10} {'best@0FP':>10} "
        f"{'PR-AUC':>8} {'miss':>9} {'single-OR':>10} "
        f"{'diag':<14} {'best_route':<22}"
    )
    sep = "-" * len(hdr)

    def _fmt_pct(x: float) -> str:
        return "  .  " if math.isnan(x) else f"{x*100:6.2f}%"

    def _fmt_int(x: float) -> str:
        return "  .  " if math.isnan(x) else f"{int(x):8d}"

    lines = [hdr, sep]
    for r in rows:
        lines.append(
            f"{r['filetype']:<16} {r['filegroup']:<12} {r['n_mal']:>8} "
            f"{_fmt_pct(r['or_recall_l3']):>10} {_fmt_pct(r['best_recall_3']):>10} "
            f"{_fmt_pct(r['best_recall_0']):>10} "
            f"{_safe(r['best_pr']):>8.4f} {_fmt_int(r['miss']):>9} "
            f"{_fmt_pct(r['single_vs_or']):>10} "
            f"{r['diag']:<14} {r['best_route_3']:<22}"
        )

    report = "\n".join(lines)
    print(report)

    # Top-of-diagnosis summary.
    print()
    diag_buckets: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        diag_buckets.setdefault(r["diag"], []).append(r)
    print("Diagnosis breakdown (count, total miss):")
    for diag, group in sorted(
        diag_buckets.items(),
        key=lambda kv: -sum(g["miss"] for g in kv[1] if not math.isnan(g["miss"])),
    ):
        total_miss = sum(g["miss"] for g in group if not math.isnan(g["miss"]))
        examples = ", ".join(g["filetype"] for g in group[:5])
        print(f"  {diag:<14} {len(group):>3} filetypes, ~{int(total_miss):>7} malware missed  e.g. {examples}")

    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(
            "# Recall Headroom\n\n"
            "```\n" + report + "\n```\n\n"
            "## Diagnosis legend\n\n"
            "- **or_loses** — the deployed OR-rule combiner is below the single best route at its own FP budget; the combiner is the bottleneck.\n"
            "- **saturated_pr** — PR-AUC > 0.99 but recall@3FP < 0.9. Ranking is good; the issue is the high-confidence score tail is crowded with hard benigns. Needs new features or hard-negative mining, not knob-tuning.\n"
            "- **low_pr** — PR-AUC < 0.99. Learning capacity is short. Autocollie can likely move the needle.\n"
            "- **limited_data** — n_malware < 1000. Will overfit before learning anything generalizable. Need more samples first.\n"
            "- **near_ceiling** — PR-AUC saturated AND recall@3FP > 0.9. Diminishing returns.\n",
        )
        print(f"\nwrote markdown to {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
