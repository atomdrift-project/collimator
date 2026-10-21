#!/usr/bin/env python3
"""Compare Python and scan n-gram features across ABI versions and token budgets.

Run with the project Python environment. Optional --reports adds an array of
real cleave reports to the synthetic boundary cases. No database is required.
Fixtures and cargo output remain under --output for diagnosis.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from collimator import features as f  # noqa: E402


def boundary_reports() -> list[dict]:
    findings = [
        {"i": f"branch/sub{i:04}/part/leaf/end::trait", "l": 3, "c": 1.0}
        for i in range(600)
    ]
    extra = [
        {"i": "zstrong/deep/path/leaf/end::one", "l": 5, "c": 0.7},
        {"i": "zstrong/deep/path/leaf/end::two", "l": 3, "c": 1.0},
        {"i": "strong/deep/path/leaf/end", "l": 4, "c": 0.875},
        {"i": "metadata/weak", "l": 2, "c": 1.0},
    ]
    reports = []
    for n in (63, 64, 65, 127, 128, 129, 511, 512, 513, 600):
        items = findings[:n] + extra
        for reverse in (False, True):
            reports.append({"v": "4", "fs": [{
                "type": "javascript", "ts": items[::-1] if reverse else items,
            }]})
    reports.append({"v": "4", "fs": [
        {"type": "javascript", "ts": (findings + extra)[i::3]} for i in range(3)
    ]})
    return reports


def compact(report: dict) -> dict:
    """Adapt finding inputs to scan's typed report schema without rescanning."""
    return {"v": "8", "files": [{
        "id": i, "path": file.get("path", str(i)), "sha": "0" * 64,
        "type": file.get("type", "unknown"), "size": max(0, int(file.get("size", 0))),
        "traits": [{"id": f.finding_id(t) or "", "crit": f.finding_crit(t) or 0,
                    "conf": f._float(f.finding_conf(t), 1.0)}
                   for t in f.file_findings(file)],
    } for i, file in enumerate(f.report_files(report))]}


def make_spec(reports: list[dict], abi: int, depth: int, overrides: bool) -> f.FeatureSpec:
    names = {"present:branch"}
    minimums = (2, 3, 4) if overrides else (3, 3, 3)
    branches = {"metadata": 4, "branch": 3} if overrides else {}
    for report in reports:
        summary = f._summarize_report_files(f.report_files(report))
        for order, prefix in ((2, "tierbi"), (3, "tiertri"), (4, "tierquad")):
            tokens = f._ranked_tiered_tokens(
                summary.sample_paths, summary.path_scores, order=order,
                min_crit=minimums[order - 2], branch_min_crit=branches,
            )
            # Include learned combinations at both ends of the token budget.
            chosen = sorted(set(tokens[:6] + tokens[-6:]))
            names.update(prefix + ":" + " + ".join(parts) for parts in combinations(chosen, order))
        for file in f.report_files(report):
            for order, limit, prefix in ((2, 512, "bigrams"), (3, 128, "trigram")):
                paths = f._ranked_ngram_paths(file, limit)
                chosen = sorted(set(paths[:4] + paths[-4:]))
                names.update(prefix + ":" + " + ".join(parts) for parts in combinations(chosen, order))
    ordered = sorted(names)

    def vocab(prefix):
        return [name[len(prefix):] for name in ordered if name.startswith(prefix)]

    return f.FeatureSpec(
        presence_vocab=["branch"], version=abi, abi_version=abi, trait_path_depth=depth,
        feature_names=ordered, total_features=len(ordered),
        bigram_vocab=vocab("bigrams:"), trigram_vocab=vocab("trigram:"),
        tiered_bigram_vocab=vocab("tierbi:"), tiered_trigram_vocab=vocab("tiertri:"),
        tiered_quadgram_vocab=vocab("tierquad:"), tiered_min_crit=minimums,
        tiered_branch_min_crit=branches,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan", type=Path, default=Path("../scan"))
    parser.add_argument("--output", type=Path, default=Path("out/diagnostics/ngram-parity"))
    parser.add_argument("--reports", type=Path, help="JSON array of additional reports")
    args = parser.parse_args()
    # A repeatable fixture should not inherit an operator's feature ablations.
    for key in list(os.environ):
        if key.startswith("COLLIMATOR_"):
            del os.environ[key]
    for name in ("TIERED_CRIT_BIGRAMS", "TIERED_CRIT_TRIGRAMS", "TIERED_CRIT_QUADGRAMS"):
        os.environ["COLLIMATOR_" + name] = "1"
    os.environ["COLLIMATOR_CONFIDENCE_WEIGHTED_NGRAMS"] = "0"
    reports = boundary_reports()
    if args.reports:
        reports.extend(json.loads(args.reports.read_text()))
    results = []
    for abi in (19, 20):
        for depth in (2, 3, 4, 5):
            os.environ["COLLIMATOR_TRAIT_PATH_DEPTH"] = str(depth)
            f.feature_config_from_env.cache_clear()
            for overrides in (False, True):
                spec = make_spec(reports, abi, depth, overrides)
                directory = args.output / f"v{abi}-depth{depth}-floors{int(overrides)}"
                directory.mkdir(parents=True, exist_ok=True)
                spec.save(directory / "feature_spec.json")
                fixture = {"n_features": spec.total_features, "feature_names": spec.feature_names,
                           "samples": [{"report": compact(r), "expected_features": f.extract(r, spec).tolist()}
                                       for r in reports]}
                (directory / "extraction_fixture.json").write_text(json.dumps(fixture))
                result = subprocess.run([
                    "cargo", "test", "--manifest-path", str(args.scan.resolve() / "Cargo.toml"),
                    "--test", "extraction_parity", "feature_extraction_matches_collimator",
                    "--", "--ignored", "--exact",
                ], env={**os.environ, "SCAN_MODELS_DIR": str(directory.resolve())},
                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                (directory / "result.log").write_text(result.stdout)
                print(f"{directory.name}: {'PASS' if result.returncode == 0 else 'FAIL'} ({len(reports)} reports)", flush=True)
                results.append({"case": directory.name, "reports": len(reports), "passed": result.returncode == 0})
                (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
                if result.returncode:
                    print(result.stdout[-8000:])
                    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
