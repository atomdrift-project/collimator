#!/usr/bin/env python3
"""Find autocollie screen runs that LOOK promising but never got promoted.

Scans ``out/experiments/azoth/runs/*.json`` for screen runs that:
  - have usable metrics (PR_AUC, recall@L50, holdout counts),
  - are NOT in ``promoted_baselines.json`` (or are marked retired there),
  - rank highly by apples-to-apples delta vs the deployed model.

Then re-evaluates each against the CURRENT gate logic (paired-σ, n_ben
floor, PR_AUC/AUC guardrails, saturation floor) and reports which would
pass today. Useful when gate code or thresholds have changed since the
candidate was originally screened — old runs that were rejected under
earlier rules may now look promotable.

Output is grouped by route, ranked within each route by:
  1. has-apples-to-apples (more trustworthy comparison wins)
  2. delta_r_op (the production-objective metric vs paired baseline)
  3. PR_AUC
  4. timestamp (more recent = less likely to reference dead rows)

Usage:
  python scripts/autocollie_favorites.py
  python scripts/autocollie_favorites.py --top 10
  python scripts/autocollie_favorites.py --route filetypes/pdf
  python scripts/autocollie_favorites.py --runs-dir out/experiments/azoth/runs

Phase 1 (this script) is read-only — no retraining, no state changes.
Run identified candidates manually via:
  make autocollie-confirm KEY=<key>
  # if PASS:
  make autocollie-promote KEY=<key>
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Gate logic mirrored from autocollie/cmd/autocollie/auto.go
# ---------------------------------------------------------------------------

# Mirror autocollie's constants. If these change there, update here.
AP_ELIGIBILITY_EPSILON = 0.0002
RECALL3_SIG_GATE_MIN_EPS = 0.002
RECALL3_SIG_GATE_MULTIPLIER = 2.0
MIN_BENIGN_HOLDOUT_FOR_GATE = 200
MAX_TOLERATED_AP_REGRESSION = 0.001
MAX_TOLERATED_RECALL3_REGRESSION = 0.01
MAX_TOLERATED_AUC_REGRESSION = 0.001
SATURATED_PRAUC_FLOOR = 0.999
SATURATED_RECALL3_FLOOR = 0.95
SATURATED_REL_MISS_REDUCTION_FLOOR = 0.10
PAIRED_CORRELATION_APPLES = 0.85


def recall3_sig_eligibility(
    baseline_r3: float, n_mal: int, n_ben: int, paired: bool,
) -> float:
    """Mirror of autocollie's recall3SigEligibility — same tiers."""
    effective_n = n_mal
    if n_ben > 0 and n_ben < effective_n:
        effective_n = n_ben
    if effective_n < 1:
        return RECALL3_SIG_GATE_MIN_EPS
    p = baseline_r3
    if p < 0.001:
        p = 0.001
    elif p > 0.999:
        p = 0.999
    rho = PAIRED_CORRELATION_APPLES if paired else 0.0
    sigma = math.sqrt(2.0 * p * (1.0 - p) * (1.0 - rho) / effective_n)
    if paired and effective_n >= 30:
        return max(0.0, RECALL3_SIG_GATE_MULTIPLIER * sigma)
    if effective_n < 500:
        return 1.0
    if effective_n < 2000:
        return max(0.03, 3.0 * sigma)
    if effective_n < 10000:
        return max(0.01, 2.5 * sigma)
    return max(RECALL3_SIG_GATE_MIN_EPS, RECALL3_SIG_GATE_MULTIPLIER * sigma)


def estimate_current_verdict(
    candidate: dict[str, Any], baseline: dict[str, Any] | None, paired: bool,
) -> tuple[bool, str]:
    """Mirror autoWinnerVerdict. Returns (would_pass, reason).

    ``candidate``/``baseline`` are dicts with avg_precision, roc_auc,
    recall_at_50_per_100M (or legacy recall_at_fp_per_million_3),
    n_malware_holdout, n_benign_holdout. Missing baseline means
    "first-run mode" — passes if candidate has positive metrics.
    """
    cand_ap = candidate.get("avg_precision")
    cand_auc = candidate.get("roc_auc")
    cand_r_op = _op_recall(candidate)
    n_mal = int(candidate.get("n_malware_holdout") or 0)
    n_ben = int(candidate.get("n_benign_holdout") or 0)

    if not isinstance(cand_ap, (int, float)):
        return False, "no PR_AUC recorded"

    if baseline is None or not baseline:
        # First-run mode: any positive-AP candidate is a winner.
        return True, "first successful run for route (no baseline)"

    base_ap = baseline.get("avg_precision") or 0.0
    base_auc = baseline.get("roc_auc") or 0.0
    base_r_op_val = _op_recall(baseline)
    base_r_op = base_r_op_val if base_r_op_val is not None else 0.0
    if base_ap == 0 and base_auc == 0:
        return True, "baseline has no usable metrics — first-run mode"

    d_ap = float(cand_ap) - float(base_ap)
    d_auc = (float(cand_auc) - float(base_auc)) if isinstance(cand_auc, (int, float)) else 0.0
    d_r_op = (float(cand_r_op) - base_r_op) if cand_r_op is not None else 0.0

    # Benign-holdout floor (only meaningful when n_ben was recorded).
    if n_ben > 0 and n_ben < MIN_BENIGN_HOLDOUT_FOR_GATE:
        return False, f"n_ben_holdout={n_ben} < {MIN_BENIGN_HOLDOUT_FOR_GATE} (too small for screen gate)"

    if d_auc < -MAX_TOLERATED_AUC_REGRESSION - 1e-12:
        return False, f"AUC regressed {d_auc:+.5f} > {MAX_TOLERATED_AUC_REGRESSION}"
    if d_ap < -MAX_TOLERATED_AP_REGRESSION - 1e-12:
        return False, f"PR_AUC regressed {d_ap:+.5f} > {MAX_TOLERATED_AP_REGRESSION}"
    if d_r_op < -MAX_TOLERATED_RECALL3_REGRESSION - 1e-12:
        return False, f"recall@L50 regressed {d_r_op:+.5f} > {MAX_TOLERATED_RECALL3_REGRESSION}"

    sig_eps = recall3_sig_eligibility(base_r_op, n_mal, n_ben, paired)
    pr_up = d_ap > AP_ELIGIBILITY_EPSILON
    rc_up = d_r_op > sig_eps
    if not pr_up and not rc_up:
        return False, (
            f"neither axis improved past noise: PR_AUC {d_ap:+.5f} "
            f"(need >{AP_ELIGIBILITY_EPSILON}), recall@L50 {d_r_op:+.5f} "
            f"(need >{sig_eps:.5f} at n_eff={min(n_mal, n_ben) if n_ben > 0 else n_mal}, paired={paired})"
        )

    saturated = base_ap > SATURATED_PRAUC_FLOOR and base_r_op > SATURATED_RECALL3_FLOOR
    if saturated:
        miss_base = 1.0 - base_r_op
        if miss_base > 0:
            rel_miss_reduction = d_r_op / miss_base
            if rel_miss_reduction < SATURATED_REL_MISS_REDUCTION_FLOOR:
                return False, (
                    f"saturated baseline (PR_AUC={base_ap:.5f}, r_op={base_r_op:.4f}); "
                    f"miss-reduction {rel_miss_reduction*100:+.1f}% < "
                    f"{SATURATED_REL_MISS_REDUCTION_FLOOR*100:.0f}%"
                )

    return True, (
        f"either-axis up: PR_AUC {d_ap:+.5f}, recall@L50 {d_r_op:+.5f} "
        f"(paired={paired}, n_mal={n_mal}, n_ben={n_ben})"
    )


# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------


def _is_finite(v: Any) -> bool:
    return isinstance(v, (int, float)) and not math.isnan(float(v))


def _op_recall(metrics: dict[str, Any] | None) -> float | None:
    """Operating-point recall: prefers L50 (per-100M), falls back to legacy L3.

    The selection metric is now ``recall_at_50_per_100M`` (L50 = 0.5 FP/M);
    older run JSONs only carry ``recall_at_fp_per_million_3`` (L3 = 3 FP/M)
    so we fall back to that to keep history readable. Returns None when
    neither field is present or both are NaN.
    """
    if not metrics:
        return None
    for key in ("recall_at_50_per_100M", "recall_at_fp_per_million_3"):
        v = metrics.get(key)
        if _is_finite(v):
            return float(v)
    return None


def load_promoted(baselines_path: Path) -> set[str]:
    """Return the set of run keys (promote_key + full_train_key) already
    promoted AND not retired. Retired entries are excluded so favorites
    can re-surface candidates that were demoted."""
    if not baselines_path.is_file():
        return set()
    try:
        data = json.loads(baselines_path.read_text())
    except (OSError, ValueError):
        return set()
    keys: set[str] = set()
    for entry in (data.get("routes") or {}).values():
        if not isinstance(entry, dict):
            continue
        if entry.get("retired_at"):
            continue  # retired entries should not block their runs from re-surfacing
        for k in ("promote_key", "full_train_key"):
            v = entry.get(k)
            if isinstance(v, str) and v:
                keys.add(v)
    return keys


def extract_run_record(path: Path) -> dict[str, Any] | None:
    """Pull the gate-relevant fields from a run JSON. Returns None when
    the run lacks the minimum needed to estimate a verdict."""
    try:
        run = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    route = run.get("route")
    if not isinstance(route, str):
        return None
    metrics = run.get("sampled_test_metrics") or {}
    ap = metrics.get("avg_precision")
    if not _is_finite(ap):
        return None
    r_op = _op_recall(metrics)
    n_mal = metrics.get("n_malware_holdout")
    n_ben = metrics.get("n_benign_holdout")
    if not (_is_finite(n_mal) and _is_finite(n_ben)):
        return None
    deployed = run.get("deployed_on_same_data") or {}
    has_apples = (
        _op_recall(deployed) is not None
        and int(deployed.get("n_malware", 0) or 0) >= 1
        and int(deployed.get("n_benign", 0) or 0) >= 1
    )
    return {
        "path": str(path),
        "route": route,
        "key": str(run.get("experiment_key") or path.stem),
        "ts": str(run.get("timestamp") or ""),
        "idea": str(run.get("idea") or ""),
        "candidate": {
            "avg_precision": float(ap),
            "roc_auc": float(metrics.get("roc_auc") or 0.0) if _is_finite(metrics.get("roc_auc")) else None,
            # Canonical: per-100M field. Carry L50 in the output dict so
            # downstream consumers see the new schema name.
            "recall_at_50_per_100M": r_op if r_op is not None else 0.0,
            "n_malware_holdout": int(n_mal),
            "n_benign_holdout": int(n_ben),
        },
        "baseline": deployed if has_apples else None,
        "has_apples": has_apples,
        "train_config": run.get("train_config") or {},
    }


def ranking_key(record: dict[str, Any]) -> tuple[int, float, float, str]:
    cand = record["candidate"]
    base = record["baseline"] or {}
    cand_r_op = cand.get("recall_at_50_per_100M", 0.0)
    base_r_op_val = _op_recall(base)
    base_r_op = base_r_op_val if base_r_op_val is not None else 0.0
    delta_r_op = cand_r_op - base_r_op
    return (
        1 if record["has_apples"] else 0,
        delta_r_op,
        cand["avg_precision"],
        record["ts"],
    )


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def dedup_by_idea(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only the highest-ranked record for each (route, idea) pair.

    Autocollie re-proposes the same idea (literally the same idea string)
    across many cycles — same spec, slightly different cached row IDs,
    sometimes re-run after the corpus grew. Without dedup the top-N
    report fills up with near-identical rows for `native_kv_vocab_15k`
    when really there's only one config to consider.

    Dedup happens AFTER ranking so the kept instance is the strongest
    signal we have for that idea — the run with the freshest apples-to-
    apples baseline OR the biggest delta_r_op.
    """
    best_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for rec in records:
        key = (rec["route"], rec["idea"])
        prev = best_by_key.get(key)
        if prev is None or ranking_key(rec) > ranking_key(prev):
            best_by_key[key] = rec
    return list(best_by_key.values())


def load_replay_history(history_path: Path) -> dict[str, dict[str, Any]]:
    """Return ``{key: {last_ts, last_outcome, last_reason, attempts: [...]}}``.

    Empty dict if no history file. Used both for display (show "last
    rejected DD/MM why") and for the replay-plan ordering (skip
    candidates that recently failed — no point burning cycles on the
    same key in a loop).
    """
    if not history_path.is_file():
        return {}
    try:
        data = json.loads(history_path.read_text())
    except (OSError, ValueError):
        return {}
    return (data.get("attempts") or {}) if isinstance(data, dict) else {}


def replay_score(record: dict[str, Any]) -> tuple:
    """Global ranking for replay ordering. Higher = try sooner.

    Composite: apples-to-apples first (more trustworthy comparison),
    then absolute recall@L50 delta (biggest wins first), then
    log(n_benign_holdout) (more reliable measurement). Recency as
    tiebreaker so a fresh run beats a stale one with the same metrics.
    """
    cand = record["candidate"]
    base = record["baseline"] or {}
    base_r_op_val = _op_recall(base)
    base_r_op = base_r_op_val if base_r_op_val is not None else 0.0
    delta_r_op = cand.get("recall_at_50_per_100M", 0.0) - base_r_op
    n_ben = cand.get("n_benign_holdout", 0)
    log_ben = math.log10(max(n_ben, 1))
    return (
        1 if record["has_apples"] else 0,
        delta_r_op,
        log_ben,
        record["ts"],
    )


def render(records: list[dict[str, Any]], top: int, route_filter: str | None,
           history: dict[str, dict[str, Any]] | None = None) -> None:
    records = dedup_by_idea(records)
    by_route: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rec in records:
        if route_filter and rec["route"] != route_filter:
            continue
        by_route[rec["route"]].append(rec)
    if not by_route:
        if route_filter:
            print(f"No favorites found for route {route_filter!r}.")
        else:
            print("No favorites found.")
        return
    print(f"# autocollie favorites — top {top} per route")
    if route_filter:
        print(f"#   filtered to route: {route_filter}")
    print()
    routes_sorted = sorted(by_route.keys())
    for route in routes_sorted:
        recs = sorted(by_route[route], key=ranking_key, reverse=True)[:top]
        print(f"## {route}  ({len(by_route[route])} eligible run(s))")
        print(f"{'#':>3} {'idea':<40} {'key':<18} {'ts':<19} "
              f"{'apples':<6} {'d_r_op':>8} {'n_ben':>6} {'last replay':<22} verdict")
        for i, rec in enumerate(recs, 1):
            paired = rec["has_apples"]
            ok, reason = estimate_current_verdict(rec["candidate"], rec["baseline"], paired)
            base_r_op_val = _op_recall(rec["baseline"] or {})
            base_r_op = base_r_op_val if base_r_op_val is not None else 0.0
            d_r_op = rec["candidate"]["recall_at_50_per_100M"] - base_r_op
            verdict_prefix = "✓" if ok else "✗"
            # Replay-history column: show last attempt outcome if recorded.
            # Lets the operator avoid burning cycles on candidates that
            # already failed promote recently for a non-fixable reason.
            replay_col = "-"
            if history and rec["key"] in history:
                h = history[rec["key"]]
                last_outcome = (h.get("last_outcome") or "?")[:8]
                last_ts = (h.get("last_ts") or "")[:10]
                replay_col = f"{last_ts} {last_outcome}"
            print(
                f"{i:>3} {rec['idea'][:40]:<40} {rec['key'][:18]:<18} "
                f"{rec['ts'][:19]:<19} "
                f"{'yes' if paired else 'no':<6} "
                f"{d_r_op*100:+7.2f}pp "
                f"{rec['candidate']['n_benign_holdout']:>6} "
                f"{replay_col:<22} "
                f"{verdict_prefix} {reason[:90]}"
            )
            # Show the last rejection reason on a second line if recent.
            if history and rec["key"] in history:
                h = history[rec["key"]]
                last_reason = (h.get("last_reason") or "").strip()
                if last_reason:
                    print(f"      ↳ last: {last_reason[:140]}")
        print()
    print("To replay any candidate (after rebuild + restart):")
    print("  make autocollie-confirm KEY=<key>")
    print("  # if confirm passes:")
    print("  make autocollie-promote KEY=<key>")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs-dir", type=Path, default=Path("out/experiments/azoth/runs"))
    parser.add_argument("--baselines",
                        type=Path,
                        default=Path("out/models/azoth/.autocollie/promoted_baselines.json"),
                        help="Path to promoted_baselines.json — runs referenced "
                             "here (full_train_key or promote_key) are EXCLUDED "
                             "from the favorites list unless their entry is retired.")
    parser.add_argument("--top", type=int, default=10,
                        help="Top N candidates per route (default 10).")
    parser.add_argument("--route", default=None,
                        help="If set, only consider this exact route "
                             "(e.g., 'filetypes/pdf' or 'filegroups/source').")
    parser.add_argument("--include-promoted", action="store_true",
                        help="Don't exclude runs that are already in "
                             "promoted_baselines.json. Useful for sanity-"
                             "checking the picker.")
    parser.add_argument("--require-apples", action="store_true",
                        help="Only consider runs with apples-to-apples "
                             "(deployed_on_same_data) baseline scoring. "
                             "Drops noise from legacy runs at the cost of "
                             "missing older candidates.")
    parser.add_argument("--history",
                        type=Path,
                        default=Path("out/autocollie/replay_history.json"),
                        help="Path to replay-attempt history written by "
                             "`make autocollie-replay-favorites`. Shown "
                             "in the report so operators can see which "
                             "candidates already failed promote and why.")
    parser.add_argument("--replay-plan", action="store_true",
                        help="Instead of the human-readable per-route "
                             "report, emit a globally-ranked list of "
                             "(key, route) lines suitable for piping to a "
                             "Make target. Only ✓-verdict candidates are "
                             "included, ordered by replay_score. "
                             "Candidates that recently failed promote "
                             "(within --replay-cooldown days) are dropped.")
    parser.add_argument("--replay-cooldown", type=float, default=2.0,
                        help="When emitting --replay-plan, exclude "
                             "candidates whose most-recent failed attempt "
                             "is less than N days ago. Default 2.0. "
                             "0 disables.")
    args = parser.parse_args()

    if not args.runs_dir.is_dir():
        print(f"error: runs dir {args.runs_dir} not found", file=sys.stderr)
        return 2

    promoted = set() if args.include_promoted else load_promoted(args.baselines)

    records: list[dict[str, Any]] = []
    scanned = 0
    for path in sorted(args.runs_dir.glob("*.json")):
        if path.name.endswith("_feature_spec.json"):
            continue
        scanned += 1
        rec = extract_run_record(path)
        if rec is None:
            continue
        if rec["key"] in promoted:
            continue
        if args.require_apples and not rec["has_apples"]:
            continue
        records.append(rec)

    history = load_replay_history(args.history)

    if args.replay_plan:
        # Globally-rank and emit just the keys suitable for shell-iteration.
        # Filter to ✓-verdict candidates only; further drop ones whose last
        # replay attempt failed within the cooldown window. Per-route dedup
        # so we don't queue the same idea twice.
        from datetime import datetime, timezone, timedelta  # noqa: PLC0415
        records = dedup_by_idea(records)
        if args.route:
            records = [r for r in records if r["route"] == args.route]
        # Score and filter
        eligible: list[tuple[tuple, dict[str, Any]]] = []
        cooldown_cutoff = None
        if args.replay_cooldown > 0:
            cooldown_cutoff = datetime.now(timezone.utc) - timedelta(days=args.replay_cooldown)
        for rec in records:
            paired = rec["has_apples"]
            ok, _ = estimate_current_verdict(rec["candidate"], rec["baseline"], paired)
            if not ok:
                continue
            if rec["key"] in history:
                h = history[rec["key"]]
                last_ts = h.get("last_ts") or ""
                last_outcome = (h.get("last_outcome") or "").lower()
                # Already-promoted candidates: skip outright, regardless of
                # cooldown. Once a key passed confirm + promote it landed
                # the win — re-replaying it just churns the bundle.
                # The fact that promoted_baselines.json only stores ONE
                # entry per route means that earlier-promoted-but-since-
                # overwritten keys would otherwise re-surface here (the
                # 2026-05-25 bug: 3 filetypes/c candidates all promoted,
                # only the LATEST was in promoted_baselines, the other
                # two looked "unpromoted" to the favorites filter).
                if last_outcome == "promoted":
                    continue
                # Failed candidates: skip if within cooldown window.
                if cooldown_cutoff and last_outcome in ("rejected", "confirm-failed", "promote-failed", "error"):
                    try:
                        ts = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
                        if ts.tzinfo is None:
                            ts = ts.replace(tzinfo=timezone.utc)
                        if ts >= cooldown_cutoff:
                            continue  # too soon to retry this one
                    except ValueError:
                        pass
            eligible.append((replay_score(rec), rec))
        eligible.sort(key=lambda x: x[0], reverse=True)
        # Top N per route, but emit globally ranked.
        per_route_count: dict[str, int] = {}
        emitted = 0
        for _, rec in eligible:
            n = per_route_count.get(rec["route"], 0)
            if n >= args.top:
                continue
            per_route_count[rec["route"]] = n + 1
            print(f"{rec['key']}\t{rec['route']}\t{rec['idea']}")
            emitted += 1
        print(f"# emitted {emitted} candidates (top {args.top} per route, "
              f"cooldown {args.replay_cooldown} days)", file=sys.stderr)
        return 0

    print(f"# scanned {scanned} run JSONs; {len(records)} eligible "
          f"(promoted-excluded={len(promoted)}, apples-required={args.require_apples})")
    if history:
        print(f"# replay history loaded: {len(history)} prior attempt(s)")
    print()

    render(records, args.top, args.route, history=history)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
