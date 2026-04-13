#!/usr/bin/env bash
set -euo pipefail

DB="postgres://hopper@localhost:5432/hopper"
OUT_ROOT="out/benchmarks"
PYTHON=".venv/bin/python"
WORKERS=8
SEED=42

# Scaled Hyperparams (Extreme Run - Safer Limits)
TRAIN_SAMPLES=150000
TEST_SAMPLES=30000
ESTIMATORS=1000
MAX_DEPTH=14
LEARNING_RATE=0.02
EARLY_STOPPING=50
BETA=2.0
FOLDS=5

mkdir -p "${OUT_ROOT}/logs"

run_benchmark() {
  local name="$1"
  shift
  local log_path="${OUT_ROOT}/logs/${name}.log"
  
  echo "== Starting Benchmark: ${name} =="
  echo "Log: ${log_path}"
  
  # Clear log first
  : > "${log_path}"
  
  # Use env to properly handle NAME=VALUE arguments
  env PYTHONUNBUFFERED=1 "$@" \
    "${PYTHON}" -u -m collimator experiment \
      --db "${DB}" \
      --output "${OUT_ROOT}/${name}" \
      --workers "${WORKERS}" \
      --seed "${SEED}" \
      --train-samples "${TRAIN_SAMPLES}" \
      --max-test-samples "${TEST_SAMPLES}" \
      --n-folds "${FOLDS}" \
      --n-estimators "${ESTIMATORS}" \
      --max-depth "${MAX_DEPTH}" \
      --learning-rate "${LEARNING_RATE}" \
      --early-stopping-rounds "${EARLY_STOPPING}" \
      --beta "${BETA}" >> "${log_path}" 2>&1
}

# 1. Semantic Core (Logic Gaps + Signature Synergy)
run_benchmark semantic_core \
  COLLIMATOR_ALLOWED_FEATURES_FILE= \
  COLLIMATOR_DISABLE_FEATURE_GROUPS=neg_space,clusters,intent_gaps \
  COLLIMATOR_SILENT_PACKER_SIGNAL=0 \
  COLLIMATOR_MTIME_KURTOSIS=0 \
  COLLIMATOR_AIR_GAP_SIGNAL=0

# 2. Contextual Scalpel (Silent Packer + Temporal + Negative Space + Air-Gap)
run_benchmark contextual_scalpel \
  COLLIMATOR_ALLOWED_FEATURES_FILE= \
  COLLIMATOR_DISABLE_FEATURE_GROUPS=logic_gaps,signature_synergy,clusters,intent_gaps \
  COLLIMATOR_SILENT_PACKER_SIGNAL=1 \
  COLLIMATOR_MTIME_KURTOSIS=1 \
  COLLIMATOR_AIR_GAP_SIGNAL=1

# 3. Ultimate Fusion (Everything + Doppelganger Anchor)
run_benchmark ultimate_fusion \
  COLLIMATOR_ALLOWED_FEATURES_FILE= \
  COLLIMATOR_SILENT_PACKER_SIGNAL=1 \
  COLLIMATOR_MTIME_KURTOSIS=1 \
  COLLIMATOR_AIR_GAP_SIGNAL=1 \
  COLLIMATOR_DISABLE_FEATURE_GROUPS=

# 4. Extreme Fusion (Ultimate + Contextual Deviance Exps 48-52)
run_benchmark extreme_fusion \
  COLLIMATOR_ALLOWED_FEATURES_FILE= \
  COLLIMATOR_SILENT_PACKER_SIGNAL=1 \
  COLLIMATOR_MTIME_KURTOSIS=1 \
  COLLIMATOR_AIR_GAP_SIGNAL=1 \
  COLLIMATOR_EXTREME_FEATURES=1 \
  COLLIMATOR_DISABLE_FEATURE_GROUPS=

# 5. Denoised Extreme Fusion (Extreme + Heuristic Pruning Exp 53)
run_benchmark denoised_extreme \
  COLLIMATOR_ALLOWED_FEATURES_FILE= \
  COLLIMATOR_SILENT_PACKER_SIGNAL=1 \
  COLLIMATOR_MTIME_KURTOSIS=1 \
  COLLIMATOR_AIR_GAP_SIGNAL=1 \
  COLLIMATOR_EXTREME_FEATURES=1 \
  COLLIMATOR_DISABLE_FEATURE_GROUPS= \
  --min-malware-score 9

echo "== All Benchmarks Complete =="
