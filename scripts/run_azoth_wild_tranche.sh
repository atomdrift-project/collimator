#!/usr/bin/env bash
set -uo pipefail

# Wild Azoth experiment tranche.
# Serial on purpose: each run uses LightGBM, Postgres-backed corpus selection, and
# sparse matrix caches. Parallel tranches reduce throughput on this box.

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
  EXP_TRAIN_SAMPLES="${EXP_TRAIN_SAMPLES:-120000}"
  EXP_MAX_TEST_SAMPLES="${EXP_MAX_TEST_SAMPLES:-30000}"
  EXP_FOLDS="${EXP_FOLDS:-0}"
  EXP_HOLDOUT_FRACTION="${EXP_HOLDOUT_FRACTION:-0.12}"
  EXP_ESTIMATORS="${EXP_ESTIMATORS:-150}"
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
    general)
      [[ -z "${EXP_TRAIN_SAMPLES:-}" ]] && profile_overrides+=(EXP_TRAIN_SAMPLES=100000)
      [[ -z "${EXP_MAX_TEST_SAMPLES:-}" ]] && profile_overrides+=(EXP_MAX_TEST_SAMPLES=30000)
      [[ -z "${EXP_ESTIMATORS:-}" ]] && profile_overrides+=(EXP_ESTIMATORS=140)
      ;;
    filetypes/pe|filegroups/native)
      [[ -z "${EXP_TRAIN_SAMPLES:-}" ]] && profile_overrides+=(EXP_TRAIN_SAMPLES=90000)
      [[ -z "${EXP_MAX_TEST_SAMPLES:-}" ]] && profile_overrides+=(EXP_MAX_TEST_SAMPLES=25000)
      [[ -z "${EXP_ESTIMATORS:-}" ]] && profile_overrides+=(EXP_ESTIMATORS=130)
      ;;
    filetypes/javascript|filetypes/c|filetypes/xml|filegroups/source|filegroups/scripts)
      [[ -z "${EXP_TRAIN_SAMPLES:-}" ]] && profile_overrides+=(EXP_TRAIN_SAMPLES=110000)
      [[ -z "${EXP_MAX_TEST_SAMPLES:-}" ]] && profile_overrides+=(EXP_MAX_TEST_SAMPLES=30000)
      [[ -z "${EXP_ESTIMATORS:-}" ]] && profile_overrides+=(EXP_ESTIMATORS=150)
      ;;
    filetypes/applescript|filetypes/powershell|filetypes/rtf|filetypes/macho)
      [[ -z "${EXP_ESTIMATORS:-}" ]] && profile_overrides+=(EXP_ESTIMATORS=120)
      [[ -z "${EXP_MIN_CHILD_SAMPLES:-}" ]] && profile_overrides+=(EXP_MIN_CHILD_SAMPLES=40)
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

echo "azoth wild tranche started: ${started_at}"
echo "workers=${EXP_WORKERS:-64} train_samples=${EXP_TRAIN_SAMPLES:-120000} max_test_samples=${EXP_MAX_TEST_SAMPLES:-30000} skip=${skip} limit=${limit}"

run_experiment general general_scoreless_symbol_kv_textenc \
  EXP_MIN_SAMPLE_SCORE=0 EXP_DISABLE_FEATURE_GROUPS=score,clusters \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=8000 EXP_SYMBOL_MIN_FREQ=3 \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=5000 EXP_KV_MIN_FREQ=3 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1

run_experiment filegroups/documents documents_textenc_kv_static \
  EXP_SYMBOL_VOCAB=0 EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=8000 EXP_KV_MIN_FREQ=2 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 \
  EXP_EMBER_LITE_FEATURES=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filegroups/documents documents_scoreless_textenc_deep_paths \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=12000 \
  EXP_TIERED_TRIGRAM_MIN_FREQ=1

run_experiment filetypes/pdf pdf_textenc_kv_deep_paths \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=6000 EXP_KV_MIN_FREQ=2 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_TIERED_CRIT_TRIGRAMS=1 \
  EXP_TIERED_TRIGRAM_PATH_DEPTH=8 EXP_TIERED_TRIGRAM_MIN_CRIT=0 \
  EXP_TIERED_TRIGRAM_MAX=8000

run_experiment filetypes/docx docx_kv_textenc_package_surface \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=7000 EXP_KV_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 \
  EXP_EMBER_LITE_FEATURES=1

run_experiment filetypes/rtf rtf_escape_textenc_hsn \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_DISABLE_FEATURE_GROUPS=score,clusters \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=6000

run_experiment filetypes/html html_script_url_textenc_symbols \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=6000 EXP_SYMBOL_MIN_FREQ=2 \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=4000 EXP_TEXT_ENCODING_FEATURES=1 \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=6

run_experiment filetypes/xml xml_kv_schema_textenc \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=8000 EXP_KV_MIN_FREQ=2 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 \
  COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filegroups/media media_textenc_kv_carrier \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=7000 EXP_KV_MIN_FREQ=2 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 \
  COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/png png_kv_chunk_textenc \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=8000 EXP_KV_MIN_FREQ=2 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_FORMAT_HINTS=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/jpeg jpeg_exif_kv_textenc \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=8000 EXP_KV_MIN_FREQ=2 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_FORMAT_HINTS=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filegroups/media media_metadata_only_no_traits \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=10000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/applescript applescript_tiny_textenc_symbols \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=3000 EXP_SYMBOL_MIN_FREQ=1 \
  EXP_KV_VOCAB=1 EXP_KV_MIN_FREQ=1 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_MIN_CHILD_SAMPLES=20

run_experiment filetypes/batch batch_cmd_symbol_textenc \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=5000 EXP_SYMBOL_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_KV_VOCAB=1 EXP_FORMAT_HINTS=1 \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1

run_experiment filetypes/batch batch_scoreless_deep_shell_paths \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=7000

run_experiment filetypes/shell shell_command_textenc_symbols \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=8000 EXP_SYMBOL_MIN_FREQ=2 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_KV_VOCAB=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1 \
  COLLIMATOR_ATTACK_NGRAMS=1

run_experiment filetypes/shell shell_kv_metric_vocab_wide \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=12000 EXP_KV_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_FORMAT_HINTS=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/shell shell_no_presence_command_surface \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,score,clusters \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=8000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_FORMAT_HINTS=1

run_experiment filetypes/powershell powershell_encoded_command_textenc \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=5000 EXP_SYMBOL_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_DISABLE_FEATURE_GROUPS=score,clusters \
  COLLIMATOR_ATTACK_NGRAMS=1

run_experiment filetypes/powershell powershell_kv_symbols_tail \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=6000 EXP_SYMBOL_MIN_FREQ=1 \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=5000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.02 EXP_HARD_NEGATIVE_WEIGHT=18

run_experiment filegroups/scripts scripts_symbol_kv_textenc_combo \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=12000 EXP_SYMBOL_MIN_FREQ=2 \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=8000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters COLLIMATOR_OBJECTIVE_TRIGRAMS=1 \
  COLLIMATOR_ATTACK_NGRAMS=1

run_experiment filegroups/scripts scripts_no_trait_command_surface \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=12000 EXP_KV_VOCAB=1 \
  EXP_KV_VOCAB_MAX=8000 EXP_TEXT_ENCODING_FEATURES=1

run_experiment filetypes/c c_symbol_static_kv \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=12000 EXP_SYMBOL_MIN_FREQ=2 \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=7000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_EMBER_LITE_FEATURES=1

run_experiment filetypes/c c_no_score_symbols_only \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_SYMBOL_VOCAB=1 \
  EXP_SYMBOL_VOCAB_MAX=16000 EXP_SYMBOL_MIN_FREQ=2 EXP_TEXT_ENCODING_FEATURES=0

run_experiment filetypes/go go_import_symbol_kv \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=12000 EXP_SYMBOL_MIN_FREQ=2 \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=7000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1

run_experiment filetypes/go go_static_textenc_scoreless \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=6000 EXP_TIERED_CRIT_TRIGRAMS=1 \
  EXP_TIERED_TRIGRAM_PATH_DEPTH=6 EXP_TIERED_TRIGRAM_MIN_CRIT=0

run_experiment filetypes/rust rust_crate_symbol_kv \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=10000 EXP_SYMBOL_MIN_FREQ=1 \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=7000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_FORMAT_HINTS=1 EXP_MIN_CHILD_SAMPLES=30

run_experiment filetypes/rust rust_sparse_bad_tail \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=10000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.03 EXP_HARD_NEGATIVE_WEIGHT=24 \
  EXP_NUM_LEAVES=48 EXP_MIN_CHILD_SAMPLES=20

run_experiment filegroups/source source_symbol_kv_textenc_combo \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=16000 EXP_SYMBOL_MIN_FREQ=2 \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=9000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_HOSTILE_FINDING_DENSITY=1 EXP_HOSTILE_DEPTH_WEIGHT=1 \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1

run_experiment filegroups/source source_static_surface_no_traits \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=16000 EXP_KV_VOCAB=1 \
  EXP_KV_VOCAB_MAX=9000 EXP_TEXT_ENCODING_FEATURES=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/package.json package_json_kv_lifecycle_textenc \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=6000 EXP_KV_VOCAB=1 \
  EXP_KV_VOCAB_MAX=12000 EXP_KV_MIN_FREQ=1 EXP_TEXT_ENCODING_FEATURES=1 \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1

run_experiment filetypes/package.json package_json_metadata_only \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=16000 EXP_KV_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_FORMAT_HINTS=1

run_experiment filetypes/pkg-info pkg_info_kv_textenc_supply_chain \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=12000 EXP_KV_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1 EXP_TAXONOMY_FEATURES=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1

run_experiment filetypes/pkg-info pkg_info_scoreless_metadata_only \
  EXP_DISABLE_FEATURE_GROUPS=present,maxcrit,elements,bigrams,trigrams,score,clusters \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=16000 EXP_KV_MIN_FREQ=1 \
  EXP_TEXT_ENCODING_FEATURES=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/elf elf_symbol_vocab_kv_static \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=16000 EXP_SYMBOL_MIN_FREQ=2 \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=8000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_EMBER_LITE_FEATURES=1

run_experiment filetypes/elf elf_no_score_symbols_textenc \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_SYMBOL_VOCAB=1 \
  EXP_SYMBOL_VOCAB_MAX=18000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=8 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0

run_experiment filetypes/macho macho_symbol_kv_textenc \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=12000 EXP_SYMBOL_MIN_FREQ=1 \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=8000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.015 EXP_HARD_NEGATIVE_WEIGHT=20

run_experiment filetypes/pe pe_symbol_kv_import_surface \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_SYMBOL_VOCAB=1 \
  EXP_SYMBOL_VOCAB_MAX=18000 EXP_SYMBOL_MIN_FREQ=3 EXP_KV_VOCAB=1 \
  EXP_KV_VOCAB_MAX=10000 EXP_TEXT_ENCODING_FEATURES=1

run_experiment filetypes/pe pe_textenc_kv_static_regularized \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=12000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_EMBER_LITE_FEATURES=1 \
  EXP_REG_ALPHA=0.35 EXP_REG_LAMBDA=3.0 EXP_COLSAMPLE_BYTREE=0.7

run_experiment filegroups/native native_symbol_kv_textenc_combo \
  EXP_SYMBOL_VOCAB=1 EXP_SYMBOL_VOCAB_MAX=18000 EXP_SYMBOL_MIN_FREQ=3 \
  EXP_KV_VOCAB=1 EXP_KV_VOCAB_MAX=10000 EXP_TEXT_ENCODING_FEATURES=1 \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_EMBER_LITE_FEATURES=1 \
  EXP_HARD_NEGATIVE_FRACTION=0.008 EXP_HARD_NEGATIVE_WEIGHT=14

echo
echo "azoth wild tranche complete: successes=${successes} failures=${#failures[@]} ran=${ran}"
if [[ "${#failures[@]}" -gt 0 ]]; then
  printf 'failed: %s\n' "${failures[@]}"
  exit 1
fi
