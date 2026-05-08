SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c

# `_comma` lets us pass a literal comma into $(subst) where the function-call
# syntax would otherwise interpret it as an argument separator. Used to convert
# autocollie's csv-joined env values (e.g. `pe=0.5,zip=2.0`) back into the
# space-separated form make's $(foreach) expects.
_comma := ,
.PHONY: azoth-train evaluate explain inspect errors scan traits thresholds thresholds-refresh filetype-matrix elf-model-benchmark elf-route-optimization azoth-specialists azoth-calibrate azoth-diagnostics azoth-policies azoth-deploy false-positives false-negatives near-false-positives near-false-negatives false-positives-archive false-negatives-archive near-false-positives-archive near-false-negatives-archive false-positives-triage near-false-positives-triage benchmark build-splits experiment ablate ablation demo-db test lint clean deploy verify-xgboost-ars verify-litmus venv help fixture

VENV_DIR ?= .venv
PYTHON ?= $(VENV_DIR)/bin/python
DB ?= postgres://hopper@localhost:5432/hopper
MODEL ?= azoth
LEARNER ?= $(if $(filter azoth%,$(MODEL)),azoth,$(MODEL))
OUT_ROOT ?= out/models
OUT_DIR ?= $(if $(filter azoth,$(MODEL)),$(OUT_ROOT)/azoth/general,$(OUT_ROOT)/$(MODEL))
MODEL_FILE ?= $(if $(filter azoth,$(LEARNER)),model.txt,model.json)
LOG_DIR ?= $(OUT_DIR)/logs
EXP_OUT_DIR ?= out/experiments/$(MODEL)
EXP_LOG_DIR ?= $(EXP_OUT_DIR)/logs
THRESHOLD_SCORES ?= $(OUT_DIR)/threshold_scores.npz
THRESHOLD_MAX_ID ?=
THRESHOLD_MAX_ID_ARG := $(if $(THRESHOLD_MAX_ID),--max-id $(THRESHOLD_MAX_ID),)
TOP_ERRORS ?= 100
THRESHOLD_TOP_ERRORS ?= 0
FILETYPE_MATRIX_OUTPUT ?= $(OUT_DIR)/filetype_metrics.json
FILETYPE_MATRIX_CSV ?= $(OUT_DIR)/filetype_metrics.csv
FILETYPE_MATRIX_MIN_COUNT ?= 25
ELF_BENCHMARK_OUTPUT ?= $(OUT_ROOT)/elf_model_benchmark.json
ELF_BENCHMARK_GENERAL_DIR ?= $(OUT_ROOT)/azoth/general
ELF_BENCHMARK_BINARY_DIR ?= $(OUT_ROOT)/azoth-binary-cpu
ELF_BENCHMARK_ELF_DIR ?= $(OUT_ROOT)/azoth-elf-cpu
ELF_BENCHMARK_FOLDS ?= 2
ELF_BENCHMARK_ESTIMATORS ?= 400
ELF_BENCHMARK_MAX_DEPTH ?= 12
ELF_BENCHMARK_LEARNING_RATE ?= 0.05
ELF_BENCHMARK_EARLY_STOPPING ?= 50
ELF_BENCHMARK_NUM_LEAVES ?= 96
ELF_BENCHMARK_MIN_CHILD_SAMPLES ?= 100
AZOTH_ROOT ?= $(OUT_ROOT)/azoth
AZOTH_SPECIALISTS_SUMMARY ?= $(AZOTH_ROOT)/specialists.json
AZOTH_GENERAL_DIR ?= $(AZOTH_ROOT)/general
AZOTH_GENERAL_SCORES ?= $(AZOTH_GENERAL_DIR)/threshold_scores.npz
AZOTH_CONFIG ?= $(AZOTH_ROOT)/config.json
AZOTH_SCORE_TABLE ?= $(AZOTH_ROOT)/score_table.npz
AZOTH_DIAGNOSTICS ?= $(AZOTH_ROOT)/route_diagnostics.md
AZOTH_DIAGNOSTICS_CSV ?= $(AZOTH_ROOT)/route_diagnostics.csv
AZOTH_SLICE_METRICS ?= $(AZOTH_ROOT)/slice_metrics.md
AZOTH_SLICE_METRICS_CSV ?= $(AZOTH_ROOT)/slice_metrics.csv
AZOTH_ROUTE_POLICIES ?= $(AZOTH_ROOT)/route_policies.json
AZOTH_ROUTE_POLICIES_CSV ?= $(AZOTH_ROOT)/route_policies.csv
AZOTH_ROUTE_POLICIES_MD ?= $(AZOTH_ROOT)/route_policies.md
AZOTH_GLOBAL_POLICY_METRICS ?= $(AZOTH_ROOT)/global_policy_metrics.json
AZOTH_GLOBAL_POLICY_METRICS_MD ?= $(AZOTH_ROOT)/global_policy_metrics.md
AZOTH_POLICY_OVERRIDE_ROUTE ?=
AZOTH_DEPLOY_DIR ?= $(XDG_DATA_HOME)/litmus/models/azoth
ELF_ROUTE_OUTPUT_DIR ?= $(AZOTH_ROOT)/elf_route_optimization
ELF_ROUTE_OUTPUT ?= $(AZOTH_ROOT)/elf_route_optimization.json
ELF_ROUTE_TEACHER_DIR ?= $(AZOTH_ROOT)/filetypes/elf
AZOTH_REFRESH_SCORES ?= 0
AZOTH_REFRESH_SCORES_ARG := $(if $(filter 1 true yes,$(AZOTH_REFRESH_SCORES)),--refresh,)
AZOTH_REFRESH_ROUTE ?=
AZOTH_SKIP_LEVEL_CALIBRATION ?= 0
AZOTH_SKIP_LEVEL_CALIBRATION_ARG := $(if $(filter 1 true yes,$(AZOTH_SKIP_LEVEL_CALIBRATION)),--skip-level-calibration,)
AZOTH_FEATURE_CACHE_DIR ?= $(OUT_DIR)/cache/azoth-route-features
AZOTH_SPECIALIST_FOLDS ?= 0
AZOTH_SPECIALIST_ESTIMATORS ?= 400
AZOTH_SPECIALIST_MAX_DEPTH ?= 12
AZOTH_SPECIALIST_LEARNING_RATE ?= 0.05
AZOTH_SPECIALIST_EARLY_STOPPING ?= 50
AZOTH_SPECIALIST_NUM_LEAVES ?= 96
AZOTH_SPECIALIST_MIN_CHILD_SAMPLES ?= 100
AZOTH_SPECIALIST_MIN_BAD ?= 50
AZOTH_SPECIALIST_MIN_GOOD ?= 50
# Multi-seed averaging (item A): K extra seeds trained against the same matrix.
# Default 2 → 3 trained seeds, averaged at predict time. Reduces seed-driven
# prediction variance by ~3× at 3× training cost; matrix extraction (the
# slow part) is shared across seeds. K=2 is the sweet spot — most independent
# variance is captured in the first 3 samples; K>2 hits diminishing returns
# because tree boosters share enough hyperparam-driven structure that the
# noise terms don't actually decorrelate to zero. Setting K=0 reverts to the
# legacy single-model layout (model.txt) — useful for debugging, since
# averaged bundles smear blame across members when something regresses.
AZOTH_SPECIALIST_N_SEED_EXTRAS ?= 2
AZOTH_SPECIALIST_ONLY ?=
AZOTH_SPECIALIST_MASK_SPEC ?=
AZOTH_SPECIALIST_TRAIN_OVERRIDE ?= pe:hard_negative_fraction=0.01 pe:hard_negative_weight=12.0
AZOTH_SPECIALIST_FEATURE_ENV ?= native:COLLIMATOR_FORMAT_HINTS=1 native:COLLIMATOR_TAXONOMY_FEATURES=1 native:COLLIMATOR_EMBER_LITE_FEATURES=1
# Where autocollie-driven experiments write run JSONs. Pointing the suite at
# this dir lets it auto-pick each route's highest-F1 historical experiment
# and replay its train_config + feature_env, so `make azoth-specialist-suite`
# uses autocollie's wins by default. Unset to revert to pure CLI/Makefile
# defaults (legacy behavior, autocollie discoveries are dropped on the floor).
AZOTH_AUTOCOLLIE_RUNS_DIR ?= out/experiments/azoth/runs
AZOTH_SPECIALIST_SKIP_EXISTING ?= 1
AZOTH_SPECIALIST_SKIP_EXISTING_ARG := $(if $(filter 1 true yes,$(AZOTH_SPECIALIST_SKIP_EXISTING)),--skip-existing,)
AZOTH_FILEGROUP_SCORE_FILTER ?= 0
AZOTH_FILEGROUP_SCORE_FILTER_ARG := $(if $(filter 1 true yes,$(AZOTH_FILEGROUP_SCORE_FILTER)),--filegroup-score-filter,)
SAMPLES_DIR ?= /data/samples
FALSE_POSITIVES_ARCHIVE ?= /tmp/false-positives.tgz
FALSE_NEGATIVES_ARCHIVE ?= /tmp/false-negatives.tgz
NEAR_FALSE_POSITIVES_ARCHIVE ?= /tmp/near-false-positives.tgz
NEAR_FALSE_NEGATIVES_ARCHIVE ?= /tmp/near-false-negatives.tgz
FALSE_POSITIVES_TRIAGE_DIR ?= /tmp/false-positives
NEAR_FALSE_POSITIVES_TRIAGE_DIR ?= /tmp/near-false-positives
FALSE_POSITIVES_TRIAGE_JSON ?= /tmp/false-positives.json
NEAR_FALSE_POSITIVES_TRIAGE_JSON ?= /tmp/near-false-positives.json
SAMPLE ?=
FILE ?=
CLEAVE ?= cleave
DEMO_DB ?= out/demo.db
WORKERS ?=
EXP_WORKERS ?= $(WORKERS)
WORKERS_ARG := $(if $(WORKERS),--workers $(WORKERS),)
EXP_WORKERS_ARG := $(if $(EXP_WORKERS),--workers $(EXP_WORKERS),)
SEED ?= 42
DEVICE ?=
DROP_FEATURE_PREFIXES ?=
# Default azoth screening profile: a probe-sized run for bulk iteration.
# Confirm winners with a different seed, an explicit larger sample, or make train.
EXP_TRAIN_SAMPLES ?= 150000
EXP_MAX_TEST_SAMPLES ?= 40000
EXP_MAX_ID ?=
EXP_REFRESH_CACHE_SNAPSHOT ?= 0
EXP_REFRESH_CACHE_SNAPSHOT_ARG := $(if $(filter 1 true yes,$(EXP_REFRESH_CACHE_SNAPSHOT)),--refresh-cache-snapshot,)
EXP_RERUN ?= 0
EXP_RERUN_ARG := $(if $(filter 1 true yes,$(EXP_RERUN)),--rerun-existing,)
EXP_ROUTE ?= general
EXP_IDEA ?= $(if $(EXP_TAG),$(patsubst _%,%,$(EXP_TAG)),adhoc)
EXP_ALLOWED_FEATURES_FILE ?=
EXP_FOLDS ?= 0
EXP_HOLDOUT_FRACTION ?= 0.12
EXP_ESTIMATORS ?= 180
EXP_MAX_DEPTH ?= 12
EXP_LEARNING_RATE ?= 0.05
EXP_EARLY_STOPPING ?= 25
EXP_NUM_LEAVES ?= $(if $(filter azoth,$(LEARNER)),96,)
EXP_MIN_CHILD_SAMPLES ?= $(if $(filter azoth,$(LEARNER)),100,)
EXP_COLSAMPLE_BYTREE ?= 0.8
EXP_SUBSAMPLE ?= 0.8
EXP_GAMMA ?= 0.0
EXP_REG_ALPHA ?= 0.0
EXP_REG_LAMBDA ?= 1.0
EXP_THRESHOLD_MODE ?= fbeta
EXP_THRESHOLD_FPR_TARGET ?=
EXP_HARD_NEGATIVE_FRACTION ?= 0.0
EXP_HARD_NEGATIVE_WEIGHT ?= 1.0
EXP_BENIGN_FILETYPE_WEIGHT ?=
EXP_MONOTONE_JSON ?=
EXP_SCALE_POS_WEIGHT_MULT ?= 1.0
EXP_BOOSTING_TYPE ?= gbdt
EXP_EXTRA_TREES ?= 0
EXP_SEED_SEARCH_K ?= 1
# When EXP_SEED_SEARCH_K>1, set EXP_SAVE_ALL_SEEDS=1 to deploy the averaged
# ensemble (item A) instead of picking-best. Bundle layout becomes
# models/seed_<S>.txt; litmus averages at predict time.
EXP_SAVE_ALL_SEEDS ?= 0
EXP_TEST_NATURAL_PREVALENCE ?= 0
EXP_BETA ?= 1.25
EXP_MIN_MALWARE_SCORE ?= 0
# Ablation 2026-04-10: silent_packer (Exp 43) and mtime_kurtosis (Exp 44) were
# net-negative at 75k experiment scale. air_gap_signal (Exp 46) and the
# extreme-features bundle (Exps 48/49/54/55/56) are kept ON.
EXP_SILENT_PACKER_SIGNAL ?= 0
EXP_MTIME_KURTOSIS ?= 0
EXP_AIR_GAP_SIGNAL ?= 1
EXP_EXTREME_FEATURES ?= 1
# Per-feature toggles within EXTREME_FEATURES bundle (Exps 48/49/51/54/55/56).
# Each defaults to inheriting from EXTREME_FEATURES; override individually for ablations.
EXP_ANACHRONISTIC_INJECTION ?=
EXP_CODE_ENTROPY_SPIKE ?=
EXP_FOREIGN_BINARY_SIGNAL ?=
EXP_EXTENSION_MISMATCH_SIGNAL ?=
EXP_HOSTILE_FINDING_DENSITY ?=
EXP_HOSTILE_DEPTH_WEIGHT ?=
# v16 default OFF: drops 163k inter:{ft}*{element/skeleton} features that contribute essentially nothing.
EXP_FILETYPE_INTERACTIONS ?= 0
EXP_FORMAT_HINTS ?= 0
# Default-on toggles in features.py — overridable for ablations.
EXP_BLINDFOLD ?= 1
EXP_SCORE_WEIGHTED_TRAITS ?= 1
EXP_SOFT_PRESENCE ?= 1
EXP_REPETITION_PENALTY_FEATURES ?= 1
EXP_FILE_SEVERITY_DISTRIBUTION ?= 1
EXP_HOSTILE_WEIGHTED_DENSITY ?= 1
EXP_HOSTILE_ESCALATION_FEATURES ?= 1
EXP_SUSPICIOUS_BREADTH_DENSITY ?= 1
EXP_STRUCT_FILE_RISK_COVERAGE ?= 1
EXP_TOP_K_RISK_FILES ?= 1
EXP_MIN_SAMPLE_SCORE ?= 3
# N-gram tuning: path depth (0=full, 2/3/4=truncated) and min crit (0=all, 3=notable+)
EXP_NGRAM_PATH_DEPTH ?= 0
EXP_NGRAM_MIN_CRIT ?= 0
EXP_TAXONOMY_FEATURES ?= 0
EXP_EXTENDED_METRICS ?= 1
EXP_METRIC_MIN_FREQ_PCT ?= 5
EXP_EMBER_LITE_FEATURES ?= 0
EXP_BIGRAM_MAX ?= 5000
EXP_BIGRAM_MIN_FREQ ?= 1000
EXP_TRIGRAM_MAX ?= 500
EXP_TRIGRAM_MAX_BENIGN_FRAC ?= 0.01
EXP_CONFIDENCE_WEIGHTED_NGRAMS ?= 0
EXP_OBJECTIVE_TRIGRAMS ?= 0
EXP_SUSPICIOUS_TRIGRAMS ?= 0
EXP_ATTACK_NGRAMS ?= 0
EXP_TIERED_BIGRAM_PATH_DEPTH ?= 3
EXP_TIERED_BIGRAM_MIN_CRIT ?= 3
EXP_TIERED_BIGRAM_MAX ?= 5000
EXP_TIERED_BIGRAM_MIN_FREQ ?= 5
EXP_TIERED_CRIT_TRIGRAMS ?= 0
EXP_TIERED_TRIGRAM_PATH_DEPTH ?= 3
EXP_TIERED_TRIGRAM_MIN_CRIT ?= 3
EXP_TIERED_TRIGRAM_MAX ?= 5000
EXP_TIERED_TRIGRAM_MIN_FREQ ?= 5
EXP_SYMBOL_VOCAB ?= 0
EXP_SYMBOL_VOCAB_MAX ?= 5000
EXP_SYMBOL_MIN_FREQ ?= 5
EXP_KV_VOCAB ?= 0
EXP_KV_VOCAB_MAX ?= 5000
EXP_KV_MIN_FREQ ?= 5
EXP_KV_SHAPE_FEATURES ?= 0
EXP_TEXT_ENCODING_FEATURES ?= 0
EXP_DISABLE_FEATURE_GROUPS ?= clusters
# packaged_capability compute mode: zero | chars | tokens | paths | findings
EXP_PACKAGED_CAPABILITY_MODE ?= paths
# Experiment data cache directory. When set, corpus selections and extracted
# matrices are cached to disk so repeated experiments skip expensive DB scans.
EXP_CACHE_DIR ?= out/cache/experiment/$(MODEL)
ABLATE_CACHE_DIR ?= $(EXP_CACHE_DIR)
ABLATE_MAX_ID ?=
ALLOWED_FEATURES ?= src/collimator/allowed_features.json

# Validate DB is set for targets that need it
check-db:
ifndef DB
	$(error DB is required. Usage: make train DB=postgres://hopper@localhost/hopper)
endif

# Fail if the newest sample is older than 24 hours (replication may be broken)
check-db-fresh: check-db
	@age_hours=$$(psql "$(DB)" -tAc \
		"SELECT EXTRACT(EPOCH FROM now() - MAX(updated_at)) / 3600 FROM samples;") ; \
	age_hours=$${age_hours%.*} ; \
	if [ "$$age_hours" -gt 2 ] 2>/dev/null; then \
		echo "ERROR: newest sample is $${age_hours}h old (>2h). Check logical replication status:" >&2 ; \
		echo "  sudo -u postgres psql -d hopper -c \"SELECT * FROM pg_stat_subscription;\"" >&2 ; \
		echo "  tail -20 /var/log/postgresql/postgresql-17-main.log" >&2 ; \
		exit 1 ; \
	fi

venv: $(VENV_DIR)/.deps.stamp

$(VENV_DIR)/bin/python:
	python3 -m venv $(VENV_DIR)

$(VENV_DIR)/.deps.stamp: requirements.txt pyproject.toml | $(VENV_DIR)/bin/python
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r requirements.txt
	$(VENV_DIR)/bin/pip install -e .
	touch $(VENV_DIR)/.deps.stamp

# azoth-train: the full top-level "give me the latest best deployed model"
# entry point.
#
#   1. Replay autocollie's highest-F1 historical run for the general route
#      (with multi-seed averaging on, so the resulting bundle is variance-
#      reduced). Configuration comes from out/experiments/azoth/runs/, so
#      every autocollie discovery flows in automatically.
#   2. Re-train every filegroup + filetype specialist using the same
#      autocollie-best-per-route mechanism (via the suite's
#      --autocollie-best-runs-dir hookup, on by default). Specialists also
#      get K=3 multi-seed averaging.
#   3. Calibrate + diagnostics + policy search + global FP/M check + bundle
#      validate + litmus parity, and copy the validated bundle to the live
#      deploy directory. Top-level docs (README.md, ENSEMBLE_MODEL.md,
#      GENERALIST_MODEL.md, route_diagnostics.md, etc.) get regenerated with
#      the new numbers.
#
# Always retrains from scratch on current DB state — the DB-snapshot pin
# protects against drift but there's no model-cache shortcut. Run any time
# you want the deployed bundle refreshed.
azoth-train: venv check-db
	$(PYTHON) scripts/azoth_train_best.py \
		--runs-dir $(AZOTH_AUTOCOLLIE_RUNS_DIR) \
		--route general \
		--set DB=$(DB) \
		$(if $(WORKERS),--set EXP_WORKERS=$(WORKERS),)
	$(MAKE) azoth-specialists
	$(MAKE) azoth-deploy

# fixture: regenerate extraction_fixture.json + cross_language_fixture.json
# using the SAME feature env autocollie's best general run was trained with,
# so litmus parity tests exercise the deployed model's feature pipeline
# rather than some divergent default.  Reuses azoth_train_best.py to resolve
# the env so there's exactly one place that knows "what features did we ship
# with" — historically this Make target reimplemented that knowledge as a
# wall of TRAIN_* vars that drifted from reality.
fixture: venv check-db
	$(PYTHON) scripts/azoth_train_best.py \
		--runs-dir $(AZOTH_AUTOCOLLIE_RUNS_DIR) \
		--route general \
		--exec $(PYTHON) -m collimator fixture --db $(DB) --output $(OUT_DIR) \
			$(if $(wildcard $(OUT_DIR)/$(MODEL_FILE)),--model $(OUT_DIR)/$(MODEL_FILE),) \
			$(if $(wildcard $(OUT_DIR)/feature_spec.json),--spec $(OUT_DIR)/feature_spec.json,)

evaluate: venv check-db
	$(PYTHON) -m collimator evaluate --db $(DB) --model $(OUT_DIR)/model.onnx --spec $(OUT_DIR)/feature_spec.json

explain: venv check-db
	$(PYTHON) -m collimator explain --db $(DB) --model $(OUT_DIR)/$(MODEL_FILE) --spec $(OUT_DIR)/feature_spec.json --output $(OUT_DIR)

inspect: venv check-db
ifndef SAMPLE
	$(error SAMPLE is required. Usage: make inspect DB=... SAMPLE=<sha256>)
endif
	$(PYTHON) -m collimator inspect --db $(DB) --sample $(SAMPLE) --model $(OUT_DIR)/$(MODEL_FILE) --spec $(OUT_DIR)/feature_spec.json

errors: venv check-db
	$(PYTHON) -m collimator errors --db $(DB) --model $(OUT_DIR)/$(MODEL_FILE) --spec $(OUT_DIR)/feature_spec.json

traits: venv check-db
	$(PYTHON) -m collimator traits --db $(DB)

thresholds: venv check-db
	$(PYTHON) -u -m collimator tune-thresholds --db $(DB) \
		--model $(OUT_DIR)/$(MODEL_FILE) \
		--spec $(OUT_DIR)/feature_spec.json \
		$(WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		--scores-cache $(THRESHOLD_SCORES) \
		--top-errors $(THRESHOLD_TOP_ERRORS) \
		--output $(OUT_DIR)/threshold_tuning.json

thresholds-refresh: venv check-db
	$(PYTHON) -u -m collimator tune-thresholds --db $(DB) \
		--model $(OUT_DIR)/$(MODEL_FILE) \
		--spec $(OUT_DIR)/feature_spec.json \
		$(WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		--scores-cache $(THRESHOLD_SCORES) \
		--refresh-cache \
		--top-errors $(THRESHOLD_TOP_ERRORS) \
		--output $(OUT_DIR)/threshold_tuning.json

filetype-matrix: venv check-db
	$(PYTHON) scripts/filetype_metric_matrix.py \
		--db $(DB) \
		--scores-cache $(THRESHOLD_SCORES) \
		--thresholds $(OUT_DIR)/threshold_tuning.json \
		--output $(FILETYPE_MATRIX_OUTPUT) \
		--csv-output $(FILETYPE_MATRIX_CSV) \
		--min-count $(FILETYPE_MATRIX_MIN_COUNT)

# Same env-resolution pattern as `fixture` — use the deployed model's
# feature env (autocollie's best general spec) so this benchmark sees the
# same features the production pipeline does.
elf-model-benchmark: venv check-db
	$(PYTHON) scripts/azoth_train_best.py \
		--runs-dir $(AZOTH_AUTOCOLLIE_RUNS_DIR) \
		--route general \
		--exec $(PYTHON) scripts/elf_model_benchmark.py \
		--db $(DB) \
		$(EXP_WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		--general-model $(ELF_BENCHMARK_GENERAL_DIR)/model.txt \
		--general-spec $(ELF_BENCHMARK_GENERAL_DIR)/feature_spec.json \
		--binary-output $(ELF_BENCHMARK_BINARY_DIR) \
		--elf-output $(ELF_BENCHMARK_ELF_DIR) \
		--output $(ELF_BENCHMARK_OUTPUT) \
		--seed $(SEED) \
		--n-folds $(ELF_BENCHMARK_FOLDS) \
		--n-estimators $(ELF_BENCHMARK_ESTIMATORS) \
		--max-depth $(ELF_BENCHMARK_MAX_DEPTH) \
		--learning-rate $(ELF_BENCHMARK_LEARNING_RATE) \
		--early-stopping-rounds $(ELF_BENCHMARK_EARLY_STOPPING) \
		--num-leaves $(ELF_BENCHMARK_NUM_LEAVES) \
		--min-child-samples $(ELF_BENCHMARK_MIN_CHILD_SAMPLES) \
		$(if $(DEVICE),--device $(DEVICE),)

elf-route-optimization: venv check-db
	$(PYTHON) scripts/elf_ensemble_experiments.py \
		--db $(DB) \
		--general-scores $(AZOTH_GENERAL_SCORES) \
		--general-spec $(AZOTH_GENERAL_DIR)/feature_spec.json \
		--teacher-model $(ELF_ROUTE_TEACHER_DIR)/model.txt \
		--teacher-spec $(ELF_ROUTE_TEACHER_DIR)/feature_spec.json \
		--output-dir $(ELF_ROUTE_OUTPUT_DIR) \
		--output $(ELF_ROUTE_OUTPUT) \
		$(EXP_WORKERS_ARG) \
		--seed $(SEED)

# Same env-resolution pattern as `fixture` and `elf-model-benchmark` —
# the suite trains every specialist with the deployed model's feature env.
# Per-route train_config and feature_env overrides for individual specialists
# come in via --autocollie-best-runs-dir (read from the suite, see the flag
# in scripts/azoth_specialist_suite.py).
azoth-specialists: venv check-db
	$(PYTHON) scripts/azoth_train_best.py \
		--runs-dir $(AZOTH_AUTOCOLLIE_RUNS_DIR) \
		--route general \
		--exec $(PYTHON) scripts/azoth_specialist_suite.py \
		--db $(DB) \
		$(EXP_WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		--output-root $(AZOTH_ROOT) \
		--summary $(AZOTH_SPECIALISTS_SUMMARY) \
		--general-dir $(AZOTH_GENERAL_DIR) \
		--seed $(SEED) \
		--n-folds $(AZOTH_SPECIALIST_FOLDS) \
		--n-estimators $(AZOTH_SPECIALIST_ESTIMATORS) \
		--max-depth $(AZOTH_SPECIALIST_MAX_DEPTH) \
		--learning-rate $(AZOTH_SPECIALIST_LEARNING_RATE) \
		--early-stopping-rounds $(AZOTH_SPECIALIST_EARLY_STOPPING) \
		--num-leaves $(AZOTH_SPECIALIST_NUM_LEAVES) \
		--min-child-samples $(AZOTH_SPECIALIST_MIN_CHILD_SAMPLES) \
		--n-seed-extras $(AZOTH_SPECIALIST_N_SEED_EXTRAS) \
		--min-bad $(AZOTH_SPECIALIST_MIN_BAD) \
		--min-good $(AZOTH_SPECIALIST_MIN_GOOD) \
		$(foreach target,$(AZOTH_SPECIALIST_ONLY),--only $(target)) \
		$(foreach mask,$(AZOTH_SPECIALIST_MASK_SPEC),--mask-spec $(mask)) \
		$(foreach override,$(AZOTH_SPECIALIST_TRAIN_OVERRIDE),--train-override $(override)) \
		$(foreach env,$(AZOTH_SPECIALIST_FEATURE_ENV),--feature-env $(env)) \
		$(if $(AZOTH_AUTOCOLLIE_RUNS_DIR),--autocollie-best-runs-dir $(AZOTH_AUTOCOLLIE_RUNS_DIR),) \
		$(AZOTH_SPECIALIST_SKIP_EXISTING_ARG) \
		$(AZOTH_FILEGROUP_SCORE_FILTER_ARG) \
		$(if $(DEVICE),--device $(DEVICE),)

azoth-calibrate: venv check-db
	$(PYTHON) scripts/azoth_calibrate_ensemble.py \
		--db $(DB) \
		$(EXP_WORKERS_ARG) \
		--azoth-root $(AZOTH_ROOT) \
		--summary $(AZOTH_SPECIALISTS_SUMMARY) \
		--general-scores $(AZOTH_GENERAL_SCORES) \
		--output $(AZOTH_CONFIG) \
		--score-table $(AZOTH_SCORE_TABLE) \
		$(AZOTH_REFRESH_SCORES_ARG) \
		$(AZOTH_SKIP_LEVEL_CALIBRATION_ARG) \
		$(foreach route,$(AZOTH_REFRESH_ROUTE),--refresh-route $(route)) \
		--feature-cache-dir $(AZOTH_FEATURE_CACHE_DIR)

azoth-diagnostics: venv
	$(PYTHON) scripts/azoth_route_diagnostics.py \
		--config $(AZOTH_CONFIG) \
		--score-table $(AZOTH_SCORE_TABLE) \
		--output $(AZOTH_DIAGNOSTICS) \
		--csv $(AZOTH_DIAGNOSTICS_CSV) \
		--slice-output $(AZOTH_SLICE_METRICS) \
		--slice-csv $(AZOTH_SLICE_METRICS_CSV)

azoth-policies: venv
	$(PYTHON) scripts/azoth_route_policy_search.py \
		$(if $(AZOTH_POLICY_OVERRIDE_ROUTE),--db $(DB),) \
		--config $(AZOTH_CONFIG) \
		--score-table $(AZOTH_SCORE_TABLE) \
		--output $(AZOTH_ROUTE_POLICIES) \
		--csv $(AZOTH_ROUTE_POLICIES_CSV) \
		--markdown $(AZOTH_ROUTE_POLICIES_MD) \
		$(foreach route,$(AZOTH_POLICY_OVERRIDE_ROUTE),--override-route $(route)) \
		$(EXP_WORKERS_ARG)

# azoth-validate runs every gate that azoth-deploy runs (calibrate, route
# diagnostics, policy search, global FP/M with --fail-on-budget, bundle
# validator, litmus parity), but stops short of copying anything into
# $(AZOTH_DEPLOY_DIR). Used by autocollie's auto-promote path to vet a
# candidate bundle without touching the live deploy.
.PHONY: azoth-validate
azoth-validate: azoth-calibrate
	@test -f $(AZOTH_ROOT)/config.json || { echo "error: $(AZOTH_ROOT)/config.json not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/score_table.npz || { echo "error: $(AZOTH_ROOT)/score_table.npz not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/specialists.json || { echo "error: $(AZOTH_ROOT)/specialists.json not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/general/model.txt || { echo "error: $(AZOTH_ROOT)/general/model.txt not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/general/feature_spec.json || { echo "error: $(AZOTH_ROOT)/general/feature_spec.json not found"; exit 1; }
	$(PYTHON) scripts/azoth_route_diagnostics.py \
		--config $(AZOTH_CONFIG) \
		--score-table $(AZOTH_SCORE_TABLE) \
		--output $(AZOTH_DIAGNOSTICS) \
		--csv $(AZOTH_DIAGNOSTICS_CSV) \
		--slice-output $(AZOTH_SLICE_METRICS) \
		--slice-csv $(AZOTH_SLICE_METRICS_CSV)
	$(PYTHON) scripts/azoth_route_policy_search.py \
		$(if $(AZOTH_POLICY_OVERRIDE_ROUTE),--db $(DB),) \
		--config $(AZOTH_CONFIG) \
		--score-table $(AZOTH_SCORE_TABLE) \
		--output $(AZOTH_ROUTE_POLICIES) \
		--csv $(AZOTH_ROUTE_POLICIES_CSV) \
		--markdown $(AZOTH_ROUTE_POLICIES_MD) \
		$(foreach route,$(AZOTH_POLICY_OVERRIDE_ROUTE),--override-route $(route)) \
		$(EXP_WORKERS_ARG)
	$(PYTHON) scripts/azoth_policy_global_metrics.py \
		--config $(AZOTH_CONFIG) \
		--policy $(AZOTH_ROUTE_POLICIES) \
		--score-table $(AZOTH_SCORE_TABLE) \
		--output $(AZOTH_GLOBAL_POLICY_METRICS) \
		--markdown $(AZOTH_GLOBAL_POLICY_METRICS_MD) \
		--fail-on-budget
	$(PYTHON) scripts/compute_routed_metrics.py --azoth-root $(AZOTH_ROOT) --db $(DB)
	$(PYTHON) scripts/write_azoth_readmes.py --azoth-root $(AZOTH_ROOT)
	@_STAGE=$$(mktemp -d) && \
	  $(PYTHON) scripts/stage_azoth_runtime_bundle.py "$(AZOTH_ROOT)" "$$_STAGE" && \
	  cp "$(AZOTH_DIAGNOSTICS)" "$$_STAGE/route_diagnostics.md" && \
	  cp "$(AZOTH_SLICE_METRICS)" "$$_STAGE/slice_metrics.md" && \
	  cp "$(AZOTH_ROUTE_POLICIES_MD)" "$$_STAGE/route_policies.md" && \
	  cp "$(AZOTH_GLOBAL_POLICY_METRICS_MD)" "$$_STAGE/global_policy_metrics.md" && \
	  $(PYTHON) scripts/validate_azoth_bundle.py "$$_STAGE" && \
	  echo "Running litmus deployed-ensemble compatibility checks against staged copy..." && \
	  ( cd $(LITMUS_DIR) && LITMUS_MODELS_DIR="$$_STAGE" cargo test --release --test scan_no_deadlock ) && \
	  $(PYTHON) scripts/verify_azoth_litmus_runtime.py --litmus-dir $(LITMUS_DIR) --models-dir "$$_STAGE" --required-model az/native --required-model az/elf && \
	  rm -rf "$$_STAGE" && \
	  echo "azoth-validate: all gates passed for $(AZOTH_ROOT)" \
	|| { ec=$$?; rm -rf "$$_STAGE"; exit $$ec; }

azoth-deploy: azoth-calibrate
	@test -f $(AZOTH_ROOT)/config.json || { echo "error: $(AZOTH_ROOT)/config.json not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/score_table.npz || { echo "error: $(AZOTH_ROOT)/score_table.npz not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/specialists.json || { echo "error: $(AZOTH_ROOT)/specialists.json not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/general/model.txt || { echo "error: $(AZOTH_ROOT)/general/model.txt not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/general/feature_spec.json || { echo "error: $(AZOTH_ROOT)/general/feature_spec.json not found"; exit 1; }
	$(PYTHON) scripts/azoth_route_diagnostics.py \
		--config $(AZOTH_CONFIG) \
		--score-table $(AZOTH_SCORE_TABLE) \
		--output $(AZOTH_DIAGNOSTICS) \
		--csv $(AZOTH_DIAGNOSTICS_CSV) \
		--slice-output $(AZOTH_SLICE_METRICS) \
		--slice-csv $(AZOTH_SLICE_METRICS_CSV)
	$(PYTHON) scripts/azoth_route_policy_search.py \
		$(if $(AZOTH_POLICY_OVERRIDE_ROUTE),--db $(DB),) \
		--config $(AZOTH_CONFIG) \
		--score-table $(AZOTH_SCORE_TABLE) \
		--output $(AZOTH_ROUTE_POLICIES) \
		--csv $(AZOTH_ROUTE_POLICIES_CSV) \
		--markdown $(AZOTH_ROUTE_POLICIES_MD) \
		$(foreach route,$(AZOTH_POLICY_OVERRIDE_ROUTE),--override-route $(route)) \
		$(EXP_WORKERS_ARG)
	$(PYTHON) scripts/azoth_policy_global_metrics.py \
		--config $(AZOTH_CONFIG) \
		--policy $(AZOTH_ROUTE_POLICIES) \
		--score-table $(AZOTH_SCORE_TABLE) \
		--output $(AZOTH_GLOBAL_POLICY_METRICS) \
		--markdown $(AZOTH_GLOBAL_POLICY_METRICS_MD) \
		--fail-on-budget
	$(PYTHON) scripts/compute_routed_metrics.py --azoth-root $(AZOTH_ROOT) --db $(DB)
	$(PYTHON) scripts/write_azoth_readmes.py --azoth-root $(AZOTH_ROOT)
	$(eval _STAGE := $(shell mktemp -d))
	$(PYTHON) scripts/stage_azoth_runtime_bundle.py "$(AZOTH_ROOT)" "$(_STAGE)"
	cp "$(AZOTH_DIAGNOSTICS)" "$(_STAGE)/route_diagnostics.md"
	cp "$(AZOTH_SLICE_METRICS)" "$(_STAGE)/slice_metrics.md"
	cp "$(AZOTH_ROUTE_POLICIES_MD)" "$(_STAGE)/route_policies.md"
	cp "$(AZOTH_GLOBAL_POLICY_METRICS_MD)" "$(_STAGE)/global_policy_metrics.md"
	$(PYTHON) scripts/validate_azoth_bundle.py "$(_STAGE)" || { rm -rf $(_STAGE); exit 1; }
	@echo "Running litmus deployed-ensemble compatibility checks against staged copy..."
	cd $(LITMUS_DIR) && LITMUS_MODELS_DIR=$(_STAGE) cargo test --release --test scan_no_deadlock || { rm -rf $(_STAGE); exit 1; }
	$(PYTHON) scripts/verify_azoth_litmus_runtime.py --litmus-dir $(LITMUS_DIR) --models-dir "$(_STAGE)" --required-model az/native --required-model az/elf || { rm -rf $(_STAGE); exit 1; }
	@mkdir -p "$(AZOTH_DEPLOY_DIR)"
	@find "$(AZOTH_DEPLOY_DIR)" -mindepth 1 -maxdepth 1 ! -name .git ! -name .gitignore ! -name LICENSE ! -name README.md ! -name TRAINING.md -exec rm -rf {} +
	@rm -f "$(AZOTH_DEPLOY_DIR)/model.json" "$(AZOTH_DEPLOY_DIR)/model.txt" "$(AZOTH_DEPLOY_DIR)/feature_spec.json" \
	  "$(AZOTH_DEPLOY_DIR)/evaluation.json" "$(AZOTH_DEPLOY_DIR)/extraction_fixture.json" "$(AZOTH_DEPLOY_DIR)/config.json" \
	  "$(AZOTH_DEPLOY_DIR)/shap_importance.json" "$(AZOTH_DEPLOY_DIR)/model.onnx" "$(AZOTH_DEPLOY_DIR)/MODEL.md" \
	  "$(AZOTH_DEPLOY_DIR)/route_diagnostics.md" "$(AZOTH_DEPLOY_DIR)/route_diagnostics.csv" \
	  "$(AZOTH_DEPLOY_DIR)/slice_metrics.md" "$(AZOTH_DEPLOY_DIR)/slice_metrics.csv" \
	  "$(AZOTH_DEPLOY_DIR)/route_policies.json" "$(AZOTH_DEPLOY_DIR)/route_policies.csv" \
	  "$(AZOTH_DEPLOY_DIR)/route_policies.md" \
	  "$(AZOTH_DEPLOY_DIR)/global_policy_metrics.json" "$(AZOTH_DEPLOY_DIR)/global_policy_metrics.md" \
	  "$(AZOTH_DEPLOY_DIR)/score_table.npz" "$(AZOTH_DEPLOY_DIR)/specialists.json"
	cp -R "$(_STAGE)/." "$(AZOTH_DEPLOY_DIR)/"
	@rm -rf $(_STAGE)
	@echo "Deployed azoth ensemble bundle to $(AZOTH_DEPLOY_DIR)"

false-positives: venv check-db
	$(PYTHON) -u -m collimator false-positives --db $(DB) \
		--model $(OUT_DIR)/$(MODEL_FILE) \
		--spec $(OUT_DIR)/feature_spec.json \
		$(WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		--scores-cache $(THRESHOLD_SCORES) \
		--top-errors $(TOP_ERRORS) \
		--output $(OUT_DIR)/false_positives.json

near-false-positives: venv check-db
	$(PYTHON) -u -m collimator near-false-positives --db $(DB) \
		--model $(OUT_DIR)/$(MODEL_FILE) \
		--spec $(OUT_DIR)/feature_spec.json \
		$(WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		--scores-cache $(THRESHOLD_SCORES) \
		--top-errors $(TOP_ERRORS) \
		--output $(OUT_DIR)/near_false_positives.json

false-negatives: venv check-db
	$(PYTHON) -u -m collimator false-negatives --db $(DB) \
		--model $(OUT_DIR)/$(MODEL_FILE) \
		--spec $(OUT_DIR)/feature_spec.json \
		$(WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		--scores-cache $(THRESHOLD_SCORES) \
		--top-errors $(TOP_ERRORS) \
		--output $(OUT_DIR)/false_negatives.json

near-false-negatives: venv check-db
	$(PYTHON) -u -m collimator near-false-negatives --db $(DB) \
		--model $(OUT_DIR)/$(MODEL_FILE) \
		--spec $(OUT_DIR)/feature_spec.json \
		$(WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		--scores-cache $(THRESHOLD_SCORES) \
		--top-errors $(TOP_ERRORS) \
		--output $(OUT_DIR)/near_false_negatives.json

false-positives-archive: false-positives
	$(PYTHON) scripts/archive_error_samples.py \
		--report $(OUT_DIR)/false_positives.json \
		--output $(FALSE_POSITIVES_ARCHIVE) \
		--samples-dir $(SAMPLES_DIR) \
		--kind false-positives \
		--top $(TOP_ERRORS)

false-negatives-archive: false-negatives
	$(PYTHON) scripts/archive_error_samples.py \
		--report $(OUT_DIR)/false_negatives.json \
		--output $(FALSE_NEGATIVES_ARCHIVE) \
		--samples-dir $(SAMPLES_DIR) \
		--kind false-negatives \
		--top $(TOP_ERRORS)

near-false-positives-archive: near-false-positives
	$(PYTHON) scripts/archive_error_samples.py \
		--report $(OUT_DIR)/near_false_positives.json \
		--output $(NEAR_FALSE_POSITIVES_ARCHIVE) \
		--samples-dir $(SAMPLES_DIR) \
		--kind near-false-positives \
		--top $(TOP_ERRORS)

near-false-negatives-archive: near-false-negatives
	$(PYTHON) scripts/archive_error_samples.py \
		--report $(OUT_DIR)/near_false_negatives.json \
		--output $(NEAR_FALSE_NEGATIVES_ARCHIVE) \
		--samples-dir $(SAMPLES_DIR) \
		--kind near-false-negatives \
		--top $(TOP_ERRORS)

false-positives-triage: false-positives
	$(PYTHON) scripts/triage_error_samples.py \
		--report $(OUT_DIR)/false_positives.json \
		--output-dir $(FALSE_POSITIVES_TRIAGE_DIR) \
		--samples-dir $(SAMPLES_DIR) \
		--kind false-positives \
		--top $(TOP_ERRORS)
	$(CLEAVE) --format=json $(FALSE_POSITIVES_TRIAGE_DIR) > $(FALSE_POSITIVES_TRIAGE_JSON)

near-false-positives-triage: near-false-positives
	$(PYTHON) scripts/triage_error_samples.py \
		--report $(OUT_DIR)/near_false_positives.json \
		--output-dir $(NEAR_FALSE_POSITIVES_TRIAGE_DIR) \
		--samples-dir $(SAMPLES_DIR) \
		--kind near-false-positives \
		--top $(TOP_ERRORS)
	$(CLEAVE) --format=json $(NEAR_FALSE_POSITIVES_TRIAGE_DIR) > $(NEAR_FALSE_POSITIVES_TRIAGE_JSON)

benchmark: venv check-db
	$(PYTHON) -m collimator benchmark --db $(DB) $(WORKERS_ARG) \
		$(if $(wildcard $(OUT_DIR)/$(MODEL_FILE)),--model $(OUT_DIR)/$(MODEL_FILE),) \
		$(if $(wildcard $(OUT_DIR)/feature_spec.json),--spec $(OUT_DIR)/feature_spec.json,)

build-splits: venv check-db
	$(PYTHON) -m collimator build-splits --db $(DB)

experiment: venv check-db
	@mkdir -p $(EXP_LOG_DIR)
	COLLIMATOR_ALLOWED_FEATURES_FILE=$(EXP_ALLOWED_FEATURES_FILE) \
	COLLIMATOR_SILENT_PACKER_SIGNAL=$(EXP_SILENT_PACKER_SIGNAL) \
	COLLIMATOR_MTIME_KURTOSIS=$(EXP_MTIME_KURTOSIS) \
	COLLIMATOR_AIR_GAP_SIGNAL=$(EXP_AIR_GAP_SIGNAL) \
	COLLIMATOR_EXTREME_FEATURES=$(EXP_EXTREME_FEATURES) \
	COLLIMATOR_ANACHRONISTIC_INJECTION=$(EXP_ANACHRONISTIC_INJECTION) \
	COLLIMATOR_CODE_ENTROPY_SPIKE=$(EXP_CODE_ENTROPY_SPIKE) \
	COLLIMATOR_FOREIGN_BINARY_SIGNAL=$(EXP_FOREIGN_BINARY_SIGNAL) \
	COLLIMATOR_EXTENSION_MISMATCH_SIGNAL=$(EXP_EXTENSION_MISMATCH_SIGNAL) \
	COLLIMATOR_HOSTILE_FINDING_DENSITY=$(EXP_HOSTILE_FINDING_DENSITY) \
	COLLIMATOR_HOSTILE_DEPTH_WEIGHT=$(EXP_HOSTILE_DEPTH_WEIGHT) \
	COLLIMATOR_FILETYPE_INTERACTIONS=$(EXP_FILETYPE_INTERACTIONS) \
	COLLIMATOR_FORMAT_HINTS=$(EXP_FORMAT_HINTS) \
	COLLIMATOR_BLINDFOLD=$(EXP_BLINDFOLD) \
	COLLIMATOR_SCORE_WEIGHTED_TRAITS=$(EXP_SCORE_WEIGHTED_TRAITS) \
	COLLIMATOR_SOFT_PRESENCE=$(EXP_SOFT_PRESENCE) \
	COLLIMATOR_REPETITION_PENALTY_FEATURES=$(EXP_REPETITION_PENALTY_FEATURES) \
	COLLIMATOR_FILE_SEVERITY_DISTRIBUTION=$(EXP_FILE_SEVERITY_DISTRIBUTION) \
	COLLIMATOR_HOSTILE_WEIGHTED_DENSITY=$(EXP_HOSTILE_WEIGHTED_DENSITY) \
	COLLIMATOR_HOSTILE_ESCALATION_FEATURES=$(EXP_HOSTILE_ESCALATION_FEATURES) \
	COLLIMATOR_SUSPICIOUS_BREADTH_DENSITY=$(EXP_SUSPICIOUS_BREADTH_DENSITY) \
	COLLIMATOR_STRUCT_FILE_RISK_COVERAGE=$(EXP_STRUCT_FILE_RISK_COVERAGE) \
	COLLIMATOR_TOP_K_RISK_FILES=$(EXP_TOP_K_RISK_FILES) \
	COLLIMATOR_DISABLE_FEATURE_GROUPS=$(EXP_DISABLE_FEATURE_GROUPS) \
	COLLIMATOR_PACKAGED_CAPABILITY_MODE=$(EXP_PACKAGED_CAPABILITY_MODE) \
	COLLIMATOR_MIN_SAMPLE_SCORE=$(EXP_MIN_SAMPLE_SCORE) \
	COLLIMATOR_NGRAM_PATH_DEPTH=$(EXP_NGRAM_PATH_DEPTH) \
	COLLIMATOR_NGRAM_MIN_CRIT=$(EXP_NGRAM_MIN_CRIT) \
	COLLIMATOR_TAXONOMY_FEATURES=$(EXP_TAXONOMY_FEATURES) \
	COLLIMATOR_EXTENDED_METRICS=$(EXP_EXTENDED_METRICS) \
	COLLIMATOR_METRIC_MIN_FREQ_PCT=$(EXP_METRIC_MIN_FREQ_PCT) \
	COLLIMATOR_EMBER_LITE_FEATURES=$(EXP_EMBER_LITE_FEATURES) \
	COLLIMATOR_BIGRAM_MAX=$(EXP_BIGRAM_MAX) \
	COLLIMATOR_BIGRAM_MIN_FREQ=$(EXP_BIGRAM_MIN_FREQ) \
	COLLIMATOR_TRIGRAM_MAX=$(EXP_TRIGRAM_MAX) \
	COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=$(EXP_TRIGRAM_MAX_BENIGN_FRAC) \
	COLLIMATOR_ATTACK_FEATURES=1 \
	COLLIMATOR_CONFIDENCE_WEIGHTED_NGRAMS=$(EXP_CONFIDENCE_WEIGHTED_NGRAMS) \
	COLLIMATOR_OBJECTIVE_TRIGRAMS=$(EXP_OBJECTIVE_TRIGRAMS) \
	COLLIMATOR_SUSPICIOUS_TRIGRAMS=$(EXP_SUSPICIOUS_TRIGRAMS) \
	COLLIMATOR_ATTACK_NGRAMS=$(EXP_ATTACK_NGRAMS) \
	COLLIMATOR_CRIT_CATEGORY_NGRAMS=1 \
	COLLIMATOR_TIERED_CRIT_BIGRAMS=1 \
	COLLIMATOR_TIERED_BIGRAM_PATH_DEPTH=$(EXP_TIERED_BIGRAM_PATH_DEPTH) \
	COLLIMATOR_TIERED_BIGRAM_MIN_CRIT=$(EXP_TIERED_BIGRAM_MIN_CRIT) \
	COLLIMATOR_TIERED_BIGRAM_MAX=$(EXP_TIERED_BIGRAM_MAX) \
	COLLIMATOR_TIERED_BIGRAM_MIN_FREQ=$(EXP_TIERED_BIGRAM_MIN_FREQ) \
	COLLIMATOR_TIERED_CRIT_TRIGRAMS=$(EXP_TIERED_CRIT_TRIGRAMS) \
	COLLIMATOR_TIERED_TRIGRAM_PATH_DEPTH=$(EXP_TIERED_TRIGRAM_PATH_DEPTH) \
	COLLIMATOR_TIERED_TRIGRAM_MIN_CRIT=$(EXP_TIERED_TRIGRAM_MIN_CRIT) \
	COLLIMATOR_TIERED_TRIGRAM_MAX=$(EXP_TIERED_TRIGRAM_MAX) \
	COLLIMATOR_TIERED_TRIGRAM_MIN_FREQ=$(EXP_TIERED_TRIGRAM_MIN_FREQ) \
	COLLIMATOR_SYMBOL_VOCAB=$(EXP_SYMBOL_VOCAB) \
	COLLIMATOR_SYMBOL_VOCAB_MAX=$(EXP_SYMBOL_VOCAB_MAX) \
	COLLIMATOR_SYMBOL_MIN_FREQ=$(EXP_SYMBOL_MIN_FREQ) \
	COLLIMATOR_KV_VOCAB=$(EXP_KV_VOCAB) \
	COLLIMATOR_KV_VOCAB_MAX=$(EXP_KV_VOCAB_MAX) \
	COLLIMATOR_KV_MIN_FREQ=$(EXP_KV_MIN_FREQ) \
	COLLIMATOR_KV_SHAPE_FEATURES=$(EXP_KV_SHAPE_FEATURES) \
	COLLIMATOR_TEXT_ENCODING_FEATURES=$(EXP_TEXT_ENCODING_FEATURES) \
	COLLIMATOR_ATTACK_CODE_NGRAMS=1 \
	COLLIMATOR_EXPERIMENT_TAG=$(EXP_TAG) \
	$(PYTHON) -u -m collimator experiment --db $(DB) --output $(EXP_OUT_DIR) --model-name $(MODEL) --learner $(LEARNER) $(EXP_WORKERS_ARG) --seed $(SEED) \
		--experiment-idea $(EXP_IDEA) --route $(EXP_ROUTE) $(EXP_RERUN_ARG) \
		--train-samples $(EXP_TRAIN_SAMPLES) --max-test-samples $(EXP_MAX_TEST_SAMPLES) \
		$(if $(EXP_MAX_ID),--max-id $(EXP_MAX_ID),) \
		$(EXP_REFRESH_CACHE_SNAPSHOT_ARG) \
		--n-folds $(EXP_FOLDS) --holdout-fraction $(EXP_HOLDOUT_FRACTION) \
		--n-estimators $(EXP_ESTIMATORS) --max-depth $(EXP_MAX_DEPTH) \
		--learning-rate $(EXP_LEARNING_RATE) --early-stopping-rounds $(EXP_EARLY_STOPPING) \
		$(if $(EXP_NUM_LEAVES),--num-leaves $(EXP_NUM_LEAVES),) \
		$(if $(EXP_MIN_CHILD_SAMPLES),--min-child-samples $(EXP_MIN_CHILD_SAMPLES),) \
		--colsample-bytree $(EXP_COLSAMPLE_BYTREE) --subsample $(EXP_SUBSAMPLE) \
		--gamma $(EXP_GAMMA) --reg-alpha $(EXP_REG_ALPHA) --reg-lambda $(EXP_REG_LAMBDA) \
		$(if $(DEVICE),--device $(DEVICE),) \
		$(if $(DROP_FEATURE_PREFIXES),--drop-feature-prefixes $(DROP_FEATURE_PREFIXES),) \
		$(if $(EXP_MONOTONE_JSON),--monotone-json '$(EXP_MONOTONE_JSON)',) \
		--min-malware-score $(EXP_MIN_MALWARE_SCORE) \
		--beta $(EXP_BETA) --threshold-mode $(EXP_THRESHOLD_MODE) \
		$(if $(EXP_THRESHOLD_FPR_TARGET),--threshold-fpr-target $(EXP_THRESHOLD_FPR_TARGET),) \
		--hard-negative-fraction $(EXP_HARD_NEGATIVE_FRACTION) --hard-negative-weight $(EXP_HARD_NEGATIVE_WEIGHT) \
		--scale-pos-weight-mult $(EXP_SCALE_POS_WEIGHT_MULT) \
		--boosting-type $(EXP_BOOSTING_TYPE) \
		$(if $(filter 1 true yes,$(EXP_EXTRA_TREES)),--extra-trees,) \
		--seed-search-k $(EXP_SEED_SEARCH_K) \
		$(if $(filter 1 true yes,$(EXP_SAVE_ALL_SEEDS)),--save-all-seeds,) \
		$(if $(filter 1 true yes,$(EXP_TEST_NATURAL_PREVALENCE)),--test-natural-prevalence,) \
		$(foreach w,$(subst $(_comma), ,$(EXP_BENIGN_FILETYPE_WEIGHT)),--benign-filetype-weight $(w)) \
		$(if $(EXP_CACHE_DIR),--cache-dir $(EXP_CACHE_DIR),) \
		2>&1 | tee "$(EXP_LOG_DIR)/$$(date +%Y-%m-%dT%H-%M-%S)-experiment$(EXP_TAG).log"

# Leave-one-group-out ablation. Same env-resolution pattern: replay the
# deployed model's feature env so ablation results reflect behavior at the
# operating point the production pipeline actually ships. Hyperparameters
# are drawn from the same source — no need for a parallel TRAIN_* knobs
# table here.
ablate: venv check-db
	$(PYTHON) scripts/azoth_train_best.py \
		--runs-dir $(AZOTH_AUTOCOLLIE_RUNS_DIR) \
		--route general \
		--exec $(PYTHON) -m collimator ablate --db $(DB) $(WORKERS_ARG) --seed $(SEED) \
			--model-name $(MODEL) --learner $(LEARNER) \
			$(if $(DEVICE),--device $(DEVICE),) \
			--n-folds $(or $(ABLATE_FOLDS),2) \
			$(if $(ABLATE_CACHE_DIR),--cache-dir $(ABLATE_CACHE_DIR),) \
			$(if $(ABLATE_MAX_ID),--max-id $(ABLATE_MAX_ID),) \
			$(if $(ABLATE_SAMPLES),--train-samples $(ABLATE_SAMPLES),) \
			$(if $(ABLATE_TEST_SAMPLES),--max-test-samples $(ABLATE_TEST_SAMPLES),) \
			$(if $(ABLATE_GROUPS),--groups $(ABLATE_GROUPS),) \
			$(if $(ABLATE_OUTPUT),--output $(ABLATE_OUTPUT),) \
			2>&1 | tee "$(LOG_DIR)/$$(date +%Y-%m-%dT%H-%M-%S)-ablation$(EXP_TAG).log"

ablation: ablate

demo-db: venv
	$(PYTHON) -m collimator demo-db --output $(DEMO_DB) --seed $(SEED)

scan: venv
ifndef FILE
	$(error FILE is required. Usage: make scan FILE=/path/to/binary)
endif
	$(PYTHON) -m collimator scan $(FILE) --model $(OUT_DIR)/$(MODEL_FILE) --spec $(OUT_DIR)/feature_spec.json --cleave $(CLEAVE) $(if $(DB),--db $(DB),)

test: venv
	$(VENV_DIR)/bin/pip install pytest
	$(PYTHON) -m pytest tests/ -v

lint: venv
	$(VENV_DIR)/bin/pip install ruff mypy
	$(VENV_DIR)/bin/ruff check src/ tests/
	$(VENV_DIR)/bin/mypy src/collimator/

XDG_DATA_HOME ?= $(HOME)/.local/share
# Model bundle directory. Azoth is the default model family; other explicit
# MODEL values deploy to same-named sibling bundles unless BUNDLE is set.
BUNDLE ?= $(if $(filter azoth,$(LEARNER)),azoth,$(MODEL))
MODELS_DIR ?= $(XDG_DATA_HOME)/litmus/models/$(BUNDLE)
XGBOOST_ARS_DIR ?= ../xgboost-ars
LIGHTGBM_ARS_DIR ?= ../lightgbm-ars

LITMUS_DIR ?= ../litmus

# verify-xgboost-ars is only meaningful when shipping an XGBoost booster.
# For azoth (LightGBM) models we skip it; lightgbm-ars's own parity
# tests live in its repo and verify-litmus exercises the integrated path.
_DEPLOY_PREREQS := verify-xgboost-ars verify-litmus

ifeq ($(LEARNER),azoth)
deploy: azoth-deploy
else
deploy: $(_DEPLOY_PREREQS)
	@# Stage to a temp dir first — every staged file passes the
	@# compatibility tests before we touch anything in MODELS_DIR.
	$(eval _STAGE := $(shell mktemp -d))
	cp $(OUT_DIR)/$(MODEL_FILE) $(_STAGE)/$(MODEL_FILE)
	cp $(OUT_DIR)/feature_spec.json $(_STAGE)/feature_spec.json
	@test -f $(OUT_DIR)/extraction_fixture.json || { rm -rf $(_STAGE); echo "error: extraction_fixture.json not found"; exit 1; }
	cp $(OUT_DIR)/extraction_fixture.json $(_STAGE)/extraction_fixture.json
	@# Optional artifacts: explain.rs reads shap_importance.json if
	@# present (and degrades silently otherwise); model.onnx is for
	@# non-litmus downstream consumers and litmus itself never reads it.
	@test ! -f $(OUT_DIR)/evaluation.json || cp $(OUT_DIR)/evaluation.json $(_STAGE)/evaluation.json
	@test ! -f $(OUT_DIR)/shap_importance.json || cp $(OUT_DIR)/shap_importance.json $(_STAGE)/shap_importance.json
	@test ! -f $(OUT_DIR)/model.onnx || cp $(OUT_DIR)/model.onnx $(_STAGE)/model.onnx
	@test ! -f $(OUT_DIR)/README.md || cp $(OUT_DIR)/README.md $(_STAGE)/README.md
	@test ! -f $(OUT_DIR)/MODEL.md || cp $(OUT_DIR)/MODEL.md $(_STAGE)/MODEL.md
	@$(PYTHON) scripts/build_litmus_config.py --threshold-tuning $(OUT_DIR)/threshold_tuning.json --output $(_STAGE)/config.json || { rm -rf $(_STAGE); exit 1; }
	@echo "Running litmus deployed-model compatibility checks against staged copy..."
	cd $(LITMUS_DIR) && LITMUS_MODELS_DIR=$(_STAGE) cargo test --release --test feature_spec || { rm -rf $(_STAGE); exit 1; }
	cd $(LITMUS_DIR) && LITMUS_MODELS_DIR=$(_STAGE) cargo test --release --test extraction_parity || { rm -rf $(_STAGE); exit 1; }
	@# Promote into MODELS_DIR without swapping the directory wholesale, so
	@# `.git/` and unrelated repo files survive. Remove stale model-layout
	@# artifacts first: litmus treats a leftover general/ directory as an
	@# ensemble bundle and would ignore the freshly deployed single bundle.
	@mkdir -p $(MODELS_DIR)
	@rm -rf "$(MODELS_DIR)/general" "$(MODELS_DIR)/filegroups" "$(MODELS_DIR)/filetypes"
	@rm -f "$(MODELS_DIR)/model.json" "$(MODELS_DIR)/model.txt" "$(MODELS_DIR)/feature_spec.json" \
	  "$(MODELS_DIR)/evaluation.json" "$(MODELS_DIR)/extraction_fixture.json" "$(MODELS_DIR)/config.json" \
	  "$(MODELS_DIR)/shap_importance.json" "$(MODELS_DIR)/model.onnx" "$(MODELS_DIR)/README.md" \
	  "$(MODELS_DIR)/MODEL.md"
	@for f in $(MODEL_FILE) feature_spec.json evaluation.json extraction_fixture.json config.json shap_importance.json model.onnx README.md MODEL.md; do \
	  if [ -f "$(_STAGE)/$$f" ]; then \
	    cp "$(_STAGE)/$$f" "$(MODELS_DIR)/$$f"; \
	  fi; \
	done
	@rm -rf $(_STAGE)
	@echo "litmus: all deploy checks passed"
	@echo "Deployed to $(MODELS_DIR) (commit and push manually if you want to publish)."
endif

.PHONY: verify-xgboost-ars
verify-xgboost-ars:
	@test -d $(XGBOOST_ARS_DIR) || { echo "error: $(XGBOOST_ARS_DIR) does not exist"; exit 1; }
	@test -f $(OUT_DIR)/reference.json || { echo "error: $(OUT_DIR)/reference.json not found — run make train first"; exit 1; }
	@echo "Running xgboost-ars tests..."
	cd $(XGBOOST_ARS_DIR) && XGBOOST_ARS_REFERENCE_JSON=$(abspath $(OUT_DIR)/reference.json) cargo test --release
	@echo "xgboost-ars: all tests passed"

.PHONY: verify-litmus
verify-litmus:
	@test -d $(LITMUS_DIR) || { echo "error: $(LITMUS_DIR) does not exist"; exit 1; }
	@test -f $(OUT_DIR)/extraction_fixture.json || { echo "error: $(OUT_DIR)/extraction_fixture.json not found — run make train first"; exit 1; }
	@test ! -f $(OUT_DIR)/threshold_tuning.json || $(PYTHON) scripts/build_litmus_config.py --threshold-tuning $(OUT_DIR)/threshold_tuning.json --output $(OUT_DIR)/config.json
	@echo "Running litmus feature-extraction parity tests..."
	@mkdir -p $(LITMUS_DIR)/tests/fixtures
	cp $(OUT_DIR)/extraction_fixture.json $(LITMUS_DIR)/tests/fixtures/extraction_fixture.json
	cd $(LITMUS_DIR) && LITMUS_MODELS_DIR=$(abspath $(OUT_DIR)) cargo test --release --test extraction_parity
	@echo "litmus: extraction parity tests passed"

AUTOCOLLIE_DIR ?= ../autocollie
AUTOCOLLIE_BIN := $(AUTOCOLLIE_DIR)/bin/autocollie
EXPERIMENTS ?= 8
# Autocollie defaults to the hopper-host Postgres so it doesn't compete with
# the local replica while it's syncing. Override with DB= to point elsewhere.
AUTOCOLLIE_DB ?= postgres://hopper@hopper:5432/hopper
# ROUTES is comma-separated, e.g. ROUTES=filetypes/javascript,filegroups/scripts
# ROUTE (singular) is accepted as a convenience.
ROUTES ?= $(ROUTE)

.PHONY: autocollie autocollie-loop autocollie-build autocollie-dryrun autocollie-screen autocollie-confirm autocollie-promote azoth-augment-small-routes

# azoth-augment-small-routes — post-hoc threshold re-search for routes whose
# default-level policy is `no_policy` because their own benign pool is too
# small to estimate FP rate at L3 (3/M).  Loads each such specialist, scores
# its filegroup peers' benigns, and re-runs the threshold search against the
# augmented pool.  Optional --use-credible-bound applies Beta-Binomial
# smoothing for routes with very small pools.
#
# Costs real inference time (default ~100k benigns × N routes); not in the
# default azoth-deploy chain.  Run after a fresh azoth-validate to recover
# deployable thresholds on small-corpus routes.
#
# Usage:
#   make azoth-augment-small-routes
#   make azoth-augment-small-routes ONLY_ROUTE=filetypes/macho
#   make azoth-augment-small-routes USE_CREDIBLE_BOUND=1
ONLY_ROUTE ?=
USE_CREDIBLE_BOUND ?=
MAX_POOL_BENIGNS ?= 100000
azoth-augment-small-routes: venv check-db
	$(PYTHON) scripts/azoth_augment_small_route_policies.py \
		--azoth-root $(AZOTH_ROOT) \
		--db $(DB) \
		--max-pool-benigns $(MAX_POOL_BENIGNS) \
		--workers $(or $(WORKERS),32) \
		$(if $(filter 1 true yes,$(USE_CREDIBLE_BOUND)),--use-credible-bound,) \
		$(if $(ONLY_ROUTE),--only-routes $(ONLY_ROUTE),)
	$(PYTHON) scripts/azoth_policy_global_metrics.py \
		--config $(AZOTH_CONFIG) \
		--policy $(AZOTH_ROUTE_POLICIES) \
		--score-table $(AZOTH_SCORE_TABLE) \
		--output $(AZOTH_GLOBAL_POLICY_METRICS) \
		--markdown $(AZOTH_GLOBAL_POLICY_METRICS_MD) \
		--fail-on-budget
	$(PYTHON) scripts/compute_routed_metrics.py --azoth-root $(AZOTH_ROOT) --db $(DB)
	$(PYTHON) scripts/write_azoth_readmes.py --azoth-root $(AZOTH_ROOT)

# Autocollie targets all default DB to AUTOCOLLIE_DB (hopper-host). User can
# still override with `make autocollie DB=...`; command-line vars beat
# target-specific assignments in GNU make.
autocollie autocollie-screen autocollie-confirm autocollie-promote autocollie-loop autocollie-dryrun: DB = $(AUTOCOLLIE_DB)

autocollie-build:
	@test -d $(AUTOCOLLIE_DIR) || { echo "error: $(AUTOCOLLIE_DIR) does not exist"; exit 1; }
	@mkdir -p $(AUTOCOLLIE_DIR)/bin
	go -C $(AUTOCOLLIE_DIR) build -o bin/autocollie ./cmd/autocollie

autocollie-dryrun: autocollie-build
	@test -n "$(ROUTES)" || { echo "error: set ROUTES=route1,route2 (or ROUTE=route)"; exit 1; }
	$(AUTOCOLLIE_BIN) dryrun \
		--collimator $(CURDIR) \
		--autocollie $(abspath $(AUTOCOLLIE_DIR)) \
		--routes $(ROUTES) \
		--experiments $(EXPERIMENTS)

autocollie-screen: venv check-db autocollie-build
	@test -n "$(ROUTES)" || { echo "error: set ROUTES=route1,route2 (or ROUTE=route)"; exit 1; }
	$(AUTOCOLLIE_BIN) screen \
		--collimator $(CURDIR) \
		--autocollie $(abspath $(AUTOCOLLIE_DIR)) \
		--routes $(ROUTES) \
		--experiments $(EXPERIMENTS) \
		--make-args "DB=$(DB) EXP_WORKERS=$(or $(WORKERS),64) EXP_ESTIMATORS=$(or $(EXP_ESTIMATORS_DEFAULT),250)"

# Confirm a screening winner by re-running with a different seed.
# Usage: make autocollie-confirm KEY=<16-hex experiment_key> [SEED=43]
CONFIRM_SEED ?= 43
autocollie-confirm: venv check-db autocollie-build
	@test -n "$(KEY)" || { echo "error: set KEY=<16-hex experiment_key>"; exit 1; }
	$(AUTOCOLLIE_BIN) confirm \
		--collimator $(CURDIR) \
		--autocollie $(abspath $(AUTOCOLLIE_DIR)) \
		--key $(KEY) \
		--seed $(CONFIRM_SEED) \
		--make-args "DB=$(DB) EXP_WORKERS=$(or $(WORKERS),64) EXP_ESTIMATORS=$(or $(EXP_ESTIMATORS_DEFAULT),250)"

# Promote a winner: confirm (different seed) -> full-train (inflated profile)
# -> compare. On pass, writes a report telling the user to run `make azoth-deploy`.
# Never deploys itself. Usage: make autocollie-promote KEY=<16-hex experiment_key>
autocollie-promote: venv check-db autocollie-build
	@test -n "$(KEY)" || { echo "error: set KEY=<16-hex experiment_key>"; exit 1; }
	$(AUTOCOLLIE_BIN) promote \
		--collimator $(CURDIR) \
		--autocollie $(abspath $(AUTOCOLLIE_DIR)) \
		--key $(KEY) \
		--seed $(CONFIRM_SEED) \
		--screen-timeout 30m \
		--promote-timeout 180m \
		--make-args "DB=$(DB) EXP_WORKERS=$(or $(WORKERS),64) EXP_ESTIMATORS=$(or $(EXP_ESTIMATORS_DEFAULT),250)"

# The full hands-off ladder: screen N specs per route -> if any winner beats
# the route's historical best, automatically promote it (confirm + full-train
# + holdout comparison). Writes per-route summaries and a deploy-or-not
# report on each promotion. Never deploys itself.
# Usage: make autocollie ROUTES=filetypes/python,filetypes/rust [EXPERIMENTS=10] [PASSES=1]
#        make autocollie ROUTES=filetypes/                       (overnight)
#        make autocollie ROUTES=filetypes/python PASSES=0        (loop until Ctrl-C)
PASSES ?= 1
AUTO_ROUTES ?=
SHUFFLE_ROUTES ?=
autocollie: venv check-db autocollie-build
	@test -n "$(ROUTES)$(AUTO_ROUTES)$(SHUFFLE_ROUTES)" || { echo "error: set ROUTES=route1,route2 (or AUTO_ROUTES=N for top-N weakest, or SHUFFLE_ROUTES=1 for random walk over every known route)"; exit 1; }
	$(AUTOCOLLIE_BIN) auto \
		--collimator $(CURDIR) \
		--autocollie $(abspath $(AUTOCOLLIE_DIR)) \
		$(if $(ROUTES),--routes $(ROUTES),) \
		$(if $(AUTO_ROUTES),--auto-routes $(AUTO_ROUTES),) \
		$(if $(filter 1 true yes,$(SHUFFLE_ROUTES)),--shuffle-routes,) \
		--experiments $(EXPERIMENTS) \
		--passes $(PASSES) \
		--seed $(CONFIRM_SEED) \
		--screen-timeout 30m \
		--promote-timeout 180m \
		--make-args "DB=$(DB) EXP_WORKERS=$(or $(WORKERS),64) EXP_ESTIMATORS=$(or $(EXP_ESTIMATORS_DEFAULT),250)"

# autocollie-loop is the same target with PASSES=0 — loops the screen+promote
# ladder over the route list until Ctrl-C. Pi sessions persist per route so
# the LLM accumulates context across passes (seeing more prior runs each
# cycle, naturally avoiding re-proposals).
#
# Three ways to use it:
#   make autocollie-loop ROUTES=filetypes/python EXPERIMENTS=10
#     — fixed route list, loops indefinitely (same order each pass)
#   make autocollie-loop AUTO_ROUTES=3 EXPERIMENTS=5
#     — picks the 3 weakest routes each pass by recall@3 headroom
#       (self-balancing — concentrates on routes with most to gain)
#   make autocollie-loop SHUFFLE_ROUTES=1 EXPERIMENTS=10
#     — walks every known route (general + all filegroups + all filetypes)
#       in random order, re-shuffling each pass. Try 10 things per route, then
#       move on. Best for "throw a bunch of stuff at the wall overnight."
autocollie-loop: PASSES=0
autocollie-loop: autocollie

clean:
	rm -rf $(OUT_DIR)

help:
	@echo "Collimator Training Pipeline"
	@echo ""
	@echo "Usage: make <target> [DB=postgres://...]"
	@echo ""
	@echo "Targets:"
	@echo "  train              Train production model on full dataset"
	@echo "  experiment         Run fast subsampled experiment"
	@echo "  evaluate           Run evaluation on external test set"
	@echo "  explain            Generate SHAP importance analysis"
	@echo "  inspect            Show feature breakdown for a sample (SAMPLE=sha256)"
	@echo "  errors             Show top false positives/negatives"
	@echo "  traits             Dump all unique traits seen in DB"
	@echo "  thresholds         Tune severity thresholds on the full corpus"
	@echo "  thresholds-refresh Rebuild cached threshold scores, then tune thresholds"
	@echo "  azoth-diagnostics  Report routed ensemble marginal value by model route"
	@echo "  azoth-policies     Search best calibrated route policy per filetype"
	@echo "  elf-route-optimization Test ELF route OR/replacement/acquittal experiments"
	@echo "  false-positives    Show false positives grouped by severity level"
	@echo "  false-negatives    Show false negatives grouped by severity level"
	@echo "  near-false-positives Show benign rows newly flagged by twice-looser level 9"
	@echo "  near-false-negatives Show bad rows newly caught by twice-looser level 9"
	@echo "  false-positives-archive Package top false positives into a tgz"
	@echo "  false-negatives-archive Package top false negatives into a tgz"
	@echo "  near-false-positives-archive Package top near false positives into a tgz"
	@echo "  near-false-negatives-archive Package top near false negatives into a tgz"
	@echo "  benchmark          Measure feature extraction & inference latency"
	@echo "  build-splits       Pre-compute data splits in DB"
	@echo "  autocollie-build   Build the autocollie Go orchestrator (../autocollie)"
	@echo "  autocollie-dryrun  Generate+validate experiment specs via LLM (no run)"
	@echo "  autocollie-screen  Generate, validate, and run experiment specs via LLM"
	@echo "  autocollie-confirm Re-run KEY=<16hex> with a different seed (SEED=43 default)"
	@echo "  autocollie-promote Confirm + full-train + compare; writes a deploy-or-not report"
	@echo "  autocollie         Full hands-off ladder: screen + auto-promote per route"
	@echo "  autocollie-loop    Same as autocollie with PASSES=0 (loop until Ctrl-C)"
	@echo "  azoth-validate     Run all azoth-deploy gates against AZOTH_ROOT without copying"
	@echo "  demo-db            Create a small SQLite DB for testing"
	@echo "  test               Run unit tests"
	@echo "  deploy             Copy model artifacts to ../litmus-models"
	@echo ""
	@echo "Options:"
	@echo "  DB=url             Hopper database DSN"
	@echo "  MODEL=name         Model artifact namespace (default: litmus-xg; e.g. azoth)"
	@echo "  LEARNER=name       Learner implementation (default: inferred from MODEL)"
	@echo "  DROP_FEATURE_PREFIXES=a,b  Drop feature prefixes for train/experiment candidates"
	@echo "  OUT_DIR=path       Output directory (default: out/models/<target-model>)"
	@echo "  DEVICE=name        Training device override (e.g. cuda for azoth)"
	@echo "  WORKERS=n          Parallel extraction workers (default: auto = physical cores)"
	@echo "  EXP_TRAIN_SAMPLES=n   Experiment train rows (default: 150000)"
	@echo "  EXP_MAX_TEST_SAMPLES=n  Cap test set via reservoir (0=full, default: 40000)"
	@echo "  EXP_FOLDS=n           Experiment CV folds (default: 0)"
	@echo "  EXP_ESTIMATORS=n      Experiment max trees (default: 180)"
	@echo "  EXP_IDEA=name        Human-readable experiment idea label"
	@echo "  EXP_ROUTE=route      Experiment route (default: general)"
	@echo "  EXP_RERUN=1          Force rerun of an existing canonical experiment"
	@echo "  ROUTES=a,b           Comma-separated routes for autocollie (or ROUTE=)"
	@echo "                       Trailing slash expands a prefix from prior runs:"
	@echo "                       ROUTES=filetypes/   -> all filetypes/* ever run"
	@echo "                       ROUTES=filegroups/  -> all filegroups/*"
	@echo "  EXPERIMENTS=n        Specs requested per autocollie cycle (default: 8)"
	@echo "  PASSES=n             Times to loop the autocollie route list (0=until Ctrl-C)"
	@echo "  EXP_ESTIMATORS_DEFAULT=n  Floor for screen/confirm/promote estimators (default: 250)"
	@echo "  AZOTH_SPECIALIST_TRAIN_OVERRIDE='route:field=value ...'"
	@echo "                       Per-route specialist TrainConfig overrides"
	@echo "  MODELS_DIR=path    Deployment target (default: ../litmus-models/<target-model>)"
