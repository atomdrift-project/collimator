# Promote REJECTED — `10d7edd475799b65` on `filetypes/ole`

Generated 2026-06-28T13:55:42Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T13-50-58_20260628T135057-promote-10d7edd475799b65_azoth-validate.log; tail: 2026-06-28 09:55:32,712 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=61.37% fp=124 (FP/100M=16453.39)
2026-06-28 09:55:32,734 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=61.99% fp=3222 (FP/100M=427522.81)
2026-06-28 09:55:32,756 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=64.54% fp=3305 (FP/100M=438535.97)
2026-06-28 09:55:32,776 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=65.28% fp=5371 (FP/100M=712670.70)
2026-06-28 09:55:32,797 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=65.84% fp=5441 (FP/100M=721958.91)
2026-06-28 09:55:32,818 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.61% fp=5506 (FP/100M=730583.67)
2026-06-28 09:55:32,838 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.79% fp=5567 (FP/100M=738677.68)
2026-06-28 09:55:32,859 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.02% fp=5622 (FP/100M=745975.55)
2026-06-28 09:55:32,881 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.45% fp=5689 (FP/100M=754865.69)
2026-06-28 09:55:32,904 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.88% fp=5752 (FP/100M=763225.08)
2026-06-28 09:55:32,927 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.31% fp=6291 (FP/100M=834744.26)
2026-06-28 09:55:32,949 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=74.97% fp=6734 (FP/100M=893525.32)
2026-06-28 09:55:32,969 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.51% fp=7415 (FP/100M=983886.29)
2026-06-28 09:55:32,989 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.29% fp=9099 (FP/100M=1207333.97)
2026-06-28 09:55:33,009 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.04% fp=10970 (FP/100M=1455594.42)
2026-06-28 09:55:33,030 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=71.76% fp=11659 (FP/100M=1547016.89)
2026-06-28 09:55:33,051 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=73.87% fp=8773 (FP/100M=1164077.47)
2026-06-28 09:55:33,072 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=74.84% fp=8805 (FP/100M=1168323.51)
2026-06-28 09:55:33,092 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.93% fp=7515 (FP/100M=997155.16)
2026-06-28 09:55:33,113 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.01% fp=7021 (FP/100M=931606.97)
2026-06-28 09:55:33,135 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.87% fp=6438 (FP/100M=854249.49)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-ole-10d7edd475799b65/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-ole-10d7edd475799b65/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-ole-10d7edd475799b65/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-ole-10d7edd475799b65/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-ole-10d7edd475799b65/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-ole-10d7edd475799b65/route_policies.md \
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

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9999)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `10d7edd475799b65` | `dc8ca8f0bb55ab23` | `dac4351375eee03d` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9991 | 0.9991 |
| F1 | 0.9935 | 0.9970 | 0.9970 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T13-50-58_20260628T135057-promote-10d7edd475799b65_azoth-validate.log; tail: 2026-06-28 09:55:32,712 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=61.37% fp=124 (FP/100M=16453.39)
2026-06-28 09:55:32,734 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=61.99% fp=3222 (FP/100M=427522.81)
2026-06-28 09:55:32,756 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=64.54% fp=3305 (FP/100M=438535.97)
2026-06-28 09:55:32,776 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=65.28% fp=5371 (FP/100M=712670.70)
2026-06-28 09:55:32,797 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=65.84% fp=5441 (FP/100M=721958.91)
2026-06-28 09:55:32,818 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.61% fp=5506 (FP/100M=730583.67)
2026-06-28 09:55:32,838 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.79% fp=5567 (FP/100M=738677.68)
2026-06-28 09:55:32,859 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.02% fp=5622 (FP/100M=745975.55)
2026-06-28 09:55:32,881 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.45% fp=5689 (FP/100M=754865.69)
2026-06-28 09:55:32,904 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.88% fp=5752 (FP/100M=763225.08)
2026-06-28 09:55:32,927 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.31% fp=6291 (FP/100M=834744.26)
2026-06-28 09:55:32,949 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=74.97% fp=6734 (FP/100M=893525.32)
2026-06-28 09:55:32,969 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.51% fp=7415 (FP/100M=983886.29)
2026-06-28 09:55:32,989 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.29% fp=9099 (FP/100M=1207333.97)
2026-06-28 09:55:33,009 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.04% fp=10970 (FP/100M=1455594.42)
2026-06-28 09:55:33,030 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=71.76% fp=11659 (FP/100M=1547016.89)
2026-06-28 09:55:33,051 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=73.87% fp=8773 (FP/100M=1164077.47)
2026-06-28 09:55:33,072 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=74.84% fp=8805 (FP/100M=1168323.51)
2026-06-28 09:55:33,092 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.93% fp=7515 (FP/100M=997155.16)
2026-06-28 09:55:33,113 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.01% fp=7021 (FP/100M=931606.97)
2026-06-28 09:55:33,135 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.87% fp=6438 (FP/100M=854249.49)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-ole-10d7edd475799b65/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-ole-10d7edd475799b65/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-ole-10d7edd475799b65/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-ole-10d7edd475799b65/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-ole-10d7edd475799b65/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-ole-10d7edd475799b65/route_policies.md \
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
