#!/usr/bin/env python3
"""Generate Python vectors for every combination of the five keyword sources."""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from collimator.features import FeatureSpec, extract
from extended_keyword_parity_fixture import fixtures as extended_fixtures


def fixtures():
    vocab = {
        "ruleword": ["curl", "download", "metadata", "post", "unseen"],
        "descword": ["curl", "download", "http", "post", "unseen", "via"],
        "fullword": ["behaviors", "curl", "download", "metadata", "micro", "network", "post", "unseen"],
        "ruletextword": ["behaviors", "curl", "download", "http", "metadata", "micro", "network", "post", "unseen", "via"],
        "contextword": ["caf", "curl", "fetch", "token", "unseen"],
    }
    reports = extended_fixtures()
    sources = list(vocab)
    output = []
    with tempfile.TemporaryDirectory() as tmp:
        for mask in range(1, 1 << len(sources)):
            selected = {source: vocab[source] for i, source in enumerate(sources) if mask & (1 << i)}
            names = ["present:metadata"] + [f"{s}:{w}" for s, words in selected.items() for w in words]
            # Reversed slots exercise name-based layout rather than a source-order assumption.
            spec = FeatureSpec(version=23, abi_version=23, base_feature_abi=20,
                               presence_vocab=["metadata"], keyword_vocabs=selected,
                               feature_names=list(reversed(names)), total_features=len(names))
            for fixture in reports:
                current = spec
                if fixture["name"] == "pruned-context-source":
                    kept = [n for n in current.feature_names if not n.startswith("contextword:")]
                    current = replace(current, feature_names=kept, total_features=len(kept))
                path = Path(tmp) / "spec.json"
                current.save(path)
                report = fixture["report"]
                expected = extract(fixture.get("training_report", report), current)
                assert (extract(report, current) == expected).all()
                output.append(dict(name=f"{mask:02d}-{fixture['name']}",
                                   spec=json.loads(path.read_text()), report=report,
                                   expected=expected.tolist()))
    assert len(output) == 31 * len(reports)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = fixtures()
    args.output.write_text(json.dumps(result, separators=(",", ":")) + "\n")
    print(f"Wrote {len(result)} cases covering all 31 nonempty source combinations")
