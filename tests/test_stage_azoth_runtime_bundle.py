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
