# Promote REJECTED — `b2c5ebae60db29bf` on `filegroups/documents`

Generated 2026-06-28T13:57:02Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T13-53-14_20260628T135210-promote-b2c5ebae60db29bf_azoth-validate.log; tail: 2026-06-28 09:57:01,181 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=65.83% fp=5417 (FP/100M=718774.38)
2026-06-28 09:57:01,201 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.60% fp=5484 (FP/100M=727664.52)
2026-06-28 09:57:01,220 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.79% fp=5549 (FP/100M=736289.28)
2026-06-28 09:57:01,240 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.01% fp=5604 (FP/100M=743587.16)
2026-06-28 09:57:01,261 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.44% fp=5672 (FP/100M=752609.99)
2026-06-28 09:57:01,280 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.87% fp=5735 (FP/100M=760969.37)
2026-06-28 09:57:01,301 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.30% fp=6282 (FP/100M=833550.06)
2026-06-28 09:57:01,323 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=74.97% fp=6728 (FP/100M=892729.19)
2026-06-28 09:57:01,349 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.51% fp=7421 (FP/100M=984682.42)
2026-06-28 09:57:01,373 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.29% fp=9168 (FP/100M=1216489.48)
2026-06-28 09:57:01,398 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.05% fp=11218 (FP/100M=1488501.20)
2026-06-28 09:57:01,423 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=71.77% fp=11933 (FP/100M=1583373.58)
2026-06-28 09:57:01,448 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=73.88% fp=9047 (FP/100M=1200434.16)
2026-06-28 09:57:01,472 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=74.84% fp=9079 (FP/100M=1204680.19)
2026-06-28 09:57:01,497 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.93% fp=7512 (FP/100M=996757.09)
2026-06-28 09:57:01,522 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.01% fp=7017 (FP/100M=931076.21)
2026-06-28 09:57:01,547 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.87% fp=6434 (FP/100M=853718.73)
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-documents-b2c5ebae60db29bf/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filegroups-documents-b2c5ebae60db29bf/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-documents-b2c5ebae60db29bf/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-documents-b2c5ebae60db29bf/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filegroups-documents-b2c5ebae60db29bf/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filegroups-documents-b2c5ebae60db29bf/route_policies.md \
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
make[2]: *** [Makefile:1338: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9295)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b2c5ebae60db29bf` | `266bdd9b127df2fc` | `942278629dc66e59` |
| PR AUC | 0.9295 | 0.9799 | 0.9800 |
| ROC AUC | 0.8943 | 0.9068 | 0.9140 |
| F1 | 0.8381 | 0.9117 | 0.9181 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T13-53-14_20260628T135210-promote-b2c5ebae60db29bf_azoth-validate.log; tail: 2026-06-28 09:57:01,181 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=65.83% fp=5417 (FP/100M=718774.38)
2026-06-28 09:57:01,201 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.60% fp=5484 (FP/100M=727664.52)
2026-06-28 09:57:01,220 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.79% fp=5549 (FP/100M=736289.28)
2026-06-28 09:57:01,240 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.01% fp=5604 (FP/100M=743587.16)
2026-06-28 09:57:01,261 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.44% fp=5672 (FP/100M=752609.99)
2026-06-28 09:57:01,280 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.87% fp=5735 (FP/100M=760969.37)
2026-06-28 09:57:01,301 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.30% fp=6282 (FP/100M=833550.06)
2026-06-28 09:57:01,323 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=74.97% fp=6728 (FP/100M=892729.19)
2026-06-28 09:57:01,349 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.51% fp=7421 (FP/100M=984682.42)
2026-06-28 09:57:01,373 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.29% fp=9168 (FP/100M=1216489.48)
2026-06-28 09:57:01,398 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.05% fp=11218 (FP/100M=1488501.20)
2026-06-28 09:57:01,423 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=71.77% fp=11933 (FP/100M=1583373.58)
2026-06-28 09:57:01,448 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=73.88% fp=9047 (FP/100M=1200434.16)
2026-06-28 09:57:01,472 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=74.84% fp=9079 (FP/100M=1204680.19)
2026-06-28 09:57:01,497 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.93% fp=7512 (FP/100M=996757.09)
2026-06-28 09:57:01,522 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.01% fp=7017 (FP/100M=931076.21)
2026-06-28 09:57:01,547 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.87% fp=6434 (FP/100M=853718.73)
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-documents-b2c5ebae60db29bf/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filegroups-documents-b2c5ebae60db29bf/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-documents-b2c5ebae60db29bf/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-documents-b2c5ebae60db29bf/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filegroups-documents-b2c5ebae60db29bf/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filegroups-documents-b2c5ebae60db29bf/route_policies.md \
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
make[2]: *** [Makefile:1338: azoth-validate] Error 1)
