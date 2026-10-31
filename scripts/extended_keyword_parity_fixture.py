#!/usr/bin/env python3
"""Produce ABI 23 Python/Scan fixtures, including both context wire encodings."""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from collimator.features import FeatureSpec, extract


def fixtures():
    vocabs = {
        'fullword': ['behaviors', 'curl', 'download', 'metadata', 'micro', 'network', 'post', 'unseen'],
        'ruletextword': ['behaviors', 'curl', 'download', 'http', 'metadata', 'micro', 'network', 'post', 'unseen', 'via'],
        'contextword': ['caf', 'curl', 'fetch', 'token', 'unseen'],
    }
    names = ['present:metadata'] + [f'{source}:{word}' for source, words in vocabs.items() for word in words]
    spec = FeatureSpec(version=23, abi_version=23, base_feature_abi=20,
                       presence_vocab=['metadata'], keyword_vocabs=vocabs,
                       feature_names=names, total_features=len(names))
    finding = dict(id='micro-behaviors/network::curl_download_post', desc='Download via HTTP POST', conf=1, crit=2)
    raw = b'curl FETCH_token\x00caf\xc3\xa9\xff'
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#'
    encoded = ''
    for start in range(0, len(raw), 4):
        chunk = raw[start:start + 4]
        value = int.from_bytes(chunk.ljust(4, b'\0'), 'big')
        digits = ''
        for _ in range(5):
            digits = alphabet[value % 85] + digits
            value //= 85
        encoded += digits[:5 if len(chunk) == 4 else len(chunk) + 1]
    current = dict(ln=0, s=''.join(chr(b or 256) for b in raw))
    legacy = dict(ln=0, b=encoded)
    cases = [
        ('byte-text-and-dedup', spec, [finding] * 2, [current] * 2),
        ('legacy-z85-and-tail', spec, [finding] * 2, [legacy] * 2),
        ('missing-description-retains-hierarchy', spec, [dict(finding, desc='')], []),
        ('low-confidence-still-reads-context', spec, [dict(finding, conf=.1)], [legacy]),
        ('legacy-slash-hierarchy', spec, [dict(finding, id='metadata/network/CURL-download-post')], []),
        ('window-boundaries', spec, [], [dict(ln=0, s='cur'), dict(ln=8, s='l')]),
        ('missing-context', spec, [finding], []),
    ]
    pruned = replace(spec, feature_names=[n for n in names if not n.startswith('contextword:')])
    pruned = replace(pruned, total_features=len(pruned.feature_names))
    cases.append(('pruned-context-source', pruned, [finding], [legacy]))
    result = []
    for name, current_spec, findings, windows in cases:
        file = dict(id=0, path='sample.py', type='python', sha='fixture', size=10, traits=findings, ctx=windows)
        report = dict(v='9' if not windows or 's' in windows[0] else '8', files=[file, dict(file, id=1, pid=0)])
        result.append(dict(name=name, report=report, expected=extract(report, current_spec).tolist()))
        # FeatureSpec's supported serialization includes normalized family metadata.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'spec.json'
            current_spec.save(path)
            result[-1]['spec'] = json.loads(path.read_text())
    # Schema 7 stored display text; the trainer imports it as UTF-8. Serving
    # receives current Cleave windows containing the same decoded text bytes.
    old = dict(v='7', files=[dict(id=0, path='sample.py', type='python', sha='fixture', size=10,
        traits=[finding], ctx=[dict(a=0, l=1, t=raw.decode('utf-8', errors='replace'))])])
    normalized = json.loads(json.dumps(old))
    plain_bytes = old['files'][0]['ctx'][0]['t'].encode('utf-8')
    normalized['v'] = '9'
    normalized['files'][0]['ctx'] = [dict(ln=0, s=''.join(chr(b or 256) for b in plain_bytes))]
    result.append(dict(name='schema7-plain-text-import', spec=result[0]['spec'], report=normalized,
                       training_report=old, expected=extract(old, spec).tolist()))
    assert extract(normalized, spec).tolist() == result[-1]['expected']
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(fixtures(), indent=2) + '\n')
