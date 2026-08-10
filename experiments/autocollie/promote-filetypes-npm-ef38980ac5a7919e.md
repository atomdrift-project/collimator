# Promote PASS — `ef38980ac5a7919e` on `filetypes/npm`

Generated 2026-08-05T00:33:50Z

full-train holds — PR_AUC 0.9642 -> 0.9657, AUC 0.9624 -> 0.9641, Brier 0.0676 -> 0.0698

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9642)
- **Full-train** (inflated profile, original seed): **PASS** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `ef38980ac5a7919e` | `0f2567fc35dae527` | `a2e62ec2456184ac` |
| PR AUC | 0.9642 | 0.9664 | 0.9657 |
| ROC AUC | 0.9624 | 0.9647 | 0.9641 |
| F1 | 0.9073 | 0.9114 | 0.9078 |

## Status: candidate bundle is built; litmus validation skipped

Autocollie ran the research and bundle gates below, but intentionally skipped litmus runtime compatibility (`AZOTH_SKIP_LITMUS_VALIDATE=1`) so undeployable feature ideas can prove whether they are worth runtime work:

- `azoth-calibrate` regenerated the score table and per-route policies with the candidate's model in place.
- `azoth_route_policy_search.py` chose the best routing per route.
- `azoth_policy_global_metrics.py --fail-on-budget` confirmed the global FP/M budget is *not* busted.
- `validate_azoth_bundle.py` confirmed the bundle layout is well-formed.
- Litmus parity was not run. Before deployment, run full validation without the skip flag or use `make azoth-deploy`, which still runs litmus checks.

The candidate bundle lives at:

```
/home/t/collimator/out/models/azoth-candidate-filetypes-npm-ef38980ac5a7919e
```

## Candidate knobs (raw EXP_* form)

```
EXP_AIR_GAP_SIGNAL=1
EXP_ALLOWED_FEATURES_FILE=/home/t/collimator/src/collimator/data/azoth_allowed_features_importance10k.json
EXP_ATTACK_CODE_NGRAMS=1
EXP_ATTACK_FEATURES=1
EXP_ATTACK_NGRAMS=0
EXP_BETA=1.25
EXP_BIGRAM_MAX=5000
EXP_BIGRAM_MIN_FREQ=1000
EXP_BLINDFOLD=1
EXP_CONFIDENCE_WEIGHTED_NGRAMS=0
EXP_CRIT_CATEGORY_NGRAMS=1
EXP_DISABLE_FEATURE_GROUPS=clusters,kv,symbols,textenc
EXP_DOCUMENT_OBFUSCATION_FEATURES=0
EXP_EMBER_LITE_FEATURES=0
EXP_ESTIMATORS=400
EXP_EXTENDED_METRICS=1
EXP_EXTREME_FEATURES=1
EXP_FILETYPE_INTERACTIONS=0
EXP_FILE_SEVERITY_DISTRIBUTION=1
EXP_FORMAT_HINTS=0
EXP_HARD_NEGATIVE_FRACTION=0.2
EXP_HARD_NEGATIVE_WEIGHT=5
EXP_HOSTILE_ESCALATION_FEATURES=1
EXP_HOSTILE_WEIGHTED_DENSITY=1
EXP_KV_MIN_FREQ=5
EXP_KV_SHAPE_FEATURES=0
EXP_KV_VALUE_SPLIT=0
EXP_KV_VOCAB=0
EXP_KV_VOCAB_MAX=5000
EXP_LEARNING_RATE=0.05
EXP_LINE_LENGTH_BUCKETS=0
EXP_MAX_DEPTH=12
EXP_MAX_TEST_SAMPLES=80000
EXP_MBC_ID_VOCAB=0
EXP_METRIC_MIN_FREQ_PCT=5
EXP_METRIC_RATIO_FEATURES=0
EXP_MIN_CHILD_SAMPLES=100
EXP_MIN_SAMPLE_SCORE=3
EXP_MTIME_KURTOSIS=0
EXP_NGRAM_MIN_CRIT=0
EXP_NGRAM_PATH_DEPTH=0
EXP_NONSTANDARD_SECTION_SIGNAL=0
EXP_NUM_LEAVES=96
EXP_NUM_THREADS=8
EXP_OBJECTIVE_TRIGRAMS=0
EXP_OVERLAY_SIGNAL=0
EXP_PACKAGED_CAPABILITY_MODE=paths
EXP_PE_FORMAT_FLAGS=0
EXP_PE_TEMPORAL_ANOMALY=0
EXP_REG_ALPHA=0
EXP_REG_LAMBDA=1
EXP_REPETITION_PENALTY_FEATURES=1
EXP_SCORE_WEIGHTED_TRAITS=1
EXP_SEVERITY_FRACTION_FEATURES=0
EXP_SILENT_PACKER_SIGNAL=0
EXP_SIZE_NORMALIZED_METRICS=0
EXP_SOFT_PRESENCE=1
EXP_STRUCT_FILE_RISK_COVERAGE=1
EXP_SUSPICIOUS_BREADTH_DENSITY=1
EXP_SUSPICIOUS_TRIGRAMS=0
EXP_SYMBOL_BIGRAMS=0
EXP_SYMBOL_BIGRAM_MAX=5000
EXP_SYMBOL_MIN_FREQ=5
EXP_SYMBOL_MIN_FREQ_BIGRAM=10
EXP_SYMBOL_MIN_FREQ_TRIGRAM=10
EXP_SYMBOL_TRIGRAMS=0
EXP_SYMBOL_TRIGRAM_MAX=2000
EXP_SYMBOL_VOCAB=0
EXP_SYMBOL_VOCAB_MAX=5000
EXP_TAXONOMY_FEATURES=0
EXP_TEXT_ENCODING_FEATURES=0
EXP_TEXT_METRICS_FULL=0
EXP_TIERED_BIGRAM_MAX=5000
EXP_TIERED_BIGRAM_MIN_CRIT=3
EXP_TIERED_BIGRAM_MIN_FREQ=5
EXP_TIERED_BIGRAM_PATH_DEPTH=3
EXP_TIERED_CRIT_BIGRAMS=1
EXP_TIERED_CRIT_QUADGRAMS=0
EXP_TIERED_CRIT_TRIGRAMS=0
EXP_TIERED_QUADGRAM_MAX=5000
EXP_TIERED_QUADGRAM_MIN_CRIT=3
EXP_TIERED_QUADGRAM_MIN_FREQ=5
EXP_TIERED_QUADGRAM_PATH_DEPTH=3
EXP_TIERED_TRIGRAM_MAX=5000
EXP_TIERED_TRIGRAM_MIN_CRIT=3
EXP_TIERED_TRIGRAM_MIN_FREQ=5
EXP_TIERED_TRIGRAM_PATH_DEPTH=3
EXP_TOP_K_RISK_FILES=1
EXP_TOP_K_RISK_FILES_MIN_CRIT=0
EXP_TRAIN_SAMPLES=600000
EXP_TRAIT_CONFIDENCE_MOMENTS=0
EXP_TRAIT_ID_LEXICAL_DISTANCE=0
EXP_TRIGRAM_MAX=500
EXP_TRIGRAM_MAX_BENIGN_FRAC=0.01
EXP_TRIGRAM_MIN_FREQ=5
SEED=42
```

## To deploy (HUMAN)

Read `/home/t/collimator/out/models/azoth-candidate-filetypes-npm-ef38980ac5a7919e/global_policy_metrics.md` and `route_policies.md` first. If you're convinced, ship the candidate bundle:

```
make azoth-deploy AZOTH_ROOT=/home/t/collimator/out/models/azoth-candidate-filetypes-npm-ef38980ac5a7919e
```

The deploy target runs litmus compatibility checks. If this candidate uses runtime-incompatible features, deploy will fail until litmus support is added.
