"""Validate supervised vocabulary selection without holdout-label leakage."""
import importlib.util
import json
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split


def script(monkeypatch):
    directory = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(directory))
    spec = importlib.util.spec_from_file_location("keyword_python_selection", directory / "keyword_python_selection.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_selector_never_sees_either_seeds_holdout(monkeypatch):
    module = script(monkeypatch)
    labels = np.array([0] * 900 + [1] * 100)
    selected = set(module.selection_rows(labels))
    assert selected
    for seed in module.SEEDS:
        fitting, holdout = train_test_split(np.arange(len(labels)), test_size=.12,
                                           stratify=labels, random_state=seed)
        assert selected <= set(fitting)
        assert selected.isdisjoint(holdout)


def test_balanced_information_is_symmetric_and_rewards_both_classes(monkeypatch):
    module = script(monkeypatch)
    malware = np.array([50, 5, 5])
    benign = np.array([500, 10, 900])
    scores = module.balanced_information(malware, benign, 100, 1000)
    reverse = module.balanced_information(benign, malware, 1000, 100)
    np.testing.assert_allclose(scores, reverse)
    assert scores[1] > scores[0]
    assert scores[2] > scores[0]
    assert np.isfinite(module.balanced_information(100, 0, 100, 1000))


def test_ranking_changes_selection_and_excludes_unsupported_words(monkeypatch):
    module = script(monkeypatch)
    words = ["common", "malware_signal", "goodware_signal", "singleton"]
    bad = np.array([50, 30, 0, 1])
    good = np.array([500, 0, 300, 0])
    frequency = module.rank_words(words, bad, good, [1000, 100], "frequency")
    association = module.rank_words(words, bad, good, [1000, 100], "balanced_mi")
    assert frequency[0] == 0
    assert association[0] in (1, 2)
    assert association[-1] == 0
    assert 3 not in frequency and 3 not in association


def test_batch_keeps_row_order_and_serializable_revision_hashes(monkeypatch, tmp_path):
    module = script(monkeypatch)
    from types import SimpleNamespace

    monkeypatch.setattr(module.features.FeatureSpec, "load", lambda _: SimpleNamespace(total_features=1))
    monkeypatch.setattr(module.data, "fetch_cleave_results", lambda *a, **kw: {
        9: {"cleave_result": {"files": []}, "evaluation_digest": b"\x01\xff"},
        3: {"cleave_result": {"files": []}, "evaluation_digest": b"\x02\xfe"},
    })
    monkeypatch.setattr(module.features, "_extract_batch_worker", lambda args:
                        ([0, 1], [0, 0], [2., 3.], [label for _, label in args[1]]))
    rows = [{"row_id": 3, "label": 1}, {"row_id": 9, "label": 0}]
    stem, digests = module.extract_batch(("unused", rows, "unused", str(tmp_path), 0))
    assert json.loads(json.dumps(digests)) == ["02fe", "01ff"]
    assert module.sp.load_npz(stem + ".npz").toarray().tolist() == [[2.], [3.]]
    assert len(list(module.token_batches([stem]))) == 2


def test_cached_reorder_preserves_rows_and_excludes_dev_words(monkeypatch, tmp_path):
    module = script(monkeypatch)
    from types import SimpleNamespace
    import gzip
    import hashlib

    previous = tmp_path / "old"
    cache = previous / "inputs"
    cache.mkdir(parents=True)
    output = tmp_path / "new"
    output.mkdir()
    train_rows = [dict(row_id=i, label=int(i >= 80), group_id=str(i)) for i in range(100)]
    dev_rows = [dict(row_id=i, label=int(i >= 120), group_id=str(i)) for i in range(100, 140)]
    old_rows = train_rows[::-1] + dev_rows[::-1]
    ids = np.array([r["row_id"] for r in old_rows])
    labels = np.array([r["label"] for r in old_rows])
    np.savez(cache / "rows.npz", row_ids=ids, train_labels=labels[:100], dev_labels=labels[100:])
    base = module.sp.csr_matrix(ids[:, None], dtype=np.float32)
    module.sp.save_npz(cache / "base.npz", base)
    with gzip.open(cache / "batch-00000.json.gz", "wt") as stream:
        json.dump([{source: ["shared", "devonly"] if rid >= 100 else ["shared"]
                    for source in module.SOURCES} for rid in ids], stream)
    manifest = dict(feature_env={}, source_sha256={"features": hashlib.sha256(Path(module.features.__file__).read_bytes()).hexdigest()},
                    base_sha256=module.matrix_digest(base), snapshot="test", report_revision_sha256="test")
    (previous / "inputs.json").write_text(json.dumps(manifest))
    args = SimpleNamespace(output=output, reuse_inputs=previous, db="unused", workers=1)
    module.prepare(args, dict(feature_env={}, train_config={}), dict(train=train_rows, test=dev_rows),
                   SimpleNamespace(total_features=1))
    restored = module.sp.load_npz(output / "inputs/base.npz").toarray().ravel()
    np.testing.assert_array_equal(restored, np.arange(140))
    for source in module.SOURCES:
        info = json.loads((output / "inputs" / f"{source}.json").read_text())
        assert info["words"] == ["shared"]
