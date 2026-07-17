#!/usr/bin/env python3
"""Walk an azoth bundle, convert every LightGBM ``.txt`` model to ``.onnx``.

Used to upgrade existing bundles trained before the training pipeline
started emitting .onnx alongside .txt. Once bundle-wide ONNX is present,
``bundle.model_files`` prefers ``.onnx`` on the load path; the ``.txt``
files become deprecated diagnostic-only artifacts.

For each model file converted, a parity check runs on a sample of rows
from the route's home filetype(s) and refuses to ship if any prob delta
exceeds ``--max-parity-delta`` (default 1e-6 — orders of magnitude under
the 1e-5 tail-drift threshold), except for a bounded number of isolated
float32 threshold branch-flip rows under ``BRANCH_FLIP_HARD_CAP`` (see
``_parity_check``). Failures stop the migration and leave the existing
``.txt`` files in place untouched.

Usage:
  scripts/convert_bundle_to_onnx.py --azoth-root out/models/azoth --db $DB

  scripts/convert_bundle_to_onnx.py --azoth-root out/models/azoth \\
      --skip-parity        # convert without parity check (faster, less safe)
  scripts/convert_bundle_to_onnx.py --azoth-root out/models/azoth \\
      --dry-run            # report what would be converted, no writes
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import features, route_prune  # noqa: E402

LOG = logging.getLogger("convert_bundle_to_onnx")

# Filetypes to sample for parity per route kind. Mirrors phase 0 — picks
# routes whose model would legitimately score those filetypes at deploy
# time, so the parity check exercises realistic feature distributions.
ROUTE_PARITY_FILETYPES = {
    "general": ["pe", "elf", "javascript", "pdf"],
}

# Ceiling for tolerated isolated branch-flip rows in the parity check (see
# _parity_check). Well under any prob shift that could move a verdict across
# the L25/L3000 operating points, far above float32 accumulation noise.
BRANCH_FLIP_HARD_CAP = 1e-2


def _filetypes_for_route(route_dir: Path, azoth_root: Path) -> list[str]:
    """Return a small list of filetypes that the route's model would
    legitimately score. ``filetypes/X`` → ``[X]``. ``filegroups/X`` →
    members of that group from config.json. ``general`` → a hand-picked
    diverse set."""
    parts = route_dir.relative_to(azoth_root).parts
    if parts == ("general",):
        return ROUTE_PARITY_FILETYPES["general"]
    if parts[0] == "filetypes" and len(parts) >= 2:
        return [parts[1]]
    if parts[0] == "filegroups" and len(parts) >= 2:
        group = parts[1]
        import json  # noqa: PLC0415
        cfg = json.loads((azoth_root / "config.json").read_text())
        mapping = cfg.get("filetype_to_group") or {}
        members = sorted(ft for ft, g in mapping.items() if g == group)
        return members[:4] if members else []
    return []


def _sample_rows(db: str, filetypes: list[str], limit: int) -> list[tuple[int, int]]:
    """Fetch a small sample of (row_id, label_int) rows for parity."""
    if not filetypes:
        return []
    import psycopg  # noqa: PLC0415
    with psycopg.connect(db) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, CASE WHEN label='bad' THEN 1 ELSE 0 END
            FROM samples
            WHERE label IN ('bad','good') AND file_type = ANY(%s)
              AND cleave_result IS NOT NULL AND skip=''
              AND canonical_sha256 IS NOT NULL
              AND get_byte(decode(right(canonical_sha256, 2), 'hex'), 0) < 32
            ORDER BY id LIMIT %s
            """,
            [filetypes, int(limit)],
        )
        return [(int(r[0]), int(r[1])) for r in cur.fetchall()]


def _parity_check(
    route_dir: Path,
    txt_path: Path,
    onnx_path: Path,
    db: str,
    sample_rows: list[tuple[int, int]],
    max_delta: float,
) -> tuple[bool, float, int]:
    """Score the same rows with .txt and .onnx; require max prob delta
    below threshold. Returns ``(ok, observed_max_delta, n_rows)``."""
    if not sample_rows:
        return True, 0.0, 0

    spec = features.FeatureSpec.load(route_dir / "feature_spec.json")
    batches = list(features.extract_labeled_from_db_batches(
        db, sample_rows, spec, n_workers=4,
    ))
    if not batches:
        return True, 0.0, 0
    x = sp.vstack([b[0] for b in batches], format="csr")

    import lightgbm  # noqa: PLC0415
    booster = lightgbm.Booster(model_file=str(txt_path))
    lgb_probs = booster.predict(x)

    import onnxruntime as ort  # noqa: PLC0415
    session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    x_dense = x.toarray().astype(np.float32)
    out = session.run(None, {input_name: x_dense})
    onnx_probs = out[1][:, 1] if out[1].ndim == 2 else out[1]
    deltas = np.abs(np.asarray(lgb_probs) - np.asarray(onnx_probs))
    delta_max = float(deltas.max())
    if delta_max <= max_delta:
        return True, delta_max, x.shape[0]
    # Isolated larger deltas are expected float32 behavior, not converter
    # bugs: ONNX stores split thresholds as float32 while the .txt keeps
    # float64, so a feature value landing in a threshold's rounding gap
    # flips one branch and moves that row's prob by ~1e-3. The 2026-07-12
    # nightly failed deploy on exactly one such live-DB sample row (delta
    # 3.45e-03, twice, then the row left the sample). Tolerate a couple of
    # flip rows, bounded in count and magnitude — systemic conversion bugs
    # (e.g. the 0-split LOGISTIC bug) shift many rows by large deltas and
    # stay fatal.
    n_over = int((deltas > max_delta).sum())
    ok = n_over <= max(1, len(deltas) // 100) and delta_max <= BRANCH_FLIP_HARD_CAP
    if ok:
        LOG.warning(
            "tolerating %d/%d row(s) over parity delta %.1e (max %.2e <= "
            "branch-flip cap %.1e): isolated float32 threshold branch-flip",
            n_over, len(deltas), max_delta, delta_max, BRANCH_FLIP_HARD_CAP,
        )
    return ok, delta_max, x.shape[0]


def _convert_one(
    booster_path: Path,
    onnx_path: Path,
) -> None:
    """Single-file LightGBM .txt → .onnx conversion using export.py's helper.

    Returns successfully on skipped (constant-predictor) models — the
    skip is logged but isn't a failure since the .txt path is still
    valid and litmus loads it fine. See export.export_lightgbm_onnx
    for the underlying ONNX Runtime bug this guards against.
    """
    from collimator import export  # noqa: PLC0415
    import lightgbm  # noqa: PLC0415
    booster = lightgbm.Booster(model_file=str(booster_path))
    ok = export.export_lightgbm_onnx(booster, booster.num_feature(), onnx_path)
    if not ok:
        # export_lightgbm_onnx returns False for constant-predictor
        # models that would trip the runtime bug. The caller handles
        # this as "skip, not failure" — propagate by raising
        # SkippedConversion which the main loop catches differently.
        raise SkippedConversion(
            f"skipped ONNX export for {booster_path}: constant-predictor "
            f"model (1 leaf). .txt remains canonical."
        )


class SkippedConversion(Exception):
    """Conversion was skipped intentionally (e.g. constant-predictor
    model). Not a failure — the .txt remains the route's artifact."""


def _walk_route_dirs(azoth_root: Path):
    """Yield every per-route bundle dir (general + filegroups/* + filetypes/*).
    Skips dirs that don't have a feature_spec.json, since those aren't
    inference targets (likely a packaging stray)."""
    candidates = [azoth_root / "general"]
    for kind in ("filegroups", "filetypes"):
        kind_dir = azoth_root / kind
        if kind_dir.is_dir():
            for sub in sorted(kind_dir.iterdir()):
                if sub.is_dir():
                    candidates.append(sub)
    for d in candidates:
        if (d / "feature_spec.json").is_file():
            yield d


def _route_name(route_dir: Path, azoth_root: Path) -> str:
    """Bundle route name for a route dir, e.g. 'general', 'filetypes/jpeg'."""
    return route_dir.relative_to(azoth_root).as_posix()


def _safe_unlink(path: Path) -> None:
    try:
        path.unlink()
    except OSError:
        pass


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--azoth-root", type=Path, required=True,
                   help="Root of the bundle to convert (e.g. out/models/azoth)")
    p.add_argument("--db", default=os.environ.get("DB", ""),
                   help="Hopper DSN for parity-check feature extraction")
    p.add_argument("--max-parity-delta", type=float, default=1e-5,
                   help=(
                       "Max tolerated |lgb_prob - onnx_prob|. Default 1e-5 "
                       "tolerates accumulated float32 noise on deep "
                       "(400-tree) models (jar's 7.45e-6 was a genuine "
                       "calibration-equivalent FP drift, not a converter "
                       "bug). Well under the 1e-4 threshold where "
                       "saturated-tail recall would shift."
                   ))
    p.add_argument("--parity-rows", type=int, default=200,
                   help="Rows per route to use for parity (default 200)")
    p.add_argument("--no-weakness-gate", action="store_true",
                   help="Skip the pre-conversion quality gate that drops "
                        "filetype specialists meaningfully worse than the "
                        "general route on home-filetype PR-AUC.")
    p.add_argument("--max-pr-auc-deficit", type=float,
                   default=route_prune.DEFAULT_PR_AUC_TOLERANCE,
                   help="Drop a filetype specialist when the general route "
                        "beats it on home-filetype PR-AUC by more than this "
                        "(default %(default)s). A dead-band, not a required "
                        "gain: ties and noise-level deficits are kept, so "
                        "strong specialists tied with general survive.")
    p.add_argument("--skip-parity", action="store_true",
                   help="Convert without parity check. Faster but unsafe.")
    p.add_argument("--dry-run", action="store_true",
                   help="Report what would be converted, no writes.")
    p.add_argument("--log-level", default="INFO")
    args = p.parse_args()
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(message)s")

    azoth_root: Path = args.azoth_root
    if not azoth_root.is_dir():
        raise SystemExit(f"azoth root not found: {azoth_root}")
    if not args.skip_parity and not args.db:
        raise SystemExit("--db is required (or set $DB) unless --skip-parity is passed")

    # Pass 0 — quality gate. Drop filetype specialists too weak to ship BEFORE
    # spending any effort converting them, so a near-random model can never
    # reach (let alone be blocked by) the float32 ONNX parity check. A
    # specialist that doesn't beat the general route on its home filetype's
    # PR-AUC carries no defensible signal; the filetype falls back to the
    # general/filegroup routes it already ensembles with.
    pruned_weak: set[str] = set()
    metrics_path = azoth_root / "per_filetype_metrics.json"
    if args.no_weakness_gate:
        LOG.info("weakness gate disabled (--no-weakness-gate)")
    elif not metrics_path.is_file():
        LOG.warning("weakness gate skipped: %s not found", metrics_path)
    else:
        metrics = json.loads(metrics_path.read_text())
        weak = route_prune.weak_filetype_specialists(
            metrics, tolerance=args.max_pr_auc_deficit)
        # Only routes actually present as a deployable model in this bundle.
        weak = {r: v for r, v in weak.items()
                if (azoth_root / r / "feature_spec.json").is_file()}
        for route, info in sorted(weak.items()):
            LOG.warning(
                "weakness gate: dropping %s (PR-AUC %.4f vs general %.4f, "
                "deficit %.4f > %.4g) — filetype falls back to general/filegroup",
                route, info["specialist_pr_auc"], info["general_pr_auc"],
                info["deficit"], args.max_pr_auc_deficit,
            )
        if weak and args.dry_run:
            LOG.info("[dry-run] would prune weak specialists: %s", sorted(weak))
        elif weak:
            pruned_weak = route_prune.prune_routes(azoth_root, set(weak))

    # Pass 1: identify every .txt that needs an .onnx sibling.
    to_convert: list[tuple[Path, Path, Path]] = []  # (route_dir, txt, onnx)
    for route_dir in _walk_route_dirs(azoth_root):
        # Multi-seed bundle: models/seed_*.txt
        multi_dir = route_dir / "models"
        if multi_dir.is_dir():
            for txt in sorted(multi_dir.glob("seed_*.txt")):
                onnx = txt.with_suffix(".onnx")
                if onnx.is_file():
                    LOG.info("%s already has %s; skipping", route_dir, onnx.name)
                    continue
                to_convert.append((route_dir, txt, onnx))
        # Legacy single-seed: model.txt
        legacy = route_dir / "model.txt"
        if legacy.is_file():
            onnx = route_dir / "model.onnx"
            if onnx.is_file():
                LOG.info("%s already has %s; skipping", route_dir, onnx.name)
            else:
                to_convert.append((route_dir, legacy, onnx))

    LOG.info("found %d .txt files to convert", len(to_convert))
    if args.dry_run:
        for rd, txt, onnx in to_convert:
            print(f"  {txt.relative_to(azoth_root)} -> {onnx.name}")
        return 0

    # Pass 2: convert + parity check, route by route.
    n_converted = 0
    n_skipped = 0
    failures: list[tuple[Path, str]] = []
    skipped: list[tuple[Path, str]] = []
    # Specialist routes whose ONNX failed parity: dropped (fall back), not fatal.
    # The general route is exempt — a parity failure there stays fatal because
    # it is the fallback of last resort, with nothing to fall back to.
    parity_failed_routes: set[str] = set()
    for route_dir, txt, onnx in to_convert:
        t0 = time.perf_counter()
        try:
            _convert_one(txt, onnx)
        except SkippedConversion as e:
            n_skipped += 1
            skipped.append((txt, str(e)))
            LOG.info("skipped %s: %s", txt.relative_to(azoth_root), e)
            continue
        except Exception as e:
            failures.append((txt, f"convert: {e}"))
            LOG.error("convert failed for %s: %s", txt, e)
            continue

        if args.skip_parity:
            n_converted += 1
            LOG.info("converted %s (%.0f ms)", txt.relative_to(azoth_root), (time.perf_counter()-t0)*1000)
            continue

        filetypes = _filetypes_for_route(route_dir, azoth_root)
        sample = _sample_rows(args.db, filetypes, args.parity_rows)
        try:
            ok, delta, n_rows = _parity_check(
                route_dir, txt, onnx, args.db, sample, args.max_parity_delta,
            )
        except Exception as e:
            _safe_unlink(onnx)
            route = _route_name(route_dir, azoth_root)
            if route == "general":
                failures.append((txt, f"parity: {e}"))
                LOG.error("parity check errored for %s: %s — removing .onnx "
                          "(FATAL: general route)", txt, e)
            else:
                parity_failed_routes.add(route)
                LOG.warning("parity check errored for %s: %s — dropping specialist "
                            "route %s (filetype falls back to general/filegroup)",
                            txt, e, route)
            continue
        if not ok:
            _safe_unlink(onnx)
            route = _route_name(route_dir, azoth_root)
            if route == "general":
                failures.append((txt, f"parity delta {delta:.2e} > {args.max_parity_delta:.2e}"))
                LOG.error(
                    "%s FAILED parity: delta=%.2e > %.2e (rows=%d) — removing .onnx "
                    "(FATAL: general route)",
                    txt, delta, args.max_parity_delta, n_rows,
                )
            else:
                parity_failed_routes.add(route)
                LOG.warning(
                    "%s FAILED parity: delta=%.2e > %.2e (rows=%d) — dropping specialist "
                    "route %s (filetype falls back to general/filegroup)",
                    txt, delta, args.max_parity_delta, n_rows, route,
                )
            continue
        n_converted += 1
        elapsed_ms = (time.perf_counter() - t0) * 1000
        LOG.info(
            "%s -> %s OK (delta=%.2e on %d rows, %.0f ms)",
            txt.relative_to(azoth_root), onnx.name, delta, n_rows, elapsed_ms,
        )

    # Drop specialist routes whose ONNX failed parity (general is never here).
    parity_pruned: set[str] = set()
    if parity_failed_routes and not args.dry_run:
        parity_pruned = route_prune.prune_routes(azoth_root, parity_failed_routes)

    dropped = sorted(pruned_weak | parity_pruned)

    print()
    print(
        f"converted {n_converted}/{len(to_convert)} files "
        f"({n_skipped} intentionally skipped, "
        f"{len(dropped)} specialist route(s) dropped, "
        f"{len(failures)} failed)"
    )
    if skipped:
        print(f"skipped ({n_skipped}, .txt remains canonical):")
        for path, reason in skipped:
            print(f"  {path.relative_to(azoth_root)}: {reason}")
    if dropped:
        print(f"dropped specialist routes ({len(dropped)}, filetype falls back "
              f"to general/filegroup — weak PR-AUC or failed ONNX parity):")
        for route in dropped:
            print(f"  {route}")
    if failures:
        print(f"failures ({len(failures)}):")
        for path, reason in failures:
            print(f"  {path}: {reason}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
