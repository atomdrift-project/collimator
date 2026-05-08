#!/usr/bin/env bash
set -uo pipefail

# Focused fast tranche for weak/high-volume Azoth routes.
# Uses make experiment's standard probe profile unless overridden by env.

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
  if [[ "${route}" == "filetypes/pe" ]]; then
    # PE feature matrices are much denser than most routes. Keep PE probes
    # inside the fast-iteration budget unless the caller explicitly asks for
    # a larger confirmation profile.
    [[ -z "${EXP_TRAIN_SAMPLES:-}" ]] && profile_overrides+=(EXP_TRAIN_SAMPLES=80000)
    [[ -z "${EXP_MAX_TEST_SAMPLES:-}" ]] && profile_overrides+=(EXP_MAX_TEST_SAMPLES=25000)
    [[ -z "${EXP_ESTIMATORS:-}" ]] && profile_overrides+=(EXP_ESTIMATORS=120)
  fi

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

echo "azoth weak-route tranche started: ${started_at}"
echo "workers=${EXP_WORKERS:-64} train_samples=${EXP_TRAIN_SAMPLES:-150000} max_test_samples=${EXP_MAX_TEST_SAMPLES:-40000} skip=${skip} limit=${limit}"

run_experiment filetypes/pe pe_route_static_tax_no_score \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_EMBER_LITE_FEATURES=1 \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/pe pe_route_tail_static \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_EMBER_LITE_FEATURES=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.008 EXP_HARD_NEGATIVE_WEIGHT=18 \
  EXP_NUM_LEAVES=160 EXP_MIN_CHILD_SAMPLES=60

run_experiment filetypes/javascript javascript_route_hsn8_allcrit \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=12000 \
  EXP_TIERED_TRIGRAM_MIN_FREQ=2

run_experiment filetypes/javascript javascript_route_no_score_objectives \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1 \
  COLLIMATOR_TRIGRAM_MAX=3500 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.003

run_experiment filetypes/python python_route_tax_density_depth8 \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_NGRAM_PATH_DEPTH=8 \
  EXP_NGRAM_MIN_CRIT=0 EXP_HOSTILE_FINDING_DENSITY=1 EXP_HOSTILE_DEPTH_WEIGHT=1 \
  COLLIMATOR_BIGRAM_MAX=12000 COLLIMATOR_BIGRAM_MIN_FREQ=80

run_experiment filetypes/python python_route_no_score_hsn \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TIERED_CRIT_TRIGRAMS=1 \
  EXP_TIERED_TRIGRAM_PATH_DEPTH=6 EXP_TIERED_TRIGRAM_MIN_CRIT=0 \
  EXP_TIERED_TRIGRAM_MAX=10000 EXP_TIERED_TRIGRAM_MIN_FREQ=2

run_experiment filegroups/scripts scripts_route_hsn8_tail \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=15000 \
  EXP_TIERED_TRIGRAM_MIN_FREQ=2 EXP_HARD_NEGATIVE_FRACTION=0.006 \
  EXP_HARD_NEGATIVE_WEIGHT=12

run_experiment filegroups/scripts scripts_route_format_tax_no_score \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_DISABLE_FEATURE_GROUPS=score,clusters \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1

run_experiment filetypes/macho macho_route_static_tax_tail \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_EMBER_LITE_FEATURES=1 \
  COLLIMATOR_METRIC_MIN_FREQ_PCT=0 EXP_HARD_NEGATIVE_FRACTION=0.012 \
  EXP_HARD_NEGATIVE_WEIGHT=18 EXP_NUM_LEAVES=160

run_experiment filetypes/macho macho_route_no_score_deep_ngram \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_NGRAM_PATH_DEPTH=8 \
  EXP_NGRAM_MIN_CRIT=0 COLLIMATOR_BIGRAM_MAX=12000 COLLIMATOR_BIGRAM_MIN_FREQ=60 \
  COLLIMATOR_TRIGRAM_MAX=3000

echo
echo "azoth weak-route tranche complete: successes=${successes} failures=${#failures[@]} ran=${ran}"
if [[ "${#failures[@]}" -gt 0 ]]; then
  printf 'failed: %s\n' "${failures[@]}"
  exit 1
fi
