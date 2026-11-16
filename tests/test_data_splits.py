"""Tests for deterministic three-way splitting by split key.

Split rule:

    test:  byte < TEST_BUCKET_MAX                       (12.5%)
    dev:   TEST_BUCKET_MAX <= byte < DEV_BUCKET_MAX     (12.5%)
    train: byte >= DEV_BUCKET_MAX                       (75%)

The split key is the file's own sha256: hopper's verdict schema keeps no
canonical (archive-wide) digest, and every archive member is a sample of its
own.
"""

from __future__ import annotations

import sqlite3

from collimator.data import (
    DEV_BUCKET_MAX,
    TEST_BUCKET_MAX,
    is_dev_sample,
    is_test_sample,
    oof_fold_of,
    partition_of,
    stream_partitioned_metadata_grouped,
)
from collimator.demo import add_sample, create_demo_db, create_schema


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


def test_dev_bucket_approximately_12_percent() -> None:
    """~12.5% of SHA256 space falls in the dev bucket."""
    assert DEV_BUCKET_MAX == 64
    assert (DEV_BUCKET_MAX - TEST_BUCKET_MAX) / 256 == 0.125


def test_partitions_are_disjoint() -> None:
    """Every byte falls in exactly one of test/dev/train."""
    for last_byte in range(256):
        sha = "ff" * 31 + f"{last_byte:02x}"
        partition = partition_of(sha)
        assert partition in ("train", "dev", "test")
        # Boolean predicates agree with partition_of.
        assert is_test_sample(sha) == (partition == "test")
        assert is_dev_sample(sha) == (partition == "dev")


def test_partition_of_boundaries() -> None:
    """Boundary bytes route to expected partitions."""
    assert partition_of("ff" * 31 + "00") == "test"
    assert partition_of("ff" * 31 + "1f") == "test"
    assert partition_of("ff" * 31 + "20") == "dev"
    assert partition_of("ff" * 31 + "3f") == "dev"
    assert partition_of("ff" * 31 + "40") == "train"
    assert partition_of("ff" * 32) == "train"


def test_oof_fold_of_returns_none_for_test_rows() -> None:
    """Test partition is excluded from OOF — returns None."""
    assert oof_fold_of("ff" * 31 + "00") is None
    assert oof_fold_of("ff" * 31 + "1f") is None


def test_oof_fold_of_assigns_0_or_1_for_non_test() -> None:
    """Train and dev rows split into folds 0/1 by next-to-last byte parity."""
    # Train+dev rows. Fold determined by next-to-last byte's lowest bit.
    # Examples constructed so fold assignment is predictable:
    # Last byte = "20" → dev partition. Second-to-last byte = "00" → bit 0 of 0x00 = 0 → fold 0.
    assert oof_fold_of("ff" * 30 + "00" + "20") == 0
    # Second-to-last byte = "01" → bit 0 of 0x01 = 1 → fold 1.
    assert oof_fold_of("ff" * 30 + "01" + "20") == 1
    # Train partition with second-to-last byte = "ff" → bit 0 of 0xff = 1.
    assert oof_fold_of("00" * 30 + "ff" + "ff") == 1
    # Train partition with second-to-last byte = "fe" → bit 0 of 0xfe = 0.
    assert oof_fold_of("00" * 30 + "fe" + "ff") == 0


def test_oof_fold_balanced_across_full_byte_space() -> None:
    """The fold split is balanced (~50/50) over a uniform byte distribution."""
    folds = [
        oof_fold_of(f"ff{'00' * 29}{i:02x}{j:02x}")
        for j in range(TEST_BUCKET_MAX, 256)  # train + dev
        for i in range(256)  # second-to-last byte spans 0..255
    ]
    folds = [f for f in folds if f is not None]
    n_zeros = folds.count(0)
    n_ones = folds.count(1)
    assert n_zeros + n_ones == len(folds)
    # Exact 50/50 because 256 is even and parity is symmetric.
    assert n_zeros == n_ones


def test_own_digest_determines_partition(tmp_path) -> None:
    """Each sample splits on its own digest, archives and their members alike."""
    db_path = tmp_path / "samples.db"
    member = "11" * 32
    conn = sqlite3.connect(str(db_path))
    try:
        create_schema(conn)
        inner = add_sample(conn, sha256=member, label="bad", file_type="python", scanned=False,
                           report={"traits": [{"id": "objectives/exfil", "crit": 5}], "risk": 9})
        for outer, label in (("aa" * 32, "good"), ("bb" * 32, "bad")):
            add_sample(conn, sha256=outer, label=label, report={}, file_type="zip",
                       members=[(inner, "member-1.py")])
        conn.commit()
    finally:
        conn.close()

    rows = list(stream_partitioned_metadata_grouped(db_path))
    assert [row[3] for row in rows] == [member, "aa" * 32, "bb" * 32]
    assert all(row[2] == partition_of(row[3]) for row in rows)


def test_partitioned_metadata_labels(tmp_path) -> None:
    """stream_partitioned_metadata_grouped yields correct labels and partition tags."""
    db_path = tmp_path / "test.db"
    create_demo_db(db_path, n_benign=20, n_malware=20, seed=42)

    rows = list(stream_partitioned_metadata_grouped(db_path))
    assert len(rows) == 40

    # Every row should have (row_id, label, partition, canonical_sha256, score).
    for row_id, label, partition, canonical, score in rows:
        assert isinstance(row_id, int)
        assert label in (0, 1)
        assert partition in ("train", "dev", "test")
        assert isinstance(canonical, str)
        assert isinstance(score, int)
