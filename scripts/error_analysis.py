
import argparse
import json
import logging
from pathlib import Path
import numpy as np
import scipy.sparse as sp

from collimator import data, features, model, export, thresholds

def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--model", default="out/model.json")
    parser.add_argument("--spec", default="out/feature_spec.json")
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    db_path = args.db
    spec = features.FeatureSpec.load(Path(args.spec))
    m = model.load_model(Path(args.model))
    
    eval_path = Path(args.model).parent / "evaluation.json"
    threshold = export.load_threshold(eval_path)
    print(f"Using threshold: {threshold:.4f}")

    # ONLY STREAM TEST SAMPLES
    print("Streaming external test samples (limit 5000)...")
    test_samples = []
    for s in data.stream_samples(db_path, only_test=True, limit=5000):
        test_samples.append(s)
    
    print(f"Loaded {len(test_samples)} test samples. Extracting features...")
    reports = [s.report for s in test_samples]
    labels = [s.label for s in test_samples]
    
    X, y = features.extract_all(reports, labels, spec)
    if spec.standardized:
        X = features.standardize(X, spec)
    
    probs = model.predict_proba(m, X)
    
    false_negatives = []
    for i, prob in enumerate(probs):
        if labels[i] == 1 and prob <= threshold:
            false_negatives.append((prob, test_samples[i]))
    
    false_negatives.sort(key=lambda x: x[0])
    
    print(f"\nTop {args.top} False Negatives on External Test Set:")
    print(f"{'Score':>7} {'SHA256':<20} {'Path'}")
    print("-" * 60)
    for prob, s in false_negatives[:args.top]:
        print(f"{prob:>7.4f} {s.sha256[:16]:<20} {s.path}")

if __name__ == "__main__":
    main()
