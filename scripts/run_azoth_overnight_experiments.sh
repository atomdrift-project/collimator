#!/usr/bin/env bash
set -uo pipefail

# Wild azoth tranche for overnight runs.
#
# The script is intentionally serial. Each call uses make experiment's
# content-addressed run key, so exact duplicates are skipped unless EXP_RERUN=1.
# Failures are recorded and the remaining experiments still run.

started_at="$(date -Is)"
failures=()
successes=0
skips_or_successes=0

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

  local min_score=3
  if [[ "${route}" == filegroups/* || "${route}" == filetypes/* ]]; then
    min_score=0
  fi

  echo
  echo "================================================================"
  echo "route=${route} idea=${idea} min_sample_score=${min_score}"
  echo "================================================================"

  if make experiment \
    "${common[@]}" \
    EXP_ROUTE="${route}" \
    EXP_IDEA="${idea}" \
    EXP_TAG="_${idea}" \
    EXP_MIN_SAMPLE_SCORE="${min_score}" \
    "$@"; then
    successes=$((successes + 1))
    skips_or_successes=$((skips_or_successes + 1))
  else
    failures+=("${route}:${idea}")
  fi
}

echo "azoth overnight tranche started: ${started_at}"
echo "workers=${EXP_WORKERS:-64} train_samples=${EXP_TRAIN_SAMPLES:-150000} max_test_samples=${EXP_MAX_TEST_SAMPLES:-40000}"

# General: broad feature and objective probes.
run_experiment general general_kv_format_taxonomy \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 EXP_EMBER_LITE_FEATURES=1

run_experiment general general_metrics_kv_dense \
  EXP_FORMAT_HINTS=1 EXP_EXTENDED_METRICS=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment general general_full_ngram_vocab \
  COLLIMATOR_BIGRAM_MAX=12000 COLLIMATOR_BIGRAM_MIN_FREQ=250 \
  COLLIMATOR_TRIGRAM_MAX=2000 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.005

run_experiment general general_tiered_deep_tri \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=5 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=2 EXP_TIERED_TRIGRAM_MAX=12000 \
  EXP_TIERED_TRIGRAM_MIN_FREQ=3

run_experiment general general_precision_hn_pe_js \
  EXP_HARD_NEGATIVE_FRACTION=0.006 EXP_HARD_NEGATIVE_WEIGHT=12 \
  EXP_BENIGN_FILETYPE_WEIGHT="pe=4 javascript=3 python=3 elf=3 macho=4"

run_experiment general general_smooth_large \
  EXP_LEARNING_RATE=0.025 EXP_ESTIMATORS=900 EXP_EARLY_STOPPING=80 \
  EXP_NUM_LEAVES=192 EXP_MIN_CHILD_SAMPLES=60 EXP_REG_LAMBDA=2

run_experiment general general_clusters_back_on \
  EXP_DISABLE_FEATURE_GROUPS= EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1

# Native and hard binary routes.
run_experiment filegroups/native native_kv_cross_binary \
  EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 EXP_TAXONOMY_FEATURES=1 \
  COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filegroups/native native_big_vocab_tail \
  COLLIMATOR_BIGRAM_MAX=15000 COLLIMATOR_BIGRAM_MIN_FREQ=200 \
  COLLIMATOR_TRIGRAM_MAX=2500 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.004 \
  EXP_HARD_NEGATIVE_FRACTION=0.006 EXP_HARD_NEGATIVE_WEIGHT=12

run_experiment filetypes/pe pe_kv_ember_format \
  EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 EXP_TAXONOMY_FEATURES=1

run_experiment filetypes/pe pe_metrics_all_kv \
  EXP_FORMAT_HINTS=1 EXP_EXTENDED_METRICS=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0 \
  EXP_FILETYPE_INTERACTIONS=1

run_experiment filetypes/pe pe_hardtail_precision \
  EXP_HARD_NEGATIVE_FRACTION=0.01 EXP_HARD_NEGATIVE_WEIGHT=16 \
  EXP_LEARNING_RATE=0.03 EXP_ESTIMATORS=700 EXP_EARLY_STOPPING=70

run_experiment filetypes/pe pe_no_score_features \
  EXP_DISABLE_FEATURE_GROUPS=score,clusters EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1

run_experiment filetypes/macho macho_kv_format_metrics \
  EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/macho macho_tail_contrast_like \
  EXP_HARD_NEGATIVE_FRACTION=0.015 EXP_HARD_NEGATIVE_WEIGHT=20 \
  EXP_NUM_LEAVES=160 EXP_MIN_CHILD_SAMPLES=40

run_experiment filetypes/elf elf_deeper_notable_vocab \
  EXP_NGRAM_PATH_DEPTH=8 EXP_NGRAM_MIN_CRIT=3 COLLIMATOR_BIGRAM_MAX=18000 \
  COLLIMATOR_BIGRAM_MIN_FREQ=80 COLLIMATOR_TRIGRAM_MAX=4000

run_experiment filetypes/elf elf_no_formula_elements_ablation \
  EXP_DISABLE_FEATURE_GROUPS=formula,elements,clusters EXP_FORMAT_HINTS=1

# Scripts and source routes.
run_experiment filegroups/scripts scripts_deep_hsn \
  EXP_TIERED_CRIT_TRIGRAMS=1 EXP_TIERED_TRIGRAM_PATH_DEPTH=6 \
  EXP_TIERED_TRIGRAM_MIN_CRIT=0 EXP_TIERED_TRIGRAM_MAX=15000 \
  EXP_TIERED_TRIGRAM_MIN_FREQ=2

run_experiment filegroups/scripts scripts_tail_hardneg \
  EXP_HARD_NEGATIVE_FRACTION=0.012 EXP_HARD_NEGATIVE_WEIGHT=18 \
  EXP_NUM_LEAVES=192 EXP_MIN_CHILD_SAMPLES=40 EXP_LEARNING_RATE=0.03 \
  EXP_ESTIMATORS=750

run_experiment filegroups/scripts scripts_kv_objective_attack \
  EXP_FORMAT_HINTS=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1 \
  COLLIMATOR_TRIGRAM_MAX=4000

run_experiment filegroups/scripts scripts_no_density_ablation \
  EXP_HOSTILE_WEIGHTED_DENSITY=0 EXP_SUSPICIOUS_BREADTH_DENSITY=0 \
  EXP_HOSTILE_ESCALATION_FEATURES=1

run_experiment filetypes/javascript javascript_objective_deep \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_SUSPICIOUS_TRIGRAMS=1 \
  COLLIMATOR_TRIGRAM_MAX=3000 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.003

run_experiment filetypes/javascript javascript_kv_metrics_tail \
  EXP_FORMAT_HINTS=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0 \
  EXP_HARD_NEGATIVE_FRACTION=0.008 EXP_HARD_NEGATIVE_WEIGHT=12

run_experiment filetypes/javascript javascript_path_depth5_allcrit \
  EXP_NGRAM_PATH_DEPTH=5 EXP_NGRAM_MIN_CRIT=0 COLLIMATOR_BIGRAM_MAX=12000 \
  COLLIMATOR_BIGRAM_MIN_FREQ=100

run_experiment filetypes/javascript javascript_no_score_soft_presence \
  EXP_SCORE_WEIGHTED_TRAITS=0 EXP_SOFT_PRESENCE=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1

run_experiment filetypes/python python_objective_attack \
  COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1 \
  COLLIMATOR_TRIGRAM_MAX=2500 COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.004

run_experiment filetypes/python python_kv_density \
  EXP_FORMAT_HINTS=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0 \
  EXP_HOSTILE_FINDING_DENSITY=1 EXP_HOSTILE_DEPTH_WEIGHT=1

run_experiment filetypes/python python_path_depth8_allcrit \
  EXP_NGRAM_PATH_DEPTH=8 EXP_NGRAM_MIN_CRIT=0 COLLIMATOR_BIGRAM_MAX=12000 \
  COLLIMATOR_BIGRAM_MIN_FREQ=80 COLLIMATOR_TRIGRAM_MAX=3000

run_experiment filegroups/source source_semantic_metrics \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1 \
  COLLIMATOR_TRIGRAM_MAX=2000

run_experiment filegroups/source source_formula_elements_dense \
  EXP_FORMAT_HINTS=1 EXP_EXTENDED_METRICS=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0 \
  EXP_TAXONOMY_FEATURES=1

# Package, archive, config, and document routes.
run_experiment filegroups/archive archive_kv_manifest \
  EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 EXP_TAXONOMY_FEATURES=1 \
  COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filegroups/archive archive_deep_inner_paths \
  EXP_NGRAM_PATH_DEPTH=7 EXP_NGRAM_MIN_CRIT=0 COLLIMATOR_BIGRAM_MAX=14000 \
  COLLIMATOR_BIGRAM_MIN_FREQ=90 EXP_FORMAT_HINTS=1

run_experiment filetypes/zip zip_archive_deep_paths \
  EXP_NGRAM_PATH_DEPTH=6 EXP_NGRAM_MIN_CRIT=0 COLLIMATOR_BIGRAM_MAX=10000 \
  COLLIMATOR_BIGRAM_MIN_FREQ=80

run_experiment filetypes/jar jar_portable_kv_bytecode \
  EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0 \
  EXP_TAXONOMY_FEATURES=1

run_experiment filegroups/portable portable_bytecode_ngram \
  EXP_FORMAT_HINTS=1 EXP_TAXONOMY_FEATURES=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1 \
  COLLIMATOR_BIGRAM_MAX=10000 COLLIMATOR_TRIGRAM_MAX=2500

run_experiment filetypes/package.json package_json_kv_fields \
  EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 EXP_EXTENDED_METRICS=1 \
  COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/pkg-info pkg_info_kv_metadata \
  EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 EXP_TAXONOMY_FEATURES=1 \
  COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filegroups/config config_kv_schema \
  EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 EXP_TAXONOMY_FEATURES=1 \
  COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/json json_config_depth6 \
  EXP_NGRAM_PATH_DEPTH=6 EXP_NGRAM_MIN_CRIT=0 EXP_FORMAT_HINTS=1 \
  COLLIMATOR_BIGRAM_MAX=9000 COLLIMATOR_BIGRAM_MIN_FREQ=60

run_experiment filegroups/documents documents_kv_macro_like \
  EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 EXP_TAXONOMY_FEATURES=1 \
  COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/pdf pdf_doc_kv_entropy \
  EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0 \
  EXP_EXTENDED_METRICS=1

run_experiment filetypes/ole ole_documents_kv \
  EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 EXP_TAXONOMY_FEATURES=1 \
  COLLIMATOR_METRIC_MIN_FREQ_PCT=0

run_experiment filetypes/html html_script_document_hybrid \
  EXP_FORMAT_HINTS=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1 \
  COLLIMATOR_TRIGRAM_MAX=3000

# Small or odd routes: negative-space and high-risk probes.
run_experiment filegroups/media media_negative_space \
  EXP_FORMAT_HINTS=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0 \
  EXP_DISABLE_FEATURE_GROUPS=clusters EXP_HOSTILE_FINDING_DENSITY=1 \
  EXP_HOSTILE_DEPTH_WEIGHT=1

run_experiment filetypes/svg svg_script_media_hybrid \
  EXP_FORMAT_HINTS=1 COLLIMATOR_OBJECTIVE_TRIGRAMS=1 COLLIMATOR_ATTACK_NGRAMS=1 \
  COLLIMATOR_TRIGRAM_MAX=2500

run_experiment filetypes/apk apk_archive_portable_hybrid \
  EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 EXP_TAXONOMY_FEATURES=1 \
  COLLIMATOR_BIGRAM_MAX=10000 COLLIMATOR_TRIGRAM_MAX=2000

run_experiment filetypes/msi msi_native_archive_hybrid \
  EXP_FORMAT_HINTS=1 EXP_EMBER_LITE_FEATURES=1 COLLIMATOR_METRIC_MIN_FREQ_PCT=0 \
  EXP_HARD_NEGATIVE_FRACTION=0.01 EXP_HARD_NEGATIVE_WEIGHT=14

run_experiment filetypes/shell shell_depth8_attack \
  EXP_NGRAM_PATH_DEPTH=8 EXP_NGRAM_MIN_CRIT=0 COLLIMATOR_ATTACK_NGRAMS=1 \
  COLLIMATOR_BIGRAM_MAX=9000 COLLIMATOR_TRIGRAM_MAX=2000

finished_at="$(date -Is)"
echo
echo "azoth overnight tranche finished: ${finished_at}"
echo "successful or skipped runs: ${skips_or_successes}"
if ((${#failures[@]})); then
  echo "failed runs:"
  printf '  %s\n' "${failures[@]}"
  exit 1
fi
echo "all experiments completed"
