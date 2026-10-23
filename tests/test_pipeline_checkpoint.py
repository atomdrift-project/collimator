"""Stage recovery verifies configuration, dependencies, and output contents."""

import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_stage_resumes_but_rejects_replaced_inputs_outputs_and_snapshot(tmp_path):
    script = tmp_path / "train.py"
    output = tmp_path / "model.txt"
    dependency = tmp_path / "feature_spec.json"
    dependency.write_text("original input")
    calls = tmp_path / "calls"
    script.write_text(
        "from pathlib import Path\n"
        f"calls = Path({str(calls)!r})\n"
        "calls.write_text(calls.read_text() + 'x' if calls.exists() else 'x')\n"
        f"Path({str(output)!r}).write_text('trained model')\n"
    )
    command = [sys.executable, str(ROOT / "scripts/azoth_checkpoint.py"),
               "--state-dir", str(tmp_path / "state"), "--stage", "general",
               "--input", str(dependency), "--output", str(output),
               "--", sys.executable, str(script), "WORKERS=24"]
    env = dict(os.environ, THRESHOLD_MAX_ID="123", COLLIMATOR_MEM_CEILING_GB="112")

    def run():
        result = subprocess.run(command, env=env, text=True, capture_output=True, timeout=10)
        assert result.returncode == 0, result.stderr
        return result.stdout

    run()
    assert calls.read_text() == "x"
    env["COLLIMATOR_MEM_CEILING_GB"] = "64"
    env["COLLIMATOR_SNAPSHOT_TIMEOUT_SECONDS"] = "600"
    command[-1] = "WORKERS=8"
    assert "skipping" in run()
    assert calls.read_text() == "x"
    output.write_text("partially replaced model")
    run()
    assert calls.read_text() == "xx"
    dependency.write_text("new feature layout")
    run()
    assert calls.read_text() == "xxx"
    env["THRESHOLD_MAX_ID"] = "124"
    run()
    assert calls.read_text() == "xxxx"
    output.unlink()
    run()
    assert calls.read_text() == "xxxxx"
    env["AZOTH_DATA_REVISION"] = "changed pinned rows"
    assert "skipping" in run()
    assert calls.read_text() == "xxxxx"
    env["EXP_SEED"] = "98765"
    run()
    assert calls.read_text() == "xxxxxx"


def test_failed_stage_does_not_record_completion(tmp_path):
    command = [sys.executable, str(ROOT / "scripts/azoth_checkpoint.py"),
               "--state-dir", str(tmp_path / "state"), "--stage", "general",
               "--output", str(tmp_path / "model.txt"), "--", sys.executable,
               "-c", "raise SystemExit(7)"]
    result = subprocess.run(command, text=True, capture_output=True, timeout=10)
    assert result.returncode == 7
    assert not (tmp_path / "state/general.json").exists()
