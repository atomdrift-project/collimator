# Promote REJECTED — `b6fa08ca50a9ac54` on `filetypes/pe`

Generated 2026-05-24T14:39:09Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-24T14-37-46_20260524T141048-promote-b6fa08ca50a9ac54_azoth-validate.log; tail: 2026-05-24 10:39:05,621 INFO azoth_calibrate_ensemble: filetypes/xls: using cached scores
2026-05-24 10:39:05,826 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-05-24 10:39:06,037 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-05-24 10:39:06,226 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-05-24 10:39:06,460 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-05-24 10:39:06,677 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-05-24 10:39:06,869 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-05-24 10:39:07,117 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-05-24 10:39:07,282 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-05-24 10:39:07,583 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-05-24 10:39:07,708 INFO azoth_calibrate_ensemble: filetypes/pptx: using cached scores
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
ValueError: ambiguous bundle layout in /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/filetypes/pe: both multi-seed (models/seed_*.{onnx,txt,json}) and legacy (model.{onnx,txt,json}) artifacts exist; remove one to disambiguate.
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
ValueError: ambiguous bundle layout in /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/filetypes/pe: both multi-seed (models/seed_*.{onnx,txt,json}) and legacy (model.{onnx,txt,json}) artifacts exist; remove one to disambiguate.
make[1]: *** [Makefile:1027: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9997)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b6fa08ca50a9ac54` | `96a4083ae34b084c` | `7b8a38aeb675012b` |
| PR AUC | 0.9997 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9999 | 0.9999 |
| F1 | 0.9918 | 0.9989 | 0.9978 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-24T14-37-46_20260524T141048-promote-b6fa08ca50a9ac54_azoth-validate.log; tail: 2026-05-24 10:39:05,621 INFO azoth_calibrate_ensemble: filetypes/xls: using cached scores
2026-05-24 10:39:05,826 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-05-24 10:39:06,037 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-05-24 10:39:06,226 INFO azoth_calibrate_ensemble: filetypes/groovy: using cached scores
2026-05-24 10:39:06,460 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-05-24 10:39:06,677 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-05-24 10:39:06,869 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-05-24 10:39:07,117 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-05-24 10:39:07,282 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-05-24 10:39:07,583 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-05-24 10:39:07,708 INFO azoth_calibrate_ensemble: filetypes/pptx: using cached scores
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
ValueError: ambiguous bundle layout in /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/filetypes/pe: both multi-seed (models/seed_*.{onnx,txt,json}) and legacy (model.{onnx,txt,json}) artifacts exist; remove one to disambiguate.
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
ValueError: ambiguous bundle layout in /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/filetypes/pe: both multi-seed (models/seed_*.{onnx,txt,json}) and legacy (model.{onnx,txt,json}) artifacts exist; remove one to disambiguate.
make[1]: *** [Makefile:1027: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
