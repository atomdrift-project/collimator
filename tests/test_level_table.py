"""Guard the canonical per-level emitters against the index-as-level bug.

The specialist suite's local `_level_table` once iterated
``range(len(SEVERITY_LEVEL_TARGETS))``, emitting array positions as level
labels and passing ``float(level)`` (a per-100M value) as target_per_million
— every row was mislabeled and scored 100x too loose. These tests pin the
shared implementation to the grid so a regression is loud.
"""

import numpy as np

from collimator import thresholds


def _synthetic_scores(n_benign=30_000, n_malware=5_000, seed=7):
    rng = np.random.default_rng(seed)
    benign = rng.beta(1, 8, size=n_benign)          # piled near 0
    malware = rng.beta(8, 1, size=n_malware)        # piled near 1
    y = np.concatenate([np.zeros(n_benign, dtype=np.int8),
                        np.ones(n_malware, dtype=np.int8)])
    p = np.concatenate([benign, malware])
    return y, p


def test_level_labels_are_grid_values_not_indices():
    y, p = _synthetic_scores()
    table = thresholds.level_table(y, p)
    labels = [row["level"] for row in table]
    grid = [int(t["level"]) for t in thresholds.SEVERITY_LEVEL_TARGETS]
    assert labels == grid
    assert labels == list(thresholds._LEVELS_PER_100M)
    # The buggy version emitted contiguous 0..41; the real grid is not
    # contiguous — make the difference explicit.
    assert labels != list(range(len(labels)))


def test_level_targets_are_per_100M_not_100x_loose():
    y, p = _synthetic_scores()
    for row in thresholds.level_table(y, p):
        # level k means k FP per 100M; the emitted target must match the
        # label exactly (the bug scored L25 at 2,500/100M).
        assert row["hostile"]["target_per_100M"] == float(row["level"])


def test_level_thresholds_monotone_and_shared_estimator():
    y, p = _synthetic_scores()
    table = thresholds.level_table(y, p)
    thr = [row["hostile"]["threshold"] for row in table]
    assert all(t is not None for t in thr)
    # Stricter level -> higher (or equal) threshold, strictly monotone
    # non-increasing as the level loosens.
    assert all(a >= b for a, b in zip(thr, thr[1:]))
    # Row 0 (L0) admits zero benign FPs by definition.
    assert table[0]["hostile"]["fp"] == 0
    # Spot-check the estimator is the shared one: L25's threshold must equal
    # quantile_severity_threshold at 0.25/M on the benign slice.
    benign = p[y == 0].astype(np.float64)
    want, _ = thresholds.quantile_severity_threshold(benign, 0.25)
    l25 = next(r for r in table if r["level"] == 25)
    assert l25["hostile"]["threshold"] == float(want)


def test_operating_point_degenerate_slices():
    empty = np.array([], dtype=np.int8)
    out = thresholds.operating_point(empty, np.array([]), 0.25)
    assert out["recall"] is None and out["budget"] is None
    y = np.ones(10, dtype=np.int8)  # malware only, no benign
    out = thresholds.operating_point(y, np.linspace(0, 1, 10), 0.25)
    assert out["recall"] is None
