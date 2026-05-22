#!/usr/bin/env python3
"""Print per-route labeled sample counts as JSON.

Used by autocollie's upfront skip filter: before spending an LLM call
and N experiment runs on a route, check whether it has enough labeled
data for autocollie's statistical machinery to find anything. Routes
below the threshold get skipped at iteration start.

Output format (JSON to stdout):

  {
    "filetypes/c": {"malware": 1766, "benign": 66647, "labeled": 68413},
    "filetypes/groovy": {"malware": 123, "benign": 5044, "labeled": 5167},
    "filegroups/source": {"malware": 19120, "benign": 1230000, "labeled": 1249120},
    "general": {"malware": 1703128, "benign": 3024390, "labeled": 4727518}
  }

For ``filegroups/<X>`` and ``general`` the counts pool across all member
filetypes (mapped via the deployed bundle's config.json filetype_to_group).
filegroup/general routes train on pooled data so their counts reflect what
the model actually sees.

Usage:
  scripts/route_sample_counts.py --routes filetypes/c,filetypes/groovy
  scripts/route_sample_counts.py --routes filegroups/source,general --bundle out/models/azoth
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from collimator import data as cdata  # noqa: E402


def _filetypes_for_route(route: str, bundle_root: Path) -> list[str] | None:
    """``filetypes/X`` → [X]; ``filegroups/X`` → members from
    bundle's filetype_to_group; ``general`` → None (means all)."""
    if route == "general":
        return None
    if route.startswith("filetypes/"):
        return [route.split("/", 1)[1]]
    if route.startswith("filegroups/"):
        group = route.split("/", 1)[1]
        config_path = bundle_root / "config.json"
        if not config_path.is_file():
            # No bundle config. Best we can do is empty — caller treats
            # the route as "unknown coverage; skip the filter."
            return []
        cfg = json.loads(config_path.read_text())
        mapping = cfg.get("filetype_to_group") or {}
        return sorted(ft for ft, g in mapping.items() if g == group)
    raise SystemExit(f"unknown route layout: {route!r}")


def _count_labeled(db_path: str, file_types: list[str] | None) -> dict[str, int]:
    """Return {"malware": N_bad, "benign": N_good} for the route's
    pooled filetype set. None file_types means "all" (the general route)."""
    is_pg = cdata._is_pg(db_path)  # noqa: SLF001
    where_base = (
        "label IN ('bad', 'good') AND cleave_result IS NOT NULL AND skip = ''"
    )
    n_mal = 0
    n_ben = 0
    with cdata._connect(db_path, repeatable_read=True) as conn:  # noqa: SLF001
        if is_pg:
            with conn.cursor() as cur:
                if file_types is None:
                    cur.execute(
                        f"SELECT label, count(*) FROM samples WHERE {where_base} GROUP BY label",  # noqa: S608
                    )
                else:
                    cur.execute(
                        f"SELECT label, count(*) FROM samples WHERE {where_base} "  # noqa: S608
                        f"AND file_type = ANY(%s) GROUP BY label",
                        [file_types],
                    )
                for label, n in cur:
                    if label == "bad":
                        n_mal = int(n)
                    elif label == "good":
                        n_ben = int(n)
        else:
            if file_types is None:
                query = (
                    f"SELECT label, count(*) FROM samples WHERE {where_base} GROUP BY label"  # noqa: S608
                )
                params: list = []
            else:
                placeholders = ",".join("?" for _ in file_types)
                query = (
                    f"SELECT label, count(*) FROM samples WHERE {where_base} "  # noqa: S608
                    f"AND file_type IN ({placeholders}) GROUP BY label"
                )
                params = list(file_types)
            for label, n in conn.execute(query, params):
                if label == "bad":
                    n_mal = int(n)
                elif label == "good":
                    n_ben = int(n)
    return {"malware": n_mal, "benign": n_ben}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--routes", required=True,
        help="Comma-separated route names "
             "(filetypes/<X>, filegroups/<X>, or 'general').",
    )
    p.add_argument(
        "--db", default=os.environ.get("DB", ""),
        help="Database DSN. Defaults to $DB.",
    )
    p.add_argument(
        "--bundle", type=Path, default=Path("out/models/azoth"),
        help="Bundle root for filetype_to_group mapping "
             "(used by filegroups/<X> routes).",
    )
    args = p.parse_args()
    if not args.db:
        raise SystemExit("--db required (or set $DB env)")

    routes = [r.strip() for r in args.routes.split(",") if r.strip()]
    out: dict[str, dict[str, int]] = {}
    for route in routes:
        file_types = _filetypes_for_route(route, args.bundle)
        counts = _count_labeled(args.db, file_types)
        out[route] = {
            "malware": counts["malware"],
            "benign": counts["benign"],
            "labeled": counts["malware"] + counts["benign"],
        }
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
