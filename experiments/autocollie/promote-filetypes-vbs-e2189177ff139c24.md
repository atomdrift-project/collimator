# Promote REJECTED — `e2189177ff139c24` on `filetypes/vbs`

Generated 2026-06-28T06:21:28Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T06-17-01_20260628T061648-promote-e2189177ff139c24_azoth-validate.log; tail: 2026-06-28 02:21:24,175 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.94% fp=5621 (FP/100M=745842.86)
2026-06-28 02:21:24,201 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6179 (FP/100M=819883.13)
2026-06-28 02:21:24,225 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.02% fp=6630 (FP/100M=879725.71)
2026-06-28 02:21:24,249 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7431 (FP/100M=986009.31)
2026-06-28 02:21:24,274 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9027 (FP/100M=1197780.38)
2026-06-28 02:21:24,297 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.48% fp=10900 (FP/100M=1446306.21)
2026-06-28 02:21:24,322 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.20% fp=11588 (FP/100M=1537596.00)
2026-06-28 02:21:24,346 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8702 (FP/100M=1154656.58)
2026-06-28 02:21:24,371 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8734 (FP/100M=1158902.61)
2026-06-28 02:21:24,400 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7377 (FP/100M=978844.12)
2026-06-28 02:21:24,425 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.05% fp=6882 (FP/100M=913163.24)
2026-06-28 02:21:24,449 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6437 (FP/100M=854116.80)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-e2189177ff139c24/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-e2189177ff139c24/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-e2189177ff139c24/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-e2189177ff139c24/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-e2189177ff139c24/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-e2189177ff139c24/route_policies.md \
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

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9964)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e2189177ff139c24` | `d02bef8331ddc1e7` | `da9c2c8461340a5c` |
| PR AUC | 0.9964 | 0.9966 | 0.9965 |
| ROC AUC | 0.9865 | 0.9874 | 0.9873 |
| F1 | 0.9576 | 0.9547 | 0.9614 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T06-17-01_20260628T061648-promote-e2189177ff139c24_azoth-validate.log; tail: 2026-06-28 02:21:24,175 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.94% fp=5621 (FP/100M=745842.86)
2026-06-28 02:21:24,201 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6179 (FP/100M=819883.13)
2026-06-28 02:21:24,225 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.02% fp=6630 (FP/100M=879725.71)
2026-06-28 02:21:24,249 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7431 (FP/100M=986009.31)
2026-06-28 02:21:24,274 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9027 (FP/100M=1197780.38)
2026-06-28 02:21:24,297 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.48% fp=10900 (FP/100M=1446306.21)
2026-06-28 02:21:24,322 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.20% fp=11588 (FP/100M=1537596.00)
2026-06-28 02:21:24,346 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8702 (FP/100M=1154656.58)
2026-06-28 02:21:24,371 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8734 (FP/100M=1158902.61)
2026-06-28 02:21:24,400 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7377 (FP/100M=978844.12)
2026-06-28 02:21:24,425 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.05% fp=6882 (FP/100M=913163.24)
2026-06-28 02:21:24,449 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6437 (FP/100M=854116.80)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-e2189177ff139c24/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-e2189177ff139c24/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-e2189177ff139c24/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-e2189177ff139c24/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-e2189177ff139c24/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-e2189177ff139c24/route_policies.md \
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
