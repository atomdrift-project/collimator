# Promote REJECTED — `9c5fc1291c9ef2d2` on `filetypes/pe`

Generated 2026-06-13T21:01:20Z

full-train failed: interrupted: context canceled
--- experiment log tail ---
COLLIMATOR_TIERED_QUADGRAM_MIN_FREQ=5 \
COLLIMATOR_MBC_ID_VOCAB=0 \
COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS=0 \
COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE=0 \
COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES=0 \
COLLIMATOR_TIERED_BIGRAM_BRANCH_MIN_CRIT= \
COLLIMATOR_EXPERIMENT_TAG=_pe_feat_symbol_vocab_bigrams_full_train \
.venv/bin/python -u -m collimator experiment --db postgres://hopper@localhost:5432/hopper --output out/experiments/azoth --model-name azoth --learner azoth --workers 128 --seed 42 \
	--experiment-idea pe_feat_symbol_vocab_bigrams_full_train --route filetypes/pe  \
	--train-samples 600000 --max-test-samples 80000 \
	--total-limit 0 \
	 \
	 \
	--n-folds 0 --holdout-fraction 0.12 \
	--n-estimators 400 --max-depth 12 \
	--learning-rate 0.05 --early-stopping-rounds 25 \
	--num-leaves 96 \
	--min-child-samples 100 \
	--min-child-weight 5 \
	--colsample-bytree 0.8 --subsample 0.8 \
	--gamma 0 --reg-alpha 0 --reg-lambda 1 \
	--device auto \
	 \
	 \
	--min-malware-score 4 \
	--beta 2 --threshold-mode fbeta \
	 \
	--hard-negative-fraction 0 --hard-negative-weight 1 \
	--scale-pos-weight-mult 1 \
	--boosting-type gbdt \
	 \
	--seed-search-k 3 \
	--save-all-seeds \
	 \
	 \
	--cache-dir out/cache/experiment/azoth \
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_pe_feat_symbol_vocab_bigrams_full_train.log"
16:53:18 INFO  collimator.experiment: using cached experiment snapshot: max_id=1713557833
16:53:18 INFO  collimator.experiment: dataset snapshot: max_id=1713557833
16:53:35 INFO  collimator.experiment: cached corpus selections: out/cache/experiment/azoth/corpus_335024ede696485b.json

EXPERIMENT
============================================================
Sampled train: 423041 (300000 malware, 123041 benign)
External test: 60216 (40000 malware, 20216 benign)
16:53:35 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
16:59:32 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
17:00:15 INFO  collimator.features: extended metrics: 165 keys from 5000 scanned rows (always-keep below threshold: ast_depth_capped)
17:00:56 INFO  collimator.features: crit-category n-grams: 52 unigrams, 371 bigrams, 438 trigrams from 5000 scanned rows
make[2]: *** [Makefile:1847: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-13T20-53-17_20260613T205317-promote-9c5fc1291c9ef2d2_pe_feat_symbol_vocab_bigrams_full_train.log

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9988)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `9c5fc1291c9ef2d2` | `4d05dfee07c188dd` | `—` |
| PR AUC | 0.9988 | 0.9999 | — |
| ROC AUC | 0.9989 | 0.9995 | — |
| F1 | 0.9841 | 0.9968 | — |

## Disposition

This spec did not survive the promotion ladder.

full-train failed: interrupted: context canceled
--- experiment log tail ---
COLLIMATOR_TIERED_QUADGRAM_MIN_FREQ=5 \
COLLIMATOR_MBC_ID_VOCAB=0 \
COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS=0 \
COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE=0 \
COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES=0 \
COLLIMATOR_TIERED_BIGRAM_BRANCH_MIN_CRIT= \
COLLIMATOR_EXPERIMENT_TAG=_pe_feat_symbol_vocab_bigrams_full_train \
.venv/bin/python -u -m collimator experiment --db postgres://hopper@localhost:5432/hopper --output out/experiments/azoth --model-name azoth --learner azoth --workers 128 --seed 42 \
	--experiment-idea pe_feat_symbol_vocab_bigrams_full_train --route filetypes/pe  \
	--train-samples 600000 --max-test-samples 80000 \
	--total-limit 0 \
	 \
	 \
	--n-folds 0 --holdout-fraction 0.12 \
	--n-estimators 400 --max-depth 12 \
	--learning-rate 0.05 --early-stopping-rounds 25 \
	--num-leaves 96 \
	--min-child-samples 100 \
	--min-child-weight 5 \
	--colsample-bytree 0.8 --subsample 0.8 \
	--gamma 0 --reg-alpha 0 --reg-lambda 1 \
	--device auto \
	 \
	 \
	--min-malware-score 4 \
	--beta 2 --threshold-mode fbeta \
	 \
	--hard-negative-fraction 0 --hard-negative-weight 1 \
	--scale-pos-weight-mult 1 \
	--boosting-type gbdt \
	 \
	--seed-search-k 3 \
	--save-all-seeds \
	 \
	 \
	--cache-dir out/cache/experiment/azoth \
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_pe_feat_symbol_vocab_bigrams_full_train.log"
16:53:18 INFO  collimator.experiment: using cached experiment snapshot: max_id=1713557833
16:53:18 INFO  collimator.experiment: dataset snapshot: max_id=1713557833
16:53:35 INFO  collimator.experiment: cached corpus selections: out/cache/experiment/azoth/corpus_335024ede696485b.json

EXPERIMENT
============================================================
Sampled train: 423041 (300000 malware, 123041 benign)
External test: 60216 (40000 malware, 20216 benign)
16:53:35 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
16:59:32 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
17:00:15 INFO  collimator.features: extended metrics: 165 keys from 5000 scanned rows (always-keep below threshold: ast_depth_capped)
17:00:56 INFO  collimator.features: crit-category n-grams: 52 unigrams, 371 bigrams, 438 trigrams from 5000 scanned rows
make[2]: *** [Makefile:1847: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-13T20-53-17_20260613T205317-promote-9c5fc1291c9ef2d2_pe_feat_symbol_vocab_bigrams_full_train.log
