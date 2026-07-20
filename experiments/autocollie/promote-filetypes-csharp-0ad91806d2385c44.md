# Promote REJECTED — `0ad91806d2385c44` on `filetypes/csharp`

Generated 2026-07-09T12:19:32Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-07-09T12-11-03_20260709T121052-promote-0ad91806d2385c44_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 16 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-0ad91806d2385c44 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-0ad91806d2385c44/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-0ad91806d2385c44/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-0ad91806d2385c44/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-0ad91806d2385c44/score_table.npz \
	--partition dev \
	--parallelism 16 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
2026-07-09 08:11:21,851 INFO azoth_calibrate_ensemble: partition 'dev': 1689197 of 13546141 rows (12.5%) kept for fit/eval; score_table covers all 13546141
make[1]: *** [Makefile:1254: azoth-calibrate] Killed)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9892)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0ad91806d2385c44` | `debd1e7f8941f433` | `b97cb09f81da7ed8` |
| PR AUC | 0.9892 | 0.9889 | 0.9892 |
| ROC AUC | 0.9968 | 0.9967 | 0.9968 |
| F1 | 0.9482 | 0.9603 | 0.9644 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-07-09T12-11-03_20260709T121052-promote-0ad91806d2385c44_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 16 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-0ad91806d2385c44 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-0ad91806d2385c44/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-0ad91806d2385c44/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-0ad91806d2385c44/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-csharp-0ad91806d2385c44/score_table.npz \
	--partition dev \
	--parallelism 16 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
2026-07-09 08:11:21,851 INFO azoth_calibrate_ensemble: partition 'dev': 1689197 of 13546141 rows (12.5%) kept for fit/eval; score_table covers all 13546141
make[1]: *** [Makefile:1254: azoth-calibrate] Killed)
