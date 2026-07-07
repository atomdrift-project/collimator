# Promote REJECTED — `05333554c30e1f55` on `filetypes/python-bytecode`

Generated 2026-07-06T09:08:31Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-07-06T08-56-29_20260706T085608-promote-05333554c30e1f55_azoth-validate.log; tail: 2026-07-06 05:04:46,143 INFO azoth_calibrate_ensemble: L15 hostile recall=59.68% fp=301
2026-07-06 05:04:46,171 INFO azoth_calibrate_ensemble: L20 hostile recall=67.35% fp=342
2026-07-06 05:04:46,199 INFO azoth_calibrate_ensemble: L25 hostile recall=68.19% fp=375
2026-07-06 05:04:46,226 INFO azoth_calibrate_ensemble: L30 hostile recall=68.58% fp=409
2026-07-06 05:04:46,255 INFO azoth_calibrate_ensemble: L40 hostile recall=69.58% fp=469
2026-07-06 05:04:46,284 INFO azoth_calibrate_ensemble: L50 hostile recall=70.12% fp=2497
2026-07-06 05:04:46,313 INFO azoth_calibrate_ensemble: L60 hostile recall=70.45% fp=2554
2026-07-06 05:04:46,343 INFO azoth_calibrate_ensemble: L70 hostile recall=70.65% fp=2610
2026-07-06 05:04:46,372 INFO azoth_calibrate_ensemble: L80 hostile recall=70.97% fp=2684
2026-07-06 05:04:46,402 INFO azoth_calibrate_ensemble: L90 hostile recall=71.28% fp=2733
2026-07-06 05:04:46,433 INFO azoth_calibrate_ensemble: L100 hostile recall=71.50% fp=2781
2026-07-06 05:04:46,463 INFO azoth_calibrate_ensemble: L125 hostile recall=71.77% fp=2894
2026-07-06 05:04:46,493 INFO azoth_calibrate_ensemble: L150 hostile recall=72.11% fp=3001
2026-07-06 05:04:46,521 INFO azoth_calibrate_ensemble: L175 hostile recall=72.50% fp=3088
2026-07-06 05:04:46,549 INFO azoth_calibrate_ensemble: L200 hostile recall=72.66% fp=3212
2026-07-06 05:04:46,580 INFO azoth_calibrate_ensemble: L250 hostile recall=73.29% fp=3373
2026-07-06 05:04:46,609 INFO azoth_calibrate_ensemble: L300 hostile recall=73.55% fp=3554
2026-07-06 05:04:46,638 INFO azoth_calibrate_ensemble: L500 hostile recall=75.19% fp=4140
2026-07-06 05:04:46,666 INFO azoth_calibrate_ensemble: L750 hostile recall=76.54% fp=7251
2026-07-06 05:04:46,695 INFO azoth_calibrate_ensemble: L1000 hostile recall=77.07% fp=7831
2026-07-06 05:04:46,723 INFO azoth_calibrate_ensemble: L1250 hostile recall=77.39% fp=8375
2026-07-06 05:04:46,750 INFO azoth_calibrate_ensemble: L1500 hostile recall=77.86% fp=8687
2026-07-06 05:04:46,778 INFO azoth_calibrate_ensemble: L1750 hostile recall=78.16% fp=9025
2026-07-06 05:04:46,806 INFO azoth_calibrate_ensemble: L2000 hostile recall=78.47% fp=28435
2026-07-06 05:04:46,834 INFO azoth_calibrate_ensemble: L2250 hostile recall=78.72% fp=28628
2026-07-06 05:04:46,861 INFO azoth_calibrate_ensemble: L2500 hostile recall=78.98% fp=28789
2026-07-06 05:04:46,888 INFO azoth_calibrate_ensemble: L3000 hostile recall=79.50% fp=29051
2026-07-06 05:04:46,917 INFO azoth_calibrate_ensemble: L4000 hostile recall=80.28% fp=29461
2026-07-06 05:04:46,948 INFO azoth_calibrate_ensemble: L5000 hostile recall=74.84% fp=28738
2026-07-06 05:04:46,980 INFO azoth_calibrate_ensemble: L6000 hostile recall=75.53% fp=9420
2026-07-06 05:04:47,008 INFO azoth_calibrate_ensemble: L7500 hostile recall=76.30% fp=8640
2026-07-06 05:04:47,036 INFO azoth_calibrate_ensemble: L10000 hostile recall=77.07% fp=5837
2026-07-06 05:04:47,067 INFO azoth_calibrate_ensemble: L15000 hostile recall=73.37% fp=4278
2026-07-06 05:04:47,097 INFO azoth_calibrate_ensemble: L20000 hostile recall=74.51% fp=3911
2026-07-06 05:04:47,127 INFO azoth_calibrate_ensemble: L25000 hostile recall=75.19% fp=4030
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-05333554c30e1f55/config.json
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-05333554c30e1f55 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-05333554c30e1f55/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-05333554c30e1f55/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-05333554c30e1f55/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-05333554c30e1f55/score_table.npz \
	--partition test \
	--parallelism 16 \
	--apply-thresholds-from /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-05333554c30e1f55/config.json \
	--feature-cache-dir out/cache/azoth-route-features
2026-07-06 05:05:10,217 INFO azoth_calibrate_ensemble: partition 'test': 1628883 of 13069437 rows (12.5%) kept for fit/eval; score_table covers all 13069437
make[2]: *** [Makefile:1260: azoth-calibrate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9948)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `05333554c30e1f55` | `60d7f35b1456b041` | `f580d75f8b00b2f5` |
| PR AUC | 0.9948 | 0.9950 | 0.9951 |
| ROC AUC | 0.9972 | 0.9978 | 0.9978 |
| F1 | 0.9764 | 0.9813 | 0.9813 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-07-06T08-56-29_20260706T085608-promote-05333554c30e1f55_azoth-validate.log; tail: 2026-07-06 05:04:46,143 INFO azoth_calibrate_ensemble: L15 hostile recall=59.68% fp=301
2026-07-06 05:04:46,171 INFO azoth_calibrate_ensemble: L20 hostile recall=67.35% fp=342
2026-07-06 05:04:46,199 INFO azoth_calibrate_ensemble: L25 hostile recall=68.19% fp=375
2026-07-06 05:04:46,226 INFO azoth_calibrate_ensemble: L30 hostile recall=68.58% fp=409
2026-07-06 05:04:46,255 INFO azoth_calibrate_ensemble: L40 hostile recall=69.58% fp=469
2026-07-06 05:04:46,284 INFO azoth_calibrate_ensemble: L50 hostile recall=70.12% fp=2497
2026-07-06 05:04:46,313 INFO azoth_calibrate_ensemble: L60 hostile recall=70.45% fp=2554
2026-07-06 05:04:46,343 INFO azoth_calibrate_ensemble: L70 hostile recall=70.65% fp=2610
2026-07-06 05:04:46,372 INFO azoth_calibrate_ensemble: L80 hostile recall=70.97% fp=2684
2026-07-06 05:04:46,402 INFO azoth_calibrate_ensemble: L90 hostile recall=71.28% fp=2733
2026-07-06 05:04:46,433 INFO azoth_calibrate_ensemble: L100 hostile recall=71.50% fp=2781
2026-07-06 05:04:46,463 INFO azoth_calibrate_ensemble: L125 hostile recall=71.77% fp=2894
2026-07-06 05:04:46,493 INFO azoth_calibrate_ensemble: L150 hostile recall=72.11% fp=3001
2026-07-06 05:04:46,521 INFO azoth_calibrate_ensemble: L175 hostile recall=72.50% fp=3088
2026-07-06 05:04:46,549 INFO azoth_calibrate_ensemble: L200 hostile recall=72.66% fp=3212
2026-07-06 05:04:46,580 INFO azoth_calibrate_ensemble: L250 hostile recall=73.29% fp=3373
2026-07-06 05:04:46,609 INFO azoth_calibrate_ensemble: L300 hostile recall=73.55% fp=3554
2026-07-06 05:04:46,638 INFO azoth_calibrate_ensemble: L500 hostile recall=75.19% fp=4140
2026-07-06 05:04:46,666 INFO azoth_calibrate_ensemble: L750 hostile recall=76.54% fp=7251
2026-07-06 05:04:46,695 INFO azoth_calibrate_ensemble: L1000 hostile recall=77.07% fp=7831
2026-07-06 05:04:46,723 INFO azoth_calibrate_ensemble: L1250 hostile recall=77.39% fp=8375
2026-07-06 05:04:46,750 INFO azoth_calibrate_ensemble: L1500 hostile recall=77.86% fp=8687
2026-07-06 05:04:46,778 INFO azoth_calibrate_ensemble: L1750 hostile recall=78.16% fp=9025
2026-07-06 05:04:46,806 INFO azoth_calibrate_ensemble: L2000 hostile recall=78.47% fp=28435
2026-07-06 05:04:46,834 INFO azoth_calibrate_ensemble: L2250 hostile recall=78.72% fp=28628
2026-07-06 05:04:46,861 INFO azoth_calibrate_ensemble: L2500 hostile recall=78.98% fp=28789
2026-07-06 05:04:46,888 INFO azoth_calibrate_ensemble: L3000 hostile recall=79.50% fp=29051
2026-07-06 05:04:46,917 INFO azoth_calibrate_ensemble: L4000 hostile recall=80.28% fp=29461
2026-07-06 05:04:46,948 INFO azoth_calibrate_ensemble: L5000 hostile recall=74.84% fp=28738
2026-07-06 05:04:46,980 INFO azoth_calibrate_ensemble: L6000 hostile recall=75.53% fp=9420
2026-07-06 05:04:47,008 INFO azoth_calibrate_ensemble: L7500 hostile recall=76.30% fp=8640
2026-07-06 05:04:47,036 INFO azoth_calibrate_ensemble: L10000 hostile recall=77.07% fp=5837
2026-07-06 05:04:47,067 INFO azoth_calibrate_ensemble: L15000 hostile recall=73.37% fp=4278
2026-07-06 05:04:47,097 INFO azoth_calibrate_ensemble: L20000 hostile recall=74.51% fp=3911
2026-07-06 05:04:47,127 INFO azoth_calibrate_ensemble: L25000 hostile recall=75.19% fp=4030
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-05333554c30e1f55/config.json
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-05333554c30e1f55 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-05333554c30e1f55/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-05333554c30e1f55/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-05333554c30e1f55/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-05333554c30e1f55/score_table.npz \
	--partition test \
	--parallelism 16 \
	--apply-thresholds-from /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-05333554c30e1f55/config.json \
	--feature-cache-dir out/cache/azoth-route-features
2026-07-06 05:05:10,217 INFO azoth_calibrate_ensemble: partition 'test': 1628883 of 13069437 rows (12.5%) kept for fit/eval; score_table covers all 13069437
make[2]: *** [Makefile:1260: azoth-calibrate] Terminated)
