# Azoth Experiment Workflow

This directory is the human-readable experiment ledger. Machine-readable run
artifacts live under `out/experiments/azoth/runs`.

## Run One Experiment

Use `make experiment` for global azoth screens:

```sh
make experiment EXP_WORKERS=64 \
  EXP_IDEA=no_hostile_weighted_density \
  EXP_TAG=_no_hwd \
  EXP_HOSTILE_WEIGHTED_DENSITY=0
```

Important knobs:

- `EXP_IDEA`: stable human label for the idea being tested.
- `EXP_ROUTE`: route being tested. Default is `general`; future specialist
  values should look like `filegroups/scripts` or `filetypes/pe`.
- `EXP_TAG`: log filename suffix only. Do not rely on it as identity.
- `EXP_RERUN=1`: force a deliberate replicate of an existing canonical run.
- `EXP_REFRESH_CACHE_SNAPSHOT=1`: refresh the pinned DB snapshot.
- `EXP_ALLOWED_FEATURES_FILE`: restrict training to an explicit feature list.
- `EXP_MONOTONE_JSON`: JSON map of feature-name prefixes to monotone
  constraints, for example `{"score:":1}`.

The default profile is a probe-sized azoth screen:

- `EXP_TRAIN_SAMPLES=150000`
- `EXP_MAX_TEST_SAMPLES=40000`
- `EXP_ESTIMATORS=180`
- `EXP_FOLDS=0`

This is the standard for bulk experiments. Do not run 400k/100k tranches by
default; those are confirmation-sized jobs and can take an hour per uncached
feature-space change. Cached matrix reuse makes hyperparameter-only reruns much
faster.

## Search Knobs

Autocollie and human tranches should prefer these exposed knobs before adding
new code.

Tree/training:

- `EXP_ESTIMATORS`, `EXP_MAX_DEPTH`, `EXP_NUM_LEAVES`,
  `EXP_MIN_CHILD_SAMPLES`
- `EXP_LEARNING_RATE`, `EXP_EARLY_STOPPING`
- `EXP_COLSAMPLE_BYTREE`, `EXP_SUBSAMPLE`
- `EXP_REG_ALPHA`, `EXP_REG_LAMBDA`, `EXP_GAMMA`
- `EXP_BETA`, `EXP_THRESHOLD_MODE`, `EXP_THRESHOLD_FPR_TARGET`
- `EXP_HARD_NEGATIVE_FRACTION`, `EXP_HARD_NEGATIVE_WEIGHT`
- `EXP_BENIGN_FILETYPE_WEIGHT`, `EXP_MONOTONE_JSON`

Sampling and route shape:

- `EXP_ROUTE`, `EXP_TRAIN_SAMPLES`, `EXP_MAX_TEST_SAMPLES`, `SEED`
- `EXP_MIN_SAMPLE_SCORE`, `EXP_MIN_MALWARE_SCORE`
- `EXP_TOP_K_RISK_FILES`
- `EXP_ALLOWED_FEATURES_FILE`, `DROP_FEATURE_PREFIXES`

Feature families:

- `EXP_DISABLE_FEATURE_GROUPS`
- `EXP_FORMAT_HINTS`, `EXP_TAXONOMY_FEATURES`, `EXP_EMBER_LITE_FEATURES`
- `EXP_EXTENDED_METRICS`, `EXP_METRIC_MIN_FREQ_PCT`
- `EXP_KV_VOCAB`, `EXP_KV_VOCAB_MAX`, `EXP_KV_MIN_FREQ`,
  `EXP_KV_SHAPE_FEATURES`
- `EXP_SYMBOL_VOCAB`, `EXP_SYMBOL_VOCAB_MAX`, `EXP_SYMBOL_MIN_FREQ`
- `EXP_TEXT_ENCODING_FEATURES`
- `EXP_PACKAGED_CAPABILITY_MODE`

N-grams:

- `EXP_NGRAM_PATH_DEPTH`, `EXP_NGRAM_MIN_CRIT`
- `EXP_BIGRAM_MAX`, `EXP_BIGRAM_MIN_FREQ`
- `EXP_TRIGRAM_MAX`, `EXP_TRIGRAM_MAX_BENIGN_FRAC`
- `EXP_CONFIDENCE_WEIGHTED_NGRAMS`
- `EXP_OBJECTIVE_TRIGRAMS`, `EXP_SUSPICIOUS_TRIGRAMS`,
  `EXP_ATTACK_NGRAMS`
- `EXP_TIERED_BIGRAM_PATH_DEPTH`, `EXP_TIERED_BIGRAM_MIN_CRIT`,
  `EXP_TIERED_BIGRAM_MAX`, `EXP_TIERED_BIGRAM_MIN_FREQ`
- `EXP_TIERED_CRIT_TRIGRAMS`, `EXP_TIERED_TRIGRAM_PATH_DEPTH`,
  `EXP_TIERED_TRIGRAM_MIN_CRIT`, `EXP_TIERED_TRIGRAM_MAX`,
  `EXP_TIERED_TRIGRAM_MIN_FREQ`

Useful future code-backed knobs:

- KV/symbol vocab ranking: `frequency`, `malware_lift`, `chi2`,
  `mutual_info`.
- Formula vocab modes: `summary`, `tokens`, `tokens_no_numbers`,
  `operators`.
- Route-local metric vocab modes, including missing-key and value-size
  features.

## Experiment Identity

Experiments are content-addressed. The runner computes an `experiment_key` from
the effective route, snapshot, sample profile, seed, learner, feature config,
training config, and filters.

The key intentionally excludes timestamps, log paths, and `EXP_TAG`.

If `out/experiments/azoth/runs/<experiment_key>.json` already exists, the runner
prints the previous result and exits. Use `EXP_RERUN=1` only when you want a
true replicate.

## Find Past Work

Search machine-readable runs:

```sh
rg '"idea": "no_hostile_weighted_density"' out/experiments/azoth/runs
rg '"route": "general"' out/experiments/azoth/runs
rg 'HOSTILE_WEIGHTED_DENSITY' out/experiments/azoth/runs
rg '"experiment_key":' out/experiments/azoth/runs
```

Search human conclusions:

```sh
rg 'no hostile weighted density|tiered crit trigrams|hard negatives' experiments
```

Reference a run by its keyed artifact when possible:

```text
out/experiments/azoth/runs/<experiment_key>.json
```

Timestamped summaries are still written for chronological debugging, but the
keyed artifact is the stable reference.

## Bulk Experiment Tranches

Run experiments in small tranches of 10-20. A tranche should have one theme,
one route, one pinned snapshot, and the default probe profile. Run serially by
default to avoid database and CPU contention.

Example:

```sh
set -euo pipefail

common='EXP_WORKERS=64 EXP_ROUTE=general'

make experiment $common EXP_IDEA=no_hwd EXP_TAG=_no_hwd \
  EXP_HOSTILE_WEIGHTED_DENSITY=0

make experiment $common EXP_IDEA=hwd_plus_trigrams EXP_TAG=_hwd_trigrams \
  EXP_HOSTILE_WEIGHTED_DENSITY=0 EXP_TIERED_CRIT_TRIGRAMS=1

make experiment $common EXP_IDEA=ngram_depth3 EXP_TAG=_ngram_d3 \
  EXP_NGRAM_PATH_DEPTH=3
```

For a concrete editable tranche, use:

```sh
scripts/run_azoth_global_tranche.sh
```

For a larger overnight tranche with general, filegroup, and filetype specialist
experiments, use:

```sh
scripts/run_azoth_overnight_experiments.sh
```

These scripts are deliberately plain shell: one shared `common` block and one
`make experiment` call per idea. Change the list, run it, then record the
outcomes below.

After each tranche:

1. Summarize JSON metrics from `out/experiments/azoth/runs`.
2. Append outcomes and verdicts to `experiments/EXPERIMENTS.md` or a focused
   route log.
3. Confirm clear wins with routed policy metrics, an explicit larger sample, or
   `make train`. A second seed is most useful for small probes; it is usually
   less useful after a 400k/100k run.
4. Write the next tranche from what was learned.

Do not keep rerunning weak ideas with small wording changes. If a run is an
exact duplicate, the key guard should skip it. If it is a near-duplicate, make
the difference explicit in `EXP_IDEA` and in the tranche notes.

## Autonomous Research

The proposed autonomous loop is documented in [AUTOCOLLIE.md](../AUTOCOLLIE.md).
It should use this experiment framework directly: route selection, five
content-addressed screening experiments, different-seed confirmation, candidate
bundle training, calibration, route policy search, diagnostics, and deployment
validation.

Autocollie should not promote from sampled F1 alone. A winner becomes real only
after it improves or preserves L3 hostile policy quality under the calibrated
full-corpus FP/M budget.

## Specialist Routes

Use `EXP_ROUTE` to label route-scoped experiments even before the full specialist
runner learns the same key system:

```sh
make experiment EXP_ROUTE=filetypes/pe EXP_IDEA=pe_hard_tail_probe ...
make experiment EXP_ROUTE=filegroups/scripts EXP_IDEA=scripts_tiered_trigrams ...
```

For deployable specialist experiments, record both local route metrics and
full-corpus routed policy metrics. A strong local specialist is not enough by
itself; it must improve the calibrated route policy.
