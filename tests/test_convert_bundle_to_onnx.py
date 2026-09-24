import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import convert_bundle_to_onnx as conv  # noqa: E402

MAX_DELTA = 1e-5


def _deltas(n_rows: int, flips: list[float]) -> np.ndarray:
    d = np.full(n_rows, 3e-8)
    d[: len(flips)] = flips
    return d


def test_clean_parity_passes():
    assert conv._parity_tolerated(_deltas(200, []), MAX_DELTA) == (True, 0)


def test_few_branch_flips_tolerated():
    # 2026-09-20: 3 benign ~1e-4 flips in a 200-row sample failed the deploy.
    ok, n_over = conv._parity_tolerated(_deltas(200, [1.14e-4, 9e-5, 3e-5]), MAX_DELTA)
    assert ok and n_over == 3


def test_flip_count_bound_is_five_percent():
    assert conv._parity_tolerated(_deltas(200, [1e-4] * 10), MAX_DELTA)[0]
    assert not conv._parity_tolerated(_deltas(200, [1e-4] * 11), MAX_DELTA)[0]


def test_single_flip_tolerated_in_tiny_sample():
    assert conv._parity_tolerated(_deltas(5, [1e-4]), MAX_DELTA)[0]


def test_flip_over_hard_cap_fails():
    assert not conv._parity_tolerated(_deltas(200, [2e-2]), MAX_DELTA)[0]


def test_systemic_shift_fails():
    # A converter bug moves most rows, not a handful.
    assert not conv._parity_tolerated(np.full(200, 5e-4), MAX_DELTA)[0]
