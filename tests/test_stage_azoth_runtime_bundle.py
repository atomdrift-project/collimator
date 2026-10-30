"""Tests for Azoth runtime bundle staging."""

from __future__ import annotations

import json

from scripts.stage_azoth_runtime_bundle import _stage_feature_spec


def test_staging_preserves_the_calibrated_feature_spec_byte_for_byte(tmp_path) -> None:
    src = tmp_path / "src_feature_spec.json"
    dst = tmp_path / "staged" / "feature_spec.json"
    src.write_text(json.dumps({
        "version": 17,
        "abi_version": 17,
        "presence_vocab": [],
        "bigram_vocab": [],
        "trigram_vocab": [],
        "feature_names": [
            "maxcrit:objectives/evasion",
            "unsigned_bigram:a>b",
            "trigram:a>b>c",
            "agg:max_crit",
        ],
        "total_features": 4,
    }))

    _stage_feature_spec(src, dst)

    assert dst.read_bytes() == src.read_bytes()


def test_staging_keeps_current_and_effective_configuration_snapshots(tmp_path,monkeypatch):
    from scripts import stage_azoth_runtime_bundle as stage
    source=tmp_path/'source';source.mkdir();target=tmp_path/'target'
    (source/'model.onnx').write_bytes(b'model')
    for name in ['feature_spec.json','accepted_config.json','training_config.json']:
        (source/name).write_text(json.dumps({'source':name}))
    monkeypatch.setattr(stage.bundle,'model_files',lambda root:[root/'model.onnx'])
    assert stage._copy_route(source,target)
    for name in ['accepted_config.json','training_config.json']:
        assert (target/name).read_bytes()==(source/name).read_bytes()
