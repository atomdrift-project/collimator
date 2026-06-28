# Promote REJECTED — `58e373ffce466bb9` on `filetypes/ole`

Generated 2026-06-28T12:34:51Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T12-28-25_20260628T122746-promote-58e373ffce466bb9_azoth-validate.log; tail: 2026-06-28 08:34:45,915 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.51% fp=5684 (FP/100M=754202.25)
2026-06-28 08:34:45,949 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.94% fp=5747 (FP/100M=762561.63)
2026-06-28 08:34:45,983 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6277 (FP/100M=832886.61)
2026-06-28 08:34:46,012 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.02% fp=6727 (FP/100M=892596.50)
2026-06-28 08:34:46,038 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7406 (FP/100M=982692.09)
2026-06-28 08:34:46,063 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9144 (FP/100M=1213304.96)
2026-06-28 08:34:46,089 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.47% fp=11017 (FP/100M=1461830.78)
2026-06-28 08:34:46,114 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.19% fp=11711 (FP/100M=1553916.70)
2026-06-28 08:34:46,140 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8825 (FP/100M=1170977.28)
2026-06-28 08:34:46,166 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8857 (FP/100M=1175223.31)
2026-06-28 08:34:46,192 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7491 (FP/100M=993970.63)
2026-06-28 08:34:46,218 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.04% fp=6996 (FP/100M=928289.75)
2026-06-28 08:34:46,245 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6413 (FP/100M=850932.27)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-ole-58e373ffce466bb9/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-ole-58e373ffce466bb9/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-ole-58e373ffce466bb9/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-ole-58e373ffce466bb9/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-ole-58e373ffce466bb9/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-ole-58e373ffce466bb9/route_policies.md \
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

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9964)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `58e373ffce466bb9` | `850caaecad9dc395` | `d41132947888f70e` |
| PR AUC | 0.9964 | 0.9967 | 0.9968 |
| ROC AUC | 0.9890 | 0.9895 | 0.9897 |
| F1 | 0.9683 | 0.9603 | 0.9647 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T12-28-25_20260628T122746-promote-58e373ffce466bb9_azoth-validate.log; tail: 2026-06-28 08:34:45,915 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.51% fp=5684 (FP/100M=754202.25)
2026-06-28 08:34:45,949 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.94% fp=5747 (FP/100M=762561.63)
2026-06-28 08:34:45,983 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6277 (FP/100M=832886.61)
2026-06-28 08:34:46,012 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.02% fp=6727 (FP/100M=892596.50)
2026-06-28 08:34:46,038 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7406 (FP/100M=982692.09)
2026-06-28 08:34:46,063 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9144 (FP/100M=1213304.96)
2026-06-28 08:34:46,089 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.47% fp=11017 (FP/100M=1461830.78)
2026-06-28 08:34:46,114 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.19% fp=11711 (FP/100M=1553916.70)
2026-06-28 08:34:46,140 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8825 (FP/100M=1170977.28)
2026-06-28 08:34:46,166 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8857 (FP/100M=1175223.31)
2026-06-28 08:34:46,192 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7491 (FP/100M=993970.63)
2026-06-28 08:34:46,218 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.04% fp=6996 (FP/100M=928289.75)
2026-06-28 08:34:46,245 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6413 (FP/100M=850932.27)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-ole-58e373ffce466bb9/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-ole-58e373ffce466bb9/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-ole-58e373ffce466bb9/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-ole-58e373ffce466bb9/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-ole-58e373ffce466bb9/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-ole-58e373ffce466bb9/route_policies.md \
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
