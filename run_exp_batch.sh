#!/usr/bin/env bash
set -euo pipefail

# Screen 10 experimental features at 100K scale.
# Each experiment enables one feature; "all" enables all 10.

CACHE_DIR="out/cache"
WORKERS="${WORKERS:-16}"
TRAIN=100000
TEST=20000
ESTIMATORS=200
MAX_DEPTH=10
LR=0.03
EARLY=30
FOLDS=2
BETA=2.0

COMMON="EXP_TRAIN_SAMPLES=${TRAIN} EXP_MAX_TEST_SAMPLES=${TEST} \
EXP_WORKERS=${WORKERS} EXP_FOLDS=${FOLDS} \
EXP_ESTIMATORS=${ESTIMATORS} EXP_MAX_DEPTH=${MAX_DEPTH} \
EXP_LEARNING_RATE=${LR} EXP_EARLY_STOPPING=${EARLY} \
EXP_BETA=${BETA} EXP_CACHE_DIR=${CACHE_DIR}"

run() {
  local name=$1
  shift
  local log="out/logs/exp_${name}.log"
  echo "== ${name} =="
  # Export experiment env vars so make's shell inherits them
  for var in "$@"; do
    export "${var?}"
  done
  make experiment ${COMMON} EXP_TAG="_exp_${name}" 2>&1 | tee "${log}"
  # Unset them for next run
  for var in "$@"; do
    unset "${var%%=*}"
  done
  echo ""
}

mkdir -p out/logs

# Baseline: no experimental features
run "baseline"

# Individual experiments
run "exp1_import_cats"       COLLIMATOR_EXP_1=1
run "exp2_api_combo"         COLLIMATOR_EXP_2=1
run "exp3_confidence"        COLLIMATOR_EXP_3=1
run "exp4_depth_var"         COLLIMATOR_EXP_4=1
run "exp5_crit_spread"       COLLIMATOR_EXP_5=1
run "exp6_metric_anomaly"    COLLIMATOR_EXP_6=1
run "exp7_unsigned_imports"  COLLIMATOR_EXP_7=1
run "exp8_entropy_hostile"   COLLIMATOR_EXP_8=1
run "exp9_hostile_obj_div"   COLLIMATOR_EXP_9=1
run "exp10_import_finding"   COLLIMATOR_EXP_10=1

# All 10 combined
run "all_combined" \
  COLLIMATOR_EXP_1=1 COLLIMATOR_EXP_2=1 COLLIMATOR_EXP_3=1 \
  COLLIMATOR_EXP_4=1 COLLIMATOR_EXP_5=1 COLLIMATOR_EXP_6=1 \
  COLLIMATOR_EXP_7=1 COLLIMATOR_EXP_8=1 COLLIMATOR_EXP_9=1 \
  COLLIMATOR_EXP_10=1

echo "== All experiments complete =="
