#!/usr/bin/env bash
set -uo pipefail

# Next round experiments — targeting specific remaining opportunities.
# Uses 200K+ trainable data with tuned hyperparams.

DB="postgres://hopper@localhost:5432/hopper"
CACHE_DIR="out/cache"

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
export COLLIMATOR_ATTACK_FEATURES=1
export COLLIMATOR_CONFIDENCE_WEIGHTED_NGRAMS=0

ARGS="--db ${DB} --workers 16 --seed 42 --train-samples 300000 --max-test-samples 50000 --cache-dir ${CACHE_DIR}"

mkdir -p out/logs/round2

run() {
  local name=$1; shift
  local log="out/logs/round2/${name}.log"
  local est=2000 depth=20 lr=0.02 early=50 beta=1.25 mms=0 folds=2
  for arg in "$@"; do
    case "$arg" in
      est=*)   est="${arg#*=}" ;; depth=*) depth="${arg#*=}" ;;
      lr=*)    lr="${arg#*=}" ;; early=*) early="${arg#*=}" ;;
      beta=*)  beta="${arg#*=}" ;; mms=*)   mms="${arg#*=}" ;;
      folds=*) folds="${arg#*=}" ;;
    esac
  done
  .venv/bin/python -u -m collimator experiment ${ARGS} \
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

echo "=== BASELINE (200K+, 2000t d20) ==="
run "baseline"

echo ""
echo "=== 1. FEATURE PRUNING ==="
# Top 2000 features capture 97.4% of gain. Remove the 86% noise.
COLLIMATOR_ALLOWED_FEATURES_FILE=out/top_2000_features.json \
  run "prune_2k"
COLLIMATOR_ALLOWED_FEATURES_FILE=out/top_1000_features.json \
  run "prune_1k"

echo ""
echo "=== 2. CONFIDENCE-WEIGHTED NGRAMS ==="
COLLIMATOR_CONFIDENCE_WEIGHTED_NGRAMS=1 \
  run "conf_ngrams"

echo ""
echo "=== 3. MORE CAPACITY ==="
# Push trees and depth even further
run "3000t_d22" est=3000 depth=22 early=75
run "5000t_d20" est=5000 depth=20 early=100

echo ""
echo "=== 4. COMBINED WINNERS ==="
# Combine conf-weighted ngrams + more capacity
COLLIMATOR_CONFIDENCE_WEIGHTED_NGRAMS=1 \
  run "conf_5000t" est=5000 depth=20 early=100

echo ""
echo "=== 5. FILETYPE INTERACTIONS ==="
COLLIMATOR_FILETYPE_INTERACTIONS=1 \
  run "filetype_inter"

echo ""
echo "=== 6. 3-FOLD CV ==="
run "3fold" folds=3

echo "=== DONE ==="
