#!/usr/bin/env python3
"""Run the full training/validation pipeline on an isolated hash sample."""

import argparse
from contextlib import ExitStack, contextmanager
from datetime import datetime
import fcntl
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import threading
import time
import uuid

from collimator.data import sample_predicate
from collimator.profiling import event, phase

ROOT = Path(__file__).resolve().parents[1]


def cancel_queries(db, env):
    if not db.startswith(("postgres://", "postgresql://")):
        return
    try:
        import psycopg
        with psycopg.connect(db, connect_timeout=3, autocommit=True,
                             application_name="collimator-profile-cleanup",
                             options="-c statement_timeout=2000") as conn:
            rows = conn.execute(
                "SELECT pg_cancel_backend(pid) FROM pg_stat_activity "
                "WHERE application_name=%s AND state='active'", (env["PGAPPNAME"],),
            ).fetchall()
        if rows:
            print(f"[timing] cancelled {sum(bool(row[0]) for row in rows)} remaining run queries", flush=True)
    except Exception as exc:
        event("pipeline.cleanup", "unavailable", error_type=type(exc).__name__)


@contextmanager
def monitor(db, env, target_seconds):
    """Low-frequency server wait samples; never log SQL or connection secrets."""
    stop = threading.Event()
    started = time.monotonic()

    def sample():
        while not stop.is_set():
            elapsed = time.monotonic() - started
            states = []
            if db.startswith(("postgres://", "postgresql://")):
                try:
                    import psycopg
                    with psycopg.connect(db, connect_timeout=3, autocommit=True,
                                         application_name="collimator-profile-monitor",
                                         options="-c statement_timeout=2000") as conn:
                        rows = conn.execute(
                            "SELECT state, wait_event_type, wait_event, count(*), "
                            "max(extract(epoch FROM clock_timestamp()-query_start)) "
                            "FROM pg_stat_activity WHERE application_name=%s "
                            "AND state IS DISTINCT FROM 'idle' GROUP BY 1,2,3",
                            (env["PGAPPNAME"],),
                        ).fetchall()
                    states = [dict(state=s, wait_type=t, wait=w, backends=n,
                                   oldest_query_seconds=float(age or 0)) for s,t,w,n,age in rows]
                except Exception as exc:
                    # Monitoring must not break training, or expose a DSN in an error.
                    event("pipeline.monitor", "unavailable", error_type=type(exc).__name__)
            event("pipeline.monitor", "sample", elapsed_seconds=elapsed, database=states)
            print(f"[timing] pipeline {elapsed:.0f}s / {target_seconds:.0f}s target; "
                  f"DB states={states}", flush=True)
            if stop.wait(30):
                break

    worker = threading.Thread(target=sample, name="profile-monitor", daemon=True)
    worker.start()
    try:
        yield
    finally:
        stop.set()
        worker.join(timeout=6)
        cancel_queries(db, env)


def plan(args):
    predicate = sample_predicate(args.percent)
    small_sample = float(args.percent) <= 2
    run = (args.output or ROOT / "out/profiles" /
           f"azoth-{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}").resolve()
    if any(c.isspace() for c in str(run)):
        raise ValueError("profile output path cannot contain whitespace (Makefile paths)")
    # Prevent ambient Make overrides from sending sampled artifacts into live
    # directories. Selected model configurations are still read from history.
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("AZOTH_", "EXP_", "COLLIMATOR_", "PUBLISH_", "DEPLOY_"))
           and key not in ("MAKEFLAGS", "MFLAGS", "MAKEOVERRIDES", "OUT_ROOT", "OUT_DIR",
                           "START_STAGE", "STOP_STAGE", "PARALLEL_CHAINS", "PARALLEL_FOLDS")}
    env.update(
        COLLIMATOR_SAMPLE_PERCENT=args.percent, PYTHONUNBUFFERED="1",
        COLLIMATOR_MEM_CEILING_GB="112", AZOTH_VALIDATE_ONLY="1",
        AZOTH_PIPELINE_RESUME="0", STOP_STAGE=str(args.stop_stage),
        MEM_LOG=str(run / "memory.log"),
        COLLIMATOR_TIMING_DIR=str(run / "timings"),
        PGAPPNAME=f"collimator-profile-{run.name}"[:63],
        # Measured 1% specialist peaks were <=4.1 GiB with six fetch workers.
        # Use a margin and fewer fetchers per fit, retaining live admission
        # and the hard memory scope. Full-size profiling keeps normal defaults.
        AZOTH_MEM_PER_FIT_GB=str(args.fit_memory_gb or (8 if small_sample else 28)),
        AZOTH_EXTRACT_WORKERS_MAX=str(args.extract_workers_per_fit or (4 if small_sample else 6)),
    )
    if args.profiler == "cprofile":
        env["COLLIMATOR_PROFILE_DIR"] = str(run / "cpu")
    python = shlex.quote(sys.executable)
    # Keep wall timings with cProfile disabled as well.
    python += " " + shlex.quote(str(ROOT / "scripts/profile_python.py"))
    variables = {
        "DB": args.db, "WORKERS": str(args.workers), "PYTHON": python,
        "MODEL": "azoth", "OUT_ROOT": str(run / "models"),
        "AZOTH_ROOT": str(run / "models/azoth"),
        "EXP_OUT_DIR": str(run / "experiments/prod"),
        "AZOTH_FOLD_A_EXP_OUT_DIR": str(run / "experiments/fold-a"),
        "AZOTH_FOLD_B_EXP_OUT_DIR": str(run / "experiments/fold-b"),
        "EXP_CACHE_DIR": str(run / "cache/experiment"),
        "AZOTH_FEATURE_CACHE_DIR": str(run / "cache/routes"),
        "AZOTH_SPECIALIST_FEATURE_CACHE_DIR": str(run / "cache/routes"),
        "AZOTH_ALLOWLIST_CACHE_DIR": str(run / "cache/allowlists"),
        "AZOTH_FOLD_FIT_MEM_FILE": str(run / "cache/fit-mem/fold.json"),
        "AZOTH_SPECIALIST_FIT_MEM_FILE": str(run / "cache/fit-mem/prod.json"),
        "AZOTH_CHECKPOINT_DIR": str(run / "checkpoints"),
        "AZOTH_VALIDATE_ONLY": "1", "AZOTH_VALIDATE_DIAGNOSTICS": "1",
        "DEPLOY_TRAIN_SAMPLES_FULL": "0", "DEPLOY_MAX_TEST_SAMPLES_FULL": "0",
        # Read-only sources for replay configuration and validation comparisons.
        "AZOTH_PROMOTED_BASELINES": str(ROOT / "out/models/azoth/.autocollie/promoted_baselines.json"),
        "AZOTH_AUTOCOLLIE_RUNS_DIR": str(ROOT / "out/experiments/azoth/runs"),
        "AZOTH_PREVIOUS_BUNDLE": str(ROOT / "out/models/azoth"),
        "AZOTH_LOW_WATER_MARK_DIR": str(ROOT / "out/models/azoth_low_water_mark"),
    }
    command = ["make", "azoth-publish-train", *(f"{k}={v}" for k, v in variables.items())]
    if args.profiler == "perf":
        command = ["perf", "record", "-e", "cycles:u", "-F", "49", "--call-graph", "dwarf,8192",
                   "-o", str(run / "perf.data"), "--", *command]
    return run, env, command, predicate


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--percent", default="1")
    parser.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    parser.add_argument("--workers", type=int, default=48)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pin", type=int, default=0)
    parser.add_argument("--profiler", choices=("cprofile", "perf", "none"), default="cprofile")
    parser.add_argument("--stop-stage", type=int, choices=range(10), default=9)
    parser.add_argument("--target-minutes", type=float, default=15)
    parser.add_argument("--fit-memory-gb", type=float)
    parser.add_argument("--extract-workers-per-fit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-memory-scope", action="store_true")
    args = parser.parse_args(argv)
    if args.workers < 1 or args.pin < 0 or not 0 < args.target_minutes < float("inf"):
        parser.error("workers/target minutes must be positive and pin must be nonnegative")
    if args.fit_memory_gb is not None and not 0 < args.fit_memory_gb < float("inf"):
        parser.error("fit memory must be positive")
    if args.extract_workers_per_fit is not None and args.extract_workers_per_fit < 1:
        parser.error("extraction workers per fit must be positive")
    run, env, command, predicate = plan(args)
    if args.dry_run:
        print(json.dumps({"output": str(run), "sample_percent": args.percent,
                          "target_seconds": args.target_minutes * 60,
                          "predicate": predicate, "command": command,
                          "environment": {k: v for k, v in env.items() if k.startswith(
                              ("COLLIMATOR_", "AZOTH_"))}}, indent=2))
        return 0
    if not args.no_memory_scope and os.environ.get("AZOTH_PROFILE_IN_SCOPE") != "1":
        os.chdir(ROOT)
        os.execvp("systemd-run", [
            "systemd-run", "--user", "--scope", "--collect", "--quiet",
            f"--unit=azoth-profile-{os.getpid()}", "--property=MemoryHigh=112G",
            "--property=MemoryMax=128G", "--property=MemorySwapMax=8G", "--property=OOMPolicy=kill",
            "env", "AZOTH_PROFILE_IN_SCOPE=1", sys.executable, str(Path(__file__).resolve()),
            *(sys.argv[1:] if argv is None else argv),
        ])
    with ExitStack() as locks:
        (ROOT / "out").mkdir(exist_ok=True)
        for name in ("nightly.lock", "nightly-autocollie.lock"):
            lock = locks.enter_context((ROOT / "out" / name).open("a"))
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise SystemExit(f"{name} is held: wait for the active run before profiling")
        # Every invocation starts fresh. Never clean or overwrite an existing run.
        run.mkdir(parents=True, exist_ok=False)
        started = time.monotonic()
        os.environ["COLLIMATOR_TIMING_DIR"] = env["COLLIMATOR_TIMING_DIR"]
        locks.enter_context(monitor(args.db, env, args.target_minutes * 60))
        locks.enter_context(phase("pipeline.total"))
        pin = args.pin
        if not pin:
            pin = int(subprocess.check_output([
                sys.executable, "-c", "import sys; from collimator.data import snapshot_max_id; "
                "print(snapshot_max_id(sys.argv[1]))", args.db,
            ], cwd=ROOT, env=env, text=True).strip())
        if pin <= 0:
            raise SystemExit("sampled corpus is empty; no profile run started")
        command.extend((f"THRESHOLD_MAX_ID={pin}", f"EXP_MAX_ID={pin}"))
        (run / "run.json").write_text(json.dumps({
            "sample_percent": args.percent, "sample_predicate": predicate,
            "snapshot_max_id": pin, "profiler": args.profiler,
            "workers": args.workers, "stop_stage": args.stop_stage,
            "target_seconds": args.target_minutes * 60,
            "fit_memory_gb": float(env["AZOTH_MEM_PER_FIT_GB"]),
            "extract_workers_per_fit": int(env["AZOTH_EXTRACT_WORKERS_MAX"]),
        }, indent=2) + "\n")
        print(f"Profile: {args.percent}% canonical-hash sample; pin={pin}; output={run}", flush=True)
        with (run / "pipeline.log").open("w") as log:
            child = subprocess.Popen(command, cwd=ROOT, env=env, text=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     start_new_session=True)
            try:
                for line in child.stdout:
                    print(line, end="", flush=True)
                    log.write(line)
                    log.flush()
                code = child.wait()
            except KeyboardInterrupt:
                os.killpg(child.pid, signal.SIGTERM)
                cancel_queries(args.db, env)
                child.wait(timeout=30)
                code = 130
            event("pipeline.total", "exit", returncode=code)
            elapsed = time.monotonic() - started
            result = dict(returncode=code, wall_seconds=elapsed,
                          target_seconds=args.target_minutes * 60,
                          full_pipeline=args.stop_stage == 9, profiler=args.profiler,
                          completed_within_target=code == 0 and args.stop_stage == 9
                          and elapsed <= args.target_minutes * 60)
            (run / "result.json").write_text(json.dumps(result, indent=2) + "\n")
            print(f"[timing] pipeline result: {result}", flush=True)
            return code


if __name__ == "__main__":
    raise SystemExit(main())
