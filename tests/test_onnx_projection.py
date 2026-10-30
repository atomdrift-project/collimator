"""Column remapping must preserve tree decisions and full-layout callers."""
from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

onnx = pytest.importorskip('onnx')
pytest.importorskip('onnxruntime')
from onnx import TensorProto, helper

from collimator import bundle, model


def tree(path: Path, column=9, width=32, constant=False, input_identity=False, echo=False):
    attrs = dict(classlabels_int64s=[0, 1], post_transform='LOGISTIC',
                 nodes_treeids=[0] if constant else [0, 0, 0],
                 nodes_nodeids=[0] if constant else [0, 1, 2],
                 nodes_featureids=[0] if constant else [column, 0, 0],
                 nodes_modes=['LEAF'] if constant else ['BRANCH_LEQ', 'LEAF', 'LEAF'],
                 nodes_values=[0.] if constant else [.5, 0., 0.],
                 nodes_truenodeids=[0] if constant else [1, 0, 0],
                 nodes_falsenodeids=[0] if constant else [2, 0, 0],
                 nodes_missing_value_tracks_true=[1] if constant else [1, 0, 0],
                 class_treeids=[0] if constant else [0, 0],
                 class_nodeids=[0] if constant else [1, 2],
                 class_ids=[0] if constant else [0, 0],
                 class_weights=[.7] if constant else [-2., 2.])
    nodes = [helper.make_node('Identity', ['input'], ['transformed'])] if input_identity else []
    nodes.append(helper.make_node('TreeEnsembleClassifier',
        ['transformed' if input_identity else 'input'], ['labels','probabilities'], domain='ai.onnx.ml', **attrs))
    outputs = [helper.make_tensor_value_info('labels', TensorProto.INT64, [None]),
               helper.make_tensor_value_info('probabilities', TensorProto.FLOAT, [None,2])]
    if echo:
        outputs.append(helper.make_tensor_value_info('input', TensorProto.FLOAT, [None,width]))
    graph = helper.make_graph(nodes, 'test', [helper.make_tensor_value_info('input', TensorProto.FLOAT, [None,width])], outputs)
    proto = helper.make_model(graph, opset_imports=[helper.make_opsetid('',15), helper.make_opsetid('ai.onnx.ml',3)], ir_version=8)
    onnx.checker.check_model(proto)
    onnx.save(proto, path)


@pytest.mark.parametrize('storage', ['dense', 'csr', 'csc', 'noncontiguous'])
def test_projection_preserves_boundaries_missing_and_original_width(tmp_path, monkeypatch, storage):
    monkeypatch.setenv('COLLIMATOR_ONNX_THREADS','1')
    path=tmp_path/'model.onnx';tree(path)
    before=path.read_bytes()
    x=np.zeros((9,32), dtype=np.float32)
    x[:,9]=[0, .5, np.nextafter(np.float32(.5),np.float32(-np.inf)),
             np.nextafter(np.float32(.5),np.float32(np.inf)),np.nan,np.inf,-np.inf,-1,2]
    if storage=='csr':x=sparse.csr_matrix(x)
    if storage=='csc':x=sparse.csc_matrix(x)
    if storage=='noncontiguous':x=np.repeat(x,2,axis=1)[:,::2]
    monkeypatch.setenv('COLLIMATOR_ONNX_PROJECT_INPUT','0')
    expected=model.load_model(path).predict_proba(x)
    monkeypatch.setenv('COLLIMATOR_ONNX_PROJECT_INPUT','1')
    projected=model.load_model(path)
    assert projected._input_columns.tolist()==[9]
    np.testing.assert_array_equal(projected.predict_proba(x),expected)
    assert projected.predict_proba(x[:0]).shape==(0,2)
    with pytest.raises(ValueError,match='original ONNX features'):
        projected.predict_proba(np.zeros((1,1),dtype=np.float32))
    assert path.read_bytes()==before


def test_ensemble_projects_union_once_before_bounded_densification(tmp_path, monkeypatch):
    monkeypatch.setenv('COLLIMATOR_ONNX_THREADS','1')
    (tmp_path/'models').mkdir()
    for seed,column in [(42,2),(43,29)]:tree(tmp_path/'models'/f'seed_{seed}.onnx',column)
    x=sparse.csr_matrix(np.random.default_rng(4).normal(size=(19,32)).astype(np.float32))
    monkeypatch.setenv('COLLIMATOR_ONNX_PROJECT_INPUT','0')
    expected=bundle.Ensemble.load_bundle(tmp_path).predict_proba(x)
    monkeypatch.setenv('COLLIMATOR_ONNX_PROJECT_INPUT','1')
    ensemble=bundle.Ensemble.load_bundle(tmp_path)
    assert ensemble.primary._input_columns.tolist()==[2,29]
    monkeypatch.setattr(model.OnnxModel,'_DENSE_BYTES',32)
    shapes=[];original=sparse.csr_matrix.toarray
    def tracked(matrix,*args,**kwargs):
        shapes.append(matrix.shape)
        return original(matrix,*args,**kwargs)
    monkeypatch.setattr(sparse.csr_matrix,'toarray',tracked)
    np.testing.assert_array_equal(ensemble.predict_proba(x),expected)
    # Keep the original-width batch boundaries, including short tails, to
    # preserve ORT's floating reduction order; densify only the used columns.
    assert shapes==[(1,2)]*19
    # Independently loaded members may have different projections.
    separate=bundle.Ensemble([model.load_model(p) for p in bundle.model_files(tmp_path)])
    np.testing.assert_array_equal(separate.predict_proba(x),expected)


@pytest.mark.parametrize('options', [{'constant':True},{'input_identity':True},{'echo':True},{'width':1,'column':0}])
def test_constant_and_unsupported_layouts_preserve_results(tmp_path, monkeypatch, options):
    monkeypatch.setenv('COLLIMATOR_ONNX_THREADS','1')
    path=tmp_path/'model.onnx';tree(path,**options)
    width=options.get('width',32)
    x=np.ones((5,width),dtype=np.float32)
    monkeypatch.setenv('COLLIMATOR_ONNX_PROJECT_INPUT','0')
    expected=model.load_model(path).predict_proba(x)
    monkeypatch.setenv('COLLIMATOR_ONNX_PROJECT_INPUT','1')
    actual=model.load_model(path)
    np.testing.assert_array_equal(actual.predict_proba(x),expected)
    assert (actual._input_columns is not None)==options.get('constant',False)


def test_unsupported_ensemble_member_keeps_full_shared_layout(tmp_path, monkeypatch):
    monkeypatch.setenv('COLLIMATOR_ONNX_THREADS','1')
    (tmp_path/'models').mkdir()
    tree(tmp_path/'models/seed_42.onnx',column=2)
    tree(tmp_path/'models/seed_43.onnx',column=29,input_identity=True)
    x=np.random.default_rng(7).normal(size=(12,32)).astype(np.float32)
    monkeypatch.setenv('COLLIMATOR_ONNX_PROJECT_INPUT','0')
    expected=bundle.Ensemble.load_bundle(tmp_path).predict_proba(x)
    monkeypatch.setenv('COLLIMATOR_ONNX_PROJECT_INPUT','1')
    actual=bundle.Ensemble.load_bundle(tmp_path)
    assert all(m._input_columns is None for m in actual._members)
    np.testing.assert_array_equal(actual.predict_proba(x),expected)
