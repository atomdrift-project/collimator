# Promote REJECTED — `06ba4c8a340d6c3c` on `filetypes/xlsx`

Generated 2026-07-03T07:00:56Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-07-03T06-51-09_20260703T065059-promote-06ba4c8a340d6c3c_azoth-validate.log; tail: 2026-07-03 02:59:44,406 INFO azoth_calibrate_ensemble: filetypes/nupkg: using cached scores
2026-07-03 02:59:44,624 INFO azoth_calibrate_ensemble: filetypes/chrome_manifest: using cached scores
2026-07-03 02:59:53,496 INFO azoth_calibrate_ensemble: filetypes/csharp: loaded route feature matrix cache out/cache/azoth-route-features/filetypes_csharp-2037843653-c0cadfea71010580-f0500833c12e95ea.matrix.npz (92307 rows, 1045 features, nnz=2364379)
2026-07-03 02:59:54,668 INFO azoth_calibrate_ensemble: filetypes/csharp: refreshed 92307 rows in 16.0s (fetch 14.7s, filter 0.0s, load 0.1s, extract 0.0s, matrix 0.0s, predict 1.1s, write 0.1s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1045 nnz=2364379)
2026-07-03 03:00:28,290 INFO azoth_calibrate_ensemble: L0 hostile recall=56.59% fp=0
2026-07-03 03:00:28,328 INFO azoth_calibrate_ensemble: L1 hostile recall=56.63% fp=95
2026-07-03 03:00:28,372 INFO azoth_calibrate_ensemble: L2 hostile recall=56.64% fp=95
2026-07-03 03:00:28,420 INFO azoth_calibrate_ensemble: L3 hostile recall=56.65% fp=95
2026-07-03 03:00:28,481 INFO azoth_calibrate_ensemble: L4 hostile recall=56.66% fp=95
2026-07-03 03:00:28,525 INFO azoth_calibrate_ensemble: L5 hostile recall=56.67% fp=95
2026-07-03 03:00:28,562 INFO azoth_calibrate_ensemble: L10 hostile recall=60.76% fp=129
2026-07-03 03:00:28,605 INFO azoth_calibrate_ensemble: L20 hostile recall=61.85% fp=242
2026-07-03 03:00:28,642 INFO azoth_calibrate_ensemble: L30 hostile recall=64.25% fp=722
2026-07-03 03:00:28,680 INFO azoth_calibrate_ensemble: L40 hostile recall=64.57% fp=2784
2026-07-03 03:00:28,719 INFO azoth_calibrate_ensemble: L50 hostile recall=65.11% fp=2838
2026-07-03 03:00:28,755 INFO azoth_calibrate_ensemble: L60 hostile recall=67.50% fp=2902
2026-07-03 03:00:28,791 INFO azoth_calibrate_ensemble: L70 hostile recall=68.11% fp=2955
2026-07-03 03:00:28,823 INFO azoth_calibrate_ensemble: L80 hostile recall=68.38% fp=3007
2026-07-03 03:00:28,857 INFO azoth_calibrate_ensemble: L90 hostile recall=69.00% fp=3181
2026-07-03 03:00:28,906 INFO azoth_calibrate_ensemble: L100 hostile recall=69.52% fp=3237
2026-07-03 03:00:28,961 INFO azoth_calibrate_ensemble: L125 hostile recall=70.28% fp=3348
2026-07-03 03:00:29,009 INFO azoth_calibrate_ensemble: L150 hostile recall=70.82% fp=3473
2026-07-03 03:00:29,052 INFO azoth_calibrate_ensemble: L175 hostile recall=71.39% fp=3565
2026-07-03 03:00:29,102 INFO azoth_calibrate_ensemble: L200 hostile recall=71.93% fp=3672
2026-07-03 03:00:29,148 INFO azoth_calibrate_ensemble: L250 hostile recall=72.71% fp=4362
2026-07-03 03:00:29,193 INFO azoth_calibrate_ensemble: L300 hostile recall=73.55% fp=4538
2026-07-03 03:00:29,239 INFO azoth_calibrate_ensemble: L500 hostile recall=75.95% fp=5260
2026-07-03 03:00:29,276 INFO azoth_calibrate_ensemble: L1000 hostile recall=78.36% fp=6445
2026-07-03 03:00:29,313 INFO azoth_calibrate_ensemble: L2000 hostile recall=80.16% fp=7996
2026-07-03 03:00:29,349 INFO azoth_calibrate_ensemble: L5000 hostile recall=73.49% fp=8386
2026-07-03 03:00:29,388 INFO azoth_calibrate_ensemble: L7500 hostile recall=74.96% fp=6703
2026-07-03 03:00:29,424 INFO azoth_calibrate_ensemble: L10000 hostile recall=76.08% fp=6216
2026-07-03 03:00:29,463 INFO azoth_calibrate_ensemble: L15000 hostile recall=77.28% fp=5266
2026-07-03 03:00:29,497 INFO azoth_calibrate_ensemble: L20000 hostile recall=78.16% fp=4580
2026-07-03 03:00:29,552 INFO azoth_calibrate_ensemble: L25000 hostile recall=78.90% fp=4707
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-06ba4c8a340d6c3c/config.json
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-06ba4c8a340d6c3c \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-06ba4c8a340d6c3c/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-06ba4c8a340d6c3c/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-06ba4c8a340d6c3c/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-06ba4c8a340d6c3c/score_table.npz \
	--partition test \
	--parallelism 16 \
	--apply-thresholds-from /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-06ba4c8a340d6c3c/config.json \
	--feature-cache-dir out/cache/azoth-route-features
2026-07-03 03:00:55,186 INFO azoth_calibrate_ensemble: partition 'test': 1608866 of 12910342 rows (12.5%) kept for fit/eval; score_table covers all 12910342
make[1]: *** [Makefile:1240: azoth-calibrate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9852)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `06ba4c8a340d6c3c` | `f480f28a9d8264db` | `23ffb6a6e97b1118` |
| PR AUC | 0.9852 | 0.9834 | 0.9872 |
| ROC AUC | 0.7261 | 0.7236 | 0.7737 |
| F1 | 0.5192 | 0.9859 | 0.9863 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-07-03T06-51-09_20260703T065059-promote-06ba4c8a340d6c3c_azoth-validate.log; tail: 2026-07-03 02:59:44,406 INFO azoth_calibrate_ensemble: filetypes/nupkg: using cached scores
2026-07-03 02:59:44,624 INFO azoth_calibrate_ensemble: filetypes/chrome_manifest: using cached scores
2026-07-03 02:59:53,496 INFO azoth_calibrate_ensemble: filetypes/csharp: loaded route feature matrix cache out/cache/azoth-route-features/filetypes_csharp-2037843653-c0cadfea71010580-f0500833c12e95ea.matrix.npz (92307 rows, 1045 features, nnz=2364379)
2026-07-03 02:59:54,668 INFO azoth_calibrate_ensemble: filetypes/csharp: refreshed 92307 rows in 16.0s (fetch 14.7s, filter 0.0s, load 0.1s, extract 0.0s, matrix 0.0s, predict 1.1s, write 0.1s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1045 nnz=2364379)
2026-07-03 03:00:28,290 INFO azoth_calibrate_ensemble: L0 hostile recall=56.59% fp=0
2026-07-03 03:00:28,328 INFO azoth_calibrate_ensemble: L1 hostile recall=56.63% fp=95
2026-07-03 03:00:28,372 INFO azoth_calibrate_ensemble: L2 hostile recall=56.64% fp=95
2026-07-03 03:00:28,420 INFO azoth_calibrate_ensemble: L3 hostile recall=56.65% fp=95
2026-07-03 03:00:28,481 INFO azoth_calibrate_ensemble: L4 hostile recall=56.66% fp=95
2026-07-03 03:00:28,525 INFO azoth_calibrate_ensemble: L5 hostile recall=56.67% fp=95
2026-07-03 03:00:28,562 INFO azoth_calibrate_ensemble: L10 hostile recall=60.76% fp=129
2026-07-03 03:00:28,605 INFO azoth_calibrate_ensemble: L20 hostile recall=61.85% fp=242
2026-07-03 03:00:28,642 INFO azoth_calibrate_ensemble: L30 hostile recall=64.25% fp=722
2026-07-03 03:00:28,680 INFO azoth_calibrate_ensemble: L40 hostile recall=64.57% fp=2784
2026-07-03 03:00:28,719 INFO azoth_calibrate_ensemble: L50 hostile recall=65.11% fp=2838
2026-07-03 03:00:28,755 INFO azoth_calibrate_ensemble: L60 hostile recall=67.50% fp=2902
2026-07-03 03:00:28,791 INFO azoth_calibrate_ensemble: L70 hostile recall=68.11% fp=2955
2026-07-03 03:00:28,823 INFO azoth_calibrate_ensemble: L80 hostile recall=68.38% fp=3007
2026-07-03 03:00:28,857 INFO azoth_calibrate_ensemble: L90 hostile recall=69.00% fp=3181
2026-07-03 03:00:28,906 INFO azoth_calibrate_ensemble: L100 hostile recall=69.52% fp=3237
2026-07-03 03:00:28,961 INFO azoth_calibrate_ensemble: L125 hostile recall=70.28% fp=3348
2026-07-03 03:00:29,009 INFO azoth_calibrate_ensemble: L150 hostile recall=70.82% fp=3473
2026-07-03 03:00:29,052 INFO azoth_calibrate_ensemble: L175 hostile recall=71.39% fp=3565
2026-07-03 03:00:29,102 INFO azoth_calibrate_ensemble: L200 hostile recall=71.93% fp=3672
2026-07-03 03:00:29,148 INFO azoth_calibrate_ensemble: L250 hostile recall=72.71% fp=4362
2026-07-03 03:00:29,193 INFO azoth_calibrate_ensemble: L300 hostile recall=73.55% fp=4538
2026-07-03 03:00:29,239 INFO azoth_calibrate_ensemble: L500 hostile recall=75.95% fp=5260
2026-07-03 03:00:29,276 INFO azoth_calibrate_ensemble: L1000 hostile recall=78.36% fp=6445
2026-07-03 03:00:29,313 INFO azoth_calibrate_ensemble: L2000 hostile recall=80.16% fp=7996
2026-07-03 03:00:29,349 INFO azoth_calibrate_ensemble: L5000 hostile recall=73.49% fp=8386
2026-07-03 03:00:29,388 INFO azoth_calibrate_ensemble: L7500 hostile recall=74.96% fp=6703
2026-07-03 03:00:29,424 INFO azoth_calibrate_ensemble: L10000 hostile recall=76.08% fp=6216
2026-07-03 03:00:29,463 INFO azoth_calibrate_ensemble: L15000 hostile recall=77.28% fp=5266
2026-07-03 03:00:29,497 INFO azoth_calibrate_ensemble: L20000 hostile recall=78.16% fp=4580
2026-07-03 03:00:29,552 INFO azoth_calibrate_ensemble: L25000 hostile recall=78.90% fp=4707
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-06ba4c8a340d6c3c/config.json
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 128 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-06ba4c8a340d6c3c \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-06ba4c8a340d6c3c/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-06ba4c8a340d6c3c/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-06ba4c8a340d6c3c/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-06ba4c8a340d6c3c/score_table.npz \
	--partition test \
	--parallelism 16 \
	--apply-thresholds-from /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-06ba4c8a340d6c3c/config.json \
	--feature-cache-dir out/cache/azoth-route-features
2026-07-03 03:00:55,186 INFO azoth_calibrate_ensemble: partition 'test': 1608866 of 12910342 rows (12.5%) kept for fit/eval; score_table covers all 12910342
make[1]: *** [Makefile:1240: azoth-calibrate] Terminated)
