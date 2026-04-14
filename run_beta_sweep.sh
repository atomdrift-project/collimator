#!/usr/bin/env bash
set -euo pipefail

# Beta sweep: test different F-beta values for threshold selection.
# Matrix cache is shared — only training changes per run.

CACHE_DIR="out/cache"
WORKERS=16
TRAIN=100000
TEST=20000
ESTIMATORS=200
MAX_DEPTH=10
LR=0.03
EARLY=30
FOLDS=2

COMMON="EXP_TRAIN_SAMPLES=${TRAIN} EXP_MAX_TEST_SAMPLES=${TEST} \
EXP_WORKERS=${WORKERS} EXP_FOLDS=${FOLDS} \
EXP_ESTIMATORS=${ESTIMATORS} EXP_MAX_DEPTH=${MAX_DEPTH} \
EXP_LEARNING_RATE=${LR} EXP_EARLY_STOPPING=${EARLY} \
EXP_CACHE_DIR=${CACHE_DIR} EXP_EXTENDED_METRICS=1"

mkdir -p out/logs

for beta in 0.5 0.75 1.0 1.25 1.5 2.0 3.0; do
  name="beta_${beta}"
  log="out/logs/sweep_${name}.log"
  echo "== ${name} =="
  make experiment ${COMMON} EXP_BETA=${beta} EXP_TAG="_sweep_${name}" \
    2>&1 | tee "${log}"
  echo ""
done

echo "== Beta sweep complete =="
