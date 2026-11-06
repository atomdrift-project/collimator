#!/usr/bin/env python3
"""Publish gate: ship the staged bundle when it is better overall at L0 and L25.

Reads ``route_policy_eval_oof.json`` from the staged bundle and from the
bundle currently deployed — each bundle's deployed ensemble scored on the
locked test partition — and pools it across every filetype:

    recall(L) = sum(tp at L) / malware      fp(L) = sum(fp at L)

L0 and L25 are the operating points that ship: L0 is the quietest, L25 the
default. The rule is autocollie's measured-target rule (``target_tie.go``)
applied to both levels at once:

  * better:   at least one of L0 / L25 recall rises by more than
              ``--min-gain`` (0.1pp, autocollie's minTargetTradeoffGain), and
  * no worse: neither falls by more than ``--max-loss`` (0.2pp, autocollie's
              maxTargetTradeoffLoss), and
  * honest:   FPs at each level stay within noise of the deployed bundle's,
              so recall was not bought with false positives.

Per-filetype and per-model swings do not decide anything — a bundle that
trades a few hundred catches on one filetype for thousands elsewhere is a
better bundle. Both are printed so they can be looked at: the largest
per-filetype catch swings at each level, and every model (route) whose PR-AUC
moved, marked retrained or unchanged.

Bypass with ``AZOTH_ALLOW_REGRESSION=1`` for a reviewed trade-off. Passes
(exit 0) when the deployed bundle has no eval to compare against.

Exit codes:
  0 — better overall (or nothing to compare against); ship
  1 — not better overall; do not ship
  2 — usage / IO error
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

LEVELS = (0, 25)
EVAL_FILE = "route_policy_eval_oof.json"
# Per-filetype swings listed for context, per level and direction.
TOP_MOVES = 5
# A model (route) is listed as better or worse when its malware-weighted PR-AUC
# moves at least this much — autocollie's PR-AUC tolerance.
ROUTE_PR_AUC_MOVE = 0.001


@dataclass(frozen=True)
class Pooled:
    tp: int
    fp: int
    malware: int
    benign: int

    @property
    def recall(self) -> float:
        return self.tp / self.malware if self.malware else 0.0


def _load(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as e:
        print(f"warning: failed to load {path}: {e}", file=sys.stderr)
        return {}


def _row(entry: dict, level: int) -> dict | None:
    return ((entry or {}).get("deployed_or_by_level") or {}).get(f"L{level}_hostile")


def _pool(report: dict, level: int) -> Pooled | None:
    """Pooled counts at ``level``, or None when no filetype carries the level."""
    filetypes = report.get("filetypes") or {}
    rows = [r for r in (_row(e, level) for e in filetypes.values()) if r]
    if not rows:
        return None
    malware = report.get("malware") or sum(e.get("malware", 0) or 0 for e in filetypes.values())
    benign = report.get("benign") or sum(e.get("benign", 0) or 0 for e in filetypes.values())
    return Pooled(
        tp=sum(int(r.get("tp") or 0) for r in rows),
        fp=sum(int(r.get("fp") or 0) for r in rows),
        malware=int(malware),
        benign=int(benign),
    )


def _fp_allowance(staged: Pooled, deployed: Pooled) -> float:
    """Most FPs the staged bundle may show and still count as no worse.

    The deployed FP count rescaled to the staged benign population, plus two
    standard deviations of Poisson noise on it.
    """
    expected = deployed.fp * (staged.benign / deployed.benign) if deployed.benign else deployed.fp
    return expected + 2 * math.sqrt(max(expected, 1.0))


def _moves(staged: dict, deployed: dict, level: int) -> list[tuple[int, str, float, float]]:
    """(tp delta, filetype, deployed recall, staged recall) for every filetype in both."""
    out = []
    s_ft, d_ft = staged.get("filetypes") or {}, deployed.get("filetypes") or {}
    for ft in s_ft.keys() & d_ft.keys():
        s, d = _row(s_ft[ft], level), _row(d_ft[ft], level)
        if not s or not d:
            continue
        out.append((
            int(s.get("tp") or 0) - int(d.get("tp") or 0), ft,
            float(d.get("recall") or 0.0), float(s.get("recall") or 0.0),
        ))
    return out


def _print_moves(staged: dict, deployed: dict) -> None:
    for level in LEVELS:
        moves = _moves(staged, deployed, level)
        losses = sorted(m for m in moves if m[0] < 0)[:TOP_MOVES]
        gains = sorted((m for m in moves if m[0] > 0), reverse=True)[:TOP_MOVES]
        if not losses and not gains:
            continue
        print(f"\nlargest per-filetype moves at L{level} (informational):")
        for delta, ft, d_rec, s_rec in gains + losses:
            print(f"  {ft:<16} {delta:+7,} caught   recall {d_rec*100:6.2f}% → {s_rec*100:6.2f}%")


def _route_metrics(report: dict) -> dict[str, dict[str, tuple[float, float, int]]]:
    """{route: {filetype: (pr_auc, recall_at_0fp, malware)}} from each slice."""
    out: dict = {}
    for ft, entry in (report.get("filetypes") or {}).items():
        malware = int((entry or {}).get("malware") or 0)
        for route, m in (((entry or {}).get("slice_metrics") or {}).get("routes") or {}).items():
            if isinstance(m, dict) and m.get("pr_auc") is not None:
                out.setdefault(route, {})[ft] = (
                    float(m["pr_auc"]), float(m.get("recall_at_0fp") or 0.0), malware,
                )
    return out


def _retrained(staged_dir: Path, deployed_dir: Path) -> set[str] | None:
    """Routes whose model or feature spec changed, or None when it can't be told."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from azoth_impact import changed_routes  # noqa: PLC0415
        return changed_routes(staged_dir, deployed_dir)[0]
    except Exception as e:  # noqa: BLE001 — attribution only; never blocks
        print(f"note: could not tell which models were retrained ({e})", file=sys.stderr)
        return None


def _print_route_moves(staged: dict, deployed: dict, retrained: set[str] | None) -> None:
    """Each model's PR-AUC and zero-FP recall, malware-weighted over the filetype
    slices it scores in both bundles, listed when PR-AUC moved at least
    ROUTE_PR_AUC_MOVE. Informational: models are judged by the bundle they make."""
    s_routes, d_routes = _route_metrics(staged), _route_metrics(deployed)
    rows = []
    for route in s_routes.keys() & d_routes.keys():
        common = s_routes[route].keys() & d_routes[route].keys()
        weight = sum(s_routes[route][ft][2] for ft in common)
        if not weight:
            continue
        def avg(side, i):  # noqa: E306
            return sum(side[route][ft][i] * s_routes[route][ft][2] for ft in common) / weight
        d_auc, s_auc = avg(d_routes, 0), avg(s_routes, 0)
        if abs(s_auc - d_auc) >= ROUTE_PR_AUC_MOVE:
            rows.append((s_auc - d_auc, route, d_auc, s_auc, avg(s_routes, 1) - avg(d_routes, 1), weight))
    for title, picked in (
        ("models that got better", sorted((r for r in rows if r[0] > 0), reverse=True)),
        ("models that got worse", sorted(r for r in rows if r[0] < 0)),
    ):
        if not picked:
            continue
        print(f"\n{title} (PR-AUC moved ≥ {ROUTE_PR_AUC_MOVE}, informational):")
        width = max(len(r[1]) for r in rows)
        for delta, route, d_auc, s_auc, d_r0, weight in picked:
            tag = "" if retrained is None else ("  retrained" if route in retrained else "  unchanged model")
            print(
                f"  {route:<{width}}  PR-AUC {d_auc:.4f} → {s_auc:.4f} ({delta:+.4f})"
                f"   zero-FP recall {d_r0*100:+.2f}pp   {weight:,} malware{tag}"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--staged", type=Path, required=True)
    parser.add_argument(
        "--deployed", type=Path,
        default=Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
        / "atomdrift" / "scan" / "models" / "azoth",
    )
    parser.add_argument(
        "--min-gain", type=float, default=0.001,
        help="Recall rise (fraction) at L0 or L25 that counts as better. Default 0.001 = 0.1pp.",
    )
    parser.add_argument(
        "--max-loss", type=float, default=0.002,
        help="Largest recall fall (fraction) tolerated at L0 or L25. Default 0.002 = 0.2pp.",
    )
    args = parser.parse_args(argv)

    if os.environ.get("AZOTH_ALLOW_REGRESSION", "").strip().lower() in {"1", "true", "yes"}:
        print("AZOTH_ALLOW_REGRESSION set; skipping publish gate")
        return 0

    staged = _load(args.staged / EVAL_FILE)
    deployed = _load(args.deployed / EVAL_FILE)
    if not staged:
        print(f"error: staged bundle has no {EVAL_FILE} at {args.staged}", file=sys.stderr)
        return 2
    if not deployed:
        print(f"publish gate: no {EVAL_FILE} at {args.deployed}; nothing to compare against, passing")
        return 0

    pooled: dict[int, tuple[Pooled, Pooled]] = {}
    for level in LEVELS:
        s, d = _pool(staged, level), _pool(deployed, level)
        if s is None:
            print(f"error: staged eval has no L{level}_hostile rows", file=sys.stderr)
            return 2
        if d is None:
            print(f"publish gate: deployed eval has no L{level}_hostile rows (older grid); passing")
            return 0
        pooled[level] = (s, d)

    s0, d0 = pooled[LEVELS[0]]
    print(
        f"publish gate: staged {args.staged} vs deployed {args.deployed}\n"
        f"  test partition: {d0.malware:,} → {s0.malware:,} malware, "
        f"{d0.benign:,} → {s0.benign:,} benign"
    )
    gains: list[str] = []
    problems: list[str] = []
    for level, (s, d) in pooled.items():
        delta = s.recall - d.recall
        allowed = _fp_allowance(s, d)
        print(
            f"  L{level:<3} recall {d.recall*100:6.2f}% → {s.recall*100:6.2f}% ({delta*100:+.2f}pp)"
            f"   FP {d.fp:,} → {s.fp:,} (allowed ≤ {allowed:,.0f})"
        )
        if delta > args.min_gain:
            gains.append(f"L{level} {delta*100:+.2f}pp")
        if -delta > args.max_loss:
            problems.append(f"L{level} recall fell {-delta*100:.2f}pp (more than {args.max_loss*100:.2f}pp)")
        if s.fp > allowed:
            problems.append(f"L{level} FPs rose {d.fp:,} → {s.fp:,} (more than noise allows: ≤ {allowed:,.0f})")
    if not gains:
        problems.append(f"neither L0 nor L25 recall rose more than {args.min_gain*100:.2f}pp")

    _print_moves(staged, deployed)
    _print_route_moves(staged, deployed, _retrained(args.staged, args.deployed))
    print()
    if problems:
        print("FAIL: not better overall, not shipping —")
        for p in problems:
            print(f"  - {p}")
        print("Set AZOTH_ALLOW_REGRESSION=1 to ship anyway after review.")
        return 1
    print(
        f"PASS: better overall ({', '.join(gains)}); no level fell more than "
        f"{args.max_loss*100:.2f}pp and FPs are within noise."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
