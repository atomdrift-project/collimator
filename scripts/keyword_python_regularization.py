#!/usr/bin/env python3
"""Follow the Python selector screen with two isolated regularization changes."""
import argparse
import json
import os
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import scipy.sparse as sp

from keyword_python_selection import fit_variant, features, atomic_write_json, matrix_digest


def main(root):
    comparison = json.loads((root / "comparison.json").read_text())
    if len(comparison["variants"]) < 13:
        raise ValueError("finish the selector screen first")
    original = comparison["inputs"]
    os.environ.update(original["feature_env"])
    features.feature_config_from_env.cache_clear()
    base = sp.load_npz(root / "inputs/base.npz")
    assert matrix_digest(base) == original["base_sha256"]
    with np.load(root / "inputs/rows.npz") as rows:
        y_train, y_dev = rows["train_labels"], rows["dev_labels"]
    n = len(y_train)
    for parent in ("baseline", "ruletextword-frequency-1000", "ruletextword-balanced_mi-5000"):
        spec = features.FeatureSpec.load(root / parent / "feature_spec.json")
        matrix = base
        for source, words in spec.keyword_vocabs.items():
            info = json.loads((root / "inputs" / f"{source}.json").read_text())
            keywords = sp.load_npz(root / "inputs" / f"{source}.npz")
            assert matrix_digest(keywords) == info["matrix_sha256"]
            lookup = {word: i for i, word in enumerate(info["words"])}
            matrix = sp.hstack([base, keywords[:, [lookup[word] for word in words]]], format="csr")
        assert matrix_digest(matrix[:n]) == comparison["variants"][parent]["train_sha256"]
        for suffix, overrides in (("leaf300", {"min_child_samples": 300}), ("lambda5", {"reg_lambda": 5.})):
            name = parent + "-" + suffix
            if name in comparison["variants"]:
                continue
            print(f"Starting {name}", flush=True)
            result = fit_variant(SimpleNamespace(output=root), name, spec, matrix[:n], matrix[n:],
                                 y_train, y_dev, original, overrides)
            result["selection_parent"] = parent
            result["regularization_override"] = overrides
            atomic_write_json(root / name / "result.json", result)
            comparison["variants"][name] = result
            atomic_write_json(root / "comparison.json", comparison)
    print("Regularization screen complete", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    main(parser.parse_args().root)
