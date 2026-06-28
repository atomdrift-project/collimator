# Promote REJECTED — `e37f927afbd32e67` on `filegroups/scripts`

Generated 2026-06-28T13:17:03Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T13-04-21_20260628T130420-promote-e37f927afbd32e67_azoth-validate.log; tail: 2026-06-28 09:16:58,027 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.51% fp=5684 (FP/100M=754202.25)
2026-06-28 09:16:58,053 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.94% fp=5747 (FP/100M=762561.63)
2026-06-28 09:16:58,079 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6277 (FP/100M=832886.61)
2026-06-28 09:16:58,106 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.02% fp=6726 (FP/100M=892463.82)
2026-06-28 09:16:58,132 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7407 (FP/100M=982824.78)
2026-06-28 09:16:58,159 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9145 (FP/100M=1213437.64)
2026-06-28 09:16:58,185 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.47% fp=11018 (FP/100M=1461963.47)
2026-06-28 09:16:58,213 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.19% fp=11707 (FP/100M=1553385.95)
2026-06-28 09:16:58,240 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8821 (FP/100M=1170446.52)
2026-06-28 09:16:58,267 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8853 (FP/100M=1174692.56)
2026-06-28 09:16:58,293 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7492 (FP/100M=994103.32)
2026-06-28 09:16:58,320 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.04% fp=6997 (FP/100M=928422.44)
2026-06-28 09:16:58,346 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6414 (FP/100M=851064.96)
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e37f927afbd32e67/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e37f927afbd32e67/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e37f927afbd32e67/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e37f927afbd32e67/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e37f927afbd32e67/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e37f927afbd32e67/route_policies.md \
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
make[2]: *** [Makefile:1338: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9970)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e37f927afbd32e67` | `b2c82d803e6ef512` | `3bf77613a28d3c8c` |
| PR AUC | 0.9970 | 0.9954 | 0.9953 |
| ROC AUC | 0.9964 | 0.9963 | 0.9962 |
| F1 | 0.9723 | 0.9664 | 0.9670 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T13-04-21_20260628T130420-promote-e37f927afbd32e67_azoth-validate.log; tail: 2026-06-28 09:16:58,027 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.51% fp=5684 (FP/100M=754202.25)
2026-06-28 09:16:58,053 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.94% fp=5747 (FP/100M=762561.63)
2026-06-28 09:16:58,079 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6277 (FP/100M=832886.61)
2026-06-28 09:16:58,106 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.02% fp=6726 (FP/100M=892463.82)
2026-06-28 09:16:58,132 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7407 (FP/100M=982824.78)
2026-06-28 09:16:58,159 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9145 (FP/100M=1213437.64)
2026-06-28 09:16:58,185 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.47% fp=11018 (FP/100M=1461963.47)
2026-06-28 09:16:58,213 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.19% fp=11707 (FP/100M=1553385.95)
2026-06-28 09:16:58,240 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8821 (FP/100M=1170446.52)
2026-06-28 09:16:58,267 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8853 (FP/100M=1174692.56)
2026-06-28 09:16:58,293 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7492 (FP/100M=994103.32)
2026-06-28 09:16:58,320 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.04% fp=6997 (FP/100M=928422.44)
2026-06-28 09:16:58,346 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6414 (FP/100M=851064.96)
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e37f927afbd32e67/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e37f927afbd32e67/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e37f927afbd32e67/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e37f927afbd32e67/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e37f927afbd32e67/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-e37f927afbd32e67/route_policies.md \
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
make[2]: *** [Makefile:1338: azoth-validate] Error 1)
