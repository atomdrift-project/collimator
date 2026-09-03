# Promote REJECTED — `079c0efc65dc468e` on `filetypes/jar`

Generated 2026-08-21T14:16:54Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-08-21T13-48-53_20260821T134729-promote-079c0efc65dc468e_azoth-validate.log; tail: 2026-08-21 09:53:33,646 INFO azoth_calibrate_ensemble: L15 hostile recall=74.22% fp=84
2026-08-21 09:53:33,706 INFO azoth_calibrate_ensemble: L20 hostile recall=74.23% fp=84
2026-08-21 09:53:33,770 INFO azoth_calibrate_ensemble: L25 hostile recall=74.24% fp=84
2026-08-21 09:53:33,836 INFO azoth_calibrate_ensemble: L30 hostile recall=74.26% fp=84
2026-08-21 09:53:33,900 INFO azoth_calibrate_ensemble: L40 hostile recall=74.28% fp=84
2026-08-21 09:53:33,963 INFO azoth_calibrate_ensemble: L50 hostile recall=74.29% fp=84
2026-08-21 09:53:34,026 INFO azoth_calibrate_ensemble: L60 hostile recall=74.31% fp=85
2026-08-21 09:53:34,085 INFO azoth_calibrate_ensemble: L70 hostile recall=74.33% fp=85
2026-08-21 09:53:34,153 INFO azoth_calibrate_ensemble: L80 hostile recall=74.35% fp=85
2026-08-21 09:53:34,218 INFO azoth_calibrate_ensemble: L90 hostile recall=74.37% fp=85
2026-08-21 09:53:34,281 INFO azoth_calibrate_ensemble: L100 hostile recall=74.38% fp=85
2026-08-21 09:53:34,343 INFO azoth_calibrate_ensemble: L125 hostile recall=74.41% fp=86
2026-08-21 09:53:34,405 INFO azoth_calibrate_ensemble: L150 hostile recall=74.43% fp=86
2026-08-21 09:53:34,466 INFO azoth_calibrate_ensemble: L175 hostile recall=74.47% fp=86
2026-08-21 09:53:34,528 INFO azoth_calibrate_ensemble: L200 hostile recall=74.53% fp=86
2026-08-21 09:53:34,594 INFO azoth_calibrate_ensemble: L250 hostile recall=74.60% fp=87
2026-08-21 09:53:34,658 INFO azoth_calibrate_ensemble: L300 hostile recall=74.64% fp=88
2026-08-21 09:53:34,718 INFO azoth_calibrate_ensemble: L500 hostile recall=75.02% fp=92
2026-08-21 09:53:34,778 INFO azoth_calibrate_ensemble: L750 hostile recall=75.19% fp=102
2026-08-21 09:53:34,838 INFO azoth_calibrate_ensemble: L1000 hostile recall=75.36% fp=108
2026-08-21 09:53:34,898 INFO azoth_calibrate_ensemble: L1250 hostile recall=75.48% fp=113
2026-08-21 09:53:34,958 INFO azoth_calibrate_ensemble: L1500 hostile recall=75.60% fp=121
2026-08-21 09:53:35,019 INFO azoth_calibrate_ensemble: L1750 hostile recall=75.81% fp=128
2026-08-21 09:53:35,083 INFO azoth_calibrate_ensemble: L2000 hostile recall=75.99% fp=135
2026-08-21 09:53:35,149 INFO azoth_calibrate_ensemble: L2250 hostile recall=76.11% fp=144
2026-08-21 09:53:35,216 INFO azoth_calibrate_ensemble: L2500 hostile recall=76.22% fp=150
2026-08-21 09:53:35,276 INFO azoth_calibrate_ensemble: L3000 hostile recall=76.39% fp=169
2026-08-21 09:53:35,333 INFO azoth_calibrate_ensemble: L4000 hostile recall=76.77% fp=196
2026-08-21 09:53:35,390 INFO azoth_calibrate_ensemble: L5000 hostile recall=77.15% fp=223
2026-08-21 09:53:35,450 INFO azoth_calibrate_ensemble: L6000 hostile recall=77.57% fp=252
2026-08-21 09:53:35,517 INFO azoth_calibrate_ensemble: L7500 hostile recall=77.87% fp=279
2026-08-21 09:53:35,577 INFO azoth_calibrate_ensemble: L10000 hostile recall=78.39% fp=365
2026-08-21 09:53:35,635 INFO azoth_calibrate_ensemble: L15000 hostile recall=79.03% fp=512
2026-08-21 09:53:35,695 INFO azoth_calibrate_ensemble: L20000 hostile recall=79.43% fp=631
2026-08-21 09:53:35,754 INFO azoth_calibrate_ensemble: L25000 hostile recall=79.81% fp=787
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jar-079c0efc65dc468e/config.json
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 24 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-jar-079c0efc65dc468e \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-jar-079c0efc65dc468e/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-jar-079c0efc65dc468e/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-jar-079c0efc65dc468e/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-jar-079c0efc65dc468e/score_table.npz \
	--partition test \
	--parallelism 16 \
	--apply-thresholds-from /home/t/collimator/out/models/azoth-candidate-filetypes-jar-079c0efc65dc468e/config.json \
	--feature-cache-dir out/cache/azoth-route-features
2026-08-21 09:53:59,338 INFO azoth_calibrate_ensemble: partition 'test': 2129520 of 17074459 rows (12.5%) kept for fit/eval; score_table covers all 17074459
make[1]: *** [Makefile:1253: azoth-calibrate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9651)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `079c0efc65dc468e` | `6dd6ed53acbd6f73` | `e8ecdbb2bad1153e` |
| PR AUC | 0.9651 | 0.9729 | 0.9723 |
| ROC AUC | 0.9893 | 0.9913 | 0.9908 |
| F1 | 0.9009 | 0.9340 | 0.9326 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-08-21T13-48-53_20260821T134729-promote-079c0efc65dc468e_azoth-validate.log; tail: 2026-08-21 09:53:33,646 INFO azoth_calibrate_ensemble: L15 hostile recall=74.22% fp=84
2026-08-21 09:53:33,706 INFO azoth_calibrate_ensemble: L20 hostile recall=74.23% fp=84
2026-08-21 09:53:33,770 INFO azoth_calibrate_ensemble: L25 hostile recall=74.24% fp=84
2026-08-21 09:53:33,836 INFO azoth_calibrate_ensemble: L30 hostile recall=74.26% fp=84
2026-08-21 09:53:33,900 INFO azoth_calibrate_ensemble: L40 hostile recall=74.28% fp=84
2026-08-21 09:53:33,963 INFO azoth_calibrate_ensemble: L50 hostile recall=74.29% fp=84
2026-08-21 09:53:34,026 INFO azoth_calibrate_ensemble: L60 hostile recall=74.31% fp=85
2026-08-21 09:53:34,085 INFO azoth_calibrate_ensemble: L70 hostile recall=74.33% fp=85
2026-08-21 09:53:34,153 INFO azoth_calibrate_ensemble: L80 hostile recall=74.35% fp=85
2026-08-21 09:53:34,218 INFO azoth_calibrate_ensemble: L90 hostile recall=74.37% fp=85
2026-08-21 09:53:34,281 INFO azoth_calibrate_ensemble: L100 hostile recall=74.38% fp=85
2026-08-21 09:53:34,343 INFO azoth_calibrate_ensemble: L125 hostile recall=74.41% fp=86
2026-08-21 09:53:34,405 INFO azoth_calibrate_ensemble: L150 hostile recall=74.43% fp=86
2026-08-21 09:53:34,466 INFO azoth_calibrate_ensemble: L175 hostile recall=74.47% fp=86
2026-08-21 09:53:34,528 INFO azoth_calibrate_ensemble: L200 hostile recall=74.53% fp=86
2026-08-21 09:53:34,594 INFO azoth_calibrate_ensemble: L250 hostile recall=74.60% fp=87
2026-08-21 09:53:34,658 INFO azoth_calibrate_ensemble: L300 hostile recall=74.64% fp=88
2026-08-21 09:53:34,718 INFO azoth_calibrate_ensemble: L500 hostile recall=75.02% fp=92
2026-08-21 09:53:34,778 INFO azoth_calibrate_ensemble: L750 hostile recall=75.19% fp=102
2026-08-21 09:53:34,838 INFO azoth_calibrate_ensemble: L1000 hostile recall=75.36% fp=108
2026-08-21 09:53:34,898 INFO azoth_calibrate_ensemble: L1250 hostile recall=75.48% fp=113
2026-08-21 09:53:34,958 INFO azoth_calibrate_ensemble: L1500 hostile recall=75.60% fp=121
2026-08-21 09:53:35,019 INFO azoth_calibrate_ensemble: L1750 hostile recall=75.81% fp=128
2026-08-21 09:53:35,083 INFO azoth_calibrate_ensemble: L2000 hostile recall=75.99% fp=135
2026-08-21 09:53:35,149 INFO azoth_calibrate_ensemble: L2250 hostile recall=76.11% fp=144
2026-08-21 09:53:35,216 INFO azoth_calibrate_ensemble: L2500 hostile recall=76.22% fp=150
2026-08-21 09:53:35,276 INFO azoth_calibrate_ensemble: L3000 hostile recall=76.39% fp=169
2026-08-21 09:53:35,333 INFO azoth_calibrate_ensemble: L4000 hostile recall=76.77% fp=196
2026-08-21 09:53:35,390 INFO azoth_calibrate_ensemble: L5000 hostile recall=77.15% fp=223
2026-08-21 09:53:35,450 INFO azoth_calibrate_ensemble: L6000 hostile recall=77.57% fp=252
2026-08-21 09:53:35,517 INFO azoth_calibrate_ensemble: L7500 hostile recall=77.87% fp=279
2026-08-21 09:53:35,577 INFO azoth_calibrate_ensemble: L10000 hostile recall=78.39% fp=365
2026-08-21 09:53:35,635 INFO azoth_calibrate_ensemble: L15000 hostile recall=79.03% fp=512
2026-08-21 09:53:35,695 INFO azoth_calibrate_ensemble: L20000 hostile recall=79.43% fp=631
2026-08-21 09:53:35,754 INFO azoth_calibrate_ensemble: L25000 hostile recall=79.81% fp=787
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jar-079c0efc65dc468e/config.json
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 24 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-jar-079c0efc65dc468e \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-jar-079c0efc65dc468e/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-jar-079c0efc65dc468e/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-jar-079c0efc65dc468e/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-jar-079c0efc65dc468e/score_table.npz \
	--partition test \
	--parallelism 16 \
	--apply-thresholds-from /home/t/collimator/out/models/azoth-candidate-filetypes-jar-079c0efc65dc468e/config.json \
	--feature-cache-dir out/cache/azoth-route-features
2026-08-21 09:53:59,338 INFO azoth_calibrate_ensemble: partition 'test': 2129520 of 17074459 rows (12.5%) kept for fit/eval; score_table covers all 17074459
make[1]: *** [Makefile:1253: azoth-calibrate] Terminated)
