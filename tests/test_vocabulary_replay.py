"""A captured counting stream replays without a database and preserves unions."""
from collections import Counter
import hashlib
from itertools import combinations
import json
from pathlib import Path
import runpy
from types import SimpleNamespace

import pytest


@pytest.mark.parametrize("mode", ["batch", "shard", "bulk"])
@pytest.mark.parametrize("shard_batches", [1, 2, 8])
@pytest.mark.parametrize("token_ids", ["dense", "stable"])
def test_replay_canonical_digest_includes_weighted_documents_and_archives(
    tmp_path, capsys, mode, shard_batches, token_ids,
):
    module = runpy.run_path(str(Path(__file__).parents[1] / "scripts/replay_vocabulary.py"))
    source = tmp_path / "capture.jsonl"
    expected = Counter()
    with source.open("w") as output:
        for batch in range(3):
            single = ["a", "b", "c", "d"]
            files = [["a", "b", "c"], ["b", "c", "e"], ["a", "b", "c"]]
            events = [["trigram", single, 3, None, 2]]
            events += [["trigram", tokens, 3, batch, 1] for tokens in files]
            output.write(json.dumps(dict(rows=3, events=events)) + "\n")
            expected.update({" + ".join(parts): 2 for parts in combinations(single, 3)})
            expected.update({" + ".join(parts) for tokens in files for parts in combinations(tokens, 3)})
    module["replay"](SimpleNamespace(input=source, mode=mode, shard_batches=shard_batches,
                                     scratch=tmp_path, token_ids=token_ids))
    result = json.loads(capsys.readouterr().out)
    digest = hashlib.sha256()
    for token, n in sorted(expected.items()):
        digest.update((json.dumps(["trigram", token, n]) + "\n").encode())
    assert result["digest"] == digest.hexdigest()
    assert result["keys"] == len(expected)
    assert result["rows"] == 9
    assert not list(tmp_path.glob("vocab-replay-*"))
