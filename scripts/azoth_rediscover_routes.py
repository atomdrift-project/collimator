#!/usr/bin/env python3
"""Re-discover normalized routes and rewrite specialists.json.

Skips retraining. The current on-disk model for each normalized route is
the one that ends up in the new summary; orphaned variant models (e.g.
`filetypes/tar.gz/` when `filetypes/tar/` is present) are dropped from
the summary so downstream tools stop seeing them, but the files stay on
disk for the next `make azoth-specialists` pass to either reuse or
overwrite cleanly.

Use after changing the route-normalization rule in
`collimator.data.normalize_archive_filetype` to consolidate the bundle
without retraining.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# scripts/ isn't a package; reach src/ for collimator imports and add
# the scripts dir so azoth_specialist_suite re-exports work.
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from collimator import bundle, data  # noqa: E402
from azoth_specialist_suite import (  # noqa: E402
    RAW_COMPRESSED_FILETYPES,
    _eligible_filetypes,
)

LOG = logging.getLogger("azoth_rediscover_routes")


def _has_on_disk_model(route_dir: Path) -> bool:
    """A route is rediscoverable when it carries a model.txt/.onnx and a
    feature_spec.json on disk — same gate `azoth_calibrate_ensemble._load_routes`
    applies, so the rewritten summary stays compatible."""
    return bundle.has_model(route_dir) and (route_dir / "feature_spec.json").exists()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--azoth-root", type=Path, required=True)
    parser.add_argument(
        "--summary", type=Path, default=None,
        help="specialists.json path (default <azoth-root>/specialists.json)",
    )
    parser.add_argument("--max-id", type=int, default=0,
                        help="0 = no upper bound on samples.id")
    parser.add_argument("--min-score", type=float, default=None,
                        help="optional lower bound on samples.score")
    parser.add_argument("--min-bad", type=int, default=200)
    parser.add_argument("--min-good", type=int, default=200)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(message)s")

    summary_path = args.summary or args.azoth_root / "specialists.json"
    if not summary_path.exists():
        LOG.error("%s does not exist; run azoth-specialists first", summary_path)
        return 1
    with open(summary_path) as f:
        existing = json.load(f)

    # Re-run discovery; this applies the current normalize_archive_filetype
    # rule, so compound archive labels (tar.gz, tar.bz2, …) merge onto
    # their container (tar). The returned routes are keyed by the
    # normalized name and carry `file_types` listing every raw variant.
    discovered = _eligible_filetypes(
        args.db,
        max_id=args.max_id,
        min_score=args.min_score,
        min_bad=args.min_bad,
        min_good=args.min_good,
    )
    normalized_names = {route["name"] for route in discovered}

    # Build new results, preserving order. Filegroup entries pass through
    # untouched; filetype entries are dropped if their name normalizes
    # to something else (folded into the container route).
    existing_results: list[dict[str, Any]] = existing.get("results", []) or []
    new_results: list[dict[str, Any]] = []
    kept_filetype_names: set[str] = set()
    dropped_filetype_names: list[tuple[str, str]] = []
    for item in existing_results:
        kind = item.get("kind")
        name = str(item.get("name", ""))
        if kind != "filetype":
            new_results.append(item)
            continue
        # Skip filetype residues from before normalization changed: an
        # entry named "tar.gz" whose normalized form "tar" is now the
        # canonical route is folded — drop the summary entry, keep the
        # on-disk model untouched for the next full retrain to overwrite.
        normalized = data.normalize_archive_filetype(name)
        if normalized != name and normalized in normalized_names:
            dropped_filetype_names.append((name, normalized))
            continue
        # Pure-compression leaves (gz, bz2, …) get dropped at discovery
        # too — they have no specialist of their own.
        if normalized in RAW_COMPRESSED_FILETYPES:
            dropped_filetype_names.append((name, "<raw-compressed>"))
            continue
        # Keep the entry, but force the name onto the normalized form
        # (idempotent for already-normalized entries).
        if normalized != name:
            LOG.info("renaming filetype entry %r -> %r in summary", name, normalized)
            item = {**item, "name": normalized}
        new_results.append(item)
        kept_filetype_names.add(normalized)

    # Any newly-discovered route that has no existing on-disk model is a
    # gap — log it so the operator knows the next full train pass will
    # need to fit it. We don't fabricate a summary entry without a model.
    for route in discovered:
        if route["name"] in kept_filetype_names:
            continue
        route_dir = args.azoth_root / "filetypes" / route["name"]
        if _has_on_disk_model(route_dir):
            LOG.info(
                "adding rediscovered route filetypes/%s (model exists on disk; "
                "specialists.json was missing the entry)",
                route["name"],
            )
            new_results.append({
                "kind": "filetype",
                "name": route["name"],
                "output_dir": str(route_dir),
                "source_dir": str(route_dir),
            })
        else:
            LOG.warning(
                "filetypes/%s: discovered (%d bad, %d good) but no model on "
                "disk; next `make azoth-specialists` will fit it",
                route["name"], route["bad"], route["good"],
            )

    payload = {
        **existing,
        "timestamp": datetime.now(UTC).isoformat(),
        "results": new_results,
        "rediscovered": True,
    }
    with open(summary_path, "w") as f:
        json.dump(payload, f, indent=2)
    LOG.info(
        "rewrote %s: %d filetype routes kept, %d dropped (folded/raw-compressed)",
        summary_path, len(kept_filetype_names), len(dropped_filetype_names),
    )
    for name, normalized in dropped_filetype_names:
        LOG.info("  dropped: %s -> %s", name, normalized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
