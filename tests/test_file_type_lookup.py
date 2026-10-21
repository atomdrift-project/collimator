"""File type enrichment preserves the usable corpus without scanning unrelated IDs."""

import sqlite3

import pytest

from collimator.data import fetch_file_types


@pytest.mark.parametrize("requested_count", [3, 1_100, 250_001])
def test_file_types_filter_requested_usable_rows(tmp_path, requested_count):
    db = tmp_path / "samples.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE samples (id INTEGER PRIMARY KEY, label TEXT, "
            "cleave_result TEXT, skip TEXT, file_type TEXT)"
        )
        conn.executemany(
            "INSERT INTO samples VALUES (?, ?, ?, ?, ?)",
            [
                (1, "good", "{}", "", "elf"),
                (2, "bad", "{}", "", ""),
                (3, "bad", "{}", "", None),
                (4, "unknown", "{}", "", "pe"),
                (5, "bad", None, "", "pe"),
                (6, "bad", "{}", "missing", "pe"),
                (7, "good", "{}", "", "unrequested"),
                (1_001, "bad", "{}", "", "python"),
            ],
        )
    wanted = [1, 2, 3] + list(range(10, requested_count + 7))
    result = fetch_file_types(db, iter(wanted + [1, 4, 5, 6]))
    expected = {1: "elf", 2: "unknown", 3: "unknown"}
    if 1_001 in wanted:
        expected[1_001] = "python"
    assert result == expected


def test_empty_file_types_does_not_open_database(tmp_path):
    assert fetch_file_types(tmp_path / "absent.db", []) == {}
