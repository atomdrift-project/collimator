"""Load labeled samples from cyclotron's SQLite database."""

from __future__ import annotations

import json
import logging
import sqlite3
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# Terminal statuses that represent confirmed classifications.
# See cyclotron/db.go for the full status state machine.
MALWARE_STATUSES = frozenset({"bad", "good-malicious"})
BENIGN_STATUSES = frozenset({"good", "bad-benign"})
ALL_TERMINAL = MALWARE_STATUSES | BENIGN_STATUSES

# Samples whose SHA256 last byte falls in [0, TEST_BUCKET_MAX) are reserved
# for threshold evaluation and excluded from training.  13/256 ≈ 5%.
TEST_BUCKET_MAX = 13


@dataclass(frozen=True, slots=True)
class Sample:
    sha256: str
    path: str
    label: int  # 1 = malware, 0 = benign
    report: dict[str, Any]


def stream_samples(
    db_path: Path,
    *,
    exclude_test: bool = False,
    only_test: bool = False,
) -> Iterator[Sample]:
    """Yield labeled samples from the database without loading all rows."""
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    placeholders = ",".join("?" for _ in ALL_TERMINAL)
    query = (
        "SELECT sha256, path, status, cleave_json"
        f" FROM samples WHERE status IN ({placeholders})"
    )
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        for sha256, path, status, cleave_json in conn.execute(
            query, tuple(sorted(ALL_TERMINAL)),
        ):
            if not cleave_json:
                continue
            is_test = is_test_sample(sha256)
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
                sha256=sha256,
                path=path,
                label=1 if status in MALWARE_STATUSES else 0,
                report=report,
            )
    finally:
        conn.close()


def load_samples(db_path: Path) -> list[Sample]:
    """Load labeled samples from a cyclotron database.

    Terminal statuses used for training:
      - 'bad', 'good-malicious'  -> label 1 (malware)
      - 'good', 'bad-benign'    -> label 0 (benign)

    Intermediate statuses (bad-review, bad-reversed, good-review, etc.)
    are skipped to ensure clean training labels.
    """
    log.info("loading samples from %s", db_path)
    samples = list(stream_samples(db_path))

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


def split_train_test(samples: list[Sample]) -> tuple[list[Sample], list[Sample]]:
    """Split samples into train and test sets using SHA256 bucket assignment."""
    train_samples = [s for s in samples if not is_test_sample(s.sha256)]
    test_samples = [s for s in samples if is_test_sample(s.sha256)]
    n_test_malware = sum(1 for s in test_samples if s.label == 1)
    n_test_benign = len(test_samples) - n_test_malware
    log.info(
        "split: %d train, %d test (%d malware, %d benign, %.1f%%)",
        len(train_samples), len(test_samples),
        n_test_malware, n_test_benign,
        100 * len(test_samples) / max(len(samples), 1),
    )
    return train_samples, test_samples


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

    placeholders = ",".join("?" for _ in ALL_TERMINAL)
    query = (
        "SELECT sha256, status, cleave_json"
        f" FROM samples WHERE status IN ({placeholders})"
    )
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        for sha256, status, cleave_json in conn.execute(
            query, tuple(sorted(ALL_TERMINAL)),
        ):
            if not cleave_json:
                continue
            is_test = is_test_sample(sha256)
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

    placeholders = ",".join("?" for _ in ALL_TERMINAL)
    query = (
        "SELECT sha256, status, cleave_json"
        f" FROM samples WHERE status IN ({placeholders})"
    )
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        for sha256, status, cleave_json in conn.execute(
            query, tuple(sorted(ALL_TERMINAL)),
        ):
            if not cleave_json:
                continue
            yield (
                cleave_json,
                1 if status in MALWARE_STATUSES else 0,
                is_test_sample(sha256),
            )
    finally:
        conn.close()
