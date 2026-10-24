#!/usr/bin/env python3
"""Freeze a hash-sampled corpus for repeatable, fresh pipeline experiments."""

import argparse
from collections import Counter
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import sqlite3
import time

from collimator import data


COLUMNS = ("id", "sha256", "path", "label", "canonical_sha256", "cleave_result",
           "formula", "elements", "score", "mtime", "file_type", "skip")


def sqlite_value(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    if isinstance(value, (date, datetime)):
        return str(value)
    return value


def freeze(db, output, *, percent="1", pin=0, batch_size=128):
    predicate = data.sample_predicate(percent)
    if pin < 0 or batch_size < 1:
        raise ValueError("pin must be nonnegative and batch size must be positive")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    partial = output / "corpus.partial.sqlite"
    started = time.monotonic()
    partitions = Counter()
    labels = Counter()
    where = "label IN ('bad', 'good') AND cleave_result IS NOT NULL AND skip = ''"
    if predicate:
        where += f" AND ({predicate})"
    with data._connect(db, repeatable_read=True) as source, sqlite3.connect(partial) as dest:
        pg = not isinstance(source, sqlite3.Connection)
        if pg:
            source.execute("SET TRANSACTION READ ONLY")
        if not pin:
            pin = int(next(data._execute(source, "SELECT MAX(id) FROM samples WHERE " + where))[0] or 0)
        if not pin:
            raise ValueError("sampled corpus is empty")
        # First use the replica's covering sample index; then fetch reports in
        # bounded batches, all under the same read-only database snapshot.
        marker = "%s" if pg else "?"
        ids = [int(row[0]) for row in data._execute(
            source, f"SELECT id FROM samples WHERE {where} AND id <= {marker} ORDER BY id", (pin,))]
        if not ids:
            raise ValueError("sampled corpus is empty at this pin")
        dest.execute("CREATE TABLE samples (id INTEGER PRIMARY KEY, sha256 TEXT, path TEXT, "
                     "label TEXT, canonical_sha256 TEXT, cleave_result TEXT, formula TEXT, "
                     "elements TEXT, score REAL, mtime REAL, file_type TEXT, skip TEXT)")
        last_log = 0
        for offset in range(0, len(ids), batch_size):
            batch = ids[offset:offset + batch_size]
            query = f"SELECT {', '.join(COLUMNS)} FROM samples WHERE "
            if pg:
                rows = list(data._execute(source, query + "id = ANY(%s)", (batch,)))
            else:
                rows = list(data._execute(source, query + f"id IN ({','.join('?' for _ in batch)})", batch))
            if {int(row[0]) for row in rows} != set(batch):
                raise ValueError("capture lost rows within its database snapshot")
            for row in rows:
                partitions[data.partition_of(row[4] or row[1])] += 1
                labels[row[3]] += 1
            dest.executemany("INSERT INTO samples VALUES (" + ",".join("?" for _ in COLUMNS) + ")",
                             [tuple(sqlite_value(v) for v in row)
                              for row in rows])
            now = time.monotonic()
            if now - last_log >= 30 or offset + len(batch) == len(ids):
                dest.commit()
                print(f"[freeze] {offset + len(batch)}/{len(ids)} rows; {now-started:.1f}s", flush=True)
                last_log = now
        dest.execute("CREATE INDEX samples_filetype_id ON samples(file_type, id)")
        dest.commit()
    final = output / "corpus.sqlite"
    partial.rename(final)
    with final.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    manifest = dict(sample_percent=percent, snapshot_max_id=pin, rows=len(ids),
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
