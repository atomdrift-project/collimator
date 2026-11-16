#!/usr/bin/env python3
"""Freeze a hash-sampled corpus for repeatable, fresh pipeline experiments."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import time

from collimator import data, demo


def freeze(db, output, *, percent="1", pin=0, batch_size=128):
    """Copy a digest-hash cohort of the usable labeled corpus into a
    verdict-schema SQLite DB, under one read-only snapshot.

    Each sample keeps its id, digest (so its partition), label and path; its
    report is stored as data.py rebuilds it, so the copy trains identically.
    """
    data.sample_predicate(percent)  # validates percent
    if pin < 0 or batch_size < 1:
        raise ValueError("pin must be nonnegative and batch size must be positive")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    partial = output / "corpus.partial.sqlite"
    started = time.monotonic()
    partitions = Counter()
    labels = Counter()
    with data._connect(db, repeatable_read=True) as source, sqlite3.connect(partial) as dest:
        corpus = data._corpus(source, max_id=pin, scores="none", with_path=True, percent=percent)
        rows = list(corpus)
        if not rows:
            raise ValueError("sampled corpus is empty")
        pin = pin or rows[-1].row_id
        demo.create_schema(dest)
        last_log = 0
        for offset in range(0, len(rows), batch_size):
            batch = rows[offset:offset + batch_size]
            reports = data._reports(source, [row.row_id for row in batch])
            if set(reports) != {row.row_id for row in batch}:
                raise ValueError("capture lost rows within its database snapshot")
            for row in batch:
                item = reports[row.row_id]
                label = "bad" if row.label else "good"
                partitions[row.partition] += 1
                labels[label] += 1
                demo.add_report(dest, row.row_id, item["cleave_result"], label=label,
                                sha256=row.sha256, path=row.path or None,
                                mtime=item["mtime"] or None)
            now = time.monotonic()
            if now - last_log >= 30 or offset + len(batch) == len(rows):
                dest.commit()
                done = offset + len(batch)
                print(f"[freeze] {done}/{len(rows)} rows; {now-started:.1f}s", flush=True)
                last_log = now
    final = output / "corpus.sqlite"
    partial.rename(final)
    with final.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    manifest = dict(sample_percent=percent, snapshot_max_id=pin, rows=len(rows),
                    partitions=dict(partitions), labels=dict(labels), sha256=digest,
                    bytes=final.stat().st_size, wall_seconds=time.monotonic() - started)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2), flush=True)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--percent", default="1")
    parser.add_argument("--pin", type=int, default=0)
    args = parser.parse_args()
    freeze(args.db, args.output, percent=args.percent, pin=args.pin)


if __name__ == "__main__":
    main()
