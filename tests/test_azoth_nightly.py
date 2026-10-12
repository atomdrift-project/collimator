"""Exercise unattended scheduling without a database or model training."""

import os
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def shell_env(tmp_path):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    memory = tmp_path / "available"
    memory.write_text("200\n")
    events = tmp_path / "events"
    stubs = {
        "nproc": "echo 128\n",
        "awk": """case "$*" in
  */proc/meminfo*) read -r available < "$TEST_MEMORY"; printf '%s' "$available" ;;
  *) exec /usr/bin/awk "$@" ;;
esac
""",
        "make": """printf 'start %s\\n' "$1" >> "$TEST_EVENTS"
sleep 0.1
printf 'end %s\\n' "$1" >> "$TEST_EVENTS"
if [[ ${TEST_MEMORY_SWITCH_TARGET:-} == "$1" ]]; then
    printf '%s\\n' "$TEST_MEMORY_AFTER" > "$TEST_MEMORY"
fi
if [[ ${TEST_FAIL_TARGET:-} == "$1" ]]; then exit 1; fi
""",
        "systemctl": "exit 0\n",
        "loginctl": "echo Linger=yes\n",
    }
    for name, body in stubs.items():
        executable = bindir / name
        executable.write_text("#!/bin/bash\n" + body)
        executable.chmod(0o755)
    env = dict(os.environ)
    for name in (
        "PARALLEL_CHAINS", "PARALLEL_FOLDS", "MAKEFLAGS", "START_STAGE", "STOP_STAGE",
        "COLLIMATOR_NUM_THREADS", "COLLIMATOR_MEM_SHARES", "AZOTH_CONCURRENT_SUITES",
    ):
        env.pop(name, None)
    env.update(
        PATH=f"{bindir}:/usr/bin:/bin",
        TEST_MEMORY=str(memory),
        TEST_EVENTS=str(events),
        MEM_LOG=str(tmp_path / "memory.log"),
        AZOTH_MEMORY_WAIT_SECONDS="0",
        START_STAGE="0",
        STOP_STAGE="2",
        WORKERS="48",
        XDG_CONFIG_HOME=str(tmp_path / "config"),
    )
    return env, memory, events


def run_pipeline(env):
    return subprocess.run(
        ["bash", "scripts/azoth_oof_pipeline.sh"], cwd=ROOT, env=env,
        text=True, capture_output=True, timeout=10,
    )


def test_parallel_training_when_ram_available(shell_env):
    env, _, events = shell_env
    result = run_pipeline(env)
    assert result.returncode == 0, result.stdout + result.stderr
    lines = events.read_text().splitlines()
    assert lines.index("start azoth-general-fold-a") < lines.index("end azoth-general")
    assert "WORKERS=24/chain" in result.stdout


@pytest.mark.parametrize("explicit", [None, "0", "1"])
def test_serial_training_under_memory_pressure(shell_env, explicit):
    env, memory, events = shell_env
    memory.write_text("110\n")
    if explicit is not None:
        env["PARALLEL_CHAINS"] = explicit
    result = run_pipeline(env)
    assert result.returncode == 0, result.stdout + result.stderr
    lines = events.read_text().splitlines()
    assert lines.index("end azoth-general") < lines.index("start azoth-general-fold-a")


def test_low_memory_does_not_launch_training(shell_env):
    env, memory, events = shell_env
    memory.write_text("33\n")
    result = run_pipeline(env)
    assert result.returncode != 0
    assert "memory admission timed out" in result.stderr
    assert not events.exists()


def test_parallel_failure_does_not_publish(shell_env):
    env, _, events = shell_env
    env["TEST_FAIL_TARGET"] = "azoth-general"
    result = run_pipeline(env)
    assert result.returncode != 0
    assert "training chain failed" in result.stdout
    assert "end azoth-general-fold-b" in events.read_text()
    assert "azoth-deploy" not in events.read_text()


@pytest.mark.parametrize("before,after", [(110, 200), (200, 110)])
def test_scoring_rechecks_memory(shell_env, tmp_path, before, after):
    env, memory, events = shell_env
    memory.write_text(f"{before}\n")
    models = tmp_path / "models"
    for name in ("azoth", "azoth.oof-fold-a", "azoth.oof-fold-b"):
        bundle = models / name
        (bundle / "general").mkdir(parents=True)
        (bundle / "specialists.json").write_text("{}\n")
    env.update(
        OUT_ROOT=str(models), STOP_STAGE="6",
        TEST_MEMORY_SWITCH_TARGET="azoth-specialists-fold-b",
        TEST_MEMORY_AFTER=str(after),
    )
    result = run_pipeline(env)
    assert result.returncode == 0, result.stdout + result.stderr
    lines = events.read_text().splitlines()
    overlaps = (
        lines.index("start azoth-oof-route-scores")
        < lines.index("end azoth-oof-merge-general")
    )
    assert overlaps == (after == 200)


def test_admission_waits_and_recovers(shell_env):
    env, _, _ = shell_env
    result = subprocess.run(
        ["bash", "-c", """source scripts/azoth_resources.sh
mock_memory=33
mem_avail_gb() { echo "$mock_memory"; }
sleep() { mock_memory=110; }
AZOTH_MEMORY_WAIT_SECONDS=60 wait_for_azoth_memory 96
"""], cwd=ROOT, env=env, text=True, capture_output=True, timeout=5,
    )
    assert result.returncode == 0, result.stderr
    assert "waiting: 33" in result.stdout
    assert "admitted: 110" in result.stdout


def test_reinstall_preserves_schedule_and_sets_limits(shell_env):
    env, _, _ = shell_env
    units = Path(env["XDG_CONFIG_HOME"]) / "systemd/user"
    units.mkdir(parents=True)
    schedule = "OnCalendar=Sun *-*-* 20:00:00\nOnCalendar=Wed *-*-* 20:00:00\n"
    (units / "azoth-nightly.timer").write_text("[Timer]\n" + schedule)
    env.pop("NIGHTLY_ONCALENDAR", None)
    result = subprocess.run(
        ["bash", "scripts/install_nightly.sh"], cwd=ROOT, env=env,
        text=True, capture_output=True, timeout=5,
    )
    assert result.returncode == 0, result.stderr
    assert schedule in (units / "azoth-nightly.timer").read_text()
    train = (units / "azoth-nightly.service").read_text()
    assert "MemoryHigh=112G" in train
    assert "MemoryMax=128G" in train
    assert "MemorySwapMax=16G" in train
    assert "OOMPolicy=stop" in train
    assert "Restart=on-abnormal" in train
    assert "StartLimitBurst=2" in train
    assert "MemoryMax=64G" in (units / "azoth-autocollie.service").read_text()


@pytest.mark.parametrize("snapshot", ["123456", "invalid"])
def test_nightly_logger_protection_and_snapshot_gate(shell_env, tmp_path, snapshot):
    env, _, events = shell_env
    sandbox = tmp_path / "checkout"
    scripts = sandbox / "scripts"
    scripts.mkdir(parents=True)
    for name in ("nightly.sh", "azoth_resources.sh"):
        content = (ROOT / "scripts" / name).read_text()
        # Keep the harness's isolated tools ahead of the service PATH bootstrap.
        content = content.replace(
            'export PATH="/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$PATH"',
            'export PATH="$PATH"',
        )
        (scripts / name).write_text(content)
    python = sandbox / ".venv/bin/python"
    python.parent.mkdir(parents=True)
    python.write_text(f"#!/bin/bash\necho {snapshot}\n")
    python.chmod(0o755)
    bindir = Path(env["PATH"].split(":")[0])
    for name, body in {
        "doas": "echo protect >> \"$TEST_EVENTS\"\n",
        "gawk": "echo logger >> \"$TEST_EVENTS\"\nexec /usr/bin/awk \"$@\"\n",
        "sleep": "exit 0\n",
        "systemctl": 'printf "systemctl %s\\n" "$*" >> "$TEST_EVENTS"\n',
    }.items():
        tool = bindir / name
        tool.write_text("#!/bin/bash\n" + body)
        tool.chmod(0o755)
    # Fail training deliberately: no Git writes or model publication in this test.
    env["TEST_FAIL_TARGET"] = "azoth-publish-train"
    result = subprocess.run(
        ["bash", str(scripts / "nightly.sh"), "train"], cwd=sandbox, env=env,
        text=True, capture_output=True, timeout=10,
    )
    assert result.returncode != 0
    lines = events.read_text().splitlines()
    assert lines.index("protect") < lines.index("logger")
    assert "systemctl --user start --no-block azoth-autocollie.service" in lines
    if snapshot == "invalid":
        assert "start azoth-publish-train" not in lines
        assert "start repin" not in lines
    else:
        assert "start repin" in lines
        assert "start azoth-publish-train" in lines
