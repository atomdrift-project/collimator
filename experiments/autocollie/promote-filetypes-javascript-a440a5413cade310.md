# Promote REJECTED — `a440a5413cade310` on `filetypes/javascript`

Generated 2026-06-18T02:25:15Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-18T02-21-41_20260618T022140-promote-a440a5413cade310_azoth-validate.log; tail: 2026-06-17 22:23:00,976 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=57.42% fp=191 (FP/100M=28208.04)
2026-06-17 22:23:00,994 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=57.42% fp=191 (FP/100M=28208.04)
2026-06-17 22:23:01,012 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=57.42% fp=191 (FP/100M=28208.04)
2026-06-17 22:23:01,031 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=57.42% fp=191 (FP/100M=28208.04)
2026-06-17 22:23:01,048 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=57.42% fp=191 (FP/100M=28208.04)
2026-06-17 22:23:01,064 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=65.89% fp=258 (FP/100M=38103.00)
2026-06-17 22:23:01,081 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=67.96% fp=353 (FP/100M=52133.18)
2026-06-17 22:23:01,098 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=68.97% fp=440 (FP/100M=64981.86)
2026-06-17 22:23:01,115 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=69.39% fp=2520 (FP/100M=372168.86)
2026-06-17 22:23:01,132 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=70.59% fp=2617 (FP/100M=386494.41)
2026-06-17 22:23:01,150 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=71.11% fp=2739 (FP/100M=404512.10)
2026-06-17 22:23:01,168 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=71.42% fp=2797 (FP/100M=413077.90)
2026-06-17 22:23:01,187 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=71.99% fp=2855 (FP/100M=421643.69)
2026-06-17 22:23:01,205 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=72.29% fp=2938 (FP/100M=433901.63)
2026-06-17 22:23:01,223 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=72.62% fp=2990 (FP/100M=441581.30)
2026-06-17 22:23:01,242 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.70% fp=3469 (FP/100M=512322.92)
2026-06-17 22:23:01,260 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=74.87% fp=3974 (FP/100M=586904.38)
2026-06-17 22:23:01,279 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=76.05% fp=4897 (FP/100M=723218.61)
2026-06-17 22:23:01,298 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=77.48% fp=6026 (FP/100M=889956.17)
2026-06-17 22:23:01,316 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=78.82% fp=8750 (FP/100M=1292252.98)
2026-06-17 22:23:01,335 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=70.10% fp=6534 (FP/100M=964980.68)
2026-06-17 22:23:01,354 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=71.14% fp=5781 (FP/100M=853773.08)
2026-06-17 22:23:01,373 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=72.25% fp=5813 (FP/100M=858499.04)
2026-06-17 22:23:01,392 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=73.53% fp=4374 (FP/100M=645978.80)
2026-06-17 22:23:01,410 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=74.42% fp=4150 (FP/100M=612897.13)
2026-06-17 22:23:01,429 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=75.05% fp=3996 (FP/100M=590153.48)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
policy_search: previous-bundle is the bundle being written (self-comparison); disabling carry-forward to recompute every route from the current score table (avoids frozen/stale thresholds)
policy_search: processing 111 filetypes across 32 worker processes (0 carried forward)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/global_policy_metrics.md \
	--fail-on-budget --max-budget-multiplier 30
make[1]: *** [Makefile:1335: azoth-validate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9975)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a440a5413cade310` | `76c87a9be457f8f6` | `01ef945eebddd339` |
| PR AUC | 0.9975 | 0.9991 | 0.9991 |
| ROC AUC | 0.9968 | 0.9988 | 0.9988 |
| F1 | 0.9777 | 0.9873 | 0.9869 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-18T02-21-41_20260618T022140-promote-a440a5413cade310_azoth-validate.log; tail: 2026-06-17 22:23:00,976 INFO azoth_calibrate_ensemble: L1 on test: hostile recall=57.42% fp=191 (FP/100M=28208.04)
2026-06-17 22:23:00,994 INFO azoth_calibrate_ensemble: L2 on test: hostile recall=57.42% fp=191 (FP/100M=28208.04)
2026-06-17 22:23:01,012 INFO azoth_calibrate_ensemble: L3 on test: hostile recall=57.42% fp=191 (FP/100M=28208.04)
2026-06-17 22:23:01,031 INFO azoth_calibrate_ensemble: L4 on test: hostile recall=57.42% fp=191 (FP/100M=28208.04)
2026-06-17 22:23:01,048 INFO azoth_calibrate_ensemble: L5 on test: hostile recall=57.42% fp=191 (FP/100M=28208.04)
2026-06-17 22:23:01,064 INFO azoth_calibrate_ensemble: L10 on test: hostile recall=65.89% fp=258 (FP/100M=38103.00)
2026-06-17 22:23:01,081 INFO azoth_calibrate_ensemble: L20 on test: hostile recall=67.96% fp=353 (FP/100M=52133.18)
2026-06-17 22:23:01,098 INFO azoth_calibrate_ensemble: L30 on test: hostile recall=68.97% fp=440 (FP/100M=64981.86)
2026-06-17 22:23:01,115 INFO azoth_calibrate_ensemble: L40 on test: hostile recall=69.39% fp=2520 (FP/100M=372168.86)
2026-06-17 22:23:01,132 INFO azoth_calibrate_ensemble: L50 on test: hostile recall=70.59% fp=2617 (FP/100M=386494.41)
2026-06-17 22:23:01,150 INFO azoth_calibrate_ensemble: L60 on test: hostile recall=71.11% fp=2739 (FP/100M=404512.10)
2026-06-17 22:23:01,168 INFO azoth_calibrate_ensemble: L70 on test: hostile recall=71.42% fp=2797 (FP/100M=413077.90)
2026-06-17 22:23:01,187 INFO azoth_calibrate_ensemble: L80 on test: hostile recall=71.99% fp=2855 (FP/100M=421643.69)
2026-06-17 22:23:01,205 INFO azoth_calibrate_ensemble: L90 on test: hostile recall=72.29% fp=2938 (FP/100M=433901.63)
2026-06-17 22:23:01,223 INFO azoth_calibrate_ensemble: L100 on test: hostile recall=72.62% fp=2990 (FP/100M=441581.30)
2026-06-17 22:23:01,242 INFO azoth_calibrate_ensemble: L200 on test: hostile recall=73.70% fp=3469 (FP/100M=512322.92)
2026-06-17 22:23:01,260 INFO azoth_calibrate_ensemble: L300 on test: hostile recall=74.87% fp=3974 (FP/100M=586904.38)
2026-06-17 22:23:01,279 INFO azoth_calibrate_ensemble: L500 on test: hostile recall=76.05% fp=4897 (FP/100M=723218.61)
2026-06-17 22:23:01,298 INFO azoth_calibrate_ensemble: L1000 on test: hostile recall=77.48% fp=6026 (FP/100M=889956.17)
2026-06-17 22:23:01,316 INFO azoth_calibrate_ensemble: L2000 on test: hostile recall=78.82% fp=8750 (FP/100M=1292252.98)
2026-06-17 22:23:01,335 INFO azoth_calibrate_ensemble: L5000 on test: hostile recall=70.10% fp=6534 (FP/100M=964980.68)
2026-06-17 22:23:01,354 INFO azoth_calibrate_ensemble: L7500 on test: hostile recall=71.14% fp=5781 (FP/100M=853773.08)
2026-06-17 22:23:01,373 INFO azoth_calibrate_ensemble: L10000 on test: hostile recall=72.25% fp=5813 (FP/100M=858499.04)
2026-06-17 22:23:01,392 INFO azoth_calibrate_ensemble: L15000 on test: hostile recall=73.53% fp=4374 (FP/100M=645978.80)
2026-06-17 22:23:01,410 INFO azoth_calibrate_ensemble: L20000 on test: hostile recall=74.42% fp=4150 (FP/100M=612897.13)
2026-06-17 22:23:01,429 INFO azoth_calibrate_ensemble: L25000 on test: hostile recall=75.05% fp=3996 (FP/100M=590153.48)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/test_metrics.json
.venv/bin/python scripts/azoth_route_policy_search.py \
	 \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/route_policies.json \
	--csv /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/route_policies.csv \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/route_policies.md \
	 \
	--previous-bundle out/models/azoth \
	--workers 128
policy_search: previous-bundle is the bundle being written (self-comparison); disabling carry-forward to recompute every route from the current score table (avoids frozen/stale thresholds)
policy_search: processing 111 filetypes across 32 worker processes (0 carried forward)
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/route_policies.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/route_policies.csv
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/route_policies.md
.venv/bin/python scripts/azoth_policy_global_metrics.py \
	--config /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/config.json \
	--policy /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/route_policies.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/score_table.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/global_policy_metrics.json \
	--markdown /home/t/collimator/out/models/azoth-candidate-filetypes-javascript-a440a5413cade310/global_policy_metrics.md \
	--fail-on-budget --max-budget-multiplier 30
make[1]: *** [Makefile:1335: azoth-validate] Terminated)
