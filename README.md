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
- A canonical deployment default of L25 on the resolution-adjusted scale:
  approximately one observed false positive plus 25 per 100 million benign
  samples in each decision pool (exact formula in [LEVELS.md](LEVELS.md))
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

Policy selection maximizes recall within each filetype's shared FP allowance:
`floor(1 + (L - 1) * N_benign / 100_000_000)` for L>=1, and zero at L0.
General, group, and specialist components share that allowance. Selection and
the deployment gate count the union of detections from all levels up to L,
matching the runtime sweep; different false-positive files at different levels
cannot each spend the same allowance. The gate checks each filetype on held-out
test rows, so unused allowances elsewhere cannot hide one route's overrun.
Small pools are included, and the default no longer applies a 30x multiplier.
Nightly gates L25 and reports all other levels; requiring an L0 test pass would
impose a different, zero-observed-FP objective.

This is an empirical operating-point convention, not a population-rate
guarantee. Reports separate the nominal level, observed FP count/rate, and
one-sided 95% binomial upper bound. A passing L25 gate does not certify 25 FPs
per 100 million future files. Zero observed FPs also does not prove zero risk.
Compare recall at zero and one FP when researching small models; one unusually
high-scoring benign can make their difference large. Repeatedly tuning against
test results consumes that holdout; use fresh confirmation data for subsequent
selection. Existing deployed bundles are not recalibrated by these code changes.

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

For unstable LightGBM seeds or saturated scores, compare
`EXP_MAX_DELTA_STEP=0` (uncapped, the default) with values such as 2, 5, and 10.
Autocollie can search this knob per route and replay it during full training.
The effective leaf update cap is `learning_rate * max_delta_step`; tighter
caps can also cause early stopping before useful ranking develops. Compare
multiple seeds on common dev rows while initially holding class weights and
hard-negative settings fixed.

`EXP_LGBM_THREADS` is the per-fit CPU ceiling for experiments and all specialist
Make targets, including both OOF folds. Saved route configurations cannot raise
the specialist suite's current thread ceiling. Small CPU fits (at most 50,000
rows and 10 million sparse entries or dense cells) use at most four threads;
larger OpenMP teams can make these fits substantially slower.

Specialists also check whether the initial Hessian can support two leaves.
For unweighted binary GBDT fits, a conservative bound can prove that every seed
would be constant. Such routes record `unsplittable_initial_hessian` and use
the filegroup/general fallback instead of exhausting seed retries. Weighted
refits and other boosting modes retain the usual training and health checks.

To bootstrap a specialist before one is deployed, screen configurations first:

```bash
make autocollie-screen ROUTES=filetypes/go EXPERIMENTS=12

# Or try specific knobs on the best prior Go configuration:
make autocollie-screen ROUTES=filetypes/go \
  TRY=num_leaves=128,min_child_samples=50,reg_lambda=2

# Consume the saved results in a full bundle build:
make azoth-full-train
```

Current accepted training knobs live in `model-configs/<route>.json`, for example
`model-configs/filetypes/npm.json`. Nightly training and autocollie read the same
file. Edit `train_config`, `feature_env`, or `min_malware_training_score` there;
explicit experiment/CLI overrides take precedence. Successful autocollie
promotions update that file. Historical run records and the promotion registry
record decisions; they do not override an existing model configuration.
Deployment retains `accepted_config.json` beside each model and
`training_config.json` records effective specialist settings, including CLI
overrides, on subsequent training runs.

Recovered history lives in `out/autocollie/history/`: recent experiments and
older acceptance dependencies are retained together. The original archive is
not required by the recovered run reader. Recovery can be repeated with
`scripts/recover_autocollie_history.py`; it preserves active files on conflicts.

Autocollie's search objective is measured recall within the L25 FP-count
allowance described in [LEVELS.md](LEVELS.md), usually one observed FP on a
small development cohort. Run records expose this as `level_budget_recall`,
with its level, allowed/actual FP counts, and contract version. The historical
interpolated `recall_at_25_per_100M` field remains a separate diagnostic.
Prompts show measured recall, cohort revisions, accepted configurations and
explicit overrides. Unverified baseline comparisons cannot claim improvement.
Small-cohort gains need confirmation across seeds and more benign data.
If measured L25 recall ties on the same cohort, a PR AUC gain greater than
0.0002 qualifies for confirmation provided measured zero-FP recall does not
regress. Missing zero-FP evidence does not qualify for this tie-breaker.
PR AUC cannot compensate for lower L25 recall. Candidate selection applies
the same tie-breaker, and confirmation must preserve measured L25 recall.
Autocollie admits small filetype routes using the same support floors as
specialist training: `AZOTH_SPECIALIST_MIN_BAD` and
`AZOTH_SPECIALIST_MIN_GOOD` (both 50 by default). These are research admission
limits, not a publishing approval. Routes still need usable artifacts and
the normal confirmation/publishing checks. Concurrent route cycles default
to two independently of calibration parallelism. While awaiting a complete
LLM response, autocollie logs a waiting heartbeat every 30 seconds; that
heartbeat does not imply token generation is progressing.
Make-driven autocollie runs use `http://elrond:8000/v1` for proposals by default;
set `AUTOCOLLIE_OPENAI_BASE_URL` to override the endpoint. The model remains
`Qwen/Qwen3.8-27B`. Compact prompts retain accepted settings, measured research
history, knob constraints, and deployment rules. Initial endpoint probes took
27–45 seconds for Gem, C, and OOXML; this is a latency observation, not a
guarantee of proposal quality or full-sweep runtime.
Screening and promotion use separate queues: validation no longer holds a
screening slot. Promotions remain serial, with at most one queued result per
route in the current pass. Screens, paired baseline scoring, confirmation,
full training, and validation share a compute-job limit equal to
`ROUTE_CONCURRENCY`. During autocollie validation, calibration defaults to one
route at a time and policy search uses the per-job CPU budget; ONNX prediction
settings and all quality gates stay unchanged. Explicit make-argument overrides
still apply. Use service CPU and memory limits for hard resource bounds.
Autocollie PostgreSQL passes share a read-only exported snapshot across
screening, confirmation, baseline scoring, and validation. Feature workers
import that same snapshot; ingestion continues normally. The snapshot closes
at pass completion or cancellation, and the next pass sees newly ingested
data. Standalone experiments also hold a snapshot through extraction and fit.
For a research script spanning several extractions, use
`python scripts/corpus_snapshot.py --db "$DB" -- <command>`. Snapshot ownership
must remain alive until its workers finish; a PostgreSQL restart still requires
restarting the interrupted comparison. Long passes retain old database row
versions until they finish, so refresh at pass boundaries rather than pinning
an entire unlimited session.
Historical favorites are configurations to remeasure, including runs that
predate evaluation provenance. `make autocollie-replay KEY=<historical-key>`
screens those settings on current data, records the new key's `replay_of`, then
runs confirmation once and the normal promotion gates on that fresh key.
The whole ladder shares one database snapshot. `REPLAY_SCREEN_ONLY=1` stops
after screening and paired baseline scoring. `make autocollie-replay-favorites`
uses this ladder for each selected historical favorite and keeps logs under
`out/autocollie/replays/`; errors stop later stages for that candidate.
Use `COOLDOWN=0` to retry entries previously blocked by infrastructure errors.
Normal `confirm` still requires recorded evaluation provenance.
An exported PostgreSQL snapshot also supplies the pass's current maximum row
ID; a legacy cached `snapshot_max_id.txt` cannot hide newly ingested rows.
An explicitly requested maximum ID remains an intentional historical cutoff.
Confirm, promote, replay and auto derive extraction workers from
`MAX_CPU_THREADS / ROUTE_CONCURRENCY` unless `WORKERS` or `EXP_WORKERS` was
explicitly supplied. For research alongside another validation job, start with
`MAX_CPU_THREADS=24 ROUTE_CONCURRENCY=2`; service limits provide hard bounds.
Additional captured development comparisons can be retained in a run's
`research_evaluations` list, with `partition: "dev"`, `evaluation_revision`,
the measured level-budget fields and `evidence_path`. Autocollie includes
these in future prompts so a larger-cohort ranking reversal is not lost.
They inform research; they do not replace the paired metrics used by gates.

`trait_path_depth` is available from 1 through 12 (default 3); it changes
finding-prefix specificity and severity-prefixed n-grams, separately from
tree `max_depth`. Start with isolated depths 2, 3 and 4, then investigate 5
when warranted. Training-only follow-ups can reuse a frozen cohort's feature
matrix; feature expansion is not required in every autocollie batch.

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

For repeatability checks, freeze all selected reports and metadata in one
read-only database snapshot, then run fresh profiles against that local corpus:

```sh
.venv/bin/python scripts/freeze_profile_corpus.py --db "$DB" --percent 1 \
  --output out/profiles/frozen-1pct
make azoth-profile DB="$PWD/out/profiles/frozen-1pct/corpus.sqlite" PROFILE_PROFILER=none
make azoth-profile DB="$PWD/out/profiles/frozen-1pct/corpus.sqlite" PROFILE_PROFILER=none
```

The manifest records the pin, row/partition counts, and database checksum.
Both profiles still start with empty training caches; the repeated 1% predicate
selects the same rows, rather than taking another 1% of the frozen sample.
Local-corpus timings exclude replica fetch latency and should be reported
separately from PostgreSQL timings. Keep replay configurations fixed between
runs as well. Use the normal PostgreSQL `DB` for the full nightly run.

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

Vocabulary counting keeps exact document frequencies. DB workers persist compact
token-set signatures, and the parent combines their weights across shards before
expanding combinations. Large expansions use two independent temporary count
writers by default; `COLLIMATOR_VOCAB_REDUCE_WORKERS=1` selects serial expansion.
The final count-store merge remains serial, but receives one expanded store per
reducer instead of an expanded store for every worker shard.
`COLLIMATOR_VOCAB_MERGE_GROUP=2` optionally groups completed outputs in pairs and
combines equal keys in a disk-backed SQL sort before updating the destination.
The default is 1: grouped merging saves writes but costs additional sorting CPU.
Each group commits its counts and partition receipts atomically; recovery skips
committed groups. Parallel expansion workers use a 256 MiB SQLite cache and
bounded NumPy batches of 1,048,576 combinations. Larger batches combine more
repeated keys before writing, and bulk conversion avoids a Python loop per
SQLite argument. `COLLIMATOR_VOCAB_REDUCE_CACHE_MIB` tunes each worker's SQLite
cache (1–1024 MiB); `COLLIMATOR_VOCAB_REDUCE_KEYS` tunes its batch bound
(1–4,194,304 keys). Serial recovery keeps smaller transaction batches.
Multi-file archives retain
the existing per-document union path. Candidate discovery and benign prevalence both
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
Merge-queue waits are timed separately, with a log message for sustained waits.
Expansion reports combinations processed, partition completion, and durable
checkpoint counts. The parent emits a heartbeat every 30 seconds while waiting
for workers and announces each final merge before it starts.
The default `sorted` reducer uses exact external sort/reduce:
it combines duplicate keys through bounded streaming merges before writing each
key once per partition. This trades SQLite updates for temporary-file I/O; use
`scripts/benchmark_vocabulary_expansion.py` to compare it against `upsert` on the
same captured, unexpanded count database. `COLLIMATOR_VOCAB_REDUCER=upsert`
selects the bounded-batch SQLite updater for comparison. The benchmark opens its source read-only,
creates a separate output database, and reports timings, exact-count digests,
and ranked vocabularies. It does not train or publish a model.
Source signatures remain durable until every expansion partition commits its
counts and recovery receipt. Retries skip committed partitions even if the
worker budget or reducer changes; the original partition assignments stay fixed.
Serial expansion commits count increments and signature
removal in the same transaction.

Pinned OOF pipelines also share raw **general-vocabulary discovery counts**
between production and the two hash folds. Each selected training fold is
counted once and published as an immutable SQLite file. Production adds both
folds' counts; each fold model consumes only the rows it trains on. Frequency
cutoffs, benign-candidate prevalence, ghosts, rare elements, and sampled
auxiliary vocabularies remain specific to each model. Matching row selections
reduce discovery visits from approximately `2N` to `N`; this does not halve
feature extraction, model fitting, or total pipeline time.

Reuse requires exactly matching selected IDs, labels, feature configuration and
feature-code revision. Different selections or settings build separate count
stores. Cached counts represent the reports observed while that fold was built;
the ID pin does not freeze live report contents. Producers coordinate through a
file lock, partial counting resumes from committed batches, and publication
atomically moves the closed database. Consumers attach these files read-only,
persisting their source references, receipts, and token dictionaries atomically
instead of copying millions of count records. Recovery checks each source's
file identity and rejects missing or replaced stores. Keep the published files
with their consumers until the run no longer needs recovery.

Production sums frequencies across both folds before applying any cutoff or
top-k selection. It caches qualifying frequencies in temporary SQLite tables
to avoid repeating that aggregation. Fold consumers read their single source
directly. Benign counts stay local to each model, and trigram matching uses
indexed token-prefix lookups into the immutable sources. Token remapping still
handles collisions and older dictionaries exactly.

Trigram benign filtering uses bounded, exactly ranked shortlists. It selects
candidates in descending malware frequency and lexical tie order, then checks
their benign prevalence with a small in-memory index in each worker. Once the
requested number of candidates survives, unseen candidates cannot displace
them. Candidates that have not been checked are never treated as benign-free.
All selected training rows still contribute discovery counts, and every benign
row is checked for each shortlist. This changes the evaluation order, not the
frequency thresholds, final vocabulary size, or training sample size.
Pages start at 4,096 candidates and double up to a 65,536-candidate memory bound.
After four unsuccessful pages, filtering falls back to the exhaustive method;
the transition clears prior subset counts atomically to prevent double-counting.
The initial page size is configurable; `COLLIMATOR_TRIGRAM_SHORTLIST_SIZE` accepts 1 to
65,536. Batch counts and receipts commit together, and the current page and
selection cursor are checkpointed so recovery does not double-count batches or
skip ties. Logs report each selection round and benign batch progress.
`COLLIMATOR_TRIGRAM_SHORTLIST=0` selects exhaustive filtering for comparison;
changing filtering modes requires a new partial-vocabulary checkpoint.

The pipeline puts these count stores under its run checkpoint directory in
`shared-vocabulary/`; retain that directory for recovery or remove it with the
completed run's checkpoints. The extra retained stores trade disk space for
avoided recounting. `AZOTH_SHARED_VOCAB=0` disables pipeline setup;
`COLLIMATOR_SHARED_VOCAB_DIR` selects an explicit directory. Standalone callers
can pass `shared_cache_dir` and canonical-hash-derived `row_folds` to
`build_vocab_from_db`.

`scripts/benchmark_shared_vocabulary.py` compares complete vocabulary generation
on a bounded frozen cohort. Run `--mode independent` and `--mode shared` in
fresh processes/output directories with identical `--db`, saved `--cohort`,
and experiment `--run` inputs. It records actual discovery row visits, every
resulting vocabulary, and order-independent digests over every raw count.
Exact-count verification time is reported separately from vocabulary timing.

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

Additional replay modes are `--mode global` (serial global expansion),
`--mode parallel` (two expansion writers), `--mode parallel-batched` (two writers
with grouped final merging), and `--mode sorted` (an experimental
bulk SQL sort/reduce, available only in this benchmark). All modes verify every
canonical key/count against the same captured input. `--prefill <closed.sqlite>`
adds a mature count-store fixture; this mode compares packed counts, and reports
fixture-copy time separately, including its filesystem sync. CPU totals include child processes.

While a nightly is active, test changes in a separate source copy with
`PYTHONPATH` pointing at that copy. Use its own scratch/output paths and a
read-only captured input, rather than the replica or live checkpoint databases.
`scripts/verify_vocabulary_optimization.py` expects sibling `baseline/` and
`candidate/` copies. It runs the full tests and all replay variants on both the
captured stream and a separate synthetic multi-gigabyte count store. It refuses
to start unless its cgroup enforces at most two CPU cores, 8 GiB RAM, and
30 MB/s read/write limits. Use a system-managed service running as the user if
the user manager lacks the I/O controller; mount the live workspace read-only
and grant writes only to the experiment directory. These component timings do
not establish a full-corpus training ETA.

OOF route scoring reuses one extraction pool across routes and fold bundles.
Each task identifies its complete feature specification, and each worker retains
only its current extraction context. Different vocabularies with equal column
counts remain separate. Worker counts and in-flight batch limits still apply;
`azoth_oof_score_routes.py --worker-pool route` selects the previous pool-per-call
behavior for comparison. Bundle timing records include model loading, first-batch
latency, prediction, and worker fetch/extraction/context time (worker sums overlap).
Route metadata selection omits unused file paths so the existing covering index
can supply all required fields without fetching each row from the table.

Full-corpus threshold scoring streams compact metadata without sorting by ID;
each completed batch keeps IDs, canonical groups, labels, and predictions aligned.
Dedicated extraction workers receive their feature specification once at startup.
ONNX ensembles share bounded dense inputs across seeds and use eight non-spinning
threads per model by default (`COLLIMATOR_ONNX_THREADS` overrides this). Progress
logs report metadata scan time and separate worker and parent stage totals.
Deployment calibration defaults to two concurrent routes
(`AZOTH_CALIBRATE_PARALLELISM=2`), independently of training concurrency.
Spawned scorers share a read-only, memory-mapped row index instead of receiving
a full-corpus Python dictionary with every job. Extraction writes bounded
batches to disk-backed CSR arrays under `COLLIMATOR_MATRIX_DISK_DIR` (default
`out/cache/matrix-scratch`). Small routes can reuse feature-matrix caches;
routes above 50,000 rows avoid loading an entire NPZ matrix into RAM.
BLAS/OpenMP pools are limited during route scoring; ONNX keeps its existing
thread count and prediction batch boundaries to preserve score arithmetic.
Calibration logs completed routes and a waiting heartbeat every 30 seconds.
Labeled calibration workers fetch at most 64 reports at once and return compact
CSR arrays instead of Python lists of sparse coordinates and values. Admission
rechecks memory headroom throughout extraction; clean, inactive matrix pages are
reclaimable, while dirty pages and live allocations remain charged. Outer batch
boundaries and row order stay unchanged. Progress logs include rows, nonzeros,
written bytes, and throughput. Wait logs identify the blocking batch's row IDs,
completed followers, and cgroup pressure counters. Worker stack dumps repeat
after 120 seconds in a batch (`COLLIMATOR_EXTRACTION_STALL_SECONDS`; zero disables).
These changes preserve full-corpus coverage and all deployment gates. Score
reuse still requires matching models, features, and corpus identity; database
writes or a PostgreSQL restart can therefore require fresh scoring even for
unchanged models. A waiting heartbeat alone does not prove worker progress.
At load time, supported direct-input ONNX tree classifiers are remapped in memory
to the union of columns their splits actually use. Callers still supply the full
feature layout; projection happens before densification and is shared across
ensemble members. Model files, thresholds, missing-value routing, and ensemble
averaging remain unchanged. Original batch boundaries are preserved because
ONNX can change floating-point reduction order for short tail batches.
Unsupported graphs use the full input layout. Set
`COLLIMATOR_ONNX_PROJECT_INPUT=0` to disable projection for comparisons.
On 32,768 real rows, the earlier worker/threading changes reduced scoring from
52.4s to 20.4s with maximum probability difference below 9e-8. This bounded
benchmark excludes the full metadata scan and is not a full-corpus runtime claim.
The general model's input projection reduces 127,227 columns to 8,116. Three
alternating inference-only comparisons on 32,768 frozen corpus rows took
0.62–0.88s with projection versus 8.1–34.0s without it under concurrent host
load, with bit-identical probabilities. This excludes database extraction;
larger prediction batches or different thread counts are not enabled because
they can change floating-point results on short tails.

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

For model-quality comparisons, `scripts/compare_frozen_bundles.py capture`
accepts `--source <bundle-root>`, `--db`, `--capture <new-directory>`, and repeated
`--bundle name=<bundle-root>` arguments. It freezes the source score table's test
labels/partitions plus PE dev rows, captures reports in one read-only database
snapshot, and copies model/spec/config/policy files. It records any live label
changes without replacing the frozen labels. `replay --capture <directory>
--name <name> --output <new-directory> --workers 8` scores each captured bundle
locally. Place replay outputs under `<results>/<name>`, then run `compare
--capture <directory> --results <results> --output <new-directory>` for paired
counts and PE score/policy counterfactuals. Policies are never refitted; historical
bundles calibrated on all partitions retain their test-exposure limitation.

Auxiliary vocabulary scans choose the 5,000 smallest fixed row-ID hash ranks.
Small corpus changes no longer reshuffle a positional random sample. Logs include
the selected-ID digest; full vocabulary counts still cover all training rows.

Database selection scans and candidate counts need not shrink in direct
proportion to the sample percentage. Hopper's replica-only
`scripts/replica/training-index.sql` and `training-statistics.sql` migrations
support this exact sampling expression. The covering index selects the cohort;
metadata queries that need paths fetch them by primary key only after selecting
sampled IDs. Route scoring does not need those path lookups.
The one-time index build is separate from the fresh pipeline runtime.

To benchmark only threshold scoring with existing models, use
`make azoth-profile-scoring PROFILE_PERCENT=1 PROFILE_DIR=out/profiles/scoring-1pct`.
This compares 6, 12, then 6 extraction workers on the same sampled corpus and
database snapshot. Override the sequence with `PROFILE_SCORING_WORKERS`.
It checks exact score, label, and row-ID parity after aligning rows, saves an
extraction CPU profile, and writes only to the new profiling directory.
On the fixed 213,941-row sample measured on 2026-10-29, six workers took
228 and 222 seconds, while twelve took 165 seconds with identical scores.
Autocollie therefore uses up to twelve general threshold-scoring workers,
bounded by its per-job CPU budget; `AZOTH_THRESHOLD_WORKERS` overrides this.
Ordinary Make invocations default that setting to `EXP_WORKERS`.
Sampling is for iteration speed; final confirmation and deployment validation
still use their full-data gates. Small filetype quality studies need enough
class support and should usually use row budgets rather than a global 1% cut.

Trigram extraction indexes learned triples by their first token, so archive
members only test triples whose first token is present. This preserves feature
values and the existing per-file token limits. On 1,000 archive reports, complete
feature extraction fell from 8.27 to 2.11 seconds with identical feature vectors.
Bigram and severity n-gram lookups now use the same first-token indexing.
Finding summaries, normalized metrics, and risk statistics are reused within
each report, then released before the next report. Together these changes
reduced measured extraction time from 42.84 to 21.66 seconds on a fixed
21,452-report sample, with exact parity across all 127,227 general-model
feature columns and ONNX scores. This measures time spent extracting features, excluding fetching and prediction;
complete scoring and full-pipeline wall times require separate benchmarks.
The subsequent fixed 1% scoring comparison covered 213,940 rows using production
unordered scheduling under the same 12-core CPU limit. The original extractor
with six workers took 303.59 and 245.08 seconds; the optimized extractor with
twelve workers took 106.92 seconds, 61.0% below the baseline average. Sorted row
IDs, labels, and every ONNX score matched exactly. This is a sampled scoring
benchmark, not a measured 100% validation or nightly runtime reduction.

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
Manual nightly runs enter a systemd user scope with `MemoryHigh=156G`,
`MemoryMax=160G`, and `OOMPolicy=kill`, so an OOM terminates the training group.
A user systemd manager is required. `NIGHTLY_MEMORY_SCOPE=0` is an explicit
opt-out for runs already contained by another supervisor. The advisory ceiling
defaults to 144 GiB for training and 48 GiB for the sweep, leaving room for fit
allocations above the worker-admission ceiling. Training no longer
lowers its OOM score by default.

The pipeline samples cgroup memory every 30 seconds. Its main log reports
`[memory] THROTTLED` or `[memory] PRESSURE` with usage, soft/hard limits,
new limit/OOM events, and the percentage of the interval lost to all-task
memory stalls. It also reports when pressure clears. Stage heartbeats alone
do not prove worker progress. Worker admission respects ancestor cgroup limits
as well as host headroom. A 160 GiB cap is not reserved RAM: concurrent build
jobs and databases can still cause a host-wide OOM.

General fits default to 32 threads (`AZOTH_GENERAL_THREADS` overrides this,
capped by the available CPU share). The pipeline coordinates additional fit
allocations through `COLLIMATOR_FIT_RESOURCE_DIR`: a process reserves its
estimated growth before allocating, and fetch workers account for outstanding
reservations. Already admitted work keeps running while new admissions wait.
Reservations disappear when their owner exits, including after a crash. These
estimates include sparse matrix copies and thread-dependent histogram storage;
they are admission estimates, not a guarantee against OOM. Admission waits
without a deadline by default, logging the fit estimate, current headroom,
outstanding reservations and host reserve. `COLLIMATOR_FIT_WAIT_SECONDS=0`
means unlimited waiting; a positive value opts into a deadline. Waiting never
forces an allocation beyond the measured budget.

For fit admission, the pipeline identifies the build runner via
`COLLIMATOR_FIT_BOUNDED_CGROUPS` (colon-separated cgroup directories). When
their hard limits can be read, the host reserve is 16 GiB plus their remaining
growth allowance, capped at the conservative 48 GiB default. Reclaimable file
cache does not reduce the growth allowance. Missing or unlimited competitor
limits retain 48 GiB; an explicit `COLLIMATOR_MEM_RESERVE_GB` overrides this
policy. This changes admission only, not the 160 GiB hard limit or the models.

Before fit admission and after fitting, coordinated runs collect unreachable
objects and, where supported, return unused native allocator pages to the OS.
The log reports the actual drop in anonymous memory. Live models and matrices
remain referenced; admission uses newly measured headroom rather than assuming
that retained heap is reusable. This prevents freed workspaces from one seed
blocking the next seed's reservation.

Extraction streams CSR arrays to `COLLIMATOR_MATRIX_DISK_DIR` (default
`out/cache/matrix-scratch`) instead of retaining all blocks and then copying
them into a combined matrix. Keep this on a disk-backed filesystem with space
for concurrent matrices. The mapped arrays are reclaimable; they are temporary
scratch, not recovery checkpoints. Fetch admission adjusts during extraction
while retaining row order. Full nightly runs capture one pinned selection of
row IDs and labels and derive both hash folds from it, allowing exact reuse of
fold discovery counts even when the live database changes between stages.

Training computes sparse means and variances in bounded float64 blocks,
releases the combined holdout after splitting calibration/evaluation, and
scores hard negatives in bounded batches. These avoid full-matrix temporary
copies without dropping samples, features, or hard-negative candidates.

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

Training and scoring keep samples whose fact profile omits some model inputs.
Available facts are extracted normally; absent inputs use the existing defaults
(typically zero). Each extraction worker warns once per profile and feature
layout. Reduced reports do not remove metrics discovered in other reports from
the vocabulary. Explicit fact-profile compatibility checks remain strict.

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
