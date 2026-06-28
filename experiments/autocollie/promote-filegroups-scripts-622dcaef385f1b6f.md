# Promote REJECTED — `622dcaef385f1b6f` on `filegroups/scripts`

Generated 2026-06-28T13:22:29Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T13-17-12_20260628T131711-promote-622dcaef385f1b6f_azoth-validate.log; tail: 2026-06-28 09:22:19,940 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=59.64% fp=69 (FP/100M=9155.52)
2026-06-28 09:22:19,962 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=61.37% fp=116 (FP/100M=15391.88)
2026-06-28 09:22:19,984 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=62.02% fp=3211 (FP/100M=426063.23)
2026-06-28 09:22:20,005 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=64.58% fp=3280 (FP/100M=435218.75)
2026-06-28 09:22:20,027 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=65.32% fp=5340 (FP/100M=708557.36)
2026-06-28 09:22:20,048 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=65.88% fp=5417 (FP/100M=718774.38)
2026-06-28 09:22:20,070 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.65% fp=5490 (FP/100M=728460.65)
2026-06-28 09:22:20,093 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.84% fp=5570 (FP/100M=739075.74)
2026-06-28 09:22:20,115 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.07% fp=5621 (FP/100M=745842.86)
2026-06-28 09:22:20,135 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.51% fp=5684 (FP/100M=754202.25)
2026-06-28 09:22:20,157 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.94% fp=5747 (FP/100M=762561.63)
2026-06-28 09:22:20,177 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6277 (FP/100M=832886.61)
2026-06-28 09:22:20,199 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.02% fp=6726 (FP/100M=892463.82)
2026-06-28 09:22:20,220 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7407 (FP/100M=982824.78)
2026-06-28 09:22:20,241 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9130 (FP/100M=1211447.31)
2026-06-28 09:22:20,263 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.47% fp=11003 (FP/100M=1459973.14)
2026-06-28 09:22:20,287 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.19% fp=11692 (FP/100M=1551395.62)
2026-06-28 09:22:20,310 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8806 (FP/100M=1168456.19)
2026-06-28 09:22:20,333 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8838 (FP/100M=1172702.23)
2026-06-28 09:22:20,355 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7477 (FP/100M=992112.99)
2026-06-28 09:22:20,376 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.04% fp=6982 (FP/100M=926432.11)
2026-06-28 09:22:20,399 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6399 (FP/100M=849074.63)
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-622dcaef385f1b6f/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-622dcaef385f1b6f/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-622dcaef385f1b6f/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-622dcaef385f1b6f/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-622dcaef385f1b6f/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-622dcaef385f1b6f/route_policies.md \
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
make[2]: *** [Makefile:1338: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9961)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `622dcaef385f1b6f` | `b2c82d803e6ef512` | `3bf77613a28d3c8c` |
| PR AUC | 0.9961 | 0.9954 | 0.9953 |
| ROC AUC | 0.9956 | 0.9963 | 0.9962 |
| F1 | 0.9683 | 0.9664 | 0.9670 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T13-17-12_20260628T131711-promote-622dcaef385f1b6f_azoth-validate.log; tail: 2026-06-28 09:22:19,940 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=59.64% fp=69 (FP/100M=9155.52)
2026-06-28 09:22:19,962 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=61.37% fp=116 (FP/100M=15391.88)
2026-06-28 09:22:19,984 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=62.02% fp=3211 (FP/100M=426063.23)
2026-06-28 09:22:20,005 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=64.58% fp=3280 (FP/100M=435218.75)
2026-06-28 09:22:20,027 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=65.32% fp=5340 (FP/100M=708557.36)
2026-06-28 09:22:20,048 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=65.88% fp=5417 (FP/100M=718774.38)
2026-06-28 09:22:20,070 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.65% fp=5490 (FP/100M=728460.65)
2026-06-28 09:22:20,093 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.84% fp=5570 (FP/100M=739075.74)
2026-06-28 09:22:20,115 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.07% fp=5621 (FP/100M=745842.86)
2026-06-28 09:22:20,135 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.51% fp=5684 (FP/100M=754202.25)
2026-06-28 09:22:20,157 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.94% fp=5747 (FP/100M=762561.63)
2026-06-28 09:22:20,177 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6277 (FP/100M=832886.61)
2026-06-28 09:22:20,199 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.02% fp=6726 (FP/100M=892463.82)
2026-06-28 09:22:20,220 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7407 (FP/100M=982824.78)
2026-06-28 09:22:20,241 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9130 (FP/100M=1211447.31)
2026-06-28 09:22:20,263 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.47% fp=11003 (FP/100M=1459973.14)
2026-06-28 09:22:20,287 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.19% fp=11692 (FP/100M=1551395.62)
2026-06-28 09:22:20,310 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8806 (FP/100M=1168456.19)
2026-06-28 09:22:20,333 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8838 (FP/100M=1172702.23)
2026-06-28 09:22:20,355 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7477 (FP/100M=992112.99)
2026-06-28 09:22:20,376 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.04% fp=6982 (FP/100M=926432.11)
2026-06-28 09:22:20,399 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6399 (FP/100M=849074.63)
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-622dcaef385f1b6f/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-622dcaef385f1b6f/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-622dcaef385f1b6f/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-622dcaef385f1b6f/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-622dcaef385f1b6f/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-622dcaef385f1b6f/route_policies.md \
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
make[2]: *** [Makefile:1338: azoth-validate] Error 1)
