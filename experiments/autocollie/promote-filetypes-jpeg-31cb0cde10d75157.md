# Promote REJECTED — `31cb0cde10d75157` on `filetypes/jpeg`

Generated 2026-06-02T02:40:39Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-02T02-40-39_20260602T024035-promote-31cb0cde10d75157_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-31cb0cde10d75157/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-31cb0cde10d75157/general — bundle is incomplete
make[1]: *** [Makefile:1052: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9645)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `31cb0cde10d75157` | `06e395ac6066f95e` | `7fd2d44fa1076d7f` |
| PR AUC | 0.9645 | 0.9832 | 0.9792 |
| ROC AUC | 0.9824 | 0.9910 | 0.9890 |
| F1 | 0.8471 | 0.9231 | 0.9000 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-02T02-40-39_20260602T024035-promote-31cb0cde10d75157_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-31cb0cde10d75157/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-31cb0cde10d75157/general — bundle is incomplete
make[1]: *** [Makefile:1052: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
