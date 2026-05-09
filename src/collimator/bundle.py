"""Bundle-layout helpers for routes that may ship one trained model or K.

A *bundle directory* is one route slot (general/, filegroups/<X>/, filetypes/<Y>/)
holding `feature_spec.json`, optional `calibrator.json`, and either:

* **Single-model layout** (legacy):
    bundle/model.txt          (LightGBM)
    bundle/model.json         (XGBoost)

* **Multi-seed layout** (item A):
    bundle/models/seed_42.txt
    bundle/models/seed_43.txt
    bundle/models/seed_44.txt
    ...

Inference over a multi-seed bundle averages the per-member probabilities, which
reduces seed-driven prediction variance by ~K while leaving the bias term
unchanged. The two layouts are mutually exclusive within one bundle (deploys
should choose one); having both is treated as an unrecoverable layout error.

The `Ensemble` class lets every read-side script in collimator stay agnostic
to which layout a bundle is in. Length-1 ensembles are mathematically identical
to the pre-item-A predict path on every input.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Iterable


# Recognized model-file extensions. .txt = LightGBM Booster dump, .json =
# XGBoost. Anything else under models/ is treated as a bystander (READMEs,
# hashes, etc.) and ignored, mirroring the litmus loader.
_MODEL_EXTS = (".txt", ".json")
_SEED_PREFIX = "seed_"


def model_files(bundle_dir: Path) -> list[Path]:
    """Return the trained-model files for a bundle, in deterministic order.

    Multi-seed layout (preferred): all ``models/seed_*.{txt,json}`` sorted by
    filename. Legacy layout (fallback): the single ``model.txt`` or
    ``model.json`` directly under ``bundle_dir``.

    Returns the empty list if the bundle has neither layout. Raises
    ``ValueError`` if the bundle has BOTH a populated ``models/`` directory
    and a top-level ``model.{txt,json}``, since that's an ambiguous deploy
    state and silently picking one would mask a packaging bug.
    """
    multi_dir = bundle_dir / "models"
    multi: list[Path] = []
    if multi_dir.is_dir():
        for entry in sorted(multi_dir.iterdir()):
            if not entry.is_file():
                continue
            if not entry.name.startswith(_SEED_PREFIX):
                continue
            if entry.suffix not in _MODEL_EXTS:
                continue
            multi.append(entry)

    legacy_xgb = bundle_dir / "model.json"
    legacy_lgb = bundle_dir / "model.txt"
    legacy: list[Path] = []
    if legacy_xgb.is_file():
        legacy.append(legacy_xgb)
    if legacy_lgb.is_file():
        legacy.append(legacy_lgb)

    if multi and legacy:
        raise ValueError(
            f"ambiguous bundle layout in {bundle_dir}: "
            f"both multi-seed (models/seed_*.{{txt,json}}) and legacy "
            f"(model.{{txt,json}}) artifacts exist; remove one to disambiguate."
        )
    if len(legacy) > 1:
        raise ValueError(
            f"ambiguous legacy bundle in {bundle_dir}: "
            f"both model.json and model.txt exist; remove one to disambiguate."
        )
    return multi if multi else legacy


def has_model(bundle_dir: Path) -> bool:
    """True iff the bundle has at least one trained-model file."""
    try:
        return bool(model_files(bundle_dir))
    except ValueError:
        # An ambiguous bundle DOES have models, just unclear which to use.
        return True


def primary_model_file(bundle_dir: Path) -> Path:
    """Return the first model file in deterministic order.

    Useful for read-side scripts that only need one representative model
    (e.g. inspecting feature importances) and don't actually need to do
    multi-seed averaged inference. Inference paths should use ``Ensemble``.

    Raises ``FileNotFoundError`` if no model is present.
    """
    files = model_files(bundle_dir)
    if not files:
        raise FileNotFoundError(f"no model file found in {bundle_dir}")
    return files[0]


def write_seed_model_path(bundle_dir: Path, seed: int, ext: str) -> Path:
    """Construct the canonical multi-seed write path for a given seed.

    The bundle's ``models/`` subdirectory is created if absent. ``ext`` is the
    backend-specific extension (``"txt"`` or ``"json"``); the leading dot is
    optional. The file itself is not created — caller writes it.
    """
    if ext.startswith("."):
        ext = ext[1:]
    if ext not in {e[1:] for e in _MODEL_EXTS}:
        raise ValueError(f"unsupported model extension {ext!r}; expected txt or json")
    multi_dir = bundle_dir / "models"
    multi_dir.mkdir(parents=True, exist_ok=True)
    return multi_dir / f"{_SEED_PREFIX}{int(seed)}.{ext}"


def atomic_write_json(path: Path, payload: Any, *, indent: int | None = 2) -> None:
    """Write ``payload`` as JSON to ``path`` atomically.

    Writes to a sibling temp file, fsyncs, then ``os.replace``s into place —
    so a partially-written file never appears at ``path``. Critical for files
    litmus or downstream pipeline steps load on every scan / cycle:
    ``calibrator.json``, ``config.json``, ``route_policies.json``, etc.
    A plain ``open(path, "w"); json.dump(...)`` truncates the destination at
    open time and a process kill mid-write leaves the truncated file
    persisted; the next reader gets corrupt JSON.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f, indent=indent)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        # Best-effort cleanup; the partial temp file shouldn't leak even if
        # the write or replace fails.  The destination is unaffected because
        # os.replace was the would-be commit point.
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


class Ensemble:
    """One-or-more trained models exposing a single ``predict_proba`` surface.

    For ``K=1`` (legacy single-model bundle) ``predict_proba`` is identical to
    calling the underlying model's ``predict_proba`` directly. For ``K>1`` the
    member probabilities are averaged in f64 (for summation stability) and
    returned as f32 — matching the litmus runtime's averaging semantics so
    collimator-side metrics agree with deployed scores.
    """

    def __init__(self, members: Iterable[Any]) -> None:
        members_list = list(members)
        if not members_list:
            raise ValueError("Ensemble must contain at least one trained model")
        self._members = members_list

    @classmethod
    def load_bundle(cls, bundle_dir: Path) -> Ensemble:
        """Load every trained-model file in the bundle into a single ensemble."""
        from collimator import model as _model  # noqa: PLC0415 — avoid cycle

        files = model_files(bundle_dir)
        if not files:
            raise FileNotFoundError(f"no model file found in {bundle_dir}")
        return cls([_model.load_model(p) for p in files])

    @property
    def n_members(self) -> int:
        return len(self._members)

    @property
    def primary(self) -> Any:
        """The first member.  Useful for callers that need one model object
        for backend introspection (feature names, importances) and don't care
        about averaging."""
        return self._members[0]

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Average member predict_proba outputs across the ensemble.

        K=1 path is mathematically identical to ``model.predict_proba(X)`` on
        the single member.  K>1 path averages in f64 then casts back to f32.
        """
        from collimator.model import predict_proba as _predict_proba  # noqa: PLC0415

        if len(self._members) == 1:
            return _predict_proba(self._members[0], X)
        accumulator = np.zeros(X.shape[0], dtype=np.float64)
        for m in self._members:
            accumulator += _predict_proba(m, X).astype(np.float64)
        return (accumulator / float(len(self._members))).astype(np.float32)
