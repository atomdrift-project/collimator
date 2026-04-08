"""Load labeled samples from a hopper database (SQLite or PostgreSQL).

Train/test splitting is deterministic and archive-aware: each sample's
canonical_sha256 (the lexicographic minimum SHA256 across the sample
itself and all embedded files, pre-computed by hopper) is used as the
split key.  This ensures archives sharing an inner file always land in
the same partition, preventing data leakage.

  test set:  int(canonical_sha256[-2:], 16) < TEST_BUCKET_MAX   (12.5%)
  train set: everything else                                     (87.5%)
"""

from __future__ import annotations

import json
import logging
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# Samples whose canonical_sha256 last byte falls in [0, TEST_BUCKET_MAX)
# are reserved for threshold evaluation and excluded from training.
# 32/256 = 12.5%.
TEST_BUCKET_MAX = 32


@dataclass(frozen=True, slots=True)
class Sample:
    row_id: int
    sha256: str
    path: str
    label: int  # 1 = malware, 0 = benign
    report: dict[str, Any]
    formula: str = ""
    elements: str = ""
    score: int = 0
    mtime: str = ""
    cluster_id: int = -1
    canonical_sha256: str = ""


def is_test_sample(canonical_sha256: str) -> bool:
    """Deterministic test-set assignment based on canonical_sha256 last byte."""
    return int(canonical_sha256[-2:], 16) < TEST_BUCKET_MAX


def _label_int(label: str) -> int:
    """Map hopper label string to int. 'bad' -> 1, everything else -> 0."""
    return 1 if label == "bad" else 0


# ---------------------------------------------------------------------------
# Database access — the only place that knows about SQLite or PostgreSQL.
# ---------------------------------------------------------------------------

def _is_pg(dsn: Path | str) -> bool:
    s = str(dsn)
    return s.startswith(("postgres://", "postgresql://"))


@contextmanager
def _connect(dsn: Path | str, *, repeatable_read: bool = False):
    """Open a read-only connection to the hopper database.

    When *repeatable_read* is True the PostgreSQL connection uses
    REPEATABLE READ isolation, pinning a consistent snapshot for the
    lifetime of the connection.  This prevents concurrent hopper writes
    (new samples, label changes) from altering the row set mid-scan.
    SQLite read-only connections are already snapshot-isolated, so the
    flag is a no-op there.
    """
    if _is_pg(dsn):
        try:
            import psycopg  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(
                "psycopg is required for PostgreSQL: pip install psycopg[binary]",
            ) from exc
        with psycopg.connect(
            str(dsn),
            autocommit=False,
            options="-c default_transaction_isolation=repeatable\\ read" if repeatable_read else "",
        ) as conn:
            yield conn
    else:
        db_path = Path(str(dsn))
        if not db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            yield conn
        finally:
            conn.close()


def _execute(conn, query: str, params=None):
    """Execute a query, adapting for sqlite3 vs psycopg cursor styles."""
    if isinstance(conn, sqlite3.Connection):
        yield from conn.execute(query, params or [])
    else:
        # psycopg
        with conn.cursor() as cur:
            cur.execute(query, params)
            yield from cur


def _cleave_json(raw) -> str | None:
    """Normalize cleave_result to a JSON string, handling psycopg's auto-decode."""
    if raw is None:
        return None
    if isinstance(raw, str):
        return raw
    # psycopg auto-decodes JSONB to dict
    return json.dumps(raw)


def fetch_cleave_results(dsn: Path | str, ids: list[int]) -> dict[int, dict[str, Any]]:
    """Batch-fetch cleave_result JSON and related metadata by row IDs.

    Used by feature extraction workers. Each worker opens its own
    connection via this function — safe for multiprocessing.
    """
    if not ids:
        return {}
    with _connect(dsn) as conn:
        if _is_pg(dsn):
            # PostgreSQL: use ANY(%s) with array parameter.
            query = "SELECT id, cleave_result, formula, elements, score, mtime, 0 AS cluster_id FROM samples WHERE id = ANY(%s)"
            with conn.cursor() as cur:
                cur.execute(query, [ids])
                return {
                    int(rid): {
                        "cleave_result": _cleave_json(cr),
                        "formula": formula,
                        "elements": elements,
                        "score": score,
                        "mtime": str(mtime) if mtime else "",
                        "cluster_id": cluster_id,
                    }
                    for rid, cr, formula, elements, score, mtime, cluster_id in cur
                    if cr is not None
                }
        else:
            placeholders = ",".join("?" for _ in ids)
            query = f"SELECT id, cleave_result, formula, elements, score, mtime, 0 AS cluster_id FROM samples WHERE id IN ({placeholders})"  # noqa: S608
            return {
                int(rid): {
                    "cleave_result": cr,
                    "formula": formula,
                    "elements": elements,
                    "score": score,
                    "mtime": str(mtime) if mtime else "",
                    "cluster_id": cluster_id,
                }
                for rid, cr, formula, elements, score, mtime, cluster_id in conn.execute(query, ids)
                if cr is not None
            }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_TRAINABLE_QUERY = (
    "SELECT id, sha256, path, label, canonical_sha256, cleave_result, formula, elements, score, mtime, 0 AS cluster_id"
    " FROM samples"
    " WHERE label IN ('bad', 'good') AND cleave_result IS NOT NULL"
    " AND skip = ''"
    " ORDER BY id"
)

_METADATA_QUERY = (
    "SELECT id, sha256, label, canonical_sha256"
    " FROM samples"
    " WHERE label IN ('bad', 'good') AND cleave_result IS NOT NULL"
    " AND skip = ''"
    " ORDER BY id"
)


def stream_samples(
    db_path: Path | str,
    *,
    exclude_test: bool = False,
    only_test: bool = False,
    limit: int = 0,
) -> Iterator[Sample]:
    """Yield labeled samples from a hopper database (SQLite or PostgreSQL)."""
    query = _TRAINABLE_QUERY
    if limit > 0:
        query += f" LIMIT {limit}"
    with _connect(db_path, repeatable_read=True) as conn:
        for row_id, sha256, path, label, canonical, cleave_result, formula, elements, score, mtime, cluster_id in _execute(conn, query):
            split_key = canonical or sha256
            is_test = is_test_sample(split_key)
            if exclude_test and is_test:
                continue
            if only_test and not is_test:
                continue
            raw = _cleave_json(cleave_result)
            if raw is None:
                continue
            try:
                report = json.loads(raw)
            except json.JSONDecodeError:
                log.warning("invalid JSON for %s, skipping", sha256)
                continue
            yield Sample(
                row_id=int(row_id),
                sha256=sha256,
                path=path or "",
                label=_label_int(label),
                report=report,
                formula=formula or "",
                elements=elements or "",
                score=score or 0,
                mtime=str(mtime) if mtime else "",
                cluster_id=cluster_id,
                canonical_sha256=split_key,
            )


def load_samples(db_path: Path | str, limit: int = 0) -> list[Sample]:
    """Load all labeled samples from a hopper database."""
    log.info("loading samples from %s (limit=%d)", db_path, limit)
    samples = list(stream_samples(db_path, limit=limit))
    n_malware = sum(1 for s in samples if s.label == 1)
    n_benign = len(samples) - n_malware
    log.info(
        "loaded %d samples (%d malware, %d benign)",
        len(samples), n_malware, n_benign,
    )
    return samples


def stream_reports(
    db_path: Path | str,
    *,
    exclude_test: bool = False,
    only_test: bool = False,
) -> Iterator[tuple[dict[str, Any], int]]:
    """Yield (report, label) pairs."""
    for sample in stream_samples(
        db_path, exclude_test=exclude_test, only_test=only_test,
    ):
        yield sample.report, sample.label


def partition_row_ids(
    db_path: Path | str,
) -> tuple[list[int], list[tuple[int, int]], list[tuple[int, int]]]:
    """Partition samples into train/test by canonical_sha256.

    Returns (train_row_ids, train_ids_labels, test_ids_labels).
    """
    train_row_ids: list[int] = []
    train_ids_labels: list[tuple[int, int]] = []
    test_ids_labels: list[tuple[int, int]] = []
    for row_id, label, is_test, _canonical in stream_partitioned_metadata_grouped(db_path):
        if is_test:
            test_ids_labels.append((row_id, label))
        else:
            train_row_ids.append(row_id)
            train_ids_labels.append((row_id, label))
    return train_row_ids, train_ids_labels, test_ids_labels


def lookup_sample(
    db_path: Path | str,
    sha256_prefix: str,
) -> tuple[str, str, str, dict[str, Any]] | None:
    """Look up a sample by SHA256 prefix. Returns (sha256, path, label, report) or None."""
    with _connect(db_path) as conn:
        query = "SELECT sha256, path, label, cleave_result FROM samples WHERE sha256 LIKE ?"
        params: list[Any] = [f"{sha256_prefix}%"]
        if not isinstance(conn, sqlite3.Connection):
            query = "SELECT sha256, path, label, cleave_result FROM samples WHERE sha256 LIKE $1"
        for sha256, path, label, cleave_result in _execute(conn, query, params):
            raw = _cleave_json(cleave_result)
            if raw is None:
                return None
            try:
                report = json.loads(raw)
            except json.JSONDecodeError:
                return None
            return sha256, path or "", label, report
    return None


def stream_partitioned_metadata_grouped(
    db_path: Path | str,
) -> Iterator[tuple[int, int, bool, str]]:
    """Yield (row_id, label, is_test, canonical_sha256) without loading raw JSON."""
    with _connect(db_path, repeatable_read=True) as conn:
        for row_id, sha256, label, canonical in _execute(conn, _METADATA_QUERY):
            split_key = canonical or sha256
            yield (
                int(row_id),
                _label_int(label),
                is_test_sample(split_key),
                split_key,
            )
