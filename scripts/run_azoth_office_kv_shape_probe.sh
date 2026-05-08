#!/usr/bin/env bash
set -uo pipefail

# Small parallel side probe for Office-like filetypes.
# Focus: filetype-local KV/metric vocabularies, key existence, empty values,
# collection sizes, string lengths, numeric buckets, and full metric-key vocab.

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
  EXP_WORKERS="${EXP_WORKERS:-32}"
  EXP_TRAIN_SAMPLES="${EXP_TRAIN_SAMPLES:-30000}"
  EXP_MAX_TEST_SAMPLES="${EXP_MAX_TEST_SAMPLES:-8000}"
  EXP_FOLDS="${EXP_FOLDS:-0}"
  EXP_HOLDOUT_FRACTION="${EXP_HOLDOUT_FRACTION:-0.12}"
  EXP_ESTIMATORS="${EXP_ESTIMATORS:-100}"
  EXP_NUM_LEAVES="${EXP_NUM_LEAVES:-48}"
  EXP_MIN_CHILD_SAMPLES="${EXP_MIN_CHILD_SAMPLES:-20}"
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

  echo
  echo "================================================================"
  echo "[$ran] route=${route} idea=${idea} min_sample_score=0"
  echo "================================================================"

  if make experiment \
    "${common[@]}" \
    EXP_ROUTE="${route}" \
    EXP_IDEA="${idea}" \
    EXP_TAG="_${idea}" \
    EXP_MIN_SAMPLE_SCORE=0 \
    "$@"; then
    successes=$((successes + 1))
  else
    failures+=("${route}:${idea}")
  fi
}

office_shape_base=(
  EXP_KV_VOCAB=1
  EXP_KV_SHAPE_FEATURES=1
  EXP_KV_VOCAB_MAX=20000
  EXP_KV_MIN_FREQ=1
  EXP_TEXT_ENCODING_FEATURES=1
  COLLIMATOR_METRIC_MIN_FREQ_PCT=0
)

echo "azoth office KV-shape probe started: ${started_at}"
echo "workers=${EXP_WORKERS:-32} train_samples=${EXP_TRAIN_SAMPLES:-30000} max_test_samples=${EXP_MAX_TEST_SAMPLES:-8000} skip=${skip} limit=${limit}"

for ft in xlsx pptx; do
  run_experiment "filetypes/${ft}" "${ft}_office_kv_shape_metrics" \
    "${office_shape_base[@]}" EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1

  run_experiment "filetypes/${ft}" "${ft}_office_kv_shape_metadata_only" \
    "${office_shape_base[@]}" \
    EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters

  run_experiment "filetypes/${ft}" "${ft}_office_kv_shape_no_traits" \
    "${office_shape_base[@]}" \
    EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,score,clusters EXP_FORMAT_HINTS=1

  run_experiment "filetypes/${ft}" "${ft}_office_kv_shape_scoreless_hsn" \
    "${office_shape_base[@]}" \
    EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TIERED_CRIT_TRIGRAMS=1 \
    EXP_TIERED_TRIGRAM_PATH_DEPTH=8 EXP_TIERED_TRIGRAM_MIN_CRIT=0 \
    EXP_TIERED_TRIGRAM_MAX=10000

  run_experiment "filetypes/${ft}" "${ft}_office_kv_shape_precision" \
    "${office_shape_base[@]}" EXP_REG_ALPHA=0.5 EXP_REG_LAMBDA=4.0 \
    EXP_NUM_LEAVES=32 EXP_MIN_CHILD_SAMPLES=30

  run_experiment "filetypes/${ft}" "${ft}_office_kv_shape_recall" \
    "${office_shape_base[@]}" EXP_BETA=2.0

  run_experiment "filetypes/${ft}" "${ft}_office_kv_shape_hardtail" \
    "${office_shape_base[@]}" EXP_HARD_NEGATIVE_FRACTION=0.02 \
    EXP_HARD_NEGATIVE_WEIGHT=18

  run_experiment "filetypes/${ft}" "${ft}_office_kv_shape_metrics_only" \
    EXP_KV_VOCAB=0 EXP_KV_SHAPE_FEATURES=0 EXP_TEXT_ENCODING_FEATURES=0 \
    COLLIMATOR_METRIC_MIN_FREQ_PCT=0 \
    EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters,kv,textenc
done

echo
echo "azoth office KV-shape probe complete: successes=${successes} failures=${#failures[@]} ran=${ran}"
if [[ "${#failures[@]}" -gt 0 ]]; then
  printf 'failed: %s\n' "${failures[@]}"
  exit 1
fi
