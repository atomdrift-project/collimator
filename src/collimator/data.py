"""Load labeled samples from hopper's verdict schema (PostgreSQL or SQLite).

hopper (store/schema.sql) keeps one ``samples`` row per file, archive members
included; one ``verdicts`` row per file per scanner; archive membership in
``contents``; and where files sit on disk in ``locations``. Collimator only
reads it: every connection is read-only and names the schema it reads
(``HOPPER_SCHEMA``, default ``verdict``). What each training input is read
from:

  label        samples.label: 'good' / 'bad'. (Legacy 'purgatory' is
               'inconclusive' now; neither trains.)
  file_type    samples.file_type.
  report       atomscan's verdict (scanner 1): verdicts.detail is the file's
               own version 8 report, zstd-compressed. The report a file trains
               on is rebuilt from it and from the reports of every file
               ``contents`` lists beneath it, as the scan that produced them
               saw the archive (see ``fetch_cleave_results``).
  formula      the report's ``mol``; elements is the formula without its
               subscript digits (legacy samples.formula / elements).
  score        the report's ``risk`` (legacy samples.score was files[0].risk).
  path, mtime  the file's newest ``locations`` row (by seen_at). Archive
               members have none: their place is in their archive's contents.

A usable labeled sample (``LABELED_WHERE``) is labeled good or bad, has an ok
atomscan verdict with a report, and is not a good/bad conflict
(label_source 'conflict', legacy skip 'conflict'). Two exclusions concern
archive members never scanned on their own (no ``scans`` row), whose label
they inherited from an archive; no column says them, so they are applied in
Python, reading each member's report:

- its report is a stub, a molecule and a risk alone (``_molecule_only``);
- it is labeled bad and its own findings do not convict it (one at crit 5,
  or two at crit 4): legacy hopper's skip-benign-archive-item
  (``_benign_archive_item``).

Splitting is deterministic. hopper's verdict schema keeps no canonical
(archive-wide) digest, so the split key is the file's own sha256, still
exposed as ``canonical_sha256`` so callers and caches keep their shape.
Three-way partition by the split key's last byte:

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

import hashlib
import itertools
import json
import logging
import os
import random
import re
import sqlite3
import time
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple

import zstandard

from .profiling import timed

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


# Historical / variant filetype spellings → the canonical label filefacts now
# emits (`filefacts::FileType::label`). hopper's `file_type` column is derived
# from each report's stored cleave JSON, so the catalog holds a MIX: rows
# analyzed before the nomenclature unification carry the old spellings
# (hyphenated `python-bytecode`, abbreviated `objc`, or Debug-mangled
# `pythonsdist`/`cargolock` where cleave's old fallback dropped underscores),
# while rows analyzed since carry the canonical label. Canonicalizing at read
# time lets old and new samples train under ONE vocabulary without rewriting
# the corpus.
#
# This map is the deploy-side mirror of filefacts' label scheme — keep it in
# sync with `filefacts::FileType::label` (only entries whose stored spelling
# differs from the canonical label need listing). Office subtypes collapse onto
# the container type because filefacts identifies the container, not the
# member: `.docx`/`.xlsx`/`.pptx` are all `ooxml`, `.doc`/`.xls`/`.ppt` all
# `ole_doc`.
_FILETYPE_ALIASES: dict[str, tuple[str, ...]] = {
    "objective_c": ("objc", "objectivec"),
    "github_actions": ("github-actions", "githubactions"),
    "systemd_service": ("systemd",),
    "desktop_entry": ("desktop-entry",),
    "python_bytecode": ("python-bytecode", "pyc"),
    "pkg_info": ("pkg-info", "pkginfo"),
    "src_info": ("srcinfo",),
    "vbs": ("vbscript",),
    "jpeg": ("jpg",),
    "java_class": ("javaclass",),
    "python_sdist": ("pythonsdist",),
    "oci_image": ("ociimage",),
    "gentoo_binpkg": ("gentoobinpkg",),
    "vsix_manifest": ("vsixmanifest",),
    "chrome_manifest": ("chromemanifest", "chrome-manifest"),
    "package.json": ("packagejson",),
    "composer.json": ("composerjson",),
    "composer.lock": ("composerlock",),
    "cargo.lock": ("cargolock",),
    "poetry.lock": ("poetrylock",),
    "pipfile.lock": ("pipfilelock",),
    "gemfile.lock": ("gemfilelock",),
    "yarn.lock": ("yarnlock",),
    "pnpm-lock.yaml": ("pnpmlock", "pnpm-lock", "pnpm.lock"),
    "requirements.txt": ("requirementstxt",),
    "go.sum": ("gosum",),
    "go.mod": ("gomod",),
    # Office formats — filefacts identifies the OPC/OLE container, not the
    # member, so every Word/Excel/PowerPoint subtype (including macro-enabled
    # and template variants) collapses onto its container. MSI is OLE2 too,
    # but filefacts reports it as its own `msi` type in the archives group.
    "ole_doc": ("oledoc", "ole", "doc", "xls", "ppt", "msg"),
    "ooxml": (
        "docx", "xlsx", "pptx",
        "xlsm", "xltx", "xltm", "xlsb", "xlam",
        "pptm", "ppsm", "potm", "potx", "ppam", "sldm", "sldx",
        "docm", "dotx",
    ),
    # Legacy / foreign labels folded to the nearest filefacts type so old rows
    # join the matching cohort instead of orphaning: HTA is HTML-based, MSIX is
    # a ZIP application package, bare `.dat` is opaque data. Bare `pkg` is the
    # macOS XAR installer — every such row in the catalog is a `.pkg` from a
    # macOS software domain (adoptium/go.dev/nodejs.org/github releases), with
    # no Arch `.pkg.tar.*` or FreeBSD-repo signal, so it disambiguates to macOS.
    "html": ("hta",),
    "zip": ("msix",),
    "data": ("dat",),
    "pkg_macos": ("pkg",),
    # Labels older cleave stored that filefacts now reports differently:
    # `.war`/`.ear` are JARs, bare `apk` is Android, `.tgz` is a gzip TAR
    # (routed as `tar`), C++ is `c`, and TOML/INI are text by extension.
    "jar": ("war", "ear"),
    "apk_android": ("apk",),
    "tar": ("tgz",),
    "c": ("cpp",),
    "yaml": ("yml",),
    "text": ("ini", "toml"),
}

# Reverse index built once: every alias → its canonical label.
_ALIAS_TO_CANONICAL: dict[str, str] = {
    alias: canonical
    for canonical, aliases in _FILETYPE_ALIASES.items()
    for alias in aliases
}


def canonicalize_filetype(file_type: str | None) -> str:
    """Map any historical filetype spelling onto its canonical filefacts label.

    `objc` → `objective_c`, `python-bytecode` → `python_bytecode`,
    `pythonsdist` → `python_sdist`, `docx` → `ooxml`. Canonical labels and
    unknown strings pass through unchanged (the function is idempotent), so it
    is safe to apply to every sample regardless of when it was analyzed.
    Lowercases and trims as a side-effect, matching `normalize_archive_filetype`.
    """
    if file_type is None:
        return ""
    normalized = str(file_type).strip().lower()
    return _ALIAS_TO_CANONICAL.get(normalized, normalized)


def expand_filetype_aliases(file_types: tuple[str, ...]) -> tuple[str, ...]:
    """Expand canonical route labels to every spelling that may sit in the DB.

    A route asks for canonical names (`objective_c`, `ole_doc`); the catalog
    still holds old rows under `objc`/`oledoc`/`doc`/…. This returns the
    canonical label plus all its known aliases so an index-backed
    `file_type IN (...)` filter matches both old and new rows. Inputs are
    canonicalized first, so passing an old label (`objc`) also works.
    """
    out: set[str] = set()
    for ft in file_types:
        canonical = canonicalize_filetype(ft)
        if not canonical:
            continue
        out.add(canonical)
        out.update(_FILETYPE_ALIASES.get(canonical, ()))
    return tuple(sorted(out))


def route_filetype(file_type: str | None) -> str:
    """The canonical route label for a stored `file_type`.

    Composes the two normalizations in the order the publish path needs:
    first strip compression suffixes onto the container
    ([`normalize_archive_filetype`]: `tar.gz` → `tar`), then fold the
    historical spelling onto the filefacts label
    ([`canonicalize_filetype`]: `python-bytecode` → `python_bytecode`,
    `xlsx` → `ooxml`). The result is exactly the label `scan` receives from
    filefacts at runtime, so a route named by this function is reachable by
    scan's exact-match lookup.

    Use this everywhere a route/specialist NAME is derived from a stored
    file_type (score table, specialist discovery, route summaries). Old and
    new spellings of one type collapse to a single route, so its specialist
    trains on the union instead of fragmenting across duplicate routes.
    `normalize_archive_filetype` alone is NOT enough — it leaves spellings
    untouched — and must stay the pure compression rule it is (scan mirrors
    it verbatim in model.rs).
    """
    return canonicalize_filetype(normalize_archive_filetype(file_type))


def expand_route_filetypes(file_types: tuple[str, ...]) -> tuple[str, ...]:
    """Stored spellings covered by canonical runtime specialist routes.

    A training summary may list only high-count aliases. Scoring still needs
    every alias that runtime maps to that specialist, including compressed TAR.
    """
    from .filegroups import FILE_GROUPS

    canonical = {route_filetype(ft) for ft in file_types} - {""}
    variants = set(file_types) | set(expand_filetype_aliases(tuple(canonical)))
    variants.update(ft for ft in FILE_GROUPS["archives"] if route_filetype(ft) in canonical)
    return tuple(sorted(variants - {""}))



log = logging.getLogger(__name__)

# Split-key last-byte ranges. test < TEST_BUCKET_MAX, dev in
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
    """Return 'train', 'dev', or 'test' for a given split key."""
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

# The schema holding hopper's verdict tables. hopper migrated production from
# the legacy tables in `public` on 2026-11-15; the legacy tables are frozen.
HOPPER_SCHEMA = os.environ.get("HOPPER_SCHEMA", "verdict")
if not re.fullmatch(r"[a-z_][a-z0-9_]*", HOPPER_SCHEMA):
    raise ValueError(f"HOPPER_SCHEMA must be a plain lowercase schema name, not {HOPPER_SCHEMA!r}")
APPLICATION_NAME = "collimator"

# scanners.id of atomscan, whose verdict row carries the file's report.
ATOMSCAN = 1

# hopper's limits on what it walks and stores: a report line (scanresult.MaxLine)
# and how deep a contents walk goes (store.maxMemberDepth). An archive's report
# lists at most MAX_REPORT_FILES files, the most a legacy stored report listed.
MAX_REPORT_BYTES = 64 << 20
MAX_REPORT_DEPTH = 16
MAX_REPORT_FILES = 20_000

# Ids per lookup: SQLite's bound-parameter limit, or one PostgreSQL array.
_SQLITE_CHUNK = 500
_PG_CHUNK = 5000


def _is_pg(dsn: Path | str) -> bool:
    s = str(dsn)
    return s.startswith(("postgres://", "postgresql://"))


def _pg_conn(conn: Any) -> bool:
    return not isinstance(conn, sqlite3.Connection)


def _marker(conn: Any) -> str:
    return "%s" if _pg_conn(conn) else "?"


def _in(conn: Any, column: str, values: list[Any]) -> tuple[str, list[Any]]:
    """`column` is one of `values`: an array parameter, or SQLite's list."""
    if _pg_conn(conn):
        return f"{column} = ANY(%s)", [list(values)]
    return f"{column} IN ({','.join('?' * len(values))})", list(values)


def _chunks(items: Iterable[Any], size: int) -> Iterator[list[Any]]:
    it = iter(items)
    while chunk := list(itertools.islice(it, size)):
        yield chunk


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


def _retry_pg_connect(dsn: str, **connect_kwargs: Any) -> Any:
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


def _require_schema(conn: Any) -> None:
    """Fail fast when the connection does not see hopper's verdict tables."""
    if _pg_conn(conn):
        row = conn.execute(
            "SELECT to_regclass('samples') IS NOT NULL AND to_regclass('verdicts') IS NOT NULL"
        ).fetchone()
        ok = bool(row and row[0])
    else:
        query = "SELECT name FROM sqlite_master WHERE type = 'table'"
        tables = {name for (name,) in conn.execute(query)}
        ok = {"samples", "verdicts"} <= tables
    if not ok:
        raise RuntimeError(
            f"hopper schema {HOPPER_SCHEMA!r} has no samples and verdicts tables: "
            "set HOPPER_SCHEMA to the schema holding hopper's verdict tables"
        )


@contextmanager
def _connect(dsn: Path | str, *, repeatable_read: bool = False) -> Iterator[Any]:
    """Open a read-only connection to hopper's verdict schema.

    PostgreSQL sessions are read-only (default_transaction_read_only), read
    HOPPER_SCHEMA alone (search_path), report times in UTC, and name
    themselves to the server (application_name). When *repeatable_read* is
    True the connection uses REPEATABLE READ isolation, pinning a consistent
    snapshot for its lifetime, so concurrent hopper writes (new samples, label
    changes) cannot alter the row set mid-scan. SQLite read-only connections
    are already snapshot-isolated, so the flag is a no-op there.

    A COLLIMATOR_PG_SNAPSHOT supplied by the research-pass owner is imported
    before any reads, including on worker connections. All such connections
    are read-only and use the same view while ingestion continues.

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
        # libpq `options` is space-separated, so a literal space inside a value
        # has to be backslash-escaped (hence "repeatable\\ read").
        opts = [
            f"-c search_path={HOPPER_SCHEMA}",
            "-c default_transaction_read_only=on",
            "-c timezone=UTC",
            f"-c max_parallel_workers_per_gather={PG_PARALLEL_WORKERS}",
        ]
        snapshot = os.environ.get("COLLIMATOR_PG_SNAPSHOT", "")
        if snapshot and os.environ.get("COLLIMATOR_PG_SNAPSHOT_DATABASE") != str(dsn):
            raise ValueError("corpus snapshot belongs to a different database")
        if repeatable_read or snapshot:
            opts.append("-c default_transaction_isolation=repeatable\\ read")
        conn = _retry_pg_connect(
            str(dsn),
            autocommit=False,
            options=" ".join(opts),
            application_name=APPLICATION_NAME,
        )
        try:
            if snapshot:
                from psycopg import sql
                conn.execute(sql.SQL("SET TRANSACTION SNAPSHOT {}").format(sql.Literal(snapshot)))
            _require_schema(conn)
            yield conn
        finally:
            conn.close()
    else:
        db_path = Path(str(dsn))
        if not db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        # PostgreSQL's md5() and encode(bytea, 'hex'), so one statement serves both.
        conn.create_function("md5", 1, lambda value: hashlib.md5(value.encode()).hexdigest(),
                             deterministic=True)
        conn.create_function("encode", 2, lambda value, _format: bytes(value).hex(),
                             deterministic=True)
        try:
            _require_schema(conn)
            if repeatable_read:
                conn.execute("BEGIN")
            yield conn
        finally:
            conn.close()


def _execute(conn: Any, query: str, params: Any = None) -> Iterator[Any]:
    """Execute a query, adapting for sqlite3 vs psycopg cursor styles."""
    if isinstance(conn, sqlite3.Connection):
        yield from conn.execute(query, params or [])
    else:
        with conn.cursor() as cur:
            cur.execute(query, params)
            yield from cur


_cursor_names = itertools.count()


def _stream(conn: Any, query: str, params: Any = None) -> Iterator[Any]:
    """Execute a query whose result is a corpus pass, holding a batch at a time.

    PostgreSQL gets a server-side cursor: a client-side one would buffer every
    row (bad rows carry their reports) before yielding the first.
    """
    if isinstance(conn, sqlite3.Connection):
        yield from conn.execute(query, params or [])
        return
    with conn.cursor(name=f"collimator_{next(_cursor_names)}") as cur:
        cur.itersize = 20_000
        cur.execute(query, params)
        yield from cur


def _array(value: Any) -> list[Any]:
    """A PostgreSQL array as psycopg returns it, or SQLite's JSON text."""
    if isinstance(value, str):
        return list(json.loads(value))
    return list(value or ())


# ---------------------------------------------------------------------------
# Reports: atomscan's zstd-compressed version 8 report of each file. hopper
# compresses them itself, without a dictionary (store.New), so a plain zstd
# frame decoder reads them.
# ---------------------------------------------------------------------------

_decompressor: zstandard.ZstdDecompressor | None = None


def decode_report(detail: bytes | memoryview | None) -> dict[str, Any] | None:
    """A stored report as a dict; None when absent, undecodable or not an object."""
    global _decompressor
    if detail is None:
        return None
    if _decompressor is None:
        _decompressor = zstandard.ZstdDecompressor()
    try:
        raw = _decompressor.decompress(bytes(detail), max_output_size=MAX_REPORT_BYTES)
        report = json.loads(raw)
    except (zstandard.ZstdError, ValueError):
        return None
    return report if isinstance(report, dict) else None


def _findings(report: dict[str, Any]) -> list[Any]:
    """A report's findings: v8 `traits`, or `find` in a v7 report hopper kept as written."""
    findings = report.get("traits") or report.get("find") or []
    return findings if isinstance(findings, list) else []


def _crit(finding: Any) -> int:
    if not isinstance(finding, dict):
        return 0
    try:
        return int(finding.get("crit") or 0)
    except (TypeError, ValueError):
        return 0


def _benign_archive_item(report: dict[str, Any]) -> bool:
    """legacy hopper's skip-benign-archive-item rule, for a bad archive member.

    A member inherited its archive's bad label; unless its own findings
    convict it (one at crit 5, or two at crit 4 or above) it is filler, and
    legacy kept it out of training (hopper.go memberSamplesFromEnvelope).
    """
    crits = [_crit(f) for f in _findings(report)]
    return max(crits, default=0) < 5 and sum(c >= 4 for c in crits) <= 1


def _molecule_only(report: dict[str, Any]) -> bool:
    """A report that says no more than a molecule and a risk (hopper's FillReports test).

    It is all an archive's report kept of a member once legacy hopper cut
    member entries out of archive reports (2026-06-18), not an analysis of
    the file. hopper's migration filled such members from their legacy
    excerpts only for rows that were never members (legacy parent = ''), so
    the members legacy trained on mostly kept a stub.
    """
    return report.keys() <= {"mol", "risk", "f", "x"}


def _risk(report: dict[str, Any]) -> int:
    """The report's risk: legacy samples.score.

    Versions 4 to 6 spell it ``x`` (legacy score equalled it on every one of
    43,205 frozen rows), as they spell the molecule ``f``.
    """
    try:
        return int(report.get("risk") or report.get("x") or 0)
    except (TypeError, ValueError):
        return 0


def _molecule(report: dict[str, Any]) -> str:
    """The report's molecule, legacy samples.formula: ``mol``, or ``f`` before version 7."""
    formula = report.get("mol", report.get("f"))
    return formula if isinstance(formula, str) else ""


_SUBSCRIPTS = str.maketrans("", "", "₀₁₂₃₄₅₆₇₈₉")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# Minimum report risk for a sample to be considered trainable.
# Controls the default floor of stream_partitioned_metadata_grouped and
# stream_samples (screens stream with min_score=None and apply this floor to
# TRAIN rows only — see experiment.sample_partitioned_reports: an eval-side
# floor changes the benign denominator and can flip the 25k operating-point
# regime, which is a measurement artifact, not a model change).
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
# A floor above 0 makes every corpus pass read every report (risk lives inside
# it), so it is much slower than the malware gate, which reads bad rows only.
_default_min = 0
try:
    MIN_SAMPLE_SCORE = int(os.getenv("COLLIMATOR_MIN_SAMPLE_SCORE", str(_default_min)))
except ValueError:
    MIN_SAMPLE_SCORE = _default_min

# Corpus scans share storage with the logical-replication apply workers.
# Keep parallel query workers opt-in so concurrent experiments do not undo
# the replica's hopper-role limit. Dedicated training databases can opt in
# with COLLIMATOR_PG_PARALLEL_WORKERS=2 (or another explicit worker count).
_default_parallel = 0
try:
    PG_PARALLEL_WORKERS = max(
        0, int(os.getenv("COLLIMATOR_PG_PARALLEL_WORKERS", str(_default_parallel)))
    )
except ValueError:
    PG_PARALLEL_WORKERS = _default_parallel


def sample_predicate(percent: str) -> str:
    """Repeatable digest sample, independent of suffix-based splits.

    The split key's trailing bytes pick the partition, so the cohort rehashes
    the digest and keeps rows whose leading 32 bits fall under the cutoff.
    The predicate is SQL over ``samples s`` that runs on PostgreSQL and on
    SQLite (``_connect`` gives SQLite md5 and encode).
    """
    from decimal import Decimal, InvalidOperation

    try:
        fraction = Decimal(percent) / 100
    except InvalidOperation as exc:
        raise ValueError("sample percent must be greater than 0 and at most 100") from exc
    if not fraction.is_finite() or not 0 < fraction <= 1:
        raise ValueError("sample percent must be greater than 0 and at most 100")
    if fraction == 1:
        return ""
    cutoff = int(fraction * (1 << 32))
    if not cutoff:
        raise ValueError("sample percent is too small for a 32-bit hash sample")
    return f"substr(md5(encode(s.sha256, 'hex')), 1, 8) < '{cutoff:08x}'"


SAMPLE_PERCENT = os.environ.get("COLLIMATOR_SAMPLE_PERCENT", "100")
SAMPLE_PREDICATE = sample_predicate(SAMPLE_PERCENT)

# Canonical predicate for a usable labeled sample. Every stage that SELECTS the
# labeled corpus — training, calibration, score-table build, specialist/OOF
# scoring, and triage — reads it through stream_corpus (or the wrappers below)
# so they all agree on the universe: a human good/bad label that is not a
# good/bad conflict, and an ok atomscan verdict with a report. stream_corpus
# also drops bad archive members that are filler (_benign_archive_item), which
# no column says. Secondary by-id lookups that merely enrich already-selected
# rows trust that upstream selection and need not repeat it.
CORPUS_FROM = (
    "samples s"
    f" JOIN verdicts v ON v.sample_id = s.id AND v.scanner_id = {ATOMSCAN}"
    " LEFT JOIN scans sc ON sc.sample_id = s.id"
)
LABELED_WHERE = (
    "s.label IN ('bad', 'good') AND v.outcome = 'ok' AND v.detail IS NOT NULL"
    " AND COALESCE(s.label_source, '') <> 'conflict'"
)
if SAMPLE_PREDICATE:
    LABELED_WHERE += f" AND ({SAMPLE_PREDICATE})"

# The newest place a file is held on disk, as hopper's prism shows it
# (store.newestLocation); locations_sample serves it.
_NEWEST_PATH = (
    "(SELECT l.path FROM locations l WHERE l.sample_id = s.id"
    " ORDER BY l.seen_at DESC, l.path LIMIT 1)"
)


class CorpusRow(NamedTuple):
    """One usable labeled sample, as a corpus pass yields it."""

    row_id: int
    sha256: str
    label: int  # 1 = malware, 0 = benign
    file_type: str  # 'unknown' when hopper has none
    score: int  # the report's risk, where the pass read it (see stream_corpus)
    path: str  # newest location; '' when not asked for, or for a member
    report_bytes: int  # compressed size of the file's own report

    @property
    def canonical_sha256(self) -> str:
        """The split key: the file's own digest (see the module docstring)."""
        return self.sha256

    @property
    def partition(self) -> str:
        return partition_of(self.sha256)


def _corpus(
    conn: Any,
    *,
    max_id: int = 0,
    file_types: tuple[str, ...] | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    scores: str = "bad",
    path_substr: str | None = None,
    with_path: bool = False,
    limit: int = 0,
    percent: str | None = None,
    ordered: bool = True,
) -> Iterator[CorpusRow]:
    """Yield the usable labeled samples in id order (see stream_corpus)."""
    mark = _marker(conn)
    where = [LABELED_WHERE]
    params: list[Any] = []
    if percent and (cohort := sample_predicate(percent)):
        where.append(f"({cohort})")
    if max_id > 0:
        where.append(f"s.id <= {mark}")
        params.append(int(max_id))
    if file_types:
        # Expand canonical route labels to every stored spelling (old + new),
        # so the filter still matches rows analyzed before the filetype
        # nomenclature was unified.
        stored = expand_filetype_aliases(tuple(str(ft) for ft in file_types if str(ft)))
        if stored:
            clause, values = _in(conn, "s.file_type", list(stored))
            where.append(clause)
            params.extend(values)
    if path_substr:
        where.append(f"LOWER({_NEWEST_PATH}) LIKE {mark}")
        params.append(f"%{path_substr.lower()}%")
    # Which reports this pass reads: risk is inside them. A member's report
    # is always read, for _molecule_only and _benign_archive_item.
    if min_score is not None or max_score is not None:
        scores = "all"
    read = {
        "all": "1 = 1",
        "bad": "s.label = 'bad' OR sc.sample_id IS NULL",
        "none": "sc.sample_id IS NULL",
    }[scores]
    path = _NEWEST_PATH if with_path or path_substr else "NULL"
    query = (
        "SELECT s.id, s.sha256, s.label, s.file_type, sc.sample_id IS NOT NULL,"
        f" CASE WHEN {read} THEN v.detail END, length(v.detail), {path}"
        f" FROM {CORPUS_FROM} WHERE {' AND '.join(where)}"
        + (" ORDER BY s.id" if ordered or limit > 0 else "")
    )
    counts = {"rows": 0, "stub": 0, "filler": 0, "unreadable": 0, "score": 0}
    started = time.monotonic()
    try:
        for row in _stream(conn, query, params):
            row_id, sha256, label, file_type, scanned, detail, size, row_path = row
            score = 0
            if detail is not None:
                report = decode_report(detail)
                if report is None:
                    counts["unreadable"] += 1
                    log.warning("sample %s: atomscan report is not a JSON object, skipping", row_id)
                    continue
                if not scanned and _molecule_only(report):
                    counts["stub"] += 1
                    continue
                if label == "bad" and not scanned and _benign_archive_item(report):
                    counts["filler"] += 1
                    continue
                score = _risk(report)
            if (min_score is not None and score < min_score) or (
                max_score is not None and score > max_score
            ):
                counts["score"] += 1
                continue
            yield CorpusRow(
                int(row_id), bytes(sha256).hex(), _label_int(label), file_type or "unknown",
                score, row_path or "", int(size or 0),
            )
            counts["rows"] += 1
            if limit and counts["rows"] >= limit:
                return
    finally:
        log.info(
            "corpus pass (max_id=%d file_types=%d scores=%s): %d rows; dropped %d member stub "
            "reports, %d bad archive filler, %d unreadable reports, %d outside score bounds; %.1fs",
            max_id, len(file_types or ()), scores, counts["rows"], counts["stub"],
            counts["filler"], counts["unreadable"], counts["score"], time.monotonic() - started,
        )


def stream_corpus(
    db_path: Path | str,
    *,
    max_id: int = 0,
    file_types: tuple[str, ...] | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    scores: str = "bad",
    path_substr: str | None = None,
    with_path: bool = False,
    limit: int = 0,
    percent: str | None = None,
    ordered: bool = True,
) -> Iterator[CorpusRow]:
    """Yield every usable labeled sample in id order, from one snapshot.

    ``max_id`` pins the corpus (see snapshot_max_id); ``file_types`` takes
    canonical route labels; ``path_substr`` matches the newest location;
    ``percent`` keeps a digest-hash cohort (sample_predicate), within the
    COLLIMATOR_SAMPLE_PERCENT one LABELED_WHERE already keeps.

    ``score`` is the report's risk, and hopper keeps risk only inside the
    compressed report, so a pass reads it only where it must: ``scores`` is
    "all", "bad" (the malware training gate; the default) or "none", and a
    score bound reads all. Rows whose report was not read report 0.
    """
    with _connect(db_path, repeatable_read=True) as conn:
        yield from _corpus(
            conn, max_id=max_id, file_types=file_types, min_score=min_score,
            max_score=max_score, scores=scores, path_substr=path_substr,
            with_path=with_path, limit=limit, percent=percent, ordered=ordered,
        )


# --- report assembly ---------------------------------------------------------


def _xmin(conn: Any) -> str:
    """The samples row's version: PostgreSQL's xmin; SQLite has none."""
    return "s.xmin::text" if _pg_conn(conn) else "''"


def _evaluation_version(row_id: int, xmin: Any, digest: Any, label: str, item: Any = None) -> list[Any]:
    """What an evaluation cache depends on: the samples row (label included) and its report."""
    report = bytes(digest).hex() if digest is not None else None
    return [int(row_id), str(xmin or ""), report, label, item]


def evaluation_versions(conn: Any, ids: list[int]) -> Iterator[tuple[int, str, list[Any]]]:
    """Yield (row_id, label, version) for each existing sample of ``ids``, by id."""
    for chunk in _chunks(sorted(ids), _PG_CHUNK if _pg_conn(conn) else _SQLITE_CHUNK):
        clause, params = _in(conn, "s.id", chunk)
        query = (
            f"SELECT s.id, {_xmin(conn)}, v.digest, s.label FROM samples s"
            f" LEFT JOIN verdicts v ON v.sample_id = s.id AND v.scanner_id = {ATOMSCAN}"
            f" WHERE {clause} ORDER BY s.id"
        )
        rows = list(_execute(conn, query, params))
        reports = _reports(conn, [int(row[0]) for row in rows])
        for row_id, xmin, digest, label in rows:
            yield int(row_id), str(label), _evaluation_version(row_id, xmin, digest, str(label), reports.get(int(row_id)))


def _members(conn: Any, roots: list[int]) -> dict[int, list[tuple[int, int, int, str]]]:
    """Each root's files, breadth first: (id, parent index, depth, path in parent).

    The root is entry 0 (parent -1). A walk stops MAX_REPORT_DEPTH levels down
    or at MAX_REPORT_FILES files, as hopper's own Members walk is bounded.
    """
    files = {root: [(root, -1, 0, "")] for root in roots}
    frontier = [(root, 0) for root in roots]
    children: dict[int, list[tuple[int, str]]] = {}
    chunk_size = _PG_CHUNK if _pg_conn(conn) else _SQLITE_CHUNK
    for depth in range(1, MAX_REPORT_DEPTH + 1):
        wanted = {files[root][i][0] for root, i in frontier} - children.keys()
        for chunk in _chunks(sorted(wanted), chunk_size):
            children.update((parent, []) for parent in chunk)
            clause, params = _in(conn, "parent_id", chunk)
            query = f"SELECT parent_id, child_ids, paths FROM contents WHERE {clause}"
            for parent, child_ids, paths in _execute(conn, query, params):
                listing = zip(map(int, _array(child_ids)), _array(paths), strict=True)
                children[int(parent)] = list(listing)
        following = []
        for root, i in frontier:
            listed = files[root]
            for child, path in children[listed[i][0]]:
                if len(listed) >= MAX_REPORT_FILES:
                    break
                listed.append((child, i, depth, str(path)))
                following.append((root, len(listed) - 1))
        frontier = following
        if not frontier:
            break
    for root, listed in files.items():
        if len(listed) >= MAX_REPORT_FILES:
            log.info("sample %d: report truncated at %d files", root, MAX_REPORT_FILES)
    return files


# A file as a report entry needs it: sha256, file type, size, report or None.
_FileRow = tuple[str, str, int, dict[str, Any] | None]


def _file_rows(conn: Any, ids: Iterable[int]) -> dict[int, _FileRow]:
    """Each file's _FileRow."""
    out: dict[int, _FileRow] = {}
    for chunk in _chunks(sorted(ids), _PG_CHUNK if _pg_conn(conn) else _SQLITE_CHUNK):
        clause, params = _in(conn, "s.id", chunk)
        query = (
            "SELECT s.id, s.sha256, s.file_type, s.size_bytes, v.detail FROM samples s"
            f" LEFT JOIN verdicts v ON v.sample_id = s.id AND v.scanner_id = {ATOMSCAN}"
            f" WHERE {clause}"
        )
        for row_id, sha256, file_type, size, detail in _execute(conn, query, params):
            report = decode_report(detail)
            out[int(row_id)] = (bytes(sha256).hex(), file_type or "", int(size or 0), report)
    return out


def _newest_locations(conn: Any, ids: list[int]) -> dict[int, tuple[str, str]]:
    """(path, mtime) of each file's newest location, as _NEWEST_PATH picks it."""
    out: dict[int, tuple[str, str]] = {}
    for chunk in _chunks(sorted(ids), _PG_CHUNK if _pg_conn(conn) else _SQLITE_CHUNK):
        clause, params = _in(conn, "sample_id", chunk)
        # Ascending seen_at then descending path: the last row of a sample wins.
        query = (
            f"SELECT sample_id, path, mtime FROM locations WHERE {clause}"
            " ORDER BY seen_at, path DESC"
        )
        for row_id, path, mtime in _execute(conn, query, params):
            out[int(row_id)] = (str(path), str(mtime) if mtime else "")
    return out


# Scan scores each archive member on its own, as a one-entry report that keeps
# its place in the archive (scan's score_embedded_files: every embedded node,
# depth > 0, gets its own verdict). Models at ABI 20, which collimator trains,
# read that depth as it is. A sample hopper never scanned on its own is such a
# member, so it trains as scan serves it: alone, nested. Its true depth is not in
# the schema without walking up contents; on legacy's member rows (python_bytecode,
# json, jar, elf) depth 1 scores within a few points of the true depth.
MEMBER_DEPTH = 1


def _scanned(conn: Any, ids: list[int]) -> set[int]:
    """The ids hopper scanned on its own (a scans row); the rest are members."""
    out: set[int] = set()
    for chunk in _chunks(sorted(set(ids)), _PG_CHUNK if _pg_conn(conn) else _SQLITE_CHUNK):
        clause, params = _in(conn, "sample_id", chunk)
        out.update(int(row_id) for (row_id,) in _execute(conn, f"SELECT sample_id FROM scans WHERE {clause}", params))
    return out


def _reports(
    conn: Any, ids: list[int], evaluation_labels: dict[int, int] | None = None,
) -> dict[int, dict[str, Any]]:
    """Rebuild the multi-file report each sample trains on.

    A version 8 report describes one file and moves what says where it sat
    (sha, type, size, depth, path, its id and its parent's) out of it; members
    are files of their own, listed in contents. This puts the archive back
    together as the scan saw it: the sample's report first (depth 0), then
    every file contents lists beneath it, breadth first, each its own report
    with those keys restored and paths joined with "!!" as cleave writes them.
    A member atomscan holds no report for is listed by type and size alone.
    The root's path is the file name of its newest location.

    A sample hopper never scanned on its own (no scans row) is an archive member:
    it is reported alone, one entry at MEMBER_DEPTH, with nothing beneath it, as
    scan featurizes a member it scores (see MEMBER_DEPTH).

    A sample without an atomscan report is absent from the result.
    """
    roots: dict[int, tuple[Any, Any]] = {}  # id -> (xmin, report digest)
    files: dict[int, _FileRow] = {}
    for chunk in _chunks(sorted(set(ids)), _PG_CHUNK if _pg_conn(conn) else _SQLITE_CHUNK):
        clause, params = _in(conn, "s.id", chunk)
        query = (
            "SELECT s.id, s.sha256, s.file_type, s.size_bytes, v.detail,"
            f" {_xmin(conn)}, v.digest"
            f" FROM samples s JOIN verdicts v ON v.sample_id = s.id AND v.scanner_id = {ATOMSCAN}"
            f" WHERE v.detail IS NOT NULL AND {clause}"
        )
        for row_id, sha256, file_type, size, detail, xmin, digest in _execute(conn, query, params):
            rid = int(row_id)
            report = decode_report(detail)
            if report is None:
                log.warning("sample %d: atomscan report is not a JSON object, skipping", rid)
                continue
            files[rid] = (bytes(sha256).hex(), file_type or "", int(size or 0), report)
            roots[rid] = (xmin, digest)
    scanned = _scanned(conn, list(roots))
    tree = _members(conn, [rid for rid in roots if rid in scanned])
    tree.update({rid: [(rid, -1, 0, "")] for rid in roots if rid not in scanned})
    listed = {fid for entries in tree.values() for fid, _p, _d, _r in entries}
    files.update(_file_rows(conn, listed - files.keys()))
    places = _newest_locations(conn, list(roots))

    result: dict[int, dict[str, Any]] = {}
    for rid, (xmin, digest) in roots.items():
        path, mtime = places.get(rid, ("", ""))
        entries: list[dict[str, Any]] = []
        paths: list[str] = []
        for index, (fid, parent, depth, rel) in enumerate(tree[rid]):
            sha256, file_type, size, report = files.get(fid, ("", "", 0, None))
            entry = dict(report or {})
            entry.update(id=index, depth=depth, sha=sha256, type=file_type, size=size)
            if parent < 0:
                entry["path"] = path.rsplit("/", 1)[-1]
                if rid not in scanned:
                    entry["depth"] = MEMBER_DEPTH
            else:
                entry["pid"] = parent
                entry["path"] = f"{paths[parent]}!!{rel}"
            paths.append(entry["path"])
            entries.append(entry)
        root = entries[0]
        formula = _molecule(root)
        item: dict[str, Any] = {
            "cleave_result": {"files": entries},
            "formula": formula,
            "elements": formula.translate(_SUBSCRIPTS),
            "score": _risk(root),
            "mtime": mtime,
            "cluster_id": 0,
        }
        if evaluation_labels and rid in evaluation_labels:
            from .cache_identity import evaluation_row_digest  # noqa: PLC0415

            selected = {0: "good", 1: "bad"}[evaluation_labels[rid]]
            version = _evaluation_version(rid, xmin, digest, selected, dict(item))
            item["evaluation_digest"] = evaluation_row_digest(version)
        result[rid] = item
    return result


@timed('db.fetch_and_decode')
def fetch_cleave_results(
    dsn: Path | str, ids: list[int], *, evaluation_labels: dict[int, int] | None = None,
) -> dict[int, dict[str, Any]]:
    """Batch-fetch each sample's training report and related metadata by row ID.

    Returns ``{row_id: {"cleave_result": report, "formula", "elements",
    "score", "mtime", "cluster_id"}}``; the report is rebuilt from hopper's
    per-file reports (see _reports) in the multi-file shape cleave wrote. The
    key keeps its legacy name so every consumer reads old and new alike.

    Used by feature extraction workers. Each worker opens its own
    connection via this function — safe for multiprocessing. All of a batch
    is read in one snapshot. When selected evaluation labels are provided,
    each evaluated row's version is digested from that same snapshot, using
    those labels rather than racing a later read of the live labels.
    """
    if not ids:
        return {}
    with _connect(dsn, repeatable_read=True) as conn:
        return _reports(conn, ids, evaluation_labels)


def _with_reports(conn: Any, rows: Iterable[CorpusRow]) -> Iterator[Sample]:
    """Each row as a Sample, its report read in batches from the same snapshot."""
    for batch in _chunks(rows, _SQLITE_CHUNK):
        reports = _reports(conn, [row.row_id for row in batch])
        for row in batch:
            item = reports.get(row.row_id)
            if item is None:
                continue
            yield Sample(
                row_id=row.row_id,
                sha256=row.sha256,
                path=row.path,
                label=row.label,
                report=item["cleave_result"],
                formula=item["formula"],
                elements=item["elements"],
                score=item["score"],
                mtime=item["mtime"],
                cluster_id=item["cluster_id"],
                canonical_sha256=row.canonical_sha256,
            )


@timed('db.file_types')
def fetch_file_types(db_path: Path | str, row_ids: Iterable[int]) -> dict[int, str]:
    """Return stored file types for the requested usable labeled rows.

    For rows a caller already selected: the filter is LABELED_WHERE alone.
    Requests up to 250k rows use bounded ID lookups, covering the usual
    150k-row experiment. Larger requests read the labeled population once.
    """
    wanted = {int(row_id) for row_id in row_ids}
    if not wanted:
        return {}
    query = (
        "SELECT s.id, COALESCE(NULLIF(s.file_type, ''), 'unknown')"
        f" FROM {CORPUS_FROM} WHERE {LABELED_WHERE}"
    )
    with _connect(db_path, repeatable_read=True) as conn:
        if len(wanted) <= 250_000:
            result: dict[int, str] = {}
            for chunk in _chunks(sorted(wanted), _PG_CHUNK if _pg_conn(conn) else _SQLITE_CHUNK):
                clause, params = _in(conn, "s.id", chunk)
                result.update(
                    (int(row_id), file_type)
                    for row_id, file_type in _execute(conn, f"{query} AND {clause}", params)
                )
            return result
        return {
            int(row_id): file_type
            for row_id, file_type in _stream(conn, f"{query} AND s.id <= {max(wanted)}")
            if int(row_id) in wanted
        }


def describe_rows(
    db_path: Path | str, row_ids: Iterable[int], *, limit: int = 200,
) -> dict[int, dict[str, Any]]:
    """Current label and atomscan-verdict state of rows, for diagnosis.

    For asking why a row selected into the corpus earlier is no longer
    readable: hopper rewrites verdicts while a run is in flight. A row with no
    verdict at all comes back with ``outcome`` None. At most *limit* rows
    (lowest ids first) are described; this is a diagnostic, not a bulk read.
    """
    wanted = sorted({int(row_id) for row_id in row_ids})[:limit]
    if not wanted:
        return {}
    out: dict[int, dict[str, Any]] = {}
    with _connect(db_path) as conn:
        clause, params = _in(conn, "s.id", wanted)
        query = (
            "SELECT s.id, s.label, s.label_source, s.file_type, v.outcome,"
            " v.detail IS NULL, v.formed_at, v.summary"
            " FROM samples s"
            f" LEFT JOIN verdicts v ON v.sample_id = s.id AND v.scanner_id = {ATOMSCAN}"
            f" WHERE {clause}"
        )
        for row_id, label, source, file_type, outcome, no_detail, formed_at, summary in _execute(
            conn, query, params,
        ):
            out[int(row_id)] = {
                "label": str(label),
                "label_source": source,
                "file_type": file_type,
                "outcome": None if outcome is None else str(outcome),
                "detail_null": None if outcome is None else bool(no_detail),
                "formed_at": None if formed_at is None else str(formed_at),
                "summary": summary,
            }
    return out


def split_keys(db_path: Path | str, row_ids: Iterable[int]) -> dict[int, str]:
    """Return the split key (canonical_sha256) of each requested usable labeled row.

    For rows a caller already selected: the filter is LABELED_WHERE alone.
    """
    out: dict[int, str] = {}
    with _connect(db_path, repeatable_read=True) as conn:
        size = _PG_CHUNK if _pg_conn(conn) else _SQLITE_CHUNK
        for chunk in _chunks(sorted({int(row_id) for row_id in row_ids}), size):
            clause, params = _in(conn, "s.id", chunk)
            query = f"SELECT s.id, s.sha256 FROM {CORPUS_FROM} WHERE {LABELED_WHERE} AND {clause}"
            rows = _execute(conn, query, params)
            out.update((int(row_id), bytes(sha256).hex()) for row_id, sha256 in rows)
    return out


@timed('db.snapshot_pin')
def snapshot_max_id(db_path: Path | str) -> int:
    """Return max(id) of usable labeled samples at this moment.

    Used to pin the dataset for a single experiment / training run so that
    concurrent inserts to the hopper database don't cause drift between runs.
    Pass the returned value as ``max_id`` to ``stream_partitioned_metadata_grouped``
    or ``partition_row_ids``. A pin needs only to bound the ids, so the
    Python-side filters (filler members, score floors) are not applied.
    """
    query = f"SELECT MAX(s.id) FROM {CORPUS_FROM} WHERE {LABELED_WHERE}"
    with _connect(db_path) as conn:
        for (max_id,) in _execute(conn, query):
            return int(max_id) if max_id is not None else 0
    return 0


# Sentinel for stream_partitioned_metadata_grouped: "apply the module-level
# MIN_SAMPLE_SCORE floor" (legacy behavior). Pass min_score=None to stream
# the full labeled population — the eval-side contract (screens measure the
# same benign universe deploy calibrates on).
_SCORE_FILTER_DEFAULT: Any = object()


def _sample_floor() -> int | None:
    return MIN_SAMPLE_SCORE if MIN_SAMPLE_SCORE > 0 else None


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
    Default yields every labeled row. ``limit`` caps the rows read.
    """

    def keep(row: CorpusRow) -> bool:
        partition = row.partition
        if exclude_test and partition == "test":
            return False
        if exclude_eval and partition in ("test", "dev"):
            return False
        if only_test and partition != "test":
            return False
        if only_dev and partition != "dev":
            return False
        return exclude_oof_fold is None or (
            partition != "test" and oof_fold_of(row.sha256) != exclude_oof_fold
        )

    with _connect(db_path, repeatable_read=True) as conn:
        rows = _corpus(conn, min_score=_sample_floor(), scores="none", with_path=True, limit=limit)
        yield from _with_reports(conn, (row for row in rows if keep(row)))


def stream_labeled_samples_full(
    db_path: Path | str,
    *,
    path_substr: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    limit: int = 0,
    max_id: int = 0,
) -> Iterator[Sample]:
    """Yield usable labeled samples with their reports, without the MIN_SAMPLE_SCORE floor.

    This is for operational corpus analysis over the full labeled hopper set,
    including low-score benign rows that are intentionally excluded from
    training/evaluation partitions.
    """
    with _connect(db_path, repeatable_read=True) as conn:
        rows = _corpus(
            conn, max_id=max_id, min_score=min_score, max_score=max_score, scores="none",
            path_substr=path_substr, with_path=True, limit=limit,
        )
        yield from _with_reports(conn, rows)


def stream_labeled_metadata_full(
    db_path: Path | str,
    *,
    path_substr: str | None = None,
    min_score: int | None = None,
    max_score: int | None = None,
    limit: int = 0,
    max_id: int = 0,
    partition: str | None = None,
    compact: bool = False,
    ordered: bool = True,
) -> Iterator[tuple[int, str, str, int, int, str]]:
    """Yield usable labeled sample metadata without loading reports.

    Yielded tuple: ``(row_id, sha256, path, score, label, canonical_sha256)``.
    ``score`` is read for bad rows, and for every row under a score bound;
    benign rows otherwise report 0 (stream_corpus). The metadata extraction
    workers replace it with each report's risk as they read the report.

    If ``partition`` is set ("train", "dev", or "test"), only rows in that
    partition are yielded.
    """
    for row in stream_corpus(
        db_path, max_id=max_id, min_score=min_score, max_score=max_score,
        path_substr=path_substr, with_path=not compact, limit=limit, ordered=ordered,
    ):
        if partition is not None and row.partition != partition:
            continue
        yield row.row_id, "" if compact else row.sha256, "" if compact else row.path, 0 if compact else row.score, row.label, row.canonical_sha256


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
    """Yield full-corpus metadata plus a report size estimate.

    Yielded tuple: ``(row_id, sha256, path, score, label, report_bytes, canonical_sha256)``.
    ``report_bytes`` is the compressed size of the file's own report: a
    relative weight for batch packing (an archive's members are not counted).
    ``score`` is as in stream_labeled_metadata_full.

    If ``partition`` is set, only rows from that partition are yielded.
    """
    for row in stream_corpus(
        db_path, max_id=max_id, min_score=min_score, max_score=max_score,
        path_substr=path_substr, with_path=True, limit=limit,
    ):
        if partition is not None and row.partition != partition:
            continue
        yield (row.row_id, row.sha256, row.path, row.score, row.label,
               row.report_bytes, row.canonical_sha256)


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
    limit: int = 0,
) -> Iterator[tuple[dict[str, Any], int]]:
    """Yield (report, label) pairs. See stream_samples for filter semantics.

    ``limit`` caps the rows read (0 = unbounded); without it a caller that
    only wants a small sample still triggers a full-corpus scan.
    """
    for sample in stream_samples(
        db_path,
        exclude_test=exclude_test,
        exclude_eval=exclude_eval,
        only_test=only_test,
        only_dev=only_dev,
        limit=limit,
    ):
        yield sample.report, sample.label


def partition_row_ids(
    db_path: Path | str,
    min_malware_training_score: int = 0,
    max_id: int = 0,
) -> tuple[list[int], list[tuple[int, int]], list[tuple[int, int]], list[tuple[int, int]]]:
    """Partition samples into train/dev/test by split key.

    Returns (train_row_ids, train_ids_labels, dev_ids_labels, test_ids_labels).
    Pass ``max_id`` from ``snapshot_max_id`` to pin the dataset.

    train_row_ids feed model fitting; dev rows feed calibration and threshold
    search; test rows produce headline metrics. Disjoint by construction.
    """
    train_row_ids: list[int] = []
    train_ids_labels: list[tuple[int, int]] = []
    dev_ids_labels: list[tuple[int, int]] = []
    test_ids_labels: list[tuple[int, int]] = []
    rows = stream_partitioned_metadata_grouped(db_path, max_id=max_id)
    for row_id, label, partition, _canonical, score in rows:
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
    """Look up a sample by SHA256 prefix. Returns (sha256, path, label, report) or None.

    The first sample (by digest) at or after the prefix that has a report.
    """
    prefix = sha256_prefix.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{1,64}", prefix):
        return None
    low, high = bytes.fromhex(prefix.ljust(64, "0")), bytes.fromhex(prefix.ljust(64, "f"))
    with _connect(db_path, repeatable_read=True) as conn:
        mark = _marker(conn)
        query = (
            f"SELECT s.id, s.label FROM samples s"
            f" JOIN verdicts v ON v.sample_id = s.id AND v.scanner_id = {ATOMSCAN}"
            f" WHERE s.sha256 >= {mark} AND s.sha256 <= {mark} AND v.detail IS NOT NULL"
            " ORDER BY s.sha256 LIMIT 1"
        )
        for row_id, label in _execute(conn, query, [low, high]):
            rid = int(row_id)
            item = _reports(conn, [rid]).get(rid)
            if item is None:
                return None
            root = item["cleave_result"]["files"][0]
            newest = f"SELECT {_NEWEST_PATH} FROM samples s WHERE s.id = {mark}"
            path = next(iter(_execute(conn, newest, [rid])))[0]
            return root["sha"], path or "", str(label), item["cleave_result"]
    return None


def stream_partitioned_metadata_grouped(
    db_path: Path | str,
    limit: int = 0,
    max_id: int = 0,
    file_types: tuple[str, ...] | None = None,
    min_score: int | None | object = _SCORE_FILTER_DEFAULT,
) -> Iterator[tuple[int, int, str, str, int]]:
    """Yield (row_id, label, partition, canonical_sha256, score) without loading reports.

    ``partition`` is one of "train", "dev", "test". If ``max_id`` > 0, only
    rows with ``id <= max_id`` are returned. Use this with a value from
    ``snapshot_max_id`` to pin the dataset for a single run, so that
    concurrent inserts don't cause drift.

    ``min_score`` — omitted: apply the module-level ``MIN_SAMPLE_SCORE``
    floor (legacy). ``None``: no score floor, the full labeled population.
    Callers that separate train from eval should stream with ``None`` and
    apply the floor to TRAIN rows only: a floor on the eval side changes the
    benign denominator (and can flip the 25k operating-point regime) for
    reasons unrelated to the model.

    ``score`` is read for every bad row (the malware training gate) and,
    while MIN_SAMPLE_SCORE is set (callers apply it to train rows), for
    every row; benign rows otherwise report 0.
    """
    effective = MIN_SAMPLE_SCORE if min_score is _SCORE_FILTER_DEFAULT else min_score
    floor = int(effective) if isinstance(effective, int) and effective > 0 else None
    rows = stream_corpus(
        db_path, max_id=max_id, file_types=file_types, min_score=floor,
        scores="all" if MIN_SAMPLE_SCORE > 0 else "bad", limit=limit,
    )
    for row in rows:
        yield row.row_id, row.label, row.partition, row.canonical_sha256, row.score


def count_labeled_by_partition_full(
    db_path: Path | str,
    *,
    max_id: int = 0,
) -> dict[str, dict[str, int]]:
    """Count all usable labeled rows by partition without score filtering.

    Returns counts under keys "train", "dev", "test", "all". FP-per-million
    reporting is a corpus-level good-file rate, so it needs the full labeled
    good-file denominator, including low-score rows.
    """
    counts = {
        part: {"good": 0, "bad": 0, "total": 0}
        for part in ("train", "dev", "test", "all")
    }
    for row in stream_corpus(db_path, max_id=max_id, scores="none"):
        name = "bad" if row.label == 1 else "good"
        for part in (row.partition, "all"):
            counts[part][name] += 1
            counts[part]["total"] += 1
    return counts


def labeled_corpus_metadata_full(
    db_path: Path | str,
    *,
    max_id: int = 0,
) -> dict[str, int]:
    """Return row counts for the full labeled threshold/FP corpus."""
    total = bad = row_max_id = 0
    for row in stream_corpus(db_path, max_id=max_id, scores="none"):
        total += 1
        bad += row.label
        row_max_id = max(row_max_id, row.row_id)
    return {"samples": total, "malware": bad, "benign": total - bad, "max_row_id": row_max_id}
