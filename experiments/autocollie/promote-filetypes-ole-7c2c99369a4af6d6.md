# Promote REJECTED — `7c2c99369a4af6d6` on `filetypes/ole`

Generated 2026-06-08T16:17:07Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-08T16-16-53_20260608T161652-promote-7c2c99369a4af6d6_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-ole-7c2c99369a4af6d6 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-ole-7c2c99369a4af6d6/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-ole-7c2c99369a4af6d6/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-ole-7c2c99369a4af6d6/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-ole-7c2c99369a4af6d6/score_table.npz \
	--partition dev \
	--parallelism 16 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
2026-06-08 12:16:57,516 INFO azoth_calibrate_ensemble: partition 'dev': 860195 of 6899010 rows (12.5%) kept for fit/eval; score_table covers all 6899010
make[1]: *** [Makefile:1201: azoth-calibrate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9966)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `7c2c99369a4af6d6` | `026d2496b60b5d52` | `785236bd76ab5f73` |
| PR AUC | 0.9966 | 0.9972 | 0.9973 |
| ROC AUC | 0.9960 | 0.9966 | 0.9966 |
| F1 | 0.8998 | 0.9742 | 0.9773 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-08T16-16-53_20260608T161652-promote-7c2c99369a4af6d6_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-ole-7c2c99369a4af6d6 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-ole-7c2c99369a4af6d6/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-ole-7c2c99369a4af6d6/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-ole-7c2c99369a4af6d6/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-ole-7c2c99369a4af6d6/score_table.npz \
	--partition dev \
	--parallelism 16 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
2026-06-08 12:16:57,516 INFO azoth_calibrate_ensemble: partition 'dev': 860195 of 6899010 rows (12.5%) kept for fit/eval; score_table covers all 6899010
make[1]: *** [Makefile:1201: azoth-calibrate] Terminated)
