"""Exact document frequencies with a bounded write cache and disk overflow.

N-grams use packed token IDs rather than repeating long taxonomy paths in every
SQLite key. Workers own disjoint documents; their files are merged by token
identity. No frequency counts are discarded under memory pressure.
"""

from __future__ import annotations

import heapq
import json
import sqlite3
import struct
from collections import OrderedDict
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path


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


@dataclass(frozen=True)
class CountView:
    """A completed worker's counts, transferred by filename rather than IPC."""
    path: str
    family: str

    def items(self):
        with sqlite3.connect(Path(self.path).resolve().as_uri() + "?mode=ro", uri=True) as db:
            tokens = dict(db.execute("SELECT id, token FROM tokens"))
            for key, n in db.execute("SELECT token, n FROM counts WHERE family=?", (self.family,)):
                yield _name(key, tokens), n


class VocabularyCounts:
    """Count contiguous documents; never revisit a document after the next one.

    ``merge`` consumes all families in a completed worker file, then removes
    it. The caller owns scratch-directory cleanup on failure. Token dictionaries
    scale with individual paths; only the much larger combination table spills.
    """

    def __init__(self, path: str = "", buffer_size: int = 100_000,
                 *, check_same_thread: bool = True, durable: bool = False,
                 resume: bool = False, cache_size_mib: int = 32) -> None:
        self.path = path
        self.buffer_size = max(1, buffer_size)
        # Per key: count, first document, last document since the last write.
        self.pending: OrderedDict[tuple[str, bytes], list] = OrderedDict()
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
            index = len(self.token_ids)
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
            self.flush(max(1, self.buffer_size // 4))

    def flush(self, limit: int | None = None) -> None:
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
            self.flush()
        if self.path:
            return CountView(self.path, family)
        return {_name(key, self.tokens): n for key, n in self.db.execute(
            "SELECT token, n FROM counts WHERE family=?", (family,),
        )}

    def merge(self, view: CountView) -> None:
        self.flush()
        self.db.execute("ATTACH DATABASE ? AS vocab_batch",
                        (Path(view.path).resolve().as_uri() + "?mode=ro",))
        try:
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
            # Counts and their completion markers commit together. A killed
            # merge rolls both back, so a restart can safely repeat its batch.
            self.db.execute("INSERT INTO batches SELECT * FROM vocab_batch.batches")
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise
        finally:
            self.db.execute("DETACH DATABASE vocab_batch")
            self.db.create_function("vocab_remap", 1, None)
        Path(view.path).unlink()

    def count_at_least(self, family: str, minimum: int) -> int:
        self.flush()
        return self.db.execute("SELECT count(*) FROM counts WHERE family=? AND n>=?",
                               (family, minimum)).fetchone()[0]

    def at_least(self, family: str, minimum: int) -> list[str]:
        self.flush()
        return sorted(_name(key, self.tokens) for key, in self.db.execute(
            "SELECT token FROM counts WHERE family=? AND n>=?", (family, minimum),
        ))

    def top(self, family: str, limit: int, minimum: int, *, benign_family: str = "",
            benign_ceiling: int = 0) -> list[str]:
        """Filter before ranking; resolve cutoff ties by names, not local IDs."""
        if limit <= 0:
            return []
        self.flush()

        def selection(minimum):
            if benign_family:
                return (
                    " FROM counts c LEFT JOIN counts b ON b.family=? AND b.token=c.token"
                    " WHERE c.family=? AND c.n>=? AND COALESCE(b.n, 0)<=?",
                    (benign_family, family, minimum, benign_ceiling),
                )
            return " FROM counts c WHERE c.family=? AND c.n>=?", (family, minimum)

        query, args = selection(minimum)
        cutoff = self.db.execute(
            "SELECT c.n" + query + " ORDER BY c.n DESC LIMIT 1 OFFSET ?", (*args, limit - 1),
        ).fetchone()
        if cutoff:
            query, args = selection(max(minimum, cutoff[0]))
        rows = self.db.execute("SELECT c.token, c.n" + query, args)
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
        rows = self.db.execute(
            "SELECT token FROM counts WHERE family='trigram' AND token>=? AND token<=? AND n>=?",
            (prefix + b"\0" * 4, prefix + b"\xff" * 4, self.minimum),
        )
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
