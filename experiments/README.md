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

## Trait keyword comparison

Compare baseline, relative rule-ID words, description words, and both:

```sh
bash scripts/run_trait_keyword_experiments.sh

# Smaller Python probe; use another seed to confirm a promising result.
EXP_ROUTE=filetypes/python bash scripts/run_trait_keyword_experiments.sh \
  EXP_TRAIN_SAMPLES=20000 EXP_MAX_TEST_SAMPLES=5000 EXP_ESTIMATORS=100 SEED=42
```

The script shares a read-only PostgreSQL snapshot across all four variants,
uses separate model directories under `out/experiments/trait-keywords`, and
disables the fixed feature allowlist for every arm. Existing features remain
enabled. Pass ordinary Make overrides to adjust the common settings.

Individual knobs: `EXP_RULE_KEYWORDS=1`, `EXP_DESCRIPTION_KEYWORDS=1`,
`EXP_KEYWORD_VOCAB_MAX=10000`, `EXP_KEYWORD_MIN_FREQ=5`. Each source gets
its own cap. Selection ranks words by document frequency across both classes
in the supplied training cohort, breaking ties lexically. It uses the full
training cohort, adding one bounded DB read pass when enabled. Evaluation
rows never select words. Compare dev recall at zero and one observed FP,
then confirm larger probes across seeds before touching locked test data.

Tokenization lowercases ASCII words, splits punctuation including underscores
and hyphens, drops single-character and purely numeric tokens, and does no
stemming or stopword filtering. ID words come from the suffix after `::`
(the leaf for legacy slash-only IDs). Description words come from the stored
report's `desc`/`d`/`description`, preserving the analyzed rule revision.
Only confident findings contribute; words are binary per report across all
embedded files. `ruleword:*` and `descword:*` have separate columns, so the
model can learn benign and malicious associations, including absence and
interactions. They can also be disabled as feature groups or dropped by prefix.

Blank or missing descriptions fail the description experiment with example
rule IDs during both discovery and prediction. ID-only runs remain usable.
Keyword models now carry ABI 22 with `base_feature_abi: 20`, preserving the
trainer's existing metric/structure semantics. Scan implements both keyword
families and checks description inputs per consulted model. ABI 21 already
defines different metric/structure behavior in Scan; earlier research artifacts
marked v21 must be regenerated through the training pipeline before deployment.
Publication continues to preserve the validated feature spec byte for byte.

Initial Python probe (2026-10-30): 20,000 selected training rows, 5,000 dev
rows (2,500 per class), seed 42, and a 100-tree budget. All variants shared
one snapshot, identical dev rows, and identical base feature columns.

| Added features | Words selected | Dev recall at 0 FP | Dev recall at 1 FP |
| --- | ---: | ---: | ---: |
| Baseline | 0 | 68.24% | 69.92% |
| Relative ID words | 4,961 | 66.72% | 66.72% |
| Description words | 5,483 | 69.64% | 70.12% |
| Both | 10,444 | 68.16% | 69.88% |

Descriptions are the candidate for further confirmation; this single-seed
screen does not establish a stable improvement. No missing descriptions
surfaced in the probe. Detailed run keys and checks are saved in
`out/experiments/trait-keywords-python-probe/comparison.json`.

Confirm descriptions against baseline at seeds 43, 44, and 45:

```sh
.venv/bin/python scripts/confirm_trait_keywords.py
```

This runs six serial fits under one shared PostgreSQL snapshot, matches
training rows within each pair, and fixes dev selection at evaluation seed 42.
Changing the seed varies both the training sample and learner randomness.
The runner checks dev row IDs, labels, report revisions, base feature columns
and values, and saved-model recall before writing `confirmation.json` under
`out/experiments/trait-keywords-confirm`. It also records recovered and lost
malware, changed false positives, and signed keyword contributions for selected
examples and the highest-scoring benign rows. Contributions are log-odds
effects in the model, not causal interpretations of words.

Use `--summarize-only` to rebuild diagnostics from the saved models and matrices.
Use a fresh `--output` directory for a new comparison. `--train-rows`,
`--dev-rows`, `--trees`, and `--seeds` control the confirmation size.

Confirmation results (2026-10-30), at the same 20,000/5,000 profile and
100-tree budget:

| Seed | Baseline, 0 FP | Descriptions, 0 FP | Baseline, 1 FP | Descriptions, 1 FP |
| --- | ---: | ---: | ---: | ---: |
| 43 | 70.72% | 70.92% | 71.32% | 71.12% |
| 44 | 64.08% | 65.88% | 68.48% | 69.48% |
| 45 | 68.64% | 66.56% | 69.68% | 71.48% |

The mean zero-FP change is -0.03 percentage points; the mean one-FP change is
+0.87 points. These are paired dev screens on one fixed cohort, not independent
population estimates. The original zero-FP gain has not confirmed, while the
one-FP result remains promising. Saved-model predictions reproduce recorded
recall when compared at the threshold selector's float32 score precision.

Seed 45 recovers 47 malware samples and loses 2 baseline detections with one
FP allowed, but recovers only 3 and loses 55 at zero FP. Its highest-scoring
benign is row `1651467894`, a hashcat path ending in `OpenCL/m18600-pure.cl`.
Metadata inspection found both the catalog and report classify it as Python,
with Python-specific obfuscation findings. This is a format/trait review
candidate; the path alone does not establish the actual file contents.
No corpus labels or reports were changed for this comparison.

Keep keyword features experimental. Review the format/trait case and compare
smaller or filtered keyword vocabularies before scaling across routes. Full
run identities, changed row IDs, and signed example contributions are saved in
`out/experiments/trait-keywords-confirm/confirmation.json`.

### Per-model autocollie integration and cap search

Autocollie's feature allowlist includes `rule_keywords`, `description_keywords`,
`keyword_vocab_max` (100..100000), and `keyword_min_freq` (1..1000). Both sources
default off; the default cap remains 10000 per source with frequency floor 5.
Settings persist in the route's `feature_env` and replay during confirmation
and full training. Actual `keyword_vocab_sizes` are recorded with experiments
and exposed in autocollie's research context to identify inactive caps.

```sh
make autocollie-screen ROUTES=filetypes/java_class \
  TRY=description_keywords,keyword_vocab_max=50000,keyword_min_freq=5

# Audit first, then fit only caps producing distinct vocabularies.
.venv/bin/python scripts/keyword_cap_sweep.py --route filetypes/java_class
```

The Java class probe selected 11,408 training rows and 2,789 dev rows (289
malware, 2,500 benign), at seed 42 with a 100-tree budget and training malware
score floor 4. Training-document counts found 1,035 distinct ID words and
1,279 description words; only 557 and 712 respectively met frequency >=5.
Caps of 1k, 3k, 10k, 25k, and 50k therefore select identical vocabularies in
this cohort. Increasing the cap cannot add features here, even at frequency 1
until more distinct words enter the training data.

| Variant | Actual words | Dev recall, 0 FP | Dev recall, 1 FP |
| --- | ---: | ---: | ---: |
| Baseline | 0 | 81.31% | 81.31% |
| Rule-ID words | 557 | 80.62% | 81.66% |
| Description words | 712 | 79.24% | 79.24% |
| Both | 1,269 | 81.31% | 81.31% |

None of these four early-stopped models actually split on a keyword column;
the tiny recall changes are not evidence of learned keyword signal. Changing
feature-space width can also change column sampling of existing features.
Do not promote from this single-seed screen. Keep the cap tunable per model
and the 10k default unchanged.

The largest vocabulary adds about 50 KiB to a 1.26 MiB spec and raises dev
matrix nonzeros from 170,868 to 211,097. Measured tree-scoring medians were
0.20..0.42 ms for the 2,789-row batch (four threads, five warm measurements);
these exclude report extraction and are affected by the different tree counts
(4, 36, 5, 4). Cold/warm cache differences also prevent comparing the raw total
experiment times as pure training overhead. The audit and measurements are in
`out/experiments/keyword-caps-java-class/comparison.json`.

## Five-route keyword controls at 10%

```sh
.venv/bin/python scripts/keyword_route_controls.py \
  --routes java_class go c python javascript --sample-percent 10 \
  --output out/experiments/keyword-controls-10pct-confirm
```

This tests baseline, ID words, description words, and both on one exported
PostgreSQL snapshot. `COLLIMATOR_SAMPLE_PERCENT=10` selects canonical groups
by a rehashed canonical key, independently of the existing partition split.
All eligible train and dev rows in that sample are used at natural prevalence;
there are no balanced reservoirs or row-count caps. Training score floors are
zero. Locked test rows are excluded from screening and vocabulary discovery.

Column sampling is 100%, the tree budget is 180, and seeds 43 and 44 train on
each identical feature matrix. Both models are retained; individual-seed recall
at zero and one FP and actual keyword split usage drive the control comparison.
The averaged ensemble is recorded separately. The runner checks identical
base train/dev feature values, dev report revisions and labels, and reproduces
recorded ensemble recall from the saved models. A missing count-budget
threshold denotes no detections, including saturated-score tie cases.

Each route retains its selected cohort, per-row dev predictions, models, specs
and logs. Regenerable matrix/vocabulary caches are removed after the route
finishes unless `--keep-cache` is set. `comparison.json` is updated after each
configuration. Small sampled malware pools are reported explicitly; they can
make large percentage changes represent only one or two files.

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
