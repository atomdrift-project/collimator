# PE keyword experiment — 2026-10-31

The strongest confirmed PE configuration combines **5k class-aware description
words, 1k class-aware relative-ID words, and 1k frequency-selected context
words**, with minimum document support five. It improves recall at both
observed false-positive budgets and in both seed-pair checks. This is a
candidate for full-data validation, not a deployed model.

The operator subsequently adopted these settings as the shared PE training
defaults in `model-configs/filetypes/pe.json`. The next `make nightly` and
autocollie PE proposals inherit them; normal validation and publishing gates
remain in place. See [integration details](keyword-scan-compatibility.md#nightly-and-autocollie-status).

## Results

The study trained 41 search configurations with two seeds, then seven
prelocked confirmation arms with four seeds: 110 native models, plus two
parallel-execution replay controls. These are fresh models trained on a 10%
sample, not measurements of the deployed PE model.

| Configuration | Search recall, 0 FP / 1 FP | Confirmation recall, 0 FP / 1 FP |
|---|---:|---:|
| Baseline | 71.03% / 75.58% | 50.65% / 77.73% |
| Descriptions 5k MI + relative IDs 1k MI + context 1k frequency | 80.84% / 84.07% | **83.58% / 84.86%** |
| Descriptions 5k, balanced MI | 82.59% / 83.63% | 81.07% / 81.41% |
| Descriptions 1k, frequency | 80.81% / 82.82% | 81.66% / 82.04% |
| Relative IDs 1k, balanced MI | 73.17% / 80.89% | 77.42% / 80.56% |
| Context 1k, frequency | 71.14% / 73.23% | 62.17% / 80.24% |
| Context-available flag only | 75.30% / 75.50% | 58.28% / 79.94% |

The winning combination gains **32.93 percentage points at zero FP and 7.13
points at one FP** over the matched baseline. Its seed-pair confirmation
results are 84.30% / 84.86% (43/44) and 81.62% / 81.67% (45/46), versus
baseline's 55.77% / 77.74% and 44.41% / 77.89%. Counting each canonical group
once, using its highest report score, gives 83.54% / 84.82% versus baseline's
51.06% / 77.71% across 5,903 goodware and 34,097 malware groups.

The baseline's large zero-FP/one-FP gap shows sensitivity to its most
suspicious goodware file. Results are ranking diagnostics at observed FP
counts, not deployment thresholds or guarantees at a production FP/M target.
The confirmation sample has 5,916 goodware files; a larger route-policy
evaluation remains necessary before promotion. No tuning continued after
the finalist lock.

The 1k frequency-description model is a simpler alternative, with fewer
keyword sources and a much smaller input vocabulary. Its 81.66% / 82.04%
confirmation recall trails the combined model by 1.91 / 2.82 points.
Its shared layout has 4,593 columns versus 44,221 for the combined model,
whose supervised candidate columns are retained across seeds. Total native
model text sizes across four seeds are 10,952,004 and 11,991,389 bytes,
respectively. These are storage/layout measurements, not a runtime latency
benchmark.

Goodware-only vocabulary selection did not win. Description-only variants
at 1k/5k reached 72.99% / 80.64% and 66.85% / 77.41% during search; ID-only
variants reached 66.97% / 77.51% and 75.05% / 75.66%. Symmetric class-aware
selection retains benign-associated words while allowing malware-associated
words to compete too.

Larger caps did not consistently help. Frequency descriptions at 10k and
25k (17,630 actual words) produced byte-identical saved probabilities for
both seeds and the ensemble. Frequency relative IDs at 5k, 10k and 25k
(5,000 / 7,581 / 7,581 actual words) also produced identical probabilities.
These comparisons are recorded in `cap_equivalence.json`.

The combined model's context words have a separate vocabulary; they are not
pooled with descriptions or IDs. Full hierarchy and pooled full-ID/description
sources were screened but did not lead. The availability-only control is
weaker than the winner, although these comparisons do not isolate the
incremental value of context within the three-source combination: the
two-source combination was not a confirmation finalist.

## Benign-word evidence and verification

The winning model uses words common in goodware and uncommon in malware:

| Word | Source | Training goodware | Training malware | Splits across four models |
|---|---|---:|---:|---:|
| `guard` | Description | 11.47% | 3.10% | 160 |
| `range` | Description | 11.59% | 3.51% | 122 |
| `notifications` | Description | 10.18% | 1.27% | 62 |
| `brepro` | Description | 26.33% | 2.59% | 27 |

For `guard`, average SHAP contribution is −0.478 raw-margin units when
present and +0.025 when absent. The existing binary features can therefore
learn benign presence and suspicious absence without inverse columns.
These are associations and fitted-model contributions, not causal effects
or guarantees about every file. The audit averages four models over up to
100 deterministic training examples per presence state; details and more
words are in `goodware_words.json`.

The final verifier reproduced predictions from all 110 experiment models
exactly, rebuilt layouts and fit-local selector statistics, checked that
trees did not split on discarded columns, recomputed metrics, verified the
pre-confirmation lock hash/options, and checked cohort row/label alignment
and group separation. All nine focused tests pass; Python compilation and
whitespace checks pass. The separate two-model parallel replay also matched
native model files and predictions exactly.

## Protocol

This follows the Mach-O keyword search using the accepted `filetypes/pe`
configuration. Its base feature allowlist is preserved, and keyword columns
are appended explicitly by the research runner. The search itself changed no
accepted model settings; the later adoption is recorded above.

Training and development search use a deterministic 10% sample of canonical
groups. Confirmation is sampled from the remaining development groups with
a separate label-blind hash, capped at 40,000 groups. Related rows stay
together across these cohorts. Locked-test reports are unused.

Before selecting the confirmation sample, contradictory-label canonical
groups were excluded: 18 training groups (208 rows) and 34 groups from the
full development pool (1,123 rows). The exclusion manifest is retained.

| Cohort | Goodware | Malware | Canonical groups |
|---|---:|---:|---:|
| Training | 20,123 | 119,261 | 129,189 |
| Development search | 3,341 | 20,061 | 22,327 |
| Reserved confirmation | 5,916 | 36,287 | 40,000 |

All arms share one read-only snapshot and cached feature inputs. The initial
screen compares five sources (relative IDs, descriptions, full IDs, pooled
description/full IDs, and decoded context) with frequency and balanced-MI
selection. Context remains separate from pooled text. Refinement tests
vocabulary size, document support, a research-only goodware-direction filter,
and combinations of the strongest sources. A context-availability-only arm
checks whether collection coverage accounts for apparent context gains.

Preparation took 1,912 seconds. The base layout has 3,593 columns. Eligible
training words (support at least two) numbered 10,583 for relative IDs,
29,045 for descriptions, 11,128 for full IDs, 30,572 for pooled text, and
288,442 for context. Context was bounded to the 100,000 most frequent
candidates; its lowest retained document support was seven. This bounds
the search and does not establish an optimum over every observed word.

At support five, relative IDs have 7,581 words, descriptions 17,630, full IDs
8,026, and pooled text 18,915. All 100,000 retained context candidates meet
that support floor. Usable context appears in 9,927/20,123 training goodware
files (49.3%) and 43,509/119,261 malware files (36.5%).

Search uses 180-tree budgets with seeds 43/44. Finalists and their options are
locked before confirmation, which uses 400-tree budgets with seeds 43–46.
After the initial source screen, seed fits use two isolated spawned processes,
each retaining the same four training threads. A parallel baseline replay
reproduced both native model files and all saved probabilities byte-for-byte;
its separate artifacts are under `parallel-replay/` and `parallel_replay.json`.
The finalist lock includes baseline, the best three-source combination,
5k balanced-MI descriptions, 1k frequency descriptions, 1k balanced-MI
relative IDs, 1k frequency context, and the context-availability control.
The strongest frequency-only and multi-source alternatives were retained
alongside the two recall-budget leaders before confirmation was opened.
Other training settings follow the accepted PE configuration, including
row-stratified internal holdout and hard-negative refitting. Supervised
keyword selection excludes that internal holdout. Canonical duplicates may
share training/calibration cohorts under the inherited internal splitting
policy; the outer search and confirmation groups are disjoint from training.

## Reproduction

The historical runner filename is retained for compatibility. Select PE with
`--route pe`; its default artifact directory is
`out/experiments/keyword-pe-search/`.

```sh
.venv/bin/python scripts/keyword_macho_search.py prepare --route pe --confirmation-groups 40000 --exclude-label-conflicts
.venv/bin/python scripts/keyword_macho_search.py screen --route pe
.venv/bin/python scripts/keyword_macho_search.py refine --route pe
.venv/bin/python scripts/keyword_macho_search.py budgets --route pe
.venv/bin/python scripts/keyword_macho_search.py availability --route pe
.venv/bin/python scripts/keyword_macho_search.py lock --route pe
.venv/bin/python scripts/keyword_macho_search.py confirm --route pe
.venv/bin/python scripts/summarize_macho_keywords.py out/experiments/keyword-pe-search --audit-model best-sources-plus-context
```

Use a new `--output` directory for another study. The interrupted preliminary
extraction is retained under `keyword-pe-search-conflicts-incomplete`; it is
not part of the experiment. Saved native models, predictions, input hashes,
fit-local selector statistics, and the finalist lock support later auditing.

`recommended_options.json` records the exact source settings and training
configuration. It preserves the experiment's special allowlist handling:
accepted base features were retained and keyword columns appended. Replaying
the keyword flags against the original production allowlist alone would
discard the new columns. The adopted allowlist now permits enabled keyword
families while keeping the base-feature filter. Supervised vocabularies retain the bounded candidate
layout across seeds; the 5k/1k budgets describe words selected per fit, not
the full number of serialized candidate columns.
