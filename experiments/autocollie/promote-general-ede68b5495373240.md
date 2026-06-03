# Promote REJECTED — `ede68b5495373240` on `general`

Generated 2026-06-03T17:21:07Z

confirm did not hold: experiment failed: interrupted: context canceled
--- experiment log tail ---
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
12:37:06 INFO  collimator.experiment: using cached experiment snapshot: max_id=1652441792
12:37:06 INFO  collimator.experiment: dataset snapshot: max_id=1652441792
12:37:41 INFO  collimator.experiment: cached corpus selections: out/cache/experiment/azoth/corpus_213b0f1893083e3d.json

EXPERIMENT
============================================================
Sampled train: 2038070 (1597025 malware, 441045 benign)
External test: 335505 (262621 malware, 72884 benign)
12:37:41 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
13:02:05 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
13:02:21 INFO  collimator.features: extended metrics: 272 keys from 5000 scanned rows
13:02:35 INFO  collimator.features: crit-category n-grams: 63 unigrams, 485 bigrams, 499 trigrams from 5000 scanned rows
13:02:50 INFO  collimator.features: ATT&CK/MBC n-grams: 288/500 atk bi/tri, 358/500 mbc bi/tri from 5000 scanned rows
13:02:50 INFO  collimator.features: vocab: 1499 paths, 88 filetypes, 30539 elements, 5000 bigrams, 2 ghosts, 272 ext_metrics -> 78435 features
13:02:52 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
13:13:04 INFO  collimator.features: saved feature spec: 78435 features to out/cache/experiment/azoth/matrix_17c70a7be2bbc0e6_spec.json
13:13:04 INFO  collimator.experiment: cached matrices: out/cache/experiment/azoth/matrix_17c70a7be2bbc0e6.npz (2038070 train, 335505 test, 78435 features)
13:13:04 INFO  collimator.experiment: seed-search attempt 1/3 (seed=43)
13:13:04 INFO  collimator.train: training: 2038070 samples (1597025 malware, 441045 benign), 78435 features, sparse nnz=1497632852 density=0.9% mem=11434MB
13:13:34 INFO  collimator.train: holdout: 244569 samples (191643 malware, 52926 benign)
13:16:20 INFO  collimator.train: cross-validation disabled
13:16:20 INFO  collimator.train: training final model on 1793501 samples
13:16:21 INFO  collimator.model: xgboost device: cuda:0
13:16:21 INFO  collimator.model: device=cpu (sparse: 0.937% density)
13:20:06 INFO  collimator.model: device=cpu (sparse: 0.937% density)
make[1]: *** [Makefile:1710: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-03T16-37-05_20260603T163705-confirm-ede68b5495373240_inherit_from_filetypes_tar_1f9a08a6_confirm_seedsearch_3.log

## Gates

- **Confirm** (different seed, original profile): **FAIL** — experiment failed: interrupted: context canceled
--- experiment log tail ---
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
12:37:06 INFO  collimator.experiment: using cached experiment snapshot: max_id=1652441792
12:37:06 INFO  collimator.experiment: dataset snapshot: max_id=1652441792
12:37:41 INFO  collimator.experiment: cached corpus selections: out/cache/experiment/azoth/corpus_213b0f1893083e3d.json

EXPERIMENT
============================================================
Sampled train: 2038070 (1597025 malware, 441045 benign)
External test: 335505 (262621 malware, 72884 benign)
12:37:41 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
13:02:05 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
13:02:21 INFO  collimator.features: extended metrics: 272 keys from 5000 scanned rows
13:02:35 INFO  collimator.features: crit-category n-grams: 63 unigrams, 485 bigrams, 499 trigrams from 5000 scanned rows
13:02:50 INFO  collimator.features: ATT&CK/MBC n-grams: 288/500 atk bi/tri, 358/500 mbc bi/tri from 5000 scanned rows
13:02:50 INFO  collimator.features: vocab: 1499 paths, 88 filetypes, 30539 elements, 5000 bigrams, 2 ghosts, 272 ext_metrics -> 78435 features
13:02:52 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
13:13:04 INFO  collimator.features: saved feature spec: 78435 features to out/cache/experiment/azoth/matrix_17c70a7be2bbc0e6_spec.json
13:13:04 INFO  collimator.experiment: cached matrices: out/cache/experiment/azoth/matrix_17c70a7be2bbc0e6.npz (2038070 train, 335505 test, 78435 features)
13:13:04 INFO  collimator.experiment: seed-search attempt 1/3 (seed=43)
13:13:04 INFO  collimator.train: training: 2038070 samples (1597025 malware, 441045 benign), 78435 features, sparse nnz=1497632852 density=0.9% mem=11434MB
13:13:34 INFO  collimator.train: holdout: 244569 samples (191643 malware, 52926 benign)
13:16:20 INFO  collimator.train: cross-validation disabled
13:16:20 INFO  collimator.train: training final model on 1793501 samples
13:16:21 INFO  collimator.model: xgboost device: cuda:0
13:16:21 INFO  collimator.model: device=cpu (sparse: 0.937% density)
13:20:06 INFO  collimator.model: device=cpu (sparse: 0.937% density)
make[1]: *** [Makefile:1710: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-03T16-37-05_20260603T163705-confirm-ede68b5495373240_inherit_from_filetypes_tar_1f9a08a6_confirm_seedsearch_3.log
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `ede68b5495373240` | `` | `—` |
| PR AUC | 0.9984 | — | — |
| ROC AUC | 0.9983 | — | — |
| F1 | 0.9854 | — | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: experiment failed: interrupted: context canceled
--- experiment log tail ---
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
12:37:06 INFO  collimator.experiment: using cached experiment snapshot: max_id=1652441792
12:37:06 INFO  collimator.experiment: dataset snapshot: max_id=1652441792
12:37:41 INFO  collimator.experiment: cached corpus selections: out/cache/experiment/azoth/corpus_213b0f1893083e3d.json

EXPERIMENT
============================================================
Sampled train: 2038070 (1597025 malware, 441045 benign)
External test: 335505 (262621 malware, 72884 benign)
12:37:41 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
13:02:05 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
13:02:21 INFO  collimator.features: extended metrics: 272 keys from 5000 scanned rows
13:02:35 INFO  collimator.features: crit-category n-grams: 63 unigrams, 485 bigrams, 499 trigrams from 5000 scanned rows
13:02:50 INFO  collimator.features: ATT&CK/MBC n-grams: 288/500 atk bi/tri, 358/500 mbc bi/tri from 5000 scanned rows
13:02:50 INFO  collimator.features: vocab: 1499 paths, 88 filetypes, 30539 elements, 5000 bigrams, 2 ghosts, 272 ext_metrics -> 78435 features
13:02:52 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
13:13:04 INFO  collimator.features: saved feature spec: 78435 features to out/cache/experiment/azoth/matrix_17c70a7be2bbc0e6_spec.json
13:13:04 INFO  collimator.experiment: cached matrices: out/cache/experiment/azoth/matrix_17c70a7be2bbc0e6.npz (2038070 train, 335505 test, 78435 features)
13:13:04 INFO  collimator.experiment: seed-search attempt 1/3 (seed=43)
13:13:04 INFO  collimator.train: training: 2038070 samples (1597025 malware, 441045 benign), 78435 features, sparse nnz=1497632852 density=0.9% mem=11434MB
13:13:34 INFO  collimator.train: holdout: 244569 samples (191643 malware, 52926 benign)
13:16:20 INFO  collimator.train: cross-validation disabled
13:16:20 INFO  collimator.train: training final model on 1793501 samples
13:16:21 INFO  collimator.model: xgboost device: cuda:0
13:16:21 INFO  collimator.model: device=cpu (sparse: 0.937% density)
13:20:06 INFO  collimator.model: device=cpu (sparse: 0.937% density)
make[1]: *** [Makefile:1710: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-03T16-37-05_20260603T163705-confirm-ede68b5495373240_inherit_from_filetypes_tar_1f9a08a6_confirm_seedsearch_3.log
