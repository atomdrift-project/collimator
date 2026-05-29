#!/usr/bin/env python3
"""Record the outcome of a replay attempt (confirm or promote) into the
replay-history file. Used by ``make autocollie-replay-favorites`` to
build up a record of which candidates have been retried, when, and why
they failed. The favorites report then shows this history so operators
can avoid burning cycles on candidates that recently failed for
non-fixable reasons.

Usage:
  python scripts/autocollie_record_replay.py \\
      --key abc123def456 \\
      --outcome rejected \\
      --reason "LWM gate: 3 filetypes regressed"

Outcomes (free-form, but conventional values):
  promoted          — replay made it through confirm + promote → deploy
  confirm-failed    — confirm rejected (seed-spread or PR_AUC regression)
  rejected          — promote ran but azoth-validate / regression check rejected
  error             — unexpected crash; reason captures the tail
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def detect_outcome_from_logs(
    confirm_log: Path | None, promote_log: Path | None,
) -> tuple[str, str]:
    """Detect (outcome, reason) by inspecting confirm/promote log content.

    Replaces the brittle Makefile-side grep logic. Returns one of:
      (promoted, "passed confirm + promote")
      (confirm-failed, "<first FAIL line>")
      (rejected, "blocked by: <gate(s)>")
      (error, "<tail of latest log>")

    Used by --auto-detect so the recipe doesn't need to interpret
    make-vs-tee exit codes (which got the previous version wrong: make
    autocollie-promote returns non-zero on LEGITIMATE REJECTED outcomes,
    but `make | tee` returns tee's status [0], so the `if !` branch never
    fired and rejected outcomes intermittently got recorded as "promoted").
    """
    def _read_tail(p: Path | None, max_lines: int = 5) -> str:
        if not p or not p.is_file():
            return ""
        try:
            lines = p.read_text(errors="replace").splitlines()
        except OSError:
            return ""
        return " | ".join(lines[-max_lines:]).strip()

    confirm_text = confirm_log.read_text(errors="replace") if confirm_log and confirm_log.is_file() else ""
    promote_text = promote_log.read_text(errors="replace") if promote_log and promote_log.is_file() else ""

    # Confirm failed — caught at confirm stage, never reached promote.
    for line in confirm_text.splitlines():
        if "=== confirm " in line and ": FAIL ===" in line:
            return ("confirm-failed", line.strip())

    # Promote attempted — look for PASS or REJECTED in promote log.
    for line in promote_text.splitlines():
        if "=== promote " in line and ": PASS ===" in line:
            return ("promoted", "passed confirm + promote")
        if "=== promote " in line and ": REJECTED ===" in line:
            # Pull the blocked-by line if present for the most actionable reason.
            for r_line in promote_text.splitlines():
                stripped = r_line.strip()
                if stripped.startswith("blocked by:"):
                    return ("rejected", stripped)
            return ("rejected", "promote rejected (no 'blocked by' line in log)")

    # Neither pattern present — crash or unexpected early exit.
    tail = _read_tail(promote_log) or _read_tail(confirm_log)
    return ("error", f"no outcome marker in logs; tail: {tail[:300]}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", required=True)
    parser.add_argument("--outcome", default=None,
                        choices=["promoted", "confirm-failed", "rejected",
                                 "promote-failed", "error"],
                        help="Explicit outcome. Mutually exclusive with --auto-detect.")
    parser.add_argument("--auto-detect", action="store_true",
                        help="Determine outcome by parsing --confirm-log "
                             "and --promote-log instead of trusting --outcome. "
                             "Used by the replay-favorites recipe so the "
                             "Makefile doesn't need to know about specific "
                             "exit-code semantics.")
    parser.add_argument("--confirm-log", type=Path, default=None)
    parser.add_argument("--promote-log", type=Path, default=None)
    parser.add_argument("--reason", default="")
    parser.add_argument("--route", default="")
    parser.add_argument("--history",
                        type=Path,
                        default=Path("out/autocollie/replay_history.json"))
    args = parser.parse_args()

    if args.auto_detect:
        outcome, reason = detect_outcome_from_logs(args.confirm_log, args.promote_log)
        # Operator-provided --reason wins over auto-detected if both set.
        if args.reason:
            reason = args.reason
        args.outcome = outcome
        args.reason = reason
    elif args.outcome is None:
        print("error: must pass either --outcome or --auto-detect", file=__import__("sys").stderr)
        return 2

    args.history.parent.mkdir(parents=True, exist_ok=True)
    if args.history.is_file():
        try:
            data = json.loads(args.history.read_text())
        except (OSError, ValueError):
            data = {}
    else:
        data = {}
    if not isinstance(data, dict):
        data = {}
    attempts = data.setdefault("attempts", {})
    entry = attempts.setdefault(args.key, {})
    now = datetime.now(timezone.utc).isoformat()
    entry["last_ts"] = now
    entry["last_outcome"] = args.outcome
    entry["last_reason"] = args.reason[:500]  # truncate; full reason in logs
    if args.route:
        entry["route"] = args.route
    history = entry.setdefault("attempts", [])
    history.append({
        "ts": now,
        "outcome": args.outcome,
        "reason": args.reason[:500],
    })
    # Atomic write so a partial-write doesn't corrupt the file under
    # concurrent replays.
    tmp = args.history.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(args.history)
    print(f"recorded {args.outcome} for {args.key[:16]} ({args.reason[:80]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
