# Promote REJECTED — `3a6f1db03980c138` on `general`

Generated 2026-05-30T03:39:33Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-30T03-39-31_20260530T032450-promote-3a6f1db03980c138_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 64 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-general-3a6f1db03980c138 \
	--summary /home/t/collimator/out/models/azoth-candidate-general-3a6f1db03980c138/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-general-3a6f1db03980c138/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-general-3a6f1db03980c138/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-general-3a6f1db03980c138/score_table.npz \
	--partition dev \
	--parallelism 2 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1662, in <module>
    raise SystemExit(main())
                     ~~~~^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1369, in main
    general_cache = np.load(args.general_scores)
  File "/home/t/collimator/.venv/lib/python3.14/site-packages/numpy/lib/_npyio_impl.py", line 454, in load
    fid = stack.enter_context(open(os.fspath(file), "rb"))
                              ~~~~^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/home/t/collimator/out/models/azoth-candidate-general-3a6f1db03980c138/general/threshold_scores.npz'
make[1]: *** [Makefile:1030: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9979)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3a6f1db03980c138` | `aac1a08fe0a3b01d` | `532c68e7c274c6e7` |
| PR AUC | 0.9979 | 0.9998 | 0.9996 |
| ROC AUC | 0.9980 | 0.9996 | 0.9996 |
| F1 | 0.9767 | 0.9934 | 0.9888 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-30T03-39-31_20260530T032450-promote-3a6f1db03980c138_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 64 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-general-3a6f1db03980c138 \
	--summary /home/t/collimator/out/models/azoth-candidate-general-3a6f1db03980c138/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-general-3a6f1db03980c138/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-general-3a6f1db03980c138/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-general-3a6f1db03980c138/score_table.npz \
	--partition dev \
	--parallelism 2 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1662, in <module>
    raise SystemExit(main())
                     ~~~~^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1369, in main
    general_cache = np.load(args.general_scores)
  File "/home/t/collimator/.venv/lib/python3.14/site-packages/numpy/lib/_npyio_impl.py", line 454, in load
    fid = stack.enter_context(open(os.fspath(file), "rb"))
                              ~~~~^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/home/t/collimator/out/models/azoth-candidate-general-3a6f1db03980c138/general/threshold_scores.npz'
make[1]: *** [Makefile:1030: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
