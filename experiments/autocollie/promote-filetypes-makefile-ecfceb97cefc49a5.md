# Promote REJECTED — `ecfceb97cefc49a5` on `filetypes/makefile`

Generated 2026-07-18T15:33:59Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-18T15-33-58_20260718T153354-promote-ecfceb97cefc49a5_azoth-validate.log; tail: make[2]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 24 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-ecfceb97cefc49a5 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-ecfceb97cefc49a5/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-ecfceb97cefc49a5/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-ecfceb97cefc49a5/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-ecfceb97cefc49a5/score_table.npz \
	--partition dev \
	--parallelism 16 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1413, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1127, in main
    general_cache = np.load(args.general_scores)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 471, in load
    ret = NpzFile(fid, own_fid=own_fid, allow_pickle=allow_pickle,
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 197, in __init__
    _zip = zipfile_factory(fid)
           ^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 112, in zipfile_factory
    return zipfile.ZipFile(file, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/zipfile/__init__.py", line 1370, in __init__
    self._RealGetContents()
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/zipfile/__init__.py", line 1437, in _RealGetContents
    raise BadZipFile("File is not a zip file")
zipfile.BadZipFile: File is not a zip file
make[2]: *** [Makefile:1254: azoth-calibrate] Error 1
make[2]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.7019)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `ecfceb97cefc49a5` | `0fc0ace316bf51fa` | `8217487ee9eb6e4d` |
| PR AUC | 0.7019 | 0.7896 | 0.8079 |
| ROC AUC | 0.9317 | 0.9378 | 0.9518 |
| F1 | 0.4545 | 0.8000 | 0.8000 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-18T15-33-58_20260718T153354-promote-ecfceb97cefc49a5_azoth-validate.log; tail: make[2]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 24 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-ecfceb97cefc49a5 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-ecfceb97cefc49a5/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-ecfceb97cefc49a5/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-ecfceb97cefc49a5/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-ecfceb97cefc49a5/score_table.npz \
	--partition dev \
	--parallelism 16 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1413, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1127, in main
    general_cache = np.load(args.general_scores)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 471, in load
    ret = NpzFile(fid, own_fid=own_fid, allow_pickle=allow_pickle,
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 197, in __init__
    _zip = zipfile_factory(fid)
           ^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 112, in zipfile_factory
    return zipfile.ZipFile(file, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/zipfile/__init__.py", line 1370, in __init__
    self._RealGetContents()
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/zipfile/__init__.py", line 1437, in _RealGetContents
    raise BadZipFile("File is not a zip file")
zipfile.BadZipFile: File is not a zip file
make[2]: *** [Makefile:1254: azoth-calibrate] Error 1
make[2]: Leaving directory '/home/t/collimator')
