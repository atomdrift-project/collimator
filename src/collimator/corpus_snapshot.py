"""Consistent PostgreSQL inputs shared by a bounded research pass and its workers."""
from contextlib import contextmanager
from functools import wraps
import os

SNAPSHOT_ENV = 'COLLIMATOR_PG_SNAPSHOT'
DATABASE_ENV = 'COLLIMATOR_PG_SNAPSHOT_DATABASE'

@contextmanager
def frozen_corpus(db):
    """Keep one read-only exported snapshot alive; nested users share it.

    This changes visibility only. Ingestion can keep inserting/updating rows.
    Close the owning context after the comparison/pass so future passes refresh.
    """
    from . import data
    if not data._is_pg(db) or os.environ.get(SNAPSHOT_ENV):
        yield os.environ.get(SNAPSHOT_ENV, '')
        return
    old = {k: os.environ.get(k) for k in (SNAPSHOT_ENV, DATABASE_ENV)}
    with data._connect(db, repeatable_read=True) as conn:
        conn.execute('SET TRANSACTION READ ONLY')
        # The owner intentionally waits while worker connections do the work.
        # Its caller's process lifetime bounds the lease.
        conn.execute('SET LOCAL idle_in_transaction_session_timeout = 0')
        snapshot = conn.execute('SELECT pg_export_snapshot()').fetchone()[0]
        os.environ.update({SNAPSHOT_ENV: snapshot, DATABASE_ENV: str(db)})
        try:
            yield snapshot
        finally:
            for key, value in old.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


def stable_experiment(fn):
    @wraps(fn)
    def wrapped(db_path, *args, **kwargs):
        with frozen_corpus(db_path):
            return fn(db_path, *args, **kwargs)
    return wrapped
