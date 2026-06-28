# Promote REJECTED — `8bdc8fb57a82aeba` on `filetypes/python`

Generated 2026-06-28T14:01:56Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T13-57-05_20260628T135705-promote-8bdc8fb57a82aeba_azoth-validate.log; tail: 2026-06-28 10:01:52,835 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.44% fp=5672 (FP/100M=752609.99)
2026-06-28 10:01:52,861 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.87% fp=5735 (FP/100M=760969.37)
2026-06-28 10:01:52,888 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.30% fp=6282 (FP/100M=833550.06)
2026-06-28 10:01:52,910 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=74.97% fp=6728 (FP/100M=892729.19)
2026-06-28 10:01:52,930 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.51% fp=7421 (FP/100M=984682.42)
2026-06-28 10:01:52,950 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.29% fp=9168 (FP/100M=1216489.48)
2026-06-28 10:01:52,971 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.05% fp=11218 (FP/100M=1488501.20)
2026-06-28 10:01:52,997 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=71.77% fp=11933 (FP/100M=1583373.58)
2026-06-28 10:01:53,021 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=73.88% fp=9048 (FP/100M=1200566.85)
2026-06-28 10:01:53,043 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=74.84% fp=9080 (FP/100M=1204812.88)
2026-06-28 10:01:53,064 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.93% fp=7514 (FP/100M=997022.47)
2026-06-28 10:01:53,085 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.01% fp=7018 (FP/100M=931208.90)
2026-06-28 10:01:53,106 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.87% fp=6436 (FP/100M=853984.11)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-python-8bdc8fb57a82aeba/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-python-8bdc8fb57a82aeba/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-python-8bdc8fb57a82aeba/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-python-8bdc8fb57a82aeba/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-python-8bdc8fb57a82aeba/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-python-8bdc8fb57a82aeba/route_policies.md \
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

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9920)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `8bdc8fb57a82aeba` | `9effa70847ad8816` | `65fbdf3569b21dab` |
| PR AUC | 0.9920 | 0.9901 | 0.9901 |
| ROC AUC | 0.9942 | 0.9935 | 0.9936 |
| F1 | 0.9579 | 0.9536 | 0.9512 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T13-57-05_20260628T135705-promote-8bdc8fb57a82aeba_azoth-validate.log; tail: 2026-06-28 10:01:52,835 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.44% fp=5672 (FP/100M=752609.99)
2026-06-28 10:01:52,861 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.87% fp=5735 (FP/100M=760969.37)
2026-06-28 10:01:52,888 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.30% fp=6282 (FP/100M=833550.06)
2026-06-28 10:01:52,910 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=74.97% fp=6728 (FP/100M=892729.19)
2026-06-28 10:01:52,930 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.51% fp=7421 (FP/100M=984682.42)
2026-06-28 10:01:52,950 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.29% fp=9168 (FP/100M=1216489.48)
2026-06-28 10:01:52,971 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.05% fp=11218 (FP/100M=1488501.20)
2026-06-28 10:01:52,997 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=71.77% fp=11933 (FP/100M=1583373.58)
2026-06-28 10:01:53,021 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=73.88% fp=9048 (FP/100M=1200566.85)
2026-06-28 10:01:53,043 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=74.84% fp=9080 (FP/100M=1204812.88)
2026-06-28 10:01:53,064 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.93% fp=7514 (FP/100M=997022.47)
2026-06-28 10:01:53,085 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.01% fp=7018 (FP/100M=931208.90)
2026-06-28 10:01:53,106 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.87% fp=6436 (FP/100M=853984.11)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-python-8bdc8fb57a82aeba/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-python-8bdc8fb57a82aeba/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-python-8bdc8fb57a82aeba/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-python-8bdc8fb57a82aeba/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-python-8bdc8fb57a82aeba/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-python-8bdc8fb57a82aeba/route_policies.md \
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
