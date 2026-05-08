# Azoth N-Gram Pool Sweep

- Timestamp: `2026-05-04T11:31:57.468237+00:00`
- Pools: `python, javascript`
- Depths: `[2, 3, 0]`
- Criticality filters: `['h', 'hs', 'hsn']`
- N sizes: `[2, 3, 4]`
- Severity-prefix modes: `both`

Criticality filters: `h` = hostile, `s` = suspicious exact, `n` = notable exact, `hs` = suspicious+hostile, `hsn` = notable+suspicious+hostile.

## python

| Rank | Variant | AUC | AP | F1 | R@0FP/M | R@5FP/M | R@50FP/M | R@1000FP/M | Test bad/good |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `python-d3-hsn-2gram-plain` | 0.9499 | 0.8843 | 0.8902 | 60.39% | 60.39% | 60.39% | 81.00% | 1853/10000 |
| 2 | `python-full-hsn-2gram-plain` | 0.9499 | 0.8843 | 0.8902 | 60.39% | 60.39% | 60.39% | 81.00% | 1853/10000 |
| 3 | `python-d3-hsn-2gram-tiered` | 0.9499 | 0.8840 | 0.8933 | 43.66% | 43.66% | 43.66% | 80.30% | 1853/10000 |
| 4 | `python-full-hsn-2gram-tiered` | 0.9499 | 0.8840 | 0.8933 | 43.66% | 43.66% | 43.66% | 80.30% | 1853/10000 |
| 5 | `python-d3-hsn-3gram-plain` | 0.9489 | 0.8828 | 0.8907 | 56.83% | 56.83% | 56.83% | 81.00% | 1853/10000 |
| 6 | `python-full-hsn-3gram-plain` | 0.9489 | 0.8828 | 0.8907 | 56.83% | 56.83% | 56.83% | 81.00% | 1853/10000 |
| 7 | `python-d3-hsn-3gram-tiered` | 0.9487 | 0.8824 | 0.8926 | 38.48% | 38.48% | 38.48% | 80.19% | 1853/10000 |
| 8 | `python-full-hsn-3gram-tiered` | 0.9487 | 0.8824 | 0.8926 | 38.48% | 38.48% | 38.48% | 80.19% | 1853/10000 |
| 9 | `python-d2-hsn-2gram-plain` | 0.9481 | 0.8814 | 0.8835 | 48.52% | 48.52% | 48.52% | 79.49% | 1853/10000 |
| 10 | `python-d2-hsn-2gram-tiered` | 0.9480 | 0.8807 | 0.8881 | 38.86% | 38.86% | 38.86% | 77.12% | 1853/10000 |
| 11 | `python-d2-hsn-3gram-plain` | 0.9416 | 0.8745 | 0.8815 | 45.82% | 45.82% | 45.82% | 78.63% | 1853/10000 |
| 12 | `python-d3-hsn-4gram-plain` | 0.9409 | 0.8738 | 0.8825 | 54.24% | 54.24% | 54.24% | 78.79% | 1853/10000 |
| 13 | `python-full-hsn-4gram-plain` | 0.9409 | 0.8738 | 0.8825 | 54.24% | 54.24% | 54.24% | 78.79% | 1853/10000 |
| 14 | `python-d2-hsn-4gram-plain` | 0.9403 | 0.8728 | 0.8806 | 44.79% | 44.79% | 44.79% | 78.52% | 1853/10000 |
| 15 | `python-d2-hsn-3gram-tiered` | 0.9407 | 0.8728 | 0.8818 | 36.81% | 36.81% | 36.81% | 73.61% | 1853/10000 |
| 16 | `python-d3-hsn-4gram-tiered` | 0.9406 | 0.8727 | 0.8843 | 36.16% | 36.16% | 36.16% | 77.44% | 1853/10000 |
| 17 | `python-full-hsn-4gram-tiered` | 0.9406 | 0.8727 | 0.8843 | 36.16% | 36.16% | 36.16% | 77.44% | 1853/10000 |
| 18 | `python-d2-hsn-4gram-tiered` | 0.9396 | 0.8713 | 0.8811 | 38.10% | 38.10% | 38.10% | 72.32% | 1853/10000 |
| 19 | `python-d2-hs-2gram-tiered` | 0.9354 | 0.8673 | 0.8850 | 54.78% | 54.78% | 54.78% | 76.04% | 1853/10000 |
| 20 | `python-d3-hs-3gram-tiered` | 0.9354 | 0.8673 | 0.8776 | 46.68% | 46.68% | 46.68% | 78.36% | 1853/10000 |

## javascript

| Rank | Variant | AUC | AP | F1 | R@0FP/M | R@5FP/M | R@50FP/M | R@1000FP/M | Test bad/good |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `javascript-d3-hsn-2gram-plain` | 0.9770 | 0.9751 | 0.9650 | 78.45% | 78.45% | 78.45% | 92.97% | 7198/10000 |
| 2 | `javascript-full-hsn-2gram-plain` | 0.9770 | 0.9751 | 0.9650 | 78.45% | 78.45% | 78.45% | 92.97% | 7198/10000 |
| 3 | `javascript-d3-hsn-2gram-tiered` | 0.9769 | 0.9751 | 0.9659 | 83.79% | 83.79% | 83.79% | 92.87% | 7198/10000 |
| 4 | `javascript-full-hsn-2gram-tiered` | 0.9769 | 0.9751 | 0.9659 | 83.79% | 83.79% | 83.79% | 92.87% | 7198/10000 |
| 5 | `javascript-d3-hsn-3gram-plain` | 0.9766 | 0.9750 | 0.9649 | 80.34% | 80.34% | 80.34% | 93.04% | 7198/10000 |
| 6 | `javascript-full-hsn-3gram-plain` | 0.9766 | 0.9750 | 0.9649 | 80.34% | 80.34% | 80.34% | 93.04% | 7198/10000 |
| 7 | `javascript-d2-hsn-2gram-plain` | 0.9765 | 0.9749 | 0.9637 | 74.08% | 74.08% | 74.08% | 91.96% | 7198/10000 |
| 8 | `javascript-d2-hsn-2gram-tiered` | 0.9764 | 0.9748 | 0.9638 | 85.76% | 85.76% | 85.76% | 91.41% | 7198/10000 |
| 9 | `javascript-d3-hsn-3gram-tiered` | 0.9763 | 0.9746 | 0.9658 | 83.66% | 83.66% | 83.66% | 92.50% | 7198/10000 |
| 10 | `javascript-full-hsn-3gram-tiered` | 0.9763 | 0.9746 | 0.9658 | 83.66% | 83.66% | 83.66% | 92.50% | 7198/10000 |
| 11 | `javascript-d3-hsn-4gram-tiered` | 0.9753 | 0.9740 | 0.9658 | 85.52% | 85.52% | 85.52% | 92.29% | 7198/10000 |
| 12 | `javascript-full-hsn-4gram-tiered` | 0.9753 | 0.9740 | 0.9658 | 85.52% | 85.52% | 85.52% | 92.29% | 7198/10000 |
| 13 | `javascript-d3-hsn-4gram-plain` | 0.9752 | 0.9738 | 0.9654 | 74.80% | 74.80% | 74.80% | 92.62% | 7198/10000 |
| 14 | `javascript-full-hsn-4gram-plain` | 0.9752 | 0.9738 | 0.9654 | 74.80% | 74.80% | 74.80% | 92.62% | 7198/10000 |
| 15 | `javascript-d2-hsn-4gram-plain` | 0.9749 | 0.9738 | 0.9633 | 80.26% | 80.26% | 80.26% | 89.01% | 7198/10000 |
| 16 | `javascript-d2-hsn-4gram-tiered` | 0.9748 | 0.9738 | 0.9640 | 86.47% | 86.47% | 86.47% | 90.80% | 7198/10000 |
| 17 | `javascript-d2-hsn-3gram-plain` | 0.9750 | 0.9737 | 0.9636 | 80.02% | 80.02% | 80.02% | 90.96% | 7198/10000 |
| 18 | `javascript-d2-hsn-3gram-tiered` | 0.9749 | 0.9737 | 0.9638 | 84.61% | 84.61% | 84.61% | 90.39% | 7198/10000 |
| 19 | `javascript-d3-hs-2gram-plain` | 0.9741 | 0.9727 | 0.9580 | 61.74% | 61.74% | 61.74% | 90.72% | 7198/10000 |
| 20 | `javascript-full-hs-2gram-plain` | 0.9741 | 0.9727 | 0.9580 | 61.74% | 61.74% | 61.74% | 90.72% | 7198/10000 |

## Route Experiments

Focused route optimization used the current azoth general scores and current
Python/JavaScript specialists as teachers.

| Route | Candidate | Full-corpus L5 hostile | Local L5 hostile | Local F1 | Verdict |
|---|---|---:|---:|---:|---|
| `python` | current teacher | 47.12% @ 9 FP | 85.62% @ 1 FP | 92.25% | baseline |
| `python` | tail contrast | 47.50% @ 9 FP | 89.47% @ 1 FP | 94.44% | useful local win, not enough alone |
| `javascript` | current teacher | 53.61% @ 9 FP | 86.88% @ 1 FP | 92.98% | baseline |
| `javascript` | tail contrast | 54.64% @ 9 FP | 92.99% @ 1 FP | 96.37% | strong local win, suspicious budget risk alone |
| `scripts` group | current teacher | 48.35% @ 9 FP | 80.36% @ 2 FP | 89.11% | baseline |
| `scripts` group | tail contrast | 55.00% @ 9 FP | 88.68% @ 2 FP | 94.00% | promoted |

The first deployability attempt using only route-policy overrides was invalid
for global metrics because the persisted score table still held the old route
scores. The corrected test rebuilt a candidate bundle with the scripts model
and matching feature spec under `out/models/azoth-scripts-tail-l3`, rewrote the
candidate `specialists.json` paths, refreshed scores, then ran the normal
policy search.

## Promotion

Promoted: scripts filegroup `tail_contrast`.

Runtime global metrics after promotion:

| Bundle | L0 hostile | L3 hostile | L3 suspicious | L5 hostile | L5 suspicious | L9 hostile | L9 suspicious |
|---|---:|---:|---:|---:|---:|---:|---:|
| previous azoth | 56.99% @ 0 FP | 53.35% @ 5 FP | 64.95% @ 58 FP | 59.80% @ 9 FP | 65.44% @ 86 FP | 60.80% @ 16 FP | 66.53% @ 137 FP |
| scripts-tail azoth | 58.32% @ 0 FP | 53.85% @ 5 FP | 65.65% @ 58 FP | 60.40% @ 9 FP | 66.11% @ 84 FP | 61.44% @ 16 FP | 67.09% @ 135 FP |

Deployed via:

```sh
make deploy DB=postgres://hopper@localhost:5432/hopper EXP_WORKERS=64
```

Validation:

- `validate_azoth_bundle.py` passed on the staged bundle.
- `../litmus` `scan_no_deadlock` passed against the staged bundle.
- Installed litmus smoke scan on `/bin/ls` completed cleanly.

Next: turn the n-gram sweep result into production features for scripts:
notable+suspicious+hostile path n-grams are consistently better than
hostile-only. For Python, start with plain depth-3 hsn bigrams. For
JavaScript, test tiered hsn 2/3/4-grams, with depth 2 and depth 3 as separate
production candidates.

## Ten Script Experiments

Ran ten broader script-detection ideas against four pools:

- `py_js`: `experiments/AZOTH-SCRIPT-DETECTION-PY-JS.md`
- `scripts`: `experiments/AZOTH-SCRIPT-DETECTION-SCRIPTS.md`
- `python`: `experiments/AZOTH-SCRIPT-DETECTION-PYTHON.md`
- `javascript`: `experiments/AZOTH-SCRIPT-DETECTION-JAVASCRIPT.md`

Best strict-FP candidates:

| Pool | Best R@1FP | R@1FP | R@5FP | Notes |
|---|---|---:|---:|---|
| `python` | `08_trait_sequence_sketch` | 69.29% | 79.44% | language-specific ordering helps most |
| `javascript` | `09_benign_framework_suppression` | 90.90% | 92.54% | good 0/1-FP behavior |
| `py_js` | `10_score_blender_general_scripts_filetype` | 85.08% | 87.68% | deployable only if calibrated as route policy, not as ad hoc score mixing |
| `scripts` | `10_score_blender_general_scripts_filetype` | 82.56% | 84.50% | strongest pooled result |

Promotable feature ideas:

- Python: trait sequence sketching, script-vocab unigram/bigram, benign-framework suppression.
- JavaScript: benign-framework suppression, joint-style hsn, density+hsn, trait sequence sketching.
- Scripts group: hard-tail weighting and score blending deserve a route-level calibration test.

Do not promote the score blender directly as a model feature yet. It is a
policy/stacking idea and must be calibrated on the full corpus route table or it
can lie about the FP budget.

## Deployable Route-Specific Script N-Grams

Added route-specific feature-spec support to `azoth_specialist_suite.py` and
trained Python/JavaScript specialists with deployable tiered notable+
bigrams+trigrams (`depth=3`, `max=10000` each).

Local specialist holdout:

| Route | Features | AUC | AP | F1 | Notes |
|---|---|---:|---:|---:|---|
| `filetypes/python` | route-specific tiered bi+tri | 0.9982 | 0.9957 | 0.9881 | strong local model |
| `filetypes/javascript` | route-specific tiered bi+tri | 0.9990 | 0.9964 | 0.9910 | strong local model |

Full routed overlay result:

| Bundle | L3 hostile | L5 hostile | L9 hostile | Verdict |
|---|---:|---:|---:|---|
| current azoth | 53.85% @ 5 FP | 60.40% @ 9 FP | 61.44% @ 16 FP | baseline |
| py/js route-specific ngrams | 53.85% @ 5 FP | 60.40% @ 9 FP | 61.44% @ 16 FP | no global win |

The local models are real, but the current route policy mostly spends script
budget through `filegroups/scripts` and `general`. The next deployable test is
therefore a route-specific `filegroups/scripts` model, not more individual
Python/JavaScript filetype work.

Calibration speed work:

- Route score caches now include model/spec hash and snapshot id.
- `AZOTH_REFRESH_ROUTE=filetypes/python` can refresh one route without forcing a
  full DB rescore.
- Cached route loading is effectively instant; cached global calibration dropped
  from roughly 23 minutes to about 8 minutes after bitset/candidate reuse.
- Legacy route caches without hashes are now refreshed when the route model or
  feature spec is newer than the cache, which prevents stale-cache reuse after
  swapping in a candidate route directory.

## Deployable Scripts Group N-Grams

Trained a route-specific `filegroups/scripts` model with tiered notable+
bigrams+trigrams (`depth=3`, `max=10000`) and no filegroup score filter.

Local holdout:

| Route | Samples | Features | AUC | AP | F1 |
|---|---:|---:|---:|---:|---:|
| `filegroups/scripts` | 549489 | 35994 | 0.9975 | 0.9920 | 0.9801 |

Full routed overlay result:

| Bundle | L3 hostile | L5 hostile | L9 hostile | Verdict |
|---|---:|---:|---:|---|
| current azoth | 53.85% @ 5 FP | 60.40% @ 9 FP | 61.44% @ 16 FP | baseline |
| scripts route-specific ngrams | 53.85% @ 5 FP | 60.40% @ 9 FP | 61.44% @ 16 FP | no global win |

Verdict: reject this promotion. The model is good locally but does not change
the global routed decision frontier. Next scripts work should change the
objective, not just add route-specific n-gram vocabulary.

## Deployable Scripts Hard-Tail N-Grams

Trained the same route-specific scripts n-gram model with two-pass hard-negative
weighting (`hard_negative_fraction=0.02`, `hard_negative_weight=8.0`).

Local holdout:

| Route | Features | AUC | AP | F1 | R@1FP | Notes |
|---|---:|---:|---:|---:|---:|---|
| `filegroups/scripts` | 35994 | 0.9986 | 0.9957 | 0.9843 | 89.96% | 1 FP in local test bucket |

Full routed overlay result:

| Bundle | L3 hostile | L5 hostile | L9 hostile | Verdict |
|---|---:|---:|---:|---|
| current azoth | 53.85% @ 5 FP | 60.40% @ 9 FP | 61.44% @ 16 FP | baseline |
| scripts hard-tail | 54.19% @ 5 FP | 60.63% @ 9 FP | 61.53% @ 16 FP | promote |

Suspicious also moved slightly upward: L3 65.65% -> 65.83%, L5 66.11% ->
66.35%, L9 67.09% -> 67.39%. L5/L9 suspicious spent one extra FP but stayed
within the full-corpus budget. This is a modest win, but it changes the routed
frontier rather than only local holdout metrics.
