# Mach-O keyword experiment — 2026-10-31

No keyword configuration earned promotion. The best combination on the search
cohort lost to the matched baseline on reserved development data. Goodware-rich
words exist, and the trees learn their presence and absence, but restricting
selection to those words did not improve search performance.

The subsequent [expanded follow-up](macho-expanded-search.md) uses substantially
more fitting data and fresh evaluation groups. It confirms a zero-FP/one-FP
tradeoff for pooled text, rather than a general improvement; Mach-O defaults
remain unchanged.

## Protocol

The experiment used one read-only database snapshot, the accepted Mach-O base
feature settings, and deterministic 10% sampling by canonical group. Training,
search, and confirmation groups are disjoint; locked-test reports were unused.

| Cohort | Goodware | Malware |
|---|---:|---:|
| Sampled training | 2,531 | 197 |
| Development search, 10% of groups | 451 | 42 |
| Reserved development confirmation, remaining 90% | 4,256 | 334 |

The search covered **44 configurations with two seeds**, followed by **six
prelocked confirmation arms with four seeds**: 112 saved native models total.
Search used a 180-tree budget and seeds 43/44; confirmation used 400 trees and
seeds 43/44/45/46. Other training settings followed the accepted configuration,
including its internal holdout and hard-negative refitting. Tables report
averaged-probability ensembles, not averages of per-seed recall.

We tested relative IDs, descriptions, full IDs, pooled full IDs plus descriptions,
and decoded context. Context remained a separate feature family. The initial
screen compared frequency and balanced mutual-information selection at 1,000
words. Refinement focused on the strongest sources, pooled text and context:
caps from 250 to 25,000, document-support floors of 2/5/20, class-aware selection,
a research-only goodware-direction filter, and equal/asymmetric source budgets.
The 25k context cap selected only 14,380 eligible words at support five; the
10k pooled cap selected 3,111. Bigger requested caps need not add features.

Candidate discovery used training document frequency only, capped at 100,000
per source. Supervised selection and the goodware-direction filter ran on each
fit's training rows, excluding its internal holdout. The direction filter kept
words with greater smoothed prevalence in goodware, then applied balanced MI.
It is a research diagnostic, not a new autocollie parameter.

## Results

Recall at zero or one observed false positive is a ranking diagnostic; these
are not deployment thresholds or estimates of the deployed model's accuracy.

| Configuration | Search recall, 0 FP / 1 FP | Confirmation recall, 0 FP / 1 FP |
|---|---:|---:|
| Baseline | 69.05% / 73.81% | **56.29% / 56.89%** |
| Pooled 1k + context 1k | 71.43% / **80.95%** | 49.70% / 50.60% |
| Pooled 500 + context 500 | 71.43% / **80.95%** | 50.60% / 54.49% |
| Context 1k | 69.05% / 78.57% | 52.99% / 57.49% |
| Pooled full ID + description 1k | 71.43% / 76.19% | 47.31% / **58.08%** |
| Context-available flag only | 69.05% / 71.43% | 55.09% / 55.69% |

All keyword finalists used frequency selection and minimum support five. The
combined 1k-per-source model lost to baseline at both recall budgets in both
confirmation seed pairs. Pooled-only gained four detected malware examples at
one FP, but lost 30 at zero FP; context-only gained two and lost 11 respectively.
Neither is a convincing general improvement. The availability-only diagnostic
also failed to improve the baseline.

Goodware-only selection did not survive the search screen: pooled text at 1k
or 5k reached 69.05% / 71.43%; context at 1k reached 69.05% / 71.43%, and at 5k
66.67% / 73.81%. Balanced MI and larger vocabularies did not yield a stronger
search candidate. We did not continue tuning after opening confirmation.

## The model does learn benign evidence

Examples from training data, with split use counted across the four confirmation
models in the combined 1k-per-source arm:

| Word | Source | Goodware prevalence | Malware prevalence | Learned splits |
|---|---|---:|---:|---:|
| `stderrp` | Context | 25.56% | 2.54% | 31 |
| `vsnprintf` | Context | 15.65% | 3.55% | 3 |
| `options` | Context | 10.87% | 4.57% | 3 |
| `parsing` | Pooled text | 10.43% | 4.57% | 2 |

For `stderrp`, mean SHAP contribution was −0.164 raw-margin units when present
and +0.046 when absent. This verifies that the existing binary representation
can learn benign presence and suspicious absence without adding inverse
columns. The audit averages over four models and up to 100 deterministic
training examples per presence state. Contributions describe the fitted model;
they are not causal effects or guarantees about every sample.

Usable context was present in 82.3% of training goodware versus 39.6% of malware;
confirmation coverage was 82.2% versus 34.7%. This difference may reflect
collection or extraction coverage. It motivated the availability-only control
and saved context-present/context-absent subgroup metrics. Missing context is
not evidence that a binary intrinsically lacks a word.

## Limits and recommendation

Keep the accepted Mach-O configuration. These are fresh models trained on a
10% sample, with only 197 training malware examples. The accepted bigram support
floor of 1,000 exceeded that count, so ordinary malware-derived bigrams were
absent from the sampled vocabulary. Full-data training could behave differently.

The accepted allowlist was retained for base features, and keyword columns were
explicitly appended by this research runner. Simply replaying keyword flags
with the existing allowlist would discard those columns; these artifacts are
not production bundles. No accepted config, allowlist, or runtime was changed.

A future follow-up should use more training malware and a newly reserved
evaluation cohort, with the coverage issue addressed before tuning. Do not use
this confirmation cohort as another search set. The evidence does not justify
adding a permanent goodware-only selector or increasing default vocabulary caps.

## Reproduction and audit

Artifacts are under `out/experiments/keyword-macho-search/`: `inputs.json`,
`cohort.json`, cached matrices and tokens, `search.json`,
`locked_finalists.json`, `confirmation.json`, `verified_summary.json`,
`goodware_words.json`, and per-arm specs, models, and predictions. The lock
records exact options and a search-summary hash before confirmation evaluation.

For a fresh study, use a new output directory and run these actions in order:

```sh
.venv/bin/python scripts/keyword_macho_search.py prepare --output out/experiments/keyword-macho-new
.venv/bin/python scripts/keyword_macho_search.py screen --output out/experiments/keyword-macho-new
.venv/bin/python scripts/keyword_macho_search.py refine --output out/experiments/keyword-macho-new
.venv/bin/python scripts/keyword_macho_search.py budgets --output out/experiments/keyword-macho-new
.venv/bin/python scripts/keyword_macho_search.py availability --output out/experiments/keyword-macho-new
.venv/bin/python scripts/keyword_macho_search.py lock --output out/experiments/keyword-macho-new
.venv/bin/python scripts/keyword_macho_search.py confirm --output out/experiments/keyword-macho-new
```

Verify the completed study without database access:

```sh
.venv/bin/python scripts/summarize_macho_keywords.py out/experiments/keyword-macho-search
.venv/bin/python -m pytest tests/test_keyword_macho_search.py -q
```

The audit reproduced predictions from all 112 saved models exactly, rebuilt
feature layouts and fit-local selector statistics, checked matrix/code hashes,
verified that trees did not split on discarded columns, and recomputed reported
ensemble metrics. Four tests cover canonical sampling, fit-local direction
filtering/restoration, post-lock search refusal, and finalist selection.
