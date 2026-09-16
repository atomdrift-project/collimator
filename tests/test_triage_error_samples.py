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


def _empty_report(tmp_path: Path) -> Path:
    report = tmp_path / "false_positives.json"
    report.write_text(json.dumps({"false_positives": []}))
    return report


def test_copy_report_refuses_relative_output_directory(tmp_path: Path) -> None:
    samples = tmp_path / "samples"
    samples.mkdir()

    with pytest.raises(ValueError, match="refusing to clear relative"):
        copy_report(
            report_path=_empty_report(tmp_path),
            output_dir=Path("relative-triage-dir"),
            samples_dir=samples,
            kind="false-positives",
            top=10,
        )


def test_copy_report_refuses_directory_with_foreign_contents(
    tmp_path: Path, monkeypatch
) -> None:
    """A mistyped --output-dir that lands on real data is not wiped."""
    monkeypatch.setattr(tes, "_TEMP_ROOTS", ())  # pytest's tmp_path is itself temp
    samples = tmp_path / "samples"
    samples.mkdir()
    output = tmp_path / "not-triage"
    output.mkdir()
    (output / "important.txt").write_text("keep me")

    with pytest.raises(ValueError, match="not a triage output directory"):
        copy_report(
            report_path=_empty_report(tmp_path),
            output_dir=output,
            samples_dir=samples,
            kind="false-positives",
            top=10,
        )
    assert (output / "important.txt").read_text() == "keep me"


def test_copy_report_accepts_any_absolute_dir_it_owns(
    tmp_path: Path, monkeypatch
) -> None:
    """Non-temp output dirs work: created on first use, re-cleared thereafter.

    TRIAGE_DIR is an operator knob (`make triage TRIAGE_DIR=/data/triage2`), so
    the guard has to key on whether the directory is triage's, not on where it
    sits.
    """
    monkeypatch.setattr(tes, "_TEMP_ROOTS", ())  # prove it's the marker, not /tmp
    samples = tmp_path / "samples"
    samples.mkdir()
    output = tmp_path / "data" / "triage2" / "mislabeled-good"

    for _ in range(2):
        copy_report(
            report_path=_empty_report(tmp_path),
            output_dir=output,
            samples_dir=samples,
            kind="false-positives",
            top=10,
        )
    assert (output / tes._MARKER).exists()

    # Second run clears what the first left behind.
    (output / "stale.bin").write_bytes(b"old")
    copy_report(
        report_path=_empty_report(tmp_path),
        output_dir=output,
        samples_dir=samples,
        kind="false-positives",
        top=10,
    )
    assert not (output / "stale.bin").exists()


def test_relocated_rows_are_skipped_not_fetched(tmp_path: Path, monkeypatch) -> None:
    """A sample the operator already sorted elsewhere is reported, not downloaded.

    The score table is a snapshot; by the next triage pass some of its rows have
    been moved good <-> bad or out to purgatory. Those skips must not consume a
    quota slot either, so the over-fetch tail still fills the bucket.
    """
    samples = tmp_path / "samples"
    output = tmp_path / "mislabeled-good"
    samples.mkdir()
    report = tmp_path / "false_positives.json"
    report.write_text(
        json.dumps(
            {
                "false_positives": [
                    # Moved into bad/ after the score table was built.
                    {"path": "moved.exe", "sha256": "S1", "parent": "",
                     "label": "good", "current_label": "bad", "hopper_skip": ""},
                    # Greyware ruling: now in purgatory/.
                    {"path": "grey.exe", "sha256": "S2", "parent": "",
                     "label": "good", "current_label": "purgatory", "hopper_skip": ""},
                    # Deleted from the DB outright.
                    {"path": "gone.exe", "sha256": "S3", "parent": "",
                     "label": "good", "current_label": "", "hopper_skip": ""},
                    # Still sitting in good/ — the only one worth a download.
                    {"path": "still.exe", "sha256": "S4", "parent": "",
                     "label": "good", "current_label": "good", "hopper_skip": ""},
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
        top=1,  # the three skips must not eat the single slot
        hopper_url="http://hopper",
        error_report=tmp_path / "errors.jsonl",
    )

    assert calls == ["S4"]
    assert summary["copied"] == 1
    assert (output / "S4__still.exe").exists()

    records = [
        json.loads(line)
        for line in (tmp_path / "errors.jsonl").read_text().splitlines()
    ]
    assert [(r["path"], r["status"], r["detail"]) for r in records] == [
        ("moved.exe", "relocated", "already relocated to bad"),
        ("grey.exe", "relocated", "already relocated to purgatory"),
        ("gone.exe", "relocated", "gone from hopper DB"),
    ]


def test_report_without_current_label_still_fetches(tmp_path: Path, monkeypatch) -> None:
    """Reports predating the pool check are unchanged: every row is fetched."""
    samples = tmp_path / "samples"
    output = tmp_path / "mislabeled-good"
    samples.mkdir()
    report = tmp_path / "false_positives.json"
    report.write_text(
        json.dumps({"false_positives": [{"path": "a.exe", "sha256": "S1", "parent": ""}]})
    )

    calls: list[str] = []
    monkeypatch.setattr(tes, "_fetch_from_hopper", _fake_fetcher(calls))

    summary = copy_report(
        report_path=report,
        output_dir=output,
        samples_dir=samples,
        kind="false-positives",
        top=5,
        hopper_url="http://hopper",
    )
    assert calls == ["S1"]
    assert summary["copied"] == 1
