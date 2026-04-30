#!/usr/bin/env bash
set -uo pipefail

DB="postgres://hopper@localhost:5432/hopper"
CACHE_DIR="out/cache"
PY=".venv/bin/python"

# Base env
export COLLIMATOR_ALLOWED_FEATURES_FILE=
export COLLIMATOR_SILENT_PACKER_SIGNAL=0
export COLLIMATOR_MTIME_KURTOSIS=0
export COLLIMATOR_AIR_GAP_SIGNAL=1
export COLLIMATOR_EXTREME_FEATURES=1
export COLLIMATOR_FILETYPE_INTERACTIONS=0
export COLLIMATOR_BLINDFOLD=1
export COLLIMATOR_SCORE_WEIGHTED_TRAITS=1
export COLLIMATOR_SOFT_PRESENCE=1
export COLLIMATOR_REPETITION_PENALTY_FEATURES=1
export COLLIMATOR_FILE_SEVERITY_DISTRIBUTION=1
export COLLIMATOR_HOSTILE_WEIGHTED_DENSITY=1
export COLLIMATOR_HOSTILE_ESCALATION_FEATURES=1
export COLLIMATOR_SUSPICIOUS_BREADTH_DENSITY=1
export COLLIMATOR_STRUCT_FILE_RISK_COVERAGE=1
export COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters
export COLLIMATOR_PACKAGED_CAPABILITY_MODE=paths
export COLLIMATOR_MIN_SAMPLE_SCORE=3
export COLLIMATOR_NGRAM_PATH_DEPTH=0
export COLLIMATOR_NGRAM_MIN_CRIT=2
export COLLIMATOR_EXTENDED_METRICS=1
export COLLIMATOR_TAXONOMY_FEATURES=0
export COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.01

ARGS="--db ${DB} --workers 16 --seed 42 --train-samples 200000 --max-test-samples 30000 --cache-dir ${CACHE_DIR}"

mkdir -p out/logs/next

run() {
  local name=$1; shift
  local log="out/logs/next/${name}.log"
  local folds=2 est=250 depth=14 lr=0.05 early=30 beta=1.25 mms=0
  for arg in "$@"; do
    case "$arg" in
      est=*)   est="${arg#*=}" ;; depth=*) depth="${arg#*=}" ;;
      lr=*)    lr="${arg#*=}" ;; early=*) early="${arg#*=}" ;;
      beta=*)  beta="${arg#*=}" ;; mms=*)   mms="${arg#*=}" ;;
      folds=*) folds="${arg#*=}" ;;
    esac
  done
  ${PY} -u -m collimator experiment ${ARGS} \
    --n-folds ${folds} --n-estimators ${est} --max-depth ${depth} \
    --learning-rate ${lr} --early-stopping-rounds ${early} \
    --beta ${beta} --min-malware-score ${mms} \
    2>&1 > "${log}"
  tf1=$(grep '  F1:' "${log}" 2>/dev/null | awk '{print $2}')
  tp=$(grep '  Precision:' "${log}" 2>/dev/null | awk '{print $2}')
  tr=$(grep '  Recall:' "${log}" 2>/dev/null | awk '{print $2}')
  feat=$(grep 'Features:' "${log}" 2>/dev/null | awk '{print $2}')
  printf "%-35s %6s  F1=%s P=%s R=%s\n" "$name" "${feat:-?}" "${tf1:--}" "${tp:--}" "${tr:--}"
}

echo "=== BASELINE (new data) ==="
run "baseline"

echo ""
echo "=== A: FEATURE PRUNING + CAPACITY ==="
COLLIMATOR_ALLOWED_FEATURES_FILE=out/top_2000_features.json \
  run "A1_prune2k_deep" est=1500 depth=18 lr=0.02 early=50

COLLIMATOR_ALLOWED_FEATURES_FILE=out/top_1000_features.json \
  run "A2_prune1k_deep" est=2000 depth=20 lr=0.02 early=50

COLLIMATOR_ALLOWED_FEATURES_FILE=out/top_500_features.json \
  run "A3_prune500_deep" est=2000 depth=20 lr=0.02 early=50

COLLIMATOR_ALLOWED_FEATURES_FILE=out/top_3000_features.json \
  run "A4_prune3k" est=500 depth=16 lr=0.03 early=40

echo ""
echo "=== F: ATT&CK FEATURES (if data available) ==="
# These use the new m/a fields — will be empty if data hasn't arrived
COLLIMATOR_ATTACK_FEATURES=1 \
  run "F1_attack_presence"

echo ""
echo "=== E: FP REDUCTION ==="
run "E1_hard_neg" est=250 depth=14

echo ""
echo "=== D: CONFIDENCE-WEIGHTED NGRAMS ==="
COLLIMATOR_CONFIDENCE_WEIGHTED_NGRAMS=1 \
  run "D1_conf_bigrams"

echo "=== DONE ==="
