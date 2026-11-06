"""The publish gate ships a bundle that is better overall at L0 and L25."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    'publish_gate', Path(__file__).parents[1] / 'scripts/check_azoth_regression.py'
)
gate = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gate  # dataclasses resolve their module by name
_spec.loader.exec_module(gate)

MAL, BEN = 100_000, 1_000_000


def report(filetypes):
    """filetypes: {name: {level: (tp, fp)}}; pooled over MAL malware, BEN benign."""
    n = len(filetypes)
    return {
        'malware': MAL, 'benign': BEN,
        'filetypes': {
            name: {
                'malware': MAL // n, 'benign': BEN // n,
                'deployed_or_by_level': {
                    f'L{level}_hostile': {'tp': tp, 'fp': fp, 'recall': tp / (MAL // n)}
                    for level, (tp, fp) in levels.items()
                },
            }
            for name, levels in filetypes.items()
        },
    }


def run_gate(tmp_path, monkeypatch, staged, deployed):
    monkeypatch.delenv('AZOTH_ALLOW_REGRESSION', raising=False)
    for name, value in [('staged', staged), ('deployed', deployed)]:
        folder = tmp_path / name
        folder.mkdir(exist_ok=True)
        if value is not None:
            (folder / 'route_policy_eval_oof.json').write_text(json.dumps(value))
    return gate.main(['--staged', str(tmp_path / 'staged'), '--deployed', str(tmp_path / 'deployed')])


BASE = {'pe': {0: (30_000, 100), 25: (40_000, 400)}, 'zip': {0: (20_000, 100), 25: (35_000, 400)}}


def changed(**levels):
    """BASE with pe's (tp, fp) replaced at the given levels, e.g. L25=(41_000, 400)."""
    out = {k: dict(v) for k, v in BASE.items()}
    for key, value in levels.items():
        out['pe'][int(key[1:])] = value
    return out


def test_net_better_ships_despite_one_filetype_falling(tmp_path, monkeypatch, capsys):
    # zip loses 1,000 catches at L25, pe gains 2,000: pooled L25 +1pp.
    staged = {'pe': {0: (30_500, 100), 25: (42_000, 400)}, 'zip': {0: (20_000, 100), 25: (34_000, 400)}}
    assert run_gate(tmp_path, monkeypatch, report(staged), report(BASE)) == 0
    out = capsys.readouterr().out
    assert 'PASS: better overall' in out
    assert '-1,000 caught' in out  # the zip loss is still shown


@pytest.mark.parametrize('level', [0, 25])
def test_a_level_falling_past_the_loss_bound_blocks(tmp_path, monkeypatch, capsys, level):
    # This level loses 0.3pp (300 of 100,000); the other gains 5pp.
    other = 25 if level == 0 else 0
    staged = changed(**{
        f'L{level}': (BASE['pe'][level][0] - 300, BASE['pe'][level][1]),
        f'L{other}': (BASE['pe'][other][0] + 5_000, BASE['pe'][other][1]),
    })
    assert run_gate(tmp_path, monkeypatch, report(staged), report(BASE)) == 1
    assert f'L{level} recall fell 0.30pp' in capsys.readouterr().out


def test_a_bounded_loss_with_a_gain_elsewhere_ships(tmp_path, monkeypatch):
    # L25 -0.15pp (inside the 0.2pp bound), L0 +0.5pp.
    staged = changed(L25=(40_000 - 150, 400), L0=(30_000 + 500, 100))
    assert run_gate(tmp_path, monkeypatch, report(staged), report(BASE)) == 0


def test_no_improvement_does_not_ship(tmp_path, monkeypatch, capsys):
    staged = changed(L25=(40_050, 400))  # +0.05pp, under the 0.1pp bar
    assert run_gate(tmp_path, monkeypatch, report(staged), report(BASE)) == 1
    assert 'neither L0 nor L25 recall rose' in capsys.readouterr().out


def test_recall_bought_with_false_positives_does_not_ship(tmp_path, monkeypatch, capsys):
    staged = changed(L25=(42_000, 600))  # +2pp, but pooled FPs 800 -> 1,000
    assert run_gate(tmp_path, monkeypatch, report(staged), report(BASE)) == 1
    assert 'L25 FPs rose 800 → 1,000' in capsys.readouterr().out


def test_fp_noise_is_tolerated(tmp_path, monkeypatch):
    staged = changed(L25=(42_000, 430))  # 800 -> 830, inside 2 sigma (~857)
    assert run_gate(tmp_path, monkeypatch, report(staged), report(BASE)) == 0


def test_levels_other_than_l0_and_l25_are_ignored(tmp_path, monkeypatch):
    deployed = {'pe': {0: (30_000, 100), 25: (40_000, 400), 25_000: (90_000, 9_000)}}
    staged = {'pe': {0: (31_000, 100), 25: (41_000, 400), 25_000: (10_000, 9_000)}}
    assert run_gate(tmp_path, monkeypatch, report(staged), report(deployed)) == 0


def test_override_skips_the_gate(tmp_path, monkeypatch):
    monkeypatch.setenv('AZOTH_ALLOW_REGRESSION', '1')
    assert gate.main(['--staged', str(tmp_path), '--deployed', str(tmp_path)]) == 0


def test_no_deployed_eval_ships(tmp_path, monkeypatch):
    assert run_gate(tmp_path, monkeypatch, report(BASE), None) == 0


def test_missing_staged_level_is_an_error(tmp_path, monkeypatch):
    staged = {'pe': {25: (40_000, 400)}, 'zip': {25: (35_000, 400)}}
    assert run_gate(tmp_path, monkeypatch, report(staged), report(BASE)) == 2


def test_missing_staged_eval_is_an_error(tmp_path, monkeypatch):
    assert run_gate(tmp_path, monkeypatch, None, report(BASE)) == 2


def test_models_that_moved_are_listed_but_do_not_decide(tmp_path, monkeypatch, capsys):
    def with_routes(rep, aucs):
        for ft, entry in rep['filetypes'].items():
            entry['slice_metrics'] = {'routes': {
                route: {'pr_auc': auc, 'recall_at_0fp': .5} for route, auc in aucs.items()
            }}
        return rep
    deployed = with_routes(report(BASE), {'general': .90, 'filetypes/pe': .95, 'filetypes/zip': .80})
    staged = with_routes(
        report(changed(L25=(41_000, 400))),
        {'general': .90, 'filetypes/pe': .97, 'filetypes/zip': .70},
    )
    assert run_gate(tmp_path, monkeypatch, staged, deployed) == 0
    out = capsys.readouterr().out
    better, worse = out.split('models that got worse')
    assert 'filetypes/pe' in better.split('models that got better')[1]
    assert 'filetypes/zip' in worse
    assert 'general' not in out.split('models that got better')[1]  # unmoved
