#!/usr/bin/env python3
"""Gate: assert the FP LEVELS are accurate — at level L (target L FP/100M) the
measured FP must stay within the level's budget. The levels are the user-facing
dial for acceptable false-positive rate, so a model that emits far more FP than
the level promises silently breaks that contract (the deployed model sits ~60x
over budget globally).

Allowed FP at level L over N benigns:  floor(N * L / 1e8) + (1 if L>0 else 0)

The +1 is a single-FP slack so tiny routes (where one FP already blows the
nominal rate) tolerate noise; for large N / high L the rate term dominates and
statistical significance takes over. One-sided: OVER budget blocks (the
production hazard); UNDER is safe. Measured on the held-out test partition and,
above all, on the GLOBAL pool (the most data we have without overfitting).
"""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path


def _allowed(n_benign: int, level: float) -> int:
    if level <= 0:
        return 0
    return math.floor(n_benign * level / 1e8) + 1


def _scan(level_fp, n_benign, label, out):
    """level_fp: list of (level, measured_fp). Returns list of violations."""
    bad = []
    for level, fp in level_fp:
        allowed = _allowed(n_benign, level)
        if fp > allowed:
            bad.append((level, fp, allowed))
    if bad:
        out.append(f"  {label} (N={n_benign:,} benign): {len(bad)} level(s) over budget:")
        for level, fp, allowed in bad[:6]:
            out.append(f"     L{level}: {fp} FP > {allowed} allowed (= floor(N*L/1e8)+1)")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--azoth-root", required=True, type=Path)
    ap.add_argument("--per-route", action="store_true",
                    help="also gate each filetype route (noise-tolerant via +1 slack)")
    a = ap.parse_args()
    out: list[str] = []
    any_bad = False

    gp = a.azoth_root / "global_policy_metrics.json"
    if gp.exists():
        d = json.loads(gp.read_text())
        nb = d.get("benign", 0)
        lf = [(L["level"], L["hostile"]["fp"]) for L in d.get("levels", [])
              if "hostile" in L and "fp" in L["hostile"]]
        any_bad |= bool(_scan(lf, nb, "GLOBAL", out))
    else:
        out.append("  GLOBAL: global_policy_metrics.json absent (bundle ships only .md) — per-route only")

    if a.per_route:
        rp = a.azoth_root / "route_policy_eval_oof.json"
        if rp.exists():
            d = json.loads(rp.read_text())
            for route, v in (d.get("filetypes", {})).items():
                nb = v.get("benign", 0)
                bl = v.get("deployed_or_by_level")
                if not isinstance(bl, dict) or not nb:
                    continue
                lf = []
                for key, m in bl.items():
                    num = "".join(c for c in key.split("_")[0] if c.isdigit())
                    if num and isinstance(m, dict) and "fp" in m:
                        lf.append((int(num), m["fp"]))
                any_bad |= bool(_scan(lf, nb, f"route {route}", out))

    if any_bad:
        print("FP-ACCURACY GATE: FAIL")
        print("\n".join(out))
        return 1
    print("FP-ACCURACY GATE: PASS — all levels within budget (floor(N*L/1e8)+1)")
    if out:
        print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
