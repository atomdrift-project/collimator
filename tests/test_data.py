"""Tests for data loading from hopper databases."""

import json
import sqlite3
import tempfile
from pathlib import Path

from collimator.data import (
    count_labeled_by_partition_full,
    labeled_corpus_metadata_full,
    load_samples,
    normalize_archive_filetype,
    stream_labeled_metadata_full_with_size,
    stream_labeled_samples_full,
)


def test_normalize_archive_filetype_strips_pure_compression():
    """Mirror of litmus' Rust `normalize_archive_filetype` test. The two
    must stay byte-equivalent — training emits labels with this rule and
    litmus routes scan-time files with the Rust mirror.
    """
    # Compound archive labels collapse onto their container.
    assert normalize_archive_filetype("tar.gz") == "tar"
    assert normalize_archive_filetype("tar.bz2") == "tar"
    assert normalize_archive_filetype("tar.xz") == "tar"
    assert normalize_archive_filetype("tar.zst") == "tar"
    assert normalize_archive_filetype("tar.Z") == "tar"
    assert normalize_archive_filetype("TAR.GZ") == "tar"
    # Repeated stripping for stacked suffixes.
    assert normalize_archive_filetype("tar.bz2.xz") == "tar"
    # Bare compression labels keep their identity — RAW_COMPRESSED_FILETYPES
    # in azoth_specialist_suite gates them at route discovery.
    assert normalize_archive_filetype("gz") == "gz"
    assert normalize_archive_filetype("bz2") == "bz2"
    # Containers without a compression suffix pass through.
    assert normalize_archive_filetype("zip") == "zip"
    assert normalize_archive_filetype("pe") == "pe"
    # Empty / None / whitespace.
    assert normalize_archive_filetype("") == ""
    assert normalize_archive_filetype(None) == ""
    assert normalize_archive_filetype("  tar.gz  ") == "tar"


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


def test_stream_labeled_metadata_full_with_size_includes_json_length() -> None:
    low_report = _minimal_report()
    high_report = json.dumps({"fs": [{"id": 0, "path": "/tmp/y", "dp": 0, "ts": ["x" * 100]}]})
    db = _create_test_db([
        {"sha256": "aaa", "label": "good", "cleave_result": low_report, "path": "/repo/harvest/low.py", "score": 0},
        {"sha256": "bbb", "label": "bad", "cleave_result": high_report, "path": "/repo/harvest/high.py", "score": 42},
        {"sha256": "ccc", "label": "good", "cleave_result": _minimal_report(), "path": "/repo/other/x.py", "score": 7, "skip": "y"},
    ])

    rows = list(stream_labeled_metadata_full_with_size(db, path_substr="harvest"))

    assert [row[:5] for row in rows] == [
        (1, "aaa", "/repo/harvest/low.py", 0, 0),
        (2, "bbb", "/repo/harvest/high.py", 42, 1),
    ]
    assert rows[0][5] == len(low_report)
    assert rows[1][5] == len(high_report)
    # canonical_sha256 is the trailing element (defaults to sha256 in the demo
    # rows since we didn't populate canonical separately).
    assert rows[0][6] == "aaa"
    assert rows[1][6] == "bbb"


def test_count_labeled_by_partition_full_includes_low_score_rows() -> None:
    # SHA256 last bytes: 00=test, 30=dev, 50=bad train, 60=unknown filtered, 70=skip filtered.
    db = _create_test_db([
        {"sha256": "00" * 32, "label": "good", "cleave_result": _minimal_report(), "score": 0},
        {"sha256": "30" * 32, "label": "good", "cleave_result": _minimal_report(), "score": 10},
        {"sha256": "50" * 32, "label": "bad", "cleave_result": _minimal_report(), "score": 1},
        {"sha256": "60" * 32, "label": "unknown", "cleave_result": _minimal_report(), "score": 10},
        {
            "sha256": "70" * 32,
            "label": "good",
            "cleave_result": _minimal_report(),
            "score": 10,
            "skip": "y",
        },
    ])

    counts = count_labeled_by_partition_full(db)

    assert counts["all"]["good"] == 2
    assert counts["all"]["bad"] == 1
    assert counts["all"]["total"] == 3
    # 00 -> test partition (byte=0 < 32)
    assert counts["test"]["good"] == 1
    # 30 -> dev partition (32 <= byte=48 < 64)
    assert counts["dev"]["good"] == 1
    # 50 -> train partition (byte=80 >= 64)
    assert counts["train"]["bad"] == 1


def test_labeled_corpus_metadata_full_matches_threshold_corpus() -> None:
    db = _create_test_db([
        {"sha256": "aaa", "label": "good", "cleave_result": _minimal_report(), "score": 0},
        {"sha256": "bbb", "label": "bad", "cleave_result": _minimal_report(), "score": 1},
        {"sha256": "ccc", "label": "unknown", "cleave_result": _minimal_report(), "score": 10},
        {"sha256": "ddd", "label": "good", "cleave_result": None, "score": 10},
        {"sha256": "eee", "label": "good", "cleave_result": _minimal_report(), "score": 10, "skip": "y"},
    ])

    metadata = labeled_corpus_metadata_full(db)

    assert metadata["samples"] == 2
    assert metadata["malware"] == 1
    assert metadata["benign"] == 1
    assert metadata["max_row_id"] == 2


def test_retry_pg_connect_succeeds_after_transient_failure(monkeypatch) -> None:
    """A transient OperationalError on the first attempt must be retried, and
    the eventual successful connect must be returned without raising."""
    import sys as _sys  # noqa: PLC0415
    from collimator import data as data_mod  # noqa: PLC0415

    # Provide a minimal stand-in for psycopg so the test doesn't need a real DB.
    class FakeOpError(Exception):
        pass

    class FakePsycopg:
        OperationalError = FakeOpError

        def __init__(self):
            self.attempts = 0

        def connect(self, *_args, **_kwargs):
            self.attempts += 1
            if self.attempts == 1:
                raise FakeOpError("server briefly unreachable")
            return object()

    fake = FakePsycopg()
    monkeypatch.setitem(_sys.modules, "psycopg", fake)
    # Compress backoff so the test doesn't actually sleep.
    monkeypatch.setattr(data_mod, "_DB_CONNECT_BASE_DELAY_S", 0.001)
    monkeypatch.setattr(data_mod, "_DB_CONNECT_MAX_DELAY_S", 0.001)

    conn = data_mod._retry_pg_connect("postgres://x/y")
    assert conn is not None
    assert fake.attempts == 2, "first call must be retried after transient OperationalError"


def test_retry_pg_connect_gives_up_after_max_attempts(monkeypatch) -> None:
    """A persistent failure raises the last error after exhausting attempts —
    we don't want to silently hang on a permanently-down DB."""
    import sys as _sys  # noqa: PLC0415
    import pytest  # noqa: PLC0415
    from collimator import data as data_mod  # noqa: PLC0415

    class FakeOpError(Exception):
        pass

    class FakePsycopg:
        OperationalError = FakeOpError

        def __init__(self):
            self.attempts = 0

        def connect(self, *_args, **_kwargs):
            self.attempts += 1
            raise FakeOpError(f"down (attempt {self.attempts})")

    fake = FakePsycopg()
    monkeypatch.setitem(_sys.modules, "psycopg", fake)
    monkeypatch.setattr(data_mod, "_DB_CONNECT_BASE_DELAY_S", 0.001)
    monkeypatch.setattr(data_mod, "_DB_CONNECT_MAX_DELAY_S", 0.001)
    monkeypatch.setattr(data_mod, "_DB_CONNECT_MAX_ATTEMPTS", 3)

    with pytest.raises(FakeOpError, match="down"):
        data_mod._retry_pg_connect("postgres://x/y")
    assert fake.attempts == 3, "must give up after _DB_CONNECT_MAX_ATTEMPTS"
