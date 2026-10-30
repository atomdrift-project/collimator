"""Snapshot lifecycle and inheritance; live PG check is run separately."""
from contextlib import contextmanager
import os
from collimator import corpus_snapshot as snapshot, data


def test_owner_lives_through_nested_users_and_restores_environment(monkeypatch):
    calls=[]
    class Connection:
        def execute(self,sql):
            calls.append(sql)
            return self
        def fetchone(self):return ('test-snapshot',)
    @contextmanager
    def connect(db,**kwargs):
        calls.append('opened')
        yield Connection()
        calls.append('closed')
    monkeypatch.setattr(data,'_connect',connect)
    monkeypatch.delenv(snapshot.SNAPSHOT_ENV,raising=False)
    monkeypatch.delenv(snapshot.DATABASE_ENV,raising=False)
    with snapshot.frozen_corpus('postgres://test') as identity:
        assert identity=='test-snapshot'
        assert os.environ[snapshot.DATABASE_ENV]=='postgres://test'
        with snapshot.frozen_corpus('postgres://test'):
            assert calls.count('opened')==1
        assert 'closed' not in calls
    assert calls[-1]=='closed'
    assert snapshot.SNAPSHOT_ENV not in os.environ


def test_sqlite_does_not_export(monkeypatch):
    monkeypatch.delenv(snapshot.SNAPSHOT_ENV,raising=False)
    with snapshot.frozen_corpus('/tmp/test.db') as identity:
        assert identity==''


def test_experiment_keeps_signature_and_context(monkeypatch):
    events=[]
    @contextmanager
    def frozen(db):
        events.append(('open',db))
        yield
        events.append(('close',db))
    monkeypatch.setattr(snapshot,'frozen_corpus',frozen)
    @snapshot.stable_experiment
    def experiment(db_path,*,value):
        assert events==[('open','database')]
        return value
    assert experiment(db_path='database',value=3)==3
    assert events[-1]==('close','database')


def test_snapshot_tokens_are_runtime_only(monkeypatch):
    from collimator import experiment
    from collimator.autocollie_selection import replay_feature_env
    monkeypatch.setenv(snapshot.SNAPSHOT_ENV, 'expired-token')
    monkeypatch.setenv(snapshot.DATABASE_ENV, 'postgres://test')
    assert snapshot.SNAPSHOT_ENV not in experiment._collimator_env()
    assert snapshot.DATABASE_ENV not in experiment._collimator_env()
    assert replay_feature_env({'feature_env': {snapshot.SNAPSHOT_ENV: 'expired-token', snapshot.DATABASE_ENV: 'postgres://test'}}) == {}


def test_exported_snapshot_refreshes_old_cached_row_boundary(tmp_path, monkeypatch):
    from collimator import experiment

    cached = tmp_path / 'snapshot_max_id.txt'
    cached.write_text('100\n')
    monkeypatch.setenv(snapshot.SNAPSHOT_ENV, 'first-pass')
    monkeypatch.setattr(data, 'snapshot_max_id', lambda _db: 800)
    assert experiment._cached_snapshot_max_id('postgres://test', tmp_path, 0) == 800
    monkeypatch.setenv(snapshot.SNAPSHOT_ENV, 'next-pass')
    monkeypatch.setattr(data, 'snapshot_max_id', lambda _db: 900)
    assert experiment._cached_snapshot_max_id('postgres://test', tmp_path, 0) == 900
    assert experiment._cached_snapshot_max_id('postgres://test', tmp_path, 42) == 42
    assert cached.read_text() == '100\n'  # concurrent passes do not mutate this file


def test_static_sqlite_keeps_explicit_cached_boundary(tmp_path, monkeypatch):
    from collimator import experiment

    (tmp_path / 'snapshot_max_id.txt').write_text('100\n')
    monkeypatch.delenv(snapshot.SNAPSHOT_ENV, raising=False)
    assert experiment._cached_snapshot_max_id(tmp_path / 'database.db', tmp_path, 0) == 100
