#!/usr/bin/env bash
set -euo pipefail

# Global azoth probes from the current backlog. Keep this intentionally
# simple: edit the make invocations below, run serially, then summarize runs.

common=(
  EXP_WORKERS="${EXP_WORKERS:-64}"
  EXP_ROUTE=general
)

run_experiment() {
  local idea="$1"
  shift

  echo
  echo "== ${idea} =="
  make experiment "${common[@]}" EXP_IDEA="${idea}" EXP_TAG="_${idea}" "$@"
}

run_experiment raw_all_lr03_600_mcs50_seed43 \
  SEED=43 \
  EXP_NGRAM_MIN_CRIT=0 \
  EXP_LEARNING_RATE=0.03 \
  EXP_ESTIMATORS=600 \
  EXP_EARLY_STOPPING=60 \
  EXP_MIN_CHILD_SAMPLES=50

run_experiment raw_all_lr03_600_leaves160_seed43 \
  SEED=43 \
  EXP_NGRAM_MIN_CRIT=0 \
  EXP_LEARNING_RATE=0.03 \
  EXP_ESTIMATORS=600 \
  EXP_EARLY_STOPPING=60 \
  EXP_NUM_LEAVES=160

run_experiment raw_all_lr04_500_seed43 \
  SEED=43 \
  EXP_NGRAM_MIN_CRIT=0 \
  EXP_LEARNING_RATE=0.04 \
  EXP_ESTIMATORS=500 \
  EXP_EARLY_STOPPING=50
