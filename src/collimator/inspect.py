"""Inspect individual samples: predictions, feature vectors, SHAP breakdowns."""

from __future__ import annotations

import json
import heapq
import logging
import subprocess
import sys
from pathlib import Path

import numpy as np

from .features import (
    FeatureSpec,
    extract,
    extract_all,
    primary_file,
    standardize,
)
from .export import load_threshold
from .model import load_model, predict_proba

log = logging.getLogger(__name__)


def _predict(model: object, vec: np.ndarray) -> float:
    return float(predict_proba(model, vec.reshape(1, -1))[0])


def _score_report(
    model: object,
    spec: FeatureSpec,
    report: dict[str, object],
) -> tuple[np.ndarray, np.ndarray, float]:
    """Extract features for one report and return raw vec, model vec, probability."""
    vec_raw = extract(report, spec)
    vec = standardize(vec_raw, spec) if spec.standardized else vec_raw
    return vec_raw, vec, _predict(model, vec)

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
    db_path: Path | str,
    model_path: Path,
    spec_path: Path,
) -> None:
    """Inspect a single sample from the database."""
    from . import data as datamod

    spec = FeatureSpec.load(spec_path)
    model = load_model(model_path)
    eval_path = model_path.parent / "evaluation.json"
    threshold = load_threshold(eval_path)
    if eval_path.exists():
        log.info("using threshold %.3f from %s", threshold, eval_path)

    result = datamod.lookup_sample(db_path, sha256)
    if not result:
        print(f"No sample found matching '{sha256}'")
        sys.exit(1)

    sample_sha, sample_path, sample_label, report = result
    pf = primary_file(report)
    vec_raw, vec, prob = _score_report(model, spec, report)

    print(f"Sample:      {sample_sha}")
    print(f"Path:        {sample_path}")
    print(f"Label:       {sample_label}")
    print(f"Prediction:  {prob:.4f} ({'MALWARE' if prob > threshold else 'BENIGN'})")
    print(f"File type:   {pf.get('file_type', 'unknown')}")
    print(f"Findings:    {len(pf.get('findings') or [])}")

    _print_feature_vector(vec_raw, spec)
    _print_shap_breakdown(model, vec, spec, vec_raw=vec_raw if spec.standardized else None)


def inspect_errors(
    db_path: Path | str,
    model_path: Path,
    spec_path: Path,
    top_n: int = 20,
) -> None:
    """Show misclassified samples with top contributing features."""
    from . import data

    spec = FeatureSpec.load(spec_path)
    model = load_model(model_path)
    eval_path = model_path.parent / "evaluation.json"
    threshold = load_threshold(eval_path)
    if eval_path.exists():
        log.info("using threshold %.3f from %s", threshold, eval_path)
    batch_size = 1024
    sample_batch: list[data.Sample] = []
    report_batch: list[dict[str, object]] = []
    label_batch: list[int] = []
    false_positives: list[tuple[float, data.Sample]] = []
    false_negatives: list[tuple[float, data.Sample]] = []
    total = 0
    n_correct = 0
    total_fp = 0
    total_fn = 0

    def _score_batch() -> None:
        nonlocal total, n_correct, total_fp, total_fn
        if not sample_batch:
            return
        X, _ = extract_all(report_batch, label_batch, spec)
        vecs = standardize(X, spec) if spec.standardized else X
        probs = predict_proba(model, vecs)
        for prob, sample in zip(probs, sample_batch, strict=False):
            total += 1
            predicted = int(prob > threshold)
            if sample.label == predicted:
                n_correct += 1
                continue
            if sample.label == 0:
                total_fp += 1
                heapq.heappush(false_positives, (float(prob), sample.sha256, sample))
                if len(false_positives) > top_n:
                    heapq.heappop(false_positives)
            else:
                total_fn += 1
                heapq.heappush(false_negatives, (-float(prob), sample.sha256, sample))
                if len(false_negatives) > top_n:
                    heapq.heappop(false_negatives)
        sample_batch.clear()
        report_batch.clear()
        label_batch.clear()

    for sample in data.stream_samples(db_path):
        sample_batch.append(sample)
        report_batch.append(sample.report)
        label_batch.append(sample.label)
        if len(sample_batch) >= batch_size:
            _score_batch()
    _score_batch()

    if total == 0:
        print("No samples found")
        return

    false_positives.sort(key=lambda x: x[0], reverse=True)
    false_negatives = [(-score, sha, sample) for score, sha, sample in false_negatives]
    false_negatives.sort(key=lambda x: x[0])

    print(f"Total samples:    {total}")
    print(f"Correct:          {n_correct} ({100 * n_correct / total:.1f}%)")
    print(f"False positives:  {total_fp} (benign flagged as malware)")
    print(f"False negatives:  {total_fn} (malware missed)")

    if false_positives:
        print(f"\nTop {min(top_n, len(false_positives))} False Positives "
              "(benign samples scored as malware):")
        print(f"  {'Score':>7} {'SHA256':<20} {'Path'}")
        print(f"  {'-' * 60}")
        for prob, _, sample in false_positives[:top_n]:
            sha_short = sample.sha256[:16]
            print(f"  {prob:>7.4f} {sha_short:<20} {sample.path}")

    if false_negatives:
        print(f"\nTop {min(top_n, len(false_negatives))} False Negatives "
              "(malware samples scored as benign):")
        print(f"  {'Score':>7} {'SHA256':<20} {'Path'}")
        print(f"  {'-' * 60}")
        for prob, _, sample in false_negatives[:top_n]:
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
    eval_path = model_path.parent / "evaluation.json"
    threshold = load_threshold(eval_path)
    if eval_path.exists():
        log.info("using threshold %.3f from %s", threshold, eval_path)

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
    vec_raw, vec, prob = _score_report(model, spec, report)
    effective_prob = prob
    promoted_path: str | None = None
    promoted_type: str | None = None

    embedded_files = [
        file_entry
        for file_entry in report.get("fs") or []
        if isinstance(file_entry, dict) and int(file_entry.get("dp", 0) or 0) > 0
    ]
    for file_entry in embedded_files:
        _ef_raw, _ef_vec, ef_prob = _score_report(
            model,
            spec,
            {"fs": [file_entry], "v": "4"},
        )
        if ef_prob > effective_prob:
            effective_prob = ef_prob
            full_path = str(file_entry.get("path", ""))
            promoted_path = full_path.rsplit("!!", 1)[-1] if full_path else None
            promoted_type = str(file_entry.get("type", "unknown"))

    findings = pf.get("ts") or []
    hostile = sum(1 for f in findings if f.get("l") == 5)
    suspicious = sum(1 for f in findings if f.get("l") == 4)

    print(f"File:        {file_path}")
    print(f"File type:   {pf.get('type', 'unknown')}")
    print(
        f"Prediction:  {effective_prob:.4f} "
        f"({'MALWARE' if effective_prob > threshold else 'BENIGN'})"
    )
    if effective_prob != prob:
        print(f"Report score: {prob:.4f} (top-level report only)")
        print(
            f"Promoted by:  {promoted_path or '<embedded>'} "
            f"[{promoted_type or 'unknown'}] -> {effective_prob:.4f}"
        )
    print(f"Findings:    {len(findings)} ({hostile} hostile, {suspicious} suspicious)")

    _print_feature_vector(vec_raw, spec)
    _print_shap_breakdown(model, vec, spec, vec_raw=vec_raw if spec.standardized else None)
