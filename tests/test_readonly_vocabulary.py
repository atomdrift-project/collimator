"""Read-only fold queries sum before filtering and preserve indexed lookups."""
from pathlib import Path
import shutil
import sqlite3

import pytest

from collimator import vocabulary
from collimator.vocabulary import CountView, DiskTrigramCandidates, TrigramSource, VocabularyCounts


def source(path, part, stable):
    with VocabularyCounts(str(path), stable_token_ids=stable) as counts:
        if part == 0:
            counts._token_id("z-first")  # Different dictionaries, including collision resolution.
        counts.group_combinations("trigram", ["a","b","c"], 3, n=6)
        counts.group_combinations("trigram", ["a","b","x" if part == 0 else "y"], 3, n=10)
        counts.record_batch(f"shared:{part}", None, 16)
    return CountView(str(path), "trigram")


@pytest.mark.parametrize("stable", [False,True])
@pytest.mark.parametrize("collision", [False,True])
def test_sum_before_threshold_and_top_k_without_copying_counts(tmp_path,monkeypatch,stable,collision):
    if collision:
        monkeypatch.setattr(vocabulary,"_token_hash",lambda _:7)
    views=[source(tmp_path/f"source{i}.sqlite",i,stable) for i in range(2)]
    target=tmp_path/"consumer.sqlite"
    with VocabularyCounts(str(target),durable=True) as counts:
        for view in views:counts.attach_shared(view)
        # Common triple is below the cutoff and outside top-1 in each source,
        # but is the most frequent triple in their union.
        assert counts.top("trigram",1,10)==["a + b + c"]
        assert counts.count_at_least("trigram",10)==3
        assert counts.at_least("trigram",11)==["a + b + c"]
        assert dict(counts.view("trigram").items())=={"a + b + c":12,"a + b + x":10,"a + b + y":10}
        assert counts.db.execute("SELECT count(*) FROM counts").fetchone()[0]==0
        counts.increment("benign_trigram",("a","b","c"),n=1)
        assert counts.top("trigram",1,10,benign_family="benign_trigram")==["a + b + x"]
        assert counts.db.execute("SELECT count(*) FROM counts WHERE family='trigram'").fetchone()[0]==0
        index=DiskTrigramCandidates(TrigramSource(str(target),10),cache_bytes=128)
        try:
            assert set(index.matches(["a","b","c","x","y"]))=={
                ("a","b","c"),("a","b","x"),("a","b","y")}
        finally:index.close()
    # Reopening restores source locations and dictionary mappings, not copies.
    with VocabularyCounts(str(target),durable=True,resume=True) as counts:
        for view in views:counts.attach_shared(view)
        assert counts.top("trigram",1,10,benign_family="benign_trigram")==["a + b + x"]
        assert len(list(counts.completed_batches("shared")))==2


def test_source_registration_is_atomic(tmp_path):
    view=source(tmp_path/"source.sqlite",0,True)
    with VocabularyCounts(str(tmp_path/"consumer.sqlite"),durable=True) as counts:
        counts.db.execute("CREATE TRIGGER reject BEFORE INSERT ON state WHEN NEW.key='readonly_sources' BEGIN SELECT RAISE(ABORT,'interrupted'); END")
        counts.db.commit()
        with pytest.raises(sqlite3.IntegrityError,match="interrupted"):
            counts.attach_shared(view)
        assert counts.state("readonly_sources")==None
        assert list(counts.completed_batches("shared"))==[]
        assert counts.token_ids=={}
        counts.db.execute("DROP TRIGGER reject");counts.db.commit()
        counts.attach_shared(view)
        assert counts.count_at_least("trigram",1)==2


@pytest.mark.parametrize("change", ["replace","delete"])
def test_recovery_rejects_missing_or_replaced_source(tmp_path,change):
    view=source(tmp_path/"source.sqlite",0,True)
    target=tmp_path/"consumer.sqlite"
    with VocabularyCounts(str(target),durable=True) as counts:
        counts.attach_shared(view)
    if change=="replace":
        replacement=tmp_path/"replacement.sqlite"
        shutil.copyfile(view.path,replacement)
        replacement.replace(view.path)
        error=ValueError
    else:
        Path(view.path).unlink();error=FileNotFoundError
    with VocabularyCounts(str(target),durable=True,resume=True) as counts:
        with pytest.raises(error):counts.top("trigram",1,1)


def test_composite_view_cannot_silently_merge_only_its_local_counts(tmp_path):
    view=source(tmp_path/"source.sqlite",0,True)
    with VocabularyCounts(str(tmp_path/"composite.sqlite"),durable=True) as composite:
        composite.attach_shared(view)
        composite_view=composite.view("trigram")
        with VocabularyCounts(str(tmp_path/"consumer.sqlite"),durable=True) as counts:
            with pytest.raises(ValueError,match="composite"):
                counts.merge(composite_view)
    assert Path(composite_view.path).exists()


def test_in_memory_consumer_reads_its_shared_frequencies(tmp_path):
    view=source(tmp_path/"source.sqlite",0,True)
    with VocabularyCounts() as counts:
        counts.attach_shared(view)
        assert counts.view("trigram")=={"a + b + c":6,"a + b + x":10}


def test_qualified_counts_handle_lower_cutoffs_and_new_local_counts(tmp_path):
    views=[source(tmp_path/f"source{i}.sqlite",i,True) for i in range(2)]
    with VocabularyCounts(str(tmp_path/"consumer.sqlite"),durable=True) as counts:
        for view in views:counts.attach_shared(view)
        assert counts.count_at_least("trigram",11)==1
        assert counts.count_at_least("trigram",10)==3
        counts.increment("trigram",("a","b","x"),n=5)
        assert counts.top("trigram",1,10)==["a + b + x"]
