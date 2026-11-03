#!/usr/bin/env python3
"""Export real keyword models and prepare Python/vector/ONNX fixtures for Scan.

`fetch` reads a small, fixed selection of saved development row IDs in a fresh
read-only snapshot. `build` needs only that saved report file and native models.
No model is trained, promoted, or installed by this script.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

import lightgbm as lgb
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from collimator import features
from collimator.export import export_lightgbm_onnx
from extended_keyword_parity_fixture import fixtures as extended_fixtures

ROOT = Path("out/experiments/keyword-scan-parity")
PE = Path("out/experiments/keyword-pe-search")
MACHO = Path("out/experiments/keyword-macho-search")
BUNDLES = {
    "pe-winner": PE / "confirmation/best-sources-plus-context",
    "pe-descriptions-ids": PE / "search/best-sources-combined",
    "pe-ids": PE / "confirmation/ruleword-balanced_mi-1000-5",
    "pe-descriptions": PE / "confirmation/descword-frequency-1000-5",
    "pe-hierarchy": PE / "search/fullword-frequency-1000-5",
    "pe-pooled": PE / "search/ruletextword-balanced_mi-1000-5",
    "pe-context": PE / "confirmation/contextword-frequency-1000-5",
    "macho-pooled-context": MACHO / "confirmation/best-sources-combined",
}


def fetch(args):
    from collimator import data
    from collimator.corpus_snapshot import frozen_corpus
    selected = {}
    for route, root, winner in (("pe", PE, "best-sources-plus-context"),
                                ("macho", MACHO, "best-sources-combined")):
        with np.load(root / "inputs/rows.npz") as arrays:
            labels, mask = arrays["y_dev"], ~arrays["search"]
            ids = arrays["row_ids"][len(arrays["y_train"]):]
        with np.load(root / "confirmation" / winner / "predictions.npz") as arrays:
            scores = arrays["ensemble"]
        for label in (0, 1):
            rows = np.flatnonzero(mask & (labels == label))
            ranked = rows[np.argsort(scores[rows], kind="stable")]
            chosen = set(ranked[np.linspace(0, len(ranked)-1, 4, dtype=int)])
            chosen.update(ranked[-4:] if label == 0 else ranked[:4])
            for index in chosen:
                selected[int(ids[index])] = (route, int(label))
        with np.load(root / "confirmation/baseline/predictions.npz") as arrays:
            rows = np.flatnonzero(mask & (labels == 0))
            for index in rows[np.argsort(arrays["ensemble"][rows], kind="stable")[-4:]]:
                selected[int(ids[index])] = (route, 0)
    args.output.mkdir(parents=True, exist_ok=True)
    if (args.output / "reports.json").exists():
        raise ValueError("reports already captured; use a new output directory for another snapshot")
    with frozen_corpus(args.db) as snapshot:
        fetched = data.fetch_cleave_results(args.db, sorted(selected),
                                           evaluation_labels={rid: label for rid, (_, label) in selected.items()})
        if set(fetched) != set(selected):
            raise ValueError("missing selected development reports")
        reports = []
        for rid in sorted(selected):
            report = features._coerce_report(fetched[rid]["cleave_result"])
            if report is None:
                raise ValueError(f"invalid report {rid}")
            route, label = selected[rid]
            reports.append(dict(name=f"{route}-{rid}", row_id=rid, label=label, report=report))
    payload = dict(scope="Runtime parity on fresh reports from saved development IDs; not a new accuracy evaluation.",
                   snapshot=snapshot, cases=reports)
    (args.output / "reports.json").write_text(json.dumps(payload, separators=(",", ":")) + "\n")
    print(f"Captured {len(reports)} real PE/Mach-O reports", flush=True)


def serving_report(report):
    """Adapt archived database schemas to Scan's current typed report input.

    This is fixture preparation, not a new Scan wire-format importer. The build
    checks the entire Python vector before and after conversion for every spec.
    Current fields and Z85 windows pass through; old aliases and display-text
    windows are converted to their current representations.
    """
    result = json.loads(json.dumps(report))
    files = features.report_files(result)
    result["files"] = files
    result.pop("fs", None)
    depths = features.report_depths(files)
    for file, depth in zip(files, depths, strict=True):
        facts = features.file_facts(file)
        normalized_facts = dict(facts)
        normalized_facts["metrics"] = features.file_metrics(file)
        normalized_facts["imp"] = [
            raw if isinstance(raw, list) else ["", raw]
            for raw in features.file_imports(file)
        ]
        for new, old in (("exp", "x"), ("funcs", "fn"), ("tgt", "ct"), ("mbr", "mc"), ("sec", "sc")):
            value = features._alias(facts, new, old)
            if value is not None:
                normalized_facts[new] = value
        findings = []
        for finding in features.file_findings(file):
            finding = dict(finding)
            for new, old in (("id", "i"), ("crit", "l"), ("conf", "c"),
                             ("desc", "d"), ("atk", "a"), ("mbc", "m")):
                value = features._alias(finding, new, old)
                if value is not None:
                    finding[new] = value
            findings.append(finding)
        file.update(size=features.file_size(file), mol=features.file_formula(file),
                    risk=features.file_risk(file) or 0, depth=depth,
                    facts=normalized_facts, traits=findings)
        for window in file.get("ctx", []):
            if "ln" not in window:
                window["ln"] = window.get("l", 0)
            if window.get("t") is not None:
                raw = features._decode_context_window(window)
                window.clear()
                window.update(ln=0, s="".join(chr(b or 256) for b in raw))
    return result


def current_runtime_report(report):
    """Represent a stored row as a freshly emitted standalone Cleave report.

    This is deliberately separate from lossless schema conversion. Historical
    rows can retain enclosing-archive placement and f32 confidences serialized
    as full f64 values. Current Cleave emits shortest f32 decimals. Changes in
    reference vectors from these two input differences are recorded in audit.
    """
    result = json.loads(json.dumps(report))
    if len(result["files"]) == 1:
        file = result["files"][0]
        file["depth"] = 0
        for key in ("pid", "p", "dp"):
            file.pop(key, None)
    for file in result["files"]:
        for finding in file.get("traits", []):
            if "conf" in finding:
                finding["conf"] = float(str(np.float32(finding["conf"])))
    return result


def build(args):
    import onnxruntime as ort
    records = json.loads((args.output / "reports.json").read_text())["cases"]
    records += [dict(name="synthetic-" + f["name"], report=f.get("training_report", f["report"]))
                for f in extended_fixtures()]
    sessions = ort.SessionOptions()
    sessions.intra_op_num_threads = 1
    sessions.inter_op_num_threads = 1
    output, audit = [], []
    for name, source in BUNDLES.items():
        feature_env = json.loads((source.parents[1] / "inputs.json").read_text())["feature_env"]
        for key in list(os.environ):
            if key.startswith("COLLIMATOR_"):
                del os.environ[key]
        os.environ.update(feature_env)
        features.feature_config_from_env.cache_clear()
        features.allowed_features.cache_clear()
        result = json.loads((source / "result.json").read_text())
        spec = features.FeatureSpec.load(source / "feature_spec.json")
        directory = (args.output / "bundles" / name).resolve()
        (directory / "models").mkdir(parents=True, exist_ok=True)
        (directory / "feature_spec.json").write_bytes((source / "feature_spec.json").read_bytes())
        vectors, reports, input_changes = [], [], []
        for record in records:
            archived = features.extract(record["report"], spec)
            normalized = serving_report(record["report"])
            np.testing.assert_array_equal(archived, features.extract(normalized, spec))
            normalized = current_runtime_report(normalized)
            vector = features.extract(normalized, spec)
            changed = np.flatnonzero(vector != archived)
            if len(changed):
                input_changes.append(dict(name=record["name"], changed_columns=len(changed),
                    columns=[spec.feature_names[i] for i in changed],
                    max_absolute_change=float(np.max(np.abs(vector - archived)))))
            vectors.append(vector)
            reports.append(normalized)
        matrix = np.stack(vectors).astype(np.float32)
        native, onnx = [], []
        for seed in result["seeds"]:
            model = lgb.Booster(model_file=str(source / f"seed_{seed}.txt"))
            path = directory / "models" / f"seed_{seed}.onnx"
            if not export_lightgbm_onnx(model, spec.total_features, path):
                raise ValueError(f"failed ONNX export: {path}")
            reference = np.asarray(model.predict(matrix, num_threads=4), dtype=np.float32)
            session = ort.InferenceSession(str(path), sess_options=sessions, providers=["CPUExecutionProvider"])
            converted = np.asarray(session.run(None, {session.get_inputs()[0].name: matrix})[1][:, 1], dtype=np.float32)
            np.testing.assert_allclose(converted, reference, rtol=0, atol=1e-5)
            native.append(reference.astype(np.float64))
            onnx.append(converted.astype(np.float64))
        probabilities = np.mean(native, axis=0).astype(np.float32)
        difference = float(np.max(np.abs(np.mean(onnx, axis=0) - probabilities)))
        cases = [dict(name=record["name"], report=report, expected=vector.tolist(), probability=float(probability))
                 for record, report, vector, probability in zip(records, reports, vectors, probabilities, strict=True)]
        output.append(dict(directory=str(directory), cases=cases))
        audit.append(dict(name=name, source=str(source), sources=sorted(spec.keyword_vocabs),
                          seeds=result["seeds"], cases=len(cases), features=spec.total_features,
                          max_python_onnx_error=difference,
                          feature_env=feature_env,
                          archive_to_current_input_changes=input_changes))
        print(f"Exported {name}: {len(result['seeds'])} seeds, {len(cases)} cases, max ONNX error {difference:.2g}", flush=True)
    path = args.output / "bundle_cases.json"
    path.write_text(json.dumps(output, separators=(",", ":")) + "\n")
    (args.output / "python_onnx_audit.json").write_text(json.dumps(dict(
        bundles=audit, reports_sha256=hashlib.sha256((args.output / "reports.json").read_bytes()).hexdigest(),
        cases_sha256=hashlib.sha256(path.read_bytes()).hexdigest()), indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("fetch", "build"))
    parser.add_argument("--output", type=Path, default=ROOT)
    parser.add_argument("--db", default="postgres://hopper@localhost:5432/hopper")
    args = parser.parse_args()
    {"fetch": fetch, "build": build}[args.action](args)
