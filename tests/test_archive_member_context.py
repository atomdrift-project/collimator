"""Archive context is reconstructed from verdicts and tracked in cache identities."""
import json
import sqlite3

from collimator import cache_identity, data, features, model_config
from collimator.demo import add_sample, create_schema, set_report


def corpus(tmp_path):
    path = tmp_path / "samples.db"
    with sqlite3.connect(path) as conn:
        create_schema(conn)
        add_sample(conn, sample_id=1, sha256="01" * 32, label="good",
                   report={"traits": [{"id": "inherited", "crit": 4, "conf": 1}]},
                   members=[(2, "module.py"), (3, "missing.py")], path="wheel.whl")
        add_sample(conn, sample_id=2, sha256="02" * 32, label="bad",
                   report={"ctx": [{"s": "import subprocess"}]})
    return path


def test_member_context_and_cache_identity(tmp_path):
    path = corpus(tmp_path)
    result = data.fetch_cleave_results(path, [1], evaluation_labels={1: 0})[1]
    files = result["cleave_result"]["files"]
    assert files[1]["ctx"] == [{"s": "import subprocess"}]
    assert features._report_keywords(files, ["contextword"])["contextword"] == {"import", "subprocess"}
    h = cache_identity.evaluation_hasher(path)
    h.update(result["evaluation_digest"])
    assert h.hexdigest() == cache_identity.evaluation_revision(path, [1], [0])
    before = h.hexdigest()
    with sqlite3.connect(path) as conn:
        set_report(conn, 2, {"ctx": [{"s": "new context"}]})
    after = cache_identity.evaluation_revision(path, [1], [0])
    assert before != after
    with sqlite3.connect(path) as conn:
        add_sample(conn, sample_id=3, sha256="03" * 32, label="good",
                   report={"ctx": [{"s": "late context"}]})
    assert cache_identity.evaluation_revision(path, [1], [0]) != after


def test_whl_default_exposes_member_context_recipe():
    accepted = model_config.load("filetypes/whl")
    run = model_config.as_run(accepted)
    assert run["feature_env"]["COLLIMATOR_ARCHIVE_MEMBER_CONTEXT"] == "1"
    assert run["feature_env"]["COLLIMATOR_CONTEXT_KEYWORD_VOCAB_MAX"] == "5000"
    assert run["feature_env"]["COLLIMATOR_CONTEXT_KEYWORD_MIN_FREQ"] == "2"
    assert run["ensemble_seeds"] == [43, 44, 45, 46]


def test_member_trains_alone_nested_as_scan_scores_it(tmp_path):
    """A sample hopper never scanned on its own is an archive member. Scan scores each
    embedded node alone, as one entry that keeps its depth, so the member is reported
    that way: no files beneath it, depth MEMBER_DEPTH; a scanned archive keeps its tree."""
    path = tmp_path / "samples.db"
    with sqlite3.connect(path) as conn:
        create_schema(conn)
        add_sample(conn, sample_id=1, sha256="01" * 32, label="bad", file_type="jar",
                   report={"mol": "Os", "risk": 3, "traits": [{"id": "t", "crit": 3}]},
                   members=[(2, "inner.jar")], path="/data/outer.jar")
        add_sample(conn, sample_id=2, sha256="02" * 32, label="bad", file_type="jar", scanned=False,
                   report={"mol": "Os", "risk": 5, "traits": [{"id": "u", "crit": 5}]},
                   members=[(3, "Evil.class")])
        add_sample(conn, sample_id=3, sha256="03" * 32, label="bad", file_type="java_class", scanned=False,
                   report={"traits": [{"id": "v", "crit": 4}]})
    got = data.fetch_cleave_results(path, [1, 2, 3])
    archive = got[1]["cleave_result"]["files"]
    assert [f["depth"] for f in archive] == [0, 1, 2]
    assert archive[1]["type"] == "jar" and archive[1]["pid"] == 0
    member = got[2]["cleave_result"]["files"]
    assert len(member) == 1, "a member is reported alone: scan never shows it its own children"
    assert member[0]["depth"] == data.MEMBER_DEPTH == 1
    assert member[0]["traits"] == [{"id": "u", "crit": 5}]
    assert got[2]["score"] == 5 and got[2]["formula"] == "Os"
    assert got[3]["cleave_result"]["files"][0]["depth"] == data.MEMBER_DEPTH

