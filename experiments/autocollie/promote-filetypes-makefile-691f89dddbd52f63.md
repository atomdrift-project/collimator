# Promote REJECTED — `691f89dddbd52f63` on `filetypes/makefile`

Generated 2026-06-14T15:20:57Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-14T15-11-41_20260614T151129-promote-691f89dddbd52f63_azoth-validate.log; tail: 2026-06-14 11:19:00,910 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=65.67% fp=2976 (FP/100M=487456.51)
2026-06-14 11:19:00,934 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=65.67% fp=2976 (FP/100M=487456.51)
2026-06-14 11:19:00,957 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=65.67% fp=2976 (FP/100M=487456.51)
2026-06-14 11:19:00,980 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=65.67% fp=2976 (FP/100M=487456.51)
2026-06-14 11:19:01,003 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=65.67% fp=2976 (FP/100M=487456.51)
2026-06-14 11:19:01,026 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=66.98% fp=3976 (FP/100M=651252.38)
2026-06-14 11:19:01,051 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=68.04% fp=4080 (FP/100M=668287.15)
2026-06-14 11:19:01,074 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=68.48% fp=4149 (FP/100M=679589.07)
2026-06-14 11:19:01,097 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=69.37% fp=4253 (FP/100M=696623.84)
2026-06-14 11:19:01,119 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=69.84% fp=6832 (FP/100M=1119053.39)
2026-06-14 11:19:01,143 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=70.71% fp=6893 (FP/100M=1129044.94)
2026-06-14 11:19:01,165 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=71.38% fp=6952 (FP/100M=1138708.90)
2026-06-14 11:19:01,194 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=71.72% fp=7006 (FP/100M=1147553.87)
2026-06-14 11:19:01,224 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=72.18% fp=7049 (FP/100M=1154597.09)
2026-06-14 11:19:01,256 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=73.53% fp=7110 (FP/100M=1164588.64)
2026-06-14 11:19:01,279 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=76.91% fp=7904 (FP/100M=1294642.56)
2026-06-14 11:19:01,304 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=78.93% fp=8398 (FP/100M=1375557.72)
2026-06-14 11:19:01,326 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=80.54% fp=13343 (FP/100M=2185528.31)
2026-06-14 11:19:01,349 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=81.95% fp=14589 (FP/100M=2389617.96)
2026-06-14 11:19:01,385 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=83.27% fp=31912 (FP/100M=5227053.84)
2026-06-14 11:19:01,414 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=76.29% fp=25565 (FP/100M=4187441.44)
2026-06-14 11:19:01,437 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=77.06% fp=23803 (FP/100M=3898833.12)
2026-06-14 11:19:01,468 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=77.69% fp=13960 (FP/100M=2286590.36)
2026-06-14 11:19:01,494 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=77.39% fp=12212 (FP/100M=2000275.18)
2026-06-14 11:19:01,523 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=78.46% fp=12014 (FP/100M=1967843.59)
2026-06-14 11:19:01,551 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=79.38% fp=12071 (FP/100M=1977179.96)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
policy_search carry-forward: 1/59 routes changed; 98/99 filetypes can be carried forward from previous bundle
policy_search: processing 1 filetypes serially (98 carried forward)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/global_policy_metrics.md \
	--fail-on-budget --max-budget-multiplier 30
make[1]: *** [Makefile:1306: azoth-validate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.6411)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `691f89dddbd52f63` | `acd86b0a85d264d5` | `4e301a3c2823d25e` |
| PR AUC | 0.6411 | 0.6968 | 0.6778 |
| ROC AUC | 0.8955 | 0.9000 | 0.8955 |
| F1 | 0.5455 | 0.7273 | 0.6667 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-14T15-11-41_20260614T151129-promote-691f89dddbd52f63_azoth-validate.log; tail: 2026-06-14 11:19:00,910 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=65.67% fp=2976 (FP/100M=487456.51)
2026-06-14 11:19:00,934 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=65.67% fp=2976 (FP/100M=487456.51)
2026-06-14 11:19:00,957 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=65.67% fp=2976 (FP/100M=487456.51)
2026-06-14 11:19:00,980 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=65.67% fp=2976 (FP/100M=487456.51)
2026-06-14 11:19:01,003 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=65.67% fp=2976 (FP/100M=487456.51)
2026-06-14 11:19:01,026 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=66.98% fp=3976 (FP/100M=651252.38)
2026-06-14 11:19:01,051 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=68.04% fp=4080 (FP/100M=668287.15)
2026-06-14 11:19:01,074 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=68.48% fp=4149 (FP/100M=679589.07)
2026-06-14 11:19:01,097 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=69.37% fp=4253 (FP/100M=696623.84)
2026-06-14 11:19:01,119 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=69.84% fp=6832 (FP/100M=1119053.39)
2026-06-14 11:19:01,143 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=70.71% fp=6893 (FP/100M=1129044.94)
2026-06-14 11:19:01,165 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=71.38% fp=6952 (FP/100M=1138708.90)
2026-06-14 11:19:01,194 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=71.72% fp=7006 (FP/100M=1147553.87)
2026-06-14 11:19:01,224 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=72.18% fp=7049 (FP/100M=1154597.09)
2026-06-14 11:19:01,256 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=73.53% fp=7110 (FP/100M=1164588.64)
2026-06-14 11:19:01,279 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=76.91% fp=7904 (FP/100M=1294642.56)
2026-06-14 11:19:01,304 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=78.93% fp=8398 (FP/100M=1375557.72)
2026-06-14 11:19:01,326 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=80.54% fp=13343 (FP/100M=2185528.31)
2026-06-14 11:19:01,349 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=81.95% fp=14589 (FP/100M=2389617.96)
2026-06-14 11:19:01,385 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=83.27% fp=31912 (FP/100M=5227053.84)
2026-06-14 11:19:01,414 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=76.29% fp=25565 (FP/100M=4187441.44)
2026-06-14 11:19:01,437 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=77.06% fp=23803 (FP/100M=3898833.12)
2026-06-14 11:19:01,468 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=77.69% fp=13960 (FP/100M=2286590.36)
2026-06-14 11:19:01,494 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=77.39% fp=12212 (FP/100M=2000275.18)
2026-06-14 11:19:01,523 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=78.46% fp=12014 (FP/100M=1967843.59)
2026-06-14 11:19:01,551 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=79.38% fp=12071 (FP/100M=1977179.96)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
policy_search carry-forward: 1/59 routes changed; 98/99 filetypes can be carried forward from previous bundle
policy_search: processing 1 filetypes serially (98 carried forward)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-691f89dddbd52f63/global_policy_metrics.md \
	--fail-on-budget --max-budget-multiplier 30
make[1]: *** [Makefile:1306: azoth-validate] Terminated)
