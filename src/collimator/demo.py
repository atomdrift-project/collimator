"""Generate a tiny synthetic hopper database for local demos and tests.

The database is SQLite in the shape of hopper's verdict schema
(hopper/store/schema.sql) as collimator reads it: a samples row per file, an
atomscan verdicts row carrying the file's zstd-compressed version 8 report,
a scans row for each file scanned on its own, contents for archive
membership and locations for paths on disk. Digests are BLOBs and arrays are
JSON text; data.py reads both spellings.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

import numpy as np
import zstandard

from .data import ATOMSCAN

SCHEMA = """
CREATE TABLE samples (
    id           INTEGER PRIMARY KEY,
    sha256       BLOB    NOT NULL UNIQUE,
    size_bytes   INTEGER,
    file_type    TEXT,
    label        TEXT    NOT NULL DEFAULT 'unknown',
    label_source TEXT,
    created_at   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE TABLE verdicts (
    sample_id  INTEGER NOT NULL REFERENCES samples,
    formed_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    outcome    TEXT    NOT NULL,
    class      TEXT,
    scanner_id INTEGER NOT NULL,
    fires_at   INTEGER,
    ruleset    TEXT    NOT NULL DEFAULT '',
    digest     BLOB,
    summary    TEXT,
    detail     BLOB,
    PRIMARY KEY (sample_id, scanner_id)
);
CREATE TABLE scans (
    sample_id  INTEGER PRIMARY KEY REFERENCES samples,
    scanned_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    ruleset    TEXT    NOT NULL DEFAULT '',
    engine     TEXT    NOT NULL DEFAULT '',
    flagged    INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE contents (
    parent_id INTEGER PRIMARY KEY REFERENCES samples,
    listed_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    child_ids TEXT    NOT NULL,
    paths     TEXT    NOT NULL
);
CREATE TABLE locations (
    path      TEXT    PRIMARY KEY,
    sample_id INTEGER NOT NULL REFERENCES samples,
    source    TEXT,
    feed      TEXT,
    mtime     TEXT,
    seen_at   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
CREATE INDEX locations_sample ON locations (sample_id);
"""


def create_schema(conn: sqlite3.Connection) -> None:
    """Create hopper's verdict tables, as collimator reads them."""
    conn.executescript(SCHEMA)


def compress_report(report: dict[str, Any]) -> bytes:
    """A report as hopper stores it: compact JSON, zstd-compressed."""
    return zstandard.ZstdCompressor().compress(json.dumps(report, sort_keys=True).encode())


def add_sample(
    conn: sqlite3.Connection,
    *,
    sha256: str,
    label: str = "good",
    report: dict[str, Any] | bytes | None = None,
    file_type: str = "",
    size: int = 0,
    label_source: str | None = None,
    sample_id: int | None = None,
    outcome: str | None = "ok",
    scanned: bool = True,
    members: Sequence[tuple[int, str]] = (),
    path: str | None = None,
    mtime: str | None = None,
) -> int:
    """Insert one file and return its id.

    ``report`` is the file's version 8 report (a dict), raw stored bytes, or
    None for a verdict without one; ``outcome`` None leaves the file with no
    atomscan verdict at all. ``scanned`` False makes it a member that was never
    scanned on its own. ``members`` lists (child id, path) as contents does.
    ``path`` and ``mtime`` give it a location.
    """
    cur = conn.execute(
        "INSERT INTO samples (id, sha256, size_bytes, file_type, label, label_source)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (sample_id, bytes.fromhex(sha256), size or None, file_type or None, label, label_source),
    )
    row_id = int(cur.lastrowid or 0)
    if outcome is not None:
        detail = compress_report(report) if isinstance(report, dict) else report
        digest = hashlib.sha256(detail).digest() if detail is not None else None
        conn.execute(
            "INSERT INTO verdicts (sample_id, outcome, scanner_id, digest, detail)"
            " VALUES (?, ?, ?, ?, ?)",
            (row_id, outcome, ATOMSCAN, digest, detail),
        )
    if scanned:
        conn.execute("INSERT INTO scans (sample_id) VALUES (?)", (row_id,))
    if members:
        conn.execute(
            "INSERT INTO contents (parent_id, child_ids, paths) VALUES (?, ?, ?)",
            (row_id, json.dumps([c for c, _ in members]), json.dumps([p for _, p in members])),
        )
    if path is not None:
        conn.execute(
            "INSERT INTO locations (path, sample_id, mtime) VALUES (?, ?, ?)",
            (path, row_id, mtime),
        )
    return row_id


def set_report(conn: sqlite3.Connection, sample_id: int, report: Any) -> None:
    """Replace a file's atomscan report, as a rescan that found otherwise would."""
    detail = zstandard.ZstdCompressor().compress(json.dumps(report, sort_keys=True).encode())
    conn.execute(
        "UPDATE verdicts SET detail = ?, digest = ? WHERE sample_id = ? AND scanner_id = ?",
        (detail, hashlib.sha256(detail).digest(), sample_id, ATOMSCAN),
    )


# Writing cleave's multi-file reports as hopper stores them. A caller that
# holds a report as collimator trains on it (cleave's ``files``/``fs`` list:
# a test, a frozen capture) stores it per file: the first entry becomes the
# sample's own version 8 report, every other entry a member sample listed in
# contents. data.fetch_cleave_results rebuilds the list from them.

# What a version 8 report never carries (v7result's placement keys, plus the
# version 4 to 6 spellings of parent, depth and size).
_PLACEMENT = {
    "id", "pid", "p", "depth", "dp", "path", "rel", "via", "role", "sha", "size", "sz",
    "type", "ident", "idn",
}


def _own(entry: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in entry.items() if k not in _PLACEMENT}


def add_report(
    conn: sqlite3.Connection,
    row_id: int,
    report: dict[str, Any] | str | None,
    *,
    label: str = "good",
    score: int | None = None,
    formula: str | None = None,
    sha256: str | None = None,
    **sample: Any,
) -> int:
    """Store ``report`` as sample ``row_id`` and return its id.

    ``report`` may be a dict in cleave's multi-file shape, raw JSON text, or
    None (an ok verdict without a report). Its n-th member becomes sample
    ``10**6 * row_id + n``. ``score`` sets the root's risk and ``formula`` its
    molecule, which hopper keeps inside the report. Other keywords go to
    add_sample for the root.
    """
    sha = sha256 or f"{row_id:064x}"
    if not isinstance(report, dict):
        detail = None if report is None else zstandard.ZstdCompressor().compress(report.encode())
        return add_sample(conn, sample_id=row_id, sha256=sha, label=label, report=detail, **sample)
    listed = report.get("files") or report.get("fs") or []
    entries = [e for e in listed if isinstance(e, dict)] or [{}]
    root, members = entries[0], entries[1:]
    by_id: dict[Any, int] = {}
    children: dict[int, list[tuple[int, str]]] = {}
    member_ids = []
    for index, entry in enumerate(members, 1):
        member_id = 10**6 * row_id + index
        member_ids.append(member_id)
        if entry.get("id") is not None:
            by_id[entry["id"]] = member_id
    for member_id, entry in zip(member_ids, members, strict=True):
        parent = by_id.get(entry.get("pid"), row_id)
        rel = str(entry.get("path") or f"member-{member_id}").rsplit("!!", 1)[-1]
        children.setdefault(parent, []).append((member_id, rel))
    for member_id, entry in zip(member_ids, members, strict=True):
        add_sample(
            conn, sample_id=member_id, sha256=f"{member_id:064x}", label="unknown",
            report=_own(entry), file_type=str(entry.get("type") or ""),
            size=int(entry.get("size") or entry.get("sz") or 0), scanned=False,
            members=children.get(member_id, ()),
        )
    own = _own(root)
    if score is not None:
        own["risk"] = score
    if formula is not None:
        own["mol"] = formula
    sample.setdefault("file_type", str(root.get("type") or ""))
    sample.setdefault("size", int(root.get("size") or root.get("sz") or 0))
    return add_sample(
        conn, sample_id=row_id, sha256=sha, label=label, report=own,
        members=children.get(row_id, ()), **sample,
    )


def write_reports(path: Path, rows: Iterable[dict[str, Any]]) -> Path:
    """Create a verdict-schema DB at ``path`` holding each row's report.

    Each row is ``add_report``'s keyword arguments, with ``id`` and ``report``.
    """
    with sqlite3.connect(path) as conn:
        create_schema(conn)
        for row in rows:
            row = dict(row)
            add_report(conn, row.pop("id"), row.pop("report"), **row)
    return path


def _hex_sha(rng: np.random.Generator) -> str:
    return "".join(rng.choice(list("0123456789abcdef"), size=64))


def _make_report(rng: np.random.Generator, *, malware: bool) -> tuple[dict[str, Any], int]:
    """A synthetic report and the file's size, drawn in a fixed order per seed."""
    findings: list[dict[str, object]] = []
    if malware:
        findings.extend([
            {"id": "objectives/evasion/process", "crit": "hostile", "conf": 0.98},
            {"id": "well-known/cobalt", "crit": "hostile", "conf": 0.95},
            {"id": "third_party/yara_match", "crit": "hostile", "conf": 0.99},
        ])
        function_count = int(rng.integers(80, 180))
        entropy = float(rng.uniform(7.0, 7.9))
    else:
        findings.extend([
            {"id": "metadata/format::common", "crit": "baseline", "conf": 0.95},
            {"id": "third_party/packer_match", "crit": "baseline", "conf": 0.80},
        ])
        function_count = int(rng.integers(5, 40))
        entropy = float(rng.uniform(4.5, 6.3))
    size = int(rng.integers(40_000, 300_000))
    report = {
        "risk": 10,
        "findings": findings,
        "imports": [] if malware else [{"name": "printf"}],
        "strings": [],
        "sections": [],
        "metrics": {
            "binary": {
                "overall_entropy": entropy,
                "function_count": function_count,
                "code_to_data_ratio": float(rng.uniform(0.7, 2.5)),
            },
            "text": {
                "char_entropy": float(rng.uniform(3.0, 5.5)),
                "total_lines": int(rng.integers(50, 600)),
            },
        },
    }
    return report, size


def create_demo_db(
    output_path: Path,
    *,
    n_benign: int = 64,
    n_malware: int = 64,
    seed: int = 42,
) -> None:
    """Create a synthetic hopper verdict-schema SQLite database for demos/tests."""
    rng = np.random.default_rng(seed)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.unlink(missing_ok=True)

    conn = sqlite3.connect(str(output_path))
    try:
        create_schema(conn)
        for malware in [False] * n_benign + [True] * n_malware:
            sha = _hex_sha(rng)
            report, size = _make_report(rng, malware=malware)
            add_sample(
                conn,
                sha256=sha,
                label="bad" if malware else "good",
                report=report,
                size=size,
                path=f"/demo/{sha[:12]}.bin",
            )
        conn.commit()
    finally:
        conn.close()
