# Confirm FAIL — 9c5fc1291c9ef2d2 on `filetypes/pe`

Cycle `20260614T230236-confirm-9c5fc1291c9ef2d2` — 2026-06-14T23:02:36Z

experiment failed: timed out after 30m0s (timeout(1) exit 124)
--- experiment log tail ---
Features: 7538
Model:    azoth  301/300 trees  depth=12  lr=0.05  leaves=96  min_child_samples=100  β=2.0  seed=43
──────────────────── Holdout ─────────────────────────
  n=68933 (61474 malware, 7459 benign)  threshold=0.375
  ROC AUC  0.9997   Avg Prec  0.9999   Brier  0.0023   ECE  0.0006
  F1  0.9981   Precision  0.9966   Recall  0.9996
  TP 61451 / 61474  (99.96%)    FN    23 / 61474  (0.04%)
  TN  7247 / 7459  (97.16%)    FP   212 / 7459  (2.84%)
======================================================

=======================EXTERNAL TEST========================
  Threshold: 0.375
  Precision: 0.9985
  Recall:    0.9960
  F1:        0.9972
  ROC AUC:   0.9997
  Avg Prec:  1.0000
  Brier:     0.0046
  Recall@FP/100M: L50(deploy)=0.9104 50=0.9104 100=0.9482 300=0.9783 500=0.9878 (n_benign=20396, min_resolvable=4902.9/100M)
19:30:07 INFO  collimator.experiment: seed-search attempt 1/3 done: F1=0.9972 AUC=0.9997 recall@L50/100M=0.9104 (110.3s)
19:30:07 INFO  collimator.experiment: seed-search attempt 2/3 (seed=44)
19:30:07 INFO  collimator.train: training: 1148879 samples (1024573 malware, 124306 benign), 7538 features, sparse nnz=525944215 density=6.1% mem=4017MB
19:30:07 INFO  collimator.train: holdout: 137866 samples (122949 malware, 14917 benign)
19:30:09 INFO  collimator.train: cross-validation disabled
19:30:09 INFO  collimator.train: training final model on 1011013 samples
19:30:09 INFO  collimator.model: device=cpu (sparse: 6.076% density)
19:31:39 INFO  collimator.train: final model: 300 trees (early stopped at 300) on cpu
19:31:39 INFO  collimator.train: evaluation: AUC=0.9998 F1=0.9984 threshold=0.267 (isotonic calibrated)

======================================================
TRAINING RESULTS
======================================================
Dataset:  1148879 (1024573 malware, 124306 benign, 0.1:1)
Features: 7538
Model:    azoth  301/300 trees  depth=12  lr=0.05  leaves=96  min_child_samples=100  β=2.0  seed=44
──────────────────── Holdout ─────────────────────────
  n=68933 (61474 malware, 7459 benign)  threshold=0.267
  ROC AUC  0.9998   Avg Prec  1.0000   Brier  0.0022   ECE  0.0004
  F1  0.9984   Precision  0.9976   Recall  0.9993
  TP 61429 / 61474  (99.93%)    FN    45 / 61474  (0.07%)
  TN  7311 / 7459  (98.02%)    FP   148 / 7459  (1.98%)
======================================================
19:31:40 INFO  collimator.experiment: seed-search attempt 2/3 done: F1=0.9976 AUC=0.9996 recall@L50/100M=0.8607 (93.2s)
19:31:40 INFO  collimator.experiment: seed-search attempt 3/3 (seed=45)
19:31:40 INFO  collimator.train: training: 1148879 samples (1024573 malware, 124306 benign), 7538 features, sparse nnz=525944215 density=6.1% mem=4017MB
19:31:40 INFO  collimator.train: holdout: 137866 samples (122949 malware, 14917 benign)
19:31:42 INFO  collimator.train: cross-validation disabled
19:31:42 INFO  collimator.train: training final model on 1011013 samples
19:31:42 INFO  collimator.model: device=cpu (sparse: 6.075% density)
make[2]: *** [Makefile:1851: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-14T23-02-36_20260614T230236-confirm-9c5fc1291c9ef2d2_pe_feat_symbol_vocab_bigrams_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `9c5fc1291c9ef2d2` | `` |
| PR AUC | 0.9988 | 0.0000 |
| ROC AUC | 0.9989 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
