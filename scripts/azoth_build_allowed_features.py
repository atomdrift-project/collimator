#!/usr/bin/env python3
"""Build an allow-list of feature names that pass a min-frequency cull.

Operationalizes the feature-frequency audit's findings as something the
training pipeline can actually consume. cleave's
``COLLIMATOR_ALLOWED_FEATURES_FILE`` env var (collimator/features.py:1306)
already filters the feature spec to a JSON list — we just need to
produce one.

The cull rule, per vocab entry rather than per column:

  Each entry in ``presence_vocab`` / ``bigram_vocab`` / etc. produces
  multiple columns in the matrix (e.g. ``present:X`` AND ``maxcrit:X``
  for presence). We can only safely drop a vocab entry when ALL its
  produced columns have nnz below the threshold — otherwise we'd kill
  high-signal siblings to chase low-signal noise.

  Concretely: group features by their (vocab_key, path), keep the group
  only if ``max(nnz)`` over the group ≥ threshold.

Inputs:
  --audit-csv   CSV produced by azoth_feature_frequency_audit.py
  --threshold   min nnz the group max must clear to be kept

Output: a JSON list of feature_name strings. Hand-off path:

  export COLLIMATOR_ALLOWED_FEATURES_FILE=out/models/azoth/allowed_features_minfreq10.json
  make azoth-publish-train   # or whichever training cycle picks it up

The training pipeline then logs ``pruned feature spec: X -> Y features``
at the start of each vocab build, and Y features get extracted + trained
on instead of X. Both extraction and training scale roughly linearly
with retained feature count.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def _vocab_key_for(feature_name: str) -> tuple[str, str]:
    """Map a feature_name back to its (vocab, key) — the granularity at
    which vocab entries can be dropped.

    Multiple feature names map to the same (vocab, key) tuple — that's
    the whole point of the grouping. Examples:

      present:X         → (presence, X)
      maxcrit:X         → (presence, X)        # same vocab entry
      bigrams:X         → (bigram, X)
      unsigned_bigram:X → (bigram, X)          # same vocab entry
      trigram:X         → (trigram, X)
      tierbi:n:X        → (tierbi, n:X)        # tier modifier stays in key

    Anything else (agg:*, single static features, ...) gets a unique key
    so it's never dropped — the audit shouldn't have included these
    anyway because they're always present.
    """
    for prefix, vocab in (
        ("present:", "presence"),
        ("maxcrit:", "presence"),
        ("bigrams:", "bigram"),
        ("unsigned_bigram:", "bigram"),
        ("trigram:", "trigram"),
        ("tierbi:", "tierbi"),
        ("elements:", "element"),
        ("ghosts:", "ghost"),
        ("skeleton:", "skeleton"),
        ("rares:", "rare_element"),
        ("metrics:", "metric"),
        ("crit_unigram:", "crit_unigram"),
        ("crit_bigram:", "crit_bigram"),
        ("crit_trigram:", "crit_trigram"),
        ("attack_bigram:", "attack_bigram"),
        ("attack_trigram:", "attack_trigram"),
        ("mbc_bigram:", "mbc_bigram"),
        ("mbc_trigram:", "mbc_trigram"),
        ("tiered_quadgram:", "tiered_quadgram"),
        ("symbol:", "symbol"),
        ("symbol_bigram:", "symbol_bigram"),
        ("symbol_trigram:", "symbol_trigram"),
        ("kv:", "kv"),
    ):
        if feature_name.startswith(prefix):
            return (vocab, feature_name[len(prefix):])
    # Unmatched prefix → unique key, won't be dropped.
    return ("singleton", feature_name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-csv",
        type=Path,
        default=Path("out/models/azoth/feature_frequency_audit.csv"),
        help="Per-feature nnz dump from azoth_feature_frequency_audit.py.",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=10,
        help=(
            "Min nnz the vocab group's max must clear. Default 10 — the "
            "elbow where the audit reports zero borderline drops. "
            "Raise this for more aggressive culls."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Where to write the allow-list. Defaults to "
            "out/models/azoth/allowed_features_minfreq{threshold}.json."
        ),
    )
    args = parser.parse_args()

    # Read audit, group by (vocab, key).
    groups: dict[tuple[str, str], list[tuple[str, int]]] = defaultdict(list)
    with open(args.audit_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["feature"]
            nnz = int(row["nnz_total"])
            groups[_vocab_key_for(name)].append((name, nnz))

    # Decide which groups to keep.
    kept_groups = 0
    dropped_groups = 0
    kept_features: list[str] = []
    dropped_features: list[str] = []
    for key, members in groups.items():
        max_nnz = max(n for _, n in members)
        if max_nnz >= args.threshold:
            kept_groups += 1
            for name, _ in members:
                kept_features.append(name)
        else:
            dropped_groups += 1
            for name, _ in members:
                dropped_features.append(name)

    output = args.output or Path(
        f"out/models/azoth/allowed_features_minfreq{args.threshold}.json",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    # Sort the allow-list for stable diffs across re-runs.
    kept_features.sort()
    with open(output, "w") as f:
        json.dump(kept_features, f)

    total = kept_groups + dropped_groups
    print(f"# threshold: nnz_max >= {args.threshold}")
    print(f"vocab groups: {kept_groups:,} kept / {dropped_groups:,} dropped "
          f"({100*dropped_groups/max(total,1):.1f}% reduction)")
    print(f"features:     {len(kept_features):,} kept / {len(dropped_features):,} dropped")
    print()
    print(f"wrote {output}")
    print()
    print("Hand-off — set this env var for the next training cycle:")
    print(f"  export COLLIMATOR_ALLOWED_FEATURES_FILE={output}")
    print()
    print("On the next vocab build cleave will log:")
    print(f"  pruned feature spec: <full_count> -> {len(kept_features):,} features")
    print()
    print("Expected runtime impact:")
    drop_pct = 100 * len(dropped_features) / max(len(kept_features) + len(dropped_features), 1)
    print(f"  ~{drop_pct:.0f}% fewer features → ~{drop_pct*0.8:.0f}% less LightGBM training time")
    print("  (LightGBM training is roughly linear in feature count with force_col_wise=True;")
    print("   the 0.8 factor accounts for fixed per-row overhead that doesn't scale.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
