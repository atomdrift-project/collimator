# Promote REJECTED — `1e5028d2bc611fa3` on `filetypes/xls`

Generated 2026-05-25T18:26:12Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-05-25T18-22-43_20260525T182240-promote-1e5028d2bc611fa3_azoth-validate.log; tail: 2026-05-25 14:24:57,804 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-05-25 14:24:58,067 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-05-25 14:24:58,245 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-05-25 14:24:58,520 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-05-25 14:24:58,844 INFO azoth_calibrate_ensemble: filetypes/pptx: using cached scores
2026-05-25 14:24:59,055 INFO azoth_calibrate_ensemble: L0 on test: hostile recall=0.00% fp=0 (FP/M=0.00); suspicious recall=68.60% fp=50 (FP/M=131.66)
2026-05-25 14:24:59,079 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=65.55% fp=52 (FP/M=136.92); suspicious recall=70.37% fp=61 (FP/M=160.62)
2026-05-25 14:24:59,103 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=66.26% fp=52 (FP/M=136.92); suspicious recall=73.22% fp=72 (FP/M=189.58)
2026-05-25 14:24:59,128 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=67.13% fp=54 (FP/M=142.19); suspicious recall=74.68% fp=78 (FP/M=205.38)
2026-05-25 14:24:59,152 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=67.23% fp=54 (FP/M=142.19); suspicious recall=76.01% fp=86 (FP/M=226.45)
2026-05-25 14:24:59,177 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=67.28% fp=54 (FP/M=142.19); suspicious recall=76.53% fp=88 (FP/M=231.71)
2026-05-25 14:24:59,201 INFO azoth_calibrate_ensemble: L6 on test: hostile recall=68.48% fp=50 (FP/M=131.66); suspicious recall=77.28% fp=90 (FP/M=236.98)
2026-05-25 14:24:59,226 INFO azoth_calibrate_ensemble: L7 on test: hostile recall=68.46% fp=49 (FP/M=129.02); suspicious recall=77.34% fp=101 (FP/M=265.94)
2026-05-25 14:24:59,250 INFO azoth_calibrate_ensemble: L8 on test: hostile recall=68.60% fp=50 (FP/M=131.66); suspicious recall=77.57% fp=104 (FP/M=273.84)
2026-05-25 14:24:59,273 INFO azoth_calibrate_ensemble: L9 on test: hostile recall=68.69% fp=51 (FP/M=134.29); suspicious recall=78.00% fp=114 (FP/M=300.17)
2026-05-25 14:24:59,295 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=68.78% fp=54 (FP/M=142.19); suspicious recall=78.30% fp=118 (FP/M=310.71)
2026-05-25 14:24:59,319 INFO azoth_calibrate_ensemble: L11 on test: hostile recall=69.57% fp=55 (FP/M=144.82); suspicious recall=78.51% fp=123 (FP/M=323.87)
2026-05-25 14:24:59,342 INFO azoth_calibrate_ensemble: L12 on test: hostile recall=69.65% fp=55 (FP/M=144.82); suspicious recall=78.74% fp=122 (FP/M=321.24)
2026-05-25 14:24:59,363 INFO azoth_calibrate_ensemble: L13 on test: hostile recall=69.71% fp=55 (FP/M=144.82); suspicious recall=79.43% fp=18523 (FP/M=48773.10)
2026-05-25 14:24:59,383 INFO azoth_calibrate_ensemble: L14 on test: hostile recall=69.81% fp=56 (FP/M=147.45); suspicious recall=79.56% fp=18527 (FP/M=48783.63)
2026-05-25 14:24:59,404 INFO azoth_calibrate_ensemble: L15 on test: hostile recall=69.85% fp=56 (FP/M=147.45); suspicious recall=79.64% fp=18530 (FP/M=48791.53)
2026-05-25 14:24:59,424 INFO azoth_calibrate_ensemble: L16 on test: hostile recall=70.25% fp=56 (FP/M=147.45); suspicious recall=79.76% fp=18531 (FP/M=48794.17)
2026-05-25 14:24:59,444 INFO azoth_calibrate_ensemble: L17 on test: hostile recall=70.50% fp=58 (FP/M=152.72); suspicious recall=79.86% fp=18540 (FP/M=48817.87)
2026-05-25 14:24:59,465 INFO azoth_calibrate_ensemble: L18 on test: hostile recall=70.54% fp=61 (FP/M=160.62); suspicious recall=80.00% fp=18545 (FP/M=48831.03)
2026-05-25 14:24:59,583 INFO azoth_calibrate_ensemble: L19 on test: hostile recall=71.10% fp=62 (FP/M=163.25); suspicious recall=80.50% fp=18552 (FP/M=48849.46)
2026-05-25 14:24:59,651 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=71.18% fp=65 (FP/M=171.15); suspicious recall=80.90% fp=18570 (FP/M=48896.86)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 64
policy_search carry-forward: 1/46 routes changed; 79/80 filetypes can be carried forward from previous bundle
policy_search: processing 1 filetypes serially (79 carried forward)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/global_policy_metrics.md \
	--fail-on-budget --max-budget-multiplier 30
make[2]: *** [Makefile:1132: azoth-validate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9999)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `1e5028d2bc611fa3` | `f97561ef4fd2772c` | `897b9c98906c85e5` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9995 | 0.9995 | 0.9995 |
| F1 | 0.9917 | 0.9921 | 0.9921 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-05-25T18-22-43_20260525T182240-promote-1e5028d2bc611fa3_azoth-validate.log; tail: 2026-05-25 14:24:57,804 INFO azoth_calibrate_ensemble: filetypes/lnk: using cached scores
2026-05-25 14:24:58,067 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-05-25 14:24:58,245 INFO azoth_calibrate_ensemble: filetypes/rtf: using cached scores
2026-05-25 14:24:58,520 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-05-25 14:24:58,844 INFO azoth_calibrate_ensemble: filetypes/pptx: using cached scores
2026-05-25 14:24:59,055 INFO azoth_calibrate_ensemble: L0 on test: hostile recall=0.00% fp=0 (FP/M=0.00); suspicious recall=68.60% fp=50 (FP/M=131.66)
2026-05-25 14:24:59,079 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=65.55% fp=52 (FP/M=136.92); suspicious recall=70.37% fp=61 (FP/M=160.62)
2026-05-25 14:24:59,103 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=66.26% fp=52 (FP/M=136.92); suspicious recall=73.22% fp=72 (FP/M=189.58)
2026-05-25 14:24:59,128 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=67.13% fp=54 (FP/M=142.19); suspicious recall=74.68% fp=78 (FP/M=205.38)
2026-05-25 14:24:59,152 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=67.23% fp=54 (FP/M=142.19); suspicious recall=76.01% fp=86 (FP/M=226.45)
2026-05-25 14:24:59,177 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=67.28% fp=54 (FP/M=142.19); suspicious recall=76.53% fp=88 (FP/M=231.71)
2026-05-25 14:24:59,201 INFO azoth_calibrate_ensemble: L6 on test: hostile recall=68.48% fp=50 (FP/M=131.66); suspicious recall=77.28% fp=90 (FP/M=236.98)
2026-05-25 14:24:59,226 INFO azoth_calibrate_ensemble: L7 on test: hostile recall=68.46% fp=49 (FP/M=129.02); suspicious recall=77.34% fp=101 (FP/M=265.94)
2026-05-25 14:24:59,250 INFO azoth_calibrate_ensemble: L8 on test: hostile recall=68.60% fp=50 (FP/M=131.66); suspicious recall=77.57% fp=104 (FP/M=273.84)
2026-05-25 14:24:59,273 INFO azoth_calibrate_ensemble: L9 on test: hostile recall=68.69% fp=51 (FP/M=134.29); suspicious recall=78.00% fp=114 (FP/M=300.17)
2026-05-25 14:24:59,295 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=68.78% fp=54 (FP/M=142.19); suspicious recall=78.30% fp=118 (FP/M=310.71)
2026-05-25 14:24:59,319 INFO azoth_calibrate_ensemble: L11 on test: hostile recall=69.57% fp=55 (FP/M=144.82); suspicious recall=78.51% fp=123 (FP/M=323.87)
2026-05-25 14:24:59,342 INFO azoth_calibrate_ensemble: L12 on test: hostile recall=69.65% fp=55 (FP/M=144.82); suspicious recall=78.74% fp=122 (FP/M=321.24)
2026-05-25 14:24:59,363 INFO azoth_calibrate_ensemble: L13 on test: hostile recall=69.71% fp=55 (FP/M=144.82); suspicious recall=79.43% fp=18523 (FP/M=48773.10)
2026-05-25 14:24:59,383 INFO azoth_calibrate_ensemble: L14 on test: hostile recall=69.81% fp=56 (FP/M=147.45); suspicious recall=79.56% fp=18527 (FP/M=48783.63)
2026-05-25 14:24:59,404 INFO azoth_calibrate_ensemble: L15 on test: hostile recall=69.85% fp=56 (FP/M=147.45); suspicious recall=79.64% fp=18530 (FP/M=48791.53)
2026-05-25 14:24:59,424 INFO azoth_calibrate_ensemble: L16 on test: hostile recall=70.25% fp=56 (FP/M=147.45); suspicious recall=79.76% fp=18531 (FP/M=48794.17)
2026-05-25 14:24:59,444 INFO azoth_calibrate_ensemble: L17 on test: hostile recall=70.50% fp=58 (FP/M=152.72); suspicious recall=79.86% fp=18540 (FP/M=48817.87)
2026-05-25 14:24:59,465 INFO azoth_calibrate_ensemble: L18 on test: hostile recall=70.54% fp=61 (FP/M=160.62); suspicious recall=80.00% fp=18545 (FP/M=48831.03)
2026-05-25 14:24:59,583 INFO azoth_calibrate_ensemble: L19 on test: hostile recall=71.10% fp=62 (FP/M=163.25); suspicious recall=80.50% fp=18552 (FP/M=48849.46)
2026-05-25 14:24:59,651 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=71.18% fp=65 (FP/M=171.15); suspicious recall=80.90% fp=18570 (FP/M=48896.86)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 64
policy_search carry-forward: 1/46 routes changed; 79/80 filetypes can be carried forward from previous bundle
policy_search: processing 1 filetypes serially (79 carried forward)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-xls-1e5028d2bc611fa3/global_policy_metrics.md \
	--fail-on-budget --max-budget-multiplier 30
make[2]: *** [Makefile:1132: azoth-validate] Terminated)
