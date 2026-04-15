#!/usr/bin/env bash
set -uo pipefail

# Experiments targeting FN/FP reduction at 200K scale.
# Focus: trigram vocab coverage, min frequency, benign tolerance,
# more model capacity, and lower malware score threshold.

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

mkdir -p out/logs/fnfp

run() {
  local name=$1; shift
  local log="out/logs/fnfp/${name}.log"
  # Parse KEY=VALUE overrides
  local folds=2 est=250 depth=14 lr=0.05 early=30 beta=1.25 mms=9
  for arg in "$@"; do
    case "$arg" in
      est=*)   est="${arg#*=}" ;;
      depth=*) depth="${arg#*=}" ;;
      lr=*)    lr="${arg#*=}" ;;
      early=*) early="${arg#*=}" ;;
      beta=*)  beta="${arg#*=}" ;;
      mms=*)   mms="${arg#*=}" ;;
      folds=*) folds="${arg#*=}" ;;
    esac
  done
  .venv/bin/python -u -m collimator experiment \
    --db "${DB}" --workers 16 --seed 42 \
    --train-samples 200000 --max-test-samples 30000 \
    --cache-dir "${CACHE_DIR}" \
    --n-folds ${folds} --n-estimators ${est} --max-depth ${depth} \
    --learning-rate ${lr} --early-stopping-rounds ${early} \
    --colsample-bytree 0.8 --subsample 0.8 \
    --min-child-weight 5 --gamma 0.0 \
    --reg-alpha 0.0 --reg-lambda 1.0 \
    --beta ${beta} --min-malware-score ${mms} \
    2>&1 > "${log}"
  tf1=$(grep '  F1:' "${log}" 2>/dev/null | awk '{print $2}')
  tp=$(grep '  Precision:' "${log}" 2>/dev/null | awk '{print $2}')
  tr=$(grep '  Recall:' "${log}" 2>/dev/null | awk '{print $2}')
  feat=$(grep 'Features:' "${log}" 2>/dev/null | awk '{print $2}')
  cvfp=$(grep '    FP' "${log}" 2>/dev/null | awk '{print $2}')
  cvfn=$(grep '    FN' "${log}" 2>/dev/null | awk '{print $2}')
  printf "%-35s %6s  F1=%s P=%s R=%s  cvFP=%s cvFN=%s\n" \
    "$name" "${feat:-?}" "${tf1:--}" "${tp:--}" "${tr:--}" "${cvfp:--}" "${cvfn:--}"
}

echo "=== BASELINE at 200K ==="
run "baseline"

echo ""
echo "=== TRIGRAM VOCAB: coverage + frequency ==="
# Exp 1: More trigrams with relaxed benign filter
COLLIMATOR_TRIGRAM_MAX=1000 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.02 \
  run "tri1000_b2pct"

# Exp 2: Lower min frequency (from 5 to 3) — catch rarer supply-chain patterns
# Need to modify the code for this... use the env var approach
COLLIMATOR_TRIGRAM_MAX=500 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.02 \
  run "tri500_b2pct"

# Exp 3: Much larger vocab with generous benign tolerance
COLLIMATOR_TRIGRAM_MAX=2000 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.02 \
  run "tri2000_b2pct"

echo ""
echo "=== MODEL CAPACITY ==="
# Exp 4: More trees + deeper — let model learn rare FN patterns
run "deep_1000t" est=1000 depth=16 lr=0.02 early=50

# Exp 5: Same capacity with current best trigram config
COLLIMATOR_TRIGRAM_MAX=1000 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.02 \
  run "deep_1000t_tri1k" est=1000 depth=16 lr=0.02 early=50

echo ""
echo "=== MALWARE SCORE THRESHOLD ==="
# Exp 6: Include lower-score malware in training (catch subtle patterns)
run "mms5" mms=5

# Exp 7: No malware score filter at all
run "mms0" mms=0

echo ""
echo "=== PRECISION-RECALL BALANCE ==="
# Exp 8: Slightly more recall-biased to catch FN
run "beta1.5" beta=1.5

# Exp 9: Combined: more capacity + more trigrams + lower mms
COLLIMATOR_TRIGRAM_MAX=1000 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.02 \
  run "combined" est=1000 depth=16 lr=0.02 early=50 mms=5

echo ""
echo "=== DONE ==="
