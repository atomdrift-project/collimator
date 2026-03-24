"""Load labeled samples from cyclotron's SQLite database."""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

log = logging.getLogger(__name__)

# Terminal statuses that represent confirmed classifications.
# See cyclotron/db.go for the full status state machine.
#
# All bad* statuses (except bad-benign, which was reclassified as benign) are
# treated as malware regardless of pipeline progress — this lets us train on
# samples cleave hasn't fully confirmed, finding patterns it can't yet detect.
MALWARE_STATUSES = frozenset({
    "bad",           # known-bad, pending analysis
    "bad-review",    # needs reverse engineering
    "bad-reversed",  # has been reverse engineered
    "bad-gapped",    # detection gaps identified
    "bad-exhausted", # pipeline gave up, still malware
    "good-malicious", # reclassified from good pipeline
})
BENIGN_STATUSES = frozenset({"good", "bad-benign"})
ALL_TERMINAL = MALWARE_STATUSES | BENIGN_STATUSES

# Samples whose SHA256 last byte falls in [0, TEST_BUCKET_MAX) are reserved
# for threshold evaluation and excluded from training. 32/256 = 12.5%.
TEST_BUCKET_MAX = 32
SPLIT_CACHE_VERSION = 1
SPLIT_METADATA_TABLE = "collimator_split_metadata"
SPLIT_ASSIGNMENTS_TABLE = "collimator_sample_splits"
NATIVE_SPLIT_TABLE = "sample_splits"


@dataclass(frozen=True, slots=True)
class SplitAssignment:
    sample_row_id: int
    group_id: str
    is_test: bool


@dataclass(frozen=True, slots=True)
class Sample:
    row_id: int
    sha256: str
    path: str
    label: int  # 1 = malware, 0 = benign
    report: dict[str, Any]


def stream_samples(
    db_path: Path,
    *,
    exclude_test: bool = False,
    only_test: bool = False,
    limit: int = 0,
) -> Iterator[Sample]:
    """Yield labeled samples from the database without loading all rows."""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    split_assignments = load_split_assignments(db_path)
    placeholders = ",".join("?" for _ in ALL_TERMINAL)
    query = (
        "SELECT id, sha256, path, status, cleave_json"
        f" FROM samples WHERE status IN ({placeholders})"
    )
    if limit > 0:
        query += f" LIMIT {limit}"
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        for row_id, sha256, path, status, cleave_json in conn.execute(
            query, tuple(sorted(ALL_TERMINAL)),
        ):
            if not cleave_json:
                continue
            assignment = split_assignments.get(int(row_id))
            is_test = assignment.is_test if assignment is not None else is_test_sample(sha256)
            if exclude_test and is_test:
                continue
            if only_test and not is_test:
                continue
            try:
                report = json.loads(cleave_json)
            except json.JSONDecodeError:
                log.warning("invalid JSON for %s, skipping", sha256)
                continue
            yield Sample(
                row_id=int(row_id),
                sha256=sha256,
                path=path,
                label=1 if status in MALWARE_STATUSES else 0,
                report=report,
            )
    finally:
        conn.close()


def load_samples(db_path: Path, limit: int = 0) -> list[Sample]:
    """Load labeled samples from a cyclotron database."""
    log.info("loading samples from %s (limit=%d)", db_path, limit)
    samples = list(stream_samples(db_path, limit=limit))

    n_malware = sum(1 for s in samples if s.label == 1)
    n_benign = len(samples) - n_malware
    log.info(
        "loaded %d samples (%d malware, %d benign)",
        len(samples), n_malware, n_benign,
    )
    return samples


def is_test_sample(sha256: str) -> bool:
    """Deterministic test-set assignment based on SHA256 last byte."""
    return int(sha256[-2:], 16) < TEST_BUCKET_MAX


def _db_fingerprint(db_path: Path) -> tuple[int, int, int]:
    """Return a fingerprint derived from the samples table, not DB file metadata."""
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        row_count, max_id, max_updated = conn.execute(
            "SELECT COUNT(*), COALESCE(MAX(id), 0), COALESCE(MAX(updated_at), 0) FROM samples"
        ).fetchone()
    finally:
        conn.close()
    return int(row_count), int(max_id), int(max_updated)


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table', 'view') AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _load_native_split_assignments(db_path: Path) -> dict[int, SplitAssignment] | None:
    """Load split assignments from cyclotron's native sample_splits table when available."""
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        if not _table_exists(conn, NATIVE_SPLIT_TABLE):
            return None
        placeholders = ",".join("?" for _ in ALL_TERMINAL)
        expected_terminal = int(
            conn.execute(
                f"SELECT COUNT(*) FROM samples WHERE status IN ({placeholders})",
                tuple(sorted(ALL_TERMINAL)),
            ).fetchone()[0]
        )
        rows = list(
            conn.execute(
                (
                    f"SELECT ss.sample_id, ss.split_name "
                    f"FROM {NATIVE_SPLIT_TABLE} ss "
                    "JOIN samples s ON s.id = ss.sample_id "
                    f"WHERE s.status IN ({placeholders})"
                ),
                tuple(sorted(ALL_TERMINAL)),
            )
        )
    finally:
        conn.close()

    if not rows or len(rows) != expected_terminal:
        return None

    return {
        int(sample_id): SplitAssignment(
            sample_row_id=int(sample_id),
            group_id=f"s{int(sample_id)}",
            is_test=(str(split_name) == "test"),
        )
        for sample_id, split_name in rows
    }


def _extract_report_file_shas(raw_report: str, outer_sha256: str) -> list[str]:
    shas: list[str] = [outer_sha256]
    try:
        report = json.loads(raw_report)
    except json.JSONDecodeError:
        return shas

    for file_entry in report.get("files") or []:
        if not isinstance(file_entry, dict):
            continue
        file_sha = file_entry.get("sha256")
        if isinstance(file_sha, str) and len(file_sha) == 64:
            shas.append(file_sha)
    return sorted(set(shas))


def _find(parent: dict[int, int], x: int) -> int:
    root = x
    while parent[root] != root:
        root = parent[root]
    while parent[x] != x:
        nxt = parent[x]
        parent[x] = root
        x = nxt
    return root


def _union(parent: dict[int, int], size: dict[int, int], a: int, b: int) -> int:
    ra = _find(parent, a)
    rb = _find(parent, b)
    if ra == rb:
        return ra
    if size[ra] < size[rb]:
        ra, rb = rb, ra
    parent[rb] = ra
    size[ra] += size[rb]
    return ra


def build_split_cache(db_path: Path) -> Path:
    """Rebuild split assignments from scratch inside the given database."""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    row_count, max_id, max_updated = _db_fingerprint(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(f"DROP TABLE IF EXISTS {SPLIT_METADATA_TABLE}")
        conn.execute(f"DROP TABLE IF EXISTS {SPLIT_ASSIGNMENTS_TABLE}")
        conn.execute(f"""
            CREATE TABLE {SPLIT_METADATA_TABLE} (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.execute(f"""
            CREATE TABLE {SPLIT_ASSIGNMENTS_TABLE} (
                sample_row_id INTEGER PRIMARY KEY,
                group_id TEXT NOT NULL,
                is_test INTEGER NOT NULL,
                split_version INTEGER NOT NULL,
                FOREIGN KEY(sample_row_id) REFERENCES samples(id)
            )
        """)

        log.info("populating split cache via SQL (deterministic SHA256 buckets)")
        placeholders = ",".join("?" for _ in ALL_TERMINAL)
        # Order: TEST_BUCKET_MAX, SPLIT_CACHE_VERSION, then sorted(ALL_TERMINAL) for the IN clause.
        sql_args = [TEST_BUCKET_MAX, SPLIT_CACHE_VERSION] + list(sorted(ALL_TERMINAL))
        conn.execute(
            f"INSERT INTO {SPLIT_ASSIGNMENTS_TABLE}(sample_row_id, group_id, is_test, split_version)"
            " SELECT id, 's'||id, (instr('0123456789abcdef', substr(sha256, -1, 1)) + 16 * instr('0123456789abcdef', substr(sha256, -2, 1)) - 17) < ?, ? FROM samples WHERE status IN (" + placeholders + ")",
            sql_args,
        )

        conn.executemany(
            f"INSERT INTO {SPLIT_METADATA_TABLE}(key, value) VALUES (?, ?)",
            [
                ("version", str(SPLIT_CACHE_VERSION)),
                ("test_bucket_max", str(TEST_BUCKET_MAX)),
                ("source_row_count", str(row_count)),
                ("source_max_id", str(max_id)),
                ("source_max_updated_at", str(max_updated)),
            ],
        )
        conn.execute(
            f"CREATE INDEX idx_collimator_sample_splits_is_test ON {SPLIT_ASSIGNMENTS_TABLE}(is_test)"
        )
        conn.execute(
            f"CREATE INDEX idx_collimator_sample_splits_group_id ON {SPLIT_ASSIGNMENTS_TABLE}(group_id)"
        )
        conn.commit()
    finally:
        conn.close()

    log.info("rebuilt split metadata in %s", db_path)
    return db_path


def ensure_split_cache(db_path: Path) -> Path:
    """Ensure in-DB split assignments exist and match the current database."""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    row_count, max_id, max_updated = _db_fingerprint(db_path)
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        metadata = dict(conn.execute(f"SELECT key, value FROM {SPLIT_METADATA_TABLE}"))
        cached_rows = int(conn.execute(f"SELECT COUNT(*) FROM {SPLIT_ASSIGNMENTS_TABLE}").fetchone()[0])
    except sqlite3.DatabaseError:
        return build_split_cache(db_path)
    finally:
        conn.close()

    expected = {
        "version": str(SPLIT_CACHE_VERSION),
        "test_bucket_max": str(TEST_BUCKET_MAX),
        "source_row_count": str(row_count),
        "source_max_id": str(max_id),
        "source_max_updated_at": str(max_updated),
    }
    if metadata != expected or cached_rows != row_count:
        return build_split_cache(db_path)
    return db_path


def load_split_assignments(db_path: Path) -> dict[int, SplitAssignment]:
    """Load split assignments, rebuilding them automatically when needed."""
    # We prioritize our internal cache because it respects the current TEST_BUCKET_MAX.
    ensure_split_cache(db_path)
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        return {
            int(row_id): SplitAssignment(
                sample_row_id=int(row_id),
                group_id=str(group_id),
                is_test=bool(is_test),
            )
            for row_id, group_id, is_test in conn.execute(
                f"SELECT sample_row_id, group_id, is_test FROM {SPLIT_ASSIGNMENTS_TABLE}"
            )
        }
    finally:
        conn.close()


def load_partitioned_group_ids(db_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load cached group IDs aligned with partitioned raw-report streaming order."""
    split_assignments = load_split_assignments(db_path)
    train_groups: list[str] = []
    test_groups: list[str] = []
    placeholders = ",".join("?" for _ in ALL_TERMINAL)
    query = (
        "SELECT id, sha256, cleave_json, status"
        f" FROM samples WHERE status IN ({placeholders})"
    )
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        for row_id, sha256, cleave_json, status in conn.execute(query, tuple(sorted(ALL_TERMINAL))):
            if status not in ALL_TERMINAL or not cleave_json:
                continue
            assignment = split_assignments.get(int(row_id))
            group_id = assignment.group_id if assignment is not None else sha256
            if assignment is not None and assignment.is_test:
                test_groups.append(group_id)
            elif assignment is None and is_test_sample(sha256):
                test_groups.append(group_id)
            else:
                train_groups.append(group_id)
    finally:
        conn.close()
    return np.array(train_groups, dtype=object), np.array(test_groups, dtype=object)


def load_train_group_ids(db_path: Path) -> np.ndarray:
    """Load cached group IDs aligned with non-test training stream order."""
    train_groups, _test_groups = load_partitioned_group_ids(db_path)
    return train_groups


def stream_reports(
    db_path: Path,
    *,
    exclude_test: bool = False,
    only_test: bool = False,
) -> Iterator[tuple[dict[str, Any], int]]:
    """Yield (report, label) pairs from the database without holding all in memory.

    Each report dict is parsed from JSON, yielded once, and discarded.
    When exclude_test=True, test-bucket samples (5%) are skipped.
    When only_test=True, only test-bucket samples are yielded.
    """
    for sample in stream_samples(
        db_path,
        exclude_test=exclude_test,
        only_test=only_test,
    ):
        yield sample.report, sample.label


def stream_raw_reports(
    db_path: Path,
    *,
    exclude_test: bool = False,
    only_test: bool = False,
) -> Iterator[tuple[str, int]]:
    """Yield raw cleave JSON strings and labels without parent-process decoding."""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    split_assignments = load_split_assignments(db_path)
    placeholders = ",".join("?" for _ in ALL_TERMINAL)
    query = (
        "SELECT id, sha256, status, cleave_json"
        f" FROM samples WHERE status IN ({placeholders})"
    )
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        for row_id, sha256, status, cleave_json in conn.execute(
            query, tuple(sorted(ALL_TERMINAL)),
        ):
            if not cleave_json:
                continue
            assignment = split_assignments.get(int(row_id))
            is_test = assignment.is_test if assignment is not None else is_test_sample(sha256)
            if exclude_test and is_test:
                continue
            if only_test and not is_test:
                continue
            yield cleave_json, (1 if status in MALWARE_STATUSES else 0)
    finally:
        conn.close()


def stream_partitioned_raw_reports(
    db_path: Path,
) -> Iterator[tuple[str, int, bool]]:
    """Yield raw cleave JSON, label, and test-split membership in one pass."""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    split_assignments = load_split_assignments(db_path)
    placeholders = ",".join("?" for _ in ALL_TERMINAL)
    query = (
        "SELECT id, sha256, status, cleave_json"
        f" FROM samples WHERE status IN ({placeholders})"
    )
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        for row_id, sha256, status, cleave_json in conn.execute(
            query, tuple(sorted(ALL_TERMINAL)),
        ):
            if not cleave_json:
                continue
            yield (
                cleave_json,
                1 if status in MALWARE_STATUSES else 0,
                split_assignments.get(int(row_id), SplitAssignment(int(row_id), "", is_test_sample(sha256))).is_test,
            )
    finally:
        conn.close()


def stream_partitioned_metadata_grouped(
    db_path: Path,
) -> Iterator[tuple[int, int, bool, str]]:
    """Yield (row_id, label, is_test, group_id) without loading raw JSON.

    Used to reservoir-sample train/test splits without holding JSON in memory.
    """
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    split_assignments = load_split_assignments(db_path)
    placeholders = ",".join("?" for _ in ALL_TERMINAL)
    query = (
        "SELECT id, sha256, status"
        f" FROM samples WHERE status IN ({placeholders})"
    )
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        for row_id, sha256, status in conn.execute(query, tuple(sorted(ALL_TERMINAL))):
            assignment = split_assignments.get(int(row_id))
            if assignment is None:
                group_id = sha256
                is_test = is_test_sample(sha256)
            else:
                group_id = assignment.group_id
                is_test = assignment.is_test
            yield (
                int(row_id),
                1 if status in MALWARE_STATUSES else 0,
                is_test,
                group_id,
            )
    finally:
        conn.close()


def stream_raw_reports_by_row_ids(
    db_path: Path,
    row_ids: frozenset[int],
) -> Iterator[tuple[str, int]]:
    """Stream (raw_json, label) for selected row IDs via a full table scan.

    Only the matching rows are yielded; unselected rows are skipped without
    buffering them in memory, so peak memory is O(batch) not O(table).
    """
    if not row_ids:
        return
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    placeholders = ",".join("?" for _ in ALL_TERMINAL)
    query = (
        "SELECT id, status, cleave_json"
        f" FROM samples WHERE status IN ({placeholders})"
    )
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        for row_id, status, cleave_json in conn.execute(query, tuple(sorted(ALL_TERMINAL))):
            if int(row_id) not in row_ids or not cleave_json:
                continue
            yield cleave_json, (1 if status in MALWARE_STATUSES else 0)
    finally:
        conn.close()


def stream_partitioned_raw_reports_grouped(
    db_path: Path,
) -> Iterator[tuple[str, int, bool, str]]:
    """Yield raw JSON, label, test membership, and cached group ID in one pass."""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    split_assignments = load_split_assignments(db_path)
    placeholders = ",".join("?" for _ in ALL_TERMINAL)
    query = (
        "SELECT id, sha256, status, cleave_json"
        f" FROM samples WHERE status IN ({placeholders})"
    )
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        for row_id, sha256, status, cleave_json in conn.execute(
            query, tuple(sorted(ALL_TERMINAL)),
        ):
            if not cleave_json:
                continue
            assignment = split_assignments.get(int(row_id))
            if assignment is None:
                group_id = sha256
                is_test = is_test_sample(sha256)
            else:
                group_id = assignment.group_id
                is_test = assignment.is_test
            yield (
                cleave_json,
                1 if status in MALWARE_STATUSES else 0,
                is_test,
                group_id,
            )
    finally:
        conn.close()
