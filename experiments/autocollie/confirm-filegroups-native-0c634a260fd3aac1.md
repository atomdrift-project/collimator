# Confirm FAIL — 0c634a260fd3aac1 on `filegroups/native`

Cycle `20260705T184915-confirm-0c634a260fd3aac1` — 2026-07-05T18:49:15Z

experiment failed: interrupted: context canceled
--- experiment log tail ---
COLLIMATOR_MBC_ID_VOCAB=0 \
COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS=0 \
COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE=0 \
COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES=0 \
COLLIMATOR_TIERED_BIGRAM_BRANCH_MIN_CRIT= \
COLLIMATOR_EXPERIMENT_TAG=_native_tiered_trigrams_hardneg_confirm_seedsearch_3 \
.venv/bin/python -u -m collimator experiment --db postgres://hopper@localhost:5432/hopper --output out/experiments/azoth --model-name azoth --learner azoth --workers 128 --seed 43 \
	--experiment-idea native_tiered_trigrams_hardneg_confirm_seedsearch_3 --route filegroups/native  \
	--train-samples 0 --max-test-samples 0 \
	--total-limit 0 \
	 \
	 \
	--n-folds 0 --holdout-fraction 0.12 \
	--n-estimators 300 --max-depth 12 \
	--learning-rate 0.05 --early-stopping-rounds 25 \
	--num-leaves 128 \
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
	--hard-negative-fraction 0.1 --hard-negative-weight 10 \
	--scale-pos-weight-mult 1 \
	--boosting-type gbdt \
	 \
	--seed-search-k 3 \
	--save-all-seeds \
	 \
	 \
	--cache-dir out/cache/experiment/azoth \
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_native_tiered_trigrams_hardneg_confirm_seedsearch_3.log"
14:49:15 INFO  collimator.experiment: using cached experiment snapshot: max_id=2086053706
14:49:15 INFO  collimator.experiment: dataset snapshot: max_id=2086053706
14:49:54 INFO  collimator.experiment: cached corpus selections: out/cache/experiment/azoth/corpus_4fa8e169708e1351.json

EXPERIMENT
============================================================
Sampled train: 1628719 (1168741 malware, 459978 benign)
External test: 270507 (194508 malware, 75999 benign)
14:49:55 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
15:21:56 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
15:22:04 INFO  collimator.features: tiered crit trigrams: 5000 vocab entries
15:22:47 INFO  collimator.features: extended metrics: 176 keys from 5000 scanned rows (always-keep below threshold: ast_depth_capped)
15:23:28 INFO  collimator.features: crit-category n-grams: 52 unigrams, 423 bigrams, 460 trigrams from 5000 scanned rows
make[1]: *** [Makefile:1913: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-07-05T18-49-15_20260705T184915-confirm-0c634a260fd3aac1_native_tiered_trigrams_hardneg_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `0c634a260fd3aac1` | `` |
| PR AUC | 0.9988 | 0.0000 |
| ROC AUC | 0.9988 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
