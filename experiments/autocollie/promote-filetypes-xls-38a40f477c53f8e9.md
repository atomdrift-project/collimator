# Promote REJECTED — `38a40f477c53f8e9` on `filetypes/xls`

Generated 2026-07-04T19:06:17Z

full-train failed: interrupted: context canceled
--- experiment log tail ---
\
	 \
	--cache-dir out/cache/experiment/azoth \
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_xls_control_train_reg_lambda_leaves_full_train.log"
15:05:47 INFO  collimator.experiment: using cached experiment snapshot: max_id=1896870317
15:05:47 INFO  collimator.experiment: dataset snapshot: max_id=1896870317
15:05:47 INFO  collimator.experiment: loaded cached matrices: 84457 train, 15100 test, 2240 features

EXPERIMENT (cached matrices: 84457 train, 15100 test)
15:05:47 INFO  collimator.experiment: seed-search attempt 1/3 (seed=42)
15:05:47 INFO  collimator.train: training: 84457 samples (61668 malware, 22789 benign), 2240 features, sparse nnz=7878819 density=4.2% mem=60MB
15:05:47 INFO  collimator.train: holdout: 10135 samples (7400 malware, 2735 benign)
15:05:47 INFO  collimator.train: cross-validation disabled
15:05:47 INFO  collimator.train: training final model on 74322 samples
15:05:48 INFO  collimator.model: xgboost device: cuda:0
15:05:48 INFO  collimator.model: device=cpu (sparse: 4.157% density)
15:05:56 INFO  collimator.train: final model: 400 trees (early stopped at 399) on cpu
15:05:56 INFO  collimator.train: evaluation: AUC=0.9994 F1=0.9968 threshold=0.200 (isotonic calibrated)

======================================================
TRAINING RESULTS
======================================================
Dataset:  84457 (61668 malware, 22789 benign, 0.4:1)
Features: 2240
Model:    azoth  400/400 trees  depth=12  lr=0.05  leaves=128  min_child_samples=100  β=2.0  seed=42
──────────────────── Holdout ─────────────────────────
  n=5068 (3700 malware, 1368 benign)  threshold=0.200
  ROC AUC  0.9994   Avg Prec  0.9995   Brier  0.0031   ECE  0.0017
  F1  0.9968   Precision  0.9949   Recall  0.9986
  TP  3695 / 3700  (99.86%)    FN     5 / 3700  (0.14%)
  TN  1349 / 1368  (98.61%)    FP    19 / 1368  (1.39%)
======================================================

=======================EXTERNAL TEST========================
  Threshold: 0.200
  Precision: 0.9970
  Recall:    0.9563
  F1:        0.9762
  ROC AUC:   0.9929
  Avg Prec:  0.9978
  Brier:     0.0363
  Recall@FP/100M: L25(deploy)=0.9386 50=0.9456 100=0.9500 300=0.9626 500=0.9638 (n_benign=3764, min_resolvable=26567.5/100M)
15:05:56 INFO  collimator.experiment: seed-search attempt 1/3 done: F1=0.9762 AUC=0.9929 recall@L50/100M=0.9456 (8.8s)
15:05:56 INFO  collimator.experiment: seed-search attempt 2/3 (seed=43)
15:05:56 INFO  collimator.train: training: 84457 samples (61668 malware, 22789 benign), 2240 features, sparse nnz=7878819 density=4.2% mem=60MB
15:05:56 INFO  collimator.train: holdout: 10135 samples (7400 malware, 2735 benign)
15:05:56 INFO  collimator.train: cross-validation disabled
15:05:56 INFO  collimator.train: training final model on 74322 samples
15:05:56 INFO  collimator.model: device=cpu (sparse: 4.183% density)
make[1]: *** [Makefile:1890: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-07-04T19-05-46_20260704T190546-promote-38a40f477c53f8e9_xls_control_train_reg_lambda_leaves_full_train.log

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9972)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `38a40f477c53f8e9` | `8295573a5639df11` | `—` |
| PR AUC | 0.9972 | 0.9976 | — |
| ROC AUC | 0.9915 | 0.9923 | — |
| F1 | 0.9676 | 0.9592 | — |

## Disposition

This spec did not survive the promotion ladder.

full-train failed: interrupted: context canceled
--- experiment log tail ---
\
	 \
	--cache-dir out/cache/experiment/azoth \
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_xls_control_train_reg_lambda_leaves_full_train.log"
15:05:47 INFO  collimator.experiment: using cached experiment snapshot: max_id=1896870317
15:05:47 INFO  collimator.experiment: dataset snapshot: max_id=1896870317
15:05:47 INFO  collimator.experiment: loaded cached matrices: 84457 train, 15100 test, 2240 features

EXPERIMENT (cached matrices: 84457 train, 15100 test)
15:05:47 INFO  collimator.experiment: seed-search attempt 1/3 (seed=42)
15:05:47 INFO  collimator.train: training: 84457 samples (61668 malware, 22789 benign), 2240 features, sparse nnz=7878819 density=4.2% mem=60MB
15:05:47 INFO  collimator.train: holdout: 10135 samples (7400 malware, 2735 benign)
15:05:47 INFO  collimator.train: cross-validation disabled
15:05:47 INFO  collimator.train: training final model on 74322 samples
15:05:48 INFO  collimator.model: xgboost device: cuda:0
15:05:48 INFO  collimator.model: device=cpu (sparse: 4.157% density)
15:05:56 INFO  collimator.train: final model: 400 trees (early stopped at 399) on cpu
15:05:56 INFO  collimator.train: evaluation: AUC=0.9994 F1=0.9968 threshold=0.200 (isotonic calibrated)

======================================================
TRAINING RESULTS
======================================================
Dataset:  84457 (61668 malware, 22789 benign, 0.4:1)
Features: 2240
Model:    azoth  400/400 trees  depth=12  lr=0.05  leaves=128  min_child_samples=100  β=2.0  seed=42
──────────────────── Holdout ─────────────────────────
  n=5068 (3700 malware, 1368 benign)  threshold=0.200
  ROC AUC  0.9994   Avg Prec  0.9995   Brier  0.0031   ECE  0.0017
  F1  0.9968   Precision  0.9949   Recall  0.9986
  TP  3695 / 3700  (99.86%)    FN     5 / 3700  (0.14%)
  TN  1349 / 1368  (98.61%)    FP    19 / 1368  (1.39%)
======================================================

=======================EXTERNAL TEST========================
  Threshold: 0.200
  Precision: 0.9970
  Recall:    0.9563
  F1:        0.9762
  ROC AUC:   0.9929
  Avg Prec:  0.9978
  Brier:     0.0363
  Recall@FP/100M: L25(deploy)=0.9386 50=0.9456 100=0.9500 300=0.9626 500=0.9638 (n_benign=3764, min_resolvable=26567.5/100M)
15:05:56 INFO  collimator.experiment: seed-search attempt 1/3 done: F1=0.9762 AUC=0.9929 recall@L50/100M=0.9456 (8.8s)
15:05:56 INFO  collimator.experiment: seed-search attempt 2/3 (seed=43)
15:05:56 INFO  collimator.train: training: 84457 samples (61668 malware, 22789 benign), 2240 features, sparse nnz=7878819 density=4.2% mem=60MB
15:05:56 INFO  collimator.train: holdout: 10135 samples (7400 malware, 2735 benign)
15:05:56 INFO  collimator.train: cross-validation disabled
15:05:56 INFO  collimator.train: training final model on 74322 samples
15:05:56 INFO  collimator.model: device=cpu (sparse: 4.183% density)
make[1]: *** [Makefile:1890: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-07-04T19-05-46_20260704T190546-promote-38a40f477c53f8e9_xls_control_train_reg_lambda_leaves_full_train.log
