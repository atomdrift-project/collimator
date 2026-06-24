"""Tests for copying error-report samples into triage directories."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import triage_error_samples as tes  # noqa: E402
from triage_error_samples import copy_report  # noqa: E402


def _fake_fetcher(calls: list[str]):
    """Stand-in for ``_fetch_from_hopper`` that records the sha it was asked for
    and writes deterministic bytes to the destination."""

    def _fetch(sha256, destination, hopper_url, timeout=45.0, retry_delays=(3.0, 12.0)):
        calls.append(sha256)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"data-" + sha256.encode())
        return "ok", ""

    return _fetch


def test_members_fetch_whole_archive_deduped(tmp_path: Path, monkeypatch) -> None:
    """Members resolve to their parent archive, downloaded once for all siblings."""
    samples = tmp_path / "samples"
    output = tmp_path / "false-positives"
    samples.mkdir()
    output.mkdir()
    (output / "stale.bin").write_bytes(b"old")
    report = tmp_path / "false_positives.json"
    report.write_text(
        json.dumps(
            {
                "false_positives": [
                    {"path": "pkg.tgz!!a.js", "sha256": "m1", "parent": "AAA"},
                    {"path": "pkg.tgz!!b.js", "sha256": "m2", "parent": "AAA"},
                    {"path": "pkg.tgz!!c.js", "sha256": "m3", "parent": "AAA"},
                    {"path": "lone.exe", "sha256": "S1", "parent": ""},
                ],
            }
        )
    )

    calls: list[str] = []
    monkeypatch.setattr(tes, "_fetch_from_hopper", _fake_fetcher(calls))

    summary = copy_report(
        report_path=report,
        output_dir=output,
        samples_dir=samples,
        kind="false-positives",
        top=10,
        hopper_url="http://hopper",
    )

    # Archive fetched once (not per member); standalone fetched once.
    assert calls == ["AAA", "S1"]
    # Two distinct files land — the archive and the standalone; siblings reuse.
    assert summary["copied"] == 2
    assert summary["fetched_from_hopper"] == 2
    assert not (output / "stale.bin").exists()  # output dir is wiped first
    assert (output / "AAA__pkg.tgz").read_bytes() == b"data-AAA"
    assert (output / "S1__lone.exe").read_bytes() == b"data-S1"


def test_same_archive_across_filetypes_copied_not_refetched(
    tmp_path: Path, monkeypatch
) -> None:
    """One archive whose members fall in two filetype buckets downloads once and
    is copied locally into the second bucket."""
    samples = tmp_path / "samples"
    output = tmp_path / "false-positives"
    samples.mkdir()
    output.mkdir()
    report = tmp_path / "fp.json"
    report.write_text(
        json.dumps(
            {
                "false_positives": [
                    {"path": "pkg.tgz!!a.js", "sha256": "m1", "parent": "AAA",
                     "filetype": "javascript"},
                    {"path": "pkg.tgz!!b.json", "sha256": "m2", "parent": "AAA",
                     "filetype": "json"},
                ],
            }
        )
    )

    calls: list[str] = []
    monkeypatch.setattr(tes, "_fetch_from_hopper", _fake_fetcher(calls))

    summary = copy_report(
        report_path=report,
        output_dir=output,
        samples_dir=samples,
        kind="false-positives",
        top=10,
        hopper_url="http://hopper",
        group_by_filetype=True,
    )

    assert calls == ["AAA"]  # downloaded once, not per bucket
    assert summary["fetched_from_hopper"] == 1
    assert summary["copied"] == 2  # present in both buckets
    assert (output / "javascript" / "AAA__pkg.tgz").exists()
    assert (output / "json" / "AAA__pkg.tgz").exists()


def test_existing_file_on_disk_is_not_refetched(tmp_path: Path, monkeypatch) -> None:
    """A sample already present in the target dir is reused without a fetch."""
    samples = tmp_path / "samples"
    base = tmp_path / "out"
    samples.mkdir()
    base.mkdir()
    # Pre-place the sha-stamped file the copier would otherwise download.
    (base / "S1__lone.exe").write_bytes(b"already here")

    calls: list[str] = []
    monkeypatch.setattr(tes, "_fetch_from_hopper", _fake_fetcher(calls))

    landed: dict[str, Path] = {}
    copied: list[str] = []
    fetched: list[str] = []
    missing: list[str] = []
    n, _ = tes._copy_rows(
        [{"path": "lone.exe", "sha256": "S1", "parent": ""}],
        base_dir=base,
        samples_dir=samples,
        top=10,
        hopper_url="http://hopper",
        landed=landed,
        copied=copied,
        fetched=fetched,
        missing=missing,
    )

    assert calls == []  # nothing fetched
    assert n == 1
    assert copied == ["S1__lone.exe"]
    assert fetched == []
    assert (base / "S1__lone.exe").read_bytes() == b"already here"


def test_copy_report_refuses_to_clear_non_tmp_directory(tmp_path: Path) -> None:
    samples = tmp_path / "samples"
    samples.mkdir()
    report = tmp_path / "false_positives.json"
    report.write_text(json.dumps({"false_positives": []}))

    with pytest.raises(ValueError, match="refusing to clear non-temp"):
        copy_report(
            report_path=report,
            output_dir=Path("relative-triage-dir"),
            samples_dir=samples,
            kind="false-positives",
            top=10,
        )
