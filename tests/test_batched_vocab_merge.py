"""Grouped reduction preserves exact counts, token identity and atomic receipts."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import shutil
import sqlite3

import pytest

from collimator import vocabulary
from collimator.vocabulary import CountView, VocabularyCounts


def shard(path, batch, *, deferred=False, stable=True, tokens=("a", "b", "c")):
    with VocabularyCounts(str(path), defer_signatures=deferred, stable_token_ids=stable) as worker:
        worker.group_combinations("bigram", tokens, 2, n=batch+1)
        # Two overlapping files in one document count each bigram just once.
        worker.increment_combinations("archive", ("a", "b", "c"), 2, batch)
        worker.increment_combinations("archive", ("b", "c", "d"), 2, batch)
        worker.record_batch(f"count:{batch}", None, batch+1)
    return CountView(str(path), "bigram")


@pytest.mark.parametrize("deferred", [False, True])
@pytest.mark.parametrize("stable", [False, True])
@pytest.mark.parametrize("collision", [False, True])
def test_grouped_reduction_exact_across_attachment_limit(tmp_path, monkeypatch, deferred, stable, collision):
    if collision:
        monkeypatch.setattr(vocabulary, "_token_hash", lambda _: 7)
    expected = Counter()
    views = []
    for i in range(11):
        tokens = ("a", "b", "c") if i%2 else ("b", "c", "d")
        views.append(shard(tmp_path/f"worker-{i}.sqlite", i, deferred=deferred, stable=stable, tokens=tokens))
        expected.update({" + ".join(c):i+1 for c in combinations(tokens, 2)})
    with VocabularyCounts(str(tmp_path/"master.sqlite"), durable=True, defer_signatures=True) as counts:
        counts.merge_many(views)
        assert dict(counts.view("bigram").items()) == expected
        assert dict(counts.view("archive").items()) == {
            "a + b":11, "a + c":11, "b + c":11, "b + d":11, "c + d":11}
        assert len(list(counts.completed_batches("count"))) == 11
    assert all(not Path(view.path).exists() for view in views)


def test_grouped_merge_receipts_and_token_allocations_rollback_together(tmp_path):
    views = [shard(tmp_path/f"worker-{i}.sqlite", i, deferred=True) for i in range(2)]
    with VocabularyCounts(str(tmp_path/"master.sqlite"), durable=True, defer_signatures=True) as counts:
        counts.db.execute("CREATE TRIGGER reject BEFORE INSERT ON batches BEGIN SELECT RAISE(ABORT,'interrupted'); END")
        counts.db.commit()
        with pytest.raises(sqlite3.IntegrityError, match="interrupted"):
            counts.merge_many(views)
        for table in ("counts", "signatures", "batches", "tokens"):
            assert counts.db.execute(f"SELECT count(*) FROM {table}").fetchone()[0] == 0
        assert counts.tokens == counts.token_ids == {}
        assert all(Path(view.path).exists() for view in views)
        counts.db.execute("DROP TRIGGER reject")
        counts.db.commit()
        counts.merge_many(views)
        assert dict(counts.view("bigram").items()) == {"a + b":3,"a + c":3,"b + c":3}


def test_duplicate_receipts_in_one_group_and_across_retries(tmp_path):
    first = shard(tmp_path/"first.sqlite", 0)
    duplicates = []
    for name in ("duplicate", "retry"):
        path = tmp_path/f"{name}.sqlite"
        shutil.copyfile(first.path, path)
        duplicates.append(CountView(str(path), "bigram"))
    second = shard(tmp_path/"second.sqlite", 1)
    with VocabularyCounts(str(tmp_path/"master.sqlite"), durable=True) as counts:
        counts.merge_many([first, duplicates[0]])
        counts.merge_many([duplicates[1], second])
        assert dict(counts.view("bigram").items()) == {"a + b":3,"a + c":3,"b + c":3}
        assert len(list(counts.completed_batches("count"))) == 2


def test_partial_receipt_overlap_rejected_without_deleting_sources(tmp_path):
    first = shard(tmp_path/"first.sqlite", 0)
    second = shard(tmp_path/"second.sqlite", 1)
    with sqlite3.connect(second.path) as db:
        db.execute("INSERT INTO batches VALUES ('count:0',NULL,1)")
    with VocabularyCounts(str(tmp_path/"master.sqlite"), durable=True) as counts:
        with pytest.raises(ValueError, match="overlapping"):
            counts.merge_many([first, second])
        assert list(counts.completed_batches("count")) == []
        assert counts.db.execute("SELECT count(*) FROM counts").fetchone()[0] == 0
    assert Path(first.path).exists() and Path(second.path).exists()


@pytest.mark.parametrize("group,expected_groups", [(1, [1, 1, 1]), (2, [2, 1])])
def test_parallel_materialization_grouping_is_opt_in(tmp_path, monkeypatch, group, expected_groups):
    monkeypatch.setattr(vocabulary, "_PARALLEL_MATERIALIZE_KEYS", 0)
    kwargs = {} if group == 1 else {"materialize_merge_size":group}
    with VocabularyCounts(str(tmp_path/"master.sqlite"), durable=True, defer_signatures=True,
                          materialize_workers=3, **kwargs) as counts:
        for i in range(3):
            counts.group_combinations("bigram", ["a", "b", f"c{i}"], 2)
        merged = []
        original = counts.merge_many
        def record(views):
            merged.append(len(views))
            original(views)
        monkeypatch.setattr(counts, "merge_many", record)
        assert dict(counts.view("bigram").items())["a + b"] == 3
        assert merged == expected_groups
