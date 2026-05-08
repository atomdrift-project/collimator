#!/usr/bin/env bash
set -uo pipefail

# All-filetype overnight tranche.
# Eight experiments per eligible filetype, smallest pools first.

exec "${PYTHON:-.venv/bin/python}" scripts/azoth_filetype_manifest_tranche.py "$@"

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
  EXP_TRAIN_SAMPLES="${EXP_TRAIN_SAMPLES:-80000}"
  EXP_MAX_TEST_SAMPLES="${EXP_MAX_TEST_SAMPLES:-22000}"
  EXP_FOLDS="${EXP_FOLDS:-0}"
  EXP_HOLDOUT_FRACTION="${EXP_HOLDOUT_FRACTION:-0.12}"
  EXP_ESTIMATORS="${EXP_ESTIMATORS:-120}"
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

  local min_score=0
  local profile_overrides=()
  case "${route}" in
    filetypes/javascript|filetypes/python|filetypes/xml)
      [[ -z "${EXP_TRAIN_SAMPLES:-}" ]] && profile_overrides+=(EXP_TRAIN_SAMPLES=90000)
      [[ -z "${EXP_MAX_TEST_SAMPLES:-}" ]] && profile_overrides+=(EXP_MAX_TEST_SAMPLES=25000)
      [[ -z "${EXP_ESTIMATORS:-}" ]] && profile_overrides+=(EXP_ESTIMATORS=130)
      ;;
    filetypes/html|filetypes/batch|filetypes/powershell)
      [[ -z "${EXP_ESTIMATORS:-}" ]] && profile_overrides+=(EXP_ESTIMATORS=120)
      [[ -z "${EXP_MIN_CHILD_SAMPLES:-}" ]] && profile_overrides+=(EXP_MIN_CHILD_SAMPLES=50)
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

echo "azoth filetype night tranche started: ${started_at}"
echo "workers=${EXP_WORKERS:-64} train_samples=${EXP_TRAIN_SAMPLES:-80000} max_test_samples=${EXP_MAX_TEST_SAMPLES:-22000} skip=${skip} limit=${limit}"

# shell
run_experiment filetypes/shell shell_kv_metric_textenc_reg \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=12000 EXP_KV_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_FORMAT_HINTS=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0 \
  EXP_REG_ALPHA=0.25 EXP_REG_LAMBDA=2.5

run_experiment filetypes/shell shell_kv_metric_symbols \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=12000 EXP_KV_MIN_FREQ=1 \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=10000 EXP_SYMBOL_MIN_FREQ=2 \
  EXP_TEXT_ENCODING_FEATURES=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/shell shell_metadata_only_tail \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=14000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.015 EXP_HARD_NEGATIVE_WEIGHT=16

run_experiment filetypes/shell shell_objective_attack_kv \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=8000 EXP_TEXT_ENCODING_FEATURES=1 \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1 \
  COLLIMATOR_TRIGRAM_MAX=4000 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.003

run_experiment filetypes/shell shell_scoreless_kv_hsn8 \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_KV_VOCAB=1 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_TIERED_CRIT_TRIGRAMS=1 \
  EXP_TIERED_TRIGRAM_PATH_DEPTH=8 EXP_TIERED_TRIGRAM_MIN_CRIT=0 \
  EXP_TIERED_TRIGRAM_MAX=9000

run_experiment filetypes/shell shell_low_leaf_precision_kv \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=12000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_NUM_LEAVES=48 EXP_MIN_CHILD_SAMPLES=180 EXP_REG_ALPHA=0.5 \
  EXP_REG_LAMBDA=4.0

run_experiment filetypes/shell shell_recall_beta2_kv \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=12000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_BETA=2.0 EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=6 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0

run_experiment filetypes/shell shell_textenc_only_no_kv \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_FORMAT_HINTS=1 EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=6

# batch
run_experiment filetypes/batch batch_kv_textenc_cmd \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=8000 EXP_KV_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_FORMAT_HINTS=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1

run_experiment filetypes/batch batch_symbols_kv_textenc \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=7000 EXP_SYMBOL_MIN_FREQ=1 \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=7000 EXP_TEXT_ENCODING_FEATURES=1

run_experiment filetypes/batch batch_metadata_only \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=9000 EXP_TEXT_ENCODING_FEATURES=1

run_experiment filetypes/batch batch_scoreless_hsn10 \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=10 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=10000

run_experiment filetypes/batch batch_tail_low_child \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=7000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.02 EXP_HARD_NEGATIVE_WEIGHT=18 \
  EXP_MIN_CHILD_SAMPLES=30

run_experiment filetypes/batch batch_precision_regularized \
  EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 EXP_NUM_LEAVES=48 \
  EXP_MIN_CHILD_SAMPLES=90 EXP_REG_ALPHA=0.5 EXP_REG_LAMBDA=4.0

run_experiment filetypes/batch batch_objective_attack_symbols \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=7000 EXP_TEXT_ENCODING_FEATURES=1 \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1 COLLIMATOR_TRIGRAM_MAX=3000

run_experiment filetypes/batch batch_no_presence_cmd_surface \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,score,clusters EXP_SYMBOL_VOCAB=1 \
  EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 EXP_FORMAT_HINTS=1

# powershell
run_experiment filetypes/powershell powershell_textenc_kv_no_tail \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=7000 EXP_KV_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_FORMAT_HINTS=1

run_experiment filetypes/powershell powershell_encoded_symbols \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=7000 EXP_SYMBOL_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1 COLLIMATOR_ATTACK_NGRAMS=1

run_experiment filetypes/powershell powershell_metadata_only \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=9000 EXP_TEXT_ENCODING_FEATURES=1

run_experiment filetypes/powershell powershell_scoreless_hsn8 \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=8000

run_experiment filetypes/powershell powershell_objective_attack_kv \
  EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1 \
  COLLIMATOR_ATTACK_NGRAMS=1 COLLIMATOR_TRIGRAM_MAX=3500

run_experiment filetypes/powershell powershell_tail_regularized \
  EXP_SYMBOL_VOCAB=1 EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.02 EXP_HARD_NEGATIVE_WEIGHT=18 \
  EXP_REG_ALPHA=0.35 EXP_REG_LAMBDA=3.0

run_experiment filetypes/powershell powershell_recall_beta2 \
  EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 EXP_BETA=2.0 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=6 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0

run_experiment filetypes/powershell powershell_low_leaf_precision \
  EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 EXP_NUM_LEAVES=48 \
  EXP_MIN_CHILD_SAMPLES=80 EXP_REG_ALPHA=0.5 EXP_REG_LAMBDA=4.0

# python
run_experiment filetypes/python python_kv_textenc_density \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=10000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_FORMAT_HINTS=1 EXP_HOSTILE_FINDING_DENSITY=1 EXP_HOSTILE_DEPTH_WEIGHT=1

run_experiment filetypes/python python_symbol_kv_density \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=12000 EXP_SYMBOL_MIN_FREQ=2 \
  EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 EXP_HOSTILE_FINDING_DENSITY=1 \
  EXP_HOSTILE_DEPTH_WEIGHT=1

run_experiment filetypes/python python_metadata_only \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=12000 EXP_TEXT_ENCODING_FEATURES=1

run_experiment filetypes/python python_scoreless_hsn10_textenc \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=10 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=14000

run_experiment filetypes/python python_objective_attack_symbols \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=12000 EXP_TEXT_ENCODING_FEATURES=1 \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1 COLLIMATOR_TRIGRAM_MAX=3500

run_experiment filetypes/python python_hardtail_kv \
  EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 EXP_HARD_NEGATIVE_FRACTION=0.01 \
  EXP_HARD_NEGATIVE_WEIGHT=14 EXP_NUM_LEAVES=160 EXP_MIN_CHILD_SAMPLES=70

run_experiment filetypes/python python_precision_regularized_kv \
  EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 EXP_NUM_LEAVES=64 \
  EXP_MIN_CHILD_SAMPLES=180 EXP_REG_ALPHA=0.5 EXP_REG_LAMBDA=4.0

run_experiment filetypes/python python_recall_beta2_symbols \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=12000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_BETA=2.0 EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0

# javascript
run_experiment filetypes/javascript javascript_objective_attack_symbols_kv \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=12000 EXP_KV_VOCAB=1 \
  EXP_TEXT_ENCODING_FEATURES=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1 \
  COLLIMATOR_ATTACK_NGRAMS=1 COLLIMATOR_TRIGRAM_MAX=4000

run_experiment filetypes/javascript javascript_kv_textenc_tail \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=10000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.01 EXP_HARD_NEGATIVE_WEIGHT=12 EXP_NUM_LEAVES=160

run_experiment filetypes/javascript javascript_metadata_only \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=12000 EXP_TEXT_ENCODING_FEATURES=1

run_experiment filetypes/javascript javascript_scoreless_hsn10_textenc \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=10 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=16000

run_experiment filetypes/javascript javascript_no_presence_objective \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,score,clusters EXP_TEXT_ENCODING_FEATURES=1 \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1 COLLIMATOR_TRIGRAM_MAX=4000

run_experiment filetypes/javascript javascript_precision_regularized \
  EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 EXP_NUM_LEAVES=64 \
  EXP_MIN_CHILD_SAMPLES=180 EXP_REG_ALPHA=0.5 EXP_REG_LAMBDA=4.0

run_experiment filetypes/javascript javascript_recall_beta2_hsn \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_BETA=2.0 EXP_TIERED_CRIT_TRIGRAMS=1 \
  EXP_TIERED_TRIGRAM_PATH_DEPTH=8 EXP_TIERED_TRIGRAM_MIN_CRIT=0

run_experiment filetypes/javascript javascript_symbol_only_stress \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_SYMBOL_VOCAB=1 \
  EXP_SYMBOL_VOCAB_MAX=16000 EXP_SYMBOL_MIN_FREQ=2 EXP_TEXT_ENCODING_FEATURES=1

# package.json
run_experiment filetypes/package.json package_json_lifecycle_kv_symbols \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=8000 EXP_KV_VOCAB=1 \
  EXP_KV_VOCAB_MAX=14000 EXP_KV_MIN_FREQ=1 EXP_TEXT_ENCODING_FEATURES=1 \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1

run_experiment filetypes/package.json package_json_metadata_reg \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=18000 EXP_KV_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_REG_ALPHA=0.25 EXP_REG_LAMBDA=2.5

run_experiment filetypes/package.json package_json_scoreless_hsn \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=8000

run_experiment filetypes/package.json package_json_tail_precision \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=14000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.015 EXP_HARD_NEGATIVE_WEIGHT=16 \
  EXP_NUM_LEAVES=64 EXP_MIN_CHILD_SAMPLES=120

run_experiment filetypes/package.json package_json_recall_beta2 \
  EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 EXP_BETA=2.0 \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1

run_experiment filetypes/package.json package_json_textenc_only \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TEXT_ENCODING_FEATURES=1 \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_TRIGRAM_MAX=2500

run_experiment filetypes/package.json package_json_kv_no_textenc \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=18000 EXP_KV_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=0 EXP_FORMAT_HINTS=1

run_experiment filetypes/package.json package_json_no_presence_kv \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,score,clusters EXP_KV_VOCAB=1 \
  EXP_KV_VOCAB_MAX=18000 EXP_TEXT_ENCODING_FEATURES=1

# html
run_experiment filetypes/html html_kv_textenc_objective \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=8000 EXP_TEXT_ENCODING_FEATURES=1 \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1 COLLIMATOR_TRIGRAM_MAX=3500

run_experiment filetypes/html html_symbol_script_surface \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=8000 EXP_SYMBOL_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1

run_experiment filetypes/html html_metadata_only \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=9000 EXP_TEXT_ENCODING_FEATURES=1

run_experiment filetypes/html html_scoreless_hsn8 \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=9000

run_experiment filetypes/html html_tail_low_child \
  EXP_SYMBOL_VOCAB=1 EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.02 EXP_HARD_NEGATIVE_WEIGHT=18 \
  EXP_MIN_CHILD_SAMPLES=30

run_experiment filetypes/html html_precision_regularized \
  EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 EXP_NUM_LEAVES=48 \
  EXP_MIN_CHILD_SAMPLES=80 EXP_REG_ALPHA=0.5 EXP_REG_LAMBDA=4.0

run_experiment filetypes/html html_recall_beta2 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_BETA=2.0 EXP_TIERED_CRIT_TRIGRAMS=1 \
  EXP_TIERED_TRIGRAM_PATH_DEPTH=8 EXP_TIERED_TRIGRAM_MIN_CRIT=0

run_experiment filetypes/html html_no_presence_script_surface \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,score,clusters EXP_SYMBOL_VOCAB=1 \
  EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1

# xml
run_experiment filetypes/xml xml_kv_textenc_reg \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=12000 EXP_KV_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_FORMAT_HINTS=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0 \
  EXP_REG_ALPHA=0.25 EXP_REG_LAMBDA=2.5

run_experiment filetypes/xml xml_metadata_only \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=16000 EXP_KV_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1

run_experiment filetypes/xml xml_scoreless_hsn8 \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=12000

run_experiment filetypes/xml xml_schema_symbols \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=10000 EXP_SYMBOL_MIN_FREQ=2 \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=12000 EXP_TEXT_ENCODING_FEATURES=1

run_experiment filetypes/xml xml_tail_precision \
  EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 EXP_HARD_NEGATIVE_FRACTION=0.01 \
  EXP_HARD_NEGATIVE_WEIGHT=12 EXP_NUM_LEAVES=64 EXP_MIN_CHILD_SAMPLES=180

run_experiment filetypes/xml xml_recall_beta2 \
  EXP_KV_VOCAB=1 EXP_TEXT_ENCODING_FEATURES=1 EXP_BETA=2.0 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0

run_experiment filetypes/xml xml_static_surface_no_traits \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=16000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_FORMAT_HINTS=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/xml xml_textenc_only_hsn \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=6 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0

echo
echo "azoth filetype night tranche complete: successes=${successes} failures=${#failures[@]} ran=${ran}"
if [[ "${#failures[@]}" -gt 0 ]]; then
  printf 'failed: %s\n' "${failures[@]}"
  exit 1
fi
