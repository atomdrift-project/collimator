# Promote REJECTED — `563636e7430e499f` on `filegroups/config`

Generated 2026-06-08T12:13:50Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-08T12-11-48_20260608T121132-promote-563636e7430e499f_azoth-validate.log; tail: 2026-06-08 08:12:57,093 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-08 08:12:57,195 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-08 08:12:57,511 INFO azoth_calibrate_ensemble: L0 on test: hostile recall=57.29% fp=10056 (FP/100M=1827921.61)
2026-06-08 08:12:57,529 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=57.29% fp=10056 (FP/100M=1827921.61)
2026-06-08 08:12:57,546 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=57.29% fp=10056 (FP/100M=1827921.61)
2026-06-08 08:12:57,563 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=57.29% fp=10056 (FP/100M=1827921.61)
2026-06-08 08:12:57,581 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=57.29% fp=10056 (FP/100M=1827921.61)
2026-06-08 08:12:57,598 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=57.29% fp=10056 (FP/100M=1827921.61)
2026-06-08 08:12:57,616 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=59.73% fp=10967 (FP/100M=1993517.93)
2026-06-08 08:12:57,633 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=62.99% fp=11056 (FP/100M=2009695.84)
2026-06-08 08:12:57,652 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=65.51% fp=11130 (FP/100M=2023147.13)
2026-06-08 08:12:57,669 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=67.15% fp=12632 (FP/100M=2296172.02)
2026-06-08 08:12:57,687 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=67.39% fp=12718 (FP/100M=2311804.60)
2026-06-08 08:12:57,704 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=75.02% fp=12806 (FP/100M=2327800.73)
2026-06-08 08:12:57,722 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=75.26% fp=14626 (FP/100M=2658629.82)
2026-06-08 08:12:57,741 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=75.57% fp=14681 (FP/100M=2668627.40)
2026-06-08 08:12:57,758 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=75.99% fp=14958 (FP/100M=2718978.87)
2026-06-08 08:12:57,776 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=76.21% fp=15002 (FP/100M=2726976.93)
2026-06-08 08:12:57,793 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=80.02% fp=15469 (FP/100M=2811865.49)
2026-06-08 08:12:57,811 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=83.12% fp=16021 (FP/100M=2912204.87)
2026-06-08 08:12:57,828 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=85.57% fp=16890 (FP/100M=3070166.67)
2026-06-08 08:12:57,846 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=88.02% fp=19434 (FP/100M=3532600.30)
2026-06-08 08:12:57,863 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=90.11% fp=21814 (FP/100M=3965222.96)
2026-06-08 08:12:57,881 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=91.26% fp=21712 (FP/100M=3946681.98)
2026-06-08 08:12:57,899 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=79.32% fp=18323 (FP/100M=3330649.13)
2026-06-08 08:12:57,917 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=80.71% fp=17682 (FP/100M=3214131.86)
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
policy_search carry-forward: 1/56 routes changed; 85/89 filetypes can be carried forward from previous bundle
policy_search: processing 4 filetypes across 4 worker processes (85 carried forward)
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/global_policy_metrics.md \
	--fail-on-budget --max-budget-multiplier 30
make[1]: *** [Makefile:1301: azoth-validate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9988)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `563636e7430e499f` | `2aab519bd42e3077` | `638c1fbccc1f530f` |
| PR AUC | 0.9988 | 0.9988 | 0.9988 |
| ROC AUC | 0.9983 | 0.9983 | 0.9983 |
| F1 | 0.9925 | 0.9937 | 0.9939 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-08T12-11-48_20260608T121132-promote-563636e7430e499f_azoth-validate.log; tail: 2026-06-08 08:12:57,093 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-08 08:12:57,195 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
2026-06-08 08:12:57,511 INFO azoth_calibrate_ensemble: L0 on test: hostile recall=57.29% fp=10056 (FP/100M=1827921.61)
2026-06-08 08:12:57,529 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=57.29% fp=10056 (FP/100M=1827921.61)
2026-06-08 08:12:57,546 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=57.29% fp=10056 (FP/100M=1827921.61)
2026-06-08 08:12:57,563 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=57.29% fp=10056 (FP/100M=1827921.61)
2026-06-08 08:12:57,581 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=57.29% fp=10056 (FP/100M=1827921.61)
2026-06-08 08:12:57,598 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=57.29% fp=10056 (FP/100M=1827921.61)
2026-06-08 08:12:57,616 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=59.73% fp=10967 (FP/100M=1993517.93)
2026-06-08 08:12:57,633 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=62.99% fp=11056 (FP/100M=2009695.84)
2026-06-08 08:12:57,652 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=65.51% fp=11130 (FP/100M=2023147.13)
2026-06-08 08:12:57,669 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=67.15% fp=12632 (FP/100M=2296172.02)
2026-06-08 08:12:57,687 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=67.39% fp=12718 (FP/100M=2311804.60)
2026-06-08 08:12:57,704 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=75.02% fp=12806 (FP/100M=2327800.73)
2026-06-08 08:12:57,722 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=75.26% fp=14626 (FP/100M=2658629.82)
2026-06-08 08:12:57,741 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=75.57% fp=14681 (FP/100M=2668627.40)
2026-06-08 08:12:57,758 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=75.99% fp=14958 (FP/100M=2718978.87)
2026-06-08 08:12:57,776 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=76.21% fp=15002 (FP/100M=2726976.93)
2026-06-08 08:12:57,793 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=80.02% fp=15469 (FP/100M=2811865.49)
2026-06-08 08:12:57,811 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=83.12% fp=16021 (FP/100M=2912204.87)
2026-06-08 08:12:57,828 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=85.57% fp=16890 (FP/100M=3070166.67)
2026-06-08 08:12:57,846 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=88.02% fp=19434 (FP/100M=3532600.30)
2026-06-08 08:12:57,863 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=90.11% fp=21814 (FP/100M=3965222.96)
2026-06-08 08:12:57,881 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=91.26% fp=21712 (FP/100M=3946681.98)
2026-06-08 08:12:57,899 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=79.32% fp=18323 (FP/100M=3330649.13)
2026-06-08 08:12:57,917 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=80.71% fp=17682 (FP/100M=3214131.86)
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
policy_search carry-forward: 1/56 routes changed; 85/89 filetypes can be carried forward from previous bundle
policy_search: processing 4 filetypes across 4 worker processes (85 carried forward)
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filegroups-config-563636e7430e499f/global_policy_metrics.md \
	--fail-on-budget --max-budget-multiplier 30
make[1]: *** [Makefile:1301: azoth-validate] Terminated)
