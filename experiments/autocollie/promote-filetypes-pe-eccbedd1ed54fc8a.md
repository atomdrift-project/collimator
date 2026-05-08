# Promote PASS — `eccbedd1ed54fc8a` on `filetypes/pe`

Generated 2026-05-08T05:05:08Z

full-train holds — F1 0.9974 -> 0.9985, AUC 0.9999 -> 0.9999, recall@FP=0 0.0000 -> 0.0000

## Gates

- **Confirm** (different seed, original profile): **PASS** — F1 held across 3 seeds (orig 0.9974)
- **Full-train** (inflated profile, original seed): **PASS** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `eccbedd1ed54fc8a` | `d3bef1d7e564670b` | `867771fd7c0deba2` |
| F1 | 0.9974 | 0.9966 | 0.9985 |
| ROC AUC | 0.9999 | 0.9999 | 0.9999 |
| AP | — | — | — |
| recall@3 FP/M (screen) | 0.6591 | 0.6012 | 0.7247 |
| recall@FP=0 (full-train) | — | — | — |
| recall@FP=5 (full-train) | — | — | — |

## Status: candidate bundle is built and validated

All gates that `make azoth-deploy` would run before copying have already run *against the candidate*:

- `azoth-calibrate` regenerated the score table and per-route policies with the candidate's model in place.
- `azoth_route_policy_search.py` chose the best routing per route.
- `azoth_policy_global_metrics.py --fail-on-budget` confirmed the global FP/M budget is *not* busted.
- `validate_azoth_bundle.py` confirmed the bundle layout is well-formed.
- Litmus parity (`scan_no_deadlock` + `verify_azoth_litmus_runtime.py`) confirmed the runtime can load and score the bundle.

The candidate bundle lives at:

```
/home/t/collimator/out/models/azoth-candidate-filetypes-pe-eccbedd1ed54fc8a
```

## Candidate knobs (raw EXP_* form)

```
EXP_AIR_GAP_SIGNAL=1
EXP_ATTACK_CODE_NGRAMS=1
EXP_ATTACK_FEATURES=1
EXP_ATTACK_NGRAMS=0
EXP_BETA=1.25
EXP_BIGRAM_MAX=5000
EXP_BIGRAM_MIN_FREQ=1000
EXP_BLINDFOLD=1
EXP_CONFIDENCE_WEIGHTED_NGRAMS=0
EXP_CRIT_CATEGORY_NGRAMS=1
EXP_DISABLE_FEATURE_GROUPS=clusters
EXP_EMBER_LITE_FEATURES=0
EXP_ESTIMATORS=400
EXP_EXTENDED_METRICS=1
EXP_EXTREME_FEATURES=1
EXP_FILETYPE_INTERACTIONS=0
EXP_FILE_SEVERITY_DISTRIBUTION=1
EXP_FORMAT_HINTS=0
EXP_HARD_NEGATIVE_FRACTION=0
EXP_HARD_NEGATIVE_WEIGHT=1
EXP_HOSTILE_ESCALATION_FEATURES=1
EXP_HOSTILE_WEIGHTED_DENSITY=1
EXP_KV_MIN_FREQ=5
EXP_KV_SHAPE_FEATURES=0
EXP_KV_VOCAB=0
EXP_KV_VOCAB_MAX=5000
EXP_LEARNING_RATE=0.05
EXP_MAX_DEPTH=12
EXP_MAX_TEST_SAMPLES=80000
EXP_METRIC_MIN_FREQ_PCT=5
EXP_MIN_CHILD_SAMPLES=100
EXP_MIN_SAMPLE_SCORE=3
EXP_MTIME_KURTOSIS=0
EXP_NGRAM_MIN_CRIT=0
EXP_NGRAM_PATH_DEPTH=0
EXP_NUM_LEAVES=96
EXP_OBJECTIVE_TRIGRAMS=0
EXP_PACKAGED_CAPABILITY_MODE=paths
EXP_REG_ALPHA=0
EXP_REG_LAMBDA=1
EXP_REPETITION_PENALTY_FEATURES=1
EXP_SCORE_WEIGHTED_TRAITS=1
EXP_SILENT_PACKER_SIGNAL=0
EXP_SOFT_PRESENCE=1
EXP_STRUCT_FILE_RISK_COVERAGE=1
EXP_SUSPICIOUS_BREADTH_DENSITY=1
EXP_SUSPICIOUS_TRIGRAMS=0
EXP_SYMBOL_MIN_FREQ=5
EXP_SYMBOL_VOCAB=0
EXP_SYMBOL_VOCAB_MAX=5000
EXP_TAXONOMY_FEATURES=0
EXP_TEXT_ENCODING_FEATURES=0
EXP_TIERED_BIGRAM_MAX=5000
EXP_TIERED_BIGRAM_MIN_CRIT=3
EXP_TIERED_BIGRAM_MIN_FREQ=5
EXP_TIERED_BIGRAM_PATH_DEPTH=3
EXP_TIERED_CRIT_BIGRAMS=1
EXP_TIERED_CRIT_TRIGRAMS=0
EXP_TIERED_TRIGRAM_MAX=5000
EXP_TIERED_TRIGRAM_MIN_CRIT=3
EXP_TIERED_TRIGRAM_MIN_FREQ=5
EXP_TIERED_TRIGRAM_PATH_DEPTH=3
EXP_TOP_K_RISK_FILES=1
EXP_TRAIN_SAMPLES=600000
EXP_TRIGRAM_MAX=500
EXP_TRIGRAM_MAX_BENIGN_FRAC=0.01
SEED=42
```

## To deploy (HUMAN)

Read `/home/t/collimator/out/models/azoth-candidate-filetypes-pe-eccbedd1ed54fc8a/global_policy_metrics.md` and `route_policies.md` first. If you're convinced, ship the validated bundle:

```
make azoth-deploy AZOTH_ROOT=/home/t/collimator/out/models/azoth-candidate-filetypes-pe-eccbedd1ed54fc8a
```

The deploy target re-runs the same gates and refuses to overwrite the production bundle if anything has regressed since validation, so this command is safe to run unattended once you've reviewed the metrics.
