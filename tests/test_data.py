"""Tests for data loading from hopper databases."""

import json
import sqlite3
import tempfile
from pathlib import Path

from collimator.data import load_samples, stream_labeled_samples_full


def _create_test_db(samples: list[tuple[str, str, str | None] | dict[str, str | int | None]]) -> Path:
    """Create a temporary hopper-schema SQLite DB.

    Each tuple: (sha256, label, cleave_result)
    Or dict with optional path/score/skip overrides.
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
    for entry in samples:
        if isinstance(entry, dict):
            sha = str(entry["sha256"])
            label = str(entry["label"])
            cr = entry["cleave_result"]
            path = str(entry.get("path", ""))
            score = int(entry.get("score", 10))
            skip = str(entry.get("skip", ""))
        else:
            sha, label, cr = entry
            path = ""
            score = 10
            skip = ""
        conn.execute(
            "INSERT INTO samples (sha256, label, canonical_sha256, cleave_result, path, score, skip)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (sha, label, sha, cr, path, score, skip),
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


def test_stream_labeled_samples_full_includes_low_score_and_applies_filters() -> None:
    db = _create_test_db([
        {"sha256": "aaa", "label": "good", "cleave_result": _minimal_report(), "path": "/repo/harvest/low.py", "score": 0},
        {"sha256": "bbb", "label": "bad", "cleave_result": _minimal_report(), "path": "/repo/harvest/high.py", "score": 42},
        {"sha256": "ccc", "label": "good", "cleave_result": _minimal_report(), "path": "/repo/other/x.py", "score": 7, "skip": "y"},
    ])
    samples = list(stream_labeled_samples_full(db, path_substr="harvest"))
    assert [sample.sha256 for sample in samples] == ["aaa", "bbb"]
    assert [sample.score for sample in samples] == [0, 42]
