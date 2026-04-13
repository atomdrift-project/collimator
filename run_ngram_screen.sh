#!/usr/bin/env bash
set -euo pipefail

# N-gram configuration screen: depth x min_crit matrix
# Depths: 0 (full), 2, 3, 4
# Min crit: 0 (all), 1 (component+), 2 (baseline+), 3 (notable+), 4 (suspicious+), 5 (hostile)

CACHE_DIR="out/cache"
WORKERS="${WORKERS:-16}"
TRAIN=50000
TEST=10000

run() {
  local depth=$1 crit=$2
  local name="depth${depth}_crit${crit}"
  local log="out/logs/ngram_${name}.log"
  echo "== ${name}: depth=${depth} min_crit=${crit} =="
  make experiment \
    EXP_TRAIN_SAMPLES=${TRAIN} EXP_MAX_TEST_SAMPLES=${TEST} \
    EXP_WORKERS=${WORKERS} EXP_FOLDS=2 \
    EXP_ESTIMATORS=80 EXP_MAX_DEPTH=8 EXP_LEARNING_RATE=0.05 EXP_EARLY_STOPPING=20 \
    EXP_CACHE_DIR="${CACHE_DIR}" \
    EXP_NGRAM_PATH_DEPTH=${depth} EXP_NGRAM_MIN_CRIT=${crit} \
    EXP_TAG="_ngram_${name}" \
    2>&1 | tee "${log}"
  echo ""
}

mkdir -p out/logs

# Baseline is already cached (depth=0, crit=0) — run it first for reference
run 0 0

# Depth 3: all criticality levels
for crit in 1 2 3 4 5; do
  run 3 $crit
done

# Depth 4: all criticality levels
for crit in 0 1 2 3 4 5; do
  run 4 $crit
done

# Depth 2: all criticality levels
for crit in 0 1 2 3 4 5; do
  run 2 $crit
done

# Depth 0 (full): remaining criticality levels
for crit in 1 2 3 4 5; do
  run 0 $crit
done

echo "== All n-gram experiments complete =="
