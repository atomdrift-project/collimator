# Promote REJECTED — `d887d7dae3e83d19` on `filetypes/pdf`

Generated 2026-06-28T07:06:05Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T07-01-53_20260628T070151-promote-d887d7dae3e83d19_azoth-validate.log; tail: 2026-06-28 03:06:02,117 INFO azoth_calibrate_ensemble: L0 on test: hostile recall=59.61% fp=66 (FP/100M=8757.45)
2026-06-28 03:06:02,140 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=59.61% fp=66 (FP/100M=8757.45)
2026-06-28 03:06:02,163 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=59.62% fp=66 (FP/100M=8757.45)
2026-06-28 03:06:02,189 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=59.63% fp=66 (FP/100M=8757.45)
2026-06-28 03:06:02,211 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=59.63% fp=66 (FP/100M=8757.45)
2026-06-28 03:06:02,236 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=59.63% fp=66 (FP/100M=8757.45)
2026-06-28 03:06:02,259 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=61.37% fp=113 (FP/100M=14993.82)
2026-06-28 03:06:02,282 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=62.01% fp=3210 (FP/100M=425930.55)
2026-06-28 03:06:02,304 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=64.59% fp=3288 (FP/100M=436280.26)
2026-06-28 03:06:02,329 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=65.32% fp=5345 (FP/100M=709220.80)
2026-06-28 03:06:02,353 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=65.88% fp=5419 (FP/100M=719039.76)
2026-06-28 03:06:02,376 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.65% fp=5493 (FP/100M=728858.72)
2026-06-28 03:06:02,400 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.84% fp=5557 (FP/100M=737350.79)
2026-06-28 03:06:02,424 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.08% fp=5611 (FP/100M=744515.98)
2026-06-28 03:06:02,452 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.51% fp=5678 (FP/100M=753406.12)
2026-06-28 03:06:02,476 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.95% fp=5742 (FP/100M=761898.19)
2026-06-28 03:06:02,500 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6300 (FP/100M=835938.45)
2026-06-28 03:06:02,525 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.03% fp=6751 (FP/100M=895781.03)
2026-06-28 03:06:02,552 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7431 (FP/100M=986009.31)
2026-06-28 03:06:02,584 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9165 (FP/100M=1216091.42)
2026-06-28 03:06:02,614 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.48% fp=11038 (FP/100M=1464617.25)
2026-06-28 03:06:02,647 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.20% fp=11726 (FP/100M=1555907.03)
2026-06-28 03:06:02,679 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8840 (FP/100M=1172967.61)
2026-06-28 03:06:02,712 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8872 (FP/100M=1177213.64)
2026-06-28 03:06:02,740 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7515 (FP/100M=997155.16)
2026-06-28 03:06:02,769 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.05% fp=7020 (FP/100M=931474.28)
2026-06-28 03:06:02,800 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6437 (FP/100M=854116.80)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pdf-d887d7dae3e83d19/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-pdf-d887d7dae3e83d19/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-pdf-d887d7dae3e83d19/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-pdf-d887d7dae3e83d19/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-pdf-d887d7dae3e83d19/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-pdf-d887d7dae3e83d19/route_policies.md \
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
make[1]: *** [Makefile:1338: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d887d7dae3e83d19` | `0a52d4d79b97b17d` | `6d7119f69882d5e2` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9990 | 0.9991 |
| F1 | 0.9945 | 0.9983 | 0.9984 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T07-01-53_20260628T070151-promote-d887d7dae3e83d19_azoth-validate.log; tail: 2026-06-28 03:06:02,117 INFO azoth_calibrate_ensemble: L0 on test: hostile recall=59.61% fp=66 (FP/100M=8757.45)
2026-06-28 03:06:02,140 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=59.61% fp=66 (FP/100M=8757.45)
2026-06-28 03:06:02,163 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=59.62% fp=66 (FP/100M=8757.45)
2026-06-28 03:06:02,189 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=59.63% fp=66 (FP/100M=8757.45)
2026-06-28 03:06:02,211 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=59.63% fp=66 (FP/100M=8757.45)
2026-06-28 03:06:02,236 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=59.63% fp=66 (FP/100M=8757.45)
2026-06-28 03:06:02,259 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=61.37% fp=113 (FP/100M=14993.82)
2026-06-28 03:06:02,282 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=62.01% fp=3210 (FP/100M=425930.55)
2026-06-28 03:06:02,304 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=64.59% fp=3288 (FP/100M=436280.26)
2026-06-28 03:06:02,329 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=65.32% fp=5345 (FP/100M=709220.80)
2026-06-28 03:06:02,353 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=65.88% fp=5419 (FP/100M=719039.76)
2026-06-28 03:06:02,376 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=66.65% fp=5493 (FP/100M=728858.72)
2026-06-28 03:06:02,400 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=67.84% fp=5557 (FP/100M=737350.79)
2026-06-28 03:06:02,424 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=68.08% fp=5611 (FP/100M=744515.98)
2026-06-28 03:06:02,452 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=69.51% fp=5678 (FP/100M=753406.12)
2026-06-28 03:06:02,476 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=69.95% fp=5742 (FP/100M=761898.19)
2026-06-28 03:06:02,500 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.39% fp=6300 (FP/100M=835938.45)
2026-06-28 03:06:02,525 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=75.03% fp=6751 (FP/100M=895781.03)
2026-06-28 03:06:02,552 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=77.63% fp=7431 (FP/100M=986009.31)
2026-06-28 03:06:02,584 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=80.72% fp=9165 (FP/100M=1216091.42)
2026-06-28 03:06:02,614 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=82.48% fp=11038 (FP/100M=1464617.25)
2026-06-28 03:06:02,647 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=72.20% fp=11726 (FP/100M=1555907.03)
2026-06-28 03:06:02,679 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=74.30% fp=8840 (FP/100M=1172967.61)
2026-06-28 03:06:02,712 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=75.27% fp=8872 (FP/100M=1177213.64)
2026-06-28 03:06:02,740 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=75.96% fp=7515 (FP/100M=997155.16)
2026-06-28 03:06:02,769 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=77.05% fp=7020 (FP/100M=931474.28)
2026-06-28 03:06:02,800 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=77.90% fp=6437 (FP/100M=854116.80)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pdf-d887d7dae3e83d19/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-pdf-d887d7dae3e83d19/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-pdf-d887d7dae3e83d19/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-pdf-d887d7dae3e83d19/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-pdf-d887d7dae3e83d19/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-pdf-d887d7dae3e83d19/route_policies.md \
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
make[1]: *** [Makefile:1338: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
