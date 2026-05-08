# Azoth-Light Experiments

## 2026-04-30: GPU Ablation Screen

Purpose: identify obvious dead-weight feature groups before adding new azoth-light experiments.

Command:

```sh
make ablation MODEL=azoth-light DEVICE=cuda \
  ABLATE_SAMPLES=120000 ABLATE_TEST_SAMPLES=30000 \
  TRAIN_ESTIMATORS=50 TRAIN_EARLY_STOPPING=10 \
  ABLATE_OUTPUT=out/models/azoth-light/ablation_screen.json \
  EXP_TAG=_screen \
  ABLATE_GROUPS="bigrams unsigned_bigram elements rare atktri mbctri trigram crittri critbi mbcbi atkbi inter metrics skeleton filetype ghost missing formula ext intent_gap gap"
```

Artifacts:

- JSON: `out/models/azoth-light/ablation_screen.json`
- Log: `out/models/azoth-light/logs/2026-04-30T14-11-54-ablation_screen.log`

Run shape:

- Model: `azoth-light`
- Device: CUDA
- Train/test sample cap: 120k train, 30k test
- Trees: 50, depth 12, learning rate 0.05, early stopping 10, 2-fold CV
- Baseline features in this screen: 16,982

Important caveat: this is a fast screen, not the final decision run. It used only 50 trees and the ablation runner rebuilt matrices once because cache support had not existed yet. After this run, ablation was updated to support the experiment matrix cache via `--cache-dir` and `--max-id`.

| Ablation | Drop | Features Removed | Test F1 | Delta F1 | Test FP | Delta FP | Test FN | Delta FN | Read |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | - | 0 | 0.9839 | 0.0000 | 121 | 0 | 503 | 0 | Baseline for this screen. |
| drop:bigrams | `bigrams` | 3,692 | 0.9840 | +0.0001 | 128 | +7 | 492 | -11 | Large drop, essentially neutral. Confirm. |
| drop:unsigned_bigram | `unsigned_bigram` | 3,692 | 0.9870 | +0.0032 | 181 | +60 | 323 | -180 | Strong recall gain, higher FP. Candidate if level thresholds absorb FP. |
| drop:elements | `elements` | 2,507 | 0.9869 | +0.0030 | 182 | +61 | 329 | -174 | Similar to unsigned bigrams; candidate. |
| drop:rare | `rare` | 1,345 | 0.9854 | +0.0015 | 149 | +28 | 418 | -85 | Candidate, smaller tradeoff. |
| drop:atktri | `atktri` | 500 | 0.9874 | +0.0035 | 204 | +83 | 288 | -215 | Candidate, but raises FP. |
| drop:mbctri | `mbctri` | 500 | 0.9879 | +0.0040 | 218 | +97 | 255 | -248 | Best F1 in screen; verify at real budget. |
| drop:trigram | `trigram` | 500 | 0.9873 | +0.0035 | 221 | +100 | 273 | -230 | Candidate, but FP-heavy. |
| drop:crittri | `crittri` | 500 | 0.9873 | +0.0034 | 199 | +78 | 296 | -207 | Candidate. |
| drop:critbi | `critbi` | 500 | 0.9865 | +0.0027 | 164 | +43 | 359 | -144 | Candidate. |
| drop:mbcbi | `mbcbi` | 500 | 0.9875 | +0.0036 | 212 | +91 | 276 | -227 | Candidate. |
| drop:atkbi | `atkbi` | 500 | 0.9870 | +0.0032 | 180 | +59 | 324 | -179 | Candidate. |
| drop:inter | `inter` | 76 | 0.9838 | -0.0001 | 125 | +4 | 503 | 0 | Neutral; likely safe to drop if simplifying. |
| drop:metrics | `metrics` | 255 | 0.9863 | +0.0024 | 219 | +98 | 316 | -187 | Candidate but FP-heavy. |
| drop:skeleton | `skeleton` | 91 | 0.9872 | +0.0034 | 199 | +78 | 299 | -204 | Candidate. |
| drop:filetype | `filetype` | 76 | 0.9839 | 0.0000 | 121 | 0 | 503 | 0 | No effect in this screen. |
| drop:ghost | `ghost` | 11 | 0.9869 | +0.0030 | 184 | +63 | 326 | -177 | Oddly positive; verify because tiny group. |
| drop:missing | `missing` | 11 | 0.9854 | +0.0016 | 151 | +30 | 414 | -89 | Candidate. |
| drop:formula | `formula` | 3 | 0.9871 | +0.0033 | 177 | +56 | 323 | -180 | Oddly positive; verify because tiny group. |
| drop:ext | `ext` | 6 | 0.9870 | +0.0032 | 183 | +62 | 322 | -181 | Oddly positive; verify because tiny group. |
| drop:intent_gap | `intent_gap` | 4 | 0.9868 | +0.0030 | 184 | +63 | 328 | -175 | Oddly positive; verify because tiny group. |
| drop:gap | `gap` | 3 | 0.9875 | +0.0036 | 200 | +79 | 288 | -215 | Oddly positive; verify because tiny group. |

Initial interpretation:

- The screen mostly says azoth-light is recall-limited at this operating point: many drops improve F1 by raising recall while allowing more FPs.
- The biggest simplification candidates are `unsigned_bigram`, `elements`, `rare`, and the n-gram families. They remove thousands of columns and did not hurt this quick held-out F1 screen.
- Do not remove tiny groups solely from this run. Positive results for `formula`, `ext`, `gap`, `intent_gap`, and `ghost` are plausible calibration/threshold noise at 50 trees.
- Before changing defaults, rerun finalists with the normal azoth-light budget and a pinned cache key, then judge against level thresholds and full-corpus FP-per-million, not just F1.

Follow-up command template:

```sh
make ablation MODEL=azoth-light DEVICE=cuda \
  ABLATE_MAX_ID=<snapshot_id> \
  ABLATE_SAMPLES=120000 ABLATE_TEST_SAMPLES=30000 \
  TRAIN_ESTIMATORS=400 TRAIN_EARLY_STOPPING=50 \
  ABLATE_OUTPUT=out/models/azoth-light/ablation_confirm.json \
  EXP_TAG=_confirm \
  ABLATE_GROUPS="unsigned_bigram elements rare mbctri mbcbi atktri trigram crittri critbi atkbi skeleton metrics"
```

## 2026-04-30: Normal-Budget Ablation Confirmation

Purpose: confirm the fast 50-tree pruning screen with the normal azoth-light budget before cutting feature defaults.

Command:

```sh
make ablate MODEL=azoth-light DEVICE=cuda \
  ABLATE_MAX_ID=7693940 \
  ABLATE_SAMPLES=120000 ABLATE_TEST_SAMPLES=30000 \
  TRAIN_ESTIMATORS=400 TRAIN_EARLY_STOPPING=50 \
  ABLATE_OUTPUT=out/models/azoth-light/ablation_confirm.json \
  EXP_TAG=_confirm \
  ABLATE_GROUPS="unsigned_bigram elements rare mbctri mbcbi atktri trigram crittri critbi atkbi skeleton metrics"
```

Artifacts:

- JSON: `out/models/azoth-light/ablation_confirm.json`
- Log: `out/models/azoth-light/logs/2026-04-30T14-52-27-ablation_confirm.log`
- Matrix cache: `out/cache/matrix_705613c879006fef*`

Run shape:

- Model: `azoth-light`
- Device: CUDA
- Snapshot: `max_id=7693940`
- Train/test sample cap: 120k train, 30k test
- Trees: 400, depth 12, learning rate 0.05, early stopping 50, 2-fold CV
- Baseline features: 16,841

| Ablation | Features Removed | CV F1 | Test F1 | Delta F1 | Test FP | Delta FP | Test FN | Delta FN | Read |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 0 | 0.9933 | 0.9910 | 0.0000 | 107 | 0 | 162 | 0 | Baseline. |
| drop:unsigned_bigram | 3,694 | 0.9930 | 0.9902 | -0.0008 | 70 | -37 | 222 | +60 | Not a quality win; lowers FP but loses recall. Might be useful only for an ultra-low-FP variant. |
| drop:elements | 2,562 | 0.9922 | 0.9912 | +0.0002 | 137 | +30 | 126 | -36 | Near-neutral, recall-favoring. Keep as candidate only if thresholds prefer recall. |
| drop:rare | 1,382 | 0.9927 | 0.9914 | +0.0003 | 116 | +9 | 143 | -19 | Small positive; possible safe simplification, needs threshold check. |
| drop:mbctri | 500 | 0.9927 | 0.9913 | +0.0003 | 139 | +32 | 123 | -39 | Recall-favoring; not an obvious default cut without FP budget check. |
| drop:mbcbi | 440 | 0.9927 | 0.9909 | -0.0001 | 93 | -14 | 180 | +18 | Slight quality loss; lowers FP. |
| drop:atktri | 500 | 0.9932 | 0.9916 | +0.0006 | 109 | +2 | 143 | -19 | Good candidate: better recall with almost unchanged FP. |
| drop:trigram | 500 | 0.9930 | 0.9918 | +0.0008 | 109 | +2 | 136 | -26 | Best normal-budget screen result; candidate. |
| drop:crittri | 499 | 0.9933 | 0.9918 | +0.0008 | 113 | +6 | 133 | -29 | Best normal-budget screen result; candidate. |
| drop:critbi | 487 | 0.9930 | 0.9916 | +0.0006 | 110 | +3 | 142 | -20 | Candidate. |
| drop:atkbi | 378 | 0.9927 | 0.9912 | +0.0002 | 136 | +29 | 128 | -34 | Recall-favoring but FP cost is higher. |
| drop:skeleton | 92 | 0.9930 | 0.9916 | +0.0006 | 104 | -3 | 148 | -14 | Strong small cut: fewer FP and fewer FN in this sample. |
| drop:metrics | 248 | 0.9921 | 0.9897 | -0.0013 | 105 | -2 | 202 | +40 | Keep. Dropping metrics hurts recall materially. |

Decision from confirmation:

- Do not broadly prune the large groups yet. At 400 trees, the broad F1 gains from the 50-tree screen mostly collapsed.
- Keep `metrics`; it is not dead weight for azoth-light.
- The best confirmation candidates are `trigram`, `crittri`, `atktri`, `critbi`, and `skeleton`.
- `rare` is a possible simplification candidate, but the gain is small and needs full-corpus threshold validation.
- `unsigned_bigram` is not a quality win, but it reduces FP in this sampled test set. It may be worth testing as a separate ultra-low-FP profile rather than a default pruning choice.

Next candidate train:

- Conservative: drop `trigram`, `crittri`, `atktri`, `critbi`, `skeleton`.
- Optional recall-favoring variant: conservative + `rare`.
- Do not drop `metrics`.

## 2026-04-30: Pruned Candidate Training

Purpose: test the confirmed feature cuts as complete azoth-light candidates before changing defaults.

Shared run shape:

- Snapshot: `EXP_MAX_ID=7693940`
- Device: CUDA
- Train/test sample cap: experiment default 120k/30k
- Trees: 400, depth 14, learning rate 0.05, early stopping 50
- Matrix cache: experiment cache under `out/cache`

| Model | Dropped Prefixes | Features | Test Precision | Test Recall | Test F1 | ROC AUC | Brier | Read |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `azoth-light-baseline` | - | 16,841 | 0.9884 | 0.9937 | 0.9911 | 0.9993 | 0.0065 | Unpruned LightGBM baseline. |
| `azoth-light-pruned` | `trigram,crittri,atktri,critbi,skeleton` | 14,763 | 0.9878 | 0.9943 | 0.9910 | 0.9993 | 0.0066 | Smaller, roughly neutral F1, slightly recall-favoring. |
| `azoth-light-pruned-rare` | `trigram,crittri,atktri,critbi,skeleton,rare` | 13,381 | 0.9906 | 0.9925 | 0.9915 | 0.9994 | 0.0064 | Best sampled precision/F1 and smallest candidate. |

Candidate decision:

- Promote `azoth-light-pruned-rare` as the current azoth-light challenger for full-corpus threshold validation.
- Keep `azoth-light-baseline` as the unpruned control.
- Do not delete the dropped feature families from the code yet; keep them selectable via `DROP_FEATURE_PREFIXES` until repeated snapshots confirm the result.

## 2026-04-30: Full-Corpus Threshold Comparison

Purpose: compare `litmus-xg`, unpruned azoth-light, and the best pruned azoth-light candidate using level thresholds measured against the entire labeled corpus, including low-score samples.

Commands:

```sh
make thresholds MODEL=azoth-light-pruned-rare WORKERS=128
make thresholds MODEL=azoth-light-baseline WORKERS=128
make thresholds MODEL=litmus-xg WORKERS=128
```

Artifacts:

- `out/models/azoth-light-pruned-rare/threshold_tuning.json`
- `out/models/azoth-light-baseline/threshold_tuning.json`
- `out/models/litmus-xg/threshold_tuning.json`
- Score caches: `out/models/*/threshold_scores.npz`

Corpus note: the three reports were generated at slightly different moments, so labeled corpus sizes differ by a few thousand rows. The comparison is still directionally useful, but the next release gate should pin one corpus snapshot for all candidates.

| Model | Samples | Malware | Benign | L5 Hostile Recall | L5 Hostile FP | L5 Suspicious Recall | L5 Suspicious FP | L9 Suspicious Recall | L9 Suspicious FP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `litmus-xg` | 1,650,556 | 326,229 | 1,324,327 | 37.63% | 1 | 62.60% | 13 | 74.94% | 66 |
| `azoth-light-baseline` | 1,647,114 | 326,229 | 1,320,885 | 40.78% | 1 | 69.49% | 13 | 83.60% | 66 |
| `azoth-light-pruned-rare` | 1,645,801 | 326,222 | 1,319,579 | 50.66% | 1 | 70.80% | 13 | 82.64% | 65 |

Policy comparison:

| Model | Default Suspicious | Default Hostile | Low-FPR Suspicious | Recall+FPR Hostile |
| --- | ---: | ---: | ---: | ---: |
| `litmus-xg` | 62.60% recall at 9.8 FP/1M | 37.63% recall at 0.8 FP/1M | 78.94% recall at 99.7 FP/1M | 85.00% recall at 219.7 FP/1M |
| `azoth-light-baseline` | 69.49% recall at 9.8 FP/1M | 40.78% recall at 0.8 FP/1M | 87.73% recall at 99.9 FP/1M | 85.00% recall at 60.6 FP/1M |
| `azoth-light-pruned-rare` | 70.80% recall at 9.9 FP/1M | 50.66% recall at 0.8 FP/1M | 87.54% recall at 99.3 FP/1M | 85.00% recall at 62.9 FP/1M |

Read:

- `azoth-light-pruned-rare` is the strongest current challenger at the strict default levels: it improves hostile L5 recall by +13.03 percentage points over `litmus-xg` at the same 1-FP budget, and +9.88 points over unpruned azoth-light.
- Unpruned azoth-light is slightly better at suspicious L9 than pruned-rare, but pruned-rare wins at the stricter default hostile and suspicious levels while using fewer features.
- Both azoth-light variants are far better than `litmus-xg` at the recall+FPR hostile policy: roughly 60-63 FP/1M versus 219.7 FP/1M for the same 85% malware recall.
- The next default candidate should be `azoth-light-pruned-rare`, pending one pinned-snapshot rerun and throughput profiling.

Threshold-cache performance notes:

- `azoth-light-pruned-rare` score-cache build took about 18 minutes before progress instrumentation was added.
- `azoth-light-baseline` score-cache build took about 21 minutes.
- `litmus-xg` score-cache build scored 1,650,556 rows in 1,263.3 seconds, averaging 1,307 rows/sec after a slow startup.
- Progress was bursty: the first litmus progress point arrived after about 2.5 minutes, then batches alternated between stalls and bursts. This points to worker startup, DB fetch, JSON parse, feature extraction, and ordered batch waiting as the main cache-building bottlenecks.

Performance actions:

- Add shardable threshold score-cache generation so workers can write independent row-id/probability shards and avoid one ordered parent-side stream.
- Carry row IDs through unordered extraction batches so slow batches cannot block faster completed batches. Completed for the parent-side extraction stream; independent shard files remain a possible next optimization.
- Profile DB fetch and JSON parse separately from feature extraction and model prediction.
- Add periodic progress to experiment/ablation cache builders too, using the same low-noise row/sec style.

## 2026-04-30: Threshold Cache Snapshot Pinning

Purpose: make threshold and false-positive cache comparisons explicit while Hopper is continuously ingesting new rows.

Implemented:

- `THRESHOLD_MAX_ID=<id>` Make variable for `thresholds`, `thresholds-refresh`, `false-positives`, `near-false-positives`, `false-negatives`, and `near-false-negatives`.
- Matching CLI `--max-id` option on all threshold/FP/FN commands.
- Threshold score caches now persist:
  - `corpus_samples`
  - `corpus_malware`
  - `corpus_benign`
  - `corpus_max_row_id`
  - `corpus_requested_max_id`
- Cache loading logs the cache corpus and the current DB corpus delta.
- Cache reuse rejects a cache built for a different pinned `--max-id`.

Validation:

```sh
make thresholds MODEL=azoth-light-pruned-rare WORKERS=128 THRESHOLD_TOP_ERRORS=0 THRESHOLD_MAX_ID=7899260
```

Observed:

- Cache reused: 1,645,801 rows, max_row_id 7,899,260.
- Current DB at that same max row ID: +2 eligible rows versus cache, max_row_id unchanged.

Read:

- The prior cache-size concern is consistent with a live ingesting/changing database rather than a gross scoring omission.
- For release comparisons, pin all candidates to the same `THRESHOLD_MAX_ID`.
- For live operational reporting, leave `THRESHOLD_MAX_ID` unset and rely on the cache-vs-current DB delta log to know how stale the snapshot is.

## 2026-04-30: Unordered Threshold Cache Builder

Purpose: remove head-of-line blocking from full-corpus threshold and false-positive cache construction.

Implemented:

- Added an unordered DB-backed extraction path for threshold scoring.
- Each completed worker batch carries row metadata with labels, so predictions, labels, paths, SHA256s, and scores stay aligned without requiring global row order.
- Threshold cache writes still produce the same `.npz` schema plus corpus metadata.
- Existing training/extraction paths keep their ordered extractor.

Validation:

```sh
.venv/bin/python -u -m collimator tune-thresholds \
  --db postgres://hopper@localhost:5432/hopper \
  --model out/models/azoth-light-pruned-rare/model.txt \
  --spec out/models/azoth-light-pruned-rare/feature_spec.json \
  --workers 8 --limit 10000 --top-errors 0
```

Observed: 10,000 rows scored in 1.4s, about 6,955 rows/sec.

Full refresh:

```sh
make thresholds-refresh MODEL=azoth-light-pruned-rare WORKERS=128 THRESHOLD_TOP_ERRORS=0
```

Observed:

- Corpus: 1,659,186 rows; 326,229 malware, 1,332,957 benign.
- Scoring complete: 416.8s, 3,980 rows/sec.
- Cache saved: `out/models/azoth-light-pruned-rare/threshold_scores.npz`, max_row_id 7,942,262.
- Batch size: 1,024 rows.

Comparison:

- Previous ordered full-corpus scoring was roughly 18-21 minutes.
- New unordered scoring is about 7 minutes for a slightly larger corpus, a practical 2.6x-3.0x wall-clock improvement over the pruned-rare run and about 3.0x over the litmus-xg timed run. Early throughput reached ~25k rows/sec, but tail batches pulled end-to-end throughput down to ~4k rows/sec.

False-positive cache reuse:

```sh
make false-positives MODEL=azoth-light-pruned-rare WORKERS=128 TOP_ERRORS=5
```

Observed:

- Cache reused immediately.
- Current DB had already grown by +2,107 eligible rows and +10,433 max row ID since the refresh.
- Level-9 false positives: 66 raw rows, 58 outer files.

Next performance target:

- Split the remaining tail latency by timing DB fetch, JSON decode, feature extraction, and prediction per batch.
- Consider shard files or a temporary row/probability table so the parent does less final in-memory aggregation for multi-million-row corpora.

## 2026-04-30: Threshold Cache Profiling

Purpose: explain the remaining tail latency after switching to unordered extraction.

Instrumentation added:

- Worker-side DB fetch timing.
- Worker-side feature extraction timing.
- Parent-side sparse matrix assembly timing.
- Parent-side prediction timing.
- Top five slowest batches by total stage time.

Full 1,024-row batch profile:

```sh
make thresholds-refresh MODEL=azoth-light-pruned-rare WORKERS=128 THRESHOLD_TOP_ERRORS=0
```

Observed:

- Corpus: 1,662,847 rows; max_row_id 7,956,839.
- Scoring complete: 421.6s, 3,945 rows/sec.
- Stage totals summed across workers:
  - DB fetch: 2,372.7s
  - feature extraction: 29,466.0s
  - matrix assembly: 43.2s
  - prediction: 40.9s
- Slowest batch: 1,024 rows, IDs 1,074,834-1,077,936, total 300.5s, fetch 74.4s, extraction 226.0s.

Slow batch inspection:

- The worst range has very large benign source archives:
  - `reactos-reactos-0.4.15-release-source.tar.gz`: ~82MB JSON
  - `pytorch-pytorch-v2.10.0-source.tar.gz`: ~81MB JSON
  - `dotnet-roslyn-v4.0.1-source.tar.gz`: ~63MB JSON
- Other slow ranges are mostly large VXUG reports around 1-6MB JSON.
- Prediction is not the bottleneck. Extraction over huge JSON reports is.

Batch-size follow-up:

- Changed unordered threshold extraction to use `_feature_batch_size(n_workers)` instead of forcing 1,024-row batches.
- With 128 workers this uses 128-row batches, spreading giant reports across more workers.

Full 128-row batch profile:

```sh
make thresholds-refresh MODEL=azoth-light-pruned-rare WORKERS=128 THRESHOLD_TOP_ERRORS=0
```

Observed:

- Corpus: 1,662,847 rows; max_row_id 7,956,839.
- Scoring complete: 357.7s, 4,649 rows/sec.
- Stage totals summed across workers:
  - DB fetch: 2,426.1s
  - feature extraction: 30,770.2s
  - matrix assembly: 68.3s
  - prediction: 204.9s
- Slowest batch: 128 rows, IDs 1,076,012-1,076,288, total 88.3s, fetch 13.2s, extraction 75.0s.

Read:

- Smaller batches reduce wall-clock time by about 15% for this corpus by shrinking the worst tail batch from ~300s to ~88s.
- More tasks increase matrix/prediction overhead, but the tail reduction wins.
- The next improvement should be size-aware batching: include JSON length in metadata and pack batches by estimated bytes/work, not just row count.
- A second possible improvement is a special path for extremely large source archives, because a small number of 60-80MB reports dominate the tail.

Size-aware batching trial:

- Added optional `COLLIMATOR_THRESHOLD_SIZE_AWARE_BATCHES=1`.
- The size-aware path includes `LENGTH(cleave_result)` in metadata and caps unordered batches with `COLLIMATOR_THRESHOLD_BATCH_BYTES` (default 16MiB).
- First attempt sorted by JSON size descending; this front-loaded the largest reports and was terminated.
- Order-preserving size-aware run:
  - Corpus: 1,683,767 rows; max_row_id 8,062,484.
  - Metadata scan before scoring took about 43s because PostgreSQL had to compute JSON lengths.
  - Scoring complete: 350.6s, 4,802 rows/sec.
  - Stage totals summed across workers: fetch 2,304.8s, extraction 29,374.3s, matrix 72.9s, prediction 200.5s.
  - Slowest batch dropped to 26.6s.

Decision:

- Keep size-aware batching as opt-in, not default.
- It improves scoring and dramatically reduces the worst tail batch, but the live `LENGTH(cleave_result::text)` scan costs enough that wall-clock is worse than the simple 128-row default.
- To make size-aware batching a default win, add a stored/generated `cleave_result_bytes` column or another cheap size estimate in Hopper.

## 2026-04-30: EMBER2024-Inspired Accuracy Plan

Source read: `/tmp/1.pdf` (`EMBER2024 - A Benchmark Dataset for Holistic Evaluation of Malware Classifiers`).

Important translation note:

- EMBER vectors are raw-file/static-parser features: byte histogram, byte-entropy histogram, string statistics/patterns, PE headers, sections, imports/exports, data directories, rich header, Authenticode, and parse warnings.
- Our azoth-light model trains from cleave reports, not raw bytes. Good experiments should use signals cleave already emits in `fs`, `ms`, `is`, `ss`, and `ts`, or add scanner-side cleave features first. We should not blindly copy EMBER dimensions that litmus cannot reproduce at scan time.
- Our corpus spans roughly 50 file types, and the taxonomy is generally filetype-neutral. Avoid making the ML pipeline PE-centric. The directly portable idea is not "EMBER features exactly"; it is "stable, low-cardinality static summaries that work across file families, then measure global vs filetype-aware variants under our false-positive budgets."

Existing ablation status:

- Broad dead-weight ablation already ran for azoth-light.
- Normal-budget confirmation says keep `metrics`; candidate cuts were `trigram`, `crittri`, `atktri`, `critbi`, `skeleton`, and possibly `rare`.
- Do not re-run the same broad ablation first. Run additive experiments, then ablate any winning new family.

Ten accuracy experiments to run next:

| ID | Experiment | Why it maps to EMBER | Our implementation route | Compare by |
| --- | --- | --- | --- | --- |
| A1 | Portable static aggregate metrics | EMBER's general/string/import/structure summaries, extrapolated beyond PE | `EXP_EMBER_LITE_FEATURES=1`, but keep the bundle focused on generic cleave metrics; PE-only fields are at most optional follow-up checks | held-out F1, PR AUC, strict level recall |
| A2 | Cross-filetype metric expansion | EMBER v3 shows static summaries matter outside PE too | curated extra `metrics:binary_*`, `metrics:text_*`, `metrics:strings_*`, `metrics:imports_*`, `metrics:archive_*`, `metrics:elf_*`, `metrics:macho_*`, `metrics:image_*`; avoid PE-only defaults | strict FP levels across all filetype buckets |
| A3 | String pattern families | EMBER v3 expanded string indicators | derive counts from `ss` for URL/path/registry/MZ/script/crypto-ish tokens | false positives in benign source/archive files |
| A4 | Import family buckets | EMBER hashes imports; we already have `is` | hashed or curated import module/API categories beyond current suspicious APIs | recall at same FP budget |
| A5 | Generic structure/resource shape | EMBER section/data-shape ratios generalized | cleave metrics: executable/writable/code/data ratios when present, archive nesting, resource/image/text ratios, largest-member concentration | recall and FP stability across binary, archive, source, document, image |
| A6 | Provenance/timestamp consistency | EMBER Authenticode is one instance of provenance metadata | signer/certificate only when normalized, plus mtime/build-time spread, source archive provenance, package metadata consistency | FP reduction on legitimate software/packages |
| A7 | Parser/anomaly surrogate | EMBER parse warnings generalized | missing expected metrics, malformed-container indicators, analyzer warning counts when cleave emits them, checksum/alignment only as format-local signals | packed/evasive/corrupt-file recall |
| A8 | Filetype-conditioned thresholds | EMBER trains/evaluates per file type | one global model, but per-primary-filetype calibration/level thresholds | whole-corpus FP/1M and per-type recall |
| A9 | Per-filetype specialists | EMBER trained all-files and subset classifiers | train `azoth-light-pe`, `azoth-light-elf`, `azoth-light-pdf/archive/source` specialists with global fallback | full-corpus ensemble thresholds |
| A10 | Challenge-set proxy training | EMBER evaluates evasive/new-family challenge malware | hard-negative and low-score/late-arriving malware slices from Hopper | level recall on hard subsets |
| H1 | EMBER/SOREL detection hyperparams | Paper's malware-detection benchmark recipe | LightGBM 500 rounds, 64 leaves, 100 min samples/leaf | same pinned matrix as baseline |
| H2 | EMBER family/tag hyperparams | Paper's smaller OvR/family recipe | LightGBM 100 rounds, 64 leaves, 10 min samples/leaf, early stopping 10 | check if shallower/less regularized model helps our taxonomy-neutral features |

Initial code status:

- Added opt-in `COLLIMATOR_EMBER_LITE_FEATURES=1`.
- Make knobs:
  - `EXP_EMBER_LITE_FEATURES=1` for `make experiment`.
  - `TRAIN_EMBER_LITE_FEATURES=1` for `make train`.
- Added LightGBM hyperparameter knobs:
  - `EXP_NUM_LEAVES` / `TRAIN_NUM_LEAVES`.
  - `EXP_MIN_CHILD_SAMPLES` / `TRAIN_MIN_CHILD_SAMPLES`.
- Focused feature extraction tests pass.

Recommended run order:

1. Run A1 against the pinned current azoth-light baseline using the experiment matrix cache.
2. If A1 is positive, run full train + thresholds for an `azoth-light-ember-lite` candidate.
3. Implement A8 before A9; per-filetype thresholds are cheaper and tell us whether specialists are likely to pay off.
4. Add A2-A7 as separate opt-in feature bundles, one bundle per experiment, instead of one large feature dump.
5. Only after a bundle wins, run ablation inside that bundle.

## 2026-04-30: Full-Corpus Azoth-Light Hyperparameter Runs

Snapshot:

- `EXP_MAX_ID=8402261`
- Full experiment split: 441,068 train rows (276,177 malware, 164,891 benign), 61,449 held-out rows (37,613 malware, 23,836 benign).
- Baseline feature matrix: 28,960 features, 215,666,957 train nonzeros.
- LightGBM CUDA is invalid for this full sparse CSR matrix: it produced a one-leaf constant model and explicit diagnostics reported that sparse features are not supported by CUDA. Full runs below use CPU.
- Full matrix cache: `out/cache/matrix_4e7c1d0715140d1d_*`.

| Model | Protocol | Trees | Leaves | Min Child Samples | CV? | Wall Time | Held-out Precision | Held-out Recall | Held-out F1 | Held-out AUC | Read |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `azoth-light-full-baseline-cpu` | current defaults | 400 | auto | auto | 2-fold + final | ~41m | 0.9940 | 0.9955 | 0.9947 | 0.9997 | Valid full baseline. CV mean F1 0.9945. |
| `azoth-light-full-ember-family-cpu` | EMBER family/tag style | 100 | 64 | 10 | final-only | ~7.5m | 0.9915 | 0.9930 | 0.9923 | 0.9992 | Too small; underperforms baseline. |
| `azoth-light-full-ember-detect-cpu` | EMBER/SOREL detection style | 500 | 64 | 100 | final-only | ~23m | 0.9947 | 0.9964 | 0.9955 | 0.9998 | Best full held-out result so far; promote to threshold validation candidate. |
| `azoth-light-full-static-detect-cpu` | detection style + portable static summaries | 500 | 64 | 100 | final-only | ~28m (+~5m matrix build) | 0.9949 | 0.9963 | 0.9956 | 0.9998 | Slightly best held-out F1/precision so far; threshold-validate next. |

Notes:

- Final-only rows report train metrics using in-sample predictions for threshold selection, so held-out AUC/PR/Brier and held-out F1 are the meaningful comparison points.
- Full CPU experiments are feasible but not cheap. Use final-only for sweeps, then rerun 2-fold CV only for finalists.
- Portable static summaries are not a large sampled-test win, but they are directionally positive. The real decision should be based on strict FP-per-million threshold tables.

Threshold validation:

| Model | Corpus Rows | Malware | Benign | Hostile L5 Recall @ FP | Suspicious L5 Recall @ FP | Suspicious L9 Recall @ FP | Read |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `azoth-light-full-baseline-cpu` | 1,732,379 | 314,385 | 1,417,994 | 50.84% @ 1 FP | 73.57% @ 14 FP | 84.73% @ 70 FP | Current-default full model. |
| `azoth-light-full-static-detect-cpu` | 1,733,103 | 315,109 | 1,417,994 | 60.23% @ 1 FP | 75.54% @ 14 FP | 86.95% @ 70 FP | Static summaries slightly helped held-out F1 but hurt strict threshold recall. |
| `azoth-light-full-ember-detect-cpu` | 1,732,781 | 314,787 | 1,417,994 | 60.76% @ 1 FP | 77.13% @ 14 FP | 88.48% @ 70 FP | Current best strict-threshold candidate. |

Read:

- The LightGBM detection hyperparameters are the real win so far: `500 trees, 64 leaves, min_child_samples=100` improves hostile L5 recall by +9.92 points over the full baseline at the same 1-FP budget, and suspicious L5 by +3.56 points at the same 14-FP budget.
- Portable static summaries did not help strict thresholds when paired with the detection hyperparameters. Keep the feature bundle as an experiment, not a default.

## 2026-05-01: Full-Corpus Azoth-Light Accuracy Follow-Ups

Purpose: test the next batch of model-only experiments before inspecting the remaining false positives. All runs used the same pinned snapshot and cached baseline feature matrix unless noted.

Common command shape:

```sh
make experiment MODEL=<name> DEVICE=cpu WORKERS=128 \
  EXP_MAX_ID=8402261 EXP_TRAIN_SAMPLES=0 EXP_MAX_TEST_SAMPLES=0 EXP_FOLDS=0 \
  EXP_ESTIMATORS=500 EXP_MAX_DEPTH=14 EXP_LEARNING_RATE=0.05 \
  EXP_NUM_LEAVES=<leaves> EXP_MIN_CHILD_SAMPLES=<min_child_samples> \
  EXP_EARLY_STOPPING=50
```

Makefile update:

- Added pass-through knobs for `make experiment`: `EXP_COLSAMPLE_BYTREE`, `EXP_SUBSAMPLE`, `EXP_GAMMA`, `EXP_REG_ALPHA`, `EXP_REG_LAMBDA`, `EXP_THRESHOLD_MODE`, `EXP_THRESHOLD_FPR_TARGET`, `EXP_HARD_NEGATIVE_FRACTION`, `EXP_HARD_NEGATIVE_WEIGHT`, and `EXP_BENIGN_FILETYPE_WEIGHT`.

Held-out results:

| Model | Change vs `azoth-light-full-ember-detect-cpu` | Features | Held-out Precision | Held-out Recall | Held-out F1 | Held-out AUC | Brier | Read |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `azoth-light-full-hn005w2-cpu` | hard-negative top 0.5% benign at 2x weight | 28,960 | 0.9947 | 0.9964 | 0.9955 | 0.9998 | 0.0043 | Held-out tie, but threshold validation is slightly worse. |
| `azoth-light-full-reg-cpu` | `colsample=0.65`, `subsample=0.9`, `reg_alpha=0.1`, `reg_lambda=5` | 28,960 | 0.9943 | 0.9966 | 0.9954 | 0.9997 | 0.0043 | More recall but lower precision; not a finalist. |
| `azoth-light-full-droprare-cpu` | drop `rare:` features | 23,676 | 0.9946 | 0.9963 | 0.9954 | 0.9998 | 0.0042 | Smaller feature space, but not better enough to promote. |
| `azoth-light-full-mcs200-cpu` | `min_child_samples=200` | 28,960 | 0.9948 | 0.9962 | 0.9955 | 0.9998 | 0.0042 | Best hostile L5 threshold result so far; suspicious L5 worse. |
| `azoth-light-full-leaves96-cpu` | `num_leaves=96`, `min_child_samples=100` | 28,960 | 0.9945 | 0.9965 | 0.9955 | 0.9998 | 0.0042 | Best all-around strict-threshold result so far. |

Threshold validation on pinned corpus:

- `THRESHOLD_MAX_ID=8402261`
- Corpus: 1,729,088 labeled rows (311,093 malware, 1,417,995 benign).

| Model | Hostile L5 Recall @ FP | Suspicious L5 Recall @ FP | Suspicious L9 Recall @ FP | Read |
| --- | ---: | ---: | ---: | --- |
| `azoth-light-full-ember-detect-cpu` | 60.76% @ 1 FP | 77.13% @ 14 FP | 88.48% @ 70 FP | Previous best reference. |
| `azoth-light-full-hn005w2-cpu` | 60.57% @ 1 FP | 76.91% @ 14 FP | 88.29% @ 70 FP | Hard-negative weighting did not help at strict budgets. |
| `azoth-light-full-mcs200-cpu` | 65.20% @ 1 FP | 76.11% @ 14 FP | 87.99% @ 70 FP | Best hostile-only point; sacrifices suspicious coverage. |
| `azoth-light-full-leaves96-cpu` | 63.42% @ 1 FP | 79.14% @ 14 FP | 88.91% @ 70 FP | New best all-around candidate. |

Read:

- Increasing leaf capacity from 64 to 96 helped the strict suspicious operating points and still improved hostile L5 over the 64-leaf reference. This is the current candidate to beat.
- Raising `min_child_samples` to 200 is a real hostile-policy tradeoff: better at 1 FP, worse at 14/70 FP. Keep it around if hostile detections are more important than suspicious breadth.
- Hard-negative weighting using the existing in-fold mining path was not useful at this setting. If we revisit hard negatives, use threshold-cache-derived false positives rather than the training-set top benign tail.
- Dropping `rare:` reduced columns by 5,284 but barely changed sparse nonzeros and did not improve metrics. Do not prune it yet solely from this run.
- The threshold builder is still extraction-bound: recent runs scored ~1.73M rows in 407-415s, with accumulated worker extraction time around 32k-33k seconds and prediction around 204-222 seconds.

Default update:

- `make train MODEL=azoth-light` and `make experiment MODEL=azoth-light...` now default to `num_leaves=96` and `min_child_samples=100`.
- Keep `min_child_samples=200` as the hostile-skewed variant: it is slightly better than leaves96 at hostile L5/L6, but worse at suspicious L5/L6/L9.

Comparison against the trained `litmus-xg` threshold report:

Corpus note: the saved `litmus-xg` threshold report was generated on an older corpus snapshot (1,650,556 rows: 326,229 malware, 1,324,327 benign). The azoth-light rows here are from the pinned `THRESHOLD_MAX_ID=8402261` snapshot (1,729,088 rows: 311,093 malware, 1,417,995 benign). The budgets/FP-per-million semantics match, but an exact release comparison should refresh `litmus-xg` on the same pinned snapshot.

| Level | Severity | `litmus-xg` Recall @ FP | `azoth-light-full-leaves96-cpu` Recall @ FP | Delta |
| ---: | --- | ---: | ---: | ---: |
| 5 | hostile | 37.63% @ 1 FP | 63.42% @ 1 FP | +25.79 pts |
| 5 | suspicious | 62.60% @ 13 FP | 79.14% @ 14 FP | +16.54 pts |
| 6 | hostile | 40.17% @ 2 FP | 65.36% @ 2 FP | +25.19 pts |
| 6 | suspicious | 66.17% @ 26 FP | 84.50% @ 28 FP | +18.33 pts |
| 9 | hostile | 51.74% @ 6 FP | 71.60% @ 7 FP | +19.86 pts |
| 9 | suspicious | 74.94% @ 66 FP | 88.91% @ 70 FP | +13.97 pts |

## 2026-05-01: Severity Calibration Policy Update

New training and threshold reports use levels 0-9 with hostile as the primary
deployment signal:

- Hostile: `L` false positives per million good files.
- Suspicious: `(L + 1) * 8` false positives per million good files.
- Default level remains L5, now meaning 5 hostile FP/1M and 48 suspicious FP/1M.

Historical tables above were produced with the older level schedule, so their
`@ FP` counts should be read literally rather than mapped to the new level names.

Fresh `azoth-light-full-leaves96-cpu` threshold refresh on the pinned
`THRESHOLD_MAX_ID=8402261` corpus:

- Corpus: 1,709,725 rows; 291,730 malware; 1,417,995 benign.
- Threshold cache rebuild: 377.5s wall-clock, 4,529 rows/sec.
- Worker-stage totals: fetch 1,856s, extract 25,121s, matrix 55s, predict 186s.
- L5 hostile: threshold 0.997465, 69.76% recall, 7 FP.
- L5 suspicious: threshold 0.979672, 87.58% recall, 68 FP.
- L9 hostile: threshold 0.994960, 77.18% recall, 12 FP.
- L9 suspicious: threshold 0.972893, 89.11% recall, 113 FP.

Accuracy-development read:

- Hostile-L5 FP pressure is concentrated in PowerShell, zip/archive-like files,
  PE, and a small Python tail.
- Many high-volume source filetypes have zero hostile-L5 FPs but poor recall,
  so the next experiment batch should split into FP reduction and missed-malware
  recovery rather than only global LightGBM tuning.
- The threshold cache builder remains extraction-bound, not inference-bound.
  Prediction was only 186s of accumulated stage time versus 25,121s extraction.

Next portable feature experiment:

- Add coarse format hints derived only from cleave-reported file types, not from
  private corpus source paths and not from filename extensions.
- First candidate should enable `EXP_FORMAT_HINTS=1` and evaluate whether
  script/native-binary/archive mixtures improve hostile L5/L9 without increasing
  the PowerShell/zip/PE false-positive tail.
- Per-format models remain a follow-up branch: try hints first, then split
  models only if the filetype matrix shows persistently different optimal
  thresholds or feature families by group.

Result: `azoth-light-full-format-hints-cpu`

Command:

```sh
make experiment MODEL=azoth-light-full-format-hints-cpu DEVICE=cpu WORKERS=96 \
  EXP_FORMAT_HINTS=1 \
  EXP_MAX_ID=8402261 EXP_TRAIN_SAMPLES=0 EXP_MAX_TEST_SAMPLES=0 EXP_FOLDS=0 \
  EXP_ESTIMATORS=500 EXP_MAX_DEPTH=14 EXP_LEARNING_RATE=0.05 \
  EXP_NUM_LEAVES=96 EXP_MIN_CHILD_SAMPLES=100 EXP_EARLY_STOPPING=50
make thresholds MODEL=azoth-light-full-format-hints-cpu WORKERS=96 THRESHOLD_MAX_ID=8402261
```

Held-out metrics looked good but did not translate to strict FP budgets:

- Held-out F1: 0.9961, precision 0.9955, recall 0.9967, AUC 0.9998.
- Threshold cache rebuild: 376.0s wall-clock, 4,547 rows/sec.
- Stage totals: fetch 1,704s, extract 24,782s, matrix 55s, predict 181s.

Strict-threshold comparison against `azoth-light-full-leaves96-cpu`:

| Model | L5 Hostile Recall @ FP | L5 Suspicious Recall @ FP | L9 Hostile Recall @ FP | L9 Suspicious Recall @ FP | Read |
| --- | ---: | ---: | ---: | ---: | --- |
| `azoth-light-full-leaves96-cpu` | 69.76% @ 7 FP | 87.58% @ 68 FP | 77.18% @ 12 FP | 89.11% @ 113 FP | Current baseline. |
| `azoth-light-full-format-hints-cpu` | 64.50% @ 7 FP | 66.24% @ 68 FP | 64.97% @ 12 FP | 66.75% @ 113 FP | Reject. Format hints hurt strict-FP recall badly. |

Read:

- Coarse format hints are not useful as a single global feature layer in this
  form. They likely gave the model an easy global partition that improved broad
  held-out classification while damaging score ordering in the extreme
  low-FP tail.
- Do not promote `EXP_FORMAT_HINTS=1`.
- If we revisit file-format specialization, do it as per-group calibration or
  separate candidate models evaluated by strict hostile FP budgets, not as these
  broad hint features.

## 2026-05-01: Benign Tail Weighting

Purpose: reduce strict-FP pressure from the main hostile-L5 false-positive
filetypes without using private source/provenance fields.

Result: `azoth-light-full-bftail-cpu`

Command:

```sh
make experiment MODEL=azoth-light-full-bftail-cpu DEVICE=cpu WORKERS=96 \
  EXP_MAX_ID=8402261 EXP_TRAIN_SAMPLES=0 EXP_MAX_TEST_SAMPLES=0 EXP_FOLDS=0 \
  EXP_ESTIMATORS=500 EXP_MAX_DEPTH=14 EXP_LEARNING_RATE=0.05 \
  EXP_NUM_LEAVES=96 EXP_MIN_CHILD_SAMPLES=100 EXP_EARLY_STOPPING=50 \
  EXP_BENIGN_FILETYPE_WEIGHT='pe=2 zip=3 powershell=5'
make thresholds MODEL=azoth-light-full-bftail-cpu WORKERS=96 THRESHOLD_MAX_ID=8402261
```

| Model | L5 Hostile Recall @ FP | L5 Suspicious Recall @ FP | L9 Hostile Recall @ FP | L9 Suspicious Recall @ FP | Read |
| --- | ---: | ---: | ---: | ---: | --- |
| `azoth-light-full-leaves96-cpu` | 69.76% @ 7 FP | 87.58% @ 68 FP | 77.18% @ 12 FP | 89.11% @ 113 FP | Current baseline. |
| `azoth-light-full-bftail-cpu` | 50.20% @ 3 FP | 53.16% @ 67 FP | 50.34% @ 12 FP | 53.57% @ 113 FP | Reject. Too blunt. |

Read:

- Upweighting all benign rows for FP-heavy filetypes made the model much more
  conservative, but badly damaged low-FP malware ranking.
- Do not promote broad benign filetype weights.
- A narrower hard-negative experiment is still worth trying because it targets
  the scored benign tail rather than whole filetype populations.

Result: `azoth-light-full-hn0025w2-cpu`

Command:

```sh
make experiment MODEL=azoth-light-full-hn0025w2-cpu DEVICE=cpu WORKERS=96 \
  EXP_MAX_ID=8402261 EXP_TRAIN_SAMPLES=0 EXP_MAX_TEST_SAMPLES=0 EXP_FOLDS=0 \
  EXP_ESTIMATORS=500 EXP_MAX_DEPTH=14 EXP_LEARNING_RATE=0.05 \
  EXP_NUM_LEAVES=96 EXP_MIN_CHILD_SAMPLES=100 EXP_EARLY_STOPPING=50 \
  EXP_HARD_NEGATIVE_FRACTION=0.0025 EXP_HARD_NEGATIVE_WEIGHT=2.0
make thresholds MODEL=azoth-light-full-hn0025w2-cpu WORKERS=96 THRESHOLD_MAX_ID=8402261
```

Notes:

- Cached-matrix train still took roughly 21 minutes because the hard-negative
  path does a two-pass fit/score/refit cycle.
- Threshold cache rebuild took 377.3s; extraction again dominated.

| Model | L5 Hostile Recall @ FP | L5 Suspicious Recall @ FP | L9 Hostile Recall @ FP | L9 Suspicious Recall @ FP | Read |
| --- | ---: | ---: | ---: | ---: | --- |
| `azoth-light-full-leaves96-cpu` | 69.76% @ 7 FP | 87.58% @ 68 FP | 77.18% @ 12 FP | 89.11% @ 113 FP | Current baseline. |
| `azoth-light-full-hn0025w2-cpu` | 53.17% @ 7 FP | 54.06% @ 68 FP | 53.17% @ 7 FP | 54.38% @ 111 FP | Reject. |

Read:

- Even a narrow 0.25% benign-tail hard-negative pass made the model too
  conservative in the strict-FP tail.
- Do not keep using the current hard-negative weighting implementation for full
  azoth experiments unless the weighting strategy changes materially.
- Next work should move toward per-format calibration/routing or feature
  additions that recover true positives, not global benign-pressure weighting.

## 2026-05-01: ELF Specialist Routing Benchmark

Purpose: compare the current general model against separately trained
specialists for ELF malware detection:

- `general`: existing `azoth-light-full-leaves96-cpu`.
- `binary-filegroup`: trained on native binary filetypes (`elf`, `macho`, `pe`).
- `elf-specific`: trained only on `file_type=elf`.

Command:

```sh
make elf-model-benchmark EXP_WORKERS=96 THRESHOLD_MAX_ID=8402261
```

Artifacts:

- Summary: `out/models/elf_model_benchmark.json`
- Binary specialist: `out/models/azoth-light-binary-cpu/`
- ELF specialist: `out/models/azoth-light-elf-cpu/`

Benchmark set: full labeled ELF test partition at `max_id=8402261`, including
low-score rows: 8,532 rows (337 malware, 8,195 benign). Training still used the
normal score-filtered trainable rows.

Important measurement caveat: on 8,195 benign ELF test rows, one false positive
is 122.0 FP/M. That means nonzero hostile/suspicious budgets such as 5, 48, or
80 FP/M all collapse to the same additive budget of one FP on this slice.

| Model | Train Rows | Features | AUC | Avg Precision | Max F1 | L0 Hostile Recall @ FP | L5 Hostile Recall @ FP | L5 Suspicious Recall @ FP | Read |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `general` | existing | 28,960 | 0.999835 | 0.996799 | 0.9835 | 85.46% @ 0 FP | 97.03% @ 1 FP | 97.03% @ 1 FP | Strong baseline. |
| `binary-filegroup` | 232,697 | 23,176 | 0.999802 | 0.997019 | 0.9837 | 89.91% @ 0 FP | 96.74% @ 1 FP | 96.74% @ 1 FP | Better zero-FP hostile recall, slightly worse at one FP. |
| `elf-specific` | 52,765 | 4,276 | 0.999900 | 0.997842 | 0.9881 | 85.16% @ 0 FP | 97.92% @ 1 FP | 97.92% @ 1 FP | Best one-FP recall and best broad metrics. |

Read:

- ELF specialization is promising. The ELF-only model wins AUC, average
  precision, max F1, and the one-FP hostile/suspicious operating point.
- The binary-filegroup model is the best zero-FP hostile model on this slice,
  improving L0 recall from 85.46% to 89.91%.
- Because hostile policy is the priority, the routing choice may not be a
  single answer: strict L0 routing favors the binary model; L5/default routing
  favors the ELF-specific model.
- Next step: repeat this benchmark at larger denominators by using all ELF rows
  or CV/out-of-fold predictions, so FP/M targets below 122 can be measured
  without additive-budget quantization.

## 2026-05-01: Deployable Shared-Spec ELF Mask

Purpose: test whether we can recover the smaller ELF-specialist behavior while
keeping litmus deployability. The model is trained with the full general
`feature_spec.json` shape, but all columns outside the older custom ELF
specialist spec are zeroed before fitting. At runtime this remains one-vector
deployable because the specialist uses the exact general feature spec.

Command:

```sh
make azoth-specialists EXP_WORKERS=96 THRESHOLD_MAX_ID=8402261 \
  AZOTH_SPECIALIST_ONLY=elf AZOTH_SPECIALIST_SKIP_EXISTING=0 \
  AZOTH_SPECIALIST_MASK_SPEC='elf=out/models/azoth-light-elf-cpu/feature_spec.json'
make azoth-calibrate EXP_WORKERS=96 AZOTH_REFRESH_SCORES=1
```

Feature overlap:

- old custom ELF spec: 4,276 features
- current general spec: 28,960 features
- overlap used by mask: 1,756 features
- custom ELF features absent from general spec: 2,520

Result, routed `general + filetypes/elf` against the full score-cache corpus:

| Model Set | L5 Hostile Recall @ FP | L5 Suspicious Recall @ FP | L9 Hostile Recall @ FP | L9 Suspicious Recall @ FP | Read |
| --- | ---: | ---: | ---: | ---: | --- |
| General baseline | 69.76% @ 7 FP | 87.58% @ 68 FP | 77.18% @ 12 FP | 89.11% @ 113 FP | Current deploy baseline. |
| Shared-spec unmasked `general+native+elf` | 69.13% @ 8 FP | 82.86% @ 77 FP | 74.55% @ 14 FP | 84.94% @ 129 FP | Budget-safe, but weaker. |
| Shared-spec masked `general+elf` | 67.05% @ 8 FP | 82.68% @ 77 FP | 73.56% @ 14 FP | 84.89% @ 129 FP | Reject. |

Read:

- The "train full-width but mask to a specialist vocabulary" idea is deployable,
  but using the old custom ELF spec as the mask is too lossy because most custom
  ELF features are not in the current general spec.
- The right deployable version is probably not "general spec as it exists
  today"; it is a stable Azoth ABI spec that is the union of general and approved
  specialist vocabularies. Then litmus still extracts once, but specialists keep
  the columns that made their custom vocabularies useful.
- Do not promote the masked ELF model.

## 2026-05-01: Refreshed ELF Pool Retest

Purpose: retest the focused ELF ensemble experiments after new labeled ELF
samples arrived. The prior focused run was tied to the general score cache
snapshot. Retesting required rebuilding that cache first; otherwise the new ELF
rows were invisible to calibration and threshold search.

Before refresh:

- Current script-visible corpus: 2,143,056 labeled rows.
- Current ELF rows: 79,811.
- Existing score-cache snapshot: `max_id=10318057`.
- ELF rows beyond that snapshot: 9,505 (2,456 malware, 7,049 benign).

Commands:

```sh
cp -n out/models/azoth-light-full-leaves96-cpu/threshold_scores.npz \
  out/models/azoth-light-full-leaves96-cpu/threshold_scores.max10318057.npz
make thresholds-refresh MODEL=azoth-light-full-leaves96-cpu \
  WORKERS=64 THRESHOLD_TOP_ERRORS=0
.venv/bin/python scripts/elf_ensemble_experiments.py \
  --db postgres://hopper@localhost:5432/hopper \
  --general-scores out/models/azoth-light-full-leaves96-cpu/threshold_scores.npz \
  --general-spec out/models/azoth/general/feature_spec.json \
  --teacher-model out/models/azoth-light-elf-cpu/model.txt \
  --teacher-spec out/models/azoth-light-elf-cpu/feature_spec.json \
  --workers 64 \
  --output-dir out/models/azoth/elf_experiments_w64_live \
  --output out/models/azoth/elf_experiments_w64_live.json
```

Artifacts:

- Preserved old cache:
  `out/models/azoth-light-full-leaves96-cpu/threshold_scores.max10318057.npz`
- Refreshed cache:
  `out/models/azoth-light-full-leaves96-cpu/threshold_scores.npz`
- Experiment output:
  `out/models/azoth/elf_experiments_w64_live.json`

Refreshed snapshot:

- `max_id=34757117`
- 2,143,738 rows: 373,591 malware, 1,770,147 benign.
- 79,910 ELF calibration rows.
- 64,923 trainable ELF rows.
- Cache build time: 471.5s at 4,547 rows/sec with 64 workers.

Full-corpus policy results:

| Experiment | Rule | Deployable | L5 Hostile Recall @ FP | L9 Hostile Recall @ FP | L5 Suspicious Recall @ FP | L9 Suspicious Recall @ FP |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `general_baseline` | `general` | yes | 48.57% @ 8 | 54.15% @ 15 | 70.36% @ 64 | 72.62% @ 134 |
| `custom_teacher_upper_bound` | `or` | no | 48.92% @ 8 | 54.45% @ 15 | 70.71% @ 84 | 72.92% @ 141 |
| `tail_contrast` | `or` | yes | 49.34% @ 8 | 54.86% @ 15 | 70.94% @ 84 | 73.17% @ 141 |
| `teacher_distill` | `or` | yes | 49.15% @ 8 | 54.67% @ 15 | 70.88% @ 82 | 73.07% @ 141 |
| `ranker` | `or` | yes | 48.70% @ 8 | 54.26% @ 15 | 70.59% @ 84 | 72.81% @ 141 |

Read:

- Yes, retesting required a score-cache refresh. The new ELF rows were not in
  the old calibration universe.
- The refreshed corpus is harder for the current general model than the older
  reports: default full-corpus hostile recall is now 48.57% at L5.
- `tail_contrast` is the best deployable focused experiment in this run:
  +0.77 percentage points at L5 hostile and +0.71 points at L9 hostile with the
  same hostile false-positive counts.
- The old custom ELF teacher remains non-deployable and is not a large upper
  bound on this refreshed corpus, so simply recovering that old feature set is
  unlikely to be enough.
- Promote `tail_contrast` only as the current ELF-specialist candidate; it is a
  real but small win. The larger accuracy work should move toward richer,
  deployable ELF-agnostic features and a stable Azoth ABI feature union.
