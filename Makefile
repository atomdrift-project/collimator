SHELL := /bin/bash
.PHONY: train evaluate explain inspect errors scan traits thresholds benchmark build-splits experiment ablate demo-db test lint clean deploy verify-xgboost-ars verify-litmus venv help fixture

VENV_DIR ?= .venv
PYTHON ?= $(VENV_DIR)/bin/python
DB ?= postgres://hopper@localhost:5432/hopper
OUT_DIR ?= out
LOG_DIR ?= $(OUT_DIR)/logs
SAMPLE ?=
FILE ?=
CLEAVE ?= cleave
DEMO_DB ?= out/demo.db
WORKERS ?=
EXP_WORKERS ?= $(WORKERS)
WORKERS_ARG := $(if $(WORKERS),--workers $(WORKERS),)
EXP_WORKERS_ARG := $(if $(EXP_WORKERS),--workers $(EXP_WORKERS),)
SEED ?= 42
EXP_TRAIN_SAMPLES ?= 120000
EXP_MAX_TEST_SAMPLES ?= 30000
EXP_FOLDS ?= 2
EXP_ESTIMATORS ?= 250
EXP_MAX_DEPTH ?= 14
EXP_LEARNING_RATE ?= 0.05
EXP_EARLY_STOPPING ?= 100
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
EXP_MIN_SAMPLE_SCORE ?= 3
# N-gram tuning: path depth (0=full, 2/3/4=truncated) and min crit (0=all, 3=notable+)
EXP_NGRAM_PATH_DEPTH ?= 0
EXP_NGRAM_MIN_CRIT ?= 3
EXP_TAXONOMY_FEATURES ?= 0
EXP_EXTENDED_METRICS ?= 1
EXP_DISABLE_FEATURE_GROUPS ?= clusters
# packaged_capability compute mode: zero | chars | tokens | paths | findings
EXP_PACKAGED_CAPABILITY_MODE ?= paths
# Experiment data cache directory. When set, corpus selections and extracted
# matrices are cached to disk so repeated experiments skip expensive DB scans.
EXP_CACHE_DIR ?= out/cache
TRAIN_MIN_MALWARE_SCORE ?= 0
TRAIN_SILENT_PACKER_SIGNAL ?= 0
TRAIN_MTIME_KURTOSIS ?= 0
TRAIN_AIR_GAP_SIGNAL ?= 1
TRAIN_EXTREME_FEATURES ?= 1
TRAIN_ANACHRONISTIC_INJECTION ?=
TRAIN_CODE_ENTROPY_SPIKE ?=
TRAIN_FOREIGN_BINARY_SIGNAL ?=
TRAIN_EXTENSION_MISMATCH_SIGNAL ?=
TRAIN_HOSTILE_FINDING_DENSITY ?=
TRAIN_HOSTILE_DEPTH_WEIGHT ?=
TRAIN_FILETYPE_INTERACTIONS ?= 0
TRAIN_BLINDFOLD ?= 1
TRAIN_SCORE_WEIGHTED_TRAITS ?= 1
TRAIN_SOFT_PRESENCE ?= 1
TRAIN_REPETITION_PENALTY_FEATURES ?= 1
TRAIN_FILE_SEVERITY_DISTRIBUTION ?= 1
TRAIN_HOSTILE_WEIGHTED_DENSITY ?= 1
TRAIN_HOSTILE_ESCALATION_FEATURES ?= 1
TRAIN_SUSPICIOUS_BREADTH_DENSITY ?= 1
TRAIN_STRUCT_FILE_RISK_COVERAGE ?= 1
TRAIN_MIN_SAMPLE_SCORE ?= 3
TRAIN_NGRAM_PATH_DEPTH ?= 0
TRAIN_NGRAM_MIN_CRIT ?= 3
TRAIN_DISABLE_FEATURE_GROUPS ?= clusters
TRAIN_PACKAGED_CAPABILITY_MODE ?= paths
TRAIN_ESTIMATORS ?= 2000
TRAIN_MAX_DEPTH ?= 20
TRAIN_LEARNING_RATE ?= 0.02
TRAIN_EARLY_STOPPING ?= 100
TRAIN_BETA ?= 1.25
ALLOWED_FEATURES ?= src/collimator/allowed_features.json

# Build optional train hyperparameter flags (only passed if set)
_TRAIN_FLAGS := $(if $(TRAIN_ESTIMATORS),--n-estimators $(TRAIN_ESTIMATORS)) \
                $(if $(TRAIN_MAX_DEPTH),--max-depth $(TRAIN_MAX_DEPTH)) \
                $(if $(TRAIN_LEARNING_RATE),--learning-rate $(TRAIN_LEARNING_RATE)) \
                $(if $(TRAIN_EARLY_STOPPING),--early-stopping-rounds $(TRAIN_EARLY_STOPPING)) \
                $(if $(TRAIN_BETA),--beta $(TRAIN_BETA))

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

train: venv check-db-fresh
	@mkdir -p $(LOG_DIR)
	COLLIMATOR_ALLOWED_FEATURES_FILE= \
	COLLIMATOR_SILENT_PACKER_SIGNAL=$(TRAIN_SILENT_PACKER_SIGNAL) \
	COLLIMATOR_MTIME_KURTOSIS=$(TRAIN_MTIME_KURTOSIS) \
	COLLIMATOR_AIR_GAP_SIGNAL=$(TRAIN_AIR_GAP_SIGNAL) \
	COLLIMATOR_EXTREME_FEATURES=$(TRAIN_EXTREME_FEATURES) \
	COLLIMATOR_ANACHRONISTIC_INJECTION=$(TRAIN_ANACHRONISTIC_INJECTION) \
	COLLIMATOR_CODE_ENTROPY_SPIKE=$(TRAIN_CODE_ENTROPY_SPIKE) \
	COLLIMATOR_FOREIGN_BINARY_SIGNAL=$(TRAIN_FOREIGN_BINARY_SIGNAL) \
	COLLIMATOR_EXTENSION_MISMATCH_SIGNAL=$(TRAIN_EXTENSION_MISMATCH_SIGNAL) \
	COLLIMATOR_HOSTILE_FINDING_DENSITY=$(TRAIN_HOSTILE_FINDING_DENSITY) \
	COLLIMATOR_HOSTILE_DEPTH_WEIGHT=$(TRAIN_HOSTILE_DEPTH_WEIGHT) \
	COLLIMATOR_FILETYPE_INTERACTIONS=$(TRAIN_FILETYPE_INTERACTIONS) \
	COLLIMATOR_BLINDFOLD=$(TRAIN_BLINDFOLD) \
	COLLIMATOR_SCORE_WEIGHTED_TRAITS=$(TRAIN_SCORE_WEIGHTED_TRAITS) \
	COLLIMATOR_SOFT_PRESENCE=$(TRAIN_SOFT_PRESENCE) \
	COLLIMATOR_REPETITION_PENALTY_FEATURES=$(TRAIN_REPETITION_PENALTY_FEATURES) \
	COLLIMATOR_FILE_SEVERITY_DISTRIBUTION=$(TRAIN_FILE_SEVERITY_DISTRIBUTION) \
	COLLIMATOR_HOSTILE_WEIGHTED_DENSITY=$(TRAIN_HOSTILE_WEIGHTED_DENSITY) \
	COLLIMATOR_HOSTILE_ESCALATION_FEATURES=$(TRAIN_HOSTILE_ESCALATION_FEATURES) \
	COLLIMATOR_SUSPICIOUS_BREADTH_DENSITY=$(TRAIN_SUSPICIOUS_BREADTH_DENSITY) \
	COLLIMATOR_STRUCT_FILE_RISK_COVERAGE=$(TRAIN_STRUCT_FILE_RISK_COVERAGE) \
	COLLIMATOR_DISABLE_FEATURE_GROUPS=$(TRAIN_DISABLE_FEATURE_GROUPS) \
	COLLIMATOR_PACKAGED_CAPABILITY_MODE=$(TRAIN_PACKAGED_CAPABILITY_MODE) \
	COLLIMATOR_MIN_SAMPLE_SCORE=$(TRAIN_MIN_SAMPLE_SCORE) \
	COLLIMATOR_NGRAM_PATH_DEPTH=$(TRAIN_NGRAM_PATH_DEPTH) \
	COLLIMATOR_NGRAM_MIN_CRIT=$(TRAIN_NGRAM_MIN_CRIT) \
	COLLIMATOR_EXTENDED_METRICS=1 \
	COLLIMATOR_ATTACK_FEATURES=1 \
	COLLIMATOR_CRIT_CATEGORY_NGRAMS=1 \
	COLLIMATOR_ATTACK_CODE_NGRAMS=1 \
	COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.01 \
	$(PYTHON) -u -m collimator train --db $(DB) --output $(OUT_DIR) $(WORKERS_ARG) --seed $(SEED) --min-malware-score $(TRAIN_MIN_MALWARE_SCORE) $(_TRAIN_FLAGS) 2>&1 | tee "$(LOG_DIR)/$$(date +%Y-%m-%dT%H-%M-%S)-train.log"

fixture: venv check-db
	@# Regenerate extraction_fixture.json and cross_language_fixture.json
	@# using the SAME feature toggles as make train, so env-gated features
	@# (BLINDFOLD, AIR_GAP_SIGNAL, EXTREME_FEATURES, etc.) are populated
	@# consistently with how the deployed model was trained.
	COLLIMATOR_SILENT_PACKER_SIGNAL=$(TRAIN_SILENT_PACKER_SIGNAL) \
	COLLIMATOR_MTIME_KURTOSIS=$(TRAIN_MTIME_KURTOSIS) \
	COLLIMATOR_AIR_GAP_SIGNAL=$(TRAIN_AIR_GAP_SIGNAL) \
	COLLIMATOR_EXTREME_FEATURES=$(TRAIN_EXTREME_FEATURES) \
	COLLIMATOR_ANACHRONISTIC_INJECTION=$(TRAIN_ANACHRONISTIC_INJECTION) \
	COLLIMATOR_CODE_ENTROPY_SPIKE=$(TRAIN_CODE_ENTROPY_SPIKE) \
	COLLIMATOR_FOREIGN_BINARY_SIGNAL=$(TRAIN_FOREIGN_BINARY_SIGNAL) \
	COLLIMATOR_EXTENSION_MISMATCH_SIGNAL=$(TRAIN_EXTENSION_MISMATCH_SIGNAL) \
	COLLIMATOR_HOSTILE_FINDING_DENSITY=$(TRAIN_HOSTILE_FINDING_DENSITY) \
	COLLIMATOR_HOSTILE_DEPTH_WEIGHT=$(TRAIN_HOSTILE_DEPTH_WEIGHT) \
	COLLIMATOR_FILETYPE_INTERACTIONS=$(TRAIN_FILETYPE_INTERACTIONS) \
	COLLIMATOR_BLINDFOLD=$(TRAIN_BLINDFOLD) \
	COLLIMATOR_SCORE_WEIGHTED_TRAITS=$(TRAIN_SCORE_WEIGHTED_TRAITS) \
	COLLIMATOR_SOFT_PRESENCE=$(TRAIN_SOFT_PRESENCE) \
	COLLIMATOR_REPETITION_PENALTY_FEATURES=$(TRAIN_REPETITION_PENALTY_FEATURES) \
	COLLIMATOR_FILE_SEVERITY_DISTRIBUTION=$(TRAIN_FILE_SEVERITY_DISTRIBUTION) \
	COLLIMATOR_HOSTILE_WEIGHTED_DENSITY=$(TRAIN_HOSTILE_WEIGHTED_DENSITY) \
	COLLIMATOR_HOSTILE_ESCALATION_FEATURES=$(TRAIN_HOSTILE_ESCALATION_FEATURES) \
	COLLIMATOR_SUSPICIOUS_BREADTH_DENSITY=$(TRAIN_SUSPICIOUS_BREADTH_DENSITY) \
	COLLIMATOR_STRUCT_FILE_RISK_COVERAGE=$(TRAIN_STRUCT_FILE_RISK_COVERAGE) \
	COLLIMATOR_DISABLE_FEATURE_GROUPS=$(TRAIN_DISABLE_FEATURE_GROUPS) \
	COLLIMATOR_PACKAGED_CAPABILITY_MODE=$(TRAIN_PACKAGED_CAPABILITY_MODE) \
	$(PYTHON) -m collimator fixture --db $(DB) --output $(OUT_DIR) \
		$(if $(wildcard $(OUT_DIR)/model.json),--model $(OUT_DIR)/model.json,) \
		$(if $(wildcard $(OUT_DIR)/feature_spec.json),--spec $(OUT_DIR)/feature_spec.json,)

evaluate: venv check-db
	$(PYTHON) -m collimator evaluate --db $(DB) --model $(OUT_DIR)/model.onnx --spec $(OUT_DIR)/feature_spec.json

explain: venv check-db
	$(PYTHON) -m collimator explain --db $(DB) --model $(OUT_DIR)/model.json --spec $(OUT_DIR)/feature_spec.json --output $(OUT_DIR)

inspect: venv check-db
ifndef SAMPLE
	$(error SAMPLE is required. Usage: make inspect DB=... SAMPLE=<sha256>)
endif
	$(PYTHON) -m collimator inspect --db $(DB) --sample $(SAMPLE) --model $(OUT_DIR)/model.json --spec $(OUT_DIR)/feature_spec.json

errors: venv check-db
	$(PYTHON) -m collimator errors --db $(DB) --model $(OUT_DIR)/model.json --spec $(OUT_DIR)/feature_spec.json

traits: venv check-db
	$(PYTHON) -m collimator traits --db $(DB)

thresholds: venv check-db
	$(PYTHON) -u -m collimator tune-thresholds --db $(DB) \
		--model $(OUT_DIR)/model.json \
		--spec $(OUT_DIR)/feature_spec.json \
		$(WORKERS_ARG) \
		--output $(OUT_DIR)/threshold_tuning.json

benchmark: venv check-db
	$(PYTHON) -m collimator benchmark --db $(DB) $(WORKERS_ARG) \
		$(if $(wildcard $(OUT_DIR)/model.json),--model $(OUT_DIR)/model.json,) \
		$(if $(wildcard $(OUT_DIR)/feature_spec.json),--spec $(OUT_DIR)/feature_spec.json,)

build-splits: venv check-db
	$(PYTHON) -m collimator build-splits --db $(DB)

experiment: venv check-db
	@mkdir -p $(LOG_DIR)
	COLLIMATOR_ALLOWED_FEATURES_FILE= \
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
	COLLIMATOR_BLINDFOLD=$(EXP_BLINDFOLD) \
	COLLIMATOR_SCORE_WEIGHTED_TRAITS=$(EXP_SCORE_WEIGHTED_TRAITS) \
	COLLIMATOR_SOFT_PRESENCE=$(EXP_SOFT_PRESENCE) \
	COLLIMATOR_REPETITION_PENALTY_FEATURES=$(EXP_REPETITION_PENALTY_FEATURES) \
	COLLIMATOR_FILE_SEVERITY_DISTRIBUTION=$(EXP_FILE_SEVERITY_DISTRIBUTION) \
	COLLIMATOR_HOSTILE_WEIGHTED_DENSITY=$(EXP_HOSTILE_WEIGHTED_DENSITY) \
	COLLIMATOR_HOSTILE_ESCALATION_FEATURES=$(EXP_HOSTILE_ESCALATION_FEATURES) \
	COLLIMATOR_SUSPICIOUS_BREADTH_DENSITY=$(EXP_SUSPICIOUS_BREADTH_DENSITY) \
	COLLIMATOR_STRUCT_FILE_RISK_COVERAGE=$(EXP_STRUCT_FILE_RISK_COVERAGE) \
	COLLIMATOR_DISABLE_FEATURE_GROUPS=$(EXP_DISABLE_FEATURE_GROUPS) \
	COLLIMATOR_PACKAGED_CAPABILITY_MODE=$(EXP_PACKAGED_CAPABILITY_MODE) \
	COLLIMATOR_MIN_SAMPLE_SCORE=$(EXP_MIN_SAMPLE_SCORE) \
	COLLIMATOR_NGRAM_PATH_DEPTH=$(EXP_NGRAM_PATH_DEPTH) \
	COLLIMATOR_NGRAM_MIN_CRIT=$(EXP_NGRAM_MIN_CRIT) \
	COLLIMATOR_TAXONOMY_FEATURES=$(EXP_TAXONOMY_FEATURES) \
	COLLIMATOR_EXTENDED_METRICS=$(EXP_EXTENDED_METRICS) \
	COLLIMATOR_CRIT_CATEGORY_NGRAMS=1 \
	COLLIMATOR_ATTACK_CODE_NGRAMS=1 \
	$(PYTHON) -u -m collimator experiment --db $(DB) --output $(OUT_DIR) $(EXP_WORKERS_ARG) --seed $(SEED) \
		--train-samples $(EXP_TRAIN_SAMPLES) --max-test-samples $(EXP_MAX_TEST_SAMPLES) \
		--n-folds $(EXP_FOLDS) --n-estimators $(EXP_ESTIMATORS) --max-depth $(EXP_MAX_DEPTH) \
		--learning-rate $(EXP_LEARNING_RATE) --early-stopping-rounds $(EXP_EARLY_STOPPING) \
		--min-malware-score $(EXP_MIN_MALWARE_SCORE) \
		--beta $(EXP_BETA) \
		$(if $(EXP_CACHE_DIR),--cache-dir $(EXP_CACHE_DIR),) \
		2>&1 | tee "$(LOG_DIR)/$$(date +%Y-%m-%dT%H-%M-%S)-experiment$(EXP_TAG).log"

ablate: venv check-db
	@# Leave-one-group-out ablation using the same env vars + hyperparams as
	@# make train, so results reflect behavior at the layered v16 operating point.
	COLLIMATOR_ALLOWED_FEATURES_FILE= \
	COLLIMATOR_SILENT_PACKER_SIGNAL=$(TRAIN_SILENT_PACKER_SIGNAL) \
	COLLIMATOR_MTIME_KURTOSIS=$(TRAIN_MTIME_KURTOSIS) \
	COLLIMATOR_AIR_GAP_SIGNAL=$(TRAIN_AIR_GAP_SIGNAL) \
	COLLIMATOR_EXTREME_FEATURES=$(TRAIN_EXTREME_FEATURES) \
	COLLIMATOR_ANACHRONISTIC_INJECTION=$(TRAIN_ANACHRONISTIC_INJECTION) \
	COLLIMATOR_CODE_ENTROPY_SPIKE=$(TRAIN_CODE_ENTROPY_SPIKE) \
	COLLIMATOR_FOREIGN_BINARY_SIGNAL=$(TRAIN_FOREIGN_BINARY_SIGNAL) \
	COLLIMATOR_EXTENSION_MISMATCH_SIGNAL=$(TRAIN_EXTENSION_MISMATCH_SIGNAL) \
	COLLIMATOR_HOSTILE_FINDING_DENSITY=$(TRAIN_HOSTILE_FINDING_DENSITY) \
	COLLIMATOR_HOSTILE_DEPTH_WEIGHT=$(TRAIN_HOSTILE_DEPTH_WEIGHT) \
	COLLIMATOR_FILETYPE_INTERACTIONS=$(TRAIN_FILETYPE_INTERACTIONS) \
	COLLIMATOR_BLINDFOLD=$(TRAIN_BLINDFOLD) \
	COLLIMATOR_SCORE_WEIGHTED_TRAITS=$(TRAIN_SCORE_WEIGHTED_TRAITS) \
	COLLIMATOR_SOFT_PRESENCE=$(TRAIN_SOFT_PRESENCE) \
	COLLIMATOR_REPETITION_PENALTY_FEATURES=$(TRAIN_REPETITION_PENALTY_FEATURES) \
	COLLIMATOR_FILE_SEVERITY_DISTRIBUTION=$(TRAIN_FILE_SEVERITY_DISTRIBUTION) \
	COLLIMATOR_HOSTILE_WEIGHTED_DENSITY=$(TRAIN_HOSTILE_WEIGHTED_DENSITY) \
	COLLIMATOR_HOSTILE_ESCALATION_FEATURES=$(TRAIN_HOSTILE_ESCALATION_FEATURES) \
	COLLIMATOR_SUSPICIOUS_BREADTH_DENSITY=$(TRAIN_SUSPICIOUS_BREADTH_DENSITY) \
	COLLIMATOR_STRUCT_FILE_RISK_COVERAGE=$(TRAIN_STRUCT_FILE_RISK_COVERAGE) \
	COLLIMATOR_DISABLE_FEATURE_GROUPS=$(TRAIN_DISABLE_FEATURE_GROUPS) \
	COLLIMATOR_PACKAGED_CAPABILITY_MODE=$(TRAIN_PACKAGED_CAPABILITY_MODE) \
	COLLIMATOR_MIN_SAMPLE_SCORE=$(TRAIN_MIN_SAMPLE_SCORE) \
	COLLIMATOR_NGRAM_PATH_DEPTH=$(TRAIN_NGRAM_PATH_DEPTH) \
	COLLIMATOR_NGRAM_MIN_CRIT=$(TRAIN_NGRAM_MIN_CRIT) \
	COLLIMATOR_EXTENDED_METRICS=1 \
	COLLIMATOR_ATTACK_FEATURES=1 \
	COLLIMATOR_CRIT_CATEGORY_NGRAMS=1 \
	COLLIMATOR_ATTACK_CODE_NGRAMS=1 \
	COLLIMATOR_TRIGRAM_MAX_BENIGN_FRAC=0.01 \
	$(PYTHON) -m collimator ablate --db $(DB) $(WORKERS_ARG) --seed $(SEED) \
		--n-estimators $(TRAIN_ESTIMATORS) --max-depth $(TRAIN_MAX_DEPTH) \
		--learning-rate $(TRAIN_LEARNING_RATE) --early-stopping-rounds $(TRAIN_EARLY_STOPPING) \
		--beta $(TRAIN_BETA) --min-malware-score $(TRAIN_MIN_MALWARE_SCORE) \
		--n-folds $(or $(ABLATE_FOLDS),2) \
		$(if $(ABLATE_SAMPLES),--train-samples $(ABLATE_SAMPLES),) \
		$(if $(ABLATE_TEST_SAMPLES),--max-test-samples $(ABLATE_TEST_SAMPLES),) \
		$(if $(ABLATE_GROUPS),--groups $(ABLATE_GROUPS),) \
		$(if $(ABLATE_OUTPUT),--output $(ABLATE_OUTPUT),)

demo-db: venv
	$(PYTHON) -m collimator demo-db --output $(DEMO_DB) --seed $(SEED)

scan: venv
ifndef FILE
	$(error FILE is required. Usage: make scan FILE=/path/to/binary)
endif
	$(PYTHON) -m collimator scan $(FILE) --model $(OUT_DIR)/model.json --spec $(OUT_DIR)/feature_spec.json --cleave $(CLEAVE) $(if $(DB),--db $(DB),)

test: venv
	$(VENV_DIR)/bin/pip install pytest
	$(PYTHON) -m pytest tests/ -v

lint: venv
	$(VENV_DIR)/bin/pip install ruff mypy
	$(VENV_DIR)/bin/ruff check src/ tests/
	$(VENV_DIR)/bin/mypy src/collimator/

MODEL_VERSION ?= $(shell $(PYTHON) -c "from collimator.features import FeatureSpec; print(FeatureSpec().version)")
MODELS_DIR ?= ../litmus-models/scan-v$(MODEL_VERSION)
XGBOOST_ARS_DIR ?= ../xgboost-ars

LITMUS_DIR ?= ../litmus

deploy: verify-xgboost-ars verify-litmus
	@# Stage to a temp dir first — only promote to MODELS_DIR after all
	@# post-deploy checks pass. This prevents partial/broken deploys.
	$(eval _STAGE := $(shell mktemp -d))
	cp $(OUT_DIR)/model.json $(_STAGE)/model.json
	cp $(OUT_DIR)/model.onnx $(_STAGE)/model.onnx
	cp $(OUT_DIR)/feature_spec.json $(_STAGE)/feature_spec.json
	cp $(OUT_DIR)/evaluation.json $(_STAGE)/evaluation.json
	@test -f $(OUT_DIR)/extraction_fixture.json || { rm -rf $(_STAGE); echo "error: extraction_fixture.json not found"; exit 1; }
	cp $(OUT_DIR)/extraction_fixture.json $(_STAGE)/extraction_fixture.json
	@$(PYTHON) -c "import json; e=json.load(open('$(OUT_DIR)/evaluation.json')); r=e.get('recommended_thresholds',{}); json.dump({k:v for k,v in r.items() if v is not None}, open('$(_STAGE)/config.json','w'), indent=2); print('  config.json: ' + ', '.join(f'{k}={v:.6f}' for k,v in r.items() if v is not None))"
	@echo "Running litmus deployed-model compatibility checks against staged copy..."
	cd $(LITMUS_DIR) && LITMUS_MODELS_DIR=$(_STAGE) cargo test --release --test feature_spec || { rm -rf $(_STAGE); exit 1; }
	cd $(LITMUS_DIR) && LITMUS_MODELS_DIR=$(_STAGE) cargo test --release --test extraction_parity || { rm -rf $(_STAGE); exit 1; }
	@# All checks passed — promote atomically.
	@mkdir -p $(MODELS_DIR)
	rm -rf $(MODELS_DIR).old 2>/dev/null; mv $(MODELS_DIR) $(MODELS_DIR).old 2>/dev/null || true
	mv $(_STAGE) $(MODELS_DIR)
	rm -rf $(MODELS_DIR).old 2>/dev/null || true
	@echo "litmus: all deploy checks passed"
	@echo "Deployed to $(MODELS_DIR)"

.PHONY: verify-xgboost-ars
verify-xgboost-ars:
	@test -d $(XGBOOST_ARS_DIR) || { echo "error: $(XGBOOST_ARS_DIR) does not exist"; exit 1; }
	@echo "Running xgboost-ars tests..."
	cd $(XGBOOST_ARS_DIR) && cargo test --release
	@echo "xgboost-ars: all tests passed"

.PHONY: verify-litmus
verify-litmus:
	@test -d $(LITMUS_DIR) || { echo "error: $(LITMUS_DIR) does not exist"; exit 1; }
	@test -f $(OUT_DIR)/extraction_fixture.json || { echo "error: $(OUT_DIR)/extraction_fixture.json not found — run make train first"; exit 1; }
	@echo "Running litmus feature-extraction parity tests..."
	@mkdir -p $(LITMUS_DIR)/tests/fixtures
	cp $(OUT_DIR)/extraction_fixture.json $(LITMUS_DIR)/tests/fixtures/extraction_fixture.json
	cd $(LITMUS_DIR) && LITMUS_MODELS_DIR=$(abspath $(OUT_DIR)) cargo test --release --test extraction_parity
	@echo "litmus: extraction parity tests passed"

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
	@echo "  thresholds         Tune suspicious/hostile thresholds on the full corpus"
	@echo "  benchmark          Measure feature extraction & inference latency"
	@echo "  build-splits       Pre-compute data splits in DB"
	@echo "  demo-db            Create a small SQLite DB for testing"
	@echo "  test               Run unit tests"
	@echo "  deploy             Copy model artifacts to ../litmus-models"
	@echo ""
	@echo "Options:"
	@echo "  DB=url             Hopper database DSN"
	@echo "  OUT_DIR=path       Output directory (default: out)"
	@echo "  WORKERS=n          Parallel extraction workers (default: auto = physical cores)"
	@echo "  EXP_TRAIN_SAMPLES=n   Experiment train rows (default: 120000)"
	@echo "  EXP_MAX_TEST_SAMPLES=n  Cap test set via reservoir (0=full, default: 30000)"
	@echo "  EXP_FOLDS=n           Experiment CV folds (default: 2)"
	@echo "  EXP_ESTIMATORS=n      Experiment max trees (default: 1000)"
	@echo "  MODELS_DIR=path    Deployment target (default: ../litmus-models/scan-v<version>)"
