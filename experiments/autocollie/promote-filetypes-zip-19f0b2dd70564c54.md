# Promote REJECTED — `19f0b2dd70564c54` on `filetypes/zip`

Generated 2026-06-28T13:02:34Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T12-54-33_20260628T125432-promote-19f0b2dd70564c54_azoth-validate.log; tail: 2026-06-28 09:02:32,328 INFO azoth_calibrate_ensemble: filetypes/php: refreshed 181389 rows in 10.3s (fetch 8.8s, filter 0.0s, load 0.2s, extract 0.0s, matrix 0.0s, predict 0.2s, write 0.1s; feature_cache_read 0.8s, feature_cache_write 0.0s; features=1323 nnz=6233443)
2026-06-28 09:02:33,004 INFO azoth_calibrate_ensemble: L0 on test: hostile recall=59.61% fp=69 (FP/100M=9155.52)
2026-06-28 09:02:33,024 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=59.62% fp=69 (FP/100M=9155.52)
2026-06-28 09:02:33,044 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=59.62% fp=69 (FP/100M=9155.52)
2026-06-28 09:02:33,063 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=59.63% fp=69 (FP/100M=9155.52)
2026-06-28 09:02:33,084 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=59.63% fp=69 (FP/100M=9155.52)
2026-06-28 09:02:33,106 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=59.64% fp=69 (FP/100M=9155.52)
2026-06-28 09:02:33,125 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=61.37% fp=116 (FP/100M=15391.88)
2026-06-28 09:02:33,146 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=62.02% fp=3211 (FP/100M=426063.23)
2026-06-28 09:02:33,168 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=64.58% fp=3280 (FP/100M=435218.75)
2026-06-28 09:02:33,189 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=65.32% fp=5340 (FP/100M=708557.36)
2026-06-28 09:02:33,211 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=65.88% fp=5417 (FP/100M=718774.38)
2026-06-28 09:02:33,232 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.65% fp=5490 (FP/100M=728460.65)
2026-06-28 09:02:33,254 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.84% fp=5570 (FP/100M=739075.74)
2026-06-28 09:02:33,275 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.07% fp=5621 (FP/100M=745842.86)
2026-06-28 09:02:33,297 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.51% fp=5684 (FP/100M=754202.25)
2026-06-28 09:02:33,320 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.94% fp=5747 (FP/100M=762561.63)
2026-06-28 09:02:33,341 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6277 (FP/100M=832886.61)
2026-06-28 09:02:33,361 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.02% fp=6726 (FP/100M=892463.82)
2026-06-28 09:02:33,381 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7407 (FP/100M=982824.78)
2026-06-28 09:02:33,403 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9145 (FP/100M=1213437.64)
2026-06-28 09:02:33,428 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.47% fp=11018 (FP/100M=1461963.47)
2026-06-28 09:02:33,452 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.19% fp=11707 (FP/100M=1553385.95)
2026-06-28 09:02:33,474 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8821 (FP/100M=1170446.52)
2026-06-28 09:02:33,496 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8853 (FP/100M=1174692.56)
2026-06-28 09:02:33,519 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7492 (FP/100M=994103.32)
2026-06-28 09:02:33,540 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.04% fp=6997 (FP/100M=928422.44)
2026-06-28 09:02:33,561 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6414 (FP/100M=851064.96)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1960, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1789, in main
    score_table = np.load(args.score_table)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 463, in load
    raise EOFError("No data left in file")
EOFError: No data left in file
make[2]: *** [Makefile:1338: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9996)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `19f0b2dd70564c54` | `32fcd545116dc2df` | `3f744812ce6a3f23` |
| PR AUC | 0.9996 | 0.9997 | 0.9997 |
| ROC AUC | 0.9973 | 0.9983 | 0.9983 |
| F1 | 0.9813 | 0.9949 | 0.9946 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T12-54-33_20260628T125432-promote-19f0b2dd70564c54_azoth-validate.log; tail: 2026-06-28 09:02:32,328 INFO azoth_calibrate_ensemble: filetypes/php: refreshed 181389 rows in 10.3s (fetch 8.8s, filter 0.0s, load 0.2s, extract 0.0s, matrix 0.0s, predict 0.2s, write 0.1s; feature_cache_read 0.8s, feature_cache_write 0.0s; features=1323 nnz=6233443)
2026-06-28 09:02:33,004 INFO azoth_calibrate_ensemble: L0 on test: hostile recall=59.61% fp=69 (FP/100M=9155.52)
2026-06-28 09:02:33,024 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=59.62% fp=69 (FP/100M=9155.52)
2026-06-28 09:02:33,044 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=59.62% fp=69 (FP/100M=9155.52)
2026-06-28 09:02:33,063 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=59.63% fp=69 (FP/100M=9155.52)
2026-06-28 09:02:33,084 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=59.63% fp=69 (FP/100M=9155.52)
2026-06-28 09:02:33,106 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=59.64% fp=69 (FP/100M=9155.52)
2026-06-28 09:02:33,125 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=61.37% fp=116 (FP/100M=15391.88)
2026-06-28 09:02:33,146 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=62.02% fp=3211 (FP/100M=426063.23)
2026-06-28 09:02:33,168 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=64.58% fp=3280 (FP/100M=435218.75)
2026-06-28 09:02:33,189 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=65.32% fp=5340 (FP/100M=708557.36)
2026-06-28 09:02:33,211 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=65.88% fp=5417 (FP/100M=718774.38)
2026-06-28 09:02:33,232 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.65% fp=5490 (FP/100M=728460.65)
2026-06-28 09:02:33,254 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.84% fp=5570 (FP/100M=739075.74)
2026-06-28 09:02:33,275 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.07% fp=5621 (FP/100M=745842.86)
2026-06-28 09:02:33,297 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.51% fp=5684 (FP/100M=754202.25)
2026-06-28 09:02:33,320 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.94% fp=5747 (FP/100M=762561.63)
2026-06-28 09:02:33,341 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6277 (FP/100M=832886.61)
2026-06-28 09:02:33,361 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.02% fp=6726 (FP/100M=892463.82)
2026-06-28 09:02:33,381 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7407 (FP/100M=982824.78)
2026-06-28 09:02:33,403 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9145 (FP/100M=1213437.64)
2026-06-28 09:02:33,428 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.47% fp=11018 (FP/100M=1461963.47)
2026-06-28 09:02:33,452 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.19% fp=11707 (FP/100M=1553385.95)
2026-06-28 09:02:33,474 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8821 (FP/100M=1170446.52)
2026-06-28 09:02:33,496 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8853 (FP/100M=1174692.56)
2026-06-28 09:02:33,519 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7492 (FP/100M=994103.32)
2026-06-28 09:02:33,540 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.04% fp=6997 (FP/100M=928422.44)
2026-06-28 09:02:33,561 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6414 (FP/100M=851064.96)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-zip-19f0b2dd70564c54/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1960, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_route_policy_search.py", line 1789, in main
    score_table = np.load(args.score_table)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/numpy/lib/_npyio_impl.py", line 463, in load
    raise EOFError("No data left in file")
EOFError: No data left in file
make[2]: *** [Makefile:1338: azoth-validate] Error 1)
