# AZOTH ELF Research Log

This log is for the unconstrained ELF specialist track. In this track the ELF
model is allowed to use a different feature vocabulary, a different model type,
and a different extraction path from the general Azoth model. Deployment can be
handled later by routing ELF files to `azoth/filetypes/elf/` and running the
ELF extractor only for that route.

The goal is not a tidy incremental model. The goal is to find what wins.

## Metric Clarification

The primary metric for this log is ELF-only recall at fixed ELF false-positive
budgets. Full-corpus routed hostile recall is still useful deployment context,
but it is not the right measure of whether the ELF specialist detects malicious
ELF files well.

This matters because ELF malware is a small slice of total malware in the full
corpus. A near-perfect ELF specialist can only move total full-corpus malware
recall by a small amount. The ELF-only numbers are much stronger than the
full-corpus routed L5 hostile column suggests.

Current ELF-only leaders:

| Model | ELF Recall @ 0 FP | ELF Recall @ 1 FP | ELF Recall @ 3 FP | ELF AUC | ELF AP | ELF Max F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| combo traits + metrics + symbols + formula, GOSS | 97.76% | 98.81% | 99.16% | 0.999970 | 0.999789 | 0.9968 |
| combo traits, GOSS | 97.53% | 97.98% | 98.86% | 0.999963 | 0.999754 | 0.9960 |
| combo traits + metrics, GOSS | 97.38% | 97.40% | 98.71% | 0.999934 | 0.999519 | 0.9954 |
| suspicious+ combo traits, GOSS | 96.90% | 97.25% | 98.61% | 0.999961 | 0.999681 | 0.9953 |
| combo traits TF-IDF, GOSS | 96.71% | 97.46% | 98.84% | 0.999951 | 0.999680 | 0.9956 |

Read:

- The ELF specialist already exceeds 90% recall by a wide margin under ELF-only
  scoring.
- The best current ELF-only model is the combined feature model, despite its
  tiny full-corpus routed lift.
- Future experiment sections should sort by ELF recall at 0 FP first, then 1 FP,
  then 3 FP, with full-corpus routed L5 hostile treated as deployment context.

## 2026-05-01: Snapshot Refresh

Before proposing the next ELF experiments, the general score cache was refreshed
so the latest labeled samples are visible to calibration and routed threshold
tests.

Commands:

```sh
cp -n out/models/azoth-light-full-leaves96-cpu/threshold_scores.npz \
  out/models/azoth-light-full-leaves96-cpu/threshold_scores.max34757117.npz
make thresholds-refresh MODEL=azoth-light-full-leaves96-cpu \
  WORKERS=64 THRESHOLD_TOP_ERRORS=0
```

Refreshed cache:

- Path: `out/models/azoth-light-full-leaves96-cpu/threshold_scores.npz`
- Preserved prior cache:
  `out/models/azoth-light-full-leaves96-cpu/threshold_scores.max34757117.npz`
- Snapshot max row id: `51198735`
- Full scored corpus: 2,173,639 rows
- Malware: 393,489
- Benign: 1,780,150
- Cache build time: 484.1s
- Throughput: 4,490 rows/sec with 64 workers

ELF rows at this snapshot:

- Total labeled ELF rows: 87,040
- Malware ELF rows: 8,072
- Benign ELF rows: 78,968
- Trainable ELF rows at `score >= 3`: 80,674
- Trainable malware ELF rows: 8,042
- Trainable benign ELF rows: 72,632

Current general-model full-corpus baseline from the refreshed cache:

| Policy | Recall | FP | Threshold |
| --- | ---: | ---: | ---: |
| L5 hostile | 46.75% | 8 | 0.999131 |
| L9 hostile | 53.17% | 16 | 0.998641 |
| L5 suspicious | 68.39% | 65 | 0.995318 |
| L9 suspicious | 70.66% | 136 | 0.994028 |

Primary promotion metric for ELF specialists:

- Routed full-corpus L5 hostile recall at the allowed full-corpus FP budget.
- L9 hostile is the secondary hostile metric.
- Suspicious is tracked, but hostile wins ties.
- ELF-slice recall at fixed ELF false-positive budgets is diagnostic, not the
  final deployment gate.

Every experiment should report:

- Full-corpus routed L0-L9 hostile and suspicious tables.
- ELF-only recall at 0, 1, 5, 9, 40, 50 FP/M good ELF.
- ELF AUC, average precision, max F1.
- Feature count, training rows, wall time, peak RAM, model size, score latency.
- Whether the experiment is deployable as an ELF route.

## 12 Experiments To Run

### E01: Deep Trait Path N-Grams

Build arbitrary trait path n-grams for ELF, not just the current bigram/trigram
families. Test orders 2 through 8 and path depths 3 through full leaf depth.
Use benign-frequency caps so rare benign coincidences do not explode the FP
rate.

Hypothesis: Linux malware behavior is often a conjunction of ordinary findings.
Deep conjunctions should help the hostile threshold more than broad aggregates.

Suggested grid:

- `order_max`: 4, 6, 8
- `path_depth`: 3, 5, full
- `min_malware_freq`: 3, 5, 10
- `max_benign_frac`: 0, 0.001, 0.01

### E02: Full Trait Hierarchy Counts

Use every trait prefix and every leaf trait as a feature, with boolean, count,
log-count, max severity, sum severity, max confidence, and confidence-weighted
count variants.

Hypothesis: the current general feature space may flatten useful ELF-specific
hierarchy. The specialist can afford a much larger sparse trait vocabulary.

### E03: Exact Finding ID Model

Train on exact finding IDs rather than curated families. Keep the top K exact
IDs by malware support and low benign prevalence, then compare boolean,
count-based, and TF-IDF-style weighting.

Hypothesis: exact IDs that are too narrow for the general model may be strong
inside ELF.

Suggested grid:

- `top_k`: 10k, 25k, 50k, all above support floor
- feature value: boolean, log-count, TF-IDF
- learner: LightGBM, XGBoost

### E04: ELF Metadata Surface

Add ELF-native static metadata:

- architecture, bitness, endian, OS ABI, ABI version
- ELF type, machine, flags
- interpreter path
- dynamic tags and needed libraries
- section and segment names, counts, sizes, permissions
- symbol table counts, stripped status, imported/exported symbol families
- RELRO/NX/PIE/static-linking indicators when available

Hypothesis: malware and benign Linux binaries differ in build, linkage, packing,
and loader behavior. These are not PE features; they are ELF route features.

### E05: Symbol And String Token N-Grams

Tokenize symbol names, dynamic symbol names, section names, interpreter paths,
library names, embedded paths, command strings, URLs, and shell fragments.
Generate hashed word n-grams and character n-grams.

Hypothesis: Linux malware leaks intent through symbols, paths, shell commands,
crypto/API names, and C2 strings even when trait extraction is incomplete.

Suggested features:

- word n-grams: 1 through 4
- char n-grams: 3 through 8
- signed hashing into 2^18, 2^20, 2^22 buckets

### E06: Byte Shape And Entropy Model

Adapt the file-neutral parts of EMBER to ELF:

- byte histogram
- byte entropy histogram
- file-size buckets
- section/segment entropy statistics
- rolling entropy percentiles
- zero-byte, printable-byte, and high-byte ratios
- simple compressibility estimate

Hypothesis: packed, encrypted, stripped, or generated ELF malware differs from
normal distro binaries in byte distribution and entropy shape.

### E07: LightGBM Aggressive ELF Sweep

Use the richest ELF feature set available and sweep LightGBM more aggressively
than the general model.

Suggested grid:

- boosting: `gbdt`, `dart`, `goss`
- `num_leaves`: 64, 96, 160, 255, 511
- `min_child_samples`: 10, 25, 50, 100, 200
- `learning_rate`: 0.015, 0.03, 0.05
- `feature_fraction`: 0.6, 0.8, 1.0
- `bagging_fraction`: 0.6, 0.8, 1.0
- `lambda_l1/lambda_l2`: 0, 0.1, 1, 5

Hypothesis: the best low-FP ELF model is likely not using the same regularizing
knobs as the general model.

### E08: XGBoost ELF Specialist

Train a competing XGBoost specialist with `hist`/GPU if practical. Test deeper
trees and more conservative shrinkage than the old litmus model.

Suggested grid:

- `max_depth`: 6, 10, 14, 20
- `eta`: 0.01, 0.02, 0.05
- `min_child_weight`: 1, 5, 20, 100
- `subsample`: 0.6, 0.8, 1.0
- `colsample_bytree`: 0.5, 0.8, 1.0
- `scale_pos_weight`: natural, sqrt imbalance, tuned

Hypothesis: XGBoost may handle the sparse high-order ELF feature space better
at hostile thresholds, even if LightGBM wins training speed.

### E09: Hard-Negative Curriculum

Train in rounds. Start with all trainable ELF data, score all benign ELF and
missed malware, then upweight:

- benign ELF near the hostile boundary
- malware ELF below the general L5 hostile threshold
- malware ELF missed by the current ELF specialist
- benign false positives from `/tmp/false-positives` triage once available

Hypothesis: hostile threshold quality is dominated by a small tail. A curriculum
should improve that tail more than uniform training.

### E10: Label-Noise And Low-Score Inclusion

Include the lower-score ELF rows with soft weights instead of filtering them out.
Use sample score, finding confidence, and disagreement between models to define
label confidence.

Hypothesis: the `score >= 3` filter removes data that is useful for calibration
and boundary shape. Low-confidence data should help if it is weighted rather than
treated as equal truth.

Suggested variants:

- current hard filter baseline
- include all ELF rows with score-derived weights
- soft labels for low-score malware
- downweight rows where general and ELF models strongly disagree

### E11: Stacked ELF Ensemble

Train multiple independent ELF scorers, then train a compact meta-model on
out-of-fold scores:

- general Azoth score
- native-group score
- current ELF LightGBM score
- deep-ngram ELF score
- byte-shape ELF score
- XGBoost ELF score
- hard-negative curriculum score

The meta-model can be logistic regression, isotonic-calibrated logistic
regression, or a tiny LightGBM. Calibrate the routed decision on the full corpus.

Hypothesis: no single feature family owns ELF. A score-level ensemble can gain
recall while keeping the full-corpus FP budget explicit.

### E12: Neural Report Sequence Model

Build a neural ELF specialist that consumes sequences rather than a flat sparse
vector:

- ordered finding IDs and trait prefixes
- file-level metadata tokens
- symbol/string tokens
- severity and confidence embeddings
- optional byte-shape numeric side channel

Start with a small Transformer or FT-Transformer style model. Evaluate it both
directly and as a teacher for LightGBM distillation.

Hypothesis: some ELF malware evidence is positional or compositional. A sequence
model may learn interactions that tree models only approximate with many sparse
cross-features.

## Execution Order

Run the experiments in this order:

1. Build or extend an ELF experiment harness that can use divergent feature
   specs, persist per-model score columns, and reuse the refreshed score table.
2. Run E07 and E08 on the current feature space to establish strong learner
   baselines.
3. Implement E01, E02, and E03 because trait-space expansion is closest to the
   current pipeline and should be cheap to iterate.
4. Implement E04, E05, and E06 because they add the largest new ELF signal.
5. Run E09 and E10 after the stronger base models exist.
6. Run E11 once there are at least three useful independent scorers.
7. Run E12 last. It is the most speculative and has the highest engineering
   cost.

Promotion rule:

- Promote an experiment only if it improves full-corpus L5 hostile recall at the
  same FP budget, or improves L9 hostile recall without hurting L5 hostile.
- If an experiment only improves suspicious, keep it as diagnostic, not as the
  next default.
- If an experiment improves ELF-only metrics but loses routed full-corpus
  hostile performance, keep it for analysis but do not promote it.

## 2026-05-01: E07/E08 First Learner Sweep

Purpose: establish stronger ELF-only learner baselines before adding new
feature families. This run keeps the current Azoth feature space fixed and tests
more aggressive LightGBM and XGBoost configurations. It is an intentionally
bounded first pass: no new deep n-grams, no ELF metadata, no byte-shape features
yet.

Harness:

- Script: `scripts/azoth_elf_research.py`
- Output: `out/models/azoth-elf/research_first_batch.json`
- Model directories: `out/models/azoth-elf/research_first_batch/`
- Feature spec: `out/models/azoth-light-full-leaves96-cpu/feature_spec.json`
- Feature count: 28,960
- Snapshot: `max_id=51198735`
- Full score-cache rows: 2,173,639
- ELF calibration rows visible in score cache: 86,785
- ELF training rows after deterministic train/test split: 70,929

Command:

```sh
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 \
  --device cuda \
  --output-dir out/models/azoth-elf/research_first_batch \
  --output out/models/azoth-elf/research_first_batch.json \
  --candidates first-batch
```

Routed full-corpus results, OR rule:

| Candidate | L5 Hostile Recall @ FP | L9 Hostile Recall @ FP | L5 Suspicious Recall @ FP | L9 Suspicious Recall @ FP | ELF AUC | ELF AP | ELF Max F1 | Fit | Size |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `general_baseline` | 46.75% @ 8 | 53.17% @ 16 | 68.39% @ 65 | 70.66% @ 136 | - | - | - | - | - |
| `lgbm_leaves96_mcs100` | 47.60% @ 8 | 53.92% @ 16 | 69.09% @ 84 | 71.30% @ 142 | 0.999920 | 0.999389 | 0.9924 | 20.3s | 1.15 MB |
| `lgbm_leaves255_mcs25` | 47.50% @ 8 | 53.82% @ 16 | 69.07% @ 85 | 71.25% @ 140 | 0.999844 | 0.998984 | 0.9909 | 12.5s | 1.54 MB |
| `lgbm_leaves511_mcs50` | 47.53% @ 8 | 53.85% @ 16 | 69.09% @ 85 | 71.25% @ 142 | 0.999900 | 0.999294 | 0.9912 | 11.3s | 1.52 MB |
| `lgbm_goss_leaves255_mcs25` | 47.60% @ 8 | 53.92% @ 16 | 69.11% @ 85 | 71.34% @ 142 | 0.999923 | 0.999508 | 0.9942 | 15.5s | 2.30 MB |
| `lgbm_dart_leaves255_mcs25` | 47.34% @ 8 | 53.68% @ 16 | 69.07% @ 85 | 71.22% @ 142 | 0.999884 | 0.999169 | 0.9917 | 56.2s | 5.67 MB |
| `xgb_depth10_eta03` | 47.67% @ 8 | 53.99% @ 16 | 69.11% @ 82 | 71.34% @ 142 | 0.999931 | 0.999493 | 0.9952 | 4.0s | 1.85 MB |
| `xgb_depth14_eta02` | 47.60% @ 8 | 53.92% @ 16 | 69.10% @ 85 | 71.30% @ 142 | 0.999911 | 0.999323 | 0.9932 | 4.8s | 2.02 MB |

Replacement routing was effectively identical to OR for this batch. The best
L5 hostile candidate was `xgb_depth10_eta03`, improving the refreshed general
baseline from 46.75% to 47.67% at the same 8 full-corpus false positives. That
is a +0.92 percentage point absolute lift.

Read:

- XGBoost is worth keeping in the ELF track. It trained faster than LightGBM on
  this slice with CUDA and produced the best hostile operating point.
- The deeper LightGBM leaves sweeps did not beat the simple leaves96 baseline.
  GOSS tied the simple baseline at L5/L9 hostile and had better ELF Max F1, so
  it remains worth testing after feature expansion.
- DART is not attractive here: slower, larger, and worse hostile recall.
- Current-feature learner tuning alone gives a real but small lift. The next
  larger gains probably need E01/E02/E03 feature expansion, not more knob
  polishing on the same feature matrix.

Promotion:

- Keep `xgb_depth10_eta03` as the current E08 leader for the ELF research track.
- Do not promote DART.
- Next run should implement E01/E02/E03 feature-space expansion and evaluate
  `xgb_depth10_eta03`, `lgbm_leaves96_mcs100`, and `lgbm_goss_leaves255_mcs25`
  on the expanded matrix.

## 2026-05-01: E01/E02/E03 Exact + Hierarchy Trait Expansion

Purpose: test whether an unconstrained ELF specialist gains from exact finding
IDs and full trait hierarchy prefixes. This stacks the current 28,960 Azoth
features with ELF-only sparse trait features selected from the ELF training
partition.

Feature extraction:

- Script: `scripts/azoth_elf_research.py`
- Output: `out/models/azoth-elf/research_combo50k_log.json`
- Model directories: `out/models/azoth-elf/research_combo50k_log/`
- Trait vocabulary: `out/models/azoth-elf/research_combo50k_log/trait_vocab.json`
- Base features: 28,960
- Selected trait features: 3,275
- Expanded features: 32,235
- Trait mode: exact finding IDs plus all hierarchy prefixes
- Value: `log1p(count)`
- Minimum malware document frequency: 3
- Maximum benign document fraction: 1%
- Top-K cap: 50,000; not reached after filters
- ELF calibration rows visible in score cache: 86,785
- ELF training rows after deterministic train/test split: 71,171

Command:

```sh
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 \
  --device cuda \
  --trait-mode combo \
  --trait-value log \
  --trait-min-crit 0 \
  --trait-path-depth 0 \
  --trait-top-k 50000 \
  --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.01 \
  --output-dir out/models/azoth-elf/research_combo50k_log \
  --output out/models/azoth-elf/research_combo50k_log.json \
  --candidates expanded-batch
```

Routed full-corpus results, OR rule:

| Candidate | L5 Hostile Recall @ FP | L9 Hostile Recall @ FP | L5 Suspicious Recall @ FP | L9 Suspicious Recall @ FP | ELF AUC | ELF AP | ELF Max F1 | Fit | Size |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `general_baseline` | 46.75% @ 8 | 53.17% @ 16 | 68.39% @ 65 | 70.66% @ 136 | - | - | - | - | - |
| `expanded_xgb_depth10_eta03` | 47.59% @ 8 | 53.91% @ 16 | 69.11% @ 85 | 71.34% @ 142 | 0.999936 | 0.999564 | 0.9945 | 3.8s | 1.65 MB |
| `expanded_lgbm_leaves96_mcs100` | 47.78% @ 8 | 54.10% @ 16 | 69.12% @ 85 | 71.35% @ 141 | 0.999962 | 0.999754 | 0.9964 | 23.6s | 2.16 MB |
| `expanded_lgbm_goss_leaves255_mcs25` | 47.84% @ 8 | 54.16% @ 16 | 69.12% @ 84 | 71.35% @ 142 | 0.999963 | 0.999754 | 0.9960 | 24.8s | 3.82 MB |

Read:

- Exact finding IDs plus full hierarchy prefixes helped, but only modestly.
  Best L5 hostile improved from 46.75% baseline to 47.84% at the same 8 FP.
- Compared with the best current-feature learner sweep result
  (`xgb_depth10_eta03`, 47.67%), this is a +0.17 point absolute gain.
- The winner changed from XGBoost to LightGBM GOSS after adding the sparse trait
  features. That suggests the feature expansion is useful, but this filtered
  version is not yet a breakthrough.
- The 1% benign-prevalence cap is probably conservative. It selected only 3,275
  features out of a 50k cap. The next trait expansion should loosen the benign
  cap and test TF-IDF weighting.

Promotion:

- Current AZOTH-ELF leader: `expanded_lgbm_goss_leaves255_mcs25`.
- Next run: repeat combo traits with a looser benign cap, then test exact-only
  and hierarchy-only ablations so we know which half is carrying the lift.

### Looser Benign-Cap Follow-Up

Purpose: test whether the 1% benign-prevalence cap was too strict. Same feature
mode and learners as above, but allow selected trait features to appear in up to
10% of benign ELF training samples.

Command:

```sh
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 \
  --device cuda \
  --trait-mode combo \
  --trait-value log \
  --trait-min-crit 0 \
  --trait-path-depth 0 \
  --trait-top-k 50000 \
  --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.10 \
  --output-dir out/models/azoth-elf/research_combo50k_log_benign10 \
  --output out/models/azoth-elf/research_combo50k_log_benign10.json \
  --candidates expanded-batch
```

Feature extraction:

- Selected trait features: 3,683
- Expanded features: 32,643
- Output: `out/models/azoth-elf/research_combo50k_log_benign10.json`

Routed full-corpus results, OR rule:

| Candidate | L5 Hostile Recall @ FP | L9 Hostile Recall @ FP | L5 Suspicious Recall @ FP | L9 Suspicious Recall @ FP | ELF AUC | ELF AP | ELF Max F1 | Fit | Size |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `general_baseline` | 46.75% @ 8 | 53.17% @ 16 | 68.39% @ 65 | 70.66% @ 136 | - | - | - | - | - |
| `expanded_xgb_depth10_eta03` | 47.67% @ 8 | 53.99% @ 16 | 69.12% @ 85 | 71.35% @ 142 | 0.999955 | 0.999682 | 0.9956 | 5.1s | 2.06 MB |
| `expanded_lgbm_leaves96_mcs100` | 47.56% @ 8 | 53.88% @ 16 | 69.09% @ 85 | 71.29% @ 142 | 0.999897 | 0.999357 | 0.9924 | 16.8s | 1.21 MB |
| `expanded_lgbm_goss_leaves255_mcs25` | 47.62% @ 8 | 53.95% @ 16 | 69.11% @ 84 | 71.34% @ 140 | 0.999917 | 0.999471 | 0.9942 | 17.0s | 2.13 MB |

Read:

- Loosening the benign cap did not help. It selected only 408 additional
  features and lost the L5/L9 hostile gain from the stricter 1% cap.
- The best result returned to XGBoost, but only matched the current-feature
  XGBoost leader at L5 hostile.
- Keep the 1% benign cap as the current trait-selection setting.

### Exact vs Hierarchy Ablation

Purpose: split the winning `combo` trait family into exact finding IDs and
hierarchy prefixes. Same 1% benign cap, same log-count values, and only the two
most relevant learners.

Commands:

```sh
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode exact --trait-value log \
  --trait-min-crit 0 --trait-path-depth 0 \
  --trait-top-k 50000 --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.01 \
  --output-dir out/models/azoth-elf/research_exact50k_log \
  --output out/models/azoth-elf/research_exact50k_log.json \
  --candidates expanded_xgb_depth10_eta03 expanded_lgbm_goss_leaves255_mcs25

.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode hierarchy --trait-value log \
  --trait-min-crit 0 --trait-path-depth 0 \
  --trait-top-k 50000 --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.01 \
  --output-dir out/models/azoth-elf/research_hierarchy50k_log \
  --output out/models/azoth-elf/research_hierarchy50k_log.json \
  --candidates expanded_xgb_depth10_eta03 expanded_lgbm_goss_leaves255_mcs25
```

Routed full-corpus results, OR rule:

| Feature Set | Trait Features | Candidate | L5 Hostile Recall @ FP | L9 Hostile Recall @ FP | L5 Suspicious Recall @ FP | L9 Suspicious Recall @ FP | ELF AUC | ELF AP | ELF Max F1 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exact IDs | 2,341 | `expanded_xgb_depth10_eta03` | 47.69% @ 8 | 54.01% @ 16 | 69.12% @ 84 | 71.35% @ 141 | 0.999959 | 0.999690 | 0.9958 |
| exact IDs | 2,341 | `expanded_lgbm_goss_leaves255_mcs25` | 47.81% @ 8 | 54.13% @ 16 | 69.12% @ 82 | 71.35% @ 142 | 0.999962 | 0.999730 | 0.9959 |
| hierarchy prefixes | 935 | `expanded_xgb_depth10_eta03` | 47.69% @ 8 | 54.01% @ 16 | 69.12% @ 83 | 71.35% @ 142 | 0.999949 | 0.999609 | 0.9957 |
| hierarchy prefixes | 935 | `expanded_lgbm_goss_leaves255_mcs25` | 47.81% @ 8 | 54.13% @ 16 | 69.12% @ 79 | 71.35% @ 142 | 0.999953 | 0.999714 | 0.9960 |

Read:

- Exact-only and hierarchy-only are nearly tied. The combo run remains slightly
  better at L5/L9 hostile, but hierarchy-only uses less than a third of the
  trait features and matches within noise.
- The broad hierarchy prefixes are carrying more value than expected. That
  makes deeper E01 n-grams over hierarchy paths more attractive than exploding
  exact-ID combinations first.
- Current leader remains `combo + lgbm_goss` at 47.84% L5 hostile, but
  `hierarchy + lgbm_goss` is the simpler fallback at 47.81%.

## 2026-05-01: Deep N-Grams, Metrics, Symbols, Formula

Purpose: follow up on the older experiment ideas that worked directionally:
formula/skeleton signal, suspicious/hostile and notable+ path n-grams, full
metrics, symbols, and strings. These runs use the expanded ELF harness so each
feature family can be evaluated against the same full-corpus routed threshold
gate.

Harness changes:

- `scripts/azoth_elf_research.py` now supports `--extra-families`:
  `ngrams`, `metrics`, `symbols`, and `formula`.
- N-grams are arbitrary path combinations up to order 8, with configurable
  `min_crit`, `path_depth`, max paths per file, and max n-grams per file.
- Metrics add raw numeric values plus present/missing indicators.
- Symbols tokenize `ss` entries into whole short strings and string tokens,
  with a no-symbols missingness token.
- Formula adds formula length buckets, element presence, and skeleton character
  n-grams.

Commands:

```sh
# Suspicious+ and hostile, full path depth, combinations up to 8.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode none \
  --extra-families ngrams \
  --extra-value log \
  --extra-top-k 50000 \
  --extra-min-malware-freq 3 \
  --extra-max-benign-frac 0.01 \
  --ngram-order-min 2 \
  --ngram-order-max 8 \
  --ngram-min-crit 4 \
  --ngram-path-depth 0 \
  --ngram-max-paths 16 \
  --ngram-max-per-file 20000 \
  --output-dir out/models/azoth-elf/research_ngram_susp_full_o8 \
  --output out/models/azoth-elf/research_ngram_susp_full_o8.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25 expanded_xgb_depth10_eta03

# Notable+, path depth 3, combinations up to 8.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode none \
  --extra-families ngrams \
  --extra-value log \
  --extra-top-k 50000 \
  --extra-min-malware-freq 3 \
  --extra-max-benign-frac 0.01 \
  --ngram-order-min 2 \
  --ngram-order-max 8 \
  --ngram-min-crit 3 \
  --ngram-path-depth 3 \
  --ngram-max-paths 16 \
  --ngram-max-per-file 20000 \
  --output-dir out/models/azoth-elf/research_ngram_notable_d3_o8 \
  --output out/models/azoth-elf/research_ngram_notable_d3_o8.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25 expanded_xgb_depth10_eta03

# Full metrics plus missingness.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode none \
  --extra-families metrics \
  --extra-min-malware-freq 3 \
  --extra-max-benign-frac 1.0 \
  --output-dir out/models/azoth-elf/research_metrics_full \
  --output out/models/azoth-elf/research_metrics_full.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25 expanded_xgb_depth10_eta03

# Symbols and strings.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode none \
  --extra-families symbols \
  --extra-value log \
  --extra-top-k 50000 \
  --extra-min-malware-freq 3 \
  --extra-max-benign-frac 0.01 \
  --output-dir out/models/azoth-elf/research_symbols50k_log \
  --output out/models/azoth-elf/research_symbols50k_log.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25 expanded_xgb_depth10_eta03

# Combo leader plus metrics, symbols, and formula.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode combo \
  --trait-value log \
  --trait-min-crit 0 \
  --trait-path-depth 0 \
  --trait-top-k 50000 \
  --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.01 \
  --extra-families metrics symbols formula \
  --extra-value log \
  --extra-top-k 50000 \
  --extra-min-malware-freq 3 \
  --extra-max-benign-frac 0.01 \
  --output-dir out/models/azoth-elf/research_combo_metrics_symbols_formula \
  --output out/models/azoth-elf/research_combo_metrics_symbols_formula.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25
```

Routed full-corpus results, OR rule:

| Feature Set | Features | Candidate | L5 Hostile Recall @ FP | L9 Hostile Recall @ FP | L5 Suspicious Recall @ FP | L9 Suspicious Recall @ FP | ELF AUC | ELF AP | ELF Max F1 |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| previous leader: combo traits | 32,235 | `expanded_lgbm_goss_leaves255_mcs25` | 47.84% @ 8 | 54.16% @ 16 | 69.12% @ 84 | 71.35% @ 142 | 0.999963 | 0.999754 | 0.9960 |
| suspicious+ n-grams, full depth, order<=8 | 78,960 | `expanded_lgbm_goss_leaves255_mcs25` | 47.77% @ 8 | 54.09% @ 16 | 69.12% @ 83 | 71.35% @ 142 | 0.999954 | 0.999656 | 0.9956 |
| suspicious+ n-grams, full depth, order<=8 | 78,960 | `expanded_xgb_depth10_eta03` | 47.67% @ 8 | 53.99% @ 16 | 69.11% @ 83 | 71.35% @ 142 | 0.999950 | 0.999610 | 0.9954 |
| notable+ n-grams, depth=3, order<=8 | 78,960 | `expanded_lgbm_goss_leaves255_mcs25` | 47.76% @ 8 | 54.08% @ 16 | 69.12% @ 85 | 71.35% @ 142 | 0.999963 | 0.999729 | 0.9955 |
| notable+ n-grams, depth=3, order<=8 | 78,960 | `expanded_xgb_depth10_eta03` | 47.69% @ 8 | 54.01% @ 16 | 69.11% @ 83 | 71.35% @ 141 | 0.999955 | 0.999639 | 0.9952 |
| full metrics + missingness | 29,554 | `expanded_lgbm_goss_leaves255_mcs25` | 47.73% @ 8 | 54.05% @ 16 | 69.12% @ 80 | 71.35% @ 141 | 0.999973 | 0.999783 | 0.9968 |
| full metrics + missingness | 29,554 | `expanded_xgb_depth10_eta03` | 47.67% @ 8 | 53.99% @ 16 | 69.12% @ 85 | 71.35% @ 142 | 0.999963 | 0.999780 | 0.9966 |
| symbols/strings | 78,960 | `expanded_lgbm_goss_leaves255_mcs25` | 47.77% @ 8 | 54.09% @ 16 | 69.12% @ 85 | 71.35% @ 142 | 0.999971 | 0.999787 | 0.9967 |
| symbols/strings | 78,960 | `expanded_xgb_depth10_eta03` | 47.73% @ 8 | 54.05% @ 16 | 69.12% @ 85 | 71.35% @ 142 | 0.999987 | 0.999883 | 0.9962 |
| combo traits + metrics + symbols + formula | 86,592 | `expanded_lgbm_goss_leaves255_mcs25` | 47.85% @ 8 | 54.16% @ 16 | 69.12% @ 85 | 71.35% @ 141 | 0.999970 | 0.999789 | 0.9968 |

Read:

- Deep path n-grams are not a win in this first bounded form. Both
  suspicious+ full-depth and notable+ depth-3 variants hit the 50k feature cap
  but underperformed the simpler combo-trait leader at hostile L5/L9.
- Full metrics and symbol/string features improve ELF ranking metrics
  materially, especially AUC/AP/Max F1, but they do not move the hostile
  full-corpus operating point enough by themselves.
- The combined run is technically the new numeric best at L5 hostile
  (47.846% vs 47.841%), but the gain is too small for the added complexity:
  +54,351 extra columns beyond combo traits.
- Formula tokens did not produce a visible hostile jump when added with metrics
  and symbols. A formula-only ablation may still be useful, but it is not an
  obvious next promotion candidate.

Promotion:

- Do not promote the kitchen-sink combo yet. It is a measurement tie, not a
  meaningful win.
- Keep the practical leader as `combo traits + lgbm_goss`.
- Keep metrics and symbols as candidates for a later stacked ensemble because
  they improve broad ELF ranking metrics even when they do not improve hostile
  L5 directly.
- For n-grams, stop testing larger raw combinations for now. If revisiting,
  test smaller, structured families: hostile-only order<=4, notable+ depth=2,
  or learned hashing instead of selected explicit combinations.

## 2026-05-01: Trait Weighting And Severity Filters

Purpose: begin the next 20-experiment round with cheap tests that reuse the
current best exact+hierarchy trait feature family. These runs test whether
weighting, presence-only encoding, or severity filtering improves the hostile
operating point.

Commands:

```sh
# TF-IDF instead of log-counts.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode combo --trait-value tfidf \
  --trait-min-crit 0 --trait-path-depth 0 \
  --trait-top-k 50000 --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.01 \
  --output-dir out/models/azoth-elf/research_combo50k_tfidf \
  --output out/models/azoth-elf/research_combo50k_tfidf.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25

# Boolean presence instead of log-counts.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode combo --trait-value boolean \
  --trait-min-crit 0 --trait-path-depth 0 \
  --trait-top-k 50000 --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.01 \
  --output-dir out/models/azoth-elf/research_combo50k_boolean \
  --output out/models/azoth-elf/research_combo50k_boolean.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25

# Suspicious+ only.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode combo --trait-value log \
  --trait-min-crit 4 --trait-path-depth 0 \
  --trait-top-k 50000 --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.01 \
  --output-dir out/models/azoth-elf/research_combo_susp_log \
  --output out/models/azoth-elf/research_combo_susp_log.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25

# Hostile only.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode combo --trait-value log \
  --trait-min-crit 5 --trait-path-depth 0 \
  --trait-top-k 50000 --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.01 \
  --output-dir out/models/azoth-elf/research_combo_hostile_log \
  --output out/models/azoth-elf/research_combo_hostile_log.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25
```

Routed full-corpus results, OR rule:

| Experiment | Trait Features | L5 Hostile Recall @ FP | L9 Hostile Recall @ FP | L5 Suspicious Recall @ FP | L9 Suspicious Recall @ FP | ELF AUC | ELF AP | ELF Max F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| previous leader: combo log-counts | 3,275 | 47.84% @ 8 | 54.16% @ 16 | 69.12% @ 84 | 71.35% @ 142 | 0.999963 | 0.999754 | 0.9960 |
| combo TF-IDF | 3,284 | 47.82% @ 8 | 54.14% @ 16 | 69.12% @ 81 | 71.35% @ 142 | 0.999951 | 0.999680 | 0.9956 |
| combo boolean | 3,286 | 47.56% @ 8 | 53.88% @ 16 | 69.11% @ 84 | 71.34% @ 142 | 0.999938 | 0.999515 | 0.9937 |
| suspicious+ combo log-counts | 1,145 | 47.83% @ 8 | 54.15% @ 16 | 69.12% @ 85 | 71.35% @ 142 | 0.999961 | 0.999681 | 0.9953 |
| hostile-only combo log-counts | 451 | 47.61% @ 8 | 53.93% @ 16 | 69.11% @ 85 | 71.34% @ 142 | 0.999930 | 0.999447 | 0.9939 |

Read:

- Log-counts remain the best value encoding. TF-IDF is close but does not win;
  boolean presence loses materially.
- Suspicious+ filtering is almost tied with all-crit combo traits using about a
  third of the features, but still trails slightly at hostile L5/L9.
- Hostile-only traits are too sparse. They are useful signal, but not enough by
  themselves.

Promotion:

- Keep `combo traits + log-counts + lgbm_goss` as the current practical leader.
- Suspicious+ combo is a compact fallback, but not the accuracy leader.

## 2026-05-01: Smaller Structured N-Grams

Purpose: revisit n-grams in smaller, sharper forms after the order-8 raw
families failed to beat the combo-trait leader.

Commands:

```sh
# Hostile-only, depth 3, order 2..4.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode none \
  --extra-families ngrams \
  --extra-value log \
  --extra-top-k 50000 \
  --extra-min-malware-freq 3 \
  --extra-max-benign-frac 0.01 \
  --ngram-order-min 2 \
  --ngram-order-max 4 \
  --ngram-min-crit 5 \
  --ngram-path-depth 3 \
  --ngram-max-paths 16 \
  --ngram-max-per-file 20000 \
  --output-dir out/models/azoth-elf/research_ngram_hostile_d3_o4 \
  --output out/models/azoth-elf/research_ngram_hostile_d3_o4.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25

# Suspicious+, depth 2, order 2..4.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode none \
  --extra-families ngrams \
  --extra-value log \
  --extra-top-k 50000 \
  --extra-min-malware-freq 3 \
  --extra-max-benign-frac 0.01 \
  --ngram-order-min 2 \
  --ngram-order-max 4 \
  --ngram-min-crit 4 \
  --ngram-path-depth 2 \
  --ngram-max-paths 16 \
  --ngram-max-per-file 20000 \
  --output-dir out/models/azoth-elf/research_ngram_susp_d2_o4 \
  --output out/models/azoth-elf/research_ngram_susp_d2_o4.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25

# Notable+, depth 2, order 2..4.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode none \
  --extra-families ngrams \
  --extra-value log \
  --extra-top-k 50000 \
  --extra-min-malware-freq 3 \
  --extra-max-benign-frac 0.01 \
  --ngram-order-min 2 \
  --ngram-order-max 4 \
  --ngram-min-crit 3 \
  --ngram-path-depth 2 \
  --ngram-max-paths 16 \
  --ngram-max-per-file 20000 \
  --output-dir out/models/azoth-elf/research_ngram_notable_d2_o4 \
  --output out/models/azoth-elf/research_ngram_notable_d2_o4.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25
```

Routed full-corpus results, OR rule:

| Experiment | N-Gram Features | L5 Hostile Recall @ FP | L9 Hostile Recall @ FP | L5 Suspicious Recall @ FP | L9 Suspicious Recall @ FP | ELF AUC | ELF AP | ELF Max F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| previous leader: combo traits | 3,275 | 47.84% @ 8 | 54.16% @ 16 | 69.12% @ 84 | 71.35% @ 142 | 0.999963 | 0.999754 | 0.9960 |
| hostile-only depth=3 order<=4 | 312 | 47.74% @ 8 | 54.06% @ 16 | 69.12% @ 85 | 71.35% @ 141 | 0.999954 | 0.999665 | 0.9953 |
| suspicious+ depth=2 order<=4 | 2,808 | 47.77% @ 8 | 54.09% @ 16 | 69.12% @ 83 | 71.35% @ 142 | 0.999954 | 0.999638 | 0.9953 |
| notable+ depth=2 order<=4 | 27,698 | 47.75% @ 8 | 54.07% @ 16 | 69.12% @ 79 | 71.35% @ 142 | 0.999956 | 0.999674 | 0.9957 |

Read:

- Smaller structured n-grams also do not beat combo traits.
- Suspicious+ depth=2 is the best n-gram variant so far, but still trails by
  about 0.07 points at L5 hostile.
- Hostile-only is too sparse, and notable+ depth=2 adds many features without
  hostile gain.

Promotion:

- Do not promote explicit n-grams.
- If n-grams return later, test hashing or use them as a separate scorer in a
  stacked ensemble rather than appending selected explicit n-gram columns.

## 2026-05-01: Combo-Plus-Family Ablations

Purpose: split the prior kitchen-sink result into single-family additions on
top of the current combo-trait leader.

Commands:

```sh
# Combo traits + metrics.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode combo --trait-value log \
  --trait-min-crit 0 --trait-path-depth 0 \
  --trait-top-k 50000 --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.01 \
  --extra-families metrics \
  --extra-min-malware-freq 3 \
  --extra-max-benign-frac 0.01 \
  --output-dir out/models/azoth-elf/research_combo_metrics \
  --output out/models/azoth-elf/research_combo_metrics.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25

# Combo traits + symbols.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode combo --trait-value log \
  --trait-min-crit 0 --trait-path-depth 0 \
  --trait-top-k 50000 --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.01 \
  --extra-families symbols \
  --extra-value log \
  --extra-top-k 50000 \
  --extra-min-malware-freq 3 \
  --extra-max-benign-frac 0.01 \
  --output-dir out/models/azoth-elf/research_combo_symbols \
  --output out/models/azoth-elf/research_combo_symbols.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25

# Combo traits + formula.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode combo --trait-value log \
  --trait-min-crit 0 --trait-path-depth 0 \
  --trait-top-k 50000 --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.01 \
  --extra-families formula \
  --extra-value log \
  --extra-top-k 50000 \
  --extra-min-malware-freq 3 \
  --extra-max-benign-frac 0.01 \
  --output-dir out/models/azoth-elf/research_combo_formula \
  --output out/models/azoth-elf/research_combo_formula.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25

# Combo traits + best compact n-gram family.
.venv/bin/python scripts/azoth_elf_research.py \
  --workers 64 --device cuda \
  --trait-mode combo --trait-value log \
  --trait-min-crit 0 --trait-path-depth 0 \
  --trait-top-k 50000 --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.01 \
  --extra-families ngrams \
  --extra-value log \
  --extra-top-k 50000 \
  --extra-min-malware-freq 3 \
  --extra-max-benign-frac 0.01 \
  --ngram-order-min 2 \
  --ngram-order-max 4 \
  --ngram-min-crit 4 \
  --ngram-path-depth 2 \
  --ngram-max-paths 16 \
  --ngram-max-per-file 20000 \
  --output-dir out/models/azoth-elf/research_combo_ngram_susp_d2_o4 \
  --output out/models/azoth-elf/research_combo_ngram_susp_d2_o4.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25
```

Routed full-corpus results, OR rule:

| Experiment | Total Features | Extra Features | L5 Hostile Recall @ FP | L9 Hostile Recall @ FP | L5 Suspicious Recall @ FP | L9 Suspicious Recall @ FP | ELF AUC | ELF AP | ELF Max F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| previous leader: combo traits | 32,235 | 3,275 | 47.84% @ 8 | 54.16% @ 16 | 69.12% @ 84 | 71.35% @ 142 | 0.999963 | 0.999754 | 0.9960 |
| combo + metrics | 32,569 | 321 | 47.84% @ 8 | 54.16% @ 16 | 69.12% @ 85 | 71.35% @ 142 | 0.999934 | 0.999519 | 0.9954 |
| combo + symbols | 82,249 | 50,000 | 47.78% @ 8 | 54.10% @ 16 | 69.12% @ 84 | 71.35% @ 142 | 0.999940 | 0.999594 | 0.9961 |
| combo + formula | 36,310 | 4,059 | 47.67% @ 8 | 53.99% @ 16 | 69.11% @ 85 | 71.35% @ 142 | 0.999926 | 0.999506 | 0.9952 |
| combo + suspicious depth=2 order<=4 n-grams | 35,064 | 2,812 | 47.75% @ 8 | 54.07% @ 16 | 69.12% @ 83 | 71.35% @ 142 | 0.999940 | 0.999641 | 0.9956 |

Read:

- No single additional family improves the combo-trait leader.
- Metrics tie the hostile operating point but reduce broad ELF ranking metrics
  in this paired run, so they are not an obvious additive feature.
- Symbols, formula, and compact n-grams all hurt hostile recall when appended to
  combo traits.

Promotion:

- No promotion.
- Avoid appending these families directly to combo traits. If used later, use
  them as separate scorers for stacking, not as more columns in the same model.

## 2026-05-02: Deployable ELF Route Optimization

Purpose: test whether the deployable ELF specialist can improve routed
full-corpus detection when used with different route rules, and whether a
deployable tail-focused ELF model can beat the current ELF specialist under the
same full-corpus FP budget.

Command:

```sh
.venv/bin/python scripts/elf_ensemble_experiments.py \
  --db postgres://hopper@localhost:5432/hopper \
  --general-scores out/models/azoth/general/threshold_scores.npz \
  --general-spec out/models/azoth/general/feature_spec.json \
  --teacher-model out/models/azoth/filetypes/elf/model.txt \
  --teacher-spec out/models/azoth/filetypes/elf/feature_spec.json \
  --output-dir out/models/azoth/elf_route_optimization \
  --output out/models/azoth/elf_route_optimization.json \
  --workers 64
```

Snapshot:

- Full-corpus rows: 2,293,938
- Malware rows: 472,475
- Benign rows: 1,821,463
- ELF calibration rows: 110,933
- ELF training rows: 96,109 on the rerun that added route-local policy metrics

Routed full-corpus results:

| Candidate | Rule | L5 Hostile Recall @ FP | L9 Hostile Recall @ FP | L5 Suspicious Recall @ FP | L9 Suspicious Recall @ FP |
| --- | --- | ---: | ---: | ---: | ---: |
| general baseline | general | 47.08% @ 9 | 55.18% @ 16 | 65.51% @ 87 | 71.74% @ 145 |
| current ELF teacher | OR | 48.34% @ 9 | 56.20% @ 16 | 66.13% @ 87 | 72.05% @ 145 |
| current ELF teacher | replacement | 48.34% @ 9 | 56.20% @ 16 | 66.13% @ 87 | 72.05% @ 145 |
| current ELF teacher | acquittal | 48.34% @ 9 | 56.20% @ 16 | 66.13% @ 87 | 72.05% @ 145 |
| tail contrast | OR | 48.65% @ 9 | 56.50% @ 16 | 66.43% @ 87 | 72.35% @ 145 |
| tail contrast | replacement | 48.65% @ 9 | 56.50% @ 16 | 66.43% @ 87 | 72.35% @ 145 |
| tail contrast | acquittal | 48.65% @ 9 | 56.50% @ 16 | 66.43% @ 87 | 72.35% @ 145 |
| teacher distill | OR | 48.58% @ 9 | 56.44% @ 16 | 66.37% @ 87 | 72.29% @ 145 |
| teacher distill | replacement | 48.57% @ 9 | 56.43% @ 16 | 66.35% @ 87 | 72.28% @ 145 |
| teacher distill | acquittal | 48.58% @ 9 | 56.44% @ 16 | 66.37% @ 87 | 72.29% @ 145 |
| ranker | OR | 47.72% @ 9 | 55.62% @ 16 | 65.74% @ 87 | 71.86% @ 145 |
| ranker | replacement | 47.62% @ 9 | 55.47% @ 16 | 65.40% @ 87 | 71.32% @ 145 |
| ranker | acquittal | 47.72% @ 9 | 55.62% @ 16 | 65.74% @ 87 | 71.86% @ 145 |

Read:

- Tail contrast is the best deployable candidate in this harness. It improves
  L5 hostile by +1.57 points over general and +0.31 points over the current ELF
  specialist at the same 9 full-corpus false positives.
- OR, replacement, and acquittal are identical for the useful candidates in this
  run. The current ELF route is buying extra positives, not reducing enough
  general false positives to make replacement/acquittal matter yet.
- Distillation is close to tail contrast but slightly weaker. Ranker is weaker.
- The earlier expanded ELF research models are not yet replayable by this
  generic harness: their saved model expects appended sidecar features, but the
  saved `feature_spec.json` alone does not reproduce those columns. Promotion of
  those models requires persisting the extra vocabularies as first-class route
  feature specs or adding an ELF-specific extractor.

Promotion:

- Promote `tail_contrast` as the next ELF specialist candidate for integrated
  azoth calibration, after wiring it into `azoth/filetypes/elf` or adding a
  candidate-specialist input path to ensemble calibration.
- Add a repeatable `make elf-route-optimization` target so this comparison can
  be rerun after new general or ELF specialists are trained.

### ELF-Local Policy Metrics

The full-corpus marginal table above is not enough to judge whether the ELF
specialist should own the ELF route. This rerun also calibrated policies on ELF
files only, while reporting both ELF-local FP/M and the equivalent contribution
to global FP/M.

At L5 hostile, the ELF-local budget is 1 benign ELF false positive:

| Candidate | Policy | ELF Recall | ELF FP | ELF FP/1M | Global FP/1M | Precision | F1 | Accuracy |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| general baseline | general only | 88.24% | 1 | 10.49 | 0.549 | 99.99% | 93.75% | 98.34% |
| current ELF specialist | OR, general-primary | 89.37% | 1 | 10.49 | 0.549 | 99.99% | 94.38% | 98.50% |
| tail contrast | ELF only | 99.26% | 1 | 10.49 | 0.549 | 99.99% | 99.62% | 99.89% |
| tail contrast | specialist-primary | 99.26% | 1 | 10.49 | 0.549 | 99.99% | 99.62% | 99.89% |
| teacher distill | specialist-primary | 94.93% | 1 | 10.49 | 0.549 | 99.99% | 97.39% | 99.29% |
| ranker | OR, general-primary | 88.48% | 1 | 10.49 | 0.549 | 99.99% | 93.89% | 98.38% |

At L9 suspicious, the ELF-local budget is 7 benign ELF false positives:

| Candidate | Policy | ELF Recall | ELF FP | ELF FP/1M | Global FP/1M | Precision | F1 | Accuracy |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| general baseline | general only | 90.38% | 7 | 73.43 | 3.843 | 99.95% | 94.92% | 98.64% |
| current ELF specialist | specialist-primary | 95.54% | 7 | 73.43 | 3.843 | 99.95% | 97.70% | 99.37% |
| tail contrast | ELF only | 99.69% | 7 | 73.43 | 3.843 | 99.96% | 99.82% | 99.95% |
| tail contrast | specialist-primary | 99.69% | 7 | 73.43 | 3.843 | 99.96% | 99.82% | 99.95% |
| teacher distill | specialist-primary | 96.95% | 7 | 73.43 | 3.843 | 99.95% | 98.43% | 99.56% |
| ranker | OR, general-primary | 90.52% | 7 | 73.43 | 3.843 | 99.95% | 95.00% | 98.66% |

Read:

- Route-local calibration changes the story completely. Tail contrast is a
  strong ELF detector when it is allowed to own the ELF route: 99.26% L5 hostile
  recall and 99.69% L9 suspicious recall at tiny global FP contribution.
- For tail contrast, `ELF only` and `specialist-primary` tie. General is not
  needed for this route at these operating points.
- The current global OR calibration underuses the ELF specialist because it asks
  "how much global marginal recall does this add?" instead of "what is the best
  calibrated policy for ELF files?"

Promotion:

- Azoth should add route-owned policy search. For ELF, the current winning
  policy is `specialist-primary` with tail contrast thresholds, effectively
  `az/elf` owning the ELF route.
- The deployment gate should check both ELF-local FP/M and the full-corpus FP
  contribution before emitting this policy for litmus.

## 2026-05-02: Per-Filetype Policy Search With General Escape

Purpose: turn the route-local idea into a general Azoth artifact. The policy
search evaluates each filetype route independently and chooses among:

- `general_only`
- `group_only`
- `filetype_only`
- `or_general_primary`
- `group_primary_with_escape`
- `specialist_primary_with_escape`

The `*_with_escape` policies start with the specialist or group model, then add
general/group/type thresholds only when they improve recall inside the route FP
budget. This preserves high-confidence general detections when they are still
useful.

Commands:

```sh
make azoth-policies

make azoth-policies WORKERS=64 \
  AZOTH_ROUTE_POLICIES=out/models/azoth/route_policies.tail-elf.json \
  AZOTH_ROUTE_POLICIES_CSV=out/models/azoth/route_policies.tail-elf.csv \
  AZOTH_ROUTE_POLICIES_MD=out/models/azoth/route_policies.tail-elf.md \
  AZOTH_POLICY_OVERRIDE_ROUTE=filetypes/elf=out/models/azoth/elf_route_optimization/tail_contrast
```

Tail-ELF policy result:

| Level | Severity | Policy | Thresholds | ELF Recall | ELF FP | ELF FP/1M | Global FP/1M | F1 | Accuracy |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | hostile | specialist_primary_with_escape | `az/elf=0.999821, az=0.967762` | 95.96% | 0 | 0.00 | 0.000 | 97.94% | 99.43% |
| 5 | hostile | specialist_primary_with_escape | `az/elf=0.995194` | 99.26% | 1 | 10.49 | 0.549 | 99.62% | 99.89% |
| 9 | hostile | specialist_primary_with_escape | `az/elf=0.995194` | 99.26% | 1 | 10.49 | 0.549 | 99.62% | 99.89% |
| 5 | suspicious | specialist_primary_with_escape | `az/elf=0.980489` | 99.57% | 3 | 31.47 | 1.647 | 99.78% | 99.94% |
| 9 | suspicious | specialist_primary_with_escape | `az/elf=0.921817` | 99.69% | 7 | 73.43 | 3.843 | 99.82% | 99.95% |

Read:

- This policy search does preserve high-confidence general hits. At L0 hostile,
  general contributes under a zero-FP route budget, so it remains in the policy.
- At L5/L9 hostile, general does not add recall after tail ELF within the
  route budget, so the best policy is effectively ELF-only.
- Weak routes also benefit: many choose `or_general_primary` or
  `specialist_primary_with_escape`, depending on whether the specialist has
  enough independent value.

Promotion:

- Keep `route_policies.json` as the Azoth-side contract for litmus policy
  execution.
- Before deploying the tail ELF policy, promote the `tail_contrast` model into
  the actual `filetypes/elf` bundle or teach config to reference a candidate
  model directory. The policy artifact must match the model litmus loads.
