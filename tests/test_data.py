"""Tests for SQLite data loading."""

import json
import sqlite3
import tempfile
from pathlib import Path

from collimator.data import ALL_TERMINAL, BENIGN_STATUSES, MALWARE_STATUSES, load_samples


def _create_test_db(samples: list[tuple[str, str, str, str | None]]) -> Path:
    """Create a temporary SQLite DB with sample rows.

    Each tuple: (sha256, path, status, cleave_json)
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sha256 TEXT UNIQUE NOT NULL,
            path TEXT NOT NULL,
            status TEXT NOT NULL,
            updated_at INTEGER NOT NULL DEFAULT 0,
            cleave_json TEXT,
            risk TEXT,
            finding_count INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 0
        )
    """)
    for sha, path, status, cj in samples:
        conn.execute(
            "INSERT INTO samples (sha256, path, status, cleave_json) VALUES (?, ?, ?, ?)",
            (sha, path, status, cj),
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


def test_load_terminal_statuses() -> None:
    db = _create_test_db([
        ("aaa", "/tmp/a", "bad", _minimal_report()),
        ("bbb", "/tmp/b", "good", _minimal_report()),
        ("ccc", "/tmp/c", "bad-review", _minimal_report()),
        ("ddd", "/tmp/d", "good-review", _minimal_report()),
    ])
    samples = load_samples(db)
    assert len(samples) == 2
    labels = {s.sha256: s.label for s in samples}
    assert labels["aaa"] == 1  # malware
    assert labels["bbb"] == 0  # benign


def test_load_reclassified_statuses() -> None:
    """bad-benign -> benign, good-malicious -> malware."""
    db = _create_test_db([
        ("aaa", "/tmp/a", "bad-benign", _minimal_report()),
        ("bbb", "/tmp/b", "good-malicious", _minimal_report()),
    ])
    samples = load_samples(db)
    assert len(samples) == 2
    labels = {s.sha256: s.label for s in samples}
    assert labels["aaa"] == 0  # reclassified as benign
    assert labels["bbb"] == 1  # reclassified as malware


def test_skip_intermediate_statuses() -> None:
    db = _create_test_db([
        ("aaa", "/tmp/a", "bad", _minimal_report()),
        ("bbb", "/tmp/b", "bad-review", _minimal_report()),
        ("ccc", "/tmp/c", "bad-reversed", _minimal_report()),
        ("ddd", "/tmp/d", "bad-gapped", _minimal_report()),
        ("eee", "/tmp/e", "good-review", _minimal_report()),
        ("fff", "/tmp/f", "good-analyzed", _minimal_report()),
    ])
    samples = load_samples(db)
    assert len(samples) == 1
    assert samples[0].sha256 == "aaa"


def test_skip_null_json() -> None:
    db = _create_test_db([
        ("aaa", "/tmp/a", "bad", _minimal_report()),
        ("bbb", "/tmp/b", "bad", ""),
        ("ccc", "/tmp/c", "good", None),
    ])
    samples = load_samples(db)
    assert len(samples) == 1
    assert samples[0].sha256 == "aaa"


def test_skip_invalid_json() -> None:
    db = _create_test_db([
        ("aaa", "/tmp/a", "bad", _minimal_report()),
        ("bbb", "/tmp/b", "bad", "not valid json{{{"),
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


def test_status_constants() -> None:
    assert "bad" in MALWARE_STATUSES
    assert "good-malicious" in MALWARE_STATUSES
    assert "good" in BENIGN_STATUSES
    assert "bad-benign" in BENIGN_STATUSES
    assert ALL_TERMINAL == MALWARE_STATUSES | BENIGN_STATUSES
