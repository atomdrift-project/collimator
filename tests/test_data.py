"""Tests for data loading from hopper databases."""

import sqlite3
import tempfile
from pathlib import Path

import zstandard

from collimator.data import (
    canonicalize_filetype,
    count_labeled_by_partition_full,
    expand_filetype_aliases,
    expand_route_filetypes,
    fetch_cleave_results,
    labeled_corpus_metadata_full,
    load_samples,
    normalize_archive_filetype,
    route_filetype,
    stream_corpus,
    stream_labeled_metadata_full_with_size,
    stream_labeled_samples_full,
)
from collimator.demo import add_sample, compress_report, create_schema


def compress_report_bytes(raw: bytes) -> bytes:
    return zstandard.ZstdCompressor().compress(raw)


def test_normalize_archive_filetype_strips_pure_compression():
    """Mirror of litmus' Rust `normalize_archive_filetype` test. The two
    must stay byte-equivalent — training emits labels with this rule and
    litmus routes scan-time files with the Rust mirror.
    """
    # Compound archive labels collapse onto their container.
    assert normalize_archive_filetype("tar.gz") == "tar"
    assert normalize_archive_filetype("tar.bz2") == "tar"
    assert normalize_archive_filetype("tar.xz") == "tar"
    assert normalize_archive_filetype("tar.zst") == "tar"
    assert normalize_archive_filetype("tar.Z") == "tar"
    assert normalize_archive_filetype("TAR.GZ") == "tar"
    # Repeated stripping for stacked suffixes.
    assert normalize_archive_filetype("tar.bz2.xz") == "tar"
    # Bare compression labels keep their identity — RAW_COMPRESSED_FILETYPES
    # in azoth_specialist_suite gates them at route discovery.
    assert normalize_archive_filetype("gz") == "gz"
    assert normalize_archive_filetype("bz2") == "bz2"
    # Containers without a compression suffix pass through.
    assert normalize_archive_filetype("zip") == "zip"
    assert normalize_archive_filetype("pe") == "pe"
    # Empty / None / whitespace.
    assert normalize_archive_filetype("") == ""
    assert normalize_archive_filetype(None) == ""
    assert normalize_archive_filetype("  tar.gz  ") == "tar"


def test_runtime_route_expansion_preserves_all_aliases_and_compressed_members():
    assert {'tar','tar.gz','tar.bz2','tar.xz','tar.zst'} <= set(expand_route_filetypes(('tar.gz',)))
    assert {'ole_doc','doc','xls','ole'} <= set(expand_route_filetypes(('xls',)))
    # filefacts reports MSI as its own type, so it is no Office alias.
    assert 'msi' not in expand_route_filetypes(('xls',))
    assert expand_route_filetypes(('pe',)) == ('pe',)


def test_canonicalize_filetype_folds_old_spellings():
    """Old cleave label spellings collapse onto filefacts' canonical labels;
    canonical and unknown inputs are returned unchanged (idempotent).
    """
    # Hyphenated / abbreviated old forms.
    assert canonicalize_filetype("objc") == "objective_c"
    assert canonicalize_filetype("python-bytecode") == "python_bytecode"
    assert canonicalize_filetype("github-actions") == "github_actions"
    assert canonicalize_filetype("systemd") == "systemd_service"
    assert canonicalize_filetype("pkg-info") == "pkg_info"
    # Debug-mangled old forms (dropped underscores).
    assert canonicalize_filetype("pythonsdist") == "python_sdist"
    assert canonicalize_filetype("javaclass") == "java_class"
    assert canonicalize_filetype("ociimage") == "oci_image"
    assert canonicalize_filetype("cargolock") == "cargo.lock"
    assert canonicalize_filetype("packagejson") == "package.json"
    # Office subtypes collapse onto the container type filefacts emits.
    assert canonicalize_filetype("docx") == "ooxml"
    assert canonicalize_filetype("xls") == "ole_doc"
    # Media spelling.
    assert canonicalize_filetype("jpg") == "jpeg"
    # Canonical labels and unknowns pass through; idempotent; case/space folded.
    assert canonicalize_filetype("objective_c") == "objective_c"
    assert canonicalize_filetype("tar.gz") == "tar.gz"
    assert canonicalize_filetype("pe") == "pe"
    assert canonicalize_filetype("totally_unknown") == "totally_unknown"
    assert canonicalize_filetype("  OBJC  ") == "objective_c"
    assert canonicalize_filetype(None) == ""


def test_expand_filetype_aliases_widens_to_stored_spellings():
    """A canonical route label expands to every stored spelling so an
    index-backed `file_type IN (...)` filter matches old and new rows alike.
    """
    # Canonical request includes itself plus its aliases.
    assert expand_filetype_aliases(("objective_c",)) == ("objc", "objective_c", "objectivec")
    # Office container expands to its collapsed subtypes (incl. macro/template
    # variants); checked by membership so adding subtypes doesn't break this.
    ooxml_expansion = set(expand_filetype_aliases(("ooxml",)))
    assert {"ooxml", "docx", "xlsx", "pptx", "xlsm", "docm", "xltx"} <= ooxml_expansion
    # Passing an old spelling canonicalizes first, then expands the same way.
    assert expand_filetype_aliases(("objc",)) == ("objc", "objective_c", "objectivec")
    # A label with no aliases expands to just itself; empties are dropped.
    assert expand_filetype_aliases(("pe", "")) == ("pe",)


def test_route_filetype_composes_compression_and_canonicalization():
    """The publish-path route label strips compression AND folds the spelling,
    so old and new stored spellings of one type collapse onto a single route
    named the way scan receives it from filefacts."""
    # Both normalizations apply: compression-stripping...
    assert route_filetype("tar.gz") == "tar"
    assert route_filetype("tar.bz2.xz") == "tar"
    # ...and spelling-folding onto the filefacts label.
    assert route_filetype("python-bytecode") == "python_bytecode"
    assert route_filetype("pyc") == "python_bytecode"
    assert route_filetype("objc") == "objective_c"
    # Office subtypes collapse onto the container specialist scan can reach.
    assert route_filetype("xlsx") == "ooxml"
    assert route_filetype("docx") == "ooxml"
    assert route_filetype("xls") == "ole_doc"
    assert route_filetype("doc") == "ole_doc"
    # Every stored spelling of one type maps to the SAME route — the merge.
    assert (
        route_filetype("python-bytecode")
        == route_filetype("python_bytecode")
        == route_filetype("pyc")
    )
    # Canonical labels and unknowns pass through; idempotent; trims/lowercases.
    assert route_filetype("ooxml") == "ooxml"
    assert route_filetype("pe") == "pe"
    assert route_filetype("totally_unknown") == "totally_unknown"
    assert route_filetype("  PYTHON-BYTECODE  ") == "python_bytecode"
    assert route_filetype(None) == ""
    # Bare compression leaves stay put (no specialist of their own).
    assert route_filetype("gz") == "gz"


def _sha(name: str) -> str:
    """A full digest spelled by repeating a short hex name ("aaa" -> "aaaa…")."""
    return (name * 64)[:64]


def _create_test_db(samples: list[tuple[str, str, dict | bytes | None] | dict]) -> Path:
    """Create a temporary hopper verdict-schema SQLite DB.

    Each tuple: (sha256, label, report) — the file's v8 report, raw stored
    bytes, or None. Or a dict with optional path/score/conflict overrides:
    score is the report's risk, conflict marks a good/bad conflict.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)
    db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    create_schema(conn)
    for entry in samples:
        if isinstance(entry, dict):
            sha = str(entry["sha256"])
            label = str(entry["label"])
            report = entry["report"]
            path = entry.get("path")
            score = int(entry.get("score", 10))
            conflict = bool(entry.get("conflict", False))
        else:
            sha, label, report = entry
            path, score, conflict = None, 10, False
        if isinstance(report, dict):
            report = {**report, "risk": score}
        add_sample(
            conn, sha256=sha, label=label, report=report, path=path,
            label_source="conflict" if conflict else None,
        )
    conn.commit()
    conn.close()
    return db_path


def _minimal_report() -> dict:
    return {"findings": [], "structure": [], "strings": []}


def test_compact_unordered_metadata_preserves_ids_and_partitions():
    from collimator.data import stream_labeled_metadata_full

    db = _create_test_db([
        {"sha256": _sha("a"), "label": "bad", "report": _minimal_report(), "path": "/include/one", "score": 7},
        {"sha256": _sha("b"), "label": "good", "report": _minimal_report(), "path": "/include/two", "score": 3},
    ])
    try:
        for options in ({}, {"limit": 1}, {"min_score": 5}, {"path_substr": "two"}, {"partition": "train"}):
            expected = list(stream_labeled_metadata_full(db, **options))
            actual = list(stream_labeled_metadata_full(db, compact=True, ordered=False, **options))
            assert sorted((r[0], r[4], r[5]) for r in actual) == sorted((r[0], r[4], r[5]) for r in expected)
            assert all(r[1:4] == ("", "", 0) for r in actual)
    finally:
        db.unlink()


def test_load_labeled_samples() -> None:
    db = _create_test_db([
        (_sha("a"), "bad", _minimal_report()),
        (_sha("b"), "good", _minimal_report()),
        (_sha("c"), "unknown", _minimal_report()),  # excluded — not bad or good
    ])
    samples = load_samples(db)
    assert len(samples) == 2
    labels = {s.sha256: s.label for s in samples}
    assert labels[_sha("a")] == 1  # malware
    assert labels[_sha("b")] == 0  # benign


def test_skip_missing_report() -> None:
    db = _create_test_db([
        (_sha("a"), "bad", _minimal_report()),
        (_sha("b"), "bad", b""),
        (_sha("c"), "good", None),
    ])
    samples = load_samples(db)
    assert len(samples) == 1
    assert samples[0].sha256 == _sha("a")


def test_skip_invalid_report() -> None:
    db = _create_test_db([
        (_sha("a"), "bad", _minimal_report()),
        (_sha("b"), "bad", b"not valid json{{{"),
        (_sha("c"), "bad", compress_report_bytes(b"not valid json{{{")),
    ])
    samples = load_samples(db)
    assert len(samples) == 1


def test_empty_database() -> None:
    db = _create_test_db([])
    samples = load_samples(db)
    assert len(samples) == 0


def test_file_not_found() -> None:
    import pytest
    with pytest.raises(FileNotFoundError):
        load_samples(Path("/nonexistent/database.db"))


def test_schema_without_verdict_tables_fails_fast(tmp_path) -> None:
    import pytest
    db = tmp_path / "legacy.db"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE samples (id INTEGER PRIMARY KEY, cleave_result TEXT)")
    with pytest.raises(RuntimeError, match="no samples and verdicts tables"):
        load_samples(db)


def test_stream_labeled_samples_full_includes_low_score_and_applies_filters() -> None:
    db = _create_test_db([
        {"sha256": _sha("a"), "label": "good", "report": _minimal_report(), "path": "/repo/harvest/low.py", "score": 0},
        {"sha256": _sha("b"), "label": "bad", "report": _minimal_report(), "path": "/repo/harvest/high.py", "score": 42},
        {"sha256": _sha("c"), "label": "good", "report": _minimal_report(), "path": "/repo/other/x.py", "score": 7, "conflict": True},
    ])
    samples = list(stream_labeled_samples_full(db, path_substr="harvest"))
    assert [sample.sha256 for sample in samples] == [_sha("a"), _sha("b")]
    assert [sample.score for sample in samples] == [0, 42]
    assert [sample.path for sample in samples] == ["/repo/harvest/low.py", "/repo/harvest/high.py"]


def test_stream_labeled_metadata_full_with_size_includes_report_size() -> None:
    low_report = {**_minimal_report(), "risk": 0}
    high_report = {"ts": ["x" * 100], "risk": 42}
    db = _create_test_db([
        {"sha256": _sha("a"), "label": "good", "report": low_report, "path": "/repo/harvest/low.py", "score": 0},
        {"sha256": _sha("b"), "label": "bad", "report": high_report, "path": "/repo/harvest/high.py", "score": 42},
        {"sha256": _sha("c"), "label": "good", "report": _minimal_report(), "path": "/repo/other/x.py", "score": 7, "conflict": True},
    ])

    rows = list(stream_labeled_metadata_full_with_size(db, path_substr="harvest"))

    # A bad row's score is its report's risk; a benign row's is read only
    # under a score bound.
    assert [row[:5] for row in rows] == [
        (1, _sha("a"), "/repo/harvest/low.py", 0, 0),
        (2, _sha("b"), "/repo/harvest/high.py", 42, 1),
    ]
    assert rows[0][5] == len(compress_report(low_report))
    assert rows[1][5] == len(compress_report(high_report))
    # The split key (canonical_sha256) is the trailing element: the file's
    # own digest.
    assert rows[0][6] == _sha("a")
    assert rows[1][6] == _sha("b")


def test_count_labeled_by_partition_full_includes_low_score_rows() -> None:
    # SHA256 last bytes: 00=test, 30=dev, 50=bad train, 60=unknown filtered, 70=conflict filtered.
    db = _create_test_db([
        {"sha256": "00" * 32, "label": "good", "report": _minimal_report(), "score": 0},
        {"sha256": "30" * 32, "label": "good", "report": _minimal_report(), "score": 10},
        {"sha256": "50" * 32, "label": "bad", "report": _minimal_report(), "score": 1},
        {"sha256": "60" * 32, "label": "unknown", "report": _minimal_report(), "score": 10},
        {
            "sha256": "70" * 32,
            "label": "good",
            "report": _minimal_report(),
            "score": 10,
            "conflict": True,
        },
    ])

    counts = count_labeled_by_partition_full(db)

    assert counts["all"]["good"] == 2
    assert counts["all"]["bad"] == 1
    assert counts["all"]["total"] == 3
    # 00 -> test partition (byte=0 < 32)
    assert counts["test"]["good"] == 1
    # 30 -> dev partition (32 <= byte=48 < 64)
    assert counts["dev"]["good"] == 1
    # 50 -> train partition (byte=80 >= 64)
    assert counts["train"]["bad"] == 1


def test_labeled_corpus_metadata_full_matches_threshold_corpus() -> None:
    db = _create_test_db([
        {"sha256": _sha("a"), "label": "good", "report": _minimal_report(), "score": 0},
        {"sha256": _sha("b"), "label": "bad", "report": _minimal_report(), "score": 1},
        {"sha256": _sha("c"), "label": "unknown", "report": _minimal_report(), "score": 10},
        {"sha256": _sha("d"), "label": "good", "report": None, "score": 10},
        {"sha256": _sha("e"), "label": "good", "report": _minimal_report(), "score": 10, "conflict": True},
    ])

    metadata = labeled_corpus_metadata_full(db)

    assert metadata["samples"] == 2
    assert metadata["malware"] == 1
    assert metadata["benign"] == 1
    assert metadata["max_row_id"] == 2


def _bad_member(conn: sqlite3.Connection, name: str, crits: list[int], *, scanned=False) -> int:
    traits = [{"id": f"t/{i}", "crit": crit} for i, crit in enumerate(crits)]
    report = {"traits": traits, "risk": 5}
    return add_sample(conn, sha256=_sha(name), label="bad", report=report, scanned=scanned)


def test_bad_archive_filler_is_not_trained_on(tmp_path) -> None:
    """legacy skip-benign-archive-item: a bad member trains only if its own
    findings convict it (one at crit 5, or two at crit 4)."""
    db = tmp_path / "members.db"
    with sqlite3.connect(db) as conn:
        create_schema(conn)
        filler = _bad_member(conn, "1", [3, 4])
        hostile = _bad_member(conn, "2", [5])
        suspicious = _bad_member(conn, "3", [4, 4])
        scanned = _bad_member(conn, "4", [1], scanned=True)  # judged on its own bytes
        good = add_sample(conn, sha256=_sha("5"), label="good", report={"facts": {}},
                          scanned=False)
    ids = [row.row_id for row in stream_corpus(db, scores="none")]
    assert filler not in ids
    assert ids == [hostile, suspicious, scanned, good]
    assert labeled_corpus_metadata_full(db)["samples"] == 4


def test_member_stub_reports_are_not_trained_on(tmp_path) -> None:
    """A member whose report is its molecule and risk alone (what an archive's
    report kept of it) is no analysis of the file; a scanned file's is."""
    db = tmp_path / "stubs.db"
    with sqlite3.connect(db) as conn:
        create_schema(conn)
        stub = add_sample(conn, sha256=_sha("1"), label="good", report={"mol": "H", "risk": 0},
                          scanned=False)
        empty = add_sample(conn, sha256=_sha("2"), label="good", report={}, scanned=False)
        full = add_sample(conn, sha256=_sha("3"), label="good", scanned=False,
                          report={"mol": "H", "risk": 0, "facts": {"metrics": {}}})
        scanned = add_sample(conn, sha256=_sha("4"), label="good", report={"risk": 0})
    ids = [row.row_id for row in stream_corpus(db)]
    assert stub not in ids and empty not in ids
    assert ids == [full, scanned]


def test_archive_report_is_rebuilt_from_members(tmp_path) -> None:
    """A training report lists the archive and every file contents names
    beneath it, each with what a v8 report moves out (type, depth, path…)."""
    db = tmp_path / "archive.db"
    with sqlite3.connect(db) as conn:
        create_schema(conn)
        inner = add_sample(conn, sha256=_sha("3"), label="unknown", file_type="javascript",
                           report={"traits": [{"id": "x/y", "crit": 4}]}, scanned=False)
        nested = add_sample(conn, sha256=_sha("2"), label="unknown", file_type="zip", report={},
                            scanned=False, members=[(inner, "lib/index.js")])
        loose = add_sample(conn, sha256=_sha("4"), label="unknown", file_type="text",
                           outcome=None, scanned=False)
        root = add_sample(conn, sha256=_sha("1"), label="bad", file_type="tar", size=99,
                          report={"mol": "H₂O", "risk": 7}, path="bad/x/pkg.tgz",
                          mtime="2026-01-02 03:04:05+00:00",
                          members=[(nested, "a.zip"), (loose, "README")])
    item = fetch_cleave_results(db, [root, inner])[root]
    files = item["cleave_result"]["files"]
    assert [(f["sha"], f["type"], f["depth"], f.get("pid"), f["path"]) for f in files] == [
        (_sha("1"), "tar", 0, None, "pkg.tgz"),
        (_sha("2"), "zip", 1, 0, "pkg.tgz!!a.zip"),
        (_sha("4"), "text", 1, 0, "pkg.tgz!!README"),
        (_sha("3"), "javascript", 2, 1, "pkg.tgz!!a.zip!!lib/index.js"),
    ]
    assert files[0]["size"] == 99
    assert files[3]["traits"] == [{"id": "x/y", "crit": 4}]
    assert (item["formula"], item["elements"], item["score"]) == ("H₂O", "HO", 7)
    assert item["mtime"] == "2026-01-02 03:04:05+00:00"


def test_retry_pg_connect_succeeds_after_transient_failure(monkeypatch) -> None:
    """A transient OperationalError on the first attempt must be retried, and
    the eventual successful connect must be returned without raising."""
    import sys as _sys  # noqa: PLC0415
    from collimator import data as data_mod  # noqa: PLC0415

    # Provide a minimal stand-in for psycopg so the test doesn't need a real DB.
    class FakeOpError(Exception):
        pass

    class FakePsycopg:
        OperationalError = FakeOpError

        def __init__(self):
            self.attempts = 0

        def connect(self, *_args, **_kwargs):
            self.attempts += 1
            if self.attempts == 1:
                raise FakeOpError("server briefly unreachable")
            return object()

    fake = FakePsycopg()
    monkeypatch.setitem(_sys.modules, "psycopg", fake)
    # Compress backoff so the test doesn't actually sleep.
    monkeypatch.setattr(data_mod, "_DB_CONNECT_BASE_DELAY_S", 0.001)
    monkeypatch.setattr(data_mod, "_DB_CONNECT_MAX_DELAY_S", 0.001)

    conn = data_mod._retry_pg_connect("postgres://x/y")
    assert conn is not None
    assert fake.attempts == 2, "first call must be retried after transient OperationalError"


def test_retry_pg_connect_gives_up_after_max_attempts(monkeypatch) -> None:
    """A persistent failure raises the last error after exhausting attempts —
    we don't want to silently hang on a permanently-down DB."""
    import sys as _sys  # noqa: PLC0415
    import pytest  # noqa: PLC0415
    from collimator import data as data_mod  # noqa: PLC0415

    class FakeOpError(Exception):
        pass

    class FakePsycopg:
        OperationalError = FakeOpError

        def __init__(self):
            self.attempts = 0

        def connect(self, *_args, **_kwargs):
            self.attempts += 1
            raise FakeOpError(f"down (attempt {self.attempts})")

    fake = FakePsycopg()
    monkeypatch.setitem(_sys.modules, "psycopg", fake)
    monkeypatch.setattr(data_mod, "_DB_CONNECT_BASE_DELAY_S", 0.001)
    monkeypatch.setattr(data_mod, "_DB_CONNECT_MAX_DELAY_S", 0.001)
    # Tiny total budget so the retry loop gives up almost immediately.
    monkeypatch.setattr(data_mod, "_DB_CONNECT_MAX_TOTAL_S", 0.02)

    with pytest.raises(FakeOpError, match="down"):
        data_mod._retry_pg_connect("postgres://x/y")
    # Must have retried at least once before exhausting the time budget.
    assert fake.attempts >= 2, "must retry before giving up within the time budget"
