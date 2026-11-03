# Expanded Mach-O follow-up — 2026-10-31

Keep the accepted Mach-O defaults. This follow-up expands the earlier
[10% keyword study](keyword-macho-search.md) and compares keyword sources,
smaller trees, ordinary-bigram support, class weighting, and hard-negative
weighting. Pooled description/full-ID keywords improve zero-FP recall, but
reduce one-FP recall in both confirmation seed pairs. No finalist preserves
both operating points, so no settings were adopted into nightly or autocollie.

## Fresh evaluation groups

The earlier study inspected the original development partition, including its
confirmation portion. This study therefore allocates fresh evaluation groups
from the original training partition. Original development and locked-test
rows are unused.

Every canonical group seen in the earlier study is excluded from both new
evaluation sets. Previously seen original-training groups remain eligible for
fitting. An independent, label-blind SHA-256 allocation assigns previously
unseen training groups 60% to fitting, 20% to search, and 20% to confirmation.
Canonical groups stay together, contradictory-label groups are excluded, and
the accepted score floor applies to fitting only. Vocabulary discovery and
feature extraction use the same read-only database snapshot.

| Cohort | Goodware | Malware |
|---|---:|---:|
| Fitting | 16,530 | 1,376 |
| Fresh search | 5,111 | 365 |
| Fresh confirmation | 5,140 | 375 |

This is an expanded fitting cohort, not training on 100% of available rows.
There are seven times as many fitting malware examples as in the earlier study.
The evaluation groups are fresh with respect to that study; these are neither
a temporal holdout nor a malware-family-disjoint benchmark.

## Search

Thirty configurations used two seeds (43/44) and a 220-tree budget. Four
finalists were locked before opening confirmation, then trained with four
seeds (43–46) and a 400-tree budget. Early stopping remains enabled. All arms
use matched fitting/evaluation rows and the accepted base-feature allowlist.
Supervised keyword selection excludes each fit's internal holdout.

The initial screen tested ordinary-bigram support floors 10/25/50/100/1000 and
four smaller or more regularized tree configurations. Source refinement tested
descriptions, pooled full ID plus description, separate context, pooled plus
context, the PE combination, balanced-MI pooled text, and a context-availability
diagnostic, against both the original trees and the strongest structural arm.
The final six checks paired the baseline and search-leading keyword arm with
half/quarter malware-class weight or disabled hard-negative weighting.

Frequency arms used 1,000 words per source and minimum document support five.
The PE combination used balanced-MI descriptions at 5,000, balanced-MI relative
IDs at 1,000, and frequency context at 1,000. Pooled text always combines full
rule ID and description; context remains separate.

Lowering the ordinary-bigram support floor added just two allowed bigrams,
with fitting-malware support 19 and 21. Neither affected predictions. The
allowlist is the limiting factor here; this experiment does not establish that
broader bigram features would be useless.

## Results

Recall at zero or one observed false positive is a ranking diagnostic, not a
deployment threshold or an estimate of production false-positive rates.

| Configuration | Search recall, 0 FP / 1 FP | Confirmation recall, 0 FP / 1 FP | Confirmation AP |
|---|---:|---:|---:|
| Accepted-settings baseline | 69.59% / 82.19% | 67.47% / **82.13%** | 0.97053 |
| Baseline, quarter malware-class multiplier | 70.14% / **85.48%** | 65.87% / 80.27% | **0.97178** |
| Smaller trees + pooled text, half malware-class multiplier | **76.16%** / 76.99% | 72.00% / 79.20% | 0.97126 |
| Smaller trees + pooled text | 75.07% / 81.37% | **74.93%** / 75.20% | 0.96914 |

The smaller-tree finalists use 31 leaves, depth eight, minimum child size 50,
and L2 regularization five. Other settings match the accepted configuration;
the multiplier scales the automatically calculated malware-class weight.
All four finalists retain ordinary-bigram support 1,000. Pooled text uses
frequency selection, cap 1,000, and support five.

Pooled text recovers 28 additional malware at zero FP, but loses 26 at one FP,
out of 375 confirmation malware. Halving its class multiplier recovers 17 at
zero FP and loses 11 at one FP. The smaller-tree baseline without keywords
was also screened, so the source comparison did not rely only on comparing
different tree configurations.

| Configuration | Confirmation seeds 43/44, 0 FP / 1 FP | Confirmation seeds 45/46, 0 FP / 1 FP |
|---|---:|---:|
| Baseline | 66.40% / 79.20% | 67.73% / 82.40% |
| Quarter malware-class multiplier | 68.27% / 80.80% | 62.13% / 78.13% |
| Pooled text, half malware-class multiplier | 70.93% / 77.07% | 72.80% / 80.53% |
| Pooled text | 76.53% / 76.53% | 73.87% / 74.13% |

The class-weight-only search win failed confirmation and changed direction
between seed pairs. Both keyword finalists consistently trade higher zero-FP
recall for lower one-FP recall. The slightly better AP of class weighting does
not establish a gain at the low-FP operating points. We stopped tuning after
opening confirmation.

The next useful experiment would relax or replace the ordinary-bigram
allowlist with a training-only, route-specific vocabulary, using a separately
planned evaluation protocol. Merely lowering its frequency floor does not
meaningfully expand the current feature space. The new confirmation groups
must not be reused as an untouched confirmation set for that experiment.

## Benign words are learned

The pooled-text/half-weight finalist learns both benign presence and suspicious
absence. Training prevalence and average raw-margin SHAP contributions are:

| Word | Goodware prevalence | Malware prevalence | Learned splits, four models | SHAP present / absent |
|---|---:|---:|---:|---:|
| `python` | 10.06% | 1.53% | 30 | −0.170 / +0.019 |
| `compilation` | 12.61% | 1.16% | 16 | −0.072 / +0.010 |
| `darwin` | 15.65% | 4.43% | 12 | −0.043 / +0.008 |

SHAP averages use up to 100 deterministic fitting examples per presence state
and average across four models. These describe model behavior, not causal or
unconditional word effects. For example, `libraries` is more common in goodware
but has a slightly positive mean contribution when present: marginal class
frequency does not determine a word's conditional effect in a tree ensemble.
Explicit inverse-presence columns are unnecessary for these learned effects.

## Context coverage

Usable context occurs in 81.9% of fitting goodware versus 39.2% of fitting
malware. Confirmation coverage is 82.6% versus 39.5%. Missing context can
reflect collection/extraction differences, rather than intrinsic absence of a
word. The availability-only arms are research diagnostics and cannot be
selected for deployment. Context-present and context-absent subgroup metrics
are saved in the verified summary.

## Reproduction

The saved study is under `out/experiments/macho-expanded-search/`. It includes
the cohort, frozen matrices/token banks, source manifests, three search plans,
native models, predictions, exact finalist configurations, search/runner
hashes, and confirmation results. Search actions refuse to run after locking;
confirmation rejects changes to the locked search or runner.

The audit rebuilt all layouts and reproduced all **76 native models'** saved
predictions exactly. It checked fit-local keyword selection, unused masked
columns, cohort separation, feature/matrix hashes, ensemble metrics, seed-pair
metrics, and context-coverage subgroups. All 13 focused helper tests passed.

All four finalists were exported to ONNX and checked through Scan's Rust
feature extraction and ensemble inference: **152 cases passed**, with maximum
probability error **1.19e-7**. Each bundle used 29 saved real PE/Mach-O reports
and nine synthetic cases. The fixture builder explicitly adapts archived input
schemas and standalone placement to current report semantics and records those
input changes; this is serving parity, not a replay of archival accuracy.
Fixtures and export audits are under `runtime-parity/` within the study root.

For another study, use a fresh output directory and run the actions in order:

```sh
for action in prepare screen refine tail lock confirm verify; do
  .venv/bin/python scripts/macho_followup.py "$action" \
    --output out/experiments/macho-expanded-new || break
done
```

Preparation requires the previous study's cohort manifest so that its groups
can be excluded. Saved-study verification requires no database access:

```sh
.venv/bin/python scripts/macho_followup.py verify
.venv/bin/python -m pytest tests/test_macho_followup.py tests/test_keyword_macho_search.py -q
```
