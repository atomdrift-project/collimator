"""Exact bounded selection, including rejected leaders, ties, and recovery."""
import json
import random
from pathlib import Path
import sqlite3

import pytest

from collimator import data, features, vocabulary
from collimator.vocabulary import CountView, VocabularyCounts


def test_ranked_pages_preserve_ties_collisions_and_separator_names(tmp_path, monkeypatch):
    monkeypatch.setattr(vocabulary, '_token_hash', lambda _: 7)
    triples = [('a', 'b + c', 'd'), ('a + b', 'c', 'd')]
    triples += [(f'p{i:03}', 'q', 'r') for i in range(80)]
    random.Random(31).shuffle(triples)
    with VocabularyCounts(str(tmp_path/'counts.sqlite')) as counts:
        for i, triple in enumerate(triples):
            counts.increment('trigram', triple, n=10 + i%3)
        expected = counts.top('trigram', 1000, 1)
        pages, boundary = [], None
        while page := counts.ranked_page('trigram', 3, 1, boundary):
            pages.extend(page)
            key,n = page[-1]
            boundary = (n, ' + '.join(counts.token_parts(key)), key.hex())
        assert len(pages) == len(triples)
        assert len({key for key,n in pages}) == len(triples)
        actual = [(-n, ' + '.join(counts.token_parts(key)), key) for key,n in pages]
        assert actual == sorted(actual)
        assert sorted(name for _,name,_ in actual) == expected


def test_ranked_shared_pages_sum_before_cutoffs(tmp_path):
    views = []
    for part in range(2):
        path = tmp_path/f'fold{part}.sqlite'
        with VocabularyCounts(str(path), stable_token_ids=False) as counts:
            counts.increment('trigram', ('a','b','c'), n=6)
            counts.increment('trigram', ('a','b','x' if part else 'y'), n=10)
            counts.record_batch(f'shared:{part}', None, 1)
        views.append(CountView(str(path), 'trigram'))
    with VocabularyCounts(str(tmp_path/'consumer.sqlite')) as counts:
        for view in views:
            counts.attach_shared(view)
        page = counts.ranked_page('trigram', 1, 10)
        assert [(counts.token_parts(key), n) for key,n in page] == [(('a','b','c'),12)]


@pytest.fixture
def selection_case(tmp_path, monkeypatch):
    rng = random.Random(411)
    triples = [(f'p{i:03}', 'q', 'r') for i in range(70)]
    frequencies = {triple:rng.randint(5,10) for triple in triples}
    reports = {}
    for rid in range(1,9):
        files = [list(triple) for triple in triples if rng.random() < .6]
        reports[rid] = {'cleave_result': {'files': files + files[:3]}}
    monkeypatch.setattr(data, 'fetch_cleave_results', lambda _, ids: {rid:reports[rid] for rid in ids})
    monkeypatch.setattr(features, '_coerce_report', lambda value:value)
    monkeypatch.setattr(features, 'report_files', lambda report:report['files'])
    monkeypatch.setattr(features, '_ranked_ngram_paths', lambda file, _:file)
    def create(path):
        counts = VocabularyCounts(str(path), durable=True, resume=path.exists())
        if not counts.state('initialized'):
            for triple,n in frequencies.items():
                counts.increment('trigram', triple, n=n)
            counts.flush()
            counts.set_state('initialized',True)
        return counts
    return reports,create


def select(counts, root, reports, **kwargs):
    return features._select_trigram_vocabulary('fake', list(reports), 1, counts, str(root),
        limit=kwargs.get('limit',7), minimum=5, benign_ceiling=kwargs.get('ceiling',3), batch_size=3)


@pytest.mark.parametrize('page_size', [1,4,17,4096])
@pytest.mark.parametrize('ceiling', [0,3,8])
def test_shortlist_matches_exhaustive_with_rejection_and_ties(selection_case, tmp_path, monkeypatch, page_size, ceiling):
    reports, create = selection_case
    monkeypatch.setenv('COLLIMATOR_TRIGRAM_SHORTLIST','0')
    with create(tmp_path/'reference.sqlite') as counts:
        expected = select(counts,tmp_path,reports,ceiling=ceiling)
    monkeypatch.setenv('COLLIMATOR_TRIGRAM_SHORTLIST','1')
    monkeypatch.setenv('COLLIMATOR_TRIGRAM_SHORTLIST_SIZE',str(page_size))
    with create(tmp_path/'shortlist.sqlite') as counts:
        actual = select(counts,tmp_path,reports,ceiling=ceiling)
        assert actual == expected
        state = counts.state('trigram_selection')
        assert state['complete']
        assert 'page' not in state or not state['page']
        assert state['tested'] <= 70
        if ceiling==8 and page_size<70:
            assert state['tested'] < 70


@pytest.mark.parametrize('interruption', ['batch_commit','round_commit'])
def test_resume_does_not_recount_or_skip_candidates(selection_case, tmp_path, monkeypatch, interruption):
    reports,create = selection_case
    monkeypatch.setenv('COLLIMATOR_TRIGRAM_SHORTLIST_SIZE','4')
    with create(tmp_path/'reference.sqlite') as counts:
        expected = select(counts,tmp_path,reports)
    merge,set_state = VocabularyCounts.merge,VocabularyCounts.set_state
    interrupted = False
    def merge_then_fail(self,view,*args,**kwargs):
        nonlocal interrupted
        merge(self,view,*args,**kwargs)
        if not interrupted and view.family=='benign_trigram':
            interrupted=True
            raise RuntimeError('interrupted batch commit')
    def state_then_fail(self,key,value):
        nonlocal interrupted
        set_state(self,key,value)
        if not interrupted and key=='trigram_selection' and value['round']>=1:
            interrupted=True
            raise RuntimeError('interrupted round commit')
    monkeypatch.setattr(VocabularyCounts, 'merge' if interruption=='batch_commit' else 'set_state',
                        merge_then_fail if interruption=='batch_commit' else state_then_fail)
    with pytest.raises(RuntimeError,match='interrupted'):
        with create(tmp_path/'resume.sqlite') as counts:
            select(counts,tmp_path,reports)
    monkeypatch.setattr(VocabularyCounts,'merge',merge)
    monkeypatch.setattr(VocabularyCounts,'set_state',set_state)
    monkeypatch.setenv('COLLIMATOR_TRIGRAM_SHORTLIST_SIZE','9')
    with create(tmp_path/'resume.sqlite') as counts:
        assert select(counts,tmp_path,reports) == expected
        monkeypatch.setattr(data,'fetch_cleave_results',lambda *_:pytest.fail('reread completed selection'))
        assert select(counts,tmp_path,reports) == expected
        monkeypatch.setenv('COLLIMATOR_TRIGRAM_SHORTLIST','0')
        with pytest.raises(ValueError,match='mode changed'):
            select(counts,tmp_path,reports)


@pytest.mark.parametrize('interruption', ['fallback_start','fallback_batch'])
def test_reject_heavy_fallback_resumes_with_exact_counts(selection_case,tmp_path,monkeypatch,interruption):
    reports,create=selection_case
    monkeypatch.setenv('COLLIMATOR_TRIGRAM_SHORTLIST','0')
    with create(tmp_path/'reference.sqlite') as counts:
        expected=select(counts,tmp_path,reports)
        expected_counts=dict(counts.view('benign_trigram').items())
    monkeypatch.setenv('COLLIMATOR_TRIGRAM_SHORTLIST','1')
    monkeypatch.setenv('COLLIMATOR_TRIGRAM_SHORTLIST_SIZE','1')
    merge,set_state=VocabularyCounts.merge,VocabularyCounts.set_state
    interrupted=False
    def merge_then_fail(self,view,*args,**kwargs):
        nonlocal interrupted
        merge(self,view,*args,**kwargs)
        if not interrupted and self.state('trigram_selection',{}).get('fallback'):
            interrupted=True
            raise RuntimeError('fallback batch')
    def state_then_fail(self,key,value):
        nonlocal interrupted
        set_state(self,key,value)
        if not interrupted and key=='trigram_selection' and value.get('fallback'):
            interrupted=True
            raise RuntimeError('fallback start')
    monkeypatch.setattr(VocabularyCounts,'merge' if interruption=='fallback_batch' else 'set_state',
                        merge_then_fail if interruption=='fallback_batch' else state_then_fail)
    with pytest.raises(RuntimeError,match='fallback'):
        with create(tmp_path/'resume.sqlite') as counts:
            select(counts,tmp_path,reports)
    monkeypatch.setattr(VocabularyCounts,'merge',merge)
    monkeypatch.setattr(VocabularyCounts,'set_state',set_state)
    with create(tmp_path/'resume.sqlite') as counts:
        assert select(counts,tmp_path,reports)==expected
        assert counts.state('trigram_selection')['fallback']
        assert dict(counts.view('benign_trigram').items())==expected_counts
