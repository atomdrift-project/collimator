# Confirm FAIL — bf97bdeec463191a on `filetypes/pe`

Cycle `20260614T032757-confirm-bf97bdeec463191a` — 2026-06-14T03:27:57Z

experiment failed: timed out after 30m0s (timeout(1) exit 124)
--- experiment log tail ---
COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES=0 \
COLLIMATOR_TIERED_BIGRAM_BRANCH_MIN_CRIT= \
COLLIMATOR_EXPERIMENT_TAG=_pe_control_hardneg_fpr_target_confirm_seedsearch_3 \
.venv/bin/python -u -m collimator experiment --db postgres://hopper@localhost:5432/hopper --output out/experiments/azoth --model-name azoth --learner azoth --workers 128 --seed 43 \
	--experiment-idea pe_control_hardneg_fpr_target_confirm_seedsearch_3 --route filetypes/pe  \
	--train-samples 0 --max-test-samples 0 \
	--total-limit 0 \
	 \
	 \
	--n-folds 0 --holdout-fraction 0.12 \
	--n-estimators 250 --max-depth 12 \
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
	--beta 2 --threshold-mode max_recall_at_fpr \
	--threshold-fpr-target 5e-07 \
	--hard-negative-fraction 0.01 --hard-negative-weight 12 \
	--scale-pos-weight-mult 1 \
	--boosting-type gbdt \
	 \
	--seed-search-k 3 \
	--save-all-seeds \
	 \
	 \
	--cache-dir out/cache/experiment/azoth \
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_pe_control_hardneg_fpr_target_confirm_seedsearch_3.log"
23:27:58 INFO  collimator.experiment: using cached experiment snapshot: max_id=1716957660
23:27:58 INFO  collimator.experiment: dataset snapshot: max_id=1716957660
23:28:02 INFO  collimator.experiment: loaded cached corpus: 1146901 train, 189711 test from out/cache/experiment/azoth/corpus_4edd741b1ec37a66.json

EXPERIMENT
============================================================
Sampled train: 1146901 (1022614 malware, 124287 benign)
External test: 189711 (169315 malware, 20396 benign)
23:28:02 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
23:50:59 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
23:51:54 INFO  collimator.features: extended metrics: 176 keys from 5000 scanned rows (always-keep below threshold: ast_depth_capped)
23:52:49 INFO  collimator.features: crit-category n-grams: 52 unigrams, 371 bigrams, 439 trigrams from 5000 scanned rows
23:54:02 INFO  collimator.features: ATT&CK/MBC n-grams: 0/500 atk bi/tri, 37/500 mbc bi/tri from 5000 scanned rows
23:54:02 INFO  collimator.features: pruned feature spec: 59979 -> 7534 features
23:54:02 INFO  collimator.features: vocab: 1198 paths, 53 filetypes, 21049 elements, 5000 bigrams, 0 ghosts, 176 ext_metrics -> 7534 features
23:54:03 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
make[2]: *** [Makefile:1847: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-14T03-27-57_20260614T032757-confirm-bf97bdeec463191a_pe_control_hardneg_fpr_target_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `bf97bdeec463191a` | `` |
| PR AUC | 0.9988 | 0.0000 |
| ROC AUC | 0.9988 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
