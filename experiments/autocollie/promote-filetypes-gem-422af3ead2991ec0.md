# Promote REJECTED — `422af3ead2991ec0` on `filetypes/gem`

Generated 2026-08-21T13:09:43Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-08-21T12-58-53_20260821T125538-promote-422af3ead2991ec0_azoth-validate.log; tail: 2026-08-21 09:09:14,165 INFO azoth_calibrate_ensemble: filetypes/cargo.toml: using cached scores
2026-08-21 09:09:14,487 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-08-21 09:09:14,914 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-08-21 09:09:15,321 INFO azoth_calibrate_ensemble: filetypes/crate: using cached scores
2026-08-21 09:09:15,738 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-08-21 09:09:16,039 INFO azoth_calibrate_ensemble: filetypes/nupkg: using cached scores
2026-08-21 09:09:16,479 INFO azoth_calibrate_ensemble: filetypes/vsix: using cached scores
2026-08-21 09:09:16,889 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-08-21 09:09:17,592 INFO azoth_calibrate_ensemble: filetypes/apk_android: using cached scores
2026-08-21 09:09:18,124 INFO azoth_calibrate_ensemble: filetypes/xpi: using cached scores
2026-08-21 09:09:18,485 INFO azoth_calibrate_ensemble: filetypes/chrome_manifest: using cached scores
2026-08-21 09:09:18,828 INFO azoth_calibrate_ensemble: filetypes/applescript: using cached scores
2026-08-21 09:09:19,278 INFO azoth_calibrate_ensemble: filetypes/asar: using cached scores
2026-08-21 09:09:19,708 INFO azoth_calibrate_ensemble: filetypes/python_sdist: using cached scores
2026-08-21 09:09:20,099 INFO azoth_calibrate_ensemble: filetypes/dmg: using cached scores
concurrent.futures.process._RemoteTraceback: 
"""
Traceback (most recent call last):
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/concurrent/futures/process.py", line 264, in _process_worker
    r = call_item.fn(*call_item.args, **call_item.kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1116, in _score_route_worker
    return _score_route(
           ^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 446, in _score_route
    spec_hash = _file_sha256(spec_path)
                ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 38, in _file_sha256
    with open(path, "rb") as f:
         ^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/home/t/collimator/out/models/azoth-candidate-filetypes-gem-422af3ead2991ec0/filetypes/gem/feature_spec.json'
"""

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1506, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1334, in main
    route_scores[general_offset + idx] = fut.result()
                                         ^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/concurrent/futures/_base.py", line 449, in result
    return self.__get_result()
           ^^^^^^^^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/concurrent/futures/_base.py", line 401, in __get_result
    raise self._exception
FileNotFoundError: [Errno 2] No such file or directory: '/home/t/collimator/out/models/azoth-candidate-filetypes-gem-422af3ead2991ec0/filetypes/gem/feature_spec.json'
make[1]: *** [Makefile:1247: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9883)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `422af3ead2991ec0` | `8f6c979158e45fbf` | `ccb9ece48868ea0c` |
| PR AUC | 0.9883 | 0.9887 | 0.9894 |
| ROC AUC | 0.9932 | 0.9942 | 0.9948 |
| F1 | 0.9765 | 0.9813 | 0.9813 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-08-21T12-58-53_20260821T125538-promote-422af3ead2991ec0_azoth-validate.log; tail: 2026-08-21 09:09:14,165 INFO azoth_calibrate_ensemble: filetypes/cargo.toml: using cached scores
2026-08-21 09:09:14,487 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-08-21 09:09:14,914 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-08-21 09:09:15,321 INFO azoth_calibrate_ensemble: filetypes/crate: using cached scores
2026-08-21 09:09:15,738 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-08-21 09:09:16,039 INFO azoth_calibrate_ensemble: filetypes/nupkg: using cached scores
2026-08-21 09:09:16,479 INFO azoth_calibrate_ensemble: filetypes/vsix: using cached scores
2026-08-21 09:09:16,889 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-08-21 09:09:17,592 INFO azoth_calibrate_ensemble: filetypes/apk_android: using cached scores
2026-08-21 09:09:18,124 INFO azoth_calibrate_ensemble: filetypes/xpi: using cached scores
2026-08-21 09:09:18,485 INFO azoth_calibrate_ensemble: filetypes/chrome_manifest: using cached scores
2026-08-21 09:09:18,828 INFO azoth_calibrate_ensemble: filetypes/applescript: using cached scores
2026-08-21 09:09:19,278 INFO azoth_calibrate_ensemble: filetypes/asar: using cached scores
2026-08-21 09:09:19,708 INFO azoth_calibrate_ensemble: filetypes/python_sdist: using cached scores
2026-08-21 09:09:20,099 INFO azoth_calibrate_ensemble: filetypes/dmg: using cached scores
concurrent.futures.process._RemoteTraceback: 
"""
Traceback (most recent call last):
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/concurrent/futures/process.py", line 264, in _process_worker
    r = call_item.fn(*call_item.args, **call_item.kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1116, in _score_route_worker
    return _score_route(
           ^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 446, in _score_route
    spec_hash = _file_sha256(spec_path)
                ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 38, in _file_sha256
    with open(path, "rb") as f:
         ^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/home/t/collimator/out/models/azoth-candidate-filetypes-gem-422af3ead2991ec0/filetypes/gem/feature_spec.json'
"""

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1506, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1334, in main
    route_scores[general_offset + idx] = fut.result()
                                         ^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/concurrent/futures/_base.py", line 449, in result
    return self.__get_result()
           ^^^^^^^^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/concurrent/futures/_base.py", line 401, in __get_result
    raise self._exception
FileNotFoundError: [Errno 2] No such file or directory: '/home/t/collimator/out/models/azoth-candidate-filetypes-gem-422af3ead2991ec0/filetypes/gem/feature_spec.json'
make[1]: *** [Makefile:1247: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
