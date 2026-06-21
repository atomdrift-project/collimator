# Promote REJECTED — `4f69046cd9cf700b` on `filetypes/jpeg`

Generated 2026-06-17T17:48:22Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-17T17-47-40_20260617T174731-promote-4f69046cd9cf700b_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-4f69046cd9cf700b \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-4f69046cd9cf700b/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-4f69046cd9cf700b/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-4f69046cd9cf700b/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-4f69046cd9cf700b/score_table.npz \
	--partition dev \
	--parallelism 16 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
2026-06-17 13:47:49,652 INFO azoth_calibrate_ensemble: partition 'dev': 1001161 of 8028377 rows (12.5%) kept for fit/eval; score_table covers all 8028377
make[1]: *** [Makefile:1230: azoth-calibrate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9879)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `4f69046cd9cf700b` | `cbad697ad93ac53d` | `b937e90f012500ef` |
| PR AUC | 0.9879 | 0.9859 | 0.9866 |
| ROC AUC | 0.9930 | 0.9930 | 0.9930 |
| F1 | 0.9286 | 0.9639 | 0.9524 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-17T17-47-40_20260617T174731-promote-4f69046cd9cf700b_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-4f69046cd9cf700b \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-4f69046cd9cf700b/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-4f69046cd9cf700b/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-4f69046cd9cf700b/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-4f69046cd9cf700b/score_table.npz \
	--partition dev \
	--parallelism 16 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
2026-06-17 13:47:49,652 INFO azoth_calibrate_ensemble: partition 'dev': 1001161 of 8028377 rows (12.5%) kept for fit/eval; score_table covers all 8028377
make[1]: *** [Makefile:1230: azoth-calibrate] Terminated)
