"""Favorites replay handles old history and respects explicit resource limits."""
import importlib.util
import os
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("record_replay", ROOT / "scripts/autocollie_record_replay.py")
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


@pytest.mark.parametrize("line,outcome", [
    ('level=ERROR msg="autocollie failed" error="fresh screening: broken"', 'error'),
    ('=== confirm fresh on route filetypes/ole: FAIL ===', 'confirm-failed'),
    ('SKIP-PROMOTE: refreshed favorite predicts regression', 'rejected'),
    ('=== promote fresh on route filetypes/ole: PASS ===', 'promoted'),
    ('=== promote fresh on route filetypes/ole: REJECTED ===', 'rejected'),
])
def test_single_replay_log_records_real_outcome(tmp_path, line, outcome):
    log = tmp_path / 'replay.log'
    log.write_text(line + '\nmake: error 1\n--make-args DB=local\n')
    actual, reason = replay.detect_outcome_from_logs(log, log)
    assert actual == outcome
    if outcome == 'error':
        assert 'fresh screening: broken' in reason


@pytest.mark.parametrize('target', ['autocollie-confirm', 'autocollie-promote', 'autocollie-replay', 'autocollie'])
@pytest.mark.parametrize('override,expected', [(None, None), ('WORKERS=3', 'EXP_WORKERS=3'), ('EXP_WORKERS=5', 'EXP_WORKERS=5')])
def test_make_uses_per_job_workers_unless_explicit(target, override, expected):
    env = dict(os.environ)
    for key in ('WORKERS', 'EXP_WORKERS', 'MAKEFLAGS', 'MAKEOVERRIDES'):
        env.pop(key, None)
    command = ['make', '-n', target, 'KEY=aaaaaaaaaaaaaaaa', 'ROUTES=filetypes/ole', 'MAX_CPU_THREADS=24']
    if override:
        command.append(override)
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, check=True)
    if expected:
        assert expected in result.stdout
    else:
        assert 'EXP_WORKERS=' not in result.stdout


def test_favorites_recipe_runs_one_snapshot_replay_per_candidate():
    text = (ROOT / 'Makefile').read_text().split('autocollie-replay-favorites: venv autocollie-build\n', 1)[1].split('\nautocollie-confirm:', 1)[0]
    assert 'autocollie-replay KEY=$$key' in text
    assert 'autocollie-confirm KEY=$$key' not in text
    assert 'autocollie-promote KEY=$$key' not in text
