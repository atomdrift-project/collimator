"""Exact document frequencies with a bounded write cache and disk overflow.

N-grams use packed token IDs rather than repeating long taxonomy paths in every
SQLite key. Workers own disjoint documents; their files are merged by token
identity. No frequency counts are discarded under memory pressure.
"""

from __future__ import annotations

import heapq
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

    def __init__(self, path: str = "", buffer_size: int = 100_000) -> None:
        self.path = path
        self.buffer_size = max(1, buffer_size)
        # Per key: count, first document, last document since the last write.
        self.pending: OrderedDict[tuple[str, bytes], list] = OrderedDict()
        self.token_ids: dict[str, int] = {}
        self.tokens: dict[int, str] = {}
        self.db = sqlite3.connect(path, uri=True)
        self.db.execute("PRAGMA cache_size=-32768")
        self.db.execute("PRAGMA temp_store=FILE")
        # Scratch data is recreated on failure, not a durable artifact.
        self.db.execute("PRAGMA journal_mode=OFF")
        self.db.execute("PRAGMA synchronous=OFF")
        self.db.execute("CREATE TABLE tokens (id INTEGER PRIMARY KEY, token TEXT NOT NULL)")
        self.db.execute(
            "CREATE TABLE counts (family TEXT, token BLOB, n INTEGER NOT NULL,"
            " first_document INTEGER, document INTEGER, PRIMARY KEY (family, token)) WITHOUT ROWID"
        )

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

    def increment_combinations(self, family: str, tokens: Iterable[str], order: int, document: int,
                               benign_family: str = "") -> None:
        # Resolve paths once per file rather than for every pair/triple.
        ids = [self._token_id(token) for token in tokens]
        pack = struct.Struct(f">{order}I").pack
        for parts in combinations(ids, order):
            packed = pack(*parts)
            self._increment_key((family, packed), 1, document)
            if benign_family:
                self._increment_key((benign_family, packed), 1, document)

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

    def view(self, family: str):
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
            mapping = {i: self._token_id(token) for i, token in self.db.execute(
                "SELECT id, token FROM vocab_batch.tokens",
            )}

            def remap(key):
                mapped = [mapping[i] for i in _ids(key)]
                return struct.pack(f">{len(mapped)}I", *mapped)

            self.db.create_function("vocab_remap", 1, remap, deterministic=True)
            # Worker-local token IDs put rows in an arbitrary order in the
            # destination's key space. Sort after remapping so a large merge
            # visits destination B-tree pages sequentially. SQLite spills the
            # sort to disk; Python never materializes the combination table.
            self.db.execute(
                "INSERT INTO counts"
                " SELECT family, vocab_remap(token) AS mapped, n, NULL, NULL"
                " FROM vocab_batch.counts WHERE true ORDER BY family, mapped"
                " ON CONFLICT(family, token) DO UPDATE SET n=n+excluded.n,"
                " first_document=NULL, document=NULL",
            )
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise
        finally:
            self.db.execute("DETACH DATABASE vocab_batch")
            self.db.create_function("vocab_remap", 1, None)
        Path(view.path).unlink()

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
        query = (
            " FROM counts c LEFT JOIN counts b ON b.family=? AND b.token=c.token"
            " WHERE c.family=? AND c.n>=? AND COALESCE(b.n, 0)<=?"
        )
        args = (benign_family, family, minimum, benign_ceiling)
        cutoff = self.db.execute(
            "SELECT c.n" + query + " ORDER BY c.n DESC LIMIT 1 OFFSET ?", (*args, limit - 1),
        ).fetchone()
        if cutoff:
            args = (benign_family, family, max(minimum, cutoff[0]), benign_ceiling)
        rows = self.db.execute("SELECT c.token, c.n" + query, args)
        # Only the top frequency band needs decoding. nsmallest bounds memory
        # even when millions of eligible features tie at the cutoff.
        best = heapq.nsmallest(limit, ((-n, _name(key, self.tokens)) for key, n in rows))
        return sorted(name for _, name in best)
