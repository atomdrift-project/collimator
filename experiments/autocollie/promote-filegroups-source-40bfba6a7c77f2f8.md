# Promote REJECTED — `40bfba6a7c77f2f8` on `filegroups/source`

Generated 2026-05-25T02:44:46Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T02-44-11_20260525T024301-promote-40bfba6a7c77f2f8_azoth-validate.log; tail: 2026-05-24 22:44:41,147 INFO azoth_calibrate_ensemble: filetypes/xls: using cached scores
2026-05-24 22:44:41,304 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-05-24 22:44:41,719 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-05-24 22:44:42,123 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-05-24 22:44:42,520 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-05-24 22:44:42,856 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-05-24 22:44:43,298 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-05-24 22:44:43,556 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-05-24 22:44:44,079 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-05-24 22:44:44,285 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-05-24 22:44:44,675 INFO azoth_calibrate_ensemble: filetypes/pptx: using cached scores
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
ValueError: ambiguous bundle layout in /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8/filegroups/source: both multi-seed (models/seed_*.{onnx,txt,json}) and legacy (model.{onnx,txt,json}) artifacts exist; remove one to disambiguate.
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
ValueError: ambiguous bundle layout in /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8/filegroups/source: both multi-seed (models/seed_*.{onnx,txt,json}) and legacy (model.{onnx,txt,json}) artifacts exist; remove one to disambiguate.
make[1]: *** [Makefile:1027: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9987)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `40bfba6a7c77f2f8` | `758b3d7304b3fdc6` | `ebc1c4fe04dea7b5` |
| PR AUC | 0.9987 | 0.9991 | 0.9991 |
| ROC AUC | 0.9980 | 0.9983 | 0.9984 |
| F1 | 0.9800 | 0.9807 | 0.9816 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T02-44-11_20260525T024301-promote-40bfba6a7c77f2f8_azoth-validate.log; tail: 2026-05-24 22:44:41,147 INFO azoth_calibrate_ensemble: filetypes/xls: using cached scores
2026-05-24 22:44:41,304 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-05-24 22:44:41,719 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-05-24 22:44:42,123 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-05-24 22:44:42,520 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-05-24 22:44:42,856 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-05-24 22:44:43,298 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-05-24 22:44:43,556 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-05-24 22:44:44,079 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-05-24 22:44:44,285 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-05-24 22:44:44,675 INFO azoth_calibrate_ensemble: filetypes/pptx: using cached scores
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
ValueError: ambiguous bundle layout in /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8/filegroups/source: both multi-seed (models/seed_*.{onnx,txt,json}) and legacy (model.{onnx,txt,json}) artifacts exist; remove one to disambiguate.
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
ValueError: ambiguous bundle layout in /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8/filegroups/source: both multi-seed (models/seed_*.{onnx,txt,json}) and legacy (model.{onnx,txt,json}) artifacts exist; remove one to disambiguate.
make[1]: *** [Makefile:1027: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
