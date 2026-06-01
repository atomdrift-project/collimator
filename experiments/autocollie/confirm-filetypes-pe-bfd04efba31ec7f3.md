# Confirm FAIL — bfd04efba31ec7f3 on `filetypes/pe`

Cycle `20260601T194801-confirm-bfd04efba31ec7f3` — 2026-06-01T19:48:01Z

experiment failed: timed out after 30m0s (timeout(1) exit 124)
--- experiment log tail ---
16:02:00 INFO  collimator.features: extended metrics: 175 keys from 5000 scanned rows
16:02:31 INFO  collimator.features: crit-category n-grams: 52 unigrams, 366 bigrams, 436 trigrams from 5000 scanned rows
16:03:15 INFO  collimator.features: ATT&CK/MBC n-grams: 0/500 atk bi/tri, 37/500 mbc bi/tri from 5000 scanned rows
16:03:46 INFO  collimator.features: symbol vocab: 8000 entries from 5000 scanned rows
16:03:46 INFO  collimator.features: kv vocab: 2823 entries from 5000 scanned rows
16:03:46 INFO  collimator.features: vocab: 1155 paths, 53 filetypes, 19644 elements, 5000 bigrams, 0 ghosts, 175 ext_metrics -> 67991 features
16:03:47 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
16:10:04 INFO  collimator.features: saved feature spec: 67991 features to out/cache/experiment/azoth/matrix_aa034e83022a25cf_spec.json
16:10:04 INFO  collimator.experiment: cached matrices: out/cache/experiment/azoth/matrix_aa034e83022a25cf.npz (1070795 train, 176433 test, 67991 features)
16:10:04 INFO  collimator.experiment: seed-search attempt 1/3 (seed=43)
16:10:04 INFO  collimator.train: training: 1070795 samples (950965 malware, 119830 benign), 67991 features, sparse nnz=1602169088 density=2.2% mem=12228MB
16:10:06 INFO  collimator.train: holdout: 128496 samples (114116 malware, 14380 benign)
16:10:53 INFO  collimator.train: cross-validation disabled
16:10:53 INFO  collimator.train: training final model on 942299 samples
16:10:54 INFO  collimator.model: xgboost device: cuda:0
16:10:54 INFO  collimator.model: device=cpu (sparse: 2.200% density)
16:14:12 INFO  collimator.train: final model: 250 trees (early stopped at 250) on cpu
16:14:13 INFO  collimator.train: evaluation: AUC=0.9998 F1=0.9989 threshold=0.306 (isotonic calibrated)

======================================================
TRAINING RESULTS
======================================================
Dataset:  1070795 (950965 malware, 119830 benign, 0.1:1)
Features: 67991
Model:    azoth  251/250 trees  depth=12  lr=0.05  leaves=96  min_child_samples=100  β=2.0  seed=43
──────────────────── Holdout ─────────────────────────
  n=64248 (57058 malware, 7190 benign)  threshold=0.306
  ROC AUC  0.9998   Avg Prec  1.0000   Brier  0.0015   ECE  0.0004
  F1  0.9989   Precision  0.9982   Recall  0.9996
  TP 57034 / 57058  (99.96%)    FN    24 / 57058  (0.04%)
  TN  7087 / 7190  (98.57%)    FP   103 / 7190  (1.43%)
======================================================

=======================EXTERNAL TEST========================
  Threshold: 0.306
  Precision: 0.9988
  Recall:    0.9992
  F1:        0.9990
  ROC AUC:   0.9999
  Avg Prec:  1.0000
  Brier:     0.0018
  Recall@FP/100M: 50=0.8948 100=0.8948 300=0.8948 500=0.8948 900=0.8948 (n_benign=19742, min_resolvable=5065.3/100M)
16:14:13 INFO  collimator.experiment: seed-search attempt 1/3 done: F1=0.9990 AUC=0.9999 recall@L50/100M=0.8948 (249.0s)
16:14:13 INFO  collimator.experiment: seed-search attempt 2/3 (seed=44)
16:14:13 INFO  collimator.train: training: 1070795 samples (950965 malware, 119830 benign), 67991 features, sparse nnz=1602169088 density=2.2% mem=12228MB
16:14:15 INFO  collimator.train: holdout: 128496 samples (114116 malware, 14380 benign)
16:14:56 INFO  collimator.train: cross-validation disabled
16:14:56 INFO  collimator.train: training final model on 942299 samples
16:14:56 INFO  collimator.model: device=cpu (sparse: 2.201% density)
make[2]: *** [Makefile:1573: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-01T19-48-01_20260601T194801-confirm-bfd04efba31ec7f3_pe_feat_kv_symbol_vocab_expanded_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `bfd04efba31ec7f3` | `` |
| PR AUC | 0.9997 | 0.0000 |
| ROC AUC | 0.9997 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
