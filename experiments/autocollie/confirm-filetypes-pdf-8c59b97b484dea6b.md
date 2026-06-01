# Confirm FAIL — 8c59b97b484dea6b on `filetypes/pdf`

Cycle `20260601T103353-confirm-8c59b97b484dea6b` — 2026-06-01T10:33:53Z

experiment failed: make experiment exit 2: exit status 2
--- experiment log tail ---
--extra-trees \
	--seed-search-k 3 \
	--save-all-seeds \
	 \
	 \
	--cache-dir out/cache/experiment/azoth \
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_pdf_ctrl_extratrees_lr003_confirm_seedsearch_3.log"
06:33:53 INFO  collimator.experiment: using cached experiment snapshot: max_id=1636831170
06:33:53 INFO  collimator.experiment: dataset snapshot: max_id=1636831170
06:33:53 INFO  collimator.experiment: loaded cached matrices: 102161 train, 16922 test, 878 features

EXPERIMENT (cached matrices: 102161 train, 16922 test)
06:33:53 INFO  collimator.experiment: seed-search attempt 1/3 (seed=43)
06:33:53 INFO  collimator.train: training: 102161 samples (101086 malware, 1075 benign), 878 features, sparse nnz=8973400 density=10.0% mem=69MB
06:33:53 INFO  collimator.train: holdout: 12260 samples (12131 malware, 129 benign)
06:33:53 INFO  collimator.train: cross-validation disabled
06:33:53 INFO  collimator.train: training final model on 89901 samples
06:33:53 INFO  collimator.model: xgboost device: cuda:0
06:33:53 INFO  collimator.model: device=cuda (rows=89901 feats=878 density=10.002%)
[LightGBM] [Fatal] CUDA Tree Learner was not enabled in this build.
Please recompile with CMake option -DUSE_CUDA=1
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/t/collimator/src/collimator/__main__.py", line 970, in <module>
    main()
  File "/home/t/collimator/src/collimator/__main__.py", line 888, in main
    experiment.run_experiment(
  File "/home/t/collimator/src/collimator/experiment.py", line 1010, in run_experiment
    attempt_result = train.train(
                     ^^^^^^^^^^^^
  File "/home/t/collimator/src/collimator/train.py", line 703, in train
    _fit_model(
  File "/home/t/collimator/src/collimator/train.py", line 319, in _fit_model
    model.fit(
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/lightgbm/sklearn.py", line 1560, in fit
    super().fit(
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/lightgbm/sklearn.py", line 1049, in fit
    self._Booster = train(
                    ^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/lightgbm/engine.py", line 297, in train
    booster = Booster(params=params, train_set=train_set)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/lightgbm/basic.py", line 3660, in __init__
    _safe_call(
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/lightgbm/basic.py", line 313, in _safe_call
    raise LightGBMError(_LIB.LGBM_GetLastError().decode("utf-8"))
lightgbm.basic.LightGBMError: CUDA Tree Learner was not enabled in this build.
Please recompile with CMake option -DUSE_CUDA=1
make[2]: *** [Makefile:1585: experiment] Error 1
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-01T10-33-53_20260601T103353-confirm-8c59b97b484dea6b_pdf_ctrl_extratrees_lr003_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `8c59b97b484dea6b` | `` |
| PR AUC | 1.0000 | 0.0000 |
| ROC AUC | 0.9992 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
