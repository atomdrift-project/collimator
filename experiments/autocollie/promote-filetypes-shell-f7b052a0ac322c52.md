# Promote REJECTED — `f7b052a0ac322c52` on `filetypes/shell`

Generated 2026-05-22T19:26:08Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-22T19-25-27_20260522T192525-promote-f7b052a0ac322c52_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 64 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-shell-f7b052a0ac322c52 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-shell-f7b052a0ac322c52/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-shell-f7b052a0ac322c52/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-shell-f7b052a0ac322c52/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-shell-f7b052a0ac322c52/score_table.npz \
	--partition dev \
	--parallelism 2 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
2026-05-22 15:25:30,044 INFO azoth_calibrate_ensemble: partition 'dev': 592917 of 4730194 rows (12.5%) kept for fit/eval; score_table covers all 4730194
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1649, in <module>
    raise SystemExit(main())
                     ~~~~^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1413, in main
    routes = list(_load_routes(args.summary))
                  ~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1069, in _load_routes
    with open(summary_path) as f:
         ~~~~^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/home/t/collimator/out/models/azoth-candidate-filetypes-shell-f7b052a0ac322c52/specialists.json'
make[1]: *** [Makefile:1010: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9966)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f7b052a0ac322c52` | `5882e274d2581d97` | `c74230522b4120ee` |
| PR AUC | 0.9966 | 0.9967 | 0.9967 |
| ROC AUC | 0.9980 | 0.9981 | 0.9980 |
| F1 | 0.9594 | 0.9560 | 0.9532 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-22T19-25-27_20260522T192525-promote-f7b052a0ac322c52_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
.venv/bin/python scripts/azoth_calibrate_ensemble.py \
	--db postgres://hopper@localhost:5432/hopper \
	--workers 64 \
	--azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-shell-f7b052a0ac322c52 \
	--summary /home/t/collimator/out/models/azoth-candidate-filetypes-shell-f7b052a0ac322c52/specialists.json \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-shell-f7b052a0ac322c52/general/threshold_scores.npz \
	--output /home/t/collimator/out/models/azoth-candidate-filetypes-shell-f7b052a0ac322c52/config.json \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-shell-f7b052a0ac322c52/score_table.npz \
	--partition dev \
	--parallelism 2 \
	 \
	 \
	 \
	 \
	--feature-cache-dir out/cache/azoth-route-features
2026-05-22 15:25:30,044 INFO azoth_calibrate_ensemble: partition 'dev': 592917 of 4730194 rows (12.5%) kept for fit/eval; score_table covers all 4730194
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1649, in <module>
    raise SystemExit(main())
                     ~~~~^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1413, in main
    routes = list(_load_routes(args.summary))
                  ~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1069, in _load_routes
    with open(summary_path) as f:
         ~~~~^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/home/t/collimator/out/models/azoth-candidate-filetypes-shell-f7b052a0ac322c52/specialists.json'
make[1]: *** [Makefile:1010: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
