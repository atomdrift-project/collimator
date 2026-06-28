# Promote REJECTED — `d4483c2273ca4533` on `filetypes/package.json`

Generated 2026-06-25T20:03:49Z

full-train failed: interrupted: context canceled
--- experiment log tail ---
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
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_inherit_from_filetypes_json_1e3933ad_full_train.log"
16:02:51 INFO  collimator.experiment: using cached experiment snapshot: max_id=1868172759
16:02:51 INFO  collimator.experiment: dataset snapshot: max_id=1868172759
16:02:55 INFO  collimator.experiment: cached corpus selections: out/cache/experiment/azoth/corpus_09bda3fa01e56f5d.json

EXPERIMENT
============================================================
Sampled train: 28498 (14501 malware, 13997 benign)
External test: 4796 (2463 malware, 2333 benign)
16:02:55 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
16:03:14 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
16:03:16 INFO  collimator.features: extended metrics: 4 keys from 5000 scanned rows (always-keep below threshold: ast_depth_capped)
16:03:18 INFO  collimator.features: crit-category n-grams: 37 unigrams, 288 bigrams, 450 trigrams from 5000 scanned rows
16:03:20 INFO  collimator.features: ATT&CK/MBC n-grams: 157/500 atk bi/tri, 16/13 mbc bi/tri from 5000 scanned rows
16:03:20 INFO  collimator.features: pruned feature spec: 8999 -> 525 features
16:03:20 INFO  collimator.features: vocab: 120 paths, 2 filetypes, 84 elements, 764 bigrams, 4 ghosts, 4 ext_metrics -> 525 features
16:03:20 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
16:03:31 INFO  collimator.features: saved feature spec: 525 features to out/cache/experiment/azoth/matrix_b23495c4828b160b_spec.json
16:03:31 INFO  collimator.experiment: cached matrices: out/cache/experiment/azoth/matrix_b23495c4828b160b.npz (28498 train, 4796 test, 525 features)
16:03:31 INFO  collimator.experiment: seed-search attempt 1/3 (seed=42)
16:03:31 INFO  collimator.train: training: 28498 samples (14501 malware, 13997 benign), 525 features, sparse nnz=2308617 density=15.4% mem=18MB
16:03:31 INFO  collimator.train: holdout: 3420 samples (1740 malware, 1680 benign)
16:03:31 INFO  collimator.train: cross-validation disabled
16:03:31 INFO  collimator.train: training final model on 25078 samples
16:03:32 INFO  collimator.model: xgboost device: cuda:0
16:03:32 INFO  collimator.model: device=cpu (small: 25078 rows)
16:03:39 INFO  collimator.model: device=cpu (small: 25078 rows)
make[1]: *** [Makefile:1890: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-25T20-02-49_20260625T200249-promote-d4483c2273ca4533_inherit_from_filetypes_json_1e3933ad_full_train.log

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9991)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d4483c2273ca4533` | `1e966f4c57e82cc9` | `—` |
| PR AUC | 0.9991 | 0.9992 | — |
| ROC AUC | 0.9988 | 0.9989 | — |
| F1 | 0.9939 | 0.9935 | — |

## Disposition

This spec did not survive the promotion ladder.

full-train failed: interrupted: context canceled
--- experiment log tail ---
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
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_inherit_from_filetypes_json_1e3933ad_full_train.log"
16:02:51 INFO  collimator.experiment: using cached experiment snapshot: max_id=1868172759
16:02:51 INFO  collimator.experiment: dataset snapshot: max_id=1868172759
16:02:55 INFO  collimator.experiment: cached corpus selections: out/cache/experiment/azoth/corpus_09bda3fa01e56f5d.json

EXPERIMENT
============================================================
Sampled train: 28498 (14501 malware, 13997 benign)
External test: 4796 (2463 malware, 2333 benign)
16:02:55 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
16:03:14 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
16:03:16 INFO  collimator.features: extended metrics: 4 keys from 5000 scanned rows (always-keep below threshold: ast_depth_capped)
16:03:18 INFO  collimator.features: crit-category n-grams: 37 unigrams, 288 bigrams, 450 trigrams from 5000 scanned rows
16:03:20 INFO  collimator.features: ATT&CK/MBC n-grams: 157/500 atk bi/tri, 16/13 mbc bi/tri from 5000 scanned rows
16:03:20 INFO  collimator.features: pruned feature spec: 8999 -> 525 features
16:03:20 INFO  collimator.features: vocab: 120 paths, 2 filetypes, 84 elements, 764 bigrams, 4 ghosts, 4 ext_metrics -> 525 features
16:03:20 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
16:03:31 INFO  collimator.features: saved feature spec: 525 features to out/cache/experiment/azoth/matrix_b23495c4828b160b_spec.json
16:03:31 INFO  collimator.experiment: cached matrices: out/cache/experiment/azoth/matrix_b23495c4828b160b.npz (28498 train, 4796 test, 525 features)
16:03:31 INFO  collimator.experiment: seed-search attempt 1/3 (seed=42)
16:03:31 INFO  collimator.train: training: 28498 samples (14501 malware, 13997 benign), 525 features, sparse nnz=2308617 density=15.4% mem=18MB
16:03:31 INFO  collimator.train: holdout: 3420 samples (1740 malware, 1680 benign)
16:03:31 INFO  collimator.train: cross-validation disabled
16:03:31 INFO  collimator.train: training final model on 25078 samples
16:03:32 INFO  collimator.model: xgboost device: cuda:0
16:03:32 INFO  collimator.model: device=cpu (small: 25078 rows)
16:03:39 INFO  collimator.model: device=cpu (small: 25078 rows)
make[1]: *** [Makefile:1890: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-25T20-02-49_20260625T200249-promote-d4483c2273ca4533_inherit_from_filetypes_json_1e3933ad_full_train.log
