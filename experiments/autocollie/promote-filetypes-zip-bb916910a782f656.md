# Promote REJECTED — `bb916910a782f656` on `filetypes/zip`

Generated 2026-06-28T13:59:04Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T13-55-44_20260628T135543-promote-bb916910a782f656_azoth-validate.log; tail: 2026-06-28 09:59:01,314 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.87% fp=5735 (FP/100M=760969.37)
2026-06-28 09:59:01,339 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.30% fp=6282 (FP/100M=833550.06)
2026-06-28 09:59:01,367 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=74.97% fp=6728 (FP/100M=892729.19)
2026-06-28 09:59:01,398 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.51% fp=7421 (FP/100M=984682.42)
2026-06-28 09:59:01,428 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.29% fp=9168 (FP/100M=1216489.48)
2026-06-28 09:59:01,459 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.05% fp=11218 (FP/100M=1488501.20)
2026-06-28 09:59:01,489 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=71.77% fp=11933 (FP/100M=1583373.58)
2026-06-28 09:59:01,520 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=73.88% fp=9047 (FP/100M=1200434.16)
2026-06-28 09:59:01,551 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=74.84% fp=9079 (FP/100M=1204680.19)
2026-06-28 09:59:01,582 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.93% fp=7512 (FP/100M=996757.09)
2026-06-28 09:59:01,614 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.01% fp=7017 (FP/100M=931076.21)
2026-06-28 09:59:01,646 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.87% fp=6434 (FP/100M=853718.73)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-zip-bb916910a782f656/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-zip-bb916910a782f656/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-zip-bb916910a782f656/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-zip-bb916910a782f656/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-zip-bb916910a782f656/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-zip-bb916910a782f656/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1960, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1791, in main
    file_types = np.asarray([str(value) for value in score_table["file_types"]])
                                                     ~~~~~~~~~~~^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 257, in __getitem__
    return format.read_array(
           ^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_format_impl.py", line 869, in read_array
    data = _read_bytes(fp, read_size, "array data")
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_format_impl.py", line 1013, in _read_bytes
    r = fp.read(size - len(data))
        ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/zipfile/__init__.py", line 1008, in read
    data = self._read1(n)
           ^^^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/zipfile/__init__.py", line 1076, in _read1
    data += self._read2(n - len(data))
            ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/zipfile/__init__.py", line 1111, in _read2
    raise EOFError
EOFError
make[1]: *** [Makefile:1338: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9995)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `bb916910a782f656` | `32fcd545116dc2df` | `3f744812ce6a3f23` |
| PR AUC | 0.9995 | 0.9997 | 0.9997 |
| ROC AUC | 0.9971 | 0.9983 | 0.9983 |
| F1 | 0.9870 | 0.9949 | 0.9946 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T13-55-44_20260628T135543-promote-bb916910a782f656_azoth-validate.log; tail: 2026-06-28 09:59:01,314 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.87% fp=5735 (FP/100M=760969.37)
2026-06-28 09:59:01,339 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.30% fp=6282 (FP/100M=833550.06)
2026-06-28 09:59:01,367 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=74.97% fp=6728 (FP/100M=892729.19)
2026-06-28 09:59:01,398 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.51% fp=7421 (FP/100M=984682.42)
2026-06-28 09:59:01,428 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.29% fp=9168 (FP/100M=1216489.48)
2026-06-28 09:59:01,459 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.05% fp=11218 (FP/100M=1488501.20)
2026-06-28 09:59:01,489 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=71.77% fp=11933 (FP/100M=1583373.58)
2026-06-28 09:59:01,520 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=73.88% fp=9047 (FP/100M=1200434.16)
2026-06-28 09:59:01,551 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=74.84% fp=9079 (FP/100M=1204680.19)
2026-06-28 09:59:01,582 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.93% fp=7512 (FP/100M=996757.09)
2026-06-28 09:59:01,614 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.01% fp=7017 (FP/100M=931076.21)
2026-06-28 09:59:01,646 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.87% fp=6434 (FP/100M=853718.73)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-zip-bb916910a782f656/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-zip-bb916910a782f656/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-zip-bb916910a782f656/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-zip-bb916910a782f656/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-zip-bb916910a782f656/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-zip-bb916910a782f656/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1960, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1791, in main
    file_types = np.asarray([str(value) for value in score_table["file_types"]])
                                                     ~~~~~~~~~~~^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 257, in __getitem__
    return format.read_array(
           ^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_format_impl.py", line 869, in read_array
    data = _read_bytes(fp, read_size, "array data")
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_format_impl.py", line 1013, in _read_bytes
    r = fp.read(size - len(data))
        ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/zipfile/__init__.py", line 1008, in read
    data = self._read1(n)
           ^^^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/zipfile/__init__.py", line 1076, in _read1
    data += self._read2(n - len(data))
            ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/zipfile/__init__.py", line 1111, in _read2
    raise EOFError
EOFError
make[1]: *** [Makefile:1338: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
