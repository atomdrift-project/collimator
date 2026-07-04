"""Carry-forward invalidation for the per-filetype metrics grid.

`compute_routed_metrics` copies a previous bundle's per-filetype metrics
verbatim when a route's scores are bytewise-unchanged (a fast path for
single-route promotes). Score-identity alone is NOT sufficient: the deploy
recall grid / operating level can move even when scores don't (a pure
recalibrate flipping the default from L50 to L25). A prior entry computed on
the old grid lacks the new levels' `recall_at_N_per_100M` fields — carrying
it forward blanks the operating-level column and holes the recall curve for
exactly the big, stable routes that never get retrained. The gate below
forces a recompute whenever the grid moved.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "compute_routed_metrics.py"
_spec = importlib.util.spec_from_file_location("compute_routed_metrics", _SCRIPT)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
sys.modules["compute_routed_metrics"] = _mod
_spec.loader.exec_module(_mod)


def _entry_on_levels(levels, *, block: str = "ensemble") -> dict:
    return {block: {f"recall_at_{lvl}_per_100M": 0.5 for lvl in levels}}


def test_full_current_grid_is_carried_forward() -> None:
    entry = _entry_on_levels(_mod.RECALL_CURVE_LEVELS)
    assert _mod._entry_covers_current_grid(entry) is True


def test_old_grid_missing_operating_level_is_recomputed() -> None:
    # Pre-L25 grid: no 15/25. This is the exact shape that produced the
    # blank "Recall @ L25" README column.
    old_grid = (0, 1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100,
                125, 150, 175, 200, 250, 300, 500, 1000, 2000, 5000,
                7500, 10000, 15000, 20000, 25000)
    entry = _entry_on_levels(old_grid)
    assert _mod._entry_covers_current_grid(entry) is False


def test_entry_missing_only_the_operating_level_is_recomputed() -> None:
    from collimator.thresholds import DEFAULT_SEVERITY_LEVEL
    partial = [lvl for lvl in _mod.RECALL_CURVE_LEVELS if lvl != DEFAULT_SEVERITY_LEVEL]
    assert _mod._entry_covers_current_grid(_entry_on_levels(partial)) is False


def test_recall_levels_read_across_all_blocks() -> None:
    entry = {
        "general": {"recall_at_0_per_100M": 0.1},
        "specialist": {"recall_at_25_per_100M": 0.2},
        "ensemble": {"recall_at_100_per_100M": 0.3, "pr_auc": 0.9},
    }
    assert _mod._entry_recall_levels(entry) == {0, 25, 100}


def test_empty_or_malformed_entry_is_not_covered() -> None:
    assert _mod._entry_covers_current_grid({}) is False
    assert _mod._entry_covers_current_grid({"ensemble": None}) is False
    assert _mod._entry_recall_levels({}) == set()
