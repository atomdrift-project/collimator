"""filefacts' file groups: the partition every filegroup route trains on.

`data/file_groups.json` is filefacts' `docs/file-groups.json`, vendored so a
route's membership is exactly the grouping filefacts reports at runtime.
Refresh it with `make sync-file-groups` when filefacts adds or regroups a type.
Labels are canonical filefacts labels; `data.expand_filetype_aliases` widens
them to the spellings older catalog rows were stored under.
"""

import json
from pathlib import Path

_TABLE = Path(__file__).parent / "data" / "file_groups.json"

FILE_GROUPS: dict[str, tuple[str, ...]] = {
    group: tuple(types)
    for group, types in json.loads(_TABLE.read_text(encoding="utf-8"))["groups"].items()
}

# Groups that never get a specialist. Single-stream compression is unwrapped
# by litmus and the inner file routed instead, so the wrapper has no signal
# of its own; `unknown` names no format at all.
UNTRAINED_GROUPS: frozenset[str] = frozenset({"compressed", "unknown"})

TRAINED_GROUPS: dict[str, tuple[str, ...]] = {
    group: types for group, types in FILE_GROUPS.items() if group not in UNTRAINED_GROUPS
}

# Canonical filefacts label → its group.
GROUP_OF: dict[str, str] = {ft: group for group, types in FILE_GROUPS.items() for ft in types}
