SHELL := /bin/bash
.PHONY: train evaluate explain inspect errors scan traits thresholds benchmark build-splits experiment ablate demo-db test lint clean deploy verify-xgboost-native verify-litmus venv help

VENV_DIR ?= .venv
PYTHON ?= $(VENV_DIR)/bin/python
DB ?= postgres://hopper@localhost:5432/hopper
OUT_DIR ?= out
LOG_DIR ?= $(OUT_DIR)/logs
SAMPLE ?=
FILE ?=
CLEAVE ?= cleave
DEMO_DB ?= out/demo.db
WORKERS ?= 8
EXP_WORKERS ?= 8
SEED ?= 42
EXP_TRAIN_SAMPLES ?= 120000
EXP_MAX_TEST_SAMPLES ?= 30000
EXP_FOLDS ?= 2
EXP_ESTIMATORS ?= 1000
EXP_MAX_DEPTH ?= 16
EXP_LEARNING_RATE ?= 0.02
EXP_EARLY_STOPPING ?= 100
EXP_BETA ?= 2.0
EXP_MIN_MALWARE_SCORE ?= 9
# Ablation 2026-04-10: silent_packer (Exp 43) and mtime_kurtosis (Exp 44) were
# net-negative at 75k experiment scale. air_gap_signal (Exp 46) and the
# extreme-features bundle (Exps 48/49/54/55/56) are kept ON.
EXP_SILENT_PACKER_SIGNAL ?= 0
EXP_MTIME_KURTOSIS ?= 0
EXP_AIR_GAP_SIGNAL ?= 1
EXP_EXTREME_FEATURES ?= 1
TRAIN_MIN_MALWARE_SCORE ?= 9
TRAIN_SILENT_PACKER_SIGNAL ?= 0
TRAIN_MTIME_KURTOSIS ?= 0
TRAIN_AIR_GAP_SIGNAL ?= 1
TRAIN_EXTREME_FEATURES ?= 1
TRAIN_ESTIMATORS ?= 1000
TRAIN_MAX_DEPTH ?= 16
TRAIN_LEARNING_RATE ?= 0.02
TRAIN_EARLY_STOPPING ?= 100
TRAIN_BETA ?= 2.0
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

venv: $(VENV_DIR)/bin/activate

$(VENV_DIR)/bin/activate: requirements.txt
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r requirements.txt
	$(VENV_DIR)/bin/pip install -e .
	touch $(VENV_DIR)/bin/activate

train: venv check-db
	@mkdir -p $(LOG_DIR)
	COLLIMATOR_ALLOWED_FEATURES_FILE= \
	COLLIMATOR_SILENT_PACKER_SIGNAL=$(TRAIN_SILENT_PACKER_SIGNAL) \
	COLLIMATOR_MTIME_KURTOSIS=$(TRAIN_MTIME_KURTOSIS) \
	COLLIMATOR_AIR_GAP_SIGNAL=$(TRAIN_AIR_GAP_SIGNAL) \
	COLLIMATOR_EXTREME_FEATURES=$(TRAIN_EXTREME_FEATURES) \
	COLLIMATOR_DISABLE_FEATURE_GROUPS= \
	$(PYTHON) -u -m collimator train --db $(DB) --output $(OUT_DIR) --workers $(WORKERS) --seed $(SEED) --min-malware-score $(TRAIN_MIN_MALWARE_SCORE) $(_TRAIN_FLAGS) 2>&1 | tee "$(LOG_DIR)/$$(date +%Y-%m-%dT%H-%M-%S)-train.log"

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
	$(PYTHON) -m collimator thresholds --db $(DB) \
		--workers $(WORKERS) \
		$(if $(wildcard $(OUT_DIR)/model.json),--model $(OUT_DIR)/model.json,) \
		$(if $(wildcard $(OUT_DIR)/feature_spec.json),--spec $(OUT_DIR)/feature_spec.json,)

benchmark: venv check-db
	$(PYTHON) -m collimator benchmark --db $(DB) --workers $(WORKERS) \
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
	COLLIMATOR_DISABLE_FEATURE_GROUPS= \
	$(PYTHON) -u -m collimator experiment --db $(DB) --output $(OUT_DIR) --workers $(EXP_WORKERS) --seed $(SEED) \
		--train-samples $(EXP_TRAIN_SAMPLES) --max-test-samples $(EXP_MAX_TEST_SAMPLES) \
		--n-folds $(EXP_FOLDS) --n-estimators $(EXP_ESTIMATORS) --max-depth $(EXP_MAX_DEPTH) \
		--learning-rate $(EXP_LEARNING_RATE) --early-stopping-rounds $(EXP_EARLY_STOPPING) \
		--min-malware-score $(EXP_MIN_MALWARE_SCORE) \
		--beta $(EXP_BETA) 2>&1 | tee "$(LOG_DIR)/$$(date +%Y-%m-%dT%H-%M-%S)-experiment$(EXP_TAG).log"

ablate: venv check-db
	$(PYTHON) -m collimator ablate --db $(DB) --workers $(WORKERS) --seed $(SEED)

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
XGBOOST_NATIVE_DIR ?= ../xgboost-native

LITMUS_DIR ?= ../litmus

deploy: verify-xgboost-native verify-litmus
	@mkdir -p $(MODELS_DIR)
	cp $(OUT_DIR)/model.json $(MODELS_DIR)/model.json
	cp $(OUT_DIR)/model.onnx $(MODELS_DIR)/model.onnx
	cp $(OUT_DIR)/feature_spec.json $(MODELS_DIR)/feature_spec.json
	cp $(OUT_DIR)/evaluation.json $(MODELS_DIR)/evaluation.json
	@test -f $(OUT_DIR)/extraction_fixture.json || { echo "error: $(OUT_DIR)/extraction_fixture.json not found — run make train first"; exit 1; }
	cp $(OUT_DIR)/extraction_fixture.json $(MODELS_DIR)/extraction_fixture.json
	@$(PYTHON) -c "import json; e=json.load(open('$(OUT_DIR)/evaluation.json')); r=e.get('recommended_thresholds',{}); json.dump({k:v for k,v in r.items() if v is not None}, open('$(MODELS_DIR)/config.json','w'), indent=2); print('  config.json: ' + ', '.join(f'{k}={v:.6f}' for k,v in r.items() if v is not None))"
	@echo "Running litmus deployed-model compatibility checks..."
	cd $(LITMUS_DIR) && LITMUS_MODELS_DIR=$(abspath $(MODELS_DIR)) cargo test --release --test feature_spec
	cd $(LITMUS_DIR) && LITMUS_MODELS_DIR=$(abspath $(MODELS_DIR)) cargo test --release --test extraction_parity
	@echo "litmus: deployed model spec/ABI checks passed"
	@echo "Deployed to $(MODELS_DIR)"

.PHONY: verify-xgboost-native
verify-xgboost-native:
	@test -d $(XGBOOST_NATIVE_DIR) || { echo "error: $(XGBOOST_NATIVE_DIR) does not exist"; exit 1; }
	@test -f $(OUT_DIR)/reference.json || { echo "error: $(OUT_DIR)/reference.json not found — run make train first"; exit 1; }
	cp $(OUT_DIR)/reference.json $(XGBOOST_NATIVE_DIR)/tests/fixtures/reference.json
	@echo "Running xgboost-native tests to verify model agreement..."
	cd $(XGBOOST_NATIVE_DIR) && cargo test --release
	@echo "xgboost-native: all tests passed"

.PHONY: verify-litmus
verify-litmus:
	@test -d $(LITMUS_DIR) || { echo "error: $(LITMUS_DIR) does not exist"; exit 1; }
	@test -f $(OUT_DIR)/extraction_fixture.json || { echo "error: $(OUT_DIR)/extraction_fixture.json not found — run make train first"; exit 1; }
	@echo "Running litmus feature-extraction parity tests..."
	cd $(LITMUS_DIR) && $(PYTHON) -m collimator extraction-fixture --output extraction_fixture.json --count 50 --db $(DB)
	cp extraction_fixture.json $(LITMUS_DIR)/tests/fixtures/extraction_fixture.json
	cd $(LITMUS_DIR) && cargo test --release --test extraction_parity
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
	@echo "  thresholds         Show recommended confidence thresholds"
	@echo "  benchmark          Measure feature extraction & inference latency"
	@echo "  build-splits       Pre-compute data splits in DB"
	@echo "  demo-db            Create a small SQLite DB for testing"
	@echo "  test               Run unit tests"
	@echo "  deploy             Copy model artifacts to ../litmus-models"
	@echo ""
	@echo "Options:"
	@echo "  DB=url             Hopper database DSN"
	@echo "  OUT_DIR=path       Output directory (default: out)"
	@echo "  WORKERS=n          Parallel extraction workers (default: 8)"
	@echo "  EXP_TRAIN_SAMPLES=n   Experiment train rows (default: 120000)"
	@echo "  EXP_MAX_TEST_SAMPLES=n  Cap test set via reservoir (0=full, default: 30000)"
	@echo "  EXP_FOLDS=n           Experiment CV folds (default: 2)"
	@echo "  EXP_ESTIMATORS=n      Experiment max trees (default: 1000)"
	@echo "  MODELS_DIR=path    Deployment target (default: ../litmus-models/scan-v<version>)"
