"""Generate a tiny synthetic hopper database for local demos."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import numpy as np


def _hex_sha(rng: np.random.Generator) -> str:
    return "".join(rng.choice(list("0123456789abcdef"), size=64))


def _make_report(rng: np.random.Generator, *, malware: bool, sha256: str) -> str:
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

    report = {
        "version": "3",
        "files": [{
            "id": 0,
            "path": "/tmp/demo.bin",
            "depth": 0,
            "file_type": "pe" if malware else "elf",
            "sha256": sha256,
            "size": int(rng.integers(40_000, 300_000)),
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
        }],
        "summary": {"files_analyzed": 1, "duration_ms": 10, "tools": ["demo"]},
    }
    return json.dumps(report)


def create_demo_db(
    output_path: Path,
    *,
    n_benign: int = 64,
    n_malware: int = 64,
    seed: int = 42,
) -> None:
    """Create a synthetic hopper-schema SQLite database for demos/tests."""
    rng = np.random.default_rng(seed)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(output_path))
    try:
        conn.execute("DROP TABLE IF EXISTS samples")
        conn.execute("""
            CREATE TABLE samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sha256 TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL DEFAULT '',
                feed TEXT NOT NULL DEFAULT '',
                ecosystem TEXT NOT NULL DEFAULT '',
                filename TEXT NOT NULL DEFAULT '',
                file_type TEXT NOT NULL DEFAULT '',
                size_bytes INTEGER NOT NULL DEFAULT 0,
                label TEXT NOT NULL DEFAULT 'unknown',
                label_source TEXT NOT NULL DEFAULT '',
                cleave_result TEXT,
                risk TEXT NOT NULL DEFAULT '',
                finding_count INTEGER NOT NULL DEFAULT 0,
                path TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT '',
                note TEXT NOT NULL DEFAULT '',
                canonical_sha256 TEXT NOT NULL DEFAULT '',
                parent TEXT NOT NULL DEFAULT '',
                skip TEXT NOT NULL DEFAULT '',
                created_at DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                updated_at DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                analyzed_at DATETIME
            )
        """)

        rows: list[tuple[str, str, str, str, str]] = []
        for _ in range(n_benign):
            sha = _hex_sha(rng)
            report = _make_report(rng, malware=False, sha256=sha)
            rows.append((sha, "good", f"/demo/{sha[:12]}.bin", sha, report))
        for _ in range(n_malware):
            sha = _hex_sha(rng)
            report = _make_report(rng, malware=True, sha256=sha)
            rows.append((sha, "bad", f"/demo/{sha[:12]}.bin", sha, report))

        conn.executemany(
            "INSERT INTO samples (sha256, label, path, canonical_sha256, cleave_result)"
            " VALUES (?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()
