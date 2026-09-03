# Promote REJECTED — `0d83a0d8d99643d6` on `filetypes/kotlin`

Generated 2026-08-21T13:28:09Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-08-21T13-15-21_20260821T131429-promote-0d83a0d8d99643d6_azoth-validate.log; tail: 2026-08-21 09:25:39,172 INFO azoth_calibrate_ensemble: L175 hostile recall=74.48% fp=86
2026-08-21 09:25:39,234 INFO azoth_calibrate_ensemble: L200 hostile recall=74.55% fp=86
2026-08-21 09:25:39,301 INFO azoth_calibrate_ensemble: L250 hostile recall=74.61% fp=87
2026-08-21 09:25:39,360 INFO azoth_calibrate_ensemble: L300 hostile recall=74.65% fp=88
2026-08-21 09:25:39,420 INFO azoth_calibrate_ensemble: L500 hostile recall=75.04% fp=92
2026-08-21 09:25:39,485 INFO azoth_calibrate_ensemble: L750 hostile recall=75.20% fp=102
2026-08-21 09:25:39,548 INFO azoth_calibrate_ensemble: L1000 hostile recall=75.37% fp=108
2026-08-21 09:25:39,622 INFO azoth_calibrate_ensemble: L1250 hostile recall=75.49% fp=113
2026-08-21 09:25:39,683 INFO azoth_calibrate_ensemble: L1500 hostile recall=75.61% fp=121
2026-08-21 09:25:39,743 INFO azoth_calibrate_ensemble: L1750 hostile recall=75.82% fp=128
2026-08-21 09:25:39,803 INFO azoth_calibrate_ensemble: L2000 hostile recall=76.00% fp=135
2026-08-21 09:25:39,861 INFO azoth_calibrate_ensemble: L2250 hostile recall=76.12% fp=144
2026-08-21 09:25:39,915 INFO azoth_calibrate_ensemble: L2500 hostile recall=76.24% fp=150
2026-08-21 09:25:39,970 INFO azoth_calibrate_ensemble: L3000 hostile recall=76.41% fp=169
2026-08-21 09:25:40,025 INFO azoth_calibrate_ensemble: L4000 hostile recall=76.79% fp=196
2026-08-21 09:25:40,083 INFO azoth_calibrate_ensemble: L5000 hostile recall=77.17% fp=223
2026-08-21 09:25:40,142 INFO azoth_calibrate_ensemble: L6000 hostile recall=77.58% fp=252
2026-08-21 09:25:40,210 INFO azoth_calibrate_ensemble: L7500 hostile recall=77.89% fp=279
2026-08-21 09:25:40,269 INFO azoth_calibrate_ensemble: L10000 hostile recall=78.41% fp=365
2026-08-21 09:25:40,323 INFO azoth_calibrate_ensemble: L15000 hostile recall=79.04% fp=512
2026-08-21 09:25:40,378 INFO azoth_calibrate_ensemble: L20000 hostile recall=79.45% fp=631
2026-08-21 09:25:40,432 INFO azoth_calibrate_ensemble: L25000 hostile recall=79.82% fp=787
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-0d83a0d8d99643d6/config.json
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 24 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-0d83a0d8d99643d6 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-0d83a0d8d99643d6/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-0d83a0d8d99643d6/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-0d83a0d8d99643d6/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-0d83a0d8d99643d6/score_table.npz \
	--partition test \
	--parallelism 16 \
	--apply-thresholds-from /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-0d83a0d8d99643d6/config.json \
	--feature-cache-dir out/cache/azoth-route-features
2026-08-21 09:26:30,570 INFO azoth_calibrate_ensemble: partition 'test': 2129520 of 17074459 rows (12.5%) kept for fit/eval; score_table covers all 17074459
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1506, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1261, in main
    file_types_by_row = _fetch_file_types(args.db, row_ids)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 249, in _fetch_file_types
    cur.execute(
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/psycopg/cursor.py", line 117, in execute
    raise ex.with_traceback(None)
psycopg.errors.AdminShutdown: terminating connection due to administrator command
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9788)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0d83a0d8d99643d6` | `641edfb16bdf8104` | `19506f1868349825` |
| PR AUC | 0.9788 | 0.9782 | 0.9783 |
| ROC AUC | 0.9848 | 0.9844 | 0.9848 |
| F1 | 0.9204 | 0.9255 | 0.9270 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-08-21T13-15-21_20260821T131429-promote-0d83a0d8d99643d6_azoth-validate.log; tail: 2026-08-21 09:25:39,172 INFO azoth_calibrate_ensemble: L175 hostile recall=74.48% fp=86
2026-08-21 09:25:39,234 INFO azoth_calibrate_ensemble: L200 hostile recall=74.55% fp=86
2026-08-21 09:25:39,301 INFO azoth_calibrate_ensemble: L250 hostile recall=74.61% fp=87
2026-08-21 09:25:39,360 INFO azoth_calibrate_ensemble: L300 hostile recall=74.65% fp=88
2026-08-21 09:25:39,420 INFO azoth_calibrate_ensemble: L500 hostile recall=75.04% fp=92
2026-08-21 09:25:39,485 INFO azoth_calibrate_ensemble: L750 hostile recall=75.20% fp=102
2026-08-21 09:25:39,548 INFO azoth_calibrate_ensemble: L1000 hostile recall=75.37% fp=108
2026-08-21 09:25:39,622 INFO azoth_calibrate_ensemble: L1250 hostile recall=75.49% fp=113
2026-08-21 09:25:39,683 INFO azoth_calibrate_ensemble: L1500 hostile recall=75.61% fp=121
2026-08-21 09:25:39,743 INFO azoth_calibrate_ensemble: L1750 hostile recall=75.82% fp=128
2026-08-21 09:25:39,803 INFO azoth_calibrate_ensemble: L2000 hostile recall=76.00% fp=135
2026-08-21 09:25:39,861 INFO azoth_calibrate_ensemble: L2250 hostile recall=76.12% fp=144
2026-08-21 09:25:39,915 INFO azoth_calibrate_ensemble: L2500 hostile recall=76.24% fp=150
2026-08-21 09:25:39,970 INFO azoth_calibrate_ensemble: L3000 hostile recall=76.41% fp=169
2026-08-21 09:25:40,025 INFO azoth_calibrate_ensemble: L4000 hostile recall=76.79% fp=196
2026-08-21 09:25:40,083 INFO azoth_calibrate_ensemble: L5000 hostile recall=77.17% fp=223
2026-08-21 09:25:40,142 INFO azoth_calibrate_ensemble: L6000 hostile recall=77.58% fp=252
2026-08-21 09:25:40,210 INFO azoth_calibrate_ensemble: L7500 hostile recall=77.89% fp=279
2026-08-21 09:25:40,269 INFO azoth_calibrate_ensemble: L10000 hostile recall=78.41% fp=365
2026-08-21 09:25:40,323 INFO azoth_calibrate_ensemble: L15000 hostile recall=79.04% fp=512
2026-08-21 09:25:40,378 INFO azoth_calibrate_ensemble: L20000 hostile recall=79.45% fp=631
2026-08-21 09:25:40,432 INFO azoth_calibrate_ensemble: L25000 hostile recall=79.82% fp=787
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-0d83a0d8d99643d6/config.json
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 24 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-0d83a0d8d99643d6 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-0d83a0d8d99643d6/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-0d83a0d8d99643d6/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-0d83a0d8d99643d6/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-0d83a0d8d99643d6/score_table.npz \
	--partition test \
	--parallelism 16 \
	--apply-thresholds-from /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-0d83a0d8d99643d6/config.json \
	--feature-cache-dir out/cache/azoth-route-features
2026-08-21 09:26:30,570 INFO azoth_calibrate_ensemble: partition 'test': 2129520 of 17074459 rows (12.5%) kept for fit/eval; score_table covers all 17074459
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1506, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1261, in main
    file_types_by_row = _fetch_file_types(args.db, row_ids)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 249, in _fetch_file_types
    cur.execute(
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/psycopg/cursor.py", line 117, in execute
    raise ex.with_traceback(None)
psycopg.errors.AdminShutdown: terminating connection due to administrator command
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
