"""Load labeled samples from a hopper database (SQLite or PostgreSQL).

Splitting is deterministic and archive-aware: each sample's
canonical_sha256 (the lexicographic minimum SHA256 across the sample
itself and all embedded files, pre-computed by hopper) is used as the
split key.  This ensures archives sharing an inner file always land in
the same partition, preventing data leakage.

Three-way partition by canonical_sha256 last byte:

  test:  byte < TEST_BUCKET_MAX                       (12.5%)
  dev:   TEST_BUCKET_MAX <= byte < DEV_BUCKET_MAX     (12.5%)
  train: byte >= DEV_BUCKET_MAX                       (75%)

- Train rows fit models.
- Dev rows fit calibrators and search L0..L9 thresholds; autocollie
  screens candidates against dev.
- Test rows produce headline metrics. Touched once per submission.

See METHODOLOGY.md for why each partition is disjoint and what limits
this still doesn't address (family-level correlation, temporal drift).
"""

from __future__ import annotations

import json
import os
import logging
import random
import sqlite3


# Pure-compression suffixes — formats with no multi-file container of
# their own. When they appear AT THE END of a compound filetype string
# (e.g. tar.gz, tar.bz2.xz) we strip them so the inner container surfaces.
# Order matters: longest first (none here overlap, but the pattern would
# extend if we add multi-char ones later).
#
# This list is the deploy-side source of truth and is mirrored verbatim
# in litmus/src/features.rs (PURE_COMPRESSION_SUFFIXES). Keep them in
# sync — collimator emits training labels using this rule and litmus
# routes scan-time files using it.
_PURE_COMPRESSION_SUFFIXES: tuple[str, ...] = (
    "gz", "bz2", "xz", "zst", "z", "lzma",
)


def normalize_archive_filetype(file_type: str | None) -> str:
    """Collapse compression-suffixed archive labels onto their container.

    `tar.gz` → `tar`, `tar.bz2.xz` → `tar`. Bare compression labels (`gz`,
    `bz2`, …) are returned as-is and remain in `RAW_COMPRESSED_FILETYPES`
    so the specialist suite continues to skip them. Lowercases and trims
    whitespace as a side-effect.

    The rule is intentionally textual: cleave emits compound labels like
    `tar.gz`, and we want every archive specialist (tar, zip, jar, …) to
    train on AND route together with its compressed variants.
    """
    if file_type is None:
        return ""
    normalized = str(file_type).strip().lower()
    while "." in normalized:
        head, _, tail = normalized.rpartition(".")
        if tail not in _PURE_COMPRESSION_SUFFIXES:
            break
        if not head:
            break
        normalized = head
    return normalized
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# canonical_sha256 last-byte ranges. test < TEST_BUCKET_MAX, dev in
# [TEST_BUCKET_MAX, DEV_BUCKET_MAX), train >= DEV_BUCKET_MAX.
# 32/256 = 12.5% (test), 32/256 = 12.5% (dev), 192/256 = 75% (train).
TEST_BUCKET_MAX = 32
DEV_BUCKET_MAX = 64


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
    """True if the row belongs to the locked test partition."""
    return int(canonical_sha256[-2:], 16) < TEST_BUCKET_MAX


def is_dev_sample(canonical_sha256: str) -> bool:
    """True if the row belongs to the dev partition (selection + calibration)."""
    last = int(canonical_sha256[-2:], 16)
    return TEST_BUCKET_MAX <= last < DEV_BUCKET_MAX


def partition_of(canonical_sha256: str) -> str:
    """Return 'train', 'dev', or 'test' for a given canonical hash."""
    last = int(canonical_sha256[-2:], 16)
    if last < TEST_BUCKET_MAX:
        return "test"
    if last < DEV_BUCKET_MAX:
        return "dev"
    return "train"


def oof_fold_of(canonical_sha256: str) -> int | None:
    """Return the OOF fold (0 or 1) for non-test rows, or None for test.

    For publication-quality calibration via k=2 out-of-fold predictions,
    the train+dev partition (byte >= TEST_BUCKET_MAX) is split deterministically
    into two halves on the second-to-last hex digit (parity of the next-to-
    last byte). This is independent of the train/dev split, so each fold
    contains roughly half of train rows and half of dev rows.

    Test partition rows return None — they're never part of OOF calibration
    and stay locked for headline reporting.
    """
    if int(canonical_sha256[-2:], 16) < TEST_BUCKET_MAX:
        return None
    return int(canonical_sha256[-4:-2], 16) & 1


def _label_int(label: str) -> int:
    """Map hopper label string to int. 'bad' -> 1, everything else -> 0."""
    return 1 if label == "bad" else 0


# ---------------------------------------------------------------------------
# Database access — the only place that knows about SQLite or PostgreSQL.
# ---------------------------------------------------------------------------

def _is_pg(dsn: Path | str) -> bool:
    s = str(dsn)
    return s.startswith(("postgres://", "postgresql://"))


# Connection-establishment retry: exponential backoff with jitter, bounded by a
# total time BUDGET (not a fixed attempt count). The DB is a local replica, so a
# connect failure is almost always transient pool exhaustion during a heavy
# parallel training cycle (many workers each open a repeatable-read snapshot, so
# the ~max_connections slots fill up). Routes finish and release slots over
# minutes, so we wait patiently — first backoff ~4s, exponential from there —
# rather than giving up in ~1 minute. Capped at ~2h total so a genuinely-down
# database still fails eventually. Only applies to the initial connect — once a
# connection is open, mid-stream failures still propagate to the caller (long
# streaming queries can't resume without losing iterator position). Override via
# COLLIMATOR_DB_CONNECT_{BASE_DELAY,MAX_DELAY,MAX_TOTAL}_S.
_DB_CONNECT_BASE_DELAY_S = float(os.getenv("COLLIMATOR_DB_CONNECT_BASE_DELAY_S", "4.0"))
_DB_CONNECT_MAX_DELAY_S = float(os.getenv("COLLIMATOR_DB_CONNECT_MAX_DELAY_S", "300.0"))
_DB_CONNECT_MAX_TOTAL_S = float(os.getenv("COLLIMATOR_DB_CONNECT_MAX_TOTAL_S", "7200.0"))  # ~2h


def _retry_pg_connect(dsn: str, **connect_kwargs):
    """Open a psycopg connection, retrying transient OperationalErrors with
    exponential backoff + jitter until ``_DB_CONNECT_MAX_TOTAL_S`` of cumulative
    wait, then raising the last error."""
    import psycopg  # noqa: PLC0415

    deadline = time.monotonic() + _DB_CONNECT_MAX_TOTAL_S
    last_err: Exception | None = None
    attempt = 0
    while True:
        try:
            return psycopg.connect(dsn, **connect_kwargs)
        except psycopg.OperationalError as e:
            last_err = e
            attempt += 1
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            # Exponential backoff capped at _DB_CONNECT_MAX_DELAY_S, with equal
            # jitter ([base/2, base]) — keeps each wait substantial so we don't
            # spam the local replica, while still decorrelating the many training
            # workers that hit pool exhaustion in lockstep.
            base = min(_DB_CONNECT_BASE_DELAY_S * (2 ** (attempt - 1)),
                       _DB_CONNECT_MAX_DELAY_S)
            delay = min(base * random.uniform(0.5, 1.0), remaining)
            log.warning(
                "psycopg connect failed (attempt %d): %s — retrying in %.0fs "
                "(%.0fs of %.0fs budget left)",
                attempt, e, delay, remaining, _DB_CONNECT_MAX_TOTAL_S,
            )
            time.sleep(delay)
    assert last_err is not None  # loop only breaks after a failure
    raise last_err


@contextmanager
def _connect(dsn: Path | str, *, repeatable_read: bool = False):
    """Open a read-only connection to the hopper database.

    When *repeatable_read* is True the PostgreSQL connection uses
    REPEATABLE READ isolation, pinning a consistent snapshot for the
    lifetime of the connection.  This prevents concurrent hopper writes
    (new samples, label changes) from altering the row set mid-scan.
    SQLite read-only connections are already snapshot-isolated, so the
    flag is a no-op there.

    Connection establishment is retried with exponential backoff for
    transient PostgreSQL errors (OperationalError: server unreachable,
    connection refused, etc.). Once a connection is open, mid-stream
    failures propagate to the caller — they're rare but recovery would
    require resumable iteration, which we don't have today. The cycle
    will fail visibly with the row position in the log if that happens.
    """
    if _is_pg(dsn):
        try:
            import psycopg  # noqa: PLC0415, F401
        except ImportError as exc:
            raise ImportError(
                "psycopg is required for PostgreSQL: pip install psycopg[binary]",
            ) from exc
        conn = _retry_pg_connect(
            str(dsn),
            autocommit=False,
            options="-c default_transaction_isolation=repeatable\\ read" if repeatable_read else "",
        )
        try:
            yield conn
        finally:
            conn.close()
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


def _cleave_value(raw):
    """Return the raw cleave_result as-is for downstream pass-through.

    Downstream consumers (``_coerce_report``) already accept either a
    pre-parsed dict (psycopg's JSONB auto-decode) or a JSON string
    (SQLite), so re-serializing PG dicts back to strings is wasted work
    — the previous ``json.dumps(...)`` here + ``json.loads(...)`` in
    ``_coerce_report`` was a profiling-visible dict→str→dict roundtrip.
    """
    return raw


def _cleave_report(raw):
    """Return the cleave_result as a dict (or ``None`` on missing/invalid).

    Handles both psycopg's pre-parsed dict and SQLite's TEXT JSON.
    """
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
    return None


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
                        "cleave_result": _cleave_value(cr),
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
# v15 used >= 8; v16 >= 3; v17 >= 1; briefly back to >= 3, now 0 (no benign
# filter). This filter applies UNIFORMLY to good and bad, so it is the BENIGN
# floor — and a low-score benign is still benign. score=0 is where the clean
# curated corpus lives (good/foraged, good/harvest, distro packages, pypi,
# rubygems — ~2.1M benigns cleave found nothing notable in), so excluding it
# removes the easiest benigns and biases the model trigger-happy. Measured: at
# floor 1, filetypes/rtf kept 76 benigns vs ~5000 malware and collapsed to AUC
# 0.50 / 100% benign-FP; at floor 0 (449 benigns) it is perfect. Earlier floor 3
# dropped 76-100% of benigns on low-volume routes (makefile 2942->240, rtf
# 85->20) and produced 1.0-prob FPs on trivial files. The label noise that
# motivated any floor lives on the HOSTILE side — gated separately by
# EXP_MIN_MALWARE_SCORE / min_malware_training_score (train-only, malware-only).
# See [[project_score_gate_and_replay_override]] and [[project_allowlist_litmus_layout]].
_default_min = 0
try:
    MIN_SAMPLE_SCORE = int(os.getenv("COLLIMATOR_MIN_SAMPLE_SCORE", str(_default_min)))
except ValueError:
    MIN_SAMPLE_SCORE = _default_min

# Canonical predicate for a usable labeled sample. Every stage that SELECTS the
# labeled corpus — training, calibration, score-table build, specialist/OOF
# scoring, and triage — filters on this so they all agree on the universe: a
# human good/bad label, cleave actually ran, and hopper hasn't flagged the row
# (skip set = missing/replaced/corrupt/misclassified/label-mismatch/…). Stages
# append their own clauses (score >=, file_type, id <=, partition) with AND.
# Secondary by-id lookups that merely enrich already-selected rows trust that
# upstream selection and need not repeat it.
LABELED_WHERE = "label IN ('bad', 'good') AND cleave_result IS NOT NULL AND skip = ''"


def snapshot_max_id(db_path: Path | str) -> int:
    """Return max(id) of trainable samples at this moment.

    Used to pin the dataset for a single experiment / training run so that
    concurrent inserts to the hopper database don't cause drift between runs.
    Pass the returned value as ``max_id`` to ``stream_partitioned_metadata_grouped``
    or ``partition_row_ids``.
    """
    query = (
        "SELECT MAX(id) FROM samples"
        f" WHERE {LABELED_WHERE}"
        f" AND score >= {MIN_SAMPLE_SCORE}"
    )
    with _connect(db_path) as conn:
        for (max_id,) in _execute(conn, query):
            return int(max_id) if max_id is not None else 0
    return 0


_TRAINABLE_QUERY = (
    "SELECT id, sha256, path, label, canonical_sha256, cleave_result, formula, elements, score, mtime, 0 AS cluster_id"
    " FROM samples"
    f" WHERE {LABELED_WHERE}"
    f" AND score >= {MIN_SAMPLE_SCORE}"
    " ORDER BY id"
)

_METADATA_QUERY = (
    "SELECT id, sha256, label, canonical_sha256, score"
    " FROM samples"
    f" WHERE {LABELED_WHERE}"
    f" AND score >= {MIN_SAMPLE_SCORE}"
    " ORDER BY id"
)


def stream_samples(
    db_path: Path | str,
    *,
    exclude_test: bool = False,
    exclude_eval: bool = False,
    only_test: bool = False,
    only_dev: bool = False,
    exclude_oof_fold: int | None = None,
    limit: int = 0,
) -> Iterator[Sample]:
    """Yield labeled samples from a hopper database.

    Filter flags (mutually exclusive families):
      exclude_test=True       drop test rows; keep dev + train.
      exclude_eval=True       drop test AND dev rows; training-only.
      only_test=True          yield test rows only.
      only_dev=True           yield dev rows only.
      exclude_oof_fold=N      drop test rows AND drop train+dev rows whose
                              ``oof_fold_of`` equals N. Used for k=2 OOF:
                              setting it to 0 trains on fold 1 only; the
                              held-out fold 0 rows then get OOF predictions
                              from this model.
    Default yields every labeled row.
    """
    query = _TRAINABLE_QUERY
    if limit > 0:
        query += f" LIMIT {limit}"
    with _connect(db_path, repeatable_read=True) as conn:
        for row_id, sha256, path, label, canonical, cleave_result, formula, elements, score, mtime, cluster_id in _execute(conn, query):
            split_key = canonical or sha256
            partition = partition_of(split_key)
            if exclude_test and partition == "test":
                continue
            if exclude_eval and partition in ("test", "dev"):
                continue
            if only_test and partition != "test":
                continue
            if only_dev and partition != "dev":
                continue
            if exclude_oof_fold is not None:
                if partition == "test":
                    continue
                if oof_fold_of(split_key) == exclude_oof_fold:
                    continue
            report = _cleave_report(cleave_result)
            if report is None:
                if cleave_result is not None:
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
            f" WHERE {LABELED_WHERE}"
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
            report = _cleave_report(cleave_result)
            if report is None:
                if cleave_result is not None:
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
    partition: str | None = None,
) -> Iterator[tuple[int, str, str, int, int, str]]:
    """Yield labeled, non-skipped sample metadata without loading JSON reports.

    Yielded tuple: ``(row_id, sha256, path, score, label, canonical_sha256)``.

    If ``partition`` is set ("train", "dev", or "test"), only rows in that
    partition are yielded. Filtering happens in Python after the row is
    fetched (canonical_sha256 isn't indexed for byte-range queries in hopper).
    """
    with _connect(db_path, repeatable_read=True) as conn:
        params: list[Any] = []
        placeholder = "?" if isinstance(conn, sqlite3.Connection) else "%s"
        query = (
            "SELECT id, sha256, path, label, score, canonical_sha256"
            " FROM samples"
            f" WHERE {LABELED_WHERE}"
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

        for row_id, sha256, path, label, score, canonical in _execute(conn, query, params):
            split_key = canonical or sha256
            if partition is not None and partition_of(split_key) != partition:
                continue
            yield int(row_id), sha256, path or "", score or 0, _label_int(label), split_key


def stream_labeled_metadata_full_with_size(
    db_path: Path | str,
    *,
    path_substr: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    limit: int = 0,
    max_id: int = 0,
    partition: str | None = None,
) -> Iterator[tuple[int, str, str, int, int, int, str]]:
    """Yield full-corpus metadata plus serialized cleave_result byte estimate.

    Yielded tuple: ``(row_id, sha256, path, score, label, json_bytes, canonical_sha256)``.

    If ``partition`` is set, only rows from that partition are yielded.
    """
    with _connect(db_path, repeatable_read=True) as conn:
        params: list[Any] = []
        placeholder = "?" if isinstance(conn, sqlite3.Connection) else "%s"
        json_len_expr = "LENGTH(cleave_result)" if isinstance(conn, sqlite3.Connection) else "LENGTH(cleave_result::text)"
        query = (
            f"SELECT id, sha256, path, label, score, {json_len_expr}, canonical_sha256"
            " FROM samples"
            f" WHERE {LABELED_WHERE}"
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

        for row_id, sha256, path, label, score, json_bytes, canonical in _execute(conn, query, params):
            split_key = canonical or sha256
            if partition is not None and partition_of(split_key) != partition:
                continue
            yield (
                int(row_id),
                sha256,
                path or "",
                score or 0,
                _label_int(label),
                int(json_bytes or 0),
                split_key,
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
    exclude_eval: bool = False,
    only_test: bool = False,
    only_dev: bool = False,
) -> Iterator[tuple[dict[str, Any], int]]:
    """Yield (report, label) pairs. See stream_samples for filter semantics."""
    for sample in stream_samples(
        db_path,
        exclude_test=exclude_test,
        exclude_eval=exclude_eval,
        only_test=only_test,
        only_dev=only_dev,
    ):
        yield sample.report, sample.label


def partition_row_ids(
    db_path: Path | str,
    min_malware_training_score: int = 0,
    max_id: int = 0,
) -> tuple[list[int], list[tuple[int, int]], list[tuple[int, int]], list[tuple[int, int]]]:
    """Partition samples into train/dev/test by canonical_sha256.

    Returns (train_row_ids, train_ids_labels, dev_ids_labels, test_ids_labels).
    Pass ``max_id`` from ``snapshot_max_id`` to pin the dataset.

    train_row_ids feed model fitting; dev rows feed calibration and threshold
    search; test rows produce headline metrics. Disjoint by construction.
    """
    train_row_ids: list[int] = []
    train_ids_labels: list[tuple[int, int]] = []
    dev_ids_labels: list[tuple[int, int]] = []
    test_ids_labels: list[tuple[int, int]] = []
    for row_id, label, partition, _canonical, score in stream_partitioned_metadata_grouped(db_path, max_id=max_id):
        if partition == "test":
            test_ids_labels.append((row_id, label))
        elif partition == "dev":
            dev_ids_labels.append((row_id, label))
        else:
            # Heuristic pruning: ignore low-score malware during training.
            if label == 1 and score < min_malware_training_score:
                continue
            train_row_ids.append(row_id)
            train_ids_labels.append((row_id, label))
    return train_row_ids, train_ids_labels, dev_ids_labels, test_ids_labels


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
            report = _cleave_report(cleave_result)
            if report is None:
                return None
            return sha256, path or "", label, report
    return None


def stream_partitioned_metadata_grouped(
    db_path: Path | str,
    limit: int = 0,
    max_id: int = 0,
    file_types: tuple[str, ...] | None = None,
) -> Iterator[tuple[int, int, str, str, int]]:
    """Yield (row_id, label, partition, canonical_sha256, score) without loading raw JSON.

    ``partition`` is one of "train", "dev", "test". If ``max_id`` > 0, only
    rows with ``id <= max_id`` are returned. Use this with a value from
    ``snapshot_max_id`` to pin the dataset for a single run, so that
    concurrent inserts don't cause drift.
    """
    query = _METADATA_QUERY
    params: list[Any] = []
    filters: list[str] = []
    if max_id > 0:
        filters.append("id <= %s" if _is_pg(db_path) else "id <= ?")
        params.append(int(max_id))
    if file_types:
        normalized = tuple(sorted({str(ft) for ft in file_types if str(ft)}))
        if normalized:
            if _is_pg(db_path):
                filters.append("file_type = ANY(%s)")
                params.append(list(normalized))
            else:
                placeholders = ",".join("?" for _ in normalized)
                filters.append(f"file_type IN ({placeholders})")
                params.extend(normalized)
    if filters:
        # Inject extra filters before ORDER BY. _METADATA_QUERY ends with ORDER BY id.
        query = query.replace(" ORDER BY id", f" AND {' AND '.join(filters)} ORDER BY id")
    if limit > 0:
        query += f" LIMIT {limit}"
    with _connect(db_path, repeatable_read=True) as conn:
        for row_id, sha256, label, canonical, score in _execute(conn, query, params):
            split_key = canonical or sha256
            yield (
                int(row_id),
                _label_int(label),
                partition_of(split_key),
                split_key,
                score or 0,
            )


def count_labeled_by_partition_full(
    db_path: Path | str,
    *,
    max_id: int = 0,
) -> dict[str, dict[str, int]]:
    """Count all labeled, non-skipped rows by partition without score filtering.

    Returns counts under keys "train", "dev", "test", "all". Training
    intentionally focuses on rows at or above ``MIN_SAMPLE_SCORE``. FP-per-
    million reporting, however, is a corpus-level good-file rate, so it
    needs the full labeled good-file denominator, including low-score rows.
    """
    counts = {
        "train": {"good": 0, "bad": 0, "total": 0},
        "dev": {"good": 0, "bad": 0, "total": 0},
        "test": {"good": 0, "bad": 0, "total": 0},
        "all": {"good": 0, "bad": 0, "total": 0},
    }
    with _connect(db_path, repeatable_read=True) as conn:
        query = (
            "SELECT id, sha256, label, canonical_sha256"
            " FROM samples"
            f" WHERE {LABELED_WHERE}"
        )
        if max_id > 0:
            query += f" AND id <= {int(max_id)}"
        for _row_id, sha256, label, canonical in _execute(conn, query):
            split_key = canonical or sha256
            part = partition_of(split_key)
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
            f" WHERE {LABELED_WHERE}"
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
