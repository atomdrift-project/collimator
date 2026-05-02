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
import os
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

# Minimum hopper score for a sample to be considered trainable / evaluable.
# Controls the SQL-level filter applied to _TRAINABLE_QUERY and _METADATA_QUERY.
# Override via COLLIMATOR_MIN_SAMPLE_SCORE env var for experiments.
# v15 used >= 8, v16 lowered to >= 3 (balanced ~1:1 bad:good pool).
_default_min = 3
try:
    MIN_SAMPLE_SCORE = int(os.getenv("COLLIMATOR_MIN_SAMPLE_SCORE", str(_default_min)))
except ValueError:
    MIN_SAMPLE_SCORE = _default_min


def snapshot_max_id(db_path: Path | str) -> int:
    """Return max(id) of trainable samples at this moment.

    Used to pin the dataset for a single experiment / training run so that
    concurrent inserts to the hopper database don't cause drift between runs.
    Pass the returned value as ``max_id`` to ``stream_partitioned_metadata_grouped``
    or ``partition_row_ids``.
    """
    query = (
        "SELECT MAX(id) FROM samples"
        " WHERE label IN ('bad', 'good') AND cleave_result IS NOT NULL"
        f" AND score >= {MIN_SAMPLE_SCORE} AND skip = ''"
    )
    with _connect(db_path) as conn:
        for (max_id,) in _execute(conn, query):
            return int(max_id) if max_id is not None else 0
    return 0


_TRAINABLE_QUERY = (
    "SELECT id, sha256, path, label, canonical_sha256, cleave_result, formula, elements, score, mtime, 0 AS cluster_id"
    " FROM samples"
    " WHERE label IN ('bad', 'good') AND cleave_result IS NOT NULL"
    f" AND score >= {MIN_SAMPLE_SCORE}"
    " AND skip = ''"
    " ORDER BY id"
)

_METADATA_QUERY = (
    "SELECT id, sha256, label, canonical_sha256, score"
    " FROM samples"
    " WHERE label IN ('bad', 'good') AND cleave_result IS NOT NULL"
    f" AND score >= {MIN_SAMPLE_SCORE}"
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


def stream_labeled_samples_full(
    db_path: Path | str,
    *,
    path_substr: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    limit: int = 0,
    max_id: int = 0,
) -> Iterator[Sample]:
    """Yield labeled, non-skipped samples without the MIN_SAMPLE_SCORE filter.

    This is for operational corpus analysis over the full labeled hopper set,
    including low-score benign rows that are intentionally excluded from
    training/evaluation partitions.
    """
    with _connect(db_path, repeatable_read=True) as conn:
        params: list[Any] = []
        placeholder = "?" if isinstance(conn, sqlite3.Connection) else "%s"
        query = (
            "SELECT id, sha256, path, label, canonical_sha256, cleave_result, formula, elements, score, mtime, 0 AS cluster_id"
            " FROM samples"
            " WHERE label IN ('bad', 'good')"
            " AND cleave_result IS NOT NULL"
            " AND skip = ''"
        )
        if max_id > 0:
            query += f" AND id <= {int(max_id)}"
        if path_substr:
            query += f" AND LOWER(path) LIKE {placeholder}"
            params.append(f"%{path_substr.lower()}%")
        if min_score is not None:
            query += f" AND score >= {placeholder}"
            params.append(int(min_score))
        if max_score is not None:
            query += f" AND score <= {placeholder}"
            params.append(int(max_score))
        query += " ORDER BY id"
        if limit > 0:
            query += f" LIMIT {int(limit)}"

        for row_id, sha256, path, label, canonical, cleave_result, formula, elements, score, mtime, cluster_id in _execute(conn, query, params):
            split_key = canonical or sha256
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


def stream_labeled_metadata_full(
    db_path: Path | str,
    *,
    path_substr: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    limit: int = 0,
    max_id: int = 0,
) -> Iterator[tuple[int, str, str, int, int]]:
    """Yield labeled, non-skipped sample metadata without loading JSON reports."""
    with _connect(db_path, repeatable_read=True) as conn:
        params: list[Any] = []
        placeholder = "?" if isinstance(conn, sqlite3.Connection) else "%s"
        query = (
            "SELECT id, sha256, path, label, score"
            " FROM samples"
            " WHERE label IN ('bad', 'good')"
            " AND cleave_result IS NOT NULL"
            " AND skip = ''"
        )
        if max_id > 0:
            query += f" AND id <= {int(max_id)}"
        if path_substr:
            query += f" AND LOWER(path) LIKE {placeholder}"
            params.append(f"%{path_substr.lower()}%")
        if min_score is not None:
            query += f" AND score >= {placeholder}"
            params.append(int(min_score))
        if max_score is not None:
            query += f" AND score <= {placeholder}"
            params.append(int(max_score))
        query += " ORDER BY id"
        if limit > 0:
            query += f" LIMIT {int(limit)}"

        for row_id, sha256, path, label, score in _execute(conn, query, params):
            yield int(row_id), sha256, path or "", score or 0, _label_int(label)


def stream_labeled_metadata_full_with_size(
    db_path: Path | str,
    *,
    path_substr: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    limit: int = 0,
    max_id: int = 0,
) -> Iterator[tuple[int, str, str, int, int, int]]:
    """Yield full-corpus metadata plus serialized cleave_result byte estimate."""
    with _connect(db_path, repeatable_read=True) as conn:
        params: list[Any] = []
        placeholder = "?" if isinstance(conn, sqlite3.Connection) else "%s"
        json_len_expr = "LENGTH(cleave_result)" if isinstance(conn, sqlite3.Connection) else "LENGTH(cleave_result::text)"
        query = (
            f"SELECT id, sha256, path, label, score, {json_len_expr}"
            " FROM samples"
            " WHERE label IN ('bad', 'good')"
            " AND cleave_result IS NOT NULL"
            " AND skip = ''"
        )
        if max_id > 0:
            query += f" AND id <= {int(max_id)}"
        if path_substr:
            query += f" AND LOWER(path) LIKE {placeholder}"
            params.append(f"%{path_substr.lower()}%")
        if min_score is not None:
            query += f" AND score >= {placeholder}"
            params.append(int(min_score))
        if max_score is not None:
            query += f" AND score <= {placeholder}"
            params.append(int(max_score))
        query += " ORDER BY id"
        if limit > 0:
            query += f" LIMIT {int(limit)}"

        for row_id, sha256, path, label, score, json_bytes in _execute(conn, query, params):
            yield (
                int(row_id),
                sha256,
                path or "",
                score or 0,
                _label_int(label),
                int(json_bytes or 0),
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
    min_malware_training_score: int = 0,
    max_id: int = 0,
) -> tuple[list[int], list[tuple[int, int]], list[tuple[int, int]]]:
    """Partition samples into train/test by canonical_sha256.

    Returns (train_row_ids, train_ids_labels, test_ids_labels).
    Pass ``max_id`` from ``snapshot_max_id`` to pin the dataset.
    """
    train_row_ids: list[int] = []
    train_ids_labels: list[tuple[int, int]] = []
    test_ids_labels: list[tuple[int, int]] = []
    for row_id, label, is_test, _canonical, score in stream_partitioned_metadata_grouped(db_path, max_id=max_id):
        if is_test:
            test_ids_labels.append((row_id, label))
        else:
            # Heuristic pruning: ignore low-score malware during training.
            if label == 1 and score < min_malware_training_score:
                continue
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
            query = "SELECT sha256, path, label, cleave_result FROM samples WHERE sha256 LIKE %s"
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
    limit: int = 0,
    max_id: int = 0,
) -> Iterator[tuple[int, int, bool, str, int]]:
    """Yield (row_id, label, is_test, canonical_sha256, score) without loading raw JSON.

    If ``max_id`` > 0, only rows with ``id <= max_id`` are returned. Use this with
    a value from ``snapshot_max_id`` to pin the dataset for a single run, so that
    concurrent inserts don't cause drift.
    """
    query = _METADATA_QUERY
    if max_id > 0:
        # Inject id cap before ORDER BY. _METADATA_QUERY ends with ORDER BY id.
        query = query.replace(" ORDER BY id", f" AND id <= {int(max_id)} ORDER BY id")
    if limit > 0:
        query += f" LIMIT {limit}"
    with _connect(db_path, repeatable_read=True) as conn:
        for row_id, sha256, label, canonical, score in _execute(conn, query):
            split_key = canonical or sha256
            yield (
                int(row_id),
                _label_int(label),
                is_test_sample(split_key),
                split_key,
                score or 0,
            )


def count_labeled_by_partition_full(
    db_path: Path | str,
    *,
    max_id: int = 0,
) -> dict[str, dict[str, int]]:
    """Count all labeled, non-skipped rows by partition without score filtering.

    Training intentionally focuses on rows at or above ``MIN_SAMPLE_SCORE``.
    FP-per-million reporting, however, is a corpus-level good-file rate, so it
    needs the full labeled good-file denominator, including low-score rows.
    """
    counts = {
        "train": {"good": 0, "bad": 0, "total": 0},
        "test": {"good": 0, "bad": 0, "total": 0},
        "all": {"good": 0, "bad": 0, "total": 0},
    }
    with _connect(db_path, repeatable_read=True) as conn:
        query = (
            "SELECT id, sha256, label, canonical_sha256"
            " FROM samples"
            " WHERE label IN ('bad', 'good')"
            " AND cleave_result IS NOT NULL"
            " AND skip = ''"
        )
        if max_id > 0:
            query += f" AND id <= {int(max_id)}"
        for _row_id, sha256, label, canonical in _execute(conn, query):
            split_key = canonical or sha256
            part = "test" if is_test_sample(split_key) else "train"
            name = "bad" if _label_int(label) == 1 else "good"
            counts[part][name] += 1
            counts[part]["total"] += 1
            counts["all"][name] += 1
            counts["all"]["total"] += 1
    return counts


def labeled_corpus_metadata_full(
    db_path: Path | str,
    *,
    max_id: int = 0,
) -> dict[str, int]:
    """Return row counts for the full labeled threshold/FP corpus."""
    with _connect(db_path, repeatable_read=True) as conn:
        query = (
            "SELECT"
            " COUNT(*),"
            " COALESCE(SUM(CASE WHEN label = 'bad' THEN 1 ELSE 0 END), 0),"
            " COALESCE(SUM(CASE WHEN label = 'good' THEN 1 ELSE 0 END), 0),"
            " COALESCE(MAX(id), 0)"
            " FROM samples"
            " WHERE label IN ('bad', 'good')"
            " AND cleave_result IS NOT NULL"
            " AND skip = ''"
        )
        if max_id > 0:
            query += f" AND id <= {int(max_id)}"
        for total, bad, good, row_max_id in _execute(conn, query):
            return {
                "samples": int(total or 0),
                "malware": int(bad or 0),
                "benign": int(good or 0),
                "max_row_id": int(row_max_id or 0),
            }
    return {"samples": 0, "malware": 0, "benign": 0, "max_row_id": 0}
