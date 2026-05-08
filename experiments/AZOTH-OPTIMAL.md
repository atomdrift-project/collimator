# Azoth Detection Optimization Log

This log tracks the next optimization batch after adding default `tierbi:`
severity-prefixed notable+ trait bigrams.

## Queue

1. General corpus `tierbi:` A/B.
2. Scripts filegroup specialist retrain with `tierbi:`.
3. PE specialist tail-contrast experiment.
4. Source specialist `tierbi:` check.
5. Native group tail-contrast.
6. Per-route general escape search.
7. Score-only gate ablation.
8. Weak filetype full-corpus retrains.
9. Tiered trigram micro-test.
10. Specialist-primary with 0-FP general escape policy variant.

## 2026-05-02: General Corpus Tiered-Bigram A/B

Purpose: test whether the scripts-pool `tierbi:` win generalizes to the
sampled general corpus before spending full deployment training time.

Commands:

```sh
make experiment DB=postgres://hopper@localhost:5432/hopper MODEL=azoth-tierbi-general LEARNER=azoth WORKERS=64 EXP_WORKERS=64
make experiment DB=postgres://hopper@localhost:5432/hopper MODEL=azoth-no-tierbi-general LEARNER=azoth WORKERS=64 EXP_WORKERS=64 EXP_DISABLE_FEATURE_GROUPS=clusters,tiered_bigrams
```

Results:

| Model | Features | CV F1 | External Precision | External Recall | External F1 | ROC AUC | Avg Prec |
|---|---:|---:|---:|---:|---:|---:|---:|
| `azoth-tierbi-general` | 20,728 | 0.9878 | 0.9861 | 0.9915 | 0.9888 | 0.9991 | 0.9991 |
| `azoth-no-tierbi-general` | 15,704 | 0.9875 | 0.9841 | 0.9913 | 0.9876 | 0.9991 | 0.9991 |

Verdict: keep `tierbi:` enabled for the next full-corpus experiments. The A/B
is small but directionally useful: +0.0012 external F1 and +0.0020 precision at
roughly equal recall. The control still counted `tierbi:` vocab during scan
because the env flag was enabled, but the feature layout excluded it via
`EXP_DISABLE_FEATURE_GROUPS=clusters,tiered_bigrams`, so scoring was a real
off-vs-on comparison.

## 2026-05-02: Scripts Filegroup Tiered-Bigram Specialist

Purpose: retrain the scripts filegroup specialist against the `tierbi:` general
spec and compare its held-out filegroup metrics to the deployed/default
specialist.

Command:

```sh
make azoth-specialists DB=postgres://hopper@localhost:5432/hopper \
  AZOTH_ROOT=out/models/azoth-tierbi-specialists \
  AZOTH_GENERAL_DIR=out/models/azoth-tierbi-general \
  AZOTH_SPECIALIST_ONLY=scripts \
  AZOTH_SPECIALIST_SKIP_EXISTING=0 \
  WORKERS=64 EXP_WORKERS=64
```

Results:

| Model | Features | L0 hostile recall @ FP | L5 hostile recall @ FP | L9 hostile recall @ FP | L5 suspicious recall @ FP |
|---|---:|---:|---:|---:|---:|
| deployed `filegroups/scripts` | 37,595 | 85.83% @ 0 | 91.82% @ 1 | 91.82% @ 1 | 92.26% @ 3 |
| `tierbi` retrain | 20,728 | 84.30% @ 0 | 91.88% @ 1 | 91.88% @ 1 | 92.12% @ 3 |

Verdict: no meaningful specialist win. `tierbi:` improved the sampled general
corpus, but the scripts specialist is basically flat: tiny L5/L9 hostile gain,
slightly weaker L0 hostile and suspicious. Do not promote this specialist solely
on the local benchmark. Revisit only through route-policy/global ensemble
metrics.

## 2026-05-02: Mach-O Tail Contrast

Purpose: test a harder native binary filetype with the ELF tail-contrast route
framework. This replaces PE as the immediate binary target; PE can run next.

Command:

```sh
.venv/bin/python scripts/elf_ensemble_experiments.py \
  --db postgres://hopper@localhost:5432/hopper \
  --file-type macho \
  --general-scores out/models/azoth/general/threshold_scores.npz \
  --general-spec out/models/azoth/general/feature_spec.json \
  --teacher-model out/models/azoth/filetypes/macho/model.txt \
  --teacher-spec out/models/azoth/filetypes/macho/feature_spec.json \
  --output-dir out/models/azoth/macho_route_optimization \
  --output out/models/azoth/macho_route_optimization.json \
  --workers 64
```

Results:

| Candidate | Global L5 hostile recall @ FP | Mach-O-local best L5 hostile recall @ FP | Local F1 | Local accuracy |
|---|---:|---:|---:|---:|
| general baseline | 47.08% @ 9 | 45.29% @ 1 | 62.31% | 88.46% |
| deployed Mach-O teacher upper bound | 47.18% @ 9 | 45.29% @ 1 | 62.31% | 88.46% |
| `tail_contrast` | 47.27% @ 9 | 98.53% @ 1 | 99.22% | 99.67% |
| `teacher_distill` | 47.23% @ 9 | 70.37% @ 1 | 82.57% | 93.74% |
| `ranker` | 47.17% @ 9 | 57.64% @ 1 | 73.09% | 91.06% |

Verdict: strong local win, small global movement. `tail_contrast` is the clear
Mach-O candidate: it turns a weak Mach-O local route into a near-perfect one
under the local benchmark. The full-corpus L5 hostile number moves only
47.08% -> 47.27% because Mach-O has just 6,150 calibration rows in this score
table. Next step for deployment is route-policy calibration, not only local
promotion.

## 2026-05-03: PE Tail Contrast

Purpose: test whether the Mach-O/native `tail_contrast` result also holds for
PE, the largest native filetype pool.

Command:

```sh
.venv/bin/python scripts/elf_ensemble_experiments.py \
  --db postgres://hopper@localhost:5432/hopper \
  --file-type pe \
  --general-scores out/models/azoth/general/threshold_scores.npz \
  --general-spec out/models/azoth/general/feature_spec.json \
  --teacher-model out/models/azoth/filetypes/pe/model.txt \
  --teacher-spec out/models/azoth/filetypes/pe/feature_spec.json \
  --output-dir out/models/azoth/pe_route_optimization \
  --output out/models/azoth/pe_route_optimization.json \
  --workers 64
```

Rows: 423,309 calibration rows, 406,435 train rows.

Results:

| Candidate | Best global policy | Global L5 hostile recall @ FP | PE-local best policy | PE-local L5 hostile recall @ FP | Local F1 | Local accuracy |
|---|---|---:|---|---:|---:|---:|
| general baseline | general only | 47.08% @ 9 | general only | 43.17% @ 1 | 60.31% | 61.03% |
| deployed PE teacher upper bound | OR/acquittal | 48.33% @ 9 | specialist-primary | 49.02% @ 1 | 65.79% | 65.04% |
| `tail_contrast` | replacement | 69.23% @ 9 | specialist-primary | 78.80% @ 1 | 88.15% | 85.46% |
| `teacher_distill` | replacement | 62.87% @ 9 | general only | 43.17% @ 1 | 60.31% | 61.03% |
| `ranker` | OR/acquittal | 48.30% @ 9 | OR/general-primary | 46.58% @ 1 | 63.56% | 63.37% |

Verdict: promote `tail_contrast` as the PE candidate too. This independently
matches the native group result: PE L5 hostile recall rises 47.08% -> 69.23%
at the same 9-FP global cap under replacement semantics. OR helps but leaves
about 6 recall points behind because general false positives still consume
budget in the route.

## 2026-05-03: Tail Filetype Route Policy Search

Purpose: test calibrated per-file route selection with the winning
`tail_contrast` overrides for ELF, Mach-O, and PE.

Command:

```sh
.venv/bin/python scripts/azoth_route_policy_search.py \
  --db postgres://hopper@localhost:5432/hopper \
  --config out/models/azoth/config.json \
  --score-table out/models/azoth/score_table.npz \
  --output out/models/azoth/route_policies_tail_filetypes.json \
  --csv out/models/azoth/route_policies_tail_filetypes.csv \
  --markdown out/models/azoth/route_policies_tail_filetypes.md \
  --override-route filetypes/elf=out/models/azoth/elf_route_optimization/tail_contrast \
  --override-route filetypes/macho=out/models/azoth/macho_route_optimization/tail_contrast \
  --override-route filetypes/pe=out/models/azoth/pe_route_optimization/tail_contrast \
  --workers 64
```

Results:

| Route | Policy set | L5 hostile policy | L5 hostile recall @ FP | L9 hostile policy | L9 hostile recall @ FP |
|---|---|---|---:|---|---:|
| ELF | deployed | group-primary escape | 99.26% @ 1 | group-primary escape | 99.26% @ 1 |
| ELF | tail override | group-primary escape | 98.99% @ 1 | group-primary escape | 98.99% @ 1 |
| Mach-O | deployed | filetype only | 0.46% @ 0 | OR/general-primary | 35.42% @ 1 |
| Mach-O | tail override | no policy | 0.00% @ 0 | OR/general-primary | 98.30% @ 1 |
| PE | deployed | OR/general-primary | 43.18% @ 1 | OR/general-primary | 43.18% @ 1 |
| PE | tail override | specialist-primary escape | 77.73% @ 1 | specialist-primary escape | 77.73% @ 1 |

Verdict: policy search confirms the practical PE and Mach-O wins, but ELF
should keep the current deployed specialist for now. Mach-O loses L5 budget in
the global selector because its best high-recall route costs one FP and the
global L5 budget is already tight; at L9 it jumps 35.42% -> 98.30%. PE is the
clear immediate win. Important tooling caveat: `azoth_policy_global_metrics.py`
cannot evaluate this override policy from the original score table because the
table lacks the override score columns. Either persist an override score table
or teach the global metrics script to score overrides before using it for this
experiment.

## 2026-05-03: General Explicit Score-Feature Ablation

Purpose: test whether explicit `score:` and `inter:*score` features are helping
the general model, or whether the model can stand on raw taxonomy and structural
features alone.

Command:

```sh
make experiment DB=postgres://hopper@localhost:5432/hopper \
  MODEL=azoth-no-score-general \
  LEARNER=azoth \
  WORKERS=64 EXP_WORKERS=64 \
  EXP_DISABLE_FEATURE_GROUPS=clusters,score
```

Note: the Makefile still sets `COLLIMATOR_SCORE_WEIGHTED_TRAITS=1`, so this is
not a pure "no score anywhere" test. It removes the explicit score feature
group only.

Results:

| Model | Features | CV F1 | External Precision | External Recall | External F1 | ROC AUC | Avg Prec |
|---|---:|---:|---:|---:|---:|---:|---:|
| `azoth-tierbi-general` | 20,728 | 0.9878 | 0.9861 | 0.9915 | 0.9888 | 0.9991 | 0.9991 |
| `azoth-no-score-general` | 20,612 | 0.9875 | 0.9843 | 0.9922 | 0.9882 | 0.9991 | 0.9991 |

Verdict: keep explicit score features. They are not carrying the model, but the
A/B gives a small precision/F1 win at the same AUC/AP. Add a Makefile knob later
for a stricter test that also disables score-weighted trait extraction.

## 2026-05-03: Weak Filetype Specialist Retrains

Purpose: retrain weak filetype specialists against the current `tierbi:`
general spec and current database snapshot, starting with `pkg-info`, `data`,
and `xml`.

Command:

```sh
make azoth-specialists DB=postgres://hopper@localhost:5432/hopper \
  AZOTH_ROOT=out/models/azoth-weak-filetypes \
  AZOTH_GENERAL_DIR=out/models/azoth-tierbi-general \
  AZOTH_SPECIALIST_ONLY="pkg-info data xml" \
  AZOTH_SPECIALIST_SKIP_EXISTING=0 \
  WORKERS=64 EXP_WORKERS=64
```

Results:

| Filetype | Model | Train rows | Bench bad/good | AUC/AP/F1 | L5 hostile recall @ FP | L9 hostile recall @ FP | L5 suspicious recall @ FP |
|---|---|---:|---:|---:|---:|---:|---:|
| `pkg-info` | deployed | 3,850 | 441/83 | 1.0000/1.0000/1.0000 | 100.00% @ 1 | 100.00% @ 1 | 100.00% @ 1 |
| `pkg-info` | retrain | 3,879 | 441/88 | 1.0000/1.0000/1.0000 | 100.00% @ 1 | 100.00% @ 1 | 100.00% @ 1 |
| `data` | deployed | 7,718 | 43/1,108 | 0.9981/0.9744/0.9512 | 90.70% @ 1 | 90.70% @ 1 | 90.70% @ 1 |
| `data` | retrain | 7,742 | 43/1,110 | 0.9969/0.9670/0.9512 | 90.70% @ 1 | 90.70% @ 1 | 90.70% @ 1 |
| `xml` | deployed | 73,866 | 144/10,449 | 0.8995/0.1039/0.1894 | - | - | - |
| `xml` | retrain | 79,112 | 145/11,190 | 0.9063/0.0980/0.1844 | - | - | - |

Verdict: no promotion. `pkg-info` was already perfect on the benchmark; `data`
is flat at low-FP levels and slightly weaker on AUC/AP; `xml` remains a real
weak route and needs feature/model work rather than a simple retrain.

## 2026-05-03: Scripts N-Gram Depth/Criticality Sweep

Purpose: test multiple path depths, criticality filters, and n-gram sizes on a
scripts pool before adding heavier production features.

Command:

```sh
.venv/bin/python scripts/ngram_pool_sweep.py \
  --db postgres://hopper@localhost:5432/hopper \
  --pools scripts \
  --depths 2,3,4,0 \
  --crit-filters h,hs,hsn \
  --n-values 2,3,4,6,8 \
  --severity-prefix both \
  --max-per-label 8000 \
  --output out/experiments/ngram_pool_sweep_scripts_depth_crit.json \
  --markdown experiments/AZOTH-NGRAMS.md
```

Top variants by recall at 5 FP/M:

| Variant | Recall @ 5 FP/M | Recall @ 1000 FP/M | AUC | AP | F1 |
|---|---:|---:|---:|---:|---:|
| `scripts-d2-hs-2gram-tiered` | 54.51% | 82.89% | 0.9650 | 0.9680 | 0.9450 |
| `scripts-d3-hsn-3gram-tiered` | 52.60% | 87.58% | 0.9664 | 0.9695 | 0.9517 |
| `scripts-d4-hsn-3gram-tiered` | 52.60% | 87.58% | 0.9664 | 0.9695 | 0.9517 |
| `scripts-full-hsn-3gram-tiered` | 52.60% | 87.58% | 0.9664 | 0.9695 | 0.9517 |
| `scripts-d2-hsn-4gram-tiered` | 51.96% | 84.92% | 0.9649 | 0.9688 | 0.9494 |

Verdict: do not chase 6/8-grams for scripts yet. They are slower and weaker at
the hostile operating point. The best pure 5-FP/M result is tiered
hostile+suspicious bigrams at depth 2, but the better balanced production
candidate is tiered notable+ trigrams at depth 3: nearly the same 5-FP/M recall
with materially better F1 and 1000-FP/M recall. Next production experiment:
add a bounded `tiertri:` family using notable+ tokens, depth 3, and compare it
against current `tierbi:`.

## 2026-05-03: General `tiertri:` Production A/B

Purpose: promote the scripts sweep winner into the production feature pipeline:
bounded report-level severity-prefixed notable+ trigrams, depth 3, max 5,000
vocab entries.

Code changes:

- Added `tiertri:` feature extraction in `src/collimator/features.py`.
- Added `tiered_trigram_vocab` to `feature_spec.json`.
- Added matching `tiertri:` extraction support in `../litmus/src/features.rs`.
- Added Make knobs `EXP_TIERED_CRIT_TRIGRAMS` and `TRAIN_TIERED_CRIT_TRIGRAMS`.

Command:

```sh
make experiment DB=postgres://hopper@localhost:5432/hopper \
  MODEL=azoth-tiertri-general \
  LEARNER=azoth \
  WORKERS=64 EXP_WORKERS=64 \
  EXP_TIERED_CRIT_TRIGRAMS=1
```

Results:

| Model | Features | CV F1 | External Precision | External Recall | External F1 | ROC AUC | Avg Prec |
|---|---:|---:|---:|---:|---:|---:|---:|
| `azoth-tierbi-general` | 20,728 | 0.9878 | 0.9861 | 0.9915 | 0.9888 | 0.9991 | 0.9991 |
| `azoth-tiertri-general` | 25,667 | 0.9875 | 0.9871 | 0.9913 | 0.9892 | 0.9992 | 0.9992 |

Verification:

- Python compile passed for `src/collimator/features.py`.
- Python smoke test hit a `tiertri:` feature.
- `../litmus` `feature_spec` and `extraction_parity` tests passed.

Verdict: promote `tiertri:` to the next full training/deploy candidate. It adds
about 4,900 features over `tierbi:` and improves sampled external F1 by 0.0004,
precision by 0.0010, and AUC/AP by 0.0001. Small but clean. Do not flip default
deployment solely from this sampled run; run full `make train`/deploy
calibration with `TRAIN_TIERED_CRIT_TRIGRAMS=1` first.

## 2026-05-02: Source Filegroup Tiered-Bigram Specialist

Purpose: test whether `tierbi:` helps the weak source filegroup route.

Command:

```sh
make azoth-specialists DB=postgres://hopper@localhost:5432/hopper \
  AZOTH_ROOT=out/models/azoth-tierbi-specialists \
  AZOTH_GENERAL_DIR=out/models/azoth-tierbi-general \
  AZOTH_SPECIALIST_ONLY=source \
  AZOTH_SPECIALIST_SKIP_EXISTING=0 \
  WORKERS=64 EXP_WORKERS=64
```

Status: running.

Results:

| Model | Features | L0 hostile recall @ FP | L5 hostile recall @ FP | L9 hostile recall @ FP | L5 suspicious recall @ FP |
|---|---:|---:|---:|---:|---:|
| deployed `filegroups/source` | 37,595 | 45.41% @ 0 | 45.86% @ 1 | 45.86% @ 1 | 46.67% @ 4 |
| `tierbi` retrain | 20,728 | 42.74% @ 0 | 42.82% @ 1 | 42.82% @ 1 | 45.12% @ 4 |

Verdict: reject for source. The `tierbi:` general feature set helped the
sampled general corpus but weakened source local operating points.

## 2026-05-02: Native Group Tail Contrast

Purpose: test whether tail contrast helps the native group as a whole
(`elf,macho,pe`) rather than only individual filetypes.

Command:

```sh
.venv/bin/python scripts/elf_ensemble_experiments.py \
  --db postgres://hopper@localhost:5432/hopper \
  --file-type elf,macho,pe \
  --general-scores out/models/azoth/general/threshold_scores.npz \
  --general-spec out/models/azoth/general/feature_spec.json \
  --teacher-model out/models/azoth/filegroups/native/model.txt \
  --teacher-spec out/models/azoth/filegroups/native/feature_spec.json \
  --output-dir out/models/azoth/native_route_optimization \
  --output out/models/azoth/native_route_optimization.json \
  --workers 64
```

Rows: 540,392 calibration rows, 516,455 train rows.

Results:

| Candidate | Best global policy | Global L5 hostile recall @ FP | Native-local best policy | Native-local L5 hostile recall @ FP | Local F1 | Local accuracy |
|---|---|---:|---|---:|---:|---:|
| general baseline | general only | 47.08% @ 9 | general only | 42.54% @ 1 | 59.69% | 67.34% |
| deployed native teacher upper bound | replacement | 47.39% @ 9 | OR/general-primary | 43.46% @ 1 | 60.59% | 67.86% |
| `tail_contrast` | replacement | 71.50% @ 9 | specialist-primary | 78.50% @ 1 | 87.95% | 87.78% |
| `teacher_distill` | replacement | 61.27% @ 9 | general only | 42.54% @ 1 | 59.69% | 67.34% |
| `ranker` | OR/acquittal | 48.15% @ 9 | OR/general-primary | 44.98% @ 1 | 62.05% | 68.72% |

Verdict: promote `tail_contrast` as the next native-group route candidate.
This is the first experiment in this round that materially improves the
full-corpus native route: L5 hostile recall rises 47.08% -> 71.50% at the same
9-FP global cap when the native model is allowed to replace the general score
inside its route. This also supports route-specific decision policy rather than
one universal OR ensemble rule.

## 2026-05-04: Tail-Contrast Filetype Sweep and L3 Runtime Check

Purpose: try `tail_contrast` across every eligible filetype and test the best
models against the real route-policy runtime path after switching the default
policy to L3 (3 hostile FP/M, 32 suspicious FP/M).

Artifacts:

- Sweep: `experiments/AZOTH-TAIL-CONTRAST.md`
- Candidate bundle: `out/models/azoth-tail-promote-l3`

Top sweep results by raw L5 hostile recall:

| Filetype | Best rule | Raw L5 hostile recall @ FP | Local L5 best |
|---|---|---:|---:|
| `pe` | replacement | 70.19% @ 9 | 74.09% @ 1 |
| `javascript` | or | 55.06% @ 9 | 96.48% @ 1 |
| `elf` | or | 48.65% @ 9 | 99.57% @ 1 |
| `tar.gz` | replacement | 48.64% @ 9 | 96.05% @ 1 |
| `package.json` | or | 48.12% @ 9 | 99.90% @ 1 |
| `zip` | or | 48.10% @ 9 | 76.92% @ 1 |

Runtime promotion check:

| Bundle | L3 hostile | L3 suspicious | L5 hostile | L9 hostile |
|---|---:|---:|---:|---:|
| current `azoth` | 53.35% @ 5 FP | 64.95% @ 58 FP | 59.80% @ 9 FP | 60.80% @ 16 FP |
| tail candidate | 53.35% @ 5 FP | 64.96% @ 58 FP | 59.81% @ 9 FP | 60.80% @ 16 FP |

Verdict: reject promotion. The best tail models do improve raw calibration in
some routes, but the gains mostly disappear after route-policy search. Next
work should target policy search and specialist objectives, not blanket
tail-contrast promotion.

Next experiment set:

1. Policy-search coordinate descent over global recall, seeded from the raw
   calibration winners, to see whether the PE/native tail gains are being
   discarded by local route policy search.
2. Native-group tail candidate as a deployable filegroup replacement, tested
   alone and with current PE/ELF/Mach-O specialists.
3. PE specialist replacement-only policy with general high-confidence escape,
   because PE was the only filetype with a large raw global gain.
4. Archive family joint model (`zip`, `tar`, `tar.gz`, `gz`, `zst`, `jar`) with
   replacement policy, since package/archive routes repeatedly show local
   strength.
5. Script family joint model (`javascript`, `python`, `shell`, `php`,
   `powershell`, `vbs`) with hostile/suspicious/notable density and tiered
   n-grams.
6. Route-local hard-negative mining: train specialists on benign samples that
   become FPs under the current ensemble plus malware missed at L3.
7. Calibration-only experiment: keep models fixed, search per-route thresholds
   directly against global L3 hostile recall instead of route-local recall.
8. Monotonic score blending per route: fit a tiny logistic calibrator over
   `(general, group, filetype)` scores and calibrate it as a route score.
9. Filegroup-specific `tail_contrast` sweep for all groups, not just native.
10. Feature-family ablation per strong route (`pe`, `elf`, `javascript`,
    `zip`) to identify whether specialist gains are coming from n-grams,
    density features, taxonomy paths, or structural metadata.

## 2026-05-04: Python/JavaScript and Scripts-Group Improvement

Purpose: focus on Python and JavaScript route quality, then test whether the
scripts filegroup can improve both in a deployable way.

Artifacts:

- Focused log: `experiments/AZOTH-PYTHON-JAVASCRIPT.md`
- Python route candidate: `out/models/azoth/python_route_optimization`
- JavaScript route candidate: `out/models/azoth/javascript_route_optimization`
- Scripts route candidate: `out/models/azoth/scripts_route_optimization`
- Promoted candidate bundle: `out/models/azoth-scripts-tail-l3`

Route-local results:

| Route | Candidate | Full-corpus L5 hostile | Local L5 hostile | Local F1 |
|---|---|---:|---:|---:|
| `python` | current teacher | 47.12% @ 9 FP | 85.62% @ 1 FP | 92.25% |
| `python` | tail contrast | 47.50% @ 9 FP | 89.47% @ 1 FP | 94.44% |
| `javascript` | current teacher | 53.61% @ 9 FP | 86.88% @ 1 FP | 92.98% |
| `javascript` | tail contrast | 54.64% @ 9 FP | 92.99% @ 1 FP | 96.37% |
| `scripts` group | current teacher | 48.35% @ 9 FP | 80.36% @ 2 FP | 89.11% |
| `scripts` group | tail contrast | 55.00% @ 9 FP | 88.68% @ 2 FP | 94.00% |

Focused n-gram sweep:

- Python winner: plain depth-3 hsn bigrams, AUC 0.9499, AP 0.8843, F1 0.8902,
  recall at 5 FP/M 60.39%.
- JavaScript highest AP: plain depth-3 hsn bigrams, AUC 0.9770, AP 0.9751,
  F1 0.9650, recall at 5 FP/M 78.45%.
- JavaScript best strict-FP recall: tiered depth-2 hsn 4-grams, AUC 0.9748,
  AP 0.9738, F1 0.9640, recall at 5 FP/M 86.47%.

Deployment result after promoting scripts-group `tail_contrast`:

| Bundle | L0 hostile | L3 hostile | L3 suspicious | L5 hostile | L5 suspicious | L9 hostile | L9 suspicious |
|---|---:|---:|---:|---:|---:|---:|---:|
| previous azoth | 56.99% @ 0 FP | 53.35% @ 5 FP | 64.95% @ 58 FP | 59.80% @ 9 FP | 65.44% @ 86 FP | 60.80% @ 16 FP | 66.53% @ 137 FP |
| scripts-tail azoth | 58.32% @ 0 FP | 53.85% @ 5 FP | 65.65% @ 58 FP | 60.40% @ 9 FP | 66.11% @ 84 FP | 61.44% @ 16 FP | 67.09% @ 135 FP |

Verdict: promote and deploy. This is a modest but clean global win at every
hostile operating point, with suspicious also improving while staying inside
budget. The larger raw calibration lift was partially consumed by route-policy
selection, but enough survived the runtime path to be worth shipping.

Validation:

- `make deploy DB=postgres://hopper@localhost:5432/hopper EXP_WORKERS=64`
  completed.
- Staged `validate_azoth_bundle.py` passed.
- Staged litmus `scan_no_deadlock` passed.
- Installed litmus smoke scan on `/bin/ls` completed cleanly.

Next experiments:

1. Production hsn bigram feature for scripts with depth 3, plain severity
   handling, to target the Python result.
2. Production tiered hsn 4-gram feature for scripts with depth 2, to target the
   JavaScript strict-FP result.
3. Compare scripts-tail plus Python-tail and JavaScript-tail after rebuilding
   persisted score tables correctly; only promote if runtime metrics improve.

## 2026-05-04: PE Hard-Tail Promotion

Purpose: PE was the largest global miss source. The active PE route had strong
local AUC but poor strict-FP full-corpus recall, so we retrained PE with
two-pass hard-negative weighting.

Default training change:

- `make azoth-specialists` now applies `AZOTH_SPECIALIST_HARD_NEGATIVE_ROUTE`
  with default `pe=0.02,8.0`.
- This makes the promoted PE behavior reproducible without applying hard-tail
  weighting to every filetype.

Speed profile:

| Route | Rows | Features | Total | Fetch | Extract | Matrix | Predict |
|---|---:|---:|---:|---:|---:|---:|---:|
| active PE refresh | 423309 | 37595 | 520.1s | 0.6s | 518.4s | 0.4s | 0.3s |
| hard-tail PE refresh | 423309 | 49964 | 512.8s | 0.6s | 510.7s | 0.8s | 0.2s |

PE route result:

| Bundle | L5 hostile | L9 hostile | L5 suspicious | L9 suspicious |
|---|---:|---:|---:|---:|
| previous active | 48.15% @ 1 FP | 48.15% @ 1 FP | 54.35% @ 6 FP | 55.85% @ 10 FP |
| PE hard-tail | 55.07% @ 1 FP | 55.07% @ 1 FP | 78.80% @ 6 FP | 84.75% @ 10 FP |

Global result:

| Bundle | L3 hostile | L5 hostile | L9 hostile | L9 suspicious |
|---|---:|---:|---:|---:|
| previous active | 54.21% @ 5 FP | 60.65% @ 9 FP | 61.55% @ 16 FP | 67.40% @ 136 FP |
| PE hard-tail | 58.46% @ 5 FP | 64.90% @ 9 FP | 65.80% @ 16 FP | 85.16% @ 136 FP |

Verdict: promote. This is the largest single global improvement so far. PE
refresh is extraction-bound, so future PE experiment loops should persist the
route feature matrix or avoid full feature re-extraction where possible.

## 2026-05-04: PE Hard-Tail Narrower Tail

Purpose: compare the promoted PE hard-tail default (`0.02,8.0`) against a
narrower, stronger benign-tail weighting.

Candidate:

- `AZOTH_SPECIALIST_HARD_NEGATIVE_ROUTE=pe=0.01,12.0`
- Output: `out/models/azoth-pe-hardtail-hn01w12`

Result:

| Bundle | L5 hostile | L9 hostile | L5 suspicious | L9 suspicious |
|---|---:|---:|---:|---:|
| PE hard-tail `0.02,8.0` | 55.07% @ 1 FP | 55.07% @ 1 FP | 78.80% @ 6 FP | 84.75% @ 10 FP |
| PE hard-tail `0.01,12.0` | 67.29% @ 1 FP | 67.29% @ 1 FP | 77.71% @ 6 FP | 83.90% @ 10 FP |

Global result:

| Bundle | L3 hostile | L5 hostile | L9 hostile | L9 suspicious |
|---|---:|---:|---:|---:|
| PE hard-tail `0.02,8.0` | 58.46% @ 5 FP | 64.90% @ 9 FP | 65.80% @ 16 FP | 85.16% @ 136 FP |
| PE hard-tail `0.01,12.0` | 65.97% @ 5 FP | 72.41% @ 9 FP | 73.31% @ 16 FP | 84.63% @ 136 FP |

Verdict: promote `0.01,12.0`. It gives up a small amount of suspicious recall
but hostile detection is much stronger, and hostile is the primary deployment
objective.

## 2026-05-04: PE Hard-Tail Too-Narrow Tail

Purpose: test whether pushing farther along the narrower/heavier hard-negative
axis improves hostile recall again.

Candidate:

- `AZOTH_SPECIALIST_HARD_NEGATIVE_ROUTE=pe=0.005,16.0`
- Output: `out/models/azoth-pe-hardtail-hn005w16`

Result:

| Bundle | L5 hostile | L9 hostile | L5 suspicious | L9 suspicious |
|---|---:|---:|---:|---:|
| active PE `0.01,12.0` | 67.29% @ 1 FP | 67.29% @ 1 FP | 77.71% @ 6 FP | 83.90% @ 10 FP |
| PE `0.005,16.0` | 59.29% @ 1 FP | 59.29% @ 1 FP | 77.99% @ 6 FP | 83.90% @ 10 FP |

Global result:

| Bundle | L3 hostile | L5 hostile | L9 hostile | L9 suspicious |
|---|---:|---:|---:|---:|
| active PE `0.01,12.0` | 65.97% @ 5 FP | 72.41% @ 9 FP | 73.31% @ 16 FP | 84.63% @ 136 FP |
| PE `0.005,16.0` | 61.06% @ 5 FP | 67.50% @ 9 FP | 68.40% @ 16 FP | 84.63% @ 136 FP |

Verdict: reject. The tail is too narrow; it preserves suspicious but gives back
too much hostile recall.

## 2026-05-04: PE Hard-Tail Midpoint

Purpose: test a midpoint between the strong hostile default (`0.01,12.0`) and
the earlier broader tail (`0.02,8.0`) to see whether suspicious recall recovers
without losing hostile recall.

Candidate:

- `AZOTH_SPECIALIST_HARD_NEGATIVE_ROUTE=pe=0.015,10.0`
- Output: `out/models/azoth-pe-hardtail-hn015w10`

Result:

| Bundle | L5 hostile | L9 hostile | L5 suspicious | L9 suspicious |
|---|---:|---:|---:|---:|
| active PE `0.01,12.0` | 65.07% @ 1 FP | 65.07% @ 1 FP | 75.22% @ 6 FP | 75.93% @ 10 FP |
| PE `0.015,10.0` | 56.05% @ 1 FP | 56.05% @ 1 FP | 77.66% @ 6 FP | 79.52% @ 10 FP |

Global result:

| Bundle | L3 hostile | L5 hostile | L9 hostile | L9 suspicious |
|---|---:|---:|---:|---:|
| active PE `0.01,12.0` | 64.61% @ 5 FP | 71.05% @ 9 FP | 71.95% @ 16 FP | 79.72% @ 136 FP |
| PE `0.015,10.0` | 59.06% @ 5 FP | 65.50% @ 9 FP | 66.41% @ 16 FP | 81.93% @ 136 FP |

Correction: the first pass reported a tiny win because the overlay
`specialists.json` still pointed at the older `0.01,12.0` route. Calibration now
normalizes route paths to the bundle layout, so copied overlays score the model
actually present under `AZOTH_ROOT/filetypes/pe`.

Verdict: reject `0.015,10.0`. It improves suspicious recall, but loses too much
hostile recall, which is the primary objective.

## 2026-05-05: PE Route-Specific Tiered Trigrams

Purpose: test whether a PE-only feature vocabulary with deeper severity-prefixed
trait trigrams can raise the PE ceiling beyond the shared general spec.

Candidate:

- Hard negatives: `pe=0.015,10.0`
- Route-specific feature overrides:
  - `COLLIMATOR_TIERED_CRIT_TRIGRAMS=1`
  - `COLLIMATOR_TIERED_TRIGRAM_PATH_DEPTH=4`
  - `COLLIMATOR_TIERED_TRIGRAM_MIN_CRIT=3`
  - `COLLIMATOR_TIERED_TRIGRAM_MAX=20000`
  - `COLLIMATOR_TIERED_TRIGRAM_MIN_FREQ=5`
- Output: `out/models/azoth-pe-tiered-trigram-d4-hn015w10`

Holdout improved on the standalone model: AUC `0.9997`, F1 `0.9969`, recall
`99.80%`, 56,598 features. Calibration had to be rerun after fixing route path
normalization; otherwise copied overlays could silently score an older route.

Result:

| Bundle | L5 hostile | L9 hostile | L5 suspicious | L9 suspicious |
|---|---:|---:|---:|---:|
| active PE `0.01,12.0` | 65.07% @ 1 FP | 65.07% @ 1 FP | 75.22% @ 6 FP | 75.93% @ 10 FP |
| PE trigram d4 | 44.87% @ 1 FP | 44.87% @ 1 FP | 50.67% @ 6 FP | 55.13% @ 10 FP |

Global result:

| Bundle | L3 hostile | L5 hostile | L9 hostile | L9 suspicious |
|---|---:|---:|---:|---:|
| active PE `0.01,12.0` | 64.61% @ 5 FP | 71.05% @ 9 FP | 71.95% @ 16 FP | 79.72% @ 136 FP |
| PE trigram d4 | 52.19% @ 5 FP | 58.63% @ 9 FP | 59.54% @ 16 FP | 66.94% @ 136 FP |

Verdict: reject. Standalone holdout metrics were misleading here; the deeper
route-specific PE trigram vocabulary is much worse at the deployed low-FP
operating point.
