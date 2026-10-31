# Python keyword selection and regularization

## Results

Completed 2026-10-31: 19 configurations, two seeds each (38 fits), on the saved
natural 10% Python cohort. These are averaged-probability ensemble results.
No model was promoted and no production configuration changed.

| Features added to baseline | Selection | Words | Recall at 0 FP | Recall at 1 FP |
|---|---|---:|---:|---:|
| None | — | 0 | 64.84% | 72.16% |
| Full ID + description, pooled | Frequency | 1,000 | 69.96% | 73.99% |
| Full ID + description, pooled | Balanced MI | 1,000 | 70.33% | 72.53% |
| Full ID + description, pooled | Balanced MI | 5,000 | 67.77% | **75.82%** |
| Context, separate | Balanced MI | 5,000 | 70.70% | 74.36% |
| Context, separate | Balanced MI | 10,000 | **72.89%** | 72.89% |

The most promising pooled candidate is 5k class-aware words: +2.93 percentage
points at zero FP and +3.66 at one FP versus the fresh baseline. At one FP,
it also beats frequency selection at the same 5k budget (73.99%). Both individual
seeds improve their one-FP recall over their respective baselines: 72.89→75.09%
and 71.79→76.19%.

For a smaller vocabulary, 1k frequency-selected pooled words remain competitive:
they gain 5.13 points at zero FP and 1.83 at one FP. Class-aware selection is not
uniformly better, and the preferred setting depends on the false-positive budget.

Increasing the cap is not automatically useful. Under the selector's stricter
training-only boundary there are 9,074 eligible pooled words and 28,727 eligible
context words. Pooled frequency 5k and all 9,074 words give identical dev scores;
context frequency 5k and 10k also give identical dev scores. The pooled frequency
and balanced-MI 10k arms use the same complete vocabulary.

The regularization follow-up independently changes minimum leaf support from
100 to 300, or L2 regularization from 1 to 5. Each has a baseline control and the
1k-frequency/5k-balanced-MI pooled candidates. Neither change improves the 5k
class-aware candidate: recall at one FP falls to 70.33% and 71.79%, respectively.
Stronger L2 helps the baseline itself (68.50% / 73.26%), so regularization gains
must not be attributed to keyword features.

All 19 rows, individual seeds, paired recovered/lost detections, matrices,
selected vocabularies, native models, and saved predictions are retained under:

`out/experiments/keyword-python-selection-10pct-v3/`

See its `RESULTS.md`, `verified_summary.json`, and `context_coverage.json`.

## Protocol and limits

- Same saved cohort membership and labels as the earlier hierarchy/context
  screen: 53,206 training rows (1,702 malware), 8,833 dev rows (273 malware).
  Train/dev canonical groups are disjoint. No locked test rows were read.
- One fresh read-only PostgreSQL snapshot supplies all reports and metadata.
  The original base feature vocabulary and feature settings remain fixed;
  all arms share identical extracted base matrices. Report inputs have changed
  since the earlier screen, so use this screen's baseline for comparisons.
- Rows follow normal `experiment.py` extraction order: ascending row ID within
  each partition. The first local ordering probe is superseded by `v3`, which
  reorders its complete cached extraction without another database read.
- Seeds 43/44, 180-tree budget, internal holdout fraction 0.12, early stopping
  patience 25, full column sampling, four CPU threads. Existing `train.train`
  performs each fit; external dev is not used for early stopping.
- Both vocabulary selectors use only the **intersection of both seeds' fitting
  rows**: 41,218 reports, comprising 39,897 goodware and 1,321 malware. Neither
  internal holdout nor external dev labels enter keyword selection. The
  historical base vocabulary is unchanged from the earlier training cohort.
- Keywords are binary per-report presence. Tokenization and minimum document
  support of five are unchanged. Compare frequency versus balanced mutual
  information at 1k/5k/10k, separately for pooled full-ID/description and context.
- Balanced MI computes smoothed class-conditional probabilities
  `p = (class_word_count + 0.5) / (class_total + 1)` and the mutual information
  of presence/absence and class under equal class priors. Equivalently, this
  is the Jensen–Shannon divergence of the two Bernoulli distributions. It can
  retain either malware-associated or goodware-associated words. Lexical ties
  and lexical feature-column ordering make selection deterministic.
- Context remains a separate source. Usable context appears in 86.76% of dev
  goodware but only 41.39% of malware. Its apparent gain needs confirmation with
  comparable capture coverage and package/family or temporal separation.
- These are exploratory comparisons on repeatedly examined dev data. Two seeds
  and 273 dev malware samples do not establish a production improvement. Confirm
  shortlisted settings on independent data before promotion.

The screen above used an experiment helper. Autocollie now also exposes
`keyword_selection=balanced_mi`, a bounded `keyword_candidate_max`, and independent
`*_keyword_vocab_max`, `*_keyword_min_freq`, and `*_keyword_selection` overrides
for all five sources. Zero/zero/`inherit` use the shared defaults. Frequency
selection remains the default and sources remain opt-in.

The integrated selector fits separately inside each training split, including
CV folds and hard-negative refits. It does not use calibration or validation
labels. This differs from this research screen's shared intersection of seed
fitting rows, so it need not choose exactly the same words. Frequency-ranked
candidate discovery remains unsupervised and bounded; the candidate matrix
and feature indices are shared across seeds. Rejected columns are zero during
fitting, so trees cannot use them, and inference needs no extra masking. Saved
run metadata distinguishes candidate, eligible, and selected counts per seed.

These settings are available for general, filegroup, and filetype models, and
survive replay into accepted model configurations. See the
[autocollie keyword controls](../../autocollie/README.md#per-model-keyword-tuning).
They use the existing Scan keyword feature contract and require no new Azoth
format. The earlier screen's artifacts remain native research models/specs;
the integration smoke run additionally exercised ONNX export.

Integration verification: 91 focused Python tests, autocollie's specs/runner/CLI
tests, all 24 keyword knob bindings, and a synthetic two-seed, two-fold
`make experiment` run with pooled cap 5, context cap 2, and frequency-ranked
full-ID cap 3. Both members exported to ONNX. Its artifacts are in
`out/experiments/autocollie-keyword-controls-smoke-v3/`; synthetic accuracy is
not evidence of a real-world improvement.

## Reproduction and verification

Use a new output directory for a fresh snapshot:

```bash
.venv/bin/python scripts/keyword_python_selection.py \
  --output out/experiments/keyword-python-selection-repeat
.venv/bin/python scripts/keyword_python_regularization.py \
  out/experiments/keyword-python-selection-repeat
.venv/bin/python scripts/summarize_python_keyword_selection.py \
  out/experiments/keyword-python-selection-repeat
```

`--reuse-inputs PATH` reuses a complete frozen extraction, verifies row membership
and labels, and restores standard row ordering. `--resume` reuses completed
fits after checking cohort, configuration, extractor/training revisions, and
matrix hashes. The database is not needed for a fully cached resume.

The verifier recomputes both-class keyword counts from only the selector rows,
checks selected vocabularies and matrix fingerprints, reloads every native
model, and requires exact equality with saved float32 dev predictions. All
38 models passed. Ten focused tests cover selector symmetry/support, holdout
exclusion, serializable revision hashes, cached row ordering, exclusion of
dev-only tokens, and existing experiment controls.
