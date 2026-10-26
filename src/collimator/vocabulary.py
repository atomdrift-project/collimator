"""Exact document frequencies with a bounded write cache and disk overflow.

N-grams use packed token IDs rather than repeating long taxonomy paths in every
SQLite key. Workers own disjoint documents; their files are merged by token
identity. No frequency counts are discarded under memory pressure.
"""

from __future__ import annotations

from .profiling import event, timed

import heapq
import hashlib
import json
import logging
import os
import sqlite3
import struct
import time
from collections import OrderedDict
from collections.abc import Iterable
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from dataclasses import dataclass
from itertools import combinations, islice, repeat
from math import comb
import multiprocessing
from pathlib import Path
import tempfile
import uuid

_SIGNATURE_REDUCE_KEYS = 262_144
_PARALLEL_MATERIALIZE_KEYS = 1_000_000


def _token_hash(token: str) -> int:
    return int.from_bytes(hashlib.blake2s(token.encode(), digest_size=4).digest(), "big")


def _ids(key: bytes) -> tuple[int, ...]:
    return struct.unpack(f">{len(key) // 4}I", key)


def _name(key: bytes, tokens: dict[int, str]) -> str:
    return " + ".join(tokens[i] for i in _ids(key))


def _packed_remapper(mapping: dict[int, int]):
    """Remap packed IDs without unpacking/repacking each combination in Python.

    The source B-tree visits adjacent keys with the same prefix. Retain just
    that prefix, so most triples need one token lookup and one concatenation.
    The cache is constant-sized and remains correct for unordered input too.
    """
    pack = struct.Struct(">I").pack
    words = {pack(old): pack(new) for old, new in mapping.items()}
    last_prefix = None
    last_mapped = b""

    def remap(key: bytes) -> bytes:
        nonlocal last_prefix, last_mapped
        prefix = key[:-4]
        if prefix != last_prefix:
            last_mapped = b"".join(words[prefix[i:i + 4]] for i in range(0, len(prefix), 4))
            last_prefix = prefix
        return last_mapped + words[key[-4:]]

    return remap


def _source_identity(path):
    info = Path(path).stat()
    return [info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns]


def _attach_count_sources(db, token_ids, entries):
    """Attach immutable counts and normalize only token dictionaries in RAM."""
    sources = []
    try:
        for i, entry in enumerate(entries):
            if _source_identity(entry["path"]) != entry["identity"]:
                raise ValueError("shared count source was replaced or changed; use a new checkpoint")
            alias = f"shared_counts_{i}"
            db.execute(f"ATTACH DATABASE ? AS {alias}",
                       (Path(entry["path"]).resolve().as_uri() + "?mode=ro",))
            source = dict(alias=alias, key="token", reverse=None, families={})
            sources.append(source)
            actual = [row[0] for row in db.execute(f"SELECT id FROM {alias}.batches ORDER BY id")]
            if actual != entry["receipts"]:
                raise ValueError("shared count source receipts changed")
            mapping = {old:token_ids[token] for old, token in db.execute(f"SELECT id,token FROM {alias}.tokens")}
            if any(old != new for old,new in mapping.items()):
                function = f"shared_remap_{i}"
                db.create_function(function, 1, _packed_remapper(mapping), deterministic=True)
                source.update(key=f"{function}(token)", reverse={new:old for old,new in mapping.items()})
    except BaseException:
        for source in sources:
            db.execute(f"DETACH DATABASE {source['alias']}")
        raise
    return sources


def _frequency_query(db, sources, family, prefix=None):
    """Sum full frequencies before filtering; never truncate a source top-k.

    Range predicates use each source's own token IDs, preserving indexed
    prefix lookup even when collision handling assigned different local IDs.
    """
    selections, parameters = [], []
    for source in sources:
        alias = source["alias"]
        present = source["families"]
        if family not in present:
            present[family] = db.execute(f"SELECT 1 FROM {alias}.counts WHERE family=? LIMIT 1", (family,)).fetchone() is not None
        if not present[family]:
            continue
        query = f"SELECT {source['key']} AS token,n FROM {alias}.counts WHERE family=?"
        args = [family]
        if prefix is not None:
            local_prefix = prefix
            if source["reverse"] is not None:
                try:
                    local_prefix = struct.pack(">II", *(source["reverse"][i] for i in _ids(prefix)))
                except KeyError:
                    continue
            query += " AND token>=? AND token<=?"
            args.extend((local_prefix+b"\0"*4, local_prefix+b"\xff"*4))
        selections.append(query)
        parameters.extend(args)
    if not selections:
        return "SELECT token,n FROM main.counts WHERE 0", ()
    if len(selections) == 1:
        return selections[0], tuple(parameters)
    return "SELECT token,SUM(n) AS n FROM (" + " UNION ALL ".join(selections) + ") GROUP BY token", tuple(parameters)


@dataclass(frozen=True)
class CountView:
    """A completed worker's counts, transferred by filename rather than IPC."""
    path: str
    family: str

    def items(self):
        db = sqlite3.connect(Path(self.path).resolve().as_uri() + "?mode=ro", uri=True)
        try:
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='signatures'").fetchone() and db.execute(
                "SELECT 1 FROM signatures LIMIT 1"
            ).fetchone():
                raise ValueError("deferred vocabulary must be materialized before reading counts")
            tokens = dict(db.execute("SELECT id, token FROM tokens"))
            state = db.execute("SELECT value FROM state WHERE key='readonly_sources'").fetchone()
            sources = [dict(alias="main", key="token", reverse=None, families={})]
            sources += _attach_count_sources(db, {token:i for i,token in tokens.items()}, json.loads(state[0]) if state else [])
            query,args = _frequency_query(db, sources, self.family)
            for key, n in db.execute(query,args):
                yield _name(key, tokens), n
        finally:
            db.close()


def _materialize_partition(source: str, output: str, partition: int, partitions: int, marker: str):
    """Expand a disjoint signature partition into an independently written DB."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    cache_mib = int(os.getenv("COLLIMATOR_VOCAB_REDUCE_CACHE_MIB", "256"))
    if not 1 <= cache_mib <= 1024:
        raise ValueError("COLLIMATOR_VOCAB_REDUCE_CACHE_MIB must be between 1 and 1024")
    with sqlite3.connect(Path(source).resolve().as_uri() + "?mode=ro", uri=True) as db:
        with VocabularyCounts(output, cache_size_mib=cache_mib) as counts:
            counts.tokens = dict(db.execute("SELECT id, token FROM tokens"))
            counts.token_ids = {token: i for i, token in counts.tokens.items()}
            counts.db.executemany("INSERT INTO tokens VALUES (?,?)", counts.tokens.items())
            strategy = os.getenv("COLLIMATOR_VOCAB_REDUCER", "sorted")
            if strategy not in ("upsert", "sorted"):
                raise ValueError("COLLIMATOR_VOCAB_REDUCER must be upsert or sorted")
            started = last_progress = time.monotonic()
            expanded = selected = 0
            counts._reduce_keys = int(os.getenv("COLLIMATOR_VOCAB_REDUCE_KEYS", "1048576"))
            if not 1 <= counts._reduce_keys <= 4194304:
                raise ValueError("COLLIMATOR_VOCAB_REDUCE_KEYS must be between 1 and 4194304")
            counts._expansion_progress = (partition, partitions, started)
            if strategy == "sorted":
                from .vocabulary_runs import SignatureRuns
                counts._signature_runs = SignatureRuns(Path(output).parent)
            for family, order, packed, n in db.execute("SELECT family, gram_order, token, n FROM signatures"):
                bucket = int.from_bytes(hashlib.blake2s(
                    family.encode() + bytes([order]) + packed, digest_size=4).digest(), "big") % partitions
                if bucket != partition:
                    continue
                selected += 1
                expanded += comb(len(packed) // 4, order)
                counts.signatures[family, order, packed] = n
                counts.signature_size += len(packed) + 256
                counts.signature_documents += n
                if counts.signature_size >= counts.signature_bytes:
                    counts.flush_signatures()
                    now = time.monotonic()
                    if now - last_progress >= 30:
                        logging.getLogger(__name__).info(
                            "vocab expansion partition %d/%d: %d sets, %d combinations, %.1fs elapsed",
                            partition + 1, partitions, selected, expanded, now - started)
                        last_progress = now
            counts.flush()
            if counts._signature_runs is not None:
                counts._signature_runs.finish(counts.db)
                counts._signature_runs.close()
                counts._signature_runs = None
            counts.record_batch(marker, None, 0)
            logging.getLogger(__name__).info(
                "vocab expansion partition %d/%d complete: %d sets, %d combinations, %.1fs elapsed",
                partition + 1, partitions, selected, expanded, time.monotonic() - started)
    return CountView(output, "")


class VocabularyCounts:
    """Count contiguous documents; never revisit a document after the next one.

    ``merge`` consumes all families in a completed worker file, then removes
    it. The caller owns scratch-directory cleanup on failure. Token dictionaries
    scale with individual paths; only the much larger combination table spills.
    """

    def __init__(self, path: str = "", buffer_size: int = 100_000,
                 *, check_same_thread: bool = True, durable: bool = False,
                 resume: bool = False, cache_size_mib: int = 32,
                 signature_bytes: int = 8 * 1024 * 1024,
                 bulk_signatures: bool = True, stable_token_ids: bool = True,
                 defer_signatures: bool = False, materialize_workers: int = 1,
                 materialize_merge_size: int = 1) -> None:
        self.path = path
        self._signature_runs = None
        self._reduce_keys = _SIGNATURE_REDUCE_KEYS
        self._expansion_progress = None
        self._expanded_combinations = 0
        self._last_expansion_log = time.monotonic()
        self.buffer_size = max(1, buffer_size)
        # Per key: count, first document, last document since the last write.
        self.pending: OrderedDict[tuple[str, bytes], list] = OrderedDict()
        # Retain compact token-set signatures across fetch batches. Expanding
        # one repeated set once is much cheaper than aggregating its millions
        # of repeated combinations. This cache is independent of report size.
        self.signatures: dict[tuple[str, int, bytes], int] = {}
        self.signature_bytes = max(0, signature_bytes)
        self.signature_size = 0
        self.signature_documents = 0
        self.bulk_signatures = bulk_signatures
        self.stable_token_ids = stable_token_ids
        self.defer_signatures = defer_signatures
        self.materialize_workers = max(1, materialize_workers)
        self.materialize_merge_size = max(1, min(8, materialize_merge_size))
        self._readonly_sources = None
        self._qualified_frequencies = {}
        self.token_ids: dict[str, int] = {}
        self.tokens: dict[int, str] = {}
        self.db = sqlite3.connect(path, uri=True, check_same_thread=check_same_thread)
        self.db.execute(f"PRAGMA cache_size={-1024 * max(1, int(cache_size_mib))}")
        self.db.execute("PRAGMA temp_store=FILE")
        self.db.execute(f"PRAGMA journal_mode={'WAL' if durable else 'OFF'}")
        self.db.execute(f"PRAGMA synchronous={'FULL' if durable else 'OFF'}")
        create = "CREATE TABLE IF NOT EXISTS" if resume else "CREATE TABLE"
        self.db.execute(f"{create} tokens (id INTEGER PRIMARY KEY, token TEXT NOT NULL)")
        self.db.execute(
            f"{create} counts (family TEXT, token BLOB, n INTEGER NOT NULL,"
            " first_document INTEGER, document INTEGER, PRIMARY KEY (family, token)) WITHOUT ROWID"
        )
        self.db.execute(f"{create} batches (id TEXT PRIMARY KEY, summary TEXT, n_rows INTEGER)")
        self.db.execute(f"{create} state (key TEXT PRIMARY KEY, value TEXT)")
        self.db.execute(
            f"{create} signatures (family TEXT, gram_order INTEGER, token BLOB, n INTEGER NOT NULL,"
            " PRIMARY KEY (family, gram_order, token)) WITHOUT ROWID"
        )
        if resume:
            self.tokens = dict(self.db.execute("SELECT id, token FROM tokens"))
            self.token_ids = {token: i for i, token in self.tokens.items()}

    def record_batch(self, batch_id: str, summary, n_rows: int) -> None:
        # CountView descriptors aren't needed to restore scalar summaries.
        scalar = [None if isinstance(value, CountView) else value for value in summary] if summary else None
        self.db.execute("INSERT INTO batches VALUES (?, ?, ?)",
                        (batch_id, json.dumps(scalar), n_rows))

    def completed_batches(self, prefix: str):
        return self.db.execute("SELECT id, summary, n_rows FROM batches WHERE id LIKE ?",
                               (prefix + ":%",))

    def state(self, key: str, default=None):
        row = self.db.execute("SELECT value FROM state WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set_state(self, key: str, value) -> None:
        self.db.execute("INSERT OR REPLACE INTO state VALUES (?, ?)", (key, json.dumps(value)))
        self.db.commit()

    def __enter__(self) -> VocabularyCounts:
        return self

    def __exit__(self, *exc) -> None:
        if exc[0] is not None:
            self.db.close()
            if self._signature_runs is not None:
                self._signature_runs.close()
                self._signature_runs = None
            return
        self.close()

    def close(self) -> None:
        try:
            self.flush()
        finally:
            self.db.close()

    def _token_id(self, token: str) -> int:
        index = self.token_ids.get(token)
        if index is None:
            # Common token identities now agree across workers. This makes the
            # usual merge a sorted INSERT SELECT, with no Python remap callback
            # or external sort. A hash is only an allocation hint: retain full
            # strings and resolve collisions, never conflate their counts.
            index = _token_hash(token) if self.stable_token_ids else len(self.token_ids)
            while index in self.tokens:
                index = (index + 1) & 0xFFFFFFFF
            self.token_ids[token] = index
            self.tokens[index] = token
            self.db.execute("INSERT INTO tokens VALUES (?, ?)", (index, token))
        return index

    def increment(self, family: str, token: str | tuple[str, ...], n: int = 1,
                  *, document: int | None = None) -> None:
        parts = token.split(" + ") if isinstance(token, str) else token
        key = (family, struct.pack(f">{len(parts)}I", *(self._token_id(p) for p in parts)))
        self._increment_key(key, n, document)

    def increment_combinations(self, family: str, tokens: Iterable[str], order: int,
                               document: int | None, benign_family: str = "", *, n: int = 1) -> None:
        """Count a file, or add n pre-aggregated samples when document is None."""
        # Resolve paths once per file rather than for every pair/triple.
        ids = [self._token_id(token) for token in tokens]
        pack = struct.Struct(f">{order}I").pack
        for parts in combinations(ids, order):
            packed = pack(*parts)
            self._increment_key((family, packed), n, document)
            if benign_family:
                self._increment_key((benign_family, packed), n, document)

    def group_combinations(self, family: str, tokens: Iterable[str], order: int,
                           *, n: int = 1) -> None:
        """Queue n distinct single-set documents; multi-file unions stay explicit."""
        ids = tuple(self._token_id(token) for token in tokens)
        if len(ids) < order:
            return
        packed = struct.pack(f">{len(ids)}I", *ids)
        key = family, order, packed
        if key not in self.signatures:
            # Includes dict/tuple/bytes/int overhead, with conservative slack.
            self.signature_size += len(packed) + 256
        self.signatures[key] = self.signatures.get(key, 0) + n
        self.signature_documents += n
        if self.signature_size >= self.signature_bytes:
            self.flush_signatures()

    @timed("vocabulary.signatures")
    def flush_signatures(self) -> None:
        if not self.signatures:
            return
        event("vocabulary.signatures", "counts", documents=self.signature_documents,
              signatures=len(self.signatures), estimated_bytes=self.signature_size)
        if self.defer_signatures:
            if self.state("materialization"):
                raise ValueError("finish interrupted materialization before adding signatures")
            # A signature represents complete, distinct single-set documents.
            # Merge these weights globally before expanding any combinations.
            self.db.executemany(
                "INSERT INTO signatures VALUES (?, ?, ?, ?) ON CONFLICT(family, gram_order, token)"
                " DO UPDATE SET n=n+excluded.n",
                ((*key, n) for key, n in self.signatures.items()),
            )
            self.db.commit()
            self.signatures.clear()
            self.signature_size = self.signature_documents = 0
            return
        if self.bulk_signatures:
            self._flush_pending()
            self._reduce_signatures()
            self.signature_size = self.signature_documents = 0
            return
        while self.signatures:
            (family, order, packed), n = self.signatures.popitem()
            pack = struct.Struct(f">{order}I").pack
            for parts in combinations(_ids(packed), order):
                self._increment_key((family, pack(*parts)), n, None)
        self.signature_size = self.signature_documents = 0

    def _reduce_signatures(self, *, commit: bool = True) -> None:
        """Expand and sort bounded packed arrays in native code, then bulk UPSERT.

        Each queued signature represents complete, distinct documents. Explicit
        multi-file unions have already been flushed, so adding these weights
        must not participate in the last-document deduplication bookkeeping.
        """
        import numpy as np

        limit = self._reduce_keys
        families = sorted({(family, order) for family, order, _ in self.signatures})
        for family, order in families:
            arrays, weights, buffered = [], [], 0

            def write():
                nonlocal arrays, weights, buffered
                if not buffered:
                    return
                keys = np.concatenate(arrays)
                values = np.concatenate(weights)
                permutation = np.argsort(keys)
                keys, values = keys[permutation], values[permutation]
                starts = np.r_[0, np.flatnonzero(keys[1:] != keys[:-1]) + 1]
                totals = np.add.reduceat(values, starts)
                self._expanded_combinations += buffered
                if self._expansion_progress is not None and time.monotonic() - self._last_expansion_log >= 30:
                    part, parts, started = self._expansion_progress
                    logging.getLogger(__name__).info(
                        "vocab expansion partition %d/%d: %d combinations reduced, %.1fs elapsed",
                        part + 1, parts, self._expanded_combinations, time.monotonic() - started)
                    self._last_expansion_log = time.monotonic()
                if self._signature_runs is not None:
                    self._signature_runs.add(family, keys[starts], totals)
                    arrays, weights, buffered = [], [], 0
                    return
                self.db.executemany(
                    "INSERT INTO counts VALUES (?, ?, ?, NULL, NULL)"
                    " ON CONFLICT(family, token) DO UPDATE SET n=n+excluded.n,"
                    " first_document=NULL, document=NULL",
                    zip(repeat(family), keys[starts].tolist(), totals.tolist()),
                )
                if commit:
                    self.db.commit()
                arrays, weights, buffered = [], [], 0

            # Copy only signature references, never the expanded combinations.
            for key in [key for key in self.signatures if key[:2] == (family, order)]:
                n = self.signatures.pop(key)
                ids = _ids(key[2])
                remaining = comb(len(ids), order)
                parts = combinations(ids, order)
                while remaining:
                    size = min(remaining, limit - buffered)
                    array = np.fromiter(islice(parts, size), dtype=np.dtype((">u4", order)), count=size)
                    arrays.append(array.view(f"V{4 * order}").reshape(-1))
                    weights.append(np.full(size, n, dtype=np.int64))
                    buffered += size
                    remaining -= size
                    if buffered == limit:
                        write()
            write()

    @timed("vocabulary.materialize")
    def materialize(self) -> None:
        """Expand globally reduced signatures, with atomic recovery per batch.

        Count increments and removal of their source signatures commit together.
        A killed expansion can therefore be repeated without double counting.
        Explicit multi-file document unions remain on the existing exact path.
        """
        self.flush()
        total, documents = self.db.execute("SELECT count(*), COALESCE(sum(n),0) FROM signatures").fetchone()
        if not total:
            return
        event("vocabulary.materialize", "counts", signatures=total, documents=documents)
        plan = self.state("materialization")
        expansion_keys = sum(comb(size // 4, order) for size, order in self.db.execute(
            "SELECT length(token), gram_order FROM signatures"))
        if plan or (self.path and self.materialize_workers > 1 and expansion_keys >= _PARALLEL_MATERIALIZE_KEYS):
            self._materialize_parallel(plan, total, documents)
            return
        completed, last_log = 0, 0.0
        while available := self.db.execute(
            "SELECT family, gram_order, token, n FROM signatures ORDER BY 1,2,3 LIMIT 256"
        ).fetchall():
            batch, combinations_pending = [], 0
            for row in available:
                batch.append(row)
                combinations_pending += comb(len(row[2]) // 4, row[1])
                if combinations_pending >= _SIGNATURE_REDUCE_KEYS:
                    break
            self.signatures = {(family, order, key): n for family, order, key, n in batch}
            try:
                self.db.execute("BEGIN")
                self._reduce_signatures(commit=False)
                self.db.executemany("DELETE FROM signatures WHERE family=? AND gram_order=? AND token=?",
                                    (row[:3] for row in batch))
                self.db.commit()
                completed += len(batch)
                now = time.monotonic()
                if now - last_log >= 30 or completed == total:
                    logging.getLogger(__name__).info(
                        "vocab signature expansion: %d/%d unique sets (%d document occurrences)",
                        completed, total, documents)
                    last_log = now
            except BaseException:
                self.db.rollback()
                raise
            finally:
                self.signatures.clear()
                self.signature_size = self.signature_documents = 0

    def _materialize_parallel(self, plan, total, documents):
        if not plan:
            plan = {"id": uuid.uuid4().hex, "partitions": min(total, self.materialize_workers)}
            self.set_state("materialization", plan)
        parts = plan["partitions"]
        markers = {part: f"materialize:{plan['id']}:{part}" for part in range(parts)}
        remaining = [part for part, marker in markers.items()
                     if not self.db.execute("SELECT 1 FROM batches WHERE id=?", (marker,)).fetchone()]
        logging.getLogger(__name__).info(
            "vocab parallel expansion: %d sets (%d document occurrences), %d/%d partitions remaining",
            total, documents, len(remaining), parts)
        if remaining:
            # Persistent signatures are retained until every partition commits.
            # Each final merge atomically records its unique receipt with counts.
            with tempfile.TemporaryDirectory(prefix="materialize-", dir=Path(self.path).resolve().parent) as scratch:
                with ProcessPoolExecutor(max_workers=min(self.materialize_workers, len(remaining)),
                                         mp_context=multiprocessing.get_context("spawn")) as pool:
                    jobs = {pool.submit(_materialize_partition, self.path, str(Path(scratch)/f"{part}.sqlite"),
                                        part, parts, markers[part]): part for part in remaining}
                    ready = []
                    pending = set(jobs)
                    committed = parts - len(remaining)
                    started = time.monotonic()
                    while pending:
                        done, pending = wait(pending, timeout=30, return_when=FIRST_COMPLETED)
                        if not done:
                            logging.getLogger(__name__).info(
                                "vocab expansion: %d/%d partitions checkpointed; %d running/queued, %.1fs elapsed",
                                committed, parts, len(pending), time.monotonic() - started)
                        for job in done:
                            ready.append(job.result())
                            if len(ready) == self.materialize_merge_size:
                                logging.getLogger(__name__).info(
                                    "vocab expansion: merging %d completed partitions (%d/%d checkpointed)",
                                    len(ready), committed, parts)
                                self.merge_many(ready)
                                committed += len(ready)
                                logging.getLogger(__name__).info(
                                    "vocab expansion: %d/%d partitions checkpointed, %.1fs elapsed",
                                    committed, parts, time.monotonic() - started)
                                ready.clear()
                    if ready:
                        logging.getLogger(__name__).info(
                            "vocab expansion: merging %d completed partitions (%d/%d checkpointed)",
                            len(ready), committed, parts)
                        self.merge_many(ready)
                        committed += len(ready)
                        logging.getLogger(__name__).info(
                            "vocab expansion: %d/%d partitions checkpointed, %.1fs elapsed",
                            committed, parts, time.monotonic() - started)
        self.db.execute("DELETE FROM signatures")
        self.db.execute("DELETE FROM state WHERE key='materialization'")
        self.db.commit()

    def _increment_key(self, key: tuple[str, bytes], n: int, document: int | None) -> None:
        pending = self.pending.get(key)
        if pending is None:
            self.pending[key] = [n if document is None else 1, document, document]
        else:
            if document is None or pending[2] is None or pending[2] != document:
                pending[0] += n if document is None else 1
            pending[2] = document
            self.pending.move_to_end(key)
        if len(self.pending) >= self.buffer_size:
            # Keep recently used keys, including counts accumulated across
            # documents. Flushing by document would rewrite common keys often.
            self._flush_pending(max(1, self.buffer_size // 4))

    def flush(self, limit: int | None = None) -> None:
        self.flush_signatures()
        self._flush_pending(limit)

    def _flush_pending(self, limit: int | None = None) -> None:
        def rows():
            for _ in range(len(self.pending) if limit is None else min(limit, len(self.pending))):
                (family, key), (n, first, last) = self.pending.popitem(last=False)
                yield family, key, n, first, last

        self.db.executemany(
            "INSERT INTO counts VALUES (?, ?, ?, ?, ?)"
            " ON CONFLICT(family, token) DO UPDATE SET"
            " n=n+excluded.n-CASE WHEN document=excluded.first_document THEN 1 ELSE 0 END,"
            " first_document=excluded.first_document, document=excluded.document",
            rows(),
        )
        self.db.commit()

    def view(self, family: str, *, flush: bool = True):
        # Active shards transfer only descriptors. Their owner flushes before
        # sealing, so keep the write cache warm between input batches.
        if flush or not self.path:
            self.materialize()
        if self.path:
            return CountView(self.path, family)
        return {_name(key, self.tokens): n for _,key,n in self.iter_counts(family)}

    @timed("vocabulary.merge")
    def merge(self, view: CountView, *, consume: bool = True) -> None:
        self.flush()
        self.db.execute("ATTACH DATABASE ? AS vocab_batch",
                        (Path(view.path).resolve().as_uri() + "?mode=ro",))
        try:
            state = self.db.execute("SELECT value FROM vocab_batch.state WHERE key='readonly_sources'").fetchone()
            if state and json.loads(state[0]):
                raise ValueError("cannot merge a composite count view; attach its original sources")
            incoming = list(self.db.execute("SELECT id FROM vocab_batch.batches"))
            seen = sum(self.db.execute("SELECT 1 FROM batches WHERE id=?", row).fetchone()
                       is not None for row in incoming)
            if seen:
                if seen != len(incoming):
                    raise ValueError("overlapping vocabulary checkpoint batches")
                return  # An already committed shard must never count twice.
            mapping = {i: self._token_id(token) for i, token in self.db.execute(
                "SELECT id, token FROM vocab_batch.tokens",
            )}
            if all(old == new for old, new in mapping.items()):
                # Identical dictionaries already have destination key order.
                # Avoid a Python callback per row and an external re-sort.
                key, ordering = "token", "family, token"
            else:
                self.db.create_function("vocab_remap", 1, _packed_remapper(mapping), deterministic=True)
                key, ordering = "vocab_remap(token)", "family, mapped"
            # Different worker dictionaries need a sort after remapping so
            # destination B-tree pages are visited sequentially. SQLite spills
            # the sort to disk instead of materializing it in Python.
            self.db.execute(
                "INSERT INTO counts"
                f" SELECT family, {key} AS mapped, n, NULL, NULL"
                f" FROM vocab_batch.counts WHERE true ORDER BY {ordering}"
                " ON CONFLICT(family, token) DO UPDATE SET n=n+excluded.n,"
                " first_document=NULL, document=NULL",
            )
            if self.db.execute(
                "SELECT 1 FROM vocab_batch.sqlite_master WHERE type='table' AND name='signatures'"
            ).fetchone():
                if self.state("materialization") and self.db.execute(
                    "SELECT 1 FROM vocab_batch.signatures LIMIT 1"
                ).fetchone():
                    raise ValueError("finish interrupted materialization before merging signatures")
                signature_order = "family, gram_order, token" if key == "token" else "family, gram_order, mapped"
                self.db.execute(
                    "INSERT INTO signatures"
                    f" SELECT family, gram_order, {key} AS mapped, n FROM vocab_batch.signatures"
                    f" WHERE true ORDER BY {signature_order}"
                    " ON CONFLICT(family, gram_order, token) DO UPDATE SET n=n+excluded.n"
                )
            # Counts and their completion markers commit together. A killed
            # merge rolls both back, so a restart can safely repeat its batch.
            self.db.execute("INSERT INTO batches SELECT * FROM vocab_batch.batches")
            self.db.commit()
            event("vocabulary.merge", "counts", batches=len(incoming),
                  phase=incoming[0][0].split(":")[0] if incoming else "unknown",
                  token_dictionary=len(mapping), source_bytes=Path(view.path).stat().st_size,
                  remapped=any(old != new for old, new in mapping.items()))
        except BaseException:
            self.db.rollback()
            raise
        finally:
            self.db.execute("DETACH DATABASE vocab_batch")
            self.db.create_function("vocab_remap", 1, None)
        if consume:
            Path(view.path).unlink()

    @timed("vocabulary.merge_many")
    def merge_many(self, views: Iterable[CountView]) -> None:
        """Sort/reduce up to eight closed shards before touching the large DB.

        Counts, signatures and receipts commit together for each bounded group.
        Completed groups may be retried; partial receipt overlap is an error.
        The SQL sort spills to disk under SQLite's configured memory budget.
        """
        source = iter(views)
        while batch := list(islice(source, 8)):
            if len(batch) == 1:
                self.merge(batch[0])
                continue
            self.flush()
            attached, functions, consumed = [], [], []
            selections, signatures, receipts = [], [], []
            incoming_ids = set()
            try:
                for i, view in enumerate(batch):
                    alias = f"vocab_group_{i}"
                    self.db.execute(f"ATTACH DATABASE ? AS {alias}",
                                    (Path(view.path).resolve().as_uri() + "?mode=ro",))
                    attached.append(alias)
                    state = self.db.execute(f"SELECT value FROM {alias}.state WHERE key='readonly_sources'").fetchone()
                    if state and json.loads(state[0]):
                        raise ValueError("cannot merge a composite count view; attach its original sources")
                    ids = {row[0] for row in self.db.execute(f"SELECT id FROM {alias}.batches")}
                    seen = sum(marker in incoming_ids or self.db.execute(
                        "SELECT 1 FROM batches WHERE id=?", (marker,)).fetchone() is not None for marker in ids)
                    if seen and seen != len(ids):
                        raise ValueError("overlapping vocabulary checkpoint batches")
                    consumed.append(view)
                    if seen:
                        continue
                    incoming_ids.update(ids)
                    mapping = {old: self._token_id(token) for old, token in self.db.execute(
                        f"SELECT id, token FROM {alias}.tokens")}
                    key = "token"
                    if any(old != new for old, new in mapping.items()):
                        function = f"vocab_group_remap_{i}"
                        self.db.create_function(function, 1, _packed_remapper(mapping), deterministic=True)
                        functions.append(function)
                        key = f"{function}(token)"
                    selections.append(f"SELECT family,{key} AS token,n FROM {alias}.counts")
                    receipts.append(alias)
                    if self.db.execute(f"SELECT 1 FROM {alias}.sqlite_master WHERE name='signatures'").fetchone():
                        if self.state("materialization") and self.db.execute(
                            f"SELECT 1 FROM {alias}.signatures LIMIT 1"
                        ).fetchone():
                            raise ValueError("finish interrupted materialization before merging signatures")
                        signatures.append(f"SELECT family,gram_order,{key} AS token,n FROM {alias}.signatures")
                if selections:
                    self.db.execute(
                        "INSERT INTO counts SELECT family,token,sum(n),NULL,NULL FROM (" +
                        " UNION ALL ".join(selections) + ") WHERE true GROUP BY family,token "
                        "ON CONFLICT(family,token) DO UPDATE SET n=n+excluded.n,first_document=NULL,document=NULL")
                if signatures:
                    self.db.execute(
                        "INSERT INTO signatures SELECT family,gram_order,token,sum(n) FROM (" +
                        " UNION ALL ".join(signatures) + ") WHERE true GROUP BY family,gram_order,token "
                        "ON CONFLICT(family,gram_order,token) DO UPDATE SET n=n+excluded.n")
                for alias in receipts:
                    self.db.execute(f"INSERT INTO batches SELECT * FROM {alias}.batches")
                self.db.commit()
                event("vocabulary.merge_many", "counts", shards=len(receipts), batches=len(incoming_ids))
            except BaseException:
                self.db.rollback()
                # Newly allocated token IDs were part of the rolled-back merge.
                self.tokens = dict(self.db.execute("SELECT id, token FROM tokens"))
                self.token_ids = {token: i for i, token in self.tokens.items()}
                raise
            finally:
                for alias in attached:
                    self.db.execute(f"DETACH DATABASE {alias}")
                for function in functions:
                    self.db.create_function(function, 1, None)
            for path in {view.path for view in consumed}:
                Path(path).unlink(missing_ok=True)

    @timed("vocabulary.attach_shared")
    def attach_shared(self, view: CountView) -> None:
        """Register an immutable source and its receipt without copying counts.

        Only dictionaries, source locations and completion receipts are stored
        locally. Their transaction can be retried after interruption.
        """
        self.flush()
        path = str(Path(view.path).resolve())
        entries = self.state("readonly_sources", [])
        for entry in entries:
            if entry["path"] == path:
                if _source_identity(path) != entry["identity"]:
                    raise ValueError("shared count source was replaced or changed; use a new checkpoint")
                return
        if len(entries) >= 2:
            raise ValueError("shared vocabulary supports two hash folds")
        if self._readonly_sources is not None:
            for source in self._readonly_sources:
                self.db.execute(f"DETACH DATABASE {source['alias']}")
            self._readonly_sources = None
        source = sqlite3.connect(Path(path).as_uri()+"?mode=ro", uri=True)
        try:
            state = source.execute("SELECT value FROM state WHERE key='readonly_sources'").fetchone()
            if state and json.loads(state[0]):
                raise ValueError("shared count source must be materialized")
            if source.execute("SELECT 1 FROM signatures LIMIT 1").fetchone():
                raise ValueError("shared count source must be materialized")
            receipts = source.execute("SELECT id,summary,n_rows FROM batches ORDER BY id").fetchall()
            if not receipts or any(self.db.execute("SELECT 1 FROM batches WHERE id=?", (r[0],)).fetchone() for r in receipts):
                raise ValueError("overlapping shared count sources")
            for _, token in source.execute("SELECT id,token FROM tokens"):
                self._token_id(token)
            self.db.executemany("INSERT INTO batches VALUES (?,?,?)", receipts)
            entries.append(dict(path=path, receipts=[r[0] for r in receipts], identity=_source_identity(path)))
            self.set_state("readonly_sources", entries)
        except BaseException:
            self.db.rollback()
            self.tokens = dict(self.db.execute("SELECT id,token FROM tokens"))
            self.token_ids = {token:i for i,token in self.tokens.items()}
            raise
        finally:
            source.close()

    def _sources(self):
        if self._readonly_sources is None:
            self._readonly_sources = _attach_count_sources(self.db, self.token_ids, self.state("readonly_sources", []))
        # Local benign counts can grow between queries, so do not cache their
        # family-presence test. Shared sources are immutable.
        return [dict(alias="main", key="token", reverse=None, families={})] + self._readonly_sources

    def iter_counts(self, family=None):
        """Read the logical counts, including attached sources, for inspection."""
        self.materialize()
        sources = self._sources()
        families = [family] if family is not None else sorted({row[0] for source in sources
            for row in self.db.execute(f"SELECT DISTINCT family FROM {source['alias']}.counts")})
        for name in families:
            query, args = _frequency_query(self.db, sources, name)
            for token,n in self.db.execute(query, args):
                yield name,token,n

    def _family_query(self, family, minimum=0):
        sources = self._sources()
        query,args = _frequency_query(self.db, sources, family)
        if len(self._readonly_sources) < 2 or self.db.execute(
            "SELECT 1 FROM main.counts WHERE family=? LIMIT 1", (family,)
        ).fetchone():
            return query,args
        # Production would otherwise repeat a full two-fold aggregation for
        # candidate discovery and both top-k queries. Cache only the eligible
        # frequencies in a bounded-memory SQLite temporary store. Fold readers
        # use their one indexed source directly; benign counts remain local.
        reusable = [(floor,table) for (name,floor),table in self._qualified_frequencies.items()
                    if name == family and floor <= minimum]
        if reusable:
            _,table = max(reusable)
        else:
            table = f"qualified_frequency_{len(self._qualified_frequencies)}"
            self.db.execute(f"CREATE TEMP TABLE {table}(token BLOB PRIMARY KEY,n INTEGER) WITHOUT ROWID")
            try:
                self.db.execute(f"INSERT INTO {table} SELECT token,n FROM ({query}) WHERE n>=?", (*args,minimum))
                self.db.commit()
            except BaseException:
                self.db.rollback()
                self.db.execute(f"DROP TABLE {table}")
                raise
            self._qualified_frequencies[family,minimum] = table
        return f"SELECT token,n FROM {table}", ()

    def count_at_least(self, family: str, minimum: int) -> int:
        self.materialize()
        query,args = self._family_query(family,minimum)
        return self.db.execute(f"SELECT count(*) FROM ({query}) WHERE n>=?", (*args,minimum)).fetchone()[0]

    def token_parts(self, key: bytes) -> tuple[str, ...]:
        return tuple(self.tokens[i] for i in _ids(key))

    @timed("vocabulary.ranked_page")
    def ranked_page(self, family: str, limit: int, minimum: int, after=None):
        """Bounded exact page in (-frequency, name, packed-key) order.

        Numeric cutoff selection avoids decoding every qualifying key. Only
        the cutoff band needs names; nsmallest bounds RAM even for huge ties.
        The packed key disambiguates tokens containing the name separator.
        """
        if limit < 1:
            raise ValueError("ranked page size must be positive")
        self.materialize()
        query, args = self._family_query(family, minimum)
        predicate = "n>=?"
        values = [minimum]
        if after is not None:
            frequency, name, packed = after
            self.db.create_function("vocab_token_name", 1, lambda key: _name(key, self.tokens))
            predicate += (" AND (n<? OR (n=? AND (vocab_token_name(token)>? OR "
                          "(vocab_token_name(token)=? AND token>?))))")
            values.extend((frequency, frequency, name, name, bytes.fromhex(packed)))
        filtered = f"SELECT token,n FROM ({query}) WHERE {predicate}"
        parameters = (*args, *values)
        cutoff = self.db.execute(filtered + " ORDER BY n DESC LIMIT 1 OFFSET ?",
                                 (*parameters, limit - 1)).fetchone()
        if cutoff is not None:
            filtered += " AND n>=?"
            parameters += (cutoff[1],)
        rows = self.db.execute(filtered, parameters)
        try:
            best = heapq.nsmallest(limit, ((-n, _name(key, self.tokens), key) for key,n in rows))
        finally:
            rows.close()
        return [(key, -negative) for negative, _, key in best]

    def at_least(self, family: str, minimum: int) -> list[str]:
        self.materialize()
        query,args = self._family_query(family,minimum)
        return sorted(_name(key, self.tokens) for key, in self.db.execute(
            f"SELECT token FROM ({query}) WHERE n>=?", (*args,minimum),
        ))

    def top(self, family: str, limit: int, minimum: int, *, benign_family: str = "",
            benign_ceiling: int = 0) -> list[str]:
        """Filter before ranking; resolve cutoff ties by names, not local IDs."""
        if limit <= 0:
            return []
        self.materialize()
        positive, positive_args = self._family_query(family,minimum)
        cte = f"WITH frequency AS ({positive})"
        base_args = positive_args
        if benign_family:
            negative, negative_args = self._family_query(benign_family)
            cte += f", benign AS ({negative})"
            base_args += negative_args

        def selection(minimum):
            if benign_family:
                return (
                    " FROM frequency c LEFT JOIN benign b ON b.token=c.token"
                    " WHERE c.n>=? AND COALESCE(b.n, 0)<=?",
                    (*base_args, minimum, benign_ceiling),
                )
            return " FROM frequency c WHERE c.n>=?", (*base_args, minimum)

        query, args = selection(minimum)
        cutoff = self.db.execute(
            cte + " SELECT c.n" + query + " ORDER BY c.n DESC LIMIT 1 OFFSET ?", (*args, limit - 1),
        ).fetchone()
        if cutoff:
            query, args = selection(max(minimum, cutoff[0]))
        rows = self.db.execute(cte + " SELECT c.token, c.n" + query, args)
        # Only the top frequency band needs decoding. nsmallest bounds memory
        # even when millions of eligible features tie at the cutoff.
        best = heapq.nsmallest(limit, ((-n, _name(key, self.tokens)) for key, n in rows))
        return sorted(name for _, name in best)


@dataclass(frozen=True)
class TrigramSource:
    path: str
    minimum: int


class DiskTrigramCandidates:
    """Look up packed triples in the shared counts DB with a bounded cache.

    Worker startup loads only the token dictionary, never the candidate list.
    SQLite's (family, token) primary key supports a range lookup per token pair.
    """

    def __init__(self, source: TrigramSource, cache_bytes: int = 16 * 1024 * 1024):
        self.db = sqlite3.connect(Path(source.path).resolve().as_uri() + "?mode=ro", uri=True,
                                 timeout=120)
        self.db.execute("PRAGMA cache_size=-8192")
        self.minimum = source.minimum
        self.token_ids = {token: i for i, token in self.db.execute("SELECT id, token FROM tokens")}
        state = self.db.execute("SELECT value FROM state WHERE key='readonly_sources'").fetchone()
        self.sources = [dict(alias="main",key="token",reverse=None,families={})]
        self.sources += _attach_count_sources(self.db, self.token_ids, json.loads(state[0]) if state else [])
        self.cache: OrderedDict[bytes, tuple[int, ...]] = OrderedDict()
        self.cache_bytes = cache_bytes
        self.used_bytes = 0

    def close(self):
        self.db.close()

    def _suffixes(self, prefix: bytes):
        if prefix in self.cache:
            self.cache.move_to_end(prefix)
            yield from self.cache[prefix]
            return
        values = []
        size = 128
        query,args = _frequency_query(self.db, self.sources, "trigram", prefix)
        rows = self.db.execute(f"SELECT token FROM ({query}) WHERE n>=?", (*args,self.minimum))
        try:
            for (key,) in rows:
                value = struct.unpack(">I", key[8:])[0]
                if size <= self.cache_bytes:
                    values.append(value)
                    size += 40  # int plus tuple slot, with room for cache overhead
                yield value
        finally:
            rows.close()
        if size <= self.cache_bytes:
            while self.cache and self.used_bytes + size > self.cache_bytes:
                _, evicted = self.cache.popitem(last=False)
                self.used_bytes -= 128 + len(evicted) * 40
            self.cache[prefix] = tuple(values)
            self.used_bytes += size

    def matches(self, paths):
        present = {self.token_ids[path]: path for path in paths if path in self.token_ids}
        ordered = sorted(present, key=present.__getitem__)
        for a, b in combinations(ordered, 2):
            prefix = struct.pack(">II", a, b)
            for c in self._suffixes(prefix):
                if c in present:
                    yield present[a], present[b], present[c]
