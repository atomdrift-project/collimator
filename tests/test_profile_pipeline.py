"""Hash-sampled profiling remains isolated and covers worker/merge CPU work."""

import json
import hashlib
import os
from pathlib import Path
import pstats
import runpy
import sqlite3
import subprocess
import sys

import pytest

from collimator import data, features
from collimator.demo import create_demo_db

ROOT = Path(__file__).resolve().parents[1]


def selected_hash(selected, suffix="80"):
    for nonce in range(100000):
        canonical = f"{nonce:0{64-len(suffix)}x}" + suffix
        bucket = int(hashlib.md5(canonical.encode()).hexdigest()[:8], 16)
        if (bucket < int(.02 * 2**32)) == selected:
            return canonical
    raise AssertionError("could not construct hash fixture")


@pytest.mark.parametrize("percent", ["0", "-1", "101", "nan", "Infinity", "bogus", "0.000000001"])
def test_invalid_sample_percent_fails(percent):
    with pytest.raises(ValueError):
        data.sample_predicate(percent)


def test_hash_sample_rehashes_canonical_key_and_preserves_suffix_splits():
    with sqlite3.connect(":memory:") as db:
        db.create_function("md5", 1, lambda value: hashlib.md5(value.encode()).hexdigest())
        db.execute("CREATE TABLE samples (id INTEGER, sha256 TEXT, canonical_sha256 TEXT)")
        # Every train/dev/test suffix and both OOF halves survive selection.
        for suffix in range(256):
            canonical = selected_hash(True, f"{suffix % 2:02x}{suffix:02x}")
            db.execute("INSERT INTO samples VALUES (?,?,?)", (suffix, "f" * 64, canonical))
        # Canonical key wins over a row hash that would itself be selected.
        db.execute("INSERT INTO samples VALUES (256,?,?)", (selected_hash(True), selected_hash(False)))
        # Empty canonical hashes fall back to the row hash, as partitioning does.
        db.execute("INSERT INTO samples VALUES (257,?,'')", (selected_hash(True),))
        selected = list(db.execute("SELECT id FROM samples WHERE " + data.sample_predicate("2")))
        assert {row[0] for row in selected} == set(range(256)) | {257}
        hashes = [row[0] for row in db.execute("SELECT canonical_sha256 FROM samples WHERE id<256")]
        assert {data.partition_of(h) for h in hashes} == {"train", "dev", "test"}
        assert {data.oof_fold_of(h) for h in hashes} == {0, 1, None}
        assert data.sample_predicate("100") == ""
        cutoff = int(.02 * 2**32)
        for prefix, expected in ((cutoff - 1, 1), (cutoff, 0)):
            db.create_function("md5", 1, lambda _: f"{prefix:08x}" + "0" * 56)
            db.execute("DELETE FROM samples")
            db.execute("INSERT INTO samples VALUES (0,?,NULL)", (f"{prefix:08x}" + "0" * 56,))
            assert db.execute("SELECT count(*) FROM samples WHERE " + data.sample_predicate("2")).fetchone()[0] == expected


def test_default_plan_is_one_percent_fresh_and_isolated(tmp_path):
    output = tmp_path / "profile"
    env = dict(os.environ, AZOTH_ROOT="/unwanted/live", EXP_OUT_DIR="/unwanted/experiments",
               MAKEFLAGS="AZOTH_ROOT=/unwanted/live", COLLIMATOR_SAMPLE_PERCENT="100")
    result = subprocess.run([
        sys.executable, "scripts/azoth_profile.py", "--dry-run", "--output", str(output),
    ], cwd=ROOT, env=env, text=True, capture_output=True, check=True)
    plan = json.loads(result.stdout)
    assert plan["sample_percent"] == "1"
    assert plan["environment"]["COLLIMATOR_SAMPLE_PERCENT"] == "1"
    assert plan["environment"]["AZOTH_VALIDATE_ONLY"] == "1"
    assert plan["environment"]["AZOTH_PIPELINE_RESUME"] == "0"
    assert plan["environment"]["AZOTH_MEM_PER_FIT_GB"] == "8"
    assert plan["environment"]["AZOTH_EXTRACT_WORKERS_MAX"] == "4"
    assignments = dict(arg.split("=", 1) for arg in plan["command"] if "=" in arg)
    assert assignments["WORKERS"] == "48"
    for name in ("OUT_ROOT", "AZOTH_ROOT", "EXP_OUT_DIR", "EXP_CACHE_DIR", "AZOTH_FEATURE_CACHE_DIR",
                 "AZOTH_FOLD_A_EXP_OUT_DIR", "AZOTH_FOLD_B_EXP_OUT_DIR", "AZOTH_CHECKPOINT_DIR",
                 "AZOTH_SPECIALIST_FEATURE_CACHE_DIR", "AZOTH_ALLOWLIST_CACHE_DIR", "AZOTH_FOLD_FIT_MEM_FILE",
                 "AZOTH_SPECIALIST_FIT_MEM_FILE"):
        assert Path(assignments[name]).is_relative_to(output)
    assert not output.exists()


@pytest.mark.parametrize("arguments,memory,workers", [
    (["--percent", "100"], "28", "6"),
    (["--fit-memory-gb", "12", "--extract-workers-per-fit", "3"], "12.0", "3"),
])
def test_profile_resource_defaults_and_overrides(arguments, memory, workers):
    plan = json.loads(subprocess.check_output([
        sys.executable, "scripts/azoth_profile.py", "--dry-run", *arguments,
    ], cwd=ROOT, text=True))
    assert plan["environment"]["AZOTH_MEM_PER_FIT_GB"] == memory
    assert plan["environment"]["AZOTH_EXTRACT_WORKERS_MAX"] == workers


@pytest.mark.parametrize("target", ["azoth-specialists", "azoth-specialists-fold-a", "azoth-specialists-fold-b"])
def test_specialist_recipes_use_isolated_caches_and_memory_history(tmp_path, target):
    plan = json.loads(subprocess.check_output([
        sys.executable, "scripts/azoth_profile.py", "--dry-run", "--output", str(tmp_path / "run"),
    ], cwd=ROOT, text=True))
    recipe = subprocess.check_output([
        "make", "-n", "-o", "venv", "-o", "check-db", target, *plan["command"][2:],
    ], cwd=ROOT, text=True)
    assert f"--feature-cache-dir {tmp_path / 'run/cache/routes'}" in recipe
    memory_name = "prod" if target == "azoth-specialists" else "fold"
    assert f"--fit-mem-file {tmp_path / f'run/cache/fit-mem/{memory_name}.json'}" in recipe
    assert "--feature-cache-dir out/cache/" not in recipe


def test_sampled_selection_allows_index_scans(monkeypatch):
    from unittest.mock import Mock
    conn = Mock()
    monkeypatch.setattr(data, "SAMPLE_PREDICATE", data.sample_predicate("1"))
    data._read_table_in_order(conn)
    conn.execute.assert_not_called()
    monkeypatch.setattr(data, "SAMPLE_PREDICATE", "")
    data._read_table_in_order(conn)
    assert conn.execute.call_count == 3


def test_calibration_general_scores_use_requested_pin():
    recipe = subprocess.check_output([
        "make", "-n", "-o", "venv", "-o", "check-db", "azoth-calibrate",
        "THRESHOLD_MAX_ID=123456",
    ], cwd=ROOT, text=True)
    scoring = recipe.split("-m collimator tune-thresholds", 1)[1].split(
        "scripts/azoth_calibrate_ensemble.py", 1,
    )[0]
    assert "--max-id 123456" in scoring


def test_sampled_path_lookup_preserves_filters_order_and_limit(tmp_path, monkeypatch):
    path = tmp_path / "metadata.db"
    chosen, excluded = selected_hash(True), selected_hash(False)
    predicate = data.sample_predicate("2")
    where = "label IN ('bad','good') AND cleave_result IS NOT NULL AND skip=''"
    monkeypatch.setattr(data, "SAMPLE_PREDICATE", predicate)
    monkeypatch.setattr(data, "LABELED_WHERE", f"{where} AND ({predicate})")
    with sqlite3.connect(path) as conn:
        conn.create_function("md5", 1, lambda value: hashlib.md5(value.encode()).hexdigest())
        conn.execute("CREATE TABLE samples (id INTEGER PRIMARY KEY, sha256 TEXT, "
                     "canonical_sha256 TEXT, path TEXT, score INTEGER, label TEXT, "
                     "cleave_result TEXT, skip TEXT)")
        conn.executemany("INSERT INTO samples VALUES (?,?,?,?,?,'bad','{}','')", [
            (1, chosen, chosen, '/ignore', 5),
            (2, excluded, excluded, '/keep', 5),
            (3, chosen, chosen, '/KEEP', 5),
            (4, chosen, chosen, '/keep', 3),
            (5, chosen, chosen, '/keep', 7),
            (6, chosen, chosen, '/keep', 5),
        ])
        # Execute both query shapes; SQLite also supports materialized CTEs.
        for postgres in (False, True):
            query = data._metadata_full_query(
                data.LABELED_WHERE + ' AND id <= 5 AND score >= ? AND score <= ?',
                postgres=postgres, path_predicate='LOWER(path) LIKE ?', limit=1,
            )
            assert conn.execute(query, (4, 6, '%keep%')).fetchall() == [
                (3, chosen, '/KEEP', 5, 'bad', chosen),
            ]
        conn.commit()
    assert list(data.stream_labeled_metadata_full(
        path, path_substr='keep', min_score=4, max_score=6, max_id=5, limit=1,
    )) == [(3, chosen, '/KEEP', 5, 1, chosen)]


def test_profile_cleanup_only_cancels_its_own_active_queries(monkeypatch):
    from unittest.mock import MagicMock
    module = runpy.run_path(str(ROOT / "scripts/azoth_profile.py"))
    driver = MagicMock()
    conn = driver.connect.return_value.__enter__.return_value
    conn.execute.return_value.fetchall.return_value = [(True,)]
    monkeypatch.setitem(sys.modules, "psycopg", driver)
    module["cancel_queries"]("postgres://local/test", {"PGAPPNAME": "unique-run"})
    sql, params = conn.execute.call_args.args
    assert "WHERE application_name=%s AND state='active'" in sql
    assert params == ("unique-run",)


def test_failed_pipeline_writes_result_without_claiming_target_met(tmp_path, monkeypatch):
    import importlib.util
    spec = importlib.util.spec_from_file_location("profile_runner", ROOT / "scripts/azoth_profile.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    run = tmp_path / "run"
    env = dict(os.environ, COLLIMATOR_TIMING_DIR=str(run / "timings"),
               AZOTH_MEM_PER_FIT_GB="8", AZOTH_EXTRACT_WORKERS_MAX="2")
    monkeypatch.setenv("COLLIMATOR_TIMING_DIR", env["COLLIMATOR_TIMING_DIR"])
    command = [sys.executable, "-c", "raise SystemExit(7)"]
    monkeypatch.setattr(runner, "plan", lambda _: (run, env, command, "sample predicate"))
    assert runner.main(["--no-memory-scope", "--pin", "1", "--db", "demo.db"]) == 7
    result = json.loads((run / "result.json").read_text())
    assert result["returncode"] == 7
    assert result["full_pipeline"] is True
    assert result["wall_seconds"] >= 0
    assert result["completed_within_target"] is False
    assert "THRESHOLD_MAX_ID=1" in command
    assert "EXP_MAX_ID=1" in command


def test_sampled_file_types_scan_cohort_once_and_filter_requested_ids(tmp_path, monkeypatch):
    path = tmp_path / "types.db"
    canonical = selected_hash(True)
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE samples (id INTEGER, sha256 TEXT, canonical_sha256 TEXT, "
                   "label TEXT, skip TEXT, cleave_result TEXT, file_type TEXT)")
        db.executemany("INSERT INTO samples VALUES (?,?,?,'good','','{}','elf')",
                       [(i, canonical, canonical) for i in range(602)])
        db.execute("UPDATE samples SET skip='excluded' WHERE id=2")
        db.execute("UPDATE samples SET file_type='' WHERE id=3")
    predicate = data.sample_predicate("2")
    monkeypatch.setattr(data, "SAMPLE_PREDICATE", predicate)
    monkeypatch.setattr(data, "LABELED_WHERE", "label IN ('bad','good') AND "
                        f"cleave_result IS NOT NULL AND skip='' AND ({predicate})")
    calls = []
    original = data._execute
    def execute(conn, query, params=None):
        calls.append(query)
        yield from original(conn, query, params)
    monkeypatch.setattr(data, "_execute", execute)
    result = data.fetch_file_types(path, range(1, 601))
    assert len(calls) == 1
    assert set(result) == set(range(1, 601)) - {2}
    assert result[3] == "unknown"


def test_live_timings_record_failures_without_cpu_profiler(tmp_path):
    env = dict(os.environ, COLLIMATOR_TIMING_DIR=str(tmp_path / "timings"))
    env.pop("COLLIMATOR_PROFILE_DIR", None)
    result = subprocess.run([
        sys.executable, "scripts/profile_stage.py", "failed-stage",
        sys.executable, "scripts/profile_python.py", "-c", "raise SystemExit(7)",
    ], cwd=ROOT, env=env, capture_output=True, text=True, timeout=10)
    assert result.returncode == 7
    events = [json.loads(line) for path in (tmp_path / "timings").glob("*.jsonl")
              for line in path.read_text().splitlines()]
    ends = {row["label"]: row for row in events if row["event"] == "end"}
    assert ends["stage.failed-stage"]["status"] == "error"
    assert ends["command"]["status"] == "error"
    assert ends["command"]["wall_seconds"] >= 0
    assert ends["command"]["thread_cpu_seconds"] >= 0
    report = subprocess.run([sys.executable, "scripts/azoth_profile_report.py", str(tmp_path)],
                            cwd=ROOT, capture_output=True, text=True, check=True)
    assert "stage.failed-stage" in report.stdout


def test_timing_report_separates_merge_phases_and_signature_reuse(tmp_path):
    timings = tmp_path / "timings"
    timings.mkdir()
    records = []
    for number, phase in enumerate(("count", "benign")):
        base = dict(pid=42, thread=1, timestamp=0)
        records.extend([
            dict(base, label="vocabulary.merge", event="start", span=number),
            dict(base, label="vocabulary.merge", event="counts", phase=phase,
                 batches=16, source_bytes=2**20, remapped=phase == "benign"),
            dict(base, label="vocabulary.merge", event="end", span=number,
                 wall_seconds=2, thread_cpu_seconds=1.5),
        ])
    records.append(dict(base, label="vocabulary.signatures", event="counts",
                        documents=100, signatures=25, estimated_bytes=1024))
    (timings / "42.jsonl").write_text("\n".join(map(json.dumps, records)) + "\n")
    result = subprocess.run([sys.executable, "scripts/azoth_profile_report.py", str(tmp_path)],
                            cwd=ROOT, capture_output=True, text=True, check=True)
    assert "Vocabulary shards" in result.stdout
    assert "benign" in result.stdout and "count" in result.stdout
    assert "100 token-set occurrences -> 25 expansions (4.00x" in result.stdout
    assert "Unfinished" not in result.stdout


def test_shared_sampling_reaches_general_and_specialist_queries(tmp_path):
    path = tmp_path / "sample.db"
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE samples (id INTEGER, sha256 TEXT, canonical_sha256 TEXT, "
                   "label TEXT, score INTEGER, skip TEXT, cleave_result TEXT, file_type TEXT)")
        for index in range(100):
            canonical = selected_hash(index < 2, f"{index:02x}80")
            db.execute("INSERT INTO samples VALUES (?,?,?,'good',5,'','{}','elf')",
                       (index + 1, canonical, canonical))
    code = """
import json, sys
sys.path.insert(0, 'scripts')
from collimator import data, cache_identity
from azoth_specialist_suite import _fetch_rows
print(json.dumps({
    'general': [r[0] for r in data.stream_partitioned_metadata_grouped(sys.argv[1])],
    'specialist': [r[0] for r in _fetch_rows(sys.argv[1], file_types=('elf',), max_id=100, min_score=None)],
    'revision': cache_identity.database_revision(sys.argv[1]),
}))
"""
    results = []
    for percent in ("2", "100"):
        result = subprocess.run([sys.executable, "-c", code, str(path)], cwd=ROOT,
                                env=dict(os.environ, COLLIMATOR_SAMPLE_PERCENT=percent),
                                capture_output=True, text=True, check=True)
        results.append(json.loads(result.stdout))
    assert results[0]["general"] == results[0]["specialist"] == [1, 2]
    assert len(results[1]["general"]) == len(results[1]["specialist"]) == 100
    assert results[0]["revision"] != results[1]["revision"]


@pytest.mark.parametrize("target", ["azoth-publish", "azoth-deploy-final"])
def test_sampled_runs_cannot_publish(target):
    result = subprocess.run(["make", "-s", "-o", "venv", target, "COLLIMATOR_SAMPLE_PERCENT=2"],
                            cwd=ROOT, capture_output=True, text=True, timeout=10)
    assert result.returncode != 0
    assert "Refusing to" in result.stdout


def test_profile_wrapper_runs_a_fresh_sampled_experiment(tmp_path):
    path = tmp_path / "demo.db"
    output = tmp_path / "model"
    create_demo_db(path, n_benign=1500, n_malware=1500, seed=7)
    env = dict(os.environ, COLLIMATOR_SAMPLE_PERCENT="2",
               COLLIMATOR_PROFILE_DIR=str(tmp_path / "cpu"), COLLIMATOR_NUM_THREADS="1",
               COLLIMATOR_DISABLE_FEATURE_GROUPS="clusters")
    result = subprocess.run([
        sys.executable, "scripts/profile_python.py", "-u", "-m", "collimator", "experiment",
        "--db", str(path), "--output", str(output), "--cache-dir", str(tmp_path / "cache"),
        "--learner", "azoth", "--model-name", "azoth", "--workers", "2", "--device", "cpu",
        "--train-samples", "0", "--max-test-samples", "0", "--min-malware-score", "0",
        "--n-estimators", "5", "--n-folds", "0",
    ], cwd=ROOT, env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    runs = [json.loads(p.read_text()) for p in (output / "runs").glob("*.json")]
    run = next(r for r in runs if "experiment_key" in r)
    assert 10 <= run["train_rows"] < 100
    assert run["feature_env"]["COLLIMATOR_SAMPLE_PERCENT"] == "2"
    assert (output / "model.txt").is_file()
    assert list((tmp_path / "cpu").glob("worker-*.prof"))
    assert list((tmp_path / "cpu").glob("collimator-*.prof"))


@pytest.mark.parametrize("code,exitcode", [("sum(i*i for i in range(100))", 0), ("raise SystemExit(7)", 7)])
def test_entrypoint_profiles_success_and_failure(tmp_path, code, exitcode):
    env = dict(os.environ, COLLIMATOR_PROFILE_DIR=str(tmp_path))
    result = subprocess.run([sys.executable, "scripts/profile_python.py", "-u", "-c", code],
                            cwd=ROOT, env=env, capture_output=True, text=True)
    assert result.returncode == exitcode, result.stderr
    profiles = list(tmp_path.glob("*.prof"))
    assert len(profiles) == 1
    assert pstats.Stats(str(profiles[0])).total_calls > 0


@pytest.mark.parametrize("shard_batches", [4, 100])
def test_profiles_include_spawned_workers_and_merge_thread(tmp_path, monkeypatch, shard_batches):
    monkeypatch.setenv("COLLIMATOR_PROFILE_DIR", str(tmp_path / "cpu"))
    monkeypatch.setenv("COLLIMATOR_VOCAB_TMPDIR", str(tmp_path / "scratch"))
    # Exercise both full background shards and a run made entirely of tails.
    monkeypatch.setenv("COLLIMATOR_VOCAB_SHARD_BATCHES", str(shard_batches))
    monkeypatch.setattr(features, "_feature_batch_size", lambda _: 8)
    path = tmp_path / "demo.db"
    create_demo_db(path, n_benign=80, n_malware=80, seed=7)
    with sqlite3.connect(path) as conn:
        labels = [(rid, int(label == "bad")) for rid, label in
                  conn.execute("SELECT id,label FROM samples ORDER BY id")]
    assert features.build_vocab_from_db(path, labels, n_workers=2).total_features > 0
    assert list((tmp_path / "cpu").glob("worker-*.prof"))
    merges = list((tmp_path / "cpu").glob("vocab-merge-*.prof"))
    assert merges
    stats = pstats.Stats(*(str(p) for p in merges))
    assert any(name == "merge" and filename.endswith("vocabulary.py")
               for filename, _, name in stats.stats)


@pytest.mark.parametrize("module,initializer", [
    ("azoth_specialist_suite", "_pool_init"),
    ("azoth_calibrate_ensemble", "_score_pool_init"),
])
def test_route_pools_write_worker_profiles(tmp_path, module, initializer):
    code = f"""
import sys
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, 'scripts')
from {module} import {initializer}
with ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context('spawn'),
                         initializer={initializer}, initargs=('WARNING',)) as pool:
    assert pool.submit(abs, -42).result() == 42
"""
    subprocess.run([sys.executable, "-c", code], cwd=ROOT, check=True,
                   env=dict(os.environ, COLLIMATOR_PROFILE_DIR=str(tmp_path)))
    profiles = list(tmp_path.glob("worker-*.prof"))
    assert profiles
    assert pstats.Stats(str(profiles[0])).total_calls > 0
