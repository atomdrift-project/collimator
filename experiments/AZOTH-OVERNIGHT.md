# Azoth Overnight Experiments

Created: 2026-05-05

Script:

```sh
scripts/run_azoth_overnight_experiments.sh
```

Purpose: run a broad, serial, content-addressed tranche of 48 azoth experiments
without stopping on individual failures. The tranche is intentionally heavier on
specialists than global changes.

Original oversized run defaults:

- `EXP_WORKERS=64`
- `EXP_TRAIN_SAMPLES=400000`
- `EXP_MAX_TEST_SAMPLES=100000`
- `EXP_FOLDS=0`
- `EXP_HOLDOUT_FRACTION=0.12`
- `EXP_MIN_SAMPLE_SCORE=3` for `general`
- `EXP_MIN_SAMPLE_SCORE=0` for `filegroups/*` and `filetypes/*`

Verdict on profile: too large for exploratory tranches. A single uncached
feature-space change took 36-73 minutes. Future bulk tranches should use the
standard probe profile from `experiments/README.md`, then confirm winners by
routed policy metrics, an explicit larger sample, or `make train`.

Routes covered:

- `general`: format, taxonomy, dense metrics, n-grams, hard negatives, larger trees.
- `filegroups/native`: binary-group format/metric/n-gram/hard-negative probes.
- `filetypes/pe`, `filetypes/macho`, `filetypes/elf`: hard binary specialist probes.
- `filegroups/scripts`, `filetypes/javascript`, `filetypes/python`, `filetypes/shell`: deep script n-grams, attack/objective trigrams, density and hard-tail tests.
- `filegroups/source`: semantic and formula/element-heavy source-code probes.
- `filegroups/archive`, `filegroups/portable`, `filegroups/config`, `filegroups/documents`, `filegroups/media`: broad non-native specialist probes.
- `filetypes/zip`, `filetypes/jar`, `filetypes/package.json`, `filetypes/pkg-info`, `filetypes/json`, `filetypes/pdf`, `filetypes/ole`, `filetypes/html`, `filetypes/svg`, `filetypes/apk`, `filetypes/msi`: filetype-specific weak-route probes.

Outcome log:

Stopped after 9/48 because the run profile was too large for bulk exploration.

Keep for confirmation:

- `general_clusters_back_on`: best global sampled-test result, but KMeans had
  overflow/convergence warnings and must not be promoted until numerically sane.
- `general_smooth_large`: clean global hyperparameter candidate.
- `native_kv_cross_binary`: best native filegroup candidate; simpler and better
  sampled F1/recall than `native_big_vocab_tail`.

Do not promote:

- `general_full_ngram_vocab`
- `general_tiered_deep_tri`
- `general_precision_hn_pe_js`
- `native_big_vocab_tail`

## Confirmation

### Native filegroup

Confirmed `native_kv_cross_binary` as a deployable filegroup recipe:

```sh
make azoth-specialists \
  AZOTH_ROOT=out/models/azoth-confirm-native \
  AZOTH_GENERAL_DIR=out/models/azoth/general \
  AZOTH_SPECIALISTS_SUMMARY=out/models/azoth-confirm-native/specialists.json \
  AZOTH_SPECIALIST_ONLY=native \
  AZOTH_SPECIALIST_SKIP_EXISTING=0 \
  AZOTH_SPECIALIST_FEATURE_ENV='native:COLLIMATOR_FORMAT_HINTS=1 native:COLLIMATOR_TAXONOMY_FEATURES=1 native:COLLIMATOR_EMBER_LITE_FEATURES=1' \
  EXP_WORKERS=64
```

Local route result:

- Rows: 541,780 train, 75,513 benchmark.
- Features: 39,115 route-specific.
- Benchmark AUC/AP/max-F1: 0.99995 / 0.99996 / 0.99840.

Route-policy override against the existing full score table:

| Policy | L3 hostile | L5 hostile | L9 hostile | L3 suspicious | L5 suspicious |
| --- | ---: | ---: | ---: | ---: | ---: |
| Current | 63.55% | 69.99% | 71.12% | 76.83% | 78.26% |
| Native candidate | 68.60% | 75.04% | 76.20% | 80.99% | 82.12% |

Verdict: promote the native route-specific feature env as the default native
filegroup recipe. This improves routed recall at the same global FP budgets.

Promoted the confirmed route-specific native artifact into `out/models/azoth`
and redeployed the ensemble. Recalibration refreshed the native score column
instead of reusing the old cache. Litmus needed runtime support for the native
route's `format:*`, taxonomy, and static aggregate features; after adding that,
`--extra` shows `az/native` scoring normally.

Updated full-corpus policy after promotion:

| L | H recall | H FP/1M | S recall | S FP/1M |
| ---: | ---: | ---: | ---: | ---: |
| 3 | 63.59% | 2.75 | 76.97% | 31.84 |
| 5 | 70.04% | 4.94 | 78.41% | 46.67 |
| 9 | 71.20% | 8.78 | 79.02% | 74.67 |

### General score-filter probe

Compared the general model recipe with and without the global sample-score
filter on the same pinned snapshot (`max_id=663343929`) and standard probe
profile (`150k` train, `40k` external test, `180` trees, seed `42`).

| Run | Min score | Features | External F1 | Precision | Recall | AUC | AP | Brier | Time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `score_filter3_probe` | 3 | 25,178 | 0.9913 | 0.9912 | 0.9913 | 0.9995 | 0.9995 | 0.0070 | 21.1m |
| `score_filter0_probe` | 0 | 24,526 | 0.9866 | 0.9925 | 0.9808 | 0.9985 | 0.9987 | 0.0102 | 17.6m |

Verdict: keep the current score-filtered general training pool for model
quality. It is a harder pool, but it produced materially better recall and F1
in this controlled probe. For public accuracy reporting, do not present only
the filtered evaluation: report full-corpus metrics separately, including the
low-score files that are treated as benign by the runtime score-filter path.
