"""Frozen iteration inputs retain selection, reports, and partition identity."""

import hashlib
import json
from pathlib import Path
import sqlite3
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from freeze_profile_corpus import COLUMNS, freeze
from convert_bundle_to_onnx import _sample_rows
from collimator import data


def test_freeze_is_repeatable_and_preserves_inputs(tmp_path):
    source = tmp_path / "source.sqlite"
    with sqlite3.connect(source) as conn:
        conn.execute("CREATE TABLE samples (" + ",".join(COLUMNS) + ")")
        for i in range(3000):
            sha = hashlib.sha256(str(i).encode()).hexdigest()
            conn.execute("INSERT INTO samples VALUES (" + ",".join("?" for _ in COLUMNS) + ")",
                         (i+1, sha, f"/{i}", "bad" if i % 2 else "good", sha if i % 3 else None,
                          json.dumps({"files": [{"type": "pe"}]}), "x", "[]", 5, 1, "pe",
                          "skip" if i % 11 == 0 else ""))
    manifest = freeze(source, tmp_path / "a", percent="1", pin=2800, batch_size=7)
    assert 10 < manifest["rows"] < 60
    assert sum(manifest["partitions"].values()) == manifest["rows"]
    with data._connect(source) as conn:
        expected = list(conn.execute("SELECT * FROM samples WHERE skip='' AND id<=2800 AND "
                                     + data.sample_predicate("1") + " ORDER BY id"))
    with data._connect(tmp_path / "a/corpus.sqlite") as conn:
        assert list(conn.execute("SELECT * FROM samples ORDER BY id")) == expected
        assert conn.execute("SELECT count(*) FROM samples WHERE " + data.sample_predicate("1")).fetchone()[0] == len(expected)
    # Sampling an already frozen cohort is idempotent; live writes cannot leak in.
    with sqlite3.connect(source) as conn:
        conn.execute("UPDATE samples SET label='unknown', cleave_result=NULL")
    repeated = freeze(tmp_path / "a/corpus.sqlite", tmp_path / "b", percent="1", pin=2800)
    assert repeated["rows"] == manifest["rows"]
    with data._connect(tmp_path / "b/corpus.sqlite") as conn:
        assert list(conn.execute("SELECT * FROM samples ORDER BY id")) == expected
    with (tmp_path / "a/corpus.sqlite").open("rb") as handle:
        assert hashlib.file_digest(handle, "sha256").hexdigest() == manifest["sha256"]
    with pytest.raises(FileExistsError):
        freeze(source, tmp_path / "a")
    wanted = [(r[0], int(r[3] == "bad")) for r in expected if r[4] and int(r[4][-2:], 16) < 32][:3]
    assert _sample_rows(str(tmp_path / "a/corpus.sqlite"), ["pe"], 3) == wanted
    assert _sample_rows(str(tmp_path / "a/corpus.sqlite"), ["elf"], 3) == []


def test_empty_capture_is_not_published(tmp_path):
    source = tmp_path / "empty.sqlite"
    with sqlite3.connect(source) as conn:
        conn.execute("CREATE TABLE samples (" + ",".join(COLUMNS) + ")")
    with pytest.raises(ValueError, match="empty"):
        freeze(source, tmp_path / "capture")
    assert not (tmp_path / "capture/corpus.sqlite").exists()
    assert not (tmp_path / "capture/manifest.json").exists()
