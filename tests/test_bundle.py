"""Unit tests for collimator.bundle layout helpers."""

from pathlib import Path

import numpy as np
import pytest

from collimator.bundle import (
    Ensemble,
    has_model,
    model_files,
    primary_model_file,
    write_seed_model_path,
)


def test_model_files_legacy_lightgbm(tmp_path: Path) -> None:
    (tmp_path / "model.txt").write_text("dummy")
    (tmp_path / "feature_spec.json").write_text("{}")
    files = model_files(tmp_path)
    assert files == [tmp_path / "model.txt"]
    assert has_model(tmp_path)
    assert primary_model_file(tmp_path) == tmp_path / "model.txt"


def test_model_files_legacy_xgboost(tmp_path: Path) -> None:
    (tmp_path / "model.json").write_text("dummy")
    files = model_files(tmp_path)
    assert files == [tmp_path / "model.json"]


def test_model_files_multi_seed(tmp_path: Path) -> None:
    multi = tmp_path / "models"
    multi.mkdir()
    (multi / "seed_44.txt").write_text("dummy")
    (multi / "seed_42.txt").write_text("dummy")
    (multi / "seed_43.txt").write_text("dummy")
    files = model_files(tmp_path)
    # Filename-sorted order is deterministic.
    assert files == [
        multi / "seed_42.txt",
        multi / "seed_43.txt",
        multi / "seed_44.txt",
    ]
    assert primary_model_file(tmp_path) == multi / "seed_42.txt"


def test_model_files_ignores_bystanders(tmp_path: Path) -> None:
    multi = tmp_path / "models"
    multi.mkdir()
    (multi / "seed_42.txt").write_text("dummy")
    (multi / "README.md").write_text("notes")
    (multi / "metadata.json").write_text("{}")  # not a seed_ prefix → ignored
    (multi / "seed_43.txt.bak").write_text("backup")  # wrong ext → ignored
    files = model_files(tmp_path)
    assert files == [multi / "seed_42.txt"]


def test_model_files_rejects_ambiguous_layout(tmp_path: Path) -> None:
    (tmp_path / "model.txt").write_text("dummy")
    multi = tmp_path / "models"
    multi.mkdir()
    (multi / "seed_42.txt").write_text("dummy")
    with pytest.raises(ValueError, match="ambiguous"):
        model_files(tmp_path)


def test_model_files_rejects_legacy_both_extensions(tmp_path: Path) -> None:
    (tmp_path / "model.txt").write_text("dummy")
    (tmp_path / "model.json").write_text("{}")
    with pytest.raises(ValueError, match="ambiguous"):
        model_files(tmp_path)


def test_model_files_returns_empty_when_bundle_has_no_model(tmp_path: Path) -> None:
    (tmp_path / "feature_spec.json").write_text("{}")
    assert model_files(tmp_path) == []
    assert not has_model(tmp_path)
    with pytest.raises(FileNotFoundError):
        primary_model_file(tmp_path)


def test_write_seed_model_path_creates_dir_and_returns_canonical_path(tmp_path: Path) -> None:
    p = write_seed_model_path(tmp_path, 42, "txt")
    assert p == tmp_path / "models" / "seed_42.txt"
    assert (tmp_path / "models").is_dir()


def test_write_seed_model_path_accepts_dotted_extension(tmp_path: Path) -> None:
    p = write_seed_model_path(tmp_path, 42, ".json")
    assert p == tmp_path / "models" / "seed_42.json"


def test_write_seed_model_path_rejects_unknown_extension(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unsupported"):
        write_seed_model_path(tmp_path, 42, "onnx")


class _FakeModel:
    """Stand-in for an XGB/LGB classifier used to exercise Ensemble averaging
    without paying for real training in the unit test."""

    __module__ = "lightgbm.basic"  # so collimator.model.predict_proba dispatches correctly

    def __init__(self, value: float) -> None:
        self._value = value

    def predict(self, X: np.ndarray, **_: object) -> np.ndarray:
        return np.full(X.shape[0], self._value, dtype=np.float32)


def test_ensemble_k1_passes_through(tmp_path: Path) -> None:
    e = Ensemble([_FakeModel(0.7)])
    X = np.zeros((4, 3), dtype=np.float32)
    probs = e.predict_proba(X)
    assert probs.shape == (4,)
    assert probs.dtype == np.float32
    np.testing.assert_allclose(probs, 0.7, rtol=0, atol=1e-6)
    assert e.n_members == 1


def test_ensemble_k3_averages(tmp_path: Path) -> None:
    e = Ensemble([_FakeModel(0.2), _FakeModel(0.6), _FakeModel(0.7)])
    X = np.zeros((4, 3), dtype=np.float32)
    probs = e.predict_proba(X)
    assert probs.shape == (4,)
    # Mean of 0.2, 0.6, 0.7 is 0.5 exactly.
    np.testing.assert_allclose(probs, 0.5, rtol=0, atol=1e-6)
    assert e.n_members == 3


def test_ensemble_rejects_empty() -> None:
    with pytest.raises(ValueError, match="at least one"):
        Ensemble([])
