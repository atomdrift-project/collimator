# Confirm FAIL — 06d7878d1640d9d5 on `general`

Cycle `20260601T215004-confirm-06d7878d1640d9d5` — 2026-06-01T21:50:04Z

experiment failed: timed out after 30m0s (timeout(1) exit 124)
--- experiment log tail ---
COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE=0 \
COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES=0 \
COLLIMATOR_TIERED_BIGRAM_BRANCH_MIN_CRIT= \
COLLIMATOR_EXPERIMENT_TAG=_general_scoreless_symbol_kv_textenc_replay_replay_confirm_seedsearch_3 \
.venv/bin/python -u -m collimator experiment --db postgres://hopper@localhost:5432/hopper --output out/experiments/azoth --model-name azoth --learner azoth --workers 128 --seed 43 \
	--experiment-idea general_scoreless_symbol_kv_textenc_replay_replay_confirm_seedsearch_3 --route general  \
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
	--beta 1.25 --threshold-mode fbeta \
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
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_general_scoreless_symbol_kv_textenc_replay_replay_confirm_seedsearch_3.log"
17:50:05 INFO  collimator.experiment: using cached experiment snapshot: max_id=1636831170
17:50:05 INFO  collimator.experiment: dataset snapshot: max_id=1636831170
17:50:36 INFO  collimator.experiment: cached corpus selections: out/cache/experiment/azoth/corpus_49325c72621c5ae7.json

EXPERIMENT
============================================================
Sampled train: 1941983 (1523028 malware, 418955 benign)
External test: 319277 (250278 malware, 68999 benign)
17:50:37 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
18:14:22 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
18:14:41 INFO  collimator.features: extended metrics: 271 keys from 5000 scanned rows
18:14:58 INFO  collimator.features: crit-category n-grams: 64 unigrams, 485 bigrams, 499 trigrams from 5000 scanned rows
18:15:15 INFO  collimator.features: ATT&CK/MBC n-grams: 279/500 atk bi/tri, 357/500 mbc bi/tri from 5000 scanned rows
18:15:15 INFO  collimator.features: vocab: 1465 paths, 88 filetypes, 29529 elements, 5000 bigrams, 2 ghosts, 271 ext_metrics -> 76288 features
18:15:17 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
make[2]: *** [Makefile:1573: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-01T21-50-04_20260601T215004-confirm-06d7878d1640d9d5_general_scoreless_symbol_kv_textenc_replay_replay_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `06d7878d1640d9d5` | `` |
| PR AUC | 0.9999 | 0.0000 |
| ROC AUC | 0.9999 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
