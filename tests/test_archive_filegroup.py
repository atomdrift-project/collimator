"""Archive pooling must agree across experiments, training, and routing."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import azoth_calibrate_ensemble as calibrate  # noqa: E402
import azoth_specialist_suite as suite  # noqa: E402
import route_sample_counts as counts  # noqa: E402
from collimator import data  # noqa: E402
from collimator.demo import create_demo_db  # noqa: E402
from collimator.experiment import _route_file_types, sample_partitioned_reports  # noqa: E402
from collimator.filegroups import ARCHIVE_FILETYPES  # noqa: E402


def test_archive_training_and_deployment_cover_the_same_containers(monkeypatch):
    members = set(_route_file_types("filegroups/archive"))
    assert {"zip", "tar", "tar.gz", "7z", "jar", "whl", "deb", "rpm"} <= members
    assert not members.intersection(suite.RAW_COMPRESSED_FILETYPES)
    assert not {"ooxml", "ole_doc", "msi", "docx"}.intersection(members)
    assert set(suite.DEPLOYMENT_GROUPS["archive"]) == set(data.expand_filetype_aliases(tuple(members)))

    monkeypatch.setattr(suite, "_count_rows", lambda _db, *, file_types, **_kw: {
        "bad": 100, "good": 100, "total": 200,
    } if "zip" in file_types else {"bad": 0, "good": 0, "total": 0})
    monkeypatch.setattr(suite, "_eligible_filetypes", lambda *_args, **_kwargs: [])
    targets = suite._targets(SimpleNamespace(
        db="unused", max_id=0, min_bad=10, min_good=10, only=["archive"],
    ))
    assert len(targets) == 1
    assert targets[0]["kind"] == "filegroup"
    assert targets[0]["name"] == "archive"

    mapping = calibrate._filetype_to_group()
    for file_type in members:
        assert mapping[data.route_filetype(file_type)] == "archive"
    assert mapping["docx"] == "documents"
    assert all(mapping.get(ft) != "archive" for ft in suite.RAW_COMPRESSED_FILETYPES)


@pytest.mark.parametrize("old_bundle", [False, True])
def test_archive_counts_work_before_bundle_contains_group(tmp_path, old_bundle):
    if old_bundle:
        (tmp_path / "config.json").write_text(json.dumps({"filetype_to_group": {"zip": "other"}}))
    assert counts._filetypes_for_route("filegroups/archive", tmp_path) == list(
        data.expand_filetype_aliases(ARCHIVE_FILETYPES)
    )


def test_archive_pool_includes_legacy_rows_and_excludes_wrappers(tmp_path):
    db_path = tmp_path / "archives.db"
    create_demo_db(db_path, n_benign=40, n_malware=40, seed=7)
    labels = ("zip", "tar.gz", "pkg", "pythonsdist", "ociimage", "gz", "xz", "pe")
    with sqlite3.connect(db_path) as conn:
        ids = [row[0] for row in conn.execute("SELECT id FROM samples ORDER BY id")]
        conn.executemany("UPDATE samples SET file_type=? WHERE id=?", [
            (labels[i % len(labels)], rid) for i, rid in enumerate(ids)
        ])
        archive_rows = list(conn.execute(
            "SELECT id, canonical_sha256 FROM samples "
            "WHERE file_type IN ('zip','tar.gz','pkg','pythonsdist','ociimage')"
        ))
        # Screens use train+dev; the locked test partition stays reserved.
        expected = {rid for rid, sha in archive_rows if data.partition_of(sha) != "test"}
    sampled = sample_partitioned_reports(
        db_path, train_samples=0, route_file_types=_route_file_types("filegroups/archive"),
    )
    actual = {row.row_id for row in sampled.train_samples + sampled.test_samples}
    assert actual == expected
    coverage = counts._filetypes_for_route("filegroups/archive", tmp_path / "absent-bundle")
    totals = counts._count_labeled(str(db_path), coverage)
    assert totals["malware"] + totals["benign"] == len(archive_rows)
