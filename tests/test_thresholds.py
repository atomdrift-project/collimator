"""Tests for threshold table semantics."""

from __future__ import annotations

import io
import re
from contextlib import redirect_stdout

import numpy as np

from collimator.thresholds import print_threshold_table


def test_print_threshold_table_uses_called_subset_accuracy() -> None:
    probs = np.array([0.95, 0.90, 0.80, 0.30, 0.20, 0.10], dtype=np.float32)
    y = np.array([1, 1, 0, 0, 1, 0], dtype=np.float32)

    buf = io.StringIO()
    with redirect_stdout(buf):
        print_threshold_table(probs, y)
    out = buf.getvalue()

    hostile_line = re.search(r"80\.000%\s+0\.900000\s+2\s+0\s+2", out)
    benign_line = re.search(r"80\.000%\s+0\.200000\s+1\s+0\s+1", out)

    assert hostile_line is not None
    assert benign_line is not None
