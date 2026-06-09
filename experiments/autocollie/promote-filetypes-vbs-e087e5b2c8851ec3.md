# Promote REJECTED — `e087e5b2c8851ec3` on `filetypes/vbs`

Generated 2026-06-09T11:27:18Z

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
	--min-malware-score 4 \
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
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_vbs_kv_vocab_split_textmetrics_full_train.log"
07:27:02 INFO  collimator.experiment: using cached experiment snapshot: max_id=1679491877
07:27:02 INFO  collimator.experiment: dataset snapshot: max_id=1679491877
07:27:02 INFO  collimator.experiment: loaded cached corpus: 10258 train, 1801 test from out/cache/experiment/azoth/corpus_464c3863d5afece6.json

EXPERIMENT
============================================================
Sampled train: 10258 (7778 malware, 2480 benign)
External test: 1801 (1383 malware, 418 benign)
07:27:02 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
07:27:06 INFO  collimator.features: tiered crit bigrams: 4051 vocab entries
07:27:08 INFO  collimator.features: extended metrics: 28 keys from 5000 scanned rows (always-keep below threshold: ast_depth_capped)
07:27:10 INFO  collimator.features: crit-category n-grams: 22 unigrams, 107 bigrams, 205 trigrams from 5000 scanned rows
07:27:11 INFO  collimator.features: ATT&CK/MBC n-grams: 494/500 atk bi/tri, 150/414 mbc bi/tri from 5000 scanned rows
07:27:13 INFO  collimator.features: kv vocab: 67 entries from 5000 scanned rows
07:27:13 INFO  collimator.features: pruned feature spec: 7631 -> 1070 features
07:27:13 INFO  collimator.features: vocab: 139 paths, 2 filetypes, 188 elements, 161 bigrams, 0 ghosts, 28 ext_metrics -> 1070 features
07:27:13 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
07:27:17 INFO  collimator.features: saved feature spec: 1070 features to out/cache/experiment/azoth/matrix_b5dd3129f08e390b_spec.json
07:27:17 INFO  collimator.experiment: cached matrices: out/cache/experiment/azoth/matrix_b5dd3129f08e390b.npz (10258 train, 1801 test, 1070 features)
07:27:17 INFO  collimator.experiment: seed-search attempt 1/3 (seed=42)
07:27:17 INFO  collimator.train: training: 10258 samples (7778 malware, 2480 benign), 1070 features, sparse nnz=1191102 density=10.9% mem=9MB
07:27:17 INFO  collimator.train: holdout: 1231 samples (933 malware, 298 benign)
07:27:17 INFO  collimator.train: cross-validation disabled
07:27:17 INFO  collimator.train: training final model on 9027 samples
07:27:17 INFO  collimator.model: xgboost device: cuda:0
07:27:17 INFO  collimator.model: device=cpu (sparse: 10.861% density)
make[1]: *** [Makefile:1847: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-09T11-27-01_20260609T112701-promote-e087e5b2c8851ec3_vbs_kv_vocab_split_textmetrics_full_train.log

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9967)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e087e5b2c8851ec3` | `9d67d840a5bee0e2` | `—` |
| PR AUC | 0.9967 | 0.9969 | — |
| ROC AUC | 0.9887 | 0.9893 | — |
| F1 | 0.9562 | 0.9579 | — |

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
	--min-malware-score 4 \
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
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_vbs_kv_vocab_split_textmetrics_full_train.log"
07:27:02 INFO  collimator.experiment: using cached experiment snapshot: max_id=1679491877
07:27:02 INFO  collimator.experiment: dataset snapshot: max_id=1679491877
07:27:02 INFO  collimator.experiment: loaded cached corpus: 10258 train, 1801 test from out/cache/experiment/azoth/corpus_464c3863d5afece6.json

EXPERIMENT
============================================================
Sampled train: 10258 (7778 malware, 2480 benign)
External test: 1801 (1383 malware, 418 benign)
07:27:02 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
07:27:06 INFO  collimator.features: tiered crit bigrams: 4051 vocab entries
07:27:08 INFO  collimator.features: extended metrics: 28 keys from 5000 scanned rows (always-keep below threshold: ast_depth_capped)
07:27:10 INFO  collimator.features: crit-category n-grams: 22 unigrams, 107 bigrams, 205 trigrams from 5000 scanned rows
07:27:11 INFO  collimator.features: ATT&CK/MBC n-grams: 494/500 atk bi/tri, 150/414 mbc bi/tri from 5000 scanned rows
07:27:13 INFO  collimator.features: kv vocab: 67 entries from 5000 scanned rows
07:27:13 INFO  collimator.features: pruned feature spec: 7631 -> 1070 features
07:27:13 INFO  collimator.features: vocab: 139 paths, 2 filetypes, 188 elements, 161 bigrams, 0 ghosts, 28 ext_metrics -> 1070 features
07:27:13 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
07:27:17 INFO  collimator.features: saved feature spec: 1070 features to out/cache/experiment/azoth/matrix_b5dd3129f08e390b_spec.json
07:27:17 INFO  collimator.experiment: cached matrices: out/cache/experiment/azoth/matrix_b5dd3129f08e390b.npz (10258 train, 1801 test, 1070 features)
07:27:17 INFO  collimator.experiment: seed-search attempt 1/3 (seed=42)
07:27:17 INFO  collimator.train: training: 10258 samples (7778 malware, 2480 benign), 1070 features, sparse nnz=1191102 density=10.9% mem=9MB
07:27:17 INFO  collimator.train: holdout: 1231 samples (933 malware, 298 benign)
07:27:17 INFO  collimator.train: cross-validation disabled
07:27:17 INFO  collimator.train: training final model on 9027 samples
07:27:17 INFO  collimator.model: xgboost device: cuda:0
07:27:17 INFO  collimator.model: device=cpu (sparse: 10.861% density)
make[1]: *** [Makefile:1847: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-09T11-27-01_20260609T112701-promote-e087e5b2c8851ec3_vbs_kv_vocab_split_textmetrics_full_train.log
