#!/usr/bin/env bash
set -uo pipefail  # no -e: continue on individual failures

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
export COLLIMATOR_NGRAM_PATH_DEPTH=4
export COLLIMATOR_NGRAM_MIN_CRIT=2
export COLLIMATOR_EXTENDED_METRICS=1
export COLLIMATOR_TAXONOMY_FEATURES=0

ARGS="--db ${DB} --workers 16 --seed 42 \
  --train-samples 100000 --max-test-samples 20000 \
  --cache-dir ${CACHE_DIR} \
  --n-folds 2 --n-estimators 250 --max-depth 14 \
  --learning-rate 0.05 --early-stopping-rounds 30 \
  --colsample-bytree 0.8 --subsample 0.8 \
  --min-child-weight 5 --gamma 0.0 \
  --reg-alpha 0.0 --reg-lambda 1.0 \
  --beta 1.25 --min-malware-score 9"

mkdir -p out/logs/sweep

run() {
  local name=$1
  local log="out/logs/sweep/${name}.log"
  timeout 600 .venv/bin/python -u -m collimator experiment ${ARGS} \
    2>&1 | tee "${log}" > /dev/null
  local rc=$?
  if [ $rc -ne 0 ]; then
    printf "%-35s  FAILED (rc=%d)\n" "$name" "$rc"
    return
  fi
  tf1=$(grep '  F1:' "${log}" 2>/dev/null | awk '{print $2}')
  tp=$(grep '  Precision:' "${log}" 2>/dev/null | awk '{print $2}')
  tr=$(grep '  Recall:' "${log}" 2>/dev/null | awk '{print $2}')
  feat=$(grep 'Features:' "${log}" 2>/dev/null | awk '{print $2}')
  printf "%-35s %6s  F1=%s  P=%s  R=%s\n" "$name" "${feat:-?}" "${tf1:--}" "${tp:--}" "${tr:--}"
}

echo "=== FEATURE TOGGLES ==="
COLLIMATOR_TAXONOMY_FEATURES=1     run "taxonomy"
COLLIMATOR_SILENT_PACKER_SIGNAL=1  run "silent_packer"
COLLIMATOR_MTIME_KURTOSIS=1       run "mtime_kurtosis"
COLLIMATOR_BLINDFOLD=0             run "no_blindfold"
COLLIMATOR_EXTENDED_METRICS=0      run "no_ext_metrics"

echo ""
echo "=== FEATURE GROUP ABLATION ==="
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,bigrams          run "drop_bigrams"
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,trigrams          run "drop_trigrams"
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,signature_synergy run "drop_sig_synergy"
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,elements          run "drop_elements"
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,logic_gaps        run "drop_logic_gaps"
COLLIMATOR_DISABLE_FEATURE_GROUPS=""                         run "enable_clusters"

echo ""
echo "=== NGRAM VARIANTS ==="
COLLIMATOR_NGRAM_PATH_DEPTH=0 COLLIMATOR_NGRAM_MIN_CRIT=2 run "ngram_d0c2"
COLLIMATOR_NGRAM_PATH_DEPTH=3 COLLIMATOR_NGRAM_MIN_CRIT=2 run "ngram_d3c2"
COLLIMATOR_NGRAM_PATH_DEPTH=4 COLLIMATOR_NGRAM_MIN_CRIT=0 run "ngram_d4c0"
COLLIMATOR_NGRAM_PATH_DEPTH=4 COLLIMATOR_NGRAM_MIN_CRIT=3 run "ngram_d4c3"

echo ""
echo "=== DONE ==="
