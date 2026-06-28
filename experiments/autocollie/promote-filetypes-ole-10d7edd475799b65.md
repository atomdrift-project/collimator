# Promote REJECTED — `10d7edd475799b65` on `filetypes/ole`

Generated 2026-06-28T02:38:38Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T02-37-00_20260628T023558-promote-10d7edd475799b65_azoth-validate.log; tail: 2026-06-27 22:38:23,644 INFO collimator.features: DB-backed feature extraction: 14118 rows, 8 workers, batch_size=1024
2026-06-27 22:38:24,068 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-06-27 22:38:24,446 INFO azoth_calibrate_ensemble: filetypes/npm: using cached scores
2026-06-27 22:38:25,059 INFO azoth_calibrate_ensemble: filetypes/cargo.toml: using cached scores
2026-06-27 22:38:25,283 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-06-27 22:38:25,514 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-27 22:38:25,737 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-27 22:38:26,278 INFO azoth_calibrate_ensemble: filetypes/ole: saved route feature matrix cache out/cache/azoth-route-features/filetypes_ole-1872261008-5531c74186faa27c-66e672425f9cfc23.matrix.npz
2026-06-27 22:38:26,378 INFO azoth_calibrate_ensemble: filetypes/ole: refreshed 14118 rows in 5.0s (fetch 1.6s, filter 0.0s, load 0.6s, extract 2.6s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=2179 nnz=426927)
2026-06-27 22:38:26,668 WARNING azoth_calibrate_ensemble: filegroups/media: skipped 29415 rows absent from general score cache
2026-06-27 22:38:26,869 INFO collimator.features: DB-backed feature extraction: 275253 rows, 8 workers, batch_size=1024
2026-06-27 22:38:31,576 WARNING azoth_calibrate_ensemble: filetypes/pkg-info: skipped 3370 rows absent from general score cache
2026-06-27 22:38:31,741 INFO azoth_calibrate_ensemble: filetypes/pkg-info: loaded route feature matrix cache out/cache/azoth-route-features/filetypes_pkg-info-1872261008-097724a6fa631ac5-6e35cbe3d9367a30.matrix.npz (14059 rows, 417 features, nnz=681740)
2026-06-27 22:38:31,891 INFO azoth_calibrate_ensemble: filetypes/pkg-info: refreshed 14059 rows in 10.9s (fetch 10.6s, filter 0.0s, load 0.1s, extract 0.0s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=417 nnz=681740)
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
FileNotFoundError: [Errno 2] No such file or directory: 'out/cache/azoth-route-features/filegroups_media-1872261008-f1d3d7a6681083b5-2d23c209b9f2fe97.matrix.tmp.npz' -> 'out/cache/azoth-route-features/filegroups_media-1872261008-f1d3d7a6681083b5-2d23c209b9f2fe97.matrix.npz'
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
FileNotFoundError: [Errno 2] No such file or directory: 'out/cache/azoth-route-features/filegroups_media-1872261008-f1d3d7a6681083b5-2d23c209b9f2fe97.matrix.tmp.npz' -> 'out/cache/azoth-route-features/filegroups_media-1872261008-f1d3d7a6681083b5-2d23c209b9f2fe97.matrix.npz'
make[1]: *** [Makefile:1234: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9999)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `10d7edd475799b65` | `dc8ca8f0bb55ab23` | `dac4351375eee03d` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9991 | 0.9991 |
| F1 | 0.9935 | 0.9970 | 0.9970 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T02-37-00_20260628T023558-promote-10d7edd475799b65_azoth-validate.log; tail: 2026-06-27 22:38:23,644 INFO collimator.features: DB-backed feature extraction: 14118 rows, 8 workers, batch_size=1024
2026-06-27 22:38:24,068 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-06-27 22:38:24,446 INFO azoth_calibrate_ensemble: filetypes/npm: using cached scores
2026-06-27 22:38:25,059 INFO azoth_calibrate_ensemble: filetypes/cargo.toml: using cached scores
2026-06-27 22:38:25,283 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-06-27 22:38:25,514 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-27 22:38:25,737 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-27 22:38:26,278 INFO azoth_calibrate_ensemble: filetypes/ole: saved route feature matrix cache out/cache/azoth-route-features/filetypes_ole-1872261008-5531c74186faa27c-66e672425f9cfc23.matrix.npz
2026-06-27 22:38:26,378 INFO azoth_calibrate_ensemble: filetypes/ole: refreshed 14118 rows in 5.0s (fetch 1.6s, filter 0.0s, load 0.6s, extract 2.6s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=2179 nnz=426927)
2026-06-27 22:38:26,668 WARNING azoth_calibrate_ensemble: filegroups/media: skipped 29415 rows absent from general score cache
2026-06-27 22:38:26,869 INFO collimator.features: DB-backed feature extraction: 275253 rows, 8 workers, batch_size=1024
2026-06-27 22:38:31,576 WARNING azoth_calibrate_ensemble: filetypes/pkg-info: skipped 3370 rows absent from general score cache
2026-06-27 22:38:31,741 INFO azoth_calibrate_ensemble: filetypes/pkg-info: loaded route feature matrix cache out/cache/azoth-route-features/filetypes_pkg-info-1872261008-097724a6fa631ac5-6e35cbe3d9367a30.matrix.npz (14059 rows, 417 features, nnz=681740)
2026-06-27 22:38:31,891 INFO azoth_calibrate_ensemble: filetypes/pkg-info: refreshed 14059 rows in 10.9s (fetch 10.6s, filter 0.0s, load 0.1s, extract 0.0s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=417 nnz=681740)
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
FileNotFoundError: [Errno 2] No such file or directory: 'out/cache/azoth-route-features/filegroups_media-1872261008-f1d3d7a6681083b5-2d23c209b9f2fe97.matrix.tmp.npz' -> 'out/cache/azoth-route-features/filegroups_media-1872261008-f1d3d7a6681083b5-2d23c209b9f2fe97.matrix.npz'
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
FileNotFoundError: [Errno 2] No such file or directory: 'out/cache/azoth-route-features/filegroups_media-1872261008-f1d3d7a6681083b5-2d23c209b9f2fe97.matrix.tmp.npz' -> 'out/cache/azoth-route-features/filegroups_media-1872261008-f1d3d7a6681083b5-2d23c209b9f2fe97.matrix.npz'
make[1]: *** [Makefile:1234: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
