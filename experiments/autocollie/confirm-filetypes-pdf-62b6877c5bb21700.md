# Confirm FAIL — 62b6877c5bb21700 on `filetypes/pdf`

Cycle `20260601T124420-confirm-62b6877c5bb21700` — 2026-06-01T12:44:20Z

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
COLLIMATOR_EXPERIMENT_TAG=_pdf_seed_search_k3_text_confirm_seedsearch_3 \
.venv/bin/python -u -m collimator experiment --db postgres://hopper@localhost:5432/hopper --output out/experiments/azoth --model-name azoth --learner azoth --workers 128 --seed 43 \
	--experiment-idea pdf_seed_search_k3_text_confirm_seedsearch_3 --route filetypes/pdf  \
	--train-samples 0 --max-test-samples 0 \
	--total-limit 0 \
	 \
	 \
	--n-folds 0 --holdout-fraction 0.12 \
	--n-estimators 300 --max-depth 12 \
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
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_pdf_seed_search_k3_text_confirm_seedsearch_3.log"
08:44:21 INFO  collimator.experiment: using cached experiment snapshot: max_id=1636831170
08:44:21 INFO  collimator.experiment: dataset snapshot: max_id=1636831170
08:44:21 INFO  collimator.experiment: loaded cached corpus: 102161 train, 16922 test from out/cache/experiment/azoth/corpus_9c2042bda194a190.json

EXPERIMENT
============================================================
Sampled train: 102161 (101086 malware, 1075 benign)
External test: 16922 (16768 malware, 154 benign)
08:44:21 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
make[2]: *** [Makefile:1573: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-01T12-44-20_20260601T124420-confirm-62b6877c5bb21700_pdf_seed_search_k3_text_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `62b6877c5bb21700` | `` |
| PR AUC | 1.0000 | 0.0000 |
| ROC AUC | 0.9993 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
