# Confirm FAIL — 45e95d1d9ba4df12 on `filetypes/pe`

Cycle `20260704T114350-confirm-45e95d1d9ba4df12` — 2026-07-04T11:43:50Z

experiment failed: timed out after 30m0s (timeout(1) exit 124)
--- experiment log tail ---
──────────────────── Holdout ─────────────────────────
  n=69457 (61639 malware, 7818 benign)  threshold=0.268
  ROC AUC  0.9996   Avg Prec  0.9999   Brier  0.0030   ECE  0.0007
  F1  0.9975   Precision  0.9959   Recall  0.9990
  TP 61580 / 61639  (99.90%)    FN    59 / 61639  (0.10%)
  TN  7567 / 7818  (96.79%)    FP   251 / 7818  (3.21%)
======================================================

=======================EXTERNAL TEST========================
  Threshold: 0.268
  Precision: 0.9986
  Recall:    0.9972
  F1:        0.9979
  ROC AUC:   0.9997
  Avg Prec:  1.0000
  Brier:     0.0051
  Recall@FP/100M: L25(deploy)=0.8154 50=0.9050 100=0.9428 300=0.9814 500=0.9905 (n_benign=21382, min_resolvable=4676.8/100M)
08:08:23 INFO  collimator.experiment: seed-search attempt 1/3 done: F1=0.9979 AUC=0.9997 recall@L50/100M=0.9050 (193.0s)
08:08:23 INFO  collimator.experiment: seed-search attempt 2/3 (seed=44)
08:08:23 INFO  collimator.train: training: 1157603 samples (1027311 malware, 130292 benign), 7534 features, sparse nnz=520563672 density=6.0% mem=3976MB
08:08:30 INFO  collimator.train: holdout: 138913 samples (123278 malware, 15635 benign)
08:08:33 INFO  collimator.train: cross-validation disabled
08:08:33 INFO  collimator.train: training final model on 1018690 samples
08:08:33 INFO  collimator.model: device=cpu (sparse: 5.970% density)
08:10:07 INFO  collimator.model: device=cpu (sparse: 5.970% density)
08:11:45 INFO  collimator.train: final model: 300 trees (early stopped at 300) on cpu
08:11:45 INFO  collimator.train: evaluation: AUC=0.9996 F1=0.9970 threshold=0.207 (isotonic calibrated)

======================================================
TRAINING RESULTS
======================================================
Dataset:  1157603 (1027311 malware, 130292 benign, 0.1:1)
Features: 7534
Model:    azoth  301/300 trees  depth=12  lr=0.05  leaves=96  min_child_samples=100  β=2.0  seed=44
──────────────────── Holdout ─────────────────────────
  n=69457 (61639 malware, 7818 benign)  threshold=0.207
  ROC AUC  0.9996   Avg Prec  0.9999   Brier  0.0030   ECE  0.0004
  F1  0.9970   Precision  0.9947   Recall  0.9994
  TP 61605 / 61639  (99.94%)    FN    34 / 61639  (0.06%)
  TN  7487 / 7818  (95.77%)    FP   331 / 7818  (4.23%)
======================================================
08:11:46 INFO  collimator.experiment: seed-search attempt 2/3 done: F1=0.9980 AUC=0.9997 recall@L50/100M=0.9151 (203.1s)
08:11:46 INFO  collimator.experiment: seed-search attempt 3/3 (seed=45)
08:11:46 INFO  collimator.train: training: 1157603 samples (1027311 malware, 130292 benign), 7534 features, sparse nnz=520563672 density=6.0% mem=3976MB
08:11:52 INFO  collimator.train: holdout: 138913 samples (123278 malware, 15635 benign)
08:11:54 INFO  collimator.train: cross-validation disabled
08:11:54 INFO  collimator.train: training final model on 1018690 samples
08:11:54 INFO  collimator.model: device=cpu (sparse: 5.970% density)
08:13:16 INFO  collimator.model: device=cpu (sparse: 5.970% density)
make[2]: *** [Makefile:1890: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-07-04T11-43-50_20260704T114350-confirm-45e95d1d9ba4df12_pe_control_hardneg_01_12_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `45e95d1d9ba4df12` | `` |
| PR AUC | 0.9997 | 0.0000 |
| ROC AUC | 0.9997 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
