"""Reporting always recomputes the current frozen policy, never cached guesses."""

import json

import numpy as np
import pytest

from scripts import compute_routed_metrics as metrics


def fixture(tmp_path, levels):
    config = {"fit_partition": "dev", "levels": [
        {"level": level, "hostile": {"thresholds": {"general": .5}}}
        for level in levels
    ]}
    (tmp_path / "config.json").write_text(json.dumps(config))
    (tmp_path / "route_policies.json").write_text('{"routes":{}}')
    np.savez(tmp_path / "scores.npz", row_ids=np.arange(4), labels=np.array([1, 0, 1, 0]),
             sha_bucket=np.array([0, 31, 32, 63]), file_types=np.array(["go"] * 4),
             file_groups=np.array(["native"] * 4), route_names=np.array(["general"]),
             scores=np.array([[.9, .1, .99, .99]], dtype=np.float32))
    return tmp_path / "scores.npz", tmp_path / "route_policies.json"


@pytest.mark.parametrize("levels", [[25], [0, 25], [0, 15, 25], [25, 100]])
def test_current_grid_is_recomputed_even_when_previous_metrics_are_supplied(tmp_path, levels):
    paths = fixture(tmp_path, levels)
    previous = tmp_path / "old.json"
    previous.write_text('{"filetypes":{"go":{"ensemble":{"recall_at_25_per_100M":0}}}}')
    result = metrics.compute_per_filetype_metrics_honest(
        *paths, level=25, previous_metrics_path=previous, include_stacked=True,
    )
    entry = result["filetypes"]["go"]["ensemble"]
    assert result["n_rows_evaluated"] == 2
    assert entry["recall_at_25_per_100M"] == 1
    assert {int(k.split("_")[2]) for k in entry
            if k.startswith("recall_at_") and k.endswith("_per_100M")} == set(levels)


def test_old_public_function_also_requires_locked_test(tmp_path):
    paths = fixture(tmp_path, [25])
    with pytest.raises(ValueError, match="locked test"):
        metrics.compute_per_filetype_metrics(*paths, partition="dev")


def test_missing_canonical_partitions_cannot_report_training_rows(tmp_path):
    paths = fixture(tmp_path, [25])
    with np.load(paths[0]) as table:
        arrays = {name: table[name] for name in table.files if name != "sha_bucket"}
    np.savez(paths[0], **arrays)
    with pytest.raises(ValueError, match="canonical partitions"):
        metrics.compute_per_filetype_metrics(*paths)
