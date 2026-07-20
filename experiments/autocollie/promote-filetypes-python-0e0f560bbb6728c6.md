# Promote REJECTED — `0e0f560bbb6728c6` on `filetypes/python`

Generated 2026-07-18T14:21:17Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-18T14-21-16_20260718T141848-promote-0e0f560bbb6728c6_azoth-validate.log; tail: make[2]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 24 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-python-0e0f560bbb6728c6 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-python-0e0f560bbb6728c6/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-python-0e0f560bbb6728c6/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-python-0e0f560bbb6728c6/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-python-0e0f560bbb6728c6/score_table.npz \
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

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9741)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0e0f560bbb6728c6` | `6696ca3297e96f72` | `d8276704e0e230b9` |
| PR AUC | 0.9741 | 0.9787 | 0.9789 |
| ROC AUC | 0.9882 | 0.9902 | 0.9903 |
| F1 | 0.9164 | 0.9324 | 0.9305 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-18T14-21-16_20260718T141848-promote-0e0f560bbb6728c6_azoth-validate.log; tail: make[2]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 24 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-python-0e0f560bbb6728c6 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-python-0e0f560bbb6728c6/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-python-0e0f560bbb6728c6/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-python-0e0f560bbb6728c6/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-python-0e0f560bbb6728c6/score_table.npz \
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
