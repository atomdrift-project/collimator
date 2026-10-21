"""Bounded sampling and cached, streaming feature-frequency audits."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import closing
from dataclasses import asdict
import hashlib
import json
import logging
import math
import os
from pathlib import Path
import time
from typing import Any

import numpy as np

from . import data, features

LOG = logging.getLogger(__name__)

def _digest(value: Any) -> str:
    def encode(obj: Any) -> Any:
        return sorted(obj) if isinstance(obj, (set, frozenset)) else str(obj)
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=encode).encode()).hexdigest()


def _database_stamp(db: str) -> dict[str, Any]:
    with data._connect(db) as conn:
        row = next(iter(data._execute(conn, f"SELECT MAX(id) FROM samples WHERE {data.LABELED_WHERE}")))
        stamp: dict[str, Any] = {"max_id": int(row[0] or 0)}
        if data._is_pg(db):
            changes = next(iter(data._execute(conn, (
                "SELECT n_tup_ins, n_tup_upd, n_tup_del FROM pg_stat_all_tables "
                "WHERE relid='samples'::regclass"
            ))), None)
            stamp["table_changes"] = list(changes) if changes is not None else None
        else:
            stat = Path(db).stat()
            stamp.update(size=stat.st_size, mtime_ns=stat.st_mtime_ns)
    return stamp


def _id_reservoir(conn: Any, db: str, filetype: str, max_id: int, capacity: int, seed: int) -> tuple[np.ndarray, int]:
    """Uniform sample via IID priorities, streaming only the covering index.

    Random ID seeks would bias the sample around ID gaps and ingestion batches.
    This scans IDs once, retaining O(sample size) IDs and priorities, then
    fetches hashes/labels only for that bounded reservoir.
    """
    marker = "%s" if data._is_pg(db) else "?"
    query = (
        f"SELECT id FROM samples WHERE {data.LABELED_WHERE} "
        f"AND file_type={marker} AND id<={marker} ORDER BY id"
    )
    cur = conn.cursor(name="allowlist_ids") if data._is_pg(db) else conn.cursor()
    rng = np.random.default_rng(seed)
    ids = np.empty(0, dtype=np.int64)
    priorities = np.empty(0, dtype=np.float64)
    scanned = 0
    last_progress = time.monotonic()
    with closing(cur):
        cur.execute(query, (filetype, max_id))
        while batch := cur.fetchmany(32768):
            incoming = np.fromiter((int(row[0]) for row in batch), dtype=np.int64, count=len(batch))
            ids = np.concatenate((ids, incoming))
            priorities = np.concatenate((priorities, rng.random(len(batch))))
            if len(ids) > capacity:
                keep = np.argpartition(priorities, capacity - 1)[:capacity]
                ids, priorities = ids[keep], priorities[keep]
            scanned += len(batch)
            if time.monotonic() - last_progress >= 10:
                LOG.info("sample %s: scanned %s indexed IDs", filetype, f"{scanned:,}")
                last_progress = time.monotonic()
    return ids[np.argsort(priorities, kind="stable")], scanned


def _sample_type(db: str, filetype: str, count: int, max_id: int, seed: int) -> list[tuple[int, int]]:
    started = time.monotonic()
    capacity = max(64, math.ceil(count * 1.5) + 32)
    with data._connect(db, repeatable_read=True) as conn:
        while True:
            ids, population = _id_reservoir(conn, db, filetype, max_id, capacity, seed)
            rows: dict[int, tuple[int, str]] = {}
            for offset in range(0, len(ids), 1000):
                chunk = [int(i) for i in ids[offset:offset + 1000]]
                if data._is_pg(db):
                    query = f"SELECT id, label, canonical_sha256, sha256 FROM samples WHERE {data.LABELED_WHERE} AND id=ANY(%s)"
                    params: Any = (chunk,)
                else:
                    marks = ",".join("?" for _ in chunk)
                    query = f"SELECT id, label, canonical_sha256, sha256 FROM samples WHERE {data.LABELED_WHERE} AND id IN ({marks})"
                    params = chunk
                for rid, label, canonical, sha in data._execute(conn, query, params):
                    rows[int(rid)] = (int(label == "bad"), str(canonical or sha))
            sample = [
                (int(rid), rows[int(rid)][0]) for rid in ids
                if int(rid) in rows and not data.is_test_sample(rows[int(rid)][1])
            ][:count]
            if len(sample) >= count or len(ids) >= population:
                LOG.info("sample %s: %s/%s training rows in %.1fs", filetype, f"{len(sample):,}", f"{population:,}", time.monotonic() - started)
                return sample
            # A test-heavy filetype may need a larger reservoir. Reusing the
            # same seed preserves the priority ordering of the first pass.
            capacity = min(population, capacity * 2)


def _sample_rows(args: Any, stamp: dict[str, Any]) -> list[tuple[int, int]]:
    rows: list[tuple[int, int]] = []
    workers = min(args.sampling_workers, len(args.filetypes))
    LOG.info("sampling %d filetypes with %d metadata workers", len(args.filetypes), workers)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending = [
            pool.submit(_sample_type, args.db, ft, args.sample_per_type, stamp["max_id"], args.seed + i)
            for i, ft in enumerate(args.filetypes)
        ]
        for result in as_completed(pending):
            rows.extend(result.result())
    return sorted(rows)


def _filetypes(db: str, max_id: int) -> list[str]:
    """Walk distinct types with one covering-index seek per type."""
    marker = "%s" if data._is_pg(db) else "?"
    query = (
        f"SELECT file_type FROM samples WHERE {data.LABELED_WHERE} "
        f"AND file_type>{marker} AND id<={marker} ORDER BY file_type LIMIT 1"
    )
    types: list[str] = []
    with data._connect(db) as conn:
        while row := next(iter(data._execute(conn, query, (types[-1] if types else "", max_id))), None):
            types.append(str(row[0]))
    return types


def _workers(args: Any, rows: int) -> int:
    return max(1, min(args.workers or os.cpu_count() or 1, args.max_db_workers, max(1, math.ceil(rows / args.batch_size))))


def count_frequencies(args: Any, sample: list[tuple[int, int]], spec: features.FeatureSpec) -> np.ndarray:
    counts = np.zeros(spec.total_features, dtype=np.int64)
    workers = _workers(args, len(sample))
    LOG.info("extracting %s sampled rows: %d workers, batch size %d", f"{len(sample):,}", workers, args.batch_size)
    completed = 0
    started = last_progress = time.monotonic()
    for matrix, _labels in features.extract_labeled_from_db_batches(
        args.db, sample, spec, n_workers=workers, batch_size=args.batch_size,
    ):
        # CSR construction coalesces duplicate entries. This equals
        # (X != 0).sum(axis=0), without materializing the whole corpus matrix.
        counts += np.bincount(matrix.indices[matrix.data != 0], minlength=spec.total_features)
        completed += matrix.shape[0]
        if time.monotonic() - last_progress >= 5 or completed == len(sample):
            LOG.info("frequency extraction: %s/%s rows in %.1fs", f"{completed:,}", f"{len(sample):,}", time.monotonic() - started)
            last_progress = time.monotonic()
    if completed != len(sample):
        raise RuntimeError(f"frequency extraction returned {completed}/{len(sample)} sampled rows; cache not saved")
    return counts


def frequency_counts(args: Any) -> tuple[list[str], np.ndarray, dict[str, Any]]:
    """Discover and count current candidates, independent of deployed models.

    Cache names with counts: an old spec must never define the search space.
    Only non-test rows enter either vocabulary discovery or frequency counts.
    """
    stamp = _database_stamp(args.db)
    if not args.filetypes:
        args.filetypes = _filetypes(args.db, stamp["max_id"])
    if not args.filetypes:
        raise RuntimeError("no labeled filetypes available for feature discovery")
    inputs = {
        "version": 2,
        "database": _digest(str(args.db)),  # Keep credentials out of metadata.
        "dataset": stamp,
        "feature_config": asdict(features.feature_config_from_env()),
        "extractor": hashlib.sha256(Path(features.__file__).read_bytes()).hexdigest(),
        "sampler": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "filetypes": args.filetypes, "sample_per_type": args.sample_per_type, "seed": args.seed,
    }
    key = _digest(inputs)
    path = args.cache_dir / f"frequency-{key}.npz"
    if not args.refresh and path.is_file() and time.time() - path.stat().st_mtime <= args.cache_max_age:
        try:
            with np.load(path, allow_pickle=False) as cached:
                names = cached["names"].tolist()
                counts = cached["counts"]
                meta = json.loads(str(cached["metadata"].item()))
                if names and all(isinstance(n, str) for n in names) and counts.shape == (len(names),) and np.issubdtype(counts.dtype, np.integer) and np.all(counts >= 0):
                    LOG.info("frequency cache hit: %s (%s sampled rows)", path.name, f"{meta['sample_rows']:,}")
                    return names, counts, {**meta, "cache_hit": True}
        except (OSError, ValueError, KeyError) as exc:
            LOG.warning("ignoring unreadable frequency cache: %s", exc)
    sample = _sample_rows(args, stamp)
    if not sample:
        raise RuntimeError("no eligible non-test samples; refusing an empty frequency audit")
    # Auxiliary vocab scans use a bounded prefix of the sample. Shuffle it so
    # those scans see a mix of filetypes and ages, rather than the oldest IDs.
    np.random.default_rng(args.seed).shuffle(sample)
    previous = os.environ.pop("COLLIMATOR_ALLOWED_FEATURES_FILE", None)
    try:
        LOG.info("discovering vocabulary from %s training rows", f"{len(sample):,}")
        spec = features.build_vocab_from_db(args.db, sample, n_workers=_workers(args, len(sample)))
    finally:
        if previous is not None:
            os.environ["COLLIMATOR_ALLOWED_FEATURES_FILE"] = previous
    names = spec.feature_names
    counts = count_frequencies(args, sample, spec)
    meta = {"sample_rows": len(sample), "dataset": stamp, "cache_key": key, "cache_hit": False, "sampling": "uniform indexed-ID priority reservoir v1"}
    if _database_stamp(args.db) != stamp:
        LOG.warning("dataset changed during audit; counts will not be cached")
        return names, counts, meta
    args.cache_dir.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("wb") as out:
        np.savez(out, names=np.asarray(names), counts=counts, sample=np.asarray(sample, dtype=np.int64), metadata=json.dumps(meta))
    temporary.replace(path)
    LOG.info("saved frequency cache: %s", path)
    return names, counts, meta
