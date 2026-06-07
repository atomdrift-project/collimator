# Confirm FAIL — 2a5ec7d1c8f5e124 on `filetypes/elf`

Cycle `20260607T031043-confirm-2a5ec7d1c8f5e124` — 2026-06-07T03:10:43Z

experiment failed: interrupted: context canceled
--- experiment log tail ---
COLLIMATOR_KV_VALUE_SPLIT=1 \
COLLIMATOR_SYMBOL_BIGRAMS=0 \
COLLIMATOR_SYMBOL_BIGRAM_MAX=5000 \
COLLIMATOR_SYMBOL_MIN_FREQ_BIGRAM=10 \
COLLIMATOR_SYMBOL_TRIGRAMS=0 \
COLLIMATOR_SYMBOL_TRIGRAM_MAX=2000 \
COLLIMATOR_SYMBOL_MIN_FREQ_TRIGRAM=10 \
COLLIMATOR_TRIGRAM_MIN_FREQ=5 \
COLLIMATOR_TIERED_CRIT_QUADGRAMS=0 \
COLLIMATOR_TIERED_QUADGRAM_PATH_DEPTH=3 \
COLLIMATOR_TIERED_QUADGRAM_MIN_CRIT=3 \
COLLIMATOR_TIERED_QUADGRAM_MAX=5000 \
COLLIMATOR_TIERED_QUADGRAM_MIN_FREQ=5 \
COLLIMATOR_MBC_ID_VOCAB=0 \
COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS=0 \
COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE=0 \
COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES=0 \
COLLIMATOR_TIERED_BIGRAM_BRANCH_MIN_CRIT= \
COLLIMATOR_EXPERIMENT_TAG=_elf_kv_vocab_split_confirm_seedsearch_3 \
.venv/bin/python -u -m collimator experiment --db postgres://hopper@localhost:5432/hopper --output out/experiments/azoth --model-name azoth --learner azoth --workers 128 --seed 43 \
	--experiment-idea elf_kv_vocab_split_confirm_seedsearch_3 --route filetypes/elf  \
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
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_elf_kv_vocab_split_confirm_seedsearch_3.log"
make[2]: *** [Makefile:1839: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-07T03-10-43_20260607T031043-confirm-2a5ec7d1c8f5e124_elf_kv_vocab_split_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `2a5ec7d1c8f5e124` | `` |
| PR AUC | 1.0000 | 0.0000 |
| ROC AUC | 1.0000 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
