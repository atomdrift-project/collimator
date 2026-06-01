# Confirm FAIL — 6ba8690ca1512828 on `filetypes/pe`

Cycle `20260601T182451-confirm-6ba8690ca1512828` — 2026-06-01T18:24:51Z

experiment failed: timed out after 30m0s (timeout(1) exit 124)
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
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_inherit_from_filetypes_tar_1f9a08a6_confirm_seedsearch_3.log"
14:24:51 INFO  collimator.experiment: using cached experiment snapshot: max_id=1636831170
14:24:51 INFO  collimator.experiment: dataset snapshot: max_id=1636831170
14:24:54 INFO  collimator.experiment: loaded cached corpus: 1070795 train, 176433 test from out/cache/experiment/azoth/corpus_6169c9015ef08b61.json

EXPERIMENT
============================================================
Sampled train: 1070795 (950965 malware, 119830 benign)
External test: 176433 (156691 malware, 19742 benign)
14:24:54 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
14:38:07 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
14:38:39 INFO  collimator.features: extended metrics: 175 keys from 5000 scanned rows
14:39:10 INFO  collimator.features: crit-category n-grams: 52 unigrams, 366 bigrams, 436 trigrams from 5000 scanned rows
14:39:55 INFO  collimator.features: ATT&CK/MBC n-grams: 0/500 atk bi/tri, 37/500 mbc bi/tri from 5000 scanned rows
14:39:55 INFO  collimator.features: vocab: 1155 paths, 53 filetypes, 19644 elements, 5000 bigrams, 0 ghosts, 175 ext_metrics -> 57168 features
14:39:55 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
14:45:30 INFO  collimator.features: saved feature spec: 57168 features to out/cache/experiment/azoth/matrix_4fb8e5931d0ab3b6_spec.json
14:45:30 INFO  collimator.experiment: cached matrices: out/cache/experiment/azoth/matrix_4fb8e5931d0ab3b6.npz (1070795 train, 176433 test, 57168 features)
14:45:30 INFO  collimator.experiment: seed-search attempt 1/3 (seed=43)
14:45:30 INFO  collimator.train: training: 1070795 samples (950965 malware, 119830 benign), 57168 features, sparse nnz=1414225633 density=2.3% mem=10794MB
14:45:31 INFO  collimator.train: holdout: 128496 samples (114116 malware, 14380 benign)
14:46:12 INFO  collimator.train: cross-validation disabled
14:46:12 INFO  collimator.train: training final model on 942299 samples
14:46:12 INFO  collimator.model: xgboost device: cuda:0
14:46:12 INFO  collimator.model: device=cpu (sparse: 2.310% density)
14:50:19 INFO  collimator.model: device=cpu (sparse: 2.310% density)
14:54:50 INFO  collimator.train: final model: 400 trees (early stopped at 400) on cpu
make[2]: *** [Makefile:1573: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-01T18-24-51_20260601T182451-confirm-6ba8690ca1512828_inherit_from_filetypes_tar_1f9a08a6_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `6ba8690ca1512828` | `` |
| PR AUC | 0.9995 | 0.0000 |
| ROC AUC | 0.9995 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
