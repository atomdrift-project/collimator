# Confirm FAIL — 532c68e7c274c6e7 on `general`

Cycle `20260601T232007-confirm-532c68e7c274c6e7` — 2026-06-01T23:20:07Z

experiment failed: timed out after 30m0s (timeout(1) exit 124)
--- experiment log tail ---
COLLIMATOR_TIERED_QUADGRAM_MAX=5000 \
COLLIMATOR_TIERED_QUADGRAM_MIN_FREQ=5 \
COLLIMATOR_MBC_ID_VOCAB=0 \
COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS=0 \
COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE=0 \
COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES=0 \
COLLIMATOR_TIERED_BIGRAM_BRANCH_MIN_CRIT= \
COLLIMATOR_EXPERIMENT_TAG=_drift_retry_symbol_kv_vocab_full_train_confirm_seedsearch_3 \
.venv/bin/python -u -m collimator experiment --db postgres://hopper@localhost:5432/hopper --output out/experiments/azoth --model-name azoth --learner azoth --workers 128 --seed 43 \
	--experiment-idea drift_retry_symbol_kv_vocab_full_train_confirm_seedsearch_3 --route general  \
	--train-samples 0 --max-test-samples 0 \
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
	--min-malware-score 0 \
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
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_drift_retry_symbol_kv_vocab_full_train_confirm_seedsearch_3.log"
19:20:08 INFO  collimator.experiment: using cached experiment snapshot: max_id=1636831170
19:20:08 INFO  collimator.experiment: dataset snapshot: max_id=1636831170
19:20:13 INFO  collimator.experiment: loaded cached corpus: 1941983 train, 319277 test from out/cache/experiment/azoth/corpus_49325c72621c5ae7.json

EXPERIMENT
============================================================
Sampled train: 1941983 (1523028 malware, 418955 benign)
External test: 319277 (250278 malware, 68999 benign)
19:20:13 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
19:49:45 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
19:50:02 INFO  collimator.features: extended metrics: 271 keys from 5000 scanned rows
make[2]: *** [Makefile:1573: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-01T23-20-07_20260601T232007-confirm-532c68e7c274c6e7_drift_retry_symbol_kv_vocab_full_train_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `532c68e7c274c6e7` | `` |
| PR AUC | 0.9996 | 0.0000 |
| ROC AUC | 0.9996 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
