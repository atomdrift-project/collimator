#!/usr/bin/env python3
"""Generate Scan's checked keyword-vector fixtures with the Python extractor."""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from collimator.features import FeatureSpec, extract


def fixtures():
    vocab = {"ruleword": ["curl", "download", "post", "post2", "unseen", "wget"],
             "descword": ["caf", "download", "http", "kernel", "post", "script", "unseen", "via"]}
    names = ["present:metadata"] + [f"{source}:{word}" for source, words in vocab.items() for word in words]
    spec = FeatureSpec(version=22, abi_version=22, base_feature_abi=20,
                       presence_vocab=["metadata"], keyword_vocabs=vocab,
                       feature_names=names, total_features=len(names))
    def finding(fid, desc="Download via HTTP POST", conf=1.0):
        return dict(id=fid, desc=desc, conf=conf, crit=2)
    cases = [
        ("binary-and-dedup", spec, [finding("metadata/network::curl_download-post")]*2),
        ("legacy-leaf-and-unicode", spec, [finding("legacy/path/CURL-download_post2", "Café İHTTP kernel")]),
        ("confidence-boundary", spec, [finding("micro/network::wget", "script", .65),
                                       finding("metadata/network::curl", "download", .64)]),
        ("missing-description", spec, [finding("metadata/network::curl", "")]),
        ("low-confidence-missing-description", spec, [finding("metadata/network::curl", "", .5)]),
        ("pruned-description-source", replace(spec,
            feature_names=[n for n in names if not n.startswith("descword:")],
            total_features=1+len(vocab["ruleword"])), [finding("metadata/network::curl", "")]),
        ("numeric-and-single-character", spec, [finding("metadata/network::x_123_curl", "1 x HTTP")]),
    ]
    output = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, current, findings in cases:
            report = {"v":"8", "files":[dict(id=0,path="sample.class",type="java_class",sha="fixture",size=10,traits=findings),
                                            dict(id=1,pid=0,path="inner.class",type="java_class",sha="inner",size=10,traits=findings)]}
            path = Path(tmp)/"spec.json"
            current.save(path)
            case = dict(name=name,spec=json.loads(path.read_text()),report=report,error=False)
            try:
                case["expected"] = extract(report,current).tolist()
            except ValueError:
                case["error"] = True
            output.append(case)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    args.output.write_text(json.dumps(fixtures(),indent=2)+"\n")
