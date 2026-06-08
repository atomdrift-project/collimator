"""Tests for Azoth runtime bundle staging."""

from __future__ import annotations

import json

from collimator.features import MODEL_ABI_VERSION
from scripts.stage_azoth_runtime_bundle import _stage_feature_spec


def test_stage_feature_spec_stamps_current_abi_and_repairs_offset_vocabs(tmp_path) -> None:
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

    staged = json.loads(dst.read_text())
    assert staged["version"] == MODEL_ABI_VERSION
    assert staged["abi_version"] == MODEL_ABI_VERSION
    assert staged["feature_names"] == [
        "maxcrit:objectives/evasion",
        "unsigned_bigram:a>b",
        "trigram:a>b>c",
        "agg:max_crit",
    ]
    assert staged["total_features"] == 4
    assert staged["presence_vocab"] == ["objectives/evasion"]
    assert staged["bigram_vocab"] == ["a>b"]
    assert staged["trigram_vocab"] == ["a>b>c"]
