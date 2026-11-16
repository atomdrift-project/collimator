"""File type enrichment preserves the usable corpus without scanning unrelated IDs."""

import sqlite3

import pytest

from collimator.data import fetch_file_types
from collimator.demo import add_sample, create_schema


@pytest.mark.parametrize("requested_count", [3, 1_100, 250_001])
def test_file_types_filter_requested_usable_rows(tmp_path, requested_count):
    db = tmp_path / "samples.db"
    with sqlite3.connect(db) as conn:
        create_schema(conn)
        for row_id, label, report, label_source, file_type in [
            (1, "good", {}, None, "elf"),
            (2, "bad", {}, None, ""),
            (3, "bad", {}, None, None),
            (4, "unknown", {}, None, "pe"),
            (5, "bad", None, None, "pe"),  # no report
            (6, "bad", {}, "conflict", "pe"),  # a good/bad conflict
            (7, "good", {}, None, "unrequested"),
            (1_001, "bad", {}, None, "python"),
        ]:
            add_sample(conn, sample_id=row_id, sha256=f"{row_id:064x}", label=label, report=report,
                       label_source=label_source, file_type=file_type or "")
    wanted = [1, 2, 3] + list(range(10, requested_count + 7))
    result = fetch_file_types(db, iter(wanted + [1, 4, 5, 6]))
    expected = {1: "elf", 2: "unknown", 3: "unknown"}
    if 1_001 in wanted:
        expected[1_001] = "python"
    assert result == expected


def test_empty_file_types_does_not_open_database(tmp_path):
    assert fetch_file_types(tmp_path / "absent.db", []) == {}
