#!/usr/bin/env bash
set -euo pipefail

DB="${DB:-postgres://hopper@localhost:5432/hopper}"
OUT_DIR="${OUT_DIR:-out/screen}"
PYTHON="${PYTHON:-.venv/bin/python}"
WORKERS="${WORKERS:-1}"
SEED="${SEED:-42}"
TRAIN_SAMPLES="${TRAIN_SAMPLES:-10000}"
TEST_SAMPLES="${TEST_SAMPLES:-5000}"
ESTIMATORS="${ESTIMATORS:-80}"
MAX_DEPTH="${MAX_DEPTH:-8}"
LEARNING_RATE="${LEARNING_RATE:-0.05}"
EARLY_STOPPING="${EARLY_STOPPING:-20}"
BETA="${BETA:-2.0}"

mkdir -p "${OUT_DIR}/logs" "${OUT_DIR}/named-runs"

run_exp() {
  local name="$1"
  shift

  local log_path="${OUT_DIR}/logs/${name}.log"
  echo "== ${name} =="
  env "$@" \
    "${PYTHON}" -u -m collimator experiment \
      --db "${DB}" \
      --output "${OUT_DIR}" \
      --workers "${WORKERS}" \
      --seed "${SEED}" \
      --train-samples "${TRAIN_SAMPLES}" \
      --max-test-samples "${TEST_SAMPLES}" \
      --n-folds 2 \
      --n-estimators "${ESTIMATORS}" \
      --max-depth "${MAX_DEPTH}" \
      --learning-rate "${LEARNING_RATE}" \
      --early-stopping-rounds "${EARLY_STOPPING}" \
      --beta "${BETA}" | tee "${log_path}"

  local latest_json
  latest_json="$(ls -1t "${OUT_DIR}/runs"/*-experiment.json | head -1)"
  cp "${latest_json}" "${OUT_DIR}/named-runs/${name}.json"
}

run_selected() {
  local name="$1"
  case "${name}" in
    baseline)
      run_exp baseline
      ;;
    no_filetype)
      run_exp no_filetype COLLIMATOR_DISABLE_FEATURE_GROUPS=filetype
      ;;
    no_metrics)
      run_exp no_metrics COLLIMATOR_DISABLE_FEATURE_GROUPS=metrics
      ;;
    no_maxcrit)
      run_exp no_maxcrit COLLIMATOR_DISABLE_FEATURE_GROUPS=maxcrit
      ;;
    no_ext)
      run_exp no_ext COLLIMATOR_DISABLE_FEATURE_GROUPS=ext
      ;;
    top3_risk_files)
      run_exp top3_risk_files COLLIMATOR_TOP_K_RISK_FILES=3
      ;;
    struct_file_risk_coverage)
      run_exp struct_file_risk_coverage COLLIMATOR_STRUCT_FILE_RISK_COVERAGE=1
      ;;
    suspicious_breadth_density)
      run_exp suspicious_breadth_density COLLIMATOR_SUSPICIOUS_BREADTH_DENSITY=1
      ;;
    top3_breadth_density)
      run_exp top3_breadth_density COLLIMATOR_TOP_K_RISK_FILES=3 COLLIMATOR_SUSPICIOUS_BREADTH_DENSITY=1
      ;;
    hostile_escalation)
      run_exp hostile_escalation COLLIMATOR_HOSTILE_ESCALATION_FEATURES=1
      ;;
    breadth_hostile_escalation)
      run_exp breadth_hostile_escalation COLLIMATOR_SUSPICIOUS_BREADTH_DENSITY=1 COLLIMATOR_HOSTILE_ESCALATION_FEATURES=1
      ;;
    top3_breadth_hostile_escalation)
      run_exp top3_breadth_hostile_escalation COLLIMATOR_TOP_K_RISK_FILES=3 COLLIMATOR_SUSPICIOUS_BREADTH_DENSITY=1 COLLIMATOR_HOSTILE_ESCALATION_FEATURES=1
      ;;
    hostile_weighted_density)
      run_exp hostile_weighted_density COLLIMATOR_HOSTILE_ESCALATION_FEATURES=1 COLLIMATOR_HOSTILE_WEIGHTED_DENSITY=1
      ;;
    repetition_penalty)
      run_exp repetition_penalty COLLIMATOR_HOSTILE_ESCALATION_FEATURES=1 COLLIMATOR_REPETITION_PENALTY_FEATURES=1
      ;;
    file_severity_distribution)
      run_exp file_severity_distribution COLLIMATOR_HOSTILE_ESCALATION_FEATURES=1 COLLIMATOR_FILE_SEVERITY_DISTRIBUTION=1
      ;;
    hostile_combo)
      run_exp hostile_combo COLLIMATOR_HOSTILE_ESCALATION_FEATURES=1 COLLIMATOR_HOSTILE_WEIGHTED_DENSITY=1 COLLIMATOR_REPETITION_PENALTY_FEATURES=1 COLLIMATOR_FILE_SEVERITY_DISTRIBUTION=1
      ;;
    logic_gaps)
      run_exp logic_gaps COLLIMATOR_ALLOWED_FEATURES_FILE=""
      ;;
    signature_synergy)
      run_exp signature_synergy COLLIMATOR_ALLOWED_FEATURES_FILE=""
      ;;
    silent_packer)
      run_exp silent_packer COLLIMATOR_SILENT_PACKER_SIGNAL=1 COLLIMATOR_ALLOWED_FEATURES_FILE=""
      ;;
    temporal_frankenstein)
      run_exp temporal_frankenstein COLLIMATOR_MTIME_KURTOSIS=1 COLLIMATOR_ALLOWED_FEATURES_FILE=""
      ;;
    neg_space)
      run_exp neg_space COLLIMATOR_DISABLE_FEATURE_GROUPS="" COLLIMATOR_ALLOWED_FEATURES_FILE=""
      ;;
    crazy_combo)
      run_exp crazy_combo COLLIMATOR_SILENT_PACKER_SIGNAL=1 COLLIMATOR_MTIME_KURTOSIS=1 COLLIMATOR_DISABLE_FEATURE_GROUPS="" COLLIMATOR_ALLOWED_FEATURES_FILE=""
      ;;
    crazy_combo_v3)
      run_exp crazy_combo_v3 COLLIMATOR_SILENT_PACKER_SIGNAL=1 COLLIMATOR_MTIME_KURTOSIS=1 COLLIMATOR_AIR_GAP_SIGNAL=1 COLLIMATOR_DISABLE_FEATURE_GROUPS="" COLLIMATOR_ALLOWED_FEATURES_FILE=""
      ;;
    *)
      echo "unknown experiment: ${name}" >&2
      exit 1
      ;;
  esac
}

if [[ "$#" -eq 0 ]]; then
  set -- baseline no_filetype no_metrics no_maxcrit no_ext top3_risk_files struct_file_risk_coverage suspicious_breadth_density top3_breadth_density hostile_escalation breadth_hostile_escalation top3_breadth_hostile_escalation hostile_weighted_density repetition_penalty file_severity_distribution hostile_combo
fi

for name in "$@"; do
  run_selected "${name}"
done
