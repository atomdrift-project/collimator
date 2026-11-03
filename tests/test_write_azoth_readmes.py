"""README generation supports unchanged retained-model benchmarks."""

import json

import pytest

from scripts import write_azoth_readmes as readmes


@pytest.mark.parametrize("metadata", [
    {},
    {"name": "general", "kind": "general"},
    {"name": "elf", "kind": "filetype"},
])
def test_retained_route_uses_bundle_slot_without_rewriting_benchmark(tmp_path, metadata):
    route = tmp_path / "filegroups" / "general_oct26"
    route.mkdir(parents=True)
    benchmark = route / "benchmark.json"
    original = json.dumps({"file_types": [], "train_config": {}, **metadata})
    benchmark.write_text(original)

    readmes._write_route(tmp_path, route)

    content = (route / "README.md").read_text()
    assert content.startswith("# `filegroup/general_oct26`\n")
    assert "for all file types." in content
    assert benchmark.read_text() == original


def test_filetype_route_keeps_held_out_metrics(tmp_path):
    route = tmp_path / "filetypes" / "elf"
    route.mkdir(parents=True)
    (route / "benchmark.json").write_text(json.dumps({
        "name": "elf", "kind": "filetype", "file_types": ["elf"],
    }))
    (tmp_path / "per_filetype_metrics.json").write_text(json.dumps({
        "filetypes": {"elf": {"n_files": 12, "n_malware": 9, "n_benign": 3,
                              "ensemble_allowed_routes": ["general", "filetypes/elf"]}},
    }))

    readmes._write_route(tmp_path, route)

    content = (route / "README.md").read_text()
    assert content.startswith("# `filetype/elf`\n")
    assert "9 malware / 3 benign (12 rows)" in content
    assert "scored by `general`, `filetypes/elf`" in content
