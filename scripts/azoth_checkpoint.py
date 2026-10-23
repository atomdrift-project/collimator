#!/usr/bin/env python3
"""Resume completed stages when the pin, configuration and artifacts match.

A receipt records completed work, not a cache of today's live database. Rows
below the pin may subsequently change without discarding a finished model.
Partial-work caches validate their own inputs; publication gates always rerun.
"""

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess


def manifest(paths):
    result = {}
    for value in paths:
        root = Path(value)
        if not root.exists():
            raise FileNotFoundError(root)
        files = [root] if root.is_file() else sorted(
            path for path in root.rglob("*") if path.is_file()
            and "oof_route_scores" not in path.relative_to(root).parts[:-1] and (
                path.suffix in (".onnx", ".txt") or path.name in (
                    "feature_spec.json", "training_provenance.json", "specialists.json",
                    "threshold_scores.npz", "threshold_scores.meta.json",
                ) or path.suffix == ".npz"
            )
        )
        if not files:
            raise ValueError(f"no completed artifacts in {root}")
        for path in files:
            digest = hashlib.sha256()
            with path.open("rb") as source:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(block)
            result[str(path)] = digest.hexdigest()
    return result


def fingerprint(command, inputs):
    root = Path(__file__).resolve().parents[1]
    code = hashlib.sha256()
    paths = [root / "Makefile", *sorted((root / "src/collimator").rglob("*.py")),
             *sorted((root / "scripts").glob("*.py")), *sorted((root / "scripts").glob("*.sh"))]
    for path in paths:
        code.update(str(path.relative_to(root)).encode())
        code.update(path.read_bytes())
    # Resource reductions must allow recovery. Training/feature settings must
    # invalidate earlier stages rather than silently reuse different models.
    environment = {
        key: value for key, value in os.environ.items()
        if (key == "DB" or key == "THRESHOLD_MAX_ID"
            or key.startswith(("EXP_", "AZOTH_", "COLLIMATOR_")))
        # Ignore obsolete corpus-checksum settings inherited from older runs.
        and key not in ("COLLIMATOR_SNAPSHOT_TIMEOUT_SECONDS", "AZOTH_DATA_REVISION")
        and not any(part in key for part in (
            "MEM", "WORKER", "THREAD", "PARALLEL", "CONCURRENT", "CHECKPOINT", "RESUME",
        ))
    }
    # WORKERS/threads vary with sequential fallback; these do not change the
    # learned configuration or row selections.
    semantic_command = [arg for arg in command if not arg.startswith("WORKERS=")]
    return {"code": code.hexdigest(), "environment": environment,
            "command": semantic_command, "inputs": manifest(inputs)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--output", action="append", default=[])
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command or not args.output:
        parser.error("a command and at least one output are required")
    args.state_dir.mkdir(parents=True, exist_ok=True)
    receipt = args.state_dir / f"{args.stage}.json"
    with receipt.with_suffix(".lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        identity = fingerprint(command, args.input)
        try:
            previous = json.loads(receipt.read_text())
            if previous["identity"] == identity and previous["outputs"] == manifest(args.output):
                print(f"[resume] {args.stage}: completed inputs and artifacts match; skipping", flush=True)
                return 0
        except (OSError, ValueError, KeyError):
            pass
        # A failed rerun must not leave an older success receipt usable.
        receipt.unlink(missing_ok=True)
        result = subprocess.run(command)
        if result.returncode:
            return result.returncode if result.returncode > 0 else 128 - result.returncode
        outputs = manifest(args.output)
        temporary = receipt.with_suffix(".tmp")
        with temporary.open("w") as destination:
            json.dump({"identity": identity, "outputs": outputs}, destination, sort_keys=True)
            destination.flush()
            os.fsync(destination.fileno())
        os.replace(temporary, receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
