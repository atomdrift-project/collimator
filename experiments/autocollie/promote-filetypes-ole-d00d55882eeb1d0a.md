# Promote REJECTED — `d00d55882eeb1d0a` on `filetypes/ole`

Generated 2026-08-05T02:33:07Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-08-05T02-11-19_20260805T021022-promote-d00d55882eeb1d0a_azoth-validate.log; tail: 2026-08-04 22:29:27,926 INFO azoth_calibrate_ensemble: L15 hostile recall=62.10% fp=31
2026-08-04 22:29:27,978 INFO azoth_calibrate_ensemble: L20 hostile recall=62.17% fp=31
2026-08-04 22:29:28,022 INFO azoth_calibrate_ensemble: L25 hostile recall=62.23% fp=31
2026-08-04 22:29:28,063 INFO azoth_calibrate_ensemble: L30 hostile recall=62.31% fp=31
2026-08-04 22:29:28,104 INFO azoth_calibrate_ensemble: L40 hostile recall=62.42% fp=31
2026-08-04 22:29:28,142 INFO azoth_calibrate_ensemble: L50 hostile recall=62.55% fp=31
2026-08-04 22:29:28,182 INFO azoth_calibrate_ensemble: L60 hostile recall=62.64% fp=31
2026-08-04 22:29:28,221 INFO azoth_calibrate_ensemble: L70 hostile recall=62.70% fp=32
2026-08-04 22:29:28,288 INFO azoth_calibrate_ensemble: L80 hostile recall=62.75% fp=32
2026-08-04 22:29:28,338 INFO azoth_calibrate_ensemble: L90 hostile recall=62.80% fp=32
2026-08-04 22:29:28,392 INFO azoth_calibrate_ensemble: L100 hostile recall=62.86% fp=32
2026-08-04 22:29:28,438 INFO azoth_calibrate_ensemble: L125 hostile recall=63.00% fp=32
2026-08-04 22:29:28,481 INFO azoth_calibrate_ensemble: L150 hostile recall=63.13% fp=32
2026-08-04 22:29:28,519 INFO azoth_calibrate_ensemble: L175 hostile recall=63.28% fp=32
2026-08-04 22:29:28,560 INFO azoth_calibrate_ensemble: L200 hostile recall=63.40% fp=33
2026-08-04 22:29:28,600 INFO azoth_calibrate_ensemble: L250 hostile recall=63.64% fp=34
2026-08-04 22:29:28,640 INFO azoth_calibrate_ensemble: L300 hostile recall=63.94% fp=35
2026-08-04 22:29:28,681 INFO azoth_calibrate_ensemble: L500 hostile recall=64.82% fp=41
2026-08-04 22:29:28,719 INFO azoth_calibrate_ensemble: L750 hostile recall=65.82% fp=47
2026-08-04 22:29:28,756 INFO azoth_calibrate_ensemble: L1000 hostile recall=66.61% fp=57
2026-08-04 22:29:28,794 INFO azoth_calibrate_ensemble: L1250 hostile recall=66.87% fp=63
2026-08-04 22:29:28,840 INFO azoth_calibrate_ensemble: L1500 hostile recall=67.01% fp=72
2026-08-04 22:29:28,888 INFO azoth_calibrate_ensemble: L1750 hostile recall=67.19% fp=77
2026-08-04 22:29:28,941 INFO azoth_calibrate_ensemble: L2000 hostile recall=67.43% fp=86
2026-08-04 22:29:28,991 INFO azoth_calibrate_ensemble: L2250 hostile recall=67.64% fp=92
2026-08-04 22:29:29,041 INFO azoth_calibrate_ensemble: L2500 hostile recall=67.78% fp=102
2026-08-04 22:29:29,095 INFO azoth_calibrate_ensemble: L3000 hostile recall=69.00% fp=118
2026-08-04 22:29:29,146 INFO azoth_calibrate_ensemble: L4000 hostile recall=70.15% fp=150
2026-08-04 22:29:29,199 INFO azoth_calibrate_ensemble: L5000 hostile recall=70.74% fp=171
2026-08-04 22:29:29,249 INFO azoth_calibrate_ensemble: L6000 hostile recall=71.28% fp=200
2026-08-04 22:29:29,320 INFO azoth_calibrate_ensemble: L7500 hostile recall=71.88% fp=249
2026-08-04 22:29:29,389 INFO azoth_calibrate_ensemble: L10000 hostile recall=72.40% fp=316
2026-08-04 22:29:29,436 INFO azoth_calibrate_ensemble: L15000 hostile recall=74.32% fp=471
2026-08-04 22:29:29,478 INFO azoth_calibrate_ensemble: L20000 hostile recall=78.27% fp=604
2026-08-04 22:29:29,519 INFO azoth_calibrate_ensemble: L25000 hostile recall=78.88% fp=754
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-ole-d00d55882eeb1d0a/config.json
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-ole-d00d55882eeb1d0a \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-ole-d00d55882eeb1d0a/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-ole-d00d55882eeb1d0a/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-ole-d00d55882eeb1d0a/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-ole-d00d55882eeb1d0a/score_table.npz \
	--partition test \
	--parallelism 16 \
	--apply-thresholds-from /home/t/collimator/out/models/azoth-candidate-filetypes-ole-d00d55882eeb1d0a/config.json \
	--feature-cache-dir out/cache/azoth-route-features
2026-08-04 22:29:56,431 INFO azoth_calibrate_ensemble: partition 'test': 1946507 of 15612661 rows (12.5%) kept for fit/eval; score_table covers all 15612661
make[1]: *** [Makefile:1260: azoth-calibrate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9977)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d00d55882eeb1d0a` | `344417be3986a630` | `5b94e89ec32b2f01` |
| PR AUC | 0.9977 | 0.9978 | 0.9978 |
| ROC AUC | 0.9932 | 0.9927 | 0.9926 |
| F1 | 0.9743 | 0.9831 | 0.9819 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-08-05T02-11-19_20260805T021022-promote-d00d55882eeb1d0a_azoth-validate.log; tail: 2026-08-04 22:29:27,926 INFO azoth_calibrate_ensemble: L15 hostile recall=62.10% fp=31
2026-08-04 22:29:27,978 INFO azoth_calibrate_ensemble: L20 hostile recall=62.17% fp=31
2026-08-04 22:29:28,022 INFO azoth_calibrate_ensemble: L25 hostile recall=62.23% fp=31
2026-08-04 22:29:28,063 INFO azoth_calibrate_ensemble: L30 hostile recall=62.31% fp=31
2026-08-04 22:29:28,104 INFO azoth_calibrate_ensemble: L40 hostile recall=62.42% fp=31
2026-08-04 22:29:28,142 INFO azoth_calibrate_ensemble: L50 hostile recall=62.55% fp=31
2026-08-04 22:29:28,182 INFO azoth_calibrate_ensemble: L60 hostile recall=62.64% fp=31
2026-08-04 22:29:28,221 INFO azoth_calibrate_ensemble: L70 hostile recall=62.70% fp=32
2026-08-04 22:29:28,288 INFO azoth_calibrate_ensemble: L80 hostile recall=62.75% fp=32
2026-08-04 22:29:28,338 INFO azoth_calibrate_ensemble: L90 hostile recall=62.80% fp=32
2026-08-04 22:29:28,392 INFO azoth_calibrate_ensemble: L100 hostile recall=62.86% fp=32
2026-08-04 22:29:28,438 INFO azoth_calibrate_ensemble: L125 hostile recall=63.00% fp=32
2026-08-04 22:29:28,481 INFO azoth_calibrate_ensemble: L150 hostile recall=63.13% fp=32
2026-08-04 22:29:28,519 INFO azoth_calibrate_ensemble: L175 hostile recall=63.28% fp=32
2026-08-04 22:29:28,560 INFO azoth_calibrate_ensemble: L200 hostile recall=63.40% fp=33
2026-08-04 22:29:28,600 INFO azoth_calibrate_ensemble: L250 hostile recall=63.64% fp=34
2026-08-04 22:29:28,640 INFO azoth_calibrate_ensemble: L300 hostile recall=63.94% fp=35
2026-08-04 22:29:28,681 INFO azoth_calibrate_ensemble: L500 hostile recall=64.82% fp=41
2026-08-04 22:29:28,719 INFO azoth_calibrate_ensemble: L750 hostile recall=65.82% fp=47
2026-08-04 22:29:28,756 INFO azoth_calibrate_ensemble: L1000 hostile recall=66.61% fp=57
2026-08-04 22:29:28,794 INFO azoth_calibrate_ensemble: L1250 hostile recall=66.87% fp=63
2026-08-04 22:29:28,840 INFO azoth_calibrate_ensemble: L1500 hostile recall=67.01% fp=72
2026-08-04 22:29:28,888 INFO azoth_calibrate_ensemble: L1750 hostile recall=67.19% fp=77
2026-08-04 22:29:28,941 INFO azoth_calibrate_ensemble: L2000 hostile recall=67.43% fp=86
2026-08-04 22:29:28,991 INFO azoth_calibrate_ensemble: L2250 hostile recall=67.64% fp=92
2026-08-04 22:29:29,041 INFO azoth_calibrate_ensemble: L2500 hostile recall=67.78% fp=102
2026-08-04 22:29:29,095 INFO azoth_calibrate_ensemble: L3000 hostile recall=69.00% fp=118
2026-08-04 22:29:29,146 INFO azoth_calibrate_ensemble: L4000 hostile recall=70.15% fp=150
2026-08-04 22:29:29,199 INFO azoth_calibrate_ensemble: L5000 hostile recall=70.74% fp=171
2026-08-04 22:29:29,249 INFO azoth_calibrate_ensemble: L6000 hostile recall=71.28% fp=200
2026-08-04 22:29:29,320 INFO azoth_calibrate_ensemble: L7500 hostile recall=71.88% fp=249
2026-08-04 22:29:29,389 INFO azoth_calibrate_ensemble: L10000 hostile recall=72.40% fp=316
2026-08-04 22:29:29,436 INFO azoth_calibrate_ensemble: L15000 hostile recall=74.32% fp=471
2026-08-04 22:29:29,478 INFO azoth_calibrate_ensemble: L20000 hostile recall=78.27% fp=604
2026-08-04 22:29:29,519 INFO azoth_calibrate_ensemble: L25000 hostile recall=78.88% fp=754
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-ole-d00d55882eeb1d0a/config.json
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-ole-d00d55882eeb1d0a \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-ole-d00d55882eeb1d0a/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-ole-d00d55882eeb1d0a/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-ole-d00d55882eeb1d0a/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-ole-d00d55882eeb1d0a/score_table.npz \
	--partition test \
	--parallelism 16 \
	--apply-thresholds-from /home/t/collimator/out/models/azoth-candidate-filetypes-ole-d00d55882eeb1d0a/config.json \
	--feature-cache-dir out/cache/azoth-route-features
2026-08-04 22:29:56,431 INFO azoth_calibrate_ensemble: partition 'test': 1946507 of 15612661 rows (12.5%) kept for fit/eval; score_table covers all 15612661
make[1]: *** [Makefile:1260: azoth-calibrate] Terminated)
