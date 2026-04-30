#!/usr/bin/env bash
set -uo pipefail

# Sweep bigram/trigram vocab sizes at 100K with tuned hyperparams.
# Uses d0c2 (full depth, crit=2) since that won the feature knob sweep.

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

ARGS="--db ${DB} --workers 16 --seed 42 \
  --train-samples 100000 --max-test-samples 20000 \
  --cache-dir ${CACHE_DIR} \
  --n-folds 2 --n-estimators 250 --max-depth 14 \
  --learning-rate 0.05 --early-stopping-rounds 30 \
  --colsample-bytree 0.8 --subsample 0.8 \
  --min-child-weight 5 --gamma 0.0 \
  --reg-alpha 0.0 --reg-lambda 1.0 \
  --beta 1.25 --min-malware-score 9"

mkdir -p out/logs/vocab

run() {
  local name=$1
  local log="out/logs/vocab/${name}.log"
  if grep -q 'experiment run summary' "$log" 2>/dev/null; then
    tf1=$(grep '  F1:' "$log" | awk '{print $2}')
    tp=$(grep '  Precision:' "$log" | awk '{print $2}')
    feat=$(grep 'Features:' "$log" | awk '{print $2}')
    printf "CACHED:  %-30s %6s  F1=%s  P=%s\n" "$name" "$feat" "$tf1" "$tp"
    return
  fi
  .venv/bin/python -u -m collimator experiment ${ARGS} 2>&1 > "$log"
  tf1=$(grep '  F1:' "$log" 2>/dev/null | awk '{print $2}')
  tp=$(grep '  Precision:' "$log" 2>/dev/null | awk '{print $2}')
  tr=$(grep '  Recall:' "$log" 2>/dev/null | awk '{print $2}')
  feat=$(grep 'Features:' "$log" 2>/dev/null | awk '{print $2}')
  printf "%-35s %6s  F1=%s  P=%s  R=%s\n" "$name" "${feat:-?}" "${tf1:--}" "${tp:--}" "${tr:--}"
}

echo "=== TRIGRAM VOCAB SIZE (bigrams=5000, benign_frac=0.0) ==="
COLLIMATOR_TRIGRAM_MAX=0     run "tri0"
COLLIMATOR_TRIGRAM_MAX=50    run "tri50"
COLLIMATOR_TRIGRAM_MAX=100   run "tri100"
COLLIMATOR_TRIGRAM_MAX=250   run "tri250"
COLLIMATOR_TRIGRAM_MAX=500   run "tri500"
COLLIMATOR_TRIGRAM_MAX=1000  run "tri1000"
COLLIMATOR_TRIGRAM_MAX=2000  run "tri2000"

echo ""
echo "=== TRIGRAM BENIGN TOLERANCE (trigrams=500) ==="
COLLIMATOR_TRIGRAM_MAX=500 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.005 run "tri500_b05pct"
COLLIMATOR_TRIGRAM_MAX=500 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.01  run "tri500_b1pct"
COLLIMATOR_TRIGRAM_MAX=500 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.02  run "tri500_b2pct"
COLLIMATOR_TRIGRAM_MAX=1000 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.01 run "tri1000_b1pct"

echo ""
echo "=== BIGRAM VOCAB SIZE (trigrams=500) ==="
COLLIMATOR_BIGRAM_MAX=1000  run "bi1000"
COLLIMATOR_BIGRAM_MAX=2500  run "bi2500"
COLLIMATOR_BIGRAM_MAX=5000  run "bi5000"
COLLIMATOR_BIGRAM_MAX=7500  run "bi7500"
COLLIMATOR_BIGRAM_MAX=10000 run "bi10000"

echo ""
echo "=== BIGRAM MIN FREQ (bigrams=5000) ==="
COLLIMATOR_BIGRAM_MIN_FREQ=500  run "bi_freq500"
COLLIMATOR_BIGRAM_MIN_FREQ=2000 run "bi_freq2000"
COLLIMATOR_BIGRAM_MIN_FREQ=3000 run "bi_freq3000"

echo ""
echo "=== COMBINED BEST ==="
# Will fill in after seeing individual winners

echo "== DONE =="
