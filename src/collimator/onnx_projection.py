"""In-memory column projection for direct-input ONNX tree classifiers.

Only feature indices and the input width change. Thresholds, tree topology,
missing-value routing, class weights, and output operations stay untouched.
Unknown input consumers fall back to the original graph.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np


def _tree_inputs(model):
    import onnx

    graph = model.graph
    if len(graph.input) != 1 or model.functions:
        return None
    value = graph.input[0]
    tensor = value.type.tensor_type
    if tensor.elem_type != onnx.TensorProto.FLOAT or len(tensor.shape.dim) != 2:
        return None
    width = tensor.shape.dim[1].dim_value
    if (width < 1 or any(v.name == value.name for v in graph.initializer)
            or any(v.values.name == value.name for v in graph.sparse_initializer)):
        return None
    # A graph output or subgraph could observe the full input layout.
    if any(v.name == value.name for v in graph.output):
        return None
    trees, used = [], set()
    for node in graph.node:
        if any(a.type in (onnx.AttributeProto.GRAPH, onnx.AttributeProto.GRAPHS)
               for a in node.attribute):
            return None
        if value.name not in node.input:
            continue
        if (node.domain != 'ai.onnx.ml' or node.op_type != 'TreeEnsembleClassifier'
                or list(node.input) != [value.name]):
            return None
        attrs = {a.name: a for a in node.attribute}
        if 'nodes_featureids' not in attrs or 'nodes_modes' not in attrs:
            return None
        ids, modes = attrs['nodes_featureids'], attrs['nodes_modes']
        if len(ids.ints) != len(modes.strings):
            return None
        for index, mode in zip(ids.ints, modes.strings, strict=True):
            if mode == b'LEAF':
                continue
            if not mode.startswith(b'BRANCH_') or not 0 <= index < width:
                return None
            used.add(index)
        trees.append((ids, modes))
    return (width, trees, used) if trees else None


def project_tree_inputs(paths: list[Path]):
    """Return runtime payloads and one shared original-column mapping.

    All members must support the same input layout. Returning paths and no
    mapping preserves the existing loader for unsupported graphs or optional
    installations without the ONNX graph-editing package.
    """
    unchanged = ([str(p) for p in paths], None, None)
    try:
        import onnx
    except ImportError:
        return unchanged
    models = [onnx.load(str(p)) for p in paths]
    descriptions = [_tree_inputs(m) for m in models]
    if not descriptions or any(d is None for d in descriptions):
        return unchanged
    widths = {d[0] for d in descriptions}
    if len(widths) != 1:
        return unchanged
    width = widths.pop()
    used = set().union(*(d[2] for d in descriptions))
    # A constant ensemble still needs a non-empty rank-two runtime input.
    columns = np.array(sorted(used or {0}), dtype=np.int64)
    if len(columns) == width:
        return unchanged
    mapping = {int(column): i for i, column in enumerate(columns)}
    for model, (_, trees, _) in zip(models, descriptions, strict=True):
        model.graph.input[0].type.tensor_type.shape.dim[1].dim_value = len(columns)
        for ids, modes in trees:
            remapped = [0 if mode == b'LEAF' else mapping[index]
                        for index, mode in zip(ids.ints, modes.strings, strict=True)]
            del ids.ints[:]
            ids.ints.extend(remapped)
    columns.flags.writeable = False
    return [m.SerializeToString() for m in models], columns, width
