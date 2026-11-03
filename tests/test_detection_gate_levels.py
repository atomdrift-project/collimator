"""Only regressions in the inclusive L0–L25 range may block deployment."""
import importlib.util
import json
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    'detection_gate', Path(__file__).parents[1] / 'scripts/check_azoth_regression.py'
)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


def report(recalls):
    return {'filetypes': {'pe': {
        'malware': 10000, 'benign': 10000,
        'deployed_or_by_level': {
            f'L{level}_hostile': {'recall': recall, 'tp': round(recall * 10000), 'fp': 0}
            for level, recall in recalls.items()
        },
    }}}


def run_gate(tmp_path, monkeypatch, staged, deployed, extra=(), lwm=None):
    monkeypatch.delenv('AZOTH_ALLOW_REGRESSION', raising=False)
    for name, values in [('staged', staged), ('deployed', deployed), ('lwm', lwm)]:
        if values is not None:
            folder = tmp_path / name
            folder.mkdir(exist_ok=True)
            (folder / 'route_policy_eval_oof.json').write_text(json.dumps(report(values)))
    args = ['--staged', str(tmp_path / 'staged'), '--deployed', str(tmp_path / 'deployed')]
    if lwm is not None:
        args += ['--low-water-mark', str(tmp_path / 'lwm')]
    return gate.main(args + list(extra))


@pytest.mark.parametrize('level', [0, 1, 10, 25, 26, 2500, 25000])
def test_only_low_range_blocks(tmp_path, monkeypatch, capsys, level):
    deployed = dict.fromkeys([0, 1, 10, 25, 26, 2500, 25000], .9)
    staged = dict(deployed)
    staged[level] = .5
    result = run_gate(tmp_path, monkeypatch, staged, deployed)
    assert result == (1 if level <= 25 else 0)
    output = capsys.readouterr().out
    assert f'L{level}' in output
    if level > 25:
        assert 'report only:' in output
        assert 'blocked by:' not in output


def test_lwm_above_25_is_report_only(tmp_path, monkeypatch, capsys):
    values = {0: .5, 25: .5, 2500: .5}
    assert run_gate(tmp_path, monkeypatch, values, values, lwm={0: .5, 25: .5, 2500: .9}) == 0
    assert 'report only:' in capsys.readouterr().out


def test_explicit_high_level_cannot_block(tmp_path, monkeypatch):
    assert run_gate(tmp_path, monkeypatch, {2500: .5}, {2500: .9}, ['--level', '2500']) == 0


def test_missing_staged_blocking_checkpoint_is_error(tmp_path, monkeypatch):
    assert run_gate(tmp_path, monkeypatch, {0: .9, 25: .9}, {0: .9, 10: .9, 25: .9}) == 2


def test_missing_high_checkpoint_does_not_block(tmp_path, monkeypatch):
    assert run_gate(tmp_path, monkeypatch, {0: .9, 25: .9}, {0: .9, 25: .9, 2500: .9}) == 0
