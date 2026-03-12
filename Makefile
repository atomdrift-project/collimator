SHELL := /bin/bash
.PHONY: train evaluate explain inspect errors scan verify traits thresholds test lint clean deploy venv help

VENV_DIR ?= .venv
PYTHON ?= $(VENV_DIR)/bin/python
DB ?=
OUT_DIR ?= out
SAMPLE ?=
FILE ?=
CLEAVE ?= cleave

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
	$(PYTHON) -m collimator train --db $(DB) --output $(OUT_DIR) --cleave $(CLEAVE)

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
	$(PYTHON) -m collimator thresholds --db $(DB)

verify: venv
	$(PYTHON) -m collimator verify --model $(OUT_DIR)/model.json --spec $(OUT_DIR)/feature_spec.json --cleave $(CLEAVE)

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
	@echo "  make scan FILE=/path/to/binary     Score a live file via cleave + model"
	@echo "  make verify                        Verify model against testdata/ samples"
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
	@echo "  DB=path         Path to cyclotron SQLite database"
	@echo "  OUT_DIR=path    Output directory (default: out)"
	@echo "  SAMPLE=sha256   SHA256 (or prefix) for inspect"
	@echo "  FILE=path       File path for scan"
	@echo "  CLEAVE=path     Path to cleave binary (default: cleave)"
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
