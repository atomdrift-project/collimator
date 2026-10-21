"""Recovery retries only incomplete work and never revives canceled runs."""

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from autocollie_recover_pass import recovery_routes  # noqa: E402
from route_sample_counts import _count_labeled, _filetypes_for_route  # noqa: E402


def _event(kind, route="", **payload):
    return {"ts": "2026-10-20T03:00:00Z", "type": kind, "route": route, "payload": payload}


def test_recovery_keeps_successful_routes_and_reconsiders_bad_proposals_and_aliases():
    events = [
        _event("pass-start"),
        _event("screen-started", "good"), _event("screen-finished", "good"),
        _event("cycle-complete", "bad", status="parse-failed"),
        _event("spec-rejected", "rejected"),
        _event("cycle-complete", "alias", status="skipped"),
        _event("pass-complete", interrupted=False),
        _event("cycle-complete", "later", status="parse-failed"),
    ]
    assert recovery_routes(events, "2026-10-20T02", {"good", "bad", "rejected", "alias", "later"}) == ["alias", "bad", "rejected"]


@pytest.mark.parametrize("end", [[], [_event("pass-complete", interrupted=True)]])
def test_canceled_or_incomplete_pass_does_not_launch_recovery(end):
    with pytest.raises(ValueError, match="canceled"):
        recovery_routes([_event("pass-start"), *end], "2026-10-20T02", {"bad"})


@pytest.mark.parametrize("success", ["screen-finished", "screen-already-run"])
def test_successful_chain_keeps_its_own_full_train(success):
    assert recovery_routes([
        _event("pass-start"), _event("screen-started", "good"),
        _event(success, "good"), _event("spec-rejected", "good"),
        _event("pass-complete", interrupted=False),
    ], "2026-10-20T02", {"good"}) == []


def test_all_crashed_route_is_retried_but_failed_variant_with_success_is_retained():
    events = [_event("pass-start")]
    for route in ("good", "bad"):
        events.extend([_event("screen-started", route), _event("screen-crashed", route)])
    events.extend([_event("screen-finished", "good"), _event("pass-complete", interrupted=False)])
    assert recovery_routes(events, "2026-10-20T02", {"good", "bad"}) == ["bad"]


def test_route_counts_include_stored_office_aliases(tmp_path):
    db = tmp_path / "counts.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE samples (file_type TEXT, label TEXT, cleave_result TEXT, skip TEXT)")
        conn.executemany("INSERT INTO samples VALUES (?, ?, '{}', '')", [
            ("docx", "bad"), ("xlsx", "good"), ("ooxml", "bad"), ("pe", "bad"),
        ])
    members = _filetypes_for_route("filetypes/ooxml", tmp_path)
    assert {"docx", "xlsx", "ooxml"} <= set(members)
    assert _count_labeled(str(db), members) == {"malware": 2, "benign": 1}
