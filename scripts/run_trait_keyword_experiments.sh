#!/usr/bin/env bash
set -euo pipefail

# Keep ingestion and label updates from changing rows between variants.
if [[ "${KEYWORD_SNAPSHOT_OWNER:-0}" != 1 ]]; then
  db="${DB:-postgres://hopper@localhost:5432/hopper}"
  for arg in "$@"; do
    case "$arg" in DB=*) db="${arg#DB=}" ;; esac
  done
  export KEYWORD_SNAPSHOT_OWNER=1
  exec "${PYTHON:-.venv/bin/python}" scripts/corpus_snapshot.py --db "$db" -- bash "$0" "$@"
fi

# Four matched probes. Pass ordinary make overrides, e.g. SEED=43 or DB=...
# Separate output directories retain each model/spec; the corpus cache is shared.
root="${KEYWORD_OUT_DIR:-out/experiments/trait-keywords}"
common=(
  "EXP_ROUTE=${EXP_ROUTE:-filegroups/scripts}"
  "EXP_WORKERS=${EXP_WORKERS:-4}"
  "EXP_CACHE_DIR=${root}/cache"
  EXP_ALLOWED_FEATURES_FILE=
  EXP_KEYWORD_VOCAB_MAX=10000
)
for variant in baseline ids descriptions both; do
  ids=0
  descriptions=0
  case "$variant" in
    ids) ids=1 ;;
    descriptions) descriptions=1 ;;
    both) ids=1; descriptions=1 ;;
  esac
  make experiment "${common[@]}" "$@" \
    "EXP_IDEA=trait_keywords_${variant}" \
    "EXP_OUT_DIR=${root}/${variant}" \
    "EXP_RULE_KEYWORDS=${ids}" \
    "EXP_DESCRIPTION_KEYWORDS=${descriptions}"
done
