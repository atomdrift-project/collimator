# Promote REJECTED — `f631902369e1a0bd` on `filetypes/java_class`

Generated 2026-06-28T08:25:32Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T08-19-54_20260628T081952-promote-f631902369e1a0bd_azoth-validate.log; tail: 2026-06-28 04:25:28,794 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.65% fp=5492 (FP/100M=728726.03)
2026-06-28 04:25:28,818 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.84% fp=5555 (FP/100M=737085.41)
2026-06-28 04:25:28,841 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.16% fp=5615 (FP/100M=745046.73)
2026-06-28 04:25:28,864 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.52% fp=5676 (FP/100M=753140.74)
2026-06-28 04:25:28,899 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.95% fp=5740 (FP/100M=761632.81)
2026-06-28 04:25:28,926 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6297 (FP/100M=835540.39)
2026-06-28 04:25:28,958 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.03% fp=6748 (FP/100M=895382.97)
2026-06-28 04:25:28,981 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7427 (FP/100M=985478.55)
2026-06-28 04:25:29,004 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9159 (FP/100M=1215295.29)
2026-06-28 04:25:29,028 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.48% fp=11032 (FP/100M=1463821.11)
2026-06-28 04:25:29,051 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.20% fp=11724 (FP/100M=1555641.66)
2026-06-28 04:25:29,075 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8838 (FP/100M=1172702.23)
2026-06-28 04:25:29,098 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8870 (FP/100M=1176948.27)
2026-06-28 04:25:29,122 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7510 (FP/100M=996491.71)
2026-06-28 04:25:29,145 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.05% fp=7015 (FP/100M=930810.83)
2026-06-28 04:25:29,176 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6432 (FP/100M=853453.35)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-f631902369e1a0bd/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-f631902369e1a0bd/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-f631902369e1a0bd/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-f631902369e1a0bd/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-f631902369e1a0bd/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-f631902369e1a0bd/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1960, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1789, in main
    score_table = np.load(args.score_table)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^
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
make[1]: *** [Makefile:1338: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9794)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f631902369e1a0bd` | `3d91188c3b42f2f1` | `20f208de5ec81870` |
| PR AUC | 0.9794 | 0.9791 | 0.9805 |
| ROC AUC | 0.9962 | 0.9968 | 0.9971 |
| F1 | 0.6585 | 0.9079 | 0.9234 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T08-19-54_20260628T081952-promote-f631902369e1a0bd_azoth-validate.log; tail: 2026-06-28 04:25:28,794 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.65% fp=5492 (FP/100M=728726.03)
2026-06-28 04:25:28,818 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.84% fp=5555 (FP/100M=737085.41)
2026-06-28 04:25:28,841 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.16% fp=5615 (FP/100M=745046.73)
2026-06-28 04:25:28,864 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.52% fp=5676 (FP/100M=753140.74)
2026-06-28 04:25:28,899 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.95% fp=5740 (FP/100M=761632.81)
2026-06-28 04:25:28,926 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6297 (FP/100M=835540.39)
2026-06-28 04:25:28,958 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.03% fp=6748 (FP/100M=895382.97)
2026-06-28 04:25:28,981 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7427 (FP/100M=985478.55)
2026-06-28 04:25:29,004 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9159 (FP/100M=1215295.29)
2026-06-28 04:25:29,028 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.48% fp=11032 (FP/100M=1463821.11)
2026-06-28 04:25:29,051 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.20% fp=11724 (FP/100M=1555641.66)
2026-06-28 04:25:29,075 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8838 (FP/100M=1172702.23)
2026-06-28 04:25:29,098 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8870 (FP/100M=1176948.27)
2026-06-28 04:25:29,122 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7510 (FP/100M=996491.71)
2026-06-28 04:25:29,145 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.05% fp=7015 (FP/100M=930810.83)
2026-06-28 04:25:29,176 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6432 (FP/100M=853453.35)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-f631902369e1a0bd/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-f631902369e1a0bd/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-f631902369e1a0bd/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-f631902369e1a0bd/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-f631902369e1a0bd/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-f631902369e1a0bd/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1960, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1789, in main
    score_table = np.load(args.score_table)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^
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
make[1]: *** [Makefile:1338: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
