# Promote REJECTED — `b5c3939397dfdb31` on `filetypes/php`

Generated 2026-06-28T08:16:21Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T08-07-48_20260628T080747-promote-b5c3939397dfdb31_azoth-validate.log; tail: 2026-06-28 04:16:13,901 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.95% fp=5740 (FP/100M=761632.81)
2026-06-28 04:16:13,924 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6297 (FP/100M=835540.39)
2026-06-28 04:16:13,946 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.03% fp=6747 (FP/100M=895250.28)
2026-06-28 04:16:13,968 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7427 (FP/100M=985478.55)
2026-06-28 04:16:13,991 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9159 (FP/100M=1215295.29)
2026-06-28 04:16:14,014 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.48% fp=11032 (FP/100M=1463821.11)
2026-06-28 04:16:14,037 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.20% fp=11724 (FP/100M=1555641.66)
2026-06-28 04:16:14,059 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8838 (FP/100M=1172702.23)
2026-06-28 04:16:14,080 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8870 (FP/100M=1176948.27)
2026-06-28 04:16:14,107 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7510 (FP/100M=996491.71)
2026-06-28 04:16:14,139 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.05% fp=7015 (FP/100M=930810.83)
2026-06-28 04:16:14,166 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6432 (FP/100M=853453.35)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-php-b5c3939397dfdb31/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-php-b5c3939397dfdb31/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-php-b5c3939397dfdb31/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-php-b5c3939397dfdb31/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-php-b5c3939397dfdb31/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-php-b5c3939397dfdb31/route_policies.md \
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

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9878)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b5c3939397dfdb31` | `bd0f79ed8e46d2d8` | `7251bf6da0788cf3` |
| PR AUC | 0.9878 | 0.9862 | 0.9856 |
| ROC AUC | 0.9956 | 0.9962 | 0.9959 |
| F1 | 0.9558 | 0.9567 | 0.9526 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T08-07-48_20260628T080747-promote-b5c3939397dfdb31_azoth-validate.log; tail: 2026-06-28 04:16:13,901 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.95% fp=5740 (FP/100M=761632.81)
2026-06-28 04:16:13,924 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6297 (FP/100M=835540.39)
2026-06-28 04:16:13,946 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.03% fp=6747 (FP/100M=895250.28)
2026-06-28 04:16:13,968 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7427 (FP/100M=985478.55)
2026-06-28 04:16:13,991 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9159 (FP/100M=1215295.29)
2026-06-28 04:16:14,014 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.48% fp=11032 (FP/100M=1463821.11)
2026-06-28 04:16:14,037 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.20% fp=11724 (FP/100M=1555641.66)
2026-06-28 04:16:14,059 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8838 (FP/100M=1172702.23)
2026-06-28 04:16:14,080 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8870 (FP/100M=1176948.27)
2026-06-28 04:16:14,107 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7510 (FP/100M=996491.71)
2026-06-28 04:16:14,139 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.05% fp=7015 (FP/100M=930810.83)
2026-06-28 04:16:14,166 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6432 (FP/100M=853453.35)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-php-b5c3939397dfdb31/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-php-b5c3939397dfdb31/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-php-b5c3939397dfdb31/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-php-b5c3939397dfdb31/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-php-b5c3939397dfdb31/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-php-b5c3939397dfdb31/route_policies.md \
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
