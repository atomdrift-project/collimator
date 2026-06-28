# Promote REJECTED — `fa8d5bccea9a86b0` on `filetypes/powershell`

Generated 2026-06-28T11:19:55Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T11-01-13_20260628T110112-promote-fa8d5bccea9a86b0_azoth-validate.log; tail: 2026-06-28 07:03:09,116 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-06-28 07:03:09,118 INFO collimator.features: DB-backed feature extraction: 1547473 rows, 8 workers, batch_size=1024
2026-06-28 07:03:09,376 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-06-28 07:03:09,751 INFO azoth_calibrate_ensemble: filetypes/npm: using cached scores
2026-06-28 07:03:10,099 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-06-28 07:03:10,151 INFO azoth_calibrate_ensemble: filetypes/cargo.toml: using cached scores
2026-06-28 07:03:10,414 WARNING azoth_calibrate_ensemble: filegroups/media: skipped 138629 rows absent from general score cache
2026-06-28 07:03:10,482 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-28 07:03:10,628 WARNING azoth_calibrate_ensemble: filetypes/powershell: skipped 1614 rows absent from general score cache
2026-06-28 07:03:10,651 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-28 07:03:11,183 INFO azoth_calibrate_ensemble: filetypes/powershell: loaded route feature matrix cache out/cache/azoth-route-features/filetypes_powershell-1872261008-48501bdce9d85a97-172b08d8417e358d.matrix.npz (8491 rows, 1378 features, nnz=689878)
2026-06-28 07:03:11,278 INFO azoth_calibrate_ensemble: filegroups/media: loaded route feature matrix cache out/cache/azoth-route-features/filegroups_media-1872261008-f1d3d7a6681083b5-e249e6d2b15fa70b.matrix.npz (275289 rows, 222 features, nnz=2414072)
2026-06-28 07:03:11,317 INFO azoth_calibrate_ensemble: filetypes/powershell: refreshed 8491 rows in 2.8s (fetch 2.1s, filter 0.0s, load 0.6s, extract 0.0s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1378 nnz=689878)
2026-06-28 07:03:18,169 INFO azoth_calibrate_ensemble: filegroups/media: refreshed 275289 rows in 18.5s (fetch 10.7s, filter 0.1s, load 0.1s, extract 0.0s, matrix 0.0s, predict 6.6s, write 0.3s; feature_cache_read 0.7s, feature_cache_write 0.0s; features=222 nnz=2414072)
concurrent.futures.process._RemoteTraceback: 
"""
Traceback (most recent call last):
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/concurrent/futures/process.py", line 264, in _process_worker
    r = call_item.fn(*call_item.args, **call_item.kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1008, in _score_route_worker
    return _score_route(
           ^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 467, in _score_route
    feature_cache_write_s = _save_route_feature_cache(
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 196, in _save_route_feature_cache
    tmp_matrix.replace(matrix_path)
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/pathlib.py", line 1376, in replace
    os.replace(self, target)
FileNotFoundError: [Errno 2] No such file or directory: 'out/cache/azoth-route-features/filetypes_pe-1872261008-4e507e5852f86a82-704b01b5013c605d.matrix.tmp.npz' -> 'out/cache/azoth-route-features/filetypes_pe-1872261008-4e507e5852f86a82-704b01b5013c605d.matrix.npz'
"""

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1398, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1226, in main
    route_scores[general_offset + idx] = fut.result()
                                         ^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/concurrent/futures/_base.py", line 449, in result
    return self.__get_result()
           ^^^^^^^^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/concurrent/futures/_base.py", line 401, in __get_result
    raise self._exception
FileNotFoundError: [Errno 2] No such file or directory: 'out/cache/azoth-route-features/filetypes_pe-1872261008-4e507e5852f86a82-704b01b5013c605d.matrix.tmp.npz' -> 'out/cache/azoth-route-features/filetypes_pe-1872261008-4e507e5852f86a82-704b01b5013c605d.matrix.npz'
make[1]: *** [Makefile:1234: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9990)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `fa8d5bccea9a86b0` | `90f4d6ac6a0c06aa` | `2bcf1ab4b10a3ce8` |
| PR AUC | 0.9990 | 0.9987 | 0.9988 |
| ROC AUC | 0.9951 | 0.9946 | 0.9951 |
| F1 | 0.9839 | 0.9842 | 0.9855 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T11-01-13_20260628T110112-promote-fa8d5bccea9a86b0_azoth-validate.log; tail: 2026-06-28 07:03:09,116 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-06-28 07:03:09,118 INFO collimator.features: DB-backed feature extraction: 1547473 rows, 8 workers, batch_size=1024
2026-06-28 07:03:09,376 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-06-28 07:03:09,751 INFO azoth_calibrate_ensemble: filetypes/npm: using cached scores
2026-06-28 07:03:10,099 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-06-28 07:03:10,151 INFO azoth_calibrate_ensemble: filetypes/cargo.toml: using cached scores
2026-06-28 07:03:10,414 WARNING azoth_calibrate_ensemble: filegroups/media: skipped 138629 rows absent from general score cache
2026-06-28 07:03:10,482 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-28 07:03:10,628 WARNING azoth_calibrate_ensemble: filetypes/powershell: skipped 1614 rows absent from general score cache
2026-06-28 07:03:10,651 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-28 07:03:11,183 INFO azoth_calibrate_ensemble: filetypes/powershell: loaded route feature matrix cache out/cache/azoth-route-features/filetypes_powershell-1872261008-48501bdce9d85a97-172b08d8417e358d.matrix.npz (8491 rows, 1378 features, nnz=689878)
2026-06-28 07:03:11,278 INFO azoth_calibrate_ensemble: filegroups/media: loaded route feature matrix cache out/cache/azoth-route-features/filegroups_media-1872261008-f1d3d7a6681083b5-e249e6d2b15fa70b.matrix.npz (275289 rows, 222 features, nnz=2414072)
2026-06-28 07:03:11,317 INFO azoth_calibrate_ensemble: filetypes/powershell: refreshed 8491 rows in 2.8s (fetch 2.1s, filter 0.0s, load 0.6s, extract 0.0s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1378 nnz=689878)
2026-06-28 07:03:18,169 INFO azoth_calibrate_ensemble: filegroups/media: refreshed 275289 rows in 18.5s (fetch 10.7s, filter 0.1s, load 0.1s, extract 0.0s, matrix 0.0s, predict 6.6s, write 0.3s; feature_cache_read 0.7s, feature_cache_write 0.0s; features=222 nnz=2414072)
concurrent.futures.process._RemoteTraceback: 
"""
Traceback (most recent call last):
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/concurrent/futures/process.py", line 264, in _process_worker
    r = call_item.fn(*call_item.args, **call_item.kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1008, in _score_route_worker
    return _score_route(
           ^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 467, in _score_route
    feature_cache_write_s = _save_route_feature_cache(
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 196, in _save_route_feature_cache
    tmp_matrix.replace(matrix_path)
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/pathlib.py", line 1376, in replace
    os.replace(self, target)
FileNotFoundError: [Errno 2] No such file or directory: 'out/cache/azoth-route-features/filetypes_pe-1872261008-4e507e5852f86a82-704b01b5013c605d.matrix.tmp.npz' -> 'out/cache/azoth-route-features/filetypes_pe-1872261008-4e507e5852f86a82-704b01b5013c605d.matrix.npz'
"""

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1398, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1226, in main
    route_scores[general_offset + idx] = fut.result()
                                         ^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/concurrent/futures/_base.py", line 449, in result
    return self.__get_result()
           ^^^^^^^^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/concurrent/futures/_base.py", line 401, in __get_result
    raise self._exception
FileNotFoundError: [Errno 2] No such file or directory: 'out/cache/azoth-route-features/filetypes_pe-1872261008-4e507e5852f86a82-704b01b5013c605d.matrix.tmp.npz' -> 'out/cache/azoth-route-features/filetypes_pe-1872261008-4e507e5852f86a82-704b01b5013c605d.matrix.npz'
make[1]: *** [Makefile:1234: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
