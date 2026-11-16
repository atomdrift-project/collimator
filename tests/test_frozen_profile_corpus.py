"""Frozen iteration inputs retain selection, reports, and partition identity."""

import hashlib
from pathlib import Path
import sqlite3
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from freeze_profile_corpus import freeze
from convert_bundle_to_onnx import _sample_rows
from collimator import data
from collimator.demo import add_sample, create_schema


def _corpus(db, percent="1", max_id=2800):
    """Each sampled usable row with its report, as training reads it."""
    rows = list(data.stream_corpus(db, max_id=max_id, percent=percent, with_path=True))
    reports = data.fetch_cleave_results(db, [row.row_id for row in rows])
    return [(row, reports[row.row_id]["cleave_result"]) for row in rows]


def test_freeze_is_repeatable_and_preserves_inputs(tmp_path):
    source = tmp_path / "source.sqlite"
    with sqlite3.connect(source) as conn:
        create_schema(conn)
        for i in range(3000):
            sha = hashlib.sha256(str(i).encode()).hexdigest()
            add_sample(conn, sample_id=i + 1, sha256=sha, path=f"/{i}",
                       label="bad" if i % 2 else "good", file_type="pe",
                       report={"traits": [{"id": "x", "crit": 5}], "risk": 5, "mol": "x"},
                       label_source="conflict" if i % 11 == 0 else None)
    manifest = freeze(source, tmp_path / "a", percent="1", pin=2800, batch_size=7)
    assert 10 < manifest["rows"] < 60
    assert sum(manifest["partitions"].values()) == manifest["rows"]
    expected = _corpus(source)
    assert len(expected) == manifest["rows"]
    assert _corpus(tmp_path / "a/corpus.sqlite") == expected
    # Sampling an already frozen cohort is idempotent; live writes cannot leak in.
    with sqlite3.connect(source) as conn:
        conn.execute("UPDATE samples SET label='unknown'")
        conn.execute("UPDATE verdicts SET detail=NULL, digest=NULL")
    repeated = freeze(tmp_path / "a/corpus.sqlite", tmp_path / "b", percent="1", pin=2800)
    assert repeated["rows"] == manifest["rows"]
    assert _corpus(tmp_path / "b/corpus.sqlite") == expected
    with (tmp_path / "a/corpus.sqlite").open("rb") as handle:
        assert hashlib.file_digest(handle, "sha256").hexdigest() == manifest["sha256"]
    with pytest.raises(FileExistsError):
        freeze(source, tmp_path / "a")
    wanted = [(row.row_id, row.label) for row, _report in expected
              if data.partition_of(row.sha256) == "test"][:3]
    assert wanted
    assert _sample_rows(str(tmp_path / "a/corpus.sqlite"), ["pe"], 3) == wanted
    assert _sample_rows(str(tmp_path / "a/corpus.sqlite"), ["elf"], 3) == []


def test_empty_capture_is_not_published(tmp_path):
    source = tmp_path / "empty.sqlite"
    with sqlite3.connect(source) as conn:
        create_schema(conn)
    with pytest.raises(ValueError, match="empty"):
        freeze(source, tmp_path / "capture")
    assert not (tmp_path / "capture/corpus.sqlite").exists()
    assert not (tmp_path / "capture/manifest.json").exists()
