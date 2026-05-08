#!/usr/bin/env bash
set -uo pipefail

# Aggressive Azoth experiment tranche.
# Serial by design: these are high-risk feature spaces, and parallel runs fight
# LightGBM, Postgres, and the sparse-matrix cache.

started_at="$(date -Is)"
failures=()
successes=0
limit="${RUN_LIMIT:-0}"
skip="${RUN_SKIP:-0}"
ran=0
seen=0

common=(
  MODEL=azoth
  LEARNER=azoth
  EXP_WORKERS="${EXP_WORKERS:-64}"
  EXP_TRAIN_SAMPLES="${EXP_TRAIN_SAMPLES:-150000}"
  EXP_MAX_TEST_SAMPLES="${EXP_MAX_TEST_SAMPLES:-40000}"
  EXP_FOLDS="${EXP_FOLDS:-0}"
  EXP_HOLDOUT_FRACTION="${EXP_HOLDOUT_FRACTION:-0.12}"
  EXP_ESTIMATORS="${EXP_ESTIMATORS:-180}"
  EXP_NUM_LEAVES="${EXP_NUM_LEAVES:-96}"
  EXP_MIN_CHILD_SAMPLES="${EXP_MIN_CHILD_SAMPLES:-100}"
  EXP_REFRESH_CACHE_SNAPSHOT="${EXP_REFRESH_CACHE_SNAPSHOT:-0}"
)

run_experiment() {
  local route="$1"
  local idea="$2"
  shift 2

  seen=$((seen + 1))
  if [[ "${skip}" -gt 0 && "${seen}" -le "${skip}" ]]; then
    echo "skip [$seen] route=${route} idea=${idea}"
    return 0
  fi
  if [[ "${limit}" -gt 0 && "${ran}" -ge "${limit}" ]]; then
    return 0
  fi
  ran=$((ran + 1))

  local min_score=3
  if [[ "${route}" == filegroups/* || "${route}" == filetypes/* ]]; then
    min_score=0
  fi

  local profile_overrides=()
  case "${route}" in
    filetypes/pe)
      [[ -z "${EXP_TRAIN_SAMPLES:-}" ]] && profile_overrides+=(EXP_TRAIN_SAMPLES=80000)
      [[ -z "${EXP_MAX_TEST_SAMPLES:-}" ]] && profile_overrides+=(EXP_MAX_TEST_SAMPLES=25000)
      [[ -z "${EXP_ESTIMATORS:-}" ]] && profile_overrides+=(EXP_ESTIMATORS=120)
      ;;
    filegroups/scripts|filegroups/native)
      [[ -z "${EXP_TRAIN_SAMPLES:-}" ]] && profile_overrides+=(EXP_TRAIN_SAMPLES=110000)
      [[ -z "${EXP_MAX_TEST_SAMPLES:-}" ]] && profile_overrides+=(EXP_MAX_TEST_SAMPLES=30000)
      [[ -z "${EXP_ESTIMATORS:-}" ]] && profile_overrides+=(EXP_ESTIMATORS=150)
      ;;
  esac

  echo
  echo "================================================================"
  echo "[$ran] route=${route} idea=${idea} min_sample_score=${min_score}"
  echo "================================================================"

  if make experiment \
    "${common[@]}" \
    "${profile_overrides[@]}" \
    EXP_ROUTE="${route}" \
    EXP_IDEA="${idea}" \
    EXP_TAG="_${idea}" \
    EXP_MIN_SAMPLE_SCORE="${min_score}" \
    "$@"; then
    successes=$((successes + 1))
  else
    failures+=("${route}:${idea}")
  fi
}

echo "azoth aggressive tranche started: ${started_at}"
echo "workers=${EXP_WORKERS:-64} train_samples=${EXP_TRAIN_SAMPLES:-150000} max_test_samples=${EXP_MAX_TEST_SAMPLES:-40000} skip=${skip} limit=${limit}"

run_experiment general general_hsn8_tax_format_no_score \
  EXP_MIN_SAMPLE_SCORE=0 EXP_DISABLE_FEATURE_GROUPS=score,clusters \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_TIERED_CRIT_TRIGRAMS=1 \
  EXP_TIERED_TRIGRAM_PATH_DEPTH=8 EXP_TIERED_TRIGRAM_MIN_CRIT=0 \
  EXP_TIERED_TRIGRAM_MAX=18000 EXP_TIERED_TRIGRAM_MIN_FREQ=2

run_experiment general general_static_tax_hardtail \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_EMBER_LITE_FEATURES=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.006 EXP_HARD_NEGATIVE_WEIGHT=14 \
  EXP_NUM_LEAVES=160 EXP_MIN_CHILD_SAMPLES=80

run_experiment general general_sparse_regularized_tail \
  EXP_REG_ALPHA=0.25 EXP_REG_LAMBDA=2.5 EXP_COLSAMPLE_BYTREE=0.65 \
  EXP_SUBSAMPLE=0.9 EXP_HARD_NEGATIVE_FRACTION=0.01 EXP_HARD_NEGATIVE_WEIGHT=10 \
  EXP_NUM_LEAVES=64 EXP_MIN_CHILD_SAMPLES=180

run_experiment general general_deep_recall_beta2 \
  EXP_BETA=2.0 EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=6 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=12000 \
  COLLIMATOR_BIGRAM_MAX=12000 COLLIMATOR_BIGRAM_MIN_FREQ=80

run_experiment general general_scoreless_objective_attack \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters COLLIMATOR_OBJECTIVE_TRIGRAMS=1 \
  COLLIMATOR_ATTACK_NGRAMS=1 COLLIMATOR_TRIGRAM_MAX=4000 \
  COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.002

run_experiment filetypes/javascript js_scoreless_hsn10_ultradeep \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TIERED_CRIT_TRIGRAMS=1 \
  EXP_TIERED_TRIGRAM_PATH_DEPTH=10 EXP_TIERED_TRIGRAM_MIN_CRIT=0 \
  EXP_TIERED_TRIGRAM_MAX=20000 EXP_TIERED_TRIGRAM_MIN_FREQ=1

run_experiment filetypes/javascript js_objective_attack_static_tail \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1 \
  COLLIMATOR_ATTACK_NGRAMS=1 EXP_HARD_NEGATIVE_FRACTION=0.01 \
  EXP_HARD_NEGATIVE_WEIGHT=12 EXP_NUM_LEAVES=160

run_experiment filetypes/javascript js_no_presence_ngrams_only \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,score,clusters \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=15000 \
  COLLIMATOR_BIGRAM_MAX=15000 COLLIMATOR_BIGRAM_MIN_FREQ=2

run_experiment filetypes/python py_promoted_plus_hardtail \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_NGRAM_PATH_DEPTH=8 \
  EXP_NGRAM_MIN_CRIT=0 EXP_HOSTILE_FINDING_DENSITY=1 EXP_HOSTILE_DEPTH_WEIGHT=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.008 EXP_HARD_NEGATIVE_WEIGHT=12 \
  COLLIMATOR_BIGRAM_MAX=12000 COLLIMATOR_BIGRAM_MIN_FREQ=80

run_experiment filetypes/python py_scoreless_hsn_tax \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_FORMAT_HINTS=1 \
  EXP_TAXONOMY_FEATURES=1 EXP_TIERED_CRIT_TRIGRAMS=1 \
  EXP_TIERED_TRIGRAM_PATH_DEPTH=8 EXP_TIERED_TRIGRAM_MIN_CRIT=0 \
  EXP_TIERED_TRIGRAM_MAX=16000 EXP_TIERED_TRIGRAM_MIN_FREQ=2

run_experiment filetypes/python py_struct_metrics_only_tail \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,rares,skeletons,score,clusters \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_EMBER_LITE_FEATURES=1 \
  EXP_HOSTILE_FINDING_DENSITY=1 EXP_HOSTILE_DEPTH_WEIGHT=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.012 EXP_HARD_NEGATIVE_WEIGHT=16

run_experiment filegroups/scripts scripts_scoreless_objective_attack \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_FORMAT_HINTS=1 \
  EXP_TAXONOMY_FEATURES=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1 \
  COLLIMATOR_ATTACK_NGRAMS=1 COLLIMATOR_TRIGRAM_MAX=5000

run_experiment filegroups/scripts scripts_hsn10_hardtail \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=10 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=20000 \
  EXP_TIERED_TRIGRAM_MIN_FREQ=1 EXP_HARD_NEGATIVE_FRACTION=0.01 \
  EXP_HARD_NEGATIVE_WEIGHT=14

run_experiment filegroups/scripts scripts_low_leaf_precision \
  EXP_REG_ALPHA=0.5 EXP_REG_LAMBDA=3.0 EXP_NUM_LEAVES=48 \
  EXP_MIN_CHILD_SAMPLES=220 EXP_HARD_NEGATIVE_FRACTION=0.015 \
  EXP_HARD_NEGATIVE_WEIGHT=18 EXP_TIERED_CRIT_TRIGRAMS=1

run_experiment filetypes/macho macho_static_tax_hardtail \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_EMBER_LITE_FEATURES=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.015 EXP_HARD_NEGATIVE_WEIGHT=20 \
  EXP_NUM_LEAVES=160 EXP_MIN_CHILD_SAMPLES=60

run_experiment filetypes/macho macho_scoreless_hsn8 \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TIERED_CRIT_TRIGRAMS=1 \
  EXP_TIERED_TRIGRAM_PATH_DEPTH=8 EXP_TIERED_TRIGRAM_MIN_CRIT=0 \
  EXP_TIERED_TRIGRAM_MAX=12000 EXP_TIERED_TRIGRAM_MIN_FREQ=2 \
  COLLIMATOR_BIGRAM_MAX=12000 COLLIMATOR_BIGRAM_MIN_FREQ=40

run_experiment filetypes/pe pe_static_tax_scoreless_small \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_EMBER_LITE_FEATURES=1 \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/pe pe_precision_tiny_leaf_tail \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_EMBER_LITE_FEATURES=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.015 EXP_HARD_NEGATIVE_WEIGHT=24 \
  EXP_NUM_LEAVES=64 EXP_MIN_CHILD_SAMPLES=240 EXP_REG_ALPHA=0.5 \
  EXP_REG_LAMBDA=4.0

run_experiment filegroups/native native_static_hsn_hardtail \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_EMBER_LITE_FEATURES=1 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=12000 \
  EXP_HARD_NEGATIVE_FRACTION=0.01 EXP_HARD_NEGATIVE_WEIGHT=16

run_experiment filegroups/source source_formula_density_tax \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_NGRAM_PATH_DEPTH=8 \
  EXP_NGRAM_MIN_CRIT=0 EXP_HOSTILE_FINDING_DENSITY=1 \
  EXP_HOSTILE_DEPTH_WEIGHT=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1 \
  COLLIMATOR_BIGRAM_MAX=12000 COLLIMATOR_BIGRAM_MIN_FREQ=40

echo
echo "azoth aggressive tranche complete: successes=${successes} failures=${#failures[@]} ran=${ran}"
if [[ "${#failures[@]}" -gt 0 ]]; then
  printf 'failed: %s\n' "${failures[@]}"
  exit 1
fi
