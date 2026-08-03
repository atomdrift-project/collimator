# Promote REJECTED — `403b3d7c80635af8` on `filetypes/jar`

Generated 2026-08-03T21:04:01Z

full-train failed: interrupted: context canceled
--- experiment log tail ---
COLLIMATOR_MBC_ID_VOCAB=0 \
COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS=0 \
COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE=0 \
COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES=0 \
COLLIMATOR_TIERED_BIGRAM_BRANCH_MIN_CRIT= \
COLLIMATOR_EXPERIMENT_TAG=_inherit_from_filetypes_plist_8b54303f_full_train \
.venv/bin/python -u -m collimator experiment --db postgres://hopper@localhost:5432/hopper --output out/experiments/azoth --model-name azoth --learner azoth --workers 24 --seed 42 \
	--experiment-idea inherit_from_filetypes_plist_8b54303f_full_train --route filetypes/jar  \
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
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_inherit_from_filetypes_plist_8b54303f_full_train.log"
17:02:35 INFO  collimator.experiment: using cached experiment snapshot: max_id=2588429170
17:02:35 INFO  collimator.experiment: dataset snapshot: max_id=2588429170
17:02:42 INFO  collimator.experiment: cached corpus selections: out/cache/experiment/azoth/corpus_e805abf2d1882122.json

EXPERIMENT
============================================================
Sampled train: 6171 (2580 malware, 3591 benign)
External test: 3566 (503 malware, 3063 benign)
17:02:42 WARNING collimator.features: mem-aware workers: capping 24 -> 1 (MemAvailable=46 GB, reserve=48 GB, per_worker=2.0 GB); tune via COLLIMATOR_MEM_RESERVE_GB / COLLIMATOR_MEM_PER_WORKER_GB or disable with COLLIMATOR_MEM_AWARE_WORKERS=0
17:02:42 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
17:03:36 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
make[1]: *** wait: No child processes.  Stop.
make[1]: *** Waiting for unfinished jobs....
make[1]: *** wait: No child processes.  Stop.
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-08-03T21-02-34_20260803T210234-promote-403b3d7c80635af8_inherit_from_filetypes_plist_8b54303f_full_train.log

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9516)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `403b3d7c80635af8` | `564a7a0aed5aee4e` | `—` |
| PR AUC | 0.9516 | 0.9574 | — |
| ROC AUC | 0.9781 | 0.9794 | — |
| F1 | 0.8929 | 0.9164 | — |

## Disposition

This spec did not survive the promotion ladder.

full-train failed: interrupted: context canceled
--- experiment log tail ---
COLLIMATOR_MBC_ID_VOCAB=0 \
COLLIMATOR_TRAIT_CONFIDENCE_MOMENTS=0 \
COLLIMATOR_TRAIT_ID_LEXICAL_DISTANCE=0 \
COLLIMATOR_DOCUMENT_OBFUSCATION_FEATURES=0 \
COLLIMATOR_TIERED_BIGRAM_BRANCH_MIN_CRIT= \
COLLIMATOR_EXPERIMENT_TAG=_inherit_from_filetypes_plist_8b54303f_full_train \
.venv/bin/python -u -m collimator experiment --db postgres://hopper@localhost:5432/hopper --output out/experiments/azoth --model-name azoth --learner azoth --workers 24 --seed 42 \
	--experiment-idea inherit_from_filetypes_plist_8b54303f_full_train --route filetypes/jar  \
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
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_inherit_from_filetypes_plist_8b54303f_full_train.log"
17:02:35 INFO  collimator.experiment: using cached experiment snapshot: max_id=2588429170
17:02:35 INFO  collimator.experiment: dataset snapshot: max_id=2588429170
17:02:42 INFO  collimator.experiment: cached corpus selections: out/cache/experiment/azoth/corpus_e805abf2d1882122.json

EXPERIMENT
============================================================
Sampled train: 6171 (2580 malware, 3591 benign)
External test: 3566 (503 malware, 3063 benign)
17:02:42 WARNING collimator.features: mem-aware workers: capping 24 -> 1 (MemAvailable=46 GB, reserve=48 GB, per_worker=2.0 GB); tune via COLLIMATOR_MEM_RESERVE_GB / COLLIMATOR_MEM_PER_WORKER_GB or disable with COLLIMATOR_MEM_AWARE_WORKERS=0
17:02:42 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
17:03:36 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
make[1]: *** wait: No child processes.  Stop.
make[1]: *** Waiting for unfinished jobs....
make[1]: *** wait: No child processes.  Stop.
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-08-03T21-02-34_20260803T210234-promote-403b3d7c80635af8_inherit_from_filetypes_plist_8b54303f_full_train.log
