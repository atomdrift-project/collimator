# Confirm FAIL — da8e23431a535154 on `filegroups/native`

Cycle `20260613T024423-confirm-da8e23431a535154` — 2026-06-13T02:44:23Z

experiment failed: interrupted: context canceled
--- experiment log tail ---
COLLIMATOR_TIERED_QUADGRAM_PATH_DEPTH=3 \
COLLIMATOR_TIERED_QUADGRAM_MIN_CRIT=3 \
COLLIMATOR_TIERED_QUADGRAM_MAX=5000 \
COLLIMATOR_TIERED_QUADGRAM_MIN_FREQ=5 \
COLLIMATOR_MBC_ID_VOCAB=0 \
COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS=0 \
COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE=0 \
COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES=0 \
COLLIMATOR_TIERED_BIGRAM_BRANCH_MIN_CRIT= \
COLLIMATOR_EXPERIMENT_TAG=_inherit_from_filetypes_tar_1f9a08a6_confirm_seedsearch_3 \
.venv/bin/python -u -m collimator experiment --db postgres://hopper@localhost:5432/hopper --output out/experiments/azoth --model-name azoth --learner azoth --workers 128 --seed 43 \
	--experiment-idea inherit_from_filetypes_tar_1f9a08a6_confirm_seedsearch_3 --route filegroups/native  \
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
	--hard-negative-fraction 0.2 --hard-negative-weight 5 \
	--scale-pos-weight-mult 1 \
	--boosting-type gbdt \
	 \
	--seed-search-k 3 \
	--save-all-seeds \
	 \
	 \
	--cache-dir out/cache/experiment/azoth \
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_inherit_from_filetypes_tar_1f9a08a6_confirm_seedsearch_3.log"
22:44:24 INFO  collimator.experiment: using cached experiment snapshot: max_id=1705763368
22:44:24 INFO  collimator.experiment: dataset snapshot: max_id=1705763368
22:44:45 INFO  collimator.experiment: cached corpus selections: out/cache/experiment/azoth/corpus_e839e5b82b2ab3f7.json

EXPERIMENT
============================================================
Sampled train: 1427002 (1161053 malware, 265949 benign)
External test: 235393 (191639 malware, 43754 benign)
22:44:45 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
make[1]: *** [Makefile:1847: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-13T02-44-23_20260613T024423-confirm-da8e23431a535154_inherit_from_filetypes_tar_1f9a08a6_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `da8e23431a535154` | `` |
| PR AUC | 0.9994 | 0.0000 |
| ROC AUC | 0.9994 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
