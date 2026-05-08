# AZOTH Source Research Log

This log tracks source-filegroup specialist experiments. The target filetypes
are:

`c`, `cpp`, `csharp`, `go`, `java`, `kotlin`, `makefile`, `rust`, `scala`,
`swift`.

The starting recipe is a rough hybrid of the general model and the winning ELF
specialist shape:

- general Azoth feature matrix
- source-specific exact + hierarchy trait features
- optional metrics, symbol/string, and formula features
- LightGBM GOSS candidate from the ELF track

Primary metric is source-only recall at fixed source false-positive budgets.
Full-corpus routed recall is deployment context, not the source-specialist
quality metric.

## 2026-05-01: Source Baseline

Snapshot:

- Score-cache snapshot: `max_id=51198735`
- Source target rows in score cache: 689,027
- Source malware rows: 7,141
- Source benign rows: 681,886
- Train rows after score filter and deterministic split: about 10.2k

Source filetype counts at the snapshot:

| Type | Total | Malware | Benign | Trainable |
| --- | ---: | ---: | ---: | ---: |
| `c` | 420,469 | 5,672 | 414,797 | 7,707 |
| `go` | 83,759 | 804 | 82,955 | 2,801 |
| `rust` | 61,316 | 52 | 61,264 | 86 |
| `csharp` | 32,310 | 635 | 31,675 | 555 |
| `kotlin` | 27,315 | 355 | 26,960 | 293 |
| `swift` | 24,288 | 0 | 24,288 | 3 |
| `java` | 20,238 | 18 | 20,220 | 91 |
| `makefile` | 17,682 | 50 | 17,632 | 150 |
| `scala` | 2,127 | 0 | 2,127 | 1 |

Commands:

```sh
# Combo traits only.
.venv/bin/python scripts/azoth_elf_research.py \
  --target-name source \
  --file-types c cpp csharp go java kotlin makefile rust scala swift \
  --workers 64 --device cuda \
  --trait-mode combo \
  --trait-value log \
  --trait-min-crit 0 \
  --trait-path-depth 0 \
  --trait-top-k 50000 \
  --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.01 \
  --output-dir out/models/azoth-source/research_combo \
  --output out/models/azoth-source/research_combo.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25

# ELF-style hybrid: combo traits + metrics + symbols + formula.
.venv/bin/python scripts/azoth_elf_research.py \
  --target-name source \
  --file-types c cpp csharp go java kotlin makefile rust scala swift \
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
  --output-dir out/models/azoth-source/research_hybrid \
  --output out/models/azoth-source/research_hybrid.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25
```

Results:

| Model | Features | Source AUC | Source AP | Max F1 | Recall @ 0 FP | Recall @ 1 FP | Recall @ 40 FP/M | Full-Corpus L5 Hostile |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| combo traits | 30,965 | 0.8814 | 0.6336 | 0.7144 | 42.11% | 47.89% | 49.81% | 47.46% @ 8 FP |
| hybrid | 44,083 | 0.8880 | 0.6469 | 0.7391 | 41.58% | 47.28% | 55.83% | 47.45% @ 8 FP |

Read:

- Source is much harder than ELF. The first source model is not close to the
  ELF specialist's 97%+ zero-FP recall.
- The source group is dominated by C and Go, with weak support for several
  languages. A single source-group model may be too broad.
- Combo-only is better at zero-FP recall, while the hybrid is better at broader
  ranking and looser source FP budgets.
- Metrics/symbols/formula help ranking and recall at 40 FP/M, but cost the
  strict zero-FP point.

Current baseline:

- Use `research_combo.json` as the strict zero-FP baseline.
- Use `research_hybrid.json` as the broad-ranking baseline.

## 2026-05-01: Formula, Elements, And Density Mini-Batch

I added two explicit source research feature families to
`scripts/azoth_elf_research.py`:

- `elements`: element tokens from `samples.elements`, with formula-derived
  fallback tokens when the elements field is absent.
- `density`: fixed hostile/suspicious finding density features measured across
  report files, including count, per-KB, top-file, file-fraction, category
  breadth, and hostile-share signals.

The live training pool grew from 10,242 to 10,249 trainable source rows during
these runs. The score-cache snapshot and full source target pool stayed fixed at
689,027 target rows.

Commands follow the same source baseline shape, changing only
`--extra-families` and the output path:

```sh
.venv/bin/python scripts/azoth_elf_research.py \
  --target-name source \
  --file-types c cpp csharp go java kotlin makefile rust scala swift \
  --workers 64 --device cuda \
  --trait-mode combo --trait-value log \
  --trait-min-crit 0 --trait-path-depth 0 \
  --trait-top-k 50000 --trait-min-malware-freq 3 \
  --trait-max-benign-frac 0.01 \
  --extra-families formula \
  --extra-value log --extra-top-k 50000 \
  --extra-min-malware-freq 3 --extra-max-benign-frac 0.01 \
  --output-dir out/models/azoth-source/research_combo_formula \
  --output out/models/azoth-source/research_combo_formula.json \
  --candidates expanded_lgbm_goss_leaves255_mcs25
```

Results:

| Model | Extra Features | Source AUC | Source AP | Max F1 | Recall @ 0 FP | Recall @ 1 FP | Recall @ 40 FP/M | Full-Corpus L5 Hostile |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| combo traits | 0 | 0.8814 | 0.6336 | 0.7144 | 42.11% | 47.89% | 49.81% | 47.46% @ 8 FP |
| combo + formula | 2,255 | 0.8835 | 0.6424 | 0.7170 | 43.38% | 47.51% | 50.81% | 47.49% @ 8 FP |
| combo + elements | 173 | 0.8830 | 0.6388 | 0.7172 | 42.08% | 48.56% | 53.42% | 47.46% @ 8 FP |
| combo + density | 14 | 0.8841 | 0.6459 | 0.7376 | 45.26% | 47.61% | 54.63% | 47.52% @ 8 FP |
| combo + formula + elements + density | 2,442 | 0.8815 | 0.6410 | 0.7269 | 41.84% | 48.61% | 52.71% | 47.46% @ 8 FP |

Read:

- Explicit density is the keeper from this batch. It improved strict source
  recall by +3.15 points over combo-only and nearly matched the broad hybrid at
  40 FP/M without the 10,839 symbol features.
- Formula helped zero-FP recall and AP, but not enough to justify bundling it
  blindly with every other source feature.
- Elements helped the 1 FP and 40 FP/M points, but did not improve the strict
  zero-FP frontier by itself.
- The combined formula+elements+density run did not compose additively. Treat
  the families as knobs for future per-language or stacked experiments, not a
  default bundle yet.

## 12 Source Experiments

### S01: Language-Split Source Models

Train separate specialists for `c`, `go`, and `csharp+kotlin+java+makefile`
instead of one source group. Evaluate each language route and an OR ensemble.

Hypothesis: C dominates the current source group, and language-specific source
signals differ enough that one model is blurring them.

### S02: C-Only Specialist

Train a C-only specialist using the combo-trait and hybrid feature sets.

Hypothesis: because C has most malware and benign support, it should be the
first source subtype where we can get ELF-like behavior.

### S03: Go-Only Specialist

Train a Go-only specialist. Include symbol/string tokens aggressively.

Hypothesis: Go malware leaks distinctive package paths, runtime strings, and
symbol patterns that a mixed source model dilutes.

### S04: Source Combo Traits, TF-IDF And Boolean

Repeat source combo traits with TF-IDF and boolean weighting.

Hypothesis: source reports may benefit from TF-IDF more than ELF because common
benign code traits are widespread.

### S05: Suspicious+ Source Traits

Use only suspicious+ and hostile source traits.

Hypothesis: source has too many benign/notable code-quality findings. Filtering
to suspicious+ may improve zero-FP recall.

### S06: Source Symbols/Strings As Primary

Train symbols/strings without combo traits, and then with combo traits. Test log
counts, TF-IDF, and top-k 10k/25k/50k.

Hypothesis: source malware intent may appear more in identifiers, URLs, shell
snippets, imports, and package names than in generic findings.

### S07: String Char-Grams

Add character n-grams over source strings/symbols, length 3 through 8, using
feature hashing or selected vocab.

Hypothesis: source indicators mutate names and paths; char-grams should
generalize better than whole tokens.

### S08: Source Metrics Bins

Discretize source/code metrics into quantile bins and add missingness.

Hypothesis: raw metric magnitudes are too noisy across languages, while binned
complexity, entropy, density, and string statistics may be stable.

### S09: Top-Risk File Traits

Extract traits only from the highest-risk file, top 3 files, and top 5 files.

Hypothesis: source packages may contain many benign helper files; all-file
aggregation dilutes the malicious file.

### S10: Hard-Negative Source Curriculum

Upweight benign source rows near the current source threshold and malware below
the current source threshold.

Hypothesis: the zero-FP frontier is dominated by a small benign tail and missed
malware cluster.

### S11: Label-Confidence Inclusion

Include lower-score source rows with score-derived weights, not as equal labels.

Hypothesis: source has many low-score benign rows and weaker malware labels;
soft weighting can improve calibration without poisoning the boundary.

### S12: Source Stacked Ensemble

Train independent scorers: combo traits, symbols/strings, metrics bins, C-only,
Go-only, and hard-negative model. Stack with logistic regression or small
LightGBM using out-of-fold predictions.

Hypothesis: source has several weak views rather than one dominant feature
family. A score-level ensemble may beat appending all columns to one model.

## 2026-05-02: Full-Corpus Source Filegroup Baseline

Command:

```sh
.venv/bin/python scripts/azoth_specialist_suite.py \
  --db postgres://hopper@localhost:5432/hopper \
  --output-root out/models/azoth-source-full-corpus \
  --summary out/models/azoth-source-full-corpus/specialists.json \
  --general-dir out/models/azoth/general \
  --workers 64 \
  --only source \
  --no-filegroup-score-filter
```

Result:

| Model | Train rows | Malware | Benign | Bench rows | AUC | AP | Max F1 | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| deployed `filegroups/source` score-filtered | 10,578 | 3,532 | 7,046 | 88,277 | 0.9203 | 0.6229 | 0.6615 | keep |
| `azoth-source-full-corpus` | 622,878 | 8,204 | 614,674 | 89,503 | 0.9051 | 0.3905 | 0.5225 | reject |

Notes:

- Removing the filegroup score filter adds a huge benign majority without
  enough additional malware signal.
- The model early-stopped almost immediately and reached only 45.4% holdout
  recall at 145 FP on 30,734 benign files.
- Do not promote full-corpus source training as a replacement for the current
  source filegroup model.
- Next source experiments should not just add more low-score benign data. Use
  targeted views: suspicious+ traits, top-risk files, source strings/symbols,
  language-specific C/Go specialists, or hard-negative weighting.
