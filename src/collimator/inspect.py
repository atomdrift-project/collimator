"""Inspect individual samples: predictions, feature vectors, SHAP breakdowns."""

from __future__ import annotations

import json
import logging
import subprocess
import sys
from pathlib import Path

import numpy as np

from .features import (
    FeatureSpec,
    extract,
    primary_file,
    standardize,
)
from .model import load_model, predict_proba

log = logging.getLogger(__name__)


def _predict(model: object, vec: np.ndarray) -> float:
    return float(predict_proba(model, vec.reshape(1, -1))[0])


def _print_feature_vector(vec: np.ndarray, spec: FeatureSpec, top_n: int = 30) -> None:
    """Print the non-zero features, sorted by absolute value."""
    nonzero = [(i, vec[i]) for i in range(len(vec)) if vec[i] != 0.0]
    nonzero.sort(key=lambda x: abs(x[1]), reverse=True)

    print(f"\nFeature vector ({len(nonzero)} non-zero of {spec.total_features}):")
    print(f"{'Feature':<55} {'Value':>10}")
    print(f"{'-' * 66}")
    for idx, val in nonzero[:top_n]:
        name = spec.feature_names[idx]
        print(f"  {name:<53} {val:>10.3f}")
    if len(nonzero) > top_n:
        print(f"  ... and {len(nonzero) - top_n} more")


def _print_shap_breakdown(
    model: object,
    vec: np.ndarray,
    spec: FeatureSpec,
    vec_raw: np.ndarray | None = None,
) -> None:
    """Per-sample SHAP breakdown using TreeExplainer."""
    try:
        import shap
    except ImportError:
        print("\nSHAP not installed, skipping per-sample breakdown")
        return

    display = vec_raw if vec_raw is not None else vec

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(vec.reshape(1, -1))

    if isinstance(shap_values, list):
        shap_values = shap_values[0]
    sv = np.array(shap_values).squeeze()

    sorted_idx = np.argsort(np.abs(sv))[::-1]

    print("\nSHAP Breakdown (top 30 features driving this prediction):")
    print(f"{'Feature':<55} {'SHAP':>10} {'Value':>10}")
    print(f"{'-' * 76}")
    for idx in sorted_idx[:30]:
        name = spec.feature_names[idx]
        print(f"  {name:<53} {sv[idx]:>+10.4f} {display[idx]:>10.3f}")

    pos_sum = float(np.sum(sv[sv > 0]))
    neg_sum = float(np.sum(sv[sv < 0]))
    print(f"\n  Total push toward malware:  {pos_sum:>+.4f}")
    print(f"  Total push toward benign:  {neg_sum:>+.4f}")


def inspect_sample(
    sha256: str,
    db_path: Path,
    model_path: Path,
    spec_path: Path,
) -> None:
    """Inspect a single sample from the database."""
    import sqlite3

    spec = FeatureSpec.load(spec_path)
    model = load_model(model_path)

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT sha256, path, status, cleave_json FROM samples WHERE sha256 LIKE ?",
        (f"{sha256}%",),
    ).fetchone()
    conn.close()

    if not row:
        print(f"No sample found matching '{sha256}'")
        sys.exit(1)

    report = json.loads(row["cleave_json"])
    pf = primary_file(report)
    vec_raw = extract(report, spec)
    vec = standardize(vec_raw, spec)
    prob = _predict(model, vec)

    print(f"Sample:      {row['sha256']}")
    print(f"Path:        {row['path']}")
    print(f"Status:      {row['status']}")
    print(f"Prediction:  {prob:.4f} ({'MALWARE' if prob > 0.5 else 'BENIGN'})")
    print(f"File type:   {pf.get('file_type', 'unknown')}")
    print(f"Findings:    {len(pf.get('findings') or [])}")

    _print_feature_vector(vec_raw, spec)
    _print_shap_breakdown(model, vec, spec, vec_raw=vec_raw)


def inspect_errors(
    db_path: Path,
    model_path: Path,
    spec_path: Path,
    top_n: int = 20,
) -> None:
    """Show misclassified samples with top contributing features."""
    from . import data

    spec = FeatureSpec.load(spec_path)
    model = load_model(model_path)
    samples = data.load_samples(db_path)

    if not samples:
        print("No samples found")
        return

    vecs_raw = np.array(
        [extract(s.report, spec) for s in samples], dtype=np.float32,
    )
    vecs = standardize(vecs_raw, spec)
    probs = predict_proba(model, vecs)

    false_positives = []
    false_negatives = []
    for i, sample in enumerate(samples):
        predicted = int(probs[i] > 0.5)
        if sample.label == 0 and predicted == 1:
            false_positives.append((i, probs[i], sample))
        elif sample.label == 1 and predicted == 0:
            false_negatives.append((i, probs[i], sample))

    false_positives.sort(key=lambda x: x[1], reverse=True)
    false_negatives.sort(key=lambda x: x[1])

    total = len(samples)
    n_correct = total - len(false_positives) - len(false_negatives)
    print(f"Total samples:    {total}")
    print(f"Correct:          {n_correct} ({100 * n_correct / total:.1f}%)")
    print(f"False positives:  {len(false_positives)} (benign flagged as malware)")
    print(f"False negatives:  {len(false_negatives)} (malware missed)")

    if false_positives:
        print(f"\nTop {min(top_n, len(false_positives))} False Positives "
              "(benign samples scored as malware):")
        print(f"  {'Score':>7} {'SHA256':<20} {'Path'}")
        print(f"  {'-' * 60}")
        for _, prob, sample in false_positives[:top_n]:
            sha_short = sample.sha256[:16]
            print(f"  {prob:>7.4f} {sha_short:<20} {sample.path}")

    if false_negatives:
        print(f"\nTop {min(top_n, len(false_negatives))} False Negatives "
              "(malware samples scored as benign):")
        print(f"  {'Score':>7} {'SHA256':<20} {'Path'}")
        print(f"  {'-' * 60}")
        for _, prob, sample in false_negatives[:top_n]:
            sha_short = sample.sha256[:16]
            print(f"  {prob:>7.4f} {sha_short:<20} {sample.path}")


def scan_file(
    file_path: str,
    model_path: Path,
    spec_path: Path,
    cleave_bin: str = "cleave",
) -> None:
    """Run cleave on a file and score it with the trained model."""
    spec = FeatureSpec.load(spec_path)
    model = load_model(model_path)

    try:
        result = subprocess.run(
            [cleave_bin, "--format=json", file_path],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except FileNotFoundError:
        print(f"cleave not found at '{cleave_bin}'. "
              "Install cleave or pass --cleave=/path/to/cleave")
        sys.exit(1)

    if result.returncode != 0:
        print(f"cleave failed (exit {result.returncode}):")
        print(result.stderr)
        sys.exit(1)

    report = json.loads(result.stdout)
    pf = primary_file(report)
    vec_raw = extract(report, spec)
    vec = standardize(vec_raw, spec)
    prob = _predict(model, vec)

    findings = pf.get("findings") or []
    hostile = sum(1 for f in findings if f.get("crit") == "hostile")
    suspicious = sum(1 for f in findings if f.get("crit") == "suspicious")

    print(f"File:        {file_path}")
    print(f"File type:   {pf.get('file_type', 'unknown')}")
    print(f"Prediction:  {prob:.4f} ({'MALWARE' if prob > 0.5 else 'BENIGN'})")
    print(f"Findings:    {len(findings)} ({hostile} hostile, {suspicious} suspicious)")

    _print_feature_vector(vec_raw, spec)
    _print_shap_breakdown(model, vec, spec, vec_raw=vec_raw)
