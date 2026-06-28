# Promote REJECTED — `0dcf80ccc8faaeb2` on `filetypes/python`

Generated 2026-06-28T08:12:53Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T08-00-48_20260628T080047-promote-0dcf80ccc8faaeb2_azoth-validate.log; tail: 2026-06-28 04:12:41,559 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=61.37% fp=113 (FP/100M=14993.82)
2026-06-28 04:12:41,579 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=62.01% fp=3210 (FP/100M=425930.55)
2026-06-28 04:12:41,598 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=64.59% fp=3288 (FP/100M=436280.26)
2026-06-28 04:12:41,618 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=65.32% fp=5345 (FP/100M=709220.80)
2026-06-28 04:12:41,638 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=65.88% fp=5419 (FP/100M=719039.76)
2026-06-28 04:12:41,659 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.65% fp=5493 (FP/100M=728858.72)
2026-06-28 04:12:41,680 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.84% fp=5556 (FP/100M=737218.10)
2026-06-28 04:12:41,703 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.08% fp=5610 (FP/100M=744383.29)
2026-06-28 04:12:41,726 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.51% fp=5677 (FP/100M=753273.43)
2026-06-28 04:12:41,750 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.95% fp=5741 (FP/100M=761765.50)
2026-06-28 04:12:41,776 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6299 (FP/100M=835805.77)
2026-06-28 04:12:41,799 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.03% fp=6750 (FP/100M=895648.34)
2026-06-28 04:12:41,819 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7431 (FP/100M=986009.31)
2026-06-28 04:12:41,841 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9163 (FP/100M=1215826.04)
2026-06-28 04:12:41,860 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.48% fp=11036 (FP/100M=1464351.87)
2026-06-28 04:12:41,880 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.20% fp=11728 (FP/100M=1556172.41)
2026-06-28 04:12:41,900 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8842 (FP/100M=1173232.99)
2026-06-28 04:12:41,921 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8874 (FP/100M=1177479.02)
2026-06-28 04:12:41,943 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7514 (FP/100M=997022.47)
2026-06-28 04:12:41,966 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.05% fp=7019 (FP/100M=931341.59)
2026-06-28 04:12:41,989 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6436 (FP/100M=853984.11)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-python-0dcf80ccc8faaeb2/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-python-0dcf80ccc8faaeb2/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-python-0dcf80ccc8faaeb2/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-python-0dcf80ccc8faaeb2/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-python-0dcf80ccc8faaeb2/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-python-0dcf80ccc8faaeb2/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1960, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1793, in main
    routes = _route_arrays(score_table)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 48, in _route_arrays
    names = [str(name) for name in score_table["route_names"]]
                                   ~~~~~~~~~~~^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 245, in __getitem__
    with self.zip.open(key) as bytes:
         ^^^^^^^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/zipfile/__init__.py", line 1639, in open
    raise BadZipFile("Truncated file header")
zipfile.BadZipFile: Truncated file header
make[1]: *** [Makefile:1338: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9884)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0dcf80ccc8faaeb2` | `9effa70847ad8816` | `65fbdf3569b21dab` |
| PR AUC | 0.9884 | 0.9901 | 0.9901 |
| ROC AUC | 0.9923 | 0.9935 | 0.9936 |
| F1 | 0.9489 | 0.9536 | 0.9512 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T08-00-48_20260628T080047-promote-0dcf80ccc8faaeb2_azoth-validate.log; tail: 2026-06-28 04:12:41,559 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=61.37% fp=113 (FP/100M=14993.82)
2026-06-28 04:12:41,579 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=62.01% fp=3210 (FP/100M=425930.55)
2026-06-28 04:12:41,598 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=64.59% fp=3288 (FP/100M=436280.26)
2026-06-28 04:12:41,618 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=65.32% fp=5345 (FP/100M=709220.80)
2026-06-28 04:12:41,638 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=65.88% fp=5419 (FP/100M=719039.76)
2026-06-28 04:12:41,659 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.65% fp=5493 (FP/100M=728858.72)
2026-06-28 04:12:41,680 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.84% fp=5556 (FP/100M=737218.10)
2026-06-28 04:12:41,703 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.08% fp=5610 (FP/100M=744383.29)
2026-06-28 04:12:41,726 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.51% fp=5677 (FP/100M=753273.43)
2026-06-28 04:12:41,750 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.95% fp=5741 (FP/100M=761765.50)
2026-06-28 04:12:41,776 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6299 (FP/100M=835805.77)
2026-06-28 04:12:41,799 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.03% fp=6750 (FP/100M=895648.34)
2026-06-28 04:12:41,819 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7431 (FP/100M=986009.31)
2026-06-28 04:12:41,841 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9163 (FP/100M=1215826.04)
2026-06-28 04:12:41,860 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.48% fp=11036 (FP/100M=1464351.87)
2026-06-28 04:12:41,880 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.20% fp=11728 (FP/100M=1556172.41)
2026-06-28 04:12:41,900 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8842 (FP/100M=1173232.99)
2026-06-28 04:12:41,921 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8874 (FP/100M=1177479.02)
2026-06-28 04:12:41,943 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7514 (FP/100M=997022.47)
2026-06-28 04:12:41,966 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.05% fp=7019 (FP/100M=931341.59)
2026-06-28 04:12:41,989 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6436 (FP/100M=853984.11)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-python-0dcf80ccc8faaeb2/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-python-0dcf80ccc8faaeb2/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-python-0dcf80ccc8faaeb2/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-python-0dcf80ccc8faaeb2/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-python-0dcf80ccc8faaeb2/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-python-0dcf80ccc8faaeb2/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1960, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1793, in main
    routes = _route_arrays(score_table)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 48, in _route_arrays
    names = [str(name) for name in score_table["route_names"]]
                                   ~~~~~~~~~~~^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 245, in __getitem__
    with self.zip.open(key) as bytes:
         ^^^^^^^^^^^^^^^^^^
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/zipfile/__init__.py", line 1639, in open
    raise BadZipFile("Truncated file header")
zipfile.BadZipFile: Truncated file header
make[1]: *** [Makefile:1338: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
