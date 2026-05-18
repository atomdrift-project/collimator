"""Combine k=2 fold-trained specialist models into per-route OOF score tables.

The route-aware sibling of ``azoth_oof_score.py``. Where that script merges
two fold-trained ``general`` bundles into honest OOF general probabilities,
this script does the same for every ``filegroups/*`` and ``filetypes/*``
specialist that exists in both fold roots.

Background: ``azoth_specialist_suite.py`` honors ``EXP_OOF_FOLD_EXCLUDE``
(landed in PR 1) so a specialist trained with that env set to 0 never sees
fold-0 rows. The fold-A bundle (trained with ``EXP_OOF_FOLD_EXCLUDE=0``)
can therefore produce honest OOF predictions on fold-0 rows; the fold-B
bundle does the same for fold-1 rows. Test rows have ``oof_fold_of`` ==
None — they're held out from both fold models and are scored by the
production single-fold bundle, which never saw them at training time
either.

Output: ``<output-dir>/<route_path>/threshold_scores.npz`` per route. The
schema matches what ``azoth_oof_score.py`` writes (row_ids, sha256, paths,
scores, labels, probs, canonical_shas, plus corpus_* metadata). The
downstream consumer in ``azoth_calibrate_ensemble.py --oof-route-scores-dir``
reads these files in lieu of running its own in-sample ``predict_proba``
pass.

Why this exists: the current score_table.npz carries in-sample specialist
probabilities (the specialist was trained on train+dev, then scored those
same rows). Every measurement we make against that table — the recall-
monotone floor, per-route Pareto curves, stacker fit data — inherits a
small bias toward "the specialist is always right." Honest OOF probs
eliminate the bias; future ensemble work can then be evaluated on a
solid foundation. See the long-run-quality discussion in the session
notes for why this is the foundation rather than another single fix.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np

_SCRIPTS = Path(__file__).resolve().parent
_SRC = _SCRIPTS.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from collimator import bundle, data, features  # noqa: E402
from collimator.model import load_model, predict_proba  # noqa: E402

LOG = logging.getLogger("azoth_oof_score_routes")


def _route_model_and_spec(route_dir: Path) -> tuple[Path, Path]:
    """Locate the primary model file and feature spec for a route bundle.

    Multi-seed bundles ship ``models/seed_*.txt``; legacy bundles ship a
    single ``model.txt``. The OOF merge averages with the production
    layout via the same logic ``azoth_calibrate_ensemble._score_route``
    uses (``bundle.Ensemble.load_bundle``), so a multi-seed fold bundle
    is fine here. We pick a representative model just to detect the
    layout — actual scoring uses the ensemble below.
    """
    spec = route_dir / "feature_spec.json"
    if not spec.is_file():
        raise FileNotFoundError(f"missing feature_spec.json under {route_dir}")
    if (route_dir / "model.txt").is_file():
        return route_dir / "model.txt", spec
    seeds = sorted((route_dir / "models").glob("seed_*.txt"))
    if not seeds:
        raise FileNotFoundError(f"no model.txt or models/seed_*.txt under {route_dir}")
    return seeds[0], spec


def _route_paths(root: Path) -> dict[str, Path]:
    """Map ``"filegroups/<name>"`` / ``"filetypes/<name>"`` to its bundle dir."""
    out: dict[str, Path] = {}
    for kind in ("filegroups", "filetypes"):
        parent = root / kind
        if not parent.is_dir():
            continue
        for child in parent.iterdir():
            if not child.is_dir():
                continue
            if not (child / "feature_spec.json").is_file():
                continue
            if not (child / "model.txt").is_file() and not (child / "models").is_dir():
                continue
            out[f"{kind}/{child.name}"] = child
    return out


def _load_route_file_types(summary_path: Path) -> dict[str, list[str]]:
    """Return ``{route_name: [file_types]}`` from a specialists.json summary.

    Mirrors ``azoth_calibrate_ensemble._load_routes`` — same ``results``
    array, same ``filegroup``/``filetype`` kind values, same
    ``filegroups/<name>`` / ``filetypes/<name>`` route-key convention.
    """
    with open(summary_path) as f:
        summary = json.load(f)
    out: dict[str, list[str]] = {}
    for entry in summary.get("results", []):
        if entry.get("error"):
            continue
        kind = entry.get("kind", "")
        name = entry.get("name", "")
        if not name or kind not in {"filegroup", "filetype"}:
            continue
        file_types = entry.get("file_types") or []
        route_name = (
            f"filegroups/{name}" if kind == "filegroup" else f"filetypes/{name}"
        )
        out[route_name] = [str(ft) for ft in file_types]
    return out


def _fetch_route_rows(
    db_path: Path | str,
    file_types: list[str],
    max_id: int,
) -> list[tuple[int, str, str, int, int, str]]:
    """Return labeled rows for the given file_types in metadata-full shape.

    Tuple format matches ``data.stream_labeled_metadata_full``:
    ``(row_id, sha256, path, score, label, split_key)``. We construct it
    via direct SQL so we can apply the file_type filter at the database
    rather than streaming the entire labeled corpus per route.
    """
    if not file_types:
        return []
    marker = "%s" if data._is_pg(db_path) else "?"  # noqa: SLF001
    where = [
        "label IN ('bad', 'good')",
        "cleave_result IS NOT NULL",
        "skip = ''",
    ]
    params: list[Any] = []
    if max_id > 0:
        where.append(f"id <= {marker}")
        params.append(int(max_id))
    select = (
        "SELECT id, sha256, path, score, label, canonical_sha256 FROM samples"
    )
    rows: list[tuple[int, str, str, int, int, str]] = []
    with data._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if data._is_pg(db_path):  # noqa: SLF001
            where.append("file_type = ANY(%s)")
            params.append(list(file_types))
            query = select + " WHERE " + " AND ".join(where) + " ORDER BY id"
            with conn.cursor() as cur:
                cur.execute(query, params)
                for row_id, sha256, path, score, label, canonical in cur:
                    split_key = canonical or sha256
                    rows.append((
                        int(row_id), str(sha256), str(path or ""),
                        int(score or 0), data._label_int(str(label)),  # noqa: SLF001
                        str(split_key),
                    ))
        else:
            placeholders = ",".join("?" for _ in file_types)
            where.append(f"file_type IN ({placeholders})")
            params.extend(file_types)
            query = select + " WHERE " + " AND ".join(where) + " ORDER BY id"
            for row_id, sha256, path, score, label, canonical in conn.execute(query, params):
                split_key = canonical or sha256
                rows.append((
                    int(row_id), str(sha256), str(path or ""),
                    int(score or 0), data._label_int(str(label)),  # noqa: SLF001
                    str(split_key),
                ))
    return rows


def _score_rows(
    db_path: Path | str,
    rows: list[tuple[int, str, str, int, int, str]],
    bundle_dir: Path,
    *,
    workers: int,
) -> dict[str, np.ndarray]:
    """Run a bundle over the given rows; return arrays in row_id order.

    Uses ``bundle.Ensemble.load_bundle`` so multi-seed bundles average
    member predictions the same way ``azoth_calibrate_ensemble._score_route``
    does at deploy. Returns ``{row_ids, sha256, paths, scores, labels,
    probs, canonical_shas}`` — the schema ``azoth_oof_score._combine`` and
    downstream consumers expect.
    """
    if not rows:
        empty_str = np.array([], dtype=object)
        return {
            "row_ids": np.array([], dtype=np.int64),
            "sha256": empty_str,
            "paths": empty_str,
            "scores": np.array([], dtype=np.int32),
            "labels": np.array([], dtype=np.int8),
            "probs": np.array([], dtype=np.float32),
            "canonical_shas": empty_str,
        }
    spec_path = bundle_dir / "feature_spec.json"
    spec = features.FeatureSpec.load(spec_path)
    clf = bundle.Ensemble.load_bundle(bundle_dir)

    pred_batches: list[np.ndarray] = []
    label_batches: list[np.ndarray] = []
    sample_buffer: list[Any] = []
    for batch_meta, x_matrix, y, _stats in features.extract_labeled_metadata_from_db_batches_unordered(
        db_path, rows, spec, n_workers=workers,
    ):
        pred_batches.append(clf.predict_proba(x_matrix).astype(np.float32))
        label_batches.append(y)
        sample_buffer.extend(batch_meta)
    if not sample_buffer:
        raise RuntimeError(
            f"{bundle_dir}: feature extraction returned no rows for {len(rows)} inputs",
        )
    # LabeledMetadata is a tuple type alias (features.py:107). 6-tuple form
    # used here: (row_id, sha256, path, score, label, canonical_sha256).
    # 7-tuple form from the size-aware streamer inserts json_bytes at idx 5
    # and pushes canonical_sha256 to idx 6 — detect via tuple length.
    canonical_idx = 6 if sample_buffer and len(sample_buffer[0]) >= 7 else 5
    return {
        "row_ids": np.array([s[0] for s in sample_buffer], dtype=np.int64),
        "sha256": np.array([s[1] for s in sample_buffer]),
        "paths": np.array([s[2] for s in sample_buffer]),
        "scores": np.array([s[3] for s in sample_buffer], dtype=np.int32),
        "labels": np.concatenate(label_batches).astype(np.int8),
        "probs": np.concatenate(pred_batches).astype(np.float32),
        "canonical_shas": np.array(
            [s[canonical_idx] or s[1] for s in sample_buffer],
        ),
    }


def _split_by_fold(
    rows: list[tuple[int, str, str, int, int, str]],
) -> tuple[list, list, list]:
    """Partition rows by ``data.oof_fold_of(canonical) ∈ {0, 1, None}``."""
    fold_0: list = []
    fold_1: list = []
    test_rows: list = []
    for row in rows:
        canonical = row[5]
        fold = data.oof_fold_of(canonical)
        if fold == 0:
            fold_0.append(row)
        elif fold == 1:
            fold_1.append(row)
        elif fold is None:
            test_rows.append(row)
        else:
            # Defensive: data.oof_fold_of currently returns {0, 1, None}; if
            # the partition definition ever grows a third fold we'd want
            # _split_by_fold to know about it before silently dropping rows.
            raise ValueError(
                f"unexpected oof_fold_of value {fold!r} for canonical {canonical}",
            )
    return fold_0, fold_1, test_rows


def _combine(parts: Iterable[dict[str, np.ndarray]]) -> dict[str, np.ndarray]:
    """Concatenate per-fold score dicts and sort by row_id."""
    keys = ("row_ids", "sha256", "paths", "scores", "labels", "probs", "canonical_shas")
    parts = [p for p in parts if len(p["row_ids"])]
    if not parts:
        return {k: np.array([]) for k in keys}
    combined = {k: np.concatenate([p[k] for p in parts]) for k in keys}
    order = np.argsort(combined["row_ids"], kind="mergesort")
    return {k: combined[k][order] for k in keys}


def _write_route(
    out_path: Path,
    combined: dict[str, np.ndarray],
    *,
    max_id_requested: int,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n_total = int(len(combined["labels"]))
    n_mal = int(np.sum(combined["labels"] == 1)) if n_total else 0
    n_ben = int(np.sum(combined["labels"] == 0)) if n_total else 0
    max_row_id = int(np.max(combined["row_ids"])) if n_total else 0
    np.savez(
        out_path,
        row_ids=combined["row_ids"],
        sha256=combined["sha256"],
        paths=combined["paths"],
        scores=combined["scores"],
        labels=combined["labels"],
        probs=combined["probs"],
        canonical_shas=combined["canonical_shas"],
        corpus_samples=np.array(n_total, dtype=np.int64),
        corpus_malware=np.array(n_mal, dtype=np.int64),
        corpus_benign=np.array(n_ben, dtype=np.int64),
        corpus_max_row_id=np.array(max_row_id, dtype=np.int64),
        corpus_requested_max_id=np.array(int(max_id_requested), dtype=np.int64),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="Hopper DSN")
    parser.add_argument(
        "--fold-a-root",
        type=Path,
        required=True,
        help=(
            "Azoth tree trained with EXP_OOF_FOLD_EXCLUDE=0 (didn't see "
            "fold-0 rows; produces OOF predictions on them)."
        ),
    )
    parser.add_argument(
        "--fold-b-root",
        type=Path,
        required=True,
        help="Azoth tree trained with EXP_OOF_FOLD_EXCLUDE=1.",
    )
    parser.add_argument(
        "--prod-root",
        type=Path,
        default=None,
        help=(
            "Production single-fold azoth tree. When set, test-partition "
            "rows are scored with the production bundle and appended to "
            "each route's OOF threshold_scores.npz. Without this, test "
            "rows get no specialist score and the eval can't include "
            "their ensemble contribution. Set to the same tree the "
            "deploy pipeline uses."
        ),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("out/models/azoth/specialists.json"),
        help=(
            "Path to specialists.json — used to look up each route's "
            "file_types. Defaults to the production summary."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help=(
            "Directory under which per-route OOF score files are written: "
            "{output_dir}/filegroups/<name>/threshold_scores.npz and "
            "{output_dir}/filetypes/<name>/threshold_scores.npz."
        ),
    )
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--max-id", type=int, default=0)
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help=(
            "Only score these routes (repeatable). e.g. --only filetypes/pe "
            "--only filegroups/scripts. Default: every route present in "
            "both fold roots."
        ),
    )
    args = parser.parse_args()
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    fold_a_routes = _route_paths(args.fold_a_root)
    fold_b_routes = _route_paths(args.fold_b_root)
    prod_routes = _route_paths(args.prod_root) if args.prod_root else {}

    # Score the intersection — a route present in only one fold can't
    # contribute honest OOF in the missing-fold rows, so skip it loudly.
    common = sorted(set(fold_a_routes) & set(fold_b_routes))
    if args.only:
        wanted = set(args.only)
        common = [r for r in common if r in wanted]
        missing_requested = wanted - set(common)
        if missing_requested:
            LOG.warning(
                "requested routes missing from one of the fold roots: %s",
                sorted(missing_requested),
            )
    if not common:
        raise SystemExit(
            "no routes in common between fold-a-root and fold-b-root "
            f"({args.fold_a_root} ∩ {args.fold_b_root})",
        )

    route_file_types = _load_route_file_types(args.summary)
    missing_summary = [r for r in common if r not in route_file_types]
    if missing_summary:
        raise SystemExit(
            f"routes missing from {args.summary}: {missing_summary} — "
            "rerun azoth_specialist_suite to refresh the summary, or pass "
            "--summary pointing at a tree containing all needed routes.",
        )

    LOG.info("scoring %d routes", len(common))
    for route_name in common:
        file_types = route_file_types[route_name]
        rows = _fetch_route_rows(args.db, file_types, args.max_id)
        if not rows:
            LOG.warning("%s: no rows match file_types=%s", route_name, file_types)
            continue
        fold_0, fold_1, test_rows = _split_by_fold(rows)
        LOG.info(
            "%s: %d rows (fold0=%d, fold1=%d, test=%d) over %s",
            route_name, len(rows), len(fold_0), len(fold_1), len(test_rows), file_types,
        )

        parts: list[dict[str, np.ndarray]] = []
        if fold_0:
            LOG.info("%s: scoring fold-0 rows with fold-A bundle", route_name)
            parts.append(_score_rows(
                args.db, fold_0, fold_a_routes[route_name], workers=args.workers,
            ))
        if fold_1:
            LOG.info("%s: scoring fold-1 rows with fold-B bundle", route_name)
            parts.append(_score_rows(
                args.db, fold_1, fold_b_routes[route_name], workers=args.workers,
            ))
        if test_rows:
            if route_name in prod_routes:
                LOG.info("%s: scoring test rows with production bundle", route_name)
                parts.append(_score_rows(
                    args.db, test_rows, prod_routes[route_name], workers=args.workers,
                ))
            else:
                LOG.info(
                    "%s: %d test rows — no --prod-root for this route, skipping; "
                    "eval will see NaN test probs",
                    route_name, len(test_rows),
                )
        combined = _combine(parts)

        out_path = args.output_dir / route_name / "threshold_scores.npz"
        _write_route(out_path, combined, max_id_requested=args.max_id)
        n = int(len(combined["labels"]))
        n_mal = int(np.sum(combined["labels"] == 1)) if n else 0
        n_ben = int(np.sum(combined["labels"] == 0)) if n else 0
        LOG.info(
            "wrote %s: %d rows (%d malware, %d benign)",
            out_path, n, n_mal, n_ben,
        )

    print(f"wrote {len(common)} route OOF score files under {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
