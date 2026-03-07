"""Load labeled samples from cyclotron's SQLite database."""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# Terminal statuses that represent confirmed classifications.
# See cyclotron/db.go for the full status state machine.
MALWARE_STATUSES = frozenset({"bad", "good-malicious"})
BENIGN_STATUSES = frozenset({"good", "bad-benign"})
ALL_TERMINAL = MALWARE_STATUSES | BENIGN_STATUSES


@dataclass(frozen=True, slots=True)
class Sample:
    sha256: str
    path: str
    label: int  # 1 = malware, 0 = benign
    report: dict[str, Any]


def load_samples(db_path: Path) -> list[Sample]:
    """Load labeled samples from a cyclotron database.

    Terminal statuses used for training:
      - 'bad', 'good-malicious'  -> label 1 (malware)
      - 'good', 'bad-benign'    -> label 0 (benign)

    Intermediate statuses (bad-review, bad-reversed, good-review, etc.)
    are skipped to ensure clean training labels.
    """
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    placeholders = ",".join("?" for _ in ALL_TERMINAL)
    query = (
        "SELECT sha256, path, status, cleave_json"
        f" FROM samples WHERE status IN ({placeholders})"
    )
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(query, tuple(sorted(ALL_TERMINAL))).fetchall()
    finally:
        conn.close()

    samples: list[Sample] = []
    skipped = 0
    for row in rows:
        cleave_json = row["cleave_json"]
        if not cleave_json:
            skipped += 1
            continue

        try:
            report = json.loads(cleave_json)
        except json.JSONDecodeError:
            log.warning("invalid JSON for %s, skipping", row["sha256"])
            skipped += 1
            continue

        label = 1 if row["status"] in MALWARE_STATUSES else 0
        samples.append(Sample(
            sha256=row["sha256"],
            path=row["path"],
            label=label,
            report=report,
        ))

    n_malware = sum(1 for s in samples if s.label == 1)
    n_benign = len(samples) - n_malware
    log.info(
        "loaded %d samples (%d malware, %d benign, %d skipped)",
        len(samples), n_malware, n_benign, skipped,
    )
    return samples
