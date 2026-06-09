# Promote REJECTED — `f41f682734dbb9cc` on `filetypes/python`

Generated 2026-06-08T19:09:29Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-08T19-09-13_20260608T190912-promote-f41f682734dbb9cc_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-python-f41f682734dbb9cc \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-python-f41f682734dbb9cc/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-python-f41f682734dbb9cc/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-python-f41f682734dbb9cc/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-python-f41f682734dbb9cc/score_table.npz \
	--partition dev \
	--parallelism 16 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
2026-06-08 15:09:17,140 INFO azoth_calibrate_ensemble: partition 'dev': 860195 of 6899010 rows (12.5%) kept for fit/eval; score_table covers all 6899010
make[1]: *** [Makefile:1201: azoth-calibrate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9942)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f41f682734dbb9cc` | `2444002bbdea3956` | `0b19b65287c459df` |
| PR AUC | 0.9942 | 0.9947 | 0.9948 |
| ROC AUC | 0.9953 | 0.9957 | 0.9957 |
| F1 | 0.9668 | 0.9685 | 0.9696 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-08T19-09-13_20260608T190912-promote-f41f682734dbb9cc_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-python-f41f682734dbb9cc \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-python-f41f682734dbb9cc/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-python-f41f682734dbb9cc/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-python-f41f682734dbb9cc/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-python-f41f682734dbb9cc/score_table.npz \
	--partition dev \
	--parallelism 16 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
2026-06-08 15:09:17,140 INFO azoth_calibrate_ensemble: partition 'dev': 860195 of 6899010 rows (12.5%) kept for fit/eval; score_table covers all 6899010
make[1]: *** [Makefile:1201: azoth-calibrate] Terminated)
