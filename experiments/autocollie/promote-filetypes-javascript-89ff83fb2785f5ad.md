# Promote REJECTED — `89ff83fb2785f5ad` on `filetypes/javascript`

Generated 2026-06-28T12:33:11Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T12-23-10_20260628T122309-promote-89ff83fb2785f5ad_azoth-validate.log; tail: 2026-06-28 08:32:59,646 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=61.37% fp=116 (FP/100M=15391.88)
2026-06-28 08:32:59,672 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=62.02% fp=3211 (FP/100M=426063.23)
2026-06-28 08:32:59,699 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=64.58% fp=3280 (FP/100M=435218.75)
2026-06-28 08:32:59,725 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=65.32% fp=5340 (FP/100M=708557.36)
2026-06-28 08:32:59,752 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=65.88% fp=5415 (FP/100M=718509.00)
2026-06-28 08:32:59,777 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.65% fp=5490 (FP/100M=728460.65)
2026-06-28 08:32:59,802 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.84% fp=5572 (FP/100M=739341.12)
2026-06-28 08:32:59,825 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.16% fp=5629 (FP/100M=746904.37)
2026-06-28 08:32:59,848 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.51% fp=5686 (FP/100M=754467.63)
2026-06-28 08:32:59,870 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.95% fp=5749 (FP/100M=762827.01)
2026-06-28 08:32:59,893 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6275 (FP/100M=832621.24)
2026-06-28 08:32:59,919 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.02% fp=6725 (FP/100M=892331.13)
2026-06-28 08:32:59,941 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.62% fp=7403 (FP/100M=982294.03)
2026-06-28 08:32:59,966 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9143 (FP/100M=1213172.27)
2026-06-28 08:32:59,992 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.47% fp=11016 (FP/100M=1461698.10)
2026-06-28 08:33:00,018 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.19% fp=11709 (FP/100M=1553651.33)
2026-06-28 08:33:00,045 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8823 (FP/100M=1170711.90)
2026-06-28 08:33:00,072 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8855 (FP/100M=1174957.94)
2026-06-28 08:33:00,097 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7489 (FP/100M=993705.25)
2026-06-28 08:33:00,124 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.04% fp=6994 (FP/100M=928024.37)
2026-06-28 08:33:00,150 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6411 (FP/100M=850666.89)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-89ff83fb2785f5ad/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-89ff83fb2785f5ad/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-89ff83fb2785f5ad/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-89ff83fb2785f5ad/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-89ff83fb2785f5ad/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-89ff83fb2785f5ad/route_policies.md \
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

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9978)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `89ff83fb2785f5ad` | `ca64ce6dbfc85299` | `73f8b84e48148575` |
| PR AUC | 0.9978 | 0.9991 | 0.9991 |
| ROC AUC | 0.9974 | 0.9989 | 0.9989 |
| F1 | 0.9792 | 0.9877 | 0.9878 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T12-23-10_20260628T122309-promote-89ff83fb2785f5ad_azoth-validate.log; tail: 2026-06-28 08:32:59,646 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=61.37% fp=116 (FP/100M=15391.88)
2026-06-28 08:32:59,672 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=62.02% fp=3211 (FP/100M=426063.23)
2026-06-28 08:32:59,699 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=64.58% fp=3280 (FP/100M=435218.75)
2026-06-28 08:32:59,725 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=65.32% fp=5340 (FP/100M=708557.36)
2026-06-28 08:32:59,752 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=65.88% fp=5415 (FP/100M=718509.00)
2026-06-28 08:32:59,777 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.65% fp=5490 (FP/100M=728460.65)
2026-06-28 08:32:59,802 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.84% fp=5572 (FP/100M=739341.12)
2026-06-28 08:32:59,825 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.16% fp=5629 (FP/100M=746904.37)
2026-06-28 08:32:59,848 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.51% fp=5686 (FP/100M=754467.63)
2026-06-28 08:32:59,870 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.95% fp=5749 (FP/100M=762827.01)
2026-06-28 08:32:59,893 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6275 (FP/100M=832621.24)
2026-06-28 08:32:59,919 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.02% fp=6725 (FP/100M=892331.13)
2026-06-28 08:32:59,941 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.62% fp=7403 (FP/100M=982294.03)
2026-06-28 08:32:59,966 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9143 (FP/100M=1213172.27)
2026-06-28 08:32:59,992 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.47% fp=11016 (FP/100M=1461698.10)
2026-06-28 08:33:00,018 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.19% fp=11709 (FP/100M=1553651.33)
2026-06-28 08:33:00,045 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8823 (FP/100M=1170711.90)
2026-06-28 08:33:00,072 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8855 (FP/100M=1174957.94)
2026-06-28 08:33:00,097 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7489 (FP/100M=993705.25)
2026-06-28 08:33:00,124 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.04% fp=6994 (FP/100M=928024.37)
2026-06-28 08:33:00,150 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6411 (FP/100M=850666.89)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-89ff83fb2785f5ad/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-89ff83fb2785f5ad/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-89ff83fb2785f5ad/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-89ff83fb2785f5ad/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-89ff83fb2785f5ad/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-89ff83fb2785f5ad/route_policies.md \
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
