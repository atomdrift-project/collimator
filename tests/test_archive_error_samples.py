"""Tests for packaging false-positive/false-negative sample archives."""

from __future__ import annotations

import json
import tarfile

from scripts.archive_error_samples import archive_report


def test_archive_report_deduplicates_embedded_members_and_preserves_hierarchy(tmp_path) -> None:
    samples_dir = tmp_path / "samples"
    outer = samples_dir / "bad" / "pkg" / "sample.zip"
    outer.parent.mkdir(parents=True)
    outer.write_bytes(b"zip bytes")
    other = samples_dir / "good" / "pkg" / "file.py"
    other.parent.mkdir(parents=True)
    other.write_text("print('ok')\n")

    report = tmp_path / "false_positives.json"
    report.write_text(json.dumps({
        "false_positives": [
            {"path": "bad/pkg/sample.zip!!inner/a.py", "probability": 0.99},
            {"path": "bad/pkg/sample.zip!!inner/b.py", "probability": 0.98},
            {"path": "good/pkg/file.py", "probability": 0.97},
        ],
    }))
    output = tmp_path / "fp.tgz"

    summary = archive_report(
        report_path=report,
        output_path=output,
        samples_dir=samples_dir,
        kind="false-positives",
        top=10,
    )

    assert summary["archived"] == 2
    with tarfile.open(output, "r:gz") as tar:
        assert sorted(tar.getnames()) == [
            "bad/pkg/sample.zip",
            "good/pkg/file.py",
        ]


def test_archive_report_reads_near_false_positive_rows(tmp_path) -> None:
    samples_dir = tmp_path / "samples"
    sample = samples_dir / "near" / "fp.py"
    sample.parent.mkdir(parents=True)
    sample.write_text("print('near')\n")

    report = tmp_path / "near_false_positives.json"
    report.write_text(json.dumps({
        "near_false_positives": [
            {"path": "near/fp.py", "probability": 0.85},
        ],
    }))
    output = tmp_path / "near-fp.tgz"

    summary = archive_report(
        report_path=report,
        output_path=output,
        samples_dir=samples_dir,
        kind="near-false-positives",
        top=10,
    )

    assert summary["archived"] == 1
    with tarfile.open(output, "r:gz") as tar:
        assert tar.getnames() == ["near/fp.py"]


def test_archive_report_reads_near_false_negative_rows(tmp_path) -> None:
    samples_dir = tmp_path / "samples"
    sample = samples_dir / "near" / "fn.py"
    sample.parent.mkdir(parents=True)
    sample.write_text("print('near')\n")

    report = tmp_path / "near_false_negatives.json"
    report.write_text(json.dumps({
        "near_false_negatives": [
            {"path": "near/fn.py", "probability": 0.85},
        ],
    }))
    output = tmp_path / "near-fn.tgz"

    summary = archive_report(
        report_path=report,
        output_path=output,
        samples_dir=samples_dir,
        kind="near-false-negatives",
        top=10,
    )

    assert summary["archived"] == 1
    with tarfile.open(output, "r:gz") as tar:
        assert tar.getnames() == ["near/fn.py"]
