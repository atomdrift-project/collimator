#!/usr/bin/env python3
"""Wait for a finite screen pass, retry failed routes, then full-train.

Completed experiments remain in the run history. Rejected proposals and
skipped routes are reconsidered alongside failures, allowing corrected knob
names and filetype aliases to take effect without restarting healthy work.
An interrupted or incomplete pass never triggers a continuation.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path


def recovery_routes(events: list[dict], since: str, allowed: set[str]) -> list[str]:
    active = False
    complete = False
    failures: set[str] = set()
    rejected: set[str] = set()
    skipped: set[str] = set()
    attempted: set[str] = set()
    succeeded: set[str] = set()
    for event in events:
        if event.get("ts", "") < since:
            continue
        kind = event.get("type")
        if not active:
            if kind != "pass-start":
                continue
            active = True
        payload = event.get("payload") or {}
        route = event.get("route", "")
        if kind == "pass-complete":
            if payload.get("interrupted"):
                raise ValueError("screen pass was interrupted; continuation canceled")
            complete = True
            break
        if kind == "screen-started":
            attempted.add(route)
        elif kind in {"screen-finished", "screen-already-run"}:
            succeeded.add(route)
        elif kind == "spec-rejected":
            rejected.add(route)
        elif kind == "cycle-complete":
            status = payload.get("status")
            if status == "skipped":
                skipped.add(route)
            elif status is not None:
                failures.add(route)
    if not complete:
        raise ValueError("screen pass has no completion event; continuation canceled")
    failures.update(attempted - succeeded)
    if not failures:
        # A successful original chain already owns its full-train step.
        return []
    return sorted((failures | rejected | skipped) & allowed)


def _process_identity(pid: int) -> tuple[str, str] | None:
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except FileNotFoundError:
        return None
    fields = stat[stat.rfind(")") + 2:].split()
    return fields[0], fields[19]  # process state and start time


def wait_for_exit(pid: int) -> None:
    original = _process_identity(pid)
    if original is None:
        return
    while True:
        current = _process_identity(pid)
        if current is None or current[0] in {"Z", "X"} or current[1] != original[1]:
            return
        time.sleep(30)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wait-pid", type=int, required=True)
    parser.add_argument("--since", required=True, help="UTC event timestamp or prefix")
    parser.add_argument("--plan", type=Path, default=Path("out/autocollie/three-attempt-plan.json"))
    parser.add_argument("--events", type=Path, default=Path("out/autocollie/events.jsonl"))
    args = parser.parse_args()
    if args.wait_pid <= 0:
        parser.error("--wait-pid must be positive")
    print(f"Waiting for existing pipeline PID {args.wait_pid}; completed work will be retained.", flush=True)
    wait_for_exit(args.wait_pid)
    plan = json.loads(args.plan.read_text())
    events = [json.loads(line) for line in args.events.read_text().splitlines() if line.strip()]
    try:
        routes = recovery_routes(events, args.since, set(plan["routes"]))
    except ValueError as exc:
        print(str(exc), flush=True)
        return 1
    if not routes:
        print("No failed screen cycles to recover; leaving the original chain's full-train step in charge.", flush=True)
        return 0
    path = Path("out/autocollie/recovery-plan.json")
    path.write_text(json.dumps({"since": args.since, "routes": routes}, indent=2) + "\n")
    print(f"Retrying {len(routes)} failed, rejected, or previously skipped routes, then full-training.", flush=True)
    command = [
        "make", "autocollie-full-train", "ROUTES=" + ",".join(routes), "EXPERIMENTS=2",
        f"ROUTE_CONCURRENCY={plan.get('route_concurrency', 2)}",
        f"MAX_CPU_THREADS={plan.get('max_cpu_threads', 64)}",
        f"WORKERS={plan.get('max_cpu_threads', 64)}",
        f"EXP_LGBM_THREADS={plan.get('lgbm_threads_per_fit', 8)}",
        f"AUTOCOLLIE_LLM_TIMEOUT={plan.get('llm_timeout', '30m')}",
        f"AUTOCOLLIE_SCREEN_TIMEOUT={plan.get('screen_timeout', '30m')}",
        f"AZOTH_AUTOCOLLIE_RUNS_DIR={plan.get('runs_dir', 'out/experiments/azoth/runs')}",
    ]
    return subprocess.call(command, cwd=Path(__file__).resolve().parents[1])


if __name__ == "__main__":
    raise SystemExit(main())
