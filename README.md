# collimator

[![License](https://img.shields.io/github/license/atomdrift-project/collimator)](LICENSE)

collimator trains and evaluates the routed malware-detection models published as
[Azoth](https://github.com/atomdrift-project/azoth) and consumed by
[Atomdrift Scan](https://github.com/atomdrift-project/scan). It reads labeled
cleave reports from [hopper](https://github.com/atomdrift-project/hopper), trains
a general model plus format specialists, selects routing policies, and stages a
validated ONNX bundle.

This repository is for model developers and operators. To scan files, install
Atomdrift Scan instead.

## What it provides

- General, file-group, and file-type LightGBM models
- Three-seed ensembles for routes where averaging improves stability
- A 42-point false-positive grid from L0 through L25000
- A canonical deployment default of L25, or 0.25 expected false positives per
  million benign files
- Deterministic train/test partitioning and per-route evaluation reports
- ONNX export, bundle validation, and regression gates before publication
- Autonomous experiment search through
  [autocollie](https://github.com/atomdrift-project/autocollie)

Training and deployment use raw model probabilities. Thresholds are selected
on that same score scale; current Azoth bundles do not ship `calibrator.json`.

Calibration uses the **exported production ensemble on dev**, never scores from
fold models or one selected seed. Canonical archive groups stay in one partition.
Policy search sees only dev; test reports the saved decisions without choosing a
new threshold or strategy. Publication checks model/spec identities and preserves
them byte for byte. Legacy bundles without train-only provenance must be retrained.
OOF runs remain useful diagnostics, but cannot set another model's thresholds.

LightGBM early stopping uses average precision. When the validation set has fewer
than 30 examples of either class, training keeps the configured tree budget rather
than making an early-stop decision from a handful of examples.

## Requirements

- Python 3.11 or newer
- Make and a C/C++ build toolchain
- A PostgreSQL hopper database containing labeled cleave reports
- Substantial CPU, memory, disk, and time for full-corpus training

The Makefile creates `.venv/` and installs the pinned Python dependencies.

## Quick start

```bash
# Show the maintained targets and required parameters.
make help

# Train the deploy-bound ensemble on the full labeled corpus.
make azoth-full-train DB=postgres://hopper@localhost:5432/hopper

# Use the smaller balanced corpus for iteration.
make azoth-fast-train DB=postgres://hopper@localhost:5432/hopper
```

Successful training builds in an isolated run directory and publishes the
validated bundle under `out/models/azoth/` only after every gate passes.

## Run an experiment

```bash
make experiment \
  EXP_ROUTE=filetypes/python \
  EXP_IDEA=larger-leaves \
  EXP_NUM_LEAVES=128 \
  DB=postgres://hopper@localhost:5432/hopper
```

Experiment records land in `out/experiments/azoth/runs/`. Use a descriptive
`EXP_IDEA`; the JSON record is the durable comparison and audit trail.

To bootstrap a specialist before one is deployed, screen configurations first:

```bash
make autocollie-screen ROUTES=filetypes/go EXPERIMENTS=12

# Or try specific knobs on the best prior Go configuration:
make autocollie-screen ROUTES=filetypes/go \
  TRY=num_leaves=128,min_child_samples=50,reg_lambda=2

# Consume the saved results in a full bundle build:
make azoth-full-train
```

`make autocollie-full-train ROUTES=filetypes/go EXPERIMENTS=12` chains the
screen and full bundle build. `make autocollie` uses the automatic promotion
ladder and requires an existing deployed specialist.

Full training prefers registered promotions, then comparisons against the
deployed model on the same rows. Without either, it selects a provisional
configuration by PR AUC from recent runs evaluated on a common test set.
Unusable metrics and holdouts with fewer than 30 examples of either class
are excluded. The suite records the source and configuration per route in
`<bundle>/.autocollie/training_selections.json`; this does not register a
promotion. Explicit operator overrides take precedence.

Full training uses all eligible training rows and keeps the separate test
partition for evaluation. Screening sample caps and CPU/memory limits are
not carried into the specialist build. The default malware quality gate
keeps training malware with score at least 4, while retaining benigns and
test malware regardless of that training quality gate.

### Evaluation and cache integrity

General and specialist training reserve both development and locked test
partitions. Screens use development rows. Confirmation increases the training
budget while retaining the screen's evaluation cap, prevalence policy, and
evaluation seed (`EXP_EVAL_SEED`, default 42). Training seeds, sample budgets,
and malware quality cutoffs have independent sampling streams.

Automatic promotion requires a deployed-model comparison on identical row
versions, with proof that the deployed model did not train on those rows.
Confirmation also rejects changed evaluation rows. Older runs remain useful
configuration starting points, but must be screened again before confirmation.
Older deployed bundles need retraining before they can establish a development
baseline. Each newly trained route records its model digest and training
partitions in `training_provenance.json`.

Cache identities include relevant source contents, library versions, feature
allowlist contents when enabled, and database state. PostgreSQL uses its
transaction visibility snapshot, which is inexpensive but conservative:
unrelated database writes can cause cache misses. SQLite uses file contents.
Caches built while the database changes are not persisted. Evaluation records
also fingerprint the exact scored rows so unrelated writes do not invalidate
a paired comparison.

Cached runs restore their own keyed model, feature specification, and
provenance before reuse. Incomplete artifacts trigger retraining.

### Feature discovery

Training and autocollie discover a vocabulary from each route's current
training rows. No deployed model or feature allowlist is required. Enabled
feature knobs, frequency cutoffs, and per-family vocabulary caps determine
the candidate columns. Historical runs supply starting settings; their old
allowlist paths are not inherited. New feature configurations get new matrix
cache keys; training-only changes reuse the matrix.

New models (ABI 20) keep the strongest n-gram tokens by
`max(severity × confidence)` from an individual finding, with lexical ties.
Selection happens before vocabulary filtering in both training and scan.
Bigrams keep 512 tokens, trigrams 128, and tiered quadgrams 64; these budgets
bound vocabulary discovery without discarding an entire overflowing family.
Older models retain their original extraction behavior.

Vocabulary frequencies count samples, not repeated archive members. Exact
counts spill to scratch SQLite files under `out/cache/vocabulary` (override
with `COLLIMATOR_VOCAB_TMPDIR`); counts are never dropped when a batch fills.
Eligible features are ranked by frequency with deterministic ties.

Vocabulary workers recheck their memory budget every 30 seconds, increasing
task concurrency when RAM recovers and draining tasks when the budget shrinks.
The requested worker count remains the maximum; `COLLIMATOR_MEM_RESERVE_GB`,
`COLLIMATOR_MEM_PER_WORKER_GB`, `COLLIMATOR_MEM_CEILING_GB`, and
`COLLIMATOR_MEM_SHARES` still bound admission. Feature extraction takes a fresh
memory budget after vocabulary completes.

Identical single-file token sets are counted once per batch with their full
sample frequency. Multi-file overlaps still count each sample once. Worker
write caches stay warm until their shard is sealed, and a bounded background
merge queue overlaps SQLite writes with worker counting. Benign trigram
candidates are indexed once per worker and matched using set intersections.

Run the synthetic counting and merge benchmark with:

```bash
.venv/bin/python scripts/benchmark_vocabulary.py --repeat 3
```

Add `--baseline-dir DIR` to compare against snapshots named
`features_before.py` and `vocabulary_before.py`; every benchmark checks exact
counts. These component timings do not predict full-corpus runtime.

Singleton vocabularies use both benign and malware training samples, so benign
signals can become features too. Combination vocabularies (bigrams, trigrams,
and quadgrams) require support in malware samples. The classifier still learns
from both classes. Ordinary bigrams default to five distinct malware samples;
inherited explicit cutoffs are preserved, with a warning if they exceed the
route's malware count. Ordinary path trigrams require `trigram_min_freq`
malware samples before candidates are checked against the benign-frequency
ceiling.

Run the Python/Rust n-gram parity checks with:

```bash
.venv/bin/python scripts/check_ngram_parity.py --scan ../scan
```

This checks both ABI versions, depths 2–5, severity-floor overrides, archive
aggregation, ordering, and token-budget boundaries. `--reports reports.json`
adds real reports from a JSON array. Fixtures and failure logs are retained
under `out/diagnostics/ngram-parity`.

```bash
make autocollie-screen ROUTES=filetypes/go EXPERIMENTS=12
make autocollie-screen ROUTES=filetypes/go TRY=trait_path_depth=5,tiered_crit_trigrams=true
make azoth-full-train
```

Repeated `TRY` names sweep alternative values:

```bash
make autocollie-screen ROUTES=filetypes/go \
  TRY=trait_path_depth=4,trait_path_depth=3,trait_path_depth=2,trait_path_depth=5
```

This runs four trials from the same starting configuration. Different knob
names combine; repeating multiple knobs forms a Cartesian sweep. The sweep
must fit within `EXPERIMENTS` (default 12), or the command reports an error.
Use `make autocollie-dryrun` with the same arguments to preview it.

The malware training cutoff is also tunable:

```bash
make autocollie-screen ROUTES=filetypes/go \
  TRY=min_malware_score=0,min_malware_score=1,min_malware_score=2,min_malware_score=4
```

This filters training positives only; evaluation includes every score band.
Full training replays each selected route's cutoff, falling back to
`EXP_MIN_MALWARE_SCORE` (4) when history has none. Setting that variable
explicitly on the Make command line or in the environment overrides every
route, including with `EXP_MIN_MALWARE_SCORE=0`. Specialist benchmarks record
the effective cutoff as `min_malware_training_score`.

Symbol/import vocabularies and categorical metric key/value vocabularies can
be enabled independently, including symbol pairs/triples and key/value shape
and split-value tokens. The obsolete `text_encoding` knob is removed: compact
reports no longer carry its raw strings. Use `text_metrics_full` for retained
text metrics.

### Optional feature allowlist

A name filter can reduce the number of columns considered during training.
Use one only after measuring its resource savings and quality. It is not part
of the default screen or full-training workflow.

```bash
make azoth-build-allowlist
make azoth-build-allowlist AZOTH_ALLOWLIST_SIZE=10000
make azoth-build-allowlist AZOTH_ALLOWLIST_REFRESH=1
```

The builder discovers a fresh vocabulary using the same feature knobs as
`make experiment`, from a uniform sample of up to 6,000 non-test rows per
filetype. It covers all labeled filetypes by default. It retains frequent
columns and any names used by existing deployed tree splits; a deployed
bundle is optional and never limits the candidate vocabulary.
It streams IDs from the existing replica index, fetches metadata only for
the sample, and counts nonzero feature values in bounded extraction batches.
`AZOTH_ALLOWLIST_SAMPLING_WORKERS` defaults to 4 and
`AZOTH_ALLOWLIST_MAX_DB_WORKERS` to 24 to bound database connections.

Frequency counts live under `out/cache/azoth-allowlist/` for up to one hour.
The cache contains candidate names and their counts. Its identity includes
the database snapshot/mutation counters, extraction settings/code, sample
size and seed. Allowlist size changes
reuse counts when those inputs are unchanged; an audit observing database
changes is not cached. `AZOTH_ALLOWLIST_REFRESH=1` forces a recount, including
after in-place updates that database statistics have not yet reported.

Generation writes `out/models/azoth/allowed_features.json`. To explicitly use
the same filter for screening and training, pass
`AZOTH_ALLOWED_FEATURES_FILE=out/models/azoth/allowed_features.json` to both
commands. A missing or invalid selected file fails immediately.

To search repeatedly with a local OpenAI-compatible model:

```bash
make autocollie-loop \
  ROUTES=filetypes/python,filetypes/javascript \
  EXPERIMENTS=10 \
  AUTOCOLLIE_DB=postgres://hopper@localhost:5432/hopper
```

Autocollie produces candidates; it does not silently replace the deployed
bundle. Inspect a candidate before staging it:

```bash
make azoth-deploy AZOTH_ROOT=out/models/azoth-candidate-<route>-<key>
```

## Test the resulting bundle

```bash
atomscan --model-dir out/models/azoth suspect.bin
```

## Important paths

| Path | Purpose |
| --- | --- |
| `src/collimator/` | Data access, feature construction, training, thresholds, and export |
| `scripts/` | Routed evaluation, deployment, diagnostics, and regression gates |
| `experiments/` | Human-readable experiment history and methodology |
| `out/experiments/azoth/runs/` | Machine-readable experiment records |
| `out/models/azoth/` | Current validated source bundle |

See [CONTRIBUTING.md](CONTRIBUTING.md) before changing features, partitions, or
deployment gates. Model changes should include the resulting run record and a
clear comparison against the current route.

## License

collimator is available under the [Apache License 2.0](LICENSE).
