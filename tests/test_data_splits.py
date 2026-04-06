"""Tests for deterministic train/test splitting via canonical_sha256.

The split rule is simple and reproducible:

    is_test = int(canonical_sha256[-2:], 16) < TEST_BUCKET_MAX   (32/256 = 12.5%)

canonical_sha256 is the lexicographic minimum SHA256 across a sample and
all its embedded files (pre-computed by hopper).  This ensures archives
sharing an inner file always land in the same partition.
"""

from __future__ import annotations

import json
import sqlite3

from collimator.data import TEST_BUCKET_MAX, is_test_sample, stream_partitioned_metadata_grouped
from collimator.demo import create_demo_db


def _hopper_schema_sql() -> str:
    return """
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
            created_at DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            updated_at DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            analyzed_at DATETIME
        )
    """


def _make_report(outer_sha: str, embedded_shas: list[str]) -> str:
    files = [{
        "id": 0,
        "path": f"/tmp/{outer_sha}.zip",
        "depth": 0,
        "file_type": "zip",
        "sha256": outer_sha,
        "findings": [],
        "imports": [],
        "sections": [],
        "strings": [],
        "metrics": {},
    }]
    for i, sha in enumerate(embedded_shas, start=1):
        files.append({
            "id": i,
            "parent_id": 0,
            "path": f"member-{i}.py",
            "depth": 1,
            "file_type": "python",
            "sha256": sha,
            "findings": [],
            "imports": [],
            "sections": [],
            "strings": [],
            "metrics": {},
        })
    return json.dumps({
        "version": "3",
        "files": files,
        "summary": {"files_analyzed": len(files), "duration_ms": 1, "tools": ["test"]},
    })


def test_is_test_sample_deterministic() -> None:
    """Same SHA256 always gets the same assignment."""
    sha = "ab" * 32
    assert is_test_sample(sha) == is_test_sample(sha)


def test_is_test_sample_boundary() -> None:
    """Boundary check: last byte < TEST_BUCKET_MAX -> test."""
    # Last 2 hex chars = "00" -> int = 0 < 32 -> test
    assert is_test_sample("ff" * 31 + "00") is True
    # Last 2 hex chars = "1f" -> int = 31 < 32 -> test
    assert is_test_sample("ff" * 31 + "1f") is True
    # Last 2 hex chars = "20" -> int = 32, NOT < 32 -> train
    assert is_test_sample("ff" * 31 + "20") is False
    # Last 2 hex chars = "ff" -> int = 255 -> train
    assert is_test_sample("ff" * 32) is False


def test_test_bucket_approximately_12_percent() -> None:
    """~12.5% of SHA256 space falls in the test bucket."""
    assert TEST_BUCKET_MAX == 32
    assert TEST_BUCKET_MAX / 256 == 0.125


def test_canonical_sha256_determines_partition(tmp_path) -> None:
    """Samples sharing a canonical_sha256 must land in the same partition.

    Two archives with different outer SHA256s but the same canonical_sha256
    (because they share an embedded file that is the lex-min) get identical
    is_test assignments.
    """
    db_path = tmp_path / "samples.db"
    # canonical = min(outer, embedded...).  Both samples share embedded "11"*32
    # which is lex-min for both, so both get canonical = "11"*32.
    canonical = "11" * 32
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(_hopper_schema_sql())
        conn.executemany(
            "INSERT INTO samples (sha256, label, canonical_sha256, cleave_result)"
            " VALUES (?, ?, ?, ?)",
            [
                ("aa" * 32, "good", canonical, _make_report("aa" * 32, [canonical])),
                ("bb" * 32, "bad", canonical, _make_report("bb" * 32, [canonical])),
            ],
        )
        conn.commit()
    finally:
        conn.close()

    rows = list(stream_partitioned_metadata_grouped(db_path))
    assert len(rows) == 2
    # Both must have the same is_test since they share canonical_sha256.
    assert rows[0][2] == rows[1][2]


def test_partitioned_metadata_labels(tmp_path) -> None:
    """stream_partitioned_metadata_grouped yields correct labels and is_test flags."""
    db_path = tmp_path / "test.db"
    create_demo_db(db_path, n_benign=20, n_malware=20, seed=42)

    rows = list(stream_partitioned_metadata_grouped(db_path))
    assert len(rows) == 40

    # Every row should have (row_id, label, is_test, canonical_sha256).
    for row_id, label, is_test, canonical in rows:
        assert isinstance(row_id, int)
        assert label in (0, 1)
        assert isinstance(is_test, bool)
        assert isinstance(canonical, str)
