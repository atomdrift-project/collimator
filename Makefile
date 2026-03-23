SHELL := /bin/bash
.PHONY: train evaluate explain inspect errors scan traits thresholds benchmark build-splits experiment ablate demo-db test lint clean deploy venv help

VENV_DIR ?= .venv
PYTHON ?= $(VENV_DIR)/bin/python
DB ?= $(HOME)/.local/share/cyclotron/cyclotron.db
OUT_DIR ?= out
LOG_DIR ?= $(OUT_DIR)/logs
SAMPLE ?=
FILE ?=
CLEAVE ?= cleave
DEMO_DB ?= out/demo.db
WORKERS ?= 0
EXP_WORKERS ?= 8
SEED ?= 42
EXP_TRAIN_SAMPLES ?= 150000
EXP_MAX_TEST_SAMPLES ?= 30000
EXP_FOLDS ?= 2
EXP_ESTIMATORS ?= 600
EXP_MAX_DEPTH ?= 10
EXP_LEARNING_RATE ?= 0.02
EXP_EARLY_STOPPING ?= 100
TRAIN_ESTIMATORS ?=
TRAIN_MAX_DEPTH ?=
TRAIN_LEARNING_RATE ?=
TRAIN_EARLY_STOPPING ?=

# Build optional train hyperparameter flags (only passed if set)
_TRAIN_FLAGS := $(if $(TRAIN_ESTIMATORS),--n-estimators $(TRAIN_ESTIMATORS)) \
                $(if $(TRAIN_MAX_DEPTH),--max-depth $(TRAIN_MAX_DEPTH)) \
                $(if $(TRAIN_LEARNING_RATE),--learning-rate $(TRAIN_LEARNING_RATE)) \
                $(if $(TRAIN_EARLY_STOPPING),--early-stopping-rounds $(TRAIN_EARLY_STOPPING))

# Validate DB is set for targets that need it
check-db:
ifndef DB
	$(error DB is required. Usage: make train DB=/path/to/cyclotron.db)
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
	$(PYTHON) -u -m collimator train --db $(DB) --output $(OUT_DIR) --workers $(WORKERS) --seed $(SEED) $(_TRAIN_FLAGS) 2>&1 | tee "$(LOG_DIR)/$$(date +%Y-%m-%dT%H-%M-%S)-train.log"

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
	$(PYTHON) -u -m collimator experiment --db $(DB) --output $(OUT_DIR) --workers $(EXP_WORKERS) --seed $(SEED) \
		--train-samples $(EXP_TRAIN_SAMPLES) --max-test-samples $(EXP_MAX_TEST_SAMPLES) \
		--n-folds $(EXP_FOLDS) --n-estimators $(EXP_ESTIMATORS) --max-depth $(EXP_MAX_DEPTH) \
		--learning-rate $(EXP_LEARNING_RATE) --early-stopping-rounds $(EXP_EARLY_STOPPING) 2>&1 | tee "$(LOG_DIR)/$$(date +%Y-%m-%dT%H-%M-%S)-experiment.log"

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

MODELS_DIR ?= ../litmus-models/v1/default

deploy:
	@test -d $(MODELS_DIR) || { echo "error: $(MODELS_DIR) does not exist"; exit 1; }
	cp $(OUT_DIR)/model.json $(MODELS_DIR)/model.json
	cp $(OUT_DIR)/model.onnx $(MODELS_DIR)/model.onnx
	cp $(OUT_DIR)/feature_spec.json $(MODELS_DIR)/feature_spec.json
	@echo "Deployed to $(MODELS_DIR)"

clean:
	rm -rf $(OUT_DIR) $(VENV_DIR) src/*.egg-info __pycache__ .mypy_cache .pytest_cache

help:
	@echo "Collimator - ML Training Pipeline for Malware Detection"
	@echo ""
	@echo "Training:"
	@echo "  make train DB=...                  Train model and export to out/"
	@echo "  make evaluate DB=...               Evaluate existing model"
	@echo "  make explain DB=...                SHAP feature importance analysis"
	@echo ""
	@echo "Debugging:"
	@echo "  make inspect DB=... SAMPLE=<sha>   Inspect a single sample (features + SHAP)"
	@echo "  make errors DB=...                 Show misclassified samples"
	@echo "  make traits DB=...                 Show trait-level prevalence / false-positive stats"
	@echo "  make thresholds DB=...             Show confidence thresholds for accuracy targets"
	@echo "  make benchmark DB=...              Benchmark extraction, training, and inference"
	@echo "  make build-splits DB=...           Rebuild grouped external-test split cache"
	@echo "  make experiment DB=...             Fast experiment with full external test evaluation"
	@echo "  make ablate DB=...                 Run leave-one-group-out feature ablations"
	@echo "  make demo-db                       Create a small synthetic demo database"
	@echo "  make scan FILE=/path/to/binary     Score a live file via cleave + model"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy                        Copy model artifacts to ../litmus-models"
	@echo ""
	@echo "Development:"
	@echo "  make test                          Run tests"
	@echo "  make lint                          Run ruff + mypy"
	@echo "  make venv                          Create virtual environment"
	@echo "  make clean                         Remove build artifacts"
	@echo ""
	@echo "Configuration:"
	@echo "  DB=path         Path to cyclotron SQLite database (default: $$HOME/.local/share/cyclotron/cyclotron.db)"
	@echo "  OUT_DIR=path    Output directory (default: out)"
	@echo "  LOG_DIR=path    Text log directory (default: out/logs)"
	@echo "  WORKERS=n       Feature extraction workers (default: 0=auto)"
	@echo "  EXP_WORKERS=n   Experiment workers (default: 1)"
	@echo "  SEED=n          Random seed for training/demo generation (default: 42)"
	@echo "  EXP_TRAIN_SAMPLES=n   Experiment train rows (default: 75000)"
	@echo "  EXP_MAX_TEST_SAMPLES=n  Cap test set via reservoir (0=full, default: 30000)"
	@echo "  EXP_FOLDS=n           Experiment CV folds (default: 2)"
	@echo "  EXP_ESTIMATORS=n      Experiment max trees (default: 220)"
	@echo "  SAMPLE=sha256   SHA256 (or prefix) for inspect"
	@echo "  FILE=path       File path for scan"
	@echo "  CLEAVE=path     Path to cleave binary (default: cleave)"
	@echo "  DEMO_DB=path    Output path for make demo-db (default: out/demo.db)"
	@echo "  MODELS_DIR=path Deployment target (default: ../litmus-models/v1/default)"

# BEGIN: lint-install .
# http://github.com/codeGROOVE-dev/lint-install

.PHONY: lint
lint: _lint

LINT_ARCH := $(shell uname -m)
LINT_OS := $(shell uname)
LINT_OS_LOWER := $(shell echo $(LINT_OS) | tr '[:upper:]' '[:lower:]')
LINT_ROOT := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# shellcheck and hadolint lack arm64 native binaries: rely on x86-64 emulation
ifeq ($(LINT_OS),Darwin)
	ifeq ($(LINT_ARCH),arm64)
		LINT_ARCH=x86_64
	endif
endif

LINTERS :=
FIXERS :=

SHELLCHECK_VERSION ?= v0.11.0
SHELLCHECK_BIN := $(LINT_ROOT)/out/linters/shellcheck-$(SHELLCHECK_VERSION)-$(LINT_ARCH)
$(SHELLCHECK_BIN):
	mkdir -p $(LINT_ROOT)/out/linters
	curl -sSfL -o $@.tar.xz https://github.com/koalaman/shellcheck/releases/download/$(SHELLCHECK_VERSION)/shellcheck-$(SHELLCHECK_VERSION).$(LINT_OS_LOWER).$(LINT_ARCH).tar.xz \
		|| echo "Unable to fetch shellcheck for $(LINT_OS)/$(LINT_ARCH): falling back to locally install"
	test -f $@.tar.xz \
		&& tar -C $(LINT_ROOT)/out/linters -xJf $@.tar.xz \
		&& mv $(LINT_ROOT)/out/linters/shellcheck-$(SHELLCHECK_VERSION)/shellcheck $@ \
		|| printf "#!/usr/bin/env shellcheck\n" > $@
	chmod u+x $@

LINTERS += shellcheck-lint
shellcheck-lint: $(SHELLCHECK_BIN)
	$(SHELLCHECK_BIN) $(shell find . -name "*.sh")

FIXERS += shellcheck-fix
shellcheck-fix: $(SHELLCHECK_BIN)
	$(SHELLCHECK_BIN) $(shell find . -name "*.sh") -f diff | { read -t 1 line || exit 0; { echo "$$line" && cat; } | git apply -p2; }

YAMLLINT_VERSION ?= 1.37.1
YAMLLINT_ROOT := $(LINT_ROOT)/out/linters/yamllint-$(YAMLLINT_VERSION)
YAMLLINT_BIN := $(YAMLLINT_ROOT)/dist/bin/yamllint
$(YAMLLINT_BIN):
	mkdir -p $(LINT_ROOT)/out/linters
	rm -rf $(LINT_ROOT)/out/linters/yamllint-*
	curl -sSfL https://github.com/adrienverge/yamllint/archive/refs/tags/v$(YAMLLINT_VERSION).tar.gz | tar -C $(LINT_ROOT)/out/linters -zxf -
	cd $(YAMLLINT_ROOT) && pip3 install --target dist . || pip install --target dist .

LINTERS += yamllint-lint
yamllint-lint: $(YAMLLINT_BIN)
	PYTHONPATH=$(YAMLLINT_ROOT)/dist $(YAMLLINT_ROOT)/dist/bin/yamllint .

BIOME_VERSION ?= 2.3.8
BIOME_BIN := $(LINT_ROOT)/out/linters/biome-$(BIOME_VERSION)-$(LINT_ARCH)
BIOME_CONFIG := $(LINT_ROOT)/biome.json

# Map architecture names for Biome downloads
BIOME_ARCH := $(LINT_ARCH)
ifeq ($(LINT_ARCH),x86_64)
	BIOME_ARCH := x64
endif

$(BIOME_BIN):
	mkdir -p $(LINT_ROOT)/out/linters
	rm -rf $(LINT_ROOT)/out/linters/biome-*
	curl -sSfL -o $@ https://github.com/biomejs/biome/releases/download/%40biomejs%2Fbiome%40$(BIOME_VERSION)/biome-$(LINT_OS_LOWER)-$(BIOME_ARCH) \
		|| echo "Unable to fetch biome for $(LINT_OS_LOWER)/$(BIOME_ARCH), falling back to local install"
	test -f $@ || printf "#!/usr/bin/env biome\n" > $@
	chmod u+x $@

LINTERS += biome-lint
biome-lint: $(BIOME_BIN)
	$(BIOME_BIN) check --config-path=$(BIOME_CONFIG) .

FIXERS += biome-fix
biome-fix: $(BIOME_BIN)
	$(BIOME_BIN) check --write --config-path=$(BIOME_CONFIG) .

.PHONY: _lint $(LINTERS)
_lint:
	@exit_code=0; \
	for target in $(LINTERS); do \
		$(MAKE) $$target || exit_code=1; \
	done; \
	exit $$exit_code

.PHONY: fix $(FIXERS)
fix:
	@exit_code=0; \
	for target in $(FIXERS); do \
		$(MAKE) $$target || exit_code=1; \
	done; \
	exit $$exit_code

# END: lint-install .
