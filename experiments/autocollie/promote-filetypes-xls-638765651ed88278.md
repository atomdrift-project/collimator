# Promote REJECTED — `638765651ed88278` on `filetypes/xls`

Generated 2026-05-24T11:07:43Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-24T11-06-50_20260524T110636-promote-638765651ed88278_azoth-validate.log; tail: 2026-05-24 07:07:32,112 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-05-24 07:07:32,517 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-05-24 07:07:33,359 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-05-24 07:07:34,362 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-05-24 07:07:35,116 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-05-24 07:07:35,517 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-05-24 07:07:36,279 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-05-24 07:07:37,317 WARNING azoth_calibrate_ensemble: filetypes/xls: skipped 12121 rows absent from general score cache
2026-05-24 07:07:37,368 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-05-24 07:07:38,878 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-05-24 07:07:39,117 INFO azoth_calibrate_ensemble: filetypes/pptx: using cached scores
concurrent.futures.process._RemoteTraceback: 
"""
Traceback (most recent call last):
  File "/usr/lib/python3.14/concurrent/futures/process.py", line 254, in _process_worker
    r = call_item.fn(*call_item.args, **call_item.kwargs)
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1252, in _score_route_worker
    return _score_route(
        job["db_path"],
    ...<7 lines>...
        oof_route_scores_dir=job.get("oof_route_scores_dir"),
    )
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 434, in _score_route
    clf = bundle.Ensemble.load_bundle(output_dir)
  File "/home/t/collimator/src/collimator/bundle.py", line 223, in load_bundle
    files = model_files(bundle_dir)
  File "/home/t/collimator/src/collimator/bundle.py", line 122, in model_files
    raise ValueError(
    ...<3 lines>...
    )
ValueError: ambiguous bundle layout in /home/t/collimator/out/models/azoth-candidate-filetypes-xls-638765651ed88278/filetypes/xls: both multi-seed (models/seed_*.{onnx,txt,json}) and legacy (model.{onnx,txt,json}) artifacts exist; remove one to disambiguate.
"""

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1649, in <module>
    raise SystemExit(main())
                     ~~~~^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1444, in main
    route_scores[general_offset + idx] = fut.result()
                                         ~~~~~~~~~~^^
  File "/usr/lib/python3.14/concurrent/futures/_base.py", line 443, in result
    return self.__get_result()
           ~~~~~~~~~~~~~~~~~^^
  File "/usr/lib/python3.14/concurrent/futures/_base.py", line 395, in __get_result
    raise self._exception
ValueError: ambiguous bundle layout in /home/t/collimator/out/models/azoth-candidate-filetypes-xls-638765651ed88278/filetypes/xls: both multi-seed (models/seed_*.{onnx,txt,json}) and legacy (model.{onnx,txt,json}) artifacts exist; remove one to disambiguate.
make[1]: *** [Makefile:1027: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9999)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `638765651ed88278` | `3fc986025213e79f` | `10705231f85ae48c` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9996 | 0.9996 | 0.9996 |
| F1 | 0.9951 | 0.9932 | 0.9932 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-24T11-06-50_20260524T110636-promote-638765651ed88278_azoth-validate.log; tail: 2026-05-24 07:07:32,112 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-05-24 07:07:32,517 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-05-24 07:07:33,359 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-05-24 07:07:34,362 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-05-24 07:07:35,116 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-05-24 07:07:35,517 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-05-24 07:07:36,279 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-05-24 07:07:37,317 WARNING azoth_calibrate_ensemble: filetypes/xls: skipped 12121 rows absent from general score cache
2026-05-24 07:07:37,368 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-05-24 07:07:38,878 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-05-24 07:07:39,117 INFO azoth_calibrate_ensemble: filetypes/pptx: using cached scores
concurrent.futures.process._RemoteTraceback: 
"""
Traceback (most recent call last):
  File "/usr/lib/python3.14/concurrent/futures/process.py", line 254, in _process_worker
    r = call_item.fn(*call_item.args, **call_item.kwargs)
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1252, in _score_route_worker
    return _score_route(
        job["db_path"],
    ...<7 lines>...
        oof_route_scores_dir=job.get("oof_route_scores_dir"),
    )
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 434, in _score_route
    clf = bundle.Ensemble.load_bundle(output_dir)
  File "/home/t/collimator/src/collimator/bundle.py", line 223, in load_bundle
    files = model_files(bundle_dir)
  File "/home/t/collimator/src/collimator/bundle.py", line 122, in model_files
    raise ValueError(
    ...<3 lines>...
    )
ValueError: ambiguous bundle layout in /home/t/collimator/out/models/azoth-candidate-filetypes-xls-638765651ed88278/filetypes/xls: both multi-seed (models/seed_*.{onnx,txt,json}) and legacy (model.{onnx,txt,json}) artifacts exist; remove one to disambiguate.
"""

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1649, in <module>
    raise SystemExit(main())
                     ~~~~^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1444, in main
    route_scores[general_offset + idx] = fut.result()
                                         ~~~~~~~~~~^^
  File "/usr/lib/python3.14/concurrent/futures/_base.py", line 443, in result
    return self.__get_result()
           ~~~~~~~~~~~~~~~~~^^
  File "/usr/lib/python3.14/concurrent/futures/_base.py", line 395, in __get_result
    raise self._exception
ValueError: ambiguous bundle layout in /home/t/collimator/out/models/azoth-candidate-filetypes-xls-638765651ed88278/filetypes/xls: both multi-seed (models/seed_*.{onnx,txt,json}) and legacy (model.{onnx,txt,json}) artifacts exist; remove one to disambiguate.
make[1]: *** [Makefile:1027: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
