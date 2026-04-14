#!/usr/bin/env bash
set -euo pipefail

# Comprehensive hyperparameter + knob sweep at 100K scale.

CACHE_DIR="out/cache"
DB="postgres://hopper@localhost:5432/hopper"
PY=".venv/bin/python"
W=16; TRAIN=100000; TEST=20000; SEED=42

# Feature env baseline
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

mkdir -p out/logs/sweep

run() {
  local name=$1; shift
  local log="out/logs/sweep/${name}.log"

  # Build args with defaults, allow caller overrides via named params
  local folds=2 est=200 depth=10 lr=0.03 early=30
  local col=0.8 sub=0.8 mcw=5 gamma=0.0 alpha=0.0 lambda=1.0
  local beta=1.25 mms=9 hn_frac=0.0 hn_w=1.0

  # Parse KEY=VALUE overrides
  for arg in "$@"; do
    case "$arg" in
      folds=*)  folds="${arg#*=}" ;;
      est=*)    est="${arg#*=}" ;;
      depth=*)  depth="${arg#*=}" ;;
      lr=*)     lr="${arg#*=}" ;;
      early=*)  early="${arg#*=}" ;;
      col=*)    col="${arg#*=}" ;;
      sub=*)    sub="${arg#*=}" ;;
      mcw=*)    mcw="${arg#*=}" ;;
      gamma=*)  gamma="${arg#*=}" ;;
      alpha=*)  alpha="${arg#*=}" ;;
      lambda=*) lambda="${arg#*=}" ;;
      beta=*)   beta="${arg#*=}" ;;
      mms=*)    mms="${arg#*=}" ;;
      hn_frac=*) hn_frac="${arg#*=}" ;;
      hn_w=*)   hn_w="${arg#*=}" ;;
    esac
  done

  ${PY} -u -m collimator experiment \
    --db "${DB}" --workers ${W} --seed ${SEED} \
    --train-samples ${TRAIN} --max-test-samples ${TEST} \
    --cache-dir "${CACHE_DIR}" \
    --n-folds ${folds} --n-estimators ${est} --max-depth ${depth} \
    --learning-rate ${lr} --early-stopping-rounds ${early} \
    --colsample-bytree ${col} --subsample ${sub} \
    --min-child-weight ${mcw} --gamma ${gamma} \
    --reg-alpha ${alpha} --reg-lambda ${lambda} \
    --beta ${beta} --min-malware-score ${mms} \
    --hard-negative-fraction ${hn_frac} --hard-negative-weight ${hn_w} \
    2>&1 | tee "${log}" > /dev/null

  tf1=$(grep '  F1:' "${log}" 2>/dev/null | awk '{print $2}')
  tp=$(grep '  Precision:' "${log}" 2>/dev/null | awk '{print $2}')
  tr=$(grep '  Recall:' "${log}" 2>/dev/null | awk '{print $2}')
  feat=$(grep 'Features:' "${log}" 2>/dev/null | awk '{print $2}')
  printf "%-35s %6s  F1=%s  P=%s  R=%s\n" "$name" "${feat:-?}" "${tf1:--}" "${tp:--}" "${tr:--}"
}

echo "================================================================"
echo "BASELINE"
echo "================================================================"
run "baseline"

echo ""
echo "================================================================"
echo "LEARNING RATE × ESTIMATORS"
echo "================================================================"
run "lr005_est500"  lr=0.005 est=500
run "lr01_est400"   lr=0.01  est=400
run "lr01_est600"   lr=0.01  est=600
run "lr02_est300"   lr=0.02  est=300
run "lr02_est500"   lr=0.02  est=500
run "lr05_est150"   lr=0.05  est=150
run "lr05_est250"   lr=0.05  est=250
run "lr10_est100"   lr=0.10  est=100

echo ""
echo "================================================================"
echo "MAX DEPTH"
echo "================================================================"
run "depth6"   depth=6
run "depth8"   depth=8
run "depth12"  depth=12
run "depth14"  depth=14
run "depth16"  depth=16
run "depth20"  depth=20

echo ""
echo "================================================================"
echo "COLSAMPLE_BYTREE"
echo "================================================================"
run "col03"  col=0.3
run "col05"  col=0.5
run "col06"  col=0.6
run "col07"  col=0.7
run "col09"  col=0.9
run "col10"  col=1.0

echo ""
echo "================================================================"
echo "SUBSAMPLE"
echo "================================================================"
run "sub05"  sub=0.5
run "sub06"  sub=0.6
run "sub07"  sub=0.7
run "sub09"  sub=0.9
run "sub10"  sub=1.0

echo ""
echo "================================================================"
echo "MIN CHILD WEIGHT"
echo "================================================================"
run "mcw1"   mcw=1
run "mcw3"   mcw=3
run "mcw10"  mcw=10
run "mcw20"  mcw=20
run "mcw50"  mcw=50

echo ""
echo "================================================================"
echo "GAMMA"
echo "================================================================"
run "gamma01"  gamma=0.1
run "gamma05"  gamma=0.5
run "gamma10"  gamma=1.0
run "gamma30"  gamma=3.0
run "gamma50"  gamma=5.0

echo ""
echo "================================================================"
echo "REG LAMBDA"
echo "================================================================"
run "lambda01"  lambda=0.1
run "lambda05"  lambda=0.5
run "lambda20"  lambda=2.0
run "lambda50"  lambda=5.0
run "lambda100" lambda=10.0

echo ""
echo "================================================================"
echo "REG ALPHA"
echo "================================================================"
run "alpha01"  alpha=0.1
run "alpha05"  alpha=0.5
run "alpha10"  alpha=1.0
run "alpha50"  alpha=5.0

echo ""
echo "================================================================"
echo "N FOLDS"
echo "================================================================"
run "fold3"  folds=3
run "fold5"  folds=5

echo ""
echo "================================================================"
echo "EARLY STOPPING"
echo "================================================================"
run "early10"   early=10
run "early20"   early=20
run "early50"   early=50
run "early100"  early=100

echo ""
echo "================================================================"
echo "HARD NEGATIVE MINING"
echo "================================================================"
run "hn001_w2"  hn_frac=0.01 hn_w=2.0
run "hn002_w3"  hn_frac=0.02 hn_w=3.0
run "hn005_w2"  hn_frac=0.05 hn_w=2.0
run "hn005_w5"  hn_frac=0.05 hn_w=5.0
run "hn010_w3"  hn_frac=0.10 hn_w=3.0

echo ""
echo "================================================================"
echo "MIN MALWARE TRAINING SCORE"
echo "================================================================"
run "mms0"   mms=0
run "mms5"   mms=5
run "mms15"  mms=15
run "mms20"  mms=20

echo ""
echo "================================================================"
echo "FEATURE TOGGLES (re-extraction)"
echo "================================================================"
COLLIMATOR_FILETYPE_INTERACTIONS=1 run "filetype_inter"
COLLIMATOR_TAXONOMY_FEATURES=1     run "taxonomy"
COLLIMATOR_SILENT_PACKER_SIGNAL=1  run "silent_packer"
COLLIMATOR_MTIME_KURTOSIS=1       run "mtime_kurtosis"
COLLIMATOR_BLINDFOLD=0             run "no_blindfold"
COLLIMATOR_EXTENDED_METRICS=0      run "no_ext_metrics"

echo ""
echo "================================================================"
echo "FEATURE GROUP ABLATION (re-extraction)"
echo "================================================================"
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,bigrams          run "drop_bigrams"
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,trigrams          run "drop_trigrams"
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,ghosts            run "drop_ghosts"
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,rares             run "drop_rares"
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,neg_space         run "drop_neg_space"
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,signature_synergy run "drop_sig_synergy"
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,logic_gaps        run "drop_logic_gaps"
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,skeletons         run "drop_skeletons"
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,elements          run "drop_elements"
COLLIMATOR_DISABLE_FEATURE_GROUPS=clusters,intent_gaps       run "drop_intent_gaps"
COLLIMATOR_DISABLE_FEATURE_GROUPS=""                         run "enable_clusters"

echo ""
echo "================================================================"
echo "NGRAM VARIANTS (re-extraction)"
echo "================================================================"
COLLIMATOR_NGRAM_PATH_DEPTH=0 COLLIMATOR_NGRAM_MIN_CRIT=2 run "ngram_d0c2"
COLLIMATOR_NGRAM_PATH_DEPTH=3 COLLIMATOR_NGRAM_MIN_CRIT=2 run "ngram_d3c2"
COLLIMATOR_NGRAM_PATH_DEPTH=4 COLLIMATOR_NGRAM_MIN_CRIT=0 run "ngram_d4c0"
COLLIMATOR_NGRAM_PATH_DEPTH=4 COLLIMATOR_NGRAM_MIN_CRIT=3 run "ngram_d4c3"

echo ""
echo "================================================================"
echo "MIN SAMPLE SCORE (new corpus)"
echo "================================================================"
COLLIMATOR_MIN_SAMPLE_SCORE=1 run "score_ge1"
COLLIMATOR_MIN_SAMPLE_SCORE=2 run "score_ge2"
COLLIMATOR_MIN_SAMPLE_SCORE=5 run "score_ge5"

echo ""
echo "== Full sweep complete: $(ls out/logs/sweep/*.log 2>/dev/null | wc -l) experiments =="
