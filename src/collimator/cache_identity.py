"""Content identities for cached training work.

PostgreSQL's visibility snapshot detects committed inserts, updates and deletes
without scanning samples or relying on delayed statistics. It is deliberately
conservative: unrelated writes can cause a miss, never a stale cache hit.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
from functools import lru_cache
from pathlib import Path

from . import data


@lru_cache(maxsize=3)
def code_revision(stage: str) -> str:
    """Keep identities stable once captured by a running training process."""
    root = Path(__file__).parent
    names = {
        "corpus": ("data.py", "filegroups.py", "experiment.py", "cache_identity.py"),
        "features": ("features.py", "keywords.py", "matrix_store.py", "vocabulary.py", "vocabulary_runs.py", "allowlist.py", "data.py", "filegroups.py", "cache_identity.py"),
        "training": ("train.py", "keywords.py", "fit_resources.py", "model.py", "onnx_projection.py", "experiment.py", "export.py", "bundle.py", "cache_identity.py"),
    }[stage]
    h = hashlib.sha256()
    for name in names:
        h.update(name.encode())
        h.update((root / name).read_bytes())
    if stage == "training":
        for path in sorted((root / "thresholds").glob("*.py")):
            h.update(path.read_bytes())
    for package in ("numpy", "scipy", "scikit-learn", "lightgbm", "xgboost"):
        try:
            version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            version = "absent"
        h.update(f"{package}={version}".encode())
    return h.hexdigest()


def database_revision(db: Path | str) -> str:
    h = hashlib.sha256()
    # Sampled and full-corpus caches must never share an identity.
    h.update(data.SAMPLE_PREDICATE.encode())
    if data._is_pg(db):
        with data._connect(db) as conn:
            row = conn.execute(
                "SELECT current_database(), inet_server_addr()::text, "
                "inet_server_port(), pg_postmaster_start_time()::text, "
                "pg_current_snapshot()::text"
            ).fetchone()
        h.update(json.dumps(row).encode())
    else:
        path = Path(db).resolve()
        h.update(str(path).encode())
        for file in (path, Path(str(path) + "-wal")):
            if file.exists():
                with file.open("rb") as source:
                    for block in iter(lambda: source.read(1024 * 1024), b""):
                        h.update(block)
    return h.hexdigest()


def evaluation_hasher(db: Path | str):
    """Combine fixed-size row digests in sorted ID order, across any batch size."""
    h = hashlib.sha256(b"evaluation-v2\n")
    h.update(str(db if data._is_pg(db) else Path(db).resolve()).encode())
    h.update(b"\n")
    return h


def evaluation_row_digest(row) -> bytes:
    return hashlib.sha256(
        json.dumps(list(row), default=str, separators=(",", ":")).encode()
    ).digest()


def evaluation_revision(db: Path | str, row_ids: list[int], labels=None) -> str:
    """Fingerprint live evaluated rows, for comparisons against captured inputs."""
    h = evaluation_hasher(db)
    expected = dict(zip(row_ids, labels, strict=True)) if labels is not None else None
    found = 0
    with data._connect(db, repeatable_read=True) as conn:
        for row_id, label, version in data.evaluation_versions(conn, row_ids):
            found += 1
            if expected is not None and {"bad": 1, "good": 0}.get(label) != expected[row_id]:
                raise ValueError("evaluation labels changed; rerun screening")
            h.update(evaluation_row_digest(version))
    if found != len(row_ids):
        raise ValueError("evaluation rows were deleted; rerun screening")
    return h.hexdigest()


def model_revision(root: Path) -> str:
    """Hash the exact ensemble used for prediction, independent of its location."""
    from . import bundle
    h = hashlib.sha256()
    paths = bundle.model_files(root)
    if not paths:
        raise ValueError(f"no models in {root}")
    for path in paths:
        h.update(hashlib.sha256(path.read_bytes()).digest())
    return h.hexdigest()


def write_training_provenance(root: Path) -> dict:
    from . import bundle
    record = {"training_partitions": ["train"], "model_revision": model_revision(root)}
    spec = root / "feature_spec.json"
    if spec.is_file():
        record["spec_revision"] = hashlib.sha256(spec.read_bytes()).hexdigest()
    bundle.atomic_write_json(root / "training_provenance.json", record)
    return record


def require_reserved_dev(root: Path) -> None:
    """Do not claim held-out calibration for legacy or replaced models."""
    path = root / "training_provenance.json"
    record = json.loads(path.read_text()) if path.is_file() else {}
    if (record.get("training_partitions") != ["train"]
            or record.get("model_revision") != model_revision(root)
            or not (root / "feature_spec.json").is_file()
            or record.get("spec_revision") != hashlib.sha256((root / "feature_spec.json").read_bytes()).hexdigest()):
        raise ValueError(f"{root}: no matching train-only provenance; retrain before dev calibration")
