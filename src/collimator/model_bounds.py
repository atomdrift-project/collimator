"""Conservative probability bounds for exported binary LightGBM ensembles."""

from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.special import expit

from . import bundle


def probability_bounds(root: Path) -> tuple[float, float] | None:
    """Bound every possible input by summing independent per-tree leaf extrema.

    Some combinations of leaves may be impossible: bounds are conservative.
    Return None for unsupported graphs rather than guess their output semantics.
    """
    import onnx

    bounds = []
    for path in bundle.model_files(root):
        if path.suffix != ".onnx":
            return None
        graph = onnx.load(path)
        classifiers = [n for n in graph.graph.node if n.op_type == "TreeEnsembleClassifier"]
        if len(classifiers) != 1:
            return None
        classifier = classifiers[0]
        # Exporters may wrap probabilities in Identity and multiplication by 1.
        # Follow only proven no-op transformations through to the graph output.
        outputs = {classifier.output[1]}
        ones = {v.name for v in graph.graph.initializer if np.all(onnx.numpy_helper.to_array(v) == 1)}
        for node in graph.graph.node:
            if (node.op_type == "Identity" and node.input[0] in outputs
                    or node.op_type == "Mul" and len(node.input) == 2
                    and any(node.input[i] in outputs and node.input[1-i] in ones for i in (0, 1))):
                outputs.update(node.output)
        if not any(output.name in outputs for output in graph.graph.output):
            return None
        attrs = {a.name: onnx.helper.get_attribute_value(a) for a in classifier.attribute}
        if (attrs.get("post_transform") != b"LOGISTIC"
                or attrs.get("classlabels_int64s") != [0, 1]
                or set(attrs.get("class_ids", [])) != {0}
                or attrs.get("base_values")):
            return None
        trees = defaultdict(list)
        for tree, weight in zip(attrs["class_treeids"], attrs["class_weights"], strict=True):
            trees[tree].append(weight)
        low = expit(sum(min(weights) for weights in trees.values()))
        high = expit(sum(max(weights) for weights in trees.values()))
        bounds.append((low, high))
    if not bounds:
        return None
    low, high = np.mean(bounds, axis=0)
    # Allow floating point accumulation differences at the inference boundary.
    return max(0., float(low) - 1e-6), min(1., float(high) + 1e-6)
