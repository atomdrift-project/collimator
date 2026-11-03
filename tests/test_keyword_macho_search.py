"""Research direction filters and the untouched confirmation boundary."""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
import scipy.sparse as sp


def script(monkeypatch):
    directory = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(directory))
    spec = importlib.util.spec_from_file_location("keyword_macho_search", directory / "keyword_macho_search.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sampling_keeps_canonical_groups_together(monkeypatch):
    module = script(monkeypatch)
    for i in range(100):
        group = f"{i:064x}"
        assert module.sampled(group) == module.sampled(group.upper())
        assert not module.sampled(group, 0)
        assert module.sampled(group, 100)


def test_goodware_only_direction_is_fit_local_and_restores_selector(monkeypatch):
    module = script(monkeypatch)
    y = np.array([0]*20+[1]*20)
    x = sp.csr_matrix(np.column_stack([1-y,y,np.ones(40)]).astype(np.float32))
    names = ["ruleword:good", "ruleword:bad", "base"]
    settings = {"ruleword":dict(selection="balanced_mi",min_freq=2,vocab_max=1,candidate_max=100)}
    original = module.keywords.select_for_fit
    with module.goodware_only_selection({"ruleword"}):
        masked, stats = module.keywords.select_for_fit(x,y,names,settings)
        np.testing.assert_array_equal(masked.toarray()[:,0],1-y)
        assert not masked.toarray()[:,1].any()
        np.testing.assert_array_equal(masked.toarray()[:,2],1)
        assert stats["ruleword"]["research_direction"] == "goodware_only"
    assert module.keywords.select_for_fit is original
    np.testing.assert_array_equal(x.toarray()[:,1],y)


def test_lock_and_refine_cannot_reopen_confirmation(monkeypatch,tmp_path):
    module = script(monkeypatch)
    study=module.Study.__new__(module.Study)
    study.root=tmp_path
    (tmp_path/"locked_finalists.json").write_text("{}")
    for action in (study.screen,study.refine,study.budgets,study.availability,study.lock_finalists):
        with pytest.raises(ValueError,match="locked"):
            action()


def test_finalist_choice_uses_search_only_and_keeps_standard_candidate(monkeypatch,tmp_path):
    module=script(monkeypatch)
    study=module.Study.__new__(module.Study)
    study.root=tmp_path
    study.summary_path=tmp_path/"search.json"
    study.summary=dict(variants={})
    for name,method,recall in [("baseline",None,.5),("research","goodware_only",.8),
                               ("standard","balanced_mi",.7),("frequency","frequency",.6)]:
        study.summary["variants"][name]=dict(name=name,options={} if method is None else
            {"ruleword":dict(method=method,cap=1000,floor=5)},search=dict(ap=.9,auc=.95,recall_0fp=recall,recall_1fp=recall))
    study.summary_path.write_text(json.dumps(study.summary))
    (tmp_path/"refinement_plan.json").write_text("{}")
    study.lock_finalists()
    locked=json.loads((tmp_path/"locked_finalists.json").read_text())
    assert locked["names"][:3]==["baseline","research","standard"]
    assert "frequency" in locked["names"]
    assert locked["seeds"]==[43,44,45,46]


def test_pe_uses_separate_default_output(monkeypatch):
    module=script(monkeypatch)
    captured=[]
    monkeypatch.setattr(module,"prepare",captured.append)
    monkeypatch.setattr("sys.argv",["keyword_macho_search.py","prepare","--route","pe"])
    module.main()
    assert captured[0].route=="pe"
    assert captured[0].output==Path("out/experiments/keyword-pe-search")


def test_route_mismatch_is_rejected_before_running(monkeypatch,tmp_path):
    from types import SimpleNamespace
    module=script(monkeypatch)
    monkeypatch.setattr(module,"Study",lambda root:SimpleNamespace(manifest={"route":"filetypes/macho"}))
    monkeypatch.setattr("sys.argv",["keyword_macho_search.py","screen","--route","pe","--output",str(tmp_path)])
    with pytest.raises(ValueError,match="route does not match"):
        module.main()


def test_confirmation_cap_preserves_search_groups_and_ignores_labels(monkeypatch):
    module=script(monkeypatch)
    rows=[dict(group_id=f"{i:064x}",label=i%2) for i in range(100)]
    rows+=rows[:20]
    selected=module.bound_confirmation(rows,12)
    assert len({r["group_id"] for r in selected if not module.sampled(r["group_id"])})==12
    assert [r for r in selected if module.sampled(r["group_id"])]==[r for r in rows if module.sampled(r["group_id"])]
    flipped=[dict(r,label=1-r["label"]) for r in rows]
    assert [r["group_id"] for r in selected]==[r["group_id"] for r in module.bound_confirmation(flipped,12)]
    assert module.bound_confirmation(rows,0) is rows


def test_conflict_exclusion_removes_entire_canonical_group(monkeypatch):
    module=script(monkeypatch)
    rows=[dict(group_id="aa",label=0),dict(group_id="AA",label=1),
          dict(group_id="bb",label=0),dict(group_id="bb",label=0)]
    clean,excluded=module.exclude_label_conflicts(rows)
    assert clean==rows[2:]
    assert excluded==rows[:2]


def test_canonical_metrics_count_each_group_once_and_reject_conflicts(monkeypatch):
    script(monkeypatch)
    from summarize_macho_keywords import canonical_metrics
    result=canonical_metrics([0,0,1,1],[.1,.2,.8,.9],["aa","AA","bb","cc"])
    assert result["goodware"]==1
    assert result["malware"]==2
    assert result["recall_0fp"]==1
    with pytest.raises(ValueError,match="contradictory"):
        canonical_metrics([0,1],[.1,.2],["aa","AA"])
