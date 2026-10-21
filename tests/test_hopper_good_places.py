"""The optional SQL tests use only temporary tables, rolled back on exit."""
import json
import os

import psycopg
import pytest
from psycopg.rows import dict_row

from scripts.hopper_good_places import PLAN_SQL, apply_batch, eligible, read_manifest, move_request, preserve_skip, normalize_location


def sha(n):
    return f"{n:064x}"


def test_duplicate_manifest_rejected(tmp_path):
    path = tmp_path / "manifest"
    path.write_text((json.dumps({"sha256": sha(1)}) + "\n") * 2)
    with pytest.raises(ValueError, match="Duplicate"):
        list(read_manifest(path))


def test_eligibility_deduplicates_places():
    place = {"kind": "parent", "identity": sha(1)}
    assert not eligible({"label": "bad", "places": [place, place]})
    assert not eligible({"label": "good", "places": [place, {"kind": "parent", "identity": sha(2)}]})


@pytest.fixture
def db():
    dsn = os.environ.get("GOOD_PLACES_TEST_DSN")
    if not dsn:
        pytest.skip("set GOOD_PLACES_TEST_DSN for temporary-table SQL tests")
    with psycopg.connect(dsn, row_factory=dict_row) as conn:
        conn.execute("SET LOCAL search_path=pg_temp")
        conn.execute("""CREATE TEMP TABLE samples (
            sha256 text PRIMARY KEY, label text, label_source text DEFAULT 'old',
            skip text DEFAULT 'skip-benign-archive-item', path text DEFAULT 'bad/a!!file',
            parent text DEFAULT '', file_type text DEFAULT 'go', cleave_result jsonb DEFAULT '{}',
            skipped_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now()) ON COMMIT DROP""")
        conn.execute("""CREATE TEMP TABLE sample_locations (
            id bigserial PRIMARY KEY, sha256 text, path text, parent_sha256 text DEFAULT '',
            rel text DEFAULT '', UNIQUE(sha256,path)) ON COMMIT DROP""")
        conn.execute("""CREATE TEMP TABLE label_events (
            sha256 text, from_label text, to_label text, from_skip text, to_skip text,
            reason text CHECK(reason<>'reject')) ON COMMIT DROP""")
        conn.execute("INSERT INTO samples (sha256,label) VALUES (%s,'bad'),(%s,'good'),(%s,'good')",
                     (sha(1), sha(2), sha(3)))
        yield conn
        conn.rollback()


def location(db, path, parent="", rel=""):
    db.execute("INSERT INTO sample_locations (sha256,path,parent_sha256,rel) VALUES (%s,%s,%s,%s)",
               (sha(1), path, parent, rel))


def planned(db):
    row = db.execute(PLAN_SQL, ([sha(1)],)).fetchone()
    row["eligible"] = eligible(row)
    return row


@pytest.mark.parametrize("places,expected", [
    ([("good/a!!one", sha(2), ""), ("good/a!!alias", sha(2), "")], False),
    ([("good/a!!one", sha(2), ""), ("good/b!!one", sha(3), "unpacked")], True),
    ([("good/a", "", ""), ("good/b!!one", sha(3), "")], True),
    ([("good/a", "", ""), ("good/b", "", "")], True),
    ([("good/a!!one", sha(2), "fetched"), ("good/b!!one", sha(3), "registry")], False),
    ([("good/a!!one", sha(2), ""), ("good/b!!one", sha(99), "")], False),
    ([("bad/legacy/file", sha(2), ""), ("good/b!!one", sha(3), "")], False),
    ([("bad/archive!!file", sha(2), ""), ("good/b!!one", sha(3), "")], True),
])
def test_planning_counts_independent_containment(db, places, expected):
    for path, parent, rel in places:
        location(db, path, parent, rel)
    assert planned(db)["eligible"] is expected


def two_parents(db):
    location(db, "good/a!!file", sha(2))
    location(db, "good/b!!file", sha(3))
    return planned(db)


def test_apply_preserves_skip_analysis_and_is_idempotent(db):
    old = two_parents(db)
    assert apply_batch(db, [old], "test") == {sha(1): "applied"}
    row = db.execute("SELECT * FROM samples WHERE sha256=%s", (sha(1),)).fetchone()
    assert row["label"] == "good"
    assert row["skip"] == old["skip"]
    assert row["path"] == old["path"]
    assert row["cleave_result"] == {}
    assert apply_batch(db, [old], "test") == {sha(1): "already_applied"}
    events = db.execute("SELECT * FROM label_events").fetchall()
    assert len(events) == 1
    assert events[0]["from_skip"] == events[0]["to_skip"] == old["skip"]


@pytest.mark.parametrize("mutation", [
    "UPDATE samples SET label='bad' WHERE sha256='" + sha(2) + "'",
    "DELETE FROM sample_locations WHERE parent_sha256='" + sha(2) + "'",
    "UPDATE sample_locations SET rel='fetched' WHERE parent_sha256='" + sha(2) + "'",
])
def test_changed_evidence_prevents_apply(db, mutation):
    old = two_parents(db)
    db.execute(mutation)
    assert apply_batch(db, [old], "test") == {sha(1): "lost_evidence"}
    assert not db.execute("SELECT * FROM label_events").fetchall()


def test_new_good_places_do_not_replace_original_witnesses(db):
    old = two_parents(db)
    db.execute("UPDATE samples SET label='bad' WHERE sha256=%s", (sha(2),))
    location(db, "good/new-place")
    # A fresh search qualifies, but this operation must use its saved evidence.
    assert planned(db)["eligible"]
    assert apply_batch(db, [old], "test") == {sha(1): "lost_evidence"}


@pytest.mark.parametrize("field,value", [("label", "purgatory"), ("label_source", "triage"),
                                         ("skip", "new-skip")])
def test_concurrent_change_not_overwritten(db, field, value):
    old = two_parents(db)
    db.execute(f"UPDATE samples SET {field}=%s WHERE sha256=%s", (value, sha(1)))
    assert apply_batch(db, [old], "test") == {sha(1): "changed_since_plan"}


def test_preferred_path_refresh_does_not_block_or_get_overwritten(db):
    old = two_parents(db)
    db.execute("UPDATE samples SET path='good/new-primary' WHERE sha256=%s", (sha(1),))
    assert apply_batch(db, [old], "test") == {sha(1): "applied"}
    assert db.execute("SELECT path FROM samples WHERE sha256=%s", (sha(1),)).fetchone()["path"] == "good/new-primary"


def test_failed_audit_rolls_back_label(db):
    old = two_parents(db)
    with pytest.raises(psycopg.errors.CheckViolation):
        apply_batch(db, [old], "reject")
    assert db.execute("SELECT label FROM samples WHERE sha256=%s", (sha(1),)).fetchone()["label"] == "bad"


def test_move_uses_exact_source_and_ruling():
    assert move_request(sha(1), "bad/projects/file", "test") == {"verdicts": [
        {"sha256": sha(1), "old_path": "bad/projects/file", "ruling": "good", "source": "test"}]}


def test_restore_skip_after_stale_api_cache_relabel(db):
    old = two_parents(db)
    old["skipped_at"] = db.execute("SELECT skipped_at FROM samples WHERE sha256=%s", (sha(1),)).fetchone()["skipped_at"]
    apply_batch(db, [old], "test")
    db.execute("UPDATE samples SET skip='',skipped_at=NULL WHERE sha256=%s", (sha(1),))
    assert preserve_skip(db, old, "test") == "restored"
    assert preserve_skip(db, old, "test") == "preserved"
    row = db.execute("SELECT skip,skipped_at FROM samples WHERE sha256=%s", (sha(1),)).fetchone()
    assert row == {"skip": old["skip"], "skipped_at": old["skipped_at"]}


@pytest.mark.parametrize("field,value,expected", [("label_source", "another", "label_changed"),
    ("label", "bad", "label_changed"), ("skip", "new-skip", "skip_changed")])
def test_skip_restore_does_not_overwrite_other_changes(db, field, value, expected):
    old = two_parents(db)
    apply_batch(db, [old], "test")
    db.execute(f"UPDATE samples SET {field}=%s WHERE sha256=%s", (value, sha(1)))
    assert preserve_skip(db, old, "test") == expected


def test_normalize_is_compare_and_swap(db):
    location(db, "bad/physical", sha(2))
    loc = db.execute("SELECT * FROM sample_locations").fetchone()
    assert normalize_location(db, sha(1), loc)
    assert not normalize_location(db, sha(1), loc)
    assert db.execute("SELECT parent_sha256,rel FROM sample_locations").fetchone() == {"parent_sha256": "", "rel": ""}
