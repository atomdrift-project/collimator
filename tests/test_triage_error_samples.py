"""Tests for copying false-positive samples into triage directories."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from triage_error_samples import copy_report  # noqa: E402


def test_copy_report_clears_and_dedupes_outer_paths(tmp_path: Path) -> None:
    samples = tmp_path / "samples"
    output = tmp_path / "false-positives"
    samples.mkdir()
    output.mkdir()
    (output / "stale.bin").write_bytes(b"old")
    (samples / "sample.zip").write_bytes(b"zip")
    (samples / "other.exe").write_bytes(b"exe")
    report = tmp_path / "false_positives.json"
    report.write_text(
        json.dumps(
            {
                "false_positives": [
                    {"path": "sample.zip!!inner/a"},
                    {"path": "sample.zip!!inner/b"},
                    {"path": "other.exe"},
                ],
            }
        )
    )

    summary = copy_report(
        report_path=report,
        output_dir=output,
        samples_dir=samples,
        kind="false-positives",
        top=10,
    )

    assert summary["copied"] == 2
    assert not (output / "stale.bin").exists()
    assert (output / "sample.zip").read_bytes() == b"zip"
    assert (output / "other.exe").read_bytes() == b"exe"


def test_copy_report_refuses_to_clear_non_tmp_directory(tmp_path: Path) -> None:
    samples = tmp_path / "samples"
    samples.mkdir()
    report = tmp_path / "false_positives.json"
    report.write_text(json.dumps({"false_positives": []}))

    with pytest.raises(ValueError, match="refusing to clear non-/tmp"):
        copy_report(
            report_path=report,
            output_dir=Path("relative-triage-dir"),
            samples_dir=samples,
            kind="false-positives",
            top=10,
        )
