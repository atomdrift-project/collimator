#!/usr/bin/env python3
"""Record an entire Make stage, with progress even during silent DB queries."""
import subprocess
import sys
import time

from collimator.profiling import event, phase


def main():
    label, *command = sys.argv[1:]
    started = time.monotonic()
    print(f"[timing] {label}: starting", flush=True)
    with phase("stage." + label):
        child = subprocess.Popen(command)
        while True:
            try:
                code = child.wait(timeout=30)
                break
            except subprocess.TimeoutExpired:
                print(f"[timing] {label}: running {time.monotonic() - started:.0f}s", flush=True)
        event("stage." + label, "exit", returncode=code)
        print(f"[timing] {label}: finished in {time.monotonic() - started:.1f}s (exit {code})", flush=True)
        if code:
            raise SystemExit(code)


if __name__ == "__main__":
    main()
