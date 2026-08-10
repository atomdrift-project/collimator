# Promote REJECTED — `b2636372e3f99c70` on `filetypes/registry`

Generated 2026-08-05T15:09:44Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-08-05T14-59-49_20260805T145850-promote-b2636372e3f99c70_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-registry-b2636372e3f99c70 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-registry-b2636372e3f99c70/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-registry-b2636372e3f99c70/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-registry-b2636372e3f99c70/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-registry-b2636372e3f99c70/score_table.npz \
	--partition dev \
	--parallelism 16 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
2026-08-05 11:00:03,807 INFO azoth_calibrate_ensemble: partition 'dev': 1947600 of 15612661 rows (12.5%) kept for fit/eval; score_table covers all 15612661
make[1]: *** [Makefile:1254: azoth-calibrate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.8443)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b2636372e3f99c70` | `55996db527e38238` | `06ec53bf4475d632` |
| PR AUC | 0.8443 | 0.8831 | 0.8813 |
| ROC AUC | 0.9986 | 0.9991 | 0.9991 |
| F1 | 0.6025 | 0.8077 | 0.8105 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-08-05T14-59-49_20260805T145850-promote-b2636372e3f99c70_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-registry-b2636372e3f99c70 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-registry-b2636372e3f99c70/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-registry-b2636372e3f99c70/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-registry-b2636372e3f99c70/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-registry-b2636372e3f99c70/score_table.npz \
	--partition dev \
	--parallelism 16 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
2026-08-05 11:00:03,807 INFO azoth_calibrate_ensemble: partition 'dev': 1947600 of 15612661 rows (12.5%) kept for fit/eval; score_table covers all 15612661
make[1]: *** [Makefile:1254: azoth-calibrate] Terminated)
