SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c

# `_comma` lets us pass a literal comma into $(subst) where the function-call
# syntax would otherwise interpret it as an argument separator. Used to convert
# autocollie's csv-joined env values (e.g. `pe=0.5,zip=2.0`) back into the
# space-separated form make's $(foreach) expects.
_comma := ,
.PHONY: azoth-full-train azoth-fast-train azoth-publish-train _azoth-train azoth-general azoth-general-fold-a azoth-general-fold-b azoth-oof-merge-general evaluate explain inspect errors scan traits thresholds thresholds-refresh filetype-matrix elf-model-benchmark elf-route-optimization azoth-specialists azoth-specialists-fold-a azoth-specialists-fold-b azoth-prefill-specialist-features azoth-oof-route-scores azoth-calibrate azoth-diagnostics azoth-policies azoth-deploy azoth-deploy-final false-positives false-negatives near-false-positives near-false-negatives false-positives-archive false-negatives-archive near-false-positives-archive near-false-negatives-archive false-positives-triage false-negatives-triage near-false-positives-triage mislabeled-triage benchmark build-splits experiment ablate ablation demo-db test lint clean deploy verify-xgboost-ars verify-litmus venv help fixture repin azoth-clean-bundle autocollie-backfill-l3

VENV_DIR ?= .venv
PYTHON ?= $(VENV_DIR)/bin/python
DB ?= postgres://hopper@localhost:5432/hopper
MODEL ?= azoth
LEARNER ?= $(if $(filter azoth%,$(MODEL)),azoth,$(MODEL))
OUT_ROOT ?= out/models
OUT_DIR ?= $(if $(filter azoth,$(MODEL)),$(OUT_ROOT)/azoth/general,$(OUT_ROOT)/$(MODEL))
# Resolve the bundle's model file. Single-seed bundles ship `model.txt`
# directly under $(OUT_DIR); multi-seed bundles ship `models/seed_NN.txt`
# (the deployed Azoth general is 3-seed). Auto-pick whichever is on disk:
# `model.txt` if present, else the lowest-numbered seed, else fall back
# to the legacy `model.txt` name (callers get a clear FileNotFoundError
# rather than a misleading "missing arg" failure).
MODEL_FILE_EXT := $(if $(filter azoth,$(LEARNER)),txt,json)
MODEL_FILE ?= $(patsubst $(OUT_DIR)/%,%,$(or \
	$(wildcard $(OUT_DIR)/model.$(MODEL_FILE_EXT)), \
	$(firstword $(sort $(wildcard $(OUT_DIR)/models/seed_*.$(MODEL_FILE_EXT)))), \
	$(OUT_DIR)/model.$(MODEL_FILE_EXT)))
LOG_DIR ?= $(OUT_DIR)/logs
EXP_OUT_DIR ?= out/experiments/$(MODEL)
EXP_LOG_DIR ?= $(EXP_OUT_DIR)/logs
THRESHOLD_SCORES ?= $(OUT_DIR)/threshold_scores.npz
THRESHOLD_MAX_ID ?=
THRESHOLD_MAX_ID_ARG := $(if $(THRESHOLD_MAX_ID),--max-id $(THRESHOLD_MAX_ID),)
TOP_ERRORS ?= 250
SKIP ?= 0
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
# Run-isolation layout. Each fresh train allocates a directory under
# $(AZOTH_RUNS_ROOT)/ and writes the entire bundle there; on success
# azoth-publish atomically updates $(OUT_ROOT)/azoth to point at it.
# See scripts/azoth_publish_run.py and the azoth-run-new / azoth-publish
# targets below.
AZOTH_RUNS_ROOT ?= $(OUT_ROOT)/azoth-runs
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

# Feature allow-list: drops vocab entries where ALL produced columns fire on
# < 10 rows across a 671k-row training matrix. ~26% feature reduction, zero
# borderline drops (no feature firing on ≥10 malware was culled). cleave's
# allowed_features() reader (src/collimator/features.py:1306) returns None
# gracefully when the file is missing, so unsetting this is a safe no-op.
#
# The default points at the in-repo committed snapshot so fresh checkouts get
# the optimization without having to first run the build script. Regenerate
# from current corpus statistics with:
#   python scripts/azoth_feature_frequency_audit.py
#   python scripts/azoth_build_allowed_features.py --threshold 10 \
#       --output src/collimator/data/azoth_allowed_features_minfreq10.json
AZOTH_ALLOWED_FEATURES_FILE ?= src/collimator/data/azoth_allowed_features_minfreq10.json
export COLLIMATOR_ALLOWED_FEATURES_FILE := $(AZOTH_ALLOWED_FEATURES_FILE)
AZOTH_ROUTE_POLICIES_MD ?= $(AZOTH_ROOT)/route_policies.md
AZOTH_GLOBAL_POLICY_METRICS ?= $(AZOTH_ROOT)/global_policy_metrics.json
AZOTH_GLOBAL_POLICY_METRICS_MD ?= $(AZOTH_ROOT)/global_policy_metrics.md
AZOTH_ROUTED_METRICS_ARGS ?=
AZOTH_VALIDATE_ROUTED_METRICS_ARGS ?= --no-ci --no-stacked
AZOTH_VALIDATE_DIAGNOSTICS ?= 0
# Whether azoth-deploy emits route_diagnostics.{md,csv} and slice_metrics.{md,csv}.
# Diagnostics are human-debugging artifacts that nothing downstream consumes —
# regression check, policy search, and routed metrics all read directly from
# config.json + score_table.npz. Generating them on every deploy adds many
# minutes to the critical path for output most deploys never read. Off by
# default; run `make azoth-diagnostics` standalone when you actually need
# the report (the deployed bundle has everything it needs to regenerate them
# on demand). Set to 1/true/yes to opt back in.
AZOTH_DEPLOY_DIAGNOSTICS ?= 0
# Low-water-mark for the regression gate: a pinned reference bundle's
# route_policy_eval_oof.json that no future deploy is allowed to fall more
# than --lwm-tolerance below (per filetype). Lives outside $(AZOTH_ROOT)
# so azoth-clean-bundle doesn't wipe it. Captured via
# `make azoth-set-low-water-mark`. If the file doesn't exist the
# regression gate silently skips the LWM check, so this is fully
# opt-in — set the LWM once you have a deploy you want to lock in.
AZOTH_LOW_WATER_MARK_DIR ?= $(OUT_ROOT)/azoth_low_water_mark
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
AZOTH_SKIP_LITMUS_VALIDATE ?= 0
AZOTH_FEATURE_CACHE_DIR ?= out/cache/azoth-route-features
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
#
# 2026-05 update: the default is now 0 (single seed). Observed seed-to-seed
# variance on holdout is ~3pp F1 (verified on go/python/pe specialists from a
# k=3 fold run); averaging trims that to ~0.1-0.5pp at the headline recall,
# which is smaller than the per-pipeline-run noise our eval harness can
# resolve. Setting K=2 burns ~18 GPU hours per publish-train for an unverified
# fraction-of-a-percent of recall — not worth it now that we have honest
# OOF + recall-monotone floor + learned_blend in the pipeline. Bump back to
# K=2 if you measure a real regression on test partition; the infrastructure
# is in place to A/B this cleanly.
AZOTH_SPECIALIST_N_SEED_EXTRAS ?= 0
# OOF specialist training (fold-A / fold-B / route-score merge) doesn't ship
# the resulting bundles to deploy — only their OOF predictions get merged.
# Variance reduction from multi-seed averaging doesn't compound through the
# merge (the OOF prediction for each row already comes from a single fold
# model), so the extra seeds add training cost for no calibration benefit.
# Default to 0 extras (single seed) for OOF runs; override to 2 if you want
# parity with production training for an apples-to-apples comparison.
AZOTH_OOF_SEED_EXTRAS ?= 0
# Companion knob for the fold GENERAL trainings: the standard
# azoth_train_best.py invocation sets EXP_SEED_SEARCH_K=3 (train 3 seeds,
# ship the best). Fold bundles aren't shipped — only their OOF predictions
# merge into general/threshold_scores.npz — so the K-1 discarded seeds
# are pure waste during OOF. Production training keeps K=3.
AZOTH_OOF_SEED_SEARCH_K ?= 1
# Skip the per-specialist benchmark extract+score during fold training.
# benchmark.json's diagnostic metrics are only consumed by
# write_azoth_readmes (which only sees the production bundle), so the
# fold pair's benchmark passes are pure overhead. Saves ~30-60min per
# fold pair. Production specialists.json keeps its full metrics.
AZOTH_OOF_SKIP_BENCHMARK ?= 1
AZOTH_OOF_SKIP_BENCHMARK_ARG := $(if $(filter 1 true yes,$(AZOTH_OOF_SKIP_BENCHMARK)),--skip-benchmark,)
# Feature cache for cross-fold sharing. azoth-prefill-specialist-features
# pre-populates this directory; both fold trainings then read from it via
# --feature-cache-dir, skipping per-fold extraction. Set empty to disable.
AZOTH_SPECIALIST_FEATURE_CACHE_DIR ?= out/cache/azoth-route-features
AZOTH_SPECIALIST_FEATURE_CACHE_ARG := $(if $(AZOTH_SPECIALIST_FEATURE_CACHE_DIR),--feature-cache-dir $(AZOTH_SPECIALIST_FEATURE_CACHE_DIR),)
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
# Concurrent specialist trainings. Default 4 is a good fit for a typical
# many-core CPU host (16-128 cores) now that azoth_specialist_suite
# auto-caps each training's LightGBM threads at ``nproc // parallelism``.
# The total CPU footprint stays roughly fixed at the core count; bumping
# parallelism trades thread count per training for more concurrent
# trainings. Empirically (128-core box, observed in 2026-05) parallelism=4
# with 32-thread LightGBM jobs runs ~30% faster than parallelism=2 with
# 64-thread jobs, because LightGBM's intra-training synchronization
# overhead grows nonlinearly with thread count.
#
# Tune knobs:
#  * GPU training (``--device cuda``): set to 1 — GPU is the single
#    bottleneck, multiple concurrent jobs serialize on or fight for memory.
#  * Tiny boxes (< 8 cores): set to 1-2 so each training gets enough
#    threads to make progress.
#  * Very large boxes (256+ cores): try 8 — the auto thread cap still
#    keeps total workers near nproc, and more concurrency hides per-job
#    feature-extraction stalls.
AZOTH_SPECIALIST_PARALLELISM ?= 4
AZOTH_FILEGROUP_SCORE_FILTER ?= 0
AZOTH_FILEGROUP_SCORE_FILTER_ARG := $(if $(filter 1 true yes,$(AZOTH_FILEGROUP_SCORE_FILTER)),--filegroup-score-filter,)
SAMPLES_DIR ?= /data/samples
FALSE_POSITIVES_ARCHIVE ?= /tmp/false-positives.tgz
FALSE_NEGATIVES_ARCHIVE ?= /tmp/false-negatives.tgz
NEAR_FALSE_POSITIVES_ARCHIVE ?= /tmp/near-false-positives.tgz
NEAR_FALSE_NEGATIVES_ARCHIVE ?= /tmp/near-false-negatives.tgz
NEAR_FALSE_POSITIVES_TRIAGE_DIR ?= /tmp/near-false-positives
NEAR_FALSE_POSITIVES_TRIAGE_JSON ?= /tmp/near-false-positives.json
# {FALSE_POSITIVES,FALSE_NEGATIVES,MISLABELED}_TRIAGE_DIR are now derived
# inside the mislabeled-triage target block from SCOPE/LEVEL/SEVERITY so
# parallel triages under different scopes don't collide on /tmp paths.
SAMPLE ?=
FILE ?=
CLEAVE ?= cleave
DEMO_DB ?= out/demo.db
WORKERS ?=
EXP_WORKERS ?= $(WORKERS)
# Hard cap on the LightGBM thread pool a single `make experiment`
# invocation may grab. Without this, LightGBM uses every host core
# (n_jobs=-1) and concurrent screens thrash. Wired to COLLIMATOR_NUM_THREADS
# in the experiment recipe; collimator.train reads that env var and
# passes it through to LightGBM. Unset = no cap (host default).
EXP_LGBM_THREADS ?=
WORKERS_ARG := $(if $(WORKERS),--workers $(WORKERS),)
EXP_WORKERS_ARG := $(if $(EXP_WORKERS),--workers $(EXP_WORKERS),)
SEED ?= 42
# Training device. `auto` runs the pick_device() heuristic in
# src/collimator/model.py: it picks CUDA only when the workload is dense
# and large enough to benefit (LightGBM's CUDA path produces garbage on
# sparse high-dim inputs — constant-prediction models, SIGFPE in fit).
# Today every collimator route is sparse + narrow-N, so this resolves to
# CPU in practice. Override with DEVICE=cuda to force-test the GPU path
# or DEVICE=cpu to skip the heuristic.
DEVICE ?= auto
DROP_FEATURE_PREFIXES ?=
# Default azoth screening profile: a probe-sized run for bulk iteration.
# Confirm winners with a different seed, an explicit larger sample, or make azoth-full-train.
EXP_TRAIN_SAMPLES ?= 150000
EXP_MAX_TEST_SAMPLES ?= 40000
EXP_TOTAL_LIMIT ?= 0
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
EXP_MIN_CHILD_WEIGHT ?=
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
EXP_BETA ?= 2.0
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
# Previously hardcoded to 1 in the experiment recipe; now toggleable so
# autocollie can ablate them. Defaults preserve historical behavior.
EXP_ATTACK_FEATURES ?= 1
EXP_ATTACK_CODE_NGRAMS ?= 1
EXP_CRIT_CATEGORY_NGRAMS ?= 1
EXP_TIERED_CRIT_BIGRAMS ?= 1
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
# Batch 1 — cheap metric extracts (default off; autocollie can toggle each).
EXP_PE_FORMAT_FLAGS ?= 0
EXP_PE_TEMPORAL_ANOMALY ?= 0
EXP_TEXT_METRICS_FULL ?= 0
EXP_OVERLAY_SIGNAL ?= 0
EXP_METRIC_RATIO_FEATURES ?= 0
EXP_SIZE_NORMALIZED_METRICS ?= 0
EXP_NONSTANDARD_SECTION_SIGNAL ?= 0
EXP_LINE_LENGTH_BUCKETS ?= 0
# Batch 2 — allowlist + filter knobs (default off / no filter).
EXP_EXTENDED_METRICS_INCLUDE ?=
EXP_TOP_K_RISK_FILES_MIN_CRIT ?= 0
EXP_METRIC_CORRELATION_PAIRS ?=
EXP_KV_VALUE_SPLIT ?= 0
# Batch 3 — symbol & string n-grams (default off; trigram_min_freq is the
# symmetry knob and defaults to the previously-hardcoded value of 5).
EXP_SYMBOL_BIGRAMS ?= 0
EXP_SYMBOL_BIGRAM_MAX ?= 5000
EXP_SYMBOL_MIN_FREQ_BIGRAM ?= 10
EXP_SYMBOL_TRIGRAMS ?= 0
EXP_SYMBOL_TRIGRAM_MAX ?= 2000
EXP_SYMBOL_MIN_FREQ_TRIGRAM ?= 10
EXP_TRIGRAM_MIN_FREQ ?= 5
EXP_TIERED_CRIT_QUADGRAMS ?= 0
EXP_TIERED_QUADGRAM_PATH_DEPTH ?= 3
EXP_TIERED_QUADGRAM_MIN_CRIT ?= 3
EXP_TIERED_QUADGRAM_MAX ?= 5000
EXP_TIERED_QUADGRAM_MIN_FREQ ?= 5
# Batch 4 — trait & taxonomy extensions (default off / no overrides).
EXP_MBC_ID_VOCAB ?= 0
EXP_TRAIT_CONFIDENCE_MOMENTS ?= 0
EXP_TRAIT_ID_LEXICAL_DISTANCE ?= 0
EXP_DOCUMENT_OBFUSCATION_FEATURES ?= 0
EXP_TIERED_BIGRAM_BRANCH_MIN_CRIT ?=
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
	$(error DB is required. Usage: make azoth-full-train DB=postgres://hopper@localhost/hopper)
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

# azoth-{full,fast}-train: the two top-level "give me the latest best deployed
# model" entry points.  Both run the same chain — replay autocollie's
# highest-F1 historical run for general → retrain every specialist with
# autocollie's per-route best → calibrate + deploy — but at different
# fidelities.  Pick one explicitly; there is no `make azoth-train` shortcut
# because the speed/quality trade-off is real and worth being conscious of.
#
#   make azoth-full-train  — train on the full labeled corpus (~2M rows in
#     natural distribution).  ~7-8 hours end-to-end at K=3 seeds.  Use this
#     for deploy-bound retrains: the natural distribution preserves the
#     benign tail that 50/50 sampling discards, which is what determines
#     L3 (≤3 FP/M, the default operating point) threshold quality.
#
#   make azoth-fast-train  — train on a 600k 50/50-balanced sample.  ~5 hours
#     end-to-end at K=3 seeds.  Same fidelity autocollie's promote step uses
#     internally, so this matches what an autocollie auto-promote would have
#     produced.  Use for fast iteration; the candidate is still deployable.
#
# Both:
#   * Always retrain from scratch on current DB state (snapshot-pinned, no
#     model cache).
#   * K=3 multi-seed averaging.
#   * Run azoth-specialists + azoth-deploy on completion.
#   * Override individual knobs via DEPLOY_ESTIMATORS, DEPLOY_TRAIN_SAMPLES,
#     DEPLOY_MAX_TEST_SAMPLES if you need a custom profile.

DEPLOY_ESTIMATORS               ?= 400
DEPLOY_TRAIN_SAMPLES_FULL       ?= 0
DEPLOY_MAX_TEST_SAMPLES_FULL    ?= 0
DEPLOY_TRAIN_SAMPLES_FAST       ?= 600000
DEPLOY_MAX_TEST_SAMPLES_FAST    ?= 80000
# Default the fidelity for any standalone azoth-general / azoth-general-fold-*
# invocation to the FULL settings. azoth-publish-train and azoth-full-train
# still pass the _FULL values explicitly so this just covers the case where
# someone calls a sub-target directly (or via scripts/azoth_oof_pipeline.sh).
# Setting them empty (the prior behavior) would propagate "--train-samples ''"
# through to the experiment CLI and abort it with an empty-arg error.
DEPLOY_TRAIN_SAMPLES            ?= $(DEPLOY_TRAIN_SAMPLES_FULL)
DEPLOY_MAX_TEST_SAMPLES         ?= $(DEPLOY_MAX_TEST_SAMPLES_FULL)

azoth-full-train: venv check-db
	$(MAKE) _azoth-train \
		DEPLOY_TRAIN_SAMPLES=$(DEPLOY_TRAIN_SAMPLES_FULL) \
		DEPLOY_MAX_TEST_SAMPLES=$(DEPLOY_MAX_TEST_SAMPLES_FULL)

azoth-fast-train: venv check-db
	$(MAKE) _azoth-train \
		DEPLOY_TRAIN_SAMPLES=$(DEPLOY_TRAIN_SAMPLES_FAST) \
		DEPLOY_MAX_TEST_SAMPLES=$(DEPLOY_MAX_TEST_SAMPLES_FAST)

# azoth-publish-train: publication-grade k=2 out-of-fold calibration.
#
# The weekly default (azoth-full-train) calibrates on dev only — ~150k
# benigns, which puts every hostile L0..L9 below data resolution at 95%
# CI. This target instead runs k=2 OOF: two fold-A/B trainings + a final
# training, then combines fold-A's predictions on fold-1 rows with
# fold-B's predictions on fold-0 rows into a single OOF threshold-score
# table covering ~2.4M benigns. The Clopper-Pearson floor drops from ~20
# FP/M to ~1.25 FP/M; L3 (q=3) becomes resolvable for the first time.
#
# Compute cost: ~3× weekly (two extra full trainings). Use for paper
# runs and quarterly publication-grade builds; weekly retrains stay on
# azoth-full-train.
#
# Steps:
#   1. Clean bundle slot.
#   2. Train fold A (with EXP_OOF_FOLD_EXCLUDE=0 — model trained on rows
#      whose oof_fold != 0, which makes its predictions on fold-0 rows OOF).
#      Stash to out/models/azoth.oof-fold-a/.
#   3. Train fold B (EXP_OOF_FOLD_EXCLUDE=1). Stash to out/models/azoth.oof-fold-b/.
#   4. Train final (no exclusion) — this is the deployed model.
#   5. Combine fold-A-on-fold-0 + fold-B-on-fold-1 predictions into the
#      general/threshold_scores.npz. Replaces the single-pass scoring step.
#   6. Calibrate using the OOF score table; --partition all means we use
#      the full OOF coverage, not just the dev byte-range filter.
#   7. Deploy.
#
# Note: only the GENERAL model gets OOF treatment in this iteration. The
# global FP/M budget is dominated by the general route's CP analysis, so
# unblocking that unlocks meaningful L3 thresholds for the deployed
# bundle. Per-route specialists keep their single-pass calibration —
# their own per-filetype CP floors are still volume-floored and that's
# documented in the cards.
azoth-publish-train: venv check-db
	@echo "azoth-publish-train: starting k=2 OOF run."
	@echo "  Old structure: 3× full _azoth-train (each ~28h with specialists)."
	@echo "  New structure: 3× azoth-general (~1h each, skip rescore for folds)"
	@echo "                 + 1× azoth-specialists (~27h, on final production general)."
	@echo "  Expected savings: ~2 days vs the pre-split flow."
	@# Step 1: train fold A — general only, with fold 0 excluded, no rescore.
	@echo "azoth-publish-train: training fold A (excluding OOF fold 0)"
	$(MAKE) azoth-general-fold-a \
		DEPLOY_TRAIN_SAMPLES=$(DEPLOY_TRAIN_SAMPLES_FULL) \
		DEPLOY_MAX_TEST_SAMPLES=$(DEPLOY_MAX_TEST_SAMPLES_FULL)
	@# Step 2: train fold B — general only, with fold 1 excluded, no rescore.
	@echo "azoth-publish-train: training fold B (excluding OOF fold 1)"
	$(MAKE) azoth-general-fold-b \
		DEPLOY_TRAIN_SAMPLES=$(DEPLOY_TRAIN_SAMPLES_FULL) \
		DEPLOY_MAX_TEST_SAMPLES=$(DEPLOY_MAX_TEST_SAMPLES_FULL)
	@# Step 3: train final production general (no fold exclusion). Rescore is
	@# deliberately skipped here too — azoth-oof-merge-general below
	@# overwrites threshold_scores with honest OOF probabilities, so the
	@# in-sample rescore would be wasted (and would briefly land a stale
	@# score table on disk between steps 3 and 4 if anything crashed).
	@echo "azoth-publish-train: training final production general"
	$(MAKE) azoth-general \
		AZOTH_GENERAL_SKIP_RESCORE=1 \
		DEPLOY_TRAIN_SAMPLES=$(DEPLOY_TRAIN_SAMPLES_FULL) \
		DEPLOY_MAX_TEST_SAMPLES=$(DEPLOY_MAX_TEST_SAMPLES_FULL)
	@# Step 4: combine fold predictions into honest OOF general probs.
	$(MAKE) azoth-oof-merge-general
	@# Step 5: train specialists ONCE on the production general. This was
	@# previously buried inside three rounds of _azoth-train (and thus ran
	@# three times); the fold runs threw two of those specialist trees
	@# straight into the bin.
	$(MAKE) azoth-specialists AZOTH_SPECIALIST_SKIP_EXISTING=0
	@# Step 6: deploy. --partition=all is intentional — OOF predictions
	@# cover all of train+dev, so we use the full coverage rather than
	@# restricting to dev byte-range.
	$(MAKE) azoth-deploy AZOTH_CALIBRATE_PARTITION=all
	@echo "azoth-publish-train: complete; OOF bundle deployed."
	@echo "azoth-publish-train: archived fold bundles at out/models/azoth.oof-fold-{a,b}/"

# azoth-general: train the general model at deploy fidelity, promote it
# into the source bundle slot, and rebuild threshold_scores against the
# fresh model.
#
# This is the GENERAL-ONLY half of what _azoth-train used to do, split
# out so the OOF-publish flow can train fold-A/-B GENERAL bundles
# without burning compute on specialists that get thrown away. See the
# refactored azoth-publish-train below.
#
# Three steps:
#   1. Train general at deploy fidelity (writes to out/experiments/azoth/).
#   2. Promote the freshly-trained general into the source bundle slot
#      (out/models/azoth/general/) so azoth-deploy actually picks it up —
#      `make experiment` writes to a different location than azoth-deploy
#      reads from, and without this step the deploy ships a stale general.
#   3. Rescore threshold_scores against the freshly-promoted model.
#
# Set AZOTH_GENERAL_SKIP_RESCORE=1 to skip step 3 — used by the fold
# variants below since azoth_oof_score.py does its own corpus-wide
# scoring after merging the two fold bundles, making this rescore a
# multi-hour wasted pass for fold builds.
azoth-general: venv check-db azoth-clean-bundle
	$(PYTHON) scripts/azoth_train_best.py \
		--runs-dir "$(AZOTH_AUTOCOLLIE_RUNS_DIR)" \
		--route general \
		--set DB=$(DB) \
		--set EXP_TRAIN_SAMPLES=$(DEPLOY_TRAIN_SAMPLES) \
		--set EXP_MAX_TEST_SAMPLES=$(DEPLOY_MAX_TEST_SAMPLES) \
		--set EXP_ESTIMATORS=$(DEPLOY_ESTIMATORS) \
		$(if $(AZOTH_GENERAL_SEED_SEARCH_K),--set EXP_SEED_SEARCH_K=$(AZOTH_GENERAL_SEED_SEARCH_K),) \
		$(if $(AZOTH_GENERAL_SEED_SEARCH_K),--set EXP_SAVE_ALL_SEEDS=0,) \
		$(if $(WORKERS),--set EXP_WORKERS=$(WORKERS),)
	@# Promote the freshly-trained general into the source bundle slot.
	@# `make experiment` wrote to out/experiments/azoth/{models/,model.txt,
	@# feature_spec.json}; copy whichever layout it used into the deployed
	@# location, replacing whatever was there. Atomic-ish: the per-file
	@# `cp` and `rm -rf` are sequenced so an interrupted run leaves the
	@# slot in a clean (older) state rather than half-overwritten.
	@# Promote from $(EXP_OUT_DIR) — NOT a hardcoded out/experiments/azoth.
	@# Hardcoding here used to silently break fold parallelism: both
	@# fold-A and fold-B wrote to the same path and clobbered each
	@# other's freshly-trained models. Honoring $(EXP_OUT_DIR) lets
	@# the fold targets point each invocation at its own workspace.
	@mkdir -p $(AZOTH_GENERAL_DIR)
	@if [ -d $(EXP_OUT_DIR)/models ]; then \
		rm -rf $(AZOTH_GENERAL_DIR)/models $(AZOTH_GENERAL_DIR)/model.txt $(AZOTH_GENERAL_DIR)/model.json; \
		cp -a $(EXP_OUT_DIR)/models $(AZOTH_GENERAL_DIR)/models; \
	elif [ -f $(EXP_OUT_DIR)/model.txt ]; then \
		rm -rf $(AZOTH_GENERAL_DIR)/models $(AZOTH_GENERAL_DIR)/model.txt; \
		cp -a $(EXP_OUT_DIR)/model.txt $(AZOTH_GENERAL_DIR)/model.txt; \
	else \
		echo "error: azoth_train_best did not produce a general model in $(EXP_OUT_DIR)/"; \
		exit 1; \
	fi
	cp -a $(EXP_OUT_DIR)/feature_spec.json $(AZOTH_GENERAL_DIR)/feature_spec.json
	@# Rebuild the general's threshold_scores cache against the freshly-
	@# promoted model. Without this, azoth-calibrate would consume a stale
	@# score table whose probabilities map to a previous model — calibrators
	@# and L0..L9 thresholds would be fit on the wrong score distribution.
	@# Picks model.txt for single-seed bundles, else the lowest-numbered
	@# seed_*.txt for multi-seed bundles (seed_42 by convention).
	@if [ "$(AZOTH_GENERAL_SKIP_RESCORE)" = "1" ]; then \
		echo "AZOTH_GENERAL_SKIP_RESCORE=1: skipping threshold_scores rescore"; \
	else \
		set -e; \
		if [ -f $(AZOTH_GENERAL_DIR)/model.txt ]; then \
		    seed_model=$(AZOTH_GENERAL_DIR)/model.txt; \
		else \
		    seed_model=$$(ls $(AZOTH_GENERAL_DIR)/models/seed_*.txt 2>/dev/null | sort | head -1); \
		fi; \
		[ -n "$$seed_model" ] || { echo "error: no general seed model found in $(AZOTH_GENERAL_DIR)"; exit 1; }; \
		echo "rescoring general against full labeled corpus -> $(AZOTH_GENERAL_SCORES)"; \
		$(PYTHON) -u -m collimator tune-thresholds --db $(DB) \
		    --model $$seed_model \
		    --spec $(AZOTH_GENERAL_DIR)/feature_spec.json \
		    $(WORKERS_ARG) \
		    --scores-cache $(AZOTH_GENERAL_SCORES) \
		    --refresh-cache \
		    --output $(AZOTH_GENERAL_DIR)/threshold_tuning.json; \
	fi

# Fold-aware general training. Each variant trains general with one OOF
# fold held out, then archives the bundle to azoth.oof-fold-{a,b}/ for
# later consumption by azoth-oof-merge-general. Skips the threshold_scores
# rescore — those scores get replaced by the OOF merge anyway, so doing it
# here is a multi-hour wasted pass.
#
# Why a separate target rather than a shell variable: the fold-A and
# fold-B bundles need DISTINCT on-disk locations (different stash dirs).
# A single parameterized target couldn't run both back-to-back without
# the second one overwriting the first's bundle slot.
azoth-general-fold-a: venv check-db
	@# Run training in a fold-specific workspace and deploy slot so that
	@# parallel folds (PARALLEL_FOLDS=1) don't race over EXP_OUT_DIR /
	@# AZOTH_ROOT. The EXP_CACHE_DIR is intentionally NOT fold-suffixed —
	@# corpus + matrix caches are content-hashed (oof_fold_exclude is in
	@# the key), so both folds can share that directory and benefit from
	@# cross-run cache hits.
	EXP_OOF_FOLD_EXCLUDE=0 $(MAKE) azoth-general \
		AZOTH_ROOT=$(OUT_ROOT)/azoth.oof-fold-a \
		EXP_OUT_DIR=out/experiments/azoth.oof-fold-a \
		AZOTH_GENERAL_SKIP_RESCORE=1 \
		AZOTH_GENERAL_SEED_SEARCH_K=$(AZOTH_OOF_SEED_SEARCH_K)
	@echo "fold-A bundle ready at $(OUT_ROOT)/azoth.oof-fold-a/"

azoth-general-fold-b: venv check-db
	EXP_OOF_FOLD_EXCLUDE=1 $(MAKE) azoth-general \
		AZOTH_ROOT=$(OUT_ROOT)/azoth.oof-fold-b \
		EXP_OUT_DIR=out/experiments/azoth.oof-fold-b \
		AZOTH_GENERAL_SKIP_RESCORE=1 \
		AZOTH_GENERAL_SEED_SEARCH_K=$(AZOTH_OOF_SEED_SEARCH_K)
	@echo "fold-B bundle ready at $(OUT_ROOT)/azoth.oof-fold-b/"

# Merge the two fold-trained general bundles into honest OOF probabilities.
# Reads from the stash dirs created by azoth-general-fold-{a,b}, writes
# the combined threshold_scores.npz that azoth-calibrate consumes. Pulled
# out of azoth-publish-train so it's individually rerunnable when only
# the merge needs refreshing.
azoth-oof-merge-general: venv check-db
	$(PYTHON) scripts/azoth_oof_score.py \
		--db $(DB) \
		--fold-a-bundle $(OUT_ROOT)/azoth.oof-fold-a \
		--fold-b-bundle $(OUT_ROOT)/azoth.oof-fold-b \
		--prod-bundle $(AZOTH_ROOT) \
		--output $(AZOTH_GENERAL_SCORES) \
		$(WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG)

# _azoth-train: shared body for the two named targets above.  Not a public
# entry point — pick azoth-full-train or azoth-fast-train explicitly.
#
# Calls azoth-general (which does train + promote + rescore), then trains
# specialists and deploys. The split lets fold-aware OOF training reuse
# the general half without the specialist+deploy tail.
_azoth-train: azoth-general
	$(MAKE) azoth-specialists AZOTH_SPECIALIST_SKIP_EXISTING=0
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
		--runs-dir "$(AZOTH_AUTOCOLLIE_RUNS_DIR)" \
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

# repin: drop the pinned snapshot_max_id so the next experiment-style
# invocation re-queries the live max(id). Chain it before the target you
# actually want to run, e.g.:
#
#   make repin azoth-full-train DB=...
#
# Make builds command-line goals left-to-right by default, so `repin` runs
# first, then the next target rebuilds the pin from the current DB.
# Prints the current pin (so you have a revert path) before clearing or
# re-setting. Pass PIN_TO=<id> to atomically replace the pin with a
# specific id (useful when reverting to the value an earlier `make repin`
# printed). Default behavior with no PIN_TO clears the pin so the next
# experiment re-queries max(id).
repin:
	@if [ -f $(EXP_CACHE_DIR)/snapshot_max_id.txt ]; then \
		echo "previous pin: $$(cat $(EXP_CACHE_DIR)/snapshot_max_id.txt) (revert with: make repin PIN_TO=$$(cat $(EXP_CACHE_DIR)/snapshot_max_id.txt))"; \
	else \
		echo "previous pin: (none)"; \
	fi
	@if [ -n "$(PIN_TO)" ]; then \
		mkdir -p $(EXP_CACHE_DIR); \
		echo "$(PIN_TO)" > $(EXP_CACHE_DIR)/snapshot_max_id.txt; \
		echo "set snapshot pin: $(EXP_CACHE_DIR)/snapshot_max_id.txt -> $(PIN_TO)"; \
	else \
		rm -f $(EXP_CACHE_DIR)/snapshot_max_id.txt; \
		echo "cleared snapshot pin: $(EXP_CACHE_DIR)/snapshot_max_id.txt (next invocation will re-query max(id))"; \
	fi

# azoth-clean-bundle: wipe regen-able deployed artifacts from the source
# bundle slot at $(AZOTH_ROOT). Caches under */cache/ are preserved (rebuilding
# feature matrices is expensive and they're keyed by snapshot+model anyway).
# Run before any retrain to guarantee no leftover seed_*.txt, calibrator.json,
# benchmark.json, etc. from a prior generation pollutes the new bundle.
#
# Categories cleaned:
#   - top-level deployed artifacts (config.json, score_table.npz, *.md, *.csv, *.json)
#   - per-route deployed artifacts (model.txt, feature_spec.json, calibrator.json,
#     benchmark.json, README.md, threshold_scores.npz, calibration_scores.npz,
#     threshold_tuning.json)
#   - per-route models/ subdirectories (catches multi-seed leftovers like
#     seed_42.txt + a stale seed_45.txt from an earlier K=4 run)
#
# Categories preserved:
#   - $(AZOTH_GENERAL_DIR)/cache/  (route feature matrices, snapshot-keyed)
#   - any sibling directories not matching the above patterns
azoth-clean-bundle:
	@# Single shell so the early-out actually skips the rest of the recipe.
	@# Each `@line` is its own subshell in make; a bare `exit 0` only exits
	@# its own line, not the recipe. Without this guard, fresh fold roots
	@# (where AZOTH_ROOT doesn't exist yet) hit `find` and fail.
	@set -e; \
	if [ ! -d $(AZOTH_ROOT) ]; then \
	    echo "azoth-clean-bundle: $(AZOTH_ROOT) does not exist; nothing to do"; \
	    exit 0; \
	fi; \
	echo "azoth-clean-bundle: wiping deployed artifacts under $(AZOTH_ROOT) (caches preserved)"; \
	find $(AZOTH_ROOT) -mindepth 1 -maxdepth 1 -type f \
	    \( -name '*.json' -o -name '*.md' -o -name '*.csv' -o -name '*.npz' \) -delete; \
	for d in $(AZOTH_ROOT)/general $(AZOTH_ROOT)/filegroups/* $(AZOTH_ROOT)/filetypes/*; do \
	    [ -d "$$d" ] || continue; \
	    rm -f "$$d"/model.txt "$$d"/model.json "$$d"/feature_spec.json \
	          "$$d"/calibrator.json "$$d"/benchmark.json "$$d"/README.md \
	          "$$d"/threshold_scores.npz "$$d"/calibration_scores.npz \
	          "$$d"/threshold_tuning.json; \
	    rm -rf "$$d"/models; \
	done

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
		--runs-dir "$(AZOTH_AUTOCOLLIE_RUNS_DIR)" \
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
	$(if $(AZOTH_AUTOCOLLIE_RUNS_DIR),\
		$(PYTHON) scripts/azoth_train_best.py \
			--runs-dir "$(AZOTH_AUTOCOLLIE_RUNS_DIR)" \
			--route general \
			--exec ,) \
	$(PYTHON) scripts/azoth_specialist_suite.py \
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
		--parallelism $(AZOTH_SPECIALIST_PARALLELISM) \
		--min-bad $(AZOTH_SPECIALIST_MIN_BAD) \
		--min-good $(AZOTH_SPECIALIST_MIN_GOOD) \
		$(foreach target,$(AZOTH_SPECIALIST_ONLY),--only $(target)) \
		$(foreach mask,$(AZOTH_SPECIALIST_MASK_SPEC),--mask-spec $(mask)) \
		$(foreach override,$(AZOTH_SPECIALIST_TRAIN_OVERRIDE),--train-override $(override)) \
		$(foreach env,$(AZOTH_SPECIALIST_FEATURE_ENV),--feature-env $(env)) \
		$(if $(AZOTH_AUTOCOLLIE_RUNS_DIR),--autocollie-best-runs-dir $(AZOTH_AUTOCOLLIE_RUNS_DIR),) \
		$(AZOTH_SPECIALIST_SKIP_EXISTING_ARG) \
		$(AZOTH_FILEGROUP_SCORE_FILTER_ARG) \
		$(AZOTH_SPECIALIST_FEATURE_CACHE_ARG) \
		$(if $(DEVICE),--device $(DEVICE),)

# Fold-aware specialist training for OOF score generation. Mirror of
# azoth-specialists with EXP_OOF_FOLD_EXCLUDE wired through (honored in
# azoth_specialist_suite._fetch_rows via _read_oof_exclude). Each fold
# bundle excludes one half of train+dev so the OTHER half can be scored
# OOF afterwards via azoth-oof-route-scores. Outputs go to azoth-fold-a/
# and azoth-fold-b/ so the production bundle under $(AZOTH_ROOT) is left
# alone — the deployed model stays single-fold; the fold bundles exist
# only to feed honest score merging downstream.
azoth-specialists-fold-a: venv check-db
	EXP_OOF_FOLD_EXCLUDE=0 $(PYTHON) scripts/azoth_train_best.py \
		--runs-dir "$(AZOTH_AUTOCOLLIE_RUNS_DIR)" \
		--route general \
		--exec $(PYTHON) scripts/azoth_specialist_suite.py \
		--db $(DB) \
		$(EXP_WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		--output-root $(OUT_ROOT)/azoth.oof-fold-a \
		--summary $(OUT_ROOT)/azoth.oof-fold-a/specialists.json \
		--general-dir $(OUT_ROOT)/azoth.oof-fold-a/general \
		--seed $(SEED) \
		--n-folds $(AZOTH_SPECIALIST_FOLDS) \
		--n-estimators $(AZOTH_SPECIALIST_ESTIMATORS) \
		--max-depth $(AZOTH_SPECIALIST_MAX_DEPTH) \
		--learning-rate $(AZOTH_SPECIALIST_LEARNING_RATE) \
		--early-stopping-rounds $(AZOTH_SPECIALIST_EARLY_STOPPING) \
		--num-leaves $(AZOTH_SPECIALIST_NUM_LEAVES) \
		--min-child-samples $(AZOTH_SPECIALIST_MIN_CHILD_SAMPLES) \
		--n-seed-extras $(AZOTH_OOF_SEED_EXTRAS) \
		--parallelism $(AZOTH_SPECIALIST_PARALLELISM) \
		--min-bad $(AZOTH_SPECIALIST_MIN_BAD) \
		--min-good $(AZOTH_SPECIALIST_MIN_GOOD) \
		$(foreach target,$(AZOTH_SPECIALIST_ONLY),--only $(target)) \
		$(foreach mask,$(AZOTH_SPECIALIST_MASK_SPEC),--mask-spec $(mask)) \
		$(foreach override,$(AZOTH_SPECIALIST_TRAIN_OVERRIDE),--train-override $(override)) \
		$(foreach env,$(AZOTH_SPECIALIST_FEATURE_ENV),--feature-env $(env)) \
		$(if $(AZOTH_AUTOCOLLIE_RUNS_DIR),--autocollie-best-runs-dir $(AZOTH_AUTOCOLLIE_RUNS_DIR),) \
		$(AZOTH_SPECIALIST_SKIP_EXISTING_ARG) \
		$(AZOTH_FILEGROUP_SCORE_FILTER_ARG) \
		$(AZOTH_OOF_SKIP_BENCHMARK_ARG) \
		$(AZOTH_SPECIALIST_FEATURE_CACHE_ARG) \
		$(if $(DEVICE),--device $(DEVICE),)

azoth-specialists-fold-b: venv check-db
	EXP_OOF_FOLD_EXCLUDE=1 $(PYTHON) scripts/azoth_train_best.py \
		--runs-dir "$(AZOTH_AUTOCOLLIE_RUNS_DIR)" \
		--route general \
		--exec $(PYTHON) scripts/azoth_specialist_suite.py \
		--db $(DB) \
		$(EXP_WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		--output-root $(OUT_ROOT)/azoth.oof-fold-b \
		--summary $(OUT_ROOT)/azoth.oof-fold-b/specialists.json \
		--general-dir $(OUT_ROOT)/azoth.oof-fold-b/general \
		--seed $(SEED) \
		--n-folds $(AZOTH_SPECIALIST_FOLDS) \
		--n-estimators $(AZOTH_SPECIALIST_ESTIMATORS) \
		--max-depth $(AZOTH_SPECIALIST_MAX_DEPTH) \
		--learning-rate $(AZOTH_SPECIALIST_LEARNING_RATE) \
		--early-stopping-rounds $(AZOTH_SPECIALIST_EARLY_STOPPING) \
		--num-leaves $(AZOTH_SPECIALIST_NUM_LEAVES) \
		--min-child-samples $(AZOTH_SPECIALIST_MIN_CHILD_SAMPLES) \
		--n-seed-extras $(AZOTH_OOF_SEED_EXTRAS) \
		--parallelism $(AZOTH_SPECIALIST_PARALLELISM) \
		--min-bad $(AZOTH_SPECIALIST_MIN_BAD) \
		--min-good $(AZOTH_SPECIALIST_MIN_GOOD) \
		$(foreach target,$(AZOTH_SPECIALIST_ONLY),--only $(target)) \
		$(foreach mask,$(AZOTH_SPECIALIST_MASK_SPEC),--mask-spec $(mask)) \
		$(foreach override,$(AZOTH_SPECIALIST_TRAIN_OVERRIDE),--train-override $(override)) \
		$(foreach env,$(AZOTH_SPECIALIST_FEATURE_ENV),--feature-env $(env)) \
		$(if $(AZOTH_AUTOCOLLIE_RUNS_DIR),--autocollie-best-runs-dir $(AZOTH_AUTOCOLLIE_RUNS_DIR),) \
		$(AZOTH_SPECIALIST_SKIP_EXISTING_ARG) \
		$(AZOTH_FILEGROUP_SCORE_FILTER_ARG) \
		$(AZOTH_OOF_SKIP_BENCHMARK_ARG) \
		$(AZOTH_SPECIALIST_FEATURE_CACHE_ARG) \
		$(if $(DEVICE),--device $(DEVICE),)

# Pre-build the per-route feature cache before fold-A / fold-B specialist
# training. Without this, each fold does its own extract_partitioned_from_db
# pass and the train+dev overlap (~88% of rows) gets extracted twice.
# Pre-fill extracts the union once and saves a fold-specific matrix under
# each fold's cache key, so both subsequent fold trainings hit the cache.
#
# Safe to run anytime — the worst case is a stale cache entry that
# fails its row-count check at load time and triggers re-extraction.
azoth-prefill-specialist-features: venv check-db
	$(PYTHON) scripts/azoth_prefill_specialist_features.py \
		--db $(DB) \
		--general-dir $(AZOTH_GENERAL_DIR) \
		--feature-cache-dir $(AZOTH_SPECIALIST_FEATURE_CACHE_DIR) \
		--min-bad $(AZOTH_SPECIALIST_MIN_BAD) \
		--min-good $(AZOTH_SPECIALIST_MIN_GOOD) \
		$(EXP_WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		$(if $(filter 1 true yes,$(AZOTH_FILEGROUP_SCORE_FILTER)),--filegroup-score-filter,) \
		$(foreach target,$(AZOTH_SPECIALIST_ONLY),--only $(target))

# Merge the two fold-trained specialist bundles into per-route OOF
# threshold_scores.npz files under $(AZOTH_ROOT)/oof_route_scores/. Pass
# --prod-root so test rows get scored with the deployed bundle (which
# never saw test rows at training time, so its predictions on them are
# legitimately OOS). The downstream calibrate-ensemble run then reads
# these files via --oof-route-scores-dir.
AZOTH_OOF_ROUTE_SCORES_DIR ?= $(AZOTH_ROOT)/oof_route_scores
azoth-oof-route-scores: venv check-db
	$(PYTHON) scripts/azoth_oof_score_routes.py \
		--db $(DB) \
		--fold-a-root $(OUT_ROOT)/azoth.oof-fold-a \
		--fold-b-root $(OUT_ROOT)/azoth.oof-fold-b \
		--prod-root $(AZOTH_ROOT) \
		--summary $(AZOTH_SPECIALISTS_SUMMARY) \
		--output-dir $(AZOTH_OOF_ROUTE_SCORES_DIR) \
		$(EXP_WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG)

# AZOTH_CALIBRATE_PARTITION selects which rows the calibrators and L0..L9
# threshold search see. Default 'dev' is the weekly methodology (dev-only,
# CP-aware budget acknowledging the volume floor). 'all' is for k=2 OOF
# publication runs where the general/threshold_scores.npz already covers
# train+dev OOF — no further filtering needed.
AZOTH_CALIBRATE_PARTITION ?= dev
# Concurrent route scoring. Same trade-offs as
# AZOTH_SPECIALIST_PARALLELISM — process-based, fan-out hits DB and CPU.
AZOTH_CALIBRATE_PARALLELISM ?= 2

# When AZOTH_USE_OOF_ROUTE_SCORES=1, pass --oof-route-scores-dir so the
# calibrator reads honest fold-merged specialist probs instead of running
# in-sample predict_proba. The flag is opt-in so the existing pipeline
# stays bit-for-bit unchanged when unset.
AZOTH_OOF_ROUTE_SCORES_ARG := $(if $(filter 1,$(AZOTH_USE_OOF_ROUTE_SCORES)),--oof-route-scores-dir $(AZOTH_OOF_ROUTE_SCORES_DIR),)

azoth-calibrate: venv check-db
	$(PYTHON) scripts/azoth_calibrate_ensemble.py \
		--db $(DB) \
		$(EXP_WORKERS_ARG) \
		--azoth-root $(AZOTH_ROOT) \
		--summary $(AZOTH_SPECIALISTS_SUMMARY) \
		--general-scores $(AZOTH_GENERAL_SCORES) \
		--output $(AZOTH_CONFIG) \
		--score-table $(AZOTH_SCORE_TABLE) \
		--partition $(AZOTH_CALIBRATE_PARTITION) \
		--parallelism $(AZOTH_CALIBRATE_PARALLELISM) \
		$(AZOTH_REFRESH_SCORES_ARG) \
		$(AZOTH_SKIP_LEVEL_CALIBRATION_ARG) \
		$(AZOTH_OOF_ROUTE_SCORES_ARG) \
		$(foreach route,$(AZOTH_REFRESH_ROUTE),--refresh-route $(route)) \
		--feature-cache-dir $(AZOTH_FEATURE_CACHE_DIR)
	@# Honest test-bucket evaluation: same dev-fit thresholds applied to
	@# the locked test partition. Output goes to $(AZOTH_ROOT)/test_metrics.json
	@# alongside (not overwriting) the deployed config.json. The second call
	@# hits the per-route calibration_scores.npz caches written above, so
	@# parallelism mainly helps the first invocation; no harm passing it here.
	$(PYTHON) scripts/azoth_calibrate_ensemble.py \
		--db $(DB) \
		$(EXP_WORKERS_ARG) \
		--azoth-root $(AZOTH_ROOT) \
		--summary $(AZOTH_SPECIALISTS_SUMMARY) \
		--general-scores $(AZOTH_GENERAL_SCORES) \
		--output $(AZOTH_CONFIG) \
		--score-table $(AZOTH_SCORE_TABLE) \
		--partition test \
		--parallelism $(AZOTH_CALIBRATE_PARALLELISM) \
		--apply-thresholds-from $(AZOTH_CONFIG) \
		--feature-cache-dir $(AZOTH_FEATURE_CACHE_DIR)

# azoth-set-low-water-mark pins the current deployed-bundle's
# route_policy_eval_oof.json as the low-water-mark for the regression
# gate. From this point on every deploy must keep per-filetype recall
# within --lwm-tolerance (default 0.9pp) of this snapshot, regardless
# of how the live deployed bundle drifts. Re-run this target whenever
# you want to advance the floor (e.g., after several deploys land
# stable improvements you want to lock in). Idempotent.
azoth-set-low-water-mark:
	@test -f "$(AZOTH_ROOT)/route_policy_eval_oof.json" || { \
	  echo "error: $(AZOTH_ROOT)/route_policy_eval_oof.json not found — run make azoth-deploy first"; \
	  exit 1; \
	}
	mkdir -p "$(AZOTH_LOW_WATER_MARK_DIR)"
	cp "$(AZOTH_ROOT)/route_policy_eval_oof.json" "$(AZOTH_LOW_WATER_MARK_DIR)/route_policy_eval_oof.json"
	@echo "low-water-mark pinned: $(AZOTH_LOW_WATER_MARK_DIR)/route_policy_eval_oof.json"
	@echo "  source: $(AZOTH_ROOT)/route_policy_eval_oof.json"
	@echo "  future deploys must stay within --lwm-tolerance of this snapshot."

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
# validator, and litmus parity unless AZOTH_SKIP_LITMUS_VALIDATE=1), but
# stops short of copying anything into $(AZOTH_DEPLOY_DIR). Used by
# autocollie's auto-promote path to vet a candidate bundle without touching
# the live deploy.
.PHONY: azoth-validate
azoth-validate: azoth-calibrate
	@test -f $(AZOTH_ROOT)/config.json || { echo "error: $(AZOTH_ROOT)/config.json not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/score_table.npz || { echo "error: $(AZOTH_ROOT)/score_table.npz not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/specialists.json || { echo "error: $(AZOTH_ROOT)/specialists.json not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/general/model.txt || ls $(AZOTH_ROOT)/general/models/seed_*.txt >/dev/null 2>&1 || { echo "error: $(AZOTH_ROOT)/general missing model.txt or models/seed_*.txt"; exit 1; }
	@test -f $(AZOTH_ROOT)/general/feature_spec.json || { echo "error: $(AZOTH_ROOT)/general/feature_spec.json not found"; exit 1; }
	@if [ "$(AZOTH_VALIDATE_DIAGNOSTICS)" = "1" ] || [ "$(AZOTH_VALIDATE_DIAGNOSTICS)" = "true" ] || [ "$(AZOTH_VALIDATE_DIAGNOSTICS)" = "yes" ]; then \
	  $(PYTHON) scripts/azoth_route_diagnostics.py \
	    --config $(AZOTH_CONFIG) \
	    --score-table $(AZOTH_SCORE_TABLE) \
	    --output $(AZOTH_DIAGNOSTICS) \
	    --csv $(AZOTH_DIAGNOSTICS_CSV) \
	    --slice-output $(AZOTH_SLICE_METRICS) \
	    --slice-csv $(AZOTH_SLICE_METRICS_CSV); \
	else \
	  printf '# Azoth Route Diagnostics\n\nSkipped during fast azoth-validate. Run `make azoth-diagnostics AZOTH_ROOT=%s` for the full report.\n' "$(AZOTH_ROOT)" > "$(AZOTH_DIAGNOSTICS)"; \
	  printf 'status,message\nskipped,fast azoth-validate\n' > "$(AZOTH_DIAGNOSTICS_CSV)"; \
	  printf '# Azoth Slice Metrics\n\nSkipped during fast azoth-validate. Run `make azoth-diagnostics AZOTH_ROOT=%s` for the full report.\n' "$(AZOTH_ROOT)" > "$(AZOTH_SLICE_METRICS)"; \
	  printf 'status,message\nskipped,fast azoth-validate\n' > "$(AZOTH_SLICE_METRICS_CSV)"; \
	fi
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
		--fail-on-budget --max-budget-multiplier 30
	$(PYTHON) scripts/compute_routed_metrics.py --azoth-root $(AZOTH_ROOT) --db $(DB) $(AZOTH_VALIDATE_ROUTED_METRICS_ARGS) $(AZOTH_ROUTED_METRICS_ARGS)
	$(PYTHON) scripts/azoth_route_policy_eval.py \
		--score-table $(AZOTH_ROOT)/score_table.npz \
		--general-scores $(AZOTH_ROOT)/general/threshold_scores.npz \
		--route-policies $(AZOTH_ROUTE_POLICIES) \
		--partition test \
		--output-md $(AZOTH_ROOT)/route_policy_eval_oof.md \
		--output-json $(AZOTH_ROOT)/route_policy_eval_oof.json
	$(PYTHON) scripts/write_azoth_readmes.py --azoth-root $(AZOTH_ROOT)
	@_STAGE=$$(mktemp -d) && \
	  $(PYTHON) scripts/stage_azoth_runtime_bundle.py "$(AZOTH_ROOT)" "$$_STAGE" && \
	  cp "$(AZOTH_DIAGNOSTICS)" "$$_STAGE/route_diagnostics.md" && \
	  cp "$(AZOTH_SLICE_METRICS)" "$$_STAGE/slice_metrics.md" && \
	  cp "$(AZOTH_ROUTE_POLICIES_MD)" "$$_STAGE/route_policies.md" && \
	  cp "$(AZOTH_GLOBAL_POLICY_METRICS_MD)" "$$_STAGE/global_policy_metrics.md" && \
	  $(PYTHON) scripts/validate_azoth_bundle.py "$$_STAGE" && \
	  $(PYTHON) scripts/check_azoth_regression.py --staged "$$_STAGE" --deployed "$(AZOTH_DEPLOY_DIR)" --low-water-mark "$(AZOTH_LOW_WATER_MARK_DIR)" && \
	  if [ "$(AZOTH_SKIP_LITMUS_VALIDATE)" = "1" ] || [ "$(AZOTH_SKIP_LITMUS_VALIDATE)" = "true" ] || [ "$(AZOTH_SKIP_LITMUS_VALIDATE)" = "yes" ]; then \
	    echo "Skipping litmus deployed-ensemble compatibility checks (AZOTH_SKIP_LITMUS_VALIDATE=$(AZOTH_SKIP_LITMUS_VALIDATE))"; \
	  else \
	    echo "Running litmus deployed-ensemble compatibility checks against staged copy..." && \
	    ( cd $(LITMUS_DIR) && LITMUS_MODELS_DIR="$$_STAGE" cargo test --release --test scan_no_deadlock ) && \
	    $(PYTHON) scripts/verify_azoth_litmus_runtime.py --litmus-dir $(LITMUS_DIR) --models-dir "$$_STAGE" --required-model az/native --required-model az/elf; \
	  fi && \
	  rm -rf "$$_STAGE" && \
	  echo "azoth-validate: all gates passed for $(AZOTH_ROOT)" \
	|| { ec=$$?; rm -rf "$$_STAGE"; exit $$ec; }

# Run isolation. Each fresh train picks a unique RUN_ID and writes its
# entire bundle into $(AZOTH_RUNS_ROOT)/$(RUN_ID)/, then atomically
# updates $(AZOTH_ROOT) (the canonical symlink) on success. Failed or
# in-flight runs leave the canonical bundle untouched.
#
# Typical usage from a shell:
#   RUN_DIR=$$(make -s azoth-run-new)
#   make azoth-specialists AZOTH_ROOT="$$RUN_DIR"   # if retraining
#   make azoth-deploy      AZOTH_ROOT="$$RUN_DIR"
#   make azoth-publish     AZOTH_ROOT="$$RUN_DIR"
#
# Or with the chained convenience target:
#   make azoth-publish-deploy
#     # allocates a run dir, runs azoth-deploy into it, publishes on success
#
# Resume an existing run by exporting AZOTH_RUN_ID=<id> before make,
# which freezes the timestamped path used by these targets.
ifeq ($(origin AZOTH_RUN_ID), undefined)
AZOTH_RUN_ID := $(shell date -u +%Y%m%dT%H%M%SZ)-$(shell openssl rand -hex 4 2>/dev/null || hexdump -n4 -e '4/1 "%02x"' /dev/urandom)
endif
AZOTH_RUN_DIR := $(AZOTH_RUNS_ROOT)/$(AZOTH_RUN_ID)

.PHONY: azoth-run-new azoth-publish azoth-publish-deploy

# Create (if needed) and print the path to the run dir for AZOTH_RUN_ID.
# Capture it with $(shell …) or make -s.
azoth-run-new:
	@mkdir -p $(AZOTH_RUN_DIR)
	@echo $(AZOTH_RUN_DIR)

# Validate that AZOTH_ROOT looks like a complete bundle, then atomically
# point $(OUT_ROOT)/azoth at it. Errors out if the bundle is incomplete.
azoth-publish: venv
	$(PYTHON) scripts/azoth_publish_run.py $(AZOTH_ROOT) --link $(OUT_ROOT)/azoth

# Apples-to-apples baseline scoring for autocollie. Given a route, an optional
# row-ids file, and a deploy-root (defaults to AZOTH_ROOT, i.e. the currently
# trained bundle), score the deployed model on those rows and write metrics to
# OUTPUT. First call per (route, model_hash) populates a cache under
# out/cache/autocollie-baseline; subsequent calls hit the cache.
#
# Usage:
#   make azoth-score-route ROUTE=filetypes/pe \
#       ROW_IDS_FILE=/tmp/rows.txt OUTPUT=/tmp/baseline.json
azoth-score-route: venv
	@test -n "$(ROUTE)"  || { echo "error: ROUTE= is required"; exit 2; }
	@test -n "$(OUTPUT)" || { echo "error: OUTPUT= is required"; exit 2; }
	$(PYTHON) scripts/azoth_score_deployed.py \
		--route $(ROUTE) \
		--db $(DB) \
		--deploy-root $(AZOTH_ROOT) \
		$(if $(ROW_IDS_FILE),--row-ids-file $(ROW_IDS_FILE),) \
		--output $(OUTPUT)

# Convenience: full deploy into a fresh run dir, then publish.
azoth-publish-deploy: venv
	@echo "publish-deploy: allocating $(AZOTH_RUN_DIR)"
	@mkdir -p $(AZOTH_RUN_DIR)
	$(MAKE) azoth-deploy AZOTH_ROOT=$(AZOTH_RUN_DIR)
	$(MAKE) azoth-publish AZOTH_ROOT=$(AZOTH_RUN_DIR)
	@echo "publish-deploy: $(OUT_ROOT)/azoth now points to $(AZOTH_RUN_DIR)"

azoth-deploy: azoth-calibrate
	@test -f $(AZOTH_ROOT)/config.json || { echo "error: $(AZOTH_ROOT)/config.json not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/score_table.npz || { echo "error: $(AZOTH_ROOT)/score_table.npz not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/specialists.json || { echo "error: $(AZOTH_ROOT)/specialists.json not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/general/model.txt || ls $(AZOTH_ROOT)/general/models/seed_*.txt >/dev/null 2>&1 || { echo "error: $(AZOTH_ROOT)/general missing model.txt or models/seed_*.txt"; exit 1; }
	@test -f $(AZOTH_ROOT)/general/feature_spec.json || { echo "error: $(AZOTH_ROOT)/general/feature_spec.json not found"; exit 1; }
	@if [ "$(AZOTH_DEPLOY_DIAGNOSTICS)" = "1" ] || [ "$(AZOTH_DEPLOY_DIAGNOSTICS)" = "true" ] || [ "$(AZOTH_DEPLOY_DIAGNOSTICS)" = "yes" ]; then \
	  $(PYTHON) scripts/azoth_route_diagnostics.py \
	    --config $(AZOTH_CONFIG) \
	    --score-table $(AZOTH_SCORE_TABLE) \
	    --output $(AZOTH_DIAGNOSTICS) \
	    --csv $(AZOTH_DIAGNOSTICS_CSV) \
	    --slice-output $(AZOTH_SLICE_METRICS) \
	    --slice-csv $(AZOTH_SLICE_METRICS_CSV); \
	else \
	  printf '# Azoth Route Diagnostics\n\nSkipped during deploy (AZOTH_DEPLOY_DIAGNOSTICS=0). Run `make azoth-diagnostics AZOTH_ROOT=%s` for the full report.\n' "$(AZOTH_ROOT)" > "$(AZOTH_DIAGNOSTICS)"; \
	  printf 'status,message\nskipped,AZOTH_DEPLOY_DIAGNOSTICS=0\n' > "$(AZOTH_DIAGNOSTICS_CSV)"; \
	  printf '# Azoth Slice Metrics\n\nSkipped during deploy (AZOTH_DEPLOY_DIAGNOSTICS=0). Run `make azoth-diagnostics AZOTH_ROOT=%s` for the full report.\n' "$(AZOTH_ROOT)" > "$(AZOTH_SLICE_METRICS)"; \
	  printf 'status,message\nskipped,AZOTH_DEPLOY_DIAGNOSTICS=0\n' > "$(AZOTH_SLICE_METRICS_CSV)"; \
	fi
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
		--fail-on-budget --max-budget-multiplier 30
	$(PYTHON) scripts/compute_routed_metrics.py --azoth-root $(AZOTH_ROOT) --db $(DB) $(AZOTH_ROUTED_METRICS_ARGS)
	$(PYTHON) scripts/azoth_route_policy_eval.py \
		--score-table $(AZOTH_ROOT)/score_table.npz \
		--general-scores $(AZOTH_ROOT)/general/threshold_scores.npz \
		--route-policies $(AZOTH_ROUTE_POLICIES) \
		--partition test \
		--output-md $(AZOTH_ROOT)/route_policy_eval_oof.md \
		--output-json $(AZOTH_ROOT)/route_policy_eval_oof.json
	$(PYTHON) scripts/write_azoth_readmes.py --azoth-root $(AZOTH_ROOT)
	$(MAKE) azoth-deploy-final

# azoth-deploy-final reruns only the post-generation deploy stages: stage the
# curated runtime/docs bundle, validate it, run litmus compatibility checks,
# mirror it into $(AZOTH_DEPLOY_DIR), and verify litmus's default deployed path.
# It intentionally skips azoth-calibrate, diagnostics, policy search, routed
# metrics, and README regeneration; use after those artifacts already exist.
azoth-deploy-final: venv
	@test -f $(AZOTH_ROOT)/config.json || { echo "error: $(AZOTH_ROOT)/config.json not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/score_table.npz || { echo "error: $(AZOTH_ROOT)/score_table.npz not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/specialists.json || { echo "error: $(AZOTH_ROOT)/specialists.json not found"; exit 1; }
	@test -f $(AZOTH_ROOT)/general/model.txt || ls $(AZOTH_ROOT)/general/models/seed_*.txt >/dev/null 2>&1 || { echo "error: $(AZOTH_ROOT)/general missing model.txt or models/seed_*.txt"; exit 1; }
	@test -f $(AZOTH_ROOT)/general/feature_spec.json || { echo "error: $(AZOTH_ROOT)/general/feature_spec.json not found"; exit 1; }
	@test -f $(AZOTH_DIAGNOSTICS) || { echo "error: $(AZOTH_DIAGNOSTICS) not found; run make azoth-deploy or regenerate diagnostics first"; exit 1; }
	@test -f $(AZOTH_SLICE_METRICS) || { echo "error: $(AZOTH_SLICE_METRICS) not found; run make azoth-deploy or regenerate diagnostics first"; exit 1; }
	@test -f $(AZOTH_ROUTE_POLICIES) || { echo "error: $(AZOTH_ROUTE_POLICIES) not found; run make azoth-deploy or make azoth-policies first"; exit 1; }
	@test -f $(AZOTH_ROUTE_POLICIES_MD) || { echo "error: $(AZOTH_ROUTE_POLICIES_MD) not found; run make azoth-deploy or make azoth-policies first"; exit 1; }
	@test -f $(AZOTH_GLOBAL_POLICY_METRICS_MD) || { echo "error: $(AZOTH_GLOBAL_POLICY_METRICS_MD) not found; run make azoth-deploy first"; exit 1; }
	@# Mirror staged bundle into deploy dir, deleting anything in the deploy
	@# tree that isn't in the staged copy. Per-route slot contents (e.g. an
	@# old `models/` dir from a prior multi-seed deploy) get cleaned even
	@# when the new bundle ships a single-seed `model.txt` for that route.
	@# The lock prevents concurrent deploys from deleting each other's rsync
	@# temp files; --delete-before avoids interleaving deletes with writes.
	@# Protect only deploy repo metadata and static root legal/training docs;
	@# the staged runtime/generated-docs payload is otherwise canonical, so
	@# stale training artifacts are removed.
	@_STAGE=$$(mktemp -d) && \
	  _LOCK=$$(dirname "$(AZOTH_DEPLOY_DIR)")/.azoth-deploy.lock && \
	  trap 'rm -rf "$$_STAGE"' EXIT INT TERM && \
	  $(PYTHON) scripts/stage_azoth_runtime_bundle.py "$(AZOTH_ROOT)" "$$_STAGE" && \
	  cp "$(AZOTH_DIAGNOSTICS)" "$$_STAGE/route_diagnostics.md" && \
	  cp "$(AZOTH_SLICE_METRICS)" "$$_STAGE/slice_metrics.md" && \
	  cp "$(AZOTH_ROUTE_POLICIES_MD)" "$$_STAGE/route_policies.md" && \
	  cp "$(AZOTH_GLOBAL_POLICY_METRICS_MD)" "$$_STAGE/global_policy_metrics.md" && \
	  $(PYTHON) scripts/validate_azoth_bundle.py "$$_STAGE" && \
	  $(PYTHON) scripts/check_azoth_regression.py --staged "$$_STAGE" --deployed "$(AZOTH_DEPLOY_DIR)" --low-water-mark "$(AZOTH_LOW_WATER_MARK_DIR)" && \
	  echo "Running litmus deployed-ensemble compatibility checks against staged copy..." && \
	  ( cd $(LITMUS_DIR) && LITMUS_MODELS_DIR="$$_STAGE" cargo test --release --test scan_no_deadlock ) && \
	  $(PYTHON) scripts/verify_azoth_litmus_runtime.py --litmus-dir $(LITMUS_DIR) --models-dir "$$_STAGE" --required-model az/native --required-model az/elf && \
	  mkdir -p "$(AZOTH_DEPLOY_DIR)" && \
	  flock "$$_LOCK" rsync -a --delete-before \
	    --filter='protect /.git/***' \
	    --filter='protect /.gitignore' \
	    --filter='protect /LICENSE' \
	    --filter='protect /TRAINING.md' \
	    "$$_STAGE/" "$(AZOTH_DEPLOY_DIR)/" && \
	  echo "Running litmus default deployed-model check..." && \
	  ( cd $(LITMUS_DIR) && cargo run --release -- --extra --show all scan /bin/ls ) && \
	  echo "Deployed azoth ensemble bundle to $(AZOTH_DEPLOY_DIR)"

# Legacy single-model false/near reports. Source generation is bumped by
# SKIP so triage can page past already-reviewed samples (TOP_ERRORS=250
# SKIP=100 → JSON has 350 rows; triage skips first 100, copies next 250).
false-positives: venv check-db
	$(PYTHON) -u -m collimator false-positives --db $(DB) \
		--model $(OUT_DIR)/$(MODEL_FILE) \
		--spec $(OUT_DIR)/feature_spec.json \
		$(WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		--scores-cache $(THRESHOLD_SCORES) \
		--top-errors $$(( $(TOP_ERRORS) + $(SKIP) )) \
		--output $(OUT_DIR)/false_positives.json

near-false-positives: venv check-db
	$(PYTHON) -u -m collimator near-false-positives --db $(DB) \
		--model $(OUT_DIR)/$(MODEL_FILE) \
		--spec $(OUT_DIR)/feature_spec.json \
		$(WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		--scores-cache $(THRESHOLD_SCORES) \
		--top-errors $$(( $(TOP_ERRORS) + $(SKIP) )) \
		--output $(OUT_DIR)/near_false_positives.json

false-negatives: venv check-db
	$(PYTHON) -u -m collimator false-negatives --db $(DB) \
		--model $(OUT_DIR)/$(MODEL_FILE) \
		--spec $(OUT_DIR)/feature_spec.json \
		$(WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		--scores-cache $(THRESHOLD_SCORES) \
		--top-errors $$(( $(TOP_ERRORS) + $(SKIP) )) \
		--output $(OUT_DIR)/false_negatives.json

near-false-negatives: venv check-db
	$(PYTHON) -u -m collimator near-false-negatives --db $(DB) \
		--model $(OUT_DIR)/$(MODEL_FILE) \
		--spec $(OUT_DIR)/feature_spec.json \
		$(WORKERS_ARG) \
		$(THRESHOLD_MAX_ID_ARG) \
		--scores-cache $(THRESHOLD_SCORES) \
		--top-errors $$(( $(TOP_ERRORS) + $(SKIP) )) \
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

# mislabeled-triage: unified deploy-aware error triage.
#
# Uses the score table + route policies (no model rescore) to pull
# benigns flagged AND malware missed by any combination of scopes,
# deduped by sample. Output: one directory with two subtrees ready
# to feed cleave. Layout:
#   $(MIS_TRIAGE_DIR)/false-positives/...
#   $(MIS_TRIAGE_DIR)/false-negatives/...
#
# Usage:
#   make mislabeled-triage                                                  # default: SCOPE=ensemble,specialists,filegroups LEVEL=3 SEVERITY=hostile
#   make mislabeled-triage SCOPE=ensemble                                   # what litmus would flag in production
#   make mislabeled-triage SCOPE=route:filetypes/jpeg LEVEL=3
#   make mislabeled-triage SCOPE=specialists LEVEL=5 SEVERITY=suspicious
#
# Granular variants surface only one side of the pool:
#   make false-positives-triage SCOPE=ensemble
#   make false-negatives-triage SCOPE=ensemble
#
# Default SCOPE combines ensemble+specialists+filegroups so the pool
# captures every error mode worth triaging in one pass — they overlap
# heavily and dedup-by-row keeps the list manageable.
# COMMA / SPACE: make doesn't let you put a literal comma in a function
# expansion since it's the argument separator, so we capture it here.
# Must be defined BEFORE MIS_TAG because := evaluates immediately.
COMMA := ,
EMPTY :=
SPACE := $(EMPTY) $(EMPTY)

SCOPE ?= ensemble,specialists,filegroups
LEVEL ?= 3
SEVERITY ?= hostile
MIS_TAG := $(subst $(SPACE),_,$(subst $(COMMA),-,$(subst :,-,$(subst /,-,$(SCOPE)))))-L$(LEVEL)-$(SEVERITY)
FP_REPORT ?= $(AZOTH_ROOT)/false_positives_$(MIS_TAG).json
FN_REPORT ?= $(AZOTH_ROOT)/false_negatives_$(MIS_TAG).json
FP_TRIAGE_DIR ?= /tmp/false-positives-$(MIS_TAG)
FN_TRIAGE_DIR ?= /tmp/false-negatives-$(MIS_TAG)
FP_TRIAGE_JSON ?= /tmp/false-positives-$(MIS_TAG).json
FN_TRIAGE_JSON ?= /tmp/false-negatives-$(MIS_TAG).json
MIS_TRIAGE_DIR ?= /tmp/mislabeled-$(MIS_TAG)
MIS_TRIAGE_JSON ?= /tmp/mislabeled-$(MIS_TAG).json

.PHONY: mislabeled-fp-report mislabeled-fn-report \
        false-positives-triage false-negatives-triage \
        mislabeled-triage

mislabeled-fp-report: venv
	$(PYTHON) scripts/mislabeled_by_scope.py \
		--kind false-positives \
		--score-table $(AZOTH_ROOT)/score_table.npz \
		--route-policies $(AZOTH_ROOT)/route_policies.json \
		--scope $(SCOPE) --level $(LEVEL) --severity $(SEVERITY) \
		--skip $(SKIP) --top-errors $(TOP_ERRORS) --db $(DB) \
		--output $(FP_REPORT)

mislabeled-fn-report: venv
	$(PYTHON) scripts/mislabeled_by_scope.py \
		--kind false-negatives \
		--score-table $(AZOTH_ROOT)/score_table.npz \
		--route-policies $(AZOTH_ROOT)/route_policies.json \
		--scope $(SCOPE) --level $(LEVEL) --severity $(SEVERITY) \
		--skip $(SKIP) --top-errors $(TOP_ERRORS) --db $(DB) \
		--output $(FN_REPORT)

false-positives-triage: mislabeled-fp-report
	$(PYTHON) scripts/triage_error_samples.py \
		--report $(FP_REPORT) \
		--output-dir $(FP_TRIAGE_DIR) \
		--samples-dir $(SAMPLES_DIR) \
		--kind false-positives --db $(DB) --top $(TOP_ERRORS)
	@echo "report:   $(FP_REPORT)"
	@echo "samples:  $(FP_TRIAGE_DIR)"
	@echo "to cleave: cleave --format=json $(FP_TRIAGE_DIR) > $(FP_TRIAGE_JSON)"

false-negatives-triage: mislabeled-fn-report
	$(PYTHON) scripts/triage_error_samples.py \
		--report $(FN_REPORT) \
		--output-dir $(FN_TRIAGE_DIR) \
		--samples-dir $(SAMPLES_DIR) \
		--kind false-negatives --db $(DB) --top $(TOP_ERRORS)
	@echo "report:   $(FN_REPORT)"
	@echo "samples:  $(FN_TRIAGE_DIR)"
	@echo "to cleave: cleave --format=json $(FN_TRIAGE_DIR) > $(FN_TRIAGE_JSON)"

mislabeled-triage: mislabeled-fp-report mislabeled-fn-report
	$(PYTHON) scripts/triage_error_samples.py \
		--report $(FP_REPORT) \
		--output-dir $(MIS_TRIAGE_DIR)/false-positives \
		--samples-dir $(SAMPLES_DIR) \
		--kind false-positives --db $(DB) --top $(TOP_ERRORS)
	$(PYTHON) scripts/triage_error_samples.py \
		--report $(FN_REPORT) \
		--output-dir $(MIS_TRIAGE_DIR)/false-negatives \
		--samples-dir $(SAMPLES_DIR) \
		--kind false-negatives --db $(DB) --top $(TOP_ERRORS)
	@echo "scope:    $(SCOPE) | level: L$(LEVEL) | severity: $(SEVERITY)"
	@echo "reports:  $(FP_REPORT) + $(FN_REPORT)"
	@echo "samples:  $(MIS_TRIAGE_DIR)/{false-positives,false-negatives}/"
	@echo "to cleave: cleave --format=json $(MIS_TRIAGE_DIR) > $(MIS_TRIAGE_JSON)"

near-false-positives-triage: near-false-positives
	$(PYTHON) scripts/triage_error_samples.py \
		--report $(OUT_DIR)/near_false_positives.json \
		--output-dir $(NEAR_FALSE_POSITIVES_TRIAGE_DIR) \
		--samples-dir $(SAMPLES_DIR) \
		--kind near-false-positives \
		--skip $(SKIP) \
		--top $(TOP_ERRORS)
	@echo "samples staged in $(NEAR_FALSE_POSITIVES_TRIAGE_DIR); run 'cleave --format=json $(NEAR_FALSE_POSITIVES_TRIAGE_DIR)' manually if needed."

benchmark: venv check-db
	$(PYTHON) -m collimator benchmark --db $(DB) $(WORKERS_ARG) \
		$(if $(wildcard $(OUT_DIR)/$(MODEL_FILE)),--model $(OUT_DIR)/$(MODEL_FILE),) \
		$(if $(wildcard $(OUT_DIR)/feature_spec.json),--spec $(OUT_DIR)/feature_spec.json,)

build-splits: venv check-db
	$(PYTHON) -m collimator build-splits --db $(DB)

experiment: venv check-db
	@mkdir -p $(EXP_LOG_DIR)
	COLLIMATOR_NUM_THREADS=$(EXP_LGBM_THREADS) \
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
	COLLIMATOR_ATTACK_FEATURES=$(EXP_ATTACK_FEATURES) \
	COLLIMATOR_CONFIDENCE_WEIGHTED_NGRAMS=$(EXP_CONFIDENCE_WEIGHTED_NGRAMS) \
	COLLIMATOR_OBJECTIVE_TRIGRAMS=$(EXP_OBJECTIVE_TRIGRAMS) \
	COLLIMATOR_SUSPICIOUS_TRIGRAMS=$(EXP_SUSPICIOUS_TRIGRAMS) \
	COLLIMATOR_ATTACK_NGRAMS=$(EXP_ATTACK_NGRAMS) \
	COLLIMATOR_CRIT_CATEGORY_NGRAMS=$(EXP_CRIT_CATEGORY_NGRAMS) \
	COLLIMATOR_TIERED_CRIT_BIGRAMS=$(EXP_TIERED_CRIT_BIGRAMS) \
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
	COLLIMATOR_ATTACK_CODE_NGRAMS=$(EXP_ATTACK_CODE_NGRAMS) \
	COLLIMATOR_PE_FORMAT_FLAGS=$(EXP_PE_FORMAT_FLAGS) \
	COLLIMATOR_PE_TEMPORAL_ANOMALY=$(EXP_PE_TEMPORAL_ANOMALY) \
	COLLIMATOR_TEXT_METRICS_FULL=$(EXP_TEXT_METRICS_FULL) \
	COLLIMATOR_OVERLAY_SIGNAL=$(EXP_OVERLAY_SIGNAL) \
	COLLIMATOR_METRIC_RATIO_FEATURES=$(EXP_METRIC_RATIO_FEATURES) \
	COLLIMATOR_SIZE_NORMALIZED_METRICS=$(EXP_SIZE_NORMALIZED_METRICS) \
	COLLIMATOR_NONSTANDARD_SECTION_SIGNAL=$(EXP_NONSTANDARD_SECTION_SIGNAL) \
	COLLIMATOR_LINE_LENGTH_BUCKETS=$(EXP_LINE_LENGTH_BUCKETS) \
	COLLIMATOR_EXTENDED_METRICS_INCLUDE=$(EXP_EXTENDED_METRICS_INCLUDE) \
	COLLIMATOR_TOP_K_RISK_FILES_MIN_CRIT=$(EXP_TOP_K_RISK_FILES_MIN_CRIT) \
	COLLIMATOR_METRIC_CORRELATION_PAIRS=$(EXP_METRIC_CORRELATION_PAIRS) \
	COLLIMATOR_KV_VALUE_SPLIT=$(EXP_KV_VALUE_SPLIT) \
	COLLIMATOR_SYMBOL_BIGRAMS=$(EXP_SYMBOL_BIGRAMS) \
	COLLIMATOR_SYMBOL_BIGRAM_MAX=$(EXP_SYMBOL_BIGRAM_MAX) \
	COLLIMATOR_SYMBOL_MIN_FREQ_BIGRAM=$(EXP_SYMBOL_MIN_FREQ_BIGRAM) \
	COLLIMATOR_SYMBOL_TRIGRAMS=$(EXP_SYMBOL_TRIGRAMS) \
	COLLIMATOR_SYMBOL_TRIGRAM_MAX=$(EXP_SYMBOL_TRIGRAM_MAX) \
	COLLIMATOR_SYMBOL_MIN_FREQ_TRIGRAM=$(EXP_SYMBOL_MIN_FREQ_TRIGRAM) \
	COLLIMATOR_TRIGRAM_MIN_FREQ=$(EXP_TRIGRAM_MIN_FREQ) \
	COLLIMATOR_TIERED_CRIT_QUADGRAMS=$(EXP_TIERED_CRIT_QUADGRAMS) \
	COLLIMATOR_TIERED_QUADGRAM_PATH_DEPTH=$(EXP_TIERED_QUADGRAM_PATH_DEPTH) \
	COLLIMATOR_TIERED_QUADGRAM_MIN_CRIT=$(EXP_TIERED_QUADGRAM_MIN_CRIT) \
	COLLIMATOR_TIERED_QUADGRAM_MAX=$(EXP_TIERED_QUADGRAM_MAX) \
	COLLIMATOR_TIERED_QUADGRAM_MIN_FREQ=$(EXP_TIERED_QUADGRAM_MIN_FREQ) \
	COLLIMATOR_MBC_ID_VOCAB=$(EXP_MBC_ID_VOCAB) \
	COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS=$(EXP_TRAIT_CONFIDENCE_MOMENTS) \
	COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE=$(EXP_TRAIT_ID_LEXICAL_DISTANCE) \
	COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES=$(EXP_DOCUMENT_OBFUSCATION_FEATURES) \
	COLLIMATOR_TIERED_BIGRAM_BRANCH_MIN_CRIT=$(EXP_TIERED_BIGRAM_BRANCH_MIN_CRIT) \
	COLLIMATOR_EXPERIMENT_TAG=$(EXP_TAG) \
	$(PYTHON) -u -m collimator experiment --db $(DB) --output $(EXP_OUT_DIR) --model-name $(MODEL) --learner $(LEARNER) $(EXP_WORKERS_ARG) --seed $(SEED) \
		--experiment-idea $(EXP_IDEA) --route $(EXP_ROUTE) $(EXP_RERUN_ARG) \
		--train-samples $(EXP_TRAIN_SAMPLES) --max-test-samples $(EXP_MAX_TEST_SAMPLES) \
		--total-limit $(EXP_TOTAL_LIMIT) \
		$(if $(EXP_MAX_ID),--max-id $(EXP_MAX_ID),) \
		$(EXP_REFRESH_CACHE_SNAPSHOT_ARG) \
		--n-folds $(EXP_FOLDS) --holdout-fraction $(EXP_HOLDOUT_FRACTION) \
		--n-estimators $(EXP_ESTIMATORS) --max-depth $(EXP_MAX_DEPTH) \
		--learning-rate $(EXP_LEARNING_RATE) --early-stopping-rounds $(EXP_EARLY_STOPPING) \
		$(if $(EXP_NUM_LEAVES),--num-leaves $(EXP_NUM_LEAVES),) \
		$(if $(EXP_MIN_CHILD_SAMPLES),--min-child-samples $(EXP_MIN_CHILD_SAMPLES),) \
		$(if $(EXP_MIN_CHILD_WEIGHT),--min-child-weight $(EXP_MIN_CHILD_WEIGHT),) \
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
		--runs-dir "$(AZOTH_AUTOCOLLIE_RUNS_DIR)" \
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
	@test -f $(OUT_DIR)/reference.json || { echo "error: $(OUT_DIR)/reference.json not found — run make azoth-fast-train first"; exit 1; }
	@echo "Running xgboost-ars tests..."
	cd $(XGBOOST_ARS_DIR) && XGBOOST_ARS_REFERENCE_JSON=$(abspath $(OUT_DIR)/reference.json) cargo test --release
	@echo "xgboost-ars: all tests passed"

.PHONY: verify-litmus
verify-litmus:
	@test -d $(LITMUS_DIR) || { echo "error: $(LITMUS_DIR) does not exist"; exit 1; }
	@test -f $(OUT_DIR)/extraction_fixture.json || { echo "error: $(OUT_DIR)/extraction_fixture.json not found — run make azoth-fast-train first"; exit 1; }
	@test ! -f $(OUT_DIR)/threshold_tuning.json || $(PYTHON) scripts/build_litmus_config.py --threshold-tuning $(OUT_DIR)/threshold_tuning.json --output $(OUT_DIR)/config.json
	@echo "Running litmus feature-extraction parity tests..."
	@mkdir -p $(LITMUS_DIR)/tests/fixtures
	cp $(OUT_DIR)/extraction_fixture.json $(LITMUS_DIR)/tests/fixtures/extraction_fixture.json
	cd $(LITMUS_DIR) && LITMUS_MODELS_DIR=$(abspath $(OUT_DIR)) cargo test --release --test extraction_parity
	@echo "litmus: extraction parity tests passed"

AUTOCOLLIE_DIR ?= ../autocollie
AUTOCOLLIE_BIN := $(AUTOCOLLIE_DIR)/bin/autocollie
EXPERIMENTS ?= 12
AUTOCOLLIE_LLM_TIMEOUT ?= 15m
AUTOCOLLIE_SCREEN_TIMEOUT ?= 90m
# Parallel route processing for autocollie auto/loop modes. Two routes
# run cycles concurrently by default; promotes serialize internally.
# EXP_WORKERS and EXP_LGBM_THREADS are auto-derived from MAX_CPU_THREADS /
# ROUTE_CONCURRENCY in autocollie so concurrent screens don't fight for
# the host's full CPU. Set ROUTE_CONCURRENCY=1 to force sequential.
ROUTE_CONCURRENCY ?= 2
MAX_CPU_THREADS ?= 128
# Autocollie defaults to the local Hopper replica. Using the bare `hopper`
# hostname can resolve through public DNS and burn screen slots on timeouts.
AUTOCOLLIE_DB ?= postgres://hopper@localhost:5432/hopper
# ROUTES is comma-separated, e.g. ROUTES=filetypes/javascript,filegroups/scripts
# ROUTE (singular) is accepted as a convenience.
ROUTES ?= $(ROUTE)

.PHONY: autocollie autocollie-loop autocollie-build autocollie-dryrun autocollie-screen autocollie-confirm autocollie-promote autocollie-backfill-l3 azoth-augment-small-routes

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
		--fail-on-budget --max-budget-multiplier 30
	$(PYTHON) scripts/compute_routed_metrics.py --azoth-root $(AZOTH_ROOT) --db $(DB) $(AZOTH_ROUTED_METRICS_ARGS)
	$(PYTHON) scripts/write_azoth_readmes.py --azoth-root $(AZOTH_ROOT)

# One-time repair for legacy autocollie baselines whose run JSONs predate
# recall_at_fp_per_million_* fields. Replays the selected historical baseline
# specs with EXP_RERUN=1, then copies refreshed metrics back onto the legacy
# baseline key so autocollie can compare real recall@3FPM instead of falling
# back to PR AUC.
#
# Usage:
#   make autocollie-backfill-l3 ROUTES=filetypes/python,filetypes/javascript
#   make autocollie-backfill-l3 ROUTES=filetypes/ DRY_RUN=1
#   make autocollie-backfill-l3 KEYS=5f2daa8cb63f39c4
DRY_RUN ?= 0
KEYS ?=
BACKFILL_LIMIT ?= 0
BACKFILL_ALL_MISSING ?= 0
autocollie-backfill-l3: venv check-db
	$(PYTHON) scripts/autocollie_backfill_l3.py \
		--runs-dir "$(AZOTH_AUTOCOLLIE_RUNS_DIR)" \
		--makefile Makefile \
		--db $(DB) \
		--workers $(or $(WORKERS),64) \
		$(if $(ROUTES),--routes $(ROUTES),) \
		$(if $(KEYS),--keys $(KEYS),) \
		$(if $(filter 1 true yes,$(DRY_RUN)),--dry-run,) \
		$(if $(filter 1 true yes,$(BACKFILL_ALL_MISSING)),--all-missing,) \
		$(if $(BACKFILL_LIMIT),--limit $(BACKFILL_LIMIT),)

# Autocollie targets all default DB to AUTOCOLLIE_DB (local replica). User can
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
		--llm-timeout $(AUTOCOLLIE_LLM_TIMEOUT) \
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
# the route's currently trained Azoth specialist in $(AZOTH_ROOT), automatically promote it (confirm + full-train
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
		--baseline-azoth-root $(AZOTH_ROOT) \
		$(if $(ROUTES),--routes $(ROUTES),) \
		$(if $(AUTO_ROUTES),--auto-routes $(AUTO_ROUTES),) \
		$(if $(filter 1 true yes,$(SHUFFLE_ROUTES)),--shuffle-routes,) \
		--experiments $(EXPERIMENTS) \
		--passes $(PASSES) \
		--seed $(CONFIRM_SEED) \
		--llm-timeout $(AUTOCOLLIE_LLM_TIMEOUT) \
		--screen-timeout $(AUTOCOLLIE_SCREEN_TIMEOUT) \
		--promote-timeout 180m \
		--route-concurrency $(ROUTE_CONCURRENCY) \
		--max-cpu-threads $(MAX_CPU_THREADS) \
		--make-args "DB=$(DB) $(if $(WORKERS),EXP_WORKERS=$(WORKERS) ,)EXP_ESTIMATORS=$(or $(EXP_ESTIMATORS_DEFAULT),250)"

# autocollie-loop is the same target with PASSES=0 — loops the screen+promote
# ladder over the route list until Ctrl-C.
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
	@echo "  autocollie-backfill-l3 Rerun selected legacy baselines to add recall@FP/M fields"
	@echo "  autocollie         Full hands-off ladder: screen + auto-promote per route"
	@echo "  autocollie-loop    Same as autocollie with PASSES=0 (loop until Ctrl-C)"
	@echo "  azoth-validate     Run azoth-deploy gates against AZOTH_ROOT without copying (AZOTH_SKIP_LITMUS_VALIDATE=1 skips litmus)"
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
	@echo "  EXPERIMENTS=n        Specs requested per autocollie cycle (default: 12)"
	@echo "  PASSES=n             Times to loop the autocollie route list (0=until Ctrl-C)"
	@echo "  EXP_ESTIMATORS_DEFAULT=n  Floor for screen/confirm/promote estimators (default: 250)"
	@echo "  AZOTH_SPECIALIST_TRAIN_OVERRIDE='route:field=value ...'"
	@echo "                       Per-route specialist TrainConfig overrides"
	@echo "  MODELS_DIR=path    Deployment target (default: ../litmus-models/<target-model>)"
