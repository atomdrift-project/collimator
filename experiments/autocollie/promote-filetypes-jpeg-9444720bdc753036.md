# Promote REJECTED — `9444720bdc753036` on `filetypes/jpeg`

Generated 2026-07-18T13:50:11Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-18T13-50-08_20260718T134952-promote-9444720bdc753036_azoth-validate.log; tail: make[2]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 24 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-9444720bdc753036 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-9444720bdc753036/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-9444720bdc753036/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-9444720bdc753036/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-9444720bdc753036/score_table.npz \
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

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9800)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `9444720bdc753036` | `286e432b15ffe3a0` | `77e81f1f3957b09e` |
| PR AUC | 0.9800 | 0.9795 | 0.9794 |
| ROC AUC | 0.9776 | 0.9791 | 0.9787 |
| F1 | 0.9114 | 0.9535 | 0.9647 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-18T13-50-08_20260718T134952-promote-9444720bdc753036_azoth-validate.log; tail: make[2]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 24 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-9444720bdc753036 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-9444720bdc753036/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-9444720bdc753036/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-9444720bdc753036/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-9444720bdc753036/score_table.npz \
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
