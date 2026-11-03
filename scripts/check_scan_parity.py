#!/usr/bin/env python3
"""Cross-repository feature and ONNX parity gate; no database or live models needed.

By default, train/export tiny two-seed models with every keyword combination
and a discovered base layout. Optionally check an existing Azoth leaf bundle
with its saved training feature environment. Calibration/routing are excluded:
this gate compares the raw per-model calculation, before policy decisions.
"""
import argparse
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import lightgbm as lgb
import numpy as np
import onnxruntime as ort

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from collimator import features
from collimator.export import export_lightgbm_onnx
from keyword_combination_parity_fixture import fixtures


def environment(values):
    for key in list(os.environ):
        if key.startswith("COLLIMATOR_"):
            del os.environ[key]
    os.environ.update(values)
    features.feature_config_from_env.cache_clear()
    features.allowed_features.cache_clear()


def reports():
    cases = [{"name": f["name"], "report": f["report"]} for f in fixtures()[:9]]
    for i, confidence in enumerate((0.0, 0.1, 0.6499999, 0.65, 0.7, 0.9, 1.0)):
        file = dict(id=0, path="sample.exe", type="pe", sha=f"synthetic-{i}",
                    size=1024 * (i + 1), risk=i * 3, mol="H₂O",
                    traits=[dict(id="objectives/execution/shell::curl_download_post",
                                 desc="Download via HTTP POST", conf=confidence, crit=5,
                                 atk="T1059.001", mbc="B0001"),
                            dict(id="metadata/signed::verified", desc="Verified signature",
                                 conf=1.0, crit=2)],
                    facts=dict(metrics=dict(file=dict(size=1024 * (i + 1)),
                                            binary=dict(overall_entropy=i / 2),
                                            pe=dict(has_signature=i % 2)),
                               imp=[["kernel32", "CreateProcessW"]]),
                    ctx=[dict(ln=0, s="curl fetch_token" if i % 2 else "verified signature")])
        cases.append(dict(name=f"confidence-{confidence}", report=dict(v="9", files=[file])))
    cases.append(dict(name="empty-report", report=dict(v="9", files=[])))
    return cases


def reference(directory, spec, cases, natives=None):
    matrix = np.stack([features.extract(case["report"], spec) for case in cases])
    model_input = features.standardize(matrix, spec) if spec.standardized else matrix
    options = ort.SessionOptions()
    options.intra_op_num_threads = options.inter_op_num_threads = 1
    paths = sorted((directory / "models").glob("*.onnx"))
    if not paths:
        paths = [directory / "model.onnx"]
    scores = []
    for i, path in enumerate(paths):
        session = ort.InferenceSession(str(path), options, providers=["CPUExecutionProvider"])
        outputs = session.run(None, {session.get_inputs()[0].name: model_input})
        probabilities = next(value for output, value in zip(session.get_outputs(), outputs, strict=True)
                             if "prob" in output.name.lower())
        score = np.asarray(probabilities, dtype=np.float32)[:, 1]
        if natives is not None:
            native = np.asarray(natives[i].predict(model_input, num_threads=1), dtype=np.float32)
            np.testing.assert_allclose(score, native, atol=1e-5, rtol=0)
            score = native
        scores.append(score.astype(np.float64))
    probability = np.mean(scores, axis=0).astype(np.float32)
    return dict(directory=str(directory), cases=[dict(
        **case, expected=vector.tolist(), probability=float(score))
        for case, vector, score in zip(cases, matrix, probability, strict=True)])


def generate(output, args):
    environment({})
    cases = reports()
    # Enough repetitions for normal vocabulary support floors, without a DB.
    base = features.build_vocab([case["report"] for case in cases] * 32, n_workers=1)
    combinations = [None] + [f["spec"] for f in fixtures()[::9]]
    combinations.append(combinations[-1])  # Also exercise z-score preprocessing.
    bundles = []
    for index, keyword_spec in enumerate(combinations):
        vocab = keyword_spec["keyword_vocabs"] if keyword_spec else {}
        names = base.feature_names + [f"{s}:{w}" for s, words in vocab.items() for w in words]
        spec = replace(base, version=23 if vocab else base.version,
                       abi_version=23 if vocab else base.abi_version,
                       base_feature_abi=base.abi_version if vocab else None,
                       keyword_vocabs=vocab, feature_names=names, total_features=len(names))
        if index == len(combinations) - 1:
            spec = replace(spec, standardized=True,
                           feature_means=[0.25] * len(names), feature_stds=[2.0] * len(names))
        directory = output / f"synthetic-{index:02d}"
        (directory / "models").mkdir(parents=True)
        spec.save(directory / "feature_spec.json")
        matrix = np.stack([features.extract(case["report"], spec) for case in cases])
        if spec.standardized:
            matrix = features.standardize(matrix, spec)
        natives = []
        for seed in (43, 44):
            classifier = lgb.LGBMClassifier(n_estimators=4, num_leaves=4,
                min_child_samples=1, min_data_in_bin=1, n_jobs=1, verbosity=-1,
                random_state=seed, colsample_bytree=0.8)
            classifier.fit(matrix, np.arange(len(cases)) % 2)
            booster = classifier.booster_
            if not export_lightgbm_onnx(booster, spec.total_features,
                                        directory / "models" / f"seed_{seed}.onnx"):
                raise RuntimeError("ONNX export failed")
            natives.append(booster)
        bundles.append(reference(directory, spec, cases, natives))
    if args.bundle:
        saved = json.loads(args.feature_env.read_text())
        environment(saved.get("feature_env", saved))
        source = args.bundle.resolve()
        directory = output / "existing-bundle"
        directory.mkdir()
        shutil.copy2(source / "feature_spec.json", directory / "feature_spec.json")
        paths = sorted((source / "models").glob("*.onnx"))
        if paths:
            (directory / "models").mkdir()
            for path in paths:
                shutil.copy2(path, directory / "models" / path.name)
        else:
            shutil.copy2(source / "model.onnx", directory / "model.onnx")
        spec = features.FeatureSpec.load(directory / "feature_spec.json")
        bundles.append(reference(directory, spec, cases))
    path = output / "cases.json"
    path.write_text(json.dumps(bundles, separators=(",", ":")) + "\n")
    print(f"Checking {len(bundles)} bundles × {len(cases)} reports; "
          f"{base.total_features} base columns plus keyword combinations", flush=True)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan-dir", type=Path, default=ROOT.parent / "scan")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--bundle", type=Path, help="optional existing Azoth leaf model directory")
    parser.add_argument("--feature-env", type=Path, help="that bundle's saved config/inputs JSON")
    args = parser.parse_args()
    if bool(args.bundle) != bool(args.feature_env):
        parser.error("--bundle and --feature-env must be supplied together")
    if not (args.scan_dir / "Cargo.toml").is_file():
        parser.error("Scan checkout required; use --scan-dir or SCAN_DIR in make")
    os.chdir(ROOT)
    with tempfile.TemporaryDirectory(prefix="collimator-scan-parity-") as tmp:
        output = args.output.resolve() if args.output else Path(tmp)
        output.mkdir(parents=True, exist_ok=True)
        path = generate(output, args)
        env = dict(os.environ, SCAN_PARITY_CASES=str(path))
        subprocess.run(["cargo", "test", "--manifest-path", str(args.scan_dir / "Cargo.toml"),
                        "--locked", "--offline", "--test", "keyword_bundle_parity", "--",
                        "--ignored", "--nocapture"], env=env, check=True)


if __name__ == "__main__":
    main()
