# Promote REJECTED — `0d3757ef3cf99524` on `filegroups/config`

Generated 2026-06-28T11:21:18Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-28T11-19-58_20260628T111957-promote-0d3757ef3cf99524_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-config-0d3757ef3cf99524 \
	--summary /home/t/collimator/out/models/azoth-candidate-filegroups-config-0d3757ef3cf99524/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-config-0d3757ef3cf99524/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-config-0d3757ef3cf99524/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-config-0d3757ef3cf99524/score_table.npz \
	--partition dev \
	--parallelism 16 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
2026-06-28 07:20:10,969 INFO azoth_calibrate_ensemble: partition 'dev': 1077447 of 8638497 rows (12.5%) kept for fit/eval; score_table covers all 8638497
make[1]: *** [Makefile:1234: azoth-calibrate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9985)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0d3757ef3cf99524` | `dfa99900ae45ef74` | `d52585a43e1247a0` |
| PR AUC | 0.9985 | 0.9983 | 0.9983 |
| ROC AUC | 0.9984 | 0.9985 | 0.9985 |
| F1 | 0.9881 | 0.9884 | 0.9896 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-06-28T11-19-58_20260628T111957-promote-0d3757ef3cf99524_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-config-0d3757ef3cf99524 \
	--summary /home/t/collimator/out/models/azoth-candidate-filegroups-config-0d3757ef3cf99524/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-config-0d3757ef3cf99524/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filegroups-config-0d3757ef3cf99524/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-config-0d3757ef3cf99524/score_table.npz \
	--partition dev \
	--parallelism 16 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
2026-06-28 07:20:10,969 INFO azoth_calibrate_ensemble: partition 'dev': 1077447 of 8638497 rows (12.5%) kept for fit/eval; score_table covers all 8638497
make[1]: *** [Makefile:1234: azoth-calibrate] Terminated)
