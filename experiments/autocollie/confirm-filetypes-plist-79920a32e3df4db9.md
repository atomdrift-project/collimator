# Confirm FAIL — 79920a32e3df4db9 on `filetypes/plist`

Cycle `20260613T012138-confirm-79920a32e3df4db9` — 2026-06-13T01:21:38Z

experiment failed: make experiment exit 2: exit status 2
--- experiment log tail ---
======================================================
TRAINING RESULTS
======================================================
Dataset:  9782 (37 malware, 9745 benign, 263.4:1)
Features: 234
Model:    azoth  175/250 trees  depth=12  lr=0.05  leaves=96  min_child_samples=100  β=2.0  seed=44
──────────────────── Holdout ─────────────────────────
  n=1174 (4 malware, 1170 benign)  threshold=0.966
  ROC AUC  0.9998   Avg Prec  0.9500   Brier  0.0015   ECE  0.0021
  F1  0.8889   Precision  0.8000   Recall  1.0000
  TP     4 / 4  (100.00%)    FN     0 / 4  (0.00%)
  TN  1169 / 1170  (99.91%)    FP     1 / 1170  (0.09%)
======================================================
21:22:04 INFO  collimator.experiment: seed-search attempt 2/3 done: F1=0.1176 AUC=0.7087 recall@L50/100M=0.0633 (0.2s)
21:22:04 INFO  collimator.experiment: seed-search attempt 3/3 (seed=45)
21:22:04 INFO  collimator.train: training: 9782 samples (37 malware, 9745 benign), 234 features, sparse nnz=257351 density=11.2% mem=2MB
21:22:04 INFO  collimator.train: holdout: 1174 samples (4 malware, 1170 benign)
21:22:04 INFO  collimator.train: cross-validation disabled
21:22:04 INFO  collimator.train: training final model on 8608 samples
21:22:04 INFO  collimator.model: device=cpu (sparse: 11.260% density)
21:22:04 WARNING collimator.train: holdout too small to separate calibration from evaluation; using same split for both
21:22:04 INFO  collimator.train: final model: 250 trees (early stopped at 130) on cpu
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/t/collimator/src/collimator/__main__.py", line 970, in <module>
    main()
  File "/home/t/collimator/src/collimator/__main__.py", line 888, in main
    experiment.run_experiment(
  File "/home/t/collimator/src/collimator/experiment.py", line 1055, in run_experiment
    attempt_result = train.train(
                     ^^^^^^^^^^^^
  File "/home/t/collimator/src/collimator/train.py", line 789, in train
    metrics = _compute_metrics(y_eval, eval_preds, optimal_threshold)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/src/collimator/train.py", line 138, in _compute_metrics
    "brier": float(brier_score_loss(y_true, y_prob)),
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/sklearn/utils/_param_validation.py", line 218, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/sklearn/metrics/_classification.py", line 3773, in brier_score_loss
    transformed_labels, y_proba = _validate_binary_probabilistic_prediction(
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/sklearn/metrics/_classification.py", line 3612, in _validate_binary_probabilistic_prediction
    raise ValueError(f"y_prob contains values greater than 1: {xp.max(y_prob)}")
ValueError: y_prob contains values greater than 1: 1.0000001192092896
make[1]: Leaving directory '/home/t/collimator'
make[1]: *** [Makefile:1847: experiment] Error 1
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-13T01-21-38_20260613T012138-confirm-79920a32e3df4db9_plist_feat_textenc_metrics_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `79920a32e3df4db9` | `` |
| PR AUC | 0.2401 | 0.0000 |
| ROC AUC | 0.8219 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
