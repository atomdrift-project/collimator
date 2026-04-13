"""Tests for data loading from hopper databases."""

import json
import sqlite3
import tempfile
from pathlib import Path

from collimator.data import load_samples


def _create_test_db(samples: list[tuple[str, str, str | None]]) -> Path:
    """Create a temporary hopper-schema SQLite DB.

    Each tuple: (sha256, label, cleave_result)
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sha256 TEXT UNIQUE NOT NULL,
            source TEXT NOT NULL DEFAULT '',
            feed TEXT NOT NULL DEFAULT '',
            ecosystem TEXT NOT NULL DEFAULT '',
            filename TEXT NOT NULL DEFAULT '',
            file_type TEXT NOT NULL DEFAULT '',
            size_bytes INTEGER NOT NULL DEFAULT 0,
            label TEXT NOT NULL DEFAULT 'unknown',
            label_source TEXT NOT NULL DEFAULT '',
            cleave_result TEXT,
            risk TEXT NOT NULL DEFAULT '',
            finding_count INTEGER NOT NULL DEFAULT 0,
            path TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT '',
            note TEXT NOT NULL DEFAULT '',
            canonical_sha256 TEXT NOT NULL DEFAULT '',
            parent TEXT NOT NULL DEFAULT '',
            skip TEXT NOT NULL DEFAULT '',
            formula TEXT NOT NULL DEFAULT '',
            elements TEXT NOT NULL DEFAULT '',
            score INTEGER NOT NULL DEFAULT 10,
            mtime DATETIME,
            created_at DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            updated_at DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            analyzed_at DATETIME
        )
    """)
    for sha, label, cr in samples:
        conn.execute(
            "INSERT INTO samples (sha256, label, canonical_sha256, cleave_result)"
            " VALUES (?, ?, ?, ?)",
            (sha, label, sha, cr),
        )
    conn.commit()
    conn.close()
    return db_path


def _minimal_report() -> str:
    return json.dumps({
        "version": "3",
        "files": [{
            "id": 0,
            "path": "/tmp/x",
            "depth": 0,
            "file_type": "elf",
            "sha256": "abc",
            "size": 1024,
            "findings": [],
            "structure": [],
            "strings": [],
        }],
        "summary": {"files_analyzed": 1, "duration_ms": 1, "tools": []},
    })


def test_load_labeled_samples() -> None:
    db = _create_test_db([
        ("aaa", "bad", _minimal_report()),
        ("bbb", "good", _minimal_report()),
        ("ccc", "unknown", _minimal_report()),  # excluded — not bad or good
    ])
    samples = load_samples(db)
    assert len(samples) == 2
    labels = {s.sha256: s.label for s in samples}
    assert labels["aaa"] == 1  # malware
    assert labels["bbb"] == 0  # benign


def test_skip_null_json() -> None:
    db = _create_test_db([
        ("aaa", "bad", _minimal_report()),
        ("bbb", "bad", ""),
        ("ccc", "good", None),
    ])
    samples = load_samples(db)
    assert len(samples) == 1
    assert samples[0].sha256 == "aaa"


def test_skip_invalid_json() -> None:
    db = _create_test_db([
        ("aaa", "bad", _minimal_report()),
        ("bbb", "bad", "not valid json{{{"),
    ])
    samples = load_samples(db)
    assert len(samples) == 1


def test_empty_database() -> None:
    db = _create_test_db([])
    samples = load_samples(db)
    assert len(samples) == 0


def test_file_not_found() -> None:
    import pytest
    with pytest.raises(FileNotFoundError):
        load_samples(Path("/nonexistent/database.db"))
