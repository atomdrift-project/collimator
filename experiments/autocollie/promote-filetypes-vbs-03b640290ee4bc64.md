# Promote REJECTED — `03b640290ee4bc64` on `filetypes/vbs`

Generated 2026-06-28T07:20:29Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T07-16-37_20260628T071623-promote-03b640290ee4bc64_azoth-validate.log; tail: 2026-06-28 03:18:27,520 INFO collimator.features: DB-backed feature extraction: 47142 rows, 8 workers, batch_size=1024
2026-06-28 03:18:27,856 INFO azoth_calibrate_ensemble: filetypes/java_class: loaded route feature matrix cache out/cache/azoth-route-features/filetypes_java_class-1872261008-e31509ee85401b77-86c386c78f363663.matrix.npz (837844 rows, 676 features, nnz=7741991)
2026-06-28 03:18:28,472 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-28 03:18:39,376 INFO azoth_calibrate_ensemble: filetypes/shell: refreshed 92945 rows in 27.8s (fetch 6.0s, filter 0.1s, load 0.4s, extract 0.0s, matrix 0.0s, predict 19.9s, write 1.1s; feature_cache_read 0.4s, feature_cache_write 0.0s; features=1635 nnz=5312183)
2026-06-28 03:18:43,244 INFO azoth_calibrate_ensemble: filetypes/xml: refreshed 252206 rows in 33.6s (fetch 11.8s, filter 0.1s, load 1.4s, extract 0.0s, matrix 0.0s, predict 18.2s, write 1.4s; feature_cache_read 0.6s, feature_cache_write 0.0s; features=447 nnz=2693838)
2026-06-28 03:18:46,908 INFO azoth_calibrate_ensemble: filegroups/media: refreshed 275285 rows in 38.6s (fetch 14.6s, filter 0.1s, load 1.0s, extract 0.0s, matrix 0.0s, predict 22.4s, write 0.2s; feature_cache_read 0.1s, feature_cache_write 0.0s; features=222 nnz=2413795)
2026-06-28 03:18:49,422 INFO azoth_calibrate_ensemble: filetypes/zip: refreshed 120700 rows in 38.2s (fetch 10.8s, filter 0.5s, load 1.3s, extract 0.0s, matrix 0.0s, predict 22.9s, write 0.4s; feature_cache_read 2.2s, feature_cache_write 0.0s; features=3265 nnz=15516012)
2026-06-28 03:19:07,623 INFO azoth_calibrate_ensemble: filetypes/java_class: refreshed 837844 rows in 58.7s (fetch 16.6s, filter 1.1s, load 0.9s, extract 0.0s, matrix 0.0s, predict 39.0s, write 0.7s; feature_cache_read 0.3s, feature_cache_write 0.0s; features=676 nnz=7741991)
2026-06-28 03:19:21,600 INFO azoth_calibrate_ensemble: filegroups/documents: saved route feature matrix cache out/cache/azoth-route-features/filegroups_documents-1872261008-dae4960f3eb9532c-8923d3113b10c8fe.matrix.npz
2026-06-28 03:19:22,889 INFO azoth_calibrate_ensemble: filegroups/documents: refreshed 405856 rows in 75.1s (fetch 4.9s, filter 0.2s, load 1.1s, extract 64.1s, matrix 3.3s, predict 0.6s, write 0.6s; feature_cache_read 0.0s, feature_cache_write 0.2s; features=2231 nnz=19057615)
2026-06-28 03:19:23,487 INFO azoth_calibrate_ensemble: filetypes/pe: loaded route feature matrix cache out/cache/azoth-route-features/filetypes_pe-1872261008-4e507e5852f86a82-c9a840e2e39836f0.matrix.npz (1547493 rows, 6781 features, nnz=377923420)
2026-06-28 03:19:39,703 INFO azoth_calibrate_ensemble: filetypes/python: saved route feature matrix cache out/cache/azoth-route-features/filetypes_python-1872261008-f934ddbb7340e765-c33a347e5bfc4cb7.matrix.npz
2026-06-28 03:19:59,548 INFO azoth_calibrate_ensemble: filetypes/python: refreshed 289191 rows in 110.0s (fetch 12.7s, filter 0.6s, load 1.6s, extract 75.0s, matrix 0.1s, predict 18.5s, write 1.4s; feature_cache_read 0.0s, feature_cache_write 0.1s; features=1739 nnz=13252305)
2026-06-28 03:20:25,910 INFO azoth_calibrate_ensemble: filetypes/pe: refreshed 1547493 rows in 137.4s (fetch 15.4s, filter 1.6s, load 1.5s, extract 0.0s, matrix 0.0s, predict 60.7s, write 1.7s; feature_cache_read 55.9s, feature_cache_write 0.0s; features=6781 nnz=377923420)
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
FileNotFoundError: [Errno 2] No such file or directory: 'out/cache/azoth-route-features/filetypes_package.json-1872261008-d7ad92943b718132-f14051a5dcbd2a14.matrix.tmp.npz' -> 'out/cache/azoth-route-features/filetypes_package.json-1872261008-d7ad92943b718132-f14051a5dcbd2a14.matrix.npz'
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
FileNotFoundError: [Errno 2] No such file or directory: 'out/cache/azoth-route-features/filetypes_package.json-1872261008-d7ad92943b718132-f14051a5dcbd2a14.matrix.tmp.npz' -> 'out/cache/azoth-route-features/filetypes_package.json-1872261008-d7ad92943b718132-f14051a5dcbd2a14.matrix.npz'
make[1]: *** [Makefile:1234: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9964)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `03b640290ee4bc64` | `cec68563ee360e14` | `dae8d7691af7b212` |
| PR AUC | 0.9964 | 0.9966 | 0.9965 |
| ROC AUC | 0.9865 | 0.9874 | 0.9873 |
| F1 | 0.9576 | 0.9547 | 0.9614 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T07-16-37_20260628T071623-promote-03b640290ee4bc64_azoth-validate.log; tail: 2026-06-28 03:18:27,520 INFO collimator.features: DB-backed feature extraction: 47142 rows, 8 workers, batch_size=1024
2026-06-28 03:18:27,856 INFO azoth_calibrate_ensemble: filetypes/java_class: loaded route feature matrix cache out/cache/azoth-route-features/filetypes_java_class-1872261008-e31509ee85401b77-86c386c78f363663.matrix.npz (837844 rows, 676 features, nnz=7741991)
2026-06-28 03:18:28,472 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-28 03:18:39,376 INFO azoth_calibrate_ensemble: filetypes/shell: refreshed 92945 rows in 27.8s (fetch 6.0s, filter 0.1s, load 0.4s, extract 0.0s, matrix 0.0s, predict 19.9s, write 1.1s; feature_cache_read 0.4s, feature_cache_write 0.0s; features=1635 nnz=5312183)
2026-06-28 03:18:43,244 INFO azoth_calibrate_ensemble: filetypes/xml: refreshed 252206 rows in 33.6s (fetch 11.8s, filter 0.1s, load 1.4s, extract 0.0s, matrix 0.0s, predict 18.2s, write 1.4s; feature_cache_read 0.6s, feature_cache_write 0.0s; features=447 nnz=2693838)
2026-06-28 03:18:46,908 INFO azoth_calibrate_ensemble: filegroups/media: refreshed 275285 rows in 38.6s (fetch 14.6s, filter 0.1s, load 1.0s, extract 0.0s, matrix 0.0s, predict 22.4s, write 0.2s; feature_cache_read 0.1s, feature_cache_write 0.0s; features=222 nnz=2413795)
2026-06-28 03:18:49,422 INFO azoth_calibrate_ensemble: filetypes/zip: refreshed 120700 rows in 38.2s (fetch 10.8s, filter 0.5s, load 1.3s, extract 0.0s, matrix 0.0s, predict 22.9s, write 0.4s; feature_cache_read 2.2s, feature_cache_write 0.0s; features=3265 nnz=15516012)
2026-06-28 03:19:07,623 INFO azoth_calibrate_ensemble: filetypes/java_class: refreshed 837844 rows in 58.7s (fetch 16.6s, filter 1.1s, load 0.9s, extract 0.0s, matrix 0.0s, predict 39.0s, write 0.7s; feature_cache_read 0.3s, feature_cache_write 0.0s; features=676 nnz=7741991)
2026-06-28 03:19:21,600 INFO azoth_calibrate_ensemble: filegroups/documents: saved route feature matrix cache out/cache/azoth-route-features/filegroups_documents-1872261008-dae4960f3eb9532c-8923d3113b10c8fe.matrix.npz
2026-06-28 03:19:22,889 INFO azoth_calibrate_ensemble: filegroups/documents: refreshed 405856 rows in 75.1s (fetch 4.9s, filter 0.2s, load 1.1s, extract 64.1s, matrix 3.3s, predict 0.6s, write 0.6s; feature_cache_read 0.0s, feature_cache_write 0.2s; features=2231 nnz=19057615)
2026-06-28 03:19:23,487 INFO azoth_calibrate_ensemble: filetypes/pe: loaded route feature matrix cache out/cache/azoth-route-features/filetypes_pe-1872261008-4e507e5852f86a82-c9a840e2e39836f0.matrix.npz (1547493 rows, 6781 features, nnz=377923420)
2026-06-28 03:19:39,703 INFO azoth_calibrate_ensemble: filetypes/python: saved route feature matrix cache out/cache/azoth-route-features/filetypes_python-1872261008-f934ddbb7340e765-c33a347e5bfc4cb7.matrix.npz
2026-06-28 03:19:59,548 INFO azoth_calibrate_ensemble: filetypes/python: refreshed 289191 rows in 110.0s (fetch 12.7s, filter 0.6s, load 1.6s, extract 75.0s, matrix 0.1s, predict 18.5s, write 1.4s; feature_cache_read 0.0s, feature_cache_write 0.1s; features=1739 nnz=13252305)
2026-06-28 03:20:25,910 INFO azoth_calibrate_ensemble: filetypes/pe: refreshed 1547493 rows in 137.4s (fetch 15.4s, filter 1.6s, load 1.5s, extract 0.0s, matrix 0.0s, predict 60.7s, write 1.7s; feature_cache_read 55.9s, feature_cache_write 0.0s; features=6781 nnz=377923420)
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
FileNotFoundError: [Errno 2] No such file or directory: 'out/cache/azoth-route-features/filetypes_package.json-1872261008-d7ad92943b718132-f14051a5dcbd2a14.matrix.tmp.npz' -> 'out/cache/azoth-route-features/filetypes_package.json-1872261008-d7ad92943b718132-f14051a5dcbd2a14.matrix.npz'
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
FileNotFoundError: [Errno 2] No such file or directory: 'out/cache/azoth-route-features/filetypes_package.json-1872261008-d7ad92943b718132-f14051a5dcbd2a14.matrix.tmp.npz' -> 'out/cache/azoth-route-features/filetypes_package.json-1872261008-d7ad92943b718132-f14051a5dcbd2a14.matrix.npz'
make[1]: *** [Makefile:1234: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
