"""Runtime staging drops search history without changing selected decisions."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import stage_azoth_runtime_bundle as stage


def test_policy_staging_preserves_all_selected_data_and_source(tmp_path):
    best = {'thresholds': {'general': 0.9999999999999999},
            'blend': {'routes': ['general'], 'weights': [1.25],
                      'intercept': -2.0, 'threshold': 0.7}, 'fp': 0}
    severity = {'best': best, 'budget': 1, 'future_metadata': {'a': 42}}
    selected = {'schema': 'azoth.route_policy_search.v1', 'timestamp': 'frozen',
                'routes': {'filetypes/elf': {'filetype': 'elf', 'models': ['general'],
                    'levels': [{'level': 25, 'hostile': severity,
                                'suspicious': severity},
                               {'level': 0, 'hostile': {'best': None}}]}}}
    source = json.loads(json.dumps(selected))
    for entry in source['routes']['filetypes/elf']['levels']:
        for name in ('hostile', 'suspicious'):
            if name in entry:
                entry[name]['candidates'] = [{'thresholds': {'general': 0.01}}] * 100
    src, dst = tmp_path / 'source.json', tmp_path / 'runtime.json'
    src.write_text(json.dumps(source, indent=2))
    before = src.read_bytes()
    stage._stage_route_policies(src, dst)
    assert json.loads(dst.read_text()) == selected
    assert src.read_bytes() == before
    assert dst.stat().st_size < src.stat().st_size / 10
    # Re-staging already deployed bundles is stable.
    again = tmp_path / 'again.json'
    stage._stage_route_policies(dst, again)
    assert again.read_bytes() == dst.read_bytes()
