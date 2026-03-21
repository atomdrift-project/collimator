"""Tests for split-cache construction and refresh."""

from __future__ import annotations

import json
import sqlite3

from collimator import data


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


def _create_db(db_path) -> None:
    conn = sqlite3.connect(db_path)
    try:
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
        conn.executemany(
            "INSERT INTO samples (sha256, path, status, cleave_json) VALUES (?, ?, ?, ?)",
            [
                (
                    "aa" * 32,
                    "/tmp/a.zip",
                    "good",
                    _make_report("aa" * 32, ["11" * 32]),
                ),
                (
                    "00" * 32,
                    "/tmp/b.zip",
                    "bad",
                    _make_report("00" * 32, ["11" * 32]),
                ),
            ],
        )
        conn.commit()
    finally:
        conn.close()


def test_shared_embedded_sha_forces_same_partition(tmp_path) -> None:
    db_path = tmp_path / "samples.db"
    _create_db(db_path)

    rows = list(data.stream_partitioned_raw_reports(db_path))

    assert len(rows) == 2
    assert rows[0][2] == rows[1][2]


def test_split_cache_rebuilds_when_row_count_changes(tmp_path) -> None:
    db_path = tmp_path / "samples.db"
    _create_db(db_path)

    assignments_before = data.load_split_assignments(db_path)
    assert len(assignments_before) == 2

    conn = sqlite3.connect(db_path)
    try:
        rows = dict(conn.execute(f"SELECT key, value FROM {data.SPLIT_METADATA_TABLE}"))
        count = conn.execute(f"SELECT COUNT(*) FROM {data.SPLIT_ASSIGNMENTS_TABLE}").fetchone()[0]
    finally:
        conn.close()
    assert rows["version"] == str(data.SPLIT_CACHE_VERSION)
    assert count == 2

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "INSERT INTO samples (sha256, path, status, cleave_json) VALUES (?, ?, ?, ?)",
            (
                "ff" * 32,
                "/tmp/c.zip",
                "good",
                _make_report("ff" * 32, ["22" * 32]),
            ),
        )
        conn.commit()
    finally:
        conn.close()

    assignments_after = data.load_split_assignments(db_path)

    assert len(assignments_after) == 3


def test_native_sample_splits_take_precedence(tmp_path) -> None:
    db_path = tmp_path / "samples.db"
    _create_db(db_path)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            CREATE TABLE sample_splits (
                sample_id INTEGER PRIMARY KEY,
                split_name TEXT NOT NULL
            )
        """)
        conn.executemany(
            "INSERT INTO sample_splits (sample_id, split_name) VALUES (?, ?)",
            [
                (1, "train"),
                (2, "test"),
            ],
        )
        conn.commit()
    finally:
        conn.close()

    assignments = data.load_split_assignments(db_path)

    assert len(assignments) == 2
    assert assignments[1].is_test is False
    assert assignments[1].group_id == "s1"
    assert assignments[2].is_test is True
    assert assignments[2].group_id == "s2"


def test_partial_native_sample_splits_fall_back_to_cache(tmp_path) -> None:
    db_path = tmp_path / "samples.db"
    _create_db(db_path)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            CREATE TABLE sample_splits (
                sample_id INTEGER PRIMARY KEY,
                split_name TEXT NOT NULL
            )
        """)
        conn.execute(
            "INSERT INTO sample_splits (sample_id, split_name) VALUES (?, ?)",
            (1, "train"),
        )
        conn.commit()
    finally:
        conn.close()

    assignments = data.load_split_assignments(db_path)

    assert len(assignments) == 2
    assert assignments[1].group_id.startswith("g")
    assert assignments[2].group_id.startswith("g")
