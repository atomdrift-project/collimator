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
The central vocabulary merge uses a 256 MiB SQLite page cache; each counting
worker keeps its 32 MiB cache. Merges translate packed token IDs with a single
cached key prefix, avoiding repeated integer unpacking for adjacent n-grams.

Vocabulary workers recheck their memory budget every 30 seconds, increasing
task concurrency when RAM recovers and draining tasks when the budget shrinks.
The requested worker count remains the maximum; `COLLIMATOR_MEM_RESERVE_GB`,
`COLLIMATOR_MEM_PER_WORKER_GB`, `COLLIMATOR_MEM_CEILING_GB`, and
`COLLIMATOR_MEM_SHARES` still bound admission. Feature extraction takes a fresh
memory budget after vocabulary completes.

Startup admission, worker budgets, and specialist fit budgets include ZFS ARC
above its minimum (`size - c_min` from `/proc/spl/kstat/zfs/arcstats`) in
addition to Linux's `MemAvailable`, matching htop's available-memory estimate.
Missing or invalid ARC counters fall back to `MemAvailable`. Host reserves,
memory shares, and the run's memory ceiling still apply; ARC reclaim may lag
allocations. Memory budgets use GiB.

Nightly keeps an unfinished run's snapshot in `out/nightly/resume/snapshot`.
Run `make nightly` again after an interruption to continue that snapshot.
Completed training and OOF scoring stages are reused only when their source,
configuration, artifact dependencies, and output hashes still match. The pin
bounds row IDs; it does not freeze the live corpus. Completed stages remain
reusable when rows below the pin change. There is no full-corpus checksum at
startup or publication. Calibration and publication gates run again using
production-model scores; reused OOF scores are diagnostics from completed work.
Partial-work recovery still validates its selected inputs, as described below.
Use `NIGHTLY_FRESH=1 make nightly` to select a new snapshot instead, or
`AZOTH_PIPELINE_RESUME=0` to rerun pipeline stages.

For fresh performance iterations, `make azoth-profile` runs the full production
and two-fold pipeline on approximately **1% of canonical hashes**. The first
32 bits of an MD5 digest of the canonical group key select the sample independently of the suffix bytes used for
train/dev/test and OOF partitions. General models, specialists, scoring, and
calibration select the same cohort; related files with the same canonical hash
stay together. Rehashing avoids bias from canonicalization picking the minimum
hash within an archive.

Test evaluation reuses the raw score table captured during dev calibration,
after checking its content hash, model and feature identities, and general
score cache. It applies the frozen thresholds to the captured test partition
without re-extracting features from a changing database.

Each invocation creates a new directory under `out/profiles/` containing models,
experiment outputs, caches, a pinned max ID in `run.json`, `pipeline.log`,
CPU profiles in `cpu/`, and live phase timings in `timings/`. It reads existing
replay configurations, but reuses no previous training artifacts. It runs
`azoth-validate` instead of publishing.
Sampling also explicitly blocks the publish/deploy targets. The profiling run
uses the nightly memory scope and refuses to overlap an active nightly/sweep.

```sh
make azoth-profile PROFILE_DRY_RUN=1         # inspect paths and sampling rule
make azoth-profile                         # fresh 1% run with cProfile
make azoth-profile PROFILE_PERCENT=5        # larger deterministic cohort
make azoth-profile PROFILE_PERCENT=2 PROFILE_TARGET_MINUTES=20 PROFILE_PROFILER=none
make azoth-profile PROFILE_STOP_STAGE=2     # just the three general models
.venv/bin/python scripts/azoth_profile_report.py out/profiles/<run>
```

`PROFILE_PIN=<max_id>` repeats the ID bound from an earlier run. Live row updates
can still change inputs under that bound. `PROFILE_PROFILER=none` measures runtime
without profiler overhead; `PROFILE_PROFILER=perf` records native CPU samples
across descendant processes/threads when host perf permissions allow it.
The default cProfile mode requires no tracing privileges and includes feature
workers, specialist workers, and the vocabulary merge thread. Its call timings
include waits and profiling overhead; summed profiles are not wall-clock time.
A small sample can fail quality gates or leave rare routes too small to train;
its metrics are for iteration, and the profiles remain available on failure.

Profiling iterations start at 1%, targeting a complete fresh run in 15 minutes
before increasing to 2% and a 20-minute target. `result.json` records elapsed
time, exit status, and whether the whole pipeline completed within the target.
Use `PROFILE_PROFILER=none` to verify wall time without cProfile overhead. Live
phase records include wall time, current-thread CPU time and process peak RSS;
30-second PostgreSQL samples report active backend wait states. Nested phases
and concurrent workers overlap, so their durations must not be added for an ETA.

For samples up to 2%, profiling uses an 8 GiB initial specialist-fit estimate
and four extraction workers per fit; measured 1% fit peaks were below 4.1 GiB.
The profiling worker budget is 48 total, split between the two training chains.
This admits several small fits instead of reserving 28 GiB for each. Live
memory admission and the 128 GiB hard scope still apply. Override with
`PROFILE_FIT_MEMORY_GB` and `PROFILE_EXTRACT_WORKERS_PER_FIT`; larger samples
default to the regular 28 GiB estimate and six extraction workers per fit.

Vocabulary counting keeps exact document frequencies. Workers aggregate compact
token-set signatures across fetch batches, then sort and reduce packed integer
keys in bounded NumPy chunks (262,144 combinations). Multi-file archives retain
per-document union semantics. Candidate discovery and benign prevalence both
combine up to 16 fetch batches per shard; workers also rotate between batches
after 60 seconds or 512 MiB on disk. The signature cache has an 8 MiB budget,
and only four completed shards queue behind the merge writer. These bounds do
not discard low-frequency keys. Counts and batch completion markers still commit
together for recovery. Deterministic token IDs let ordinary shards merge without
per-key Python remapping or a second sort. Full token strings detect hash
collisions; collisions and older checkpoint dictionaries use exact remapping.
`COLLIMATOR_VOCAB_SHARD_BATCHES` overrides the batch limit
for direct training runs. Timing files distinguish discovery and benign merges,
and record signature reuse and shard sizes.

For local aggregation experiments, capture a bounded set of counting inputs
from an existing model's score cohort, then replay without accessing PostgreSQL:

```sh
.venv/bin/python scripts/replay_vocabulary.py capture \
  --model out/profiles/<run>/models/azoth/general \
  --db "$DB" --rows 8192 --batch-size 170 --input /tmp/vocab-inputs.jsonl
.venv/bin/python scripts/replay_vocabulary.py compare --input /tmp/vocab-inputs.jsonl
```

The comparison fixes fetch boundaries, varies aggregation windows (8/16/32
batches), compares Python/native reducers and dense/deterministic IDs, and verifies every canonical
key/count. It reports counting/merging time and peak RSS separately from the
exact-count verification. This is an aggregation benchmark; it excludes database
fetches, report decoding, benign-candidate matching, and model training.

OOF route scoring reuses one extraction pool across routes and fold bundles.
Each task identifies its complete feature specification, and each worker retains
only its current extraction context. Different vocabularies with equal column
counts remain separate. Worker counts and in-flight batch limits still apply;
`azoth_oof_score_routes.py --worker-pool route` selects the previous pool-per-call
behavior for comparison. Bundle timing records include model loading, first-batch
latency, prediction, and worker fetch/extraction/context time (worker sums overlap).
Route metadata selection omits unused file paths so the existing covering index
can supply all required fields without fetching each row from the table.

To benchmark scoring without retraining, capture reports for rows already selected
by an existing run, then compare against the frozen inputs and models:

```sh
.venv/bin/python scripts/replay_route_scoring.py capture \
  --run out/profiles/<run> --db "$DB" \
  --capture /tmp/scoring-capture --rows-per-route 2048
.venv/bin/python scripts/replay_route_scoring.py compare \
  --capture /tmp/scoring-capture --output /tmp/scoring-comparison --workers 24
```

Both destinations must be new. The replay uses local SQLite reports, verifies
model/spec and database fingerprints, and compares every saved score and metadata
array exactly. Its timing excludes capture and fingerprint validation. It measures
scoring on a bounded cohort; it does not establish a fresh full-pipeline runtime.

Database selection scans and candidate counts need not shrink in direct
proportion to the sample percentage. Hopper's replica-only
`scripts/replica/training-index.sql` and `training-statistics.sql` migrations
support this exact sampling expression. The covering index selects the cohort;
metadata queries that need paths fetch them by primary key only after selecting
sampled IDs. Route scoring does not need those path lookups.
The one-time index build is separate from the fresh pipeline runtime.

Trigram extraction indexes learned triples by their first token, so archive
members only test triples whose first token is present. This preserves feature
values and the existing per-file token limits. On 1,000 archive reports, complete
feature extraction fell from 8.27 to 2.11 seconds with identical feature vectors.

Vocabulary counting also checkpoints each committed shard, including scalar
counts and completed batch IDs, in the experiment cache. Recovery hashes the
selected IDs and labels already in memory, feature settings, and code; it does
not scan the database again or require live training labels to remain unchanged.
Counting and extraction use those selected labels. Committed batches retain
counts from the reports they read; unfinished batches read current reports.
This is incremental processing of a live corpus, not an immutable content
snapshot. A different selection or selected label starts a different checkpoint.
Worker-count changes preserve the original batch boundaries.
Benign trigram prevalence uses a shared disk index with an 8 MiB
SQLite cache and at most 16 MiB of cached token-pair lookups per worker; it never
copies the full candidate vocabulary into workers. Uncommitted shards may be
recomputed after a crash. Once the feature spec is saved, completed counts are
removed; the spec and its identity remain reusable. Old runs without checkpoints
cannot be resumed from their anonymous scratch files.

Experiment evaluation uses the selected labels and captures row versions in
the same queries that fetch reports for extraction. Its revision describes the
inputs actually scored; later live label/report changes do not abort training.
Deleted or invalid reports are excluded with their IDs, keeping feature rows,
labels, and evaluation IDs aligned. Matrix caches retain this revision and
older caches without it are rebuilt. Baseline comparisons still require a
matching evaluation revision; changed live inputs are not treated as comparable
to captured results. Publication calibration and regression gates still rerun.

Vocabulary admission can drain to zero and wait when RAM is short, then grow
again after recovery. It also waits when kernel `MemAvailable` falls below
`COLLIMATOR_MEM_MIN_AVAILABLE_GB` (default 8), allowing ARC reclaim to catch up.
Manual nightly runs enter a systemd user scope with `MemoryHigh=112G`,
`MemoryMax=128G`, and `OOMPolicy=kill`, so an OOM terminates the training group.
A user systemd manager is required. `NIGHTLY_MEMORY_SCOPE=0` is an explicit
opt-out for runs already contained by another supervisor. The advisory ceiling
defaults to 112 GiB for training and 48 GiB for the sweep, and training no longer
lowers its OOM score by default.

Identical single-file token sets are counted once per batch with their full
sample frequency. Multi-file overlaps still count each sample once. Worker
write caches stay warm until their shard is sealed, and a bounded background
merge queue overlaps SQLite writes with worker counting. Benign trigram
candidates stay in the shared counts database and use bounded token-pair lookups.

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
