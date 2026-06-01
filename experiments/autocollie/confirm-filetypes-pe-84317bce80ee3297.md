# Confirm FAIL — 84317bce80ee3297 on `filetypes/pe`

Cycle `20260601T170434-confirm-84317bce80ee3297` — 2026-06-01T17:04:34Z

experiment failed: timed out after 30m0s (timeout(1) exit 124)
--- experiment log tail ---
Sampled train: 1070795 (950965 malware, 119830 benign)
External test: 176433 (156691 malware, 19742 benign)
13:04:38 INFO  collimator.experiment: pass 1: building vocabulary (worker-local DB fetching)
13:17:55 INFO  collimator.features: tiered crit bigrams: 5000 vocab entries
13:18:28 INFO  collimator.features: extended metrics: 175 keys from 5000 scanned rows
13:19:01 INFO  collimator.features: crit-category n-grams: 52 unigrams, 366 bigrams, 436 trigrams from 5000 scanned rows
13:19:43 INFO  collimator.features: ATT&CK/MBC n-grams: 0/500 atk bi/tri, 37/500 mbc bi/tri from 5000 scanned rows
13:19:43 INFO  collimator.features: vocab: 1155 paths, 53 filetypes, 19644 elements, 5000 bigrams, 0 ghosts, 175 ext_metrics -> 57168 features
13:19:43 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
13:25:19 INFO  collimator.features: saved feature spec: 57168 features to out/cache/experiment/azoth/matrix_f2393b4f4d64a6aa_spec.json
13:25:19 INFO  collimator.experiment: cached matrices: out/cache/experiment/azoth/matrix_f2393b4f4d64a6aa.npz (1070795 train, 176433 test, 57168 features)
13:25:19 INFO  collimator.experiment: seed-search attempt 1/3 (seed=43)
13:25:19 INFO  collimator.train: training: 1070795 samples (950965 malware, 119830 benign), 57168 features, sparse nnz=1414225633 density=2.3% mem=10794MB
13:25:20 INFO  collimator.train: holdout: 128496 samples (114116 malware, 14380 benign)
13:26:03 INFO  collimator.train: cross-validation disabled
13:26:03 INFO  collimator.train: training final model on 942299 samples
13:26:03 INFO  collimator.model: xgboost device: cuda:0
13:26:03 INFO  collimator.model: device=cpu (sparse: 2.310% density)
13:29:59 INFO  collimator.model: device=cpu (sparse: 2.310% density)
13:34:30 INFO  collimator.train: final model: 350 trees (early stopped at 350) on cpu
13:34:31 INFO  collimator.train: evaluation: AUC=0.9998 F1=0.9986 threshold=0.302 (isotonic calibrated)

======================================================
TRAINING RESULTS
======================================================
Dataset:  1070795 (950965 malware, 119830 benign, 0.1:1)
Features: 57168
Model:    azoth  351/350 trees  depth=12  lr=0.03  leaves=96  min_child_samples=100  β=2.0  seed=43
──────────────────── Holdout ─────────────────────────
  n=64248 (57058 malware, 7190 benign)  threshold=0.302
  ROC AUC  0.9998   Avg Prec  1.0000   Brier  0.0017   ECE  0.0005
  F1  0.9986   Precision  0.9976   Recall  0.9997
  TP 57042 / 57058  (99.97%)    FN    16 / 57058  (0.03%)
  TN  7051 / 7190  (98.07%)    FP   139 / 7190  (1.93%)
======================================================

=======================EXTERNAL TEST========================
  Threshold: 0.302
  Precision: 0.9993
  Recall:    0.9963
  F1:        0.9978
  ROC AUC:   0.9999
  Avg Prec:  1.0000
  Brier:     0.0050
  Recall@FP/100M: 50=0.8808 100=0.8808 300=0.8808 500=0.8808 900=0.8808 (n_benign=19742, min_resolvable=5065.3/100M)
13:34:31 INFO  collimator.experiment: seed-search attempt 1/3 done: F1=0.9978 AUC=0.9999 recall@L50/100M=0.8808 (552.4s)
13:34:31 INFO  collimator.experiment: seed-search attempt 2/3 (seed=44)
13:34:31 INFO  collimator.train: training: 1070795 samples (950965 malware, 119830 benign), 57168 features, sparse nnz=1414225633 density=2.3% mem=10794MB
13:34:32 INFO  collimator.train: holdout: 128496 samples (114116 malware, 14380 benign)
make[2]: *** [Makefile:1573: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-01T17-04-34_20260601T170434-confirm-84317bce80ee3297_pe_train_hardneg_01_12_lr003_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `84317bce80ee3297` | `` |
| PR AUC | 0.9995 | 0.0000 |
| ROC AUC | 0.9995 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
